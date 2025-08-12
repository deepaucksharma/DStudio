#!/usr/bin/env python3
"""
Weighted Load Balancer for Regional Server Capacity
क्षेत्रीय सर्वर क्षमता के लिए weighted load balancing

यह example दिखाता है कि कैसे विभिन्न regions में servers की अलग-अलग
capacities के आधार पर weighted load balancing implement करें।
"""

import time
import random
import threading
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import heapq
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class WeightedServer:
    """Weighted server with capacity and performance metrics"""
    server_id: str
    name: str
    host: str
    region: str
    base_weight: int  # Static weight based on capacity
    current_weight: int  # Dynamic weight for selection
    max_capacity: int
    current_load: int = 0
    is_healthy: bool = True
    
    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time_ms: float = 0.0
    success_rate: float = 100.0
    
    # Traffic metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_selected: float = field(default_factory=time.time)
    
    # Regional factors
    network_latency_ms: float = 0.0
    peak_hour_multiplier: float = 1.0


@dataclass 
class Request:
    """Generic request structure"""
    request_id: str
    user_region: str
    request_type: str
    priority: int = 1  # 1=normal, 2=high, 3=critical
    timestamp: float = field(default_factory=time.time)
    estimated_processing_time: float = 0.1


class RegionalWeightedLoadBalancer:
    """
    क्षेत्रीय weighted load balancer
    भारतीय regions के लिए optimized
    """
    
    def __init__(self):
        self.servers: List[WeightedServer] = []
        self.region_preferences: Dict[str, List[str]] = {}
        self.lock = threading.Lock()
        self.stats = defaultdict(int)
        
        # Initialize Indian regional servers
        self._initialize_regional_servers()
        self._setup_region_preferences()
        
        # Start background monitoring
        self._start_monitoring()
        
        logger.info("🌍 Regional Weighted Load Balancer initialized")
    
    def _initialize_regional_servers(self):
        """Initialize servers across Indian regions with different capacities"""
        
        regional_servers = [
            # North India - High capacity (Delhi NCR tech hub)
            WeightedServer(
                server_id="NORTH_PRIMARY",
                name="Delhi Primary Data Center",
                host="north-primary.india.com",
                region="North India",
                base_weight=100,  # Highest weight
                current_weight=100,
                max_capacity=15000,
                network_latency_ms=10.0
            ),
            
            WeightedServer(
                server_id="NORTH_SECONDARY", 
                name="Gurgaon Secondary Data Center",
                host="north-secondary.india.com",
                region="North India", 
                base_weight=80,
                current_weight=80,
                max_capacity=12000,
                network_latency_ms=15.0
            ),
            
            # West India - Very high capacity (Mumbai financial hub)
            WeightedServer(
                server_id="WEST_PRIMARY",
                name="Mumbai Primary Data Center",
                host="west-primary.india.com", 
                region="West India",
                base_weight=120,  # Highest due to financial traffic
                current_weight=120,
                max_capacity=18000,
                network_latency_ms=8.0
            ),
            
            WeightedServer(
                server_id="WEST_SECONDARY",
                name="Pune Secondary Data Center", 
                host="west-secondary.india.com",
                region="West India",
                base_weight=90,
                current_weight=90, 
                max_capacity=13000,
                network_latency_ms=12.0
            ),
            
            # South India - High capacity (Bangalore tech hub)
            WeightedServer(
                server_id="SOUTH_PRIMARY",
                name="Bangalore Primary Data Center",
                host="south-primary.india.com",
                region="South India", 
                base_weight=110,
                current_weight=110,
                max_capacity=16000,
                network_latency_ms=9.0
            ),
            
            WeightedServer(
                server_id="SOUTH_SECONDARY",
                name="Chennai Secondary Data Center",
                host="south-secondary.india.com", 
                region="South India",
                base_weight=85,
                current_weight=85,
                max_capacity=11000,
                network_latency_ms=14.0
            ),
            
            # East India - Medium capacity
            WeightedServer(
                server_id="EAST_PRIMARY", 
                name="Kolkata Data Center",
                host="east-primary.india.com",
                region="East India",
                base_weight=70,
                current_weight=70,
                max_capacity=9000,
                network_latency_ms=18.0
            ),
            
            # Northeast India - Lower capacity but strategic
            WeightedServer(
                server_id="NORTHEAST_PRIMARY",
                name="Guwahati Data Center", 
                host="northeast-primary.india.com",
                region="Northeast India",
                base_weight=50,
                current_weight=50,
                max_capacity=5000,
                network_latency_ms=25.0
            )
        ]
        
        self.servers = regional_servers
        
        for server in self.servers:
            logger.info(f"📡 Added server: {server.name} (Weight: {server.base_weight}, "
                       f"Capacity: {server.max_capacity})")
    
    def _setup_region_preferences(self):
        """Setup region proximity preferences for better routing"""
        self.region_preferences = {
            "North India": ["North India", "West India", "East India", "South India", "Northeast India"],
            "West India": ["West India", "South India", "North India", "East India", "Northeast India"], 
            "South India": ["South India", "West India", "East India", "North India", "Northeast India"],
            "East India": ["East India", "North India", "Northeast India", "South India", "West India"],
            "Northeast India": ["Northeast India", "East India", "North India", "South India", "West India"]
        }
    
    def select_server_weighted(self, request: Request) -> Optional[WeightedServer]:
        """
        Select server using weighted round-robin algorithm
        भारित राउंड-रॉबिन algorithm से server selection
        """
        with self.lock:
            # Filter healthy servers
            healthy_servers = [s for s in self.servers if s.is_healthy and s.current_load < s.max_capacity]
            
            if not healthy_servers:
                logger.warning("⚠️ No healthy servers available")
                return None
            
            # Apply regional preferences for better latency
            preferred_servers = self._get_preferred_servers(healthy_servers, request.user_region)
            
            if not preferred_servers:
                preferred_servers = healthy_servers
            
            # Calculate dynamic weights based on current conditions
            self._update_dynamic_weights(preferred_servers)
            
            # Weighted selection using smooth weighted round-robin
            selected_server = self._smooth_weighted_selection(preferred_servers)
            
            if selected_server:
                selected_server.last_selected = time.time()
                logger.info(f"🎯 Selected {selected_server.name} (Weight: {selected_server.current_weight}, "
                           f"Load: {selected_server.current_load}/{selected_server.max_capacity})")
            
            return selected_server
    
    def _get_preferred_servers(self, servers: List[WeightedServer], user_region: str) -> List[WeightedServer]:
        """Get servers ordered by regional preference"""
        if user_region not in self.region_preferences:
            return servers
        
        region_order = self.region_preferences[user_region]
        preferred_servers = []
        
        for preferred_region in region_order:
            region_servers = [s for s in servers if s.region == preferred_region]
            preferred_servers.extend(region_servers)
        
        return preferred_servers
    
    def _update_dynamic_weights(self, servers: List[WeightedServer]):
        """Update dynamic weights based on current server conditions"""
        current_time = time.time()
        
        for server in servers:
            # Start with base weight
            dynamic_weight = server.base_weight
            
            # Adjust for current load
            load_factor = 1.0 - (server.current_load / server.max_capacity)
            dynamic_weight = int(dynamic_weight * load_factor)
            
            # Adjust for performance metrics
            if server.response_time_ms > 0:
                # Reduce weight for slower servers
                if server.response_time_ms > 500:  # > 500ms
                    dynamic_weight = int(dynamic_weight * 0.7)
                elif server.response_time_ms > 200:  # > 200ms
                    dynamic_weight = int(dynamic_weight * 0.85)
            
            # Adjust for success rate
            if server.total_requests > 10:  # Only if we have enough data
                if server.success_rate < 95:
                    dynamic_weight = int(dynamic_weight * 0.8)
                elif server.success_rate < 98:
                    dynamic_weight = int(dynamic_weight * 0.9)
            
            # Apply peak hour multipliers
            dynamic_weight = int(dynamic_weight * server.peak_hour_multiplier)
            
            # Ensure minimum weight
            server.current_weight = max(1, dynamic_weight)
    
    def _smooth_weighted_selection(self, servers: List[WeightedServer]) -> Optional[WeightedServer]:
        """Smooth weighted round-robin selection algorithm"""
        if not servers:
            return None
        
        # Find server with highest current weight
        best_server = max(servers, key=lambda s: s.current_weight)
        
        # Reduce selected server's current weight
        best_server.current_weight -= sum(s.base_weight for s in servers)
        
        # Increase all servers' current weights by their base weights
        for server in servers:
            server.current_weight += server.base_weight
        
        return best_server
    
    def process_request(self, request: Request) -> Dict:
        """Process request through weighted load balancer"""
        start_time = time.time()
        
        # Select appropriate server
        server = self.select_server_weighted(request)
        
        if not server:
            self.stats['failed_no_server'] += 1
            return {
                'success': False,
                'error': 'No servers available',
                'request_id': request.request_id,
                'timestamp': time.time()
            }
        
        # Update server load
        server.current_load += 1
        server.total_requests += 1
        
        try:
            # Simulate request processing
            processing_result = self._simulate_request_processing(server, request)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_server_metrics(server, processing_time, processing_result['success'])
            
            processing_result.update({
                'server_used': server.name,
                'server_region': server.region,
                'processing_time_ms': processing_time * 1000,
                'server_load': f"{server.current_load}/{server.max_capacity}"
            })
            
            return processing_result
            
        except Exception as e:
            logger.error(f"💥 Request processing error: {e}")
            server.failed_requests += 1
            return {
                'success': False,
                'error': str(e),
                'request_id': request.request_id,
                'server_used': server.name
            }
        finally:
            # Always decrement load
            server.current_load = max(0, server.current_load - 1)
    
    def _simulate_request_processing(self, server: WeightedServer, request: Request) -> Dict:
        """Simulate request processing with realistic factors"""
        
        # Base processing time
        processing_time = request.estimated_processing_time
        
        # Add server-specific factors
        processing_time += server.network_latency_ms / 1000.0
        
        # Add load-based delay
        load_factor = server.current_load / server.max_capacity
        processing_time += processing_time * load_factor * 0.5
        
        # Add some randomness
        processing_time *= random.uniform(0.8, 1.4)
        
        # Simulate processing
        time.sleep(processing_time)
        
        # Simulate success/failure based on server health
        base_success_rate = 0.98  # 98% base success rate
        
        # Adjust for server load
        if load_factor > 0.8:
            base_success_rate -= 0.05  # Reduce success rate under high load
        
        # Adjust for request priority
        if request.priority == 3:  # Critical requests
            base_success_rate += 0.015  # Slight boost for critical requests
        
        success = random.random() < base_success_rate
        
        if success:
            return {
                'success': True,
                'request_id': request.request_id,
                'status': 'completed',
                'result': f"Request processed successfully on {server.region}"
            }
        else:
            return {
                'success': False,
                'error': 'Processing failed - temporary server issue',
                'request_id': request.request_id,
                'status': 'failed'
            }
    
    def _update_server_metrics(self, server: WeightedServer, processing_time: float, success: bool):
        """Update server performance metrics"""
        
        # Update response time (moving average)
        if server.response_time_ms == 0:
            server.response_time_ms = processing_time * 1000
        else:
            server.response_time_ms = (server.response_time_ms + processing_time * 1000) / 2
        
        # Update success rate
        if success:
            server.successful_requests += 1
        else:
            server.failed_requests += 1
        
        if server.total_requests > 0:
            server.success_rate = (server.successful_requests / server.total_requests) * 100
    
    def _start_monitoring(self):
        """Start background monitoring and health checks"""
        def monitor():
            while True:
                current_time = time.time()
                
                for server in self.servers:
                    # Simulate health fluctuations
                    server.is_healthy = random.random() > 0.03  # 3% chance unhealthy
                    
                    # Simulate resource utilization
                    base_cpu = 30 + (server.current_load / server.max_capacity) * 50
                    server.cpu_usage = min(100, base_cpu + random.uniform(-10, 15))
                    
                    base_memory = 40 + (server.current_load / server.max_capacity) * 40  
                    server.memory_usage = min(100, base_memory + random.uniform(-5, 10))
                    
                    # Simulate peak hour effects (10 AM - 6 PM IST)
                    hour = time.localtime().tm_hour
                    if 10 <= hour <= 18:
                        server.peak_hour_multiplier = 0.8  # Reduce weight during peak
                    else:
                        server.peak_hour_multiplier = 1.0
                
                time.sleep(30)  # Monitor every 30 seconds
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def get_load_balancer_stats(self) -> Dict:
        """Get comprehensive load balancer statistics"""
        
        healthy_servers = [s for s in self.servers if s.is_healthy]
        total_capacity = sum(s.max_capacity for s in healthy_servers)
        current_load = sum(s.current_load for s in healthy_servers)
        
        regional_stats = defaultdict(lambda: {
            'servers': 0, 'healthy_servers': 0, 'total_capacity': 0, 
            'current_load': 0, 'avg_weight': 0, 'avg_response_time': 0
        })
        
        for server in self.servers:
            region = server.region
            regional_stats[region]['servers'] += 1
            
            if server.is_healthy:
                regional_stats[region]['healthy_servers'] += 1
                regional_stats[region]['total_capacity'] += server.max_capacity
                regional_stats[region]['current_load'] += server.current_load
                regional_stats[region]['avg_weight'] += server.current_weight
                regional_stats[region]['avg_response_time'] += server.response_time_ms
        
        # Calculate averages
        for region, stats in regional_stats.items():
            healthy_count = stats['healthy_servers']
            if healthy_count > 0:
                stats['avg_weight'] = stats['avg_weight'] / healthy_count
                stats['avg_response_time'] = stats['avg_response_time'] / healthy_count
                stats['load_percentage'] = (stats['current_load'] / max(1, stats['total_capacity'])) * 100
        
        return {
            'system_overview': {
                'total_servers': len(self.servers),
                'healthy_servers': len(healthy_servers),
                'total_capacity': total_capacity,
                'current_load': current_load,
                'system_load_percentage': (current_load / max(1, total_capacity)) * 100,
            },
            'regional_stats': dict(regional_stats),
            'server_details': [
                {
                    'name': s.name,
                    'region': s.region,
                    'health': 'Healthy' if s.is_healthy else 'Unhealthy',
                    'weight': f"{s.current_weight} (base: {s.base_weight})",
                    'load': f"{s.current_load}/{s.max_capacity}",
                    'load_percentage': f"{(s.current_load/s.max_capacity)*100:.1f}%",
                    'success_rate': f"{s.success_rate:.1f}%",
                    'response_time': f"{s.response_time_ms:.1f}ms",
                    'cpu_usage': f"{s.cpu_usage:.1f}%",
                    'memory_usage': f"{s.memory_usage:.1f}%"
                }
                for s in self.servers
            ]
        }


