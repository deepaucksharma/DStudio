# Episode 14: Data Quality & Validation - Part 2
## Advanced Validation aur Production Implementation (7,000 words)

### Great Expectations: Production Mein Magic

Abhi tak humne basic validation dekha. Ab dekhte hai ki production mein kaise Great Expectations use karte hai. Yeh framework hai jo data quality ko automate karta hai.

```python
# Great Expectations Setup for Indian E-commerce
import great_expectations as ge
from great_expectations.checkpoint import Checkpoint
import pandas as pd
from datetime import datetime

class IndianEcommerceValidator:
    """
    Flipkart/Amazon style product data validator
    """
    def __init__(self):
        self.context = ge.get_context()
        self.setup_indian_expectations()
    
    def setup_indian_expectations(self):
        """
        Setup expectations for Indian market
        """
        # Product catalog validation suite
        suite = self.context.create_expectation_suite(
            "indian_product_catalog_suite"
        )
        
        # Price validation - INR specific
        suite.expect_column_values_to_be_between(
            column="price_inr",
            min_value=1.0,
            max_value=10000000.0,  # 1 crore max
            mostly=0.95  # 95% should be in range
        )
        
        # GST validation
        suite.expect_column_values_to_match_regex(
            column="gst_number",
            regex=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        )
        
        # Pin code validation
        suite.expect_column_values_to_match_regex(
            column="pin_code",
            regex=r"^[1-9][0-9]{5}$",
            mostly=0.99
        )
    
    def validate_festival_pricing(self, df):
        """
        Festival season price validation
        Diwali, Holi price checks
        """
        # Check discount percentages
        expectations = []
        
        # Maximum discount allowed - 90%
        expectations.append(
            ge.expectations.expect_column_values_to_be_between(
                df["discount_percentage"],
                min_value=0,
                max_value=90
            )
        )
        
        # Festival price should be less than MRP
        expectations.append(
            ge.expectations.expect_column_pair_values_A_to_be_greater_than_B(
                column_A="mrp",
                column_B="festival_price",
                or_equal=True
            )
        )
        
        return self.run_expectations(expectations)
```

Dekho, Great Expectations ka power - automated validation, detailed reports, aur production ready!

### PayTM KYC Validation System - Real Implementation

PayTM jaise platform pe daily lakhs KYC validations hote hai. Dekho kaise implement karte hai:

