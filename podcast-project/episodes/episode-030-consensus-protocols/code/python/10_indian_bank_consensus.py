#!/usr/bin/env python3
"""
Indian Bank Consensus System
============================

Multi-bank transaction consensus - RBI coordination style!
Simulates how Indian banks coordinate for inter-bank transactions,
NEFT/RTGS settlements, and regulatory compliance.

Features:
- Multi-bank consensus for large transactions
- RBI oversight and validation
- NEFT/RTGS settlement simulation
- Fraud detection consensus
- Mumbai banking network simulation

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json
import uuid
from datetime import datetime, timedelta

class BankType(Enum):
    """Types of banks in Indian system"""
    PUBLIC_SECTOR = "public_sector"
    PRIVATE_SECTOR = "private_sector"
    FOREIGN = "foreign"
    COOPERATIVE = "cooperative"
    PAYMENT_BANK = "payment_bank"
    SMALL_FINANCE = "small_finance"

class TransactionType(Enum):
    """Types of banking transactions"""
    NEFT = "neft"           # National Electronic Funds Transfer
    RTGS = "rtgs"           # Real Time Gross Settlement
    IMPS = "imps"           # Immediate Payment Service
    UPI = "upi"             # Unified Payments Interface
    WIRE_TRANSFER = "wire_transfer"
    BULK_TRANSFER = "bulk_transfer"

class TransactionStatus(Enum):
    """Transaction processing status"""
    SUBMITTED = "submitted"
    PENDING_CONSENSUS = "pending_consensus"
    VALIDATED = "validated"
    SETTLED = "settled"
    REJECTED = "rejected"
    FLAGGED = "flagged"

class RiskLevel(Enum):
    """Risk levels for transactions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BankingTransaction:
    """
    Inter-bank transaction structure
    """
    tx_id: str
    tx_type: TransactionType
    sender_bank: str
    receiver_bank: str
    sender_account: str
    receiver_account: str
    amount: float
    currency: str = "INR"
    
    # Regulatory fields
    purpose_code: str = ""
    customer_id: str = ""
    aml_score: float = 0.0  # Anti-Money Laundering score
    
    # Timestamps
    submitted_at: float = field(default_factory=time.time)
    settlement_time: Optional[float] = None
    
    # Risk assessment
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: List[str] = field(default_factory=list)
    
    def get_hash(self) -> str:
        """Calculate transaction hash for integrity"""
        data = f"{self.sender_bank}:{self.receiver_bank}:{self.amount}:{self.submitted_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def assess_risk_level(self) -> RiskLevel:
        """Assess transaction risk level"""
        risk_score = 0
        self.risk_factors = []
        
        # Amount-based risk
        if self.amount > 50000000:  # 5 crores
            risk_score += 3
            self.risk_factors.append("high_value")
        elif self.amount > 10000000:  # 1 crore
            risk_score += 2
            self.risk_factors.append("medium_value")
        
        # Cross-border risk
        if self.sender_bank.endswith("_FOREIGN") or self.receiver_bank.endswith("_FOREIGN"):
            risk_score += 2
            self.risk_factors.append("cross_border")
        
        # Time-based risk (late night transactions)
        hour = datetime.fromtimestamp(self.submitted_at).hour
        if hour < 6 or hour > 22:
            risk_score += 1
            self.risk_factors.append("odd_hours")
        
        # AML score risk
        if self.aml_score > 0.7:
            risk_score += 2
            self.risk_factors.append("high_aml_score")
        
        # Transaction type risk
        if self.tx_type == TransactionType.WIRE_TRANSFER:
            risk_score += 1
            self.risk_factors.append("wire_transfer")
        
        # Determine risk level
        if risk_score >= 6:
            self.risk_level = RiskLevel.CRITICAL
        elif risk_score >= 4:
            self.risk_level = RiskLevel.HIGH
        elif risk_score >= 2:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
        
        return self.risk_level

