#!/usr/bin/env python3
"""
Least Connections Load Balancer for Swiggy Order Routing
स्विगी ऑर्डर रूटिंग के लिए least connections load balancing

यह example दिखाता है कि कैसे food delivery services में
least connections algorithm से optimal server selection करें।
"""

import time
import random
import threading
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import heapq
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DeliveryServer:
    """Food delivery server with connection tracking"""
    server_id: str
    name: str
    host: str
    region: str
    city: str
    zone: str  # Delivery zone within city
    
    # Connection metrics
    active_connections: int = 0
    max_connections: int = 1000
    connection_queue: int = 0  # Queued connections
    
    # Performance metrics
    avg_order_processing_time: float = 2.5  # seconds
    avg_delivery_assignment_time: float = 1.2  # seconds
    success_rate: float = 98.5
    
    # Geographic factors
    coverage_radius_km: float = 5.0
    delivery_partner_count: int = 100
    active_delivery_partners: int = 0
    
    # Server health
    is_healthy: bool = True
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_health_check: float = field(default_factory=time.time)
    
    # Statistics
    total_orders_processed: int = 0
    successful_orders: int = 0
    failed_orders: int = 0


@dataclass
class SwiggyOrder:
    """Swiggy order request structure"""
    order_id: str
    customer_id: str
    restaurant_id: str
    customer_location: Tuple[float, float]  # (lat, lng)
    restaurant_location: Tuple[float, float]  # (lat, lng)
    order_value: float
    item_count: int
    estimated_prep_time: int  # minutes
    delivery_priority: int = 1  # 1=normal, 2=priority, 3=pro
    timestamp: float = field(default_factory=time.time)


