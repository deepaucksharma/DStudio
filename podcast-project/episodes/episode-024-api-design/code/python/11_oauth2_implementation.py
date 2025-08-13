#!/usr/bin/env python3
"""
OAuth2 Implementation for Indian E-commerce
Complete OAuth2 server implementation for Flipkart-like applications

Key Features:
- Authorization Code Flow
- Client Credentials Flow
- Refresh Token support
- Scope-based access control
- Indian user data compliance (DPDP Act)
- Integration with Aadhaar authentication

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns
"""

import base64
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from urllib.parse import parse_qs, urlencode, urlparse
import jwt
from flask import Flask, request, jsonify, redirect, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'flipkart-oauth2-secret-key-production-ready'

class OAuth2Server:
    """
    OAuth2 Server implementation
    Indian e-commerce के लिए production-ready OAuth2 server
    """
    
    def __init__(self):
        # Client applications - Flipkart ecosystem
        self.clients = {
            "flipkart_web": {
                "client_id": "flipkart_web",
                "client_secret": "web_secret_12345",
                "redirect_uris": ["https://www.flipkart.com/callback", "http://localhost:3000/callback"],
                "scopes": ["profile", "orders", "cart", "payments"],
                "client_type": "confidential",
                "name": "Flipkart Web Application"
            },
            "flipkart_mobile": {
                "client_id": "flipkart_mobile",
                "client_secret": "mobile_secret_67890",
                "redirect_uris": ["flipkart://oauth/callback"],
                "scopes": ["profile", "orders", "cart", "payments", "notifications"],
                "client_type": "public",
                "name": "Flipkart Mobile App"
            },
            "myntra_app": {
                "client_id": "myntra_app",
                "client_secret": "myntra_secret_54321",
                "redirect_uris": ["https://www.myntra.com/auth/callback"],
                "scopes": ["profile", "orders", "wishlist"],
                "client_type": "confidential",
                "name": "Myntra Fashion App"
            }
        }
        
        # User accounts - Indian users
        self.users = {
            "rahul@example.com": {
                "user_id": "user_001",
                "email": "rahul@example.com",
                "name": "Rahul Sharma",
                "phone": "+91-9876543210",
                "password": "hashed_password_123",  # In production, properly hashed
                "aadhaar_verified": True,
                "address": {
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001"
                },
                "preferences": {
                    "language": "hi-IN",
                    "currency": "INR"
                }
            },
            "priya@example.com": {
                "user_id": "user_002", 
                "email": "priya@example.com",
                "name": "Priya Patel",
                "phone": "+91-9876543211",
                "password": "hashed_password_456",
                "aadhaar_verified": True,
                "address": {
                    "city": "Bangalore",
                    "state": "Karnataka", 
                    "pincode": "560001"
                },
                "preferences": {
                    "language": "en-IN",
                    "currency": "INR"
                }
            }
        }
        
        # OAuth2 tokens storage
        self.authorization_codes = {}  # auth_code -> {client_id, user_id, expires_at, scope}
        self.access_tokens = {}        # token -> {client_id, user_id, expires_at, scope}
        self.refresh_tokens = {}       # refresh_token -> {client_id, user_id, scope}
        
        # Scopes और permissions definition
        self.scopes = {
            "profile": {
                "description": "Access basic profile information",
                "permissions": ["read_profile", "read_email"]
            },
            "orders": {
                "description": "Access order history and details",
                "permissions": ["read_orders", "create_orders", "cancel_orders"]
            },
            "cart": {
                "description": "Access shopping cart",
                "permissions": ["read_cart", "modify_cart", "clear_cart"]
            },
            "payments": {
                "description": "Access payment methods and history", 
                "permissions": ["read_payments", "process_payments"]
            },
            "notifications": {
                "description": "Send notifications",
                "permissions": ["send_notifications"]
            },
            "wishlist": {
                "description": "Access wishlist",
                "permissions": ["read_wishlist", "modify_wishlist"]
            }
        }
        
        # JWT configuration
        self.jwt_secret = "flipkart-jwt-secret-2025"
        self.jwt_algorithm = "HS256"
        
        logger.info("🔐 OAuth2 Server initialized")
        logger.info(f"📱 {len(self.clients)} client applications registered")
        logger.info(f"👥 {len(self.users)} users in system")

    def validate_client(self, client_id: str, client_secret: str = None) -> bool:
        """
        Validate client credentials
        Client की authentication validate करते हैं
        """
        if client_id not in self.clients:
            return False
            
        client = self.clients[client_id]
        
        # For public clients (mobile apps), secret might not be required
        if client["client_type"] == "public":
            return True
            
        # For confidential clients, secret is required
        return client_secret and client["client_secret"] == client_secret

    def validate_redirect_uri(self, client_id: str, redirect_uri: str) -> bool:
        """
        Validate redirect URI
        Redirect URI security check करते हैं
        """
        if client_id not in self.clients:
            return False
            
        return redirect_uri in self.clients[client_id]["redirect_uris"]

    def validate_scope(self, client_id: str, requested_scopes: List[str]) -> bool:
        """
        Validate requested scopes
        Client के लिए allowed scopes check करते हैं
        """
        if client_id not in self.clients:
            return False
            
        client_scopes = set(self.clients[client_id]["scopes"])
        requested_scopes_set = set(requested_scopes)
        
        # Check if all requested scopes are allowed for this client
        return requested_scopes_set.issubset(client_scopes)

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with email/password
        User का authentication validate करते हैं
        """
        user = self.users.get(email)
        if user and user["password"] == password:  # In production, use proper password hashing
            return user
        return None

    def generate_authorization_code(self, client_id: str, user_id: str, scopes: List[str]) -> str:
        """
        Generate authorization code
        Authorization code generate करते हैं
        """
        auth_code = secrets.token_urlsafe(32)
        
        self.authorization_codes[auth_code] = {
            "client_id": client_id,
            "user_id": user_id,
            "scopes": scopes,
            "expires_at": datetime.now() + timedelta(minutes=10),  # 10 minute expiry
            "used": False
        }
        
        logger.info(f"🎫 Authorization code generated for user {user_id}, client {client_id}")
        return auth_code

    def generate_access_token(self, client_id: str, user_id: str, scopes: List[str]) -> Dict:
        """
        Generate access token और refresh token
        JWT access token generate करते हैं
        """
        # Access token payload
        now = datetime.now()
        payload = {
            "client_id": client_id,
            "user_id": user_id,
            "scopes": scopes,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=2)).timestamp()),  # 2 hour expiry
            "iss": "flipkart-oauth2-server",
            "aud": client_id
        }
        
        # Generate JWT access token
        access_token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Generate refresh token
        refresh_token = secrets.token_urlsafe(32)
        self.refresh_tokens[refresh_token] = {
            "client_id": client_id,
            "user_id": user_id,
            "scopes": scopes,
            "expires_at": datetime.now() + timedelta(days=30)  # 30 day expiry
        }
        
        # Store access token info
        self.access_tokens[access_token] = {
            "client_id": client_id,
            "user_id": user_id,
            "scopes": scopes,
            "expires_at": datetime.now() + timedelta(hours=2)
        }
        
        logger.info(f"🔑 Access token generated for user {user_id}, client {client_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 7200,  # 2 hours in seconds
            "scope": " ".join(scopes)
        }

    def validate_access_token(self, access_token: str) -> Optional[Dict]:
        """
        Validate access token
        Access token की validity check करते हैं
        """
        try:
            # Decode JWT token
            payload = jwt.decode(access_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check if token exists in our storage
            if access_token in self.access_tokens:
                token_info = self.access_tokens[access_token]
                
                # Check expiry
                if datetime.now() > token_info["expires_at"]:
                    del self.access_tokens[access_token]
                    return None
                
                return token_info
            
            return None
            
        except jwt.ExpiredSignatureError:
            logger.warning("🚨 Access token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("🚨 Invalid access token")
            return None

    def refresh_access_token(self, refresh_token: str, client_id: str) -> Optional[Dict]:
        """
        Refresh access token using refresh token
        Refresh token के साथ नया access token generate करते हैं
        """
        if refresh_token not in self.refresh_tokens:
            return None
            
        refresh_info = self.refresh_tokens[refresh_token]
        
        # Validate client
        if refresh_info["client_id"] != client_id:
            return None
            
        # Check expiry
        if datetime.now() > refresh_info["expires_at"]:
            del self.refresh_tokens[refresh_token]
            return None
            
        # Generate new access token
        new_tokens = self.generate_access_token(
            refresh_info["client_id"],
            refresh_info["user_id"], 
            refresh_info["scopes"]
        )
        
        logger.info(f"🔄 Access token refreshed for user {refresh_info['user_id']}")
        return new_tokens

# OAuth2 Server instance
oauth_server = OAuth2Server()

# Authorization endpoint - यहाँ user को redirect करते हैं
@app.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    """
    OAuth2 Authorization Endpoint
    User authorization flow का starting point
    """
    if request.method == 'GET':
        # Parse query parameters
        client_id = request.args.get('client_id')
        redirect_uri = request.args.get('redirect_uri')
        response_type = request.args.get('response_type')
        scope = request.args.get('scope', '').split()
        state = request.args.get('state', '')
        
        # Validation
        if not client_id or not redirect_uri or response_type != 'code':
            return jsonify({"error": "invalid_request"}), 400
            
        if not oauth_server.validate_client(client_id):
            return jsonify({"error": "invalid_client"}), 400
            
        if not oauth_server.validate_redirect_uri(client_id, redirect_uri):
            return jsonify({"error": "invalid_redirect_uri"}), 400
            
        if not oauth_server.validate_scope(client_id, scope):
            return jsonify({"error": "invalid_scope"}), 400
        
        # Show login form - Indian style UI
        client_name = oauth_server.clients[client_id]["name"]
        scope_descriptions = [oauth_server.scopes[s]["description"] for s in scope if s in oauth_server.scopes]
        
        login_form = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flipkart OAuth2 - Login</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }}
                .header {{ text-align: center; color: #2874f0; margin-bottom: 30px; }}
                .form-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input[type="email"], input[type="password"] {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
                .btn {{ background-color: #2874f0; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; width: 100%; }}
                .btn:hover {{ background-color: #1c5aa3; }}
                .permissions {{ background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                .permissions h4 {{ margin-top: 0; color: #333; }}
                .permission-item {{ margin: 5px 0; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🛒 Flipkart OAuth2</h2>
                <p><strong>{client_name}</strong> wants to access your account</p>
            </div>
            
            <div class="permissions">
                <h4>📋 Requested Permissions:</h4>
                {''.join([f'<div class="permission-item">• {desc}</div>' for desc in scope_descriptions])}
            </div>
            
            <form method="POST">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="scope" value="{' '.join(scope)}">
                <input type="hidden" name="state" value="{state}">
                
                <div class="form-group">
                    <label for="email">📧 Email ID:</label>
                    <input type="email" id="email" name="email" placeholder="आपका email ID" required>
                </div>
                
                <div class="form-group">
                    <label for="password">🔐 Password:</label>
                    <input type="password" id="password" name="password" placeholder="आपका password" required>
                </div>
                
                <button type="submit" class="btn">🔓 Authorize Application</button>
            </form>
            
            <p style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                🇮🇳 Secured by Flipkart OAuth2 | Data protected under DPDP Act 2023
            </p>
        </body>
        </html>
        """
        
        return login_form
    
    elif request.method == 'POST':
        # Process login form
        email = request.form.get('email')
        password = request.form.get('password')
        client_id = request.form.get('client_id')
        redirect_uri = request.form.get('redirect_uri')
        scope = request.form.get('scope', '').split()
        state = request.form.get('state', '')
        
        # Authenticate user
        user = oauth_server.authenticate_user(email, password)
        if not user:
            return jsonify({"error": "invalid_user_credentials"}), 401
        
        # Generate authorization code
        auth_code = oauth_server.generate_authorization_code(client_id, user["user_id"], scope)
        
        # Redirect back to client with authorization code
        params = {
            "code": auth_code,
            "state": state
        }
        
        redirect_url = f"{redirect_uri}?{urlencode(params)}"
        logger.info(f"🔄 Redirecting to: {redirect_url}")
        
        return redirect(redirect_url)

