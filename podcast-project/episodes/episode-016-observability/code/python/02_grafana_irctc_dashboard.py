#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 2: Grafana IRCTC Tatkal Booking Dashboard

IRCTC Tatkal booking system के लिए comprehensive monitoring dashboard
10 AM rush hour analytics और real-time performance tracking

Author: Hindi Tech Podcast
Context: Railway booking system monitoring at Indian scale
"""

import json
import time
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import structlog

# Grafana API client के लिए
from grafana_api.grafana_face import GrafanaFace

logger = structlog.get_logger()

class IRCTCBookingStatus(Enum):
    """IRCTC booking status types"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    QUEUE_FULL = "queue_full"
    PAYMENT_FAILED = "payment_failed"
    TECHNICAL_ERROR = "technical_error"
    USER_CANCELLED = "user_cancelled"

class TrainRoute(Enum):
    """Popular train routes for Tatkal booking"""
    MUMBAI_DELHI = "mumbai_delhi"
    DELHI_MUMBAI = "delhi_mumbai"
    BANGALORE_DELHI = "bangalore_delhi"
    CHENNAI_MUMBAI = "chennai_mumbai"
    KOLKATA_DELHI = "kolkata_delhi"
    PUNE_DELHI = "pune_delhi"
    HYDERABAD_MUMBAI = "hyderabad_mumbai"
    AHMEDABAD_MUMBAI = "ahmedabad_mumbai"

