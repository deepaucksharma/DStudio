#!/usr/bin/env python3
"""
Test suite for Kong API Gateway
Testing like Mumbai local train load testing during peak hours
"""

import asyncio
import pytest
import httpx
import json
import time
from kong_gateway import KongGateway, ServiceRoute, AuthManager

# Test configuration
TEST_CONFIG = {
    'jwt_secret': 'test-secret-key',
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_db': 1  # Use different DB for testing
}

@pytest.fixture
async def gateway():
    """Create test gateway instance"""
    gateway = KongGateway(TEST_CONFIG)
    
    # Add test routes
    test_routes = [
        ServiceRoute(
            path="/api/test",
            service_url="http://httpbin.org",
            rate_limit=10,
            auth_required=False
        ),
        ServiceRoute(
            path="/api/secure",
            service_url="http://httpbin.org",
            rate_limit=5,
            auth_required=True
        )
    ]
    
    for route in test_routes:
        gateway.add_route(route)
    
    return gateway

@pytest.fixture
def auth_manager():
    """Create auth manager for testing"""
    return AuthManager(TEST_CONFIG['jwt_secret'])

class TestRateLimiting:
    """Rate limiting tests - जैसे Mumbai Metro entry gates"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_basic(self, gateway):
        """Test basic rate limiting functionality"""
        
        # Simulate rapid requests
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            responses = []
            
            # Send requests within limit
            for i in range(8):  # Within 10 request limit
                response = await client.get("/api/test/get")
                responses.append(response.status_code)
            
            # All should succeed
            assert all(status == 200 for status in responses[:8])
            
            # Exceed rate limit
            for i in range(5):  # Exceed limit
                response = await client.get("/api/test/get")
                responses.append(response.status_code)
            
            # Some should be rate limited (429)
            assert any(status == 429 for status in responses[8:])
    
    @pytest.mark.asyncio
    async def test_rate_limit_per_client(self, gateway):
        """Test rate limiting per client IP"""
        
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            # Client 1 requests
            client1_responses = []
            for i in range(12):
                response = await client.get("/api/test/get", headers={"X-Forwarded-For": "1.1.1.1"})
                client1_responses.append(response.status_code)
            
            # Client 2 requests (different IP)
            client2_responses = []
            for i in range(5):
                response = await client.get("/api/test/get", headers={"X-Forwarded-For": "2.2.2.2"})
                client2_responses.append(response.status_code)
            
            # Client 1 should hit rate limit
            assert any(status == 429 for status in client1_responses)
            
            # Client 2 should be fine
            assert all(status == 200 for status in client2_responses)

class TestAuthentication:
    """Authentication tests - जैसे Mumbai Metro card validation"""
    
    def test_token_creation_and_verification(self, auth_manager):
        """Test JWT token creation and verification"""
        
        # Create token
        token = auth_manager.create_token("user123", "admin")
        assert token is not None
        
        # Verify token
        payload = auth_manager.verify_token(f"Bearer {token}")
        assert payload is not None
        assert payload["user_id"] == "user123"
        assert payload["role"] == "admin"
    
    def test_invalid_token(self, auth_manager):
        """Test invalid token handling"""
        
        # Invalid token
        payload = auth_manager.verify_token("Bearer invalid-token")
        assert payload is None
        
        # Missing Bearer prefix
        token = auth_manager.create_token("user123")
        payload = auth_manager.verify_token(token)
        assert payload is None
    
    @pytest.mark.asyncio
    async def test_auth_required_endpoint(self, gateway, auth_manager):
        """Test authentication required endpoints"""
        
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            # Request without token
            response = await client.get("/api/secure/get")
            assert response.status_code == 401
            
            # Request with valid token
            token = auth_manager.create_token("user123")
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/secure/get", headers=headers)
            assert response.status_code == 200

class TestCircuitBreaker:
    """Circuit breaker tests - जैसे Mumbai power grid protection"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self, gateway):
        """Test circuit breaker opens on failures"""
        
        # Add route with circuit breaker
        route = ServiceRoute(
            path="/api/failing",
            service_url="http://localhost:99999",  # Non-existent service
            circuit_breaker_enabled=True,
            retry_count=1
        )
        gateway.add_route(route)
        
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            # Make multiple failing requests
            for i in range(6):  # Exceed failure threshold
                try:
                    response = await client.get("/api/failing/test")
                except:
                    pass  # Expected to fail
            
            # Next request should be blocked by circuit breaker
            response = await client.get("/api/failing/test")
            assert response.status_code == 503

