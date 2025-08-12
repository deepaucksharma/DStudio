#!/usr/bin/env python3
"""
Advanced Health Check and Monitoring System for Load Balancers
लोड बैलेंसर के लिए उन्नत स्वास्थ्य जांच प्रणाली

यह system दिखाता है कि कैसे comprehensive health monitoring
implement करें multiple servers के साथ intelligent failover।
"""

import time
import asyncio
import aiohttp
import threading
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import psutil
import requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Server health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class HealthMetrics:
    """Comprehensive health metrics for a server"""
    # Basic connectivity
    is_reachable: bool = False
    response_time_ms: float = 0.0
    
    # HTTP health
    http_status_code: int = 0
    http_response_time_ms: float = 0.0
    
    # System resources
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    
    # Application metrics
    active_connections: int = 0
    queue_depth: int = 0
    error_rate_percent: float = 0.0
    throughput_rps: float = 0.0
    
    # Network metrics
    network_latency_ms: float = 0.0
    packet_loss_percent: float = 0.0
    bandwidth_utilization_percent: float = 0.0
    
    # Business metrics (for Indian context)
    successful_transactions: int = 0
    failed_transactions: int = 0
    upi_success_rate: float = 100.0  # For payment systems
    order_completion_rate: float = 100.0  # For e-commerce
    
    # Timestamps
    last_check: float = field(default_factory=time.time)
    check_duration_ms: float = 0.0


@dataclass
class MonitoredServer:
    """Server configuration with monitoring details"""
    server_id: str
    name: str
    host: str
    port: int
    region: str
    service_type: str  # web, api, database, cache, etc.
    
    # Health check endpoints
    health_check_url: str = ""
    metrics_url: str = ""
    status_url: str = ""
    
    # Current status
    current_status: HealthStatus = HealthStatus.UNKNOWN
    current_metrics: HealthMetrics = field(default_factory=HealthMetrics)
    
    # Historical data (sliding window)
    metrics_history: deque = field(default_factory=lambda: deque(maxlen=100))
    status_changes: deque = field(default_factory=lambda: deque(maxlen=50))
    
    # Configuration
    check_interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3  # Consecutive failures before marking unhealthy
    recovery_threshold: int = 2  # Consecutive successes before marking healthy
    
    # Counters
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    total_checks: int = 0
    total_failures: int = 0