@dataclass
class IRCTCBookingEvent:
    """
    IRCTC booking event का data structure
    Comprehensive tracking के लिए all required fields
    """
    booking_id: str
    user_id: str
    train_number: str
    route: TrainRoute
    booking_class: str  # AC1, AC2, AC3, SL
    journey_date: str
    booking_status: IRCTCBookingStatus
    queue_position: Optional[int] = None
    wait_time_seconds: float = 0.0
    payment_time_seconds: float = 0.0
    total_time_seconds: float = 0.0
    error_code: Optional[str] = None
    user_agent: str = "mobile_app"
    user_city: str = "Mumbai"
    timestamp: datetime = None
    retry_attempt: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class GrafanaIRCTCDashboard:
    """
    Grafana dashboard manager for IRCTC monitoring
    Dashboard creation, update, और management के लिए
    """
    
    def __init__(self, grafana_url: str = "http://localhost:3000", 
                 api_key: str = None, username: str = "admin", password: str = "admin"):
        """
        Grafana API client initialize करता है
        """
        if api_key:
            self.grafana = GrafanaFace(auth=api_key, host=grafana_url)
        else:
            self.grafana = GrafanaFace(auth=(username, password), host=grafana_url)
        
        self.dashboard_uid = "irctc-tatkal-monitoring"
        self.dashboard_title = "IRCTC Tatkal Booking Monitoring"
        
        logger.info("Grafana IRCTC Dashboard initialized", 
                   url=grafana_url, dashboard_uid=self.dashboard_uid)

    def create_irctc_dashboard(self) -> Dict[str, Any]:
        """
        Complete IRCTC monitoring dashboard create करता है
        Production-ready panels के साथ
        """
        dashboard_config = {
            "dashboard": {
                "uid": self.dashboard_uid,
                "title": self.dashboard_title,
                "tags": ["irctc", "railway", "tatkal", "booking", "indian-railways"],
                "timezone": "Asia/Kolkata",
                "refresh": "10s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "timepicker": {
                    "refresh_intervals": ["5s", "10s", "30s", "1m", "5m"],
                    "time_options": ["5m", "15m", "1h", "6h", "12h", "24h"]
                },
                "panels": self._create_dashboard_panels(),
                "templating": {
                    "list": self._create_template_variables()
                },
                "annotations": {
                    "list": self._create_annotations()
                }
            },
            "folderId": 0,
            "overwrite": True
        }
        
        try:
            result = self.grafana.dashboard.update_dashboard(dashboard_config)
            logger.info("IRCTC dashboard created/updated successfully", 
                       uid=self.dashboard_uid, url=result.get('url'))
            return result
        except Exception as e:
            logger.error("Failed to create IRCTC dashboard", error=str(e))
            raise

    def _create_dashboard_panels(self) -> List[Dict[str, Any]]:
        """
        Dashboard panels की complete list create करता है
        IRCTC specific metrics के साथ
        """
        panels = []
        
        # Panel 1: Real-time booking success rate
        panels.append({
            "id": 1,
            "title": "📊 Tatkal Booking Success Rate (Real-time)",
            "type": "stat",
            "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
            "targets": [{
                "expr": "rate(irctc_bookings_total{status=\"success\"}[5m]) / rate(irctc_bookings_total[5m]) * 100",
                "legendFormat": "Success Rate %",
                "refId": "A"
            }],
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100,
                    "thresholds": {
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "yellow", "value": 70},
                            {"color": "green", "value": 85}
                        ]
                    }
                }
            },
            "options": {
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "orientation": "auto",
                "textMode": "value_and_name",
                "colorMode": "value"
            }
        })
        
        # Panel 2: Current active users (10 AM rush)
        panels.append({
            "id": 2,
            "title": "👥 Active Users (Concurrent)",
            "type": "stat",
            "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
            "targets": [{
                "expr": "irctc_concurrent_users",
                "legendFormat": "Active Users",
                "refId": "A"
            }],
            "fieldConfig": {
                "defaults": {
                    "unit": "short",
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": 0},
                            {"color": "yellow", "value": 500000},
                            {"color": "red", "value": 1000000}
                        ]
                    }
                }
            }
        })
        
        # Panel 3: Average booking completion time
        panels.append({
            "id": 3,
            "title": "⏱️ Avg Booking Time",
            "type": "stat",
            "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
            "targets": [{
                "expr": "rate(irctc_booking_duration_seconds_sum[5m]) / rate(irctc_booking_duration_seconds_count[5m])",
                "legendFormat": "Avg Time (sec)",
                "refId": "A"
            }],
            "fieldConfig": {
                "defaults": {
                    "unit": "s",
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": 0},
                            {"color": "yellow", "value": 60},
                            {"color": "red", "value": 180}
                        ]
                    }
                }
            }
        })
        
        # Panel 4: Queue depth monitoring
        panels.append({
            "id": 4,
            "title": "🚦 Queue Depth",
            "type": "stat", 
            "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
            "targets": [{
                "expr": "irctc_queue_depth",
                "legendFormat": "Queue Size",
                "refId": "A"
            }],
            "fieldConfig": {
                "defaults": {
                    "unit": "short",
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": 0},
                            {"color": "yellow", "value": 1000},
                            {"color": "red", "value": 5000}
                        ]
                    }
                }
            }
        })
        
        # Panel 5: Booking attempts vs success (time series)
        panels.append({
            "id": 5,
            "title": "📈 Booking Attempts vs Success Rate",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
            "targets": [
                {
                    "expr": "rate(irctc_bookings_total[1m]) * 60",
                    "legendFormat": "Total Attempts/min",
                    "refId": "A"
                },
                {
                    "expr": "rate(irctc_bookings_total{status=\"success\"}[1m]) * 60",
                    "legendFormat": "Successful Bookings/min",
                    "refId": "B"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "short",
                    "custom": {"drawStyle": "line", "fillOpacity": 10}
                }
            }
        })
        
        # Panel 6: Route-wise performance
        panels.append({
            "id": 6,
            "title": "🚄 Route-wise Success Rate",
            "type": "barchart",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
            "targets": [{
                "expr": "rate(irctc_bookings_total{status=\"success\"}[5m]) by (route) / rate(irctc_bookings_total[5m]) by (route) * 100",
                "legendFormat": "{{route}}",
                "refId": "A"
            }],
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "custom": {"orientation": "horizontal"}
                }
            }
        })
        
        # Panel 7: Error breakdown
        panels.append({
            "id": 7,
            "title": "❌ Error Breakdown (Last 15 minutes)",
            "type": "piechart",
            "gridPos": {"h": 8, "w": 8, "x": 0, "y": 16},
            "targets": [{
                "expr": "increase(irctc_errors_total[15m])",
                "legendFormat": "{{error_type}}",
                "refId": "A"
            }],
            "options": {
                "pieType": "donut",
                "displayLabels": ["name", "value"]
            }
        })
        
        # Panel 8: Payment gateway performance
        panels.append({
            "id": 8,
            "title": "💳 Payment Gateway Success Rate",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 8, "x": 8, "y": 16},
            "targets": [{
                "expr": "rate(irctc_payment_success_total[5m]) by (gateway) / rate(irctc_payment_attempts_total[5m]) by (gateway) * 100",
                "legendFormat": "{{gateway}}",
                "refId": "A"
            }],
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "min": 0,
                    "max": 100
                }
            }
        })
        
        # Panel 9: Regional performance heatmap
        panels.append({
            "id": 9,
            "title": "🗺️ Regional Performance",
            "type": "table",
            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 16},
            "targets": [{
                "expr": "avg by (city) (rate(irctc_booking_duration_seconds_sum[5m]) / rate(irctc_booking_duration_seconds_count[5m]))",
                "legendFormat": "{{city}}",
                "refId": "A",
                "format": "table"
            }],
            "transformations": [{
                "id": "organize",
                "options": {
                    "excludeByName": {},
                    "indexByName": {},
                    "renameByName": {
                        "city": "City",
                        "Value": "Avg Response Time (s)"
                    }
                }
            }]
        })
        
        # Panel 10: Peak hour analysis (10 AM slot focus)
        panels.append({
            "id": 10,
            "title": "🕙 Peak Hour Analysis (10 AM Tatkal)",
            "type": "timeseries",
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24},
            "targets": [
                {
                    "expr": "irctc_tatkal_booking_rate{hour=\"10\"}",
                    "legendFormat": "10 AM Bookings/sec",
                    "refId": "A"
                },
                {
                    "expr": "irctc_tatkal_booking_rate{hour=\"11\"}",
                    "legendFormat": "11 AM Bookings/sec",
                    "refId": "B"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "reqps",
                    "custom": {"fillOpacity": 20}
                }
            }
        })
        
        return panels

    def _create_template_variables(self) -> List[Dict[str, Any]]:
        """
        Dashboard template variables create करता है
        Dynamic filtering के लिए
        """
        return [
            {
                "name": "route",
                "type": "query",
                "query": "label_values(irctc_bookings_total, route)",
                "refresh": 1,
                "includeAll": True,
                "allValue": ".*",
                "multi": True
            },
            {
                "name": "booking_class",
                "type": "query", 
                "query": "label_values(irctc_bookings_total, booking_class)",
                "refresh": 1,
                "includeAll": True,
                "allValue": ".*",
                "multi": True
            },
            {
                "name": "city",
                "type": "query",
                "query": "label_values(irctc_bookings_total, user_city)",
                "refresh": 1,
                "includeAll": True,
                "allValue": ".*",
                "multi": True
            }
        ]

    def _create_annotations(self) -> List[Dict[str, Any]]:
        """
        Important events के लिए annotations create करता है
        """
        return [
            {
                "name": "Tatkal Opening Times",
                "enable": True,
                "query": "irctc_tatkal_opening_time",
                "iconColor": "green",
                "textFormat": "Tatkal booking opened for {{train_number}}"
            },
            {
                "name": "System Maintenance",
                "enable": True,
                "query": "irctc_maintenance_events",
                "iconColor": "red",
                "textFormat": "System maintenance: {{description}}"
            }
        ]

