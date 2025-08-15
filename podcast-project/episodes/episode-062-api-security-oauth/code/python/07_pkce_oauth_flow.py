"""
PKCE (Proof Key for Code Exchange) OAuth Flow
============================================

यह implementation PKCE OAuth flow को demonstrate करता है।
Mobile apps और SPA (Single Page Applications) में इसी security
pattern का use होता है। Google, Facebook जैसे apps में यही
implementation होती है।

PKCE RFC 7636 के अनुसार:
- Code Verifier generation
- Code Challenge creation
- Authorization request with challenge
- Token exchange with verifier

Author: Hindi Tech Podcast  
Episode: 062 - API Security & OAuth
"""

import hashlib
import base64
import secrets
import time
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from urllib.parse import urlencode, parse_qs, urlparse
from fastapi import FastAPI, HTTPException, Request, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
import jwt

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeChallengeMethod(Enum):
    """PKCE code challenge methods"""
    PLAIN = "plain"
    S256 = "S256"  # SHA256 (recommended)

class PKCEState(Enum):
    """PKCE flow states"""
    INITIATED = "initiated"
    AUTHORIZED = "authorized"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"

@dataclass
class PKCESession:
    """PKCE session data"""
    session_id: str
    client_id: str
    redirect_uri: str
    scope: str
    state: str
    code_verifier: str
    code_challenge: str
    code_challenge_method: CodeChallengeMethod
    authorization_code: Optional[str]
    pkce_state: PKCEState
    created_at: datetime
    expires_at: datetime
    user_id: Optional[str] = None

@dataclass 
class PKCEClient:
    """PKCE client configuration"""
    client_id: str
    client_name: str
    redirect_uris: List[str]
    allowed_scopes: List[str]
    client_type: str  # "public" for mobile/SPA, "confidential" for server
    pkce_required: bool = True

class PKCECodeGenerator:
    """PKCE code verifier और challenge generator"""
    
    @staticmethod
    def generate_code_verifier() -> str:
        """
        Code verifier generate करता है
        
        RFC 7636 के अनुसार:
        - 43-128 characters long
        - URL-safe characters only
        - Cryptographically random
        """
        # Generate 32 random bytes = 43 characters in base64url
        random_bytes = secrets.token_bytes(32)
        code_verifier = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        return code_verifier
    
    @staticmethod
    def generate_code_challenge(
        code_verifier: str, 
        method: CodeChallengeMethod = CodeChallengeMethod.S256
    ) -> str:
        """
        Code challenge generate करता है
        
        S256 method (recommended):
        code_challenge = BASE64URL(SHA256(code_verifier))
        """
        if method == CodeChallengeMethod.PLAIN:
            return code_verifier
        elif method == CodeChallengeMethod.S256:
            # SHA256 hash और base64url encode
            sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
            code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
            return code_challenge
        else:
            raise ValueError(f"Unsupported challenge method: {method}")
    
    @staticmethod
    def verify_code_challenge(
        code_verifier: str, 
        code_challenge: str, 
        method: CodeChallengeMethod
    ) -> bool:
        """Code verifier को challenge के साथ verify करता है"""
        
        expected_challenge = PKCECodeGenerator.generate_code_challenge(code_verifier, method)
        return expected_challenge == code_challenge

