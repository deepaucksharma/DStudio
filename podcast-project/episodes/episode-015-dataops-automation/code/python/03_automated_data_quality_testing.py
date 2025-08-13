#!/usr/bin/env python3
"""
DataOps Example 03: Automated Data Quality Testing
Comprehensive data quality testing framework for Indian companies
Focus: IRCTC booking data, UPI transaction validation, Aadhaar data quality

Author: DataOps Architecture Series  
Episode: 015 - DataOps Automation
"""

import os
import sys
import json
import uuid
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re
import phonenumbers
from phonenumbers import NumberParseException
import great_expectations as ge
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.checkpoint import SimpleCheckpoint
import sqlite3
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dataops/data_quality.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()

class QualityCheckType(Enum):
    """Types of data quality checks for Indian data"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    INDIAN_SPECIFIC = "indian_specific"

class SeverityLevel(Enum):
    """Severity levels for quality issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class QualityCheckResult:
    """Result of a data quality check"""
    check_id: str
    check_name: str
    check_type: QualityCheckType
    dataset_name: str
    passed: bool
    score: float
    threshold: float
    severity: SeverityLevel
    message: str
    details: Dict[str, Any]
    execution_time: datetime
    affected_rows: int = 0
    cost_impact_inr: float = 0.0

class DataQualityCheck(Base):
    """Data quality check results table"""
    __tablename__ = 'data_quality_results'
    
    id = Column(String, primary_key=True)
    check_id = Column(String, nullable=False)
    check_name = Column(String, nullable=False)
    check_type = Column(String, nullable=False)
    dataset_name = Column(String, nullable=False)
    passed = Column(Boolean, nullable=False)
    score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(Text)
    details = Column(JSON)
    execution_time = Column(DateTime, default=datetime.utcnow)
    affected_rows = Column(Integer, default=0)
    cost_impact_inr = Column(Float, default=0.0)

