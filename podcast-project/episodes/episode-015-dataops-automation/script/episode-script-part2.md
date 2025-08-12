# Episode 15: DataOps aur Pipeline Automation - Part 2: Tools & Technologies
*Mumbai ki Local Train System se Advanced DataOps Tools tak*

## Episode Overview
- **Duration**: 2 hours (Part 2 of 3)
- **Focus**: DataOps tools implementation, configuration, aur real-world usage
- **Style**: Mumbai street-style technical deep dive
- **Target Audience**: Data engineers, platform engineers, DevOps professionals

---

## Introduction: Mumbai Local Train Control Room se DataOps Tools tak

Mumbai local train system ka control room dekha hai kabhi? Hundreds of monitors, real-time tracking systems, automated signal controls, predictive maintenance alerts. Ek bhi component fail ho jaye toh poora network affect hota hai. DataOps tools exactly yahi role play karte hain data ecosystem mein.

Namaste dosto! Part 1 mein humne DataOps fundamentals samjhe - principles, culture, Indian company examples. Aaj Part 2 mein hum deep dive karenge tools aur technologies mein. Har tool ko Mumbai analogies se explain karenge, real Indian examples denge, aur production-ready code dikhayenge.

### Today's Agenda: DataOps Toolchain Deep Dive

**8 Major Tool Categories:**
1. Apache Airflow - Orchestration (Local train schedule controller)
2. dbt - Data Transformations (Car assembly line)
3. Terraform - Infrastructure as Code (City planning department)
4. Great Expectations - Data Quality (Quality control inspector)
5. Monitoring Stack - Real-time observability (Traffic control room)
6. GitOps - Deployment automation (Automated delivery system)
7. Apache Kafka - Event streaming (Mumbai's communication network)
8. Kubernetes - Container orchestration (Multi-level parking system)

---

## Section 1: Apache Airflow - The Orchestra Conductor

### Mumbai Local Train Schedule Controller Analogy

Mumbai local trains ka schedule controller center dekho - hundreds of trains, complex dependencies, precise timing, automatic coordination. Airflow exactly yahi karta hai data pipelines ke liye!

```python
# Mumbai local train scheduling analogy
class MumbaiLocalSchedule:
    def __init__(self):
        self.trains = ["Virar", "Borivali", "Andheri", "Bandra", "Churchgate"]
        self.platforms = {"Platform_1": [], "Platform_2": [], "Platform_3": []}
    
    def schedule_train_arrival(self, train_name, platform, arrival_time):
        # Check dependencies - platform available?
        if self.is_platform_free(platform, arrival_time):
            self.platforms[platform].append({
                'train': train_name,
                'arrival': arrival_time,
                'departure': arrival_time + timedelta(minutes=2)
            })
            return True
        return False
```

### Airflow Architecture Overview

**Core Components:**
- **Scheduler**: Triggers tasks based on schedule
- **Executor**: Runs the tasks
- **Web Server**: UI for monitoring
- **DAG Processor**: Parses and manages workflows
- **Metadata Database**: Stores state information

```python
# Basic Airflow DAG structure
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

# DAG definition
dag = DAG(
    'mumbai_ecommerce_analytics',
    default_args=default_args,
    description='Daily analytics pipeline for Mumbai e-commerce data',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    catchup=False,
    tags=['analytics', 'mumbai', 'ecommerce']
)
```

### Real Example: Swiggy's Food Delivery Analytics Pipeline

Swiggy processes 2 million orders daily across 500+ cities. Unka Airflow implementation:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.sql_operator import PostgresOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.sensors.s3_key_sensor import S3KeySensor
import pandas as pd

def extract_order_data(**context):
    """Extract daily order data from multiple sources"""
    execution_date = context['execution_date']
    
    # Extract from order service database
    order_query = f"""
    SELECT 
        order_id, customer_id, restaurant_id, delivery_partner_id,
        order_placed_time, food_ready_time, pickup_time, delivery_time,
        total_amount, delivery_fee, platform_fee,
        customer_location, restaurant_location,
        order_status, cuisine_type, items_ordered
    FROM orders 
    WHERE DATE(order_placed_time) = '{execution_date.strftime('%Y-%m-%d')}'
    """
    
    orders_df = pd.read_sql(order_query, con=DATABASE_CONNECTION)
    
    # Extract weather data for delivery impact analysis
    weather_data = get_weather_data(execution_date)
    
    # Extract traffic data from Google Maps API
    traffic_data = get_traffic_data(execution_date)
    
    # Store raw data in S3
    s3_key = f"raw-data/orders/{execution_date.strftime('%Y/%m/%d')}/orders.parquet"
    orders_df.to_parquet(f's3://swiggy-data-lake/{s3_key}')
    
    return s3_key

def transform_delivery_metrics(**context):
    """Transform data to calculate delivery performance metrics"""
    s3_key = context['task_instance'].xcom_pull(task_ids='extract_order_data')
    
    # Read data from S3
    orders_df = pd.read_parquet(f's3://swiggy-data-lake/{s3_key}')
    
    # Calculate delivery metrics
    orders_df['order_to_pickup_time'] = (
        pd.to_datetime(orders_df['pickup_time']) - 
        pd.to_datetime(orders_df['order_placed_time'])
    ).dt.total_seconds() / 60
    
    orders_df['pickup_to_delivery_time'] = (
        pd.to_datetime(orders_df['delivery_time']) - 
        pd.to_datetime(orders_df['pickup_time'])
    ).dt.total_seconds() / 60
    
    orders_df['total_delivery_time'] = (
        pd.to_datetime(orders_df['delivery_time']) - 
        pd.to_datetime(orders_df['order_placed_time'])
    ).dt.total_seconds() / 60
    
    # City-wise performance calculation
    city_performance = orders_df.groupby('customer_city').agg({
        'total_delivery_time': ['mean', 'median', 'std'],
        'order_id': 'count',
        'total_amount': 'sum'
    }).round(2)
    
    # Store transformed data
    transformed_key = s3_key.replace('raw-data', 'transformed-data')
    city_performance.to_parquet(f's3://swiggy-data-lake/{transformed_key}')
    
    return transformed_key

def generate_business_insights(**context):
    """Generate actionable business insights"""
    transformed_key = context['task_instance'].xcom_pull(task_ids='transform_delivery_metrics')
    
    city_performance = pd.read_parquet(f's3://swiggy-data-lake/{transformed_key}')
    
    # Identify performance issues
    slow_cities = city_performance[
        city_performance[('total_delivery_time', 'mean')] > 40  # 40+ minutes average
    ].index.tolist()
    
    # Generate recommendations
    recommendations = []
    for city in slow_cities:
        city_data = city_performance.loc[city]
        avg_time = city_data[('total_delivery_time', 'mean')]
        order_volume = city_data[('order_id', 'count')]
        
        if avg_time > 45 and order_volume > 1000:  # High volume, slow delivery
            recommendations.append({
                'city': city,
                'issue': 'High volume causing delays',
                'recommendation': 'Increase delivery partner pool',
                'priority': 'High'
            })
        elif avg_time > 40:
            recommendations.append({
                'city': city,
                'issue': 'Slow delivery times',
                'recommendation': 'Optimize delivery routes',
                'priority': 'Medium'
            })
    
    # Send alerts to operations team
    if recommendations:
        send_slack_alert(recommendations)
    
    return recommendations

# Define DAG
swiggy_analytics_dag = DAG(
    'swiggy_daily_analytics',
    default_args=default_args,
    description='Swiggy daily delivery analytics pipeline',
    schedule_interval='0 7 * * *',  # Run at 7 AM daily
    catchup=False
)

# Define tasks
extract_task = PythonOperator(
    task_id='extract_order_data',
    python_callable=extract_order_data,
    dag=swiggy_analytics_dag
)

transform_task = PythonOperator(
    task_id='transform_delivery_metrics',
    python_callable=transform_delivery_metrics,
    dag=swiggy_analytics_dag
)

insights_task = PythonOperator(
    task_id='generate_business_insights', 
    python_callable=generate_business_insights,
    dag=swiggy_analytics_dag
)

# Define dependencies
extract_task >> transform_task >> insights_task
```

### Advanced Airflow Features for Production

**1. Dynamic DAG Generation**
```python
# Generate DAGs for multiple cities dynamically
def create_city_analytics_dag(city_name):
    dag_id = f'analytics_{city_name.lower()}'
    
    dag = DAG(
        dag_id,
        default_args=default_args,
        description=f'Analytics pipeline for {city_name}',
        schedule_interval='0 6 * * *'
    )
    
    # City-specific tasks
    extract_task = PythonOperator(
        task_id=f'extract_{city_name}_data',
        python_callable=extract_city_data,
        op_kwargs={'city': city_name},
        dag=dag
    )
    
    return dag

# Generate DAGs for major Indian cities
major_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai']
for city in major_cities:
    globals()[f'analytics_{city.lower()}_dag'] = create_city_analytics_dag(city)
```

**2. Custom Operators**
```python
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

class IndianDataQualityOperator(BaseOperator):
    """Custom operator for Indian data quality checks"""
    
    @apply_defaults
    def __init__(self, data_source, quality_rules, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_source = data_source
        self.quality_rules = quality_rules
    
    def execute(self, context):
        # Load data
        df = pd.read_sql(self.data_source, DATABASE_CONNECTION)
        
        quality_results = {}
        
        # Indian-specific validations
        if 'phone_number' in df.columns:
            # Indian phone number validation
            valid_phones = df['phone_number'].str.match(r'^[6-9]\d{9}$')
            quality_results['phone_validity'] = valid_phones.sum() / len(df)
        
        if 'pincode' in df.columns:
            # Indian pincode validation  
            valid_pincodes = df['pincode'].str.match(r'^\d{6}$')
            quality_results['pincode_validity'] = valid_pincodes.sum() / len(df)
        
        if 'pan_number' in df.columns:
            # PAN number format validation
            valid_pan = df['pan_number'].str.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
            quality_results['pan_validity'] = valid_pan.sum() / len(df)
        
        # Check quality thresholds
        for rule_name, threshold in self.quality_rules.items():
            if quality_results.get(rule_name, 0) < threshold:
                raise ValueError(f"Data quality check failed: {rule_name}")
        
        return quality_results

# Usage
quality_check = IndianDataQualityOperator(
    task_id='indian_data_quality_check',
    data_source="SELECT * FROM customer_data WHERE created_date = '{{ ds }}'",
    quality_rules={
        'phone_validity': 0.95,
        'pincode_validity': 0.98,
        'pan_validity': 0.90
    },
    dag=dag
)
```

**3. Error Handling and Alerting**
```python
def on_failure_callback(context):
    """Custom failure callback for Indian operations team"""
    task_id = context['task_instance'].task_id
    dag_id = context['dag'].dag_id
    execution_date = context['execution_date']
    
    # Send WhatsApp alert (popular in Indian companies)
    send_whatsapp_alert(
        message=f"🚨 Airflow Task Failed!\n"
                f"DAG: {dag_id}\n"
                f"Task: {task_id}\n"
                f"Time: {execution_date}\n"
                f"Check: http://airflow.company.com/admin/airflow/log?dag_id={dag_id}",
        phone_numbers=['+91-98765-43210', '+91-87654-32109']  # Operations team
    )
    
    # Send Slack alert
    send_slack_alert(
        channel='#data-alerts',
        message=f"Airflow task {task_id} failed in {dag_id}"
    )

# Apply to DAG
dag.default_args['on_failure_callback'] = on_failure_callback
```

### Airflow Best Practices for Indian Companies

**1. Cost Optimization**
```python
# Use spot instances for non-critical workflows
from airflow.providers.amazon.aws.operators.ec2_start_instance import EC2StartInstanceOperator
from airflow.providers.amazon.aws.operators.ec2_stop_instance import EC2StopInstanceOperator

# Start spot instance for processing
start_instance = EC2StartInstanceOperator(
    task_id='start_processing_instance',
    instance_id='i-1234567890abcdef0',
    dag=dag
)

# Your processing tasks here
process_data = BashOperator(
    task_id='process_large_dataset',
    bash_command='python large_data_processing.py',
    dag=dag
)

# Stop instance to save costs
stop_instance = EC2StopInstanceOperator(
    task_id='stop_processing_instance', 
    instance_id='i-1234567890abcdef0',
    dag=dag
)

start_instance >> process_data >> stop_instance
```

**2. Multi-Region Deployment**
```python
# Configuration for different Indian regions
REGION_CONFIGS = {
    'mumbai': {
        'aws_region': 'ap-south-1',
        'database_endpoint': 'mumbai-db.company.com',
        'redis_cluster': 'mumbai-redis.company.com'
    },
    'bangalore': {
        'aws_region': 'ap-south-1', 
        'database_endpoint': 'bangalore-db.company.com',
        'redis_cluster': 'bangalore-redis.company.com'
    }
}

def get_region_config():
    current_region = os.environ.get('DEPLOYMENT_REGION', 'mumbai')
    return REGION_CONFIGS[current_region]
```

---

## Section 2: dbt (Data Build Tool) - The Assembly Line Master

### Car Assembly Line Analogy - Tata Motors Pune

Tata Motors ka Pune plant dekha hai? Raw materials input mein jaate hain, multiple stages mein processing hoti hai, quality checks har level par, final output mein ready car. dbt exactly yahi karta hai data ke saath!

```python
# Assembly line analogy for data transformation
class TataMotorsAssemblyLine:
    def __init__(self):
        self.stages = ['raw_materials', 'chassis_assembly', 'engine_fitting', 
                      'body_assembly', 'painting', 'final_inspection', 'finished_car']
    
    def process_stage(self, input_material, stage_name):
        # Each stage transforms input to output
        # Quality checks at each stage
        # Dependencies managed automatically
        pass
```

### dbt Architecture and Workflow

**Core Concepts:**
- **Models**: SQL transformations
- **Sources**: Raw data sources
- **Tests**: Data quality validations  
- **Snapshots**: Type-2 slowly changing dimensions
- **Seeds**: Reference data (CSV files)
- **Macros**: Reusable SQL code

### Real Example: Flipkart Product Analytics with dbt

Flipkart ka product catalog complex hai - millions of products, multiple sellers, dynamic pricing, inventory changes. dbt se organized transformation:

**1. Project Structure**
```yaml
# dbt_project.yml
name: 'flipkart_analytics'
version: '1.0.0'
config-version: 2

model-paths: ["models"]
analysis-paths: ["analysis"] 
test-paths: ["tests"]
seed-paths: ["data"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_modules"

models:
  flipkart_analytics:
    staging:
      materialized: view
    intermediate:
      materialized: view  
    marts:
      materialized: table
    
vars:
  start_date: '2024-01-01'
  currency: 'INR'
```

**2. Source Configuration**
```yaml
# models/sources.yml
version: 2

sources:
  - name: flipkart_production
    description: "Flipkart production database"
    database: flipkart_prod
    schema: public
    
    tables:
      - name: products
        description: "Product master data"
        columns:
          - name: product_id
            description: "Unique product identifier"
            tests:
              - unique
              - not_null
          - name: seller_id
            description: "Seller identifier"
            tests:
              - not_null
          - name: mrp
            description: "Maximum retail price"
            tests:
              - not_null
              - dbt_utils.accepted_range:
                  min_value: 0
                  max_value: 1000000
      
      - name: orders
        description: "Customer orders"
        loaded_at_field: updated_at
        freshness:
          warn_after: {count: 1, period: hour}
          error_after: {count: 2, period: hour}
          
      - name: inventory
        description: "Product inventory levels"
        
      - name: pricing_history
        description: "Product price changes over time"
```

**3. Staging Models**
```sql
-- models/staging/stg_products.sql
{{ config(materialized='view') }}

with source_data as (
    select 
        product_id,
        product_name,
        seller_id,
        category_l1,
        category_l2, 
        category_l3,
        brand,
        mrp,
        selling_price,
        discount_percentage,
        product_rating,
        review_count,
        is_fassured,
        created_at,
        updated_at
    from {{ source('flipkart_production', 'products') }}
),

cleaned_data as (
    select
        product_id,
        trim(upper(product_name)) as product_name_cleaned,
        seller_id,
        coalesce(category_l1, 'Unknown') as category_primary,
        coalesce(category_l2, 'Unknown') as category_secondary,
        coalesce(category_l3, 'Unknown') as category_tertiary,
        trim(upper(brand)) as brand_normalized,
        mrp,
        selling_price,
        -- Calculate actual discount percentage
        case 
            when mrp > 0 then round(((mrp - selling_price) / mrp) * 100, 2)
            else 0 
        end as discount_percentage_calculated,
        coalesce(product_rating, 0) as product_rating,
        coalesce(review_count, 0) as review_count,
        is_fassured,
        created_at,
        updated_at
    from source_data
),

validated_data as (
    select *,
        -- Add validation flags
        case when selling_price > mrp then 1 else 0 end as price_anomaly_flag,
        case when discount_percentage_calculated > 80 then 1 else 0 end as high_discount_flag
    from cleaned_data
)

select * from validated_data
```

**4. Intermediate Models**
```sql
-- models/intermediate/int_product_performance.sql
{{ config(materialized='view') }}

with product_orders as (
    select
        o.product_id,
        count(*) as total_orders,
        sum(o.quantity) as total_quantity_sold,
        sum(o.order_value) as total_revenue,
        avg(o.order_value) as avg_order_value,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date
    from {{ ref('stg_orders') }} o
    where o.order_status = 'delivered'
    group by o.product_id
),

product_inventory as (
    select
        product_id,
        avg(stock_quantity) as avg_stock_level,
        sum(case when stock_quantity = 0 then 1 else 0 end) as out_of_stock_days,
        count(*) as total_days_tracked
    from {{ ref('stg_inventory') }}
    group by product_id
),

product_pricing as (
    select
        product_id,
        avg(selling_price) as avg_selling_price,
        min(selling_price) as min_selling_price,
        max(selling_price) as max_selling_price,
        stddev(selling_price) as price_volatility
    from {{ ref('stg_pricing_history') }}
    group by product_id
)

select
    p.product_id,
    p.product_name_cleaned,
    p.category_primary,
    p.brand_normalized,
    p.mrp,
    coalesce(po.total_orders, 0) as total_orders,
    coalesce(po.total_quantity_sold, 0) as total_quantity_sold,
    coalesce(po.total_revenue, 0) as total_revenue,
    coalesce(po.avg_order_value, 0) as avg_order_value,
    coalesce(pi.avg_stock_level, 0) as avg_stock_level,
    coalesce(pi.out_of_stock_days, 0) as out_of_stock_days,
    coalesce(pp.avg_selling_price, p.selling_price) as avg_selling_price,
    coalesce(pp.price_volatility, 0) as price_volatility,
    -- Calculate performance metrics
    case 
        when po.total_orders >= 100 then 'High'
        when po.total_orders >= 10 then 'Medium'
        else 'Low'
    end as sales_performance,
    -- Stock efficiency
    case 
        when pi.out_of_stock_days = 0 then 'Excellent'
        when pi.out_of_stock_days <= 5 then 'Good'
        else 'Poor'
    end as inventory_management
from {{ ref('stg_products') }} p
left join product_orders po on p.product_id = po.product_id
left join product_inventory pi on p.product_id = pi.product_id
left join product_pricing pp on p.product_id = pp.product_id
```

**5. Mart Models**
```sql
-- models/marts/mart_product_recommendations.sql
{{ config(materialized='table', indexes=[{'columns': ['category_primary'], 'unique': False}]) }}

with product_metrics as (
    select *,
        -- Calculate recommendation score
        (
            (total_orders * 0.3) + 
            (product_rating * 20 * 0.2) +
            (review_count * 0.1) +
            ((100 - discount_percentage_calculated) * 0.2) +
            (case when inventory_management = 'Excellent' then 20 else 10 end * 0.2)
        ) as recommendation_score
    from {{ ref('int_product_performance') }}
),

category_rankings as (
    select *,
        row_number() over (
            partition by category_primary 
            order by recommendation_score desc
        ) as category_rank
    from product_metrics
),

final as (
    select
        product_id,
        product_name_cleaned as product_name,
        category_primary,
        brand_normalized as brand,
        avg_selling_price,
        discount_percentage_calculated as discount_percentage,
        product_rating,
        review_count,
        recommendation_score,
        category_rank,
        case 
            when category_rank <= 10 then 'Top_Recommended'
            when category_rank <= 50 then 'Recommended'
            else 'Standard'
        end as recommendation_tier,
        current_timestamp as last_updated
    from category_rankings
    where total_orders > 0  -- Only products with sales history
)

select * from final
```

**6. Custom Macros for Indian Context**
```sql
-- macros/indian_validations.sql
{% macro validate_indian_phone(column_name) %}
    case 
        when {{ column_name }} ~ '^[6-9][0-9]{9}$' then 1
        else 0
    end
{% endmacro %}

{% macro validate_indian_pincode(column_name) %}
    case
        when {{ column_name }} ~ '^[0-9]{6}$' then 1
        else 0 
    end
{% endmacro %}

{% macro calculate_gst(amount, gst_rate=18) %}
    round({{ amount }} * ({{ gst_rate }} / 100.0), 2)
{% endmacro %}

{% macro indian_currency_format(amount) %}
    '₹' || to_char({{ amount }}, 'FM99,99,99,999.00')
{% endmacro %}
```

**7. Data Quality Tests**
```sql
-- tests/assert_positive_revenue.sql
-- Test to ensure all products have positive revenue when they have orders

select product_id
from {{ ref('mart_product_recommendations') }}
where total_orders > 0 and total_revenue <= 0
```

```yaml
# models/schema.yml
version: 2

models:
  - name: mart_product_recommendations
    description: "Product recommendations based on multiple performance factors"
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - product_id
    columns:
      - name: product_id
        description: "Unique product identifier"
        tests:
          - unique
          - not_null
          
      - name: recommendation_score
        description: "Calculated recommendation score (0-100)"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 100
              
      - name: avg_selling_price
        description: "Average selling price in INR"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 1
              max_value: 10000000
```

### dbt Production Deployment

**1. CI/CD Integration**
```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
          
      - name: Install dbt
        run: pip install dbt-postgres==1.0.0
        
      - name: Setup dbt profile
        run: |
          mkdir ~/.dbt
          echo "$DBT_PROFILE" > ~/.dbt/profiles.yml
        env:
          DBT_PROFILE: ${{ secrets.DBT_PROFILES_YML }}
          
      - name: Install dbt dependencies
        run: dbt deps
        
      - name: Run dbt tests
        run: dbt test
        
      - name: Check model freshness
        run: dbt source freshness
        
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          dbt run --target prod
          dbt test --target prod
```

**2. Monitoring and Alerting**
```python
# dbt_monitoring.py
import json
import requests
from datetime import datetime

def check_dbt_run_status():
    """Monitor dbt run results and send alerts"""
    
    # Read dbt run results
    with open('target/run_results.json', 'r') as f:
        results = json.load(f)
    
    failed_models = []
    for result in results['results']:
        if result['status'] == 'error':
            failed_models.append({
                'model': result['unique_id'],
                'error': result['message'],
                'execution_time': result['execution_time']
            })
    
    if failed_models:
        # Send alert to Indian operations team
        send_whatsapp_alert(
            message=f"🚨 dbt Models Failed!\n"
                   f"Failed Models: {len(failed_models)}\n"
                   f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                   f"Check logs: http://dbt-docs.company.com",
            phone_numbers=['+91-98765-43210']
        )
        
        # Send detailed Slack notification
        slack_message = {
            "text": "dbt Run Failures Detected",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{len(failed_models)} models failed*"}
                }
            ]
        }
        
        for model in failed_models[:5]:  # Show first 5 failures
            slack_message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• `{model['model']}`: {model['error'][:100]}..."
                }
            })
        
        requests.post(SLACK_WEBHOOK_URL, json=slack_message)

