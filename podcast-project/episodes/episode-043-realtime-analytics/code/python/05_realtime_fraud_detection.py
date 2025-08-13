#!/usr/bin/env python3
"""
Real-time Fraud Detection System
Episode 43: Real-time Analytics at Scale

Production-grade fraud detection using real-time analytics
Machine learning based anomaly detection with immediate response

Use Case: Paytm/PhonePe real-time fraud detection
UPI transactions में fraud को real-time detect करना
"""

import asyncio
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import hashlib
import logging
import numpy as np
from enum import Enum
import math
import statistics

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class UPITransaction:
    """UPI transaction event"""
    transaction_id: str
    sender_vpa: str
    receiver_vpa: str
    amount: float
    timestamp: datetime
    merchant_category: Optional[str] = None
    device_id: str = ""
    ip_address: str = ""
    location: str = ""
    app_version: str = ""
    network_type: str = "4G"
    transaction_type: str = "P2P"  # P2P, P2M, Bill Payment
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            'transaction_id': self.transaction_id,
            'sender_vpa': self.sender_vpa,
            'receiver_vpa': self.receiver_vpa,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat(),
            'merchant_category': self.merchant_category,
            'device_id': self.device_id,
            'ip_address': self.ip_address,
            'location': self.location,
            'app_version': self.app_version,
            'network_type': self.network_type,
            'transaction_type': self.transaction_type
        }
        return data

@dataclass
class FraudDetectionResult:
    """Fraud detection result"""
    transaction_id: str
    risk_level: RiskLevel
    risk_score: float
    status: TransactionStatus
    detected_patterns: List[str]
    processing_time_ms: float
    rules_triggered: List[str]
    ml_score: Optional[float] = None
    recommendation: str = ""

class UserBehaviorTracker:
    """
    User behavior tracking for fraud detection
    User के normal behavior pattern को track करता है
    """
    
    def __init__(self, history_window_hours: int = 24):
        self.history_window = timedelta(hours=history_window_hours)
        self.user_transactions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.user_patterns: Dict[str, Dict] = defaultdict(dict)
        
    def add_transaction(self, transaction: UPITransaction):
        """Add transaction to user's history"""
        vpa = transaction.sender_vpa
        self.user_transactions[vpa].append(transaction)
        self._update_user_pattern(vpa)
    
    def _update_user_pattern(self, vpa: str):
        """Update user's behavior pattern"""
        transactions = list(self.user_transactions[vpa])
        
        if len(transactions) < 5:  # Need minimum transactions for pattern
            return
        
        # Filter transactions within window
        current_time = datetime.now()
        recent_transactions = [
            txn for txn in transactions 
            if current_time - txn.timestamp <= self.history_window
        ]
        
        if not recent_transactions:
            return
        
        # Calculate behavior patterns
        amounts = [txn.amount for txn in recent_transactions]
        hours = [txn.timestamp.hour for txn in recent_transactions]
        locations = [txn.location for txn in recent_transactions]
        merchants = [txn.merchant_category for txn in recent_transactions if txn.merchant_category]
        
        pattern = {
            'avg_amount': statistics.mean(amounts),
            'std_amount': statistics.stdev(amounts) if len(amounts) > 1 else 0,
            'median_amount': statistics.median(amounts),
            'max_amount': max(amounts),
            'min_amount': min(amounts),
            'preferred_hours': list(set(hours)),
            'common_locations': list(set(locations)),
            'frequent_merchants': list(set(merchants)),
            'transaction_frequency': len(recent_transactions) / 24.0,  # per hour
            'last_updated': current_time.isoformat()
        }
        
        self.user_patterns[vpa] = pattern
    
    def get_user_pattern(self, vpa: str) -> Dict:
        """Get user's behavior pattern"""
        return self.user_patterns.get(vpa, {})
    
    def is_amount_anomaly(self, vpa: str, amount: float) -> Tuple[bool, float]:
        """Check if transaction amount is anomalous for user"""
        pattern = self.get_user_pattern(vpa)
        
        if not pattern or 'std_amount' not in pattern:
            return False, 0.0
        
        avg_amount = pattern['avg_amount']
        std_amount = pattern['std_amount']
        
        if std_amount == 0:
            # User always transacts same amount
            anomaly_score = abs(amount - avg_amount) / max(avg_amount, 1.0)
            return anomaly_score > 0.5, anomaly_score
        
        # Z-score based anomaly detection
        z_score = abs(amount - avg_amount) / std_amount
        is_anomaly = z_score > 3.0  # 3 standard deviations
        
        return is_anomaly, z_score
    
    def is_time_anomaly(self, vpa: str, timestamp: datetime) -> Tuple[bool, str]:
        """Check if transaction time is anomalous for user"""
        pattern = self.get_user_pattern(vpa)
        
        if not pattern or 'preferred_hours' not in pattern:
            return False, ""
        
        hour = timestamp.hour
        preferred_hours = pattern['preferred_hours']
        
        # Check if current hour is significantly different from usual pattern
        if len(preferred_hours) < 3:
            return False, ""
        
        hour_distribution = defaultdict(int)
        for h in preferred_hours:
            hour_distribution[h] += 1
        
        # If user never transacts at this hour and it's unusual time (2-6 AM)
        if hour not in preferred_hours and 2 <= hour <= 6:
            return True, f"असामान्य समय: {hour}:00 बजे (सामान्यतः {preferred_hours} बजे)"
        
        return False, ""
    
    def is_location_anomaly(self, vpa: str, location: str) -> Tuple[bool, str]:
        """Check if transaction location is anomalous"""
        pattern = self.get_user_pattern(vpa)
        
        if not pattern or 'common_locations' not in pattern:
            return False, ""
        
        common_locations = pattern['common_locations']
        
        if len(common_locations) < 2:
            return False, ""
        
        # Simple location anomaly - if completely new location
        if location not in common_locations:
            return True, f"नई location: {location} (सामान्यतः {common_locations})"
        
        return False, ""