def simulate_regional_traffic():
    """Simulate regional traffic patterns across India"""
    
    print("\n🌍 Simulating Regional Traffic Patterns")
    print("=" * 50)
    
    load_balancer = RegionalWeightedLoadBalancer()
    
    # Generate requests from different regions with different patterns
    requests = []
    
    # Regional traffic patterns (realistic distribution)
    regional_distribution = {
        "West India": 0.35,    # Mumbai financial hub
        "North India": 0.25,   # Delhi NCR tech hub  
        "South India": 0.25,   # Bangalore tech hub
        "East India": 0.10,    # Traditional industries
        "Northeast India": 0.05 # Smaller population
    }
    
    request_types = [
        ("payment", 3, 0.2),      # Critical priority, longer processing
        ("user_query", 1, 0.05),  # Normal priority, quick
        ("data_sync", 2, 0.15),   # High priority, medium processing
        ("analytics", 1, 0.3),    # Normal priority, longer processing
        ("api_call", 1, 0.08)     # Normal priority, quick
    ]
    
    # Generate 100 requests with realistic regional distribution
    for i in range(100):
        # Select region based on distribution
        rand_val = random.random()
        cumulative = 0
        selected_region = "North India"  # default
        
        for region, probability in regional_distribution.items():
            cumulative += probability
            if rand_val <= cumulative:
                selected_region = region
                break
        
        # Select request type
        req_type, priority, proc_time = random.choice(request_types)
        
        request = Request(
            request_id=f"REQ_{i:03d}",
            user_region=selected_region,
            request_type=req_type,
            priority=priority,
            estimated_processing_time=proc_time
        )
        
        requests.append(request)
    
    # Process requests
    print(f"Processing {len(requests)} requests with weighted load balancing...")
    
    results = []
    for request in requests:
        result = load_balancer.process_request(request)
        results.append(result)
        
        # Small delay to simulate realistic timing
        time.sleep(0.01)
    
    return load_balancer, results