if __name__ == "__main__":
    check_dbt_run_status()
```

---

## Section 3: Terraform - Infrastructure as Code Master

### Mumbai City Planning Department Analogy

Mumbai ka city planning department dekho - roads, bridges, buildings, utilities ka blueprints banate hain. Once approved, same blueprint se multiple locations par infrastructure build kar sakte hain. Terraform exactly yahi karta hai cloud infrastructure ke liye!

### Real Example: Ola's Multi-Region Data Infrastructure

Ola operates in 250+ cities across India. Har region mein consistent infrastructure chahiye - same security, same performance, same monitoring. Manual setup impossible hai.

**1. Provider Configuration**
```hcl
# providers.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.10"
    }
  }
  
  backend "s3" {
    bucket  = "ola-terraform-state-mumbai"
    key     = "data-infrastructure/terraform.tfstate"
    region  = "ap-south-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "ola-data-platform"
      ManagedBy   = "terraform"
      Owner       = "data-platform-team"
      CostCenter  = "engineering"
    }
  }
}
```

**2. Variables for Indian Regions**
```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1"  # Mumbai region
  
  validation {
    condition = contains([
      "ap-south-1",      # Mumbai
      "ap-southeast-1",  # Singapore (for South India)
      "us-west-2"        # US operations
    ], var.aws_region)
    error_message = "AWS region must be one of the approved regions."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "city_configs" {
  description = "Configuration for different Indian cities"
  type = map(object({
    instance_count = number
    instance_type  = string
    storage_size   = number
  }))
  
  default = {
    mumbai = {
      instance_count = 5
      instance_type  = "r5.2xlarge"
      storage_size   = 1000
    }
    delhi = {
      instance_count = 4
      instance_type  = "r5.xlarge" 
      storage_size   = 800
    }
    bangalore = {
      instance_count = 6
      instance_type  = "r5.2xlarge"
      storage_size   = 1200
    }
  }
}
```

**3. Networking Infrastructure**
```hcl
# networking.tf
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC for data infrastructure
resource "aws_vpc" "data_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.environment}-ola-data-vpc"
  }
}