class VelocityTracker:
    """
    Transaction velocity tracking
    Fast successive transactions detect करता है
    """
    
    def __init__(self):
        self.transaction_windows = {
            'minute': defaultdict(list),
            'hour': defaultdict(list),
            'day': defaultdict(list)
        }
        
        # Velocity limits
        self.limits = {
            'minute': {'count': 5, 'amount': 50000},
            'hour': {'count': 50, 'amount': 200000},
            'day': {'count': 200, 'amount': 500000}
        }
    
    def add_transaction(self, transaction: UPITransaction):
        """Add transaction to velocity tracking"""
        vpa = transaction.sender_vpa
        current_time = transaction.timestamp
        
        # Add to all windows
        self.transaction_windows['minute'][vpa].append((current_time, transaction.amount))
        self.transaction_windows['hour'][vpa].append((current_time, transaction.amount))
        self.transaction_windows['day'][vpa].append((current_time, transaction.amount))
        
        # Clean old transactions
        self._clean_old_transactions(vpa, current_time)
    
    def _clean_old_transactions(self, vpa: str, current_time: datetime):
        """Remove old transactions from windows"""
        windows = {
            'minute': timedelta(minutes=1),
            'hour': timedelta(hours=1),
            'day': timedelta(days=1)
        }
        
        for window_name, window_size in windows.items():
            cutoff_time = current_time - window_size
            
            self.transaction_windows[window_name][vpa] = [
                (ts, amount) for ts, amount in self.transaction_windows[window_name][vpa]
                if ts >= cutoff_time
            ]
    
    def check_velocity_violation(self, vpa: str) -> List[str]:
        """Check for velocity violations"""
        violations = []
        
        for window_name, limits in self.limits.items():
            transactions = self.transaction_windows[window_name][vpa]
            
            if not transactions:
                continue
            
            count = len(transactions)
            total_amount = sum(amount for _, amount in transactions)
            
            if count > limits['count']:
                violations.append(f"{window_name} में {count} transactions (limit: {limits['count']})")
            
            if total_amount > limits['amount']:
                violations.append(f"{window_name} में ₹{total_amount:,.0f} (limit: ₹{limits['amount']:,.0f})")
        
        return violations

