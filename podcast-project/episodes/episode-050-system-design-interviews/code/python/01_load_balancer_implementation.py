#!/usr/bin/env python3
"""
Load Balancer Implementation - Episode 50: System Design Interview Mastery
Mumbai Local Train Traffic Management System

Load balancing जैसे Mumbai local train का traffic control है।
हर platform पर crowd evenly distribute करना है।

Author: Hindi Podcast Series
Topic: Distributed System Load Balancing with Indian Context
"""

import random
import time
import hashlib
import threading
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict
import json

class LoadBalancingStrategy(Enum):
    """Load balancing strategies - Traffic distribution ke tarike"""
    ROUND_ROBIN = "round_robin"  # Railway platform rotation
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  # Priority based on platform size
    LEAST_CONNECTIONS = "least_connections"  # Kamse kam bheed wala platform
    RANDOM = "random"  # Random platform selection
    CONSISTENT_HASH = "consistent_hash"  # Consistent user routing

@dataclass
class Server:
    """Server representation - Mumbai Railway Station Platform"""
    id: str
    host: str
    port: int
    weight: int = 1
    is_healthy: bool = True
    current_connections: int = 0
    max_connections: int = 1000
    response_time: float = 0.0
    
    def get_load_score(self) -> float:
        """Calculate load score - Platform की load capacity"""
        if not self.is_healthy:
            return float('inf')
        return (self.current_connections / self.max_connections) * 100

