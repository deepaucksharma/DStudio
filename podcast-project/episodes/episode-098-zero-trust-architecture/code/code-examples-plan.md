# Episode 098: Zero Trust Architecture - Code Examples Plan

## Overview

This document outlines 15+ production-ready code examples for Zero Trust Architecture implementation, progressing from basic concepts to advanced enterprise patterns. All examples are designed to run in Indian enterprise contexts with appropriate cost considerations and regulatory compliance.

**Languages Used**: Python, Java, Go, TypeScript/JavaScript, YAML
**Focus**: Production-ready, testable, and documented code
**Context**: Indian banking, e-commerce, and enterprise environments

---

## Code Example 1: Basic Zero Trust Security Context
**File**: `basic_zt_context.py`
**Complexity**: Beginner
**Use Case**: Foundation security context for all Zero Trust decisions
**Indian Context**: Basic verification similar to building security guard

```python
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
import time

class TrustLevel(Enum):
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4

@dataclass
class SecurityContext:
    user_id: str
    device_id: str
    location: str
    network_type: str
    trust_level: TrustLevel
    risk_score: float
    last_verified: float
    session_data: Dict[str, any]
    
    def is_session_valid(self, max_age_seconds: int = 3600) -> bool:
        """Check if verification is still valid - like TC checking season pass"""
        current_time = time.time()
        return (current_time - self.last_verified) < max_age_seconds
    
    def requires_re_verification(self, risk_threshold: float = 0.5) -> bool:
        """Mumbai traffic police style - high risk needs more checking"""
        return self.risk_score > risk_threshold or not self.is_session_valid()
```

## Code Example 2: Multi-Factor Authentication System
**File**: `mfa_system.py`
**Complexity**: Beginner-Intermediate
**Use Case**: Banking-style MFA for Indian financial institutions
**Indian Context**: Multiple document verification like traffic police

```python
import hashlib
import random
import time
from typing import List, Dict, Optional
import qrcode
import pyotp

class MFASystem:
    """Multi-Factor Authentication system for Indian banking compliance"""
    
    def __init__(self):
        self.user_secrets = {}  # In production, use encrypted database
        self.otp_attempts = {}  # Rate limiting for OTP attempts
        
    def setup_user_mfa(self, user_id: str, phone_number: str) -> Dict[str, str]:
        """Setup MFA for user - like bank account opening process"""
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Store securely (in production, encrypt this)
        self.user_secrets[user_id] = {
            'totp_secret': secret,
            'phone_number': phone_number,
            'backup_codes': self._generate_backup_codes(),
            'setup_time': time.time()
        }
        
        # Generate QR code for mobile app
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name="IndianBank_ZeroTrust"
        )
        
        return {
            'secret': secret,
            'qr_code_uri': totp_uri,
            'backup_codes': self.user_secrets[user_id]['backup_codes']
        }
    
    def verify_mfa(self, user_id: str, otp_code: str, 
                   backup_code: Optional[str] = None) -> bool:
        """Verify MFA token - Indian banking style verification"""
        
        if user_id not in self.user_secrets:
            return False
        
        user_data = self.user_secrets[user_id]
        
        # Rate limiting - prevent brute force
        if self._is_rate_limited(user_id):
            raise Exception("Too many OTP attempts. Please wait 5 minutes.")
        
        # Verify TOTP code
        totp = pyotp.TOTP(user_data['totp_secret'])
        if totp.verify(otp_code, valid_window=1):  # 30-second window
            self._reset_attempts(user_id)
            return True
        
        # Verify backup code if TOTP fails
        if backup_code and backup_code in user_data['backup_codes']:
            # Remove used backup code
            user_data['backup_codes'].remove(backup_code)
            self._reset_attempts(user_id)
            return True
        
        # Track failed attempt
        self._track_failed_attempt(user_id)
        return False
    
    def send_sms_otp(self, user_id: str) -> str:
        """Send SMS OTP for high-risk transactions - Indian banking standard"""
        if user_id not in self.user_secrets:
            raise Exception("User not found")
        
        # Generate 6-digit OTP
        otp = f"{random.randint(100000, 999999)}"
        
        # Store OTP with expiration (5 minutes)
        self.user_secrets[user_id]['sms_otp'] = {
            'code': hashlib.sha256(otp.encode()).hexdigest(),
            'expires': time.time() + 300,  # 5 minutes
            'attempts': 0
        }
        
        # In production, integrate with SMS gateway
        phone = self.user_secrets[user_id]['phone_number']
        print(f"SMS OTP {otp} sent to {phone} (Demo only)")
        
        return otp  # Only for demo - never return in production
    
    def _generate_backup_codes(self) -> List[str]:
        """Generate backup codes for account recovery"""
        return [f"{random.randint(10000000, 99999999)}" for _ in range(10)]
    
    def _is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited"""
        if user_id not in self.otp_attempts:
            return False
        
        attempts = self.otp_attempts[user_id]
        return attempts['count'] >= 5 and (time.time() - attempts['last_attempt']) < 300
    
    def _track_failed_attempt(self, user_id: str):
        """Track failed OTP attempt"""
        current_time = time.time()
        if user_id not in self.otp_attempts:
            self.otp_attempts[user_id] = {'count': 1, 'last_attempt': current_time}
        else:
            self.otp_attempts[user_id]['count'] += 1
            self.otp_attempts[user_id]['last_attempt'] = current_time
    
    def _reset_attempts(self, user_id: str):
        """Reset failed attempt counter"""
        if user_id in self.otp_attempts:
            del self.otp_attempts[user_id]
```

