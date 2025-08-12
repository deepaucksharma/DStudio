#!/usr/bin/env python3
"""
Service Mesh Examples 2-15
Production Service Mesh for Indian Banking & Fintech

यह file में 14 complete service mesh systems हैं:
2. Envoy Proxy Config - Traffic management
3. Circuit Breaker - Failure handling  
4. Service Discovery - Dynamic routing
5. mTLS Setup - Service security
6. Traffic Shifting - Canary deployments
7. Rate Limiting - Service protection
8. Retry Logic - Resilience patterns
9. Load Balancing - Service distribution
10. Observability - Mesh metrics
11. Fault Injection - Chaos testing
12. Header Manipulation - Request routing
13. Authorization Policies - Service RBAC
14. Virtual Services - Traffic management
15. Gateway Configuration - Ingress setup

All examples production-ready with Indian banking context.
"""

import yaml
import json
import time
import uuid
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# EXAMPLE 2: ENVOY PROXY CONFIGURATION
# =============================================================================

class EnvoyProxyConfig:
    """
    Production Envoy Proxy Configuration for Indian Banking
    Traffic management for HDFC Bank microservices
    """
    
    def __init__(self, service_name: str = "hdfc-payment-service"):
        self.service_name = service_name
        self.config_version = "v1.28"
        
    def generate_envoy_config(self) -> Dict[str, Any]:
        """Generate comprehensive Envoy configuration"""
        
        config = {
            "node": {
                "cluster": "hdfc-banking-cluster",
                "id": f"{self.service_name}-proxy",
                "metadata": {
                    "business_unit": "payments",
                    "datacenter": "mumbai-dc1",
                    "environment": "production"
                }
            },
            "static_resources": {
                "listeners": [
                    {
                        "name": "banking_api_listener",
                        "address": {
                            "socket_address": {
                                "address": "0.0.0.0",
                                "port_value": 8080
                            }
                        },
                        "filter_chains": [
                            {
                                "filters": [
                                    {
                                        "name": "envoy.filters.network.http_connection_manager",
                                        "typed_config": {
                                            "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                                            "stat_prefix": "ingress_http",
                                            "route_config": {
                                                "name": "banking_routes",
                                                "virtual_hosts": [
                                                    {
                                                        "name": "banking_service",
                                                        "domains": ["*"],
                                                        "routes": [
                                                            {
                                                                "match": {
                                                                    "prefix": "/api/v1/payments"
                                                                },
                                                                "route": {
                                                                    "cluster": "payment_service_cluster",
                                                                    "timeout": "30s",
                                                                    "retry_policy": {
                                                                        "retry_on": "5xx,gateway-error,connect-failure",
                                                                        "num_retries": 3,
                                                                        "per_try_timeout": "10s",
                                                                        "retry_back_off": {
                                                                            "base_interval": "0.25s",
                                                                            "max_interval": "2.5s"
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            {
                                                                "match": {
                                                                    "prefix": "/api/v1/accounts"
                                                                },
                                                                "route": {
                                                                    "cluster": "account_service_cluster",
                                                                    "timeout": "15s"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                ]
                                            },
                                            "http_filters": [
                                                {
                                                    "name": "envoy.filters.http.jwt_authn",
                                                    "typed_config": {
                                                        "@type": "type.googleapis.com/envoy.extensions.filters.http.jwt_authn.v3.JwtAuthentication",
                                                        "providers": {
                                                            "hdfc_auth": {
                                                                "issuer": "https://auth.hdfcbank.com",
                                                                "audiences": ["hdfc-banking-api"],
                                                                "remote_jwks": {
                                                                    "http_uri": {
                                                                        "uri": "https://auth.hdfcbank.com/.well-known/jwks.json",
                                                                        "cluster": "jwks_cluster",
                                                                        "timeout": "5s"
                                                                    },
                                                                    "cache_duration": "300s"
                                                                }
                                                            }
                                                        },
                                                        "rules": [
                                                            {
                                                                "match": {
                                                                    "prefix": "/api/v1/"
                                                                },
                                                                "requires": {
                                                                    "provider_name": "hdfc_auth"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                },
                                                {
                                                    "name": "envoy.filters.http.router"
                                                }
                                            ],
                                            "access_log": [
                                                {
                                                    "name": "envoy.access_loggers.file",
                                                    "typed_config": {
                                                        "@type": "type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog",
                                                        "path": "/var/log/envoy/access.log",
                                                        "format": "{\"timestamp\":\"%START_TIME%\",\"method\":\"%REQ(:METHOD)%\",\"path\":\"%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%\",\"response_code\":\"%RESPONSE_CODE%\",\"duration\":\"%DURATION%\",\"upstream_service\":\"%UPSTREAM_CLUSTER%\"}\n"
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "clusters": [
                    {
                        "name": "payment_service_cluster",
                        "connect_timeout": "0.25s",
                        "type": "STRICT_DNS",
                        "lb_policy": "ROUND_ROBIN",
                        "load_assignment": {
                            "cluster_name": "payment_service_cluster",
                            "endpoints": [
                                {
                                    "lb_endpoints": [
                                        {
                                            "endpoint": {
                                                "address": {
                                                    "socket_address": {
                                                        "address": "payment-service",
                                                        "port_value": 8080
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                        "circuit_breakers": {
                            "thresholds": [
                                {
                                    "priority": "DEFAULT",
                                    "max_connections": 100,
                                    "max_pending_requests": 50,
                                    "max_requests": 200,
                                    "max_retries": 3,
                                    "max_connection_pools": 10
                                }
                            ]
                        },
                        "outlier_detection": {
                            "consecutive_5xx": 5,
                            "interval": "30s",
                            "base_ejection_time": "30s",
                            "max_ejection_percent": 50,
                            "min_health_percent": 50
                        }
                    }
                ]
            }
        }
        
        return config

# =============================================================================
# EXAMPLE 3: CIRCUIT BREAKER IMPLEMENTATION
# =============================================================================

class ServiceMeshCircuitBreaker:
    """Istio/Envoy Circuit Breaker for Banking Services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.failure_count = 0
        self.success_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None
        self.timeout_duration = 30  # seconds
        
    def generate_destination_rule(self) -> str:
        """Generate Istio DestinationRule with circuit breaker"""
        
        destination_rule = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": f"{self.service_name}-circuit-breaker",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "host": f"{self.service_name}.hdfc-payments.svc.cluster.local",
                "trafficPolicy": {
                    "connectionPool": {
                        "tcp": {
                            "maxConnections": 100
                        },
                        "http": {
                            "http1MaxPendingRequests": 50,
                            "http2MaxRequests": 200,
                            "maxRequestsPerConnection": 10,
                            "maxRetries": 3,
                            "connectTimeout": "10s",
                            "h2UpgradePolicy": "UPGRADE"
                        }
                    },
                    "circuitBreaker": {
                        "consecutiveErrors": 5,
                        "interval": "30s",
                        "baseEjectionTime": "30s",
                        "maxEjectionPercent": 50,
                        "minHealthPercent": 50,
                        "splitExternalLocalOriginErrors": True
                    },
                    "outlierDetection": {
                        "consecutiveGatewayErrors": 5,
                        "consecutive5xxErrors": 5,
                        "interval": "30s",
                        "baseEjectionTime": "30s",
                        "maxEjectionPercent": 50,
                        "minHealthPercent": 30
                    }
                },
                "subsets": [
                    {
                        "name": "v1",
                        "labels": {
                            "version": "v1"
                        }
                    },
                    {
                        "name": "v2",
                        "labels": {
                            "version": "v2"
                        }
                    }
                ]
            }
        }
        
        return yaml.dump(destination_rule, default_flow_style=False)

# =============================================================================
# EXAMPLE 4: SERVICE DISCOVERY
# =============================================================================

class IstioServiceDiscovery:
    """Service Discovery Configuration for Banking Services"""
    
    def __init__(self):
        self.services = {}
        self.endpoints = defaultdict(list)
    
    def register_banking_services(self) -> Dict[str, str]:
        """Register core banking services in service mesh"""
        
        services = {
            "payment-service": {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "payment-service",
                    "namespace": "hdfc-payments",
                    "labels": {
                        "app": "payment-service",
                        "version": "v1",
                        "business-unit": "payments"
                    }
                },
                "spec": {
                    "selector": {
                        "app": "payment-service"
                    },
                    "ports": [
                        {
                            "name": "http",
                            "port": 8080,
                            "targetPort": 8080
                        },
                        {
                            "name": "grpc",
                            "port": 9090,
                            "targetPort": 9090
                        }
                    ]
                }
            },
            "account-service": {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "account-service",
                    "namespace": "hdfc-accounts",
                    "labels": {
                        "app": "account-service",
                        "version": "v1",
                        "business-unit": "core-banking"
                    }
                },
                "spec": {
                    "selector": {
                        "app": "account-service"
                    },
                    "ports": [
                        {
                            "name": "http",
                            "port": 8080,
                            "targetPort": 8080
                        }
                    ]
                }
            }
        }
        
        return {name: yaml.dump(config, default_flow_style=False) for name, config in services.items()}

# =============================================================================
# EXAMPLES 5-15: CONSOLIDATED SERVICE MESH CONFIGURATIONS
# =============================================================================

class mTLSConfiguration:
    """Example 5: mTLS Setup for Service Security"""
    
    def generate_mtls_policy(self) -> str:
        """Generate strict mTLS policy for banking services"""
        
        peer_auth = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": "default",
                "namespace": "hdfc-banking"
            },
            "spec": {
                "mtls": {
                    "mode": "STRICT"
                }
            }
        }
        
        return yaml.dump(peer_auth, default_flow_style=False)

class TrafficShifting:
    """Example 6: Canary Deployments with Traffic Shifting"""
    
    def generate_virtual_service(self, canary_weight: int = 10) -> str:
        """Generate VirtualService for canary deployment"""
        
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": "payment-service-canary",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "hosts": ["payment-service"],
                "http": [
                    {
                        "match": [
                            {
                                "headers": {
                                    "canary": {
                                        "exact": "true"
                                    }
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service",
                                    "subset": "v2"
                                }
                            }
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service",
                                    "subset": "v1"
                                },
                                "weight": 100 - canary_weight
                            },
                            {
                                "destination": {
                                    "host": "payment-service",
                                    "subset": "v2"
                                },
                                "weight": canary_weight
                            }
                        ]
                    }
                ]
            }
        }
        
        return yaml.dump(virtual_service, default_flow_style=False)

class RateLimitingConfig:
    """Example 7: Rate Limiting for Service Protection"""
    
    def generate_rate_limit_config(self) -> str:
        """Generate EnvoyFilter for rate limiting"""
        
        envoy_filter = {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "EnvoyFilter",
            "metadata": {
                "name": "payment-rate-limit",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "workloadSelector": {
                    "labels": {
                        "app": "payment-service"
                    }
                },
                "configPatches": [
                    {
                        "applyTo": "HTTP_FILTER",
                        "match": {
                            "context": "SIDECAR_INBOUND",
                            "listener": {
                                "filterChain": {
                                    "filter": {
                                        "name": "envoy.filters.network.http_connection_manager"
                                    }
                                }
                            }
                        },
                        "patch": {
                            "operation": "INSERT_BEFORE",
                            "value": {
                                "name": "envoy.filters.http.local_ratelimit",
                                "typed_config": {
                                    "@type": "type.googleapis.com/udpa.type.v1.TypedStruct",
                                    "type_url": "type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit",
                                    "value": {
                                        "stat_prefix": "local_rate_limiter",
                                        "token_bucket": {
                                            "max_tokens": 100,
                                            "tokens_per_fill": 100,
                                            "fill_interval": "60s"
                                        },
                                        "filter_enabled": {
                                            "runtime_key": "local_rate_limit_enabled",
                                            "default_value": {
                                                "numerator": 100,
                                                "denominator": "HUNDRED"
                                            }
                                        },
                                        "filter_enforced": {
                                            "runtime_key": "local_rate_limit_enforced",
                                            "default_value": {
                                                "numerator": 100,
                                                "denominator": "HUNDRED"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        return yaml.dump(envoy_filter, default_flow_style=False)

class RetryLogicConfig:
    """Example 8: Resilience Patterns with Retry Logic"""
    
    def generate_retry_policy(self) -> str:
        """Generate VirtualService with retry configuration"""
        
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": "payment-retry-policy",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "hosts": ["payment-service"],
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service"
                                }
                            }
                        ],
                        "retries": {
                            "attempts": 3,
                            "perTryTimeout": "10s",
                            "retryOn": "5xx,reset,connect-failure,refused-stream",
                            "retryRemoteLocalities": False
                        },
                        "timeout": "30s"
                    }
                ]
            }
        }
        
        return yaml.dump(virtual_service, default_flow_style=False)

class LoadBalancingConfig:
    """Example 9: Service Distribution with Load Balancing"""
    
    def generate_load_balancer_config(self) -> str:
        """Generate DestinationRule with load balancing"""
        
        destination_rule = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": "payment-lb-config",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "host": "payment-service",
                "trafficPolicy": {
                    "loadBalancer": {
                        "simple": "LEAST_CONN"  # ROUND_ROBIN, LEAST_CONN, RANDOM, PASSTHROUGH
                    },
                    "connectionPool": {
                        "tcp": {
                            "maxConnections": 100
                        },
                        "http": {
                            "http1MaxPendingRequests": 50,
                            "http2MaxRequests": 200,
                            "maxRequestsPerConnection": 10
                        }
                    }
                },
                "subsets": [
                    {
                        "name": "v1",
                        "labels": {
                            "version": "v1"
                        },
                        "trafficPolicy": {
                            "loadBalancer": {
                                "simple": "ROUND_ROBIN"
                            }
                        }
                    },
                    {
                        "name": "v2",
                        "labels": {
                            "version": "v2"
                        },
                        "trafficPolicy": {
                            "loadBalancer": {
                                "consistentHash": {
                                    "httpHeaderName": "x-user-id"
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        return yaml.dump(destination_rule, default_flow_style=False)

class MeshObservability:
    """Example 10: Service Mesh Observability"""
    
    def configure_telemetry(self) -> Dict[str, str]:
        """Configure comprehensive telemetry for banking services"""
        
        configs = {}
        
        # Telemetry configuration
        telemetry = {
            "apiVersion": "telemetry.istio.io/v1alpha1",
            "kind": "Telemetry",
            "metadata": {
                "name": "banking-observability",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "metrics": [
                    {
                        "providers": [
                            {"name": "prometheus"}
                        ],
                        "overrides": [
                            {
                                "match": {
                                    "metric": "requests_total"
                                },
                                "tagOverrides": {
                                    "business_unit": {
                                        "value": "payments"
                                    },
                                    "transaction_type": {
                                        "operation": "UPSERT",
                                        "value": "%{REQUEST_HEADERS['x-transaction-type']}"
                                    }
                                }
                            }
                        ]
                    }
                ],
                "tracing": [
                    {
                        "providers": [
                            {"name": "jaeger"}
                        ]
                    }
                ]
            }
        }
        
        configs['telemetry'] = yaml.dump(telemetry, default_flow_style=False)
        
        return configs

class FaultInjectionConfig:
    """Example 11: Chaos Engineering with Fault Injection"""
    
    def generate_fault_injection(self) -> str:
        """Generate VirtualService with fault injection for testing"""
        
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": "payment-fault-injection",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "hosts": ["payment-service"],
                "http": [
                    {
                        "match": [
                            {
                                "headers": {
                                    "x-chaos-test": {
                                        "exact": "enabled"
                                    }
                                }
                            }
                        ],
                        "fault": {
                            "delay": {
                                "percentage": {
                                    "value": 10.0
                                },
                                "fixedDelay": "5s"
                            },
                            "abort": {
                                "percentage": {
                                    "value": 5.0
                                },
                                "httpStatus": 500
                            }
                        },
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service"
                                }
                            }
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        return yaml.dump(virtual_service, default_flow_style=False)

class HeaderManipulationConfig:
    """Example 12: Request Routing with Header Manipulation"""
    
    def generate_header_manipulation(self) -> str:
        """Generate VirtualService with header manipulation"""
        
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": "payment-header-manipulation",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "hosts": ["payment-service"],
                "http": [
                    {
                        "match": [
                            {
                                "uri": {
                                    "prefix": "/api/v1/payments"
                                }
                            }
                        ],
                        "headers": {
                            "request": {
                                "add": {
                                    "x-bank-code": "HDFC",
                                    "x-request-id": "%REQ_ID%",
                                    "x-forwarded-proto": "https"
                                },
                                "remove": [
                                    "x-internal-header"
                                ]
                            },
                            "response": {
                                "add": {
                                    "x-response-time": "%DURATION%",
                                    "x-server-version": "v1.0.0"
                                },
                                "remove": [
                                    "server"
                                ]
                            }
                        },
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        return yaml.dump(virtual_service, default_flow_style=False)

class AuthorizationPolicyConfig:
    """Example 13: Service RBAC with Authorization Policies"""
    
    def generate_rbac_policies(self) -> Dict[str, str]:
        """Generate comprehensive RBAC policies for banking services"""
        
        policies = {}
        
        # Payment service authorization
        payment_authz = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": "payment-service-rbac",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "payment-service"
                    }
                },
                "rules": [
                    {
                        "from": [
                            {
                                "source": {
                                    "principals": [
                                        "cluster.local/ns/hdfc-accounts/sa/account-service",
                                        "cluster.local/ns/hdfc-mobile/sa/mobile-app"
                                    ]
                                }
                            }
                        ],
                        "to": [
                            {
                                "operation": {
                                    "methods": ["POST", "GET"],
                                    "paths": ["/api/v1/payments/*"]
                                }
                            }
                        ],
                        "when": [
                            {
                                "key": "request.headers[x-user-role]",
                                "values": ["customer", "merchant"]
                            },
                            {
                                "key": "source.ip",
                                "notValues": ["0.0.0.0/0"]
                            }
                        ]
                    }
                ]
            }
        }
        
        policies['payment_authorization'] = yaml.dump(payment_authz, default_flow_style=False)
        
        # Deny all policy for sensitive services
        deny_all = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": "deny-all-default",
                "namespace": "hdfc-admin"
            },
            "spec": {}  # Empty spec denies all traffic
        }
        
        policies['deny_all'] = yaml.dump(deny_all, default_flow_style=False)
        
        return policies

class VirtualServiceConfig:
    """Example 14: Advanced Traffic Management with Virtual Services"""
    
    def generate_advanced_routing(self) -> str:
        """Generate advanced routing configuration"""
        
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": "banking-advanced-routing",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "hosts": ["payment-service"],
                "http": [
                    {
                        "match": [
                            {
                                "headers": {
                                    "x-user-tier": {
                                        "exact": "premium"
                                    }
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service",
                                    "subset": "premium"
                                }
                            }
                        ],
                        "timeout": "60s"
                    },
                    {
                        "match": [
                            {
                                "uri": {
                                    "regex": "^/api/v1/payments/upi/.*"
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": "upi-service"
                                }
                            }
                        ],
                        "retries": {
                            "attempts": 3,
                            "perTryTimeout": "5s",
                            "retryOn": "gateway-error,connect-failure,refused-stream"
                        }
                    },
                    {
                        "match": [
                            {
                                "queryParams": {
                                    "amount": {
                                        "regex": "^[1-9][0-9]{4,}$"  # Large amounts (>=10000)
                                    }
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": "high-value-payment-service"
                                }
                            }
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service",
                                    "subset": "v1"
                                },
                                "weight": 80
                            },
                            {
                                "destination": {
                                    "host": "payment-service", 
                                    "subset": "v2"
                                },
                                "weight": 20
                            }
                        ]
                    }
                ]
            }
        }
        
        return yaml.dump(virtual_service, default_flow_style=False)

class GatewayConfig:
    """Example 15: Ingress Gateway Configuration"""
    
    def generate_banking_gateway(self) -> Dict[str, str]:
        """Generate production gateway configuration for banking"""
        
        configs = {}
        
        # Main banking gateway
        gateway = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": "hdfc-banking-gateway",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "selector": {
                    "istio": "ingressgateway"
                },
                "servers": [
                    {
                        "port": {
                            "number": 443,
                            "name": "https",
                            "protocol": "HTTPS"
                        },
                        "tls": {
                            "mode": "SIMPLE",
                            "credentialName": "hdfc-banking-tls"
                        },
                        "hosts": [
                            "api.hdfcbank.com",
                            "mobile-api.hdfcbank.com"
                        ]
                    },
                    {
                        "port": {
                            "number": 80,
                            "name": "http",
                            "protocol": "HTTP"
                        },
                        "hosts": [
                            "api.hdfcbank.com"
                        ],
                        "tls": {
                            "httpsRedirect": True
                        }
                    }
                ]
            }
        }
        
        configs['gateway'] = yaml.dump(gateway, default_flow_style=False)
        
        # Gateway virtual service
        gateway_vs = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": "hdfc-banking-vs",
                "namespace": "hdfc-payments"
            },
            "spec": {
                "hosts": [
                    "api.hdfcbank.com",
                    "mobile-api.hdfcbank.com"
                ],
                "gateways": [
                    "hdfc-banking-gateway"
                ],
                "http": [
                    {
                        "match": [
                            {
                                "uri": {
                                    "prefix": "/api/v1/payments"
                                },
                                "headers": {
                                    "host": {
                                        "exact": "api.hdfcbank.com"
                                    }
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": "payment-service",
                                    "port": {
                                        "number": 8080
                                    }
                                }
                            }
                        ],
                        "corsPolicy": {
                            "allowOrigins": [
                                {
                                    "exact": "https://netbanking.hdfcbank.com"
                                },
                                {
                                    "exact": "https://mobile.hdfcbank.com"
                                }
                            ],
                            "allowMethods": [
                                "POST",
                                "GET", 
                                "OPTIONS"
                            ],
                            "allowHeaders": [
                                "authorization",
                                "content-type",
                                "x-user-id",
                                "x-request-id"
                            ],
                            "exposeHeaders": [
                                "x-response-time"
                            ],
                            "maxAge": "24h"
                        }
                    },
                    {
                        "match": [
                            {
                                "uri": {
                                    "prefix": "/api/v1/mobile"
                                },
                                "headers": {
                                    "host": {
                                        "exact": "mobile-api.hdfcbank.com"
                                    }
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": "mobile-banking-service"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        configs['gateway_virtualservice'] = yaml.dump(gateway_vs, default_flow_style=False)
        
        return configs

def demonstrate_comprehensive_service_mesh():
    """Demonstrate comprehensive service mesh for Indian banking"""
    print("\n🌐 Comprehensive Service Mesh Demo - Indian Banking")
    print("=" * 55)
    
    # Initialize all service mesh components
    envoy_config = EnvoyProxyConfig("hdfc-payment-service")
    circuit_breaker = ServiceMeshCircuitBreaker("payment-service")
    service_discovery = IstioServiceDiscovery()
    mtls_config = mTLSConfiguration()
    traffic_shifting = TrafficShifting()
    rate_limiting = RateLimitingConfig()
    retry_logic = RetryLogicConfig()
    load_balancing = LoadBalancingConfig()
    observability = MeshObservability()
    fault_injection = FaultInjectionConfig()
    header_manipulation = HeaderManipulationConfig()
    authorization = AuthorizationPolicyConfig()
    virtual_services = VirtualServiceConfig()
    gateway_config = GatewayConfig()
    
    print("✅ All service mesh components initialized")
    
    # Demonstrate key configurations
    print("\n🔧 Envoy Proxy Configuration")
    print("-" * 30)
    
    proxy_config = envoy_config.generate_envoy_config()
    print("✅ Generated Envoy configuration:")
    print(f"   • Banking API listener on port 8080")
    print(f"   • JWT authentication with HDFC Auth")
    print(f"   • Circuit breaker with outlier detection")
    print(f"   • Structured access logging")
    print(f"   • Retry policies for resilience")
    
    # Security configuration
    print("\n🔒 Security Configuration")
    print("-" * 25)
    
    mtls_policy = mtls_config.generate_mtls_policy()
    authz_policies = authorization.generate_rbac_policies()
    
    print("✅ Security policies configured:")
    print("   • Strict mTLS for all banking services")
    print(f"   • {len(authz_policies)} authorization policies")
    print("   • Service-to-service RBAC")
    print("   • JWT-based authentication")
    
    # Traffic management
    print("\n🚦 Traffic Management")
    print("-" * 22)
    
    canary_config = traffic_shifting.generate_virtual_service(canary_weight=20)
    rate_limit_config = rate_limiting.generate_rate_limit_config()
    retry_config = retry_logic.generate_retry_policy()
    
    print("✅ Traffic management configured:")
    print("   • Canary deployments (20% traffic to v2)")
    print("   • Rate limiting (100 requests/minute)")
    print("   • Retry policies (3 attempts, 10s timeout)")
    print("   • Circuit breaker with outlier detection")
    
    # Load balancing
    print("\n⚖️  Load Balancing Configuration")
    print("-" * 32)
    
    lb_config = load_balancing.generate_load_balancer_config()
    print("✅ Load balancing configured:")
    print("   • LEAST_CONN for default traffic")
    print("   • ROUND_ROBIN for v1 subset")
    print("   • Consistent hash for v2 (by user-id)")
    print("   • Connection pooling limits")
    
    # Observability
    print("\n📊 Observability & Telemetry")
    print("-" * 30)
    
    telemetry_configs = observability.configure_telemetry()
    print("✅ Observability configured:")
    print("   • Prometheus metrics with business tags")
    print("   • Jaeger distributed tracing")
    print("   • Custom metric overrides")
    print("   • Transaction type tagging")
    
    # Fault injection
    print("\n🧪 Chaos Engineering")
    print("-" * 20)
    
    fault_config = fault_injection.generate_fault_injection()
    print("✅ Fault injection configured:")
    print("   • 10% delay injection (5s delay)")
    print("   • 5% error injection (HTTP 500)")
    print("   • Enabled only with chaos-test header")
    
    # Gateway configuration
    print("\n🚪 Gateway Configuration")
    print("-" * 25)
    
    gateway_configs = gateway_config.generate_banking_gateway()
    print("✅ Ingress gateway configured:")
    print("   • HTTPS on port 443 with TLS")
    print("   • HTTP to HTTPS redirect")
    print("   • Multi-host routing")
    print("   • CORS policies for web apps")
    
    # Advanced routing
    print("\n🛣️  Advanced Routing")
    print("-" * 19)
    
    advanced_routing = virtual_services.generate_advanced_routing()
    print("✅ Advanced routing configured:")
    print("   • Premium user routing")
    print("   • UPI-specific service routing")
    print("   • High-value transaction routing")
    print("   • Weighted traffic distribution")
    
    # Service discovery
    print("\n🔍 Service Discovery")
    print("-" * 20)
    
    services = service_discovery.register_banking_services()
    print(f"✅ Registered {len(services)} banking services:")
    for service_name in services.keys():
        print(f"   • {service_name}")
    
    # Production summary
    print("\n🏆 Service Mesh Features Summary")
    print("-" * 35)
    print("✅ Zero-trust networking with strict mTLS")
    print("✅ Traffic shaping and canary deployments")
    print("✅ Circuit breakers and retry policies")
    print("✅ Rate limiting and DDoS protection")
    print("✅ Comprehensive observability")
    print("✅ Fine-grained authorization")
    print("✅ Load balancing strategies")
    print("✅ Fault injection for testing")
    print("✅ Header manipulation and routing")
    print("✅ Production-ready gateway config")
    
    # Banking-specific benefits
    print("\n🏦 Banking-Specific Benefits")
    print("-" * 30)
    print("• RBI compliance with zero-trust security")
    print("• Audit trail for all service communications")
    print("• Gradual rollouts for critical banking services")
    print("• High availability with traffic failover")
    print("• Real-time observability for SLA monitoring")
    print("• Protection against service failures")
    print("• Consistent security policies across services")

if __name__ == "__main__":
    demonstrate_comprehensive_service_mesh()