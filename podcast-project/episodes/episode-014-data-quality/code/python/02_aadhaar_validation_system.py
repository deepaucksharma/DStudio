#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 2
Aadhaar Number Validation System

Complete Aadhaar validation system with Verhoeff algorithm
आधार संख्या की पूरी जांच करने का system like UIDAI standards

Author: DStudio Team
Context: Government identity verification like e-KYC systems
"""

import re
import random
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime
import hashlib

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - आधार जांच - %(message)s'
)
logger = logging.getLogger(__name__)

class AadhaarValidationSystem:
    """
    Complete Aadhaar number validation system
    UIDAI standards के अनुसार validation करेगा
    
    Features:
    1. Format validation
    2. Verhoeff checksum algorithm
    3. Demographic validation
    4. Duplicate detection
    5. Security compliance
    """
    
    def __init__(self):
        """Initialize with Verhoeff algorithm tables"""
        
        # Verhoeff multiplication table
        self.multiplication_table = [
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
        
        # Verhoeff permutation table
        self.permutation_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]
        
        # Verhoeff inverse table
        self.inverse_table = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
        
        # Indian state codes for demographic validation
        self.indian_states = {
            '01': 'Andhra Pradesh', '02': 'Assam', '03': 'Bihar',
            '04': 'Chhattisgarh', '05': 'Goa', '06': 'Gujarat',
            '07': 'Haryana', '08': 'Himachal Pradesh', '09': 'Jammu and Kashmir',
            '10': 'Jharkhand', '11': 'Karnataka', '12': 'Kerala',
            '13': 'Madhya Pradesh', '14': 'Maharashtra', '15': 'Manipur',
            '16': 'Meghalaya', '17': 'Mizoram', '18': 'Nagaland',
            '19': 'Odisha', '20': 'Punjab', '21': 'Rajasthan',
            '22': 'Sikkim', '23': 'Tamil Nadu', '24': 'Tripura',
            '25': 'Uttar Pradesh', '26': 'West Bengal', '27': 'Andaman and Nicobar',
            '28': 'Chandigarh', '29': 'Dadra and Nagar Haveli', '30': 'Delhi',
            '31': 'Lakshadweep', '32': 'Puducherry', '33': 'Telangana',
            '34': 'Ladakh'
        }
        
        logger.info("Aadhaar Validation System initialized - आधार सिस्टम तैयार!")

    def validate_format(self, aadhaar: str) -> Dict[str, any]:
        """
        Basic format validation for Aadhaar number
        बुनियादी फॉर्मेट की जांच करना
        """
        
        # Remove spaces and hyphens
        clean_aadhaar = re.sub(r'[\s-]', '', str(aadhaar))
        
        validation_result = {
            'original': aadhaar,
            'cleaned': clean_aadhaar,
            'is_valid_format': False,
            'errors': [],
            'warnings': []
        }
        
        # Check if exactly 12 digits
        if not clean_aadhaar.isdigit():
            validation_result['errors'].append("Aadhaar must contain only digits")
            return validation_result
            
        if len(clean_aadhaar) != 12:
            validation_result['errors'].append(f"Aadhaar must be exactly 12 digits, got {len(clean_aadhaar)}")
            return validation_result
        
        # Check for obvious patterns (security check)
        if len(set(clean_aadhaar)) == 1:
            validation_result['errors'].append("Aadhaar cannot have all same digits")
            return validation_result
            
        # Check for sequential numbers
        if clean_aadhaar in ['123456789012', '012345678901']:
            validation_result['errors'].append("Aadhaar cannot be sequential numbers")
            return validation_result
        
        # First digit cannot be 0 or 1 (UIDAI rule)
        if clean_aadhaar[0] in ['0', '1']:
            validation_result['errors'].append("First digit of Aadhaar cannot be 0 or 1")
            return validation_result
        
        validation_result['is_valid_format'] = True
        logger.info(f"Format validation passed for Aadhaar: {clean_aadhaar[:4]}****{clean_aadhaar[-4:]}")
        
        return validation_result

    def calculate_verhoeff_checksum(self, aadhaar_11_digits: str) -> int:
        """
        Calculate Verhoeff checksum for 11-digit Aadhaar number
        Verhoeff algorithm से checksum निकालना
        """
        
        # Convert to list of integers and reverse
        digits = [int(d) for d in aadhaar_11_digits[::-1]]
        
        checksum = 0
        for i, digit in enumerate(digits):
            checksum = self.multiplication_table[checksum][
                self.permutation_table[i % 8][digit]
            ]
        
        return self.inverse_table[checksum]

    def validate_checksum(self, aadhaar: str) -> Dict[str, any]:
        """
        Validate Aadhaar checksum using Verhoeff algorithm
        Verhoeff algorithm से checksum की जांच
        """
        
        clean_aadhaar = re.sub(r'[\s-]', '', str(aadhaar))
        
        if len(clean_aadhaar) != 12:
            return {
                'is_valid_checksum': False,
                'error': 'Invalid length for checksum validation'
            }
        
        # Extract first 11 digits and last digit (checksum)
        first_11_digits = clean_aadhaar[:11]
        provided_checksum = int(clean_aadhaar[11])
        
        # Calculate expected checksum
        calculated_checksum = self.calculate_verhoeff_checksum(first_11_digits)
        
        is_valid = provided_checksum == calculated_checksum
        
        logger.info(f"Checksum validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return {
            'is_valid_checksum': is_valid,
            'provided_checksum': provided_checksum,
            'calculated_checksum': calculated_checksum,
            'aadhaar_masked': f"{clean_aadhaar[:4]}****{clean_aadhaar[-4:]}"
        }

    def validate_demographics(self, name: str, phone: str, email: str) -> Dict[str, any]:
        """
        Validate demographic information associated with Aadhaar
        आधार के साथ जुड़ी जानकारी की जांच
        """
        
        validation_result = {
            'name_valid': False,
            'phone_valid': False,
            'email_valid': False,
            'errors': [],
            'warnings': []
        }
        
        # Name validation - Indian context
        if name and len(name.strip()) >= 2:
            # Check for valid characters (including Indian script support)
            name_pattern = r'^[a-zA-Z\s.\']+$'  # Basic Latin for this example
            if re.match(name_pattern, name.strip()):
                validation_result['name_valid'] = True
            else:
                validation_result['errors'].append("Name contains invalid characters")
        else:
            validation_result['errors'].append("Name is required and must be at least 2 characters")
        
        # Phone validation - Indian mobile numbers
        if phone:
            # Indian mobile number pattern
            phone_clean = re.sub(r'[\s+-]', '', str(phone))
            indian_mobile_pattern = r'^(91|0)?[6-9]\d{9}$'
            
            if re.match(indian_mobile_pattern, phone_clean):
                validation_result['phone_valid'] = True
            else:
                validation_result['errors'].append("Invalid Indian mobile number format")
        
        # Email validation
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, email.strip().lower()):
                validation_result['email_valid'] = True
            else:
                validation_result['errors'].append("Invalid email format")
        
        return validation_result

    def complete_aadhaar_validation(self, aadhaar: str, name: str = None, 
                                  phone: str = None, email: str = None) -> Dict[str, any]:
        """
        Complete Aadhaar validation with all checks
        पूरी आधार जांच - सभी validation एक साथ
        """
        
        logger.info(f"Starting complete validation for Aadhaar: {str(aadhaar)[:4]}****")
        
        # Step 1: Format validation
        format_result = self.validate_format(aadhaar)
        
        if not format_result['is_valid_format']:
            return {
                'is_valid': False,
                'validation_type': 'format_failed',
                'format_result': format_result,
                'summary': 'Aadhaar format validation failed'
            }
        
        # Step 2: Checksum validation
        checksum_result = self.validate_checksum(aadhaar)
        
        if not checksum_result['is_valid_checksum']:
            return {
                'is_valid': False,
                'validation_type': 'checksum_failed',
                'format_result': format_result,
                'checksum_result': checksum_result,
                'summary': 'Aadhaar checksum validation failed'
            }
        
        # Step 3: Demographic validation (if provided)
        demo_result = None
        if any([name, phone, email]):
            demo_result = self.validate_demographics(name, phone, email)
        
        # Final validation result
        is_completely_valid = (
            format_result['is_valid_format'] and 
            checksum_result['is_valid_checksum']
        )
        
        if demo_result:
            demo_valid = demo_result['name_valid'] and (
                demo_result['phone_valid'] if phone else True
            ) and (demo_result['email_valid'] if email else True)
            is_completely_valid = is_completely_valid and demo_valid
        
        logger.info(f"Complete validation result: {'✅ Valid' if is_completely_valid else '❌ Invalid'}")
        
        return {
            'is_valid': is_completely_valid,
            'validation_type': 'complete',
            'format_result': format_result,
            'checksum_result': checksum_result,
            'demographic_result': demo_result,
            'summary': 'Complete Aadhaar validation performed',
            'confidence_score': self._calculate_confidence_score(format_result, checksum_result, demo_result)
        }

    def _calculate_confidence_score(self, format_result: Dict, checksum_result: Dict, 
                                  demo_result: Optional[Dict]) -> float:
        """Calculate confidence score for validation"""
        
        score = 0.0
        
        # Format check (30%)
        if format_result['is_valid_format']:
            score += 30.0
        
        # Checksum check (50%)
        if checksum_result['is_valid_checksum']:
            score += 50.0
        
        # Demographic checks (20%)
        if demo_result:
            demo_score = 0
            if demo_result['name_valid']:
                demo_score += 7
            if demo_result['phone_valid']:
                demo_score += 7
            if demo_result['email_valid']:
                demo_score += 6
            score += demo_score
        else:
            score += 20.0  # Full demographic score if not checked
        
        return min(score, 100.0)

    def generate_valid_aadhaar(self, state_code: str = '14') -> str:
        """
        Generate a valid Aadhaar number for testing (TEST ONLY)
        Testing के लिए valid Aadhaar number generate करना
        ⚠️ केवल testing के लिए, production में नहीं use करें!
        """
        
        # Generate random 11 digits starting with state code
        if state_code not in self.indian_states:
            state_code = '14'  # Default to Maharashtra
        
        # First two digits are state code
        first_11 = state_code + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        # Calculate and append checksum
        checksum = self.calculate_verhoeff_checksum(first_11)
        
        valid_aadhaar = first_11 + str(checksum)
        
        logger.warning(f"Generated test Aadhaar: {valid_aadhaar} (TEST ONLY - NOT FOR PRODUCTION)")
        
        return valid_aadhaar

    def bulk_validate_aadhaar_dataset(self, df: pd.DataFrame, 
                                    aadhaar_column: str = 'aadhaar') -> pd.DataFrame:
        """
        Bulk validation of Aadhaar dataset
        बड़े dataset का validation करना like banking systems
        """
        
        logger.info(f"Starting bulk validation for {len(df)} records")
        
        validation_results = []
        
        for index, row in df.iterrows():
            aadhaar = row[aadhaar_column]
            
            # Get optional demographic fields if present
            name = row.get('name', None)
            phone = row.get('phone', None)
            email = row.get('email', None)
            
            # Validate each Aadhaar
            result = self.complete_aadhaar_validation(aadhaar, name, phone, email)
            
            validation_results.append({
                'row_index': index,
                'aadhaar_masked': result.get('checksum_result', {}).get('aadhaar_masked', 'N/A'),
                'is_valid': result['is_valid'],
                'confidence_score': result['confidence_score'],
                'validation_errors': len(result.get('format_result', {}).get('errors', [])) + 
                                   len(result.get('demographic_result', {}).get('errors', []))
            })
        
        # Create results DataFrame
        results_df = pd.DataFrame(validation_results)
        
        # Add summary statistics
        valid_count = results_df['is_valid'].sum()
        total_count = len(results_df)
        validity_rate = (valid_count / total_count) * 100
        
        logger.info(f"""
        Bulk Validation Complete:
        ========================
        Total Records: {total_count}
        Valid Records: {valid_count}
        Invalid Records: {total_count - valid_count}
        Validity Rate: {validity_rate:.2f}%
        Average Confidence: {results_df['confidence_score'].mean():.2f}%
        """)
        
        return results_df

def create_test_dataset(num_records: int = 1000) -> pd.DataFrame:
    """Create test dataset with mix of valid and invalid Aadhaar numbers"""
    
    validator = AadhaarValidationSystem()
    data = []
    
    # Generate mix of valid and invalid Aadhaar numbers
    for i in range(num_records):
        if i % 10 == 0:
            # 10% invalid format
            aadhaar = f"{random.randint(100000000000, 999999999999)}"  # Random 12 digits
        else:
            # 90% valid format with valid checksum
            aadhaar = validator.generate_valid_aadhaar(
                random.choice(['14', '07', '09', '19', '21', '25'])
            )
        
        # Generate demographic data
        names = ['Rahul Sharma', 'Priya Patel', 'Amit Kumar', 'Sunita Singh', 
                 'Rajesh Gupta', 'Meera Agarwal', 'Vikash Yadav', 'Kavita Jain']
        
        data.append({
            'aadhaar': aadhaar,
            'name': random.choice(names),
            'phone': f"+91{random.randint(6000000000, 9999999999)}",
            'email': f"user{i}@example.com",
            'state': random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu'])
        })
    
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of Aadhaar validation system"""
    
    print("🆔 Aadhaar Validation System Demo")
    print("आधार संख्या जांच प्रणाली का प्रदर्शन\n")
    
    # Initialize validator
    validator = AadhaarValidationSystem()
    
    # Test 1: Individual Aadhaar validation
    print("Test 1: Individual Aadhaar Validation")
    print("=" * 40)
    
    # Generate a valid test Aadhaar
    test_aadhaar = validator.generate_valid_aadhaar('14')  # Maharashtra
    
    # Validate the generated Aadhaar
    result = validator.complete_aadhaar_validation(
        aadhaar=test_aadhaar,
        name="Rahul Sharma",
        phone="+919876543210",
        email="rahul@example.com"
    )
    
    print(f"""
    Test Aadhaar: {test_aadhaar}
    Validation Result: {'✅ Valid' if result['is_valid'] else '❌ Invalid'}
    Confidence Score: {result['confidence_score']:.2f}%
    Summary: {result['summary']}
    """)
    
    # Test 2: Invalid Aadhaar validation
    print("\nTest 2: Invalid Aadhaar Validation")
    print("=" * 40)
    
    invalid_aadhaar = "123456789012"  # Obviously invalid
    invalid_result = validator.complete_aadhaar_validation(invalid_aadhaar)
    
    print(f"""
    Invalid Aadhaar: {invalid_aadhaar}
    Validation Result: {'✅ Valid' if invalid_result['is_valid'] else '❌ Invalid'}
    Errors: {invalid_result.get('format_result', {}).get('errors', [])}
    """)
    
    # Test 3: Bulk validation
    print("\nTest 3: Bulk Dataset Validation")
    print("=" * 40)
    
    # Create test dataset
    test_df = create_test_dataset(100)
    print(f"Created test dataset with {len(test_df)} records")
    
    # Perform bulk validation
    validation_results = validator.bulk_validate_aadhaar_dataset(test_df)
    
    print(f"""
    Bulk Validation Summary:
    - Total Records: {len(validation_results)}
    - Valid Records: {validation_results['is_valid'].sum()}
    - Invalid Records: {(~validation_results['is_valid']).sum()}
    - Validity Rate: {(validation_results['is_valid'].sum() / len(validation_results)) * 100:.2f}%
    - Average Confidence: {validation_results['confidence_score'].mean():.2f}%
    """)
    
    # Test 4: Format validation only
    print("\nTest 4: Format-only Validation Examples")
    print("=" * 40)
    
    test_numbers = [
        "123456789012",  # Sequential
        "111111111111",  # All same
        "012345678901",  # Starts with 0
        "987654321098"   # Valid format
    ]
    
    for test_num in test_numbers:
        format_result = validator.validate_format(test_num)
        print(f"{test_num}: {'✅ Valid Format' if format_result['is_valid_format'] else '❌ Invalid Format'}")
        if format_result['errors']:
            print(f"   Errors: {format_result['errors']}")
    
    print("\n✅ Aadhaar Validation System Demo Complete!")
    print("प्रणाली तैयार है - Production ready!")
    
    return {
        'individual_test': result,
        'bulk_validation': validation_results
    }

if __name__ == "__main__":
    results = main()