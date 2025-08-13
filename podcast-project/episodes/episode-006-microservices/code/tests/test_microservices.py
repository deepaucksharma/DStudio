#!/usr/bin/env python3
"""
Unit Tests for Episode 6: Microservices Patterns
भारतीय microservices patterns के लिए unit tests

This test suite covers individual microservices components:
- Circuit breaker logic testing
- Load balancer algorithms testing
- Service discovery functionality testing
- Health check mechanisms testing
- API gateway routing logic testing

Real Production Context:
- Flipkart: E-commerce microservices patterns
- Ola: Ride-sharing service coordination
- Zomato: Restaurant service availability
- PayTM: Payment transaction flows
- CRED: Credit scoring microservices

Author: Code Developer Agent
Context: Unit testing for भारतीय microservices components
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class TestServiceDiscovery:
    """
    Test service discovery functionality
    Service discovery functionality का testing
    """
    
    def test_service_registration(self):
        """Test service registration functionality"""
        # Mock service registry
        service_registry = {}
        
        def register_service(service_name: str, service_url: str, health_check_url: str):
            """Register a service in the registry"""
            service_registry[service_name] = {
                'url': service_url,
                'health_check': health_check_url,
                'registered_at': time.time(),
                'status': 'healthy'
            }
            return True
        
        # Test Flipkart product service registration
        result = register_service(
            "flipkart-product-catalog",
            "http://localhost:8001",
            "http://localhost:8001/health"
        )
        
        assert result is True
        assert "flipkart-product-catalog" in service_registry
        assert service_registry["flipkart-product-catalog"]["url"] == "http://localhost:8001"
        assert service_registry["flipkart-product-catalog"]["status"] == "healthy"
        
        print("✅ Service registration test passed - Flipkart style")
    
    def test_service_discovery_lookup(self):
        """Test service discovery lookup"""
        # Mock service registry with Indian services
        service_registry = {
            "ola-driver-service": {
                'url': 'http://mumbai-1.ola.com:8001',
                'health_check': 'http://mumbai-1.ola.com:8001/health',
                'region': 'mumbai',
                'status': 'healthy'
            },
            "zomato-restaurant-service": {
                'url': 'http://bangalore-1.zomato.com:8002',
                'health_check': 'http://bangalore-1.zomato.com:8002/health',
                'region': 'bangalore',
                'status': 'healthy'
            }
        }
        
        def discover_service(service_name: str, region: str = None):
            """Discover services by name and optional region"""
            if service_name not in service_registry:
                return None
            
            service = service_registry[service_name]
            
            # Regional filtering
            if region and service.get('region') != region:
                return None
                
            return service
        
        # Test service discovery
        ola_service = discover_service("ola-driver-service", "mumbai")
        assert ola_service is not None
        assert ola_service['url'] == 'http://mumbai-1.ola.com:8001'
        assert ola_service['region'] == 'mumbai'
        
        # Test regional filtering
        zomato_in_mumbai = discover_service("zomato-restaurant-service", "mumbai")
        assert zomato_in_mumbai is None  # Service not in Mumbai
        
        print("✅ Service discovery lookup test passed - Regional filtering works")

class TestCircuitBreaker:
    """
    Test circuit breaker pattern
    Circuit breaker pattern का testing
    """
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in CLOSED state"""
        
        class SimpleCircuitBreaker:
            def __init__(self, failure_threshold: int = 5, timeout: float = 60):
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.failure_count = 0
                self.state = "CLOSED"
                self.last_failure_time = None
            
            def call(self, func, *args, **kwargs):
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.timeout:
                        self.state = "HALF_OPEN"
                    else:
                        raise Exception("Circuit breaker is OPEN")
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Success - reset failure count
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                    self.failure_count = 0
                    return result
                    
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                    
                    raise e
        
        # Test circuit breaker with Zomato restaurant service
        circuit_breaker = SimpleCircuitBreaker(failure_threshold=3)
        
        def healthy_restaurant_service():
            """Simulate healthy restaurant service"""
            return {"restaurant_id": "123", "available": True, "eta": 30}
        
        # Test successful calls
        for i in range(5):
            result = circuit_breaker.call(healthy_restaurant_service)
            assert result["available"] is True
            assert circuit_breaker.state == "CLOSED"
            assert circuit_breaker.failure_count == 0
        
        print("✅ Circuit breaker CLOSED state test passed - Zomato style")
    
    def test_circuit_breaker_open_state(self):
        """Test circuit breaker in OPEN state"""
        
        class SimpleCircuitBreaker:
            def __init__(self, failure_threshold: int = 3):
                self.failure_threshold = failure_threshold
                self.failure_count = 0
                self.state = "CLOSED"
                self.last_failure_time = None
            
            def call(self, func, *args, **kwargs):
                if self.state == "OPEN":
                    raise Exception("Circuit breaker is OPEN - Service unavailable")
                
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                    
                    raise e
        
        circuit_breaker = SimpleCircuitBreaker(failure_threshold=3)
        
        def failing_service():
            """Simulate failing service"""
            raise Exception("Service unavailable")
        
        # Cause failures to open circuit
        for i in range(3):
            try:
                circuit_breaker.call(failing_service)
                assert False, "Should have raised exception"
            except Exception:
                pass  # Expected
        
        # Circuit should be open now
        assert circuit_breaker.state == "OPEN"
        
        # Subsequent calls should fail fast
        try:
            circuit_breaker.call(failing_service)
            assert False, "Circuit breaker should be OPEN"
        except Exception as e:
            assert "Circuit breaker is OPEN" in str(e)
        
        print("✅ Circuit breaker OPEN state test passed - Fast failure")

