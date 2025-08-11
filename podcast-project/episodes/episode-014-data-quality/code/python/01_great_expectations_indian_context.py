#!/usr/bin/env python3
"""
Data Quality & Validation - Episode 14, Example 1
Great Expectations Framework with Indian Business Context

Mumbai-style data validation framework for e-commerce and fintech
हर data point ka सत्यापन करना है like Dabbawalas check each tiffin box

Author: DStudio Team
Context: Indian e-commerce data validation like Flipkart/Amazon
"""

import great_expectations as ge
from great_expectations.dataset import PandasDataset
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Any

# Setup logging with Hindi touch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - डेटा जांच करते हैं - %(message)s'
)
logger = logging.getLogger(__name__)

class IndianDataQualityFramework:
    """
    Indian context data quality framework using Great Expectations
    यह system हर data row को validate करेगा like Railway TTE checks tickets
    """
    
    def __init__(self):
        """Initialize framework with Indian business rules"""
        self.ge_context = ge.get_context()
        self.indian_state_codes = [
            'AP', 'AR', 'AS', 'BR', 'CT', 'GA', 'GJ', 'HR', 'HP', 'JH',
            'KA', 'KL', 'MP', 'MH', 'MN', 'ML', 'MZ', 'NL', 'OR', 'PB',
            'RJ', 'SK', 'TN', 'TG', 'TR', 'UP', 'UT', 'WB', 'AN', 'CH',
            'DH', 'DD', 'LD', 'JK', 'LA', 'PY'
        ]
        
        logger.info("Indian Data Quality Framework initialized - तैयार है!")

    def validate_ecommerce_orders(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate e-commerce order data like Flipkart/Amazon
        हर order का पूरा details check करना है
        """
        
        # Convert DataFrame to Great Expectations Dataset
        ge_df = PandasDataset(df)
        
        # Basic existence checks - ये columns होने चाहिए
        expectations = []
        
        # Order ID should exist and be unique - हर order unique होना चाहिए
        expectation = ge_df.expect_column_to_exist('order_id')
        expectations.append(expectation)
        
        expectation = ge_df.expect_column_values_to_be_unique('order_id')
        expectations.append(expectation)
        
        # Customer details validation - customer information check
        expectation = ge_df.expect_column_to_exist('customer_email')
        expectations.append(expectation)
        
        # Email format check - proper email होना चाहिए
        expectation = ge_df.expect_column_values_to_match_regex(
            'customer_email',
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        expectations.append(expectation)
        
        # Phone number validation - Indian mobile format
        expectation = ge_df.expect_column_values_to_match_regex(
            'customer_phone',
            r'^(\+91|91|0)?[6-9]\d{9}$'
        )
        expectations.append(expectation)
        
        # Order amount validation - reasonable amount होना चाहिए
        expectation = ge_df.expect_column_values_to_be_between(
            'order_amount',
            min_value=1,
            max_value=1000000  # 10 lakh max reasonable order
        )
        expectations.append(expectation)
        
        # State code validation - valid Indian states
        expectation = ge_df.expect_column_values_to_be_in_set(
            'delivery_state',
            self.indian_state_codes
        )
        expectations.append(expectation)
        
        # Pincode validation - Indian pincode format
        expectation = ge_df.expect_column_values_to_match_regex(
            'delivery_pincode',
            r'^\d{6}$'
        )
        expectations.append(expectation)
        
        # Order date validation - not future date
        expectation = ge_df.expect_column_values_to_be_between(
            'order_date',
            min_value=datetime.now() - timedelta(days=365*5),  # 5 years back max
            max_value=datetime.now()
        )
        expectations.append(expectation)
        
        # Product category should not be null
        expectation = ge_df.expect_column_values_to_not_be_null('product_category')
        expectations.append(expectation)
        
        # Payment method validation - common Indian methods
        valid_payment_methods = ['COD', 'UPI', 'Card', 'Net Banking', 'Wallet']
        expectation = ge_df.expect_column_values_to_be_in_set(
            'payment_method',
            valid_payment_methods
        )
        expectations.append(expectation)
        
        # Calculate success rate
        successful_expectations = sum(1 for exp in expectations if exp['success'])
        success_rate = (successful_expectations / len(expectations)) * 100
        
        logger.info(f"Validation completed - {successful_expectations}/{len(expectations)} checks passed")
        logger.info(f"Success Rate: {success_rate:.2f}% - {'बहुत अच्छा!' if success_rate > 90 else 'सुधार की जरूरत है'}")
        
        return {
            'total_expectations': len(expectations),
            'successful_expectations': successful_expectations,
            'success_rate': success_rate,
            'failed_expectations': [exp for exp in expectations if not exp['success']],
            'validation_summary': f"Data quality {'excellent' if success_rate > 95 else 'needs improvement'}"
        }

    def validate_fintech_transactions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate UPI/payment transaction data like PhonePe/GPay
        हर transaction का security और validity check
        """
        
        ge_df = PandasDataset(df)
        expectations = []
        
        # Transaction ID uniqueness - हर transaction unique
        expectation = ge_df.expect_column_values_to_be_unique('transaction_id')
        expectations.append(expectation)
        
        # Amount validation - reasonable limits
        expectation = ge_df.expect_column_values_to_be_between(
            'amount',
            min_value=1,
            max_value=200000  # 2 lakh UPI limit
        )
        expectations.append(expectation)
        
        # UPI ID validation - proper format
        expectation = ge_df.expect_column_values_to_match_regex(
            'sender_upi',
            r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z][a-zA-Z0-9.\-_]{2,64}$'
        )
        expectations.append(expectation)
        
        # Transaction status validation
        valid_statuses = ['SUCCESS', 'FAILED', 'PENDING', 'TIMEOUT']
        expectation = ge_df.expect_column_values_to_be_in_set(
            'status',
            valid_statuses
        )
        expectations.append(expectation)
        
        # Bank code validation - Indian bank codes
        expectation = ge_df.expect_column_values_to_match_regex(
            'bank_code',
            r'^[A-Z]{4}0[A-Z0-9]{6}$'  # IFSC format
        )
        expectations.append(expectation)
        
        # Time validation - realistic transaction time
        expectation = ge_df.expect_column_values_to_be_between(
            'transaction_time',
            min_value=datetime.now() - timedelta(days=90),
            max_value=datetime.now()
        )
        expectations.append(expectation)
        
        successful_expectations = sum(1 for exp in expectations if exp['success'])
        success_rate = (successful_expectations / len(expectations)) * 100
        
        return {
            'total_expectations': len(expectations),
            'successful_expectations': successful_expectations,
            'success_rate': success_rate,
            'validation_summary': f"Transaction data quality: {success_rate:.1f}%"
        }

    def create_data_docs(self, validation_results: Dict[str, Any], output_path: str = "./data_docs"):
        """
        Create comprehensive data documentation like professional report
        पूरा data analysis report बनाना है
        """
        
        # Create expectation suite
        suite_name = "indian_ecommerce_suite"
        suite = self.ge_context.create_expectation_suite(
            expectation_suite_name=suite_name,
            overwrite_existing=True
        )
        
        # Build data docs
        self.ge_context.build_data_docs()
        
        logger.info(f"Data documentation created at {output_path}")
        logger.info("Quality report ready - रिपोर्ट तैयार है!")
        
        return f"Documentation generated successfully at {output_path}"

