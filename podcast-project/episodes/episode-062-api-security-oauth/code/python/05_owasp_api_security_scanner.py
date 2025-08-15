"""
OWASP API Security Scanner
=========================

यह comprehensive API security scanner है जो OWASP API Top 10
vulnerabilities को detect करता है। Banks और fintech companies
अपने APIs को secure रखने के लिए इसी तरह के tools use करती हैं।

OWASP API Top 10 (2023):
1. Broken Object Level Authorization
2. Broken Authentication  
3. Broken Object Property Level Authorization
4. Unrestricted Resource Consumption
5. Broken Function Level Authorization
6. Unrestricted Access to Sensitive Business Flows
7. Server Side Request Forgery (SSRF)
8. Security Misconfiguration
9. Improper Inventory Management
10. Unsafe Consumption of APIs

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

import asyncio
import aiohttp
import json
import re
import time
import ssl
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import hashlib
import logging
from urllib.parse import urljoin, urlparse, parse_qs
import yaml

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VulnerabilityLevel(Enum):
    """Vulnerability severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ScanType(Enum):
    """Types of security scans"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INJECTION = "injection"
    MISCONFIGURATION = "misconfiguration"
    BUSINESS_LOGIC = "business_logic"
    SSRF = "ssrf"
    RATE_LIMITING = "rate_limiting"

@dataclass
class Vulnerability:
    """Vulnerability information"""
    id: str
    title: str
    description: str
    severity: VulnerabilityLevel
    owasp_category: str
    cwe_id: Optional[str]
    endpoint: str
    method: str
    evidence: Dict[str, Any]
    recommendation: str
    references: List[str]

@dataclass
class ScanResult:
    """Complete scan result"""
    target_url: str
    scan_id: str
    start_time: datetime
    end_time: datetime
    vulnerabilities: List[Vulnerability]
    endpoints_scanned: int
    tests_performed: int
    scan_summary: Dict[str, int]

class APIEndpointDiscovery:
    """API endpoint discovery और analysis"""
    
    def __init__(self):
        self.discovered_endpoints = set()
        self.api_patterns = [
            r'/api/v\d+/',
            r'/v\d+/',
            r'/rest/',
            r'/graphql',
            r'/webhook'
        ]
    
    async def discover_endpoints(self, base_url: str, session: aiohttp.ClientSession) -> List[Dict[str, str]]:
        """API endpoints discover करता है"""
        
        endpoints = []
        
        # Common API paths to check
        common_paths = [
            '/api', '/api/v1', '/api/v2', '/v1', '/v2',
            '/rest', '/rest/api', '/graphql',
            '/users', '/user', '/accounts', '/account',
            '/auth', '/login', '/register', '/logout',
            '/admin', '/dashboard', '/config',
            '/payments', '/transactions', '/orders',
            '/docs', '/swagger', '/openapi.json'
        ]
        
        # HTTP methods to test
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        for path in common_paths:
            url = urljoin(base_url, path)
            
            for method in methods:
                try:
                    async with session.request(method, url, timeout=5) as response:
                        if response.status != 404:
                            endpoints.append({
                                'url': url,
                                'method': method,
                                'status': response.status,
                                'content_type': response.headers.get('content-type', '')
                            })
                            
                            logger.info(f"Discovered: {method} {url} -> {response.status}")
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    continue
        
        # Try to discover from robots.txt और sitemap
        await self._discover_from_robots(base_url, session, endpoints)
        await self._discover_from_swagger(base_url, session, endpoints)
        
        return endpoints
    
    async def _discover_from_robots(self, base_url: str, session: aiohttp.ClientSession, endpoints: List[Dict]):
        """robots.txt से endpoints discover करता है"""
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            async with session.get(robots_url) as response:
                if response.status == 200:
                    content = await response.text()
                    for line in content.split('\n'):
                        if 'Disallow:' in line or 'Allow:' in line:
                            path = line.split(':', 1)[1].strip()
                            if path.startswith('/'):
                                url = urljoin(base_url, path)
                                endpoints.append({
                                    'url': url,
                                    'method': 'GET',
                                    'status': 0,
                                    'source': 'robots.txt'
                                })
        except:
            pass
    
    async def _discover_from_swagger(self, base_url: str, session: aiohttp.ClientSession, endpoints: List[Dict]):
        """Swagger/OpenAPI spec से endpoints discover करता है"""
        
        swagger_paths = ['/swagger.json', '/openapi.json', '/api-docs', '/docs/swagger.json']
        
        for path in swagger_paths:
            try:
                swagger_url = urljoin(base_url, path)
                async with session.get(swagger_url) as response:
                    if response.status == 200:
                        spec = await response.json()
                        
                        # Parse OpenAPI spec
                        base_path = spec.get('basePath', '')
                        paths = spec.get('paths', {})
                        
                        for path, methods in paths.items():
                            full_path = base_path + path
                            url = urljoin(base_url, full_path)
                            
                            for method in methods.keys():
                                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                                    endpoints.append({
                                        'url': url,
                                        'method': method.upper(),
                                        'status': 0,
                                        'source': 'swagger'
                                    })
            except:
                continue

class OWASPAPIScanner:
    """
    OWASP API Top 10 Security Scanner
    
    Comprehensive API security testing tool
    """
    
    def __init__(self):
        self.session = None
        self.vulnerabilities = []
        self.scan_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.endpoint_discovery = APIEndpointDiscovery()
        
        # Test payloads for different attacks
        self.sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT NULL,NULL,NULL--",
            "admin'--",
            "' OR 1=1#"
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]
        
        self.nosql_payloads = [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$where": "this.password.match(/.*/)"}',
            '{"$regex": ".*"}'
        ]
        
        # Common sensitive file paths
        self.sensitive_files = [
            '/.env', '/config.json', '/config.yml',
            '/backup.sql', '/database.sql', '/dump.sql',
            '/admin/config.php', '/wp-config.php',
            '/.git/config', '/.svn/entries',
            '/id_rsa', '/id_dsa', '/.ssh/id_rsa'
        ]
    
    async def scan_api(self, target_url: str, auth_token: Optional[str] = None) -> ScanResult:
        """Complete API security scan करता है"""
        
        start_time = datetime.utcnow()
        logger.info(f"Starting OWASP API security scan for: {target_url}")
        
        # Setup session with proper headers
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL verification for testing
        
        headers = {
            'User-Agent': 'OWASP-API-Scanner/1.0 (Security Testing)',
            'Accept': 'application/json, */*',
            'Content-Type': 'application/json'
        }
        
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        async with aiohttp.ClientSession(
            timeout=timeout, 
            connector=connector, 
            headers=headers
        ) as session:
            
            self.session = session
            
            # 1. Endpoint Discovery
            logger.info("🔍 Discovering API endpoints...")
            endpoints = await self.endpoint_discovery.discover_endpoints(target_url, session)
            logger.info(f"Found {len(endpoints)} endpoints")
            
            # 2. Run all OWASP Top 10 tests
            await self._test_broken_object_authorization(endpoints)
            await self._test_broken_authentication(endpoints)
            await self._test_broken_property_authorization(endpoints)
            await self._test_unrestricted_resource_consumption(endpoints)
            await self._test_broken_function_authorization(endpoints)
            await self._test_business_flow_restrictions(endpoints)
            await self._test_ssrf_vulnerabilities(endpoints)
            await self._test_security_misconfiguration(endpoints)
            await self._test_inventory_management(endpoints)
            await self._test_unsafe_api_consumption(endpoints)
        
        end_time = datetime.utcnow()
        
        # Generate scan summary
        scan_summary = self._generate_scan_summary()
        
        return ScanResult(
            target_url=target_url,
            scan_id=self.scan_id,
            start_time=start_time,
            end_time=end_time,
            vulnerabilities=self.vulnerabilities,
            endpoints_scanned=len(endpoints),
            tests_performed=len(self.vulnerabilities),
            scan_summary=scan_summary
        )
    
    async def _test_broken_object_authorization(self, endpoints: List[Dict]):
        """OWASP #1: Broken Object Level Authorization"""
        
        logger.info("Testing: Broken Object Level Authorization")
        
        for endpoint in endpoints:
            if endpoint['method'] in ['GET', 'PUT', 'DELETE']:
                url = endpoint['url']
                
                # Test for IDOR (Insecure Direct Object Reference)
                if re.search(r'/(\d+|[a-f0-9-]{36})/?$', url):
                    await self._test_idor_vulnerability(url, endpoint['method'])
                
                # Test for user enumeration
                if '/users/' in url or '/user/' in url:
                    await self._test_user_enumeration(url, endpoint['method'])
    
    async def _test_idor_vulnerability(self, url: str, method: str):
        """IDOR vulnerability test करता है"""
        
        # Extract ID from URL
        id_match = re.search(r'/(\d+|[a-f0-9-]{36})/?$', url)
        if not id_match:
            return
        
        original_id = id_match.group(1)
        
        # Test with different IDs
        test_ids = ['1', '2', '999', '0', '-1', 'admin', 'test']
        
        if original_id.isdigit():
            test_ids.extend([str(int(original_id) + 1), str(int(original_id) - 1)])
        
        for test_id in test_ids:
            test_url = url.replace(original_id, test_id)
            
            try:
                async with self.session.request(method, test_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check if response contains sensitive data
                        if self._contains_sensitive_data(content):
                            self.vulnerabilities.append(Vulnerability(
                                id=f"IDOR_{hashlib.md5(test_url.encode()).hexdigest()[:8]}",
                                title="Insecure Direct Object Reference (IDOR)",
                                description=f"Endpoint allows access to other users' data by manipulating ID parameter",
                                severity=VulnerabilityLevel.HIGH,
                                owasp_category="API1:2023 - Broken Object Level Authorization",
                                cwe_id="CWE-639",
                                endpoint=test_url,
                                method=method,
                                evidence={
                                    "original_id": original_id,
                                    "test_id": test_id,
                                    "response_status": response.status,
                                    "response_length": len(content)
                                },
                                recommendation="Implement proper authorization checks for object access",
                                references=[
                                    "https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/"
                                ]
                            ))
            except:
                continue
    
    async def _test_user_enumeration(self, url: str, method: str):
        """User enumeration vulnerability test करता है"""
        
        test_users = ['admin', 'test', 'user1', 'nonexistent_user_123456']
        
        responses = {}
        
        for user in test_users:
            test_url = url.replace('/users/', f'/users/{user}').replace('/user/', f'/user/{user}')
            
            try:
                async with self.session.request(method, test_url) as response:
                    responses[user] = {
                        'status': response.status,
                        'content_length': len(await response.text()),
                        'response_time': time.time()
                    }
            except:
                continue
        
        # Analyze response patterns
        if len(set(r['status'] for r in responses.values())) > 1:
            self.vulnerabilities.append(Vulnerability(
                id=f"USER_ENUM_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                title="User Enumeration Vulnerability",
                description="Different responses for existing vs non-existing users allow enumeration",
                severity=VulnerabilityLevel.MEDIUM,
                owasp_category="API1:2023 - Broken Object Level Authorization",
                cwe_id="CWE-204",
                endpoint=url,
                method=method,
                evidence={"response_patterns": responses},
                recommendation="Return consistent responses for both existing and non-existing users",
                references=["https://owasp.org/www-community/vulnerabilities/User_enumeration"]
            ))
    
    async def _test_broken_authentication(self, endpoints: List[Dict]):
        """OWASP #2: Broken Authentication"""
        
        logger.info("Testing: Broken Authentication")
        
        auth_endpoints = [ep for ep in endpoints if any(
            auth_path in ep['url'].lower() 
            for auth_path in ['/auth', '/login', '/signin', '/token']
        )]
        
        for endpoint in auth_endpoints:
            await self._test_weak_jwt(endpoint)
            await self._test_credential_stuffing(endpoint)
            await self._test_brute_force_protection(endpoint)
    
    async def _test_weak_jwt(self, endpoint: Dict):
        """Weak JWT implementation test करता है"""
        
        if endpoint['method'] != 'POST':
            return
        
        # Test for JWT with weak secrets
        weak_secrets = ['secret', '123456', 'password', 'jwt', 'key']
        
        for secret in weak_secrets:
            try:
                # Create a test JWT with weak secret
                import jwt
                payload = {"user": "admin", "role": "admin", "exp": time.time() + 3600}
                test_token = jwt.encode(payload, secret, algorithm="HS256")
                
                # Test if server accepts this token
                headers = {'Authorization': f'Bearer {test_token}'}
                
                async with self.session.get(endpoint['url'], headers=headers) as response:
                    if response.status in [200, 401]:  # Any meaningful response
                        self.vulnerabilities.append(Vulnerability(
                            id=f"WEAK_JWT_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                            title="Weak JWT Secret",
                            description="JWT tokens can be forged due to weak signing secret",
                            severity=VulnerabilityLevel.CRITICAL,
                            owasp_category="API2:2023 - Broken Authentication",
                            cwe_id="CWE-326",
                            endpoint=endpoint['url'],
                            method=endpoint['method'],
                            evidence={"weak_secret": secret, "forged_token": test_token[:50] + "..."},
                            recommendation="Use strong, randomly generated JWT signing secrets",
                            references=["https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/"]
                        ))
                        break
                        
            except Exception:
                continue
    
    async def _test_credential_stuffing(self, endpoint: Dict):
        """Credential stuffing protection test करता है"""
        
        if endpoint['method'] != 'POST':
            return
        
        # Common credential pairs
        common_creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('test', 'test'),
            ('guest', 'guest'),
            ('user', 'user')
        ]
        
        successful_logins = 0
        
        for username, password in common_creds:
            payload = {
                'username': username,
                'password': password,
                'email': f'{username}@test.com'
            }
            
            try:
                async with self.session.post(endpoint['url'], json=payload) as response:
                    if response.status == 200:
                        content = await response.text()
                        if 'token' in content.lower() or 'success' in content.lower():
                            successful_logins += 1
            except:
                continue
        
        if successful_logins > 0:
            self.vulnerabilities.append(Vulnerability(
                id=f"WEAK_CREDS_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                title="Weak Default Credentials",
                description="Default or weak credentials are accepted",
                severity=VulnerabilityLevel.HIGH,
                owasp_category="API2:2023 - Broken Authentication",
                cwe_id="CWE-521",
                endpoint=endpoint['url'],
                method=endpoint['method'],
                evidence={"successful_logins": successful_logins},
                recommendation="Enforce strong password policies and disable default accounts",
                references=["https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/"]
            ))
    
    async def _test_brute_force_protection(self, endpoint: Dict):
        """Brute force protection test करता है"""
        
        if endpoint['method'] != 'POST':
            return
        
        # Attempt multiple failed logins
        failed_attempts = 0
        
        for i in range(10):  # Try 10 failed attempts
            payload = {
                'username': 'testuser',
                'password': f'wrongpassword{i}'
            }
            
            try:
                start_time = time.time()
                async with self.session.post(endpoint['url'], json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status in [401, 403]:
                        failed_attempts += 1
                        
                        # Check if there's any delay or blocking
                        if response_time > 5:  # Artificial delay
                            return  # Good, rate limiting is working
                            
            except:
                continue
        
        # If all attempts completed without blocking
        if failed_attempts >= 8:
            self.vulnerabilities.append(Vulnerability(
                id=f"NO_BRUTE_FORCE_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                title="No Brute Force Protection",
                description="Login endpoint lacks brute force protection",
                severity=VulnerabilityLevel.MEDIUM,
                owasp_category="API2:2023 - Broken Authentication",
                cwe_id="CWE-307",
                endpoint=endpoint['url'],
                method=endpoint['method'],
                evidence={"failed_attempts_allowed": failed_attempts},
                recommendation="Implement account lockout and rate limiting for login attempts",
                references=["https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/"]
            ))
    
    async def _test_broken_property_authorization(self, endpoints: List[Dict]):
        """OWASP #3: Broken Object Property Level Authorization"""
        
        logger.info("Testing: Broken Object Property Level Authorization")
        
        for endpoint in endpoints:
            if endpoint['method'] in ['GET', 'POST', 'PUT']:
                await self._test_mass_assignment(endpoint)
                await self._test_sensitive_data_exposure(endpoint)
    
    async def _test_mass_assignment(self, endpoint: Dict):
        """Mass assignment vulnerability test करता है"""
        
        if endpoint['method'] not in ['POST', 'PUT']:
            return
        
        # Test payloads with admin fields
        test_payloads = [
            {'name': 'test', 'role': 'admin', 'is_admin': True},
            {'email': 'test@test.com', 'admin': True, 'privileges': ['admin']},
            {'username': 'test', 'role': 'superuser', 'permissions': 'all'}
        ]
        
        for payload in test_payloads:
            try:
                async with self.session.request(endpoint['method'], endpoint['url'], json=payload) as response:
                    if response.status in [200, 201]:
                        content = await response.text()
                        
                        # Check if admin fields were accepted
                        if any(field in content.lower() for field in ['admin', 'role', 'privilege']):
                            self.vulnerabilities.append(Vulnerability(
                                id=f"MASS_ASSIGN_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                                title="Mass Assignment Vulnerability",
                                description="API accepts unauthorized fields that could elevate privileges",
                                severity=VulnerabilityLevel.HIGH,
                                owasp_category="API3:2023 - Broken Object Property Level Authorization",
                                cwe_id="CWE-915",
                                endpoint=endpoint['url'],
                                method=endpoint['method'],
                                evidence={"accepted_payload": payload},
                                recommendation="Implement proper input validation and field whitelisting",
                                references=["https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/"]
                            ))
                            break
            except:
                continue
    
    async def _test_sensitive_data_exposure(self, endpoint: Dict):
        """Sensitive data exposure test करता है"""
        
        if endpoint['method'] != 'GET':
            return
        
        try:
            async with self.session.get(endpoint['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for sensitive data patterns
                    sensitive_patterns = [
                        r'password["\s]*[:=]["\s]*\w+',
                        r'api[_-]?key["\s]*[:=]["\s]*[\w-]+',
                        r'secret["\s]*[:=]["\s]*[\w-]+',
                        r'token["\s]*[:=]["\s]*[\w.-]+',
                        r'\d{16}',  # Credit card numbers
                        r'\d{3}-\d{2}-\d{4}',  # SSN pattern
                        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'  # Email
                    ]
                    
                    found_patterns = []
                    for pattern in sensitive_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            found_patterns.extend(matches[:3])  # Limit evidence
                    
                    if found_patterns:
                        self.vulnerabilities.append(Vulnerability(
                            id=f"SENSITIVE_DATA_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                            title="Sensitive Data Exposure",
                            description="API response contains sensitive information",
                            severity=VulnerabilityLevel.MEDIUM,
                            owasp_category="API3:2023 - Broken Object Property Level Authorization",
                            cwe_id="CWE-200",
                            endpoint=endpoint['url'],
                            method=endpoint['method'],
                            evidence={"exposed_data": found_patterns[:5]},  # Limit for privacy
                            recommendation="Filter sensitive data from API responses",
                            references=["https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/"]
                        ))
        except:
            pass
    
    async def _test_unrestricted_resource_consumption(self, endpoints: List[Dict]):
        """OWASP #4: Unrestricted Resource Consumption"""
        
        logger.info("Testing: Unrestricted Resource Consumption")
        
        for endpoint in endpoints:
            await self._test_rate_limiting(endpoint)
            await self._test_resource_exhaustion(endpoint)
    
    async def _test_rate_limiting(self, endpoint: Dict):
        """Rate limiting test करता है"""
        
        rapid_requests = 50
        successful_requests = 0
        
        tasks = []
        for i in range(rapid_requests):
            task = self._make_request(endpoint['url'], endpoint['method'])
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for response in responses:
                if hasattr(response, 'status') and response.status == 200:
                    successful_requests += 1
            
            # If most requests succeeded, there's likely no rate limiting
            if successful_requests > rapid_requests * 0.8:
                self.vulnerabilities.append(Vulnerability(
                    id=f"NO_RATE_LIMIT_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                    title="No Rate Limiting",
                    description="API endpoint lacks proper rate limiting",
                    severity=VulnerabilityLevel.MEDIUM,
                    owasp_category="API4:2023 - Unrestricted Resource Consumption",
                    cwe_id="CWE-770",
                    endpoint=endpoint['url'],
                    method=endpoint['method'],
                    evidence={
                        "total_requests": rapid_requests,
                        "successful_requests": successful_requests
                    },
                    recommendation="Implement proper rate limiting and request throttling",
                    references=["https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/"]
                ))
        except:
            pass
    
    async def _make_request(self, url: str, method: str):
        """Single request बनाता है rate limiting test के लिए"""
        try:
            async with self.session.request(method, url) as response:
                return response
        except:
            return None
    
    async def _test_resource_exhaustion(self, endpoint: Dict):
        """Resource exhaustion test करता है"""
        
        if endpoint['method'] not in ['POST', 'PUT']:
            return
        
        # Test with large payloads
        large_payloads = [
            {'data': 'A' * 10000},  # 10KB string
            {'array': ['item'] * 1000},  # Large array
            {'nested': {'level' + str(i): f'value{i}' for i in range(100)}}  # Deep nesting
        ]
        
        for payload in large_payloads:
            try:
                start_time = time.time()
                async with self.session.request(endpoint['method'], endpoint['url'], json=payload) as response:
                    response_time = time.time() - start_time
                    
                    # If server takes too long or accepts huge payload
                    if response_time > 10 or response.status == 200:
                        self.vulnerabilities.append(Vulnerability(
                            id=f"RESOURCE_EXHAUST_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                            title="Resource Exhaustion Vulnerability",
                            description="API accepts large payloads that could exhaust server resources",
                            severity=VulnerabilityLevel.MEDIUM,
                            owasp_category="API4:2023 - Unrestricted Resource Consumption",
                            cwe_id="CWE-400",
                            endpoint=endpoint['url'],
                            method=endpoint['method'],
                            evidence={
                                "payload_size": len(json.dumps(payload)),
                                "response_time": response_time
                            },
                            recommendation="Implement payload size limits and input validation",
                            references=["https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/"]
                        ))
                        break
            except:
                continue
    
    async def _test_broken_function_authorization(self, endpoints: List[Dict]):
        """OWASP #5: Broken Function Level Authorization"""
        
        logger.info("Testing: Broken Function Level Authorization")
        
        admin_endpoints = [ep for ep in endpoints if any(
            admin_path in ep['url'].lower() 
            for admin_path in ['/admin', '/manage', '/config', '/dashboard']
        )]
        
        for endpoint in admin_endpoints:
            await self._test_admin_access_without_auth(endpoint)
    
    async def _test_admin_access_without_auth(self, endpoint: Dict):
        """Admin functions की unauthorized access test करता है"""
        
        try:
            # Remove any authorization headers
            headers = {'User-Agent': 'Test'}
            
            async with self.session.request(endpoint['method'], endpoint['url'], headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check for admin content
                    admin_indicators = ['dashboard', 'admin', 'manage', 'configure', 'users', 'settings']
                    
                    if any(indicator in content.lower() for indicator in admin_indicators):
                        self.vulnerabilities.append(Vulnerability(
                            id=f"UNAUTH_ADMIN_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                            title="Unauthorized Admin Access",
                            description="Administrative function accessible without proper authorization",
                            severity=VulnerabilityLevel.CRITICAL,
                            owasp_category="API5:2023 - Broken Function Level Authorization",
                            cwe_id="CWE-285",
                            endpoint=endpoint['url'],
                            method=endpoint['method'],
                            evidence={"response_status": response.status},
                            recommendation="Implement proper role-based access control (RBAC)",
                            references=["https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/"]
                        ))
        except:
            pass
    
    async def _test_business_flow_restrictions(self, endpoints: List[Dict]):
        """OWASP #6: Business Flow Restrictions"""
        
        logger.info("Testing: Unrestricted Access to Sensitive Business Flows")
        
        # Test for business logic flaws
        for endpoint in endpoints:
            if any(term in endpoint['url'].lower() for term in ['payment', 'order', 'purchase', 'transaction']):
                await self._test_business_logic_flaws(endpoint)
    
    async def _test_business_logic_flaws(self, endpoint: Dict):
        """Business logic flaws test करता है"""
        
        if endpoint['method'] != 'POST':
            return
        
        # Test negative amounts, zero amounts, etc.
        test_payloads = [
            {'amount': -100, 'user_id': 'test'},  # Negative amount
            {'amount': 0, 'user_id': 'test'},     # Zero amount  
            {'quantity': -1, 'product_id': 'test'}, # Negative quantity
            {'price': 0.01, 'original_price': 1000}  # Price manipulation
        ]
        
        for payload in test_payloads:
            try:
                async with self.session.post(endpoint['url'], json=payload) as response:
                    if response.status in [200, 201]:
                        self.vulnerabilities.append(Vulnerability(
                            id=f"BUSINESS_LOGIC_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                            title="Business Logic Flaw",
                            description="API accepts invalid business logic parameters",
                            severity=VulnerabilityLevel.HIGH,
                            owasp_category="API6:2023 - Unrestricted Access to Sensitive Business Flows",
                            cwe_id="CWE-840",
                            endpoint=endpoint['url'],
                            method=endpoint['method'],
                            evidence={"accepted_payload": payload},
                            recommendation="Implement proper business logic validation",
                            references=["https://owasp.org/API-Security/editions/2023/en/0xa6-unrestricted-access-to-sensitive-business-flows/"]
                        ))
                        break
            except:
                continue
    
    async def _test_ssrf_vulnerabilities(self, endpoints: List[Dict]):
        """OWASP #7: Server Side Request Forgery (SSRF)"""
        
        logger.info("Testing: Server Side Request Forgery")
        
        for endpoint in endpoints:
            if endpoint['method'] in ['POST', 'PUT']:
                await self._test_ssrf(endpoint)
    
    async def _test_ssrf(self, endpoint: Dict):
        """SSRF vulnerability test करता है"""
        
        # SSRF test payloads
        ssrf_payloads = [
            {'url': 'http://localhost:22'},
            {'url': 'http://127.0.0.1:3306'},
            {'url': 'http://169.254.169.254/latest/meta-data/'},  # AWS metadata
            {'callback_url': 'http://localhost:8080'},
            {'webhook': 'file:///etc/passwd'}
        ]
        
        for payload in ssrf_payloads:
            try:
                async with self.session.request(endpoint['method'], endpoint['url'], json=payload) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for signs of successful SSRF
                        ssrf_indicators = ['connection', 'timeout', 'refused', 'internal', 'metadata']
                        
                        if any(indicator in content.lower() for indicator in ssrf_indicators):
                            self.vulnerabilities.append(Vulnerability(
                                id=f"SSRF_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                                title="Server Side Request Forgery (SSRF)",
                                description="API makes requests to internal resources based on user input",
                                severity=VulnerabilityLevel.HIGH,
                                owasp_category="API7:2023 - Server Side Request Forgery",
                                cwe_id="CWE-918",
                                endpoint=endpoint['url'],
                                method=endpoint['method'],
                                evidence={"test_payload": payload},
                                recommendation="Validate and sanitize all URL inputs, implement network restrictions",
                                references=["https://owasp.org/API-Security/editions/2023/en/0xa7-server-side-request-forgery/"]
                            ))
                            break
            except:
                continue
    
    async def _test_security_misconfiguration(self, endpoints: List[Dict]):
        """OWASP #8: Security Misconfiguration"""
        
        logger.info("Testing: Security Misconfiguration")
        
        # Test for common misconfigurations
        base_url = endpoints[0]['url'].split('/api')[0] if endpoints else ''
        
        await self._test_debug_endpoints(base_url)
        await self._test_default_credentials(endpoints)
        await self._test_error_handling(endpoints)
    
    async def _test_debug_endpoints(self, base_url: str):
        """Debug endpoints test करता है"""
        
        debug_paths = [
            '/debug', '/test', '/dev', '/api/debug',
            '/actuator/health', '/actuator/env',
            '/metrics', '/status', '/info'
        ]
        
        for path in debug_paths:
            url = urljoin(base_url, path)
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for sensitive debug info
                        if any(term in content.lower() for term in ['debug', 'environment', 'config', 'database']):
                            self.vulnerabilities.append(Vulnerability(
                                id=f"DEBUG_ENDPOINT_{hashlib.md5(url.encode()).hexdigest()[:8]}",
                                title="Debug Endpoint Exposed",
                                description="Debug or monitoring endpoint exposes sensitive information",
                                severity=VulnerabilityLevel.MEDIUM,
                                owasp_category="API8:2023 - Security Misconfiguration",
                                cwe_id="CWE-489",
                                endpoint=url,
                                method="GET",
                                evidence={"content_snippet": content[:200]},
                                recommendation="Disable debug endpoints in production",
                                references=["https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/"]
                            ))
            except:
                continue
    
    async def _test_default_credentials(self, endpoints: List[Dict]):
        """Default credentials test करता है"""
        
        # This is partially covered in authentication tests
        pass
    
    async def _test_error_handling(self, endpoints: List[Dict]):
        """Error handling test करता है"""
        
        for endpoint in endpoints:
            # Send malformed requests to trigger errors
            malformed_requests = [
                {'invalid': 'json"'},  # Invalid JSON
                'not_json_at_all',      # Not JSON
                {'sql': "'; DROP TABLE users; --"}  # SQL injection attempt
            ]
            
            for malformed in malformed_requests:
                try:
                    async with self.session.request(endpoint['method'], endpoint['url'], json=malformed) as response:
                        if response.status >= 500:
                            content = await response.text()
                            
                            # Check for stack traces or sensitive error info
                            error_indicators = ['traceback', 'stack trace', 'exception', 'file not found', 'database error']
                            
                            if any(indicator in content.lower() for indicator in error_indicators):
                                self.vulnerabilities.append(Vulnerability(
                                    id=f"VERBOSE_ERRORS_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                                    title="Verbose Error Messages",
                                    description="API returns detailed error messages that could help attackers",
                                    severity=VulnerabilityLevel.LOW,
                                    owasp_category="API8:2023 - Security Misconfiguration",
                                    cwe_id="CWE-209",
                                    endpoint=endpoint['url'],
                                    method=endpoint['method'],
                                    evidence={"error_response": content[:300]},
                                    recommendation="Implement generic error responses that don't leak implementation details",
                                    references=["https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/"]
                                ))
                                break
                except:
                    continue
    
    async def _test_inventory_management(self, endpoints: List[Dict]):
        """OWASP #9: Improper Inventory Management"""
        
        logger.info("Testing: Improper Inventory Management")
        
        # Test for outdated API versions
        await self._test_outdated_api_versions(endpoints)
    
    async def _test_outdated_api_versions(self, endpoints: List[Dict]):
        """Outdated API versions test करता है"""
        
        # Extract API versions from URLs
        versions = set()
        for endpoint in endpoints:
            version_match = re.search(r'/v(\d+)/', endpoint['url'])
            if version_match:
                versions.add(int(version_match.group(1)))
        
        if len(versions) > 1:
            # Multiple versions found
            max_version = max(versions)
            
            for version in versions:
                if version < max_version:
                    self.vulnerabilities.append(Vulnerability(
                        id=f"OUTDATED_API_V{version}",
                        title="Outdated API Version",
                        description=f"API version v{version} is still accessible while v{max_version} exists",
                        severity=VulnerabilityLevel.LOW,
                        owasp_category="API9:2023 - Improper Inventory Management",
                        cwe_id="CWE-1059",
                        endpoint=f"/v{version}/",
                        method="*",
                        evidence={"outdated_version": version, "current_version": max_version},
                        recommendation="Deprecate and remove outdated API versions",
                        references=["https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/"]
                    ))
    
    async def _test_unsafe_api_consumption(self, endpoints: List[Dict]):
        """OWASP #10: Unsafe Consumption of APIs"""
        
        logger.info("Testing: Unsafe Consumption of APIs")
        
        # This test is more about how the API consumes third-party APIs
        # We'll test for potential integration vulnerabilities
        for endpoint in endpoints:
            if endpoint['method'] in ['POST', 'PUT']:
                await self._test_third_party_api_consumption(endpoint)
    
    async def _test_third_party_api_consumption(self, endpoint: Dict):
        """Third-party API consumption vulnerabilities test करता है"""
        
        # Test payloads that might be passed to third-party APIs
        test_payloads = [
            {'api_key': '../../../etc/passwd'},
            {'external_url': 'javascript:alert("XSS")'},
            {'webhook_url': 'http://localhost:22'}
        ]
        
        for payload in test_payloads:
            try:
                async with self.session.request(endpoint['method'], endpoint['url'], json=payload) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for signs of unsafe consumption
                        if 'error' in content.lower() and any(term in content.lower() for term in ['external', 'api', 'request']):
                            self.vulnerabilities.append(Vulnerability(
                                id=f"UNSAFE_API_CONSUMPTION_{hashlib.md5(endpoint['url'].encode()).hexdigest()[:8]}",
                                title="Unsafe API Consumption",
                                description="API may unsafely consume third-party services with user input",
                                severity=VulnerabilityLevel.MEDIUM,
                                owasp_category="API10:2023 - Unsafe Consumption of APIs",
                                cwe_id="CWE-20",
                                endpoint=endpoint['url'],
                                method=endpoint['method'],
                                evidence={"test_payload": payload},
                                recommendation="Validate and sanitize all data sent to third-party APIs",
                                references=["https://owasp.org/API-Security/editions/2023/en/0xa10-unsafe-consumption-of-apis/"]
                            ))
                            break
            except:
                continue
    
    def _contains_sensitive_data(self, content: str) -> bool:
        """Content में sensitive data है या नहीं check करता है"""
        
        sensitive_patterns = [
            r'password', r'secret', r'key', r'token',
            r'\d{16}', r'\d{3}-\d{2}-\d{4}',  # Credit card, SSN
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'  # Email
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _generate_scan_summary(self) -> Dict[str, int]:
        """Scan summary generate करता है"""
        
        summary = {
            'total_vulnerabilities': len(self.vulnerabilities),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for vuln in self.vulnerabilities:
            summary[vuln.severity.value] += 1
        
        return summary
    
    def generate_report(self, scan_result: ScanResult) -> str:
        """Detailed security report generate करता है"""
        
        report = f"""
OWASP API Security Scan Report
==============================

Target: {scan_result.target_url}
Scan ID: {scan_result.scan_id}
Scan Duration: {scan_result.end_time - scan_result.start_time}
Endpoints Scanned: {scan_result.endpoints_scanned}

VULNERABILITY SUMMARY:
---------------------
Total Vulnerabilities: {scan_result.scan_summary['total_vulnerabilities']}
🔴 Critical: {scan_result.scan_summary['critical']}
🟠 High: {scan_result.scan_summary['high']}
🟡 Medium: {scan_result.scan_summary['medium']}
🔵 Low: {scan_result.scan_summary['low']}
⚪ Info: {scan_result.scan_summary['info']}

DETAILED FINDINGS:
-----------------
"""
        
        for i, vuln in enumerate(scan_result.vulnerabilities, 1):
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠', 
                'medium': '🟡',
                'low': '🔵',
                'info': '⚪'
            }
            
            report += f"""
{i}. {severity_emoji[vuln.severity.value]} {vuln.title}
   Endpoint: {vuln.method} {vuln.endpoint}
   Severity: {vuln.severity.value.upper()}
   Category: {vuln.owasp_category}
   Description: {vuln.description}
   Recommendation: {vuln.recommendation}
   
"""
        
        report += f"""
OWASP API Top 10 Coverage:
--------------------------
✅ API1:2023 - Broken Object Level Authorization
✅ API2:2023 - Broken Authentication
✅ API3:2023 - Broken Object Property Level Authorization
✅ API4:2023 - Unrestricted Resource Consumption
✅ API5:2023 - Broken Function Level Authorization
✅ API6:2023 - Unrestricted Access to Sensitive Business Flows
✅ API7:2023 - Server Side Request Forgery
✅ API8:2023 - Security Misconfiguration
✅ API9:2023 - Improper Inventory Management
✅ API10:2023 - Unsafe Consumption of APIs

Generated by: OWASP API Security Scanner
Report Time: {datetime.utcnow().isoformat()}Z
"""
        
        return report

# Example usage
async def main():
    """Main function for testing the scanner"""
    
    scanner = OWASPAPIScanner()
    
    # Test target (use a test API or your own)
    target_url = "http://localhost:8000"  # Replace with actual target
    
    print("🔍 Starting OWASP API Security Scan...")
    print(f"🎯 Target: {target_url}")
    print("🛡️ Scanning for OWASP API Top 10 vulnerabilities...")
    
    try:
        # Run the scan
        scan_result = await scanner.scan_api(target_url)
        
        # Generate and print report
        report = scanner.generate_report(scan_result)
        print(report)
        
        # Save report to file
        with open(f'api_security_scan_{scan_result.scan_id}.txt', 'w') as f:
            f.write(report)
        
        print(f"📄 Report saved to: api_security_scan_{scan_result.scan_id}.txt")
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")

if __name__ == "__main__":
    print("🔐 OWASP API Security Scanner")
    print("📋 Comprehensive API security testing tool")
    print("🏦 Banking grade security assessment")
    print("⚡ OWASP API Top 10 (2023) coverage")
    
    asyncio.run(main())

"""
Production Usage Notes:
======================

1. Legal Compliance:
   - Only scan APIs you own or have permission to test
   - Follow responsible disclosure for vulnerabilities
   - Comply with local laws and regulations

2. Advanced Configuration:
   - Add custom authentication mechanisms
   - Implement custom payload generators
   - Add specific business logic tests
   - Integrate with CI/CD pipelines

3. Reporting Integration:
   - Export to SARIF format for tool integration
   - Send results to SIEM systems
   - Generate executive summaries
   - Track vulnerability remediation

4. Performance Optimization:
   - Implement concurrent scanning with rate limiting
   - Add intelligent payload selection
   - Cache endpoint discovery results
   - Optimize for large APIs

यह scanner professional security teams की level का API security testing provide करता है!
"""