class SwiggyLeastConnectionsLoadBalancer:
    """
    स्विगी के लिए least connections load balancer
    Food delivery optimization के लिए specially designed
    """
    
    def __init__(self):
        self.servers: List[DeliveryServer] = []
        self.server_lock = threading.Lock()
        self.city_server_map: Dict[str, List[DeliveryServer]] = defaultdict(list)
        self.zone_server_map: Dict[str, List[DeliveryServer]] = defaultdict(list)
        
        # Performance tracking
        self.stats = {
            'total_orders': 0,
            'successful_assignments': 0,
            'failed_assignments': 0,
            'avg_assignment_time': 0.0,
            'peak_connections': 0
        }
        
        # Initialize Swiggy delivery servers across major Indian cities
        self._initialize_swiggy_servers()
        
        # Start monitoring
        self._start_connection_monitoring()
        
        logger.info("🍔 Swiggy Least Connections Load Balancer initialized")
    
    def _initialize_swiggy_servers(self):
        """Initialize Swiggy delivery servers across major Indian cities"""
        
        server_configs = [
            # Mumbai - Multiple zones due to high density
            ("MUM_BANDRA", "Mumbai Bandra Server", "mumbai-bandra.swiggy.com", "West India", "Mumbai", "Bandra-Khar", 1200, 8.0, 250),
            ("MUM_ANDHERI", "Mumbai Andheri Server", "mumbai-andheri.swiggy.com", "West India", "Mumbai", "Andheri-Versova", 1500, 10.0, 300),
            ("MUM_POWAI", "Mumbai Powai Server", "mumbai-powai.swiggy.com", "West India", "Mumbai", "Powai-Vikhroli", 1000, 6.0, 180),
            ("MUM_SOUTH", "Mumbai South Server", "mumbai-south.swiggy.com", "West India", "Mumbai", "South-Mumbai", 1800, 12.0, 400),
            
            # Delhi NCR - High capacity for tech hub
            ("DEL_CENTRAL", "Delhi Central Server", "delhi-central.swiggy.com", "North India", "Delhi", "Central-Delhi", 1400, 15.0, 320),
            ("GUR_DLF", "Gurgaon DLF Server", "gurgaon-dlf.swiggy.com", "North India", "Gurgaon", "DLF-CyberCity", 1300, 8.0, 280),
            ("NOI_SECTOR", "Noida Sector Server", "noida-sector.swiggy.com", "North India", "Noida", "Sector-18-62", 1100, 12.0, 250),
            
            # Bangalore - Tech hub with high order volume
            ("BLR_KORAMANGALA", "Bangalore Koramangala Server", "blr-koramangala.swiggy.com", "South India", "Bangalore", "Koramangala-BTM", 1600, 10.0, 350),
            ("BLR_WHITEFIELD", "Bangalore Whitefield Server", "blr-whitefield.swiggy.com", "South India", "Bangalore", "Whitefield-Marathalli", 1200, 14.0, 280),
            ("BLR_INDIRANAGAR", "Bangalore Indiranagar Server", "blr-indiranagar.swiggy.com", "South India", "Bangalore", "Indiranagar-CV-Raman", 1000, 8.0, 220),
            
            # Hyderabad - Growing tech hub
            ("HYD_HITECH", "Hyderabad Hitech Server", "hyd-hitech.swiggy.com", "South India", "Hyderabad", "Hitech-City-Gachibowli", 1300, 12.0, 300),
            ("HYD_BANJARA", "Hyderabad Banjara Hills Server", "hyd-banjara.swiggy.com", "South India", "Hyderabad", "Banjara-Hills-Jubilee", 900, 8.0, 200),
            
            # Chennai - Traditional metro
            ("CHN_CENTRAL", "Chennai Central Server", "chennai-central.swiggy.com", "South India", "Chennai", "Central-Chennai", 1100, 10.0, 250),
            ("CHN_OMR", "Chennai OMR Server", "chennai-omr.swiggy.com", "South India", "Chennai", "OMR-Sholinganallur", 800, 15.0, 180),
            
            # Pune - Emerging IT hub
            ("PUN_HINJEWADI", "Pune Hinjewadi Server", "pune-hinjewadi.swiggy.com", "West India", "Pune", "Hinjewadi-Wakad", 900, 12.0, 200),
            ("PUN_KOREGAON", "Pune Koregaon Park Server", "pune-koregaon.swiggy.com", "West India", "Pune", "Koregaon-Park-Viman-Nagar", 700, 8.0, 160),
        ]
        
        for server_id, name, host, region, city, zone, max_conn, radius, partners in server_configs:
            server = DeliveryServer(
                server_id=server_id,
                name=name,
                host=host,
                region=region,
                city=city,
                zone=zone,
                max_connections=max_conn,
                coverage_radius_km=radius,
                delivery_partner_count=partners,
                active_delivery_partners=int(partners * random.uniform(0.6, 0.9))  # 60-90% active
            )
            
            self.servers.append(server)
            self.city_server_map[city].append(server)
            self.zone_server_map[f"{city}_{zone}"].append(server)
            
            logger.info(f"🏪 Added server: {name} (Max Conn: {max_conn}, Partners: {partners})")
    
    def select_server_least_connections(self, order: SwiggyOrder) -> Optional[DeliveryServer]:
        """
        Select server with least connections for the order location
        ऑर्डर location के लिए कम से कम connections वाला server select करता है
        """
        with self.server_lock:
            # Find servers that can handle this location
            candidate_servers = self._find_candidate_servers(order)
            
            if not candidate_servers:
                logger.warning(f"⚠️ No servers found for order location")
                return None
            
            # Filter healthy servers with available capacity
            available_servers = [
                server for server in candidate_servers
                if (server.is_healthy and 
                    server.active_connections < server.max_connections and
                    server.active_delivery_partners > 0)
            ]
            
            if not available_servers:
                logger.warning(f"⚠️ No available servers for order {order.order_id}")
                return None
            
            # Select server with least connections (with tie-breaking)
            selected_server = self._select_optimal_server(available_servers, order)
            
            if selected_server:
                # Reserve connection
                selected_server.active_connections += 1
                logger.info(f"🎯 Selected {selected_server.name} "
                           f"(Connections: {selected_server.active_connections}/{selected_server.max_connections})")
            
            return selected_server
    
    def _find_candidate_servers(self, order: SwiggyOrder) -> List[DeliveryServer]:
        """Find servers that can service the order location"""
        candidate_servers = []
        
        # Extract city from order (simplified - in production, use geocoding)
        order_city = self._extract_city_from_location(order.customer_location)
        
        if order_city in self.city_server_map:
            # Get all servers in the same city
            city_servers = self.city_server_map[order_city]
            
            # Filter by geographic coverage (simplified distance check)
            for server in city_servers:
                if self._is_within_coverage(order, server):
                    candidate_servers.append(server)
        
        return candidate_servers
    
    def _extract_city_from_location(self, location: Tuple[float, float]) -> str:
        """Extract city from coordinates (simplified implementation)"""
        lat, lng = location
        
        # Simplified city mapping based on coordinate ranges
        # In production, use proper geocoding service
        if 19.0 <= lat <= 19.3 and 72.8 <= lng <= 72.98:
            return "Mumbai"
        elif 28.4 <= lat <= 28.9 and 77.0 <= lng <= 77.4:
            return "Delhi"
        elif 12.8 <= lat <= 13.2 and 77.5 <= lng <= 77.8:
            return "Bangalore"
        elif 17.3 <= lat <= 17.6 and 78.3 <= lng <= 78.6:
            return "Hyderabad"
        elif 13.0 <= lat <= 13.3 and 80.1 <= lng <= 80.4:
            return "Chennai"
        elif 18.4 <= lat <= 18.7 and 73.7 <= lng <= 74.0:
            return "Pune"
        else:
            return "Unknown"
    
    def _is_within_coverage(self, order: SwiggyOrder, server: DeliveryServer) -> bool:
        """Check if order is within server's coverage area (simplified)"""
        # Simplified distance calculation
        # In production, use proper haversine formula and delivery zones
        
        # For this example, assume all servers in a city can handle any order in that city
        # with priority given to zone-specific servers
        return True
    
    def _select_optimal_server(self, servers: List[DeliveryServer], order: SwiggyOrder) -> DeliveryServer:
        """Select optimal server using least connections with intelligent tie-breaking"""
        
        # Sort by connection count (primary criteria)
        servers_by_connections = sorted(servers, key=lambda s: (
            s.active_connections,
            -s.active_delivery_partners,  # More delivery partners is better
            s.avg_order_processing_time,  # Faster processing is better
            -s.success_rate  # Higher success rate is better (negative for ascending sort)
        ))
        
        best_server = servers_by_connections[0]
        
        # Additional optimization for high-priority orders
        if order.delivery_priority >= 2:  # Priority or Pro orders
            # Check if there's a server with slightly more connections but better performance
            for server in servers_by_connections[:3]:  # Top 3 candidates
                if (server.active_connections <= best_server.active_connections + 2 and
                    server.success_rate > best_server.success_rate + 1.0):
                    best_server = server
                    break
        
        return best_server
    
    def process_order(self, order: SwiggyOrder) -> Dict:
        """Process Swiggy order through least connections load balancer"""
        start_time = time.time()
        
        # Select optimal server
        server = self.select_server_least_connections(order)
        
        if not server:
            self._update_stats(start_time, success=False)
            return {
                'success': False,
                'error': 'No servers available for delivery location',
                'order_id': order.order_id,
                'timestamp': time.time()
            }
        
        try:
            # Process order on selected server
            result = self._simulate_order_processing(server, order)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_stats(start_time, success=result['success'])
            self._update_server_metrics(server, processing_time, result['success'])
            
            result.update({
                'server_used': server.name,
                'server_city': server.city,
                'server_zone': server.zone,
                'processing_time_ms': processing_time * 1000,
                'server_load': f"{server.active_connections}/{server.max_connections}",
                'delivery_partners_available': server.active_delivery_partners
            })
            
            return result
            
        except Exception as e:
            logger.error(f"💥 Order processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'order_id': order.order_id,
                'server_used': server.name if server else 'Unknown'
            }
        finally:
            # Always release connection
            if server:
                server.active_connections = max(0, server.active_connections - 1)
    
    def _simulate_order_processing(self, server: DeliveryServer, order: SwiggyOrder) -> Dict:
        """Simulate order processing with realistic delivery factors"""
        
        # Calculate processing time based on various factors
        base_processing_time = server.avg_order_processing_time
        
        # Adjust for order complexity
        complexity_factor = 1.0
        if order.item_count > 5:
            complexity_factor += 0.2
        if order.order_value > 1000:  # High-value order
            complexity_factor += 0.1
        
        # Adjust for server load
        load_factor = server.active_connections / server.max_connections
        processing_time = base_processing_time * complexity_factor * (1 + load_factor * 0.5)
        
        # Add delivery partner assignment time
        if server.active_delivery_partners < 10:  # Low availability
            processing_time += server.avg_delivery_assignment_time * 2
        else:
            processing_time += server.avg_delivery_assignment_time
        
        # Simulate processing
        time.sleep(min(processing_time, 0.5))  # Cap simulation time
        
        # Calculate success probability
        base_success_rate = server.success_rate / 100.0
        
        # Adjust for delivery partner availability
        partner_availability = server.active_delivery_partners / server.delivery_partner_count
        if partner_availability < 0.3:  # Less than 30% partners available
            base_success_rate -= 0.1
        
        # Adjust for server load
        if load_factor > 0.8:
            base_success_rate -= 0.05
        
        # Priority orders get better treatment
        if order.delivery_priority >= 2:
            base_success_rate += 0.02
        
        success = random.random() < base_success_rate
        
        if success:
            # Assign delivery partner
            assigned_partner_id = f"DP_{server.city}_{random.randint(1000, 9999)}"
            estimated_delivery_time = order.estimated_prep_time + random.randint(20, 45)  # minutes
            
            return {
                'success': True,
                'order_id': order.order_id,
                'status': 'assigned',
                'delivery_partner_id': assigned_partner_id,
                'estimated_delivery_time': estimated_delivery_time,
                'restaurant_location': order.restaurant_location,
                'customer_location': order.customer_location,
                'message': f"Order assigned to delivery partner in {server.zone}"
            }
        else:
            # Common failure reasons in food delivery
            failure_reasons = [
                "No delivery partners available in the area",
                "Restaurant temporarily unavailable", 
                "High demand - please try again later",
                "Delivery area temporarily out of service"
            ]
            
            return {
                'success': False,
                'error': random.choice(failure_reasons),
                'order_id': order.order_id,
                'status': 'failed',
                'retry_suggested': True
            }
    
    def _update_stats(self, start_time: float, success: bool):
        """Update global statistics"""
        processing_time = time.time() - start_time
        
        self.stats['total_orders'] += 1
        
        if success:
            self.stats['successful_assignments'] += 1
        else:
            self.stats['failed_assignments'] += 1
        
        # Update average assignment time
        current_avg = self.stats['avg_assignment_time']
        total_orders = self.stats['total_orders']
        self.stats['avg_assignment_time'] = (current_avg * (total_orders - 1) + processing_time * 1000) / total_orders
        
        # Track peak connections
        current_total_connections = sum(s.active_connections for s in self.servers)
        if current_total_connections > self.stats['peak_connections']:
            self.stats['peak_connections'] = current_total_connections
    
    def _update_server_metrics(self, server: DeliveryServer, processing_time: float, success: bool):
        """Update individual server metrics"""
        server.total_orders_processed += 1
        
        if success:
            server.successful_orders += 1
        else:
            server.failed_orders += 1
        
        # Update success rate
        server.success_rate = (server.successful_orders / server.total_orders_processed) * 100
        
        # Update average processing time
        server.avg_order_processing_time = (server.avg_order_processing_time + processing_time) / 2
    
    def _start_connection_monitoring(self):
        """Start background monitoring of connections and server health"""
        def monitor():
            while True:
                for server in self.servers:
                    # Simulate health fluctuations
                    server.is_healthy = random.random() > 0.02  # 2% chance unhealthy
                    
                    # Simulate resource usage
                    connection_ratio = server.active_connections / server.max_connections
                    server.cpu_usage = min(100, 20 + connection_ratio * 60 + random.uniform(-10, 15))
                    server.memory_usage = min(100, 30 + connection_ratio * 50 + random.uniform(-5, 10))
                    
                    # Simulate delivery partner availability changes
                    base_partners = server.delivery_partner_count
                    # More partners active during meal times
                    hour = time.localtime().tm_hour
                    if 11 <= hour <= 14 or 19 <= hour <= 22:  # Lunch and dinner
                        availability_rate = random.uniform(0.7, 0.95)
                    else:
                        availability_rate = random.uniform(0.4, 0.8)
                    
                    server.active_delivery_partners = int(base_partners * availability_rate)
                    
                    server.last_health_check = time.time()
                
                time.sleep(15)  # Monitor every 15 seconds
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        
        # Calculate system-wide metrics
        total_connections = sum(s.active_connections for s in self.servers)
        total_capacity = sum(s.max_connections for s in self.servers)
        healthy_servers = sum(1 for s in self.servers if s.is_healthy)
        total_delivery_partners = sum(s.active_delivery_partners for s in self.servers)
        
        # City-wise statistics
        city_stats = defaultdict(lambda: {
            'servers': 0, 'healthy_servers': 0, 'connections': 0, 
            'capacity': 0, 'delivery_partners': 0, 'avg_success_rate': 0
        })
        
        for server in self.servers:
            city = server.city
            city_stats[city]['servers'] += 1
            if server.is_healthy:
                city_stats[city]['healthy_servers'] += 1
            city_stats[city]['connections'] += server.active_connections
            city_stats[city]['capacity'] += server.max_connections
            city_stats[city]['delivery_partners'] += server.active_delivery_partners
            city_stats[city]['avg_success_rate'] += server.success_rate
        
        # Calculate averages
        for city, stats in city_stats.items():
            if stats['servers'] > 0:
                stats['avg_success_rate'] = stats['avg_success_rate'] / stats['servers']
                stats['load_percentage'] = (stats['connections'] / max(1, stats['capacity'])) * 100
        
        return {
            'system_overview': {
                'total_servers': len(self.servers),
                'healthy_servers': healthy_servers,
                'total_connections': total_connections,
                'total_capacity': total_capacity,
                'system_load_percentage': (total_connections / max(1, total_capacity)) * 100,
                'total_delivery_partners': total_delivery_partners,
                'total_orders_processed': self.stats['total_orders'],
                'success_rate': (self.stats['successful_assignments'] / max(1, self.stats['total_orders'])) * 100,
                'avg_assignment_time': f"{self.stats['avg_assignment_time']:.1f}ms",
                'peak_connections': self.stats['peak_connections']
            },
            'city_stats': dict(city_stats),
            'server_details': [
                {
                    'name': s.name,
                    'city': s.city,
                    'zone': s.zone,
                    'health': 'Healthy' if s.is_healthy else 'Unhealthy',
                    'connections': f"{s.active_connections}/{s.max_connections}",
                    'load_percentage': f"{(s.active_connections/s.max_connections)*100:.1f}%",
                    'delivery_partners': f"{s.active_delivery_partners}/{s.delivery_partner_count}",
                    'success_rate': f"{s.success_rate:.1f}%",
                    'orders_processed': s.total_orders_processed,
                    'avg_processing_time': f"{s.avg_order_processing_time:.2f}s"
                }
                for s in self.servers
            ]
        }


