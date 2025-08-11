#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 4
GST Invoice Validation System

Complete GST invoice and GSTIN validation system
GST invoice की पूरी जांच करने का system like GST Portal standards

Author: DStudio Team
Context: Tax compliance and e-invoice systems like ClearTax/BillDesk
"""

import re
import json
import random
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import string

# Setup logging with Hindi context
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - GST जांच - %(message)s'
)
logger = logging.getLogger(__name__)

class GSTInvoiceValidationSystem:
    """
    Complete GST invoice validation system
    GST Portal standards के अनुसार validation करेगा
    
    Features:
    1. GSTIN format validation
    2. Invoice number validation
    3. Tax calculation verification
    4. HSN/SAC code validation
    5. Date and amount validations
    6. E-invoice compliance check
    7. GSTR filing format validation
    """
    
    def __init__(self):
        """Initialize GST validation system"""
        
        # Indian state codes for GSTIN validation
        self.state_codes = {
            '01': 'Jammu and Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab',
            '04': 'Chandigarh', '05': 'Uttarakhand', '06': 'Haryana',
            '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
            '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
            '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram',
            '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam',
            '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha',
            '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
            '25': 'Daman and Diu', '26': 'Dadra and Nagar Haveli',
            '27': 'Maharashtra', '28': 'Andhra Pradesh', '29': 'Karnataka',
            '30': 'Goa', '31': 'Lakshadweep', '32': 'Kerala',
            '33': 'Tamil Nadu', '34': 'Puducherry', '35': 'Andaman and Nicobar',
            '36': 'Telangana', '37': 'Andhra Pradesh (New)', '38': 'Ladakh'
        }
        
        # GST rates commonly used in India
        self.standard_gst_rates = [0, 3, 5, 12, 18, 28]  # Standard GST rates
        
        # Common HSN codes for validation
        self.common_hsn_codes = [
            '1001', '1006', '1701', '2201', '2202',  # Food items
            '6109', '6203', '6204', '6205', '6206',  # Textiles
            '8471', '8517', '8518', '8519', '8521',  # Electronics
            '3004', '3005', '3006', '3007',          # Pharmaceuticals
            '8703', '8711', '8712',                  # Vehicles
            '9403', '9401', '9404'                   # Furniture
        ]
        
        # Entity types for GSTIN
        self.entity_types = {
            '1': 'Proprietorship',
            '2': 'Partnership',
            '3': 'Company',
            '4': 'Hindu Undivided Family',
            '5': 'Trust',
            '6': 'Society',
            '7': 'Government',
            '8': 'Others'
        }
        
        logger.info("GST Invoice Validation System initialized - GST सिस्टम तैयार!")

    def validate_gstin_format(self, gstin: str) -> Dict[str, Any]:
        """
        Validate GSTIN format according to GST Portal standards
        GSTIN का format check करना जैसे GST Portal करता है
        Format: 27AAAPL1234C1Z5 (15 characters)
        """
        
        clean_gstin = str(gstin).upper().strip()
        
        validation_result = {
            'original': gstin,
            'cleaned': clean_gstin,
            'is_valid_format': False,
            'state_code': None,
            'state_name': None,
            'pan_number': None,
            'entity_type': None,
            'checksum': None,
            'errors': [],
            'warnings': []
        }
        
        # Basic length check
        if len(clean_gstin) != 15:
            validation_result['errors'].append(f"GSTIN must be exactly 15 characters, got {len(clean_gstin)}")
            return validation_result
        
        # GSTIN regex pattern
        gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z][Z0-9A-Z]$'
        
        if not re.match(gstin_pattern, clean_gstin):
            validation_result['errors'].append("GSTIN format invalid")
            return validation_result
        
        # Extract components
        state_code = clean_gstin[:2]
        pan_part = clean_gstin[2:12]
        entity_code = clean_gstin[12]
        additional_code = clean_gstin[13]
        checksum = clean_gstin[14]
        
        # Validate state code
        if state_code in self.state_codes:
            validation_result['state_code'] = state_code
            validation_result['state_name'] = self.state_codes[state_code]
        else:
            validation_result['errors'].append(f"Invalid state code: {state_code}")
            return validation_result
        
        # Validate PAN pattern within GSTIN
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        if not re.match(pan_pattern, pan_part):
            validation_result['errors'].append("Invalid PAN pattern in GSTIN")
            return validation_result
        
        validation_result['pan_number'] = pan_part
        validation_result['entity_type'] = entity_code
        validation_result['checksum'] = checksum
        validation_result['is_valid_format'] = True
        
        logger.info(f"GSTIN format validated: {clean_gstin[:4]}***{clean_gstin[-3:]}")
        
        return validation_result

    def calculate_gstin_checksum(self, gstin_14_chars: str) -> str:
        """
        Calculate GSTIN checksum using weighted algorithm
        GSTIN का checksum निकालना
        """
        
        # GSTIN checksum calculation as per GST rules
        weights = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
        
        # Character to number mapping
        char_values = {}
        for i, char in enumerate('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            char_values[char] = i
        
        total = 0
        for i, char in enumerate(gstin_14_chars):
            value = char_values[char]
            weighted_value = value * weights[i]
            
            # If weighted value > 35, add digits
            if weighted_value > 35:
                total += (weighted_value // 36) + (weighted_value % 36)
            else:
                total += weighted_value
        
        # Calculate checksum
        checksum_value = (36 - (total % 36)) % 36
        
        # Convert back to character
        checksum_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return checksum_chars[checksum_value]

    def validate_gstin_checksum(self, gstin: str) -> Dict[str, Any]:
        """
        Validate GSTIN checksum
        GSTIN का checksum verify करना
        """
        
        clean_gstin = str(gstin).upper().strip()
        
        if len(clean_gstin) != 15:
            return {
                'is_valid_checksum': False,
                'error': 'Invalid GSTIN length for checksum validation'
            }
        
        # Extract first 14 characters and checksum
        first_14 = clean_gstin[:14]
        provided_checksum = clean_gstin[14]
        
        # Calculate expected checksum
        calculated_checksum = self.calculate_gstin_checksum(first_14)
        
        is_valid = provided_checksum == calculated_checksum
        
        logger.info(f"GSTIN checksum: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return {
            'is_valid_checksum': is_valid,
            'provided_checksum': provided_checksum,
            'calculated_checksum': calculated_checksum,
            'gstin_masked': f"{clean_gstin[:4]}***{clean_gstin[-3:]}"
        }

    def validate_invoice_number(self, invoice_number: str, financial_year: str = None) -> Dict[str, Any]:
        """
        Validate invoice number format
        Invoice number की format check करना
        """
        
        validation_result = {
            'invoice_number': invoice_number,
            'is_valid_format': False,
            'errors': [],
            'warnings': []
        }
        
        if not invoice_number or len(str(invoice_number).strip()) == 0:
            validation_result['errors'].append("Invoice number cannot be empty")
            return validation_result
        
        clean_invoice = str(invoice_number).strip()
        
        # Basic validations
        if len(clean_invoice) > 50:
            validation_result['errors'].append("Invoice number cannot exceed 50 characters")
            return validation_result
        
        if len(clean_invoice) < 3:
            validation_result['errors'].append("Invoice number must be at least 3 characters")
            return validation_result
        
        # Check for valid characters
        valid_pattern = r'^[A-Za-z0-9/\-_.]+$'
        if not re.match(valid_pattern, clean_invoice):
            validation_result['errors'].append("Invoice number contains invalid characters")
            return validation_result
        
        # Check for sequential pattern (warning)
        if clean_invoice.isdigit() and len(clean_invoice) > 3:
            validation_result['warnings'].append("Sequential numeric invoice numbers should have proper series")
        
        validation_result['is_valid_format'] = True
        
        return validation_result

    def validate_hsn_sac_code(self, code: str, code_type: str = 'HSN') -> Dict[str, Any]:
        """
        Validate HSN or SAC code format
        HSN/SAC code की validation करना
        """
        
        validation_result = {
            'code': code,
            'code_type': code_type,
            'is_valid_format': False,
            'errors': []
        }
        
        if not code:
            validation_result['errors'].append(f"{code_type} code cannot be empty")
            return validation_result
        
        clean_code = str(code).strip()
        
        if code_type.upper() == 'HSN':
            # HSN codes are 4, 6, or 8 digits
            if not clean_code.isdigit():
                validation_result['errors'].append("HSN code must contain only digits")
                return validation_result
            
            if len(clean_code) not in [4, 6, 8]:
                validation_result['errors'].append("HSN code must be 4, 6, or 8 digits")
                return validation_result
        
        elif code_type.upper() == 'SAC':
            # SAC codes are 6 digits
            if not clean_code.isdigit():
                validation_result['errors'].append("SAC code must contain only digits")
                return validation_result
            
            if len(clean_code) != 6:
                validation_result['errors'].append("SAC code must be exactly 6 digits")
                return validation_result
        
        validation_result['is_valid_format'] = True
        
        return validation_result

    def validate_tax_calculations(self, taxable_amount: float, cgst_rate: float,
                                sgst_rate: float, igst_rate: float = 0.0,
                                cess_rate: float = 0.0) -> Dict[str, Any]:
        """
        Validate GST tax calculations
        GST tax की calculation verify करना
        """
        
        validation_result = {
            'taxable_amount': taxable_amount,
            'cgst_rate': cgst_rate,
            'sgst_rate': sgst_rate,
            'igst_rate': igst_rate,
            'cess_rate': cess_rate,
            'is_valid_calculation': False,
            'calculated_amounts': {},
            'errors': []
        }
        
        try:
            # Convert to Decimal for precise calculations
            taxable = Decimal(str(taxable_amount))
            
            # Validate rates
            if cgst_rate < 0 or sgst_rate < 0 or igst_rate < 0:
                validation_result['errors'].append("Tax rates cannot be negative")
                return validation_result
            
            # CGST + SGST should equal IGST for inter-state vs intra-state
            if igst_rate > 0 and (cgst_rate > 0 or sgst_rate > 0):
                validation_result['errors'].append("Cannot have both IGST and CGST/SGST")
                return validation_result
            
            if igst_rate == 0 and abs(cgst_rate - sgst_rate) > 0.01:
                validation_result['errors'].append("CGST and SGST rates should be equal")
                return validation_result
            
            # Calculate tax amounts
            cgst_amount = (taxable * Decimal(str(cgst_rate)) / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            sgst_amount = (taxable * Decimal(str(sgst_rate)) / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            igst_amount = (taxable * Decimal(str(igst_rate)) / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            cess_amount = (taxable * Decimal(str(cess_rate)) / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            total_tax = cgst_amount + sgst_amount + igst_amount + cess_amount
            total_amount = taxable + total_tax
            
            validation_result['calculated_amounts'] = {
                'cgst_amount': float(cgst_amount),
                'sgst_amount': float(sgst_amount),
                'igst_amount': float(igst_amount),
                'cess_amount': float(cess_amount),
                'total_tax': float(total_tax),
                'total_amount': float(total_amount)
            }
            
            validation_result['is_valid_calculation'] = True
            
        except Exception as e:
            validation_result['errors'].append(f"Calculation error: {str(e)}")
        
        return validation_result

    def validate_invoice_dates(self, invoice_date: str, supply_date: str = None,
                             due_date: str = None) -> Dict[str, Any]:
        """
        Validate invoice dates
        Invoice के dates की validation करना
        """
        
        validation_result = {
            'invoice_date': invoice_date,
            'supply_date': supply_date,
            'due_date': due_date,
            'is_valid_dates': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Parse invoice date
            if isinstance(invoice_date, str):
                inv_date = datetime.strptime(invoice_date, '%Y-%m-%d')
            else:
                inv_date = invoice_date
            
            # Invoice date shouldn't be in future
            if inv_date > datetime.now():
                validation_result['errors'].append("Invoice date cannot be in future")
                return validation_result
            
            # Invoice date shouldn't be too old (more than 3 years)
            if inv_date < datetime.now() - timedelta(days=3*365):
                validation_result['warnings'].append("Invoice date is more than 3 years old")
            
            # Supply date validation
            if supply_date:
                if isinstance(supply_date, str):
                    sup_date = datetime.strptime(supply_date, '%Y-%m-%d')
                else:
                    sup_date = supply_date
                
                if sup_date > datetime.now():
                    validation_result['errors'].append("Supply date cannot be in future")
                    return validation_result
                
                if sup_date > inv_date + timedelta(days=30):
                    validation_result['warnings'].append("Supply date is significantly after invoice date")
            
            # Due date validation
            if due_date:
                if isinstance(due_date, str):
                    d_date = datetime.strptime(due_date, '%Y-%m-%d')
                else:
                    d_date = due_date
                
                if d_date < inv_date:
                    validation_result['errors'].append("Due date cannot be before invoice date")
                    return validation_result
                
                if d_date > inv_date + timedelta(days=365):
                    validation_result['warnings'].append("Due date is more than a year after invoice")
            
            validation_result['is_valid_dates'] = True
            
        except ValueError as e:
            validation_result['errors'].append(f"Date parsing error: {str(e)}")
        except Exception as e:
            validation_result['errors'].append(f"Date validation error: {str(e)}")
        
        return validation_result

    def validate_complete_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete GST invoice validation
        पूरी GST invoice की comprehensive validation
        """
        
        logger.info(f"Validating complete GST invoice: {invoice_data.get('invoice_number', 'N/A')}")
        
        validation_result = {
            'invoice_number': invoice_data.get('invoice_number'),
            'is_valid_invoice': False,
            'validations': {},
            'summary': {},
            'errors': [],
            'warnings': []
        }
        
        # 1. Supplier GSTIN validation
        supplier_gstin = invoice_data.get('supplier_gstin')
        if supplier_gstin:
            gstin_validation = self.validate_gstin_format(supplier_gstin)
            gstin_checksum = self.validate_gstin_checksum(supplier_gstin)
            validation_result['validations']['supplier_gstin'] = {
                'format': gstin_validation,
                'checksum': gstin_checksum
            }
        else:
            validation_result['errors'].append("Supplier GSTIN is required")
        
        # 2. Customer GSTIN validation (if B2B)
        customer_gstin = invoice_data.get('customer_gstin')
        invoice_type = invoice_data.get('invoice_type', 'B2B')
        
        if invoice_type == 'B2B' and customer_gstin:
            cust_gstin_validation = self.validate_gstin_format(customer_gstin)
            cust_gstin_checksum = self.validate_gstin_checksum(customer_gstin)
            validation_result['validations']['customer_gstin'] = {
                'format': cust_gstin_validation,
                'checksum': cust_gstin_checksum
            }
        
        # 3. Invoice number validation
        invoice_number = invoice_data.get('invoice_number')
        if invoice_number:
            inv_num_validation = self.validate_invoice_number(invoice_number)
            validation_result['validations']['invoice_number'] = inv_num_validation
        else:
            validation_result['errors'].append("Invoice number is required")
        
        # 4. Date validations
        invoice_date = invoice_data.get('invoice_date')
        supply_date = invoice_data.get('supply_date')
        due_date = invoice_data.get('due_date')
        
        date_validation = self.validate_invoice_dates(invoice_date, supply_date, due_date)
        validation_result['validations']['dates'] = date_validation
        
        # 5. Line items validation
        line_items = invoice_data.get('line_items', [])
        total_validation_errors = 0
        total_calculated_amount = 0
        
        for i, item in enumerate(line_items):
            # HSN/SAC validation
            hsn_code = item.get('hsn_code')
            if hsn_code:
                hsn_validation = self.validate_hsn_sac_code(hsn_code, 'HSN')
                validation_result['validations'][f'item_{i}_hsn'] = hsn_validation
                if not hsn_validation['is_valid_format']:
                    total_validation_errors += 1
            
            # Tax calculation validation
            taxable_amount = item.get('taxable_amount', 0)
            cgst_rate = item.get('cgst_rate', 0)
            sgst_rate = item.get('sgst_rate', 0)
            igst_rate = item.get('igst_rate', 0)
            cess_rate = item.get('cess_rate', 0)
            
            tax_validation = self.validate_tax_calculations(
                taxable_amount, cgst_rate, sgst_rate, igst_rate, cess_rate
            )
            validation_result['validations'][f'item_{i}_tax'] = tax_validation
            
            if tax_validation['is_valid_calculation']:
                total_calculated_amount += tax_validation['calculated_amounts']['total_amount']
            else:
                total_validation_errors += 1
        
        # 6. Total amount verification
        declared_total = invoice_data.get('total_amount', 0)
        amount_difference = abs(total_calculated_amount - declared_total)
        
        if amount_difference > 0.01:  # Allow 1 paisa difference for rounding
            validation_result['warnings'].append(
                f"Total amount mismatch: Declared {declared_total}, Calculated {total_calculated_amount}"
            )
        
        # Final validation status
        validation_result['is_valid_invoice'] = (
            len(validation_result['errors']) == 0 and
            total_validation_errors == 0
        )
        
        validation_result['summary'] = {
            'total_line_items': len(line_items),
            'validation_errors': total_validation_errors,
            'total_errors': len(validation_result['errors']),
            'total_warnings': len(validation_result['warnings']),
            'calculated_amount': total_calculated_amount,
            'declared_amount': declared_total,
            'amount_difference': amount_difference
        }
        
        logger.info(f"Invoice validation complete: {'✅ Valid' if validation_result['is_valid_invoice'] else '❌ Invalid'}")
        
        return validation_result

    def generate_test_gstin(self, state_code: str = '27') -> str:
        """Generate test GSTIN for validation testing"""
        
        if state_code not in self.state_codes:
            state_code = '27'  # Default to Maharashtra
        
        # Generate PAN part
        pan_letters = ''.join(random.choices(string.ascii_uppercase, k=5))
        pan_numbers = ''.join(random.choices(string.digits, k=4))
        pan_check = random.choice(string.ascii_uppercase)
        
        pan_part = pan_letters + pan_numbers + pan_check
        
        # Entity code
        entity_code = random.choice('123456')
        
        # Additional code
        additional_code = '1'
        
        # Calculate checksum
        first_14 = state_code + pan_part + entity_code + additional_code
        checksum = self.calculate_gstin_checksum(first_14)
        
        test_gstin = first_14 + checksum
        
        logger.warning(f"Generated test GSTIN: {test_gstin} (TEST ONLY)")
        
        return test_gstin

