#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 11
Bank Account Number and IFSC Code Validation System

Complete banking validation for Indian financial systems
भारतीय बैंकिंग प्रणाली के लिए account number और IFSC validation

Author: DStudio Team
Context: Banking validation like NEFT, RTGS, IMPS systems
Scale: 80+ crore bank accounts in India validation
"""

import re
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import requests
import hashlib

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - बैंक जांच - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BankValidationResult:
    """Bank account validation result structure"""
    account_number: str
    ifsc_code: str
    is_valid: bool
    bank_name: str
    branch_name: str
    city: str
    state: str
    errors: List[str]
    warnings: List[str]
    confidence_score: float
    metadata: Dict

class IndianBankValidationSystem:
    """
    Complete Indian bank account and IFSC validation system
    भारतीय बैंक खाता और IFSC कोड validation system
    
    Features:
    1. IFSC code validation with bank database
    2. Account number format validation per bank
    3. Bank branch information lookup
    4. MICR code validation
    5. Fraud detection for fake accounts
    6. Bulk validation for payment systems
    
    Scale: Handles 80+ crore bank accounts like payment gateways
    """
    
    def __init__(self):
        """Initialize with Indian banking data"""
        
        # Major Indian banks with their IFSC patterns - प्रमुख भारतीय बैंक
        self.bank_codes = {
            'SBIN': {
                'name': 'State Bank of India',
                'account_length': [9, 10, 11, 12, 13],
                'account_pattern': r'^\d{9,13}$',
                'established': 1955,
                'type': 'Public Sector'
            },
            'HDFC': {
                'name': 'HDFC Bank',
                'account_length': [11, 14],
                'account_pattern': r'^\d{11,14}$',
                'established': 1994,
                'type': 'Private Sector'
            },
            'ICIC': {
                'name': 'ICICI Bank',
                'account_length': [12],
                'account_pattern': r'^\d{12}$',
                'established': 1994,
                'type': 'Private Sector'
            },
            'AXIS': {
                'name': 'Axis Bank',
                'account_length': [12, 15, 16],
                'account_pattern': r'^\d{12,16}$',
                'established': 1993,
                'type': 'Private Sector'
            },
            'PUNB': {
                'name': 'Punjab National Bank',
                'account_length': [10, 11, 12, 13],
                'account_pattern': r'^\d{10,13}$',
                'established': 1894,
                'type': 'Public Sector'
            },
            'UBIN': {
                'name': 'Union Bank of India',
                'account_length': [11, 12, 13, 14, 15],
                'account_pattern': r'^\d{11,15}$',
                'established': 1919,
                'type': 'Public Sector'
            },
            'CNRB': {
                'name': 'Canara Bank',
                'account_length': [10, 11, 12, 13],
                'account_pattern': r'^\d{10,13}$',
                'established': 1906,
                'type': 'Public Sector'
            },
            'BKID': {
                'name': 'Bank of India',
                'account_length': [12, 13, 14, 15],
                'account_pattern': r'^\d{12,15}$',
                'established': 1906,
                'type': 'Public Sector'
            },
            'YESB': {
                'name': 'Yes Bank',
                'account_length': [15],
                'account_pattern': r'^\d{15}$',
                'established': 2004,
                'type': 'Private Sector'
            },
            'KKBK': {
                'name': 'Kotak Mahindra Bank',
                'account_length': [10, 11, 12],
                'account_pattern': r'^\d{10,12}$',
                'established': 2003,
                'type': 'Private Sector'
            },
            'IDIB': {
                'name': 'Indian Bank',
                'account_length': [11, 12, 13, 14],
                'account_pattern': r'^\d{11,14}$',
                'established': 1907,
                'type': 'Public Sector'
            },
            'IDFB': {
                'name': 'IDFC First Bank',
                'account_length': [10, 11, 12, 13],
                'account_pattern': r'^\d{10,13}$',
                'established': 2015,
                'type': 'Private Sector'
            }
        }
        
        # IFSC format pattern - IFSC कोड का format
        self.ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        
        # Sample bank branch database (in production, this would be comprehensive)
        # नमूना बैंक शाखा database
        self.sample_branches = {
            'SBIN0001234': {
                'bank_name': 'State Bank of India',
                'branch_name': 'Mumbai Main Branch',
                'address': 'Nariman Point, Mumbai',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'contact': '022-22885444',
                'micr': '400002002'
            },
            'HDFC0000123': {
                'bank_name': 'HDFC Bank',
                'branch_name': 'Connaught Place',
                'address': 'CP, New Delhi',
                'city': 'New Delhi',
                'state': 'Delhi',
                'contact': '011-23456789',
                'micr': '110240001'
            },
            'ICIC0001234': {
                'bank_name': 'ICICI Bank',
                'branch_name': 'Bangalore Electronic City',
                'address': 'Electronic City, Bangalore',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'contact': '080-12345678',
                'micr': '560229001'
            }
        }
        
        # Fraud patterns for fake accounts
        self.fraud_patterns = {
            'sequential_accounts': r'(01234|12345|23456|34567|45678|56789)',
            'repeated_digits': r'(\d)\1{6,}',
            'all_same': r'^(\d)\1+$',
            'obvious_test': r'(123456789|987654321|111111111|000000000)'
        }
        
        # Common account number formats by bank type
        self.account_formats = {
            'savings': r'^\d{9,16}$',
            'current': r'^\d{10,16}$',
            'fixed_deposit': r'^FD\d{8,12}$',
            'recurring_deposit': r'^RD\d{8,12}$',
            'credit_card': r'^CC\d{10,16}$'
        }
        
        logger.info("Indian Bank Validation System initialized - बैंक सिस्टम तैयार!")
        logger.info(f"Supporting {len(self.bank_codes)} major banks")

    def validate_ifsc_format(self, ifsc: str) -> Dict[str, any]:
        """
        Validate IFSC code format according to RBI standards
        RBI मानकों के अनुसार IFSC कोड format validation
        """
        
        ifsc_clean = str(ifsc).strip().upper()
        
        validation_result = {
            'original_ifsc': ifsc,
            'cleaned_ifsc': ifsc_clean,
            'is_valid_format': False,
            'bank_code': None,
            'branch_code': None,
            'errors': [],
            'warnings': []
        }
        
        # Basic format check
        if not ifsc_clean:
            validation_result['errors'].append("IFSC code cannot be empty")
            return validation_result
        
        # Length check - must be exactly 11 characters
        if len(ifsc_clean) != 11:
            validation_result['errors'].append(f"IFSC must be exactly 11 characters, got {len(ifsc_clean)}")
            return validation_result
        
        # Pattern validation
        if not re.match(self.ifsc_pattern, ifsc_clean):
            validation_result['errors'].append("IFSC format invalid. Must be: 4 letters + 0 + 6 alphanumeric")
            return validation_result
        
        # Extract bank code and branch code
        bank_code = ifsc_clean[:4]
        branch_code = ifsc_clean[5:]  # Skip the mandatory '0' at position 4
        
        validation_result['bank_code'] = bank_code
        validation_result['branch_code'] = branch_code
        
        # Check if bank code is known
        if bank_code not in self.bank_codes:
            validation_result['warnings'].append(f"Unknown bank code: {bank_code}")
        
        # Fifth character must be '0'
        if ifsc_clean[4] != '0':
            validation_result['errors'].append("Fifth character of IFSC must be '0'")
            return validation_result
        
        validation_result['is_valid_format'] = True
        logger.debug(f"IFSC format validation passed: {ifsc_clean}")
        
        return validation_result

    def lookup_branch_details(self, ifsc: str) -> Dict[str, any]:
        """
        Lookup bank branch details from IFSC code
        IFSC कोड से बैंक शाखा की जानकारी लेना
        """
        
        ifsc_clean = str(ifsc).strip().upper()
        
        # In production, this would query the official RBI database
        # यहाँ production में RBI database से query करना होगा
        
        if ifsc_clean in self.sample_branches:
            return {
                'found': True,
                'details': self.sample_branches[ifsc_clean],
                'source': 'local_database'
            }
        
        # Try to identify bank from code
        bank_code = ifsc_clean[:4] if len(ifsc_clean) >= 4 else ""
        
        if bank_code in self.bank_codes:
            return {
                'found': False,
                'bank_info': self.bank_codes[bank_code],
                'message': f"Bank identified as {self.bank_codes[bank_code]['name']} but branch details not found",
                'source': 'bank_code_lookup'
            }
        
        return {
            'found': False,
            'message': 'IFSC not found in database',
            'source': 'not_found'
        }

    def validate_account_number(self, account_number: str, ifsc: str = None) -> Dict[str, any]:
        """
        Validate bank account number format
        बैंक account number का format validation
        """
        
        account_clean = str(account_number).strip()
        
        validation_result = {
            'original_account': account_number,
            'cleaned_account': account_clean,
            'is_valid_format': False,
            'detected_bank': None,
            'account_type': None,
            'errors': [],
            'warnings': []
        }
        
        # Basic checks
        if not account_clean:
            validation_result['errors'].append("Account number cannot be empty")
            return validation_result
        
        # Remove any non-alphanumeric characters for validation
        account_alphanumeric = re.sub(r'[^A-Za-z0-9]', '', account_clean)
        
        if not account_alphanumeric:
            validation_result['errors'].append("Account number must contain alphanumeric characters")
            return validation_result
        
        # Length validation - Indian bank accounts are typically 9-16 digits
        if len(account_alphanumeric) < 8 or len(account_alphanumeric) > 20:
            validation_result['errors'].append(f"Account number length unusual: {len(account_alphanumeric)} characters")
        
        # If IFSC is provided, validate against bank-specific rules
        if ifsc:
            ifsc_result = self.validate_ifsc_format(ifsc)
            if ifsc_result['is_valid_format']:
                bank_code = ifsc_result['bank_code']
                
                if bank_code in self.bank_codes:
                    bank_info = self.bank_codes[bank_code]
                    validation_result['detected_bank'] = bank_info['name']
                    
                    # Check account number length for this bank
                    if len(account_alphanumeric) not in bank_info['account_length']:
                        validation_result['warnings'].append(
                            f"Account length {len(account_alphanumeric)} unusual for {bank_info['name']}"
                        )
                    
                    # Check account pattern
                    if not re.match(bank_info['account_pattern'], account_alphanumeric):
                        validation_result['warnings'].append(
                            f"Account format doesn't match typical {bank_info['name']} pattern"
                        )
        
        # Detect account type based on format
        for acc_type, pattern in self.account_formats.items():
            if re.match(pattern, account_alphanumeric):
                validation_result['account_type'] = acc_type
                break
        
        if not validation_result['account_type']:
            validation_result['account_type'] = 'unknown'
        
        # Fraud detection
        fraud_indicators = []
        for pattern_name, pattern in self.fraud_patterns.items():
            if re.search(pattern, account_alphanumeric):
                fraud_indicators.append(f"Matches {pattern_name} pattern")
        
        if fraud_indicators:
            validation_result['warnings'].extend(fraud_indicators)
        
        # Check for obvious invalid patterns
        if len(set(account_alphanumeric)) == 1:
            validation_result['errors'].append("Account number cannot have all same digits")
            return validation_result
        
        # Check for too many zeros
        zero_count = account_alphanumeric.count('0')
        if zero_count > len(account_alphanumeric) * 0.7:
            validation_result['warnings'].append("Too many zeros in account number")
        
        validation_result['is_valid_format'] = True
        logger.debug(f"Account validation passed: {account_alphanumeric[:4]}****{account_alphanumeric[-4:]}")
        
        return validation_result

    def validate_micr_code(self, micr: str) -> Dict[str, any]:
        """
        Validate MICR code format
        MICR कोड का format validation
        """
        
        micr_clean = str(micr).strip()
        
        validation_result = {
            'original_micr': micr,
            'cleaned_micr': micr_clean,
            'is_valid_format': False,
            'city_code': None,
            'bank_code': None,
            'branch_code': None,
            'errors': [],
            'warnings': []
        }
        
        # MICR should be exactly 9 digits
        if not micr_clean.isdigit():
            validation_result['errors'].append("MICR code must contain only digits")
            return validation_result
        
        if len(micr_clean) != 9:
            validation_result['errors'].append(f"MICR must be exactly 9 digits, got {len(micr_clean)}")
            return validation_result
        
        # Extract components
        city_code = micr_clean[:3]
        bank_code = micr_clean[3:6]
        branch_code = micr_clean[6:9]
        
        validation_result['city_code'] = city_code
        validation_result['bank_code'] = bank_code
        validation_result['branch_code'] = branch_code
        validation_result['is_valid_format'] = True
        
        return validation_result

    def complete_bank_validation(self, account_number: str, ifsc: str, 
                                micr: str = None) -> BankValidationResult:
        """
        Complete bank account validation with all checks
        सभी जांच के साथ complete bank validation
        """
        
        logger.info(f"Starting complete bank validation for IFSC: {ifsc}")
        
        # Step 1: IFSC validation
        ifsc_result = self.validate_ifsc_format(ifsc)
        
        if not ifsc_result['is_valid_format']:
            return BankValidationResult(
                account_number=account_number,
                ifsc_code=ifsc,
                is_valid=False,
                bank_name='Unknown',
                branch_name='Unknown',
                city='Unknown',
                state='Unknown',
                errors=ifsc_result['errors'],
                warnings=ifsc_result['warnings'],
                confidence_score=0.0,
                metadata={'ifsc_result': ifsc_result}
            )
        
        # Step 2: Branch lookup
        branch_result = self.lookup_branch_details(ifsc)
        
        # Step 3: Account number validation
        account_result = self.validate_account_number(account_number, ifsc)
        
        # Step 4: MICR validation (if provided)
        micr_result = None
        if micr:
            micr_result = self.validate_micr_code(micr)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            ifsc_result, branch_result, account_result, micr_result
        )
        
        # Determine overall validity
        is_valid = (
            ifsc_result['is_valid_format'] and
            account_result['is_valid_format'] and
            len(account_result['errors']) == 0 and
            (micr_result is None or micr_result.get('is_valid_format', True))
        )
        
        # Extract bank and branch information
        bank_name = 'Unknown'
        branch_name = 'Unknown'
        city = 'Unknown'
        state = 'Unknown'
        
        if branch_result['found']:
            details = branch_result['details']
            bank_name = details['bank_name']
            branch_name = details['branch_name']
            city = details['city']
            state = details['state']
        elif ifsc_result['bank_code'] in self.bank_codes:
            bank_name = self.bank_codes[ifsc_result['bank_code']]['name']
        
        # Collect all errors and warnings
        all_errors = ifsc_result['errors'] + account_result['errors']
        all_warnings = ifsc_result['warnings'] + account_result['warnings']
        
        if micr_result and micr_result.get('errors'):
            all_errors.extend(micr_result['errors'])
        
        logger.info(f"Complete bank validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return BankValidationResult(
            account_number=account_number,
            ifsc_code=ifsc,
            is_valid=is_valid,
            bank_name=bank_name,
            branch_name=branch_name,
            city=city,
            state=state,
            errors=all_errors,
            warnings=all_warnings,
            confidence_score=confidence_score,
            metadata={
                'ifsc_result': ifsc_result,
                'branch_result': branch_result,
                'account_result': account_result,
                'micr_result': micr_result
            }
        )

    def _calculate_confidence_score(self, ifsc_result: Dict, branch_result: Dict,
                                  account_result: Dict, micr_result: Optional[Dict]) -> float:
        """Calculate overall confidence score for bank validation"""
        
        score = 0.0
        
        # IFSC validation (30%)
        if ifsc_result['is_valid_format']:
            score += 30.0
        
        # Branch lookup (25%)
        if branch_result['found']:
            score += 25.0
        elif branch_result.get('bank_info'):
            score += 15.0  # Partial credit for bank identification
        
        # Account number validation (30%)
        if account_result['is_valid_format']:
            score += 30.0
            # Bonus for bank-specific validation
            if account_result['detected_bank']:
                score += 5.0
        
        # MICR validation (15%)
        if micr_result:
            if micr_result.get('is_valid_format'):
                score += 15.0
        else:
            score += 10.0  # Partial credit if MICR not provided
        
        return min(score, 100.0)

    def bulk_validate_bank_dataset(self, df: pd.DataFrame, 
                                  account_column: str = 'account_number',
                                  ifsc_column: str = 'ifsc_code',
                                  micr_column: str = None) -> pd.DataFrame:
        """
        Bulk bank validation for payment systems
        Payment systems के लिए bulk bank validation
        """
        
        logger.info(f"Starting bulk bank validation for {len(df)} records")
        
        validation_results = []
        bank_stats = defaultdict(int)
        
        for index, row in df.iterrows():
            account_number = row[account_column]
            ifsc_code = row[ifsc_column]
            micr_code = row[micr_column] if micr_column and micr_column in row else None
            
            # Validate each bank record
            result = self.complete_bank_validation(account_number, ifsc_code, micr_code)
            
            # Update bank statistics
            if result.bank_name != 'Unknown':
                bank_stats[result.bank_name] += 1
            
            validation_results.append({
                'row_index': index,
                'account_number_masked': f"{str(account_number)[:4]}****{str(account_number)[-4:]}",
                'ifsc_code': ifsc_code,
                'is_valid': result.is_valid,
                'bank_name': result.bank_name,
                'branch_name': result.branch_name,
                'city': result.city,
                'state': result.state,
                'confidence_score': result.confidence_score,
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
        
        logger.info(f"""
        Bulk Bank Validation Complete:
        ==============================
        Total Records: {total_count}
        Valid Bank Details: {valid_count}
        Invalid Bank Details: {total_count - valid_count}
        Validity Rate: {validity_rate:.2f}%
        Average Confidence: {results_df['confidence_score'].mean():.2f}%
        
        Bank Distribution:
        {json.dumps(dict(bank_stats), indent=2)}
        """)
        
        return results_df

def create_sample_bank_dataset(num_records: int = 500) -> pd.DataFrame:
    """Create sample bank dataset for testing"""
    
    import random
    np.random.seed(42)
    random.seed(42)
    
    # Sample IFSC codes and account numbers
    sample_ifsc_codes = [
        'SBIN0001234', 'HDFC0000123', 'ICIC0001234', 'AXIS0000456',
        'PUNB0012345', 'UBIN0067890', 'CNRB0001122', 'BKID0003344',
        'YESB0000555', 'KKBK0000666', 'INVALID123', 'SBIN'  # Some invalid
    ]
    
    data = []
    
    for i in range(num_records):
        if i % 20 == 0:
            # 5% invalid IFSC
            ifsc = random.choice(['INVALID123', 'SBIN', 'ABCD1234567', ''])
            account = f"{random.randint(1000000000, 9999999999)}"
        else:
            # Valid IFSC codes
            ifsc = random.choice(sample_ifsc_codes[:10])  # Valid ones only
            
            # Generate realistic account numbers based on bank
            if ifsc.startswith('SBIN'):
                account = f"{random.randint(100000000, 9999999999)}"  # SBI format
            elif ifsc.startswith('HDFC'):
                account = f"{random.randint(10000000000, 99999999999999)}"  # HDFC format
            elif ifsc.startswith('ICIC'):
                account = f"{random.randint(100000000000, 999999999999)}"  # ICICI format
            else:
                account = f"{random.randint(1000000000, 99999999999)}"
        
        # Add some MICR codes
        micr = f"{random.randint(100000000, 999999999)}" if i % 3 == 0 else None
        
        data.append({
            'account_number': account,
            'ifsc_code': ifsc,
            'micr_code': micr,
            'customer_name': f"Customer {i+1}",
            'account_type': random.choice(['Savings', 'Current', 'Fixed Deposit']),
            'created_date': datetime.now() - timedelta(days=random.randint(1, 1000))
        })
    
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of bank validation system"""
    
    print("🏦 Indian Bank Validation System Demo")
    print("भारतीय बैंक सत्यापन प्रणाली का प्रदर्शन\n")
    
    # Initialize validator
    validator = IndianBankValidationSystem()
    
    # Test 1: IFSC validation
    print("Test 1: IFSC Code Validation")
    print("=" * 30)
    
    test_ifsc_codes = [
        'SBIN0001234',    # Valid SBI
        'HDFC0000123',    # Valid HDFC
        'ICIC0001234',    # Valid ICICI
        'INVALID123',     # Invalid format
        'SBIN',           # Too short
        'SBIN1001234',    # Wrong 5th character
        'sbin0001234',    # Lowercase
        'ABCD0123456'     # Unknown bank
    ]
    
    for ifsc in test_ifsc_codes:
        result = validator.validate_ifsc_format(ifsc)
        print(f"""
    IFSC: {ifsc}
    Valid: {'✅' if result['is_valid_format'] else '❌'}
    Bank Code: {result['bank_code']}
    Branch Code: {result['branch_code']}
    Errors: {len(result['errors'])}
    Warnings: {len(result['warnings'])}
        """)
    
    # Test 2: Account number validation
    print("\nTest 2: Account Number Validation")
    print("=" * 35)
    
    test_accounts = [
        ('12345678901', 'SBIN0001234'),     # SBI account
        ('123456789012345', 'HDFC0000123'), # HDFC account
        ('123456789012', 'ICIC0001234'),    # ICICI account
        ('1111111111', 'AXIS0000456'),      # Suspicious pattern
        ('123', 'SBIN0001234'),             # Too short
        ('AB123456789', 'HDFC0000123')      # Contains letters
    ]
    
    for account, ifsc in test_accounts:
        result = validator.validate_account_number(account, ifsc)
        print(f"""
    Account: {account}
    IFSC: {ifsc}
    Valid: {'✅' if result['is_valid_format'] else '❌'}
    Bank: {result['detected_bank'] or 'Unknown'}
    Type: {result['account_type']}
    Errors: {len(result['errors'])}
    Warnings: {len(result['warnings'])}
        """)
    
    # Test 3: Complete bank validation
    print("\nTest 3: Complete Bank Validation")
    print("=" * 35)
    
    complete_test_cases = [
        {
            'account': '12345678901',
            'ifsc': 'SBIN0001234',
            'micr': '400002002'
        },
        {
            'account': '123456789012345',
            'ifsc': 'HDFC0000123',
            'micr': '110240001'
        },
        {
            'account': '1111111111',
            'ifsc': 'INVALID123',
            'micr': None
        }
    ]
    
    for case in complete_test_cases:
        result = validator.complete_bank_validation(
            case['account'], case['ifsc'], case['micr']
        )
        print(f"""
    Account: {case['account']}
    IFSC: {case['ifsc']}
    Valid: {'✅' if result.is_valid else '❌'}
    Bank: {result.bank_name}
    Branch: {result.branch_name}
    City: {result.city}
    State: {result.state}
    Confidence: {result.confidence_score:.1f}%
    Errors: {len(result.errors)}
    Warnings: {len(result.warnings)}
        """)
    
    # Test 4: Bulk validation
    print("\nTest 4: Bulk Dataset Validation")
    print("=" * 35)
    
    # Create test dataset
    test_df = create_sample_bank_dataset(100)
    print(f"Created test dataset with {len(test_df)} bank records")
    
    # Perform bulk validation
    validation_results = validator.bulk_validate_bank_dataset(
        test_df, 
        account_column='account_number',
        ifsc_column='ifsc_code',
        micr_column='micr_code'
    )
    
    # Generate summary
    bank_distribution = validation_results['bank_name'].value_counts()
    state_distribution = validation_results['state'].value_counts()
    
    print(f"""
    Bulk Validation Summary:
    =======================
    Total Records: {len(validation_results)}
    Valid Bank Details: {validation_results['is_valid'].sum()}
    Invalid Bank Details: {(~validation_results['is_valid']).sum()}
    Validity Rate: {(validation_results['is_valid'].sum() / len(validation_results)) * 100:.2f}%
    Average Confidence: {validation_results['confidence_score'].mean():.2f}%
    
    Bank Distribution:
    {bank_distribution.head().to_dict()}
    
    State Distribution:
    {state_distribution.head().to_dict()}
    """)
    
    print("\n✅ Indian Bank Validation System Demo Complete!")
    print("Banking system ready - बैंकिंग सिस्टम तैयार!")
    
    return {
        'validation_results': validation_results,
        'test_cases': complete_test_cases
    }

if __name__ == "__main__":
    results = main()