class DeviceTracker:
    """
    Device-based fraud detection
    Multiple devices से same user की activity track करता है
    """
    
    def __init__(self):
        self.user_devices: Dict[str, set] = defaultdict(set)
        self.device_locations: Dict[str, List] = defaultdict(list)
        self.device_first_seen: Dict[str, datetime] = {}
    
    def add_transaction(self, transaction: UPITransaction):
        """Track device usage"""
        vpa = transaction.sender_vpa
        device_id = transaction.device_id
        location = transaction.location
        timestamp = transaction.timestamp
        
        # Track user's devices
        self.user_devices[vpa].add(device_id)
        
        # Track device locations
        self.device_locations[device_id].append((location, timestamp))
        
        # Track first seen time for new devices
        if device_id not in self.device_first_seen:
            self.device_first_seen[device_id] = timestamp
    
    def check_device_anomalies(self, transaction: UPITransaction) -> List[str]:
        """Check for device-based anomalies"""
        anomalies = []
        vpa = transaction.sender_vpa
        device_id = transaction.device_id
        location = transaction.location
        timestamp = transaction.timestamp
        
        # Multiple devices for same user
        user_device_count = len(self.user_devices[vpa])
        if user_device_count > 3:
            anomalies.append(f"Multiple devices: {user_device_count} devices का use")
        
        # New device
        if device_id in self.device_first_seen:
            first_seen = self.device_first_seen[device_id]
            if timestamp - first_seen < timedelta(hours=1):
                anomalies.append(f"नया device: {device_id} (पहली बार {first_seen.strftime('%H:%M')} बजे देखा गया)")
        
        # Device location inconsistency
        device_locations = self.device_locations[device_id]
        if len(device_locations) > 1:
            recent_locations = [loc for loc, ts in device_locations 
                              if timestamp - ts <= timedelta(hours=2)]
            unique_locations = set(recent_locations)
            
            if len(unique_locations) > 2:
                anomalies.append(f"Device location jump: {list(unique_locations)}")
        
        return anomalies

class MLAnomalyDetector:
    """
    Machine Learning based anomaly detection
    Simplified ML model for fraud detection
    """
    
    def __init__(self):
        # Feature weights (learned from historical data)
        self.feature_weights = {
            'amount_zscore': 0.25,
            'time_anomaly': 0.15,
            'location_anomaly': 0.20,
            'velocity_violation': 0.30,
            'device_anomaly': 0.10
        }
        
        # Historical statistics (normally loaded from training data)
        self.global_stats = {
            'avg_amount': 2500.0,
            'std_amount': 5000.0,
            'common_hours': list(range(8, 22)),  # 8 AM to 10 PM
            'high_risk_amounts': [100000, 200000, 500000]
        }
    
    def calculate_ml_score(self, transaction: UPITransaction, 
                          user_behavior: UserBehaviorTracker,
                          velocity_tracker: VelocityTracker,
                          device_tracker: DeviceTracker) -> float:
        """Calculate ML-based risk score"""
        
        features = self._extract_features(transaction, user_behavior, 
                                        velocity_tracker, device_tracker)
        
        # Weighted sum of feature scores
        ml_score = 0.0
        for feature_name, weight in self.feature_weights.items():
            feature_score = features.get(feature_name, 0.0)
            ml_score += feature_score * weight
        
        # Normalize to 0-1 range
        ml_score = max(0.0, min(1.0, ml_score))
        
        return ml_score
    
    def _extract_features(self, transaction: UPITransaction,
                         user_behavior: UserBehaviorTracker,
                         velocity_tracker: VelocityTracker,
                         device_tracker: DeviceTracker) -> Dict[str, float]:
        """Extract features for ML model"""
        
        features = {}
        
        # Amount-based features
        is_amount_anomaly, amount_score = user_behavior.is_amount_anomaly(
            transaction.sender_vpa, transaction.amount
        )
        features['amount_zscore'] = min(amount_score / 5.0, 1.0)  # Normalize
        
        # Time-based features
        is_time_anomaly, _ = user_behavior.is_time_anomaly(
            transaction.sender_vpa, transaction.timestamp
        )
        features['time_anomaly'] = 1.0 if is_time_anomaly else 0.0
        
        # Location-based features
        is_location_anomaly, _ = user_behavior.is_location_anomaly(
            transaction.sender_vpa, transaction.location
        )
        features['location_anomaly'] = 1.0 if is_location_anomaly else 0.0
        
        # Velocity features
        velocity_violations = velocity_tracker.check_velocity_violation(transaction.sender_vpa)
        features['velocity_violation'] = min(len(velocity_violations) / 3.0, 1.0)
        
        # Device features
        device_anomalies = device_tracker.check_device_anomalies(transaction)
        features['device_anomaly'] = min(len(device_anomalies) / 2.0, 1.0)
        
        return features

