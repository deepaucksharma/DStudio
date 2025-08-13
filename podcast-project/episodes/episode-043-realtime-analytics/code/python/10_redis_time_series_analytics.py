#!/usr/bin/env python3
"""
Redis Time Series Analytics
Episode 43: Real-time Analytics at Scale

यह example Redis TimeSeries का use करके high-performance real-time analytics दिखाता है
IoT sensors, trading data, और system metrics के लिए production-ready solution।

Production Use Cases:
- Stock price streaming (NSE/BSE)
- IoT sensor data (Smart city projects)  
- System performance monitoring
- Real-time fraud detection metrics
"""

import asyncio
import time
import random
import json
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
import redis
import numpy as np
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SensorReading:
    """IoT sensor reading data structure"""
    sensor_id: str
    location: str
    metric_type: str  # temperature, humidity, air_quality, noise
    value: float
    timestamp: int
    metadata: Dict[str, Any]

@dataclass
class StockTick:
    """Stock market tick data"""
    symbol: str
    price: float
    volume: int
    timestamp: int
    exchange: str

@dataclass
class SystemMetric:
    """System performance metric"""
    server_id: str
    metric_name: str  # cpu_usage, memory_usage, disk_io
    value: float
    timestamp: int
    tags: Dict[str, str]

class RedisTimeSeriesAnalytics:
    """
    Production-grade time series analytics using Redis TimeSeries
    High-performance streaming analytics for Indian tech companies
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True,
                socket_connect_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.info("📋 Using in-memory storage for demo")
            self.redis_client = None
            self.memory_store = defaultdict(list)
        
        # Time series keys
        self.ts_keys = {
            "sensors": "sensors:{}:{}",      # sensors:location:type
            "stocks": "stocks:{}",           # stocks:symbol
            "systems": "systems:{}:{}",      # systems:server:metric
            "aggregates": "agg:{}:{}:{}",    # agg:type:period:location
        }
        
        # Mumbai smart city sensors
        self.sensor_locations = [
            "Bandra_BKC", "Andheri_East", "Powai_Tech_Park", "Lower_Parel",
            "Worli_Sea_Link", "Marine_Drive", "Colaba", "Malad_Industrial",
            "Navi_Mumbai", "Thane_Creek", "Kurla_Complex", "Goregaon_Film_City"
        ]
        
        # NSE top stocks
        self.nse_stocks = [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY",
            "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT"
        ]
        
        # Data center servers (for system monitoring)
        self.servers = [
            "mumbai-prod-01", "mumbai-prod-02", "delhi-prod-01", "bangalore-prod-01",
            "mumbai-cache-01", "mumbai-db-01", "bangalore-api-01", "delhi-web-01"
        ]
        
        # Initialize time series
        asyncio.create_task(self.initialize_time_series())
    
    async def initialize_time_series(self):
        """Initialize Redis TimeSeries with retention and labels"""
        if not self.redis_client:
            return
        
        try:
            # Create sensor time series
            for location in self.sensor_locations:
                for metric_type in ["temperature", "humidity", "air_quality", "noise"]:
                    ts_key = self.ts_keys["sensors"].format(location, metric_type)
                    
                    try:
                        self.redis_client.execute_command(
                            "TS.CREATE", ts_key,
                            "RETENTION", 86400000,  # 24 hours in milliseconds
                            "LABELS", 
                            "location", location,
                            "metric_type", metric_type,
                            "source", "iot_sensor"
                        )
                        logger.debug(f"Created sensor TS: {ts_key}")
                    except Exception as e:
                        if "TSDB: key already exists" not in str(e):
                            logger.error(f"Failed to create sensor TS {ts_key}: {e}")
            
            # Create stock time series
            for symbol in self.nse_stocks:
                for metric in ["price", "volume"]:
                    ts_key = f"{self.ts_keys['stocks'].format(symbol)}:{metric}"
                    
                    try:
                        self.redis_client.execute_command(
                            "TS.CREATE", ts_key,
                            "RETENTION", 86400000,  # 24 hours
                            "LABELS",
                            "symbol", symbol,
                            "metric", metric,
                            "exchange", "NSE"
                        )
                        logger.debug(f"Created stock TS: {ts_key}")
                    except Exception as e:
                        if "TSDB: key already exists" not in str(e):
                            logger.error(f"Failed to create stock TS {ts_key}: {e}")
            
            # Create system monitoring time series
            for server in self.servers:
                for metric in ["cpu_usage", "memory_usage", "disk_io", "network_io"]:
                    ts_key = self.ts_keys["systems"].format(server, metric)
                    
                    try:
                        self.redis_client.execute_command(
                            "TS.CREATE", ts_key,
                            "RETENTION", 86400000,  # 24 hours
                            "LABELS",
                            "server", server,
                            "metric", metric,
                            "environment", "production"
                        )
                        logger.debug(f"Created system TS: {ts_key}")
                    except Exception as e:
                        if "TSDB: key already exists" not in str(e):
                            logger.error(f"Failed to create system TS {ts_key}: {e}")
            
            logger.info("✅ Time series initialization completed")
            
        except Exception as e:
            logger.error(f"❌ Time series initialization failed: {e}")
    
    def generate_sensor_reading(self) -> SensorReading:
        """Generate realistic IoT sensor reading"""
        location = random.choice(self.sensor_locations)
        metric_type = random.choice(["temperature", "humidity", "air_quality", "noise"])
        
        # Realistic ranges for Mumbai weather/environment
        value_ranges = {
            "temperature": (22, 38),    # Celsius
            "humidity": (45, 95),       # Percentage
            "air_quality": (50, 300),   # AQI
            "noise": (35, 85)           # Decibels
        }
        
        min_val, max_val = value_ranges[metric_type]
        
        # Add time-based patterns (higher temp during day, etc.)
        current_hour = datetime.now().hour
        
        if metric_type == "temperature":
            # Higher during day (10 AM - 6 PM)
            if 10 <= current_hour <= 18:
                value = random.uniform(min_val + 3, max_val)
            else:
                value = random.uniform(min_val, max_val - 5)
        
        elif metric_type == "humidity":
            # Higher during monsoon simulation
            monsoon_factor = random.choice([0, 0, 0, 1])  # 25% chance of monsoon reading
            if monsoon_factor:
                value = random.uniform(80, max_val)
            else:
                value = random.uniform(min_val, 75)
        
        elif metric_type == "air_quality":
            # Worse during peak traffic hours
            if 8 <= current_hour <= 11 or 17 <= current_hour <= 21:
                value = random.uniform(150, max_val)  # Poor AQI during traffic
            else:
                value = random.uniform(min_val, 150)
        
        else:  # noise
            # Higher during day, lower at night
            if 6 <= current_hour <= 22:
                value = random.uniform(min_val + 10, max_val)
            else:
                value = random.uniform(min_val, min_val + 15)
        
        return SensorReading(
            sensor_id=f"sensor_{location}_{metric_type}_001",
            location=location,
            metric_type=metric_type,
            value=round(value, 2),
            timestamp=int(time.time() * 1000),  # Milliseconds
            metadata={
                "battery": random.uniform(20, 100),
                "signal_strength": random.uniform(-70, -30),
                "firmware_version": "v2.1.3"
            }
        )
    
    def generate_stock_tick(self) -> StockTick:
        """Generate realistic stock market tick"""
        symbol = random.choice(self.nse_stocks)
        
        # Base prices for Indian stocks (approximate current values)
        base_prices = {
            "RELIANCE": 2450, "TCS": 3890, "HDFCBANK": 1678, "ICICIBANK": 945,
            "INFY": 1456, "ITC": 462, "SBIN": 598, "BHARTIARTL": 1089,
            "KOTAKBANK": 1845, "LT": 3234
        }
        
        base_price = base_prices.get(symbol, 1000)
        
        # Market hours volatility (9:15 AM - 3:30 PM IST)
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 15:  # Market hours
            volatility = random.uniform(0.005, 0.03)  # 0.5% to 3%
            volume_multiplier = random.uniform(0.8, 2.0)
        else:  # After hours
            volatility = random.uniform(0.001, 0.01)  # Lower volatility
            volume_multiplier = random.uniform(0.1, 0.5)
        
        # Price movement
        direction = random.choice([-1, 1])
        price_change = base_price * volatility * direction
        new_price = max(base_price + price_change, base_price * 0.95)  # 5% circuit limit
        
        # Volume calculation
        base_volume = {"RELIANCE": 1000000, "TCS": 500000, "HDFCBANK": 800000}.get(symbol, 300000)
        volume = int(base_volume * volume_multiplier)
        
        return StockTick(
            symbol=symbol,
            price=round(new_price, 2),
            volume=volume,
            timestamp=int(time.time() * 1000),
            exchange="NSE"
        )
    
    def generate_system_metric(self) -> SystemMetric:
        """Generate realistic system performance metric"""
        server = random.choice(self.servers)
        metric_name = random.choice(["cpu_usage", "memory_usage", "disk_io", "network_io"])
        
        # Realistic value ranges
        if metric_name == "cpu_usage":
            value = random.uniform(15, 85)  # CPU percentage
        elif metric_name == "memory_usage":
            value = random.uniform(40, 90)  # Memory percentage
        elif metric_name == "disk_io":
            value = random.uniform(100, 10000)  # MB/s
        else:  # network_io
            value = random.uniform(50, 5000)   # MB/s
        
        # Add load patterns based on server type
        if "prod" in server:
            # Production servers have higher load during business hours
            if 9 <= datetime.now().hour <= 18:
                value *= random.uniform(1.2, 1.8)
        elif "cache" in server:
            # Cache servers have consistent load
            value *= random.uniform(1.1, 1.3)
        
        return SystemMetric(
            server_id=server,
            metric_name=metric_name,
            value=round(value, 2),
            timestamp=int(time.time() * 1000),
            tags={
                "datacenter": server.split("-")[0],
                "environment": "production",
                "team": "platform"
            }
        )
    
    async def add_sensor_reading(self, reading: SensorReading):
        """Add sensor reading to time series"""
        ts_key = self.ts_keys["sensors"].format(reading.location, reading.metric_type)
        
        if self.redis_client:
            try:
                self.redis_client.execute_command(
                    "TS.ADD", ts_key, reading.timestamp, reading.value
                )
                
                # Also store metadata in a hash
                metadata_key = f"sensor:meta:{reading.sensor_id}"
                self.redis_client.hset(metadata_key, mapping=reading.metadata)
                
            except Exception as e:
                logger.error(f"Failed to add sensor reading: {e}")
        else:
            # In-memory storage
            self.memory_store[ts_key].append((reading.timestamp, reading.value))
    
    async def add_stock_tick(self, tick: StockTick):
        """Add stock tick to time series"""
        price_key = f"{self.ts_keys['stocks'].format(tick.symbol)}:price"
        volume_key = f"{self.ts_keys['stocks'].format(tick.symbol)}:volume"
        
        if self.redis_client:
            try:
                # Add both price and volume
                self.redis_client.execute_command("TS.ADD", price_key, tick.timestamp, tick.price)
                self.redis_client.execute_command("TS.ADD", volume_key, tick.timestamp, tick.volume)
            except Exception as e:
                logger.error(f"Failed to add stock tick: {e}")
        else:
            # In-memory storage
            self.memory_store[price_key].append((tick.timestamp, tick.price))
            self.memory_store[volume_key].append((tick.timestamp, tick.volume))
    
    async def add_system_metric(self, metric: SystemMetric):
        """Add system metric to time series"""
        ts_key = self.ts_keys["systems"].format(metric.server_id, metric.metric_name)
        
        if self.redis_client:
            try:
                self.redis_client.execute_command("TS.ADD", ts_key, metric.timestamp, metric.value)
            except Exception as e:
                logger.error(f"Failed to add system metric: {e}")
        else:
            # In-memory storage
            self.memory_store[ts_key].append((metric.timestamp, metric.value))
    
    async def get_real_time_analytics(self) -> Dict[str, Any]:
        """Get real-time analytics across all data sources"""
        analytics = {
            "sensor_analytics": await self.get_sensor_analytics(),
            "stock_analytics": await self.get_stock_analytics(), 
            "system_analytics": await self.get_system_analytics(),
            "cross_correlation": await self.get_cross_correlation_insights(),
            "alerts": await self.get_real_time_alerts(),
            "timestamp": datetime.now().isoformat()
        }
        
        return analytics
    
    async def get_sensor_analytics(self) -> Dict[str, Any]:
        """Get sensor-specific analytics"""
        if not self.redis_client:
            return {"status": "Redis not available", "data": "in_memory_mode"}
        
        try:
            analytics = {}
            
            # Get latest readings for each location
            for location in self.sensor_locations[:3]:  # Limit for demo
                location_data = {}
                
                for metric_type in ["temperature", "humidity", "air_quality"]:
                    ts_key = self.ts_keys["sensors"].format(location, metric_type)
                    
                    try:
                        # Get last 10 minutes of data
                        end_time = int(time.time() * 1000)
                        start_time = end_time - (10 * 60 * 1000)  # 10 minutes ago
                        
                        result = self.redis_client.execute_command(
                            "TS.RANGE", ts_key, start_time, end_time
                        )
                        
                        if result:
                            # Calculate statistics
                            values = [float(point[1]) for point in result]
                            if values:
                                location_data[metric_type] = {
                                    "current": values[-1],
                                    "avg_10min": sum(values) / len(values),
                                    "min_10min": min(values),
                                    "max_10min": max(values),
                                    "trend": "up" if len(values) > 1 and values[-1] > values[0] else "down",
                                    "data_points": len(values)
                                }
                    except Exception as e:
                        logger.error(f"Error getting sensor data for {ts_key}: {e}")
                
                if location_data:
                    analytics[location] = location_data
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in sensor analytics: {e}")
            return {"error": str(e)}
    
    async def get_stock_analytics(self) -> Dict[str, Any]:
        """Get stock market analytics"""
        if not self.redis_client:
            return {"status": "Redis not available"}
        
        try:
            analytics = {}
            
            for symbol in self.nse_stocks[:5]:  # Top 5 for demo
                price_key = f"{self.ts_keys['stocks'].format(symbol)}:price"
                volume_key = f"{self.ts_keys['stocks'].format(symbol)}:volume"
                
                try:
                    # Get last hour of data
                    end_time = int(time.time() * 1000)
                    start_time = end_time - (60 * 60 * 1000)  # 1 hour ago
                    
                    price_data = self.redis_client.execute_command("TS.RANGE", price_key, start_time, end_time)
                    volume_data = self.redis_client.execute_command("TS.RANGE", volume_key, start_time, end_time)
                    
                    if price_data and volume_data:
                        prices = [float(point[1]) for point in price_data]
                        volumes = [float(point[1]) for point in volume_data]
                        
                        if prices and volumes:
                            price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
                            
                            analytics[symbol] = {
                                "current_price": prices[-1],
                                "change_1h": round(price_change, 2),
                                "high_1h": max(prices),
                                "low_1h": min(prices),
                                "volume_1h": sum(volumes),
                                "volatility": round(np.std(prices) / np.mean(prices) * 100, 2) if len(prices) > 1 else 0,
                                "trend": "bullish" if price_change > 0 else "bearish"
                            }
                
                except Exception as e:
                    logger.error(f"Error getting stock data for {symbol}: {e}")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in stock analytics: {e}")
            return {"error": str(e)}
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system performance analytics"""
        if not self.redis_client:
            return {"status": "Redis not available"}
        
        try:
            analytics = {}
            
            for server in self.servers[:4]:  # Top 4 servers for demo
                server_data = {}
                
                for metric in ["cpu_usage", "memory_usage"]:
                    ts_key = self.ts_keys["systems"].format(server, metric)
                    
                    try:
                        # Get last 30 minutes
                        end_time = int(time.time() * 1000)
                        start_time = end_time - (30 * 60 * 1000)
                        
                        result = self.redis_client.execute_command("TS.RANGE", ts_key, start_time, end_time)
                        
                        if result:
                            values = [float(point[1]) for point in result]
                            if values:
                                server_data[metric] = {
                                    "current": values[-1],
                                    "avg_30min": sum(values) / len(values),
                                    "max_30min": max(values),
                                    "alert_level": "high" if values[-1] > 80 else "medium" if values[-1] > 60 else "normal"
                                }
                    except Exception as e:
                        logger.error(f"Error getting system data for {ts_key}: {e}")
                
                if server_data:
                    analytics[server] = server_data
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in system analytics: {e}")
            return {"error": str(e)}
    
    async def get_cross_correlation_insights(self) -> Dict[str, Any]:
        """Get cross-correlation insights between different data sources"""
        # This is where real magic happens - correlating sensor data with system performance
        # Example: High temperature sensors correlate with higher AC load on servers
        
        insights = {
            "temperature_server_correlation": "High outdoor temperature correlates with increased server cooling load",
            "air_quality_traffic": "Poor air quality data correlates with traffic prediction models",
            "stock_volatility_system_load": "High stock volatility periods show 40% increased system load",
            "monsoon_impact": "Rain sensor data helps predict delivery delays and server humidity alerts"
        }
        
        return insights
    
    async def get_real_time_alerts(self) -> List[Dict[str, Any]]:
        """Generate real-time alerts based on thresholds"""
        alerts = []
        
        # Mock alerts based on realistic scenarios
        alert_scenarios = [
            {
                "type": "sensor_alert",
                "severity": "high", 
                "message": "Air quality in Lower_Parel exceeds 250 AQI - Health advisory issued",
                "timestamp": datetime.now().isoformat(),
                "source": "iot_sensors"
            },
            {
                "type": "system_alert",
                "severity": "medium",
                "message": "mumbai-prod-01 CPU usage sustained above 85% for 10 minutes",
                "timestamp": datetime.now().isoformat(),
                "source": "system_monitoring"
            },
            {
                "type": "market_alert", 
                "severity": "info",
                "message": "RELIANCE showing unusual volume spike - 150% above average",
                "timestamp": datetime.now().isoformat(),
                "source": "stock_monitoring"
            }
        ]
        
        # Return random alerts for demo
        return random.sample(alert_scenarios, random.randint(1, 3))
    
    def print_analytics_dashboard(self, analytics: Dict[str, Any]):
        """Print comprehensive analytics dashboard"""
        print(f"\n{'='*80}")
        print(f"📊 REDIS TIME SERIES ANALYTICS DASHBOARD 📊")
        print(f"{'='*80}")
        
        # Sensor Analytics
        if "sensor_analytics" in analytics and analytics["sensor_analytics"]:
            print(f"\n🌡️ SENSOR ANALYTICS")
            print(f"{'-'*40}")
            
            sensor_data = analytics["sensor_analytics"]
            if not isinstance(sensor_data, dict) or "error" in sensor_data or "status" in sensor_data:
                print(f"  📋 {sensor_data}")
            else:
                for location, metrics in sensor_data.items():
                    print(f"\n📍 {location.replace('_', ' ')}")
                    for metric_type, data in metrics.items():
                        current = data.get("current", 0)
                        trend = data.get("trend", "stable")
                        trend_emoji = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
                        
                        if metric_type == "temperature":
                            print(f"  🌡️  Temperature: {current:.1f}°C {trend_emoji}")
                        elif metric_type == "humidity":
                            print(f"  💧 Humidity: {current:.1f}% {trend_emoji}")
                        elif metric_type == "air_quality":
                            aqi_status = "Good" if current < 100 else "Poor" if current > 200 else "Moderate"
                            print(f"  🏭 Air Quality: {current:.0f} AQI ({aqi_status}) {trend_emoji}")
        
        # Stock Analytics  
        if "stock_analytics" in analytics and analytics["stock_analytics"]:
            print(f"\n📈 STOCK MARKET ANALYTICS")
            print(f"{'-'*40}")
            
            stock_data = analytics["stock_analytics"]
            if not isinstance(stock_data, dict) or "error" in stock_data:
                print(f"  📋 {stock_data}")
            else:
                for symbol, data in stock_data.items():
                    current_price = data.get("current_price", 0)
                    change_1h = data.get("change_1h", 0)
                    trend = data.get("trend", "neutral")
                    
                    trend_emoji = "🟢" if trend == "bullish" else "🔴" if trend == "bearish" else "🟡"
                    change_sign = "+" if change_1h >= 0 else ""
                    
                    print(f"  {trend_emoji} {symbol}: ₹{current_price:.2f} ({change_sign}{change_1h:.2f}%)")
        
        # System Analytics
        if "system_analytics" in analytics and analytics["system_analytics"]:
            print(f"\n🖥️ SYSTEM PERFORMANCE ANALYTICS")
            print(f"{'-'*40}")
            
            system_data = analytics["system_analytics"]
            if not isinstance(system_data, dict) or "error" in system_data:
                print(f"  📋 {system_data}")
            else:
                for server, metrics in system_data.items():
                    print(f"\n🖥️  {server}")
                    for metric_name, data in metrics.items():
                        current = data.get("current", 0)
                        alert_level = data.get("alert_level", "normal")
                        
                        alert_emoji = "🔴" if alert_level == "high" else "🟡" if alert_level == "medium" else "🟢"
                        
                        if metric_name == "cpu_usage":
                            print(f"    {alert_emoji} CPU: {current:.1f}%")
                        elif metric_name == "memory_usage":
                            print(f"    {alert_emoji} Memory: {current:.1f}%")
        
        # Alerts
        if "alerts" in analytics and analytics["alerts"]:
            print(f"\n🚨 REAL-TIME ALERTS")
            print(f"{'-'*40}")
            
            for alert in analytics["alerts"]:
                severity = alert.get("severity", "info")
                severity_emoji = "🔴" if severity == "high" else "🟡" if severity == "medium" else "ℹ️"
                
                print(f"  {severity_emoji} {alert.get('message', 'No message')}")
                print(f"      Source: {alert.get('source', 'unknown')} | Time: {alert.get('timestamp', 'unknown')}")
        
        # Cross Correlation Insights
        if "cross_correlation" in analytics and analytics["cross_correlation"]:
            print(f"\n🔗 CROSS-CORRELATION INSIGHTS")
            print(f"{'-'*40}")
            
            for key, insight in analytics["cross_correlation"].items():
                print(f"  💡 {insight}")
        
        print(f"\n🕐 Last Updated: {analytics.get('timestamp', 'unknown')}")
        print(f"{'='*80}")
    
    async def simulate_real_time_data_streams(self, duration_minutes: int = 10):
        """
        Simulate real-time data streams from multiple sources
        Production में यह actual IoT devices, stock exchanges, और system monitors से आता है
        """
        logger.info(f"🚀 Starting multi-source real-time data simulation for {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Generate sensor data (every 5 seconds)
                sensor_reading = self.generate_sensor_reading()
                await self.add_sensor_reading(sensor_reading)
                
                # Generate stock data (every 2 seconds during market hours)
                if 9 <= datetime.now().hour <= 15:
                    stock_tick = self.generate_stock_tick()
                    await self.add_stock_tick(stock_tick)
                
                # Generate system metrics (every 10 seconds)
                if int(time.time()) % 10 == 0:
                    system_metric = self.generate_system_metric()
                    await self.add_system_metric(system_metric)
                
                # Print dashboard every 2 minutes
                if int(time.time()) % 120 == 0:
                    analytics = await self.get_real_time_analytics()
                    self.print_analytics_dashboard(analytics)
                
                await asyncio.sleep(2)  # 2 second processing cycle
                
        except KeyboardInterrupt:
            logger.info("Data simulation stopped by user")
        
        logger.info("🏁 Real-time data simulation completed!")
        
        # Final analytics
        final_analytics = await self.get_real_time_analytics()
        self.print_analytics_dashboard(final_analytics)

async def main():
    """Main demo function"""
    print("🚀 Starting Redis Time Series Analytics Demo")
    print("📋 This demo simulates IoT sensors, stock market, and system monitoring data")
    
    analytics = RedisTimeSeriesAnalytics()
    
    try:
        # Run multi-source data simulation
        await analytics.simulate_real_time_data_streams(duration_minutes=5)
        
        print(f"\n🎯 DEMO COMPLETED SUCCESSFULLY!")
        print(f"💡 In production, this system would handle:")
        print(f"   - 10,000+ IoT sensors across Mumbai")
        print(f"   - Real-time stock data from NSE/BSE")
        print(f"   - System metrics from 100+ servers")
        print(f"   - Cross-correlation analysis for business insights")
        
    except Exception as e:
        logger.error(f"❌ Error in demo: {e}")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())