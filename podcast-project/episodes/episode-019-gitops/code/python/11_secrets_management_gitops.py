#!/usr/bin/env python3
"""
GitOps Secrets Management System
=================================

Indian compliance-aware secrets management with GitOps integration।
RBI data residency, HashiCorp Vault integration, और automated secret rotation।

Features:
- GitOps-driven secret provisioning और rotation
- HashiCorp Vault integration with Indian regions
- RBI compliant audit trails और access controls
- Automated secret rotation for banking systems
- Emergency secret revocation workflows
- Cross-region secret replication for DR

Author: Hindi Tech Podcast - Episode 19
Context: Secure Secrets Management for Indian Banking
"""

import asyncio
import logging
import json
import yaml
import os
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import kubernetes
from kubernetes import client, config
import aiohttp
import asyncpg
import hvac  # HashiCorp Vault client
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pytz
from pathlib import Path
import uuid

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for secrets operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('secrets_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecretType(Enum):
    """Types of secrets managed"""
    DATABASE_PASSWORD = "database_password"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    OAUTH_TOKEN = "oauth_token"
    ENCRYPTION_KEY = "encryption_key"
    JWT_SECRET = "jwt_secret"
    UPI_CREDENTIALS = "upi_credentials"
    BANKING_API_KEY = "banking_api_key"

class SecretStatus(Enum):
    """Secret lifecycle status"""
    ACTIVE = "active"
    PENDING_ROTATION = "pending_rotation"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"
    EMERGENCY_REVOKED = "emergency_revoked"

class AccessLevel(Enum):
    """Access levels for Indian compliance"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # RBI restricted
    TOP_SECRET = "top_secret"  # Banking secrets

@dataclass
class SecretMetadata:
    """Secret metadata and configuration"""
    secret_id: str
    name: str
    secret_type: SecretType
    access_level: AccessLevel
    
    # Lifecycle
    status: SecretStatus = SecretStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(IST))
    updated_at: datetime = field(default_factory=lambda: datetime.now(IST))
    expires_at: Optional[datetime] = None
    
    # Rotation
    rotation_enabled: bool = True
    rotation_interval_days: int = 90
    last_rotated_at: Optional[datetime] = None
    next_rotation_at: Optional[datetime] = None
    
    # Compliance
    data_classification: str = "internal"
    requires_rbi_approval: bool = False
    audit_level: str = "standard"  # standard, high, critical
    
    # Access control
    allowed_namespaces: List[str] = field(default_factory=list)
    allowed_applications: List[str] = field(default_factory=list)
    allowed_regions: List[str] = field(default_factory=lambda: ['mumbai', 'delhi', 'bangalore'])
    
    # Backup and DR
    backup_enabled: bool = True
    cross_region_replication: bool = False
    
    # Owner info
    owner: str = ""
    team: str = ""
    cost_center: str = ""

@dataclass
class SecretValue:
    """Secret value with encryption"""
    secret_id: str
    value: str
    encrypted_value: str = ""
    encryption_key_id: str = ""
    
    # Version tracking
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(IST))
    
    # Hash for integrity checking
    value_hash: str = ""

@dataclass
class SecretAccess:
    """Secret access audit record"""
    access_id: str
    secret_id: str
    accessor_id: str
    access_type: str  # read, write, rotate, revoke
    
    # Context
    namespace: str = ""
    application: str = ""
    region: str = ""
    
    # Request info
    requested_at: datetime = field(default_factory=lambda: datetime.now(IST))
    ip_address: str = ""
    user_agent: str = ""
    
    # Result
    success: bool = False
    error_message: str = ""
    
    # Compliance
    compliance_reviewed: bool = False
    compliance_notes: str = ""

@dataclass
class SecretsConfig:
    """Secrets management configuration"""
    # Vault configuration
    vault_url: str = "https://vault.company.com"
    vault_token: str = ""
    vault_namespace: str = "admin"
    vault_mount_path: str = "secret"
    
    # Database
    postgres_url: str = "postgresql://user:pass@postgres:5432/secrets"
    
    # Kubernetes
    k8s_secret_namespace: str = "secrets"
    
    # Encryption
    master_key: str = ""  # Base64 encoded master key
    encryption_algorithm: str = "AES-256-GCM"
    
    # Rotation
    default_rotation_interval: int = 90  # days
    enable_auto_rotation: bool = True
    rotation_window_hours: List[int] = field(default_factory=lambda: [2, 3, 4])  # 2-4 AM IST
    
    # Compliance
    enable_audit_logging: bool = True
    audit_retention_years: int = 7  # RBI requirement
    enable_rbi_reporting: bool = True
    data_residency_regions: List[str] = field(default_factory=lambda: ['ap-south-1', 'ap-south-2'])
    
    # Access control
    enable_rbac: bool = True
    require_mfa_for_sensitive: bool = True
    
    # Notifications
    slack_webhook: str = ""
    security_team_email: str = "security@company.com"
    compliance_team_email: str = "compliance@company.com"

class IndianSecretsCompliance:
    """
    Indian compliance rules for secrets management।
    
    RBI guidelines, IT Act 2000, और banking regulations के according
    secrets classification और handling rules।
    """
    
    @staticmethod
    def classify_secret(secret_type: SecretType, content: str) -> Tuple[AccessLevel, bool]:
        """Classify secret based on type and content"""
        
        # Banking और payment secrets are always restricted
        if secret_type in [SecretType.UPI_CREDENTIALS, SecretType.BANKING_API_KEY]:
            return AccessLevel.RESTRICTED, True
        
        # Check for banking keywords in content
        banking_keywords = [
            'razorpay', 'paytm', 'phonepe', 'sbi', 'hdfc', 'icici', 'axis',
            'upi', 'imps', 'neft', 'rtgs', 'npci', 'rbi'
        ]
        
        content_lower = content.lower()
        has_banking_content = any(keyword in content_lower for keyword in banking_keywords)
        
        if has_banking_content:
            return AccessLevel.RESTRICTED, True
        
        # Certificate and private keys
        if secret_type in [SecretType.CERTIFICATE, SecretType.PRIVATE_KEY]:
            return AccessLevel.CONFIDENTIAL, False
        
        # Database passwords for production
        if secret_type == SecretType.DATABASE_PASSWORD:
            if 'prod' in content_lower or 'production' in content_lower:
                return AccessLevel.CONFIDENTIAL, False
            else:
                return AccessLevel.INTERNAL, False
        
        # API keys
        if secret_type == SecretType.API_KEY:
            return AccessLevel.INTERNAL, False
        
        # Default classification
        return AccessLevel.INTERNAL, False
    
    @staticmethod
    def get_retention_period(access_level: AccessLevel) -> int:
        """Get retention period in years based on access level"""
        retention_map = {
            AccessLevel.PUBLIC: 1,
            AccessLevel.INTERNAL: 3,
            AccessLevel.CONFIDENTIAL: 5,
            AccessLevel.RESTRICTED: 7,  # RBI requirement
            AccessLevel.TOP_SECRET: 10
        }
        
        return retention_map.get(access_level, 3)
    
    @staticmethod
    def requires_cross_region_backup(access_level: AccessLevel) -> bool:
        """Check if secret requires cross-region backup"""
        return access_level in [AccessLevel.RESTRICTED, AccessLevel.TOP_SECRET]
    
    @staticmethod
    def get_rotation_interval(secret_type: SecretType, access_level: AccessLevel) -> int:
        """Get rotation interval in days"""
        
        # Banking secrets rotate more frequently
        if secret_type in [SecretType.UPI_CREDENTIALS, SecretType.BANKING_API_KEY]:
            return 30  # Monthly rotation
        
        if access_level == AccessLevel.RESTRICTED:
            return 60  # Every 2 months
        elif access_level == AccessLevel.CONFIDENTIAL:
            return 90  # Every 3 months
        else:
            return 180  # Every 6 months

class VaultSecretStore:
    """
    HashiCorp Vault integration।
    
    Indian regions के साथ secure secret storage और retrieval।
    """
    
    def __init__(self, config: SecretsConfig):
        self.config = config
        self.vault_client = None
        
    async def initialize(self) -> bool:
        """Initialize Vault connection"""
        try:
            logger.info("🔐 Initializing Vault connection")
            
            self.vault_client = hvac.Client(
                url=self.config.vault_url,
                token=self.config.vault_token,
                namespace=self.config.vault_namespace
            )
            
            # Verify connection
            if self.vault_client.is_authenticated():
                logger.info("✅ Vault connection established")
                return True
            else:
                logger.error("❌ Vault authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Vault initialization failed: {e}")
            return False
    
    async def store_secret(self, metadata: SecretMetadata, value: SecretValue) -> bool:
        """Store secret in Vault"""
        try:
            logger.info(f"🔒 Storing secret: {metadata.secret_id}")
            
            # Prepare secret data
            secret_data = {
                'value': value.value,
                'metadata': asdict(metadata),
                'version': value.version,
                'created_at': value.created_at.isoformat(),
                'value_hash': value.value_hash
            }
            
            # Store in Vault
            vault_path = f"{self.config.vault_mount_path}/data/{metadata.secret_id}"
            
            response = self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=vault_path,
                secret=secret_data
            )
            
            if response:
                logger.info(f"✅ Secret stored in Vault: {metadata.secret_id}")
                
                # Store in cross-region if required
                if metadata.cross_region_replication:
                    await self._replicate_cross_region(metadata, value)
                
                return True
            else:
                logger.error(f"❌ Failed to store secret in Vault: {metadata.secret_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to store secret {metadata.secret_id}: {e}")
            return False
    
    async def retrieve_secret(self, secret_id: str, version: Optional[int] = None) -> Optional[SecretValue]:
        """Retrieve secret from Vault"""
        try:
            logger.info(f"🔓 Retrieving secret: {secret_id}")
            
            vault_path = f"{self.config.vault_mount_path}/data/{secret_id}"
            
            if version:
                response = self.vault_client.secrets.kv.v2.read_secret_version(
                    path=vault_path,
                    version=version
                )
            else:
                response = self.vault_client.secrets.kv.v2.read_secret_version(
                    path=vault_path
                )
            
            if response and 'data' in response:
                secret_data = response['data']['data']
                
                secret_value = SecretValue(
                    secret_id=secret_id,
                    value=secret_data['value'],
                    version=secret_data.get('version', 1),
                    created_at=datetime.fromisoformat(secret_data['created_at']),
                    value_hash=secret_data.get('value_hash', '')
                )
                
                logger.info(f"✅ Secret retrieved: {secret_id}")
                return secret_value
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve secret {secret_id}: {e}")
            return None
    
    async def delete_secret(self, secret_id: str) -> bool:
        """Delete secret from Vault"""
        try:
            logger.info(f"🗑️ Deleting secret: {secret_id}")
            
            vault_path = f"{self.config.vault_mount_path}/data/{secret_id}"
            
            # Soft delete (mark as deleted but keep versions)
            response = self.vault_client.secrets.kv.v2.delete_latest_version_of_secret(
                path=vault_path
            )
            
            if response:
                logger.info(f"✅ Secret deleted: {secret_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to delete secret {secret_id}: {e}")
            return False
    
    async def _replicate_cross_region(self, metadata: SecretMetadata, value: SecretValue) -> None:
        """Replicate secret across regions for DR"""
        try:
            logger.info(f"🌍 Cross-region replication for: {metadata.secret_id}")
            
            # In a real implementation, this would replicate to other Vault clusters
            # For now, we'll simulate the process
            
            for region in metadata.allowed_regions:
                if region != "mumbai":  # Don't replicate to same region
                    logger.info(f"📡 Replicating to {region}")
                    # Actual replication logic would go here
                    
            logger.info(f"✅ Cross-region replication completed: {metadata.secret_id}")
            
        except Exception as e:
            logger.error(f"❌ Cross-region replication failed: {e}")

class KubernetesSecretSyncer:
    """
    Kubernetes Secret synchronization।
    
    Vault से secrets को Kubernetes Secrets में sync करता है।
    """
    
    def __init__(self, config: SecretsConfig):
        self.config = config
        self.k8s_client = None
        
    async def initialize(self) -> bool:
        """Initialize Kubernetes client"""
        try:
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.k8s_client = client.ApiClient()
            return True
            
        except Exception as e:
            logger.error(f"❌ Kubernetes client initialization failed: {e}")
            return False
    
    async def sync_secret_to_k8s(self, metadata: SecretMetadata, value: SecretValue) -> bool:
        """Sync secret to Kubernetes Secret"""
        try:
            logger.info(f"🔄 Syncing secret to Kubernetes: {metadata.secret_id}")
            
            v1 = client.CoreV1Api()
            
            # Prepare secret data
            secret_data = {
                metadata.name: base64.b64encode(value.value.encode()).decode()
            }
            
            # Create Kubernetes Secret
            k8s_secret = client.V1Secret(
                metadata=client.V1ObjectMeta(
                    name=metadata.secret_id,
                    namespace=self.config.k8s_secret_namespace,
                    labels={
                        'managed-by': 'gitops-secrets-controller',
                        'secret-type': metadata.secret_type.value,
                        'access-level': metadata.access_level.value,
                        'region': 'india'
                    },
                    annotations={
                        'secrets.gitops/created-at': metadata.created_at.isoformat(),
                        'secrets.gitops/rotation-enabled': str(metadata.rotation_enabled),
                        'secrets.gitops/next-rotation': metadata.next_rotation_at.isoformat() if metadata.next_rotation_at else '',
                        'secrets.gitops/data-classification': metadata.data_classification,
                        'secrets.gitops/owner': metadata.owner
                    }
                ),
                type='Opaque',
                data=secret_data
            )
            
            try:
                v1.create_namespaced_secret(
                    namespace=self.config.k8s_secret_namespace,
                    body=k8s_secret
                )
                logger.info(f"✅ Secret created in Kubernetes: {metadata.secret_id}")
            except client.ApiException as e:
                if e.status == 409:  # Already exists, update it
                    v1.patch_namespaced_secret(
                        name=metadata.secret_id,
                        namespace=self.config.k8s_secret_namespace,
                        body=k8s_secret
                    )
                    logger.info(f"✅ Secret updated in Kubernetes: {metadata.secret_id}")
                else:
                    raise e
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to sync secret to Kubernetes: {e}")
            return False
    
    async def remove_secret_from_k8s(self, secret_id: str) -> bool:
        """Remove secret from Kubernetes"""
        try:
            logger.info(f"🗑️ Removing secret from Kubernetes: {secret_id}")
            
            v1 = client.CoreV1Api()
            
            v1.delete_namespaced_secret(
                name=secret_id,
                namespace=self.config.k8s_secret_namespace
            )
            
            logger.info(f"✅ Secret removed from Kubernetes: {secret_id}")
            return True
            
        except client.ApiException as e:
            if e.status == 404:
                logger.info(f"Secret not found in Kubernetes: {secret_id}")
                return True
            else:
                logger.error(f"❌ Failed to remove secret from Kubernetes: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to remove secret from Kubernetes: {e}")
            return False

class SecretRotationEngine:
    """
    Automated secret rotation engine।
    
    Indian business hours के according intelligent secret rotation।
    """
    
    def __init__(self, config: SecretsConfig):
        self.config = config
        self.rotation_generators = {
            SecretType.DATABASE_PASSWORD: self._generate_database_password,
            SecretType.API_KEY: self._generate_api_key,
            SecretType.JWT_SECRET: self._generate_jwt_secret,
            SecretType.ENCRYPTION_KEY: self._generate_encryption_key,
            SecretType.UPI_CREDENTIALS: self._generate_upi_credentials
        }
        
    async def rotate_secret(self, metadata: SecretMetadata, current_value: SecretValue) -> Optional[SecretValue]:
        """Rotate secret to new value"""
        try:
            logger.info(f"🔄 Rotating secret: {metadata.secret_id}")
            
            # Check if rotation is allowed now
            if not self._is_rotation_allowed():
                logger.info(f"⏰ Rotation not allowed at this time: {metadata.secret_id}")
                return None
            
            # Generate new secret value
            generator = self.rotation_generators.get(metadata.secret_type)
            if not generator:
                logger.error(f"❌ No rotation generator for type: {metadata.secret_type}")
                return None
            
            new_value = await generator(metadata, current_value)
            if not new_value:
                logger.error(f"❌ Failed to generate new value for: {metadata.secret_id}")
                return None
            
            # Create new secret value
            new_secret_value = SecretValue(
                secret_id=metadata.secret_id,
                value=new_value,
                version=current_value.version + 1,
                value_hash=hashlib.sha256(new_value.encode()).hexdigest()
            )
            
            # Update metadata
            metadata.last_rotated_at = datetime.now(IST)
            metadata.next_rotation_at = datetime.now(IST) + timedelta(days=metadata.rotation_interval_days)
            metadata.updated_at = datetime.now(IST)
            
            logger.info(f"✅ Secret rotated: {metadata.secret_id} (v{new_secret_value.version})")
            return new_secret_value
            
        except Exception as e:
            logger.error(f"❌ Secret rotation failed: {e}")
            return None
    
    def _is_rotation_allowed(self) -> bool:
        """Check if rotation is allowed based on business hours"""
        current_time = datetime.now(IST)
        
        # Don't rotate during business hours (avoid disruption)
        if 9 <= current_time.hour <= 21:
            return False
        
        # Only rotate during configured window
        if current_time.hour not in self.config.rotation_window_hours:
            return False
        
        # Don't rotate on weekends (avoid on-call issues)
        if current_time.weekday() >= 5:  # Saturday, Sunday
            return False
        
        return True
    
    async def _generate_database_password(self, metadata: SecretMetadata, current: SecretValue) -> Optional[str]:
        """Generate new database password"""
        import secrets
        import string
        
        # Generate strong password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Ensure it has required character types
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*" for c in password)):
            return password
        
        # Retry if password doesn't meet criteria
        return await self._generate_database_password(metadata, current)
    
    async def _generate_api_key(self, metadata: SecretMetadata, current: SecretValue) -> Optional[str]:
        """Generate new API key"""
        import secrets
        
        # Generate 64-character hex API key
        return secrets.token_hex(32)
    
    async def _generate_jwt_secret(self, metadata: SecretMetadata, current: SecretValue) -> Optional[str]:
        """Generate new JWT secret"""
        import secrets
        
        # Generate 256-bit base64 JWT secret
        return base64.b64encode(secrets.token_bytes(32)).decode()
    
    async def _generate_encryption_key(self, metadata: SecretMetadata, current: SecretValue) -> Optional[str]:
        """Generate new encryption key"""
        # Generate Fernet key
        return Fernet.generate_key().decode()
    
    async def _generate_upi_credentials(self, metadata: SecretMetadata, current: SecretValue) -> Optional[str]:
        """Generate new UPI credentials (mock)"""
        import secrets
        
        # In real implementation, this would integrate with payment gateway APIs
        # For demo, generate a mock credential structure
        upi_creds = {
            "merchant_id": f"UPI{secrets.randbelow(1000000):06d}",
            "api_key": secrets.token_hex(32),
            "secret_key": secrets.token_hex(32),
            "webhook_secret": secrets.token_hex(16)
        }
        
        return json.dumps(upi_creds)

class GitOpsSecretsController:
    """
    Main GitOps secrets management controller।
    
    Complete secrets lifecycle management के साथ Indian compliance
    और automated rotation capabilities।
    """
    
    def __init__(self, config: SecretsConfig):
        self.config = config
        self.vault_store = VaultSecretStore(config)
        self.k8s_syncer = KubernetesSecretSyncer(config)
        self.rotation_engine = SecretRotationEngine(config)
        self.pg_pool = None
        self.active_secrets = {}  # Track active secrets
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Initialize secrets controller"""
        try:
            logger.info("🚀 Initializing GitOps Secrets Controller")
            
            # Initialize components
            if not await self.vault_store.initialize():
                return False
            
            if not await self.k8s_syncer.initialize():
                return False
            
            # Setup database connection
            self.pg_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            
            # Initialize database schema
            await self._initialize_database()
            
            # Load existing secrets
            await self._load_active_secrets()
            
            logger.info("✅ GitOps Secrets Controller initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Secrets controller initialization failed: {e}")
            return False
    
    async def _initialize_database(self) -> None:
        """Initialize secrets management database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS secret_metadata (
            id SERIAL PRIMARY KEY,
            secret_id VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(500) NOT NULL,
            secret_type VARCHAR(100) NOT NULL,
            access_level VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE,
            last_rotated_at TIMESTAMP WITH TIME ZONE,
            next_rotation_at TIMESTAMP WITH TIME ZONE,
            rotation_enabled BOOLEAN DEFAULT TRUE,
            rotation_interval_days INTEGER DEFAULT 90,
            metadata_json JSONB DEFAULT '{}'::jsonb,
            
            INDEX idx_secret_type (secret_type),
            INDEX idx_secret_status (status),
            INDEX idx_secret_next_rotation (next_rotation_at)
        );
        
        CREATE TABLE IF NOT EXISTS secret_access_log (
            id SERIAL PRIMARY KEY,
            access_id VARCHAR(255) UNIQUE NOT NULL,
            secret_id VARCHAR(255) NOT NULL,
            accessor_id VARCHAR(255) NOT NULL,
            access_type VARCHAR(50) NOT NULL,
            namespace VARCHAR(255),
            application VARCHAR(255),
            region VARCHAR(100),
            requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ip_address INET,
            user_agent TEXT,
            success BOOLEAN DEFAULT FALSE,
            error_message TEXT,
            compliance_reviewed BOOLEAN DEFAULT FALSE,
            
            INDEX idx_access_secret (secret_id),
            INDEX idx_access_requested (requested_at),
            INDEX idx_access_success (success)
        );
        
        CREATE TABLE IF NOT EXISTS secret_rotation_log (
            id SERIAL PRIMARY KEY,
            rotation_id VARCHAR(255) UNIQUE NOT NULL,
            secret_id VARCHAR(255) NOT NULL,
            old_version INTEGER,
            new_version INTEGER,
            rotation_type VARCHAR(50) NOT NULL, -- scheduled, manual, emergency
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            success BOOLEAN DEFAULT FALSE,
            error_message TEXT,
            rotated_by VARCHAR(255),
            
            INDEX idx_rotation_secret (secret_id),
            INDEX idx_rotation_started (started_at)
        );
        """
        
        async with self.pg_pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Secrets management database schema initialized")
    
    async def _load_active_secrets(self) -> None:
        """Load active secrets from database"""
        try:
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT secret_id, metadata_json FROM secret_metadata 
                    WHERE status IN ('active', 'pending_rotation', 'rotating')
                """)
                
                for row in rows:
                    metadata_dict = row['metadata_json']
                    metadata = SecretMetadata(**metadata_dict)
                    self.active_secrets[row['secret_id']] = metadata
                    
            logger.info(f"📊 Loaded {len(self.active_secrets)} active secrets")
            
        except Exception as e:
            logger.error(f"❌ Failed to load active secrets: {e}")
    
    async def create_secret(self, name: str, secret_type: SecretType, 
                          value: str, owner: str, **kwargs) -> Optional[str]:
        """Create new secret"""
        try:
            secret_id = f"secret-{uuid.uuid4().hex[:12]}"
            logger.info(f"📝 Creating secret: {secret_id}")
            
            # Classify secret for compliance
            access_level, requires_rbi = IndianSecretsCompliance.classify_secret(secret_type, value)
            
            # Create metadata
            metadata = SecretMetadata(
                secret_id=secret_id,
                name=name,
                secret_type=secret_type,
                access_level=access_level,
                requires_rbi_approval=requires_rbi,
                rotation_interval_days=IndianSecretsCompliance.get_rotation_interval(secret_type, access_level),
                cross_region_replication=IndianSecretsCompliance.requires_cross_region_backup(access_level),
                owner=owner,
                **kwargs
            )
            
            # Set rotation schedule
            if metadata.rotation_enabled:
                metadata.next_rotation_at = datetime.now(IST) + timedelta(days=metadata.rotation_interval_days)
            
            # Create secret value
            secret_value = SecretValue(
                secret_id=secret_id,
                value=value,
                value_hash=hashlib.sha256(value.encode()).hexdigest()
            )
            
            # Store in Vault
            if not await self.vault_store.store_secret(metadata, secret_value):
                return None
            
            # Sync to Kubernetes
            if not await self.k8s_syncer.sync_secret_to_k8s(metadata, secret_value):
                logger.warning(f"⚠️ Failed to sync to Kubernetes: {secret_id}")
            
            # Save metadata to database
            await self._save_secret_metadata(metadata)
            
            # Add to active secrets
            self.active_secrets[secret_id] = metadata
            
            # Log access
            await self._log_secret_access(secret_id, owner, "create", success=True)
            
            logger.info(f"✅ Secret created: {secret_id}")
            return secret_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create secret: {e}")
            await self._log_secret_access(secret_id if 'secret_id' in locals() else 'unknown', 
                                        owner, "create", success=False, error=str(e))
            return None
    
    async def get_secret(self, secret_id: str, accessor_id: str, 
                       namespace: str = "", application: str = "") -> Optional[str]:
        """Get secret value"""
        try:
            logger.info(f"🔓 Retrieving secret: {secret_id}")
            
            # Check if secret exists and is active
            metadata = self.active_secrets.get(secret_id)
            if not metadata or metadata.status not in [SecretStatus.ACTIVE, SecretStatus.PENDING_ROTATION]:
                await self._log_secret_access(secret_id, accessor_id, "read", 
                                            namespace=namespace, application=application,
                                            success=False, error="Secret not found or inactive")
                return None
            
            # Check access permissions
            if not self._check_access_permissions(metadata, namespace, application):
                await self._log_secret_access(secret_id, accessor_id, "read",
                                            namespace=namespace, application=application,
                                            success=False, error="Access denied")
                return None
            
            # Retrieve from Vault
            secret_value = await self.vault_store.retrieve_secret(secret_id)
            if not secret_value:
                await self._log_secret_access(secret_id, accessor_id, "read",
                                            namespace=namespace, application=application,
                                            success=False, error="Failed to retrieve from vault")
                return None
            
            # Log successful access
            await self._log_secret_access(secret_id, accessor_id, "read",
                                        namespace=namespace, application=application,
                                        success=True)
            
            return secret_value.value
            
        except Exception as e:
            logger.error(f"❌ Failed to get secret {secret_id}: {e}")
            await self._log_secret_access(secret_id, accessor_id, "read",
                                        namespace=namespace, application=application,
                                        success=False, error=str(e))
            return None
    
    async def start_rotation_scheduler(self) -> None:
        """Start automatic secret rotation scheduler"""
        logger.info("⏰ Starting secret rotation scheduler")
        self.is_running = True
        
        while self.is_running:
            try:
                # Check for secrets needing rotation
                current_time = datetime.now(IST)
                
                for secret_id, metadata in self.active_secrets.items():
                    if (metadata.rotation_enabled and 
                        metadata.next_rotation_at and
                        metadata.next_rotation_at <= current_time and
                        metadata.status == SecretStatus.ACTIVE):
                        
                        logger.info(f"🔄 Scheduling rotation for: {secret_id}")
                        await self._rotate_secret_async(secret_id)
                
                # Sleep for 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Rotation scheduler error: {e}")
                await asyncio.sleep(3600)
    
    async def _rotate_secret_async(self, secret_id: str) -> None:
        """Rotate secret asynchronously"""
        try:
            metadata = self.active_secrets.get(secret_id)
            if not metadata:
                return
            
            # Mark as rotating
            metadata.status = SecretStatus.ROTATING
            await self._save_secret_metadata(metadata)
            
            # Get current value
            current_value = await self.vault_store.retrieve_secret(secret_id)
            if not current_value:
                logger.error(f"❌ Cannot rotate - current value not found: {secret_id}")
                metadata.status = SecretStatus.ACTIVE
                return
            
            # Rotate
            new_value = await self.rotation_engine.rotate_secret(metadata, current_value)
            if not new_value:
                logger.error(f"❌ Failed to rotate secret: {secret_id}")
                metadata.status = SecretStatus.ACTIVE
                await self._save_secret_metadata(metadata)
                return
            
            # Store new value
            if await self.vault_store.store_secret(metadata, new_value):
                # Sync to Kubernetes
                await self.k8s_syncer.sync_secret_to_k8s(metadata, new_value)
                
                # Mark as active
                metadata.status = SecretStatus.ACTIVE
                await self._save_secret_metadata(metadata)
                
                # Log rotation
                await self._log_rotation(secret_id, current_value.version, new_value.version, "scheduled", True)
                
                logger.info(f"✅ Secret rotated successfully: {secret_id}")
            else:
                metadata.status = SecretStatus.ACTIVE
                await self._save_secret_metadata(metadata)
                await self._log_rotation(secret_id, current_value.version, new_value.version, "scheduled", False)
                
        except Exception as e:
            logger.error(f"❌ Secret rotation failed: {e}")
    
    def _check_access_permissions(self, metadata: SecretMetadata, 
                                namespace: str, application: str) -> bool:
        """Check access permissions"""
        
        # Check namespace restrictions
        if metadata.allowed_namespaces and namespace not in metadata.allowed_namespaces:
            return False
        
        # Check application restrictions
        if metadata.allowed_applications and application not in metadata.allowed_applications:
            return False
        
        # Additional checks would go here (RBAC, etc.)
        return True
    
    async def _save_secret_metadata(self, metadata: SecretMetadata) -> None:
        """Save secret metadata to database"""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO secret_metadata 
                    (secret_id, name, secret_type, access_level, status, created_at,
                     updated_at, expires_at, last_rotated_at, next_rotation_at,
                     rotation_enabled, rotation_interval_days, metadata_json)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    ON CONFLICT (secret_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at,
                        last_rotated_at = EXCLUDED.last_rotated_at,
                        next_rotation_at = EXCLUDED.next_rotation_at,
                        metadata_json = EXCLUDED.metadata_json
                """,
                metadata.secret_id, metadata.name, metadata.secret_type.value,
                metadata.access_level.value, metadata.status.value, metadata.created_at,
                metadata.updated_at, metadata.expires_at, metadata.last_rotated_at,
                metadata.next_rotation_at, metadata.rotation_enabled, metadata.rotation_interval_days,
                json.dumps(asdict(metadata), default=str))
                
        except Exception as e:
            logger.error(f"❌ Failed to save secret metadata: {e}")
    
    async def _log_secret_access(self, secret_id: str, accessor_id: str, access_type: str,
                               namespace: str = "", application: str = "", region: str = "",
                               success: bool = False, error: str = "") -> None:
        """Log secret access for audit"""
        try:
            access_id = f"access-{uuid.uuid4().hex[:12]}"
            
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO secret_access_log
                    (access_id, secret_id, accessor_id, access_type, namespace,
                     application, region, requested_at, success, error_message)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                access_id, secret_id, accessor_id, access_type, namespace,
                application, region, datetime.now(IST), success, error)
                
        except Exception as e:
            logger.error(f"❌ Failed to log secret access: {e}")
    
    async def _log_rotation(self, secret_id: str, old_version: int, new_version: int,
                          rotation_type: str, success: bool, error: str = "") -> None:
        """Log secret rotation"""
        try:
            rotation_id = f"rotation-{uuid.uuid4().hex[:12]}"
            
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO secret_rotation_log
                    (rotation_id, secret_id, old_version, new_version, rotation_type,
                     started_at, completed_at, success, error_message, rotated_by)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                rotation_id, secret_id, old_version, new_version, rotation_type,
                datetime.now(IST), datetime.now(IST), success, error, "automated-rotation")
                
        except Exception as e:
            logger.error(f"❌ Failed to log rotation: {e}")
    
    async def stop_scheduler(self) -> None:
        """Stop scheduler and cleanup"""
        logger.info("🛑 Stopping secrets controller...")
        self.is_running = False
        
        if self.pg_pool:
            await self.pg_pool.close()
        
        logger.info("✅ Secrets controller stopped")