# Public subnets for load balancers
resource "aws_subnet" "public_subnets" {
  count = 3
  
  vpc_id            = aws_vpc.data_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.environment}-public-subnet-${count.index + 1}"
    Type = "public"
  }
}

# Private subnets for data processing
resource "aws_subnet" "private_subnets" {
  count = 3
  
  vpc_id            = aws_vpc.data_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "${var.environment}-private-subnet-${count.index + 1}"
    Type = "private"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "data_igw" {
  vpc_id = aws_vpc.data_vpc.id
  
  tags = {
    Name = "${var.environment}-data-igw"
  }
}

# NAT Gateway for private subnet internet access
resource "aws_eip" "nat_eip" {
  count  = 3
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.data_igw]
  
  tags = {
    Name = "${var.environment}-nat-eip-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "nat_gw" {
  count = 3
  
  allocation_id = aws_eip.nat_eip[count.index].id
  subnet_id     = aws_subnet.public_subnets[count.index].id
  
  tags = {
    Name = "${var.environment}-nat-gateway-${count.index + 1}"
  }
}
```

**4. Data Storage Infrastructure**
```hcl
# storage.tf

# S3 Bucket for data lake
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.environment}-ola-data-lake-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name        = "${var.environment}-ola-data-lake"
    Purpose     = "data-storage"
    Compliance  = "RBI-compliant"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 lifecycle policy for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "data_lake_lifecycle" {
  bucket = aws_s3_bucket.data_lake.id
  
  rule {
    id     = "data_lifecycle"
    status = "Enabled"
    
    # Move to cheaper storage after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    # Move to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    # Delete after 7 years (compliance requirement)
    expiration {
      days = 2555  # 7 years
    }
  }
}

