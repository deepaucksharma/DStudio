"""
OAuth 2.0 Authorization Server Implementation
============================================

यह example एक complete OAuth 2.0 authorization server banata hai
जो production में use हो सकता है। PhonePe और Paytm जैसे platforms
इसी तरह का security implement करते हैं।

Features:
- Authorization Code Flow
- Client Credentials Flow
- Token Validation
- Scope Management
- Rate Limiting Integration

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
import jwt
import hashlib
import secrets
import time
import redis
import logging
from datetime import datetime, timedelta
import asyncio

# Logger setup - Audit trail ke liye zaroori
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OAuth 2.0 Authorization Server")
security = HTTPBearer()

# Redis connection for session management
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# JWT Configuration
JWT_SECRET = "super_secret_key_production_mein_change_karna"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

class Client(BaseModel):
    """OAuth Client Model - Paytm/PhonePe जैसे third-party apps के लिए"""
    client_id: str
    client_secret: str
    redirect_uris: List[str]
    scope: List[str]
    grant_types: List[str]
    
class User(BaseModel):
    """User Model - Banking apps में customer details"""
    user_id: str
    username: str
    email: str
    scopes: List[str]

class TokenRequest(BaseModel):
    """Token Request Model"""
    grant_type: str
    client_id: str
    client_secret: str
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None

# Mock database - Production में proper database use करें
CLIENTS_DB = {
    "paytm_client": Client(
        client_id="paytm_client",
        client_secret="paytm_secret_2024",
        redirect_uris=["https://paytm.com/callback"],
        scope=["read", "write", "payment"],
        grant_types=["authorization_code", "refresh_token"]
    ),
    "phonepe_client": Client(
        client_id="phonepe_client", 
        client_secret="phonepe_secret_2024",
        redirect_uris=["https://phonepe.com/callback"],
        scope=["read", "payment", "transfer"],
        grant_types=["client_credentials", "authorization_code"]
    )
}

USERS_DB = {
    "user123": User(
        user_id="user123",
        username="rahul_mumbai",
        email="rahul@gmail.com",
        scopes=["read", "write", "payment"]
    )
}

class SecurityUtils:
    """Security utilities - Production security के लिए zaroori functions"""
    
    @staticmethod
    def generate_auth_code(client_id: str, user_id: str) -> str:
        """Authorization code generate करता है - 10 minute validity"""
        code_data = f"{client_id}:{user_id}:{time.time()}"
        auth_code = hashlib.sha256(code_data.encode()).hexdigest()[:16]
        
        # Redis में store करें with expiry
        redis_client.setex(f"auth_code:{auth_code}", 600, f"{client_id}:{user_id}")
        return auth_code
    
    @staticmethod
    def validate_auth_code(auth_code: str, client_id: str) -> Optional[str]:
        """Authorization code validate करता है"""
        stored_data = redis_client.get(f"auth_code:{auth_code}")
        if not stored_data:
            return None
            
        stored_client_id, user_id = stored_data.split(":")
        if stored_client_id != client_id:
            return None
            
        # Code use हो गया, delete कर दो - One time use only
        redis_client.delete(f"auth_code:{auth_code}")
        return user_id
    
    @staticmethod
    def generate_access_token(client_id: str, user_id: str, scopes: List[str]) -> str:
        """JWT access token generate करता है"""
        payload = {
            "client_id": client_id,
            "user_id": user_id,
            "scopes": scopes,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "type": "access_token"
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def generate_refresh_token(client_id: str, user_id: str) -> str:
        """Refresh token generate करता है - Long term validity"""
        payload = {
            "client_id": client_id,
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow(),
            "type": "refresh_token"
        }
        refresh_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Redis में store करें for revocation capability
        redis_client.setex(f"refresh_token:{refresh_token}", 
                          REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600, 
                          f"{client_id}:{user_id}")
        return refresh_token
    
    @staticmethod
    def validate_token(token: str) -> Optional[Dict]:
        """Token validate करता है - हर API call पर check"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Blacklist check - Token revoke हुआ है या नहीं
            if redis_client.sismember("blacklisted_tokens", token):
                return None
                
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