## Code Example 3: Risk Assessment Engine
**File**: `risk_assessment.py`
**Complexity**: Intermediate
**Use Case**: Real-time risk scoring for Indian banking transactions
**Indian Context**: TC's experience-based risk assessment

```python
import time
import ipaddress
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class RiskFactors:
    location_risk: float
    device_risk: float
    behavioral_risk: float
    time_risk: float
    transaction_risk: float
    network_risk: float

class RiskAssessmentEngine:
    """Advanced risk assessment for Indian Zero Trust implementations"""
    
    def __init__(self):
        self.user_baselines = {}  # User behavior baselines
        self.trusted_networks = ['10.0.0.0/8', '192.168.0.0/16']  # Corporate networks
        self.high_risk_countries = ['CN', 'RU', 'KP']  # Example high-risk locations
        self.business_hours = (9, 17)  # 9 AM to 5 PM IST
        
    def calculate_comprehensive_risk(self, user_id: str, request_context: Dict) -> float:
        """Calculate comprehensive risk score like HDFC's 3000-parameter system"""
        
        factors = RiskFactors(
            location_risk=self._assess_location_risk(user_id, request_context.get('location')),
            device_risk=self._assess_device_risk(user_id, request_context.get('device_id')),
            behavioral_risk=self._assess_behavioral_risk(user_id, request_context),
            time_risk=self._assess_time_risk(),
            transaction_risk=self._assess_transaction_risk(request_context),
            network_risk=self._assess_network_risk(request_context.get('source_ip'))
        )
        
        # Weighted risk calculation (Indian banking standards)
        weights = {
            'location': 0.2,
            'device': 0.25,
            'behavioral': 0.3,
            'time': 0.1,
            'transaction': 0.1,
            'network': 0.05
        }
        
        total_risk = (
            factors.location_risk * weights['location'] +
            factors.device_risk * weights['device'] +
            factors.behavioral_risk * weights['behavioral'] +
            factors.time_risk * weights['time'] +
            factors.transaction_risk * weights['transaction'] +
            factors.network_risk * weights['network']
        )
        
        # Log risk calculation for audit (RBI compliance)
        self._log_risk_assessment(user_id, factors, total_risk, request_context)
        
        return min(max(total_risk, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _assess_location_risk(self, user_id: str, location: Optional[str]) -> float:
        """Assess location-based risk - Mumbai vs unknown location"""
        if not location:
            return 0.8  # High risk for unknown location
        
        # Get user's typical locations
        baseline = self.user_baselines.get(user_id, {})
        known_locations = baseline.get('locations', [])
        
        if location in known_locations:
            return 0.1  # Low risk for known location
        elif location in ['Mumbai', 'Delhi', 'Bangalore', 'Chennai']:
            return 0.3  # Medium risk for major Indian cities
        elif location in self.high_risk_countries:
            return 0.9  # High risk for suspicious countries
        else:
            return 0.6  # Medium-high risk for new locations
    
    def _assess_device_risk(self, user_id: str, device_id: Optional[str]) -> float:
        """Assess device risk - known vs unknown devices"""
        if not device_id:
            return 0.9  # Very high risk for unknown device
        
        baseline = self.user_baselines.get(user_id, {})
        trusted_devices = baseline.get('devices', [])
        
        if device_id in trusted_devices:
            return 0.1  # Low risk for trusted device
        else:
            return 0.7  # High risk for new device
    
    def _assess_behavioral_risk(self, user_id: str, context: Dict) -> float:
        """Behavioral analysis - like dabbawala recognizing patterns"""
        baseline = self.user_baselines.get(user_id, {})
        
        risk_score = 0.0
        
        # Check access patterns
        typical_hours = baseline.get('access_hours', [])
        current_hour = time.localtime().tm_hour
        
        if typical_hours and current_hour not in typical_hours:
            risk_score += 0.3  # Unusual time access
        
        # Check transaction patterns
        typical_amounts = baseline.get('transaction_amounts', [])
        requested_amount = context.get('amount', 0)
        
        if typical_amounts:
            avg_amount = sum(typical_amounts) / len(typical_amounts)
            if requested_amount > avg_amount * 5:  # 5x normal amount
                risk_score += 0.4  # High transaction amount risk
        
        # Check resource access patterns
        typical_resources = baseline.get('accessed_resources', [])
        requested_resource = context.get('resource')
        
        if requested_resource and requested_resource not in typical_resources:
            if 'admin' in requested_resource or 'sensitive' in requested_resource:
                risk_score += 0.5  # High risk for unusual admin access
            else:
                risk_score += 0.2  # Medium risk for new resource
        
        return min(risk_score, 1.0)
    
    def _assess_time_risk(self) -> float:
        """Time-based risk assessment - business hours vs off-hours"""
        current_hour = time.localtime().tm_hour
        
        if self.business_hours[0] <= current_hour <= self.business_hours[1]:
            return 0.1  # Low risk during business hours
        elif 6 <= current_hour <= 22:  # Extended hours
            return 0.3  # Medium risk
        else:  # Night hours
            return 0.7  # High risk
    
    def _assess_transaction_risk(self, context: Dict) -> float:
        """Transaction-specific risk assessment"""
        transaction_type = context.get('transaction_type', 'read')
        amount = context.get('amount', 0)
        
        risk = 0.0
        
        # Transaction type risk
        if transaction_type in ['transfer', 'payment', 'withdrawal']:
            risk += 0.3
        elif transaction_type in ['admin', 'delete', 'modify']:
            risk += 0.5
        
        # Amount-based risk (Indian banking thresholds)
        if amount > 200000:  # ₹2 lakhs - high value transaction
            risk += 0.4
        elif amount > 50000:  # ₹50k - medium value
            risk += 0.2
        
        return min(risk, 1.0)
    
    def _assess_network_risk(self, source_ip: Optional[str]) -> float:
        """Network-based risk assessment"""
        if not source_ip:
            return 0.8
        
        try:
            ip = ipaddress.ip_address(source_ip)
            
            # Check if IP is in trusted networks
            for trusted in self.trusted_networks:
                if ip in ipaddress.ip_network(trusted):
                    return 0.1  # Low risk for corporate network
            
            # Check for private IP ranges
            if ip.is_private:
                return 0.3  # Medium risk for private IPs
            
            # Public IP - higher risk
            return 0.6
            
        except ValueError:
            return 0.9  # Invalid IP - high risk
    
    def _log_risk_assessment(self, user_id: str, factors: RiskFactors, 
                           total_risk: float, context: Dict):
        """Log risk assessment for audit trail (RBI compliance)"""
        log_entry = {
            'timestamp': time.time(),
            'user_id': user_id,
            'risk_factors': {
                'location': factors.location_risk,
                'device': factors.device_risk,
                'behavioral': factors.behavioral_risk,
                'time': factors.time_risk,
                'transaction': factors.transaction_risk,
                'network': factors.network_risk
            },
            'total_risk': total_risk,
            'context': context
        }
        
        # In production, send to SIEM/logging system
        print(f"RISK_ASSESSMENT: {json.dumps(log_entry)}")
    
    def update_user_baseline(self, user_id: str, activity_data: Dict):
        """Update user behavior baseline - continuous learning"""
        if user_id not in self.user_baselines:
            self.user_baselines[user_id] = {
                'locations': [],
                'devices': [],
                'access_hours': [],
                'transaction_amounts': [],
                'accessed_resources': []
            }
        
        baseline = self.user_baselines[user_id]
        
        # Update location baseline
        location = activity_data.get('location')
        if location and location not in baseline['locations']:
            baseline['locations'].append(location)
        
        # Update device baseline
        device = activity_data.get('device_id')
        if device and device not in baseline['devices']:
            baseline['devices'].append(device)
        
        # Update time patterns
        hour = time.localtime().tm_hour
        if hour not in baseline['access_hours']:
            baseline['access_hours'].append(hour)
        
        # Keep only recent patterns (last 30 entries)
        for key in ['locations', 'devices', 'access_hours']:
            baseline[key] = baseline[key][-30:]
```

