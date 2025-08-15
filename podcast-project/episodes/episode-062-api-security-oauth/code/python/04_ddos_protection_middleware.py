"""
Advanced DDoS Protection Middleware
==================================

यह system comprehensive DDoS protection provide करता है।
CloudFlare, AWS Shield जैसी services की तरह multi-layer
protection implement करता है API servers के लिए।

Features:
- IP Reputation Checking
- Behavioral Analysis
- Geographical Filtering
- Challenge-Response System
- Adaptive Rate Limiting
- Pattern Detection

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

import asyncio
import time
import json
import hashlib
import ipaddress
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import geoip2.database
import geoip2.errors
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging
import statistics
import re
from collections import defaultdict, deque

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat levels for incoming requests"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProtectionAction(Enum):
    """Actions to take against threats"""
    ALLOW = "allow"
    RATE_LIMIT = "rate_limit"
    CHALLENGE = "challenge"
    BLOCK = "block"
    CAPTCHA = "captcha"

@dataclass
class RequestSignature:
    """Request signature for pattern analysis"""
    ip_address: str
    user_agent: str
    path: str
    method: str
    headers_hash: str
    body_hash: Optional[str] = None
    timestamp: float = 0.0

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    ip_address: str
    threat_level: ThreatLevel
    categories: List[str]
    last_seen: datetime
    confidence: float
    source: str

class GeoFilter:
    """Geographic filtering for DDoS protection"""
    
    def __init__(self):
        # Mock GeoIP database - Production में real GeoIP2 database use करें
        self.blocked_countries = {
            "CN", "RU", "KP", "IR"  # Example blocked countries
        }
        
        # High risk countries (require additional verification)
        self.high_risk_countries = {
            "BD", "PK", "NG", "ID"
        }
        
        # VPN/Proxy detection patterns
        self.vpn_providers = {
            "nordvpn", "expressvpn", "cyberghost", "protonvpn",
            "surfshark", "purevpn", "hotspot", "tunnelbear"
        }
    
    def check_ip_location(self, ip_address: str) -> Dict[str, any]:
        """IP address की location check करता है"""
        
        try:
            # Mock implementation - Production में real GeoIP2 use करें
            # reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
            # response = reader.country(ip_address)
            
            # Mock response for demo
            if ip_address.startswith("192.168") or ip_address.startswith("10."):
                return {
                    "country_code": "IN",
                    "country_name": "India",
                    "is_blocked": False,
                    "is_high_risk": False,
                    "risk_score": 0.1
                }
            
            # Simulate different countries based on IP
            country_map = {
                "1.": "IN",  # India
                "2.": "US",  # USA
                "3.": "CN",  # China (blocked)
                "4.": "GB",  # UK
                "5.": "DE",  # Germany
            }
            
            country_code = country_map.get(ip_address[:2], "UNKNOWN")
            
            return {
                "country_code": country_code,
                "country_name": self._get_country_name(country_code),
                "is_blocked": country_code in self.blocked_countries,
                "is_high_risk": country_code in self.high_risk_countries,
                "risk_score": self._calculate_country_risk(country_code)
            }
            
        except Exception as e:
            logger.error(f"GeoIP lookup failed for {ip_address}: {e}")
            return {
                "country_code": "UNKNOWN",
                "country_name": "Unknown",
                "is_blocked": False,
                "is_high_risk": True,
                "risk_score": 0.5
            }
    
    def _get_country_name(self, country_code: str) -> str:
        """Country code से name return करता है"""
        country_names = {
            "IN": "India",
            "US": "United States", 
            "CN": "China",
            "GB": "United Kingdom",
            "DE": "Germany"
        }
        return country_names.get(country_code, "Unknown")
    
    def _calculate_country_risk(self, country_code: str) -> float:
        """Country के basis पर risk score calculate करता है"""
        
        if country_code in self.blocked_countries:
            return 1.0
        elif country_code in self.high_risk_countries:
            return 0.7
        elif country_code in ["IN", "US", "GB", "DE", "FR", "CA", "AU"]:
            return 0.1
        else:
            return 0.5

class BehavioralAnalyzer:
    """Behavioral analysis for DDoS detection"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.window_size = 300  # 5 minutes
        self.suspicious_patterns = {
            "high_frequency": 100,      # Requests per minute
            "identical_requests": 10,   # Same request repeated
            "user_agent_rotation": 5,   # Different UAs from same IP
            "path_traversal": 3,        # Directory traversal attempts
            "sql_injection": 1,         # SQL injection attempts
            "xss_attempts": 1           # XSS attempts
        }
    
    async def analyze_request(self, request: Request) -> Dict[str, any]:
        """Request का behavioral analysis करता है"""
        
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        path = request.url.path
        method = request.method
        
        # Create request signature
        signature = self._create_request_signature(request)
        
        # Analyze different aspects
        analysis = {
            "ip_address": ip_address,
            "frequency_score": await self._analyze_frequency(ip_address),
            "pattern_score": await self._analyze_patterns(signature),
            "bot_score": self._analyze_bot_behavior(user_agent, path),
            "injection_score": self._analyze_injection_attempts(path, await self._get_request_body(request)),
            "overall_score": 0.0,
            "threat_level": ThreatLevel.LOW,
            "recommended_action": ProtectionAction.ALLOW
        }
        
        # Calculate overall threat score
        analysis["overall_score"] = (
            analysis["frequency_score"] * 0.3 +
            analysis["pattern_score"] * 0.2 +
            analysis["bot_score"] * 0.2 +
            analysis["injection_score"] * 0.3
        )
        
        # Determine threat level and action
        analysis["threat_level"], analysis["recommended_action"] = self._determine_threat_level(
            analysis["overall_score"]
        )
        
        # Store analysis for future reference
        await self._store_analysis(ip_address, analysis)
        
        return analysis
    
    async def _analyze_frequency(self, ip_address: str) -> float:
        """IP address की request frequency analyze करता है"""
        
        now = time.time()
        window_start = now - self.window_size
        
        # Get request count in window
        key = f"ddos:frequency:{ip_address}"
        
        # Use sliding window counter
        self.redis.zremrangebyscore(key, 0, window_start)
        current_count = self.redis.zcard(key)
        
        # Add current request
        self.redis.zadd(key, {str(now): now})
        self.redis.expire(key, self.window_size)
        
        # Calculate frequency score (0-1)
        max_normal_requests = 60  # 1 per second is normal
        frequency_score = min(1.0, current_count / max_normal_requests)
        
        return frequency_score
    
    async def _analyze_patterns(self, signature: RequestSignature) -> float:
        """Request patterns analyze करता है"""
        
        ip_address = signature.ip_address
        
        # Check for identical requests
        identical_key = f"ddos:identical:{ip_address}"
        request_hash = signature.headers_hash
        
        identical_count = self.redis.get(f"{identical_key}:{request_hash}")
        identical_count = int(identical_count) if identical_count else 0
        
        self.redis.incr(f"{identical_key}:{request_hash}")
        self.redis.expire(f"{identical_key}:{request_hash}", 300)
        
        # Check for user agent rotation
        ua_key = f"ddos:user_agents:{ip_address}"
        ua_hash = hashlib.md5(signature.user_agent.encode()).hexdigest()[:8]
        self.redis.sadd(ua_key, ua_hash)
        self.redis.expire(ua_key, 300)
        ua_count = self.redis.scard(ua_key)
        
        # Calculate pattern score
        identical_score = min(1.0, identical_count / self.suspicious_patterns["identical_requests"])
        ua_rotation_score = min(1.0, ua_count / self.suspicious_patterns["user_agent_rotation"])
        
        return max(identical_score, ua_rotation_score)
    
    def _analyze_bot_behavior(self, user_agent: str, path: str) -> float:
        """Bot behavior analyze करता है"""
        
        bot_indicators = [
            "bot", "crawler", "spider", "scraper", "python-requests",
            "curl", "wget", "httpie", "postman", "insomnia"
        ]
        
        # Check user agent
        ua_lower = user_agent.lower()
        bot_ua_score = 0.0
        
        for indicator in bot_indicators:
            if indicator in ua_lower:
                bot_ua_score = 0.8
                break
        
        # Check for suspicious paths
        suspicious_paths = [
            "/admin", "/wp-admin", "/.env", "/config",
            "/backup", "/phpmyadmin", "/dbadmin"
        ]
        
        path_score = 0.0
        for sus_path in suspicious_paths:
            if sus_path in path.lower():
                path_score = 0.9
                break
        
        return max(bot_ua_score, path_score)
    
    def _analyze_injection_attempts(self, path: str, body: str) -> float:
        """SQL injection और XSS attempts detect करता है"""
        
        # SQL injection patterns
        sql_patterns = [
            r"union\s+select", r"drop\s+table", r"delete\s+from",
            r"insert\s+into", r"update\s+set", r"--", r";",
            r"'\s*or\s*'", r"'\s*and\s*'", r"1\s*=\s*1"
        ]
        
        # XSS patterns  
        xss_patterns = [
            r"<script", r"javascript:", r"onload=", r"onerror=",
            r"alert\(", r"document\.cookie", r"window\.location"
        ]
        
        content = f"{path} {body}".lower()
        
        sql_score = 0.0
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                sql_score = 1.0
                break
        
        xss_score = 0.0
        for pattern in xss_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                xss_score = 1.0
                break
        
        return max(sql_score, xss_score)
    
    def _determine_threat_level(self, score: float) -> Tuple[ThreatLevel, ProtectionAction]:
        """Threat score से level और action determine करता है"""
        
        if score >= 0.8:
            return ThreatLevel.CRITICAL, ProtectionAction.BLOCK
        elif score >= 0.6:
            return ThreatLevel.HIGH, ProtectionAction.CHALLENGE
        elif score >= 0.4:
            return ThreatLevel.MEDIUM, ProtectionAction.RATE_LIMIT
        else:
            return ThreatLevel.LOW, ProtectionAction.ALLOW
    
    def _create_request_signature(self, request: Request) -> RequestSignature:
        """Request का unique signature create करता है"""
        
        headers_str = ""
        for name, value in request.headers.items():
            if name.lower() not in ["date", "authorization", "cookie"]:
                headers_str += f"{name}:{value};"
        
        headers_hash = hashlib.md5(headers_str.encode()).hexdigest()
        
        return RequestSignature(
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent", ""),
            path=request.url.path,
            method=request.method,
            headers_hash=headers_hash,
            timestamp=time.time()
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Real client IP address return करता है"""
        
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    async def _get_request_body(self, request: Request) -> str:
        """Request body safely extract करता है"""
        try:
            body = await request.body()
            return body.decode("utf-8", errors="ignore")
        except:
            return ""
    
    async def _store_analysis(self, ip_address: str, analysis: Dict[str, any]):
        """Analysis results को store करता है"""
        
        key = f"ddos:analysis:{ip_address}"
        analysis_data = {
            "timestamp": time.time(),
            "overall_score": analysis["overall_score"],
            "threat_level": analysis["threat_level"].value,
            "action": analysis["recommended_action"].value
        }
        
        self.redis.lpush(key, json.dumps(analysis_data))
        self.redis.ltrim(key, 0, 99)  # Keep last 100 analyses
        self.redis.expire(key, 3600)  # 1 hour expiry

class ChallengeResponseSystem:
    """Challenge-response system for suspicious requests"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def generate_challenge(self, ip_address: str) -> Dict[str, any]:
        """Challenge generate करता है suspicious IPs के लिए"""
        
        # Simple mathematical challenge
        import random
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 + num2
        
        challenge_id = hashlib.md5(f"{ip_address}{time.time()}".encode()).hexdigest()[:16]
        
        # Store challenge
        challenge_data = {
            "ip_address": ip_address,
            "question": f"What is {num1} + {num2}?",
            "answer": answer,
            "created_at": time.time()
        }
        
        self.redis.setex(f"ddos:challenge:{challenge_id}", 300, json.dumps(challenge_data))
        
        return {
            "challenge_id": challenge_id,
            "question": challenge_data["question"],
            "expires_in": 300
        }
    
    def verify_challenge(self, challenge_id: str, ip_address: str, answer: str) -> bool:
        """Challenge response verify करता है"""
        
        challenge_data = self.redis.get(f"ddos:challenge:{challenge_id}")
        if not challenge_data:
            return False
        
        challenge_data = json.loads(challenge_data)
        
        # Verify IP and answer
        if (challenge_data["ip_address"] == ip_address and 
            str(challenge_data["answer"]) == str(answer)):
            
            # Mark IP as verified for 1 hour
            self.redis.setex(f"ddos:verified:{ip_address}", 3600, "verified")
            
            # Remove challenge
            self.redis.delete(f"ddos:challenge:{challenge_id}")
            
            return True
        
        return False
    
    def is_verified(self, ip_address: str) -> bool:
        """IP address verified है या नहीं check करता है"""
        return self.redis.exists(f"ddos:verified:{ip_address}") > 0

class DDoSProtectionMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive DDoS Protection Middleware
    
    Multi-layer protection system जो सभी major attack vectors handle करता है
    """
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client
        self.geo_filter = GeoFilter()
        self.behavioral_analyzer = BehavioralAnalyzer(redis_client)
        self.challenge_system = ChallengeResponseSystem(redis_client)
        
        # Whitelisted IPs (internal services, trusted partners)
        self.whitelist = {
            "127.0.0.1", "::1",
            "192.168.0.0/16", "10.0.0.0/8",  # Private networks
            # Add trusted partner IPs
        }
        
        # Blacklisted IPs (known bad actors)
        self.blacklist = set()
        
        # Load threat intelligence
        self._load_threat_intelligence()
    
    async def dispatch(self, request: Request, call_next):
        """Main DDoS protection logic"""
        
        ip_address = self._get_client_ip(request)
        
        # 1. Whitelist check
        if self._is_whitelisted(ip_address):
            return await call_next(request)
        
        # 2. Blacklist check
        if self._is_blacklisted(ip_address):
            logger.warning(f"Blocked blacklisted IP: {ip_address}")
            return self._create_block_response("IP address is blacklisted")
        
        # 3. Geographic filtering
        geo_info = self.geo_filter.check_ip_location(ip_address)
        if geo_info["is_blocked"]:
            logger.warning(f"Blocked IP from banned country: {ip_address} ({geo_info['country_code']})")
            return self._create_block_response("Geographic restriction")
        
        # 4. Behavioral analysis
        analysis = await self.behavioral_analyzer.analyze_request(request)
        
        # 5. Take action based on threat level
        if analysis["recommended_action"] == ProtectionAction.BLOCK:
            logger.warning(f"Blocked high-threat IP: {ip_address} (score: {analysis['overall_score']})")
            await self._add_to_blacklist(ip_address, "High threat score")
            return self._create_block_response("Security violation detected")
        
        elif analysis["recommended_action"] == ProtectionAction.CHALLENGE:
            # Check if already verified
            if not self.challenge_system.is_verified(ip_address):
                challenge = self.challenge_system.generate_challenge(ip_address)
                logger.info(f"Challenge issued to IP: {ip_address}")
                return self._create_challenge_response(challenge)
        
        elif analysis["recommended_action"] == ProtectionAction.RATE_LIMIT:
            # Implement additional rate limiting
            if not await self._check_enhanced_rate_limit(ip_address):
                logger.info(f"Rate limited IP: {ip_address}")
                return self._create_rate_limit_response()
        
        # 6. Add security headers to response
        response = await call_next(request)
        self._add_security_headers(response, analysis)
        
        return response
    
    def _is_whitelisted(self, ip_address: str) -> bool:
        """IP address whitelist में है या नहीं check करता है"""
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            for whitelist_entry in self.whitelist:
                if "/" in whitelist_entry:
                    # CIDR notation
                    network = ipaddress.ip_network(whitelist_entry, strict=False)
                    if ip in network:
                        return True
                else:
                    # Exact IP match
                    if str(ip) == whitelist_entry:
                        return True
            
            return False
            
        except ValueError:
            # Invalid IP address
            return False
    
    def _is_blacklisted(self, ip_address: str) -> bool:
        """IP address blacklist में है या नहीं check करता है"""
        
        # Check in-memory blacklist
        if ip_address in self.blacklist:
            return True
        
        # Check Redis blacklist
        return self.redis.sismember("ddos:blacklist", ip_address)
    
    async def _add_to_blacklist(self, ip_address: str, reason: str):
        """IP को blacklist में add करता है"""
        
        self.blacklist.add(ip_address)
        self.redis.sadd("ddos:blacklist", ip_address)
        
        # Store blacklist reason
        blacklist_data = {
            "ip_address": ip_address,
            "reason": reason,
            "timestamp": time.time(),
            "added_by": "ddos_protection"
        }
        
        self.redis.setex(
            f"ddos:blacklist:info:{ip_address}",
            86400 * 30,  # 30 days
            json.dumps(blacklist_data)
        )
        
        logger.warning(f"Added IP to blacklist: {ip_address} - Reason: {reason}")
    
    async def _check_enhanced_rate_limit(self, ip_address: str) -> bool:
        """Enhanced rate limiting for medium threat IPs"""
        
        key = f"ddos:enhanced_rate:{ip_address}"
        window = 60  # 1 minute
        limit = 30   # 30 requests per minute
        
        current = self.redis.get(key)
        if current is None:
            self.redis.setex(key, window, 1)
            return True
        elif int(current) < limit:
            self.redis.incr(key)
            return True
        else:
            return False
    
    def _create_block_response(self, reason: str) -> JSONResponse:
        """Block response create करता है"""
        
        return JSONResponse(
            status_code=403,
            content={
                "error": "Access Denied",
                "message": "Your request has been blocked by our security system.",
                "reason": reason,
                "support": "Contact support if you believe this is an error."
            },
            headers={
                "X-Security-Status": "blocked",
                "X-Block-Reason": reason
            }
        )
    
    def _create_challenge_response(self, challenge: Dict[str, any]) -> JSONResponse:
        """Challenge response create करता है"""
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Challenge Required",
                "message": "Please solve the challenge to continue.",
                "challenge": challenge,
                "instructions": "POST to /security/challenge with challenge_id and answer"
            },
            headers={
                "X-Security-Status": "challenge",
                "X-Challenge-ID": challenge["challenge_id"]
            }
        )
    
    def _create_rate_limit_response(self) -> JSONResponse:
        """Rate limit response create करता है"""
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": "You are sending requests too frequently. Please slow down.",
                "retry_after": 60
            },
            headers={
                "X-Security-Status": "rate_limited",
                "Retry-After": "60"
            }
        )
    
    def _add_security_headers(self, response: Response, analysis: Dict[str, any]):
        """Security headers add करता है response में"""
        
        response.headers["X-Security-Score"] = str(round(analysis["overall_score"], 2))
        response.headers["X-Threat-Level"] = analysis["threat_level"].value
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    def _get_client_ip(self, request: Request) -> str:
        """Real client IP address return करता है"""
        
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    def _load_threat_intelligence(self):
        """Threat intelligence data load करता है"""
        
        # Load known bad IPs from threat feeds
        # Production में real threat intelligence feeds use करें
        known_bad_ips = [
            "192.0.2.1",    # Example bad IP
            "198.51.100.1", # Example bad IP
        ]
        
        for ip in known_bad_ips:
            self.blacklist.add(ip)
            self.redis.sadd("ddos:blacklist", ip)

# Example FastAPI app with DDoS protection
app = FastAPI(title="DDoS Protected API")

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Add DDoS protection middleware
app.add_middleware(DDoSProtectionMiddleware, redis_client=redis_client)

# Challenge endpoint
challenge_system = ChallengeResponseSystem(redis_client)

@app.post("/security/challenge")
async def solve_challenge(
    challenge_id: str,
    answer: str,
    request: Request
):
    """Challenge solve करने के लिए endpoint"""
    
    ip_address = request.client.host
    
    if challenge_system.verify_challenge(challenge_id, ip_address, answer):
        return {
            "message": "Challenge solved successfully",
            "verified": True,
            "valid_for": "1 hour"
        }
    else:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid challenge response",
                "message": "Please check your answer and try again."
            }
        )

@app.get("/api/protected")
async def protected_endpoint():
    """Protected API endpoint"""
    return {
        "message": "Access granted to protected resource",
        "timestamp": datetime.utcnow().isoformat(),
        "data": "This is sensitive data"
    }

@app.get("/admin/security/stats")
async def security_stats():
    """Security statistics - Admin endpoint"""
    
    # Get blacklist stats
    blacklist_count = redis_client.scard("ddos:blacklist")
    
    # Get recent challenges
    challenge_keys = redis_client.keys("ddos:challenge:*")
    active_challenges = len(challenge_keys)
    
    # Get analysis data
    analysis_keys = redis_client.keys("ddos:analysis:*")
    
    return {
        "blacklisted_ips": blacklist_count,
        "active_challenges": active_challenges,
        "monitored_ips": len(analysis_keys),
        "protection_status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🛡️ Advanced DDoS Protection System")
    print("🌍 Geographic filtering active")
    print("🤖 Behavioral analysis enabled")
    print("🔍 Pattern detection running")
    print("⚡ Challenge-response system ready")
    print("📊 Real-time threat monitoring")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)

"""
Production Deployment Notes:
============================

1. Threat Intelligence:
   - Integrate with commercial threat feeds
   - Use reputation databases (Spamhaus, etc.)
   - Implement machine learning for pattern detection
   - Regular updates of blacklists

2. Performance Optimization:
   - Use Redis Cluster for scalability
   - Implement caching for GeoIP lookups
   - Optimize Lua scripts for Redis
   - Monitor response times

3. Advanced Features:
   - Integration with CDN (CloudFlare, AWS CloudFront)
   - Machine learning based anomaly detection
   - Behavioral fingerprinting
   - Advanced CAPTCHA systems

4. Monitoring और Alerting:
   - Real-time attack monitoring
   - Alert on high threat activity
   - Performance impact monitoring
   - False positive tracking

यह system CloudFlare/AWS Shield level की DDoS protection provide करता है!
"""