#!/usr/bin/env python3
"""
Distributed Load Balancer with Health Monitoring
Episode 45: Distributed Computing at Scale

यह example distributed load balancer दिखाता है multiple algorithms,
health checking, और automatic failover के साथ। High availability
और performance optimization के लिए production-ready implementation।

Production Stats:
- Cloudflare: 100+ Tbps of traffic load balanced globally
- AWS ELB: 99.99% availability with automatic failover
- Indian CDNs: Handle 50+ Gbps during cricket matches
- Latency reduction: 40-60% with optimal routing
- Health check frequency: Every 2-5 seconds
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics
import heapq

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_CONNECTIONS = "LEAST_CONNECTIONS"
    WEIGHTED_ROUND_ROBIN = "WEIGHTED_ROUND_ROBIN"
    IP_HASH = "IP_HASH"
    LEAST_RESPONSE_TIME = "LEAST_RESPONSE_TIME"
    RESOURCE_BASED = "RESOURCE_BASED"

class ServerHealth(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED" 
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"

@dataclass
class ServerNode:
    """Backend server node"""
    server_id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    health: ServerHealth = ServerHealth.UNKNOWN
    last_health_check: Optional[datetime] = None
    response_times: deque = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    region: str = "Unknown"
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = deque(maxlen=100)
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def connection_utilization(self) -> float:
        return (self.current_connections / self.max_connections) * 100
    
    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

@dataclass
class RequestInfo:
    """Information about incoming request"""
    request_id: str
    client_ip: str
    method: str
    path: str
    headers: Dict[str, str]
    timestamp: datetime
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class LoadBalancerStats:
    """Load balancer performance statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    requests_per_server: Dict[str, int] = None
    
    def __post_init__(self):
        if self.requests_per_server is None:
            self.requests_per_server = defaultdict(int)
    
    @property
    def success_rate(self) -> float:
        return (self.successful_requests / max(self.total_requests, 1)) * 100
    
    @property
    def avg_response_time(self) -> float:
        return self.total_response_time / max(self.successful_requests, 1)

class HealthChecker:
    """Health monitoring for backend servers"""
    
    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval
        self.is_running = False
        self.servers = {}  # server_id -> ServerNode
        self.health_history = defaultdict(list)  # server_id -> [health_status]
        
    def add_server(self, server: ServerNode):
        """Add server for health monitoring"""
        self.servers[server.server_id] = server
        logger.info(f"🏥 Added server {server.server_id} to health monitoring")
    
    def remove_server(self, server_id: str):
        """Remove server from health monitoring"""
        if server_id in self.servers:
            del self.servers[server_id]
            logger.info(f"🏥 Removed server {server_id} from health monitoring")
    
    async def start_monitoring(self):
        """Start health check monitoring"""
        self.is_running = True
        logger.info("🏥 Health monitoring started")
        
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in health monitoring: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_running = False
        logger.info("🏥 Health monitoring stopped")
    
    async def _perform_health_checks(self):
        """Perform health checks on all servers"""
        tasks = []
        for server in self.servers.values():
            task = self._check_server_health(server)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_server_health(self, server: ServerNode):
        """Check health of individual server"""
        start_time = time.time()
        
        try:
            # Simulate health check (HTTP GET to /health endpoint)
            health_check_result = await self._simulate_health_check(server)
            
            response_time = (time.time() - start_time) * 1000
            server.response_times.append(response_time)
            server.last_health_check = datetime.now()
            
            # Determine health status
            if health_check_result["status"] == "ok":
                if response_time < 1000:  # < 1 second
                    server.health = ServerHealth.HEALTHY
                else:
                    server.health = ServerHealth.DEGRADED
            else:
                server.health = ServerHealth.UNHEALTHY
            
            # Update resource metrics
            server.cpu_usage = health_check_result.get("cpu_usage", 0.0)
            server.memory_usage = health_check_result.get("memory_usage", 0.0)
            
            # Store health history
            self.health_history[server.server_id].append({
                "timestamp": datetime.now(),
                "health": server.health,
                "response_time": response_time,
                "cpu_usage": server.cpu_usage,
                "memory_usage": server.memory_usage
            })
            
            # Keep only last 100 health checks
            if len(self.health_history[server.server_id]) > 100:
                self.health_history[server.server_id].pop(0)
            
        except Exception as e:
            logger.error(f"❌ Health check failed for {server.server_id}: {e}")
            server.health = ServerHealth.UNHEALTHY
            server.last_health_check = datetime.now()
    
    async def _simulate_health_check(self, server: ServerNode) -> Dict[str, Any]:
        """Simulate health check HTTP request"""
        # Simulate network latency based on region
        if server.region == "Mumbai":
            latency = random.uniform(0.010, 0.050)  # 10-50ms
        elif server.region == "Delhi":
            latency = random.uniform(0.020, 0.080)  # 20-80ms
        else:
            latency = random.uniform(0.050, 0.150)  # 50-150ms
        
        await asyncio.sleep(latency)
        
        # Simulate health check results
        if server.health == ServerHealth.UNHEALTHY and random.random() < 0.1:
            # 10% chance to recover from unhealthy
            status = "ok"
        elif server.health == ServerHealth.HEALTHY and random.random() < 0.05:
            # 5% chance to become unhealthy
            status = "error"
        else:
            # Maintain current status with some variation
            status = "ok" if server.health != ServerHealth.UNHEALTHY else "error"
        
        return {
            "status": status,
            "cpu_usage": random.uniform(10, 90),
            "memory_usage": random.uniform(20, 80),
            "active_connections": server.current_connections,
            "response_time_ms": latency * 1000
        }

