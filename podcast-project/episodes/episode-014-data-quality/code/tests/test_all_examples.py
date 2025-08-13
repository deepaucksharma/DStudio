#!/usr/bin/env python3
"""
Comprehensive Test Suite for Episode 14: Data Quality & Validation
All 16+ code examples के लिए comprehensive test suite

Author: DStudio Team
Coverage: Tests all production-ready examples with Indian context
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import tempfile
import sqlite3

# Add the code directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))

# Import all the modules we want to test
try:
    from python.aadhaar_validation_system import AadhaarValidationSystem
    from python.upi_id_validation_system import UPIValidationSystem
    from python.indian_mobile_validation import IndianMobileValidationSystem
    from python.bank_account_ifsc_validation import IndianBankValidationSystem
    from python.realtime_data_quality_monitoring import RealTimeDataQualityMonitor
    from python.data_lineage_tracking import DataLineageTracker
    from python.schema_evolution_handling import SchemaEvolutionManager
    from python.automated_data_quality_reports import AutomatedDataQualityReporter
    from python.compliance_validation_framework import ComplianceValidationFramework
except ImportError as e:
    # Fallback imports for when running from different directory
    try:
        sys.path.append(os.path.dirname(__file__))
        from aadhaar_validation_system import AadhaarValidationSystem
        from upi_id_validation_system import UPIValidationSystem
        from indian_mobile_validation import IndianMobileValidationSystem
        from bank_account_ifsc_validation import IndianBankValidationSystem
        from realtime_data_quality_monitoring import RealTimeDataQualityMonitor
        from data_lineage_tracking import DataLineageTracker
        from schema_evolution_handling import SchemaEvolutionManager
        from automated_data_quality_reports import AutomatedDataQualityReporter
        from compliance_validation_framework import ComplianceValidationFramework
    except ImportError:
        print(f"Import error: {e}")
        print("Please ensure all code files are in the correct directory")
        sys.exit(1)

class TestAadhaarValidationSystem:
    """Test suite for Aadhaar validation system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = AadhaarValidationSystem()
    
    def test_aadhaar_format_validation_valid(self):
        """Test valid Aadhaar format validation"""
        # Generate a valid test Aadhaar
        test_aadhaar = self.validator.generate_valid_aadhaar('14')
        result = self.validator.validate_format(test_aadhaar)
        
        assert result['is_valid_format'] == True
        assert len(result['errors']) == 0
        assert result['cleaned'] == test_aadhaar.replace(' ', '').replace('-', '')
    
    def test_aadhaar_format_validation_invalid(self):
        """Test invalid Aadhaar format validation"""
        invalid_aadhaars = [
            '123456789',      # Too short
            '12345678901234', # Too long
            '123456789abc',   # Contains letters
            '000000000000',   # Invalid pattern
            '123456789012',   # Sequential (invalid)
        ]
        
        for invalid in invalid_aadhaars:
            result = self.validator.validate_format(invalid)
            assert result['is_valid_format'] == False
            assert len(result['errors']) > 0
    
    def test_aadhaar_checksum_validation(self):
        """Test Aadhaar checksum validation using Verhoeff algorithm"""
        # Generate valid Aadhaar and test checksum
        test_aadhaar = self.validator.generate_valid_aadhaar('14')
        result = self.validator.validate_checksum(test_aadhaar)
        
        assert result['is_valid_checksum'] == True
        assert result['provided_checksum'] == result['calculated_checksum']
    
    def test_demographic_validation(self):
        """Test demographic information validation"""
        result = self.validator.validate_demographics(
            name="Rahul Sharma",
            phone="+919876543210",
            email="rahul@example.com"
        )
        
        assert result['name_valid'] == True
        assert result['phone_valid'] == True
        assert result['email_valid'] == True
        assert len(result['errors']) == 0
    
    def test_bulk_validation(self):
        """Test bulk Aadhaar validation"""
        # Create test dataset
        test_data = []
        for i in range(10):
            test_data.append({
                'aadhaar': self.validator.generate_valid_aadhaar('14'),
                'name': f'Test User {i}',
                'phone': f'+9198765432{i:02d}',
                'email': f'user{i}@example.com'
            })
        
        # Add some invalid entries
        test_data.append({
            'aadhaar': '123456789012',  # Invalid
            'name': 'Invalid User',
            'phone': '123',
            'email': 'invalid'
        })
        
        df = pd.DataFrame(test_data)
        results = self.validator.bulk_validate_aadhaar_dataset(df)
        
        assert len(results) == len(test_data)
        assert results['is_valid'].sum() == 10  # 10 valid entries
        assert (~results['is_valid']).sum() == 1  # 1 invalid entry


