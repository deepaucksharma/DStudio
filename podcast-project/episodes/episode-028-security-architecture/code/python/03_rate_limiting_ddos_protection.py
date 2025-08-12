#!/usr/bin/env python3
"""
Rate Limiting & DDoS Protection System
Banking Grade Security for Indian Financial Services

यह system HDFC Bank, ICICI, और Axis Bank जैसे institutions के लिए
DDoS protection और rate limiting implement करता है। Production में
distributed rate limiting, IP blocking, और adaptive throttling करता है।

Real-world Context:
- Indian banks face 10,000+ DDoS attacks per month
- UPI processes 8 billion transactions/month
- RBI mandates 99.5% uptime for critical banking services
- Peak load: 50,000 TPS during festival seasons (Diwali, etc.)
"""

import time
import redis
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
from threading import Lock, RLock
import ipaddress
import json

# Setup logging for security incidents
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_incidents.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    name: str
    requests_per_minute: int
    burst_limit: int
    window_size_seconds: int = 60
    block_duration_minutes: int = 15
    whitelist_ips: Set[str] = None
    blacklist_ips: Set[str] = None
    
    def __post_init__(self):
        if self.whitelist_ips is None:
            self.whitelist_ips = set()
        if self.blacklist_ips is None:
            self.blacklist_ips = set()

@dataclass
class SecurityMetrics:
    """Security metrics tracking"""
    total_requests: int = 0
    blocked_requests: int = 0
    suspicious_ips: int = 0
    active_blocks: int = 0
    avg_response_time: float = 0.0
    peak_rps: int = 0
    threat_level: str = "LOW"

