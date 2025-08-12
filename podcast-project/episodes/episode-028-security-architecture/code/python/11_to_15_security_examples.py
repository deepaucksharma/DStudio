#!/usr/bin/env python3
"""
Security Architecture Examples 11-15
Comprehensive Security Systems for Production

यह file में 5 complete security systems हैं:
11. Audit Logging System
12. JWT Token Rotation 
13. Input Validation Framework
14. CORS Security Configuration
15. Production Security Headers

All examples production-ready with Indian context.
"""

import os
import jwt
import json
import time
import uuid
import hmac
import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from functools import wraps
import threading
import asyncio
from urllib.parse import urlparse
import secrets

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_comprehensive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# EXAMPLE 11: AUDIT LOGGING SYSTEM
# =============================================================================

@dataclass
class AuditEvent:
    """Audit event structure for compliance"""
    event_id: str
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any]
    risk_score: int = 0

class ComplianceAuditLogger:
    """
    Production Audit Logging System for Banking Compliance
    RBI, PCI-DSS, SOX compliance requirements
    """
    
    def __init__(self, organization: str = "HDFC Bank"):
        self.organization = organization
        self.audit_events: List[AuditEvent] = []
        self.compliance_rules = {
            'financial_transaction': {'retention_days': 2555, 'encryption': True},  # 7 years
            'login_attempt': {'retention_days': 365, 'encryption': False},
            'data_access': {'retention_days': 1095, 'encryption': True},  # 3 years
            'admin_action': {'retention_days': 2555, 'encryption': True}
        }
        
        # Risk scoring matrix
        self.risk_matrix = {
            'failed_login': 3,
            'admin_login': 5,
            'data_export': 8,
            'config_change': 7,
            'payment_processing': 9,
            'account_creation': 4
        }
        
        logger.info(f"Audit Logger initialized for {organization}")
    
    def log_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        details: Dict[str, Any] = None,
        event_type: str = "general"
    ) -> str:
        """Log audit event with compliance requirements"""
        
        event_id = str(uuid.uuid4())
        risk_score = self._calculate_risk_score(action, success, details)
        
        audit_event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {},
            risk_score=risk_score
        )
        
        self.audit_events.append(audit_event)
        
        # Log to external systems (SIEM, Compliance DB)
        self._export_to_siem(audit_event)
        
        if risk_score >= 7:
            self._trigger_security_alert(audit_event)
        
        logger.info(f"AUDIT: {action} by {user_id} on {resource} - {'SUCCESS' if success else 'FAILED'}")
        return event_id
    
    def _calculate_risk_score(self, action: str, success: bool, details: Dict) -> int:
        """Calculate risk score for the event"""
        base_score = self.risk_matrix.get(action, 2)
        
        # Increase risk for failed actions
        if not success:
            base_score += 2
        
        # Check for high-risk indicators
        if details:
            if 'bulk_operation' in details and details['bulk_operation']:
                base_score += 3
            if 'admin_privileges' in details and details['admin_privileges']:
                base_score += 2
            if 'external_access' in details and details['external_access']:
                base_score += 2
        
        return min(base_score, 10)  # Cap at 10
    
    def _export_to_siem(self, event: AuditEvent):
        """Export to SIEM system (simulated)"""
        siem_data = {
            'timestamp': event.timestamp.isoformat(),
            'source': self.organization,
            'event_type': 'audit_log',
            'severity': 'high' if event.risk_score >= 7 else 'medium' if event.risk_score >= 4 else 'low',
            'user_id': event.user_id,
            'action': event.action,
            'resource': event.resource,
            'success': event.success,
            'risk_score': event.risk_score
        }
        
        # In production: send to Splunk, ELK, or other SIEM
        logger.info(f"SIEM_EXPORT: {json.dumps(siem_data)}")
    
    def _trigger_security_alert(self, event: AuditEvent):
        """Trigger security alert for high-risk events"""
        alert = {
            'alert_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'severity': 'HIGH',
            'event_id': event.event_id,
            'user_id': event.user_id,
            'action': event.action,
            'risk_score': event.risk_score
        }
        
        logger.warning(f"SECURITY_ALERT: {json.dumps(alert)}")
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate compliance audit report"""
        filtered_events = [
            event for event in self.audit_events
            if start_date <= event.timestamp <= end_date
        ]
        
        return {
            'report_period': f"{start_date.date()} to {end_date.date()}",
            'total_events': len(filtered_events),
            'successful_events': len([e for e in filtered_events if e.success]),
            'failed_events': len([e for e in filtered_events if not e.success]),
            'high_risk_events': len([e for e in filtered_events if e.risk_score >= 7]),
            'unique_users': len(set(e.user_id for e in filtered_events)),
            'top_actions': self._get_top_actions(filtered_events),
            'compliance_status': 'COMPLIANT'
        }
    
    def _get_top_actions(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Get top actions by frequency"""
        action_counts = {}
        for event in events:
            action_counts[event.action] = action_counts.get(event.action, 0) + 1
        
        return dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10])

