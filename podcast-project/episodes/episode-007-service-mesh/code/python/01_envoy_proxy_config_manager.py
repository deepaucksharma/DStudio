#!/usr/bin/env python3
"""
Envoy Proxy Configuration Manager
Mumbai Local Train Route Optimization System

Context: 
Paytm/PhonePe जैसे services के लिए Envoy proxy को dynamically configure करना
जैसे Mumbai local train routes को real-time optimize करते हैं traffic के हिसाब से

Author: Mumbai Service Mesh Team
"""

import json
import yaml
import time
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging

# Logging setup - Hindi comments के साथ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [हिंदी: %(name)s]',
    handlers=[
        logging.FileHandler('/var/log/envoy-config-manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EnvoyConfigManager')

@dataclass
class ServiceEndpoint:
    """
    Service endpoint representation
    जैसे Mumbai local train का station
    """
    host: str
    port: int
    weight: int = 100
    health_check_path: str = "/health"
    region: str = "mumbai"
    az: str = "west"
    
    def to_envoy_endpoint(self) -> Dict[str, Any]:
        """Convert to Envoy endpoint format"""
        return {
            "endpoint": {
                "address": {
                    "socket_address": {
                        "address": self.host,
                        "port_value": self.port
                    }
                }
            },
            "load_balancing_weight": self.weight,
            "metadata": {
                "filter_metadata": {
                    "envoy.lb": {
                        "region": self.region,
                        "az": self.az,
                        "canary": False  # Production traffic के लिए
                    }
                }
            }
        }

@dataclass  
class CircuitBreakerConfig:
    """
    Mumbai traffic signal की तरह circuit breaker
    Peak hours में automatic failover
    """
    max_connections: int = 100
    max_pending_requests: int = 50
    max_requests: int = 200
    max_retries: int = 3
    track_remaining: bool = True
    
    # Mumbai specific settings
    peak_hour_multiplier: float = 0.7  # Peak में कम traffic allow करें
    monsoon_factor: float = 0.8  # Monsoon में network issues के लिए

class EnvoyConfigManager:
    """
    Envoy Proxy Configuration Manager
    Mumbai traffic control room की तरह centralized control
    """
    
    def __init__(self, envoy_admin_url: str = "http://localhost:9901"):
        self.envoy_admin_url = envoy_admin_url
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        
        # Mumbai context - Peak hours definition
        self.peak_hours = [(7, 11), (17, 22)]  # Morning and evening rush
        
        logger.info("Mumbai Service Mesh Control initialized 🚂")
        logger.info("Peak hours configured: %s", self.peak_hours)
    
    def register_service(self, service_name: str, endpoints: List[ServiceEndpoint]):
        """
        Register service with endpoints
        जैसे नया train route add करना
        """
        self.services[service_name] = endpoints
        logger.info("Service registered: %s with %d endpoints", 
                   service_name, len(endpoints))
        
        # Auto-configure circuit breakers
        self._configure_circuit_breaker(service_name)
        
    def _configure_circuit_breaker(self, service_name: str):
        """Configure circuit breaker for service"""
        current_hour = time.localtime().tm_hour
        is_peak = any(start <= current_hour <= end for start, end in self.peak_hours)
        
        # Peak hours में conservative settings
        if is_peak:
            circuit_config = CircuitBreakerConfig(
                max_connections=70,  # Reduced during peak
                max_pending_requests=30,
                max_requests=140
            )
            logger.info("Peak hour circuit breaker configured for %s 🚦", service_name)
        else:
            circuit_config = CircuitBreakerConfig()
            
        self._apply_circuit_breaker(service_name, circuit_config)
    
    def _apply_circuit_breaker(self, service_name: str, config: CircuitBreakerConfig):
        """Apply circuit breaker configuration to Envoy"""
        circuit_breaker_config = {
            "thresholds": [
                {
                    "priority": "DEFAULT",
                    "max_connections": config.max_connections,
                    "max_pending_requests": config.max_pending_requests,
                    "max_requests": config.max_requests,
                    "max_retries": config.max_retries,
                    "track_remaining": config.track_remaining
                }
            ]
        }
        
        # Apply via Envoy admin API
        try:
            self._update_cluster_config(service_name, {
                "circuit_breakers": circuit_breaker_config
            })
            logger.info("Circuit breaker applied to %s", service_name)
        except Exception as e:
            logger.error("Failed to apply circuit breaker: %s", e)
    
    def generate_cluster_config(self, service_name: str) -> Dict[str, Any]:
        """
        Generate Envoy cluster configuration
        Mumbai local train cluster की तरह - multiple trains (instances)
        """
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not registered")
            
        endpoints = self.services[service_name]
        
        # Health check configuration - train status check की तरह  
        health_check = {
            "timeout": "5s",
            "interval": "10s",
            "unhealthy_threshold": 3,
            "healthy_threshold": 2,
            "path": "/health",
            "http_health_check": {
                "path": "/health",
                "request_headers_to_add": [
                    {
                        "header": {
                            "key": "x-health-check",
                            "value": "mumbai-mesh"
                        }
                    }
                ]
            }
        }
        
        # Load balancing - Mumbai traffic distribution strategy
        load_assignment = {
            "cluster_name": service_name,
            "endpoints": [
                {
                    "lb_endpoints": [ep.to_envoy_endpoint() for ep in endpoints]
                }
            ]
        }
        
        cluster_config = {
            "name": service_name,
            "type": "STRICT_DNS",  # DNS resolution for cloud services
            "lb_policy": "WEIGHTED_ROUND_ROBIN",  # Fair distribution
            "load_assignment": load_assignment,
            "health_checks": [health_check],
            
            # Connection pooling - Mumbai local train capacity management
            "circuit_breakers": {
                "thresholds": [
                    {
                        "priority": "DEFAULT",
                        "max_connections": 100,
                        "max_pending_requests": 50,
                        "max_requests": 200,
                        "max_retries": 3
                    }
                ]
            },
            
            # Outlier detection - Failed train (service) को temporarily remove करना
            "outlier_detection": {
                "consecutive_5xx": 5,
                "interval": "30s",
                "base_ejection_time": "30s",
                "max_ejection_percent": 50,
                "min_health_percent": 50
            },
            
            # Retry policy - Mumbai style jugaad
            "retry_policy": {
                "retry_on": "5xx,reset,connect-failure,refused-stream",
                "num_retries": 3,
                "per_try_timeout": "5s",
                "retry_back_off": {
                    "base_interval": "0.25s",
                    "max_interval": "2s"
                }
            }
        }
        
        return cluster_config
    
    def _update_cluster_config(self, service_name: str, config_update: Dict[str, Any]):
        """Update cluster configuration via Envoy admin API"""
        try:
            # Get current config
            response = requests.get(f"{self.envoy_admin_url}/config_dump")
            if response.status_code == 200:
                # Apply update via CDS (Cluster Discovery Service)
                update_url = f"{self.envoy_admin_url}/clusters/{service_name}"
                update_response = requests.post(
                    update_url,
                    json=config_update,
                    headers={'Content-Type': 'application/json'}
                )
                
                if update_response.status_code == 200:
                    logger.info("Cluster config updated for %s", service_name)
                else:
                    logger.error("Failed to update cluster: %d", update_response.status_code)
            
        except requests.RequestException as e:
            logger.error("Network error updating cluster config: %s", e)
    
    def handle_peak_traffic(self):
        """
        Handle Mumbai peak hour traffic
        Morning/Evening rush के time special configuration
        """
        current_hour = time.localtime().tm_hour
        is_peak = any(start <= current_hour <= end for start, end in self.peak_hours)
        
        if is_peak:
            logger.info("🚦 Peak hour detected - Applying traffic management")
            
            # All services के लिए conservative settings apply करें
            for service_name in self.services:
                self._configure_circuit_breaker(service_name)
                
                # Priority routing for critical services
                if service_name in ['payment-service', 'auth-service', 'upi-service']:
                    self._enable_priority_routing(service_name)
        
        return is_peak
    
    def _enable_priority_routing(self, service_name: str):
        """Enable priority routing for critical services"""
        logger.info("Enabling priority routing for critical service: %s", service_name)
        
        # Route configuration with priority
        route_config = {
            "route": {
                "priority": "HIGH",
                "timeout": "15s",  # Longer timeout for critical services
                "retry_policy": {
                    "retry_on": "5xx,reset,connect-failure",
                    "num_retries": 5  # More retries for critical services
                }
            }
        }
        
        # Apply via RDS (Route Discovery Service)
        try:
            self._update_route_config(service_name, route_config)
        except Exception as e:
            logger.error("Failed to enable priority routing: %s", e)
    
    def _update_route_config(self, service_name: str, route_config: Dict[str, Any]):
        """Update route configuration"""
        # Placeholder for route configuration update
        logger.info("Route config would be updated for %s", service_name)
    
    def monitor_service_health(self) -> Dict[str, Any]:
        """
        Monitor service health
        Mumbai local train status की तरह real-time monitoring
        """
        health_status = {}
        
        for service_name, endpoints in self.services.items():
            service_health = {
                'total_endpoints': len(endpoints),
                'healthy_endpoints': 0,
                'unhealthy_endpoints': 0,
                'endpoint_details': []
            }
            
            # Check each endpoint health
            for endpoint in endpoints:
                try:
                    health_url = f"http://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}"
                    response = requests.get(health_url, timeout=5)
                    
                    is_healthy = response.status_code == 200
                    
                    if is_healthy:
                        service_health['healthy_endpoints'] += 1
                    else:
                        service_health['unhealthy_endpoints'] += 1
                    
                    service_health['endpoint_details'].append({
                        'host': endpoint.host,
                        'port': endpoint.port,
                        'healthy': is_healthy,
                        'response_time_ms': response.elapsed.total_seconds() * 1000
                    })
                    
                except requests.RequestException as e:
                    service_health['unhealthy_endpoints'] += 1
                    service_health['endpoint_details'].append({
                        'host': endpoint.host,
                        'port': endpoint.port,
                        'healthy': False,
                        'error': str(e)
                    })
            
            health_status[service_name] = service_health
        
        return health_status
    
    def export_config_for_kubernetes(self, output_file: str):
        """
        Export configuration as Kubernetes ConfigMap
        Mumbai local train timetable की तरह - structured configuration
        """
        envoy_config = {
            'static_resources': {
                'clusters': []
            }
        }
        
        # Generate cluster configs for all services
        for service_name in self.services:
            cluster_config = self.generate_cluster_config(service_name)
            envoy_config['static_resources']['clusters'].append(cluster_config)
        
        # Create Kubernetes ConfigMap
        configmap = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': 'envoy-config',
                'namespace': 'istio-system',
                'labels': {
                    'app': 'envoy-proxy',
                    'version': 'mumbai-v1',
                    'context': 'service-mesh'
                }
            },
            'data': {
                'envoy.yaml': yaml.dump(envoy_config, default_flow_style=False)
            }
        }
        
        # Save to file
        with open(output_file, 'w') as f:
            yaml.dump(configmap, f, default_flow_style=False)
        
        logger.info("Kubernetes ConfigMap exported to %s", output_file)

