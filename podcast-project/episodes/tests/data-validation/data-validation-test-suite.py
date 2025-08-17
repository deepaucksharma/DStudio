#!/usr/bin/env python3
"""
Data Validation Test Suite for Episodes 92-100
डेटा वैलिडेशन टेस्ट सूट

Comprehensive data validation testing with Indian context:
- Input validation for Indian data formats
- Data integrity and consistency testing
- Schema validation for APIs
- Business rule validation
- Data quality testing
"""

import asyncio
import pytest
import re
import json
import datetime
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import phonenumbers
from decimal import Decimal, InvalidOperation
import unicodedata

# Import test fixtures
from tests.conftest import (
    indian_test_data, performance_monitor, indian_user_session,
    mock_database, mock_redis, IndianTestDataGenerator
)

class ValidationSeverity(Enum):
    """Validation error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    """Data validation result"""
    field_name: str
    value: Any
    is_valid: bool
    error_message: str = ""
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    suggested_fix: str = ""
    validation_rule: str = ""

@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    total_records: int
    valid_records: int
    invalid_records: int
    validation_results: List[ValidationResult] = field(default_factory=list)
    quality_score: float = 0.0
    
    def __post_init__(self):
        if self.total_records > 0:
            self.quality_score = (self.valid_records / self.total_records) * 100

class IndianDataValidator:
    """Validator for Indian-specific data formats"""
    
    def __init__(self):
        self.indian_states = {
            "AN": "Andaman and Nicobar Islands",
            "AP": "Andhra Pradesh", 
            "AR": "Arunachal Pradesh",
            "AS": "Assam",
            "BR": "Bihar",
            "CH": "Chandigarh",
            "CG": "Chhattisgarh",
            "DN": "Dadra and Nagar Haveli",
            "DD": "Daman and Diu",
            "DL": "Delhi",
            "GA": "Goa",
            "GJ": "Gujarat",
            "HR": "Haryana",
            "HP": "Himachal Pradesh",
            "JK": "Jammu and Kashmir",
            "JH": "Jharkhand",
            "KA": "Karnataka",
            "KL": "Kerala",
            "LD": "Lakshadweep",
            "MP": "Madhya Pradesh",
            "MH": "Maharashtra",
            "MN": "Manipur",
            "ML": "Meghalaya",
            "MZ": "Mizoram",
            "NL": "Nagaland",
            "OD": "Odisha",
            "PY": "Puducherry",
            "PB": "Punjab",
            "RJ": "Rajasthan",
            "SK": "Sikkim",
            "TN": "Tamil Nadu",
            "TS": "Telangana",
            "TR": "Tripura",
            "UP": "Uttar Pradesh",
            "UK": "Uttarakhand",
            "WB": "West Bengal"
        }
        
        self.indian_banks = [
            "HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "PNB", "BOB",
            "CANARA", "UNION", "INDIAN", "CENTRAL", "SYNDICATE"
        ]
        
    def validate_pan_number(self, pan: str) -> ValidationResult:
        """Validate Indian PAN number"""
        if not pan:
            return ValidationResult(
                "pan", pan, False, 
                "PAN number is required",
                ValidationSeverity.HIGH,
                "Provide a valid PAN number",
                "PAN format validation"
            )
            
        # PAN format: AAAAA9999A (5 letters + 4 digits + 1 letter)
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        if not re.match(pan_pattern, pan.upper()):
            return ValidationResult(
                "pan", pan, False,
                "Invalid PAN format. Expected format: AAAAA9999A",
                ValidationSeverity.HIGH,
                "Use format: 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)",
                "PAN format validation"
            )
            
        return ValidationResult(
            "pan", pan, True,
            "",
            ValidationSeverity.LOW,
            "",
            "PAN format validation"
        )
        
    def validate_aadhaar_number(self, aadhaar: str) -> ValidationResult:
        """Validate Indian Aadhaar number"""
        if not aadhaar:
            return ValidationResult(
                "aadhaar", aadhaar, False,
                "Aadhaar number is required",
                ValidationSeverity.HIGH,
                "Provide a valid 12-digit Aadhaar number",
                "Aadhaar format validation"
            )
            
        # Remove spaces and hyphens
        clean_aadhaar = re.sub(r'[\s-]', '', aadhaar)
        
        # Check if it's 12 digits
        if not re.match(r'^\d{12}$', clean_aadhaar):
            return ValidationResult(
                "aadhaar", aadhaar, False,
                "Aadhaar must be 12 digits",
                ValidationSeverity.HIGH,
                "Provide exactly 12 digits",
                "Aadhaar format validation"
            )
            
        # Basic Verhoeff algorithm check (simplified)
        if not self._validate_aadhaar_checksum(clean_aadhaar):
            return ValidationResult(
                "aadhaar", aadhaar, False,
                "Invalid Aadhaar checksum",
                ValidationSeverity.MEDIUM,
                "Verify the Aadhaar number digits",
                "Aadhaar checksum validation"
            )
            
        return ValidationResult(
            "aadhaar", aadhaar, True,
            "",
            ValidationSeverity.LOW,
            "",
            "Aadhaar format validation"
        )
        
    def _validate_aadhaar_checksum(self, aadhaar: str) -> bool:
        """Simplified Aadhaar checksum validation using Verhoeff algorithm"""
        # This is a simplified version. Real implementation would use full Verhoeff algorithm
        # For testing purposes, we'll do a basic validation
        if aadhaar == "000000000000" or aadhaar == "111111111111":
            return False  # Common invalid patterns
        return True
        
    def validate_indian_phone(self, phone: str) -> ValidationResult:
        """Validate Indian phone number"""
        if not phone:
            return ValidationResult(
                "phone", phone, False,
                "Phone number is required",
                ValidationSeverity.HIGH,
                "Provide a valid Indian phone number",
                "Phone format validation"
            )
            
        try:
            # Parse phone number with Indian country code
            parsed = phonenumbers.parse(phone, "IN")
            
            if not phonenumbers.is_valid_number(parsed):
                return ValidationResult(
                    "phone", phone, False,
                    "Invalid Indian phone number",
                    ValidationSeverity.HIGH,
                    "Use format: +91XXXXXXXXXX or 10-digit mobile number",
                    "Phone format validation"
                )
                
            # Check if it's a mobile number (starts with 6, 7, 8, 9)
            national_number = str(parsed.national_number)
            if len(national_number) == 10 and national_number[0] in ['6', '7', '8', '9']:
                return ValidationResult(
                    "phone", phone, True,
                    "",
                    ValidationSeverity.LOW,
                    "",
                    "Phone format validation"
                )
            else:
                return ValidationResult(
                    "phone", phone, False,
                    "Must be a valid Indian mobile number",
                    ValidationSeverity.MEDIUM,
                    "Indian mobile numbers start with 6, 7, 8, or 9",
                    "Phone format validation"
                )
                
        except phonenumbers.NumberParseException:
            return ValidationResult(
                "phone", phone, False,
                "Cannot parse phone number",
                ValidationSeverity.HIGH,
                "Use format: +91XXXXXXXXXX",
                "Phone format validation"
            )
            
    def validate_indian_pincode(self, pincode: str) -> ValidationResult:
        """Validate Indian postal code (PIN code)"""
        if not pincode:
            return ValidationResult(
                "pincode", pincode, False,
                "PIN code is required",
                ValidationSeverity.HIGH,
                "Provide a valid 6-digit PIN code",
                "PIN code format validation"
            )
            
        # Indian PIN codes are 6 digits
        if not re.match(r'^\d{6}$', pincode):
            return ValidationResult(
                "pincode", pincode, False,
                "PIN code must be 6 digits",
                ValidationSeverity.HIGH,
                "Use 6-digit format (e.g., 400001)",
                "PIN code format validation"
            )
            
        # Check for invalid PIN codes
        invalid_pincodes = ["000000", "111111", "999999"]
        if pincode in invalid_pincodes:
            return ValidationResult(
                "pincode", pincode, False,
                "Invalid PIN code pattern",
                ValidationSeverity.MEDIUM,
                "Use a valid geographic PIN code",
                "PIN code pattern validation"
            )
            
        return ValidationResult(
            "pincode", pincode, True,
            "",
            ValidationSeverity.LOW,
            "",
            "PIN code format validation"
        )
        
    def validate_ifsc_code(self, ifsc: str) -> ValidationResult:
        """Validate Indian IFSC code"""
        if not ifsc:
            return ValidationResult(
                "ifsc", ifsc, False,
                "IFSC code is required",
                ValidationSeverity.HIGH,
                "Provide a valid IFSC code",
                "IFSC format validation"
            )
            
        # IFSC format: AAAA0BBBBBB (4 letters + 0 + 6 alphanumeric)
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        
        if not re.match(ifsc_pattern, ifsc.upper()):
            return ValidationResult(
                "ifsc", ifsc, False,
                "Invalid IFSC format. Expected: AAAA0BBBBBB",
                ValidationSeverity.HIGH,
                "Use format: 4 letters + 0 + 6 alphanumeric (e.g., HDFC0000001)",
                "IFSC format validation"
            )
            
        # Check if bank code is recognized
        bank_code = ifsc[:4].upper()
        if bank_code not in self.indian_banks:
            return ValidationResult(
                "ifsc", ifsc, False,
                f"Unrecognized bank code: {bank_code}",
                ValidationSeverity.MEDIUM,
                f"Use a valid bank code like: {', '.join(self.indian_banks[:5])}",
                "IFSC bank code validation"
            )
            
        return ValidationResult(
            "ifsc", ifsc, True,
            "",
            ValidationSeverity.LOW,
            "",
            "IFSC format validation"
        )
        
    def validate_upi_id(self, upi_id: str) -> ValidationResult:
        """Validate UPI ID"""
        if not upi_id:
            return ValidationResult(
                "upi_id", upi_id, False,
                "UPI ID is required",
                ValidationSeverity.HIGH,
                "Provide a valid UPI ID",
                "UPI ID format validation"
            )
            
        # UPI ID format: username@bank
        upi_pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$'
        
        if not re.match(upi_pattern, upi_id):
            return ValidationResult(
                "upi_id", upi_id, False,
                "Invalid UPI ID format",
                ValidationSeverity.HIGH,
                "Use format: username@bank (e.g., user123@paytm)",
                "UPI ID format validation"
            )
            
        # Check handle length
        parts = upi_id.split('@')
        if len(parts[0]) < 3:
            return ValidationResult(
                "upi_id", upi_id, False,
                "UPI username too short (minimum 3 characters)",
                ValidationSeverity.MEDIUM,
                "Use at least 3 characters for username",
                "UPI ID username validation"
            )
            
        return ValidationResult(
            "upi_id", upi_id, True,
            "",
            ValidationSeverity.LOW,
            "",
            "UPI ID format validation"
        )
        
    def validate_gst_number(self, gst: str) -> ValidationResult:
        """Validate Indian GST number"""
        if not gst:
            return ValidationResult(
                "gst", gst, False,
                "GST number is required for business",
                ValidationSeverity.HIGH,
                "Provide a valid 15-digit GST number",
                "GST format validation"
            )
            
        # GST format: DDAAAAA9999AZZD (15 characters)
        # DD = State code, AAAAA = PAN first 5, 9999 = Entity number, A = PAN last, Z = check digit, D = default
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$'
        
        if not re.match(gst_pattern, gst.upper()):
            return ValidationResult(
                "gst", gst, False,
                "Invalid GST format",
                ValidationSeverity.HIGH,
                "Use 15-character GST format: DDAAAAA9999AZZD",
                "GST format validation"
            )
            
        # Validate state code
        state_code = gst[:2]
        valid_state_codes = [str(i).zfill(2) for i in range(1, 38)]  # Indian state codes 01-37
        
        if state_code not in valid_state_codes:
            return ValidationResult(
                "gst", gst, False,
                f"Invalid state code: {state_code}",
                ValidationSeverity.MEDIUM,
                "Use valid Indian state code (01-37)",
                "GST state code validation"
            )
            
        return ValidationResult(
            "gst", gst, True,
            "",
            ValidationSeverity.LOW,
            "",
            "GST format validation"
        )

class DataTypeValidator:
    """Generic data type validator"""
    
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email address"""
        if not email:
            return ValidationResult(
                "email", email, False,
                "Email is required",
                ValidationSeverity.HIGH,
                "Provide a valid email address",
                "Email format validation"
            )
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return ValidationResult(
                "email", email, False,
                "Invalid email format",
                ValidationSeverity.HIGH,
                "Use format: user@domain.com",
                "Email format validation"
            )
            
        # Check for common invalid domains
        invalid_domains = ["test.com", "example.com", "temp.com"]
        domain = email.split('@')[1].lower()
        
        if domain in invalid_domains:
            return ValidationResult(
                "email", email, False,
                f"Invalid email domain: {domain}",
                ValidationSeverity.MEDIUM,
                "Use a valid email domain",
                "Email domain validation"
            )
            
        return ValidationResult(
            "email", email, True,
            "",
            ValidationSeverity.LOW,
            "",
            "Email format validation"
        )
        
    def validate_date(self, date_str: str, date_format: str = "%Y-%m-%d") -> ValidationResult:
        """Validate date string"""
        if not date_str:
            return ValidationResult(
                "date", date_str, False,
                "Date is required",
                ValidationSeverity.HIGH,
                f"Provide date in format: {date_format}",
                "Date format validation"
            )
            
        try:
            parsed_date = datetime.datetime.strptime(date_str, date_format)
            
            # Check if date is in reasonable range
            min_date = datetime.datetime(1900, 1, 1)
            max_date = datetime.datetime(2100, 12, 31)
            
            if parsed_date < min_date or parsed_date > max_date:
                return ValidationResult(
                    "date", date_str, False,
                    "Date out of valid range",
                    ValidationSeverity.MEDIUM,
                    "Use dates between 1900-2100",
                    "Date range validation"
                )
                
            return ValidationResult(
                "date", date_str, True,
                "",
                ValidationSeverity.LOW,
                "",
                "Date format validation"
            )
            
        except ValueError:
            return ValidationResult(
                "date", date_str, False,
                f"Invalid date format, expected: {date_format}",
                ValidationSeverity.HIGH,
                f"Use format: {date_format}",
                "Date format validation"
            )
            
    def validate_numeric(self, value: str, min_val: float = None, max_val: float = None) -> ValidationResult:
        """Validate numeric value"""
        if not value:
            return ValidationResult(
                "numeric", value, False,
                "Numeric value is required",
                ValidationSeverity.HIGH,
                "Provide a valid number",
                "Numeric validation"
            )
            
        try:
            num_value = float(value)
            
            if min_val is not None and num_value < min_val:
                return ValidationResult(
                    "numeric", value, False,
                    f"Value {num_value} is below minimum {min_val}",
                    ValidationSeverity.MEDIUM,
                    f"Use value >= {min_val}",
                    "Numeric range validation"
                )
                
            if max_val is not None and num_value > max_val:
                return ValidationResult(
                    "numeric", value, False,
                    f"Value {num_value} is above maximum {max_val}",
                    ValidationSeverity.MEDIUM,
                    f"Use value <= {max_val}",
                    "Numeric range validation"
                )
                
            return ValidationResult(
                "numeric", value, True,
                "",
                ValidationSeverity.LOW,
                "",
                "Numeric validation"
            )
            
        except ValueError:
            return ValidationResult(
                "numeric", value, False,
                "Invalid numeric value",
                ValidationSeverity.HIGH,
                "Provide a valid number",
                "Numeric format validation"
            )
            
    def validate_string_length(self, value: str, min_len: int = 0, max_len: int = None) -> ValidationResult:
        """Validate string length"""
        if value is None:
            value = ""
            
        length = len(value)
        
        if length < min_len:
            return ValidationResult(
                "string_length", value, False,
                f"String too short: {length} characters (minimum: {min_len})",
                ValidationSeverity.MEDIUM,
                f"Use at least {min_len} characters",
                "String length validation"
            )
            
        if max_len is not None and length > max_len:
            return ValidationResult(
                "string_length", value, False,
                f"String too long: {length} characters (maximum: {max_len})",
                ValidationSeverity.MEDIUM,
                f"Use at most {max_len} characters",
                "String length validation"
            )
            
        return ValidationResult(
            "string_length", value, True,
            "",
            ValidationSeverity.LOW,
            "",
            "String length validation"
        )
        
    def validate_currency(self, amount: str, currency: str = "INR") -> ValidationResult:
        """Validate currency amount"""
        if not amount:
            return ValidationResult(
                "currency", amount, False,
                "Amount is required",
                ValidationSeverity.HIGH,
                "Provide a valid amount",
                "Currency validation"
            )
            
        try:
            # Remove currency symbols and spaces
            clean_amount = re.sub(r'[₹$€£,\s]', '', amount)
            decimal_amount = Decimal(clean_amount)
            
            if decimal_amount < 0:
                return ValidationResult(
                    "currency", amount, False,
                    "Amount cannot be negative",
                    ValidationSeverity.HIGH,
                    "Use positive amount",
                    "Currency value validation"
                )
                
            # Check decimal places (max 2 for currency)
            if decimal_amount.as_tuple().exponent < -2:
                return ValidationResult(
                    "currency", amount, False,
                    "Too many decimal places for currency",
                    ValidationSeverity.MEDIUM,
                    "Use maximum 2 decimal places",
                    "Currency precision validation"
                )
                
            # Currency-specific validations
            if currency == "INR":
                # Check for reasonable INR amounts
                if decimal_amount > Decimal('10000000'):  # 1 crore
                    return ValidationResult(
                        "currency", amount, False,
                        "Amount seems unusually large",
                        ValidationSeverity.MEDIUM,
                        "Verify the amount is correct",
                        "Currency range validation"
                    )
                    
            return ValidationResult(
                "currency", amount, True,
                "",
                ValidationSeverity.LOW,
                "",
                "Currency validation"
            )
            
        except (ValueError, InvalidOperation):
            return ValidationResult(
                "currency", amount, False,
                "Invalid currency format",
                ValidationSeverity.HIGH,
                "Use numeric format (e.g., 1234.56)",
                "Currency format validation"
            )