class RuleEngine:
    """
    Business rules for fraud detection
    Predefined rules for immediate fraud detection
    """
    
    def __init__(self):
        # High-risk patterns
        self.high_risk_amounts = [99999, 100000, 200000, 500000]  # Round numbers
        self.suspicious_merchants = ["online_gaming", "crypto", "unknown"]
        self.blacklisted_ips = set()
        self.blacklisted_devices = set()
        
        # Time-based rules
        self.high_risk_hours = list(range(2, 6))  # 2 AM to 6 AM
        
    def evaluate_transaction(self, transaction: UPITransaction) -> Tuple[List[str], RiskLevel]:
        """Evaluate transaction against business rules"""
        
        triggered_rules = []
        risk_level = RiskLevel.LOW
        
        # Amount-based rules
        if transaction.amount >= 100000:
            triggered_rules.append("High amount transaction (₹1L+)")
            risk_level = RiskLevel.HIGH
        elif transaction.amount in self.high_risk_amounts:
            triggered_rules.append("Suspicious round amount")
            risk_level = RiskLevel.MEDIUM
        
        # Time-based rules
        if transaction.timestamp.hour in self.high_risk_hours:
            triggered_rules.append("Late night transaction")
            if risk_level == RiskLevel.LOW:
                risk_level = RiskLevel.MEDIUM
        
        # Merchant-based rules
        if transaction.merchant_category in self.suspicious_merchants:
            triggered_rules.append(f"Suspicious merchant: {transaction.merchant_category}")
            risk_level = RiskLevel.HIGH
        
        # Device/IP rules
        if transaction.device_id in self.blacklisted_devices:
            triggered_rules.append("Blacklisted device")
            risk_level = RiskLevel.CRITICAL
        
        if transaction.ip_address in self.blacklisted_ips:
            triggered_rules.append("Blacklisted IP address")
            risk_level = RiskLevel.CRITICAL
        
        # VPA patterns
        if self._is_suspicious_vpa_pattern(transaction.receiver_vpa):
            triggered_rules.append("Suspicious receiver VPA pattern")
            if risk_level == RiskLevel.LOW:
                risk_level = RiskLevel.MEDIUM
        
        return triggered_rules, risk_level
    
    def _is_suspicious_vpa_pattern(self, vpa: str) -> bool:
        """Check for suspicious VPA patterns"""
        # Random number patterns
        if len([c for c in vpa if c.isdigit()]) > 8:
            return True
        
        # Repeated characters
        if any(vpa.count(char) > 4 for char in set(vpa)):
            return True
        
        return False

