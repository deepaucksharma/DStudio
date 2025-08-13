#!/usr/bin/env python3
"""
Container Health Monitoring System - Flipkart Style
Cloud Native Health Checks and Monitoring for Container Orchestration

Flipkart ke container infrastructure ke liye comprehensive health monitoring
Kubernetes, Docker Swarm, aur ECS ke saath compatible
"""

import os
import json
import time
import psutil
import requests
import threading
import subprocess
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


class HealthStatus(Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result data structure"""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ContainerMetrics:
    """Container resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    network_io: Dict
    container_id: str
    container_name: str
    uptime_seconds: int
    restart_count: int


class FlipkartHealthMonitor:
    """
    Flipkart container health monitoring system
    Mumbai se Bangalore tak har container ki health track karta hai
    """
    
    def __init__(self, service_name: str = "flipkart-service"):
        self.service_name = service_name
        self.container_id = os.environ.get('HOSTNAME', 'local-container')
        self.health_checks: List[Callable] = []
        self.health_history: List[HealthCheckResult] = []
        self.max_history = 100
        
        # Flipkart specific configuration
        self.flipkart_service_tier = os.environ.get('FLIPKART_SERVICE_TIER', 'bronze')
        self.flipkart_region = os.environ.get('FLIPKART_REGION', 'mumbai')
        self.flipkart_env = os.environ.get('FLIPKART_ENV', 'production')
        
        # Health check thresholds
        self.cpu_threshold = float(os.environ.get('CPU_THRESHOLD', '80.0'))
        self.memory_threshold = float(os.environ.get('MEMORY_THRESHOLD', '85.0'))
        self.disk_threshold = float(os.environ.get('DISK_THRESHOLD', '90.0'))
        
        # Setup logging
        self.setup_logging()
        
        # Register default health checks
        self.register_default_checks()
        
        self.logger.info(f"🏥 Flipkart Health Monitor initialized for {self.service_name}")
        self.logger.info(f"📍 Region: {self.flipkart_region}, Tier: {self.flipkart_service_tier}")
    
    def setup_logging(self):
        """Setup health monitoring logging"""
        self.logger = logging.getLogger(f"flipkart-health-{self.service_name}")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.container_id}] %(asctime)s %(levelname)s [%(name)s]: %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def register_health_check(self, check_func: Callable, name: str = None):
        """Register a custom health check function"""
        if name:
            check_func._health_check_name = name
        self.health_checks.append(check_func)
        self.logger.info(f"✅ Registered health check: {name or check_func.__name__}")
    
    def register_default_checks(self):
        """Register Flipkart's standard health checks"""
        self.register_health_check(self.check_system_resources, "system_resources")
        self.register_health_check(self.check_disk_space, "disk_space")
        self.register_health_check(self.check_network_connectivity, "network")
        self.register_health_check(self.check_application_health, "application")
        self.register_health_check(self.check_dependencies, "dependencies")
        self.register_health_check(self.check_flipkart_services, "flipkart_services")
    
    def check_system_resources(self) -> HealthCheckResult:
        """
        System resource health check
        CPU aur Memory usage check karta hai - Mumbai datacenter ke liye critical
        """
        start_time = time.time()
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Determine health status
            status = HealthStatus.HEALTHY
            messages = []
            
            if cpu_percent > self.cpu_threshold:
                status = HealthStatus.DEGRADED if cpu_percent < 95 else HealthStatus.UNHEALTHY
                messages.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > self.memory_threshold:
                current_status = HealthStatus.DEGRADED if memory.percent < 95 else HealthStatus.UNHEALTHY
                if current_status.value == "unhealthy" or status.value != "unhealthy":
                    status = current_status
                messages.append(f"High memory usage: {memory.percent:.1f}%")
            
            message = "; ".join(messages) if messages else f"CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name="system_resources",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / 1024 / 1024,
                    'thresholds': {
                        'cpu': self.cpu_threshold,
                        'memory': self.memory_threshold
                    }
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="system_resources",
                status=HealthStatus.UNHEALTHY,
                message=f"Resource check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat()
            )
    
    def check_disk_space(self) -> HealthCheckResult:
        """
        Disk space health check
        Flipkart ke logs aur cache ke liye disk space critical hai
        """
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            status = HealthStatus.HEALTHY
            if disk_percent > self.disk_threshold:
                status = HealthStatus.DEGRADED if disk_percent < 95 else HealthStatus.UNHEALTHY
            
            message = f"Disk usage: {disk_percent:.1f}% ({disk.free / 1024 / 1024 / 1024:.1f}GB free)"
            
            return HealthCheckResult(
                name="disk_space",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'disk_percent': disk_percent,
                    'free_gb': disk.free / 1024 / 1024 / 1024,
                    'total_gb': disk.total / 1024 / 1024 / 1024,
                    'threshold': self.disk_threshold
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat()
            )
    
    def check_network_connectivity(self) -> HealthCheckResult:
        """
        Network connectivity health check
        Flipkart ke microservices ke beech communication check karta hai
        """
        start_time = time.time()
        
        try:
            # Check external connectivity
            external_hosts = ['8.8.8.8', 'flipkart.com']
            failed_hosts = []
            
            for host in external_hosts:
                try:
                    result = subprocess.run(
                        ['ping', '-c', '1', '-W', '3', host],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode != 0:
                        failed_hosts.append(host)
                except subprocess.TimeoutExpired:
                    failed_hosts.append(host)
            
            # Check internal service connectivity (if configured)
            internal_services = os.environ.get('HEALTH_CHECK_INTERNAL_SERVICES', '').split(',')
            internal_services = [s.strip() for s in internal_services if s.strip()]
            
            failed_internal = []
            for service in internal_services:
                try:
                    response = requests.get(f"http://{service}/health", timeout=3)
                    if response.status_code != 200:
                        failed_internal.append(service)
                except requests.RequestException:
                    failed_internal.append(service)
            
            # Determine status
            total_failed = len(failed_hosts) + len(failed_internal)
            if total_failed == 0:
                status = HealthStatus.HEALTHY
                message = "All network checks passed"
            elif total_failed < 2:
                status = HealthStatus.DEGRADED
                message = f"Some network issues: external={failed_hosts}, internal={failed_internal}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Network connectivity issues: external={failed_hosts}, internal={failed_internal}"
            
            return HealthCheckResult(
                name="network",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'external_failed': failed_hosts,
                    'internal_failed': failed_internal,
                    'external_tested': external_hosts,
                    'internal_tested': internal_services
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="network",
                status=HealthStatus.UNHEALTHY,
                message=f"Network check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat()
            )
    
    def check_application_health(self) -> HealthCheckResult:
        """
        Application-specific health check
        Flipkart service ki internal health check karta hai
        """
        start_time = time.time()
        
        try:
            # Check if application port is listening
            app_port = int(os.environ.get('APP_PORT', '8080'))
            
            try:
                response = requests.get(f"http://localhost:{app_port}/health", timeout=5)
                if response.status_code == 200:
                    app_health = response.json()
                    status = HealthStatus.HEALTHY
                    message = f"Application healthy on port {app_port}"
                    metadata = app_health
                else:
                    status = HealthStatus.DEGRADED
                    message = f"Application responding but unhealthy (status: {response.status_code})"
                    metadata = {"status_code": response.status_code}
            except requests.RequestException:
                # Check if port is at least listening
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', app_port))
                sock.close()
                
                if result == 0:
                    status = HealthStatus.DEGRADED
                    message = f"Port {app_port} listening but health endpoint not responding"
                    metadata = {"port_listening": True, "health_endpoint": False}
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"Application not listening on port {app_port}"
                    metadata = {"port_listening": False}
            
            return HealthCheckResult(
                name="application",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat(),
                metadata=metadata
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="application",
                status=HealthStatus.UNHEALTHY,
                message=f"Application check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat()
            )
    
    def check_dependencies(self) -> HealthCheckResult:
        """
        Dependencies health check
        Database, cache, aur external services ki connectivity check
        """
        start_time = time.time()
        
        try:
            dependencies = {
                'database': os.environ.get('DATABASE_URL'),
                'redis': os.environ.get('REDIS_URL'),
                'elasticsearch': os.environ.get('ELASTICSEARCH_URL')
            }
            
            failed_deps = []
            checked_deps = []
            
            for dep_name, dep_url in dependencies.items():
                if not dep_url:
                    continue
                    
                checked_deps.append(dep_name)
                
                try:
                    if dep_name == 'database' and 'postgresql://' in dep_url:
                        import psycopg2
                        conn = psycopg2.connect(dep_url)
                        conn.close()
                    elif dep_name == 'redis' and 'redis://' in dep_url:
                        import redis
                        r = redis.from_url(dep_url)
                        r.ping()
                    elif dep_name == 'elasticsearch':
                        response = requests.get(f"{dep_url}/_health", timeout=3)
                        if response.status_code != 200:
                            raise Exception(f"Elasticsearch unhealthy: {response.status_code}")
                    else:
                        # Generic HTTP health check
                        response = requests.get(f"{dep_url}/health", timeout=3)
                        if response.status_code != 200:
                            raise Exception(f"Service unhealthy: {response.status_code}")
                            
                except Exception as dep_error:
                    failed_deps.append(f"{dep_name}: {str(dep_error)}")
            
            # Determine status
            if not checked_deps:
                status = HealthStatus.HEALTHY
                message = "No dependencies configured"
            elif not failed_deps:
                status = HealthStatus.HEALTHY
                message = f"All dependencies healthy: {checked_deps}"
            elif len(failed_deps) < len(checked_deps):
                status = HealthStatus.DEGRADED
                message = f"Some dependencies failed: {failed_deps}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"All dependencies failed: {failed_deps}"
            
            return HealthCheckResult(
                name="dependencies",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'checked': checked_deps,
                    'failed': failed_deps,
                    'configured': list(dependencies.keys())
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="dependencies",
                status=HealthStatus.UNHEALTHY,
                message=f"Dependencies check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat()
            )
    
    def check_flipkart_services(self) -> HealthCheckResult:
        """
        Flipkart-specific service health checks
        Internal Flipkart services aur APIs ki health check
        """
        start_time = time.time()
        
        try:
            # Flipkart internal services (mock URLs for demo)
            flipkart_services = {
                'catalog-service': 'http://catalog-service:8080',
                'inventory-service': 'http://inventory-service:8080',
                'pricing-service': 'http://pricing-service:8080',
                'recommendation-service': 'http://recommendation-service:8080'
            }
            
            service_status = {}
            overall_healthy = 0
            
            for service_name, service_url in flipkart_services.items():
                try:
                    # In real implementation, use actual service URLs
                    # For demo, simulate health check
                    import random
                    if random.random() > 0.1:  # 90% success rate
                        service_status[service_name] = "healthy"
                        overall_healthy += 1
                    else:
                        service_status[service_name] = "unhealthy"
                except Exception:
                    service_status[service_name] = "error"
            
            total_services = len(flipkart_services)
            healthy_percentage = (overall_healthy / total_services) * 100 if total_services > 0 else 100
            
            if healthy_percentage >= 80:
                status = HealthStatus.HEALTHY
                message = f"Flipkart services healthy: {overall_healthy}/{total_services}"
            elif healthy_percentage >= 50:
                status = HealthStatus.DEGRADED
                message = f"Some Flipkart services unhealthy: {overall_healthy}/{total_services}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Multiple Flipkart services down: {overall_healthy}/{total_services}"
            
            return HealthCheckResult(
                name="flipkart_services",
                status=status,
                message=message,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'service_status': service_status,
                    'healthy_percentage': healthy_percentage,
                    'total_services': total_services,
                    'region': self.flipkart_region,
                    'tier': self.flipkart_service_tier
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="flipkart_services",
                status=HealthStatus.UNHEALTHY,
                message=f"Flipkart services check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow().isoformat()
            )
    
    def run_all_health_checks(self) -> Dict[str, HealthCheckResult]:
        """
        Run all registered health checks
        Parallel execution for faster response
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(self.health_checks)) as executor:
            # Submit all health checks
            future_to_check = {}
            for check_func in self.health_checks:
                check_name = getattr(check_func, '_health_check_name', check_func.__name__)
                future = executor.submit(check_func)
                future_to_check[future] = check_name
            
            # Collect results
            for future in as_completed(future_to_check):
                check_name = future_to_check[future]
                try:
                    result = future.result(timeout=10)  # 10 second timeout per check
                    results[check_name] = result
                except Exception as e:
                    results[check_name] = HealthCheckResult(
                        name=check_name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check timeout or error: {str(e)}",
                        response_time_ms=10000,
                        timestamp=datetime.utcnow().isoformat()
                    )
        
        return results
    
    def get_overall_health(self, health_results: Dict[str, HealthCheckResult]) -> Dict:
        """
        Calculate overall health status
        Flipkart ke liye comprehensive health assessment
        """
        if not health_results:
            return {
                'status': HealthStatus.UNKNOWN.value,
                'message': 'No health checks performed',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        status_counts = {
            HealthStatus.HEALTHY.value: 0,
            HealthStatus.DEGRADED.value: 0,
            HealthStatus.UNHEALTHY.value: 0,
            HealthStatus.UNKNOWN.value: 0
        }
        
        total_checks = len(health_results)
        for result in health_results.values():
            status_counts[result.status.value] += 1
        
        # Overall status calculation
        unhealthy_percentage = (status_counts[HealthStatus.UNHEALTHY.value] / total_checks) * 100
        degraded_percentage = (status_counts[HealthStatus.DEGRADED.value] / total_checks) * 100
        
        if unhealthy_percentage > 20:  # More than 20% unhealthy
            overall_status = HealthStatus.UNHEALTHY
            message = f"Service critically unhealthy ({unhealthy_percentage:.1f}% checks failed)"
        elif unhealthy_percentage > 0 or degraded_percentage > 30:  # Any unhealthy or >30% degraded
            overall_status = HealthStatus.DEGRADED
            message = f"Service degraded ({unhealthy_percentage:.1f}% unhealthy, {degraded_percentage:.1f}% degraded)"
        else:
            overall_status = HealthStatus.HEALTHY
            message = f"Service healthy ({status_counts[HealthStatus.HEALTHY.value]}/{total_checks} checks passed)"
        
        return {
            'status': overall_status.value,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'details': {
                'total_checks': total_checks,
                'healthy': status_counts[HealthStatus.HEALTHY.value],
                'degraded': status_counts[HealthStatus.DEGRADED.value],
                'unhealthy': status_counts[HealthStatus.UNHEALTHY.value],
                'unknown': status_counts[HealthStatus.UNKNOWN.value]
            },
            'service_info': {
                'name': self.service_name,
                'container_id': self.container_id,
                'region': self.flipkart_region,
                'tier': self.flipkart_service_tier,
                'environment': self.flipkart_env
            }
        }
    
    def get_container_metrics(self) -> ContainerMetrics:
        """
        Get detailed container metrics
        Mumbai datacenter mein resource utilization track karta hai
        """
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Network I/O (simplified)
            network_io = psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Container-specific metrics (mock for demo)
            uptime = int(time.time() - psutil.boot_time())
            restart_count = int(os.environ.get('CONTAINER_RESTART_COUNT', '0'))
            
            return ContainerMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_total_mb=memory.total / 1024 / 1024,
                disk_usage_percent=disk_percent,
                network_io=network_io,
                container_id=self.container_id,
                container_name=self.service_name,
                uptime_seconds=uptime,
                restart_count=restart_count
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get container metrics: {e}")
            raise
    
    def health_check_endpoint(self) -> Dict:
        """
        Main health check endpoint for containers
        Kubernetes liveness/readiness probes ke liye
        """
        start_time = time.time()
        
        # Run all health checks
        health_results = self.run_all_health_checks()
        
        # Calculate overall health
        overall_health = self.get_overall_health(health_results)
        
        # Add individual check results
        individual_checks = {}
        for name, result in health_results.items():
            individual_checks[name] = asdict(result)
        
        # Build complete response
        response = {
            'overall': overall_health,
            'checks': individual_checks,
            'execution_time_ms': int((time.time() - start_time) * 1000),
            'flipkart_metadata': {
                'service': self.service_name,
                'region': self.flipkart_region,
                'tier': self.flipkart_service_tier,
                'environment': self.flipkart_env,
                'container_id': self.container_id
            }
        }
        
        # Store in history
        overall_result = HealthCheckResult(
            name="overall",
            status=HealthStatus(overall_health['status']),
            message=overall_health['message'],
            response_time_ms=response['execution_time_ms'],
            timestamp=overall_health['timestamp'],
            metadata=overall_health['details']
        )
        
        self.health_history.append(overall_result)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)
        
        self.logger.info(f"🏥 Health check completed: {overall_health['status']} ({response['execution_time_ms']}ms)")
        
        return response


# Flask app for health endpoints
from flask import Flask, jsonify

def create_health_app(monitor: FlipkartHealthMonitor) -> Flask:
    """Create Flask app with health endpoints"""
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        """Kubernetes readiness probe"""
        result = monitor.health_check_endpoint()
        status_code = 200
        
        if result['overall']['status'] == 'unhealthy':
            status_code = 503
        elif result['overall']['status'] == 'degraded':
            status_code = 200  # Still serve traffic but log issues
            
        return jsonify(result), status_code
    
    @app.route('/health/live')
    def liveness():
        """Kubernetes liveness probe - simpler check"""
        try:
            basic_checks = ['system_resources', 'disk_space']
            results = {}
            
            for check_name in basic_checks:
                check_func = None
                for func in monitor.health_checks:
                    if getattr(func, '_health_check_name', func.__name__) == check_name:
                        check_func = func
                        break
                
                if check_func:
                    results[check_name] = check_func()
            
            unhealthy_count = sum(1 for r in results.values() if r.status == HealthStatus.UNHEALTHY)
            
            if unhealthy_count == 0:
                return jsonify({'status': 'alive', 'checks': len(results)}), 200
            else:
                return jsonify({'status': 'dead', 'unhealthy': unhealthy_count}), 503
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 503
    
    @app.route('/health/ready')
    def readiness():
        """Kubernetes readiness probe - comprehensive check"""
        result = monitor.health_check_endpoint()
        
        # Ready if not unhealthy
        if result['overall']['status'] == 'unhealthy':
            return jsonify(result), 503
        else:
            return jsonify(result), 200
    
    @app.route('/metrics')
    def metrics():
        """Container metrics endpoint"""
        try:
            metrics = monitor.get_container_metrics()
            return jsonify(asdict(metrics)), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health/history')
    def health_history():
        """Health check history"""
        history = [asdict(result) for result in monitor.health_history]
        return jsonify({
            'history': history,
            'count': len(history),
            'service': monitor.service_name
        })
    
    return app


if __name__ == '__main__':
    # Initialize Flipkart health monitor
    monitor = FlipkartHealthMonitor("flipkart-catalog-service")
    
    # Create Flask app
    app = create_health_app(monitor)
    
    # Run the health monitoring service
    port = int(os.environ.get('HEALTH_PORT', '8088'))
    print(f"🏥 Starting Flipkart Health Monitor on port {port}")
    print(f"📍 Service: {monitor.service_name}, Region: {monitor.flipkart_region}")
    print("🔍 Health endpoints available:")
    print("   /health - Overall health check")
    print("   /health/live - Liveness probe")
    print("   /health/ready - Readiness probe")
    print("   /metrics - Container metrics")
    print("   /health/history - Health history")
    
    # Test health check
    test_result = monitor.health_check_endpoint()
    print(f"🧪 Initial health check: {test_result['overall']['status']}")
    
    app.run(host='0.0.0.0', port=port, debug=False)