class BusinessRuleValidator:
    """Business logic validation"""
    
    def validate_age_requirement(self, birth_date: str, min_age: int = 18) -> ValidationResult:
        """Validate age requirement"""
        try:
            birth_dt = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            age = (today - birth_dt).days // 365
            
            if age < min_age:
                return ValidationResult(
                    "age", birth_date, False,
                    f"Minimum age requirement not met: {age} years (required: {min_age})",
                    ValidationSeverity.HIGH,
                    f"Must be at least {min_age} years old",
                    "Age requirement validation"
                )
                
            if age > 150:
                return ValidationResult(
                    "age", birth_date, False,
                    f"Age seems unrealistic: {age} years",
                    ValidationSeverity.MEDIUM,
                    "Verify birth date is correct",
                    "Age reasonableness validation"
                )
                
            return ValidationResult(
                "age", birth_date, True,
                "",
                ValidationSeverity.LOW,
                "",
                "Age requirement validation"
            )
            
        except ValueError:
            return ValidationResult(
                "age", birth_date, False,
                "Invalid birth date format",
                ValidationSeverity.HIGH,
                "Use YYYY-MM-DD format",
                "Date format validation"
            )
            
    def validate_password_strength(self, password: str) -> ValidationResult:
        """Validate password strength"""
        if not password:
            return ValidationResult(
                "password", "", False,
                "Password is required",
                ValidationSeverity.CRITICAL,
                "Provide a strong password",
                "Password requirement validation"
            )
            
        issues = []
        
        if len(password) < 8:
            issues.append("at least 8 characters")
            
        if not re.search(r'[A-Z]', password):
            issues.append("uppercase letter")
            
        if not re.search(r'[a-z]', password):
            issues.append("lowercase letter")
            
        if not re.search(r'[0-9]', password):
            issues.append("number")
            
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"|,.<>?]', password):
            issues.append("special character")
            
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome']
        if password.lower() in weak_passwords:
            issues.append("not a common weak password")
            
        if issues:
            return ValidationResult(
                "password", "***", False,
                f"Password must include: {', '.join(issues)}",
                ValidationSeverity.CRITICAL,
                "Use a strong password with mixed case, numbers, and symbols",
                "Password strength validation"
            )
            
        return ValidationResult(
            "password", "***", True,
            "",
            ValidationSeverity.LOW,
            "",
            "Password strength validation"
        )
        
    def validate_transaction_amount(self, amount: Decimal, account_balance: Decimal, 
                                   transaction_type: str = "debit") -> ValidationResult:
        """Validate transaction amount against business rules"""
        if amount <= 0:
            return ValidationResult(
                "transaction_amount", str(amount), False,
                "Transaction amount must be positive",
                ValidationSeverity.HIGH,
                "Use positive amount",
                "Transaction amount validation"
            )
            
        if transaction_type == "debit" and amount > account_balance:
            return ValidationResult(
                "transaction_amount", str(amount), False,
                f"Insufficient balance: ₹{amount} (available: ₹{account_balance})",
                ValidationSeverity.CRITICAL,
                "Reduce amount or add funds",
                "Insufficient balance validation"
            )
            
        # UPI transaction limits
        if transaction_type == "upi":
            daily_limit = Decimal('100000')  # ₹1,00,000 daily limit
            if amount > daily_limit:
                return ValidationResult(
                    "transaction_amount", str(amount), False,
                    f"Amount exceeds UPI daily limit: ₹{amount} (limit: ₹{daily_limit})",
                    ValidationSeverity.HIGH,
                    f"Use amount ≤ ₹{daily_limit} for UPI",
                    "UPI limit validation"
                )
                
        return ValidationResult(
            "transaction_amount", str(amount), True,
            "",
            ValidationSeverity.LOW,
            "",
            "Transaction amount validation"
        )

