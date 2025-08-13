#!/usr/bin/env python3
"""
ArgoCD GitOps Setup Script
IRCTC Railway Booking System के लिए ArgoCD configuration

यह script ArgoCD को setup करती है Indian railway booking system के लिए
Author: Railway Engineering Team
"""

import subprocess
import yaml
import json
import time
import logging
from typing import Dict, List, Optional
import requests
from pathlib import Path

# लॉगिंग सेटअप
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('argocd-setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IRCTCArgoCDSetup:
    """IRCTC के लिए ArgoCD setup और management class"""
    
    def __init__(self, cluster_config: Dict[str, str]):
        self.cluster_config = cluster_config
        self.argocd_namespace = "argocd"
        self.applications = []
        
        # Indian railway specific configuration
        self.railway_config = {
            "regions": ["mumbai", "delhi", "chennai", "kolkata"],
            "environments": ["development", "staging", "production"],
            "services": [
                "booking-service",
                "payment-gateway", 
                "user-management",
                "train-schedule",
                "seat-availability"
            ]
        }
    
    def install_argocd(self) -> bool:
        """
        ArgoCD को Kubernetes cluster में install करता है
        Returns: True if successful, False otherwise
        """
        try:
            logger.info("🚂 ArgoCD install कर रहे हैं IRCTC cluster में...")
            
            # ArgoCD namespace बनाते हैं
            subprocess.run([
                "kubectl", "create", "namespace", self.argocd_namespace
            ], check=False)
            
            # ArgoCD install करते हैं
            subprocess.run([
                "kubectl", "apply", "-n", self.argocd_namespace,
                "-f", "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
            ], check=True)
            
            # Wait for ArgoCD to be ready
            logger.info("⏳ ArgoCD pods का ready होने का wait कर रहे हैं...")
            subprocess.run([
                "kubectl", "wait", "--for=condition=available", "--timeout=300s",
                "deployment/argocd-server", "-n", self.argocd_namespace
            ], check=True)
            
            logger.info("✅ ArgoCD successfully install हो गया!")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ArgoCD install में error: {e}")
            return False
    
    def configure_argocd_for_railway(self) -> bool:
        """
        ArgoCD को Indian railway system के लिए configure करता है
        """
        try:
            logger.info("🔧 ArgoCD को railway system के लिए configure कर रहे हैं...")
            
            # Railway specific ConfigMap
            railway_config = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": "argocd-railway-config",
                    "namespace": self.argocd_namespace,
                    "labels": {
                        "app.kubernetes.io/name": "argocd-railway-config",
                        "app.kubernetes.io/part-of": "argocd"
                    }
                },
                "data": {
                    "railway.regions": ",".join(self.railway_config["regions"]),
                    "railway.services": ",".join(self.railway_config["services"]),
                    "railway.peak.hours": "06:00-10:00,17:00-21:00",
                    "railway.max.concurrent.bookings": "100000",
                    "railway.timeout.seconds": "30"
                }
            }
            
            # ConfigMap को apply करते हैं
            with open("/tmp/railway-config.yaml", "w") as f:
                yaml.dump(railway_config, f)
            
            subprocess.run([
                "kubectl", "apply", "-f", "/tmp/railway-config.yaml"
            ], check=True)
            
            # ArgoCD server को railway config के साथ restart करते हैं
            self._restart_argocd_server()
            
            logger.info("✅ Railway configuration applied successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Railway configuration में error: {e}")
            return False
    
    def create_railway_applications(self) -> bool:
        """
        Railway services के लिए ArgoCD applications बनाता है
        """
        try:
            logger.info("📱 Railway applications create कर रहे हैं...")
            
            for service in self.railway_config["services"]:
                for env in self.railway_config["environments"]:
                    app_config = self._generate_application_config(service, env)
                    
                    # Application file save करते हैं
                    app_file = f"/tmp/{service}-{env}-app.yaml"
                    with open(app_file, "w") as f:
                        yaml.dump(app_config, f)
                    
                    # Application को apply करते हैं
                    subprocess.run([
                        "kubectl", "apply", "-f", app_file
                    ], check=True)
                    
                    self.applications.append(f"{service}-{env}")
                    logger.info(f"✅ Application created: {service}-{env}")
            
            logger.info(f"🎉 Total {len(self.applications)} applications created!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Applications create करने में error: {e}")
            return False
    
    def _generate_application_config(self, service: str, environment: str) -> Dict:
        """
        Individual service के लिए ArgoCD application config generate करता है
        """
        return {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": f"irctc-{service}-{environment}",
                "namespace": self.argocd_namespace,
                "labels": {
                    "app.kubernetes.io/name": f"irctc-{service}",
                    "environment": environment,
                    "service": service,
                    "team": "railway-engineering"
                }
            },
            "spec": {
                "source": {
                    "repoURL": f"https://github.com/irctc/{service}-gitops",
                    "targetRevision": "main",
                    "path": f"manifests/{environment}",
                    "helm": {
                        "valueFiles": [f"values-{environment}.yaml"]
                    }
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": f"irctc-{service}-{environment}"
                },
                "project": "irctc-production",
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": True
                    },
                    "syncOptions": [
                        "CreateNamespace=true"
                    ]
                }
            }
        }
    
    def _restart_argocd_server(self):
        """ArgoCD server को restart करता है"""
        subprocess.run([
            "kubectl", "rollout", "restart", "deployment/argocd-server",
            "-n", self.argocd_namespace
        ], check=True)
        
        # Wait for rollout to complete
        subprocess.run([
            "kubectl", "rollout", "status", "deployment/argocd-server",
            "-n", self.argocd_namespace
        ], check=True)
    
    def get_argocd_password(self) -> Optional[str]:
        """
        ArgoCD admin password retrieve करता है
        """
        try:
            result = subprocess.run([
                "kubectl", "-n", self.argocd_namespace,
                "get", "secret", "argocd-initial-admin-secret",
                "-o", "jsonpath={.data.password}"
            ], capture_output=True, text=True, check=True)
            
            # Base64 decode करते हैं
            import base64
            password = base64.b64decode(result.stdout).decode('utf-8')
            return password
            
        except subprocess.CalledProcessError:
            logger.error("❌ ArgoCD password retrieve नहीं कर सके")
            return None
    
    def setup_port_forward(self) -> subprocess.Popen:
        """
        ArgoCD UI के लिए port forward setup करता है
        """
        logger.info("🌐 ArgoCD UI के लिए port forward setup कर रहे हैं...")
        
        process = subprocess.Popen([
            "kubectl", "port-forward", "svc/argocd-server",
            "-n", self.argocd_namespace, "8080:443"
        ])
        
        logger.info("✅ ArgoCD UI available at: https://localhost:8080")
        return process
    
    def verify_setup(self) -> bool:
        """
        ArgoCD setup को verify करता है
        """
        try:
            logger.info("🔍 ArgoCD setup verify कर रहे हैं...")
            
            # Check if ArgoCD server is running
            result = subprocess.run([
                "kubectl", "get", "pods", "-n", self.argocd_namespace,
                "-l", "app.kubernetes.io/name=argocd-server",
                "-o", "json"
            ], capture_output=True, text=True, check=True)
            
            pods = json.loads(result.stdout)
            running_pods = [
                pod for pod in pods["items"]
                if pod["status"]["phase"] == "Running"
            ]
            
            if not running_pods:
                logger.error("❌ ArgoCD server pods running नहीं हैं")
                return False
            
            # Check applications
            result = subprocess.run([
                "kubectl", "get", "applications", "-n", self.argocd_namespace,
                "-o", "json"
            ], capture_output=True, text=True, check=True)
            
            apps = json.loads(result.stdout)
            logger.info(f"✅ Total applications found: {len(apps['items'])}")
            
            for app in apps["items"]:
                app_name = app["metadata"]["name"]
                status = app.get("status", {}).get("health", {}).get("status", "Unknown")
                logger.info(f"  📱 {app_name}: {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup verification में error: {e}")
            return False

