"""
Hotstar-style Real-time Viewership Count using Spark Streaming
यह Spark Streaming application Hotstar जैसे platforms के लिए real-time viewership tracking करती है
Example: IPL matches के दौरान concurrent viewers, regional distribution, quality metrics
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.streaming import *
import json
from datetime import datetime, timedelta

class HotstarViewershipAnalytics:
    
    def __init__(self):
        """
        Spark session initialize करते हैं optimized settings के साथ
        Hotstar-scale data के लिए high-performance configuration
        """
        self.spark = SparkSession.builder \
            .appName("Hotstar IPL Viewership Analytics") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
            .config("spark.sql.streaming.stateStore.maintenanceInterval", "60s") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.streaming.kafka.consumer.cache.capacity", "64") \
            .getOrCreate()
        
        # Set log level to reduce noise during processing
        self.spark.sparkContext.setLogLevel("WARN")
        
        print("🏏 Hotstar IPL Viewership Analytics शुरू हो रहा है...")
    
    def create_viewer_events_schema(self):
        """
        Viewer events के लिए schema define करते हैं
        Hotstar से आने वाले viewer data का structure
        """
        return StructType([
            StructField("viewer_id", StringType(), True),
            StructField("match_id", StringType(), True),
            StructField("event_type", StringType(), True),  # JOIN, LEAVE, QUALITY_CHANGE, etc.
            StructField("timestamp", TimestampType(), True),
            StructField("device_type", StringType(), True),  # MOBILE, TV, DESKTOP
            StructField("quality", StringType(), True),     # 480p, 720p, 1080p, 4K
            StructField("region", StringType(), True),      # Mumbai, Delhi, Bangalore, etc.
            StructField("city", StringType(), True),
            StructField("isp", StringType(), True),         # Jio, Airtel, BSNL, etc.
            StructField("bandwidth_mbps", DoubleType(), True),
            StructField("buffer_time_ms", IntegerType(), True),
            StructField("session_id", StringType(), True),
            StructField("user_agent", StringType(), True)
        ])
    
    def setup_kafka_stream(self):
        """
        Kafka से viewer events को read करते हैं
        High-throughput के लिए optimized configuration
        """
        viewer_events = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "hotstar-viewer-events") \
            .option("failOnDataLoss", "false") \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", "10000") \
            .option("kafka.consumer.group.id", "hotstar-analytics") \
            .load()
        
        # Parse JSON data from Kafka
        viewer_data = viewer_events \
            .select(from_json(col("value").cast("string"), 
                            self.create_viewer_events_schema()).alias("data")) \
            .select("data.*") \
            .withWatermark("timestamp", "30 seconds")  # Handle late arriving data
        
        return viewer_data
    
    def calculate_concurrent_viewership(self, viewer_stream):
        """
        Real-time concurrent viewership calculation
        Mumbai local train की तरह - stations पर कितने लोग हैं real-time में
        """
        print("📊 Concurrent viewership tracking शुरू कर रहे हैं...")
        
        # Window-based concurrent viewer count
        concurrent_viewers = viewer_stream \
            .filter(col("event_type").isin(["JOIN", "LEAVE"])) \
            .withColumn("viewer_delta", 
                       when(col("event_type") == "JOIN", 1)
                       .when(col("event_type") == "LEAVE", -1)
                       .otherwise(0)) \
            .groupBy(
                col("match_id"),
                window(col("timestamp"), "1 minute", "10 seconds")  # 1-minute window, 10-second slide
            ) \
            .agg(
                sum("viewer_delta").alias("viewer_change"),
                count("*").alias("total_events"),
                countDistinct("viewer_id").alias("unique_viewers"),
                avg("bandwidth_mbps").alias("avg_bandwidth"),
                avg("buffer_time_ms").alias("avg_buffer_time")
            ) \
            .withColumn("window_start", col("window.start")) \
            .withColumn("window_end", col("window.end")) \
            .drop("window")
        
        # Write concurrent viewership to console for monitoring
        query1 = concurrent_viewers.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="10 seconds") \
            .queryName("concurrent_viewership") \
            .start()
        
        return query1
    
    def analyze_regional_distribution(self, viewer_stream):
        """
        Regional viewership analysis
        India के different regions में कितने viewers हैं
        """
        print("🗺️ Regional distribution analysis शुरू कर रहे हैं...")
        
        regional_stats = viewer_stream \
            .filter(col("event_type") == "JOIN") \
            .groupBy(
                col("match_id"),
                col("region"),
                col("city"),
                window(col("timestamp"), "5 minutes")
            ) \
            .agg(
                countDistinct("viewer_id").alias("unique_viewers"),
                countDistinct("device_type").alias("device_types"),
                mode("quality").alias("popular_quality"),  # Most common quality in region
                avg("bandwidth_mbps").alias("avg_bandwidth"),
                max("bandwidth_mbps").alias("max_bandwidth"),
                min("bandwidth_mbps").alias("min_bandwidth")
            ) \
            .withColumn("window_time", col("window.start")) \
            .drop("window") \
            .orderBy(desc("unique_viewers"))
        
        # Console output for regional analysis
        query2 = regional_stats.writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("numRows", 20) \
            .option("truncate", False) \
            .trigger(processingTime="30 seconds") \
            .queryName("regional_distribution") \
            .start()
        
        return query2
    
    def monitor_quality_metrics(self, viewer_stream):
        """
        Quality metrics monitoring (buffering, quality changes)
        Network quality के हिसाब से viewer experience track करते हैं
        """
        print("📶 Quality metrics monitoring शुरू कर रहे हैं...")
        
        quality_metrics = viewer_stream \
            .groupBy(
                col("match_id"),
                col("quality"),
                col("isp"),
                window(col("timestamp"), "2 minutes")
            ) \
            .agg(
                count("*").alias("total_events"),
                countDistinct("viewer_id").alias("unique_viewers"),
                avg("buffer_time_ms").alias("avg_buffer_time"),
                max("buffer_time_ms").alias("max_buffer_time"),
                stddev("buffer_time_ms").alias("buffer_time_stddev"),
                sum(when(col("buffer_time_ms") > 5000, 1).otherwise(0)).alias("high_buffer_events"),
                avg("bandwidth_mbps").alias("avg_bandwidth")
            ) \
            .withColumn("buffer_ratio", col("high_buffer_events") / col("total_events")) \
            .withColumn("quality_score", 
                       when(col("avg_buffer_time") < 1000, 5.0)
                       .when(col("avg_buffer_time") < 3000, 4.0)
                       .when(col("avg_buffer_time") < 5000, 3.0)
                       .when(col("avg_buffer_time") < 10000, 2.0)
                       .otherwise(1.0)) \
            .filter(col("unique_viewers") > 10)  # Only analyze if sufficient sample size
        
        # Write quality metrics to console
        query3 = quality_metrics.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="20 seconds") \
            .queryName("quality_metrics") \
            .start()
        
        return query3
    
    def detect_peak_traffic_patterns(self, viewer_stream):
        """
        Peak traffic detection during cricket events
        Wickets, boundaries के time पर traffic spike detect करते हैं
        """
        print("🚀 Peak traffic pattern detection शुरू कर रहे हैं...")
        
        # Sliding window to detect sudden spikes
        traffic_patterns = viewer_stream \
            .filter(col("event_type") == "JOIN") \
            .groupBy(
                col("match_id"),
                window(col("timestamp"), "30 seconds", "5 seconds")  # 30-sec window, 5-sec slide
            ) \
            .agg(
                count("*").alias("join_events"),
                countDistinct("viewer_id").alias("new_viewers"),
                countDistinct("city").alias("cities_joining"),
                mode("device_type").alias("popular_device")
            ) \
            .withColumn("window_start", col("window.start")) \
            .drop("window")
        
        # Detect spikes by comparing with previous window
        traffic_with_spikes = traffic_patterns \
            .withColumn("prev_join_events", 
                       lag("join_events", 1).over(
                           Window.partitionBy("match_id").orderBy("window_start"))) \
            .withColumn("spike_ratio", 
                       when(col("prev_join_events") > 0, 
                            col("join_events") / col("prev_join_events"))
                       .otherwise(1.0)) \
            .filter(col("spike_ratio") > 2.0)  # 200% spike threshold
        
        # Alert for significant spikes
        query4 = traffic_with_spikes.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="5 seconds") \
            .queryName("traffic_spikes") \
            .foreachBatch(self.handle_traffic_spike) \
            .start()
        
        return query4
    
    def handle_traffic_spike(self, batch_df, batch_id):
        """
        Traffic spike का handle करते हैं
        Auto-scaling triggers या alerts भेज सकते हैं
        """
        if batch_df.count() > 0:
            print(f"🚨 TRAFFIC SPIKE DETECTED at batch {batch_id}!")
            
            # Get spike details
            spike_details = batch_df.collect()
            for spike in spike_details:
                print(f"Match: {spike.match_id}")
                print(f"New viewers in 30s: {spike.new_viewers}")
                print(f"Spike ratio: {spike.spike_ratio:.2f}x")
                print(f"Cities affected: {spike.cities_joining}")
                print(f"Time: {spike.window_start}")
                print("---")
                
                # यहाँ auto-scaling logic होगी production में
                # trigger_auto_scaling(spike.match_id, spike.spike_ratio)
    
    def analyze_device_distribution(self, viewer_stream):
        """
        Device-wise viewership analysis
        Mobile, TV, Desktop पर कितने users हैं
        """
        print("📱 Device distribution analysis शुरू कर रहे हैं...")
        
        device_stats = viewer_stream \
            .filter(col("event_type") == "JOIN") \
            .groupBy(
                col("match_id"),
                col("device_type"),
                window(col("timestamp"), "3 minutes")
            ) \
            .agg(
                countDistinct("viewer_id").alias("unique_viewers"),
                avg("bandwidth_mbps").alias("avg_bandwidth"),
                mode("quality").alias("popular_quality"),
                count("*").alias("total_joins"),
                approx_count_distinct("city").alias("cities_covered")
            ) \
            .withColumn("window_time", col("window.start")) \
            .drop("window")
        
        query5 = device_stats.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="30 seconds") \
            .queryName("device_distribution") \
            .start()
        
        return query5
    
    def calculate_engagement_metrics(self, viewer_stream):
        """
        User engagement metrics
        Average session duration, retention rate, etc.
        """
        print("💡 Engagement metrics calculation शुरू कर रहे हैं...")
        
        # Session duration calculation
        session_metrics = viewer_stream \
            .filter(col("event_type").isin(["JOIN", "LEAVE"])) \
            .groupBy("session_id", "match_id", "viewer_id") \
            .agg(
                min("timestamp").alias("session_start"),
                max("timestamp").alias("session_end"),
                count("*").alias("events_count")
            ) \
            .withColumn("session_duration_minutes", 
                       (col("session_end").cast("long") - col("session_start").cast("long")) / 60) \
            .filter(col("session_duration_minutes") > 0)  # Valid sessions only
        
        # Aggregate engagement by match
        engagement_summary = session_metrics \
            .groupBy(
                col("match_id"),
                window(col("session_start"), "10 minutes")
            ) \
            .agg(
                count("*").alias("total_sessions"),
                avg("session_duration_minutes").alias("avg_session_duration"),
                max("session_duration_minutes").alias("max_session_duration"),
                sum("session_duration_minutes").alias("total_watch_time")
            ) \
            .withColumn("window_time", col("window.start")) \
            .drop("window")
        
        query6 = engagement_summary.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime="60 seconds") \
            .queryName("engagement_metrics") \
            .start()
        
        return query6
    
    def run_analytics(self):
        """
        सभी analytics को parallel में चलाते हैं
        Multiple streaming queries को simultaneously handle करते हैं
        """
        try:
            # Setup input stream
            viewer_stream = self.setup_kafka_stream()
            
            print("🎯 Starting all analytics streams...")
            
            # Start all streaming analytics
            queries = []
            queries.append(self.calculate_concurrent_viewership(viewer_stream))
            queries.append(self.analyze_regional_distribution(viewer_stream))
            queries.append(self.monitor_quality_metrics(viewer_stream))
            queries.append(self.detect_peak_traffic_patterns(viewer_stream))
            queries.append(self.analyze_device_distribution(viewer_stream))
            queries.append(self.calculate_engagement_metrics(viewer_stream))
            
            print(f"✅ Started {len(queries)} analytics streams successfully!")
            print("📺 Hotstar IPL Analytics चल रहा है... Press Ctrl+C to stop")
            
            # Wait for all queries to finish
            for query in queries:
                query.awaitTermination()
                
        except KeyboardInterrupt:
            print("\n🛑 Analytics को stop कर रहे हैं...")
            for query in queries:
                query.stop()
        except Exception as e:
            print(f"❌ Error in analytics: {str(e)}")
        finally:
            self.spark.stop()
            print("✅ Spark session बंद हो गया")

def create_sample_viewer_data():
    """
    Testing के लिए sample viewer data generate करते हैं
    Production में यह Hotstar के actual events से आएगा
    """
    import random
    import time
    from kafka import KafkaProducer
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    devices = ["MOBILE", "TV", "DESKTOP", "TABLET"]
    qualities = ["480p", "720p", "1080p", "4K"]
    regions = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata"]
    cities = {
        "Mumbai": ["Andheri", "Bandra", "Powai", "Thane"],
        "Delhi": ["CP", "Dwarka", "Gurgaon", "Noida"],
        "Bangalore": ["Koramangala", "HSR", "Whitefield", "Electronic City"],
        "Hyderabad": ["HITEC City", "Gachibowli", "Banjara Hills"],
        "Chennai": ["T. Nagar", "Anna Nagar", "Adyar"],
        "Kolkata": ["Salt Lake", "Park Street", "Howrah"]
    }
    isps = ["Jio", "Airtel", "BSNL", "Vi"]
    events = ["JOIN", "LEAVE", "QUALITY_CHANGE"]
    
    match_id = "MI_vs_CSK_IPL_Final_2024"
    
    print("📡 Generating sample viewer data...")
    
    try:
        for i in range(1000):  # Generate 1000 sample events
            region = random.choice(regions)
            
            sample_event = {
                "viewer_id": f"viewer_{random.randint(1000, 9999)}",
                "match_id": match_id,
                "event_type": random.choice(events),
                "timestamp": datetime.now().isoformat(),
                "device_type": random.choice(devices),
                "quality": random.choice(qualities),
                "region": region,
                "city": random.choice(cities[region]),
                "isp": random.choice(isps),
                "bandwidth_mbps": round(random.uniform(1.0, 100.0), 2),
                "buffer_time_ms": random.randint(0, 10000),
                "session_id": f"session_{random.randint(10000, 99999)}",
                "user_agent": f"HotstarApp/Android_{random.randint(8, 12)}"
            }
            
            producer.send('hotstar-viewer-events', value=sample_event)
            
            if i % 100 == 0:
                print(f"Sent {i} events...")
            
            time.sleep(0.1)  # 100ms delay between events
            
        producer.flush()
        print("✅ Sample data generation complete!")
        
    except Exception as e:
        print(f"❌ Error generating sample data: {str(e)}")
    finally:
        producer.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-data":
        # Generate sample data for testing
        create_sample_viewer_data()
    else:
        # Run analytics
        analytics = HotstarViewershipAnalytics()
        analytics.run_analytics()