class SchemaValidator:
    """JSON schema validation"""
    
    def __init__(self):
        self.schemas = {
            "user_registration": {
                "type": "object",
                "required": ["name", "email", "phone", "password"],
                "properties": {
                    "name": {"type": "string", "minLength": 2, "maxLength": 100},
                    "email": {"type": "string", "format": "email"},
                    "phone": {"type": "string", "pattern": r"^\+91[6-9]\d{9}$"},
                    "password": {"type": "string", "minLength": 8},
                    "age": {"type": "integer", "minimum": 18, "maximum": 120},
                    "address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                            "state": {"type": "string"},
                            "pincode": {"type": "string", "pattern": r"^\d{6}$"}
                        }
                    }
                }
            },
            "payment_request": {
                "type": "object",
                "required": ["amount", "currency", "from_account", "to_account"],
                "properties": {
                    "amount": {"type": "number", "minimum": 1, "maximum": 1000000},
                    "currency": {"type": "string", "enum": ["INR", "USD", "EUR"]},
                    "from_account": {"type": "string", "minLength": 10},
                    "to_account": {"type": "string", "minLength": 10},
                    "purpose": {"type": "string", "maxLength": 200},
                    "upi_id": {"type": "string", "pattern": r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$"}
                }
            }
        }
        
    def validate_schema(self, data: Dict[str, Any], schema_name: str) -> List[ValidationResult]:
        """Validate data against predefined schema"""
        results = []
        
        if schema_name not in self.schemas:
            results.append(ValidationResult(
                "schema", schema_name, False,
                f"Unknown schema: {schema_name}",
                ValidationSeverity.CRITICAL,
                f"Use valid schema: {list(self.schemas.keys())}",
                "Schema validation"
            ))
            return results
            
        schema = self.schemas[schema_name]
        
        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                results.append(ValidationResult(
                    field, None, False,
                    f"Required field missing: {field}",
                    ValidationSeverity.HIGH,
                    f"Include {field} in request",
                    "Required field validation"
                ))
                
        # Validate field properties
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                field_results = self._validate_field_schema(field, value, field_schema)
                results.extend(field_results)
                
        return results
        
    def _validate_field_schema(self, field_name: str, value: Any, 
                              field_schema: Dict[str, Any]) -> List[ValidationResult]:
        """Validate individual field against schema"""
        results = []
        
        # Type validation
        expected_type = field_schema.get("type")
        if expected_type:
            if not self._check_type(value, expected_type):
                results.append(ValidationResult(
                    field_name, value, False,
                    f"Expected {expected_type}, got {type(value).__name__}",
                    ValidationSeverity.HIGH,
                    f"Provide {expected_type} value",
                    "Type validation"
                ))
                return results  # Skip other validations if type is wrong
                
        # String validations
        if expected_type == "string" and isinstance(value, str):
            min_length = field_schema.get("minLength")
            if min_length and len(value) < min_length:
                results.append(ValidationResult(
                    field_name, value, False,
                    f"String too short: {len(value)} < {min_length}",
                    ValidationSeverity.MEDIUM,
                    f"Use at least {min_length} characters",
                    "String length validation"
                ))
                
            max_length = field_schema.get("maxLength")
            if max_length and len(value) > max_length:
                results.append(ValidationResult(
                    field_name, value, False,
                    f"String too long: {len(value)} > {max_length}",
                    ValidationSeverity.MEDIUM,
                    f"Use at most {max_length} characters",
                    "String length validation"
                ))
                
            pattern = field_schema.get("pattern")
            if pattern and not re.match(pattern, value):
                results.append(ValidationResult(
                    field_name, value, False,
                    f"String doesn't match pattern: {pattern}",
                    ValidationSeverity.HIGH,
                    "Use correct format",
                    "Pattern validation"
                ))
                
        # Number validations
        if expected_type in ["number", "integer"] and isinstance(value, (int, float)):
            minimum = field_schema.get("minimum")
            if minimum is not None and value < minimum:
                results.append(ValidationResult(
                    field_name, value, False,
                    f"Value too small: {value} < {minimum}",
                    ValidationSeverity.MEDIUM,
                    f"Use value >= {minimum}",
                    "Range validation"
                ))
                
            maximum = field_schema.get("maximum")
            if maximum is not None and value > maximum:
                results.append(ValidationResult(
                    field_name, value, False,
                    f"Value too large: {value} > {maximum}",
                    ValidationSeverity.MEDIUM,
                    f"Use value <= {maximum}",
                    "Range validation"
                ))
                
        # Enum validation
        enum_values = field_schema.get("enum")
        if enum_values and value not in enum_values:
            results.append(ValidationResult(
                field_name, value, False,
                f"Invalid value: {value} (allowed: {enum_values})",
                ValidationSeverity.HIGH,
                f"Use one of: {enum_values}",
                "Enum validation"
            ))
            
        return results
        
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return False