class DistributedRateLimiter:
    """
    Production-grade distributed rate limiter with DDoS protection
    
    Features:
    - Token bucket algorithm
    - Sliding window rate limiting
    - IP-based blocking
    - Adaptive throttling
    - Geographical filtering
    - Pattern-based detection
    """
    
    def __init__(
        self, 
        redis_host: str = "localhost", 
        redis_port: int = 6379,
        redis_password: str = None
    ):
        # Redis for distributed state
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Local caches for performance
        self.local_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_patterns: Dict[str, int] = defaultdict(int)
        self.cache_lock = RLock()
        
        # Security metrics
        self.metrics = SecurityMetrics()
        
        # Default rules for Indian banking
        self.rules = {
            'upi_payments': RateLimitRule(
                name='UPI Payments',
                requests_per_minute=100,
                burst_limit=20,
                window_size_seconds=60,
                block_duration_minutes=30
            ),
            'account_balance': RateLimitRule(
                name='Account Balance Check',
                requests_per_minute=60,
                burst_limit=10,
                window_size_seconds=60,
                block_duration_minutes=15
            ),
            'neft_rtgs': RateLimitRule(
                name='NEFT/RTGS Transfers',
                requests_per_minute=10,
                burst_limit=3,
                window_size_seconds=300,  # 5 minutes
                block_duration_minutes=60
            ),
            'login_attempts': RateLimitRule(
                name='Login Attempts',
                requests_per_minute=5,
                burst_limit=3,
                window_size_seconds=300,
                block_duration_minutes=120
            )
        }
        
        # Whitelist for trusted IPs (bank branches, ATMs)
        self.trusted_networks = {
            '203.192.0.0/16',    # HDFC Bank network
            '202.54.0.0/16',     # ICICI Bank network  
            '115.242.0.0/16',    # Axis Bank network
            '127.0.0.1/32',      # Localhost for testing
        }
        
        # Suspicious patterns
        self.attack_patterns = {
            'sql_injection': [
                "' or '1'='1", "union select", "drop table",
                "insert into", "delete from", "update set"
            ],
            'xss_patterns': [
                "<script>", "javascript:", "onload=", 
                "onerror=", "onclick=", "alert("
            ],
            'path_traversal': [
                "../", "..\\", "/etc/passwd", 
                "/proc/", "\\windows\\system32"
            ],
            'brute_force': [
                # Pattern detected by frequency analysis
            ]
        }
        
        logger.info("Distributed Rate Limiter initialized for Indian banking")
    
    def is_trusted_ip(self, ip: str) -> bool:
        """Check if IP is in trusted network ranges"""
        try:
            client_ip = ipaddress.ip_address(ip)
            for network in self.trusted_networks:
                if client_ip in ipaddress.ip_network(network):
                    return True
            return False
        except Exception:
            return False
    
    def detect_attack_patterns(self, request_data: str) -> List[str]:
        """Detect potential attack patterns in request"""
        detected_attacks = []
        request_lower = request_data.lower()
        
        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    detected_attacks.append(attack_type)
                    break
        
        return detected_attacks
    
    def check_rate_limit(
        self, 
        ip: str, 
        endpoint: str, 
        request_data: str = "",
        user_agent: str = ""
    ) -> Tuple[bool, str, Dict]:
        """
        Check if request should be allowed
        
        Returns:
            (is_allowed, reason, metadata)
        """
        try:
            current_time = time.time()
            self.metrics.total_requests += 1
            
            # Check if IP is blocked
            if ip in self.blocked_ips:
                if datetime.now() < self.blocked_ips[ip]:
                    self.metrics.blocked_requests += 1
                    return False, "IP_BLOCKED", {
                        'blocked_until': self.blocked_ips[ip].isoformat(),
                        'reason': 'Previous violations'
                    }
                else:
                    # Unblock expired IPs
                    del self.blocked_ips[ip]
            
            # Check trusted networks
            if self.is_trusted_ip(ip):
                return True, "TRUSTED_NETWORK", {'network': 'bank_internal'}
            
            # Detect attack patterns
            attacks = self.detect_attack_patterns(request_data + " " + user_agent)
            if attacks:
                self._block_ip(ip, f"Attack patterns detected: {', '.join(attacks)}")
                self.metrics.blocked_requests += 1
                return False, "ATTACK_DETECTED", {'attacks': attacks}
            
            # Get appropriate rule
            rule = self._get_rule_for_endpoint(endpoint)
            if not rule:
                return True, "NO_RULE", {}
            
            # Sliding window rate limiting
            is_allowed, metadata = self._sliding_window_check(ip, rule, current_time)
            
            if not is_allowed:
                self.metrics.blocked_requests += 1
                
                # Adaptive blocking - more violations = longer blocks
                violation_count = self.suspicious_patterns[ip]
                if violation_count > 5:
                    self._block_ip(ip, f"Repeated violations: {violation_count}")
                    return False, "IP_BLOCKED_ADAPTIVE", metadata
            
            return is_allowed, "ALLOWED" if is_allowed else "RATE_LIMITED", metadata
            
        except Exception as e:
            logger.error(f"Rate limit check failed for {ip}: {e}")
            return True, "ERROR", {'error': str(e)}  # Fail open for availability
    
    def _get_rule_for_endpoint(self, endpoint: str) -> Optional[RateLimitRule]:
        """Map endpoint to rate limit rule"""
        endpoint_mapping = {
            '/api/v1/upi/pay': 'upi_payments',
            '/api/v1/account/balance': 'account_balance',
            '/api/v1/transfer/neft': 'neft_rtgs',
            '/api/v1/transfer/rtgs': 'neft_rtgs',
            '/api/v1/auth/login': 'login_attempts',
            '/api/v1/cards/payment': 'upi_payments',
        }
        
        for pattern, rule_name in endpoint_mapping.items():
            if pattern in endpoint:
                return self.rules[rule_name]
        
        # Default rule for unknown endpoints
        return RateLimitRule(
            name='Default',
            requests_per_minute=30,
            burst_limit=10,
            window_size_seconds=60
        )
    
    def _sliding_window_check(
        self, 
        ip: str, 
        rule: RateLimitRule, 
        current_time: float
    ) -> Tuple[bool, Dict]:
        """Implement sliding window rate limiting"""
        try:
            window_key = f"rate_limit:{ip}:{rule.name}"
            window_start = current_time - rule.window_size_seconds
            
            # Use Redis for distributed tracking
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(window_key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(window_key)
            
            # Add current request
            pipe.zadd(window_key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(window_key, rule.window_size_seconds + 60)
            
            results = pipe.execute()
            current_count = results[1] if len(results) > 1 else 0
            
            # Check limits
            if current_count >= rule.requests_per_minute:
                # Record violation
                self.suspicious_patterns[ip] += 1
                
                return False, {
                    'current_count': current_count,
                    'limit': rule.requests_per_minute,
                    'window_seconds': rule.window_size_seconds,
                    'violation_count': self.suspicious_patterns[ip]
                }
            
            # Check burst limit
            recent_window = current_time - 60  # Last minute
            recent_count = self.redis_client.zcount(
                window_key, recent_window, current_time
            )
            
            if recent_count >= rule.burst_limit:
                self.suspicious_patterns[ip] += 1
                
                return False, {
                    'burst_count': recent_count,
                    'burst_limit': rule.burst_limit,
                    'violation_type': 'burst'
                }
            
            return True, {
                'current_count': current_count,
                'limit': rule.requests_per_minute,
                'remaining': rule.requests_per_minute - current_count
            }
            
        except Exception as e:
            logger.error(f"Sliding window check failed: {e}")
            return True, {'error': str(e)}
    
    def _block_ip(self, ip: str, reason: str, duration_minutes: int = None):
        """Block IP address"""
        try:
            if duration_minutes is None:
                duration_minutes = 15
                
            # Adaptive blocking - repeat offenders get longer blocks
            violation_count = self.suspicious_patterns[ip]
            if violation_count > 10:
                duration_minutes = 240  # 4 hours
            elif violation_count > 5:
                duration_minutes = 120  # 2 hours
            elif violation_count > 3:
                duration_minutes = 60   # 1 hour
            
            block_until = datetime.now() + timedelta(minutes=duration_minutes)
            self.blocked_ips[ip] = block_until
            
            # Store in Redis for distributed blocking
            block_key = f"blocked_ip:{ip}"
            self.redis_client.setex(
                block_key, 
                duration_minutes * 60, 
                json.dumps({
                    'reason': reason,
                    'blocked_at': datetime.now().isoformat(),
                    'blocked_until': block_until.isoformat(),
                    'violation_count': violation_count
                })
            )
            
            self.metrics.active_blocks += 1
            logger.warning(f"IP blocked: {ip}, Reason: {reason}, Duration: {duration_minutes}min")
            
        except Exception as e:
            logger.error(f"IP blocking failed: {e}")
    
    def get_security_metrics(self) -> Dict:
        """Get current security metrics"""
        try:
            # Update threat level based on metrics
            block_rate = (
                self.metrics.blocked_requests / max(self.metrics.total_requests, 1)
            ) * 100
            
            if block_rate > 20:
                self.metrics.threat_level = "CRITICAL"
            elif block_rate > 10:
                self.metrics.threat_level = "HIGH"
            elif block_rate > 5:
                self.metrics.threat_level = "MEDIUM"
            else:
                self.metrics.threat_level = "LOW"
            
            # Count suspicious IPs
            self.metrics.suspicious_ips = len(self.suspicious_patterns)
            self.metrics.active_blocks = len(self.blocked_ips)
            
            return {
                'total_requests': self.metrics.total_requests,
                'blocked_requests': self.metrics.blocked_requests,
                'block_rate_percent': round(block_rate, 2),
                'suspicious_ips': self.metrics.suspicious_ips,
                'active_blocks': self.metrics.active_blocks,
                'threat_level': self.metrics.threat_level,
                'timestamp': datetime.now().isoformat(),
                'top_offenders': dict(
                    sorted(
                        self.suspicious_patterns.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                )
            }
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {}
    
    def unblock_ip(self, ip: str, reason: str = "Manual unblock"):
        """Manually unblock an IP address"""
        try:
            if ip in self.blocked_ips:
                del self.blocked_ips[ip]
                
            # Remove from Redis
            self.redis_client.delete(f"blocked_ip:{ip}")
            
            # Reset suspicious pattern count
            if ip in self.suspicious_patterns:
                self.suspicious_patterns[ip] = 0
                
            logger.info(f"IP unblocked: {ip}, Reason: {reason}")
            
        except Exception as e:
            logger.error(f"IP unblock failed: {e}")

class DDoSProtectionMiddleware:
    """
    Flask/Django middleware for DDoS protection
    Indian banking context with UPI, NEFT, RTGS protection
    """
    
    def __init__(self, rate_limiter: DistributedRateLimiter):
        self.rate_limiter = rate_limiter
    
    def process_request(self, request) -> Tuple[bool, Dict]:
        """Process incoming request for DDoS protection"""
        try:
            # Extract request details
            ip = self._get_client_ip(request)
            endpoint = request.path
            method = request.method
            user_agent = request.headers.get('User-Agent', '')
            request_data = self._get_request_data(request)
            
            # Rate limiting check
            is_allowed, reason, metadata = self.rate_limiter.check_rate_limit(
                ip=ip,
                endpoint=endpoint,
                request_data=request_data,
                user_agent=user_agent
            )
            
            response_data = {
                'allowed': is_allowed,
                'reason': reason,
                'metadata': metadata,
                'ip': ip,
                'endpoint': endpoint,
                'timestamp': datetime.now().isoformat()
            }
            
            if not is_allowed:
                logger.warning(f"Request blocked - IP: {ip}, Endpoint: {endpoint}, Reason: {reason}")
            
            return is_allowed, response_data
            
        except Exception as e:
            logger.error(f"DDoS middleware error: {e}")
            return True, {'error': str(e)}  # Fail open
    
    def _get_client_ip(self, request) -> str:
        """Extract real client IP (handles proxy headers)"""
        # Check for common proxy headers
        forwarded_ips = [
            request.headers.get('X-Forwarded-For'),
            request.headers.get('X-Real-IP'),
            request.headers.get('CF-Connecting-IP'),  # Cloudflare
            request.remote_addr
        ]
        
        for ip in forwarded_ips:
            if ip:
                # Take first IP if comma-separated
                return ip.split(',')[0].strip()
        
        return '127.0.0.1'  # Fallback
    
    def _get_request_data(self, request) -> str:
        """Extract request data for pattern analysis"""
        try:
            data_parts = []
            
            # URL parameters
            if hasattr(request, 'args'):
                data_parts.append(str(request.args))
            
            # Form data (limit size for performance)
            if hasattr(request, 'form'):
                form_data = str(request.form)[:1000]  # Limit to 1KB
                data_parts.append(form_data)
            
            # JSON data
            if hasattr(request, 'json') and request.json:
                json_data = str(request.json)[:1000]
                data_parts.append(json_data)
            
            return ' '.join(data_parts)
            
        except Exception:
            return ""

def simulate_indian_banking_ddos():
    """
    Simulate DDoS attack scenarios on Indian banking infrastructure
    Test rate limiting for UPI, NEFT, RTGS, and card payments
    """
    print("\n🛡️  भारतीय Banking DDoS Protection Demo")
    print("=" * 50)
    
    # Initialize rate limiter
    rate_limiter = DistributedRateLimiter()
    
    # Simulate normal traffic patterns
    print("\n📊 Normal Traffic Simulation")
    print("-" * 30)
    
    normal_ips = ['203.192.1.100', '202.54.2.50', '115.242.3.25']  # Bank networks
    endpoints = [
        '/api/v1/upi/pay',
        '/api/v1/account/balance', 
        '/api/v1/transfer/neft'
    ]
    
    for i in range(10):
        for ip in normal_ips:
            for endpoint in endpoints:
                allowed, reason, metadata = rate_limiter.check_rate_limit(
                    ip=ip,
                    endpoint=endpoint,
                    request_data='{"amount": 1000, "beneficiary": "test"}'
                )
                if i < 3:  # Show first few
                    print(f"✅ {ip} → {endpoint}: {reason}")
        time.sleep(0.1)
    
    # Simulate DDoS attack
    print("\n🚨 DDoS Attack Simulation")
    print("-" * 30)
    
    # Attacker IPs
    attacker_ips = ['192.168.1.100', '10.0.0.50', '172.16.0.75']
    
    print("🔥 High-frequency requests from suspicious IPs:")
    for attacker in attacker_ips:
        print(f"\n   Attacking from: {attacker}")
        for i in range(25):  # Exceed rate limits
            allowed, reason, metadata = rate_limiter.check_rate_limit(
                ip=attacker,
                endpoint='/api/v1/upi/pay',
                request_data='{"amount": 50000}'
            )
            if i < 5 or not allowed:  # Show initial and blocked requests
                status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
                print(f"     Request {i+1}: {status} - {reason}")
            if not allowed:
                break
    
    # Simulate attack with malicious patterns
    print("\n🎯 Malicious Pattern Detection")
    print("-" * 35)
    
    malicious_requests = [
        ("SQL Injection", "' OR '1'='1' --"),
        ("XSS Attack", "<script>alert('xss')</script>"),
        ("Path Traversal", "../../../etc/passwd"),
        ("Brute Force", "admin:password123")
    ]
    
    for attack_type, payload in malicious_requests:
        allowed, reason, metadata = rate_limiter.check_rate_limit(
            ip='203.0.113.100',  # Attacker IP
            endpoint='/api/v1/auth/login',
            request_data=payload
        )
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        print(f"{attack_type}: {status} - {reason}")
    
    # Show security metrics
    print("\n📈 Security Metrics Dashboard")
    print("-" * 35)
    metrics = rate_limiter.get_security_metrics()
    
    print(f"🔢 Total requests: {metrics['total_requests']}")
    print(f"🚫 Blocked requests: {metrics['blocked_requests']}")
    print(f"📊 Block rate: {metrics['block_rate_percent']}%")
    print(f"🚨 Threat level: {metrics['threat_level']}")
    print(f"👥 Suspicious IPs: {metrics['suspicious_ips']}")
    print(f"🔒 Active blocks: {metrics['active_blocks']}")
    
    if metrics['top_offenders']:
        print("\n🏆 Top Offending IPs:")
        for ip, violations in list(metrics['top_offenders'].items())[:5]:
            print(f"   {ip}: {violations} violations")
    
    # Test manual unblocking
    print("\n🔓 Manual IP Management")
    print("-" * 25)
    
    blocked_ip = list(rate_limiter.blocked_ips.keys())[0] if rate_limiter.blocked_ips else None
    if blocked_ip:
        print(f"🔒 Currently blocked: {blocked_ip}")
        rate_limiter.unblock_ip(blocked_ip, "Security team review")
        print(f"🔓 Unblocked: {blocked_ip}")
    
    # Adaptive protection demo
    print("\n🧠 Adaptive Protection Demo")
    print("-" * 30)
    
    print("🎯 Repeat offender gets longer blocks:")
    repeat_offender = '198.51.100.10'
    
    for attempt in range(3):
        # Simulate multiple violations
        for _ in range(10):
            rate_limiter.check_rate_limit(
                ip=repeat_offender,
                endpoint='/api/v1/upi/pay'
            )
        
        violation_count = rate_limiter.suspicious_patterns[repeat_offender]
        print(f"   Attempt {attempt + 1}: {violation_count} violations")
        
        if repeat_offender in rate_limiter.blocked_ips:
            block_time = rate_limiter.blocked_ips[repeat_offender]
            duration = (block_time - datetime.now()).total_seconds() / 60
            print(f"   ⏰ Block duration: {duration:.0f} minutes")

def demonstrate_production_integration():
    """Show production Flask/Django integration"""
    print("\n" + "="*50)
    print("🏭 PRODUCTION INTEGRATION EXAMPLE")
    print("="*50)
    
    print("""
# Flask Integration Example

from flask import Flask, request, jsonify
from rate_limiting_ddos_protection import DistributedRateLimiter, DDoSProtectionMiddleware

app = Flask(__name__)
rate_limiter = DistributedRateLimiter(
    redis_host='redis-cluster.hdfc.com',
    redis_password=os.getenv('REDIS_PASSWORD')
)
ddos_middleware = DDoSProtectionMiddleware(rate_limiter)

@app.before_request
def check_ddos_protection():
    is_allowed, response_data = ddos_middleware.process_request(request)
    
    if not is_allowed:
        return jsonify({
            'error': 'Request blocked',
            'reason': response_data['reason'],
            'retry_after': 60
        }), 429
    
    # Add rate limit headers
    g.rate_limit_data = response_data

@app.route('/api/v1/upi/pay', methods=['POST'])
def upi_payment():
    # Your UPI payment logic
    return jsonify({'status': 'success'})

# Django Middleware Example

class DDoSProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = DistributedRateLimiter()
        
    def __call__(self, request):
        is_allowed, response_data = self.process_request(request)
        
        if not is_allowed:
            return JsonResponse({
                'error': 'Request blocked',
                'reason': response_data['reason']
            }, status=429)
            
        response = self.get_response(request)
        return response

# Add to Django settings.py
MIDDLEWARE = [
    'myapp.middleware.DDoSProtectionMiddleware',
    # ... other middleware
]

# Monitoring Integration

# Send metrics to Prometheus
from prometheus_client import Counter, Histogram, Gauge

blocked_requests = Counter('ddos_blocked_requests_total', 'Blocked requests', ['reason'])
threat_level_gauge = Gauge('ddos_threat_level', 'Current threat level')

# In your monitoring loop:
metrics = rate_limiter.get_security_metrics()
threat_level_gauge.set(
    {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}[metrics['threat_level']]
)
    """)

if __name__ == "__main__":
    simulate_indian_banking_ddos()
    demonstrate_production_integration()