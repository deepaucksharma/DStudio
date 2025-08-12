#!/usr/bin/env python3
"""
OAuth2 Implementation for DigiLocker-style Authentication
डिजिलॉकर स्टाइल authentication के लिए OAuth2 implementation

यह example दिखाता है कि कैसे भारतीय government services में
OAuth2 protocol implement करें secure document access के साथ।
"""

import time
import secrets
import hashlib
import base64
import jwt
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from urllib.parse import urlencode, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GrantType(Enum):
    """OAuth2 Grant Types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    PASSWORD = "password"  # Not recommended, only for legacy systems


class TokenType(Enum):
    """Token Types"""
    BEARER = "Bearer"
    MAC = "MAC"


@dataclass
class OAuthClient:
    """OAuth2 client application"""
    client_id: str
    client_secret: str
    client_name: str
    organization: str
    redirect_uris: List[str]
    scopes: List[str]
    grant_types: List[GrantType]
    is_government: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    # Indian-specific fields
    ministry: Optional[str] = None  # For government apps
    license_number: Optional[str] = None  # For private apps
    data_localization_compliant: bool = True


@dataclass
class DigiLockerUser:
    """DigiLocker user representation"""
    user_id: str
    aadhaar_number: str  # Masked for security
    mobile_number: str
    email: str
    name: str
    
    # Government document access
    pan_number: Optional[str] = None
    driving_license: Optional[str] = None
    passport_number: Optional[str] = None
    voter_id: Optional[str] = None
    
    # Account status
    is_verified: bool = True
    kyc_status: str = "VERIFIED"
    account_created: datetime = field(default_factory=datetime.now)
    last_login: datetime = field(default_factory=datetime.now)
    
    # Security preferences
    two_factor_enabled: bool = True
    allowed_devices: List[str] = field(default_factory=list)


@dataclass
class AuthorizationCode:
    """Authorization code for OAuth2 flow"""
    code: str
    client_id: str
    user_id: str
    redirect_uri: str
    scopes: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(minutes=10))
    is_used: bool = False


@dataclass
class AccessToken:
    """OAuth2 access token"""
    token: str
    client_id: str
    user_id: str
    scopes: List[str]
    token_type: TokenType = TokenType.BEARER
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # Indian compliance
    data_access_log: List[Dict] = field(default_factory=list)
    geographic_restriction: Optional[str] = "INDIA_ONLY"


@dataclass
class RefreshToken:
    """OAuth2 refresh token"""
    token: str
    client_id: str
    user_id: str
    scopes: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    is_revoked: bool = False


class DigiLockerOAuth2Server:
    """
    डिजिलॉकर-style OAuth2 authorization server
    भारतीय government services के लिए optimized
    """
    
    def __init__(self):
        # Storage (In production, use secure database)
        self.clients: Dict[str, OAuthClient] = {}
        self.users: Dict[str, DigiLockerUser] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        
        # JWT signing key (In production, use proper key management)
        self.jwt_secret = "digilocker_oauth2_secret_key_2024"
        
        # Initialize with sample data
        self._initialize_sample_data()
        
        logger.info("🔐 DigiLocker OAuth2 Server initialized")
    
    def _initialize_sample_data(self):
        """Initialize with sample Indian clients and users"""
        
        # Government clients
        govt_client = OAuthClient(
            client_id="GOV_INCOME_TAX_2024",
            client_secret=self._generate_client_secret(),
            client_name="Income Tax e-Filing Portal",
            organization="Central Board of Direct Taxes",
            redirect_uris=["https://incometax.gov.in/oauth/callback"],
            scopes=["profile", "documents", "pan_details", "aadhaar_basic"],
            grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.CLIENT_CREDENTIALS],
            is_government=True,
            ministry="Ministry of Finance",
            data_localization_compliant=True
        )
        
        bank_client = OAuthClient(
            client_id="SBI_DIGITAL_BANKING",
            client_secret=self._generate_client_secret(),
            client_name="SBI Digital Banking Platform", 
            organization="State Bank of India",
            redirect_uris=["https://onlinesbi.sbi/oauth/callback", "https://sbi.co.in/oauth/callback"],
            scopes=["profile", "kyc_documents", "income_proof"],
            grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
            license_number="RBI_LICENSE_SBI_2024",
            data_localization_compliant=True
        )
        
        # Private sector client
        insurance_client = OAuthClient(
            client_id="LIC_POLICY_PORTAL",
            client_secret=self._generate_client_secret(), 
            client_name="LIC Policy Management Portal",
            organization="Life Insurance Corporation of India",
            redirect_uris=["https://licindia.in/oauth/callback"],
            scopes=["profile", "age_proof", "address_proof", "income_documents"],
            grant_types=[GrantType.AUTHORIZATION_CODE],
            license_number="IRDAI_LICENSE_LIC_001",
            data_localization_compliant=True
        )
        
        self.clients.update({
            govt_client.client_id: govt_client,
            bank_client.client_id: bank_client,
            insurance_client.client_id: insurance_client
        })
        
        # Sample users
        user1 = DigiLockerUser(
            user_id="DL_USER_001",
            aadhaar_number="****-****-2345",  # Masked
            mobile_number="+91-98765-43210",
            email="raj.sharma@example.com", 
            name="राज शर्मा",
            pan_number="ABCDE1234F",
            driving_license="DL-12-20210001234",
            kyc_status="VERIFIED",
            two_factor_enabled=True
        )
        
        user2 = DigiLockerUser(
            user_id="DL_USER_002", 
            aadhaar_number="****-****-6789",  # Masked
            mobile_number="+91-87654-32109",
            email="priya.patel@example.com",
            name="प्रिया पटेल", 
            pan_number="FGHIJ5678K",
            voter_id="GHI1234567890",
            kyc_status="VERIFIED",
            two_factor_enabled=True
        )
        
        self.users.update({
            user1.user_id: user1,
            user2.user_id: user2
        })
        
        logger.info(f"📊 Initialized {len(self.clients)} clients and {len(self.users)} users")
    
    def _generate_client_secret(self) -> str:
        """Generate secure client secret"""
        return secrets.token_urlsafe(32)
    
    def _generate_authorization_code(self) -> str:
        """Generate authorization code"""
        return secrets.token_urlsafe(32)
    
    def _generate_access_token(self, client_id: str, user_id: str, scopes: List[str]) -> str:
        """Generate JWT access token"""
        payload = {
            'client_id': client_id,
            'user_id': user_id,
            'scopes': scopes,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iss': 'digilocker-oauth2',
            'aud': client_id,
            'jti': str(uuid.uuid4())  # JWT ID for token tracking
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def _generate_refresh_token(self) -> str:
        """Generate refresh token"""
        return secrets.token_urlsafe(64)
    
    def authorize(self, client_id: str, redirect_uri: str, scopes: List[str], 
                  state: str, response_type: str = "code") -> Dict:
        """
        OAuth2 authorization endpoint
        OAuth2 प्राधिकरण endpoint
        """
        logger.info(f"🔐 Authorization request: client={client_id}, scopes={scopes}")
        
        # Validate client
        client = self.clients.get(client_id)
        if not client:
            return {
                'error': 'invalid_client',
                'error_description': 'Client not found or invalid',
                'state': state
            }
        
        if not client.is_active:
            return {
                'error': 'client_inactive',
                'error_description': 'Client application is inactive',
                'state': state
            }
        
        # Validate redirect URI
        if redirect_uri not in client.redirect_uris:
            return {
                'error': 'invalid_redirect_uri',
                'error_description': 'Redirect URI not registered',
                'state': state
            }
        
        # Validate response type
        if response_type != "code":
            return {
                'error': 'unsupported_response_type',
                'error_description': 'Only authorization code flow is supported',
                'state': state
            }
        
        # Validate scopes
        invalid_scopes = set(scopes) - set(client.scopes)
        if invalid_scopes:
            return {
                'error': 'invalid_scope',
                'error_description': f'Invalid scopes: {invalid_scopes}',
                'state': state
            }
        
        # In a real implementation, this would show user consent screen
        # For demo, we'll assume user consent
        return {
            'consent_required': True,
            'client_info': {
                'name': client.client_name,
                'organization': client.organization,
                'is_government': client.is_government,
                'requested_scopes': scopes
            },
            'authorization_url': f"/oauth/consent?client_id={client_id}&state={state}"
        }
    
    def grant_authorization(self, client_id: str, user_id: str, redirect_uri: str, 
                          scopes: List[str], state: str) -> Dict:
        """
        Grant authorization after user consent
        उपयोगकर्ता की सहमति के बाद प्राधिकरण प्रदान करता है
        """
        
        # Validate user
        user = self.users.get(user_id)
        if not user:
            return {
                'error': 'invalid_user',
                'error_description': 'User not found or inactive'
            }
        
        if not user.is_verified:
            return {
                'error': 'user_not_verified',
                'error_description': 'User account not verified'
            }
        
        # Generate authorization code
        auth_code = self._generate_authorization_code()
        
        authorization = AuthorizationCode(
            code=auth_code,
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=scopes
        )
        
        self.authorization_codes[auth_code] = authorization
        
        # Log authorization for audit
        logger.info(f"✅ Authorization granted: user={user.name}, client={client_id}, scopes={scopes}")
        
        return {
            'success': True,
            'redirect_url': f"{redirect_uri}?code={auth_code}&state={state}",
            'authorization_code': auth_code  # For demo purposes
        }
    
    def exchange_code_for_tokens(self, client_id: str, client_secret: str, 
                               code: str, redirect_uri: str, grant_type: str = "authorization_code") -> Dict:
        """
        Exchange authorization code for access and refresh tokens
        प्राधिकरण कोड को access और refresh tokens के लिए बदलता है
        """
        
        # Validate grant type
        if grant_type != "authorization_code":
            return {
                'error': 'unsupported_grant_type',
                'error_description': 'Only authorization_code grant type is supported'
            }
        
        # Validate client credentials
        client = self.clients.get(client_id)
        if not client or client.client_secret != client_secret:
            return {
                'error': 'invalid_client',
                'error_description': 'Invalid client credentials'
            }
        
        # Validate authorization code
        auth_code_obj = self.authorization_codes.get(code)
        if not auth_code_obj:
            return {
                'error': 'invalid_grant',
                'error_description': 'Authorization code not found'
            }
        
        if auth_code_obj.is_used:
            return {
                'error': 'invalid_grant',
                'error_description': 'Authorization code already used'
            }
        
        if auth_code_obj.expires_at < datetime.now():
            return {
                'error': 'invalid_grant', 
                'error_description': 'Authorization code expired'
            }
        
        if auth_code_obj.client_id != client_id:
            return {
                'error': 'invalid_grant',
                'error_description': 'Authorization code issued to different client'
            }
        
        if auth_code_obj.redirect_uri != redirect_uri:
            return {
                'error': 'invalid_grant',
                'error_description': 'Redirect URI mismatch'
            }
        
        # Mark code as used
        auth_code_obj.is_used = True
        
        # Generate tokens
        access_token = self._generate_access_token(
            client_id, auth_code_obj.user_id, auth_code_obj.scopes
        )
        refresh_token = self._generate_refresh_token()
        
        # Store tokens
        access_token_obj = AccessToken(
            token=access_token,
            client_id=client_id,
            user_id=auth_code_obj.user_id,
            scopes=auth_code_obj.scopes
        )
        
        refresh_token_obj = RefreshToken(
            token=refresh_token,
            client_id=client_id,
            user_id=auth_code_obj.user_id,
            scopes=auth_code_obj.scopes
        )
        
        self.access_tokens[access_token] = access_token_obj
        self.refresh_tokens[refresh_token] = refresh_token_obj
        
        # Log token issuance
        user = self.users[auth_code_obj.user_id]
        logger.info(f"🎫 Tokens issued: user={user.name}, client={client.client_name}")
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,  # 1 hour
            'refresh_token': refresh_token,
            'scope': ' '.join(auth_code_obj.scopes),
            'user_info': {
                'user_id': auth_code_obj.user_id,
                'name': user.name,
                'verified': user.is_verified
            }
        }
    
    def refresh_access_token(self, client_id: str, client_secret: str, 
                           refresh_token: str, grant_type: str = "refresh_token") -> Dict:
        """
        Refresh access token using refresh token
        Refresh token का उपयोग करके access token को refresh करता है
        """
        
        if grant_type != "refresh_token":
            return {
                'error': 'unsupported_grant_type',
                'error_description': 'Invalid grant type'
            }
        
        # Validate client
        client = self.clients.get(client_id)
        if not client or client.client_secret != client_secret:
            return {
                'error': 'invalid_client',
                'error_description': 'Invalid client credentials'
            }
        
        # Validate refresh token
        refresh_token_obj = self.refresh_tokens.get(refresh_token)
        if not refresh_token_obj:
            return {
                'error': 'invalid_grant',
                'error_description': 'Refresh token not found'
            }
        
        if refresh_token_obj.is_revoked:
            return {
                'error': 'invalid_grant',
                'error_description': 'Refresh token revoked'
            }
        
        if refresh_token_obj.expires_at < datetime.now():
            return {
                'error': 'invalid_grant',
                'error_description': 'Refresh token expired'
            }
        
        if refresh_token_obj.client_id != client_id:
            return {
                'error': 'invalid_grant', 
                'error_description': 'Refresh token issued to different client'
            }
        
        # Generate new access token
        new_access_token = self._generate_access_token(
            client_id, refresh_token_obj.user_id, refresh_token_obj.scopes
        )
        
        # Store new access token
        access_token_obj = AccessToken(
            token=new_access_token,
            client_id=client_id,
            user_id=refresh_token_obj.user_id,
            scopes=refresh_token_obj.scopes
        )
        
        self.access_tokens[new_access_token] = access_token_obj
        
        logger.info(f"🔄 Access token refreshed for client {client.client_name}")
        
        return {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': ' '.join(refresh_token_obj.scopes)
        }
    
    def validate_access_token(self, access_token: str, required_scopes: Optional[List[str]] = None) -> Dict:
        """
        Validate access token and return user info
        Access token को validate करके user info return करता है
        """
        
        try:
            # Decode JWT token
            payload = jwt.decode(access_token, self.jwt_secret, algorithms=['HS256'])
            
            client_id = payload.get('client_id')
            user_id = payload.get('user_id')
            scopes = payload.get('scopes', [])
            
            # Check if token exists in our store
            token_obj = self.access_tokens.get(access_token)
            if not token_obj:
                return {
                    'valid': False,
                    'error': 'token_not_found',
                    'error_description': 'Access token not found in store'
                }
            
            # Check expiration
            if token_obj.expires_at < datetime.now():
                return {
                    'valid': False,
                    'error': 'token_expired',
                    'error_description': 'Access token has expired'
                }
            
            # Check required scopes
            if required_scopes:
                missing_scopes = set(required_scopes) - set(scopes)
                if missing_scopes:
                    return {
                        'valid': False,
                        'error': 'insufficient_scope',
                        'error_description': f'Missing required scopes: {missing_scopes}'
                    }
            
            # Get user and client info
            user = self.users.get(user_id)
            client = self.clients.get(client_id)
            
            if not user or not client:
                return {
                    'valid': False,
                    'error': 'invalid_token',
                    'error_description': 'Associated user or client not found'
                }
            
            # Log access for audit
            token_obj.data_access_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'token_validation',
                'client': client.client_name,
                'scopes': scopes
            })
            
            return {
                'valid': True,
                'user': {
                    'user_id': user.user_id,
                    'name': user.name,
                    'email': user.email,
                    'mobile': user.mobile_number,
                    'kyc_status': user.kyc_status,
                    'is_verified': user.is_verified
                },
                'client': {
                    'client_id': client.client_id,
                    'name': client.client_name,
                    'organization': client.organization,
                    'is_government': client.is_government
                },
                'scopes': scopes,
                'expires_in': int((token_obj.expires_at - datetime.now()).total_seconds())
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'token_expired',
                'error_description': 'JWT token has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'valid': False,
                'error': 'invalid_token',
                'error_description': 'Invalid JWT token'
            }
    
    def get_user_profile(self, access_token: str) -> Dict:
        """
        Get user profile using access token (requires 'profile' scope)
        Access token का उपयोग करके user profile प्राप्त करता है
        """
        
        validation = self.validate_access_token(access_token, ['profile'])
        
        if not validation['valid']:
            return validation
        
        user = self.users[validation['user']['user_id']]
        
        # Return profile information based on scopes
        scopes = validation['scopes']
        profile = {
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'mobile': user.mobile_number,
            'kyc_status': user.kyc_status,
            'account_created': user.account_created.isoformat(),
            'last_login': user.last_login.isoformat()
        }
        
        # Add sensitive information based on scopes
        if 'aadhaar_basic' in scopes:
            profile['aadhaar_masked'] = user.aadhaar_number
        
        if 'pan_details' in scopes and user.pan_number:
            profile['pan_number'] = user.pan_number
        
        if 'documents' in scopes:
            documents = []
            if user.driving_license:
                documents.append({'type': 'driving_license', 'number': user.driving_license})
            if user.voter_id:
                documents.append({'type': 'voter_id', 'number': user.voter_id})
            profile['documents'] = documents
        
        logger.info(f"👤 Profile accessed: {user.name} by {validation['client']['name']}")
        
        return {
            'success': True,
            'profile': profile,
            'scopes': scopes
        }
    
    def revoke_token(self, client_id: str, client_secret: str, token: str, 
                    token_type_hint: str = "access_token") -> Dict:
        """
        Revoke access or refresh token
        Access या refresh token को revoke करता है
        """
        
        # Validate client
        client = self.clients.get(client_id)
        if not client or client.client_secret != client_secret:
            return {
                'error': 'invalid_client',
                'error_description': 'Invalid client credentials'
            }
        
        # Try to revoke access token
        if token in self.access_tokens:
            del self.access_tokens[token]
            logger.info(f"🚫 Access token revoked for client {client.client_name}")
            return {'success': True, 'message': 'Access token revoked'}
        
        # Try to revoke refresh token
        if token in self.refresh_tokens:
            self.refresh_tokens[token].is_revoked = True
            logger.info(f"🚫 Refresh token revoked for client {client.client_name}")
            return {'success': True, 'message': 'Refresh token revoked'}
        
        # Token not found (still return success per OAuth2 spec)
        return {'success': True, 'message': 'Token not found or already revoked'}
    
    def get_server_stats(self) -> Dict:
        """Get OAuth2 server statistics"""
        
        active_access_tokens = len([t for t in self.access_tokens.values() 
                                   if t.expires_at > datetime.now()])
        active_refresh_tokens = len([t for t in self.refresh_tokens.values() 
                                    if not t.is_revoked and t.expires_at > datetime.now()])
        
        # Client type distribution
        govt_clients = len([c for c in self.clients.values() if c.is_government])
        private_clients = len(self.clients) - govt_clients
        
        return {
            'server_info': {
                'total_clients': len(self.clients),
                'government_clients': govt_clients,
                'private_clients': private_clients,
                'total_users': len(self.users),
                'verified_users': len([u for u in self.users.values() if u.is_verified])
            },
            'token_stats': {
                'active_access_tokens': active_access_tokens,
                'active_refresh_tokens': active_refresh_tokens,
                'authorization_codes_issued': len(self.authorization_codes),
                'used_authorization_codes': len([c for c in self.authorization_codes.values() if c.is_used])
            },
            'security_stats': {
                'two_factor_enabled_users': len([u for u in self.users.values() if u.two_factor_enabled]),
                'data_localization_compliant_clients': len([c for c in self.clients.values() if c.data_localization_compliant])
            }
        }


def demonstrate_oauth2_flow():
    """Demonstrate complete OAuth2 flow with Indian examples"""
    
    print("🔐 भारतीय डिजिटल सर्विसेज OAuth2 Implementation")
    print("=" * 70)
    
    # Initialize OAuth2 server
    oauth_server = DigiLockerOAuth2Server()
    
    # Step 1: Client requests authorization
    print("\n1️⃣ Step 1: Authorization Request")
    print("-" * 40)
    
    client_id = "SBI_DIGITAL_BANKING"
    redirect_uri = "https://onlinesbi.sbi/oauth/callback"
    scopes = ["profile", "kyc_documents", "income_proof"]
    state = "random_state_123"
    
    auth_response = oauth_server.authorize(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=scopes,
        state=state
    )
    
    if 'consent_required' in auth_response:
        client_info = auth_response['client_info']
        print(f"🏛️ Authorization requested by: {client_info['name']}")
        print(f"   Organization: {client_info['organization']}")
        print(f"   Government: {client_info['is_government']}")
        print(f"   Requested Scopes: {client_info['requested_scopes']}")
        
        # Step 2: User grants consent (simulated)
        print(f"\n2️⃣ Step 2: User Consent (Simulated)")
        print("-" * 40)
        
        user_id = "DL_USER_001"  # राज शर्मा
        
        grant_response = oauth_server.grant_authorization(
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            state=state
        )
        
        if grant_response['success']:
            auth_code = grant_response['authorization_code']
            print(f"✅ User consent granted")
            print(f"   Authorization Code: {auth_code[:16]}...")
            print(f"   Redirect URL: {grant_response['redirect_url'][:50]}...")
            
            # Step 3: Exchange code for tokens
            print(f"\n3️⃣ Step 3: Token Exchange")
            print("-" * 30)
            
            client_secret = oauth_server.clients[client_id].client_secret
            
            token_response = oauth_server.exchange_code_for_tokens(
                client_id=client_id,
                client_secret=client_secret,
                code=auth_code,
                redirect_uri=redirect_uri
            )
            
            if 'access_token' in token_response:
                access_token = token_response['access_token']
                refresh_token = token_response['refresh_token']
                
                print(f"✅ Tokens issued successfully")
                print(f"   Access Token: {access_token[:50]}...")
                print(f"   Refresh Token: {refresh_token[:32]}...")
                print(f"   Expires In: {token_response['expires_in']} seconds")
                print(f"   Scopes: {token_response['scope']}")
                
                # Step 4: Access protected resource
                print(f"\n4️⃣ Step 4: Access Protected Resource")
                print("-" * 45)
                
                profile_response = oauth_server.get_user_profile(access_token)
                
                if profile_response['success']:
                    profile = profile_response['profile']
                    print(f"👤 User Profile Retrieved:")
                    print(f"   Name: {profile['name']}")
                    print(f"   Email: {profile['email']}")
                    print(f"   Mobile: {profile['mobile']}")
                    print(f"   KYC Status: {profile['kyc_status']}")
                    
                    if 'pan_number' in profile:
                        print(f"   PAN: {profile['pan_number']}")
                    
                    if 'documents' in profile:
                        print(f"   Documents: {len(profile['documents'])} available")
                
                # Step 5: Refresh token
                print(f"\n5️⃣ Step 5: Token Refresh")
                print("-" * 30)
                
                refresh_response = oauth_server.refresh_access_token(
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=refresh_token
                )
                
                if 'access_token' in refresh_response:
                    new_access_token = refresh_response['access_token']
                    print(f"✅ Token refreshed successfully")
                    print(f"   New Access Token: {new_access_token[:50]}...")
                
                # Step 6: Token validation
                print(f"\n6️⃣ Step 6: Token Validation")
                print("-" * 35)
                
                validation_response = oauth_server.validate_access_token(
                    access_token=access_token,
                    required_scopes=['profile']
                )
                
                if validation_response['valid']:
                    print(f"✅ Token is valid")
                    print(f"   User: {validation_response['user']['name']}")
                    print(f"   Client: {validation_response['client']['name']}")
                    print(f"   Expires in: {validation_response['expires_in']} seconds")
                
                # Step 7: Token revocation
                print(f"\n7️⃣ Step 7: Token Revocation")
                print("-" * 35)
                
                revoke_response = oauth_server.revoke_token(
                    client_id=client_id,
                    client_secret=client_secret,
                    token=access_token
                )
                
                if revoke_response['success']:
                    print(f"✅ Token revoked successfully")
    
    # Display server statistics
    print(f"\n📊 OAuth2 Server Statistics:")
    print("=" * 40)
    
    stats = oauth_server.get_server_stats()
    
    print(f"Server Info:")
    server_info = stats['server_info']
    print(f"  Total Clients: {server_info['total_clients']}")
    print(f"  Government Clients: {server_info['government_clients']}")
    print(f"  Private Clients: {server_info['private_clients']}")
    print(f"  Total Users: {server_info['total_users']}")
    print(f"  Verified Users: {server_info['verified_users']}")
    
    print(f"\nToken Statistics:")
    token_stats = stats['token_stats']
    print(f"  Active Access Tokens: {token_stats['active_access_tokens']}")
    print(f"  Active Refresh Tokens: {token_stats['active_refresh_tokens']}")
    print(f"  Authorization Codes Issued: {token_stats['authorization_codes_issued']}")
    
    print(f"\nSecurity Statistics:")
    security_stats = stats['security_stats']
    print(f"  2FA Enabled Users: {security_stats['two_factor_enabled_users']}")
    print(f"  Data Localization Compliant: {security_stats['data_localization_compliant_clients']}")
    
    print(f"\n💡 Production Recommendations:")
    print("=" * 35)
    print("🔐 Implement PKCE for mobile applications")
    print("🛡️ Use hardware security modules (HSM) for key management")
    print("📊 Add comprehensive audit logging")
    print("⚡ Implement rate limiting and DDoS protection")
    print("🌍 Ensure GDPR and Indian data protection compliance")
    print("🔄 Implement token introspection for microservices")
    print("📱 Add device-based authentication for mobile apps")


if __name__ == "__main__":
    demonstrate_oauth2_flow()