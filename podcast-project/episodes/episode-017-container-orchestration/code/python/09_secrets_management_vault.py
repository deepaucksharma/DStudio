#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secrets Management with HashiCorp Vault for Container Orchestration
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे CRED जैसी fintech companies
production में container secrets को securely manage करती हैं।

Real-world scenario: CRED का secure secrets management for containers
"""

import hvac
import os
import json
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from loguru import logger
import requests
import yaml
from cryptography.fernet import Fernet
import hashlib

class SecretType(Enum):
    """Secret type enumeration"""
    DATABASE = "database"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    OAUTH_TOKEN = "oauth_token"
    ENCRYPTION_KEY = "encryption_key"
    PAYMENT_CONFIG = "payment_config"

class Environment(Enum):
    """Environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class SecretConfig:
    """Secret configuration structure"""
    secret_name: str
    secret_type: SecretType
    environment: Environment
    path: str
    ttl: int  # Time to live in seconds
    renewable: bool
    metadata: Dict[str, str]
    access_policy: str

@dataclass
class SecretRotationConfig:
    """Secret rotation configuration"""
    secret_name: str
    rotation_interval: int  # Days
    notification_before: int  # Days before expiry
    auto_rotation: bool
    rotation_script: str

class CREDSecretsManager:
    """
    CRED-style Secrets Manager for Container Orchestration
    Production-ready Vault integration with Indian fintech requirements
    """
    
    def __init__(self, vault_url: str, vault_token: Optional[str] = None):
        self.vault_url = vault_url
        
        # Initialize Vault client
        self.vault_client = hvac.Client(url=vault_url, token=vault_token)
        
        # Verify Vault connection
        if not self.vault_client.is_authenticated():
            logger.error("Failed to authenticate with Vault")
            raise Exception("Vault authentication failed")
        
        # Indian fintech specific secret categories
        self.fintech_secret_categories = {
            "payment_gateways": [
                "razorpay_keys", "paytm_keys", "phonepe_keys", 
                "upi_keys", "neft_config", "rtgs_config"
            ],
            "banking_apis": [
                "icici_api", "hdfc_api", "sbi_api", "axis_api",
                "yes_bank_api", "kotak_api"
            ],
            "regulatory": [
                "rbi_certificates", "sebi_keys", "irdai_config",
                "npci_certificates", "cbdt_keys"
            ],
            "kyc_services": [
                "aadhaar_api", "pan_verification", "voter_id_api",
                "passport_api", "driving_license_api"
            ],
            "credit_bureaus": [
                "cibil_api", "experian_api", "equifax_api", 
                "highmark_api"
            ]
        }
        
        # Environment-specific configurations
        self.environment_configs = {
            Environment.DEVELOPMENT: {
                "ttl": 86400,  # 1 day
                "max_ttl": 604800,  # 7 days
                "rotation_enabled": False,
                "audit_enabled": True
            },
            Environment.STAGING: {
                "ttl": 43200,  # 12 hours
                "max_ttl": 259200,  # 3 days
                "rotation_enabled": True,
                "audit_enabled": True
            },
            Environment.PRODUCTION: {
                "ttl": 3600,  # 1 hour
                "max_ttl": 86400,  # 1 day
                "rotation_enabled": True,
                "audit_enabled": True
            }
        }
        
        # Vault secret engines for different purposes
        self.secret_engines = {
            "database": "database/",
            "pki": "pki/",
            "kv": "secret/",
            "transit": "transit/"
        }
        
        logger.info("💳 CRED Secrets Manager initialized!")
        logger.info(f"Connected to Vault at {vault_url}")
    
    def setup_vault_policies(self):
        """
        Setup Vault policies for different service roles
        """
        
        # CRED application policy
        cred_app_policy = '''
# CRED Application Policy
path "secret/data/cred/{{identity.entity.aliases.auth_kubernetes_xxxxx.metadata.service_account_namespace}}/*" {
  capabilities = ["read"]
}

path "database/creds/cred-readonly" {
  capabilities = ["read"]
}

path "pki/issue/cred-internal" {
  capabilities = ["create", "update"]
}

path "transit/encrypt/cred-data" {
  capabilities = ["create", "update"]
}

path "transit/decrypt/cred-data" {
  capabilities = ["create", "update"]
}
'''
        
        # CRED admin policy
        cred_admin_policy = '''
# CRED Admin Policy
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "database/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "pki/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "transit/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
'''
        
        # Production read-only policy
        cred_readonly_policy = '''
# CRED Read-Only Policy
path "secret/data/cred/production/*" {
  capabilities = ["read"]
}

path "database/creds/cred-readonly" {
  capabilities = ["read"]
}
'''
        
        policies = {
            "cred-app": cred_app_policy,
            "cred-admin": cred_admin_policy,
            "cred-readonly": cred_readonly_policy
        }
        
        for policy_name, policy_content in policies.items():
            try:
                self.vault_client.sys.create_or_update_policy(
                    name=policy_name,
                    policy=policy_content
                )
                logger.info(f"✅ Policy created: {policy_name}")
            except Exception as e:
                logger.error(f"Failed to create policy {policy_name}: {str(e)}")
    
    def setup_secret_engines(self):
        """
        Setup and configure Vault secret engines
        """
        
        # Enable KV v2 secret engine
        try:
            self.vault_client.sys.enable_secrets_engine(
                backend_type='kv',
                path='secret',
                options={'version': '2'}
            )
            logger.info("✅ KV v2 secret engine enabled")
        except Exception as e:
            logger.warning(f"KV engine already exists or error: {str(e)}")
        
        # Enable database secret engine
        try:
            self.vault_client.sys.enable_secrets_engine(
                backend_type='database',
                path='database'
            )
            logger.info("✅ Database secret engine enabled")
        except Exception as e:
            logger.warning(f"Database engine already exists or error: {str(e)}")
        
        # Enable PKI secret engine
        try:
            self.vault_client.sys.enable_secrets_engine(
                backend_type='pki',
                path='pki'
            )
            logger.info("✅ PKI secret engine enabled")
        except Exception as e:
            logger.warning(f"PKI engine already exists or error: {str(e)}")
        
        # Enable Transit secret engine
        try:
            self.vault_client.sys.enable_secrets_engine(
                backend_type='transit',
                path='transit'
            )
            logger.info("✅ Transit secret engine enabled")
        except Exception as e:
            logger.warning(f"Transit engine already exists or error: {str(e)}")
    
    def configure_kubernetes_auth(self, kubernetes_host: str, ca_cert: str, jwt_token: str):
        """
        Configure Kubernetes authentication for container access
        """
        
        try:
            # Enable Kubernetes auth method
            self.vault_client.sys.enable_auth_method('kubernetes')
            
            # Configure Kubernetes auth
            self.vault_client.auth.kubernetes.configure(
                kubernetes_host=kubernetes_host,
                kubernetes_ca_cert=ca_cert,
                token_reviewer_jwt=jwt_token
            )
            
            # Create role for CRED applications
            self.vault_client.auth.kubernetes.create_role(
                name='cred-app',
                bound_service_account_names=['cred-service-account'],
                bound_service_account_namespaces=['cred-prod', 'cred-staging', 'cred-dev'],
                token_policies=['cred-app'],
                token_ttl=3600,  # 1 hour
                token_max_ttl=86400  # 1 day
            )
            
            logger.info("✅ Kubernetes authentication configured")
            
        except Exception as e:
            logger.error(f"Failed to configure Kubernetes auth: {str(e)}")
    
    def store_fintech_secrets(self, environment: Environment):
        """
        Store fintech-specific secrets for CRED
        """
        
        env_name = environment.value
        
        # Payment gateway secrets
        payment_secrets = {
            "razorpay": {
                "key_id": f"rzp_{'live' if env_name == 'production' else 'test'}_xxxxxxxx",
                "key_secret": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "webhook_secret": "xxxxxxxxxxxxxxxxxxxxxxxx"
            },
            "paytm": {
                "merchant_id": f"CRED{'PROD' if env_name == 'production' else 'TEST'}",
                "merchant_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "website": f"CRED{'PROD' if env_name == 'production' else 'TEST'}WEB",
                "industry_type": "Retail"
            },
            "upi": {
                "vpa": f"cred@{'icici' if env_name == 'production' else 'test'}",
                "merchant_code": "1234567890123456",
                "terminal_id": "TERM001"
            }
        }
        
        # Banking API secrets
        banking_secrets = {
            "icici_bank": {
                "api_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "client_id": "CRED_ICICI_CLIENT",
                "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "base_url": f"https://{'api' if env_name == 'production' else 'sandbox'}.icicibank.com"
            },
            "hdfc_bank": {
                "api_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "customer_id": "CRED123456",
                "base_url": f"https://{'api' if env_name == 'production' else 'uat'}.hdfcbank.com"
            }
        }
        
        # Regulatory secrets
        regulatory_secrets = {
            "rbi": {
                "license_number": "NBFC-P2P-2023-001",
                "reporting_endpoint": "https://cosmos.rbi.org.in",
                "digital_signature_cert": "-----BEGIN CERTIFICATE-----\\n...",
                "private_key": "-----BEGIN PRIVATE KEY-----\\n..."
            },
            "npci": {
                "member_id": "CRED001",
                "api_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "certificate": "-----BEGIN CERTIFICATE-----\\n..."
            }
        }
        
        # KYC service secrets
        kyc_secrets = {
            "aadhaar_api": {
                "license_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "agency_id": "CRED_KYC",
                "base_url": f"https://{'prod' if env_name == 'production' else 'stage'}.uidai.gov.in"
            },
            "pan_verification": {
                "api_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "user_id": "CRED_PAN_USER",
                "base_url": "https://api.nsdl.com"
            }
        }
        
        # Credit bureau secrets
        credit_secrets = {
            "cibil": {
                "member_code": "CRED001",
                "user_id": "CREDUSER",
                "password": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "enquiry_purpose": "05",  # Credit card
                "base_url": f"https://{'connect' if env_name == 'production' else 'sandbox'}.cibilonline.com"
            },
            "experian": {
                "client_id": "CRED_EXPERIAN",
                "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "subscriber_id": "12345678",
                "base_url": f"https://{'api' if env_name == 'production' else 'sandbox'}.experian.in"
            }
        }
        
        # Database secrets
        database_secrets = {
            "postgres_primary": {
                "host": f"cred-db-{'prod' if env_name == 'production' else env_name}.cluster.amazonaws.com",
                "port": "5432",
                "database": "cred_main",
                "username": "cred_app",
                "password": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "ssl_mode": "require"
            },
            "redis_cache": {
                "host": f"cred-redis-{'prod' if env_name == 'production' else env_name}.cluster.amazonaws.com",
                "port": "6379",
                "password": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "ssl": "true"
            }
        }
        
        # Store all secrets
        secret_groups = {
            "payment_gateways": payment_secrets,
            "banking_apis": banking_secrets,
            "regulatory": regulatory_secrets,
            "kyc_services": kyc_secrets,
            "credit_bureaus": credit_secrets,
            "databases": database_secrets
        }
        
        for group_name, secrets in secret_groups.items():
            for secret_name, secret_data in secrets.items():
                path = f"secret/data/cred/{env_name}/{group_name}/{secret_name}"
                
                try:
                    self.vault_client.secrets.kv.v2.create_or_update_secret(
                        path=path,
                        secret=secret_data,
                        metadata={
                            "environment": env_name,
                            "service": "cred",
                            "category": group_name,
                            "created_by": "cred-secrets-manager",
                            "created_at": datetime.now().isoformat(),
                            "compliance": "RBI,SEBI,PCI_DSS"
                        }
                    )
                    
                    logger.info(f"✅ Stored secret: {group_name}/{secret_name} for {env_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to store secret {path}: {str(e)}")
    
    def retrieve_secret(self, secret_path: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve secret from Vault with audit logging
        """
        
        try:
            response = self.vault_client.secrets.kv.v2.read_secret_version(
                path=secret_path,
                version=version
            )
            
            secret_data = response['data']['data']
            metadata = response['data']['metadata']
            
            # Log secret access for audit
            self.log_secret_access(secret_path, "READ", True)
            
            logger.info(f"✅ Retrieved secret: {secret_path}")
            return {
                "data": secret_data,
                "metadata": metadata
            }
            
        except Exception as e:
            self.log_secret_access(secret_path, "READ", False, str(e))
            logger.error(f"Failed to retrieve secret {secret_path}: {str(e)}")
            return None
    
    def rotate_secret(self, secret_path: str, new_secret_data: Dict[str, Any]) -> bool:
        """
        Rotate secret with backup of old version
        """
        
        try:
            # Get current secret for backup
            current_secret = self.retrieve_secret(secret_path)
            
            if current_secret:
                # Update secret with new data
                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path=secret_path,
                    secret=new_secret_data,
                    metadata={
                        "rotated_at": datetime.now().isoformat(),
                        "rotated_by": "cred-secrets-manager",
                        "rotation_reason": "scheduled_rotation"
                    }
                )
                
                self.log_secret_access(secret_path, "ROTATE", True)
                logger.info(f"✅ Rotated secret: {secret_path}")
                return True
            else:
                logger.error(f"Cannot rotate secret, current version not found: {secret_path}")
                return False
                
        except Exception as e:
            self.log_secret_access(secret_path, "ROTATE", False, str(e))
            logger.error(f"Failed to rotate secret {secret_path}: {str(e)}")
            return False
    
    def generate_kubernetes_secret_manifest(self, secret_name: str, secret_data: Dict[str, str], 
                                          namespace: str) -> str:
        """
        Generate Kubernetes secret manifest from Vault data
        """
        
        # Encode secret data in base64
        encoded_data = {}
        for key, value in secret_data.items():
            encoded_data[key] = base64.b64encode(value.encode()).decode()
        
        secret_manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": secret_name,
                "namespace": namespace,
                "labels": {
                    "app": "cred",
                    "managed-by": "vault-secrets-operator"
                },
                "annotations": {
                    "vault.security.banzaicloud.io/vault-addr": self.vault_url,
                    "vault.security.banzaicloud.io/vault-path": f"secret/data/cred/{namespace}/{secret_name}",
                    "vault.security.banzaicloud.io/vault-role": "cred-app"
                }
            },
            "type": "Opaque",
            "data": encoded_data
        }
        
        return yaml.dump(secret_manifest, default_flow_style=False)
    
    def setup_secret_injection_webhook(self) -> str:
        """
        Generate Vault secret injection webhook configuration
        """
        
        webhook_config = '''
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingAdmissionWebhook
metadata:
  name: vault-secrets-webhook
  labels:
    app: vault-secrets-webhook
spec:
  clientConfig:
    service:
      name: vault-secrets-webhook
      namespace: vault-system
      path: /mutate
  rules:
  - operations: [CREATE, UPDATE]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  admissionReviewVersions: ["v1", "v1beta1"]
  sideEffects: None
  failurePolicy: Fail
'''
        
        return webhook_config
    
    def log_secret_access(self, secret_path: str, operation: str, success: bool, error: Optional[str] = None):
        """
        Log secret access for audit compliance
        """
        
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "secret_path": secret_path,
            "operation": operation,
            "success": success,
            "error": error,
            "service": "cred-secrets-manager",
            "compliance": "RBI_AUDIT_LOG"
        }
        
        # In production, this would go to a secure audit logging system
        logger.info(f"AUDIT: {json.dumps(audit_log)}")
    
    def get_secret_health_status(self) -> Dict[str, Any]:
        """
        Get health status of secret management system
        """
        
        try:
            # Check Vault health
            vault_health = self.vault_client.sys.read_health_status()
            
            # Count secrets by environment
            secret_counts = {}
            for env in Environment:
                try:
                    secrets = self.vault_client.secrets.kv.v2.list_secrets(
                        path=f"secret/metadata/cred/{env.value}"
                    )
                    secret_counts[env.value] = len(secrets['data']['keys'])
                except Exception:
                    secret_counts[env.value] = 0
            
            return {
                "vault_status": "healthy" if vault_health['initialized'] else "unhealthy",
                "vault_sealed": vault_health.get('sealed', True),
                "secret_counts": secret_counts,
                "last_check": datetime.now().isoformat(),
                "compliance_status": "RBI_COMPLIANT"
            }
            
        except Exception as e:
            return {
                "vault_status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

def main():
    """Demonstration of CRED secrets management"""
    
    print("💳 CRED Secrets Management Demo")
    print("Production-ready Vault integration for Indian fintech")
    print("=" * 60)
    
    # Initialize secrets manager (using dev Vault instance)
    try:
        secrets_manager = CREDSecretsManager(
            vault_url="http://localhost:8200",
            vault_token="dev-only-token"  # In production, use proper auth
        )
        
        print("🔧 Setting up Vault configuration...")
        
        # Setup Vault policies and engines
        secrets_manager.setup_vault_policies()
        secrets_manager.setup_secret_engines()
        
        print("💾 Storing fintech secrets...")
        
        # Store secrets for all environments
        for environment in Environment:
            print(f"   Storing secrets for {environment.value}...")
            secrets_manager.store_fintech_secrets(environment)
        
        print("\\n🔍 Testing secret retrieval...")
        
        # Test secret retrieval
        test_secret = secrets_manager.retrieve_secret("secret/data/cred/production/payment_gateways/razorpay")
        if test_secret:
            print("   ✅ Secret retrieval successful")
            print(f"   Metadata: {test_secret['metadata']}")
        
        print("\\n📊 Secrets health status:")
        health_status = secrets_manager.get_secret_health_status()
        for key, value in health_status.items():
            print(f"   {key}: {value}")
        
        print("\\n📋 Kubernetes Integration:")
        
        # Generate Kubernetes secret manifest
        k8s_manifest = secrets_manager.generate_kubernetes_secret_manifest(
            secret_name="cred-razorpay-keys",
            secret_data={
                "key_id": "rzp_live_xxxxxxxx",
                "key_secret": "xxxxxxxxxxxxxxxxxxxxxxxx"
            },
            namespace="cred-prod"
        )
        
        print("Generated Kubernetes secret manifest:")
        print(k8s_manifest)
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("Note: This demo requires a running Vault instance at localhost:8200")
    
    print("\\n✅ CRED secrets management demonstration completed!")

if __name__ == "__main__":
    main()

# Production Deployment Instructions:
"""
# 1. Deploy Vault in production:
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault --set='server.ha.enabled=true'

# 2. Initialize and unseal Vault:
kubectl exec vault-0 -- vault operator init
kubectl exec vault-0 -- vault operator unseal <key1>
kubectl exec vault-0 -- vault operator unseal <key2>
kubectl exec vault-0 -- vault operator unseal <key3>

# 3. Configure authentication:
kubectl exec vault-0 -- vault auth enable kubernetes
kubectl exec vault-0 -- vault write auth/kubernetes/config \\
    token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \\
    kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443" \\
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# 4. Deploy Vault Secrets Operator:
helm repo add banzaicloud-stable https://kubernetes-charts.banzaicloud.com
helm install vault-secrets-operator banzaicloud-stable/vault-secrets-operator

# 5. Create CRED service account:
kubectl create serviceaccount cred-service-account -n cred-prod
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cred-vault-auth
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: cred-service-account
  namespace: cred-prod
EOF

# 6. Use in container deployments:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cred-app
spec:
  template:
    metadata:
      annotations:
        vault.security.banzaicloud.io/vault-addr: "https://vault.cred.com"
        vault.security.banzaicloud.io/vault-role: "cred-app"
        vault.security.banzaicloud.io/vault-path: "secret/data/cred/production"
    spec:
      serviceAccountName: cred-service-account
      containers:
      - name: cred-app
        image: cred/app:latest
        env:
        - name: RAZORPAY_KEY
          value: "vault:secret/data/cred/production/payment_gateways/razorpay#key_id"
        - name: RAZORPAY_SECRET
          value: "vault:secret/data/cred/production/payment_gateways/razorpay#key_secret"
"""