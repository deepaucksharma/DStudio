#!/usr/bin/env python3
"""
Episode 22: Streaming Architectures - Real-time Fraud Detection for Indian Banking
Author: Code Developer Agent
Description: ML-powered real-time fraud detection using streaming data

Real-time fraud detection में हर millisecond count करता है
Indian banking में fraud patterns बहुत sophisticated हैं
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import math
from collections import deque, defaultdict
import threading
import logging

# Fraud Detection Models
class TransactionType(Enum):
    UPI = "upi"
    CARD = "card"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    NEFT = "neft"
    RTGS = "rtgs"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Transaction:
    """Banking transaction model"""
    transaction_id: str
    user_id: str
    account_number: str
    transaction_type: TransactionType
    amount: float
    currency: str
    timestamp: datetime
    merchant_id: Optional[str]
    merchant_category: Optional[str]
    location: Dict[str, float]  # {"lat": 19.0760, "lon": 72.8777}
    device_id: str
    ip_address: str
    user_agent: str
    is_authenticated: bool
    authentication_method: str
    metadata: Dict[str, Any]

@dataclass
class FraudAlert:
    """Fraud detection alert"""
    alert_id: str
    transaction_id: str
    user_id: str
    risk_score: float
    risk_level: RiskLevel
    fraud_types: List[str]
    confidence: float
    reasons: List[str]
    suggested_action: str
    created_at: datetime
    features: Dict[str, Any]

@dataclass
class UserProfile:
    """User behavioral profile"""
    user_id: str
    account_number: str
    typical_amounts: List[float]
    typical_locations: List[Dict]
    typical_hours: List[int]
    typical_merchants: List[str]
    average_daily_transactions: float
    max_single_transaction: float
    preferred_payment_methods: List[str]
    last_updated: datetime
    risk_score_history: List[float]

# Feature Engineering
class FraudFeatureExtractor:
    """Extract fraud detection features from transactions"""
    
    def __init__(self):
        self.user_profiles = {}
        self.transaction_history = defaultdict(deque)  # Last 100 transactions per user
        self.location_clusters = {}  # User's frequent locations
        self.merchant_categories = {
            "grocery": ["bigbasket", "grofers", "dmart"],
            "food": ["zomato", "swiggy", "dominos"],
            "transport": ["ola", "uber", "irctc"],
            "ecommerce": ["amazon", "flipkart", "myntra"],
            "entertainment": ["bookmyshow", "netflix", "spotify"],
            "utilities": ["electricity", "gas", "mobile_recharge"]
        }
    
    def extract_features(self, transaction: Transaction) -> Dict[str, float]:
        """Extract fraud detection features"""
        features = {}
        
        # 1. Amount-based features
        features.update(self._extract_amount_features(transaction))
        
        # 2. Time-based features
        features.update(self._extract_time_features(transaction))
        
        # 3. Location-based features
        features.update(self._extract_location_features(transaction))
        
        # 4. Device/Network features
        features.update(self._extract_device_features(transaction))
        
        # 5. Behavioral features
        features.update(self._extract_behavioral_features(transaction))
        
        # 6. Velocity features
        features.update(self._extract_velocity_features(transaction))
        
        return features
    
    def _extract_amount_features(self, transaction: Transaction) -> Dict[str, float]:
        """Amount-based fraud indicators"""
        features = {}
        
        # Basic amount features
        features['amount'] = transaction.amount
        features['amount_log'] = math.log1p(transaction.amount)
        
        # Round number indicator (fraudsters often use round numbers)
        features['is_round_amount'] = 1.0 if transaction.amount % 1000 == 0 else 0.0
        
        # Large amount indicator
        features['is_large_amount'] = 1.0 if transaction.amount > 50000 else 0.0
        
        # Very large amount indicator
        features['is_very_large_amount'] = 1.0 if transaction.amount > 200000 else 0.0
        
        # Get user's historical transaction amounts
        user_history = self.transaction_history.get(transaction.user_id, deque())
        if user_history:
            historical_amounts = [t.amount for t in user_history]
            avg_amount = np.mean(historical_amounts)
            std_amount = np.std(historical_amounts) if len(historical_amounts) > 1 else 0
            max_amount = max(historical_amounts)
            
            # Deviation from user's typical amount
            features['amount_deviation_from_avg'] = abs(transaction.amount - avg_amount) / (avg_amount + 1)
            features['amount_z_score'] = (transaction.amount - avg_amount) / (std_amount + 1)
            features['amount_ratio_to_max'] = transaction.amount / (max_amount + 1)
        else:
            features['amount_deviation_from_avg'] = 0.0
            features['amount_z_score'] = 0.0
            features['amount_ratio_to_max'] = 0.0
        
        return features
    
    def _extract_time_features(self, transaction: Transaction) -> Dict[str, float]:
        """Time-based fraud indicators"""
        features = {}
        
        # Time of day (hour)
        hour = transaction.timestamp.hour
        features['hour'] = hour
        features['is_night_time'] = 1.0 if hour < 6 or hour > 23 else 0.0
        features['is_business_hours'] = 1.0 if 9 <= hour <= 18 else 0.0
        
        # Day of week
        day_of_week = transaction.timestamp.weekday()
        features['day_of_week'] = day_of_week
        features['is_weekend'] = 1.0 if day_of_week >= 5 else 0.0
        
        # Time since last transaction
        user_history = self.transaction_history.get(transaction.user_id, deque())
        if user_history:
            last_transaction = user_history[-1]
            time_diff = (transaction.timestamp - last_transaction.timestamp).total_seconds()
            features['time_since_last_transaction'] = time_diff / 3600  # Hours
            features['is_rapid_transaction'] = 1.0 if time_diff < 60 else 0.0  # < 1 minute
        else:
            features['time_since_last_transaction'] = 24.0  # Default to 24 hours
            features['is_rapid_transaction'] = 0.0
        
        return features
    
    def _extract_location_features(self, transaction: Transaction) -> Dict[str, float]:
        """Location-based fraud indicators"""
        features = {}
        
        # Basic location features
        lat = transaction.location.get('lat', 0.0)
        lon = transaction.location.get('lon', 0.0)
        
        features['latitude'] = lat
        features['longitude'] = lon
        
        # Major Indian cities (simplified coordinates)
        major_cities = {
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.7041, 77.1025),
            'bangalore': (12.9716, 77.5946),
            'hyderabad': (17.3850, 78.4867),
            'chennai': (13.0827, 80.2707),
            'kolkata': (22.5726, 88.3639),
            'pune': (18.5204, 73.8567),
            'ahmedabad': (23.0225, 72.5714)
        }
        
        # Distance from major cities
        min_distance_to_city = float('inf')
        for city, (city_lat, city_lon) in major_cities.items():
            distance = self._calculate_distance(lat, lon, city_lat, city_lon)
            min_distance_to_city = min(min_distance_to_city, distance)
            features[f'distance_to_{city}'] = distance
        
        features['min_distance_to_major_city'] = min_distance_to_city
        features['is_in_major_city'] = 1.0 if min_distance_to_city < 50 else 0.0  # Within 50km
        
        # Distance from user's typical locations
        user_history = self.transaction_history.get(transaction.user_id, deque())
        if user_history:
            historical_locations = [(t.location.get('lat', 0), t.location.get('lon', 0)) 
                                  for t in user_history if t.location]
            
            if historical_locations:
                distances = [self._calculate_distance(lat, lon, hist_lat, hist_lon) 
                           for hist_lat, hist_lon in historical_locations]
                min_distance = min(distances)
                avg_distance = np.mean(distances)
                
                features['min_distance_from_usual'] = min_distance
                features['avg_distance_from_usual'] = avg_distance
                features['is_unusual_location'] = 1.0 if min_distance > 100 else 0.0  # > 100km
            else:
                features['min_distance_from_usual'] = 0.0
                features['avg_distance_from_usual'] = 0.0
                features['is_unusual_location'] = 0.0
        else:
            features['min_distance_from_usual'] = 0.0
            features['avg_distance_from_usual'] = 0.0
            features['is_unusual_location'] = 0.0
        
        return features
    
    def _extract_device_features(self, transaction: Transaction) -> Dict[str, float]:
        """Device and network-based features"""
        features = {}
        
        # Device consistency
        user_history = self.transaction_history.get(transaction.user_id, deque())
        if user_history:
            historical_devices = [t.device_id for t in user_history]
            device_frequency = historical_devices.count(transaction.device_id)
            
            features['device_frequency'] = device_frequency
            features['is_new_device'] = 1.0 if device_frequency == 0 else 0.0
            features['device_consistency'] = device_frequency / len(historical_devices)
        else:
            features['device_frequency'] = 0.0
            features['is_new_device'] = 1.0
            features['device_consistency'] = 0.0
        
        # IP address features (simplified)
        ip_parts = transaction.ip_address.split('.')
        if len(ip_parts) == 4:
            # Check for private IP ranges (more trusted)
            first_octet = int(ip_parts[0])
            features['is_private_ip'] = 1.0 if first_octet in [10, 172, 192] else 0.0
        else:
            features['is_private_ip'] = 0.0
        
        # User agent consistency
        if user_history:
            historical_user_agents = [t.user_agent for t in user_history]
            ua_frequency = historical_user_agents.count(transaction.user_agent)
            features['user_agent_consistency'] = ua_frequency / len(historical_user_agents)
        else:
            features['user_agent_consistency'] = 0.0
        
        return features
    
    def _extract_behavioral_features(self, transaction: Transaction) -> Dict[str, float]:
        """User behavioral patterns"""
        features = {}
        
        # Authentication strength
        auth_scores = {
            'otp': 0.9,
            'biometric': 0.95,
            'pin': 0.7,
            'password': 0.6,
            'none': 0.0
        }
        
        features['auth_score'] = auth_scores.get(transaction.authentication_method, 0.5)
        features['is_authenticated'] = 1.0 if transaction.is_authenticated else 0.0
        
        # Merchant category analysis
        if transaction.merchant_id:
            merchant_category = self._get_merchant_category(transaction.merchant_id)
            features[f'merchant_category_{merchant_category}'] = 1.0
            
            # Check if user typically transacts with this category
            user_history = self.transaction_history.get(transaction.user_id, deque())
            if user_history:
                historical_categories = [self._get_merchant_category(t.merchant_id) 
                                       for t in user_history if t.merchant_id]
                category_frequency = historical_categories.count(merchant_category)
                features['merchant_category_familiarity'] = category_frequency / len(user_history)
            else:
                features['merchant_category_familiarity'] = 0.0
        else:
            features['merchant_category_familiarity'] = 0.0
        
        return features
    
    def _extract_velocity_features(self, transaction: Transaction) -> Dict[str, float]:
        """Transaction velocity features"""
        features = {}
        
        user_history = list(self.transaction_history.get(transaction.user_id, deque()))
        
        if not user_history:
            return {
                'transactions_last_hour': 0.0,
                'transactions_last_day': 0.0,
                'amount_last_hour': 0.0,
                'amount_last_day': 0.0,
                'velocity_score': 0.0
            }
        
        current_time = transaction.timestamp
        
        # Transactions in last hour
        last_hour = current_time - timedelta(hours=1)
        recent_transactions = [t for t in user_history if t.timestamp >= last_hour]
        features['transactions_last_hour'] = len(recent_transactions)
        features['amount_last_hour'] = sum(t.amount for t in recent_transactions)
        
        # Transactions in last day
        last_day = current_time - timedelta(days=1)
        day_transactions = [t for t in user_history if t.timestamp >= last_day]
        features['transactions_last_day'] = len(day_transactions)
        features['amount_last_day'] = sum(t.amount for t in day_transactions)
        
        # Velocity score (combination of frequency and amount)
        normal_daily_transactions = 5  # Typical user does 5 transactions per day
        normal_daily_amount = 10000  # Typical daily spending
        
        velocity_score = (
            (features['transactions_last_day'] / normal_daily_transactions) +
            (features['amount_last_day'] / normal_daily_amount)
        ) / 2
        
        features['velocity_score'] = velocity_score
        
        return features
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        if lat1 == 0 and lon1 == 0:
            return 1000  # Unknown location, assume far
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _get_merchant_category(self, merchant_id: str) -> str:
        """Get merchant category from merchant ID"""
        if not merchant_id:
            return "unknown"
        
        merchant_lower = merchant_id.lower()
        
        for category, merchants in self.merchant_categories.items():
            for merchant in merchants:
                if merchant in merchant_lower:
                    return category
        
        return "others"
    
    def update_user_history(self, transaction: Transaction):
        """Update user transaction history"""
        user_history = self.transaction_history[transaction.user_id]
        user_history.append(transaction)
        
        # Keep only last 100 transactions
        if len(user_history) > 100:
            user_history.popleft()

# ML-based Fraud Detector
class FraudDetectionModel:
    """Simplified ML model for fraud detection"""
    
    def __init__(self):
        self.feature_weights = {
            # Amount features
            'is_large_amount': 0.15,
            'is_very_large_amount': 0.25,
            'amount_z_score': 0.20,
            'is_round_amount': 0.05,
            
            # Time features
            'is_night_time': 0.10,
            'is_rapid_transaction': 0.20,
            
            # Location features
            'is_unusual_location': 0.30,
            'min_distance_from_usual': 0.15,
            
            # Device features
            'is_new_device': 0.25,
            'device_consistency': -0.20,  # Negative weight (good sign)
            
            # Behavioral features
            'auth_score': -0.15,  # Negative weight (good sign)
            'merchant_category_familiarity': -0.10,  # Negative weight
            
            # Velocity features
            'velocity_score': 0.25,
            'transactions_last_hour': 0.15
        }
        
        self.threshold_low = 0.3
        self.threshold_medium = 0.5
        self.threshold_high = 0.7
        self.threshold_critical = 0.85
    
    def predict_fraud(self, features: Dict[str, float]) -> Tuple[float, RiskLevel, List[str]]:
        """Predict fraud probability and risk level"""
        
        # Calculate weighted score
        risk_score = 0.0
        active_features = []
        
        for feature_name, weight in self.feature_weights.items():
            if feature_name in features:
                feature_value = features[feature_name]
                contribution = weight * feature_value
                risk_score += contribution
                
                # Track significant contributing features
                if abs(contribution) > 0.05:
                    active_features.append(feature_name)
        
        # Normalize score to 0-1 range
        risk_score = max(0.0, min(1.0, risk_score))
        
        # Determine risk level
        if risk_score >= self.threshold_critical:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= self.threshold_high:
            risk_level = RiskLevel.HIGH
        elif risk_score >= self.threshold_medium:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return risk_score, risk_level, active_features

# Real-time Fraud Detection Engine
class RealTimeFraudDetectionEngine:
    """Real-time fraud detection engine"""
    
    def __init__(self):
        self.feature_extractor = FraudFeatureExtractor()
        self.fraud_model = FraudDetectionModel()
        self.alerts_generated = []
        self.transactions_processed = 0
        self.fraud_detected = 0
    
    async def process_transaction(self, transaction: Transaction) -> Optional[FraudAlert]:
        """Process transaction for fraud detection"""
        try:
            self.transactions_processed += 1
            
            # Extract features
            features = self.feature_extractor.extract_features(transaction)
            
            # Predict fraud
            risk_score, risk_level, active_features = self.fraud_model.predict_fraud(features)
            
            # Update user history
            self.feature_extractor.update_user_history(transaction)
            
            # Generate alert if high risk
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                alert = self._generate_fraud_alert(
                    transaction, risk_score, risk_level, active_features, features
                )
                self.alerts_generated.append(alert)
                self.fraud_detected += 1
                
                print(f"🚨 FRAUD ALERT: {alert.alert_id} | Risk: {risk_score:.3f} | Level: {risk_level.value}")
                return alert
            
            elif risk_level == RiskLevel.MEDIUM:
                print(f"⚠️ Medium Risk: {transaction.transaction_id} | Risk: {risk_score:.3f}")
            
            return None
            
        except Exception as e:
            print(f"❌ Error processing transaction {transaction.transaction_id}: {e}")
            return None
    
    def _generate_fraud_alert(self, transaction: Transaction, risk_score: float, 
                            risk_level: RiskLevel, active_features: List[str], 
                            features: Dict[str, float]) -> FraudAlert:
        """Generate fraud alert"""
        
        # Determine fraud types based on active features
        fraud_types = []
        reasons = []
        
        if 'is_very_large_amount' in active_features:
            fraud_types.append("UNUSUAL_AMOUNT")
            reasons.append(f"Very large transaction: ₹{transaction.amount:,.2f}")
        
        if 'is_unusual_location' in active_features:
            fraud_types.append("LOCATION_ANOMALY")
            reasons.append("Transaction from unusual location")
        
        if 'is_new_device' in active_features:
            fraud_types.append("NEW_DEVICE")
            reasons.append("Transaction from new/unknown device")
        
        if 'is_night_time' in active_features:
            fraud_types.append("UNUSUAL_TIME")
            reasons.append("Transaction during unusual hours")
        
        if 'velocity_score' in active_features:
            fraud_types.append("HIGH_VELOCITY")
            reasons.append("High transaction velocity detected")
        
        if 'is_rapid_transaction' in active_features:
            fraud_types.append("RAPID_TRANSACTIONS")
            reasons.append("Rapid successive transactions")
        
        # Determine suggested action
        if risk_level == RiskLevel.CRITICAL:
            suggested_action = "BLOCK_TRANSACTION"
        elif risk_level == RiskLevel.HIGH:
            suggested_action = "MANUAL_REVIEW"
        else:
            suggested_action = "MONITOR"
        
        return FraudAlert(
            alert_id=f"FA{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}",
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            risk_score=risk_score,
            risk_level=risk_level,
            fraud_types=fraud_types,
            confidence=min(0.95, risk_score + 0.1),
            reasons=reasons,
            suggested_action=suggested_action,
            created_at=datetime.now(),
            features=features
        )

# Transaction Generator for Demo
class TransactionGenerator:
    """Generate realistic transactions with some fraudulent ones"""
    
    def __init__(self):
        self.users = [
            {"user_id": "U001", "account": "1234567890", "name": "Rajesh Sharma"},
            {"user_id": "U002", "account": "2345678901", "name": "Priya Patel"},
            {"user_id": "U003", "account": "3456789012", "name": "Amit Kumar"},
            {"user_id": "U004", "account": "4567890123", "name": "Sunita Singh"},
            {"user_id": "U005", "account": "5678901234", "name": "Rohit Gupta"}
        ]
        
        self.merchants = [
            "amazon_in", "flipkart", "zomato", "swiggy", "paytm_mall",
            "myntra", "bigbasket", "bookmyshow", "uber", "ola"
        ]
        
        self.locations = {
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.7041, 77.1025),
            "bangalore": (12.9716, 77.5946),
            "pune": (18.5204, 73.8567),
            "chennai": (13.0827, 80.2707)
        }
    
    def generate_normal_transaction(self) -> Transaction:
        """Generate normal transaction"""
        import random
        
        user = random.choice(self.users)
        location_name = random.choice(list(self.locations.keys()))
        location = self.locations[location_name]
        
        # Add some noise to location
        lat = location[0] + random.uniform(-0.1, 0.1)
        lon = location[1] + random.uniform(-0.1, 0.1)
        
        return Transaction(
            transaction_id=f"TXN{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}",
            user_id=user["user_id"],
            account_number=user["account"],
            transaction_type=random.choice(list(TransactionType)),
            amount=round(random.uniform(100, 5000), 2),
            currency="INR",
            timestamp=datetime.now(),
            merchant_id=random.choice(self.merchants),
            merchant_category="ecommerce",
            location={"lat": lat, "lon": lon},
            device_id=f"DEV_{user['user_id']}_001",  # Consistent device
            ip_address=f"192.168.1.{random.randint(1, 254)}",  # Private IP
            user_agent="Mozilla/5.0 (Android 11; Mobile)",
            is_authenticated=True,
            authentication_method="otp",
            metadata={"app_version": "1.2.3", "session_id": uuid.uuid4().hex[:8]}
        )
    
    def generate_fraudulent_transaction(self) -> Transaction:
        """Generate fraudulent transaction"""
        import random
        
        user = random.choice(self.users)
        
        # Fraudulent patterns
        fraud_patterns = [
            "large_amount", "unusual_location", "new_device", 
            "night_time", "rapid_transactions"
        ]
        
        pattern = random.choice(fraud_patterns)
        
        if pattern == "large_amount":
            amount = round(random.uniform(75000, 200000), 2)
            location = self.locations["mumbai"]
        elif pattern == "unusual_location":
            amount = round(random.uniform(1000, 10000), 2)
            # Unusual location (international coordinates)
            location = (40.7128, -74.0060)  # New York
        elif pattern == "new_device":
            amount = round(random.uniform(5000, 25000), 2)
            device_id = f"DEV_UNKNOWN_{uuid.uuid4().hex[:8]}"
            location = self.locations["mumbai"]
        elif pattern == "night_time":
            amount = round(random.uniform(2000, 15000), 2)
            # Set timestamp to night time
            timestamp = datetime.now().replace(hour=2, minute=30)
            location = self.locations["mumbai"]
        else:  # rapid_transactions
            amount = round(random.uniform(3000, 8000), 2)
            location = self.locations["mumbai"]
        
        # Common fraudulent characteristics
        is_authenticated = random.choice([True, False])  # Sometimes not authenticated
        auth_method = random.choice(["none", "pin", "otp"])
        
        base_transaction = Transaction(
            transaction_id=f"TXN{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}",
            user_id=user["user_id"],
            account_number=user["account"],
            transaction_type=random.choice(list(TransactionType)),
            amount=amount,
            currency="INR",
            timestamp=datetime.now() if pattern != "night_time" else timestamp,
            merchant_id=random.choice(self.merchants),
            merchant_category="ecommerce",
            location={"lat": location[0], "lon": location[1]},
            device_id=device_id if pattern == "new_device" else f"DEV_{user['user_id']}_001",
            ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Unknown Device)",
            is_authenticated=is_authenticated,
            authentication_method=auth_method,
            metadata={"app_version": "1.0.0", "session_id": uuid.uuid4().hex[:8]}
        )
        
        return base_transaction

# Demo Function
async def demonstrate_realtime_fraud_detection():
    """Demonstrate real-time fraud detection"""
    print("🛡️ Real-time Fraud Detection Demo")
    print("=" * 50)
    
    # Initialize fraud detection engine
    fraud_engine = RealTimeFraudDetectionEngine()
    transaction_generator = TransactionGenerator()
    
    try:
        print("\n📊 Processing transactions...")
        
        # Generate normal transactions first (to build user profiles)
        print("\n✅ Processing normal transactions to build user profiles...")
        for i in range(15):
            transaction = transaction_generator.generate_normal_transaction()
            await fraud_engine.process_transaction(transaction)
            await asyncio.sleep(0.1)  # Small delay
        
        # Now process some fraudulent transactions
        print("\n🚨 Processing potentially fraudulent transactions...")
        for i in range(10):
            # Mix of normal and fraudulent
            if i % 3 == 0:  # Every 3rd transaction is fraudulent
                transaction = transaction_generator.generate_fraudulent_transaction()
            else:
                transaction = transaction_generator.generate_normal_transaction()
            
            await fraud_engine.process_transaction(transaction)
            await asyncio.sleep(0.2)
        
        # Display results
        print(f"\n📈 Fraud Detection Summary:")
        print(f"  Total Transactions Processed: {fraud_engine.transactions_processed}")
        print(f"  Fraud Alerts Generated: {fraud_engine.fraud_detected}")
        print(f"  Detection Rate: {(fraud_engine.fraud_detected / fraud_engine.transactions_processed) * 100:.1f}%")
        
        # Show recent alerts
        print(f"\n🚨 Recent Fraud Alerts:")
        for alert in fraud_engine.alerts_generated[-5:]:  # Last 5 alerts
            print(f"  Alert {alert.alert_id}:")
            print(f"    Risk Score: {alert.risk_score:.3f}")
            print(f"    Risk Level: {alert.risk_level.value}")
            print(f"    Fraud Types: {', '.join(alert.fraud_types)}")
            print(f"    Action: {alert.suggested_action}")
            print(f"    Reasons: {'; '.join(alert.reasons)}")
            print()
        
        print("✅ Real-time Fraud Detection Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    """
    Key Real-time Fraud Detection Benefits:
    1. Immediate Detection: Fraud को milliseconds में detect करना
    2. Feature Engineering: Complex patterns और behavioral analysis
    3. Scalability: High-volume transaction processing
    4. Adaptability: User behavior patterns को learn करना
    5. Multi-layered: Multiple fraud indicators combine करना
    6. Real-time Actions: Immediate blocking या alerts
    7. Continuous Learning: Fraud patterns को continuously update करना
    """
    asyncio.run(demonstrate_realtime_fraud_detection())