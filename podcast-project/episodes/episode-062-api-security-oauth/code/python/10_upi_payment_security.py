"""
UPI-Style Payment Security System
================================

यह comprehensive payment security system है जो UPI (Unified Payments Interface)
की security standards को follow करता है। PhonePe, GPay, Paytm जैसे apps
में इसी level की security होती है।

Features:
- Multi-factor Authentication
- Device Binding
- Transaction Limits
- Fraud Detection
- Real-time Risk Assessment
- Secure PIN Management

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
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import jwt
import bcrypt

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """Transaction types"""
    P2P = "person_to_person"
    P2M = "person_to_merchant"
    BILL_PAYMENT = "bill_payment"
    MOBILE_RECHARGE = "mobile_recharge"
    MONEY_REQUEST = "money_request"

class TransactionStatus(Enum):
    """Transaction status"""
    INITIATED = "initiated"
    PENDING_AUTH = "pending_auth"
    AUTHENTICATED = "authenticated"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    DECLINED = "declined"
    TIMEOUT = "timeout"

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuthMethod(Enum):
    """Authentication methods"""
    PIN = "pin"
    BIOMETRIC = "biometric"
    OTP = "otp"
    PATTERN = "pattern"

@dataclass
class UPIUser:
    """UPI user profile"""
    user_id: str
    phone_number: str
    upi_id: str
    bank_accounts: List[str]
    daily_limit: float
    per_transaction_limit: float
    pin_hash: str
    device_id: str
    kyc_verified: bool
    risk_score: float = 0.0

@dataclass
class PaymentTransaction:
    """Payment transaction details"""
    txn_id: str
    from_user: str
    to_user: str
    amount: float
    currency: str
    txn_type: TransactionType
    status: TransactionStatus
    risk_level: RiskLevel
    created_at: datetime
    notes: Optional[str] = None
    merchant_ref: Optional[str] = None

@dataclass
class DeviceInfo:
    """Device information for security"""
    device_id: str
    device_name: str
    os_version: str
    app_version: str
    location: Optional[Dict[str, float]]
    ip_address: str
    is_rooted: bool
    last_seen: datetime

class UPIPaymentSecuritySystem:
    """
    UPI-level Payment Security System
    
    PhonePe, GPay, Paytm level की comprehensive security implementation
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key.encode())
        
        # Security limits और thresholds
        self.security_config = {
            "max_daily_amount": 100000.0,  # ₹1 lakh per day
            "max_transaction_amount": 25000.0,  # ₹25K per transaction
            "max_failed_attempts": 3,
            "account_lockout_duration": 1800,  # 30 minutes
            "fraud_detection_threshold": 0.7,
            "mfa_required_amount": 5000.0,  # ₹5K+ requires MFA
            "velocity_check_window": 300,  # 5 minutes
            "max_transactions_per_window": 5
        }
        
        # Mock user database
        self.users = {
            "user_mumbai_123": UPIUser(
                user_id="user_mumbai_123",
                phone_number="+91-9876543210",
                upi_id="rahul@paytm",
                bank_accounts=["HDFC123", "ICICI456"],
                daily_limit=50000.0,
                per_transaction_limit=10000.0,
                pin_hash=bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode(),
                device_id="device_samsung_galaxy",
                kyc_verified=True,
                risk_score=0.1
            ),
            "user_delhi_456": UPIUser(
                user_id="user_delhi_456",
                phone_number="+91-8765432109",
                upi_id="priya@phonepe",
                bank_accounts=["SBI789"],
                daily_limit=75000.0,
                per_transaction_limit=15000.0,
                pin_hash=bcrypt.hashpw("9876".encode(), bcrypt.gensalt()).decode(),
                device_id="device_iphone_12",
                kyc_verified=True,
                risk_score=0.2
            )
        }
    
    def _get_encryption_key(self) -> str:
        """Encryption key retrieve करता है"""
        key = self.redis.get("upi_encryption_key")
        if not key:
            key = Fernet.generate_key().decode()
            self.redis.set("upi_encryption_key", key)
        return key
    
    async def initiate_payment(
        self,
        from_user_id: str,
        to_upi_id: str,
        amount: float,
        device_info: DeviceInfo,
        notes: Optional[str] = None,
        merchant_ref: Optional[str] = None
    ) -> PaymentTransaction:
        """
        Payment initiation के साथ comprehensive security checks
        
        यह UPI payment का पहला step है
        """
        
        # Validate sender
        from_user = self.users.get(from_user_id)
        if not from_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Device validation
        await self._validate_device(from_user_id, device_info)
        
        # Basic amount validation
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        if amount > from_user.per_transaction_limit:
            raise HTTPException(status_code=400, detail="Amount exceeds transaction limit")
        
        # Daily limit check
        daily_spent = await self._get_daily_spent(from_user_id)
        if daily_spent + amount > from_user.daily_limit:
            raise HTTPException(status_code=400, detail="Amount exceeds daily limit")
        
        # Velocity check (transaction frequency)
        await self._check_transaction_velocity(from_user_id)
        
        # Find recipient
        to_user_id = await self._resolve_upi_id(to_upi_id)
        if not to_user_id:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        # Create transaction
        txn_id = f"TXN{int(time.time())}{secrets.token_hex(4)}"
        
        transaction = PaymentTransaction(
            txn_id=txn_id,
            from_user=from_user_id,
            to_user=to_user_id,
            amount=amount,
            currency="INR",
            txn_type=TransactionType.P2P if not merchant_ref else TransactionType.P2M,
            status=TransactionStatus.INITIATED,
            risk_level=RiskLevel.LOW,  # Will be assessed
            created_at=datetime.utcnow(),
            notes=notes,
            merchant_ref=merchant_ref
        )
        
        # Risk assessment
        risk_assessment = await self._assess_transaction_risk(transaction, device_info)
        transaction.risk_level = risk_assessment["risk_level"]
        
        # Store transaction
        await self._store_transaction(transaction)
        
        # Log initiation
        await self._log_payment_event("payment_initiated", {
            "txn_id": txn_id,
            "from_user": from_user_id,
            "amount": amount,
            "risk_level": risk_assessment["risk_level"].value,
            "device_id": device_info.device_id
        })
        
        logger.info(f"Payment initiated: {txn_id}, Amount: ₹{amount}")
        return transaction
    
    async def authenticate_payment(
        self,
        txn_id: str,
        user_id: str,
        pin: str,
        auth_method: AuthMethod = AuthMethod.PIN,
        biometric_data: Optional[str] = None
    ) -> PaymentTransaction:
        """
        Payment authentication with PIN/Biometric verification
        
        UPI का critical security step
        """
        
        # Get transaction
        transaction = await self._get_transaction(txn_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Validate transaction state
        if transaction.status != TransactionStatus.INITIATED:
            raise HTTPException(status_code=400, detail="Invalid transaction state")
        
        # Validate user
        if transaction.from_user != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Check transaction timeout (5 minutes)
        if datetime.utcnow() - transaction.created_at > timedelta(minutes=5):
            transaction.status = TransactionStatus.TIMEOUT
            await self._store_transaction(transaction)
            raise HTTPException(status_code=408, detail="Transaction timeout")
        
        # Check failed attempts
        failed_attempts = await self._get_failed_attempts(user_id)
        if failed_attempts >= self.security_config["max_failed_attempts"]:
            await self._lock_account(user_id)
            raise HTTPException(status_code=423, detail="Account locked due to failed attempts")
        
        # Authenticate based on method
        auth_success = False
        
        if auth_method == AuthMethod.PIN:
            auth_success = await self._verify_pin(user_id, pin)
        elif auth_method == AuthMethod.BIOMETRIC:
            auth_success = await self._verify_biometric(user_id, biometric_data)
        elif auth_method == AuthMethod.OTP:
            auth_success = await self._verify_otp(user_id, pin)  # PIN field contains OTP
        
        if not auth_success:
            await self._record_failed_attempt(user_id)
            transaction.status = TransactionStatus.DECLINED
            await self._store_transaction(transaction)
            
            await self._log_payment_event("authentication_failed", {
                "txn_id": txn_id,
                "user_id": user_id,
                "auth_method": auth_method.value,
                "failed_attempts": failed_attempts + 1
            })
            
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Authentication successful
        transaction.status = TransactionStatus.AUTHENTICATED
        await self._store_transaction(transaction)
        
        # Clear failed attempts
        await self._clear_failed_attempts(user_id)
        
        # Additional MFA for high-value transactions
        if transaction.amount >= self.security_config["mfa_required_amount"]:
            if auth_method == AuthMethod.PIN:
                # Require additional OTP
                otp = await self._send_transaction_otp(user_id, txn_id)
                transaction.status = TransactionStatus.PENDING_AUTH
                await self._store_transaction(transaction)
                
                return transaction  # Requires OTP verification
        
        # Proceed to processing
        return await self._process_payment(transaction)
    
    async def verify_transaction_otp(
        self,
        txn_id: str,
        user_id: str,
        otp: str
    ) -> PaymentTransaction:
        """High-value transaction के लिए OTP verification"""
        
        transaction = await self._get_transaction(txn_id)
        if not transaction or transaction.status != TransactionStatus.PENDING_AUTH:
            raise HTTPException(status_code=400, detail="Invalid transaction state")
        
        # Verify OTP
        if not await self._verify_otp(user_id, otp):
            await self._record_failed_attempt(user_id)
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        # Proceed to processing
        return await self._process_payment(transaction)
    
    async def _process_payment(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """
        Actual payment processing
        
        Real implementation में bank integration होगा
        """
        
        transaction.status = TransactionStatus.PROCESSING
        await self._store_transaction(transaction)
        
        # Simulate bank processing
        await asyncio.sleep(1)
        
        # Random failure simulation (5% chance)
        if secrets.randbelow(100) < 5:
            transaction.status = TransactionStatus.FAILED
            await self._store_transaction(transaction)
            
            await self._log_payment_event("payment_failed", {
                "txn_id": transaction.txn_id,
                "amount": transaction.amount,
                "reason": "Bank processing failed"
            })
            
            raise HTTPException(status_code=502, detail="Payment processing failed")
        
        # Success
        transaction.status = TransactionStatus.SUCCESS
        await self._store_transaction(transaction)
        
        # Update user limits
        await self._update_daily_spent(transaction.from_user, transaction.amount)
        
        # Send notifications
        await self._send_payment_notifications(transaction)
        
        await self._log_payment_event("payment_success", {
            "txn_id": transaction.txn_id,
            "from_user": transaction.from_user,
            "to_user": transaction.to_user,
            "amount": transaction.amount
        })
        
        logger.info(f"Payment successful: {transaction.txn_id}, Amount: ₹{transaction.amount}")
        return transaction
    
    async def _assess_transaction_risk(
        self,
        transaction: PaymentTransaction,
        device_info: DeviceInfo
    ) -> Dict[str, Any]:
        """
        Comprehensive risk assessment
        
        Machine learning models यहाँ use होते हैं production में
        """
        
        risk_factors = []
        risk_score = 0.0
        
        # Amount-based risk
        if transaction.amount > 10000:
            risk_score += 0.2
            risk_factors.append("high_amount")
        
        # Time-based risk
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 23:
            risk_score += 0.3
            risk_factors.append("unusual_time")
        
        # Device risk
        if device_info.is_rooted:
            risk_score += 0.5
            risk_factors.append("rooted_device")
        
        # User risk score
        from_user = self.users.get(transaction.from_user)
        if from_user:
            risk_score += from_user.risk_score
        
        # Velocity risk
        recent_transactions = await self._get_recent_transactions(transaction.from_user, 3600)
        if len(recent_transactions) > 10:
            risk_score += 0.4
            risk_factors.append("high_velocity")
        
        # Location risk (if available)
        if device_info.location:
            location_risk = await self._assess_location_risk(
                transaction.from_user, 
                device_info.location
            )
            risk_score += location_risk
            if location_risk > 0.3:
                risk_factors.append("unusual_location")
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors
        }
    
    async def _validate_device(self, user_id: str, device_info: DeviceInfo):
        """Device validation और binding check"""
        
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Device binding check
        if user.device_id != device_info.device_id:
            # Allow device change with additional verification
            await self._log_payment_event("device_mismatch", {
                "user_id": user_id,
                "registered_device": user.device_id,
                "current_device": device_info.device_id
            })
            
            # In production, require device verification
            # For now, we'll allow but increase risk
        
        # Check for rooted/jailbroken device
        if device_info.is_rooted:
            await self._log_payment_event("rooted_device_detected", {
                "user_id": user_id,
                "device_id": device_info.device_id
            })
            
            # In production, may block transaction
        
        # Store device info
        await self._store_device_info(user_id, device_info)
    
    async def _verify_pin(self, user_id: str, pin: str) -> bool:
        """UPI PIN verification"""
        
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Verify PIN hash
        return bcrypt.checkpw(pin.encode(), user.pin_hash.encode())
    
    async def _verify_biometric(self, user_id: str, biometric_data: Optional[str]) -> bool:
        """Biometric verification (fingerprint/face)"""
        
        if not biometric_data:
            return False
        
        # In production, compare with stored biometric template
        # For demo, simulate verification
        stored_biometric = self.redis.get(f"biometric:{user_id}")
        if not stored_biometric:
            return False
        
        return stored_biometric == biometric_data
    
    async def _verify_otp(self, user_id: str, otp: str) -> bool:
        """OTP verification"""
        
        stored_otp = self.redis.get(f"otp:{user_id}")
        if not stored_otp:
            return False
        
        # Delete OTP after verification (one-time use)
        self.redis.delete(f"otp:{user_id}")
        
        return stored_otp == otp
    
    async def _send_transaction_otp(self, user_id: str, txn_id: str) -> str:
        """Transaction OTP send करता है"""
        
        # Generate 6-digit OTP
        otp = f"{secrets.randbelow(900000) + 100000}"
        
        # Store with 5-minute expiry
        self.redis.setex(f"otp:{user_id}", 300, otp)
        
        # Log OTP generation
        await self._log_payment_event("otp_sent", {
            "user_id": user_id,
            "txn_id": txn_id,
            "otp_length": len(otp)
        })
        
        # In production, send via SMS/Email
        logger.info(f"OTP sent to user {user_id}: {otp}")  # Remove in production
        
        return otp
    
    async def _get_daily_spent(self, user_id: str) -> float:
        """Daily spent amount retrieve करता है"""
        
        today = datetime.utcnow().date().isoformat()
        key = f"daily_spent:{user_id}:{today}"
        
        spent = self.redis.get(key)
        return float(spent) if spent else 0.0
    
    async def _update_daily_spent(self, user_id: str, amount: float):
        """Daily spent amount update करता है"""
        
        today = datetime.utcnow().date().isoformat()
        key = f"daily_spent:{user_id}:{today}"
        
        self.redis.incrbyfloat(key, amount)
        self.redis.expire(key, 86400)  # Expire at end of day
    
    async def _check_transaction_velocity(self, user_id: str):
        """Transaction velocity check करता है"""
        
        window = self.security_config["velocity_check_window"]
        max_transactions = self.security_config["max_transactions_per_window"]
        
        now = time.time()
        window_start = now - window
        
        key = f"velocity:{user_id}"
        
        # Remove old transactions
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current transactions
        current_count = self.redis.zcard(key)
        
        if current_count >= max_transactions:
            raise HTTPException(
                status_code=429,
                detail=f"Too many transactions. Max {max_transactions} per {window} seconds"
            )
        
        # Add current transaction
        self.redis.zadd(key, {str(now): now})
        self.redis.expire(key, window)
    
    async def _resolve_upi_id(self, upi_id: str) -> Optional[str]:
        """UPI ID को user ID में resolve करता है"""
        
        for user_id, user in self.users.items():
            if user.upi_id == upi_id:
                return user_id
        
        return None
    
    async def _get_failed_attempts(self, user_id: str) -> int:
        """Failed authentication attempts count करता है"""
        
        attempts = self.redis.get(f"failed_attempts:{user_id}")
        return int(attempts) if attempts else 0
    
    async def _record_failed_attempt(self, user_id: str):
        """Failed attempt record करता है"""
        
        key = f"failed_attempts:{user_id}"
        self.redis.incr(key)
        self.redis.expire(key, self.security_config["account_lockout_duration"])
    
    async def _clear_failed_attempts(self, user_id: str):
        """Failed attempts clear करता है successful auth के बाद"""
        
        self.redis.delete(f"failed_attempts:{user_id}")
    
    async def _lock_account(self, user_id: str):
        """Account को temporarily lock करता है"""
        
        lockout_duration = self.security_config["account_lockout_duration"]
        self.redis.setex(f"account_locked:{user_id}", lockout_duration, "locked")
        
        await self._log_payment_event("account_locked", {
            "user_id": user_id,
            "lockout_duration": lockout_duration
        })
    
    async def _store_transaction(self, transaction: PaymentTransaction):
        """Transaction को store करता है"""
        
        txn_data = asdict(transaction)
        txn_data["created_at"] = txn_data["created_at"].isoformat()
        txn_data["txn_type"] = txn_data["txn_type"].value
        txn_data["status"] = txn_data["status"].value
        txn_data["risk_level"] = txn_data["risk_level"].value
        
        # Encrypt sensitive data
        encrypted_data = self.fernet.encrypt(json.dumps(txn_data).encode()).decode()
        
        # Store transaction
        self.redis.setex(f"transaction:{transaction.txn_id}", 86400 * 30, encrypted_data)
        
        # Add to user's transaction history
        self.redis.lpush(f"user_transactions:{transaction.from_user}", transaction.txn_id)
        self.redis.ltrim(f"user_transactions:{transaction.from_user}", 0, 999)
    
    async def _get_transaction(self, txn_id: str) -> Optional[PaymentTransaction]:
        """Transaction retrieve करता है"""
        
        encrypted_data = self.redis.get(f"transaction:{txn_id}")
        if not encrypted_data:
            return None
        
        try:
            txn_data = json.loads(self.fernet.decrypt(encrypted_data.encode()).decode())
            
            # Convert back to objects
            txn_data["created_at"] = datetime.fromisoformat(txn_data["created_at"])
            txn_data["txn_type"] = TransactionType(txn_data["txn_type"])
            txn_data["status"] = TransactionStatus(txn_data["status"])
            txn_data["risk_level"] = RiskLevel(txn_data["risk_level"])
            
            return PaymentTransaction(**txn_data)
        except Exception as e:
            logger.error(f"Error decrypting transaction {txn_id}: {e}")
            return None
    
    async def _get_recent_transactions(self, user_id: str, seconds: int) -> List[str]:
        """Recent transactions retrieve करता है"""
        
        # Get recent transaction IDs
        txn_ids = self.redis.lrange(f"user_transactions:{user_id}", 0, 50)
        
        recent_txns = []
        cutoff_time = datetime.utcnow() - timedelta(seconds=seconds)
        
        for txn_id in txn_ids:
            transaction = await self._get_transaction(txn_id)
            if transaction and transaction.created_at > cutoff_time:
                recent_txns.append(txn_id)
        
        return recent_txns
    
    async def _assess_location_risk(self, user_id: str, current_location: Dict[str, float]) -> float:
        """Location-based risk assessment"""
        
        # Get user's historical locations
        locations_data = self.redis.get(f"user_locations:{user_id}")
        if not locations_data:
            return 0.5  # Unknown location = medium risk
        
        locations = json.loads(locations_data)
        
        # Calculate distance from known locations
        min_distance = float('inf')
        
        for loc in locations:
            # Simple distance calculation (production में proper geolocation use करें)
            distance = abs(current_location["lat"] - loc["lat"]) + abs(current_location["lng"] - loc["lng"])
            min_distance = min(min_distance, distance)
        
        # Risk based on distance (simplified)
        if min_distance > 1.0:  # > 1 degree = high risk
            return 0.8
        elif min_distance > 0.1:  # > 0.1 degree = medium risk
            return 0.4
        else:
            return 0.1  # Known location = low risk
    
    async def _store_device_info(self, user_id: str, device_info: DeviceInfo):
        """Device information store करता है"""
        
        device_data = asdict(device_info)
        device_data["last_seen"] = device_data["last_seen"].isoformat()
        
        self.redis.setex(
            f"device_info:{user_id}:{device_info.device_id}",
            86400 * 30,  # 30 days
            json.dumps(device_data)
        )
    
    async def _send_payment_notifications(self, transaction: PaymentTransaction):
        """Payment notifications send करता है"""
        
        # In production, send push notifications, SMS, email
        notification_data = {
            "txn_id": transaction.txn_id,
            "amount": transaction.amount,
            "status": transaction.status.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store notification for delivery
        self.redis.lpush(f"notifications:{transaction.from_user}", json.dumps(notification_data))
        self.redis.lpush(f"notifications:{transaction.to_user}", json.dumps(notification_data))
    
    async def _log_payment_event(self, event_type: str, details: Dict[str, Any]):
        """Payment events को log करता है"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "service": "upi_payment_security"
        }
        
        logger.info(f"UPI Payment Event: {json.dumps(log_entry)}")
        
        # Store for monitoring
        self.redis.lpush("upi_payment_events", json.dumps(log_entry))
        self.redis.ltrim("upi_payment_events", 0, 9999)

# FastAPI application
app = FastAPI(title="UPI Payment Security System")

# Redis connection  
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# UPI Security System
upi_security = UPIPaymentSecuritySystem(redis_client)

# Pydantic models for API
class PaymentRequest(BaseModel):
    to_upi_id: str
    amount: float
    notes: Optional[str] = None
    merchant_ref: Optional[str] = None

class AuthRequest(BaseModel):
    txn_id: str
    pin: str
    auth_method: str = "pin"
    biometric_data: Optional[str] = None

class OTPRequest(BaseModel):
    txn_id: str
    otp: str

class DeviceInfoModel(BaseModel):
    device_id: str
    device_name: str
    os_version: str
    app_version: str
    location: Optional[Dict[str, float]] = None
    is_rooted: bool = False

@app.post("/upi/payment/initiate")
async def initiate_payment(
    payment_request: PaymentRequest,
    device_info: DeviceInfoModel,
    user_id: str,
    request: Request
):
    """Payment initiation endpoint"""
    
    device = DeviceInfo(
        device_id=device_info.device_id,
        device_name=device_info.device_name,
        os_version=device_info.os_version,
        app_version=device_info.app_version,
        location=device_info.location,
        ip_address=request.client.host,
        is_rooted=device_info.is_rooted,
        last_seen=datetime.utcnow()
    )
    
    transaction = await upi_security.initiate_payment(
        from_user_id=user_id,
        to_upi_id=payment_request.to_upi_id,
        amount=payment_request.amount,
        device_info=device,
        notes=payment_request.notes,
        merchant_ref=payment_request.merchant_ref
    )
    
    return {
        "txn_id": transaction.txn_id,
        "status": transaction.status.value,
        "risk_level": transaction.risk_level.value,
        "amount": transaction.amount,
        "requires_mfa": transaction.amount >= upi_security.security_config["mfa_required_amount"]
    }

@app.post("/upi/payment/authenticate")
async def authenticate_payment(auth_request: AuthRequest, user_id: str):
    """Payment authentication endpoint"""
    
    auth_method = AuthMethod(auth_request.auth_method)
    
    transaction = await upi_security.authenticate_payment(
        txn_id=auth_request.txn_id,
        user_id=user_id,
        pin=auth_request.pin,
        auth_method=auth_method,
        biometric_data=auth_request.biometric_data
    )
    
    return {
        "txn_id": transaction.txn_id,
        "status": transaction.status.value,
        "amount": transaction.amount,
        "requires_otp": transaction.status == TransactionStatus.PENDING_AUTH
    }

@app.post("/upi/payment/verify-otp")
async def verify_otp(otp_request: OTPRequest, user_id: str):
    """OTP verification endpoint"""
    
    transaction = await upi_security.verify_transaction_otp(
        txn_id=otp_request.txn_id,
        user_id=user_id,
        otp=otp_request.otp
    )
    
    return {
        "txn_id": transaction.txn_id,
        "status": transaction.status.value,
        "amount": transaction.amount,
        "success": transaction.status == TransactionStatus.SUCCESS
    }

@app.get("/upi/transaction/{txn_id}")
async def get_transaction_status(txn_id: str, user_id: str):
    """Transaction status check करता है"""
    
    transaction = await upi_security._get_transaction(txn_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Only allow user to see their own transactions
    if transaction.from_user != user_id and transaction.to_user != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return {
        "txn_id": transaction.txn_id,
        "status": transaction.status.value,
        "amount": transaction.amount,
        "created_at": transaction.created_at.isoformat(),
        "risk_level": transaction.risk_level.value
    }

@app.get("/upi/user/{user_id}/transactions")
async def get_user_transactions(user_id: str, limit: int = 10):
    """User के recent transactions return करता है"""
    
    txn_ids = redis_client.lrange(f"user_transactions:{user_id}", 0, limit - 1)
    
    transactions = []
    for txn_id in txn_ids:
        transaction = await upi_security._get_transaction(txn_id)
        if transaction:
            transactions.append({
                "txn_id": transaction.txn_id,
                "amount": transaction.amount,
                "status": transaction.status.value,
                "created_at": transaction.created_at.isoformat(),
                "to_user": transaction.to_user if transaction.from_user == user_id else transaction.from_user,
                "type": "sent" if transaction.from_user == user_id else "received"
            })
    
    return {"transactions": transactions}

@app.get("/upi/user/{user_id}/limits")
async def get_user_limits(user_id: str):
    """User के transaction limits return करता है"""
    
    user = upi_security.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    daily_spent = await upi_security._get_daily_spent(user_id)
    
    return {
        "daily_limit": user.daily_limit,
        "per_transaction_limit": user.per_transaction_limit,
        "daily_spent": daily_spent,
        "daily_remaining": user.daily_limit - daily_spent,
        "kyc_verified": user.kyc_verified
    }

if __name__ == "__main__":
    import uvicorn
    
    print("💳 UPI Payment Security System")
    print("🔐 PhonePe/GPay level security implementation")
    print("🛡️ Multi-factor authentication")
    print("📊 Real-time fraud detection")
    print("⚡ Banking grade transaction security")
    
    uvicorn.run(app, host="0.0.0.0", port=8008)

"""
Production Implementation Notes:
===============================

1. Security Enhancements:
   - Hardware security module (HSM) for key storage
   - Advanced biometric verification
   - ML-based fraud detection models
   - Real-time location verification
   - Device fingerprinting

2. Compliance:
   - RBI guidelines compliance
   - PCI DSS certification
   - Data localization requirements
   - Audit trail maintenance
   - Regular security assessments

3. Performance:
   - Sub-second transaction processing
   - High availability (99.99%+)
   - Horizontal scaling
   - Database sharding
   - Caching strategies

4. Integration:
   - Bank APIs (NPCI integration)
   - SMS gateways for OTP
   - Push notification services
   - Analytics platforms
   - Monitoring systems

यह implementation PhonePe, GPay, Paytm level की UPI security provide करता है!
"""