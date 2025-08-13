#!/usr/bin/env python3
"""
Consumer-Driven Contracts for API Versioning
Inspired by MakeMyTrip's approach to manage hotel partner API contracts

Example: MakeMyTrip ne kaise manage kiya hundreds of hotel partners ka API contracts
"""

import json
import yaml
import jsonschema
import requests
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import hashlib
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractStatus(Enum):
    """Contract status tracking"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    VIOLATED = "violated"
    RETIRED = "retired"

class ConsumerType(Enum):
    """Types of API consumers"""
    MOBILE_APP = "mobile_app"
    WEB_CLIENT = "web_client"
    PARTNER_API = "partner_api"
    INTERNAL_SERVICE = "internal_service"
    THIRD_PARTY = "third_party"

@dataclass
class APIExpectation:
    """Consumer expectation for API behavior"""
    field_path: str
    expected_type: str
    required: bool = True
    description: str = ""
    example_value: Any = None
    constraints: Optional[Dict[str, Any]] = None

@dataclass
class ContractTest:
    """Individual contract test case"""
    test_id: str
    name: str
    description: str
    request_data: Dict[str, Any]
    expected_response: Dict[str, Any]
    expectations: List[APIExpectation]
    priority: str = "medium"  # low, medium, high, critical

@dataclass
class ConsumerContract:
    """Complete consumer contract definition"""
    contract_id: str
    consumer_name: str
    consumer_type: ConsumerType
    api_version: str
    contract_version: str
    status: ContractStatus
    created_at: str
    updated_at: str
    tests: List[ContractTest] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContractViolation:
    """Contract violation record"""
    violation_id: str
    contract_id: str
    test_id: str
    violation_type: str
    expected_value: Any
    actual_value: Any
    field_path: str
    timestamp: str
    impact_level: str

class ConsumerDrivenContractManager:
    """
    Manage consumer-driven contracts for API evolution
    MakeMyTrip style contract management for multiple consumers
    """
    
    def __init__(self):
        self.contracts: Dict[str, ConsumerContract] = {}
        self.violations: List[ContractViolation] = []
        self.contract_templates = self._initialize_contract_templates()
    
    def _initialize_contract_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize contract templates for different consumer types"""
        return {
            "hotel_booking_mobile_app": {
                "name": "MakeMyTrip Mobile App - Hotel Booking",
                "consumer_type": ConsumerType.MOBILE_APP,
                "critical_fields": [
                    "hotel_id", "room_price", "availability", "hotel_name",
                    "location", "rating", "amenities"
                ],
                "expectations": [
                    APIExpectation(
                        field_path="hotel_id",
                        expected_type="string",
                        required=True,
                        description="Unique hotel identifier",
                        constraints={"min_length": 5, "pattern": "^HTL_[0-9]+$"}
                    ),
                    APIExpectation(
                        field_path="room_price",
                        expected_type="number",
                        required=True,
                        description="Room price in INR",
                        constraints={"minimum": 500, "maximum": 50000}
                    ),
                    APIExpectation(
                        field_path="availability",
                        expected_type="boolean",
                        required=True,
                        description="Room availability status"
                    ),
                    APIExpectation(
                        field_path="hotel_name",
                        expected_type="string",
                        required=True,
                        description="Hotel display name",
                        constraints={"min_length": 3, "max_length": 100}
                    ),
                    APIExpectation(
                        field_path="location.city",
                        expected_type="string",
                        required=True,
                        description="Hotel city location"
                    ),
                    APIExpectation(
                        field_path="rating",
                        expected_type="number",
                        required=False,
                        description="Hotel rating out of 5",
                        constraints={"minimum": 0, "maximum": 5}
                    )
                ]
            },
            "hotel_partner_api": {
                "name": "Hotel Partner Integration API",
                "consumer_type": ConsumerType.PARTNER_API,
                "critical_fields": [
                    "booking_id", "guest_details", "check_in_date", 
                    "check_out_date", "room_type", "total_amount"
                ],
                "expectations": [
                    APIExpectation(
                        field_path="booking_id",
                        expected_type="string",
                        required=True,
                        description="MakeMyTrip booking reference",
                        constraints={"pattern": "^MMT[0-9]{10}$"}
                    ),
                    APIExpectation(
                        field_path="guest_details.name",
                        expected_type="string",
                        required=True,
                        description="Primary guest name"
                    ),
                    APIExpectation(
                        field_path="guest_details.phone",
                        expected_type="string",
                        required=True,
                        description="Guest contact number",
                        constraints={"pattern": "^\\+91[6-9][0-9]{9}$"}
                    ),
                    APIExpectation(
                        field_path="check_in_date",
                        expected_type="string",
                        required=True,
                        description="Check-in date in YYYY-MM-DD format",
                        constraints={"format": "date"}
                    ),
                    APIExpectation(
                        field_path="total_amount",
                        expected_type="number",
                        required=True,
                        description="Total booking amount including taxes",
                        constraints={"minimum": 0}
                    )
                ]
            }
        }
    
    def create_contract_from_template(self, template_name: str, 
                                    consumer_name: str, 
                                    api_version: str) -> ConsumerContract:
        """Create consumer contract from template"""
        
        if template_name not in self.contract_templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.contract_templates[template_name]
        
        contract_id = self._generate_contract_id(consumer_name, api_version)
        
        # Create sample test cases based on template
        sample_tests = self._generate_sample_tests(template, api_version)
        
        contract = ConsumerContract(
            contract_id=contract_id,
            consumer_name=consumer_name,
            consumer_type=template["consumer_type"],
            api_version=api_version,
            contract_version="1.0",
            status=ContractStatus.DRAFT,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tests=sample_tests,
            metadata={
                "template_used": template_name,
                "critical_fields": template["critical_fields"]
            }
        )
        
        return contract
    
    def _generate_contract_id(self, consumer_name: str, api_version: str) -> str:
        """Generate unique contract ID"""
        base_string = f"{consumer_name}_{api_version}_{datetime.now().isoformat()}"
        hash_object = hashlib.md5(base_string.encode())
        return f"CONTRACT_{hash_object.hexdigest()[:8].upper()}"
    
    def _generate_sample_tests(self, template: Dict[str, Any], 
                             api_version: str) -> List[ContractTest]:
        """Generate sample test cases from template"""
        tests = []
        
        if template["consumer_type"] == ConsumerType.MOBILE_APP:
            # Mobile app hotel search test
            tests.append(ContractTest(
                test_id="mobile_hotel_search_001",
                name="Hotel Search Response Validation",
                description="Validate hotel search API returns expected fields",
                request_data={
                    "city": "Mumbai",
                    "check_in": "2024-02-15",
                    "check_out": "2024-02-17",
                    "guests": 2,
                    "rooms": 1
                },
                expected_response={
                    "hotels": [
                        {
                            "hotel_id": "HTL_12345",
                            "hotel_name": "Taj Mahal Hotel",
                            "room_price": 8500.0,
                            "availability": True,
                            "location": {
                                "city": "Mumbai",
                                "area": "Colaba",
                                "coordinates": {
                                    "lat": 18.9217,
                                    "lng": 72.8330
                                }
                            },
                            "rating": 4.5,
                            "amenities": ["WiFi", "Pool", "Gym", "Spa"]
                        }
                    ],
                    "total_results": 156,
                    "filters_applied": []
                },
                expectations=template["expectations"],
                priority="critical"
            ))
        
        elif template["consumer_type"] == ConsumerType.PARTNER_API:
            # Partner booking confirmation test
            tests.append(ContractTest(
                test_id="partner_booking_001",
                name="Booking Confirmation Validation",
                description="Validate booking confirmation sent to hotel partner",
                request_data={
                    "booking_id": "MMT1234567890",
                    "hotel_id": "HTL_12345",
                    "guest_details": {
                        "name": "Rajesh Sharma",
                        "phone": "+919876543210",
                        "email": "rajesh@example.com",
                        "guest_count": 2
                    },
                    "check_in_date": "2024-02-15",
                    "check_out_date": "2024-02-17",
                    "room_type": "Deluxe Room",
                    "room_count": 1,
                    "total_amount": 17000.0,
                    "payment_status": "confirmed"
                },
                expected_response={
                    "confirmation_id": "HOTEL_CONF_123",
                    "status": "confirmed",
                    "message": "Booking confirmed successfully"
                },
                expectations=template["expectations"],
                priority="critical"
            ))
        
        return tests
    
    def register_contract(self, contract: ConsumerContract) -> str:
        """Register a new consumer contract"""
        contract.status = ContractStatus.ACTIVE
        contract.updated_at = datetime.now().isoformat()
        
        self.contracts[contract.contract_id] = contract
        
        logger.info(f"Contract registered: {contract.contract_id} for {contract.consumer_name}")
        return contract.contract_id
    
    def validate_api_response(self, contract_id: str, test_id: str, 
                            actual_response: Dict[str, Any]) -> List[ContractViolation]:
        """
        Validate API response against consumer contract
        """
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract = self.contracts[contract_id]
        test_case = next((t for t in contract.tests if t.test_id == test_id), None)
        
        if not test_case:
            raise ValueError(f"Test case {test_id} not found in contract {contract_id}")
        
        violations = []
        
        # Validate each expectation
        for expectation in test_case.expectations:
            violation = self._validate_single_expectation(
                contract_id, test_id, expectation, actual_response
            )
            if violation:
                violations.append(violation)
                self.violations.append(violation)
        
        # Update contract status if violations found
        if violations:
            critical_violations = [v for v in violations if v.impact_level == "critical"]
            if critical_violations:
                contract.status = ContractStatus.VIOLATED
                logger.error(f"Critical contract violations found for {contract_id}")
        
        return violations
    
    def _validate_single_expectation(self, contract_id: str, test_id: str,
                                   expectation: APIExpectation, 
                                   response: Dict[str, Any]) -> Optional[ContractViolation]:
        """Validate single expectation against response"""
        
        # Extract field value from response
        field_value = self._extract_field_value(response, expectation.field_path)
        
        # Check if required field is missing
        if expectation.required and field_value is None:
            return ContractViolation(
                violation_id=str(uuid.uuid4()),
                contract_id=contract_id,
                test_id=test_id,
                violation_type="missing_required_field",
                expected_value=f"Required field: {expectation.field_path}",
                actual_value=None,
                field_path=expectation.field_path,
                timestamp=datetime.now().isoformat(),
                impact_level="critical" if expectation.field_path in ["hotel_id", "booking_id", "room_price"] else "medium"
            )
        
        # Skip validation if field is optional and not present
        if not expectation.required and field_value is None:
            return None
        
        # Validate field type
        expected_python_type = self._map_type_to_python(expectation.expected_type)
        if not isinstance(field_value, expected_python_type):
            return ContractViolation(
                violation_id=str(uuid.uuid4()),
                contract_id=contract_id,
                test_id=test_id,
                violation_type="type_mismatch",
                expected_value=expectation.expected_type,
                actual_value=type(field_value).__name__,
                field_path=expectation.field_path,
                timestamp=datetime.now().isoformat(),
                impact_level="high"
            )
        
        # Validate constraints if present
        if expectation.constraints:
            constraint_violation = self._validate_constraints(
                field_value, expectation.constraints, contract_id, test_id, expectation.field_path
            )
            if constraint_violation:
                return constraint_violation
        
        return None
    
    def _extract_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Extract field value using dot notation path"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _map_type_to_python(self, type_string: str) -> type:
        """Map JSON schema type to Python type"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return type_mapping.get(type_string, object)
    
    def _validate_constraints(self, value: Any, constraints: Dict[str, Any],
                            contract_id: str, test_id: str, field_path: str) -> Optional[ContractViolation]:
        """Validate field constraints"""
        
        # String constraints
        if isinstance(value, str):
            if "min_length" in constraints and len(value) < constraints["min_length"]:
                return ContractViolation(
                    violation_id=str(uuid.uuid4()),
                    contract_id=contract_id,
                    test_id=test_id,
                    violation_type="constraint_violation",
                    expected_value=f"min_length: {constraints['min_length']}",
                    actual_value=f"length: {len(value)}",
                    field_path=field_path,
                    timestamp=datetime.now().isoformat(),
                    impact_level="medium"
                )
            
            if "pattern" in constraints:
                import re
                if not re.match(constraints["pattern"], value):
                    return ContractViolation(
                        violation_id=str(uuid.uuid4()),
                        contract_id=contract_id,
                        test_id=test_id,
                        violation_type="pattern_mismatch",
                        expected_value=constraints["pattern"],
                        actual_value=value,
                        field_path=field_path,
                        timestamp=datetime.now().isoformat(),
                        impact_level="medium"
                    )
        
        # Numeric constraints
        if isinstance(value, (int, float)):
            if "minimum" in constraints and value < constraints["minimum"]:
                return ContractViolation(
                    violation_id=str(uuid.uuid4()),
                    contract_id=contract_id,
                    test_id=test_id,
                    violation_type="value_below_minimum",
                    expected_value=f"minimum: {constraints['minimum']}",
                    actual_value=value,
                    field_path=field_path,
                    timestamp=datetime.now().isoformat(),
                    impact_level="high" if field_path == "room_price" else "medium"
                )
            
            if "maximum" in constraints and value > constraints["maximum"]:
                return ContractViolation(
                    violation_id=str(uuid.uuid4()),
                    contract_id=contract_id,
                    test_id=test_id,
                    violation_type="value_above_maximum",
                    expected_value=f"maximum: {constraints['maximum']}",
                    actual_value=value,
                    field_path=field_path,
                    timestamp=datetime.now().isoformat(),
                    impact_level="medium"
                )
        
        return None
    
    def get_contract_compliance_report(self, contract_id: str) -> Dict[str, Any]:
        """Generate compliance report for a contract"""
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract = self.contracts[contract_id]
        contract_violations = [v for v in self.violations if v.contract_id == contract_id]
        
        # Group violations by type
        violations_by_type = {}
        for violation in contract_violations:
            violation_type = violation.violation_type
            if violation_type not in violations_by_type:
                violations_by_type[violation_type] = []
            violations_by_type[violation_type].append(violation)
        
        # Calculate compliance score
        total_expectations = sum(len(test.expectations) for test in contract.tests)
        total_violations = len(contract_violations)
        compliance_score = ((total_expectations - total_violations) / total_expectations * 100) if total_expectations > 0 else 100
        
        return {
            "contract_id": contract_id,
            "consumer_name": contract.consumer_name,
            "contract_status": contract.status.value,
            "compliance_score": round(compliance_score, 2),
            "total_tests": len(contract.tests),
            "total_expectations": total_expectations,
            "total_violations": total_violations,
            "violations_by_type": {
                vtype: len(violations) for vtype, violations in violations_by_type.items()
            },
            "critical_violations": len([v for v in contract_violations if v.impact_level == "critical"]),
            "recent_violations": [
                {
                    "violation_type": v.violation_type,
                    "field_path": v.field_path,
                    "expected": v.expected_value,
                    "actual": v.actual_value,
                    "impact_level": v.impact_level,
                    "timestamp": v.timestamp
                }
                for v in sorted(contract_violations, key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }
    
    def get_all_contracts_summary(self) -> Dict[str, Any]:
        """Get summary of all consumer contracts"""
        total_contracts = len(self.contracts)
        active_contracts = len([c for c in self.contracts.values() if c.status == ContractStatus.ACTIVE])
        violated_contracts = len([c for c in self.contracts.values() if c.status == ContractStatus.VIOLATED])
        
        contracts_by_consumer_type = {}
        for contract in self.contracts.values():
            ctype = contract.consumer_type.value
            if ctype not in contracts_by_consumer_type:
                contracts_by_consumer_type[ctype] = 0
            contracts_by_consumer_type[ctype] += 1
        
        return {
            "total_contracts": total_contracts,
            "active_contracts": active_contracts,
            "violated_contracts": violated_contracts,
            "compliance_rate": round((active_contracts / total_contracts * 100) if total_contracts > 0 else 100, 2),
            "contracts_by_consumer_type": contracts_by_consumer_type,
            "total_violations": len(self.violations),
            "contracts": [
                {
                    "contract_id": contract.contract_id,
                    "consumer_name": contract.consumer_name,
                    "consumer_type": contract.consumer_type.value,
                    "status": contract.status.value,
                    "api_version": contract.api_version,
                    "tests_count": len(contract.tests)
                }
                for contract in self.contracts.values()
            ]
        }

def demonstrate_consumer_driven_contracts():
    """
    Demonstrate consumer-driven contracts with MakeMyTrip examples
    """
    print("🔥 Consumer-Driven Contracts - MakeMyTrip Style")
    print("=" * 60)
    
    cdc_manager = ConsumerDrivenContractManager()
    
    # Create contracts for different consumers
    print("\n📋 Creating Consumer Contracts...")
    
    # Mobile app contract
    mobile_contract = cdc_manager.create_contract_from_template(
        "hotel_booking_mobile_app",
        "MakeMyTrip Mobile App v4.1",
        "v2"
    )
    mobile_contract_id = cdc_manager.register_contract(mobile_contract)
    print(f"✅ Created mobile app contract: {mobile_contract_id}")
    
    # Hotel partner contract
    partner_contract = cdc_manager.create_contract_from_template(
        "hotel_partner_api",
        "Taj Hotels Integration",
        "v2"
    )
    partner_contract_id = cdc_manager.register_contract(partner_contract)
    print(f"✅ Created partner API contract: {partner_contract_id}")
    
    # Simulate API responses for validation
    print("\n🧪 Testing API Response Validation...")
    
    # Test 1: Valid mobile app response
    valid_mobile_response = {
        "hotels": [
            {
                "hotel_id": "HTL_12345",
                "hotel_name": "Taj Mahal Hotel",
                "room_price": 8500.0,
                "availability": True,
                "location": {
                    "city": "Mumbai",
                    "area": "Colaba",
                    "coordinates": {
                        "lat": 18.9217,
                        "lng": 72.8330
                    }
                },
                "rating": 4.5,
                "amenities": ["WiFi", "Pool", "Gym", "Spa"]
            }
        ],
        "total_results": 156,
        "filters_applied": []
    }
    
    mobile_violations = cdc_manager.validate_api_response(
        mobile_contract_id, 
        "mobile_hotel_search_001", 
        valid_mobile_response
    )
    
    print(f"Mobile app validation: {len(mobile_violations)} violations found")
    
    # Test 2: Invalid partner response (missing required field)
    invalid_partner_response = {
        "confirmation_id": "HOTEL_CONF_123",
        "status": "confirmed",
        # Missing 'message' field - but it's not required in our contract
        # Let's violate a constraint instead
    }
    
    # Create a response that violates the phone pattern
    invalid_booking_data = {
        "booking_id": "MMT1234567890",
        "hotel_id": "HTL_12345",
        "guest_details": {
            "name": "Rajesh Sharma",
            "phone": "9876543210",  # Missing +91 prefix - violates pattern
            "email": "rajesh@example.com",
            "guest_count": 2
        },
        "check_in_date": "2024-02-15",
        "check_out_date": "2024-02-17",
        "room_type": "Deluxe Room",
        "room_count": 1,
        "total_amount": 17000.0,
        "payment_status": "confirmed"
    }
    
    # We need to validate the request data, not response for this test
    # Let's create a simple validation
    print("\n🔍 Testing Contract Violations...")
    
    # Create a mock response with violations
    invalid_mobile_response = {
        "hotels": [
            {
                "hotel_id": "INVALID_ID",  # Violates pattern
                "hotel_name": "Taj Mahal Hotel",
                "room_price": -100.0,  # Violates minimum constraint
                "availability": True,
                "location": {
                    "city": "Mumbai"
                },
                "rating": 6.0  # Violates maximum constraint
            }
        ]
    }
    
    mobile_violations = cdc_manager.validate_api_response(
        mobile_contract_id,
        "mobile_hotel_search_001",
        invalid_mobile_response
    )
    
    print(f"Invalid mobile response: {len(mobile_violations)} violations found")
    for violation in mobile_violations:
        print(f"  ⚠️  {violation.violation_type}: {violation.field_path}")
        print(f"     Expected: {violation.expected_value}")
        print(f"     Actual: {violation.actual_value}")
    
    # Generate compliance reports
    print("\n📊 Generating Compliance Reports...")
    
    mobile_report = cdc_manager.get_contract_compliance_report(mobile_contract_id)
    print(f"\nMobile App Contract Compliance:")
    print(f"  Compliance Score: {mobile_report['compliance_score']}%")
    print(f"  Total Violations: {mobile_report['total_violations']}")
    print(f"  Critical Violations: {mobile_report['critical_violations']}")
    
    partner_report = cdc_manager.get_contract_compliance_report(partner_contract_id)
    print(f"\nPartner API Contract Compliance:")
    print(f"  Compliance Score: {partner_report['compliance_score']}%")
    print(f"  Total Violations: {partner_report['total_violations']}")
    
    # Overall summary
    summary = cdc_manager.get_all_contracts_summary()
    print(f"\n📈 Overall Contract Summary:")
    print(f"Total Contracts: {summary['total_contracts']}")
    print(f"Active Contracts: {summary['active_contracts']}")
    print(f"Violated Contracts: {summary['violated_contracts']}")
    print(f"Overall Compliance Rate: {summary['compliance_rate']}%")
    
    print(f"\nContracts by Consumer Type:")
    for ctype, count in summary['contracts_by_consumer_type'].items():
        print(f"  {ctype.replace('_', ' ').title()}: {count}")
    
    print("\n💡 Consumer-Driven Contract Benefits:")
    print("1. Prevents breaking changes that affect consumers")
    print("2. Clear communication of consumer expectations")
    print("3. Automated validation in CI/CD pipeline")
    print("4. Version compatibility verification")
    print("5. Consumer-focused API evolution")
    
    print("\n🎯 MakeMyTrip Implementation Insights:")
    print("1. Mobile apps define critical fields for user experience")
    print("2. Hotel partners specify booking flow requirements")
    print("3. Contract violations are caught before production")
    print("4. API changes are validated against all consumer contracts")
    print("5. Different consumers have different priority requirements")

if __name__ == "__main__":
    demonstrate_consumer_driven_contracts()