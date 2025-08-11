#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 5
Indian Email/Phone Validation with Regional Patterns

Complete contact validation system for Indian context
Indian email/phone patterns की comprehensive validation like OTP systems

Author: DStudio Team
Context: Contact validation for Indian users like WhatsApp/PhonePe
"""

import re
import json
import random
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import string
from phonenumbers import geocoder, carrier, timezone
import phonenumbers
from email_validator import validate_email, EmailNotValidError

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - संपर्क जांच - %(message)s'
)
logger = logging.getLogger(__name__)

class IndianContactValidationSystem:
    """
    Complete Indian contact validation system
    Indian phone numbers और emails की validation करने का system
    
    Features:
    1. Indian mobile number validation
    2. Landline number validation
    3. Telecom operator identification
    4. Email format validation
    5. Domain validation
    6. Regional pattern recognition
    7. Bulk contact validation
    8. Contact quality scoring
    """
    
    def __init__(self):
        """Initialize Indian contact validation system"""
        
        # Indian mobile number prefixes by operator
        self.mobile_prefixes = {
            # Jio
            'JIO': ['701', '702', '703', '704', '705', '706', '707', '708', '709'],
            # Airtel
            'AIRTEL': ['700', '900', '901', '902', '903', '904', '905', '906', '907', '908', '909', '910', '911', '912', '913', '914', '915', '916', '917', '918', '919'],
            # Vi (Vodafone Idea)
            'VI': ['600', '601', '602', '603', '604', '605', '606', '607', '608', '609', '740', '741', '742', '743', '744', '745', '746', '747', '748', '749'],
            # BSNL
            'BSNL': ['620', '621', '622', '623', '624', '625', '626', '627', '628', '629', '640', '641', '642', '643', '644', '645', '646', '647', '648', '649'],
            # Tata Docomo
            'TATA': ['720', '721', '722', '723', '724', '725', '726', '727', '728', '729']
        }
        
        # State-wise STD codes for landlines
        self.std_codes = {
            # Major cities
            '011': 'Delhi', '022': 'Mumbai', '033': 'Kolkata', '040': 'Hyderabad',
            '044': 'Chennai', '080': 'Bangalore', '079': 'Ahmedabad', '020': 'Pune',
            
            # State codes
            '0141': 'Jaipur', '0135': 'Dehradun', '0172': 'Chandigarh',
            '0484': 'Kochi', '0481': 'Thrissur', '0471': 'Thiruvananthapuram',
            '0821': 'Mysore', '0824': 'Mangalore', '0836': 'Hubli',
            
            # Smaller cities
            '0261': 'Surat', '0265': 'Vadodara', '0278': 'Bhuj',
            '0361': 'Guwahati', '0364': 'Aizawl', '0370': 'Gangtok'
        }
        
        # Common Indian email domains
        self.common_indian_domains = {
            # Popular international
            'gmail.com': 'Google Gmail',
            'yahoo.com': 'Yahoo Mail', 
            'yahoo.co.in': 'Yahoo India',
            'hotmail.com': 'Microsoft Hotmail',
            'outlook.com': 'Microsoft Outlook',
            
            # Indian specific
            'rediffmail.com': 'Rediffmail',
            'sify.com': 'Sify',
            'in.com': 'India.com',
            'indiatimes.com': 'Times Internet',
            'vsnl.com': 'VSNL',
            
            # Corporate domains
            'tcs.com': 'Tata Consultancy Services',
            'infosys.com': 'Infosys',
            'wipro.com': 'Wipro',
            'hcl.com': 'HCL Technologies',
            'cognizant.com': 'Cognizant'
        }
        
        # Suspicious email patterns
        self.suspicious_patterns = [
            r'.*test.*@.*',           # Test emails
            r'.*temp.*@.*',           # Temporary emails
            r'.*fake.*@.*',           # Fake emails
            r'.*dummy.*@.*',          # Dummy emails
            r'.*[0-9]{10,}@.*',      # Long numeric usernames
            r'.*admin.*@.*',          # Admin emails
        ]
        
        logger.info("Indian Contact Validation System initialized - संपर्क सिस्टम तैयार!")

    def validate_indian_mobile(self, mobile: str) -> Dict[str, Any]:
        """
        Validate Indian mobile number with operator detection
        Indian mobile number की complete validation करना
        """
        
        # Clean the mobile number
        clean_mobile = re.sub(r'[\s\-\+\(\)]', '', str(mobile))
        
        validation_result = {
            'original': mobile,
            'cleaned': clean_mobile,
            'is_valid': False,
            'country_code': None,
            'mobile_number': None,
            'operator': None,
            'circle': None,
            'number_type': 'mobile',
            'errors': [],
            'warnings': []
        }
        
        # Handle different input formats
        if clean_mobile.startswith('91'):
            clean_mobile = clean_mobile[2:]  # Remove country code
            validation_result['country_code'] = '+91'
        elif clean_mobile.startswith('+91'):
            clean_mobile = clean_mobile[3:]
            validation_result['country_code'] = '+91'
        elif clean_mobile.startswith('0'):
            clean_mobile = clean_mobile[1:]  # Remove leading zero
        
        # Check length
        if len(clean_mobile) != 10:
            validation_result['errors'].append(f"Indian mobile must be 10 digits, got {len(clean_mobile)}")
            return validation_result
        
        # Check if all digits
        if not clean_mobile.isdigit():
            validation_result['errors'].append("Mobile number must contain only digits")
            return validation_result
        
        # Check if starts with valid mobile prefix (6, 7, 8, 9)
        if not clean_mobile[0] in ['6', '7', '8', '9']:
            validation_result['errors'].append("Indian mobile must start with 6, 7, 8, or 9")
            return validation_result
        
        # Detect operator based on prefix
        prefix = clean_mobile[:3]
        detected_operator = None
        
        for operator, prefixes in self.mobile_prefixes.items():
            if prefix in prefixes:
                detected_operator = operator
                break
        
        if not detected_operator:
            # Check broader patterns
            first_digit = clean_mobile[0]
            if first_digit == '9':
                detected_operator = 'AIRTEL/VI'  # Most 9xx numbers
            elif first_digit == '8':
                detected_operator = 'AIRTEL/VI/JIO'
            elif first_digit == '7':
                detected_operator = 'JIO/AIRTEL'
            elif first_digit == '6':
                detected_operator = 'VI/BSNL'
        
        # Use phonenumbers library for additional validation
        try:
            phone_number = phonenumbers.parse(f"+91{clean_mobile}", "IN")
            if phonenumbers.is_valid_number(phone_number):
                validation_result['operator'] = detected_operator or carrier.name_for_number(phone_number, "en")
                validation_result['circle'] = geocoder.description_for_number(phone_number, "en")
                validation_result['is_valid'] = True
            else:
                validation_result['errors'].append("Invalid mobile number according to telecom standards")
        except Exception as e:
            validation_result['warnings'].append(f"Advanced validation failed: {str(e)}")
            # Basic validation passed, so still mark as valid
            validation_result['is_valid'] = True
            validation_result['operator'] = detected_operator
        
        validation_result['mobile_number'] = clean_mobile
        validation_result['country_code'] = '+91'
        
        logger.info(f"Mobile validated: {clean_mobile[:3]}****{clean_mobile[-2:]} - {detected_operator}")
        
        return validation_result

    def validate_indian_landline(self, landline: str) -> Dict[str, Any]:
        """
        Validate Indian landline number
        Landline number की validation करना
        """
        
        clean_landline = re.sub(r'[\s\-\+\(\)]', '', str(landline))
        
        validation_result = {
            'original': landline,
            'cleaned': clean_landline,
            'is_valid': False,
            'std_code': None,
            'local_number': None,
            'city': None,
            'number_type': 'landline',
            'errors': []
        }
        
        # Remove country code if present
        if clean_landline.startswith('91'):
            clean_landline = clean_landline[2:]
        elif clean_landline.startswith('+91'):
            clean_landline = clean_landline[3:]
        
        # Remove leading zero
        if clean_landline.startswith('0'):
            clean_landline = clean_landline[1:]
        
        # Check length (STD code + local number)
        if len(clean_landline) < 8 or len(clean_landline) > 11:
            validation_result['errors'].append("Landline number length invalid")
            return validation_result
        
        # Extract STD code and validate
        std_code_found = False
        for std_code, city in self.std_codes.items():
            std_without_zero = std_code[1:] if std_code.startswith('0') else std_code
            if clean_landline.startswith(std_without_zero):
                validation_result['std_code'] = std_code
                validation_result['city'] = city
                validation_result['local_number'] = clean_landline[len(std_without_zero):]
                std_code_found = True
                break
        
        if not std_code_found:
            validation_result['errors'].append("Invalid STD code")
            return validation_result
        
        # Validate local number length
        local_number_length = len(validation_result['local_number'])
        if local_number_length < 6 or local_number_length > 8:
            validation_result['errors'].append("Local number length invalid")
            return validation_result
        
        validation_result['is_valid'] = True
        
        return validation_result

    def validate_email_format(self, email: str) -> Dict[str, Any]:
        """
        Validate email format with Indian context
        Email की comprehensive validation करना
        """
        
        validation_result = {
            'original': email,
            'email': email.lower().strip() if email else '',
            'is_valid': False,
            'domain': None,
            'domain_type': None,
            'is_suspicious': False,
            'quality_score': 0,
            'errors': [],
            'warnings': []
        }
        
        if not email or len(email.strip()) == 0:
            validation_result['errors'].append("Email cannot be empty")
            return validation_result
        
        clean_email = email.lower().strip()
        validation_result['email'] = clean_email
        
        # Basic format validation using regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, clean_email):
            validation_result['errors'].append("Invalid email format")
            return validation_result
        
        # Advanced validation using email-validator library
        try:
            valid = validate_email(clean_email)
            clean_email = valid.email
            validation_result['email'] = clean_email
            validation_result['is_valid'] = True
        except EmailNotValidError as e:
            validation_result['errors'].append(f"Email validation failed: {str(e)}")
            return validation_result
        
        # Extract domain
        domain = clean_email.split('@')[1]
        validation_result['domain'] = domain
        
        # Check domain type
        if domain in self.common_indian_domains:
            validation_result['domain_type'] = f"Common - {self.common_indian_domains[domain]}"
            validation_result['quality_score'] += 20
        elif domain.endswith('.in'):
            validation_result['domain_type'] = "Indian domain"
            validation_result['quality_score'] += 15
        elif domain.endswith('.com'):
            validation_result['domain_type'] = "International (.com)"
            validation_result['quality_score'] += 10
        else:
            validation_result['domain_type'] = "Other domain"
            validation_result['quality_score'] += 5
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.match(pattern, clean_email):
                validation_result['is_suspicious'] = True
                validation_result['warnings'].append("Email matches suspicious pattern")
                validation_result['quality_score'] -= 30
                break
        
        # Username quality check
        username = clean_email.split('@')[0]
        if len(username) > 20:
            validation_result['warnings'].append("Username is very long")
        elif len(username) < 3:
            validation_result['warnings'].append("Username is very short")
        else:
            validation_result['quality_score'] += 10
        
        # Check for meaningful username
        if username.isdigit():
            validation_result['warnings'].append("Username is all numeric")
            validation_result['quality_score'] -= 10
        elif re.match(r'^[a-zA-Z]+[0-9]+$', username):
            validation_result['quality_score'] += 15  # Name + numbers pattern
        
        validation_result['quality_score'] = max(0, min(100, validation_result['quality_score']))
        
        return validation_result

    def validate_contact_pair(self, email: str, mobile: str) -> Dict[str, Any]:
        """
        Validate email-mobile pair for consistency
        Email और mobile का combination validate करना
        """
        
        validation_result = {
            'email_validation': self.validate_email_format(email),
            'mobile_validation': self.validate_indian_mobile(mobile),
            'pair_consistency': {},
            'overall_valid': False,
            'confidence_score': 0
        }
        
        # Check pair consistency
        email_valid = validation_result['email_validation']['is_valid']
        mobile_valid = validation_result['mobile_validation']['is_valid']
        
        validation_result['overall_valid'] = email_valid and mobile_valid
        
        # Calculate confidence score
        confidence = 0
        if email_valid:
            confidence += 40
            confidence += validation_result['email_validation']['quality_score'] * 0.3
        
        if mobile_valid:
            confidence += 40
        
        # Bonus for Indian domain + Indian mobile
        if (email_valid and mobile_valid and 
            validation_result['email_validation']['domain'].endswith('.in')):
            confidence += 20
        
        validation_result['confidence_score'] = min(100, confidence)
        
        # Additional consistency checks
        if email_valid and mobile_valid:
            email_username = validation_result['email_validation']['email'].split('@')[0]
            mobile_number = validation_result['mobile_validation']['mobile_number']
            
            # Check if mobile number appears in email username
            if mobile_number in email_username:
                validation_result['pair_consistency']['mobile_in_email'] = True
                validation_result['confidence_score'] += 10
            else:
                validation_result['pair_consistency']['mobile_in_email'] = False
        
        return validation_result

    def bulk_validate_contacts(self, df: pd.DataFrame, 
                              email_column: str = 'email',
                              mobile_column: str = 'mobile') -> pd.DataFrame:
        """
        Bulk validation of contact data
        बड़े contact dataset का validation करना
        """
        
        logger.info(f"Starting bulk contact validation for {len(df)} records")
        
        validation_results = []
        
        for index, row in df.iterrows():
            email = row.get(email_column, '')
            mobile = row.get(mobile_column, '')
            
            # Validate contact pair
            result = self.validate_contact_pair(email, mobile)
            
            validation_results.append({
                'row_index': index,
                'email_masked': self._mask_email(email),
                'mobile_masked': self._mask_mobile(mobile),
                'email_valid': result['email_validation']['is_valid'],
                'mobile_valid': result['mobile_validation']['is_valid'],
                'overall_valid': result['overall_valid'],
                'confidence_score': result['confidence_score'],
                'email_quality': result['email_validation'].get('quality_score', 0),
                'mobile_operator': result['mobile_validation'].get('operator', 'Unknown'),
                'email_domain_type': result['email_validation'].get('domain_type', 'Unknown'),
                'is_suspicious': result['email_validation'].get('is_suspicious', False)
            })
        
        # Create results DataFrame
        results_df = pd.DataFrame(validation_results)
        
        # Summary statistics
        total_count = len(results_df)
        valid_pairs = results_df['overall_valid'].sum()
        valid_emails = results_df['email_valid'].sum()
        valid_mobiles = results_df['mobile_valid'].sum()
        
        avg_confidence = results_df['confidence_score'].mean()
        avg_email_quality = results_df['email_quality'].mean()
        
        # Operator distribution
        operator_dist = results_df['mobile_operator'].value_counts()
        
        # Domain type distribution  
        domain_dist = results_df['email_domain_type'].value_counts()
        
        logger.info(f"""
        Bulk Contact Validation Complete:
        =================================
        Total Records: {total_count}
        Valid Email-Mobile Pairs: {valid_pairs} ({(valid_pairs/total_count)*100:.2f}%)
        Valid Emails Only: {valid_emails} ({(valid_emails/total_count)*100:.2f}%)
        Valid Mobiles Only: {valid_mobiles} ({(valid_mobiles/total_count)*100:.2f}%)
        
        Average Confidence Score: {avg_confidence:.2f}%
        Average Email Quality: {avg_email_quality:.2f}%
        
        Top Mobile Operators:
        {operator_dist.head(5).to_string()}
        
        Top Email Domain Types:
        {domain_dist.head(5).to_string()}
        """)
        
        return results_df

    def _mask_email(self, email: str) -> str:
        """Mask email for privacy"""
        if not email or '@' not in email:
            return email
        
        username, domain = email.split('@')
        if len(username) <= 3:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            masked_username = username[:2] + '*' * (len(username) - 3) + username[-1]
        
        return f"{masked_username}@{domain}"
    
    def _mask_mobile(self, mobile: str) -> str:
        """Mask mobile for privacy"""
        clean_mobile = re.sub(r'[\s\-\+\(\)]', '', str(mobile))
        if len(clean_mobile) >= 10:
            return clean_mobile[:3] + '****' + clean_mobile[-3:]
        return mobile

    def generate_contact_quality_report(self, validation_results: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive contact quality report
        Contact quality की detailed report बनाना
        """
        
        total_records = len(validation_results)
        
        quality_report = {
            'total_records': total_records,
            'validity_metrics': {
                'valid_pairs': validation_results['overall_valid'].sum(),
                'valid_emails': validation_results['email_valid'].sum(),
                'valid_mobiles': validation_results['mobile_valid'].sum(),
                'pair_validity_rate': (validation_results['overall_valid'].sum() / total_records) * 100,
                'email_validity_rate': (validation_results['email_valid'].sum() / total_records) * 100,
                'mobile_validity_rate': (validation_results['mobile_valid'].sum() / total_records) * 100
            },
            'quality_metrics': {
                'avg_confidence_score': validation_results['confidence_score'].mean(),
                'avg_email_quality': validation_results['email_quality'].mean(),
                'high_confidence_contacts': (validation_results['confidence_score'] > 80).sum(),
                'suspicious_emails': validation_results['is_suspicious'].sum()
            },
            'operator_distribution': validation_results['mobile_operator'].value_counts().to_dict(),
            'domain_type_distribution': validation_results['email_domain_type'].value_counts().to_dict(),
            'recommendations': []
        }
        
        # Generate recommendations
        if quality_report['validity_metrics']['pair_validity_rate'] < 80:
            quality_report['recommendations'].append(
                "Contact quality is below optimal. Consider implementing stricter validation at data entry."
            )
        
        if quality_report['quality_metrics']['suspicious_emails'] > total_records * 0.05:
            quality_report['recommendations'].append(
                "High number of suspicious emails detected. Review data sources and implement email verification."
            )
        
        if quality_report['quality_metrics']['avg_confidence_score'] < 70:
            quality_report['recommendations'].append(
                "Low average confidence score. Consider implementing OTP verification for contacts."
            )
        
        return quality_report