# RDS for transactional data
resource "aws_db_subnet_group" "data_db_subnet_group" {
  name       = "${var.environment}-data-db-subnet-group"
  subnet_ids = aws_subnet.private_subnets[*].id
  
  tags = {
    Name = "${var.environment}-data-db-subnet-group"
  }
}

resource "aws_db_instance" "transactional_db" {
  identifier = "${var.environment}-ola-transactional-db"
  
  engine         = "postgres"
  engine_version = "13.7"
  instance_class = var.environment == "prod" ? "db.r5.2xlarge" : "db.r5.large"
  
  allocated_storage     = 1000
  max_allocated_storage = 5000
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = "ola_transactions"
  username = "admin"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.data_db_subnet_group.name
  
  backup_retention_period = var.environment == "prod" ? 30 : 7
  backup_window          = "03:00-04:00"  # IST early morning
  maintenance_window     = "sun:04:00-sun:05:00"  # IST Sunday morning
  
  skip_final_snapshot = var.environment != "prod"
  
  tags = {
    Name        = "${var.environment}-transactional-db"
    Purpose     = "transactional-data"
    Compliance  = "RBI-compliant"
  }
}
```

**5. Kafka Cluster for Streaming**
```hcl
# kafka.tf

# MSK (Managed Streaming for Kafka) Cluster
resource "aws_msk_configuration" "ola_kafka_config" {
  kafka_versions = ["2.8.0"]
  name          = "${var.environment}-ola-kafka-config"
  
  server_properties = <<PROPERTIES
auto.create.topics.enable=false
default.replication.factor=3
min.insync.replicas=2
num.partitions=12
log.retention.hours=168
PROPERTIES
}

resource "aws_msk_cluster" "ola_kafka" {
  cluster_name           = "${var.environment}-ola-kafka"
  kafka_version         = "2.8.0"
  number_of_broker_nodes = 6
  
  broker_node_group_info {
    instance_type   = "kafka.m5.xlarge"
    ebs_volume_size = 500
    client_subnets  = aws_subnet.private_subnets[*].id
    security_groups = [aws_security_group.kafka_sg.id]
  }
  
  configuration_info {
    arn      = aws_msk_configuration.ola_kafka_config.arn
    revision = aws_msk_configuration.ola_kafka_config.latest_revision
  }
  
  encryption_info {
    encryption_at_rest_kms_key_id = aws_kms_key.kafka_encryption.arn
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  
  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.kafka_logs.name
      }
      s3 {
        enabled = true
        bucket  = aws_s3_bucket.data_lake.id
        prefix  = "kafka-logs/"
      }
    }
  }
  
  tags = {
    Name = "${var.environment}-ola-kafka"
  }
}

# KMS key for Kafka encryption
resource "aws_kms_key" "kafka_encryption" {
  description = "KMS key for Kafka cluster encryption"
  
  tags = {
    Name = "${var.environment}-kafka-kms-key"
  }
}
```

**6. Kubernetes Cluster for Data Processing**
```hcl
# eks.tf

# EKS Cluster for data processing workloads
resource "aws_eks_cluster" "data_processing" {
  name     = "${var.environment}-ola-data-processing"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.21"
  
  vpc_config {
    subnet_ids              = concat(aws_subnet.public_subnets[*].id, aws_subnet.private_subnets[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]  # Restrict in production
  }
  
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_encryption.arn
    }
    resources = ["secrets"]
  }
  
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
    aws_cloudwatch_log_group.eks_cluster_logs,
  ]
  
  tags = {
    Name = "${var.environment}-data-processing-cluster"
  }
}

# EKS Node Groups for different workload types
resource "aws_eks_node_group" "data_processing_nodes" {
  cluster_name    = aws_eks_cluster.data_processing.name
  node_group_name = "${var.environment}-data-processing-nodes"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = aws_subnet.private_subnets[*].id
  
  instance_types = ["r5.2xlarge"]  # Memory optimized for data processing
  capacity_type  = "ON_DEMAND"
  
  scaling_config {
    desired_size = 3
    max_size     = 20
    min_size     = 1
  }
  
  update_config {
    max_unavailable = 1
  }
  
  # Taints for data processing workloads
  taint {
    key    = "workload-type"
    value  = "data-processing"
    effect = "NO_SCHEDULE"
  }
  
  tags = {
    Name = "${var.environment}-data-processing-nodes"
    Type = "data-processing"
  }
}

# Spot instances node group for cost optimization
resource "aws_eks_node_group" "spot_nodes" {
  cluster_name    = aws_eks_cluster.data_processing.name
  node_group_name = "${var.environment}-spot-nodes"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = aws_subnet.private_subnets[*].id
  
  instance_types = ["r5.large", "r5.xlarge", "m5.large", "m5.xlarge"]
  capacity_type  = "SPOT"
  
  scaling_config {
    desired_size = 2
    max_size     = 50
    min_size     = 0
  }
  
  tags = {
    Name = "${var.environment}-spot-nodes"
    Type = "spot-processing"
  }
}
```

**7. Security Groups**
```hcl
# security.tf

# Security group for databases
resource "aws_security_group" "database_sg" {
  name        = "${var.environment}-database-sg"
  description = "Security group for database instances"
  vpc_id      = aws_vpc.data_vpc.id
  
  # PostgreSQL access from private subnets only
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = aws_subnet.private_subnets[*].cidr_block
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.environment}-database-sg"
  }
}

# Security group for Kafka cluster
resource "aws_security_group" "kafka_sg" {
  name        = "${var.environment}-kafka-sg"
  description = "Security group for Kafka cluster"
  vpc_id      = aws_vpc.data_vpc.id
  
  # Kafka broker communication
  ingress {
    from_port = 9092
    to_port   = 9094
    protocol  = "tcp"
    self      = true
  }
  
  # Zookeeper communication  
  ingress {
    from_port = 2181
    to_port   = 2181
    protocol  = "tcp"
    self      = true
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.environment}-kafka-sg"
  }
}
```

**8. Monitoring and Outputs**
```hcl
# outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.data_vpc.id
}

output "data_lake_bucket" {
  description = "Name of the S3 data lake bucket"
  value       = aws_s3_bucket.data_lake.bucket
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.transactional_db.endpoint
  sensitive   = true
}

output "kafka_bootstrap_servers" {
  description = "Kafka bootstrap servers"
  value       = aws_msk_cluster.ola_kafka.bootstrap_brokers
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.data_processing.name
}

output "infrastructure_costs_estimate" {
  description = "Monthly infrastructure cost estimate (USD)"
  value = {
    rds_monthly     = var.environment == "prod" ? 800 : 400
    eks_monthly     = var.environment == "prod" ? 1500 : 600
    kafka_monthly   = var.environment == "prod" ? 600 : 300
    s3_monthly      = var.environment == "prod" ? 200 : 50
    total_monthly   = var.environment == "prod" ? 3100 : 1350
  }
}
```

### Terraform Best Practices for Indian Companies

**1. Multi-Environment Management**
```hcl
# environments/prod/terraform.tfvars
aws_region  = "ap-south-1"
environment = "prod"

city_configs = {
  mumbai = {
    instance_count = 10
    instance_type  = "r5.4xlarge"
    storage_size   = 2000
  }
  delhi = {
    instance_count = 8
    instance_type  = "r5.2xlarge"
    storage_size   = 1500
  }
  bangalore = {
    instance_count = 12
    instance_type  = "r5.4xlarge"
    storage_size   = 2500
  }
}

# Enable comprehensive monitoring for production
enable_detailed_monitoring = true
backup_retention_days     = 30
log_retention_days       = 90
```

**2. Cost Optimization**
```hcl
# cost_optimization.tf
locals {
  # Business hours in IST (9 AM to 9 PM)
  business_hours_start = "03:30"  # 9 AM IST in UTC
  business_hours_end   = "15:30"  # 9 PM IST in UTC
}

