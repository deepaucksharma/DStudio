#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 10
Indian Mobile Number Validation System

Complete mobile number validation for Indian telecom networks
भारतीय मोबाइल नंबर की पूरी जांच करने का system like telecom operators

Author: DStudio Team
Context: Telecom validation like Jio, Airtel, Vi network systems
Scale: 100+ crore mobile numbers in India validation
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
import phonenumbers
from phonenumbers import NumberParseException

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - मोबाइल जांच - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MobileValidationResult:
    """Mobile number validation result structure"""
    original_number: str
    formatted_number: str
    is_valid: bool
    operator: Optional[str]
    circle: Optional[str]
    number_type: str
    errors: List[str]
    warnings: List[str]
    confidence_score: float
    metadata: Dict

class IndianMobileValidationSystem:
    """
    Complete Indian mobile number validation system
    भारतीय मोबाइल नंबर validation system for telecom operators
    
    Features:
    1. Format validation with multiple input formats
    2. Operator identification (Jio, Airtel, Vi, BSNL, etc.)
    3. Circle/state identification  
    4. Number portability tracking
    5. Bulk validation for customer databases
    6. Fraud detection for fake numbers
    
    Scale: Handles 100+ crore mobile numbers like telecom databases
    """
    
    def __init__(self):
        """Initialize with Indian telecom operator data"""
        
        # Indian mobile number series mapping - भारतीय मोबाइल नंबर series
        # Based on DoT (Department of Telecommunications) allocations
        self.operator_series = {
            'Jio': {
                'series': ['70', '71', '72', '73', '74', '75', '76', '77', '78', '79'],
                'company': 'Reliance Jio',
                'launch_year': 2016,
                'technology': '4G/5G'
            },
            'Airtel': {
                'series': ['60', '61', '62', '63', '64', '65', '66', '67', '68', '69', 
                          '70', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89'],
                'company': 'Bharti Airtel',
                'launch_year': 1995,
                'technology': '2G/3G/4G/5G'
            },
            'Vi': {  # Vodafone Idea
                'series': ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99'],
                'company': 'Vodafone Idea Limited',
                'launch_year': 1994,
                'technology': '2G/3G/4G'
            },
            'BSNL': {
                'series': ['60', '62', '63', '64', '65', '66', '67', '68', '69', '94', '95'],
                'company': 'Bharat Sanchar Nigam Limited',
                'launch_year': 2000,
                'technology': '2G/3G/4G'
            },
            'MTNL': {
                'series': ['99'],
                'company': 'Mahanagar Telephone Nigam Limited',
                'launch_year': 1986,
                'technology': '2G/3G'
            }
        }
        
        # Telecom circles mapping - दूरसंचार सर्कल mapping
        self.telecom_circles = {
            'Delhi': ['011'],
            'Mumbai': ['022'],
            'Kolkata': ['033'], 
            'Chennai': ['044'],
            'Andhra Pradesh': ['040', '0863', '0866', '0870'],
            'Assam': ['0361', '0373', '0374'],
            'Bihar': ['0612', '0621', '0651'],
            'Gujarat': ['079', '0261', '0265', '0281'],
            'Haryana': ['0124', '0129', '0131'],
            'Himachal Pradesh': ['0177', '0180', '0193'],
            'Jammu & Kashmir': ['0191', '0194', '0196'],
            'Karnataka': ['080', '0824', '0831', '0836'],
            'Kerala': ['0484', '0487', '0495', '0496'],
            'Madhya Pradesh': ['0755', '0761', '0771', '0788'],
            'Maharashtra': ['020', '0212', '0217', '0233'],
            'North East': ['0370', '0389', '0394'],
            'Orissa': ['0674', '0661', '0663', '0671'],
            'Punjab': ['0161', '0172', '0175', '0181'],
            'Rajasthan': ['0141', '0145', '0151', '0294'],
            'Tamil Nadu': ['0422', '0431', '0462', '0468'],
            'Uttar Pradesh (East)': ['0522', '0542', '0551', '0562'],
            'Uttar Pradesh (West)': ['0120', '0512', '0571', '0581'],
            'West Bengal': ['0343', '0353', '0364', '0384']
        }
        
        # Mobile number patterns
        self.indian_mobile_patterns = {
            'standard': r'^[6-9]\d{9}$',
            'with_country_code': r'^(\+91|91|0)?[6-9]\d{9}$',
            'with_spaces': r'^(\+91|91|0)?\s*[6-9]\d{4}\s*\d{5}$',
            'with_hyphens': r'^(\+91|91|0)?[6-9]\d{4}-\d{5}$'
        }
        
        # Suspicious number patterns for fraud detection
        self.suspicious_patterns = {
            'sequential': r'(012|123|234|345|456|567|678|789|890)',
            'repeated': r'(\d)\1{4,}',
            'all_same': r'^(\d)\1{9}$',
            'obvious_fake': r'(1111111111|2222222222|0000000000)',
            'test_numbers': r'(1234567890|0987654321|5555555555)'
        }
        
        # Number portability tracking (MNP - Mobile Number Portability)
        self.mnp_database = {}  # In production, this would be from official MNP database
        
        logger.info("Indian Mobile Validation System initialized - मोबाइल सिस्टम तैयार!")
        logger.info(f"Supporting {len(self.operator_series)} major operators")

    def clean_mobile_number(self, mobile: str) -> str:
        """
        Clean and standardize mobile number format
        मोबाइल नंबर को clean और standardize करना
        """
        
        if not mobile:
            return ""
        
        # Convert to string and remove all non-digit characters except +
        mobile_str = str(mobile).strip()
        
        # Remove common separators
        mobile_clean = re.sub(r'[\s\-\(\)\.]', '', mobile_str)
        
        # Handle country codes
        if mobile_clean.startswith('+91'):
            mobile_clean = mobile_clean[3:]
        elif mobile_clean.startswith('91') and len(mobile_clean) == 12:
            mobile_clean = mobile_clean[2:]
        elif mobile_clean.startswith('0') and len(mobile_clean) == 11:
            mobile_clean = mobile_clean[1:]
        
        return mobile_clean

    def validate_mobile_format(self, mobile: str) -> Dict[str, any]:
        """
        Validate Indian mobile number format
        भारतीय मोबाइल नंबर का format validation
        """
        
        original_number = mobile
        cleaned_number = self.clean_mobile_number(mobile)
        
        validation_result = {
            'original_number': original_number,
            'cleaned_number': cleaned_number,
            'is_valid_format': False,
            'errors': [],
            'warnings': [],
            'detected_format': None
        }
        
        # Check if empty
        if not cleaned_number:
            validation_result['errors'].append("Mobile number cannot be empty")
            return validation_result
        
        # Check for non-digit characters
        if not cleaned_number.isdigit():
            validation_result['errors'].append("Mobile number must contain only digits after cleaning")
            return validation_result
        
        # Check length - must be exactly 10 digits
        if len(cleaned_number) != 10:
            validation_result['errors'].append(f"Mobile number must be exactly 10 digits, got {len(cleaned_number)}")
            return validation_result
        
        # Check first digit - must be 6, 7, 8, or 9
        if not cleaned_number[0] in ['6', '7', '8', '9']:
            validation_result['errors'].append("Indian mobile numbers must start with 6, 7, 8, or 9")
            return validation_result
        
        # Detect original format
        for format_name, pattern in self.indian_mobile_patterns.items():
            if re.match(pattern, original_number):
                validation_result['detected_format'] = format_name
                break
        
        # Additional validations
        if cleaned_number.startswith('0'):
            validation_result['warnings'].append("Number starts with 0 - might be landline")
        
        if len(set(cleaned_number)) == 1:
            validation_result['errors'].append("All digits are the same - likely invalid")
            return validation_result
        
        validation_result['is_valid_format'] = True
        logger.debug(f"Format validation passed for: {cleaned_number[:3]}*****{cleaned_number[-2:]}")
        
        return validation_result

    def identify_operator(self, mobile: str) -> Dict[str, any]:
        """
        Identify telecom operator from mobile number
        मोबाइल नंबर से operator की पहचान करना
        """
        
        cleaned_number = self.clean_mobile_number(mobile)
        
        if len(cleaned_number) != 10:
            return {
                'operator': None,
                'company': None,
                'series': None,
                'confidence': 0.0,
                'technology': None
            }
        
        # Get first two digits for series identification
        number_series = cleaned_number[:2]
        
        # Check against operator series
        for operator, info in self.operator_series.items():
            if number_series in info['series']:
                return {
                    'operator': operator,
                    'company': info['company'],
                    'series': number_series,
                    'confidence': 90.0,  # High confidence for series match
                    'technology': info['technology'],
                    'launch_year': info['launch_year']
                }
        
        # If no exact match, try partial matching
        possible_operators = []
        for operator, info in self.operator_series.items():
            for series in info['series']:
                if number_series.startswith(series[0]):
                    possible_operators.append((operator, info, 50.0))
        
        if possible_operators:
            # Return the most likely operator
            best_match = max(possible_operators, key=lambda x: x[2])
            return {
                'operator': best_match[0],
                'company': best_match[1]['company'],
                'series': number_series,
                'confidence': best_match[2],
                'technology': best_match[1]['technology'],
                'note': 'Partial match - may not be accurate'
            }
        
        return {
            'operator': 'Unknown',
            'company': 'Unknown Operator',
            'series': number_series,
            'confidence': 0.0,
            'technology': 'Unknown',
            'note': 'Series not found in database'
        }

    def detect_fraud_patterns(self, mobile: str) -> Dict[str, any]:
        """
        Detect fraud patterns in mobile numbers
        मोबाइल नंबर में fraud patterns की detection
        """
        
        cleaned_number = self.clean_mobile_number(mobile)
        
        fraud_analysis = {
            'is_suspicious': False,
            'fraud_indicators': [],
            'risk_score': 0,
            'risk_level': 'LOW',
            'recommendations': []
        }
        
        # Check suspicious patterns
        for pattern_name, pattern in self.suspicious_patterns.items():
            if re.search(pattern, cleaned_number):
                fraud_analysis['fraud_indicators'].append(f"Matches {pattern_name} pattern")
                
                # Assign risk scores
                risk_scores = {
                    'sequential': 15,
                    'repeated': 20,
                    'all_same': 25,
                    'obvious_fake': 30,
                    'test_numbers': 35
                }
                fraud_analysis['risk_score'] += risk_scores.get(pattern_name, 10)
        
        # Check for mathematical sequences
        digits = [int(d) for d in cleaned_number]
        
        # Ascending sequence
        if all(digits[i] <= digits[i+1] for i in range(len(digits)-1)):
            fraud_analysis['fraud_indicators'].append("Ascending sequence detected")
            fraud_analysis['risk_score'] += 12
        
        # Descending sequence
        if all(digits[i] >= digits[i+1] for i in range(len(digits)-1)):
            fraud_analysis['fraud_indicators'].append("Descending sequence detected")
            fraud_analysis['risk_score'] += 12
        
        # Too many repeated digits
        digit_counts = Counter(digits)
        max_repeat = max(digit_counts.values())
        if max_repeat >= 6:
            fraud_analysis['fraud_indicators'].append(f"Digit repeated {max_repeat} times")
            fraud_analysis['risk_score'] += 10
        
        # Determine risk level
        if fraud_analysis['risk_score'] >= 40:
            fraud_analysis['risk_level'] = 'HIGH'
            fraud_analysis['is_suspicious'] = True
            fraud_analysis['recommendations'].append("Block number - high fraud probability")
        elif fraud_analysis['risk_score'] >= 20:
            fraud_analysis['risk_level'] = 'MEDIUM'
            fraud_analysis['recommendations'].append("Additional verification required")
        else:
            fraud_analysis['risk_level'] = 'LOW'
            fraud_analysis['recommendations'].append("Number appears legitimate")
        
        return fraud_analysis

    def validate_with_phonenumbers_lib(self, mobile: str) -> Dict[str, any]:
        """
        Validate using Google's phonenumbers library for additional verification
        Google phonenumbers library से additional verification
        """
        
        try:
            # Parse the number with India country code
            parsed_number = phonenumbers.parse(mobile, "IN")
            
            # Various validations
            is_valid = phonenumbers.is_valid_number(parsed_number)
            is_possible = phonenumbers.is_possible_number(parsed_number)
            number_type = phonenumbers.number_type(parsed_number)
            
            # Format in different ways
            international_format = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            national_format = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
            )
            e164_format = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
            
            # Number type mapping
            type_mapping = {
                phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
                phonenumbers.PhoneNumberType.FIXED_LINE: 'Landline',
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Mobile or Landline',
                phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
                phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
                phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown'
            }
            
            return {
                'is_valid': is_valid,
                'is_possible': is_possible,
                'number_type': type_mapping.get(number_type, 'Unknown'),
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number,
                'international_format': international_format,
                'national_format': national_format,
                'e164_format': e164_format,
                'validation_source': 'Google phonenumbers library'
            }
            
        except NumberParseException as e:
            return {
                'is_valid': False,
                'error': str(e),
                'error_type': e.error_type,
                'validation_source': 'Google phonenumbers library'
            }

    def complete_mobile_validation(self, mobile: str) -> MobileValidationResult:
        """
        Complete mobile number validation with all checks
        सभी जांच के साथ complete mobile validation
        """
        
        logger.info(f"Starting complete mobile validation for: {str(mobile)[:3]}*****")
        
        # Step 1: Format validation
        format_result = self.validate_mobile_format(mobile)
        
        if not format_result['is_valid_format']:
            return MobileValidationResult(
                original_number=mobile,
                formatted_number=format_result['cleaned_number'],
                is_valid=False,
                operator=None,
                circle=None,
                number_type='Invalid',
                errors=format_result['errors'],
                warnings=format_result['warnings'],
                confidence_score=0.0,
                metadata={'format_result': format_result}
            )
        
        cleaned_number = format_result['cleaned_number']
        
        # Step 2: Operator identification
        operator_result = self.identify_operator(cleaned_number)
        
        # Step 3: Fraud detection
        fraud_result = self.detect_fraud_patterns(cleaned_number)
        
        # Step 4: phonenumbers library validation
        phonenumbers_result = self.validate_with_phonenumbers_lib(mobile)
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(
            format_result, operator_result, fraud_result, phonenumbers_result
        )
        
        # Determine if mobile is valid
        is_valid = (
            format_result['is_valid_format'] and
            not fraud_result['is_suspicious'] and
            phonenumbers_result.get('is_valid', True) and
            operator_result['operator'] != 'Unknown'
        )
        
        # Format the number consistently
        formatted_number = f"+91 {cleaned_number[:5]} {cleaned_number[5:]}"
        
        # Collect all errors and warnings
        all_errors = format_result['errors'].copy()
        all_warnings = format_result['warnings'] + fraud_result['fraud_indicators']
        
        if not phonenumbers_result.get('is_valid', True):
            all_errors.append(f"phonenumbers validation failed: {phonenumbers_result.get('error', 'Unknown error')}")
        
        logger.info(f"Complete mobile validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return MobileValidationResult(
            original_number=mobile,
            formatted_number=formatted_number,
            is_valid=is_valid,
            operator=operator_result['operator'],
            circle=None,  # Would be determined by area code analysis
            number_type=phonenumbers_result.get('number_type', 'Mobile'),
            errors=all_errors,
            warnings=all_warnings,
            confidence_score=confidence_score,
            metadata={
                'format_result': format_result,
                'operator_result': operator_result,
                'fraud_result': fraud_result,
                'phonenumbers_result': phonenumbers_result
            }
        )

    def _calculate_confidence_score(self, format_result: Dict, operator_result: Dict,
                                  fraud_result: Dict, phonenumbers_result: Dict) -> float:
        """Calculate overall confidence score for mobile validation"""
        
        score = 0.0
        
        # Format validation (25%)
        if format_result['is_valid_format']:
            score += 25.0
        
        # Operator identification (25%)
        operator_confidence = operator_result.get('confidence', 0)
        score += (operator_confidence / 100) * 25.0
        
        # Fraud check (25%)
        fraud_risk = fraud_result.get('risk_score', 0)
        fraud_score = max(0, 25 - (fraud_risk * 0.625))  # Higher risk = lower score
        score += fraud_score
        
        # phonenumbers library validation (25%)
        if phonenumbers_result.get('is_valid', False):
            score += 25.0
        elif phonenumbers_result.get('is_possible', False):
            score += 15.0
        
        return min(score, 100.0)

    def bulk_validate_mobile_dataset(self, df: pd.DataFrame, 
                                   mobile_column: str = 'mobile') -> pd.DataFrame:
        """
        Bulk mobile validation for customer databases
        Customer databases के लिए bulk mobile validation
        """
        
        logger.info(f"Starting bulk mobile validation for {len(df)} records")
        
        validation_results = []
        operator_stats = defaultdict(int)
        
        for index, row in df.iterrows():
            mobile = row[mobile_column]
            
            # Validate each mobile number
            result = self.complete_mobile_validation(mobile)
            
            # Update operator statistics
            if result.operator:
                operator_stats[result.operator] += 1
            
            validation_results.append({
                'row_index': index,
                'original_mobile': mobile,
                'formatted_mobile': result.formatted_number,
                'is_valid': result.is_valid,
                'operator': result.operator,
                'number_type': result.number_type,
                'confidence_score': result.confidence_score,
                'error_count': len(result.errors),
                'warning_count': len(result.warnings),
                'risk_level': result.metadata.get('fraud_result', {}).get('risk_level', 'LOW')
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
        Bulk Mobile Validation Complete:
        ===============================
        Total Records: {total_count}
        Valid Mobiles: {valid_count}
        Invalid Mobiles: {total_count - valid_count}
        Validity Rate: {validity_rate:.2f}%
        Average Confidence: {results_df['confidence_score'].mean():.2f}%
        
        Operator Distribution:
        {json.dumps(dict(operator_stats), indent=2)}
        """)
        
        return results_df

def create_sample_mobile_dataset(num_records: int = 1000) -> pd.DataFrame:
    """Create sample mobile dataset for testing"""
    
    # Common mobile patterns for testing
    import random
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    # Operator series for generating realistic numbers
    jio_series = ['70', '71', '72', '73', '74', '75', '76', '77', '78', '79']
    airtel_series = ['60', '61', '62', '63', '64', '65', '66', '67', '68', '69']
    vi_series = ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99']
    
    for i in range(num_records):
        if i % 20 == 0:
            # 5% invalid numbers
            mobile = f"{random.randint(1000000000, 5999999999)}"  # Invalid first digit
        elif i % 15 == 0:
            # Some suspicious patterns
            mobile = "9999999999"  # All 9s
        elif i % 10 == 0:
            # Different formats
            series = random.choice(jio_series + airtel_series + vi_series)
            number = f"{series}{random.randint(10000000, 99999999)}"
            mobile = f"+91 {number[:5]} {number[5:]}"  # With formatting
        else:
            # Valid numbers
            series = random.choice(jio_series + airtel_series + vi_series)
            mobile = f"{series}{random.randint(10000000, 99999999)}"
        
        # Add customer data
        data.append({
            'mobile': mobile,
            'customer_name': f"Customer {i+1}",
            'city': random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']),
            'registration_date': datetime.now() - timedelta(days=random.randint(1, 365))
        })
    
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of mobile validation system"""
    
    print("📱 Indian Mobile Validation System Demo")
    print("भारतीय मोबाइल नंबर सत्यापन प्रणाली का प्रदर्शन\n")
    
    # Initialize validator
    validator = IndianMobileValidationSystem()
    
    # Test 1: Individual mobile validations
    print("Test 1: Individual Mobile Validations")
    print("=" * 45)
    
    test_mobiles = [
        "9876543210",          # Valid format
        "+91 98765 43210",     # With country code and formatting
        "7890123456",          # Jio number
        "6123456789",          # Airtel number
        "9123456789",          # Vi number
        "1234567890",          # Invalid first digit
        "98765432101",         # Too long
        "987654321",           # Too short
        "9999999999",          # All 9s (suspicious)
        "0987654321",          # Starts with 0
        "+91-9876-543-210",    # Different formatting
        "919876543210"         # With country code
    ]
    
    for mobile in test_mobiles:
        result = validator.complete_mobile_validation(mobile)
        print(f"""
    Mobile: {mobile}
    Valid: {'✅' if result.is_valid else '❌'}
    Formatted: {result.formatted_number}
    Operator: {result.operator or 'Unknown'}
    Type: {result.number_type}
    Confidence: {result.confidence_score:.1f}%
    Errors: {len(result.errors)}
    Warnings: {len(result.warnings)}
        """)
    
    # Test 2: Operator identification
    print("\nTest 2: Operator Identification")
    print("=" * 35)
    
    operator_test_numbers = [
        "7012345678",  # Jio
        "6012345678",  # Airtel  
        "9012345678",  # Vi
        "9412345678",  # BSNL
        "9912345678"   # MTNL
    ]
    
    for mobile in operator_test_numbers:
        operator_result = validator.identify_operator(mobile)
        print(f"""
    Mobile: {mobile}
    Operator: {operator_result['operator']}
    Company: {operator_result['company']}
    Technology: {operator_result['technology']}
    Confidence: {operator_result['confidence']:.1f}%
        """)
    
    # Test 3: Fraud detection
    print("\nTest 3: Fraud Detection")
    print("=" * 25)
    
    suspicious_numbers = [
        "1234567890",  # Sequential
        "9999999999",  # All same
        "1111111111",  # All same
        "5555555555",  # Test number
        "0987654321",  # Descending
        "7777777777"   # Repeated
    ]
    
    for mobile in suspicious_numbers:
        fraud_result = validator.detect_fraud_patterns(mobile)
        print(f"""
    Mobile: {mobile}
    Suspicious: {'🚨 YES' if fraud_result['is_suspicious'] else '✅ NO'}
    Risk Level: {fraud_result['risk_level']}
    Risk Score: {fraud_result['risk_score']}
    Indicators: {len(fraud_result['fraud_indicators'])}
        """)
    
    # Test 4: Bulk validation
    print("\nTest 4: Bulk Dataset Validation")
    print("=" * 35)
    
    # Create test dataset
    test_df = create_sample_mobile_dataset(200)
    print(f"Created test dataset with {len(test_df)} mobile records")
    
    # Perform bulk validation
    validation_results = validator.bulk_validate_mobile_dataset(test_df, 'mobile')
    
    # Generate summary
    operator_distribution = validation_results['operator'].value_counts()
    risk_distribution = validation_results['risk_level'].value_counts()
    
    print(f"""
    Bulk Validation Summary:
    =======================
    Total Records: {len(validation_results)}
    Valid Mobiles: {validation_results['is_valid'].sum()}
    Invalid Mobiles: {(~validation_results['is_valid']).sum()}
    Validity Rate: {(validation_results['is_valid'].sum() / len(validation_results)) * 100:.2f}%
    Average Confidence: {validation_results['confidence_score'].mean():.2f}%
    
    Operator Distribution:
    {operator_distribution.to_dict()}
    
    Risk Level Distribution:
    {risk_distribution.to_dict()}
    """)
    
    print("\n✅ Indian Mobile Validation System Demo Complete!")
    print("Telecom system ready - दूरसंचार सिस्टम तैयार!")
    
    return {
        'validation_results': validation_results,
        'test_results': test_mobiles
    }

if __name__ == "__main__":
    results = main()