def create_test_contact_dataset(num_records: int = 1000) -> pd.DataFrame:
    """Create test dataset with mix of valid and invalid contacts"""
    
    validator = IndianContactValidationSystem()
    data = []
    
    # Sample data
    names = ['rahul', 'priya', 'amit', 'sunita', 'rajesh', 'meera', 'vikash', 'kavita']
    domains = ['gmail.com', 'yahoo.com', 'rediffmail.com', 'hotmail.com', 'company.co.in']
    
    for i in range(num_records):
        # Generate email
        if i % 20 == 0:
            # 5% invalid emails
            email = f"invalid.email{i}"
        elif i % 15 == 0:
            # Some suspicious emails
            email = f"test{i}123456789@{random.choice(domains)}"
        else:
            # Normal emails
            name = random.choice(names)
            email = f"{name}{random.randint(1, 999)}@{random.choice(domains)}"
        
        # Generate mobile
        if i % 25 == 0:
            # 4% invalid mobiles
            mobile = f"123456{i:04d}"
        else:
            # Valid mobiles
            first_digit = random.choice(['6', '7', '8', '9'])
            mobile = first_digit + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        data.append({
            'name': random.choice(['Rahul Sharma', 'Priya Patel', 'Amit Kumar', 'Sunita Singh']),
            'email': email,
            'mobile': mobile,
            'source': random.choice(['Website', 'App', 'Manual', 'Import'])
        })
    
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of contact validation system"""
    
    print("📞 Indian Contact Validation System Demo")
    print("संपर्क validation प्रणाली का प्रदर्शन\n")
    
    # Initialize validator
    validator = IndianContactValidationSystem()
    
    # Test 1: Mobile Number Validation
    print("Test 1: Indian Mobile Number Validation")
    print("=" * 40)
    
    test_mobiles = [
        "9876543210",      # Valid
        "+91 9876543210",  # With country code
        "8765432109",      # Valid Jio/Airtel
        "7654321098",      # Valid Jio
        "5432109876",      # Invalid (starts with 5)
        "98765432",        # Too short
        "98765432101"      # Too long
    ]
    
    for mobile in test_mobiles:
        result = validator.validate_indian_mobile(mobile)
        status = "✅ Valid" if result['is_valid'] else "❌ Invalid"
        operator = result.get('operator', 'Unknown')
        print(f"{mobile}: {status} - {operator}")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
    
    # Test 2: Email Validation
    print("\nTest 2: Email Format Validation")
    print("=" * 40)
    
    test_emails = [
        "user@gmail.com",           # Valid Gmail
        "rahul123@rediffmail.com",  # Valid Rediff
        "test@company.co.in",       # Valid Indian domain
        "invalid.email",            # Invalid format
        "user@",                    # Incomplete
        "very.long.username.with.lots.of.dots@domain.com",  # Long username
        "test123456789@gmail.com"   # Suspicious pattern
    ]
    
    for email in test_emails:
        result = validator.validate_email_format(email)
        status = "✅ Valid" if result['is_valid'] else "❌ Invalid"
        quality = result.get('quality_score', 0)
        suspicious = "⚠️ Suspicious" if result.get('is_suspicious') else ""
        print(f"{email}: {status} (Quality: {quality}%) {suspicious}")
        if result['errors']:
            print(f"   Errors: {result['errors']}")
        if result['warnings']:
            print(f"   Warnings: {result['warnings']}")
    
    # Test 3: Landline Validation
    print("\nTest 3: Landline Number Validation")
    print("=" * 40)
    
    test_landlines = [
        "02212345678",    # Mumbai
        "01123456789",    # Delhi
        "08012345678",    # Bangalore
        "04412345678",    # Chennai
        "123456789"       # Invalid
    ]
    
    for landline in test_landlines:
        result = validator.validate_indian_landline(landline)
        status = "✅ Valid" if result['is_valid'] else "❌ Invalid"
        city = result.get('city', 'Unknown')
        print(f"{landline}: {status} - {city}")
    
    # Test 4: Contact Pair Validation
    print("\nTest 4: Email-Mobile Pair Validation")
    print("=" * 40)
    
    contact_pairs = [
        ("rahul@gmail.com", "9876543210"),
        ("priya123@rediffmail.com", "8765432109"),
        ("invalid.email", "1234567890"),
        ("user9876543210@gmail.com", "9876543210")  # Mobile in email
    ]
    
    for email, mobile in contact_pairs:
        result = validator.validate_contact_pair(email, mobile)
        status = "✅ Valid Pair" if result['overall_valid'] else "❌ Invalid Pair"
        confidence = result['confidence_score']
        print(f"{email} + {mobile}: {status} (Confidence: {confidence:.1f}%)")
    
    # Test 5: Bulk Validation
    print("\nTest 5: Bulk Contact Dataset Validation")
    print("=" * 40)
    
    # Create test dataset
    test_df = create_test_contact_dataset(200)
    print(f"Created test dataset with {len(test_df)} records")
    
    # Perform bulk validation
    validation_results = validator.bulk_validate_contacts(test_df)
    
    # Generate quality report
    quality_report = validator.generate_contact_quality_report(validation_results)
    
    print(f"""
    Bulk Validation Summary:
    - Total Records: {quality_report['total_records']}
    - Valid Pairs: {quality_report['validity_metrics']['valid_pairs']} ({quality_report['validity_metrics']['pair_validity_rate']:.2f}%)
    - Valid Emails: {quality_report['validity_metrics']['valid_emails']} ({quality_report['validity_metrics']['email_validity_rate']:.2f}%)
    - Valid Mobiles: {quality_report['validity_metrics']['valid_mobiles']} ({quality_report['validity_metrics']['mobile_validity_rate']:.2f}%)
    
    Quality Metrics:
    - Average Confidence: {quality_report['quality_metrics']['avg_confidence_score']:.2f}%
    - Average Email Quality: {quality_report['quality_metrics']['avg_email_quality']:.2f}%
    - High Confidence Contacts: {quality_report['quality_metrics']['high_confidence_contacts']}
    - Suspicious Emails: {quality_report['quality_metrics']['suspicious_emails']}
    """)
    
    # Display recommendations
    if quality_report['recommendations']:
        print("\nRecommendations:")
        for i, rec in enumerate(quality_report['recommendations'], 1):
            print(f"{i}. {rec}")
    
    print("\n✅ Indian Contact Validation System Demo Complete!")
    print("प्रणाली तैयार है - Ready for contact verification systems!")
    
    return {
        'validation_results': validation_results,
        'quality_report': quality_report
    }

if __name__ == "__main__":
    results = main()