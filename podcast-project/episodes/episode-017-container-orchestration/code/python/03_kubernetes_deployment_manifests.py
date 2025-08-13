#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kubernetes Deployment Manifests Generator
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे BigBasket जैसी companies
production-grade Kubernetes manifests बनाती हैं।

Real-world scenario: BigBasket का inventory service deployment
"""

import yaml
import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class KubernetesAppConfig:
    """Kubernetes application configuration for Indian companies"""
    app_name: str
    namespace: str
    replicas: int
    image: str
    version: str
    company: str
    environment: str  # dev, staging, prod
    region: str  # mumbai, bangalore, delhi
    resource_requests: Dict[str, str]
    resource_limits: Dict[str, str]
    ports: List[int]
    health_check_path: str

class BigBasketK8sGenerator:
    """
    BigBasket-style Kubernetes manifest generator
    Production-ready deployments with Indian company practices
    """
    
    def __init__(self):
        self.indian_node_selectors = {
            "mumbai": {"zone": "mumbai", "tier": "production"},
            "bangalore": {"zone": "bangalore", "tier": "production"},
            "delhi": {"zone": "delhi", "tier": "production"},
            "hyderabad": {"zone": "hyderabad", "tier": "staging"}
        }
        
        # Indian company resource standards
        self.resource_profiles = {
            "small": {
                "requests": {"cpu": "100m", "memory": "128Mi"},
                "limits": {"cpu": "500m", "memory": "512Mi"}
            },
            "medium": {
                "requests": {"cpu": "250m", "memory": "256Mi"},
                "limits": {"cpu": "1000m", "memory": "1Gi"}
            },
            "large": {
                "requests": {"cpu": "500m", "memory": "512Mi"},
                "limits": {"cpu": "2000m", "memory": "2Gi"}
            }
        }
        
        print("🛸 BigBasket Kubernetes Generator initialized!")
        print("Production-ready K8s manifests banane ke liye ready!")
    
    def generate_namespace(self, config: KubernetesAppConfig) -> Dict[str, Any]:
        """
        Namespace manifest generation - Company isolation के लिए
        """
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": config.namespace,
                "labels": {
                    "company": config.company,
                    "environment": config.environment,
                    "region": config.region,
                    "managed-by": "hindi-tech-podcast"
                },
                "annotations": {
                    "created-by": f"{config.company}-devops-team",
                    "created-at": datetime.now().isoformat(),
                    "purpose": f"{config.company} {config.environment} environment"
                }
            }
        }
    
    def generate_deployment(self, config: KubernetesAppConfig) -> Dict[str, Any]:
        """
        Deployment manifest generation - Main application deployment
        """
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.app_name,
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                    "version": config.version,
                    "company": config.company,
                    "environment": config.environment,
                    "region": config.region
                },
                "annotations": {
                    "deployment.kubernetes.io/revision": "1",
                    "company.com/owner": f"{config.company}-backend-team",
                    "company.com/slack-channel": f"#{config.company}-alerts",
                    "company.com/runbook": f"https://docs.{config.company}.com/runbooks/{config.app_name}"
                }
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": config.app_name,
                        "version": config.version
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.app_name,
                            "version": config.version,
                            "company": config.company,
                            "environment": config.environment,
                            "region": config.region
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8000",
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        # Node selection - Indian datacenter specific
                        "nodeSelector": self.indian_node_selectors.get(config.region, {}),
                        
                        # Pod anti-affinity - High availability के लिए
                        "affinity": {
                            "podAntiAffinity": {
                                "preferredDuringSchedulingIgnoredDuringExecution": [{
                                    "weight": 100,
                                    "podAffinityTerm": {
                                        "labelSelector": {
                                            "matchExpressions": [{
                                                "key": "app",
                                                "operator": "In",
                                                "values": [config.app_name]
                                            }]
                                        },
                                        "topologyKey": "kubernetes.io/hostname"
                                    }
                                }]
                            }
                        },
                        
                        # Security context - Production security
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "fsGroup": 2000
                        },
                        
                        # Service account for RBAC
                        "serviceAccountName": f"{config.app_name}-sa",
                        
                        "containers": [{
                            "name": config.app_name,
                            "image": f"{config.image}:{config.version}",
                            "imagePullPolicy": "Always",
                            
                            # Ports configuration
                            "ports": [
                                {"containerPort": port, "protocol": "TCP"}
                                for port in config.ports
                            ],
                            
                            # Environment variables - Indian company specific
                            "env": [
                                {"name": "APP_ENV", "value": config.environment},
                                {"name": "COMPANY", "value": config.company},
                                {"name": "REGION", "value": config.region},
                                {"name": "POD_NAME", "valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}}},
                                {"name": "POD_NAMESPACE", "valueFrom": {"fieldRef": {"fieldPath": "metadata.namespace"}}},
                                {"name": "POD_IP", "valueFrom": {"fieldRef": {"fieldPath": "status.podIP"}}},
                                {"name": "TZ", "value": "Asia/Kolkata"}
                            ],
                            
                            # Resource management - Production optimization
                            "resources": {
                                "requests": config.resource_requests,
                                "limits": config.resource_limits
                            },
                            
                            # Health checks - Kubernetes native
                            "livenessProbe": {
                                "httpGet": {
                                    "path": config.health_check_path,
                                    "port": config.ports[0]
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                                "timeoutSeconds": 5,
                                "failureThreshold": 3
                            },
                            
                            "readinessProbe": {
                                "httpGet": {
                                    "path": config.health_check_path,
                                    "port": config.ports[0]
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5,
                                "timeoutSeconds": 3,
                                "failureThreshold": 2
                            },
                            
                            # Startup probe for slow starting applications
                            "startupProbe": {
                                "httpGet": {
                                    "path": config.health_check_path,
                                    "port": config.ports[0]
                                },
                                "failureThreshold": 30,
                                "periodSeconds": 10
                            },
                            
                            # Security context for container
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True,
                                "capabilities": {"drop": ["ALL"]}
                            },
                            
                            # Volume mounts for logs and temp files
                            "volumeMounts": [
                                {"name": "tmp", "mountPath": "/tmp"},
                                {"name": "logs", "mountPath": "/app/logs"}
                            ]
                        }],
                        
                        # Volumes
                        "volumes": [
                            {"name": "tmp", "emptyDir": {}},
                            {"name": "logs", "emptyDir": {}}
                        ],
                        
                        # Tolerations for specific nodes
                        "tolerations": [
                            {
                                "key": "company.com/dedicated",
                                "operator": "Equal",
                                "value": config.company,
                                "effect": "NoSchedule"
                            }
                        ]
                    }
                },
                
                # Deployment strategy - Rolling update
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1
                    }
                }
            }
        }
    
    def generate_service(self, config: KubernetesAppConfig) -> Dict[str, Any]:
        """
        Service manifest generation - Load balancing के लिए
        """
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{config.app_name}-service",
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                    "company": config.company,
                    "environment": config.environment
                },
                "annotations": {
                    "service.beta.kubernetes.io/aws-load-balancer-type": "nlb",
                    "service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": "true"
                }
            },
            "spec": {
                "selector": {
                    "app": config.app_name
                },
                "ports": [
                    {
                        "name": f"http-{port}",
                        "port": port,
                        "targetPort": port,
                        "protocol": "TCP"
                    }
                    for port in config.ports
                ],
                "type": "ClusterIP"  # Internal service, LoadBalancer for external
            }
        }
    
    def generate_configmap(self, config: KubernetesAppConfig) -> Dict[str, Any]:
        """
        ConfigMap generation - Configuration management
        """
        app_config = {
            "app.yaml": f"""# {config.company} {config.app_name} configuration