def simulate_swiggy_dinner_rush():
    """Simulate Swiggy dinner rush with high concurrent orders"""
    
    print("\n🍽️ Simulating Swiggy Dinner Rush (8 PM - 10 PM)")
    print("=" * 60)
    
    load_balancer = SwiggyLeastConnectionsLoadBalancer()
    
    # Generate realistic dinner orders
    orders = []
    
    # Popular delivery locations in major cities
    delivery_locations = [
        # Mumbai
        ((19.0760, 72.8777), (19.0896, 72.8656), "Mumbai", 850, 3, 25),  # Bandra
        ((19.1136, 72.8697), (19.1197, 72.8464), "Mumbai", 920, 4, 30),  # Andheri
        ((19.0176, 72.8489), (19.0123, 72.8420), "Mumbai", 1200, 2, 35),  # South Mumbai
        
        # Delhi
        ((28.5355, 77.3910), (28.5321, 77.3865), "Delhi", 750, 3, 28),   # CP area
        ((28.4595, 77.0266), (28.4734, 77.0365), "Gurgaon", 980, 5, 25), # DLF
        
        # Bangalore
        ((12.9352, 77.6245), (12.9279, 77.6271), "Bangalore", 680, 4, 30), # Koramangala
        ((12.9698, 77.7500), (12.9612, 77.7645), "Bangalore", 720, 3, 35), # Whitefield
        
        # Hyderabad
        ((17.4435, 78.3772), (17.4399, 78.3821), "Hyderabad", 580, 2, 25), # Hitech City
        
        # Chennai
        ((13.0827, 80.2707), (13.0756, 80.2834), "Chennai", 520, 3, 30),   # Central
        
        # Pune
        ((18.5679, 73.9143), (18.5592, 73.9088), "Pune", 450, 2, 20),     # Hinjewadi
    ]
    
    # Generate 150 concurrent dinner orders
    for i in range(150):
        customer_loc, restaurant_loc, city, value, items, prep_time = random.choice(delivery_locations)
        
        # Add some variation
        lat_var = random.uniform(-0.01, 0.01)
        lng_var = random.uniform(-0.01, 0.01)
        customer_loc = (customer_loc[0] + lat_var, customer_loc[1] + lng_var)
        
        order = SwiggyOrder(
            order_id=f"SWGY_DINNER_{i:03d}",
            customer_id=f"CUST_{random.randint(100000, 999999)}",
            restaurant_id=f"REST_{city.upper()}_{random.randint(1000, 9999)}",
            customer_location=customer_loc,
            restaurant_location=restaurant_loc,
            order_value=value + random.uniform(-100, 200),
            item_count=items + random.randint(-1, 2),
            estimated_prep_time=prep_time + random.randint(-5, 10),
            delivery_priority=random.choices([1, 2, 3], weights=[70, 25, 5])[0]  # Weighted priority
        )
        
        orders.append(order)
    
    # Process orders concurrently (simulating high load)
    print(f"Processing {len(orders)} dinner orders concurrently...")
    
    results = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(load_balancer.process_order, order) for order in orders]
        
        for future in futures:
            try:
                result = future.result(timeout=15)
                results.append(result)
            except Exception as e:
                logger.error(f"Order processing timeout: {e}")
    
    return load_balancer, results


