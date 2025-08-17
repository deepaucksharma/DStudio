#!/usr/bin/env python3
"""
🇮🇳 etcd v3 Service Registry - Kubernetes Native Style
Delhi Metro की तरह centralized coordination system

Features:
- Kubernetes-native service discovery
- Lease-based service registration
- Watch-based real-time updates
- Paytm-style distributed architecture
- Production-ready error handling
- Hindi comments और logging

Author: Agent 5 - Code Developer
Episode: 64 - Service Discovery
Context: Kubernetes-native microservices (Paytm banking style)
"""

import etcd3
import json
import time
import threading
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Callable
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Hindi logging setup - Delhi Metro style
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PaytmServiceRegistry')

@dataclass
class ServiceRegistration:
    """Service registration information - Paytm banking style"""
    service_name: str
    instance_id: str
    host: str
    port: int
    health_endpoint: str
    version: str
    tags: List[str]
    metadata: Dict[str, str]
    region: str = "delhi"
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class PaytmServiceRegistry:
    """
    Paytm-style service registry using etcd v3
    
    Delhi Metro analogy:
    - etcd = Central command control room
    - Services = Metro stations across Delhi
    - Leases = Station operational permits
    - Watches = Real-time status monitoring
    - Key-Value pairs = Station information database
    """
    
    def __init__(self, etcd_host='localhost', etcd_port=2379, lease_ttl=30):
        self.etcd = etcd3.client(host=etcd_host, port=etcd_port)
        self.lease_ttl = lease_ttl
        self.services = {}  # Local service cache
        self.leases = {}    # Service lease tracking
        self.watchers = {}  # Service watchers
        self.running = True
        
        # Test etcd connection
        try:
            self.etcd.status()
            logger.info(f"🚇 Paytm Service Registry initialized")
            logger.info(f"📍 etcd endpoint: {etcd_host}:{etcd_port}")
            logger.info(f"⏰ Lease TTL: {lease_ttl} seconds")
        except Exception as e:
            logger.error(f"💥 etcd connection failed: {str(e)}")
            raise
    
    def register_service(self, service: ServiceRegistration) -> bool:
        """
        Register service with etcd using lease mechanism
        
        Delhi Metro station registration:
        - Create lease for service (operational permit)
        - Store service details in etcd
        - Start lease renewal (station operational status)
        """
        try:
            # Create lease for service
            lease = self.etcd.lease(self.lease_ttl)
            
            # Service key following K8s convention
            service_key = f"/services/{service.service_name}/{service.instance_id}"
            
            # Service data
            service_data = {
                "host": service.host,
                "port": service.port,
                "health_endpoint": service.health_endpoint,
                "version": service.version,
                "tags": service.tags,
                "metadata": service.metadata,
                "region": service.region,
                "created_at": service.created_at,
                "last_updated": time.time()
            }
            
            # Store service with lease
            self.etcd.put(
                service_key,
                json.dumps(service_data),
                lease=lease
            )
            
            # Track lease for renewal
            self.leases[service.instance_id] = lease
            self.services[service.instance_id] = service
            
            # Start lease renewal in background
            self._start_lease_renewal(service.instance_id, lease)
            
            logger.info(f"✅ Service registered: {service.service_name}/{service.instance_id}")
            logger.info(f"🚇 Station {service.service_name} operational in {service.region}")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Registration error: {str(e)}")
            return False
    
    def discover_services(self, service_name: str, 
                         region: Optional[str] = None) -> List[ServiceRegistration]:
        """
        Discover services by name with optional region filtering
        
        Delhi Metro route discovery:
        - Find all stations on a metro line
        - Filter by region (North Delhi, South Delhi, etc.)
        - Return operational stations only
        """
        try:
            service_prefix = f"/services/{service_name}/"
            
            # Get all instances of the service
            services_data = self.etcd.get_prefix(service_prefix)
            discovered_services = []
            
            for value, metadata in services_data:
                try:
                    service_data = json.loads(value.decode('utf-8'))
                    
                    # Extract instance ID from key
                    key = metadata.key.decode('utf-8')
                    instance_id = key.split('/')[-1]
                    
                    # Region filtering
                    if region and service_data.get('region') != region:
                        continue
                    
                    # Create ServiceRegistration object
                    service = ServiceRegistration(
                        service_name=service_name,
                        instance_id=instance_id,
                        host=service_data['host'],
                        port=service_data['port'],
                        health_endpoint=service_data['health_endpoint'],
                        version=service_data['version'],
                        tags=service_data['tags'],
                        metadata=service_data['metadata'],
                        region=service_data['region'],
                        created_at=service_data['created_at']
                    )
                    
                    discovered_services.append(service)
                    
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"⚠️ Invalid service data in etcd: {str(e)}")
                    continue
            
            logger.info(f"🔍 Discovered {len(discovered_services)} instances of {service_name}")
            if region:
                logger.info(f"📍 Filtered by region: {region}")
            
            return discovered_services
            
        except Exception as e:
            logger.error(f"💥 Discovery error: {str(e)}")
            return []
    
    def watch_service(self, service_name: str, 
                     callback: Callable[[str, ServiceRegistration, str], None]):
        """
        Watch for service changes (add/update/delete)
        
        Delhi Metro real-time monitoring:
        - Watch station status changes
        - Get notified when stations go online/offline
        - Real-time service mesh updates
        
        Args:
            service_name: Service to watch
            callback: Function called on changes (action, service, event_type)
        """
        def watch_callback(event):
            try:
                event_type = "unknown"
                if event.type == etcd3.events.PutEvent:
                    event_type = "PUT"
                elif event.type == etcd3.events.DeleteEvent:
                    event_type = "DELETE"
                
                # Extract service info from event
                key = event.key.decode('utf-8')
                if not key.startswith(f"/services/{service_name}/"):
                    return
                
                instance_id = key.split('/')[-1]
                
                if event.type == etcd3.events.PutEvent and event.value:
                    try:
                        service_data = json.loads(event.value.decode('utf-8'))
                        service = ServiceRegistration(
                            service_name=service_name,
                            instance_id=instance_id,
                            host=service_data['host'],
                            port=service_data['port'],
                            health_endpoint=service_data['health_endpoint'],
                            version=service_data['version'],
                            tags=service_data['tags'],
                            metadata=service_data['metadata'],
                            region=service_data['region'],
                            created_at=service_data['created_at']
                        )
                        
                        logger.info(f"🔄 Service {event_type}: {service_name}/{instance_id}")
                        callback(service_name, service, event_type)
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"⚠️ Invalid service data in watch: {str(e)}")
                
                elif event.type == etcd3.events.DeleteEvent:
                    logger.info(f"🗑️ Service deleted: {service_name}/{instance_id}")
                    callback(service_name, None, event_type)
                
            except Exception as e:
                logger.error(f"💥 Watch callback error: {str(e)}")
        
        try:
            service_prefix = f"/services/{service_name}/"
            watch_id = self.etcd.add_watch_prefix_callback(service_prefix, watch_callback)
            self.watchers[service_name] = watch_id
            
            logger.info(f"👁️ Watching service: {service_name}")
            return watch_id
            
        except Exception as e:
            logger.error(f"💥 Watch setup error: {str(e)}")
            return None
    
    def _start_lease_renewal(self, instance_id: str, lease):
        """
        Start lease renewal in background thread
        
        Delhi Metro operational permit renewal:
        - Automatic permit renewal
        - Failure detection and cleanup
        - Graceful degradation
        """
        def renew_lease():
            while self.running and instance_id in self.leases:
                try:
                    # Renew lease (TTL/3 interval for safety)
                    time.sleep(self.lease_ttl // 3)
                    
                    if instance_id in self.leases:
                        lease.refresh()
                        service = self.services.get(instance_id)
                        if service:
                            logger.debug(f"🔄 Lease renewed: {service.service_name}/{instance_id}")
                    
                except Exception as e:
                    logger.error(f"💥 Lease renewal failed for {instance_id}: {str(e)}")
                    # Remove failed service
                    self._cleanup_service(instance_id)
                    break
        
        # Start renewal thread
        renewal_thread = threading.Thread(target=renew_lease)
        renewal_thread.daemon = True
        renewal_thread.start()
    
    def _cleanup_service(self, instance_id: str):
        """Clean up failed service"""
        if instance_id in self.services:
            service = self.services[instance_id]
            logger.warning(f"🧹 Cleaning up failed service: {service.service_name}/{instance_id}")
            
            # Remove from local cache
            del self.services[instance_id]
            
            # Revoke lease
            if instance_id in self.leases:
                try:
                    self.leases[instance_id].revoke()
                except:
                    pass
                del self.leases[instance_id]
    
    def deregister_service(self, instance_id: str) -> bool:
        """
        Gracefully deregister a service
        
        Delhi Metro station shutdown:
        - Revoke operational permit
        - Remove from service directory
        - Notify watchers
        """
        try:
            if instance_id not in self.services:
                logger.warning(f"⚠️ Service not found: {instance_id}")
                return False
            
            service = self.services[instance_id]
            service_key = f"/services/{service.service_name}/{instance_id}"
            
            # Delete from etcd
            self.etcd.delete(service_key)
            
            # Revoke lease
            if instance_id in self.leases:
                self.leases[instance_id].revoke()
                del self.leases[instance_id]
            
            # Remove from local cache
            del self.services[instance_id]
            
            logger.info(f"✅ Service deregistered: {service.service_name}/{instance_id}")
            logger.info(f"🚇 Station {service.service_name} shutdown in {service.region}")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Deregistration error: {str(e)}")
            return False
    
    def get_service_catalog(self) -> Dict[str, List[ServiceRegistration]]:
        """
        Get complete service catalog
        
        Delhi Metro complete network:
        - All operational metro lines
        - Station details and status
        - Regional distribution
        """
        try:
            all_services = self.etcd.get_prefix("/services/")
            catalog = {}
            
            for value, metadata in all_services:
                try:
                    key = metadata.key.decode('utf-8')
                    key_parts = key.split('/')
                    
                    if len(key_parts) < 4:
                        continue
                    
                    service_name = key_parts[2]
                    instance_id = key_parts[3]
                    
                    service_data = json.loads(value.decode('utf-8'))
                    
                    service = ServiceRegistration(
                        service_name=service_name,
                        instance_id=instance_id,
                        host=service_data['host'],
                        port=service_data['port'],
                        health_endpoint=service_data['health_endpoint'],
                        version=service_data['version'],
                        tags=service_data['tags'],
                        metadata=service_data['metadata'],
                        region=service_data['region'],
                        created_at=service_data['created_at']
                    )
                    
                    if service_name not in catalog:
                        catalog[service_name] = []
                    catalog[service_name].append(service)
                    
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    logger.warning(f"⚠️ Invalid service data: {str(e)}")
                    continue
            
            logger.info(f"📋 Service catalog: {len(catalog)} services available")
            return catalog
            
        except Exception as e:
            logger.error(f"💥 Catalog error: {str(e)}")
            return {}
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Deregister all local services
        for instance_id in list(self.services.keys()):
            self.deregister_service(instance_id)
        
        # Cancel all watchers
        for service_name, watch_id in self.watchers.items():
            try:
                self.etcd.cancel_watch(watch_id)
            except:
                pass
        
        logger.info("🛑 Paytm Service Registry shutdown complete")

# Usage Example
if __name__ == "__main__":
    # Initialize Paytm service registry
    registry = PaytmServiceRegistry()
    
    # Define watch callback
    def service_change_handler(service_name, service, event_type):
        if event_type == "PUT":
            if service:
                print(f"🔄 Service updated: {service.service_name} in {service.region}")
        elif event_type == "DELETE":
            print(f"🗑️ Service removed: {service_name}")
    
    # Register services (Paytm banking microservices)
    services = [
        ServiceRegistration(
            service_name="user-authentication",
            instance_id="auth-delhi-01",
            host="10.1.1.10",
            port=8080,
            health_endpoint="http://10.1.1.10:8080/health",
            version="3.2.1",
            tags=["auth", "security", "critical"],
            metadata={"datacenter": "delhi-central", "cluster": "primary"},
            region="delhi"
        ),
        ServiceRegistration(
            service_name="payment-processor",
            instance_id="payment-mumbai-01",
            host="10.1.2.20",
            port=8081,
            health_endpoint="http://10.1.2.20:8081/health",
            version="4.1.0",
            tags=["payment", "upi", "core"],
            metadata={"datacenter": "mumbai-bkc", "cluster": "primary"},
            region="mumbai"
        ),
        ServiceRegistration(
            service_name="wallet-service",
            instance_id="wallet-bangalore-01",
            host="10.1.3.30",
            port=8082,
            health_endpoint="http://10.1.3.30:8082/health",
            version="2.8.5",
            tags=["wallet", "balance", "core"],
            metadata={"datacenter": "bangalore-electronic-city", "cluster": "secondary"},
            region="bangalore"
        )
    ]
    
    # Register all services
    for service in services:
        registry.register_service(service)
    
    # Setup watchers
    registry.watch_service("user-authentication", service_change_handler)
    registry.watch_service("payment-processor", service_change_handler)
    
    print("\n🚇 Paytm Service Registry Demo")
    print("=" * 50)
    
    # Service discovery examples
    print("\n1. 🔍 Discovering authentication services:")
    auth_services = registry.discover_services("user-authentication")
    for service in auth_services:
        print(f"   🔐 {service.service_name} @ {service.host}:{service.port} [{service.region}] v{service.version}")
    
    print("\n2. 🌍 Region-specific discovery:")
    mumbai_services = registry.discover_services("payment-processor", region="mumbai")
    for service in mumbai_services:
        print(f"   💳 {service.service_name} in {service.region} - v{service.version}")
    
    print("\n3. 📋 Complete service catalog:")
    catalog = registry.get_service_catalog()
    for service_name, instances in catalog.items():
        print(f"   🏪 {service_name}: {len(instances)} instances")
        for instance in instances:
            print(f"      📍 {instance.region} - {instance.host}:{instance.port} (v{instance.version})")
    
    # Keep running for demo
    try:
        print("\n⏰ Registry running... (Ctrl+C to stop)")
        print("👁️ Watching for service changes...")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        registry.shutdown()