## Code Example 4: Zero Trust API Gateway
**File**: `zt_api_gateway.java`
**Complexity**: Intermediate
**Use Case**: ICICI Bank style API gateway for fintech partnerships
**Indian Context**: Multiple train lines coordination with security

```java
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ZeroTrustApiGateway {
    
    private Map<String, PartnerConfig> partnerConfigs;
    private Map<String, RateLimitTracker> rateLimits;
    private SecurityValidator securityValidator;
    private AuditLogger auditLogger;
    
    public ZeroTrustApiGateway() {
        this.partnerConfigs = new ConcurrentHashMap<>();
        this.rateLimits = new ConcurrentHashMap<>();
        this.securityValidator = new SecurityValidator();
        this.auditLogger = new AuditLogger();
        
        initializePartnerConfigs();
    }
    
    public ApiResponse processRequest(ApiRequest request) {
        String requestId = UUID.randomUUID().toString();
        long startTime = System.currentTimeMillis();
        
        try {
            // Step 1: Partner Authentication (OAuth 2.0)
            PartnerConfig partner = authenticatePartner(request);
            if (partner == null) {
                return createErrorResponse(401, "Invalid partner credentials");
            }
            
            // Step 2: Rate Limiting (Mumbai traffic control style)
            if (!checkRateLimit(partner.getPartnerId(), request)) {
                return createErrorResponse(429, "Rate limit exceeded");
            }
            
            // Step 3: Request Validation
            ValidationResult validation = securityValidator.validateRequest(request, partner);
            if (!validation.isValid()) {
                return createErrorResponse(400, validation.getErrorMessage());
            }
            
            // Step 4: Data Masking (PII protection)
            ApiRequest maskedRequest = applyDataMasking(request, partner);
            
            // Step 5: Process the actual request
            ApiResponse response = processBusinessLogic(maskedRequest, partner);
            
            // Step 6: Response filtering and masking
            ApiResponse filteredResponse = filterResponse(response, partner);
            
            // Step 7: Audit logging (RBI compliance)
            auditLogger.logApiAccess(requestId, partner, request, response, 
                                   System.currentTimeMillis() - startTime);
            
            return filteredResponse;
            
        } catch (Exception e) {
            auditLogger.logError(requestId, request, e);
            return createErrorResponse(500, "Internal server error");
        }
    }
    
    private PartnerConfig authenticatePartner(ApiRequest request) {
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return null;
        }
        
        String token = authHeader.substring(7);
        
        // Validate JWT token (simplified)
        try {
            Map<String, Object> claims = parseJwtToken(token);
            String partnerId = (String) claims.get("partner_id");
            String scope = (String) claims.get("scope");
            
            PartnerConfig config = partnerConfigs.get(partnerId);
            if (config != null && config.hasScope(scope)) {
                return config;
            }
        } catch (Exception e) {
            // Token validation failed
        }
        
        return null;
    }
    
    private boolean checkRateLimit(String partnerId, ApiRequest request) {
        String key = partnerId + ":" + request.getEndpoint();
        RateLimitTracker tracker = rateLimits.computeIfAbsent(key, 
            k -> new RateLimitTracker());
        
        PartnerConfig config = partnerConfigs.get(partnerId);
        int limit = config.getRateLimit(request.getEndpoint());
        
        return tracker.isAllowed(limit);
    }
    
    private ApiRequest applyDataMasking(ApiRequest request, PartnerConfig partner) {
        // Clone request for masking
        ApiRequest masked = request.clone();
        
        // Apply data masking based on partner permissions
        if (!partner.hasPermission("view_pii")) {
            masked.maskField("phone_number");
            masked.maskField("email");
            masked.maskField("address");
        }
        
        if (!partner.hasPermission("view_financial")) {
            masked.maskField("account_number");
            masked.maskField("balance");
            masked.maskField("transaction_history");
        }
        
        return masked;
    }
    
    private ApiResponse processBusinessLogic(ApiRequest request, PartnerConfig partner) {
        // Route to appropriate service based on endpoint
        switch (request.getEndpoint()) {
            case "/api/user/profile":
                return userService.getProfile(request);
            case "/api/account/balance":
                return accountService.getBalance(request);
            case "/api/transaction/history":
                return transactionService.getHistory(request);
            default:
                return createErrorResponse(404, "Endpoint not found");
        }
    }
    
    private void initializePartnerConfigs() {
        // Example: Fintech partner configuration
        partnerConfigs.put("fintech_partner_1", new PartnerConfig()
            .setPartnerId("fintech_partner_1")
            .setName("PaymentApp Pvt Ltd")
            .addScope("read:user_profile")
            .addScope("read:account_balance") 
            .addPermission("view_basic_info")
            .setRateLimit("/api/user/profile", 1000)  // 1000 requests per hour
            .setRateLimit("/api/account/balance", 500)
        );
        
        // Example: High-trust enterprise partner
        partnerConfigs.put("enterprise_partner_1", new PartnerConfig()
            .setPartnerId("enterprise_partner_1") 
            .setName("TechCorp Solutions")
            .addScope("read:user_profile")
            .addScope("write:user_profile")
            .addScope("read:transactions")
            .addPermission("view_pii")
            .addPermission("view_financial")
            .setRateLimit("/api/user/profile", 5000)
            .setRateLimit("/api/transaction/history", 2000)
        );
    }
}

class PartnerConfig {
    private String partnerId;
    private String name;
    private Set<String> scopes;
    private Set<String> permissions;
    private Map<String, Integer> rateLimits;
    
    public PartnerConfig() {
        this.scopes = new HashSet<>();
        this.permissions = new HashSet<>();
        this.rateLimits = new HashMap<>();
    }
    
    // Getters and fluent setters
    public String getPartnerId() { return partnerId; }
    public PartnerConfig setPartnerId(String partnerId) { 
        this.partnerId = partnerId; return this; 
    }
    
    public boolean hasScope(String scope) { return scopes.contains(scope); }
    public PartnerConfig addScope(String scope) { 
        scopes.add(scope); return this; 
    }
    
    public boolean hasPermission(String permission) { 
        return permissions.contains(permission); 
    }
    public PartnerConfig addPermission(String permission) { 
        permissions.add(permission); return this; 
    }
    
    public int getRateLimit(String endpoint) { 
        return rateLimits.getOrDefault(endpoint, 100); 
    }
    public PartnerConfig setRateLimit(String endpoint, int limit) { 
        rateLimits.put(endpoint, limit); return this; 
    }
}

class RateLimitTracker {
    private Queue<Long> requests;
    private final long WINDOW_SIZE = 3600000; // 1 hour in milliseconds
    
    public RateLimitTracker() {
        this.requests = new LinkedList<>();
    }
    
    public synchronized boolean isAllowed(int limit) {
        long now = System.currentTimeMillis();
        
        // Remove old requests outside the window
        while (!requests.isEmpty() && now - requests.peek() > WINDOW_SIZE) {
            requests.poll();
        }
        
        // Check if under limit
        if (requests.size() < limit) {
            requests.offer(now);
            return true;
        }
        
        return false;
    }
}
```

