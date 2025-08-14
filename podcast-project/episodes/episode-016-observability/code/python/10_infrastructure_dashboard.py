#!/usr/bin/env python3
"""
Episode 16: Observability & Monitoring
Example 10: Infrastructure Dashboard for Indian Scale

भारतीय context: IRCTC जैसे massive scale infrastructure monitoring
जैसे 10 AM Tatkal booking के time infrastructure health track करना

Real-world scenario: Flipkart BBD infrastructure dashboard
Challenge: Multi-region, multi-cloud, vendor diversity, cost optimization
"""

import time
import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import structlog

# भारतीय infrastructure components और cloud providers
class InfrastructureComponent(Enum):
    """Infrastructure components for Indian scale"""
    LOAD_BALANCER = "load_balancer"          # ELB, ALB, HAProxy
    WEB_SERVER = "web_server"                # Nginx, Apache
    APPLICATION_SERVER = "application_server" # Tomcat, Gunicorn
    DATABASE = "database"                    # MySQL, PostgreSQL, MongoDB
    CACHE = "cache"                          # Redis, Memcached
    MESSAGE_QUEUE = "message_queue"          # Kafka, RabbitMQ, SQS
    STORAGE = "storage"                      # S3, EBS, local storage
    CONTAINER = "container"                  # Docker, Kubernetes pods
    NETWORK = "network"                      # VPC, subnets, security groups
    CDN = "cdn"                             # CloudFront, KeyCDN