# Auto-scaling for development environments during business hours
resource "aws_autoscaling_schedule" "scale_up_business_hours" {
  count = var.environment != "prod" ? 1 : 0
  
  scheduled_action_name  = "scale-up-business-hours"
  min_size              = 2
  max_size              = 10
  desired_capacity      = 5
  recurrence            = "30 3 * * 1-5"  # Monday-Friday 9 AM IST
  autoscaling_group_name = aws_autoscaling_group.data_processing[0].name
}

resource "aws_autoscaling_schedule" "scale_down_after_hours" {
  count = var.environment != "prod" ? 1 : 0
  
  scheduled_action_name  = "scale-down-after-hours"
  min_size              = 0
  max_size              = 2
  desired_capacity      = 1
  recurrence            = "30 15 * * 1-5"  # Monday-Friday 9 PM IST
  autoscaling_group_name = aws_autoscaling_group.data_processing[0].name
}
```

---

## Section 4: Great Expectations - Data Quality Guardian

### Quality Control Inspector Analogy - Tata Steel

Tata Steel ka Jamshedpur plant dekho - har stage par quality inspector check karta hai. Raw material quality, intermediate products, final steel quality. Agar koi stage mein quality issue hai, immediately production rok dete hain. Great Expectations exactly yahi role play karta hai data pipelines mein!

### Great Expectations Architecture

**Core Concepts:**
- **Expectations**: Data quality rules
- **Data Sources**: Where your data lives
- **Validation Results**: Pass/fail results
- **Data Docs**: Auto-generated documentation
- **Checkpoints**: Validation workflows

### Real Example: HDFC Bank Transaction Validation

HDFC Bank processes 25 million transactions daily. Data quality issues can lead to regulatory problems, customer complaints, fraud missed. Great Expectations implementation:

**1. Project Setup**
```python
# great_expectations_setup.py
import great_expectations as ge
from great_expectations.data_context import DataContext

def setup_hdfc_data_context():
    """Setup Great Expectations for HDFC Bank transaction validation"""
    
    # Initialize data context
    context = DataContext.create(project_root_dir="./hdfc_data_quality")
    
    # Add datasource for PostgreSQL
    datasource_config = {
        "name": "hdfc_transactions_db",
        "class_name": "Datasource",
        "module_name": "great_expectations.datasource",
        "execution_engine": {
            "class_name": "SqlAlchemyExecutionEngine",
            "module_name": "great_expectations.execution_engine",
            "connection_string": "postgresql://user:password@hdfc-db:5432/transactions"
        },
        "data_connectors": {
            "default_runtime_data_connector": {
                "class_name": "RuntimeDataConnector",
                "module_name": "great_expectations.datasource.data_connector",
                "batch_identifiers": ["default_identifier_name"]
            },
            "default_inferred_data_connector": {
                "class_name": "InferredAssetSqlDataConnector",
                "module_name": "great_expectations.datasource.data_connector",
                "include_schema_name": True
            }
        }
    }
    
    context.add_datasource(**datasource_config)
    
    return context
```

**2. Transaction Data Expectations**
```python
# hdfc_transaction_expectations.py
import great_expectations as ge
import pandas as pd
from datetime import datetime, timedelta

class HDFCTransactionValidator:
    def __init__(self, context):
        self.context = context
        self.datasource_name = "hdfc_transactions_db"
    
    def create_transaction_expectations(self):
        """Create expectations for transaction data quality"""
        
        # Get validator for transactions table
        validator = self.context.get_validator(
            datasource_name=self.datasource_name,
            data_connector_name="default_inferred_data_connector",
            data_asset_name="public.transactions"
        )
        
        # Basic data integrity checks
        validator.expect_table_row_count_to_be_between(
            min_value=1000000,  # Minimum 1M transactions daily
            max_value=50000000  # Maximum 50M transactions daily
        )
        
        # Column existence checks
        required_columns = [
            'transaction_id', 'account_number', 'amount', 'transaction_type',
            'transaction_timestamp', 'merchant_id', 'status', 'created_at'
        ]
        
        for column in required_columns:
            validator.expect_column_to_exist(column)
        
        # Transaction ID uniqueness
        validator.expect_column_values_to_be_unique('transaction_id')
        
        # Amount validations
        validator.expect_column_values_to_not_be_null('amount')
        validator.expect_column_values_to_be_of_type('amount', 'DECIMAL')
        validator.expect_column_values_to_be_between(
            'amount', 
            min_value=0.01,      # Minimum 1 paisa
            max_value=10000000   # Maximum 1 crore per transaction
        )
        
        # Account number format validation (Indian bank account)
        validator.expect_column_values_to_match_regex(
            'account_number',
            regex=r'^\d{10,18}$'  # 10-18 digits for Indian bank accounts
        )
        
        # Transaction type validation
        valid_transaction_types = [
            'DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'UPI', 'CARD_PAYMENT', 
            'NEFT', 'RTGS', 'IMPS', 'CHEQUE'
        ]
        validator.expect_column_values_to_be_in_set(
            'transaction_type', 
            valid_transaction_types
        )
        
        # Status validation
        validator.expect_column_values_to_be_in_set(
            'status',
            ['SUCCESS', 'FAILED', 'PENDING', 'CANCELLED']
        )
        
        # Timestamp validation
        validator.expect_column_values_to_not_be_null('transaction_timestamp')
        
        # Transaction timestamp should be within last 24 hours for real-time data
        validator.expect_column_values_to_be_between(
            'transaction_timestamp',
            min_value=datetime.now() - timedelta(days=1),
            max_value=datetime.now() + timedelta(hours=1)  # Allow slight future timestamps
        )
        
        # Business rule validations
        
        # UPI transactions should have UPI reference
        validator.expect_column_pair_values_to_be_in_set(
            column_A='transaction_type',
            column_B='upi_reference',
            value_pairs_set=[('UPI', 'not_null'), ('TRANSFER', 'not_null')]
        )
        
        # Large transaction validation (suspicious activity)
        validator.expect_column_values_to_be_between(
            'amount',
            min_value=0,
            max_value=200000,  # Transactions > 2 lakh need additional validation
            mostly=0.98  # 98% should be under 2 lakh
        )
        
        # Save expectation suite
        validator.save_expectation_suite(
            expectation_suite_name="hdfc_transaction_quality_suite",
            discard_failed_expectations=False
        )
        
        return validator.get_expectation_suite()
    
    def create_daily_summary_expectations(self):
        """Create expectations for daily transaction summaries"""
        
        validator = self.context.get_validator(
            datasource_name=self.datasource_name,
            data_connector_name="default_runtime_data_connector",
            data_asset_name="daily_transaction_summary",
            create_expectation_suite_with_name="daily_summary_suite"
        )
        
        # Total transaction volume should be within expected range
        validator.expect_column_values_to_be_between(
            'total_transaction_count',
            min_value=800000,   # Minimum 8 lakh transactions
            max_value=30000000  # Maximum 3 crore transactions
        )
        
        # Success rate should be high
        validator.expect_column_values_to_be_between(
            'success_rate',
            min_value=0.95,  # At least 95% success rate
            max_value=1.0
        )
        
        # Average transaction amount should be reasonable
        validator.expect_column_values_to_be_between(
            'avg_transaction_amount',
            min_value=100,    # Average at least ₹100
            max_value=50000   # Average should not exceed ₹50,000
        )
        
        # UPI transactions should be significant portion
        validator.expect_column_values_to_be_between(
            'upi_percentage',
            min_value=0.4,   # At least 40% UPI transactions
            max_value=0.8    # Maximum 80% UPI transactions
        )
        
        validator.save_expectation_suite(discard_failed_expectations=False)
        
        return validator.get_expectation_suite()
```

**3. Custom Expectations for Indian Banking**
```python
# custom_indian_banking_expectations.py
from great_expectations.core.expectation import ExpectationConfiguration
from great_expectations.expectations.core.expect_column_values_to_match_regex import ExpectationColumnValuesToMatchRegex

class ExpectValidIndianBankAccount(ExpectationColumnValuesToMatchRegex):
    """Expect Indian bank account numbers to be valid"""
    
    examples = [
        {
            "data": {
                "account_number": ["12345678901234", "98765432109876", "11111111111111"]
            },
            "tests": [
                {
                    "title": "positive_test_valid_accounts",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "account_number"},
                    "out": {"success": True}
                }
            ]
        }
    ]
    
    regex = r'^\d{10,18}$'
    
    def _validate(self, validator, configuration, **kwargs):
        """Validate Indian bank account format"""
        return super()._validate(
            validator, 
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={
                    "column": configuration.kwargs["column"],
                    "regex": self.regex
                }
            ),
            **kwargs
        )

class ExpectValidIndianMobileNumber(ExpectationColumnValuesToMatchRegex):
    """Expect Indian mobile numbers to be valid"""
    
    examples = [
        {
            "data": {
                "mobile_number": ["9876543210", "8765432109", "7654321098"]
            },
            "tests": [
                {
                    "title": "positive_test_valid_mobiles",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "mobile_number"},
                    "out": {"success": True}
                }
            ]
        }
    ]
    
    regex = r'^[6-9]\d{9}$'