company: {config.company}
environment: {config.environment}
region: {config.region}
timezone: Asia/Kolkata

# Database configuration
database:
  host: postgres-service.{config.namespace}.svc.cluster.local
  port: 5432
  name: {config.app_name}_db
  
# Redis configuration  
redis:
  host: redis-service.{config.namespace}.svc.cluster.local
  port: 6379
  
# Monitoring configuration
monitoring:
  enabled: true
  metrics_port: 8000
  metrics_path: /metrics
  
# Indian specific settings
localization:
  currency: INR
  language: hi
  date_format: "DD/MM/YYYY"
  
# Feature flags
features:
  new_ui: {str(config.environment != 'production').lower()}
  advanced_analytics: true
  regional_pricing: true
""",
            
            "logging.yaml": f"""# Logging configuration for {config.company}
version: 1
disable_existing_loggers: false

formatters:
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
  
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: detailed
    stream: ext://sys.stdout
    
  file:
    class: logging.FileHandler
    level: DEBUG
    formatter: detailed
    filename: /app/logs/{config.app_name}.log
    
loggers:
  {config.app_name}:
    level: DEBUG
    handlers: [console, file]
    propagate: false
    
root:
  level: INFO
  handlers: [console]
"""
        }
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{config.app_name}-config",
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                    "company": config.company,
                    "environment": config.environment
                }
            },
            "data": app_config
        }
    
    def generate_hpa(self, config: KubernetesAppConfig) -> Dict[str, Any]:
        """
        Horizontal Pod Autoscaler - Auto-scaling के लिए
        """
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{config.app_name}-hpa",
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                    "company": config.company,
                    "environment": config.environment
                }
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": config.app_name
                },
                "minReplicas": max(1, config.replicas // 2),  # Minimum replicas
                "maxReplicas": config.replicas * 3,  # Maximum replicas
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Resource", 
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ],
                "behavior": {
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {
                                "type": "Percent",
                                "value": 100,
                                "periodSeconds": 15
                            }
                        ]
                    },
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {
                                "type": "Percent", 
                                "value": 10,
                                "periodSeconds": 60
                            }
                        ]
                    }
                }
            }
        }
    
    def generate_ingress(self, config: KubernetesAppConfig) -> Dict[str, Any]:
        """
        Ingress configuration - External access के लिए
        """
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{config.app_name}-ingress",
                "namespace": config.namespace,
                "labels": {
                    "app": config.app_name,
                    "company": config.company,
                    "environment": config.environment
                },
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                }
            },
            "spec": {
                "tls": [
                    {
                        "hosts": [f"{config.app_name}.{config.company}.com"],
                        "secretName": f"{config.app_name}-tls"
                    }
                ],
                "rules": [
                    {
                        "host": f"{config.app_name}.{config.company}.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": f"{config.app_name}-service",
                                            "port": {"number": config.ports[0]}
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def generate_all_manifests(self, config: KubernetesAppConfig) -> Dict[str, Any]:
        """
        All Kubernetes manifests generation - Complete setup
        """
        manifests = {
            "namespace": self.generate_namespace(config),
            "deployment": self.generate_deployment(config),
            "service": self.generate_service(config),
            "configmap": self.generate_configmap(config),
            "hpa": self.generate_hpa(config),
            "ingress": self.generate_ingress(config)
        }
        
        return manifests
    
    def save_manifests_to_files(self, manifests: Dict[str, Any], output_dir: str):
        """
        Save manifests to separate YAML files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for manifest_type, manifest_content in manifests.items():
            filename = f"{manifest_type}.yaml"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                yaml.dump(manifest_content, f, default_flow_style=False, sort_keys=False)
            
            print(f"✅ {manifest_type} manifest saved: {filepath}")