class IndianBank:
    """
    Indian bank participating in consensus
    """
    
    def __init__(self, bank_code: str, bank_name: str, bank_type: BankType):
        self.bank_code = bank_code
        self.bank_name = bank_name
        self.bank_type = bank_type
        
        # Banking parameters
        self.daily_limit = self.get_daily_limit()
        self.transaction_limit = self.get_transaction_limit()
        self.reserve_ratio = random.uniform(0.15, 0.25)  # Cash Reserve Ratio
        
        # Consensus participation
        self.consensus_weight = self.calculate_consensus_weight()
        self.reliability_score = random.uniform(0.9, 0.99)
        self.processing_capacity = random.randint(1000, 10000)  # Transactions per hour
        
        # Current state
        self.available_liquidity = random.uniform(1000000000, 10000000000)  # 100 crore to 1000 crore
        self.pending_settlements = []
        self.processed_today = 0
        
        # Performance tracking
        self.transactions_processed = 0
        self.consensus_participations = 0
        self.votes_cast = 0
        self.settlements_completed = 0
        
        # Mumbai operational characteristics
        self.response_time = random.uniform(0.1, 1.0)  # Response time in seconds
        self.fraud_detection_accuracy = random.uniform(0.85, 0.95)
        
        print(f"🏦 {bank_name} initialized ({bank_type.value}) - Weight: {self.consensus_weight}")
    
    def get_daily_limit(self) -> float:
        """Get daily transaction limit based on bank type"""
        limit_map = {
            BankType.PUBLIC_SECTOR: 100000000000,    # 1000 crores
            BankType.PRIVATE_SECTOR: 50000000000,     # 500 crores  
            BankType.FOREIGN: 200000000000,           # 2000 crores
            BankType.COOPERATIVE: 5000000000,         # 50 crores
            BankType.PAYMENT_BANK: 1000000000,        # 10 crores
            BankType.SMALL_FINANCE: 2000000000        # 20 crores
        }
        return limit_map.get(self.bank_type, 10000000000)
    
    def get_transaction_limit(self) -> float:
        """Get per-transaction limit"""
        return self.daily_limit / 100  # 1% of daily limit per transaction
    
    def calculate_consensus_weight(self) -> float:
        """Calculate consensus weight based on bank characteristics"""
        base_weight = 1.0
        
        # Bank type weighting
        type_weights = {
            BankType.PUBLIC_SECTOR: 1.5,
            BankType.PRIVATE_SECTOR: 1.2,
            BankType.FOREIGN: 1.0,
            BankType.COOPERATIVE: 0.8,
            BankType.PAYMENT_BANK: 0.6,
            BankType.SMALL_FINANCE: 0.7
        }
        
        base_weight *= type_weights.get(self.bank_type, 1.0)
        
        # Add some randomness for individual bank strength
        individual_factor = random.uniform(0.8, 1.3)
        
        return base_weight * individual_factor
    
    def validate_transaction(self, transaction: BankingTransaction) -> Tuple[bool, str]:
        """
        Validate transaction - Mumbai banking compliance check
        """
        # Simulate processing time
        time.sleep(self.response_time)
        
        # Check if bank is sender or receiver
        is_participant = (transaction.sender_bank == self.bank_code or 
                         transaction.receiver_bank == self.bank_code)
        
        if not is_participant:
            # Third-party validation
            return self.validate_third_party_transaction(transaction)
        
        # Participant bank validation
        validation_checks = []
        
        # Liquidity check
        if transaction.sender_bank == self.bank_code:
            if transaction.amount > self.available_liquidity:
                return False, "Insufficient liquidity"
            validation_checks.append("liquidity_ok")
        
        # Daily limit check
        if self.processed_today + transaction.amount > self.daily_limit:
            return False, "Daily limit exceeded"
        validation_checks.append("daily_limit_ok")
        
        # Transaction limit check
        if transaction.amount > self.transaction_limit:
            return False, f"Transaction limit exceeded (max: {self.transaction_limit:,.0f})"
        validation_checks.append("transaction_limit_ok")
        
        # Risk assessment
        risk_level = transaction.assess_risk_level()
        if risk_level == RiskLevel.CRITICAL:
            return False, f"Critical risk level: {', '.join(transaction.risk_factors)}"
        validation_checks.append("risk_acceptable")
        
        # AML/KYC check
        if transaction.aml_score > 0.8:
            return False, "AML compliance failure"
        validation_checks.append("aml_ok")
        
        # Account validation (simplified)
        if not transaction.sender_account or not transaction.receiver_account:
            return False, "Invalid account details"
        validation_checks.append("accounts_valid")
        
        # All checks passed
        return True, f"Validation passed: {', '.join(validation_checks)}"
    
    def validate_third_party_transaction(self, transaction: BankingTransaction) -> Tuple[bool, str]:
        """
        Validate transaction as third-party (consensus participant)
        """
        # Fraud detection
        fraud_probability = self.detect_fraud_probability(transaction)
        if fraud_probability > 0.7:
            return False, f"Potential fraud detected (score: {fraud_probability:.2f})"
        
        # Regulatory compliance
        if not self.check_regulatory_compliance(transaction):
            return False, "Regulatory compliance failure"
        
        # Network capacity check
        if len(self.pending_settlements) > self.processing_capacity:
            return False, "Network capacity exceeded"
        
        return True, "Third-party validation passed"
    
    def detect_fraud_probability(self, transaction: BankingTransaction) -> float:
        """
        Detect fraud probability - Mumbai banking AI
        """
        fraud_score = 0.0
        
        # Amount pattern analysis
        if transaction.amount % 100000 == 0:  # Round numbers suspicious
            fraud_score += 0.1
        
        # Time pattern analysis
        hour = datetime.fromtimestamp(transaction.submitted_at).hour
        if hour < 4 or hour > 23:  # Very late/early hours
            fraud_score += 0.2
        
        # Cross-border transactions
        if transaction.sender_bank.endswith("_FOREIGN") or transaction.receiver_bank.endswith("_FOREIGN"):
            fraud_score += 0.15
        
        # High-value transactions
        if transaction.amount > 10000000:  # Above 1 crore
            fraud_score += 0.1
        
        # AML score integration
        fraud_score += transaction.aml_score * 0.3
        
        # Random factor for ML uncertainty
        fraud_score += random.uniform(-0.1, 0.2)
        
        # Apply bank's fraud detection accuracy
        accuracy_factor = random.uniform(self.fraud_detection_accuracy, 1.0)
        
        return min(1.0, max(0.0, fraud_score * accuracy_factor))
    
    def check_regulatory_compliance(self, transaction: BankingTransaction) -> bool:
        """
        Check RBI regulatory compliance
        """
        # Purpose code requirement for high-value transactions
        if transaction.amount > 5000000 and not transaction.purpose_code:  # 50 lakh
            return False
        
        # Customer ID requirement
        if transaction.amount > 1000000 and not transaction.customer_id:  # 10 lakh
            return False
        
        # Transaction type compliance
        if transaction.tx_type == TransactionType.RTGS and transaction.amount < 200000:  # 2 lakh minimum
            return False
        
        if transaction.tx_type == TransactionType.NEFT and transaction.amount > 25000000:  # 2.5 crore limit
            return False
        
        return True
    
    def vote_on_transaction(self, transaction: BankingTransaction) -> Tuple[bool, float, str]:
        """
        Vote on transaction consensus - Mumbai banking committee decision
        """
        self.votes_cast += 1
        self.consensus_participations += 1
        
        # Validate transaction
        is_valid, reason = self.validate_transaction(transaction)
        
        # Calculate confidence score
        confidence = self.reliability_score
        
        if not is_valid:
            confidence *= 0.1  # Low confidence if validation failed
        
        # Adjust confidence based on risk level
        risk_adjustments = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 0.8,
            RiskLevel.HIGH: 0.6,
            RiskLevel.CRITICAL: 0.2
        }
        confidence *= risk_adjustments.get(transaction.risk_level, 0.5)
        
        # Mumbai banking sentiment factor
        market_sentiment = random.uniform(0.8, 1.2)
        confidence *= market_sentiment
        
        vote = is_valid and confidence > 0.7
        
        print(f"   🗳️ {self.bank_name} voted: {'✅ APPROVE' if vote else '❌ REJECT'} "
              f"(confidence: {confidence:.2f})")
        
        return vote, confidence, reason
    
    def process_settlement(self, transaction: BankingTransaction):
        """
        Process transaction settlement - Mumbai clearing house
        """
        if transaction.sender_bank == self.bank_code:
            # Debit sender account
            self.available_liquidity -= transaction.amount
            self.processed_today += transaction.amount
            print(f"   💸 {self.bank_name} debited ₹{transaction.amount:,.0f}")
            
        elif transaction.receiver_bank == self.bank_code:
            # Credit receiver account
            self.available_liquidity += transaction.amount
            print(f"   💰 {self.bank_name} credited ₹{transaction.amount:,.0f}")
        
        self.settlements_completed += 1
        self.transactions_processed += 1
    
    def get_bank_stats(self) -> Dict:
        """Get bank performance statistics"""
        return {
            "bank_code": self.bank_code,
            "bank_name": self.bank_name,
            "bank_type": self.bank_type.value,
            "consensus_weight": self.consensus_weight,
            "reliability_score": self.reliability_score,
            "available_liquidity": self.available_liquidity,
            "processed_today": self.processed_today,
            "daily_limit": self.daily_limit,
            "transactions_processed": self.transactions_processed,
            "consensus_participations": self.consensus_participations,
            "votes_cast": self.votes_cast,
            "settlements_completed": self.settlements_completed,
            "fraud_detection_accuracy": self.fraud_detection_accuracy
        }

