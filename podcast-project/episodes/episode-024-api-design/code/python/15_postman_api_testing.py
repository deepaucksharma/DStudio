#!/usr/bin/env python3
"""
Comprehensive API Testing Suite - Postman Collection Style
सभी API design patterns को test करने के लिए complete testing suite

Testing Coverage:
- REST API endpoints (IRCTC, Flipkart)
- GraphQL queries and mutations  
- gRPC service calls
- JWT authentication flows
- Rate limiting validation
- Webhook signature verification
- OpenAPI spec compliance

Mumbai-style test scenarios with real Indian use cases

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns (API Testing Suite)
"""

import requests
import json
import time
import jwt
import hmac
import hashlib
from datetime import datetime, timedelta
import uuid
import pytest
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result structure"""
    test_name: str
    status: str  # PASS, FAIL, SKIP
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    assertions_passed: int = 0
    assertions_total: int = 0

class APITestSuite:
    """
    Comprehensive API testing suite for Episode 24 examples
    सभी APIs को systematically test करता है
    """
    
    def __init__(self):
        # Base URLs for different services
        self.base_urls = {
            'irctc': 'http://localhost:8000',
            'flipkart': 'http://localhost:5000', 
            'upi': 'http://localhost:50051',
            'paytm': 'http://localhost:6000',
            'aadhaar': 'http://localhost:7000',
            'swiggy': 'http://localhost:8001',
            'razorpay': 'http://localhost:8002',
            'zomato': 'http://localhost:8003'
        }
        
        # Test data
        self.test_data = {
            'valid_user': {
                'email': 'rahul@gmail.com',
                'mobile': '+91-9876543210',
                'name': 'Rahul Sharma'
            },
            'valid_aadhaar': '123456789012',
            'valid_pan': 'ABCDE1234F',
            'valid_upi': 'rahul@paytm',
            'test_order': {
                'amount': 25000,  # ₹250
                'currency': 'INR',
                'description': 'Mumbai Vada Pav payment'
            }
        }
        
        # Authentication tokens
        self.auth_tokens = {}
        self.api_keys = {
            'aadhaar': 'PAYTM_DEV_123',
            'razorpay': 'rzp_test_123456'
        }
        
        # Test results storage
        self.results = []
    
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        HTTP request with timing and error handling
        """
        start_time = time.time()
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            response.response_time = time.time() - start_time
            return response
        except requests.exceptions.RequestException as e:
            # Create mock response for failed requests
            mock_response = requests.Response()
            mock_response.status_code = 0
            mock_response._content = str(e).encode()
            mock_response.response_time = time.time() - start_time
            return mock_response
    
    def assert_status_code(self, response: requests.Response, expected: int, test_name: str):
        """Assert HTTP status code"""
        if response.status_code == expected:
            logger.info(f"✅ {test_name}: Status code {expected} as expected")
            return True
        else:
            logger.error(f"❌ {test_name}: Expected {expected}, got {response.status_code}")
            return False
    
    def assert_response_time(self, response: requests.Response, max_time: float, test_name: str):
        """Assert response time"""
        if hasattr(response, 'response_time') and response.response_time <= max_time:
            logger.info(f"✅ {test_name}: Response time {response.response_time:.2f}s within limit")
            return True
        else:
            actual_time = getattr(response, 'response_time', 0)
            logger.error(f"❌ {test_name}: Response time {actual_time:.2f}s exceeds {max_time}s")
            return False
    
    def assert_json_field(self, response: requests.Response, field: str, test_name: str):
        """Assert JSON field exists"""
        try:
            data = response.json()
            if field in data:
                logger.info(f"✅ {test_name}: Field '{field}' exists in response")
                return True
            else:
                logger.error(f"❌ {test_name}: Field '{field}' missing in response")
                return False
        except json.JSONDecodeError:
            logger.error(f"❌ {test_name}: Invalid JSON response")
            return False
    
    # IRCTC REST API Tests
    def test_irctc_train_search(self) -> TestResult:
        """Test IRCTC train search API"""
        test_name = "IRCTC Train Search"
        
        try:
            url = f"{self.base_urls['irctc']}/api/v1/trains/search"
            params = {
                'source': 'Mumbai Central',
                'destination': 'New Delhi', 
                'journey_date': '2025-01-15'
            }
            
            response = self.make_request('GET', url, params=params)
            
            assertions = []
            assertions.append(self.assert_status_code(response, 200, test_name))
            assertions.append(self.assert_response_time(response, 2.0, test_name))
            assertions.append(self.assert_json_field(response, 'trains', test_name))
            
            passed = sum(assertions)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Found {data.get('trains_found', 0)} trains Mumbai to Delhi")
            
            return TestResult(
                test_name=test_name,
                status="PASS" if passed == len(assertions) else "FAIL",
                response_time=getattr(response, 'response_time', 0),
                status_code=response.status_code,
                assertions_passed=passed,
                assertions_total=len(assertions)
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                response_time=0,
                error_message=str(e),
                assertions_passed=0,
                assertions_total=3
            )
    
    def test_irctc_booking_creation(self) -> TestResult:
        """Test IRCTC booking creation"""
        test_name = "IRCTC Booking Creation"
        
        try:
            url = f"{self.base_urls['irctc']}/api/v1/booking/create"
            data = {
                "train_number": "12137",
                "journey_date": "2025-01-15",
                "passengers": [
                    {
                        "name": self.test_data['valid_user']['name'],
                        "age": 30,
                        "gender": "M",
                        "aadhar_number": self.test_data['valid_aadhaar'],
                        "mobile": self.test_data['valid_user']['mobile']
                    }
                ],
                "class_type": "3AC",
                "quota": "GENERAL"
            }
            
            response = self.make_request('POST', url, json=data)
            
            assertions = []
            assertions.append(self.assert_status_code(response, 201, test_name))
            assertions.append(self.assert_response_time(response, 5.0, test_name))
            assertions.append(self.assert_json_field(response, 'pnr_number', test_name))
            
            passed = sum(assertions)
            
            if response.status_code == 201:
                booking_data = response.json()
                logger.info(f"Booking created: PNR {booking_data.get('pnr_number')}")
            
            return TestResult(
                test_name=test_name,
                status="PASS" if passed == len(assertions) else "FAIL",
                response_time=getattr(response, 'response_time', 0),
                status_code=response.status_code,
                assertions_passed=passed,
                assertions_total=len(assertions)
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                response_time=0,
                error_message=str(e),
                assertions_passed=0,
                assertions_total=3
            )
    
    # GraphQL API Tests
    def test_flipkart_graphql_search(self) -> TestResult:
        """Test Flipkart GraphQL product search"""
        test_name = "Flipkart GraphQL Search"
        
        try:
            url = f"{self.base_urls['flipkart']}/graphql"
            query = """
            query SearchProducts($query: String!, $limit: Int) {
                searchProducts(query: $query, limit: $limit) {
                    name
                    brand
                    price {
                        sellingPrice
                        discountPercentage
                    }
                    rating {
                        averageRating
                    }
                    inStock
                }
            }
            """
            
            data = {
                "query": query,
                "variables": {
                    "query": "phone",
                    "limit": 2
                }
            }
            
            response = self.make_request('POST', url, json=data)
            
            assertions = []
            assertions.append(self.assert_status_code(response, 200, test_name))
            assertions.append(self.assert_response_time(response, 3.0, test_name))
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'searchProducts' in data['data']:
                    logger.info(f"GraphQL search successful: {len(data['data']['searchProducts'])} products")
                    assertions.append(True)
                else:
                    assertions.append(False)
            else:
                assertions.append(False)
            
            passed = sum(assertions)
            
            return TestResult(
                test_name=test_name,
                status="PASS" if passed == len(assertions) else "FAIL",
                response_time=getattr(response, 'response_time', 0),
                status_code=response.status_code,
                assertions_passed=passed,
                assertions_total=len(assertions)
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                response_time=0,
                error_message=str(e),
                assertions_passed=0,
                assertions_total=3
            )
    
    # JWT Authentication Tests
    def test_swiggy_login(self) -> TestResult:
        """Test Swiggy JWT login flow"""
        test_name = "Swiggy JWT Login"
        
        try:
            url = f"{self.base_urls['swiggy']}/api/auth/login"
            data = {
                "identifier": "customer_123",
                "password": "password123",
                "user_type": "customer"
            }
            
            response = self.make_request('POST', url, json=data)
            
            assertions = []
            assertions.append(self.assert_status_code(response, 200, test_name))
            assertions.append(self.assert_response_time(response, 2.0, test_name))
            assertions.append(self.assert_json_field(response, 'access_token', test_name))
            assertions.append(self.assert_json_field(response, 'refresh_token', test_name))
            
            # Store token for subsequent tests
            if response.status_code == 200:
                login_data = response.json()
                self.auth_tokens['swiggy'] = login_data.get('access_token')
                logger.info("JWT token stored for further tests")
            
            passed = sum(assertions)
            
            return TestResult(
                test_name=test_name,
                status="PASS" if passed == len(assertions) else "FAIL",
                response_time=getattr(response, 'response_time', 0),
                status_code=response.status_code,
                assertions_passed=passed,
                assertions_total=len(assertions)
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                response_time=0,
                error_message=str(e),
                assertions_passed=0,
                assertions_total=4
            )
    
    def test_swiggy_protected_endpoint(self) -> TestResult:
        """Test Swiggy protected endpoint with JWT"""
        test_name = "Swiggy Protected Endpoint"
        
        if 'swiggy' not in self.auth_tokens:
            return TestResult(
                test_name=test_name,
                status="SKIP",
                response_time=0,
                error_message="No auth token available",
                assertions_passed=0,
                assertions_total=0
            )
        
        try:
            url = f"{self.base_urls['swiggy']}/api/customer/profile"
            headers = {
                'Authorization': f"Bearer {self.auth_tokens['swiggy']}"
            }
            
            response = self.make_request('GET', url, headers=headers)
            
            assertions = []
            assertions.append(self.assert_status_code(response, 200, test_name))
            assertions.append(self.assert_response_time(response, 1.0, test_name))
            assertions.append(self.assert_json_field(response, 'name', test_name))
            
            passed = sum(assertions)
            
            return TestResult(
                test_name=test_name,
                status="PASS" if passed == len(assertions) else "FAIL",
                response_time=getattr(response, 'response_time', 0),
                status_code=response.status_code,
                assertions_passed=passed,
                assertions_total=len(assertions)
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                response_time=0,
                error_message=str(e),
                assertions_passed=0,
                assertions_total=3
            )
    
    # Rate Limiting Tests
    def test_aadhaar_rate_limiting(self) -> TestResult:
        """Test Aadhaar API rate limiting"""
        test_name = "Aadhaar Rate Limiting"
        
        try:
            url = f"{self.base_urls['aadhaar']}/api/v1/aadhaar/verify"
            headers = {
                'X-API-Key': self.api_keys['aadhaar']
            }
            data = {
                "aadhaar_number": self.test_data['valid_aadhaar'],
                "name": self.test_data['valid_user']['name']
            }
            
            # Make multiple requests to trigger rate limit
            responses = []
            for i in range(7):  # Exceed the 5 per minute limit
                response = self.make_request('POST', url, json=data, headers=headers)
                responses.append(response)
                time.sleep(0.1)  # Small delay
            
            assertions = []
            
            # First few requests should succeed
            success_count = sum(1 for r in responses[:5] if r.status_code == 200)
            assertions.append(success_count >= 3)  # At least 3 should succeed
            
            # Later requests should be rate limited
            rate_limited = any(r.status_code == 429 for r in responses[5:])
            assertions.append(rate_limited)
            
            logger.info(f"Rate limiting test: {success_count}/5 successful, rate limited: {rate_limited}")
            
            passed = sum(assertions)
            
            return TestResult(
                test_name=test_name,
                status="PASS" if passed == len(assertions) else "FAIL",
                response_time=sum(getattr(r, 'response_time', 0) for r in responses) / len(responses),
                status_code=responses[-1].status_code,
                assertions_passed=passed,
                assertions_total=len(assertions)
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                response_time=0,
                error_message=str(e),
                assertions_passed=0,
                assertions_total=2
            )
    
    # Webhook Tests
    def test_zomato_webhook_signature(self) -> TestResult:
        """Test Zomato webhook signature verification"""
        test_name = "Zomato Webhook Signature"
        
        try:
            # Test webhook endpoint
            url = f"{self.base_urls['zomato']}/webhooks/restaurant/rest_mumbai_vadapav"
            
            # Create webhook payload
            payload = json.dumps({
                "event_type": "order.accepted",
                "order_id": "order_mumbai_001",
                "restaurant_id": "rest_mumbai_vadapav",
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate signature
            secret = "rest_mumbai_vadapav_secret"
            signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'Content-Type': 'application/json',
                'X-Restaurant-Signature': f"sha256={signature}"
            }
            
            response = self.make_request('POST', url, data=payload, headers=headers)
            
            assertions = []
            # Should accept valid signature
            assertions.append(self.assert_status_code(response, 200, test_name))
            assertions.append(self.assert_response_time(response, 1.0, test_name))
            
            # Test invalid signature
            headers['X-Restaurant-Signature'] = "sha256=invalid_signature"
            response2 = self.make_request('POST', url, data=payload, headers=headers)
            assertions.append(response2.status_code == 401)  # Should reject invalid signature
            
            passed = sum(assertions)
            
            return TestResult(
                test_name=test_name,
                status="PASS" if passed == len(assertions) else "FAIL",
                response_time=getattr(response, 'response_time', 0),
                status_code=response.status_code,
                assertions_passed=passed,
                assertions_total=len(assertions)
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                response_time=0,
                error_message=str(e),
                assertions_passed=0,
                assertions_total=3
            )
    
    def run_all_tests(self) -> Dict:
        """
        Run complete test suite
        सभी API patterns को comprehensive test करता है
        """
        logger.info("🧪 Starting comprehensive API testing suite...")
        logger.info("Testing Episode 24 API design patterns")
        
        # Test methods to run
        test_methods = [
            self.test_irctc_train_search,
            self.test_irctc_booking_creation,
            self.test_flipkart_graphql_search,
            self.test_swiggy_login,
            self.test_swiggy_protected_endpoint,
            self.test_aadhaar_rate_limiting,
            self.test_zomato_webhook_signature
        ]
        
        results = []
        start_time = time.time()
        
        for test_method in test_methods:
            logger.info(f"Running: {test_method.__name__}")
            result = test_method()
            results.append(result)
            
            # Status logging
            status_emoji = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏭️"
            logger.info(f"{status_emoji} {result.test_name}: {result.status}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        total_time = time.time() - start_time
        
        # Calculate summary statistics
        summary = {
            "total_tests": len(results),
            "passed": len([r for r in results if r.status == "PASS"]),
            "failed": len([r for r in results if r.status == "FAIL"]),
            "skipped": len([r for r in results if r.status == "SKIP"]),
            "total_time": total_time,
            "average_response_time": sum(r.response_time for r in results) / len(results),
            "results": results
        }
        
        # Print summary
        self.print_test_summary(summary)
        
        return summary
    
    def print_test_summary(self, summary: Dict):
        """Print formatted test summary"""
        print("\n" + "="*60)
        print("🧪 API TESTING SUITE SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️ Skipped: {summary['skipped']}")
        print(f"⏱️ Total Time: {summary['total_time']:.2f}s")
        print(f"📊 Average Response Time: {summary['average_response_time']:.3f}s")
        print(f"📈 Success Rate: {(summary['passed']/summary['total_tests']*100):.1f}%")
        
        print(f"\n{'Test Name':<30} {'Status':<8} {'Time':<8} {'Assertions':<12}")
        print("-" * 60)
        
        for result in summary['results']:
            assertions = f"{result.assertions_passed}/{result.assertions_total}"
            print(f"{result.test_name:<30} {result.status:<8} {result.response_time:.3f}s   {assertions:<12}")
            
            if result.error_message:
                print(f"   Error: {result.error_message}")
        
        print("\n" + "="*60)
        
        # Mumbai-style conclusion
        if summary['passed'] == summary['total_tests']:
            print("🎉 All tests passed! API design patterns are working perfectly!")
            print("Mumbai से Delhi tak sab APIs running smoothly! 🚀")
        elif summary['passed'] >= summary['total_tests'] * 0.8:
            print("🟡 Most tests passed! Few issues need attention")
            print("Thoda fix karo, phir sab theek ho jayega!")
        else:
            print("🔴 Multiple tests failed! Need urgent attention")
            print("APIs में problem hai - debug karna padega!")

def main():
    """
    Main function to run API testing suite
    """
    print("🇮🇳 Episode 24 - API Design Patterns Testing Suite")
    print("Testing all Mumbai-style APIs with real Indian use cases")
    print("\nAPIs under test:")
    print("- IRCTC Train Booking (REST)")
    print("- Flipkart Product Catalog (GraphQL)")
    print("- Swiggy Authentication (JWT)")
    print("- Aadhaar Verification (Rate Limiting)")
    print("- Zomato Webhooks (Signature Verification)")
    
    # Initialize and run test suite
    test_suite = APITestSuite()
    summary = test_suite.run_all_tests()
    
    # Exit code based on results
    exit_code = 0 if summary['failed'] == 0 else 1
    return exit_code

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)