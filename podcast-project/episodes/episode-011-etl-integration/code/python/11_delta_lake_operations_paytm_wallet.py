#!/usr/bin/env python3
"""
Advanced Delta Lake Operations for Paytm Wallet Analytics
Focus: Time travel, ACID transactions, schema evolution, optimization

Ye Delta Lake implementation Paytm Wallet ke transaction data ke liye hai.
Mumbai ke banking jaise secure aur reliable!

Production Ready: Yes
Testing Required: Yes
Performance: Optimized for millions of transactions
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
    row_number, rank, dense_rank,
    lag, lead, first, last,
    collect_list, collect_set,
    coalesce, split, trim, lower,
    regexp_replace, regexp_extract,
    monotonically_increasing_id,
    sha2, md5, uuid
)
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, BooleanType, DecimalType
import pyspark.sql.functions as F

# Delta Lake imports
from delta.tables import DeltaTable
from delta import configure_spark_with_delta_pip

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DeltaLakeConfig:
    """Configuration for Delta Lake operations"""
    base_path: str = "/data/paytm/delta/"
    checkpoint_path: str = "/data/paytm/checkpoints/"
    warehouse_path: str = "/data/paytm/warehouse/"
    table_properties: Dict[str, str] = None
    partition_columns: List[str] = None
    optimization_schedule: str = "0 2 * * *"  # Daily at 2 AM
    retention_days: int = 30
    vacuum_retention_hours: int = 168  # 7 days
    
    def __post_init__(self):
        if self.table_properties is None:
            self.table_properties = {
                'delta.autoOptimize.optimizeWrite': 'true',
                'delta.autoOptimize.autoCompact': 'true',
                'delta.tuneFileSizesForRewrites': 'true',
                'delta.enableChangeDataFeed': 'true'
            }
        if self.partition_columns is None:
            self.partition_columns = ['year', 'month', 'day']

class PaytmWalletDeltaLake:
    """
    Advanced Delta Lake operations for Paytm Wallet
    
    Mumbai ke UPI transactions jaise fast aur secure!
    """
    
    def __init__(self, config: DeltaLakeConfig):
        self.config = config
        self.spark = self._create_spark_session()
        self.delta_tables = {}
        
    def _create_spark_session(self) -> SparkSession:
        """Create Spark session with Delta Lake configuration"""
        logger.info("🚀 Creating Spark session with Delta Lake...")
        
        # Configure Spark for Delta Lake
        builder = SparkSession.builder \
            .appName("PaytmWalletDeltaLake") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.sql.parquet.compression.codec", "snappy") \
            .config("spark.sql.warehouse.dir", self.config.warehouse_path) \
            .config("spark.databricks.delta.retentionDurationCheck.enabled", "false") \
            .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \
            .config("spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite", "true") \
            .config("spark.databricks.delta.properties.defaults.autoOptimize.autoCompact", "true")
        
        # Configure Delta Lake
        spark = configure_spark_with_delta_pip(builder).getOrCreate()
        
        # Set checkpoint directory
        spark.sparkContext.setCheckpointDir(self.config.checkpoint_path)
        
        logger.info("✅ Spark session with Delta Lake created successfully!")
        return spark
    
    def create_wallet_transaction_schema(self) -> StructType:
        """Create schema for Paytm wallet transactions"""
        return StructType([
            # Transaction identifiers
            StructField("transaction_id", StringType(), False),
            StructField("order_id", StringType(), True),
            StructField("paytm_transaction_id", StringType(), True),
            StructField("wallet_id", StringType(), False),
            StructField("user_id", StringType(), False),
            
            # Transaction details
            StructField("transaction_type", StringType(), False),  # CREDIT, DEBIT, TRANSFER
            StructField("transaction_category", StringType(), True), # RECHARGE, BILL_PAYMENT, P2P, etc.
            StructField("amount", DecimalType(15, 2), False),
            StructField("fee", DecimalType(10, 2), True),
            StructField("tax", DecimalType(10, 2), True),
            StructField("net_amount", DecimalType(15, 2), False),
            
            # Status and timing
            StructField("status", StringType(), False),  # SUCCESS, FAILED, PENDING, REFUNDED
            StructField("transaction_timestamp", TimestampType(), False),
            StructField("processed_timestamp", TimestampType(), True),
            StructField("settlement_timestamp", TimestampType(), True),
            
            # Source and destination
            StructField("source_type", StringType(), True),  # BANK, CARD, UPI, WALLET
            StructField("source_identifier", StringType(), True),
            StructField("destination_type", StringType(), True),
            StructField("destination_identifier", StringType(), True),
            
            # Merchant information (for payments)
            StructField("merchant_id", StringType(), True),
            StructField("merchant_name", StringType(), True),
            StructField("merchant_category", StringType(), True),
            StructField("mcc_code", StringType(), True),
            
            # Risk and compliance
            StructField("risk_score", DoubleType(), True),
            StructField("is_suspicious", BooleanType(), True),
            StructField("kyc_status", StringType(), True),
            StructField("compliance_flags", StringType(), True),
            
            # Geographic and device info
            StructField("city", StringType(), True),
            StructField("state", StringType(), True),
            StructField("country", StringType(), True),
            StructField("device_id", StringType(), True),
            StructField("device_type", StringType(), True),
            StructField("app_version", StringType(), True),
            
            # Partition columns
            StructField("year", StringType(), False),
            StructField("month", StringType(), False),
            StructField("day", StringType(), False),
            StructField("hour", StringType(), False)
        ])
    
    def create_delta_table(self, table_name: str, schema: StructType, 
                          partition_cols: List[str] = None) -> DeltaTable:
        """Create Delta Lake table with configuration"""
        logger.info(f"📊 Creating Delta table: {table_name}")
        
        table_path = f"{self.config.base_path}/{table_name}"
        
        if partition_cols is None:
            partition_cols = self.config.partition_columns
        
        # Create table builder
        builder = DeltaTable.create(self.spark) \
            .tableName(table_name) \
            .location(table_path) \
            .addColumns(schema)
        
        # Add partitioning
        if partition_cols:
            builder = builder.partitionedBy(*partition_cols)
        
        # Add table properties
        for key, value in self.config.table_properties.items():
            builder = builder.property(key, value)
        
        # Create table
        delta_table = builder.execute()
        
        # Store reference
        self.delta_tables[table_name] = {
            'table': delta_table,
            'path': table_path,
            'schema': schema
        }
        
        logger.info(f"✅ Delta table created: {table_name}")
        return delta_table
    
    def get_or_create_table(self, table_name: str) -> DeltaTable:
        """Get existing Delta table or create new one"""
        table_path = f"{self.config.base_path}/{table_name}"
        
        try:
            # Try to load existing table
            delta_table = DeltaTable.forPath(self.spark, table_path)
            logger.info(f"📖 Loaded existing Delta table: {table_name}")
            
        except Exception:
            # Create new table if it doesn't exist
            logger.info(f"Creating new Delta table: {table_name}")
            schema = self.create_wallet_transaction_schema()
            delta_table = self.create_delta_table(table_name, schema)
        
        return delta_table
    
    def upsert_wallet_transactions(self, df: DataFrame, table_name: str = "wallet_transactions") -> Dict[str, Any]:
        """Upsert wallet transactions using Delta Lake MERGE"""
        logger.info(f"💫 Upserting transactions to table: {table_name}")
        
        # Get or create Delta table
        delta_table = self.get_or_create_table(table_name)
        
        # Add partition columns if not present
        df_with_partitions = df.withColumn(
            "year", date_format(col("transaction_timestamp"), "yyyy")
        ).withColumn(
            "month", date_format(col("transaction_timestamp"), "MM")
        ).withColumn(
            "day", date_format(col("transaction_timestamp"), "dd")
        ).withColumn(
            "hour", date_format(col("transaction_timestamp"), "HH")
        )
        
        # Add processing metadata
        df_final = df_with_partitions.withColumn(
            "data_ingestion_timestamp", current_timestamp()
        ).withColumn(
            "data_hash", sha2(
                F.concat_ws("|", col("transaction_id"), col("amount"), col("status")), 256
            )
        )
        
        # Perform MERGE operation
        merge_condition = "target.transaction_id = source.transaction_id"
        
        merge_stats = delta_table.alias("target").merge(
            df_final.alias("source"),
            merge_condition
        ).whenMatchedUpdate(set={
            "status": "source.status",
            "processed_timestamp": "source.processed_timestamp",
            "settlement_timestamp": "source.settlement_timestamp",
            "risk_score": "source.risk_score",
            "is_suspicious": "source.is_suspicious",
            "data_ingestion_timestamp": "current_timestamp()",
            "data_hash": "source.data_hash"
        }).whenNotMatchedInsert(values={
            col_name: f"source.{col_name}" for col_name in df_final.columns
        }).execute()
        
        logger.info(f"✅ MERGE operation completed: {merge_stats}")
        return merge_stats
    
    def time_travel_analysis(self, table_name: str, 
                           analysis_type: str = "version_comparison") -> Dict[str, Any]:
        """Perform time travel analysis on Delta table"""
        logger.info(f"⏰ Performing time travel analysis: {analysis_type}")
        
        table_path = f"{self.config.base_path}/{table_name}"
        
        if analysis_type == "version_comparison":
            # Compare current vs previous version
            current_df = self.spark.read.format("delta").load(table_path)
            previous_df = self.spark.read.format("delta").option("versionAsOf", "1").load(table_path)
            
            current_stats = current_df.agg(
                count("*").alias("current_count"),
                spark_sum("amount").alias("current_total_amount")
            ).collect()[0]
            
            previous_stats = previous_df.agg(
                count("*").alias("previous_count"),
                spark_sum("amount").alias("previous_total_amount")
            ).collect()[0]
            
            comparison = {
                "current_version": {
                    "record_count": current_stats["current_count"],
                    "total_amount": float(current_stats["current_total_amount"] or 0)
                },
                "previous_version": {
                    "record_count": previous_stats["previous_count"],
                    "total_amount": float(previous_stats["previous_total_amount"] or 0)
                },
                "changes": {
                    "record_delta": current_stats["current_count"] - previous_stats["previous_count"],
                    "amount_delta": float((current_stats["current_total_amount"] or 0) - (previous_stats["previous_total_amount"] or 0))
                }
            }
            
        elif analysis_type == "historical_trends":
            # Analyze trends over multiple versions
            delta_table = DeltaTable.forPath(self.spark, table_path)
            history_df = delta_table.history()
            
            trends = history_df.select(
                "version",
                "timestamp",
                "operationMetrics.numOutputRows",
                "operationMetrics.numOutputBytes"
            ).collect()
            
            comparison = {
                "version_history": [
                    {
                        "version": row["version"],
                        "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                        "rows_written": row["numOutputRows"],
                        "bytes_written": row["numOutputBytes"]
                    } for row in trends
                ]
            }
            
        elif analysis_type == "point_in_time":
            # Analyze data at specific timestamp (yesterday)
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
            
            pit_df = self.spark.read.format("delta") \
                .option("timestampAsOf", yesterday_str) \
                .load(table_path)
            
            pit_stats = pit_df.agg(
                count("*").alias("record_count"),
                spark_sum("amount").alias("total_amount"),
                count(when(col("status") == "SUCCESS", 1)).alias("success_count"),
                count(when(col("status") == "FAILED", 1)).alias("failed_count")
            ).collect()[0]
            
            comparison = {
                "point_in_time": yesterday_str,
                "statistics": {
                    "record_count": pit_stats["record_count"],
                    "total_amount": float(pit_stats["total_amount"] or 0),
                    "success_count": pit_stats["success_count"],
                    "failed_count": pit_stats["failed_count"],
                    "success_rate": (pit_stats["success_count"] / pit_stats["record_count"] * 100) if pit_stats["record_count"] > 0 else 0
                }
            }
        
        logger.info(f"✅ Time travel analysis completed: {analysis_type}")
        return comparison
    
    def schema_evolution_example(self, table_name: str) -> Dict[str, Any]:
        """Demonstrate schema evolution capabilities"""
        logger.info(f"🔄 Demonstrating schema evolution for: {table_name}")
        
        table_path = f"{self.config.base_path}/{table_name}"
        
        # Create sample data with new columns
        evolved_data = self.spark.createDataFrame([
            ("TXN_001", "WALLET_001", "USER_001", "CREDIT", 1000.0, "SUCCESS", 
             datetime.now(), "Mumbai", "Maharashtra", "IN", "NEW_COLUMN_VALUE", 123.45, True),
        ], schema=StructType([
            StructField("transaction_id", StringType(), False),
            StructField("wallet_id", StringType(), False),
            StructField("user_id", StringType(), False),
            StructField("transaction_type", StringType(), False),
            StructField("amount", DoubleType(), False),
            StructField("status", StringType(), False),
            StructField("transaction_timestamp", TimestampType(), False),
            StructField("city", StringType(), True),
            StructField("state", StringType(), True),
            StructField("country", StringType(), True),
            # New columns for schema evolution
            StructField("new_feature_flag", StringType(), True),
            StructField("ai_risk_score", DoubleType(), True),
            StructField("is_premium_user", BooleanType(), True)
        ]))
        
        # Add partition columns
        evolved_data = evolved_data.withColumn(
            "year", date_format(col("transaction_timestamp"), "yyyy")
        ).withColumn(
            "month", date_format(col("transaction_timestamp"), "MM")
        ).withColumn(
            "day", date_format(col("transaction_timestamp"), "dd")
        )
        
        # Write with schema merging enabled
        try:
            evolved_data.write \
                .format("delta") \
                .mode("append") \
                .option("mergeSchema", "true") \
                .save(table_path)
            
            # Verify schema evolution
            delta_table = DeltaTable.forPath(self.spark, table_path)
            current_schema = delta_table.toDF().schema
            
            schema_info = {
                "schema_evolution": "SUCCESS",
                "new_columns_added": ["new_feature_flag", "ai_risk_score", "is_premium_user"],
                "total_columns": len(current_schema.fields),
                "column_names": [field.name for field in current_schema.fields]
            }
            
        except Exception as e:
            schema_info = {
                "schema_evolution": "FAILED",
                "error": str(e)
            }
        
        logger.info(f"✅ Schema evolution completed: {schema_info}")
        return schema_info
    
    def optimize_delta_table(self, table_name: str, optimization_type: str = "compact") -> Dict[str, Any]:
        """Optimize Delta Lake table for performance"""
        logger.info(f"⚡ Optimizing Delta table: {table_name} ({optimization_type})")
        
        table_path = f"{self.config.base_path}/{table_name}"
        delta_table = DeltaTable.forPath(self.spark, table_path)
        
        optimization_results = {}
        
        if optimization_type == "compact":
            # File compaction
            before_files = self.spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]["numFiles"]
            
            # Run OPTIMIZE command
            self.spark.sql(f"OPTIMIZE delta.`{table_path}`")
            
            after_files = self.spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]["numFiles"]
            
            optimization_results = {
                "optimization_type": "compact",
                "files_before": before_files,
                "files_after": after_files,
                "files_reduced": before_files - after_files,
                "compression_ratio": f"{((before_files - after_files) / before_files * 100):.2f}%" if before_files > 0 else "0%"
            }
            
        elif optimization_type == "z_order":
            # Z-order optimization for frequently queried columns
            optimize_columns = ["user_id", "transaction_timestamp", "status"]
            
            self.spark.sql(f"""
                OPTIMIZE delta.`{table_path}`
                ZORDER BY ({', '.join(optimize_columns)})
            """)
            
            optimization_results = {
                "optimization_type": "z_order",
                "optimized_columns": optimize_columns,
                "status": "completed"
            }
            
        elif optimization_type == "vacuum":
            # Clean up old files
            retention_hours = self.config.vacuum_retention_hours
            
            # Get file count before vacuum
            file_count_before = len(self.spark.sql(f"""
                DESCRIBE DETAIL delta.`{table_path}`
            """).collect())
            
            # Run VACUUM
            self.spark.sql(f"""
                VACUUM delta.`{table_path}` RETAIN {retention_hours} HOURS
            """)
            
            file_count_after = len(self.spark.sql(f"""
                DESCRIBE DETAIL delta.`{table_path}`
            """).collect())
            
            optimization_results = {
                "optimization_type": "vacuum",
                "retention_hours": retention_hours,
                "files_before": file_count_before,
                "files_after": file_count_after,
                "files_cleaned": file_count_before - file_count_after
            }
        
        logger.info(f"✅ Table optimization completed: {optimization_results}")
        return optimization_results
    
    def audit_trail_analysis(self, table_name: str) -> Dict[str, Any]:
        """Analyze Delta Lake audit trail and operations"""
        logger.info(f"📋 Analyzing audit trail for: {table_name}")
        
        table_path = f"{self.config.base_path}/{table_name}"
        delta_table = DeltaTable.forPath(self.spark, table_path)
        
        # Get detailed history
        history_df = delta_table.history()
        
        # Analyze operations
        operations_summary = history_df.groupBy("operation").agg(
            count("*").alias("operation_count"),
            spark_max("timestamp").alias("last_executed"),
            spark_min("timestamp").alias("first_executed")
        ).collect()
        
        # Get recent operations (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_operations = history_df.filter(
            col("timestamp") >= lit(recent_cutoff)
        ).select(
            "version", "timestamp", "operation", "operationParameters",
            "operationMetrics.numOutputRows", "operationMetrics.numOutputBytes"
        ).collect()
        
        audit_info = {
            "operations_summary": [
                {
                    "operation": row["operation"],
                    "count": row["operation_count"],
                    "last_executed": row["last_executed"].isoformat() if row["last_executed"] else None,
                    "first_executed": row["first_executed"].isoformat() if row["first_executed"] else None
                } for row in operations_summary
            ],
            "recent_operations": [
                {
                    "version": row["version"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "operation": row["operation"],
                    "parameters": row["operationParameters"],
                    "rows_affected": row["numOutputRows"],
                    "bytes_written": row["numOutputBytes"]
                } for row in recent_operations
            ],
            "total_versions": history_df.count(),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Audit trail analysis completed")
        return audit_info
    
    def fraud_detection_pipeline(self, table_name: str = "wallet_transactions") -> DataFrame:
        """Advanced fraud detection using Delta Lake features"""
        logger.info("🕵️ Running fraud detection pipeline...")
        
        table_path = f"{self.config.base_path}/{table_name}"
        
        # Read current transactions
        df = self.spark.read.format("delta").load(table_path)
        
        # Define user behavior window
        user_window = Window.partitionBy("user_id").orderBy("transaction_timestamp") \
            .rangeBetween(-86400, 0)  # 24 hours window
        
        # Calculate fraud indicators
        fraud_features = df.withColumn(
            "daily_transaction_count",
            count("transaction_id").over(user_window)
        ).withColumn(
            "daily_transaction_amount",
            spark_sum("amount").over(user_window)
        ).withColumn(
            "avg_transaction_amount",
            avg("amount").over(user_window)
        ).withColumn(
            "unique_merchants_daily",
            F.size(collect_set("merchant_id").over(user_window))
        ).withColumn(
            "different_cities_daily",
            F.size(collect_set("city").over(user_window))
        ).withColumn(
            "night_transactions",
            count(when((F.hour("transaction_timestamp") >= 23) | 
                      (F.hour("transaction_timestamp") <= 5), 1)).over(user_window)
        )
        
        # Calculate fraud score
        fraud_scored = fraud_features.withColumn(
            "calculated_fraud_score",
            # Complex fraud scoring algorithm
            when(col("daily_transaction_count") > 50, 30)
            .when(col("daily_transaction_count") > 20, 15)
            .otherwise(0) +
            when(col("daily_transaction_amount") > 100000, 25)
            .when(col("daily_transaction_amount") > 50000, 15)
            .otherwise(0) +
            when(col("different_cities_daily") > 3, 20)
            .when(col("different_cities_daily") > 1, 10)
            .otherwise(0) +
            when(col("night_transactions") > 5, 15)
            .when(col("night_transactions") > 2, 8)
            .otherwise(0) +
            when(col("amount") > col("avg_transaction_amount") * 10, 20)
            .when(col("amount") > col("avg_transaction_amount") * 5, 10)
            .otherwise(0)
        ).withColumn(
            "fraud_risk_level",
            when(col("calculated_fraud_score") >= 70, "HIGH")
            .when(col("calculated_fraud_score") >= 40, "MEDIUM")
            .when(col("calculated_fraud_score") >= 20, "LOW")
            .otherwise("MINIMAL")
        ).withColumn(
            "requires_manual_review",
            col("calculated_fraud_score") >= 40
        )
        
        # Update risk scores in Delta table
        fraud_updates = fraud_scored.select(
            "transaction_id", "calculated_fraud_score", 
            "fraud_risk_level", "requires_manual_review"
        )
        
        # Write fraud scores back to Delta table using MERGE
        delta_table = DeltaTable.forPath(self.spark, table_path)
        
        delta_table.alias("target").merge(
            fraud_updates.alias("source"),
            "target.transaction_id = source.transaction_id"
        ).whenMatchedUpdate(set={
            "risk_score": "source.calculated_fraud_score",
            "is_suspicious": "source.requires_manual_review"
        }).execute()
        
        # Return high-risk transactions for manual review
        high_risk_transactions = fraud_scored.filter(
            col("fraud_risk_level") == "HIGH"
        ).select(
            "transaction_id", "user_id", "amount", "merchant_name",
            "city", "calculated_fraud_score", "daily_transaction_count",
            "daily_transaction_amount", "different_cities_daily"
        )
        
        logger.info("✅ Fraud detection pipeline completed")
        return high_risk_transactions
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up Delta Lake resources...")
        self.spark.stop()
        logger.info("✅ Cleanup completed!")

def main():
    """Main function to demonstrate Delta Lake operations"""
    
    # Configure Delta Lake
    config = DeltaLakeConfig(
        base_path="/data/paytm/delta",
        checkpoint_path="/data/paytm/checkpoints",
        warehouse_path="/data/paytm/warehouse"
    )
    
    # Initialize Delta Lake operations
    delta_ops = PaytmWalletDeltaLake(config)
    
    try:
        logger.info("🚀 Starting Paytm Wallet Delta Lake operations...")
        
        # Create sample wallet transaction data
        sample_data = delta_ops.spark.createDataFrame([
            ("TXN_001", None, "PTM_001", "WALLET_001", "USER_001", "CREDIT", "RECHARGE", 
             1000.0, 10.0, 18.0, 1008.0, "SUCCESS", 
             datetime.now(), datetime.now(), datetime.now(),
             "UPI", "user@paytm", "WALLET", "WALLET_001", 
             None, None, None, None,
             75.5, False, "VERIFIED", None,
             "Mumbai", "Maharashtra", "IN", "DEVICE_001", "ANDROID", "v12.1.0",
             "2024", "01", "15", "10"),
            ("TXN_002", "ORDER_002", "PTM_002", "WALLET_002", "USER_002", "DEBIT", "BILL_PAYMENT",
             2500.0, 25.0, 45.0, 2520.0, "SUCCESS",
             datetime.now() - timedelta(hours=1), datetime.now() - timedelta(hours=1), None,
             "WALLET", "WALLET_002", "BILLER", "ELECTRICITY_BOARD",
             "MERCHANT_001", "MSEB", "UTILITY", "1234",
             25.5, False, "VERIFIED", None,
             "Pune", "Maharashtra", "IN", "DEVICE_002", "iOS", "v12.1.0",
             "2024", "01", "15", "09")
        ], schema=delta_ops.create_wallet_transaction_schema())
        
        # 1. Upsert transactions
        upsert_results = delta_ops.upsert_wallet_transactions(sample_data, "wallet_transactions")
        logger.info(f"Upsert results: {upsert_results}")
        
        # 2. Time travel analysis
        time_travel_results = delta_ops.time_travel_analysis("wallet_transactions", "version_comparison")
        logger.info(f"Time travel analysis: {json.dumps(time_travel_results, indent=2, default=str)}")
        
        # 3. Schema evolution
        schema_evolution_results = delta_ops.schema_evolution_example("wallet_transactions")
        logger.info(f"Schema evolution: {json.dumps(schema_evolution_results, indent=2, default=str)}")
        
        # 4. Optimize table
        optimization_results = delta_ops.optimize_delta_table("wallet_transactions", "compact")
        logger.info(f"Optimization results: {json.dumps(optimization_results, indent=2, default=str)}")
        
        # 5. Audit trail analysis
        audit_results = delta_ops.audit_trail_analysis("wallet_transactions")
        logger.info(f"Audit trail: {json.dumps(audit_results, indent=2, default=str)}")
        
        # 6. Fraud detection pipeline
        high_risk_transactions = delta_ops.fraud_detection_pipeline("wallet_transactions")
        logger.info(f"High risk transactions found: {high_risk_transactions.count()}")
        if high_risk_transactions.count() > 0:
            high_risk_transactions.show(10, truncate=False)
        
        logger.info("🎉 All Delta Lake operations completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Delta Lake operations failed: {str(e)}")
        raise
    finally:
        delta_ops.cleanup()

if __name__ == "__main__":
    main()

"""
Mumbai Learning Notes:
1. Delta Lake ACID transaction capabilities for financial data
2. Time travel queries for audit and compliance
3. Schema evolution for agile development
4. Advanced optimization techniques (OPTIMIZE, Z-ORDER, VACUUM)
5. Fraud detection using window functions and Delta Lake features
6. Audit trail analysis for compliance requirements
7. Partition strategies for large-scale Indian payment data
8. Integration with Spark SQL for complex analytics

Production Deployment:
- Set up proper Delta Lake cluster configuration
- Configure appropriate storage (S3/HDFS/Azure) for table storage
- Implement data governance and access controls
- Set up monitoring for Delta Lake operations
- Configure automated optimization schedules
- Implement backup and disaster recovery procedures
- Add compliance logging for financial regulations
- Set up real-time fraud detection alerts
"""