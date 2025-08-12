#!/usr/bin/env python3
"""
Round-Robin Load Balancer for IRCTC Server Distribution
भारतीय रेलवे के लिए राउंड-रॉबिन लोड बैलेंसर

यह example दिखाता है कि कैसे IRCTC जैसे high-traffic systems में
round-robin load balancing implement करें multiple servers के साथ।
"""

import time
import random
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Server:
    """Server configuration and status"""
    server_id: str
    name: str
    host: str
    port: int
    region: str
    capacity: int
    current_load: int = 0
    is_healthy: bool = True
    response_time_ms: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_health_check: float = field(default_factory=time.time)


@dataclass
class BookingRequest:
    """IRCTC booking request structure"""
    request_id: str
    user_id: str
    train_number: str
    from_station: str
    to_station: str
    journey_date: str
    passenger_count: int
    booking_class: str
    mobile_number: str
    timestamp: float = field(default_factory=time.time)


class IRCTCRoundRobinLoadBalancer:
    """
    IRCTC के लिए Round-Robin Load Balancer
    भारतीय रेलवे booking system के लिए optimized
    """
    
    def __init__(self):
        self.servers: List[Server] = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.health_check_interval = 30  # seconds
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0
        }
        
        # Initialize IRCTC server fleet
        self._initialize_irctc_servers()
        
        # Start health monitoring
        self._start_health_monitoring()
        
        logger.info("🚂 IRCTC Round-Robin Load Balancer initialized")
    
    def _initialize_irctc_servers(self):
        """Initialize IRCTC server configurations across India"""
        irctc_servers = [
            Server("IRCTC_DEL_001", "Delhi Primary Server", "irctc-delhi-1.indianrailways.gov.in", 443, "North India", 10000),
            Server("IRCTC_DEL_002", "Delhi Secondary Server", "irctc-delhi-2.indianrailways.gov.in", 443, "North India", 10000),
            Server("IRCTC_MUM_001", "Mumbai Primary Server", "irctc-mumbai-1.indianrailways.gov.in", 443, "West India", 12000),
            Server("IRCTC_MUM_002", "Mumbai Secondary Server", "irctc-mumbai-2.indianrailways.gov.in", 443, "West India", 12000),
            Server("IRCTC_BLR_001", "Bangalore Primary Server", "irctc-bangalore-1.indianrailways.gov.in", 443, "South India", 8000),
            Server("IRCTC_BLR_002", "Bangalore Secondary Server", "irctc-bangalore-2.indianrailways.gov.in", 443, "South India", 8000),
            Server("IRCTC_KOL_001", "Kolkata Primary Server", "irctc-kolkata-1.indianrailways.gov.in", 443, "East India", 7000),
            Server("IRCTC_CHN_001", "Chennai Server", "irctc-chennai-1.indianrailways.gov.in", 443, "South India", 9000),
        ]
        
        self.servers = irctc_servers
        
        for server in self.servers:
            logger.info(f"📡 Added server: {server.name} ({server.region}) - Capacity: {server.capacity}")
    
    def get_next_server(self) -> Optional[Server]:
        """
        Get next server using round-robin algorithm
        राउंड-रॉबिन algorithm से अगला server लाता है
        """
        with self.lock:
            if not self.servers:
                return None
            
            # Filter healthy servers
            healthy_servers = [s for s in self.servers if s.is_healthy]
            
            if not healthy_servers:
                logger.warning("⚠️ No healthy servers available!")
                return None
            
            # Round-robin selection among healthy servers
            server = healthy_servers[self.current_index % len(healthy_servers)]
            self.current_index = (self.current_index + 1) % len(healthy_servers)
            
            return server
    
    def process_booking_request(self, request: BookingRequest) -> Dict:
        """
        Process IRCTC booking request through load balancer
        लोड बैलेंसर के माध्यम से booking request प्रोसेस करता है
        """
        start_time = time.time()
        
        # Get server for request
        server = self.get_next_server()
        
        if not server:
            self._update_stats(start_time, success=False)
            return {
                'success': False,
                'error': 'No servers available',
                'request_id': request.request_id,
                'timestamp': time.time()
            }
        
        # Check server capacity
        if server.current_load >= server.capacity:
            logger.warning(f"⚠️ Server {server.name} at full capacity")
            # Try next server
            server = self._find_available_server()
            if not server:
                self._update_stats(start_time, success=False)
                return {
                    'success': False,
                    'error': 'All servers at capacity',
                    'request_id': request.request_id,
                    'timestamp': time.time()
                }
        
        # Process request on selected server
        result = self._simulate_booking_on_server(server, request)
        
        # Update statistics
        response_time = time.time() - start_time
        self._update_stats(start_time, success=result['success'])
        self._update_server_stats(server, response_time, result['success'])
        
        result['server_used'] = server.name
        result['response_time_ms'] = response_time * 1000
        
        return result
    
    def _find_available_server(self) -> Optional[Server]:
        """Find a server with available capacity"""
        for _ in range(len(self.servers)):
            server = self.get_next_server()
            if server and server.current_load < server.capacity:
                return server
        return None
    
    def _simulate_booking_on_server(self, server: Server, request: BookingRequest) -> Dict:
        """
        Simulate booking processing on specific server
        विशिष्ट server पर booking processing की simulation
        """
        # Simulate processing time based on booking complexity
        processing_time = self._calculate_processing_time(request)
        
        # Simulate server load
        server.current_load += 1
        
        try:
            # Simulate actual booking process
            time.sleep(processing_time)
            
            # Simulate success/failure (95% success rate)
            success = random.random() > 0.05
            
            if success:
                booking_id = f"PNR{random.randint(1000000000, 9999999999)}"
                logger.info(f"✅ Booking successful: {request.request_id} -> {booking_id} on {server.name}")
                
                result = {
                    'success': True,
                    'booking_id': booking_id,
                    'request_id': request.request_id,
                    'train_number': request.train_number,
                    'from_station': request.from_station,
                    'to_station': request.to_station,
                    'journey_date': request.journey_date,
                    'status': 'CONFIRMED',
                    'message': 'Booking confirmed successfully'
                }
            else:
                logger.warning(f"❌ Booking failed: {request.request_id} on {server.name}")
                result = {
                    'success': False,
                    'error': 'Booking failed - please try again',
                    'request_id': request.request_id,
                    'status': 'FAILED'
                }
                
        except Exception as e:
            logger.error(f"💥 Server error on {server.name}: {e}")
            result = {
                'success': False,
                'error': f'Server error: {str(e)}',
                'request_id': request.request_id,
                'status': 'ERROR'
            }
        finally:
            # Release server load
            server.current_load = max(0, server.current_load - 1)
        
        return result
    
    def _calculate_processing_time(self, request: BookingRequest) -> float:
        """Calculate processing time based on request complexity"""
        base_time = 0.1  # 100ms base processing
        
        # Add complexity factors
        if request.booking_class in ['1A', '2A', '3A']:  # AC classes
            base_time += 0.05
        
        if request.passenger_count > 4:  # Large groups
            base_time += 0.03 * (request.passenger_count - 4)
        
        # Add some randomness for realistic simulation
        variation = random.uniform(0.8, 1.5)
        
        return base_time * variation
    
    def _update_stats(self, start_time: float, success: bool):
        """Update global statistics"""
        response_time = time.time() - start_time
        
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Update running average of response time
        current_avg = self.stats['avg_response_time']
        total_requests = self.stats['total_requests']
        self.stats['avg_response_time'] = (current_avg * (total_requests - 1) + response_time * 1000) / total_requests
    
    def _update_server_stats(self, server: Server, response_time: float, success: bool):
        """Update individual server statistics"""
        server.total_requests += 1
        server.response_time_ms = (server.response_time_ms + response_time * 1000) / 2  # Simple moving average
        
        if success:
            server.successful_requests += 1
        else:
            server.failed_requests += 1
    
    def _start_health_monitoring(self):
        """Start health monitoring for servers"""
        def health_check():
            while True:
                for server in self.servers:
                    # Simulate health check
                    server.is_healthy = random.random() > 0.02  # 2% chance of unhealthy
                    server.last_health_check = time.time()
                    
                    if not server.is_healthy:
                        logger.warning(f"🔴 Server {server.name} marked unhealthy")
                    
                time.sleep(self.health_check_interval)
        
        health_thread = threading.Thread(target=health_check, daemon=True)
        health_thread.start()
    
    def get_load_balancer_stats(self) -> Dict:
        """Get comprehensive load balancer statistics"""
        healthy_servers = sum(1 for s in self.servers if s.is_healthy)
        total_capacity = sum(s.capacity for s in self.servers if s.is_healthy)
        current_load = sum(s.current_load for s in self.servers if s.is_healthy)
        
        server_stats = []
        for server in self.servers:
            success_rate = (server.successful_requests / max(1, server.total_requests)) * 100
            
            server_stats.append({
                'name': server.name,
                'region': server.region,
                'health': 'Healthy' if server.is_healthy else 'Unhealthy',
                'load': f"{server.current_load}/{server.capacity}",
                'load_percentage': f"{(server.current_load/server.capacity)*100:.1f}%",
                'total_requests': server.total_requests,
                'success_rate': f"{success_rate:.1f}%",
                'avg_response_time': f"{server.response_time_ms:.1f}ms"
            })
        
        return {
            'load_balancer_stats': {
                'total_servers': len(self.servers),
                'healthy_servers': healthy_servers,
                'total_capacity': total_capacity,
                'current_load': current_load,
                'system_load_percentage': f"{(current_load/max(1, total_capacity))*100:.1f}%",
                'total_requests': self.stats['total_requests'],
                'success_rate': f"{(self.stats['successful_requests']/max(1, self.stats['total_requests']))*100:.1f}%",
                'avg_response_time': f"{self.stats['avg_response_time']:.1f}ms"
            },
            'server_details': server_stats
        }


