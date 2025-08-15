"""
API Key Rotation System
======================

यह system automatic API key rotation implement करता है।
AWS, Azure जैसे cloud providers अपने API keys को इसी तरह 
automatically rotate करते हैं security best practices के लिए।

Features:
- Automatic Key Generation
- Graceful Key Rotation
- Zero-Downtime Updates
- Audit Trail
- Emergency Revocation
- Multi-Environment Support

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

import asyncio
import hashlib
import secrets
import time
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import schedule
import threading

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeyStatus(Enum):
    """API key status"""
    ACTIVE = "active"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"
    EXPIRED = "expired"

class RotationTrigger(Enum):
    """Key rotation triggers"""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    SECURITY_INCIDENT = "security_incident"
    USAGE_THRESHOLD = "usage_threshold"
    COMPROMISE_DETECTED = "compromise_detected"

@dataclass
class APIKey:
    """API Key data structure"""
    key_id: str
    key_value: str
    client_id: str
    environment: str  # dev, staging, prod
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    status: KeyStatus
    usage_count: int = 0
    last_used: Optional[datetime] = None
    rotation_count: int = 0

@dataclass
class RotationEvent:
    """Key rotation event"""
    event_id: str
    key_id: str
    old_key: str
    new_key: str
    trigger: RotationTrigger
    timestamp: datetime
    client_id: str
    environment: str
    success: bool
    error_message: Optional[str] = None

class APIKeyGenerator:
    """Secure API key generator"""
    
    @staticmethod
    def generate_key_pair() -> Tuple[str, str]:
        """Key ID और Key Value generate करता है"""
        
        # Key ID format: ak_<env>_<random>
        key_id = f"ak_{secrets.token_hex(4)}_{secrets.token_hex(8)}"
        
        # Key Value: Base64 encoded secure random bytes
        key_value = secrets.token_urlsafe(48)  # 48 bytes = 64 chars in base64
        
        return key_id, key_value
    
    @staticmethod
    def generate_signing_key() -> str:
        """API key signing के लिए key generate करता है"""
        return Fernet.generate_key().decode()

class APIKeyRotationManager:
    """
    API Key Rotation Manager
    
    यह class complete API key lifecycle manage करती है
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key.encode())
        
        # Rotation policies
        self.rotation_policies = {
            "dev": {
                "rotation_interval_days": 30,
                "max_usage_count": 100000,
                "auto_rotate": True
            },
            "staging": {
                "rotation_interval_days": 15,
                "max_usage_count": 50000,
                "auto_rotate": True
            },
            "prod": {
                "rotation_interval_days": 7,
                "max_usage_count": 1000000,
                "auto_rotate": True
            }
        }
        
        # Grace period for old keys (overlap period)
        self.grace_period_hours = 24
        
        # Start background rotation scheduler
        self._start_rotation_scheduler()
    
    def _get_or_create_encryption_key(self) -> str:
        """Encryption key को Redis से get करता है या create करता है"""
        
        key = self.redis.get("api_key_encryption_key")
        if not key:
            key = Fernet.generate_key().decode()
            self.redis.set("api_key_encryption_key", key)
            logger.info("Created new encryption key for API keys")
        
        return key
    
    async def create_api_key(
        self, 
        client_id: str, 
        environment: str, 
        permissions: List[str],
        expires_in_days: Optional[int] = None
    ) -> APIKey:
        """नई API key create करता है"""
        
        key_id, key_value = APIKeyGenerator.generate_key_pair()
        
        # Set expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key object
        api_key = APIKey(
            key_id=key_id,
            key_value=key_value,
            client_id=client_id,
            environment=environment,
            permissions=permissions,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            status=KeyStatus.ACTIVE,
            usage_count=0,
            rotation_count=0
        )
        
        # Store in Redis (encrypted)
        await self._store_api_key(api_key)
        
        # Log creation event
        await self._log_key_event("key_created", {
            "key_id": key_id,
            "client_id": client_id,
            "environment": environment,
            "permissions": permissions
        })
        
        logger.info(f"Created API key {key_id} for client {client_id}")
        return api_key
    
    async def rotate_api_key(
        self, 
        key_id: str, 
        trigger: RotationTrigger = RotationTrigger.MANUAL
    ) -> Tuple[APIKey, APIKey]:
        """API key को rotate करता है"""
        
        # Get current key
        current_key = await self._get_api_key(key_id)
        if not current_key:
            raise ValueError(f"API key {key_id} not found")
        
        if current_key.status not in [KeyStatus.ACTIVE, KeyStatus.ROTATING]:
            raise ValueError(f"Cannot rotate key in status: {current_key.status}")
        
        # Mark current key as rotating
        current_key.status = KeyStatus.ROTATING
        await self._store_api_key(current_key)
        
        try:
            # Generate new key
            new_key_id, new_key_value = APIKeyGenerator.generate_key_pair()
            
            # Create new API key with same permissions
            new_api_key = APIKey(
                key_id=new_key_id,
                key_value=new_key_value,
                client_id=current_key.client_id,
                environment=current_key.environment,
                permissions=current_key.permissions.copy(),
                created_at=datetime.utcnow(),
                expires_at=current_key.expires_at,
                status=KeyStatus.ACTIVE,
                usage_count=0,
                rotation_count=current_key.rotation_count + 1
            )
            
            # Store new key
            await self._store_api_key(new_api_key)
            
            # Schedule old key deprecation (after grace period)
            await self._schedule_key_deprecation(current_key.key_id, self.grace_period_hours)
            
            # Log rotation event
            rotation_event = RotationEvent(
                event_id=secrets.token_hex(8),
                key_id=current_key.key_id,
                old_key=current_key.key_value[:10] + "...",  # Partial for security
                new_key=new_api_key.key_value[:10] + "...",
                trigger=trigger,
                timestamp=datetime.utcnow(),
                client_id=current_key.client_id,
                environment=current_key.environment,
                success=True
            )
            
            await self._store_rotation_event(rotation_event)
            
            await self._log_key_event("key_rotated", {
                "old_key_id": current_key.key_id,
                "new_key_id": new_api_key.key_id,
                "client_id": current_key.client_id,
                "trigger": trigger.value,
                "grace_period_hours": self.grace_period_hours
            })
            
            logger.info(f"Rotated API key {key_id} -> {new_key_id} for client {current_key.client_id}")
            
            return current_key, new_api_key
            
        except Exception as e:
            # Revert rotation status on failure
            current_key.status = KeyStatus.ACTIVE
            await self._store_api_key(current_key)
            
            # Log failed rotation
            rotation_event = RotationEvent(
                event_id=secrets.token_hex(8),
                key_id=current_key.key_id,
                old_key=current_key.key_value[:10] + "...",
                new_key="",
                trigger=trigger,
                timestamp=datetime.utcnow(),
                client_id=current_key.client_id,
                environment=current_key.environment,
                success=False,
                error_message=str(e)
            )
            
            await self._store_rotation_event(rotation_event)
            
            logger.error(f"Failed to rotate API key {key_id}: {e}")
            raise
    
    async def validate_api_key(self, key_value: str) -> Optional[APIKey]:
        """API key को validate करता है"""
        
        # Search for key by value (this is expensive, but necessary)
        all_keys = await self._get_all_active_keys()
        
        for api_key in all_keys:
            if api_key.key_value == key_value:
                # Check if key is valid
                if not await self._is_key_valid(api_key):
                    return None
                
                # Update usage statistics
                await self._update_key_usage(api_key.key_id)
                
                # Check if rotation is needed
                await self._check_rotation_needed(api_key)
                
                return api_key
        
        return None
    
    async def revoke_api_key(self, key_id: str, reason: str = "Manual revocation") -> bool:
        """API key को immediately revoke करता है"""
        
        api_key = await self._get_api_key(key_id)
        if not api_key:
            return False
        
        # Mark as revoked
        api_key.status = KeyStatus.REVOKED
        await self._store_api_key(api_key)
        
        # Log revocation
        await self._log_key_event("key_revoked", {
            "key_id": key_id,
            "client_id": api_key.client_id,
            "reason": reason
        })
        
        logger.warning(f"Revoked API key {key_id} - Reason: {reason}")
        return True
    
    async def get_client_keys(self, client_id: str, environment: str = None) -> List[APIKey]:
        """Client के सभी keys return करता है"""
        
        pattern = f"api_key:{client_id}:*"
        if environment:
            pattern = f"api_key:{client_id}:{environment}:*"
        
        keys = []
        for key_name in self.redis.scan_iter(match=pattern):
            key_data = self.redis.get(key_name)
            if key_data:
                try:
                    decrypted_data = self.fernet.decrypt(key_data.encode()).decode()
                    api_key_dict = json.loads(decrypted_data)
                    api_key = APIKey(**api_key_dict)
                    keys.append(api_key)
                except:
                    continue
        
        return sorted(keys, key=lambda k: k.created_at, reverse=True)
    
    async def emergency_rotation(self, client_id: str, environment: str = None) -> List[Tuple[APIKey, APIKey]]:
        """Emergency में सभी keys को rotate करता है"""
        
        logger.warning(f"Emergency rotation triggered for client {client_id}")
        
        client_keys = await self.get_client_keys(client_id, environment)
        active_keys = [k for k in client_keys if k.status == KeyStatus.ACTIVE]
        
        rotated_pairs = []
        
        for api_key in active_keys:
            try:
                old_key, new_key = await self.rotate_api_key(
                    api_key.key_id, 
                    RotationTrigger.SECURITY_INCIDENT
                )
                rotated_pairs.append((old_key, new_key))
            except Exception as e:
                logger.error(f"Failed to emergency rotate key {api_key.key_id}: {e}")
        
        await self._log_key_event("emergency_rotation", {
            "client_id": client_id,
            "environment": environment,
            "keys_rotated": len(rotated_pairs)
        })
        
        return rotated_pairs
    
    async def _store_api_key(self, api_key: APIKey):
        """API key को encrypted format में store करता है"""
        
        # Convert to dict and encrypt
        key_dict = asdict(api_key)
        key_dict["created_at"] = key_dict["created_at"].isoformat()
        if key_dict["expires_at"]:
            key_dict["expires_at"] = key_dict["expires_at"].isoformat()
        if key_dict["last_used"]:
            key_dict["last_used"] = key_dict["last_used"].isoformat()
        
        key_json = json.dumps(key_dict)
        encrypted_data = self.fernet.encrypt(key_json.encode()).decode()
        
        # Store with structured key
        redis_key = f"api_key:{api_key.client_id}:{api_key.environment}:{api_key.key_id}"
        self.redis.set(redis_key, encrypted_data)
        
        # Add to active keys index for faster lookup
        if api_key.status == KeyStatus.ACTIVE:
            self.redis.sadd("active_api_keys", redis_key)
        else:
            self.redis.srem("active_api_keys", redis_key)
    
    async def _get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Key ID से API key retrieve करता है"""
        
        # Search in all client/environment combinations
        for key_name in self.redis.scan_iter(match=f"api_key:*:*:{key_id}"):
            key_data = self.redis.get(key_name)
            if key_data:
                try:
                    decrypted_data = self.fernet.decrypt(key_data.encode()).decode()
                    key_dict = json.loads(decrypted_data)
                    
                    # Convert datetime strings back to datetime objects
                    key_dict["created_at"] = datetime.fromisoformat(key_dict["created_at"])
                    if key_dict["expires_at"]:
                        key_dict["expires_at"] = datetime.fromisoformat(key_dict["expires_at"])
                    if key_dict["last_used"]:
                        key_dict["last_used"] = datetime.fromisoformat(key_dict["last_used"])
                    
                    return APIKey(**key_dict)
                except:
                    continue
        
        return None
    
    async def _get_all_active_keys(self) -> List[APIKey]:
        """सभी active keys return करता है"""
        
        active_keys = []
        key_names = self.redis.smembers("active_api_keys")
        
        for key_name in key_names:
            key_data = self.redis.get(key_name)
            if key_data:
                try:
                    decrypted_data = self.fernet.decrypt(key_data.encode()).decode()
                    key_dict = json.loads(decrypted_data)
                    
                    # Convert datetime strings
                    key_dict["created_at"] = datetime.fromisoformat(key_dict["created_at"])
                    if key_dict["expires_at"]:
                        key_dict["expires_at"] = datetime.fromisoformat(key_dict["expires_at"])
                    if key_dict["last_used"]:
                        key_dict["last_used"] = datetime.fromisoformat(key_dict["last_used"])
                    
                    active_keys.append(APIKey(**key_dict))
                except:
                    # Remove invalid key from index
                    self.redis.srem("active_api_keys", key_name)
                    continue
        
        return active_keys
    
    async def _is_key_valid(self, api_key: APIKey) -> bool:
        """Key valid है या नहीं check करता है"""
        
        # Check status
        if api_key.status not in [KeyStatus.ACTIVE, KeyStatus.ROTATING]:
            return False
        
        # Check expiration
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            # Mark as expired
            api_key.status = KeyStatus.EXPIRED
            await self._store_api_key(api_key)
            return False
        
        return True
    
    async def _update_key_usage(self, key_id: str):
        """Key usage statistics update करता है"""
        
        api_key = await self._get_api_key(key_id)
        if api_key:
            api_key.usage_count += 1
            api_key.last_used = datetime.utcnow()
            await self._store_api_key(api_key)
    
    async def _check_rotation_needed(self, api_key: APIKey):
        """Check करता है कि rotation की जरूरत है या नहीं"""
        
        policy = self.rotation_policies.get(api_key.environment, self.rotation_policies["prod"])
        
        if not policy["auto_rotate"]:
            return
        
        # Check age-based rotation
        age_days = (datetime.utcnow() - api_key.created_at).days
        if age_days >= policy["rotation_interval_days"]:
            await self.rotate_api_key(api_key.key_id, RotationTrigger.SCHEDULED)
            return
        
        # Check usage-based rotation
        if api_key.usage_count >= policy["max_usage_count"]:
            await self.rotate_api_key(api_key.key_id, RotationTrigger.USAGE_THRESHOLD)
            return
    
    async def _schedule_key_deprecation(self, key_id: str, hours: int):
        """Key deprecation को schedule करता है"""
        
        deprecation_time = datetime.utcnow() + timedelta(hours=hours)
        
        # Store deprecation schedule
        schedule_data = {
            "key_id": key_id,
            "deprecation_time": deprecation_time.isoformat(),
            "scheduled_at": datetime.utcnow().isoformat()
        }
        
        self.redis.setex(
            f"key_deprecation_schedule:{key_id}",
            int(timedelta(hours=hours).total_seconds()),
            json.dumps(schedule_data)
        )
    
    async def _store_rotation_event(self, event: RotationEvent):
        """Rotation event को store करता है audit के लिए"""
        
        event_dict = asdict(event)
        event_dict["timestamp"] = event_dict["timestamp"].isoformat()
        
        # Store in rotation history
        self.redis.lpush(
            f"rotation_history:{event.client_id}",
            json.dumps(event_dict)
        )
        
        # Keep only last 100 events
        self.redis.ltrim(f"rotation_history:{event.client_id}", 0, 99)
    
    async def _log_key_event(self, event_type: str, details: Dict[str, Any]):
        """Key events को log करता है"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "service": "api_key_rotation"
        }
        
        logger.info(f"API Key Event: {json.dumps(log_entry)}")
        
        # Store in Redis for monitoring
        self.redis.lpush("api_key_events", json.dumps(log_entry))
        self.redis.ltrim("api_key_events", 0, 999)  # Keep last 1000 events
    
    def _start_rotation_scheduler(self):
        """Background rotation scheduler start करता है"""
        
        def run_scheduler():
            schedule.every(1).hours.do(self._cleanup_expired_keys)
            schedule.every(6).hours.do(self._process_scheduled_deprecations)
            schedule.every(1).days.do(self._check_all_keys_for_rotation)
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Started API key rotation scheduler")
    
    def _cleanup_expired_keys(self):
        """Expired keys को cleanup करता है"""
        asyncio.create_task(self._async_cleanup_expired_keys())
    
    async def _async_cleanup_expired_keys(self):
        """Async cleanup for expired keys"""
        
        all_keys = await self._get_all_active_keys()
        
        for api_key in all_keys:
            if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
                api_key.status = KeyStatus.EXPIRED
                await self._store_api_key(api_key)
                
                await self._log_key_event("key_expired", {
                    "key_id": api_key.key_id,
                    "client_id": api_key.client_id,
                    "expired_at": api_key.expires_at.isoformat()
                })
    
    def _process_scheduled_deprecations(self):
        """Scheduled deprecations को process करता है"""
        asyncio.create_task(self._async_process_scheduled_deprecations())
    
    async def _async_process_scheduled_deprecations(self):
        """Async processing of scheduled deprecations"""
        
        # Get all deprecation schedules
        for key_name in self.redis.scan_iter(match="key_deprecation_schedule:*"):
            schedule_data = self.redis.get(key_name)
            if schedule_data:
                try:
                    schedule_info = json.loads(schedule_data)
                    deprecation_time = datetime.fromisoformat(schedule_info["deprecation_time"])
                    
                    if datetime.utcnow() >= deprecation_time:
                        key_id = schedule_info["key_id"]
                        
                        # Deprecate the key
                        api_key = await self._get_api_key(key_id)
                        if api_key and api_key.status == KeyStatus.ROTATING:
                            api_key.status = KeyStatus.DEPRECATED
                            await self._store_api_key(api_key)
                            
                            await self._log_key_event("key_deprecated", {
                                "key_id": key_id,
                                "client_id": api_key.client_id,
                                "deprecated_at": datetime.utcnow().isoformat()
                            })
                        
                        # Remove schedule
                        self.redis.delete(key_name)
                        
                except:
                    continue
    
    def _check_all_keys_for_rotation(self):
        """सभी keys को rotation के लिए check करता है"""
        asyncio.create_task(self._async_check_all_keys_for_rotation())
    
    async def _async_check_all_keys_for_rotation(self):
        """Async check for all keys rotation"""
        
        all_keys = await self._get_all_active_keys()
        
        for api_key in all_keys:
            try:
                await self._check_rotation_needed(api_key)
            except Exception as e:
                logger.error(f"Error checking rotation for key {api_key.key_id}: {e}")