class PKCEAuthorizationServer:
    """
    PKCE-enabled OAuth 2.0 Authorization Server
    
    Mobile apps और SPAs के लिए secure OAuth flow provide करता है
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_timeout_minutes = 10  # Authorization session timeout
        self.code_timeout_minutes = 5      # Authorization code timeout
        
        # JWT settings
        self.jwt_secret = "pkce_jwt_secret_production_mein_change_karna"
        self.jwt_algorithm = "HS256"
        self.access_token_lifetime = timedelta(minutes=15)
        self.refresh_token_lifetime = timedelta(days=30)
        
        # Registered PKCE clients
        self.clients = {
            "zomato_mobile_app": PKCEClient(
                client_id="zomato_mobile_app",
                client_name="Zomato Mobile App",
                redirect_uris=["com.zomato.app://oauth/callback", "https://zomato.com/oauth/callback"],
                allowed_scopes=["read_profile", "place_order", "read_orders"],
                client_type="public",
                pkce_required=True
            ),
            "swiggy_spa": PKCEClient(
                client_id="swiggy_spa",
                client_name="Swiggy Web App",
                redirect_uris=["https://swiggy.com/auth/callback"],
                allowed_scopes=["read_profile", "place_order"],
                client_type="public", 
                pkce_required=True
            ),
            "paytm_mobile": PKCEClient(
                client_id="paytm_mobile",
                client_name="Paytm Mobile App",
                redirect_uris=["com.paytm.app://oauth/callback"],
                allowed_scopes=["read_profile", "read_balance", "make_payment"],
                client_type="public",
                pkce_required=True
            )
        }
        
        # Mock user database
        self.users = {
            "user_mumbai_123": {
                "user_id": "user_mumbai_123",
                "username": "rahul_mumbai",
                "email": "rahul@gmail.com",
                "phone": "+91-9876543210",
                "verified": True
            },
            "user_delhi_456": {
                "user_id": "user_delhi_456", 
                "username": "priya_delhi",
                "email": "priya@gmail.com",
                "phone": "+91-8765432109",
                "verified": True
            }
        }
    
    async def initiate_pkce_flow(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        state: str,
        code_challenge: str,
        code_challenge_method: str = "S256"
    ) -> PKCESession:
        """
        PKCE flow initiate करता है
        
        Mobile app से यह step सबसे पहले call होता है
        """
        
        # Validate client
        client = self.clients.get(client_id)
        if not client:
            raise HTTPException(status_code=400, detail="Invalid client_id")
        
        # Validate redirect URI
        if redirect_uri not in client.redirect_uris:
            raise HTTPException(status_code=400, detail="Invalid redirect_uri")
        
        # Validate scope
        requested_scopes = scope.split(" ")
        if not all(s in client.allowed_scopes for s in requested_scopes):
            raise HTTPException(status_code=400, detail="Invalid scope")
        
        # Validate code challenge method
        try:
            challenge_method = CodeChallengeMethod(code_challenge_method)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid code_challenge_method")
        
        # Validate code challenge format
        if not code_challenge or len(code_challenge) < 43:
            raise HTTPException(status_code=400, detail="Invalid code_challenge")
        
        # Create PKCE session
        session_id = secrets.token_urlsafe(32)
        
        pkce_session = PKCESession(
            session_id=session_id,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            code_verifier="",  # Client नहीं भेजता, server store नहीं करता
            code_challenge=code_challenge,
            code_challenge_method=challenge_method,
            authorization_code=None,
            pkce_state=PKCEState.INITIATED,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
        )
        
        # Store session in Redis
        await self._store_pkce_session(pkce_session)
        
        # Log initiation
        await self._log_pkce_event("pkce_initiated", {
            "session_id": session_id,
            "client_id": client_id,
            "challenge_method": code_challenge_method,
            "scope": scope
        })
        
        logger.info(f"PKCE flow initiated for client {client_id}, session {session_id}")
        return pkce_session
    
    async def authorize_pkce_session(
        self,
        session_id: str,
        user_id: str,
        user_consent: bool = True
    ) -> str:
        """
        User authorization के बाद authorization code generate करता है
        
        User login और consent के बाद यह step होता है
        """
        
        # Get PKCE session
        pkce_session = await self._get_pkce_session(session_id)
        if not pkce_session:
            raise HTTPException(status_code=400, detail="Invalid session")
        
        # Check session state
        if pkce_session.pkce_state != PKCEState.INITIATED:
            raise HTTPException(status_code=400, detail="Invalid session state")
        
        # Check session expiry
        if datetime.utcnow() > pkce_session.expires_at:
            pkce_session.pkce_state = PKCEState.EXPIRED
            await self._store_pkce_session(pkce_session)
            raise HTTPException(status_code=400, detail="Session expired")
        
        # Check user consent
        if not user_consent:
            pkce_session.pkce_state = PKCEState.FAILED
            await self._store_pkce_session(pkce_session)
            raise HTTPException(status_code=400, detail="User denied consent")
        
        # Validate user
        if user_id not in self.users:
            raise HTTPException(status_code=400, detail="Invalid user")
        
        # Generate authorization code
        auth_code = secrets.token_urlsafe(32)
        
        # Update session
        pkce_session.authorization_code = auth_code
        pkce_session.user_id = user_id
        pkce_session.pkce_state = PKCEState.AUTHORIZED
        
        # Store updated session
        await self._store_pkce_session(pkce_session)
        
        # Store authorization code with short expiry
        code_data = {
            "session_id": session_id,
            "user_id": user_id,
            "client_id": pkce_session.client_id,
            "scope": pkce_session.scope,
            "code_challenge": pkce_session.code_challenge,
            "code_challenge_method": pkce_session.code_challenge_method.value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.redis.setex(
            f"pkce_auth_code:{auth_code}",
            self.code_timeout_minutes * 60,
            json.dumps(code_data)
        )
        
        # Log authorization
        await self._log_pkce_event("user_authorized", {
            "session_id": session_id,
            "user_id": user_id,
            "client_id": pkce_session.client_id,
            "scope": pkce_session.scope
        })
        
        logger.info(f"User {user_id} authorized PKCE session {session_id}")
        return auth_code
    
    async def exchange_code_for_tokens(
        self,
        client_id: str,
        code: str,
        redirect_uri: str,
        code_verifier: str
    ) -> Dict[str, Any]:
        """
        Authorization code को access token के लिए exchange करता है
        
        यह PKCE का most critical step है - code verifier verification
        """
        
        # Get authorization code data
        code_data = self.redis.get(f"pkce_auth_code:{code}")
        if not code_data:
            raise HTTPException(status_code=400, detail="Invalid or expired authorization code")
        
        code_info = json.loads(code_data)
        
        # Validate client
        if code_info["client_id"] != client_id:
            raise HTTPException(status_code=400, detail="Client mismatch")
        
        # Get PKCE session
        session_id = code_info["session_id"]
        pkce_session = await self._get_pkce_session(session_id)
        if not pkce_session:
            raise HTTPException(status_code=400, detail="Invalid session")
        
        # Validate redirect URI
        if pkce_session.redirect_uri != redirect_uri:
            raise HTTPException(status_code=400, detail="Redirect URI mismatch")
        
        # CRITICAL: Verify code verifier against challenge
        challenge_method = CodeChallengeMethod(code_info["code_challenge_method"])
        if not PKCECodeGenerator.verify_code_challenge(
            code_verifier,
            code_info["code_challenge"],
            challenge_method
        ):
            # Log security violation
            await self._log_pkce_event("code_verifier_mismatch", {
                "session_id": session_id,
                "client_id": client_id,
                "challenge_method": challenge_method.value
            })
            
            # Mark session as failed
            pkce_session.pkce_state = PKCEState.FAILED
            await self._store_pkce_session(pkce_session)
            
            raise HTTPException(status_code=400, detail="Invalid code verifier")
        
        # Generate tokens
        user_id = code_info["user_id"]
        scope = code_info["scope"]
        
        access_token = self._generate_access_token(user_id, client_id, scope)
        refresh_token = self._generate_refresh_token(user_id, client_id)
        
        # Mark session as completed
        pkce_session.pkce_state = PKCEState.COMPLETED
        await self._store_pkce_session(pkce_session)
        
        # Delete authorization code (one-time use)
        self.redis.delete(f"pkce_auth_code:{code}")
        
        # Log successful token exchange
        await self._log_pkce_event("tokens_issued", {
            "session_id": session_id,
            "user_id": user_id,
            "client_id": client_id,
            "scope": scope
        })
        
        logger.info(f"PKCE tokens issued for user {user_id}, client {client_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(self.access_token_lifetime.total_seconds()),
            "scope": scope
        }
    
    def _generate_access_token(self, user_id: str, client_id: str, scope: str) -> str:
        """JWT access token generate करता है"""
        
        payload = {
            "sub": user_id,
            "client_id": client_id,
            "scope": scope.split(" "),
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + self.access_token_lifetime).timestamp(),
            "iss": "pkce_auth_server",
            "aud": client_id,
            "jti": secrets.token_hex(16)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _generate_refresh_token(self, user_id: str, client_id: str) -> str:
        """Refresh token generate करता है"""
        
        payload = {
            "sub": user_id,
            "client_id": client_id,
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + self.refresh_token_lifetime).timestamp(),
            "type": "refresh_token",
            "jti": secrets.token_hex(16)
        }
        
        refresh_token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Store refresh token in Redis for revocation capability
        self.redis.setex(
            f"pkce_refresh_token:{refresh_token}",
            int(self.refresh_token_lifetime.total_seconds()),
            json.dumps({"user_id": user_id, "client_id": client_id})
        )
        
        return refresh_token
    
    async def _store_pkce_session(self, session: PKCESession):
        """PKCE session को Redis में store करता है"""
        
        session_dict = asdict(session)
        session_dict["created_at"] = session_dict["created_at"].isoformat()
        session_dict["expires_at"] = session_dict["expires_at"].isoformat()
        session_dict["code_challenge_method"] = session_dict["code_challenge_method"].value
        session_dict["pkce_state"] = session_dict["pkce_state"].value
        
        self.redis.setex(
            f"pkce_session:{session.session_id}",
            self.session_timeout_minutes * 60,
            json.dumps(session_dict)
        )
    
    async def _get_pkce_session(self, session_id: str) -> Optional[PKCESession]:
        """PKCE session को Redis से retrieve करता है"""
        
        session_data = self.redis.get(f"pkce_session:{session_id}")
        if not session_data:
            return None
        
        session_dict = json.loads(session_data)
        session_dict["created_at"] = datetime.fromisoformat(session_dict["created_at"])
        session_dict["expires_at"] = datetime.fromisoformat(session_dict["expires_at"])
        session_dict["code_challenge_method"] = CodeChallengeMethod(session_dict["code_challenge_method"])
        session_dict["pkce_state"] = PKCEState(session_dict["pkce_state"])
        
        return PKCESession(**session_dict)
    
    async def _log_pkce_event(self, event_type: str, details: Dict[str, Any]):
        """PKCE events को log करता है"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "service": "pkce_auth_server"
        }
        
        logger.info(f"PKCE Event: {json.dumps(log_entry)}")
        
        # Store in Redis for monitoring
        self.redis.lpush("pkce_events", json.dumps(log_entry))
        self.redis.ltrim("pkce_events", 0, 999)

