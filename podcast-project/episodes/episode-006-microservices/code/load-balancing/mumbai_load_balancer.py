#!/usr/bin/env python3
"""
Load Balancing Strategies for Mumbai-scale Traffic
Multiple algorithms for distributing traffic like Mumbai transport system

जैसे Mumbai में different routes available होते हैं same destination ke लिए,
वैसे ही load balancer different servers पर traffic distribute करता है
"""

import asyncio
import time
import random
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import aiohttp
import statistics
from datetime import datetime, timedelta

# Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MumbaiLoadBalancer")

class ServerStatus(Enum):
    """Server health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"  # Like train going out of service
    MAINTENANCE = "maintenance"

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    GEOGRAPHIC_HASH = "geographic_hash"  # Mumbai-specific
    RESPONSE_TIME = "response_time"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"
    CONSISTENT_HASH = "consistent_hash"

@dataclass
class ServerNode:
    """Individual server node - जैसे Mumbai local train coach"""
    server_id: str
    host: str
    port: int
    weight: int = 100  # Default weight
    status: ServerStatus = ServerStatus.HEALTHY
    current_connections: int = 0
    max_connections: int = 1000
    region: str = "mumbai-central"
    
    # Performance metrics
    response_times: List[float] = field(default_factory=list)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    error_count: int = 0
    last_health_check: datetime = field(default_factory=datetime.now)
    
    def get_avg_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times[-100:])  # Last 100 requests
    
    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        if self.request_count == 0:
            return 100.0
        return ((self.request_count - self.error_count) / self.request_count) * 100
    
    def get_load_score(self) -> float:
        """Get overall load score (0-100, lower is better)"""
        connection_load = (self.current_connections / self.max_connections) * 100
        cpu_load = self.cpu_usage
        memory_load = self.memory_usage
        response_load = min(self.get_avg_response_time() * 10, 100)  # Response time in 100ms units
        
        return (connection_load + cpu_load + memory_load + response_load) / 4
    
    def is_available(self) -> bool:
        """Check if server is available for requests"""
        return (self.status == ServerStatus.HEALTHY and 
                self.current_connections < self.max_connections)

@dataclass 
class Request:
    """Incoming request"""
    request_id: str
    client_ip: str
    path: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    region: str = "mumbai"
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None

class LoadBalancer(ABC):
    """Base load balancer class"""
    
    def __init__(self, name: str, servers: List[ServerNode]):
        self.name = name
        self.servers = {server.server_id: server for server in servers}
        self.request_count = 0
        self.start_time = datetime.now()
    
    @abstractmethod
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        """Select best server for the request"""
        pass
    
    def get_healthy_servers(self) -> List[ServerNode]:
        """Get list of healthy servers"""
        return [server for server in self.servers.values() if server.is_available()]

class RoundRobinBalancer(LoadBalancer):
    """
    Round Robin Load Balancer
    जैसे Mumbai local train platforms में trains की sequence
    """
    
    def __init__(self, servers: List[ServerNode]):
        super().__init__("Round Robin", servers)
        self.current_index = 0
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Simple round robin
        server = healthy_servers[self.current_index % len(healthy_servers)]
        self.current_index += 1
        
        logger.debug(f"Round Robin selected: {server.server_id}")
        return server

class WeightedRoundRobinBalancer(LoadBalancer):
    """
    Weighted Round Robin - जैसे express trains को ज्यादा preference
    """
    
    def __init__(self, servers: List[ServerNode]):
        super().__init__("Weighted Round Robin", servers)
        self.current_weights = {}
        self.reset_weights()
    
    def reset_weights(self):
        """Reset current weights to server weights"""
        for server in self.servers.values():
            self.current_weights[server.server_id] = server.weight
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Find server with highest current weight
        max_weight = -1
        selected_server = None
        
        for server in healthy_servers:
            if self.current_weights[server.server_id] > max_weight:
                max_weight = self.current_weights[server.server_id]
                selected_server = server
        
        if selected_server:
            # Decrease selected server's current weight
            self.current_weights[selected_server.server_id] -= 1
            
            # Reset weights if all are zero
            if all(weight <= 0 for weight in self.current_weights.values()):
                self.reset_weights()
        
        logger.debug(f"Weighted RR selected: {selected_server.server_id if selected_server else None}")
        return selected_server

class LeastConnectionsBalancer(LoadBalancer):
    """
    Least Connections - जैसे सबसे कम crowded train coach choose करना
    """
    
    def __init__(self, servers: List[ServerNode]):
        super().__init__("Least Connections", servers)
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Select server with least connections
        selected_server = min(healthy_servers, key=lambda s: s.current_connections)
        
        logger.debug(f"Least Connections selected: {selected_server.server_id} ({selected_server.current_connections} conn)")
        return selected_server

class IPHashBalancer(LoadBalancer):
    """
    IP Hash - Same client always goes to same server
    जैसे specific train route preference
    """
    
    def __init__(self, servers: List[ServerNode]):
        super().__init__("IP Hash", servers)
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Hash client IP to consistently select same server
        ip_hash = int(hashlib.md5(request.client_ip.encode()).hexdigest(), 16)
        server_index = ip_hash % len(healthy_servers)
        selected_server = healthy_servers[server_index]
        
        logger.debug(f"IP Hash selected: {selected_server.server_id} for IP {request.client_ip}")
        return selected_server

class ResponseTimeBalancer(LoadBalancer):
    """
    Response Time Based - Select fastest server
    जैसे सबसे fast train route choose करना
    """
    
    def __init__(self, servers: List[ServerNode]):
        super().__init__("Response Time Based", servers)
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Select server with lowest average response time
        selected_server = min(healthy_servers, key=lambda s: s.get_avg_response_time())
        
        logger.debug(f"Response Time selected: {selected_server.server_id} ({selected_server.get_avg_response_time():.2f}ms avg)")
        return selected_server

class ResourceBasedBalancer(LoadBalancer):
    """
    Resource-based selection - Consider CPU, memory, connections
    जैसे train capacity के according seat allocation
    """
    
    def __init__(self, servers: List[ServerNode]):
        super().__init__("Resource Based", servers)
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Select server with lowest overall load score
        selected_server = min(healthy_servers, key=lambda s: s.get_load_score())
        
        logger.debug(f"Resource Based selected: {selected_server.server_id} (load: {selected_server.get_load_score():.1f})")
        return selected_server

class GeographicHashBalancer(LoadBalancer):
    """
    Geographic Hash - Mumbai-specific regional routing
    जैसे local area के servers को preference
    """
    
    def __init__(self, servers: List[ServerNode]):
        super().__init__("Geographic Hash", servers)
        
        # Mumbai regions mapping
        self.region_preferences = {
            "mumbai-central": ["mumbai-central", "mumbai-south", "mumbai-north"],
            "mumbai-west": ["mumbai-west", "mumbai-central", "mumbai-north"],
            "mumbai-east": ["mumbai-east", "mumbai-central", "mumbai-west"],
            "navi-mumbai": ["navi-mumbai", "mumbai-east", "mumbai-central"]
        }
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Prefer servers in same region first
        preferred_regions = self.region_preferences.get(request.region, [request.region])
        
        for region in preferred_regions:
            regional_servers = [s for s in healthy_servers if s.region == region]
            if regional_servers:
                # Use least connections within preferred region
                selected_server = min(regional_servers, key=lambda s: s.current_connections)
                logger.debug(f"Geographic selected: {selected_server.server_id} in region {region}")
                return selected_server
        
        # Fallback to any healthy server
        selected_server = healthy_servers[0]
        logger.debug(f"Geographic fallback: {selected_server.server_id}")
        return selected_server

class ConsistentHashBalancer(LoadBalancer):
    """
    Consistent Hashing - Minimal disruption when servers added/removed
    जैसे Mumbai train routes में resilience
    """
    
    def __init__(self, servers: List[ServerNode], virtual_nodes: int = 100):
        super().__init__("Consistent Hash", servers)
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self.rebuild_ring()
    
    def rebuild_ring(self):
        """Rebuild the consistent hash ring"""
        self.ring.clear()
        
        for server in self.servers.values():
            for i in range(self.virtual_nodes):
                virtual_key = f"{server.server_id}:{i}"
                hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                self.ring[hash_value] = server
        
        self.sorted_keys = sorted(self.ring.keys())
        logger.info(f"Rebuilt hash ring with {len(self.ring)} virtual nodes")
    
    async def select_server(self, request: Request) -> Optional[ServerNode]:
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            return None
        
        # Hash the request key (IP + path for stickiness)
        request_key = f"{request.client_ip}:{request.path}"
        request_hash = int(hashlib.md5(request_key.encode()).hexdigest(), 16)
        
        # Find the first server on or after this hash value
        for key in self.sorted_keys:
            if key >= request_hash:
                server = self.ring[key]
                if server.is_available():
                    logger.debug(f"Consistent Hash selected: {server.server_id}")
                    return server
        
        # Wrap around to the first server
        if self.sorted_keys:
            server = self.ring[self.sorted_keys[0]]
            if server.is_available():
                logger.debug(f"Consistent Hash wrapped: {server.server_id}")
                return server
        
        return None

class MumbaiLoadBalancerManager:
    """
    Main load balancer manager - जैसे Mumbai transport control center
    """
    
    def __init__(self):
        self.balancers: Dict[str, LoadBalancer] = {}
        self.current_balancer: Optional[LoadBalancer] = None
        self.health_check_interval = 30  # seconds
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0
        }
    
    def add_balancer(self, algorithm: LoadBalancingAlgorithm, servers: List[ServerNode]):
        """Add a load balancer with specific algorithm"""
        balancer_map = {
            LoadBalancingAlgorithm.ROUND_ROBIN: RoundRobinBalancer,
            LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinBalancer,
            LoadBalancingAlgorithm.LEAST_CONNECTIONS: LeastConnectionsBalancer,
            LoadBalancingAlgorithm.IP_HASH: IPHashBalancer,
            LoadBalancingAlgorithm.RESPONSE_TIME: ResponseTimeBalancer,
            LoadBalancingAlgorithm.RESOURCE_BASED: ResourceBasedBalancer,
            LoadBalancingAlgorithm.GEOGRAPHIC_HASH: GeographicHashBalancer,
            LoadBalancingAlgorithm.CONSISTENT_HASH: ConsistentHashBalancer,
        }
        
        if algorithm in balancer_map:
            balancer = balancer_map[algorithm](servers)
            self.balancers[algorithm.value] = balancer
            
            if not self.current_balancer:
                self.current_balancer = balancer
            
            logger.info(f"Added {algorithm.value} load balancer with {len(servers)} servers")
    
    def switch_algorithm(self, algorithm: LoadBalancingAlgorithm):
        """Switch to different load balancing algorithm"""
        if algorithm.value in self.balancers:
            self.current_balancer = self.balancers[algorithm.value]
            logger.info(f"Switched to {algorithm.value} load balancing")
            return True
        return False
    
    async def handle_request(self, request: Request) -> Dict[str, Any]:
        """Handle incoming request with load balancing"""
        if not self.current_balancer:
            return {"error": "No load balancer configured", "status": 503}
        
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Select server using current algorithm
            selected_server = await self.current_balancer.select_server(request)
            
            if not selected_server:
                self.stats['failed_requests'] += 1
                return {
                    "error": "No healthy servers available", 
                    "status": 503,
                    "message": "All Mumbai servers are busy - like peak hour traffic!"
                }
            
            # Simulate request processing
            selected_server.current_connections += 1
            selected_server.request_count += 1
            
            # Simulate network request to selected server
            response_time = await self.simulate_server_request(selected_server, request)
            
            # Record response time
            selected_server.response_times.append(response_time)
            if len(selected_server.response_times) > 1000:
                selected_server.response_times = selected_server.response_times[-1000:]
            
            # Update stats
            total_time = (time.time() - start_time) * 1000
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (self.stats['total_requests'] - 1) + total_time) / 
                self.stats['total_requests']
            )
            self.stats['successful_requests'] += 1
            
            return {
                "status": 200,
                "server": selected_server.server_id,
                "region": selected_server.region,
                "response_time_ms": response_time,
                "algorithm": self.current_balancer.name,
                "message": f"Request processed by {selected_server.server_id} - Mumbai efficiency!"
            }
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Request handling error: {str(e)}")
            return {"error": str(e), "status": 500}
        
        finally:
            if selected_server:
                selected_server.current_connections = max(0, selected_server.current_connections - 1)
    
    async def simulate_server_request(self, server: ServerNode, request: Request) -> float:
        """Simulate actual server request processing"""
        # Base response time varies by server load
        base_time = 50 + (server.get_load_score() * 2)  # 50-250ms base
        
        # Add random variation
        variation = random.uniform(0.8, 1.5)
        response_time = base_time * variation
        
        # Simulate occasional slow responses
        if random.random() < 0.05:  # 5% chance of slow response
            response_time *= 3
        
        # Simulate network delay
        await asyncio.sleep(response_time / 1000.0)
        
        # Simulate occasional failures
        if random.random() < 0.02:  # 2% failure rate
            server.error_count += 1
            raise Exception("Simulated server error - like Mumbai monsoon disruption")
        
        return response_time
    
    async def health_check_servers(self):
        """Perform health checks on all servers - जैसे train maintenance check"""
        while True:
            try:
                for balancer in self.balancers.values():
                    for server in balancer.servers.values():
                        await self.check_server_health(server)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                await asyncio.sleep(5)
    
    async def check_server_health(self, server: ServerNode):
        """Check individual server health"""
        try:
            # Simulate health check request
            start_time = time.time()
            
            # Simulate health check response time
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
            health_response_time = (time.time() - start_time) * 1000
            
            # Update server metrics (simulated)
            server.cpu_usage = random.uniform(10, 90)
            server.memory_usage = random.uniform(20, 80)
            server.last_health_check = datetime.now()
            
            # Determine health status
            if health_response_time > 1000 or server.cpu_usage > 95 or server.memory_usage > 95:
                server.status = ServerStatus.UNHEALTHY
            elif server.cpu_usage > 80 or server.memory_usage > 80:
                server.status = ServerStatus.DRAINING
            else:
                server.status = ServerStatus.HEALTHY
            
        except Exception as e:
            logger.warning(f"Health check failed for {server.server_id}: {str(e)}")
            server.status = ServerStatus.UNHEALTHY
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        uptime = datetime.now() - self.current_balancer.start_time if self.current_balancer else timedelta()
        
        server_stats = {}
        if self.current_balancer:
            for server in self.current_balancer.servers.values():
                server_stats[server.server_id] = {
                    "status": server.status.value,
                    "connections": server.current_connections,
                    "requests": server.request_count,
                    "errors": server.error_count,
                    "success_rate": f"{server.get_success_rate():.1f}%",
                    "avg_response_time": f"{server.get_avg_response_time():.1f}ms",
                    "load_score": f"{server.get_load_score():.1f}",
                    "cpu_usage": f"{server.cpu_usage:.1f}%",
                    "memory_usage": f"{server.memory_usage:.1f}%"
                }
        
        return {
            "current_algorithm": self.current_balancer.name if self.current_balancer else "None",
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.stats['total_requests'],
            "successful_requests": self.stats['successful_requests'],
            "failed_requests": self.stats['failed_requests'],
            "success_rate": f"{(self.stats['successful_requests'] / max(1, self.stats['total_requests'])) * 100:.1f}%",
            "avg_response_time": f"{self.stats['avg_response_time']:.1f}ms",
            "servers": server_stats
        }

async def demo_mumbai_load_balancer():
    """
    Demonstrate different load balancing algorithms
    Mumbai-style traffic distribution across multiple servers
    """
    print("\n=== Mumbai Load Balancer Demo ===")
    print("Different algorithms for distributing traffic like Mumbai transport system!")
    
    # Create servers representing Mumbai regions
    servers = [
        ServerNode("server_mumbai_central_1", "192.168.1.10", 8080, weight=150, region="mumbai-central"),
        ServerNode("server_mumbai_central_2", "192.168.1.11", 8080, weight=100, region="mumbai-central"),
        ServerNode("server_mumbai_west_1", "192.168.1.20", 8080, weight=120, region="mumbai-west"),
        ServerNode("server_mumbai_west_2", "192.168.1.21", 8080, weight=100, region="mumbai-west"),
        ServerNode("server_mumbai_east_1", "192.168.1.30", 8080, weight=80, region="mumbai-east"),
        ServerNode("server_navi_mumbai_1", "192.168.1.40", 8080, weight=90, region="navi-mumbai"),
    ]
    
    # Initialize load balancer manager
    manager = MumbaiLoadBalancerManager()
    
    # Add different algorithms
    algorithms = [
        LoadBalancingAlgorithm.ROUND_ROBIN,
        LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
        LoadBalancingAlgorithm.LEAST_CONNECTIONS,
        LoadBalancingAlgorithm.IP_HASH,
        LoadBalancingAlgorithm.RESPONSE_TIME,
        LoadBalancingAlgorithm.RESOURCE_BASED,
        LoadBalancingAlgorithm.GEOGRAPHIC_HASH,
        LoadBalancingAlgorithm.CONSISTENT_HASH,
    ]
    
    for algorithm in algorithms:
        manager.add_balancer(algorithm, servers)
    
    # Start health checking
    health_task = asyncio.create_task(manager.health_check_servers())
    
    # Demo different algorithms
    for algorithm in algorithms[:4]:  # Test first 4 algorithms
        print(f"\n--- Testing {algorithm.value.title()} Algorithm ---")
        manager.switch_algorithm(algorithm)
        
        # Create sample requests from different regions
        sample_requests = [
            Request("req_001", "192.168.1.100", "/api/products", region="mumbai-central"),
            Request("req_002", "192.168.1.101", "/api/orders", region="mumbai-west"),
            Request("req_003", "192.168.1.102", "/api/search", region="mumbai-east"),
            Request("req_004", "192.168.1.100", "/api/products", region="mumbai-central"),  # Same IP for hash testing
            Request("req_005", "192.168.1.103", "/api/checkout", region="navi-mumbai"),
            Request("req_006", "192.168.1.101", "/api/profile", region="mumbai-west"),
        ]
        
        # Process requests
        for i, request in enumerate(sample_requests, 1):
            response = await manager.handle_request(request)
            if response.get("status") == 200:
                print(f"  Request {i}: → {response['server']} ({response['region']}) - {response['response_time_ms']:.1f}ms")
            else:
                print(f"  Request {i}: ❌ {response.get('error', 'Unknown error')}")
            
            # Small delay between requests
            await asyncio.sleep(0.1)
    
    # Show final statistics
    print(f"\n--- Load Balancer Statistics ---")
    stats = manager.get_stats()
    
    print(f"Current Algorithm: {stats['current_algorithm']}")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Success Rate: {stats['success_rate']}")
    print(f"Average Response Time: {stats['avg_response_time']}")
    
    print(f"\nServer Performance:")
    for server_id, server_stats in stats['servers'].items():
        status_emoji = "✅" if server_stats['status'] == 'healthy' else "⚠️"
        print(f"  {status_emoji} {server_id}: {server_stats['requests']} requests, "
              f"{server_stats['success_rate']} success, {server_stats['avg_response_time']} avg")
    
    # Demonstrate algorithm switching
    print(f"\n--- Algorithm Switching Demo ---")
    print("Switching between algorithms based on traffic patterns...")
    
    # High traffic scenario - use resource-based
    print("High traffic detected → Switching to Resource-Based algorithm")
    manager.switch_algorithm(LoadBalancingAlgorithm.RESOURCE_BASED)
    
    # Process high traffic
    high_traffic_requests = [Request(f"req_high_{i}", f"192.168.1.{100+i}", "/api/sale") 
                           for i in range(10)]
    
    for request in high_traffic_requests:
        response = await manager.handle_request(request)
        if response.get("status") == 200:
            server_load = next(s.get_load_score() for s in servers if s.server_id == response['server'])
            print(f"  High traffic → {response['server']} (load: {server_load:.1f})")
        await asyncio.sleep(0.05)
    
    # Geographic traffic - use geographic hash
    print("\nGeographic traffic detected → Switching to Geographic Hash")
    manager.switch_algorithm(LoadBalancingAlgorithm.GEOGRAPHIC_HASH)
    
    geo_requests = [
        Request("geo_1", "192.168.1.200", "/api/local", region="mumbai-central"),
        Request("geo_2", "192.168.1.201", "/api/local", region="mumbai-west"),
        Request("geo_3", "192.168.1.202", "/api/local", region="navi-mumbai"),
    ]
    
    for request in geo_requests:
        response = await manager.handle_request(request)
        if response.get("status") == 200:
            print(f"  {request.region} → {response['server']} ({response['region']})")
    
    # Show algorithm comparison
    print(f"\n--- Algorithm Comparison Summary ---")
    print("✅ Round Robin: Simple, equal distribution - like Mumbai local train sequence")
    print("✅ Weighted Round Robin: Server capacity awareness - like express vs local trains")  
    print("✅ Least Connections: Dynamic load balancing - like choosing less crowded coach")
    print("✅ IP Hash: Session stickiness - like regular commuter route preference")
    print("✅ Response Time: Performance optimization - like fastest route selection")
    print("✅ Resource Based: Comprehensive health - like train capacity + condition")
    print("✅ Geographic Hash: Regional optimization - like Mumbai local zone system")
    print("✅ Consistent Hash: Fault tolerance - like Mumbai transport resilience")
    
    print(f"\n🚂 Mumbai Load Balancer Demo completed!")
    print(f"   Different algorithms suited for different traffic patterns")
    print(f"   Like Mumbai transport system - multiple routes, optimal distribution!")
    
    # Cleanup
    health_task.cancel()

if __name__ == "__main__":
    print("Starting Mumbai Load Balancer Demo...")
    asyncio.run(demo_mumbai_load_balancer())