def simulate_tatkal_booking_rush():
    """
    Simulate Tatkal booking rush scenario
    तत्काल booking rush की simulation
    """
    print("\n🚄 Simulating Tatkal Booking Rush (तत्काल बुकिंग रश)")
    print("=" * 60)
    
    load_balancer = IRCTCRoundRobinLoadBalancer()
    
    # Generate high-volume booking requests
    booking_requests = []
    
    # Popular trains and routes
    popular_trains = [
        ("12951", "Mumbai Central", "New Delhi", "Rajdhani Express"),
        ("12301", "Howrah", "New Delhi", "Howrah Rajdhani"),
        ("12621", "Chennai Central", "New Delhi", "Tamil Nadu Express"),
        ("12002", "Bhopal", "New Delhi", "Shatabdi Express"),
        ("18621", "Jammu Tawi", "New Delhi", "Jammu Mail"),
    ]
    
    # Generate 50 concurrent booking requests
    for i in range(50):
        train_info = random.choice(popular_trains)
        
        request = BookingRequest(
            request_id=f"REQ_TATKAL_{i:03d}",
            user_id=f"USER_{random.randint(100000, 999999)}",
            train_number=train_info[0],
            from_station=train_info[1],
            to_station=train_info[2],
            journey_date="2024-12-25",  # Christmas travel
            passenger_count=random.randint(1, 6),
            booking_class=random.choice(["SL", "3A", "2A", "1A"]),
            mobile_number=f"9{random.randint(100000000, 999999999)}"
        )
        
        booking_requests.append(request)
    
    # Process requests concurrently (simulating Tatkal rush)
    print(f"Processing {len(booking_requests)} booking requests...")
    
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(load_balancer.process_booking_request, req) 
                  for req in booking_requests]
        
        for future in futures:
            try:
                result = future.result(timeout=10)
                results.append(result)
            except Exception as e:
                logger.error(f"Request processing error: {e}")
    
    # Analyze results
    successful_bookings = sum(1 for r in results if r.get('success', False))
    failed_bookings = len(results) - successful_bookings
    
    print(f"\n📊 Tatkal Rush Results:")
    print(f"Total Requests: {len(booking_requests)}")
    print(f"Successful Bookings: {successful_bookings}")
    print(f"Failed Bookings: {failed_bookings}")
    print(f"Success Rate: {(successful_bookings/len(results))*100:.1f}%")
    
    # Show sample successful bookings
    print(f"\n🎫 Sample Successful Bookings:")
    successful_results = [r for r in results if r.get('success', False)][:5]
    
    for result in successful_results:
        print(f"  PNR: {result.get('booking_id')} - {result.get('train_number')} "
              f"({result.get('from_station')} → {result.get('to_station')})")
        print(f"    Server: {result.get('server_used')}, "
              f"Response: {result.get('response_time_ms', 0):.1f}ms")
    
    return load_balancer


