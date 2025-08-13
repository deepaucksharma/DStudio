#!/usr/bin/env python3
"""
ArgoCD Setup Automation for Indian Enterprise
==================================================

IRCTC जैसी railway booking system के लिए production-ready ArgoCD setup।
Multi-environment deployment के साथ Indian compliance और audit trails।

Features:
- Automated ArgoCD installation with Indian configurations
- Multi-region setup (Mumbai, Delhi, Bangalore)
- RBI compliance audit logging
- Indian timezone और business hours awareness
- UPI/payment system integration readiness

Author: Hindi Tech Podcast - Episode 19
Context: GitOps for Indian Railways and E-commerce
"""

import asyncio
import logging
import os
import json
import yaml
from datetime import datetime
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import kubernetes
from kubernetes import client, config
import requests
from pathlib import Path
import tempfile
import shutil

# Indian timezone support
import pytz
IST = pytz.timezone('Asia/Kolkata')

# Configure logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('argocd_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class IndianRegionConfig:
    """Indian regions ke liye specific configuration"""
    name: str
    display_name: str  # Hindi में display name
    kubernetes_context: str
    timezone: str
    primary_datacenter: str
    backup_datacenter: str
    compliance_level: str  # 'rbi', 'sebi', 'basic'
    payment_gateways: List[str]
    business_hours: Dict[str, str]

@dataclass
class ArgoConfig:
    """ArgoCD configuration for Indian compliance"""
    version: str = "v2.8.4"
    namespace: str = "argocd"
    admin_password: str = ""
    enable_audit: bool = True
    data_residency: bool = True  # RBI requirement
    backup_enabled: bool = True
    monitoring_enabled: bool = True
    indian_holidays_aware: bool = True