# FastAPI integration for API key management
app = FastAPI(title="API Key Rotation Management")

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Key rotation manager
key_manager = APIKeyRotationManager(redis_client)

# Security dependency
security = HTTPBearer()

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Admin token verify करता है"""
    # Simplified admin verification
    if credentials.credentials != "admin_token_for_demo":
        raise HTTPException(status_code=403, detail="Invalid admin token")
    return credentials.credentials

@app.post("/api-keys/create")
async def create_api_key(
    client_id: str,
    environment: str,
    permissions: List[str],
    expires_in_days: Optional[int] = None,
    admin_token: str = Depends(verify_admin_token)
):
    """New API key create करता है"""
    
    api_key = await key_manager.create_api_key(
        client_id=client_id,
        environment=environment,
        permissions=permissions,
        expires_in_days=expires_in_days
    )
    
    return {
        "key_id": api_key.key_id,
        "key_value": api_key.key_value,  # Only return once!
        "client_id": api_key.client_id,
        "environment": api_key.environment,
        "permissions": api_key.permissions,
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None
    }

@app.post("/api-keys/{key_id}/rotate")
async def rotate_api_key(
    key_id: str,
    admin_token: str = Depends(verify_admin_token)
):
    """API key को rotate करता है"""
    
    old_key, new_key = await key_manager.rotate_api_key(key_id, RotationTrigger.MANUAL)
    
    return {
        "message": "Key rotated successfully",
        "old_key_id": old_key.key_id,
        "new_key_id": new_key.key_id,
        "new_key_value": new_key.key_value,  # Return new key
        "grace_period_hours": key_manager.grace_period_hours
    }

@app.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    reason: str = "Manual revocation",
    admin_token: str = Depends(verify_admin_token)
):
    """API key को revoke करता है"""
    
    success = await key_manager.revoke_api_key(key_id, reason)
    
    if success:
        return {"message": "Key revoked successfully"}
    else:
        raise HTTPException(status_code=404, detail="Key not found")

@app.get("/api-keys/client/{client_id}")
async def get_client_keys(
    client_id: str,
    environment: Optional[str] = None,
    admin_token: str = Depends(verify_admin_token)
):
    """Client के सभी keys return करता है"""
    
    keys = await key_manager.get_client_keys(client_id, environment)
    
    # Don't return key values in list
    return [
        {
            "key_id": key.key_id,
            "environment": key.environment,
            "permissions": key.permissions,
            "status": key.status.value,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "usage_count": key.usage_count,
            "last_used": key.last_used.isoformat() if key.last_used else None,
            "rotation_count": key.rotation_count
        }
        for key in keys
    ]

@app.post("/api-keys/emergency-rotation/{client_id}")
async def emergency_rotation(
    client_id: str,
    environment: Optional[str] = None,
    admin_token: str = Depends(verify_admin_token)
):
    """Emergency rotation trigger करता है"""
    
    rotated_pairs = await key_manager.emergency_rotation(client_id, environment)
    
    return {
        "message": "Emergency rotation completed",
        "rotated_keys": len(rotated_pairs),
        "new_keys": [
            {
                "old_key_id": old.key_id,
                "new_key_id": new.key_id,
                "new_key_value": new.key_value
            }
            for old, new in rotated_pairs
        ]
    }

@app.get("/validate")
async def validate_api_key_endpoint(api_key: str):
    """API key validation endpoint"""
    
    validated_key = await key_manager.validate_api_key(api_key)
    
    if validated_key:
        return {
            "valid": True,
            "key_id": validated_key.key_id,
            "client_id": validated_key.client_id,
            "environment": validated_key.environment,
            "permissions": validated_key.permissions,
            "usage_count": validated_key.usage_count
        }
    else:
        return {"valid": False}

if __name__ == "__main__":
    import uvicorn
    
    print("🔑 API Key Rotation System")
    print("🔄 Automatic key rotation enabled")
    print("🛡️ Zero-downtime key updates")
    print("📊 Complete audit trail")
    print("⚡ AWS/Azure level key management")
    
    uvicorn.run(app, host="0.0.0.0", port=8004)

"""
Production Deployment Notes:
============================

1. Security Best Practices:
   - Use HSM for encryption key storage
   - Implement proper admin authentication
   - Log all key operations to SIEM
   - Regular security audits

2. High Availability:
   - Redis cluster for key storage
   - Multiple rotation service instances
   - Database replication
   - Monitoring और alerting

3. Integration:
   - API Gateway integration
   - CI/CD pipeline notifications
   - Slack/Teams notifications for rotations
   - Metrics और dashboards

4. Compliance:
   - SOC 2 Type II compliance
   - GDPR data retention policies
   - Industry-specific requirements
   - Regular penetration testing

यह system AWS API Gateway या Azure API Management level की key rotation provide करता है!
"""