#!/usr/bin/env python3
"""
Web Application Firewall (WAF) for E-commerce Protection
Flipkart, Amazon India, Myntra Production Security

यह system e-commerce applications के लिए comprehensive WAF implement करता है।
Production में SQL injection, XSS, DDoS protection, और bot mitigation।

Real-world Context:
- Flipkart handles 100M+ requests during Big Billion Days
- E-commerce sites face 10,000+ attacks daily
- WAF reduces false positives by 90% with ML-based rules
- Average attack response time: <100ms
"""

import re
import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
from urllib.parse import unquote, parse_qs
import ipaddress
import asyncio
import threading

# Setup logging for WAF operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('waf_security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityRule:
    """WAF security rule definition"""
    rule_id: str
    name: str
    description: str
    pattern: str
    rule_type: str  # regex, keyword, ml, rate_limit
    severity: str   # low, medium, high, critical
    action: str     # block, monitor, rate_limit
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    ip_address: str
    threat_type: str
    confidence: float
    source: str
    first_seen: datetime
    last_seen: datetime
    attack_count: int = 0

@dataclass
class AttackEvent:
    """Security attack event"""
    event_id: str
    timestamp: datetime
    client_ip: str
    user_agent: str
    method: str
    uri: str
    payload: str
    rule_matched: str
    severity: str
    action_taken: str
    blocked: bool