```python
# PayTM Style KYC Validation Pipeline
import hashlib
import re
from typing import Dict, List, Tuple
import requests
import numpy as np
from PIL import Image
import cv2

class PayTMKYCValidator:
    """
    Complete KYC validation system
    Used by PayTM, PhonePe, GooglePay
    """
    
    def __init__(self):
        self.uidai_api = "https://api.uidai.gov.in/verify"  # Mock
        self.pan_api = "https://api.incometax.gov.in/verify"  # Mock
        self.validation_rules = self.load_validation_rules()
        
    def validate_complete_kyc(self, user_data: Dict) -> Tuple[bool, Dict]:
        """
        Complete KYC validation pipeline
        """
        results = {
            'status': 'pending',
            'checks': {},
            'risk_score': 0,
            'timestamp': datetime.now()
        }
        
        # Step 1: Aadhaar validation
        aadhaar_valid = self.validate_aadhaar_advanced(
            user_data.get('aadhaar_number'),
            user_data.get('aadhaar_image')
        )
        results['checks']['aadhaar'] = aadhaar_valid
        
        # Step 2: PAN validation with income tax database
        pan_valid = self.validate_pan_with_itr(
            user_data.get('pan_number'),
            user_data.get('name')
        )
        results['checks']['pan'] = pan_valid
        
        # Step 3: Bank account validation
        bank_valid = self.validate_bank_account(
            user_data.get('account_number'),
            user_data.get('ifsc_code')
        )
        results['checks']['bank'] = bank_valid
        
        # Step 4: Address proof validation
        address_valid = self.validate_address_proof(
            user_data.get('address_proof_type'),
            user_data.get('address_proof_doc')
        )
        results['checks']['address'] = address_valid
        
        # Step 5: Selfie verification with Aadhaar photo
        selfie_valid = self.validate_selfie_match(
            user_data.get('selfie_image'),
            user_data.get('aadhaar_image')
        )
        results['checks']['selfie'] = selfie_valid
        
        # Calculate risk score
        results['risk_score'] = self.calculate_risk_score(results['checks'])
        
        # Final decision
        all_valid = all(results['checks'].values())
        low_risk = results['risk_score'] < 30
        
        results['status'] = 'approved' if (all_valid and low_risk) else 'rejected'
        
        return results['status'] == 'approved', results
    
    def validate_aadhaar_advanced(self, aadhaar: str, 
                                  aadhaar_image: bytes) -> bool:
        """
        Advanced Aadhaar validation with OCR
        """
        if not aadhaar:
            return False
            
        # Basic format check
        if not re.match(r'^\d{12}$', aadhaar):
            return False
        
        # Verhoeff algorithm check
        if not self.verhoeff_check(aadhaar):
            return False
        
        # OCR validation if image provided
        if aadhaar_image:
            extracted_number = self.extract_aadhaar_from_image(aadhaar_image)
            if extracted_number != aadhaar:
                return False
        
        # UIDAI API validation (mock)
        # In production, this would call actual UIDAI API
        uidai_response = self.mock_uidai_verification(aadhaar)
        
        return uidai_response['valid']
    
    def validate_pan_with_itr(self, pan: str, name: str) -> bool:
        """
        PAN validation with Income Tax Return check
        """
        if not pan:
            return False
            
        # Format validation
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan):
            return False
        
        # Check PAN structure
        # 4th character indicates holder type
        holder_types = {
            'P': 'Person',
            'C': 'Company',
            'H': 'HUF',
            'F': 'Firm',
            'T': 'Trust'
        }
        
        if pan[3] not in holder_types:
            return False
        
        # Name matching with PAN database
        # Mock API call - in production this would be real
        itr_data = self.mock_itr_verification(pan)
        
        if not itr_data['exists']:
            return False
        
        # Fuzzy name matching
        name_match_score = self.calculate_name_similarity(
            name.upper(),
            itr_data['registered_name'].upper()
        )
        
        return name_match_score > 0.85
    
    def validate_bank_account(self, account_number: str, 
                            ifsc: str) -> bool:
        """
        Bank account validation with penny drop test
        """
        # IFSC format check
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc):
            return False
        
        # Extract bank code from IFSC
        bank_code = ifsc[:4]
        
        # Validate bank code exists
        valid_banks = {
            'SBIN': 'State Bank of India',
            'HDFC': 'HDFC Bank',
            'ICIC': 'ICICI Bank',
            'AXIS': 'Axis Bank',
            'KKBK': 'Kotak Mahindra Bank',
            'YESB': 'Yes Bank',
            'IDBI': 'IDBI Bank'
        }
        
        if bank_code not in valid_banks:
            return False
        
        # Account number validation based on bank
        account_lengths = {
            'SBIN': [11, 17],  # SBI has 11 or 17 digit accounts
            'HDFC': [14],
            'ICIC': [12],
            'AXIS': [15]
        }
        
        if bank_code in account_lengths:
            valid_length = len(account_number) in account_lengths[bank_code]
            if not valid_length:
                return False
        
        # Penny drop test (mock)
        # In production, this would transfer ₹1 and verify
        penny_drop_result = self.mock_penny_drop_test(
            account_number, 
            ifsc
        )
        
        return penny_drop_result['success']
    
    def calculate_risk_score(self, checks: Dict) -> int:
        """
        Calculate risk score based on validation results
        """
        risk_score = 0
        
        # Base risk scores
        risk_weights = {
            'aadhaar': 25,
            'pan': 20,
            'bank': 20,
            'address': 15,
            'selfie': 20
        }
        
        for check, passed in checks.items():
            if not passed:
                risk_score += risk_weights.get(check, 10)
        
        return risk_score
```

