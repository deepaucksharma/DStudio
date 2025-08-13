#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 16
Compliance Validation Framework

Complete compliance validation framework for regulatory requirements
Regulatory requirements के लिए complete compliance validation framework

Author: DStudio Team
Context: Compliance like RBI, SEBI, GDPR, PCI-DSS requirements
Scale: Handle compliance for 1000+ data processing workflows
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any, Union
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
from enum import Enum
import re
import hashlib
import sqlite3
import uuid
from pathlib import Path

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - अनुपालन जांच - %(message)s'
)
logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"                    # General Data Protection Regulation
    PCI_DSS = "pci_dss"             # Payment Card Industry Data Security Standard
    RBI_GUIDELINES = "rbi"          # Reserve Bank of India Guidelines
    SEBI_REGULATIONS = "sebi"       # Securities and Exchange Board of India
    IT_ACT_2000 = "it_act"          # Information Technology Act 2000
    DPDP_ACT = "dpdp"               # Digital Personal Data Protection Act
    SOX = "sox"                      # Sarbanes-Oxley Act
    HIPAA = "hipaa"                  # Health Insurance Portability and Accountability Act

class ViolationSeverity(Enum):
    """Compliance violation severity levels"""
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"           # Action required within 24 hours
    MEDIUM = "medium"       # Action required within 72 hours
    LOW = "low"            # Action required within 1 week
    INFO = "info"          # Informational only

@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    rule_name: str
    framework: ComplianceFramework
    description: str
    validation_logic: str
    severity: ViolationSeverity
    remediation_steps: List[str]
    legal_reference: str
    penalty_range: str  # In INR for Indian regulations
    data_categories: List[str]  # PII, Financial, Health, etc.
    enabled: bool = True

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    framework: ComplianceFramework
    severity: ViolationSeverity
    description: str
    affected_records: int
    affected_fields: List[str]
    detected_at: datetime
    violation_details: Dict[str, Any]
    remediation_deadline: datetime
    status: str = "open"  # open, in_progress, resolved, waived
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    assessment_date: datetime
    frameworks_assessed: List[ComplianceFramework]
    total_rules_checked: int
    total_violations: int
    violations_by_severity: Dict[str, int]
    compliance_score: float  # Percentage
    risk_level: str
    remediation_timeline: str
    cost_estimate: float  # In INR
    recommendations: List[str]