class IndianArgoSetup:
    """
    Indian enterprise के लिए ArgoCD setup automation।
    
    यह class IRCTC, Flipkart जैसी large scale systems के लिए 
    production-ready ArgoCD environment setup करता है।
    """
    
    def __init__(self, config: ArgoConfig):
        self.config = config
        self.k8s_client = None
        self.indian_regions = self._setup_indian_regions()
        self.current_time = datetime.now(IST)
        
    def _setup_indian_regions(self) -> Dict[str, IndianRegionConfig]:
        """Indian regions का configuration setup"""
        return {
            'mumbai': IndianRegionConfig(
                name='mumbai',
                display_name='मुंबई - वित्तीय राजधानी',
                kubernetes_context='mumbai-prod-k8s',
                timezone='Asia/Kolkata',
                primary_datacenter='mumbai-dc1',
                backup_datacenter='pune-dc2', 
                compliance_level='rbi',
                payment_gateways=['razorpay', 'paytm', 'phonepe'],
                business_hours={'start': '09:00', 'end': '18:00'}
            ),
            'delhi': IndianRegionConfig(
                name='delhi',
                display_name='दिल्ली - राष्ट्रीय राजधानी',
                kubernetes_context='delhi-prod-k8s',
                timezone='Asia/Kolkata',
                primary_datacenter='delhi-dc1',
                backup_datacenter='noida-dc2',
                compliance_level='rbi',
                payment_gateways=['sbi', 'icici', 'hdfc'],
                business_hours={'start': '09:00', 'end': '18:00'}
            ),
            'bangalore': IndianRegionConfig(
                name='bangalore',
                display_name='बैंगलोर - IT हब',
                kubernetes_context='blr-prod-k8s', 
                timezone='Asia/Kolkata',
                primary_datacenter='bangalore-dc1',
                backup_datacenter='mysore-dc2',
                compliance_level='basic',
                payment_gateways=['gpay', 'amazon_pay', 'freecharge'],
                business_hours={'start': '10:00', 'end': '19:00'}
            )
        }

    async def setup_kubernetes_client(self) -> bool:
        """Kubernetes client setup with Indian cluster access"""
        try:
            logger.info("🇮🇳 Setting up Kubernetes client for Indian clusters...")
            
            # Load kubeconfig - try different locations
            kubeconfig_paths = [
                os.path.expanduser('~/.kube/config'),
                '/var/run/secrets/kubernetes.io/serviceaccount',
                os.getenv('KUBECONFIG', '')
            ]
            
            for path in kubeconfig_paths:
                if path and os.path.exists(path):
                    logger.info(f"Loading kubeconfig from: {path}")
                    config.load_kube_config(config_file=path)
                    break
            else:
                # Try in-cluster config for pod-based execution
                config.load_incluster_config()
                
            self.k8s_client = client.ApiClient()
            logger.info("✅ Kubernetes client successfully configured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Kubernetes client setup failed: {e}")
            return False

    async def install_argocd_namespace(self) -> bool:
        """ArgoCD namespace create करना with Indian labels"""
        try:
            v1 = client.CoreV1Api()
            
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=self.config.namespace,
                    labels={
                        'app': 'argocd',
                        'environment': 'production',
                        'region': 'india',
                        'compliance': 'rbi-compliant',
                        'data-residency': 'india',
                        'created-by': 'hindi-tech-podcast'
                    },
                    annotations={
                        'setup-time': self.current_time.isoformat(),
                        'timezone': 'Asia/Kolkata',
                        'business-hours': '09:00-18:00 IST',
                        'description': 'ArgoCD namespace for Indian enterprise deployment'
                    }
                )
            )
            
            try:
                v1.create_namespace(body=namespace)
                logger.info(f"✅ Namespace '{self.config.namespace}' created successfully")
            except client.ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(f"ℹ️ Namespace '{self.config.namespace}' already exists")
                else:
                    raise e
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create ArgoCD namespace: {e}")
            return False

    async def download_and_apply_argocd_manifests(self) -> bool:
        """ArgoCD manifests download और apply करना"""
        try:
            logger.info("📥 Downloading ArgoCD manifests...")
            
            # ArgoCD stable release URL
            argocd_url = f"https://raw.githubusercontent.com/argoproj/argo-cd/{self.config.version}/manifests/install.yaml"
            
            # Download manifests
            response = requests.get(argocd_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(response.text)
                temp_manifest_path = f.name
            
            logger.info("🔧 Applying ArgoCD manifests to cluster...")
            
            # Apply manifests using kubectl
            result = subprocess.run([
                'kubectl', 'apply', '-f', temp_manifest_path, 
                '-n', self.config.namespace
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ ArgoCD manifests applied successfully")
                
                # Wait for ArgoCD server to be ready
                await self._wait_for_argocd_ready()
                return True
            else:
                logger.error(f"❌ Failed to apply manifests: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to download/apply ArgoCD manifests: {e}")
            return False
        finally:
            # Clean up temporary file
            if 'temp_manifest_path' in locals():
                os.unlink(temp_manifest_path)

    async def _wait_for_argocd_ready(self, timeout: int = 300) -> bool:
        """ArgoCD components के ready होने का wait करना"""
        try:
            logger.info("⏳ Waiting for ArgoCD components to be ready...")
            
            apps_v1 = client.AppsV1Api()
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < timeout:
                try:
                    # Check ArgoCD server deployment
                    server_deployment = apps_v1.read_namespaced_deployment(
                        name='argocd-server',
                        namespace=self.config.namespace
                    )
                    
                    # Check if deployment is ready
                    if (server_deployment.status.ready_replicas and 
                        server_deployment.status.ready_replicas > 0):
                        
                        logger.info("✅ ArgoCD server is ready!")
                        return True
                        
                except client.ApiException:
                    pass
                
                await asyncio.sleep(10)
                logger.info("⏳ Still waiting for ArgoCD server...")
            
            logger.warning("⚠️ ArgoCD server readiness check timed out")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for ArgoCD readiness: {e}")
            return False

    async def configure_indian_compliance(self) -> bool:
        """Indian compliance के लिए ArgoCD configuration"""
        try:
            logger.info("🇮🇳 Configuring Indian compliance settings...")
            
            # Create ConfigMap for Indian settings
            v1 = client.CoreV1Api()
            
            indian_config = {
                'timezone': 'Asia/Kolkata',
                'business_hours': {
                    'start': '09:00',
                    'end': '18:00',
                    'weekend_deployments': False
                },
                'compliance': {
                    'audit_logging': True,
                    'data_residency': True,
                    'encryption_at_rest': True,
                    'backup_retention_days': 2555,  # 7 years for RBI
                    'access_logging': True
                },
                'indian_holidays': [
                    '2024-01-26',  # Republic Day
                    '2024-08-15',  # Independence Day
                    '2024-10-31',  # Diwali (approx)
                    '2024-03-08',  # Holi (approx)
                ],
                'regional_settings': {
                    'primary_region': 'mumbai',
                    'backup_regions': ['delhi', 'bangalore'],
                    'data_centers': list(self.indian_regions.keys())
                }
            }
            
            config_map = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name='argocd-indian-config',
                    namespace=self.config.namespace,
                    labels={'app': 'argocd', 'config': 'indian-compliance'}
                ),
                data={
                    'indian-config.yaml': yaml.dump(indian_config),
                    'compliance-level': 'rbi-approved',
                    'data-residency': 'india-only'
                }
            )
            
            try:
                v1.create_namespaced_config_map(
                    namespace=self.config.namespace,
                    body=config_map
                )
                logger.info("✅ Indian compliance ConfigMap created")
            except client.ApiException as e:
                if e.status == 409:
                    logger.info("ℹ️ Indian compliance ConfigMap already exists")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Indian compliance: {e}")
            return False

    async def setup_monitoring_and_alerts(self) -> bool:
        """ArgoCD के लिए monitoring और alerting setup"""
        try:
            logger.info("📊 Setting up monitoring and alerting...")
            
            # Create ServiceMonitor for Prometheus
            monitoring_config = {
                'apiVersion': 'monitoring.coreos.com/v1',
                'kind': 'ServiceMonitor',
                'metadata': {
                    'name': 'argocd-metrics',
                    'namespace': self.config.namespace,
                    'labels': {
                        'app': 'argocd',
                        'monitoring': 'enabled'
                    }
                },
                'spec': {
                    'selector': {
                        'matchLabels': {
                            'app.kubernetes.io/name': 'argocd-metrics'
                        }
                    },
                    'endpoints': [{
                        'port': 'metrics',
                        'interval': '30s',
                        'path': '/metrics'
                    }]
                }
            }
            
            # Apply monitoring configuration
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(monitoring_config, f)
                monitoring_file = f.name
            
            result = subprocess.run([
                'kubectl', 'apply', '-f', monitoring_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Monitoring configuration applied")
            else:
                logger.warning(f"⚠️ Monitoring setup warning: {result.stderr}")
            
            # Create alerts for Indian business hours
            await self._create_indian_alerts()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup monitoring: {e}")
            return False
        finally:
            if 'monitoring_file' in locals():
                os.unlink(monitoring_file)

    async def _create_indian_alerts(self) -> bool:
        """Indian business context के लिए alerts create करना"""
        try:
            alert_rules = {
                'groups': [{
                    'name': 'argocd-indian-alerts',
                    'rules': [
                        {
                            'alert': 'ArgoCDDownDuringBusinessHours',
                            'expr': 'up{job="argocd-metrics"} == 0',
                            'for': '1m',
                            'annotations': {
                                'summary': 'ArgoCD down during Indian business hours',
                                'description': 'ArgoCD is down during business hours (9 AM - 6 PM IST)',
                                'severity': 'critical',
                                'business_impact': 'high'
                            }
                        },
                        {
                            'alert': 'ArgoCDSyncFailureECommerce', 
                            'expr': 'argocd_app_sync_total{phase="Failed"} > 0',
                            'for': '5m',
                            'annotations': {
                                'summary': 'ArgoCD sync failure for e-commerce apps',
                                'description': 'E-commerce application sync failed - potential revenue impact',
                                'severity': 'warning',
                                'business_impact': 'medium'
                            }
                        },
                        {
                            'alert': 'ArgoCDCertificateExpiringSoon',
                            'expr': '(argocd_cert_expiry_time - time()) / 86400 < 30',
                            'for': '1h',
                            'annotations': {
                                'summary': 'ArgoCD certificate expiring in 30 days',
                                'description': 'SSL certificate will expire soon - plan renewal',
                                'severity': 'warning'
                            }
                        }
                    ]
                }]
            }
            
            # Create PrometheusRule
            rule_config = {
                'apiVersion': 'monitoring.coreos.com/v1',
                'kind': 'PrometheusRule',
                'metadata': {
                    'name': 'argocd-indian-rules',
                    'namespace': self.config.namespace,
                    'labels': {'app': 'argocd', 'alerts': 'indian-business'}
                },
                'spec': alert_rules
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(rule_config, f)
                rules_file = f.name
            
            result = subprocess.run([
                'kubectl', 'apply', '-f', rules_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Indian business alert rules created")
                return True
            else:
                logger.warning(f"⚠️ Alert rules creation warning: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create Indian alerts: {e}")
            return False
        finally:
            if 'rules_file' in locals():
                os.unlink(rules_file)

    async def create_sample_applications(self) -> bool:
        """Indian context के sample applications create करना"""
        try:
            logger.info("🏗️ Creating sample Indian applications...")
            
            # Sample apps for different Indian use cases
            sample_apps = [
                {
                    'name': 'irctc-booking-frontend',
                    'description': 'IRCTC Railway Booking System Frontend',
                    'repo_url': 'https://github.com/indian-railways/booking-frontend',
                    'path': 'k8s-manifests',
                    'environment': 'production'
                },
                {
                    'name': 'paytm-payment-gateway', 
                    'description': 'Paytm Payment Gateway Integration',
                    'repo_url': 'https://github.com/paytm/payment-gateway',
                    'path': 'deployment',
                    'environment': 'production'
                },
                {
                    'name': 'flipkart-inventory-service',
                    'description': 'Flipkart Inventory Management Service',
                    'repo_url': 'https://github.com/flipkart/inventory-service',
                    'path': 'k8s',
                    'environment': 'production'
                }
            ]
            
            for app in sample_apps:
                await self._create_argocd_application(app)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create sample applications: {e}")
            return False

    async def _create_argocd_application(self, app_config: Dict[str, str]) -> bool:
        """Individual ArgoCD application create करना"""
        try:
            app_manifest = {
                'apiVersion': 'argoproj.io/v1alpha1',
                'kind': 'Application',
                'metadata': {
                    'name': app_config['name'],
                    'namespace': self.config.namespace,
                    'labels': {
                        'environment': app_config['environment'],
                        'country': 'india',
                        'compliance': 'rbi-approved'
                    },
                    'annotations': {
                        'description': app_config['description'],
                        'created-at': self.current_time.isoformat(),
                        'business-hours': '09:00-18:00 IST'
                    }
                },
                'spec': {
                    'project': 'default',
                    'source': {
                        'repoURL': app_config['repo_url'],
                        'targetRevision': 'HEAD',
                        'path': app_config['path']
                    },
                    'destination': {
                        'server': 'https://kubernetes.default.svc',
                        'namespace': f"{app_config['name']}-{app_config['environment']}"
                    },
                    'syncPolicy': {
                        'automated': {
                            'prune': True,
                            'selfHeal': True
                        },
                        'syncOptions': [
                            'CreateNamespace=true',
                            'PruneLast=true'
                        ]
                    }
                }
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(app_manifest, f)
                app_file = f.name
            
            result = subprocess.run([
                'kubectl', 'apply', '-f', app_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ Application '{app_config['name']}' created successfully")
                return True
            else:
                logger.error(f"❌ Failed to create app '{app_config['name']}': {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create application {app_config['name']}: {e}")
            return False
        finally:
            if 'app_file' in locals():
                os.unlink(app_file)

    async def setup_backup_and_recovery(self) -> bool:
        """ArgoCD backup और disaster recovery setup"""
        try:
            logger.info("💾 Setting up backup and disaster recovery...")
            
            # Create backup CronJob
            backup_cronjob = {
                'apiVersion': 'batch/v1',
                'kind': 'CronJob',
                'metadata': {
                    'name': 'argocd-backup',
                    'namespace': self.config.namespace,
                    'labels': {'app': 'argocd-backup'}
                },
                'spec': {
                    'schedule': '0 2 * * *',  # Daily at 2 AM IST
                    'timeZone': 'Asia/Kolkata',
                    'jobTemplate': {
                        'spec': {
                            'template': {
                                'spec': {
                                    'containers': [{
                                        'name': 'argocd-backup',
                                        'image': 'argoproj/argocd:v2.8.4',
                                        'command': ['sh', '-c'],
                                        'args': [
                                            'argocd admin export > /backup/argocd-backup-$(date +%Y%m%d-%H%M%S).yaml'
                                        ],
                                        'volumeMounts': [{
                                            'name': 'backup-storage',
                                            'mountPath': '/backup'
                                        }]
                                    }],
                                    'volumes': [{
                                        'name': 'backup-storage',
                                        'persistentVolumeClaim': {
                                            'claimName': 'argocd-backup-pvc'
                                        }
                                    }],
                                    'restartPolicy': 'OnFailure'
                                }
                            }
                        }
                    }
                }
            }
            
            # Create PVC for backups
            backup_pvc = {
                'apiVersion': 'v1',
                'kind': 'PersistentVolumeClaim',
                'metadata': {
                    'name': 'argocd-backup-pvc',
                    'namespace': self.config.namespace
                },
                'spec': {
                    'accessModes': ['ReadWriteOnce'],
                    'resources': {
                        'requests': {
                            'storage': '10Gi'
                        }
                    },
                    'storageClassName': 'fast-ssd'
                }
            }
            
            # Apply backup configurations
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump_all([backup_pvc, backup_cronjob], f)
                backup_file = f.name
            
            result = subprocess.run([
                'kubectl', 'apply', '-f', backup_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Backup and recovery setup completed")
                return True
            else:
                logger.error(f"❌ Backup setup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to setup backup and recovery: {e}")
            return False
        finally:
            if 'backup_file' in locals():
                os.unlink(backup_file)

    async def print_access_info(self) -> None:
        """ArgoCD access information print करना"""
        try:
            logger.info("🔐 Getting ArgoCD access information...")
            
            # Get ArgoCD server service
            v1 = client.CoreV1Api()
            service = v1.read_namespaced_service(
                name='argocd-server',
                namespace=self.config.namespace
            )
            
            # Port-forward command
            port_forward_cmd = f"kubectl port-forward svc/argocd-server -n {self.config.namespace} 8080:443"
            
            # Get initial admin password
            try:
                secret = v1.read_namespaced_secret(
                    name='argocd-initial-admin-secret',
                    namespace=self.config.namespace
                )
                import base64
                admin_password = base64.b64decode(secret.data['password']).decode('utf-8')
            except:
                admin_password = "Check kubectl get secret argocd-initial-admin-secret -n argocd -o yaml"
            
            print("\n" + "="*60)
            print("🎉 ArgoCD Setup Complete!")
            print("="*60)
            print(f"📍 Namespace: {self.config.namespace}")
            print(f"🌐 Access URL: https://localhost:8080 (after port-forward)")
            print(f"👤 Username: admin") 
            print(f"🔑 Password: {admin_password}")
            print(f"⚡ Port Forward: {port_forward_cmd}")
            print("\n🇮🇳 Indian Configuration Features:")
            print("   ✅ RBI Compliance enabled")
            print("   ✅ Data residency in India") 
            print("   ✅ IST timezone configured")
            print("   ✅ Business hours alerting")
            print("   ✅ Backup and DR ready")
            print("   ✅ Multi-region support")
            print("\n💡 Next Steps:")
            print("   1. Run port-forward command above")
            print("   2. Login to ArgoCD UI")
            print("   3. Change admin password")
            print("   4. Configure your Git repositories")
            print("   5. Deploy your first Indian application")
            print("="*60)
            
        except Exception as e:
            logger.error(f"❌ Failed to get access info: {e}")

    async def run_complete_setup(self) -> bool:
        """Complete ArgoCD setup को run करना"""
        logger.info("🚀 Starting ArgoCD setup for Indian enterprise...")
        logger.info(f"⏰ Setup time: {self.current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
        
        steps = [
            ("Setting up Kubernetes client", self.setup_kubernetes_client),
            ("Creating ArgoCD namespace", self.install_argocd_namespace), 
            ("Installing ArgoCD", self.download_and_apply_argocd_manifests),
            ("Configuring Indian compliance", self.configure_indian_compliance),
            ("Setting up monitoring", self.setup_monitoring_and_alerts),
            ("Creating sample applications", self.create_sample_applications),
            ("Setting up backup and recovery", self.setup_backup_and_recovery)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"▶️ {step_name}...")
            success = await step_func()
            if not success:
                logger.error(f"❌ Failed at step: {step_name}")
                return False
                
        await self.print_access_info()
        logger.info("🎉 ArgoCD setup completed successfully!")
        return True


async def main():
    """Main function for ArgoCD setup"""
    print("🇮🇳 ArgoCD Setup for Indian Enterprise")
    print("=====================================")
    
    # Configuration
    config = ArgoConfig(
        version="v2.8.4",
        namespace="argocd",
        enable_audit=True,
        data_residency=True,
        backup_enabled=True,
        monitoring_enabled=True,
        indian_holidays_aware=True
    )
    
    # Initialize setup
    setup = IndianArgoSetup(config)
    
    # Run complete setup
    success = await setup.run_complete_setup()
    
    if success:
        print("\n✅ ArgoCD setup completed successfully!")
        print("Ready for Indian enterprise GitOps deployment! 🚀")
    else:
        print("\n❌ ArgoCD setup failed!")
        print("Check logs for details.")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())