class HealthChecker:
    """Health check system - Platform operational status monitor"""
    
    def __init__(self):
        self.check_interval = 5  # seconds
        self.timeout = 3  # seconds
        self.running = False
        self.thread = None
    
    def start_health_checks(self, servers: List[Server], load_balancer):
        """Start continuous health monitoring"""
        self.running = True
        self.thread = threading.Thread(
            target=self._health_check_loop, 
            args=(servers, load_balancer)
        )
        self.thread.daemon = True
        self.thread.start()
        print("🏥 Health checker शुरू हो गया - Platform monitoring active")
    
    def _health_check_loop(self, servers: List[Server], load_balancer):
        """Continuous health check loop"""
        while self.running:
            for server in servers:
                try:
                    # Simulate health check - Real implementation में HTTP/TCP check होगा
                    if self._check_server_health(server):
                        if not server.is_healthy:
                            server.is_healthy = True
                            print(f"✅ Platform {server.id} वापस operational - Traffic restored")
                    else:
                        if server.is_healthy:
                            server.is_healthy = False
                            print(f"🚫 Platform {server.id} down detected - Traffic redirected")
                            load_balancer.remove_unhealthy_server(server)
                except Exception as e:
                    server.is_healthy = False
                    print(f"❌ Platform {server.id} health check failed: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_server_health(self, server: Server) -> bool:
        """Individual server health check"""
        # Real implementation में TCP connection या HTTP request होगी
        # Simulation के लिए random failure
        if server.current_connections > server.max_connections * 0.9:
            return random.choice([True, False])  # Overloaded platform
        return random.random() > 0.05  # 5% failure rate

class LoadBalancer:
    """Main Load Balancer - Mumbai Railway Traffic Control Center"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.servers: List[Server] = []
        self.strategy = strategy
        self.current_index = 0
        self.lock = threading.Lock()
        self.health_checker = HealthChecker()
        self.metrics = defaultdict(int)
        self.consistent_hash_ring = {}
        
        print(f"🚂 Load Balancer initialized - Strategy: {strategy.value}")
    
    def add_server(self, server: Server):
        """Add new server platform"""
        with self.lock:
            self.servers.append(server)
            if self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
                self._add_to_hash_ring(server)
        print(f"🏢 Platform {server.id} added - Total platforms: {len(self.servers)}")
    
    def remove_server(self, server_id: str):
        """Remove server platform"""
        with self.lock:
            self.servers = [s for s in self.servers if s.id != server_id]
            if self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
                self._rebuild_hash_ring()
        print(f"🗑️ Platform {server_id} removed")
    
    def remove_unhealthy_server(self, unhealthy_server: Server):
        """Temporarily remove unhealthy server from rotation"""
        print(f"⚠️ Platform {unhealthy_server.id} marked unhealthy - Traffic rerouted")
        self.metrics['unhealthy_removals'] += 1
    
    def get_next_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get next server based on strategy - अगला platform select करें"""
        
        healthy_servers = [s for s in self.servers if s.is_healthy]
        if not healthy_servers:
            print("🚨 No healthy platforms available!")
            return None
        
        with self.lock:
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_select(healthy_servers)
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_select(healthy_servers)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_select(healthy_servers)
            elif self.strategy == LoadBalancingStrategy.RANDOM:
                return self._random_select(healthy_servers)
            elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
                return self._consistent_hash_select(healthy_servers, client_id)
    
    def _round_robin_select(self, servers: List[Server]) -> Server:
        """Round Robin - Railway platform rotation system"""
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        self.metrics['round_robin_selections'] += 1
        return server
    
    def _weighted_round_robin_select(self, servers: List[Server]) -> Server:
        """Weighted Round Robin - Platform size के अनुसार priority"""
        total_weight = sum(s.weight for s in servers)
        random_weight = random.randint(1, total_weight)
        
        current_weight = 0
        for server in servers:
            current_weight += server.weight
            if random_weight <= current_weight:
                self.metrics['weighted_selections'] += 1
                return server
        
        return servers[0]  # Fallback
    
    def _least_connections_select(self, servers: List[Server]) -> Server:
        """Least Connections - सबसे कम भीड़ वाला platform"""
        min_connections_server = min(servers, key=lambda s: s.current_connections)
        self.metrics['least_connections_selections'] += 1
        return min_connections_server
    
    def _random_select(self, servers: List[Server]) -> Server:
        """Random Selection - Random platform choose"""
        server = random.choice(servers)
        self.metrics['random_selections'] += 1
        return server
    
    def _consistent_hash_select(self, servers: List[Server], client_id: str) -> Server:
        """Consistent Hashing - User को same platform पर route करना"""
        if not client_id:
            return self._random_select(servers)
        
        hash_key = int(hashlib.md5(client_id.encode()).hexdigest(), 16)
        # Find nearest server in hash ring
        sorted_keys = sorted(self.consistent_hash_ring.keys())
        
        for key in sorted_keys:
            if hash_key <= key:
                server_id = self.consistent_hash_ring[key]
                server = next((s for s in servers if s.id == server_id), None)
                if server:
                    self.metrics['consistent_hash_selections'] += 1
                    return server
        
        # Wrap around to first server
        if sorted_keys:
            server_id = self.consistent_hash_ring[sorted_keys[0]]
            server = next((s for s in servers if s.id == server_id), None)
            if server:
                return server
        
        return self._random_select(servers)
    
    def _add_to_hash_ring(self, server: Server):
        """Add server to consistent hash ring"""
        # Multiple virtual nodes for better distribution
        for i in range(3):
            key = int(hashlib.md5(f"{server.id}-{i}".encode()).hexdigest(), 16)
            self.consistent_hash_ring[key] = server.id
    
    def _rebuild_hash_ring(self):
        """Rebuild consistent hash ring after server changes"""
        self.consistent_hash_ring.clear()
        for server in self.servers:
            self._add_to_hash_ring(server)
    
    def handle_request(self, client_id: str = None) -> Dict:
        """Handle incoming request - Request को process करना"""
        server = self.get_next_server(client_id)
        
        if not server:
            self.metrics['failed_requests'] += 1
            return {
                'status': 'error',
                'message': 'No available servers',
                'server': None
            }
        
        # Simulate request processing
        server.current_connections += 1
        start_time = time.time()
        
        try:
            # Simulate processing time
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            server.response_time = processing_time
            self.metrics['successful_requests'] += 1
            
            return {
                'status': 'success',
                'server': server.id,
                'response_time': processing_time,
                'load_score': server.get_load_score()
            }
        
        finally:
            server.current_connections -= 1
    
    def start_monitoring(self):
        """Start health monitoring system"""
        self.health_checker.start_health_checks(self.servers, self)
    
    def get_metrics(self) -> Dict:
        """Get load balancer metrics"""
        return {
            'total_servers': len(self.servers),
            'healthy_servers': len([s for s in self.servers if s.is_healthy]),
            'strategy': self.strategy.value,
            'metrics': dict(self.metrics),
            'server_stats': [
                {
                    'id': s.id,
                    'healthy': s.is_healthy,
                    'connections': s.current_connections,
                    'load_score': s.get_load_score(),
                    'response_time': s.response_time
                } for s in self.servers
            ]
        }

def demonstrate_mumbai_railway_load_balancer():
    """Mumbai Railway Load Balancing Demo - CST to Andheri route"""
    print("🚂 Mumbai Railway Load Balancer Demo Started")
    print("=" * 60)
    
    # Create Mumbai Railway stations as servers
    stations = [
        Server("CST", "cst.mumbai.railway", 8001, weight=3, max_connections=500),
        Server("DADAR", "dadar.mumbai.railway", 8002, weight=4, max_connections=600), 
        Server("BANDRA", "bandra.mumbai.railway", 8003, weight=2, max_connections=400),
        Server("ANDHERI", "andheri.mumbai.railway", 8004, weight=3, max_connections=500),
    ]
    
    # Test different strategies
    strategies = [
        LoadBalancingStrategy.ROUND_ROBIN,
        LoadBalancingStrategy.LEAST_CONNECTIONS,
        LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
        LoadBalancingStrategy.CONSISTENT_HASH
    ]
    
    for strategy in strategies:
        print(f"\n📊 Testing Strategy: {strategy.value}")
        print("-" * 40)
        
        lb = LoadBalancer(strategy)
        
        # Add stations
        for station in stations:
            # Reset station state
            station.current_connections = 0
            station.is_healthy = True
            station.response_time = 0.0
            lb.add_server(station)
        
        # Start monitoring
        lb.start_monitoring()
        
        # Simulate passenger requests
        passengers = [f"passenger_{i}" for i in range(20)]
        
        print("\n🎫 Processing passenger requests...")
        for passenger in passengers:
            result = lb.handle_request(passenger)
            if result['status'] == 'success':
                print(f"👤 {passenger} → Platform {result['server']} "
                      f"(Response: {result['response_time']:.3f}s)")
        
        print(f"\n📈 Strategy Performance:")
        metrics = lb.get_metrics()
        print(f"   Successful Requests: {metrics['metrics'].get('successful_requests', 0)}")
        print(f"   Failed Requests: {metrics['metrics'].get('failed_requests', 0)}")
        
        # Show load distribution
        print(f"\n🏢 Platform Load Distribution:")
        for server_stat in metrics['server_stats']:
            print(f"   {server_stat['id']}: Load {server_stat['load_score']:.1f}%")

def simulate_zomato_restaurant_load_balancer():
    """Zomato Restaurant Load Balancer - Order distribution"""
    print("\n🍕 Zomato Restaurant Load Balancer Demo")
    print("=" * 60)
    
    # Mumbai Zomato restaurant servers
    restaurants = [
        Server("TOIT_PUNE", "toit.pune.zomato", 9001, weight=5),  # Popular brewpub
        Server("SOCIAL_BKC", "social.bkc.zomato", 9002, weight=4),  # Co-working restaurant
        Server("THEOBROMA", "theobroma.mumbai.zomato", 9003, weight=3),  # Bakery chain
        Server("BURGER_KING", "bk.mumbai.zomato", 9004, weight=2),  # Fast food
    ]
    
    lb = LoadBalancer(LoadBalancingStrategy.LEAST_CONNECTIONS)
    
    for restaurant in restaurants:
        lb.add_server(restaurant)
    
    print("\n📱 Processing Zomato orders...")
    orders = [
        "order_pizza_001", "order_burger_002", "order_cake_003", 
        "order_biryani_004", "order_sandwich_005", "order_pasta_006"
    ]
    
    for order in orders:
        result = lb.handle_request(order)
        if result['status'] == 'success':
            print(f"🍽️ {order} → {result['server']} "
                  f"(Load: {result['load_score']:.1f}%)")
    
    print(f"\n📊 Final Metrics:")
    final_metrics = lb.get_metrics()
    print(json.dumps(final_metrics, indent=2))

if __name__ == "__main__":
    # Run demonstrations
    demonstrate_mumbai_railway_load_balancer()
    
    print("\n" + "="*80 + "\n")
    
    simulate_zomato_restaurant_load_balancer()
    
    print(f"\n✅ Load Balancer Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Round Robin - Platform rotation")
    print(f"   • Weighted Round Robin - Priority based distribution") 
    print(f"   • Least Connections - Minimum load distribution")
    print(f"   • Consistent Hashing - User session affinity")
    print(f"   • Health Checking - Platform monitoring")
    print(f"   • Load Metrics - Performance measurement")