class TestLoadBalancer:
    """
    Test load balancing algorithms
    Load balancing algorithms का testing
    """
    
    def test_round_robin_balancer(self):
        """Test round-robin load balancing"""
        
        class RoundRobinBalancer:
            def __init__(self, servers):
                self.servers = servers
                self.current_index = 0
            
            def get_server(self):
                if not self.servers:
                    return None
                
                server = self.servers[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.servers)
                return server
        
        # Mumbai-based servers for testing
        mumbai_servers = [
            {"id": "mumbai-1", "region": "west", "capacity": 100},
            {"id": "mumbai-2", "region": "west", "capacity": 100},
            {"id": "pune-1", "region": "west", "capacity": 80}
        ]
        
        balancer = RoundRobinBalancer(mumbai_servers)
        
        # Test round-robin distribution
        selected_servers = []
        for i in range(9):  # 3 full cycles
            server = balancer.get_server()
            selected_servers.append(server["id"])
        
        # Should distribute evenly: mumbai-1, mumbai-2, pune-1, mumbai-1, ...
        expected = ["mumbai-1", "mumbai-2", "pune-1"] * 3
        assert selected_servers == expected
        
        print("✅ Round-robin load balancer test passed - Mumbai distribution")
    
    def test_weighted_load_balancer(self):
        """Test weighted load balancing"""
        
        class WeightedBalancer:
            def __init__(self, servers):
                self.servers = servers
                self.total_weight = sum(s.get("weight", 1) for s in servers)
                self.current_weights = [0] * len(servers)
            
            def get_server(self):
                if not self.servers:
                    return None
                
                # Weighted round-robin algorithm
                for i, server in enumerate(self.servers):
                    weight = server.get("weight", 1)
                    self.current_weights[i] += weight
                
                # Find server with highest current weight
                max_weight_idx = max(range(len(self.current_weights)), 
                                   key=lambda i: self.current_weights[i])
                
                selected_server = self.servers[max_weight_idx]
                self.current_weights[max_weight_idx] -= self.total_weight
                
                return selected_server
        
        # Flipkart servers with different capacities (weights)
        flipkart_servers = [
            {"id": "bangalore-1", "weight": 3, "capacity": 300},  # High capacity
            {"id": "delhi-1", "weight": 2, "capacity": 200},     # Medium capacity  
            {"id": "mumbai-1", "weight": 1, "capacity": 100}     # Lower capacity
        ]
        
        balancer = WeightedBalancer(flipkart_servers)
        
        # Test weighted distribution over 12 requests
        server_counts = {"bangalore-1": 0, "delhi-1": 0, "mumbai-1": 0}
        for i in range(12):
            server = balancer.get_server()
            server_counts[server["id"]] += 1
        
        # Should follow weight ratio 3:2:1 (6:4:2 out of 12)
        assert server_counts["bangalore-1"] == 6  # 3/(3+2+1) * 12 = 6
        assert server_counts["delhi-1"] == 4      # 2/(3+2+1) * 12 = 4  
        assert server_counts["mumbai-1"] == 2     # 1/(3+2+1) * 12 = 2
        
        print("✅ Weighted load balancer test passed - Flipkart capacity distribution")