class ComplianceValidationFramework:
    """
    Complete compliance validation framework for data governance
    Data governance के लिए complete compliance validation framework
    
    Features:
    1. Multi-framework compliance checking (GDPR, RBI, PCI-DSS, etc.)
    2. Automated violation detection and tracking
    3. Risk assessment and remediation planning
    4. Audit trail and reporting
    5. Continuous monitoring and alerting
    6. Indian regulatory compliance focus
    
    Scale: Handle compliance for 1000+ data processing workflows
    """
    
    def __init__(self, config: Dict = None):
        """Initialize compliance validation framework"""
        
        self.config = config or {}
        self.db_path = self.config.get('db_path', 'compliance.db')
        self.db_connection = None
        
        # Compliance rules registry
        self.compliance_rules = {}
        
        # Violation tracking
        self.active_violations = {}
        
        # Framework-specific configurations
        self.framework_configs = {}
        
        # Data classification patterns
        self.data_patterns = {
            'indian_phone': r'^(\+91|91|0)?[6-9]\d{9}$',
            'aadhaar': r'^\d{4}\s?\d{4}\s?\d{4}$',
            'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'credit_card': r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$',
            'ifsc': r'^[A-Z]{4}0[A-Z0-9]{6}$',
            'gstin': r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        }
        
        # Penalty and cost models (in INR)
        self.penalty_models = {
            ComplianceFramework.GDPR: {
                'critical': 20000000,  # 2 crore max penalty
                'high': 5000000,       # 50 lakh
                'medium': 1000000,     # 10 lakh
                'low': 200000          # 2 lakh
            },
            ComplianceFramework.RBI_GUIDELINES: {
                'critical': 10000000,  # 1 crore
                'high': 2500000,       # 25 lakh
                'medium': 500000,      # 5 lakh
                'low': 100000          # 1 lakh
            },
            ComplianceFramework.PCI_DSS: {
                'critical': 5000000,   # 50 lakh
                'high': 1000000,       # 10 lakh
                'medium': 250000,      # 2.5 lakh
                'low': 50000           # 50 thousand
            }
        }
        
        # Initialize database
        self._init_database()
        
        # Load compliance rules
        self._load_default_rules()
        
        logger.info("Compliance Validation Framework initialized - अनुपालन ढांचा तैयार!")

    def _init_database(self):
        """Initialize database for compliance tracking"""
        try:
            self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Compliance rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_rules (
                    rule_id TEXT PRIMARY KEY,
                    rule_name TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    description TEXT,
                    validation_logic TEXT,
                    severity TEXT,
                    remediation_steps TEXT,
                    legal_reference TEXT,
                    penalty_range TEXT,
                    data_categories TEXT,
                    enabled BOOLEAN,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            ''')
            
            # Compliance violations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_violations (
                    violation_id TEXT PRIMARY KEY,
                    rule_id TEXT,
                    framework TEXT,
                    severity TEXT,
                    description TEXT,
                    affected_records INTEGER,
                    affected_fields TEXT,
                    detected_at DATETIME,
                    violation_details TEXT,
                    remediation_deadline DATETIME,
                    status TEXT,
                    assigned_to TEXT,
                    resolution_notes TEXT,
                    resolved_at DATETIME,
                    FOREIGN KEY (rule_id) REFERENCES compliance_rules(rule_id)
                )
            ''')
            
            # Compliance assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    assessment_date DATETIME,
                    frameworks_assessed TEXT,
                    total_rules_checked INTEGER,
                    total_violations INTEGER,
                    violations_by_severity TEXT,
                    compliance_score REAL,
                    risk_level TEXT,
                    remediation_timeline TEXT,
                    cost_estimate REAL,
                    recommendations TEXT,
                    report_json TEXT
                )
            ''')
            
            # Audit trail table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_trail (
                    audit_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    entity_type TEXT,
                    entity_id TEXT,
                    user_id TEXT,
                    action TEXT,
                    old_values TEXT,
                    new_values TEXT,
                    timestamp DATETIME,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Compliance database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _load_default_rules(self):
        """Load default compliance rules for Indian context"""
        
        default_rules = [
            # GDPR Rules
            ComplianceRule(
                rule_id='gdpr_001',
                rule_name='Personal Data Encryption',
                framework=ComplianceFramework.GDPR,
                description='Personal data must be encrypted at rest and in transit',
                validation_logic='check_encryption_status',
                severity=ViolationSeverity.CRITICAL,
                remediation_steps=[
                    'Implement AES-256 encryption for personal data',
                    'Enable TLS 1.3 for data in transit',
                    'Regular encryption key rotation'
                ],
                legal_reference='GDPR Article 32 - Security of Processing',
                penalty_range='Up to 4% of annual global turnover or €20 million',
                data_categories=['PII', 'Personal Data']
            ),
            
            ComplianceRule(
                rule_id='gdpr_002',
                rule_name='Data Retention Limits',
                framework=ComplianceFramework.GDPR,
                description='Personal data must not be retained beyond necessary period',
                validation_logic='check_data_retention',
                severity=ViolationSeverity.HIGH,
                remediation_steps=[
                    'Implement automated data purging',
                    'Define data retention policies',
                    'Regular compliance audits'
                ],
                legal_reference='GDPR Article 5(1)(e) - Storage Limitation',
                penalty_range='Up to 2% of annual global turnover or €10 million',
                data_categories=['PII', 'Personal Data']
            ),
            
            # RBI Guidelines
            ComplianceRule(
                rule_id='rbi_001',
                rule_name='Financial Data Localization',
                framework=ComplianceFramework.RBI_GUIDELINES,
                description='Payment system data must be stored in India',
                validation_logic='check_data_location',
                severity=ViolationSeverity.CRITICAL,
                remediation_steps=[
                    'Migrate data to Indian data centers',
                    'Implement data residency controls',
                    'Regular location compliance audits'
                ],
                legal_reference='RBI Circular on Storage of Payment System Data',
                penalty_range='Up to ₹1 crore or license cancellation',
                data_categories=['Financial', 'Payment Data']
            ),
            
            ComplianceRule(
                rule_id='rbi_002',
                rule_name='Know Your Customer (KYC) Data Protection',
                framework=ComplianceFramework.RBI_GUIDELINES,
                description='KYC data must be protected with appropriate security measures',
                validation_logic='check_kyc_security',
                severity=ViolationSeverity.HIGH,
                remediation_steps=[
                    'Implement multi-factor authentication',
                    'Regular security assessments',
                    'Employee training on KYC handling'
                ],
                legal_reference='RBI Master Direction on KYC',
                penalty_range='Up to ₹25 lakh per violation',
                data_categories=['KYC', 'Financial']
            ),
            
            # PCI DSS Rules
            ComplianceRule(
                rule_id='pci_001',
                rule_name='Credit Card Data Encryption',
                framework=ComplianceFramework.PCI_DSS,
                description='Cardholder data must be encrypted using strong cryptography',
                validation_logic='check_card_encryption',
                severity=ViolationSeverity.CRITICAL,
                remediation_steps=[
                    'Implement strong encryption algorithms',
                    'Secure key management practices',
                    'Regular vulnerability assessments'
                ],
                legal_reference='PCI DSS Requirement 3 - Protect Stored Cardholder Data',
                penalty_range='Up to ₹50 lakh in fines plus card brand penalties',
                data_categories=['Credit Card', 'Payment Data']
            ),
            
            # IT Act 2000
            ComplianceRule(
                rule_id='it_act_001',
                rule_name='Data Breach Notification',
                framework=ComplianceFramework.IT_ACT_2000,
                description='Data breaches must be reported within 72 hours',
                validation_logic='check_breach_notification',
                severity=ViolationSeverity.HIGH,
                remediation_steps=[
                    'Implement breach detection systems',
                    'Define incident response procedures',
                    'Regular security monitoring'
                ],
                legal_reference='IT Act 2000 Section 72A - Disclosure of Information',
                penalty_range='Up to ₹5 crore in compensation',
                data_categories=['All Data Types']
            ),
            
            # DPDP Act (Digital Personal Data Protection Act)
            ComplianceRule(
                rule_id='dpdp_001',
                rule_name='Consent Management',
                framework=ComplianceFramework.DPDP_ACT,
                description='Valid consent required for personal data processing',
                validation_logic='check_consent_records',
                severity=ViolationSeverity.CRITICAL,
                remediation_steps=[
                    'Implement consent management platform',
                    'Maintain consent records',
                    'Provide easy consent withdrawal'
                ],
                legal_reference='DPDP Act 2023 Section 6 - Grounds for Processing',
                penalty_range='Up to ₹250 crore per violation',
                data_categories=['Personal Data', 'PII']
            )
        ]
        
        # Register all default rules
        for rule in default_rules:
            self.register_compliance_rule(rule)

    def register_compliance_rule(self, rule: ComplianceRule) -> bool:
        """
        Register a new compliance rule
        नया compliance rule register करना
        """
        try:
            # Add to memory
            self.compliance_rules[rule.rule_id] = rule
            
            # Store in database
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO compliance_rules
                    (rule_id, rule_name, framework, description, validation_logic,
                     severity, remediation_steps, legal_reference, penalty_range,
                     data_categories, enabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rule.rule_id,
                    rule.rule_name,
                    rule.framework.value,
                    rule.description,
                    rule.validation_logic,
                    rule.severity.value,
                    json.dumps(rule.remediation_steps),
                    rule.legal_reference,
                    rule.penalty_range,
                    json.dumps(rule.data_categories),
                    rule.enabled,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                self.db_connection.commit()
            
            logger.info(f"Registered compliance rule: {rule.rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register compliance rule: {e}")
            return False

    def classify_data_fields(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Classify data fields based on data types and patterns
        Data fields को type और patterns के basis पर classify करना
        """
        
        classification = defaultdict(list)
        
        for column in df.columns:
            sample_values = df[column].dropna().astype(str).head(100)
            
            # Check for PII patterns
            if any(re.match(self.data_patterns['email'], str(val)) for val in sample_values):
                classification['email'].append(column)
                classification['PII'].append(column)
            
            if any(re.match(self.data_patterns['indian_phone'], str(val)) for val in sample_values):
                classification['phone'].append(column)
                classification['PII'].append(column)
            
            if any(re.match(self.data_patterns['aadhaar'], str(val)) for val in sample_values):
                classification['aadhaar'].append(column)
                classification['PII'].append(column)
                classification['KYC'].append(column)
            
            if any(re.match(self.data_patterns['pan'], str(val)) for val in sample_values):
                classification['pan'].append(column)
                classification['PII'].append(column)
                classification['KYC'].append(column)
            
            if any(re.match(self.data_patterns['credit_card'], str(val)) for val in sample_values):
                classification['credit_card'].append(column)
                classification['Financial'].append(column)
                classification['Payment Data'].append(column)
            
            if any(re.match(self.data_patterns['ifsc'], str(val)) for val in sample_values):
                classification['ifsc'].append(column)
                classification['Financial'].append(column)
            
            # Check for common field names
            column_lower = column.lower()
            if any(keyword in column_lower for keyword in ['name', 'firstname', 'lastname']):
                classification['PII'].append(column)
            
            if any(keyword in column_lower for keyword in ['address', 'location', 'city', 'state']):
                classification['PII'].append(column)
            
            if any(keyword in column_lower for keyword in ['salary', 'income', 'amount', 'balance']):
                classification['Financial'].append(column)
            
            if any(keyword in column_lower for keyword in ['password', 'secret', 'key', 'token']):
                classification['Sensitive'].append(column)
        
        return dict(classification)

    def validate_framework_compliance(self, df: pd.DataFrame, 
                                    framework: ComplianceFramework,
                                    data_context: Dict = None) -> List[ComplianceViolation]:
        """
        Validate data against specific compliance framework
        Specific compliance framework के against data validate करना
        """
        
        violations = []
        data_classification = self.classify_data_fields(df)
        
        # Get rules for this framework
        framework_rules = [rule for rule in self.compliance_rules.values() 
                          if rule.framework == framework and rule.enabled]
        
        for rule in framework_rules:
            try:
                violation = self._check_rule_compliance(rule, df, data_classification, data_context)
                if violation:
                    violations.append(violation)
            except Exception as e:
                logger.error(f"Error checking rule {rule.rule_id}: {e}")
        
        return violations

    def _check_rule_compliance(self, rule: ComplianceRule, df: pd.DataFrame,
                             data_classification: Dict, context: Dict = None) -> Optional[ComplianceViolation]:
        """Check compliance for a specific rule"""
        
        context = context or {}
        
        # Rule-specific validation logic
        if rule.validation_logic == 'check_encryption_status':
            return self._check_encryption_compliance(rule, df, data_classification)
        
        elif rule.validation_logic == 'check_data_retention':
            return self._check_retention_compliance(rule, df, context)
        
        elif rule.validation_logic == 'check_data_location':
            return self._check_location_compliance(rule, df, context)
        
        elif rule.validation_logic == 'check_kyc_security':
            return self._check_kyc_compliance(rule, df, data_classification)
        
        elif rule.validation_logic == 'check_card_encryption':
            return self._check_card_data_compliance(rule, df, data_classification)
        
        elif rule.validation_logic == 'check_consent_records':
            return self._check_consent_compliance(rule, df, context)
        
        elif rule.validation_logic == 'check_breach_notification':
            return self._check_breach_notification_compliance(rule, context)
        
        return None

    def _check_encryption_compliance(self, rule: ComplianceRule, df: pd.DataFrame,
                                   data_classification: Dict) -> Optional[ComplianceViolation]:
        """Check encryption compliance for personal data"""
        
        pii_fields = data_classification.get('PII', [])
        
        if not pii_fields:
            return None
        
        # Check if PII fields appear to be encrypted (simplified check)
        unencrypted_fields = []
        for field in pii_fields:
            if field in df.columns:
                # Simple heuristic: encrypted data should not match common patterns
                sample_values = df[field].dropna().astype(str).head(100)
                
                # If values match PII patterns, they're likely not encrypted
                if field in data_classification.get('email', []):
                    if any(re.match(self.data_patterns['email'], val) for val in sample_values):
                        unencrypted_fields.append(field)
                
                elif field in data_classification.get('phone', []):
                    if any(re.match(self.data_patterns['indian_phone'], val) for val in sample_values):
                        unencrypted_fields.append(field)
        
        if unencrypted_fields:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                framework=rule.framework,
                severity=rule.severity,
                description=f"Unencrypted personal data found in fields: {', '.join(unencrypted_fields)}",
                affected_records=len(df),
                affected_fields=unencrypted_fields,
                detected_at=datetime.now(),
                violation_details={
                    'unencrypted_fields': unencrypted_fields,
                    'total_records': len(df),
                    'recommendation': 'Implement field-level encryption for PII data'
                },
                remediation_deadline=datetime.now() + timedelta(days=7)
            )
        
        return None

    def _check_retention_compliance(self, rule: ComplianceRule, df: pd.DataFrame,
                                  context: Dict) -> Optional[ComplianceViolation]:
        """Check data retention compliance"""
        
        # Check for timestamp fields
        timestamp_fields = []
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower() or 'created' in col.lower():
                timestamp_fields.append(col)
        
        if not timestamp_fields:
            return None
        
        # Check retention policy (example: 7 years for financial data)
        retention_limit = context.get('retention_days', 2555)  # 7 years default
        cutoff_date = datetime.now() - timedelta(days=retention_limit)
        
        old_records = 0
        for field in timestamp_fields:
            try:
                timestamps = pd.to_datetime(df[field], errors='coerce')
                old_records += (timestamps < cutoff_date).sum()
            except:
                continue
        
        if old_records > 0:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                framework=rule.framework,
                severity=rule.severity,
                description=f"Found {old_records} records exceeding retention period",
                affected_records=old_records,
                affected_fields=timestamp_fields,
                detected_at=datetime.now(),
                violation_details={
                    'retention_limit_days': retention_limit,
                    'cutoff_date': cutoff_date.isoformat(),
                    'old_records_count': old_records
                },
                remediation_deadline=datetime.now() + timedelta(days=30)
            )
        
        return None

    def _check_location_compliance(self, rule: ComplianceRule, df: pd.DataFrame,
                                 context: Dict) -> Optional[ComplianceViolation]:
        """Check data location compliance (simplified)"""
        
        # This would normally check actual data location through infrastructure APIs
        data_location = context.get('data_location', 'unknown')
        
        if rule.framework == ComplianceFramework.RBI_GUIDELINES:
            if data_location not in ['india', 'IN']:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    framework=rule.framework,
                    severity=rule.severity,
                    description=f"Financial data stored outside India: {data_location}",
                    affected_records=len(df),
                    affected_fields=['all'],
                    detected_at=datetime.now(),
                    violation_details={
                        'current_location': data_location,
                        'required_location': 'India',
                        'total_records': len(df)
                    },
                    remediation_deadline=datetime.now() + timedelta(days=90)
                )
        
        return None

    def _check_kyc_compliance(self, rule: ComplianceRule, df: pd.DataFrame,
                            data_classification: Dict) -> Optional[ComplianceViolation]:
        """Check KYC data security compliance"""
        
        kyc_fields = data_classification.get('KYC', [])
        
        if not kyc_fields:
            return None
        
        # Check for common KYC security issues
        issues = []
        
        # Check if KYC data is masked properly
        for field in kyc_fields:
            if field in df.columns:
                sample_values = df[field].dropna().astype(str).head(100)
                
                # Check if Aadhaar numbers are not masked
                if field in data_classification.get('aadhaar', []):
                    unmasked_count = sum(1 for val in sample_values 
                                       if re.match(r'^\d{12}$', val.replace(' ', '')))
                    if unmasked_count > 0:
                        issues.append(f"Unmasked Aadhaar numbers in {field}")
                
                # Check if PAN numbers are exposed
                if field in data_classification.get('pan', []):
                    exposed_count = sum(1 for val in sample_values 
                                      if re.match(self.data_patterns['pan'], val))
                    if exposed_count > 0:
                        issues.append(f"Exposed PAN numbers in {field}")
        
        if issues:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                framework=rule.framework,
                severity=rule.severity,
                description=f"KYC security violations: {'; '.join(issues)}",
                affected_records=len(df),
                affected_fields=kyc_fields,
                detected_at=datetime.now(),
                violation_details={
                    'security_issues': issues,
                    'kyc_fields': kyc_fields,
                    'recommendation': 'Implement proper KYC data masking and access controls'
                },
                remediation_deadline=datetime.now() + timedelta(days=14)
            )
        
        return None

    def _check_card_data_compliance(self, rule: ComplianceRule, df: pd.DataFrame,
                                  data_classification: Dict) -> Optional[ComplianceViolation]:
        """Check credit card data compliance"""
        
        card_fields = data_classification.get('credit_card', [])
        
        if not card_fields:
            return None
        
        # Check if credit card numbers are stored in plain text
        violations = []
        for field in card_fields:
            if field in df.columns:
                sample_values = df[field].dropna().astype(str).head(100)
                
                # Check for unencrypted credit card numbers
                plain_text_cards = sum(1 for val in sample_values 
                                     if re.match(self.data_patterns['credit_card'], val.replace(' ', '')))
                
                if plain_text_cards > 0:
                    violations.append(f"Plain text credit card numbers in {field}")
        
        if violations:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                framework=rule.framework,
                severity=rule.severity,
                description=f"PCI DSS violations: {'; '.join(violations)}",
                affected_records=len(df),
                affected_fields=card_fields,
                detected_at=datetime.now(),
                violation_details={
                    'pci_violations': violations,
                    'card_fields': card_fields,
                    'recommendation': 'Implement strong encryption for cardholder data'
                },
                remediation_deadline=datetime.now() + timedelta(days=3)
            )
        
        return None

    def _check_consent_compliance(self, rule: ComplianceRule, df: pd.DataFrame,
                                context: Dict) -> Optional[ComplianceViolation]:
        """Check consent management compliance"""
        
        # Check if consent records exist
        consent_fields = [col for col in df.columns if 'consent' in col.lower()]
        
        if not consent_fields:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                framework=rule.framework,
                severity=rule.severity,
                description="No consent records found for personal data processing",
                affected_records=len(df),
                affected_fields=['consent_missing'],
                detected_at=datetime.now(),
                violation_details={
                    'issue': 'Missing consent records',
                    'total_records': len(df),
                    'recommendation': 'Implement consent management system'
                },
                remediation_deadline=datetime.now() + timedelta(days=30)
            )
        
        return None

    def _check_breach_notification_compliance(self, rule: ComplianceRule,
                                            context: Dict) -> Optional[ComplianceViolation]:
        """Check breach notification compliance"""
        
        # This would check actual breach notification logs
        last_breach = context.get('last_breach_date')
        notification_sent = context.get('notification_sent', False)
        
        if last_breach and not notification_sent:
            breach_date = datetime.fromisoformat(last_breach)
            hours_since_breach = (datetime.now() - breach_date).total_seconds() / 3600
            
            if hours_since_breach > 72:  # 72 hour notification requirement
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    framework=rule.framework,
                    severity=rule.severity,
                    description=f"Breach notification overdue by {hours_since_breach - 72:.1f} hours",
                    affected_records=0,
                    affected_fields=['notification'],
                    detected_at=datetime.now(),
                    violation_details={
                        'breach_date': last_breach,
                        'hours_overdue': hours_since_breach - 72,
                        'notification_sent': notification_sent
                    },
                    remediation_deadline=datetime.now() + timedelta(hours=1)
                )
        
        return None

    def comprehensive_compliance_assessment(self, df: pd.DataFrame,
                                          frameworks: List[ComplianceFramework],
                                          context: Dict = None) -> ComplianceReport:
        """
        Perform comprehensive compliance assessment
        Comprehensive compliance assessment करना
        """
        
        all_violations = []
        total_rules_checked = 0
        
        # Check each framework
        for framework in frameworks:
            framework_violations = self.validate_framework_compliance(df, framework, context)
            all_violations.extend(framework_violations)
            
            framework_rules = [rule for rule in self.compliance_rules.values() 
                             if rule.framework == framework and rule.enabled]
            total_rules_checked += len(framework_rules)
        
        # Calculate metrics
        violations_by_severity = Counter(v.severity.value for v in all_violations)
        
        # Calculate compliance score
        total_possible_violations = total_rules_checked
        actual_violations = len(all_violations)
        compliance_score = ((total_possible_violations - actual_violations) / 
                          total_possible_violations * 100) if total_possible_violations > 0 else 100
        
        # Determine risk level
        critical_violations = violations_by_severity.get('critical', 0)
        high_violations = violations_by_severity.get('high', 0)
        
        if critical_violations > 0:
            risk_level = 'CRITICAL'
        elif high_violations > 2:
            risk_level = 'HIGH'
        elif high_violations > 0 or violations_by_severity.get('medium', 0) > 3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Estimate remediation timeline
        max_days = 0
        for violation in all_violations:
            days_to_deadline = (violation.remediation_deadline - datetime.now()).days
            max_days = max(max_days, days_to_deadline)
        
        if max_days <= 7:
            remediation_timeline = 'Within 1 week'
        elif max_days <= 30:
            remediation_timeline = 'Within 1 month'
        elif max_days <= 90:
            remediation_timeline = 'Within 3 months'
        else:
            remediation_timeline = 'More than 3 months'
        
        # Estimate cost impact
        cost_estimate = self._calculate_violation_cost(all_violations)
        
        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(all_violations, frameworks)
        
        # Create report
        report = ComplianceReport(
            report_id=str(uuid.uuid4()),
            assessment_date=datetime.now(),
            frameworks_assessed=frameworks,
            total_rules_checked=total_rules_checked,
            total_violations=len(all_violations),
            violations_by_severity=dict(violations_by_severity),
            compliance_score=compliance_score,
            risk_level=risk_level,
            remediation_timeline=remediation_timeline,
            cost_estimate=cost_estimate,
            recommendations=recommendations
        )
        
        # Store violations and report
        for violation in all_violations:
            self._store_violation(violation)
        
        self._store_assessment_report(report)
        
        return report

    def _calculate_violation_cost(self, violations: List[ComplianceViolation]) -> float:
        """Calculate estimated cost impact of violations"""
        
        total_cost = 0
        
        for violation in violations:
            framework_penalties = self.penalty_models.get(violation.framework, {})
            penalty_amount = framework_penalties.get(violation.severity.value, 100000)
            total_cost += penalty_amount
        
        return total_cost

    def _generate_compliance_recommendations(self, violations: List[ComplianceViolation],
                                           frameworks: List[ComplianceFramework]) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        # Framework-specific recommendations
        if ComplianceFramework.GDPR in frameworks:
            recommendations.append("Implement comprehensive data protection impact assessments")
            recommendations.append("Establish data processing agreements with all vendors")
        
        if ComplianceFramework.RBI_GUIDELINES in frameworks:
            recommendations.append("Ensure all payment data is stored within India")
            recommendations.append("Implement strong customer authentication mechanisms")
        
        if ComplianceFramework.PCI_DSS in frameworks:
            recommendations.append("Implement end-to-end encryption for payment card data")
            recommendations.append("Regular penetration testing and vulnerability assessments")
        
        # Violation-specific recommendations
        critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        if critical_violations:
            recommendations.append("Address critical violations immediately - business operations at risk")
        
        high_violations = [v for v in violations if v.severity == ViolationSeverity.HIGH]
        if len(high_violations) > 3:
            recommendations.append("Multiple high-severity issues detected - implement urgent remediation plan")
        
        # General recommendations
        recommendations.extend([
            "Implement continuous compliance monitoring",
            "Regular compliance training for all employees",
            "Establish data governance committee",
            "Regular third-party compliance audits"
        ])
        
        return recommendations

    def _store_violation(self, violation: ComplianceViolation):
        """Store violation in database"""
        try:
            if not self.db_connection:
                return
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO compliance_violations
                (violation_id, rule_id, framework, severity, description,
                 affected_records, affected_fields, detected_at, violation_details,
                 remediation_deadline, status, assigned_to, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                violation.violation_id,
                violation.rule_id,
                violation.framework.value,
                violation.severity.value,
                violation.description,
                violation.affected_records,
                json.dumps(violation.affected_fields),
                violation.detected_at.isoformat(),
                json.dumps(violation.violation_details),
                violation.remediation_deadline.isoformat(),
                violation.status,
                violation.assigned_to,
                violation.resolution_notes
            ))
            self.db_connection.commit()
        except Exception as e:
            logger.error(f"Failed to store violation: {e}")

    def _store_assessment_report(self, report: ComplianceReport):
        """Store assessment report in database"""
        try:
            if not self.db_connection:
                return
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO compliance_assessments
                (assessment_id, assessment_date, frameworks_assessed, total_rules_checked,
                 total_violations, violations_by_severity, compliance_score, risk_level,
                 remediation_timeline, cost_estimate, recommendations, report_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id,
                report.assessment_date.isoformat(),
                json.dumps([f.value for f in report.frameworks_assessed]),
                report.total_rules_checked,
                report.total_violations,
                json.dumps(report.violations_by_severity),
                report.compliance_score,
                report.risk_level,
                report.remediation_timeline,
                report.cost_estimate,
                json.dumps(report.recommendations),
                json.dumps(asdict(report), default=str)
            ))
            self.db_connection.commit()
        except Exception as e:
            logger.error(f"Failed to store assessment report: {e}")

def create_sample_compliance_data() -> Tuple[pd.DataFrame, Dict]:
    """Create sample data for compliance testing"""
    
    # Sample Indian e-commerce customer data with compliance issues
    np.random.seed(42)
    
    # Generate sample data with various compliance issues
    data = {
        'customer_id': [f'CUST-{i:06d}' for i in range(1, 1001)],
        'full_name': [f'Customer {i}' for i in range(1, 1001)],
        'email': [f'customer{i}@example.com' for i in range(1, 1001)],
        'phone': [f'+91{np.random.randint(6000000000, 9999999999)}' for _ in range(1000)],
        'aadhaar': [f'{np.random.randint(100000000000, 999999999999):012d}' for _ in range(1000)],  # Unmasked!
        'pan': [f'{chr(65+np.random.randint(0,26))}{chr(65+np.random.randint(0,26))}{chr(65+np.random.randint(0,26))}{chr(65+np.random.randint(0,26))}{chr(65+np.random.randint(0,26))}{np.random.randint(1000,9999)}{chr(65+np.random.randint(0,26))}' for _ in range(1000)],
        'credit_card': [f'4{np.random.randint(100000000000000, 999999999999999):015d}' for _ in range(1000)],  # Plain text!
        'salary': np.random.normal(50000, 20000, 1000),
        'account_created': pd.date_range('2015-01-01', '2024-12-31', periods=1000),
        'last_login': pd.date_range('2020-01-01', '2024-12-31', periods=1000),
        'consent_marketing': np.random.choice([True, False], 1000),
        'data_location': ['singapore'] * 1000  # RBI violation!
    }
    
    df = pd.DataFrame(data)
    
    # Add some very old records (retention violation)
    old_dates = pd.date_range('2010-01-01', '2015-01-01', periods=50)
    df.loc[:49, 'account_created'] = old_dates
    
    # Remove consent for some records (GDPR/DPDP violation)
    df.loc[900:, 'consent_marketing'] = None
    
    # Context for compliance checking
    context = {
        'data_location': 'singapore',  # Should be India for financial data
        'retention_days': 2555,  # 7 years
        'last_breach_date': '2024-12-01T10:00:00',
        'notification_sent': False,  # Breach notification violation
        'encryption_enabled': False  # Encryption violation
    }
    
    return df, context

def main():
    """Main execution function - demo of compliance validation framework"""
    
    print("⚖️ Compliance Validation Framework Demo")
    print("अनुपालन सत्यापन ढांचे का प्रदर्शन\n")
    
    # Initialize framework
    framework = ComplianceValidationFramework()
    
    # Test 1: Data classification
    print("Test 1: Data Field Classification")
    print("=" * 35)
    
    sample_df, context = create_sample_compliance_data()
    data_classification = framework.classify_data_fields(sample_df)
    
    print("Data Classification Results:")
    for category, fields in data_classification.items():
        print(f"  {category}: {fields}")
    
    # Test 2: Individual framework compliance
    print("\nTest 2: Individual Framework Compliance Testing")
    print("=" * 50)
    
    # Test GDPR compliance
    gdpr_violations = framework.validate_framework_compliance(
        sample_df, ComplianceFramework.GDPR, context
    )
    
    print(f"GDPR Violations Found: {len(gdpr_violations)}")
    for violation in gdpr_violations:
        print(f"  - {violation.description} (Severity: {violation.severity.value})")
    
    # Test RBI compliance
    rbi_violations = framework.validate_framework_compliance(
        sample_df, ComplianceFramework.RBI_GUIDELINES, context
    )
    
    print(f"\nRBI Violations Found: {len(rbi_violations)}")
    for violation in rbi_violations:
        print(f"  - {violation.description} (Severity: {violation.severity.value})")
    
    # Test PCI DSS compliance
    pci_violations = framework.validate_framework_compliance(
        sample_df, ComplianceFramework.PCI_DSS, context
    )
    
    print(f"\nPCI DSS Violations Found: {len(pci_violations)}")
    for violation in pci_violations:
        print(f"  - {violation.description} (Severity: {violation.severity.value})")
    
    # Test 3: Comprehensive compliance assessment
    print("\nTest 3: Comprehensive Compliance Assessment")
    print("=" * 45)
    
    frameworks_to_test = [
        ComplianceFramework.GDPR,
        ComplianceFramework.RBI_GUIDELINES,
        ComplianceFramework.PCI_DSS,
        ComplianceFramework.DPDP_ACT
    ]
    
    report = framework.comprehensive_compliance_assessment(
        sample_df, frameworks_to_test, context
    )
    
    print(f"""
    Comprehensive Compliance Report:
    ===============================
    Assessment Date: {report.assessment_date.strftime('%Y-%m-%d %H:%M:%S')}
    Frameworks Assessed: {[f.value for f in report.frameworks_assessed]}
    
    Results:
    --------
    Total Rules Checked: {report.total_rules_checked}
    Total Violations: {report.total_violations}
    Compliance Score: {report.compliance_score:.1f}%
    Risk Level: {report.risk_level}
    
    Violations by Severity:
    {json.dumps(report.violations_by_severity, indent=2)}
    
    Cost Impact Estimate: ₹{report.cost_estimate:,.2f}
    Remediation Timeline: {report.remediation_timeline}
    
    Key Recommendations:
    {chr(10).join(['- ' + rec for rec in report.recommendations[:5]])}
    """)
    
    # Test 4: Rule registration
    print("\nTest 4: Custom Rule Registration")
    print("=" * 35)
    
    # Add custom rule for Indian context
    custom_rule = ComplianceRule(
        rule_id='custom_001',
        rule_name='GST Number Validation',
        framework=ComplianceFramework.IT_ACT_2000,
        description='GST numbers must be validated and formatted correctly',
        validation_logic='check_gst_format',
        severity=ViolationSeverity.MEDIUM,
        remediation_steps=[
            'Validate GST number format',
            'Implement GST verification API',
            'Add data quality checks'
        ],
        legal_reference='GST Act Section 25 - Registration Requirements',
        penalty_range='Up to ₹10,000 per incorrect GST record',
        data_categories=['Tax Data', 'Business Data']
    )
    
    success = framework.register_compliance_rule(custom_rule)
    print(f"Custom rule registration: {'✅ Success' if success else '❌ Failed'}")
    print(f"Total rules in framework: {len(framework.compliance_rules)}")
    
    # Test 5: Cost analysis
    print("\nTest 5: Compliance Cost Analysis")
    print("=" * 35)
    
    total_potential_cost = 0
    for framework_name, penalties in framework.penalty_models.items():
        framework_cost = sum(penalties.values())
        total_potential_cost += framework_cost
        print(f"{framework_name.value.upper()} Maximum Penalties: ₹{framework_cost:,}")
    
    print(f"\nTotal Potential Compliance Cost: ₹{total_potential_cost:,}")
    print(f"Current Assessment Risk: ₹{report.cost_estimate:,}")
    print(f"Risk Mitigation Savings: ₹{total_potential_cost - report.cost_estimate:,}")
    
    # Test 6: Framework coverage analysis
    print("\nTest 6: Framework Coverage Analysis")
    print("=" * 35)
    
    framework_rules = defaultdict(int)
    for rule in framework.compliance_rules.values():
        framework_rules[rule.framework.value] += 1
    
    print("Rules by Framework:")
    for framework_name, count in framework_rules.items():
        print(f"  {framework_name.upper()}: {count} rules")
    
    print(f"\nTotal Compliance Rules: {len(framework.compliance_rules)}")
    print(f"Active Rules: {sum(1 for r in framework.compliance_rules.values() if r.enabled)}")
    
    print("\n✅ Compliance Validation Framework Demo Complete!")
    print("Regulatory compliance system ready - नियामक अनुपालन सिस्टम तैयार!")
    
    return {
        'compliance_report': report,
        'total_violations': report.total_violations,
        'compliance_score': report.compliance_score,
        'cost_estimate': report.cost_estimate
    }

if __name__ == "__main__":
    results = main()