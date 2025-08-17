#!/usr/bin/env python3
"""
Service Discovery Integration Tests
सर्विस डिस्कवरी इंटीग्रेशन टेस्ट्स

Testing service discovery patterns with Indian microservices scenarios.
Focus on Consul, etcd, Kubernetes service discovery with realistic load.
"""

import asyncio
import pytest
import time
import json
import random
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
import socket

# Import test fixtures
from tests.conftest import (
    indian_test_data, performance_monitor, festival_traffic_simulator,
    chaos_simulator, indian_user_session, mock_http_client
)

class MockConsulClient:
    """Mock Consul client for testing"""
    
    def __init__(self):
        self.services = {}
        self.health_checks = {}
        self.kv_store = {}
        self.sessions = {}
        self.events = []
        
    def register_service(self, service_id, service_name, address, port, 
                        tags=None, check=None):
        """Register a service with Consul"""
        service = {
            "id": service_id,
            "name": service_name,
            "address": address,
            "port": port,
            "tags": tags or [],
            "check": check,
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self.services[service_id] = service
        
        if check:
            self.health_checks[service_id] = {
                "status": "passing",
                "last_check": datetime.utcnow().isoformat()
            }
            
        return {"status": "registered", "service_id": service_id}
        
    def deregister_service(self, service_id):
        """Deregister a service"""
        service = self.services.pop(service_id, None)
        self.health_checks.pop(service_id, None)
        return {"status": "deregistered", "found": service is not None}
        
    def discover_services(self, service_name, healthy_only=True):
        """Discover services by name"""
        matching_services = []
        
        for service_id, service in self.services.items():
            if service["name"] == service_name:
                if healthy_only:
                    health = self.health_checks.get(service_id, {})
                    if health.get("status") == "passing":
                        matching_services.append(service)
                else:
                    matching_services.append(service)
                    
        return matching_services
        
    def get_service_health(self, service_id):
        """Get service health status"""
        return self.health_checks.get(service_id, {"status": "unknown"})
        
    def update_health_check(self, service_id, status="passing"):
        """Update service health check"""
        if service_id in self.health_checks:
            self.health_checks[service_id]["status"] = status
            self.health_checks[service_id]["last_check"] = datetime.utcnow().isoformat()
            return True
        return False
        
    def put_kv(self, key, value):
        """Put key-value pair"""
        self.kv_store[key] = {
            "value": value,
            "create_index": len(self.kv_store) + 1,
            "modify_index": len(self.kv_store) + 1,
            "timestamp": datetime.utcnow().isoformat()
        }
        return True
        
    def get_kv(self, key):
        """Get key-value pair"""
        return self.kv_store.get(key)

class MockEtcdClient:
    """Mock etcd client for testing"""
    
    def __init__(self):
        self.data = {}
        self.watchers = {}
        self.leases = {}
        
    def put(self, key, value, lease=None):
        """Put key-value with optional lease"""
        self.data[key] = {
            "value": value,
            "revision": len(self.data) + 1,
            "created_revision": len(self.data) + 1,
            "lease": lease,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Notify watchers
        self._notify_watchers(key, "PUT", value)
        return True
        
    def get(self, key):
        """Get value by key"""
        return self.data.get(key)
        
    def delete(self, key):
        """Delete key"""
        deleted = self.data.pop(key, None)
        if deleted:
            self._notify_watchers(key, "DELETE", None)
        return deleted is not None
        
    def watch(self, key, callback):
        """Watch key for changes"""
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
        
    def _notify_watchers(self, key, event_type, value):
        """Notify watchers of changes"""
        for watcher_key in self.watchers:
            if key.startswith(watcher_key):
                for callback in self.watchers[watcher_key]:
                    callback(key, event_type, value)
                    
    def grant_lease(self, ttl):
        """Grant a lease with TTL"""
        lease_id = f"lease_{len(self.leases) + 1}"
        self.leases[lease_id] = {
            "ttl": ttl,
            "granted_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
        }
        return lease_id
        
    def revoke_lease(self, lease_id):
        """Revoke a lease"""
        return self.leases.pop(lease_id, None) is not None

class ServiceDiscoveryManager:
    """Service discovery management system"""
    
    def __init__(self, backend="consul", consul_client=None, etcd_client=None):
        self.backend = backend
        self.consul_client = consul_client or MockConsulClient()
        self.etcd_client = etcd_client or MockEtcdClient()
        self.local_cache = {}
        self.cache_ttl = 30  # seconds
        self.health_check_interval = 10  # seconds
        self.metrics = {
            "services_registered": 0,
            "services_discovered": 0,
            "health_checks_performed": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
    async def register_service(self, service_id, service_name, host, port, 
                              tags=None, health_check_url=None):
        """Register a service with the discovery backend"""
        
        if self.backend == "consul":
            check = None
            if health_check_url:
                check = {
                    "http": health_check_url,
                    "interval": "10s",
                    "timeout": "3s"
                }
                
            result = self.consul_client.register_service(
                service_id, service_name, host, port, tags, check
            )
            
        elif self.backend == "etcd":
            service_data = {
                "id": service_id,
                "name": service_name,
                "host": host,
                "port": port,
                "tags": tags or [],
                "health_check_url": health_check_url,
                "registered_at": datetime.utcnow().isoformat()
            }
            
            key = f"/services/{service_name}/{service_id}"
            result = self.etcd_client.put(key, json.dumps(service_data))
            
        self.metrics["services_registered"] += 1
        return result
        
    async def discover_services(self, service_name, use_cache=True):
        """Discover services by name"""
        cache_key = f"services:{service_name}"
        
        # Check cache first
        if use_cache and cache_key in self.local_cache:
            cache_entry = self.local_cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                self.metrics["cache_hits"] += 1
                return cache_entry["services"]
                
        self.metrics["cache_misses"] += 1
        
        if self.backend == "consul":
            services = self.consul_client.discover_services(service_name)
            
        elif self.backend == "etcd":
            services = []
            # In etcd, we'd scan the /services/{service_name}/ prefix
            for key, data in self.etcd_client.data.items():
                if key.startswith(f"/services/{service_name}/"):
                    service_data = json.loads(data["value"])
                    services.append(service_data)
                    
        # Update cache
        if use_cache:
            self.local_cache[cache_key] = {
                "services": services,
                "timestamp": time.time()
            }
            
        self.metrics["services_discovered"] += 1
        return services
        
    async def get_service_instance(self, service_name, load_balancing="round_robin"):
        """Get a single service instance using load balancing"""
        services = await self.discover_services(service_name)
        
        if not services:
            return None
            
        if load_balancing == "round_robin":
            # Simple round robin (in real implementation, maintain counter)
            return services[random.randint(0, len(services) - 1)]
            
        elif load_balancing == "random":
            return random.choice(services)
            
        elif load_balancing == "least_connections":
            # Mock least connections - return first service
            return services[0]
            
        return services[0]
        
    async def health_check_service(self, service_id):
        """Perform health check on a service"""
        if self.backend == "consul":
            health = self.consul_client.get_service_health(service_id)
            
        elif self.backend == "etcd":
            # Mock health check for etcd
            health = {"status": "passing"}
            
        self.metrics["health_checks_performed"] += 1
        return health
        
    async def deregister_service(self, service_id):
        """Deregister a service"""
        if self.backend == "consul":
            result = self.consul_client.deregister_service(service_id)
            
        elif self.backend == "etcd":
            # Find and delete service from etcd
            result = {"status": "deregistered", "found": False}
            for key in list(self.etcd_client.data.keys()):
                if service_id in key:
                    self.etcd_client.delete(key)
                    result["found"] = True
                    break
                    
        return result
        
    def get_metrics(self):
        """Get discovery metrics"""
        return self.metrics.copy()
        
    def clear_cache(self):
        """Clear the local cache"""
        self.local_cache.clear()

class LoadBalancer:
    """Simple load balancer for discovered services"""
    
    def __init__(self, service_discovery):
        self.service_discovery = service_discovery
        self.round_robin_counters = {}
        self.connection_counts = {}
        
    async def get_backend(self, service_name, algorithm="round_robin"):
        """Get backend service using specified algorithm"""
        services = await self.service_discovery.discover_services(service_name)
        
        if not services:
            return None
            
        if algorithm == "round_robin":
            counter = self.round_robin_counters.get(service_name, 0)
            selected = services[counter % len(services)]
            self.round_robin_counters[service_name] = counter + 1
            return selected
            
        elif algorithm == "random":
            return random.choice(services)
            
        elif algorithm == "least_connections":
            # Find service with least connections
            min_connections = float('inf')
            selected = None
            
            for service in services:
                service_key = f"{service['address']}:{service['port']}"
                connections = self.connection_counts.get(service_key, 0)
                if connections < min_connections:
                    min_connections = connections
                    selected = service
                    
            return selected
            
        return services[0]
        
    def track_connection(self, service, increment=True):
        """Track connection count for least connections algorithm"""
        service_key = f"{service['address']}:{service['port']}"
        current = self.connection_counts.get(service_key, 0)
        
        if increment:
            self.connection_counts[service_key] = current + 1
        else:
            self.connection_counts[service_key] = max(0, current - 1)

# Test Classes
class TestServiceDiscoveryBasics:
    """Test basic service discovery functionality"""
    
    def test_consul_service_registration(self):
        """Test service registration with Consul"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        result = asyncio.run(discovery.register_service(
            "web-server-1", "web-server", "192.168.1.10", 8080,
            tags=["web", "api"], health_check_url="http://192.168.1.10:8080/health"
        ))
        
        assert result["status"] == "registered"
        assert result["service_id"] == "web-server-1"
        assert discovery.metrics["services_registered"] == 1
        
    def test_etcd_service_registration(self):
        """Test service registration with etcd"""
        discovery = ServiceDiscoveryManager(backend="etcd")
        
        result = asyncio.run(discovery.register_service(
            "api-server-1", "api-server", "192.168.1.11", 9000,
            tags=["api", "v1"], health_check_url="http://192.168.1.11:9000/health"
        ))
        
        assert result is True
        assert discovery.metrics["services_registered"] == 1
        
    @pytest.mark.asyncio
    async def test_service_discovery(self):
        """Test service discovery"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register multiple services
        await discovery.register_service(
            "web-1", "web-server", "192.168.1.10", 8080
        )
        await discovery.register_service(
            "web-2", "web-server", "192.168.1.11", 8080
        )
        await discovery.register_service(
            "web-3", "web-server", "192.168.1.12", 8080
        )
        
        # Discover services
        services = await discovery.discover_services("web-server")
        
        assert len(services) == 3
        assert all(service["name"] == "web-server" for service in services)
        assert discovery.metrics["services_discovered"] == 1
        
    @pytest.mark.asyncio
    async def test_service_cache(self):
        """Test service discovery caching"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register service
        await discovery.register_service(
            "cache-test", "cache-service", "192.168.1.20", 8080
        )
        
        # First discovery (cache miss)
        services1 = await discovery.discover_services("cache-service")
        assert discovery.metrics["cache_misses"] == 1
        assert discovery.metrics["cache_hits"] == 0
        
        # Second discovery (cache hit)
        services2 = await discovery.discover_services("cache-service")
        assert discovery.metrics["cache_hits"] == 1
        
        assert services1 == services2

class TestLoadBalancing:
    """Test load balancing functionality"""
    
    @pytest.mark.asyncio
    async def test_round_robin_load_balancing(self):
        """Test round robin load balancing"""
        discovery = ServiceDiscoveryManager(backend="consul")
        load_balancer = LoadBalancer(discovery)
        
        # Register multiple services
        for i in range(3):
            await discovery.register_service(
                f"lb-test-{i}", "lb-service", f"192.168.1.{10+i}", 8080
            )
            
        # Test round robin selection
        selected_services = []
        for _ in range(6):  # 2 full rounds
            service = await load_balancer.get_backend("lb-service", "round_robin")
            selected_services.append(service["address"])
            
        # Should cycle through all services
        assert len(set(selected_services)) == 3
        
    @pytest.mark.asyncio
    async def test_random_load_balancing(self):
        """Test random load balancing"""
        discovery = ServiceDiscoveryManager(backend="consul")
        load_balancer = LoadBalancer(discovery)
        
        # Register multiple services
        for i in range(5):
            await discovery.register_service(
                f"random-test-{i}", "random-service", f"192.168.1.{20+i}", 8080
            )
            
        # Test random selection
        selected_services = []
        for _ in range(20):
            service = await load_balancer.get_backend("random-service", "random")
            selected_services.append(service["address"])
            
        # Should select from all services (probabilistically)
        unique_selections = set(selected_services)
        assert len(unique_selections) >= 3  # Should hit most services
        
    @pytest.mark.asyncio
    async def test_least_connections_load_balancing(self):
        """Test least connections load balancing"""
        discovery = ServiceDiscoveryManager(backend="consul")
        load_balancer = LoadBalancer(discovery)
        
        # Register services
        for i in range(3):
            await discovery.register_service(
                f"conn-test-{i}", "conn-service", f"192.168.1.{30+i}", 8080
            )
            
        # Simulate connections to first service
        services = await discovery.discover_services("conn-service")
        load_balancer.track_connection(services[0], increment=True)
        load_balancer.track_connection(services[0], increment=True)
        
        # Next selection should prefer service with fewer connections
        selected = await load_balancer.get_backend("conn-service", "least_connections")
        assert selected["address"] != services[0]["address"]

class TestHealthChecking:
    """Test health checking functionality"""
    
    @pytest.mark.asyncio
    async def test_health_check_passing(self):
        """Test health check for healthy service"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register service with health check
        await discovery.register_service(
            "healthy-service", "health-test", "192.168.1.40", 8080,
            health_check_url="http://192.168.1.40:8080/health"
        )
        
        # Check health
        health = await discovery.health_check_service("healthy-service")
        assert health["status"] == "passing"
        assert discovery.metrics["health_checks_performed"] == 1
        
    @pytest.mark.asyncio
    async def test_unhealthy_service_filtering(self):
        """Test filtering of unhealthy services"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register healthy service
        await discovery.register_service(
            "healthy-1", "filter-test", "192.168.1.50", 8080
        )
        
        # Register unhealthy service
        await discovery.register_service(
            "unhealthy-1", "filter-test", "192.168.1.51", 8080
        )
        
        # Mark second service as unhealthy
        discovery.consul_client.update_health_check("unhealthy-1", "failing")
        
        # Discovery should only return healthy services
        services = await discovery.discover_services("filter-test", use_cache=False)
        assert len(services) == 1
        assert services[0]["id"] == "healthy-1"

class TestIndianMicroservicesScenarios:
    """Test Indian microservices scenarios"""
    
    @pytest.mark.asyncio
    @pytest.mark.indian_context
    @pytest.mark.ecommerce
    async def test_flipkart_microservices_discovery(self):
        """Test Flipkart-style microservices discovery"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register Flipkart-like microservices
        services = [
            ("product-catalog-1", "product-catalog", "mumbai-dc1", 8080),
            ("product-catalog-2", "product-catalog", "mumbai-dc2", 8080),
            ("inventory-service-1", "inventory-service", "bangalore-dc1", 8081),
            ("inventory-service-2", "inventory-service", "bangalore-dc2", 8081),
            ("cart-service-1", "cart-service", "delhi-dc1", 8082),
            ("payment-gateway-1", "payment-gateway", "mumbai-dc1", 8083),
            ("payment-gateway-2", "payment-gateway", "mumbai-dc2", 8083),
            ("order-service-1", "order-service", "bangalore-dc1", 8084),
            ("notification-service-1", "notification-service", "delhi-dc1", 8085)
        ]
        
        for service_id, service_name, dc, port in services:
            await discovery.register_service(
                service_id, service_name, f"192.168.1.{hash(dc) % 100 + 100}", port,
                tags=[dc.split('-')[0], "production"]
            )
            
        # Test discovery of critical services
        product_services = await discovery.discover_services("product-catalog")
        inventory_services = await discovery.discover_services("inventory-service") 
        payment_services = await discovery.discover_services("payment-gateway")
        
        assert len(product_services) == 2
        assert len(inventory_services) == 2
        assert len(payment_services) == 2
        
        # Verify regional distribution
        mumbai_services = [s for s in product_services + payment_services 
                          if "mumbai" in s.get("tags", [])]
        bangalore_services = [s for s in inventory_services 
                             if "bangalore" in s.get("tags", [])]
        
        assert len(mumbai_services) >= 2  # Product + Payment in Mumbai
        assert len(bangalore_services) >= 1  # Inventory in Bangalore
        
    @pytest.mark.asyncio
    @pytest.mark.indian_context
    @pytest.mark.banking
    async def test_upi_payment_service_discovery(self):
        """Test UPI payment service discovery"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register UPI ecosystem services
        upi_services = [
            ("upi-gateway-1", "upi-gateway", "primary", 8080),
            ("upi-gateway-2", "upi-gateway", "secondary", 8080),
            ("bank-connector-hdfc", "bank-connector", "hdfc", 8081),
            ("bank-connector-icici", "bank-connector", "icici", 8081),
            ("bank-connector-sbi", "bank-connector", "sbi", 8081),
            ("fraud-detection-1", "fraud-detection", "primary", 8082),
            ("fraud-detection-2", "fraud-detection", "secondary", 8082),
            ("transaction-processor-1", "transaction-processor", "primary", 8083),
            ("transaction-processor-2", "transaction-processor", "secondary", 8083)
        ]
        
        for service_id, service_name, zone, port in upi_services:
            await discovery.register_service(
                service_id, service_name, f"10.0.{hash(zone) % 10 + 1}.{port % 100}", port,
                tags=[zone, "upi", "financial"]
            )
            
        # Test discovery of UPI services
        gateways = await discovery.discover_services("upi-gateway")
        bank_connectors = await discovery.discover_services("bank-connector")
        fraud_services = await discovery.discover_services("fraud-detection")
        
        assert len(gateways) == 2  # High availability
        assert len(bank_connectors) == 3  # Multiple bank integrations
        assert len(fraud_services) == 2  # Fraud detection redundancy
        
        # Test load balancing for UPI transactions
        load_balancer = LoadBalancer(discovery)
        
        # Simulate UPI transaction routing
        selected_gateway = await load_balancer.get_backend("upi-gateway")
        selected_processor = await load_balancer.get_backend("transaction-processor")
        
        assert selected_gateway is not None
        assert selected_processor is not None
        
    @pytest.mark.asyncio
    @pytest.mark.indian_context
    @pytest.mark.gaming
    async def test_gaming_service_discovery(self):
        """Test gaming service discovery (Dream11/MPL style)"""
        discovery = ServiceDiscoveryManager(backend="etcd")
        
        # Register gaming platform services
        gaming_services = [
            ("match-engine-1", "match-engine", "primary", 8080),
            ("match-engine-2", "match-engine", "secondary", 8080),
            ("user-service-1", "user-service", "mumbai", 8081),
            ("user-service-2", "user-service", "delhi", 8081),
            ("leaderboard-1", "leaderboard", "redis-primary", 8082),
            ("leaderboard-2", "leaderboard", "redis-secondary", 8082),
            ("payment-service-1", "payment-service", "secure-zone", 8083),
            ("notification-push-1", "notification-push", "primary", 8084),
            ("analytics-collector-1", "analytics-collector", "primary", 8085)
        ]
        
        for service_id, service_name, zone, port in gaming_services:
            await discovery.register_service(
                service_id, service_name, f"172.16.{hash(zone) % 10 + 1}.{port % 100}", port,
                tags=[zone, "gaming", "real-time"]
            )
            
        # Test discovery for real-time gaming
        match_engines = await discovery.discover_services("match-engine")
        leaderboards = await discovery.discover_services("leaderboard")
        user_services = await discovery.discover_services("user-service")
        
        assert len(match_engines) == 2  # Real-time redundancy
        assert len(leaderboards) == 2  # Fast leaderboard access
        assert len(user_services) == 2  # Geo-distributed users

class TestFailureScenarios:
    """Test failure scenarios and resilience"""
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_service_failure_detection(self, chaos_simulator):
        """Test detection of failed services"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register services
        await discovery.register_service(
            "resilient-1", "resilient-service", "192.168.1.60", 8080
        )
        await discovery.register_service(
            "resilient-2", "resilient-service", "192.168.1.61", 8080
        )
        
        # Simulate service failure
        chaos_simulator.service_failure("resilient-1", 1.0)  # 100% failure rate
        discovery.consul_client.update_health_check("resilient-1", "failing")
        
        # Discovery should return only healthy services
        services = await discovery.discover_services("resilient-service", use_cache=False)
        healthy_services = [s for s in services 
                           if discovery.consul_client.get_service_health(s["id"])["status"] == "passing"]
        
        assert len(healthy_services) == 1
        assert healthy_services[0]["id"] == "resilient-2"
        
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_discovery_backend_failure(self, chaos_simulator):
        """Test handling of discovery backend failure"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register and cache some services
        await discovery.register_service(
            "cache-test-1", "cache-service", "192.168.1.70", 8080
        )
        
        # First discovery to populate cache
        services1 = await discovery.discover_services("cache-service")
        assert len(services1) == 1
        
        # Simulate Consul failure by making it return empty results
        original_discover = discovery.consul_client.discover_services
        discovery.consul_client.discover_services = lambda name, healthy=True: []
        
        # Should fall back to cache
        services2 = await discovery.discover_services("cache-service")
        assert len(services2) == 1  # From cache
        assert discovery.metrics["cache_hits"] >= 1
        
        # Restore original function
        discovery.consul_client.discover_services = original_discover
        
    @pytest.mark.asyncio
    async def test_network_partition_handling(self):
        """Test handling of network partitions"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register services in different zones
        await discovery.register_service(
            "zone-a-1", "partition-test", "10.1.1.10", 8080,
            tags=["zone-a"]
        )
        await discovery.register_service(
            "zone-b-1", "partition-test", "10.2.1.10", 8080,
            tags=["zone-b"]
        )
        
        # Simulate network partition affecting zone-b
        discovery.consul_client.update_health_check("zone-b-1", "failing")
        
        # Should prefer services in available zones
        services = await discovery.discover_services("partition-test", use_cache=False)
        healthy_services = [s for s in services 
                           if discovery.consul_client.get_service_health(s["id"])["status"] == "passing"]
        
        assert len(healthy_services) == 1
        assert "zone-a" in healthy_services[0]["tags"]

class TestPerformanceScenarios:
    """Test performance under load"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_high_frequency_discovery(self, performance_monitor):
        """Test high frequency service discovery"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register multiple services
        for i in range(10):
            await discovery.register_service(
                f"perf-test-{i}", "perf-service", f"192.168.2.{10+i}", 8080
            )
            
        # Perform high frequency discovery
        performance_monitor.start_timer("discovery")
        
        tasks = []
        for _ in range(100):
            task = discovery.discover_services("perf-service")
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        
        discovery_time = performance_monitor.end_timer("discovery")
        
        # Verify all discoveries succeeded
        assert all(len(services) == 10 for services in results)
        
        # Check performance
        assert discovery_time < 1000  # < 1 second for 100 discoveries
        performance_monitor.assert_performance("discovery", 1000)
        
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_cache_performance(self, performance_monitor):
        """Test cache performance impact"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register services
        for i in range(5):
            await discovery.register_service(
                f"cache-perf-{i}", "cache-perf-service", f"192.168.2.{20+i}", 8080
            )
            
        # Test without cache
        discovery.clear_cache()
        performance_monitor.start_timer("no_cache")
        
        for _ in range(50):
            await discovery.discover_services("cache-perf-service", use_cache=False)
            
        no_cache_time = performance_monitor.end_timer("no_cache")
        
        # Test with cache
        discovery.clear_cache()
        performance_monitor.start_timer("with_cache")
        
        for _ in range(50):
            await discovery.discover_services("cache-perf-service", use_cache=True)
            
        with_cache_time = performance_monitor.end_timer("with_cache")
        
        # Cache should improve performance significantly
        assert with_cache_time < no_cache_time
        assert discovery.metrics["cache_hits"] > 40  # Most should be cache hits
        
    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.indian_context
    async def test_festival_load_discovery(self, festival_traffic_simulator, performance_monitor):
        """Test service discovery under festival load"""
        discovery = ServiceDiscoveryManager(backend="consul")
        
        # Register e-commerce services
        ecommerce_services = [
            "product-catalog", "inventory-service", "cart-service",
            "payment-gateway", "order-service", "notification-service"
        ]
        
        for service_name in ecommerce_services:
            for i in range(3):  # 3 instances each
                await discovery.register_service(
                    f"{service_name}-{i}", service_name, f"192.168.3.{10+i}", 8080
                )
                
        # Simulate Diwali traffic
        festival_sim = festival_traffic_simulator.simulate_festival("diwali")
        load_multiplier = festival_sim["multiplier"] / 10  # Scale for test
        
        # Test discovery under load
        performance_monitor.start_timer("festival_discovery")
        
        discovery_tasks = []
        for _ in range(int(100 * load_multiplier)):
            service_name = random.choice(ecommerce_services)
            task = discovery.discover_services(service_name)
            discovery_tasks.append(task)
            
        results = await asyncio.gather(*discovery_tasks)
        
        festival_time = performance_monitor.end_timer("festival_discovery")
        
        # Verify all discoveries succeeded
        assert all(len(services) == 3 for services in results)
        
        # Should handle festival load efficiently
        assert festival_time < 5000  # < 5 seconds even under heavy load

class TestIntegrationScenarios:
    """Integration tests with real-world scenarios"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.indian_context
    async def test_end_to_end_ecommerce_discovery(self):
        """Test complete e-commerce service discovery flow"""
        discovery = ServiceDiscoveryManager(backend="consul")
        load_balancer = LoadBalancer(discovery)
        
        # 1. Register complete e-commerce platform
        services_config = {
            "frontend": {"instances": 3, "port": 80},
            "api-gateway": {"instances": 2, "port": 8080},
            "user-service": {"instances": 2, "port": 8081},
            "product-catalog": {"instances": 4, "port": 8082},
            "inventory-service": {"instances": 3, "port": 8083},
            "cart-service": {"instances": 2, "port": 8084},
            "payment-gateway": {"instances": 4, "port": 8085},
            "order-service": {"instances": 3, "port": 8086},
            "notification-service": {"instances": 2, "port": 8087}
        }
        
        for service_name, config in services_config.items():
            for i in range(config["instances"]):
                await discovery.register_service(
                    f"{service_name}-{i}", service_name,
                    f"192.168.4.{10 + (hash(service_name) % 50) + i}", config["port"],
                    tags=["ecommerce", "production"]
                )
                
        # 2. Test service discovery for critical user journey
        user_journey = [
            "frontend",         # User visits site
            "api-gateway",      # API gateway routes request
            "user-service",     # User authentication
            "product-catalog",  # Browse products
            "cart-service",     # Add to cart
            "payment-gateway",  # Payment processing
            "order-service",    # Order placement
            "notification-service"  # Order confirmation
        ]
        
        discovered_services = {}
        for service_name in user_journey:
            services = await discovery.discover_services(service_name)
            discovered_services[service_name] = services
            
            # Verify service availability
            assert len(services) == services_config[service_name]["instances"]
            assert all(service["name"] == service_name for service in services)
            
        # 3. Test load balancing across the journey
        load_balanced_services = {}
        for service_name in user_journey:
            selected = await load_balancer.get_backend(service_name, "round_robin")
            load_balanced_services[service_name] = selected
            assert selected is not None
            
        # 4. Verify end-to-end connectivity
        assert len(discovered_services) == len(user_journey)
        assert len(load_balanced_services) == len(user_journey)
        
        # 5. Check metrics
        metrics = discovery.get_metrics()
        assert metrics["services_registered"] == sum(config["instances"] for config in services_config.values())
        assert metrics["services_discovered"] == len(user_journey)
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.indian_context
    @pytest.mark.banking
    async def test_end_to_end_banking_discovery(self):
        """Test complete banking service discovery flow"""
        discovery = ServiceDiscoveryManager(backend="etcd")
        
        # Register banking services across regions
        banking_services = {
            "user-auth": {"mumbai": 2, "delhi": 2, "bangalore": 1},
            "account-service": {"mumbai": 3, "delhi": 2, "bangalore": 2},
            "transaction-processor": {"mumbai": 4, "delhi": 3, "bangalore": 2},
            "fraud-detection": {"mumbai": 2, "delhi": 2, "bangalore": 1},
            "notification-service": {"mumbai": 2, "delhi": 2, "bangalore": 1},
            "audit-service": {"mumbai": 1, "delhi": 1, "bangalore": 1}
        }
        
        for service_name, regions in banking_services.items():
            for region, instances in regions.items():
                for i in range(instances):
                    await discovery.register_service(
                        f"{service_name}-{region}-{i}", service_name,
                        f"10.{hash(region) % 10 + 1}.{hash(service_name) % 100 + 1}.{10+i}",
                        8080 + hash(service_name) % 10,
                        tags=[region, "banking", "secure"]
                    )
                    
        # Test money transfer flow
        transfer_flow = [
            "user-auth",           # User authentication
            "account-service",     # Account validation
            "fraud-detection",     # Fraud check
            "transaction-processor", # Process transfer
            "notification-service", # Send notifications
            "audit-service"        # Audit logging
        ]
        
        for service_name in transfer_flow:
            services = await discovery.discover_services(service_name)
            total_expected = sum(banking_services[service_name].values())
            assert len(services) == total_expected
            
            # Verify regional distribution
            regions_found = set()
            for service in services:
                for tag in service.get("tags", []):
                    if tag in ["mumbai", "delhi", "bangalore"]:
                        regions_found.add(tag)
                        
            assert len(regions_found) >= 2  # Services should be distributed

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])