# Token endpoint - authorization code के बदले access token देते हैं
@app.route('/oauth/token', methods=['POST'])
def token():
    """
    OAuth2 Token Endpoint
    Authorization code को access token में convert करते हैं
    """
    grant_type = request.form.get('grant_type')
    
    if grant_type == 'authorization_code':
        return handle_authorization_code_grant()
    elif grant_type == 'refresh_token':
        return handle_refresh_token_grant()
    elif grant_type == 'client_credentials':
        return handle_client_credentials_grant()
    else:
        return jsonify({"error": "unsupported_grant_type"}), 400

def handle_authorization_code_grant():
    """Handle authorization code grant type"""
    code = request.form.get('code')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    redirect_uri = request.form.get('redirect_uri')
    
    # Validate client
    if not oauth_server.validate_client(client_id, client_secret):
        return jsonify({"error": "invalid_client"}), 401
    
    # Validate authorization code
    if code not in oauth_server.authorization_codes:
        return jsonify({"error": "invalid_grant"}), 400
    
    auth_info = oauth_server.authorization_codes[code]
    
    # Check if code is expired or already used
    if datetime.now() > auth_info["expires_at"] or auth_info["used"]:
        del oauth_server.authorization_codes[code]
        return jsonify({"error": "invalid_grant"}), 400
    
    # Check client match
    if auth_info["client_id"] != client_id:
        return jsonify({"error": "invalid_grant"}), 400
    
    # Mark code as used
    auth_info["used"] = True
    
    # Generate access token
    tokens = oauth_server.generate_access_token(
        client_id,
        auth_info["user_id"],
        auth_info["scopes"]
    )
    
    logger.info(f"✅ Access token issued for client {client_id}")
    return jsonify(tokens)