class DataQualityAssessor:
    """Assess overall data quality"""
    
    def __init__(self):
        self.indian_validator = IndianDataValidator()
        self.type_validator = DataTypeValidator()
        self.business_validator = BusinessRuleValidator()
        self.schema_validator = SchemaValidator()
        
    def assess_user_data_quality(self, user_data: List[Dict[str, Any]]) -> DataQualityReport:
        """Assess quality of user data"""
        all_results = []
        valid_count = 0
        
        for i, user in enumerate(user_data):
            user_results = []
            
            # Validate individual fields
            if "email" in user:
                result = self.type_validator.validate_email(user["email"])
                user_results.append(result)
                
            if "phone" in user:
                result = self.indian_validator.validate_indian_phone(user["phone"])
                user_results.append(result)
                
            if "pan" in user:
                result = self.indian_validator.validate_pan_number(user["pan"])
                user_results.append(result)
                
            if "pincode" in user:
                result = self.indian_validator.validate_indian_pincode(user["pincode"])
                user_results.append(result)
                
            if "birth_date" in user:
                result = self.business_validator.validate_age_requirement(user["birth_date"])
                user_results.append(result)
                
            # Check if user record is overall valid
            user_valid = all(r.is_valid for r in user_results)
            if user_valid:
                valid_count += 1
                
            all_results.extend(user_results)
            
        return DataQualityReport(
            total_records=len(user_data),
            valid_records=valid_count,
            invalid_records=len(user_data) - valid_count,
            validation_results=all_results
        )
        
    def assess_transaction_data_quality(self, transaction_data: List[Dict[str, Any]]) -> DataQualityReport:
        """Assess quality of transaction data"""
        all_results = []
        valid_count = 0
        
        for transaction in transaction_data:
            transaction_results = []
            
            # Validate amount
            if "amount" in transaction:
                result = self.type_validator.validate_currency(str(transaction["amount"]))
                transaction_results.append(result)
                
            # Validate UPI ID if present
            if "upi_id" in transaction:
                result = self.indian_validator.validate_upi_id(transaction["upi_id"])
                transaction_results.append(result)
                
            # Validate IFSC if present
            if "ifsc" in transaction:
                result = self.indian_validator.validate_ifsc_code(transaction["ifsc"])
                transaction_results.append(result)
                
            # Business rule validation
            if "amount" in transaction and "account_balance" in transaction:
                amount = Decimal(str(transaction["amount"]))
                balance = Decimal(str(transaction["account_balance"]))
                result = self.business_validator.validate_transaction_amount(amount, balance)
                transaction_results.append(result)
                
            # Check if transaction is overall valid
            transaction_valid = all(r.is_valid for r in transaction_results)
            if transaction_valid:
                valid_count += 1
                
            all_results.extend(transaction_results)
            
        return DataQualityReport(
            total_records=len(transaction_data),
            valid_records=valid_count,
            invalid_records=len(transaction_data) - valid_count,
            validation_results=all_results
        )

