# 🐍 Python Service Discovery Examples
## Episode 64: Service Discovery - Python Implementations

---

## 🇮🇳 भारतीय Context में Service Discovery

Service discovery Indian microservices architecture का heart है। Flipkart के जैसे e-commerce platforms पर millions of services run करती हैं - product catalog, payment gateway, inventory, shipping - सबको efficiently communicate करना पड़ता है।

Mumbai local trains की तरह, services को पता होना चाहिए कि कौन सी service कहाँ available है, कितनी healthy है, और कैसे reach करना है।

---

## 📂 Examples Structure

```
python/
├── 01_consul_service_discovery.py      # Consul-based discovery (Flipkart style)
├── 02_etcd_service_registry.py         # etcd v3 service registry (K8s native)
├── 03_eureka_client_implementation.py  # Netflix Eureka pattern
├── 04_zookeeper_coordination.py        # Distributed coordination
├── 05_custom_dns_discovery.py          # Lightweight DNS-based discovery
├── requirements.txt                     # Python dependencies
├── tests/                              # Unit tests
│   ├── test_consul_discovery.py
│   ├── test_etcd_registry.py
│   └── test_dns_discovery.py
└── README.md                           # This file
```

---

## 🚀 Example 1: Consul Service Discovery (Flipkart Style)