class RateLimiter:
    """Rate limiting - DDoS protection ke liye"""
    
    @staticmethod
    def check_rate_limit(client_id: str, limit: int = 100, window: int = 3600) -> bool:
        """Rate limit check करता है - hourly limit"""
        key = f"rate_limit:{client_id}:{int(time.time() / window)}"
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, window, 1)
            return True
        elif int(current) < limit:
            redis_client.incr(key)
            return True
        else:
            return False

def validate_client(client_id: str, client_secret: str) -> Optional[Client]:
    """Client credentials validate करता है"""
    client = CLIENTS_DB.get(client_id)
    if not client or client.client_secret != client_secret:
        return None
    return client

async def log_security_event(event_type: str, details: Dict):
    """Security events को log करता है - Audit trail"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "details": details
    }
    logger.info(f"Security Event: {log_entry}")
    
    # Production में इसे proper SIEM system में send करें
    # Example: Splunk, ELK Stack, or AWS CloudTrail

@app.post("/oauth/authorize")
async def authorize(
    request: Request,
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(...),
    state: str = Form(None),
    user_id: str = Form(...) # Normally यह login flow से आएगा
):
    """
    Authorization endpoint - User को authorize करता है
    
    यह PhonePe/Paytm जैसे apps में consent screen दिखाने के बाद call होता है
    """
    
    # Rate limiting check
    if not RateLimiter.check_rate_limit(client_id, limit=50):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Client validation
    client = CLIENTS_DB.get(client_id)
    if not client:
        await log_security_event("invalid_client", {"client_id": client_id})
        raise HTTPException(status_code=400, detail="Invalid client")
    
    # Redirect URI validation
    if redirect_uri not in client.redirect_uris:
        await log_security_event("invalid_redirect_uri", {
            "client_id": client_id,
            "redirect_uri": redirect_uri
        })
        raise HTTPException(status_code=400, detail="Invalid redirect URI")
    
    # Response type validation
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response type")
    
    # User validation
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    # Scope validation
    requested_scopes = scope.split(" ")
    if not all(s in user.scopes for s in requested_scopes):
        raise HTTPException(status_code=400, detail="Insufficient scope")
    
    # Authorization code generate करें
    auth_code = SecurityUtils.generate_auth_code(client_id, user_id)
    
    await log_security_event("authorization_granted", {
        "client_id": client_id,
        "user_id": user_id,
        "scopes": requested_scopes
    })
    
    # Production में यह redirect response होगा
    return {
        "authorization_code": auth_code,
        "state": state,
        "expires_in": 600
    }

@app.post("/oauth/token")
async def token(request: Request, token_request: TokenRequest):
    """
    Token endpoint - Access token issue करता है
    
    Different grant types handle करता है:
    - authorization_code: Web apps के लिए
    - client_credentials: Server-to-server communication
    - refresh_token: Token refresh करने के लिए
    """
    
    # Rate limiting
    if not RateLimiter.check_rate_limit(token_request.client_id, limit=200):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Client validation
    client = validate_client(token_request.client_id, token_request.client_secret)
    if not client:
        await log_security_event("invalid_client_credentials", {
            "client_id": token_request.client_id
        })
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    
    if token_request.grant_type == "authorization_code":
        # Authorization Code Flow
        if "authorization_code" not in client.grant_types:
            raise HTTPException(status_code=400, detail="Grant type not allowed")
        
        if not token_request.code:
            raise HTTPException(status_code=400, detail="Authorization code required")
        
        user_id = SecurityUtils.validate_auth_code(token_request.code, token_request.client_id)
        if not user_id:
            await log_security_event("invalid_authorization_code", {
                "client_id": token_request.client_id,
                "code": token_request.code
            })
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        user = USERS_DB[user_id]
        access_token = SecurityUtils.generate_access_token(
            token_request.client_id, user_id, user.scopes
        )
        refresh_token = SecurityUtils.generate_refresh_token(token_request.client_id, user_id)
        
        await log_security_event("access_token_issued", {
            "client_id": token_request.client_id,
            "user_id": user_id,
            "grant_type": "authorization_code"
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scope": " ".join(user.scopes)
        }
    
    elif token_request.grant_type == "client_credentials":
        # Client Credentials Flow - Server to server
        if "client_credentials" not in client.grant_types:
            raise HTTPException(status_code=400, detail="Grant type not allowed")
        
        access_token = SecurityUtils.generate_access_token(
            token_request.client_id, token_request.client_id, client.scope
        )
        
        await log_security_event("access_token_issued", {
            "client_id": token_request.client_id,
            "grant_type": "client_credentials"
        })
        
        return {
            "access_token": access_token,
            "token_type": "Bearer", 
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scope": " ".join(client.scope)
        }
    
    elif token_request.grant_type == "refresh_token":
        # Refresh Token Flow
        if not token_request.refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")
        
        # Refresh token validate करें
        if not redis_client.get(f"refresh_token:{token_request.refresh_token}"):
            await log_security_event("invalid_refresh_token", {
                "client_id": token_request.client_id
            })
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        token_payload = SecurityUtils.validate_token(token_request.refresh_token)
        if not token_payload or token_payload.get("type") != "refresh_token":
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        if token_payload["client_id"] != token_request.client_id:
            raise HTTPException(status_code=400, detail="Client mismatch")
        
        user_id = token_payload["user_id"]
        user = USERS_DB.get(user_id)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # New access token issue करें
        new_access_token = SecurityUtils.generate_access_token(
            token_request.client_id, user_id, user.scopes
        )
        
        await log_security_event("token_refreshed", {
            "client_id": token_request.client_id,
            "user_id": user_id
        })
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "scope": " ".join(user.scopes)
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")

@app.post("/oauth/introspect")
async def introspect(
    token: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Token introspection endpoint - Token की validity check करता है
    
    यह API Gateway या Resource Server use करते हैं token validate करने के लिए
    """
    
    # Basic auth से client validate करें (Production में proper implementation)
    # यहाँ simplified version है
    
    token_payload = SecurityUtils.validate_token(token)
    if not token_payload:
        return {"active": False}
    
    return {
        "active": True,
        "client_id": token_payload.get("client_id"),
        "user_id": token_payload.get("user_id"),
        "scope": " ".join(token_payload.get("scopes", [])),
        "exp": token_payload.get("exp"),
        "iat": token_payload.get("iat")
    }