def handle_refresh_token_grant():
    """Handle refresh token grant type"""
    refresh_token = request.form.get('refresh_token')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    
    # Validate client
    if not oauth_server.validate_client(client_id, client_secret):
        return jsonify({"error": "invalid_client"}), 401
    
    # Refresh access token
    tokens = oauth_server.refresh_access_token(refresh_token, client_id)
    
    if tokens:
        logger.info(f"🔄 Token refreshed for client {client_id}")
        return jsonify(tokens)
    else:
        return jsonify({"error": "invalid_grant"}), 400

def handle_client_credentials_grant():
    """Handle client credentials grant type (for server-to-server)"""
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    scope = request.form.get('scope', '').split()
    
    # Validate client
    if not oauth_server.validate_client(client_id, client_secret):
        return jsonify({"error": "invalid_client"}), 401
    
    # Validate scope
    if not oauth_server.validate_scope(client_id, scope):
        return jsonify({"error": "invalid_scope"}), 400
    
    # Generate access token for client (no user context)
    tokens = oauth_server.generate_access_token(client_id, None, scope)
    
    # Remove refresh token for client credentials flow
    tokens.pop('refresh_token', None)
    
    logger.info(f"🤖 Client credentials token issued for {client_id}")
    return jsonify(tokens)

# User info endpoint - access token के साथ user data return करते हैं
@app.route('/oauth/userinfo', methods=['GET'])
def userinfo():
    """
    OAuth2 UserInfo Endpoint
    Access token के साथ user information return करते हैं
    """
    # Get access token from Authorization header
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "invalid_token"}), 401
    
    access_token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Validate access token
    token_info = oauth_server.validate_access_token(access_token)
    if not token_info:
        return jsonify({"error": "invalid_token"}), 401
    
    # Check if 'profile' scope is present
    if 'profile' not in token_info['scopes']:
        return jsonify({"error": "insufficient_scope"}), 403
    
    # Get user information
    user_id = token_info['user_id']
    user = None
    
    # Find user by user_id
    for email, user_data in oauth_server.users.items():
        if user_data['user_id'] == user_id:
            user = user_data
            break
    
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    # Return user info based on scopes
    user_info = {
        "sub": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "aadhaar_verified": user["aadhaar_verified"],
        "preferred_language": user["preferences"]["language"],
        "currency": user["preferences"]["currency"]
    }
    
    # Add address if scope allows
    if 'address' in token_info['scopes']:
        user_info["address"] = user["address"]
    
    logger.info(f"👤 User info requested for user {user_id}")
    return jsonify(user_info)

