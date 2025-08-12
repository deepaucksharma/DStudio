#!/usr/bin/env python3
"""
Real-time Stream Processing for Zomato Order Analytics
Focus: Kafka Streams, Structured Streaming, real-time dashboards

Ye streaming ETL Zomato ke live orders process karta hai.
Mumbai ke food delivery jaise fast aur continuous!

Production Ready: Yes
Testing Required: Yes
Performance: Optimized for thousands of orders per second
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
import json

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, when, lit, sum as spark_sum, avg, count, 
    max as spark_max, min as spark_min,
    window, to_timestamp, date_format, 
    current_timestamp, unix_timestamp,
    from_json, to_json, struct,
    explode, split, trim, lower,
    regexp_replace, regexp_extract,
    monotonically_increasing_id,
    sha2, md5, uuid, 
    collect_list, collect_set,
    coalesce, first, last,
    lag, lead, row_number
)
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, BooleanType, ArrayType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class StreamingConfig:
    """Configuration for streaming ETL"""
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topics: Dict[str, str] = None
    checkpoint_path: str = "/data/zomato/checkpoints/"
    output_path: str = "/data/zomato/streaming/"
    trigger_interval: str = "10 seconds"
    max_offsets_per_trigger: int = 1000
    watermark_delay: str = "1 minute"
    late_data_threshold: str = "5 minutes"
    
    def __post_init__(self):
        if self.kafka_topics is None:
            self.kafka_topics = {
                'orders': 'zomato-orders',
                'deliveries': 'zomato-deliveries', 
                'restaurants': 'zomato-restaurants',
                'ratings': 'zomato-ratings',
                'payments': 'zomato-payments'
            }

class ZomatoStreamingETL:
    """
    Real-time streaming ETL for Zomato order analytics
    
    Mumbai ke tiffin delivery jaise precise timing!
    """
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.spark = self._create_spark_session()
        self.running_queries = []
        
    def _create_spark_session(self) -> SparkSession:
        """Create Spark session for streaming"""
        logger.info("🚀 Creating Spark streaming session...")
        
        spark = SparkSession.builder \
            .appName("ZomatoStreamingETL") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.streaming.stateStore.maintenanceInterval", "60s") \
            .config("spark.sql.streaming.stopGracefullyOnShutdown", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.sql.streaming.checkpointLocation", self.config.checkpoint_path) \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN")
        logger.info("✅ Spark streaming session created!")
        return spark
    
    def create_order_schema(self) -> StructType:
        """Create schema for Zomato order events"""
        return StructType([
            # Order identifiers
            StructField("order_id", StringType(), False),
            StructField("user_id", StringType(), False),
            StructField("restaurant_id", StringType(), False),
            StructField("delivery_partner_id", StringType(), True),
            
            # Order details
            StructField("order_status", StringType(), False),  # PLACED, CONFIRMED, PREPARING, OUT_FOR_DELIVERY, DELIVERED, CANCELLED
            StructField("order_timestamp", TimestampType(), False),
            StructField("estimated_delivery_time", TimestampType(), True),
            StructField("actual_delivery_time", TimestampType(), True),
            
            # Items and pricing
            StructField("items", ArrayType(StructType([
                StructField("item_id", StringType(), False),
                StructField("item_name", StringType(), False),
                StructField("quantity", IntegerType(), False),
                StructField("unit_price", DoubleType(), False),
                StructField("total_price", DoubleType(), False),
                StructField("category", StringType(), True),
                StructField("is_veg", BooleanType(), True)
            ])), False),
            
            StructField("subtotal", DoubleType(), False),
            StructField("delivery_fee", DoubleType(), True),
            StructField("taxes", DoubleType(), True),
            StructField("discount_amount", DoubleType(), True),
            StructField("total_amount", DoubleType(), False),
            
            # Restaurant information
            StructField("restaurant_name", StringType(), False),
            StructField("restaurant_category", StringType(), True),
            StructField("restaurant_rating", DoubleType(), True),
            StructField("restaurant_location", StructType([
                StructField("area", StringType(), True),
                StructField("city", StringType(), False),
                StructField("state", StringType(), False),
                StructField("pincode", StringType(), True),
                StructField("latitude", DoubleType(), True),
                StructField("longitude", DoubleType(), True)
            ]), True),
            
            # Delivery information
            StructField("delivery_location", StructType([
                StructField("area", StringType(), True),
                StructField("city", StringType(), False),
                StructField("state", StringType(), False),
                StructField("pincode", StringType(), True),
                StructField("latitude", DoubleType(), True),
                StructField("longitude", DoubleType(), True)
            ]), True),
            
            StructField("delivery_distance_km", DoubleType(), True),
            StructField("delivery_type", StringType(), True),  # EXPRESS, STANDARD, SCHEDULED
            
            # User and session info
            StructField("user_segment", StringType(), True),  # NEW, REGULAR, VIP
            StructField("payment_method", StringType(), True),
            StructField("is_first_order", BooleanType(), True),
            StructField("app_version", StringType(), True),
            StructField("device_type", StringType(), True),
            
            # Event metadata
            StructField("event_timestamp", TimestampType(), False),
            StructField("event_source", StringType(), True)
        ])
    
    def create_delivery_schema(self) -> StructType:
        """Create schema for delivery tracking events"""
        return StructType([
            StructField("delivery_id", StringType(), False),
            StructField("order_id", StringType(), False),
            StructField("delivery_partner_id", StringType(), False),
            StructField("partner_name", StringType(), True),
            StructField("vehicle_type", StringType(), True),
            StructField("current_location", StructType([
                StructField("latitude", DoubleType(), False),
                StructField("longitude", DoubleType(), False)
            ]), True),
            StructField("delivery_status", StringType(), False),  # ASSIGNED, PICKED_UP, IN_TRANSIT, DELIVERED
            StructField("pickup_timestamp", TimestampType(), True),
            StructField("delivery_timestamp", TimestampType(), True),
            StructField("estimated_arrival", TimestampType(), True),
            StructField("delivery_notes", StringType(), True),
            StructField("event_timestamp", TimestampType(), False)
        ])
    
    def read_kafka_stream(self, topic: str, schema: StructType) -> DataFrame:
        """Read streaming data from Kafka"""
        logger.info(f"📡 Reading from Kafka topic: {topic}")
        
        # Read from Kafka
        kafka_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.config.kafka_bootstrap_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", self.config.max_offsets_per_trigger) \
            .option("failOnDataLoss", "false") \
            .load()
        
        # Parse JSON messages
        parsed_df = kafka_df.select(
            col("key").cast("string").alias("message_key"),
            from_json(col("value").cast("string"), schema).alias("data"),
            col("topic"),
            col("partition"),
            col("offset"),
            col("timestamp").alias("kafka_timestamp")
        ).select("message_key", "data.*", "topic", "partition", "offset", "kafka_timestamp")
        
        logger.info(f"✅ Kafka stream created for topic: {topic}")
        return parsed_df
    
    def process_order_events(self) -> StreamingQuery:
        """Process order events in real-time"""
        logger.info("🍕 Starting order events processing...")
        
        # Read order stream
        orders_stream = self.read_kafka_stream(
            self.config.kafka_topics['orders'], 
            self.create_order_schema()
        )
        
        # Add watermark for late data handling
        watermarked_orders = orders_stream.withWatermark("event_timestamp", self.config.watermark_delay)
        
        # Enrich orders with derived metrics
        enriched_orders = watermarked_orders.withColumn(
            "order_hour", date_format(col("order_timestamp"), "HH")
        ).withColumn(
            "order_day_of_week", date_format(col("order_timestamp"), "EEEE")  
        ).withColumn(
            "is_weekend", 
            when(date_format(col("order_timestamp"), "EEEE").isin(["Saturday", "Sunday"]), True)
            .otherwise(False)
        ).withColumn(
            "is_peak_hour",
            when(col("order_hour").isin(["12", "13", "19", "20", "21"]), True)
            .otherwise(False)
        ).withColumn(
            "delivery_time_minutes",
            when(col("actual_delivery_time").isNotNull() & col("order_timestamp").isNotNull(),
                 (unix_timestamp("actual_delivery_time") - unix_timestamp("order_timestamp")) / 60)
            .otherwise(None)
        ).withColumn(
            "is_delayed",
            when(col("actual_delivery_time").isNotNull() & col("estimated_delivery_time").isNotNull(),
                 col("actual_delivery_time") > col("estimated_delivery_time"))
            .otherwise(False)
        ).withColumn(
            "revenue_per_item",
            col("total_amount") / F.size(col("items"))
        )
        
        # Real-time order metrics
        order_metrics = enriched_orders.groupBy(
            window(col("event_timestamp"), "1 minute"),
            col("restaurant_location.city"),
            col("order_status")
        ).agg(
            count("order_id").alias("order_count"),
            spark_sum("total_amount").alias("total_revenue"),
            avg("total_amount").alias("avg_order_value"),
            avg("delivery_time_minutes").alias("avg_delivery_time"),
            count(when(col("is_delayed"), True)).alias("delayed_orders"),
            count(when(col("is_peak_hour"), True)).alias("peak_hour_orders"),
            count(when(col("order_status") == "CANCELLED", True)).alias("cancelled_orders")
        ).withColumn(
            "cancellation_rate",
            (col("cancelled_orders") / col("order_count") * 100).cast("decimal(5,2)")
        ).withColumn(
            "delay_rate", 
            (col("delayed_orders") / col("order_count") * 100).cast("decimal(5,2)")
        )
        
        # Write to console for monitoring
        console_query = order_metrics.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime=self.config.trigger_interval) \
            .start()
        
        # Write to Delta Lake for persistence
        delta_query = enriched_orders.writeStream \
            .outputMode("append") \
            .format("delta") \
            .option("checkpointLocation", f"{self.config.checkpoint_path}/orders") \
            .option("path", f"{self.config.output_path}/orders") \
            .partitionBy("order_status", "restaurant_location.city") \
            .trigger(processingTime=self.config.trigger_interval) \
            .start()
        
        self.running_queries.extend([console_query, delta_query])
        logger.info("✅ Order events processing started!")
        return delta_query
    
    def process_delivery_tracking(self) -> StreamingQuery:
        """Process delivery tracking events"""
        logger.info("🛵 Starting delivery tracking processing...")
        
        # Read delivery stream
        delivery_stream = self.read_kafka_stream(
            self.config.kafka_topics['deliveries'],
            self.create_delivery_schema()
        )
        
        # Add watermark
        watermarked_deliveries = delivery_stream.withWatermark("event_timestamp", self.config.watermark_delay)
        
        # Calculate delivery metrics
        delivery_metrics = watermarked_deliveries.withColumn(
            "delivery_duration_minutes",
            when(col("delivery_timestamp").isNotNull() & col("pickup_timestamp").isNotNull(),
                 (unix_timestamp("delivery_timestamp") - unix_timestamp("pickup_timestamp")) / 60)
            .otherwise(None)
        )
        
        # Real-time delivery partner performance
        partner_performance = delivery_metrics.groupBy(
            window(col("event_timestamp"), "5 minutes"),
            col("delivery_partner_id"),
            col("partner_name")
        ).agg(
            count("delivery_id").alias("total_deliveries"),
            count(when(col("delivery_status") == "DELIVERED", True)).alias("completed_deliveries"),
            avg("delivery_duration_minutes").alias("avg_delivery_duration"),
            count(when(col("delivery_duration_minutes") > 30, True)).alias("slow_deliveries")
        ).withColumn(
            "completion_rate",
            (col("completed_deliveries") / col("total_deliveries") * 100).cast("decimal(5,2)")
        ).withColumn(
            "efficiency_score",
            when(col("avg_delivery_duration") <= 20, 100)
            .when(col("avg_delivery_duration") <= 30, 80)
            .when(col("avg_delivery_duration") <= 45, 60)
            .otherwise(40)
        )
        
        # Write delivery metrics
        delivery_query = partner_performance.writeStream \
            .outputMode("update") \
            .format("delta") \
            .option("checkpointLocation", f"{self.config.checkpoint_path}/deliveries") \
            .option("path", f"{self.config.output_path}/delivery_metrics") \
            .trigger(processingTime=self.config.trigger_interval) \
            .start()
        
        self.running_queries.append(delivery_query)
        logger.info("✅ Delivery tracking processing started!")
        return delivery_query
    
    def real_time_restaurant_analytics(self) -> StreamingQuery:
        """Real-time restaurant performance analytics"""
        logger.info("🏪 Starting restaurant analytics...")
        
        # Read orders stream for restaurant analytics
        orders_stream = self.read_kafka_stream(
            self.config.kafka_topics['orders'],
            self.create_order_schema()
        )
        
        watermarked_orders = orders_stream.withWatermark("event_timestamp", self.config.watermark_delay)
        
        # Restaurant performance metrics
        restaurant_metrics = watermarked_orders.groupBy(
            window(col("event_timestamp"), "10 minutes"),
            col("restaurant_id"),
            col("restaurant_name"),
            col("restaurant_location.city")
        ).agg(
            count("order_id").alias("total_orders"),
            spark_sum("total_amount").alias("total_revenue"), 
            avg("total_amount").alias("avg_order_value"),
            count(when(col("order_status") == "DELIVERED", True)).alias("successful_orders"),
            count(when(col("order_status") == "CANCELLED", True)).alias("cancelled_orders"),
            avg("delivery_time_minutes").alias("avg_delivery_time"),
            F.size(collect_set("user_id")).alias("unique_customers")
        ).withColumn(
            "success_rate",
            (col("successful_orders") / col("total_orders") * 100).cast("decimal(5,2)")
        ).withColumn(
            "cancellation_rate", 
            (col("cancelled_orders") / col("total_orders") * 100).cast("decimal(5,2)")
        ).withColumn(
            "performance_score",
            when(col("success_rate") >= 95, 100)
            .when(col("success_rate") >= 90, 80)
            .when(col("success_rate") >= 85, 60)
            .otherwise(40)
        )
        
        # Popular items analysis
        popular_items = watermarked_orders.select(
            col("restaurant_id"),
            col("restaurant_name"), 
            explode(col("items")).alias("item"),
            col("event_timestamp")
        ).withWatermark("event_timestamp", self.config.watermark_delay) \
        .groupBy(
            window(col("event_timestamp"), "15 minutes"),
            col("restaurant_id"),
            col("item.item_name"),
            col("item.category")
        ).agg(
            spark_sum("item.quantity").alias("total_quantity_sold"),
            spark_sum("item.total_price").alias("total_item_revenue"),
            count("item.item_id").alias("order_frequency")
        ).withColumn(
            "item_popularity_score",
            col("total_quantity_sold") + col("order_frequency") * 2
        )
        
        # Write restaurant metrics
        restaurant_query = restaurant_metrics.writeStream \
            .outputMode("update") \
            .format("delta") \
            .option("checkpointLocation", f"{self.config.checkpoint_path}/restaurants") \
            .option("path", f"{self.config.output_path}/restaurant_metrics") \
            .trigger(processingTime=self.config.trigger_interval) \
            .start()
        
        # Write popular items
        items_query = popular_items.writeStream \
            .outputMode("update") \
            .format("delta") \
            .option("checkpointLocation", f"{self.config.checkpoint_path}/popular_items") \
            .option("path", f"{self.config.output_path}/popular_items") \
            .trigger(processingTime=self.config.trigger_interval) \
            .start()
        
        self.running_queries.extend([restaurant_query, items_query])
        logger.info("✅ Restaurant analytics started!")
        return restaurant_query
    
    def city_wise_demand_forecasting(self) -> StreamingQuery:
        """City-wise demand forecasting in real-time"""
        logger.info("🌆 Starting city-wise demand forecasting...")
        
        orders_stream = self.read_kafka_stream(
            self.config.kafka_topics['orders'],
            self.create_order_schema()
        )
        
        watermarked_orders = orders_stream.withWatermark("event_timestamp", self.config.watermark_delay)
        
        # Add time-based features
        enhanced_orders = watermarked_orders.withColumn(
            "hour_of_day", date_format(col("order_timestamp"), "HH").cast("int")
        ).withColumn(
            "day_of_week", date_format(col("order_timestamp"), "u").cast("int")  # 1=Monday, 7=Sunday
        ).withColumn(
            "is_weekend",
            when(col("day_of_week").isin([6, 7]), 1).otherwise(0)
        ).withColumn(
            "is_lunch_hour",
            when(col("hour_of_day").between(11, 14), 1).otherwise(0)
        ).withColumn(
            "is_dinner_hour", 
            when(col("hour_of_day").between(18, 22), 1).otherwise(0)
        )
        
        # City-wise demand patterns
        city_demand = enhanced_orders.groupBy(
            window(col("event_timestamp"), "30 minutes"),
            col("restaurant_location.city"),
            col("restaurant_location.state"),
            col("hour_of_day")
        ).agg(
            count("order_id").alias("order_count"),
            spark_sum("total_amount").alias("total_revenue"),
            avg("total_amount").alias("avg_order_value"),
            count(when(col("is_lunch_hour") == 1, True)).alias("lunch_orders"),
            count(when(col("is_dinner_hour") == 1, True)).alias("dinner_orders"),
            F.size(collect_set("restaurant_id")).alias("active_restaurants"),
            F.size(collect_set("user_id")).alias("unique_users")
        )
        
        # Add trend analysis using window functions
        city_window = Window.partitionBy("city", "state").orderBy("window")
        
        demand_trends = city_demand.withColumn(
            "prev_hour_orders",
            lag("order_count", 1).over(city_window)
        ).withColumn(
            "order_growth_rate",
            when(col("prev_hour_orders") > 0,
                 ((col("order_count") - col("prev_hour_orders")) / col("prev_hour_orders") * 100).cast("decimal(5,2)")))
        .withColumn(
            "demand_level",
            when(col("order_count") >= 1000, "VERY_HIGH")
            .when(col("order_count") >= 500, "HIGH")
            .when(col("order_count") >= 200, "MEDIUM")
            .when(col("order_count") >= 50, "LOW")
            .otherwise("VERY_LOW")
        ).withColumn(
            "restaurant_saturation",
            (col("order_count") / col("active_restaurants")).cast("decimal(8,2)")
        )
        
        # Real-time alerts for demand spikes
        demand_alerts = demand_trends.filter(
            (col("order_growth_rate") > 50) |  # 50% increase in orders
            (col("demand_level") == "VERY_HIGH") |
            (col("restaurant_saturation") > 100)  # More than 100 orders per restaurant
        ).select(
            col("window"),
            col("city"),
            col("state"),
            col("order_count"),
            col("order_growth_rate"),
            col("demand_level"),
            col("restaurant_saturation"),
            lit("DEMAND_SPIKE").alias("alert_type"),
            current_timestamp().alias("alert_timestamp")
        )
        
        # Write demand forecasting results
        demand_query = demand_trends.writeStream \
            .outputMode("update") \
            .format("delta") \
            .option("checkpointLocation", f"{self.config.checkpoint_path}/demand_forecast") \
            .option("path", f"{self.config.output_path}/demand_forecast") \
            .trigger(processingTime=self.config.trigger_interval) \
            .start()
        
        # Write alerts to separate stream for immediate action
        alerts_query = demand_alerts.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="30 seconds") \
            .start()
        
        self.running_queries.extend([demand_query, alerts_query])
        logger.info("✅ Demand forecasting started!")
        return demand_query
    
    def fraud_detection_stream(self) -> StreamingQuery:
        """Real-time fraud detection for orders"""
        logger.info("🕵️ Starting fraud detection stream...")
        
        orders_stream = self.read_kafka_stream(
            self.config.kafka_topics['orders'],
            self.create_order_schema()
        )
        
        watermarked_orders = orders_stream.withWatermark("event_timestamp", self.config.watermark_delay)
        
        # User behavior analysis window (last 1 hour)
        user_window = Window.partitionBy("user_id") \
            .orderBy("event_timestamp") \
            .rangeBetween(-3600, 0)  # 1 hour in seconds
        
        # Calculate fraud indicators
        fraud_features = watermarked_orders.withColumn(
            "orders_last_hour",
            count("order_id").over(user_window)
        ).withColumn(
            "total_spent_last_hour", 
            spark_sum("total_amount").over(user_window)
        ).withColumn(
            "unique_restaurants_last_hour",
            F.size(collect_set("restaurant_id").over(user_window))
        ).withColumn(
            "different_cities_last_hour",
            F.size(collect_set("restaurant_location.city").over(user_window))
        ).withColumn(
            "high_value_orders_last_hour",
            count(when(col("total_amount") > 2000, True)).over(user_window)
        ).withColumn(
            "cancelled_orders_last_hour",
            count(when(col("order_status") == "CANCELLED", True)).over(user_window)
        )
        
        # Calculate fraud score
        fraud_scored = fraud_features.withColumn(
            "fraud_score",
            # Multiple orders in short time
            when(col("orders_last_hour") > 10, 20)
            .when(col("orders_last_hour") > 5, 10)
            .otherwise(0) +
            # High spending
            when(col("total_spent_last_hour") > 10000, 25)
            .when(col("total_spent_last_hour") > 5000, 15)
            .otherwise(0) +
            # Multiple cities (impossible delivery)
            when(col("different_cities_last_hour") > 2, 30)
            .when(col("different_cities_last_hour") > 1, 10)
            .otherwise(0) +
            # Too many restaurants
            when(col("unique_restaurants_last_hour") > 8, 15)
            .when(col("unique_restaurants_last_hour") > 5, 8)
            .otherwise(0) +
            # High cancellation rate
            when(col("cancelled_orders_last_hour") > 3, 20)
            .when(col("cancelled_orders_last_hour") > 1, 10)
            .otherwise(0)
        ).withColumn(
            "risk_level",
            when(col("fraud_score") >= 60, "HIGH")
            .when(col("fraud_score") >= 30, "MEDIUM")
            .when(col("fraud_score") >= 15, "LOW")
            .otherwise("MINIMAL")
        ).withColumn(
            "requires_review",
            col("fraud_score") >= 30
        )
        
        # Filter high-risk transactions
        high_risk_orders = fraud_scored.filter(
            col("risk_level").isin(["HIGH", "MEDIUM"])
        ).select(
            col("order_id"),
            col("user_id"),
            col("total_amount"),
            col("restaurant_name"),
            col("restaurant_location.city"),
            col("fraud_score"),
            col("risk_level"),
            col("orders_last_hour"),
            col("total_spent_last_hour"),
            col("different_cities_last_hour"),
            col("event_timestamp")
        )
        
        # Write fraud detection results
        fraud_query = high_risk_orders.writeStream \
            .outputMode("append") \
            .format("delta") \
            .option("checkpointLocation", f"{self.config.checkpoint_path}/fraud_detection") \
            .option("path", f"{self.config.output_path}/fraud_alerts") \
            .trigger(processingTime="15 seconds") \
            .start()
        
        # Real-time console output for immediate action
        fraud_console = high_risk_orders.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="10 seconds") \
            .start()
        
        self.running_queries.extend([fraud_query, fraud_console])
        logger.info("✅ Fraud detection stream started!")
        return fraud_query
    
    def start_all_streams(self) -> List[StreamingQuery]:
        """Start all streaming queries"""
        logger.info("🚀 Starting all Zomato streaming pipelines...")
        
        try:
            # Start all streaming processes
            order_query = self.process_order_events()
            delivery_query = self.process_delivery_tracking() 
            restaurant_query = self.real_time_restaurant_analytics()
            demand_query = self.city_wise_demand_forecasting()
            fraud_query = self.fraud_detection_stream()
            
            logger.info(f"✅ Started {len(self.running_queries)} streaming queries")
            
            return self.running_queries
            
        except Exception as e:
            logger.error(f"❌ Failed to start streaming pipelines: {str(e)}")
            self.stop_all_streams()
            raise
    
    def stop_all_streams(self):
        """Stop all running streaming queries"""
        logger.info("⏹️ Stopping all streaming queries...")
        
        for query in self.running_queries:
            try:
                if query.isActive:
                    query.stop()
                    logger.info(f"Stopped query: {query.name}")
            except Exception as e:
                logger.error(f"Error stopping query: {str(e)}")
        
        logger.info("✅ All streaming queries stopped!")
    
    def get_streaming_metrics(self) -> Dict[str, Any]:
        """Get metrics from all running streams"""
        metrics = {
            "total_queries": len(self.running_queries),
            "active_queries": sum(1 for q in self.running_queries if q.isActive),
            "query_details": []
        }
        
        for query in self.running_queries:
            if query.isActive:
                progress = query.lastProgress
                metrics["query_details"].append({
                    "query_name": query.name,
                    "status": "RUNNING",
                    "input_rows_per_second": progress.get("inputRowsPerSecond", 0),
                    "processed_rows_per_second": progress.get("processedRowsPerSecond", 0),
                    "batch_duration": progress.get("durationMs", {}).get("triggerExecution", 0)
                })
            else:
                metrics["query_details"].append({
                    "query_name": query.name,
                    "status": "STOPPED"
                })
        
        return metrics
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up streaming resources...")
        self.stop_all_streams()
        self.spark.stop()
        logger.info("✅ Cleanup completed!")

def main():
    """Main function to run Zomato streaming ETL"""
    
    # Configure streaming
    config = StreamingConfig(
        kafka_bootstrap_servers="localhost:9092",
        checkpoint_path="/data/zomato/checkpoints",
        output_path="/data/zomato/streaming",
        trigger_interval="10 seconds"
    )
    
    # Initialize streaming ETL
    streaming_etl = ZomatoStreamingETL(config)
    
    try:
        logger.info("🚀 Starting Zomato Real-time Streaming ETL...")
        
        # Start all streaming pipelines
        queries = streaming_etl.start_all_streams()
        
        logger.info(f"✅ All {len(queries)} streaming queries started successfully!")
        
        # Monitor streams for a demo period (in production, this would run indefinitely)
        import time
        monitor_duration = 300  # 5 minutes
        logger.info(f"Monitoring streams for {monitor_duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < monitor_duration:
            time.sleep(30)  # Check every 30 seconds
            
            # Get metrics
            metrics = streaming_etl.get_streaming_metrics()
            logger.info(f"Streaming Metrics: {json.dumps(metrics, indent=2, default=str)}")
            
            # Check if all queries are still active
            active_count = metrics["active_queries"]
            if active_count < metrics["total_queries"]:
                logger.warning(f"Some queries stopped! Active: {active_count}/{metrics['total_queries']}")
        
        logger.info("🎉 Monitoring completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Received interrupt signal, stopping streams...")
    except Exception as e:
        logger.error(f"❌ Streaming ETL failed: {str(e)}")
        raise
    finally:
        streaming_etl.cleanup()

if __name__ == "__main__":
    main()

"""
Mumbai Learning Notes:
1. Real-time streaming ETL with Kafka and Structured Streaming
2. Watermarking and late data handling for production reliability
3. Complex window operations for time-based analytics
4. Real-time fraud detection using streaming patterns
5. City-wise demand forecasting for business intelligence
6. Restaurant performance analytics in real-time
7. Delivery tracking and partner performance monitoring
8. Scalable streaming architecture for Indian food delivery scale

Production Deployment:
- Set up Kafka cluster with proper replication
- Configure Spark Streaming cluster with auto-scaling
- Implement monitoring and alerting for stream failures
- Set up proper checkpointing and state management
- Add data quality checks and error handling
- Configure resource allocation based on peak load
- Implement stream recovery and backfill procedures
- Add security and authentication for Kafka topics
"""