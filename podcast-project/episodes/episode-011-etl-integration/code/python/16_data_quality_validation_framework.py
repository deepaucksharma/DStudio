#!/usr/bin/env python3
"""
Comprehensive Data Quality Validation Framework - Episode 11
Production-grade data quality framework with ML-based anomaly detection and compliance

यह comprehensive data quality framework दिखाता है:
- Rule-based validation (Great Expectations style)
- ML-based anomaly detection
- Data profiling and drift detection
- Compliance reporting (GDPR, PCI-DSS)
- Auto-healing data corrections

Indian Context: Banking data quality जैसे strict compliance और Aadhaar validation patterns
"""

import pandas as pd
import numpy as np
import json
import logging
import uuid
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import sqlite3
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import joblib
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Configure logging for Hindi comments
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_quality.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SeverityLevel(Enum):
    """Severity levels for data quality issues"""
    LOW = "low"           # Warning level - can proceed
    MEDIUM = "medium"     # Caution - needs attention
    HIGH = "high"         # Error - should not proceed
    CRITICAL = "critical" # Blocker - must fix immediately

class ComplianceType(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"         # European data protection
    PCI_DSS = "pci_dss"   # Payment card industry
    HIPAA = "hipaa"       # Healthcare data
    SOX = "sox"           # Financial reporting
    PDP = "pdp"           # Personal Data Protection (India)
    RBI = "rbi"           # Reserve Bank of India

@dataclass
class DataQualityIssue:
    """Data quality issue information"""
    issue_id: str
    rule_name: str
    severity: SeverityLevel
    message: str
    affected_records: int
    affected_columns: List[str]
    sample_values: List[Any]
    suggested_fix: str
    compliance_impact: List[ComplianceType]
    detected_at: datetime
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of data validation"""
    dataset_id: str
    total_records: int
    total_columns: int
    passed_checks: int
    failed_checks: int
    issues: List[DataQualityIssue]
    quality_score: float
    compliance_status: Dict[ComplianceType, bool]
    processing_time: float
    recommendations: List[str]
    
    @property
    def is_valid(self) -> bool:
        """Check if dataset passes quality threshold"""
        return self.quality_score >= 0.8 and not any(
            issue.severity == SeverityLevel.CRITICAL for issue in self.issues
        )

class IndianDataValidator:
    """
    Indian-specific data validators
    भारतीय context के लिए specific validation rules
    """
    
    @staticmethod
    def validate_aadhaar(aadhaar: str) -> Tuple[bool, str]:
        """Validate Aadhaar number format and checksum"""
        if pd.isna(aadhaar) or not str(aadhaar).strip():
            return False, "Empty Aadhaar number"
        
        aadhaar_clean = re.sub(r'\D', '', str(aadhaar))
        
        if len(aadhaar_clean) != 12:
            return False, f"Aadhaar must be 12 digits, got {len(aadhaar_clean)}"
        
        # Verhoeff algorithm for Aadhaar checksum
        multiplication_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        ]
        
        permutation_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]
        
        checksum = 0
        for i, digit in enumerate(reversed(aadhaar_clean)):
            checksum = multiplication_table[checksum][permutation_table[i % 8][int(digit)]]
        
        is_valid = checksum == 0
        return is_valid, "Valid Aadhaar" if is_valid else "Invalid Aadhaar checksum"
    
    @staticmethod
    def validate_pan(pan: str) -> Tuple[bool, str]:
        """Validate PAN (Permanent Account Number) format"""
        if pd.isna(pan) or not str(pan).strip():
            return False, "Empty PAN number"
        
        pan_clean = str(pan).upper().strip()
        
        # PAN format: AAAPL1234C (5 letters, 4 digits, 1 letter)
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        if not re.match(pan_pattern, pan_clean):
            return False, "Invalid PAN format. Should be AAAPL1234C"
        
        return True, "Valid PAN"
    
    @staticmethod
    def validate_indian_mobile(mobile: str) -> Tuple[bool, str]:
        """Validate Indian mobile number"""
        if pd.isna(mobile) or not str(mobile).strip():
            return False, "Empty mobile number"
        
        try:
            # Parse with Indian country code
            phone_number = phonenumbers.parse(str(mobile), "IN")
            
            if not phonenumbers.is_valid_number(phone_number):
                return False, "Invalid mobile number format"
            
            # Check if it's a mobile number (not landline)
            if phonenumbers.number_type(phone_number) != phonenumbers.PhoneNumberType.MOBILE:
                return False, "Not a mobile number"
            
            return True, "Valid Indian mobile number"
            
        except phonenumbers.NumberParseException:
            return False, "Failed to parse mobile number"
    
    @staticmethod
    def validate_ifsc_code(ifsc: str) -> Tuple[bool, str]:
        """Validate IFSC (Indian Financial System Code)"""
        if pd.isna(ifsc) or not str(ifsc).strip():
            return False, "Empty IFSC code"
        
        ifsc_clean = str(ifsc).upper().strip()
        
        # IFSC format: ABCD0123456 (4 letters, 1 zero, 6 characters)
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        
        if not re.match(ifsc_pattern, ifsc_clean):
            return False, "Invalid IFSC format. Should be ABCD0123456"
        
        # List of valid bank codes (first 4 characters)
        valid_bank_codes = {
            'SBIN', 'HDFC', 'ICIC', 'AXIS', 'KOTAK', 'PUNB', 'UBIN', 'CANB',
            'KKBK', 'IDIB', 'IBKL', 'ALLA', 'CBIN', 'YESB', 'SCBL', 'UTIB'
        }
        
        bank_code = ifsc_clean[:4]
        if bank_code not in valid_bank_codes:
            return False, f"Unknown bank code: {bank_code}"
        
        return True, "Valid IFSC code"
    
    @staticmethod
    def validate_gst_number(gst: str) -> Tuple[bool, str]:
        """Validate GST (Goods and Services Tax) number"""
        if pd.isna(gst) or not str(gst).strip():
            return False, "Empty GST number"
        
        gst_clean = str(gst).upper().strip()
        
        # GST format: 15 characters (2 state code + 10 PAN + 1 entity + 1 Z + 1 checksum)
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
        
        if not re.match(gst_pattern, gst_clean):
            return False, "Invalid GST format"
        
        # Validate PAN part (positions 2-11)
        pan_part = gst_clean[2:12]
        is_pan_valid, _ = IndianDataValidator.validate_pan(pan_part)
        
        if not is_pan_valid:
            return False, "Invalid PAN in GST number"
        
        return True, "Valid GST number"

class MLAnomalyDetector:
    """
    Machine Learning based anomaly detection for data quality
    ML algorithms से unusual patterns detect करते हैं
    """
    
    def __init__(self, contamination_rate: float = 0.1):
        self.contamination_rate = contamination_rate
        self.isolation_forest = IsolationForest(
            contamination=contamination_rate,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train_on_clean_data(self, clean_data: pd.DataFrame):
        """Train anomaly detector on known clean data"""
        # Select numeric columns for training
        numeric_cols = clean_data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            logger.warning("No numeric columns found for anomaly detection training")
            return
        
        training_data = clean_data[numeric_cols].fillna(clean_data[numeric_cols].median())
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(training_data)
        
        # Train isolation forest
        self.isolation_forest.fit(scaled_data)
        self.is_trained = True
        
        logger.info(f"Anomaly detector trained on {len(training_data)} records with {len(numeric_cols)} features")
    
    def detect_anomalies(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies in new data"""
        if not self.is_trained:
            raise ValueError("Anomaly detector not trained. Call train_on_clean_data first.")
        
        # Select same numeric columns used for training
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        test_data = data[numeric_cols].fillna(data[numeric_cols].median())
        
        # Scale the data
        scaled_data = self.scaler.transform(test_data)
        
        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.isolation_forest.predict(scaled_data)
        
        # Get anomaly scores (lower scores indicate more anomalous)
        scores = self.isolation_forest.decision_function(scaled_data)
        
        return predictions, scores
    
    def detect_clustering_anomalies(self, data: pd.DataFrame, eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
        """Use DBSCAN clustering to detect outliers"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return np.array([])
        
        cluster_data = data[numeric_cols].fillna(data[numeric_cols].median())
        scaled_data = StandardScaler().fit_transform(cluster_data)
        
        # Apply DBSCAN clustering
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = dbscan.fit_predict(scaled_data)
        
        # Points with label -1 are considered outliers
        return cluster_labels == -1

class DataQualityFramework:
    """
    Comprehensive Data Quality Validation Framework
    Production-grade data quality validation जो सभी aspects cover करता है
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.indian_validator = IndianDataValidator()
        self.anomaly_detector = MLAnomalyDetector()
        
        # Initialize issue database
        self.db_path = config.get('database_path', 'data_quality.db')
        self._init_database()
        
        # Load validation rules
        self.validation_rules = self._load_validation_rules()
        
        # Performance thresholds
        self.quality_thresholds = {
            'completeness': 0.95,      # 95% complete data
            'accuracy': 0.98,          # 98% accurate data
            'consistency': 0.99,       # 99% consistent data
            'timeliness': 0.90,        # 90% timely data
            'validity': 0.97           # 97% valid format
        }
    
    def _init_database(self):
        """Initialize SQLite database for tracking issues"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_issues (
                issue_id TEXT PRIMARY KEY,
                dataset_id TEXT,
                rule_name TEXT,
                severity TEXT,
                message TEXT,
                affected_records INTEGER,
                detected_at TIMESTAMP,
                resolved_at TIMESTAMP,
                is_resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                metric_id TEXT PRIMARY KEY,
                dataset_id TEXT,
                metric_name TEXT,
                metric_value REAL,
                threshold_value REAL,
                is_passed BOOLEAN,
                measured_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_validation_rules(self) -> Dict[str, Dict]:
        """Load validation rules configuration"""
        return {
            'completeness_rules': {
                'required_fields': ['user_id', 'transaction_id', 'amount', 'timestamp'],
                'null_threshold': 0.05,  # Max 5% null values allowed
                'description': 'Check for missing required fields'
            },
            'format_rules': {
                'email_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'phone_pattern': r'^\+91[789]\d{9}$',
                'amount_range': [0, 1000000],  # ₹0 to ₹10 lakh
                'description': 'Validate data formats and ranges'
            },
            'business_rules': {
                'transaction_limits': {
                    'upi_limit': 100000,      # ₹1 lakh UPI limit
                    'card_limit': 200000,     # ₹2 lakh card limit
                    'wallet_limit': 10000     # ₹10k wallet limit
                },
                'working_hours': (6, 23),     # 6 AM to 11 PM
                'description': 'Business logic validation'
            },
            'compliance_rules': {
                'gdpr': {
                    'pii_fields': ['name', 'email', 'phone', 'address'],
                    'retention_days': 365,
                    'consent_required': True
                },
                'pci_dss': {
                    'card_fields': ['card_number', 'cvv', 'expiry'],
                    'encryption_required': True
                },
                'description': 'Compliance and regulatory checks'
            }
        }
    
    def validate_dataset(self, df: pd.DataFrame, dataset_id: str) -> ValidationResult:
        """
        Comprehensive validation of a dataset
        Complete data quality validation with all checks
        """
        logger.info(f"🔍 Starting comprehensive validation for dataset: {dataset_id}")
        start_time = time.time()
        
        issues = []
        passed_checks = 0
        total_checks = 0
        
        # 1. Completeness validation
        completeness_issues, completeness_passed, completeness_total = self._validate_completeness(df, dataset_id)
        issues.extend(completeness_issues)
        passed_checks += completeness_passed
        total_checks += completeness_total
        
        # 2. Format validation
        format_issues, format_passed, format_total = self._validate_formats(df, dataset_id)
        issues.extend(format_issues)
        passed_checks += format_passed
        total_checks += format_total
        
        # 3. Business rule validation
        business_issues, business_passed, business_total = self._validate_business_rules(df, dataset_id)
        issues.extend(business_issues)
        passed_checks += business_passed
        total_checks += business_total
        
        # 4. Anomaly detection
        if len(df) > 100:  # Only for larger datasets
            anomaly_issues = self._detect_anomalies(df, dataset_id)
            issues.extend(anomaly_issues)
            total_checks += 1
            if not anomaly_issues:
                passed_checks += 1
        
        # 5. Compliance validation
        compliance_issues, compliance_status = self._validate_compliance(df, dataset_id)
        issues.extend(compliance_issues)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(df, issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues)
        
        # Create validation result
        result = ValidationResult(
            dataset_id=dataset_id,
            total_records=len(df),
            total_columns=len(df.columns),
            passed_checks=passed_checks,
            failed_checks=total_checks - passed_checks,
            issues=issues,
            quality_score=quality_score,
            compliance_status=compliance_status,
            processing_time=time.time() - start_time,
            recommendations=recommendations
        )
        
        # Store results in database
        self._store_validation_results(result)
        
        logger.info(f"✅ Validation completed - Score: {quality_score:.2f}, Issues: {len(issues)}")
        return result
    
    def _validate_completeness(self, df: pd.DataFrame, dataset_id: str) -> Tuple[List[DataQualityIssue], int, int]:
        """Validate data completeness"""
        issues = []
        passed = 0
        total = 0
        
        # Check required fields
        required_fields = self.validation_rules['completeness_rules']['required_fields']
        for field in required_fields:
            total += 1
            if field in df.columns:
                null_count = df[field].isna().sum()
                null_percentage = null_count / len(df)
                
                if null_percentage > self.validation_rules['completeness_rules']['null_threshold']:
                    issues.append(DataQualityIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=f'completeness_{field}',
                        severity=SeverityLevel.HIGH if null_percentage > 0.1 else SeverityLevel.MEDIUM,
                        message=f"Field '{field}' has {null_percentage:.1%} missing values (threshold: 5%)",
                        affected_records=null_count,
                        affected_columns=[field],
                        sample_values=[],
                        suggested_fix=f"Fill missing values for {field} or update data source",
                        compliance_impact=[ComplianceType.GDPR] if field in ['email', 'phone'] else [],
                        detected_at=datetime.now(),
                        context={'null_percentage': null_percentage, 'threshold': 0.05}
                    ))
                else:
                    passed += 1
            else:
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name=f'missing_field_{field}',
                    severity=SeverityLevel.CRITICAL,
                    message=f"Required field '{field}' is missing from dataset",
                    affected_records=len(df),
                    affected_columns=[field],
                    sample_values=[],
                    suggested_fix=f"Add {field} column to dataset",
                    compliance_impact=[ComplianceType.PCI_DSS] if 'card' in field else [],
                    detected_at=datetime.now()
                ))
        
        # Check for completely empty rows
        total += 1
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            issues.append(DataQualityIssue(
                issue_id=str(uuid.uuid4()),
                rule_name='empty_rows',
                severity=SeverityLevel.MEDIUM,
                message=f"Dataset contains {empty_rows} completely empty rows",
                affected_records=empty_rows,
                affected_columns=list(df.columns),
                sample_values=[],
                suggested_fix="Remove empty rows from dataset",
                compliance_impact=[],
                detected_at=datetime.now()
            ))
        else:
            passed += 1
        
        return issues, passed, total
    
    def _validate_formats(self, df: pd.DataFrame, dataset_id: str) -> Tuple[List[DataQualityIssue], int, int]:
        """Validate data formats"""
        issues = []
        passed = 0
        total = 0
        
        # Email validation
        if 'email' in df.columns:
            total += 1
            invalid_emails = []
            
            for idx, email in df['email'].dropna().items():
                try:
                    validate_email(email)
                except EmailNotValidError:
                    invalid_emails.append((idx, email))
            
            if invalid_emails:
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name='invalid_email_format',
                    severity=SeverityLevel.HIGH,
                    message=f"Found {len(invalid_emails)} invalid email addresses",
                    affected_records=len(invalid_emails),
                    affected_columns=['email'],
                    sample_values=[email for _, email in invalid_emails[:5]],
                    suggested_fix="Validate and correct email formats",
                    compliance_impact=[ComplianceType.GDPR],
                    detected_at=datetime.now()
                ))
            else:
                passed += 1
        
        # Phone number validation (Indian)
        if 'phone' in df.columns:
            total += 1
            invalid_phones = []
            
            for idx, phone in df['phone'].dropna().items():
                is_valid, _ = self.indian_validator.validate_indian_mobile(phone)
                if not is_valid:
                    invalid_phones.append((idx, phone))
            
            if invalid_phones:
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name='invalid_phone_format',
                    severity=SeverityLevel.HIGH,
                    message=f"Found {len(invalid_phones)} invalid phone numbers",
                    affected_records=len(invalid_phones),
                    affected_columns=['phone'],
                    sample_values=[phone for _, phone in invalid_phones[:5]],
                    suggested_fix="Validate and correct phone number formats",
                    compliance_impact=[ComplianceType.PDP],
                    detected_at=datetime.now()
                ))
            else:
                passed += 1
        
        # Indian-specific validations
        indian_fields = {
            'aadhaar': self.indian_validator.validate_aadhaar,
            'pan': self.indian_validator.validate_pan,
            'ifsc': self.indian_validator.validate_ifsc_code,
            'gst': self.indian_validator.validate_gst_number
        }
        
        for field, validator in indian_fields.items():
            if field in df.columns:
                total += 1
                invalid_values = []
                
                for idx, value in df[field].dropna().items():
                    is_valid, _ = validator(value)
                    if not is_valid:
                        invalid_values.append((idx, value))
                
                if invalid_values:
                    issues.append(DataQualityIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name=f'invalid_{field}_format',
                        severity=SeverityLevel.HIGH,
                        message=f"Found {len(invalid_values)} invalid {field.upper()} values",
                        affected_records=len(invalid_values),
                        affected_columns=[field],
                        sample_values=[value for _, value in invalid_values[:5]],
                        suggested_fix=f"Validate and correct {field.upper()} formats",
                        compliance_impact=[ComplianceType.RBI] if field in ['ifsc', 'pan'] else [ComplianceType.PDP],
                        detected_at=datetime.now()
                    ))
                else:
                    passed += 1
        
        # Amount validation
        if 'amount' in df.columns:
            total += 1
            amount_min, amount_max = self.validation_rules['format_rules']['amount_range']
            invalid_amounts = df[
                (df['amount'] < amount_min) | 
                (df['amount'] > amount_max) |
                (df['amount'].isna())
            ]
            
            if len(invalid_amounts) > 0:
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name='invalid_amount_range',
                    severity=SeverityLevel.MEDIUM,
                    message=f"Found {len(invalid_amounts)} amounts outside valid range (₹{amount_min:,} - ₹{amount_max:,})",
                    affected_records=len(invalid_amounts),
                    affected_columns=['amount'],
                    sample_values=invalid_amounts['amount'].head(5).tolist(),
                    suggested_fix=f"Verify amounts are within ₹{amount_min:,} - ₹{amount_max:,} range",
                    compliance_impact=[ComplianceType.RBI],
                    detected_at=datetime.now()
                ))
            else:
                passed += 1
        
        return issues, passed, total
    
    def _validate_business_rules(self, df: pd.DataFrame, dataset_id: str) -> Tuple[List[DataQualityIssue], int, int]:
        """Validate business logic rules"""
        issues = []
        passed = 0
        total = 0
        
        business_rules = self.validation_rules['business_rules']
        
        # Transaction limit validation
        if 'amount' in df.columns and 'payment_method' in df.columns:
            total += 1
            violations = []
            
            for idx, row in df.iterrows():
                amount = row.get('amount', 0)
                method = row.get('payment_method', '').lower()
                
                limit_key = f"{method}_limit"
                if limit_key in business_rules['transaction_limits']:
                    limit = business_rules['transaction_limits'][limit_key]
                    if amount > limit:
                        violations.append((idx, method, amount, limit))
            
            if violations:
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name='transaction_limit_violation',
                    severity=SeverityLevel.HIGH,
                    message=f"Found {len(violations)} transactions exceeding method limits",
                    affected_records=len(violations),
                    affected_columns=['amount', 'payment_method'],
                    sample_values=[f"{method}: ₹{amount:,} > ₹{limit:,}" for _, method, amount, limit in violations[:5]],
                    suggested_fix="Review transaction amounts against payment method limits",
                    compliance_impact=[ComplianceType.RBI],
                    detected_at=datetime.now()
                ))
            else:
                passed += 1
        
        # Time-based validation
        if 'timestamp' in df.columns:
            total += 1
            try:
                df_timestamp = pd.to_datetime(df['timestamp'])
                working_start, working_end = business_rules['working_hours']
                
                # Check for transactions outside working hours
                outside_hours = df_timestamp.dt.hour < working_start
                outside_hours |= df_timestamp.dt.hour >= working_end
                
                suspicious_count = outside_hours.sum()
                
                if suspicious_count > len(df) * 0.1:  # More than 10% outside working hours
                    issues.append(DataQualityIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name='unusual_timing_pattern',
                        severity=SeverityLevel.MEDIUM,
                        message=f"High volume of transactions ({suspicious_count}) outside working hours ({working_start}-{working_end})",
                        affected_records=suspicious_count,
                        affected_columns=['timestamp'],
                        sample_values=df_timestamp[outside_hours].head(5).astype(str).tolist(),
                        suggested_fix="Review transactions outside working hours for potential issues",
                        compliance_impact=[],
                        detected_at=datetime.now()
                    ))
                else:
                    passed += 1
                    
            except Exception as e:
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name='timestamp_parsing_error',
                    severity=SeverityLevel.HIGH,
                    message=f"Failed to parse timestamp column: {str(e)}",
                    affected_records=len(df),
                    affected_columns=['timestamp'],
                    sample_values=df['timestamp'].head(5).astype(str).tolist(),
                    suggested_fix="Fix timestamp format in source data",
                    compliance_impact=[],
                    detected_at=datetime.now()
                ))
        
        # Duplicate detection
        total += 1
        if 'transaction_id' in df.columns:
            duplicates = df['transaction_id'].duplicated()
            duplicate_count = duplicates.sum()
            
            if duplicate_count > 0:
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name='duplicate_transaction_ids',
                    severity=SeverityLevel.CRITICAL,
                    message=f"Found {duplicate_count} duplicate transaction IDs",
                    affected_records=duplicate_count,
                    affected_columns=['transaction_id'],
                    sample_values=df[duplicates]['transaction_id'].head(5).tolist(),
                    suggested_fix="Remove or fix duplicate transaction IDs",
                    compliance_impact=[ComplianceType.SOX],
                    detected_at=datetime.now()
                ))
            else:
                passed += 1
        
        return issues, passed, total
    
    def _detect_anomalies(self, df: pd.DataFrame, dataset_id: str) -> List[DataQualityIssue]:
        """Detect anomalies using ML techniques"""
        issues = []
        
        try:
            # If not trained, train on current data (assuming it's mostly clean)
            if not self.anomaly_detector.is_trained:
                self.anomaly_detector.train_on_clean_data(df)
            
            # Detect anomalies
            predictions, scores = self.anomaly_detector.detect_anomalies(df)
            
            # Count anomalies
            anomaly_count = (predictions == -1).sum()
            
            if anomaly_count > 0:
                # Get most anomalous records
                anomaly_indices = np.where(predictions == -1)[0]
                most_anomalous = anomaly_indices[np.argsort(scores[anomaly_indices])[:5]]
                
                issues.append(DataQualityIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_name='ml_anomaly_detection',
                    severity=SeverityLevel.MEDIUM,
                    message=f"ML model detected {anomaly_count} potential anomalies",
                    affected_records=anomaly_count,
                    affected_columns=df.select_dtypes(include=[np.number]).columns.tolist(),
                    sample_values=[f"Row {idx}: score {scores[idx]:.3f}" for idx in most_anomalous],
                    suggested_fix="Review flagged records for potential data quality issues",
                    compliance_impact=[],
                    detected_at=datetime.now(),
                    context={'anomaly_percentage': anomaly_count / len(df)}
                ))
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
        
        return issues
    
    def _validate_compliance(self, df: pd.DataFrame, dataset_id: str) -> Tuple[List[DataQualityIssue], Dict[ComplianceType, bool]]:
        """Validate compliance requirements"""
        issues = []
        compliance_status = {comp: True for comp in ComplianceType}
        
        compliance_rules = self.validation_rules['compliance_rules']
        
        # GDPR compliance check
        if 'gdpr' in compliance_rules:
            gdpr_rules = compliance_rules['gdpr']
            pii_fields = gdpr_rules['pii_fields']
            
            # Check for PII fields without consent
            if 'consent' in df.columns:
                no_consent = df[df['consent'] != True]
                
                for pii_field in pii_fields:
                    if pii_field in df.columns:
                        pii_without_consent = no_consent[no_consent[pii_field].notna()]
                        
                        if len(pii_without_consent) > 0:
                            issues.append(DataQualityIssue(
                                issue_id=str(uuid.uuid4()),
                                rule_name=f'gdpr_consent_{pii_field}',
                                severity=SeverityLevel.CRITICAL,
                                message=f"Found {len(pii_without_consent)} records with PII field '{pii_field}' but no consent",
                                affected_records=len(pii_without_consent),
                                affected_columns=[pii_field, 'consent'],
                                sample_values=[],  # Don't show PII in logs
                                suggested_fix=f"Remove PII data or obtain consent for {pii_field}",
                                compliance_impact=[ComplianceType.GDPR],
                                detected_at=datetime.now()
                            ))
                            compliance_status[ComplianceType.GDPR] = False
            
            # Check data retention
            if 'created_at' in df.columns:
                retention_days = gdpr_rules['retention_days']
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                old_records = df[pd.to_datetime(df['created_at']) < cutoff_date]
                
                if len(old_records) > 0:
                    issues.append(DataQualityIssue(
                        issue_id=str(uuid.uuid4()),
                        rule_name='gdpr_data_retention',
                        severity=SeverityLevel.HIGH,
                        message=f"Found {len(old_records)} records older than {retention_days} days (GDPR retention limit)",
                        affected_records=len(old_records),
                        affected_columns=['created_at'],
                        sample_values=[],
                        suggested_fix=f"Archive or delete records older than {retention_days} days",
                        compliance_impact=[ComplianceType.GDPR],
                        detected_at=datetime.now()
                    ))
                    compliance_status[ComplianceType.GDPR] = False
        
        # PCI-DSS compliance check
        if 'pci_dss' in compliance_rules:
            pci_rules = compliance_rules['pci_dss']
            card_fields = pci_rules['card_fields']
            
            for card_field in card_fields:
                if card_field in df.columns:
                    # Check if card data is in plaintext (compliance violation)
                    plaintext_cards = df[df[card_field].astype(str).str.len() > 4]  # Assuming stored cards should be masked
                    
                    if len(plaintext_cards) > 0:
                        issues.append(DataQualityIssue(
                            issue_id=str(uuid.uuid4()),
                            rule_name=f'pci_dss_plaintext_{card_field}',
                            severity=SeverityLevel.CRITICAL,
                            message=f"Found {len(plaintext_cards)} records with unencrypted {card_field} data",
                            affected_records=len(plaintext_cards),
                            affected_columns=[card_field],
                            sample_values=[],  # Never log card data
                            suggested_fix=f"Encrypt or mask {card_field} data according to PCI-DSS standards",
                            compliance_impact=[ComplianceType.PCI_DSS],
                            detected_at=datetime.now()
                        ))
                        compliance_status[ComplianceType.PCI_DSS] = False
        
        return issues, compliance_status
    
    def _calculate_quality_score(self, df: pd.DataFrame, issues: List[DataQualityIssue]) -> float:
        """Calculate overall data quality score"""
        if not issues:
            return 1.0
        
        # Weight issues by severity
        severity_weights = {
            SeverityLevel.LOW: 0.1,
            SeverityLevel.MEDIUM: 0.3,
            SeverityLevel.HIGH: 0.7,
            SeverityLevel.CRITICAL: 1.0
        }
        
        total_penalty = 0
        for issue in issues:
            # Calculate penalty based on severity and affected records percentage
            affected_percentage = issue.affected_records / len(df) if len(df) > 0 else 1
            penalty = severity_weights[issue.severity] * affected_percentage
            total_penalty += penalty
        
        # Normalize penalty to get score between 0 and 1
        quality_score = max(0, 1 - (total_penalty / len(issues)) if issues else 1)
        
        return quality_score
    
    def _generate_recommendations(self, issues: List[DataQualityIssue]) -> List[str]:
        """Generate actionable recommendations based on issues"""
        recommendations = []
        
        # Group issues by type
        issue_types = defaultdict(list)
        for issue in issues:
            issue_types[issue.severity].append(issue)
        
        # Critical issues first
        if SeverityLevel.CRITICAL in issue_types:
            recommendations.append("🚨 Address CRITICAL issues immediately - they may block data processing")
            
        # Format-specific recommendations
        format_issues = [issue for issue in issues if 'format' in issue.rule_name]
        if format_issues:
            recommendations.append("🔧 Implement data validation at source to prevent format issues")
        
        # Compliance recommendations
        compliance_issues = [issue for issue in issues if issue.compliance_impact]
        if compliance_issues:
            recommendations.append("📋 Review data governance policies for compliance violations")
        
        # ML anomaly recommendations
        ml_issues = [issue for issue in issues if 'anomaly' in issue.rule_name]
        if ml_issues:
            recommendations.append("🤖 Investigate ML-flagged anomalies for potential data corruption")
        
        # General recommendations
        if len(issues) > 10:
            recommendations.append("⚡ Consider implementing real-time data validation")
        
        return recommendations
    
    def _store_validation_results(self, result: ValidationResult):
        """Store validation results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store issues
        for issue in result.issues:
            cursor.execute('''
                INSERT OR REPLACE INTO quality_issues
                (issue_id, dataset_id, rule_name, severity, message, affected_records, detected_at, is_resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                issue.issue_id, result.dataset_id, issue.rule_name, issue.severity.value,
                issue.message, issue.affected_records, issue.detected_at, False
            ))
        
        # Store metrics
        metrics = [
            ('quality_score', result.quality_score, 0.8),
            ('completeness', 1 - (len([i for i in result.issues if 'completeness' in i.rule_name]) / max(result.total_records, 1)), self.quality_thresholds['completeness']),
            ('validity', 1 - (len([i for i in result.issues if 'format' in i.rule_name]) / max(result.total_records, 1)), self.quality_thresholds['validity'])
        ]
        
        for metric_name, value, threshold in metrics:
            cursor.execute('''
                INSERT INTO quality_metrics
                (metric_id, dataset_id, metric_name, metric_value, threshold_value, is_passed, measured_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()), result.dataset_id, metric_name, value, threshold,
                value >= threshold, datetime.now()
            ))
        
        conn.commit()
        conn.close()
    
    def generate_quality_report(self, dataset_id: str) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        conn = sqlite3.connect(self.db_path)
        
        # Get recent validation results
        issues_df = pd.read_sql_query('''
            SELECT * FROM quality_issues 
            WHERE dataset_id = ? 
            ORDER BY detected_at DESC 
            LIMIT 100
        ''', conn, params=(dataset_id,))
        
        metrics_df = pd.read_sql_query('''
            SELECT * FROM quality_metrics 
            WHERE dataset_id = ? 
            ORDER BY measured_at DESC 
            LIMIT 50
        ''', conn, params=(dataset_id,))
        
        conn.close()
        
        # Generate report
        report = {
            'dataset_id': dataset_id,
            'report_generated_at': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(issues_df),
                'critical_issues': len(issues_df[issues_df['severity'] == 'critical']),
                'resolved_issues': len(issues_df[issues_df['is_resolved'] == True]),
                'latest_quality_score': metrics_df[metrics_df['metric_name'] == 'quality_score']['metric_value'].iloc[0] if len(metrics_df) > 0 else 0
            },
            'issue_breakdown': issues_df['severity'].value_counts().to_dict() if len(issues_df) > 0 else {},
            'trend_analysis': {
                'quality_trend': 'improving' if len(metrics_df) > 1 and metrics_df['metric_value'].iloc[0] > metrics_df['metric_value'].iloc[1] else 'stable',
                'recent_metrics': metrics_df.head(10).to_dict('records')
            },
            'recommendations': [
                'Focus on resolving critical issues first',
                'Implement automated data validation',
                'Set up real-time monitoring dashboards'
            ]
        }
        
        return report

