#!/usr/bin/env python3
"""
Indian Banking Byzantine Fault Tolerance - Multi-Bank Consensus
Real-world application: UPI network fault tolerance and NEFT/RTGS consensus

यह implementation Indian banking ecosystem में Byzantine fault tolerance को demonstrate करती है
जैसे कि UPI में multiple PSP banks के बीच consensus की जरूरत होती है
"""

import time
import threading
import json
import hashlib
import random
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import uuid
from decimal import Decimal

class BankType(Enum):
    PUBLIC_SECTOR = "public_sector"      # SBI, PNB, etc.
    PRIVATE_SECTOR = "private_sector"    # HDFC, ICICI, etc.
    PAYMENT_BANK = "payment_bank"        # Paytm Payments Bank, etc.
    COOPERATIVE = "cooperative"          # Urban Co-op banks
    FOREIGN = "foreign"                  # Citibank, Standard Chartered

class TransactionType(Enum):
    UPI_TRANSFER = "upi_transfer"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    SETTLEMENT = "settlement"

class BankingMessageType(Enum):
    TRANSACTION_REQUEST = "transaction_request"
    VALIDATION_REQUEST = "validation_request"
    SETTLEMENT_PROPOSAL = "settlement_proposal"
    CONSENSUS_VOTE = "consensus_vote"
    FRAUD_ALERT = "fraud_alert"

@dataclass
class UPITransaction:
    """UPI transaction details"""
    transaction_id: str
    sender_vpa: str
    receiver_vpa: str
    amount: Decimal
    sender_bank: str
    receiver_bank: str
    timestamp: float
    transaction_type: TransactionType
    reference_id: str = ""
    
    def __post_init__(self):
        if not self.reference_id:
            self.reference_id = f"UPI{int(self.timestamp)}{self.transaction_id[-6:]}"

@dataclass
class BankingMessage:
    """Banking network message for consensus"""
    msg_type: BankingMessageType
    sender_bank: str
    receiver_bank: str
    transaction: Optional[UPITransaction]
    content: Dict[str, Any]
    round_number: int
    timestamp: float
    message_hash: str = ""
    
    def __post_init__(self):
        if not self.message_hash:
            # Create secure hash for message integrity
            content_str = json.dumps(self.content, sort_keys=True, default=str)
            msg_data = f"{self.msg_type.value}:{self.sender_bank}:{content_str}:{self.timestamp}"
            self.message_hash = hashlib.sha256(msg_data.encode()).hexdigest()[:16]