class PaytmFraudDetectionEngine:
    """
    Complete fraud detection engine for Paytm/UPI transactions
    Real-time fraud detection with immediate response
    """
    
    def __init__(self):
        self.user_behavior = UserBehaviorTracker()
        self.velocity_tracker = VelocityTracker()
        self.device_tracker = DeviceTracker()
        self.ml_detector = MLAnomalyDetector()
        self.rule_engine = RuleEngine()
        
        # Processing metrics
        self.metrics = {
            'total_transactions': 0,
            'fraud_detected': 0,
            'false_positives': 0,
            'processing_times': deque(maxlen=1000)
        }
        
        # Fraud detection thresholds
        self.thresholds = {
            RiskLevel.LOW: 0.3,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.7,
            RiskLevel.CRITICAL: 0.9
        }
    
    def process_transaction(self, transaction: UPITransaction) -> FraudDetectionResult:
        """
        Process transaction for fraud detection
        Real-time में fraud check करके immediate response देता है
        """
        
        start_time = time.time()
        
        # Update trackers
        self.user_behavior.add_transaction(transaction)
        self.velocity_tracker.add_transaction(transaction)
        self.device_tracker.add_transaction(transaction)
        
        # Rule-based detection
        triggered_rules, rule_risk_level = self.rule_engine.evaluate_transaction(transaction)
        
        # ML-based detection
        ml_score = self.ml_detector.calculate_ml_score(
            transaction, self.user_behavior, 
            self.velocity_tracker, self.device_tracker
        )
        
        # Collect all detected patterns
        detected_patterns = []
        
        # User behavior anomalies
        is_amount_anomaly, amount_score = self.user_behavior.is_amount_anomaly(
            transaction.sender_vpa, transaction.amount
        )
        if is_amount_anomaly:
            detected_patterns.append(f"Amount anomaly (Z-score: {amount_score:.2f})")
        
        is_time_anomaly, time_msg = self.user_behavior.is_time_anomaly(
            transaction.sender_vpa, transaction.timestamp
        )
        if is_time_anomaly:
            detected_patterns.append(time_msg)
        
        is_location_anomaly, location_msg = self.user_behavior.is_location_anomaly(
            transaction.sender_vpa, transaction.location
        )
        if is_location_anomaly:
            detected_patterns.append(location_msg)
        
        # Velocity violations
        velocity_violations = self.velocity_tracker.check_velocity_violation(transaction.sender_vpa)
        detected_patterns.extend(velocity_violations)
        
        # Device anomalies
        device_anomalies = self.device_tracker.check_device_anomalies(transaction)
        detected_patterns.extend(device_anomalies)
        
        # Determine final risk level and status
        combined_risk_score = self._calculate_combined_risk_score(
            rule_risk_level, ml_score, len(detected_patterns)
        )
        
        final_risk_level, status = self._determine_final_decision(
            combined_risk_score, rule_risk_level
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            final_risk_level, detected_patterns, triggered_rules
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # milliseconds
        self.metrics['processing_times'].append(processing_time)
        
        # Update metrics
        self.metrics['total_transactions'] += 1
        if status in [TransactionStatus.DECLINED, TransactionStatus.FLAGGED]:
            self.metrics['fraud_detected'] += 1
        
        return FraudDetectionResult(
            transaction_id=transaction.transaction_id,
            risk_level=final_risk_level,
            risk_score=combined_risk_score,
            status=status,
            detected_patterns=detected_patterns,
            processing_time_ms=processing_time,
            rules_triggered=triggered_rules,
            ml_score=ml_score,
            recommendation=recommendation
        )
    
    def _calculate_combined_risk_score(self, rule_risk_level: RiskLevel, 
                                     ml_score: float, pattern_count: int) -> float:
        """Calculate combined risk score from multiple sources"""
        
        # Rule-based score
        rule_score_map = {
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 1.0
        }
        rule_score = rule_score_map[rule_risk_level]
        
        # Pattern-based score
        pattern_score = min(pattern_count * 0.2, 1.0)
        
        # Weighted combination
        combined_score = (rule_score * 0.4) + (ml_score * 0.4) + (pattern_score * 0.2)
        
        return min(combined_score, 1.0)
    
    def _determine_final_decision(self, risk_score: float, 
                                rule_risk_level: RiskLevel) -> Tuple[RiskLevel, TransactionStatus]:
        """Determine final risk level and transaction status"""
        
        # Critical rules always trigger immediate action
        if rule_risk_level == RiskLevel.CRITICAL:
            return RiskLevel.CRITICAL, TransactionStatus.DECLINED
        
        # Risk score based decision
        if risk_score >= 0.9:
            return RiskLevel.CRITICAL, TransactionStatus.DECLINED
        elif risk_score >= 0.7:
            return RiskLevel.HIGH, TransactionStatus.FLAGGED
        elif risk_score >= 0.5:
            return RiskLevel.MEDIUM, TransactionStatus.UNDER_REVIEW
        elif risk_score >= 0.3:
            return RiskLevel.LOW, TransactionStatus.APPROVED
        else:
            return RiskLevel.LOW, TransactionStatus.APPROVED
    
    def _generate_recommendation(self, risk_level: RiskLevel, 
                               patterns: List[str], rules: List[str]) -> str:
        """Generate recommendation for the transaction"""
        
        if risk_level == RiskLevel.CRITICAL:
            return "तुरंत decline करें और user को block करें"
        elif risk_level == RiskLevel.HIGH:
            return "Manual review के लिए flag करें, OTP verification करें"
        elif risk_level == RiskLevel.MEDIUM:
            return "Additional verification करें (SMS OTP + PIN)"
        else:
            return "Safe transaction - proceed normally"
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time fraud detection metrics"""
        
        if self.metrics['processing_times']:
            avg_processing_time = statistics.mean(self.metrics['processing_times'])
            p95_processing_time = sorted(self.metrics['processing_times'])[int(0.95 * len(self.metrics['processing_times']))]
        else:
            avg_processing_time = 0
            p95_processing_time = 0
        
        fraud_rate = (self.metrics['fraud_detected'] / max(self.metrics['total_transactions'], 1)) * 100
        
        return {
            'total_transactions': self.metrics['total_transactions'],
            'fraud_detected': self.metrics['fraud_detected'],
            'fraud_rate_percent': fraud_rate,
            'avg_processing_time_ms': avg_processing_time,
            'p95_processing_time_ms': p95_processing_time,
            'unique_users': len(self.user_behavior.user_patterns),
            'active_devices': len(self.device_tracker.device_first_seen),
            'timestamp': datetime.now().isoformat()
        }

def generate_sample_transactions(num_transactions: int = 1000) -> List[UPITransaction]:
    """Generate sample UPI transactions for testing"""
    import random
    
    # Sample data
    vpas = [f"user{i:03d}@paytm" for i in range(1, 101)]
    merchants = [f"merchant{i:03d}@paytm" for i in range(1, 51)]
    locations = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad"]
    merchant_categories = ["grocery", "restaurant", "fuel", "retail", "online", "pharmacy"]
    
    transactions = []
    base_time = datetime.now() - timedelta(hours=48)
    
    # Create realistic transaction patterns
    for i in range(num_transactions):
        sender = random.choice(vpas)
        
        # 80% P2M (Person to Merchant), 20% P2P
        if random.random() < 0.8:
            receiver = random.choice(merchants)
            transaction_type = "P2M"
            merchant_category = random.choice(merchant_categories)
        else:
            receiver = random.choice([vpa for vpa in vpas if vpa != sender])
            transaction_type = "P2P"
            merchant_category = None
        
        # Realistic amount distribution
        if random.random() < 0.6:
            amount = random.uniform(50, 2000)  # Regular transactions
        elif random.random() < 0.9:
            amount = random.uniform(2000, 10000)  # Medium transactions
        else:
            amount = random.uniform(10000, 100000)  # Large transactions
        
        # Add some fraud patterns
        is_fraud = random.random() < 0.05  # 5% fraud rate
        
        if is_fraud:
            # Create suspicious patterns
            if random.random() < 0.3:
                amount = random.choice([99999, 100000, 200000])  # Round amounts
            if random.random() < 0.3:
                timestamp = base_time + timedelta(
                    hours=random.randint(2, 5),  # Late night
                    minutes=random.randint(0, 59)
                )
            else:
                timestamp = base_time + timedelta(minutes=i * 2 + random.randint(0, 30))
        else:
            # Normal transaction time
            timestamp = base_time + timedelta(minutes=i * 2 + random.randint(0, 120))
        
        transaction = UPITransaction(
            transaction_id=f"TXN{i:06d}",
            sender_vpa=sender,
            receiver_vpa=receiver,
            amount=round(amount, 2),
            timestamp=timestamp,
            merchant_category=merchant_category,
            device_id=f"device_{hash(sender) % 20:03d}",
            ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            location=random.choice(locations),
            app_version=f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
            network_type=random.choice(["4G", "WiFi", "3G"]),
            transaction_type=transaction_type
        )
        
        transactions.append(transaction)
    
    return sorted(transactions, key=lambda x: x.timestamp)

def run_fraud_detection_demo():
    """Run fraud detection demo"""
    
    logger.info("Starting Paytm Fraud Detection Demo...")
    
    # Initialize fraud detection engine
    fraud_engine = PaytmFraudDetectionEngine()
    
    # Generate sample transactions
    transactions = generate_sample_transactions(500)
    
    # Process transactions
    fraud_results = []
    flagged_transactions = []
    
    for i, transaction in enumerate(transactions):
        result = fraud_engine.process_transaction(transaction)
        fraud_results.append(result)
        
        # Log significant findings
        if result.status in [TransactionStatus.DECLINED, TransactionStatus.FLAGGED]:
            flagged_transactions.append((transaction, result))
            
            logger.warning(f"FRAUD ALERT - {transaction.transaction_id}: "
                         f"{result.status.value} (Risk: {result.risk_level.value}, "
                         f"Score: {result.risk_score:.3f})")
        
        # Print metrics every 100 transactions
        if (i + 1) % 100 == 0:
            metrics = fraud_engine.get_real_time_metrics()
            print(f"\n=== Fraud Detection Metrics (after {i+1} transactions) ===")
            print(f"Total Transactions: {metrics['total_transactions']:,}")
            print(f"Fraud Detected: {metrics['fraud_detected']}")
            print(f"Fraud Rate: {metrics['fraud_rate_percent']:.2f}%")
            print(f"Avg Processing Time: {metrics['avg_processing_time_ms']:.2f}ms")
            print(f"P95 Processing Time: {metrics['p95_processing_time_ms']:.2f}ms")
    
    # Final report
    print(f"\n=== Final Fraud Detection Report ===")
    
    final_metrics = fraud_engine.get_real_time_metrics()
    print(f"Total Transactions Processed: {final_metrics['total_transactions']:,}")
    print(f"Fraud Cases Detected: {final_metrics['fraud_detected']}")
    print(f"Overall Fraud Rate: {final_metrics['fraud_rate_percent']:.2f}%")
    print(f"Unique Users: {final_metrics['unique_users']}")
    print(f"Active Devices: {final_metrics['active_devices']}")
    
    # Risk level distribution
    risk_distribution = defaultdict(int)
    status_distribution = defaultdict(int)
    
    for result in fraud_results:
        risk_distribution[result.risk_level.value] += 1
        status_distribution[result.status.value] += 1
    
    print(f"\n=== Risk Level Distribution ===")
    for risk_level, count in sorted(risk_distribution.items()):
        percentage = (count / len(fraud_results)) * 100
        print(f"{risk_level}: {count} ({percentage:.1f}%)")
    
    print(f"\n=== Transaction Status Distribution ===")
    for status, count in sorted(status_distribution.items()):
        percentage = (count / len(fraud_results)) * 100
        print(f"{status}: {count} ({percentage:.1f}%)")
    
    # Sample fraud cases
    print(f"\n=== Sample Fraud Cases Detected ===")
    for i, (transaction, result) in enumerate(flagged_transactions[:5]):
        print(f"\n{i+1}. Transaction ID: {transaction.transaction_id}")
        print(f"   Amount: ₹{transaction.amount:,.2f}")
        print(f"   From: {transaction.sender_vpa} → {transaction.receiver_vpa}")
        print(f"   Risk Score: {result.risk_score:.3f} ({result.risk_level.value})")
        print(f"   Status: {result.status.value}")
        print(f"   Detected Patterns: {', '.join(result.detected_patterns[:3])}")
        print(f"   Recommendation: {result.recommendation}")

if __name__ == "__main__":
    run_fraud_detection_demo()