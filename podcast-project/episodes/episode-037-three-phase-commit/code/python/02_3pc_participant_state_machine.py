#!/usr/bin/env python3
"""
Three-Phase Commit Participant State Machine
==========================================

Production-ready 3PC participant implementation with proper state management.
Handles all participant states and transitions according to 3PC protocol.

Mumbai Context: यह Mumbai local train के passenger का journey जैसा है!
1. Platform पर wait (INIT)
2. Train announcement सुनकर ready (UNCERTAIN after Can-Commit)
3. Train platform पर आकर boarding position (PREPARED after Pre-Commit)
4. Train में safely board (COMMITTED after Do-Commit)

Real-world usage:
- Database transaction participants
- Microservice transaction endpoints
- Distributed cache coordination
- Message queue transaction support
"""

import time
import threading
import logging
import json
import uuid
import socket
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import sqlite3
from contextlib import contextmanager
import pickle
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParticipantState(Enum):
    """3PC Participant state machine states"""
    INIT = "INIT"                # Initial state
    UNCERTAIN = "UNCERTAIN"      # After voting YES in Can-Commit
    PREPARED = "PREPARED"        # After ACK in Pre-Commit  
    COMMITTED = "COMMITTED"      # After final commit
    ABORTED = "ABORTED"         # After abort

class MessageType(Enum):
    """3PC Protocol message types"""
    # Coordinator to Participant
    CAN_COMMIT = "CAN_COMMIT"
    PRE_COMMIT = "PRE_COMMIT"
    DO_COMMIT = "DO_COMMIT"
    ABORT = "ABORT"
    
    # Participant to Coordinator
    YES_VOTE = "YES_VOTE"
    NO_VOTE = "NO_VOTE"
    PRE_COMMIT_ACK = "PRE_COMMIT_ACK"
    COMMIT_ACK = "COMMIT_ACK"
    ABORT_ACK = "ABORT_ACK"
    
    # Timeout/Recovery
    TIMEOUT = "TIMEOUT"
    ELECTION = "ELECTION"

@dataclass
class Message:
    """3PC Protocol message"""
    message_type: MessageType
    transaction_id: str
    sender_id: str
    timestamp: float
    data: Optional[Dict[str, Any]] = None

@dataclass
class TransactionLog:
    """Transaction log entry for recovery"""
    transaction_id: str
    state: ParticipantState
    operation: str
    data: Dict[str, Any]
    timestamp: float
    coordinator_id: str

