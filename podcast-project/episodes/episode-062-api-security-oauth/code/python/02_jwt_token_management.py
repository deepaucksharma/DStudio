"""
Advanced JWT Token Management System
===================================

यह system JWT tokens का complete lifecycle manage करता है।
HDFC Bank, ICICI Bank जैसे banking systems में इसी तरह की 
token management होती है।

Features:
- Token Generation with Custom Claims
- Token Validation and Verification
- Token Rotation and Refresh
- Blacklist Management
- Security Headers Integration
- Audit Trail

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

import jwt
import json
import time
import hashlib
import secrets
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenType(Enum):
    """Token types - Different purpose ke liye alag tokens"""
    ACCESS = "access_token"
    REFRESH = "refresh_token"
    ID = "id_token"
    RESET = "reset_token"
    VERIFICATION = "verification_token"

@dataclass
class TokenClaims:
    """JWT Claims structure - Banking grade security ke liye"""
    user_id: str
    client_id: str
    scopes: List[str]
    roles: List[str]
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Banking specific claims
    account_access: Optional[List[str]] = None
    transaction_limit: Optional[float] = None
    mfa_verified: bool = False
    risk_score: float = 0.0

class JWTManager:
    """
    Production grade JWT Token Manager
    
    यह class JWT tokens का complete management करती है।
    Banking apps में इसी level की security होती है।
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
        # RSA Key Pair for production grade security
        self.private_key = self._generate_private_key()
        self.public_key = self.private_key.public_key()
        
        # Token expiry settings - Banking standards के अनुसार
        self.token_expiry = {
            TokenType.ACCESS: timedelta(minutes=15),    # Short lived
            TokenType.REFRESH: timedelta(days=30),      # Long lived
            TokenType.ID: timedelta(hours=1),           # Medium lived
            TokenType.RESET: timedelta(minutes=10),     # Very short
            TokenType.VERIFICATION: timedelta(hours=24) # Day long
        }
        
        # Algorithm configuration
        self.algorithm = "RS256"  # RSA with SHA-256
        
        # Security configuration
        self.issuer = "hdfc-bank-api"  # Bank identifier
        self.audience = "hdfc-mobile-banking"  # App identifier
        
    def _generate_private_key(self) -> rsa.RSAPrivateKey:
        """RSA private key generate करता है - 2048 bit security"""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
    
    def _get_private_key_pem(self) -> bytes:
        """Private key का PEM format return करता है"""
        return self.private_key.private_key(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    def _get_public_key_pem(self) -> bytes:
        """Public key का PEM format return करता है"""
        return self.public_key.public_key(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def generate_token(
        self, 
        token_type: TokenType, 
        claims: TokenClaims,
        custom_expiry: Optional[timedelta] = None
    ) -> str:
        """
        JWT token generate करता है
        
        Banking grade security के साथ comprehensive claims
        """
        
        # Current time
        now = datetime.utcnow()
        expiry = custom_expiry or self.token_expiry[token_type]
        
        # Standard JWT claims
        payload = {
            "iss": self.issuer,                    # Issuer
            "aud": self.audience,                  # Audience  
            "sub": claims.user_id,                 # Subject (User ID)
            "iat": int(now.timestamp()),           # Issued At
            "exp": int((now + expiry).timestamp()), # Expiry
            "nbf": int(now.timestamp()),           # Not Before
            "jti": self._generate_jti(),           # JWT ID (unique)
            "typ": token_type.value                # Token Type
        }
        
        # Custom claims add करें
        payload.update({
            "client_id": claims.client_id,
            "scopes": claims.scopes,
            "roles": claims.roles,
            "device_id": claims.device_id,
            "session_id": claims.session_id,
            "ip_address": claims.ip_address,
            "user_agent": claims.user_agent,
            "account_access": claims.account_access,
            "transaction_limit": claims.transaction_limit,
            "mfa_verified": claims.mfa_verified,
            "risk_score": claims.risk_score
        })
        
        # Token generate करें using RSA private key
        token = jwt.encode(payload, self._get_private_key_pem(), algorithm=self.algorithm)
        
        # Token को Redis में store करें - Revocation के लिए
        jti = payload["jti"]
        redis_key = f"token:{jti}"
        token_metadata = {
            "user_id": claims.user_id,
            "client_id": claims.client_id,
            "token_type": token_type.value,
            "created_at": now.isoformat(),
            "expires_at": (now + expiry).isoformat(),
            "ip_address": claims.ip_address,
            "device_id": claims.device_id
        }
        
        # Store in Redis with expiry
        self.redis_client.setex(
            redis_key, 
            int(expiry.total_seconds()), 
            json.dumps(token_metadata)
        )
        
        # Audit log
        self._log_token_event("token_generated", {
            "jti": jti,
            "user_id": claims.user_id,
            "token_type": token_type.value,
            "scopes": claims.scopes,
            "expires_in": int(expiry.total_seconds())
        })
        
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Token validate करता है - Security checks के साथ
        
        हर API call पर यह function चलता है
        """
        
        try:
            # Decode token using public key
            payload = jwt.decode(
                token, 
                self._get_public_key_pem(), 
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer
            )
            
            jti = payload.get("jti")
            if not jti:
                logger.warning("Token missing JTI")
                return None
            
            # Check if token is blacklisted
            if self.is_token_blacklisted(jti):
                logger.warning(f"Token {jti} is blacklisted")
                return None
            
            # Check if token exists in Redis
            redis_key = f"token:{jti}"
            token_metadata = self.redis_client.get(redis_key)
            if not token_metadata:
                logger.warning(f"Token {jti} not found in store")
                return None
            
            # Additional security validations
            if not self._validate_security_context(payload):
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh token से new access token generate करता है
        
        Banking apps में automatic token refresh होता है
        """
        
        # Refresh token validate करें
        payload = self.validate_token(refresh_token)
        if not payload:
            return None
        
        # Check token type
        if payload.get("typ") != TokenType.REFRESH.value:
            logger.warning("Invalid token type for refresh")
            return None
        
        # Create new claims from refresh token
        claims = TokenClaims(
            user_id=payload["sub"],
            client_id=payload["client_id"],
            scopes=payload["scopes"],
            roles=payload["roles"],
            device_id=payload["device_id"],
            session_id=payload["session_id"],
            ip_address=payload["ip_address"],
            user_agent=payload["user_agent"],
            account_access=payload["account_access"],
            transaction_limit=payload["transaction_limit"],
            mfa_verified=payload["mfa_verified"],
            risk_score=payload["risk_score"]
        )
        
        # Generate new tokens
        new_access_token = self.generate_token(TokenType.ACCESS, claims)
        new_refresh_token = self.generate_token(TokenType.REFRESH, claims)
        
        # Blacklist old refresh token
        self.blacklist_token(refresh_token)
        
        self._log_token_event("token_refreshed", {
            "user_id": claims.user_id,
            "old_jti": payload["jti"]
        })
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": int(self.token_expiry[TokenType.ACCESS].total_seconds())
        }
    
    def blacklist_token(self, token: str) -> bool:
        """
        Token को blacklist करता है - Immediate revocation
        
        Security breach या user logout पर use होता है
        """
        
        try:
            # Extract JTI without validation (for blacklisting)
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            jti = unverified_payload.get("jti")
            
            if not jti:
                return False
            
            # Add to blacklist set - Never expires automatically
            blacklist_key = f"blacklist:{jti}"
            self.redis_client.setex(blacklist_key, 86400 * 365, "blacklisted")  # 1 year
            
            # Remove from active tokens
            self.redis_client.delete(f"token:{jti}")
            
            self._log_token_event("token_blacklisted", {
                "jti": jti,
                "reason": "manual_revocation"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False
    
    def is_token_blacklisted(self, jti: str) -> bool:
        """Check करता है कि token blacklisted है या नहीं"""
        blacklist_key = f"blacklist:{jti}"
        return self.redis_client.exists(blacklist_key) > 0
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Token की detailed information return करता है
        
        Admin panel या debugging के लिए useful
        """
        
        payload = self.validate_token(token)
        if not payload:
            return None
        
        jti = payload["jti"]
        redis_key = f"token:{jti}"
        metadata = self.redis_client.get(redis_key)
        
        if metadata:
            metadata = json.loads(metadata)
        
        return {
            "jti": jti,
            "user_id": payload["sub"],
            "client_id": payload["client_id"],
            "token_type": payload["typ"],
            "scopes": payload["scopes"],
            "roles": payload["roles"],
            "issued_at": datetime.fromtimestamp(payload["iat"]).isoformat(),
            "expires_at": datetime.fromtimestamp(payload["exp"]).isoformat(),
            "metadata": metadata
        }
    
    def rotate_signing_keys(self) -> Dict[str, str]:
        """
        Signing keys को rotate करता है - Security best practice
        
        Production में regular intervals पर run करना चाहिए
        """
        
        # Old keys backup करें
        old_private_key_pem = self._get_private_key_pem().decode()
        old_public_key_pem = self._get_public_key_pem().decode()
        
        # New keys generate करें
        self.private_key = self._generate_private_key()
        self.public_key = self.private_key.public_key()
        
        # Store old keys with timestamp for verification
        timestamp = datetime.utcnow().isoformat()
        self.redis_client.setex(
            f"old_keys:{timestamp}", 
            86400 * 7,  # 7 days
            json.dumps({
                "private_key": old_private_key_pem,
                "public_key": old_public_key_pem,
                "rotated_at": timestamp
            })
        )
        
        self._log_token_event("keys_rotated", {
            "timestamp": timestamp,
            "reason": "scheduled_rotation"
        })
        
        return {
            "old_public_key": old_public_key_pem,
            "new_public_key": self._get_public_key_pem().decode(),
            "rotated_at": timestamp
        }
    
    def cleanup_expired_tokens(self) -> int:
        """
        Expired tokens का cleanup करता है
        
        Cron job के रूप में daily run करना चाहिए
        """
        
        cleaned_count = 0
        
        # Get all token keys
        token_keys = self.redis_client.keys("token:*")
        
        for key in token_keys:
            try:
                # Check if key exists (might have expired)
                if not self.redis_client.exists(key):
                    cleaned_count += 1
                    continue
                
                # Get token metadata
                metadata = self.redis_client.get(key)
                if not metadata:
                    continue
                
                metadata = json.loads(metadata)
                expires_at = datetime.fromisoformat(metadata["expires_at"])
                
                # If expired, remove from active tokens
                if datetime.utcnow() > expires_at:
                    self.redis_client.delete(key)
                    cleaned_count += 1
                    
            except Exception as e:
                logger.error(f"Error cleaning token {key}: {e}")
                
        self._log_token_event("tokens_cleaned", {
            "cleaned_count": cleaned_count
        })
        
        return cleaned_count
    
    def _generate_jti(self) -> str:
        """Unique JWT ID generate करता है"""
        return secrets.token_urlsafe(16)
    
    def _validate_security_context(self, payload: Dict[str, Any]) -> bool:
        """
        Security context validate करता है
        
        Additional security checks - Banking level
        """
        
        # Risk score check
        risk_score = payload.get("risk_score", 0.0)
        if risk_score > 0.8:  # High risk threshold
            logger.warning(f"High risk token detected: {risk_score}")
            return False
        
        # MFA requirement for sensitive operations
        sensitive_scopes = ["transfer", "payment", "account_management"]
        token_scopes = payload.get("scopes", [])
        
        if any(scope in sensitive_scopes for scope in token_scopes):
            if not payload.get("mfa_verified", False):
                logger.warning("MFA required for sensitive scope")
                return False
        
        # Device binding check
        device_id = payload.get("device_id")
        if device_id:
            # Check if device is still valid
            device_key = f"device:{device_id}"
            if not self.redis_client.exists(device_key):
                logger.warning(f"Device {device_id} not registered")
                return False
        
        return True
    
    def _log_token_event(self, event_type: str, details: Dict[str, Any]):
        """Token events को log करता है - Audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "service": "jwt_manager"
        }
        logger.info(f"Token Event: {json.dumps(log_entry)}")

class TokenMiddleware:
    """
    Token validation middleware for FastAPI/Flask
    
    हर API request पर token validate करता है
    """
    
    def __init__(self, jwt_manager: JWTManager):
        self.jwt_manager = jwt_manager
    
    def validate_request_token(self, authorization_header: str) -> Optional[Dict[str, Any]]:
        """Authorization header से token validate करता है"""
        
        if not authorization_header:
            return None
        
        # Bearer token extract करें
        try:
            scheme, token = authorization_header.split()
            if scheme.lower() != "bearer":
                return None
        except ValueError:
            return None
        
        return self.jwt_manager.validate_token(token)
    
    def require_scopes(self, required_scopes: List[str]) -> bool:
        """Required scopes check करता है"""
        # Implementation would depend on request context
        # This is a placeholder for the concept
        pass

# Example usage और testing
if __name__ == "__main__":
    # Redis connection
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # JWT Manager initialize करें
    jwt_manager = JWTManager(redis_client)
    
    print("🔐 JWT Token Management System")
    print("🏦 Banking grade security implementation")
    print("💳 Mumbai banking style token management")
    
    # Test claims
    test_claims = TokenClaims(
        user_id="user_mumbai_123",
        client_id="hdfc_mobile_app",
        scopes=["read", "write", "transfer"],
        roles=["customer", "premium"],
        device_id="device_samsung_galaxy",
        session_id="session_" + secrets.token_hex(8),
        ip_address="192.168.1.100",
        user_agent="HDFC Mobile App 2.1.0",
        account_access=["savings_001", "current_002"],
        transaction_limit=100000.0,
        mfa_verified=True,
        risk_score=0.2
    )
    
    # Generate tokens
    access_token = jwt_manager.generate_token(TokenType.ACCESS, test_claims)
    refresh_token = jwt_manager.generate_token(TokenType.REFRESH, test_claims)
    
    print(f"\n✅ Access Token Generated: {access_token[:50]}...")
    print(f"✅ Refresh Token Generated: {refresh_token[:50]}...")
    
    # Validate token
    payload = jwt_manager.validate_token(access_token)
    if payload:
        print(f"✅ Token Validation Successful")
        print(f"👤 User: {payload['sub']}")
        print(f"🔒 Scopes: {payload['scopes']}")
        print(f"⏰ Expires: {datetime.fromtimestamp(payload['exp'])}")
    
    # Token info
    token_info = jwt_manager.get_token_info(access_token)
    if token_info:
        print(f"\n📊 Token Info:")
        print(f"🆔 JTI: {token_info['jti']}")
        print(f"🏦 Client: {token_info['client_id']}")
        print(f"⚡ Type: {token_info['token_type']}")
    
    # Refresh token test
    new_tokens = jwt_manager.refresh_token(refresh_token)
    if new_tokens:
        print(f"\n🔄 Token Refresh Successful")
        print(f"🆕 New Access Token: {new_tokens['access_token'][:50]}...")
    
    print(f"\n🚀 JWT Token Management System Ready!")
    print(f"🔐 Production grade security implemented")
    print(f"🏦 Banking level token protection active")

"""
Production Implementation Notes:
==============================

1. Key Management:
   - Use HSM (Hardware Security Module) for key storage
   - Implement key rotation schedule (monthly/quarterly)
   - Store keys securely (AWS KMS, Azure Key Vault)

2. Security Enhancements:
   - Add IP whitelisting
   - Implement device fingerprinting
   - Add geolocation checks
   - Implement rate limiting per user/device

3. Monitoring:
   - Token generation metrics
   - Failed validation alerts
   - Unusual activity detection
   - Performance monitoring

4. Compliance:
   - PCI DSS compliance for payment tokens
   - GDPR compliance for EU users
   - RBI guidelines for banking apps
   - SOC 2 Type II certification

यह implementation HDFC Bank, ICICI Bank level की security provide करता है!
"""