def create_sample_invoice() -> Dict[str, Any]:
    """Create sample GST invoice for testing"""
    
    validator = GSTInvoiceValidationSystem()
    
    # Generate test GSTINs
    supplier_gstin = validator.generate_test_gstin('27')  # Maharashtra
    customer_gstin = validator.generate_test_gstin('07')  # Delhi
    
    sample_invoice = {
        'invoice_number': 'INV-2024-001',
        'invoice_date': '2024-01-15',
        'supply_date': '2024-01-15',
        'due_date': '2024-02-14',
        'invoice_type': 'B2B',
        'supplier_gstin': supplier_gstin,
        'customer_gstin': customer_gstin,
        'line_items': [
            {
                'item_description': 'Laptop Computer',
                'hsn_code': '8471',
                'quantity': 2,
                'unit_price': 50000.00,
                'taxable_amount': 100000.00,
                'cgst_rate': 9.0,
                'sgst_rate': 9.0,
                'igst_rate': 0.0,
                'cess_rate': 0.0
            },
            {
                'item_description': 'Computer Mouse',
                'hsn_code': '8471',
                'quantity': 2,
                'unit_price': 1000.00,
                'taxable_amount': 2000.00,
                'cgst_rate': 9.0,
                'sgst_rate': 9.0,
                'igst_rate': 0.0,
                'cess_rate': 0.0
            }
        ],
        'total_amount': 120360.00  # 102000 + 18360 tax
    }
    
    return sample_invoice

