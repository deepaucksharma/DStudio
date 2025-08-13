#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Logging and Monitoring Stack for Container Orchestration
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे Nykaa जैसी e-commerce companies
production में container logging और monitoring करती हैं।

Real-world scenario: Nykaa का comprehensive observability stack
"""

import os
import json
import time
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from loguru import logger
import requests
import yaml
from elasticsearch import Elasticsearch
import redis
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary, start_http_server
import threading

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: LogLevel
    service: str
    container_id: str
    message: str
    user_id: Optional[str]
    session_id: Optional[str]
    trace_id: Optional[str]
    span_id: Optional[str]
    environment: str
    region: str
    additional_fields: Dict[str, Any]

@dataclass
class MetricDefinition:
    """Metric definition structure"""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str]
    unit: str

class NykaaObservabilityStack:
    """
    Nykaa-style Comprehensive Observability Stack
    Production-ready logging, monitoring, and alerting for containers
    """
    
    def __init__(self):
        # Elasticsearch for centralized logging
        self.elasticsearch_client = None
        try:
            self.elasticsearch_client = Elasticsearch([
                {'host': 'localhost', 'port': 9200}
            ])
            logger.info("✅ Connected to Elasticsearch")
        except Exception as e:
            logger.warning(f"Failed to connect to Elasticsearch: {str(e)}")
        
        # Redis for metrics caching and real-time data
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            self.redis_client.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {str(e)}")
        
        # Prometheus metrics registry
        self.metrics_registry = CollectorRegistry()
        self.setup_prometheus_metrics()
        
        # Indian e-commerce specific service metrics
        self.nykaa_services = {
            "beauty-catalog": {
                "critical_metrics": ["product_views", "search_queries", "cart_additions"],
                "business_metrics": ["conversion_rate", "average_order_value", "inventory_levels"],
                "performance_metrics": ["response_time", "database_queries", "cache_hit_rate"]
            },
            "fashion-catalog": {
                "critical_metrics": ["product_recommendations", "wishlist_additions", "size_guide_views"],
                "business_metrics": ["category_performance", "brand_engagement", "return_rate"],
                "performance_metrics": ["image_load_time", "search_latency", "recommendation_accuracy"]
            },
            "payment-service": {
                "critical_metrics": ["payment_attempts", "payment_success", "payment_failures"],
                "business_metrics": ["payment_method_usage", "transaction_value", "refund_requests"],
                "performance_metrics": ["payment_gateway_latency", "fraud_detection_time", "webhook_delivery"]
            },
            "order-management": {
                "critical_metrics": ["order_creation", "order_fulfillment", "delivery_tracking"],
                "business_metrics": ["order_value", "delivery_time", "customer_satisfaction"],
                "performance_metrics": ["warehouse_efficiency", "shipping_api_latency", "inventory_sync"]
            },
            "user-service": {
                "critical_metrics": ["user_registrations", "login_attempts", "profile_updates"],
                "business_metrics": ["user_engagement", "session_duration", "feature_adoption"],
                "performance_metrics": ["authentication_time", "session_management", "personalization_latency"]
            }
        }
        
        # Indian region-specific configurations
        self.regional_configs = {
            "mumbai": {
                "log_retention_days": 30,
                "metric_resolution": "1m",
                "alert_latency_ms": 100
            },
            "bangalore": {
                "log_retention_days": 30,
                "metric_resolution": "1m", 
                "alert_latency_ms": 120
            },
            "delhi": {
                "log_retention_days": 30,
                "metric_resolution": "1m",
                "alert_latency_ms": 150
            }
        }
        
        # Alert thresholds for Nykaa business metrics
        self.alert_thresholds = {
            "error_rate": 5.0,           # 5% error rate
            "response_time_p95": 2000,   # 2 seconds 95th percentile
            "conversion_rate_drop": 10,  # 10% drop in conversion
            "payment_failure_rate": 3.0, # 3% payment failure rate
            "inventory_low": 10,         # 10 items remaining
            "user_engagement_drop": 15   # 15% drop in engagement
        }
        
        # Log aggregation patterns
        self.log_patterns = {
            "business_events": [
                "product_view", "add_to_cart", "checkout_start", "payment_complete",
                "order_placed", "delivery_scheduled", "review_submitted"
            ],
            "security_events": [
                "login_failure", "account_lockout", "suspicious_activity",
                "fraud_detected", "unauthorized_access", "data_breach_attempt"
            ],
            "performance_events": [
                "slow_query", "high_memory_usage", "cpu_spike",
                "cache_miss", "api_timeout", "database_connection_error"
            ]
        }
        
        logger.info("👗 Nykaa Observability Stack initialized!")
        logger.info("Production-ready logging and monitoring ready!")
    
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics for Nykaa services"""
        
        # Business metrics
        self.product_views = Counter(
            'nykaa_product_views_total',
            'Total product views',
            ['product_category', 'brand', 'region'],
            registry=self.metrics_registry
        )
        
        self.order_value = Histogram(
            'nykaa_order_value_inr',
            'Order value in INR',
            ['payment_method', 'category', 'region'],
            buckets=[100, 500, 1000, 2000, 5000, 10000, 20000, 50000],
            registry=self.metrics_registry
        )
        
        self.conversion_rate = Gauge(
            'nykaa_conversion_rate_percent',
            'Conversion rate percentage',
            ['category', 'region', 'device_type'],
            registry=self.metrics_registry
        )
        
        # Performance metrics
        self.api_response_time = Histogram(
            'nykaa_api_response_time_seconds',
            'API response time in seconds',
            ['service', 'endpoint', 'method', 'region'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.metrics_registry
        )
        
        self.database_connections = Gauge(
            'nykaa_database_connections_active',
            'Active database connections',
            ['service', 'database_type', 'region'],
            registry=self.metrics_registry
        )
        
        self.cache_hit_rate = Gauge(
            'nykaa_cache_hit_rate_percent',
            'Cache hit rate percentage',
            ['service', 'cache_type', 'region'],
            registry=self.metrics_registry
        )
        
        # Error metrics
        self.error_count = Counter(
            'nykaa_errors_total',
            'Total error count',
            ['service', 'error_type', 'severity', 'region'],
            registry=self.metrics_registry
        )
        
        self.payment_failures = Counter(
            'nykaa_payment_failures_total',
            'Total payment failures',
            ['payment_gateway', 'failure_reason', 'region'],
            registry=self.metrics_registry
        )
        
        # User engagement metrics
        self.user_sessions = Counter(
            'nykaa_user_sessions_total',
            'Total user sessions',
            ['device_type', 'channel', 'region'],
            registry=self.metrics_registry
        )
        
        self.session_duration = Histogram(
            'nykaa_session_duration_minutes',
            'User session duration in minutes',
            ['user_segment', 'device_type', 'region'],
            buckets=[1, 5, 10, 20, 30, 60, 120],
            registry=self.metrics_registry
        )
        
        # Inventory metrics
        self.inventory_levels = Gauge(
            'nykaa_inventory_levels',
            'Current inventory levels',
            ['product_id', 'warehouse', 'category'],
            registry=self.metrics_registry
        )
        
        logger.info("📊 Prometheus metrics configured for Nykaa services")
    
    def create_log_entry(self, level: LogLevel, service: str, message: str, 
                        container_id: str = "unknown", **kwargs) -> LogEntry:
        """Create structured log entry"""
        
        return LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            service=service,
            container_id=container_id,
            message=message,
            user_id=kwargs.get('user_id'),
            session_id=kwargs.get('session_id'),
            trace_id=kwargs.get('trace_id'),
            span_id=kwargs.get('span_id'),
            environment=kwargs.get('environment', 'production'),
            region=kwargs.get('region', 'mumbai'),
            additional_fields=kwargs.get('additional_fields', {})
        )
    
    def send_log_to_elasticsearch(self, log_entry: LogEntry):
        """Send log entry to Elasticsearch"""
        
        if not self.elasticsearch_client:
            logger.warning("Elasticsearch not available, logging to console")
            print(f"LOG: {json.dumps(asdict(log_entry), indent=2)}")
            return
        
        try:
            # Create index name with date for daily rotation
            index_name = f"nykaa-logs-{datetime.now().strftime('%Y-%m-%d')}"
            
            # Send to Elasticsearch
            self.elasticsearch_client.index(
                index=index_name,
                body=asdict(log_entry)
            )
            
            # Cache recent logs in Redis for real-time dashboard
            if self.redis_client:
                log_key = f"recent_logs:{log_entry.service}:{log_entry.level.value}"
                self.redis_client.lpush(log_key, json.dumps(asdict(log_entry)))
                self.redis_client.ltrim(log_key, 0, 99)  # Keep last 100 logs
                self.redis_client.expire(log_key, 3600)  # 1 hour expiry
            
        except Exception as e:
            logger.error(f"Failed to send log to Elasticsearch: {str(e)}")
    
    def log_business_event(self, event_type: str, **event_data):
        """Log business-specific events for Nykaa"""
        
        # Map event types to services
        service_mapping = {
            "product_view": "beauty-catalog",
            "add_to_cart": "beauty-catalog",
            "checkout_start": "payment-service",
            "payment_complete": "payment-service",
            "order_placed": "order-management",
            "delivery_scheduled": "order-management"
        }
        
        service = service_mapping.get(event_type, "unknown-service")
        
        log_entry = self.create_log_entry(
            level=LogLevel.INFO,
            service=service,
            message=f"Business event: {event_type}",
            additional_fields={
                "event_type": event_type,
                "event_data": event_data,
                "business_impact": True
            },
            **event_data
        )
        
        self.send_log_to_elasticsearch(log_entry)
        
        # Update corresponding metrics
        if event_type == "product_view":
            self.product_views.labels(
                product_category=event_data.get('category', 'unknown'),
                brand=event_data.get('brand', 'unknown'),
                region=event_data.get('region', 'mumbai')
            ).inc()
        
        elif event_type == "payment_complete":
            order_value = event_data.get('order_value', 0)
            self.order_value.labels(
                payment_method=event_data.get('payment_method', 'unknown'),
                category=event_data.get('category', 'unknown'),
                region=event_data.get('region', 'mumbai')
            ).observe(order_value)
        
        elif event_type == "user_session_start":
            self.user_sessions.labels(
                device_type=event_data.get('device_type', 'unknown'),
                channel=event_data.get('channel', 'web'),
                region=event_data.get('region', 'mumbai')
            ).inc()
    
    def log_performance_metric(self, service: str, metric_name: str, value: float, **labels):
        """Log performance metrics"""
        
        log_entry = self.create_log_entry(
            level=LogLevel.DEBUG,
            service=service,
            message=f"Performance metric: {metric_name} = {value}",
            additional_fields={
                "metric_name": metric_name,
                "metric_value": value,
                "metric_labels": labels,
                "performance_data": True
            }
        )
        
        self.send_log_to_elasticsearch(log_entry)
        
        # Update Prometheus metrics
        if metric_name == "api_response_time":
            self.api_response_time.labels(
                service=service,
                endpoint=labels.get('endpoint', 'unknown'),
                method=labels.get('method', 'GET'),
                region=labels.get('region', 'mumbai')
            ).observe(value)
        
        elif metric_name == "database_connections":
            self.database_connections.labels(
                service=service,
                database_type=labels.get('database_type', 'postgres'),
                region=labels.get('region', 'mumbai')
            ).set(value)
        
        elif metric_name == "cache_hit_rate":
            self.cache_hit_rate.labels(
                service=service,
                cache_type=labels.get('cache_type', 'redis'),
                region=labels.get('region', 'mumbai')
            ).set(value)
    
    def log_error(self, service: str, error_type: str, error_message: str, 
                  severity: str = "ERROR", **context):
        """Log error events with context"""
        
        log_entry = self.create_log_entry(
            level=LogLevel.ERROR if severity == "ERROR" else LogLevel.CRITICAL,
            service=service,
            message=f"Error: {error_message}",
            additional_fields={
                "error_type": error_type,
                "error_message": error_message,
                "severity": severity,
                "context": context,
                "stack_trace": context.get('stack_trace'),
                "error_code": context.get('error_code')
            },
            **context
        )
        
        self.send_log_to_elasticsearch(log_entry)
        
        # Update error metrics
        self.error_count.labels(
            service=service,
            error_type=error_type,
            severity=severity,
            region=context.get('region', 'mumbai')
        ).inc()
        
        # Special handling for payment failures
        if service == "payment-service" and error_type == "payment_failure":
            self.payment_failures.labels(
                payment_gateway=context.get('payment_gateway', 'unknown'),
                failure_reason=context.get('failure_reason', 'unknown'),
                region=context.get('region', 'mumbai')
            ).inc()
    
    def create_dashboard_queries(self) -> Dict[str, str]:
        """Create Elasticsearch queries for Nykaa dashboard"""
        
        queries = {
            # Business metrics queries
            "top_products": '''
            {
              "size": 0,
              "query": {
                "bool": {
                  "filter": [
                    {"range": {"timestamp": {"gte": "now-1h"}}},
                    {"term": {"additional_fields.event_type": "product_view"}}
                  ]
                }
              },
              "aggs": {
                "top_products": {
                  "terms": {
                    "field": "additional_fields.event_data.product_id.keyword",
                    "size": 10
                  }
                }
              }
            }
            ''',
            
            "conversion_funnel": '''
            {
              "size": 0,
              "query": {
                "bool": {
                  "filter": [
                    {"range": {"timestamp": {"gte": "now-24h"}}}
                  ]
                }
              },
              "aggs": {
                "funnel_steps": {
                  "filters": {
                    "filters": {
                      "product_views": {"term": {"additional_fields.event_type": "product_view"}},
                      "cart_additions": {"term": {"additional_fields.event_type": "add_to_cart"}},
                      "checkout_starts": {"term": {"additional_fields.event_type": "checkout_start"}},
                      "payments": {"term": {"additional_fields.event_type": "payment_complete"}}
                    }
                  }
                }
              }
            }
            ''',
            
            "error_analysis": '''
            {
              "size": 0,
              "query": {
                "bool": {
                  "filter": [
                    {"range": {"timestamp": {"gte": "now-1h"}}},
                    {"terms": {"level": ["ERROR", "CRITICAL"]}}
                  ]
                }
              },
              "aggs": {
                "errors_by_service": {
                  "terms": {"field": "service.keyword"},
                  "aggs": {
                    "error_types": {
                      "terms": {"field": "additional_fields.error_type.keyword"}
                    }
                  }
                }
              }
            }
            ''',
            
            "performance_trends": '''
            {
              "size": 0,
              "query": {
                "bool": {
                  "filter": [
                    {"range": {"timestamp": {"gte": "now-6h"}}},
                    {"term": {"additional_fields.performance_data": true}}
                  ]
                }
              },
              "aggs": {
                "performance_over_time": {
                  "date_histogram": {
                    "field": "timestamp",
                    "interval": "10m"
                  },
                  "aggs": {
                    "avg_response_time": {
                      "avg": {"field": "additional_fields.metric_value"}
                    }
                  }
                }
              }
            }
            '''
        }
        
        return queries
    
    def setup_alerting_rules(self) -> Dict[str, Dict]:
        """Setup alerting rules for Nykaa services"""
        
        alerting_rules = {
            "high_error_rate": {
                "condition": "error_rate > 5%",
                "query": '''
                  rate(nykaa_errors_total[5m]) / 
                  rate(nykaa_api_requests_total[5m]) * 100 > 5
                ''',
                "severity": "warning",
                "notification_channels": ["slack", "pagerduty"],
                "runbook": "https://nykaa.com/runbooks/high-error-rate"
            },
            
            "payment_failure_spike": {
                "condition": "payment_failure_rate > 3%",
                "query": '''
                  rate(nykaa_payment_failures_total[5m]) /
                  rate(nykaa_payment_attempts_total[5m]) * 100 > 3
                ''',
                "severity": "critical",
                "notification_channels": ["slack", "pagerduty", "email"],
                "runbook": "https://nykaa.com/runbooks/payment-failures"
            },
            
            "low_inventory_alert": {
                "condition": "inventory < 10 units",
                "query": "nykaa_inventory_levels < 10",
                "severity": "warning",
                "notification_channels": ["slack", "email"],
                "runbook": "https://nykaa.com/runbooks/inventory-management"
            },
            
            "high_response_time": {
                "condition": "p95_response_time > 2s",
                "query": '''
                  histogram_quantile(0.95, 
                    rate(nykaa_api_response_time_seconds_bucket[5m])
                  ) > 2
                ''',
                "severity": "warning",
                "notification_channels": ["slack"],
                "runbook": "https://nykaa.com/runbooks/performance-issues"
            },
            
            "conversion_rate_drop": {
                "condition": "conversion_rate drops > 10%",
                "query": '''
                  (
                    avg_over_time(nykaa_conversion_rate_percent[1h]) -
                    avg_over_time(nykaa_conversion_rate_percent[1h] offset 1h)
                  ) / avg_over_time(nykaa_conversion_rate_percent[1h] offset 1h) * 100 < -10
                ''',
                "severity": "critical",
                "notification_channels": ["slack", "pagerduty", "email"],
                "runbook": "https://nykaa.com/runbooks/conversion-issues"
            }
        }
        
        return alerting_rules
    
    def generate_grafana_dashboard(self) -> str:
        """Generate Grafana dashboard configuration for Nykaa"""
        
        dashboard_config = {
            "dashboard": {
                "id": None,
                "title": "Nykaa Container Observability",
                "tags": ["nykaa", "containers", "observability"],
                "timezone": "Asia/Kolkata",
                "panels": [
                    {
                        "id": 1,
                        "title": "Business Metrics",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(rate(nykaa_product_views_total[5m]))",
                                "legendFormat": "Product Views/sec"
                            },
                            {
                                "expr": "sum(rate(nykaa_order_value_inr_sum[5m]))",
                                "legendFormat": "Revenue/sec (INR)"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "short"
                            }
                        }
                    },
                    
                    {
                        "id": 2,
                        "title": "Conversion Funnel",
                        "type": "bargauge",
                        "targets": [
                            {
                                "expr": "sum by (step) (nykaa_conversion_funnel)",
                                "legendFormat": "{{step}}"
                            }
                        ]
                    },
                    
                    {
                        "id": 3,
                        "title": "API Response Time (95th percentile)",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": '''histogram_quantile(0.95, 
                                         sum(rate(nykaa_api_response_time_seconds_bucket[5m])) 
                                         by (le, service))''',
                                "legendFormat": "{{service}}"
                            }
                        ]
                    },
                    
                    {
                        "id": 4,
                        "title": "Error Rate by Service",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": '''sum(rate(nykaa_errors_total[5m])) by (service) /
                                         sum(rate(nykaa_api_requests_total[5m])) by (service) * 100''',
                                "legendFormat": "{{service}}"
                            }
                        ]
                    },
                    
                    {
                        "id": 5,
                        "title": "Payment Method Distribution",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sum by (payment_method) (nykaa_order_value_inr_count)",
                                "legendFormat": "{{payment_method}}"
                            }
                        ]
                    },
                    
                    {
                        "id": 6,
                        "title": "Inventory Levels (Low Stock)",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "nykaa_inventory_levels < 50",
                                "legendFormat": "{{product_id}} - {{warehouse}}"
                            }
                        ]
                    }
                ]
            }
        }
        
        return json.dumps(dashboard_config, indent=2)
    
    def simulate_nykaa_traffic(self):
        """Simulate realistic Nykaa traffic patterns"""
        
        import random
        import time
        
        # Simulate different types of events
        events = [
            ("product_view", {"category": "makeup", "brand": "nykaa", "product_id": "NK001"}),
            ("add_to_cart", {"category": "skincare", "brand": "loreal", "product_id": "NK002"}),
            ("checkout_start", {"cart_value": 2500, "items_count": 3}),
            ("payment_complete", {"order_value": 2500, "payment_method": "upi"}),
            ("user_session_start", {"device_type": "mobile", "channel": "app"})
        ]
        
        # Simulate performance metrics
        services = ["beauty-catalog", "fashion-catalog", "payment-service", "order-management"]
        
        while True:
            # Log business events
            event_type, event_data = random.choice(events)
            event_data["region"] = random.choice(["mumbai", "bangalore", "delhi"])
            event_data["user_id"] = f"user_{random.randint(1000, 9999)}"
            
            self.log_business_event(event_type, **event_data)
            
            # Log performance metrics
            service = random.choice(services)
            response_time = random.uniform(0.1, 3.0)
            
            self.log_performance_metric(
                service=service,
                metric_name="api_response_time",
                value=response_time,
                endpoint="/api/products",
                method="GET",
                region=event_data["region"]
            )
            
            # Occasionally log errors
            if random.random() < 0.05:  # 5% chance of error
                self.log_error(
                    service=service,
                    error_type="database_timeout",
                    error_message="Database query timeout after 30 seconds",
                    region=event_data["region"],
                    error_code="DB_TIMEOUT_001"
                )
            
            time.sleep(1)  # 1 event per second

def main():
    """Demonstration of Nykaa observability stack"""
    
    print("👗 Nykaa Observability Stack Demo")
    print("Production-ready logging and monitoring for Indian e-commerce")
    print("=" * 60)
    
    # Initialize observability stack
    observability = NykaaObservabilityStack()
    
    # Start Prometheus metrics server
    start_http_server(8090, registry=observability.metrics_registry)
    logger.info("📊 Prometheus metrics server started on port 8090")
    
    print("\\n🔧 Observability Stack Components:")
    print("  📊 Prometheus metrics: http://localhost:8090/metrics")
    print("  🔍 Elasticsearch indices: nykaa-logs-YYYY-MM-DD")
    print("  💾 Redis caching: recent_logs:*")
    print("  📈 Grafana dashboard: Nykaa Container Observability")
    
    print("\\n📋 Dashboard Queries:")
    queries = observability.create_dashboard_queries()
    for query_name, query in queries.items():
        print(f"  - {query_name}: Ready for Elasticsearch")
    
    print("\\n🚨 Alerting Rules:")
    alerts = observability.setup_alerting_rules()
    for alert_name, alert_config in alerts.items():
        print(f"  - {alert_name}: {alert_config['severity']} ({alert_config['condition']})")
    
    print("\\n📊 Grafana Dashboard:")
    dashboard_json = observability.generate_grafana_dashboard()
    print("  Dashboard configuration generated (JSON format)")
    
    print("\\n🎯 Simulating Nykaa traffic...")
    
    # Simulate some traffic for demo
    for i in range(10):
        # Business events
        observability.log_business_event(
            "product_view",
            category="makeup",
            brand="nykaa",
            product_id=f"NK00{i+1}",
            region="mumbai",
            user_id=f"user_{1000+i}"
        )
        
        # Performance metrics
        observability.log_performance_metric(
            service="beauty-catalog",
            metric_name="api_response_time",
            value=0.5 + (i * 0.1),
            endpoint="/api/products",
            method="GET",
            region="mumbai"
        )
        
        # Occasional error
        if i == 7:
            observability.log_error(
                service="payment-service",
                error_type="payment_gateway_timeout",
                error_message="Payment gateway timeout after 30 seconds",
                region="mumbai",
                payment_gateway="razorpay",
                error_code="PG_TIMEOUT_001"
            )
        
        time.sleep(0.5)
    
    print("\\n✅ Traffic simulation completed!")
    print("\\n📊 Metrics Summary:")
    print("  - 10 product views logged")
    print("  - 10 performance metrics recorded")
    print("  - 1 error event logged")
    print("  - All data available in Elasticsearch and Prometheus")

if __name__ == "__main__":
    main()

# Production Deployment Guide:
"""
# 1. Elasticsearch deployment:
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch \\
  --set replicas=3 \\
  --set volumeClaimTemplate.resources.requests.storage=100Gi

# 2. Prometheus deployment:
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# 3. Grafana configuration:
# Import dashboard JSON from generate_grafana_dashboard()

# 4. Fluentd for log collection:
helm install fluentd stable/fluentd-elasticsearch \\
  --set elasticsearch.host=elasticsearch \\
  --set elasticsearch.port=9200

# 5. Alert manager configuration:
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      slack_api_url: 'https://hooks.slack.com/services/nykaa/alerts'
    route:
      group_by: ['alertname']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'nykaa-alerts'
    receivers:
    - name: 'nykaa-alerts'
      slack_configs:
      - channel: '#nykaa-alerts'
        title: 'Nykaa Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
EOF

# 6. Container log shipping:
# Add to Dockerfile:
# COPY fluentd.conf /fluentd/etc/
# Configure log drivers in Kubernetes:
# spec.containers[].env:
# - name: FLUENTD_CONF
#   value: "fluentd.conf"
"""