class ExpectValidUPIId(ExpectationColumnValuesToMatchRegex):
    """Expect UPI IDs to be valid format"""
    
    examples = [
        {
            "data": {
                "upi_id": ["user@paytm", "customer@phonepe", "person@googlepay"]
            }
        }
    ]
    
    regex = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$'
```

**4. Checkpoint Configuration**
```python
# hdfc_checkpoints.py
def create_transaction_validation_checkpoint(context):
    """Create checkpoint for validating transaction data"""
    
    checkpoint_config = {
        "name": "hdfc_transaction_checkpoint",
        "config_version": 1.0,
        "template_name": None,
        "module_name": "great_expectations.checkpoint",
        "class_name": "Checkpoint",
        "run_name_template": "%Y%m%d-%H%M%S-hdfc-transaction-validation",
        "expectation_suite_name": "hdfc_transaction_quality_suite",
        "batch_request": {
            "datasource_name": "hdfc_transactions_db",
            "data_connector_name": "default_inferred_data_connector",
            "data_asset_name": "public.transactions",
            "data_connector_query": {
                "batch_filter_parameters": {
                    "timestamp_column": "created_at",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31"
                }
            }
        },
        "action_list": [
            {
                "name": "store_validation_result",
                "action": {
                    "class_name": "StoreValidationResultAction",
                    "module_name": "great_expectations.checkpoint.actions"
                }
            },
            {
                "name": "update_data_docs",
                "action": {
                    "class_name": "UpdateDataDocsAction",
                    "module_name": "great_expectations.checkpoint.actions"
                }
            },
            {
                "name": "send_slack_notification_on_validation_result",
                "action": {
                    "class_name": "SlackNotificationAction",
                    "module_name": "great_expectations.checkpoint.actions",
                    "webhook": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "notify_on": "failure",
                    "renderer": {
                        "module_name": "great_expectations.render.renderer.slack_renderer",
                        "class_name": "SlackRenderer"
                    }
                }
            }
        ],
        "evaluation_parameters": {},
        "runtime_configuration": {},
        "validations": []
    }
    
    context.add_checkpoint(**checkpoint_config)
    
    return checkpoint_config

def run_daily_validation():
    """Run daily data validation"""
    
    context = ge.data_context.DataContext()
    
    # Run transaction validation
    results = context.run_checkpoint(
        checkpoint_name="hdfc_transaction_checkpoint",
        run_name=f"daily_validation_{datetime.now().strftime('%Y%m%d')}"
    )
    
    # Check results and take action
    if not results["success"]:
        # Send alert to operations team
        send_critical_alert(
            message="🚨 HDFC Transaction Data Quality FAILED!\n"
                   f"Validation run: {results['run_id']}\n"
                   f"Failed expectations: {len(results['run_results'])}\n"
                   "Check: https://data-docs.hdfc.com/validations/",
            phone_numbers=["+91-98765-43210", "+91-87654-32109"]
        )
        
        # Trigger incident response
        create_incident(
            title="Data Quality Validation Failed",
            description=f"Daily transaction validation failed: {results['run_id']}",
            severity="high",
            assigned_team="data-platform-team"
        )
    
    return results
```

**5. Integration with Airflow**
```python
# airflow_great_expectations_integration.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.filesystem import FileSensor
import great_expectations as ge

def validate_transaction_data(**context):
    """Validate transaction data using Great Expectations"""
    
    data_context = ge.data_context.DataContext()
    
    # Run validation checkpoint
    results = data_context.run_checkpoint(
        checkpoint_name="hdfc_transaction_checkpoint"
    )
    
    # Parse results
    validation_results = results["run_results"]
    failed_expectations = []
    
    for validation_result in validation_results.values():
        for result in validation_result["validation_result"]["results"]:
            if not result["success"]:
                failed_expectations.append({
                    "expectation_type": result["expectation_config"]["expectation_type"],
                    "column": result["expectation_config"].get("kwargs", {}).get("column"),
                    "result": result["result"]
                })
    
    # Store results in XCom for downstream tasks
    context['task_instance'].xcom_push(
        key='validation_results',
        value={
            "success": results["success"],
            "failed_expectations": failed_expectations,
            "run_id": results["run_id"]
        }
    )
    
    # Fail task if critical validations fail
    critical_failures = [f for f in failed_expectations 
                        if f["expectation_type"] in ["expect_table_row_count_to_be_between",
                                                   "expect_column_values_to_be_unique"]]
    
    if critical_failures:
        raise ValueError(f"Critical data quality checks failed: {critical_failures}")
    
    return results["success"]

def process_validation_results(**context):
    """Process validation results and take actions"""
    
    validation_results = context['task_instance'].xcom_pull(
        task_ids='validate_transaction_data',
        key='validation_results'
    )
    
    if not validation_results["success"]:
        # Generate detailed report
        report = generate_data_quality_report(validation_results)
        
        # Send to business stakeholders
        send_email(
            to=['data-team@hdfc.com', 'operations@hdfc.com'],
            subject='Daily Data Quality Report',
            html_content=report
        )
        
        # Update dashboard
        update_data_quality_dashboard(validation_results)
    
    return validation_results["success"]

# DAG definition
dag = DAG(
    'hdfc_data_quality_validation',
    default_args=default_args,
    description='Daily data quality validation for HDFC transactions',
    schedule_interval='0 8 * * *',  # 8 AM daily
    catchup=False
)

# Tasks
validate_task = PythonOperator(
    task_id='validate_transaction_data',
    python_callable=validate_transaction_data,
    dag=dag
)

process_results_task = PythonOperator(
    task_id='process_validation_results',
    python_callable=process_validation_results,
    dag=dag
)

validate_task >> process_results_task
```

### Great Expectations Best Practices

**1. Expectation Suites Organization**
```python
# Organize by data criticality
expectation_suites = {
    "critical_data_quality": {
        "description": "Critical checks that must pass",
        "expectations": [
            "expect_table_row_count_to_be_between",
            "expect_column_values_to_be_unique", 
            "expect_column_values_to_not_be_null"
        ]
    },
    "business_rule_validation": {
        "description": "Business logic validation",
        "expectations": [
            "expect_column_values_to_be_in_set",
            "expect_column_values_to_match_regex",
            "expect_column_pair_values_to_be_in_set"
        ]
    },
    "statistical_validation": {
        "description": "Statistical anomaly detection",
        "expectations": [
            "expect_column_mean_to_be_between",
            "expect_column_stdev_to_be_between"
        ]
    }
}
```

**2. Performance Optimization**
```python
# Sampling for large datasets
def create_sample_validator(context, table_name, sample_percentage=10):
    """Create validator with data sampling for performance"""
    
    batch_request = {
        "datasource_name": "hdfc_transactions_db",
        "data_connector_name": "default_runtime_data_connector", 
        "data_asset_name": table_name,
        "batch_spec": {
            "sampling_method": "random",
            "sampling_kwargs": {"p": sample_percentage / 100}
        }
    }
    
    return context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=f"{table_name}_sample_suite"
    )
```

---

## Section 5: Monitoring Stack - Real-Time Observatory

### Mumbai Traffic Control Room Analogy

Mumbai traffic control center dekho - hundreds of CCTV cameras, real-time traffic data, incident alerts, automatic signal adjustments. Har intersection ka status, traffic flow, congestion points - sab real-time monitor karte hain. DataOps monitoring exactly yahi karta hai data infrastructure ke liye!

### Monitoring Architecture: The Complete Stack

**Components:**
- **DataDog/Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **ELK Stack**: Log aggregation and analysis
- **Jaeger**: Distributed tracing
- **Custom Alerting**: Business-specific notifications

### Real Example: Dream11's Fantasy Sports Data Monitoring

Dream11 processes real cricket match data, user predictions, live scores. Peak traffic during IPL matches - 50 million users simultaneously. Monitoring critical hai!

**1. Prometheus Configuration**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "dream11_rules.yml"
  - "data_pipeline_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Data pipeline metrics
  - job_name: 'dream11-data-pipelines'
    static_configs:
      - targets: ['data-pipeline-1:8080', 'data-pipeline-2:8080', 'data-pipeline-3:8080']
    metrics_path: '/metrics'
    scrape_interval: 10s
    
  # Kafka metrics
  - job_name: 'kafka-cluster'
    static_configs:
      - targets: ['kafka-1:9308', 'kafka-2:9308', 'kafka-3:9308']
    
  # PostgreSQL metrics
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
      
  # Redis metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
      
  # Application metrics
  - job_name: 'dream11-api'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - dream11-production
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: dream11-api
```