class IndianBankNode:
    """
    Indian Bank Node with Byzantine Fault Tolerance
    यह RBI, NPCI, और individual banks के बीच consensus maintain करता है
    """
    
    def __init__(self, bank_code: str, bank_name: str, bank_type: BankType, 
                 is_malicious: bool = False):
        self.bank_code = bank_code
        self.bank_name = bank_name
        self.bank_type = bank_type
        self.is_malicious = is_malicious
        
        # Banking state
        self.account_balances: Dict[str, Decimal] = {}  # VPA -> balance
        self.pending_transactions: Dict[str, UPITransaction] = {}
        self.settled_transactions: Set[str] = set()
        self.blocked_accounts: Set[str] = set()
        
        # Consensus state
        self.current_round = 0
        self.votes_received: Dict[int, Dict[str, Any]] = {}  # round -> bank -> vote
        self.consensus_decisions: Dict[str, bool] = {}  # transaction_id -> approved
        
        # Network and fraud detection
        self.network: Dict[str, 'IndianBankNode'] = {}
        self.fraud_patterns: Dict[str, int] = {}  # pattern -> count
        self.daily_limits: Dict[str, Decimal] = {}  # VPA -> daily limit used
        
        # Byzantine behavior parameters
        self.malicious_probability = 0.8 if is_malicious else 0.0
        
        # Performance metrics
        self.transactions_processed = 0
        self.fraud_attempts_blocked = 0
        self.consensus_rounds_participated = 0
        
        print(f"🏦 Bank {bank_code} ({bank_name}) initialized - Type: {bank_type.value}")
        if is_malicious:
            print(f"⚠️ WARNING: {bank_code} configured as malicious node")
    
    def set_network(self, network: Dict[str, 'IndianBankNode']):
        """Set banking network connections"""
        self.network = network
    
    def create_account(self, vpa: str, initial_balance: Decimal = Decimal('0')):
        """Create new UPI account"""
        self.account_balances[vpa] = initial_balance
        self.daily_limits[vpa] = Decimal('0')
        print(f"💳 Bank {self.bank_code}: Created account {vpa} with balance ₹{initial_balance}")
    
    def initiate_upi_transaction(self, transaction: UPITransaction) -> bool:
        """
        Initiate UPI transaction with Byzantine consensus
        यह function UPI transaction को initiate करता है और consensus के लिए भेजता है
        """
        print(f"\n💸 Bank {self.bank_code}: Initiating UPI transaction")
        print(f"   From: {transaction.sender_vpa} (₹{transaction.amount})")
        print(f"   To: {transaction.receiver_vpa}")
        print(f"   Transaction ID: {transaction.transaction_id}")
        
        # Pre-validation checks
        if not self.validate_transaction_locally(transaction):
            print(f"❌ Local validation failed for transaction {transaction.transaction_id}")
            return False
        
        # Add to pending
        self.pending_transactions[transaction.transaction_id] = transaction
        
        # Start Byzantine consensus for transaction approval
        return self.start_transaction_consensus(transaction)
    
    def validate_transaction_locally(self, transaction: UPITransaction) -> bool:
        """Local transaction validation before consensus"""
        sender_vpa = transaction.sender_vpa
        amount = transaction.amount
        
        # Check account exists
        if sender_vpa not in self.account_balances:
            print(f"❌ Sender account {sender_vpa} not found")
            return False
        
        # Check sufficient balance
        if self.account_balances[sender_vpa] < amount:
            print(f"❌ Insufficient balance: ₹{self.account_balances[sender_vpa]} < ₹{amount}")
            return False
        
        # Check daily limits
        current_daily_usage = self.daily_limits.get(sender_vpa, Decimal('0'))
        if current_daily_usage + amount > Decimal('100000'):  # ₹1 lakh daily limit
            print(f"❌ Daily limit exceeded: ₹{current_daily_usage + amount}")
            return False
        
        # Check for blocked accounts
        if sender_vpa in self.blocked_accounts or transaction.receiver_vpa in self.blocked_accounts:
            print(f"❌ Blocked account involved in transaction")
            return False
        
        # Fraud pattern detection
        fraud_score = self.calculate_fraud_score(transaction)
        if fraud_score > 0.7:  # High fraud probability
            print(f"🚨 High fraud score detected: {fraud_score}")
            return False
        
        return True
    
    def calculate_fraud_score(self, transaction: UPITransaction) -> float:
        """Calculate fraud probability score"""
        fraud_score = 0.0
        
        # Check amount patterns
        if transaction.amount > Decimal('50000'):  # High value transaction
            fraud_score += 0.3
        
        # Check time patterns (late night transactions are suspicious)
        current_hour = time.localtime(transaction.timestamp).tm_hour
        if current_hour < 6 or current_hour > 23:
            fraud_score += 0.2
        
        # Check frequency patterns
        sender_pattern_key = f"sender:{transaction.sender_vpa}:hourly"
        current_count = self.fraud_patterns.get(sender_pattern_key, 0)
        if current_count > 10:  # More than 10 transactions per hour
            fraud_score += 0.4
        
        return min(fraud_score, 1.0)
    
    def start_transaction_consensus(self, transaction: UPITransaction) -> bool:
        """Start Byzantine consensus for transaction approval"""
        self.current_round += 1
        round_number = self.current_round
        
        print(f"🎯 Starting consensus round {round_number} for transaction {transaction.transaction_id}")
        
        # Prepare consensus message
        consensus_message = BankingMessage(
            msg_type=BankingMessageType.VALIDATION_REQUEST,
            sender_bank=self.bank_code,
            receiver_bank="ALL",
            transaction=transaction,
            content={
                "action": "validate_transaction",
                "transaction_id": transaction.transaction_id,
                "amount": str(transaction.amount),
                "fraud_score": self.calculate_fraud_score(transaction)
            },
            round_number=round_number,
            timestamp=time.time()
        )
        
        # Broadcast to all banks in network
        self.broadcast_consensus_message(consensus_message)
        
        # Wait for responses
        time.sleep(1)
        
        # Count votes
        return self.count_consensus_votes(round_number, transaction.transaction_id)
    
    def broadcast_consensus_message(self, message: BankingMessage):
        """Broadcast consensus message to all banks"""
        for bank_code, bank in self.network.items():
            if bank_code != self.bank_code:
                # Simulate malicious behavior
                if self.is_malicious and random.random() < self.malicious_probability:
                    # Send corrupted message
                    corrupted_message = self.corrupt_message(message)
                    threading.Thread(target=bank.receive_consensus_message, args=(corrupted_message,)).start()
                    print(f"💀 Malicious bank {self.bank_code}: Sent corrupted message to {bank_code}")
                else:
                    threading.Thread(target=bank.receive_consensus_message, args=(message,)).start()
    
    def corrupt_message(self, message: BankingMessage) -> BankingMessage:
        """Corrupt message for Byzantine behavior"""
        if message.transaction:
            # Change amount to create double-spending
            corrupted_transaction = UPITransaction(
                transaction_id=message.transaction.transaction_id,
                sender_vpa=message.transaction.sender_vpa,
                receiver_vpa="malicious@fakebank",  # Divert to malicious account
                amount=message.transaction.amount * 2,  # Double the amount
                sender_bank=message.transaction.sender_bank,
                receiver_bank="FAKE001",
                timestamp=message.transaction.timestamp,
                transaction_type=message.transaction.transaction_type
            )
            
            corrupted_content = message.content.copy()
            corrupted_content["amount"] = str(corrupted_transaction.amount)
            corrupted_content["malicious_flag"] = True
            
            return BankingMessage(
                msg_type=message.msg_type,
                sender_bank=message.sender_bank,
                receiver_bank=message.receiver_bank,
                transaction=corrupted_transaction,
                content=corrupted_content,
                round_number=message.round_number,
                timestamp=message.timestamp
            )
        
        return message
    
    def receive_consensus_message(self, message: BankingMessage):
        """Receive and process consensus message"""
        if message.msg_type == BankingMessageType.VALIDATION_REQUEST:
            self.handle_validation_request(message)
    
    def handle_validation_request(self, message: BankingMessage):
        """Handle transaction validation request"""
        transaction = message.transaction
        round_number = message.round_number
        
        print(f"📨 Bank {self.bank_code}: Received validation request from {message.sender_bank}")
        
        # Validate transaction
        vote_decision = self.validate_transaction_for_consensus(transaction, message.content)
        
        # Send vote back
        vote_message = BankingMessage(
            msg_type=BankingMessageType.CONSENSUS_VOTE,
            sender_bank=self.bank_code,
            receiver_bank=message.sender_bank,
            transaction=transaction,
            content={
                "vote": vote_decision,
                "transaction_id": transaction.transaction_id,
                "round_number": round_number,
                "validation_details": self.get_validation_details(transaction)
            },
            round_number=round_number,
            timestamp=time.time()
        )
        
        # Send vote
        if message.sender_bank in self.network:
            initiating_bank = self.network[message.sender_bank]
            threading.Thread(target=initiating_bank.receive_consensus_vote, args=(vote_message,)).start()
    
    def validate_transaction_for_consensus(self, transaction: UPITransaction, 
                                         message_content: Dict[str, Any]) -> bool:
        """Validate transaction during consensus"""
        # Check for malicious indicators
        if message_content.get("malicious_flag", False):
            print(f"🚨 Bank {self.bank_code}: Detected malicious transaction flag")
            return False
        
        # Validate receiver bank
        if transaction.receiver_bank == "FAKE001":
            print(f"🚨 Bank {self.bank_code}: Detected fake receiver bank")
            return False
        
        # Check amount consistency
        reported_amount = Decimal(message_content.get("amount", "0"))
        if reported_amount != transaction.amount:
            print(f"🚨 Bank {self.bank_code}: Amount mismatch detected")
            return False
        
        # Check fraud score
        fraud_score = float(message_content.get("fraud_score", 0))
        if fraud_score > 0.8:  # Very high fraud score
            print(f"🚨 Bank {self.bank_code}: High fraud score: {fraud_score}")
            return False
        
        # Additional checks based on bank type
        if self.bank_type == BankType.PAYMENT_BANK and transaction.amount > Decimal('200000'):
            # Payment banks might have stricter limits
            print(f"⚠️ Payment bank {self.bank_code}: Amount exceeds payment bank limits")
            return False
        
        # Malicious bank might vote randomly
        if self.is_malicious and random.random() < self.malicious_probability:
            malicious_vote = random.choice([True, False])
            print(f"💀 Malicious bank {self.bank_code}: Random vote: {malicious_vote}")
            return malicious_vote
        
        print(f"✅ Bank {self.bank_code}: Transaction validated successfully")
        return True
    
    def get_validation_details(self, transaction: UPITransaction) -> Dict[str, Any]:
        """Get detailed validation information"""
        return {
            "bank_type": self.bank_type.value,
            "risk_assessment": "low" if transaction.amount < Decimal('10000') else "medium",
            "validation_timestamp": time.time(),
            "validator_bank": self.bank_code
        }
    
    def receive_consensus_vote(self, message: BankingMessage):
        """Receive consensus vote from other bank"""
        round_number = message.round_number
        voter_bank = message.sender_bank
        vote = message.content["vote"]
        
        print(f"📊 Bank {self.bank_code}: Received vote from {voter_bank}: {'APPROVE' if vote else 'REJECT'}")
        
        # Store vote
        if round_number not in self.votes_received:
            self.votes_received[round_number] = {}
        
        self.votes_received[round_number][voter_bank] = {
            "vote": vote,
            "details": message.content.get("validation_details", {}),
            "timestamp": message.timestamp
        }
    
    def count_consensus_votes(self, round_number: int, transaction_id: str) -> bool:
        """Count votes and make consensus decision"""
        if round_number not in self.votes_received:
            print(f"❌ No votes received for round {round_number}")
            return False
        
        votes = self.votes_received[round_number]
        approve_votes = sum(1 for vote_info in votes.values() if vote_info["vote"])
        reject_votes = len(votes) - approve_votes
        total_voters = len(self.network)  # All other banks
        
        print(f"\n📊 Consensus Results for Transaction {transaction_id}:")
        print(f"   Total voters: {total_voters}")
        print(f"   Votes received: {len(votes)}")
        print(f"   Approve: {approve_votes}")
        print(f"   Reject: {reject_votes}")
        
        # Byzantine fault tolerance: need majority approval
        required_majority = (total_voters // 2) + 1
        
        if approve_votes >= required_majority:
            print(f"✅ Transaction APPROVED by consensus (majority: {approve_votes}/{total_voters})")
            self.consensus_decisions[transaction_id] = True
            self.execute_approved_transaction(transaction_id)
            return True
        else:
            print(f"❌ Transaction REJECTED by consensus")
            self.consensus_decisions[transaction_id] = False
            self.reject_transaction(transaction_id)
            return False
    
    def execute_approved_transaction(self, transaction_id: str):
        """Execute transaction after consensus approval"""
        if transaction_id not in self.pending_transactions:
            return
        
        transaction = self.pending_transactions[transaction_id]
        
        # Debit sender account
        if transaction.sender_vpa in self.account_balances:
            self.account_balances[transaction.sender_vpa] -= transaction.amount
            
            # Update daily limits
            if transaction.sender_vpa not in self.daily_limits:
                self.daily_limits[transaction.sender_vpa] = Decimal('0')
            self.daily_limits[transaction.sender_vpa] += transaction.amount
            
            print(f"💰 Debited ₹{transaction.amount} from {transaction.sender_vpa}")
            print(f"   New balance: ₹{self.account_balances[transaction.sender_vpa]}")
        
        # Move to settled
        self.settled_transactions.add(transaction_id)
        del self.pending_transactions[transaction_id]
        self.transactions_processed += 1
        
        print(f"✅ Transaction {transaction_id} executed successfully")
        
        # Notify receiver bank (if in network)
        receiver_bank = transaction.receiver_bank
        if receiver_bank in self.network:
            receiver = self.network[receiver_bank]
            receiver.credit_account(transaction.receiver_vpa, transaction.amount, transaction_id)
    
    def credit_account(self, vpa: str, amount: Decimal, transaction_id: str):
        """Credit account from external transaction"""
        if vpa not in self.account_balances:
            self.account_balances[vpa] = Decimal('0')
        
        self.account_balances[vpa] += amount
        self.settled_transactions.add(transaction_id)
        
        print(f"💰 Bank {self.bank_code}: Credited ₹{amount} to {vpa}")
        print(f"   New balance: ₹{self.account_balances[vpa]}")
    
    def reject_transaction(self, transaction_id: str):
        """Reject transaction after consensus"""
        if transaction_id in self.pending_transactions:
            transaction = self.pending_transactions[transaction_id]
            del self.pending_transactions[transaction_id]
            
            print(f"❌ Transaction {transaction_id} rejected and removed from pending")
            
            # Could notify customer about rejection
            print(f"📱 Customer notification: Transaction from {transaction.sender_vpa} rejected by network")
    
    def get_banking_status(self) -> Dict[str, Any]:
        """Get comprehensive banking status"""
        total_balance = sum(self.account_balances.values())
        
        return {
            "bank_code": self.bank_code,
            "bank_name": self.bank_name,
            "bank_type": self.bank_type.value,
            "is_malicious": self.is_malicious,
            "total_accounts": len(self.account_balances),
            "total_balance": str(total_balance),
            "transactions_processed": self.transactions_processed,
            "pending_transactions": len(self.pending_transactions),
            "settled_transactions": len(self.settled_transactions),
            "fraud_attempts_blocked": self.fraud_attempts_blocked,
            "consensus_rounds": self.consensus_rounds_participated
        }

def simulate_indian_banking_consensus():
    """
    Simulate Indian Banking Network with Byzantine Fault Tolerance
    यह simulation UPI network में consensus और fraud prevention को demonstrate करता है
    """
    print("🇮🇳 Indian Banking Byzantine Consensus - UPI Network Simulation")
    print("🏦 Scenario: Multi-bank UPI transaction processing with fault tolerance")
    print("=" * 80)
    
    # Create Indian banking network
    indian_banks = {
        "SBI001": IndianBankNode("SBI001", "State Bank of India", BankType.PUBLIC_SECTOR),
        "HDFC01": IndianBankNode("HDFC01", "HDFC Bank", BankType.PRIVATE_SECTOR),
        "ICICI01": IndianBankNode("ICICI01", "ICICI Bank", BankType.PRIVATE_SECTOR),
        "PAYTM01": IndianBankNode("PAYTM01", "Paytm Payments Bank", BankType.PAYMENT_BANK),
        "AXIS001": IndianBankNode("AXIS001", "Axis Bank", BankType.PRIVATE_SECTOR, is_malicious=True),  # Byzantine node
        "PNB0001": IndianBankNode("PNB0001", "Punjab National Bank", BankType.PUBLIC_SECTOR)
    }
    
    # Set network connections
    for bank in indian_banks.values():
        bank.set_network(indian_banks)
    
    print(f"\n🏦 Indian Banking Network ({len(indian_banks)} banks):")
    for bank_code, bank in indian_banks.items():
        status = "MALICIOUS" if bank.is_malicious else "TRUSTED"
        print(f"   {bank_code}: {bank.bank_name} ({bank.bank_type.value}) - {status}")
    
    # Create customer accounts across different banks
    print(f"\n💳 Setting up customer accounts...")
    
    # SBI accounts
    indian_banks["SBI001"].create_account("rahul@sbi", Decimal('50000'))
    indian_banks["SBI001"].create_account("priya@sbi", Decimal('75000'))
    
    # HDFC accounts
    indian_banks["HDFC01"].create_account("amit@hdfc", Decimal('120000'))
    indian_banks["HDFC01"].create_account("sneha@hdfc", Decimal('60000'))
    
    # ICICI accounts
    indian_banks["ICICI01"].create_account("rajesh@icici", Decimal('90000'))
    
    # Paytm Payments Bank
    indian_banks["PAYTM01"].create_account("mobile123@paytm", Decimal('25000'))
    
    # PNB accounts
    indian_banks["PNB0001"].create_account("vikash@pnb", Decimal('80000'))
    
    # Simulate UPI transactions
    print(f"\n💸 Processing UPI transactions through Byzantine consensus...")
    
    upi_transactions = [
        UPITransaction(
            transaction_id="UPI2024001",
            sender_vpa="rahul@sbi",
            receiver_vpa="amit@hdfc", 
            amount=Decimal('15000'),
            sender_bank="SBI001",
            receiver_bank="HDFC01",
            timestamp=time.time(),
            transaction_type=TransactionType.UPI_TRANSFER
        ),
        UPITransaction(
            transaction_id="UPI2024002",
            sender_vpa="priya@sbi",
            receiver_vpa="mobile123@paytm",
            amount=Decimal('5000'),
            sender_bank="SBI001", 
            receiver_bank="PAYTM01",
            timestamp=time.time(),
            transaction_type=TransactionType.UPI_TRANSFER
        ),
        UPITransaction(
            transaction_id="UPI2024003",
            sender_vpa="sneha@hdfc",
            receiver_vpa="rajesh@icici",
            amount=Decimal('25000'),
            sender_bank="HDFC01",
            receiver_bank="ICICI01", 
            timestamp=time.time(),
            transaction_type=TransactionType.UPI_TRANSFER
        ),
        # Suspicious high-value transaction
        UPITransaction(
            transaction_id="UPI2024004",
            sender_vpa="vikash@pnb",
            receiver_vpa="amit@hdfc",
            amount=Decimal('95000'),  # Very high amount
            sender_bank="PNB0001",
            receiver_bank="HDFC01",
            timestamp=time.time(),
            transaction_type=TransactionType.UPI_TRANSFER
        )
    ]
    
    # Process each transaction
    for i, transaction in enumerate(upi_transactions):
        print(f"\n{'='*60}")
        print(f"🔄 UPI Transaction {i+1}/{len(upi_transactions)}")
        print(f"💳 {transaction.sender_vpa} → {transaction.receiver_vpa}: ₹{transaction.amount}")
        
        # Find sender bank and initiate transaction
        sender_bank_obj = indian_banks[transaction.sender_bank]
        success = sender_bank_obj.initiate_upi_transaction(transaction)
        
        if success:
            print(f"✅ Transaction processed successfully")
        else:
            print(f"❌ Transaction failed")
        
        # Wait between transactions
        time.sleep(2)
    
    # Wait for all consensus to complete
    print(f"\n⏳ Waiting for all consensus rounds to complete...")
    time.sleep(3)
    
    # Show final banking network state
    print(f"\n💰 Final Banking Network State:")
    print("=" * 80)
    
    for bank_code, bank in indian_banks.items():
        status = bank.get_banking_status()
        
        print(f"\n🏦 {status['bank_name']} ({bank_code})")
        print(f"   Type: {status['bank_type']}")
        print(f"   Status: {'BYZANTINE' if status['is_malicious'] else 'HONEST'}")
        print(f"   Total accounts: {status['total_accounts']}")
        print(f"   Total balance: ₹{status['total_balance']}")
        print(f"   Transactions processed: {status['transactions_processed']}")
        print(f"   Pending transactions: {status['pending_transactions']}")
        
        # Show account balances
        if bank.account_balances:
            print(f"   Account balances:")
            for vpa, balance in bank.account_balances.items():
                print(f"     {vpa}: ₹{balance}")
    
    # Network-wide statistics
    print(f"\n📊 UPI Network Statistics:")
    total_transactions = sum(bank.transactions_processed for bank in indian_banks.values())
    total_pending = sum(len(bank.pending_transactions) for bank in indian_banks.values())
    total_settled = sum(len(bank.settled_transactions) for bank in indian_banks.values())
    
    print(f"   Total transactions processed: {total_transactions}")
    print(f"   Total pending transactions: {total_pending}")
    print(f"   Total settled transactions: {total_settled}")
    print(f"   Byzantine nodes in network: 1/{len(indian_banks)}")
    print(f"   Fault tolerance: {(len(indian_banks) - 1) // 3} Byzantine nodes")
    
    # Verify network integrity
    honest_banks = [bank for bank in indian_banks.values() if not bank.is_malicious]
    if len(honest_banks) >= 2 * ((len(indian_banks) - 1) // 3) + 1:
        print(f"✅ Network maintains Byzantine fault tolerance")
        print(f"🛡️ System can tolerate up to {(len(indian_banks) - 1) // 3} malicious banks")
    else:
        print(f"⚠️ Network Byzantine fault tolerance compromised")

def simulate_settlement_consensus():
    """
    Simulate daily settlement consensus among banks
    यह example end-of-day settlement में banks के बीच consensus को show करता है
    """
    print("\n" + "="*80)
    print("🇮🇳 Daily Settlement Consensus - RBI Settlement System")
    print("=" * 80)
    
    # Simplified settlement scenario
    settlement_banks = {
        "RBI001": IndianBankNode("RBI001", "Reserve Bank of India", BankType.PUBLIC_SECTOR),
        "SBI001": IndianBankNode("SBI001", "State Bank of India", BankType.PUBLIC_SECTOR),
        "HDFC01": IndianBankNode("HDFC01", "HDFC Bank", BankType.PRIVATE_SECTOR),
        "ICICI01": IndianBankNode("ICICI01", "ICICI Bank", BankType.PRIVATE_SECTOR, is_malicious=True)
    }
    
    for bank in settlement_banks.values():
        bank.set_network(settlement_banks)
    
    print(f"\n🏛️ Settlement Network: RBI + {len(settlement_banks)-1} commercial banks")
    
    # Simulate settlement amounts
    settlement_data = {
        "SBI001": {"net_position": Decimal('50000000'), "transactions": 125000},  # ₹5 crore net credit
        "HDFC01": {"net_position": Decimal('-30000000'), "transactions": 98000},  # ₹3 crore net debit
        "ICICI01": {"net_position": Decimal('-20000000'), "transactions": 87000}  # ₹2 crore net debit
    }
    
    print(f"\n💹 End-of-Day Settlement Positions:")
    for bank_code, data in settlement_data.items():
        position = "CREDIT" if data["net_position"] > 0 else "DEBIT"
        print(f"   {bank_code}: ₹{abs(data['net_position']):,} {position} ({data['transactions']:,} txns)")
    
    # RBI initiates settlement consensus
    rbi = settlement_banks["RBI001"]
    settlement_transaction = UPITransaction(
        transaction_id="SETTLEMENT2024001",
        sender_vpa="settlement@rbi",
        receiver_vpa="clearing@rbi", 
        amount=sum(abs(data["net_position"]) for data in settlement_data.values()),
        sender_bank="RBI001",
        receiver_bank="RBI001",
        timestamp=time.time(),
        transaction_type=TransactionType.SETTLEMENT
    )
    
    print(f"\n🎯 RBI initiating daily settlement consensus...")
    success = rbi.initiate_upi_transaction(settlement_transaction)
    
    if success:
        print(f"✅ Daily settlement completed successfully")
    else:
        print(f"❌ Settlement consensus failed")

if __name__ == "__main__":
    # Run Indian banking consensus simulation
    simulate_indian_banking_consensus()
    
    # Run settlement consensus simulation  
    simulate_settlement_consensus()
    
    print("\n" + "="*80)
    print("🇮🇳 Indian Banking Byzantine Fault Tolerance Benefits:")
    print("1. Protects UPI network from malicious Payment Service Providers")
    print("2. Ensures transaction integrity across bank boundaries") 
    print("3. Prevents double-spending and fraud through consensus")
    print("4. Maintains network operation despite compromised banks")
    print("5. Enables secure inter-bank settlement")
    print("6. Supports regulatory compliance through distributed validation")
    print("7. Provides audit trail for RBI oversight")