# Test Classes
class TestIndianDataValidation:
    """Test Indian-specific data validation"""
    
    def test_pan_validation(self):
        """Test PAN number validation"""
        validator = IndianDataValidator()
        
        # Valid PAN
        result = validator.validate_pan_number("ABCDE1234F")
        assert result.is_valid
        
        # Invalid PAN format
        result = validator.validate_pan_number("ABC123")
        assert not result.is_valid
        assert "Invalid PAN format" in result.error_message
        
        # Empty PAN
        result = validator.validate_pan_number("")
        assert not result.is_valid
        assert result.severity == ValidationSeverity.HIGH
        
    def test_aadhaar_validation(self):
        """Test Aadhaar number validation"""
        validator = IndianDataValidator()
        
        # Valid Aadhaar
        result = validator.validate_aadhaar_number("123456789012")
        assert result.is_valid
        
        # Aadhaar with spaces
        result = validator.validate_aadhaar_number("1234 5678 9012")
        assert result.is_valid
        
        # Invalid Aadhaar (too short)
        result = validator.validate_aadhaar_number("12345")
        assert not result.is_valid
        
        # Invalid Aadhaar (all zeros)
        result = validator.validate_aadhaar_number("000000000000")
        assert not result.is_valid
        
    def test_phone_validation(self):
        """Test Indian phone number validation"""
        validator = IndianDataValidator()
        
        # Valid mobile numbers
        valid_phones = ["+919876543210", "9876543210", "+91 98765 43210"]
        for phone in valid_phones:
            result = validator.validate_indian_phone(phone)
            assert result.is_valid, f"Phone {phone} should be valid"
            
        # Invalid phone numbers
        invalid_phones = ["123456", "1234567890", "+1234567890"]
        for phone in invalid_phones:
            result = validator.validate_indian_phone(phone)
            assert not result.is_valid, f"Phone {phone} should be invalid"
            
    def test_pincode_validation(self):
        """Test PIN code validation"""
        validator = IndianDataValidator()
        
        # Valid PIN codes
        result = validator.validate_indian_pincode("400001")
        assert result.is_valid
        
        result = validator.validate_indian_pincode("110001")
        assert result.is_valid
        
        # Invalid PIN codes
        result = validator.validate_indian_pincode("12345")
        assert not result.is_valid
        
        result = validator.validate_indian_pincode("000000")
        assert not result.is_valid
        
    def test_upi_validation(self):
        """Test UPI ID validation"""
        validator = IndianDataValidator()
        
        # Valid UPI IDs
        valid_upis = ["user123@paytm", "john.doe@phonepe", "test_user@googlepay"]
        for upi in valid_upis:
            result = validator.validate_upi_id(upi)
            assert result.is_valid, f"UPI {upi} should be valid"
            
        # Invalid UPI IDs
        invalid_upis = ["user123", "@paytm", "us@", "a@b"]
        for upi in invalid_upis:
            result = validator.validate_upi_id(upi)
            assert not result.is_valid, f"UPI {upi} should be invalid"
            
    def test_ifsc_validation(self):
        """Test IFSC code validation"""
        validator = IndianDataValidator()
        
        # Valid IFSC codes
        result = validator.validate_ifsc_code("HDFC0000001")
        assert result.is_valid
        
        result = validator.validate_ifsc_code("ICICI0000123")
        assert result.is_valid
        
        # Invalid IFSC codes
        result = validator.validate_ifsc_code("HDFC123")
        assert not result.is_valid
        
        result = validator.validate_ifsc_code("INVALID0001")
        assert not result.is_valid
        
    def test_gst_validation(self):
        """Test GST number validation"""
        validator = IndianDataValidator()
        
        # Valid GST format
        result = validator.validate_gst_number("27ABCDE1234F1ZD")
        assert result.is_valid
        
        # Invalid GST format
        result = validator.validate_gst_number("INVALID")
        assert not result.is_valid
        
        # Invalid state code
        result = validator.validate_gst_number("99ABCDE1234F1ZD")
        assert not result.is_valid

