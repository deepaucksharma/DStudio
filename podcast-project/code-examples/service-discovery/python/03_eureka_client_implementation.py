#!/usr/bin/env python3
"""
🇮🇳 Netflix Eureka Client Implementation - OLA/Uber Style
Bangalore traffic management की तरह dynamic service discovery

Features:
- Netflix Eureka client implementation
- Service registration with heartbeats
- Instance metadata and health checks
- Ola/Uber ride-sharing context
- Zone-aware service discovery
- Production-ready error handling
- Hindi comments और logging

Author: Agent 5 - Code Developer
Episode: 64 - Service Discovery
Context: OLA-style microservices (ride-sharing platform)
"""

import requests
import json
import time
import threading
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import logging
import socket
import uuid
from datetime import datetime, timedelta

# Hindi logging setup - Bangalore traffic style
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OlaEurekaClient')

@dataclass
class EurekaInstance:
    """Eureka service instance - OLA cab style"""
    app_name: str
    instance_id: str
    host_name: str
    ip_addr: str
    port: int
    secure_port: int = 443
    home_page_url: str = ""
    status_page_url: str = ""
    health_check_url: str = ""
    vip_address: str = ""
    secure_vip_address: str = ""
    is_coord_disc_server: bool = False
    last_updated_timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    last_dirty_timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    action_type: str = "ADDED"
    overridden_status: str = "UNKNOWN"
    status: str = "UP"
    lease_info: Dict = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)
    datacenter_info: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.instance_id:
            self.instance_id = f"{self.host_name}:{self.app_name}:{self.port}"
        
        if not self.home_page_url:
            self.home_page_url = f"http://{self.ip_addr}:{self.port}/"
        
        if not self.status_page_url:
            self.status_page_url = f"http://{self.ip_addr}:{self.port}/info"
        
        if not self.health_check_url:
            self.health_check_url = f"http://{self.ip_addr}:{self.port}/health"
        
        if not self.vip_address:
            self.vip_address = self.app_name.lower()
        
        if not self.lease_info:
            self.lease_info = {
                "renewalIntervalInSecs": 30,
                "durationInSecs": 90,
                "registrationTimestamp": int(time.time() * 1000),
                "lastRenewalTimestamp": int(time.time() * 1000),
                "evictionTimestamp": 0,
                "serviceUpTimestamp": int(time.time() * 1000)
            }