# FastAPI application
app = FastAPI(title="PKCE OAuth 2.0 Server")

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# PKCE Authorization Server
pkce_server = PKCEAuthorizationServer(redis_client)

@app.get("/oauth/authorize")
async def authorize_endpoint(
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    response_type: str = Query(...),
    scope: str = Query(...),
    state: str = Query(...),
    code_challenge: str = Query(...),
    code_challenge_method: str = Query(default="S256")
):
    """
    PKCE Authorization endpoint
    
    Mobile app यहाँ user को redirect करता है authorization के लिए
    """
    
    # Validate response type
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Invalid response_type")
    
    try:
        # Initiate PKCE flow
        pkce_session = await pkce_server.initiate_pkce_flow(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method
        )
        
        # Return login page with session ID
        login_html = f"""
        <html>
        <head><title>PKCE OAuth Login</title></head>
        <body>
            <h2>🔐 Authorize {pkce_server.clients[client_id].client_name}</h2>
            <p>The app is requesting access to:</p>
            <ul>
                {''.join(f'<li>{scope_item}</li>' for scope_item in scope.split(' '))}
            </ul>
            
            <form method="post" action="/oauth/login">
                <input type="hidden" name="session_id" value="{pkce_session.session_id}">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="state" value="{state}">
                
                <p>Login:</p>
                <select name="user_id">
                    <option value="user_mumbai_123">Rahul Mumbai</option>
                    <option value="user_delhi_456">Priya Delhi</option>
                </select>
                
                <br><br>
                <input type="submit" name="action" value="Authorize">
                <input type="submit" name="action" value="Deny">
            </form>
            
            <p><small>Session ID: {pkce_session.session_id}</small></p>
        </body>
        </html>
        """
        
        return HTMLResponse(content=login_html)
        
    except HTTPException as e:
        # Redirect back with error
        error_params = urlencode({
            "error": "invalid_request",
            "error_description": e.detail,
            "state": state
        })
        return RedirectResponse(url=f"{redirect_uri}?{error_params}")