class LoadBalancer:
    """Advanced distributed load balancer"""
    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.servers = {}  # server_id -> ServerNode
        self.healthy_servers = []  # List of healthy server IDs
        
        # Algorithm-specific state
        self.round_robin_index = 0
        self.weighted_round_robin_weights = {}
        self.weighted_round_robin_current = {}
        
        # Performance tracking
        self.stats = LoadBalancerStats()
        self.request_history = deque(maxlen=10000)
        
        # Health monitoring
        self.health_checker = HealthChecker()
        self.health_monitoring_task = None
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info(f"⚖️ Load balancer initialized with {algorithm.value} algorithm")
    
    def add_server(self, server: ServerNode):
        """Add backend server to load balancer"""
        with self.lock:
            self.servers[server.server_id] = server
            self.health_checker.add_server(server)
            self._update_healthy_servers()
            
            # Initialize algorithm-specific data
            if self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                self.weighted_round_robin_weights[server.server_id] = server.weight
                self.weighted_round_robin_current[server.server_id] = 0
            
            logger.info(f"➕ Added server {server.server_id} ({server.endpoint}) to load balancer")
    
    def remove_server(self, server_id: str):
        """Remove backend server from load balancer"""
        with self.lock:
            if server_id in self.servers:
                del self.servers[server_id]
                self.health_checker.remove_server(server_id)
                self._update_healthy_servers()
                
                # Clean up algorithm-specific data
                if server_id in self.weighted_round_robin_weights:
                    del self.weighted_round_robin_weights[server_id]
                if server_id in self.weighted_round_robin_current:
                    del self.weighted_round_robin_current[server_id]
                
                logger.info(f"➖ Removed server {server_id} from load balancer")
    
    def _update_healthy_servers(self):
        """Update list of healthy servers"""
        self.healthy_servers = [
            server_id for server_id, server in self.servers.items()
            if server.health in [ServerHealth.HEALTHY, ServerHealth.DEGRADED]
        ]
        logger.debug(f"🏥 Updated healthy servers: {len(self.healthy_servers)}/{len(self.servers)}")
    
    async def start(self):
        """Start load balancer and health monitoring"""
        # Start health monitoring
        self.health_monitoring_task = asyncio.create_task(
            self.health_checker.start_monitoring()
        )
        logger.info("🚀 Load balancer started")
    
    def stop(self):
        """Stop load balancer and health monitoring"""
        self.health_checker.stop_monitoring()
        if self.health_monitoring_task:
            self.health_monitoring_task.cancel()
        logger.info("🛑 Load balancer stopped")
    
    async def route_request(self, request: RequestInfo) -> Optional[ServerNode]:
        """Route request to optimal backend server"""
        with self.lock:
            # Update healthy servers based on current health status
            self._update_healthy_servers()
            
            if not self.healthy_servers:
                logger.error("❌ No healthy servers available")
                self.stats.failed_requests += 1
                return None
            
            # Select server based on algorithm
            selected_server = self._select_server(request)
            
            if selected_server:
                # Update connection count
                selected_server.current_connections += 1
                
                # Update statistics
                self.stats.total_requests += 1
                self.stats.requests_per_server[selected_server.server_id] += 1
                
                # Store request in history
                self.request_history.append({
                    "request_id": request.request_id,
                    "server_id": selected_server.server_id,
                    "timestamp": request.timestamp,
                    "client_ip": request.client_ip
                })
                
                logger.debug(f"🎯 Routed request {request.request_id} to {selected_server.server_id}")
                
            return selected_server
    
    def _select_server(self, request: RequestInfo) -> Optional[ServerNode]:
        """Select server based on load balancing algorithm"""
        if not self.healthy_servers:
            return None
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin_select()
        
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select()
        
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select()
        
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash_select(request.client_ip)
        
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._least_response_time_select()
        
        elif self.algorithm == LoadBalancingAlgorithm.RESOURCE_BASED:
            return self._resource_based_select()
        
        else:
            # Default to round robin
            return self._round_robin_select()
    
    def _round_robin_select(self) -> ServerNode:
        """Round robin server selection"""
        server_id = self.healthy_servers[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.healthy_servers)
        return self.servers[server_id]
    
    def _least_connections_select(self) -> ServerNode:
        """Select server with least connections"""
        min_connections = float('inf')
        selected_server = None
        
        for server_id in self.healthy_servers:
            server = self.servers[server_id]
            if server.current_connections < min_connections:
                min_connections = server.current_connections
                selected_server = server
        
        return selected_server
    
    def _weighted_round_robin_select(self) -> ServerNode:
        """Weighted round robin selection"""
        # Find server with highest current weight
        max_current_weight = -1
        selected_server_id = None
        total_weight = 0
        
        for server_id in self.healthy_servers:
            if server_id in self.weighted_round_robin_current:
                weight = self.weighted_round_robin_weights.get(server_id, 1)
                total_weight += weight
                self.weighted_round_robin_current[server_id] += weight
                
                if self.weighted_round_robin_current[server_id] > max_current_weight:
                    max_current_weight = self.weighted_round_robin_current[server_id]
                    selected_server_id = server_id
        
        if selected_server_id:
            # Decrease selected server's current weight
            self.weighted_round_robin_current[selected_server_id] -= total_weight
            return self.servers[selected_server_id]
        
        # Fallback to round robin
        return self._round_robin_select()
    
    def _ip_hash_select(self, client_ip: str) -> ServerNode:
        """IP hash-based selection for session affinity"""
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        server_index = hash_value % len(self.healthy_servers)
        server_id = self.healthy_servers[server_index]
        return self.servers[server_id]
    
    def _least_response_time_select(self) -> ServerNode:
        """Select server with least average response time"""
        min_response_time = float('inf')
        selected_server = None
        
        for server_id in self.healthy_servers:
            server = self.servers[server_id]
            avg_response = server.avg_response_time
            
            if avg_response < min_response_time:
                min_response_time = avg_response
                selected_server = server
        
        return selected_server or self._round_robin_select()
    
    def _resource_based_select(self) -> ServerNode:
        """Select server based on resource utilization"""
        min_load_score = float('inf')
        selected_server = None
        
        for server_id in self.healthy_servers:
            server = self.servers[server_id]
            
            # Calculate composite load score
            cpu_score = server.cpu_usage / 100.0
            memory_score = server.memory_usage / 100.0
            connection_score = server.connection_utilization / 100.0
            response_score = min(server.avg_response_time / 1000.0, 1.0)  # Normalize to 0-1
            
            # Weighted composite score
            load_score = (cpu_score * 0.3 + memory_score * 0.2 + 
                         connection_score * 0.3 + response_score * 0.2)
            
            if load_score < min_load_score:
                min_load_score = load_score
                selected_server = server
        
        return selected_server or self._round_robin_select()
    
    async def complete_request(self, server: ServerNode, success: bool, response_time_ms: float):
        """Mark request as completed and update statistics"""
        with self.lock:
            # Update connection count
            server.current_connections = max(0, server.current_connections - 1)
            
            # Update statistics
            if success:
                self.stats.successful_requests += 1
                self.stats.total_response_time += response_time_ms
            else:
                self.stats.failed_requests += 1
            
            # Update server response times
            server.response_times.append(response_time_ms)
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics"""
        with self.lock:
            # Server statistics
            server_stats = {}
            for server_id, server in self.servers.items():
                health_history = self.health_checker.health_history.get(server_id, [])
                recent_health = health_history[-10:] if health_history else []
                
                server_stats[server_id] = {
                    "endpoint": server.endpoint,
                    "region": server.region,
                    "health": server.health.value,
                    "weight": server.weight,
                    "current_connections": server.current_connections,
                    "connection_utilization": server.connection_utilization,
                    "avg_response_time": server.avg_response_time,
                    "cpu_usage": server.cpu_usage,
                    "memory_usage": server.memory_usage,
                    "requests_handled": self.stats.requests_per_server.get(server_id, 0),
                    "last_health_check": server.last_health_check.isoformat() if server.last_health_check else None,
                    "recent_health_checks": len(recent_health)
                }
            
            return {
                "algorithm": self.algorithm.value,
                "total_servers": len(self.servers),
                "healthy_servers": len(self.healthy_servers),
                "total_requests": self.stats.total_requests,
                "successful_requests": self.stats.successful_requests,
                "failed_requests": self.stats.failed_requests,
                "success_rate": self.stats.success_rate,
                "avg_response_time": self.stats.avg_response_time,
                "requests_per_minute": len([r for r in self.request_history 
                                          if datetime.now() - r["timestamp"] < timedelta(minutes=1)]),
                "servers": server_stats,
                "timestamp": datetime.now().isoformat()
            }
    
    def print_dashboard(self):
        """Print load balancer dashboard"""
        stats = self.get_load_balancer_stats()
        
        print(f"\n{'='*80}")
        print(f"⚖️ DISTRIBUTED LOAD BALANCER DASHBOARD ⚖️")
        print(f"{'='*80}")
        
        print(f"🎯 Load Balancer Overview:")
        print(f"   Algorithm: {stats['algorithm']}")
        print(f"   Total Servers: {stats['total_servers']}")
        print(f"   Healthy Servers: {stats['healthy_servers']}")
        print(f"   Requests/Minute: {stats['requests_per_minute']}")
        
        print(f"\n📊 Request Statistics:")
        print(f"   Total Requests: {stats['total_requests']:,}")
        print(f"   Successful: {stats['successful_requests']:,}")
        print(f"   Failed: {stats['failed_requests']:,}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   Avg Response Time: {stats['avg_response_time']:.1f}ms")
        
        print(f"\n🖥️ Server Status:")
        for server_id, server_stats in stats['servers'].items():
            health_indicator = {
                "HEALTHY": "🟢",
                "DEGRADED": "🟡", 
                "UNHEALTHY": "🔴",
                "UNKNOWN": "⚪"
            }.get(server_stats['health'], "⚪")
            
            print(f"   {health_indicator} {server_id} ({server_stats['endpoint']}):")
            print(f"     Region: {server_stats['region']}")
            print(f"     Health: {server_stats['health']}")
            print(f"     Connections: {server_stats['current_connections']} ({server_stats['connection_utilization']:.1f}%)")
            print(f"     CPU: {server_stats['cpu_usage']:.1f}%")
            print(f"     Memory: {server_stats['memory_usage']:.1f}%")
            print(f"     Avg Response: {server_stats['avg_response_time']:.1f}ms")
            print(f"     Requests Handled: {server_stats['requests_handled']:,}")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

# Simulated backend servers
async def simulate_server_response(server: ServerNode, request: RequestInfo) -> Tuple[bool, float]:
    """Simulate backend server processing request"""
    # Base response time varies by region and server load
    base_latency = {
        "Mumbai": random.uniform(50, 200),
        "Delhi": random.uniform(80, 300),
        "Bangalore": random.uniform(60, 250),
        "Chennai": random.uniform(90, 350)
    }.get(server.region, random.uniform(100, 400))
    
    # Add load-based latency
    load_factor = (server.cpu_usage + server.memory_usage + server.connection_utilization) / 300
    actual_latency = base_latency * (1 + load_factor)
    
    await asyncio.sleep(actual_latency / 1000)  # Convert to seconds
    
    # Determine success based on server health
    success_probability = {
        ServerHealth.HEALTHY: 0.99,
        ServerHealth.DEGRADED: 0.95,
        ServerHealth.UNHEALTHY: 0.1,
        ServerHealth.UNKNOWN: 0.8
    }.get(server.health, 0.8)
    
    success = random.random() < success_probability
    
    return success, actual_latency

async def simulate_traffic_load(load_balancer: LoadBalancer, duration_minutes: int = 5):
    """Simulate realistic traffic load with Indian patterns"""
    logger.info(f"🚦 Starting traffic simulation for {duration_minutes} minutes")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    request_count = 0
    
    # Indian user IPs (simulated)
    indian_ips = [
        "103.21.244." + str(random.randint(1, 254)),
        "117.239.104." + str(random.randint(1, 254)),
        "27.109.11." + str(random.randint(1, 254)),
        "122.162.144." + str(random.randint(1, 254))
    ]
    
    try:
        while time.time() < end_time:
            # Simulate traffic patterns
            current_hour = datetime.now().hour
            
            if 9 <= current_hour <= 11 or 14 <= current_hour <= 16 or 20 <= current_hour <= 22:
                # Peak hours - higher traffic
                requests_per_second = random.randint(20, 50)
            else:
                # Normal hours
                requests_per_second = random.randint(5, 20)
            
            # Generate and process requests
            tasks = []
            for _ in range(requests_per_second):
                request = RequestInfo(
                    request_id=f"REQ_{int(time.time())}{random.randint(1000, 9999)}",
                    client_ip=random.choice(indian_ips),
                    method=random.choice(["GET", "POST", "PUT"]),
                    path=random.choice(["/api/users", "/api/orders", "/api/products", "/api/search"]),
                    headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
                    user_id=f"user_{random.randint(10000, 99999)}"
                )
                
                task = process_request(load_balancer, request)
                tasks.append(task)
                request_count += 1
            
            # Process requests concurrently
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Print dashboard every 30 seconds
            if request_count % 500 == 0:
                load_balancer.print_dashboard()
            
            await asyncio.sleep(1.0)
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    
    logger.info(f"🏁 Traffic simulation completed! Processed {request_count} requests")
    
    # Final dashboard
    load_balancer.print_dashboard()

async def process_request(load_balancer: LoadBalancer, request: RequestInfo):
    """Process individual request through load balancer"""
    start_time = time.time()
    
    try:
        # Route request to backend server
        server = await load_balancer.route_request(request)
        
        if not server:
            logger.error(f"❌ No server available for request {request.request_id}")
            return
        
        # Simulate server processing
        success, response_time = await simulate_server_response(server, request)
        
        # Complete request
        await load_balancer.complete_request(server, success, response_time)
        
        total_time = (time.time() - start_time) * 1000
        
        if success:
            logger.debug(f"✅ Request {request.request_id} completed in {total_time:.1f}ms via {server.server_id}")
        else:
            logger.warning(f"❌ Request {request.request_id} failed on {server.server_id}")
            
    except Exception as e:
        logger.error(f"❌ Error processing request {request.request_id}: {e}")

async def main():
    """Main demo function"""
    print("🇮🇳 Distributed Load Balancer System")
    print("⚖️ Advanced load balancing with health monitoring और multiple algorithms")
    print("🚦 Simulating high-traffic Indian application load balancing...\n")
    
    # Test different algorithms
    algorithms = [
        LoadBalancingAlgorithm.ROUND_ROBIN,
        LoadBalancingAlgorithm.LEAST_CONNECTIONS,
        LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
        LoadBalancingAlgorithm.RESOURCE_BASED
    ]
    
    for algorithm in algorithms[:1]:  # Test one algorithm for demo
        print(f"\n🧪 Testing {algorithm.value} Algorithm")
        print("="*50)
        
        # Initialize load balancer
        load_balancer = LoadBalancer(algorithm)
        
        # Add Indian region servers
        servers = [
            ServerNode("server_mumbai_1", "app1.mumbai.company.com", 8080, weight=3, region="Mumbai"),
            ServerNode("server_mumbai_2", "app2.mumbai.company.com", 8080, weight=3, region="Mumbai"),
            ServerNode("server_delhi_1", "app1.delhi.company.com", 8080, weight=2, region="Delhi"),
            ServerNode("server_delhi_2", "app2.delhi.company.com", 8080, weight=2, region="Delhi"),
            ServerNode("server_bangalore_1", "app1.bangalore.company.com", 8080, weight=1, region="Bangalore"),
            ServerNode("server_chennai_1", "app1.chennai.company.com", 8080, weight=1, region="Chennai"),
        ]
        
        for server in servers:
            load_balancer.add_server(server)
        
        try:
            # Start load balancer
            await load_balancer.start()
            
            # Show initial status
            load_balancer.print_dashboard()
            
            # Simulate traffic
            await simulate_traffic_load(load_balancer, duration_minutes=2)
            
        finally:
            # Stop load balancer
            load_balancer.stop()
    
    print(f"\n🎯 SIMULATION COMPLETED!")
    print(f"💡 Production system capabilities:")
    print(f"   - Multiple load balancing algorithms")
    print(f"   - Real-time health monitoring और automatic failover")
    print(f"   - Geographic server distribution")
    print(f"   - Session affinity और sticky connections")
    print(f"   - Resource-based intelligent routing")
    print(f"   - 99.99% availability with redundancy")

if __name__ == "__main__":
    # Run the distributed load balancer demo
    asyncio.run(main())