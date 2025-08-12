#!/usr/bin/env python3
"""
Flipkart-style Product Service Discovery
Consul-based service discovery for distributed product catalog

जैसे Flipkart में millions products हैं, वैसे ही हमारे services का catalog
Mumbai के market जैसे - har shop का address aur specialty पता होनी चाहिए
"""

import consul
import time
import json
import logging
import threading
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from flask import Flask, jsonify, request
import requests

# Configure logging - Production में proper log aggregation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProductService:
    """
    Product service information
    जैसे Flipkart में har category का alag service - Electronics, Fashion, Books
    """
    service_id: str
    service_name: str
    address: str
    port: int
    category: str  # electronics, fashion, books, grocery
    capacity: int  # concurrent requests handle kar sakta hai
    region: str    # mumbai, delhi, bangalore
    version: str
    health_status: str = "unknown"
    load_score: float = 0.0  # 0-100, lower is better

class FlipkartServiceDiscovery:
    """
    Flipkart-style service discovery with product catalog management
    Mumbai के wholesale market की tarah - har vendor का location aur specialty
    """
    
    def __init__(self, consul_host='localhost', consul_port=8500):
        """Initialize service discovery client"""
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.local_cache = {}  # Service cache for faster lookups
        self.last_update = 0
        self.cache_ttl = 30  # seconds
        
        # Load balancing strategies
        self.lb_strategies = {
            'round_robin': self._round_robin_select,
            'weighted': self._weighted_select,
            'least_connections': self._least_connections_select
        }
        
        logger.info("Flipkart Service Discovery initialized - Ready like Dadar market!")
    
    def register_product_service(self, service: ProductService) -> bool:
        """
        Register product service with Consul
        जैसे नया shop Crawford Market में register करना
        """
        try:
            # Health check configuration
            health_check = consul.Check.http(
                url=f"http://{service.address}:{service.port}/health",
                timeout="10s",
                interval="30s",
                deregister="60s"
            )
            
            # Service metadata - Flipkart style tagging
            tags = [
                f"category:{service.category}",
                f"region:{service.region}",
                f"version:{service.version}",
                f"capacity:{service.capacity}",
                "flipkart-product-service"
            ]
            
            # Register service
            success = self.consul.agent.service.register(
                name=service.service_name,
                service_id=service.service_id,
                address=service.address,
                port=service.port,
                tags=tags,
                check=health_check,
                meta={
                    'category': service.category,
                    'region': service.region,
                    'capacity': str(service.capacity),
                    'version': service.version,
                    'registered_at': str(int(time.time()))
                }
            )
            
            if success:
                logger.info(f"Product service {service.service_name} registered successfully!")
                logger.info(f"Category: {service.category}, Region: {service.region}")
                return True
            else:
                logger.error(f"Failed to register service {service.service_name}")
                return False
                
        except Exception as e:
            logger.error(f"Service registration error: {e}")
            return False
    
    def discover_product_services(self, category: Optional[str] = None, 
                                region: Optional[str] = None) -> List[ProductService]:
        """
        Discover available product services by category and region
        जैसे Zomato में nearby restaurants by cuisine type
        """
        try:
            # Check cache first - Mumbai traffic में time bachana hai
            cache_key = f"{category}_{region}"
            current_time = time.time()
            
            if (cache_key in self.local_cache and 
                current_time - self.last_update < self.cache_ttl):
                logger.info(f"Returning cached services for {cache_key}")
                return self.local_cache[cache_key]
            
            # Query Consul for services
            index, services = self.consul.health.service(
                service='product-service',
                passing=True  # Only healthy services
            )
            
            discovered_services = []
            for service_data in services:
                service_info = service_data['Service']
                checks = service_data['Checks']
                
                # Parse service metadata
                tags = service_info.get('Tags', [])
                meta = service_info.get('Meta', {})
                
                # Extract category and region from tags
                svc_category = self._extract_tag_value(tags, 'category')
                svc_region = self._extract_tag_value(tags, 'region')
                svc_capacity = int(self._extract_tag_value(tags, 'capacity', '100'))
                svc_version = self._extract_tag_value(tags, 'version', '1.0.0')
                
                # Filter by category and region if specified
                if category and svc_category != category:
                    continue
                if region and svc_region != region:
                    continue
                
                # Determine health status
                health_status = "healthy"
                for check in checks:
                    if check['Status'] != 'passing':
                        health_status = "unhealthy"
                        break
                
                # Create service object
                product_service = ProductService(
                    service_id=service_info['ID'],
                    service_name=service_info['Service'],
                    address=service_info['Address'],
                    port=service_info['Port'],
                    category=svc_category,
                    capacity=svc_capacity,
                    region=svc_region,
                    version=svc_version,
                    health_status=health_status,
                    load_score=self._calculate_load_score(service_info['ID'])
                )
                
                discovered_services.append(product_service)
            
            # Update cache
            self.local_cache[cache_key] = discovered_services
            self.last_update = current_time
            
            logger.info(f"Discovered {len(discovered_services)} services - "
                       f"Like finding good vadapav stalls in Dadar!")
            
            return discovered_services
            
        except Exception as e:
            logger.error(f"Service discovery error: {e}")
            return []
    
    def get_best_service(self, category: str, region: str = None, 
                        strategy: str = 'weighted') -> Optional[ProductService]:
        """
        Get best service based on load balancing strategy
        जैसे Mumbai में fastest route choose करना traffic के according
        """
        services = self.discover_product_services(category, region)
        
        if not services:
            logger.warning(f"No services found for category: {category}")
            return None
        
        # Filter only healthy services
        healthy_services = [s for s in services if s.health_status == "healthy"]
        
        if not healthy_services:
            logger.warning(f"No healthy services found for category: {category}")
            return None
        
        # Apply load balancing strategy
        lb_func = self.lb_strategies.get(strategy, self._weighted_select)
        selected_service = lb_func(healthy_services)
        
        logger.info(f"Selected service: {selected_service.service_id} "
                   f"using {strategy} strategy")
        
        return selected_service
    
    def _extract_tag_value(self, tags: List[str], key: str, default: str = '') -> str:
        """Extract value from tags list"""
        for tag in tags:
            if tag.startswith(f"{key}:"):
                return tag.split(':', 1)[1]
        return default
    
    def _calculate_load_score(self, service_id: str) -> float:
        """
        Calculate service load score (0-100)
        Production में actual metrics से calculate करेंगे - CPU, memory, response time
        """
        # Simulated load calculation
        # Real implementation would query metrics from Prometheus/DataDog
        return random.uniform(10.0, 90.0)
    
    def _round_robin_select(self, services: List[ProductService]) -> ProductService:
        """Round robin selection"""
        # Simple implementation - production में proper state management
        return services[int(time.time()) % len(services)]
    
    def _weighted_select(self, services: List[ProductService]) -> ProductService:
        """Weighted selection based on capacity and load"""
        # Calculate weights (higher capacity, lower load = higher weight)
        weights = []
        for service in services:
            # Weight formula: capacity / (load_score + 1)
            weight = service.capacity / (service.load_score + 1)
            weights.append(weight)
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return services[0]
        
        r = random.uniform(0, total_weight)
        for i, weight in enumerate(weights):
            r -= weight
            if r <= 0:
                return services[i]
        
        return services[-1]
    
    def _least_connections_select(self, services: List[ProductService]) -> ProductService:
        """Select service with least load score"""
        return min(services, key=lambda s: s.load_score)