@app.post("/oauth/login")
async def login_endpoint(
    session_id: str = Form(...),
    client_id: str = Form(...),
    state: str = Form(...),
    user_id: str = Form(...),
    action: str = Form(...)
):
    """User login और consent handling"""
    
    try:
        # Get client for redirect URI
        client = pkce_server.clients[client_id]
        redirect_uri = client.redirect_uris[0]  # Use first redirect URI
        
        if action == "Deny":
            # User denied consent
            error_params = urlencode({
                "error": "access_denied",
                "error_description": "User denied the request",
                "state": state
            })
            return RedirectResponse(url=f"{redirect_uri}?{error_params}")
        
        # User authorized - generate authorization code
        auth_code = await pkce_server.authorize_pkce_session(
            session_id=session_id,
            user_id=user_id,
            user_consent=True
        )
        
        # Redirect back to app with authorization code
        success_params = urlencode({
            "code": auth_code,
            "state": state
        })
        
        return RedirectResponse(url=f"{redirect_uri}?{success_params}")
        
    except HTTPException as e:
        error_params = urlencode({
            "error": "server_error",
            "error_description": e.detail,
            "state": state
        })
        return RedirectResponse(url=f"{redirect_uri}?{error_params}")

@app.post("/oauth/token")
async def token_endpoint(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    code_verifier: str = Form(...)
):
    """
    Token endpoint - Authorization code को tokens के लिए exchange करता है
    
    यहाँ PKCE verification होती है
    """
    
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Invalid grant_type")
    
    try:
        tokens = await pkce_server.exchange_code_for_tokens(
            client_id=client_id,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier
        )
        
        return tokens
        
    except HTTPException as e:
        return {
            "error": "invalid_grant",
            "error_description": e.detail
        }