class IndianDataValidator:
    """
    Specialized validator for Indian data formats
    Handles Aadhaar, PAN, UPI, phone numbers, addresses, etc.
    """
    
    def __init__(self):
        # Indian data patterns
        self.patterns = {
            'aadhaar': r'^\d{4}\s?\d{4}\s?\d{4}$',
            'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
            'upi_id': r'^[\w\.\-\_]+@[\w\-\_]+$',
            'indian_mobile': r'^(\+91[\-\s]?)?[0]?(91)?[6-9]\d{9}$',
            'ifsc': r'^[A-Z]{4}0[A-Z0-9]{6}$',
            'gstin': r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$',
            'pincode': r'^[1-9][0-9]{5}$',
            'vehicle_number': r'^[A-Z]{2}[ -]?[0-9]{1,2}(?: [A-Z])?(?: [A-Z]*)? [0-9]{4}$'
        }
        
        # State codes for validation
        self.state_codes = {
            '01': 'Jammu and Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab',
            '04': 'Chandigarh', '05': 'Uttarakhand', '06': 'Haryana',
            '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
            '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
            '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram',
            '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam',
            '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha',
            '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
            '25': 'Daman and Diu', '26': 'Dadra and Nagar Haveli',
            '27': 'Maharashtra', '28': 'Andhra Pradesh', '29': 'Karnataka',
            '30': 'Goa', '31': 'Lakshadweep', '32': 'Kerala',
            '33': 'Tamil Nadu', '34': 'Puducherry', '35': 'Andaman and Nicobar',
            '36': 'Telangana', '37': 'Andhra Pradesh'
        }
        
        logger.info("Indian data validator initialized")
    
    def validate_aadhaar(self, aadhaar: str) -> Tuple[bool, str]:
        """Validate Aadhaar number format and checksum"""
        try:
            # Remove spaces and check length
            clean_aadhaar = re.sub(r'\s+', '', str(aadhaar))
            
            if not re.match(self.patterns['aadhaar'], aadhaar):
                return False, "Invalid Aadhaar format"
            
            # Basic checksum validation (simplified)
            if len(clean_aadhaar) != 12:
                return False, "Aadhaar must be 12 digits"
            
            # Check if all digits are same (invalid)
            if len(set(clean_aadhaar)) == 1:
                return False, "Invalid Aadhaar - all digits same"
            
            # Verhoeff algorithm for checksum (simplified version)
            if self.verhoeff_checksum(clean_aadhaar):
                return True, "Valid Aadhaar format"
            else:
                return False, "Invalid Aadhaar checksum"
                
        except Exception as e:
            return False, f"Aadhaar validation error: {str(e)}"
    
    def verhoeff_checksum(self, number: str) -> bool:
        """Simplified Verhoeff algorithm for Aadhaar validation"""
        try:
            # This is a simplified version - production would use full algorithm
            digits = [int(d) for d in number]
            checksum = sum(digits) % 10
            return checksum == 0 or checksum == 5  # Simplified check
        except:
            return False
    
    def validate_pan(self, pan: str) -> Tuple[bool, str]:
        """Validate PAN card format"""
        try:
            pan_upper = str(pan).upper().strip()
            
            if not re.match(self.patterns['pan'], pan_upper):
                return False, "Invalid PAN format (should be ABCDE1234F)"
            
            # Check structure: 5 letters + 4 digits + 1 letter
            if len(pan_upper) != 10:
                return False, "PAN must be 10 characters"
            
            # 4th character should be 'P' for individual
            fourth_char = pan_upper[3]
            if fourth_char not in ['P', 'C', 'H', 'F', 'A', 'T', 'B', 'L', 'J', 'G']:
                return False, "Invalid PAN category code"
            
            return True, "Valid PAN format"
            
        except Exception as e:
            return False, f"PAN validation error: {str(e)}"
    
    def validate_upi_id(self, upi_id: str) -> Tuple[bool, str]:
        """Validate UPI ID format"""
        try:
            upi_lower = str(upi_id).lower().strip()
            
            if not re.match(self.patterns['upi_id'], upi_lower):
                return False, "Invalid UPI ID format"
            
            # Check for common UPI providers
            valid_providers = [
                'paytm', 'phonepe', 'gpay', 'amazonpay', 'mobikwik',
                'freecharge', 'airtel', 'jio', 'sbi', 'hdfc', 'icici',
                'axis', 'kotak', 'ybl', 'ibl', 'upi'
            ]
            
            provider = upi_lower.split('@')[1]
            if not any(vp in provider for vp in valid_providers):
                return False, f"Unrecognized UPI provider: {provider}"
            
            return True, "Valid UPI ID format"
            
        except Exception as e:
            return False, f"UPI validation error: {str(e)}"
    
    def validate_indian_mobile(self, mobile: str) -> Tuple[bool, str]:
        """Validate Indian mobile number"""
        try:
            # Clean the number
            clean_mobile = re.sub(r'[\s\-\(\)]', '', str(mobile))
            
            # Parse using phonenumbers library
            try:
                parsed_number = phonenumbers.parse(clean_mobile, 'IN')
                if phonenumbers.is_valid_number(parsed_number):
                    formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                    return True, f"Valid mobile number: {formatted}"
                else:
                    return False, "Invalid mobile number for India"
            except NumberParseException:
                # Fallback to regex
                if re.match(self.patterns['indian_mobile'], clean_mobile):
                    return True, "Valid mobile format (regex check)"
                else:
                    return False, "Invalid Indian mobile number format"
                    
        except Exception as e:
            return False, f"Mobile validation error: {str(e)}"
    
    def validate_ifsc(self, ifsc: str) -> Tuple[bool, str]:
        """Validate IFSC code"""
        try:
            ifsc_upper = str(ifsc).upper().strip()
            
            if not re.match(self.patterns['ifsc'], ifsc_upper):
                return False, "Invalid IFSC format (should be ABCD0123456)"
            
            # Check if it's a known bank code (simplified check)
            bank_codes = [
                'SBIN', 'HDFC', 'ICIC', 'AXIS', 'KOTAK', 'INDB', 'PUNB',
                'UBIN', 'CNRB', 'ANDB', 'BKID', 'MAHB', 'ALLA', 'CBIN'
            ]
            
            bank_code = ifsc_upper[:4]
            if bank_code in bank_codes:
                return True, f"Valid IFSC for {bank_code} bank"
            else:
                return True, f"Valid IFSC format (bank code: {bank_code})"
                
        except Exception as e:
            return False, f"IFSC validation error: {str(e)}"
    
    def validate_gstin(self, gstin: str) -> Tuple[bool, str]:
        """Validate GSTIN format"""
        try:
            gstin_upper = str(gstin).upper().strip()
            
            if not re.match(self.patterns['gstin'], gstin_upper):
                return False, "Invalid GSTIN format"
            
            # Extract state code and validate
            state_code = gstin_upper[:2]
            if state_code in self.state_codes:
                state_name = self.state_codes[state_code]
                return True, f"Valid GSTIN for {state_name}"
            else:
                return False, f"Invalid state code in GSTIN: {state_code}"
                
        except Exception as e:
            return False, f"GSTIN validation error: {str(e)}"