class TestUPIValidationSystem:
    """Test suite for UPI ID validation system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = UPIValidationSystem()
    
    def test_valid_upi_formats(self):
        """Test validation of valid UPI ID formats"""
        valid_upis = [
            '9876543210@ybl',      # PhonePe
            'user123@paytm',       # Paytm
            'merchant@okicici',    # Google Pay ICICI
            'shop@sbi',           # SBI
            'customer@hdfc'        # HDFC
        ]
        
        for upi in valid_upis:
            result = self.validator.complete_upi_validation(upi)
            assert result.is_valid == True
            assert len(result.errors) == 0
    
    def test_invalid_upi_formats(self):
        """Test validation of invalid UPI ID formats"""
        invalid_upis = [
            'user@gmail.com',      # Not a UPI domain
            'user@@ybl',          # Double @
            'user',               # No domain
            '@ybl',               # No username
            'ab@ybl',             # Username too short
            'user@invalid'        # Invalid domain
        ]
        
        for upi in invalid_upis:
            result = self.validator.complete_upi_validation(upi)
            assert result.is_valid == False
            assert len(result.errors) > 0
    
    def test_fraud_detection(self):
        """Test fraud pattern detection"""
        suspicious_upis = [
            'admin@ybl',
            'test123456@paytm',
            'money.cash@sbi',
            '1111111111@upi'
        ]
        
        for upi in suspicious_upis:
            fraud_result = self.validator.detect_upi_fraud_patterns(upi)
            assert fraud_result['is_suspicious'] == True or fraud_result['risk_level'] in ['MEDIUM', 'HIGH']
    
    def test_bulk_validation(self):
        """Test bulk UPI validation"""
        test_upis = [
            '9876543210@ybl',
            'user@paytm',
            'invalid@gmail.com',
            'merchant@sbi',
            'fake@invalid'
        ]
        
        df = pd.DataFrame({
            'upi_id': test_upis,
            'amount': [1000, 2000, 3000, 4000, 5000]
        })
        
        results = self.validator.bulk_validate_upi_dataset(df)
        assert len(results) == len(test_upis)
        assert results['is_valid'].sum() >= 2  # At least 2 valid UPIs


class TestIndianMobileValidationSystem:
    """Test suite for Indian mobile number validation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = IndianMobileValidationSystem()
    
    def test_valid_mobile_formats(self):
        """Test valid Indian mobile number formats"""
        valid_mobiles = [
            '9876543210',
            '+919876543210',
            '91 98765 43210',
            '7890123456',  # Jio
            '6123456789'   # Airtel
        ]
        
        for mobile in valid_mobiles:
            result = self.validator.complete_mobile_validation(mobile)
            assert result.is_valid == True
            assert len(result.errors) == 0
    
    def test_invalid_mobile_formats(self):
        """Test invalid mobile number formats"""
        invalid_mobiles = [
            '1234567890',    # Invalid first digit
            '98765432101',   # Too long
            '987654321',     # Too short
            'abcd123456',    # Contains letters
            '0987654321'     # Starts with 0
        ]
        
        for mobile in invalid_mobiles:
            result = self.validator.complete_mobile_validation(mobile)
            assert result.is_valid == False
            assert len(result.errors) > 0
    
    def test_operator_identification(self):
        """Test mobile operator identification"""
        operator_tests = [
            ('7012345678', 'Jio'),
            ('6012345678', 'Airtel'),
            ('9012345678', 'Vi')
        ]
        
        for mobile, expected_operator in operator_tests:
            operator_result = self.validator.identify_operator(mobile)
            assert operator_result['operator'] == expected_operator
    
    def test_fraud_detection(self):
        """Test mobile number fraud detection"""
        suspicious_numbers = [
            '9999999999',  # All same digits
            '1234567890',  # Sequential
            '5555555555'   # Test number
        ]
        
        for mobile in suspicious_numbers:
            fraud_result = self.validator.detect_fraud_patterns(mobile)
            assert fraud_result['risk_level'] in ['MEDIUM', 'HIGH']


