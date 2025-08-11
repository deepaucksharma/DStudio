#!/usr/bin/env python3
"""
Data Quality Validation System - Paytm Transaction Validation
=============================================================

जैसे Paytm में हर transaction की security और accuracy check होती है,
वैसे ही comprehensive data quality framework बनाएंगे।

Real-world use case: Paytm processes 2.5 billion+ transactions/month
Data quality requirements: 99.99% accuracy, zero tolerance for financial errors

Author: DStudio Engineering Team
Episode: 11 - ETL & Data Integration Patterns
"""

import logging
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import re
import hashlib
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

# Great Expectations for data validation
try:
    import great_expectations as ge
    from great_expectations.core.expectation_configuration import ExpectationConfiguration
    from great_expectations.data_context import DataContext
    GE_AVAILABLE = True
except ImportError:
    GE_AVAILABLE = False
    print("⚠️ Great Expectations not available - using basic validation")

class ValidationSeverity(Enum):
    """Data quality issue severity levels"""
    CRITICAL = "CRITICAL"    # Transaction blocking issues
    HIGH = "HIGH"           # Data accuracy issues
    MEDIUM = "MEDIUM"       # Data completeness issues
    LOW = "LOW"            # Data formatting issues
    WARNING = "WARNING"     # Data anomaly warnings

@dataclass
class ValidationRule:
    """Single validation rule definition"""
    rule_id: str
    rule_name: str
    description: str
    severity: ValidationSeverity
    validation_function: Callable
    error_message: str
    business_impact: str
    remediation_hint: str

