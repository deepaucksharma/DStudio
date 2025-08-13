#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service Discovery with Consul - Indian Company Implementation
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे Ola जैसी companies
service discovery के लिए Consul का इस्तेमाल करती हैं।

Real-world scenario: Ola का dynamic service registration और discovery
"""

import consul
import json
import time
import socket
import threading
import requests
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from loguru import logger
import asyncio
import random

@dataclass
class OlaService:
    """Ola service definition for service discovery"""
    service_id: str
    service_name: str
    address: str
    port: int
    tags: List[str]
    health_check_url: str
    metadata: Dict[str, str]
    region: str  # mumbai, bangalore, delhi
    zone: str   # central, east, west, north, south

class OlaServiceDiscovery:
    """
    Ola-style Service Discovery using Consul
    Production-ready implementation with Indian city-based routing
    """
    
    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        # Consul client initialization
        self.consul_client = consul.Consul(host=consul_host, port=consul_port)
        
        # Indian city-specific configurations
        self.city_zones = {
            "mumbai": ["andheri", "bandra", "worli", "powai", "thane"],
            "bangalore": ["koramangala", "whitefield", "indiranagar", "jayanagar", "electronic_city"],
            "delhi": ["cp", "gurgaon", "noida", "dwarka", "rohini"],
            "pune": ["hadapsar", "hinjewadi", "kothrud", "viman_nagar", "wakad"],
            "hyderabad": ["hitech_city", "gachibowli", "jubilee_hills", "banjara_hills", "secunderabad"]
        }
        
        # Service registry in memory (backup)
        self.local_registry: Dict[str, OlaService] = {}
        
        # Health check thread control
        self.health_check_running = False
        self.health_check_thread = None
        
        logger.info("🚗 Ola Service Discovery initialized!")
        logger.info(f"Connected to Consul at {consul_host}:{consul_port}")
    
    def register_service(self, service: OlaService) -> bool:
        """
        Service registration in Consul - Ola microservice को register करना
        """
        try:
            # Health check configuration
            health_check = consul.Check.http(
                url=service.health_check_url,
                interval="10s",
                timeout="5s",
                deregister_critical_service_after="30s"
            )
            
            # Service registration with Consul
            registration_result = self.consul_client.agent.service.register(
                name=service.service_name,
                service_id=service.service_id,
                address=service.address,
                port=service.port,
                tags=service.tags + [service.region, service.zone],
                check=health_check,
                meta=service.metadata
            )
            
            if registration_result:
                # Store in local registry as backup
                self.local_registry[service.service_id] = service
                
                logger.info(f"✅ Service registered: {service.service_name} ({service.service_id})")
                logger.info(f"   Region: {service.region}, Zone: {service.zone}")
                logger.info(f"   Address: {service.address}:{service.port}")
                return True
            else:
                logger.error(f"❌ Failed to register service: {service.service_id}")
                return False
                
        except Exception as e:
            logger.error(f"Service registration error: {str(e)}")
            return False
    
    def deregister_service(self, service_id: str) -> bool:
        """
        Service deregistration - Service को Consul से remove करना
        """
        try:
            result = self.consul_client.agent.service.deregister(service_id)
            
            if result:
                # Remove from local registry
                if service_id in self.local_registry:
                    del self.local_registry[service_id]
                
                logger.info(f"✅ Service deregistered: {service_id}")
                return True
            else:
                logger.error(f"❌ Failed to deregister service: {service_id}")
                return False
                
        except Exception as e:
            logger.error(f"Service deregistration error: {str(e)}")
            return False
    
    def discover_services(self, service_name: str, region: Optional[str] = None, 
                         zone: Optional[str] = None, healthy_only: bool = True) -> List[Dict]:
        """
        Service discovery - Ola services को find करना
        Regional और zonal filtering के साथ
        """
        try:
            # Get services from Consul
            services = self.consul_client.health.service(
                service=service_name,
                passing=healthy_only  # Only healthy services
            )[1]
            
            discovered_services = []
            
            for service_data in services:
                service_info = service_data['Service']
                node_info = service_data['Node']
                
                # Regional filtering
                if region and region not in service_info.get('Tags', []):
                    continue
                
                # Zonal filtering
                if zone and zone not in service_info.get('Tags', []):
                    continue
                
                service_details = {
                    'service_id': service_info['ID'],
                    'service_name': service_info['Service'],
                    'address': service_info['Address'] or node_info['Address'],
                    'port': service_info['Port'],
                    'tags': service_info.get('Tags', []),
                    'metadata': service_info.get('Meta', {}),
                    'node_name': node_info['Node'],
                    'datacenter': node_info['Datacenter']
                }
                
                discovered_services.append(service_details)
            
            logger.info(f"🔍 Discovered {len(discovered_services)} services for '{service_name}'")
            if region:
                logger.info(f"   Filtered by region: {region}")
            if zone:
                logger.info(f"   Filtered by zone: {zone}")
            
            return discovered_services
            
        except Exception as e:
            logger.error(f"Service discovery error: {str(e)}")
            return []
    
    def get_service_endpoint(self, service_name: str, region: Optional[str] = None,
                           load_balancing: str = "random") -> Optional[str]:
        """
        Get single service endpoint - Load balancing के साथ
        """
        services = self.discover_services(service_name, region=region)
        
        if not services:
            logger.warning(f"No healthy services found for: {service_name}")
            return None
        
        # Load balancing strategies
        if load_balancing == "random":
            selected_service = random.choice(services)
        elif load_balancing == "round_robin":
            # Simple round-robin (in production, use proper state management)
            selected_service = services[int(time.time()) % len(services)]
        else:
            # Default to first available
            selected_service = services[0]
        
        endpoint = f"http://{selected_service['address']}:{selected_service['port']}"
        
        logger.info(f"🎯 Selected endpoint: {endpoint} ({load_balancing} strategy)")
        return endpoint
    
    def watch_service_changes(self, service_name: str, callback: Callable[[List[Dict]], None]):
        """
        Watch for service changes - Real-time updates के लिए
        """
        def watcher():
            last_index = None
            
            while True:
                try:
                    # Watch for changes using Consul's blocking queries
                    index, services = self.consul_client.health.service(
                        service=service_name,
                        index=last_index,
                        wait="10s"
                    )
                    
                    if last_index != index:
                        last_index = index
                        
                        # Parse service data
                        service_list = []
                        for service_data in services:
                            service_info = service_data['Service']
                            service_list.append({
                                'service_id': service_info['ID'],
                                'address': service_info['Address'],
                                'port': service_info['Port'],
                                'tags': service_info.get('Tags', [])
                            })
                        
                        # Call the callback with updated services
                        callback(service_list)
                        
                        logger.info(f"🔄 Service '{service_name}' updated, {len(service_list)} instances")
                
                except Exception as e:
                    logger.error(f"Service watch error: {str(e)}")
                    time.sleep(5)  # Wait before retrying
        
        # Start watcher in background thread
        watch_thread = threading.Thread(target=watcher, daemon=True)
        watch_thread.start()
        
        logger.info(f"👀 Started watching service: {service_name}")
    
    def start_health_monitoring(self):
        """
        Start health monitoring for registered services
        """
        if self.health_check_running:
            logger.warning("Health monitoring already running")
            return
        
        self.health_check_running = True
        
        def health_monitor():
            while self.health_check_running:
                for service_id, service in self.local_registry.items():
                    try:
                        # Check service health
                        response = requests.get(
                            service.health_check_url,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            logger.debug(f"✅ Health check passed: {service_id}")
                        else:
                            logger.warning(f"⚠️ Health check failed: {service_id} (HTTP {response.status_code})")
                    
                    except Exception as e:
                        logger.error(f"❌ Health check error for {service_id}: {str(e)}")
                
                time.sleep(30)  # Check every 30 seconds
        
        self.health_check_thread = threading.Thread(target=health_monitor, daemon=True)
        self.health_check_thread.start()
        
        logger.info("🏥 Health monitoring started")
    
    def stop_health_monitoring(self):
        """Stop health monitoring"""
        self.health_check_running = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        logger.info("🛑 Health monitoring stopped")
    
    def get_service_catalog(self) -> Dict[str, List[Dict]]:
        """
        Get complete service catalog - सारी services की list
        """
        try:
            catalog = self.consul_client.catalog.services()[1]
            
            service_catalog = {}
            for service_name, tags in catalog.items():
                services = self.discover_services(service_name)
                service_catalog[service_name] = services
            
            logger.info(f"📚 Service catalog contains {len(service_catalog)} services")
            return service_catalog
        
        except Exception as e:
            logger.error(f"Error getting service catalog: {str(e)}")
            return {}

class OlaRideMatchingClient:
    """
    Ola Ride Matching service client using service discovery
    """
    
    def __init__(self, service_discovery: OlaServiceDiscovery):
        self.service_discovery = service_discovery
        self.service_name = "ola-ride-matching"
    
    async def find_nearby_rides(self, lat: float, lng: float, region: str) -> List[Dict]:
        """
        Find nearby rides using service discovery
        """
        try:
            # Discover ride matching service
            endpoint = self.service_discovery.get_service_endpoint(
                self.service_name,
                region=region,
                load_balancing="random"
            )
            
            if not endpoint:
                logger.error("Ride matching service not available!")
                return []
            
            # Make API call to discovered service
            response = requests.post(
                f"{endpoint}/api/v1/rides/find",
                json={
                    "latitude": lat,
                    "longitude": lng,
                    "region": region,
                    "max_distance": 2.0  # 2 km radius
                },
                timeout=10
            )
            
            if response.status_code == 200:
                rides = response.json().get("rides", [])
                logger.info(f"🚗 Found {len(rides)} nearby rides in {region}")
                return rides
            else:
                logger.error(f"Ride matching API error: HTTP {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error finding rides: {str(e)}")
            return []

def main():
    """Demonstration of Ola service discovery implementation"""
    
    # Initialize service discovery
    service_discovery = OlaServiceDiscovery()
    
    # Register Ola services across Indian cities
    services_to_register = [
        # Mumbai Ola services
        OlaService(
            service_id="ola-ride-matching-mumbai-001",
            service_name="ola-ride-matching",
            address="10.0.1.10",
            port=8001,
            tags=["v1.0", "production", "ride-matching"],
            health_check_url="http://10.0.1.10:8001/health",
            metadata={"city": "mumbai", "capacity": "1000"},
            region="mumbai",
            zone="andheri"
        ),
        
        OlaService(
            service_id="ola-ride-matching-mumbai-002", 
            service_name="ola-ride-matching",
            address="10.0.1.11",
            port=8001,
            tags=["v1.0", "production", "ride-matching"],
            health_check_url="http://10.0.1.11:8001/health",
            metadata={"city": "mumbai", "capacity": "800"},
            region="mumbai",
            zone="bandra"
        ),
        
        # Bangalore Ola services
        OlaService(
            service_id="ola-ride-matching-bangalore-001",
            service_name="ola-ride-matching", 
            address="10.0.2.10",
            port=8001,
            tags=["v1.1", "production", "ride-matching"],
            health_check_url="http://10.0.2.10:8001/health",
            metadata={"city": "bangalore", "capacity": "1200"},
            region="bangalore",
            zone="koramangala"
        ),
        
        # Driver tracking services
        OlaService(
            service_id="ola-driver-tracking-mumbai-001",
            service_name="ola-driver-tracking",
            address="10.0.1.20",
            port=8002,
            tags=["v2.0", "production", "tracking"],
            health_check_url="http://10.0.1.20:8002/health",
            metadata={"city": "mumbai", "tracking_frequency": "2s"},
            region="mumbai", 
            zone="worli"
        ),
        
        # Payment services
        OlaService(
            service_id="ola-payment-service-001",
            service_name="ola-payment",
            address="10.0.3.10",
            port=8003,
            tags=["v1.5", "production", "payment"],
            health_check_url="http://10.0.3.10:8003/health",
            metadata={"processor": "paytm", "backup": "razorpay"},
            region="mumbai",
            zone="central"
        )
    ]
    
    # Register all services
    print("🏢 Registering Ola services across India...")
    for service in services_to_register:
        success = service_discovery.register_service(service)
        if success:
            print(f"   ✅ {service.service_name} registered in {service.region}")
        else:
            print(f"   ❌ Failed to register {service.service_name}")
    
    # Start health monitoring
    service_discovery.start_health_monitoring()
    
    # Demonstrate service discovery
    print("\\n🔍 Discovering services...")
    
    # Find all ride matching services
    all_ride_services = service_discovery.discover_services("ola-ride-matching")
    print(f"\\n📍 Found {len(all_ride_services)} ride matching services:")
    for service in all_ride_services:
        print(f"   - {service['service_id']} at {service['address']}:{service['port']}")
    
    # Find Mumbai-specific services
    mumbai_services = service_discovery.discover_services("ola-ride-matching", region="mumbai")
    print(f"\\n🏙️ Mumbai ride matching services: {len(mumbai_services)}")
    for service in mumbai_services:
        print(f"   - {service['service_id']} in zone: {[tag for tag in service['tags'] if tag in ['andheri', 'bandra', 'worli']]}")
    
    # Get load-balanced endpoint
    print("\\n⚖️ Load balancing demonstration:")
    for i in range(5):
        endpoint = service_discovery.get_service_endpoint(
            "ola-ride-matching",
            region="mumbai",
            load_balancing="random"
        )
        print(f"   Attempt {i+1}: {endpoint}")
    
    # Demonstrate service catalog
    print("\\n📚 Complete service catalog:")
    catalog = service_discovery.get_service_catalog()
    for service_name, instances in catalog.items():
        print(f"   - {service_name}: {len(instances)} instances")
    
    # Setup service change watching
    def on_service_change(services):
        print(f"\\n🔄 Service change detected: {len(services)} ride matching instances")
        for service in services:
            print(f"   - {service['service_id']} at {service['address']}:{service['port']}")
    
    service_discovery.watch_service_changes("ola-ride-matching", on_service_change)
    
    # Demonstrate client usage
    print("\\n🚗 Demonstrating Ola ride matching client...")
    client = OlaRideMatchingClient(service_discovery)
    
    # Simulate finding rides (this would make actual API calls in production)
    mumbai_coordinates = (19.0760, 72.8777)  # Mumbai coordinates
    print(f"   Searching for rides near Mumbai coordinates: {mumbai_coordinates}")
    
    # Keep the demo running for a bit
    print("\\n⏰ Service discovery is running. Press Ctrl+C to stop...")
    try:
        time.sleep(30)  # Run for 30 seconds
    except KeyboardInterrupt:
        print("\\n🛑 Stopping service discovery...")
    
    # Cleanup
    print("\\n🧹 Cleaning up services...")
    for service in services_to_register:
        service_discovery.deregister_service(service.service_id)
    
    service_discovery.stop_health_monitoring()
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    main()

# Production deployment commands:
"""
# Start Consul cluster:
consul agent -dev -client=0.0.0.0

# Register Ola service:
python 04_service_discovery_consul.py

# Check service health:
curl http://localhost:8500/v1/health/service/ola-ride-matching

# Query services by region:
curl "http://localhost:8500/v1/health/service/ola-ride-matching?tag=mumbai"

# Consul UI:
http://localhost:8500/ui/

# Service mesh integration:
consul connect proxy -sidecar-for ola-ride-matching-mumbai-001
"""