#!/usr/bin/env python3
"""
Time-Series Database System with IST - Episode 50: System Design Interview Mastery
Ola Cab Ride Metrics Time-Series Database

Time-series database जैसे Mumbai local train का schedule record है।
हर minute का data store करके trends और patterns identify करते हैं।

Author: Hindi Podcast Series
Topic: Time-Series Database with Indian Standard Time (IST) Context
"""

import time
import threading
import random
import bisect
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import sqlite3
from datetime import datetime, timezone, timedelta
import pytz
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import math

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Indian Standard Time timezone
IST = pytz.timezone('Asia/Kolkata')

class AggregationType(Enum):
    """Time-series aggregation types"""
    SUM = "sum"                    # Total sum
    AVG = "average"               # Average value
    MIN = "minimum"               # Minimum value
    MAX = "maximum"               # Maximum value
    COUNT = "count"               # Count of data points
    LAST = "last"                 # Last value
    FIRST = "first"               # First value
    STDDEV = "standard_deviation" # Standard deviation
    PERCENTILE_95 = "p95"         # 95th percentile
    PERCENTILE_99 = "p99"         # 99th percentile

class RetentionPolicy(Enum):
    """Data retention policies"""
    RAW_1DAY = "raw_1day"         # Raw data for 1 day
    MIN_1WEEK = "1min_1week"      # 1-minute aggregates for 1 week
    HOUR_1MONTH = "1hour_1month"  # 1-hour aggregates for 1 month
    DAY_1YEAR = "1day_1year"      # Daily aggregates for 1 year

@dataclass
class TimeSeriesPoint:
    """Single time-series data point"""
    timestamp: float
    value: Union[float, int]
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_ist_datetime(self) -> datetime:
        """Convert timestamp to IST datetime"""
        utc_dt = datetime.fromtimestamp(self.timestamp, tz=timezone.utc)
        return utc_dt.astimezone(IST)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'value': self.value,
            'tags': self.tags,
            'ist_time': self.to_ist_datetime().isoformat()
        }

@dataclass
class TimeSeriesQuery:
    """Time-series query parameters"""
    metric_name: str
    start_time: float
    end_time: float
    aggregation: AggregationType = AggregationType.AVG
    interval: int = 300  # 5 minutes default
    tags: Dict[str, str] = field(default_factory=dict)
    downsample: bool = True

class TimeSeriesBucket:
    """Time-series data bucket for a specific time range"""
    
    def __init__(self, start_time: float, bucket_size: int):
        """Initialize time bucket"""
        self.start_time = start_time
        self.bucket_size = bucket_size  # Size in seconds
        self.end_time = start_time + bucket_size
        self.points: List[TimeSeriesPoint] = []
        self.lock = threading.Lock()
    
    def add_point(self, point: TimeSeriesPoint) -> bool:
        """Add point to bucket if it belongs to this time range"""
        if self.start_time <= point.timestamp < self.end_time:
            with self.lock:
                # Insert in sorted order
                bisect.insort(self.points, point, key=lambda p: p.timestamp)
                return True
        return False
    
    def aggregate(self, aggregation: AggregationType) -> Optional[TimeSeriesPoint]:
        """Aggregate all points in bucket"""
        with self.lock:
            if not self.points:
                return None
            
            values = [p.value for p in self.points]
            bucket_timestamp = self.start_time + (self.bucket_size / 2)
            
            if aggregation == AggregationType.SUM:
                agg_value = sum(values)
            elif aggregation == AggregationType.AVG:
                agg_value = sum(values) / len(values)
            elif aggregation == AggregationType.MIN:
                agg_value = min(values)
            elif aggregation == AggregationType.MAX:
                agg_value = max(values)
            elif aggregation == AggregationType.COUNT:
                agg_value = len(values)
            elif aggregation == AggregationType.LAST:
                agg_value = values[-1]
            elif aggregation == AggregationType.FIRST:
                agg_value = values[0]
            elif aggregation == AggregationType.STDDEV:
                if len(values) > 1:
                    mean = sum(values) / len(values)
                    variance = sum((v - mean) ** 2 for v in values) / len(values)
                    agg_value = math.sqrt(variance)
                else:
                    agg_value = 0.0
            elif aggregation == AggregationType.PERCENTILE_95:
                agg_value = np.percentile(values, 95)
            elif aggregation == AggregationType.PERCENTILE_99:
                agg_value = np.percentile(values, 99)
            else:
                agg_value = sum(values) / len(values)  # Default to average
            
            # Merge tags from all points
            merged_tags = {}
            for point in self.points:
                merged_tags.update(point.tags)
            
            return TimeSeriesPoint(
                timestamp=bucket_timestamp,
                value=agg_value,
                tags=merged_tags
            )