class IndianServerHealthMonitor:
    """
    भारतीय servers के लिए comprehensive health monitoring system
    Multiple data centers और services के साथ
    """
    
    def __init__(self):
        self.servers: Dict[str, MonitoredServer] = {}
        self.health_check_tasks = {}
        self.monitoring_active = False
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring statistics
        self.stats = {
            'total_checks_performed': 0,
            'alerts_sent': 0,
            'servers_failed_over': 0,
            'average_response_time': 0.0
        }
        
        # Initialize Indian server fleet
        self._initialize_indian_servers()
        
        logger.info("🏥 Indian Server Health Monitor initialized")
    
    def _initialize_indian_servers(self):
        """Initialize monitoring for Indian servers across regions"""
        
        indian_servers = [
            # Payment systems (UPI/Banking)
            MonitoredServer(
                "PAYTM_MUM_001", "Paytm Mumbai Primary", "paytm-mumbai-1.com", 443, 
                "West India", "payment",
                health_check_url="https://paytm-mumbai-1.com/health",
                metrics_url="https://paytm-mumbai-1.com/metrics"
            ),
            MonitoredServer(
                "PHONEPE_BLR_001", "PhonePe Bangalore Primary", "phonepe-blr-1.com", 443,
                "South India", "payment",
                health_check_url="https://phonepe-blr-1.com/health",
                metrics_url="https://phonepe-blr-1.com/metrics"
            ),
            
            # E-commerce systems
            MonitoredServer(
                "FLIPKART_BLR_001", "Flipkart Bangalore API", "flipkart-api-blr.com", 443,
                "South India", "ecommerce",
                health_check_url="https://flipkart-api-blr.com/health",
                metrics_url="https://flipkart-api-blr.com/metrics"
            ),
            MonitoredServer(
                "AMAZON_DEL_001", "Amazon Delhi Fulfillment", "amazon-delhi-fc.com", 443,
                "North India", "ecommerce", 
                health_check_url="https://amazon-delhi-fc.com/health",
                metrics_url="https://amazon-delhi-fc.com/metrics"
            ),
            
            # Food delivery
            MonitoredServer(
                "SWIGGY_HYD_001", "Swiggy Hyderabad Orders", "swiggy-hyd-orders.com", 443,
                "South India", "fooddelivery",
                health_check_url="https://swiggy-hyd-orders.com/health",
                metrics_url="https://swiggy-hyd-orders.com/metrics"
            ),
            MonitoredServer(
                "ZOMATO_DEL_001", "Zomato Delhi Central", "zomato-delhi-central.com", 443,
                "North India", "fooddelivery",
                health_check_url="https://zomato-delhi-central.com/health", 
                metrics_url="https://zomato-delhi-central.com/metrics"
            ),
            
            # Government services
            MonitoredServer(
                "AADHAAR_DEL_001", "Aadhaar Delhi Data Center", "aadhaar-del-dc1.uidai.gov.in", 443,
                "North India", "government",
                health_check_url="https://aadhaar-del-dc1.uidai.gov.in/health",
                metrics_url="https://aadhaar-del-dc1.uidai.gov.in/metrics"
            ),
            MonitoredServer(
                "IRCTC_MUM_001", "IRCTC Mumbai Booking", "irctc-mumbai-booking.com", 443,
                "West India", "government", 
                health_check_url="https://irctc-mumbai-booking.com/health",
                metrics_url="https://irctc-mumbai-booking.com/metrics"
            ),
            
            # Banking systems
            MonitoredServer(
                "SBI_MUM_001", "SBI Mumbai Core Banking", "sbi-mumbai-core.com", 443,
                "West India", "banking",
                health_check_url="https://sbi-mumbai-core.com/health",
                metrics_url="https://sbi-mumbai-core.com/metrics"
            ),
            MonitoredServer(
                "HDFC_BLR_001", "HDFC Bangalore Digital", "hdfc-blr-digital.com", 443,
                "South India", "banking",
                health_check_url="https://hdfc-blr-digital.com/health", 
                metrics_url="https://hdfc-blr-digital.com/metrics"
            )
        ]
        
        for server in indian_servers:
            self.servers[server.server_id] = server
            logger.info(f"📡 Added server: {server.name} ({server.service_type}) - {server.region}")
    
    async def perform_health_check(self, server: MonitoredServer) -> HealthMetrics:
        """
        Perform comprehensive health check for a server
        किसी server के लिए व्यापक स्वास्थ्य जांच करता है
        """
        start_time = time.time()
        metrics = HealthMetrics()
        
        try:
            # Basic connectivity check
            metrics.is_reachable = await self._check_connectivity(server)
            
            if metrics.is_reachable:
                # HTTP health check
                metrics.http_status_code, metrics.http_response_time_ms = await self._check_http_health(server)
                
                # Application-specific metrics
                app_metrics = await self._get_application_metrics(server)
                if app_metrics:
                    metrics.active_connections = app_metrics.get('active_connections', 0)
                    metrics.queue_depth = app_metrics.get('queue_depth', 0)
                    metrics.error_rate_percent = app_metrics.get('error_rate', 0.0)
                    metrics.throughput_rps = app_metrics.get('throughput', 0.0)
                    
                    # Service-specific metrics
                    if server.service_type == 'payment':
                        metrics.upi_success_rate = app_metrics.get('upi_success_rate', 100.0)
                    elif server.service_type == 'ecommerce':
                        metrics.order_completion_rate = app_metrics.get('order_completion_rate', 100.0)
                
                # System resource metrics (simulated for external servers)
                metrics.cpu_usage_percent = await self._get_cpu_usage(server)
                metrics.memory_usage_percent = await self._get_memory_usage(server)
                metrics.disk_usage_percent = await self._get_disk_usage(server)
                
                # Network metrics
                metrics.network_latency_ms = metrics.http_response_time_ms
                metrics.packet_loss_percent = await self._check_packet_loss(server)
        
        except Exception as e:
            logger.error(f"❌ Health check failed for {server.name}: {e}")
            metrics.is_reachable = False
        
        # Calculate total check duration
        metrics.check_duration_ms = (time.time() - start_time) * 1000
        metrics.last_check = time.time()
        
        return metrics
    
    async def _check_connectivity(self, server: MonitoredServer) -> bool:
        """Check basic network connectivity"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=server.timeout_seconds)) as session:
                async with session.get(f"https://{server.host}:{server.port}/") as response:
                    return True
        except:
            return False
    
    async def _check_http_health(self, server: MonitoredServer) -> Tuple[int, float]:
        """Check HTTP health endpoint"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=server.timeout_seconds)) as session:
                url = server.health_check_url or f"https://{server.host}/health"
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    return response.status, response_time
        except:
            response_time = (time.time() - start_time) * 1000
            return 0, response_time
    
    async def _get_application_metrics(self, server: MonitoredServer) -> Optional[Dict]:
        """Get application-specific metrics"""
        try:
            if not server.metrics_url:
                return None
                
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=server.timeout_seconds)) as session:
                async with session.get(server.metrics_url) as response:
                    if response.status == 200:
                        return await response.json()
        except:
            pass
        
        # Simulate realistic metrics for demo
        return self._simulate_application_metrics(server)
    
    def _simulate_application_metrics(self, server: MonitoredServer) -> Dict:
        """Simulate realistic application metrics"""
        import random
        
        base_metrics = {
            'active_connections': random.randint(50, 1000),
            'queue_depth': random.randint(0, 50),
            'error_rate': random.uniform(0.1, 5.0),
            'throughput': random.uniform(100, 2000)
        }
        
        # Service-specific metrics
        if server.service_type == 'payment':
            base_metrics.update({
                'upi_success_rate': random.uniform(95.0, 99.9),
                'transaction_volume': random.randint(1000, 50000)
            })
        elif server.service_type == 'ecommerce':
            base_metrics.update({
                'order_completion_rate': random.uniform(92.0, 98.5),
                'cart_abandonment_rate': random.uniform(60.0, 80.0)
            })
        elif server.service_type == 'fooddelivery':
            base_metrics.update({
                'delivery_success_rate': random.uniform(88.0, 95.0),
                'average_delivery_time': random.uniform(25, 45)
            })
        
        return base_metrics
    
    async def _get_cpu_usage(self, server: MonitoredServer) -> float:
        """Get CPU usage (simulated for external servers)"""
        import random
        return random.uniform(20.0, 85.0)
    
    async def _get_memory_usage(self, server: MonitoredServer) -> float:
        """Get memory usage (simulated for external servers)"""
        import random
        return random.uniform(40.0, 90.0)
    
    async def _get_disk_usage(self, server: MonitoredServer) -> float:
        """Get disk usage (simulated for external servers)"""
        import random
        return random.uniform(30.0, 75.0)
    
    async def _check_packet_loss(self, server: MonitoredServer) -> float:
        """Check packet loss (simulated)"""
        import random
        return random.uniform(0.0, 2.0)
    
    def determine_health_status(self, server: MonitoredServer, metrics: HealthMetrics) -> HealthStatus:
        """
        Determine overall health status based on metrics
        मेट्रिक्स के आधार पर समग्र स्वास्थ्य स्थिति निर्धारित करता है
        """
        # Critical failures
        if not metrics.is_reachable:
            return HealthStatus.UNHEALTHY
        
        if metrics.http_status_code not in [200, 201, 202]:
            return HealthStatus.UNHEALTHY
        
        # Performance degradation checks
        degraded_conditions = 0
        
        if metrics.response_time_ms > 1000:  # > 1 second
            degraded_conditions += 1
        
        if metrics.cpu_usage_percent > 80:
            degraded_conditions += 1
        
        if metrics.memory_usage_percent > 85:
            degraded_conditions += 1
        
        if metrics.error_rate_percent > 5.0:
            degraded_conditions += 1
        
        # Service-specific health checks
        if server.service_type == 'payment' and metrics.upi_success_rate < 95.0:
            degraded_conditions += 1
        
        if server.service_type == 'ecommerce' and metrics.order_completion_rate < 90.0:
            degraded_conditions += 1
        
        # Determine status
        if degraded_conditions >= 3:
            return HealthStatus.UNHEALTHY
        elif degraded_conditions >= 1:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def update_server_status(self, server: MonitoredServer, new_metrics: HealthMetrics):
        """Update server status based on new health check results"""
        new_status = self.determine_health_status(server, new_metrics)
        old_status = server.current_status
        
        # Update metrics
        server.current_metrics = new_metrics
        server.metrics_history.append(new_metrics)
        server.total_checks += 1
        
        # Handle status transitions
        if new_status == HealthStatus.HEALTHY:
            server.consecutive_successes += 1
            server.consecutive_failures = 0
            
            # Mark healthy if enough consecutive successes
            if (server.consecutive_successes >= server.recovery_threshold and 
                old_status != HealthStatus.HEALTHY):
                self._change_server_status(server, old_status, HealthStatus.HEALTHY)
        
        else:  # DEGRADED or UNHEALTHY
            server.consecutive_failures += 1
            server.consecutive_successes = 0
            server.total_failures += 1
            
            # Mark unhealthy if enough consecutive failures
            if (server.consecutive_failures >= server.failure_threshold and 
                old_status != HealthStatus.UNHEALTHY):
                self._change_server_status(server, old_status, HealthStatus.UNHEALTHY)
            elif new_status == HealthStatus.DEGRADED and old_status == HealthStatus.HEALTHY:
                self._change_server_status(server, old_status, HealthStatus.DEGRADED)
    
    def _change_server_status(self, server: MonitoredServer, old_status: HealthStatus, new_status: HealthStatus):
        """Handle server status changes and send alerts"""
        server.current_status = new_status
        
        # Record status change
        status_change = {
            'timestamp': time.time(),
            'from_status': old_status.value,
            'to_status': new_status.value,
            'metrics': server.current_metrics
        }
        server.status_changes.append(status_change)
        
        # Log status change
        logger.info(f"🔄 {server.name} status changed: {old_status.value} -> {new_status.value}")
        
        # Send alerts for critical changes
        if new_status == HealthStatus.UNHEALTHY:
            self._send_alert(server, "CRITICAL", f"{server.name} is UNHEALTHY")
        elif new_status == HealthStatus.DEGRADED:
            self._send_alert(server, "WARNING", f"{server.name} performance is DEGRADED")
        elif new_status == HealthStatus.HEALTHY and old_status == HealthStatus.UNHEALTHY:
            self._send_alert(server, "INFO", f"{server.name} has RECOVERED")
    
    def _send_alert(self, server: MonitoredServer, severity: str, message: str):
        """Send alert notifications"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'server_id': server.server_id,
            'server_name': server.name,
            'region': server.region,
            'service_type': server.service_type,
            'severity': severity,
            'message': message,
            'metrics': {
                'response_time_ms': server.current_metrics.response_time_ms,
                'cpu_usage': server.current_metrics.cpu_usage_percent,
                'memory_usage': server.current_metrics.memory_usage_percent,
                'error_rate': server.current_metrics.error_rate_percent
            }
        }
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        self.stats['alerts_sent'] += 1
        
        # Console alert for demo
        print(f"\n🚨 ALERT [{severity}]: {message}")
        print(f"   Server: {server.name} ({server.region})")
        print(f"   Service: {server.service_type}")
        print(f"   Response Time: {server.current_metrics.response_time_ms:.1f}ms")
        print(f"   CPU: {server.current_metrics.cpu_usage_percent:.1f}%")
        print(f"   Error Rate: {server.current_metrics.error_rate_percent:.2f}%")
    
    async def monitor_server(self, server_id: str):
        """Continuous monitoring loop for a specific server"""
        server = self.servers.get(server_id)
        if not server:
            logger.error(f"Server not found: {server_id}")
            return
        
        logger.info(f"🏥 Starting health monitoring for {server.name}")
        
        while self.monitoring_active:
            try:
                # Perform health check
                metrics = await self.perform_health_check(server)
                
                # Update server status
                self.update_server_status(server, metrics)
                
                # Update global statistics
                self.stats['total_checks_performed'] += 1
                
                # Update average response time
                total_response_time = sum(m.response_time_ms for m in server.metrics_history if m.response_time_ms > 0)
                avg_count = len([m for m in server.metrics_history if m.response_time_ms > 0])
                if avg_count > 0:
                    self.stats['average_response_time'] = total_response_time / avg_count
                
                # Wait for next check
                await asyncio.sleep(server.check_interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Monitoring error for {server.name}: {e}")
                await asyncio.sleep(server.check_interval_seconds)
        
        logger.info(f"🛑 Stopped monitoring {server.name}")
    
    def start_monitoring(self):
        """Start health monitoring for all servers"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        logger.info("🚀 Starting health monitoring system")
        
        # Start monitoring tasks for all servers
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_monitors():
            tasks = []
            for server_id in self.servers.keys():
                task = asyncio.create_task(self.monitor_server(server_id))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        try:
            loop.run_until_complete(run_monitors())
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        finally:
            self.monitoring_active = False
            loop.close()
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Stopping health monitoring system")
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status report"""
        healthy_servers = sum(1 for s in self.servers.values() if s.current_status == HealthStatus.HEALTHY)
        degraded_servers = sum(1 for s in self.servers.values() if s.current_status == HealthStatus.DEGRADED)
        unhealthy_servers = sum(1 for s in self.servers.values() if s.current_status == HealthStatus.UNHEALTHY)
        
        # Regional breakdown
        regional_status = defaultdict(lambda: {'healthy': 0, 'degraded': 0, 'unhealthy': 0})
        service_status = defaultdict(lambda: {'healthy': 0, 'degraded': 0, 'unhealthy': 0})
        
        for server in self.servers.values():
            status_key = server.current_status.value
            if status_key in ['healthy', 'degraded', 'unhealthy']:
                regional_status[server.region][status_key] += 1
                service_status[server.service_type][status_key] += 1
        
        return {
            'system_overview': {
                'total_servers': len(self.servers),
                'healthy_servers': healthy_servers,
                'degraded_servers': degraded_servers,
                'unhealthy_servers': unhealthy_servers,
                'overall_health_percentage': (healthy_servers / len(self.servers)) * 100 if self.servers else 0
            },
            'regional_status': dict(regional_status),
            'service_status': dict(service_status),
            'statistics': self.stats,
            'server_details': [
                {
                    'server_id': s.server_id,
                    'name': s.name,
                    'region': s.region,
                    'service_type': s.service_type,
                    'status': s.current_status.value,
                    'last_check': datetime.fromtimestamp(s.current_metrics.last_check).strftime('%Y-%m-%d %H:%M:%S'),
                    'response_time_ms': s.current_metrics.response_time_ms,
                    'cpu_usage': f"{s.current_metrics.cpu_usage_percent:.1f}%",
                    'memory_usage': f"{s.current_metrics.memory_usage_percent:.1f}%",
                    'error_rate': f"{s.current_metrics.error_rate_percent:.2f}%",
                    'consecutive_failures': s.consecutive_failures,
                    'total_checks': s.total_checks,
                    'total_failures': s.total_failures,
                    'failure_rate': f"{(s.total_failures/max(1, s.total_checks))*100:.2f}%"
                }
                for s in self.servers.values()
            ]
        }
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback function for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def simulate_server_failure(self, server_id: str):
        """Simulate server failure for testing"""
        server = self.servers.get(server_id)
        if server:
            logger.info(f"🧪 Simulating failure for {server.name}")
            server.current_status = HealthStatus.UNHEALTHY
            server.consecutive_failures = server.failure_threshold
            self._send_alert(server, "CRITICAL", f"SIMULATED FAILURE: {server.name}")


def demonstrate_health_monitoring():
    """Demonstrate the health monitoring system"""
    print("🏥 भारतीय सर्वर स्वास्थ्य निगरानी प्रणाली")
    print("=" * 60)
    
    # Initialize monitoring system
    monitor = IndianServerHealthMonitor()
    
    # Add alert callback
    def alert_handler(alert):
        print(f"\n📧 Alert sent to operations team:")
        print(f"   Severity: {alert['severity']}")
        print(f"   Message: {alert['message']}")
        print(f"   Server: {alert['server_name']} ({alert['region']})")
    
    monitor.add_alert_callback(alert_handler)
    
    # Simulate some health checks
    print("\n🔍 Performing initial health checks...")
    
    # Run a few health check cycles
    import asyncio
    
    async def run_demo_checks():
        # Perform health checks for all servers
        for server in list(monitor.servers.values())[:5]:  # Just first 5 for demo
            metrics = await monitor.perform_health_check(server)
            monitor.update_server_status(server, metrics)
            print(f"✅ Checked {server.name}: {server.current_status.value}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_demo_checks())
    loop.close()
    
    # Display system status
    print(f"\n📊 System Health Status Report:")
    print("=" * 50)
    
    status = monitor.get_system_status()
    system_overview = status['system_overview']
    
    print(f"System Overview:")
    print(f"  Total Servers: {system_overview['total_servers']}")
    print(f"  Healthy: {system_overview['healthy_servers']} "
          f"({system_overview['overall_health_percentage']:.1f}%)")
    print(f"  Degraded: {system_overview['degraded_servers']}")
    print(f"  Unhealthy: {system_overview['unhealthy_servers']}")
    
    print(f"\n🌍 Regional Health Distribution:")
    for region, counts in status['regional_status'].items():
        total = counts['healthy'] + counts['degraded'] + counts['unhealthy']
        health_pct = (counts['healthy'] / max(1, total)) * 100
        print(f"  {region}: {health_pct:.1f}% healthy "
              f"({counts['healthy']}/{total} servers)")
    
    print(f"\n🔧 Service Type Health:")
    for service, counts in status['service_status'].items():
        total = counts['healthy'] + counts['degraded'] + counts['unhealthy']
        health_pct = (counts['healthy'] / max(1, total)) * 100
        print(f"  {service.capitalize()}: {health_pct:.1f}% healthy")
    
    # Show detailed server information
    print(f"\n🖥️ Server Details (Top 8 by Response Time):")
    print("-" * 120)
    print(f"{'Server Name':<30} {'Region':<15} {'Service':<12} {'Status':<10} {'Response':<10} {'CPU':<8} {'Memory':<8} {'Error%':<8}")
    print("-" * 120)
    
    servers_sorted = sorted(status['server_details'], 
                           key=lambda x: x['response_time_ms'], reverse=True)[:8]
    
    for server in servers_sorted:
        status_icon = "🟢" if server['status'] == 'healthy' else "🟡" if server['status'] == 'degraded' else "🔴"
        print(f"{server['name']:<30} {server['region']:<15} {server['service_type']:<12} "
              f"{status_icon} {server['status']:<7} {server['response_time_ms']:<10.1f} "
              f"{server['cpu_usage']:<8} {server['memory_usage']:<8} {server['error_rate']:<8}")
    
    # Demonstrate failure simulation
    print(f"\n🧪 Simulating Server Failure for Demo:")
    print("-" * 40)
    
    # Simulate failure of a payment server
    monitor.simulate_server_failure("PAYTM_MUM_001")
    
    # Show updated status
    updated_status = monitor.get_system_status()
    unhealthy_after = updated_status['system_overview']['unhealthy_servers']
    
    print(f"Unhealthy servers after simulation: {unhealthy_after}")
    
    print(f"\n💡 Production Recommendations:")
    print("=" * 35)
    print("🔄 Implement automated failover based on health status")
    print("📊 Set up real-time dashboards for operations team")
    print("📱 Mobile alerts for critical failures")
    print("🤖 ML-based anomaly detection for predictive alerts")
    print("⚖️ Load balancer integration for automatic traffic rerouting")
    print("📈 Historical trend analysis for capacity planning")
    
    print(f"\n🚀 Indian-Specific Enhancements:")
    print("🇮🇳 Multi-language alert messages (Hindi/English)")
    print("🎆 Festival season scaling alerts")
    print("🏛️ Government compliance monitoring")  
    print("💰 Cost optimization based on regional usage")
    print("📡 Edge location health for better user experience")


if __name__ == "__main__":
    demonstrate_health_monitoring()