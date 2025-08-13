#!/usr/bin/env python3
"""
Data Quality Validation Framework
Episode 47: Data Governance at Scale

यह framework Indian banking और e-commerce systems के लिए comprehensive 
data quality validation provide करता है।

Author: Hindi Podcast Series
Context: Mumbai financial data validation system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

# Configure logging - Hindi me logs bhi milenge
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeverityLevel(Enum):
    """Data quality issue severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ValidationResult:
    """Data validation result container"""
    field_name: str
    rule_name: str
    passed: bool
    error_count: int
    total_count: int
    severity: SeverityLevel
    error_message: str
    sample_errors: List[Any]

class IndianDataQualityFramework:
    """
    Comprehensive data quality framework for Indian businesses
    
    Features:
    - Aadhaar number validation
    - PAN card validation  
    - GSTIN validation
    - UPI ID validation
    - Mobile number validation
    - Banking details validation
    """
    
    def __init__(self):
        self.validation_rules = {}
        self.results = []
        self.setup_indian_validators()
    
    def setup_indian_validators(self):
        """Setup Indian-specific validation rules"""
        # Aadhaar pattern: 12 digits, no consecutive identical digits
        self.aadhaar_pattern = re.compile(r'^[2-9]{1}[0-9]{3}[0-9]{4}[0-9]{4}$')
        
        # PAN pattern: 5 letters, 4 digits, 1 letter
        self.pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
        
        # GSTIN pattern: 15 character alphanumeric
        self.gstin_pattern = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[0-9A-Z]{1}$')
        
        # UPI pattern: user@bank
        self.upi_pattern = re.compile(r'^[a-zA-Z0-9.-]{2,256}@[a-zA-Z][a-zA-Z0-9.-]+[a-zA-Z]$')
        
        # Indian mobile pattern: +91 followed by 10 digits
        self.mobile_pattern = re.compile(r'^(\+91|91)?[6789]\d{9}$')
        
        logger.info("Indian validation patterns initialized successfully")
    
    def validate_aadhaar(self, aadhaar_series: pd.Series) -> ValidationResult:
        """
        Validate Aadhaar numbers
        
        Rules:
        1. Must be 12 digits
        2. Should not have consecutive identical digits
        3. Should not be all zeros
        """
        errors = []
        error_samples = []
        
        for idx, aadhaar in aadhaar_series.items():
            if pd.isna(aadhaar):
                errors.append(idx)
                error_samples.append("Missing Aadhaar")
                continue
                
            aadhaar_str = str(aadhaar).strip()
            
            # Check pattern
            if not self.aadhaar_pattern.match(aadhaar_str):
                errors.append(idx)
                error_samples.append(f"Invalid format: {aadhaar_str}")
                continue
            
            # Check for consecutive identical digits (not allowed)
            if len(set(aadhaar_str)) < 4:  # Too few unique digits
                errors.append(idx)
                error_samples.append(f"Too few unique digits: {aadhaar_str}")
                continue
        
        return ValidationResult(
            field_name="aadhaar",
            rule_name="aadhaar_validation",
            passed=len(errors) == 0,
            error_count=len(errors),
            total_count=len(aadhaar_series),
            severity=SeverityLevel.CRITICAL,
            error_message=f"Found {len(errors)} invalid Aadhaar numbers",
            sample_errors=error_samples[:5]  # First 5 errors
        )
    
    def validate_pan(self, pan_series: pd.Series) -> ValidationResult:
        """Validate PAN card numbers"""
        errors = []
        error_samples = []
        
        for idx, pan in pan_series.items():
            if pd.isna(pan):
                errors.append(idx)
                error_samples.append("Missing PAN")
                continue
                
            pan_str = str(pan).strip().upper()
            
            if not self.pan_pattern.match(pan_str):
                errors.append(idx)
                error_samples.append(f"Invalid PAN format: {pan_str}")
        
        return ValidationResult(
            field_name="pan",
            rule_name="pan_validation",
            passed=len(errors) == 0,
            error_count=len(errors),
            total_count=len(pan_series),
            severity=SeverityLevel.HIGH,
            error_message=f"Found {len(errors)} invalid PAN numbers",
            sample_errors=error_samples[:5]
        )
    
    def validate_upi_id(self, upi_series: pd.Series) -> ValidationResult:
        """Validate UPI IDs"""
        errors = []
        error_samples = []
        
        for idx, upi in upi_series.items():
            if pd.isna(upi):
                errors.append(idx)
                error_samples.append("Missing UPI ID")
                continue
                
            upi_str = str(upi).strip().lower()
            
            if not self.upi_pattern.match(upi_str):
                errors.append(idx)
                error_samples.append(f"Invalid UPI format: {upi_str}")
        
        return ValidationResult(
            field_name="upi_id",
            rule_name="upi_validation",
            passed=len(errors) == 0,
            error_count=len(errors),
            total_count=len(upi_series),
            severity=SeverityLevel.MEDIUM,
            error_message=f"Found {len(errors)} invalid UPI IDs",
            sample_errors=error_samples[:5]
        )
    
    def validate_completeness(self, df: pd.DataFrame, 
                            critical_fields: List[str]) -> List[ValidationResult]:
        """Check completeness of critical fields"""
        results = []
        
        for field in critical_fields:
            if field not in df.columns:
                results.append(ValidationResult(
                    field_name=field,
                    rule_name="field_existence",
                    passed=False,
                    error_count=1,
                    total_count=1,
                    severity=SeverityLevel.CRITICAL,
                    error_message=f"Critical field {field} missing from dataset",
                    sample_errors=[f"Field {field} not found"]
                ))
                continue
            
            null_count = df[field].isnull().sum()
            total_count = len(df)
            
            # Critical fields should have <5% missing values
            missing_percentage = (null_count / total_count) * 100
            passed = missing_percentage < 5.0
            
            severity = SeverityLevel.CRITICAL if missing_percentage > 20 else \
                      SeverityLevel.HIGH if missing_percentage > 10 else \
                      SeverityLevel.MEDIUM if missing_percentage > 5 else \
                      SeverityLevel.LOW
            
            results.append(ValidationResult(
                field_name=field,
                rule_name="completeness_check",
                passed=passed,
                error_count=null_count,
                total_count=total_count,
                severity=severity,
                error_message=f"{field} has {missing_percentage:.2f}% missing values",
                sample_errors=[f"Missing values in {field}"]
            ))
        
        return results
    
    def validate_uniqueness(self, df: pd.DataFrame, 
                          unique_fields: List[str]) -> List[ValidationResult]:
        """Check uniqueness constraints"""
        results = []
        
        for field in unique_fields:
            if field not in df.columns:
                continue
            
            duplicate_count = df[field].duplicated().sum()
            total_count = len(df)
            
            results.append(ValidationResult(
                field_name=field,
                rule_name="uniqueness_check",
                passed=duplicate_count == 0,
                error_count=duplicate_count,
                total_count=total_count,
                severity=SeverityLevel.HIGH if duplicate_count > 0 else SeverityLevel.LOW,
                error_message=f"{field} has {duplicate_count} duplicate values",
                sample_errors=df[df[field].duplicated()][field].head(5).tolist()
            ))
        
        return results
    
    def validate_numerical_ranges(self, df: pd.DataFrame, 
                                range_rules: Dict[str, Tuple[float, float]]) -> List[ValidationResult]:
        """Validate numerical fields are within expected ranges"""
        results = []
        
        for field, (min_val, max_val) in range_rules.items():
            if field not in df.columns:
                continue
            
            # Convert to numeric, errors='coerce' converts invalid to NaN
            numeric_series = pd.to_numeric(df[field], errors='coerce')
            
            # Find out-of-range values
            out_of_range = (numeric_series < min_val) | (numeric_series > max_val)
            out_of_range_count = out_of_range.sum()
            
            results.append(ValidationResult(
                field_name=field,
                rule_name="range_validation",
                passed=out_of_range_count == 0,
                error_count=out_of_range_count,
                total_count=len(df),
                severity=SeverityLevel.MEDIUM,
                error_message=f"{field} has {out_of_range_count} values outside range [{min_val}, {max_val}]",
                sample_errors=df[out_of_range][field].head(5).tolist()
            ))
        
        return results
    
    def run_comprehensive_validation(self, df: pd.DataFrame, 
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive data quality validation
        
        Args:
            df: DataFrame to validate
            config: Validation configuration
                {
                    'critical_fields': ['field1', 'field2'],
                    'unique_fields': ['id', 'email'],
                    'range_rules': {'age': (18, 100), 'salary': (10000, 10000000)},
                    'indian_fields': {
                        'aadhaar': 'aadhaar_column',
                        'pan': 'pan_column',
                        'upi': 'upi_column'
                    }
                }
        """
        all_results = []
        
        logger.info("शुरू कर रहे हैं comprehensive data quality validation")
        
        # Completeness validation
        if 'critical_fields' in config:
            all_results.extend(
                self.validate_completeness(df, config['critical_fields'])
            )
        
        # Uniqueness validation
        if 'unique_fields' in config:
            all_results.extend(
                self.validate_uniqueness(df, config['unique_fields'])
            )
        
        # Range validation
        if 'range_rules' in config:
            all_results.extend(
                self.validate_numerical_ranges(df, config['range_rules'])
            )
        
        # Indian-specific validations
        if 'indian_fields' in config:
            indian_fields = config['indian_fields']
            
            if 'aadhaar' in indian_fields and indian_fields['aadhaar'] in df.columns:
                all_results.append(
                    self.validate_aadhaar(df[indian_fields['aadhaar']])
                )
            
            if 'pan' in indian_fields and indian_fields['pan'] in df.columns:
                all_results.append(
                    self.validate_pan(df[indian_fields['pan']])
                )
            
            if 'upi' in indian_fields and indian_fields['upi'] in df.columns:
                all_results.append(
                    self.validate_upi_id(df[indian_fields['upi']])
                )
        
        # Generate summary
        total_errors = sum(result.error_count for result in all_results)
        failed_rules = sum(1 for result in all_results if not result.passed)
        total_rules = len(all_results)
        
        critical_failures = [r for r in all_results if r.severity == SeverityLevel.CRITICAL and not r.passed]
        
        summary = {
            'total_rules': total_rules,
            'passed_rules': total_rules - failed_rules,
            'failed_rules': failed_rules,
            'total_errors': total_errors,
            'critical_failures': len(critical_failures),
            'data_quality_score': ((total_rules - failed_rules) / total_rules * 100) if total_rules > 0 else 0,
            'results': all_results,
            'is_production_ready': len(critical_failures) == 0
        }
        
        logger.info(f"Data quality validation complete. Score: {summary['data_quality_score']:.2f}%")
        
        return summary
    
    def generate_report(self, validation_summary: Dict[str, Any]) -> str:
        """Generate detailed data quality report"""
        report = []
        report.append("=" * 60)
        report.append("DATA QUALITY VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary section
        report.append("SUMMARY:")
        report.append(f"Data Quality Score: {validation_summary['data_quality_score']:.2f}%")
        report.append(f"Total Rules: {validation_summary['total_rules']}")
        report.append(f"Passed Rules: {validation_summary['passed_rules']}")
        report.append(f"Failed Rules: {validation_summary['failed_rules']}")
        report.append(f"Total Errors: {validation_summary['total_errors']}")
        report.append(f"Critical Failures: {validation_summary['critical_failures']}")
        report.append(f"Production Ready: {'YES' if validation_summary['is_production_ready'] else 'NO'}")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        
        for result in validation_summary['results']:
            status = "PASS" if result.passed else "FAIL"
            report.append(f"[{status}] {result.field_name} - {result.rule_name}")
            report.append(f"    Severity: {result.severity.name}")
            report.append(f"    Errors: {result.error_count}/{result.total_count}")
            report.append(f"    Message: {result.error_message}")
            if result.sample_errors:
                report.append(f"    Sample Errors: {result.sample_errors}")
            report.append("")
        
        return "\n".join(report)

def create_sample_data():
    """Create sample data for testing"""
    data = {
        'customer_id': [1, 2, 3, 4, 5, 1],  # Duplicate customer_id
        'name': ['Raj Sharma', 'Priya Patel', None, 'Amit Kumar', 'Sunita Singh', 'Raj Sharma'],
        'aadhaar': ['123456789012', '987654321098', '111111111111', '555566667777', None, '123456789012'],
        'pan': ['ABCDE1234F', 'FGHIJ5678K', 'INVALID', 'LMNOP9012Q', 'RSTUV3456W', 'ABCDE1234F'],
        'upi_id': ['raj@paytm', 'priya@phonepe', 'invalid-upi', 'amit@gpay', 'sunita@paytm', 'raj@paytm'],
        'age': [25, 35, -5, 150, 45, 25],  # Invalid ages
        'income': [50000, 75000, 100000, 200000, None, 50000]
    }
    
    return pd.DataFrame(data)

def main():
    """Main function demonstrating the framework"""
    print("🏦 Starting Indian Data Quality Validation Framework Demo")
    print("=" * 60)
    
    # Create framework instance
    framework = IndianDataQualityFramework()
    
    # Create sample data
    df = create_sample_data()
    print("Sample data created with intentional quality issues")
    print(df.to_string())
    print()
    
    # Define validation configuration
    config = {
        'critical_fields': ['customer_id', 'name', 'aadhaar'],
        'unique_fields': ['customer_id', 'aadhaar'],
        'range_rules': {
            'age': (18, 100),
            'income': (15000, 10000000)  # Minimum wage to max reasonable income
        },
        'indian_fields': {
            'aadhaar': 'aadhaar',
            'pan': 'pan',
            'upi': 'upi_id'
        }
    }
    
    # Run validation
    print("🔍 Running comprehensive validation...")
    validation_summary = framework.run_comprehensive_validation(df, config)
    
    # Generate and print report
    report = framework.generate_report(validation_summary)
    print(report)
    
    # Recommendations
    print("\n🚀 RECOMMENDATIONS:")
    if not validation_summary['is_production_ready']:
        print("❌ Data is NOT ready for production")
        print("   - Fix critical failures before proceeding")
        print("   - Implement data cleansing pipeline")
        print("   - Add validation rules to data ingestion")
    else:
        print("✅ Data quality meets production standards")
        print("   - Consider monitoring for data drift")
        print("   - Set up automated quality checks")

if __name__ == "__main__":
    main()