def main():
    """Main demonstration of Regional Weighted Load Balancer"""
    
    print("🏛️ भारतीय क्षेत्रीय भारित लोड बैलेंसर")
    print("=" * 60)
    
    # Simulate regional traffic
    load_balancer, results = simulate_regional_traffic()
    
    # Analyze results
    successful_requests = sum(1 for r in results if r.get('success', False))
    failed_requests = len(results) - successful_requests
    
    print(f"\n📊 Processing Results:")
    print(f"Total Requests: {len(results)}")
    print(f"Successful: {successful_requests}")
    print(f"Failed: {failed_requests}")
    print(f"Success Rate: {(successful_requests/len(results))*100:.1f}%")
    
    # Regional distribution analysis
    region_counts = {}
    server_usage = {}
    
    for result in results:
        if result.get('success'):
            region = result.get('server_region', 'Unknown')
            server = result.get('server_used', 'Unknown')
            
            region_counts[region] = region_counts.get(region, 0) + 1
            server_usage[server] = server_usage.get(server, 0) + 1
    
    print(f"\n🗺️ Traffic Distribution by Region:")
    print("-" * 40)
    for region, count in sorted(region_counts.items()):
        percentage = (count / successful_requests) * 100
        print(f"{region}: {count} requests ({percentage:.1f}%)")
    
    # Get comprehensive statistics
    print(f"\n📈 Load Balancer Statistics:")
    print("=" * 50)
    
    stats = load_balancer.get_load_balancer_stats()
    
    # System overview
    system_stats = stats['system_overview']
    print(f"System Overview:")
    print(f"  Active Servers: {system_stats['healthy_servers']}/{system_stats['total_servers']}")
    print(f"  System Load: {system_stats['system_load_percentage']:.1f}%")
    print(f"  Total Capacity: {system_stats['total_capacity']:,} requests")
    
    # Regional statistics
    print(f"\n🌍 Regional Performance:")
    print("-" * 70)
    print(f"{'Region':<20} {'Servers':<10} {'Load':<15} {'Avg Weight':<12} {'Avg Response':<12}")
    print("-" * 70)
    
    for region, region_stats in stats['regional_stats'].items():
        if region_stats['healthy_servers'] > 0:
            print(f"{region:<20} "
                  f"{region_stats['healthy_servers']}/{region_stats['servers']:<10} "
                  f"{region_stats['load_percentage']:.1f}%{'':(<10)} "
                  f"{region_stats['avg_weight']:.1f}{'':(<8)} "
                  f"{region_stats['avg_response_time']:.1f}ms{'':(<8)}")
    
    # Individual server details
    print(f"\n🖥️ Individual Server Performance:")
    print("-" * 100)
    print(f"{'Server':<30} {'Region':<15} {'Weight':<15} {'Load':<12} {'Success':<8} {'Response':<10} {'CPU':<6} {'Memory':<6}")
    print("-" * 100)
    
    for server in stats['server_details']:
        print(f"{server['name']:<30} "
              f"{server['region']:<15} "
              f"{server['weight']:<15} "
              f"{server['load']:<12} "
              f"{server['success_rate']:<8} "
              f"{server['response_time']:<10} "
              f"{server['cpu_usage']:<6} "
              f"{server['memory_usage']:<6}")
    
    # Recommendations
    print(f"\n💡 Optimization Recommendations:")
    print("=" * 40)
    print("⚖️ Weights automatically adjust based on server performance")
    print("🗺️ Regional preferences improve user experience with lower latency")
    print("📊 Dynamic weight adjustments prevent server overload")
    print("🔄 Peak hour multipliers balance load during high-traffic periods")
    print("🎯 Success rate monitoring ensures quality of service")
    print("💪 Resource-based adjustments optimize server utilization")
    
    print(f"\n🚀 Production Enhancements:")
    print("📈 Implement predictive scaling based on traffic patterns")
    print("🔍 Add machine learning for intelligent weight optimization")
    print("⚡ Use real-time metrics for instant weight adjustments")
    print("🌐 Integrate with CDN for static content delivery")
    print("📱 Mobile-specific routing optimizations")


if __name__ == "__main__":
    main()