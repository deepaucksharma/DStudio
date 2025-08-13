#!/usr/bin/env python3
"""
Three-Phase Commit (3PC) Protocol Implementation
==============================================

Production-ready 3PC coordinator implementation for distributed transactions.
3PC eliminates the blocking problem of 2PC by adding a "pre-commit" phase.

Mumbai Context: 3PC = Mumbai local train का 3-stage boarding process जैसा है!
1. Platform पर wait (Can-Commit)
2. Train आने पर ready (Pre-Commit)  
3. Actual boarding (Do-Commit)

Real-world usage:
- Banking transaction coordination
- E-commerce order processing
- Distributed database transactions
- Microservices transaction orchestration
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Optional, Enum, Any
from dataclasses import dataclass, asdict
from enum import Enum
import socket
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionState(Enum):
    """Transaction states in 3PC protocol"""
    INIT = "INIT"
    CAN_COMMIT = "CAN_COMMIT"
    PRE_COMMIT = "PRE_COMMIT"
    COMMIT = "COMMIT"
    ABORT = "ABORT"

class ParticipantState(Enum):
    """Participant states in 3PC protocol"""
    INIT = "INIT"
    UNCERTAIN = "UNCERTAIN"      # After Can-Commit YES
    PREPARED = "PREPARED"        # After Pre-Commit ACK
    COMMITTED = "COMMITTED"      # After Do-Commit
    ABORTED = "ABORTED"         # After Abort

class MessageType(Enum):
    """3PC Protocol message types"""
    # Phase 1: Can-Commit
    CAN_COMMIT = "CAN_COMMIT"
    YES_VOTE = "YES_VOTE"
    NO_VOTE = "NO_VOTE"
    
    # Phase 2: Pre-Commit  
    PRE_COMMIT = "PRE_COMMIT"
    PRE_COMMIT_ACK = "PRE_COMMIT_ACK"
    
    # Phase 3: Do-Commit
    DO_COMMIT = "DO_COMMIT"
    COMMIT_ACK = "COMMIT_ACK"
    
    # Abort messages
    ABORT = "ABORT"
    ABORT_ACK = "ABORT_ACK"
    
    # Recovery messages
    PARTICIPANT_TIMEOUT = "PARTICIPANT_TIMEOUT"
    COORDINATOR_TIMEOUT = "COORDINATOR_TIMEOUT"

@dataclass
class Message:
    """3PC Protocol message"""
    message_type: MessageType
    transaction_id: str
    sender_id: str
    timestamp: float
    data: Optional[Dict[str, Any]] = None

@dataclass
class Transaction:
    """Distributed transaction"""
    transaction_id: str
    coordinator_id: str
    participants: List[str]
    operation: str
    data: Dict[str, Any]
    state: TransactionState
    created_at: float
    timeout_seconds: int = 30

class ThreePhaseCommitCoordinator:
    """
    Three-Phase Commit Coordinator Implementation
    
    Mumbai Metaphor: यह Mumbai Railway का Central Control Room जैसा है!
    सभी stations (participants) को 3 phases में coordinate करता है:
    1. Can you handle this train? (Can-Commit)
    2. Get ready for train arrival (Pre-Commit)
    3. Train is arriving now! (Do-Commit)
    """
    
    def __init__(self, coordinator_id: str, port: int = 8000):
        self.coordinator_id = coordinator_id
        self.port = port
        self.participants: Dict[str, str] = {}  # participant_id -> address
        self.active_transactions: Dict[str, Transaction] = {}
        self.transaction_results: Dict[str, bool] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.message_queue = queue.Queue()
        self.running = False
        
        # Statistics
        self.stats = {
            'transactions_started': 0,
            'transactions_committed': 0,
            'transactions_aborted': 0,
            'phase1_timeouts': 0,
            'phase2_timeouts': 0,
            'phase3_timeouts': 0,
            'participant_failures': 0
        }
        
        logger.info(f"🎯 3PC Coordinator initialized: {coordinator_id} on port {port}")
    
    def register_participant(self, participant_id: str, address: str):
        """Register a new participant"""
        self.participants[participant_id] = address
        logger.info(f"📋 Participant registered: {participant_id} at {address}")
    
    def start_transaction(self, operation: str, data: Dict[str, Any], 
                         participant_ids: List[str], timeout_seconds: int = 30) -> str:
        """
        Start a new distributed transaction
        
        Args:
            operation: Operation to perform
            data: Transaction data
            participant_ids: List of participants
            timeout_seconds: Transaction timeout
            
        Returns:
            Transaction ID
        """
        transaction_id = f"TXN_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        # Validate participants
        for pid in participant_ids:
            if pid not in self.participants:
                raise ValueError(f"Unknown participant: {pid}")
        
        transaction = Transaction(
            transaction_id=transaction_id,
            coordinator_id=self.coordinator_id,
            participants=participant_ids.copy(),
            operation=operation,
            data=data,
            state=TransactionState.INIT,
            created_at=time.time(),
            timeout_seconds=timeout_seconds
        )
        
        self.active_transactions[transaction_id] = transaction
        self.stats['transactions_started'] += 1
        
        logger.info(f"🚀 Transaction started: {transaction_id} with {len(participant_ids)} participants")
        
        # Start 3PC protocol
        self.executor.submit(self._execute_3pc_protocol, transaction)
        
        return transaction_id
    
    def _execute_3pc_protocol(self, transaction: Transaction):
        """Execute the 3-phase commit protocol"""
        try:
            # Phase 1: Can-Commit
            logger.info(f"📝 Phase 1 (Can-Commit): {transaction.transaction_id}")
            if not self._phase1_can_commit(transaction):
                self._abort_transaction(transaction)
                return
            
            # Phase 2: Pre-Commit
            logger.info(f"🔄 Phase 2 (Pre-Commit): {transaction.transaction_id}")
            if not self._phase2_pre_commit(transaction):
                self._abort_transaction(transaction)
                return
            
            # Phase 3: Do-Commit
            logger.info(f"✅ Phase 3 (Do-Commit): {transaction.transaction_id}")
            self._phase3_do_commit(transaction)
            
        except Exception as e:
            logger.error(f"❌ 3PC Protocol failed for {transaction.transaction_id}: {e}")
            self._abort_transaction(transaction)
    
    def _phase1_can_commit(self, transaction: Transaction) -> bool:
        """
        Phase 1: Can-Commit
        Send Can-Commit message to all participants and wait for votes
        """
        transaction.state = TransactionState.CAN_COMMIT
        
        # Send Can-Commit messages
        can_commit_msg = Message(
            message_type=MessageType.CAN_COMMIT,
            transaction_id=transaction.transaction_id,
            sender_id=self.coordinator_id,
            timestamp=time.time(),
            data={
                'operation': transaction.operation,
                'transaction_data': transaction.data
            }
        )
        
        # Send to all participants in parallel
        futures = []
        for participant_id in transaction.participants:
            future = self.executor.submit(
                self._send_message_to_participant,
                participant_id,
                can_commit_msg,
                transaction.timeout_seconds
            )
            futures.append((participant_id, future))
        
        # Collect votes
        votes = {}
        for participant_id, future in futures:
            try:
                response = future.result(timeout=transaction.timeout_seconds)
                if response and response.message_type in [MessageType.YES_VOTE, MessageType.NO_VOTE]:
                    votes[participant_id] = response.message_type == MessageType.YES_VOTE
                else:
                    logger.warning(f"⚠️ Invalid response from {participant_id} in Phase 1")
                    votes[participant_id] = False
            except Exception as e:
                logger.error(f"❌ Phase 1 timeout/error with {participant_id}: {e}")
                votes[participant_id] = False
                self.stats['phase1_timeouts'] += 1
        
        # Check if all participants voted YES
        all_yes = all(votes.values()) and len(votes) == len(transaction.participants)
        
        if all_yes:
            logger.info(f"✅ Phase 1 SUCCESS: All participants voted YES for {transaction.transaction_id}")
            return True
        else:
            no_votes = [pid for pid, vote in votes.items() if not vote]
            logger.warning(f"❌ Phase 1 FAILED: NO votes from {no_votes} for {transaction.transaction_id}")
            return False
    
    def _phase2_pre_commit(self, transaction: Transaction) -> bool:
        """
        Phase 2: Pre-Commit
        Send Pre-Commit message to all participants and wait for acknowledgments
        """
        transaction.state = TransactionState.PRE_COMMIT
        
        # Send Pre-Commit messages
        pre_commit_msg = Message(
            message_type=MessageType.PRE_COMMIT,
            transaction_id=transaction.transaction_id,
            sender_id=self.coordinator_id,
            timestamp=time.time(),
            data={'ready_to_commit': True}
        )
        
        # Send to all participants
        futures = []
        for participant_id in transaction.participants:
            future = self.executor.submit(
                self._send_message_to_participant,
                participant_id,
                pre_commit_msg,
                transaction.timeout_seconds
            )
            futures.append((participant_id, future))
        
        # Collect acknowledgments
        acks = {}
        for participant_id, future in futures:
            try:
                response = future.result(timeout=transaction.timeout_seconds)
                if response and response.message_type == MessageType.PRE_COMMIT_ACK:
                    acks[participant_id] = True
                else:
                    logger.warning(f"⚠️ Invalid Pre-Commit response from {participant_id}")
                    acks[participant_id] = False
            except Exception as e:
                logger.error(f"❌ Phase 2 timeout/error with {participant_id}: {e}")
                acks[participant_id] = False
                self.stats['phase2_timeouts'] += 1
        
        # Check if all participants acknowledged
        all_ack = all(acks.values()) and len(acks) == len(transaction.participants)
        
        if all_ack:
            logger.info(f"✅ Phase 2 SUCCESS: All participants ready for {transaction.transaction_id}")
            return True
        else:
            failed_acks = [pid for pid, ack in acks.items() if not ack]
            logger.warning(f"❌ Phase 2 FAILED: No ACK from {failed_acks} for {transaction.transaction_id}")
            return False
    
    def _phase3_do_commit(self, transaction: Transaction):
        """
        Phase 3: Do-Commit
        Send Do-Commit message to all participants
        """
        transaction.state = TransactionState.COMMIT
        
        # Send Do-Commit messages
        do_commit_msg = Message(
            message_type=MessageType.DO_COMMIT,
            transaction_id=transaction.transaction_id,
            sender_id=self.coordinator_id,
            timestamp=time.time(),
            data={'commit_now': True}
        )
        
        # Send to all participants
        futures = []
        for participant_id in transaction.participants:
            future = self.executor.submit(
                self._send_message_to_participant,
                participant_id,
                do_commit_msg,
                transaction.timeout_seconds
            )
            futures.append((participant_id, future))
        
        # Collect final acknowledgments (best effort)
        commit_acks = 0
        for participant_id, future in futures:
            try:
                response = future.result(timeout=transaction.timeout_seconds)
                if response and response.message_type == MessageType.COMMIT_ACK:
                    commit_acks += 1
            except Exception as e:
                logger.warning(f"⚠️ Phase 3 ACK timeout from {participant_id}: {e}")
                self.stats['phase3_timeouts'] += 1
        
        # Transaction is committed regardless of ACKs in Phase 3
        # (This is key difference from 2PC - non-blocking)
        self.transaction_results[transaction.transaction_id] = True
        self.stats['transactions_committed'] += 1
        
        logger.info(f"🎉 Transaction COMMITTED: {transaction.transaction_id} " +
                   f"(ACKs: {commit_acks}/{len(transaction.participants)})")
    
    def _abort_transaction(self, transaction: Transaction):
        """Abort a transaction by sending ABORT to all participants"""
        transaction.state = TransactionState.ABORT
        
        # Send ABORT messages
        abort_msg = Message(
            message_type=MessageType.ABORT,
            transaction_id=transaction.transaction_id,
            sender_id=self.coordinator_id,
            timestamp=time.time(),
            data={'reason': 'Transaction aborted by coordinator'}
        )
        
        # Send to all participants (best effort)
        for participant_id in transaction.participants:
            try:
                self.executor.submit(
                    self._send_message_to_participant,
                    participant_id,
                    abort_msg,
                    5  # Short timeout for abort messages
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to send ABORT to {participant_id}: {e}")
        
        self.transaction_results[transaction.transaction_id] = False
        self.stats['transactions_aborted'] += 1
        
        logger.info(f"🚫 Transaction ABORTED: {transaction.transaction_id}")
    
    def _send_message_to_participant(self, participant_id: str, message: Message, timeout: int) -> Optional[Message]:
        """
        Send message to participant and wait for response
        
        Note: In production, this would use proper networking (HTTP, gRPC, etc.)
        Here we simulate network communication for demonstration.
        """
        try:
            # Simulate network delay
            time.sleep(0.01 + (hash(participant_id) % 50) / 1000.0)  # 10-60ms
            
            # Simulate participant response based on message type
            if message.message_type == MessageType.CAN_COMMIT:
                # Simulate participant decision (90% YES rate)
                vote = MessageType.YES_VOTE if (hash(participant_id + message.transaction_id) % 10) < 9 else MessageType.NO_VOTE
                
                return Message(
                    message_type=vote,
                    transaction_id=message.transaction_id,
                    sender_id=participant_id,
                    timestamp=time.time()
                )
            
            elif message.message_type == MessageType.PRE_COMMIT:
                # Simulate Pre-Commit ACK (95% success rate)
                if (hash(participant_id + message.transaction_id) % 20) < 19:
                    return Message(
                        message_type=MessageType.PRE_COMMIT_ACK,
                        transaction_id=message.transaction_id,
                        sender_id=participant_id,
                        timestamp=time.time()
                    )
                else:
                    # Simulate timeout/failure
                    raise Exception("Simulated participant failure in Pre-Commit")
            
            elif message.message_type == MessageType.DO_COMMIT:
                # Simulate final commit ACK (98% success rate)  
                if (hash(participant_id + message.transaction_id) % 50) < 49:
                    return Message(
                        message_type=MessageType.COMMIT_ACK,
                        transaction_id=message.transaction_id,
                        sender_id=participant_id,
                        timestamp=time.time()
                    )
                else:
                    # Simulate timeout (but transaction still commits)
                    raise Exception("Simulated timeout in Do-Commit phase")
            
            elif message.message_type == MessageType.ABORT:
                # Always ACK abort messages
                return Message(
                    message_type=MessageType.ABORT_ACK,
                    transaction_id=message.transaction_id,
                    sender_id=participant_id,
                    timestamp=time.time()
                )
            
        except Exception as e:
            logger.debug(f"Simulated network error: {e}")
            raise
        
        return None
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a transaction"""
        if transaction_id in self.active_transactions:
            transaction = self.active_transactions[transaction_id]
            return {
                'transaction_id': transaction_id,
                'state': transaction.state.value,
                'participants': transaction.participants,
                'operation': transaction.operation,
                'created_at': transaction.created_at,
                'elapsed_time': time.time() - transaction.created_at
            }
        
        if transaction_id in self.transaction_results:
            return {
                'transaction_id': transaction_id,
                'state': 'COMMITTED' if self.transaction_results[transaction_id] else 'ABORTED',
                'completed': True
            }
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        total_transactions = self.stats['transactions_started']
        success_rate = 0.0
        if total_transactions > 0:
            success_rate = (self.stats['transactions_committed'] / total_transactions) * 100.0
        
        return {
            **self.stats,
            'active_transactions': len(self.active_transactions),
            'completed_transactions': len(self.transaction_results),
            'success_rate': success_rate,
            'registered_participants': len(self.participants)
        }