def main():
    """Main demonstration of Swiggy Least Connections Load Balancer"""
    
    print("🍔 स्विगी Least Connections लोड बैलेंसर")
    print("=" * 60)
    
    # Simulate dinner rush
    load_balancer, results = simulate_swiggy_dinner_rush()
    
    # Analyze results
    successful_orders = sum(1 for r in results if r.get('success', False))
    failed_orders = len(results) - successful_orders
    
    print(f"\n📊 Dinner Rush Results:")
    print(f"Total Orders: {len(results)}")
    print(f"Successfully Assigned: {successful_orders}")
    print(f"Failed Assignments: {failed_orders}")
    print(f"Success Rate: {(successful_orders/len(results))*100:.1f}%")
    
    # Show sample successful assignments
    print(f"\n🚚 Sample Successful Order Assignments:")
    successful_results = [r for r in results if r.get('success', False)][:5]
    
    for result in successful_results:
        print(f"  Order: {result.get('order_id')} - ETA: {result.get('estimated_delivery_time')}min")
        print(f"    Server: {result.get('server_used')} ({result.get('server_zone')})")
        print(f"    Delivery Partner: {result.get('delivery_partner_id')}")
        print(f"    Processing Time: {result.get('processing_time_ms', 0):.1f}ms")
    
    # Get comprehensive statistics
    time.sleep(1)  # Allow for final metrics update
    
    print(f"\n📈 System Performance Statistics:")
    print("=" * 50)
    
    stats = load_balancer.get_system_stats()
    
    # System overview
    system_overview = stats['system_overview']
    print(f"System Overview:")
    print(f"  Total Servers: {system_overview['total_servers']}")
    print(f"  Healthy Servers: {system_overview['healthy_servers']}")
    print(f"  Active Connections: {system_overview['total_connections']}/{system_overview['total_capacity']}")
    print(f"  System Load: {system_overview['system_load_percentage']:.1f}%")
    print(f"  Peak Connections: {system_overview['peak_connections']}")
    print(f"  Total Delivery Partners: {system_overview['total_delivery_partners']}")
    print(f"  Overall Success Rate: {system_overview['success_rate']:.1f}%")
    print(f"  Average Assignment Time: {system_overview['avg_assignment_time']}")
    
    # City-wise performance
    print(f"\n🏙️ City-wise Performance:")
    print("-" * 80)
    print(f"{'City':<15} {'Servers':<12} {'Load':<15} {'Partners':<12} {'Success Rate':<12}")
    print("-" * 80)
    
    for city, city_stats in stats['city_stats'].items():
        print(f"{city:<15} "
              f"{city_stats['healthy_servers']}/{city_stats['servers']:<12} "
              f"{city_stats['load_percentage']:.1f}%{'':(<10)} "
              f"{city_stats['delivery_partners']:<12} "
              f"{city_stats['avg_success_rate']:.1f}%{'':(<8)}")
    
    # Top servers by load
    server_details = sorted(stats['server_details'], 
                           key=lambda s: float(s['load_percentage'].rstrip('%')), 
                           reverse=True)
    
    print(f"\n🏆 Top Loaded Servers:")
    print("-" * 90)
    print(f"{'Server':<35} {'City':<12} {'Zone':<20} {'Load':<15} {'Partners':<12} {'Orders':<8}")
    print("-" * 90)
    
    for server in server_details[:8]:  # Top 8
        print(f"{server['name']:<35} "
              f"{server['city']:<12} "
              f"{server['zone']:<20} "
              f"{server['connections']:<15} "
              f"{server['delivery_partners']:<12} "
              f"{server['orders_processed']:<8}")
    
    # Performance insights
    print(f"\n💡 Performance Insights:")
    print("=" * 35)
    print("🎯 Least connections algorithm ensures optimal load distribution")
    print("🌍 Geographic routing reduces delivery time and costs")
    print("📊 Real-time partner availability affects server selection")
    print("⚡ Connection-based routing prevents server overload")
    print("🚀 Priority orders get preferential server allocation")
    
    print(f"\n🔧 Optimization Recommendations:")
    print("📱 Implement predictive load balancing for peak hours")
    print("🗺️ Use AI-based delivery partner optimization")
    print("⏰ Dynamic server scaling based on order patterns")
    print("📈 Real-time traffic data integration for better routing")
    print("🏍️ Partner location tracking for smarter assignments")


if __name__ == "__main__":
    main()