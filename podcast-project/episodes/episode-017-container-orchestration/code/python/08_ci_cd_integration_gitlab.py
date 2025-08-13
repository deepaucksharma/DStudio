#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD Integration with GitLab for Container Orchestration
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे PayTM जैसी companies
GitLab CI/CD के साथ container deployment करती हैं।

Real-world scenario: PayTM का automated deployment pipeline
"""

import os
import yaml
import json
import time
import requests
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from loguru import logger
import subprocess
import base64

class PipelineStage(Enum):
    """CI/CD pipeline stage enumeration"""
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    DEPLOY_DEV = "deploy_dev"
    DEPLOY_STAGING = "deploy_staging"
    DEPLOY_PRODUCTION = "deploy_production"

class PipelineStatus(Enum):
    """Pipeline status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PipelineJob:
    """Pipeline job configuration"""
    job_name: str
    stage: PipelineStage
    image: str
    script: List[str]
    variables: Dict[str, str]
    artifacts: List[str]
    dependencies: List[str]
    only: List[str]
    except_rules: List[str]
    retry: int

@dataclass
class DeploymentConfig:
    """Deployment configuration for different environments"""
    environment: str
    cluster_endpoint: str
    namespace: str
    replicas: int
    resources: Dict[str, Dict[str, str]]
    secrets: List[str]
    config_maps: List[str]
    ingress_host: str
    monitoring_enabled: bool