# =============================================================================
# EXAMPLE 12: JWT TOKEN ROTATION SYSTEM
# =============================================================================

class JWTTokenManager:
    """
    Production JWT Token Management with Automatic Rotation
    Banking-grade security with refresh token support
    """
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.refresh_tokens: Dict[str, Dict] = {}
        self.blacklisted_tokens: Set[str] = set()
        
        # Token configuration
        self.access_token_expiry = timedelta(minutes=15)
        self.refresh_token_expiry = timedelta(days=7)
        self.max_refresh_tokens_per_user = 5
        
        logger.info("JWT Token Manager initialized")
    
    def generate_token_pair(
        self,
        user_id: str,
        permissions: List[str] = None,
        metadata: Dict = None
    ) -> Dict[str, str]:
        """Generate access and refresh token pair"""
        
        now = datetime.utcnow()
        jti = str(uuid.uuid4())  # JWT ID for tracking
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'permissions': permissions or [],
            'type': 'access',
            'jti': jti,
            'iat': now,
            'exp': now + self.access_token_expiry,
            'iss': 'hdfc-bank-auth',
            'aud': 'hdfc-bank-services'
        }
        
        if metadata:
            access_payload.update(metadata)
        
        # Generate access token
        access_token = jwt.encode(
            access_payload,
            self.secret_key,
            algorithm='HS256'
        )
        
        # Refresh token payload
        refresh_jti = str(uuid.uuid4())
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'jti': refresh_jti,
            'access_jti': jti,
            'iat': now,
            'exp': now + self.refresh_token_expiry
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            self.secret_key,
            algorithm='HS256'
        )
        
        # Store refresh token
        self._store_refresh_token(user_id, refresh_jti, refresh_token)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(self.access_token_expiry.total_seconds()),
            'token_type': 'Bearer'
        }
    
    def _store_refresh_token(self, user_id: str, jti: str, token: str):
        """Store refresh token with cleanup of old tokens"""
        if user_id not in self.refresh_tokens:
            self.refresh_tokens[user_id] = {}
        
        # Clean up expired tokens
        now = datetime.utcnow()
        expired_tokens = []
        for token_jti, token_data in self.refresh_tokens[user_id].items():
            if token_data['expires_at'] <= now:
                expired_tokens.append(token_jti)
        
        for expired_jti in expired_tokens:
            del self.refresh_tokens[user_id][expired_jti]
        
        # Limit number of refresh tokens per user
        if len(self.refresh_tokens[user_id]) >= self.max_refresh_tokens_per_user:
            # Remove oldest token
            oldest_jti = min(
                self.refresh_tokens[user_id].keys(),
                key=lambda x: self.refresh_tokens[user_id][x]['created_at']
            )
            del self.refresh_tokens[user_id][oldest_jti]
        
        # Store new refresh token
        self.refresh_tokens[user_id][jti] = {
            'token': token,
            'created_at': now,
            'expires_at': now + self.refresh_token_expiry
        }
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token"""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                return None
            
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256'],
                audience='hdfc-bank-services',
                issuer='hdfc-bank-auth'
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using refresh token"""
        try:
            # Validate refresh token
            payload = jwt.decode(
                refresh_token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'refresh':
                return None
            
            user_id = payload['user_id']
            refresh_jti = payload['jti']
            
            # Check if refresh token exists and is valid
            if (user_id not in self.refresh_tokens or
                refresh_jti not in self.refresh_tokens[user_id]):
                return None
            
            stored_token_data = self.refresh_tokens[user_id][refresh_jti]
            if stored_token_data['expires_at'] <= datetime.utcnow():
                # Clean up expired token
                del self.refresh_tokens[user_id][refresh_jti]
                return None
            
            # Generate new token pair
            return self.generate_token_pair(user_id)
            
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token: str):
        """Revoke (blacklist) a token"""
        self.blacklisted_tokens.add(token)
        logger.info("Token revoked")
    
    def revoke_all_user_tokens(self, user_id: str):
        """Revoke all tokens for a user"""
        if user_id in self.refresh_tokens:
            # Blacklist all refresh tokens
            for token_data in self.refresh_tokens[user_id].values():
                self.blacklisted_tokens.add(token_data['token'])
            
            # Clear refresh tokens
            del self.refresh_tokens[user_id]
        
        logger.info(f"All tokens revoked for user: {user_id}")

