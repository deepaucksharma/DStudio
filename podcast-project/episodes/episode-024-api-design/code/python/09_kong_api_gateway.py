#!/usr/bin/env python3
"""
Kong API Gateway Configuration for Indian E-commerce
Kong Gateway setup for Flipkart-like microservices architecture

Key Features:
- Service registration और routing
- Rate limiting per customer
- Authentication और authorization
- Load balancing across Mumbai और Bangalore servers
- Circuit breaker pattern implementation

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns
"""

import requests
import json
import time
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KongAPIGateway:
    """
    Kong API Gateway manager for Indian microservices
    भारतीय e-commerce के लिए Kong gateway configuration
    """
    
    def __init__(self, kong_admin_url: str = "http://localhost:8001"):
        self.kong_admin_url = kong_admin_url
        self.headers = {"Content-Type": "application/json"}
        
    def create_service(self, service_name: str, service_url: str, description: str = ""):
        """
        Create a new service in Kong
        नई service Kong में register करते हैं
        """
        service_config = {
            "name": service_name,
            "url": service_url,
            "retries": 3,
            "connect_timeout": 60000,
            "write_timeout": 60000,
            "read_timeout": 60000,
            "tags": ["indian-ecommerce", "microservice"]
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/services",
                headers=self.headers,
                json=service_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Service '{service_name}' created successfully")
                return response.json()
            else:
                logger.error(f"❌ Failed to create service: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating service: {str(e)}")
            return None
    
    def create_route(self, service_name: str, route_path: str, methods: List[str] = ["GET", "POST"]):
        """
        Create route for service
        Service के लिए route बनाते हैं
        """
        route_config = {
            "paths": [route_path],
            "methods": methods,
            "strip_path": False,
            "preserve_host": True,
            "tags": ["api-route", "v1"]
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/services/{service_name}/routes",
                headers=self.headers,
                json=route_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Route '{route_path}' created for service '{service_name}'")
                return response.json()
            else:
                logger.error(f"❌ Failed to create route: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating route: {str(e)}")
            return None
    
    def add_rate_limiting(self, service_name: str, requests_per_minute: int = 100):
        """
        Add rate limiting plugin to service
        Service पर rate limiting लगाते हैं - Mumbai traffic जैसा control
        """
        rate_limit_config = {
            "name": "rate-limiting",
            "config": {
                "minute": requests_per_minute,
                "hour": requests_per_minute * 60,
                "policy": "local",
                "fault_tolerant": True,
                "hide_client_headers": False
            }
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/services/{service_name}/plugins",
                headers=self.headers,
                json=rate_limit_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Rate limiting enabled for '{service_name}': {requests_per_minute} req/min")
                return response.json()
            else:
                logger.error(f"❌ Failed to add rate limiting: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error adding rate limiting: {str(e)}")
            return None
    
    def add_jwt_authentication(self, service_name: str):
        """
        Add JWT authentication plugin
        JWT authentication लगाते हैं - Paytm जैसी security के लिए
        """
        jwt_config = {
            "name": "jwt",
            "config": {
                "uri_param_names": ["token"],
                "cookie_names": ["jwt"],
                "header_names": ["authorization"],
                "claims_to_verify": ["exp", "iss"],
                "key_claim_name": "iss",
                "secret_is_base64": False,
                "run_on_preflight": True
            }
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/services/{service_name}/plugins",
                headers=self.headers,
                json=jwt_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ JWT authentication enabled for '{service_name}'")
                return response.json()
            else:
                logger.error(f"❌ Failed to add JWT auth: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error adding JWT auth: {str(e)}")
            return None
    
    def add_cors_plugin(self, service_name: str):
        """
        Add CORS plugin for web applications
        Web apps के लिए CORS enable करते हैं
        """
        cors_config = {
            "name": "cors",
            "config": {
                "origins": ["*"],
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "headers": ["Accept", "Accept-Version", "Content-Length", "Content-MD5", 
                           "Content-Type", "Date", "X-Auth-Token", "Authorization"],
                "exposed_headers": ["X-Auth-Token"],
                "credentials": True,
                "max_age": 3600,
                "preflight_continue": False
            }
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/services/{service_name}/plugins",
                headers=self.headers,
                json=cors_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ CORS enabled for '{service_name}'")
                return response.json()
            else:
                logger.error(f"❌ Failed to add CORS: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error adding CORS: {str(e)}")
            return None
    
    def add_circuit_breaker(self, service_name: str, failure_threshold: int = 50):
        """
        Add circuit breaker plugin
        Circuit breaker pattern - Mumbai local train जैसा backup system
        """
        circuit_breaker_config = {
            "name": "http-circuit-breaker",
            "config": {
                "failure_threshold": failure_threshold,
                "recovery_timeout": 30,
                "failure_percentage_threshold": 75,
                "minimum_requests": 10,
                "break_on": [500, 502, 503, 504],
                "recovery_percentage_threshold": 25
            }
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/services/{service_name}/plugins",
                headers=self.headers,
                json=circuit_breaker_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Circuit breaker enabled for '{service_name}'")
                return response.json()
            else:
                logger.error(f"❌ Failed to add circuit breaker: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error adding circuit breaker: {str(e)}")
            return None
    
    def create_consumer(self, consumer_name: str, custom_id: str = None):
        """
        Create consumer for API access
        API access के लिए consumer बनाते हैं
        """
        consumer_config = {
            "username": consumer_name,
            "custom_id": custom_id or consumer_name,
            "tags": ["ecommerce-client", "production"]
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/consumers",
                headers=self.headers,
                json=consumer_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Consumer '{consumer_name}' created successfully")
                return response.json()
            else:
                logger.error(f"❌ Failed to create consumer: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating consumer: {str(e)}")
            return None
    
    def generate_jwt_credential(self, consumer_name: str, algorithm: str = "HS256"):
        """
        Generate JWT credentials for consumer
        Consumer के लिए JWT credentials generate करते हैं
        """
        jwt_credential_config = {
            "algorithm": algorithm,
            "rsa_public_key": None,
            "key": f"flipkart-api-{consumer_name}",
            "secret": f"flipkart-secret-{consumer_name}-{int(time.time())}"
        }
        
        try:
            response = requests.post(
                f"{self.kong_admin_url}/consumers/{consumer_name}/jwt",
                headers=self.headers,
                json=jwt_credential_config
            )
            
            if response.status_code == 201:
                logger.info(f"✅ JWT credentials generated for '{consumer_name}'")
                return response.json()
            else:
                logger.error(f"❌ Failed to generate JWT credentials: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating JWT credentials: {str(e)}")
            return None
    
    def get_service_health(self, service_name: str):
        """
        Check service health and metrics
        Service की health check करते हैं
        """
        try:
            # Get service details
            service_response = requests.get(
                f"{self.kong_admin_url}/services/{service_name}"
            )
            
            if service_response.status_code != 200:
                return {"status": "error", "message": "Service not found"}
            
            # Get service routes
            routes_response = requests.get(
                f"{self.kong_admin_url}/services/{service_name}/routes"
            )
            
            # Get service plugins
            plugins_response = requests.get(
                f"{self.kong_admin_url}/services/{service_name}/plugins"
            )
            
            service_data = service_response.json()
            routes_data = routes_response.json() if routes_response.status_code == 200 else {"data": []}
            plugins_data = plugins_response.json() if plugins_response.status_code == 200 else {"data": []}
            
            health_status = {
                "service_name": service_name,
                "service_url": service_data.get("url"),
                "total_routes": len(routes_data.get("data", [])),
                "total_plugins": len(plugins_data.get("data", [])),
                "plugins_enabled": [plugin["name"] for plugin in plugins_data.get("data", [])],
                "routes": [
                    {
                        "path": route.get("paths", []),
                        "methods": route.get("methods", [])
                    }
                    for route in routes_data.get("data", [])
                ],
                "timestamp": int(time.time()),
                "status": "healthy"
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking service health: {str(e)}")
            return {"status": "error", "message": str(e)}

def setup_flipkart_microservices():
    """
    Setup complete Flipkart-like microservices architecture
    Flipkart जैसा complete microservices setup करते हैं
    """
    gateway = KongAPIGateway()
    
    # Flipkart microservices configuration
    services_config = [
        {
            "name": "user-service",
            "url": "http://user-service:8080",
            "path": "/api/v1/users",
            "rate_limit": 200
        },
        {
            "name": "product-catalog",
            "url": "http://catalog-service:8080", 
            "path": "/api/v1/products",
            "rate_limit": 500
        },
        {
            "name": "cart-service",
            "url": "http://cart-service:8080",
            "path": "/api/v1/cart",
            "rate_limit": 300
        },
        {
            "name": "order-service",
            "url": "http://order-service:8080",
            "path": "/api/v1/orders", 
            "rate_limit": 150
        },
        {
            "name": "payment-service",
            "url": "http://payment-service:8080",
            "path": "/api/v1/payments",
            "rate_limit": 100
        },
        {
            "name": "inventory-service",
            "url": "http://inventory-service:8080",
            "path": "/api/v1/inventory",
            "rate_limit": 400
        }
    ]
    
    print("🏪 Setting up Flipkart-like microservices architecture...")
    print("=" * 60)
    
    for service_config in services_config:
        print(f"\n📦 Setting up {service_config['name']}...")
        
        # Create service
        service = gateway.create_service(
            service_config["name"],
            service_config["url"],
            f"Flipkart {service_config['name']} microservice"
        )
        
        if service:
            # Create route
            gateway.create_route(
                service_config["name"],
                service_config["path"]
            )
            
            # Add rate limiting
            gateway.add_rate_limiting(
                service_config["name"],
                service_config["rate_limit"]
            )
            
            # Add JWT authentication for sensitive services
            if service_config["name"] in ["user-service", "payment-service", "order-service"]:
                gateway.add_jwt_authentication(service_config["name"])
            
            # Add CORS for all services
            gateway.add_cors_plugin(service_config["name"])
            
            # Add circuit breaker for critical services
            if service_config["name"] in ["payment-service", "order-service", "inventory-service"]:
                gateway.add_circuit_breaker(service_config["name"])
            
            print(f"✅ {service_config['name']} setup completed!")
        else:
            print(f"❌ Failed to setup {service_config['name']}")
    
    # Create consumers for different client types
    print("\n👥 Creating API consumers...")
    consumers = [
        {"name": "flipkart-web-app", "id": "web-app-001"},
        {"name": "flipkart-mobile-app", "id": "mobile-app-001"}, 
        {"name": "flipkart-partner-api", "id": "partner-api-001"},
        {"name": "flipkart-admin-panel", "id": "admin-panel-001"}
    ]
    
    for consumer in consumers:
        consumer_obj = gateway.create_consumer(consumer["name"], consumer["id"])
        if consumer_obj:
            gateway.generate_jwt_credential(consumer["name"])
            print(f"✅ Consumer '{consumer['name']}' created with JWT credentials")
    
    print("\n🎉 Kong API Gateway setup completed!")
    print("📊 Health check all services:")
    
    # Health check all services
    for service_config in services_config:
        health = gateway.get_service_health(service_config["name"])
        print(f"  📈 {service_config['name']}: {health.get('status', 'unknown')}")

if __name__ == "__main__":
    print("🚀 Kong API Gateway Configuration for Indian E-commerce")
    print("🇮🇳 Flipkart-style microservices architecture setup")
    print("=" * 60)
    
    try:
        setup_flipkart_microservices()
        
        print("\n📋 Next Steps:")
        print("1. Start Kong Gateway: docker run -d --name kong kong:latest")
        print("2. Configure Kong Admin API: http://localhost:8001")
        print("3. Test API Gateway: http://localhost:8000")
        print("4. Monitor with Konga UI: docker run -d --name konga pantsel/konga")
        print("5. Set up service mesh integration for production")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        print("💡 Make sure Kong is running and accessible")