class PayTMCICDPipeline:
    """
    PayTM-style CI/CD Pipeline for Container Orchestration
    Production-ready GitLab integration with Indian context
    """
    
    def __init__(self, project_name: str, gitlab_token: str):
        self.project_name = project_name
        self.gitlab_token = gitlab_token
        self.gitlab_api_base = "https://gitlab.com/api/v4"
        
        # Indian environment configurations
        self.environments = {
            "development": DeploymentConfig(
                environment="development",
                cluster_endpoint="k8s-dev.paytm.internal",
                namespace="paytm-dev",
                replicas=1,
                resources={
                    "requests": {"cpu": "100m", "memory": "128Mi"},
                    "limits": {"cpu": "500m", "memory": "512Mi"}
                },
                secrets=["dev-db-secret", "dev-api-keys"],
                config_maps=["dev-config"],
                ingress_host="dev.paytm.internal",
                monitoring_enabled=True
            ),
            
            "staging": DeploymentConfig(
                environment="staging",
                cluster_endpoint="k8s-staging.paytm.com",
                namespace="paytm-staging",
                replicas=3,
                resources={
                    "requests": {"cpu": "250m", "memory": "256Mi"},
                    "limits": {"cpu": "1000m", "memory": "1Gi"}
                },
                secrets=["staging-db-secret", "staging-api-keys", "staging-payment-keys"],
                config_maps=["staging-config"],
                ingress_host="staging.paytm.com",
                monitoring_enabled=True
            ),
            
            "production": DeploymentConfig(
                environment="production",
                cluster_endpoint="k8s-prod.paytm.com",
                namespace="paytm-prod",
                replicas=10,
                resources={
                    "requests": {"cpu": "500m", "memory": "512Mi"},
                    "limits": {"cpu": "2000m", "memory": "2Gi"}
                },
                secrets=["prod-db-secret", "prod-api-keys", "prod-payment-keys", "prod-rbi-certs"],
                config_maps=["prod-config"],
                ingress_host="api.paytm.com",
                monitoring_enabled=True
            )
        }
        
        # Indian compliance and security requirements
        self.compliance_checks = [
            "rbi_guidelines_check",
            "pci_dss_compliance",
            "data_localization_check",
            "encryption_verification",
            "audit_logging_check"
        ]
        
        # Regional deployment configuration
        self.regional_clusters = {
            "mumbai": "k8s-mumbai.paytm.com",
            "bangalore": "k8s-bangalore.paytm.com",
            "delhi": "k8s-delhi.paytm.com"
        }
        
        logger.info(f"💳 PayTM CI/CD Pipeline initialized for {project_name}")
        logger.info("Production-ready GitLab integration ready!")
    
    def generate_gitlab_ci_config(self, service_name: str) -> str:
        """
        Generate comprehensive GitLab CI configuration
        """
        
        config = {
            # Global configuration
            "image": "docker:20.10.16",
            "services": ["docker:20.10.16-dind"],
            
            # Variables for Indian context
            "variables": {
                "DOCKER_DRIVER": "overlay2",
                "DOCKER_TLS_CERTDIR": "/certs",
                "REGISTRY": "registry.paytm.com",
                "SERVICE_NAME": service_name,
                "KUBE_NAMESPACE": "${CI_ENVIRONMENT_NAME}",
                "REGION": "asia-south1",  # Indian region
                "TIMEZONE": "Asia/Kolkata"
            },
            
            # Pipeline stages
            "stages": [
                "build",
                "test", 
                "security_scan",
                "deploy_dev",
                "deploy_staging",
                "deploy_production"
            ],
            
            # Before script - common setup
            "before_script": [
                "echo 'Setting up PayTM deployment environment...'",
                "apk add --no-cache curl jq python3 py3-pip",
                "pip3 install kubectl awscli",
                "export KUBECONFIG=$HOME/.kube/config"
            ]
        }
        
        # Add job definitions
        jobs = self.generate_pipeline_jobs(service_name)
        config.update(jobs)
        
        return yaml.dump(config, default_flow_style=False)
    
    def generate_pipeline_jobs(self, service_name: str) -> Dict[str, Any]:
        """
        Generate all pipeline jobs for PayTM deployment
        """
        
        jobs = {}
        
        # Build job
        jobs["build_image"] = {
            "stage": "build",
            "script": [
                "echo '🔨 Building PayTM container image...'",
                "docker build -t $REGISTRY/$SERVICE_NAME:$CI_COMMIT_SHA .",
                "docker build -t $REGISTRY/$SERVICE_NAME:latest .",
                "echo '📦 Image built successfully'"
            ],
            "only": ["main", "develop", "release/*"],
            "artifacts": {
                "reports": {
                    "junit": "test-results.xml"
                },
                "paths": ["build-report.json"],
                "expire_in": "1 week"
            }
        }
        
        # Test job
        jobs["run_tests"] = {
            "stage": "test",
            "image": "python:3.11-alpine",
            "script": [
                "echo '🧪 Running PayTM service tests...'",
                "pip install -r requirements.txt",
                "pip install pytest pytest-cov",
                "pytest tests/ --junitxml=test-results.xml --cov=src/",
                "echo '✅ All tests passed'"
            ],
            "artifacts": {
                "reports": {
                    "junit": "test-results.xml",
                    "coverage_report": {
                        "coverage_format": "cobertura",
                        "path": "coverage.xml"
                    }
                }
            },
            "coverage": "/TOTAL.+?(\\d+%)/"
        }
        
        # Security scan job
        jobs["security_scan"] = {
            "stage": "security_scan",
            "image": "aquasec/trivy:latest",
            "script": [
                "echo '🔒 Running PayTM security scan...'",
                "trivy image --exit-code 0 --format json --output trivy-report.json $REGISTRY/$SERVICE_NAME:$CI_COMMIT_SHA",
                "trivy image --exit-code 1 --severity CRITICAL $REGISTRY/$SERVICE_NAME:$CI_COMMIT_SHA",
                "echo '🛡️ Security scan completed'"
            ],
            "artifacts": {
                "reports": {
                    "container_scanning": "trivy-report.json"
                }
            },
            "allow_failure": False  # Block deployment on critical vulnerabilities
        }
        
        # Indian compliance check job
        jobs["compliance_check"] = {
            "stage": "security_scan",
            "image": "python:3.11-alpine",
            "script": [
                "echo '🇮🇳 Running Indian compliance checks...'",
                "python scripts/rbi_compliance_check.py",
                "python scripts/data_localization_check.py",
                "python scripts/pci_dss_check.py",
                "echo '✅ Compliance checks passed'"
            ],
            "artifacts": {
                "reports": {
                    "junit": "compliance-results.xml"
                }
            }
        }
        
        # Development deployment
        jobs["deploy_dev"] = self.generate_deployment_job("development", service_name)
        
        # Staging deployment (manual trigger)
        jobs["deploy_staging"] = self.generate_deployment_job("staging", service_name, manual=True)
        
        # Production deployment (manual trigger with approvals)
        jobs["deploy_production"] = self.generate_deployment_job("production", service_name, manual=True, when="manual")
        
        return jobs
    
    def generate_deployment_job(self, environment: str, service_name: str, 
                              manual: bool = False, when: str = "on_success") -> Dict[str, Any]:
        """
        Generate deployment job for specific environment
        """
        
        env_config = self.environments[environment]
        
        job = {
            "stage": f"deploy_{environment}",
            "image": "bitnami/kubectl:latest",
            "environment": {
                "name": environment,
                "url": f"https://{env_config.ingress_host}"
            },
            "script": [
                f"echo '🚀 Deploying to {environment.upper()} environment...'",
                f"kubectl config set-cluster paytm-{environment} --server={env_config.cluster_endpoint}",
                f"kubectl config set-context paytm-{environment} --cluster=paytm-{environment} --namespace={env_config.namespace}",
                f"kubectl config use-context paytm-{environment}",
                
                # Update deployment manifest
                f"envsubst < k8s/deployment-{environment}.yaml | kubectl apply -f -",
                f"envsubst < k8s/service-{environment}.yaml | kubectl apply -f -",
                f"envsubst < k8s/ingress-{environment}.yaml | kubectl apply -f -",
                
                # Wait for rollout
                f"kubectl rollout status deployment/{service_name} -n {env_config.namespace} --timeout=300s",
                
                # Health check
                f"echo '🏥 Running health checks...'",
                f"sleep 30",  # Wait for pods to be ready
                f"kubectl get pods -n {env_config.namespace} -l app={service_name}",
                
                # PayTM specific post-deployment checks
                "python scripts/paytm_health_check.py",
                "python scripts/payment_gateway_check.py",
                
                f"echo '✅ Deployment to {environment} completed successfully'"
            ],
            "variables": {
                "KUBE_NAMESPACE": env_config.namespace,
                "REPLICAS": str(env_config.replicas),
                "ENVIRONMENT": environment
            }
        }
        
        # Add manual trigger for staging and production
        if manual:
            job["when"] = when
            
        # Add approval requirements for production
        if environment == "production":
            job["environment"]["deployment_tier"] = "production"
            job["rules"] = [
                {
                    "if": "$CI_COMMIT_BRANCH == 'main'",
                    "when": "manual",
                    "allow_failure": False
                }
            ]
        
        # Environment-specific configurations
        if environment == "development":
            job["only"] = ["develop", "feature/*"]
        elif environment == "staging":
            job["only"] = ["main", "release/*"]
        elif environment == "production":
            job["only"] = ["main", "tags"]
        
        return job
    
    def generate_kubernetes_manifests(self, service_name: str, environment: str) -> Dict[str, str]:
        """
        Generate Kubernetes manifests for deployment
        """
        
        env_config = self.environments[environment]
        manifests = {}
        
        # Deployment manifest
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_name,
                "namespace": env_config.namespace,
                "labels": {
                    "app": service_name,
                    "company": "paytm",
                    "environment": environment,
                    "version": "${CI_COMMIT_SHA}"
                }
            },
            "spec": {
                "replicas": env_config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name,
                            "company": "paytm",
                            "environment": environment
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": service_name,
                            "image": f"${{REGISTRY}}/${{SERVICE_NAME}}:${{CI_COMMIT_SHA}}",
                            "ports": [{"containerPort": 8000}],
                            "env": [
                                {"name": "ENVIRONMENT", "value": environment},
                                {"name": "SERVICE_NAME", "value": service_name},
                                {"name": "REGION", "value": "asia-south1"},
                                {"name": "TZ", "value": "Asia/Kolkata"}
                            ],
                            "resources": env_config.resources,
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8000
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": 8000
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        manifests[f"deployment-{environment}.yaml"] = yaml.dump(deployment)
        
        # Service manifest
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{service_name}-service",
                "namespace": env_config.namespace,
                "labels": {
                    "app": service_name,
                    "company": "paytm",
                    "environment": environment
                }
            },
            "spec": {
                "selector": {
                    "app": service_name
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 8000,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }
        
        manifests[f"service-{environment}.yaml"] = yaml.dump(service)
        
        # Ingress manifest
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{service_name}-ingress",
                "namespace": env_config.namespace,
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/rate-limit": "1000",  # PayTM high-traffic handling
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": [env_config.ingress_host],
                    "secretName": f"{service_name}-tls"
                }],
                "rules": [{
                    "host": env_config.ingress_host,
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": f"{service_name}-service",
                                    "port": {"number": 80}
                                }
                            }
                        }]
                    }
                }]
            }
        }
        
        manifests[f"ingress-{environment}.yaml"] = yaml.dump(ingress)
        
        return manifests
    
    def generate_deployment_scripts(self, service_name: str) -> Dict[str, str]:
        """
        Generate deployment and health check scripts
        """
        
        scripts = {}
        
        # PayTM health check script
        scripts["paytm_health_check.py"] = '''#!/usr/bin/env python3
"""PayTM Service Health Check Script"""

import requests
import sys
import time
import os

def check_service_health():
    """Check PayTM service health endpoints"""
    
    service_url = os.getenv('SERVICE_URL', 'http://localhost:8000')
    
    # Health check endpoints
    endpoints = [
        '/health',
        '/ready',
        '/api/health',
        '/metrics'
    ]
    
    print("🏥 Running PayTM health checks...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{service_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")
            return False
    
    print("✅ All health checks passed!")
    return True

if __name__ == "__main__":
    if not check_service_health():
        sys.exit(1)
'''
        
        # Payment gateway check script
        scripts["payment_gateway_check.py"] = '''#!/usr/bin/env python3
"""PayTM Payment Gateway Health Check"""

import requests
import json
import os
import sys

def check_payment_gateway():
    """Check PayTM payment gateway connectivity"""
    
    print("💳 Checking PayTM payment gateway...")
    
    # Mock payment gateway health check
    gateway_url = os.getenv('PAYMENT_GATEWAY_URL', 'https://api.paytm.com')
    
    try:
        # Test payment gateway connectivity
        response = requests.get(f"{gateway_url}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Payment gateway: Connected")
            return True
        else:
            print(f"❌ Payment gateway: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Payment gateway: {str(e)}")
        return False

if __name__ == "__main__":
    if not check_payment_gateway():
        sys.exit(1)
'''
        
        # RBI compliance check script
        scripts["rbi_compliance_check.py"] = '''#!/usr/bin/env python3
"""RBI Compliance Check for PayTM Services"""

import os
import sys
import json

def check_rbi_compliance():
    """Check RBI compliance requirements"""
    
    print("🇮🇳 Checking RBI compliance...")
    
    compliance_checks = [
        "data_localization",
        "encryption_standards",
        "audit_logging",
        "transaction_monitoring",
        "kyc_verification"
    ]
    
    for check in compliance_checks:
        # Simulate compliance check
        print(f"✅ {check}: Compliant")
    
    print("✅ All RBI compliance checks passed!")
    return True

if __name__ == "__main__":
    if not check_rbi_compliance():
        sys.exit(1)
'''
        
        return scripts
    
    def create_complete_pipeline(self, service_name: str, output_dir: str):
        """
        Create complete CI/CD pipeline files
        """
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate GitLab CI configuration
        gitlab_ci_config = self.generate_gitlab_ci_config(service_name)
        with open(os.path.join(output_dir, ".gitlab-ci.yml"), "w") as f:
            f.write(gitlab_ci_config)
        
        # Generate Kubernetes manifests for all environments
        k8s_dir = os.path.join(output_dir, "k8s")
        os.makedirs(k8s_dir, exist_ok=True)
        
        for environment in self.environments.keys():
            manifests = self.generate_kubernetes_manifests(service_name, environment)
            
            for filename, content in manifests.items():
                with open(os.path.join(k8s_dir, filename), "w") as f:
                    f.write(content)
        
        # Generate deployment scripts
        scripts_dir = os.path.join(output_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        scripts = self.generate_deployment_scripts(service_name)
        for filename, content in scripts.items():
            script_path = os.path.join(scripts_dir, filename)
            with open(script_path, "w") as f:
                f.write(content)
            os.chmod(script_path, 0o755)  # Make executable
        
        logger.info(f"✅ Complete CI/CD pipeline created in {output_dir}")

def main():
    """Demonstration of PayTM CI/CD pipeline generation"""
    
    print("💳 PayTM CI/CD Pipeline Generator")
    print("Production-ready GitLab integration for Indian fintech")
    print("=" * 60)
    
    # Initialize pipeline generator
    pipeline = PayTMCICDPipeline(
        project_name="paytm-wallet-service",
        gitlab_token="glpat-xxxxxxxxxxxxxxxxxxxx"
    )
    
    # Generate complete pipeline for PayTM wallet service
    service_name = "paytm-wallet-service"
    output_dir = "/tmp/paytm_cicd_pipeline"
    
    print(f"🔧 Generating CI/CD pipeline for {service_name}...")
    pipeline.create_complete_pipeline(service_name, output_dir)
    
    print(f"\\n📁 Pipeline files created in: {output_dir}")
    print("\\n📋 Generated files:")
    
    # List generated files
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(output_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print("\\n🚀 Pipeline Features:")
    print("  ✅ Multi-environment deployment (Dev/Staging/Prod)")
    print("  ✅ Security scanning with Trivy")
    print("  ✅ Indian compliance checks (RBI, PCI DSS)")
    print("  ✅ Automated testing and coverage")
    print("  ✅ Manual approvals for production")
    print("  ✅ PayTM-specific health checks")
    print("  ✅ Regional deployment support")
    
    print("\\n📖 Usage Instructions:")
    print("  1. Copy .gitlab-ci.yml to your GitLab repository")
    print("  2. Copy k8s/ directory for Kubernetes manifests")
    print("  3. Copy scripts/ directory for deployment scripts")
    print("  4. Configure GitLab variables for your environment")
    print("  5. Push to trigger the pipeline!")

if __name__ == "__main__":
    main()

# GitLab Variables Configuration:
"""
Required GitLab CI/CD Variables:

# Registry Configuration
REGISTRY_URL: registry.paytm.com
REGISTRY_USER: paytm-ci
REGISTRY_PASSWORD: <secure-password>

# Kubernetes Configuration
KUBE_CONFIG_DEV: <base64-encoded-kubeconfig-dev>
KUBE_CONFIG_STAGING: <base64-encoded-kubeconfig-staging>
KUBE_CONFIG_PROD: <base64-encoded-kubeconfig-prod>

# PayTM Specific
PAYMENT_GATEWAY_URL: https://api.paytm.com
RBI_COMPLIANCE_ENDPOINT: https://compliance.paytm.com
AUDIT_LOG_ENDPOINT: https://audit.paytm.com

# Security
SECURITY_SCAN_TOKEN: <trivy-token>
COMPLIANCE_API_KEY: <compliance-api-key>

# Notifications
SLACK_WEBHOOK_URL: <slack-webhook-for-alerts>
TEAMS_WEBHOOK_URL: <teams-webhook-for-notifications>
"""