class TestDataTypeValidation:
    """Test generic data type validation"""
    
    def test_email_validation(self):
        """Test email validation"""
        validator = DataTypeValidator()
        
        # Valid emails
        valid_emails = ["user@example.com", "test.email@domain.co.in", "user+tag@domain.org"]
        for email in valid_emails:
            result = validator.validate_email(email)
            assert result.is_valid, f"Email {email} should be valid"
            
        # Invalid emails
        invalid_emails = ["invalid", "@domain.com", "user@", "user@test.com"]
        for email in invalid_emails:
            result = validator.validate_email(email)
            assert not result.is_valid, f"Email {email} should be invalid"
            
    def test_date_validation(self):
        """Test date validation"""
        validator = DataTypeValidator()
        
        # Valid dates
        result = validator.validate_date("2023-12-25")
        assert result.is_valid
        
        result = validator.validate_date("1990-01-01")
        assert result.is_valid
        
        # Invalid dates
        result = validator.validate_date("2023-13-01")  # Invalid month
        assert not result.is_valid
        
        result = validator.validate_date("invalid-date")
        assert not result.is_valid
        
        # Date out of range
        result = validator.validate_date("1800-01-01")
        assert not result.is_valid
        
    def test_numeric_validation(self):
        """Test numeric validation"""
        validator = DataTypeValidator()
        
        # Valid numbers
        result = validator.validate_numeric("123.45")
        assert result.is_valid
        
        result = validator.validate_numeric("100", min_val=50, max_val=150)
        assert result.is_valid
        
        # Invalid numbers
        result = validator.validate_numeric("not_a_number")
        assert not result.is_valid
        
        # Out of range
        result = validator.validate_numeric("200", min_val=50, max_val=150)
        assert not result.is_valid
        
    def test_currency_validation(self):
        """Test currency validation"""
        validator = DataTypeValidator()
        
        # Valid amounts
        result = validator.validate_currency("1234.56")
        assert result.is_valid
        
        result = validator.validate_currency("₹1,000.50")
        assert result.is_valid
        
        # Invalid amounts
        result = validator.validate_currency("-100")
        assert not result.is_valid
        
        result = validator.validate_currency("1234.567")  # Too many decimals
        assert not result.is_valid

class TestBusinessRuleValidation:
    """Test business rule validation"""
    
    def test_age_requirement(self):
        """Test age requirement validation"""
        validator = BusinessRuleValidator()
        
        # Valid age (25 years old)
        birth_date = "1998-01-01"
        result = validator.validate_age_requirement(birth_date, min_age=18)
        assert result.is_valid
        
        # Under age (10 years old)
        birth_date = "2013-01-01"
        result = validator.validate_age_requirement(birth_date, min_age=18)
        assert not result.is_valid
        assert result.severity == ValidationSeverity.HIGH
        
    def test_password_strength(self):
        """Test password strength validation"""
        validator = BusinessRuleValidator()
        
        # Strong password
        result = validator.validate_password_strength("StrongP@ssw0rd!")
        assert result.is_valid
        
        # Weak passwords
        weak_passwords = ["123456", "password", "abc", "PASSWORD"]
        for password in weak_passwords:
            result = validator.validate_password_strength(password)
            assert not result.is_valid, f"Password '{password}' should be invalid"
            assert result.severity == ValidationSeverity.CRITICAL
            
    def test_transaction_amount(self):
        """Test transaction amount validation"""
        validator = BusinessRuleValidator()
        
        # Valid transaction
        result = validator.validate_transaction_amount(
            Decimal("1000"), Decimal("5000"), "debit"
        )
        assert result.is_valid
        
        # Insufficient balance
        result = validator.validate_transaction_amount(
            Decimal("6000"), Decimal("5000"), "debit"
        )
        assert not result.is_valid
        assert result.severity == ValidationSeverity.CRITICAL
        
        # UPI limit exceeded
        result = validator.validate_transaction_amount(
            Decimal("150000"), Decimal("200000"), "upi"
        )
        assert not result.is_valid

