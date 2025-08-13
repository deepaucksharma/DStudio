#!/usr/bin/env python3
"""
API Monitoring and Metrics Collection System
Comprehensive API monitoring for Indian e-commerce platforms

Key Features:
- Real-time API performance monitoring
- Error rate tracking और alerting
- Response time analysis (Mumbai vs Bangalore latency)
- Rate limiting monitoring
- Business metrics collection
- Prometheus और Grafana integration

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns
"""

import time
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple
import threading
import logging
import statistics
from dataclasses import dataclass, asdict
import redis
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIMetric:
    """API metric data structure"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_id: Optional[str] = None
    region: str = "mumbai"
    service_name: str = "unknown"

@dataclass
class APIHealth:
    """API health status"""
    endpoint: str
    status: str  # healthy, degraded, down
    success_rate: float
    avg_response_time: float
    error_count: int
    last_check: datetime

class PrometheusMetrics:
    """
    Prometheus metrics collection
    Production-grade metrics collection जैसा Flipkart use करता है
    """
    
    def __init__(self):
        # Counter metrics
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status', 'region']
        )
        
        self.api_errors_total = Counter(
            'api_errors_total', 
            'Total API errors',
            ['method', 'endpoint', 'error_type', 'region']
        )
        
        # Histogram metrics for response times
        self.api_response_time = Histogram(
            'api_response_time_seconds',
            'API response time in seconds',
            ['method', 'endpoint', 'region'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Gauge metrics
        self.active_connections = Gauge(
            'api_active_connections',
            'Number of active connections',
            ['service']
        )
        
        self.api_rate_limit_remaining = Gauge(
            'api_rate_limit_remaining',
            'Remaining rate limit quota',
            ['user_id', 'endpoint']
        )

class APIMonitor:
    """
    Comprehensive API monitoring system
    Complete API monitoring जैसा Indian unicorns use करते हैं
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.metrics = PrometheusMetrics()
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # In-memory data structures for real-time analysis
        self.recent_requests = deque(maxlen=10000)  # Last 10k requests
        self.endpoint_stats = defaultdict(list)     # Response times per endpoint
        self.error_counts = defaultdict(int)        # Error counts
        self.active_users = set()                   # Active user tracking
        
        # Health check configuration
        self.health_check_interval = 30  # seconds
        self.health_thresholds = {
            "response_time": 2.0,    # 2 seconds max
            "error_rate": 0.05,      # 5% max error rate
            "availability": 0.99     # 99% availability
        }
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def record_api_call(self, metric: APIMetric):
        """
        Record API call metrics
        हर API call को track करते हैं - detailed monitoring
        """
        try:
            # Record in Prometheus
            self.metrics.api_requests_total.labels(
                method=metric.method,
                endpoint=metric.endpoint,
                status=str(metric.status_code),
                region=metric.region
            ).inc()
            
            self.metrics.api_response_time.labels(
                method=metric.method,
                endpoint=metric.endpoint,
                region=metric.region
            ).observe(metric.response_time)
            
            # Record errors
            if metric.status_code >= 400:
                error_type = self._categorize_error(metric.status_code)
                self.metrics.api_errors_total.labels(
                    method=metric.method,
                    endpoint=metric.endpoint,
                    error_type=error_type,
                    region=metric.region
                ).inc()
                
                self.error_counts[f"{metric.endpoint}_{error_type}"] += 1
            
            # Store in memory for real-time analysis
            self.recent_requests.append(metric)
            self.endpoint_stats[metric.endpoint].append(metric.response_time)
            
            # Track active users
            if metric.user_id:
                self.active_users.add(metric.user_id)
            
            # Store in Redis for persistence
            self._store_in_redis(metric)
            
            # Check for anomalies
            self._check_anomalies(metric)
            
        except Exception as e:
            logger.error(f"Error recording API metric: {str(e)}")
    
    def _categorize_error(self, status_code: int) -> str:
        """Categorize error types"""
        if status_code == 400:
            return "bad_request"
        elif status_code == 401:
            return "unauthorized"
        elif status_code == 403:
            return "forbidden"
        elif status_code == 404:
            return "not_found"
        elif status_code == 429:
            return "rate_limited"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "other"
    
    def _store_in_redis(self, metric: APIMetric):
        """Store metrics in Redis for persistence"""
        try:
            # Store raw metric
            metric_key = f"api_metric:{int(time.time())}"
            self.redis_client.setex(
                metric_key, 
                3600,  # 1 hour TTL
                json.dumps(asdict(metric), default=str)
            )
            
            # Update aggregated stats
            endpoint_key = f"endpoint_stats:{metric.endpoint}"
            self.redis_client.lpush(endpoint_key, metric.response_time)
            self.redis_client.ltrim(endpoint_key, 0, 999)  # Keep last 1000 responses
            self.redis_client.expire(endpoint_key, 3600)
            
        except Exception as e:
            logger.error(f"Error storing in Redis: {str(e)}")
    
    def _check_anomalies(self, metric: APIMetric):
        """
        Check for performance anomalies
        Performance issues को detect करते हैं - Mumbai traffic jam जैसा
        """
        try:
            # Check response time anomaly
            if metric.response_time > self.health_thresholds["response_time"]:
                self._trigger_alert(
                    "HIGH_RESPONSE_TIME",
                    f"High response time detected: {metric.response_time:.2f}s for {metric.endpoint}",
                    metric
                )
            
            # Check error rate for endpoint
            if len(self.endpoint_stats[metric.endpoint]) >= 100:
                recent_errors = sum(1 for m in self.recent_requests 
                                  if m.endpoint == metric.endpoint and m.status_code >= 400)
                error_rate = recent_errors / len(self.endpoint_stats[metric.endpoint])
                
                if error_rate > self.health_thresholds["error_rate"]:
                    self._trigger_alert(
                        "HIGH_ERROR_RATE",
                        f"High error rate detected: {error_rate:.2%} for {metric.endpoint}",
                        metric
                    )
            
        except Exception as e:
            logger.error(f"Error checking anomalies: {str(e)}")
    
    def _trigger_alert(self, alert_type: str, message: str, metric: APIMetric):
        """
        Trigger monitoring alerts
        Alert trigger करते हैं - immediate action के लिए
        """
        alert_data = {
            "type": alert_type,
            "message": message,
            "endpoint": metric.endpoint,
            "timestamp": datetime.now().isoformat(),
            "region": metric.region,
            "service": metric.service_name,
            "severity": "high" if alert_type in ["HIGH_ERROR_RATE", "SERVICE_DOWN"] else "medium"
        }
        
        # Store alert in Redis
        alert_key = f"alert:{int(time.time())}"
        self.redis_client.setex(alert_key, 86400, json.dumps(alert_data))  # 24 hour TTL
        
        # Log alert
        logger.warning(f"🚨 ALERT [{alert_type}]: {message}")
        
        # In production, यहाँ Slack/PagerDuty integration होगा
        self._send_notification(alert_data)
    
    def _send_notification(self, alert_data: Dict):
        """Send notification to team (Slack/Email/PagerDuty)"""
        # Slack webhook URL for Indian teams
        slack_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        
        slack_message = {
            "text": f"🚨 API Alert: {alert_data['type']}",
            "attachments": [
                {
                    "color": "danger" if alert_data["severity"] == "high" else "warning",
                    "fields": [
                        {"title": "Message", "value": alert_data["message"], "short": False},
                        {"title": "Endpoint", "value": alert_data["endpoint"], "short": True},
                        {"title": "Region", "value": alert_data["region"], "short": True},
                        {"title": "Time", "value": alert_data["timestamp"], "short": True}
                    ]
                }
            ]
        }
        
        try:
            # In production, uncomment this line
            # requests.post(slack_webhook, json=slack_message)
            logger.info(f"📱 Notification sent: {alert_data['message']}")
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
    
    def get_api_health(self, endpoint: str = None) -> Dict:
        """
        Get current API health status
        Current API health check करते हैं
        """
        try:
            if endpoint:
                # Health for specific endpoint
                recent_calls = [m for m in self.recent_requests if m.endpoint == endpoint]
            else:
                # Overall health
                recent_calls = list(self.recent_requests)
            
            if not recent_calls:
                return {"status": "no_data", "message": "No recent data available"}
            
            # Calculate metrics
            total_calls = len(recent_calls)
            error_calls = sum(1 for call in recent_calls if call.status_code >= 400)
            error_rate = error_calls / total_calls if total_calls > 0 else 0
            
            response_times = [call.response_time for call in recent_calls]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else avg_response_time
            
            # Determine health status
            status = "healthy"
            if error_rate > self.health_thresholds["error_rate"]:
                status = "degraded"
            if avg_response_time > self.health_thresholds["response_time"] * 2:
                status = "degraded"
            if error_rate > 0.2:  # 20% error rate
                status = "down"
            
            health_data = {
                "endpoint": endpoint or "overall",
                "status": status,
                "total_requests": total_calls,
                "error_rate": f"{error_rate:.2%}",
                "avg_response_time": f"{avg_response_time:.3f}s",
                "p95_response_time": f"{p95_response_time:.3f}s",
                "active_users": len(self.active_users),
                "timestamp": datetime.now().isoformat(),
                "region_breakdown": self._get_region_breakdown(recent_calls)
            }
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error getting API health: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_region_breakdown(self, calls: List[APIMetric]) -> Dict:
        """Get metrics breakdown by region"""
        region_stats = defaultdict(list)
        for call in calls:
            region_stats[call.region].append(call.response_time)
        
        breakdown = {}
        for region, times in region_stats.items():
            breakdown[region] = {
                "requests": len(times),
                "avg_response_time": f"{statistics.mean(times):.3f}s",
                "percentage": f"{len(times)/len(calls)*100:.1f}%"
            }
        
        return breakdown
    
    def get_top_slow_endpoints(self, limit: int = 10) -> List[Dict]:
        """
        Get top slow performing endpoints
        Sabse slow endpoints identify करते हैं
        """
        endpoint_avg_times = {}
        
        for endpoint, times in self.endpoint_stats.items():
            if len(times) >= 10:  # At least 10 samples
                endpoint_avg_times[endpoint] = {
                    "avg_time": statistics.mean(times),
                    "p95_time": statistics.quantiles(times, n=20)[18] if len(times) > 20 else statistics.mean(times),
                    "total_calls": len(times),
                    "endpoint": endpoint
                }
        
        # Sort by average response time
        slow_endpoints = sorted(
            endpoint_avg_times.values(),
            key=lambda x: x["avg_time"],
            reverse=True
        )[:limit]
        
        return slow_endpoints
    
    def generate_daily_report(self) -> Dict:
        """
        Generate daily API performance report
        Daily report generate करते हैं - team के लिए
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)
            
            # Get last 24 hours data
            daily_calls = [
                call for call in self.recent_requests
                if start_time <= call.timestamp <= end_time
            ]
            
            if not daily_calls:
                return {"message": "No data available for last 24 hours"}
            
            # Calculate daily metrics
            total_requests = len(daily_calls)
            total_errors = sum(1 for call in daily_calls if call.status_code >= 400)
            error_rate = total_errors / total_requests if total_requests > 0 else 0
            
            # Response time stats
            response_times = [call.response_time for call in daily_calls]
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Top endpoints by volume
            endpoint_counts = defaultdict(int)
            for call in daily_calls:
                endpoint_counts[call.endpoint] += 1
            
            top_endpoints = sorted(
                endpoint_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Generate report
            report = {
                "report_date": end_time.strftime("%Y-%m-%d"),
                "summary": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "error_rate": f"{error_rate:.2%}",
                    "avg_response_time": f"{avg_response_time:.3f}s",
                    "min_response_time": f"{min_response_time:.3f}s",
                    "max_response_time": f"{max_response_time:.3f}s",
                    "unique_users": len(set(call.user_id for call in daily_calls if call.user_id))
                },
                "top_endpoints": [
                    {"endpoint": ep, "requests": count, "percentage": f"{count/total_requests*100:.1f}%"}
                    for ep, count in top_endpoints
                ],
                "slow_endpoints": self.get_top_slow_endpoints(5),
                "regional_performance": self._get_region_breakdown(daily_calls),
                "hourly_traffic": self._get_hourly_traffic(daily_calls)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
            return {"error": str(e)}
    
    def _get_hourly_traffic(self, calls: List[APIMetric]) -> Dict:
        """Get hourly traffic breakdown"""
        hourly_counts = defaultdict(int)
        for call in calls:
            hour = call.timestamp.hour
            hourly_counts[hour] += 1
        
        return {f"{hour:02d}:00": count for hour, count in sorted(hourly_counts.items())}
    
    def _start_background_monitoring(self):
        """Start background monitoring tasks"""
        def health_check_worker():
            while True:
                try:
                    # Clear old active users (older than 5 minutes)
                    # In production, this would be more sophisticated
                    if len(self.active_users) > 1000:
                        self.active_users.clear()
                    
                    # Update system metrics
                    cpu_usage = psutil.cpu_percent()
                    memory_usage = psutil.virtual_memory().percent
                    
                    # Log system health
                    logger.info(f"System Health - CPU: {cpu_usage}%, Memory: {memory_usage}%")
                    
                    time.sleep(self.health_check_interval)
                    
                except Exception as e:
                    logger.error(f"Background monitoring error: {str(e)}")
                    time.sleep(60)  # Wait 1 minute on error
        
        # Start background thread
        monitoring_thread = threading.Thread(target=health_check_worker, daemon=True)
        monitoring_thread.start()
        logger.info("🔄 Background monitoring started")

# Demo functions for testing
def simulate_api_traffic(monitor: APIMonitor, duration: int = 60):
    """
    Simulate realistic API traffic
    Realistic API traffic simulate करते हैं - testing के लिए
    """
    import random
    
    endpoints = [
        "/api/v1/products/search",
        "/api/v1/user/profile", 
        "/api/v1/cart/add",
        "/api/v1/orders/create",
        "/api/v1/payments/process",
        "/api/v1/inventory/check"
    ]
    
    regions = ["mumbai", "bangalore", "delhi", "hyderabad"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    
    print(f"🎭 Simulating API traffic for {duration} seconds...")
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration:
        # Simulate API call
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        region = random.choice(regions)
        
        # Simulate response time (Mumbai slightly slower due to traffic 😄)
        base_time = random.uniform(0.1, 2.0)
        if region == "mumbai":
            base_time *= 1.2  # Mumbai traffic effect
        
        # Simulate errors (5% error rate)
        status_code = 200 if random.random() > 0.05 else random.choice([400, 404, 500, 503])
        
        metric = APIMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=base_time,
            timestamp=datetime.now(),
            user_id=f"user_{random.randint(1, 1000)}",
            region=region,
            service_name="flipkart-api"
        )
        
        monitor.record_api_call(metric)
        request_count += 1
        
        # Random sleep between requests
        time.sleep(random.uniform(0.01, 0.1))
    
    print(f"✅ Simulated {request_count} API calls")

if __name__ == "__main__":
    print("📊 API Monitoring & Metrics System")
    print("🇮🇳 Production-grade monitoring for Indian e-commerce")
    print("=" * 60)
    
    # Initialize monitoring
    monitor = APIMonitor()
    
    # Start Prometheus metrics server
    start_http_server(8090)
    print("📈 Prometheus metrics available at: http://localhost:8090/metrics")
    
    try:
        # Simulate some traffic
        simulate_api_traffic(monitor, 30)
        
        # Get health status
        print("\n🏥 API Health Status:")
        health = monitor.get_api_health()
        print(json.dumps(health, indent=2))
        
        # Get slow endpoints
        print("\n🐌 Top Slow Endpoints:")
        slow_endpoints = monitor.get_top_slow_endpoints(5)
        for i, endpoint in enumerate(slow_endpoints, 1):
            print(f"{i}. {endpoint['endpoint']}: {endpoint['avg_time']:.3f}s avg")
        
        # Generate daily report
        print("\n📋 Daily Performance Report:")
        report = monitor.generate_daily_report()
        print(json.dumps(report, indent=2))
        
        print("\n🎯 Monitoring setup completed!")
        print("💡 In production:")
        print("  - Set up Grafana dashboards")
        print("  - Configure Slack/PagerDuty alerts")
        print("  - Add custom business metrics")
        print("  - Set up log aggregation")
        
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Monitoring error: {str(e)}")