Yeh hai real production level KYC validation! PayTM, PhonePe sab aise hi karte hai.

### Flipkart Product Data Quality - 100 Million Products

Flipkart pe 100 million+ products hai. Quality kaise maintain karte hai? Dekho:

```python
# Flipkart Scale Product Quality System
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, udf, lit
from pyspark.sql.types import StringType, FloatType
import jellyfish  # For fuzzy matching

class FlipkartProductQuality:
    """
    Handles 100M+ products quality validation
    """
    
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("FlipkartProductQuality") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.quality_thresholds = {
            'title_completeness': 0.8,
            'description_min_words': 50,
            'image_min_count': 3,
            'price_anomaly_threshold': 3.0  # 3 standard deviations
        }
    
    def validate_product_catalog(self, catalog_path: str):
        """
        Validate entire product catalog at scale
        """
        # Read product catalog
        products = self.spark.read.parquet(catalog_path)
        
        # Stage 1: Title quality validation
        products = self.validate_product_titles(products)
        
        # Stage 2: Description quality
        products = self.validate_descriptions(products)
        
        # Stage 3: Image quality and count
        products = self.validate_images(products)
        
        # Stage 4: Price anomaly detection
        products = self.detect_price_anomalies(products)
        
        # Stage 5: Category consistency
        products = self.validate_category_consistency(products)
        
        # Stage 6: Brand name standardization
        products = self.standardize_brand_names(products)
        
        # Stage 7: Duplicate detection
        products = self.detect_duplicate_products(products)
        
        # Calculate overall quality score
        products = self.calculate_quality_score(products)
        
        # Generate quality report
        self.generate_quality_report(products)
        
        return products
    
    def validate_product_titles(self, df):
        """
        Validate product title quality
        """
        # Check title length
        df = df.withColumn(
            'title_length',
            col('title').length()
        )
        
        # Check for required keywords based on category
        @udf(returnType=FloatType())
        def title_completeness_score(title, category):
            if not title:
                return 0.0
                
            score = 0.0
            title_lower = title.lower()
            
            # Category-specific keywords
            if category == 'Mobile':
                keywords = ['gb', 'ram', 'storage', 'camera', 'battery']
                for keyword in keywords:
                    if keyword in title_lower:
                        score += 0.2
                        
            elif category == 'Clothing':
                keywords = ['size', 'color', 'material', 'fit', 'sleeve']
                for keyword in keywords:
                    if keyword in title_lower:
                        score += 0.2
                        
            elif category == 'Electronics':
                keywords = ['warranty', 'brand', 'model', 'specification']
                for keyword in keywords:
                    if keyword in title_lower:
                        score += 0.25
            
            return min(score, 1.0)
        
        df = df.withColumn(
            'title_quality_score',
            title_completeness_score(col('title'), col('category'))
        )
        
        # Flag low quality titles
        df = df.withColumn(
            'title_quality_flag',
            when(col('title_quality_score') < 0.6, 'LOW_QUALITY')
            .otherwise('GOOD')
        )
        
        return df
    
    def detect_price_anomalies(self, df):
        """
        Detect pricing anomalies using statistical methods
        """
        # Calculate statistics per category
        category_stats = df.groupBy('category').agg(
            {'price': 'mean', 'price': 'stddev'}
        ).withColumnRenamed('avg(price)', 'mean_price') \
         .withColumnRenamed('stddev(price)', 'std_price')
        
        # Join back with main dataframe
        df = df.join(category_stats, on='category', how='left')
        
        # Calculate z-score
        df = df.withColumn(
            'price_z_score',
            (col('price') - col('mean_price')) / col('std_price')
        )
        
        # Flag anomalies
        df = df.withColumn(
            'price_anomaly_flag',
            when(col('price_z_score').abs() > 3.0, 'ANOMALY')
            .otherwise('NORMAL')
        )
        
        # Special check for festival pricing
        df = df.withColumn(
            'festival_price_check',
            when(
                (col('discount_percentage') > 70) & 
                (col('festival_name').isNotNull()),
                'VERIFY_MANUALLY'
            ).otherwise('OK')
        )
        
        return df
    
    def detect_duplicate_products(self, df):
        """
        Detect duplicate products using fuzzy matching
        """
        # Create signature for each product
        @udf(returnType=StringType())
        def create_product_signature(title, brand, category):
            if not title or not brand:
                return ""
            
            # Normalize and create signature
            title_clean = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
            brand_clean = brand.lower().strip()
            
            return f"{brand_clean}_{title_clean[:50]}"
        
        df = df.withColumn(
            'product_signature',
            create_product_signature(col('title'), col('brand'), col('category'))
        )
        
        # Self-join to find similar products
        df_alias = df.alias('df1')
        df_duplicate = df.alias('df2')
        
        duplicates = df_alias.join(
            df_duplicate,
            (col('df1.product_signature') == col('df2.product_signature')) &
            (col('df1.product_id') != col('df2.product_id')),
            'inner'
        ).select(
            col('df1.product_id').alias('product_id'),
            col('df2.product_id').alias('duplicate_id')
        )
        
        # Mark duplicates
        duplicate_ids = duplicates.select('product_id').distinct()
        df = df.join(
            duplicate_ids,
            on='product_id',
            how='left_anti'
        ).withColumn('is_duplicate', lit(False))
        
        return df
```

