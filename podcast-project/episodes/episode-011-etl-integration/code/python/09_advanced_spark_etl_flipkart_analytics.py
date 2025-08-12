#!/usr/bin/env python3
"""
Advanced Spark ETL Pipeline for Flipkart Analytics
Focus: Complex transformations, partitioning, performance optimization

Ye advanced Spark ETL example hai jo Flipkart ke Big Billion Day
ke real-time analytics ke liye use karte hain. Mumbai ki traffic
jaise complex transformations handle karte hain.

Production Ready: Yes
Testing Required: Yes
Performance: Optimized for billion records
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, when, lit, sum as spark_sum, avg, count, 
    max as spark_max, min as spark_min,
    window, to_timestamp, date_format, 
    broadcast, coalesce, lag, lead,
    regexp_replace, split, trim, lower,
    row_number, rank, dense_rank,
    collect_list, collect_set, array_contains,
    monotonically_increasing_id,
    current_timestamp, unix_timestamp
)
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, BooleanType
import pyspark.sql.functions as F

# Configure logging - Mumbai style
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ETLConfig:
    """ETL configuration for Flipkart analytics"""
    input_path: str = "/data/flipkart/raw/"
    output_path: str = "/data/flipkart/processed/"
    checkpoint_path: str = "/data/flipkart/checkpoints/"
    partition_columns: List[str] = None
    window_duration: str = "1 hour"
    watermark_delay: str = "10 minutes"
    max_files_per_trigger: int = 100
    
    def __post_init__(self):
        if self.partition_columns is None:
            self.partition_columns = ["year", "month", "day", "hour"]

class FlipkartAdvancedETL:
    """
    Advanced ETL pipeline for Flipkart's billion-record analytics
    
    Mumbai ke local train jaise efficient - sabko time pe deliver karna hai!
    """
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.spark = self._create_spark_session()
        
    def _create_spark_session(self) -> SparkSession:
        """Create optimized Spark session for Indian e-commerce scale"""
        logger.info("🚀 Creating Spark session - Flipkart scale ready!")
        
        spark = SparkSession.builder \
            .appName("FlipkartAdvancedETL") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.enabled", "true") \
            .config("spark.sql.adaptive.localShuffleReader.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.sql.parquet.compression.codec", "snappy") \
            .config("spark.sql.shuffle.partitions", "200") \
            .config("spark.default.parallelism", "100") \
            .config("spark.sql.streaming.stateStore.maintenanceInterval", "300s") \
            .getOrCreate()
            
        # Mumbai monsoon ke liye backup - checkpointing
        spark.sparkContext.setCheckpointDir(self.config.checkpoint_path)
        
        logger.info("✅ Spark session created successfully!")
        return spark
    
    def create_schemas(self) -> Dict[str, StructType]:
        """Define schemas for different data sources"""
        
        # Flipkart orders schema - Big Billion Day ready
        orders_schema = StructType([
            StructField("order_id", StringType(), False),
            StructField("user_id", StringType(), False),
            StructField("product_id", StringType(), False),
            StructField("seller_id", StringType(), False),
            StructField("category", StringType(), True),
            StructField("subcategory", StringType(), True),
            StructField("brand", StringType(), True),
            StructField("quantity", IntegerType(), False),
            StructField("unit_price", DoubleType(), False),
            StructField("total_amount", DoubleType(), False),
            StructField("discount_amount", DoubleType(), True),
            StructField("shipping_cost", DoubleType(), True),
            StructField("order_timestamp", TimestampType(), False),
            StructField("delivery_address_state", StringType(), True),
            StructField("delivery_address_city", StringType(), True),
            StructField("delivery_address_pincode", StringType(), True),
            StructField("payment_method", StringType(), True),
            StructField("is_cod", BooleanType(), True),
            StructField("delivery_status", StringType(), True)
        ])
        
        # User behavior schema - for recommendation engine
        user_behavior_schema = StructType([
            StructField("user_id", StringType(), False),
            StructField("session_id", StringType(), False),
            StructField("event_type", StringType(), False),
            StructField("product_id", StringType(), True),
            StructField("category", StringType(), True),
            StructField("timestamp", TimestampType(), False),
            StructField("device_type", StringType(), True),
            StructField("platform", StringType(), True),
            StructField("location_state", StringType(), True),
            StructField("duration_seconds", IntegerType(), True)
        ])
        
        # Inventory schema - stock management
        inventory_schema = StructType([
            StructField("product_id", StringType(), False),
            StructField("seller_id", StringType(), False),
            StructField("warehouse_id", StringType(), False),
            StructField("available_stock", IntegerType(), False),
            StructField("reserved_stock", IntegerType(), False),
            StructField("last_updated", TimestampType(), False),
            StructField("reorder_level", IntegerType(), True),
            StructField("max_stock_level", IntegerType(), True)
        ])
        
        return {
            "orders": orders_schema,
            "user_behavior": user_behavior_schema,
            "inventory": inventory_schema
        }
    
    def load_streaming_data(self, source_type: str) -> DataFrame:
        """Load streaming data from Kafka - like Mumbai's never-ending traffic"""
        logger.info(f"📊 Loading streaming data: {source_type}")
        
        schemas = self.create_schemas()
        
        if source_type == "orders":
            # Load orders from Kafka - Big Billion Day ke liye ready
            df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "localhost:9092,kafka-cluster:9092") \
                .option("subscribe", "flipkart-orders") \
                .option("startingOffsets", "earliest") \
                .option("maxOffsetsPerTrigger", 10000) \
                .load()
            
            # Parse Kafka messages
            parsed_df = df.select(
                col("key").cast("string").alias("order_id"),
                col("value").cast("string").alias("order_data"),
                col("timestamp").alias("kafka_timestamp"),
                col("partition"),
                col("offset")
            )
            
            # Convert JSON to structured data
            from pyspark.sql.functions import from_json
            orders_df = parsed_df.select(
                col("order_id"),
                from_json(col("order_data"), schemas["orders"]).alias("order"),
                col("kafka_timestamp"),
                col("partition"),
                col("offset")
            ).select(
                col("order_id"),
                col("order.*"),
                col("kafka_timestamp"),
                col("partition"),
                col("offset")
            )
            
            return orders_df
            
        elif source_type == "user_behavior":
            # User behavior stream - for real-time recommendations
            df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "localhost:9092") \
                .option("subscribe", "user-behavior") \
                .option("startingOffsets", "latest") \
                .load()
            
            from pyspark.sql.functions import from_json
            behavior_df = df.select(
                from_json(col("value").cast("string"), schemas["user_behavior"]).alias("behavior")
            ).select("behavior.*")
            
            return behavior_df
            
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    def complex_transformations(self, orders_df: DataFrame) -> Dict[str, DataFrame]:
        """
        Complex transformations - Mumbai ke traffic signal optimization jaise
        Multiple business metrics ek saath calculate karte hain
        """
        logger.info("🔄 Starting complex transformations...")
        
        # Add derived columns
        enriched_orders = orders_df.withColumn(
            "order_hour", date_format(col("order_timestamp"), "HH")
        ).withColumn(
            "order_day_of_week", date_format(col("order_timestamp"), "EEEE")
        ).withColumn(
            "is_weekend", 
            when(date_format(col("order_timestamp"), "EEEE").isin(["Saturday", "Sunday"]), True)
            .otherwise(False)
        ).withColumn(
            "is_peak_hour",
            when(col("order_hour").isin(["10", "11", "12", "20", "21", "22"]), True)
            .otherwise(False)
        ).withColumn(
            "revenue", col("total_amount") - col("discount_amount")
        ).withColumn(
            "profit_margin", 
            when(col("total_amount") > 0, 
                 (col("revenue") - col("shipping_cost")) / col("total_amount") * 100)
            .otherwise(0)
        )
        
        # 1. Hourly sales analytics - like Mumbai local train frequency analysis
        hourly_sales = enriched_orders.groupBy(
            window(col("order_timestamp"), self.config.window_duration),
            "category",
            "delivery_address_state"
        ).agg(
            count("order_id").alias("total_orders"),
            spark_sum("revenue").alias("total_revenue"),
            avg("revenue").alias("avg_order_value"),
            spark_sum("quantity").alias("total_quantity"),
            count(when(col("is_cod"), True)).alias("cod_orders"),
            count(when(col("payment_method") == "UPI", True)).alias("upi_orders"),
            count(when(col("payment_method") == "Card", True)).alias("card_orders")
        ).withColumn(
            "cod_percentage", 
            (col("cod_orders") / col("total_orders") * 100).cast("decimal(5,2)")
        ).withColumn(
            "digital_payment_percentage",
            ((col("upi_orders") + col("card_orders")) / col("total_orders") * 100).cast("decimal(5,2)")
        )
        
        # 2. User behavior analytics - customer journey mapping
        user_window = Window.partitionBy("user_id").orderBy("order_timestamp")
        
        user_analytics = enriched_orders.withColumn(
            "user_order_sequence", row_number().over(user_window)
        ).withColumn(
            "previous_order_timestamp", lag("order_timestamp").over(user_window)
        ).withColumn(
            "days_since_last_order",
            when(col("previous_order_timestamp").isNotNull(),
                 (unix_timestamp("order_timestamp") - unix_timestamp("previous_order_timestamp")) / 86400)
            .otherwise(None)
        ).groupBy("user_id").agg(
            count("order_id").alias("total_orders"),
            spark_sum("revenue").alias("lifetime_value"),
            avg("revenue").alias("avg_order_value"),
            spark_min("order_timestamp").alias("first_order_date"),
            spark_max("order_timestamp").alias("last_order_date"),
            avg("days_since_last_order").alias("avg_days_between_orders"),
            collect_set("category").alias("preferred_categories"),
            count(when(col("is_cod"), True)).alias("cod_preference_count")
        ).withColumn(
            "customer_segment",
            when(col("total_orders") >= 50, "VIP")
            .when(col("total_orders") >= 20, "Loyal")
            .when(col("total_orders") >= 5, "Regular")
            .otherwise("New")
        ).withColumn(
            "preferred_payment_mode",
            when(col("cod_preference_count") / col("total_orders") > 0.7, "COD")
            .otherwise("Digital")
        )
        
        # 3. Geographic sales performance - state-wise analysis like Indian elections!
        geographic_performance = enriched_orders.groupBy(
            "delivery_address_state",
            "delivery_address_city"
        ).agg(
            count("order_id").alias("total_orders"),
            spark_sum("revenue").alias("total_revenue"),
            avg("revenue").alias("avg_order_value"),
            count(when(col("is_cod"), True)).alias("cod_orders"),
            count(when(col("delivery_status") == "Delivered", True)).alias("successful_deliveries")
        ).withColumn(
            "delivery_success_rate",
            (col("successful_deliveries") / col("total_orders") * 100).cast("decimal(5,2)")
        ).withColumn(
            "cod_preference_rate",
            (col("cod_orders") / col("total_orders") * 100).cast("decimal(5,2)")
        ).orderBy(col("total_revenue").desc())
        
        # 4. Category performance with seasonal trends
        category_performance = enriched_orders.groupBy(
            "category",
            "subcategory",
            "brand",
            date_format(col("order_timestamp"), "yyyy-MM").alias("month")
        ).agg(
            count("order_id").alias("total_orders"),
            spark_sum("revenue").alias("total_revenue"),
            avg("profit_margin").alias("avg_profit_margin"),
            spark_sum("quantity").alias("total_quantity_sold")
        ).withColumn(
            "revenue_per_order", col("total_revenue") / col("total_orders")
        )
        
        # 5. Real-time inventory alerts - stock level monitoring
        current_timestamp_col = current_timestamp()
        inventory_alerts = enriched_orders.groupBy("product_id", "seller_id").agg(
            spark_sum("quantity").alias("total_sold_today"),
            count("order_id").alias("order_frequency")
        ).withColumn(
            "alert_timestamp", current_timestamp_col
        ).withColumn(
            "restock_priority",
            when(col("total_sold_today") > 100, "HIGH")
            .when(col("total_sold_today") > 50, "MEDIUM")
            .otherwise("LOW")
        )
        
        logger.info("✅ Complex transformations completed!")
        
        return {
            "hourly_sales": hourly_sales,
            "user_analytics": user_analytics,
            "geographic_performance": geographic_performance,
            "category_performance": category_performance,
            "inventory_alerts": inventory_alerts
        }
    
    def apply_data_quality_rules(self, df: DataFrame) -> DataFrame:
        """Apply data quality rules - Mumbai ki quality control jaise strict!"""
        logger.info("🔍 Applying data quality rules...")
        
        cleaned_df = df.filter(
            # Remove null or empty order IDs
            col("order_id").isNotNull() & (col("order_id") != "")
        ).filter(
            # Remove orders with invalid amounts
            (col("total_amount") > 0) & (col("total_amount") < 1000000)
        ).filter(
            # Remove orders with invalid quantities
            (col("quantity") > 0) & (col("quantity") <= 100)
        ).filter(
            # Remove orders with future timestamps (data quality issue)
            col("order_timestamp") <= current_timestamp()
        ).withColumn(
            # Clean city names - standardize Mumbai variations
            "delivery_address_city",
            when(col("delivery_address_city").rlike("(?i)mumbai|bombay"), "Mumbai")
            .when(col("delivery_address_city").rlike("(?i)delhi|new delhi"), "Delhi")
            .when(col("delivery_address_city").rlike("(?i)bengaluru|bangalore"), "Bangalore")
            .otherwise(col("delivery_address_city"))
        ).withColumn(
            # Standardize payment methods
            "payment_method",
            when(col("payment_method").rlike("(?i)upi|bhim|paytm|gpay|phonepe"), "UPI")
            .when(col("payment_method").rlike("(?i)card|debit|credit"), "Card")
            .when(col("payment_method").rlike("(?i)cod|cash"), "COD")
            .when(col("payment_method").rlike("(?i)wallet|paytm wallet"), "Wallet")
            .otherwise("Other")
        ).dropDuplicates(["order_id"])  # Remove duplicate orders
        
        logger.info("✅ Data quality rules applied!")
        return cleaned_df
    
    def optimize_for_performance(self, df: DataFrame, operation_type: str = "batch") -> DataFrame:
        """Optimize DataFrame for performance - Mumbai local train efficiency!"""
        logger.info(f"⚡ Optimizing for performance: {operation_type}")
        
        if operation_type == "batch":
            # Batch optimization
            optimized_df = df.coalesce(50)  # Reduce small files
            
        elif operation_type == "streaming":
            # Streaming optimization
            optimized_df = df.repartition(col("delivery_address_state"))  # Partition by state
            
        elif operation_type == "join":
            # Join optimization - broadcast smaller tables
            optimized_df = df.hint("broadcast") if df.count() < 1000000 else df
            
        else:
            optimized_df = df
        
        # Cache if DataFrame will be used multiple times
        optimized_df.persist()
        
        logger.info("✅ Performance optimization completed!")
        return optimized_df
    
    def write_to_delta_lake(self, df: DataFrame, table_name: str, mode: str = "append") -> None:
        """Write to Delta Lake with partitioning - organized like Mumbai's dabba system!"""
        logger.info(f"💾 Writing to Delta Lake table: {table_name}")
        
        output_path = f"{self.config.output_path}/delta/{table_name}"
        
        # Add partition columns
        df_with_partitions = df.withColumn(
            "year", date_format(col("order_timestamp"), "yyyy")
        ).withColumn(
            "month", date_format(col("order_timestamp"), "MM")
        ).withColumn(
            "day", date_format(col("order_timestamp"), "dd")
        ).withColumn(
            "hour", date_format(col("order_timestamp"), "HH")
        )
        
        # Write with Delta Lake features
        df_with_partitions.write \
            .format("delta") \
            .mode(mode) \
            .partitionBy("year", "month", "day") \
            .option("mergeSchema", "true") \
            .option("optimizeWrite", "true") \
            .option("autoCompact", "true") \
            .save(output_path)
        
        logger.info(f"✅ Data written to Delta Lake: {output_path}")
    
    def create_streaming_query(self, df: DataFrame, output_table: str) -> None:
        """Create streaming query with checkpointing - continuous like Mumbai monsoons!"""
        logger.info(f"🌊 Creating streaming query for: {output_table}")
        
        query = df.writeStream \
            .outputMode("append") \
            .format("delta") \
            .option("checkpointLocation", f"{self.config.checkpoint_path}/{output_table}") \
            .option("mergeSchema", "true") \
            .partitionBy("year", "month", "day") \
            .trigger(processingTime=self.config.window_duration) \
            .start(f"{self.config.output_path}/streaming/{output_table}")
        
        logger.info(f"✅ Streaming query started for: {output_table}")
        return query
    
    def run_batch_etl(self) -> Dict[str, str]:
        """Run complete batch ETL pipeline"""
        logger.info("🚀 Starting Flipkart Batch ETL Pipeline...")
        
        try:
            # Load batch data
            orders_df = self.spark.read \
                .option("mergeSchema", "true") \
                .parquet(f"{self.config.input_path}/orders/")
            
            # Apply data quality rules
            clean_orders = self.apply_data_quality_rules(orders_df)
            
            # Apply complex transformations
            transformed_data = self.complex_transformations(clean_orders)
            
            # Write to Delta Lake
            results = {}
            for table_name, df in transformed_data.items():
                optimized_df = self.optimize_for_performance(df, "batch")
                self.write_to_delta_lake(optimized_df, table_name, "overwrite")
                results[table_name] = f"✅ Processed {optimized_df.count()} records"
            
            logger.info("🎉 Batch ETL completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch ETL failed: {str(e)}")
            raise
    
    def run_streaming_etl(self) -> List[object]:
        """Run streaming ETL pipeline - like Mumbai's continuous data flow"""
        logger.info("🌊 Starting Flipkart Streaming ETL Pipeline...")
        
        try:
            # Load streaming data
            orders_stream = self.load_streaming_data("orders")
            
            # Apply data quality rules
            clean_orders = self.apply_data_quality_rules(orders_stream)
            
            # Apply transformations
            transformed_data = self.complex_transformations(clean_orders)
            
            # Create streaming queries
            queries = []
            for table_name, df in transformed_data.items():
                if table_name in ["hourly_sales", "inventory_alerts"]:  # Real-time tables
                    query = self.create_streaming_query(df, f"realtime_{table_name}")
                    queries.append(query)
            
            logger.info("🎉 Streaming ETL queries started!")
            return queries
            
        except Exception as e:
            logger.error(f"❌ Streaming ETL failed: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up resources...")
        self.spark.stop()
        logger.info("✅ Cleanup completed!")