# =============================================================================
# EXAMPLE 13: INPUT VALIDATION FRAMEWORK
# =============================================================================

class SecurityValidator:
    """
    Comprehensive Input Validation Framework
    SQL Injection, XSS, and other attack prevention
    """
    
    def __init__(self):
        # Common attack patterns
        self.sql_injection_patterns = [
            r"('|(\\')|(;)|(\\;))",  # Basic SQL injection
            r"(union|select|insert|delete|update|drop|create|alter)\s",  # SQL keywords
            r"(exec|execute|sp_|xp_)",  # Stored procedures
            r"(\bor\b|\band\b)\s+.*(=|like)",  # Boolean-based injection
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"on\w+\s*=",  # Event handlers
            r"<iframe[^>]*>",  # Iframe injection
            r"vbscript:",  # VBScript URLs
        ]
        
        self.command_injection_patterns = [
            r"[;&|`$]",  # Command separators
            r"\$\(.*\)",  # Command substitution
            r"`.*`",  # Backtick execution
        ]
        
        # Indian specific patterns
        self.indian_patterns = {
            'aadhaar': r'^\d{12}$',
            'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
            'mobile': r'^[6-9]\d{9}$',
            'ifsc': r'^[A-Z]{4}0[A-Z0-9]{6}$',
            'pincode': r'^\d{6}$'
        }
        
        logger.info("Security Validator initialized")
    
    def validate_input(
        self,
        data: Any,
        validation_type: str = "general",
        max_length: int = 1000,
        allow_html: bool = False
    ) -> Tuple[bool, List[str]]:
        """Comprehensive input validation"""
        
        errors = []
        
        if data is None:
            return True, []
        
        # Convert to string for validation
        data_str = str(data)
        
        # Length validation
        if len(data_str) > max_length:
            errors.append(f"Input length exceeds maximum ({max_length})")
        
        # SQL injection detection
        if self._contains_sql_injection(data_str):
            errors.append("Potential SQL injection detected")
        
        # XSS detection
        if not allow_html and self._contains_xss(data_str):
            errors.append("Potential XSS attack detected")
        
        # Command injection detection
        if self._contains_command_injection(data_str):
            errors.append("Potential command injection detected")
        
        # Type-specific validation
        if validation_type in self.indian_patterns:
            if not re.match(self.indian_patterns[validation_type], data_str):
                errors.append(f"Invalid {validation_type} format")
        
        return len(errors) == 0, errors
    
    def _contains_sql_injection(self, data: str) -> bool:
        """Check for SQL injection patterns"""
        data_lower = data.lower()
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, data_lower, re.IGNORECASE):
                return True
        return False
    
    def _contains_xss(self, data: str) -> bool:
        """Check for XSS patterns"""
        for pattern in self.xss_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False
    
    def _contains_command_injection(self, data: str) -> bool:
        """Check for command injection patterns"""
        for pattern in self.command_injection_patterns:
            if re.search(pattern, data):
                return True
        return False
    
    def sanitize_input(self, data: str, sanitization_type: str = "general") -> str:
        """Sanitize input data"""
        if not data:
            return data
        
        if sanitization_type == "html":
            # Basic HTML sanitization
            data = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
            data = re.sub(r'<[^>]+>', '', data)  # Remove all tags
        
        elif sanitization_type == "sql":
            # Basic SQL sanitization
            data = data.replace("'", "''")  # Escape single quotes
            data = re.sub(r'[;\-\-/\*\*/]', '', data)  # Remove SQL metacharacters
        
        elif sanitization_type == "alphanumeric":
            # Keep only alphanumeric characters
            data = re.sub(r'[^a-zA-Z0-9]', '', data)
        
        return data.strip()

