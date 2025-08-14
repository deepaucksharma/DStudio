#!/usr/bin/env python3
"""
Edge Load Balancer - एज पर लोड बैलेंसिंग
Mumbai local train platform management की तरह - traffic को efficiently distribute करना

Real-world inspired by AWS Application Load Balancer, NGINX Plus
Use cases: API load balancing, microservices traffic distribution, edge caching
Cost: Edge LB ₹10 per million requests vs Cloud LB ₹100 per million requests
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import statistics
import hashlib
import aiohttp
import random
import uuid
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "रोटेशन"              # Round-robin distribution
    WEIGHTED_ROUND_ROBIN = "भारित रोटेशन"  # Weighted round-robin
    LEAST_CONNECTIONS = "न्यूनतम कनेक्शन"   # Least connections first
    LEAST_RESPONSE_TIME = "न्यूनतम समय"    # Fastest response time
    IP_HASH = "आईपी हैश"               # IP hash-based
    GEOGRAPHIC = "भौगोलिक"             # Geographic proximity

class ServerStatus(Enum):
    """Backend server status"""
    HEALTHY = "स्वस्थ"        # Server is healthy
    UNHEALTHY = "अस्वस्थ"     # Server is unhealthy
    DRAINING = "निकासी"       # Server is draining connections
    MAINTENANCE = "रखरखाव"    # Server in maintenance mode

class RequestPriority(Enum):
    """Request priority levels"""
    LOW = "निम्न"           # Low priority
    NORMAL = "सामान्य"       # Normal priority  
    HIGH = "उच्च"           # High priority
    CRITICAL = "गंभीर"       # Critical priority

@dataclass
class BackendServer:
    """Backend server configuration"""
    server_id: str
    hostname: str
    port: int
    weight: int = 100  # Weight for weighted algorithms
    max_connections: int = 1000
    current_connections: int = 0
    status: ServerStatus = ServerStatus.HEALTHY
    health_check_url: str = "/health"
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    last_health_check: Optional[datetime] = None
    total_requests: int = 0
    failed_requests: int = 0
    location: Optional[str] = None  # Geographic location
    
    def __post_init__(self):
        self.base_url = f"http://{self.hostname}:{self.port}"
    
    @property
    def success_rate(self) -> float:
        """Calculate server success rate"""
        if self.total_requests == 0:
            return 100.0
        return ((self.total_requests - self.failed_requests) / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def is_available(self) -> bool:
        """Check if server is available for new requests"""
        return (self.status == ServerStatus.HEALTHY and 
                self.current_connections < self.max_connections)

@dataclass
class LoadBalancerRequest:
    """Load balancer request representation"""
    request_id: str
    client_ip: str
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[str] = None
    priority: RequestPriority = RequestPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    target_server: Optional[str] = None
    processing_time_ms: Optional[float] = None

class EdgeLoadBalancer:
    """
    Edge Load Balancer - Mumbai Railway Traffic Control की तरह
    Incoming requests को backend servers में efficiently distribute करना
    """
    
    def __init__(self, lb_id: str, location: str = "Mumbai", port: int = 8080):
        """
        Initialize Edge Load Balancer
        Args:
            lb_id: Unique load balancer identifier
            location: Geographic location
            port: Load balancer listening port
        """
        self.lb_id = lb_id
        self.location = location
        self.port = port
        
        # Backend server management
        self.backend_servers: Dict[str, BackendServer] = {}
        self.algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        self.round_robin_index = 0
        
        # Request tracking
        self.active_requests: Dict[str, LoadBalancerRequest] = {}
        self.request_history: deque = deque(maxlen=10000)
        self.request_queue = asyncio.Queue()
        
        # Health checking
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5    # seconds
        self.consecutive_failures_threshold = 3
        
        # Performance metrics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'requests_per_second': deque(maxlen=60),  # Last 60 seconds
            'response_times': deque(maxlen=1000),
            'bytes_transferred': 0,
            'active_connections': 0,
            'uptime_start': datetime.now(),
            'algorithm_switches': 0,
            'server_failures': defaultdict(int)
        }
        
        # Threading and async
        self.running = False
        self.worker_tasks = []
        self.session = None
        
        # Mumbai-specific configurations
        self._initialize_mumbai_config()
        
        logger.info(f"Edge Load Balancer initialized: {lb_id} @ {location}:{port}")
    
    def _initialize_mumbai_config(self):
        """Initialize Mumbai-specific load balancer configuration"""
        
        # Default health check settings for Mumbai network conditions
        self.health_check_config = {
            'interval_seconds': 30,
            'timeout_seconds': 10,  # Higher timeout for Mumbai network
            'failure_threshold': 3,
            'recovery_threshold': 2,
            'check_method': 'GET',
            'expected_status': [200, 201, 204]
        }
        
        # Traffic patterns for Mumbai (business hours consideration)
        self.traffic_patterns = {
            'business_hours': {
                'start': 9,   # 9 AM
                'end': 18,    # 6 PM
                'peak_multiplier': 3.0
            },
            'lunch_hours': {
                'start': 12,  # 12 PM
                'end': 14,    # 2 PM
                'peak_multiplier': 2.0
            },
            'weekend_traffic': 0.6  # 60% of weekday traffic
        }
        
        # Request routing rules
        self.routing_rules = [
            {
                'name': 'api_requests',
                'pattern': '/api/*',
                'algorithm': LoadBalancingAlgorithm.LEAST_RESPONSE_TIME,
                'priority': RequestPriority.HIGH
            },
            {
                'name': 'static_content',
                'pattern': '/static/*',
                'algorithm': LoadBalancingAlgorithm.IP_HASH,
                'priority': RequestPriority.LOW
            },
            {
                'name': 'user_uploads',
                'pattern': '/upload/*',
                'algorithm': LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                'priority': RequestPriority.NORMAL
            }
        ]
    
    async def start(self):
        """Start the load balancer"""
        if self.running:
            logger.warning("Load balancer already running")
            return
        
        self.running = True
        self.session = aiohttp.ClientSession()
        
        # Start worker tasks
        self.worker_tasks = [
            asyncio.create_task(self._request_processor_loop()),
            asyncio.create_task(self._health_checker_loop()),
            asyncio.create_task(self._metrics_collector_loop()),
            asyncio.create_task(self._auto_scaling_loop())
        ]
        
        logger.info(f"Edge Load Balancer started on port {self.port}")
    
    async def stop(self):
        """Stop the load balancer"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        try:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error stopping worker tasks: {str(e)}")
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info("Edge Load Balancer stopped")
    
    def add_backend_server(self, server: BackendServer) -> bool:
        """
        Add backend server to load balancer
        Mumbai local train में new coach add करने की तरह
        """
        try:
            if server.server_id in self.backend_servers:
                logger.warning(f"Server {server.server_id} already exists")
                return False
            
            self.backend_servers[server.server_id] = server
            logger.info(f"Backend server added: {server.server_id} ({server.hostname}:{server.port})")
            
            # Perform initial health check
            asyncio.create_task(self._check_server_health(server))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add backend server: {str(e)}")
            return False
    
    def remove_backend_server(self, server_id: str) -> bool:
        """Remove backend server from load balancer"""
        try:
            if server_id not in self.backend_servers:
                logger.warning(f"Server {server_id} not found")
                return False
            
            # Mark server for draining
            server = self.backend_servers[server_id]
            server.status = ServerStatus.DRAINING
            
            # Wait for active connections to complete (simplified)
            # In production, this would be more sophisticated
            del self.backend_servers[server_id]
            
            logger.info(f"Backend server removed: {server_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove backend server: {str(e)}")
            return False
    
    def set_algorithm(self, algorithm: LoadBalancingAlgorithm):
        """Change load balancing algorithm"""
        if self.algorithm != algorithm:
            self.algorithm = algorithm
            self.stats['algorithm_switches'] += 1
            logger.info(f"Load balancing algorithm changed to: {algorithm.value}")
    
    async def handle_request(self, request: LoadBalancerRequest) -> Tuple[int, str, Dict[str, str]]:
        """
        Handle incoming request
        Mumbai train platform की तरह - request को right destination भेजना
        """
        start_time = time.time()
        
        try:
            # Update statistics
            self.stats['total_requests'] += 1
            self.stats['active_connections'] += 1
            self.active_requests[request.request_id] = request
            
            # Apply routing rules
            routing_rule = self._match_routing_rule(request.path)
            if routing_rule:
                request.priority = routing_rule['priority']
                algorithm = routing_rule['algorithm']
            else:
                algorithm = self.algorithm
            
            # Select backend server
            target_server = await self._select_backend_server(request, algorithm)
            
            if not target_server:
                self.stats['failed_requests'] += 1
                return 503, "Service Unavailable - No healthy backends", {}
            
            request.target_server = target_server.server_id
            
            # Forward request to backend
            status_code, response_body, response_headers = await self._forward_request(
                target_server, request
            )
            
            # Update server metrics
            processing_time = (time.time() - start_time) * 1000
            target_server.response_times.append(processing_time)
            target_server.total_requests += 1
            
            if status_code >= 200 and status_code < 400:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
                target_server.failed_requests += 1
            
            # Update global metrics
            request.processing_time_ms = processing_time
            self.stats['response_times'].append(processing_time)
            self.stats['bytes_transferred'] += len(response_body.encode('utf-8'))
            
            return status_code, response_body, response_headers
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Request handling failed: {str(e)}")
            return 500, f"Internal Server Error: {str(e)}", {}
            
        finally:
            # Clean up
            self.stats['active_connections'] -= 1
            if request.request_id in self.active_requests:
                completed_request = self.active_requests.pop(request.request_id)
                self.request_history.append(completed_request)
    
    def _match_routing_rule(self, path: str) -> Optional[Dict[str, Any]]:
        """Match request path against routing rules"""
        for rule in self.routing_rules:
            pattern = rule['pattern'].replace('*', '.*')  # Convert to regex
            if path.startswith(pattern.replace('.*', '')):
                return rule
        return None
    
    async def _select_backend_server(self, request: LoadBalancerRequest, 
                                   algorithm: LoadBalancingAlgorithm) -> Optional[BackendServer]:
        """
        Select backend server using specified algorithm
        Mumbai train platform allocation की तरह - optimal server selection
        """
        try:
            available_servers = [
                server for server in self.backend_servers.values()
                if server.is_available
            ]
            
            if not available_servers:
                return None
            
            if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                return self._round_robin_selection(available_servers)
                
            elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(available_servers)
                
            elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return self._least_connections_selection(available_servers)
                
            elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                return self._least_response_time_selection(available_servers)
                
            elif algorithm == LoadBalancingAlgorithm.IP_HASH:
                return self._ip_hash_selection(available_servers, request.client_ip)
                
            elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
                return self._geographic_selection(available_servers, request.client_ip)
            
            else:
                # Default to round-robin
                return self._round_robin_selection(available_servers)
                
        except Exception as e:
            logger.error(f"Server selection failed: {str(e)}")
            return None
    
    def _round_robin_selection(self, servers: List[BackendServer]) -> BackendServer:
        """Round-robin server selection"""
        selected_server = servers[self.round_robin_index % len(servers)]
        self.round_robin_index += 1
        return selected_server
    
    def _weighted_round_robin_selection(self, servers: List[BackendServer]) -> BackendServer:
        """Weighted round-robin selection based on server weights"""
        total_weight = sum(server.weight for server in servers)
        random_weight = random.randint(1, total_weight)
        
        cumulative_weight = 0
        for server in servers:
            cumulative_weight += server.weight
            if random_weight <= cumulative_weight:
                return server
        
        return servers[0]  # Fallback
    
    def _least_connections_selection(self, servers: List[BackendServer]) -> BackendServer:
        """Select server with least active connections"""
        return min(servers, key=lambda s: s.current_connections)
    
    def _least_response_time_selection(self, servers: List[BackendServer]) -> BackendServer:
        """Select server with best response time"""
        servers_with_metrics = [s for s in servers if s.response_times]
        if not servers_with_metrics:
            return self._round_robin_selection(servers)
        
        return min(servers_with_metrics, key=lambda s: s.avg_response_time)
    
    def _ip_hash_selection(self, servers: List[BackendServer], client_ip: str) -> BackendServer:
        """Hash-based selection for session affinity"""
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        server_index = hash_value % len(servers)
        return servers[server_index]
    
    def _geographic_selection(self, servers: List[BackendServer], client_ip: str) -> BackendServer:
        """Geographic proximity-based selection (simplified)"""
        # In production, this would use actual geolocation
        mumbai_servers = [s for s in servers if s.location and 'mumbai' in s.location.lower()]
        if mumbai_servers:
            return self._least_response_time_selection(mumbai_servers)
        return self._least_response_time_selection(servers)
    
    async def _forward_request(self, server: BackendServer, 
                             request: LoadBalancerRequest) -> Tuple[int, str, Dict[str, str]]:
        """
        Forward request to backend server
        Mumbai train passenger को destination तक पहुंचाना
        """
        try:
            server.current_connections += 1
            
            # Build target URL
            target_url = f"{server.base_url}{request.path}"
            
            # Prepare headers
            headers = dict(request.headers)
            headers['X-Forwarded-For'] = request.client_ip
            headers['X-Load-Balancer'] = self.lb_id
            
            # Make HTTP request
            async with self.session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.body,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_body = await response.text()
                response_headers = dict(response.headers)
                
                return response.status, response_body, response_headers
                
        except asyncio.TimeoutError:
            server.failed_requests += 1
            return 504, "Gateway Timeout", {}
            
        except Exception as e:
            server.failed_requests += 1
            logger.error(f"Request forwarding failed: {str(e)}")
            return 502, f"Bad Gateway: {str(e)}", {}
            
        finally:
            server.current_connections = max(0, server.current_connections - 1)
    
    async def _request_processor_loop(self):
        """Background request processing loop"""
        logger.info("Request processor started")
        
        while self.running:
            try:
                # Calculate current RPS
                current_time = datetime.now()
                current_rps = self.stats['total_requests'] - sum(
                    list(self.stats['requests_per_second'])[-60:]  # Last minute
                )
                self.stats['requests_per_second'].append(current_rps)
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Request processor error: {str(e)}")
                await asyncio.sleep(5)
        
        logger.info("Request processor stopped")
    
    async def _health_checker_loop(self):
        """
        Background health checking loop
        Mumbai train maintenance check की तरह - regular server health monitoring
        """
        logger.info("Health checker started")
        
        while self.running:
            try:
                # Check health of all backend servers
                health_check_tasks = [
                    self._check_server_health(server)
                    for server in self.backend_servers.values()
                ]
                
                if health_check_tasks:
                    await asyncio.gather(*health_check_tasks, return_exceptions=True)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health checker error: {str(e)}")
                await asyncio.sleep(10)
        
        logger.info("Health checker stopped")
    
    async def _check_server_health(self, server: BackendServer):
        """Check health of individual server"""
        try:
            health_url = f"{server.base_url}{server.health_check_url}"
            
            start_time = time.time()
            async with self.session.get(
                health_url,
                timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                # Check if response is healthy
                if response.status in self.health_check_config['expected_status']:
                    if server.status != ServerStatus.HEALTHY:
                        server.status = ServerStatus.HEALTHY
                        logger.info(f"Server {server.server_id} back to healthy state")
                    
                    # Update response time metrics
                    server.response_times.append(response_time)
                else:
                    logger.warning(f"Server {server.server_id} health check failed: {response.status}")
                    await self._handle_server_failure(server)
                
                server.last_health_check = datetime.now()
                
        except asyncio.TimeoutError:
            logger.warning(f"Server {server.server_id} health check timeout")
            await self._handle_server_failure(server)
            
        except Exception as e:
            logger.error(f"Health check failed for {server.server_id}: {str(e)}")
            await self._handle_server_failure(server)
    
    async def _handle_server_failure(self, server: BackendServer):
        """Handle server failure"""
        try:
            self.stats['server_failures'][server.server_id] += 1
            
            # Mark server as unhealthy after consecutive failures
            consecutive_failures = self.stats['server_failures'][server.server_id]
            
            if consecutive_failures >= self.consecutive_failures_threshold:
                if server.status == ServerStatus.HEALTHY:
                    server.status = ServerStatus.UNHEALTHY
                    logger.error(f"Server {server.server_id} marked as unhealthy after {consecutive_failures} failures")
            
        except Exception as e:
            logger.error(f"Server failure handling error: {str(e)}")
    
    async def _metrics_collector_loop(self):
        """Collect and aggregate performance metrics"""
        logger.info("Metrics collector started")
        
        while self.running:
            try:
                # Clean up old metrics
                current_time = datetime.now()
                
                # Remove old request history (keep last 1 hour)
                cutoff_time = current_time - timedelta(hours=1)
                while (self.request_history and 
                       self.request_history[0].timestamp < cutoff_time):
                    self.request_history.popleft()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Metrics collector error: {str(e)}")
                await asyncio.sleep(60)
        
        logger.info("Metrics collector stopped")
    
    async def _auto_scaling_loop(self):
        """Auto-scaling based on traffic patterns"""
        logger.info("Auto-scaling monitor started")
        
        while self.running:
            try:
                # Analyze traffic patterns and suggest scaling
                current_hour = datetime.now().hour
                current_rps = (
                    self.stats['requests_per_second'][-1] 
                    if self.stats['requests_per_second'] else 0
                )
                
                # Check if we need to adjust algorithm based on load
                if current_rps > 1000:  # High traffic
                    if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                        self.set_algorithm(LoadBalancingAlgorithm.LEAST_RESPONSE_TIME)
                        logger.info("Switched to LEAST_RESPONSE_TIME due to high traffic")
                        
                elif current_rps < 100:  # Low traffic
                    if self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                        self.set_algorithm(LoadBalancingAlgorithm.ROUND_ROBIN)
                        logger.info("Switched to ROUND_ROBIN due to low traffic")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Auto-scaling error: {str(e)}")
                await asyncio.sleep(60)
        
        logger.info("Auto-scaling monitor stopped")
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics"""
        try:
            current_time = datetime.now()
            uptime = current_time - self.stats['uptime_start']
            
            # Calculate performance metrics
            total_requests = self.stats['total_requests']
            if total_requests > 0:
                success_rate = (self.stats['successful_requests'] / total_requests) * 100
                error_rate = (self.stats['failed_requests'] / total_requests) * 100
            else:
                success_rate = 0
                error_rate = 0
            
            # Average response time
            avg_response_time = (
                statistics.mean(self.stats['response_times'])
                if self.stats['response_times'] else 0
            )
            
            # Current RPS
            current_rps = (
                self.stats['requests_per_second'][-1]
                if self.stats['requests_per_second'] else 0
            )
            
            # Server statistics
            server_stats = {}
            healthy_servers = 0
            
            for server_id, server in self.backend_servers.items():
                server_stats[server_id] = {
                    'status': server.status.value,
                    'hostname': f"{server.hostname}:{server.port}",
                    'weight': server.weight,
                    'current_connections': server.current_connections,
                    'total_requests': server.total_requests,
                    'failed_requests': server.failed_requests,
                    'success_rate': server.success_rate,
                    'avg_response_time': server.avg_response_time,
                    'last_health_check': server.last_health_check.isoformat() if server.last_health_check else None
                }
                
                if server.status == ServerStatus.HEALTHY:
                    healthy_servers += 1
            
            return {
                "load_balancer_info": {
                    "lb_id": self.lb_id,
                    "location": self.location,
                    "port": self.port,
                    "algorithm": self.algorithm.value,
                    "uptime_hours": round(uptime.total_seconds() / 3600, 2),
                    "status": "running" if self.running else "stopped"
                },
                "performance_metrics": {
                    "total_requests": total_requests,
                    "successful_requests": self.stats['successful_requests'],
                    "failed_requests": self.stats['failed_requests'],
                    "success_rate_percent": round(success_rate, 2),
                    "error_rate_percent": round(error_rate, 2),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "current_rps": current_rps,
                    "active_connections": self.stats['active_connections'],
                    "bytes_transferred": self.stats['bytes_transferred']
                },
                "backend_servers": {
                    "total_servers": len(self.backend_servers),
                    "healthy_servers": healthy_servers,
                    "unhealthy_servers": len(self.backend_servers) - healthy_servers,
                    "server_details": server_stats
                },
                "algorithm_stats": {
                    "current_algorithm": self.algorithm.value,
                    "algorithm_switches": self.stats['algorithm_switches']
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get load balancer stats: {str(e)}")
            return {"error": str(e)}

# Mock backend server for testing
class MockBackendServer:
    """Mock backend server for testing purposes"""
    
    def __init__(self, server_id: str, port: int, response_delay: float = 0.1):
        self.server_id = server_id
        self.port = port
        self.response_delay = response_delay
        self.request_count = 0
        
    async def handle_request(self, request: LoadBalancerRequest) -> Tuple[int, str, Dict[str, str]]:
        """Simulate backend server request handling"""
        
        # Simulate processing delay
        await asyncio.sleep(self.response_delay)
        
        self.request_count += 1
        
        # Simulate occasional failures (5% failure rate)
        if random.random() < 0.05:
            return 500, "Internal Server Error", {"Content-Type": "text/plain"}
        
        # Simulate different response types
        if request.path.startswith('/api/'):
            response_body = json.dumps({
                "server_id": self.server_id,
                "request_count": self.request_count,
                "timestamp": datetime.now().isoformat(),
                "path": request.path
            })
            return 200, response_body, {"Content-Type": "application/json"}
        
        elif request.path == '/health':
            return 200, "OK", {"Content-Type": "text/plain"}
        
        else:
            return 200, f"Response from {self.server_id}", {"Content-Type": "text/plain"}

# Example usage and testing
async def main():
    """
    Comprehensive Edge Load Balancer testing
    Mumbai railway traffic management demonstration
    """
    print("⚖️ Edge Load Balancer - Mumbai Traffic Distribution")
    print("=" * 55)
    
    # Initialize load balancer
    load_balancer = EdgeLoadBalancer("mumbai-lb-01", "Mumbai Central", 8080)
    await load_balancer.start()
    
    print(f"✅ Load Balancer started: {load_balancer.lb_id}")
    print(f"🌐 Listening on port: {load_balancer.port}")
    print(f"📍 Location: {load_balancer.location}")
    
    # Add backend servers (Mumbai locations)
    print(f"\n🖥️ Adding Mumbai Backend Servers...")
    
    mumbai_servers = [
        BackendServer(
            server_id="mumbai_app_01",
            hostname="mumbai-app-01.local",
            port=3001,
            weight=100,
            max_connections=500,
            location="Mumbai Central"
        ),
        BackendServer(
            server_id="mumbai_app_02", 
            hostname="mumbai-app-02.local",
            port=3002,
            weight=150,  # Higher weight - more powerful server
            max_connections=750,
            location="Mumbai Central"
        ),
        BackendServer(
            server_id="mumbai_app_03",
            hostname="mumbai-app-03.local",
            port=3003,
            weight=80,   # Lower weight - less powerful
            max_connections=400,
            location="Navi Mumbai"
        ),
        BackendServer(
            server_id="mumbai_backup_01",
            hostname="mumbai-backup-01.local",
            port=3004,
            weight=60,
            max_connections=300,
            location="Thane"
        )
    ]
    
    # Add servers to load balancer
    for server in mumbai_servers:
        success = load_balancer.add_backend_server(server)
        status_emoji = "✅" if success else "❌"
        print(f"{status_emoji} {server.server_id}: {server.hostname}:{server.port} "
              f"(Weight: {server.weight}, Max Conn: {server.max_connections})")
    
    # Test different load balancing algorithms
    algorithms_to_test = [
        LoadBalancingAlgorithm.ROUND_ROBIN,
        LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
        LoadBalancingAlgorithm.LEAST_CONNECTIONS,
        LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
    ]
    
    print(f"\n🧪 Testing Load Balancing Algorithms...")
    
    for algorithm in algorithms_to_test:
        print(f"\n📊 Testing {algorithm.value}...")
        load_balancer.set_algorithm(algorithm)
        
        # Generate test requests
        test_requests = []
        for i in range(20):
            request = LoadBalancerRequest(
                request_id=f"test_{algorithm.name.lower()}_{i+1:03d}",
                client_ip=f"192.168.1.{100 + (i % 50)}",
                method="GET",
                path=f"/api/test/{i+1}",
                headers={"User-Agent": "LoadBalancer-Test/1.0"}
            )
            test_requests.append(request)
        
        # Process requests with mock backend
        request_results = []
        for request in test_requests:
            # Simulate request processing
            start_time = time.time()
            
            # Select backend server using current algorithm  
            selected_server = await load_balancer._select_backend_server(request, algorithm)
            
            if selected_server:
                # Simulate response
                processing_time = random.uniform(50, 200)  # 50-200ms
                selected_server.response_times.append(processing_time)
                selected_server.total_requests += 1
                selected_server.current_connections += 1
                
                # Simulate connection completion
                selected_server.current_connections = max(0, selected_server.current_connections - 1)
                
                request_results.append({
                    'request_id': request.request_id,
                    'target_server': selected_server.server_id,
                    'response_time': processing_time
                })
        
        # Analyze results
        server_distribution = {}
        total_response_time = 0
        
        for result in request_results:
            server_id = result['target_server']
            server_distribution[server_id] = server_distribution.get(server_id, 0) + 1
            total_response_time += result['response_time']
        
        avg_response_time = total_response_time / len(request_results)
        
        print(f"   📈 Results for {algorithm.value}:")
        print(f"   • Average Response Time: {avg_response_time:.1f}ms")
        print(f"   • Request Distribution:")
        
        for server_id, count in server_distribution.items():
            percentage = (count / len(request_results)) * 100
            print(f"     - {server_id}: {count} requests ({percentage:.1f}%)")
    
    # Simulate health check scenarios
    print(f"\n🏥 Simulating Server Health Scenarios...")
    
    # Mark one server as unhealthy
    mumbai_servers[2].status = ServerStatus.UNHEALTHY
    print(f"❌ Marked {mumbai_servers[2].server_id} as unhealthy")
    
    # Test load balancing with unhealthy server
    load_balancer.set_algorithm(LoadBalancingAlgorithm.ROUND_ROBIN)
    
    healthy_distribution = {}
    for i in range(15):
        request = LoadBalancerRequest(
            request_id=f"health_test_{i+1:03d}",
            client_ip=f"192.168.1.{120 + i}",
            method="GET", 
            path=f"/api/health_test/{i+1}",
            headers={}
        )
        
        selected_server = await load_balancer._select_backend_server(
            request, LoadBalancingAlgorithm.ROUND_ROBIN
        )
        
        if selected_server:
            server_id = selected_server.server_id
            healthy_distribution[server_id] = healthy_distribution.get(server_id, 0) + 1
    
    print(f"📊 Distribution with unhealthy server:")
    for server_id, count in healthy_distribution.items():
        percentage = (count / 15) * 100
        print(f"   • {server_id}: {count} requests ({percentage:.1f}%)")
    
    # Get comprehensive statistics
    print(f"\n📊 Load Balancer Performance Report:")
    print("=" * 45)
    
    stats = load_balancer.get_load_balancer_stats()
    
    # Load balancer info
    lb_info = stats["load_balancer_info"]
    print(f"Load Balancer: {lb_info['lb_id']} @ {lb_info['location']}")
    print(f"Algorithm: {lb_info['algorithm']}")
    print(f"Status: {lb_info['status']}")
    
    # Performance metrics (simulated)
    print(f"\n⚡ Performance Metrics:")
    print(f"• Algorithm Switches: {stats['algorithm_stats']['algorithm_switches']}")
    print(f"• Active Connections: 0 (test environment)")
    print(f"• Bytes Transferred: 0 (test environment)")
    
    # Backend server status
    backend_info = stats["backend_servers"]
    print(f"\n🖥️ Backend Server Status:")
    print(f"• Total Servers: {backend_info['total_servers']}")
    print(f"• Healthy Servers: {backend_info['healthy_servers']}")
    print(f"• Unhealthy Servers: {backend_info['unhealthy_servers']}")
    
    print(f"\n📋 Server Details:")
    for server_id, server_details in backend_info['server_details'].items():
        status_emoji = {"स्वस्थ": "🟢", "अस्वस्थ": "🔴", "निकासी": "🟡", "रखरखाव": "🟠"}
        status = server_details['status']
        
        print(f"{status_emoji.get(status, '🔵')} {server_id}")
        print(f"   Host: {server_details['hostname']}")
        print(f"   Weight: {server_details['weight']}")
        print(f"   Status: {status}")
        print(f"   Total Requests: {server_details['total_requests']}")
        if server_details['total_requests'] > 0:
            print(f"   Success Rate: {server_details['success_rate']:.1f}%")
            print(f"   Avg Response Time: {server_details['avg_response_time']:.1f}ms")
    
    # Cost analysis
    print(f"\n💰 Cost Analysis (Monthly):")
    print("-" * 25)
    
    # Simulate monthly request volume
    monthly_requests = 10_000_000  # 10 million requests per month
    
    edge_lb_cost = (monthly_requests / 1_000_000) * 10   # ₹10 per million requests
    cloud_lb_cost = (monthly_requests / 1_000_000) * 100 # ₹100 per million requests
    savings = cloud_lb_cost - edge_lb_cost
    
    print(f"Edge LB Cost: ₹{edge_lb_cost:,.0f}/month")
    print(f"Cloud LB Cost: ₹{cloud_lb_cost:,.0f}/month")
    print(f"Monthly Savings: ₹{savings:,.0f}")
    print(f"Savings Percentage: {(savings/cloud_lb_cost)*100:.1f}%")
    
    # Business benefits
    print(f"\n🎯 Business Benefits:")
    print("• Local traffic distribution reduces latency")
    print("• Intelligent algorithm switching based on load")
    print("• Automated health checking and failover")
    print("• Geographic load balancing for Mumbai region")
    print("• Cost-effective compared to cloud load balancers")
    print("• Real-time performance monitoring and metrics")
    
    # Mumbai-specific advantages
    print(f"\n🏙️ Mumbai-Specific Advantages:")
    print("• Optimized for Mumbai network conditions")
    print("• Business hours traffic pattern awareness")
    print("• Local server preference for reduced latency")
    print("• Monsoon-resilient failover mechanisms")
    print("• Cost savings in INR for Indian businesses")
    
    # Stop load balancer
    print(f"\n🛑 Stopping load balancer...")
    await load_balancer.stop()
    
    print(f"\n✅ Edge Load Balancer demonstration completed!")
    print(f"⚖️ Mumbai traffic distribution optimized with intelligent load balancing!")

if __name__ == "__main__":
    asyncio.run(main())