class ProductServiceApp:
    """
    Sample Product Service Application
    जैसे Flipkart का electronics service या fashion service
    """
    
    def __init__(self, service_id: str, category: str, port: int, region: str = "mumbai"):
        self.app = Flask(__name__)
        self.service_id = service_id
        self.category = category
        self.port = port
        self.region = region
        self.discovery = FlipkartServiceDiscovery()
        
        # Service metrics for load calculation
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        self._setup_routes()
        self._register_service()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            uptime = time.time() - self.start_time
            return jsonify({
                'status': 'healthy',
                'service_id': self.service_id,
                'category': self.category,
                'region': self.region,
                'uptime': uptime,
                'request_count': self.request_count,
                'error_rate': self.error_count / max(self.request_count, 1),
                'message': f'{self.category} service running like Dabbawalas!'
            })
        
        @self.app.route('/products', methods=['GET'])
        def get_products():
            """Get products for this category"""
            self.request_count += 1
            
            # Simulate some processing time
            time.sleep(random.uniform(0.1, 0.5))
            
            sample_products = self._generate_sample_products()
            
            return jsonify({
                'category': self.category,
                'region': self.region,
                'products': sample_products,
                'count': len(sample_products),
                'service_id': self.service_id
            })
        
        @self.app.route('/product/<product_id>', methods=['GET'])
        def get_product(product_id):
            """Get specific product"""
            self.request_count += 1
            
            # Simulate database lookup
            product = {
                'id': product_id,
                'category': self.category,
                'name': f'Sample {self.category} Product {product_id}',
                'price': random.randint(500, 50000),
                'currency': 'INR',
                'availability': 'in_stock',
                'region': self.region,
                'service_id': self.service_id
            }
            
            return jsonify(product)
    
    def _generate_sample_products(self) -> List[Dict]:
        """Generate sample products based on category"""
        products = []
        
        if self.category == 'electronics':
            products = [
                {'id': 'mob001', 'name': 'OnePlus 12', 'price': 65999, 'brand': 'OnePlus'},
                {'id': 'lap001', 'name': 'MacBook Air M2', 'price': 119900, 'brand': 'Apple'},
                {'id': 'tv001', 'name': 'Samsung 55" 4K TV', 'price': 42999, 'brand': 'Samsung'}
            ]
        elif self.category == 'fashion':
            products = [
                {'id': 'shirt001', 'name': 'Cotton Shirt', 'price': 1299, 'brand': 'Allen Solly'},
                {'id': 'jeans001', 'name': 'Slim Fit Jeans', 'price': 2499, 'brand': 'Levis'},
                {'id': 'shoe001', 'name': 'Running Shoes', 'price': 4999, 'brand': 'Nike'}
            ]
        elif self.category == 'books':
            products = [
                {'id': 'book001', 'name': 'System Design Interview', 'price': 899, 'author': 'Alex Xu'},
                {'id': 'book002', 'name': 'Clean Code', 'price': 1299, 'author': 'Robert Martin'},
                {'id': 'book003', 'name': 'Designing Data-Intensive Applications', 'price': 1599, 'author': 'Martin Kleppmann'}
            ]
        
        # Add service metadata to each product
        for product in products:
            product.update({
                'region': self.region,
                'service_id': self.service_id,
                'currency': 'INR'
            })
        
        return products
    
    def _register_service(self):
        """Register this service with discovery"""
        service = ProductService(
            service_id=self.service_id,
            service_name='product-service',
            address='localhost',
            port=self.port,
            category=self.category,
            capacity=100,  # Can handle 100 concurrent requests
            region=self.region,
            version='1.0.0'
        )
        
        success = self.discovery.register_product_service(service)
        if success:
            logger.info(f"Service {self.service_id} registered successfully!")
        else:
            logger.error(f"Failed to register service {self.service_id}")
    
    def run(self):
        """Start the service"""
        logger.info(f"Starting {self.category} service on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

def demo_service_discovery():
    """
    Demo function showing service discovery in action
    जैसे Flipkart में different services को discover करना
    """
    print("\n=== Flipkart-style Service Discovery Demo ===")
    print("Mumbai के market जैसे service discovery!")
    
    discovery = FlipkartServiceDiscovery()
    
    # Register sample services
    services = [
        ProductService('electronics-mumbai-001', 'product-service', 'localhost', 8001, 
                      'electronics', 150, 'mumbai', '1.0.0'),
        ProductService('fashion-mumbai-001', 'product-service', 'localhost', 8002, 
                      'fashion', 120, 'mumbai', '1.0.0'),
        ProductService('books-delhi-001', 'product-service', 'localhost', 8003, 
                      'books', 100, 'delhi', '1.0.0'),
        ProductService('electronics-bangalore-001', 'product-service', 'localhost', 8004, 
                      'electronics', 200, 'bangalore', '1.1.0'),
    ]
    
    # Register all services
    for service in services:
        discovery.register_product_service(service)
        time.sleep(0.5)
    
    print("\n--- Service Discovery Examples ---")
    
    # 1. Find all electronics services
    print("\n1. Finding all electronics services:")
    electronics_services = discovery.discover_product_services(category='electronics')
    for service in electronics_services:
        print(f"  - {service.service_id}: {service.region} (capacity: {service.capacity})")
    
    # 2. Find services in Mumbai
    print("\n2. Finding services in Mumbai:")
    mumbai_services = discovery.discover_product_services(region='mumbai')
    for service in mumbai_services:
        print(f"  - {service.service_id}: {service.category}")
    
    # 3. Get best service for electronics
    print("\n3. Getting best electronics service (weighted selection):")
    best_service = discovery.get_best_service('electronics', strategy='weighted')
    if best_service:
        print(f"  - Selected: {best_service.service_id}")
        print(f"  - Region: {best_service.region}, Capacity: {best_service.capacity}")
        print(f"  - Load Score: {best_service.load_score:.2f}")
    
    # 4. Load balancing comparison
    print("\n4. Load balancing strategy comparison:")
    strategies = ['round_robin', 'weighted', 'least_connections']
    for strategy in strategies:
        selected = discovery.get_best_service('electronics', strategy=strategy)
        if selected:
            print(f"  - {strategy}: {selected.service_id} (load: {selected.load_score:.2f})")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'demo':
            demo_service_discovery()
        elif sys.argv[1] == 'service':
            # Start a sample service
            category = sys.argv[2] if len(sys.argv) > 2 else 'electronics'
            port = int(sys.argv[3]) if len(sys.argv) > 3 else 8001
            service_id = f"{category}-mumbai-{port}"
            
            service_app = ProductServiceApp(service_id, category, port)
            service_app.run()
    else:
        print("Usage:")
        print("  python flipkart_product_discovery.py demo")
        print("  python flipkart_product_discovery.py service [category] [port]")
        print("\nExample:")
        print("  python flipkart_product_discovery.py service electronics 8001")