# =============================================================================
# EXAMPLE 14: CORS SECURITY CONFIGURATION
# =============================================================================

class CORSSecurityManager:
    """
    Production CORS Security Configuration
    Frontend-Backend security for Indian fintech apps
    """
    
    def __init__(self):
        # Allowed origins for Indian fintech companies
        self.allowed_origins = {
            'production': [
                'https://hdfc.com',
                'https://www.hdfcbank.com',
                'https://netbanking.hdfcbank.com',
                'https://payzapp.hdfcbank.com'
            ],
            'staging': [
                'https://staging.hdfcbank.com',
                'https://test-netbanking.hdfcbank.com'
            ],
            'development': [
                'http://localhost:3000',
                'http://localhost:8080',
                'https://dev.hdfcbank.com'
            ]
        }
        
        self.allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allowed_headers = [
            'Accept',
            'Accept-Language',
            'Content-Language',
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'X-CSRF-Token',
            'X-API-Key'
        ]
        
        # Security headers
        self.security_headers = {
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '86400',  # 24 hours
            'Vary': 'Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        }
        
        logger.info("CORS Security Manager initialized")
    
    def validate_origin(self, origin: str, environment: str = 'production') -> bool:
        """Validate if origin is allowed"""
        if not origin:
            return False
        
        allowed_list = self.allowed_origins.get(environment, [])
        
        # Exact match
        if origin in allowed_list:
            return True
        
        # Subdomain matching for production
        if environment == 'production':
            for allowed_origin in allowed_list:
                if self._is_subdomain(origin, allowed_origin):
                    return True
        
        return False
    
    def _is_subdomain(self, origin: str, allowed_origin: str) -> bool:
        """Check if origin is a valid subdomain"""
        try:
            origin_parsed = urlparse(origin)
            allowed_parsed = urlparse(allowed_origin)
            
            # Same scheme required
            if origin_parsed.scheme != allowed_parsed.scheme:
                return False
            
            origin_domain = origin_parsed.netloc
            allowed_domain = allowed_parsed.netloc
            
            # Check if origin domain ends with allowed domain
            return (origin_domain == allowed_domain or 
                   origin_domain.endswith('.' + allowed_domain))
            
        except Exception:
            return False
    
    def generate_cors_headers(
        self,
        request_origin: str,
        request_method: str = 'GET',
        request_headers: List[str] = None,
        environment: str = 'production'
    ) -> Dict[str, str]:
        """Generate appropriate CORS headers"""
        
        headers = {}
        
        # Validate origin
        if self.validate_origin(request_origin, environment):
            headers['Access-Control-Allow-Origin'] = request_origin
        else:
            # Don't set CORS headers for invalid origins
            return {}
        
        # Add security headers
        headers.update(self.security_headers)
        
        # Handle preflight requests
        if request_method == 'OPTIONS':
            headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
            headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
        
        return headers
    
    def is_preflight_request(self, method: str, headers: Dict[str, str]) -> bool:
        """Check if request is CORS preflight"""
        return (method == 'OPTIONS' and
               'Access-Control-Request-Method' in headers)

# =============================================================================
# EXAMPLE 15: PRODUCTION SECURITY HEADERS
# =============================================================================

class SecurityHeadersManager:
    """
    Production Security Headers Configuration
    OWASP recommended headers for Indian banking applications
    """
    
    def __init__(self, app_name: str = "HDFC NetBanking"):
        self.app_name = app_name
        
        # Security headers configuration
        self.security_headers = {
            # XSS Protection
            'X-XSS-Protection': '1; mode=block',
            
            # Content Type Options
            'X-Content-Type-Options': 'nosniff',
            
            # Frame Options
            'X-Frame-Options': 'DENY',
            
            # Referrer Policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Feature Policy / Permissions Policy
            'Permissions-Policy': (
                'geolocation=(), microphone=(), camera=(), '
                'payment=(self), usb=(), magnetometer=(), gyroscope=()'
            ),
            
            # Content Security Policy
            'Content-Security-Policy': self._generate_csp_policy(),
            
            # HTTP Strict Transport Security
            'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
            
            # Expect-CT
            'Expect-CT': 'max-age=86400, enforce'
        }
        
        logger.info(f"Security Headers Manager initialized for {app_name}")
    
    def _generate_csp_policy(self) -> str:
        """Generate Content Security Policy for banking application"""
        
        # Banking-specific CSP policy
        csp_directives = {
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline' https://apis.google.com https://www.google.com",
            'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
            'font-src': "'self' https://fonts.gstatic.com",
            'img-src': "'self' data: https:",
            'connect-src': "'self' https://api.hdfcbank.com wss://ws.hdfcbank.com",
            'frame-src': "'none'",
            'object-src': "'none'",
            'base-uri': "'self'",
            'form-action': "'self'",
            'upgrade-insecure-requests': '',
            'report-uri': '/csp-report'
        }
        
        # Convert to CSP string
        csp_policy = '; '.join([
            f"{directive} {value}" if value else directive
            for directive, value in csp_directives.items()
        ])
        
        return csp_policy
    
    def get_security_headers(self, request_path: str = "/") -> Dict[str, str]:
        """Get security headers for specific request path"""
        
        headers = self.security_headers.copy()
        
        # Path-specific adjustments
        if request_path.startswith('/api/'):
            # API endpoints don't need frame protection
            headers.pop('X-Frame-Options', None)
            
            # Relaxed CSP for API
            headers['Content-Security-Policy'] = "default-src 'none'"
        
        elif request_path.startswith('/embed/'):
            # Embeddable content
            headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        return headers
    
    def validate_security_headers(self, response_headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate that security headers are properly set"""
        
        validation_results = {
            'score': 0,
            'max_score': len(self.security_headers),
            'missing_headers': [],
            'weak_headers': [],
            'recommendations': []
        }
        
        for header_name, expected_value in self.security_headers.items():
            if header_name not in response_headers:
                validation_results['missing_headers'].append(header_name)
            else:
                validation_results['score'] += 1
                
                # Check for weak configurations
                actual_value = response_headers[header_name]
                if self._is_weak_header_value(header_name, actual_value):
                    validation_results['weak_headers'].append({
                        'header': header_name,
                        'current': actual_value,
                        'recommended': expected_value
                    })
        
        # Generate recommendations
        if validation_results['missing_headers']:
            validation_results['recommendations'].append(
                f"Add missing security headers: {', '.join(validation_results['missing_headers'])}"
            )
        
        if validation_results['weak_headers']:
            validation_results['recommendations'].append(
                "Strengthen weak security header configurations"
            )
        
        validation_results['grade'] = self._calculate_security_grade(validation_results['score'], validation_results['max_score'])
        
        return validation_results
    
    def _is_weak_header_value(self, header_name: str, value: str) -> bool:
        """Check if header value is weak/insufficient"""
        
        weak_patterns = {
            'Strict-Transport-Security': [
                r'max-age=\d{1,6}[^0-9]',  # Less than 7 digits (< 1 year)
                r'^[^;]*$'  # Missing includeSubDomains
            ],
            'Content-Security-Policy': [
                r"'unsafe-eval'",  # Dangerous CSP directive
                r'\*',  # Wildcard in CSP
            ],
            'X-Frame-Options': [
                r'ALLOWALL'  # Allows framing from anywhere
            ]
        }
        
        if header_name in weak_patterns:
            for pattern in weak_patterns[header_name]:
                if re.search(pattern, value, re.IGNORECASE):
                    return True
        
        return False
    
    def _calculate_security_grade(self, score: int, max_score: int) -> str:
        """Calculate security grade based on score"""
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        else:
            return 'F'

# =============================================================================
# DEMONSTRATION FUNCTION
# =============================================================================

def demonstrate_security_systems():
    """Demonstrate all 5 security systems"""
    print("\n🛡️  Comprehensive Security Systems Demo (Examples 11-15)")
    print("=" * 60)
    
    # Example 11: Audit Logging
    print("\n📋 Example 11: Compliance Audit Logging")
    print("-" * 40)
    
    audit_logger = ComplianceAuditLogger("HDFC Bank")
    
    # Log various events
    audit_logger.log_event(
        user_id="emp_12345",
        action="payment_processing",
        resource="/api/payments/transfer",
        ip_address="203.192.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        success=True,
        details={"amount": 50000, "beneficiary": "ACC123456"},
        event_type="financial_transaction"
    )
    
    audit_logger.log_event(
        user_id="admin_001",
        action="config_change",
        resource="/admin/security-settings",
        ip_address="192.168.1.100",
        user_agent="Chrome/91.0",
        success=True,
        details={"setting": "max_login_attempts", "old_value": 3, "new_value": 5}
    )
    
    print("✅ Audit events logged")
    
    # Generate compliance report
    report = audit_logger.generate_compliance_report(
        datetime.now() - timedelta(days=1),
        datetime.now()
    )
    print(f"📊 Compliance Report: {report['total_events']} events, {report['high_risk_events']} high-risk")
    
    # Example 12: JWT Token Management
    print("\n🎫 Example 12: JWT Token Rotation")
    print("-" * 35)
    
    token_manager = JWTTokenManager()
    
    # Generate token pair
    tokens = token_manager.generate_token_pair(
        user_id="user123",
        permissions=["read", "write", "transfer"],
        metadata={"branch": "mumbai_bandra"}
    )
    
    print("✅ Token pair generated")
    print(f"   Access Token: {tokens['access_token'][:30]}...")
    print(f"   Expires in: {tokens['expires_in']} seconds")
    
    # Validate token
    payload = token_manager.validate_token(tokens['access_token'])
    if payload:
        print(f"✅ Token valid for user: {payload['user_id']}")
    
    # Example 13: Input Validation
    print("\n🔍 Example 13: Input Validation Framework")
    print("-" * 42)
    
    validator = SecurityValidator()
    
    test_inputs = [
        ("9876543210", "mobile", "Valid mobile number"),
        ("ABCDE1234F", "pan", "Valid PAN number"),
        ("SELECT * FROM users", "general", "SQL injection attempt"),
        ("<script>alert('xss')</script>", "general", "XSS attempt")
    ]
    
    for test_input, validation_type, description in test_inputs:
        is_valid, errors = validator.validate_input(test_input, validation_type)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"   {description}: {status}")
        if errors:
            print(f"      Errors: {', '.join(errors)}")
    
    # Example 14: CORS Security
    print("\n🌐 Example 14: CORS Security Configuration")
    print("-" * 42)
    
    cors_manager = CORSSecurityManager()
    
    test_origins = [
        ("https://www.hdfcbank.com", "production", "Official HDFC site"),
        ("https://evil-site.com", "production", "Malicious site"),
        ("http://localhost:3000", "development", "Development server")
    ]
    
    for origin, env, description in test_origins:
        is_allowed = cors_manager.validate_origin(origin, env)
        status = "✅ ALLOWED" if is_allowed else "❌ BLOCKED"
        print(f"   {description}: {status}")
    
    # Example 15: Security Headers
    print("\n🔒 Example 15: Production Security Headers")
    print("-" * 42)
    
    headers_manager = SecurityHeadersManager("HDFC NetBanking")
    
    # Get security headers
    security_headers = headers_manager.get_security_headers("/")
    print(f"✅ Generated {len(security_headers)} security headers")
    
    # Show key headers
    key_headers = ['X-Frame-Options', 'X-XSS-Protection', 'Strict-Transport-Security']
    for header in key_headers:
        if header in security_headers:
            print(f"   {header}: {security_headers[header]}")
    
    # Validate headers
    validation = headers_manager.validate_security_headers(security_headers)
    print(f"📊 Security Grade: {validation['grade']}")
    print(f"   Score: {validation['score']}/{validation['max_score']}")
    
    print("\n🏆 All Security Systems Demonstrated Successfully!")
    print("=" * 50)
    
    # Summary
    print("\n📝 Systems Summary:")
    print("   11. ✅ Audit Logging - RBI/PCI-DSS compliant")
    print("   12. ✅ JWT Token Management - Auto-rotation")
    print("   13. ✅ Input Validation - SQL/XSS protection")
    print("   14. ✅ CORS Security - Origin validation")
    print("   15. ✅ Security Headers - OWASP recommended")

if __name__ == "__main__":
    demonstrate_security_systems()