# Performance monitoring and metrics
class ETLMetricsCollector:
    """Collect and monitor ETL performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def collect_spark_metrics(self, spark: SparkSession) -> Dict:
        """Collect Spark performance metrics"""
        status_tracker = spark.sparkContext.statusTracker()
        
        metrics = {
            "active_jobs": len(status_tracker.getActiveJobIds()),
            "active_stages": len(status_tracker.getActiveStageIds()),
            "executor_infos": len(status_tracker.getExecutorInfos()),
            "application_id": spark.sparkContext.applicationId,
            "application_name": spark.sparkContext.appName
        }
        
        return metrics
    
    def log_processing_stats(self, operation: str, start_time: datetime, record_count: int):
        """Log processing statistics"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        throughput = record_count / duration if duration > 0 else 0
        
        logger.info(f"""
        📊 ETL Processing Stats:
        Operation: {operation}
        Duration: {duration:.2f} seconds
        Records Processed: {record_count:,}
        Throughput: {throughput:.2f} records/second
        """)

def main():
    """Main function to run Flipkart Advanced ETL"""
    
    # Configure ETL
    config = ETLConfig(
        input_path="/data/flipkart/raw",
        output_path="/data/flipkart/processed",
        checkpoint_path="/data/flipkart/checkpoints"
    )
    
    # Initialize ETL pipeline
    etl = FlipkartAdvancedETL(config)
    metrics = ETLMetricsCollector()
    
    try:
        # Run batch ETL
        logger.info("Starting batch processing...")
        start_time = datetime.now()
        
        batch_results = etl.run_batch_etl()
        
        # Log results
        for table, result in batch_results.items():
            logger.info(f"{table}: {result}")
        
        # Collect metrics
        spark_metrics = metrics.collect_spark_metrics(etl.spark)
        logger.info(f"Spark Metrics: {spark_metrics}")
        
        # Run streaming ETL (comment out for batch-only execution)
        # streaming_queries = etl.run_streaming_etl()
        # logger.info(f"Started {len(streaming_queries)} streaming queries")
        
        logger.info("🎉 Flipkart Advanced ETL completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ ETL pipeline failed: {str(e)}")
        raise
    finally:
        etl.cleanup()

if __name__ == "__main__":
    main()

"""
Mumbai Learning Notes:
1. Advanced Spark optimizations for Indian e-commerce scale
2. Delta Lake integration with partitioning strategies
3. Complex transformations for business analytics
4. Streaming ETL with checkpointing and fault tolerance
5. Data quality rules specific to Indian market
6. Performance monitoring and metrics collection
7. Real-world Flipkart use cases and scenarios

Production Deployment:
- Use cluster mode for large datasets
- Configure appropriate memory and CPU settings
- Set up monitoring with Spark UI and custom metrics
- Implement data lineage tracking
- Add alerting for pipeline failures
"""