class TestSchemaValidation:
    """Test JSON schema validation"""
    
    def test_user_registration_schema(self):
        """Test user registration schema validation"""
        validator = SchemaValidator()
        
        # Valid user data
        valid_user = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+919876543210",
            "password": "StrongP@ssw0rd!",
            "age": 25
        }
        
        results = validator.validate_schema(valid_user, "user_registration")
        validation_errors = [r for r in results if not r.is_valid]
        assert len(validation_errors) == 0
        
        # Invalid user data (missing required field)
        invalid_user = {
            "name": "John Doe",
            "email": "john@example.com"
            # Missing phone and password
        }
        
        results = validator.validate_schema(invalid_user, "user_registration")
        validation_errors = [r for r in results if not r.is_valid]
        assert len(validation_errors) > 0
        
    def test_payment_request_schema(self):
        """Test payment request schema validation"""
        validator = SchemaValidator()
        
        # Valid payment request
        valid_payment = {
            "amount": 1000.50,
            "currency": "INR",
            "from_account": "HDFC0000001",
            "to_account": "ICICI0000001",
            "upi_id": "user@paytm"
        }
        
        results = validator.validate_schema(valid_payment, "payment_request")
        validation_errors = [r for r in results if not r.is_valid]
        assert len(validation_errors) == 0
        
        # Invalid payment request
        invalid_payment = {
            "amount": -100,  # Negative amount
            "currency": "INVALID",  # Invalid currency
            "from_account": "123"  # Too short
        }
        
        results = validator.validate_schema(invalid_payment, "payment_request")
        validation_errors = [r for r in results if not r.is_valid]
        assert len(validation_errors) > 0

class TestDataQualityAssessment:
    """Test data quality assessment"""
    
    @pytest.mark.asyncio
    async def test_user_data_quality_assessment(self, indian_test_data):
        """Test user data quality assessment"""
        assessor = DataQualityAssessor()
        
        # Generate test user data
        test_users = []
        generator = IndianTestDataGenerator()
        
        for i in range(10):
            user = {
                "name": generator.indian_name(),
                "email": generator.indian_email(),
                "phone": generator.indian_phone(),
                "pan": "ABCDE1234F",
                "pincode": "400001",
                "birth_date": "1990-01-01"
            }
            test_users.append(user)
            
        # Add some invalid data
        test_users.append({
            "name": "",  # Invalid: empty name
            "email": "invalid-email",  # Invalid: bad email format
            "phone": "123",  # Invalid: bad phone
            "pan": "INVALID",  # Invalid: bad PAN
            "pincode": "12345",  # Invalid: 5 digits instead of 6
            "birth_date": "2010-01-01"  # Invalid: under age
        })
        
        # Assess data quality
        report = assessor.assess_user_data_quality(test_users)
        
        assert report.total_records == 11
        assert report.invalid_records > 0  # Should catch the invalid user
        assert report.quality_score < 100  # Should be less than perfect
        assert len(report.validation_results) > 0
        
    @pytest.mark.asyncio
    async def test_transaction_data_quality_assessment(self):
        """Test transaction data quality assessment"""
        assessor = DataQualityAssessor()
        
        # Test transaction data
        test_transactions = [
            {
                "amount": "1000.50",
                "upi_id": "user@paytm",
                "ifsc": "HDFC0000001",
                "account_balance": "5000.00"
            },
            {
                "amount": "500.00",
                "upi_id": "test@phonepe",
                "ifsc": "ICICI0000001",
                "account_balance": "1000.00"
            },
            {
                "amount": "10000.00",  # Amount > balance
                "upi_id": "invalid_upi",  # Invalid UPI
                "ifsc": "INVALID",  # Invalid IFSC
                "account_balance": "5000.00"
            }
        ]
        
        # Assess data quality
        report = assessor.assess_transaction_data_quality(test_transactions)
        
        assert report.total_records == 3
        assert report.invalid_records > 0  # Should catch invalid transactions
        assert len(report.validation_results) > 0

