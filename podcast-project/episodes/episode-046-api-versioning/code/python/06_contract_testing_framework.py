#!/usr/bin/env python3
"""
Contract Testing Framework for API Versioning
Inspired by PhonePe's API contract management with merchant partners

Example: PhonePe ne kaise ensure kiya ki merchant integration break na ho
"""

import json
import jsonschema
import requests
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
import pytest
from unittest.mock import Mock
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractType(Enum):
    """Types of API contracts"""
    REQUEST_SCHEMA = "request_schema"
    RESPONSE_SCHEMA = "response_schema"
    BEHAVIOR_CONTRACT = "behavior_contract"
    PERFORMANCE_CONTRACT = "performance_contract"

class TestResult(Enum):
    """Contract test results"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIPPED = "skipped"

@dataclass
class ContractTest:
    """Individual contract test definition"""
    name: str
    contract_type: ContractType
    version: str
    schema: Dict[str, Any]
    test_data: List[Dict[str, Any]]
    expected_behavior: Optional[Dict[str, Any]] = None

@dataclass
class TestExecution:
    """Contract test execution result"""
    test_name: str
    result: TestResult
    message: str
    duration_ms: float
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class APIContractManager:
    """
    Contract testing framework for API versioning
    PhonePe style contract management for merchant APIs
    """
    
    def __init__(self):
        self.contracts = self._initialize_contracts()
        self.test_results = []
    
    def _initialize_contracts(self) -> Dict[str, List[ContractTest]]:
        """Initialize contract definitions for different versions"""
        
        # PhonePe Payment API v1 contracts
        payment_v1_request_schema = {
            "type": "object",
            "properties": {
                "merchant_id": {"type": "string", "minLength": 1},
                "transaction_id": {"type": "string", "minLength": 1},
                "amount": {"type": "number", "minimum": 1},
                "currency": {"type": "string", "enum": ["INR"]},
                "customer_mobile": {"type": "string", "pattern": "^[6-9]\\d{9}$"}
            },
            "required": ["merchant_id", "transaction_id", "amount", "currency"],
            "additionalProperties": False
        }
        
        payment_v1_response_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["SUCCESS", "FAILURE", "PENDING"]},
                "transaction_id": {"type": "string"},
                "phonepe_transaction_id": {"type": "string"},
                "amount": {"type": "number"},
                "message": {"type": "string"}
            },
            "required": ["status", "transaction_id", "phonepe_transaction_id"],
            "additionalProperties": True  # Allow additional fields for backward compatibility
        }
        
        # PhonePe Payment API v2 contracts (enhanced)
        payment_v2_request_schema = {
            "type": "object",
            "properties": {
                "merchant_id": {"type": "string", "minLength": 1},
                "transaction_id": {"type": "string", "minLength": 1},
                "amount": {"type": "number", "minimum": 1},
                "currency": {"type": "string", "enum": ["INR"]},
                "customer_mobile": {"type": "string", "pattern": "^[6-9]\\d{9}$"},
                # V2 additions
                "callback_url": {"type": "string", "format": "uri"},
                "payment_method": {"type": "string", "enum": ["UPI", "WALLET", "CARD"]},
                "customer_email": {"type": "string", "format": "email"},
                "description": {"type": "string", "maxLength": 100}
            },
            "required": ["merchant_id", "transaction_id", "amount", "currency", "callback_url"],
            "additionalProperties": False
        }
        
        payment_v2_response_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["SUCCESS", "FAILURE", "PENDING"]},
                "transaction_id": {"type": "string"},
                "phonepe_transaction_id": {"type": "string"},
                "amount": {"type": "number"},
                "message": {"type": "string"},
                # V2 additions
                "payment_method": {"type": "string"},
                "upi_transaction_id": {"type": "string"},
                "cashback_amount": {"type": "number", "minimum": 0},
                "estimated_settlement_time": {"type": "string"}
            },
            "required": ["status", "transaction_id", "phonepe_transaction_id"],
            "additionalProperties": True
        }
        
        return {
            "v1": [
                ContractTest(
                    name="payment_request_v1",
                    contract_type=ContractType.REQUEST_SCHEMA,
                    version="v1",
                    schema=payment_v1_request_schema,
                    test_data=[
                        {
                            "merchant_id": "M12345",
                            "transaction_id": "TXN_001",
                            "amount": 100.0,
                            "currency": "INR",
                            "customer_mobile": "9876543210"
                        },
                        {
                            "merchant_id": "M67890",
                            "transaction_id": "TXN_002",
                            "amount": 250.50,
                            "currency": "INR"
                        }
                    ]
                ),
                ContractTest(
                    name="payment_response_v1",
                    contract_type=ContractType.RESPONSE_SCHEMA,
                    version="v1",
                    schema=payment_v1_response_schema,
                    test_data=[
                        {
                            "status": "SUCCESS",
                            "transaction_id": "TXN_001",
                            "phonepe_transaction_id": "PP_TXN_001",
                            "amount": 100.0,
                            "message": "Payment successful"
                        }
                    ]
                )
            ],
            "v2": [
                ContractTest(
                    name="payment_request_v2",
                    contract_type=ContractType.REQUEST_SCHEMA,
                    version="v2",
                    schema=payment_v2_request_schema,
                    test_data=[
                        {
                            "merchant_id": "M12345",
                            "transaction_id": "TXN_V2_001",
                            "amount": 100.0,
                            "currency": "INR",
                            "customer_mobile": "9876543210",
                            "callback_url": "https://merchant.com/callback",
                            "payment_method": "UPI",
                            "customer_email": "customer@example.com",
                            "description": "Test payment"
                        }
                    ]
                ),
                ContractTest(
                    name="payment_response_v2",
                    contract_type=ContractType.RESPONSE_SCHEMA,
                    version="v2",
                    schema=payment_v2_response_schema,
                    test_data=[
                        {
                            "status": "SUCCESS",
                            "transaction_id": "TXN_V2_001",
                            "phonepe_transaction_id": "PP_TXN_V2_001",
                            "amount": 100.0,
                            "message": "Payment successful",
                            "payment_method": "UPI",
                            "upi_transaction_id": "UPI123456789",
                            "cashback_amount": 5.0,
                            "estimated_settlement_time": "T+1 day"
                        }
                    ]
                )
            ]
        }
    
    def validate_contract(self, contract_test: ContractTest, data: Dict[str, Any]) -> TestExecution:
        """
        Validate data against contract schema
        """
        start_time = datetime.now()
        
        try:
            # Validate against JSON schema
            jsonschema.validate(data, contract_test.schema)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestExecution(
                test_name=contract_test.name,
                result=TestResult.PASS,
                message="Contract validation passed",
                duration_ms=duration,
                timestamp=datetime.now().isoformat(),
                details={"validated_fields": list(data.keys())}
            )
            
        except jsonschema.ValidationError as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestExecution(
                test_name=contract_test.name,
                result=TestResult.FAIL,
                message=f"Contract validation failed: {e.message}",
                duration_ms=duration,
                timestamp=datetime.now().isoformat(),
                details={
                    "error_path": list(e.absolute_path),
                    "failed_value": e.instance,
                    "schema_path": list(e.schema_path)
                }
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestExecution(
                test_name=contract_test.name,
                result=TestResult.FAIL,
                message=f"Unexpected error: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now().isoformat()
            )
    
    def run_contract_tests(self, version: str) -> List[TestExecution]:
        """
        Run all contract tests for a specific version
        """
        if version not in self.contracts:
            return []
        
        results = []
        contracts = self.contracts[version]
        
        for contract in contracts:
            for test_data in contract.test_data:
                result = self.validate_contract(contract, test_data)
                results.append(result)
                self.test_results.append(result)
        
        return results
    
    def run_backward_compatibility_tests(self, from_version: str, to_version: str) -> List[TestExecution]:
        """
        Test backward compatibility between versions
        V1 data should work with V2 schema (with appropriate handling)
        """
        results = []
        
        if from_version not in self.contracts or to_version not in self.contracts:
            return results
        
        from_contracts = self.contracts[from_version]
        to_contracts = self.contracts[to_version]
        
        # Test if old request format works with new schema
        for from_contract in from_contracts:
            if from_contract.contract_type == ContractType.REQUEST_SCHEMA:
                # Find corresponding contract in new version
                to_contract = next(
                    (c for c in to_contracts if c.name.replace(f"_{to_version}", f"_{from_version}") == from_contract.name),
                    None
                )
                
                if to_contract:
                    for test_data in from_contract.test_data:
                        # Test old data against new schema
                        result = self.validate_contract(to_contract, test_data)
                        result.test_name = f"backward_compat_{from_version}_to_{to_version}_{from_contract.name}"
                        
                        # If validation fails, it might still be acceptable for backward compatibility
                        if result.result == TestResult.FAIL:
                            # Check if failure is due to missing non-required fields
                            missing_fields = self._check_missing_optional_fields(
                                test_data, to_contract.schema
                            )
                            if missing_fields:
                                result.result = TestResult.WARNING
                                result.message = f"Missing optional fields: {missing_fields}"
                        
                        results.append(result)
                        self.test_results.append(result)
        
        return results
    
    def _check_missing_optional_fields(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Check for missing optional fields in schema"""
        missing_fields = []
        
        if "properties" in schema:
            required_fields = set(schema.get("required", []))
            schema_fields = set(schema["properties"].keys())
            data_fields = set(data.keys())
            
            missing_fields = list(schema_fields - data_fields - required_fields)
        
        return missing_fields
    
    def generate_contract_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive contract testing report
        """
        total_tests = len(self.test_results)
        if total_tests == 0:
            return {"message": "No tests executed"}
        
        passed = len([r for r in self.test_results if r.result == TestResult.PASS])
        failed = len([r for r in self.test_results if r.result == TestResult.FAIL])
        warnings = len([r for r in self.test_results if r.result == TestResult.WARNING])
        
        avg_duration = sum(r.duration_ms for r in self.test_results) / total_tests
        
        # Group by test type
        test_by_type = {}
        for result in self.test_results:
            test_type = result.test_name.split('_')[0]
            if test_type not in test_by_type:
                test_by_type[test_type] = {"pass": 0, "fail": 0, "warning": 0}
            
            test_by_type[test_type][result.result.value] += 1
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": round((passed / total_tests) * 100, 2),
                "avg_duration_ms": round(avg_duration, 2)
            },
            "test_breakdown": test_by_type,
            "failed_tests": [
                {
                    "name": r.test_name,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.test_results if r.result == TestResult.FAIL
            ],
            "warnings": [
                {
                    "name": r.test_name,
                    "message": r.message
                }
                for r in self.test_results if r.result == TestResult.WARNING
            ],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r.result == TestResult.FAIL]
        warning_tests = [r for r in self.test_results if r.result == TestResult.WARNING]
        
        if failed_tests:
            recommendations.append("🚨 Fix failing contract tests before releasing")
            recommendations.append("Review schema definitions for accuracy")
        
        if warning_tests:
            recommendations.append("⚠️  Address warnings for better compatibility")
            recommendations.append("Consider making optional fields truly optional")
        
        if len(failed_tests) > len(self.test_results) * 0.1:  # >10% failure rate
            recommendations.append("High failure rate detected - review contract design")
        
        recommendations.extend([
            "Automate contract testing in CI/CD pipeline",
            "Version contract schemas along with API versions",
            "Provide contract test results to API consumers",
            "Monitor real-world API usage against contracts"
        ])
        
        return recommendations

class MockAPIServer:
    """
    Mock API server for contract testing
    Simulates PhonePe payment API responses
    """
    
    def __init__(self):
        self.request_logs = []
    
    def process_payment_v1(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock V1 payment processing"""
        self.request_logs.append({"version": "v1", "data": request_data})
        
        return {
            "status": "SUCCESS",
            "transaction_id": request_data["transaction_id"],
            "phonepe_transaction_id": f"PP_{request_data['transaction_id']}",
            "amount": request_data["amount"],
            "message": "Payment processed successfully"
        }
    
    def process_payment_v2(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock V2 payment processing with enhanced response"""
        self.request_logs.append({"version": "v2", "data": request_data})
        
        return {
            "status": "SUCCESS",
            "transaction_id": request_data["transaction_id"],
            "phonepe_transaction_id": f"PP_{request_data['transaction_id']}",
            "amount": request_data["amount"],
            "message": "Payment processed successfully",
            "payment_method": request_data.get("payment_method", "UPI"),
            "upi_transaction_id": f"UPI_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "cashback_amount": request_data["amount"] * 0.01,  # 1% cashback
            "estimated_settlement_time": "T+1 day"
        }

def demonstrate_contract_testing():
    """
    Demonstrate contract testing framework with PhonePe style examples
    """
    print("🔥 Contract Testing Framework - PhonePe API Style")
    print("=" * 60)
    
    # Initialize contract manager and mock server
    contract_manager = APIContractManager()
    mock_server = MockAPIServer()
    
    print("\n📋 Running Contract Tests...")
    
    # Test V1 contracts
    print("\n🔍 Testing V1 Contracts:")
    v1_results = contract_manager.run_contract_tests("v1")
    for result in v1_results:
        status_icon = "✅" if result.result == TestResult.PASS else "❌"
        print(f"  {status_icon} {result.test_name}: {result.message}")
    
    # Test V2 contracts
    print("\n🔍 Testing V2 Contracts:")
    v2_results = contract_manager.run_contract_tests("v2")
    for result in v2_results:
        status_icon = "✅" if result.result == TestResult.PASS else "❌"
        print(f"  {status_icon} {result.test_name}: {result.message}")
    
    # Test backward compatibility
    print("\n🔄 Testing Backward Compatibility (V1 -> V2):")
    compat_results = contract_manager.run_backward_compatibility_tests("v1", "v2")
    for result in compat_results:
        if result.result == TestResult.PASS:
            status_icon = "✅"
        elif result.result == TestResult.WARNING:
            status_icon = "⚠️"
        else:
            status_icon = "❌"
        print(f"  {status_icon} {result.test_name}: {result.message}")
    
    # Generate and display report
    print("\n📊 Contract Testing Report:")
    report = contract_manager.generate_contract_report()
    print(json.dumps(report, indent=2))
    
    print("\n💡 Contract Testing Benefits:")
    print("1. Catch breaking changes early in development")
    print("2. Ensure API consistency across versions")
    print("3. Validate merchant integration compatibility")
    print("4. Automate API quality assurance")
    print("5. Reduce production issues from contract violations")
    
    print("\n🎯 PhonePe Implementation Insights:")
    print("1. Strict schema validation prevents payment failures")
    print("2. Backward compatibility ensures merchant apps don't break")
    print("3. Contract evolution supports new payment methods")
    print("4. Automated testing reduces manual QA effort")
    print("5. Clear error messages help merchants debug integration")

def run_contract_test_suite():
    """
    Run comprehensive contract test suite
    Can be integrated with pytest or other testing frameworks
    """
    contract_manager = APIContractManager()
    
    # Test all versions
    all_results = []
    
    for version in ["v1", "v2"]:
        results = contract_manager.run_contract_tests(version)
        all_results.extend(results)
    
    # Test backward compatibility
    compat_results = contract_manager.run_backward_compatibility_tests("v1", "v2")
    all_results.extend(compat_results)
    
    # Assert all critical tests pass
    failed_tests = [r for r in all_results if r.result == TestResult.FAIL]
    
    if failed_tests:
        print(f"❌ {len(failed_tests)} contract tests failed:")
        for test in failed_tests:
            print(f"   - {test.test_name}: {test.message}")
        return False
    else:
        print(f"✅ All {len(all_results)} contract tests passed")
        return True

if __name__ == "__main__":
    # Run demonstration
    demonstrate_contract_testing()
    
    print("\n" + "="*60)
    print("🧪 Running Contract Test Suite:")
    success = run_contract_test_suite()
    
    if success:
        print("✅ Contract test suite passed - Ready for deployment")
    else:
        print("❌ Contract test suite failed - Fix issues before deployment")
        exit(1)