class HDFCBankingTransactionCoordinator:
    """
    HDFC Banking Transaction Coordinator using 3PC
    
    Mumbai Story: HDFC Bank में large corporate transactions के लिए multiple
    branches और systems को coordinate करना पड़ता है. 3PC ensures कि 
    distributed banking operations safely complete हों!
    """
    
    def __init__(self):
        self.coordinator = ThreePhaseCommitCoordinator("HDFC_Main_Coordinator", 8000)
        self.account_balances = {
            'HDFC001234567890': 500000.0,  # Corporate Account - Mumbai
            'HDFC001234567891': 750000.0,  # Corporate Account - Delhi  
            'HDFC001234567892': 300000.0,  # Corporate Account - Bangalore
            'HDFC001234567893': 1000000.0, # Corporate Account - Chennai
            'HDFC001234567894': 250000.0,  # Corporate Account - Kolkata
        }
        
        # Register bank branches as participants
        branches = [
            ('HDFC_Mumbai_Branch', 'hdfc-mumbai:8001'),
            ('HDFC_Delhi_Branch', 'hdfc-delhi:8002'),
            ('HDFC_Bangalore_Branch', 'hdfc-bangalore:8003'),
            ('HDFC_Chennai_Branch', 'hdfc-chennai:8004'),
            ('HDFC_Kolkata_Branch', 'hdfc-kolkata:8005'),
        ]
        
        for branch_id, address in branches:
            self.coordinator.register_participant(branch_id, address)
        
        logger.info("🏦 HDFC Banking Transaction Coordinator initialized")
    
    def process_fund_transfer(self, from_account: str, to_account: str, 
                             amount: float, reference: str) -> str:
        """
        Process distributed fund transfer using 3PC
        
        Args:
            from_account: Source account
            to_account: Destination account
            amount: Transfer amount
            reference: Transfer reference
            
        Returns:
            Transaction ID
        """
        # Determine participating branches based on accounts
        participants = self._get_account_branches([from_account, to_account])
        
        # Prepare transaction data
        transaction_data = {
            'from_account': from_account,
            'to_account': to_account,
            'amount': amount,
            'reference': reference,
            'timestamp': time.time()
        }
        
        # Start 3PC transaction
        transaction_id = self.coordinator.start_transaction(
            operation='FUND_TRANSFER',
            data=transaction_data,
            participant_ids=participants,
            timeout_seconds=45
        )
        
        logger.info(f"💰 Fund transfer initiated: {transaction_id} - ₹{amount:.2f} " +
                   f"({from_account[-4:]}*** → {to_account[-4:]}***)")
        
        return transaction_id
    
    def process_salary_disbursement(self, company_account: str, 
                                   employee_accounts: List[str], 
                                   amounts: List[float]) -> str:
        """
        Process salary disbursement to multiple employees using 3PC
        
        Args:
            company_account: Company's main account
            employee_accounts: List of employee accounts
            amounts: Corresponding salary amounts
            
        Returns:
            Transaction ID
        """
        if len(employee_accounts) != len(amounts):
            raise ValueError("Employee accounts and amounts lists must have same length")
        
        total_amount = sum(amounts)
        
        # Get all participating branches
        all_accounts = [company_account] + employee_accounts
        participants = self._get_account_branches(all_accounts)
        
        # Prepare salary disbursement data
        salary_data = {
            'company_account': company_account,
            'disbursements': [
                {'account': acc, 'amount': amt} 
                for acc, amt in zip(employee_accounts, amounts)
            ],
            'total_amount': total_amount,
            'disbursement_date': time.strftime('%Y-%m-%d'),
            'timestamp': time.time()
        }
        
        # Start 3PC transaction
        transaction_id = self.coordinator.start_transaction(
            operation='SALARY_DISBURSEMENT',
            data=salary_data,
            participant_ids=participants,
            timeout_seconds=60
        )
        
        logger.info(f"💸 Salary disbursement initiated: {transaction_id} - " +
                   f"₹{total_amount:.2f} to {len(employee_accounts)} employees")
        
        return transaction_id
    
    def _get_account_branches(self, accounts: List[str]) -> List[str]:
        """Determine which branches are involved based on account numbers"""
        # Simplified mapping - in reality this would be based on account routing
        branch_mapping = {
            'HDFC001234567890': 'HDFC_Mumbai_Branch',
            'HDFC001234567891': 'HDFC_Delhi_Branch', 
            'HDFC001234567892': 'HDFC_Bangalore_Branch',
            'HDFC001234567893': 'HDFC_Chennai_Branch',
            'HDFC001234567894': 'HDFC_Kolkata_Branch',
        }
        
        involved_branches = set()
        for account in accounts:
            if account in branch_mapping:
                involved_branches.add(branch_mapping[account])
            else:
                # Default to Mumbai branch for unknown accounts
                involved_branches.add('HDFC_Mumbai_Branch')
        
        return list(involved_branches)
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction status"""
        return self.coordinator.get_transaction_status(transaction_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get banking coordinator statistics"""
        return self.coordinator.get_statistics()