class TestHealthChecks:
    """
    Test health check mechanisms
    Health check mechanisms का testing
    """
    
    def test_service_health_monitoring(self):
        """Test service health monitoring"""
        
        class HealthMonitor:
            def __init__(self):
                self.services = {}
            
            def register_service(self, service_id: str, health_check_func):
                self.services[service_id] = {
                    'health_check': health_check_func,
                    'status': 'unknown',
                    'last_check': None,
                    'failure_count': 0
                }
            
            def check_service_health(self, service_id: str):
                if service_id not in self.services:
                    return False
                
                service = self.services[service_id]
                
                try:
                    is_healthy = service['health_check']()
                    service['status'] = 'healthy' if is_healthy else 'unhealthy'
                    service['last_check'] = time.time()
                    
                    if is_healthy:
                        service['failure_count'] = 0
                    else:
                        service['failure_count'] += 1
                    
                    return is_healthy
                    
                except Exception as e:
                    service['status'] = 'error'
                    service['failure_count'] += 1
                    service['last_check'] = time.time()
                    return False
            
            def get_healthy_services(self):
                return [sid for sid, service in self.services.items() 
                       if service['status'] == 'healthy']
        
        monitor = HealthMonitor()
        
        # Register Ola services with health checks
        def ola_driver_health():
            return True  # Healthy
        
        def ola_booking_health():
            return False  # Unhealthy
        
        def ola_payment_health():
            raise Exception("Service error")
        
        monitor.register_service("ola-driver-service", ola_driver_health)
        monitor.register_service("ola-booking-service", ola_booking_health)
        monitor.register_service("ola-payment-service", ola_payment_health)
        
        # Check health
        assert monitor.check_service_health("ola-driver-service") is True
        assert monitor.check_service_health("ola-booking-service") is False
        assert monitor.check_service_health("ola-payment-service") is False
        
        # Get healthy services
        healthy_services = monitor.get_healthy_services()
        assert healthy_services == ["ola-driver-service"]
        
        print("✅ Health monitoring test passed - Ola services monitored")

class TestApiGateway:
    """
    Test API Gateway functionality
    API Gateway functionality का testing
    """
    
    def test_route_matching(self):
        """Test API Gateway route matching"""
        
        class SimpleApiGateway:
            def __init__(self):
                self.routes = {}
            
            def add_route(self, path_pattern: str, service_url: str, methods=None):
                if methods is None:
                    methods = ["GET"]
                
                self.routes[path_pattern] = {
                    'service_url': service_url,
                    'methods': methods
                }
            
            def route_request(self, path: str, method: str = "GET"):
                # Simple pattern matching (in production, would use regex)
                for pattern, route_config in self.routes.items():
                    if self._path_matches(path, pattern) and method in route_config['methods']:
                        return route_config['service_url']
                
                return None
            
            def _path_matches(self, path: str, pattern: str):
                # Simple wildcard matching
                if "*" in pattern:
                    prefix = pattern.replace("*", "")
                    return path.startswith(prefix)
                else:
                    return path == pattern
        
        gateway = SimpleApiGateway()
        
        # Add PayTM-style routes
        gateway.add_route("/api/v1/payments/*", "http://payment-service:8001", ["POST", "GET"])
        gateway.add_route("/api/v1/wallet/*", "http://wallet-service:8002", ["GET", "POST"])
        gateway.add_route("/api/v1/users/*", "http://user-service:8003", ["GET", "PUT"])
        
        # Test route matching
        payment_route = gateway.route_request("/api/v1/payments/create", "POST")
        assert payment_route == "http://payment-service:8001"
        
        wallet_route = gateway.route_request("/api/v1/wallet/balance", "GET")
        assert wallet_route == "http://wallet-service:8002"
        
        user_route = gateway.route_request("/api/v1/users/profile", "GET")
        assert user_route == "http://user-service:8003"
        
        # Test non-matching route
        invalid_route = gateway.route_request("/api/v1/unknown", "GET")
        assert invalid_route is None
        
        print("✅ API Gateway routing test passed - PayTM style routes")
    
    def test_rate_limiting(self):
        """Test API Gateway rate limiting"""
        
        class RateLimiter:
            def __init__(self, max_requests: int, time_window: int):
                self.max_requests = max_requests
                self.time_window = time_window  # in seconds
                self.requests = {}  # client_id -> list of timestamps
            
            def is_allowed(self, client_id: str):
                now = time.time()
                
                if client_id not in self.requests:
                    self.requests[client_id] = []
                
                # Clean old requests outside time window
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if now - req_time < self.time_window
                ]
                
                # Check if under limit
                if len(self.requests[client_id]) < self.max_requests:
                    self.requests[client_id].append(now)
                    return True
                else:
                    return False
        
        # Test rate limiting for Flipkart API (100 requests per minute)
        rate_limiter = RateLimiter(max_requests=5, time_window=60)  # 5 req/min for testing
        
        client_id = "flipkart_mobile_app"
        
        # First 5 requests should be allowed
        for i in range(5):
            assert rate_limiter.is_allowed(client_id) is True
        
        # 6th request should be denied
        assert rate_limiter.is_allowed(client_id) is False
        
        # Different client should be allowed
        assert rate_limiter.is_allowed("flipkart_web_app") is True
        
        print("✅ Rate limiting test passed - Flipkart API protection")