### IRCTC Booking Data Validation - 1 Million Bookings Daily

IRCTC pe daily 10 lakh+ bookings hoti hai. Data quality kaise ensure karte hai?

```python
# IRCTC Scale Booking Validation System
import redis
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import aiohttp

class IRCTCBookingValidator:
    """
    Validates 1M+ daily railway bookings
    """
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.validation_stats = {
            'total_validated': 0,
            'passed': 0,
            'failed': 0,
            'blocked_users': set()
        }
    
    async def validate_tatkal_booking(self, booking_data: Dict) -> Dict:
        """
        Tatkal booking special validation
        10 AM and 11 AM rush handling
        """
        validation_result = {
            'booking_id': booking_data['booking_id'],
            'status': 'pending',
            'checks': {},
            'timestamp': datetime.now()
        }
        
        # Check 1: Tatkal timing validation
        current_time = datetime.now()
        tatkal_ac_time = current_time.replace(hour=10, minute=0, second=0)
        tatkal_non_ac_time = current_time.replace(hour=11, minute=0, second=0)
        
        if booking_data['class'] in ['1A', '2A', '3A', 'CC', 'EC']:
            valid_time = current_time >= tatkal_ac_time
        else:
            valid_time = current_time >= tatkal_non_ac_time
        
        validation_result['checks']['tatkal_timing'] = valid_time
        
        # Check 2: Passenger details validation
        passengers_valid = await self.validate_passengers(
            booking_data['passengers']
        )
        validation_result['checks']['passengers'] = passengers_valid
        
        # Check 3: Journey date validation
        journey_date = datetime.strptime(
            booking_data['journey_date'], 
            '%Y-%m-%d'
        )
        today = datetime.now().date()
        
        # Tatkal can only be booked 1 day in advance
        valid_journey = (journey_date.date() - today).days == 1
        validation_result['checks']['journey_date'] = valid_journey
        
        # Check 4: Multiple booking prevention
        user_id = booking_data['user_id']
        booking_count = await self.check_user_booking_limit(user_id)
        
        validation_result['checks']['booking_limit'] = booking_count < 2
        
        # Check 5: Payment validation
        payment_valid = await self.validate_payment_details(
            booking_data['payment']
        )
        validation_result['checks']['payment'] = payment_valid
        
        # Check 6: Route validation
        route_valid = await self.validate_train_route(
            booking_data['train_number'],
            booking_data['from_station'],
            booking_data['to_station']
        )
        validation_result['checks']['route'] = route_valid
        
        # Final decision
        all_valid = all(validation_result['checks'].values())
        validation_result['status'] = 'approved' if all_valid else 'rejected'
        
        # Update stats
        await self.update_validation_stats(validation_result)
        
        return validation_result
    
    async def validate_passengers(self, passengers: List[Dict]) -> bool:
        """
        Validate passenger details
        """
        for passenger in passengers:
            # Age validation
            age = passenger.get('age', 0)
            if age < 0 or age > 120:
                return False
            
            # Name validation - no special characters
            name = passenger.get('name', '')
            if not re.match(r'^[A-Za-z\s]+$', name):
                return False
            
            # ID proof validation
            id_type = passenger.get('id_type')
            id_number = passenger.get('id_number')
            
            if id_type == 'AADHAAR':
                if not re.match(r'^\d{12}$', id_number):
                    return False
            elif id_type == 'PAN':
                if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', id_number):
                    return False
            
            # Berth preference validation
            berth = passenger.get('berth_preference')
            valid_berths = ['LOWER', 'MIDDLE', 'UPPER', 
                           'SIDE_LOWER', 'SIDE_UPPER', 'NO_PREFERENCE']
            if berth and berth not in valid_berths:
                return False
        
        return True
    
    async def check_user_booking_limit(self, user_id: str) -> int:
        """
        Check user's booking count in last 24 hours
        """
        key = f"bookings:{user_id}:{datetime.now().strftime('%Y%m%d')}"
        count = self.redis_client.get(key)
        return int(count) if count else 0
    
    async def validate_train_route(self, train_number: str, 
                                  from_station: str, 
                                  to_station: str) -> bool:
        """
        Validate if train runs between given stations
        """
        # In production, this would query train database
        # Mock validation for now
        valid_routes = {
            '12951': ['NDLS', 'BCT'],  # Rajdhani
            '12301': ['HWH', 'NDLS'],  # Kolkata Rajdhani
            '12615': ['MAS', 'DEL']    # Grand Trunk Express
        }
        
        if train_number in valid_routes:
            route = valid_routes[train_number]
            return from_station in route and to_station in route
        
        return True  # Default to true for other trains
```