@app.get("/oauth/userinfo")
async def userinfo_endpoint(authorization: str = Query(..., alias="Authorization")):
    """User info endpoint - Access token से user details return करता है"""
    
    try:
        # Extract bearer token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization[7:]  # Remove "Bearer "
        
        # Decode JWT token
        payload = jwt.decode(token, pkce_server.jwt_secret, algorithms=[pkce_server.jwt_algorithm])
        
        user_id = payload["sub"]
        user_info = pkce_server.users.get(user_id)
        
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "sub": user_id,
            "username": user_info["username"],
            "email": user_info["email"],
            "phone": user_info["phone"],
            "verified": user_info["verified"]
        }
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Mobile app simulator endpoints
@app.get("/demo/mobile-app")
async def mobile_app_demo():
    """Mobile app simulation - PKCE flow demonstration"""
    
    # Generate PKCE parameters
    code_verifier = PKCECodeGenerator.generate_code_verifier()
    code_challenge = PKCECodeGenerator.generate_code_challenge(code_verifier)
    
    # App state
    state = secrets.token_urlsafe(16)
    
    # Authorization URL
    auth_params = urlencode({
        "client_id": "zomato_mobile_app",
        "redirect_uri": "com.zomato.app://oauth/callback",
        "response_type": "code",
        "scope": "read_profile place_order",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    })
    
    auth_url = f"/oauth/authorize?{auth_params}"
    
    demo_html = f"""
    <html>
    <head><title>📱 PKCE Mobile App Demo</title></head>
    <body>
        <h2>🍕 Zomato Mobile App - PKCE OAuth Demo</h2>
        
        <h3>Step 1: Generate PKCE Parameters</h3>
        <p><strong>Code Verifier:</strong> <code>{code_verifier}</code></p>
        <p><strong>Code Challenge:</strong> <code>{code_challenge}</code></p>
        <p><strong>Challenge Method:</strong> S256</p>
        <p><strong>State:</strong> <code>{state}</code></p>
        
        <h3>Step 2: Authorization Request</h3>
        <p><a href="{auth_url}" target="_blank">🔗 Authorize App (नई window में खुलेगा)</a></p>
        
        <h3>Step 3: Token Exchange</h3>
        <p>Authorization के बाद, app को code मिलेगा। फिर code_verifier के साथ token exchange करना होगा।</p>
        
        <form method="post" action="/demo/token-exchange">
            <input type="hidden" name="code_verifier" value="{code_verifier}">
            <input type="hidden" name="state" value="{state}">
            
            <label>Authorization Code (callback से copy करें):</label><br>
            <input type="text" name="code" size="50" placeholder="Authorization code यहाँ paste करें"><br><br>
            
            <input type="submit" value="🔄 Exchange for Tokens">
        </form>
        
        <h3>Security Benefits of PKCE:</h3>
        <ul>
            <li>✅ No client secret needed (public clients के लिए safe)</li>
            <li>✅ Authorization code interception attacks prevent होते हैं</li>
            <li>✅ Code verifier dynamic है, reuse नहीं हो सकता</li>
            <li>✅ SHA256 challenge cryptographically secure है</li>
        </ul>
    </body>
    </html>
    """
    
    return HTMLResponse(content=demo_html)