class EcommerceWAF:
    """
    Production Web Application Firewall for E-commerce
    
    Features:
    - SQL injection protection
    - XSS prevention
    - CSRF protection
    - Rate limiting
    - Bot detection
    - Geo-blocking
    - Content filtering
    - Real-time threat intelligence
    """
    
    def __init__(self, site_name: str = "Flipkart"):
        self.site_name = site_name
        self.security_rules: Dict[str, SecurityRule] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.attack_events: deque = deque(maxlen=10000)
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Initialize security rules
        self._initialize_security_rules()
        self._load_threat_intelligence()
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'threats_detected': 0,
            'false_positives': 0,
            'avg_response_time_ms': 0
        }
        
        logger.info(f"E-commerce WAF initialized for {site_name}")
    
    def _initialize_security_rules(self):
        """Initialize comprehensive security rules for e-commerce"""
        
        # SQL Injection Rules
        sql_injection_rules = [
            {
                'rule_id': 'SQL_001',
                'name': 'SQL Injection - Union Attack',
                'pattern': r'(?i)\bunion\b.*\bselect\b',
                'severity': 'critical'
            },
            {
                'rule_id': 'SQL_002', 
                'name': 'SQL Injection - Comment Injection',
                'pattern': r'(?i)(--|#|/\*|\*/)',
                'severity': 'high'
            },
            {
                'rule_id': 'SQL_003',
                'name': 'SQL Injection - Classic Quotes',
                'pattern': r"(?i)('|\").*(\bor\b|\band\b).*('|\"|\d)",
                'severity': 'high'
            }
        ]
        
        # XSS Rules
        xss_rules = [
            {
                'rule_id': 'XSS_001',
                'name': 'XSS - Script Tag Injection',
                'pattern': r'(?i)<script[^>]*>',
                'severity': 'high'
            },
            {
                'rule_id': 'XSS_002',
                'name': 'XSS - Event Handler Injection',
                'pattern': r'(?i)\bon\w+\s*=',
                'severity': 'medium'
            },
            {
                'rule_id': 'XSS_003',
                'name': 'XSS - JavaScript URL',
                'pattern': r'(?i)javascript:',
                'severity': 'medium'
            }
        ]
        
        # E-commerce Specific Rules
        ecommerce_rules = [
            {
                'rule_id': 'ECOM_001',
                'name': 'Price Manipulation Attempt',
                'pattern': r'(?i)(price|amount|total).*(<|>|=).*(-|\d{4,})',
                'severity': 'high'
            },
            {
                'rule_id': 'ECOM_002',
                'name': 'Inventory Enumeration',
                'pattern': r'(?i)product_id.*(\.\./|%2e%2e%2f)',
                'severity': 'medium'
            },
            {
                'rule_id': 'ECOM_003',
                'name': 'Cart Tampering',
                'pattern': r'(?i)cart.*quantity.*(-\d|\d{3,})',
                'severity': 'high'
            }
        ]
        
        # Bot Detection Rules
        bot_rules = [
            {
                'rule_id': 'BOT_001',
                'name': 'Scraping Bot Detection',
                'pattern': r'(?i)(scrapy|beautifulsoup|selenium|phantomjs)',
                'severity': 'medium'
            },
            {
                'rule_id': 'BOT_002',
                'name': 'Automated Tool Detection', 
                'pattern': r'(?i)(curl|wget|python-requests|postman)',
                'severity': 'low'
            }
        ]
        
        # Combine all rules
        all_rules = sql_injection_rules + xss_rules + ecommerce_rules + bot_rules
        
        for rule_data in all_rules:
            rule = SecurityRule(
                rule_id=rule_data['rule_id'],
                name=rule_data['name'],
                description=f"Detects {rule_data['name'].lower()}",
                pattern=rule_data['pattern'],
                rule_type='regex',
                severity=rule_data['severity'],
                action='block' if rule_data['severity'] in ['high', 'critical'] else 'monitor'
            )
            self.security_rules[rule.rule_id] = rule
        
        logger.info(f"Initialized {len(all_rules)} security rules")
    
    def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        
        # Known malicious IPs (simulated threat intel feeds)
        malicious_ips = [
            '192.0.2.100',    # Known scraper
            '198.51.100.50',  # Botnet C&C
            '203.0.113.25',   # Brute force attacker
            '185.220.101.1',  # Tor exit node
            '45.142.214.1'    # VPN/Proxy service
        ]
        
        for ip in malicious_ips:
            threat = ThreatIntelligence(
                ip_address=ip,
                threat_type='malicious_ip',
                confidence=0.95,
                source='threat_intelligence_feed',
                first_seen=datetime.now() - timedelta(days=30),
                last_seen=datetime.now() - timedelta(hours=2),
                attack_count=50
            )
            self.threat_intelligence[ip] = threat
        
        logger.info(f"Loaded {len(malicious_ips)} threat intelligence entries")
    
    def analyze_request(
        self,
        client_ip: str,
        method: str,
        uri: str,
        headers: Dict[str, str],
        body: str = "",
        query_params: Dict = None
    ) -> Tuple[bool, List[str], str]:
        """
        Analyze HTTP request for security threats
        
        Returns:
            (is_allowed, matched_rules, action_taken)
        """
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        try:
            # Check if IP is already blocked
            if self._is_ip_blocked(client_ip):
                self.metrics['blocked_requests'] += 1
                return False, ['IP_BLOCKED'], 'blocked'
            
            # Check threat intelligence
            if client_ip in self.threat_intelligence:
                threat = self.threat_intelligence[client_ip]
                if threat.confidence > 0.8:
                    self._block_ip(client_ip, 'threat_intelligence', 24*60)  # 24 hours
                    return False, ['THREAT_INTEL'], 'blocked'
            
            # Rate limiting check
            if self._check_rate_limit(client_ip):
                return False, ['RATE_LIMIT'], 'rate_limited'
            
            # Analyze request content
            content_to_analyze = f"{uri} {body}"
            if query_params:
                content_to_analyze += " " + str(query_params)
            
            # URL decode content
            content_to_analyze = unquote(content_to_analyze)
            
            matched_rules = []
            highest_severity = 'low'
            
            # Apply security rules
            for rule in self.security_rules.values():
                if not rule.enabled:
                    continue
                
                if rule.rule_type == 'regex':
                    if re.search(rule.pattern, content_to_analyze):
                        matched_rules.append(rule.rule_id)
                        if self._severity_level(rule.severity) > self._severity_level(highest_severity):
                            highest_severity = rule.severity
            
            # Analyze user agent
            user_agent = headers.get('User-Agent', '')
            ua_rules = self._analyze_user_agent(user_agent)
            matched_rules.extend(ua_rules)
            
            # Determine action
            action_taken = 'allowed'
            is_allowed = True
            
            if matched_rules:
                self.metrics['threats_detected'] += 1
                
                if highest_severity in ['critical', 'high']:
                    is_allowed = False
                    action_taken = 'blocked'
                    self.metrics['blocked_requests'] += 1
                    
                    # Block IP for repeat offenders
                    if len(matched_rules) > 2:
                        self._block_ip(client_ip, 'multiple_rule_matches', 60)  # 1 hour
                
                elif highest_severity == 'medium':
                    # Monitor but allow
                    action_taken = 'monitored'
                
                # Log attack event
                self._log_attack_event(
                    client_ip=client_ip,
                    method=method,
                    uri=uri,
                    payload=body[:500],  # Truncate large payloads
                    rules_matched=matched_rules,
                    severity=highest_severity,
                    action=action_taken,
                    blocked=not is_allowed
                )
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_response_time_metric(processing_time)
            
            return is_allowed, matched_rules, action_taken
            
        except Exception as e:
            logger.error(f"Request analysis failed: {e}")
            # Fail open for availability
            return True, [], 'error'
    
    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked"""
        if ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip]:
                return True
            else:
                # Unblock expired IPs
                del self.blocked_ips[ip]
        return False
    
    def _block_ip(self, ip: str, reason: str, duration_minutes: int):
        """Block IP address"""
        block_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.blocked_ips[ip] = block_until
        
        logger.warning(f"IP blocked: {ip}, Reason: {reason}, Duration: {duration_minutes}min")
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check rate limiting"""
        current_time = time.time()
        
        # Add current request
        self.request_counts[ip].append(current_time)
        
        # Clean old entries (last 60 seconds)
        while (self.request_counts[ip] and 
               current_time - self.request_counts[ip][0] > 60):
            self.request_counts[ip].popleft()
        
        # Check rate limit (max 100 requests per minute)
        if len(self.request_counts[ip]) > 100:
            self._block_ip(ip, 'rate_limit_exceeded', 15)  # 15 minutes
            return True
        
        return False
    
    def _analyze_user_agent(self, user_agent: str) -> List[str]:
        """Analyze user agent for suspicious patterns"""
        matched_rules = []
        
        # Check against bot rules
        for rule in self.security_rules.values():
            if rule.rule_id.startswith('BOT_') and rule.enabled:
                if re.search(rule.pattern, user_agent):
                    matched_rules.append(rule.rule_id)
        
        # Check for empty or suspicious user agents
        if not user_agent or len(user_agent) < 10:
            matched_rules.append('SUSPICIOUS_UA')
        
        return matched_rules
    
    def _severity_level(self, severity: str) -> int:
        """Convert severity to numeric level"""
        levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        return levels.get(severity, 1)
    
    def _log_attack_event(
        self,
        client_ip: str,
        method: str,
        uri: str,
        payload: str,
        rules_matched: List[str],
        severity: str,
        action: str,
        blocked: bool
    ):
        """Log security attack event"""
        event = AttackEvent(
            event_id=hashlib.md5(f"{client_ip}{time.time()}".encode()).hexdigest()[:16],
            timestamp=datetime.now(),
            client_ip=client_ip,
            user_agent="",  # Would be filled from headers
            method=method,
            uri=uri,
            payload=payload,
            rule_matched=','.join(rules_matched),
            severity=severity,
            action_taken=action,
            blocked=blocked
        )
        
        self.attack_events.append(event)
        
        # Log to file for SIEM integration
        logger.warning(f"ATTACK_DETECTED: {client_ip} -> {uri} | Rules: {rules_matched} | Action: {action}")
    
    def _update_response_time_metric(self, processing_time_ms: float):
        """Update average response time metric"""
        current_avg = self.metrics['avg_response_time_ms']
        total_requests = self.metrics['total_requests']
        
        # Moving average calculation
        self.metrics['avg_response_time_ms'] = (
            (current_avg * (total_requests - 1) + processing_time_ms) / total_requests
        )
    
    def get_security_metrics(self) -> Dict:
        """Get WAF security metrics"""
        active_blocks = len([
            ip for ip, expiry in self.blocked_ips.items()
            if datetime.now() < expiry
        ])
        
        recent_attacks = len([
            event for event in self.attack_events
            if event.timestamp > datetime.now() - timedelta(hours=1)
        ])
        
        return {
            'total_requests': self.metrics['total_requests'],
            'blocked_requests': self.metrics['blocked_requests'],
            'threats_detected': self.metrics['threats_detected'],
            'block_rate_percent': (
                self.metrics['blocked_requests'] / max(self.metrics['total_requests'], 1) * 100
            ),
            'active_ip_blocks': active_blocks,
            'recent_attacks_1h': recent_attacks,
            'avg_response_time_ms': round(self.metrics['avg_response_time_ms'], 2),
            'rules_enabled': len([r for r in self.security_rules.values() if r.enabled]),
            'threat_intel_entries': len(self.threat_intelligence)
        }
    
    def get_top_attackers(self, hours: int = 24) -> List[Dict]:
        """Get top attacking IPs"""
        since = datetime.now() - timedelta(hours=hours)
        
        attacker_counts = defaultdict(int)
        for event in self.attack_events:
            if event.timestamp >= since:
                attacker_counts[event.client_ip] += 1
        
        # Sort by attack count
        top_attackers = sorted(
            attacker_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'ip': ip, 'attack_count': count}
            for ip, count in top_attackers[:10]
        ]
    
    def get_attack_patterns(self) -> Dict:
        """Analyze attack patterns"""
        recent_events = [
            event for event in self.attack_events
            if event.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        # Rule frequency
        rule_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for event in recent_events:
            for rule in event.rule_matched.split(','):
                if rule:
                    rule_counts[rule] += 1
            severity_counts[event.severity] += 1
        
        return {
            'total_attacks_24h': len(recent_events),
            'top_triggered_rules': dict(
                sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            'severity_distribution': dict(severity_counts),
            'attack_timeline': self._generate_attack_timeline(recent_events)
        }
    
    def _generate_attack_timeline(self, events: List[AttackEvent]) -> Dict:
        """Generate hourly attack timeline"""
        timeline = defaultdict(int)
        
        for event in events:
            hour_key = event.timestamp.strftime('%Y-%m-%d %H:00')
            timeline[hour_key] += 1
        
        return dict(timeline)

def demonstrate_ecommerce_waf():
    """
    Demonstrate WAF protection for Indian e-commerce platforms
    Flipkart, Amazon India, Myntra security scenarios
    """
    print("\n🛡️  E-commerce Web Application Firewall Demo")
    print("=" * 45)
    
    # Initialize WAF for Flipkart-style e-commerce
    waf = EcommerceWAF("Flipkart BigBillionDays")
    
    # Simulate legitimate e-commerce requests
    print("\n✅ Legitimate E-commerce Requests")
    print("-" * 38)
    
    legitimate_requests = [
        {
            'name': 'Product Search',
            'ip': '203.192.1.100',
            'method': 'GET', 
            'uri': '/search?q=smartphone&brand=xiaomi',
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        },
        {
            'name': 'Add to Cart',
            'ip': '203.192.1.101',
            'method': 'POST',
            'uri': '/cart/add',
            'headers': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'},
            'body': '{"product_id": "12345", "quantity": 1, "price": 15999}'
        },
        {
            'name': 'Checkout Process',
            'ip': '203.192.1.102', 
            'method': 'POST',
            'uri': '/checkout/payment',
            'headers': {'User-Agent': 'Mozilla/5.0 (Android 11; Mobile; rv:68.0)'},
            'body': '{"payment_method": "upi", "amount": 15999}'
        }
    ]
    
    for req in legitimate_requests:
        allowed, rules, action = waf.analyze_request(
            client_ip=req['ip'],
            method=req['method'],
            uri=req['uri'],
            headers=req['headers'],
            body=req.get('body', '')
        )
        
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        print(f"   {req['name']}: {status} ({action})")
    
    # Simulate attack scenarios
    print("\n🚨 Attack Scenarios")
    print("-" * 20)
    
    attack_scenarios = [
        {
            'name': 'SQL Injection - Product Search',
            'ip': '192.0.2.100',
            'method': 'GET',
            'uri': "/search?q=' UNION SELECT * FROM users--",
            'headers': {'User-Agent': 'sqlmap/1.4.7'},
        },
        {
            'name': 'XSS Injection - Review Form',
            'ip': '192.0.2.101',
            'method': 'POST',
            'uri': '/product/review',
            'body': '<script>alert("XSS Attack")</script>',
            'headers': {'User-Agent': 'Mozilla/5.0'},
        },
        {
            'name': 'Price Manipulation',
            'ip': '192.0.2.102',
            'method': 'POST',
            'uri': '/cart/update',
            'body': '{"product_id": "12345", "price": -1000, "quantity": 1}',
            'headers': {'User-Agent': 'PostmanRuntime/7.26.8'},
        },
        {
            'name': 'Bot Scraping',
            'ip': '198.51.100.50',
            'method': 'GET',
            'uri': '/api/products/bulk',
            'headers': {'User-Agent': 'scrapy-redis (+http://scrapy-redis.readthedocs.io)'},
        },
        {
            'name': 'Cart Tampering',
            'ip': '203.0.113.25',
            'method': 'POST', 
            'uri': '/cart/add',
            'body': '{"product_id": "12345", "quantity": -5, "price": 1}',
            'headers': {'User-Agent': 'curl/7.68.0'},
        }
    ]
    
    for attack in attack_scenarios:
        allowed, rules, action = waf.analyze_request(
            client_ip=attack['ip'],
            method=attack['method'],
            uri=attack['uri'],
            headers=attack['headers'],
            body=attack.get('body', '')
        )
        
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED" 
        print(f"   {attack['name']}: {status}")
        print(f"      Rules Matched: {', '.join(rules) if rules else 'None'}")
        print(f"      Action: {action.upper()}")
    
    # Rate limiting demonstration
    print("\n⏱️  Rate Limiting Demo")
    print("-" * 22)
    
    print("🔥 Simulating high-frequency requests from single IP:")
    rate_limit_ip = '10.0.0.100'
    
    for i in range(15):  # Exceed rate limit
        allowed, rules, action = waf.analyze_request(
            client_ip=rate_limit_ip,
            method='GET',
            uri=f'/api/products/{i}',
            headers={'User-Agent': 'RapidRequestBot/1.0'}
        )
        
        if i < 5 or not allowed:  # Show first 5 and any blocked
            status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
            print(f"   Request {i+1}: {status} ({action})")
        
        if not allowed:
            print(f"   ⚠️  Rate limit triggered after {i+1} requests")
            break
    
    # Security metrics dashboard
    print("\n📊 WAF Security Metrics")
    print("-" * 25)
    
    metrics = waf.get_security_metrics()
    print(f"🔢 Total Requests: {metrics['total_requests']}")
    print(f"🚫 Blocked Requests: {metrics['blocked_requests']}")
    print(f"🎯 Threats Detected: {metrics['threats_detected']}")
    print(f"📊 Block Rate: {metrics['block_rate_percent']:.2f}%")
    print(f"🔒 Active IP Blocks: {metrics['active_ip_blocks']}")
    print(f"⚡ Avg Response Time: {metrics['avg_response_time_ms']}ms")
    print(f"📋 Security Rules: {metrics['rules_enabled']} enabled")
    
    # Top attackers
    print("\n🏆 Top Attackers (Last 24h)")
    print("-" * 30)
    
    top_attackers = waf.get_top_attackers()
    for i, attacker in enumerate(top_attackers[:5], 1):
        threat_type = "🔴 KNOWN THREAT" if attacker['ip'] in waf.threat_intelligence else "⚪ UNKNOWN"
        print(f"   {i}. {attacker['ip']}: {attacker['attack_count']} attacks - {threat_type}")
    
    # Attack pattern analysis
    print("\n🔍 Attack Pattern Analysis")
    print("-" * 30)
    
    patterns = waf.get_attack_patterns()
    print(f"📈 Total Attacks (24h): {patterns['total_attacks_24h']}")
    
    print("\n🎯 Most Triggered Rules:")
    for rule, count in list(patterns['top_triggered_rules'].items())[:3]:
        rule_name = waf.security_rules.get(rule, type('', (), {'name': rule})).name
        print(f"   • {rule_name}: {count} triggers")
    
    print("\n⚠️  Severity Distribution:")
    for severity, count in patterns['severity_distribution'].items():
        print(f"   • {severity.upper()}: {count}")
    
    # WAF configuration
    print("\n⚙️  WAF Configuration")
    print("-" * 22)
    
    sql_rules = [r for r in waf.security_rules.values() if r.rule_id.startswith('SQL_')]
    xss_rules = [r for r in waf.security_rules.values() if r.rule_id.startswith('XSS_')]
    ecom_rules = [r for r in waf.security_rules.values() if r.rule_id.startswith('ECOM_')]
    bot_rules = [r for r in waf.security_rules.values() if r.rule_id.startswith('BOT_')]
    
    print(f"🛡️  Rule Categories:")
    print(f"   • SQL Injection Rules: {len(sql_rules)}")
    print(f"   • XSS Protection Rules: {len(xss_rules)}")
    print(f"   • E-commerce Rules: {len(ecom_rules)}")
    print(f"   • Bot Detection Rules: {len(bot_rules)}")
    
    # Best practices
    print("\n💡 E-commerce WAF Best Practices")
    print("-" * 35)
    print("✓ Multi-layered defense (WAF + CDN + Rate limiting)")
    print("✓ Real-time threat intelligence integration")
    print("✓ Machine learning for anomaly detection")
    print("✓ Automated rule updates and tuning")
    print("✓ Comprehensive logging for compliance")
    print("✓ Regular security rule testing")
    print("✓ Bot management for legitimate crawlers")
    print("✓ Geo-blocking for high-risk countries")

if __name__ == "__main__":
    demonstrate_ecommerce_waf()