## Code Example 5: Service Mesh Security Configuration
**File**: `istio_zero_trust.yaml`
**Complexity**: Intermediate-Advanced
**Use Case**: Microservices security for Indian e-commerce platforms
**Indian Context**: Mumbai suburban train network coordination

```yaml
# Complete Istio Zero Trust Configuration for Indian E-commerce
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce-zt
  labels:
    istio-injection: enabled
    security-level: high
---
# Strict mTLS for all services
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default-mtls
  namespace: ecommerce-zt
spec:
  mtls:
    mode: STRICT
---
# JWT Authentication for customer-facing services
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: customer-jwt-auth
  namespace: ecommerce-zt
spec:
  selector:
    matchLabels:
      app: customer-api
  jwtRules:
  - issuer: "https://auth.indianecommerce.com"
    jwksUri: "https://auth.indianecommerce.com/.well-known/jwks.json"
    audiences:
    - "api.indianecommerce.com"
    - "mobile.indianecommerce.com"
    forwardOriginalToken: true
---
# Authorization policies for different service tiers
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: customer-service-authz
  namespace: ecommerce-zt
spec:
  selector:
    matchLabels:
      app: customer-service
  rules:
  # Allow customer API to access customer service
  - from:
    - source:
        principals: ["cluster.local/ns/ecommerce-zt/sa/customer-api"]
    to:
    - operation:
        methods: ["GET", "POST", "PUT"]
        paths: ["/customer/*"]
    when:
    - key: request.headers[x-user-id]
      values: ["*"]  # Must have user ID header
---
# Strict authorization for payment services
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service-authz
  namespace: ecommerce-zt
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
  # Only order service can access payment service
  - from:
    - source:
        principals: ["cluster.local/ns/ecommerce-zt/sa/order-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/payment/process", "/payment/verify"]
    when:
    - key: request.headers[x-transaction-id]
      values: ["*"]
    - key: request.headers[x-amount]
      values: ["*"]
    # Additional security for high-value transactions
  - from:
    - source:
        principals: ["cluster.local/ns/ecommerce-zt/sa/order-service"]
    to:
    - operation:
        methods: ["POST"] 
        paths: ["/payment/high-value"]
    when:
    - key: request.headers[x-approval-token]
      values: ["*"]  # Requires management approval
---
# Network policy for additional network-level security
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ecommerce-network-policy
  namespace: ecommerce-zt
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow ingress from istio-system (for sidecar injection)
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system
  # Allow customer API ingress from gateway
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system
    ports:
    - protocol: TCP
      port: 8080
  egress:
  # Allow egress to other services in same namespace
  - to:
    - namespaceSelector:
        matchLabels:
          name: ecommerce-zt
  # Allow egress to external payment gateways (Razorpay, etc.)
  - to: []
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
  # Allow DNS
  - to: []
    ports:
    - protocol: UDP
      port: 53
---
# Telemetry for security monitoring
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: security-metrics
  namespace: ecommerce-zt
spec:
  metrics:
  - providers:
    - name: prometheus
  - overrides:
    - match:
        metric: ALL_METRICS
      tagOverrides:
        user_id:
          value: "%{REQUEST_HEADERS:x-user-id | 'anonymous'}"
        transaction_type:
          value: "%{REQUEST_HEADERS:x-transaction-type | 'unknown'}"
        risk_score:
          value: "%{REQUEST_HEADERS:x-risk-score | '0'}"
---
# Security policies for different risk levels
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: risk-based-access
  namespace: ecommerce-zt
spec:
  selector:
    matchLabels:
      app: sensitive-service
  rules:
  # High trust users - minimal restrictions
  - from:
    - source:
        principals: ["cluster.local/ns/ecommerce-zt/sa/customer-api"]
    when:
    - key: request.headers[x-trust-level]
      values: ["HIGH", "VERIFIED"]
    - key: request.headers[x-risk-score]
      values: ["0.[0-2]*"]  # Risk score < 0.3
  # Medium trust users - time restrictions
  - from:
    - source:
        principals: ["cluster.local/ns/ecommerce-zt/sa/customer-api"]
    when:
    - key: request.headers[x-trust-level]
      values: ["MEDIUM"]
    - key: request.headers[x-time-hour]
      values: ["09", "10", "11", "12", "13", "14", "15", "16", "17"]  # Business hours
  # Low trust users - very restricted
  - from:
    - source:
        principals: ["cluster.local/ns/ecommerce-zt/sa/customer-api"]
    to:
    - operation:
        methods: ["GET"]  # Read-only
        paths: ["/public/*"]
    when:
    - key: request.headers[x-trust-level]
      values: ["LOW"]
```