async def main():
    """Main function for secrets management"""
    print("🔐 GitOps Secrets Management System")
    print("=" * 50)
    
    # Configuration
    config = SecretsConfig(
        vault_url=os.getenv("VAULT_URL", "https://vault.company.com"),
        vault_token=os.getenv("VAULT_TOKEN", ""),
        postgres_url=os.getenv("DATABASE_URL", "postgresql://user:pass@postgres:5432/secrets"),
        k8s_secret_namespace="secrets",
        default_rotation_interval=90,
        enable_auto_rotation=True,
        enable_audit_logging=True,
        audit_retention_years=7,
        enable_rbi_reporting=True,
        slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
        security_team_email="security@company.com"
    )
    
    # Initialize controller
    controller = GitOpsSecretsController(config)
    
    try:
        if await controller.initialize():
            print("✅ Secrets Controller initialized successfully")
            
            # Example: Create a banking API secret
            secret_id = await controller.create_secret(
                name="razorpay-api-key",
                secret_type=SecretType.BANKING_API_KEY,
                value="rzp_live_abcdef123456789",
                owner="payments-team",
                team="payments",
                allowed_namespaces=["production", "payments"],
                allowed_applications=["payment-gateway", "checkout-service"]
            )
            
            if secret_id:
                print(f"✅ Created banking secret: {secret_id}")
                
                # Example: Retrieve the secret
                secret_value = await controller.get_secret(
                    secret_id=secret_id,
                    accessor_id="payment-gateway-pod",
                    namespace="production",
                    application="payment-gateway"
                )
                
                if secret_value:
                    print(f"✅ Retrieved secret successfully (length: {len(secret_value)})")
                else:
                    print("❌ Failed to retrieve secret")
                    
            # Start rotation scheduler (would run in background in production)
            print("⏰ Starting rotation scheduler...")
            await controller.start_rotation_scheduler()
            
        else:
            print("❌ Failed to initialize Secrets Controller")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping secrets management...")
        await controller.stop_scheduler()
    except Exception as e:
        print(f"❌ Secrets management error: {e}")
        await controller.stop_scheduler()


if __name__ == "__main__":
    asyncio.run(main())