def create_sample_dataset() -> pd.DataFrame:
    """Create sample dataset for testing"""
    np.random.seed(42)
    
    # Generate sample data with various quality issues
    n_records = 1000
    
    data = {
        'user_id': [f'USER_{i:06d}' for i in range(n_records)],
        'email': [
            f'user{i}@example.com' if i % 10 != 0 else f'invalid_email_{i}'  # 10% invalid emails
            for i in range(n_records)
        ],
        'phone': [
            f'+919876543{str(i).zfill(3)[-3:]}' if i % 15 != 0 else f'invalid_phone_{i}'  # Invalid phones
            for i in range(n_records)
        ],
        'amount': [
            np.random.uniform(100, 50000) if i % 20 != 0 else -100  # Some negative amounts
            for i in range(n_records)
        ],
        'payment_method': np.random.choice(['upi', 'card', 'wallet'], n_records),
        'timestamp': [
            datetime.now() - timedelta(minutes=np.random.randint(0, 10080))  # Last week
            for i in range(n_records)
        ],
        'transaction_id': [
            f'TXN_{i:08d}' if i not in [100, 200] else 'TXN_00000100'  # Duplicates
            for i in range(n_records)
        ],
        'aadhaar': [
            '123456789012' if i % 8 != 0 else None  # Some missing Aadhaar
            for i in range(n_records)
        ],
        'pan': [
            f'ABCDE1234{chr(65 + i % 26)}' if i % 12 != 0 else 'INVALID_PAN'
            for i in range(n_records)
        ]
    }
    
    # Add some completely null rows
    for i in [50, 150, 250]:
        for col in data:
            if isinstance(data[col], list) and i < len(data[col]):
                data[col][i] = None
    
    return pd.DataFrame(data)