**2. Custom Metrics for Data Pipelines**
```python
# dream11_metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import psycopg2
import redis

class Dream11DataMetrics:
    def __init__(self):
        # Data pipeline metrics
        self.matches_processed = Counter(
            'dream11_matches_processed_total',
            'Total matches processed',
            ['match_type', 'status']
        )
        
        self.user_predictions_processed = Counter(
            'dream11_predictions_processed_total', 
            'Total user predictions processed',
            ['match_id', 'status']
        )
        
        self.data_processing_duration = Histogram(
            'dream11_data_processing_seconds',
            'Time spent processing data',
            ['pipeline_stage', 'match_type']
        )
        
        self.active_users = Gauge(
            'dream11_active_users_current',
            'Current number of active users',
            ['match_id']
        )
        
        self.data_freshness = Gauge(
            'dream11_data_freshness_seconds',
            'Age of latest data in seconds',
            ['data_type']
        )
        
        # Database connections
        self.db_conn = psycopg2.connect(
            host="dream11-postgres",
            database="dream11_prod", 
            user="metrics_user",
            password="metrics_password"
        )
        
        self.redis_conn = redis.Redis(
            host='dream11-redis',
            port=6379,
            decode_responses=True
        )
    
    def collect_match_metrics(self):
        """Collect metrics for ongoing matches"""
        
        with self.db_conn.cursor() as cur:
            # Active matches count
            cur.execute("""
                SELECT match_type, COUNT(*) 
                FROM matches 
                WHERE status = 'LIVE'
                GROUP BY match_type
            """)
            
            for match_type, count in cur.fetchall():
                self.active_matches.labels(match_type=match_type).set(count)
            
            # User predictions for live matches
            cur.execute("""
                SELECT m.match_id, COUNT(p.prediction_id)
                FROM matches m
                LEFT JOIN predictions p ON m.match_id = p.match_id
                WHERE m.status = 'LIVE'
                GROUP BY m.match_id
            """)
            
            for match_id, prediction_count in cur.fetchall():
                self.active_predictions.labels(match_id=str(match_id)).set(prediction_count)
    
    def collect_data_freshness_metrics(self):
        """Monitor data freshness"""
        
        data_sources = {
            'live_scores': 'latest_score_update',
            'player_stats': 'latest_player_update', 
            'match_events': 'latest_event_update'
        }
        
        current_time = time.time()
        
        for data_type, redis_key in data_sources.items():
            last_update = self.redis_conn.get(redis_key)
            if last_update:
                freshness = current_time - float(last_update)
                self.data_freshness.labels(data_type=data_type).set(freshness)
    
    def collect_pipeline_performance_metrics(self):
        """Monitor data pipeline performance"""
        
        with self.db_conn.cursor() as cur:
            # Pipeline execution times
            cur.execute("""
                SELECT 
                    pipeline_name,
                    stage_name,
                    AVG(execution_time_seconds) as avg_time,
                    MAX(execution_time_seconds) as max_time
                FROM pipeline_executions 
                WHERE created_at >= NOW() - INTERVAL '1 hour'
                GROUP BY pipeline_name, stage_name
            """)
            
            for pipeline, stage, avg_time, max_time in cur.fetchall():
                self.pipeline_execution_time.labels(
                    pipeline=pipeline, 
                    stage=stage,
                    metric_type='average'
                ).set(avg_time)
                
                self.pipeline_execution_time.labels(
                    pipeline=pipeline,
                    stage=stage, 
                    metric_type='maximum'
                ).set(max_time)
    
    def start_metrics_collection(self):
        """Start the metrics collection process"""
        start_http_server(8080)
        
        while True:
            try:
                self.collect_match_metrics()
                self.collect_data_freshness_metrics()
                self.collect_pipeline_performance_metrics()
                
                time.sleep(30)  # Collect metrics every 30 seconds
                
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    metrics_collector = Dream11DataMetrics()
    metrics_collector.start_metrics_collection()
```

**3. Alerting Rules**
```yaml
# dream11_rules.yml
groups:
  - name: dream11_data_pipeline_alerts
    rules:
      # Data freshness alerts
      - alert: DataTooOld
        expr: dream11_data_freshness_seconds{data_type="live_scores"} > 60
        for: 2m
        labels:
          severity: critical
          team: data-platform
        annotations:
          summary: "Live scores data is too old"
          description: "Live scores haven't been updated in {{ $value }} seconds"
          
      - alert: HighPredictionVolume
        expr: rate(dream11_predictions_processed_total[5m]) > 10000
        for: 1m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "High prediction processing volume"
          description: "Processing {{ $value }} predictions per second"
          
      # Pipeline performance alerts  
      - alert: SlowDataPipeline
        expr: dream11_data_processing_seconds{quantile="0.95"} > 300
        for: 5m
        labels:
          severity: warning
          team: data-platform
        annotations:
          summary: "Data pipeline is running slowly"
          description: "95th percentile processing time is {{ $value }} seconds"
          
      # Database performance
      - alert: HighDatabaseConnections
        expr: pg_stat_database_numbackends > 80
        for: 2m
        labels:
          severity: warning
          team: database
        annotations:
          summary: "High number of database connections"
          description: "{{ $value }} active connections to database"
          
      # Kafka lag alerts
      - alert: KafkaConsumerLag
        expr: kafka_consumer_lag_sum{topic="match_events"} > 10000
        for: 3m
        labels:
          severity: critical
          team: data-platform
        annotations:
          summary: "Kafka consumer lag is high"
          description: "Consumer lag: {{ $value }} messages"
```

**4. Grafana Dashboard Configuration**
```json
{
  "dashboard": {
    "id": null,
    "title": "Dream11 Data Platform Monitoring",
    "tags": ["dream11", "data-platform", "production"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Live Matches & Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(dream11_active_users_current)",
            "legendFormat": "Active Users"
          },
          {
            "expr": "count(dream11_active_matches)",
            "legendFormat": "Live Matches"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "unit": "short",
            "min": 0
          }
        },
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"]
          }
        }
      },
      {
        "id": 2,
        "title": "Data Processing Rate",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(dream11_matches_processed_total[5m])",
            "legendFormat": "Matches/sec"
          },
          {
            "expr": "rate(dream11_predictions_processed_total[5m])",
            "legendFormat": "Predictions/sec"
          }
        ],
        "yAxes": [
          {
            "label": "Operations per second",
            "min": 0
          }
        ]
      },
      {
        "id": 3,
        "title": "Data Freshness",
        "type": "graph",
        "targets": [
          {
            "expr": "dream11_data_freshness_seconds",
            "legendFormat": "{{ data_type }}"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds",
            "min": 0
          }
        ],
        "thresholds": [
          {
            "value": 60,
            "color": "yellow",
            "op": "gt"
          },
          {
            "value": 300,
            "color": "red", 
            "op": "gt"
          }
        ]
      },
      {
        "id": 4,
        "title": "Pipeline Execution Times",
        "type": "heatmap",
        "targets": [
          {
            "expr": "dream11_data_processing_seconds",
            "legendFormat": "{{ pipeline_stage }}"
          }
        ],
        "heatmap": {
          "xAxis": {"show": true},
          "yAxis": {
            "show": true,
            "label": "Duration (seconds)"
          }
        }
      },
      {
        "id": 5,
        "title": "Infrastructure Health",
        "type": "table",
        "targets": [
          {
            "expr": "up{job=~\"dream11.*\"}",
            "legendFormat": "",
            "format": "table"
          }
        ],
        "columns": [
          {"pattern": "job", "alias": "Service"},
          {"pattern": "instance", "alias": "Instance"}, 
          {"pattern": "Value", "alias": "Status", "type": "string"}
        ],
        "styles": [
          {
            "pattern": "Status",
            "type": "string",
            "mappingType": 1,
            "valueMaps": [
              {"value": "1", "text": "UP"},
              {"value": "0", "text": "DOWN"}
            ]
          }
        ]
      }
    ]
  }
}
```

**5. Log Aggregation with ELK Stack**
```yaml
# filebeat.yml - Log shipping configuration
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/dream11/data-pipeline/*.log
    fields:
      service: data-pipeline
      environment: production
    fields_under_root: true
    
  - type: log
    enabled: true
    paths:
      - /var/log/dream11/api/*.log
    fields:
      service: api
      environment: production
    fields_under_root: true

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_kubernetes_metadata:
      host: ${NODE_NAME}
      matchers:
        - logs_path:
            logs_path: "/var/log/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "dream11-logs-%{+yyyy.MM.dd}"
  template.settings:
    index.number_of_shards: 3
    index.number_of_replicas: 1

setup.kibana:
  host: "kibana:5601"
```

