#!/usr/bin/env python3
"""
Paytm-style Fraud Detection System - MLOps Episode 44
Production-ready fraud detection with real-time ML inference

Author: Claude Code
Context: Real-time fraud detection system like Paytm's production system
"""

import json
import time
import uuid
import hashlib
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FraudRiskLevel(Enum):
    """Fraud risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TransactionStatus(Enum):
    """Transaction processing status"""
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    MANUAL_REVIEW = "manual_review"
    BLOCKED = "blocked"

@dataclass
class Transaction:
    """Transaction data structure"""
    transaction_id: str
    user_id: str
    amount: float
    merchant_id: str
    merchant_category: str
    timestamp: datetime
    location_lat: Optional[float]
    location_lon: Optional[float]
    device_id: str
    ip_address: str
    payment_method: str
    currency: str = "INR"
    
@dataclass
class FraudFeatures:
    """Extracted features for fraud detection"""
    # Amount features
    amount: float
    amount_zscore: float
    amount_percentile: float
    
    # Velocity features
    transaction_count_1h: int
    transaction_count_24h: int
    total_amount_1h: float
    total_amount_24h: float
    
    # User behavior features
    user_age_days: int
    user_transaction_frequency: float
    user_avg_amount: float
    new_merchant_flag: bool
    
    # Location features
    location_distance_km: float
    location_velocity_kmh: float
    unusual_location_flag: bool
    
    # Device features
    new_device_flag: bool
    device_change_flag: bool
    
    # Time features
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    is_night: bool
    
    # Network features
    ip_risk_score: float
    vpn_flag: bool

@dataclass
class FraudPrediction:
    """Fraud prediction result"""
    transaction_id: str
    fraud_probability: float
    risk_level: FraudRiskLevel
    prediction_time_ms: float
    model_version: str
    features_used: Dict[str, float]
    risk_factors: List[str]
    recommended_action: TransactionStatus

class PaytmFraudDetector:
    """
    Production Fraud Detection System for Paytm-style payments
    Mumbai me sabse advanced fraud detection!
    """
    
    def __init__(self, db_path: str = "fraud_detection.db"):
        self.db_path = db_path
        self.models = {}
        self.feature_scalers = {}
        self.user_profiles = defaultdict(dict)
        self.transaction_history = defaultdict(lambda: deque(maxlen=1000))
        self.location_history = defaultdict(lambda: deque(maxlen=100))
        self.device_history = defaultdict(set)
        self.lock = threading.Lock()
        
        # Risk thresholds
        self.risk_thresholds = {
            FraudRiskLevel.LOW: 0.2,
            FraudRiskLevel.MEDIUM: 0.5,
            FraudRiskLevel.HIGH: 0.8,
            FraudRiskLevel.CRITICAL: 0.95
        }
        
        self._init_database()
        self._load_models()
    
    def _init_database(self):
        """Initialize fraud detection database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    merchant_id TEXT NOT NULL,
                    merchant_category TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    location_lat REAL,
                    location_lon REAL,
                    device_id TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    payment_method TEXT NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    is_fraud INTEGER DEFAULT 0,
                    fraud_probability REAL,
                    risk_level TEXT,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    first_transaction_date TEXT,
                    total_transactions INTEGER DEFAULT 0,
                    total_amount REAL DEFAULT 0.0,
                    avg_amount REAL DEFAULT 0.0,
                    unique_merchants INTEGER DEFAULT 0,
                    unique_devices INTEGER DEFAULT 0,
                    fraud_count INTEGER DEFAULT 0,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fraud_predictions (
                    prediction_id TEXT PRIMARY KEY,
                    transaction_id TEXT NOT NULL,
                    fraud_probability REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    prediction_time_ms REAL NOT NULL,
                    model_version TEXT NOT NULL,
                    features_json TEXT,
                    risk_factors_json TEXT,
                    recommended_action TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id)
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_time ON transactions (user_id, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_fraud ON transactions (is_fraud)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_fraud_predictions_transaction ON fraud_predictions (transaction_id)')
    
    def _load_models(self):
        """Load pre-trained fraud detection models"""
        try:
            # In production, these would be loaded from model registry
            # For demo, we'll create simple models
            self._create_demo_models()
            logger.info("Fraud detection models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self._create_demo_models()
    
    def _create_demo_models(self):
        """Create demo fraud detection models"""
        # Primary fraud detection model
        self.models['primary'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        # Anomaly detection model for unusual patterns
        self.models['anomaly'] = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_jobs=-1
        )
        
        # Feature scalers
        self.feature_scalers['standard'] = StandardScaler()
        
        logger.info("Demo models created")
    
    def _calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        if None in [lat1, lon1, lat2, lon2]:
            return 0.0
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _extract_features(self, transaction: Transaction) -> FraudFeatures:
        """
        Extract comprehensive fraud detection features
        Mumbai me feature engineering ka best practice!
        """
        user_id = transaction.user_id
        current_time = transaction.timestamp
        
        # Get user transaction history
        user_transactions = list(self.transaction_history[user_id])
        
        # Amount features
        user_amounts = [t['amount'] for t in user_transactions] if user_transactions else [transaction.amount]
        amount_mean = np.mean(user_amounts)
        amount_std = np.std(user_amounts) if len(user_amounts) > 1 else 1.0
        
        amount_zscore = (transaction.amount - amount_mean) / amount_std if amount_std > 0 else 0
        amount_percentile = np.percentile(user_amounts, 95) if len(user_amounts) > 5 else transaction.amount
        
        # Velocity features (time-based)
        hour_ago = current_time - timedelta(hours=1)
        day_ago = current_time - timedelta(hours=24)
        
        recent_1h = [t for t in user_transactions if datetime.fromisoformat(t['timestamp']) > hour_ago]
        recent_24h = [t for t in user_transactions if datetime.fromisoformat(t['timestamp']) > day_ago]
        
        transaction_count_1h = len(recent_1h)
        transaction_count_24h = len(recent_24h)
        total_amount_1h = sum(t['amount'] for t in recent_1h)
        total_amount_24h = sum(t['amount'] for t in recent_24h)
        
        # User behavior features
        user_profile = self.user_profiles.get(user_id, {})
        first_transaction = user_profile.get('first_transaction_date')
        
        if first_transaction:
            user_age_days = (current_time - datetime.fromisoformat(first_transaction)).days
        else:
            user_age_days = 0
        
        user_transaction_frequency = len(user_transactions) / max(user_age_days, 1)
        user_avg_amount = user_profile.get('avg_amount', transaction.amount)
        
        # Check if merchant is new for user
        user_merchants = set(t['merchant_id'] for t in user_transactions)
        new_merchant_flag = transaction.merchant_id not in user_merchants
        
        # Location features
        user_locations = list(self.location_history[user_id])
        location_distance_km = 0.0
        location_velocity_kmh = 0.0
        unusual_location_flag = False
        
        if user_locations and transaction.location_lat and transaction.location_lon:
            last_location = user_locations[-1]
            location_distance_km = self._calculate_distance_km(
                last_location['lat'], last_location['lon'],
                transaction.location_lat, transaction.location_lon
            )
            
            # Calculate velocity if we have time difference
            time_diff_hours = (current_time - datetime.fromisoformat(last_location['timestamp'])).total_seconds() / 3600
            if time_diff_hours > 0:
                location_velocity_kmh = location_distance_km / time_diff_hours
            
            # Check if location is unusual (more than 100km from usual locations)
            usual_locations = [(loc['lat'], loc['lon']) for loc in user_locations[-10:]]
            min_distance = min(
                self._calculate_distance_km(transaction.location_lat, transaction.location_lon, lat, lon)
                for lat, lon in usual_locations
            ) if usual_locations else 0
            
            unusual_location_flag = min_distance > 100  # 100km threshold
        
        # Device features
        user_devices = self.device_history[user_id]
        new_device_flag = transaction.device_id not in user_devices
        device_change_flag = len(user_devices) > 1 and new_device_flag
        
        # Time features
        hour_of_day = current_time.hour
        day_of_week = current_time.weekday()
        is_weekend = day_of_week >= 5
        is_night = hour_of_day < 6 or hour_of_day > 22
        
        # Network features (simplified)
        ip_risk_score = self._calculate_ip_risk_score(transaction.ip_address)
        vpn_flag = self._detect_vpn(transaction.ip_address)
        
        return FraudFeatures(
            amount=transaction.amount,
            amount_zscore=amount_zscore,
            amount_percentile=amount_percentile,
            transaction_count_1h=transaction_count_1h,
            transaction_count_24h=transaction_count_24h,
            total_amount_1h=total_amount_1h,
            total_amount_24h=total_amount_24h,
            user_age_days=user_age_days,
            user_transaction_frequency=user_transaction_frequency,
            user_avg_amount=user_avg_amount,
            new_merchant_flag=new_merchant_flag,
            location_distance_km=location_distance_km,
            location_velocity_kmh=location_velocity_kmh,
            unusual_location_flag=unusual_location_flag,
            new_device_flag=new_device_flag,
            device_change_flag=device_change_flag,
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_night=is_night,
            ip_risk_score=ip_risk_score,
            vpn_flag=vpn_flag
        )
    
    def _calculate_ip_risk_score(self, ip_address: str) -> float:
        """Calculate IP address risk score (simplified)"""
        # In production, this would use IP reputation databases
        # For demo, create simple heuristic
        ip_hash = int(hashlib.md5(ip_address.encode()).hexdigest(), 16)
        return (ip_hash % 100) / 100.0
    
    def _detect_vpn(self, ip_address: str) -> bool:
        """Detect VPN usage (simplified)"""
        # In production, use VPN detection services
        # For demo, random detection based on IP hash
        ip_hash = int(hashlib.md5(ip_address.encode()).hexdigest(), 16)
        return (ip_hash % 100) < 5  # 5% VPN rate
    
    def _features_to_array(self, features: FraudFeatures) -> np.ndarray:
        """Convert features to numpy array for model input"""
        feature_vector = np.array([
            features.amount,
            features.amount_zscore,
            features.amount_percentile,
            features.transaction_count_1h,
            features.transaction_count_24h,
            features.total_amount_1h,
            features.total_amount_24h,
            features.user_age_days,
            features.user_transaction_frequency,
            features.user_avg_amount,
            int(features.new_merchant_flag),
            features.location_distance_km,
            features.location_velocity_kmh,
            int(features.unusual_location_flag),
            int(features.new_device_flag),
            int(features.device_change_flag),
            features.hour_of_day,
            features.day_of_week,
            int(features.is_weekend),
            int(features.is_night),
            features.ip_risk_score,
            int(features.vpn_flag)
        ])
        
        return feature_vector.reshape(1, -1)
    
    def predict_fraud(self, transaction: Transaction) -> FraudPrediction:
        """
        Real-time fraud prediction
        Mumbai me real-time fraud detection!
        """
        start_time = time.time()
        
        # Extract features
        features = self._extract_features(transaction)
        feature_array = self._features_to_array(features)
        
        # Get fraud probability from primary model
        # For demo, use rule-based scoring since we don't have trained model
        fraud_score = self._calculate_rule_based_score(features)
        
        # Determine risk level
        risk_level = FraudRiskLevel.LOW
        for level, threshold in sorted(self.risk_thresholds.items(), key=lambda x: x[1]):
            if fraud_score >= threshold:
                risk_level = level
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(features)
        
        # Determine recommended action
        recommended_action = self._get_recommended_action(fraud_score, risk_level)
        
        prediction_time_ms = (time.time() - start_time) * 1000
        
        prediction = FraudPrediction(
            transaction_id=transaction.transaction_id,
            fraud_probability=fraud_score,
            risk_level=risk_level,
            prediction_time_ms=prediction_time_ms,
            model_version="demo_v1.0",
            features_used=asdict(features),
            risk_factors=risk_factors,
            recommended_action=recommended_action
        )
        
        # Store prediction
        self._store_prediction(prediction)
        
        return prediction
    
    def _calculate_rule_based_score(self, features: FraudFeatures) -> float:
        """
        Rule-based fraud scoring for demo
        Mumbai me rule-based fraud detection!
        """
        score = 0.0
        
        # High amount risk
        if features.amount > 50000:
            score += 0.3
        elif features.amount > 10000:
            score += 0.1
        
        # High velocity risk
        if features.transaction_count_1h > 5:
            score += 0.4
        elif features.transaction_count_24h > 20:
            score += 0.2
        
        # Location risk
        if features.location_velocity_kmh > 500:  # Impossible speed
            score += 0.5
        elif features.unusual_location_flag:
            score += 0.2
        
        # Device and behavior risk
        if features.new_device_flag and features.new_merchant_flag:
            score += 0.3
        elif features.new_device_flag:
            score += 0.1
        
        # Time-based risk
        if features.is_night:
            score += 0.1
        
        # Network risk
        if features.vpn_flag:
            score += 0.2
        
        score += features.ip_risk_score * 0.1
        
        # Amount anomaly
        if abs(features.amount_zscore) > 3:
            score += 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _identify_risk_factors(self, features: FraudFeatures) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        if features.amount > 50000:
            risk_factors.append("High transaction amount")
        
        if features.transaction_count_1h > 5:
            risk_factors.append("High transaction velocity")
        
        if features.location_velocity_kmh > 500:
            risk_factors.append("Impossible travel speed")
        
        if features.unusual_location_flag:
            risk_factors.append("Unusual transaction location")
        
        if features.new_device_flag:
            risk_factors.append("New device")
        
        if features.new_merchant_flag:
            risk_factors.append("New merchant")
        
        if features.is_night:
            risk_factors.append("Night time transaction")
        
        if features.vpn_flag:
            risk_factors.append("VPN usage detected")
        
        if abs(features.amount_zscore) > 3:
            risk_factors.append("Amount significantly different from user pattern")
        
        return risk_factors
    
    def _get_recommended_action(self, fraud_score: float, risk_level: FraudRiskLevel) -> TransactionStatus:
        """Determine recommended action based on risk"""
        if risk_level == FraudRiskLevel.CRITICAL:
            return TransactionStatus.BLOCKED
        elif risk_level == FraudRiskLevel.HIGH:
            return TransactionStatus.MANUAL_REVIEW
        elif risk_level == FraudRiskLevel.MEDIUM:
            return TransactionStatus.MANUAL_REVIEW
        else:
            return TransactionStatus.APPROVED
    
    def _store_prediction(self, prediction: FraudPrediction):
        """Store fraud prediction in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO fraud_predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()),
                    prediction.transaction_id,
                    prediction.fraud_probability,
                    prediction.risk_level.value,
                    prediction.prediction_time_ms,
                    prediction.model_version,
                    json.dumps(prediction.features_used, default=str),
                    json.dumps(prediction.risk_factors),
                    prediction.recommended_action.value,
                    datetime.now().isoformat()
                ))
        except Exception as e:
            logger.error(f"Failed to store prediction: {e}")
    
    def update_user_profile(self, transaction: Transaction, is_fraud: bool = False):
        """
        Update user profile with transaction
        Mumbai me user profile ka update!
        """
        with self.lock:
            user_id = transaction.user_id
            
            # Add to transaction history
            transaction_dict = {
                'transaction_id': transaction.transaction_id,
                'amount': transaction.amount,
                'merchant_id': transaction.merchant_id,
                'timestamp': transaction.timestamp.isoformat(),
                'is_fraud': is_fraud
            }
            self.transaction_history[user_id].append(transaction_dict)
            
            # Add to location history
            if transaction.location_lat and transaction.location_lon:
                location_dict = {
                    'lat': transaction.location_lat,
                    'lon': transaction.location_lon,
                    'timestamp': transaction.timestamp.isoformat()
                }
                self.location_history[user_id].append(location_dict)
            
            # Add device
            self.device_history[user_id].add(transaction.device_id)
            
            # Update user profile in database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Get current profile
                    cursor = conn.execute(
                        "SELECT total_transactions, total_amount, fraud_count FROM user_profiles WHERE user_id = ?",
                        (user_id,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        total_transactions, total_amount, fraud_count = row
                        total_transactions += 1
                        total_amount += transaction.amount
                        if is_fraud:
                            fraud_count += 1
                        
                        avg_amount = total_amount / total_transactions
                        
                        conn.execute('''
                            UPDATE user_profiles 
                            SET total_transactions = ?, total_amount = ?, avg_amount = ?, 
                                fraud_count = ?, last_updated = ?
                            WHERE user_id = ?
                        ''', (total_transactions, total_amount, avg_amount, fraud_count, 
                              datetime.now().isoformat(), user_id))
                    else:
                        # Create new profile
                        conn.execute('''
                            INSERT INTO user_profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            user_id, transaction.timestamp.isoformat(), 1, transaction.amount,
                            transaction.amount, 1, 1, 1 if is_fraud else 0, datetime.now().isoformat()
                        ))
            except Exception as e:
                logger.error(f"Failed to update user profile: {e}")
    
    def get_user_risk_profile(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user risk profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM user_profiles WHERE user_id = ?",
                (user_id,)
            )
            profile = cursor.fetchone()
            
            if not profile:
                return {'error': 'User not found'}
            
            # Get recent fraud predictions
            cursor = conn.execute('''
                SELECT fraud_probability, risk_level, created_at 
                FROM fraud_predictions fp
                JOIN transactions t ON fp.transaction_id = t.transaction_id
                WHERE t.user_id = ?
                ORDER BY fp.created_at DESC LIMIT 10
            ''', (user_id,))
            
            recent_predictions = cursor.fetchall()
            
            return {
                'user_id': user_id,
                'total_transactions': profile[2],
                'total_amount': profile[3],
                'avg_amount': profile[4],
                'fraud_count': profile[7],
                'fraud_rate': profile[7] / profile[2] if profile[2] > 0 else 0,
                'recent_predictions': [
                    {'fraud_probability': p[0], 'risk_level': p[1], 'timestamp': p[2]}
                    for p in recent_predictions
                ]
            }

def generate_sample_transactions(n_transactions: int = 1000) -> List[Transaction]:
    """
    Generate sample transactions for testing
    Mumbai me realistic transaction data!
    """
    transactions = []
    users = [f"user_{i:04d}" for i in range(100)]
    merchants = [f"merchant_{i:03d}" for i in range(50)]
    categories = ["grocery", "fuel", "restaurant", "online", "retail", "medical", "entertainment"]
    payment_methods = ["card", "upi", "wallet", "netbanking"]
    
    # Mumbai coordinates (approximate)
    mumbai_lat, mumbai_lon = 19.0760, 72.8777
    
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(n_transactions):
        # Random user and merchant
        user_id = np.random.choice(users)
        merchant_id = np.random.choice(merchants)
        
        # Amount distribution (log-normal)
        amount = max(10, np.random.lognormal(6, 1))  # Mean ~400 INR
        
        # Add some fraud transactions (5% fraud rate)
        is_fraud_sample = np.random.random() < 0.05
        if is_fraud_sample:
            # Fraud transactions tend to be higher amounts, unusual times
            amount *= np.random.uniform(5, 20)  # Much higher amounts
        
        # Random timestamp in last 30 days
        hours_offset = np.random.randint(0, 30 * 24)
        timestamp = base_time + timedelta(hours=hours_offset)
        
        # Location (near Mumbai with some variation)
        lat = mumbai_lat + np.random.normal(0, 0.1)
        lon = mumbai_lon + np.random.normal(0, 0.1)
        
        transaction = Transaction(
            transaction_id=f"txn_{i:06d}",
            user_id=user_id,
            amount=round(amount, 2),
            merchant_id=merchant_id,
            merchant_category=np.random.choice(categories),
            timestamp=timestamp,
            location_lat=lat,
            location_lon=lon,
            device_id=f"device_{hash(user_id) % 20:03d}",
            ip_address=f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
            payment_method=np.random.choice(payment_methods)
        )
        
        transactions.append(transaction)
    
    # Sort by timestamp
    transactions.sort(key=lambda x: x.timestamp)
    
    return transactions

def main():
    """
    Demo Paytm Fraud Detection System
    Mumbai ke fraud detection ka demo!
    """
    print("🛡️  Starting Paytm Fraud Detection Demo")
    print("=" * 50)
    
    # Initialize fraud detector
    detector = PaytmFraudDetector("paytm_fraud_demo.db")
    
    # Generate sample transactions
    print("\n📊 Generating sample transactions...")
    transactions = generate_sample_transactions(500)
    print(f"Generated {len(transactions)} transactions")
    
    # Process transactions and detect fraud
    print("\n🔍 Processing transactions for fraud detection...")
    predictions = []
    fraud_count = 0
    
    for i, transaction in enumerate(transactions):
        # Predict fraud
        prediction = detector.predict_fraud(transaction)
        predictions.append(prediction)
        
        # Update user profile (simulate feedback)
        is_actual_fraud = prediction.fraud_probability > 0.8  # Simulate ground truth
        detector.update_user_profile(transaction, is_actual_fraud)
        
        if prediction.risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL]:
            fraud_count += 1
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1} transactions...")
    
    print(f"\n📈 Processing Results:")
    print(f"  Total Transactions: {len(transactions)}")
    print(f"  High Risk Transactions: {fraud_count}")
    print(f"  Fraud Rate: {fraud_count / len(transactions) * 100:.1f}%")
    
    # Analyze predictions
    risk_distribution = defaultdict(int)
    action_distribution = defaultdict(int)
    avg_prediction_time = 0
    
    for prediction in predictions:
        risk_distribution[prediction.risk_level.value] += 1
        action_distribution[prediction.recommended_action.value] += 1
        avg_prediction_time += prediction.prediction_time_ms
    
    avg_prediction_time /= len(predictions)
    
    print(f"\n📊 Risk Level Distribution:")
    for risk_level, count in risk_distribution.items():
        percentage = count / len(predictions) * 100
        print(f"  {risk_level.upper()}: {count} ({percentage:.1f}%)")
    
    print(f"\n🎯 Recommended Actions:")
    for action, count in action_distribution.items():
        percentage = count / len(predictions) * 100
        print(f"  {action.upper()}: {count} ({percentage:.1f}%)")
    
    print(f"\n⚡ Performance Metrics:")
    print(f"  Average Prediction Time: {avg_prediction_time:.2f}ms")
    print(f"  Throughput: {1000 / avg_prediction_time:.0f} predictions/second")
    
    # Show some high-risk examples
    print(f"\n🚨 High-Risk Transaction Examples:")
    high_risk_predictions = [p for p in predictions if p.risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL]]
    
    for i, prediction in enumerate(high_risk_predictions[:3]):
        print(f"\n  Example {i + 1}:")
        print(f"    Transaction ID: {prediction.transaction_id}")
        print(f"    Fraud Probability: {prediction.fraud_probability:.3f}")
        print(f"    Risk Level: {prediction.risk_level.value}")
        print(f"    Recommended Action: {prediction.recommended_action.value}")
        print(f"    Risk Factors: {', '.join(prediction.risk_factors)}")
    
    # User risk profile example
    print(f"\n👤 Sample User Risk Profile:")
    sample_user = transactions[0].user_id
    risk_profile = detector.get_user_risk_profile(sample_user)
    
    print(f"  User ID: {risk_profile['user_id']}")
    print(f"  Total Transactions: {risk_profile['total_transactions']}")
    print(f"  Average Amount: ₹{risk_profile['avg_amount']:.2f}")
    print(f"  Fraud Rate: {risk_profile['fraud_rate']*100:.1f}%")
    
    print(f"\n✅ Fraud detection demo completed!")
    print("Mumbai me fraud detection bhi police ki tarah alert!")

if __name__ == "__main__":
    main()