class IRCTCMetricsSimulator:
    """
    IRCTC metrics का realistic simulation
    Dashboard testing के लिए
    """
    
    def __init__(self):
        self.booking_events = []
        self.concurrent_users = 0
        self.queue_depth = 0
        self.is_peak_hour = False
        
    def generate_booking_event(self) -> IRCTCBookingEvent:
        """
        Realistic IRCTC booking event generate करता है
        """
        # Peak hour detection (10 AM - 11 AM IST)
        current_hour = datetime.now().hour
        self.is_peak_hour = current_hour in [10, 11]
        
        # Route distribution (popular routes get more traffic)
        route_weights = {
            TrainRoute.MUMBAI_DELHI: 0.25,
            TrainRoute.DELHI_MUMBAI: 0.25,
            TrainRoute.BANGALORE_DELHI: 0.15,
            TrainRoute.CHENNAI_MUMBAI: 0.10,
            TrainRoute.KOLKATA_DELHI: 0.10,
            TrainRoute.PUNE_DELHI: 0.08,
            TrainRoute.HYDERABAD_MUMBAI: 0.04,
            TrainRoute.AHMEDABAD_MUMBAI: 0.03
        }
        
        route = random.choices(
            list(route_weights.keys()),
            weights=list(route_weights.values())
        )[0]
        
        # Class distribution (AC classes more popular in Tatkal)
        class_weights = {"AC1": 0.05, "AC2": 0.30, "AC3": 0.45, "SL": 0.20}
        booking_class = random.choices(
            list(class_weights.keys()),
            weights=list(class_weights.values())
        )[0]
        
        # Success rate varies by time and class
        base_success_rate = 0.15 if self.is_peak_hour else 0.60
        if booking_class in ["AC1", "AC2"]:
            base_success_rate += 0.10  # Premium classes have better success rate
        
        success = random.random() < base_success_rate
        status = IRCTCBookingStatus.SUCCESS if success else random.choice([
            IRCTCBookingStatus.FAILED,
            IRCTCBookingStatus.TIMEOUT,
            IRCTCBookingStatus.QUEUE_FULL,
            IRCTCBookingStatus.PAYMENT_FAILED
        ])
        
        # Timing simulation
        if self.is_peak_hour:
            wait_time = random.uniform(30, 300)    # 30 seconds to 5 minutes
            payment_time = random.uniform(10, 60)  # 10 seconds to 1 minute
        else:
            wait_time = random.uniform(5, 30)      # 5 to 30 seconds
            payment_time = random.uniform(5, 20)   # 5 to 20 seconds
        
        total_time = wait_time + payment_time
        
        # Queue position for peak hours
        queue_position = random.randint(1, 50000) if self.is_peak_hour else None
        
        cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Pune", "Hyderabad", "Ahmedabad", "Jaipur", "Lucknow"
        ]
        
        return IRCTCBookingEvent(
            booking_id=f"IRB{int(time.time())}{random.randint(1000, 9999)}",
            user_id=f"U{random.randint(100000, 999999)}",
            train_number=f"{random.randint(12000, 22000)}",
            route=route,
            booking_class=booking_class,
            journey_date=(datetime.now() + timedelta(days=random.randint(1, 120))).strftime("%Y-%m-%d"),
            booking_status=status,
            queue_position=queue_position,
            wait_time_seconds=wait_time,
            payment_time_seconds=payment_time,
            total_time_seconds=total_time,
            user_agent=random.choice(["mobile_app", "web_browser", "mobile_web"]),
            user_city=random.choice(cities),
            retry_attempt=random.randint(0, 5) if not success else 0
        )
    
    def update_concurrent_metrics(self):
        """
        Concurrent users और queue depth update करता है
        """
        if self.is_peak_hour:
            self.concurrent_users = random.randint(800000, 1200000)  # 8-12 lakh users
            self.queue_depth = random.randint(2000, 10000)
        else:
            self.concurrent_users = random.randint(50000, 200000)    # 50k-2 lakh users
            self.queue_depth = random.randint(100, 1000)

