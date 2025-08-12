#!/usr/bin/env python3
"""
Kubernetes Secrets Management for Production
Indian Cloud Infrastructure - TCS, Infosys, Wipro deployment patterns

यह system production Kubernetes environments के लिए comprehensive secrets management।
HashiCorp Vault, Sealed Secrets, और External Secrets Operator integration।

Real-world Context:
- Indian IT services manage 10,000+ K8s clusters globally
- Average enterprise has 500+ secrets per cluster
- 85% of security breaches involve exposed credentials
- K8s secrets are base64 encoded, not encrypted by default
"""

import os
import json
import base64
import yaml
import time
import hvac
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from kubernetes import client, config
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests

# Setup logging for secrets management audit
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('secrets_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecretDefinition:
    """Secret definition with metadata"""
    name: str
    namespace: str
    secret_type: str  # generic, tls, docker-registry, etc.
    data: Dict[str, str]
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.annotations is None:
            self.annotations = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class VaultSecret:
    """Vault secret structure"""
    path: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None
    version: int = 1
    created_time: datetime = None
    
class KubernetesSecretsManager:
    """
    Production Kubernetes Secrets Management
    
    Features:
    - Native K8s secrets management
    - HashiCorp Vault integration
    - Sealed Secrets support
    - External Secrets Operator
    - Secret rotation
    - Audit logging
    - Encryption at rest
    """
    
    def __init__(self, kubeconfig_path: str = None):
        # Initialize Kubernetes client
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                # Try in-cluster config first, then local config
                try:
                    config.load_incluster_config()
                    logger.info("Using in-cluster Kubernetes config")
                except:
                    config.load_kube_config()
                    logger.info("Using local Kubernetes config")
        except Exception as e:
            logger.warning(f"Kubernetes config not available: {e}")
            # Create mock client for demo
            self.k8s_v1 = None
        else:
            self.k8s_v1 = client.CoreV1Api()
        
        # Initialize encryption
        self.fernet = self._initialize_encryption()
        
        # Vault configuration
        self.vault_client = None
        self._setup_vault_client()
        
        # Secret templates for Indian cloud providers
        self.secret_templates = self._load_secret_templates()
        
        # Audit trail
        self.audit_logs: List[Dict] = []
        
        logger.info("Kubernetes Secrets Manager initialized")
    
    def _initialize_encryption(self) -> Fernet:
        """Initialize encryption for local secret storage"""
        master_key = os.getenv('SECRETS_MASTER_KEY', 'indian_cloud_secrets_2024')
        
        salt = b'tcs_infosys_wipro_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return Fernet(key)
    
    def _setup_vault_client(self):
        """Setup HashiCorp Vault client"""
        vault_url = os.getenv('VAULT_URL', 'http://localhost:8200')
        vault_token = os.getenv('VAULT_TOKEN', 'development-token')
        
        try:
            self.vault_client = hvac.Client(url=vault_url, token=vault_token)
            if self.vault_client.is_authenticated():
                logger.info("HashiCorp Vault client authenticated")
            else:
                logger.warning("Vault authentication failed")
                self.vault_client = None
        except Exception as e:
            logger.warning(f"Vault client setup failed: {e}")
            self.vault_client = None
    
    def _load_secret_templates(self) -> Dict:
        """Load secret templates for common services"""
        return {
            'database': {
                'postgresql': {
                    'host': 'postgres.tcs-cloud.com',
                    'port': '5432',
                    'database': 'production',
                    'username': '',
                    'password': ''
                },
                'mysql': {
                    'host': 'mysql.infosys-cloud.com',
                    'port': '3306',
                    'database': 'production',
                    'username': '',
                    'password': ''
                },
                'mongodb': {
                    'uri': 'mongodb://mongodb.wipro-cloud.com:27017/production',
                    'username': '',
                    'password': ''
                }
            },
            'api': {
                'razorpay': {
                    'key_id': '',
                    'key_secret': '',
                    'webhook_secret': ''
                },
                'aws': {
                    'access_key_id': '',
                    'secret_access_key': '',
                    'region': 'ap-south-1'  # Mumbai region
                },
                'gcp': {
                    'type': 'service_account',
                    'project_id': '',
                    'client_email': '',
                    'private_key': ''
                }
            },
            'tls': {
                'certificate': '',
                'private_key': '',
                'ca_certificate': ''
            }
        }
    
    def create_secret(
        self, 
        secret_def: SecretDefinition,
        encrypt_locally: bool = True
    ) -> bool:
        """
        Create Kubernetes secret
        
        Args:
            secret_def: Secret definition
            encrypt_locally: Whether to encrypt locally before storing
            
        Returns:
            Success status
        """
        try:
            # Encrypt sensitive data if requested
            if encrypt_locally:
                encrypted_data = {}
                for key, value in secret_def.data.items():
                    encrypted_value = self.fernet.encrypt(value.encode())
                    encrypted_data[key] = base64.b64encode(encrypted_value).decode()
                secret_def.data = encrypted_data
            else:
                # Base64 encode for K8s (standard approach)
                encoded_data = {}
                for key, value in secret_def.data.items():
                    encoded_data[key] = base64.b64encode(value.encode()).decode()
                secret_def.data = encoded_data
            
            # Create K8s secret object
            secret = client.V1Secret(
                api_version="v1",
                kind="Secret",
                metadata=client.V1ObjectMeta(
                    name=secret_def.name,
                    namespace=secret_def.namespace,
                    labels=secret_def.labels,
                    annotations=secret_def.annotations
                ),
                type=secret_def.secret_type,
                data=secret_def.data
            )
            
            # Create in cluster (or simulate)
            if self.k8s_v1:
                self.k8s_v1.create_namespaced_secret(
                    namespace=secret_def.namespace,
                    body=secret
                )
                logger.info(f"Secret created: {secret_def.name} in {secret_def.namespace}")
            else:
                logger.info(f"[DEMO] Secret would be created: {secret_def.name}")
            
            # Audit log
            self._log_audit_event("SECRET_CREATED", {
                'name': secret_def.name,
                'namespace': secret_def.namespace,
                'type': secret_def.secret_type,
                'keys': list(secret_def.data.keys()),
                'encrypted': encrypt_locally
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Secret creation failed: {e}")
            return False
    
    def get_secret(
        self, 
        name: str, 
        namespace: str,
        decrypt_locally: bool = True
    ) -> Optional[Dict[str, str]]:
        """
        Get secret from Kubernetes
        
        Args:
            name: Secret name
            namespace: Namespace
            decrypt_locally: Whether to decrypt locally encrypted data
            
        Returns:
            Decrypted secret data
        """
        try:
            if self.k8s_v1:
                secret = self.k8s_v1.read_namespaced_secret(name=name, namespace=namespace)
                secret_data = secret.data or {}
            else:
                # Demo data
                secret_data = {
                    'username': base64.b64encode(b'demo_user').decode(),
                    'password': base64.b64encode(b'demo_pass').decode()
                }
            
            # Decode and potentially decrypt
            decoded_data = {}
            for key, value in secret_data.items():
                decoded_value = base64.b64decode(value.encode())
                
                if decrypt_locally:
                    try:
                        # Try to decrypt (if it was encrypted locally)
                        decrypted_value = self.fernet.decrypt(decoded_value)
                        decoded_data[key] = decrypted_value.decode()
                    except:
                        # If decryption fails, it's probably standard base64
                        decoded_data[key] = decoded_value.decode()
                else:
                    decoded_data[key] = decoded_value.decode()
            
            # Audit log
            self._log_audit_event("SECRET_ACCESSED", {
                'name': name,
                'namespace': namespace,
                'keys': list(decoded_data.keys())
            })
            
            return decoded_data
            
        except Exception as e:
            logger.error(f"Secret retrieval failed: {e}")
            return None
    
    def update_secret(
        self, 
        name: str, 
        namespace: str, 
        new_data: Dict[str, str]
    ) -> bool:
        """Update existing secret"""
        try:
            # Get current secret
            if self.k8s_v1:
                current_secret = self.k8s_v1.read_namespaced_secret(name=name, namespace=namespace)
                
                # Update data
                encoded_data = {}
                for key, value in new_data.items():
                    encoded_data[key] = base64.b64encode(value.encode()).decode()
                
                current_secret.data = encoded_data
                
                # Apply update
                self.k8s_v1.replace_namespaced_secret(
                    name=name,
                    namespace=namespace,
                    body=current_secret
                )
                
                logger.info(f"Secret updated: {name}")
            else:
                logger.info(f"[DEMO] Secret would be updated: {name}")
            
            # Audit log
            self._log_audit_event("SECRET_UPDATED", {
                'name': name,
                'namespace': namespace,
                'updated_keys': list(new_data.keys())
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Secret update failed: {e}")
            return False
    
    def delete_secret(self, name: str, namespace: str) -> bool:
        """Delete secret"""
        try:
            if self.k8s_v1:
                self.k8s_v1.delete_namespaced_secret(name=name, namespace=namespace)
                logger.info(f"Secret deleted: {name}")
            else:
                logger.info(f"[DEMO] Secret would be deleted: {name}")
            
            # Audit log
            self._log_audit_event("SECRET_DELETED", {
                'name': name,
                'namespace': namespace
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Secret deletion failed: {e}")
            return False
    
    def sync_from_vault(self, vault_path: str, k8s_secret_name: str, namespace: str) -> bool:
        """Sync secret from HashiCorp Vault to Kubernetes"""
        try:
            if not self.vault_client:
                raise Exception("Vault client not available")
            
            # Read from Vault
            vault_response = self.vault_client.secrets.kv.v2.read_secret_version(
                path=vault_path
            )
            vault_data = vault_response['data']['data']
            
            # Create K8s secret
            secret_def = SecretDefinition(
                name=k8s_secret_name,
                namespace=namespace,
                secret_type="Opaque",
                data=vault_data,
                annotations={
                    'vault.hashicorp.com/vault-path': vault_path,
                    'secrets.tcs.com/synced-from-vault': 'true'
                }
            )
            
            success = self.create_secret(secret_def, encrypt_locally=False)
            
            if success:
                logger.info(f"Secret synced from Vault: {vault_path} → {k8s_secret_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Vault sync failed: {e}")
            return False
    
    def create_vault_secret(self, path: str, data: Dict[str, Any]) -> bool:
        """Create secret in HashiCorp Vault"""
        try:
            if not self.vault_client:
                logger.warning("Vault client not available - simulating")
                logger.info(f"[DEMO] Vault secret would be created at: {path}")
                return True
            
            # Store in Vault
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data
            )
            
            # Audit log
            self._log_audit_event("VAULT_SECRET_CREATED", {
                'path': path,
                'keys': list(data.keys())
            })
            
            logger.info(f"Vault secret created: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Vault secret creation failed: {e}")
            return False
    
    def rotate_secret(
        self, 
        name: str, 
        namespace: str,
        rotation_strategy: str = "immediate"
    ) -> bool:
        """
        Rotate secret with different strategies
        
        Strategies:
        - immediate: Replace immediately
        - staged: Keep old version for graceful transition
        - scheduled: Schedule for specific time
        """
        try:
            # Get current secret
            current_data = self.get_secret(name, namespace)
            if not current_data:
                return False
            
            # Generate new values based on secret type
            new_data = self._generate_rotated_values(current_data)
            
            if rotation_strategy == "staged":
                # Create new secret with version suffix
                versioned_name = f"{name}-v{int(time.time())}"
                
                versioned_secret = SecretDefinition(
                    name=versioned_name,
                    namespace=namespace,
                    secret_type="Opaque",
                    data=new_data,
                    labels={
                        'secrets.tcs.com/original-secret': name,
                        'secrets.tcs.com/rotation-version': str(int(time.time()))
                    }
                )
                
                self.create_secret(versioned_secret)
                
                # Update original secret after delay (simulate)
                logger.info(f"Staged rotation: {versioned_name} created, original will update later")
                
            else:  # immediate
                self.update_secret(name, namespace, new_data)
            
            # Audit log
            self._log_audit_event("SECRET_ROTATED", {
                'name': name,
                'namespace': namespace,
                'strategy': rotation_strategy
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Secret rotation failed: {e}")
            return False
    
    def _generate_rotated_values(self, current_data: Dict[str, str]) -> Dict[str, str]:
        """Generate new values for secret rotation"""
        import secrets
        import string
        
        new_data = {}
        
        for key, current_value in current_data.items():
            if key.lower() in ['password', 'secret', 'key']:
                # Generate new password/secret
                new_data[key] = ''.join(
                    secrets.choice(string.ascii_letters + string.digits) 
                    for _ in range(32)
                )
            elif key.lower() in ['token', 'api_key']:
                # Generate new token
                new_data[key] = secrets.token_urlsafe(32)
            else:
                # Keep existing value for non-sensitive fields
                new_data[key] = current_value
        
        return new_data
    
    def create_sealed_secret(self, secret_def: SecretDefinition) -> str:
        """
        Create Sealed Secret YAML
        SealedSecrets encrypt secrets that can be stored in Git
        """
        try:
            # This would normally use kubeseal CLI or bitnami-labs/sealed-secrets
            sealed_secret_yaml = f"""
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: {secret_def.name}
  namespace: {secret_def.namespace}
spec:
  encryptedData:"""
            
            # Simulate encryption (in production, use actual sealed-secrets controller)
            for key, value in secret_def.data.items():
                encrypted_value = base64.b64encode(
                    self.fernet.encrypt(value.encode())
                ).decode()
                sealed_secret_yaml += f"\n    {key}: {encrypted_value}"
            
            sealed_secret_yaml += f"""
  template:
    metadata:
      name: {secret_def.name}
      namespace: {secret_def.namespace}
    type: {secret_def.secret_type}
"""
            
            logger.info(f"Sealed secret YAML generated for: {secret_def.name}")
            return sealed_secret_yaml
            
        except Exception as e:
            logger.error(f"Sealed secret creation failed: {e}")
            return ""
    
    def create_external_secret(
        self, 
        name: str, 
        namespace: str,
        vault_path: str,
        keys: List[str]
    ) -> str:
        """
        Create External Secret YAML for External Secrets Operator
        Syncs secrets from external systems (Vault, AWS Secrets Manager, etc.)
        """
        try:
            external_secret_yaml = f"""
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {name}
  namespace: {namespace}
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: {name}
    creationPolicy: Owner
  data:"""
            
            for key in keys:
                external_secret_yaml += f"""
  - secretKey: {key}
    remoteRef:
      key: {vault_path}
      property: {key}"""
            
            external_secret_yaml += f"""
---
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: {namespace}
spec:
  provider:
    vault:
      server: "http://vault.tcs-cloud.com:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets"
          serviceAccountRef:
            name: external-secrets
"""
            
            logger.info(f"External secret YAML generated for: {name}")
            return external_secret_yaml
            
        except Exception as e:
            logger.error(f"External secret creation failed: {e}")
            return ""
    
    def scan_secrets_security(self, namespace: str = None) -> Dict:
        """Scan secrets for security issues"""
        try:
            security_report = {
                'total_secrets': 0,
                'issues': [],
                'recommendations': [],
                'compliant_secrets': 0
            }
            
            # Get all secrets (or simulate)
            if self.k8s_v1:
                if namespace:
                    secrets = self.k8s_v1.list_namespaced_secret(namespace=namespace)
                else:
                    secrets = self.k8s_v1.list_secret_for_all_namespaces()
                secret_list = secrets.items
            else:
                # Demo data
                secret_list = [
                    type('MockSecret', (), {
                        'metadata': type('MockMeta', (), {
                            'name': 'database-secret',
                            'namespace': 'production',
                            'annotations': {}
                        })(),
                        'data': {'password': base64.b64encode(b'weak123').decode()}
                    })(),
                    type('MockSecret', (), {
                        'metadata': type('MockMeta', (), {
                            'name': 'api-keys',
                            'namespace': 'production', 
                            'annotations': {'secrets.tcs.com/encrypted': 'true'}
                        })(),
                        'data': {'api_key': base64.b64encode(b'strong_key_here').decode()}
                    })()
                ]
            
            security_report['total_secrets'] = len(secret_list)
            
            for secret in secret_list:
                secret_name = secret.metadata.name
                secret_namespace = secret.metadata.namespace
                
                # Check for security issues
                issues = []
                
                # Check if secret is encrypted beyond base64
                annotations = getattr(secret.metadata, 'annotations', {}) or {}
                if not annotations.get('secrets.tcs.com/encrypted'):
                    issues.append("Not encrypted beyond base64")
                
                # Check for weak passwords (if we can decode)
                if secret.data:
                    for key, value in secret.data.items():
                        if key.lower() in ['password', 'secret']:
                            try:
                                decoded = base64.b64decode(value.encode()).decode()
                                if len(decoded) < 12:
                                    issues.append(f"Weak {key}: less than 12 characters")
                            except:
                                pass
                
                # Check for proper labels
                labels = getattr(secret.metadata, 'labels', {}) or {}
                if not labels.get('app'):
                    issues.append("Missing app label for tracking")
                
                if issues:
                    security_report['issues'].append({
                        'secret': f"{secret_namespace}/{secret_name}",
                        'issues': issues
                    })
                else:
                    security_report['compliant_secrets'] += 1
            
            # Generate recommendations
            security_report['recommendations'] = [
                "Use External Secrets Operator for centralized secret management",
                "Implement secret rotation policies",
                "Enable encryption at rest in etcd",
                "Use Sealed Secrets for GitOps workflows",
                "Implement proper RBAC for secret access",
                "Regular security scanning of secrets"
            ]
            
            return security_report
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return {'error': str(e)}
    
    def _log_audit_event(self, event_type: str, details: Dict):
        """Log audit event"""
        audit_entry = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.audit_logs.append(audit_entry)
        
        # Keep last 1000 entries
        if len(self.audit_logs) > 1000:
            self.audit_logs = self.audit_logs[-500:]
    
    def get_audit_trail(self, hours: int = 24) -> List[Dict]:
        """Get audit trail for specified time period"""
        since = datetime.now() - timedelta(hours=hours)
        
        return [
            log for log in self.audit_logs 
            if datetime.fromisoformat(log['timestamp']) >= since
        ]

def demonstrate_kubernetes_secrets():
    """
    Demonstrate Kubernetes secrets management for Indian cloud infrastructure
    TCS, Infosys, Wipro production deployment patterns
    """
    print("\n🔐 Kubernetes Secrets Management - Indian Cloud Infrastructure")
    print("=" * 65)
    
    # Initialize secrets manager
    secrets_mgr = KubernetesSecretsManager()
    
    # Scenario 1: Database secrets for TCS deployment
    print("\n🗄️  Scenario 1: TCS Database Secrets")
    print("-" * 35)
    
    tcs_db_secret = SecretDefinition(
        name="postgresql-credentials",
        namespace="tcs-production",
        secret_type="Opaque",
        data={
            'host': 'postgres.tcs-cloud.com',
            'port': '5432',
            'database': 'customer_portal',
            'username': 'tcs_app_user',
            'password': 'SecureP@ssw0rd2024!',
            'connection_string': 'postgresql://tcs_app_user:SecureP@ssw0rd2024!@postgres.tcs-cloud.com:5432/customer_portal'
        },
        labels={
            'app': 'customer-portal',
            'tier': 'database',
            'managed-by': 'tcs-platform'
        },
        annotations={
            'secrets.tcs.com/rotation-schedule': '90d',
            'secrets.tcs.com/encrypted': 'true'
        }
    )
    
    success = secrets_mgr.create_secret(tcs_db_secret, encrypt_locally=True)
    print(f"✅ TCS Database secret created: {success}")
    
    # Scenario 2: API keys for Infosys microservices
    print("\n🔑 Scenario 2: Infosys API Keys")
    print("-" * 30)
    
    infosys_api_secret = SecretDefinition(
        name="payment-gateway-keys",
        namespace="infosys-fintech",
        secret_type="Opaque",
        data={
            'razorpay_key_id': 'rzp_live_IxIGODxBToCpcc',
            'razorpay_key_secret': 'ali_dbDuLXsdmHUbUVvJBhWxySo',
            'paytm_merchant_id': 'INFOSYS123456789',
            'paytm_merchant_key': 'kbzk1DSbJiV_O3p5',
            'upi_psp_key': 'INFOSYS@YBL'
        },
        labels={
            'app': 'payment-service',
            'component': 'gateway',
            'managed-by': 'infosys-platform'
        }
    )
    
    success = secrets_mgr.create_secret(infosys_api_secret)
    print(f"✅ Infosys API keys created: {success}")
    
    # Scenario 3: TLS certificates for Wipro
    print("\n🔒 Scenario 3: Wipro TLS Certificates")
    print("-" * 35)
    
    wipro_tls_secret = SecretDefinition(
        name="wipro-tls-cert",
        namespace="wipro-services",
        secret_type="kubernetes.io/tls",
        data={
            'tls.crt': """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAMy6QJgY1qGHMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAlVTMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhXaXBybyBDbG91
ZCBTZXJ2aWNlcyBJbmMwHhcNMjQwMTAxMDAwMDAwWhcNMjUwMTAxMDAwMDAwWjBF
... (truncated for demo)
-----END CERTIFICATE-----""",
            'tls.key': """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC5/9HZK8mY3Xla
... (truncated for demo)
-----END PRIVATE KEY-----"""
        },
        labels={
            'app': 'web-frontend',
            'cert-manager.io/cluster-issuer': 'wipro-ca'
        }
    )
    
    success = secrets_mgr.create_secret(wipro_tls_secret, encrypt_locally=False)
    print(f"✅ Wipro TLS certificate created: {success}")
    
    # Vault integration demo
    print("\n🏦 HashiCorp Vault Integration")
    print("-" * 35)
    
    # Store secret in Vault
    vault_data = {
        'mongodb_uri': 'mongodb://cluster.tcs-cloud.com:27017',
        'mongodb_username': 'tcs_mongodb_user',
        'mongodb_password': 'MongoSecure2024!',
        'replica_set': 'tcs-production-rs'
    }
    
    vault_success = secrets_mgr.create_vault_secret('tcs/database/mongodb', vault_data)
    print(f"✅ Vault secret stored: {vault_success}")
    
    # Sync from Vault to K8s
    sync_success = secrets_mgr.sync_from_vault(
        vault_path='tcs/database/mongodb',
        k8s_secret_name='mongodb-credentials',
        namespace='tcs-production'
    )
    print(f"✅ Vault → K8s sync: {sync_success}")
    
    # Secret retrieval demo
    print("\n📖 Secret Retrieval Demo")
    print("-" * 25)
    
    retrieved_secret = secrets_mgr.get_secret('postgresql-credentials', 'tcs-production')
    if retrieved_secret:
        print(f"✅ Retrieved TCS database secret")
        print(f"   Host: {retrieved_secret.get('host', 'N/A')}")
        print(f"   Database: {retrieved_secret.get('database', 'N/A')}")
        print(f"   Username: {retrieved_secret.get('username', 'N/A')}")
        print(f"   Password: {retrieved_secret.get('password', 'N/A')[:8]}...")
    
    # Secret rotation demo
    print("\n🔄 Secret Rotation Demo")
    print("-" * 25)
    
    rotation_success = secrets_mgr.rotate_secret(
        'payment-gateway-keys', 
        'infosys-fintech',
        rotation_strategy='immediate'
    )
    print(f"✅ Infosys API keys rotated: {rotation_success}")
    
    # Sealed Secrets demo
    print("\n📦 Sealed Secrets (GitOps)")
    print("-" * 25)
    
    sealed_yaml = secrets_mgr.create_sealed_secret(tcs_db_secret)
    print("✅ Sealed Secret YAML generated:")
    print(sealed_yaml[:200] + "...")
    
    # External Secrets demo
    print("\n🔗 External Secrets Operator")
    print("-" * 30)
    
    external_yaml = secrets_mgr.create_external_secret(
        name='vault-synced-secret',
        namespace='tcs-production',
        vault_path='tcs/api/external',
        keys=['api_key', 'secret_key', 'webhook_url']
    )
    print("✅ External Secret YAML generated")
    print(f"   Length: {len(external_yaml)} characters")
    
    # Security scan demo
    print("\n🔍 Security Scan Results")
    print("-" * 25)
    
    security_report = secrets_mgr.scan_secrets_security('production')
    print(f"📊 Total secrets scanned: {security_report['total_secrets']}")
    print(f"✅ Compliant secrets: {security_report['compliant_secrets']}")
    print(f"⚠️  Issues found: {len(security_report['issues'])}")
    
    if security_report['issues']:
        print("\n🚨 Security Issues:")
        for issue in security_report['issues'][:3]:  # Show first 3
            print(f"   • {issue['secret']}: {', '.join(issue['issues'])}")
    
    print("\n💡 Security Recommendations:")
    for i, rec in enumerate(security_report['recommendations'][:3], 1):
        print(f"   {i}. {rec}")
    
    # Audit trail
    print("\n📋 Recent Audit Trail")
    print("-" * 22)
    
    audit_logs = secrets_mgr.get_audit_trail(hours=1)
    for i, log in enumerate(audit_logs[-5:], 1):  # Last 5 events
        print(f"   {i}. {log['event_type']} at {log['timestamp'][:19]}")
        if 'name' in log['details']:
            print(f"      Secret: {log['details']['name']}")

def demonstrate_production_patterns():
    """Show production deployment patterns"""
    print("\n" + "="*60)
    print("🏭 PRODUCTION DEPLOYMENT PATTERNS")
    print("="*60)
    
    print("""
# 1. GitOps with Sealed Secrets

apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: database-credentials
  namespace: production
spec:
  encryptedData:
    username: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEQAx...
    password: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEQAx...
  template:
    metadata:
      name: database-credentials
      namespace: production

# 2. External Secrets with Vault

apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: vault-secret
  namespace: production
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: app-secret
    creationPolicy: Owner
  data:
  - secretKey: api-key
    remoteRef:
      key: myapp/config
      property: api_key

# 3. Secret Rotation with CronJob

apiVersion: batch/v1
kind: CronJob
metadata:
  name: secret-rotation
spec:
  schedule: "0 2 * * 0"  # Weekly at 2 AM Sunday
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: rotator
            image: tcs/secret-rotator:v1.0
            command:
            - /bin/sh
            - -c
            - |
              # Rotate database password
              NEW_PASSWORD=$(openssl rand -base64 32)
              kubectl patch secret postgresql-credentials \\
                -p='{"data":{"password":"'$(echo -n $NEW_PASSWORD | base64)'"}}'
              
              # Update database user password
              PGPASSWORD=$OLD_PASSWORD psql -h $DB_HOST -U $DB_USER \\
                -c "ALTER USER $DB_USER PASSWORD '$NEW_PASSWORD';"
          restartPolicy: OnFailure

# 4. Secrets Operator Custom Controller

import kopf
import kubernetes
import logging

@kopf.on.create('v1', 'secrets')
def secret_created(spec, name, namespace, **kwargs):
    logging.info(f"Secret created: {namespace}/{name}")
    
    # Add security labels
    api = kubernetes.client.CoreV1Api()
    secret = api.read_namespaced_secret(name=name, namespace=namespace)
    
    if not secret.metadata.labels:
        secret.metadata.labels = {}
    
    secret.metadata.labels['secrets.tcs.com/managed'] = 'true'
    secret.metadata.labels['secrets.tcs.com/created'] = str(int(time.time()))
    
    api.replace_namespaced_secret(name=name, namespace=namespace, body=secret)

# 5. Multi-Cluster Secret Sync

apiVersion: v1
kind: ConfigMap
metadata:
  name: secret-sync-config
data:
  clusters.yaml: |
    clusters:
      - name: mumbai-cluster
        endpoint: https://k8s-mumbai.tcs.com
        secrets:
          - source: production/api-keys
            target: production/api-keys
      - name: bangalore-cluster  
        endpoint: https://k8s-bangalore.tcs.com
        secrets:
          - source: production/database-creds
            target: production/database-creds

# 6. Secret Scanning with Falco

apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-rules
data:
  secrets_rules.yaml: |
    - rule: Secret Access Outside Business Hours
      desc: Detect secret access outside business hours
      condition: >
        k8s_audit and
        ka.verb in (get, list) and
        ka.target.resource=secrets and
        not (ka.user.name contains "system:") and
        (ka.request_timestamp.hour < 6 or ka.request_timestamp.hour > 22)
      output: >
        Suspicious secret access outside business hours
        (user=%ka.user.name verb=%ka.verb resource=%ka.target.resource
        secret=%ka.target.name time=%ka.request_timestamp)
      priority: WARNING

# 7. Helm Chart with Secret Management

apiVersion: v2
name: tcs-microservice
description: TCS Microservice with Secret Management
version: 1.0.0

templates/secret.yaml:
{{- if .Values.secrets.external }}
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {{ include "app.fullname" . }}-secret
spec:
  secretStoreRef:
    name: {{ .Values.secrets.store }}
    kind: SecretStore
  target:
    name: {{ include "app.fullname" . }}-secret
  data:
  {{- range .Values.secrets.data }}
  - secretKey: {{ .key }}
    remoteRef:
      key: {{ .path }}
      property: {{ .property }}
  {{- end }}
{{- else }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "app.fullname" . }}-secret
data:
  {{- range $key, $value := .Values.secrets.data }}
  {{ $key }}: {{ $value | b64enc | quote }}
  {{- end }}
{{- end }}
    """)

if __name__ == "__main__":
    demonstrate_kubernetes_secrets()
    demonstrate_production_patterns()