# Integration test
class TestMicroservicesIntegration:
    """
    Test microservices integration scenarios
    Microservices integration scenarios का testing
    """
    
    @pytest.mark.asyncio
    async def test_end_to_end_request_flow(self):
        """Test end-to-end request flow through multiple services"""
        
        # Mock services
        async def mock_user_service(user_id: str):
            await asyncio.sleep(0.1)  # Simulate service call
            return {"user_id": user_id, "name": "Rahul Sharma", "verified": True}
        
        async def mock_product_service(product_id: str):
            await asyncio.sleep(0.05)
            return {"product_id": product_id, "name": "iPhone 15", "price": 79000, "available": True}
        
        async def mock_inventory_service(product_id: str):
            await asyncio.sleep(0.03)
            return {"product_id": product_id, "quantity": 50, "reserved": 5}
        
        async def mock_payment_service(amount: float, user_id: str):
            await asyncio.sleep(0.2)  # Payment takes longer
            return {"transaction_id": "TXN123", "status": "success", "amount": amount}
        
        # Simulate end-to-end order flow
        async def process_order(user_id: str, product_id: str):
            start_time = time.time()
            
            # Call services in sequence
            user = await mock_user_service(user_id)
            if not user["verified"]:
                return {"error": "User not verified"}
            
            product = await mock_product_service(product_id)
            if not product["available"]:
                return {"error": "Product not available"}
            
            inventory = await mock_inventory_service(product_id)
            if inventory["quantity"] <= inventory["reserved"]:
                return {"error": "Insufficient inventory"}
            
            payment = await mock_payment_service(product["price"], user_id)
            if payment["status"] != "success":
                return {"error": "Payment failed"}
            
            end_time = time.time()
            
            return {
                "order_id": "ORD123",
                "user": user,
                "product": product,
                "payment": payment,
                "processing_time": end_time - start_time,
                "status": "confirmed"
            }
        
        # Test successful order flow
        result = await process_order("USER123", "PROD456")
        
        assert result["status"] == "confirmed"
        assert result["user"]["user_id"] == "USER123"
        assert result["product"]["product_id"] == "PROD456"
        assert result["payment"]["status"] == "success"
        assert result["processing_time"] < 0.5  # Should complete within 500ms
        
        print("✅ End-to-end integration test passed - Order flow complete")

# Test runner
def run_microservices_tests():
    """Run all microservices unit tests"""
    print("🚀 Running Microservices Unit Tests")
    print("भारतीय microservices patterns के लिए unit testing")
    print("=" * 60)
    
    test_classes = [
        TestServiceDiscovery(),
        TestCircuitBreaker(), 
        TestLoadBalancer(),
        TestHealthChecks(),
        TestApiGateway()
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n🧪 Running {class_name} tests...")
        
        # Get test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method_name in test_methods:
            try:
                test_method = getattr(test_class, test_method_name)
                test_method()
                total_tests += 1
                passed_tests += 1
            except Exception as e:
                print(f"❌ {test_method_name} failed: {str(e)}")
                total_tests += 1
    
    # Run async integration test
    try:
        print(f"\n🧪 Running Integration tests...")
        integration_test = TestMicroservicesIntegration()
        asyncio.run(integration_test.test_end_to_end_request_flow())
        total_tests += 1
        passed_tests += 1
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        total_tests += 1
    
    print(f"\n" + "=" * 60)
    print(f"🎯 TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} {'❌' if total_tests - passed_tests > 0 else '✅'}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL MICROSERVICES UNIT TESTS PASSED!")
        print(f"🚀 Production Ready for भारतीय Microservices!")
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print(f"🔧 Fix failing tests before production deployment")

if __name__ == "__main__":
    run_microservices_tests()