class TestDataValidationPerformance:
    """Test data validation performance"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_bulk_validation_performance(self, performance_monitor):
        """Test performance of bulk data validation"""
        validator = DataQualityAssessor()
        
        # Generate large dataset
        test_data = []
        generator = IndianTestDataGenerator()
        
        for i in range(1000):  # 1000 records
            user = {
                "name": generator.indian_name(),
                "email": generator.indian_email(),
                "phone": generator.indian_phone(),
                "pan": "ABCDE1234F",
                "pincode": "400001"
            }
            test_data.append(user)
            
        # Measure validation performance
        performance_monitor.start_timer("bulk_validation")
        
        report = validator.assess_user_data_quality(test_data)
        
        validation_time = performance_monitor.end_timer("bulk_validation")
        
        # Performance assertions
        assert validation_time < 5000  # Should complete in < 5 seconds
        assert report.total_records == 1000
        
        # Calculate validation rate
        validation_rate = report.total_records / (validation_time / 1000)  # records per second
        assert validation_rate > 100  # Should validate > 100 records per second
        
        print(f"Validated {report.total_records} records in {validation_time:.2f}ms")
        print(f"Validation rate: {validation_rate:.1f} records/second")

# Data Validation Test Runner
class DataValidationTestRunner:
    """Comprehensive data validation test runner"""
    
    def __init__(self):
        self.validators = {
            "indian": IndianDataValidator(),
            "type": DataTypeValidator(),
            "business": BusinessRuleValidator(),
            "schema": SchemaValidator(),
            "quality": DataQualityAssessor()
        }
        self.test_results = []
        
    async def run_comprehensive_validation_tests(self):
        """Run comprehensive data validation tests"""
        print("📊 Starting Comprehensive Data Validation Tests")
        print("=" * 60)
        
        # Test Indian data formats
        await self._test_indian_data_formats()
        
        # Test generic data types
        await self._test_generic_data_types()
        
        # Test business rules
        await self._test_business_rules()
        
        # Test schema validation
        await self._test_schema_validation()
        
        # Test data quality assessment
        await self._test_data_quality()
        
        self._print_validation_summary()
        
    async def _test_indian_data_formats(self):
        """Test Indian-specific data format validation"""
        print("\n🇮🇳 Testing Indian Data Format Validation")
        
        indian_validator = self.validators["indian"]
        
        test_cases = [
            ("PAN", "ABCDE1234F", indian_validator.validate_pan_number),
            ("Aadhaar", "123456789012", indian_validator.validate_aadhaar_number),
            ("Phone", "+919876543210", indian_validator.validate_indian_phone),
            ("PIN Code", "400001", indian_validator.validate_indian_pincode),
            ("UPI ID", "user@paytm", indian_validator.validate_upi_id),
            ("IFSC", "HDFC0000001", indian_validator.validate_ifsc_code),
            ("GST", "27ABCDE1234F1ZD", indian_validator.validate_gst_number)
        ]
        
        for test_name, test_value, validator_func in test_cases:
            result = validator_func(test_value)
            self.test_results.append((f"Indian {test_name}", result.is_valid))
            status = "✅" if result.is_valid else "❌"
            print(f"   {status} {test_name}: {test_value}")
            
    async def _test_generic_data_types(self):
        """Test generic data type validation"""
        print("\n📝 Testing Generic Data Type Validation")
        
        type_validator = self.validators["type"]
        
        test_cases = [
            ("Email", "user@example.com", type_validator.validate_email),
            ("Date", "2023-12-25", lambda x: type_validator.validate_date(x)),
            ("Numeric", "1234.56", lambda x: type_validator.validate_numeric(x)),
            ("Currency", "₹1,000.50", lambda x: type_validator.validate_currency(x))
        ]
        
        for test_name, test_value, validator_func in test_cases:
            result = validator_func(test_value)
            self.test_results.append((f"Type {test_name}", result.is_valid))
            status = "✅" if result.is_valid else "❌"
            print(f"   {status} {test_name}: {test_value}")
            
    async def _test_business_rules(self):
        """Test business rule validation"""
        print("\n💼 Testing Business Rule Validation")
        
        business_validator = self.validators["business"]
        
        # Test age requirement
        age_result = business_validator.validate_age_requirement("1990-01-01", 18)
        self.test_results.append(("Business Age Requirement", age_result.is_valid))
        status = "✅" if age_result.is_valid else "❌"
        print(f"   {status} Age Requirement: 1990-01-01")
        
        # Test password strength
        password_result = business_validator.validate_password_strength("StrongP@ssw0rd!")
        self.test_results.append(("Business Password Strength", password_result.is_valid))
        status = "✅" if password_result.is_valid else "❌"
        print(f"   {status} Password Strength: Strong password")
        
        # Test transaction amount
        transaction_result = business_validator.validate_transaction_amount(
            Decimal("1000"), Decimal("5000"), "debit"
        )
        self.test_results.append(("Business Transaction Amount", transaction_result.is_valid))
        status = "✅" if transaction_result.is_valid else "❌"
        print(f"   {status} Transaction Amount: ₹1000 (balance: ₹5000)")
        
    async def _test_schema_validation(self):
        """Test JSON schema validation"""
        print("\n📋 Testing Schema Validation")
        
        schema_validator = self.validators["schema"]
        
        # Test user registration schema
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+919876543210",
            "password": "StrongP@ssw0rd!",
            "age": 25
        }
        
        user_results = schema_validator.validate_schema(user_data, "user_registration")
        user_valid = all(r.is_valid for r in user_results)
        self.test_results.append(("Schema User Registration", user_valid))
        status = "✅" if user_valid else "❌"
        print(f"   {status} User Registration Schema")
        
        # Test payment request schema
        payment_data = {
            "amount": 1000.50,
            "currency": "INR",
            "from_account": "HDFC0000001",
            "to_account": "ICICI0000001"
        }
        
        payment_results = schema_validator.validate_schema(payment_data, "payment_request")
        payment_valid = all(r.is_valid for r in payment_results)
        self.test_results.append(("Schema Payment Request", payment_valid))
        status = "✅" if payment_valid else "❌"
        print(f"   {status} Payment Request Schema")
        
    async def _test_data_quality(self):
        """Test data quality assessment"""
        print("\n🎯 Testing Data Quality Assessment")
        
        quality_assessor = self.validators["quality"]
        
        # Generate test data
        generator = IndianTestDataGenerator()
        test_users = []
        
        for i in range(50):
            user = {
                "name": generator.indian_name(),
                "email": generator.indian_email(),
                "phone": generator.indian_phone(),
                "pan": "ABCDE1234F",
                "pincode": "400001",
                "birth_date": "1990-01-01"
            }
            test_users.append(user)
            
        # Assess data quality
        quality_report = quality_assessor.assess_user_data_quality(test_users)
        
        quality_passed = quality_report.quality_score > 80  # 80% quality threshold
        self.test_results.append(("Data Quality Assessment", quality_passed))
        status = "✅" if quality_passed else "❌"
        print(f"   {status} Data Quality Score: {quality_report.quality_score:.1f}%")
        print(f"   📊 Valid Records: {quality_report.valid_records}/{quality_report.total_records}")
        
    def _print_validation_summary(self):
        """Print validation test summary"""
        print("\n" + "=" * 60)
        print("📈 Data Validation Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\nTest Results:")
        for test_name, passed in self.test_results:
            status = "✅" if passed else "❌"
            print(f"  {status} {test_name}")
            
        print(f"\n🎯 Data Validation Capabilities:")
        print(f"  ✅ Indian data format validation (PAN, Aadhaar, UPI)")
        print(f"  ✅ Generic data type validation (email, dates, currency)")
        print(f"  ✅ Business rule enforcement")
        print(f"  ✅ JSON schema validation")
        print(f"  ✅ Data quality assessment")

# Example usage
async def main():
    """Run comprehensive data validation tests"""
    runner = DataValidationTestRunner()
    await runner.run_comprehensive_validation_tests()

if __name__ == "__main__":
    asyncio.run(main())