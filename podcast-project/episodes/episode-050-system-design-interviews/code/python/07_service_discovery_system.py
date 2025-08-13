#!/usr/bin/env python3
"""
Service Discovery System - Episode 50: System Design Interview Mastery
Zomato Restaurant Discovery Service - Mumbai Food Network

Service Discovery जैसे Mumbai के delivery boys को restaurants ढूंढना है -
कौन सा restaurant open है, कहाँ है, कैसे contact करें

Author: Hindi Podcast Series
Topic: Distributed Service Discovery and Registry
"""

import json
import time
import threading
import uuid
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum
import hashlib
import random
import socket

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

@dataclass
class ServiceInstance:
    """Individual service instance - Mumbai restaurant branch"""
    service_id: str
    instance_id: str
    host: str
    port: int
    protocol: str = "http"
    version: str = "1.0.0"
    region: str = "mumbai"
    zone: str = "central"
    metadata: Dict = None
    tags: Set[str] = None
    
    # Health and status
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_heartbeat: float = None
    registration_time: float = None
    
    # Performance metrics
    load_factor: float = 0.0
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = set()
        if self.last_heartbeat is None:
            self.last_heartbeat = time.time()
        if self.registration_time is None:
            self.registration_time = time.time()
    
    def get_endpoint(self) -> str:
        """Get full service endpoint"""
        return f"{self.protocol}://{self.host}:{self.port}"
    
    def is_healthy(self) -> bool:
        """Check if service instance is healthy"""
        if self.status != ServiceStatus.HEALTHY:
            return False
        
        # Check heartbeat timeout (30 seconds)
        return time.time() - self.last_heartbeat < 30
    
    def update_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.last_heartbeat = time.time()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['tags'] = list(self.tags)
        data['status'] = self.status.value
        return data

