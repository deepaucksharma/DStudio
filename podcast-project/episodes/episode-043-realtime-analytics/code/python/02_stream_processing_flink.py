#!/usr/bin/env python3
"""
Stream Processing with Apache Flink (PyFlink)
Episode 43: Real-time Analytics at Scale

Flink के साथ real-time stream processing का implementation
Production-grade windowing और aggregation के साथ।

Use Case: Hotstar में concurrent viewers को real-time track करना
Cricket match के दौरान 400M+ concurrent users होते हैं
"""

from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.window import Tumble, Session, Slide
from pyflink.table.expressions import col, lit
from pyflink.common import WatermarkStrategy, Time
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
import json
from datetime import datetime, timedelta
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HotstarViewerAnalytics:
    """
    Hotstar के लिए real-time viewer analytics
    Cricket World Cup के दौरान peak traffic handle करता है
    """
    
    def __init__(self):
        # Flink environment setup
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
        self.env.set_parallelism(4)  # Production में 100+ parallelism होता है
        
        # Table environment for SQL-like operations
        self.t_env = StreamTableEnvironment.create(self.env)
        
        # Configure checkpointing for fault tolerance
        self.env.enable_checkpointing(5000)  # Checkpoint every 5 seconds
    
    def setup_kafka_source(self):
        """Setup Kafka source for viewer events"""
        
        # Kafka consumer properties
        kafka_props = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'hotstar_analytics',
            'auto.offset.reset': 'latest'
        }
        
        # Define source table in Flink SQL
        source_ddl = """
        CREATE TABLE viewer_events (
            user_id STRING,
            content_id STRING,
            content_type STRING,
            event_type STRING,
            location STRING,
            device_type STRING,
            timestamp_ms BIGINT,
            event_time AS TO_TIMESTAMP(FROM_UNIXTIME(timestamp_ms / 1000)),
            WATERMARK FOR event_time AS event_time - INTERVAL '30' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'hotstar_events',
            'properties.bootstrap.servers' = 'localhost:9092',
            'properties.group.id' = 'hotstar_analytics',
            'format' = 'json'
        )
        """
        
        self.t_env.execute_sql(source_ddl)
    
    def setup_kafka_sink(self):
        """Setup Kafka sink for processed analytics"""
        
        sink_ddl = """
        CREATE TABLE viewer_analytics (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            content_id STRING,
            concurrent_viewers BIGINT,
            total_watch_time BIGINT,
            top_location STRING,
            peak_timestamp TIMESTAMP(3)
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'hotstar_analytics',
            'properties.bootstrap.servers' = 'localhost:9092',
            'format' = 'json'
        )
        """
        
        self.t_env.execute_sql(sink_ddl)
    
    def calculate_concurrent_viewers(self):
        """
        Calculate concurrent viewers using tumbling windows
        हर 30 second में concurrent viewers count करता है
        """
        
        concurrent_viewers_sql = """
        INSERT INTO viewer_analytics
        SELECT 
            window_start,
            window_end,
            content_id,
            COUNT(DISTINCT user_id) as concurrent_viewers,
            SUM(CASE WHEN event_type = 'watch' THEN 30 ELSE 0 END) as total_watch_time,
            MODE(location) as top_location,
            MAX(event_time) as peak_timestamp
        FROM TABLE(
            TUMBLE(TABLE viewer_events, DESCRIPTOR(event_time), INTERVAL '30' SECONDS)
        )
        WHERE event_type IN ('watch', 'start', 'resume')
        GROUP BY window_start, window_end, content_id
        HAVING COUNT(DISTINCT user_id) > 100
        """
        
        return self.t_env.execute_sql(concurrent_viewers_sql)
    
    def detect_trending_content(self):
        """
        Detect trending content using sliding windows
        Last 5 minutes में rapid growth detect करता है
        """
        
        trending_sql = """
        CREATE VIEW trending_content AS
        SELECT 
            content_id,
            content_type,
            window_start,
            window_end,
            COUNT(DISTINCT user_id) as viewer_count,
            COUNT(DISTINCT user_id) / 300.0 as viewers_per_second,
            LAG(COUNT(DISTINCT user_id)) OVER (
                PARTITION BY content_id 
                ORDER BY window_start
            ) as prev_viewer_count
        FROM TABLE(
            HOP(TABLE viewer_events, DESCRIPTOR(event_time), INTERVAL '1' MINUTE, INTERVAL '5' MINUTES)
        )
        WHERE event_type = 'start'
        GROUP BY content_id, content_type, window_start, window_end
        """
        
        self.t_env.execute_sql(trending_sql)
        
        # Identify content with >50% growth
        growth_detection_sql = """
        SELECT 
            content_id,
            viewer_count,
            prev_viewer_count,
            (viewer_count - prev_viewer_count) * 100.0 / prev_viewer_count as growth_percentage,
            window_end
        FROM trending_content
        WHERE prev_viewer_count > 0 
        AND (viewer_count - prev_viewer_count) * 100.0 / prev_viewer_count > 50.0
        ORDER BY growth_percentage DESC
        """
        
        return self.t_env.execute_sql(growth_detection_sql)
    
    def session_analytics(self):
        """
        Session-based analytics using session windows
        User के continuous viewing sessions track करता है
        """
        
        session_sql = """
        CREATE VIEW user_sessions AS
        SELECT 
            user_id,
            content_id,
            session_start(event_time) as session_start,
            session_end(event_time) as session_end,
            COUNT(*) as event_count,
            SUM(CASE WHEN event_type = 'watch' THEN 30 ELSE 0 END) as total_watch_time,
            device_type,
            location
        FROM TABLE(
            SESSION(TABLE viewer_events, DESCRIPTOR(event_time), INTERVAL '10' MINUTES)
        )
        GROUP BY user_id, content_id, device_type, location, 
                 session_start(event_time), session_end(event_time)
        HAVING total_watch_time > 300
        """
        
        self.t_env.execute_sql(session_sql)
    
    def create_sample_data_generator(self):
        """Create sample data for testing"""
        
        sample_data_sql = """
        CREATE TABLE sample_viewer_events (
            user_id STRING,
            content_id STRING,
            content_type STRING,
            event_type STRING,
            location STRING,
            device_type STRING,
            timestamp_ms BIGINT,
            event_time AS TO_TIMESTAMP(FROM_UNIXTIME(timestamp_ms / 1000)),
            WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'datagen',
            'rows-per-second' = '1000',
            'fields.user_id.length' = '10',
            'fields.content_id.length' = '8',
            'fields.content_type.kind' = 'random',
            'fields.content_type.enum' = 'cricket,movie,series,news',
            'fields.event_type.kind' = 'random',
            'fields.event_type.enum' = 'start,watch,pause,resume,stop',
            'fields.location.kind' = 'random',
            'fields.location.enum' = 'Mumbai,Delhi,Bangalore,Chennai,Kolkata,Hyderabad',
            'fields.device_type.kind' = 'random',
            'fields.device_type.enum' = 'mobile,tv,laptop,tablet'
        )
        """
        
        self.t_env.execute_sql(sample_data_sql)
    
    def run_real_time_analytics(self):
        """
        Run complete real-time analytics pipeline
        Production में continuously run होता है
        """
        
        logger.info("शुरू कर रहे हैं Hotstar real-time analytics...")
        
        # Setup sources and sinks
        self.setup_kafka_source()
        self.setup_kafka_sink()
        
        # Create sample data for demo
        self.create_sample_data_generator()
        
        # Start concurrent viewer calculation
        logger.info("Starting concurrent viewer calculation...")
        concurrent_job = self.calculate_concurrent_viewers()
        
        # Start trending content detection
        logger.info("Starting trending content detection...")
        trending_job = self.detect_trending_content()
        
        # Start session analytics
        logger.info("Starting session analytics...")
        self.session_analytics()
        
        # Monitor analytics in real-time
        monitor_sql = """
        SELECT 
            content_id,
            concurrent_viewers,
            total_watch_time,
            top_location,
            window_end
        FROM viewer_analytics
        WHERE concurrent_viewers > 1000
        ORDER BY concurrent_viewers DESC
        """
        
        result = self.t_env.execute_sql(monitor_sql)
        logger.info("Real-time analytics results:")
        
        # Print results (in production, this would go to dashboard)
        with result.collect() as results:
            for result in results:
                print(f"Content: {result[0]}, Viewers: {result[1]:,}, "
                      f"Watch Time: {result[2]}s, Top Location: {result[3]}")

