#!/usr/bin/env python3
"""
Zero Trust Network Architecture for Banking
HDFC Bank, ICICI Bank, Axis Bank Production Security

यह system zero trust model implement करता है banking infrastructure के लिए।
Production में network segmentation, identity verification, और continuous monitoring।

Real-world Context:
- Indian banks lose ₹300 crore annually to cyber attacks
- RBI mandates zero trust for tier-1 banks by 2025
- Average breach detection time: 197 days
- Zero trust reduces breach cost by 44%
"""

import os
import jwt
import json
import time
import uuid
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import ipaddress
import asyncio
import aiohttp

# Setup logging for security monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zero_trust_security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrustLevel(Enum):
    """Trust levels for zero trust model"""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ResourceType(Enum):
    """Banking resource types"""
    CUSTOMER_DATA = "customer_data"
    TRANSACTION_API = "transaction_api"
    CORE_BANKING = "core_banking"
    PAYMENT_GATEWAY = "payment_gateway"
    COMPLIANCE_SYSTEM = "compliance_system"

@dataclass
class ZeroTrustPolicy:
    """Zero trust access policy"""
    policy_id: str
    resource_type: ResourceType
    required_trust_level: TrustLevel
    allowed_networks: List[str]
    required_factors: List[str]  # MFA requirements
    time_restrictions: Dict[str, str]
    compliance_requirements: List[str]
    
@dataclass
class AccessRequest:
    """Access request for zero trust evaluation"""
    request_id: str
    user_id: str
    resource: str
    resource_type: ResourceType
    client_ip: str
    device_id: str
    timestamp: datetime
    user_agent: str
    geolocation: Dict[str, Any]
    
@dataclass
class TrustScore:
    """Dynamic trust score calculation"""
    user_id: str
    base_score: int
    device_trust: int
    location_trust: int
    behavioral_trust: int
    time_trust: int
    network_trust: int
    final_score: int
    risk_factors: List[str]

