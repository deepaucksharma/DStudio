#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 3
PAN Card Validation System with Checksum Algorithm

Complete PAN card validation system for Indian tax identification
PAN कार्ड की पूरी जांच करने का system like Income Tax Department

Author: DStudio Team
Context: Tax compliance and financial KYC like Zerodha/Groww
"""

import re
import random
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import string

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PAN जांच - %(message)s'
)
logger = logging.getLogger(__name__)

class PANCardValidationSystem:
    """
    Complete PAN card validation system
    Income Tax Department standards के अनुसार validation
    
    PAN Format: ABCDE1234F
    - First 5: Alphabets
    - Next 4: Numbers
    - Last 1: Alphabet (checksum)
    
    Features:
    1. Format validation
    2. Checksum verification
    3. Category identification
    4. Blacklist checking
    5. Bulk validation
    """
    
    def __init__(self):
        """Initialize PAN validation system with lookup tables"""
        
        # PAN category codes (4th character)
        self.pan_categories = {
            'P': 'Individual',
            'F': 'Firm/LLP',
            'C': 'Company',
            'H': 'HUF (Hindu Undivided Family)',
            'A': 'Association of Persons',
            'T': 'Trust',
            'B': 'Body of Individuals',
            'G': 'Government',
            'J': 'Artificial Juridical Person',
            'L': 'Local Authority',
            'K': 'Krish (Special Category)'
        }
        
        # Common invalid/test PAN numbers to reject
        self.blacklisted_pans = {
            'ABCDE1234F',  # Common test PAN
            'AAAAA0000A',  # Invalid pattern
            'ZZZZZ9999Z',  # Invalid pattern
            'PANPA1234A',  # Obvious fake
            'TESTX1234T'   # Test pattern
        }
        
        # First letter patterns for different entity types
        self.first_letter_patterns = {
            'Individual': ['A', 'B', 'C', 'F', 'G', 'H', 'L', 'J', 'P'],
            'Company': ['A', 'B', 'C', 'F', 'G', 'H', 'L', 'J'],
            'Trust': ['A', 'B', 'C', 'F', 'G', 'H', 'L', 'J', 'T']
        }
        
        logger.info("PAN Card Validation System initialized - PAN सिस्टम तैयार!")

    def validate_format(self, pan: str) -> Dict[str, any]:
        """
        Validate PAN card format according to IT Department standards
        PAN का format check करना जैसे IT Department करता है
        """
        
        # Clean and uppercase PAN
        clean_pan = str(pan).upper().strip()
        
        validation_result = {
            'original': pan,
            'cleaned': clean_pan,
            'is_valid_format': False,
            'pan_category': None,
            'entity_type': None,
            'errors': [],
            'warnings': []
        }
        
        # Basic length check
        if len(clean_pan) != 10:
            validation_result['errors'].append(f"PAN must be exactly 10 characters, got {len(clean_pan)}")
            return validation_result
        
        # PAN regex pattern: ABCDE1234F
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        if not re.match(pan_pattern, clean_pan):
            validation_result['errors'].append("PAN format invalid. Expected: 5 letters + 4 digits + 1 letter")
            return validation_result
        
        # Check blacklisted PANs
        if clean_pan in self.blacklisted_pans:
            validation_result['errors'].append("PAN appears to be a test/invalid number")
            return validation_result
        
        # Extract and validate category (4th character)
        category_char = clean_pan[3]
        if category_char in self.pan_categories:
            validation_result['pan_category'] = category_char
            validation_result['entity_type'] = self.pan_categories[category_char]
        else:
            validation_result['warnings'].append(f"Unusual category character: {category_char}")
        
        # Check for obvious patterns
        if len(set(clean_pan[:5])) == 1:  # All same letters
            validation_result['errors'].append("First 5 letters cannot be identical")
            return validation_result
        
        if clean_pan[4:8] == '0000':  # All zeros in number part
            validation_result['errors'].append("Number part cannot be all zeros")
            return validation_result
        
        validation_result['is_valid_format'] = True
        logger.info(f"Format validation passed for PAN: {clean_pan[:3]}***{clean_pan[-1]}")
        
        return validation_result

    def calculate_pan_checksum(self, pan_9_chars: str) -> str:
        """
        Calculate PAN checksum using weighted algorithm
        PAN का checksum निकालना (simplified algorithm for demo)
        Note: Actual PAN checksum algorithm is proprietary to IT Department
        """
        
        # This is a simplified demonstration algorithm
        # Real PAN checksum is more complex and proprietary
        
        weights = [2, 3, 4, 5, 6, 7, 8, 9, 2]  # Example weights
        total = 0
        
        for i, char in enumerate(pan_9_chars):
            if char.isalpha():
                # Convert letter to number (A=1, B=2, etc.)
                value = ord(char) - ord('A') + 1
            else:
                # Numeric character
                value = int(char)
            
            total += value * weights[i]
        
        # Calculate checksum digit
        checksum_value = total % 26
        checksum_char = chr(ord('A') + checksum_value)
        
        return checksum_char

    def validate_checksum(self, pan: str) -> Dict[str, any]:
        """
        Validate PAN checksum (demonstration only)
        PAN का checksum check करना (demo purpose)
        ⚠️ Real checksum algorithm is proprietary to IT Department
        """
        
        clean_pan = str(pan).upper().strip()
        
        if len(clean_pan) != 10:
            return {
                'is_valid_checksum': False,
                'error': 'Invalid PAN length for checksum validation'
            }
        
        # Extract first 9 characters and last character
        first_9 = clean_pan[:9]
        provided_checksum = clean_pan[9]
        
        # Calculate expected checksum (demo algorithm)
        calculated_checksum = self.calculate_pan_checksum(first_9)
        
        # Note: This is for demonstration only
        # Real PAN validation requires IT Department's proprietary algorithm
        is_valid = provided_checksum == calculated_checksum
        
        logger.info(f"Checksum validation: {'✅ Valid' if is_valid else '❌ Invalid'} (DEMO ONLY)")
        
        return {
            'is_valid_checksum': is_valid,
            'provided_checksum': provided_checksum,
            'calculated_checksum': calculated_checksum,
            'pan_masked': f"{clean_pan[:3]}***{clean_pan[-1]}",
            'note': 'This is demonstration only - real checksum validation requires IT Dept algorithm'
        }

    def extract_pan_details(self, pan: str) -> Dict[str, any]:
        """
        Extract detailed information from PAN structure
        PAN से सभी जानकारी निकालना
        """
        
        clean_pan = str(pan).upper().strip()
        
        if len(clean_pan) != 10:
            return {'error': 'Invalid PAN length'}
        
        details = {
            'pan': clean_pan,
            'first_3_chars': clean_pan[:3],  # Sequence from AAA to ZZZ
            'category_char': clean_pan[3],   # Entity type
            'last_name_char': clean_pan[4],  # First character of last name/entity
            'number_sequence': clean_pan[4:8],  # Running sequence
            'check_digit': clean_pan[9],     # Checksum character
            'category_description': self.pan_categories.get(clean_pan[3], 'Unknown'),
            'is_individual': clean_pan[3] == 'P',
            'is_company': clean_pan[3] == 'C',
            'is_trust': clean_pan[3] == 'T'
        }
        
        return details

    def validate_pan_with_name(self, pan: str, name: str) -> Dict[str, any]:
        """
        Validate PAN against holder's name
        PAN को नाम के साथ match करना
        """
        
        clean_pan = str(pan).upper().strip()
        clean_name = str(name).upper().strip()
        
        validation_result = {
            'pan': clean_pan,
            'name': clean_name,
            'name_match_score': 0.0,
            'is_name_compatible': False,
            'suggestions': []
        }
        
        if len(clean_pan) != 10 or not clean_name:
            validation_result['error'] = 'Invalid PAN or name'
            return validation_result
        
        # For individuals (P category), check last name initial
        if clean_pan[3] == 'P':
            # 5th character should match first letter of surname
            pan_surname_initial = clean_pan[4]
            
            # Extract potential surname (last word of name)
            name_parts = clean_name.split()
            if len(name_parts) > 1:
                surname = name_parts[-1]
                surname_initial = surname[0]
                
                if pan_surname_initial == surname_initial:
                    validation_result['name_match_score'] = 0.8
                    validation_result['is_name_compatible'] = True
                else:
                    validation_result['suggestions'].append(
                        f"PAN surname initial '{pan_surname_initial}' doesn't match name surname '{surname_initial}'"
                    )
            else:
                validation_result['suggestions'].append(
                    "Single name provided, cannot verify surname initial match"
                )
        
        # For companies, check if name contains company identifiers
        elif clean_pan[3] == 'C':
            company_identifiers = ['LTD', 'LIMITED', 'PVT', 'PRIVATE', 'COMPANY', 'CORP']
            has_company_identifier = any(identifier in clean_name for identifier in company_identifiers)
            
            if has_company_identifier:
                validation_result['name_match_score'] = 0.7
                validation_result['is_name_compatible'] = True
            else:
                validation_result['suggestions'].append(
                    "Company PAN but name doesn't contain company identifiers"
                )
        
        return validation_result

    def complete_pan_validation(self, pan: str, name: str = None, 
                              check_format_only: bool = False) -> Dict[str, any]:
        """
        Complete PAN validation with all checks
        पूरी PAN जांच - सभी validation एक साथ
        """
        
        logger.info(f"Starting complete PAN validation: {str(pan)[:3]}***")
        
        # Step 1: Format validation
        format_result = self.validate_format(pan)
        
        if not format_result['is_valid_format']:
            return {
                'is_valid': False,
                'validation_type': 'format_failed',
                'format_result': format_result,
                'summary': 'PAN format validation failed'
            }
        
        # Step 2: Extract PAN details
        pan_details = self.extract_pan_details(pan)
        
        # Step 3: Checksum validation (if not format-only)
        checksum_result = None
        if not check_format_only:
            checksum_result = self.validate_checksum(pan)
        
        # Step 4: Name matching (if name provided)
        name_match_result = None
        if name:
            name_match_result = self.validate_pan_with_name(pan, name)
        
        # Calculate overall validity
        is_valid = format_result['is_valid_format']
        
        if checksum_result:
            is_valid = is_valid and checksum_result['is_valid_checksum']
        
        if name_match_result:
            is_valid = is_valid and name_match_result['is_name_compatible']
        
        confidence_score = self._calculate_pan_confidence(format_result, checksum_result, name_match_result)
        
        logger.info(f"Complete PAN validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return {
            'is_valid': is_valid,
            'validation_type': 'complete',
            'format_result': format_result,
            'pan_details': pan_details,
            'checksum_result': checksum_result,
            'name_match_result': name_match_result,
            'confidence_score': confidence_score,
            'summary': f"Complete PAN validation - {pan_details.get('category_description', 'Unknown')} type"
        }

    def _calculate_pan_confidence(self, format_result: Dict, checksum_result: Optional[Dict],
                                name_match_result: Optional[Dict]) -> float:
        """Calculate confidence score for PAN validation"""
        
        score = 0.0
        
        # Format validation (50%)
        if format_result['is_valid_format']:
            score += 50.0
        
        # Checksum validation (30%)
        if checksum_result and checksum_result['is_valid_checksum']:
            score += 30.0
        elif not checksum_result:
            score += 30.0  # Give credit if not checked
        
        # Name matching (20%)
        if name_match_result:
            score += name_match_result['name_match_score'] * 20.0
        else:
            score += 20.0  # Give credit if not checked
        
        return min(score, 100.0)

    def bulk_validate_pan_dataset(self, df: pd.DataFrame, 
                                pan_column: str = 'pan',
                                name_column: str = 'name') -> pd.DataFrame:
        """
        Bulk validation of PAN dataset
        बड़े dataset का PAN validation like mutual fund KYC
        """
        
        logger.info(f"Starting bulk PAN validation for {len(df)} records")
        
        validation_results = []
        
        for index, row in df.iterrows():
            pan = row[pan_column]
            name = row.get(name_column, None)
            
            # Validate each PAN
            result = self.complete_pan_validation(pan, name)
            
            validation_results.append({
                'row_index': index,
                'pan_masked': result.get('pan_details', {}).get('pan', str(pan))[:3] + '***' + str(pan)[-1:],
                'is_valid': result['is_valid'],
                'entity_type': result.get('pan_details', {}).get('category_description', 'Unknown'),
                'confidence_score': result['confidence_score'],
                'has_format_errors': len(result.get('format_result', {}).get('errors', [])) > 0,
                'has_name_match': result.get('name_match_result') is not None
            })
        
        # Create results DataFrame
        results_df = pd.DataFrame(validation_results)
        
        # Summary statistics
        valid_count = results_df['is_valid'].sum()
        total_count = len(results_df)
        validity_rate = (valid_count / total_count) * 100
        
        # Entity type distribution
        entity_distribution = results_df['entity_type'].value_counts()
        
        logger.info(f"""
        Bulk PAN Validation Complete:
        =============================
        Total Records: {total_count}
        Valid PANs: {valid_count}
        Invalid PANs: {total_count - valid_count}
        Validity Rate: {validity_rate:.2f}%
        Average Confidence: {results_df['confidence_score'].mean():.2f}%
        
        Entity Type Distribution:
        {entity_distribution.to_string()}
        """)
        
        return results_df

    def generate_test_pan(self, category: str = 'P') -> str:
        """
        Generate test PAN for validation testing (TEST ONLY)
        Testing के लिए PAN generate करना
        ⚠️ केवल testing के लिए!
        """
        
        if category not in self.pan_categories:
            category = 'P'
        
        # Generate first 3 characters (random)
        first_3 = ''.join(random.choices(string.ascii_uppercase, k=3))
        
        # 4th character is category
        category_char = category
        
        # 5th character (random for demo)
        fifth_char = random.choice(string.ascii_uppercase)
        
        # 4 digits
        numbers = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        # Calculate checksum
        first_9 = first_3 + category_char + fifth_char + numbers
        checksum = self.calculate_pan_checksum(first_9)
        
        test_pan = first_9 + checksum
        
        logger.warning(f"Generated test PAN: {test_pan} (TEST ONLY - NOT FOR PRODUCTION)")
        
        return test_pan

def create_test_pan_dataset(num_records: int = 500) -> pd.DataFrame:
    """Create test dataset with mix of valid and invalid PANs"""
    
    validator = PANCardValidationSystem()
    data = []
    
    # Common Indian names
    names = [
        'RAHUL SHARMA', 'PRIYA PATEL', 'AMIT KUMAR', 'SUNITA SINGH',
        'RAJESH GUPTA', 'MEERA AGARWAL', 'VIKASH YADAV', 'KAVITA JAIN',
        'SURESH COMPANY LIMITED', 'ABC PRIVATE LIMITED', 'XYZ TRUST'
    ]
    
    for i in range(num_records):
        if i % 20 == 0:
            # 5% completely invalid format
            pan = f"INVALID{i:04d}"
        elif i % 10 == 0:
            # 10% valid format but wrong checksum
            test_pan = validator.generate_test_pan(random.choice(['P', 'C', 'F', 'H']))
            # Corrupt the checksum
            pan = test_pan[:-1] + random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        else:
            # 85% valid PANs
            pan = validator.generate_test_pan(random.choice(['P', 'C', 'F', 'H', 'T']))
        
        data.append({
            'pan': pan,
            'name': random.choice(names),
            'entity_type': random.choice(['Individual', 'Company', 'Trust', 'HUF']),
            'application_date': f"2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        })
    
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of PAN validation system"""
    
    print("🏛️ PAN Card Validation System Demo")
    print("PAN कार्ड जांच प्रणाली का प्रदर्शन\n")
    
    # Initialize validator
    validator = PANCardValidationSystem()
    
    # Test 1: Individual PAN validation
    print("Test 1: Individual PAN Validation")
    print("=" * 40)
    
    # Generate test PAN
    test_pan = validator.generate_test_pan('P')  # Individual
    
    result = validator.complete_pan_validation(
        pan=test_pan,
        name="Rahul Sharma"
    )
    
    print(f"""
    Test PAN: {test_pan}
    Category: {result['pan_details']['category_description']}
    Format Valid: {'✅' if result['format_result']['is_valid_format'] else '❌'}
    Checksum Valid: {'✅' if result.get('checksum_result', {}).get('is_valid_checksum') else '❌'}
    Name Compatible: {'✅' if result.get('name_match_result', {}).get('is_name_compatible') else '❌'}
    Overall Valid: {'✅' if result['is_valid'] else '❌'}
    Confidence: {result['confidence_score']:.2f}%
    """)
    
    # Test 2: Company PAN validation
    print("\nTest 2: Company PAN Validation")
    print("=" * 40)
    
    company_pan = validator.generate_test_pan('C')  # Company
    
    company_result = validator.complete_pan_validation(
        pan=company_pan,
        name="ABC PRIVATE LIMITED"
    )
    
    print(f"""
    Company PAN: {company_pan}
    Category: {company_result['pan_details']['category_description']}
    Format Valid: {'✅' if company_result['format_result']['is_valid_format'] else '❌'}
    Overall Valid: {'✅' if company_result['is_valid'] else '❌'}
    """)
    
    # Test 3: Invalid PAN examples
    print("\nTest 3: Invalid PAN Examples")
    print("=" * 40)
    
    invalid_pans = [
        "ABCDE1234",      # Too short
        "ABCDE12345F",    # Too long
        "12345ABCDF",     # Wrong format
        "ABCDE1234F",     # Blacklisted
        "AAAAA0000A"      # Invalid pattern
    ]
    
    for invalid_pan in invalid_pans:
        format_check = validator.validate_format(invalid_pan)
        print(f"{invalid_pan}: {'✅' if format_check['is_valid_format'] else '❌'} - {format_check.get('errors', ['Valid'])}")
    
    # Test 4: Bulk validation
    print("\nTest 4: Bulk Dataset Validation")
    print("=" * 40)
    
    # Create test dataset
    test_df = create_test_pan_dataset(100)
    print(f"Created test dataset with {len(test_df)} records")
    
    # Perform bulk validation
    validation_results = validator.bulk_validate_pan_dataset(test_df)
    
    print(f"""
    Bulk Validation Summary:
    - Total Records: {len(validation_results)}
    - Valid PANs: {validation_results['is_valid'].sum()}
    - Invalid PANs: {(~validation_results['is_valid']).sum()}
    - Validity Rate: {(validation_results['is_valid'].sum() / len(validation_results)) * 100:.2f}%
    - Average Confidence: {validation_results['confidence_score'].mean():.2f}%
    
    Entity Type Distribution:
    {validation_results['entity_type'].value_counts().to_string()}
    """)
    
    # Test 5: PAN details extraction
    print("\nTest 5: PAN Details Extraction")
    print("=" * 40)
    
    sample_pan = validator.generate_test_pan('H')  # HUF
    details = validator.extract_pan_details(sample_pan)
    
    print(f"""
    Sample PAN: {sample_pan}
    Details Extracted:
    - Category: {details['category_description']}
    - Is Individual: {details['is_individual']}
    - Is Company: {details['is_company']}
    - First 3 chars: {details['first_3_chars']}
    - Category char: {details['category_char']}
    - Check digit: {details['check_digit']}
    """)
    
    print("\n✅ PAN Card Validation System Demo Complete!")
    print("प्रणाली तैयार है - Ready for tax compliance systems!")
    print("\n⚠️ Note: Checksum validation is demonstration only.")
    print("Real PAN checksum algorithm is proprietary to IT Department.")
    
    return {
        'individual_test': result,
        'company_test': company_result,
        'bulk_validation': validation_results
    }

if __name__ == "__main__":
    results = main()