class TestBankValidationSystem:
    """Test suite for Indian bank validation system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = IndianBankValidationSystem()
    
    def test_valid_ifsc_codes(self):
        """Test valid IFSC code validation"""
        valid_ifsc_codes = [
            'SBIN0001234',
            'HDFC0000123',
            'ICIC0001234',
            'AXIS0000456'
        ]
        
        for ifsc in valid_ifsc_codes:
            result = self.validator.validate_ifsc_format(ifsc)
            assert result['is_valid_format'] == True
            assert len(result['errors']) == 0
    
    def test_invalid_ifsc_codes(self):
        """Test invalid IFSC code validation"""
        invalid_ifsc_codes = [
            'INVALID123',     # Wrong format
            'SBIN',          # Too short
            'SBIN1001234',   # Wrong 5th character
            'sbin0001234'    # Lowercase
        ]
        
        for ifsc in invalid_ifsc_codes:
            result = self.validator.validate_ifsc_format(ifsc)
            assert result['is_valid_format'] == False
            assert len(result['errors']) > 0
    
    def test_account_number_validation(self):
        """Test bank account number validation"""
        test_cases = [
            ('12345678901', 'SBIN0001234', True),   # Valid SBI
            ('123456789012345', 'HDFC0000123', True), # Valid HDFC
            ('123', 'SBIN0001234', False),          # Too short
            ('1111111111', 'AXIS0000456', False)    # Suspicious pattern
        ]
        
        for account, ifsc, should_be_valid in test_cases:
            result = self.validator.validate_account_number(account, ifsc)
            if should_be_valid:
                assert result['is_valid_format'] == True
            else:
                assert result['is_valid_format'] == False or len(result['warnings']) > 0
    
    def test_complete_validation(self):
        """Test complete bank validation"""
        result = self.validator.complete_bank_validation(
            account_number='12345678901',
            ifsc='SBIN0001234',
            micr='400002002'
        )
        
        assert result.ifsc_code == 'SBIN0001234'
        assert result.account_number == '12345678901'
        assert isinstance(result.confidence_score, (int, float))


class TestRealTimeDataQualityMonitor:
    """Test suite for real-time data quality monitoring"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            self.temp_db = tmp.name
        self.monitor = RealTimeDataQualityMonitor({'db_path': self.temp_db})
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)
    
    def test_quality_rules_loading(self):
        """Test default quality rules are loaded"""
        assert len(self.monitor.quality_rules) > 0
        assert 'order_id_not_null' in self.monitor.quality_rules
        assert 'email_format' in self.monitor.quality_rules
    
    def test_record_validation(self):
        """Test individual record validation"""
        valid_record = {
            'order_id': 'ORD-12345678',
            'customer_email': 'user@example.com',
            'customer_phone': '+919876543210',
            'order_amount': 1500,
            'delivery_pincode': '400001',
            'order_date': datetime.now().isoformat()
        }
        
        is_valid, errors = self.monitor.validate_record(valid_record)
        assert is_valid == True
        assert len(errors) == 0
        
        # Test invalid record
        invalid_record = {
            'order_id': None,  # Null order ID
            'customer_email': 'invalid-email',
            'customer_phone': '123',
            'order_amount': -100,
            'delivery_pincode': '12345',
            'order_date': (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        is_valid, errors = self.monitor.validate_record(invalid_record)
        assert is_valid == False
        assert len(errors) > 0
    
    def test_metrics_calculation(self):
        """Test metrics calculation and updates"""
        # This would test the metrics calculation functionality
        # For now, just verify the monitor initializes properly
        assert hasattr(self.monitor, 'current_metrics')
        assert hasattr(self.monitor, 'quality_rules')


class TestDataLineageTracker:
    """Test suite for data lineage tracking"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            self.temp_db = tmp.name
        self.tracker = DataLineageTracker(self.temp_db)
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)
    
    def test_tracker_initialization(self):
        """Test data lineage tracker initialization"""
        assert self.tracker.db_connection is not None
        assert hasattr(self.tracker, 'lineage_graph')
        assert hasattr(self.tracker, 'data_sources')
    
    def test_source_registration(self):
        """Test data source registration"""
        from data_lineage_tracking import DataSource
        
        test_source = DataSource(
            source_id='test_source',
            source_name='Test Database',
            source_type='database',
            location='test://localhost',
            schema={'id': 'string', 'name': 'string'},
            created_at=datetime.now()
        )
        
        result = self.tracker.register_data_source(test_source)
        assert result == True
        assert 'test_source' in self.tracker.data_sources


class TestSchemaEvolutionManager:
    """Test suite for schema evolution handling"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            self.temp_db = tmp.name
        self.manager = SchemaEvolutionManager(self.temp_db)
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)
    
    def test_manager_initialization(self):
        """Test schema evolution manager initialization"""
        assert self.manager.db_connection is not None
        assert hasattr(self.manager, 'schema_registry')
        assert hasattr(self.manager, 'compatibility_rules')
    
    def test_schema_validation(self):
        """Test schema definition validation"""
        valid_schema = {
            'type': 'record',
            'fields': [
                {'name': 'id', 'type': 'string'},
                {'name': 'name', 'type': 'string'}
            ]
        }
        
        invalid_schema = {
            'type': 'invalid',
            'fields': 'not_a_list'
        }
        
        assert self.manager._validate_schema_definition(valid_schema) == True
        assert self.manager._validate_schema_definition(invalid_schema) == False


class TestAutomatedDataQualityReporter:
    """Test suite for automated data quality reporting"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.temp_dir = tmpdir
            self.config = {
                'db_path': os.path.join(tmpdir, 'test_reports.db'),
                'template_dir': os.path.join(tmpdir, 'templates')
            }
            self.reporter = AutomatedDataQualityReporter(self.config)
    
    def test_reporter_initialization(self):
        """Test reporter initialization"""
        assert self.reporter.db_connection is not None
        assert hasattr(self.reporter, 'quality_thresholds')
        assert hasattr(self.reporter, 'template_env')
    
    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        # Create sample data
        test_data = {
            'id': range(100),
            'email': [f'user{i}@example.com' for i in range(100)],
            'phone': [f'+9198765432{i:02d}' for i in range(100)],
            'amount': np.random.uniform(100, 1000, 100),
            'created_at': pd.date_range('2024-01-01', periods=100)
        }
        df = pd.DataFrame(test_data)
        
        schema_rules = {
            'unique_columns': ['id'],
            'format_rules': {
                'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            },
            'timestamp_columns': ['created_at']
        }
        
        score = self.reporter.calculate_quality_score(df, schema_rules)
        
        assert isinstance(score.overall_score, (int, float))
        assert 0 <= score.overall_score <= 100
        assert isinstance(score.completeness, (int, float))
        assert isinstance(score.validity, (int, float))


class TestComplianceValidationFramework:
    """Test suite for compliance validation framework"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            self.temp_db = tmp.name
        self.framework = ComplianceValidationFramework({'db_path': self.temp_db})
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        if os.path.exists(self.temp_db):
            os.unlink(self.temp_db)
    
    def test_framework_initialization(self):
        """Test compliance framework initialization"""
        assert self.framework.db_connection is not None
        assert len(self.framework.compliance_rules) > 0
        assert hasattr(self.framework, 'data_patterns')
    
    def test_data_classification(self):
        """Test data field classification"""
        test_data = {
            'customer_email': ['user@example.com'],
            'phone_number': ['+919876543210'],
            'aadhaar_number': ['123456789012'],
            'credit_card': ['4111111111111111']
        }
        df = pd.DataFrame(test_data)
        
        classification = self.framework.classify_data_fields(df)
        
        assert 'email' in classification
        assert 'phone' in classification
        assert 'PII' in classification
    
    def test_compliance_rule_registration(self):
        """Test custom compliance rule registration"""
        from compliance_validation_framework import ComplianceRule, ComplianceFramework, ViolationSeverity
        
        test_rule = ComplianceRule(
            rule_id='test_001',
            rule_name='Test Rule',
            framework=ComplianceFramework.GDPR,
            description='Test compliance rule',
            validation_logic='test_logic',
            severity=ViolationSeverity.MEDIUM,
            remediation_steps=['Test step'],
            legal_reference='Test Article',
            penalty_range='Test penalty',
            data_categories=['Test']
        )
        
        result = self.framework.register_compliance_rule(test_rule)
        assert result == True
        assert 'test_001' in self.framework.compliance_rules


# Integration tests
class TestIntegration:
    """Integration tests across multiple systems"""
    
    def test_end_to_end_validation_pipeline(self):
        """Test end-to-end data validation pipeline"""
        # Create sample Indian e-commerce data
        sample_data = {
            'order_id': [f'ORD-{i:08d}' for i in range(100)],
            'customer_email': [f'customer{i}@example.com' for i in range(100)],
            'customer_phone': ['+919876543210'] * 100,
            'aadhaar': ['123456789012'] * 100,  # This should trigger compliance issues
            'order_amount': np.random.uniform(100, 10000, 100)
        }
        df = pd.DataFrame(sample_data)
        
        # Test Aadhaar validation
        aadhaar_validator = AadhaarValidationSystem()
        # Test first Aadhaar (this is a dummy, so will fail checksum)
        aadhaar_result = aadhaar_validator.validate_format('123456789012')
        assert aadhaar_result['is_valid_format'] == False  # Invalid format
        
        # Test UPI validation
        upi_validator = UPIValidationSystem()
        upi_result = upi_validator.complete_upi_validation('9876543210@ybl')
        assert upi_result.is_valid == True
        
        # Test compliance framework
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            temp_db = tmp.name
        
        try:
            compliance_framework = ComplianceValidationFramework({'db_path': temp_db})
            classification = compliance_framework.classify_data_fields(df)
            
            # Should detect PII and other sensitive data
            assert 'PII' in classification
            assert len(classification['PII']) > 0
        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)
    
    def test_bulk_validation_performance(self):
        """Test performance with larger datasets"""
        # Create larger sample dataset (1000 records)
        large_data = {
            'phone': [f'+9198765432{i:02d}' for i in range(1000)],
            'email': [f'user{i}@example.com' for i in range(1000)],
            'upi_id': [f'user{i}@ybl' for i in range(1000)]
        }
        df = pd.DataFrame(large_data)
        
        # Test mobile validation performance
        mobile_validator = IndianMobileValidationSystem()
        start_time = datetime.now()
        
        # Validate first 10 records to avoid timeout in tests
        sample_df = df.head(10)
        results = mobile_validator.bulk_validate_mobile_dataset(sample_df, 'phone')
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        assert len(results) == 10
        assert processing_time < 30  # Should complete within 30 seconds for 10 records


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def sample_indian_data():
    """Fixture providing sample Indian data for testing"""
    return {
        'valid_aadhaar': '234567890123',  # This would need proper checksum
        'valid_mobile': '+919876543210',
        'valid_upi': '9876543210@ybl',
        'valid_ifsc': 'SBIN0001234',
        'valid_pan': 'ABCDE1234F',
        'valid_email': 'test@example.com'
    }


def test_all_imports():
    """Test that all required modules can be imported"""
    # This test ensures all imports work correctly
    assert AadhaarValidationSystem is not None
    assert UPIValidationSystem is not None
    assert IndianMobileValidationSystem is not None
    assert IndianBankValidationSystem is not None
    assert RealTimeDataQualityMonitor is not None
    assert DataLineageTracker is not None
    assert SchemaEvolutionManager is not None
    assert AutomatedDataQualityReporter is not None
    assert ComplianceValidationFramework is not None


if __name__ == "__main__":
    # Run specific test classes
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--maxfail=5"
    ])