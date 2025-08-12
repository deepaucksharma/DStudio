#!/usr/bin/env python3
"""
Health Monitoring and Service Discovery for Mumbai-scale Microservices
Complete health check and monitoring system

जैसे Mumbai local train system में हर train की health monitor करते हैं,
वैसे ही microservices की health continuously monitor करनी चाहिए
"""

import asyncio
import time
import json
import logging
import psutil
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import redis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MumbaiHealthMonitor")

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    response_time_ms: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceHealth:
    """Complete service health information"""
    service_name: str
    version: str
    status: HealthStatus
    uptime_seconds: float
    checks: List[HealthCheck] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

class MumbaiHealthMonitor:
    """Mumbai-style comprehensive health monitoring system"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.start_time = time.time()
        self.health_checks = {}
        self.redis_client = None
        
        # Register default system health checks
        self.register_default_checks()
        
    def register_default_checks(self):
        """Register default Mumbai-style health checks"""
        self.register_check("cpu_usage", self.check_cpu_usage)
        self.register_check("memory_usage", self.check_memory_usage) 
        self.register_check("disk_usage", self.check_disk_usage)
        self.register_check("database_connectivity", self.check_database)
        self.register_check("redis_connectivity", self.check_redis)
        self.register_check("external_api_health", self.check_external_apis)
        
    def register_check(self, name: str, check_function):
        """Register a health check function"""
        self.health_checks[name] = check_function
        logger.info(f"Registered health check: {name}")
        
    async def check_cpu_usage(self) -> HealthCheck:
        """Check CPU usage - जैसे train engine performance"""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            response_time = (time.time() - start_time) * 1000
            
            if cpu_percent < 70:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}% - Running smooth like Mumbai local!"
            elif cpu_percent < 85:
                status = HealthStatus.DEGRADED
                message = f"CPU usage elevated: {cpu_percent:.1f}% - Like peak hour traffic"
            elif cpu_percent < 95:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage high: {cpu_percent:.1f}% - Like Dadar station congestion!"
            else:
                status = HealthStatus.CRITICAL
                message = f"CPU usage critical: {cpu_percent:.1f}% - System overloaded!"
            
            return HealthCheck(
                name="cpu_usage",
                status=status,
                response_time_ms=response_time,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                    "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="cpu_usage",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"CPU check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def check_memory_usage(self) -> HealthCheck:
        """Check memory usage - जैसे train compartment capacity"""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            response_time = (time.time() - start_time) * 1000
            
            if memory.percent < 70:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}% - Plenty of space like AC first class"
            elif memory.percent < 85:
                status = HealthStatus.DEGRADED  
                message = f"Memory usage elevated: {memory.percent:.1f}% - Getting crowded like general compartment"
            elif memory.percent < 95:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage high: {memory.percent:.1f}% - Packed like Mumbai local at rush hour!"
            else:
                status = HealthStatus.CRITICAL
                message = f"Memory usage critical: {memory.percent:.1f}% - No space left!"
            
            return HealthCheck(
                name="memory_usage",
                status=status,
                response_time_ms=response_time,
                message=message,
                details={
                    "memory_percent": memory.percent,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2)
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="memory_usage",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Memory check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def check_disk_usage(self) -> HealthCheck:
        """Check disk usage - जैसे train storage capacity"""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            response_time = (time.time() - start_time) * 1000
            
            if disk_percent < 75:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}% - Storage like spacious Mumbai Metro"
            elif disk_percent < 85:
                status = HealthStatus.DEGRADED
                message = f"Disk usage elevated: {disk_percent:.1f}% - Storage getting full"
            elif disk_percent < 95:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage high: {disk_percent:.1f}% - Storage almost full like overhead luggage!"
            else:
                status = HealthStatus.CRITICAL
                message = f"Disk usage critical: {disk_percent:.1f}% - Storage full!"
            
            return HealthCheck(
                name="disk_usage", 
                status=status,
                response_time_ms=response_time,
                message=message,
                details={
                    "disk_percent": round(disk_percent, 2),
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2)
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk_usage",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Disk check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def check_database(self) -> HealthCheck:
        """Check database connectivity - जैसे train signal system"""
        start_time = time.time()
        
        try:
            # Simulate database connection check
            await asyncio.sleep(0.05)  # Simulate DB query time
            
            # For demo, simulate 95% success rate
            import random
            success = random.random() > 0.05
            
            response_time = (time.time() - start_time) * 1000
            
            if success:
                status = HealthStatus.HEALTHY
                message = "Database connectivity healthy - Connected like Mumbai local network!"
                details = {
                    "connection_pool_size": 20,
                    "active_connections": random.randint(5, 15),
                    "query_response_time_ms": round(response_time, 2)
                }
            else:
                status = HealthStatus.CRITICAL
                message = "Database connectivity failed - Like train signal failure!"
                details = {"error": "Connection timeout", "retry_attempts": 3}
            
            return HealthCheck(
                name="database_connectivity",
                status=status,
                response_time_ms=response_time,
                message=message,
                details=details
            )
            
        except Exception as e:
            return HealthCheck(
                name="database_connectivity",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Database check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def check_redis(self) -> HealthCheck:
        """Check Redis connectivity - जैसे Mumbai traffic signal coordination"""
        start_time = time.time()
        
        try:
            if not self.redis_client:
                # Initialize Redis client for demo
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0, 
                                              socket_connect_timeout=2, socket_timeout=2)
            
            # Test Redis connectivity
            try:
                self.redis_client.ping()
                redis_info = self.redis_client.info()
                
                status = HealthStatus.HEALTHY
                message = "Redis connectivity healthy - Cache working like Mumbai Dabbawalas precision!"
                details = {
                    "connected_clients": redis_info.get('connected_clients', 0),
                    "used_memory_human": redis_info.get('used_memory_human', 'Unknown'),
                    "redis_version": redis_info.get('redis_version', 'Unknown')
                }
            except Exception:
                status = HealthStatus.UNHEALTHY
                message = "Redis connectivity failed - Cache down like monsoon power cut!"
                details = {"error": "Redis connection failed"}
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="redis_connectivity",
                status=status,
                response_time_ms=response_time,
                message=message,
                details=details
            )
            
        except Exception as e:
            return HealthCheck(
                name="redis_connectivity",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Redis check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def check_external_apis(self) -> HealthCheck:
        """Check external API dependencies - जैसे train route coordination"""
        start_time = time.time()
        
        try:
            # Check multiple external APIs
            api_results = []
            
            # Simulate checking payment gateway (like Razorpay)
            payment_status = await self.check_single_api("https://api.razorpay.com/health", "Payment Gateway")
            api_results.append(payment_status)
            
            # Simulate checking notification service  
            notification_status = await self.check_single_api("https://api.twilio.com/health", "SMS Service")
            api_results.append(notification_status)
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine overall status
            healthy_apis = sum(1 for api in api_results if api["healthy"])
            total_apis = len(api_results)
            
            if healthy_apis == total_apis:
                status = HealthStatus.HEALTHY
                message = f"All external APIs healthy ({healthy_apis}/{total_apis}) - Connected like Mumbai network!"
            elif healthy_apis >= total_apis * 0.7:  # 70% threshold
                status = HealthStatus.DEGRADED
                message = f"Some external APIs degraded ({healthy_apis}/{total_apis}) - Partial connectivity"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Multiple external APIs failed ({healthy_apis}/{total_apis}) - Network issues!"
            
            return HealthCheck(
                name="external_api_health",
                status=status,
                response_time_ms=response_time,
                message=message,
                details={
                    "apis_checked": total_apis,
                    "healthy_apis": healthy_apis,
                    "api_results": api_results
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="external_api_health",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"External API check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def check_single_api(self, url: str, name: str) -> Dict[str, Any]:
        """Check single external API"""
        try:
            # For demo, simulate API responses
            import random
            await asyncio.sleep(random.uniform(0.05, 0.2))  # Simulate network delay
            
            # 90% success rate for external APIs
            healthy = random.random() > 0.1
            response_time = random.uniform(50, 300)
            
            return {
                "name": name,
                "url": url,
                "healthy": healthy,
                "response_time_ms": round(response_time, 2),
                "status_code": 200 if healthy else 503
            }
            
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "healthy": False,
                "error": str(e),
                "response_time_ms": 0
            }
    
    async def get_health_status(self) -> ServiceHealth:
        """Get complete service health status"""
        logger.info(f"Running health checks for {self.service_name}...")
        
        # Run all health checks
        health_results = []
        for check_name, check_function in self.health_checks.items():
            try:
                result = await check_function()
                health_results.append(result)
                logger.debug(f"Health check {check_name}: {result.status.value}")
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {str(e)}")
                health_results.append(HealthCheck(
                    name=check_name,
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0,
                    message=f"Check execution failed: {str(e)}"
                ))
        
        # Determine overall service health
        overall_status = self.calculate_overall_status(health_results)
        
        # Calculate metrics
        uptime = time.time() - self.start_time
        
        metrics = {
            "uptime_seconds": round(uptime, 2),
            "uptime_human": str(timedelta(seconds=int(uptime))),
            "total_checks": len(health_results),
            "healthy_checks": len([h for h in health_results if h.status == HealthStatus.HEALTHY]),
            "degraded_checks": len([h for h in health_results if h.status == HealthStatus.DEGRADED]),
            "unhealthy_checks": len([h for h in health_results if h.status == HealthStatus.UNHEALTHY]),
            "critical_checks": len([h for h in health_results if h.status == HealthStatus.CRITICAL]),
            "avg_response_time_ms": round(sum(h.response_time_ms for h in health_results) / len(health_results), 2)
        }
        
        return ServiceHealth(
            service_name=self.service_name,
            version=self.version,
            status=overall_status,
            uptime_seconds=uptime,
            checks=health_results,
            metrics=metrics
        )
    
    def calculate_overall_status(self, health_results: List[HealthCheck]) -> HealthStatus:
        """Calculate overall service status from individual checks"""
        if not health_results:
            return HealthStatus.CRITICAL
        
        # Count status types
        status_counts = {}
        for result in health_results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        # Determine overall status based on Mumbai-style rules
        if status_counts.get(HealthStatus.CRITICAL, 0) > 0:
            return HealthStatus.CRITICAL
        elif status_counts.get(HealthStatus.UNHEALTHY, 0) >= 2:  # 2+ unhealthy = overall unhealthy
            return HealthStatus.UNHEALTHY
        elif status_counts.get(HealthStatus.UNHEALTHY, 0) > 0 or status_counts.get(HealthStatus.DEGRADED, 0) >= 2:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_health_summary(self) -> str:
        """Get Mumbai-style health summary message"""
        status_messages = {
            HealthStatus.HEALTHY: "Service running smoothly like Mumbai Dabbawalas! 🚂",
            HealthStatus.DEGRADED: "Service operational but with some issues - like monsoon delays ⚠️",
            HealthStatus.UNHEALTHY: "Service facing significant issues - like peak hour congestion 🚨",
            HealthStatus.CRITICAL: "Service critical - immediate attention needed like emergency services! 🆘"
        }
        return status_messages.get(self.service_name, "Unknown status")

class HealthMonitoringService:
    """Central health monitoring service for all Mumbai microservices"""
    
    def __init__(self):
        self.services = {}
        self.monitoring_interval = 30  # seconds
        self.is_monitoring = False
    
    def register_service(self, service_name: str, health_monitor: MumbaiHealthMonitor):
        """Register a service for monitoring"""
        self.services[service_name] = health_monitor
        logger.info(f"Registered service for monitoring: {service_name}")
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.is_monitoring = True
        logger.info("Started Mumbai health monitoring service")
        
        while self.is_monitoring:
            try:
                # Check all registered services
                for service_name, monitor in self.services.items():
                    health_status = await monitor.get_health_status()
                    
                    # Log health status
                    self.log_health_status(health_status)
                    
                    # Store in monitoring system (Redis, database, etc.)
                    await self.store_health_data(health_status)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(5)
    
    def log_health_status(self, health: ServiceHealth):
        """Log service health status"""
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️", 
            HealthStatus.UNHEALTHY: "🚨",
            HealthStatus.CRITICAL: "🆘"
        }
        
        emoji = status_emoji.get(health.status, "❓")
        logger.info(f"{emoji} {health.service_name} ({health.version}): {health.status.value} - "
                   f"{health.metrics['healthy_checks']}/{health.metrics['total_checks']} checks healthy")
        
        # Log critical issues immediately
        if health.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            critical_checks = [c for c in health.checks if c.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]]
            for check in critical_checks:
                logger.warning(f"  ❌ {check.name}: {check.message}")
    
    async def store_health_data(self, health: ServiceHealth):
        """Store health data for historical analysis"""
        # In production, store in time-series database like InfluxDB
        try:
            health_data = {
                "service_name": health.service_name,
                "timestamp": health.last_updated.isoformat(),
                "status": health.status.value,
                "uptime": health.uptime_seconds,
                "metrics": health.metrics
            }
            
            # For demo, just log the storage action
            logger.debug(f"Stored health data for {health.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to store health data: {str(e)}")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        logger.info("Stopped health monitoring service")
    
    async def get_system_health_dashboard(self) -> Dict[str, Any]:
        """Get overall system health dashboard"""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "total_services": len(self.services),
            "services": {},
            "overall_status": HealthStatus.HEALTHY.value,
            "summary": {
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "critical": 0
            }
        }
        
        # Get current health for all services
        for service_name, monitor in self.services.items():
            health = await monitor.get_health_status()
            dashboard["services"][service_name] = {
                "status": health.status.value,
                "uptime": health.uptime_seconds,
                "checks": len(health.checks),
                "healthy_checks": health.metrics["healthy_checks"]
            }
            
            # Update summary
            if health.status == HealthStatus.HEALTHY:
                dashboard["summary"]["healthy"] += 1
            elif health.status == HealthStatus.DEGRADED:
                dashboard["summary"]["degraded"] += 1
            elif health.status == HealthStatus.UNHEALTHY:
                dashboard["summary"]["unhealthy"] += 1
            else:
                dashboard["summary"]["critical"] += 1
        
        # Determine overall system status
        if dashboard["summary"]["critical"] > 0:
            dashboard["overall_status"] = HealthStatus.CRITICAL.value
        elif dashboard["summary"]["unhealthy"] > 0:
            dashboard["overall_status"] = HealthStatus.UNHEALTHY.value
        elif dashboard["summary"]["degraded"] > 0:
            dashboard["overall_status"] = HealthStatus.DEGRADED.value
        
        return dashboard

async def demo_mumbai_health_monitoring():
    """Demonstrate comprehensive health monitoring system"""
    print("\n=== Mumbai Microservices Health Monitoring Demo ===")
    print("Complete health monitoring like Mumbai transport system!")
    
    # Create health monitors for different services
    services = {
        "api-gateway": MumbaiHealthMonitor("api-gateway", "2.1.0"),
        "product-service": MumbaiHealthMonitor("product-service", "1.5.2"),
        "order-service": MumbaiHealthMonitor("order-service", "1.8.1"),
        "payment-service": MumbaiHealthMonitor("payment-service", "2.0.0"),
    }
    
    # Create monitoring service
    monitor_service = HealthMonitoringService()
    
    # Register all services
    for name, monitor in services.items():
        monitor_service.register_service(name, monitor)
    
    print(f"\n--- Individual Service Health Checks ---")
    
    # Check health of each service
    for service_name, monitor in services.items():
        print(f"\n🔍 Checking health of {service_name}...")
        health = await monitor.get_health_status()
        
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "🚨", 
            HealthStatus.CRITICAL: "🆘"
        }
        
        emoji = status_emoji.get(health.status, "❓")
        print(f"{emoji} {health.service_name} v{health.version}: {health.status.value}")
        print(f"   Uptime: {health.metrics['uptime_human']}")
        print(f"   Health Checks: {health.metrics['healthy_checks']}/{health.metrics['total_checks']} passing")
        print(f"   Avg Response Time: {health.metrics['avg_response_time_ms']}ms")
        
        # Show individual check results
        for check in health.checks:
            check_emoji = "✅" if check.status == HealthStatus.HEALTHY else "❌"
            print(f"   {check_emoji} {check.name}: {check.message}")
    
    print(f"\n--- System Health Dashboard ---")
    
    # Get system-wide health dashboard  
    dashboard = await monitor_service.get_system_health_dashboard()
    
    print(f"🏥 Mumbai Microservices Health Dashboard")
    print(f"   Overall Status: {dashboard['overall_status']}")
    print(f"   Total Services: {dashboard['total_services']}")
    print(f"   Healthy: {dashboard['summary']['healthy']}")
    print(f"   Degraded: {dashboard['summary']['degraded']}")
    print(f"   Unhealthy: {dashboard['summary']['unhealthy']}")
    print(f"   Critical: {dashboard['summary']['critical']}")
    
    print(f"\n   Service Details:")
    for service_name, service_data in dashboard["services"].items():
        status_icon = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "🚨", "critical": "🆘"}.get(service_data["status"], "❓")
        print(f"   {status_icon} {service_name}: {service_data['status']} - "
              f"{service_data['healthy_checks']}/{service_data['checks']} checks passing")
    
    print(f"\n--- Continuous Monitoring Simulation ---")
    
    # Start monitoring service
    monitoring_task = asyncio.create_task(monitor_service.start_monitoring())
    
    print("Started continuous health monitoring...")
    print("Monitoring services for 10 seconds...")
    
    # Let it monitor for a short time
    await asyncio.sleep(10)
    
    # Stop monitoring
    monitor_service.stop_monitoring()
    monitoring_task.cancel()
    
    print(f"\n--- Health Monitoring Benefits ---")
    print("✅ Real-time Health Monitoring:")
    print("   - Continuous service health assessment")
    print("   - Early detection of issues like Mumbai traffic alerts")
    print("   - Automated alerting for critical conditions")
    
    print("\n✅ Comprehensive Metrics:")
    print("   - System resource usage (CPU, memory, disk)")
    print("   - Database and cache connectivity")
    print("   - External API dependency health")
    print("   - Response time tracking")
    
    print("\n✅ Operational Intelligence:")
    print("   - Service uptime tracking")
    print("   - Health trend analysis")
    print("   - Capacity planning insights")
    print("   - Incident response automation")
    
    print(f"\n🚂 Mumbai Health Monitoring completed!")
    print(f"   Like Mumbai local train system monitoring")
    print(f"   Continuous oversight ensures system reliability!")

if __name__ == "__main__":
    print("Starting Mumbai Health Monitoring Demo...")
    asyncio.run(demo_mumbai_health_monitoring())