def generate_sample_ecommerce_data(num_records: int = 1000) -> pd.DataFrame:
    """Generate sample Indian e-commerce data for testing"""
    
    # Indian cities and states mapping
    city_state_mapping = {
        'Mumbai': 'MH', 'Delhi': 'DL', 'Bangalore': 'KA', 'Chennai': 'TN',
        'Kolkata': 'WB', 'Hyderabad': 'TG', 'Pune': 'MH', 'Ahmedabad': 'GJ',
        'Jaipur': 'RJ', 'Lucknow': 'UP', 'Kanpur': 'UP', 'Nagpur': 'MH'
    }
    
    cities = list(city_state_mapping.keys())
    
    # Generate realistic data
    np.random.seed(42)
    
    data = {
        'order_id': [f'ORD-{str(i).zfill(8)}' for i in range(1, num_records + 1)],
        'customer_email': [f'customer{i}@gmail.com' for i in range(1, num_records + 1)],
        'customer_phone': [f'+91{np.random.randint(6000000000, 9999999999)}' for _ in range(num_records)],
        'order_amount': np.random.lognormal(mean=6, sigma=1.5, size=num_records).astype(int),
        'delivery_city': np.random.choice(cities, num_records),
        'delivery_pincode': [f'{np.random.randint(100000, 999999):06d}' for _ in range(num_records)],
        'order_date': pd.date_range(
            start=datetime.now() - timedelta(days=365),
            end=datetime.now(),
            periods=num_records
        ),
        'product_category': np.random.choice([
            'Electronics', 'Fashion', 'Home', 'Books', 'Sports', 'Beauty'
        ], num_records),
        'payment_method': np.random.choice(['COD', 'UPI', 'Card', 'Net Banking'], num_records, p=[0.4, 0.3, 0.2, 0.1])
    }
    
    # Add corresponding state codes
    data['delivery_state'] = [city_state_mapping.get(city, 'MH') for city in data['delivery_city']]
    
    # Introduce some data quality issues for testing (real-world scenario)
    # कुछ गलत data भी डालते हैं realistic testing के लिए
    error_indices = np.random.choice(num_records, size=num_records//20, replace=False)
    
    for idx in error_indices[:5]:
        data['customer_email'][idx] = 'invalid_email'  # Invalid email
    
    for idx in error_indices[5:10]:
        data['customer_phone'][idx] = '123456789'  # Invalid phone
    
    for idx in error_indices[10:15]:
        data['delivery_pincode'][idx] = '12345'  # Invalid pincode
        
    return pd.DataFrame(data)

def main():
    """Main execution function - demo of the framework"""
    
    print("🚀 Indian Data Quality Framework Demo Starting...")
    print("डेटा की जांच शुरू करते हैं!\n")
    
    # Initialize framework
    quality_framework = IndianDataQualityFramework()
    
    # Generate sample data
    print("📊 Generating sample e-commerce data...")
    sample_data = generate_sample_ecommerce_data(1000)
    print(f"Generated {len(sample_data)} records\n")
    
    # Validate e-commerce data
    print("🔍 Validating e-commerce data...")
    ecommerce_results = quality_framework.validate_ecommerce_orders(sample_data)
    
    print(f"""
    📋 E-commerce Validation Results:
    ================================
    Total Checks: {ecommerce_results['total_expectations']}
    Passed Checks: {ecommerce_results['successful_expectations']}
    Success Rate: {ecommerce_results['success_rate']:.2f}%
    Status: {ecommerce_results['validation_summary']}
    """)
    
    # Print failed expectations for debugging
    if ecommerce_results['failed_expectations']:
        print("❌ Failed Validations:")
        for failed_exp in ecommerce_results['failed_expectations']:
            print(f"   - {failed_exp.get('expectation_type', 'Unknown')}")
    
    # Generate fintech sample data
    print("\n💳 Generating sample fintech transaction data...")
    fintech_data = pd.DataFrame({
        'transaction_id': [f'TXN{i:010d}' for i in range(1, 501)],
        'amount': np.random.exponential(scale=1000, size=500).astype(int),
        'sender_upi': [f'user{i}@paytm' for i in range(1, 501)],
        'receiver_upi': [f'merchant{i}@phonepe' for i in range(1, 501)],
        'status': np.random.choice(['SUCCESS', 'FAILED', 'PENDING'], 500, p=[0.85, 0.1, 0.05]),
        'bank_code': [f'SBIN0{i:06d}' for i in range(1, 501)],
        'transaction_time': pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            periods=500
        )
    })
    
    # Validate fintech data
    print("🔍 Validating fintech transaction data...")
    fintech_results = quality_framework.validate_fintech_transactions(fintech_data)
    
    print(f"""
    💳 Fintech Validation Results:
    ==============================
    Total Checks: {fintech_results['total_expectations']}
    Passed Checks: {fintech_results['successful_expectations']}
    Success Rate: {fintech_results['success_rate']:.2f}%
    Status: {fintech_results['validation_summary']}
    """)
    
    print("\n✅ Data Quality Framework Demo Complete!")
    print("Framework ready for production use - उत्पादन के लिए तैयार!")
    
    return {
        'ecommerce_results': ecommerce_results,
        'fintech_results': fintech_results
    }

if __name__ == "__main__":
    results = main()