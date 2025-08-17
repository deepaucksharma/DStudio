#!/usr/bin/env python3
"""
🇮🇳 Unit Tests for Consul Service Discovery
Episode 64: Service Discovery - Consul Tests

Author: Agent 5 - Code Developer
Context: Testing Flipkart-style service discovery
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from typing import List, Dict, Optional

# Mock the consul import since it might not be available in test environment
sys.modules['consul'] = MagicMock()

# Import after mocking
from consul_service_discovery import FlipkartServiceDiscovery, ServiceInstance

class TestServiceInstance:
    """Test ServiceInstance dataclass"""
    
    def test_service_instance_creation(self):
        """Test basic service instance creation"""
        service = ServiceInstance(
            name="test-service",
            host="localhost",
            port=8080,
            health_endpoint="http://localhost:8080/health",
            tags=["test", "api"],
            metadata={"version": "1.0.0"},
            region="mumbai"
        )
        
        assert service.name == "test-service"
        assert service.host == "localhost"
        assert service.port == 8080
        assert service.region == "mumbai"
        assert "test" in service.tags
        assert service.metadata["version"] == "1.0.0"

    def test_service_instance_defaults(self):
        """Test default values in service instance"""
        service = ServiceInstance(
            name="test-service",
            host="localhost", 
            port=8080,
            health_endpoint="http://localhost:8080/health",
            tags=[],
            metadata={}
        )
        
        assert service.region == "mumbai"  # Default region

class TestFlipkartServiceDiscovery:
    """Test Flipkart Service Discovery implementation"""
    
    @pytest.fixture
    def mock_consul(self):
        """Create mock consul client"""
        mock_consul = MagicMock()
        mock_consul.agent.service.register.return_value = True
        mock_consul.agent.service.deregister.return_value = True
        mock_consul.health.service.return_value = (None, [])
        mock_consul.catalog.services.return_value = (None, {})
        return mock_consul
    
    @pytest.fixture
    def discovery_service(self, mock_consul):
        """Create discovery service with mocked consul"""
        with patch('consul.Consul', return_value=mock_consul):
            discovery = FlipkartServiceDiscovery()
            return discovery
    
    def test_initialization(self, discovery_service):
        """Test service discovery initialization"""
        assert discovery_service is not None
        assert discovery_service.local_services == {}
        assert discovery_service.running is True
    
    def test_register_service_success(self, discovery_service, mock_consul):
        """Test successful service registration"""
        service = ServiceInstance(
            name="product-catalog",
            host="10.0.1.10",
            port=8080,
            health_endpoint="http://10.0.1.10:8080/health",
            tags=["catalog", "products"],
            metadata={"version": "2.1.0"},
            region="mumbai"
        )
        
        # Mock consul client
        discovery_service.consul = mock_consul
        
        result = discovery_service.register_service(service)
        
        assert result is True
        assert len(discovery_service.local_services) == 1
        
        # Verify consul.agent.service.register was called
        mock_consul.agent.service.register.assert_called_once()
        
        call_args = mock_consul.agent.service.register.call_args
        assert call_args[1]['name'] == 'product-catalog'
        assert call_args[1]['address'] == '10.0.1.10'
        assert call_args[1]['port'] == 8080
    
    def test_register_service_failure(self, discovery_service, mock_consul):
        """Test service registration failure"""
        service = ServiceInstance(
            name="test-service",
            host="localhost",
            port=8080,
            health_endpoint="http://localhost:8080/health",
            tags=[],
            metadata={}
        )
        
        # Mock consul registration failure
        mock_consul.agent.service.register.return_value = False
        discovery_service.consul = mock_consul
        
        result = discovery_service.register_service(service)
        
        assert result is False
        assert len(discovery_service.local_services) == 0
    
    def test_discover_services_empty(self, discovery_service, mock_consul):
        """Test service discovery with no services"""
        discovery_service.consul = mock_consul
        
        # Mock empty service response
        mock_consul.health.service.return_value = (None, [])
        
        services = discovery_service.discover_services("nonexistent-service")
        
        assert services == []
        mock_consul.health.service.assert_called_once_with(
            "nonexistent-service", passing=True, tag=None
        )
    
    def test_discover_services_with_results(self, discovery_service, mock_consul):
        """Test service discovery with results"""
        discovery_service.consul = mock_consul
        
        # Mock service response
        mock_service_data = [{
            'Service': {
                'Service': 'product-catalog',
                'Address': '10.0.1.10',
                'Port': 8080,
                'Tags': ['catalog', 'products', 'region:mumbai'],
                'Meta': {'version': '2.1.0'}
            }
        }]
        
        mock_consul.health.service.return_value = (None, mock_service_data)
        
        services = discovery_service.discover_services("product-catalog")
        
        assert len(services) == 1
        service = services[0]
        assert service.name == 'product-catalog'
        assert service.host == '10.0.1.10'
        assert service.port == 8080
        assert service.region == 'mumbai'
    
    def test_discover_services_region_filter(self, discovery_service, mock_consul):
        """Test service discovery with region filtering"""
        discovery_service.consul = mock_consul
        
        # Mock multiple services in different regions
        mock_service_data = [
            {
                'Service': {
                    'Service': 'payment-gateway',
                    'Address': '10.0.1.20',
                    'Port': 8081,
                    'Tags': ['payment', 'region:mumbai'],
                    'Meta': {}
                }
            },
            {
                'Service': {
                    'Service': 'payment-gateway',
                    'Address': '10.0.2.20',
                    'Port': 8081,
                    'Tags': ['payment', 'region:delhi'],
                    'Meta': {}
                }
            }
        ]
        
        mock_consul.health.service.return_value = (None, mock_service_data)
        
        # Test region filtering
        mumbai_services = discovery_service.discover_services("payment-gateway", region="mumbai")
        
        assert len(mumbai_services) == 1
        assert mumbai_services[0].region == "mumbai"
        assert mumbai_services[0].host == "10.0.1.20"
    
    def test_get_service_instance_round_robin(self, discovery_service, mock_consul):
        """Test round-robin load balancing"""
        discovery_service.consul = mock_consul
        
        # Mock multiple service instances
        mock_service_data = [
            {
                'Service': {
                    'Service': 'api-service',
                    'Address': '10.0.1.10',
                    'Port': 8080,
                    'Tags': ['api', 'region:mumbai'],
                    'Meta': {}
                }
            },
            {
                'Service': {
                    'Service': 'api-service',
                    'Address': '10.0.1.11',
                    'Port': 8080,
                    'Tags': ['api', 'region:mumbai'],
                    'Meta': {}
                }
            }
        ]
        
        mock_consul.health.service.return_value = (None, mock_service_data)
        
        instance = discovery_service.get_service_instance("api-service", "round_robin")
        
        assert instance is not None
        assert instance.name == "api-service"
        assert instance.host in ["10.0.1.10", "10.0.1.11"]
    
    def test_get_service_instance_no_instances(self, discovery_service, mock_consul):
        """Test getting service instance when none available"""
        discovery_service.consul = mock_consul
        mock_consul.health.service.return_value = (None, [])
        
        instance = discovery_service.get_service_instance("nonexistent-service")
        
        assert instance is None
    
    def test_deregister_service_success(self, discovery_service, mock_consul):
        """Test successful service deregistration"""
        # First register a service
        service = ServiceInstance(
            name="test-service",
            host="localhost",
            port=8080,
            health_endpoint="http://localhost:8080/health",
            tags=[],
            metadata={},
            region="mumbai"
        )
        
        discovery_service.consul = mock_consul
        discovery_service.register_service(service)
        
        # Get the service ID
        service_id = list(discovery_service.local_services.keys())[0]
        
        # Test deregistration
        result = discovery_service.deregister_service(service_id)
        
        assert result is True
        assert len(discovery_service.local_services) == 0
        mock_consul.agent.service.deregister.assert_called_once_with(service_id)
    
    def test_deregister_nonexistent_service(self, discovery_service):
        """Test deregistering non-existent service"""
        result = discovery_service.deregister_service("nonexistent-service-id")
        
        assert result is False
    
    def test_get_service_catalog(self, discovery_service, mock_consul):
        """Test getting complete service catalog"""
        discovery_service.consul = mock_consul
        
        # Mock catalog response
        mock_consul.catalog.services.return_value = (None, {
            'product-catalog': [],
            'payment-gateway': [],
            'inventory-service': []
        })
        
        # Mock individual service discoveries
        def mock_discover_services(service_name):
            if service_name == 'product-catalog':
                return [ServiceInstance(
                    name=service_name,
                    host="10.0.1.10",
                    port=8080,
                    health_endpoint="http://10.0.1.10:8080/health",
                    tags=[],
                    metadata={}
                )]
            return []
        
        discovery_service.discover_services = Mock(side_effect=mock_discover_services)
        
        catalog = discovery_service.get_service_catalog()
        
        assert 'product-catalog' in catalog
        assert len(catalog['product-catalog']) == 1
    
    def test_shutdown(self, discovery_service, mock_consul):
        """Test graceful shutdown"""
        # Register a service first
        service = ServiceInstance(
            name="test-service",
            host="localhost",
            port=8080,
            health_endpoint="http://localhost:8080/health",
            tags=[],
            metadata={}
        )
        
        discovery_service.consul = mock_consul
        discovery_service.register_service(service)
        
        # Test shutdown
        discovery_service.shutdown()
        
        assert discovery_service.running is False
        assert len(discovery_service.local_services) == 0
    
    @patch('requests.get')
    def test_monitor_service_health(self, mock_requests, discovery_service):
        """Test service health monitoring"""
        # Mock healthy response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        service = ServiceInstance(
            name="test-service",
            host="localhost",
            port=8080,
            health_endpoint="http://localhost:8080/health",
            tags=[],
            metadata={}
        )
        
        discovery_service.local_services['test-service-id'] = service
        
        # Start monitoring (for testing, we'll call it directly)
        discovery_service.monitor_service_health(interval=1)
        
        # Give it a moment to start
        time.sleep(0.1)
        
        assert discovery_service.health_check_thread is not None

class TestIntegration:
    """Integration tests for service discovery workflow"""
    
    @patch('consul.Consul')
    def test_full_workflow(self, mock_consul_class):
        """Test complete service discovery workflow"""
        mock_consul = MagicMock()
        mock_consul.agent.service.register.return_value = True
        mock_consul.agent.service.deregister.return_value = True
        mock_consul.health.service.return_value = (None, [])
        mock_consul_class.return_value = mock_consul
        
        # Initialize discovery
        discovery = FlipkartServiceDiscovery()
        
        # Register service
        service = ServiceInstance(
            name="integration-test",
            host="localhost",
            port=8080,
            health_endpoint="http://localhost:8080/health",
            tags=["test"],
            metadata={"version": "1.0.0"}
        )
        
        result = discovery.register_service(service)
        assert result is True
        
        # Verify registration
        assert len(discovery.local_services) == 1
        
        # Deregister service
        service_id = list(discovery.local_services.keys())[0]
        result = discovery.deregister_service(service_id)
        assert result is True
        
        # Verify deregistration
        assert len(discovery.local_services) == 0
        
        # Shutdown
        discovery.shutdown()
        assert discovery.running is False

# Performance tests
class TestPerformance:
    """Performance and load tests"""
    
    @patch('consul.Consul')
    def test_multiple_service_registration(self, mock_consul_class):
        """Test registering multiple services"""
        mock_consul = MagicMock()
        mock_consul.agent.service.register.return_value = True
        mock_consul_class.return_value = mock_consul
        
        discovery = FlipkartServiceDiscovery()
        
        # Register multiple services
        services = []
        for i in range(10):
            service = ServiceInstance(
                name=f"service-{i}",
                host=f"10.0.1.{i + 10}",
                port=8080 + i,
                health_endpoint=f"http://10.0.1.{i + 10}:{8080 + i}/health",
                tags=[f"test-{i}"],
                metadata={"id": str(i)}
            )
            services.append(service)
        
        start_time = time.time()
        
        for service in services:
            result = discovery.register_service(service)
            assert result is True
        
        end_time = time.time()
        registration_time = end_time - start_time
        
        # Should register 10 services in under 1 second
        assert registration_time < 1.0
        assert len(discovery.local_services) == 10
        
        discovery.shutdown()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])