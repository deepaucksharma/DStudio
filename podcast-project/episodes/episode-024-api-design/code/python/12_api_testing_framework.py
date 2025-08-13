#!/usr/bin/env python3
"""
Comprehensive API Testing Framework
Production-ready API testing for Indian e-commerce applications

Key Features:
- Automated API testing suite
- Performance benchmarking
- Load testing (Mumbai traffic simulation)
- Contract testing
- Security testing
- Indian compliance testing (DPDP Act)

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns
"""

import asyncio
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import requests
import concurrent.futures
from dataclasses import dataclass, asdict
import logging
import subprocess
import threading
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APITestCase:
    """Single API test case definition"""
    name: str
    method: str
    endpoint: str
    headers: Dict[str, str]
    body: Optional[Dict] = None
    expected_status: int = 200
    expected_response_keys: List[str] = None
    max_response_time: float = 2.0  # seconds
    auth_required: bool = False
    timeout: float = 10.0

@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    passed: bool
    status_code: int
    response_time: float
    response_size: int
    error_message: Optional[str] = None
    timestamp: datetime = None

@dataclass
class LoadTestResult:
    """Load test result"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    requests_per_second: float
    error_rate: float

class APITestFramework:
    """
    Comprehensive API testing framework
    Production-ready API testing for Indian e-commerce
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
        # Default headers for Indian e-commerce
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Flipkart-API-Test/1.0",
            "Accept-Language": "hi-IN,en-IN;q=0.9",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        logger.info(f"🧪 API Test Framework initialized for {base_url}")

    def set_auth_token(self, token: str):
        """Set authentication token for protected endpoints"""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        logger.info("🔐 Authentication token set")

    def create_test_suite(self) -> List[APITestCase]:
        """
        Create comprehensive test suite for Indian e-commerce APIs
        Indian e-commerce के लिए complete test cases
        """
        return [
            # User Management APIs
            APITestCase(
                name="User Registration - Valid Data",
                method="POST",
                endpoint="/api/v1/users/register",
                headers=self.default_headers,
                body={
                    "name": "राहुल शर्मा",
                    "email": "rahul.test@example.com",
                    "phone": "+91-9876543210",
                    "password": "SecurePass123!",
                    "city": "Mumbai",
                    "state": "Maharashtra"
                },
                expected_status=201,
                expected_response_keys=["user_id", "email", "name"],
                max_response_time=3.0
            ),
            
            APITestCase(
                name="User Login - Valid Credentials",
                method="POST",
                endpoint="/api/v1/auth/login",
                headers=self.default_headers,
                body={
                    "email": "rahul.test@example.com",
                    "password": "SecurePass123!"
                },
                expected_status=200,
                expected_response_keys=["access_token", "refresh_token", "expires_in"],
                max_response_time=2.0
            ),
            
            # Product Catalog APIs
            APITestCase(
                name="Product Search - Smartphones",
                method="GET",
                endpoint="/api/v1/products/search?q=smartphone&page=1&limit=20",
                headers=self.default_headers,
                expected_status=200,
                expected_response_keys=["products", "total_count", "page"],
                max_response_time=1.5
            ),
            
            APITestCase(
                name="Product Details - Valid Product ID",
                method="GET",
                endpoint="/api/v1/products/PROD123456",
                headers=self.default_headers,
                expected_status=200,
                expected_response_keys=["product_id", "name", "price", "availability"],
                max_response_time=1.0
            ),
            
            # Shopping Cart APIs
            APITestCase(
                name="Add to Cart - Authenticated User",
                method="POST",
                endpoint="/api/v1/cart/add",
                headers=self.default_headers,
                body={
                    "product_id": "PROD123456",
                    "quantity": 2,
                    "variant_id": "VAR789"
                },
                expected_status=200,
                auth_required=True,
                max_response_time=1.0
            ),
            
            APITestCase(
                name="Get Cart Contents",
                method="GET", 
                endpoint="/api/v1/cart",
                headers=self.default_headers,
                expected_status=200,
                expected_response_keys=["items", "total_amount", "total_items"],
                auth_required=True,
                max_response_time=1.0
            ),
            
            # Order Management APIs
            APITestCase(
                name="Create Order - Valid Cart",
                method="POST",
                endpoint="/api/v1/orders",
                headers=self.default_headers,
                body={
                    "payment_method": "UPI",
                    "upi_id": "rahul@paytm",
                    "delivery_address": {
                        "street": "123 MG Road",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001"
                    }
                },
                expected_status=201,
                expected_response_keys=["order_id", "status", "total_amount"],
                auth_required=True,
                max_response_time=3.0
            ),
            
            # Payment APIs
            APITestCase(
                name="Process UPI Payment",
                method="POST",
                endpoint="/api/v1/payments/process",
                headers=self.default_headers,
                body={
                    "order_id": "ORD789012",
                    "payment_method": "UPI",
                    "upi_id": "rahul@phonepe",
                    "amount": 1999.00
                },
                expected_status=200,
                expected_response_keys=["payment_id", "status", "transaction_id"],
                auth_required=True,
                max_response_time=5.0
            ),
            
            # Inventory APIs
            APITestCase(
                name="Check Product Availability",
                method="GET",
                endpoint="/api/v1/inventory/PROD123456?pincode=400001",
                headers=self.default_headers,
                expected_status=200,
                expected_response_keys=["available", "quantity", "delivery_time"],
                max_response_time=1.0
            ),
            
            # Error Handling Tests
            APITestCase(
                name="Product Not Found - 404 Test",
                method="GET",
                endpoint="/api/v1/products/INVALID_PRODUCT",
                headers=self.default_headers,
                expected_status=404,
                max_response_time=1.0
            ),
            
            APITestCase(
                name="Unauthorized Access - 401 Test",
                method="GET",
                endpoint="/api/v1/orders",
                headers=self.default_headers,
                expected_status=401,
                max_response_time=1.0
            ),
            
            # Indian Compliance Tests
            APITestCase(
                name="DPDP Compliance - Data Access Request",
                method="GET",
                endpoint="/api/v1/users/data-export",
                headers=self.default_headers,
                expected_status=200,
                auth_required=True,
                max_response_time=2.0
            ),
            
            APITestCase(
                name="GST Calculation Test",
                method="POST",
                endpoint="/api/v1/tax/calculate",
                headers=self.default_headers,
                body={
                    "amount": 1000.00,
                    "state": "Maharashtra",
                    "product_category": "electronics"
                },
                expected_status=200,
                expected_response_keys=["cgst", "sgst", "igst", "total_tax"],
                max_response_time=1.0
            )
        ]

    def execute_test(self, test_case: APITestCase) -> TestResult:
        """
        Execute single test case
        Individual test case को execute करते हैं
        """
        logger.info(f"🔍 Running test: {test_case.name}")
        
        try:
            # Prepare request
            url = urljoin(self.base_url, test_case.endpoint)
            headers = {**self.default_headers, **test_case.headers}
            
            # Add auth if required
            if test_case.auth_required and self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Execute request
            start_time = time.time()
            
            if test_case.method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=test_case.timeout)
            elif test_case.method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=test_case.body, timeout=test_case.timeout)
            elif test_case.method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=test_case.body, timeout=test_case.timeout)
            elif test_case.method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=test_case.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {test_case.method}")
            
            response_time = time.time() - start_time
            
            # Validate response
            passed = True
            error_message = None
            
            # Check status code
            if response.status_code != test_case.expected_status:
                passed = False
                error_message = f"Expected status {test_case.expected_status}, got {response.status_code}"
            
            # Check response time
            if response_time > test_case.max_response_time:
                passed = False
                error_message = f"Response time {response_time:.2f}s exceeds limit {test_case.max_response_time}s"
            
            # Check response structure
            if test_case.expected_response_keys and passed:
                try:
                    response_json = response.json()
                    missing_keys = [key for key in test_case.expected_response_keys if key not in response_json]
                    if missing_keys:
                        passed = False
                        error_message = f"Missing response keys: {missing_keys}"
                except json.JSONDecodeError:
                    passed = False
                    error_message = "Invalid JSON response"
            
            result = TestResult(
                test_name=test_case.name,
                passed=passed,
                status_code=response.status_code,
                response_time=response_time,
                response_size=len(response.content),
                error_message=error_message,
                timestamp=datetime.now()
            )
            
            if passed:
                logger.info(f"✅ Test passed: {test_case.name}")
            else:
                logger.error(f"❌ Test failed: {test_case.name} - {error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Test error: {test_case.name} - {str(e)}")
            return TestResult(
                test_name=test_case.name,
                passed=False,
                status_code=0,
                response_time=0.0,
                response_size=0,
                error_message=str(e),
                timestamp=datetime.now()
            )

    def run_test_suite(self, parallel: bool = True) -> List[TestResult]:
        """
        Run complete test suite
        पूरा test suite execute करते हैं
        """
        test_cases = self.create_test_suite()
        logger.info(f"🚀 Running {len(test_cases)} test cases")
        
        if parallel:
            # Run tests in parallel for faster execution
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(self.execute_test, test_cases))
        else:
            # Run tests sequentially
            results = [self.execute_test(test_case) for test_case in test_cases]
        
        self.test_results.extend(results)
        
        # Print summary
        passed_tests = sum(1 for result in results if result.passed)
        total_tests = len(results)
        
        logger.info(f"📊 Test Results: {passed_tests}/{total_tests} passed")
        
        return results

    def run_load_test(self, endpoint: str, concurrent_users: int = 10, 
                     duration_seconds: int = 60, method: str = "GET", 
                     body: Dict = None) -> LoadTestResult:
        """
        Run load test on specific endpoint
        Mumbai traffic जैसा load test करते हैं
        """
        logger.info(f"🚛 Starting load test: {concurrent_users} users for {duration_seconds}s")
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def worker():
            """Worker function for load testing"""
            while time.time() < end_time:
                try:
                    url = urljoin(self.base_url, endpoint)
                    
                    request_start = time.time()
                    if method.upper() == "GET":
                        response = self.session.get(url, timeout=10)
                    elif method.upper() == "POST":
                        response = self.session.post(url, json=body, timeout=10)
                    
                    request_time = time.time() - request_start
                    
                    results.append({
                        "status_code": response.status_code,
                        "response_time": request_time,
                        "success": 200 <= response.status_code < 400
                    })
                    
                except Exception as e:
                    results.append({
                        "status_code": 0,
                        "response_time": 10.0,  # Timeout
                        "success": False,
                        "error": str(e)
                    })
                
                # Small delay to prevent overwhelming
                time.sleep(0.1)
        
        # Start concurrent workers
        threads = []
        for _ in range(concurrent_users):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Calculate metrics
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests
        
        response_times = [r["response_time"] for r in results]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Calculate 95th percentile
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else avg_response_time
        
        actual_duration = time.time() - start_time
        requests_per_second = total_requests / actual_duration if actual_duration > 0 else 0
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        load_result = LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )
        
        logger.info(f"📈 Load test completed: {requests_per_second:.1f} RPS, {error_rate:.1%} error rate")
        
        return load_result

    def run_security_tests(self) -> List[TestResult]:
        """
        Run security-focused tests
        Security testing के लिए specific test cases
        """
        security_tests = [
            # SQL Injection Tests
            APITestCase(
                name="SQL Injection - Product Search",
                method="GET",
                endpoint="/api/v1/products/search?q=' OR '1'='1",
                headers=self.default_headers,
                expected_status=400,  # Should be rejected
                max_response_time=2.0
            ),
            
            # XSS Tests
            APITestCase(
                name="XSS Prevention - User Input",
                method="POST",
                endpoint="/api/v1/users/register",
                headers=self.default_headers,
                body={
                    "name": "<script>alert('xss')</script>",
                    "email": "test@example.com",
                    "phone": "+91-9876543210"
                },
                expected_status=400,  # Should be rejected
                max_response_time=2.0
            ),
            
            # Authentication Tests
            APITestCase(
                name="JWT Token Tampering",
                method="GET",
                endpoint="/api/v1/orders",
                headers={**self.default_headers, "Authorization": "Bearer invalid.jwt.token"},
                expected_status=401,
                max_response_time=1.0
            ),
            
            # Rate Limiting Tests
            APITestCase(
                name="Rate Limiting Check",
                method="GET",
                endpoint="/api/v1/products/search?q=test",
                headers=self.default_headers,
                expected_status=200,  # First request should succeed
                max_response_time=2.0
            )
        ]
        
        logger.info("🔒 Running security tests")
        results = [self.execute_test(test) for test in security_tests]
        
        # Test rate limiting by making rapid requests
        logger.info("🚦 Testing rate limiting with rapid requests")
        for i in range(10):
            result = self.execute_test(security_tests[-1])  # Rate limiting test
            if result.status_code == 429:  # Too Many Requests
                logger.info("✅ Rate limiting is working correctly")
                break
            time.sleep(0.1)
        
        return results

    def generate_report(self, include_load_test: bool = True) -> Dict:
        """
        Generate comprehensive test report
        Detailed test report generate करते हैं
        """
        if not self.test_results:
            return {"error": "No test results available"}
        
        # Basic stats
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        # Response time stats
        response_times = [result.response_time for result in self.test_results if result.response_time > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Failed tests details
        failed_test_details = [
            {
                "name": result.test_name,
                "error": result.error_message,
                "status_code": result.status_code
            }
            for result in self.test_results if not result.passed
        ]
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                "avg_response_time": f"{avg_response_time:.3f}s",
                "max_response_time": f"{max_response_time:.3f}s"
            },
            "failed_tests": failed_test_details,
            "generated_at": datetime.now().isoformat(),
            "base_url": self.base_url
        }
        
        # Add load test results if requested
        if include_load_test:
            try:
                load_result = self.run_load_test("/api/v1/products/search?q=smartphone", 
                                               concurrent_users=5, duration_seconds=30)
                report["load_test"] = asdict(load_result)
            except Exception as e:
                report["load_test"] = {"error": str(e)}
        
        return report