@app.post("/oauth/revoke")
async def revoke_token(
    token: str = Form(...),
    token_type_hint: str = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Token revocation endpoint - Token को blacklist करता है
    
    User logout या security breach के time use होता है
    """
    
    # Token को blacklist में add करें
    redis_client.sadd("blacklisted_tokens", token)
    
    # Refresh token revoke करने के लिए Redis से भी remove करें
    if token_type_hint == "refresh_token":
        redis_client.delete(f"refresh_token:{token}")
    
    await log_security_event("token_revoked", {
        "token_type_hint": token_type_hint
    })
    
    return {"revoked": True}

@app.get("/oauth/userinfo")
async def get_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    User info endpoint - Token से user information return करता है
    
    OpenID Connect compatible endpoint
    """
    
    token = credentials.credentials
    token_payload = SecurityUtils.validate_token(token)
    
    if not token_payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = token_payload.get("user_id")
    user = USERS_DB.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Scope check - profile scope required for user info
    scopes = token_payload.get("scopes", [])
    if "profile" not in scopes:
        raise HTTPException(status_code=403, detail="Insufficient scope")
    
    return {
        "sub": user.user_id,
        "username": user.username,
        "email": user.email,
        "scopes": user.scopes
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - Load balancer के लिए"""
    try:
        # Redis connectivity check
        redis_client.ping()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

if __name__ == "__main__":
    import uvicorn
    
    print("🔐 OAuth 2.0 Authorization Server Starting...")
    print("📱 Mumbai style security with Paytm/PhonePe level protection")
    print("🚀 Production ready with rate limiting and audit logging")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)

"""
Production Deployment Notes:
============================

1. Environment Variables:
   - JWT_SECRET: Strong random key (256-bit)
   - REDIS_URL: Redis cluster URL
   - DATABASE_URL: Proper database connection

2. Security Considerations:
   - HTTPS only in production
   - Rate limiting with proper Redis cluster
   - Token rotation policy
   - Audit logging to SIEM
   - Regular security audits

3. Monitoring:
   - Token generation metrics
   - Failed authentication alerts
   - Rate limit breaches
   - Performance monitoring

4. Scalability:
   - Redis Cluster for session management
   - Database read replicas
   - Load balancer with health checks
   - Horizontal pod autoscaling

यह implementation PhonePe/Paytm level की security provide करता है!
"""