def main():
    """Main execution function - demo of GST validation system"""
    
    print("📄 GST Invoice Validation System Demo")
    print("GST invoice जांच प्रणाली का प्रदर्शन\n")
    
    # Initialize validator
    validator = GSTInvoiceValidationSystem()
    
    # Test 1: GSTIN Format Validation
    print("Test 1: GSTIN Format Validation")
    print("=" * 40)
    
    test_gstin = validator.generate_test_gstin('27')
    gstin_format = validator.validate_gstin_format(test_gstin)
    gstin_checksum = validator.validate_gstin_checksum(test_gstin)
    
    print(f"""
    Test GSTIN: {test_gstin}
    State: {gstin_format['state_name']}
    Format Valid: {'✅' if gstin_format['is_valid_format'] else '❌'}
    Checksum Valid: {'✅' if gstin_checksum['is_valid_checksum'] else '❌'}
    PAN Part: {gstin_format['pan_number']}
    """)
    
    # Test 2: Invalid GSTIN Examples
    print("\nTest 2: Invalid GSTIN Examples")
    print("=" * 40)
    
    invalid_gstins = [
        "27AAAPL1234C1Z",    # Too short
        "99AAAPL1234C1Z5",   # Invalid state code
        "27AAAPL12341Z5",    # Invalid entity code
        "27AAAPL1234C1Z9"    # Wrong checksum
    ]
    
    for invalid_gstin in invalid_gstins:
        result = validator.validate_gstin_format(invalid_gstin)
        print(f"{invalid_gstin}: {'✅' if result['is_valid_format'] else '❌'} - {result.get('errors', ['Valid'])}")
    
    # Test 3: Tax Calculation Validation
    print("\nTest 3: Tax Calculation Validation")
    print("=" * 40)
    
    tax_result = validator.validate_tax_calculations(
        taxable_amount=100000.00,
        cgst_rate=9.0,
        sgst_rate=9.0,
        igst_rate=0.0,
        cess_rate=0.0
    )
    
    print(f"""
    Taxable Amount: ₹{tax_result['taxable_amount']:,.2f}
    CGST (9%): ₹{tax_result['calculated_amounts']['cgst_amount']:,.2f}
    SGST (9%): ₹{tax_result['calculated_amounts']['sgst_amount']:,.2f}
    Total Tax: ₹{tax_result['calculated_amounts']['total_tax']:,.2f}
    Total Amount: ₹{tax_result['calculated_amounts']['total_amount']:,.2f}
    Calculation Valid: {'✅' if tax_result['is_valid_calculation'] else '❌'}
    """)
    
    # Test 4: Complete Invoice Validation
    print("\nTest 4: Complete Invoice Validation")
    print("=" * 40)
    
    sample_invoice = create_sample_invoice()
    invoice_validation = validator.validate_complete_invoice(sample_invoice)
    
    print(f"""
    Invoice Number: {sample_invoice['invoice_number']}
    Invoice Valid: {'✅' if invoice_validation['is_valid_invoice'] else '❌'}
    Total Line Items: {invoice_validation['summary']['total_line_items']}
    Validation Errors: {invoice_validation['summary']['validation_errors']}
    Total Errors: {invoice_validation['summary']['total_errors']}
    Total Warnings: {invoice_validation['summary']['total_warnings']}
    
    Declared Amount: ₹{invoice_validation['summary']['declared_amount']:,.2f}
    Calculated Amount: ₹{invoice_validation['summary']['calculated_amount']:,.2f}
    Difference: ₹{invoice_validation['summary']['amount_difference']:,.2f}
    """)
    
    # Test 5: HSN Code Validation
    print("\nTest 5: HSN/SAC Code Validation")
    print("=" * 40)
    
    hsn_codes = ['8471', '123456', '1234', 'ABCD', '84711234']
    
    for hsn in hsn_codes:
        hsn_result = validator.validate_hsn_sac_code(hsn, 'HSN')
        print(f"HSN {hsn}: {'✅ Valid' if hsn_result['is_valid_format'] else '❌ Invalid'}")
        if hsn_result['errors']:
            print(f"   Errors: {hsn_result['errors']}")
    
    # Test 6: Date Validation
    print("\nTest 6: Invoice Date Validation")
    print("=" * 40)
    
    date_validation = validator.validate_invoice_dates(
        invoice_date='2024-01-15',
        supply_date='2024-01-15',
        due_date='2024-02-15'
    )
    
    print(f"""
    Invoice Date: {date_validation['invoice_date']}
    Supply Date: {date_validation['supply_date']}
    Due Date: {date_validation['due_date']}
    Dates Valid: {'✅' if date_validation['is_valid_dates'] else '❌'}
    Warnings: {len(date_validation['warnings'])}
    """)
    
    print("\n✅ GST Invoice Validation System Demo Complete!")
    print("प्रणाली तैयार है - Ready for GST compliance!")
    
    return {
        'gstin_validation': {'format': gstin_format, 'checksum': gstin_checksum},
        'tax_calculation': tax_result,
        'invoice_validation': invoice_validation
    }

if __name__ == "__main__":
    results = main()