class IRCTCDashboardManager:
    """
    Complete IRCTC dashboard management system
    Creation, updates, और monitoring के लिए
    """
    
    def __init__(self, grafana_url: str = "http://localhost:3000"):
        self.dashboard = GrafanaIRCTCDashboard(grafana_url=grafana_url)
        self.simulator = IRCTCMetricsSimulator()
        self.running = False
        
    async def setup_complete_monitoring(self):
        """
        Complete IRCTC monitoring setup करता है
        Dashboard creation से लेकर data simulation तक
        """
        print("🚀 Setting up IRCTC Tatkal Monitoring Dashboard")
        
        try:
            # Create/update dashboard
            result = self.dashboard.create_irctc_dashboard()
            print(f"✅ Dashboard created: {result.get('url', 'Unknown URL')}")
            
            # Setup datasource if needed
            await self._setup_prometheus_datasource()
            
            # Start metrics simulation
            print("📊 Starting metrics simulation...")
            await self._start_metrics_simulation()
            
        except Exception as e:
            logger.error("Failed to setup IRCTC monitoring", error=str(e))
            raise

    async def _setup_prometheus_datasource(self):
        """
        Prometheus datasource setup करता है अगर exist नहीं करता
        """
        try:
            datasources = self.dashboard.grafana.datasource.list_datasources()
            prometheus_exists = any(ds['type'] == 'prometheus' for ds in datasources)
            
            if not prometheus_exists:
                datasource_config = {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "url": "http://localhost:9090",
                    "access": "proxy",
                    "isDefault": True
                }
                
                self.dashboard.grafana.datasource.create_datasource(datasource_config)
                logger.info("Prometheus datasource created")
            else:
                logger.info("Prometheus datasource already exists")
                
        except Exception as e:
            logger.warning("Could not setup datasource", error=str(e))

    async def _start_metrics_simulation(self):
        """
        Metrics simulation start करता है
        Realistic IRCTC data के साथ
        """
        self.running = True
        
        while self.running:
            try:
                # Generate booking events
                for _ in range(random.randint(1, 20)):  # Burst traffic simulation
                    event = self.simulator.generate_booking_event()
                    
                    # Log event for metrics collection
                    logger.info("IRCTC booking event", 
                               booking_id=event.booking_id,
                               route=event.route.value,
                               status=event.booking_status.value,
                               total_time=event.total_time_seconds)
                
                # Update concurrent metrics
                self.simulator.update_concurrent_metrics()
                
                # Sleep based on peak hour
                if self.simulator.is_peak_hour:
                    await asyncio.sleep(0.1)  # High frequency during peak
                else:
                    await asyncio.sleep(1.0)   # Normal frequency
                    
            except Exception as e:
                logger.error("Metrics simulation error", error=str(e))
                await asyncio.sleep(1)

    def stop_monitoring(self):
        """Monitoring को gracefully stop करता है"""
        self.running = False
        logger.info("IRCTC monitoring stopped")