class RBIConsensusSystem:
    """
    RBI-supervised consensus system for inter-bank transactions
    """
    
    def __init__(self, banks: List[IndianBank]):
        self.banks = {bank.bank_code: bank for bank in banks}
        self.bank_weights = {bank.bank_code: bank.consensus_weight for bank in banks}
        
        # Consensus parameters
        self.approval_threshold = 0.67  # 2/3rd majority
        self.minimum_participants = max(3, len(banks) // 2)
        self.settlement_window = 30.0  # seconds for settlement
        
        # RBI oversight
        self.rbi_approval_required_amount = 100000000  # 10 crores
        self.suspicious_transaction_threshold = 0.6
        
        # System state
        self.processed_transactions = []
        self.pending_transactions = []
        self.settlement_queue = []
        
        # Performance metrics
        self.total_volume = 0.0
        self.successful_settlements = 0
        self.failed_settlements = 0
        self.fraud_prevented = 0
        
        print(f"🏛️ RBI Consensus System initialized with {len(banks)} banks")
        print(f"   Approval threshold: {self.approval_threshold*100}%")
        print(f"   Minimum participants: {self.minimum_participants}")
    
    def submit_transaction(self, transaction: BankingTransaction) -> str:
        """
        Submit transaction for consensus
        """
        print(f"\n📨 TRANSACTION SUBMISSION")
        print(f"   TX ID: {transaction.tx_id}")
        print(f"   Type: {transaction.tx_type.value.upper()}")
        print(f"   Amount: ₹{transaction.amount:,.0f}")
        print(f"   From: {transaction.sender_bank} → To: {transaction.receiver_bank}")
        
        # Assess risk level
        risk_level = transaction.assess_risk_level()
        print(f"   Risk Level: {risk_level.value.upper()}")
        if transaction.risk_factors:
            print(f"   Risk Factors: {', '.join(transaction.risk_factors)}")
        
        self.pending_transactions.append(transaction)
        return transaction.tx_id
    
    def run_consensus(self, transaction: BankingTransaction) -> Tuple[bool, Dict]:
        """
        Run consensus process for transaction
        """
        print(f"\n🏛️ CONSENSUS PROCESS for {transaction.tx_id}")
        print("=" * 60)
        
        # Check if RBI approval required
        if transaction.amount >= self.rbi_approval_required_amount:
            rbi_approved = self.get_rbi_approval(transaction)
            if not rbi_approved:
                return False, {
                    "result": "rejected",
                    "reason": "RBI approval denied",
                    "rbi_approval": False
                }
        
        # Get participant banks (all banks participate in consensus)
        participating_banks = list(self.banks.keys())
        
        if len(participating_banks) < self.minimum_participants:
            return False, {
                "result": "rejected",
                "reason": f"Insufficient participants: {len(participating_banks)} < {self.minimum_participants}"
            }
        
        print(f"   Participating banks: {len(participating_banks)}")
        
        # Collect votes
        votes = {}
        vote_weights = {}
        vote_confidences = {}
        vote_reasons = {}
        
        for bank_code in participating_banks:
            bank = self.banks[bank_code]
            
            try:
                vote, confidence, reason = bank.vote_on_transaction(transaction)
                votes[bank_code] = vote
                vote_weights[bank_code] = bank.consensus_weight
                vote_confidences[bank_code] = confidence
                vote_reasons[bank_code] = reason
                
            except Exception as e:
                print(f"   ❌ {bank.bank_name} voting error: {str(e)}")
                votes[bank_code] = False
                vote_weights[bank_code] = bank.consensus_weight
                vote_confidences[bank_code] = 0.0
                vote_reasons[bank_code] = f"Error: {str(e)}"
        
        # Calculate weighted consensus
        total_weight = sum(vote_weights.values())
        approval_weight = sum(
            vote_weights[bank_code] 
            for bank_code, vote in votes.items() 
            if vote
        )
        
        approval_ratio = approval_weight / total_weight if total_weight > 0 else 0
        consensus_reached = approval_ratio >= self.approval_threshold
        
        # Analyze voting results
        approval_votes = sum(1 for vote in votes.values() if vote)
        rejection_votes = len(votes) - approval_votes
        avg_confidence = sum(vote_confidences.values()) / len(vote_confidences)
        
        print(f"\n   📊 VOTING RESULTS:")
        print(f"      Approval votes: {approval_votes}")
        print(f"      Rejection votes: {rejection_votes}")
        print(f"      Weighted approval: {approval_ratio:.2%}")
        print(f"      Average confidence: {avg_confidence:.2f}")
        print(f"      Consensus: {'✅ REACHED' if consensus_reached else '❌ FAILED'}")
        
        # Prepare result
        result = {
            "result": "approved" if consensus_reached else "rejected",
            "approval_ratio": approval_ratio,
            "approval_votes": approval_votes,
            "rejection_votes": rejection_votes,
            "average_confidence": avg_confidence,
            "participant_count": len(participating_banks),
            "vote_details": {
                bank_code: {
                    "vote": votes[bank_code],
                    "weight": vote_weights[bank_code],
                    "confidence": vote_confidences[bank_code],
                    "reason": vote_reasons[bank_code]
                }
                for bank_code in participating_banks
            }
        }
        
        return consensus_reached, result
    
    def get_rbi_approval(self, transaction: BankingTransaction) -> bool:
        """
        Get RBI approval for high-value transactions
        """
        print(f"   🏛️ Seeking RBI approval for high-value transaction...")
        
        # Simulate RBI approval process
        approval_factors = []
        
        # Check regulatory compliance
        if transaction.purpose_code:
            approval_factors.append("purpose_code_provided")
        
        if transaction.customer_id:
            approval_factors.append("customer_verified")
        
        # AML compliance
        if transaction.aml_score < 0.3:
            approval_factors.append("aml_compliant")
        
        # Transaction type appropriateness
        if transaction.tx_type == TransactionType.RTGS:
            approval_factors.append("appropriate_channel")
        
        # Risk level consideration
        if transaction.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            approval_factors.append("acceptable_risk")
        
        # Calculate approval probability
        approval_score = len(approval_factors) / 5.0  # 5 total factors
        rbi_approval_threshold = 0.6
        
        approved = approval_score >= rbi_approval_threshold
        
        print(f"   RBI Decision: {'✅ APPROVED' if approved else '❌ DENIED'} "
              f"(score: {approval_score:.2f})")
        if approval_factors:
            print(f"   Approval factors: {', '.join(approval_factors)}")
        
        return approved
    
    def process_settlement(self, transaction: BankingTransaction, consensus_result: Dict):
        """
        Process transaction settlement after consensus
        """
        if consensus_result["result"] != "approved":
            self.failed_settlements += 1
            print(f"   ❌ Settlement failed: {consensus_result['result']}")
            return False
        
        print(f"\n💰 SETTLEMENT PROCESSING")
        print("-" * 30)
        
        # Process settlement at participating banks
        sender_bank = self.banks.get(transaction.sender_bank)
        receiver_bank = self.banks.get(transaction.receiver_bank)
        
        settlement_success = True
        
        try:
            if sender_bank:
                sender_bank.process_settlement(transaction)
            
            if receiver_bank:
                receiver_bank.process_settlement(transaction)
            
            # Update transaction status
            transaction.settlement_time = time.time()
            self.processed_transactions.append(transaction)
            self.total_volume += transaction.amount
            self.successful_settlements += 1
            
            print(f"   ✅ Settlement completed successfully")
            
        except Exception as e:
            print(f"   ❌ Settlement error: {str(e)}")
            self.failed_settlements += 1
            settlement_success = False
        
        return settlement_success
    
    def simulate_banking_day(self, transactions: List[BankingTransaction]) -> Dict:
        """
        Simulate complete banking day operations
        """
        print(f"\n🌅 MUMBAI BANKING DAY SIMULATION")
        print(f"Transactions to process: {len(transactions)}")
        print("=" * 70)
        
        day_results = {
            "transactions_submitted": len(transactions),
            "transactions_processed": 0,
            "successful_settlements": 0,
            "failed_settlements": 0,
            "fraud_prevented": 0,
            "total_volume": 0.0,
            "processing_details": []
        }
        
        for idx, transaction in enumerate(transactions):
            print(f"\n{'='*50}")
            print(f"PROCESSING TRANSACTION {idx + 1}/{len(transactions)}")
            print(f"{'='*50}")
            
            # Submit transaction
            tx_id = self.submit_transaction(transaction)
            
            # Run consensus
            consensus_reached, consensus_result = self.run_consensus(transaction)
            
            # Record processing details
            processing_detail = {
                "transaction_id": transaction.tx_id,
                "amount": transaction.amount,
                "type": transaction.tx_type.value,
                "risk_level": transaction.risk_level.value,
                "consensus_reached": consensus_reached,
                "approval_ratio": consensus_result.get("approval_ratio", 0),
                "settlement_success": False
            }
            
            # Process settlement if consensus reached
            if consensus_reached:
                settlement_success = self.process_settlement(transaction, consensus_result)
                processing_detail["settlement_success"] = settlement_success
                
                if settlement_success:
                    day_results["successful_settlements"] += 1
                    day_results["total_volume"] += transaction.amount
                else:
                    day_results["failed_settlements"] += 1
            else:
                day_results["failed_settlements"] += 1
                
                # Check if fraud was prevented
                if transaction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    day_results["fraud_prevented"] += 1
            
            day_results["transactions_processed"] += 1
            day_results["processing_details"].append(processing_detail)
            
            # Brief processing delay
            time.sleep(0.3)
        
        # Update system metrics
        self.successful_settlements = day_results["successful_settlements"]
        self.failed_settlements = day_results["failed_settlements"]
        self.total_volume = day_results["total_volume"]
        
        return day_results
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        bank_stats = [bank.get_bank_stats() for bank in self.banks.values()]
        
        total_transactions = sum(bank.transactions_processed for bank in self.banks.values())
        total_consensus_participations = sum(bank.consensus_participations for bank in self.banks.values())
        
        return {
            "total_banks": len(self.banks),
            "total_volume_processed": self.total_volume,
            "successful_settlements": self.successful_settlements,
            "failed_settlements": self.failed_settlements,
            "fraud_prevented": self.fraud_prevented,
            "success_rate": (self.successful_settlements / max(1, self.successful_settlements + self.failed_settlements)) * 100,
            "total_transactions": total_transactions,
            "total_consensus_participations": total_consensus_participations,
            "average_participations_per_bank": total_consensus_participations / len(self.banks),
            "bank_details": bank_stats
        }

def create_mumbai_banking_network() -> Tuple[RBIConsensusSystem, List[IndianBank]]:
    """
    Create Mumbai banking network with major Indian banks
    """
    print("🏗️ CREATING MUMBAI BANKING NETWORK")
    print("=" * 50)
    
    # Major Indian banks
    indian_banks_data = [
        ("SBI", "State Bank of India", BankType.PUBLIC_SECTOR),
        ("HDFC", "HDFC Bank", BankType.PRIVATE_SECTOR),
        ("ICICI", "ICICI Bank", BankType.PRIVATE_SECTOR),
        ("PNB", "Punjab National Bank", BankType.PUBLIC_SECTOR),
        ("AXIS", "Axis Bank", BankType.PRIVATE_SECTOR),
        ("BOI", "Bank of India", BankType.PUBLIC_SECTOR),
        ("KOTAK", "Kotak Mahindra Bank", BankType.PRIVATE_SECTOR),
        ("CITI_FOREIGN", "Citibank India", BankType.FOREIGN),
        ("HSBC_FOREIGN", "HSBC India", BankType.FOREIGN),
        ("PAYTM", "Paytm Payments Bank", BankType.PAYMENT_BANK)
    ]
    
    banks = []
    for bank_code, bank_name, bank_type in indian_banks_data:
        bank = IndianBank(bank_code, bank_name, bank_type)
        banks.append(bank)
    
    # Create consensus system
    consensus_system = RBIConsensusSystem(banks)
    
    return consensus_system, banks

def create_sample_transactions() -> List[BankingTransaction]:
    """
    Create sample inter-bank transactions - Mumbai business day
    """
    banks = ["SBI", "HDFC", "ICICI", "PNB", "AXIS", "BOI", "KOTAK"]
    foreign_banks = ["CITI_FOREIGN", "HSBC_FOREIGN"]
    all_banks = banks + foreign_banks
    
    transactions = []
    
    # Regular transactions
    for i in range(15):
        sender = random.choice(all_banks)
        receiver = random.choice([b for b in all_banks if b != sender])
        
        tx = BankingTransaction(
            tx_id=f"TXN{datetime.now().strftime('%Y%m%d')}{i:04d}",
            tx_type=random.choice([TransactionType.NEFT, TransactionType.RTGS, TransactionType.IMPS]),
            sender_bank=sender,
            receiver_bank=receiver,
            sender_account=f"ACC{random.randint(100000, 999999)}",
            receiver_account=f"ACC{random.randint(100000, 999999)}",
            amount=random.uniform(100000, 50000000),  # 1 lakh to 5 crore
            purpose_code=f"P{random.randint(1000, 9999)}" if random.random() > 0.3 else "",
            customer_id=f"CUST{random.randint(10000, 99999)}" if random.random() > 0.2 else "",
            aml_score=random.uniform(0.0, 0.6)  # Mostly clean transactions
        )
        
        transactions.append(tx)
    
    # Add some high-risk transactions
    for i in range(3):
        tx = BankingTransaction(
            tx_id=f"HTXN{datetime.now().strftime('%Y%m%d')}{i:03d}",
            tx_type=TransactionType.WIRE_TRANSFER,
            sender_bank=random.choice(foreign_banks),
            receiver_bank=random.choice(banks),
            sender_account=f"FACC{random.randint(100000, 999999)}",
            receiver_account=f"ACC{random.randint(100000, 999999)}",
            amount=random.uniform(10000000, 200000000),  # 1 crore to 20 crore
            purpose_code="",  # Missing purpose code
            customer_id="",   # Missing customer ID
            aml_score=random.uniform(0.7, 0.9)  # High AML score
        )
        
        transactions.append(tx)
    
    return transactions

if __name__ == "__main__":
    print("🚀 INDIAN BANK CONSENSUS SYSTEM")
    print("Mumbai Inter-Bank Transaction Processing")
    print("=" * 70)
    
    try:
        # Create Mumbai banking network
        consensus_system, banks = create_mumbai_banking_network()
        
        # Show initial system state
        initial_stats = consensus_system.get_system_stats()
        print(f"\n📊 INITIAL SYSTEM STATE")
        print("-" * 40)
        print(f"Total banks: {initial_stats['total_banks']}")
        
        # Show bank details
        print(f"\n🏦 PARTICIPATING BANKS")
        print("-" * 30)
        for bank in banks[:5]:  # Show first 5 banks
            print(f"{bank.bank_name} ({bank.bank_type.value}): "
                  f"Weight {bank.consensus_weight:.2f}")
        
        # Create sample transactions
        transactions = create_sample_transactions()
        print(f"\n📝 Created {len(transactions)} sample transactions")
        
        # Simulate banking day
        day_results = consensus_system.simulate_banking_day(transactions)
        
        # Analyze results
        print(f"\n📈 BANKING DAY RESULTS")
        print("=" * 50)
        print(f"Transactions submitted: {day_results['transactions_submitted']}")
        print(f"Successful settlements: {day_results['successful_settlements']}")
        print(f"Failed settlements: {day_results['failed_settlements']}")
        print(f"Fraud prevented: {day_results['fraud_prevented']}")
        print(f"Total volume: ₹{day_results['total_volume']:,.0f}")
        print(f"Success rate: {(day_results['successful_settlements']/day_results['transactions_submitted']*100):.1f}%")
        
        # Final system statistics
        final_stats = consensus_system.get_system_stats()
        
        print(f"\n🏆 FINAL SYSTEM STATISTICS")
        print("-" * 40)
        print(f"Total volume processed: ₹{final_stats['total_volume_processed']:,.0f}")
        print(f"System success rate: {final_stats['success_rate']:.1f}%")
        print(f"Average consensus participations per bank: {final_stats['average_participations_per_bank']:.1f}")
        
        print("\n🎯 Key Insights:")
        print("• Multi-bank consensus ensures transaction integrity")
        print("• Risk-based validation prevents fraud")
        print("• RBI oversight for high-value transactions")
        print("• Weighted voting based on bank characteristics")
        print("• Like Mumbai's financial district - collaborative yet competitive!")
        
        print("\n🎊 BANKING CONSENSUS SIMULATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error in banking simulation: {e}")
        raise