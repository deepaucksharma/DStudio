#!/usr/bin/env python3
"""
Apache Spark ETL Pipeline - Flipkart Order Processing at Scale
==============================================================

जैसे Flipkart Big Billion Day में करोड़ों orders process करता है,
वैसे ही हम Spark का use करके massive scale पे ETL करेंगे।

Real-world use case: Flipkart's order processing during sales events
Daily volume: 10M+ orders, Peak: 50K orders/minute

Author: DStudio Engineering Team
Episode: 11 - ETL & Data Integration Patterns
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class FlipkartSparkETL:
    """
    Flipkart Scale ETL with Apache Spark
    ===================================
    
    Big Billion Day जैसे sales events के लिए massive scale ETL pipeline।
    Real-time order processing, inventory updates, analytics preparation।
    """
    
    def __init__(self, spark_config: Dict = None):
        self.spark = self._create_spark_session(spark_config)
        self.logger = self._setup_logging()
        
        # Flipkart business constants
        self.BUSINESS_RULES = {
            'max_order_value': 200000,  # 2 लाख रुपए - fraud detection के लिए
            'peak_hour_start': 10,      # सुबह 10 बजे से peak traffic
            'peak_hour_end': 22,        # रात 10 बजे तक peak traffic  
            'delivery_zones': ['North', 'South', 'East', 'West', 'Northeast'],
            'payment_methods': ['UPI', 'Card', 'COD', 'EMI', 'Wallet'],
            'priority_categories': ['Electronics', 'Fashion', 'Mobiles']
        }
        
    def _create_spark_session(self, config: Dict = None) -> SparkSession:
        """Production-grade Spark session with optimized configuration"""
        
        builder = SparkSession.builder \
            .appName("FlipkartETL-BigBillionDay") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.shuffle.partitions", "200") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        
        # Custom configuration override
        if config:
            for key, value in config.items():
                builder = builder.config(key, value)
                
        spark = builder.getOrCreate()
        spark.sparkContext.setLogLevel("WARN")  # Reduce log noise
        
        return spark
    
    def _setup_logging(self):
        """Spark-compatible logging setup"""
        logger = logging.getLogger("FlipkartSparkETL")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def extract_orders_data(self, data_path: str) -> "DataFrame":
        """
        Extract करना - Multiple sources से order data
        ============================================
        
        Flipkart के हजारों servers से आने वाला order data।
        JSON, Parquet, CSV - सभी formats support करना।
        """
        self.logger.info(f"🚚 Extract phase: Reading order data from {data_path}")
        
        # Order data schema definition - Strong typing के लिए
        order_schema = StructType([
            StructField("order_id", StringType(), False),
            StructField("customer_id", StringType(), False), 
            StructField("seller_id", StringType(), False),
            StructField("product_id", StringType(), False),
            StructField("product_name", StringType(), True),
            StructField("category", StringType(), True),
            StructField("quantity", IntegerType(), True),
            StructField("unit_price", DoubleType(), True),
            StructField("total_amount", DoubleType(), True),
            StructField("payment_method", StringType(), True),
            StructField("delivery_zone", StringType(), True),
            StructField("order_timestamp", TimestampType(), True),
            StructField("customer_tier", StringType(), True),  # Plus member या नहीं
            StructField("discount_applied", DoubleType(), True),
            StructField("delivery_pincode", StringType(), True)
        ])
        
        try:
            # Auto-detect file format और efficiently read करना
            if data_path.endswith('.parquet'):
                df = self.spark.read.schema(order_schema).parquet(data_path)
            elif data_path.endswith('.json') or data_path.endswith('.jsonl'):
                df = self.spark.read.schema(order_schema).json(data_path)
            else:
                # CSV के लिए header detection
                df = self.spark.read.schema(order_schema) \
                    .option("header", "true") \
                    .csv(data_path)
            
            record_count = df.count()
            self.logger.info(f"✅ Successfully extracted {record_count} orders")
            self.logger.info(f"📊 Data partitions: {df.rdd.getNumPartitions()}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Extract failed: {str(e)}")
            raise

    def transform_orders(self, orders_df: "DataFrame") -> "DataFrame":
        """
        Transform Phase - Business logic और data enrichment
        ==================================================
        
        Flipkart के complex business rules apply करना:
        - Fraud detection
        - Customer segmentation  
        - Inventory impact calculation
        - Delivery optimization
        """
        self.logger.info("🔄 Transform phase: Applying Flipkart business logic")
        
        try:
            # 1. Data quality और basic validations
            cleaned_df = orders_df \
                .filter(col("order_id").isNotNull()) \
                .filter(col("total_amount") > 0) \
                .filter(col("total_amount") <= self.BUSINESS_RULES['max_order_value']) \
                .filter(col("quantity") > 0) \
                .dropDuplicates(["order_id"])
            
            self.logger.info("✅ Data quality checks completed")
            
            # 2. Customer tier enrichment - Plus member analysis
            enriched_df = cleaned_df \
                .withColumn("is_plus_member", 
                           when(col("customer_tier") == "Plus", True).otherwise(False)) \
                .withColumn("plus_discount_eligible",
                           when(col("is_plus_member"), col("total_amount") * 0.05).otherwise(0))
            
            # 3. Order timing analysis - Peak vs Non-peak
            enriched_df = enriched_df \
                .withColumn("order_hour", hour(col("order_timestamp"))) \
                .withColumn("is_peak_hour",
                           when(
                               (col("order_hour") >= self.BUSINESS_RULES['peak_hour_start']) & 
                               (col("order_hour") <= self.BUSINESS_RULES['peak_hour_end']),
                               True
                           ).otherwise(False)) \
                .withColumn("day_of_week", dayofweek(col("order_timestamp")))
            
            # 4. Payment method risk assessment
            payment_risk = {
                'COD': 'HIGH',      # Cash on Delivery - return risk ज्यादा
                'UPI': 'LOW',       # UPI - secure और instant
                'Card': 'MEDIUM',   # Cards - chargeback risk
                'Wallet': 'LOW',    # Wallets - pre-paid
                'EMI': 'MEDIUM'     # EMI - credit risk
            }
            
            # Create payment risk mapping
            payment_risk_expr = create_map([lit(x) for x in [item for sublist in payment_risk.items() for item in sublist]])
            
            enriched_df = enriched_df \
                .withColumn("payment_risk", payment_risk_expr[col("payment_method")])
            
            # 5. Geographic analysis - Delivery complexity
            zone_priority = {
                'North': 1,     # Delhi NCR - highest priority
                'West': 2,      # Mumbai - second priority  
                'South': 3,     # Bangalore - tech hub
                'East': 4,      # Kolkata - traditional market
                'Northeast': 5   # Special handling required
            }
            
            zone_priority_expr = create_map([lit(x) for x in [item for sublist in zone_priority.items() for item in sublist]])
            
            enriched_df = enriched_df \
                .withColumn("zone_priority", zone_priority_expr[col("delivery_zone")]) \
                .withColumn("delivery_complexity",
                           when(col("delivery_zone") == "Northeast", "HIGH")
                           .when(col("delivery_zone").isin(["North", "West"]), "LOW")
                           .otherwise("MEDIUM"))
            
            # 6. Customer behavior analysis - Repeat customer detection
            window_spec = Window.partitionBy("customer_id").orderBy("order_timestamp")
            
            enriched_df = enriched_df \
                .withColumn("customer_order_sequence", 
                           row_number().over(window_spec)) \
                .withColumn("is_repeat_customer",
                           when(col("customer_order_sequence") > 1, True).otherwise(False))
            
            # 7. Category-based business metrics
            enriched_df = enriched_df \
                .withColumn("is_priority_category",
                           col("category").isin(self.BUSINESS_RULES['priority_categories'])) \
                .withColumn("category_commission_rate",
                           when(col("category") == "Electronics", 0.05)
                           .when(col("category") == "Fashion", 0.12)
                           .when(col("category") == "Mobiles", 0.03)
                           .otherwise(0.08))
            
            # 8. Fraud detection scoring - Multiple factors
            enriched_df = enriched_df \
                .withColumn("fraud_score",
                           # High order value = higher risk
                           when(col("total_amount") > 50000, 3).otherwise(0) +
                           # COD payment = higher risk 
                           when(col("payment_method") == "COD", 2).otherwise(0) +
                           # New customer = slight risk
                           when(~col("is_repeat_customer"), 1).otherwise(0) +
                           # Northeast delivery = logistics complexity
                           when(col("delivery_zone") == "Northeast", 1).otherwise(0)) \
                .withColumn("fraud_risk_level",
                           when(col("fraud_score") >= 5, "HIGH")
                           .when(col("fraud_score") >= 3, "MEDIUM")
                           .otherwise("LOW"))
            
            # 9. Revenue and profit calculations
            enriched_df = enriched_df \
                .withColumn("commission_amount", 
                           col("total_amount") * col("category_commission_rate")) \
                .withColumn("net_revenue",
                           col("total_amount") - col("discount_applied") - col("plus_discount_eligible")) \
                .withColumn("estimated_profit",
                           col("commission_amount") - (col("total_amount") * 0.02)) # 2% operational cost
            
            # 10. Delivery prediction - Based on historical data
            enriched_df = enriched_df \
                .withColumn("expected_delivery_days",
                           when(col("delivery_complexity") == "LOW", 2)
                           .when(col("delivery_complexity") == "MEDIUM", 4) 
                           .otherwise(7)) \
                .withColumn("estimated_delivery_date",
                           date_add(col("order_timestamp").cast("date"), 
                                   col("expected_delivery_days")))
            
            # 11. Performance metrics calculation
            total_orders = enriched_df.count()
            peak_hour_orders = enriched_df.filter(col("is_peak_hour")).count()
            plus_member_orders = enriched_df.filter(col("is_plus_member")).count()
            high_risk_orders = enriched_df.filter(col("fraud_risk_level") == "HIGH").count()
            
            self.logger.info(f"📊 Transform completed:")
            self.logger.info(f"   - Total orders processed: {total_orders}")
            self.logger.info(f"   - Peak hour orders: {peak_hour_orders} ({peak_hour_orders/total_orders*100:.1f}%)")
            self.logger.info(f"   - Plus member orders: {plus_member_orders} ({plus_member_orders/total_orders*100:.1f}%)")
            self.logger.info(f"   - High risk orders: {high_risk_orders} ({high_risk_orders/total_orders*100:.1f}%)")
            
            return enriched_df
            
        except Exception as e:
            self.logger.error(f"❌ Transform failed: {str(e)}")
            raise

    def create_analytics_views(self, orders_df: "DataFrame") -> Dict[str, "DataFrame"]:
        """
        Analytics Views - Multiple business perspectives
        ==============================================
        
        Flipkart के different teams के लिए अलग-अलग views:
        - Finance team के लिए revenue analytics
        - Operations team के लिए logistics analytics  
        - Product team के लिए catalog analytics
        """
        self.logger.info("📈 Creating analytics views for different business teams")
        
        analytics_views = {}
        
        # 1. Revenue Analytics - Finance team के लिए
        revenue_analytics = orders_df \
            .groupBy("category", "payment_method", "customer_tier") \
            .agg(
                count("order_id").alias("total_orders"),
                sum("total_amount").alias("gross_revenue"),
                sum("net_revenue").alias("net_revenue"), 
                sum("commission_amount").alias("total_commission"),
                sum("estimated_profit").alias("estimated_profit"),
                avg("total_amount").alias("avg_order_value"),
                sum("discount_applied").alias("total_discounts")
            ) \
            .withColumn("profit_margin", col("estimated_profit") / col("gross_revenue") * 100) \
            .orderBy(desc("gross_revenue"))
        
        analytics_views["revenue_analytics"] = revenue_analytics
        
        # 2. Geographic Performance - Logistics team के लिए  
        geo_analytics = orders_df \
            .groupBy("delivery_zone", "delivery_complexity") \
            .agg(
                count("order_id").alias("total_orders"),
                sum("total_amount").alias("zone_revenue"),
                avg("expected_delivery_days").alias("avg_delivery_days"),
                countDistinct("customer_id").alias("unique_customers"),
                sum(when(col("fraud_risk_level") == "HIGH", 1).otherwise(0)).alias("high_risk_orders")
            ) \
            .withColumn("revenue_per_customer", col("zone_revenue") / col("unique_customers")) \
            .withColumn("risk_percentage", col("high_risk_orders") / col("total_orders") * 100) \
            .orderBy("zone_priority")
        
        analytics_views["geo_analytics"] = geo_analytics
        
        # 3. Customer Behavior - CRM team के लिए
        customer_analytics = orders_df \
            .groupBy("customer_id", "customer_tier", "is_plus_member") \
            .agg(
                count("order_id").alias("total_orders"),
                sum("total_amount").alias("customer_lifetime_value"),
                avg("total_amount").alias("avg_order_value"),
                max("order_timestamp").alias("last_order_date"),
                countDistinct("category").alias("categories_purchased"),
                sum("discount_applied").alias("total_discounts_received")
            ) \
            .withColumn("days_since_last_order", 
                       datediff(current_date(), col("last_order_date").cast("date"))) \
            .withColumn("customer_segment",
                       when(col("customer_lifetime_value") > 50000, "VIP")
                       .when(col("customer_lifetime_value") > 20000, "Premium")
                       .when(col("customer_lifetime_value") > 5000, "Regular")
                       .otherwise("New")) \
            .orderBy(desc("customer_lifetime_value"))
        
        analytics_views["customer_analytics"] = customer_analytics
        
        # 4. Product Performance - Catalog team के लिए
        product_analytics = orders_df \
            .groupBy("category", "product_name") \
            .agg(
                count("order_id").alias("total_orders"),
                sum("quantity").alias("total_quantity_sold"),
                sum("total_amount").alias("product_revenue"),
                avg("unit_price").alias("avg_selling_price"),
                countDistinct("customer_id").alias("unique_buyers")
            ) \
            .withColumn("revenue_per_order", col("product_revenue") / col("total_orders")) \
            .withColumn("cross_sell_potential", col("unique_buyers") / col("total_orders")) \
            .orderBy(desc("product_revenue"))
        
        analytics_views["product_analytics"] = product_analytics
        
        # 5. Hourly Performance - Operations team के लिए
        hourly_analytics = orders_df \
            .groupBy("order_hour", "is_peak_hour") \
            .agg(
                count("order_id").alias("orders_count"),
                sum("total_amount").alias("hourly_revenue"),
                avg("total_amount").alias("avg_order_value"),
                sum(when(col("payment_method") == "COD", 1).otherwise(0)).alias("cod_orders"),
                sum(when(col("fraud_risk_level") == "HIGH", 1).otherwise(0)).alias("risky_orders")
            ) \
            .withColumn("cod_percentage", col("cod_orders") / col("orders_count") * 100) \
            .withColumn("risk_percentage", col("risky_orders") / col("orders_count") * 100) \
            .orderBy("order_hour")
        
        analytics_views["hourly_analytics"] = hourly_analytics
        
        self.logger.info(f"✅ Created {len(analytics_views)} analytics views")
        return analytics_views

    def load_to_warehouse(self, orders_df: "DataFrame", analytics_views: Dict[str, "DataFrame"], output_path: str):
        """
        Load Phase - Data warehouse में optimized storage
        ===============================================
        
        Partitioned storage with proper format for analytics queries।
        """
        self.logger.info(f"📦 Loading data to warehouse: {output_path}")
        
        try:
            # 1. Main orders table - Partitioned by date and zone
            orders_df \
                .withColumn("order_date", col("order_timestamp").cast("date")) \
                .coalesce(10) \
                .write \
                .mode("overwrite") \
                .partitionBy("order_date", "delivery_zone") \
                .parquet(f"{output_path}/orders")
            
            self.logger.info("✅ Main orders table loaded")
            
            # 2. Analytics views को separate tables के रूप में store करना
            for view_name, df in analytics_views.items():
                df.coalesce(1) \
                  .write \
                  .mode("overwrite") \
                  .parquet(f"{output_path}/analytics/{view_name}")
                
                self.logger.info(f"✅ {view_name} analytics view loaded")
            
            # 3. Summary statistics table
            summary_stats = {
                "processing_timestamp": datetime.now().isoformat(),
                "total_orders": orders_df.count(),
                "total_revenue": orders_df.agg(sum("total_amount")).collect()[0][0],
                "unique_customers": orders_df.select("customer_id").distinct().count(),
                "avg_order_value": orders_df.agg(avg("total_amount")).collect()[0][0],
                "data_partitions": orders_df.rdd.getNumPartitions()
            }
            
            # Convert to DataFrame और save करना
            summary_df = self.spark.createDataFrame([summary_stats])
            summary_df \
                .write \
                .mode("overwrite") \
                .json(f"{output_path}/summary_statistics")
            
            self.logger.info("✅ Summary statistics saved")
            self.logger.info("📊 Data warehouse loading completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Load phase failed: {str(e)}")
            raise

    def run_flipkart_etl(self, input_path: str, output_path: str) -> Dict:
        """
        Complete Flipkart ETL Pipeline
        ==============================
        
        Big Billion Day scale processing pipeline।
        """
        self.logger.info("🚀 Starting Flipkart Big Billion Day ETL Pipeline...")
        
        start_time = datetime.now()
        pipeline_stats = {"start_time": start_time}
        
        try:
            # Step 1: Extract
            self.logger.info("📍 Step 1/4: EXTRACT phase")
            raw_orders = self.extract_orders_data(input_path)
            pipeline_stats["extracted_records"] = raw_orders.count()
            
            # Step 2: Transform
            self.logger.info("📍 Step 2/4: TRANSFORM phase")
            processed_orders = self.transform_orders(raw_orders)
            pipeline_stats["transformed_records"] = processed_orders.count()
            
            # Step 3: Analytics
            self.logger.info("📍 Step 3/4: ANALYTICS phase")
            analytics_views = self.create_analytics_views(processed_orders)
            pipeline_stats["analytics_views"] = len(analytics_views)
            
            # Step 4: Load
            self.logger.info("📍 Step 4/4: LOAD phase")
            self.load_to_warehouse(processed_orders, analytics_views, output_path)
            
            # Success metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() / 60  # minutes
            
            pipeline_stats.update({
                "end_time": end_time,
                "duration_minutes": duration,
                "status": "SUCCESS",
                "records_per_minute": pipeline_stats["transformed_records"] / duration if duration > 0 else 0
            })
            
            self.logger.info(f"🎉 Pipeline completed successfully!")
            self.logger.info(f"⏱️ Duration: {duration:.2f} minutes")
            self.logger.info(f"📈 Processing speed: {pipeline_stats['records_per_minute']:.0f} records/minute")
            
            return pipeline_stats
            
        except Exception as e:
            pipeline_stats.update({
                "end_time": datetime.now(),
                "status": "FAILED",
                "error": str(e)
            })
            self.logger.error(f"💥 Pipeline failed: {str(e)}")
            raise
        
        finally:
            # Cleanup resources
            self.spark.stop()

def main():
    """
    Production Flipkart ETL Pipeline
    ===============================
    
    Big Billion Day के लिए real-world scale processing।
    """
    
    print("🛒 Flipkart Big Billion Day ETL Pipeline")
    print("=" * 50)
    
    # Production Spark configuration
    spark_config = {
        "spark.executor.instances": "20",           # 20 executors
        "spark.executor.cores": "4",                # 4 cores per executor  
        "spark.executor.memory": "8g",              # 8GB memory per executor
        "spark.driver.memory": "4g",                # Driver memory
        "spark.sql.shuffle.partitions": "400",     # More partitions for large data
        "spark.dynamicAllocation.enabled": "true", # Auto-scaling
        "spark.dynamicAllocation.minExecutors": "5",
        "spark.dynamicAllocation.maxExecutors": "50"
    }
    
    # Initialize ETL pipeline
    etl_pipeline = FlipkartSparkETL(spark_config)
    
    # Production paths
    input_path = "s3a://flipkart-raw-data/orders/2024/big-billion-day/"
    output_path = "s3a://flipkart-analytics/processed-orders/2024/"
    
    try:
        # Run complete pipeline
        results = etl_pipeline.run_flipkart_etl(input_path, output_path)
        
        print("\n📊 Pipeline Results:")
        print("=" * 30)
        print(json.dumps(results, indent=2, default=str))
        
        if results["status"] == "SUCCESS":
            print(f"\n✅ Success! Processed {results['transformed_records']:,} orders")
            print(f"⚡ Speed: {results['records_per_minute']:,.0f} records/minute")
            
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


# Production Deployment Notes:
"""
🚀 Production Deployment Guide:

1. **Cluster Configuration**:
   - YARN cluster with 100+ nodes
   - Each node: 64GB RAM, 16 cores, 1TB SSD
   - Spark 3.4+ with Delta Lake support

2. **Data Sources**:
   - Real-time: Kafka streams (order events)
   - Batch: S3/HDFS (historical data)
   - Reference data: PostgreSQL (product catalog)

3. **Monitoring Setup**:
   - Spark History Server
   - Ganglia/Prometheus metrics  
   - Custom Grafana dashboards
   - PagerDuty alerts

4. **Performance Optimization**:
   - Use columnar storage (Parquet/Delta)
   - Proper partitioning strategy
   - Z-order optimization for queries
   - Broadcast joins for small tables

5. **Cost Control**:
   - Spot instances for processing
   - Auto-scaling based on data volume
   - Data lifecycle management
   - Query result caching

6. **Security & Compliance**:
   - Kerberos authentication
   - Data encryption at rest/transit
   - PII data masking
   - Audit logging

Big Billion Day में 50 करोड़ orders, 10TB data - यह scale है Flipkart का! 🛒💥
"""