class ThreePhaseCommitParticipant:
    """
    Three-Phase Commit Participant Implementation
    
    Mumbai Metaphor: यह Mumbai local train का passenger जैसा है जो 3 stages में
    journey करता है - wait, ready, board. Participant भी 3 phases में अपना
    state change करता है और recovery भी कर सकता है!
    """
    
    def __init__(self, participant_id: str, port: int, db_path: str = None):
        self.participant_id = participant_id
        self.port = port
        self.db_path = db_path or f"{participant_id}.db"
        
        # State management
        self.current_transactions: Dict[str, TransactionLog] = {}
        self.state_lock = threading.RLock()
        
        # Message handling
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.CAN_COMMIT: self._handle_can_commit,
            MessageType.PRE_COMMIT: self._handle_pre_commit,
            MessageType.DO_COMMIT: self._handle_do_commit,
            MessageType.ABORT: self._handle_abort,
        }
        
        # Recovery and timeouts
        self.timeout_threads: Dict[str, threading.Timer] = {}
        self.default_timeout = 30  # seconds
        
        # Statistics
        self.stats = {
            'transactions_processed': 0,
            'yes_votes': 0,
            'no_votes': 0,
            'commits_executed': 0,
            'aborts_executed': 0,
            'timeouts_occurred': 0,
            'recovery_actions': 0
        }
        
        # Initialize database for persistence
        self._init_database()
        
        # Load any incomplete transactions from disk
        self._load_incomplete_transactions()
        
        logger.info(f"🎭 3PC Participant initialized: {participant_id} on port {port}")
    
    def _init_database(self):
        """Initialize SQLite database for transaction logging"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transaction_log (
                    transaction_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    operation TEXT,
                    data TEXT,
                    timestamp REAL,
                    coordinator_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_state_timestamp 
                ON transaction_log(state, timestamp)
            """)
    
    def _load_incomplete_transactions(self):
        """Load incomplete transactions from database for recovery"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT transaction_id, state, operation, data, timestamp, coordinator_id
                FROM transaction_log
                WHERE state NOT IN ('COMMITTED', 'ABORTED')
                ORDER BY timestamp DESC
            """)
            
            for row in cursor.fetchall():
                txn_id, state, operation, data_json, timestamp, coordinator_id = row
                
                try:
                    data = json.loads(data_json) if data_json else {}
                    
                    log_entry = TransactionLog(
                        transaction_id=txn_id,
                        state=ParticipantState(state),
                        operation=operation,
                        data=data,
                        timestamp=timestamp,
                        coordinator_id=coordinator_id
                    )
                    
                    self.current_transactions[txn_id] = log_entry
                    self.stats['recovery_actions'] += 1
                    
                    # Start timeout for incomplete transactions
                    self._start_transaction_timeout(txn_id)
                    
                    logger.info(f"🔄 Recovered incomplete transaction: {txn_id} in state {state}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to recover transaction {txn_id}: {e}")
    
    def process_message(self, message: Message) -> Optional[Message]:
        """
        Process incoming 3PC protocol message
        
        Args:
            message: Incoming message from coordinator
            
        Returns:
            Response message to send back to coordinator
        """
        with self.state_lock:
            handler = self.message_handlers.get(message.message_type)
            if not handler:
                logger.warning(f"⚠️ Unknown message type: {message.message_type}")
                return None
            
            try:
                response = handler(message)
                logger.debug(f"📨 Processed {message.message_type} for {message.transaction_id}")
                return response
                
            except Exception as e:
                logger.error(f"❌ Failed to process {message.message_type}: {e}")
                return None
    
    def _handle_can_commit(self, message: Message) -> Message:
        """
        Handle Can-Commit message (Phase 1)
        
        Participant evaluates if it can commit to the transaction
        """
        transaction_id = message.transaction_id
        
        # Check if we can commit to this transaction
        can_commit = self._evaluate_can_commit(message)
        
        if can_commit:
            # Vote YES and move to UNCERTAIN state
            self._log_transaction_state(
                transaction_id=transaction_id,
                state=ParticipantState.UNCERTAIN,
                operation=message.data.get('operation', 'UNKNOWN'),
                data=message.data.get('transaction_data', {}),
                coordinator_id=message.sender_id
            )
            
            # Start timeout for waiting Pre-Commit
            self._start_transaction_timeout(transaction_id)
            
            self.stats['yes_votes'] += 1
            
            logger.info(f"✅ Voted YES for transaction: {transaction_id}")
            
            return Message(
                message_type=MessageType.YES_VOTE,
                transaction_id=transaction_id,
                sender_id=self.participant_id,
                timestamp=time.time()
            )
        else:
            # Vote NO and abort
            self._log_transaction_state(
                transaction_id=transaction_id,
                state=ParticipantState.ABORTED,
                operation=message.data.get('operation', 'UNKNOWN'),
                data=message.data.get('transaction_data', {}),
                coordinator_id=message.sender_id
            )
            
            self.stats['no_votes'] += 1
            
            logger.info(f"❌ Voted NO for transaction: {transaction_id}")
            
            return Message(
                message_type=MessageType.NO_VOTE,
                transaction_id=transaction_id,
                sender_id=self.participant_id,
                timestamp=time.time()
            )
    
    def _handle_pre_commit(self, message: Message) -> Message:
        """
        Handle Pre-Commit message (Phase 2)
        
        Participant prepares for commit and moves to PREPARED state
        """
        transaction_id = message.transaction_id
        
        # Check if we're in correct state
        if transaction_id not in self.current_transactions:
            logger.warning(f"⚠️ Pre-Commit for unknown transaction: {transaction_id}")
            return None
        
        current_log = self.current_transactions[transaction_id]
        if current_log.state != ParticipantState.UNCERTAIN:
            logger.warning(f"⚠️ Pre-Commit in wrong state {current_log.state}: {transaction_id}")
            return None
        
        # Prepare for commit
        prepared = self._prepare_for_commit(current_log)
        
        if prepared:
            # Move to PREPARED state
            self._log_transaction_state(
                transaction_id=transaction_id,
                state=ParticipantState.PREPARED,
                operation=current_log.operation,
                data=current_log.data,
                coordinator_id=current_log.coordinator_id
            )
            
            # Cancel old timeout and start new one for Do-Commit
            self._cancel_transaction_timeout(transaction_id)
            self._start_transaction_timeout(transaction_id)
            
            logger.info(f"🔄 Prepared for commit: {transaction_id}")
            
            return Message(
                message_type=MessageType.PRE_COMMIT_ACK,
                transaction_id=transaction_id,
                sender_id=self.participant_id,
                timestamp=time.time()
            )
        else:
            # Failed to prepare - this shouldn't happen in normal operation
            logger.error(f"❌ Failed to prepare transaction: {transaction_id}")
            return None
    
    def _handle_do_commit(self, message: Message) -> Message:
        """
        Handle Do-Commit message (Phase 3)
        
        Participant commits the transaction
        """
        transaction_id = message.transaction_id
        
        # Check if we're in correct state
        if transaction_id not in self.current_transactions:
            # This could happen if we recovered and already committed
            logger.info(f"ℹ️ Do-Commit for unknown/completed transaction: {transaction_id}")
            return Message(
                message_type=MessageType.COMMIT_ACK,
                transaction_id=transaction_id,
                sender_id=self.participant_id,
                timestamp=time.time()
            )
        
        current_log = self.current_transactions[transaction_id]
        
        # In 3PC, we can commit from PREPARED state
        if current_log.state != ParticipantState.PREPARED:
            logger.warning(f"⚠️ Do-Commit in wrong state {current_log.state}: {transaction_id}")
        
        # Execute the commit
        committed = self._execute_commit(current_log)
        
        if committed:
            # Move to COMMITTED state
            self._log_transaction_state(
                transaction_id=transaction_id,
                state=ParticipantState.COMMITTED,
                operation=current_log.operation,
                data=current_log.data,
                coordinator_id=current_log.coordinator_id
            )
            
            # Clean up
            self._cancel_transaction_timeout(transaction_id)
            del self.current_transactions[transaction_id]
            
            self.stats['commits_executed'] += 1
            self.stats['transactions_processed'] += 1
            
            logger.info(f"🎉 Transaction committed: {transaction_id}")
            
            return Message(
                message_type=MessageType.COMMIT_ACK,
                transaction_id=transaction_id,
                sender_id=self.participant_id,
                timestamp=time.time()
            )
        else:
            logger.error(f"❌ Failed to commit transaction: {transaction_id}")
            return None
    
    def _handle_abort(self, message: Message) -> Message:
        """
        Handle Abort message
        
        Participant aborts the transaction
        """
        transaction_id = message.transaction_id
        
        if transaction_id in self.current_transactions:
            current_log = self.current_transactions[transaction_id]
            
            # Execute abort
            self._execute_abort(current_log)
            
            # Move to ABORTED state
            self._log_transaction_state(
                transaction_id=transaction_id,
                state=ParticipantState.ABORTED,
                operation=current_log.operation,
                data=current_log.data,
                coordinator_id=current_log.coordinator_id
            )
            
            # Clean up
            self._cancel_transaction_timeout(transaction_id)
            del self.current_transactions[transaction_id]
            
            self.stats['aborts_executed'] += 1
            self.stats['transactions_processed'] += 1
            
            logger.info(f"🚫 Transaction aborted: {transaction_id}")
        
        return Message(
            message_type=MessageType.ABORT_ACK,
            transaction_id=transaction_id,
            sender_id=self.participant_id,
            timestamp=time.time()
        )
    
    def _evaluate_can_commit(self, message: Message) -> bool:
        """
        Evaluate if participant can commit to the transaction
        
        This is where business logic would determine if the operation
        is valid and can be performed.
        """
        try:
            operation = message.data.get('operation')
            data = message.data.get('transaction_data', {})
            
            # Business logic evaluation
            if operation == 'FUND_TRANSFER':
                from_account = data.get('from_account')
                amount = data.get('amount', 0)
                
                # Check if we have this account and sufficient balance
                if self._has_account(from_account):
                    balance = self._get_account_balance(from_account)
                    return balance >= amount
                
                # If we don't have the from_account, we might have to_account
                to_account = data.get('to_account')
                return self._has_account(to_account)
            
            elif operation == 'SALARY_DISBURSEMENT':
                company_account = data.get('company_account')
                total_amount = data.get('total_amount', 0)
                
                if self._has_account(company_account):
                    balance = self._get_account_balance(company_account)
                    return balance >= total_amount
                
                # Check if we have any employee accounts
                disbursements = data.get('disbursements', [])
                for disbursement in disbursements:
                    if self._has_account(disbursement.get('account')):
                        return True
                
                return False
            
            # Default: accept unknown operations
            return True
            
        except Exception as e:
            logger.error(f"❌ Error evaluating can-commit: {e}")
            return False
    
    def _prepare_for_commit(self, transaction_log: TransactionLog) -> bool:
        """
        Prepare resources for commit
        
        This phase locks resources and prepares for the actual commit
        """
        try:
            operation = transaction_log.operation
            data = transaction_log.data
            
            if operation == 'FUND_TRANSFER':
                from_account = data.get('from_account')
                to_account = data.get('to_account')
                amount = data.get('amount', 0)
                
                # Lock accounts (simplified - in reality would use proper locking)
                if self._has_account(from_account):
                    # Reserve the amount
                    return self._reserve_funds(from_account, amount)
                elif self._has_account(to_account):
                    # Prepare to receive funds
                    return True
            
            elif operation == 'SALARY_DISBURSEMENT':
                company_account = data.get('company_account')
                total_amount = data.get('total_amount', 0)
                
                if self._has_account(company_account):
                    return self._reserve_funds(company_account, total_amount)
                else:
                    # Prepare employee accounts to receive salary
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error preparing for commit: {e}")
            return False
    
    def _execute_commit(self, transaction_log: TransactionLog) -> bool:
        """
        Execute the actual transaction commit
        """
        try:
            operation = transaction_log.operation
            data = transaction_log.data
            
            if operation == 'FUND_TRANSFER':
                from_account = data.get('from_account')
                to_account = data.get('to_account')
                amount = data.get('amount', 0)
                
                if self._has_account(from_account):
                    # Debit from account
                    return self._debit_account(from_account, amount)
                elif self._has_account(to_account):
                    # Credit to account
                    return self._credit_account(to_account, amount)
            
            elif operation == 'SALARY_DISBURSEMENT':
                company_account = data.get('company_account')
                disbursements = data.get('disbursements', [])
                
                if self._has_account(company_account):
                    # Debit company account for total amount
                    total_amount = sum(d.get('amount', 0) for d in disbursements)
                    return self._debit_account(company_account, total_amount)
                else:
                    # Credit employee accounts
                    for disbursement in disbursements:
                        emp_account = disbursement.get('account')
                        salary_amount = disbursement.get('amount', 0)
                        
                        if self._has_account(emp_account):
                            self._credit_account(emp_account, salary_amount)
                    
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing commit: {e}")
            return False
    
    def _execute_abort(self, transaction_log: TransactionLog):
        """
        Execute transaction abort - release any reserved resources
        """
        try:
            operation = transaction_log.operation
            data = transaction_log.data
            
            # Release any reserved resources
            if operation in ['FUND_TRANSFER', 'SALARY_DISBURSEMENT']:
                logger.info(f"🔄 Released reserved resources for {transaction_log.transaction_id}")
            
        except Exception as e:
            logger.error(f"❌ Error executing abort: {e}")
    
    def _log_transaction_state(self, transaction_id: str, state: ParticipantState,
                              operation: str, data: Dict[str, Any], coordinator_id: str):
        """Log transaction state to database for recovery"""
        log_entry = TransactionLog(
            transaction_id=transaction_id,
            state=state,
            operation=operation,
            data=data,
            timestamp=time.time(),
            coordinator_id=coordinator_id
        )
        
        self.current_transactions[transaction_id] = log_entry
        
        # Persist to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO transaction_log 
                (transaction_id, state, operation, data, timestamp, coordinator_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                state.value,
                operation,
                json.dumps(data),
                log_entry.timestamp,
                coordinator_id
            ))
    
    def _start_transaction_timeout(self, transaction_id: str):
        """Start timeout timer for transaction"""
        def timeout_handler():
            self._handle_transaction_timeout(transaction_id)
        
        # Cancel existing timeout if any
        self._cancel_transaction_timeout(transaction_id)
        
        timer = threading.Timer(self.default_timeout, timeout_handler)
        timer.start()
        self.timeout_threads[transaction_id] = timer
    
    def _cancel_transaction_timeout(self, transaction_id: str):
        """Cancel timeout timer for transaction"""
        if transaction_id in self.timeout_threads:
            self.timeout_threads[transaction_id].cancel()
            del self.timeout_threads[transaction_id]
    
    def _handle_transaction_timeout(self, transaction_id: str):
        """Handle transaction timeout"""
        with self.state_lock:
            if transaction_id not in self.current_transactions:
                return
            
            current_log = self.current_transactions[transaction_id]
            self.stats['timeouts_occurred'] += 1
            
            logger.warning(f"⏰ Transaction timeout in state {current_log.state}: {transaction_id}")
            
            # 3PC timeout recovery logic
            if current_log.state == ParticipantState.UNCERTAIN:
                # In UNCERTAIN state, participant can abort
                logger.info(f"🚫 Aborting due to timeout in UNCERTAIN state: {transaction_id}")
                self._execute_abort(current_log)
                self._log_transaction_state(
                    transaction_id=transaction_id,
                    state=ParticipantState.ABORTED,
                    operation=current_log.operation,
                    data=current_log.data,
                    coordinator_id=current_log.coordinator_id
                )
                del self.current_transactions[transaction_id]
                self.stats['aborts_executed'] += 1
                
            elif current_log.state == ParticipantState.PREPARED:
                # In PREPARED state, participant should commit (key 3PC property)
                logger.info(f"✅ Committing due to timeout in PREPARED state: {transaction_id}")
                committed = self._execute_commit(current_log)
                if committed:
                    self._log_transaction_state(
                        transaction_id=transaction_id,
                        state=ParticipantState.COMMITTED,
                        operation=current_log.operation,
                        data=current_log.data,
                        coordinator_id=current_log.coordinator_id
                    )
                    del self.current_transactions[transaction_id]
                    self.stats['commits_executed'] += 1
    
    # Mock account operations for simulation
    def _has_account(self, account_id: str) -> bool:
        """Check if participant manages this account"""
        # Simple mapping based on participant ID
        if self.participant_id == 'HDFC_Mumbai_Branch':
            return account_id.endswith('890') or account_id.endswith('894')
        elif self.participant_id == 'HDFC_Delhi_Branch':
            return account_id.endswith('891')
        elif self.participant_id == 'HDFC_Bangalore_Branch':
            return account_id.endswith('892')
        elif self.participant_id == 'HDFC_Chennai_Branch':
            return account_id.endswith('893')
        return False
    
    def _get_account_balance(self, account_id: str) -> float:
        """Get account balance (mock implementation)"""
        # Mock balances for simulation
        mock_balances = {
            'HDFC001234567890': 500000.0,
            'HDFC001234567891': 750000.0,
            'HDFC001234567892': 300000.0,
            'HDFC001234567893': 1000000.0,
            'HDFC001234567894': 250000.0,
        }
        return mock_balances.get(account_id, 0.0)
    
    def _reserve_funds(self, account_id: str, amount: float) -> bool:
        """Reserve funds for transaction (mock implementation)"""
        balance = self._get_account_balance(account_id)
        logger.info(f"💰 Reserved ₹{amount:.2f} from {account_id[-4:]}*** (balance: ₹{balance:.2f})")
        return balance >= amount
    
    def _debit_account(self, account_id: str, amount: float) -> bool:
        """Debit account (mock implementation)"""
        logger.info(f"💸 Debited ₹{amount:.2f} from {account_id[-4:]}***")
        return True
    
    def _credit_account(self, account_id: str, amount: float) -> bool:
        """Credit account (mock implementation)"""
        logger.info(f"💰 Credited ₹{amount:.2f} to {account_id[-4:]}***")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get participant statistics"""
        return {
            **self.stats,
            'active_transactions': len(self.current_transactions),
            'current_state': list(self.current_transactions.keys())
        }
    
    def get_transaction_state(self, transaction_id: str) -> Optional[ParticipantState]:
        """Get current state of a transaction"""
        if transaction_id in self.current_transactions:
            return self.current_transactions[transaction_id].state
        return None

def simulate_hdfc_branch_participants():
    """
    Simulate HDFC branch participants in 3PC protocol
    
    Mumbai Scenario: Different HDFC branches act as participants in
    distributed banking transactions. Each branch manages specific
    accounts and follows 3PC protocol for consistency!
    """
    logger.info("🏦 Starting HDFC Branch Participants simulation...")
    
    # Initialize branch participants
    branches = [
        ThreePhaseCommitParticipant('HDFC_Mumbai_Branch', 8001),
        ThreePhaseCommitParticipant('HDFC_Delhi_Branch', 8002),
        ThreePhaseCommitParticipant('HDFC_Bangalore_Branch', 8003),
    ]
    
    # Simulate coordinator messages
    transaction_id = f"TXN_{int(time.time() * 1000)}_TEST"
    
    # Phase 1: Can-Commit
    logger.info("\n📝 Phase 1: Can-Commit")
    can_commit_msg = Message(
        message_type=MessageType.CAN_COMMIT,
        transaction_id=transaction_id,
        sender_id="TEST_COORDINATOR",
        timestamp=time.time(),
        data={
            'operation': 'FUND_TRANSFER',
            'transaction_data': {
                'from_account': 'HDFC001234567890',
                'to_account': 'HDFC001234567891',
                'amount': 50000.0,
                'reference': 'Test_Transfer'
            }
        }
    )
    
    responses = []
    for branch in branches:
        response = branch.process_message(can_commit_msg)
        responses.append((branch.participant_id, response))
        logger.info(f"  {branch.participant_id}: {response.message_type.value if response else 'NO_RESPONSE'}")
    
    # Phase 2: Pre-Commit (only to YES voters)
    logger.info("\n🔄 Phase 2: Pre-Commit")
    pre_commit_msg = Message(
        message_type=MessageType.PRE_COMMIT,
        transaction_id=transaction_id,
        sender_id="TEST_COORDINATOR",
        timestamp=time.time(),
        data={'ready_to_commit': True}
    )
    
    yes_voters = [branch for branch, resp in zip(branches, responses) 
                 if resp and resp.message_type == MessageType.YES_VOTE]
    
    pre_commit_responses = []
    for branch in yes_voters:
        response = branch.process_message(pre_commit_msg)
        pre_commit_responses.append((branch.participant_id, response))
        logger.info(f"  {branch.participant_id}: {response.message_type.value if response else 'NO_RESPONSE'}")
    
    # Phase 3: Do-Commit
    logger.info("\n✅ Phase 3: Do-Commit")
    do_commit_msg = Message(
        message_type=MessageType.DO_COMMIT,
        transaction_id=transaction_id,
        sender_id="TEST_COORDINATOR",
        timestamp=time.time(),
        data={'commit_now': True}
    )
    
    for branch in yes_voters:
        response = branch.process_message(do_commit_msg)
        logger.info(f"  {branch.participant_id}: {response.message_type.value if response else 'NO_RESPONSE'}")
    
    # Show final statistics
    logger.info("\n📊 Branch Participant Statistics:")
    for branch in branches:
        stats = branch.get_statistics()
        logger.info(f"  {branch.participant_id}:")
        logger.info(f"    Transactions processed: {stats['transactions_processed']}")
        logger.info(f"    YES votes: {stats['yes_votes']}")
        logger.info(f"    NO votes: {stats['no_votes']}")
        logger.info(f"    Commits executed: {stats['commits_executed']}")
        logger.info(f"    Active transactions: {stats['active_transactions']}")

if __name__ == "__main__":
    try:
        simulate_hdfc_branch_participants()
        logger.info("\n🎉 HDFC Branch Participants simulation completed!")
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()