def main():
    """Demonstration of Kubernetes manifests for Indian companies"""
    
    # BigBasket inventory service configuration
    bigbasket_config = KubernetesAppConfig(
        app_name="inventory-service",
        namespace="bigbasket-prod",
        replicas=5,
        image="bigbasket/inventory-service",
        version="v2.1.0",
        company="bigbasket",
        environment="production",
        region="bangalore",
        resource_requests={"cpu": "500m", "memory": "512Mi"},
        resource_limits={"cpu": "2000m", "memory": "2Gi"},
        ports=[8000, 9090],
        health_check_path="/health"
    )
    
    # Zomato order service configuration
    zomato_config = KubernetesAppConfig(
        app_name="order-service",
        namespace="zomato-prod",
        replicas=10,
        image="zomato/order-service",
        version="v1.5.3",
        company="zomato",
        environment="production",
        region="mumbai",
        resource_requests={"cpu": "250m", "memory": "256Mi"},
        resource_limits={"cpu": "1000m", "memory": "1Gi"},
        ports=[8000],
        health_check_path="/health"
    )
    
    # Ola ride matching service configuration
    ola_config = KubernetesAppConfig(
        app_name="ride-matching",
        namespace="ola-prod",
        replicas=15,
        image="ola/ride-matching",
        version="v3.2.1",
        company="ola",
        environment="production",
        region="delhi",
        resource_requests={"cpu": "1000m", "memory": "1Gi"},
        resource_limits={"cpu": "4000m", "memory": "4Gi"},
        ports=[8000, 8080],
        health_check_path="/health"
    )
    
    generator = BigBasketK8sGenerator()
    
    # Generate manifests for all companies
    companies = [
        ("bigbasket", bigbasket_config),
        ("zomato", zomato_config),
        ("ola", ola_config)
    ]
    
    for company_name, config in companies:
        print(f"\\n🏢 Generating Kubernetes manifests for {company_name.upper()}...")
        
        manifests = generator.generate_all_manifests(config)
        output_dir = f"/tmp/{company_name}_k8s_manifests"
        generator.save_manifests_to_files(manifests, output_dir)
        
        print(f"📂 {company_name} manifests saved in: {output_dir}")
    
    print("\\n🎉 All Kubernetes manifests generated successfully!")
    print("Ready for Indian production deployment! 🇮🇳")
    
    # Print deployment commands
    print("\\n📋 Deployment commands:")
    for company_name, config in companies:
        print(f"\\n# {company_name.upper()} deployment:")
        print(f"kubectl apply -f /tmp/{company_name}_k8s_manifests/")
        print(f"kubectl get pods -n {config.namespace}")
        print(f"kubectl logs -f deployment/{config.app_name} -n {config.namespace}")

if __name__ == "__main__":
    main()

# Usage examples:
"""
# Generate all manifests:
python 03_kubernetes_deployment_manifests.py

# Deploy BigBasket inventory service:
kubectl apply -f /tmp/bigbasket_k8s_manifests/

# Check deployment status:
kubectl get deployment inventory-service -n bigbasket-prod

# Scale manually:
kubectl scale deployment inventory-service --replicas=10 -n bigbasket-prod

# Check HPA status:
kubectl get hpa inventory-service-hpa -n bigbasket-prod

# Port forward for testing:
kubectl port-forward service/inventory-service-service 8000:8000 -n bigbasket-prod

# Check logs:
kubectl logs -f deployment/inventory-service -n bigbasket-prod
"""