## Code Example 6: Device Trust Manager
**File**: `device_trust_manager.go`
**Complexity**: Intermediate
**Use Case**: Device compliance checking for Indian enterprises
**Indian Context**: Vehicle registration and compliance checking

```go
package main

import (
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "fmt"
    "log"
    "time"
)

type DeviceTrustLevel int

const (
    Untrusted DeviceTrustLevel = iota
    New
    Verified
    Trusted
    Compromised
)

type DeviceInfo struct {
    DeviceID        string            `json:"device_id"`
    UserID          string            `json:"user_id"`
    DeviceType      string            `json:"device_type"`
    OS              string            `json:"os"`
    OSVersion       string            `json:"os_version"`
    AppVersion      string            `json:"app_version"`
    IsJailbroken    bool              `json:"is_jailbroken"`
    HasAntiVirus    bool              `json:"has_antivirus"`
    IsEncrypted     bool              `json:"is_encrypted"`
    LastSeen        time.Time         `json:"last_seen"`
    TrustLevel      DeviceTrustLevel  `json:"trust_level"`
    Attributes      map[string]string `json:"attributes"`
    ViolationCount  int               `json:"violation_count"`
}

type DeviceTrustManager struct {
    devices          map[string]*DeviceInfo
    compliancePolicies map[string]CompliancePolicy
}

type CompliancePolicy struct {
    RequireEncryption   bool     `json:"require_encryption"`
    RequireAntiVirus    bool     `json:"require_antivirus"`
    BlockJailbroken     bool     `json:"block_jailbroken"`
    AllowedOSVersions   []string `json:"allowed_os_versions"`
    MinAppVersion       string   `json:"min_app_version"`
    MaxDeviceAge        int      `json:"max_device_age_days"`
}

func NewDeviceTrustManager() *DeviceTrustManager {
    dtm := &DeviceTrustManager{
        devices:            make(map[string]*DeviceInfo),
        compliancePolicies: make(map[string]CompliancePolicy),
    }
    
    // Initialize compliance policies for different user types
    dtm.initializePolicies()
    return dtm
}

func (dtm *DeviceTrustManager) initializePolicies() {
    // Banking employee policy - strict compliance
    dtm.compliancePolicies["banking_employee"] = CompliancePolicy{
        RequireEncryption: true,
        RequireAntiVirus:  true,
        BlockJailbroken:   true,
        AllowedOSVersions: []string{"iOS 15+", "Android 11+"},
        MinAppVersion:     "2.1.0",
        MaxDeviceAge:      730, // 2 years
    }
    
    // Customer policy - balanced security and usability
    dtm.compliancePolicies["customer"] = CompliancePolicy{
        RequireEncryption: true,
        RequireAntiVirus:  false, // Not required for customers
        BlockJailbroken:   true,
        AllowedOSVersions: []string{"iOS 13+", "Android 9+"},
        MinAppVersion:     "2.0.0",
        MaxDeviceAge:      1460, // 4 years
    }
    
    // Partner/contractor policy - medium security
    dtm.compliancePolicies["partner"] = CompliancePolicy{
        RequireEncryption: true,
        RequireAntiVirus:  true,
        BlockJailbroken:   true,
        AllowedOSVersions: []string{"iOS 14+", "Android 10+"},
        MinAppVersion:     "2.0.5",
        MaxDeviceAge:      1095, // 3 years
    }
}

func (dtm *DeviceTrustManager) RegisterDevice(userID, userType string, deviceData map[string]interface{}) (*DeviceInfo, error) {
    // Generate device fingerprint
    deviceFingerprint := dtm.generateDeviceFingerprint(deviceData)
    
    // Check if device already exists
    if existingDevice, exists := dtm.devices[deviceFingerprint]; exists {
        log.Printf("Device %s already registered for user %s", deviceFingerprint, userID)
        return existingDevice, nil
    }
    
    // Create new device info
    device := &DeviceInfo{
        DeviceID:    deviceFingerprint,
        UserID:      userID,
        DeviceType:  dtm.getStringValue(deviceData, "device_type"),
        OS:          dtm.getStringValue(deviceData, "os"),
        OSVersion:   dtm.getStringValue(deviceData, "os_version"),
        AppVersion:  dtm.getStringValue(deviceData, "app_version"),
        IsJailbroken: dtm.getBoolValue(deviceData, "is_jailbroken"),
        HasAntiVirus: dtm.getBoolValue(deviceData, "has_antivirus"),
        IsEncrypted:  dtm.getBoolValue(deviceData, "is_encrypted"),
        LastSeen:     time.Now(),
        TrustLevel:   New, // Start with New trust level
        Attributes:   dtm.extractAttributes(deviceData),
        ViolationCount: 0,
    }
    
    // Assess initial compliance
    compliance := dtm.assessCompliance(device, userType)
    if !compliance.IsCompliant {
        device.TrustLevel = Untrusted
        log.Printf("Device %s failed compliance check: %s", deviceFingerprint, compliance.Reason)
    }
    
    // Store device
    dtm.devices[deviceFingerprint] = device
    
    log.Printf("Device registered: %s for user %s with trust level %v", 
               deviceFingerprint, userID, device.TrustLevel)
    
    return device, nil
}

func (dtm *DeviceTrustManager) AssessDeviceTrust(deviceFingerprint, userID, userType string) DeviceTrustLevel {
    device, exists := dtm.devices[deviceFingerprint]
    if !exists {
        log.Printf("Unknown device: %s", deviceFingerprint)
        return Untrusted
    }
    
    // Verify device belongs to user
    if device.UserID != userID {
        log.Printf("Device %s does not belong to user %s", deviceFingerprint, userID)
        return Untrusted
    }
    
    // Check for compromise indicators
    if dtm.isDeviceCompromised(device) {
        device.TrustLevel = Compromised
        log.Printf("Device %s marked as compromised", deviceFingerprint)
        return Compromised
    }
    
    // Assess current compliance
    compliance := dtm.assessCompliance(device, userType)
    if !compliance.IsCompliant {
        device.TrustLevel = Untrusted
        device.ViolationCount++
        log.Printf("Device %s compliance violation: %s", deviceFingerprint, compliance.Reason)
        return Untrusted
    }
    
    // Improve trust level over time with good behavior
    dtm.updateTrustLevel(device)
    
    // Update last seen
    device.LastSeen = time.Now()
    
    return device.TrustLevel
}

type ComplianceResult struct {
    IsCompliant bool   `json:"is_compliant"`
    Reason      string `json:"reason"`
    Score       float64 `json:"score"`
}

func (dtm *DeviceTrustManager) assessCompliance(device *DeviceInfo, userType string) ComplianceResult {
    policy, exists := dtm.compliancePolicies[userType]
    if !exists {
        return ComplianceResult{false, "Unknown user type", 0.0}
    }
    
    score := 1.0
    
    // Check encryption requirement
    if policy.RequireEncryption && !device.IsEncrypted {
        return ComplianceResult{false, "Device encryption required", 0.0}
    }
    
    // Check antivirus requirement
    if policy.RequireAntiVirus && !device.HasAntiVirus {
        return ComplianceResult{false, "Antivirus software required", 0.0}
    }
    
    // Check jailbreak/root status
    if policy.BlockJailbroken && device.IsJailbroken {
        return ComplianceResult{false, "Jailbroken/rooted devices not allowed", 0.0}
    }
    
    // Check OS version compliance
    if !dtm.isOSVersionAllowed(device.OS, device.OSVersion, policy.AllowedOSVersions) {
        return ComplianceResult{false, "OS version not supported", 0.5}
    }
    
    // Check app version
    if !dtm.isAppVersionValid(device.AppVersion, policy.MinAppVersion) {
        score -= 0.3
    }
    
    // Check device age (if we can determine it)
    deviceAge := dtm.estimateDeviceAge(device)
    if deviceAge > policy.MaxDeviceAge {
        score -= 0.2
    }
    
    isCompliant := score >= 0.7 // 70% compliance threshold
    reason := "Compliant"
    if !isCompliant {
        reason = "Compliance score below threshold"
    }
    
    return ComplianceResult{isCompliant, reason, score}
}

func (dtm *DeviceTrustManager) isDeviceCompromised(device *DeviceInfo) bool {
    // Check for compromise indicators
    
    // Too many compliance violations
    if device.ViolationCount > 5 {
        return true
    }
    
    // Device not seen for too long
    if time.Since(device.LastSeen) > 90*24*time.Hour { // 90 days
        return true
    }
    
    // Check for suspicious attributes
    if device.IsJailbroken {
        return true
    }
    
    // Check for suspicious app versions (too old or unknown)
    if device.AppVersion == "" || device.AppVersion == "unknown" {
        return true
    }
    
    return false
}

func (dtm *DeviceTrustManager) updateTrustLevel(device *DeviceInfo) {
    daysSinceRegistration := time.Since(device.LastSeen).Hours() / 24
    
    switch device.TrustLevel {
    case New:
        if daysSinceRegistration > 7 && device.ViolationCount == 0 {
            device.TrustLevel = Verified
        }
    case Verified:
        if daysSinceRegistration > 30 && device.ViolationCount == 0 {
            device.TrustLevel = Trusted
        }
    case Untrusted:
        if device.ViolationCount == 0 && daysSinceRegistration > 1 {
            device.TrustLevel = New // Give another chance
        }
    }
}

func (dtm *DeviceTrustManager) generateDeviceFingerprint(deviceData map[string]interface{}) string {
    // Combine device characteristics to create unique fingerprint
    fingerprint := fmt.Sprintf("%s_%s_%s_%s_%s",
        dtm.getStringValue(deviceData, "device_model"),
        dtm.getStringValue(deviceData, "os"),
        dtm.getStringValue(deviceData, "screen_resolution"),
        dtm.getStringValue(deviceData, "timezone"),
        dtm.getStringValue(deviceData, "language"),
    )
    
    hash := sha256.Sum256([]byte(fingerprint))
    return hex.EncodeToString(hash[:16]) // First 16 bytes for shorter ID
}

// Helper functions
func (dtm *DeviceTrustManager) getStringValue(data map[string]interface{}, key string) string {
    if val, ok := data[key]; ok {
        if str, ok := val.(string); ok {
            return str
        }
    }
    return ""
}

func (dtm *DeviceTrustManager) getBoolValue(data map[string]interface{}, key string) bool {
    if val, ok := data[key]; ok {
        if b, ok := val.(bool); ok {
            return b
        }
    }
    return false
}

func (dtm *DeviceTrustManager) extractAttributes(data map[string]interface{}) map[string]string {
    attributes := make(map[string]string)
    for key, value := range data {
        if str, ok := value.(string); ok {
            attributes[key] = str
        }
    }
    return attributes
}

func (dtm *DeviceTrustManager) isOSVersionAllowed(os, version string, allowed []string) bool {
    // Simplified version checking - in production use proper version comparison
    for _, allowedVersion := range allowed {
        if allowedVersion == fmt.Sprintf("%s %s", os, version) {
            return true
        }
    }
    return false
}

func (dtm *DeviceTrustManager) isAppVersionValid(current, minimum string) bool {
    // Simplified version checking
    return current >= minimum
}

func (dtm *DeviceTrustManager) estimateDeviceAge(device *DeviceInfo) int {
    // Simplified device age estimation
    // In production, use device model release dates
    return int(time.Since(device.LastSeen).Hours() / 24)
}

// Example usage
func main() {
    dtm := NewDeviceTrustManager()
    
    // Simulate device registration
    deviceData := map[string]interface{}{
        "device_model":      "iPhone 13",
        "os":               "iOS",
        "os_version":       "15.6",
        "app_version":      "2.1.0",
        "is_jailbroken":    false,
        "has_antivirus":    false, // iOS doesn't need antivirus
        "is_encrypted":     true,
        "screen_resolution": "1170x2532",
        "timezone":         "Asia/Kolkata",
        "language":         "en-IN",
    }
    
    device, err := dtm.RegisterDevice("user123", "customer", deviceData)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Device registered: %+v\n", device)
    
    // Assess trust level
    trustLevel := dtm.AssessDeviceTrust(device.DeviceID, "user123", "customer")
    fmt.Printf("Device trust level: %v\n", trustLevel)
}
```

