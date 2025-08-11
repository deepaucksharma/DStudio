"""
UPI Fraud Detection using Graph Patterns
Indian payment system mein fraud detection algorithms

Author: Episode 10 - Graph Analytics at Scale
Context: UPI, PhonePe, GPay scale fraud detection patterns
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter, deque
import logging
import time
import json
from datetime import datetime, timedelta
import random
from dataclasses import dataclass
from enum import Enum
import math
import itertools

# Hindi mein logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FraudType(Enum):
    """Types of UPI fraud patterns"""
    CIRCULAR_TRANSFER = "circular_transfer"      # Money laundering rings
    RAPID_SUCCESSION = "rapid_succession"       # Bot-like behavior
    AMOUNT_STRUCTURING = "amount_structuring"   # Avoiding limits
    FAKE_MERCHANT = "fake_merchant"             # Fake business accounts
    ACCOUNT_TAKEOVER = "account_takeover"       # Compromised accounts
    MULE_NETWORK = "mule_network"              # Money mule operations
    SMURFING = "smurfing"                      # Breaking large amounts

class RiskLevel(Enum):
    """Risk levels for transactions/accounts"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FraudAlert:
    """Fraud detection alert"""
    alert_id: str
    fraud_type: FraudType
    risk_level: RiskLevel
    accounts_involved: List[str]
    transaction_ids: List[str]
    pattern_score: float
    description: str
    timestamp: datetime
    evidence: Dict