def main():
    """
    Demo: Mumbai UPI Payment Service Mesh Setup
    Paytm/PhonePe जैसे high-scale services के लिए
    """
    print("🚂 Mumbai Service Mesh Configuration Manager")
    print("=" * 50)
    
    # Initialize manager
    config_manager = EnvoyConfigManager()
    
    # Register UPI payment service - Multiple zones for reliability
    payment_endpoints = [
        ServiceEndpoint("10.0.1.10", 8080, weight=100, region="mumbai", az="west"),
        ServiceEndpoint("10.0.1.11", 8080, weight=100, region="mumbai", az="west"), 
        ServiceEndpoint("10.0.2.10", 8080, weight=80, region="mumbai", az="east"),   # Lower weight for cross-zone
        ServiceEndpoint("10.0.3.10", 8080, weight=60, region="pune", az="west")     # DR instance
    ]
    
    config_manager.register_service("upi-payment-service", payment_endpoints)
    
    # Register order service
    order_endpoints = [
        ServiceEndpoint("10.0.1.20", 8081, weight=100, region="mumbai", az="west"),
        ServiceEndpoint("10.0.1.21", 8081, weight=100, region="mumbai", az="west"),
    ]
    
    config_manager.register_service("order-service", order_endpoints)
    
    # Handle peak traffic scenario
    is_peak = config_manager.handle_peak_traffic()
    print(f"Peak hour status: {'🚦 ACTIVE' if is_peak else '🟢 Normal'}")
    
    # Monitor health
    health_status = config_manager.monitor_service_health()
    print("\n📊 Service Health Status:")
    for service, health in health_status.items():
        total = health['total_endpoints'] 
        healthy = health['healthy_endpoints']
        print(f"  {service}: {healthy}/{total} healthy endpoints")
    
    # Export configuration
    config_manager.export_config_for_kubernetes("/tmp/envoy-mumbai-config.yaml")
    print("\n✅ Configuration exported for Kubernetes deployment")
    
    # Generate sample cluster config
    print("\n🔧 Sample UPI Service Cluster Configuration:")
    print(json.dumps(
        config_manager.generate_cluster_config("upi-payment-service"),
        indent=2
    ))

if __name__ == "__main__":
    main()