class ZeroTrustEngine:
    """
    Production Zero Trust Engine for Banking
    
    Features:
    - Dynamic trust scoring
    - Continuous authentication
    - Network micro-segmentation
    - Device verification
    - Behavioral analysis
    - Compliance enforcement
    """
    
    def __init__(self, bank_code: str = "HDFC"):
        self.bank_code = bank_code
        self.policies: Dict[str, ZeroTrustPolicy] = {}
        self.trust_scores: Dict[str, TrustScore] = {}
        self.access_logs: List[Dict] = []
        
        # Initialize banking-specific configurations
        self.banking_config = self._load_banking_config()
        self.compliance_rules = self._load_compliance_rules()
        
        # JWT secret for token generation
        self.jwt_secret = os.getenv('JWT_SECRET', 'banking_zero_trust_2024')
        
        # Initialize default policies
        self._initialize_default_policies()
        
        logger.info(f"Zero Trust Engine initialized for {bank_code}")
    
    def _load_banking_config(self) -> Dict:
        """Load banking-specific configuration"""
        return {
            'HDFC': {
                'trusted_networks': ['203.192.0.0/16', '10.10.0.0/16'],
                'branch_networks': ['172.16.0.0/12'],
                'datacenter_networks': ['192.168.100.0/24'],
                'compliance_level': 'RBI_TIER1',
                'max_session_hours': 8,
                'require_hardware_token': True
            },
            'ICICI': {
                'trusted_networks': ['202.54.0.0/16', '10.20.0.0/16'],
                'branch_networks': ['172.20.0.0/12'],
                'datacenter_networks': ['192.168.200.0/24'],
                'compliance_level': 'RBI_TIER1',
                'max_session_hours': 8,
                'require_hardware_token': True
            },
            'AXIS': {
                'trusted_networks': ['115.242.0.0/16', '10.30.0.0/16'],
                'branch_networks': ['172.30.0.0/12'],
                'datacenter_networks': ['192.168.300.0/24'],
                'compliance_level': 'RBI_TIER1',
                'max_session_hours': 6,
                'require_hardware_token': True
            }
        }
    
    def _load_compliance_rules(self) -> Dict:
        """Load RBI and banking compliance rules"""
        return {
            'RBI_TIER1': {
                'min_password_length': 12,
                'require_mfa': True,
                'session_timeout_minutes': 15,
                'max_failed_attempts': 3,
                'require_device_registration': True,
                'audit_all_access': True,
                'encrypt_all_data': True
            },
            'PCI_DSS': {
                'card_data_access_log': True,
                'encrypt_card_numbers': True,
                'mask_sensitive_data': True,
                'require_dual_authorization': True
            },
            'NPCI_UPI': {
                'transaction_logging': True,
                'real_time_monitoring': True,
                'fraud_detection': True,
                'settlement_validation': True
            }
        }
    
    def _initialize_default_policies(self):
        """Initialize default zero trust policies"""
        
        # Customer data access policy
        self.add_policy(ZeroTrustPolicy(
            policy_id="CUSTOMER_DATA_ACCESS",
            resource_type=ResourceType.CUSTOMER_DATA,
            required_trust_level=TrustLevel.HIGH,
            allowed_networks=self.banking_config[self.bank_code]['trusted_networks'],
            required_factors=['password', 'otp', 'biometric'],
            time_restrictions={'start': '06:00', 'end': '22:00'},
            compliance_requirements=['RBI_TIER1', 'PCI_DSS']
        ))
        
        # Core banking system policy
        self.add_policy(ZeroTrustPolicy(
            policy_id="CORE_BANKING_ACCESS",
            resource_type=ResourceType.CORE_BANKING,
            required_trust_level=TrustLevel.CRITICAL,
            allowed_networks=self.banking_config[self.bank_code]['datacenter_networks'],
            required_factors=['password', 'hardware_token', 'biometric'],
            time_restrictions={'start': '00:00', 'end': '23:59'},
            compliance_requirements=['RBI_TIER1']
        ))
        
        # Payment gateway policy
        self.add_policy(ZeroTrustPolicy(
            policy_id="PAYMENT_GATEWAY_ACCESS",
            resource_type=ResourceType.PAYMENT_GATEWAY,
            required_trust_level=TrustLevel.HIGH,
            allowed_networks=self.banking_config[self.bank_code]['trusted_networks'],
            required_factors=['password', 'otp'],
            time_restrictions={'start': '05:00', 'end': '23:00'},
            compliance_requirements=['PCI_DSS', 'NPCI_UPI']
        ))
    
    def add_policy(self, policy: ZeroTrustPolicy):
        """Add new zero trust policy"""
        self.policies[policy.policy_id] = policy
        logger.info(f"Zero trust policy added: {policy.policy_id}")
    
    def calculate_trust_score(
        self, 
        user_id: str, 
        access_request: AccessRequest
    ) -> TrustScore:
        """
        Calculate dynamic trust score
        
        Factors considered:
        - User authentication history
        - Device trust level
        - Network location
        - Time-based patterns
        - Behavioral analysis
        """
        try:
            # Base score from user profile
            base_score = self._get_user_base_score(user_id)
            
            # Device trust score
            device_trust = self._calculate_device_trust(
                access_request.device_id, 
                user_id
            )
            
            # Network location trust
            location_trust = self._calculate_location_trust(
                access_request.client_ip,
                access_request.geolocation
            )
            
            # Behavioral patterns
            behavioral_trust = self._calculate_behavioral_trust(
                user_id,
                access_request
            )
            
            # Time-based trust
            time_trust = self._calculate_time_trust(
                access_request.timestamp,
                user_id
            )
            
            # Network trust
            network_trust = self._calculate_network_trust(
                access_request.client_ip
            )
            
            # Calculate final score (weighted average)
            weights = {
                'base': 0.3,
                'device': 0.2,
                'location': 0.15,
                'behavioral': 0.15,
                'time': 0.1,
                'network': 0.1
            }
            
            final_score = int(
                base_score * weights['base'] +
                device_trust * weights['device'] +
                location_trust * weights['location'] +
                behavioral_trust * weights['behavioral'] +
                time_trust * weights['time'] +
                network_trust * weights['network']
            )
            
            # Identify risk factors
            risk_factors = []
            if device_trust < 70: risk_factors.append("untrusted_device")
            if location_trust < 60: risk_factors.append("suspicious_location")
            if behavioral_trust < 50: risk_factors.append("abnormal_behavior")
            if network_trust < 80: risk_factors.append("unsecure_network")
            
            trust_score = TrustScore(
                user_id=user_id,
                base_score=base_score,
                device_trust=device_trust,
                location_trust=location_trust,
                behavioral_trust=behavioral_trust,
                time_trust=time_trust,
                network_trust=network_trust,
                final_score=final_score,
                risk_factors=risk_factors
            )
            
            # Cache the score
            self.trust_scores[user_id] = trust_score
            
            logger.info(f"Trust score calculated for {user_id}: {final_score}")
            return trust_score
            
        except Exception as e:
            logger.error(f"Trust score calculation failed: {e}")
            # Return low trust score on error
            return TrustScore(
                user_id=user_id,
                base_score=0, device_trust=0, location_trust=0,
                behavioral_trust=0, time_trust=0, network_trust=0,
                final_score=0, risk_factors=["calculation_error"]
            )
    
    def _get_user_base_score(self, user_id: str) -> int:
        """Get base trust score for user"""
        # In production, this would query user profile database
        user_profiles = {
            'bank_manager_001': 90,
            'cashier_mumbai_001': 80,
            'customer_service_001': 75,
            'it_admin_001': 85,
            'security_officer_001': 95,
            'external_auditor_001': 60
        }
        return user_profiles.get(user_id, 50)  # Default medium trust
    
    def _calculate_device_trust(self, device_id: str, user_id: str) -> int:
        """Calculate device trust score"""
        # Simulate device trust calculation
        registered_devices = {
            f"{user_id}_laptop": 90,
            f"{user_id}_mobile": 85,
            f"{user_id}_tablet": 75
        }
        
        base_device_trust = registered_devices.get(device_id, 30)
        
        # Factor in device security features
        security_features = self._get_device_security_features(device_id)
        if security_features.get('encrypted_storage'):
            base_device_trust += 10
        if security_features.get('biometric_enabled'):
            base_device_trust += 10
        if security_features.get('updated_os'):
            base_device_trust += 5
            
        return min(base_device_trust, 100)
    
    def _get_device_security_features(self, device_id: str) -> Dict:
        """Get device security features"""
        # In production, this would query device management system
        return {
            'encrypted_storage': True,
            'biometric_enabled': True,
            'updated_os': True,
            'antivirus_active': True,
            'firewall_enabled': True
        }
    
    def _calculate_location_trust(
        self, 
        client_ip: str, 
        geolocation: Dict
    ) -> int:
        """Calculate location-based trust"""
        try:
            # Check if IP is in trusted networks
            client_ip_obj = ipaddress.ip_address(client_ip)
            
            # Bank internal networks = highest trust
            for network in self.banking_config[self.bank_code]['trusted_networks']:
                if client_ip_obj in ipaddress.ip_network(network):
                    return 100
            
            # Branch networks = high trust
            for network in self.banking_config[self.bank_code]['branch_networks']:
                if client_ip_obj in ipaddress.ip_network(network):
                    return 90
            
            # Check geolocation
            if geolocation:
                country = geolocation.get('country', '').upper()
                if country == 'IN':  # India
                    return 80
                elif country in ['US', 'UK', 'SG']:  # Trusted countries
                    return 60
                else:
                    return 30
            
            return 40  # Unknown location
            
        except Exception:
            return 20  # Invalid IP
    
    def _calculate_behavioral_trust(
        self, 
        user_id: str, 
        access_request: AccessRequest
    ) -> int:
        """Calculate behavioral trust score"""
        # In production, this would analyze user behavior patterns
        
        # Simulate behavioral analysis
        current_hour = access_request.timestamp.hour
        
        # Check if access is during usual hours
        usual_hours = self._get_user_usual_hours(user_id)
        if usual_hours['start'] <= current_hour <= usual_hours['end']:
            time_score = 90
        else:
            time_score = 40
        
        # Check access frequency
        recent_access_count = self._get_recent_access_count(user_id)
        if recent_access_count > 50:  # Too frequent
            frequency_score = 30
        elif recent_access_count < 5:  # Too rare
            frequency_score = 60
        else:
            frequency_score = 85
        
        # Resource access patterns
        resource_pattern_score = self._check_resource_access_pattern(
            user_id, 
            access_request.resource_type
        )
        
        return int((time_score + frequency_score + resource_pattern_score) / 3)
    
    def _get_user_usual_hours(self, user_id: str) -> Dict:
        """Get user's usual working hours"""
        # Simulate user working patterns
        patterns = {
            'bank_manager_001': {'start': 9, 'end': 18},
            'cashier_mumbai_001': {'start': 10, 'end': 17},
            'it_admin_001': {'start': 8, 'end': 20},
            'security_officer_001': {'start': 0, 'end': 23}
        }
        return patterns.get(user_id, {'start': 9, 'end': 17})
    
    def _get_recent_access_count(self, user_id: str) -> int:
        """Get recent access count for user"""
        # Count accesses in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        count = sum(1 for log in self.access_logs 
                   if log.get('user_id') == user_id and 
                   datetime.fromisoformat(log.get('timestamp', '')) > one_hour_ago)
        return count
    
    def _check_resource_access_pattern(
        self, 
        user_id: str, 
        resource_type: ResourceType
    ) -> int:
        """Check if resource access matches user role"""
        # Role-based resource access patterns
        role_patterns = {
            'bank_manager_001': [ResourceType.CUSTOMER_DATA, ResourceType.CORE_BANKING],
            'cashier_mumbai_001': [ResourceType.CUSTOMER_DATA, ResourceType.TRANSACTION_API],
            'it_admin_001': [ResourceType.CORE_BANKING, ResourceType.COMPLIANCE_SYSTEM],
            'security_officer_001': [ResourceType.COMPLIANCE_SYSTEM]
        }
        
        allowed_resources = role_patterns.get(user_id, [])
        if resource_type in allowed_resources:
            return 90
        else:
            return 30
    
    def _calculate_time_trust(self, timestamp: datetime, user_id: str) -> int:
        """Calculate time-based trust"""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Business hours boost
        if 9 <= hour <= 18 and day_of_week < 5:  # Weekday business hours
            return 90
        elif 6 <= hour <= 22:  # Extended hours
            return 70
        else:  # Night hours
            return 30
    
    def _calculate_network_trust(self, client_ip: str) -> int:
        """Calculate network security trust"""
        try:
            # Check against threat intelligence
            if self._is_malicious_ip(client_ip):
                return 0
            
            # Check if VPN/Proxy
            if self._is_proxy_ip(client_ip):
                return 40
            
            # Check network reputation
            reputation = self._get_ip_reputation(client_ip)
            return reputation
            
        except Exception:
            return 50
    
    def _is_malicious_ip(self, ip: str) -> bool:
        """Check if IP is in threat intelligence feeds"""
        # Simulate threat intelligence check
        malicious_ips = {'192.0.2.1', '198.51.100.1', '203.0.113.1'}
        return ip in malicious_ips
    
    def _is_proxy_ip(self, ip: str) -> bool:
        """Check if IP is a proxy/VPN"""
        # Simulate proxy detection
        proxy_ranges = ['10.0.0.0/8', '172.16.0.0/12']
        try:
            client_ip = ipaddress.ip_address(ip)
            for proxy_range in proxy_ranges:
                if client_ip in ipaddress.ip_network(proxy_range):
                    return True
        except Exception:
            pass
        return False
    
    def _get_ip_reputation(self, ip: str) -> int:
        """Get IP reputation score"""
        # Simulate reputation scoring
        return 80  # Default good reputation
    
    def evaluate_access_request(self, access_request: AccessRequest) -> Tuple[bool, str, Dict]:
        """
        Evaluate zero trust access request
        
        Returns:
            (is_allowed, reason, metadata)
        """
        try:
            # Calculate trust score
            trust_score = self.calculate_trust_score(
                access_request.user_id,
                access_request
            )
            
            # Get applicable policy
            policy = self._get_policy_for_resource(access_request.resource_type)
            if not policy:
                return False, "NO_POLICY_FOUND", {}
            
            # Check minimum trust level
            required_score = self._trust_level_to_score(policy.required_trust_level)
            if trust_score.final_score < required_score:
                self._log_access_attempt(access_request, False, "INSUFFICIENT_TRUST_SCORE")
                return False, "INSUFFICIENT_TRUST_SCORE", {
                    'required': required_score,
                    'actual': trust_score.final_score,
                    'risk_factors': trust_score.risk_factors
                }
            
            # Check network restrictions
            if not self._check_network_policy(access_request.client_ip, policy):
                self._log_access_attempt(access_request, False, "NETWORK_VIOLATION")
                return False, "NETWORK_VIOLATION", {}
            
            # Check time restrictions
            if not self._check_time_policy(access_request.timestamp, policy):
                self._log_access_attempt(access_request, False, "TIME_VIOLATION")
                return False, "TIME_VIOLATION", {}
            
            # Generate access token
            access_token = self._generate_access_token(
                access_request.user_id,
                access_request.resource,
                trust_score.final_score
            )
            
            self._log_access_attempt(access_request, True, "ACCESS_GRANTED")
            
            return True, "ACCESS_GRANTED", {
                'trust_score': trust_score.final_score,
                'access_token': access_token,
                'expires_in': 3600  # 1 hour
            }
            
        except Exception as e:
            logger.error(f"Access evaluation failed: {e}")
            return False, "EVALUATION_ERROR", {'error': str(e)}
    
    def _get_policy_for_resource(self, resource_type: ResourceType) -> Optional[ZeroTrustPolicy]:
        """Get policy for resource type"""
        for policy in self.policies.values():
            if policy.resource_type == resource_type:
                return policy
        return None
    
    def _trust_level_to_score(self, trust_level: TrustLevel) -> int:
        """Convert trust level to numeric score"""
        mapping = {
            TrustLevel.UNTRUSTED: 0,
            TrustLevel.LOW: 40,
            TrustLevel.MEDIUM: 60,
            TrustLevel.HIGH: 80,
            TrustLevel.CRITICAL: 95
        }
        return mapping[trust_level]
    
    def _check_network_policy(self, client_ip: str, policy: ZeroTrustPolicy) -> bool:
        """Check if client IP meets network policy"""
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            for allowed_network in policy.allowed_networks:
                if client_ip_obj in ipaddress.ip_network(allowed_network):
                    return True
            return False
        except Exception:
            return False
    
    def _check_time_policy(self, timestamp: datetime, policy: ZeroTrustPolicy) -> bool:
        """Check if access time meets policy"""
        if not policy.time_restrictions:
            return True
        
        current_time = timestamp.time()
        start_time = datetime.strptime(
            policy.time_restrictions['start'], 
            '%H:%M'
        ).time()
        end_time = datetime.strptime(
            policy.time_restrictions['end'], 
            '%H:%M'
        ).time()
        
        return start_time <= current_time <= end_time
    
    def _generate_access_token(
        self, 
        user_id: str, 
        resource: str, 
        trust_score: int
    ) -> str:
        """Generate JWT access token"""
        payload = {
            'user_id': user_id,
            'resource': resource,
            'trust_score': trust_score,
            'issued_at': datetime.now().timestamp(),
            'expires_at': (datetime.now() + timedelta(hours=1)).timestamp(),
            'bank_code': self.bank_code
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def _log_access_attempt(
        self, 
        access_request: AccessRequest, 
        granted: bool, 
        reason: str
    ):
        """Log access attempt for audit"""
        log_entry = {
            'request_id': access_request.request_id,
            'user_id': access_request.user_id,
            'resource': access_request.resource,
            'client_ip': access_request.client_ip,
            'granted': granted,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        self.access_logs.append(log_entry)
        logger.info(f"Access {'GRANTED' if granted else 'DENIED'}: {access_request.user_id} → {access_request.resource}")

def demonstrate_zero_trust_banking():
    """
    Demonstrate zero trust architecture for Indian banking
    HDFC, ICICI, Axis Bank production scenarios
    """
    print("\n🛡️  Zero Trust Banking Architecture Demo")
    print("=" * 45)
    
    # Initialize zero trust engines for different banks
    hdfc_zt = ZeroTrustEngine("HDFC")
    icici_zt = ZeroTrustEngine("ICICI")
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Branch Manager - Customer Data Access',
            'request': AccessRequest(
                request_id=str(uuid.uuid4()),
                user_id='bank_manager_001',
                resource='/api/customer/profile/12345',
                resource_type=ResourceType.CUSTOMER_DATA,
                client_ip='203.192.1.100',  # HDFC network
                device_id='bank_manager_001_laptop',
                timestamp=datetime.now().replace(hour=14),
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                geolocation={'country': 'IN', 'city': 'Mumbai', 'state': 'MH'}
            )
        },
        {
            'name': 'External Access - Suspicious',
            'request': AccessRequest(
                request_id=str(uuid.uuid4()),
                user_id='cashier_mumbai_001',
                resource='/api/core-banking/transfer',
                resource_type=ResourceType.CORE_BANKING,
                client_ip='198.51.100.10',  # External IP
                device_id='unknown_device_001',
                timestamp=datetime.now().replace(hour=2),  # 2 AM
                user_agent='curl/7.68.0',
                geolocation={'country': 'US', 'city': 'Unknown'}
            )
        },
        {
            'name': 'IT Admin - System Access',
            'request': AccessRequest(
                request_id=str(uuid.uuid4()),
                user_id='it_admin_001',
                resource='/api/compliance/audit-logs',
                resource_type=ResourceType.COMPLIANCE_SYSTEM,
                client_ip='192.168.100.50',  # Datacenter
                device_id='it_admin_001_laptop',
                timestamp=datetime.now().replace(hour=16),
                user_agent='Mozilla/5.0 (Linux; Ubuntu)',
                geolocation={'country': 'IN', 'city': 'Bangalore'}
            )
        }
    ]
    
    print("\n📊 Zero Trust Access Evaluations")
    print("-" * 40)
    
    for scenario in test_scenarios:
        print(f"\n🔍 Scenario: {scenario['name']}")
        print(f"   User: {scenario['request'].user_id}")
        print(f"   Resource: {scenario['request'].resource_type.value}")
        print(f"   IP: {scenario['request'].client_ip}")
        print(f"   Time: {scenario['request'].timestamp.strftime('%H:%M')}")
        
        # Evaluate with HDFC zero trust
        allowed, reason, metadata = hdfc_zt.evaluate_access_request(scenario['request'])
        
        if allowed:
            print(f"   ✅ Result: ACCESS GRANTED")
            print(f"   🔑 Trust Score: {metadata.get('trust_score', 0)}")
            print(f"   🎫 Token: {metadata.get('access_token', '')[:30]}...")
        else:
            print(f"   ❌ Result: ACCESS DENIED")
            print(f"   📝 Reason: {reason}")
            if 'risk_factors' in metadata:
                print(f"   ⚠️  Risk Factors: {', '.join(metadata['risk_factors'])}")
    
    # Trust score breakdown
    print(f"\n📈 Trust Score Breakdown")
    print("-" * 30)
    
    sample_user = 'bank_manager_001'
    if sample_user in hdfc_zt.trust_scores:
        ts = hdfc_zt.trust_scores[sample_user]
        print(f"User: {sample_user}")
        print(f"   Base Score: {ts.base_score}")
        print(f"   Device Trust: {ts.device_trust}")
        print(f"   Location Trust: {ts.location_trust}")
        print(f"   Behavioral Trust: {ts.behavioral_trust}")
        print(f"   Time Trust: {ts.time_trust}")
        print(f"   Network Trust: {ts.network_trust}")
        print(f"   Final Score: {ts.final_score}")
    
    # Audit trail
    print(f"\n📋 Recent Access Audit Trail")
    print("-" * 35)
    
    for i, log in enumerate(hdfc_zt.access_logs[-5:], 1):
        status = "✅ GRANTED" if log['granted'] else "❌ DENIED"
        print(f"   {i}. {log['user_id']} → {status}")
        print(f"      Time: {log['timestamp'][:19]}")
        print(f"      Reason: {log['reason']}")
    
    # Policy management
    print(f"\n⚙️  Zero Trust Policies")
    print("-" * 25)
    
    for policy_id, policy in hdfc_zt.policies.items():
        print(f"   {policy_id}:")
        print(f"      Trust Level: {policy.required_trust_level.name}")
        print(f"      MFA Required: {', '.join(policy.required_factors)}")
        print(f"      Time Window: {policy.time_restrictions.get('start', 'N/A')}-{policy.time_restrictions.get('end', 'N/A')}")