class LoadBalancingStrategy(Enum):
    """Load balancing strategies for service discovery"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    LOCALITY_AWARE = "locality_aware"

class ServiceRegistry:
    """Service registry - Mumbai restaurant directory"""
    
    def __init__(self, name: str = "MumbaiServiceRegistry"):
        self.name = name
        self.services = defaultdict(list)  # service_name -> [ServiceInstance]
        self.service_watchers = defaultdict(list)  # service_name -> [callback]
        self.lock = threading.RWLock()
        
        # Health checking
        self.health_check_interval = 10  # seconds
        self.health_checker_thread = None
        self.running = True
        
        # Metrics
        self.total_registrations = 0
        self.total_deregistrations = 0
        self.total_discoveries = 0
        
        # Start health checker
        self._start_health_checker()
        
        print(f"🏢 Service Registry '{name}' initialized")
    
    def register_service(self, instance: ServiceInstance) -> bool:
        """Register service instance - Restaurant को directory में add करना"""
        try:
            with self.lock.writer():
                # Check if instance already exists
                existing_instances = self.services[instance.service_id]
                for existing in existing_instances:
                    if existing.instance_id == instance.instance_id:
                        print(f"⚠️ Instance {instance.instance_id} already registered, updating...")
                        existing_instances.remove(existing)
                        break
                
                # Add new instance
                self.services[instance.service_id].append(instance)
                self.total_registrations += 1
                
                print(f"✅ Service registered: {instance.service_id}/{instance.instance_id} "
                      f"at {instance.get_endpoint()}")
                
                # Notify watchers
                self._notify_watchers(instance.service_id, "register", instance)
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to register service {instance.instance_id}: {e}")
            return False
    
    def deregister_service(self, service_id: str, instance_id: str) -> bool:
        """Deregister service instance - Restaurant को directory से remove करना"""
        try:
            with self.lock.writer():
                instances = self.services[service_id]
                for instance in instances:
                    if instance.instance_id == instance_id:
                        instances.remove(instance)
                        self.total_deregistrations += 1
                        
                        print(f"🗑️ Service deregistered: {service_id}/{instance_id}")
                        
                        # Notify watchers
                        self._notify_watchers(service_id, "deregister", instance)
                        
                        # Clean up empty service lists
                        if not instances:
                            del self.services[service_id]
                        
                        return True
                
                print(f"⚠️ Instance {instance_id} not found for service {service_id}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to deregister service {instance_id}: {e}")
            return False
    
    def discover_service(self, service_id: str, 
                        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
                        filters: Dict = None) -> Optional[ServiceInstance]:
        """Discover service instance - Restaurant ढूंढना"""
        
        self.total_discoveries += 1
        
        with self.lock.reader():
            if service_id not in self.services:
                print(f"❌ Service {service_id} not found")
                return None
            
            candidates = self.services[service_id]
            
            # Filter healthy instances
            healthy_instances = [inst for inst in candidates if inst.is_healthy()]
            
            if not healthy_instances:
                print(f"❌ No healthy instances found for service {service_id}")
                return None
            
            # Apply additional filters
            if filters:
                healthy_instances = self._apply_filters(healthy_instances, filters)
                if not healthy_instances:
                    print(f"❌ No instances match filters for service {service_id}")
                    return None
            
            # Apply load balancing strategy
            selected = self._apply_load_balancing(healthy_instances, strategy)
            
            if selected:
                print(f"🎯 Discovered service: {selected.service_id}/{selected.instance_id} "
                      f"at {selected.get_endpoint()}")
            
            return selected
    
    def discover_all_services(self, service_id: str, filters: Dict = None) -> List[ServiceInstance]:
        """Get all healthy instances of a service"""
        with self.lock.reader():
            if service_id not in self.services:
                return []
            
            candidates = self.services[service_id]
            healthy_instances = [inst for inst in candidates if inst.is_healthy()]
            
            if filters:
                healthy_instances = self._apply_filters(healthy_instances, filters)
            
            return healthy_instances
    
    def _apply_filters(self, instances: List[ServiceInstance], filters: Dict) -> List[ServiceInstance]:
        """Apply filters to service instances"""
        filtered = instances
        
        if 'region' in filters:
            filtered = [inst for inst in filtered if inst.region == filters['region']]
        
        if 'zone' in filters:
            filtered = [inst for inst in filtered if inst.zone == filters['zone']]
        
        if 'version' in filters:
            filtered = [inst for inst in filtered if inst.version == filters['version']]
        
        if 'tags' in filters:
            required_tags = set(filters['tags'])
            filtered = [inst for inst in filtered if required_tags.issubset(inst.tags)]
        
        if 'max_load' in filters:
            max_load = filters['max_load']
            filtered = [inst for inst in filtered if inst.load_factor <= max_load]
        
        return filtered
    
    def _apply_load_balancing(self, instances: List[ServiceInstance], 
                            strategy: LoadBalancingStrategy) -> Optional[ServiceInstance]:
        """Apply load balancing strategy"""
        if not instances:
            return None
        
        if strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(instances)
        
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(instances, key=lambda x: x.load_factor)
        
        elif strategy == LoadBalancingStrategy.WEIGHTED_RANDOM:
            # Weight inversely proportional to load
            weights = [1.0 / (inst.load_factor + 0.1) for inst in instances]
            return random.choices(instances, weights=weights)[0]
        
        elif strategy == LoadBalancingStrategy.LOCALITY_AWARE:
            # Prefer local zone, then region
            local_zone = [inst for inst in instances if inst.zone == "central"]
            if local_zone:
                return random.choice(local_zone)
            
            local_region = [inst for inst in instances if inst.region == "mumbai"]
            if local_region:
                return random.choice(local_region)
            
            return random.choice(instances)
        
        else:  # ROUND_ROBIN (default)
            # Simple round-robin based on instance ID hash
            instance_hash = hash(str([inst.instance_id for inst in instances]))
            index = abs(instance_hash) % len(instances)
            return instances[index]
    
    def watch_service(self, service_id: str, callback: Callable):
        """Watch service changes - Restaurant status updates के लिए subscribe"""
        with self.lock.writer():
            self.service_watchers[service_id].append(callback)
            print(f"👁️ Watcher added for service {service_id}")
    
    def _notify_watchers(self, service_id: str, event_type: str, instance: ServiceInstance):
        """Notify service watchers about changes"""
        watchers = self.service_watchers.get(service_id, [])
        for callback in watchers:
            try:
                callback(event_type, instance)
            except Exception as e:
                print(f"❌ Error notifying watcher: {e}")
    
    def update_instance_health(self, service_id: str, instance_id: str, 
                             health_data: Dict) -> bool:
        """Update instance health metrics"""
        with self.lock.writer():
            if service_id in self.services:
                for instance in self.services[service_id]:
                    if instance.instance_id == instance_id:
                        instance.update_heartbeat()
                        instance.load_factor = health_data.get('load_factor', instance.load_factor)
                        instance.response_time_ms = health_data.get('response_time_ms', instance.response_time_ms)
                        instance.error_rate = health_data.get('error_rate', instance.error_rate)
                        
                        if 'status' in health_data:
                            try:
                                instance.status = ServiceStatus(health_data['status'])
                            except ValueError:
                                pass
                        
                        return True
        return False
    
    def _start_health_checker(self):
        """Start background health checker thread"""
        self.health_checker_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_checker_thread.start()
        print("🏥 Health checker started")
    
    def _health_check_loop(self):
        """Background health checking loop"""
        while self.running:
            try:
                self._perform_health_checks()
                time.sleep(self.health_check_interval)
            except Exception as e:
                print(f"❌ Health check error: {e}")
    
    def _perform_health_checks(self):
        """Perform health checks on all instances"""
        with self.lock.writer():
            unhealthy_instances = []
            
            for service_id, instances in self.services.items():
                for instance in instances:
                    # Check heartbeat timeout
                    if not instance.is_healthy():
                        if instance.status == ServiceStatus.HEALTHY:
                            instance.status = ServiceStatus.UNHEALTHY
                            unhealthy_instances.append((service_id, instance))
                            print(f"💔 Instance {service_id}/{instance.instance_id} marked unhealthy")
                            
                            # Notify watchers
                            self._notify_watchers(service_id, "unhealthy", instance)
            
            # Optional: Remove unhealthy instances after timeout
            # In production, you might want to keep them for a grace period
    
    def get_registry_stats(self) -> Dict:
        """Get registry statistics"""
        with self.lock.reader():
            total_instances = sum(len(instances) for instances in self.services.values())
            healthy_instances = sum(len([inst for inst in instances if inst.is_healthy()]) 
                                  for instances in self.services.values())
            
            service_stats = {}
            for service_id, instances in self.services.items():
                healthy_count = len([inst for inst in instances if inst.is_healthy()])
                service_stats[service_id] = {
                    'total_instances': len(instances),
                    'healthy_instances': healthy_count,
                    'average_load': sum(inst.load_factor for inst in instances) / len(instances) if instances else 0,
                    'average_response_time': sum(inst.response_time_ms for inst in instances) / len(instances) if instances else 0
                }
            
            return {
                'registry_name': self.name,
                'total_services': len(self.services),
                'total_instances': total_instances,
                'healthy_instances': healthy_instances,
                'total_registrations': self.total_registrations,
                'total_deregistrations': self.total_deregistrations,
                'total_discoveries': self.total_discoveries,
                'service_details': service_stats
            }
    
    def shutdown(self):
        """Shutdown service registry"""
        print(f"🛑 Shutting down service registry '{self.name}'...")
        self.running = False
        if self.health_checker_thread:
            self.health_checker_thread.join(timeout=5)
        print("✅ Service registry shutdown complete")

def demonstrate_zomato_restaurant_discovery():
    """Zomato Restaurant Service Discovery Demo"""
    print("🍕 Zomato Restaurant Service Discovery Demo")
    print("=" * 60)
    
    # Create service registry
    registry = ServiceRegistry("Zomato_Mumbai_Registry")
    
    # Register Mumbai restaurants as services
    restaurants = [
        ServiceInstance(
            service_id="pizza_service",
            instance_id="dominos_bandra",
            host="dominos-bandra.zomato.in",
            port=8001,
            region="mumbai",
            zone="western",
            version="2.1.0",
            tags={"cuisine:italian", "delivery", "fast_food"},
            metadata={"rating": 4.2, "avg_delivery_time": 25}
        ),
        ServiceInstance(
            service_id="pizza_service", 
            instance_id="pizza_hut_andheri",
            host="pizzahut-andheri.zomato.in",
            port=8002,
            region="mumbai",
            zone="western", 
            version="2.0.0",
            tags={"cuisine:italian", "delivery", "dine_in"},
            metadata={"rating": 4.0, "avg_delivery_time": 30}
        ),
        ServiceInstance(
            service_id="biryani_service",
            instance_id="biryani_by_kilo_dadar",
            host="bbk-dadar.zomato.in",
            port=8003,
            region="mumbai",
            zone="central",
            version="1.5.0",
            tags={"cuisine:indian", "delivery", "premium"},
            metadata={"rating": 4.5, "avg_delivery_time": 35}
        ),
        ServiceInstance(
            service_id="chinese_service",
            instance_id="mainland_china_bkc",
            host="mainland-bkc.zomato.in", 
            port=8004,
            region="mumbai",
            zone="central",
            version="1.8.0",
            tags={"cuisine:chinese", "dine_in", "premium"},
            metadata={"rating": 4.3, "avg_delivery_time": 40}
        ),
    ]
    
    # Register all restaurants
    print("\n🏪 Registering Mumbai restaurants...")
    for restaurant in restaurants:
        registry.register_service(restaurant)
    
    # Set up service watcher
    def restaurant_status_watcher(event_type: str, instance: ServiceInstance):
        print(f"📢 Restaurant Update: {event_type} - {instance.service_id}/{instance.instance_id}")
    
    registry.watch_service("pizza_service", restaurant_status_watcher)
    
    # Simulate customer food discovery requests
    print("\n🔍 Simulating customer food discovery requests...")
    
    discovery_scenarios = [
        {"service": "pizza_service", "strategy": LoadBalancingStrategy.RANDOM, "filters": None},
        {"service": "pizza_service", "strategy": LoadBalancingStrategy.LOCALITY_AWARE, "filters": {"zone": "western"}},
        {"service": "biryani_service", "strategy": LoadBalancingStrategy.LEAST_CONNECTIONS, "filters": None},
        {"service": "chinese_service", "strategy": LoadBalancingStrategy.WEIGHTED_RANDOM, "filters": {"tags": ["dine_in"]}},
    ]
    
    for i, scenario in enumerate(discovery_scenarios):
        print(f"\n🎯 Discovery Request {i+1}: {scenario['service']}")
        
        instance = registry.discover_service(
            scenario['service'],
            strategy=scenario['strategy'],
            filters=scenario['filters']
        )
        
        if instance:
            print(f"   → Selected: {instance.instance_id}")
            print(f"   → Endpoint: {instance.get_endpoint()}")
            print(f"   → Rating: {instance.metadata.get('rating', 'N/A')}")
            print(f"   → Delivery Time: {instance.metadata.get('avg_delivery_time', 'N/A')} mins")
        else:
            print(f"   → No restaurants available")
    
    # Simulate health updates
    print("\n💓 Simulating restaurant health updates...")
    health_updates = [
        ("pizza_service", "dominos_bandra", {"load_factor": 0.7, "response_time_ms": 150}),
        ("pizza_service", "pizza_hut_andheri", {"load_factor": 0.3, "response_time_ms": 120}),
        ("biryani_service", "biryani_by_kilo_dadar", {"load_factor": 0.9, "response_time_ms": 200}),
    ]
    
    for service_id, instance_id, health_data in health_updates:
        success = registry.update_instance_health(service_id, instance_id, health_data)
        if success:
            print(f"✅ Updated health for {instance_id}: Load {health_data.get('load_factor', 0):.1f}")
    
    # Test service discovery with different strategies after health updates
    print("\n🎯 Testing discovery after health updates:")
    
    strategies_to_test = [
        LoadBalancingStrategy.LEAST_CONNECTIONS,
        LoadBalancingStrategy.WEIGHTED_RANDOM,
        LoadBalancingStrategy.LOCALITY_AWARE
    ]
    
    for strategy in strategies_to_test:
        instance = registry.discover_service("pizza_service", strategy=strategy)
        if instance:
            print(f"   {strategy.value}: → {instance.instance_id} (Load: {instance.load_factor:.1f})")
    
    # Show registry statistics
    print("\n📊 Registry Statistics:")
    stats = registry.get_registry_stats()
    print(f"   Total Services: {stats['total_services']}")
    print(f"   Total Instances: {stats['total_instances']}")
    print(f"   Healthy Instances: {stats['healthy_instances']}")
    print(f"   Total Discoveries: {stats['total_discoveries']}")
    
    for service_id, service_stats in stats['service_details'].items():
        print(f"\n   📈 {service_id}:")
        print(f"      Instances: {service_stats['healthy_instances']}/{service_stats['total_instances']}")
        print(f"      Avg Load: {service_stats['average_load']:.2f}")
        print(f"      Avg Response: {service_stats['average_response_time']:.1f}ms")
    
    # Simulate service deregistration (restaurant closing)
    print("\n🏪 Simulating restaurant closure...")
    registry.deregister_service("pizza_service", "dominos_bandra")
    
    # Final discovery test
    print("\n🔍 Final discovery test after restaurant closure:")
    instance = registry.discover_service("pizza_service")
    if instance:
        print(f"   Available pizza service: {instance.instance_id}")
    
    # Cleanup
    time.sleep(1)
    registry.shutdown()

def demonstrate_paytm_service_discovery():
    """Paytm Microservices Service Discovery Demo"""
    print("\n💰 Paytm Microservices Service Discovery Demo")
    print("=" * 60)
    
    registry = ServiceRegistry("Paytm_Service_Registry")
    
    # Register Paytm microservices
    paytm_services = [
        ServiceInstance(
            service_id="payment_service",
            instance_id="payment_mumbai_1",
            host="payment-mumbai-1.paytm.in",
            port=9001,
            region="mumbai",
            zone="central",
            version="3.2.1",
            tags={"finance", "critical", "pci_compliant"},
            metadata={"max_amount": 100000, "supported_methods": ["upi", "wallet", "card"]}
        ),
        ServiceInstance(
            service_id="payment_service",
            instance_id="payment_mumbai_2", 
            host="payment-mumbai-2.paytm.in",
            port=9002,
            region="mumbai",
            zone="western",
            version="3.2.1",
            tags={"finance", "critical", "pci_compliant"},
            metadata={"max_amount": 100000, "supported_methods": ["upi", "wallet"]}
        ),
        ServiceInstance(
            service_id="wallet_service",
            instance_id="wallet_mumbai_1",
            host="wallet-mumbai-1.paytm.in", 
            port=9101,
            region="mumbai",
            zone="central",
            version="2.8.5",
            tags={"finance", "wallet", "balance"},
            metadata={"balance_check_tps": 10000}
        ),
        ServiceInstance(
            service_id="notification_service",
            instance_id="notification_mumbai_1",
            host="notification-mumbai-1.paytm.in",
            port=9201,
            region="mumbai", 
            zone="central",
            version="1.9.2",
            tags={"communication", "sms", "push"},
            metadata={"channels": ["sms", "push", "email"]}
        )
    ]
    
    # Register services
    print("\n🏢 Registering Paytm microservices...")
    for service in paytm_services:
        registry.register_service(service)
    
    # Simulate service discovery for payment flow
    print("\n💳 Simulating payment transaction flow...")
    
    # Step 1: Discover payment service
    payment_service = registry.discover_service(
        "payment_service",
        strategy=LoadBalancingStrategy.LEAST_CONNECTIONS,
        filters={"tags": ["pci_compliant"], "version": "3.2.1"}
    )
    
    if payment_service:
        print(f"🏦 Payment Service: {payment_service.instance_id}")
        print(f"   Methods: {payment_service.metadata.get('supported_methods')}")
    
    # Step 2: Discover wallet service for balance check
    wallet_service = registry.discover_service(
        "wallet_service",
        strategy=LoadBalancingStrategy.LOCALITY_AWARE
    )
    
    if wallet_service:
        print(f"💰 Wallet Service: {wallet_service.instance_id}")
        print(f"   TPS: {wallet_service.metadata.get('balance_check_tps')}")
    
    # Step 3: Discover notification service
    notification_service = registry.discover_service(
        "notification_service",
        filters={"tags": ["sms"]}
    )
    
    if notification_service:
        print(f"📱 Notification Service: {notification_service.instance_id}")
        print(f"   Channels: {notification_service.metadata.get('channels')}")
    
    # Show final stats
    print("\n📊 Paytm Service Registry Stats:")
    stats = registry.get_registry_stats()
    print(json.dumps(stats, indent=2, default=str))
    
    registry.shutdown()

if __name__ == "__main__":
    # Run Zomato restaurant discovery demo
    demonstrate_zomato_restaurant_discovery()
    
    print("\n" + "="*80 + "\n")
    
    # Run Paytm service discovery demo  
    demonstrate_paytm_service_discovery()
    
    print("\n" + "="*80)
    print("✅ Service Discovery System Demo Complete!")
    print("📚 Key Features Demonstrated:")
    print("   • Service registration and deregistration")
    print("   • Multiple load balancing strategies")
    print("   • Advanced filtering capabilities")
    print("   • Health monitoring and heartbeats")
    print("   • Service watchers and notifications")
    print("   • Locality-aware routing")
    print("   • Comprehensive metrics and statistics")
    print("   • Production-ready for Mumbai scale operations")