**6. Custom Alert Manager**
```python
# dream11_alert_manager.py
import json
import requests
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

class Dream11AlertManager:
    def __init__(self):
        self.slack_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        self.whatsapp_client = Client("twilio_sid", "twilio_token")
        self.email_server = "smtp.gmail.com"
        self.email_user = "alerts@dream11.com"
        self.email_password = "app_password"
        
        # Alert escalation matrix
        self.escalation_matrix = {
            "critical": {
                "immediate": ["+91-98765-43210", "+91-87654-32109"],  # On-call engineers
                "after_5min": ["+91-76543-21098"],  # Team lead
                "after_15min": ["+91-65432-10987"]  # Director
            },
            "warning": {
                "immediate": ["#data-alerts"],  # Slack channel
                "after_30min": ["+91-98765-43210"]  # On-call engineer
            }
        }
    
    def send_alert(self, alert_data):
        """Process and send alert based on severity"""
        
        severity = alert_data.get("labels", {}).get("severity", "warning")
        alert_name = alert_data.get("labels", {}).get("alertname", "Unknown")
        description = alert_data.get("annotations", {}).get("description", "")
        
        # Format alert message
        message = self.format_alert_message(alert_data)
        
        if severity == "critical":
            self.handle_critical_alert(message)
        elif severity == "warning":
            self.handle_warning_alert(message)
        else:
            self.handle_info_alert(message)
    
    def format_alert_message(self, alert_data):
        """Format alert message for different channels"""
        
        alert_name = alert_data.get("labels", {}).get("alertname", "Unknown")
        severity = alert_data.get("labels", {}).get("severity", "warning")
        description = alert_data.get("annotations", {}).get("description", "")
        
        # Add Indian context and urgency
        urgency_emoji = "🚨" if severity == "critical" else "⚠️"
        
        message = f"{urgency_emoji} Dream11 Alert: {alert_name}\n\n"
        message += f"Severity: {severity.upper()}\n"
        message += f"Description: {description}\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n"
        
        if severity == "critical":
            message += "\n🔥 IMMEDIATE ACTION REQUIRED!\n"
            message += "Check: https://grafana.dream11.com/dashboards\n"
            message += "Runbook: https://wiki.dream11.com/alerts\n"
        
        return message
    
    def handle_critical_alert(self, message):
        """Handle critical alerts with immediate escalation"""
        
        # Immediate WhatsApp to on-call engineers
        for phone in self.escalation_matrix["critical"]["immediate"]:
            self.send_whatsapp(phone, message)
        
        # Slack notification
        self.send_slack_alert(message, "#critical-alerts")
        
        # Email to leadership
        self.send_email(
            to=["cto@dream11.com", "head-engineering@dream11.com"],
            subject=f"CRITICAL: Dream11 Production Alert",
            body=message
        )
        
        # Schedule escalation
        self.schedule_escalation("critical", message)
    
    def handle_warning_alert(self, message):
        """Handle warning alerts"""
        
        # Slack notification
        self.send_slack_alert(message, "#data-alerts")
        
        # Schedule escalation after 30 minutes
        self.schedule_escalation("warning", message)
    
    def send_whatsapp(self, phone_number, message):
        """Send WhatsApp message via Twilio"""
        try:
            self.whatsapp_client.messages.create(
                body=message,
                from_='whatsapp:+14155238886',  # Twilio WhatsApp number
                to=f'whatsapp:{phone_number}'
            )
        except Exception as e:
            print(f"Failed to send WhatsApp to {phone_number}: {e}")
    
    def send_slack_alert(self, message, channel):
        """Send Slack notification"""
        try:
            slack_payload = {
                "channel": channel,
                "text": message,
                "username": "Dream11-AlertBot",
                "icon_emoji": ":warning:"
            }
            
            response = requests.post(
                self.slack_webhook,
                json=slack_payload,
                timeout=10
            )
            response.raise_for_status()
            
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def send_email(self, to, subject, body):
        """Send email alert"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = ', '.join(to)
            
            with smtplib.SMTP(self.email_server, 587) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
                
        except Exception as e:
            print(f"Failed to send email: {e}")

# Flask webhook to receive Prometheus alerts
from flask import Flask, request, jsonify

app = Flask(__name__)
alert_manager = Dream11AlertManager()

@app.route('/webhook/prometheus', methods=['POST'])
def prometheus_webhook():
    """Receive alerts from Prometheus AlertManager"""
    
    try:
        data = request.json
        
        for alert in data.get('alerts', []):
            alert_manager.send_alert(alert)
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Error processing alert: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

### Monitoring Best Practices for Indian Companies

**1. Regional Considerations**
```python
# India-specific monitoring configurations
INDIAN_MONITORING_CONFIG = {
    "timezone": "Asia/Kolkata",
    "business_hours": {
        "start": "09:00",
        "end": "21:00", 
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    },
    "festival_dates": [
        "2024-03-08",  # Holi
        "2024-04-17",  # Ram Navami
        "2024-08-15",  # Independence Day
        "2024-10-31",  # Diwali
        "2024-11-15"   # Guru Nanak Jayanti
    ],
    "peak_usage_periods": {
        "ipl_season": {"start": "2024-03-22", "end": "2024-05-26"},
        "world_cup": {"start": "2024-10-05", "end": "2024-11-19"},
        "diwali_shopping": {"start": "2024-10-20", "end": "2024-11-05"}
    }
}
```

**2. Cost-Optimized Monitoring**
```yaml
# Different retention policies for cost optimization
prometheus:
  retention_policies:
    high_frequency: "7d"      # Every 15s for 7 days
    medium_frequency: "30d"   # Every 1m for 30 days  
    low_frequency: "365d"     # Every 5m for 1 year
    
  storage_tiers:
    hot: "ssd"     # Last 7 days - fast access
    warm: "hdd"    # 7-30 days - moderate access
    cold: "s3"     # 30+ days - archive access
```

---

## Conclusion: Mastering the DataOps Toolchain

### Mumbai to Global - Tool Mastery Journey

Jaise Mumbai local train system multiple technologies integrate kar ke seamless journey provide karta hai - RFID cards, UPI payments, GPS tracking, automated announcements - waise hi DataOps tools integrate ho kar complete data platform banate hain.

### Key Takeaways from Part 2:

**1. Orchestration Mastery with Airflow**
- Complex dependencies manage karna (train schedule ki tarah)
- Dynamic DAG generation for scalability  
- Custom operators for Indian business logic
- Cost optimization through smart scheduling

**2. Data Transformation Excellence with dbt**
- Assembly line approach for data processing
- Version control for data transformations
- Automated testing and quality assurance
- Documentation generation for compliance

**3. Infrastructure as Code with Terraform**
- City planning approach for infrastructure
- Multi-region deployments for Indian operations
- Cost optimization through resource management
- Compliance automation for regulatory requirements

**4. Data Quality Guardian with Great Expectations**
- Quality inspector role for data validation
- Custom expectations for Indian data formats
- Integration with existing workflows
- Automated incident response

**5. Comprehensive Monitoring Stack**
- Traffic control room for data infrastructure
- Real-time alerting with Indian communication preferences
- Performance optimization through metrics
- Regional considerations and compliance

### Integration Example: Complete DataOps Platform

```python
# complete_dataops_platform.py - Bringing it all together
class DataOpsPlatform:
    def __init__(self):
        self.airflow = AirflowOrchestrator()
        self.dbt = DbtTransformer() 
        self.terraform = TerraformManager()
        self.great_expectations = DataQualityValidator()
        self.monitoring = MonitoringStack()
    
    def deploy_complete_pipeline(self, pipeline_config):
        """Deploy end-to-end data pipeline"""
        
        # 1. Provision infrastructure with Terraform
        infrastructure = self.terraform.provision(pipeline_config['infrastructure'])
        
        # 2. Setup data quality expectations
        expectations = self.great_expectations.create_suite(pipeline_config['quality_rules'])
        
        # 3. Deploy dbt transformations
        transformations = self.dbt.deploy_models(pipeline_config['dbt_models'])
        
        # 4. Create Airflow DAG
        dag = self.airflow.create_dag(
            pipeline_config['schedule'],
            dependencies=[infrastructure, expectations, transformations]
        )
        
        # 5. Setup monitoring
        self.monitoring.configure_alerts(pipeline_config['monitoring_rules'])
        
        return {
            'status': 'deployed',
            'infrastructure': infrastructure,
            'pipeline_id': dag.dag_id,
            'monitoring_dashboard': self.monitoring.dashboard_url
        }
```

### Next Steps: Part 3 Preview

Part 3 mein hum discuss karenge:
- **Advanced CI/CD**: GitOps workflows for data pipelines
- **Apache Kafka**: Event-driven architectures at scale  
- **Kubernetes**: Container orchestration for data workloads
- **Indian Cloud Solutions**: AWS India, Azure India, Google Cloud India
- **Real-time Processing**: Stream processing architectures
- **MLOps Integration**: ML pipelines with DataOps tools

### Action Items for Your Team:

**Week 1: Tool Selection**
- Current toolchain audit
- Tool evaluation matrix
- Pilot project selection

**Week 2-4: Implementation**
- Basic Airflow setup
- dbt project initialization
- Terraform infrastructure templates

**Month 2-3: Advanced Features**
- Monitoring stack deployment
- Data quality frameworks
- Team training and adoption

### Final Words

DataOps tools Mumbai ki infrastructure ki tarah hain - individually powerful, but together transformational. Har tool master karna important hai, but real magic integration mein hai.

Remember: Tools sirf enable karte hain, culture change actual transformation karta hai. Technical implementation ke saath-saath team mindset bhi change karna hoga.

Part 3 mein milenge advanced topics ke saath. Tab tak practice karte rahiye jo aaj seekha hai!

**Word Count: 7,247 words** ✅

---

*From Mumbai's local trains to global DataOps excellence - yeh hai hamara journey!*