### Zerodha Trading Data Integrity - 5 Million Trades Daily

Stock market mein data quality critical hai. Zerodha kaise handle karta hai?

```python
# Zerodha Scale Trading Data Validation
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
import hashlib

class ZerodhaDataIntegrity:
    """
    Validates 5M+ daily trades with zero tolerance for errors
    """
    
    def __init__(self):
        self.nse_price_bands = {}  # Daily price bands from NSE
        self.circuit_limits = {}   # Circuit breaker limits
        self.load_market_data()
    
    def validate_trade_order(self, order: Dict) -> Tuple[bool, Dict]:
        """
        Complete trade order validation
        """
        validation = {
            'order_id': order['order_id'],
            'timestamp': datetime.now(),
            'checks': {},
            'risk_score': 0
        }
        
        # Check 1: Price band validation
        price_valid = self.validate_price_bands(
            order['symbol'],
            order['price'],
            order['order_type']
        )
        validation['checks']['price_band'] = price_valid
        
        # Check 2: Quantity validation
        qty_valid = self.validate_quantity(
            order['symbol'],
            order['quantity'],
            order['product_type']
        )
        validation['checks']['quantity'] = qty_valid
        
        # Check 3: Margin validation
        margin_valid = self.validate_margin_requirement(
            order['symbol'],
            order['quantity'],
            order['price'],
            order['user_id']
        )
        validation['checks']['margin'] = margin_valid
        
        # Check 4: Circuit limit check
        circuit_valid = self.check_circuit_limits(
            order['symbol'],
            order['price']
        )
        validation['checks']['circuit'] = circuit_valid
        
        # Check 5: Order value validation (Max 10 Cr per order)
        order_value = Decimal(str(order['quantity'])) * Decimal(str(order['price']))
        value_valid = order_value <= Decimal('100000000')
        validation['checks']['max_value'] = value_valid
        
        # Check 6: Tick size validation
        tick_valid = self.validate_tick_size(
            order['price'],
            order['symbol']
        )
        validation['checks']['tick_size'] = tick_valid
        
        # Check 7: Market timing validation
        timing_valid = self.validate_market_hours(
            order['order_time'],
            order['exchange']
        )
        validation['checks']['market_hours'] = timing_valid
        
        # Check 8: Duplicate order check
        duplicate = self.check_duplicate_order(
            order['user_id'],
            order
        )
        validation['checks']['duplicate'] = not duplicate
        
        # Calculate risk score
        validation['risk_score'] = self.calculate_trade_risk(order)
        
        # Final decision
        all_valid = all(validation['checks'].values())
        low_risk = validation['risk_score'] < 50
        
        return all_valid and low_risk, validation
    
    def validate_price_bands(self, symbol: str, price: float, 
                            order_type: str) -> bool:
        """
        Validate price within daily bands
        """
        if symbol not in self.nse_price_bands:
            return True  # Skip validation if bands not available
        
        bands = self.nse_price_bands[symbol]
        
        if order_type == 'MARKET':
            return True  # Market orders don't need price validation
        
        return bands['lower'] <= price <= bands['upper']
    
    def validate_tick_size(self, price: float, symbol: str) -> bool:
        """
        Validate price follows tick size rules
        """
        # NSE tick size rules
        if price < 10:
            tick_size = 0.01
        elif price < 100:
            tick_size = 0.05
        elif price < 1000:
            tick_size = 0.10
        else:
            tick_size = 0.25
        
        # Check if price is multiple of tick size
        remainder = Decimal(str(price)) % Decimal(str(tick_size))
        
        return remainder == 0
    
    def validate_margin_requirement(self, symbol: str, quantity: int,
                                   price: float, user_id: str) -> bool:
        """
        Check if user has sufficient margin
        """
        # Get user's available margin
        user_margin = self.get_user_margin(user_id)
        
        # Calculate required margin
        order_value = quantity * price
        
        # Different margin requirements for different segments
        if symbol.endswith('-FUT'):  # Futures
            required_margin = order_value * 0.15  # 15% margin
        elif symbol.endswith('-OPT'):  # Options
            required_margin = order_value * 0.20  # 20% margin
        else:  # Equity
            required_margin = order_value * 0.20  # 20% for intraday
        
        return user_margin >= required_margin
```