class DataQualityTestSuite:
    """
    Comprehensive data quality testing suite for Indian companies
    """
    
    def __init__(self, database_url: str = "sqlite:///data_quality.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        self.indian_validator = IndianDataValidator()
        self.ge_context = ge.get_context()
        
        # Quality thresholds for different check types
        self.thresholds = {
            QualityCheckType.COMPLETENESS: 0.95,  # 95% non-null
            QualityCheckType.ACCURACY: 0.90,      # 90% accurate
            QualityCheckType.CONSISTENCY: 0.98,   # 98% consistent
            QualityCheckType.VALIDITY: 0.85,      # 85% valid format
            QualityCheckType.UNIQUENESS: 0.99,    # 99% unique where expected
            QualityCheckType.TIMELINESS: 0.95     # 95% within SLA
        }
        
        logger.info("Data quality test suite initialized")
    
    def run_completeness_checks(self, df: pd.DataFrame, dataset_name: str) -> List[QualityCheckResult]:
        """Check data completeness"""
        results = []
        
        try:
            for column in df.columns:
                null_count = df[column].isnull().sum()
                total_count = len(df)
                completeness_score = (total_count - null_count) / total_count if total_count > 0 else 0
                
                passed = completeness_score >= self.thresholds[QualityCheckType.COMPLETENESS]
                severity = SeverityLevel.CRITICAL if completeness_score < 0.5 else SeverityLevel.HIGH if completeness_score < 0.8 else SeverityLevel.LOW
                
                result = QualityCheckResult(
                    check_id=str(uuid.uuid4()),
                    check_name=f"completeness_{column}",
                    check_type=QualityCheckType.COMPLETENESS,
                    dataset_name=dataset_name,
                    passed=passed,
                    score=completeness_score,
                    threshold=self.thresholds[QualityCheckType.COMPLETENESS],
                    severity=severity,
                    message=f"Column {column}: {completeness_score:.2%} complete",
                    details={
                        'column': column,
                        'null_count': int(null_count),
                        'total_count': int(total_count),
                        'null_percentage': float(null_count / total_count * 100) if total_count > 0 else 0
                    },
                    execution_time=datetime.now(),
                    affected_rows=int(null_count),
                    cost_impact_inr=self.calculate_cost_impact(null_count, total_count)
                )
                
                results.append(result)
                self.save_result(result)
                
        except Exception as e:
            logger.error(f"Completeness check failed: {e}")
        
        return results
    
    def run_indian_validity_checks(self, df: pd.DataFrame, dataset_name: str) -> List[QualityCheckResult]:
        """Check validity of Indian data formats"""
        results = []
        
        try:
            # Aadhaar validation
            if 'aadhaar' in df.columns or 'aadhaar_number' in df.columns:
                aadhaar_col = 'aadhaar' if 'aadhaar' in df.columns else 'aadhaar_number'
                results.extend(self._validate_column_format(
                    df, aadhaar_col, dataset_name, 'aadhaar', self.indian_validator.validate_aadhaar
                ))
            
            # PAN validation
            if 'pan' in df.columns or 'pan_number' in df.columns:
                pan_col = 'pan' if 'pan' in df.columns else 'pan_number'
                results.extend(self._validate_column_format(
                    df, pan_col, dataset_name, 'pan', self.indian_validator.validate_pan
                ))
            
            # UPI ID validation
            if 'upi_id' in df.columns or 'upi' in df.columns:
                upi_col = 'upi_id' if 'upi_id' in df.columns else 'upi'
                results.extend(self._validate_column_format(
                    df, upi_col, dataset_name, 'upi', self.indian_validator.validate_upi_id
                ))
            
            # Mobile number validation
            mobile_cols = [col for col in df.columns if 'mobile' in col.lower() or 'phone' in col.lower()]
            for mobile_col in mobile_cols:
                results.extend(self._validate_column_format(
                    df, mobile_col, dataset_name, 'mobile', self.indian_validator.validate_indian_mobile
                ))
            
            # IFSC validation
            if 'ifsc' in df.columns or 'ifsc_code' in df.columns:
                ifsc_col = 'ifsc' if 'ifsc' in df.columns else 'ifsc_code'
                results.extend(self._validate_column_format(
                    df, ifsc_col, dataset_name, 'ifsc', self.indian_validator.validate_ifsc
                ))
            
            # GSTIN validation
            if 'gstin' in df.columns or 'gst_number' in df.columns:
                gstin_col = 'gstin' if 'gstin' in df.columns else 'gst_number'
                results.extend(self._validate_column_format(
                    df, gstin_col, dataset_name, 'gstin', self.indian_validator.validate_gstin
                ))
                
        except Exception as e:
            logger.error(f"Indian validity check failed: {e}")
        
        return results
    
    def _validate_column_format(self, df: pd.DataFrame, column: str, dataset_name: str, 
                               format_type: str, validator_func) -> List[QualityCheckResult]:
        """Helper method to validate column format"""
        results = []
        
        try:
            if column not in df.columns:
                return results
            
            valid_count = 0
            invalid_rows = []
            total_count = df[column].notna().sum()  # Only count non-null values
            
            for idx, value in df[column].dropna().items():
                is_valid, message = validator_func(value)
                if is_valid:
                    valid_count += 1
                else:
                    invalid_rows.append({'index': int(idx), 'value': str(value), 'error': message})
            
            validity_score = valid_count / total_count if total_count > 0 else 0
            passed = validity_score >= self.thresholds[QualityCheckType.VALIDITY]
            
            severity = SeverityLevel.CRITICAL if validity_score < 0.5 else SeverityLevel.HIGH if validity_score < 0.8 else SeverityLevel.LOW
            
            result = QualityCheckResult(
                check_id=str(uuid.uuid4()),
                check_name=f"validity_{format_type}_{column}",
                check_type=QualityCheckType.VALIDITY,
                dataset_name=dataset_name,
                passed=passed,
                score=validity_score,
                threshold=self.thresholds[QualityCheckType.VALIDITY],
                severity=severity,
                message=f"{format_type.upper()} validation for {column}: {validity_score:.2%} valid",
                details={
                    'column': column,
                    'format_type': format_type,
                    'valid_count': int(valid_count),
                    'total_count': int(total_count),
                    'invalid_rows': invalid_rows[:10],  # Limit to first 10 for storage
                    'invalid_percentage': float((total_count - valid_count) / total_count * 100) if total_count > 0 else 0
                },
                execution_time=datetime.now(),
                affected_rows=int(total_count - valid_count),
                cost_impact_inr=self.calculate_cost_impact(total_count - valid_count, total_count)
            )
            
            results.append(result)
            self.save_result(result)
            
        except Exception as e:
            logger.error(f"Format validation failed for {column}: {e}")
        
        return results
    
    def run_business_logic_checks(self, df: pd.DataFrame, dataset_name: str, 
                                 business_rules: Dict[str, Any] = None) -> List[QualityCheckResult]:
        """Run business logic validation specific to Indian companies"""
        results = []
        
        try:
            if business_rules is None:
                business_rules = self.get_default_indian_business_rules()
            
            # Age validation for Indian context
            if 'age' in df.columns:
                results.extend(self._validate_age_range(df, dataset_name))
            
            # Transaction amount validation
            if 'amount' in df.columns or 'transaction_amount' in df.columns:
                amount_col = 'amount' if 'amount' in df.columns else 'transaction_amount'
                results.extend(self._validate_transaction_amounts(df, amount_col, dataset_name))
            
            # Date validation for Indian holidays and working days
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            for date_col in date_cols:
                results.extend(self._validate_business_dates(df, date_col, dataset_name))
            
            # State and city validation
            if 'state' in df.columns:
                results.extend(self._validate_indian_states(df, dataset_name))
            
        except Exception as e:
            logger.error(f"Business logic check failed: {e}")
        
        return results
    
    def _validate_age_range(self, df: pd.DataFrame, dataset_name: str) -> List[QualityCheckResult]:
        """Validate age ranges for Indian context"""
        results = []
        
        try:
            if 'age' not in df.columns:
                return results
            
            # Define reasonable age ranges for different contexts
            min_age = 0
            max_age = 120
            
            # For financial services, minimum age might be 18
            if 'bank' in dataset_name.lower() or 'loan' in dataset_name.lower():
                min_age = 18
            
            invalid_ages = df[(df['age'] < min_age) | (df['age'] > max_age)]
            total_count = df['age'].notna().sum()
            invalid_count = len(invalid_ages)
            
            accuracy_score = (total_count - invalid_count) / total_count if total_count > 0 else 0
            passed = accuracy_score >= self.thresholds[QualityCheckType.ACCURACY]
            
            result = QualityCheckResult(
                check_id=str(uuid.uuid4()),
                check_name="business_logic_age_range",
                check_type=QualityCheckType.ACCURACY,
                dataset_name=dataset_name,
                passed=passed,
                score=accuracy_score,
                threshold=self.thresholds[QualityCheckType.ACCURACY],
                severity=SeverityLevel.MEDIUM,
                message=f"Age range validation: {accuracy_score:.2%} within valid range ({min_age}-{max_age})",
                details={
                    'min_age': min_age,
                    'max_age': max_age,
                    'invalid_count': int(invalid_count),
                    'total_count': int(total_count),
                    'invalid_ages': invalid_ages['age'].tolist()[:10]
                },
                execution_time=datetime.now(),
                affected_rows=int(invalid_count)
            )
            
            results.append(result)
            self.save_result(result)
            
        except Exception as e:
            logger.error(f"Age validation failed: {e}")
        
        return results
    
    def _validate_transaction_amounts(self, df: pd.DataFrame, amount_col: str, dataset_name: str) -> List[QualityCheckResult]:
        """Validate transaction amounts for Indian context"""
        results = []
        
        try:
            if amount_col not in df.columns:
                return results
            
            # Define reasonable amount ranges based on context
            min_amount = 0.01  # 1 paisa
            max_amount = 1000000  # 10 lakh INR for regular transactions
            
            # UPI transaction limits
            if 'upi' in dataset_name.lower():
                max_amount = 100000  # 1 lakh UPI limit
            
            # Large value transaction limits
            if 'rtgs' in dataset_name.lower():
                min_amount = 200000  # 2 lakh minimum for RTGS
            
            invalid_amounts = df[(df[amount_col] < min_amount) | (df[amount_col] > max_amount)]
            total_count = df[amount_col].notna().sum()
            invalid_count = len(invalid_amounts)
            
            accuracy_score = (total_count - invalid_count) / total_count if total_count > 0 else 0
            passed = accuracy_score >= self.thresholds[QualityCheckType.ACCURACY]
            
            result = QualityCheckResult(
                check_id=str(uuid.uuid4()),
                check_name=f"business_logic_amount_range_{amount_col}",
                check_type=QualityCheckType.ACCURACY,
                dataset_name=dataset_name,
                passed=passed,
                score=accuracy_score,
                threshold=self.thresholds[QualityCheckType.ACCURACY],
                severity=SeverityLevel.HIGH,
                message=f"Amount range validation: {accuracy_score:.2%} within valid range (₹{min_amount:,.2f}-₹{max_amount:,.2f})",
                details={
                    'min_amount': min_amount,
                    'max_amount': max_amount,
                    'invalid_count': int(invalid_count),
                    'total_count': int(total_count),
                    'amount_stats': {
                        'mean': float(df[amount_col].mean()),
                        'median': float(df[amount_col].median()),
                        'std': float(df[amount_col].std())
                    }
                },
                execution_time=datetime.now(),
                affected_rows=int(invalid_count)
            )
            
            results.append(result)
            self.save_result(result)
            
        except Exception as e:
            logger.error(f"Amount validation failed: {e}")
        
        return results
    
    def _validate_business_dates(self, df: pd.DataFrame, date_col: str, dataset_name: str) -> List[QualityCheckResult]:
        """Validate business dates against Indian calendar"""
        results = []
        
        try:
            if date_col not in df.columns:
                return results
            
            # Convert to datetime if not already
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Check for future dates (should not exist for completed transactions)
            future_dates = df[df[date_col] > datetime.now()]
            
            # Check for very old dates (more than 10 years old)
            old_threshold = datetime.now() - timedelta(days=365*10)
            very_old_dates = df[df[date_col] < old_threshold]
            
            total_count = df[date_col].notna().sum()
            invalid_count = len(future_dates) + len(very_old_dates)
            
            timeliness_score = (total_count - invalid_count) / total_count if total_count > 0 else 0
            passed = timeliness_score >= self.thresholds[QualityCheckType.TIMELINESS]
            
            result = QualityCheckResult(
                check_id=str(uuid.uuid4()),
                check_name=f"business_logic_date_range_{date_col}",
                check_type=QualityCheckType.TIMELINESS,
                dataset_name=dataset_name,
                passed=passed,
                score=timeliness_score,
                threshold=self.thresholds[QualityCheckType.TIMELINESS],
                severity=SeverityLevel.MEDIUM,
                message=f"Date range validation: {timeliness_score:.2%} within reasonable timeframe",
                details={
                    'future_dates_count': len(future_dates),
                    'very_old_dates_count': len(very_old_dates),
                    'total_count': int(total_count),
                    'date_range': {
                        'min_date': str(df[date_col].min()),
                        'max_date': str(df[date_col].max())
                    }
                },
                execution_time=datetime.now(),
                affected_rows=int(invalid_count)
            )
            
            results.append(result)
            self.save_result(result)
            
        except Exception as e:
            logger.error(f"Date validation failed: {e}")
        
        return results
    
    def _validate_indian_states(self, df: pd.DataFrame, dataset_name: str) -> List[QualityCheckResult]:
        """Validate Indian state names"""
        results = []
        
        try:
            if 'state' not in df.columns:
                return results
            
            valid_states = list(self.indian_validator.state_codes.values()) + [
                'Andaman and Nicobar Islands', 'Delhi', 'Jammu & Kashmir',
                'Ladakh', 'Lakshadweep', 'Puducherry'
            ]
            
            # Also include common abbreviations
            state_abbreviations = {
                'MH': 'Maharashtra', 'KA': 'Karnataka', 'TN': 'Tamil Nadu',
                'UP': 'Uttar Pradesh', 'WB': 'West Bengal', 'RJ': 'Rajasthan',
                'GJ': 'Gujarat', 'MP': 'Madhya Pradesh', 'AP': 'Andhra Pradesh',
                'TS': 'Telangana', 'KL': 'Kerala', 'OR': 'Odisha',
                'PB': 'Punjab', 'HR': 'Haryana', 'JH': 'Jharkhand',
                'CG': 'Chhattisgarh', 'AS': 'Assam', 'HP': 'Himachal Pradesh'
            }
            
            valid_states.extend(state_abbreviations.keys())
            
            invalid_states = df[~df['state'].str.strip().isin(valid_states)]
            total_count = df['state'].notna().sum()
            invalid_count = len(invalid_states)
            
            validity_score = (total_count - invalid_count) / total_count if total_count > 0 else 0
            passed = validity_score >= self.thresholds[QualityCheckType.VALIDITY]
            
            result = QualityCheckResult(
                check_id=str(uuid.uuid4()),
                check_name="business_logic_indian_states",
                check_type=QualityCheckType.VALIDITY,
                dataset_name=dataset_name,
                passed=passed,
                score=validity_score,
                threshold=self.thresholds[QualityCheckType.VALIDITY],
                severity=SeverityLevel.MEDIUM,
                message=f"Indian state validation: {validity_score:.2%} valid states",
                details={
                    'invalid_count': int(invalid_count),
                    'total_count': int(total_count),
                    'invalid_states': invalid_states['state'].unique().tolist()[:10]
                },
                execution_time=datetime.now(),
                affected_rows=int(invalid_count)
            )
            
            results.append(result)
            self.save_result(result)
            
        except Exception as e:
            logger.error(f"State validation failed: {e}")
        
        return results
    
    def calculate_cost_impact(self, affected_rows: int, total_rows: int) -> float:
        """Calculate cost impact of data quality issues in INR"""
        try:
            # Cost factors for Indian companies
            cost_per_bad_record = 10  # INR per bad record
            processing_cost_multiplier = 1.5  # 50% extra processing cost
            
            # Base cost impact
            direct_cost = affected_rows * cost_per_bad_record
            
            # Processing overhead
            overhead_cost = (affected_rows / total_rows) * total_rows * 0.5 if total_rows > 0 else 0
            
            total_cost = direct_cost + overhead_cost
            
            return round(total_cost, 2)
            
        except Exception as e:
            logger.error(f"Cost calculation failed: {e}")
            return 0.0
    
    def get_default_indian_business_rules(self) -> Dict[str, Any]:
        """Get default business rules for Indian companies"""
        return {
            'age_range': {'min': 0, 'max': 120},
            'transaction_limits': {
                'upi': {'min': 0.01, 'max': 100000},
                'neft': {'min': 1, 'max': 1000000},
                'rtgs': {'min': 200000, 'max': 50000000},
                'imps': {'min': 1, 'max': 200000}
            },
            'working_hours': {'start': 9, 'end': 18},
            'valid_currencies': ['INR', 'USD', 'EUR'],
            'indian_states': list(self.indian_validator.state_codes.values())
        }
    
    def save_result(self, result: QualityCheckResult):
        """Save quality check result to database"""
        try:
            db_result = DataQualityCheck(
                id=str(uuid.uuid4()),
                check_id=result.check_id,
                check_name=result.check_name,
                check_type=result.check_type.value,
                dataset_name=result.dataset_name,
                passed=result.passed,
                score=result.score,
                threshold=result.threshold,
                severity=result.severity.value,
                message=result.message,
                details=result.details,
                execution_time=result.execution_time,
                affected_rows=result.affected_rows,
                cost_impact_inr=result.cost_impact_inr
            )
            
            self.session.add(db_result)
            self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to save result: {e}")
            self.session.rollback()
    
    def generate_quality_report(self, dataset_name: str, output_path: str = "/tmp/quality_report.html") -> str:
        """Generate comprehensive quality report"""
        try:
            # Get all results for dataset
            results = self.session.query(DataQualityCheck).filter_by(dataset_name=dataset_name).all()
            
            if not results:
                logger.warning(f"No quality results found for dataset: {dataset_name}")
                return ""
            
            # Calculate summary statistics
            total_checks = len(results)
            passed_checks = len([r for r in results if r.passed])
            failed_checks = total_checks - passed_checks
            overall_score = passed_checks / total_checks if total_checks > 0 else 0
            
            total_cost_impact = sum(r.cost_impact_inr for r in results)
            
            # Group results by check type
            results_by_type = {}
            for result in results:
                check_type = result.check_type
                if check_type not in results_by_type:
                    results_by_type[check_type] = []
                results_by_type[check_type].append(result)
            
            # Generate HTML report
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Data Quality Report - {dataset_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .metric {{ text-align: center; }}
                    .metric h3 {{ margin: 0; color: #333; }}
                    .metric p {{ font-size: 24px; font-weight: bold; margin: 5px 0; }}
                    .passed {{ color: #28a745; }}
                    .failed {{ color: #dc3545; }}
                    .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    .table th {{ background-color: #f2f2f2; }}
                    .severity-critical {{ background-color: #f8d7da; }}
                    .severity-high {{ background-color: #fef9e7; }}
                    .severity-medium {{ background-color: #e2f3ff; }}
                    .severity-low {{ background-color: #d4edda; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Data Quality Report</h1>
                    <h2>Dataset: {dataset_name}</h2>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="summary">
                    <div class="metric">
                        <h3>Overall Score</h3>
                        <p class="{'passed' if overall_score >= 0.8 else 'failed'}">{overall_score:.1%}</p>
                    </div>
                    <div class="metric">
                        <h3>Total Checks</h3>
                        <p>{total_checks}</p>
                    </div>
                    <div class="metric">
                        <h3>Passed</h3>
                        <p class="passed">{passed_checks}</p>
                    </div>
                    <div class="metric">
                        <h3>Failed</h3>
                        <p class="failed">{failed_checks}</p>
                    </div>
                    <div class="metric">
                        <h3>Cost Impact</h3>
                        <p>₹{total_cost_impact:,.2f}</p>
                    </div>
                </div>
                
                <h3>Detailed Results</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Check Name</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Score</th>
                            <th>Severity</th>
                            <th>Affected Rows</th>
                            <th>Cost Impact (₹)</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for result in results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                html_content += f"""
                        <tr class="severity-{result.severity}">
                            <td>{result.check_name}</td>
                            <td>{result.check_type}</td>
                            <td>{status}</td>
                            <td>{result.score:.2%}</td>
                            <td>{result.severity.upper()}</td>
                            <td>{result.affected_rows}</td>
                            <td>₹{result.cost_impact_inr:,.2f}</td>
                            <td>{result.message}</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
                
                <h3>Recommendations</h3>
                <ul>
            """
            
            # Add recommendations based on failed checks
            if failed_checks > 0:
                html_content += "<li>Address failed quality checks to improve data reliability</li>"
            
            if total_cost_impact > 1000:
                html_content += f"<li>High cost impact detected (₹{total_cost_impact:,.2f}) - prioritize data quality improvements</li>"
            
            critical_issues = [r for r in results if r.severity == 'critical' and not r.passed]
            if critical_issues:
                html_content += f"<li>Critical issues found ({len(critical_issues)}) - immediate attention required</li>"
            
            html_content += """
                </ul>
            </body>
            </html>
            """
            
            # Save report
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Quality report saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return ""

def main():
    """Demonstrate automated data quality testing for Indian companies"""
    
    print("🔍 Starting Automated Data Quality Testing Demo")
    print("=" * 60)
    
    # Initialize test suite
    test_suite = DataQualityTestSuite()
    
    # Create sample Indian data for testing
    print("\n📊 Creating sample Indian e-commerce data...")
    
    sample_data = pd.DataFrame({
        'customer_id': ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005'],
        'aadhaar': ['1234 5678 9012', '9876 5432 1098', '1111 2222 3333', 'invalid_aadhaar', '5555 6666 7777'],
        'pan': ['ABCDE1234F', 'FGHIJ5678K', 'INVALID_PAN', 'LMNOP9012Q', ''],
        'upi_id': ['customer1@paytm', 'user2@phonepe', 'invalid_upi', 'customer4@gpay', 'user5@ybl'],
        'mobile': ['+91 98765 43210', '9876543210', '1234567890', '+91 87654 32109', '98765432101'],
        'ifsc': ['SBIN0001234', 'HDFC0002345', 'INVALID_IFSC', 'ICIC0003456', 'AXIS0004567'],
        'amount': [50000, 25000, 1500000, -1000, 75000],  # Mix of valid and invalid amounts
        'age': [25, 30, 150, 15, 35],  # Mix of valid and invalid ages
        'state': ['Maharashtra', 'Karnataka', 'Invalid State', 'Tamil Nadu', 'MH'],
        'transaction_date': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=5),
            datetime.now() + timedelta(days=1),  # Future date (invalid)
            datetime.now() - timedelta(days=365*15),  # Very old date
            datetime.now() - timedelta(hours=2)
        ]
    })
    
    dataset_name = "sample_ecommerce_data"
    
    # Run completeness checks
    print("\n🔍 Running completeness checks...")
    completeness_results = test_suite.run_completeness_checks(sample_data, dataset_name)
    
    print(f"   Completeness checks: {len(completeness_results)} executed")
    
    # Run Indian format validation checks
    print("\n🇮🇳 Running Indian format validation...")
    validity_results = test_suite.run_indian_validity_checks(sample_data, dataset_name)
    
    print(f"   Format validation checks: {len(validity_results)} executed")
    
    # Run business logic checks
    print("\n💼 Running business logic validation...")
    business_results = test_suite.run_business_logic_checks(sample_data, dataset_name)
    
    print(f"   Business logic checks: {len(business_results)} executed")
    
    # Generate quality report
    print("\n📋 Generating quality report...")
    report_path = test_suite.generate_quality_report(dataset_name, "/tmp/indian_data_quality_report.html")
    
    if report_path:
        print(f"   Report saved to: {report_path}")
    
    # Summary statistics
    all_results = completeness_results + validity_results + business_results
    total_checks = len(all_results)
    passed_checks = len([r for r in all_results if r.passed])
    failed_checks = total_checks - passed_checks
    total_cost_impact = sum(r.cost_impact_inr for r in all_results)
    
    print(f"\n📊 Quality Testing Summary:")
    print(f"   Total checks executed: {total_checks}")
    print(f"   Checks passed: {passed_checks}")
    print(f"   Checks failed: {failed_checks}")
    print(f"   Overall success rate: {passed_checks/total_checks:.1%}")
    print(f"   Total cost impact: ₹{total_cost_impact:,.2f}")
    
    # Print sample failed checks for demonstration
    failed_results = [r for r in all_results if not r.passed]
    if failed_results:
        print(f"\n❌ Sample Failed Checks:")
        for result in failed_results[:3]:  # Show first 3 failures
            print(f"   • {result.check_name}: {result.message}")
            print(f"     Severity: {result.severity.value.upper()}, Affected rows: {result.affected_rows}")
    
    print("\n✅ Automated data quality testing completed!")
    print("\n📝 Features demonstrated:")
    print("   ✓ Indian format validation (Aadhaar, PAN, UPI, Mobile)")
    print("   ✓ Business logic validation")
    print("   ✓ Completeness and accuracy checks")
    print("   ✓ Cost impact calculation in INR")
    print("   ✓ Severity-based issue classification")
    print("   ✓ Comprehensive HTML reporting")
    print("   ✓ Database storage for historical tracking")

if __name__ == "__main__":
    main()