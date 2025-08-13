#!/usr/bin/env python3
"""
DataOps Example 07: Compliance Automation for Indian Regulations
Automated compliance checking for RBI, SEBI, IT Act regulations
Focus: Data localization, audit trails, privacy compliance

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json
import hashlib
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceChecker:
    """Compliance automation for Indian regulations"""
    
    def __init__(self, company_type: str):
        self.company_type = company_type  # 'bank', 'fintech', 'ecommerce', 'healthcare'
        self.regulations = self.get_applicable_regulations()
        
    def get_applicable_regulations(self) -> List[str]:
        """Get applicable regulations based on company type"""
        base_regulations = ['IT_Act_2000', 'DPDP_Act_2023', 'Data_Localization']
        
        if self.company_type == 'bank':
            return base_regulations + ['RBI_Guidelines', 'Banking_Regulation_Act', 'PCI_DSS']
        elif self.company_type == 'fintech':
            return base_regulations + ['RBI_Guidelines', 'UPI_Guidelines', 'NPCI_Standards']
        elif self.company_type == 'ecommerce':
            return base_regulations + ['Consumer_Protection_Act', 'FDI_Policy']
        elif self.company_type == 'healthcare':
            return base_regulations + ['Clinical_Establishment_Act', 'Drugs_Rules']
        else:
            return base_regulations
    
    def check_data_localization(self, data_locations: List[str]) -> Dict[str, bool]:
        """Check data localization compliance"""
        try:
            results = {
                'all_data_in_india': True,
                'sensitive_data_localized': True,
                'backup_locations_compliant': True,
                'cross_border_restrictions': True
            }
            
            indian_regions = [
                'ap-south-1',  # Mumbai
                'ap-south-2',  # Hyderabad (when available)
                'india-west',
                'india-central',
                'mumbai',
                'delhi',
                'bangalore',
                'chennai'
            ]
            
            for location in data_locations:
                location_lower = location.lower()
                
                # Check if data is stored in India
                if not any(region in location_lower for region in indian_regions):
                    if 'sensitive' in location_lower or 'customer' in location_lower:
                        results['sensitive_data_localized'] = False
                    results['all_data_in_india'] = False
                
                # Check for prohibited regions
                prohibited_regions = ['us-', 'eu-', 'china-', 'ap-northeast']
                if any(region in location_lower for region in prohibited_regions):
                    results['cross_border_restrictions'] = False
            
            logger.info(f"Data localization check: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Data localization check failed: {e}")
            return {}
    
    def validate_audit_trail(self, audit_logs: pd.DataFrame) -> Dict[str, bool]:
        """Validate audit trail completeness"""
        try:
            results = {
                'logs_complete': False,
                'timestamps_accurate': False,
                'user_identification': False,
                'action_tracking': False,
                'data_integrity': False
            }
            
            if len(audit_logs) == 0:
                return results
            
            # Check required columns
            required_columns = ['timestamp', 'user_id', 'action', 'resource', 'ip_address']
            if all(col in audit_logs.columns for col in required_columns):
                results['logs_complete'] = True
            
            # Check timestamp validity
            if 'timestamp' in audit_logs.columns:
                try:
                    audit_logs['timestamp'] = pd.to_datetime(audit_logs['timestamp'])
                    # Check if timestamps are within reasonable range
                    recent_threshold = datetime.now() - timedelta(days=365)
                    valid_timestamps = audit_logs['timestamp'] > recent_threshold
                    if valid_timestamps.all():
                        results['timestamps_accurate'] = True
                except:
                    pass
            
            # Check user identification
            if 'user_id' in audit_logs.columns:
                null_users = audit_logs['user_id'].isnull().sum()
                if null_users / len(audit_logs) < 0.05:  # Less than 5% null
                    results['user_identification'] = True
            
            # Check action tracking
            if 'action' in audit_logs.columns:
                valid_actions = ['CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT']
                action_coverage = audit_logs['action'].isin(valid_actions).sum()
                if action_coverage / len(audit_logs) > 0.9:  # 90% valid actions
                    results['action_tracking'] = True
            
            # Check data integrity (simulate hash verification)
            if 'hash' in audit_logs.columns:
                valid_hashes = audit_logs['hash'].str.len() == 64  # SHA256 length
                if valid_hashes.all():
                    results['data_integrity'] = True
            
            logger.info(f"Audit trail validation: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Audit trail validation failed: {e}")
            return {}
    
    def check_data_retention(self, data_categories: Dict[str, int]) -> Dict[str, bool]:
        """Check data retention policy compliance"""
        try:
            results = {}
            
            # Indian data retention requirements
            retention_limits = {
                'customer_data': 2555,      # 7 years in days
                'transaction_data': 3653,   # 10 years for financial
                'audit_logs': 2555,         # 7 years
                'session_data': 30,         # 30 days
                'marketing_data': 1095,     # 3 years
                'biometric_data': 1825,     # 5 years
                'health_data': 3653,        # 10 years
                'payment_data': 3653        # 10 years
            }
            
            for category, retention_days in data_categories.items():
                max_allowed = retention_limits.get(category, 2555)  # Default 7 years
                
                if retention_days <= max_allowed:
                    results[f"{category}_retention_compliant"] = True
                else:
                    results[f"{category}_retention_compliant"] = False
                    logger.warning(
                        f"{category} retention ({retention_days} days) exceeds limit ({max_allowed} days)"
                    )
            
            return results
            
        except Exception as e:
            logger.error(f"Data retention check failed: {e}")
            return {}
    
    def validate_encryption_standards(self, encryption_configs: Dict[str, str]) -> Dict[str, bool]:
        """Validate encryption standards compliance"""
        try:
            results = {
                'data_at_rest_encrypted': False,
                'data_in_transit_encrypted': False,
                'key_management_compliant': False,
                'algorithm_strength_adequate': False
            }
            
            # Check encryption at rest
            rest_encryption = encryption_configs.get('at_rest', '').lower()
            if any(alg in rest_encryption for alg in ['aes-256', 'aes256', 'rsa-2048']):
                results['data_at_rest_encrypted'] = True
            
            # Check encryption in transit
            transit_encryption = encryption_configs.get('in_transit', '').lower()
            if any(protocol in transit_encryption for protocol in ['tls1.2', 'tls1.3', 'https']):
                results['data_in_transit_encrypted'] = True
            
            # Check key management
            key_management = encryption_configs.get('key_management', '').lower()
            if any(kms in key_management for kms in ['aws-kms', 'azure-keyvault', 'hashicorp-vault']):
                results['key_management_compliant'] = True
            
            # Check algorithm strength
            algorithms = encryption_configs.get('algorithms', [])
            strong_algorithms = ['AES-256', 'RSA-2048', 'RSA-4096', 'ECDSA-256']
            if any(alg in algorithms for alg in strong_algorithms):
                results['algorithm_strength_adequate'] = True
            
            logger.info(f"Encryption validation: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Encryption validation failed: {e}")
            return {}
    
    def generate_compliance_report(self, checks: Dict[str, Dict[str, bool]]) -> str:
        """Generate comprehensive compliance report"""
        try:
            report_lines = [
                "Indian Data Compliance Report",
                "=" * 40,
                f"Company Type: {self.company_type}",
                f"Applicable Regulations: {', '.join(self.regulations)}",
                f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}",
                "",
                "Compliance Summary:",
                "-" * 20
            ]
            
            total_checks = 0
            passed_checks = 0
            
            for category, results in checks.items():
                report_lines.append(f"\n{category.replace('_', ' ').title()}:")
                
                for check_name, passed in results.items():
                    status = "✅ PASS" if passed else "❌ FAIL"
                    check_display = check_name.replace('_', ' ').title()
                    report_lines.append(f"  {check_display}: {status}")
                    
                    total_checks += 1
                    if passed:
                        passed_checks += 1
            
            # Overall compliance score
            compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            report_lines.extend([
                "",
                "Overall Compliance:",
                "-" * 20,
                f"Score: {compliance_score:.1f}% ({passed_checks}/{total_checks} checks passed)",
                ""
            ])
            
            # Recommendations
            if compliance_score < 100:
                report_lines.extend([
                    "Recommendations:",
                    "-" * 15,
                    "1. Address failed compliance checks immediately",
                    "2. Implement automated compliance monitoring",
                    "3. Regular compliance audits (quarterly)",
                    "4. Staff training on Indian data protection laws",
                    "5. Document compliance procedures",
                    ""
                ])
            
            # Regulatory contacts
            report_lines.extend([
                "Regulatory Contacts:",
                "-" * 20,
                "RBI: https://www.rbi.org.in",
                "SEBI: https://www.sebi.gov.in",
                "CERT-In: https://www.cert-in.org.in",
                "NPCI: https://www.npci.org.in",
                ""
            ])
            
            report = "\n".join(report_lines)
            
            # Save report
            report_file = f"/tmp/compliance_report_{self.company_type}_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info(f"Compliance report saved: {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return ""

def main():
    """Demonstrate compliance automation for Indian companies"""
    
    print("📜 Indian Data Compliance Automation Demo")
    print("=" * 60)
    
    # Test different company types
    company_scenarios = [
        {
            'type': 'fintech',
            'name': 'Paytm',
            'data_locations': ['ap-south-1', 'mumbai-datacenter', 'bangalore-backup'],
            'retention': {
                'customer_data': 2555,  # 7 years
                'transaction_data': 3653,  # 10 years
                'session_data': 30
            },
            'encryption': {
                'at_rest': 'AES-256',
                'in_transit': 'TLS1.3',
                'key_management': 'aws-kms',
                'algorithms': ['AES-256', 'RSA-2048']
            }
        },
        {
            'type': 'ecommerce',
            'name': 'Flipkart',
            'data_locations': ['ap-south-1', 'us-west-2', 'mumbai-warehouse'],  # Non-compliant
            'retention': {
                'customer_data': 1825,  # 5 years
                'marketing_data': 1095,  # 3 years
                'session_data': 7
            },
            'encryption': {
                'at_rest': 'AES-128',  # Weak encryption
                'in_transit': 'HTTPS',
                'key_management': 'manual',  # Non-compliant
                'algorithms': ['AES-128']
            }
        }
    ]
    
    for scenario in company_scenarios:
        print(f"\n🏢 Compliance Check: {scenario['name']} ({scenario['type']})")
        
        checker = ComplianceChecker(scenario['type'])
        
        # Run compliance checks
        checks = {}
        
        # Data localization check
        checks['data_localization'] = checker.check_data_localization(scenario['data_locations'])
        
        # Data retention check
        checks['data_retention'] = checker.check_data_retention(scenario['retention'])
        
        # Encryption standards check
        checks['encryption'] = checker.validate_encryption_standards(scenario['encryption'])
        
        # Generate sample audit logs
        audit_logs = pd.DataFrame({
            'timestamp': [datetime.now() - timedelta(days=i) for i in range(100)],
            'user_id': [f'user_{i:03d}' for i in range(100)],
            'action': np.random.choice(['CREATE', 'READ', 'UPDATE', 'DELETE'], 100),
            'resource': [f'resource_{i}' for i in range(100)],
            'ip_address': [f'192.168.1.{i%255}' for i in range(100)],
            'hash': [hashlib.sha256(f'data_{i}'.encode()).hexdigest() for i in range(100)]
        })
        
        checks['audit_trail'] = checker.validate_audit_trail(audit_logs)
        
        # Generate compliance report
        report = checker.generate_compliance_report(checks)
        
        # Print summary
        total_checks = sum(len(category) for category in checks.values())
        passed_checks = sum(sum(category.values()) for category in checks.values())
        compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        print(f"   📋 Compliance Score: {compliance_score:.1f}% ({passed_checks}/{total_checks})")
        
        if compliance_score >= 90:
            print(f"   ✅ Excellent compliance - ready for audit")
        elif compliance_score >= 75:
            print(f"   ⚠️  Good compliance - minor issues to address")
        elif compliance_score >= 50:
            print(f"   🔴 Moderate compliance - significant gaps found")
        else:
            print(f"   ❌ Poor compliance - major violations detected")
        
        # Show key failures
        failures = []
        for category, results in checks.items():
            for check, passed in results.items():
                if not passed:
                    failures.append(f"{category}: {check}")
        
        if failures:
            print(f"   ❌ Key failures: {', '.join(failures[:3])}")
    
    print("\n📊 Compliance Automation Benefits:")
    print("   • Automated regulatory compliance checking")
    print("   • Real-time violation detection")
    print("   • Comprehensive audit reporting")
    print("   • Indian regulation-specific rules")
    print("   • Cost reduction through automation")
    print("   • Risk mitigation and penalty avoidance")
    
    print("\n✅ Compliance automation demo completed!")

if __name__ == "__main__":
    main()