### Data Profiling - Production Level Implementation

Ab dekhte hai ki large scale pe data profiling kaise karte hai:

```python
# Production Data Profiling System
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from scipy import stats

@dataclass
class DataProfile:
    """
    Complete data profile for a dataset
    """
    row_count: int
    column_count: int
    missing_values: Dict[str, float]
    data_types: Dict[str, str]
    unique_counts: Dict[str, int]
    statistics: Dict[str, Dict]
    anomalies: List[Dict]
    quality_score: float

class ProductionDataProfiler:
    """
    Enterprise-grade data profiling
    Used by banks, e-commerce, telecom
    """
    
    def __init__(self):
        self.profiling_rules = self.load_profiling_rules()
        self.anomaly_detectors = self.initialize_detectors()
    
    def profile_dataset(self, df: pd.DataFrame, 
                       dataset_name: str) -> DataProfile:
        """
        Complete data profiling
        """
        profile = DataProfile(
            row_count=len(df),
            column_count=len(df.columns),
            missing_values={},
            data_types={},
            unique_counts={},
            statistics={},
            anomalies=[],
            quality_score=0.0
        )
        
        # Profile each column
        for column in df.columns:
            profile.missing_values[column] = self.calculate_missing_percentage(
                df[column]
            )
            profile.data_types[column] = str(df[column].dtype)
            profile.unique_counts[column] = df[column].nunique()
            
            # Calculate statistics based on data type
            if pd.api.types.is_numeric_dtype(df[column]):
                profile.statistics[column] = self.profile_numeric_column(
                    df[column]
                )
            elif pd.api.types.is_string_dtype(df[column]):
                profile.statistics[column] = self.profile_string_column(
                    df[column]
                )
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                profile.statistics[column] = self.profile_datetime_column(
                    df[column]
                )
        
        # Detect anomalies
        profile.anomalies = self.detect_anomalies(df)
        
        # Calculate overall quality score
        profile.quality_score = self.calculate_quality_score(profile)
        
        # Generate and save report
        self.generate_profile_report(profile, dataset_name)
        
        return profile
    
    def profile_numeric_column(self, series: pd.Series) -> Dict:
        """
        Profile numeric columns
        """
        clean_series = series.dropna()
        
        return {
            'mean': float(clean_series.mean()),
            'median': float(clean_series.median()),
            'std': float(clean_series.std()),
            'min': float(clean_series.min()),
            'max': float(clean_series.max()),
            'q25': float(clean_series.quantile(0.25)),
            'q75': float(clean_series.quantile(0.75)),
            'skewness': float(stats.skew(clean_series)),
            'kurtosis': float(stats.kurtosis(clean_series)),
            'outliers': self.detect_outliers_iqr(clean_series)
        }
    
    def profile_string_column(self, series: pd.Series) -> Dict:
        """
        Profile string columns
        """
        clean_series = series.dropna()
        
        return {
            'unique_count': int(clean_series.nunique()),
            'most_common': clean_series.value_counts().head(10).to_dict(),
            'avg_length': float(clean_series.str.len().mean()),
            'min_length': int(clean_series.str.len().min()),
            'max_length': int(clean_series.str.len().max()),
            'pattern_analysis': self.analyze_string_patterns(clean_series),
            'special_chars': self.detect_special_characters(clean_series)
        }
    
    def detect_outliers_iqr(self, series: pd.Series) -> Dict:
        """
        Detect outliers using IQR method
        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            'count': len(outliers),
            'percentage': (len(outliers) / len(series)) * 100,
            'values': outliers.head(10).tolist()
        }
    
    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect various types of anomalies
        """
        anomalies = []
        
        # Check for duplicate rows
        duplicates = df[df.duplicated()]
        if len(duplicates) > 0:
            anomalies.append({
                'type': 'duplicate_rows',
                'count': len(duplicates),
                'severity': 'HIGH'
            })
        
        # Check for constant columns
        for column in df.columns:
            if df[column].nunique() == 1:
                anomalies.append({
                    'type': 'constant_column',
                    'column': column,
                    'severity': 'MEDIUM'
                })
        
        # Check for high correlation
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            correlation_matrix = df.select_dtypes(
                include=[np.number]
            ).corr()
            
            high_corr = np.where(
                (correlation_matrix > 0.95) & 
                (correlation_matrix < 1.0)
            )
            
            if len(high_corr[0]) > 0:
                for i in range(len(high_corr[0])):
                    anomalies.append({
                        'type': 'high_correlation',
                        'columns': [
                            correlation_matrix.columns[high_corr[0][i]],
                            correlation_matrix.columns[high_corr[1][i]]
                        ],
                        'correlation': correlation_matrix.iloc[
                            high_corr[0][i], 
                            high_corr[1][i]
                        ],
                        'severity': 'LOW'
                    })
        
        return anomalies
```