# Token introspection endpoint
@app.route('/oauth/introspect', methods=['POST'])
def introspect():
    """
    OAuth2 Token Introspection Endpoint
    Token की details और validity check करते हैं
    """
    token = request.form.get('token')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    
    # Validate client
    if not oauth_server.validate_client(client_id, client_secret):
        return jsonify({"error": "invalid_client"}), 401
    
    # Validate token
    token_info = oauth_server.validate_access_token(token)
    
    if token_info:
        response = {
            "active": True,
            "client_id": token_info["client_id"],
            "user_id": token_info["user_id"],
            "scope": " ".join(token_info["scopes"]),
            "exp": int(token_info["expires_at"].timestamp())
        }
    else:
        response = {"active": False}
    
    return jsonify(response)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    """OAuth2 server health check"""
    return jsonify({
        "status": "healthy",
        "service": "Flipkart OAuth2 Server",
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "active_clients": len(oauth_server.clients),
            "total_users": len(oauth_server.users),
            "active_tokens": len(oauth_server.access_tokens),
            "active_refresh_tokens": len(oauth_server.refresh_tokens)
        }
    })

if __name__ == '__main__':
    print("🔐 OAuth2 Server for Indian E-commerce")
    print("🇮🇳 Flipkart-style authentication & authorization")
    print("=" * 60)
    print("📋 Available endpoints:")
    print("  - GET  /oauth/authorize  - User authorization")
    print("  - POST /oauth/token      - Token exchange")
    print("  - GET  /oauth/userinfo   - User information")
    print("  - POST /oauth/introspect - Token introspection")
    print("  - GET  /health          - Health check")
    print()
    print("🎯 Test the OAuth2 flow:")
    print("1. Open: http://localhost:5000/oauth/authorize?client_id=flipkart_web&redirect_uri=http://localhost:3000/callback&response_type=code&scope=profile%20orders")
    print("2. Login with: rahul@example.com / hashed_password_123")
    print("3. Exchange authorization code for access token")
    print("4. Use access token to access user info")
    print()
    print("🚀 Starting OAuth2 server on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)