## Additional Code Examples (7-15)

### Code Example 7: Zero Trust Network Policy Engine (`network_policy_engine.py`)
- Dynamic network segmentation
- Kubernetes NetworkPolicy generation
- Traffic flow analysis and anomaly detection

### Code Example 8: Behavioral Analytics Engine (`behavioral_analytics.ts`)
- User behavior profiling
- Anomaly detection algorithms
- Machine learning model integration

### Code Example 9: Certificate Management System (`cert_manager.java`)
- Automatic certificate provisioning
- mTLS certificate rotation
- PKI integration for device certificates

### Code Example 10: Zero Trust Monitoring Dashboard (`monitoring_dashboard.py`)
- Real-time security metrics
- Risk score visualization
- Compliance reporting for RBI

### Code Example 11: Identity Federation Gateway (`identity_federation.go`)
- SAML/OIDC integration
- Multi-provider authentication
- Token translation and validation

### Code Example 12: Data Classification Engine (`data_classifier.py`)
- Automatic data sensitivity classification
- PII detection and masking
- Compliance-based data handling

### Code Example 13: Zero Trust CLI Tool (`zt_cli.py`)
- Command-line interface for Zero Trust management
- Policy deployment and validation
- Security assessment automation

### Code Example 14: Serverless Zero Trust Functions (`serverless_zt.js`)
- AWS Lambda/Azure Functions security
- Function-level access control
- Event-driven security policies

### Code Example 15: Zero Trust Testing Framework (`zt_test_framework.py`)
- Security policy testing
- Penetration testing automation
- Compliance validation scripts

## Testing and Validation Strategy

### Unit Tests:
- Individual component testing
- Mock service integration
- Security policy validation

### Integration Tests:
- End-to-end authentication flows
- API gateway security testing
- Service mesh policy verification

### Performance Tests:
- Latency impact measurement
- Throughput under security constraints
- Scale testing for Indian enterprise loads

### Security Tests:
- Penetration testing scenarios
- Compliance validation
- Vulnerability assessment automation

## Indian Context Adaptations

### Regulatory Compliance:
- RBI cybersecurity framework alignment
- Data localization requirements
- Audit trail generation for Indian regulators

### Cultural Considerations:
- Hindi comments in critical sections
- Indian business hour configurations
- Local holiday and festival considerations

### Cost Optimization:
- Resource usage monitoring
- Cloud cost optimization for Indian markets
- Open-source alternative integration

This comprehensive code examples plan provides a complete toolkit for implementing Zero Trust Architecture in Indian enterprise environments, with appropriate cultural context, regulatory compliance, and cost considerations.