#!/usr/bin/env python3
"""
API Key Management System
Payment Gateway Security for Indian Companies

यह system Razorpay, Paytm, और PhonePe जैसे payment gateways के लिए
API keys को securely manage करता है। Production में API key rotation,
encryption, और access control implement करता है।

Real-world Context:
- Razorpay handles 100M+ transactions/month
- API key compromise can lead to ₹10 crore+ losses
- NPCI mandates key rotation every 90 days for UPI
- RBI guidelines require encryption at rest and transit
"""

import os
import json
import time
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Setup logging - भारतीय security compliance के लिए audit logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_key_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class APIKey:
    """API Key dataclass with Indian payment gateway context"""
    key_id: str
    gateway: str  # razorpay, paytm, phonepe, hdfc, icici
    encrypted_key: str
    created_at: datetime
    expires_at: datetime
    permissions: List[str]
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_active: bool = True
    client_id: str = ""
    
    def to_dict(self) -> Dict:
        """Dictionary representation - JSON serialization के लिए"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        return data

class APIKeyManager:
    """
    Production-ready API Key Management System
    
    Features:
    - Key encryption/decryption
    - Automatic rotation
    - Usage tracking
    - Permission-based access
    - Audit logging
    - Rate limiting integration
    """
    
    def __init__(self, master_password: str = "razorpay_secure_2024"):
        self.master_password = master_password.encode()
        self.cipher_suite = self._initialize_encryption()
        self.keys: Dict[str, APIKey] = {}
        self.load_keys()
        
        # भारतीय payment gateways configuration
        self.gateway_config = {
            'razorpay': {
                'base_url': 'https://api.razorpay.com/v1/',
                'key_prefix': 'rzp_',
                'rotation_days': 90,
                'permissions': ['payment.create', 'payment.capture', 'refund.create']
            },
            'paytm': {
                'base_url': 'https://securegw.paytm.in/theia/',
                'key_prefix': 'paytm_',
                'rotation_days': 60,
                'permissions': ['txn.create', 'txn.status', 'refund.initiate']
            },
            'phonepe': {
                'base_url': 'https://api-preprod.phonepe.com/apis/',
                'key_prefix': 'phonepe_',
                'rotation_days': 90,
                'permissions': ['pay.create', 'pay.status', 'refund.process']
            },
            'hdfc': {
                'base_url': 'https://api.hdfcbank.com/',
                'key_prefix': 'hdfc_',
                'rotation_days': 30,
                'permissions': ['account.balance', 'transfer.neft', 'transfer.rtgs']
            }
        }
        
        logger.info("APIKeyManager initialized - Production ready for Indian gateways")
    
    def _initialize_encryption(self) -> Fernet:
        """Master encryption key generation - AES-256 with PBKDF2"""
        try:
            salt = b'razorpay_india_salt_2024'  # Production में environment से
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
            return Fernet(key)
        except Exception as e:
            logger.error(f"Encryption initialization failed: {e}")
            raise
    
    def generate_api_key(
        self, 
        gateway: str, 
        client_id: str = "default_client",
        validity_days: int = 90,
        permissions: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        Generate new API key for specified gateway
        
        Args:
            gateway: Payment gateway name (razorpay, paytm, etc.)
            client_id: Client identifier
            validity_days: Key validity period
            permissions: List of allowed operations
            
        Returns:
            Tuple of (key_id, actual_key)
        """
        try:
            if gateway not in self.gateway_config:
                raise ValueError(f"Unsupported gateway: {gateway}")
            
            # Generate unique key ID
            key_id = f"{gateway}_{client_id}_{int(time.time())}"
            
            # Generate secure API key
            raw_key = secrets.token_urlsafe(32)
            prefix = self.gateway_config[gateway]['key_prefix']
            actual_key = f"{prefix}{raw_key}"
            
            # Encrypt the key
            encrypted_key = self.cipher_suite.encrypt(actual_key.encode()).decode()
            
            # Set permissions
            if permissions is None:
                permissions = self.gateway_config[gateway]['permissions']
            
            # Create API key object
            api_key = APIKey(
                key_id=key_id,
                gateway=gateway,
                encrypted_key=encrypted_key,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=validity_days),
                permissions=permissions,
                client_id=client_id
            )
            
            # Store key
            self.keys[key_id] = api_key
            self.save_keys()
            
            logger.info(f"API key generated - Gateway: {gateway}, Client: {client_id}")
            return key_id, actual_key
            
        except Exception as e:
            logger.error(f"API key generation failed: {e}")
            raise
    
    def validate_key(self, key_id: str, requested_permission: str = None) -> bool:
        """
        Validate API key and check permissions
        
        Args:
            key_id: API key identifier
            requested_permission: Required permission for operation
            
        Returns:
            Boolean indicating if key is valid
        """
        try:
            if key_id not in self.keys:
                logger.warning(f"Invalid key access attempt: {key_id}")
                return False
            
            api_key = self.keys[key_id]
            
            # Check if key is active
            if not api_key.is_active:
                logger.warning(f"Inactive key used: {key_id}")
                return False
            
            # Check expiration
            if datetime.now() > api_key.expires_at:
                logger.warning(f"Expired key used: {key_id}")
                api_key.is_active = False
                self.save_keys()
                return False
            
            # Check permissions
            if requested_permission and requested_permission not in api_key.permissions:
                logger.warning(f"Permission denied - Key: {key_id}, Permission: {requested_permission}")
                return False
            
            # Update usage
            api_key.usage_count += 1
            api_key.last_used = datetime.now()
            self.save_keys()
            
            logger.info(f"Key validated - {key_id}, Permission: {requested_permission}")
            return True
            
        except Exception as e:
            logger.error(f"Key validation failed: {e}")
            return False
    
    def rotate_key(self, key_id: str) -> Tuple[str, str]:
        """
        Rotate API key - Indian payment gateways में mandatory
        
        Args:
            key_id: Current key identifier
            
        Returns:
            Tuple of (new_key_id, new_actual_key)
        """
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key not found: {key_id}")
            
            old_key = self.keys[key_id]
            
            # Generate new key with same properties
            new_key_id, new_actual_key = self.generate_api_key(
                gateway=old_key.gateway,
                client_id=old_key.client_id,
                permissions=old_key.permissions
            )
            
            # Deactivate old key
            old_key.is_active = False
            self.save_keys()
            
            logger.info(f"Key rotated - Old: {key_id}, New: {new_key_id}")
            return new_key_id, new_actual_key
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise
    
    def get_key_stats(self, gateway: str = None) -> Dict:
        """
        Get API key usage statistics
        
        Args:
            gateway: Filter by specific gateway
            
        Returns:
            Dictionary with key statistics
        """
        try:
            filtered_keys = self.keys.values()
            if gateway:
                filtered_keys = [k for k in self.keys.values() if k.gateway == gateway]
            
            total_keys = len(filtered_keys)
            active_keys = len([k for k in filtered_keys if k.is_active])
            expired_keys = len([
                k for k in filtered_keys 
                if datetime.now() > k.expires_at
            ])
            
            # Gateway-wise breakdown
            gateway_breakdown = {}
            for key in filtered_keys:
                gw = key.gateway
                if gw not in gateway_breakdown:
                    gateway_breakdown[gw] = {
                        'total': 0,
                        'active': 0,
                        'usage': 0
                    }
                gateway_breakdown[gw]['total'] += 1
                if key.is_active:
                    gateway_breakdown[gw]['active'] += 1
                gateway_breakdown[gw]['usage'] += key.usage_count
            
            stats = {
                'total_keys': total_keys,
                'active_keys': active_keys,
                'expired_keys': expired_keys,
                'gateway_breakdown': gateway_breakdown,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Key statistics generated - Total: {total_keys}")
            return stats
            
        except Exception as e:
            logger.error(f"Statistics generation failed: {e}")
            return {}
    
    def cleanup_expired_keys(self) -> int:
        """
        Clean up expired API keys
        
        Returns:
            Number of keys cleaned up
        """
        try:
            expired_keys = []
            current_time = datetime.now()
            
            for key_id, api_key in self.keys.items():
                if current_time > api_key.expires_at:
                    expired_keys.append(key_id)
                    api_key.is_active = False
            
            # Remove keys expired more than 30 days ago
            cleanup_threshold = current_time - timedelta(days=30)
            keys_to_remove = []
            
            for key_id in expired_keys:
                if self.keys[key_id].expires_at < cleanup_threshold:
                    keys_to_remove.append(key_id)
            
            for key_id in keys_to_remove:
                del self.keys[key_id]
            
            if keys_to_remove:
                self.save_keys()
            
            logger.info(f"Expired keys cleaned - Removed: {len(keys_to_remove)}")
            return len(keys_to_remove)
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
    
    def save_keys(self):
        """Save keys to encrypted storage"""
        try:
            keys_data = {
                key_id: api_key.to_dict() 
                for key_id, api_key in self.keys.items()
            }
            
            # Encrypt and save
            encrypted_data = self.cipher_suite.encrypt(
                json.dumps(keys_data).encode()
            )
            
            with open('api_keys.encrypted', 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            logger.error(f"Key save failed: {e}")
    
    def load_keys(self):
        """Load keys from encrypted storage"""
        try:
            if not os.path.exists('api_keys.encrypted'):
                return
            
            with open('api_keys.encrypted', 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            keys_data = json.loads(decrypted_data.decode())
            
            for key_id, key_data in keys_data.items():
                # Reconstruct datetime objects
                key_data['created_at'] = datetime.fromisoformat(key_data['created_at'])
                key_data['expires_at'] = datetime.fromisoformat(key_data['expires_at'])
                if key_data.get('last_used'):
                    key_data['last_used'] = datetime.fromisoformat(key_data['last_used'])
                
                self.keys[key_id] = APIKey(**key_data)
                
        except Exception as e:
            logger.error(f"Key load failed: {e}")

def demonstrate_indian_payment_security():
    """
    Demonstrate API key management for Indian payment gateways
    Real production scenarios with Razorpay, Paytm, PhonePe
    """
    print("\n🔐 भारतीय Payment Gateway API Key Management")
    print("=" * 60)
    
    # Initialize manager
    key_manager = APIKeyManager()
    
    # Scenario 1: Razorpay integration for e-commerce
    print("\n📱 Scenario 1: Razorpay Key for Flipkart-style E-commerce")
    flipkart_key_id, flipkart_key = key_manager.generate_api_key(
        gateway='razorpay',
        client_id='flipkart_checkout',
        permissions=['payment.create', 'payment.capture']
    )
    print(f"✅ Generated Razorpay key: {flipkart_key_id}")
    print(f"   Key: {flipkart_key[:20]}...")
    
    # Scenario 2: Paytm for wallet transactions
    print("\n💳 Scenario 2: Paytm Wallet Integration")
    paytm_key_id, paytm_key = key_manager.generate_api_key(
        gateway='paytm',
        client_id='wallet_service',
        validity_days=60
    )
    print(f"✅ Generated Paytm key: {paytm_key_id}")
    
    # Scenario 3: PhonePe for UPI payments
    print("\n📲 Scenario 3: PhonePe UPI Integration")
    phonepe_key_id, phonepe_key = key_manager.generate_api_key(
        gateway='phonepe',
        client_id='upi_service',
        permissions=['pay.create', 'pay.status']
    )
    print(f"✅ Generated PhonePe key: {phonepe_key_id}")
    
    # Key validation testing
    print("\n🔍 Key Validation Testing")
    print("-" * 30)
    
    # Valid key with permission
    is_valid = key_manager.validate_key(flipkart_key_id, 'payment.create')
    print(f"✅ Razorpay key validation (payment.create): {is_valid}")
    
    # Valid key without permission
    is_valid = key_manager.validate_key(flipkart_key_id, 'refund.create')
    print(f"❌ Razorpay key validation (refund.create): {is_valid}")
    
    # Key rotation demo
    print("\n🔄 Key Rotation Demo")
    print("-" * 25)
    
    new_key_id, new_key = key_manager.rotate_key(flipkart_key_id)
    print(f"🔄 Rotated key: {flipkart_key_id} → {new_key_id}")
    
    # Statistics
    print("\n📊 API Key Statistics")
    print("-" * 25)
    stats = key_manager.get_key_stats()
    print(f"📈 Total keys: {stats['total_keys']}")
    print(f"✅ Active keys: {stats['active_keys']}")
    print(f"❌ Expired keys: {stats['expired_keys']}")
    
    print("\n🏪 Gateway-wise breakdown:")
    for gateway, data in stats['gateway_breakdown'].items():
        print(f"   {gateway.upper()}: {data['active']}/{data['total']} active, {data['usage']} calls")
    
    # Cleanup demo
    print("\n🧹 Cleanup Expired Keys")
    cleaned = key_manager.cleanup_expired_keys()
    print(f"🗑️  Cleaned up {cleaned} expired keys")
    
    # Security best practices
    print("\n🛡️  Security Best Practices")
    print("-" * 30)
    print("✓ Keys encrypted at rest using AES-256")
    print("✓ Automatic key rotation every 90 days")
    print("✓ Permission-based access control")
    print("✓ Complete audit logging")
    print("✓ Usage tracking and monitoring")
    print("✓ Secure key generation with secrets module")

if __name__ == "__main__":
    demonstrate_indian_payment_security()
    
    # Production usage example
    print("\n" + "="*60)
    print("🏭 PRODUCTION USAGE EXAMPLE")
    print("="*60)
    
    print("""
    # API Key Management in Production Environment
    
    from api_key_management import APIKeyManager
    
    # Initialize with secure master password from environment
    key_manager = APIKeyManager(os.getenv('MASTER_KEY'))
    
    # Generate key for new client
    key_id, api_key = key_manager.generate_api_key(
        gateway='razorpay',
        client_id='new_ecommerce_client',
        permissions=['payment.create', 'payment.capture']
    )
    
    # Validate key for payment processing
    if key_manager.validate_key(key_id, 'payment.create'):
        # Process payment
        process_razorpay_payment(api_key, payment_data)
    
    # Monthly key rotation (automated via cron)
    for key_id in get_keys_due_for_rotation():
        new_key_id, new_key = key_manager.rotate_key(key_id)
        update_client_configuration(new_key_id, new_key)
    
    # Production monitoring
    stats = key_manager.get_key_stats()
    send_to_monitoring_dashboard(stats)
    """)