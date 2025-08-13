#!/usr/bin/env python3
"""
Privacy Compliance Checker for Indian Data Protection Laws
Episode 47: Data Governance at Scale

GDPR, DPDP Act 2023, और Indian banking compliance के लिए comprehensive
privacy compliance system।

Author: Hindi Podcast Series
Context: Multi-jurisdictional privacy compliance for Indian businesses
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple
import re
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrivacyRegulation(Enum):
    """Privacy regulations supported"""
    GDPR = "GDPR"
    DPDP_ACT = "DPDP_ACT_2023"
    CCPA = "CCPA"
    RBI_GUIDELINES = "RBI_DATA_PROTECTION"

class DataCategory(Enum):
    """Data categories for classification"""
    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    PUBLIC_DATA = "public_data"

class ConsentStatus(Enum):
    """Consent status options"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

@dataclass
class PIIField:
    """PII field definition"""
    field_name: str
    data_category: DataCategory
    required_consent: bool
    retention_days: int
    masking_required: bool
    encryption_required: bool

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    field_name: str
    regulation: PrivacyRegulation
    violation_type: str
    severity: str
    description: str
    recommendation: str
    record_count: int

class IndianPrivacyComplianceChecker:
    """
    Comprehensive privacy compliance checker for Indian businesses
    
    Supports:
    - GDPR compliance for European customers
    - DPDP Act 2023 for Indian customers  
    - RBI guidelines for banking data
    - PCI DSS for payment data
    - Consent management
    - Data retention policies
    """
    
    def __init__(self):
        self.pii_fields = {}
        self.consent_records = {}
        self.violations = []
        self.setup_indian_pii_patterns()
        self.setup_compliance_rules()
    
    def setup_indian_pii_patterns(self):
        """Setup Indian-specific PII detection patterns"""
        self.pii_patterns = {
            # Aadhaar number pattern
            'aadhaar': re.compile(r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b'),
            
            # PAN number pattern
            'pan': re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'),
            
            # Indian mobile number
            'mobile': re.compile(r'(\+91|91)?[6789]\d{9}'),
            
            # Email pattern
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # Credit card pattern
            'credit_card': re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b'),
            
            # Bank account pattern (Indian)
            'bank_account': re.compile(r'\b[0-9]{9,18}\b'),
            
            # IFSC code pattern
            'ifsc': re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b'),
            
            # Vehicle registration
            'vehicle_reg': re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}\b'),
            
            # Passport number
            'passport': re.compile(r'\b[A-Z][0-9]{7}\b')
        }
        
        logger.info("Indian PII patterns initialized")
    
    def setup_compliance_rules(self):
        """Setup compliance rules for different regulations"""
        self.compliance_rules = {
            PrivacyRegulation.GDPR: {
                'consent_required': True,
                'right_to_erasure': True,
                'data_portability': True,
                'privacy_by_design': True,
                'breach_notification_hours': 72,
                'max_retention_days': 365 * 6  # 6 years for most data
            },
            
            PrivacyRegulation.DPDP_ACT: {
                'consent_required': True,
                'purpose_limitation': True,
                'data_minimization': True,
                'storage_limitation': True,
                'notice_and_consent': True,
                'breach_notification_hours': 72,
                'max_retention_days': 365 * 3  # 3 years default
            },
            
            PrivacyRegulation.RBI_GUIDELINES: {
                'data_localization': True,
                'encryption_at_rest': True,
                'encryption_in_transit': True,
                'access_controls': True,
                'audit_logging': True,
                'max_retention_days': 365 * 10  # 10 years for financial data
            }
        }
    
    def register_pii_fields(self, field_definitions: List[PIIField]):
        """Register PII fields with their compliance requirements"""
        for field_def in field_definitions:
            self.pii_fields[field_def.field_name] = field_def
        
        logger.info(f"Registered {len(field_definitions)} PII fields")
    
    def detect_pii_in_text(self, text: str) -> Dict[str, List[str]]:
        """Detect PII patterns in free text"""
        if pd.isna(text) or not isinstance(text, str):
            return {}
        
        detected_pii = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected_pii[pii_type] = matches
        
        return detected_pii
    
    def scan_dataframe_for_pii(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Scan DataFrame for PII across all columns"""
        pii_findings = {}
        
        for column in df.columns:
            column_findings = {
                'detected_patterns': {},
                'sample_values': [],
                'risk_level': 'LOW'
            }
            
            # Sample some values for PII detection
            sample_size = min(1000, len(df))
            sample_data = df[column].dropna().sample(n=min(sample_size, len(df[column].dropna())))
            
            for value in sample_data:
                pii_found = self.detect_pii_in_text(str(value))
                for pii_type, matches in pii_found.items():
                    if pii_type not in column_findings['detected_patterns']:
                        column_findings['detected_patterns'][pii_type] = 0
                    column_findings['detected_patterns'][pii_type] += len(matches)
                    
                    # Store sample for analysis
                    column_findings['sample_values'].extend(matches[:2])  # First 2 matches
            
            # Determine risk level
            if column_findings['detected_patterns']:
                sensitive_patterns = {'aadhaar', 'pan', 'credit_card', 'passport'}
                if any(pattern in sensitive_patterns for pattern in column_findings['detected_patterns']):
                    column_findings['risk_level'] = 'HIGH'
                elif any(pattern in {'mobile', 'email'} for pattern in column_findings['detected_patterns']):
                    column_findings['risk_level'] = 'MEDIUM'
            
            if column_findings['detected_patterns'] or column_findings['risk_level'] != 'LOW':
                pii_findings[column] = column_findings
        
        return pii_findings
    
    def check_consent_compliance(self, df: pd.DataFrame, 
                                consent_column: str = 'consent_status',
                                consent_date_column: str = 'consent_date') -> List[ComplianceViolation]:
        """Check consent compliance for personal data processing"""
        violations = []
        
        if consent_column not in df.columns:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                field_name=consent_column,
                regulation=PrivacyRegulation.GDPR,
                violation_type="MISSING_CONSENT_TRACKING",
                severity="HIGH",
                description="Consent status column missing from dataset",
                recommendation="Implement consent tracking mechanism",
                record_count=len(df)
            ))
            return violations
        
        # Check for missing consent
        missing_consent = df[df[consent_column].isnull()]
        if not missing_consent.empty:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                field_name=consent_column,
                regulation=PrivacyRegulation.DPDP_ACT,
                violation_type="MISSING_CONSENT",
                severity="CRITICAL",
                description=f"Found {len(missing_consent)} records without consent status",
                recommendation="Obtain explicit consent before processing personal data",
                record_count=len(missing_consent)
            ))
        
        # Check for withdrawn consent
        if consent_date_column in df.columns:
            current_date = datetime.now()
            
            # Check for expired consent (older than 2 years)
            df[consent_date_column] = pd.to_datetime(df[consent_date_column], errors='coerce')
            expired_consent = df[
                (df[consent_date_column] < current_date - timedelta(days=730)) &
                (df[consent_column] == 'given')
            ]
            
            if not expired_consent.empty:
                violations.append(ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    field_name=consent_date_column,
                    regulation=PrivacyRegulation.GDPR,
                    violation_type="EXPIRED_CONSENT",
                    severity="MEDIUM",
                    description=f"Found {len(expired_consent)} records with expired consent",
                    recommendation="Re-obtain consent or delete personal data",
                    record_count=len(expired_consent)
                ))
        
        return violations
    
    def check_data_retention_compliance(self, df: pd.DataFrame,
                                      creation_date_column: str = 'created_at') -> List[ComplianceViolation]:
        """Check data retention policy compliance"""
        violations = []
        
        if creation_date_column not in df.columns:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                field_name=creation_date_column,
                regulation=PrivacyRegulation.DPDP_ACT,
                violation_type="MISSING_RETENTION_TRACKING",
                severity="MEDIUM",
                description="Creation date column missing - cannot verify retention compliance",
                recommendation="Add timestamp tracking for all personal data",
                record_count=len(df)
            ))
            return violations
        
        df[creation_date_column] = pd.to_datetime(df[creation_date_column], errors='coerce')
        current_date = datetime.now()
        
        # Check against GDPR retention (6 years)
        gdpr_expired = df[df[creation_date_column] < current_date - timedelta(days=365*6)]
        if not gdpr_expired.empty:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                field_name=creation_date_column,
                regulation=PrivacyRegulation.GDPR,
                violation_type="RETENTION_VIOLATION",
                severity="HIGH",
                description=f"Found {len(gdpr_expired)} records exceeding GDPR retention period",
                recommendation="Delete or anonymize records older than 6 years",
                record_count=len(gdpr_expired)
            ))
        
        # Check against DPDP Act retention (3 years)
        dpdp_expired = df[df[creation_date_column] < current_date - timedelta(days=365*3)]
        if not dpdp_expired.empty:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                field_name=creation_date_column,
                regulation=PrivacyRegulation.DPDP_ACT,
                violation_type="RETENTION_VIOLATION",
                severity="MEDIUM",
                description=f"Found {len(dpdp_expired)} records exceeding DPDP retention period",
                recommendation="Review retention necessity or obtain extended consent",
                record_count=len(dpdp_expired)
            ))
        
        return violations
    
    def check_purpose_limitation(self, df: pd.DataFrame,
                               purpose_column: str = 'processing_purpose') -> List[ComplianceViolation]:
        """Check purpose limitation principle"""
        violations = []
        
        if purpose_column not in df.columns:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                field_name=purpose_column,
                regulation=PrivacyRegulation.DPDP_ACT,
                violation_type="MISSING_PURPOSE_TRACKING",
                severity="HIGH",
                description="Processing purpose not documented for personal data",
                recommendation="Document and track processing purposes for all personal data",
                record_count=len(df)
            ))
            return violations
        
        # Check for vague or missing purposes
        vague_purposes = ['general', 'business', 'analysis', '', None]
        vague_records = df[df[purpose_column].isin(vague_purposes) | df[purpose_column].isnull()]
        
        if not vague_records.empty:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                field_name=purpose_column,
                regulation=PrivacyRegulation.GDPR,
                violation_type="VAGUE_PURPOSE",
                severity="MEDIUM",
                description=f"Found {len(vague_records)} records with vague or missing processing purposes",
                recommendation="Specify clear, legitimate purposes for data processing",
                record_count=len(vague_records)
            ))
        
        return violations
    
    def check_encryption_compliance(self, df: pd.DataFrame,
                                  sensitive_fields: List[str]) -> List[ComplianceViolation]:
        """Check if sensitive data is properly encrypted"""
        violations = []
        
        for field in sensitive_fields:
            if field not in df.columns:
                continue
            
            # Simple check: encrypted data should not contain readable patterns
            sample_values = df[field].dropna().sample(n=min(100, len(df[field].dropna())))
            
            potentially_unencrypted = 0
            for value in sample_values:
                # Check if value contains readable PII patterns
                pii_found = self.detect_pii_in_text(str(value))
                if pii_found:
                    potentially_unencrypted += 1
            
            if potentially_unencrypted > 0:
                violations.append(ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    field_name=field,
                    regulation=PrivacyRegulation.RBI_GUIDELINES,
                    violation_type="UNENCRYPTED_SENSITIVE_DATA",
                    severity="CRITICAL",
                    description=f"Field {field} contains potentially unencrypted sensitive data",
                    recommendation="Implement field-level encryption for sensitive data",
                    record_count=potentially_unencrypted
                ))
        
        return violations
    
    def run_comprehensive_compliance_check(self, df: pd.DataFrame,
                                         config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive privacy compliance check
        
        Args:
            df: DataFrame to check
            config: Configuration dict with columns and requirements
        """
        all_violations = []
        
        logger.info("🔒 शुरू कर रहे हैं privacy compliance assessment")
        
        # PII Detection
        pii_findings = self.scan_dataframe_for_pii(df)
        
        # Consent compliance
        if config.get('check_consent', True):
            consent_violations = self.check_consent_compliance(
                df, 
                config.get('consent_column', 'consent_status'),
                config.get('consent_date_column', 'consent_date')
            )
            all_violations.extend(consent_violations)
        
        # Retention compliance
        if config.get('check_retention', True):
            retention_violations = self.check_data_retention_compliance(
                df,
                config.get('creation_date_column', 'created_at')
            )
            all_violations.extend(retention_violations)
        
        # Purpose limitation
        if config.get('check_purpose', True):
            purpose_violations = self.check_purpose_limitation(
                df,
                config.get('purpose_column', 'processing_purpose')
            )
            all_violations.extend(purpose_violations)
        
        # Encryption compliance
        if config.get('sensitive_fields'):
            encryption_violations = self.check_encryption_compliance(
                df,
                config['sensitive_fields']
            )
            all_violations.extend(encryption_violations)
        
        # Calculate compliance score
        critical_violations = [v for v in all_violations if v.severity == 'CRITICAL']
        high_violations = [v for v in all_violations if v.severity == 'HIGH']
        
        total_violations = len(all_violations)
        compliance_score = max(0, 100 - (len(critical_violations) * 25) - (len(high_violations) * 10))
        
        is_compliant = len(critical_violations) == 0 and len(high_violations) < 3
        
        summary = {
            'compliance_score': compliance_score,
            'is_compliant': is_compliant,
            'total_violations': total_violations,
            'critical_violations': len(critical_violations),
            'high_violations': len(high_violations),
            'pii_findings': pii_findings,
            'violations': all_violations,
            'recommendations': self.generate_recommendations(all_violations)
        }
        
        logger.info(f"Privacy compliance assessment complete. Score: {compliance_score}%")
        
        return summary
    
    def generate_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate actionable recommendations based on violations"""
        recommendations = []
        
        violation_types = {}
        for violation in violations:
            if violation.violation_type not in violation_types:
                violation_types[violation.violation_type] = 0
            violation_types[violation.violation_type] += 1
        
        # Priority recommendations
        if 'UNENCRYPTED_SENSITIVE_DATA' in violation_types:
            recommendations.append("🔐 CRITICAL: Implement field-level encryption for sensitive data immediately")
        
        if 'MISSING_CONSENT' in violation_types:
            recommendations.append("📝 HIGH: Implement consent management system")
        
        if 'RETENTION_VIOLATION' in violation_types:
            recommendations.append("🗓️ MEDIUM: Set up automated data retention policies")
        
        if 'MISSING_PURPOSE_TRACKING' in violation_types:
            recommendations.append("🎯 MEDIUM: Document processing purposes for all data collection")
        
        # General recommendations
        recommendations.extend([
            "📊 Implement regular privacy impact assessments",
            "🔄 Set up automated compliance monitoring",
            "📚 Train staff on data protection regulations",
            "🛡️ Consider Privacy by Design principles in new systems"
        ])
        
        return recommendations[:8]  # Top 8 recommendations
    
    def generate_compliance_report(self, compliance_summary: Dict[str, Any]) -> str:
        """Generate detailed compliance report"""
        report = []
        report.append("=" * 70)
        report.append("PRIVACY COMPLIANCE ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY:")
        report.append(f"Compliance Score: {compliance_summary['compliance_score']}%")
        report.append(f"Overall Status: {'COMPLIANT' if compliance_summary['is_compliant'] else 'NON-COMPLIANT'}")
        report.append(f"Total Violations: {compliance_summary['total_violations']}")
        report.append(f"Critical Issues: {compliance_summary['critical_violations']}")
        report.append(f"High Priority Issues: {compliance_summary['high_violations']}")
        report.append("")
        
        # PII Findings
        if compliance_summary['pii_findings']:
            report.append("PII DETECTION RESULTS:")
            report.append("-" * 30)
            for field, findings in compliance_summary['pii_findings'].items():
                report.append(f"Field: {field}")
                report.append(f"  Risk Level: {findings['risk_level']}")
                if findings['detected_patterns']:
                    report.append(f"  PII Patterns: {list(findings['detected_patterns'].keys())}")
                report.append("")
        
        # Violations
        if compliance_summary['violations']:
            report.append("COMPLIANCE VIOLATIONS:")
            report.append("-" * 30)
            for violation in compliance_summary['violations']:
                report.append(f"[{violation.severity}] {violation.violation_type}")
                report.append(f"  Field: {violation.field_name}")
                report.append(f"  Regulation: {violation.regulation.value}")
                report.append(f"  Description: {violation.description}")
                report.append(f"  Records Affected: {violation.record_count}")
                report.append(f"  Recommendation: {violation.recommendation}")
                report.append("")
        
        # Recommendations
        report.append("RECOMMENDED ACTIONS:")
        report.append("-" * 30)
        for i, recommendation in enumerate(compliance_summary['recommendations'], 1):
            report.append(f"{i}. {recommendation}")
        
        return "\n".join(report)

def create_sample_customer_data():
    """Create sample customer data for testing compliance"""
    data = {
        'customer_id': range(1, 101),
        'name': [f'Customer {i}' for i in range(1, 101)],
        'email': [f'customer{i}@example.com' for i in range(1, 101)],
        'phone': [f'9876543{100+i:03d}' for i in range(1, 101)],
        'aadhaar': [f'12345678{9000+i:04d}' for i in range(1, 101)],
        'pan': [f'ABCDE{1234+i:04d}F' for i in range(1, 101)],
        'created_at': pd.date_range(start='2020-01-01', periods=100, freq='D'),
        'consent_status': ['given'] * 80 + ['withdrawn'] * 10 + [None] * 10,
        'consent_date': pd.date_range(start='2020-01-01', periods=100, freq='D'),
        'processing_purpose': ['customer_service'] * 70 + ['marketing'] * 20 + [None] * 10,
        'salary': np.random.randint(30000, 200000, 100)
    }
    
    # Add some old records for retention testing
    old_dates = pd.date_range(start='2015-01-01', periods=20, freq='M')
    for i in range(20):
        data['created_at'][i] = old_dates[i]
        data['consent_date'][i] = old_dates[i]
    
    return pd.DataFrame(data)

def main():
    """Main function demonstrating privacy compliance checker"""
    print("🔒 Starting Indian Privacy Compliance Checker Demo")
    print("=" * 70)
    
    # Create checker instance
    checker = IndianPrivacyComplianceChecker()
    
    # Create sample data
    df = create_sample_customer_data()
    print("Sample customer data created")
    print(f"Records: {len(df)}")
    print()
    
    # Configuration
    config = {
        'check_consent': True,
        'check_retention': True,
        'check_purpose': True,
        'consent_column': 'consent_status',
        'consent_date_column': 'consent_date',
        'creation_date_column': 'created_at',
        'purpose_column': 'processing_purpose',
        'sensitive_fields': ['aadhaar', 'pan', 'salary']
    }
    
    # Run compliance check
    print("🔍 Running comprehensive privacy compliance check...")
    compliance_summary = checker.run_comprehensive_compliance_check(df, config)
    
    # Generate and print report
    report = checker.generate_compliance_report(compliance_summary)
    print(report)
    
    # Action items
    print("\n🚀 IMMEDIATE ACTION ITEMS:")
    if not compliance_summary['is_compliant']:
        critical_count = compliance_summary['critical_violations']
        high_count = compliance_summary['high_violations']
        
        if critical_count > 0:
            print(f"❌ CRITICAL: {critical_count} critical privacy violations found")
            print("   - Address immediately before processing any data")
        
        if high_count > 0:
            print(f"⚠️ HIGH: {high_count} high priority issues")
            print("   - Create remediation plan within 30 days")
    else:
        print("✅ Privacy compliance standards met")
        print("   - Continue monitoring with regular assessments")

if __name__ == "__main__":
    main()