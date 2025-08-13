#!/usr/bin/env python3
"""
Kong API Gateway Management System
Gateway of India Digital Implementation

Context:
Paytm/Razorpay style API Gateway management for Indian fintech services
जैसे Gateway of India Mumbai का main entry point है, वैसे ही API Gateway

Features:
- Kong API configuration
- Service registration
- Plugin management
- Route optimization
- Indian financial compliance
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from urllib.parse import urljoin
import threading
from concurrent.futures import ThreadPoolExecutor

# Setup Mumbai-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [मुंबई-Gateway] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mumbai-api-gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MumbaiAPIGateway')

@dataclass
class ServiceConfig:
    """Service configuration for Kong"""
    name: str
    url: str
    host: str
    port: int
    protocol: str = "http"
    path: str = "/"
    retries: int = 5
    connect_timeout: int = 60000  # 60 seconds for Indian network
    write_timeout: int = 60000
    read_timeout: int = 60000
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class RouteConfig:
    """Route configuration for Kong"""
    name: str
    service_id: str
    protocols: List[str] = field(default_factory=lambda: ["http", "https"])
    methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    hosts: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    strip_path: bool = True
    preserve_host: bool = False
    tags: List[str] = field(default_factory=list)

@dataclass  
class PluginConfig:
    """Plugin configuration for Kong"""
    name: str
    service_id: Optional[str] = None
    route_id: Optional[str] = None
    consumer_id: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    protocols: List[str] = field(default_factory=lambda: ["grpc", "grpcs", "http", "https"])
    enabled: bool = True
    tags: List[str] = field(default_factory=list)

@dataclass
class ConsumerConfig:
    """Consumer configuration for Kong"""
    username: str
    custom_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    # Indian user context
    metadata: Dict[str, str] = field(default_factory=dict)

class MumbaiKongManager:
    """
    Kong API Gateway Manager
    Mumbai Gateway of India style API management
    """
    
    def __init__(self, kong_admin_url: str = "http://localhost:8001"):
        self.kong_admin_url = kong_admin_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mumbai-Gateway-Manager/1.0'
        })
        
        # Mumbai context - Indian financial services
        self.indian_services = {
            'upi-payment': 'UPI Payment Service',
            'bank-integration': 'Bank Integration Service', 
            'kyc-verification': 'KYC Verification Service',
            'wallet-service': 'Digital Wallet Service'
        }
        
        # Compliance settings for Indian fintech
        self.compliance_plugins = [
            'rate-limiting',  # RBI transaction limits
            'jwt',           # Strong authentication
            'cors',          # Web/mobile app support
            'request-transformer',  # Add compliance headers
            'response-transformer', # Remove sensitive data
            'prometheus',    # Monitoring for compliance
            'acl'           # Access control lists
        ]
        
        # Test connection
        self._test_connection()
        
        logger.info("🏛️ Mumbai Kong API Gateway Manager initialized")
        logger.info("Admin URL: %s", kong_admin_url)
    
    def _test_connection(self):
        """Test connection to Kong Admin API"""
        try:
            response = self.session.get(f"{self.kong_admin_url}/status")
            response.raise_for_status()
            
            status = response.json()
            logger.info("✅ Connected to Kong Gateway")
            logger.info("Kong version: %s", status.get('version', 'unknown'))
            
        except requests.RequestException as e:
            logger.error("❌ Failed to connect to Kong Admin API: %s", e)
            raise
    
    def create_service(self, service_config: ServiceConfig) -> Dict[str, Any]:
        """
        Create service in Kong
        Register new service like registering at Gateway of India
        """
        logger.info("🏗️ Creating service: %s", service_config.name)
        
        # Prepare service data with Mumbai context
        service_data = {
            "name": service_config.name,
            "url": service_config.url,
            "protocol": service_config.protocol,
            "host": service_config.host,
            "port": service_config.port,
            "path": service_config.path,
            "retries": service_config.retries,
            "connect_timeout": service_config.connect_timeout,
            "write_timeout": service_config.write_timeout,
            "read_timeout": service_config.read_timeout,
            "tags": service_config.tags + ["mumbai", "india", "production"]
        }
        
        # Add Indian compliance metadata
        if service_config.name in self.indian_services:
            service_data["tags"].extend(["financial", "rbi-compliant"])
        
        try:
            response = self.session.post(
                f"{self.kong_admin_url}/services",
                json=service_data
            )
            response.raise_for_status()
            
            service = response.json()
            logger.info("✅ Service created: %s (ID: %s)", service_config.name, service["id"])
            
            return service
            
        except requests.RequestException as e:
            logger.error("❌ Failed to create service %s: %s", service_config.name, e)
            raise
    
    def create_route(self, route_config: RouteConfig) -> Dict[str, Any]:
        """
        Create route in Kong
        Setup traffic route like Mumbai traffic routing
        """
        logger.info("🛣️ Creating route: %s", route_config.name)
        
        route_data = {
            "name": route_config.name,
            "protocols": route_config.protocols,
            "methods": route_config.methods,
            "hosts": route_config.hosts,
            "paths": route_config.paths,
            "strip_path": route_config.strip_path,
            "preserve_host": route_config.preserve_host,
            "tags": route_config.tags + ["mumbai", "api-route"]
        }
        
        try:
            # Create route for specific service
            response = self.session.post(
                f"{self.kong_admin_url}/services/{route_config.service_id}/routes",
                json=route_data
            )
            response.raise_for_status()
            
            route = response.json()
            logger.info("✅ Route created: %s (ID: %s)", route_config.name, route["id"])
            
            return route
            
        except requests.RequestException as e:
            logger.error("❌ Failed to create route %s: %s", route_config.name, e)
            raise
    
    def add_plugin(self, plugin_config: PluginConfig) -> Dict[str, Any]:
        """
        Add plugin to Kong
        Add security/functionality like Mumbai traffic management
        """
        logger.info("🔌 Adding plugin: %s", plugin_config.name)
        
        plugin_data = {
            "name": plugin_config.name,
            "config": plugin_config.config,
            "protocols": plugin_config.protocols,
            "enabled": plugin_config.enabled,
            "tags": plugin_config.tags + ["mumbai", "plugin"]
        }
        
        # Determine plugin scope URL
        url_path = "/plugins"
        
        if plugin_config.service_id:
            url_path = f"/services/{plugin_config.service_id}/plugins"
        elif plugin_config.route_id:
            url_path = f"/routes/{plugin_config.route_id}/plugins"
        elif plugin_config.consumer_id:
            url_path = f"/consumers/{plugin_config.consumer_id}/plugins"
        
        try:
            response = self.session.post(
                f"{self.kong_admin_url}{url_path}",
                json=plugin_data
            )
            response.raise_for_status()
            
            plugin = response.json()
            logger.info("✅ Plugin added: %s (ID: %s)", plugin_config.name, plugin["id"])
            
            return plugin
            
        except requests.RequestException as e:
            logger.error("❌ Failed to add plugin %s: %s", plugin_config.name, e)
            raise
    
    def create_consumer(self, consumer_config: ConsumerConfig) -> Dict[str, Any]:
        """
        Create consumer in Kong
        Register API user like visitor registration at Gateway of India
        """
        logger.info("👤 Creating consumer: %s", consumer_config.username)
        
        consumer_data = {
            "username": consumer_config.username,
            "tags": consumer_config.tags + ["mumbai", "api-user"]
        }
        
        if consumer_config.custom_id:
            consumer_data["custom_id"] = consumer_config.custom_id
        
        try:
            response = self.session.post(
                f"{self.kong_admin_url}/consumers",
                json=consumer_data
            )
            response.raise_for_status()
            
            consumer = response.json()
            logger.info("✅ Consumer created: %s (ID: %s)", 
                       consumer_config.username, consumer["id"])
            
            return consumer
            
        except requests.RequestException as e:
            logger.error("❌ Failed to create consumer %s: %s", 
                        consumer_config.username, e)
            raise
    
    def setup_upi_payment_api(self) -> Dict[str, Any]:
        """
        Setup UPI payment API with Indian compliance
        Mumbai-style financial service configuration
        """
        logger.info("💳 Setting up UPI Payment API with Indian compliance")
        
        # Create UPI service
        upi_service_config = ServiceConfig(
            name="upi-payment-service",
            url="http://upi-backend.mumbai.svc.cluster.local:8080",
            host="upi-backend.mumbai.svc.cluster.local",
            port=8080,
            protocol="http",
            path="/",
            retries=3,  # Less retries for financial transactions
            connect_timeout=30000,  # 30 seconds for UPI
            write_timeout=30000,
            read_timeout=30000,
            tags=["upi", "financial", "rbi-compliant"],
            metadata={
                "service_type": "payment",
                "compliance": "rbi",
                "region": "india"
            }
        )
        
        service = self.create_service(upi_service_config)
        
        # Create UPI routes
        upi_route_config = RouteConfig(
            name="upi-payment-routes",
            service_id=service["id"],
            protocols=["https"],  # HTTPS only for payments
            methods=["POST"],     # Only POST for UPI transactions
            hosts=["payments.mumbai-gateway.com"],
            paths=["/api/upi", "/api/v1/upi"],
            strip_path=True,
            preserve_host=False,
            tags=["upi", "secure", "financial"]
        )
        
        route = self.create_route(upi_route_config)
        
        # Add rate limiting for UPI (RBI guidelines)
        rate_limit_plugin = PluginConfig(
            name="rate-limiting",
            service_id=service["id"],
            config={
                "minute": 20,      # Max 20 UPI transactions per minute
                "hour": 100,       # Max 100 per hour
                "day": 1000,       # Max 1000 per day (RBI limit)
                "policy": "redis", # Distributed rate limiting
                "redis_host": "redis.mumbai-gateway.svc.cluster.local",
                "redis_port": 6379,
                "redis_password": "mumbai123",
                "redis_timeout": 2000,
                "fault_tolerant": True,
                "hide_client_headers": False
            }
        )
        
        self.add_plugin(rate_limit_plugin)
        
        # Add JWT authentication (mandatory for UPI)
        jwt_plugin = PluginConfig(
            name="jwt",
            service_id=service["id"],
            config={
                "claims_to_verify": ["exp", "aud", "sub"],
                "key_claim_name": "iss",
                "secret_is_base64": False,
                "maximum_expiration": 3600,  # 1 hour max for UPI
                "algorithm": "HS256",
                "header_names": ["Authorization"],
                "cookie_names": ["jwt-token"]
            }
        )
        
        self.add_plugin(jwt_plugin)
        
        # Add request transformer for Indian compliance
        request_transformer = PluginConfig(
            name="request-transformer",
            service_id=service["id"],
            config={
                "add": {
                    "headers": [
                        "X-Country:IN",
                        "X-Currency:INR", 
                        "X-Gateway:Mumbai-Digital-Gateway",
                        "X-Compliance:RBI-UPI",
                        "X-Request-Time:" + datetime.now().isoformat()
                    ]
                },
                "remove": {
                    "headers": ["X-Internal-Debug"]
                }
            }
        )
        
        self.add_plugin(request_transformer)
        
        # Add response transformer
        response_transformer = PluginConfig(
            name="response-transformer",
            service_id=service["id"],
            config={
                "add": {
                    "headers": [
                        "X-Processed-By:Mumbai-Gateway",
                        "X-RBI-Compliant:true"
                    ],
                    "json": [
                        "gateway_info.location:Mumbai",
                        "gateway_info.compliance:RBI-UPI"
                    ]
                },
                "remove": {
                    "headers": ["Server", "X-Powered-By"],
                    "json": ["internal_trace_id", "debug_info"]
                }
            }
        )
        
        self.add_plugin(response_transformer)
        
        logger.info("✅ UPI Payment API configured with RBI compliance")
        
        return {
            "service": service,
            "route": route,
            "compliance": "RBI-UPI",
            "rate_limits": "20/min, 100/hr, 1000/day"
        }
    
    def setup_general_api_gateway(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Setup general API gateway for Mumbai-style applications
        Comprehensive gateway setup for Indian services
        """
        logger.info("🏛️ Setting up comprehensive Mumbai API Gateway")
        
        results = {
            "services": [],
            "routes": [],
            "plugins": [],
            "consumers": []
        }
        
        # Define Mumbai services (Zomato/Swiggy style)
        mumbai_services = [
            {
                "name": "order-service",
                "host": "order-backend.mumbai.svc.cluster.local",
                "port": 8080,
                "paths": ["/api/orders", "/api/v1/orders"]
            },
            {
                "name": "restaurant-service", 
                "host": "restaurant-backend.mumbai.svc.cluster.local",
                "port": 8080,
                "paths": ["/api/restaurants", "/api/v1/restaurants"]
            },
            {
                "name": "user-service",
                "host": "user-backend.mumbai.svc.cluster.local", 
                "port": 8080,
                "paths": ["/api/users", "/api/v1/users"]
            },
            {
                "name": "notification-service",
                "host": "notification-backend.mumbai.svc.cluster.local",
                "port": 8080,
                "paths": ["/api/notifications", "/api/v1/notifications"]
            }
        ]
        
        # Create services and routes
        for svc_config in mumbai_services:
            # Create service
            service_config = ServiceConfig(
                name=svc_config["name"],
                url=f"http://{svc_config['host']}:{svc_config['port']}",
                host=svc_config["host"],
                port=svc_config["port"],
                protocol="http",
                retries=5,
                connect_timeout=60000,
                write_timeout=60000,
                read_timeout=60000,
                tags=["mumbai", "microservice", "production"]
            )
            
            service = self.create_service(service_config)
            results["services"].append(service)
            
            # Create routes
            route_config = RouteConfig(
                name=f"{svc_config['name']}-routes",
                service_id=service["id"],
                protocols=["http", "https"],
                methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                hosts=["api.mumbai-gateway.com"],
                paths=svc_config["paths"],
                strip_path=True,
                tags=["api-route", "mumbai"]
            )
            
            route = self.create_route(route_config)
            results["routes"].append(route)
            
            # Add common plugins to each service
            
            # CORS for web/mobile apps
            cors_plugin = PluginConfig(
                name="cors",
                service_id=service["id"],
                config={
                    "origins": [
                        "*.mumbai-app.com",
                        "*.zomato.com",
                        "*.swiggy.com", 
                        "localhost:*",
                        "http://localhost:*",
                        "https://localhost:*"
                    ],
                    "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                    "headers": [
                        "Accept", "Accept-Version", "Content-Length",
                        "Content-MD5", "Content-Type", "Date", "X-Auth-Token",
                        "Authorization", "X-User-ID", "X-Request-ID"
                    ],
                    "exposed_headers": ["X-Auth-Token", "X-Request-ID"],
                    "credentials": True,
                    "max_age": 3600
                }
            )
            
            cors_result = self.add_plugin(cors_plugin)
            results["plugins"].append(cors_result)
            
            # Rate limiting (generous for general APIs)
            rate_limit_plugin = PluginConfig(
                name="rate-limiting",
                service_id=service["id"],
                config={
                    "minute": 100,     # 100 requests per minute
                    "hour": 1000,      # 1000 requests per hour  
                    "policy": "local", # Local policy for general APIs
                    "fault_tolerant": True,
                    "hide_client_headers": False
                }
            )
            
            rate_result = self.add_plugin(rate_limit_plugin)
            results["plugins"].append(rate_result)
            
            # Add Prometheus monitoring
            prometheus_plugin = PluginConfig(
                name="prometheus",
                service_id=service["id"],
                config={
                    "per_consumer": True,
                    "status_code_metrics": True,
                    "latency_metrics": True,
                    "bandwidth_metrics": True,
                    "upstream_health_metrics": True
                }
            )
            
            prom_result = self.add_plugin(prometheus_plugin)
            results["plugins"].append(prom_result)
        
        # Create sample consumers
        mumbai_consumers = [
            {"username": "zomato-web-app", "custom_id": "zomato-001"},
            {"username": "swiggy-mobile-app", "custom_id": "swiggy-001"},
            {"username": "internal-dashboard", "custom_id": "internal-001"},
            {"username": "partner-api", "custom_id": "partner-001"}
        ]
        
        for consumer_data in mumbai_consumers:
            consumer_config = ConsumerConfig(
                username=consumer_data["username"],
                custom_id=consumer_data["custom_id"],
                tags=["mumbai", "api-consumer", "production"]
            )
            
            consumer = self.create_consumer(consumer_config)
            results["consumers"].append(consumer)
        
        logger.info("✅ Mumbai API Gateway setup completed")
        logger.info("Created: %d services, %d routes, %d plugins, %d consumers",
                   len(results["services"]), len(results["routes"]),
                   len(results["plugins"]), len(results["consumers"]))
        
        return results
    
    def get_gateway_status(self) -> Dict[str, Any]:
        """
        Get comprehensive gateway status
        Mumbai traffic control dashboard style
        """
        try:
            # Get Kong status
            status_response = self.session.get(f"{self.kong_admin_url}/status")
            status_response.raise_for_status()
            kong_status = status_response.json()
            
            # Get services count
            services_response = self.session.get(f"{self.kong_admin_url}/services")
            services_response.raise_for_status()
            services_count = len(services_response.json().get("data", []))
            
            # Get routes count
            routes_response = self.session.get(f"{self.kong_admin_url}/routes")
            routes_response.raise_for_status()
            routes_count = len(routes_response.json().get("data", []))
            
            # Get plugins count
            plugins_response = self.session.get(f"{self.kong_admin_url}/plugins")
            plugins_response.raise_for_status()
            plugins_count = len(plugins_response.json().get("data", []))
            
            # Get consumers count
            consumers_response = self.session.get(f"{self.kong_admin_url}/consumers")
            consumers_response.raise_for_status()
            consumers_count = len(consumers_response.json().get("data", []))
            
            return {
                "status": "healthy",
                "gateway_info": {
                    "location": "Mumbai",
                    "type": "Digital Gateway of India",
                    "kong_version": kong_status.get("version", "unknown")
                },
                "database": kong_status.get("database", {}),
                "configuration": {
                    "services": services_count,
                    "routes": routes_count,
                    "plugins": plugins_count,
                    "consumers": consumers_count
                },
                "compliance": {
                    "rbi_compliant": True,
                    "data_residency": "India",
                    "encryption": "TLS 1.3"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error("❌ Failed to get gateway status: %s", e)
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def health_check_services(self) -> Dict[str, Any]:
        """
        Health check all registered services
        Mumbai traffic monitoring system style
        """
        try:
            services_response = self.session.get(f"{self.kong_admin_url}/services")
            services_response.raise_for_status()
            services = services_response.json().get("data", [])
            
            health_results = []
            
            for service in services:
                service_name = service["name"]
                service_host = service["host"]
                service_port = service["port"]
                
                # Check service health
                try:
                    health_url = f"http://{service_host}:{service_port}/health"
                    health_response = requests.get(health_url, timeout=5)
                    
                    health_status = {
                        "service_name": service_name,
                        "service_id": service["id"],
                        "host": service_host,
                        "port": service_port,
                        "healthy": health_response.status_code == 200,
                        "response_time_ms": health_response.elapsed.total_seconds() * 1000,
                        "status_code": health_response.status_code
                    }
                    
                except requests.RequestException as e:
                    health_status = {
                        "service_name": service_name,
                        "service_id": service["id"],
                        "host": service_host,
                        "port": service_port,
                        "healthy": False,
                        "error": str(e)
                    }
                
                health_results.append(health_status)
            
            healthy_count = sum(1 for h in health_results if h.get("healthy", False))
            total_count = len(health_results)
            
            return {
                "overall_health": "healthy" if healthy_count == total_count else "degraded",
                "healthy_services": healthy_count,
                "total_services": total_count,
                "health_percentage": (healthy_count / total_count * 100) if total_count > 0 else 100,
                "services": health_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error("❌ Failed to check service health: %s", e)
            return {
                "overall_health": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

def main():
    """
    Demo: Mumbai API Gateway Setup
    Complete Gateway of India style API management
    """
    print("🏛️ Mumbai API Gateway Management System")
    print("=" * 55)
    
    # Initialize Kong manager
    kong_manager = MumbaiKongManager()
    
    # Setup UPI Payment API with RBI compliance
    print("\n💳 Setting up UPI Payment API...")
    upi_setup = kong_manager.setup_upi_payment_api()
    print(f"✅ UPI API configured with {upi_setup['compliance']} compliance")
    print(f"   Rate limits: {upi_setup['rate_limits']}")
    
    # Setup general API gateway
    print("\n🌐 Setting up general API gateway...")
    gateway_setup = kong_manager.setup_general_api_gateway()
    
    services_count = len(gateway_setup["services"])
    routes_count = len(gateway_setup["routes"])
    plugins_count = len(gateway_setup["plugins"])
    consumers_count = len(gateway_setup["consumers"])
    
    print(f"✅ Gateway setup completed:")
    print(f"   Services: {services_count}")
    print(f"   Routes: {routes_count}")
    print(f"   Plugins: {plugins_count}")
    print(f"   Consumers: {consumers_count}")
    
    # Check gateway status
    print("\n📊 Gateway Status:")
    status = kong_manager.get_gateway_status()
    
    if status["status"] == "healthy":
        print("✅ Gateway is healthy")
        print(f"   Kong Version: {status['gateway_info']['kong_version']}")
        print(f"   Database: Connected")
        print(f"   Services: {status['configuration']['services']}")
        print(f"   Routes: {status['configuration']['routes']}")
        print(f"   Plugins: {status['configuration']['plugins']}")
        print(f"   Consumers: {status['configuration']['consumers']}")
        print(f"   Compliance: RBI Compliant ✅")
    else:
        print("❌ Gateway is unhealthy")
        print(f"   Error: {status.get('error')}")
    
    # Health check services
    print("\n🏥 Service Health Check:")
    health_check = kong_manager.health_check_services()
    
    print(f"Overall Health: {health_check['overall_health'].upper()}")
    print(f"Healthy Services: {health_check.get('healthy_services', 0)}/{health_check.get('total_services', 0)}")
    
    if 'services' in health_check:
        for service_health in health_check['services'][:5]:  # Show first 5
            status_emoji = "✅" if service_health.get('healthy') else "❌"
            service_name = service_health['service_name']
            
            if service_health.get('healthy'):
                response_time = service_health.get('response_time_ms', 0)
                print(f"   {status_emoji} {service_name}: {response_time:.0f}ms")
            else:
                print(f"   {status_emoji} {service_name}: Unhealthy")
    
    print(f"\n🚀 Mumbai Digital Gateway is ready!")
    print(f"🌐 Admin UI: http://localhost:8002")
    print(f"📊 Metrics: http://localhost:8001/metrics")
    print(f"🔍 Status: http://localhost:8001/status")

if __name__ == "__main__":
    main()