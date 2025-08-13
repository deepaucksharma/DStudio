#!/usr/bin/env python3
"""
Paytm Distributed Consensus System for UPI Transactions
Episode 45: Distributed Computing at Scale

यह example Paytm का distributed consensus system दिखाता है
UPI payment processing के लिए multi-node agreement, transaction
consistency, और fault tolerance के साथ।

Production Stats:
- Paytm: 1.4 billion+ transactions per month
- UPI volume: ₹10+ lakh crore monthly
- Transaction success rate: 99.5%+
- Processing latency: <2 seconds
- Node consensus time: <100ms
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import base64

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionType(Enum):
    UPI_P2P = "UPI_P2P"           # Person to Person
    UPI_P2M = "UPI_P2M"           # Person to Merchant
    WALLET_TRANSFER = "WALLET_TRANSFER"
    BANK_TRANSFER = "BANK_TRANSFER"
    RECHARGE = "RECHARGE"
    BILL_PAYMENT = "BILL_PAYMENT"

class TransactionStatus(Enum):
    INITIATED = "INITIATED"
    VALIDATED = "VALIDATED"
    CONSENSUS_PENDING = "CONSENSUS_PENDING"
    CONSENSUS_ACHIEVED = "CONSENSUS_ACHIEVED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    DISPUTED = "DISPUTED"

class NodeState(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"
    OFFLINE = "OFFLINE"

@dataclass
class UPITransaction:
    """UPI transaction with Indian payment system specifics"""
    transaction_id: str
    upi_transaction_id: str  # UPI reference number
    payer_vpa: str           # Virtual Payment Address
    payee_vpa: str
    amount: float
    currency: str = "INR"
    transaction_type: TransactionType = TransactionType.UPI_P2P
    status: TransactionStatus = TransactionStatus.INITIATED
    timestamp: datetime = None
    expiry_time: datetime = None
    merchant_id: Optional[str] = None
    reference_id: Optional[str] = None
    description: str = ""
    
    # Bank details
    payer_account_number: str = ""
    payer_ifsc: str = ""
    payee_account_number: str = ""
    payee_ifsc: str = ""
    
    # Validation flags
    otp_verified: bool = False
    biometric_verified: bool = False
    daily_limit_checked: bool = False
    fraud_check_passed: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.expiry_time is None:
            self.expiry_time = self.timestamp + timedelta(minutes=5)  # 5 min expiry

@dataclass
class ConsensusProposal:
    """Consensus proposal for transaction processing"""
    proposal_id: str
    transaction_id: str
    proposed_action: str  # APPROVE, REJECT, HOLD
    proposer_node_id: str
    timestamp: datetime
    round_number: int
    votes_received: Set[str]
    approved_by: Set[str]
    rejected_by: Set[str]
    
    def __post_init__(self):
        if not isinstance(self.votes_received, set):
            self.votes_received = set()
        if not isinstance(self.approved_by, set):
            self.approved_by = set()
        if not isinstance(self.rejected_by, set):
            self.rejected_by = set()

@dataclass
class NodeInfo:
    """Information about a consensus node"""
    node_id: str
    endpoint: str
    region: str
    is_active: bool
    last_heartbeat: datetime
    current_term: int
    voted_for: Optional[str]
    state: NodeState
    transactions_processed: int
    consensus_rounds_participated: int

class TransactionValidator:
    """Validates UPI transactions according to RBI guidelines"""
    
    def __init__(self):
        # Daily transaction limits (in INR)
        self.daily_limits = {
            "UPI_P2P": 100000,      # ₹1 lakh per day
            "UPI_P2M": 200000,      # ₹2 lakh per day
            "WALLET_TRANSFER": 50000, # ₹50,000 per day
        }
        
        # Per transaction limits
        self.per_transaction_limits = {
            "UPI_P2P": 100000,      # ₹1 lakh per transaction
            "UPI_P2M": 200000,      # ₹2 lakh per transaction
            "WALLET_TRANSFER": 25000, # ₹25,000 per transaction
        }
        
        # Fraud detection patterns
        self.fraud_patterns = {
            "suspicious_amount": [1, 11, 111, 1111],  # Common fraud amounts
            "velocity_threshold": 10,  # Max 10 transactions per minute
            "night_hour_limit": 5000,  # ₹5000 limit between 11 PM - 6 AM
        }
    
    def validate_transaction(self, transaction: UPITransaction) -> Tuple[bool, List[str]]:
        """Comprehensive transaction validation"""
        errors = []
        
        # Basic validations
        if transaction.amount <= 0:
            errors.append("Invalid transaction amount")
        
        if transaction.amount > self.per_transaction_limits.get(transaction.transaction_type.value, 100000):
            errors.append(f"Amount exceeds per-transaction limit")
        
        # VPA format validation
        if not self._validate_vpa(transaction.payer_vpa):
            errors.append("Invalid payer VPA format")
        
        if not self._validate_vpa(transaction.payee_vpa):
            errors.append("Invalid payee VPA format")
        
        # Time-based validations
        current_time = datetime.now()
        if transaction.expiry_time < current_time:
            errors.append("Transaction has expired")
        
        # Night hour restrictions
        if 23 <= current_time.hour or current_time.hour <= 6:
            if transaction.amount > self.fraud_patterns["night_hour_limit"]:
                errors.append("Amount exceeds night hour limit")
        
        # Fraud detection
        if transaction.amount in self.fraud_patterns["suspicious_amount"]:
            errors.append("Suspicious transaction amount detected")
        
        # IFSC validation for bank transfers
        if transaction.transaction_type in [TransactionType.UPI_P2P, TransactionType.UPI_P2M]:
            if not self._validate_ifsc(transaction.payer_ifsc):
                errors.append("Invalid payer IFSC code")
            if not self._validate_ifsc(transaction.payee_ifsc):
                errors.append("Invalid payee IFSC code")
        
        return len(errors) == 0, errors
    
    def _validate_vpa(self, vpa: str) -> bool:
        """Validate Virtual Payment Address format"""
        if not vpa or '@' not in vpa:
            return False
        
        parts = vpa.split('@')
        if len(parts) != 2:
            return False
        
        username, psp = parts
        
        # Username should be alphanumeric with some special chars
        if not username or len(username) < 3:
            return False
        
        # PSP should be valid (simplified check)
        valid_psps = ['paytm', 'phonepe', 'googlepay', 'amazonpay', 'okaxis', 'ybl', 'ibl']
        return psp.lower() in valid_psps
    
    def _validate_ifsc(self, ifsc: str) -> bool:
        """Validate IFSC code format"""
        if not ifsc or len(ifsc) != 11:
            return False
        
        # First 4 chars should be bank code (letters)
        if not ifsc[:4].isalpha():
            return False
        
        # 5th char should be 0
        if ifsc[4] != '0':
            return False
        
        # Last 6 chars should be alphanumeric
        if not ifsc[5:].isalnum():
            return False
        
        return True

class PaytmConsensusNode:
    """Individual node in Paytm's distributed consensus system"""
    
    def __init__(self, node_id: str, region: str, peer_nodes: List[str]):
        self.node_info = NodeInfo(
            node_id=node_id,
            endpoint=f"https://{node_id}.paytm.com",
            region=region,
            is_active=True,
            last_heartbeat=datetime.now(),
            current_term=0,
            voted_for=None,
            state=NodeState.FOLLOWER,
            transactions_processed=0,
            consensus_rounds_participated=0
        )
        
        self.peer_nodes = set(peer_nodes)
        self.validator = TransactionValidator()
        
        # Consensus state
        self.current_proposals = {}  # proposal_id -> ConsensusProposal
        self.transaction_log = []    # Committed transactions
        self.pending_transactions = {}  # transaction_id -> UPITransaction
        
        # Performance metrics
        self.consensus_latencies = deque(maxlen=1000)
        self.validation_times = deque(maxlen=1000)
        
        # Leader election
        self.leader_id = None
        self.election_timeout = 5.0  # seconds
        self.last_heartbeat_received = time.time()
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info(f"🏛️ Consensus node {node_id} initialized in {region}")
    
    async def process_transaction(self, transaction: UPITransaction) -> Dict[str, Any]:
        """Process UPI transaction through consensus"""
        start_time = time.time()
        
        try:
            with self.lock:
                # Store pending transaction
                self.pending_transactions[transaction.transaction_id] = transaction
                transaction.status = TransactionStatus.VALIDATED
            
            # Validate transaction
            validation_start = time.time()
            is_valid, errors = self.validator.validate_transaction(transaction)
            validation_time = (time.time() - validation_start) * 1000
            self.validation_times.append(validation_time)
            
            if not is_valid:
                transaction.status = TransactionStatus.FAILED
                return {
                    "transaction_id": transaction.transaction_id,
                    "status": transaction.status.value,
                    "errors": errors,
                    "processing_time_ms": (time.time() - start_time) * 1000
                }
            
            # Create consensus proposal
            proposal = self._create_consensus_proposal(transaction, "APPROVE")
            
            # Start consensus round
            consensus_result = await self._run_consensus_round(proposal)
            
            # Update transaction status based on consensus
            if consensus_result["consensus_achieved"]:
                if consensus_result["decision"] == "APPROVE":
                    transaction.status = TransactionStatus.SUCCESS
                    self._commit_transaction(transaction)
                else:
                    transaction.status = TransactionStatus.FAILED
            else:
                transaction.status = TransactionStatus.TIMEOUT
            
            processing_time = (time.time() - start_time) * 1000
            self.consensus_latencies.append(processing_time)
            
            # Update metrics
            self.node_info.transactions_processed += 1
            
            return {
                "transaction_id": transaction.transaction_id,
                "status": transaction.status.value,
                "consensus_achieved": consensus_result["consensus_achieved"],
                "participating_nodes": consensus_result["participating_nodes"],
                "processing_time_ms": processing_time,
                "validation_time_ms": validation_time
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing transaction {transaction.transaction_id}: {e}")
            transaction.status = TransactionStatus.FAILED
            return {
                "transaction_id": transaction.transaction_id,
                "status": "ERROR",
                "error": str(e)
            }
    
    def _create_consensus_proposal(self, transaction: UPITransaction, action: str) -> ConsensusProposal:
        """Create consensus proposal for transaction"""
        proposal = ConsensusProposal(
            proposal_id=str(uuid.uuid4()),
            transaction_id=transaction.transaction_id,
            proposed_action=action,
            proposer_node_id=self.node_info.node_id,
            timestamp=datetime.now(),
            round_number=1,
            votes_received=set(),
            approved_by=set(),
            rejected_by=set()
        )
        
        self.current_proposals[proposal.proposal_id] = proposal
        return proposal
    
    async def _run_consensus_round(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Run consensus round using modified PBFT algorithm"""
        consensus_start = time.time()
        
        # Phase 1: Prepare - Send proposal to all nodes
        prepare_responses = await self._send_prepare_messages(proposal)
        
        # Phase 2: Commit - If majority agreed, send commit messages
        if len(prepare_responses["approved"]) > len(self.peer_nodes) // 2:
            commit_responses = await self._send_commit_messages(proposal)
            
            consensus_achieved = len(commit_responses["committed"]) > len(self.peer_nodes) // 2
            decision = "APPROVE" if consensus_achieved else "REJECT"
        else:
            consensus_achieved = False
            decision = "REJECT"
            commit_responses = {"committed": set(), "rejected": set()}
        
        consensus_time = (time.time() - consensus_start) * 1000
        
        # Update proposal state
        proposal.votes_received = prepare_responses["approved"] | prepare_responses["rejected"]
        proposal.approved_by = commit_responses.get("committed", set())
        proposal.rejected_by = commit_responses.get("rejected", set())
        
        self.node_info.consensus_rounds_participated += 1
        
        return {
            "consensus_achieved": consensus_achieved,
            "decision": decision,
            "participating_nodes": list(prepare_responses["approved"] | prepare_responses["rejected"]),
            "consensus_time_ms": consensus_time,
            "prepare_phase": prepare_responses,
            "commit_phase": commit_responses
        }
    
    async def _send_prepare_messages(self, proposal: ConsensusProposal) -> Dict[str, Set[str]]:
        """Send prepare messages to peer nodes (simulated)"""
        approved = set()
        rejected = set()
        
        # Add own vote
        approved.add(self.node_info.node_id)
        
        # Simulate sending to peer nodes
        for peer_node_id in self.peer_nodes:
            # Simulate network delay
            await asyncio.sleep(0.001)  # 1ms
            
            # Simulate peer response (in real system, this would be network call)
            if self._simulate_peer_response(peer_node_id, proposal):
                approved.add(peer_node_id)
            else:
                rejected.add(peer_node_id)
        
        return {"approved": approved, "rejected": rejected}
    
    async def _send_commit_messages(self, proposal: ConsensusProposal) -> Dict[str, Set[str]]:
        """Send commit messages to peer nodes (simulated)"""
        committed = set()
        rejected = set()
        
        # Add own commit
        committed.add(self.node_info.node_id)
        
        # Simulate sending to peer nodes
        for peer_node_id in self.peer_nodes:
            # Simulate network delay
            await asyncio.sleep(0.001)  # 1ms
            
            # Most nodes will commit if they approved in prepare phase
            if peer_node_id in proposal.approved_by and random.random() < 0.95:
                committed.add(peer_node_id)
            else:
                rejected.add(peer_node_id)
        
        return {"committed": committed, "rejected": rejected}
    
    def _simulate_peer_response(self, peer_node_id: str, proposal: ConsensusProposal) -> bool:
        """Simulate peer node response to consensus proposal"""
        # Get transaction details
        transaction = self.pending_transactions.get(proposal.transaction_id)
        if not transaction:
            return False
        
        # Simulate different node behaviors
        if "fraud" in peer_node_id:
            # Fraud detection node - stricter validation
            return random.random() < 0.8  # 80% approval rate
        elif "backup" in peer_node_id:
            # Backup node - conservative
            return random.random() < 0.85  # 85% approval rate
        else:
            # Regular node
            return random.random() < 0.95  # 95% approval rate
    
    def _commit_transaction(self, transaction: UPITransaction):
        """Commit transaction to the ledger"""
        with self.lock:
            # Add to transaction log
            commit_entry = {
                "transaction_id": transaction.transaction_id,
                "upi_transaction_id": transaction.upi_transaction_id,
                "amount": transaction.amount,
                "payer_vpa": transaction.payer_vpa,
                "payee_vpa": transaction.payee_vpa,
                "status": transaction.status.value,
                "timestamp": transaction.timestamp.isoformat(),
                "commit_time": datetime.now().isoformat(),
                "committing_node": self.node_info.node_id
            }
            
            self.transaction_log.append(commit_entry)
            
            # Remove from pending
            if transaction.transaction_id in self.pending_transactions:
                del self.pending_transactions[transaction.transaction_id]
            
            logger.info(f"💳 Transaction committed: {transaction.upi_transaction_id} - ₹{transaction.amount:.2f}")
    
    def get_node_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this node"""
        avg_consensus_latency = sum(self.consensus_latencies) / max(len(self.consensus_latencies), 1)
        avg_validation_time = sum(self.validation_times) / max(len(self.validation_times), 1)
        
        return {
            "node_id": self.node_info.node_id,
            "region": self.node_info.region,
            "state": self.node_info.state.value,
            "transactions_processed": self.node_info.transactions_processed,
            "consensus_rounds": self.node_info.consensus_rounds_participated,
            "committed_transactions": len(self.transaction_log),
            "pending_transactions": len(self.pending_transactions),
            "active_proposals": len(self.current_proposals),
            "avg_consensus_latency_ms": avg_consensus_latency,
            "avg_validation_time_ms": avg_validation_time,
            "current_term": self.node_info.current_term,
            "is_leader": self.node_info.state == NodeState.LEADER,
            "peer_count": len(self.peer_nodes)
        }

class PaytmDistributedConsensusSystem:
    """Complete distributed consensus system for Paytm"""
    
    def __init__(self):
        # Create geographically distributed nodes
        self.nodes = {}
        self.setup_distributed_nodes()
        
        # System metrics
        self.system_start_time = datetime.now()
        self.total_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        self.total_consensus_time = 0.0
        
        logger.info(f"🚀 Paytm distributed consensus system initialized with {len(self.nodes)} nodes")
    
    def setup_distributed_nodes(self):
        """Setup geographically distributed consensus nodes"""
        # Indian data centers and regions
        regions = [
            {"id": "primary_mumbai", "region": "Mumbai", "type": "primary"},
            {"id": "secondary_delhi", "region": "Delhi", "type": "secondary"},
            {"id": "backup_bangalore", "region": "Bangalore", "type": "backup"},
            {"id": "fraud_hyderabad", "region": "Hyderabad", "type": "fraud_detection"},
            {"id": "backup_chennai", "region": "Chennai", "type": "backup"},
        ]
        
        # Create nodes
        for region_info in regions:
            node_id = region_info["id"]
            other_nodes = [r["id"] for r in regions if r["id"] != node_id]
            
            node = PaytmConsensusNode(node_id, region_info["region"], other_nodes)
            self.nodes[node_id] = node
        
        # Set leader (primary Mumbai node)
        primary_node = self.nodes["primary_mumbai"]
        primary_node.node_info.state = NodeState.LEADER
        primary_node.leader_id = primary_node.node_info.node_id
        
        # Update leader info in all nodes
        for node in self.nodes.values():
            node.leader_id = primary_node.node_info.node_id
    
    def select_processing_node(self, transaction: UPITransaction) -> str:
        """Select node to process transaction based on load balancing"""
        # Simple round-robin selection (in production, would consider load, latency, etc.)
        active_nodes = [node_id for node_id, node in self.nodes.items() 
                       if node.node_info.is_active]
        
        if not active_nodes:
            return list(self.nodes.keys())[0]  # Fallback
        
        # Hash-based selection for consistency
        transaction_hash = hash(transaction.transaction_id) % len(active_nodes)
        return active_nodes[transaction_hash]
    
    async def process_upi_transaction(self, transaction: UPITransaction) -> Dict[str, Any]:
        """Process UPI transaction through distributed consensus"""
        # Select processing node
        processing_node_id = self.select_processing_node(transaction)
        processing_node = self.nodes[processing_node_id]
        
        # Process transaction
        result = await processing_node.process_transaction(transaction)
        
        # Update system metrics
        self.total_transactions += 1
        if result.get("status") == "SUCCESS":
            self.successful_transactions += 1
        else:
            self.failed_transactions += 1
        
        if "processing_time_ms" in result:
            self.total_consensus_time += result["processing_time_ms"]
        
        result["processing_node"] = processing_node_id
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        uptime = datetime.now() - self.system_start_time
        
        # Aggregate metrics from all nodes
        total_processed = sum(node.node_info.transactions_processed for node in self.nodes.values())
        total_committed = sum(len(node.transaction_log) for node in self.nodes.values())
        total_pending = sum(len(node.pending_transactions) for node in self.nodes.values())
        
        # Calculate success rate
        success_rate = (self.successful_transactions / max(self.total_transactions, 1)) * 100
        
        # Average consensus time
        avg_consensus_time = self.total_consensus_time / max(self.total_transactions, 1)
        
        # Node statuses
        node_statuses = {node_id: node.get_node_metrics() for node_id, node in self.nodes.items()}
        
        return {
            "system_uptime": str(uptime),
            "total_nodes": len(self.nodes),
            "active_nodes": sum(1 for node in self.nodes.values() if node.node_info.is_active),
            "leader_node": next((node_id for node_id, node in self.nodes.items() 
                               if node.node_info.state == NodeState.LEADER), None),
            "total_transactions": self.total_transactions,
            "successful_transactions": self.successful_transactions,
            "failed_transactions": self.failed_transactions,
            "success_rate_percent": success_rate,
            "total_processed_by_nodes": total_processed,
            "total_committed": total_committed,
            "total_pending": total_pending,
            "avg_consensus_time_ms": avg_consensus_time,
            "transactions_per_second": self.total_transactions / max(uptime.total_seconds(), 1),
            "nodes": node_statuses,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_system_dashboard(self):
        """Print comprehensive system dashboard"""
        status = self.get_system_status()
        
        print(f"\n{'='*80}")
        print(f"💳 PAYTM DISTRIBUTED CONSENSUS SYSTEM DASHBOARD 💳")
        print(f"{'='*80}")
        
        print(f"🏛️ System Overview:")
        print(f"   Total Nodes: {status['total_nodes']}")
        print(f"   Active Nodes: {status['active_nodes']}")
        print(f"   Leader Node: {status['leader_node']}")
        print(f"   System Uptime: {status['system_uptime']}")
        
        print(f"\n📊 Transaction Metrics:")
        print(f"   Total Transactions: {status['total_transactions']:,}")
        print(f"   Successful: {status['successful_transactions']:,}")
        print(f"   Failed: {status['failed_transactions']:,}")
        print(f"   Success Rate: {status['success_rate_percent']:.2f}%")
        print(f"   Committed: {status['total_committed']:,}")
        print(f"   Pending: {status['total_pending']:,}")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Consensus Time: {status['avg_consensus_time_ms']:.2f} ms")
        print(f"   Transactions/Second: {status['transactions_per_second']:.1f}")
        
        print(f"\n🖥️ Node Status:")
        for node_id, node_status in status['nodes'].items():
            print(f"   {node_id} ({node_status['region']}):")
            print(f"     State: {node_status['state']}")
            print(f"     Processed: {node_status['transactions_processed']:,}")
            print(f"     Committed: {node_status['committed_transactions']:,}")
            print(f"     Consensus Latency: {node_status['avg_consensus_latency_ms']:.2f} ms")
            print(f"     Validation Time: {node_status['avg_validation_time_ms']:.2f} ms")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

def generate_random_upi_transaction() -> UPITransaction:
    """Generate realistic UPI transaction for simulation"""
    transaction_types = [
        TransactionType.UPI_P2P,
        TransactionType.UPI_P2M,
        TransactionType.WALLET_TRANSFER,
        TransactionType.RECHARGE,
        TransactionType.BILL_PAYMENT
    ]
    
    # Common Indian VPAs
    payer_vpas = [
        "user1@paytm", "customer@phonepe", "buyer@googlepay",
        "shopper@amazonpay", "person@okaxis", "individual@ybl"
    ]
    
    payee_vpas = [
        "merchant@paytm", "store@phonepe", "shop@googlepay",
        "business@amazonpay", "vendor@okaxis", "company@ybl"
    ]
    
    # Indian IFSC codes (sample)
    ifsc_codes = [
        "SBIN0000123", "HDFC0000456", "ICIC0000789",
        "AXIS0000012", "UBIN0000345", "PUNB0000678"
    ]
    
    transaction_type = random.choice(transaction_types)
    
    # Generate realistic amounts based on transaction type
    if transaction_type == TransactionType.UPI_P2P:
        amount = random.choice([100, 200, 500, 1000, 2000, 5000, 10000])
    elif transaction_type == TransactionType.UPI_P2M:
        amount = random.choice([50, 150, 350, 750, 1500, 3000, 7500])
    elif transaction_type == TransactionType.RECHARGE:
        amount = random.choice([99, 199, 299, 399, 499, 599])
    else:
        amount = random.choice([200, 500, 1000, 2000, 5000])
    
    return UPITransaction(
        transaction_id=str(uuid.uuid4()),
        upi_transaction_id=f"UPI{int(time.time())}{random.randint(1000, 9999)}",
        payer_vpa=random.choice(payer_vpas),
        payee_vpa=random.choice(payee_vpas),
        amount=float(amount),
        transaction_type=transaction_type,
        payer_ifsc=random.choice(ifsc_codes),
        payee_ifsc=random.choice(ifsc_codes),
        description=f"Payment for {transaction_type.value}",
        otp_verified=True,
        biometric_verified=random.choice([True, False]),
        daily_limit_checked=True,
        fraud_check_passed=True
    )

async def simulate_upi_payment_rush(system: PaytmDistributedConsensusSystem, duration_minutes: int = 5):
    """Simulate high-volume UPI payment processing"""
    logger.info(f"💳 Starting Paytm UPI payment simulation for {duration_minutes} minutes")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    transaction_count = 0
    
    try:
        while time.time() < end_time:
            # Simulate different load patterns
            current_hour = datetime.now().hour
            
            # Peak hours for UPI transactions
            if 9 <= current_hour <= 11 or 19 <= current_hour <= 22:
                # Peak hours - higher transaction rate
                transactions_per_second = random.randint(8, 15)
            elif 12 <= current_hour <= 14:
                # Lunch time - medium load
                transactions_per_second = random.randint(5, 10)
            else:
                # Normal hours
                transactions_per_second = random.randint(2, 6)
            
            # Process batch of transactions
            tasks = []
            for _ in range(transactions_per_second):
                transaction = generate_random_upi_transaction()
                task = system.process_upi_transaction(transaction)
                tasks.append(task)
                transaction_count += 1
            
            # Wait for batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log interesting events
            for i, result in enumerate(results):
                if isinstance(result, dict) and result.get("status") == "SUCCESS":
                    if result.get("processing_time_ms", 0) > 100:  # Log slow transactions
                        logger.info(f"⚠️ Slow transaction: {result['transaction_id']} took {result['processing_time_ms']:.1f}ms")
            
            # Print dashboard every 30 seconds
            if transaction_count % 50 == 0:
                system.print_system_dashboard()
            
            # Wait before next batch
            await asyncio.sleep(1.0)
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    
    logger.info(f"🏁 UPI simulation completed! Processed {transaction_count} transactions")
    
    # Final dashboard
    system.print_system_dashboard()

async def main():
    """Main demo function"""
    print("🇮🇳 Paytm Distributed Consensus System")
    print("💳 Byzantine fault-tolerant consensus for UPI payment processing")
    print("🏛️ Multi-node agreement with RBI compliance और fraud detection...\n")
    
    # Initialize distributed consensus system
    system = PaytmDistributedConsensusSystem()
    
    try:
        # Show initial system status
        system.print_system_dashboard()
        
        # Run UPI payment simulation
        await simulate_upi_payment_rush(system, duration_minutes=3)
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"💡 Production system capabilities:")
        print(f"   - Process 1.4 billion+ transactions per month")
        print(f"   - Byzantine fault tolerance across data centers")
        print(f"   - Sub-second consensus for UPI payments")
        print(f"   - 99.5%+ transaction success rate")
        print(f"   - Real-time fraud detection और validation")
        print(f"   - Geographic distribution across India")
        
    except Exception as e:
        logger.error(f"❌ Error in simulation: {e}")

if __name__ == "__main__":
    # Run the distributed consensus system demo
    asyncio.run(main())