def demonstrate_production_integration():
    """Show production integration examples"""
    print("\n" + "="*50)
    print("🏭 PRODUCTION INTEGRATION EXAMPLES")
    print("="*50)
    
    print("""
# Flask API with Zero Trust Integration

from flask import Flask, request, jsonify, g
from zero_trust_banking import ZeroTrustEngine, AccessRequest, ResourceType

app = Flask(__name__)
zt_engine = ZeroTrustEngine("HDFC")

@app.before_request
def zero_trust_check():
    if request.endpoint in ['login', 'health']:
        return  # Skip zero trust for login and health
    
    # Create access request
    access_request = AccessRequest(
        request_id=str(uuid.uuid4()),
        user_id=request.headers.get('X-User-ID'),
        resource=request.path,
        resource_type=ResourceType.CUSTOMER_DATA,  # Map based on endpoint
        client_ip=request.remote_addr,
        device_id=request.headers.get('X-Device-ID'),
        timestamp=datetime.now(),
        user_agent=request.headers.get('User-Agent'),
        geolocation=get_geolocation_from_ip(request.remote_addr)
    )
    
    # Evaluate access
    allowed, reason, metadata = zt_engine.evaluate_access_request(access_request)
    
    if not allowed:
        return jsonify({
            'error': 'Access Denied',
            'reason': reason,
            'code': 'ZERO_TRUST_VIOLATION'
        }), 403
    
    # Store for use in request
    g.trust_score = metadata.get('trust_score')
    g.access_token = metadata.get('access_token')

@app.route('/api/customer/<customer_id>')
def get_customer_data(customer_id):
    # Your API logic here
    return jsonify({
        'customer_id': customer_id,
        'trust_score': g.trust_score,
        'data': get_customer_data_from_db(customer_id)
    })

# Microservices Integration with Service Mesh

apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: zero-trust-banking
spec:
  rules:
  - from:
    - source:
        custom:
          zero_trust_score: ">= 80"
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/customer/*"]
    when:
    - key: custom.time_range
      values: ["09:00-18:00"]
    - key: custom.network_trust
      values: ["high", "critical"]

# Event-Driven Zero Trust Monitoring

import asyncio
import aioredis
from datetime import datetime

class ZeroTrustMonitor:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost")
        self.zt_engine = ZeroTrustEngine("HDFC")
        
    async def monitor_access_patterns(self):
        while True:
            # Get recent access attempts
            recent_logs = self.zt_engine.access_logs[-100:]
            
            # Analyze patterns
            failed_attempts = [log for log in recent_logs if not log['granted']]
            
            if len(failed_attempts) > 10:  # Threshold breach
                await self.trigger_security_alert({
                    'type': 'HIGH_FAILED_ATTEMPTS',
                    'count': len(failed_attempts),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Check for suspicious IPs
            ip_attempts = {}
            for log in recent_logs:
                ip = log['client_ip']
                ip_attempts[ip] = ip_attempts.get(ip, 0) + 1
            
            for ip, count in ip_attempts.items():
                if count > 20:  # Suspicious activity
                    await self.trigger_security_alert({
                        'type': 'SUSPICIOUS_IP',
                        'ip': ip,
                        'attempts': count
                    })
            
            await asyncio.sleep(60)  # Check every minute
    
    async def trigger_security_alert(self, alert_data):
        # Send to security team
        await self.redis.publish('security_alerts', json.dumps(alert_data))
        
        # Log to SIEM
        logger.warning(f"SECURITY_ALERT: {alert_data}")

# Continuous Authentication

class ContinuousAuth:
    def __init__(self, zt_engine):
        self.zt_engine = zt_engine
        
    async def validate_session(self, session_id, user_id):
        # Re-evaluate trust score periodically
        while True:
            current_request = self.get_current_request_context(session_id)
            
            trust_score = self.zt_engine.calculate_trust_score(
                user_id, current_request
            )
            
            if trust_score.final_score < 60:  # Trust degraded
                await self.terminate_session(session_id)
                await self.notify_user(user_id, "Session terminated due to trust degradation")
                break
            
            await asyncio.sleep(300)  # Check every 5 minutes
    """)

if __name__ == "__main__":
    demonstrate_zero_trust_banking()
    demonstrate_production_integration()