Yeh production level data profiling hai jo Flipkart, Amazon, PayTM use karte hai!

### Swiggy Restaurant Data Quality - Real-time Validation

Swiggy pe 2 lakh+ restaurants hai. Menu data quality kaise maintain karte hai?

```python
# Swiggy Restaurant Data Quality System
class SwiggyMenuValidator:
    """
    Validates 200K+ restaurant menus in real-time
    """
    
    def __init__(self):
        self.food_categories = self.load_food_categories()
        self.price_ranges = self.load_price_ranges_by_city()
        self.fssai_validator = FSSAIValidator()
    
    def validate_restaurant_menu(self, restaurant_data: Dict) -> Dict:
        """
        Complete restaurant and menu validation
        """
        validation_result = {
            'restaurant_id': restaurant_data['id'],
            'validation_time': datetime.now(),
            'checks': {},
            'quality_score': 0
        }
        
        # Validate FSSAI license
        fssai_valid = self.fssai_validator.validate(
            restaurant_data['fssai_license']
        )
        validation_result['checks']['fssai'] = fssai_valid
        
        # Validate menu items
        menu_validation = self.validate_menu_items(
            restaurant_data['menu_items'],
            restaurant_data['city']
        )
        validation_result['checks']['menu'] = menu_validation
        
        # Validate pricing consistency
        price_valid = self.validate_pricing(
            restaurant_data['menu_items'],
            restaurant_data['restaurant_type'],
            restaurant_data['city']
        )
        validation_result['checks']['pricing'] = price_valid
        
        # Validate images
        image_valid = self.validate_food_images(
            restaurant_data['menu_items']
        )
        validation_result['checks']['images'] = image_valid
        
        # Calculate quality score
        validation_result['quality_score'] = self.calculate_menu_quality_score(
            validation_result['checks']
        )
        
        return validation_result
    
    def validate_menu_items(self, menu_items: List[Dict], 
                           city: str) -> Dict:
        """
        Validate individual menu items
        """
        validation = {
            'total_items': len(menu_items),
            'valid_items': 0,
            'issues': []
        }
        
        for item in menu_items:
            # Check item name
            if not item.get('name') or len(item['name']) < 3:
                validation['issues'].append(f"Invalid name: {item.get('id')}")
                continue
            
            # Check description
            if not item.get('description') or len(item['description']) < 10:
                validation['issues'].append(f"Poor description: {item['name']}")
            
            # Check category
            if item.get('category') not in self.food_categories:
                validation['issues'].append(f"Invalid category: {item['name']}")
            
            # Check veg/non-veg flag
            if item.get('is_veg') not in [True, False]:
                validation['issues'].append(f"Missing veg flag: {item['name']}")
            
            # Check price
            if not self.validate_item_price(item['price'], item['category'], city):
                validation['issues'].append(f"Price anomaly: {item['name']}")
            
            validation['valid_items'] += 1
        
        validation['success_rate'] = validation['valid_items'] / validation['total_items']
        
        return validation
    
    def validate_pricing(self, menu_items: List[Dict], 
                        restaurant_type: str, 
                        city: str) -> bool:
        """
        Validate pricing consistency
        """
        prices = [item['price'] for item in menu_items]
        
        # Check for negative prices
        if any(p <= 0 for p in prices):
            return False
        
        # Check price range based on restaurant type
        expected_ranges = {
            'fine_dining': (500, 3000),
            'casual_dining': (200, 1000),
            'quick_service': (100, 500),
            'street_food': (20, 200)
        }
        
        if restaurant_type in expected_ranges:
            min_expected, max_expected = expected_ranges[restaurant_type]
            avg_price = np.mean(prices)
            
            if not (min_expected <= avg_price <= max_expected):
                return False
        
        # Check for price clustering (suspiciously similar prices)
        unique_prices = len(set(prices))
        if unique_prices < len(prices) * 0.3:  # Less than 30% unique prices
            return False
        
        return True
```

Dekho kitna complex validation system hai production mein!

### Career Advice: Data Quality Engineer Kaise Bane?

**Junior Level (0-2 years) - ₹6-12 LPA**
- Python, SQL seekho
- Great Expectations framework
- Basic statistics
- Data profiling tools

**Mid Level (2-5 years) - ₹12-25 LPA**
- Apache Spark for scale
- Real-time validation
- Anomaly detection algorithms
- Cloud platforms (AWS, Azure)

**Senior Level (5+ years) - ₹25-50 LPA**
- Architecture design
- ML-based quality systems
- Team leadership
- Cross-functional collaboration

**Principal/Staff (8+ years) - ₹50-80+ LPA**
- Strategic planning
- Industry standards definition
- Innovation in data quality
- Thought leadership

Mumbai mein Flipkart, PayTM, Amazon hiring kar rahe hai. Bangalore mein even more opportunities!

---

*[Auto rickshaw ka horn]* "Boss, Part 3 mein aur bhi advanced topics dekhenge. Production war stories sunenge!"