async def main():
    """
    Main function demonstrating comprehensive data quality framework
    Complete data quality validation का production demo
    """
    
    logger.info("📊 Starting Comprehensive Data Quality Validation Framework")
    logger.info("यह framework production-ready data quality validation करता है:")
    logger.info("  • Format और business rule validation")
    logger.info("  • ML-based anomaly detection")
    logger.info("  • Indian compliance (Aadhaar, PAN, IFSC)")
    logger.info("  • GDPR और PCI-DSS compliance")
    logger.info("  • Auto-healing recommendations")
    
    # Configuration
    config = {
        'database_path': 'data_quality_demo.db',
        'quality_thresholds': {
            'completeness': 0.95,
            'accuracy': 0.98,
            'consistency': 0.99,
            'timeliness': 0.90,
            'validity': 0.97
        }
    }
    
    # Initialize framework
    framework = DataQualityFramework(config)
    
    try:
        # Create sample dataset
        print("\n📝 Creating sample dataset with quality issues...")
        sample_data = create_sample_dataset()
        
        print(f"  • Dataset created: {len(sample_data)} records, {len(sample_data.columns)} columns")
        print(f"  • Intentionally added quality issues for demonstration")
        
        # Run comprehensive validation
        print(f"\n🔍 Running comprehensive data quality validation...")
        
        validation_result = framework.validate_dataset(sample_data, 'demo_dataset_001')
        
        # Display results
        print(f"\n" + "="*80)
        print(f"📊 DATA QUALITY VALIDATION RESULTS")
        print(f"="*80)
        
        print(f"Dataset: {validation_result.dataset_id}")
        print(f"Records: {validation_result.total_records:,}")
        print(f"Columns: {validation_result.total_columns}")
        print(f"Processing Time: {validation_result.processing_time:.2f}s")
        print(f"\n🎯 QUALITY SCORE: {validation_result.quality_score:.2f}/1.00")
        print(f"Overall Status: {'✅ PASSED' if validation_result.is_valid else '❌ FAILED'}")
        
        print(f"\n📈 VALIDATION SUMMARY:")
        print(f"  • Passed Checks: {validation_result.passed_checks}")
        print(f"  • Failed Checks: {validation_result.failed_checks}")
        print(f"  • Total Issues Found: {len(validation_result.issues)}")
        
        # Issue breakdown by severity
        issue_counts = Counter(issue.severity for issue in validation_result.issues)
        print(f"\n🚨 ISSUES BY SEVERITY:")
        for severity, count in issue_counts.items():
            emoji = {'critical': '🔥', 'high': '⚠️', 'medium': '🟡', 'low': '🔵'}.get(severity.value, '❓')
            print(f"  {emoji} {severity.value.upper()}: {count} issues")
        
        # Show top issues
        print(f"\n🔍 TOP CRITICAL ISSUES:")
        critical_issues = [issue for issue in validation_result.issues if issue.severity == SeverityLevel.CRITICAL]
        for i, issue in enumerate(critical_issues[:5], 1):
            print(f"  {i}. {issue.message}")
            print(f"     • Affected: {issue.affected_records:,} records")
            print(f"     • Fix: {issue.suggested_fix}")
            if issue.compliance_impact:
                compliance_names = [comp.value.upper() for comp in issue.compliance_impact]
                print(f"     • Compliance Impact: {', '.join(compliance_names)}")
        
        # Compliance status
        print(f"\n📋 COMPLIANCE STATUS:")
        for compliance_type, status in validation_result.compliance_status.items():
            emoji = '✅' if status else '❌'
            print(f"  {emoji} {compliance_type.value.upper()}: {'COMPLIANT' if status else 'VIOLATIONS FOUND'}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, recommendation in enumerate(validation_result.recommendations, 1):
            print(f"  {i}. {recommendation}")
        
        # Indian-specific validation results
        print(f"\n🇮🇳 INDIAN DATA VALIDATION:")
        indian_issues = [issue for issue in validation_result.issues if any(
            indian_field in issue.rule_name for indian_field in ['aadhaar', 'pan', 'ifsc', 'gst', 'phone']
        )]
        
        for issue in indian_issues[:3]:
            print(f"  • {issue.rule_name.replace('_', ' ').title()}: {issue.message}")
        
        # ML Anomaly Detection Results
        ml_issues = [issue for issue in validation_result.issues if 'anomaly' in issue.rule_name]
        if ml_issues:
            print(f"\n🤖 ML ANOMALY DETECTION:")
            for issue in ml_issues:
                print(f"  • {issue.message}")
                anomaly_pct = issue.context.get('anomaly_percentage', 0) * 100
                print(f"  • Anomaly Rate: {anomaly_pct:.1f}%")
        
        # Generate detailed report
        print(f"\n📊 Generating detailed quality report...")
        quality_report = framework.generate_quality_report('demo_dataset_001')
        
        print(f"\n📈 QUALITY TRENDS:")
        print(f"  • Latest Quality Score: {quality_report['summary']['latest_quality_score']:.2f}")
        print(f"  • Total Issues: {quality_report['summary']['total_issues']}")
        print(f"  • Critical Issues: {quality_report['summary']['critical_issues']}")
        print(f"  • Quality Trend: {quality_report['trend_analysis']['quality_trend'].title()}")
        
        # Sample data healing suggestions
        print(f"\n🔧 DATA HEALING SUGGESTIONS:")
        healing_suggestions = [
            "Implement source validation for email formats",
            "Add Aadhaar checksum validation at data entry",
            "Set up automated phone number normalization",
            "Create business rule engine for transaction limits",
            "Implement real-time anomaly detection alerts"
        ]
        
        for i, suggestion in enumerate(healing_suggestions, 1):
            print(f"  {i}. {suggestion}")
        
        print(f"\n✅ Data Quality Framework demonstration completed!")
        print(f"यह comprehensive framework production में use करने के लिए ready है।")
        print(f"Database में validation results store हो गए हैं: {config['database_path']}")
        
        # Show validation success criteria
        print(f"\n🎯 PRODUCTION READINESS CRITERIA:")
        criteria = [
            f"Quality Score ≥ 0.80: {'✅' if validation_result.quality_score >= 0.80 else '❌'} ({validation_result.quality_score:.2f})",
            f"No Critical Issues: {'✅' if not critical_issues else '❌'} ({len(critical_issues)} found)",
            f"GDPR Compliant: {'✅' if validation_result.compliance_status.get(ComplianceType.GDPR, True) else '❌'}",
            f"PCI-DSS Compliant: {'✅' if validation_result.compliance_status.get(ComplianceType.PCI_DSS, True) else '❌'}"
        ]
        
        for criterion in criteria:
            print(f"  • {criterion}")
        
        final_status = "🟢 READY FOR PRODUCTION" if validation_result.is_valid else "🔴 NEEDS ATTENTION"
        print(f"\n{final_status}")
        
    except Exception as e:
        logger.error(f"Data quality framework demonstration failed: {e}")
        raise

if __name__ == "__main__":
    # Run the data quality framework demo
    import time
    asyncio.run(main())