class UPIFraudDetectionSystem:
    """
    UPI Fraud Detection System using Graph Analytics
    
    Scale:
    - 100 crore+ UPI transactions monthly
    - 50 crore+ active users
    - Real-time fraud detection (< 100ms)
    - 99.9%+ accuracy required
    """
    
    def __init__(self):
        self.transaction_graph = nx.DiGraph()  # Directed for money flow
        self.account_profiles = {}
        self.transaction_history = {}
        self.fraud_alerts = []
        self.detection_rules = {}
        
        # Indian UPI ecosystem
        self.upi_apps = {
            'phonepe': {'market_share': 0.47, 'typical_limits': 100000},
            'googlepay': {'market_share': 0.34, 'typical_limits': 100000}, 
            'paytm': {'market_share': 0.14, 'typical_limits': 100000},
            'amazonpay': {'market_share': 0.02, 'typical_limits': 50000},
            'mobikwik': {'market_share': 0.01, 'typical_limits': 25000},
            'freecharge': {'market_share': 0.01, 'typical_limits': 25000},
            'other': {'market_share': 0.01, 'typical_limits': 10000}
        }
        
        # Indian banks for UPI
        self.indian_banks = [
            'sbi', 'hdfc', 'icici', 'axis', 'kotak', 'pnb', 'bob', 'canara',
            'union', 'indianbank', 'uco', 'central', 'syndicate', 'allahabad'
        ]
        
        # Fraud detection thresholds
        self.detection_thresholds = {
            'rapid_transactions': {'count': 10, 'window_minutes': 5},
            'circular_amount': {'min_amount': 50000, 'participants': 3},
            'structuring_pattern': {'transactions': 5, 'amount_range': (9000, 9999)},
            'velocity_limit': {'daily_limit': 1000000, 'hourly_limit': 200000},
            'network_density': {'edges_per_node': 50}
        }
        
        # Initialize detection rules
        self._initialize_fraud_detection_rules()
        
        logger.info("UPI Fraud Detection System initialized!")
    
    def _initialize_fraud_detection_rules(self):
        """Initialize fraud detection rules"""
        self.detection_rules = {
            FraudType.CIRCULAR_TRANSFER: self._detect_circular_transfer_patterns,
            FraudType.RAPID_SUCCESSION: self._detect_rapid_succession_fraud,
            FraudType.AMOUNT_STRUCTURING: self._detect_amount_structuring,
            FraudType.FAKE_MERCHANT: self._detect_fake_merchant_patterns,
            FraudType.ACCOUNT_TAKEOVER: self._detect_account_takeover,
            FraudType.MULE_NETWORK: self._detect_mule_networks,
            FraudType.SMURFING: self._detect_smurfing_patterns
        }
    
    def generate_upi_transaction_data(self, num_accounts: int = 10000, 
                                    num_transactions: int = 100000,
                                    fraud_percentage: float = 0.05):
        """
        Realistic UPI transaction data generate karta hai with fraud patterns
        """
        logger.info(f"Generating UPI transaction data: {num_accounts:,} accounts, "
                   f"{num_transactions:,} transactions, {fraud_percentage*100}% fraud")
        
        # Generate account profiles
        self._generate_account_profiles(num_accounts)
        
        # Generate legitimate transactions (95%)
        legitimate_transactions = int(num_transactions * (1 - fraud_percentage))
        self._generate_legitimate_transactions(legitimate_transactions)
        
        # Generate fraudulent transactions (5%)
        fraud_transactions = num_transactions - legitimate_transactions
        self._inject_fraud_patterns(fraud_transactions)
        
        logger.info(f"UPI data generated: {self.transaction_graph.number_of_nodes():,} accounts, "
                   f"{self.transaction_graph.number_of_edges():,} transactions")
    
    def _generate_account_profiles(self, num_accounts: int):
        """UPI account profiles generate karta hai"""
        for i in range(num_accounts):
            account_id = f"upi_{i:08d}"
            
            # Account demographics
            account_type = random.choices(
                ['individual', 'merchant', 'business'],
                weights=[85, 10, 5]  # Individual accounts majority
            )[0]
            
            # UPI app preference
            upi_app = random.choices(
                list(self.upi_apps.keys()),
                weights=[app['market_share'] for app in self.upi_apps.values()]
            )[0]
            
            # Bank selection
            bank = random.choice(self.indian_banks)
            
            # Account characteristics
            if account_type == 'individual':
                monthly_volume = random.lognormal(8, 1.5)  # Log-normal distribution
                monthly_volume = max(1000, min(500000, monthly_volume))  # 1K to 5L
                daily_txn_limit = min(100000, monthly_volume / 10)
            elif account_type == 'merchant':
                monthly_volume = random.lognormal(10, 1.8)
                monthly_volume = max(50000, min(5000000, monthly_volume))  # 50K to 50L
                daily_txn_limit = min(1000000, monthly_volume / 5)
            else:  # business
                monthly_volume = random.lognormal(12, 2.0)
                monthly_volume = max(100000, min(10000000, monthly_volume))  # 1L to 1Cr
                daily_txn_limit = min(2000000, monthly_volume / 3)
            
            # Risk factors
            kyc_status = random.choices(['full', 'minimal', 'none'], weights=[80, 15, 5])[0]
            account_age_days = random.randint(1, 2000)  # 1 day to 5+ years
            
            # Behavioral patterns
            typical_transaction_time = random.choice(['morning', 'afternoon', 'evening', 'night'])
            transaction_frequency = random.choice(['low', 'medium', 'high'])
            
            account_profile = {
                'account_type': account_type,
                'upi_app': upi_app,
                'bank': bank,
                'monthly_volume': monthly_volume,
                'daily_txn_limit': daily_txn_limit,
                'kyc_status': kyc_status,
                'account_age_days': account_age_days,
                'typical_time': typical_transaction_time,
                'frequency': transaction_frequency,
                'city': random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad']),
                'risk_score': 0.0,  # Will be calculated
                'is_flagged': False
            }
            
            self.account_profiles[account_id] = account_profile
            self.transaction_graph.add_node(account_id, **account_profile)
    
    def _generate_legitimate_transactions(self, num_transactions: int):
        """Legitimate UPI transactions generate karta hai"""
        logger.info("Generating legitimate transactions...")
        
        accounts = list(self.account_profiles.keys())
        
        for i in range(num_transactions):
            # Select sender and receiver
            sender = random.choice(accounts)
            receiver = random.choice([acc for acc in accounts if acc != sender])
            
            sender_profile = self.account_profiles[sender]
            receiver_profile = self.account_profiles[receiver]
            
            # Generate realistic transaction amount
            amount = self._generate_realistic_amount(sender_profile, receiver_profile)
            
            # Transaction timing
            base_time = datetime.now() - timedelta(days=random.randint(0, 30))
            transaction_time = self._adjust_time_for_behavior(base_time, sender_profile['typical_time'])
            
            # Transaction metadata
            transaction_id = f"txn_{i:012d}"
            transaction_type = random.choices(
                ['p2p', 'p2m', 'm2p', 'bill_payment', 'recharge'],
                weights=[50, 25, 10, 10, 5]
            )[0]
            
            # Success rate based on factors
            success_probability = self._calculate_success_probability(sender_profile, amount)
            is_successful = random.random() < success_probability
            
            # Add transaction edge
            self.transaction_graph.add_edge(
                sender, receiver,
                transaction_id=transaction_id,
                amount=amount,
                timestamp=transaction_time,
                transaction_type=transaction_type,
                is_successful=is_successful,
                is_fraudulent=False,
                fraud_score=0.0
            )
            
            # Track in history
            if sender not in self.transaction_history:
                self.transaction_history[sender] = []
            
            self.transaction_history[sender].append({
                'transaction_id': transaction_id,
                'receiver': receiver,
                'amount': amount,
                'timestamp': transaction_time,
                'type': transaction_type,
                'successful': is_successful,
                'fraudulent': False
            })
    
    def _generate_realistic_amount(self, sender_profile: Dict, receiver_profile: Dict) -> float:
        """Realistic transaction amount generate karta hai"""
        sender_type = sender_profile['account_type']
        receiver_type = receiver_profile['account_type']
        
        # Amount ranges based on account types
        if sender_type == 'individual' and receiver_type == 'individual':
            # P2P transactions: typically small amounts
            base_amount = random.lognormal(6, 1.2)  # Mean around ₹400
            amount = max(10, min(50000, base_amount))
        
        elif sender_type == 'individual' and receiver_type == 'merchant':
            # P2M transactions: shopping, food, services
            base_amount = random.lognormal(6.5, 1.5)  # Mean around ₹700
            amount = max(50, min(25000, base_amount))
        
        elif sender_type == 'merchant' and receiver_type == 'individual':
            # M2P transactions: refunds, cashbacks
            base_amount = random.lognormal(5.5, 1.0)  # Mean around ₹250
            amount = max(10, min(10000, base_amount))
        
        else:  # Business transactions
            base_amount = random.lognormal(8, 2.0)  # Mean around ₹3000
            amount = max(500, min(500000, base_amount))
        
        # Round to practical values
        if amount < 100:
            amount = round(amount, 0)  # Whole rupees
        else:
            amount = round(amount, -1)  # Round to 10s
        
        return amount
    
    def _adjust_time_for_behavior(self, base_time: datetime, typical_time: str) -> datetime:
        """User behavior ke according time adjust karta hai"""
        time_ranges = {
            'morning': (6, 11),
            'afternoon': (11, 17),
            'evening': (17, 22),
            'night': (22, 6)
        }
        
        start_hour, end_hour = time_ranges[typical_time]
        
        if end_hour < start_hour:  # Night time crosses midnight
            hour = random.choice(list(range(start_hour, 24)) + list(range(0, end_hour)))
        else:
            hour = random.randint(start_hour, end_hour)
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        return base_time.replace(hour=hour, minute=minute, second=second)
    
    def _calculate_success_probability(self, sender_profile: Dict, amount: float) -> float:
        """Transaction success probability calculate karta hai"""
        base_probability = 0.98  # 98% success rate baseline
        
        # Reduce for high amounts
        if amount > sender_profile['daily_txn_limit']:
            base_probability *= 0.7
        
        # Reduce for non-KYC accounts
        if sender_profile['kyc_status'] == 'minimal':
            base_probability *= 0.95
        elif sender_profile['kyc_status'] == 'none':
            base_probability *= 0.90
        
        # Reduce for new accounts
        if sender_profile['account_age_days'] < 30:
            base_probability *= 0.92
        
        return base_probability
    
    def _inject_fraud_patterns(self, num_fraud_transactions: int):
        """Fraudulent patterns inject karta hai"""
        logger.info(f"Injecting {num_fraud_transactions} fraudulent transactions...")
        
        fraud_distribution = {
            FraudType.CIRCULAR_TRANSFER: 0.3,
            FraudType.RAPID_SUCCESSION: 0.25,
            FraudType.AMOUNT_STRUCTURING: 0.2,
            FraudType.FAKE_MERCHANT: 0.1,
            FraudType.MULE_NETWORK: 0.1,
            FraudType.SMURFING: 0.05
        }
        
        fraud_transactions_created = 0
        
        for fraud_type, proportion in fraud_distribution.items():
            num_pattern_transactions = int(num_fraud_transactions * proportion)
            
            if fraud_type == FraudType.CIRCULAR_TRANSFER:
                fraud_transactions_created += self._create_circular_transfer_fraud(num_pattern_transactions)
            elif fraud_type == FraudType.RAPID_SUCCESSION:
                fraud_transactions_created += self._create_rapid_succession_fraud(num_pattern_transactions)
            elif fraud_type == FraudType.AMOUNT_STRUCTURING:
                fraud_transactions_created += self._create_amount_structuring_fraud(num_pattern_transactions)
            elif fraud_type == FraudType.FAKE_MERCHANT:
                fraud_transactions_created += self._create_fake_merchant_fraud(num_pattern_transactions)
            elif fraud_type == FraudType.MULE_NETWORK:
                fraud_transactions_created += self._create_mule_network_fraud(num_pattern_transactions)
            elif fraud_type == FraudType.SMURFING:
                fraud_transactions_created += self._create_smurfing_fraud(num_pattern_transactions)
        
        logger.info(f"Created {fraud_transactions_created} fraudulent transactions")
    
    def _create_circular_transfer_fraud(self, num_transactions: int) -> int:
        """Circular money transfer patterns create karta hai"""
        transactions_created = 0
        accounts = list(self.account_profiles.keys())
        
        # Create circular rings of 3-6 participants
        while transactions_created < num_transactions:
            ring_size = random.randint(3, 6)
            ring_accounts = random.sample(accounts, ring_size)
            
            # High amount circular transfers
            base_amount = random.randint(50000, 500000)
            
            for i in range(ring_size):
                sender = ring_accounts[i]
                receiver = ring_accounts[(i + 1) % ring_size]  # Circular
                
                # Add some randomness to amounts
                amount = base_amount * random.uniform(0.9, 1.1)
                
                transaction_id = f"fraud_circular_{transactions_created:06d}"
                timestamp = datetime.now() - timedelta(minutes=random.randint(5, 60))
                
                self.transaction_graph.add_edge(
                    sender, receiver,
                    transaction_id=transaction_id,
                    amount=amount,
                    timestamp=timestamp,
                    transaction_type='p2p',
                    is_successful=True,
                    is_fraudulent=True,
                    fraud_type=FraudType.CIRCULAR_TRANSFER.value,
                    fraud_score=0.9
                )
                
                transactions_created += 1
                
                if transactions_created >= num_transactions:
                    break
        
        return transactions_created
    
    def _create_rapid_succession_fraud(self, num_transactions: int) -> int:
        """Rapid succession bot-like fraud patterns"""
        transactions_created = 0
        accounts = list(self.account_profiles.keys())
        
        while transactions_created < num_transactions:
            # Select a compromised account
            fraudster = random.choice(accounts)
            
            # Rapid fire transactions within minutes
            base_time = datetime.now() - timedelta(hours=random.randint(1, 24))
            
            # 15-30 transactions within 5 minutes
            burst_size = random.randint(15, 30)
            for i in range(min(burst_size, num_transactions - transactions_created)):
                receiver = random.choice([acc for acc in accounts if acc != fraudster])
                
                # Small amounts to avoid individual detection
                amount = random.randint(500, 5000)
                
                # Very close timestamps (bot behavior)
                timestamp = base_time + timedelta(seconds=random.randint(10, 300))
                
                transaction_id = f"fraud_rapid_{transactions_created:06d}"
                
                self.transaction_graph.add_edge(
                    fraudster, receiver,
                    transaction_id=transaction_id,
                    amount=amount,
                    timestamp=timestamp,
                    transaction_type='p2p',
                    is_successful=True,
                    is_fraudulent=True,
                    fraud_type=FraudType.RAPID_SUCCESSION.value,
                    fraud_score=0.8
                )
                
                transactions_created += 1
                
            if transactions_created >= num_transactions:
                break
        
        return transactions_created
    
    def _create_amount_structuring_fraud(self, num_transactions: int) -> int:
        """Amount structuring to avoid limits"""
        transactions_created = 0
        accounts = list(self.account_profiles.keys())
        
        while transactions_created < num_transactions:
            fraudster = random.choice(accounts)
            receiver = random.choice([acc for acc in accounts if acc != fraudster])
            
            # Structure large amount into smaller transactions just below limits
            # UPI limit avoidance: amounts like 9,999, 19,999, etc.
            structured_amounts = [9999, 19999, 49999, 99999]
            
            # Create series of structured transactions
            series_size = random.randint(5, 15)
            base_time = datetime.now() - timedelta(hours=random.randint(1, 48))
            
            for i in range(min(series_size, num_transactions - transactions_created)):
                amount = random.choice(structured_amounts)
                
                # Spread over time to avoid detection
                timestamp = base_time + timedelta(hours=random.randint(1, 12))
                
                transaction_id = f"fraud_struct_{transactions_created:06d}"
                
                self.transaction_graph.add_edge(
                    fraudster, receiver,
                    transaction_id=transaction_id,
                    amount=amount,
                    timestamp=timestamp,
                    transaction_type='p2p',
                    is_successful=True,
                    is_fraudulent=True,
                    fraud_type=FraudType.AMOUNT_STRUCTURING.value,
                    fraud_score=0.75
                )
                
                transactions_created += 1
        
        return transactions_created
    
    def _create_fake_merchant_fraud(self, num_transactions: int) -> int:
        """Fake merchant fraud patterns"""
        transactions_created = 0
        accounts = list(self.account_profiles.keys())
        
        # Create fake merchant accounts
        fake_merchants = random.sample(accounts, min(10, len(accounts) // 100))
        
        for fake_merchant in fake_merchants:
            # Mark as fake merchant
            self.account_profiles[fake_merchant]['is_fake_merchant'] = True
            
            # Multiple victims send money to fake merchant
            num_victims = random.randint(20, 100)
            victims = random.sample([acc for acc in accounts if acc != fake_merchant], num_victims)
            
            for victim in victims:
                if transactions_created >= num_transactions:
                    break
                
                # Fake purchase amounts
                amount = random.randint(1000, 15000)
                
                timestamp = datetime.now() - timedelta(days=random.randint(1, 7))
                transaction_id = f"fraud_merchant_{transactions_created:06d}"
                
                self.transaction_graph.add_edge(
                    victim, fake_merchant,
                    transaction_id=transaction_id,
                    amount=amount,
                    timestamp=timestamp,
                    transaction_type='p2m',
                    is_successful=True,
                    is_fraudulent=True,
                    fraud_type=FraudType.FAKE_MERCHANT.value,
                    fraud_score=0.85
                )
                
                transactions_created += 1
            
            if transactions_created >= num_transactions:
                break
        
        return transactions_created
    
    def _create_mule_network_fraud(self, num_transactions: int) -> int:
        """Money mule network patterns"""
        transactions_created = 0
        accounts = list(self.account_profiles.keys())
        
        # Create mule network: Source -> Mules -> Final destination
        source_account = random.choice(accounts)
        final_destination = random.choice([acc for acc in accounts if acc != source_account])
        
        # 5-15 mule accounts
        num_mules = random.randint(5, 15)
        mule_accounts = random.sample(
            [acc for acc in accounts if acc not in [source_account, final_destination]], 
            num_mules
        )
        
        # Layer 1: Source to mules
        base_amount = random.randint(100000, 1000000)
        mule_amounts = []
        
        for mule in mule_accounts:
            if transactions_created >= num_transactions:
                break
                
            amount = base_amount / num_mules * random.uniform(0.8, 1.2)
            mule_amounts.append((mule, amount))
            
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 12))
            transaction_id = f"fraud_mule_1_{transactions_created:06d}"
            
            self.transaction_graph.add_edge(
                source_account, mule,
                transaction_id=transaction_id,
                amount=amount,
                timestamp=timestamp,
                transaction_type='p2p',
                is_successful=True,
                is_fraudulent=True,
                fraud_type=FraudType.MULE_NETWORK.value,
                fraud_score=0.9
            )
            
            transactions_created += 1
        
        # Layer 2: Mules to final destination
        for mule, amount in mule_amounts:
            if transactions_created >= num_transactions:
                break
            
            # Slightly less amount (mule commission)
            final_amount = amount * random.uniform(0.9, 0.95)
            
            timestamp = datetime.now() - timedelta(hours=random.randint(13, 24))
            transaction_id = f"fraud_mule_2_{transactions_created:06d}"
            
            self.transaction_graph.add_edge(
                mule, final_destination,
                transaction_id=transaction_id,
                amount=final_amount,
                timestamp=timestamp,
                transaction_type='p2p',
                is_successful=True,
                is_fraudulent=True,
                fraud_type=FraudType.MULE_NETWORK.value,
                fraud_score=0.9
            )
            
            transactions_created += 1
        
        return transactions_created
    
    def _create_smurfing_fraud(self, num_transactions: int) -> int:
        """Smurfing fraud patterns (breaking large amounts)"""
        transactions_created = 0
        accounts = list(self.account_profiles.keys())
        
        while transactions_created < num_transactions:
            source = random.choice(accounts)
            target = random.choice([acc for acc in accounts if acc != source])
            
            # Large amount broken into many small transactions
            total_amount = random.randint(500000, 2000000)  # 5L to 20L
            num_smurfs = random.randint(50, 200)  # Many small transactions
            
            base_time = datetime.now() - timedelta(days=random.randint(1, 30))
            
            for i in range(min(num_smurfs, num_transactions - transactions_created)):
                # Small amount per transaction
                amount = total_amount / num_smurfs * random.uniform(0.8, 1.2)
                amount = max(100, min(9999, amount))  # Keep below limits
                
                # Spread over days/weeks
                timestamp = base_time + timedelta(days=random.uniform(0, 7))
                
                transaction_id = f"fraud_smurf_{transactions_created:06d}"
                
                self.transaction_graph.add_edge(
                    source, target,
                    transaction_id=transaction_id,
                    amount=amount,
                    timestamp=timestamp,
                    transaction_type='p2p',
                    is_successful=True,
                    is_fraudulent=True,
                    fraud_type=FraudType.SMURFING.value,
                    fraud_score=0.7
                )
                
                transactions_created += 1
        
        return transactions_created
    
    def run_fraud_detection(self) -> List[FraudAlert]:
        """
        Complete fraud detection analysis run karta hai
        """
        logger.info("Running comprehensive fraud detection analysis...")
        
        detected_alerts = []
        
        # Run all detection algorithms
        for fraud_type, detection_function in self.detection_rules.items():
            logger.info(f"Running {fraud_type.value} detection...")
            
            try:
                alerts = detection_function()
                detected_alerts.extend(alerts)
                logger.info(f"Detected {len(alerts)} {fraud_type.value} alerts")
                
            except Exception as e:
                logger.error(f"Error in {fraud_type.value} detection: {e}")
        
        # Sort alerts by risk level and score
        risk_priority = {RiskLevel.CRITICAL: 4, RiskLevel.HIGH: 3, 
                        RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}
        
        detected_alerts.sort(key=lambda x: (risk_priority[x.risk_level], x.pattern_score), 
                           reverse=True)
        
        self.fraud_alerts = detected_alerts
        
        logger.info(f"Total fraud alerts generated: {len(detected_alerts)}")
        return detected_alerts
    
    def _detect_circular_transfer_patterns(self) -> List[FraudAlert]:
        """Circular transfer patterns detect karta hai"""
        alerts = []
        
        # Find cycles in the graph
        try:
            # Look for cycles of length 3-6 with high amounts
            for cycle_length in range(3, 7):
                cycles = []
                
                # Sample nodes for performance
                sample_nodes = random.sample(
                    list(self.transaction_graph.nodes()), 
                    min(1000, self.transaction_graph.number_of_nodes())
                )
                
                for start_node in sample_nodes:
                    cycles.extend(
                        self._find_cycles_from_node(start_node, cycle_length)
                    )
                
                # Analyze cycles for suspicious patterns
                for cycle in cycles[:100]:  # Limit analysis
                    cycle_amounts = []
                    cycle_transactions = []
                    
                    for i in range(len(cycle)):
                        node1 = cycle[i]
                        node2 = cycle[(i + 1) % len(cycle)]
                        
                        if self.transaction_graph.has_edge(node1, node2):
                            edge_data = self.transaction_graph[node1][node2]
                            cycle_amounts.append(edge_data['amount'])
                            cycle_transactions.append(edge_data['transaction_id'])
                    
                    if cycle_amounts and min(cycle_amounts) > 50000:  # High amount threshold
                        avg_amount = np.mean(cycle_amounts)
                        amount_variance = np.var(cycle_amounts)
                        
                        # Suspicious if amounts are similar (low variance)
                        if amount_variance / avg_amount < 0.1:
                            pattern_score = min(1.0, avg_amount / 100000)
                            
                            risk_level = RiskLevel.HIGH if avg_amount > 200000 else RiskLevel.MEDIUM
                            
                            alert = FraudAlert(
                                alert_id=f"circular_{len(alerts):04d}",
                                fraud_type=FraudType.CIRCULAR_TRANSFER,
                                risk_level=risk_level,
                                accounts_involved=cycle,
                                transaction_ids=cycle_transactions,
                                pattern_score=pattern_score,
                                description=f"Circular transfer ring with {len(cycle)} participants, "
                                          f"avg amount: ₹{avg_amount:,.0f}",
                                timestamp=datetime.now(),
                                evidence={
                                    'cycle_length': len(cycle),
                                    'total_amount': sum(cycle_amounts),
                                    'avg_amount': avg_amount,
                                    'amount_variance': amount_variance
                                }
                            )
                            
                            alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in circular transfer detection: {e}")
        
        return alerts
    
    def _find_cycles_from_node(self, start_node: str, max_length: int) -> List[List[str]]:
        """Starting node se cycles find karta hai"""
        cycles = []
        
        def dfs(current_path, visited_in_path):
            if len(current_path) > max_length:
                return
            
            current_node = current_path[-1]
            
            for neighbor in self.transaction_graph.successors(current_node):
                if neighbor == start_node and len(current_path) >= 3:
                    # Found a cycle back to start
                    cycles.append(current_path[:])
                elif neighbor not in visited_in_path and len(current_path) < max_length:
                    # Continue exploring
                    dfs(current_path + [neighbor], visited_in_path | {neighbor})
        
        dfs([start_node], {start_node})
        return cycles
    
    def _detect_rapid_succession_fraud(self) -> List[FraudAlert]:
        """Rapid succession fraud patterns detect karta hai"""
        alerts = []
        
        # Group transactions by sender and time windows
        for sender in self.transaction_graph.nodes():
            outgoing_edges = []
            
            for _, receiver, edge_data in self.transaction_graph.edges(sender, data=True):
                outgoing_edges.append((receiver, edge_data))
            
            if len(outgoing_edges) < 10:  # Too few transactions
                continue
            
            # Sort by timestamp
            outgoing_edges.sort(key=lambda x: x[1]['timestamp'])
            
            # Check for rapid succession in 5-minute windows
            window_size = timedelta(minutes=5)
            
            for i in range(len(outgoing_edges)):
                window_start = outgoing_edges[i][1]['timestamp']
                window_end = window_start + window_size
                
                window_transactions = []
                for j in range(i, len(outgoing_edges)):
                    if outgoing_edges[j][1]['timestamp'] <= window_end:
                        window_transactions.append(outgoing_edges[j])
                    else:
                        break
                
                # Alert if too many transactions in short time
                if len(window_transactions) >= 10:
                    total_amount = sum([tx[1]['amount'] for tx in window_transactions])
                    transaction_ids = [tx[1]['transaction_id'] for tx in window_transactions]
                    receivers = [tx[0] for tx in window_transactions]
                    
                    pattern_score = min(1.0, len(window_transactions) / 20)
                    risk_level = RiskLevel.HIGH if len(window_transactions) > 20 else RiskLevel.MEDIUM
                    
                    alert = FraudAlert(
                        alert_id=f"rapid_{len(alerts):04d}",
                        fraud_type=FraudType.RAPID_SUCCESSION,
                        risk_level=risk_level,
                        accounts_involved=[sender] + list(set(receivers)),
                        transaction_ids=transaction_ids,
                        pattern_score=pattern_score,
                        description=f"Rapid succession: {len(window_transactions)} transactions "
                                  f"in 5 minutes, total: ₹{total_amount:,.0f}",
                        timestamp=datetime.now(),
                        evidence={
                            'transaction_count': len(window_transactions),
                            'time_window': '5 minutes',
                            'total_amount': total_amount,
                            'unique_receivers': len(set(receivers))
                        }
                    )
                    
                    alerts.append(alert)
                    break  # Avoid duplicate alerts for same account
        
        return alerts
    
    def _detect_amount_structuring(self) -> List[FraudAlert]:
        """Amount structuring patterns detect karta hai"""
        alerts = []
        
        # Look for repeated transactions with amounts just below limits
        suspicious_amounts = [9999, 19999, 49999, 99999, 199999]
        tolerance = 100  # ±100 tolerance
        
        for sender in self.transaction_graph.nodes():
            for target_amount in suspicious_amounts:
                # Find transactions near target amount
                near_target_transactions = []
                
                for _, receiver, edge_data in self.transaction_graph.edges(sender, data=True):
                    amount = edge_data['amount']
                    if abs(amount - target_amount) <= tolerance:
                        near_target_transactions.append((receiver, edge_data))
                
                # Alert if too many transactions near limit
                if len(near_target_transactions) >= 5:
                    total_amount = sum([tx[1]['amount'] for tx in near_target_transactions])
                    transaction_ids = [tx[1]['transaction_id'] for tx in near_target_transactions]
                    receivers = [tx[0] for tx in near_target_transactions]
                    
                    pattern_score = min(1.0, len(near_target_transactions) / 10)
                    risk_level = RiskLevel.MEDIUM
                    
                    alert = FraudAlert(
                        alert_id=f"structuring_{len(alerts):04d}",
                        fraud_type=FraudType.AMOUNT_STRUCTURING,
                        risk_level=risk_level,
                        accounts_involved=[sender] + list(set(receivers)),
                        transaction_ids=transaction_ids,
                        pattern_score=pattern_score,
                        description=f"Amount structuring: {len(near_target_transactions)} "
                                  f"transactions near ₹{target_amount:,}",
                        timestamp=datetime.now(),
                        evidence={
                            'target_amount': target_amount,
                            'transaction_count': len(near_target_transactions),
                            'total_amount': total_amount,
                            'avg_amount': total_amount / len(near_target_transactions)
                        }
                    )
                    
                    alerts.append(alert)
        
        return alerts
    
    def _detect_fake_merchant_patterns(self) -> List[FraudAlert]:
        """Fake merchant patterns detect karta hai"""
        alerts = []
        
        # Find accounts with high incoming P2M transactions from many sources
        for account in self.transaction_graph.nodes():
            incoming_p2m = []
            
            for sender, _, edge_data in self.transaction_graph.in_edges(account, data=True):
                if edge_data.get('transaction_type') == 'p2m':
                    incoming_p2m.append((sender, edge_data))
            
            # Alert if many different senders to same "merchant"
            if len(incoming_p2m) >= 20:
                unique_senders = len(set([tx[0] for tx in incoming_p2m]))
                total_amount = sum([tx[1]['amount'] for tx in incoming_p2m])
                transaction_ids = [tx[1]['transaction_id'] for tx in incoming_p2m]
                
                # Check if account profile suggests legitimate merchant
                account_profile = self.account_profiles[account]
                if account_profile.get('account_type') != 'merchant':
                    # Suspicious: individual account receiving many merchant payments
                    
                    pattern_score = min(1.0, unique_senders / 50)
                    risk_level = RiskLevel.HIGH if unique_senders > 50 else RiskLevel.MEDIUM
                    
                    alert = FraudAlert(
                        alert_id=f"fake_merchant_{len(alerts):04d}",
                        fraud_type=FraudType.FAKE_MERCHANT,
                        risk_level=risk_level,
                        accounts_involved=[account] + [tx[0] for tx in incoming_p2m[:10]],  # Top 10 senders
                        transaction_ids=transaction_ids,
                        pattern_score=pattern_score,
                        description=f"Potential fake merchant: {unique_senders} senders, "
                                  f"total: ₹{total_amount:,.0f}",
                        timestamp=datetime.now(),
                        evidence={
                            'unique_senders': unique_senders,
                            'total_transactions': len(incoming_p2m),
                            'total_amount': total_amount,
                            'account_type': account_profile['account_type']
                        }
                    )
                    
                    alerts.append(alert)
        
        return alerts
    
    def _detect_account_takeover(self) -> List[FraudAlert]:
        """Account takeover patterns detect karta hai"""
        alerts = []
        
        # Look for sudden changes in transaction behavior
        for account in self.transaction_graph.nodes():
            if account not in self.transaction_history:
                continue
            
            transactions = self.transaction_history[account]
            if len(transactions) < 10:
                continue
            
            # Sort by timestamp
            transactions.sort(key=lambda x: x['timestamp'])
            
            # Split into before and after periods
            split_point = len(transactions) * 3 // 4  # Recent 25% vs previous 75%
            before_transactions = transactions[:split_point]
            after_transactions = transactions[split_point:]
            
            if len(after_transactions) < 5:
                continue
            
            # Calculate behavior changes
            before_avg_amount = np.mean([tx['amount'] for tx in before_transactions])
            after_avg_amount = np.mean([tx['amount'] for tx in after_transactions])
            
            before_frequency = len(before_transactions) / max(1, 
                (before_transactions[-1]['timestamp'] - before_transactions[0]['timestamp']).days)
            after_frequency = len(after_transactions) / max(1,
                (after_transactions[-1]['timestamp'] - after_transactions[0]['timestamp']).days)
            
            # Check for significant changes
            amount_change_ratio = after_avg_amount / before_avg_amount if before_avg_amount > 0 else 0
            frequency_change_ratio = after_frequency / before_frequency if before_frequency > 0 else 0
            
            # Alert if significant behavior change
            if (amount_change_ratio > 3 or frequency_change_ratio > 5 or 
                (amount_change_ratio > 2 and frequency_change_ratio > 3)):
                
                pattern_score = min(1.0, max(amount_change_ratio, frequency_change_ratio) / 10)
                risk_level = RiskLevel.HIGH if pattern_score > 0.7 else RiskLevel.MEDIUM
                
                suspicious_transaction_ids = [tx['transaction_id'] for tx in after_transactions]
                
                alert = FraudAlert(
                    alert_id=f"takeover_{len(alerts):04d}",
                    fraud_type=FraudType.ACCOUNT_TAKEOVER,
                    risk_level=risk_level,
                    accounts_involved=[account],
                    transaction_ids=suspicious_transaction_ids,
                    pattern_score=pattern_score,
                    description=f"Potential account takeover: {amount_change_ratio:.1f}x amount change, "
                              f"{frequency_change_ratio:.1f}x frequency change",
                    timestamp=datetime.now(),
                    evidence={
                        'before_avg_amount': before_avg_amount,
                        'after_avg_amount': after_avg_amount,
                        'amount_change_ratio': amount_change_ratio,
                        'frequency_change_ratio': frequency_change_ratio,
                        'recent_transaction_count': len(after_transactions)
                    }
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _detect_mule_networks(self) -> List[FraudAlert]:
        """Money mule network patterns detect karta hai"""
        alerts = []
        
        # Look for hub-like structures: one source -> many intermediaries -> few destinations
        for potential_source in self.transaction_graph.nodes():
            # Find accounts that receive from potential_source and then forward money
            intermediaries = []
            
            for receiver in self.transaction_graph.successors(potential_source):
                # Check if receiver forwards money to other accounts
                forward_count = self.transaction_graph.out_degree(receiver)
                receive_amount = sum([edge_data['amount'] 
                                    for _, _, edge_data in 
                                    self.transaction_graph.edges(potential_source, receiver, data=True)])
                
                if forward_count > 0:
                    forward_amount = sum([edge_data['amount'] 
                                        for _, _, edge_data in 
                                        self.transaction_graph.edges(receiver, data=True)])
                    
                    # Check if forward amount is close to receive amount (mule behavior)
                    if receive_amount > 0 and 0.8 <= forward_amount / receive_amount <= 0.98:
                        intermediaries.append((receiver, receive_amount, forward_amount))
            
            # Alert if multiple potential mules found
            if len(intermediaries) >= 3:
                total_source_amount = sum([data[1] for data in intermediaries])
                
                # Get transaction IDs
                transaction_ids = []
                for intermediary, _, _ in intermediaries:
                    for _, _, edge_data in self.transaction_graph.edges(potential_source, intermediary, data=True):
                        transaction_ids.append(edge_data['transaction_id'])
                    for _, _, edge_data in self.transaction_graph.edges(intermediary, data=True):
                        transaction_ids.append(edge_data['transaction_id'])
                
                pattern_score = min(1.0, len(intermediaries) / 10)
                risk_level = RiskLevel.HIGH if len(intermediaries) > 5 else RiskLevel.MEDIUM
                
                accounts_involved = [potential_source] + [data[0] for data in intermediaries]
                
                alert = FraudAlert(
                    alert_id=f"mule_network_{len(alerts):04d}",
                    fraud_type=FraudType.MULE_NETWORK,
                    risk_level=risk_level,
                    accounts_involved=accounts_involved,
                    transaction_ids=transaction_ids,
                    pattern_score=pattern_score,
                    description=f"Money mule network: {len(intermediaries)} intermediaries, "
                              f"total: ₹{total_source_amount:,.0f}",
                    timestamp=datetime.now(),
                    evidence={
                        'intermediary_count': len(intermediaries),
                        'total_amount': total_source_amount,
                        'avg_retention_rate': np.mean([1 - (data[2]/data[1]) for data in intermediaries])
                    }
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _detect_smurfing_patterns(self) -> List[FraudAlert]:
        """Smurfing patterns detect karta hai"""
        alerts = []
        
        # Look for many small transactions between same pair of accounts
        account_pairs = defaultdict(list)
        
        # Group transactions by account pairs
        for sender, receiver, edge_data in self.transaction_graph.edges(data=True):
            if sender != receiver:  # Avoid self-loops
                pair_key = tuple(sorted([sender, receiver]))
                account_pairs[pair_key].append(edge_data)
        
        # Analyze each pair for smurfing patterns
        for (account1, account2), transactions in account_pairs.items():
            if len(transactions) < 20:  # Too few transactions
                continue
            
            # Check if amounts are consistently small
            amounts = [tx['amount'] for tx in transactions]
            avg_amount = np.mean(amounts)
            max_amount = max(amounts)
            
            # Smurfing characteristics: many small, similar amounts
            if (len(transactions) >= 20 and avg_amount < 10000 and 
                max_amount < 50000 and np.std(amounts) / avg_amount < 0.5):
                
                total_amount = sum(amounts)
                transaction_ids = [tx['transaction_id'] for tx in transactions]
                
                # Time span analysis
                timestamps = [tx['timestamp'] for tx in transactions]
                time_span = max(timestamps) - min(timestamps)
                
                pattern_score = min(1.0, (len(transactions) * avg_amount) / 1000000)
                risk_level = RiskLevel.MEDIUM if total_amount > 500000 else RiskLevel.LOW
                
                alert = FraudAlert(
                    alert_id=f"smurfing_{len(alerts):04d}",
                    fraud_type=FraudType.SMURFING,
                    risk_level=risk_level,
                    accounts_involved=[account1, account2],
                    transaction_ids=transaction_ids,
                    pattern_score=pattern_score,
                    description=f"Smurfing pattern: {len(transactions)} small transactions, "
                              f"total: ₹{total_amount:,.0f}",
                    timestamp=datetime.now(),
                    evidence={
                        'transaction_count': len(transactions),
                        'avg_amount': avg_amount,
                        'total_amount': total_amount,
                        'time_span_days': time_span.days,
                        'amount_consistency': 1 - (np.std(amounts) / avg_amount)
                    }
                )
                
                alerts.append(alert)
        
        return alerts
    
    def generate_fraud_detection_report(self, alerts: List[FraudAlert]) -> str:
        """
        Comprehensive fraud detection report generate karta hai
        """
        report = []
        report.append("🚨 UPI FRAUD DETECTION SYSTEM - ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # System overview
        report.append("📊 SYSTEM OVERVIEW:")
        report.append(f"• Total Accounts: {len(self.account_profiles):,}")
        report.append(f"• Total Transactions: {self.transaction_graph.number_of_edges():,}")
        report.append(f"• Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Alert summary
        if alerts:
            report.append(f"🚨 FRAUD ALERTS SUMMARY:")
            report.append(f"• Total Alerts Generated: {len(alerts)}")
            
            # Count by risk level
            risk_counts = Counter([alert.risk_level for alert in alerts])
            for risk_level, count in sorted(risk_counts.items(), key=lambda x: x[0].value):
                report.append(f"• {risk_level.value.title()} Risk: {count} alerts")
            
            # Count by fraud type
            fraud_type_counts = Counter([alert.fraud_type for alert in alerts])
            report.append("\n🎯 FRAUD TYPE DISTRIBUTION:")
            for fraud_type, count in fraud_type_counts.most_common():
                report.append(f"• {fraud_type.value.replace('_', ' ').title()}: {count} alerts")
            
            report.append("")
        
        # Detailed alerts (top 10)
        if alerts:
            report.append("🔍 TOP PRIORITY ALERTS:")
            report.append("-" * 40)
            
            for i, alert in enumerate(alerts[:10], 1):
                report.append(f"\n{i}. Alert ID: {alert.alert_id}")
                report.append(f"   Type: {alert.fraud_type.value.replace('_', ' ').title()}")
                report.append(f"   Risk Level: {alert.risk_level.value.title()}")
                report.append(f"   Pattern Score: {alert.pattern_score:.3f}")
                report.append(f"   Accounts: {len(alert.accounts_involved)} involved")
                report.append(f"   Transactions: {len(alert.transaction_ids)}")
                report.append(f"   Description: {alert.description}")
                
                # Key evidence
                if alert.evidence:
                    report.append("   Evidence:")
                    for key, value in list(alert.evidence.items())[:3]:  # Top 3 evidence points
                        if isinstance(value, float):
                            report.append(f"     • {key}: {value:.2f}")
                        else:
                            report.append(f"     • {key}: {value}")
        
        # Network statistics
        report.append(f"\n📈 NETWORK ANALYSIS:")
        report.append("-" * 25)
        
        # Basic network metrics
        avg_degree = 2 * self.transaction_graph.number_of_edges() / self.transaction_graph.number_of_nodes()
        report.append(f"• Average Connections per Account: {avg_degree:.1f}")
        
        # Top active accounts
        out_degrees = dict(self.transaction_graph.out_degree())
        top_senders = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        
        report.append("\n• Most Active Senders:")
        for account, degree in top_senders:
            account_type = self.account_profiles[account]['account_type']
            report.append(f"  - {account} ({account_type}): {degree} outgoing transactions")
        
        # Detection performance
        report.append(f"\n⚡ DETECTION PERFORMANCE:")
        report.append("-" * 30)
        
        # Calculate detection rates (assuming we know ground truth from injected fraud)
        total_fraudulent_edges = sum(1 for _, _, data in self.transaction_graph.edges(data=True)
                                   if data.get('is_fraudulent', False))
        
        if total_fraudulent_edges > 0:
            # Count unique fraudulent transactions in alerts
            alerted_fraud_transactions = set()
            for alert in alerts:
                alerted_fraud_transactions.update(alert.transaction_ids)
            
            # Check how many are actually fraudulent
            true_positives = 0
            for tx_id in alerted_fraud_transactions:
                for _, _, data in self.transaction_graph.edges(data=True):
                    if (data.get('transaction_id') == tx_id and 
                        data.get('is_fraudulent', False)):
                        true_positives += 1
                        break
            
            detection_rate = true_positives / total_fraudulent_edges if total_fraudulent_edges > 0 else 0
            precision = true_positives / len(alerted_fraud_transactions) if alerted_fraud_transactions else 0
            
            report.append(f"• Detection Rate: {detection_rate:.1%}")
            report.append(f"• Precision: {precision:.1%}")
            report.append(f"• Total Fraudulent Patterns: {total_fraudulent_edges:,}")
            report.append(f"• Detected Patterns: {true_positives:,}")
        
        # Recommendations
        report.append(f"\n💡 RECOMMENDATIONS:")
        report.append("-" * 22)
        report.append("• Investigate CRITICAL and HIGH risk alerts immediately")
        report.append("• Monitor accounts involved in multiple alert types")
        report.append("• Implement real-time blocking for circular transfers > ₹5L")
        report.append("• Enhance KYC verification for high-risk accounts")
        report.append("• Set up automated alerts for rapid succession patterns")
        
        # Production deployment notes
        report.append(f"\n🚀 PRODUCTION DEPLOYMENT:")
        report.append("-" * 30)
        report.append("• Real-time processing: < 100ms per transaction")
        report.append("• Batch analysis: Run every 15 minutes")
        report.append("• Model updates: Retrain weekly with new patterns")
        report.append("• False positive rate: Target < 0.1%")
        report.append("• Integration: API endpoints for external systems")
        
        return "\n".join(report)


def run_upi_fraud_detection_demo():
    """
    Complete UPI fraud detection system demonstration
    """
    print("🚨 UPI Fraud Detection System - Graph Pattern Analysis")
    print("="*60)
    
    # Initialize fraud detection system
    fraud_detector = UPIFraudDetectionSystem()
    
    # Generate realistic UPI transaction data with fraud patterns
    print("\n🏗️ Generating UPI transaction dataset with fraud patterns...")
    fraud_detector.generate_upi_transaction_data(
        num_accounts=5000,      # 5K accounts for demo
        num_transactions=50000,  # 50K transactions 
        fraud_percentage=0.05    # 5% fraud rate
    )
    
    print(f"✅ UPI transaction dataset generated!")
    print(f"   • Total Accounts: {len(fraud_detector.account_profiles):,}")
    print(f"   • Total Transactions: {fraud_detector.transaction_graph.number_of_edges():,}")
    print(f"   • Expected Fraud Transactions: ~{int(50000 * 0.05):,}")
    
    # Run comprehensive fraud detection
    print("\n🔍 Running comprehensive fraud detection analysis...")
    fraud_alerts = fraud_detector.run_fraud_detection()
    
    # Generate detailed report
    print(f"\n📋 FRAUD DETECTION REPORT:")
    print("=" * 50)
    
    report = fraud_detector.generate_fraud_detection_report(fraud_alerts)
    print(report)
    
    # Show sample alerts in detail
    if fraud_alerts:
        print(f"\n🚨 SAMPLE HIGH-RISK ALERT DETAILS:")
        print("-" * 40)
        
        # Show top 3 alerts
        for i, alert in enumerate(fraud_alerts[:3], 1):
            print(f"\nAlert {i}:")
            print(f"  🆔 ID: {alert.alert_id}")
            print(f"  ⚠️  Type: {alert.fraud_type.value.replace('_', ' ').title()}")
            print(f"  🎯 Risk: {alert.risk_level.value.title()}")
            print(f"  📊 Score: {alert.pattern_score:.3f}")
            print(f"  👥 Accounts: {len(alert.accounts_involved)}")
            print(f"  💳 Transactions: {len(alert.transaction_ids)}")
            print(f"  📝 Description: {alert.description}")
            
            if alert.evidence:
                print("  🔍 Key Evidence:")
                for key, value in list(alert.evidence.items())[:3]:
                    if isinstance(value, (int, float)):
                        print(f"     • {key}: {value:,}" if isinstance(value, int) else f"     • {key}: {value:.2f}")
                    else:
                        print(f"     • {key}: {value}")
    
    # Performance analysis
    print(f"\n⚡ SYSTEM PERFORMANCE ANALYSIS:")
    print("-" * 35)
    
    # Measure detection performance
    start_time = time.time()
    sample_alerts = fraud_detector.run_fraud_detection()
    detection_time = time.time() - start_time
    
    print(f"🕐 Detection Time: {detection_time:.2f} seconds")
    print(f"📊 Throughput: {fraud_detector.transaction_graph.number_of_edges() / detection_time:.0f} transactions/second")
    print(f"💾 Memory Usage: ~{fraud_detector.transaction_graph.number_of_nodes() * 0.5:.1f} MB")
    
    # Scalability projections
    print(f"\n📈 SCALABILITY PROJECTIONS:")
    print("-" * 30)
    
    scale_scenarios = [
        ("Demo Scale", "5K accounts, 50K txns", f"{detection_time:.1f}s", "Single server"),
        ("Branch Scale", "50K accounts, 1M txns", "30-60s", "Multi-core server"),
        ("Bank Scale", "1M accounts, 100M txns", "10-20 minutes", "Distributed cluster"),
        ("UPI Scale", "50M accounts, 10B txns", "2-4 hours", "Large cluster + streaming")
    ]
    
    for scenario, data_size, time_est, infrastructure in scale_scenarios:
        print(f"🎯 {scenario}: {data_size} → {time_est} ({infrastructure})")
    
    # Real-world deployment considerations
    print(f"\n🚀 PRODUCTION DEPLOYMENT FEATURES:")
    print("-" * 40)
    features = [
        "⚡ Real-time transaction scoring (< 100ms)",
        "📊 Batch fraud pattern analysis (15-minute cycles)",  
        "🔄 Streaming data integration (Kafka/Pulsar)",
        "📱 Mobile app integration for instant alerts",
        "🤖 ML model auto-retraining with new patterns",
        "🔒 Privacy-preserving analytics (data anonymization)",
        "📈 Real-time dashboards for fraud analysts",
        "🚨 Automated account blocking for high-risk patterns"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    # Regulatory compliance
    print(f"\n⚖️ REGULATORY COMPLIANCE:")
    print("-" * 28)
    compliance_features = [
        "🇮🇳 RBI compliance for transaction monitoring",
        "🔐 Data localization (Indian data centers only)",
        "📋 Audit trails for all fraud decisions",
        "🕒 Transaction data retention (7 years)",
        "🔍 AML (Anti-Money Laundering) reporting",
        "📊 Suspicious Activity Report (SAR) generation"
    ]
    
    for feature in compliance_features:
        print(f"   {feature}")


if __name__ == "__main__":
    # UPI fraud detection demo
    run_upi_fraud_detection_demo()
    
    print("\n" + "="*60)
    print("📚 LEARNING POINTS:")
    print("• Graph patterns Indian payment systems mein fraud detection ke liye powerful hai")
    print("• Circular transfers, rapid succession, amount structuring common fraud types hai")
    print("• Real-time detection systems 100ms response time mein accurate results de sakte hai")
    print("• Network analysis se complex fraud rings identify kar sakte hai")
    print("• Production systems mein privacy, compliance, और scalability critical factors hai")