class CloudProvider(Enum):
    """Cloud providers popular in India"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    JIOCLOUD = "jiocloud"
    TATACLOUD = "tatacloud"
    ON_PREMISE = "on_premise"

class Region(Enum):
    """Indian regions and availability zones"""
    MUMBAI_AZ1 = "mumbai_az1"
    MUMBAI_AZ2 = "mumbai_az2"
    BANGALORE_AZ1 = "bangalore_az1"
    BANGALORE_AZ2 = "bangalore_az2"
    DELHI_AZ1 = "delhi_az1"
    DELHI_AZ2 = "delhi_az2"
    CHENNAI_AZ1 = "chennai_az1"
    HYDERABAD_AZ1 = "hyderabad_az1"

@dataclass
class InfrastructureMetric:
    """Infrastructure metric definition"""
    component_id: str
    component_type: InfrastructureComponent
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    region: Region
    cloud_provider: CloudProvider
    tags: Dict[str, str] = field(default_factory=dict)
    threshold_config: Dict[str, float] = field(default_factory=dict)

@dataclass
class InfrastructureAlert:
    """Infrastructure alert definition"""
    alert_id: str
    component_id: str
    alert_type: str
    severity: str  # critical, high, medium, low
    message: str
    timestamp: datetime
    auto_remediation_attempted: bool = False
    business_impact: str = "unknown"

class IndianInfrastructureDashboard:
    """
    Indian Scale Infrastructure Dashboard
    
    Features:
    - Multi-region infrastructure monitoring
    - Cloud provider cost tracking
    - Festival season capacity planning
    - Auto-remediation for common issues
    - Business impact assessment
    - Compliance monitoring (data localization)
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.current_time = datetime.now()
        
        # Infrastructure topology
        self.infrastructure_topology = self._initialize_infrastructure_topology()
        
        # Metrics storage (in production, use InfluxDB/Prometheus)
        self.metrics_storage = defaultdict(lambda: deque(maxlen=1440))  # 24 hours at 1-min resolution
        self.alerts_storage = deque(maxlen=10000)
        
        # Thresholds and configurations
        self.monitoring_config = self._initialize_monitoring_config()
        
        # Business context
        self.business_context = self._initialize_business_context()
        
        # Auto-remediation rules
        self.remediation_rules = self._initialize_auto_remediation()
        
        # Cost tracking
        self.cost_tracking = self._initialize_cost_tracking()
        
        # Logger
        self.logger = structlog.get_logger("indian-infrastructure-dashboard")
        
    def _initialize_infrastructure_topology(self) -> Dict[str, Dict]:
        """Initialize infrastructure topology for Indian scale"""
        
        topology = {
            # Load Balancers (Entry Points)
            "mumbai_alb_1": {
                "component_type": InfrastructureComponent.LOAD_BALANCER,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "capacity": "5000 RPS",
                "cost_per_hour_inr": 250,
                "business_criticality": "critical"
            },
            
            "bangalore_alb_1": {
                "component_type": InfrastructureComponent.LOAD_BALANCER,
                "region": Region.BANGALORE_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "capacity": "3000 RPS",
                "cost_per_hour_inr": 200,
                "business_criticality": "critical"
            },
            
            # Web Servers
            "mumbai_nginx_cluster": {
                "component_type": InfrastructureComponent.WEB_SERVER,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "instance_count": 10,
                "instance_type": "c5.2xlarge",
                "cost_per_hour_inr": 1200,  # 10 instances * ₹120/hour
                "business_criticality": "high"
            },
            
            "bangalore_nginx_cluster": {
                "component_type": InfrastructureComponent.WEB_SERVER,
                "region": Region.BANGALORE_AZ1,
                "cloud_provider": CloudProvider.AZURE,  # Multi-cloud strategy
                "instance_count": 8,
                "instance_type": "Standard_D4s_v3",
                "cost_per_hour_inr": 960,  # 8 instances * ₹120/hour
                "business_criticality": "high"
            },
            
            # Application Servers
            "mumbai_app_servers": {
                "component_type": InfrastructureComponent.APPLICATION_SERVER,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "instance_count": 20,
                "instance_type": "m5.xlarge",
                "cost_per_hour_inr": 2400,  # 20 instances * ₹120/hour
                "business_criticality": "critical",
                "auto_scaling": True,
                "min_instances": 10,
                "max_instances": 50
            },
            
            # Databases
            "mumbai_mysql_primary": {
                "component_type": InfrastructureComponent.DATABASE,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "db_type": "MySQL 8.0",
                "instance_type": "db.r5.8xlarge",
                "storage_gb": 2000,
                "cost_per_hour_inr": 800,
                "business_criticality": "critical",
                "backup_enabled": True,
                "multi_az": True
            },
            
            "bangalore_mysql_replica": {
                "component_type": InfrastructureComponent.DATABASE,
                "region": Region.BANGALORE_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "db_type": "MySQL 8.0 Read Replica",
                "instance_type": "db.r5.4xlarge",
                "cost_per_hour_inr": 400,
                "business_criticality": "high",
                "read_only": True
            },
            
            # Cache Layers
            "mumbai_redis_cluster": {
                "component_type": InfrastructureComponent.CACHE,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "cache_type": "Redis 7.0",
                "node_count": 3,
                "node_type": "cache.r6g.2xlarge",
                "cost_per_hour_inr": 600,  # 3 nodes * ₹200/hour
                "business_criticality": "high",
                "memory_gb": 52  # Per node
            },
            
            # Message Queues
            "kafka_cluster": {
                "component_type": InfrastructureComponent.MESSAGE_QUEUE,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "queue_type": "Apache Kafka",
                "broker_count": 3,
                "instance_type": "kafka.m5.2xlarge",
                "cost_per_hour_inr": 900,  # 3 brokers * ₹300/hour
                "business_criticality": "critical",
                "topics": ["orders", "payments", "notifications", "analytics"]
            },
            
            # Storage
            "mumbai_s3_bucket": {
                "component_type": InfrastructureComponent.STORAGE,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "storage_type": "S3 Standard",
                "size_gb": 50000,  # 50 TB
                "cost_per_gb_inr": 0.023,  # ₹0.023 per GB per month
                "business_criticality": "medium",
                "compliance": "data_localization_india"
            },
            
            # CDN
            "cloudfront_distribution": {
                "component_type": InfrastructureComponent.CDN,
                "region": "global",
                "cloud_provider": CloudProvider.AWS,
                "edge_locations": ["mumbai", "bangalore", "delhi", "chennai"],
                "cost_per_gb_inr": 0.085,  # Data transfer cost
                "business_criticality": "high",
                "cache_hit_rate_target": 85
            },
            
            # Kubernetes Clusters
            "mumbai_k8s_cluster": {
                "component_type": InfrastructureComponent.CONTAINER,
                "region": Region.MUMBAI_AZ1,
                "cloud_provider": CloudProvider.AWS,
                "cluster_type": "EKS",
                "node_count": 15,
                "node_type": "m5.2xlarge",
                "cost_per_hour_inr": 1800,  # 15 nodes * ₹120/hour
                "business_criticality": "critical",
                "pods_running": 0,  # Will be populated dynamically
                "namespaces": ["production", "staging", "monitoring"]
            }
        }
        
        return topology
        
    def _initialize_monitoring_config(self) -> Dict[str, Any]:
        """Initialize monitoring configuration and thresholds"""
        
        return {
            "cpu_thresholds": {
                "warning": 70,    # 70% CPU usage warning
                "critical": 85,   # 85% CPU usage critical
                "festival_warning": 80,    # Higher threshold during festivals
                "festival_critical": 90
            },
            
            "memory_thresholds": {
                "warning": 75,
                "critical": 90,
                "festival_warning": 85,
                "festival_critical": 95
            },
            
            "disk_thresholds": {
                "warning": 80,
                "critical": 95,
                "festival_warning": 85,
                "festival_critical": 98
            },
            
            "network_thresholds": {
                "bandwidth_utilization_warning": 70,
                "bandwidth_utilization_critical": 90,
                "packet_loss_warning": 1.0,    # 1% packet loss
                "packet_loss_critical": 5.0,   # 5% packet loss
                "latency_warning_ms": 100,
                "latency_critical_ms": 500
            },
            
            "database_thresholds": {
                "connection_pool_warning": 80,
                "connection_pool_critical": 95,
                "query_latency_warning_ms": 500,
                "query_latency_critical_ms": 2000,
                "replication_lag_warning_sec": 30,
                "replication_lag_critical_sec": 300
            },
            
            "application_thresholds": {
                "response_time_warning_ms": 200,
                "response_time_critical_ms": 1000,
                "error_rate_warning": 5,      # 5% error rate
                "error_rate_critical": 10,    # 10% error rate
                "queue_depth_warning": 1000,
                "queue_depth_critical": 5000
            },
            
            # Festival season adjustments
            "festival_mode": {
                "enabled": False,
                "traffic_multiplier": 1.0,
                "cost_budget_multiplier": 2.0,
                "alert_suppression": False
            }
        }
        
    def _initialize_business_context(self) -> Dict[str, Any]:
        """Initialize business context for impact assessment"""
        
        return {
            "peak_business_hours": {
                "morning": {"start": "09:00", "end": "12:00", "traffic_multiplier": 1.5},
                "afternoon": {"start": "12:00", "end": "15:00", "traffic_multiplier": 1.2},
                "evening": {"start": "18:00", "end": "22:00", "traffic_multiplier": 2.0},
                "night": {"start": "22:00", "end": "02:00", "traffic_multiplier": 0.5}
            },
            
            "revenue_impact_per_minute": {
                "critical_components": 100000,    # ₹1L per minute during outage
                "high_components": 50000,         # ₹50k per minute
                "medium_components": 10000,       # ₹10k per minute
                "low_components": 1000            # ₹1k per minute
            },
            
            "sla_commitments": {
                "api_availability": 99.9,         # 99.9% uptime commitment
                "payment_success_rate": 99.5,     # 99.5% payment success
                "page_load_time_p95": 2000        # P95 under 2 seconds
            },
            
            "compliance_requirements": {
                "data_localization": True,        # RBI mandate
                "audit_logging": True,           # Compliance audit trail
                "encryption_at_rest": True,      # Data protection
                "backup_retention_days": 2555    # 7 years for financial data
            }
        }
        
    def _initialize_auto_remediation(self) -> Dict[str, Dict]:
        """Initialize auto-remediation rules for common issues"""
        
        return {
            "high_cpu_usage": {
                "trigger_threshold": 85,
                "actions": [
                    "scale_out_instances",
                    "restart_high_cpu_processes",
                    "enable_cpu_throttling"
                ],
                "max_attempts": 3,
                "cooldown_minutes": 10
            },
            
            "high_memory_usage": {
                "trigger_threshold": 90,
                "actions": [
                    "clear_application_cache",
                    "restart_memory_leaking_processes",
                    "scale_out_instances"
                ],
                "max_attempts": 2,
                "cooldown_minutes": 5
            },
            
            "database_connection_exhaustion": {
                "trigger_threshold": 95,  # 95% of connection pool used
                "actions": [
                    "kill_long_running_queries",
                    "increase_connection_pool_size",
                    "restart_connection_pool"
                ],
                "max_attempts": 3,
                "cooldown_minutes": 5
            },
            
            "disk_space_critical": {
                "trigger_threshold": 95,
                "actions": [
                    "cleanup_log_files",
                    "cleanup_temp_files",
                    "compress_old_logs",
                    "extend_disk_volume"
                ],
                "max_attempts": 5,
                "cooldown_minutes": 2
            },
            
            "load_balancer_health_check_failures": {
                "trigger_threshold": 50,  # 50% of instances failing
                "actions": [
                    "restart_failing_instances",
                    "route_traffic_to_healthy_region",
                    "scale_out_replacement_instances"
                ],
                "max_attempts": 2,
                "cooldown_minutes": 3
            }
        }
        
    def _initialize_cost_tracking(self) -> Dict[str, Any]:
        """Initialize cost tracking for Indian operations"""
        
        return {
            "monthly_budget_inr": 5000000,  # ₹50L monthly budget
            "current_spend_inr": 0,
            "projected_spend_inr": 0,
            
            "cost_centers": {
                "compute": {"budget_percentage": 40, "current_spend": 0},
                "storage": {"budget_percentage": 20, "current_spend": 0},
                "network": {"budget_percentage": 15, "current_spend": 0},
                "database": {"budget_percentage": 15, "current_spend": 0},
                "monitoring": {"budget_percentage": 5, "current_spend": 0},
                "other": {"budget_percentage": 5, "current_spend": 0}
            },
            
            "cost_optimization_rules": {
                "auto_stop_non_prod_instances": True,
                "right_size_underutilized_instances": True,
                "use_spot_instances_for_batch_jobs": True,
                "implement_data_lifecycle_policies": True,
                "optimize_data_transfer_costs": True
            },
            
            "regional_cost_multipliers": {
                "mumbai": 1.0,      # Base cost
                "bangalore": 0.95,   # Slightly cheaper
                "delhi": 1.05,      # Slightly more expensive
                "tier2_cities": 0.8  # Much cheaper
            }
        }
        
    def collect_infrastructure_metrics(self, component_id: str) -> List[InfrastructureMetric]:
        """Collect comprehensive metrics for infrastructure component"""
        
        if component_id not in self.infrastructure_topology:
            self.logger.warning(f"Unknown component: {component_id}")
            return []
            
        component_config = self.infrastructure_topology[component_id]
        component_type = component_config["component_type"]
        region = component_config.get("region", Region.MUMBAI_AZ1)
        cloud_provider = component_config.get("cloud_provider", CloudProvider.AWS)
        
        current_time = datetime.now()
        metrics = []
        
        # Generate metrics based on component type
        if component_type == InfrastructureComponent.LOAD_BALANCER:
            metrics.extend(self._collect_load_balancer_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.WEB_SERVER:
            metrics.extend(self._collect_web_server_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.APPLICATION_SERVER:
            metrics.extend(self._collect_application_server_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.DATABASE:
            metrics.extend(self._collect_database_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.CACHE:
            metrics.extend(self._collect_cache_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.MESSAGE_QUEUE:
            metrics.extend(self._collect_message_queue_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.STORAGE:
            metrics.extend(self._collect_storage_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.CDN:
            metrics.extend(self._collect_cdn_metrics(component_id, component_config, current_time))
            
        elif component_type == InfrastructureComponent.CONTAINER:
            metrics.extend(self._collect_container_metrics(component_id, component_config, current_time))
        
        # Store metrics
        for metric in metrics:
            self.metrics_storage[f"{component_id}_{metric.metric_name}"].append(metric)
            
        # Check for alerts
        self._check_metric_thresholds(metrics)
        
        return metrics
        
    def _collect_load_balancer_metrics(self, component_id: str, config: Dict, timestamp: datetime) -> List[InfrastructureMetric]:
        """Collect load balancer specific metrics"""
        
        # Simulate realistic load balancer metrics
        base_rps = 1000
        
        # Simulate traffic patterns (higher during business hours)
        hour = timestamp.hour
        if 9 <= hour <= 22:  # Business hours
            traffic_multiplier = 2.0 + random.uniform(-0.5, 0.5)
        else:
            traffic_multiplier = 0.5 + random.uniform(-0.2, 0.2)
            
        current_rps = base_rps * traffic_multiplier
        
        metrics = [
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.LOAD_BALANCER,
                metric_name="requests_per_second",
                value=current_rps,
                unit="rps",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 4000, "critical": 4800}
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.LOAD_BALANCER,
                metric_name="response_time_p95",
                value=random.uniform(50, 200) + (current_rps / 100),  # Latency increases with load
                unit="milliseconds",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 200, "critical": 500}
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.LOAD_BALANCER,
                metric_name="healthy_targets_percentage",
                value=random.uniform(85, 100),  # Simulate occasional unhealthy targets
                unit="percentage",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 90, "critical": 80}
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.LOAD_BALANCER,
                metric_name="ssl_negotiation_errors_per_minute",
                value=random.uniform(0, 10),
                unit="errors_per_minute",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 50, "critical": 100}
            )
        ]
        
        return metrics
        
    def _collect_database_metrics(self, component_id: str, config: Dict, timestamp: datetime) -> List[InfrastructureMetric]:
        """Collect database specific metrics"""
        
        # Simulate database load patterns
        is_read_replica = config.get("read_only", False)
        base_connections = 50 if is_read_replica else 100
        
        metrics = [
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.DATABASE,
                metric_name="cpu_utilization",
                value=random.uniform(30, 85),
                unit="percentage",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 70, "critical": 85}
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.DATABASE,
                metric_name="active_connections",
                value=base_connections + random.uniform(-20, 50),
                unit="connections",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 80, "critical": 95}  # Percentage of max connections
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.DATABASE,
                metric_name="query_latency_p95",
                value=random.uniform(10, 500),
                unit="milliseconds",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 200, "critical": 1000}
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.DATABASE,
                metric_name="slow_queries_per_minute",
                value=random.uniform(0, 20),
                unit="queries_per_minute",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 10, "critical": 50}
            )
        ]
        
        # Add replication lag for read replicas
        if is_read_replica:
            metrics.append(
                InfrastructureMetric(
                    component_id=component_id,
                    component_type=InfrastructureComponent.DATABASE,
                    metric_name="replication_lag",
                    value=random.uniform(0, 60),  # 0-60 seconds lag
                    unit="seconds",
                    timestamp=timestamp,
                    region=config.get("region", Region.MUMBAI_AZ1),
                    cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                    threshold_config={"warning": 30, "critical": 300}
                )
            )
        
        return metrics
        
    def _collect_cache_metrics(self, component_id: str, config: Dict, timestamp: datetime) -> List[InfrastructureMetric]:
        """Collect cache (Redis/Memcached) specific metrics"""
        
        metrics = [
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.CACHE,
                metric_name="cache_hit_rate",
                value=random.uniform(75, 98),  # Good cache hit rate
                unit="percentage",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 80, "critical": 60}  # Below 60% is critical
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.CACHE,
                metric_name="memory_utilization",
                value=random.uniform(40, 85),
                unit="percentage",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 80, "critical": 95}
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.CACHE,
                metric_name="evictions_per_minute",
                value=random.uniform(0, 100),
                unit="evictions_per_minute",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 500, "critical": 2000}
            ),
            
            InfrastructureMetric(
                component_id=component_id,
                component_type=InfrastructureComponent.CACHE,
                metric_name="operations_per_second",
                value=random.uniform(1000, 10000),
                unit="ops_per_second",
                timestamp=timestamp,
                region=config.get("region", Region.MUMBAI_AZ1),
                cloud_provider=config.get("cloud_provider", CloudProvider.AWS),
                threshold_config={"warning": 50000, "critical": 80000}
            )
        ]
        
        return metrics
        
    def _check_metric_thresholds(self, metrics: List[InfrastructureMetric]):
        """Check metrics against thresholds and generate alerts"""
        
        for metric in metrics:
            threshold_config = metric.threshold_config
            
            if not threshold_config:
                continue
                
            # Check critical threshold
            if "critical" in threshold_config:
                critical_threshold = threshold_config["critical"]
                
                # Handle different threshold types
                if metric.metric_name in ["cache_hit_rate", "healthy_targets_percentage"]:
                    # These should be high (above threshold is good)
                    if metric.value < critical_threshold:
                        self._generate_alert(metric, "critical", f"{metric.metric_name} dropped below critical threshold")
                        
                elif metric.metric_name in ["cpu_utilization", "memory_utilization", "replication_lag"]:
                    # These should be low (below threshold is good)
                    if metric.value > critical_threshold:
                        self._generate_alert(metric, "critical", f"{metric.metric_name} exceeded critical threshold")
                        
            # Check warning threshold
            if "warning" in threshold_config:
                warning_threshold = threshold_config["warning"]
                
                if metric.metric_name in ["cache_hit_rate", "healthy_targets_percentage"]:
                    if metric.value < warning_threshold and metric.value >= threshold_config.get("critical", 0):
                        self._generate_alert(metric, "warning", f"{metric.metric_name} dropped below warning threshold")
                        
                elif metric.metric_name in ["cpu_utilization", "memory_utilization", "replication_lag"]:
                    if metric.value > warning_threshold and metric.value < threshold_config.get("critical", 100):
                        self._generate_alert(metric, "warning", f"{metric.metric_name} exceeded warning threshold")
                        
    def _generate_alert(self, metric: InfrastructureMetric, severity: str, message: str):
        """Generate infrastructure alert"""
        
        alert_id = f"alert_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Assess business impact
        component_config = self.infrastructure_topology.get(metric.component_id, {})
        business_criticality = component_config.get("business_criticality", "medium")
        
        alert = InfrastructureAlert(
            alert_id=alert_id,
            component_id=metric.component_id,
            alert_type=f"{metric.metric_name}_{severity}",
            severity=severity,
            message=f"{message}. Current value: {metric.value:.2f} {metric.unit}",
            timestamp=metric.timestamp,
            business_impact=business_criticality
        )
        
        # Store alert
        self.alerts_storage.append(alert)
        
        # Log alert
        self.logger.bind(severity=severity).warning(
            "infrastructure_alert_generated",
            alert_id=alert_id,
            component_id=metric.component_id,
            metric_name=metric.metric_name,
            current_value=metric.value,
            threshold=metric.threshold_config.get(severity, "unknown"),
            business_impact=business_criticality
        )
        
        # Attempt auto-remediation for critical alerts
        if severity == "critical":
            self._attempt_auto_remediation(alert, metric)
            
        return alert
        
    def _attempt_auto_remediation(self, alert: InfrastructureAlert, metric: InfrastructureMetric):
        """Attempt automatic remediation for critical alerts"""
        
        remediation_key = None
        
        # Map metric to remediation rule
        if metric.metric_name == "cpu_utilization" and metric.value > 85:
            remediation_key = "high_cpu_usage"
        elif metric.metric_name == "memory_utilization" and metric.value > 90:
            remediation_key = "high_memory_usage"
        elif metric.metric_name == "active_connections" and metric.value > 95:
            remediation_key = "database_connection_exhaustion"
        elif metric.metric_name == "healthy_targets_percentage" and metric.value < 50:
            remediation_key = "load_balancer_health_check_failures"
            
        if remediation_key and remediation_key in self.remediation_rules:
            remediation_rule = self.remediation_rules[remediation_key]
            
            self.logger.info(
                "auto_remediation_initiated",
                alert_id=alert.alert_id,
                component_id=metric.component_id,
                remediation_rule=remediation_key,
                actions=remediation_rule["actions"]
            )
            
            # Mark remediation attempt
            alert.auto_remediation_attempted = True
            
            # In production, actually execute remediation actions
            # For demo, just simulate
            success_rate = random.uniform(0.6, 0.9)  # 60-90% success rate
            
            if random.random() < success_rate:
                self.logger.info(
                    "auto_remediation_successful",
                    alert_id=alert.alert_id,
                    component_id=metric.component_id
                )
            else:
                self.logger.warning(
                    "auto_remediation_failed",
                    alert_id=alert.alert_id,
                    component_id=metric.component_id,
                    escalation_required=True
                )
                
    def generate_infrastructure_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        
        dashboard_data = {
            "service_name": self.service_name,
            "last_updated": datetime.now().isoformat(),
            "overall_health": self._calculate_overall_health(),
            "component_status": {},
            "regional_breakdown": {},
            "cost_analysis": self._calculate_cost_analysis(),
            "alert_summary": self._get_alert_summary(),
            "business_impact_assessment": self._assess_business_impact(),
            "capacity_planning": self._generate_capacity_planning(),
            "recommendations": []
        }
        
        # Component status
        for component_id, config in self.infrastructure_topology.items():
            # Get latest metrics for this component
            latest_metrics = self._get_latest_metrics_for_component(component_id)
            
            dashboard_data["component_status"][component_id] = {
                "type": config["component_type"].value,
                "region": config.get("region", "unknown"),
                "cloud_provider": config.get("cloud_provider", "unknown"),
                "health_status": self._determine_component_health(latest_metrics),
                "business_criticality": config.get("business_criticality", "medium"),
                "cost_per_hour_inr": config.get("cost_per_hour_inr", 0),
                "latest_metrics": {m.metric_name: {"value": m.value, "unit": m.unit} for m in latest_metrics}
            }
        
        # Regional breakdown
        dashboard_data["regional_breakdown"] = self._generate_regional_breakdown()
        
        # Generate recommendations
        dashboard_data["recommendations"] = self._generate_infrastructure_recommendations(dashboard_data)
        
        return dashboard_data
        
    def _calculate_overall_health(self) -> Dict[str, Any]:
        """Calculate overall infrastructure health score"""
        
        total_components = len(self.infrastructure_topology)
        healthy_components = 0
        critical_alerts = len([a for a in self.alerts_storage if a.severity == "critical"])
        
        # Simplified health calculation
        for component_id in self.infrastructure_topology.keys():
            latest_metrics = self._get_latest_metrics_for_component(component_id)
            if self._determine_component_health(latest_metrics) in ["healthy", "warning"]:
                healthy_components += 1
        
        health_percentage = (healthy_components / total_components) * 100 if total_components > 0 else 100
        
        return {
            "health_percentage": round(health_percentage, 1),
            "status": "healthy" if health_percentage >= 95 else "degraded" if health_percentage >= 80 else "critical",
            "healthy_components": healthy_components,
            "total_components": total_components,
            "critical_alerts": critical_alerts,
            "auto_remediation_success_rate": 85.0  # Simulated value
        }
        
    def _get_latest_metrics_for_component(self, component_id: str) -> List[InfrastructureMetric]:
        """Get latest metrics for a specific component"""
        
        latest_metrics = []
        
        for key, metrics_queue in self.metrics_storage.items():
            if key.startswith(component_id + "_") and metrics_queue:
                latest_metrics.append(metrics_queue[-1])  # Get most recent metric
                
        return latest_metrics
        
    def _determine_component_health(self, metrics: List[InfrastructureMetric]) -> str:
        """Determine health status based on metrics"""
        
        if not metrics:
            return "unknown"
            
        critical_violations = 0
        warning_violations = 0
        
        for metric in metrics:
            threshold_config = metric.threshold_config
            
            if "critical" in threshold_config:
                critical_threshold = threshold_config["critical"]
                
                # Check if metric violates critical threshold
                if metric.metric_name in ["cache_hit_rate", "healthy_targets_percentage"]:
                    if metric.value < critical_threshold:
                        critical_violations += 1
                elif metric.metric_name in ["cpu_utilization", "memory_utilization", "replication_lag"]:
                    if metric.value > critical_threshold:
                        critical_violations += 1
                        
            if "warning" in threshold_config:
                warning_threshold = threshold_config["warning"]
                
                if metric.metric_name in ["cache_hit_rate", "healthy_targets_percentage"]:
                    if metric.value < warning_threshold:
                        warning_violations += 1
                elif metric.metric_name in ["cpu_utilization", "memory_utilization", "replication_lag"]:
                    if metric.value > warning_threshold:
                        warning_violations += 1
        
        if critical_violations > 0:
            return "critical"
        elif warning_violations > 0:
            return "warning"
        else:
            return "healthy"
            
    def _calculate_cost_analysis(self) -> Dict[str, Any]:
        """Calculate cost analysis and optimization opportunities"""
        
        current_hourly_cost = 0
        projected_monthly_cost = 0
        
        for component_id, config in self.infrastructure_topology.items():
            hourly_cost = config.get("cost_per_hour_inr", 0)
            current_hourly_cost += hourly_cost
            
        projected_monthly_cost = current_hourly_cost * 24 * 30  # 30 days
        
        cost_analysis = {
            "current_hourly_cost_inr": current_hourly_cost,
            "projected_monthly_cost_inr": projected_monthly_cost,
            "monthly_budget_inr": self.cost_tracking["monthly_budget_inr"],
            "budget_utilization_percentage": min(100, (projected_monthly_cost / self.cost_tracking["monthly_budget_inr"]) * 100),
            "cost_optimization_potential_inr": projected_monthly_cost * 0.2,  # 20% potential savings
            "top_cost_components": self._get_top_cost_components()
        }
        
        return cost_analysis
        
    def _get_top_cost_components(self) -> List[Dict[str, Any]]:
        """Get top cost components for optimization"""
        
        components_by_cost = []
        
        for component_id, config in self.infrastructure_topology.items():
            hourly_cost = config.get("cost_per_hour_inr", 0)
            monthly_cost = hourly_cost * 24 * 30
            
            components_by_cost.append({
                "component_id": component_id,
                "component_type": config["component_type"].value,
                "monthly_cost_inr": monthly_cost,
                "optimization_potential": monthly_cost * random.uniform(0.1, 0.3)  # 10-30% savings
            })
        
        # Sort by cost (descending)
        components_by_cost.sort(key=lambda x: x["monthly_cost_inr"], reverse=True)
        
        return components_by_cost[:5]  # Top 5 most expensive
        
    def _get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alerts"""
        
        alerts_by_severity = defaultdict(int)
        alerts_by_component = defaultdict(int)
        recent_alerts = 0
        
        current_time = datetime.now()
        
        for alert in self.alerts_storage:
            alerts_by_severity[alert.severity] += 1
            alerts_by_component[alert.component_id] += 1
            
            # Count alerts in last hour
            if (current_time - alert.timestamp).total_seconds() < 3600:
                recent_alerts += 1
        
        return {
            "total_alerts": len(self.alerts_storage),
            "alerts_by_severity": dict(alerts_by_severity),
            "alerts_by_component": dict(alerts_by_component),
            "recent_alerts_1h": recent_alerts,
            "auto_remediation_attempts": len([a for a in self.alerts_storage if a.auto_remediation_attempted])
        }
        
    def _assess_business_impact(self) -> Dict[str, Any]:
        """Assess current business impact of infrastructure issues"""
        
        critical_components_down = 0
        estimated_revenue_impact_per_minute = 0
        
        for component_id, config in self.infrastructure_topology.items():
            latest_metrics = self._get_latest_metrics_for_component(component_id)
            health = self._determine_component_health(latest_metrics)
            
            if health == "critical":
                business_criticality = config.get("business_criticality", "medium")
                if business_criticality == "critical":
                    critical_components_down += 1
                    estimated_revenue_impact_per_minute += self.business_context["revenue_impact_per_minute"]["critical_components"]
                elif business_criticality == "high":
                    estimated_revenue_impact_per_minute += self.business_context["revenue_impact_per_minute"]["high_components"]
        
        return {
            "critical_components_affected": critical_components_down,
            "estimated_revenue_impact_per_minute_inr": estimated_revenue_impact_per_minute,
            "sla_breach_risk": "high" if critical_components_down > 0 else "low",
            "customer_impact_level": "severe" if critical_components_down > 2 else "moderate" if critical_components_down > 0 else "minimal"
        }
        
    def _generate_capacity_planning(self) -> Dict[str, Any]:
        """Generate capacity planning recommendations"""
        
        return {
            "current_utilization": {
                "compute": random.uniform(60, 85),  # Simulated
                "storage": random.uniform(45, 75),
                "network": random.uniform(30, 60),
                "database": random.uniform(50, 80)
            },
            
            "growth_projections": {
                "next_month": {"traffic_increase": 15, "resource_increase_needed": 10},
                "next_quarter": {"traffic_increase": 50, "resource_increase_needed": 40},
                "festival_season": {"traffic_increase": 300, "resource_increase_needed": 200}
            },
            
            "scaling_recommendations": [
                "Add 5 more application servers before next month",
                "Upgrade database instance size by 50% for festival season",
                "Implement auto-scaling for web servers",
                "Increase Redis cache capacity by 30%"
            ]
        }
        
    def _generate_regional_breakdown(self) -> Dict[str, Any]:
        """Generate regional performance breakdown"""
        
        regional_data = {}
        
        for region in Region:
            # Count components in each region
            components_in_region = [
                comp_id for comp_id, config in self.infrastructure_topology.items()
                if config.get("region") == region
            ]
            
            if components_in_region:
                regional_data[region.value] = {
                    "total_components": len(components_in_region),
                    "healthy_components": len(components_in_region) - random.randint(0, 1),  # Simulate health
                    "cost_per_hour_inr": sum([
                        self.infrastructure_topology[comp_id].get("cost_per_hour_inr", 0)
                        for comp_id in components_in_region
                    ]),
                    "network_latency_avg_ms": random.uniform(20, 100),  # Simulated
                    "availability_percentage": random.uniform(98, 99.9)  # Simulated
                }
        
        return regional_data
        
    def _generate_infrastructure_recommendations(self, dashboard_data: Dict) -> List[str]:
        """Generate actionable infrastructure recommendations"""
        
        recommendations = []
        
        # Cost optimization recommendations
        cost_analysis = dashboard_data["cost_analysis"]
        if cost_analysis["budget_utilization_percentage"] > 90:
            recommendations.append(
                f"Budget utilization at {cost_analysis['budget_utilization_percentage']:.1f}%. "
                f"Implement cost optimization to save ₹{cost_analysis['cost_optimization_potential_inr']:,.0f}/month."
            )
        
        # Health-based recommendations
        overall_health = dashboard_data["overall_health"]
        if overall_health["health_percentage"] < 90:
            recommendations.append(
                f"Overall health at {overall_health['health_percentage']}%. "
                "Address critical alerts and consider infrastructure improvements."
            )
        
        # Alert-based recommendations
        alert_summary = dashboard_data["alert_summary"]
        if alert_summary["alerts_by_severity"].get("critical", 0) > 5:
            recommendations.append(
                f"{alert_summary['alerts_by_severity']['critical']} critical alerts active. "
                "Implement immediate remediation and review alerting thresholds."
            )
        
        # Business impact recommendations
        business_impact = dashboard_data["business_impact_assessment"]
        if business_impact["estimated_revenue_impact_per_minute_inr"] > 50000:
            recommendations.append(
                f"Estimated revenue impact: ₹{business_impact['estimated_revenue_impact_per_minute_inr']:,}/minute. "
                "Prioritize critical component recovery immediately."
            )
        
        return recommendations

# Test and simulation functions
async def simulate_irctc_tatkal_infrastructure_load():
    """Simulate IRCTC Tatkal booking infrastructure load at 10 AM"""
    print("🚂 Simulating IRCTC Tatkal booking infrastructure load...")
    
    dashboard = IndianInfrastructureDashboard("IRCTC-Tatkal")
    
    print(f"🏗️  Initialized {len(dashboard.infrastructure_topology)} infrastructure components")
    
    # Simulate 10 minutes of Tatkal booking load (10:00 AM to 10:10 AM)
    print("⏰ Simulating 10 AM Tatkal rush...")
    
    for minute in range(10):  # 10 minutes of monitoring
        print(f"\n📊 Minute {minute + 1}/10 - Collecting metrics...")
        
        # Collect metrics from all components
        all_metrics = []
        for component_id in dashboard.infrastructure_topology.keys():
            metrics = dashboard.collect_infrastructure_metrics(component_id)
            all_metrics.extend(metrics)
            
        print(f"  📈 Collected {len(all_metrics)} metrics")
        
        # Simulate load pattern (massive spike at minute 1-3, then decline)
        if minute < 3:
            print("  🔥 PEAK LOAD: Massive Tatkal booking rush!")
        elif minute < 6:
            print("  📉 HIGH LOAD: Sustained high traffic")
        else:
            print("  📊 NORMAL LOAD: Traffic normalizing")
            
        # Brief pause between metric collection cycles
        await asyncio.sleep(0.1)
    
    # Generate dashboard data
    print("\n📋 Generating infrastructure dashboard...")
    dashboard_data = dashboard.generate_infrastructure_dashboard_data()
    
    print(f"\n🏥 Overall Infrastructure Health: {dashboard_data['overall_health']['health_percentage']}%")
    print(f"💰 Projected Monthly Cost: ₹{dashboard_data['cost_analysis']['projected_monthly_cost_inr']:,.0f}")
    print(f"🚨 Total Alerts: {dashboard_data['alert_summary']['total_alerts']}")
    
    print(f"\n🏆 Top Cost Components:")
    for i, comp in enumerate(dashboard_data['cost_analysis']['top_cost_components'][:3], 1):
        print(f"  {i}. {comp['component_id']}: ₹{comp['monthly_cost_inr']:,.0f}/month")
    
    print(f"\n💡 Key Recommendations:")
    for i, rec in enumerate(dashboard_data['recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    
    return dashboard, dashboard_data

def test_multi_region_infrastructure():
    """Test multi-region infrastructure monitoring"""
    print("\n🌏 Testing multi-region infrastructure monitoring...")
    
    dashboard = IndianInfrastructureDashboard("Flipkart-BBD")
    
    # Collect metrics from different regions
    regional_performance = {}
    
    for component_id, config in dashboard.infrastructure_topology.items():
        region = config.get("region", "unknown")
        if region != "unknown":
            if region not in regional_performance:
                regional_performance[region] = {"components": 0, "healthy": 0, "cost": 0}
            
            # Collect metrics
            metrics = dashboard.collect_infrastructure_metrics(component_id)
            health = dashboard._determine_component_health(metrics)
            
            regional_performance[region]["components"] += 1
            if health in ["healthy", "warning"]:
                regional_performance[region]["healthy"] += 1
            regional_performance[region]["cost"] += config.get("cost_per_hour_inr", 0)
    
    print("\n📊 Regional Performance Summary:")
    for region, stats in regional_performance.items():
        health_pct = (stats["healthy"] / stats["components"]) * 100 if stats["components"] > 0 else 0
        print(f"  {region}: {health_pct:.1f}% healthy, ₹{stats['cost']:,.0f}/hour")

def test_cost_optimization_analysis():
    """Test cost optimization recommendations"""
    print("\n💰 Testing cost optimization analysis...")
    
    dashboard = IndianInfrastructureDashboard("Paytm-Payments")
    
    # Generate cost analysis
    dashboard_data = dashboard.generate_infrastructure_dashboard_data()
    cost_analysis = dashboard_data["cost_analysis"]
    
    print(f"Current hourly cost: ₹{cost_analysis['current_hourly_cost_inr']:,.0f}")
    print(f"Monthly projection: ₹{cost_analysis['projected_monthly_cost_inr']:,.0f}")
    print(f"Budget utilization: {cost_analysis['budget_utilization_percentage']:.1f}%")
    print(f"Optimization potential: ₹{cost_analysis['cost_optimization_potential_inr']:,.0f}")

if __name__ == "__main__":
    print("🚀 Episode 16: Infrastructure Dashboard for Indian Scale")
    print("🇮🇳 IRCTC se Flipkart tak, sab ka infrastructure monitor karte hain!")
    print("=" * 60)
    
    # Run comprehensive testing
    asyncio.run(simulate_irctc_tatkal_infrastructure_load())
    test_multi_region_infrastructure()
    test_cost_optimization_analysis()
    
    print("\n" + "=" * 60)
    print("✅ Infrastructure dashboard testing completed!")
    print("📊 Key Insights:")
    print("  - Multi-component health monitoring is critical")
    print("  - Cost optimization can save 20-30% monthly spend")
    print("  - Auto-remediation handles 85%+ of common issues")
    print("  - Regional monitoring reveals performance patterns")
    print("🔍 Next: Setup real-time dashboard visualization")