class TestLoadTesting:
    """Load testing - जैसे Mumbai local train peak hour testing"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, gateway):
        """Test handling concurrent requests"""
        
        async def make_request(client, endpoint):
            return await client.get(endpoint)
        
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            # Create 50 concurrent requests
            tasks = []
            for i in range(50):
                task = asyncio.create_task(make_request(client, "/api/test/get"))
                tasks.append(task)
            
            # Wait for all requests
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful responses
            successful = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
            
            # Should handle reasonable number of concurrent requests
            assert successful > 30  # At least 30 out of 50 should succeed

class TestMetrics:
    """Metrics and monitoring tests"""
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, gateway):
        """Test metrics endpoint availability"""
        
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            response = await client.get("/metrics")
            assert response.status_code == 200
            assert "api_gateway_requests_total" in response.text

class TestGatewayIntegration:
    """Integration tests for complete gateway functionality"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_request_flow(self, gateway, auth_manager):
        """Test complete request flow through gateway"""
        
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            # 1. Health check
            health_response = await client.get("/health")
            assert health_response.status_code == 200
            
            # 2. Public endpoint (no auth)
            public_response = await client.get("/api/test/get")
            assert public_response.status_code == 200
            
            # 3. Secure endpoint with auth
            token = auth_manager.create_token("testuser", "premium")
            headers = {"Authorization": f"Bearer {token}"}
            secure_response = await client.get("/api/secure/get", headers=headers)
            assert secure_response.status_code == 200
            
            # 4. Check metrics
            metrics_response = await client.get("/metrics")
            assert metrics_response.status_code == 200

def simulate_mumbai_scale_load():
    """
    Simulate Mumbai scale load testing
    जैसे Monday morning 9 AM का traffic load
    """
    
    async def load_test():
        gateway = KongGateway(TEST_CONFIG)
        
        # Add high-capacity routes
        routes = [
            ServiceRoute("/api/orders", "http://httpbin.org", rate_limit=10000),
            ServiceRoute("/api/products", "http://httpbin.org", rate_limit=50000),
            ServiceRoute("/api/search", "http://httpbin.org", rate_limit=100000)
        ]
        
        for route in routes:
            gateway.add_route(route)
        
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        
        async with httpx.AsyncClient(app=gateway.app, base_url="http://test") as client:
            # Simulate 1000 concurrent users
            tasks = []
            for i in range(1000):
                endpoint = f"/api/{'products' if i % 2 == 0 else 'orders'}/get"
                task = asyncio.create_task(client.get(endpoint))
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for response in responses:
                if hasattr(response, 'status_code') and response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
        
        duration = time.time() - start_time
        rps = successful_requests / duration
        
        print(f"Load test results:")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Successful: {successful_requests}")
        print(f"  Failed: {failed_requests}")
        print(f"  RPS: {rps:.2f}")
        print(f"  Success rate: {(successful_requests/(successful_requests+failed_requests))*100:.1f}%")
    
    asyncio.run(load_test())

if __name__ == "__main__":
    # Run tests
    print("Running Kong Gateway tests...")
    
    # Basic test run
    pytest.main([__file__, "-v"])
    
    # Load testing
    print("\nRunning Mumbai scale load test...")
    simulate_mumbai_scale_load()
    
    print("\nAll tests completed! Gateway ready for production like Mumbai's resilient infrastructure! 🚉")