class TimeSeriesMetric:
    """Time-series metric storage and management"""
    
    def __init__(self, name: str, bucket_size: int = 300):  # 5 minute buckets
        """Initialize time-series metric"""
        self.name = name
        self.bucket_size = bucket_size
        self.buckets: Dict[int, TimeSeriesBucket] = {}
        self.lock = threading.RLock()
        self.total_points = 0
        
        # Retention settings
        self.retention_seconds = 24 * 3600  # 24 hours default
        self.last_cleanup = time.time()
    
    def _get_bucket_key(self, timestamp: float) -> int:
        """Get bucket key for timestamp"""
        return int(timestamp // self.bucket_size)
    
    def _get_or_create_bucket(self, timestamp: float) -> TimeSeriesBucket:
        """Get or create bucket for timestamp"""
        bucket_key = self._get_bucket_key(timestamp)
        
        if bucket_key not in self.buckets:
            bucket_start = bucket_key * self.bucket_size
            self.buckets[bucket_key] = TimeSeriesBucket(bucket_start, self.bucket_size)
        
        return self.buckets[bucket_key]
    
    def add_point(self, point: TimeSeriesPoint):
        """Add data point to metric"""
        with self.lock:
            bucket = self._get_or_create_bucket(point.timestamp)
            if bucket.add_point(point):
                self.total_points += 1
    
    def query(self, start_time: float, end_time: float, 
             aggregation: AggregationType = AggregationType.AVG,
             interval: int = None) -> List[TimeSeriesPoint]:
        """Query metric data for time range"""
        
        if interval is None:
            interval = self.bucket_size
        
        results = []
        current_time = start_time
        
        with self.lock:
            while current_time < end_time:
                window_end = min(current_time + interval, end_time)
                
                # Find all buckets that overlap with this window
                window_points = []
                start_bucket = self._get_bucket_key(current_time)
                end_bucket = self._get_bucket_key(window_end)
                
                for bucket_key in range(start_bucket, end_bucket + 1):
                    if bucket_key in self.buckets:
                        bucket = self.buckets[bucket_key]
                        with bucket.lock:
                            for point in bucket.points:
                                if current_time <= point.timestamp < window_end:
                                    window_points.append(point)
                
                # Aggregate points in this window
                if window_points:
                    values = [p.value for p in window_points]
                    window_timestamp = current_time + (interval / 2)
                    
                    if aggregation == AggregationType.SUM:
                        agg_value = sum(values)
                    elif aggregation == AggregationType.AVG:
                        agg_value = sum(values) / len(values)
                    elif aggregation == AggregationType.MIN:
                        agg_value = min(values)
                    elif aggregation == AggregationType.MAX:
                        agg_value = max(values)
                    elif aggregation == AggregationType.COUNT:
                        agg_value = len(values)
                    else:
                        agg_value = sum(values) / len(values)
                    
                    results.append(TimeSeriesPoint(
                        timestamp=window_timestamp,
                        value=agg_value,
                        tags={'aggregation': aggregation.value, 'interval': str(interval)}
                    ))
                
                current_time += interval
        
        return results
    
    def cleanup_old_data(self, retention_seconds: int = None):
        """Remove old data beyond retention period"""
        if retention_seconds is None:
            retention_seconds = self.retention_seconds
        
        cutoff_time = time.time() - retention_seconds
        cutoff_bucket = self._get_bucket_key(cutoff_time)
        
        with self.lock:
            old_buckets = [k for k in self.buckets.keys() if k < cutoff_bucket]
            
            removed_points = 0
            for bucket_key in old_buckets:
                bucket = self.buckets.pop(bucket_key)
                removed_points += len(bucket.points)
            
            self.total_points -= removed_points
            
            if removed_points > 0:
                logger.debug(f"Cleaned up {removed_points} old points from {self.name}")
    
    def get_stats(self) -> Dict:
        """Get metric statistics"""
        with self.lock:
            return {
                'name': self.name,
                'total_points': self.total_points,
                'total_buckets': len(self.buckets),
                'bucket_size': self.bucket_size,
                'retention_seconds': self.retention_seconds,
                'oldest_timestamp': min(self.buckets.keys()) * self.bucket_size if self.buckets else None,
                'newest_timestamp': max(self.buckets.keys()) * self.bucket_size if self.buckets else None
            }

class TimeSeriesDatabase:
    """Time-Series Database - Ola Cab Metrics System"""
    
    def __init__(self, name: str = "ola_metrics_tsdb"):
        """Initialize time-series database"""
        self.name = name
        self.metrics: Dict[str, TimeSeriesMetric] = {}
        self.lock = threading.RLock()
        self.stats = {
            'points_written': 0,
            'queries_executed': 0,
            'cleanup_runs': 0
        }
        
        # Background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.running = True
        self.cleanup_thread.start()
        
        logger.info(f"📊 Time-Series Database '{name}' initialized")
    
    def write_point(self, metric_name: str, timestamp: float, value: Union[float, int],
                   tags: Dict[str, str] = None):
        """Write single data point"""
        if tags is None:
            tags = {}
        
        point = TimeSeriesPoint(timestamp=timestamp, value=value, tags=tags)
        
        with self.lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = TimeSeriesMetric(metric_name)
            
            self.metrics[metric_name].add_point(point)
            self.stats['points_written'] += 1
    
    def write_points_batch(self, points: List[Dict]):
        """Write multiple data points in batch"""
        for point_data in points:
            self.write_point(
                metric_name=point_data['metric'],
                timestamp=point_data['timestamp'],
                value=point_data['value'],
                tags=point_data.get('tags', {})
            )
    
    def query_metric(self, query: TimeSeriesQuery) -> List[TimeSeriesPoint]:
        """Query metric data"""
        with self.lock:
            if query.metric_name not in self.metrics:
                return []
            
            metric = self.metrics[query.metric_name]
            results = metric.query(
                start_time=query.start_time,
                end_time=query.end_time,
                aggregation=query.aggregation,
                interval=query.interval
            )
            
            self.stats['queries_executed'] += 1
            return results
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while self.running:
            try:
                time.sleep(300)  # Run every 5 minutes
                
                with self.lock:
                    for metric in self.metrics.values():
                        metric.cleanup_old_data()
                
                self.stats['cleanup_runs'] += 1
                
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.lock:
            metric_stats = {}
            total_points = 0
            total_buckets = 0
            
            for metric_name, metric in self.metrics.items():
                stats = metric.get_stats()
                metric_stats[metric_name] = stats
                total_points += stats['total_points']
                total_buckets += stats['total_buckets']
            
            return {
                'database_name': self.name,
                'total_metrics': len(self.metrics),
                'total_points': total_points,
                'total_buckets': total_buckets,
                'database_stats': self.stats,
                'metric_stats': metric_stats
            }
    
    def shutdown(self):
        """Shutdown database"""
        self.running = False
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        logger.info(f"📊 Time-Series Database '{self.name}' shutdown")

class OlaCabMetricsSystem:
    """Ola Cab Ride Metrics Collection and Analysis System"""
    
    def __init__(self):
        """Initialize Ola metrics system"""
        self.tsdb = TimeSeriesDatabase("ola_cab_metrics")
        
        # Indian cities with Ola service
        self.cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 
            'Kolkata', 'Pune', 'Ahmedabad', 'Surat', 'Jaipur',
            'Lucknow', 'Kochi', 'Indore', 'Bhopal', 'Coimbatore'
        ]
        
        # Cab types available
        self.cab_types = ['Micro', 'Mini', 'Prime', 'Auto', 'Share']
        
        # Metric definitions
        self.metrics = {
            'ride_requests': 'Total ride requests per minute',
            'ride_completions': 'Completed rides per minute',
            'driver_earnings': 'Driver earnings in INR',
            'wait_time_seconds': 'Average wait time in seconds',
            'ride_distance_km': 'Ride distance in kilometers',
            'surge_multiplier': 'Dynamic pricing surge multiplier',
            'active_drivers': 'Number of active drivers',
            'customer_rating': 'Average customer rating (1-5)',
            'cancellation_rate': 'Ride cancellation rate percentage'
        }
        
        # Data generation thread
        self.data_generation_thread = None
        self.generating_data = False
        
        print("🚗 Ola Cab Metrics System initialized")
        print(f"   Cities: {len(self.cities)}")
        print(f"   Cab Types: {self.cab_types}")
        print(f"   Metrics: {len(self.metrics)}")
    
    def _generate_realistic_metric_value(self, metric_name: str, 
                                       city: str, cab_type: str, 
                                       ist_hour: int) -> float:
        """Generate realistic metric values based on Indian patterns"""
        
        # Peak hours in Indian cities: 8-10 AM and 7-9 PM
        is_peak_morning = 8 <= ist_hour <= 10
        is_peak_evening = 19 <= ist_hour <= 21
        is_peak = is_peak_morning or is_peak_evening
        
        # Weekend vs weekday (simplified - assume random)
        is_weekend = random.choice([True, False])
        
        # City size factor (larger cities have more rides)
        city_factor = {
            'Mumbai': 3.0, 'Delhi': 2.8, 'Bangalore': 2.5, 'Hyderabad': 2.0,
            'Chennai': 1.8, 'Kolkata': 1.6, 'Pune': 1.5
        }.get(city, 1.0)
        
        # Cab type factor
        cab_factor = {
            'Micro': 0.7, 'Mini': 1.0, 'Prime': 0.4, 'Auto': 1.2, 'Share': 0.6
        }.get(cab_type, 1.0)
        
        base_values = {
            'ride_requests': 50 * city_factor * cab_factor,
            'ride_completions': 40 * city_factor * cab_factor,
            'driver_earnings': 200 * city_factor,
            'wait_time_seconds': 180,  # 3 minutes base
            'ride_distance_km': 8.5,
            'surge_multiplier': 1.0,
            'active_drivers': 100 * city_factor,
            'customer_rating': 4.2,
            'cancellation_rate': 12.0  # 12% base
        }
        
        base_value = base_values.get(metric_name, 1.0)
        
        # Apply peak hour multipliers
        if is_peak:
            peak_multipliers = {
                'ride_requests': 2.5,
                'ride_completions': 2.2,
                'wait_time_seconds': 1.8,
                'surge_multiplier': 2.0,
                'cancellation_rate': 1.4
            }
            base_value *= peak_multipliers.get(metric_name, 1.2)
        
        # Add weekend variations
        if is_weekend:
            weekend_multipliers = {
                'ride_requests': 1.3,
                'driver_earnings': 1.4,
                'ride_distance_km': 1.2
            }
            base_value *= weekend_multipliers.get(metric_name, 1.0)
        
        # Add random variation (±20%)
        variation = random.uniform(0.8, 1.2)
        final_value = base_value * variation
        
        # Apply metric-specific constraints
        if metric_name == 'customer_rating':
            final_value = max(3.0, min(5.0, final_value))
        elif metric_name == 'surge_multiplier':
            final_value = max(1.0, min(5.0, final_value))
        elif metric_name == 'cancellation_rate':
            final_value = max(0.0, min(50.0, final_value))
        elif metric_name in ['ride_requests', 'ride_completions', 'active_drivers']:
            final_value = max(0, int(final_value))
        
        return final_value
    
    def start_data_generation(self, duration_minutes: int = 60, 
                            interval_seconds: int = 10):
        """Start generating simulated Ola metrics data"""
        if self.generating_data:
            logger.warning("Data generation already running")
            return
        
        def generate_data():
            """Data generation loop"""
            self.generating_data = True
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            logger.info(f"🚀 Starting Ola metrics data generation for {duration_minutes} minutes")
            
            while time.time() < end_time and self.generating_data:
                current_time = time.time()
                ist_datetime = datetime.fromtimestamp(current_time, tz=IST)
                ist_hour = ist_datetime.hour
                
                # Generate metrics for all combinations
                points_batch = []
                
                for city in self.cities:
                    for cab_type in self.cab_types:
                        for metric_name in self.metrics.keys():
                            value = self._generate_realistic_metric_value(
                                metric_name, city, cab_type, ist_hour
                            )
                            
                            points_batch.append({
                                'metric': metric_name,
                                'timestamp': current_time,
                                'value': value,
                                'tags': {
                                    'city': city,
                                    'cab_type': cab_type,
                                    'hour': str(ist_hour),
                                    'timezone': 'IST'
                                }
                            })
                
                # Write batch to database
                self.tsdb.write_points_batch(points_batch)
                
                if int(time.time()) % 60 == 0:  # Log every minute
                    logger.info(f"Generated {len(points_batch)} metrics points at {ist_datetime.strftime('%H:%M:%S IST')}")
                
                time.sleep(interval_seconds)
            
            self.generating_data = False
            logger.info("✅ Ola metrics data generation completed")
        
        self.data_generation_thread = threading.Thread(target=generate_data, daemon=True)
        self.data_generation_thread.start()
    
    def stop_data_generation(self):
        """Stop data generation"""
        self.generating_data = False
        if self.data_generation_thread:
            self.data_generation_thread.join(timeout=5)
    
    def analyze_peak_hours(self, city: str, metric: str, 
                          hours_back: int = 24) -> Dict:
        """Analyze peak hours for a specific city and metric"""
        
        end_time = time.time()
        start_time = end_time - (hours_back * 3600)
        
        query = TimeSeriesQuery(
            metric_name=metric,
            start_time=start_time,
            end_time=end_time,
            aggregation=AggregationType.AVG,
            interval=3600  # 1 hour intervals
        )
        
        results = self.tsdb.query_metric(query)
        
        # Filter for specific city
        city_results = []
        for point in results:
            if point.tags.get('city') == city:
                city_results.append(point)
        
        if not city_results:
            return {'error': f'No data found for {city}'}
        
        # Analyze hourly patterns
        hourly_avg = defaultdict(list)
        
        for point in city_results:
            ist_dt = point.to_ist_datetime()
            hour = ist_dt.hour
            hourly_avg[hour].append(point.value)
        
        # Calculate average for each hour
        hourly_analysis = {}
        for hour, values in hourly_avg.items():
            hourly_analysis[hour] = {
                'average': sum(values) / len(values),
                'count': len(values),
                'min': min(values),
                'max': max(values)
            }
        
        # Find peak hours
        peak_hours = sorted(hourly_analysis.keys(), 
                          key=lambda h: hourly_analysis[h]['average'], 
                          reverse=True)[:3]
        
        return {
            'city': city,
            'metric': metric,
            'analysis_period_hours': hours_back,
            'peak_hours': peak_hours,
            'hourly_analysis': hourly_analysis,
            'insights': {
                'highest_avg_hour': peak_hours[0] if peak_hours else None,
                'lowest_avg_hour': min(hourly_analysis.keys(), 
                                     key=lambda h: hourly_analysis[h]['average']) if hourly_analysis else None
            }
        }
    
    def get_city_comparison(self, metric: str, hours_back: int = 6) -> Dict:
        """Compare metric across different cities"""
        
        end_time = time.time()
        start_time = end_time - (hours_back * 3600)
        
        query = TimeSeriesQuery(
            metric_name=metric,
            start_time=start_time,
            end_time=end_time,
            aggregation=AggregationType.AVG,
            interval=1800  # 30 minute intervals
        )
        
        results = self.tsdb.query_metric(query)
        
        # Group by city
        city_data = defaultdict(list)
        
        for point in results:
            city = point.tags.get('city', 'Unknown')
            city_data[city].append(point.value)
        
        # Calculate city statistics
        city_comparison = {}
        
        for city, values in city_data.items():
            if values:
                city_comparison[city] = {
                    'average': sum(values) / len(values),
                    'total_points': len(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': values[-1] if values else None
                }
        
        # Rank cities
        ranked_cities = sorted(city_comparison.keys(), 
                             key=lambda c: city_comparison[c]['average'], 
                             reverse=True)
        
        return {
            'metric': metric,
            'analysis_period_hours': hours_back,
            'city_comparison': city_comparison,
            'city_ranking': ranked_cities,
            'top_performing_city': ranked_cities[0] if ranked_cities else None
        }
    
    def get_surge_pricing_analysis(self, hours_back: int = 12) -> Dict:
        """Analyze surge pricing patterns"""
        
        end_time = time.time()
        start_time = end_time - (hours_back * 3600)
        
        query = TimeSeriesQuery(
            metric_name='surge_multiplier',
            start_time=start_time,
            end_time=end_time,
            aggregation=AggregationType.MAX,  # Use MAX for surge analysis
            interval=600  # 10 minute intervals
        )
        
        results = self.tsdb.query_metric(query)
        
        # Analyze surge patterns
        surge_analysis = {
            'high_surge_periods': [],
            'city_surge_stats': defaultdict(list),
            'cab_type_surge_stats': defaultdict(list)
        }
        
        for point in results:
            ist_dt = point.to_ist_datetime()
            city = point.tags.get('city', 'Unknown')
            cab_type = point.tags.get('cab_type', 'Unknown')
            
            surge_analysis['city_surge_stats'][city].append(point.value)
            surge_analysis['cab_type_surge_stats'][cab_type].append(point.value)
            
            # Flag high surge periods (>2.0x)
            if point.value > 2.0:
                surge_analysis['high_surge_periods'].append({
                    'timestamp': point.timestamp,
                    'ist_time': ist_dt.strftime('%Y-%m-%d %H:%M:%S IST'),
                    'surge_multiplier': point.value,
                    'city': city,
                    'cab_type': cab_type
                })
        
        # Calculate summary statistics
        city_surge_summary = {}
        for city, surge_values in surge_analysis['city_surge_stats'].items():
            if surge_values:
                city_surge_summary[city] = {
                    'avg_surge': sum(surge_values) / len(surge_values),
                    'max_surge': max(surge_values),
                    'high_surge_count': len([s for s in surge_values if s > 2.0])
                }
        
        return {
            'analysis_period_hours': hours_back,
            'high_surge_periods_count': len(surge_analysis['high_surge_periods']),
            'city_surge_summary': city_surge_summary,
            'highest_surge_city': max(city_surge_summary.keys(), 
                                    key=lambda c: city_surge_summary[c]['max_surge']) if city_surge_summary else None
        }
    
    def get_system_health(self) -> Dict:
        """Get overall system health metrics"""
        db_stats = self.tsdb.get_database_stats()
        
        # Calculate health indicators
        total_points = db_stats['total_points']
        total_metrics = db_stats['total_metrics']
        expected_metrics = len(self.metrics) * len(self.cities) * len(self.cab_types)
        
        health_score = min(100, (total_metrics / expected_metrics) * 100) if expected_metrics > 0 else 0
        
        return {
            'system_status': 'healthy' if health_score > 80 else 'degraded',
            'health_score': health_score,
            'data_generation_active': self.generating_data,
            'database_stats': db_stats,
            'coverage': {
                'cities_covered': len(self.cities),
                'cab_types_covered': len(self.cab_types), 
                'metrics_tracked': len(self.metrics)
            }
        }
    
    def shutdown(self):
        """Shutdown metrics system"""
        self.stop_data_generation()
        self.tsdb.shutdown()
        logger.info("🚗 Ola Cab Metrics System shutdown")

def demonstrate_basic_timeseries_operations():
    """Demonstrate basic time-series operations"""
    print("📊 Basic Time-Series Operations Demo - IST Timezone Handling")
    print("=" * 65)
    
    # Create time-series database
    tsdb = TimeSeriesDatabase("demo_tsdb")
    
    print(f"\n📈 Writing sample metrics with IST timestamps:")
    print("-" * 50)
    
    # Generate sample data over last hour
    current_time = time.time()
    start_time = current_time - 3600  # 1 hour ago
    
    sample_metrics = ['api_requests', 'response_time_ms', 'error_rate']
    
    points_written = 0
    for i in range(60):  # 60 data points (1 per minute)
        timestamp = start_time + (i * 60)
        ist_dt = datetime.fromtimestamp(timestamp, tz=IST)
        
        for metric in sample_metrics:
            if metric == 'api_requests':
                value = random.randint(50, 200)
            elif metric == 'response_time_ms':
                value = random.uniform(100, 800)
            else:  # error_rate
                value = random.uniform(0.1, 5.0)
            
            tsdb.write_point(
                metric_name=metric,
                timestamp=timestamp,
                value=value,
                tags={'service': 'api_gateway', 'region': 'mumbai'}
            )
            points_written += 1
    
    print(f"   ✅ Written {points_written} data points")
    
    # Query data
    print(f"\n🔍 Querying metrics data:")
    print("-" * 30)
    
    for metric in sample_metrics:
        query = TimeSeriesQuery(
            metric_name=metric,
            start_time=start_time,
            end_time=current_time,
            aggregation=AggregationType.AVG,
            interval=600  # 10 minute intervals
        )
        
        results = tsdb.query_metric(query)
        
        if results:
            latest_point = results[-1]
            ist_time = latest_point.to_ist_datetime()
            
            print(f"   {metric}:")
            print(f"     Data points: {len(results)}")
            print(f"     Latest value: {latest_point.value:.2f}")
            print(f"     Latest IST time: {ist_time.strftime('%H:%M:%S IST')}")
    
    # Show database stats
    stats = tsdb.get_database_stats()
    print(f"\n📊 Database Statistics:")
    print(f"   Total metrics: {stats['total_metrics']}")
    print(f"   Total points: {stats['total_points']}")
    print(f"   Total buckets: {stats['total_buckets']}")
    
    tsdb.shutdown()

def demonstrate_ola_metrics_system():
    """Demonstrate Ola cab metrics system"""
    print("\n🚗 Ola Cab Metrics System Demo - Real-time Ride Analytics")
    print("=" * 65)
    
    # Initialize Ola metrics system
    ola_system = OlaCabMetricsSystem()
    
    print(f"\n⚡ Starting real-time data generation (2 minutes)...")
    print("-" * 50)
    
    # Start data generation
    ola_system.start_data_generation(duration_minutes=2, interval_seconds=5)
    
    # Wait a bit for data to accumulate
    time.sleep(30)
    
    # Get system health
    health = ola_system.get_system_health()
    print(f"   System Health: {health['system_status'].upper()}")
    print(f"   Health Score: {health['health_score']:.1f}%")
    print(f"   Total Data Points: {health['database_stats']['total_points']}")
    
    # Wait for more data
    time.sleep(60)
    
    # Analyze peak hours for Mumbai
    print(f"\n📈 Peak Hours Analysis - Mumbai Ride Requests:")
    print("-" * 50)
    
    peak_analysis = ola_system.analyze_peak_hours('Mumbai', 'ride_requests', hours_back=2)
    
    if 'error' not in peak_analysis:
        peak_hours = peak_analysis.get('peak_hours', [])
        print(f"   Peak hours: {[f'{h}:00' for h in peak_hours[:3]]}")
        
        insights = peak_analysis.get('insights', {})
        if insights.get('highest_avg_hour') is not None:
            highest_hour = insights['highest_avg_hour']
            print(f"   Highest activity: {highest_hour}:00 IST")
    
    # City comparison
    print(f"\n🏙️ City Comparison - Average Wait Times:")
    print("-" * 45)
    
    city_comparison = ola_system.get_city_comparison('wait_time_seconds', hours_back=1)
    
    comparison_data = city_comparison.get('city_comparison', {})
    top_cities = list(city_comparison.get('city_ranking', []))[:5]
    
    for i, city in enumerate(top_cities, 1):
        if city in comparison_data:
            avg_wait = comparison_data[city]['average']
            print(f"   {i}. {city:<12}: {avg_wait:.1f} seconds avg wait")
    
    # Surge pricing analysis
    print(f"\n💰 Surge Pricing Analysis:")
    print("-" * 30)
    
    surge_analysis = ola_system.get_surge_pricing_analysis(hours_back=1)
    
    high_surge_count = surge_analysis.get('high_surge_periods_count', 0)
    highest_surge_city = surge_analysis.get('highest_surge_city', 'Unknown')
    
    print(f"   High surge periods: {high_surge_count}")
    print(f"   Highest surge city: {highest_surge_city}")
    
    city_surge = surge_analysis.get('city_surge_summary', {})
    if city_surge:
        print(f"   Top surge cities:")
        top_surge_cities = sorted(city_surge.keys(), 
                                key=lambda c: city_surge[c]['max_surge'], 
                                reverse=True)[:3]
        
        for i, city in enumerate(top_surge_cities, 1):
            max_surge = city_surge[city]['max_surge']
            avg_surge = city_surge[city]['avg_surge']
            print(f"     {i}. {city}: {max_surge:.1f}x max, {avg_surge:.1f}x avg")
    
    # Wait for data generation to complete
    time.sleep(30)
    
    # Final system statistics
    final_health = ola_system.get_system_health()
    final_stats = final_health['database_stats']
    
    print(f"\n📊 Final System Statistics:")
    print("-" * 30)
    print(f"   Total Data Points: {final_stats['total_points']:,}")
    print(f"   Total Metrics: {final_stats['total_metrics']}")
    print(f"   Queries Executed: {final_stats['database_stats']['queries_executed']}")
    print(f"   Data Generation: {'Active' if ola_system.generating_data else 'Completed'}")
    
    # Stop system
    ola_system.stop_data_generation()
    ola_system.shutdown()
    
    return ola_system

def demonstrate_ist_timezone_handling():
    """Demonstrate IST timezone handling in time-series data"""
    print("\n🌏 IST Timezone Handling Demo - Indian Standard Time")
    print("=" * 60)
    
    tsdb = TimeSeriesDatabase("ist_timezone_demo")
    
    print(f"\n🕒 Current IST Time Comparison:")
    print("-" * 35)
    
    current_utc = datetime.now(timezone.utc)
    current_ist = current_utc.astimezone(IST)
    
    print(f"   UTC Time: {current_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   IST Time: {current_ist.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"   IST Offset: {current_ist.strftime('%z')} ({current_ist.tzinfo})")
    
    # Generate data across different IST hours
    print(f"\n📊 Generating data across IST business hours:")
    print("-" * 50)
    
    # Simulate data for different IST hours
    base_timestamp = time.time() - 43200  # 12 hours ago
    
    business_hours_data = []
    
    for hour_offset in range(12):  # 12 hours of data
        timestamp = base_timestamp + (hour_offset * 3600)  # Each hour
        utc_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        ist_dt = utc_dt.astimezone(IST)
        
        # Simulate business activity patterns
        ist_hour = ist_dt.hour
        
        if 9 <= ist_hour <= 18:  # Business hours
            activity_level = random.uniform(80, 100)
        elif 6 <= ist_hour <= 8 or 19 <= ist_hour <= 22:  # Peak hours
            activity_level = random.uniform(60, 90)
        else:  # Off hours
            activity_level = random.uniform(10, 40)
        
        tsdb.write_point(
            metric_name='business_activity',
            timestamp=timestamp,
            value=activity_level,
            tags={
                'timezone': 'IST',
                'ist_hour': str(ist_hour),
                'utc_time': utc_dt.isoformat(),
                'ist_time': ist_dt.isoformat()
            }
        )
        
        business_hours_data.append({
            'ist_hour': ist_hour,
            'activity': activity_level,
            'ist_time': ist_dt.strftime('%H:%M IST')
        })
    
    print(f"   ✅ Generated business activity data for 12 hours")
    
    # Query and show IST patterns
    print(f"\n📈 Business Activity by IST Hour:")
    print("-" * 35)
    
    query = TimeSeriesQuery(
        metric_name='business_activity',
        start_time=base_timestamp,
        end_time=time.time(),
        aggregation=AggregationType.AVG,
        interval=3600  # 1 hour intervals
    )
    
    results = tsdb.query_metric(query)
    
    for point in results:
        ist_dt = point.to_ist_datetime()
        ist_hour = ist_dt.hour
        activity = point.value
        
        # Categorize hour
        if 9 <= ist_hour <= 18:
            category = "Business"
        elif 6 <= ist_hour <= 8 or 19 <= ist_hour <= 22:
            category = "Peak"
        else:
            category = "Off"
        
        print(f"   {ist_hour:2d}:00 IST: {activity:5.1f}% activity ({category} hours)")
    
    # Show timezone conversion examples
    print(f"\n🔄 Timezone Conversion Examples:")
    print("-" * 35)
    
    example_timestamps = [
        time.time() - 3600,  # 1 hour ago
        time.time(),         # Now
        time.time() + 3600   # 1 hour from now
    ]
    
    for i, ts in enumerate(example_timestamps, 1):
        utc_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        ist_dt = utc_dt.astimezone(IST)
        
        point = TimeSeriesPoint(timestamp=ts, value=100.0)
        converted_ist = point.to_ist_datetime()
        
        print(f"   Example {i}:")
        print(f"     UTC: {utc_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"     IST: {converted_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"     Offset: +05:30 from UTC")
    
    tsdb.shutdown()

def demonstrate_performance_analysis():
    """Demonstrate time-series performance analysis"""
    print("\n⚡ Performance Analysis Demo - High-Volume Metrics")
    print("=" * 55)
    
    tsdb = TimeSeriesDatabase("performance_test_tsdb")
    
    print(f"\n🚀 Performance Test - Writing 10,000 data points:")
    print("-" * 55)
    
    # Performance test - write many points quickly
    start_time = time.time()
    points_to_write = 10000
    
    # Generate high-volume data
    current_ts = time.time()
    
    for i in range(points_to_write):
        # Vary the timestamp slightly for each point
        point_ts = current_ts - (points_to_write - i) * 10  # 10 seconds apart
        
        # Multiple metrics per timestamp
        metrics_data = [
            ('cpu_utilization', random.uniform(10, 90)),
            ('memory_usage', random.uniform(30, 85)),
            ('disk_io_ops', random.randint(100, 1000)),
            ('network_bytes', random.randint(1000, 50000))
        ]
        
        for metric_name, value in metrics_data:
            tsdb.write_point(
                metric_name=metric_name,
                timestamp=point_ts,
                value=value,
                tags={
                    'server': f'srv-{(i % 10) + 1:02d}',
                    'region': random.choice(['mumbai', 'bangalore', 'delhi'])
                }
            )
    
    write_duration = time.time() - start_time
    total_points = points_to_write * 4  # 4 metrics per iteration
    
    print(f"   ✅ Wrote {total_points:,} points in {write_duration:.2f}s")
    print(f"   📊 Write throughput: {total_points/write_duration:,.0f} points/second")
    
    # Performance test - query data
    print(f"\n🔍 Performance Test - Querying aggregated data:")
    print("-" * 50)
    
    query_start = time.time()
    
    # Query each metric
    query_results = {}
    for metric_name in ['cpu_utilization', 'memory_usage', 'disk_io_ops', 'network_bytes']:
        query = TimeSeriesQuery(
            metric_name=metric_name,
            start_time=current_ts - (points_to_write * 10),
            end_time=current_ts,
            aggregation=AggregationType.AVG,
            interval=300  # 5 minute intervals
        )
        
        results = tsdb.query_metric(query)
        query_results[metric_name] = len(results)
    
    query_duration = time.time() - query_start
    
    print(f"   ✅ Queried 4 metrics in {query_duration:.3f}s")
    print(f"   📊 Query performance:")
    for metric, result_count in query_results.items():
        print(f"     {metric}: {result_count} aggregated points")
    
    # Show final database statistics
    final_stats = tsdb.get_database_stats()
    print(f"\n📈 Final Database Statistics:")
    print("-" * 30)
    print(f"   Total Points: {final_stats['total_points']:,}")
    print(f"   Total Metrics: {final_stats['total_metrics']}")
    print(f"   Total Buckets: {final_stats['total_buckets']}")
    print(f"   Points Written: {final_stats['database_stats']['points_written']:,}")
    print(f"   Queries Executed: {final_stats['database_stats']['queries_executed']}")
    
    tsdb.shutdown()

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_basic_timeseries_operations()
    
    print("\n" + "="*80 + "\n")
    
    ola_metrics_system = demonstrate_ola_metrics_system()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_ist_timezone_handling()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_performance_analysis()
    
    print(f"\n✅ Time-Series Database with IST Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Time-Series Storage - Bucketed data organization")
    print(f"   • IST Timezone Handling - Indian Standard Time support") 
    print(f"   • Data Aggregation - Sum, average, min, max, percentiles")
    print(f"   • Time-Based Queries - Range queries with intervals")
    print(f"   • Peak Analysis - Business hours and surge patterns")
    print(f"   • Real-time Metrics - Continuous data generation")
    print(f"   • Performance Optimization - High-throughput writes and queries")
    print(f"   • Indian Context - Ola cabs, IST business hours, Indian cities")
    print(f"   • Data Retention - Automatic cleanup of old data")