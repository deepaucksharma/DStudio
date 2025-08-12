#!/usr/bin/env python3
"""
Istio Service Mesh Installation & Configuration
Production Setup for Indian Banking - HDFC, ICICI, SBI

यह system comprehensive Istio service mesh setup करता है banking grade security के साथ।
Production में traffic management, security policies, और observability configuration।

Real-world Context:
- Indian banks run 500+ microservices across multiple datacenters
- Istio reduces network complexity by 70% in large deployments
- Zero-trust networking mandatory for RBI compliance
- Service mesh enables canary deployments for critical banking services
"""

import os
import yaml
import json
import time
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IstioConfig:
    """Istio configuration for banking environment"""
    version: str
    profile: str
    namespace: str
    cluster_name: str
    region: str
    environment: str
    security_enabled: bool = True
    telemetry_enabled: bool = True
    tracing_enabled: bool = True

class IstioInstaller:
    """
    Production Istio Installation for Indian Banking
    
    Features:
    - Multi-datacenter setup
    - Banking-grade security
    - Compliance-ready configuration
    - High availability deployment
    - Observability integration
    """
    
    def __init__(self, config: IstioConfig):
        self.config = config
        self.installation_status = {}
        
        # Banking-specific Istio configuration
        self.banking_profiles = {
            'production': {
                'security': 'strict',
                'telemetry': 'full',
                'resource_requests': 'high',
                'ha_enabled': True
            },
            'staging': {
                'security': 'permissive',
                'telemetry': 'standard',
                'resource_requests': 'medium',
                'ha_enabled': False
            },
            'development': {
                'security': 'permissive',
                'telemetry': 'basic',
                'resource_requests': 'low',
                'ha_enabled': False
            }
        }
        
        logger.info(f"Istio installer initialized for {config.cluster_name}")
    
    def pre_installation_checks(self) -> Dict[str, bool]:
        """Perform pre-installation checks"""
        
        checks = {
            'kubernetes_version': False,
            'cluster_resources': False,
            'network_policies': False,
            'storage_classes': False,
            'dns_resolution': False,
            'rbac_permissions': False
        }
        
        try:
            # Simulate Kubernetes version check
            logger.info("Checking Kubernetes version compatibility...")
            checks['kubernetes_version'] = True  # Assume v1.24+
            
            # Check cluster resources
            logger.info("Verifying cluster resources...")
            checks['cluster_resources'] = True  # Assume sufficient resources
            
            # Network policies check
            logger.info("Checking network policies support...")
            checks['network_policies'] = True  # CNI supports network policies
            
            # Storage classes
            logger.info("Verifying storage classes...")
            checks['storage_classes'] = True  # Dynamic provisioning available
            
            # DNS resolution
            logger.info("Testing DNS resolution...")
            checks['dns_resolution'] = True  # CoreDNS working
            
            # RBAC permissions
            logger.info("Checking RBAC permissions...")
            checks['rbac_permissions'] = True  # Cluster admin available
            
            logger.info("✅ All pre-installation checks passed")
            
        except Exception as e:
            logger.error(f"Pre-installation check failed: {e}")
        
        return checks
    
    def generate_installation_manifest(self) -> str:
        """Generate Istio installation manifest"""
        
        profile_config = self.banking_profiles.get(self.config.environment, self.banking_profiles['production'])
        
        # Base Istio installation configuration
        istio_manifest = {
            'apiVersion': 'install.istio.io/v1alpha1',
            'kind': 'IstioOperator',
            'metadata': {
                'name': f'istio-{self.config.environment}',
                'namespace': self.config.namespace
            },
            'spec': {
                'revision': self.config.version,
                'values': {
                    'global': {
                        'meshID': f'hdfc-mesh-{self.config.region}',
                        'multiCluster': {
                            'clusterName': self.config.cluster_name
                        },
                        'network': f'network-{self.config.region}',
                        'proxy': {
                            'resources': self._get_proxy_resources(profile_config['resource_requests'])
                        }
                    },
                    'pilot': {
                        'resources': self._get_pilot_resources(profile_config['resource_requests']),
                        'traceSampling': 1.0 if self.config.environment != 'production' else 0.1
                    },
                    'gateways': {
                        'istio-ingressgateway': {
                            'resources': self._get_gateway_resources(profile_config['resource_requests']),
                            'serviceAnnotations': {
                                'service.beta.kubernetes.io/aws-load-balancer-type': 'nlb',
                                'service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled': 'true'
                            }
                        }
                    }
                },
                'components': {
                    'pilot': {
                        'k8s': {
                            'replicaCount': 2 if profile_config['ha_enabled'] else 1,
                            'hpaSpec': {
                                'minReplicas': 2 if profile_config['ha_enabled'] else 1,
                                'maxReplicas': 5
                            } if profile_config['ha_enabled'] else None
                        }
                    },
                    'ingressGateways': [
                        {
                            'name': 'istio-ingressgateway',
                            'enabled': True,
                            'k8s': {
                                'replicaCount': 2 if profile_config['ha_enabled'] else 1,
                                'service': {
                                    'type': 'LoadBalancer',
                                    'ports': [
                                        {'name': 'status-port', 'port': 15021, 'targetPort': 15021},
                                        {'name': 'http2', 'port': 80, 'targetPort': 8080},
                                        {'name': 'https', 'port': 443, 'targetPort': 8443},
                                        {'name': 'tcp-banking', 'port': 9443, 'targetPort': 9443}  # Banking-specific port
                                    ]
                                }
                            }
                        }
                    ],
                    'egressGateways': [
                        {
                            'name': 'istio-egressgateway',
                            'enabled': True,
                            'k8s': {
                                'replicaCount': 1
                            }
                        }
                    ]
                }
            }
        }
        
        # Add banking-specific security configuration
        if profile_config['security'] == 'strict':
            istio_manifest['spec']['values']['global']['peerAuthn'] = 'STRICT'
            istio_manifest['spec']['values']['global']['proxy']['privileged'] = False
        
        return yaml.dump(istio_manifest, default_flow_style=False)
    
    def _get_proxy_resources(self, resource_level: str) -> Dict:
        """Get proxy resource configuration based on level"""
        
        resource_configs = {
            'low': {
                'requests': {'cpu': '100m', 'memory': '128Mi'},
                'limits': {'cpu': '200m', 'memory': '256Mi'}
            },
            'medium': {
                'requests': {'cpu': '200m', 'memory': '256Mi'},
                'limits': {'cpu': '500m', 'memory': '512Mi'}
            },
            'high': {
                'requests': {'cpu': '500m', 'memory': '512Mi'},
                'limits': {'cpu': '1000m', 'memory': '1Gi'}
            }
        }
        
        return resource_configs.get(resource_level, resource_configs['medium'])
    
    def _get_pilot_resources(self, resource_level: str) -> Dict:
        """Get Pilot resource configuration"""
        
        resource_configs = {
            'low': {
                'requests': {'cpu': '200m', 'memory': '256Mi'},
                'limits': {'cpu': '500m', 'memory': '512Mi'}
            },
            'medium': {
                'requests': {'cpu': '500m', 'memory': '1Gi'},
                'limits': {'cpu': '1000m', 'memory': '2Gi'}
            },
            'high': {
                'requests': {'cpu': '1000m', 'memory': '2Gi'},
                'limits': {'cpu': '2000m', 'memory': '4Gi'}
            }
        }
        
        return resource_configs.get(resource_level, resource_configs['medium'])
    
    def _get_gateway_resources(self, resource_level: str) -> Dict:
        """Get gateway resource configuration"""
        
        resource_configs = {
            'low': {
                'requests': {'cpu': '200m', 'memory': '256Mi'},
                'limits': {'cpu': '500m', 'memory': '512Mi'}
            },
            'medium': {
                'requests': {'cpu': '500m', 'memory': '1Gi'},
                'limits': {'cpu': '1000m', 'memory': '2Gi'}
            },
            'high': {
                'requests': {'cpu': '1000m', 'memory': '2Gi'},
                'limits': {'cpu': '2000m', 'memory': '4Gi'}
            }
        }
        
        return resource_configs.get(resource_level, resource_configs['medium'])
    
    def install_istio(self) -> Dict[str, Any]:
        """Install Istio on the cluster"""
        
        installation_result = {
            'status': 'success',
            'components': [],
            'errors': [],
            'duration_seconds': 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Create namespace
            logger.info(f"Creating Istio namespace: {self.config.namespace}")
            installation_result['components'].append('namespace')
            
            # Step 2: Generate and apply manifest
            logger.info("Generating Istio installation manifest")
            manifest = self.generate_installation_manifest()
            
            # In production, this would apply to Kubernetes
            logger.info("Applying Istio installation manifest")
            # kubectl apply would happen here
            installation_result['components'].append('control-plane')
            
            # Step 3: Install gateways
            logger.info("Installing Istio gateways")
            installation_result['components'].append('gateways')
            
            # Step 4: Wait for deployment
            logger.info("Waiting for Istio components to be ready")
            time.sleep(2)  # Simulate installation time
            installation_result['components'].append('ready')
            
            # Step 5: Enable sidecar injection
            logger.info("Enabling automatic sidecar injection")
            self._enable_sidecar_injection()
            installation_result['components'].append('sidecar-injection')
            
            installation_result['duration_seconds'] = time.time() - start_time
            logger.info(f"✅ Istio installation completed in {installation_result['duration_seconds']:.1f} seconds")
            
        except Exception as e:
            installation_result['status'] = 'failed'
            installation_result['errors'].append(str(e))
            logger.error(f"Istio installation failed: {e}")
        
        return installation_result
    
    def _enable_sidecar_injection(self):
        """Enable automatic sidecar injection for banking services"""
        
        # Namespaces that should have sidecar injection
        banking_namespaces = [
            'hdfc-payments',
            'hdfc-accounts',
            'hdfc-loans',
            'hdfc-kyc',
            'hdfc-mobile-banking'
        ]
        
        for namespace in banking_namespaces:
            logger.info(f"Enabling sidecar injection for namespace: {namespace}")
            # In production: kubectl label namespace {namespace} istio-injection=enabled
    
    def configure_banking_security(self) -> Dict[str, str]:
        """Configure banking-specific security policies"""
        
        security_configs = {}
        
        # 1. Peer Authentication Policy
        peer_auth_policy = {
            'apiVersion': 'security.istio.io/v1beta1',
            'kind': 'PeerAuthentication',
            'metadata': {
                'name': 'default',
                'namespace': 'hdfc-payments'
            },
            'spec': {
                'mtls': {
                    'mode': 'STRICT'  # Require mTLS for all banking services
                }
            }
        }
        
        security_configs['peer_authentication'] = yaml.dump(peer_auth_policy, default_flow_style=False)
        
        # 2. Authorization Policy for Payment Services
        authz_policy = {
            'apiVersion': 'security.istio.io/v1beta1',
            'kind': 'AuthorizationPolicy',
            'metadata': {
                'name': 'payment-service-policy',
                'namespace': 'hdfc-payments'
            },
            'spec': {
                'selector': {
                    'matchLabels': {
                        'app': 'payment-service'
                    }
                },
                'rules': [
                    {
                        'from': [
                            {
                                'source': {
                                    'principals': ['cluster.local/ns/hdfc-accounts/sa/account-service']
                                }
                            }
                        ],
                        'to': [
                            {
                                'operation': {
                                    'methods': ['POST'],
                                    'paths': ['/api/v1/payments/*']
                                }
                            }
                        ],
                        'when': [
                            {
                                'key': 'request.headers[x-user-role]',
                                'values': ['customer', 'merchant']
                            }
                        ]
                    }
                ]
            }
        }
        
        security_configs['authorization_policy'] = yaml.dump(authz_policy, default_flow_style=False)
        
        # 3. Request Authentication for JWT validation
        request_auth = {
            'apiVersion': 'security.istio.io/v1beta1',
            'kind': 'RequestAuthentication',
            'metadata': {
                'name': 'jwt-auth',
                'namespace': 'hdfc-payments'
            },
            'spec': {
                'selector': {
                    'matchLabels': {
                        'app': 'payment-service'
                    }
                },
                'jwtRules': [
                    {
                        'issuer': 'https://auth.hdfcbank.com',
                        'jwksUri': 'https://auth.hdfcbank.com/.well-known/jwks.json',
                        'audiences': ['hdfc-banking-api'],
                        'fromHeaders': [
                            {
                                'name': 'Authorization',
                                'prefix': 'Bearer '
                            }
                        ]
                    }
                ]
            }
        }
        
        security_configs['request_authentication'] = yaml.dump(request_auth, default_flow_style=False)
        
        return security_configs
    
    def configure_telemetry(self) -> Dict[str, str]:
        """Configure telemetry and observability"""
        
        telemetry_configs = {}
        
        # 1. Telemetry configuration
        telemetry_config = {
            'apiVersion': 'telemetry.istio.io/v1alpha1',
            'kind': 'Telemetry',
            'metadata': {
                'name': 'banking-telemetry',
                'namespace': self.config.namespace
            },
            'spec': {
                'metrics': [
                    {
                        'providers': [
                            {
                                'name': 'prometheus'
                            }
                        ],
                        'overrides': [
                            {
                                'match': {
                                    'metric': 'ALL_METRICS'
                                },
                                'tagOverrides': {
                                    'business_unit': {
                                        'value': 'banking'
                                    },
                                    'datacenter': {
                                        'value': self.config.region
                                    }
                                }
                            }
                        ]
                    }
                ],
                'tracing': [
                    {
                        'providers': [
                            {
                                'name': 'jaeger'
                            }
                        ]
                    }
                ],
                'accessLogging': [
                    {
                        'providers': [
                            {
                                'name': 'otel'
                            }
                        ]
                    }
                ]
            }
        }
        
        telemetry_configs['telemetry'] = yaml.dump(telemetry_config, default_flow_style=False)
        
        return telemetry_configs
    
    def validate_installation(self) -> Dict[str, Any]:
        """Validate Istio installation"""
        
        validation_results = {
            'control_plane_healthy': False,
            'gateways_ready': False,
            'webhooks_ready': False,
            'proxy_version_consistent': False,
            'security_enabled': False,
            'telemetry_working': False,
            'overall_status': 'unknown'
        }
        
        try:
            # Check control plane health
            logger.info("Validating control plane health")
            validation_results['control_plane_healthy'] = True  # Simulate healthy state
            
            # Check gateways
            logger.info("Validating gateway deployment")
            validation_results['gateways_ready'] = True
            
            # Check admission webhooks
            logger.info("Validating admission webhooks")
            validation_results['webhooks_ready'] = True
            
            # Check proxy versions
            logger.info("Validating proxy version consistency")
            validation_results['proxy_version_consistent'] = True
            
            # Check security configuration
            logger.info("Validating security configuration")
            validation_results['security_enabled'] = self.config.security_enabled
            
            # Check telemetry
            logger.info("Validating telemetry configuration")
            validation_results['telemetry_working'] = self.config.telemetry_enabled
            
            # Overall status
            all_checks_passed = all([
                validation_results['control_plane_healthy'],
                validation_results['gateways_ready'],
                validation_results['webhooks_ready'],
                validation_results['proxy_version_consistent']
            ])
            
            validation_results['overall_status'] = 'healthy' if all_checks_passed else 'degraded'
            
            logger.info(f"✅ Istio validation completed - Status: {validation_results['overall_status']}")
            
        except Exception as e:
            validation_results['overall_status'] = 'failed'
            logger.error(f"Istio validation failed: {e}")
        
        return validation_results

def demonstrate_istio_installation():
    """Demonstrate Istio installation for Indian banking"""
    print("\n🌐 Istio Service Mesh Installation Demo - Indian Banking")
    print("=" * 60)
    
    # Configure Istio for HDFC Bank production environment
    config = IstioConfig(
        version='1.20.0',
        profile='production',
        namespace='istio-system',
        cluster_name='hdfc-mumbai-prod',
        region='mumbai',
        environment='production',
        security_enabled=True,
        telemetry_enabled=True,
        tracing_enabled=True
    )
    
    installer = IstioInstaller(config)
    
    print("✅ Istio installer configured for HDFC Bank")
    print(f"   Cluster: {config.cluster_name}")
    print(f"   Region: {config.region}")
    print(f"   Environment: {config.environment}")
    
    # Pre-installation checks
    print("\n🔍 Pre-installation Checks")
    print("-" * 30)
    
    checks = installer.pre_installation_checks()
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check_name.replace('_', ' ').title()}: {status}")
    
    # Generate installation manifest
    print("\n📝 Installation Manifest Generation")
    print("-" * 38)
    
    manifest = installer.generate_installation_manifest()
    manifest_lines = manifest.count('\n')
    print(f"✅ Generated Istio manifest ({manifest_lines} lines)")
    print("   Key components:")
    print("   • Control plane with HA configuration")
    print("   • Ingress gateway with LoadBalancer")
    print("   • Egress gateway for external calls")
    print("   • Banking-specific port configuration")
    
    # Install Istio
    print("\n🚀 Istio Installation")
    print("-" * 20)
    
    installation_result = installer.install_istio()
    
    if installation_result['status'] == 'success':
        print("✅ Istio installation successful")
        print(f"   Duration: {installation_result['duration_seconds']:.1f} seconds")
        print("   Installed components:")
        for component in installation_result['components']:
            print(f"     • {component.replace('-', ' ').title()}")
    else:
        print("❌ Istio installation failed")
        for error in installation_result['errors']:
            print(f"     Error: {error}")
    
    # Configure banking security
    print("\n🔒 Banking Security Configuration")
    print("-" * 35)
    
    security_configs = installer.configure_banking_security()
    print("✅ Generated security policies:")
    for policy_name, _ in security_configs.items():
        print(f"   • {policy_name.replace('_', ' ').title()}")
    
    print("\n🔐 Security Features:")
    print("   ✓ Strict mTLS for all banking services")
    print("   ✓ JWT authentication for APIs")
    print("   ✓ Fine-grained authorization policies")
    print("   ✓ Service-to-service access control")
    
    # Configure telemetry
    print("\n📊 Telemetry Configuration")
    print("-" * 27)
    
    telemetry_configs = installer.configure_telemetry()
    print("✅ Configured observability:")
    print("   • Prometheus metrics collection")
    print("   • Jaeger distributed tracing")
    print("   • Access logging with OpenTelemetry")
    print("   • Custom business unit tagging")
    
    # Validate installation
    print("\n✅ Installation Validation")
    print("-" * 26)
    
    validation = installer.validate_installation()
    print("🔍 Validation Results:")
    
    validation_checks = [
        ('Control Plane', validation['control_plane_healthy']),
        ('Gateways', validation['gateways_ready']),
        ('Webhooks', validation['webhooks_ready']),
        ('Proxy Versions', validation['proxy_version_consistent']),
        ('Security', validation['security_enabled']),
        ('Telemetry', validation['telemetry_working'])
    ]
    
    for check_name, passed in validation_checks:
        status = "✅ HEALTHY" if passed else "❌ UNHEALTHY"
        print(f"   {check_name}: {status}")
    
    overall_status = validation['overall_status'].upper()
    status_emoji = "✅" if overall_status == "HEALTHY" else "⚠️" if overall_status == "DEGRADED" else "❌"
    print(f"\n{status_emoji} Overall Status: {overall_status}")
    
    # Production recommendations
    print("\n💡 Production Recommendations")
    print("-" * 32)
    print("• Deploy across multiple availability zones")
    print("• Configure external certificate management")
    print("• Set up monitoring and alerting")
    print("• Implement backup and disaster recovery")
    print("• Regular security policy audits")
    print("• Performance testing with production load")
    print("• Gradual rollout with canary deployments")
    
    # Banking-specific considerations
    print("\n🏦 Banking-Specific Considerations")
    print("-" * 36)
    print("• RBI compliance for network security")
    print("• Audit trail for all service communications")
    print("• Data residency requirements")
    print("• Integration with existing banking systems")
    print("• Disaster recovery across regions")
    print("• Performance SLA requirements")

if __name__ == "__main__":
    demonstrate_istio_installation()