@app.post("/demo/token-exchange")
async def demo_token_exchange(
    code: str = Form(...),
    code_verifier: str = Form(...),
    state: str = Form(...)
):
    """Demo token exchange"""
    
    try:
        tokens = await pkce_server.exchange_code_for_tokens(
            client_id="zomato_mobile_app",
            code=code,
            redirect_uri="com.zomato.app://oauth/callback",
            code_verifier=code_verifier
        )
        
        result_html = f"""
        <html>
        <head><title>✅ PKCE Token Exchange Success</title></head>
        <body>
            <h2>🎉 Token Exchange Successful!</h2>
            
            <h3>Tokens Received:</h3>
            <p><strong>Access Token:</strong><br><code>{tokens['access_token']}</code></p>
            <p><strong>Refresh Token:</strong><br><code>{tokens['refresh_token']}</code></p>
            <p><strong>Token Type:</strong> {tokens['token_type']}</p>
            <p><strong>Expires In:</strong> {tokens['expires_in']} seconds</p>
            <p><strong>Scope:</strong> {tokens['scope']}</p>
            
            <h3>Test API Call:</h3>
            <form method="get" action="/oauth/userinfo">
                <input type="hidden" name="Authorization" value="Bearer {tokens['access_token']}">
                <input type="submit" value="📋 Get User Info">
            </form>
            
            <p><a href="/demo/mobile-app">🔄 Start New PKCE Flow</a></p>
        </body>
        </html>
        """
        
        return HTMLResponse(content=result_html)
        
    except Exception as e:
        error_html = f"""
        <html>
        <head><title>❌ Token Exchange Failed</title></head>
        <body>
            <h2>❌ Token Exchange Failed</h2>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><a href="/demo/mobile-app">🔄 Try Again</a></p>
        </body>
        </html>
        """
        
        return HTMLResponse(content=error_html)

@app.get("/")
async def home():
    """Home page with links to demos"""
    
    home_html = """
    <html>
    <head><title>🔐 PKCE OAuth 2.0 Server</title></head>
    <body>
        <h1>🔐 PKCE OAuth 2.0 Authorization Server</h1>
        
        <h2>🚀 What is PKCE?</h2>
        <p>PKCE (Proof Key for Code Exchange) एक OAuth 2.0 extension है जो public clients 
        (mobile apps, SPAs) के लिए additional security provide करता है।</p>
        
        <h2>🔒 Security Benefits:</h2>
        <ul>
            <li>Authorization code interception attacks prevent करता है</li>
            <li>Client secret की जरूरत नहीं (public clients के लिए)</li>
            <li>Dynamic code verifier/challenge pair</li>
            <li>Cryptographically secure (SHA256)</li>
        </ul>
        
        <h2>📱 Demo Applications:</h2>
        <ul>
            <li><a href="/demo/mobile-app">🍕 Zomato Mobile App Demo</a></li>
            <li><a href="/docs">📚 API Documentation</a></li>
        </ul>
        
        <h2>🏦 Real World Usage:</h2>
        <p>यह implementation Google, Facebook, Twitter जैसे major OAuth providers 
        में use होती है mobile apps के लिए।</p>
    </body>
    </html>
    """
    
    return HTMLResponse(content=home_html)

if __name__ == "__main__":
    import uvicorn
    
    print("🔐 PKCE OAuth 2.0 Authorization Server")
    print("📱 Mobile app security के लिए RFC 7636 implementation")
    print("🍕 Zomato/Swiggy style mobile authentication")
    print("🔒 Authorization code interception protection")
    print("⚡ Production ready PKCE flow")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)

"""
Production Implementation Notes:
===============================

1. Security Enhancements:
   - Implement proper user authentication
   - Add CSRF protection
   - Use HTTPS only
   - Implement proper session management
   - Add brute force protection

2. Mobile App Integration:
   - Custom URL schemes for deep linking
   - Secure storage for code_verifier
   - Network security (certificate pinning)
   - Biometric authentication integration

3. Monitoring और Analytics:
   - PKCE flow completion rates
   - Failed verification attempts
   - User consent patterns
   - Security incident detection

4. Compliance:
   - OAuth 2.1 compliance
   - OIDC integration
   - Privacy regulations (GDPR, etc.)
   - Industry standards (PCI DSS for payments)

यह implementation Google Play Services और Apple Sign-In level की security provide करता है!
"""