def main():
    """Main demonstration of IRCTC Round-Robin Load Balancer"""
    
    print("🚂 भारतीय रेलवे IRCTC राउंड-रॉबिन लोड बैलेंसर")
    print("=" * 70)
    
    # Simulate Tatkal booking rush
    load_balancer = simulate_tatkal_booking_rush()
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Display comprehensive statistics
    print(f"\n📈 Load Balancer Performance Statistics:")
    print("=" * 50)
    
    stats = load_balancer.get_load_balancer_stats()
    
    # System-level stats
    lb_stats = stats['load_balancer_stats']
    print(f"System Overview:")
    print(f"  Total Servers: {lb_stats['total_servers']}")
    print(f"  Healthy Servers: {lb_stats['healthy_servers']}")
    print(f"  System Load: {lb_stats['system_load_percentage']}")
    print(f"  Total Requests: {lb_stats['total_requests']}")
    print(f"  Overall Success Rate: {lb_stats['success_rate']}")
    print(f"  Average Response Time: {lb_stats['avg_response_time']}")
    
    # Individual server performance
    print(f"\n🖥️ Individual Server Performance:")
    print("-" * 80)
    print(f"{'Server Name':<25} {'Region':<12} {'Health':<10} {'Load':<12} {'Requests':<10} {'Success':<8} {'Avg RT':<8}")
    print("-" * 80)
    
    for server_stat in stats['server_details']:
        print(f"{server_stat['name']:<25} "
              f"{server_stat['region']:<12} "
              f"{server_stat['health']:<10} "
              f"{server_stat['load']:<12} "
              f"{server_stat['total_requests']:<10} "
              f"{server_stat['success_rate']:<8} "
              f"{server_stat['avg_response_time']:<8}")
    
    # Recommendations
    print(f"\n💡 Operational Recommendations:")
    print("=" * 40)
    print("✅ Round-Robin ensures fair distribution across servers")
    print("⚡ Consider weighted round-robin for servers with different capacities")
    print("🔄 Implement sticky sessions for multi-step booking process")
    print("📊 Monitor server health and automatically remove unhealthy servers")
    print("🚀 Use geographic load balancing for better user experience")
    print("⏱️ Implement request timeouts to prevent cascading failures")
    
    print(f"\n🎯 IRCTC-Specific Optimizations:")
    print("🚂 Prioritize servers closer to user's location")
    print("⏰ Scale up servers before peak booking hours (10 AM, 11 AM)")
    print("🎫 Implement queue-based system for Tatkal bookings")
    print("💳 Separate payment processing servers for better isolation")
    print("📱 Mobile-optimized servers for app-based bookings")


if __name__ == "__main__":
    main()