class OlaEurekaClient:
    """
    OLA-style Eureka client for service discovery
    
    Bangalore traffic analogy:
    - Eureka Server = Traffic control center
    - Services = OLA cabs in different zones
    - Registration = Cab driver check-in
    - Heartbeat = Regular location updates
    - Discovery = Finding nearest available cab
    """
    
    def __init__(self, eureka_url: str = "http://localhost:8761/eureka",
                 zone: str = "bangalore", region: str = "south-india"):
        self.eureka_url = eureka_url.rstrip('/')
        self.zone = zone
        self.region = region
        self.registered_instances: Dict[str, EurekaInstance] = {}
        self.service_cache: Dict[str, List[EurekaInstance]] = {}
        self.cache_last_updated = 0
        self.cache_ttl = 30  # seconds
        self.heartbeat_threads: Dict[str, threading.Thread] = {}
        self.running = True
        
        logger.info(f"🚗 OLA Eureka Client initialized")
        logger.info(f"📍 Eureka server: {eureka_url}")
        logger.info(f"🌐 Zone: {zone}, Region: {region}")
    
    def register_instance(self, instance: EurekaInstance) -> bool:
        """
        Register service instance with Eureka
        
        OLA cab registration:
        - Driver checks in with dispatch
        - Provides location and availability
        - Sets up regular heartbeat updates
        """
        try:
            # Add zone and region metadata
            instance.metadata.update({
                "zone": self.zone,
                "region": self.region,
                "management.port": str(instance.port)
            })
            
            # Create registration payload
            registration_data = {
                "instance": {
                    "instanceId": instance.instance_id,
                    "app": instance.app_name.upper(),
                    "appName": instance.app_name.upper(),
                    "ipAddr": instance.ip_addr,
                    "port": {"$": instance.port, "@enabled": "true"},
                    "securePort": {"$": instance.secure_port, "@enabled": "false"},
                    "homePageUrl": instance.home_page_url,
                    "statusPageUrl": instance.status_page_url,
                    "healthCheckUrl": instance.health_check_url,
                    "vipAddress": instance.vip_address,
                    "secureVipAddress": instance.secure_vip_address,
                    "isCoordinatingDiscoveryServer": instance.is_coord_disc_server,
                    "lastUpdatedTimestamp": instance.last_updated_timestamp,
                    "lastDirtyTimestamp": instance.last_dirty_timestamp,
                    "actionType": instance.action_type,
                    "overriddenStatus": instance.overridden_status,
                    "status": instance.status,
                    "leaseInfo": instance.lease_info,
                    "metadata": instance.metadata,
                    "dataCenterInfo": {
                        "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                        "name": "MyOwn"
                    }
                }
            }
            
            # Register with Eureka
            url = f"{self.eureka_url}/apps/{instance.app_name.upper()}"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(url, json=registration_data, headers=headers)
            
            if response.status_code in [200, 204]:
                self.registered_instances[instance.instance_id] = instance
                
                # Start heartbeat
                self._start_heartbeat(instance)
                
                logger.info(f"✅ Instance registered: {instance.instance_id}")
                logger.info(f"🚗 OLA cab {instance.app_name} online in {self.zone}")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Registration error: {str(e)}")
            return False
    
    def _start_heartbeat(self, instance: EurekaInstance):
        """
        Start heartbeat thread for instance
        
        OLA cab heartbeat:
        - Regular location updates
        - Driver availability status
        - Health check responses
        """
        def send_heartbeat():
            while self.running and instance.instance_id in self.registered_instances:
                try:
                    url = f"{self.eureka_url}/apps/{instance.app_name.upper()}/{instance.instance_id}"
                    headers = {"Accept": "application/json"}
                    
                    response = requests.put(url, headers=headers)
                    
                    if response.status_code == 200:
                        # Update lease renewal timestamp
                        instance.lease_info["lastRenewalTimestamp"] = int(time.time() * 1000)
                        logger.debug(f"💓 Heartbeat sent: {instance.instance_id}")
                    else:
                        logger.warning(f"💛 Heartbeat failed: {instance.instance_id} - {response.status_code}")
                    
                    # Sleep for renewal interval
                    time.sleep(instance.lease_info["renewalIntervalInSecs"])
                    
                except Exception as e:
                    logger.error(f"💥 Heartbeat error for {instance.instance_id}: {str(e)}")
                    time.sleep(30)  # Retry after 30 seconds
        
        # Start heartbeat thread
        thread = threading.Thread(target=send_heartbeat)
        thread.daemon = True
        thread.start()
        self.heartbeat_threads[instance.instance_id] = thread
        
        logger.info(f"💓 Heartbeat started for {instance.instance_id}")
    
    def discover_services(self, app_name: str, 
                         use_cache: bool = True) -> List[EurekaInstance]:
        """
        Discover service instances by application name
        
        OLA cab discovery:
        - Find available cabs in area
        - Filter by service type (auto, cab, bike)
        - Return nearest available options
        """
        app_name_upper = app_name.upper()
        
        # Check cache first
        if use_cache and app_name_upper in self.service_cache:
            cache_age = time.time() - self.cache_last_updated
            if cache_age < self.cache_ttl:
                logger.debug(f"📋 Using cached data for {app_name}")
                return self.service_cache[app_name_upper]
        
        try:
            url = f"{self.eureka_url}/apps/{app_name_upper}"
            headers = {"Accept": "application/json"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                instances = []
                
                if "application" in data and "instance" in data["application"]:
                    instance_data = data["application"]["instance"]
                    
                    # Handle single instance vs list
                    if isinstance(instance_data, dict):
                        instance_data = [instance_data]
                    
                    for inst_data in instance_data:
                        # Only include UP instances
                        if inst_data.get("status") == "UP":
                            instance = self._parse_eureka_instance(inst_data, app_name)
                            instances.append(instance)
                
                # Update cache
                self.service_cache[app_name_upper] = instances
                self.cache_last_updated = time.time()
                
                logger.info(f"🔍 Discovered {len(instances)} instances of {app_name}")
                return instances
            
            elif response.status_code == 404:
                logger.info(f"📭 No instances found for {app_name}")
                return []
            else:
                logger.error(f"❌ Discovery failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"💥 Discovery error: {str(e)}")
            return []
    
    def _parse_eureka_instance(self, inst_data: Dict, app_name: str) -> EurekaInstance:
        """Parse Eureka instance data into EurekaInstance object"""
        port = inst_data.get("port", {})
        if isinstance(port, dict):
            port_value = port.get("$", 8080)
        else:
            port_value = port
        
        secure_port = inst_data.get("securePort", {})
        if isinstance(secure_port, dict):
            secure_port_value = secure_port.get("$", 443)
        else:
            secure_port_value = secure_port
        
        return EurekaInstance(
            app_name=app_name,
            instance_id=inst_data.get("instanceId", ""),
            host_name=inst_data.get("hostName", ""),
            ip_addr=inst_data.get("ipAddr", ""),
            port=int(port_value),
            secure_port=int(secure_port_value),
            home_page_url=inst_data.get("homePageUrl", ""),
            status_page_url=inst_data.get("statusPageUrl", ""),
            health_check_url=inst_data.get("healthCheckUrl", ""),
            vip_address=inst_data.get("vipAddress", ""),
            status=inst_data.get("status", "UP"),
            lease_info=inst_data.get("leaseInfo", {}),
            metadata=inst_data.get("metadata", {}),
            datacenter_info=inst_data.get("dataCenterInfo", {})
        )
    
    def get_service_instance(self, app_name: str, 
                           preferred_zone: Optional[str] = None) -> Optional[EurekaInstance]:
        """
        Get a single service instance with zone preference
        
        OLA cab selection:
        - Prefer cabs in same zone (area)
        - Fallback to any available cab
        - Load balance across available options
        """
        instances = self.discover_services(app_name)
        
        if not instances:
            logger.warning(f"⚠️ No instances found for {app_name}")
            return None
        
        # Zone-aware selection
        preferred_instances = []
        if preferred_zone:
            for instance in instances:
                instance_zone = instance.metadata.get("zone", "")
                if instance_zone == preferred_zone:
                    preferred_instances.append(instance)
        
        # Use preferred zone instances if available, otherwise all instances
        candidates = preferred_instances if preferred_instances else instances
        
        # Simple round-robin using current time
        index = int(time.time()) % len(candidates)
        selected = candidates[index]
        
        zone_info = selected.metadata.get("zone", "unknown")
        logger.info(f"🎯 Selected instance: {selected.instance_id}")
        logger.info(f"🚗 OLA cab {selected.app_name} from {zone_info} zone")
        
        return selected
    
    def get_all_applications(self) -> Dict[str, List[EurekaInstance]]:
        """
        Get all registered applications
        
        OLA complete fleet:
        - All service types
        - All zones and regions
        - Current availability status
        """
        try:
            url = f"{self.eureka_url}/apps"
            headers = {"Accept": "application/json"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                applications = {}
                
                if "applications" in data and "application" in data["applications"]:
                    apps_data = data["applications"]["application"]
                    
                    # Handle single application vs list
                    if isinstance(apps_data, dict):
                        apps_data = [apps_data]
                    
                    for app_data in apps_data:
                        app_name = app_data.get("name", "").lower()
                        instances = []
                        
                        if "instance" in app_data:
                            instance_data = app_data["instance"]
                            
                            # Handle single instance vs list
                            if isinstance(instance_data, dict):
                                instance_data = [instance_data]
                            
                            for inst_data in instance_data:
                                if inst_data.get("status") == "UP":
                                    instance = self._parse_eureka_instance(inst_data, app_name)
                                    instances.append(instance)
                        
                        if instances:
                            applications[app_name] = instances
                
                logger.info(f"📋 Found {len(applications)} applications")
                return applications
            else:
                logger.error(f"❌ Failed to get applications: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"💥 Get applications error: {str(e)}")
            return {}
    
    def deregister_instance(self, instance_id: str) -> bool:
        """
        Deregister instance from Eureka
        
        OLA cab sign-off:
        - Driver going offline
        - Remove from available cabs
        - Stop heartbeat updates
        """
        try:
            if instance_id not in self.registered_instances:
                logger.warning(f"⚠️ Instance not found: {instance_id}")
                return False
            
            instance = self.registered_instances[instance_id]
            
            url = f"{self.eureka_url}/apps/{instance.app_name.upper()}/{instance_id}"
            headers = {"Accept": "application/json"}
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code in [200, 204]:
                # Stop heartbeat thread
                if instance_id in self.heartbeat_threads:
                    # Thread will stop automatically due to instance removal
                    del self.heartbeat_threads[instance_id]
                
                del self.registered_instances[instance_id]
                
                logger.info(f"✅ Instance deregistered: {instance_id}")
                logger.info(f"🚗 OLA cab {instance.app_name} signed off from {self.zone}")
                return True
            else:
                logger.error(f"❌ Deregistration failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Deregistration error: {str(e)}")
            return False
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Deregister all instances
        for instance_id in list(self.registered_instances.keys()):
            self.deregister_instance(instance_id)
        
        logger.info("🛑 OLA Eureka Client shutdown complete")

# Usage Example
if __name__ == "__main__":
    # Initialize OLA Eureka client
    client = OlaEurekaClient(
        eureka_url="http://localhost:8761/eureka",
        zone="bangalore-south",
        region="south-india"
    )
    
    # Create service instances (OLA microservices)
    instances = [
        EurekaInstance(
            app_name="driver-service",
            instance_id="driver-bangalore-01",
            host_name="driver-service-01",
            ip_addr="10.2.1.10",
            port=8080,
            metadata={
                "service_type": "core",
                "version": "2.1.0",
                "zone": "bangalore-south"
            }
        ),
        EurekaInstance(
            app_name="ride-matching",
            instance_id="matching-bangalore-01", 
            host_name="ride-matching-01",
            ip_addr="10.2.1.20",
            port=8081,
            metadata={
                "service_type": "core",
                "version": "3.0.1",
                "zone": "bangalore-south"
            }
        ),
        EurekaInstance(
            app_name="payment-service",
            instance_id="payment-bangalore-01",
            host_name="payment-service-01", 
            ip_addr="10.2.1.30",
            port=8082,
            metadata={
                "service_type": "critical",
                "version": "1.8.5",
                "zone": "bangalore-south"
            }
        )
    ]
    
    # Register all instances
    for instance in instances:
        client.register_instance(instance)
    
    print("\n🚗 OLA Eureka Client Demo")
    print("=" * 50)
    
    # Service discovery examples
    print("\n1. 🔍 Discovering driver services:")
    driver_services = client.discover_services("driver-service")
    for service in driver_services:
        zone = service.metadata.get("zone", "unknown")
        print(f"   🚗 {service.instance_id} @ {service.ip_addr}:{service.port} [{zone}]")
    
    print("\n2. 🎯 Getting specific service instance:")
    matching_instance = client.get_service_instance("ride-matching", preferred_zone="bangalore-south")
    if matching_instance:
        print(f"   🎯 Using {matching_instance.instance_id} in {matching_instance.metadata.get('zone')}")
    
    print("\n3. 📋 All registered applications:")
    applications = client.get_all_applications()
    for app_name, instances in applications.items():
        print(f"   🏪 {app_name}: {len(instances)} instances")
        for instance in instances:
            zone = instance.metadata.get("zone", "unknown")
            print(f"      📍 {zone} - {instance.ip_addr}:{instance.port}")
    
    # Keep running for demo
    try:
        print("\n⏰ Services running... (Ctrl+C to stop)")
        print("💓 Sending heartbeats...")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        client.shutdown()