def simulate_hdfc_banking_transactions():
    """
    Simulate HDFC corporate banking transactions using 3PC
    
    Mumbai Scenario: एक बड़ी company के end of month में salary disbursement
    और vendor payments के लिए multiple branches में coordination की जरुरत होती है.
    3PC ensures कि सभी transactions safely complete हों!
    """
    logger.info("🏦 Starting HDFC Banking 3PC Transaction simulation...")
    
    # Initialize banking coordinator
    banking_coordinator = HDFCBankingTransactionCoordinator()
    
    # Simulate concurrent banking transactions
    transactions = []
    
    # 1. Large fund transfers
    fund_transfers = [
        ('HDFC001234567890', 'HDFC001234567891', 50000.0, 'Quarterly_Settlement_Q4'),
        ('HDFC001234567892', 'HDFC001234567893', 75000.0, 'Project_Payment_Alpha'),
        ('HDFC001234567894', 'HDFC001234567890', 30000.0, 'Vendor_Payment_Dec'),
        ('HDFC001234567891', 'HDFC001234567892', 45000.0, 'Marketing_Budget_Transfer'),
    ]
    
    for from_acc, to_acc, amount, ref in fund_transfers:
        try:
            txn_id = banking_coordinator.process_fund_transfer(from_acc, to_acc, amount, ref)
            transactions.append(txn_id)
        except Exception as e:
            logger.error(f"Fund transfer failed: {e}")
    
    # 2. Salary disbursements
    try:
        # Mumbai office salary disbursement
        employee_accounts = [
            'HDFC001234567891', 'HDFC001234567892', 
            'HDFC001234567893', 'HDFC001234567894'
        ]
        salary_amounts = [85000.0, 92000.0, 78000.0, 105000.0]
        
        salary_txn = banking_coordinator.process_salary_disbursement(
            'HDFC001234567890',  # Company account
            employee_accounts,
            salary_amounts
        )
        transactions.append(salary_txn)
        
    except Exception as e:
        logger.error(f"Salary disbursement failed: {e}")
    
    # Wait for transactions to complete
    logger.info("⏳ Waiting for transactions to complete...")
    time.sleep(5)
    
    # Check transaction statuses
    logger.info("\n📊 Transaction Results:")
    completed_count = 0
    committed_count = 0
    
    for txn_id in transactions:
        status = banking_coordinator.get_transaction_status(txn_id)
        if status:
            logger.info(f"Transaction {txn_id}: {status.get('state', 'UNKNOWN')}")
            if status.get('completed'):
                completed_count += 1
                if status.get('state') == 'COMMITTED':
                    committed_count += 1
    
    # Show final statistics
    stats = banking_coordinator.get_statistics()
    
    logger.info("\n📈 HDFC Banking 3PC Statistics:")
    logger.info(f"Total transactions started: {stats['transactions_started']}")
    logger.info(f"Transactions committed: {stats['transactions_committed']}")
    logger.info(f"Transactions aborted: {stats['transactions_aborted']}")
    logger.info(f"Success rate: {stats['success_rate']:.2f}%")
    logger.info(f"Phase 1 timeouts: {stats['phase1_timeouts']}")
    logger.info(f"Phase 2 timeouts: {stats['phase2_timeouts']}")
    logger.info(f"Phase 3 timeouts: {stats['phase3_timeouts']}")
    logger.info(f"Registered branches: {stats['registered_participants']}")

if __name__ == "__main__":
    try:
        simulate_hdfc_banking_transactions()
        logger.info("\n🎉 HDFC Banking 3PC simulation completed successfully!")
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()