def main():
    """
    Main function - IRCTC dashboard setup और monitoring
    """
    print("🚄 IRCTC Tatkal Booking Dashboard Setup")
    print("📊 Setting up comprehensive monitoring for Indian Railways")
    print("🕙 Special focus on 10 AM Tatkal rush hour")
    print("🗺️ Regional performance tracking across Indian cities")
    print("\nDashboard Features:")
    print("  ✅ Real-time booking success rates")
    print("  ✅ Queue depth monitoring")
    print("  ✅ Route-wise performance analysis")
    print("  ✅ Payment gateway tracking")
    print("  ✅ Regional performance heatmap")
    print("  ✅ Peak hour analysis (10-11 AM)")
    print("\nAccess URLs:")
    print("  📊 Grafana Dashboard: http://localhost:3000")
    print("  🔧 Prometheus Metrics: http://localhost:9090")
    print("\nPress Ctrl+C to stop\n")
    
    manager = IRCTCDashboardManager()
    
    try:
        asyncio.run(manager.setup_complete_monitoring())
    except KeyboardInterrupt:
        print("\n🛑 Stopping IRCTC monitoring...")
        manager.stop_monitoring()
        print("✅ Monitoring stopped successfully!")

if __name__ == "__main__":
    main()

"""
Production Deployment Guide:

1. Grafana Configuration:
   - Set proper admin credentials
   - Configure SMTP for alerting
   - Setup user roles and permissions
   - Enable anonymous access if needed

2. Dashboard Customization:
   - Adjust time ranges for Indian timezone
   - Add custom annotations for maintenance
   - Configure alert rules for critical metrics
   - Setup dashboard links for drill-down

3. Metrics Collection:
   - Deploy Prometheus to collect IRCTC metrics
   - Configure service discovery for IRCTC endpoints
   - Set appropriate scrape intervals
   - Setup long-term storage with Thanos

4. Alerting Rules:
   - Booking success rate < 70%
   - Queue depth > 10,000 users
   - Response time > 3 minutes
   - Payment gateway failures > 5%

5. Indian Context Features:
   - IST timezone configuration
   - Regional performance tracking
   - Festival season alert adjustments
   - Multi-language error categorization

6. Performance Optimization:
   - Dashboard variable caching
   - Query optimization for large datasets
   - Panel refresh rate configuration
   - Resource limit settings

Example Alert Rules (Grafana):
```yaml
- alert: IRCTCBookingSuccessRateLow
  expr: rate(irctc_bookings_total{status="success"}[5m]) / rate(irctc_bookings_total[5m]) * 100 < 70
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "IRCTC booking success rate is below 70%"

- alert: IRCTCQueueDepthHigh
  expr: irctc_queue_depth > 10000
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "IRCTC queue depth is very high ({{$value}} users)"
```

Dashboard Export:
The dashboard JSON can be exported and version controlled for deployment automation.
"""