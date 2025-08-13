#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 9
UPI ID Validation System for Payment Platforms

Complete UPI ID validation for Indian payment systems like PhonePe, GPay, Paytm
UPI ID की पूरी जांच करने का system like payment gateway standards

Author: DStudio Team
Context: Payment platform validation like PhonePe/GPay/Paytm
Scale: 50+ crore UPI transactions per month validation
"""

import re
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib
import hmac
from collections import Counter

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - UPI जांच - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class UPIValidationResult:
    """UPI validation result structure"""
    upi_id: str
    is_valid: bool
    validation_type: str
    errors: List[str]
    warnings: List[str]
    provider: Optional[str]
    confidence_score: float
    risk_level: str
    metadata: Dict

class UPIValidationSystem:
    """
    Complete UPI ID validation system for Indian payment platforms
    भारतीय payment systems के लिए UPI ID validation
    
    Features:
    1. Format validation per NPCI guidelines
    2. Provider-specific validation
    3. Security checks for fraud prevention
    4. Bulk validation for merchant systems
    5. Real-time validation APIs
    
    Scale: Handles 50+ crore transactions/month like PhonePe
    """
    
    def __init__(self):
        """Initialize UPI validation system with Indian payment providers"""
        
        # Major Indian UPI providers - प्रमुख भारतीय UPI प्रदाता
        self.upi_providers = {
            'phonepe': {
                'domains': ['ybl'],
                'format': r'^[a-zA-Z0-9._-]+@ybl$',
                'max_length': 50,
                'company': 'PhonePe'
            },
            'googlepay': {
                'domains': ['okaxis', 'okicici', 'oksbi', 'okhdfc', 'paytm'],
                'format': r'^[a-zA-Z0-9._-]+@(okaxis|okicici|oksbi|okhdfc)$',
                'max_length': 50,
                'company': 'Google Pay'
            },
            'paytm': {
                'domains': ['paytm'],
                'format': r'^[a-zA-Z0-9._-]+@paytm$',
                'max_length': 50,
                'company': 'Paytm'
            },
            'bhim': {
                'domains': ['upi'],
                'format': r'^[a-zA-Z0-9._-]+@upi$',
                'max_length': 50,
                'company': 'BHIM'
            },
            'amazonpay': {
                'domains': ['apl'],
                'format': r'^[a-zA-Z0-9._-]+@apl$',
                'max_length': 50,
                'company': 'Amazon Pay'
            },
            'sbi': {
                'domains': ['sbi'],
                'format': r'^[a-zA-Z0-9._-]+@sbi$',
                'max_length': 50,
                'company': 'State Bank of India'
            },
            'icici': {
                'domains': ['icici'],
                'format': r'^[a-zA-Z0-9._-]+@icici$',
                'max_length': 50,
                'company': 'ICICI Bank'
            },
            'hdfc': {
                'domains': ['hdfcbank'],
                'format': r'^[a-zA-Z0-9._-]+@hdfcbank$',
                'max_length': 50,
                'company': 'HDFC Bank'
            }
        }
        
        # All valid UPI domains - सभी valid UPI domains
        self.all_upi_domains = set()
        for provider_info in self.upi_providers.values():
            self.all_upi_domains.update(provider_info['domains'])
        
        # Additional bank domains
        additional_domains = [
            'axl', 'ibl', 'yesbank', 'kotak', 'pnb', 'boi', 'canara', 
            'unionbank', 'indianbank', 'idbi', 'federal', 'rbl', 'axis'
        ]
        self.all_upi_domains.update(additional_domains)
        
        # Suspicious patterns for fraud detection
        self.suspicious_patterns = [
            r'admin', r'test', r'demo', r'root', r'system', r'bank',
            r'upi', r'payment', r'money', r'cash', r'fund', r'transfer'
        ]
        
        # Mobile number pattern for Indian numbers
        self.indian_mobile_pattern = r'^[6-9]\d{9}$'
        
        logger.info("UPI Validation System initialized - UPI सिस्टम तैयार!")
        logger.info(f"Supporting {len(self.all_upi_domains)} UPI providers")

    def validate_upi_format(self, upi_id: str) -> Dict[str, any]:
        """
        Basic UPI ID format validation per NPCI guidelines
        NPCI नियमों के अनुसार UPI ID format validation
        """
        
        upi_clean = str(upi_id).strip().lower()
        
        validation_result = {
            'original': upi_id,
            'cleaned': upi_clean,
            'is_valid_format': False,
            'errors': [],
            'warnings': [],
            'provider': None,
            'domain': None
        }
        
        # Basic format check - बुनियादी format जांच
        if not upi_clean:
            validation_result['errors'].append("UPI ID cannot be empty")
            return validation_result
        
        # Must contain exactly one @ symbol
        if upi_clean.count('@') != 1:
            validation_result['errors'].append("UPI ID must contain exactly one '@' symbol")
            return validation_result
        
        # Split into username and domain
        try:
            username, domain = upi_clean.split('@', 1)
        except ValueError:
            validation_result['errors'].append("Invalid UPI ID format")
            return validation_result
        
        validation_result['domain'] = domain
        
        # Username validation - username की जांच
        if len(username) < 3:
            validation_result['errors'].append("Username part must be at least 3 characters")
            return validation_result
        
        if len(username) > 50:
            validation_result['errors'].append("Username part too long (max 50 characters)")
            return validation_result
        
        # Username character validation
        username_pattern = r'^[a-zA-Z0-9._-]+$'
        if not re.match(username_pattern, username):
            validation_result['errors'].append("Username contains invalid characters (only alphanumeric, dot, underscore, hyphen allowed)")
            return validation_result
        
        # Check for consecutive special characters
        if re.search(r'[._-]{2,}', username):
            validation_result['warnings'].append("Username contains consecutive special characters")
        
        # Domain validation - domain की जांच
        if not domain:
            validation_result['errors'].append("UPI domain cannot be empty")
            return validation_result
        
        if domain not in self.all_upi_domains:
            validation_result['errors'].append(f"Unknown UPI domain: {domain}")
            validation_result['warnings'].append("This might be a new or regional UPI provider")
            return validation_result
        
        # Provider identification
        for provider_name, provider_info in self.upi_providers.items():
            if domain in provider_info['domains']:
                validation_result['provider'] = provider_name
                
                # Provider-specific format check
                if not re.match(provider_info['format'], upi_clean):
                    validation_result['warnings'].append(f"Unusual format for {provider_info['company']}")
                break
        
        # Security checks - सुरक्षा जांच
        for pattern in self.suspicious_patterns:
            if re.search(pattern, username, re.IGNORECASE):
                validation_result['warnings'].append(f"Username contains suspicious pattern: {pattern}")
        
        # Check if username is mobile number
        if re.match(self.indian_mobile_pattern, username):
            validation_result['warnings'].append("Username appears to be a mobile number")
        
        validation_result['is_valid_format'] = True
        logger.info(f"UPI format validation passed: {username[:3]}***@{domain}")
        
        return validation_result

    def validate_upi_provider_specific(self, upi_id: str) -> Dict[str, any]:
        """
        Provider-specific UPI validation with business rules
        Provider-specific validation और business rules
        """
        
        format_result = self.validate_upi_format(upi_id)
        
        if not format_result['is_valid_format']:
            return format_result
        
        provider = format_result['provider']
        domain = format_result['domain']
        username = upi_id.split('@')[0].lower()
        
        provider_validation = {
            'provider_name': provider,
            'provider_checks': [],
            'business_rules_passed': True,
            'risk_score': 0
        }
        
        # PhonePe specific checks
        if provider == 'phonepe':
            # PhonePe typically uses mobile numbers
            if not re.match(self.indian_mobile_pattern, username):
                provider_validation['provider_checks'].append("PhonePe usually uses mobile numbers as username")
                provider_validation['risk_score'] += 10
            
            # Length check for PhonePe
            if len(username) > 15:
                provider_validation['provider_checks'].append("Unusually long username for PhonePe")
                provider_validation['risk_score'] += 5
        
        # Google Pay specific checks
        elif provider == 'googlepay':
            # Google Pay domains mapping
            bank_mapping = {
                'okaxis': 'Axis Bank',
                'okicici': 'ICICI Bank',
                'oksbi': 'State Bank of India',
                'okhdfc': 'HDFC Bank'
            }
            
            if domain in bank_mapping:
                provider_validation['provider_checks'].append(f"Google Pay with {bank_mapping[domain]}")
        
        # Paytm specific checks
        elif provider == 'paytm':
            # Paytm typically uses mobile numbers or emails
            if not (re.match(self.indian_mobile_pattern, username) or '@' in username):
                provider_validation['provider_checks'].append("Paytm usually uses mobile numbers")
                provider_validation['risk_score'] += 5
        
        # Risk assessment - जोखिम आकलन
        if provider_validation['risk_score'] > 20:
            provider_validation['business_rules_passed'] = False
        
        format_result.update(provider_validation)
        return format_result

    def detect_upi_fraud_patterns(self, upi_id: str) -> Dict[str, any]:
        """
        Fraud detection for UPI IDs using pattern analysis
        UPI ID में fraud detection और suspicious pattern analysis
        """
        
        fraud_analysis = {
            'is_suspicious': False,
            'fraud_indicators': [],
            'risk_level': 'LOW',
            'confidence': 0.0,
            'recommendations': []
        }
        
        username = upi_id.split('@')[0].lower()
        
        # Pattern 1: Sequential numbers
        if re.search(r'(012|123|234|345|456|567|678|789|890)', username):
            fraud_analysis['fraud_indicators'].append("Sequential numbers in username")
            fraud_analysis['confidence'] += 15
        
        # Pattern 2: Repeated characters
        if re.search(r'(.)\1{3,}', username):
            fraud_analysis['fraud_indicators'].append("Repeated characters (possible bot)")
            fraud_analysis['confidence'] += 20
        
        # Pattern 3: Common fraud terms
        fraud_terms = ['fake', 'test', 'fraud', 'scam', 'money', 'cash', 'pay']
        for term in fraud_terms:
            if term in username:
                fraud_analysis['fraud_indicators'].append(f"Contains fraud-related term: {term}")
                fraud_analysis['confidence'] += 25
        
        # Pattern 4: Too many special characters
        special_char_count = sum(1 for char in username if char in '._-')
        if special_char_count > len(username) * 0.3:
            fraud_analysis['fraud_indicators'].append("Excessive special characters")
            fraud_analysis['confidence'] += 10
        
        # Pattern 5: Very short or very long usernames
        if len(username) < 4:
            fraud_analysis['fraud_indicators'].append("Unusually short username")
            fraud_analysis['confidence'] += 8
        elif len(username) > 25:
            fraud_analysis['fraud_indicators'].append("Unusually long username")
            fraud_analysis['confidence'] += 12
        
        # Risk level calculation
        if fraud_analysis['confidence'] >= 50:
            fraud_analysis['risk_level'] = 'HIGH'
            fraud_analysis['is_suspicious'] = True
            fraud_analysis['recommendations'].append("Block transaction and verify identity")
        elif fraud_analysis['confidence'] >= 25:
            fraud_analysis['risk_level'] = 'MEDIUM'
            fraud_analysis['recommendations'].append("Additional verification required")
        else:
            fraud_analysis['risk_level'] = 'LOW'
            fraud_analysis['recommendations'].append("Proceed with normal verification")
        
        return fraud_analysis

    def complete_upi_validation(self, upi_id: str, 
                               amount: Optional[float] = None,
                               transaction_type: str = 'P2P') -> UPIValidationResult:
        """
        Complete UPI validation with all checks and fraud detection
        सभी जांच के साथ complete UPI validation
        """
        
        logger.info(f"Starting complete UPI validation for: {upi_id[:6]}***")
        
        # Step 1: Format validation
        format_result = self.validate_upi_format(upi_id)
        
        if not format_result['is_valid_format']:
            return UPIValidationResult(
                upi_id=upi_id,
                is_valid=False,
                validation_type='format_failed',
                errors=format_result['errors'],
                warnings=format_result['warnings'],
                provider=None,
                confidence_score=0.0,
                risk_level='HIGH',
                metadata={'format_result': format_result}
            )
        
        # Step 2: Provider-specific validation
        provider_result = self.validate_upi_provider_specific(upi_id)
        
        # Step 3: Fraud detection
        fraud_result = self.detect_upi_fraud_patterns(upi_id)
        
        # Step 4: Transaction amount validation (if provided)
        amount_checks = {}
        if amount is not None:
            amount_checks = self._validate_transaction_amount(amount, transaction_type)
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(
            format_result, provider_result, fraud_result, amount_checks
        )
        
        # Determine if UPI is valid
        is_valid = (
            format_result['is_valid_format'] and
            provider_result.get('business_rules_passed', True) and
            not fraud_result['is_suspicious'] and
            amount_checks.get('is_valid_amount', True)
        )
        
        # Collect all errors and warnings
        all_errors = format_result['errors'] + provider_result.get('errors', [])
        all_warnings = (format_result['warnings'] + 
                       provider_result.get('warnings', []) + 
                       fraud_result['fraud_indicators'])
        
        logger.info(f"Complete UPI validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return UPIValidationResult(
            upi_id=upi_id,
            is_valid=is_valid,
            validation_type='complete',
            errors=all_errors,
            warnings=all_warnings,
            provider=format_result.get('provider'),
            confidence_score=confidence_score,
            risk_level=fraud_result['risk_level'],
            metadata={
                'format_result': format_result,
                'provider_result': provider_result,
                'fraud_result': fraud_result,
                'amount_checks': amount_checks
            }
        )

    def _validate_transaction_amount(self, amount: float, transaction_type: str) -> Dict[str, any]:
        """Validate transaction amount based on UPI limits"""
        
        # UPI transaction limits as per RBI guidelines
        limits = {
            'P2P': {'min': 1, 'max': 100000},  # Person to Person
            'P2M': {'min': 1, 'max': 200000},  # Person to Merchant
            'P2B': {'min': 1, 'max': 1000000}  # Person to Business
        }
        
        limit = limits.get(transaction_type, limits['P2P'])
        
        return {
            'amount': amount,
            'transaction_type': transaction_type,
            'is_valid_amount': limit['min'] <= amount <= limit['max'],
            'limit_min': limit['min'],
            'limit_max': limit['max'],
            'within_limits': amount <= limit['max']
        }

    def _calculate_confidence_score(self, format_result: Dict, provider_result: Dict,
                                  fraud_result: Dict, amount_checks: Dict) -> float:
        """Calculate overall confidence score for UPI validation"""
        
        score = 0.0
        
        # Format validation (30%)
        if format_result['is_valid_format']:
            score += 30.0
        
        # Provider validation (25%)
        if provider_result.get('business_rules_passed', True):
            score += 25.0
        
        # Fraud check (25%)
        fraud_confidence = fraud_result.get('confidence', 0)
        fraud_score = max(0, 25 - (fraud_confidence * 0.5))
        score += fraud_score
        
        # Amount validation (20%)
        if amount_checks.get('is_valid_amount', True):
            score += 20.0
        
        return min(score, 100.0)

    def bulk_validate_upi_dataset(self, df: pd.DataFrame, 
                                 upi_column: str = 'upi_id',
                                 amount_column: str = None) -> pd.DataFrame:
        """
        Bulk UPI validation for payment systems
        Payment systems के लिए bulk UPI validation
        """
        
        logger.info(f"Starting bulk UPI validation for {len(df)} records")
        
        validation_results = []
        
        for index, row in df.iterrows():
            upi_id = row[upi_column]
            amount = row[amount_column] if amount_column and amount_column in row else None
            
            # Validate each UPI ID
            result = self.complete_upi_validation(upi_id, amount)
            
            validation_results.append({
                'row_index': index,
                'upi_id_masked': f"{upi_id[:6]}***@{upi_id.split('@')[1] if '@' in upi_id else 'unknown'}",
                'is_valid': result.is_valid,
                'provider': result.provider,
                'confidence_score': result.confidence_score,
                'risk_level': result.risk_level,
                'error_count': len(result.errors),
                'warning_count': len(result.warnings)
            })
            
            if index % 1000 == 0:
                logger.info(f"Processed {index + 1} records...")
        
        # Create results DataFrame
        results_df = pd.DataFrame(validation_results)
        
        # Summary statistics
        valid_count = results_df['is_valid'].sum()
        total_count = len(results_df)
        validity_rate = (valid_count / total_count) * 100
        
        # Risk distribution
        risk_distribution = results_df['risk_level'].value_counts()
        
        logger.info(f"""
        Bulk UPI Validation Complete:
        =============================
        Total Records: {total_count}
        Valid UPI IDs: {valid_count}
        Invalid UPI IDs: {total_count - valid_count}
        Validity Rate: {validity_rate:.2f}%
        Average Confidence: {results_df['confidence_score'].mean():.2f}%
        
        Risk Distribution:
        - LOW: {risk_distribution.get('LOW', 0)} ({risk_distribution.get('LOW', 0)/total_count*100:.1f}%)
        - MEDIUM: {risk_distribution.get('MEDIUM', 0)} ({risk_distribution.get('MEDIUM', 0)/total_count*100:.1f}%)
        - HIGH: {risk_distribution.get('HIGH', 0)} ({risk_distribution.get('HIGH', 0)/total_count*100:.1f}%)
        """)
        
        return results_df

    def generate_validation_report(self, validation_results: pd.DataFrame) -> Dict[str, any]:
        """Generate comprehensive validation report for management"""
        
        # Provider distribution
        provider_stats = validation_results['provider'].value_counts()
        
        # Risk analysis
        risk_stats = validation_results['risk_level'].value_counts()
        
        # Error analysis
        error_analysis = validation_results.groupby('error_count').size()
        
        report = {
            'summary': {
                'total_upis_validated': len(validation_results),
                'valid_upis': validation_results['is_valid'].sum(),
                'validity_rate': (validation_results['is_valid'].sum() / len(validation_results)) * 100,
                'average_confidence': validation_results['confidence_score'].mean()
            },
            'provider_distribution': provider_stats.to_dict(),
            'risk_distribution': risk_stats.to_dict(),
            'error_distribution': error_analysis.to_dict(),
            'recommendations': self._generate_recommendations(validation_results)
        }
        
        return report

    def _generate_recommendations(self, results_df: pd.DataFrame) -> List[str]:
        """Generate recommendations based on validation results"""
        
        recommendations = []
        
        validity_rate = (results_df['is_valid'].sum() / len(results_df)) * 100
        high_risk_count = (results_df['risk_level'] == 'HIGH').sum()
        
        if validity_rate < 85:
            recommendations.append("UPI validity rate below 85% - review data source quality")
        
        if high_risk_count > len(results_df) * 0.05:
            recommendations.append("High risk UPI IDs detected - enhance fraud monitoring")
        
        if results_df['confidence_score'].mean() < 75:
            recommendations.append("Low average confidence - implement additional validation steps")
        
        # Provider-specific recommendations
        provider_stats = results_df['provider'].value_counts()
        if 'phonepe' in provider_stats and provider_stats['phonepe'] > len(results_df) * 0.5:
            recommendations.append("PhonePe dominance detected - ensure diversified provider support")
        
        return recommendations

def create_sample_upi_dataset(num_records: int = 1000) -> pd.DataFrame:
    """Create sample UPI dataset for testing"""
    
    # Common UPI patterns
    upi_patterns = [
        lambda i: f"{random.randint(6000000000, 9999999999)}@ybl",  # PhonePe mobile
        lambda i: f"user{i}@paytm",  # Paytm user
        lambda i: f"{random.randint(6000000000, 9999999999)}@okicici",  # GPay ICICI
        lambda i: f"merchant{i}@sbi",  # SBI merchant
        lambda i: f"shop{i}@hdfc",  # HDFC business
        lambda i: f"test{i}@upi",  # BHIM test (some invalid)
        lambda i: f"user.{i}@axis",  # Axis bank
        lambda i: f"invalid_email@gmail.com",  # Invalid (not UPI)
    ]
    
    import random
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for i in range(num_records):
        pattern = random.choice(upi_patterns)
        upi_id = pattern(i)
        
        # Generate transaction data
        amount = np.random.exponential(scale=1000)
        transaction_type = random.choice(['P2P', 'P2M', 'P2B'])
        
        data.append({
            'upi_id': upi_id,
            'amount': round(amount, 2),
            'transaction_type': transaction_type,
            'timestamp': datetime.now() - timedelta(days=random.randint(0, 30))
        })
    
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of UPI validation system"""
    
    print("💳 UPI Validation System Demo")
    print("UPI ID सत्यापन प्रणाली का प्रदर्शन\n")
    
    # Initialize validator
    validator = UPIValidationSystem()
    
    # Test 1: Individual UPI validations
    print("Test 1: Individual UPI Validations")
    print("=" * 40)
    
    test_upis = [
        "9876543210@ybl",         # Valid PhonePe
        "user123@paytm",          # Valid Paytm
        "merchant@okicici",       # Valid Google Pay
        "test@invalid",           # Invalid domain
        "toolong_username_that_exceeds_limit@sbi",  # Too long
        "ab@upi",                 # Too short username
        "user..test@hdfc",        # Consecutive dots
        "9876543210@gmail.com"    # Not a UPI ID
    ]
    
    for upi_id in test_upis:
        result = validator.complete_upi_validation(upi_id)
        print(f"""
    UPI ID: {upi_id}
    Valid: {'✅' if result.is_valid else '❌'}
    Provider: {result.provider or 'Unknown'}
    Confidence: {result.confidence_score:.1f}%
    Risk: {result.risk_level}
    Errors: {len(result.errors)}
    Warnings: {len(result.warnings)}
        """)
    
    # Test 2: Fraud detection
    print("\nTest 2: Fraud Detection Examples")
    print("=" * 40)
    
    suspicious_upis = [
        "admin@ybl",
        "test123456@paytm",
        "money.cash@sbi",
        "1111111111@upi",
        "fake.user@hdfc"
    ]
    
    for upi_id in suspicious_upis:
        fraud_result = validator.detect_upi_fraud_patterns(upi_id)
        print(f"""
    UPI: {upi_id}
    Suspicious: {'🚨 YES' if fraud_result['is_suspicious'] else '✅ NO'}
    Risk Level: {fraud_result['risk_level']}
    Indicators: {len(fraud_result['fraud_indicators'])}
        """)
    
    # Test 3: Bulk validation
    print("\nTest 3: Bulk Dataset Validation")
    print("=" * 40)
    
    # Create test dataset
    test_df = create_sample_upi_dataset(500)
    print(f"Created test dataset with {len(test_df)} UPI records")
    
    # Perform bulk validation
    validation_results = validator.bulk_validate_upi_dataset(
        test_df, 
        upi_column='upi_id',
        amount_column='amount'
    )
    
    # Generate report
    report = validator.generate_validation_report(validation_results)
    
    print(f"""
    Bulk Validation Report:
    ======================
    Total UPIs: {report['summary']['total_upis_validated']}
    Valid UPIs: {report['summary']['valid_upis']}
    Validity Rate: {report['summary']['validity_rate']:.2f}%
    Average Confidence: {report['summary']['average_confidence']:.2f}%
    
    Provider Distribution:
    {json.dumps(report['provider_distribution'], indent=2)}
    
    Risk Distribution:
    {json.dumps(report['risk_distribution'], indent=2)}
    
    Recommendations:
    {chr(10).join(['- ' + rec for rec in report['recommendations']])}
    """)
    
    print("\n✅ UPI Validation System Demo Complete!")
    print("Payment gateway ready - पेमेंट गेटवे तैयार!")
    
    return {
        'validation_results': validation_results,
        'report': report
    }

if __name__ == "__main__":
    results = main()