def main():
    """Main function - IRCTC ArgoCD setup चलाता है"""
    logger.info("🚀 IRCTC ArgoCD GitOps Setup शुरू कर रहे हैं...")
    
    # Cluster configuration
    cluster_config = {
        "name": "irctc-mumbai-cluster",
        "region": "mumbai",
        "environment": "production"
    }
    
    # Setup instance बनाते हैं
    setup = IRCTCArgoCDSetup(cluster_config)
    
    try:
        # Step 1: Install ArgoCD
        if not setup.install_argocd():
            logger.error("❌ ArgoCD installation failed")
            return 1
        
        # Step 2: Configure for railway
        if not setup.configure_argocd_for_railway():
            logger.error("❌ Railway configuration failed")
            return 1
        
        # Step 3: Create applications
        if not setup.create_railway_applications():
            logger.error("❌ Application creation failed")
            return 1
        
        # Step 4: Get admin password
        password = setup.get_argocd_password()
        if password:
            logger.info(f"🔑 ArgoCD Admin Password: {password}")
        
        # Step 5: Setup port forward (optional)
        print("\n" + "="*50)
        print("🎉 IRCTC ArgoCD Setup Complete!")
        print("="*50)
        print(f"🌐 ArgoCD UI: https://localhost:8080")
        print(f"👤 Username: admin")
        print(f"🔑 Password: {password}")
        print("="*50)
        
        # Option to start port forward
        choice = input("\nPort forward शुरू करें? (y/n): ")
        if choice.lower() == 'y':
            port_forward_process = setup.setup_port_forward()
            
            try:
                print("\n🌐 Port forward चल रहा है... Ctrl+C से stop करें")
                port_forward_process.wait()
            except KeyboardInterrupt:
                print("\n👋 Port forward stop कर रहे हैं...")
                port_forward_process.terminate()
        
        # Step 6: Verify setup
        if setup.verify_setup():
            logger.info("✅ Setup verification successful!")
            return 0
        else:
            logger.error("❌ Setup verification failed!")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Setup में critical error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())