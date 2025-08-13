#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Container Health Monitoring and Observability
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे BigBasket जैसी companies
production में container health monitoring करती हैं।

Real-world scenario: BigBasket का comprehensive container observability
"""

import docker
import psutil
import time
import json
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, start_http_server, generate_latest
import logging
from loguru import logger

class HealthStatus(Enum):
    """Container health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    UNKNOWN = "unknown"

@dataclass
class ContainerMetrics:
    """Container metrics data structure"""
    container_id: str
    container_name: str
    image: str
    status: str
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_limit_mb: float
    network_rx_bytes: int
    network_tx_bytes: int
    disk_read_bytes: int
    disk_write_bytes: int
    restart_count: int
    uptime_seconds: float
    health_status: HealthStatus
    timestamp: float

@dataclass
class HealthCheckResult:
    """Health check result structure"""
    container_id: str
    check_type: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: float

class BigBasketContainerMonitor:
    """
    BigBasket-style Container Health Monitoring System
    Production-ready observability with Indian company context
    """
    
    def __init__(self, monitoring_interval: int = 30):
        # Docker client initialization
        try:
            self.docker_client = docker.from_env()
            logger.info("🐳 Docker client connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {str(e)}")
            raise
        
        self.monitoring_interval = monitoring_interval
        
        # Prometheus metrics setup
        self.registry = CollectorRegistry()
        self.setup_prometheus_metrics()
        
        # Container registry and health status
        self.container_registry: Dict[str, ContainerMetrics] = {}
        self.health_check_results: List[HealthCheckResult] = []
        
        # Monitoring thread control
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Alert thresholds - Indian production standards
        self.alert_thresholds = {
            "cpu_high": 80.0,           # 80% CPU usage
            "memory_high": 85.0,        # 85% Memory usage
            "disk_io_high": 100 * 1024 * 1024,  # 100MB/s disk I/O
            "response_time_high": 5000,  # 5 seconds response time
            "restart_count_high": 3      # 3 restarts in monitoring period
        }
        
        # Indian company specific service mappings
        self.service_mappings = {
            "bigbasket-inventory": {
                "critical": True,
                "health_endpoints": ["/health", "/api/health"],
                "expected_instances": 5
            },
            "bigbasket-orders": {
                "critical": True,
                "health_endpoints": ["/health", "/api/v1/health"],
                "expected_instances": 10
            },
            "bigbasket-payments": {
                "critical": True,
                "health_endpoints": ["/health", "/payments/health"],
                "expected_instances": 3
            },
            "bigbasket-delivery": {
                "critical": True,
                "health_endpoints": ["/health", "/delivery/status"],
                "expected_instances": 8
            }
        }
        
        logger.info("🏥 BigBasket Container Monitor initialized!")
        logger.info(f"Monitoring interval: {monitoring_interval} seconds")
    
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics for container monitoring"""
        
        # Container resource metrics
        self.container_cpu_usage = Gauge(
            'bigbasket_container_cpu_usage_percent',
            'Container CPU usage percentage',
            ['container_name', 'service', 'environment'],
            registry=self.registry
        )
        
        self.container_memory_usage = Gauge(
            'bigbasket_container_memory_usage_mb',
            'Container memory usage in MB',
            ['container_name', 'service', 'environment'],
            registry=self.registry
        )
        
        self.container_network_rx = Counter(
            'bigbasket_container_network_rx_bytes_total',
            'Container network received bytes total',
            ['container_name', 'service'],
            registry=self.registry
        )
        
        self.container_network_tx = Counter(
            'bigbasket_container_network_tx_bytes_total',
            'Container network transmitted bytes total',
            ['container_name', 'service'],
            registry=self.registry
        )
        
        # Health check metrics
        self.health_check_duration = Histogram(
            'bigbasket_health_check_duration_seconds',
            'Health check duration in seconds',
            ['container_name', 'check_type', 'status'],
            registry=self.registry
        )
        
        self.container_restart_count = Counter(
            'bigbasket_container_restarts_total',
            'Container restart count total',
            ['container_name', 'service', 'reason'],
            registry=self.registry
        )
        
        # Service availability metrics
        self.service_availability = Gauge(
            'bigbasket_service_availability_ratio',
            'Service availability ratio (0-1)',
            ['service', 'environment'],
            registry=self.registry
        )
        
        logger.info("📊 Prometheus metrics configured")
    
    def get_container_metrics(self, container) -> Optional[ContainerMetrics]:
        """
        Get comprehensive metrics for a single container
        """
        try:
            # Basic container info
            container.reload()  # Refresh container state
            
            # CPU and Memory stats
            stats = container.stats(stream=False)
            
            # Calculate CPU usage percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            
            cpu_usage = 0.0
            if system_delta > 0:
                cpu_usage = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
            
            # Memory usage
            memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)  # Convert to MB
            memory_limit = stats['memory_stats']['limit'] / (1024 * 1024)  # Convert to MB
            
            # Network I/O
            network_rx = network_tx = 0
            if 'networks' in stats:
                for interface, net_stats in stats['networks'].items():
                    network_rx += net_stats['rx_bytes']
                    network_tx += net_stats['tx_bytes']
            
            # Disk I/O
            disk_read = disk_write = 0
            if 'blkio_stats' in stats and 'io_service_bytes_recursive' in stats['blkio_stats']:
                for item in stats['blkio_stats']['io_service_bytes_recursive']:
                    if item['op'] == 'Read':
                        disk_read += item['value']
                    elif item['op'] == 'Write':
                        disk_write += item['value']
            
            # Container status and health
            health_status = self.determine_health_status(container)
            
            # Uptime calculation
            created_time = datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
            uptime = (datetime.now(created_time.tzinfo) - created_time).total_seconds()
            
            # Restart count
            restart_count = container.attrs['RestartCount']
            
            return ContainerMetrics(
                container_id=container.id[:12],  # Short ID
                container_name=container.name,
                image=container.image.tags[0] if container.image.tags else container.image.id[:12],
                status=container.status,
                cpu_usage_percent=round(cpu_usage, 2),
                memory_usage_mb=round(memory_usage, 2),
                memory_limit_mb=round(memory_limit, 2),
                network_rx_bytes=network_rx,
                network_tx_bytes=network_tx,
                disk_read_bytes=disk_read,
                disk_write_bytes=disk_write,
                restart_count=restart_count,
                uptime_seconds=uptime,
                health_status=health_status,
                timestamp=time.time()
            )
        
        except Exception as e:
            logger.error(f"Error getting metrics for container {container.name}: {str(e)}")
            return None
    
    def determine_health_status(self, container) -> HealthStatus:
        """
        Determine container health status using multiple checks
        """
        # Check container state
        if container.status != 'running':
            return HealthStatus.UNHEALTHY
        
        # Check if container has health checks defined
        container_config = container.attrs.get('Config', {})
        if 'Healthcheck' in container_config:
            health_status = container.attrs.get('State', {}).get('Health', {}).get('Status', '')
            
            if health_status == 'healthy':
                return HealthStatus.HEALTHY
            elif health_status == 'unhealthy':
                return HealthStatus.UNHEALTHY
            elif health_status == 'starting':
                return HealthStatus.STARTING
        
        # If no health check, assume healthy if running for > 30 seconds
        created_time = datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
        uptime = (datetime.now(created_time.tzinfo) - created_time).total_seconds()
        
        if uptime > 30:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.STARTING
    
    async def perform_health_check(self, container_name: str, endpoint: str, port: int = 8000) -> HealthCheckResult:
        """
        Perform HTTP health check on container endpoint
        """
        start_time = time.time()
        
        try:
            # Get container IP
            container = self.docker_client.containers.get(container_name)
            networks = container.attrs['NetworkSettings']['Networks']
            
            container_ip = None
            for network_name, network_info in networks.items():
                if network_info.get('IPAddress'):
                    container_ip = network_info['IPAddress']
                    break
            
            if not container_ip:
                return HealthCheckResult(
                    container_id=container.id[:12],
                    check_type="http_health",
                    status=HealthStatus.UNKNOWN,
                    message="No IP address found",
                    response_time_ms=0,
                    timestamp=time.time()
                )
            
            # Perform HTTP health check
            health_url = f"http://{container_ip}:{port}{endpoint}"
            response = requests.get(health_url, timeout=5)
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                status = HealthStatus.HEALTHY
                message = "Health check passed"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"HTTP {response.status_code}"
            
            return HealthCheckResult(
                container_id=container.id[:12],
                check_type="http_health",
                status=status,
                message=message,
                response_time_ms=round(response_time, 2),
                timestamp=time.time()
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                container_id="unknown",
                check_type="http_health",
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                response_time_ms=round(response_time, 2),
                timestamp=time.time()
            )
    
    def update_prometheus_metrics(self, metrics: ContainerMetrics):
        """
        Update Prometheus metrics with container data
        """
        # Extract service name from container name
        service_name = "unknown"
        environment = "production"
        
        for service, config in self.service_mappings.items():
            if service in metrics.container_name:
                service_name = service
                break
        
        # Update resource metrics
        self.container_cpu_usage.labels(
            container_name=metrics.container_name,
            service=service_name,
            environment=environment
        ).set(metrics.cpu_usage_percent)
        
        self.container_memory_usage.labels(
            container_name=metrics.container_name,
            service=service_name,
            environment=environment
        ).set(metrics.memory_usage_mb)
        
        # Update network metrics (counters)
        self.container_network_rx.labels(
            container_name=metrics.container_name,
            service=service_name
        )._value._value = metrics.network_rx_bytes
        
        self.container_network_tx.labels(
            container_name=metrics.container_name,
            service=service_name
        )._value._value = metrics.network_tx_bytes
        
        # Update restart count if changed
        if metrics.restart_count > 0:
            self.container_restart_count.labels(
                container_name=metrics.container_name,
                service=service_name,
                reason="unknown"
            )._value._value = metrics.restart_count
    
    def check_alert_conditions(self, metrics: ContainerMetrics) -> List[Dict[str, Any]]:
        """
        Check if any alert conditions are met
        """
        alerts = []
        
        # High CPU usage alert
        if metrics.cpu_usage_percent > self.alert_thresholds["cpu_high"]:
            alerts.append({
                "type": "cpu_high",
                "severity": "warning",
                "container": metrics.container_name,
                "value": metrics.cpu_usage_percent,
                "threshold": self.alert_thresholds["cpu_high"],
                "message": f"High CPU usage: {metrics.cpu_usage_percent:.1f}%"
            })
        
        # High memory usage alert
        memory_usage_percent = (metrics.memory_usage_mb / metrics.memory_limit_mb) * 100
        if memory_usage_percent > self.alert_thresholds["memory_high"]:
            alerts.append({
                "type": "memory_high",
                "severity": "warning",
                "container": metrics.container_name,
                "value": memory_usage_percent,
                "threshold": self.alert_thresholds["memory_high"],
                "message": f"High memory usage: {memory_usage_percent:.1f}%"
            })
        
        # Container unhealthy alert
        if metrics.health_status == HealthStatus.UNHEALTHY:
            alerts.append({
                "type": "container_unhealthy",
                "severity": "critical",
                "container": metrics.container_name,
                "message": f"Container {metrics.container_name} is unhealthy"
            })
        
        # High restart count alert
        if metrics.restart_count >= self.alert_thresholds["restart_count_high"]:
            alerts.append({
                "type": "high_restart_count",
                "severity": "warning",
                "container": metrics.container_name,
                "value": metrics.restart_count,
                "threshold": self.alert_thresholds["restart_count_high"],
                "message": f"Container restarted {metrics.restart_count} times"
            })
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]):
        """
        Send alert to monitoring system (Slack, PagerDuty, etc.)
        """
        # In production, integrate with alerting systems
        alert_message = f"🚨 ALERT: {alert['message']} (Container: {alert['container']})"
        
        if alert['severity'] == 'critical':
            logger.error(alert_message)
        else:
            logger.warning(alert_message)
        
        # Simulate Slack webhook call
        slack_payload = {
            "text": alert_message,
            "channel": "#bigbasket-alerts",
            "username": "BigBasket Monitor",
            "icon_emoji": ":warning:"
        }
        
        # In production: requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
        logger.info(f"📱 Alert sent to Slack: {alert['type']}")
    
    def monitor_containers(self):
        """
        Main monitoring loop for all containers
        """
        logger.info("🔄 Starting container monitoring...")
        
        while self.monitoring_active:
            try:
                # Get all running containers
                containers = self.docker_client.containers.list()
                logger.info(f"📊 Monitoring {len(containers)} containers")
                
                current_metrics = {}
                
                for container in containers:
                    # Get metrics for this container
                    metrics = self.get_container_metrics(container)
                    
                    if metrics:
                        # Store metrics
                        current_metrics[container.id] = metrics
                        self.container_registry[container.id] = metrics
                        
                        # Update Prometheus metrics
                        self.update_prometheus_metrics(metrics)
                        
                        # Check for alerts
                        alerts = self.check_alert_conditions(metrics)
                        for alert in alerts:
                            self.send_alert(alert)
                        
                        # Log status
                        logger.info(f"📈 {metrics.container_name}: "
                                  f"CPU {metrics.cpu_usage_percent:.1f}%, "
                                  f"Mem {metrics.memory_usage_mb:.0f}MB, "
                                  f"Status: {metrics.health_status.value}")
                
                # Update service availability metrics
                self.update_service_availability()
                
                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                time.sleep(30)  # Shorter sleep on error
    
    def update_service_availability(self):
        """
        Calculate and update service availability metrics
        """
        for service_name, config in self.service_mappings.items():
            healthy_instances = 0
            total_instances = 0
            
            for container_id, metrics in self.container_registry.items():
                if service_name in metrics.container_name:
                    total_instances += 1
                    if metrics.health_status == HealthStatus.HEALTHY:
                        healthy_instances += 1
            
            if total_instances > 0:
                availability_ratio = healthy_instances / total_instances
                self.service_availability.labels(
                    service=service_name,
                    environment="production"
                ).set(availability_ratio)
                
                logger.info(f"🎯 {service_name} availability: "
                          f"{healthy_instances}/{total_instances} "
                          f"({availability_ratio:.2%})")
    
    def start_monitoring(self):
        """Start container monitoring in background"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitor_containers, daemon=True)
        self.monitoring_thread.start()
        
        # Start Prometheus metrics server
        start_http_server(8090, registry=self.registry)
        logger.info("📊 Prometheus metrics server started on port 8090")
        
        logger.info("🚀 Container monitoring started")
    
    def stop_monitoring(self):
        """Stop container monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        logger.info("🛑 Container monitoring stopped")
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """
        Generate monitoring dashboard data
        """
        if not self.container_registry:
            return {"message": "No container data available"}
        
        # Calculate summary statistics
        total_containers = len(self.container_registry)
        healthy_containers = sum(1 for m in self.container_registry.values() 
                               if m.health_status == HealthStatus.HEALTHY)
        
        avg_cpu = sum(m.cpu_usage_percent for m in self.container_registry.values()) / total_containers
        avg_memory = sum(m.memory_usage_mb for m in self.container_registry.values()) / total_containers
        
        # Service breakdown
        service_stats = {}
        for service_name in self.service_mappings.keys():
            service_containers = [m for m in self.container_registry.values() 
                                if service_name in m.container_name]
            
            if service_containers:
                healthy_count = sum(1 for m in service_containers 
                                  if m.health_status == HealthStatus.HEALTHY)
                service_stats[service_name] = {
                    "total": len(service_containers),
                    "healthy": healthy_count,
                    "availability": healthy_count / len(service_containers)
                }
        
        return {
            "summary": {
                "total_containers": total_containers,
                "healthy_containers": healthy_containers,
                "availability": healthy_containers / total_containers if total_containers > 0 else 0,
                "avg_cpu_usage": round(avg_cpu, 1),
                "avg_memory_usage": round(avg_memory, 1)
            },
            "services": service_stats,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Demonstration of BigBasket container monitoring"""
    
    print("🏢 BigBasket Container Health Monitoring Demo")
    print("=" * 60)
    
    # Initialize monitor
    monitor = BigBasketContainerMonitor(monitoring_interval=30)
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        print("🔄 Monitoring started. Metrics available at:")
        print("   - Prometheus: http://localhost:8090/metrics")
        print("   - Dashboard: Check logs for real-time updates")
        print("\\nPress Ctrl+C to stop monitoring...")
        
        # Run monitoring demo
        demo_duration = 180  # 3 minutes
        start_time = time.time()
        
        while time.time() - start_time < demo_duration:
            # Print dashboard every 60 seconds
            if int(time.time()) % 60 == 0:
                dashboard = monitor.get_monitoring_dashboard()
                print(f"\\n📊 Dashboard Update:")
                print(f"   Total containers: {dashboard.get('summary', {}).get('total_containers', 0)}")
                print(f"   Healthy containers: {dashboard.get('summary', {}).get('healthy_containers', 0)}")
                print(f"   Avg CPU: {dashboard.get('summary', {}).get('avg_cpu_usage', 0)}%")
                print(f"   Avg Memory: {dashboard.get('summary', {}).get('avg_memory_usage', 0)}MB")
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        print("\\n🛑 Stopping monitoring...")
    
    finally:
        monitor.stop_monitoring()
        print("✅ Monitoring stopped successfully!")

if __name__ == "__main__":
    main()

# Production deployment commands:
"""
# Install dependencies:
pip install docker psutil prometheus-client requests loguru

# Run monitoring:
python 06_container_health_monitoring.py

# Access Prometheus metrics:
curl http://localhost:8090/metrics

# Grafana dashboard configuration:
# Add data source: http://localhost:8090
# Import dashboard with BigBasket container metrics

# Kubernetes deployment:
kubectl apply -f bigbasket-monitoring-deployment.yaml

# Check monitoring logs:
kubectl logs -f deployment/bigbasket-monitor -n monitoring
"""