```python
# 01_consul_service_discovery.py
"""
🇮🇳 Flipkart-style Service Discovery using Consul
Mumbai के distribution centers की तरह services को organize करता है
"""

import consul
import json
import time
import random
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional
import requests
import logging

# Hindi logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FlipkartServiceDiscovery')

@dataclass
class ServiceInstance:
    """Service instance information - Flipkart style"""
    name: str
    host: str
    port: int
    health_endpoint: str
    tags: List[str]
    metadata: Dict[str, str]
    region: str = "mumbai"  # Default Mumbai region
    
class FlipkartServiceDiscovery:
    """
    Flipkart-style service discovery using Consul
    
    Mumbai warehouse analogy:
    - Consul = Central warehouse management system
    - Services = Individual warehouses (Pune, Delhi, Bangalore)
    - Health checks = Warehouse inventory status
    - Load balancing = Order routing to nearest warehouse
    """
    
    def __init__(self, consul_host='localhost', consul_port=8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.local_services = {}
        self.health_check_thread = None
        self.running = True
        
        logger.info(f"🏪 Flipkart Service Discovery initialized")
        logger.info(f"📍 Consul endpoint: {consul_host}:{consul_port}")
    
    def register_service(self, service: ServiceInstance) -> bool:
        """
        Register a service with Consul
        
        Mumbai warehouse registration जैसा:
        - Service details store करते हैं
        - Health check URL setup करते हैं  
        - Regional tagging करते हैं
        """
        try:
            # Flipkart style service ID
            service_id = f"{service.name}-{service.region}-{service.host}-{service.port}"
            
            # Health check configuration
            health_check = consul.Check.http(
                service.health_endpoint,
                interval="10s",
                timeout="5s",
                deregister="30s"  # Auto cleanup after 30s
            )
            
            # Register service with metadata
            success = self.consul.agent.service.register(
                name=service.name,
                service_id=service_id,
                address=service.host,
                port=service.port,
                tags=service.tags + [f"region:{service.region}"],
                check=health_check,
                meta=service.metadata
            )
            
            if success:
                self.local_services[service_id] = service
                logger.info(f"✅ Service registered: {service_id}")
                logger.info(f"🏪 {service.name} warehouse available in {service.region}")
                return True
            else:
                logger.error(f"❌ Failed to register service: {service_id}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Registration error: {str(e)}")
            return False
    
    def discover_services(self, service_name: str, 
                         region: Optional[str] = None,
                         tag: Optional[str] = None) -> List[ServiceInstance]:
        """
        Discover available services
        
        Flipkart warehouse discovery:
        - Available warehouses find करते हैं
        - Region-wise filtering
        - Tag-based service filtering (payment, inventory, shipping)
        """
        try:
            # Build query filter
            query_tags = []
            if region:
                query_tags.append(f"region:{region}")
            if tag:
                query_tags.append(tag)
            
            # Get services from Consul
            _, services = self.consul.health.service(
                service_name,
                passing=True,  # Only healthy services
                tag=tag
            )
            
            discovered_services = []
            
            for service in services:
                service_info = service['Service']
                
                # Extract region from tags
                service_region = "unknown"
                for tag in service_info.get('Tags', []):
                    if tag.startswith('region:'):
                        service_region = tag.split(':', 1)[1]
                        break
                
                # Region filtering
                if region and service_region != region:
                    continue
                
                # Create ServiceInstance
                instance = ServiceInstance(
                    name=service_info['Service'],
                    host=service_info['Address'],
                    port=service_info['Port'],
                    health_endpoint=f"http://{service_info['Address']}:{service_info['Port']}/health",
                    tags=service_info.get('Tags', []),
                    metadata=service_info.get('Meta', {}),
                    region=service_region
                )
                
                discovered_services.append(instance)
            
            logger.info(f"🔍 Discovered {len(discovered_services)} instances of {service_name}")
            if region:
                logger.info(f"📍 Filtered by region: {region}")
            
            return discovered_services
            
        except Exception as e:
            logger.error(f"💥 Discovery error: {str(e)}")
            return []
    
    def get_service_instance(self, service_name: str, 
                           load_balancing: str = "round_robin") -> Optional[ServiceInstance]:
        """
        Get a single service instance using load balancing
        
        Flipkart order routing strategy:
        - round_robin: Equal distribution (सभी warehouses को equally use करें)
        - random: Random selection (Mumbai local train compartment selection जैसा)
        - least_connections: Least loaded (कम busy warehouse choose करें)
        """
        instances = self.discover_services(service_name)
        
        if not instances:
            logger.warning(f"⚠️ No instances found for {service_name}")
            return None
        
        if load_balancing == "round_robin":
            # Simple round-robin using current time
            index = int(time.time()) % len(instances)
            selected = instances[index]
            
        elif load_balancing == "random":
            selected = random.choice(instances)
            
        elif load_balancing == "least_connections":
            # For demo, we'll use random (in production, track actual connections)
            selected = random.choice(instances)
            
        else:
            selected = instances[0]
        
        logger.info(f"🎯 Selected instance: {selected.name} at {selected.host}:{selected.port}")
        logger.info(f"📍 Warehouse location: {selected.region}")
        
        return selected
    
    def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service from Consul
        
        Warehouse shutdown procedure:
        - Gracefully remove from discovery
        - Prevent new requests
        - Clean shutdown
        """
        try:
            success = self.consul.agent.service.deregister(service_id)
            
            if success and service_id in self.local_services:
                del self.local_services[service_id]
                logger.info(f"✅ Service deregistered: {service_id}")
                logger.info(f"🏪 Warehouse {service_id} gracefully shutdown")
                return True
            else:
                logger.error(f"❌ Failed to deregister service: {service_id}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Deregistration error: {str(e)}")
            return False
    
    def monitor_service_health(self, interval: int = 30):
        """
        Monitor health of discovered services
        
        Mumbai warehouse monitoring:
        - Regular health checks
        - Performance monitoring
        - Alerting on failures
        """
        def health_monitor():
            while self.running:
                try:
                    for service_id, service in self.local_services.items():
                        # Check service health
                        health_url = service.health_endpoint
                        
                        try:
                            response = requests.get(health_url, timeout=5)
                            if response.status_code == 200:
                                logger.info(f"💚 {service.name} healthy in {service.region}")
                            else:
                                logger.warning(f"💛 {service.name} degraded in {service.region}")
                                
                        except requests.RequestException:
                            logger.error(f"💔 {service.name} unhealthy in {service.region}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"💥 Health monitor error: {str(e)}")
                    time.sleep(interval)
        
        if not self.health_check_thread:
            self.health_check_thread = threading.Thread(target=health_monitor)
            self.health_check_thread.daemon = True
            self.health_check_thread.start()
            logger.info(f"🔍 Health monitoring started (interval: {interval}s)")
    
    def get_service_catalog(self) -> Dict[str, List[ServiceInstance]]:
        """
        Get complete service catalog
        
        Flipkart complete warehouse directory:
        - All available services
        - Region-wise distribution
        - Service metadata
        """
        try:
            _, services = self.consul.catalog.services()
            catalog = {}
            
            for service_name in services:
                instances = self.discover_services(service_name)
                if instances:
                    catalog[service_name] = instances
            
            logger.info(f"📋 Service catalog: {len(catalog)} services available")
            return catalog
            
        except Exception as e:
            logger.error(f"💥 Catalog error: {str(e)}")
            return {}
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Deregister all local services
        for service_id in list(self.local_services.keys()):
            self.deregister_service(service_id)
        
        logger.info("🛑 Flipkart Service Discovery shutdown complete")

# Usage Example
if __name__ == "__main__":
    # Initialize Flipkart service discovery
    discovery = FlipkartServiceDiscovery()
    
    # Register services (Flipkart microservices)
    services = [
        ServiceInstance(
            name="product-catalog",
            host="10.0.1.10",
            port=8080,
            health_endpoint="http://10.0.1.10:8080/health",
            tags=["catalog", "products", "core"],
            metadata={"version": "2.1.0", "datacenter": "mumbai-central"},
            region="mumbai"
        ),
        ServiceInstance(
            name="payment-gateway",
            host="10.0.1.20",
            port=8081,
            health_endpoint="http://10.0.1.20:8081/health",
            tags=["payment", "upi", "critical"],
            metadata={"version": "3.0.1", "datacenter": "mumbai-bkc"},
            region="mumbai"
        ),
        ServiceInstance(
            name="inventory-service",
            host="10.0.2.10",
            port=8082,
            health_endpoint="http://10.0.2.10:8082/health",
            tags=["inventory", "warehouse", "core"],
            metadata={"version": "1.8.0", "datacenter": "pune-hinjewadi"},
            region="pune"
        )
    ]
    
    # Register all services
    for service in services:
        discovery.register_service(service)
    
    # Start health monitoring
    discovery.monitor_service_health(interval=15)
    
    print("\n🏪 Flipkart Service Discovery Demo")
    print("=" * 50)
    
    # Service discovery examples
    print("\n1. 🔍 Discovering payment services:")
    payment_services = discovery.discover_services("payment-gateway")
    for service in payment_services:
        print(f"   💳 {service.name} @ {service.host}:{service.port} [{service.region}]")
    
    print("\n2. 🎯 Getting specific service instance:")
    catalog_instance = discovery.get_service_instance("product-catalog", "round_robin")
    if catalog_instance:
        print(f"   📦 Using {catalog_instance.name} in {catalog_instance.region}")
    
    print("\n3. 📋 Complete service catalog:")
    catalog = discovery.get_service_catalog()
    for service_name, instances in catalog.items():
        print(f"   🏪 {service_name}: {len(instances)} instances")
        for instance in instances:
            print(f"      📍 {instance.region} - {instance.host}:{instance.port}")
    
    print("\n4. 🌍 Region-specific discovery:")
    mumbai_services = discovery.discover_services("product-catalog", region="mumbai")
    print(f"   🏙️ Mumbai services: {len(mumbai_services)}")
    
    # Keep running for demo
    try:
        print("\n⏰ Monitoring services... (Ctrl+C to stop)")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        discovery.shutdown()
```

This is the complete first example. Let me create the requirements file and continue with the other examples.