@dataclass  
class ValidationResult:
    """Result of a single validation check"""
    rule_id: str
    rule_name: str
    severity: ValidationSeverity
    passed: bool
    failed_records_count: int = 0
    total_records_count: int = 0
    error_details: List[Dict] = field(default_factory=list)
    execution_time_ms: float = 0.0
    remediation_suggestions: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Success rate percentage"""
        if self.total_records_count == 0:
            return 100.0
        return ((self.total_records_count - self.failed_records_count) / self.total_records_count) * 100

@dataclass
class QualityReport:
    """Complete data quality assessment report"""
    dataset_name: str
    validation_timestamp: datetime
    total_records: int
    validation_results: List[ValidationResult]
    overall_score: float = 0.0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    warnings: int = 0
    
    def __post_init__(self):
        """Calculate summary statistics"""
        for result in self.validation_results:
            if not result.passed:
                if result.severity == ValidationSeverity.CRITICAL:
                    self.critical_issues += 1
                elif result.severity == ValidationSeverity.HIGH:
                    self.high_issues += 1
                elif result.severity == ValidationSeverity.MEDIUM:
                    self.medium_issues += 1
                elif result.severity == ValidationSeverity.LOW:
                    self.low_issues += 1
                elif result.severity == ValidationSeverity.WARNING:
                    self.warnings += 1
        
        # Calculate overall quality score (0-100)
        if self.validation_results:
            success_rates = [result.success_rate for result in self.validation_results]
            self.overall_score = statistics.mean(success_rates)

class PaytmDataQualityValidator:
    """
    Paytm-style Data Quality Validation Framework
    ============================================
    
    Paytm के financial data quality standards के अनुसार
    comprehensive validation system।
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.validation_rules = []
        self.business_rules = self._load_paytm_business_rules()
        self._register_default_rules()
        
    def _setup_logging(self):
        """Production-grade logging for quality monitoring"""
        logger = logging.getLogger("PaytmDataQuality")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler for audit trail
            file_handler = logging.FileHandler(
                f"paytm_data_quality_{datetime.now().strftime('%Y%m%d')}.log"
            )
            
            # Console handler for real-time monitoring
            console_handler = logging.StreamHandler()
            
            # Formatter with transaction context
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [QUALITY] - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _load_paytm_business_rules(self) -> Dict:
        """Paytm के business rules और limits"""
        return {
            # Transaction limits - RBI और Paytm wallet guidelines
            'min_transaction_amount': Decimal('1.00'),          # Minimum ₹1
            'max_wallet_transaction': Decimal('200000.00'),     # Paytm wallet limit ₹2 lakhs
            'max_bank_transaction': Decimal('1000000.00'),      # Bank transfer limit ₹10 lakhs
            'daily_wallet_limit': Decimal('20000.00'),          # Daily wallet spending ₹20k
            'monthly_wallet_limit': Decimal('200000.00'),       # Monthly wallet limit ₹2 lakhs
            
            # Account validation patterns
            'mobile_pattern': r'^[6-9]\d{9}$',                  # Indian mobile numbers
            'email_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'pan_pattern': r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',       # PAN card format
            'aadhaar_pattern': r'^\d{4}\s?\d{4}\s?\d{4}$',      # Aadhaar format
            
            # Transaction types और categories
            'valid_transaction_types': [
                'P2P', 'P2M', 'WALLET_TOPUP', 'BILL_PAYMENT', 
                'RECHARGE', 'MONEY_TRANSFER', 'QR_PAYMENT', 'MERCHANT_PAYMENT'
            ],
            'valid_payment_methods': [
                'WALLET', 'UPI', 'DEBIT_CARD', 'CREDIT_CARD', 'NET_BANKING'
            ],
            'valid_merchant_categories': [
                'FOOD', 'TRANSPORT', 'ENTERTAINMENT', 'SHOPPING', 'UTILITIES',
                'HEALTHCARE', 'EDUCATION', 'PETROL', 'GROCERY'
            ],
            
            # Status validations
            'valid_transaction_statuses': [
                'SUCCESS', 'FAILED', 'PENDING', 'TIMEOUT', 'CANCELLED'
            ],
            
            # Time-based rules
            'max_transaction_age_hours': 24,                    # Stale transaction detection
            'suspicious_time_gap_seconds': 5,                  # Too quick consecutive transactions
            'business_hours': (9, 21),                         # 9 AM to 9 PM
            
            # Fraud detection thresholds
            'high_velocity_threshold': 10,                      # 10 transactions in short time
            'amount_spike_multiplier': 5,                       # 5x average amount
            'geographic_distance_km': 100,                     # Impossible travel distance
        }
    
    def _register_default_rules(self):
        """Default validation rules का registration"""
        
        # 1. CRITICAL Rules - Transaction blocking
        self.add_validation_rule(ValidationRule(
            rule_id="CRIT001",
            rule_name="Transaction Amount Validation",
            description="Transaction amount must be positive and within limits",
            severity=ValidationSeverity.CRITICAL,
            validation_function=self._validate_transaction_amounts,
            error_message="Invalid transaction amount detected",
            business_impact="Prevents fraudulent or error transactions",
            remediation_hint="Check source system amount validation logic"
        ))
        
        self.add_validation_rule(ValidationRule(
            rule_id="CRIT002", 
            rule_name="Account Number Validation",
            description="Account numbers must be valid format and non-empty",
            severity=ValidationSeverity.CRITICAL,
            validation_function=self._validate_account_numbers,
            error_message="Invalid or missing account numbers",
            business_impact="Prevents failed transactions due to wrong account info",
            remediation_hint="Implement stricter account validation in frontend"
        ))
        
        # 2. HIGH Priority Rules - Data accuracy
        self.add_validation_rule(ValidationRule(
            rule_id="HIGH001",
            rule_name="Duplicate Transaction Detection", 
            description="Detect duplicate transactions within time window",
            severity=ValidationSeverity.HIGH,
            validation_function=self._detect_duplicate_transactions,
            error_message="Potential duplicate transactions found",
            business_impact="Prevents double charging customers",
            remediation_hint="Implement idempotency keys in transaction processing"
        ))
        
        self.add_validation_rule(ValidationRule(
            rule_id="HIGH002",
            rule_name="Mobile Number Validation",
            description="Mobile numbers must follow Indian format",
            severity=ValidationSeverity.HIGH,
            validation_function=self._validate_mobile_numbers,
            error_message="Invalid mobile number format",
            business_impact="Affects OTP delivery and user notifications",
            remediation_hint="Add mobile number format validation in registration"
        ))
        
        # 3. MEDIUM Priority Rules - Data completeness  
        self.add_validation_rule(ValidationRule(
            rule_id="MED001",
            rule_name="Mandatory Fields Completeness",
            description="All mandatory fields must be present and non-null",
            severity=ValidationSeverity.MEDIUM,
            validation_function=self._validate_mandatory_fields,
            error_message="Missing mandatory fields in transaction data",
            business_impact="Affects transaction processing and reporting accuracy",
            remediation_hint="Implement field validation in data ingestion layer"
        ))
        
        self.add_validation_rule(ValidationRule(
            rule_id="MED002",
            rule_name="Merchant Data Consistency",
            description="Merchant information should be consistent and valid",
            severity=ValidationSeverity.MEDIUM,
            validation_function=self._validate_merchant_data,
            error_message="Inconsistent merchant information",
            business_impact="Affects merchant analytics and settlement",
            remediation_hint="Maintain updated merchant master data"
        ))
        
        # 4. LOW Priority Rules - Data formatting
        self.add_validation_rule(ValidationRule(
            rule_id="LOW001", 
            rule_name="Timestamp Format Validation",
            description="All timestamps should be in correct format",
            severity=ValidationSeverity.LOW,
            validation_function=self._validate_timestamps,
            error_message="Invalid timestamp format",
            business_impact="Affects time-based analytics and reporting",
            remediation_hint="Standardize timestamp format across all systems"
        ))
        
        # 5. WARNING Rules - Anomaly detection
        self.add_validation_rule(ValidationRule(
            rule_id="WARN001",
            rule_name="Fraud Pattern Detection",
            description="Detect suspicious transaction patterns",
            severity=ValidationSeverity.WARNING,
            validation_function=self._detect_fraud_patterns,
            error_message="Suspicious transaction patterns detected",
            business_impact="Early fraud detection and prevention",
            remediation_hint="Review fraud detection algorithms and thresholds"
        ))
    
    def add_validation_rule(self, rule: ValidationRule):
        """Custom validation rule add करना"""
        self.validation_rules.append(rule)
        self.logger.info(f"✅ Validation rule added: {rule.rule_id} - {rule.rule_name}")
    
    # Individual validation functions
    def _validate_transaction_amounts(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Transaction amounts की comprehensive validation"""
        errors = []
        
        try:
            # Check for null amounts
            null_amount_mask = df['amount'].isnull()
            if null_amount_mask.any():
                null_records = df[null_amount_mask].to_dict('records')
                errors.extend([
                    {
                        'transaction_id': record.get('transaction_id', 'unknown'),
                        'error': 'Null amount',
                        'value': None
                    } for record in null_records
                ])
            
            # Check for negative amounts
            negative_amount_mask = df['amount'] <= 0
            if negative_amount_mask.any():
                negative_records = df[negative_amount_mask].to_dict('records')
                errors.extend([
                    {
                        'transaction_id': record.get('transaction_id', 'unknown'),
                        'error': 'Negative or zero amount',
                        'value': record.get('amount')
                    } for record in negative_records
                ])
            
            # Check for amount limits based on transaction type
            for idx, row in df.iterrows():
                try:
                    amount = Decimal(str(row['amount']))
                    transaction_type = row.get('payment_method', 'UNKNOWN')
                    
                    if transaction_type == 'WALLET' and amount > self.business_rules['max_wallet_transaction']:
                        errors.append({
                            'transaction_id': row.get('transaction_id', 'unknown'),
                            'error': 'Amount exceeds wallet limit',
                            'value': float(amount),
                            'limit': float(self.business_rules['max_wallet_transaction'])
                        })
                    
                    elif amount > self.business_rules['max_bank_transaction']:
                        errors.append({
                            'transaction_id': row.get('transaction_id', 'unknown'),
                            'error': 'Amount exceeds maximum limit',
                            'value': float(amount),
                            'limit': float(self.business_rules['max_bank_transaction'])
                        })
                    
                    elif amount < self.business_rules['min_transaction_amount']:
                        errors.append({
                            'transaction_id': row.get('transaction_id', 'unknown'),
                            'error': 'Amount below minimum limit',
                            'value': float(amount),
                            'minimum': float(self.business_rules['min_transaction_amount'])
                        })
                        
                except (InvalidOperation, TypeError, ValueError):
                    errors.append({
                        'transaction_id': row.get('transaction_id', 'unknown'),
                        'error': 'Invalid amount format',
                        'value': row.get('amount')
                    })
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Amount validation failed: {str(e)}")
            return False, [{'error': f'Validation system error: {str(e)}'}]
    
    def _validate_account_numbers(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Account numbers और VPA validation"""
        errors = []
        
        try:
            # Check for null/empty payer account
            payer_null_mask = df['payer_account'].isnull() | (df['payer_account'] == '')
            if payer_null_mask.any():
                null_records = df[payer_null_mask]
                errors.extend([
                    {
                        'transaction_id': row.get('transaction_id', 'unknown'),
                        'error': 'Missing payer account',
                        'field': 'payer_account'
                    } for _, row in null_records.iterrows()
                ])
            
            # Check for null/empty payee account
            payee_null_mask = df['payee_account'].isnull() | (df['payee_account'] == '')
            if payee_null_mask.any():
                null_records = df[payee_null_mask]
                errors.extend([
                    {
                        'transaction_id': row.get('transaction_id', 'unknown'),
                        'error': 'Missing payee account',
                        'field': 'payee_account'
                    } for _, row in null_records.iterrows()
                ])
            
            # Validate mobile number format for accounts
            mobile_pattern = re.compile(self.business_rules['mobile_pattern'])
            
            for idx, row in df.iterrows():
                payer_account = str(row.get('payer_account', ''))
                payee_account = str(row.get('payee_account', ''))
                
                # Check if account is mobile number format
                if payer_account.isdigit() and len(payer_account) == 10:
                    if not mobile_pattern.match(payer_account):
                        errors.append({
                            'transaction_id': row.get('transaction_id', 'unknown'),
                            'error': 'Invalid payer mobile number format',
                            'value': payer_account
                        })
                
                if payee_account.isdigit() and len(payee_account) == 10:
                    if not mobile_pattern.match(payee_account):
                        errors.append({
                            'transaction_id': row.get('transaction_id', 'unknown'),
                            'error': 'Invalid payee mobile number format', 
                            'value': payee_account
                        })
                
                # Check for self-transactions
                if payer_account == payee_account and payer_account != '':
                    errors.append({
                        'transaction_id': row.get('transaction_id', 'unknown'),
                        'error': 'Self-transaction detected',
                        'payer': payer_account,
                        'payee': payee_account
                    })
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Account validation failed: {str(e)}")
            return False, [{'error': f'Account validation error: {str(e)}'}]
    
    def _detect_duplicate_transactions(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Duplicate transactions detection - Same payer, payee, amount within time window"""
        errors = []
        
        try:
            # Sort by timestamp for efficient duplicate detection
            df_sorted = df.sort_values('transaction_timestamp')
            
            # Group by potential duplicate criteria
            duplicate_groups = df_sorted.groupby([
                'payer_account', 'payee_account', 'amount'
            ])
            
            for (payer, payee, amount), group in duplicate_groups:
                if len(group) > 1:
                    # Check if transactions are within suspicious time window
                    group_sorted = group.sort_values('transaction_timestamp')
                    
                    for i in range(1, len(group_sorted)):
                        current_time = pd.to_datetime(group_sorted.iloc[i]['transaction_timestamp'])
                        prev_time = pd.to_datetime(group_sorted.iloc[i-1]['transaction_timestamp'])
                        
                        time_diff = (current_time - prev_time).total_seconds()
                        
                        # If transactions are within suspicious timeframe (30 seconds)
                        if time_diff <= 30:
                            errors.append({
                                'transaction_id_1': group_sorted.iloc[i-1].get('transaction_id', 'unknown'),
                                'transaction_id_2': group_sorted.iloc[i].get('transaction_id', 'unknown'),
                                'error': 'Potential duplicate transaction',
                                'time_gap_seconds': time_diff,
                                'payer': payer,
                                'payee': payee,
                                'amount': float(amount)
                            })
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Duplicate detection failed: {str(e)}")
            return False, [{'error': f'Duplicate detection error: {str(e)}'}]
    
    def _validate_mobile_numbers(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Mobile numbers validation - Indian format"""
        errors = []
        
        try:
            mobile_pattern = re.compile(self.business_rules['mobile_pattern'])
            
            # Check all mobile number columns
            mobile_columns = ['payer_mobile', 'payee_mobile', 'registered_mobile']
            
            for column in mobile_columns:
                if column in df.columns:
                    for idx, row in df.iterrows():
                        mobile = str(row.get(column, ''))
                        
                        if mobile and mobile != 'nan':
                            # Remove any formatting (spaces, hyphens)
                            cleaned_mobile = re.sub(r'[^0-9]', '', mobile)
                            
                            if not mobile_pattern.match(cleaned_mobile):
                                errors.append({
                                    'transaction_id': row.get('transaction_id', 'unknown'),
                                    'error': f'Invalid mobile number in {column}',
                                    'value': mobile,
                                    'cleaned_value': cleaned_mobile,
                                    'expected_format': 'Indian mobile: 6/7/8/9 followed by 9 digits'
                                })
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Mobile validation failed: {str(e)}")
            return False, [{'error': f'Mobile validation error: {str(e)}'}]
    
    def _validate_mandatory_fields(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Mandatory fields completeness check"""
        errors = []
        
        try:
            # Define mandatory fields for Paytm transactions
            mandatory_fields = [
                'transaction_id', 'payer_account', 'payee_account', 
                'amount', 'transaction_timestamp', 'transaction_type',
                'payment_method', 'status'
            ]
            
            for field in mandatory_fields:
                if field not in df.columns:
                    errors.append({
                        'error': f'Missing mandatory column: {field}',
                        'impact': 'All records affected',
                        'column': field
                    })
                    continue
                
                # Check for null/empty values
                null_mask = df[field].isnull() | (df[field] == '')
                if null_mask.any():
                    null_records = df[null_mask]
                    for _, row in null_records.iterrows():
                        errors.append({
                            'transaction_id': row.get('transaction_id', 'unknown'),
                            'error': f'Missing mandatory field: {field}',
                            'field': field,
                            'value': row.get(field)
                        })
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Mandatory fields validation failed: {str(e)}")
            return False, [{'error': f'Mandatory fields validation error: {str(e)}'}]
    
    def _validate_merchant_data(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Merchant information consistency validation"""
        errors = []
        
        try:
            # Check for P2M transactions (merchant payments)
            p2m_transactions = df[df['transaction_type'] == 'P2M']
            
            for idx, row in p2m_transactions.iterrows():
                transaction_id = row.get('transaction_id', 'unknown')
                
                # Merchant ID should be present for P2M transactions
                merchant_id = row.get('merchant_id', '')
                if not merchant_id:
                    errors.append({
                        'transaction_id': transaction_id,
                        'error': 'Missing merchant ID for P2M transaction',
                        'transaction_type': 'P2M'
                    })
                
                # Merchant category should be valid
                merchant_category = row.get('merchant_category', '')
                if merchant_category not in self.business_rules['valid_merchant_categories']:
                    errors.append({
                        'transaction_id': transaction_id,
                        'error': 'Invalid merchant category',
                        'value': merchant_category,
                        'valid_categories': self.business_rules['valid_merchant_categories']
                    })
                
                # MCC code validation (4-digit merchant category code)
                mcc_code = str(row.get('mcc_code', ''))
                if mcc_code and not (mcc_code.isdigit() and len(mcc_code) == 4):
                    errors.append({
                        'transaction_id': transaction_id,
                        'error': 'Invalid MCC code format',
                        'value': mcc_code,
                        'expected_format': '4-digit numeric code'
                    })
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Merchant validation failed: {str(e)}")
            return False, [{'error': f'Merchant validation error: {str(e)}'}]
    
    def _validate_timestamps(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Timestamp format और business rules validation"""
        errors = []
        
        try:
            timestamp_columns = [
                'transaction_timestamp', 'created_at', 'updated_at', 'processed_at'
            ]
            
            for column in timestamp_columns:
                if column in df.columns:
                    for idx, row in df.iterrows():
                        timestamp_value = row.get(column)
                        transaction_id = row.get('transaction_id', 'unknown')
                        
                        if pd.isnull(timestamp_value):
                            if column == 'transaction_timestamp':  # Critical timestamp
                                errors.append({
                                    'transaction_id': transaction_id,
                                    'error': f'Missing critical timestamp: {column}',
                                    'column': column
                                })
                            continue
                        
                        try:
                            # Parse timestamp
                            parsed_time = pd.to_datetime(timestamp_value)
                            
                            # Check if timestamp is in future (more than 5 minutes)
                            if parsed_time > datetime.now() + timedelta(minutes=5):
                                errors.append({
                                    'transaction_id': transaction_id,
                                    'error': f'Future timestamp detected in {column}',
                                    'value': str(timestamp_value),
                                    'parsed_time': str(parsed_time)
                                })
                            
                            # Check if timestamp is too old (more than 1 year)
                            if parsed_time < datetime.now() - timedelta(days=365):
                                errors.append({
                                    'transaction_id': transaction_id,
                                    'error': f'Very old timestamp in {column}',
                                    'value': str(timestamp_value),
                                    'parsed_time': str(parsed_time)
                                })
                                
                        except (ValueError, TypeError):
                            errors.append({
                                'transaction_id': transaction_id,
                                'error': f'Invalid timestamp format in {column}',
                                'value': str(timestamp_value),
                                'expected_format': 'ISO format: YYYY-MM-DD HH:MM:SS'
                            })
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"❌ Timestamp validation failed: {str(e)}")
            return False, [{'error': f'Timestamp validation error: {str(e)}'}]
    
    def _detect_fraud_patterns(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Fraud और suspicious patterns detection"""
        warnings = []
        
        try:
            # Sort by timestamp for pattern analysis
            df_sorted = df.sort_values('transaction_timestamp')
            
            # 1. High velocity transactions (same user, multiple transactions quickly)
            for payer in df['payer_account'].unique():
                payer_transactions = df_sorted[df_sorted['payer_account'] == payer]
                
                if len(payer_transactions) >= self.business_rules['high_velocity_threshold']:
                    # Check time window
                    first_txn_time = pd.to_datetime(payer_transactions.iloc[0]['transaction_timestamp'])
                    last_txn_time = pd.to_datetime(payer_transactions.iloc[-1]['transaction_timestamp'])
                    
                    time_window_minutes = (last_txn_time - first_txn_time).total_seconds() / 60
                    
                    if time_window_minutes <= 10:  # 10+ transactions in 10 minutes
                        warnings.append({
                            'payer_account': payer,
                            'pattern': 'High velocity transactions',
                            'transaction_count': len(payer_transactions),
                            'time_window_minutes': time_window_minutes,
                            'risk_level': 'HIGH'
                        })
            
            # 2. Amount spike detection (transaction much larger than user's average)
            payer_stats = df.groupby('payer_account')['amount'].agg(['mean', 'std', 'count']).reset_index()
            
            for idx, row in df.iterrows():
                payer = row['payer_account']
                current_amount = float(row['amount'])
                
                payer_stat = payer_stats[payer_stats['payer_account'] == payer]
                if not payer_stat.empty and payer_stat.iloc[0]['count'] >= 5:  # Enough history
                    avg_amount = payer_stat.iloc[0]['mean']
                    
                    if current_amount > avg_amount * self.business_rules['amount_spike_multiplier']:
                        warnings.append({
                            'transaction_id': row.get('transaction_id', 'unknown'),
                            'payer_account': payer,
                            'pattern': 'Amount spike',
                            'current_amount': current_amount,
                            'average_amount': avg_amount,
                            'spike_multiplier': current_amount / avg_amount,
                            'risk_level': 'MEDIUM'
                        })
            
            # 3. Round number amounts (possible money laundering indicator)
            round_amounts = df[df['amount'] % 1000 == 0]  # Amounts divisible by 1000
            high_round_amounts = round_amounts[round_amounts['amount'] >= 50000]  # >= 50k
            
            for _, row in high_round_amounts.iterrows():
                warnings.append({
                    'transaction_id': row.get('transaction_id', 'unknown'),
                    'pattern': 'High value round amount',
                    'amount': float(row['amount']),
                    'risk_level': 'MEDIUM'
                })
            
            # 4. Off-hours transaction pattern
            business_hours = self.business_rules['business_hours']
            
            for idx, row in df.iterrows():
                try:
                    txn_time = pd.to_datetime(row['transaction_timestamp'])
                    hour = txn_time.hour
                    
                    if not (business_hours[0] <= hour <= business_hours[1]):
                        if float(row['amount']) >= 10000:  # High value off-hours
                            warnings.append({
                                'transaction_id': row.get('transaction_id', 'unknown'),
                                'pattern': 'High value off-hours transaction',
                                'amount': float(row['amount']),
                                'hour': hour,
                                'business_hours': f"{business_hours[0]}:00 - {business_hours[1]}:00",
                                'risk_level': 'LOW'
                            })
                except:
                    continue
            
            return len(warnings) == 0, warnings
            
        except Exception as e:
            self.logger.error(f"❌ Fraud pattern detection failed: {str(e)}")
            return False, [{'error': f'Fraud detection error: {str(e)}'}]
    
    def run_validation(self, df: pd.DataFrame, dataset_name: str = "Paytm Transactions") -> QualityReport:
        """
        Complete data quality validation pipeline
        ========================================
        
        All registered rules को execute करके comprehensive report generate करना।
        """
        self.logger.info(f"🔍 Starting data quality validation for {dataset_name}")
        self.logger.info(f"📊 Dataset size: {len(df)} records, {len(df.columns)} columns")
        
        validation_results = []
        validation_start_time = datetime.now()
        
        # Run all validation rules
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_rule = {
                executor.submit(self._execute_validation_rule, rule, df): rule 
                for rule in self.validation_rules
            }
            
            for future in as_completed(future_to_rule):
                rule = future_to_rule[future]
                try:
                    result = future.result()
                    validation_results.append(result)
                    
                    # Log result
                    status = "✅ PASSED" if result.passed else "❌ FAILED"
                    self.logger.info(f"{status} {rule.rule_id}: {rule.rule_name} "
                                   f"(Success Rate: {result.success_rate:.1f}%)")
                    
                except Exception as e:
                    self.logger.error(f"❌ Rule execution failed for {rule.rule_id}: {str(e)}")
                    # Create failed result
                    failed_result = ValidationResult(
                        rule_id=rule.rule_id,
                        rule_name=rule.rule_name,
                        severity=rule.severity,
                        passed=False,
                        failed_records_count=len(df),
                        total_records_count=len(df),
                        error_details=[{'error': f'Rule execution failed: {str(e)}'}],
                        execution_time_ms=0.0
                    )
                    validation_results.append(failed_result)
        
        # Create quality report
        quality_report = QualityReport(
            dataset_name=dataset_name,
            validation_timestamp=validation_start_time,
            total_records=len(df),
            validation_results=validation_results
        )
        
        # Log summary
        self._log_quality_summary(quality_report)
        
        return quality_report
    
    def _execute_validation_rule(self, rule: ValidationRule, df: pd.DataFrame) -> ValidationResult:
        """Single validation rule को execute करना"""
        start_time = time.time()
        
        try:
            # Execute validation function
            passed, error_details = rule.validation_function(df)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Create result
            result = ValidationResult(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                severity=rule.severity,
                passed=passed,
                failed_records_count=len(error_details),
                total_records_count=len(df),
                error_details=error_details,
                execution_time_ms=execution_time
            )
            
            # Add remediation suggestions if failed
            if not passed:
                result.remediation_suggestions = [
                    rule.remediation_hint,
                    f"Business Impact: {rule.business_impact}"
                ]
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.logger.error(f"❌ Rule execution error {rule.rule_id}: {str(e)}")
            
            return ValidationResult(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                severity=rule.severity,
                passed=False,
                failed_records_count=len(df),
                total_records_count=len(df),
                error_details=[{'error': f'Execution failed: {str(e)}'}],
                execution_time_ms=execution_time
            )
    
    def _log_quality_summary(self, report: QualityReport):
        """Quality report का summary logging"""
        self.logger.info("=" * 60)
        self.logger.info("📋 DATA QUALITY SUMMARY REPORT")
        self.logger.info("=" * 60)
        self.logger.info(f"Dataset: {report.dataset_name}")
        self.logger.info(f"Validation Time: {report.validation_timestamp}")
        self.logger.info(f"Total Records: {report.total_records:,}")
        self.logger.info(f"Overall Quality Score: {report.overall_score:.1f}%")
        self.logger.info("")
        self.logger.info("🚨 ISSUES SUMMARY:")
        self.logger.info(f"   Critical Issues: {report.critical_issues}")
        self.logger.info(f"   High Priority: {report.high_issues}")
        self.logger.info(f"   Medium Priority: {report.medium_issues}")
        self.logger.info(f"   Low Priority: {report.low_issues}")
        self.logger.info(f"   Warnings: {report.warnings}")
        self.logger.info("")
        
        if report.critical_issues > 0:
            self.logger.error("🔴 CRITICAL ISSUES FOUND - IMMEDIATE ACTION REQUIRED!")
        elif report.high_issues > 0:
            self.logger.warning("🟡 HIGH PRIORITY ISSUES - REVIEW NEEDED")
        else:
            self.logger.info("✅ NO CRITICAL ISSUES - DATA QUALITY ACCEPTABLE")
    
    def export_quality_report(self, report: QualityReport, output_path: str = None):
        """Quality report को JSON format में export करना"""
        if output_path is None:
            output_path = f"paytm_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            # Convert report to dictionary
            report_dict = {
                'dataset_name': report.dataset_name,
                'validation_timestamp': report.validation_timestamp.isoformat(),
                'total_records': report.total_records,
                'overall_score': report.overall_score,
                'summary': {
                    'critical_issues': report.critical_issues,
                    'high_issues': report.high_issues,
                    'medium_issues': report.medium_issues,
                    'low_issues': report.low_issues,
                    'warnings': report.warnings
                },
                'validation_results': []
            }
            
            for result in report.validation_results:
                result_dict = {
                    'rule_id': result.rule_id,
                    'rule_name': result.rule_name,
                    'severity': result.severity.value,
                    'passed': result.passed,
                    'success_rate': result.success_rate,
                    'failed_records_count': result.failed_records_count,
                    'total_records_count': result.total_records_count,
                    'execution_time_ms': result.execution_time_ms,
                    'error_details': result.error_details[:100],  # Limit to first 100 errors
                    'remediation_suggestions': result.remediation_suggestions
                }
                report_dict['validation_results'].append(result_dict)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📁 Quality report exported to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Report export failed: {str(e)}")

def create_sample_paytm_data() -> pd.DataFrame:
    """
    Sample Paytm transaction data generation
    ======================================
    
    Testing के लिए realistic Paytm transaction data।
    """
    
    import random
    from datetime import datetime, timedelta
    
    # Sample data generation
    sample_data = []
    
    mobile_numbers = ['9876543210', '8765432109', '7654321098', '9123456789', '8234567890']
    merchant_ids = ['MERCHANT_001', 'MERCHANT_002', 'MERCHANT_003']
    
    for i in range(1000):
        # Random transaction data
        transaction_id = f"TXN_{random.randint(100000, 999999)}_{i}"
        payer_mobile = random.choice(mobile_numbers)
        payee_mobile = random.choice(mobile_numbers)
        
        # Ensure no self-transactions in most cases
        while payee_mobile == payer_mobile and random.random() < 0.95:
            payee_mobile = random.choice(mobile_numbers)
        
        amount = random.choice([
            round(random.uniform(1, 100), 2),          # Small amounts
            round(random.uniform(100, 5000), 2),       # Medium amounts  
            round(random.uniform(5000, 50000), 2),     # Large amounts
            50000, 100000, 200000                      # Round amounts (suspicious)
        ])
        
        # Random timestamp within last 30 days
        base_time = datetime.now() - timedelta(days=random.randint(0, 30))
        transaction_timestamp = base_time - timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        transaction_type = random.choice(['P2P', 'P2M', 'WALLET_TOPUP', 'BILL_PAYMENT'])
        payment_method = random.choice(['WALLET', 'UPI', 'DEBIT_CARD', 'CREDIT_CARD'])
        status = random.choice(['SUCCESS', 'SUCCESS', 'SUCCESS', 'FAILED'])  # More success
        
        # Add some data quality issues intentionally for testing
        if random.random() < 0.05:  # 5% bad data
            if random.random() < 0.3:
                amount = -amount  # Negative amount
            elif random.random() < 0.3:
                payer_mobile = "invalid_mobile"  # Invalid mobile
            elif random.random() < 0.3:
                transaction_id = None  # Missing transaction ID
        
        record = {
            'transaction_id': transaction_id,
            'payer_account': payer_mobile,
            'payee_account': payee_mobile,
            'payer_mobile': payer_mobile,
            'payee_mobile': payee_mobile,
            'amount': amount,
            'transaction_timestamp': transaction_timestamp,
            'transaction_type': transaction_type,
            'payment_method': payment_method,
            'status': status,
            'merchant_id': random.choice(merchant_ids) if transaction_type == 'P2M' else None,
            'merchant_category': random.choice(['FOOD', 'SHOPPING', 'TRANSPORT']) if transaction_type == 'P2M' else None,
            'mcc_code': f"{random.randint(1000, 9999)}" if transaction_type == 'P2M' else None,
            'created_at': transaction_timestamp,
            'updated_at': transaction_timestamp + timedelta(seconds=random.randint(1, 300))
        }
        
        sample_data.append(record)
    
    return pd.DataFrame(sample_data)

def main():
    """
    Paytm Data Quality Validation Demo
    =================================
    
    Production-grade data quality validation का demonstration।
    """
    
    print("💳 Paytm Data Quality Validation System")
    print("=" * 50)
    
    # Initialize validator
    validator = PaytmDataQualityValidator()
    
    print(f"✅ Validator initialized with {len(validator.validation_rules)} rules")
    
    # Generate sample data
    print("📊 Generating sample transaction data...")
    sample_data = create_sample_paytm_data()
    print(f"✅ Generated {len(sample_data)} sample transactions")
    
    # Run validation
    print("\n🔍 Running comprehensive data quality validation...")
    quality_report = validator.run_validation(
        df=sample_data,
        dataset_name="Paytm Sample Transactions"
    )
    
    # Export report
    print("\n📁 Exporting quality report...")
    validator.export_quality_report(quality_report, "paytm_quality_report.json")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 VALIDATION COMPLETE!")
    print("=" * 60)
    
    if quality_report.critical_issues == 0:
        print("✅ NO CRITICAL ISSUES - Data ready for processing")
    else:
        print(f"🔴 {quality_report.critical_issues} CRITICAL ISSUES - Fix required before processing")
    
    print(f"📊 Overall Quality Score: {quality_report.overall_score:.1f}%")
    print(f"📁 Detailed report saved to: paytm_quality_report.json")
    
    return quality_report.critical_issues == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


# Production Integration Guide:
"""
🔧 Production Integration - Paytm Scale:

1. **Real-time Validation**:
   - Kafka Streams integration
   - Sub-second validation response
   - Circuit breaker for validation failures
   
2. **Data Quality Dashboard**:
   - Grafana dashboards for quality metrics
   - Real-time alerting on quality degradation
   - Historical quality trends
   
3. **Quality Gates**:
   - ETL pipeline quality checkpoints
   - Automatic data quarantine for failed validation
   - Quality score thresholds for processing

4. **Monitoring & Alerting**:
   - PagerDuty integration for critical issues
   - Slack notifications for quality warnings
   - Quality SLA monitoring (99.9% target)

5. **Data Lineage**:
   - Track quality issues to source systems
   - Impact analysis for downstream systems
   - Automated remediation workflows

6. **Compliance & Audit**:
   - RBI compliance validation rules
   - Audit trail for all quality checks
   - Regulatory reporting capabilities

Quality is King - especially जब paisa की baat हो! 💰✨
"""