class IPLMatchAnalytics:
    """
    IPL match के लिए specialized real-time analytics
    Match के दौरान ball-by-ball engagement track करता है
    """
    
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.t_env = StreamTableEnvironment.create(self.env)
        
        # IPL specific configuration
        self.env.set_parallelism(8)  # Higher parallelism for IPL traffic
        self.env.enable_checkpointing(1000)  # More frequent checkpointing
    
    def setup_ipl_analytics(self):
        """Setup IPL-specific analytics tables"""
        
        # Ball-by-ball events
        ball_events_ddl = """
        CREATE TABLE ball_events (
            match_id STRING,
            over_number INT,
            ball_number INT,
            batsman STRING,
            bowler STRING,
            runs INT,
            is_wicket BOOLEAN,
            is_boundary BOOLEAN,
            event_time TIMESTAMP(3),
            WATERMARK FOR event_time AS event_time - INTERVAL '2' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'ipl_ball_events',
            'properties.bootstrap.servers' = 'localhost:9092',
            'format' = 'json'
        )
        """
        
        # Viewer engagement events
        engagement_ddl = """
        CREATE TABLE viewer_engagement (
            user_id STRING,
            match_id STRING,
            engagement_type STRING,
            intensity INT,
            device_type STRING,
            event_time TIMESTAMP(3),
            WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'ipl_engagement',
            'properties.bootstrap.servers' = 'localhost:9092',
            'format' = 'json'
        )
        """
        
        self.t_env.execute_sql(ball_events_ddl)
        self.t_env.execute_sql(engagement_ddl)
    
    def real_time_engagement_spikes(self):
        """
        Detect engagement spikes during exciting moments
        Wicket, boundary के time पर viewer engagement spike होता है
        """
        
        spike_detection_sql = """
        SELECT 
            b.match_id,
            b.over_number,
            b.ball_number,
            b.runs,
            b.is_wicket,
            b.is_boundary,
            COUNT(DISTINCT e.user_id) as engaged_viewers,
            AVG(e.intensity) as avg_intensity,
            b.event_time
        FROM ball_events b
        LEFT JOIN viewer_engagement e
        ON b.match_id = e.match_id
        AND e.event_time BETWEEN b.event_time - INTERVAL '10' SECOND 
                               AND b.event_time + INTERVAL '30' SECOND
        WHERE b.is_wicket = true OR b.is_boundary = true OR b.runs >= 4
        GROUP BY b.match_id, b.over_number, b.ball_number, b.runs, 
                 b.is_wicket, b.is_boundary, b.event_time
        HAVING COUNT(DISTINCT e.user_id) > 10000
        ORDER BY engaged_viewers DESC
        """
        
        return self.t_env.execute_sql(spike_detection_sql)

def run_hotstar_demo():
    """Run Hotstar analytics demo"""
    analytics = HotstarViewerAnalytics()
    analytics.run_real_time_analytics()

def run_ipl_demo():
    """Run IPL analytics demo"""
    ipl_analytics = IPLMatchAnalytics()
    ipl_analytics.setup_ipl_analytics()
    result = ipl_analytics.real_time_engagement_spikes()
    
    logger.info("IPL engagement spikes detected:")
    with result.collect() as results:
        for result in results:
            print(f"Over {result[1]}.{result[2]}: {result[3]} runs, "
                  f"Engaged viewers: {result[7]:,}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "ipl":
        run_ipl_demo()
    else:
        run_hotstar_demo()