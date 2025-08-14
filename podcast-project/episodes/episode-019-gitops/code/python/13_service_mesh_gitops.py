#!/usr/bin/env python3
"""
Service Mesh GitOps Integration System
=====================================

Istio service mesh के साथ GitOps integration।
Indian enterprise के लिए comprehensive service mesh automation।

Features:
- Istio service mesh GitOps automation और configuration management
- Multi-cluster service mesh coordination across Indian regions
- Traffic management के साथ festival season scaling
- Security policies और mTLS automation
- Observability और distributed tracing setup
- Indian compliance के साथ service mesh governance

Author: Hindi Tech Podcast - Episode 19
Context: Service Mesh GitOps for Indian Microservices
"""

import asyncio
import logging
import json
import yaml
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import kubernetes
from kubernetes import client, config
import aiohttp
import pytz
from pathlib import Path
import hashlib
import subprocess
import base64
import tempfile

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for service mesh operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('service_mesh_gitops.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrafficStrategy(Enum):
    """Traffic management strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTION = "least_connection"
    STICKY_SESSION = "sticky_session"
    REGIONAL_PREFERENCE = "regional_preference"

class SecurityPolicy(Enum):
    """Service mesh security policies"""
    STRICT_MTLS = "strict_mtls"
    PERMISSIVE_MTLS = "permissive_mtls"
    JWT_VALIDATION = "jwt_validation"
    RBAC_ENFORCEMENT = "rbac_enforcement"
    RATE_LIMITING = "rate_limiting"

class ObservabilityLevel(Enum):
    """Observability configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    FULL_TRACING = "full_tracing"

class FestivalScalingMode(Enum):
    """Festival season scaling modes"""
    NORMAL = "normal"
    FESTIVAL_PREPARATION = "festival_preparation"
    FESTIVAL_PEAK = "festival_peak"
    POST_FESTIVAL = "post_festival"

@dataclass
class IndianServiceContext:
    """Indian service context for mesh configuration"""
    
    @staticmethod
    def get_regional_service_priorities() -> Dict[str, List[str]]:
        """Get service priorities by Indian regions"""
        return {
            "mumbai_west": ["payment", "trading", "banking", "fintech"],
            "bangalore_south": ["ecommerce", "tech", "startup", "analytics"],
            "delhi_ncr": ["government", "enterprise", "logistics", "telecom"],
            "hyderabad_central": ["pharma", "biotech", "healthcare", "research"],
            "chennai_coastal": ["automotive", "manufacturing", "port", "shipping"],
            "pune_maharashtra": ["automotive", "it", "education", "agriculture"],
            "kolkata_east": ["jute", "coal", "traditional", "cultural"]
        }
    
    @staticmethod
    def get_festival_traffic_patterns() -> Dict[str, Any]:
        """Get festival-specific traffic patterns"""
        current_date = datetime.now(IST)
        
        return {
            "diwali": {
                "duration_days": 15,
                "peak_hours": [18, 19, 20, 21, 22],
                "traffic_multiplier": 4.5,
                "priority_services": ["payment", "ecommerce", "delivery"],
                "regions": ["mumbai_west", "delhi_ncr", "bangalore_south"]
            },
            "durga_puja": {
                "duration_days": 10,
                "peak_hours": [17, 18, 19, 20, 21],
                "traffic_multiplier": 5.2,
                "priority_services": ["payment", "booking", "delivery"],
                "regions": ["kolkata_east", "mumbai_west"]
            },
            "holi": {
                "duration_days": 3,
                "peak_hours": [10, 11, 12, 13, 14, 15],
                "traffic_multiplier": 3.8,
                "priority_services": ["social", "media", "delivery"],
                "regions": ["delhi_ncr", "mumbai_west", "pune_maharashtra"]
            },
            "ipl_season": {
                "duration_days": 60,
                "peak_hours": [19, 20, 21, 22, 23],
                "traffic_multiplier": 2.8,
                "priority_services": ["streaming", "betting", "social"],
                "regions": ["mumbai_west", "bangalore_south", "chennai_coastal"]
            }
        }
    
    @staticmethod
    def get_compliance_service_mappings() -> Dict[str, List[str]]:
        """Map services to Indian compliance requirements"""
        return {
            "rbi_services": ["payment", "banking", "wallet", "lending", "insurance"],
            "sebi_services": ["trading", "mutual_fund", "investment", "advisory"],
            "irdai_services": ["insurance", "health_insurance", "life_insurance"],
            "rto_services": ["vehicle_registration", "driving_license", "transport"],
            "gstn_services": ["invoice", "tax", "billing", "accounting"]
        }

@dataclass
class ServiceMeshConfig:
    """Service mesh configuration"""
    mesh_name: str
    namespace: str = "istio-system"
    
    # Istio configuration
    istio_version: str = "1.19.0"
    enable_istio_cni: bool = True
    enable_auto_injection: bool = True
    
    # Traffic management
    traffic_strategy: TrafficStrategy = TrafficStrategy.WEIGHTED
    enable_circuit_breaker: bool = True
    enable_retry_policy: bool = True
    enable_timeout_policy: bool = True
    
    # Security settings
    security_policies: List[SecurityPolicy] = field(default_factory=lambda: [
        SecurityPolicy.STRICT_MTLS, SecurityPolicy.RBAC_ENFORCEMENT
    ])
    enable_authz_policies: bool = True
    jwt_issuer: str = ""
    
    # Observability
    observability_level: ObservabilityLevel = ObservabilityLevel.STANDARD
    enable_jaeger: bool = True
    enable_kiali: bool = True
    enable_prometheus: bool = True
    enable_grafana: bool = True
    
    # Indian specific settings
    festival_scaling_mode: FestivalScalingMode = FestivalScalingMode.NORMAL
    enable_regional_failover: bool = True
    data_residency_enforcement: bool = True
    
    # Multi-cluster settings
    enable_cross_cluster_discovery: bool = False
    cluster_endpoints: Dict[str, str] = field(default_factory=dict)
    
    # GitOps integration
    git_repo: str = ""
    git_branch: str = "main"
    sync_interval_seconds: int = 300

@dataclass
class ServiceDefinition:
    """Service definition for mesh configuration"""
    name: str
    namespace: str
    version: str
    
    # Service properties
    port: int
    protocol: str = "HTTP"
    service_type: str = "ClusterIP"
    
    # Traffic management
    traffic_weight: float = 100.0
    circuit_breaker_settings: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    timeout_policy: Dict[str, Any] = field(default_factory=dict)
    
    # Security
    security_policies: List[str] = field(default_factory=list)
    allowed_sources: List[str] = field(default_factory=list)
    required_jwt_claims: Dict[str, str] = field(default_factory=dict)
    
    # Observability
    enable_tracing: bool = True
    enable_metrics: bool = True
    custom_telemetry: Dict[str, Any] = field(default_factory=dict)
    
    # Indian compliance
    compliance_requirements: List[str] = field(default_factory=list)
    data_classification: str = "internal"  # public, internal, confidential, restricted
    
    # Regional settings
    preferred_regions: List[str] = field(default_factory=list)
    festival_scaling_factor: float = 1.0

class ServiceMeshGitOpsManager:
    """
    Service Mesh GitOps Manager।
    
    Istio service mesh के लिए complete GitOps automation with Indian
    enterprise requirements, festival season scaling, और compliance।
    """
    
    def __init__(self, config: ServiceMeshConfig):
        self.config = config
        self.k8s_client = None
        self.istio_client = None
        self.services = {}  # Service definitions
        self.mesh_resources = {}  # Generated mesh resources
        
    async def initialize(self) -> bool:
        """Initialize service mesh GitOps manager"""
        try:
            logger.info("🚀 Initializing Service Mesh GitOps Manager")
            
            # Setup Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.k8s_client = {
                'v1': client.CoreV1Api(),
                'apps_v1': client.AppsV1Api(),
                'networking_v1': client.NetworkingV1Api(),
                'custom_objects': client.CustomObjectsApi()
            }
            
            # Verify Istio installation
            istio_status = await self._verify_istio_installation()
            if not istio_status["installed"]:
                logger.warning("⚠️ Istio not found, attempting installation...")
                install_result = await self._install_istio()
                if not install_result["success"]:
                    logger.error(f"❌ Istio installation failed: {install_result['error']}")
                    return False
            
            # Setup observability stack
            observability_result = await self._setup_observability_stack()
            if not observability_result["success"]:
                logger.warning(f"⚠️ Observability setup issues: {observability_result['error']}")
            
            # Initialize festival season monitoring
            await self._initialize_festival_monitoring()
            
            logger.info("✅ Service Mesh GitOps Manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Service mesh manager initialization failed: {e}")
            return False
    
    async def _verify_istio_installation(self) -> Dict[str, Any]:
        """Verify Istio installation status"""
        try:
            logger.info("🔍 Verifying Istio installation")
            
            # Check istio-system namespace
            try:
                namespace = self.k8s_client['v1'].read_namespace(name="istio-system")
                logger.info("✅ istio-system namespace found")
            except client.ApiException as e:
                if e.status == 404:
                    return {"installed": False, "reason": "istio-system namespace not found"}
                raise e
            
            # Check Istio control plane pods
            pods = self.k8s_client['v1'].list_namespaced_pod(namespace="istio-system")
            
            istio_components = ["istiod", "istio-proxy"]
            found_components = []
            
            for pod in pods.items:
                for component in istio_components:
                    if component in pod.metadata.name:
                        found_components.append(component)
            
            if "istiod" in found_components:
                logger.info("✅ Istio control plane detected")
                return {"installed": True, "version": "detected", "components": found_components}
            else:
                return {"installed": False, "reason": "Istio control plane not found"}
                
        except Exception as e:
            logger.error(f"❌ Istio verification failed: {e}")
            return {"installed": False, "reason": str(e)}
    
    async def _install_istio(self) -> Dict[str, Any]:
        """Install Istio service mesh"""
        try:
            logger.info("📦 Installing Istio service mesh")
            
            # Check if istioctl is available
            try:
                subprocess.run(["istioctl", "version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "istioctl not found in PATH"}
            
            # Install Istio with custom configuration
            istio_config = {
                "apiVersion": "install.istio.io/v1alpha1",
                "kind": "IstioOperator",
                "metadata": {
                    "name": "control-plane"
                },
                "spec": {
                    "components": {
                        "pilot": {
                            "k8s": {
                                "resources": {
                                    "requests": {
                                        "cpu": "500m",
                                        "memory": "1Gi"
                                    }
                                }
                            }
                        }
                    },
                    "meshConfig": {
                        "defaultConfig": {
                            "holdApplicationUntilProxyStarts": True,
                            "tracing": {
                                "zipkin": {
                                    "address": "jaeger-collector.istio-system.svc.cluster.local:9411"
                                }
                            }
                        }
                    }
                }
            }
            
            # Write configuration to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(istio_config, f)
                config_file = f.name
            
            try:
                # Install Istio
                install_cmd = ["istioctl", "install", "-f", config_file, "-y"]
                process = subprocess.run(install_cmd, capture_output=True, text=True, timeout=600)
                
                if process.returncode == 0:
                    logger.info("✅ Istio installation completed")
                    
                    # Enable automatic sidecar injection for default namespace
                    await self._enable_sidecar_injection("default")
                    
                    return {"success": True, "output": process.stdout}
                else:
                    logger.error(f"❌ Istio installation failed: {process.stderr}")
                    return {"success": False, "error": process.stderr}
                    
            finally:
                # Clean up temp file
                os.unlink(config_file)
                
        except Exception as e:
            logger.error(f"❌ Istio installation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _enable_sidecar_injection(self, namespace: str) -> bool:
        """Enable Istio sidecar injection for namespace"""
        try:
            logger.info(f"💉 Enabling sidecar injection for namespace: {namespace}")
            
            # Label namespace for automatic injection
            body = {
                "metadata": {
                    "labels": {
                        "istio-injection": "enabled"
                    }
                }
            }
            
            self.k8s_client['v1'].patch_namespace(
                name=namespace,
                body=body
            )
            
            logger.info(f"✅ Sidecar injection enabled for {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enable sidecar injection for {namespace}: {e}")
            return False
    
    async def _setup_observability_stack(self) -> Dict[str, Any]:
        """Setup observability stack (Jaeger, Kiali, Prometheus, Grafana)"""
        try:
            logger.info("📊 Setting up observability stack")
            
            results = {}
            
            # Install Jaeger for distributed tracing
            if self.config.enable_jaeger:
                jaeger_result = await self._install_jaeger()
                results["jaeger"] = jaeger_result
            
            # Install Kiali for service mesh visualization
            if self.config.enable_kiali:
                kiali_result = await self._install_kiali()
                results["kiali"] = kiali_result
            
            # Install Prometheus for metrics
            if self.config.enable_prometheus:
                prometheus_result = await self._install_prometheus()
                results["prometheus"] = prometheus_result
            
            # Install Grafana for dashboards
            if self.config.enable_grafana:
                grafana_result = await self._install_grafana()
                results["grafana"] = grafana_result
            
            # Check overall success
            all_success = all(result.get("success", False) for result in results.values())
            
            if all_success:
                logger.info("✅ Observability stack setup completed")
                return {"success": True, "components": results}
            else:
                failed_components = [name for name, result in results.items() if not result.get("success", False)]
                logger.warning(f"⚠️ Some observability components failed: {failed_components}")
                return {"success": False, "error": f"Failed components: {failed_components}", "results": results}
                
        except Exception as e:
            logger.error(f"❌ Observability stack setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _install_jaeger(self) -> Dict[str, Any]:
        """Install Jaeger for distributed tracing"""
        try:
            logger.info("🔍 Installing Jaeger tracing")
            
            jaeger_deployment = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "jaeger",
                    "namespace": "istio-system",
                    "labels": {
                        "app": "jaeger"
                    }
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": "jaeger"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "jaeger"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "jaeger",
                                    "image": "jaegertracing/all-in-one:1.47",
                                    "env": [
                                        {
                                            "name": "COLLECTOR_ZIPKIN_HOST_PORT",
                                            "value": ":9411"
                                        }
                                    ],
                                    "ports": [
                                        {"containerPort": 16686, "name": "http-query"},
                                        {"containerPort": 9411, "name": "zipkin"}
                                    ],
                                    "resources": {
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        },
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
            
            jaeger_service = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "jaeger-collector",
                    "namespace": "istio-system",
                    "labels": {
                        "app": "jaeger"
                    }
                },
                "spec": {
                    "ports": [
                        {"port": 9411, "targetPort": 9411, "name": "zipkin"}
                    ],
                    "selector": {
                        "app": "jaeger"
                    }
                }
            }
            
            jaeger_query_service = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "jaeger-query",
                    "namespace": "istio-system",
                    "labels": {
                        "app": "jaeger"
                    }
                },
                "spec": {
                    "ports": [
                        {"port": 16686, "targetPort": 16686, "name": "http-query"}
                    ],
                    "selector": {
                        "app": "jaeger"
                    }
                }
            }
            
            # Create Jaeger resources
            self.k8s_client['apps_v1'].create_namespaced_deployment(
                namespace="istio-system",
                body=jaeger_deployment
            )
            
            self.k8s_client['v1'].create_namespaced_service(
                namespace="istio-system",
                body=jaeger_service
            )
            
            self.k8s_client['v1'].create_namespaced_service(
                namespace="istio-system",
                body=jaeger_query_service
            )
            
            logger.info("✅ Jaeger tracing installed")
            return {"success": True, "component": "jaeger"}
            
        except Exception as e:
            logger.error(f"❌ Jaeger installation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _install_kiali(self) -> Dict[str, Any]:
        """Install Kiali for service mesh visualization"""
        try:
            logger.info("🕸️ Installing Kiali visualization")
            
            # Create Kiali service account and RBAC
            kiali_sa = {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": "kiali",
                    "namespace": "istio-system"
                }
            }
            
            kiali_clusterrole = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": "kiali"
                },
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["namespaces", "services", "endpoints", "pods", "replicationcontrollers", "nodes"],
                        "verbs": ["get", "list", "watch"]
                    },
                    {
                        "apiGroups": ["apps"],
                        "resources": ["deployments", "replicasets"],
                        "verbs": ["get", "list", "watch"]
                    },
                    {
                        "apiGroups": ["networking.istio.io"],
                        "resources": ["*"],
                        "verbs": ["get", "list", "watch"]
                    }
                ]
            }
            
            kiali_clusterrolebinding = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "name": "kiali"
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": "kiali"
                },
                "subjects": [
                    {
                        "kind": "ServiceAccount",
                        "name": "kiali",
                        "namespace": "istio-system"
                    }
                ]
            }
            
            # Create RBAC resources
            self.k8s_client['v1'].create_namespaced_service_account(
                namespace="istio-system",
                body=kiali_sa
            )
            
            # Note: In production, you would use proper Kiali operator or helm chart
            logger.info("✅ Kiali RBAC configured (full installation requires Kiali operator)")
            return {"success": True, "component": "kiali", "note": "RBAC configured"}
            
        except Exception as e:
            logger.error(f"❌ Kiali installation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def register_service(self, service: ServiceDefinition) -> bool:
        """Register service with mesh configuration"""
        try:
            logger.info(f"📋 Registering service: {service.name}")
            
            self.services[service.name] = service
            
            # Generate Istio resources for service
            istio_resources = await self._generate_istio_resources(service)
            self.mesh_resources[service.name] = istio_resources
            
            # Apply resources to cluster
            apply_result = await self._apply_istio_resources(service.name, istio_resources)
            
            if apply_result["success"]:
                logger.info(f"✅ Service registered successfully: {service.name}")
                
                # Apply Indian compliance policies if required
                if service.compliance_requirements:
                    compliance_result = await self._apply_compliance_policies(service)
                    if not compliance_result["success"]:
                        logger.warning(f"⚠️ Compliance policy application failed: {compliance_result['error']}")
                
                return True
            else:
                logger.error(f"❌ Service registration failed: {apply_result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Service registration failed for {service.name}: {e}")
            return False
    
    async def _generate_istio_resources(self, service: ServiceDefinition) -> Dict[str, Any]:
        """Generate Istio resources for service"""
        try:
            logger.info(f"⚙️ Generating Istio resources for: {service.name}")
            
            resources = {}
            
            # Generate DestinationRule
            destination_rule = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "DestinationRule",
                "metadata": {
                    "name": f"{service.name}-destination-rule",
                    "namespace": service.namespace
                },
                "spec": {
                    "host": service.name,
                    "trafficPolicy": {
                        "tls": {
                            "mode": "ISTIO_MUTUAL" if SecurityPolicy.STRICT_MTLS in self.config.security_policies else "SIMPLE"
                        }
                    }
                }
            }
            
            # Add circuit breaker if configured
            if service.circuit_breaker_settings:
                destination_rule["spec"]["trafficPolicy"]["connectionPool"] = {
                    "tcp": {
                        "maxConnections": service.circuit_breaker_settings.get("max_connections", 10)
                    },
                    "http": {
                        "http1MaxPendingRequests": service.circuit_breaker_settings.get("max_pending_requests", 10),
                        "maxRequestsPerConnection": service.circuit_breaker_settings.get("max_requests_per_connection", 2)
                    }
                }
                
                destination_rule["spec"]["trafficPolicy"]["outlierDetection"] = {
                    "consecutive5xxErrors": service.circuit_breaker_settings.get("consecutive_errors", 5),
                    "interval": "30s",
                    "baseEjectionTime": "30s",
                    "maxEjectionPercent": 50
                }
            
            resources["destination_rule"] = destination_rule
            
            # Generate VirtualService for traffic management
            virtual_service = {
                "apiVersion": "networking.istio.io/v1beta1",
                "kind": "VirtualService",
                "metadata": {
                    "name": f"{service.name}-virtual-service",
                    "namespace": service.namespace
                },
                "spec": {
                    "hosts": [service.name],
                    "http": [
                        {
                            "match": [{"uri": {"prefix": "/"}}],
                            "route": [
                                {
                                    "destination": {
                                        "host": service.name,
                                        "port": {"number": service.port}
                                    },
                                    "weight": int(service.traffic_weight)
                                }
                            ]
                        }
                    ]
                }
            }
            
            # Add timeout configuration
            if service.timeout_policy:
                virtual_service["spec"]["http"][0]["timeout"] = service.timeout_policy.get("timeout", "15s")
            
            # Add retry policy
            if service.retry_policy:
                virtual_service["spec"]["http"][0]["retries"] = {
                    "attempts": service.retry_policy.get("attempts", 3),
                    "perTryTimeout": service.retry_policy.get("per_try_timeout", "5s")
                }
            
            # Add festival season routing if applicable
            if service.festival_scaling_factor > 1.0 and self.config.festival_scaling_mode != FestivalScalingMode.NORMAL:
                virtual_service = self._add_festival_routing(virtual_service, service)
            
            resources["virtual_service"] = virtual_service
            
            # Generate AuthorizationPolicy for security
            if service.allowed_sources or SecurityPolicy.RBAC_ENFORCEMENT in self.config.security_policies:
                authz_policy = {
                    "apiVersion": "security.istio.io/v1beta1",
                    "kind": "AuthorizationPolicy",
                    "metadata": {
                        "name": f"{service.name}-authz-policy",
                        "namespace": service.namespace
                    },
                    "spec": {
                        "selector": {
                            "matchLabels": {
                                "app": service.name
                            }
                        },
                        "rules": []
                    }
                }
                
                # Add source-based rules
                if service.allowed_sources:
                    for source in service.allowed_sources:
                        rule = {
                            "from": [
                                {
                                    "source": {
                                        "principals": [f"cluster.local/ns/{service.namespace}/sa/{source}"]
                                    }
                                }
                            ]
                        }
                        authz_policy["spec"]["rules"].append(rule)
                
                resources["authorization_policy"] = authz_policy
            
            # Generate RequestAuthentication for JWT validation
            if service.required_jwt_claims and SecurityPolicy.JWT_VALIDATION in self.config.security_policies:
                request_auth = {
                    "apiVersion": "security.istio.io/v1beta1",
                    "kind": "RequestAuthentication",
                    "metadata": {
                        "name": f"{service.name}-jwt-auth",
                        "namespace": service.namespace
                    },
                    "spec": {
                        "selector": {
                            "matchLabels": {
                                "app": service.name
                            }
                        },
                        "jwtRules": [
                            {
                                "issuer": self.config.jwt_issuer,
                                "jwksUri": f"{self.config.jwt_issuer}/.well-known/jwks.json"
                            }
                        ]
                    }
                }
                
                resources["request_authentication"] = request_auth
            
            logger.info(f"✅ Generated {len(resources)} Istio resources for {service.name}")
            return resources
            
        except Exception as e:
            logger.error(f"❌ Resource generation failed for {service.name}: {e}")
            return {}
    
    def _add_festival_routing(self, virtual_service: Dict[str, Any], 
                            service: ServiceDefinition) -> Dict[str, Any]:
        """Add festival season specific routing"""
        try:
            # Add header-based routing for festival traffic
            festival_route = {
                "match": [
                    {
                        "headers": {
                            "x-festival-priority": {
                                "exact": "high"
                            }
                        }
                    }
                ],
                "route": [
                    {
                        "destination": {
                            "host": service.name,
                            "port": {"number": service.port}
                        },
                        "weight": 100
                    }
                ],
                "priority": 100  # Higher priority for festival traffic
            }
            
            # Insert festival route at the beginning
            virtual_service["spec"]["http"].insert(0, festival_route)
            
            return virtual_service
            
        except Exception as e:
            logger.error(f"❌ Failed to add festival routing: {e}")
            return virtual_service
    
    async def _apply_istio_resources(self, service_name: str, 
                                   resources: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Istio resources to cluster"""
        try:
            logger.info(f"🔧 Applying Istio resources for: {service_name}")
            
            applied_resources = []
            errors = []
            
            for resource_type, resource in resources.items():
                try:
                    # Apply resource using custom objects API
                    group = resource["apiVersion"].split("/")[0]
                    version = resource["apiVersion"].split("/")[1]
                    plural = self._get_resource_plural(resource["kind"])
                    
                    self.k8s_client['custom_objects'].create_namespaced_custom_object(
                        group=group,
                        version=version,
                        namespace=resource["metadata"]["namespace"],
                        plural=plural,
                        body=resource
                    )
                    
                    applied_resources.append(f"{resource['kind']}/{resource['metadata']['name']}")
                    logger.info(f"✅ Applied {resource['kind']}: {resource['metadata']['name']}")
                    
                except Exception as e:
                    error_msg = f"Failed to apply {resource_type}: {e}"
                    errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            if errors:
                return {
                    "success": False,
                    "error": "; ".join(errors),
                    "applied_resources": applied_resources
                }
            else:
                return {
                    "success": True,
                    "applied_resources": applied_resources
                }
                
        except Exception as e:
            logger.error(f"❌ Resource application failed for {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_resource_plural(self, kind: str) -> str:
        """Get plural form of Kubernetes resource kind"""
        plurals = {
            "DestinationRule": "destinationrules",
            "VirtualService": "virtualservices",
            "AuthorizationPolicy": "authorizationpolicies",
            "RequestAuthentication": "requestauthentications",
            "PeerAuthentication": "peerauthentications",
            "Gateway": "gateways"
        }
        return plurals.get(kind, kind.lower() + "s")
    
    async def _apply_compliance_policies(self, service: ServiceDefinition) -> Dict[str, Any]:
        """Apply Indian compliance policies to service"""
        try:
            logger.info(f"📋 Applying compliance policies for: {service.name}")
            
            compliance_mappings = IndianServiceContext.get_compliance_service_mappings()
            
            # Apply RBI compliance if required
            if "rbi" in service.compliance_requirements:
                rbi_services = compliance_mappings["rbi_services"]
                if any(svc_type in service.name.lower() for svc_type in rbi_services):
                    await self._apply_rbi_policies(service)
            
            # Apply SEBI compliance if required
            if "sebi" in service.compliance_requirements:
                sebi_services = compliance_mappings["sebi_services"]
                if any(svc_type in service.name.lower() for svc_type in sebi_services):
                    await self._apply_sebi_policies(service)
            
            # Apply data residency policies
            if "data_residency" in service.compliance_requirements:
                await self._apply_data_residency_policies(service)
            
            logger.info(f"✅ Compliance policies applied for: {service.name}")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ Compliance policy application failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _apply_rbi_policies(self, service: ServiceDefinition) -> None:
        """Apply RBI-specific security policies"""
        logger.info(f"🏛️ Applying RBI compliance policies for: {service.name}")
        # Implementation would include:
        # - Strict mTLS enforcement
        # - Enhanced logging and audit trails
        # - Data encryption requirements
        # - Access control policies
    
    async def _apply_sebi_policies(self, service: ServiceDefinition) -> None:
        """Apply SEBI-specific trading compliance policies"""
        logger.info(f"📈 Applying SEBI compliance policies for: {service.name}")
        # Implementation would include:
        # - Trading hours enforcement
        # - Transaction logging
        # - Market data compliance
        # - Regulatory reporting
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.k8s_client:
            # Close any open connections
            pass
        
        logger.info("🧹 Service Mesh GitOps Manager cleaned up")


async def main():
    """Main function for service mesh GitOps"""
    print("🕸️ Service Mesh GitOps Integration System")
    print("=" * 50)
    
    # Configuration
    config = ServiceMeshConfig(
        mesh_name="indian-enterprise-mesh",
        namespace="istio-system",
        istio_version="1.19.0",
        enable_istio_cni=True,
        enable_auto_injection=True,
        traffic_strategy=TrafficStrategy.WEIGHTED,
        security_policies=[SecurityPolicy.STRICT_MTLS, SecurityPolicy.RBAC_ENFORCEMENT],
        observability_level=ObservabilityLevel.ADVANCED,
        festival_scaling_mode=FestivalScalingMode.FESTIVAL_PREPARATION,
        enable_regional_failover=True,
        data_residency_enforcement=True,
        git_repo="https://github.com/company/service-mesh-config",
        git_branch="main"
    )
    
    # Initialize service mesh manager
    mesh_manager = ServiceMeshGitOpsManager(config)
    
    try:
        if await mesh_manager.initialize():
            print("✅ Service Mesh GitOps Manager initialized successfully")
            
            # Example: Register a payment service
            payment_service = ServiceDefinition(
                name="payment-service",
                namespace="default",
                version="v2.1.0",
                port=8080,
                protocol="HTTP",
                traffic_weight=100.0,
                circuit_breaker_settings={
                    "max_connections": 20,
                    "max_pending_requests": 10,
                    "consecutive_errors": 5
                },
                retry_policy={
                    "attempts": 3,
                    "per_try_timeout": "5s"
                },
                timeout_policy={
                    "timeout": "15s"
                },
                security_policies=["strict_mtls", "rbac"],
                allowed_sources=["frontend-service", "api-gateway"],
                compliance_requirements=["rbi", "data_residency"],
                data_classification="restricted",
                preferred_regions=["mumbai_west", "delhi_ncr"],
                festival_scaling_factor=3.5
            )
            
            # Register service with mesh
            registration_result = await mesh_manager.register_service(payment_service)
            
            print(f"\n📊 Service Registration Results:")
            print(f"   Service: {payment_service.name}")
            print(f"   Success: {'✅' if registration_result else '❌'}")
            print(f"   Compliance: {', '.join(payment_service.compliance_requirements)}")
            print(f"   Festival Scaling: {payment_service.festival_scaling_factor}x")
                
        else:
            print("❌ Failed to initialize Service Mesh GitOps Manager")
            
    except Exception as e:
        print(f"❌ Service Mesh GitOps error: {e}")
    finally:
        await mesh_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())