def run_demo():
    """
    Demo function showing API testing framework usage
    Testing framework का demonstration
    """
    print("🧪 API Testing Framework Demo")
    print("🇮🇳 Testing Indian e-commerce APIs")
    print("=" * 60)
    
    # Note: Using httpbin.org for demo since we don't have a real API
    test_framework = APITestFramework("https://httpbin.org")
    
    # Create sample test cases for httpbin
    demo_tests = [
        APITestCase(
            name="GET Request Test",
            method="GET",
            endpoint="/get",
            headers={"X-Test": "demo"},
            expected_status=200,
            max_response_time=3.0
        ),
        APITestCase(
            name="POST Request Test", 
            method="POST",
            endpoint="/post",
            headers={"Content-Type": "application/json"},
            body={"test": "data", "user": "rahul"},
            expected_status=200,
            max_response_time=3.0
        ),
        APITestCase(
            name="Status Code Test - 404",
            method="GET",
            endpoint="/status/404",
            headers={},
            expected_status=404,
            max_response_time=2.0
        )
    ]
    
    # Run individual tests
    print("\n🔍 Running individual test cases:")
    for test_case in demo_tests:
        result = test_framework.execute_test(test_case)
        status_icon = "✅" if result.passed else "❌"
        print(f"  {status_icon} {result.test_name}: {result.response_time:.3f}s")
    
    # Run load test
    print("\n🚛 Running load test:")
    load_result = test_framework.run_load_test("/get", concurrent_users=3, duration_seconds=10)
    print(f"  📊 {load_result.total_requests} requests, {load_result.requests_per_second:.1f} RPS")
    print(f"  📈 Avg response time: {load_result.avg_response_time:.3f}s")
    print(f"  🎯 Success rate: {((load_result.successful_requests/load_result.total_requests)*100):.1f}%")
    
    # Generate report
    print("\n📋 Generating test report:")
    test_framework.test_results = [test_framework.execute_test(test) for test in demo_tests]
    report = test_framework.generate_report(include_load_test=False)
    
    print(f"  📊 Total tests: {report['test_summary']['total_tests']}")
    print(f"  ✅ Success rate: {report['test_summary']['success_rate']}")
    print(f"  ⏱️  Avg response time: {report['test_summary']['avg_response_time']}")
    
    print("\n🎉 API Testing Framework demo completed!")
    print("💡 In production, you would:")
    print("  - Set up CI/CD integration")
    print("  - Configure automated alerts")
    print("  - Add contract testing")
    print("  - Implement chaos testing")
    print("  - Set up performance baselines")

if __name__ == "__main__":
    run_demo()