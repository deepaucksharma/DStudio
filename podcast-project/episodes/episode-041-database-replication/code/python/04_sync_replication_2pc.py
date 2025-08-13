#!/usr/bin/env python3
"""
Episode 41: Database Replication Strategies
Example 4: Synchronous Replication with Two-Phase Commit (2PC) - Banking Transactions

यह example banking industry में critical transactions के लिए sync replication
और 2PC का real implementation दिखाता है। ACID properties ensure करने के लिए
synchronous replication जरूरी होती है financial systems में।

Real-world Use Case: Inter-bank Fund Transfer (NEFT/RTGS)
- Synchronous replication for consistency
- Two-phase commit for distributed transactions
- Strong consistency for financial compliance
- Coordinator-participant model implementation
"""

import asyncio
import time
import uuid
import json
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransactionPhase(Enum):
    PREPARE = "prepare"
    COMMIT = "commit"
    ABORT = "abort"

class TransactionState(Enum):
    PENDING = "pending"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"
    TIMEOUT = "timeout"

class VoteResponse(Enum):
    YES = "yes"
    NO = "no"
    TIMEOUT = "timeout"

@dataclass
class BankingTransaction:
    """Banking transaction for 2PC protocol"""
    transaction_id: str
    from_account: str
    to_account: str
    amount: float
    from_bank: str
    to_bank: str
    transaction_type: str  # NEFT, RTGS, IMPS
    timestamp: datetime
    state: TransactionState = TransactionState.PENDING
    coordinator_id: str = ""
    participants: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = f"TXN_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8].upper()}"

@dataclass
class PrepareMessage:
    """2PC Prepare phase message"""
    transaction_id: str
    transaction_data: BankingTransaction
    coordinator_id: str
    timeout: int = 30  # seconds

@dataclass
class VoteMessage:
    """2PC Vote response message"""
    transaction_id: str
    participant_id: str
    vote: VoteResponse
    timestamp: datetime
    error_message: str = ""

@dataclass
class CommitMessage:
    """2PC Commit/Abort phase message"""
    transaction_id: str
    phase: TransactionPhase
    coordinator_id: str

class BankNode:
    """
    Bank node implementing 2PC participant
    हर bank अपना separate node होता है with strong consistency
    """
    
    def __init__(self, bank_id: str, bank_name: str):
        self.bank_id = bank_id
        self.bank_name = bank_name
        
        # Account balances
        self.accounts: Dict[str, float] = {}
        
        # Transaction management
        self.active_transactions: Dict[str, BankingTransaction] = {}
        self.prepared_transactions: Dict[str, BankingTransaction] = {}
        self.transaction_log: List[BankingTransaction] = []
        
        # 2PC state management
        self.is_coordinator = False
        self.coordinator_for: Set[str] = set()  # Transaction IDs where this is coordinator
        
        # Network and timing
        self.is_online = True
        self.network_latency = 0.02  # 20ms inter-bank latency
        self.timeout_threshold = 30  # seconds
        
        # Performance metrics
        self.transactions_processed = 0
        self.commits_successful = 0
        self.aborts_count = 0
        self.timeouts_count = 0
        
        # Initialize test accounts
        self._initialize_accounts()
        
    def _initialize_accounts(self):
        """Initialize test bank accounts"""
        # Generate sample accounts based on bank
        account_prefixes = {
            "HDFC": "HDFC",
            "ICICI": "ICICI", 
            "SBI": "SBI",
            "AXIS": "AXIS",
            "KOTAK": "KOTAK"
        }
        
        prefix = account_prefixes.get(self.bank_id, self.bank_id)
        
        for i in range(1, 6):  # 5 accounts per bank
            account_number = f"{prefix}{str(i).zfill(8)}"
            self.accounts[account_number] = 100000.0  # ₹1,00,000 initial balance
            
    async def prepare_transaction(self, prepare_msg: PrepareMessage) -> VoteMessage:
        """
        2PC Prepare phase - validate and lock resources
        यहाँ banking validation और resource locking होती है
        """
        transaction = prepare_msg.transaction_data
        
        try:
            # Simulate network latency
            await asyncio.sleep(self.network_latency)
            
            if not self.is_online:
                return VoteMessage(
                    transaction_id=transaction.transaction_id,
                    participant_id=self.bank_id,
                    vote=VoteResponse.NO,
                    timestamp=datetime.now(),
                    error_message="Bank node offline"
                )
            
            # Validate transaction
            validation_result = self._validate_transaction(transaction)
            
            if not validation_result[0]:
                return VoteMessage(
                    transaction_id=transaction.transaction_id,
                    participant_id=self.bank_id,
                    vote=VoteResponse.NO,
                    timestamp=datetime.now(),
                    error_message=validation_result[1]
                )
                
            # Lock resources (prepare phase)
            lock_result = self._lock_resources(transaction)
            
            if lock_result:
                # Store in prepared state
                transaction.state = TransactionState.PREPARED
                self.prepared_transactions[transaction.transaction_id] = transaction
                
                logger.info(f"{self.bank_name}: Transaction {transaction.transaction_id} prepared successfully")
                
                return VoteMessage(
                    transaction_id=transaction.transaction_id,
                    participant_id=self.bank_id,
                    vote=VoteResponse.YES,
                    timestamp=datetime.now()
                )
            else:
                return VoteMessage(
                    transaction_id=transaction.transaction_id,
                    participant_id=self.bank_id,
                    vote=VoteResponse.NO,
                    timestamp=datetime.now(),
                    error_message="Resource lock failed"
                )
                
        except Exception as e:
            logger.error(f"{self.bank_name}: Prepare failed for {transaction.transaction_id}: {e}")
            return VoteMessage(
                transaction_id=transaction.transaction_id,
                participant_id=self.bank_id,
                vote=VoteResponse.NO,
                timestamp=datetime.now(),
                error_message=str(e)
            )
            
    def _validate_transaction(self, transaction: BankingTransaction) -> Tuple[bool, str]:
        """Validate banking transaction according to banking rules"""
        
        # Basic validation
        if transaction.amount <= 0:
            return False, "Invalid amount"
            
        if transaction.from_account == transaction.to_account:
            return False, "Same account transfer"
            
        # Transaction type limits (RBI guidelines)
        if transaction.transaction_type == "IMPS" and transaction.amount > 200000:
            return False, "IMPS limit exceeded (₹2,00,000)"
            
        if transaction.transaction_type == "NEFT" and transaction.amount > 1000000:
            return False, "NEFT limit exceeded (₹10,00,000)"
            
        # Check if account belongs to this bank
        from_account_our_bank = self._is_our_account(transaction.from_account)
        to_account_our_bank = self._is_our_account(transaction.to_account)
        
        if not (from_account_our_bank or to_account_our_bank):
            return False, "Transaction doesn't involve our bank"
            
        # Check balance for debit transactions
        if from_account_our_bank:
            current_balance = self.accounts.get(transaction.from_account, 0)
            if current_balance < transaction.amount:
                return False, f"Insufficient balance. Available: ₹{current_balance}"
                
        # Banking hours validation (simplified)
        current_hour = datetime.now().hour
        if transaction.transaction_type == "NEFT" and (current_hour < 8 or current_hour > 19):
            return False, "NEFT not available outside banking hours"
            
        return True, "Valid"
        
    def _is_our_account(self, account_number: str) -> bool:
        """Check if account belongs to this bank"""
        return account_number in self.accounts
        
    def _lock_resources(self, transaction: BankingTransaction) -> bool:
        """Lock resources for transaction (prepare phase)"""
        try:
            # For simplicity, we'll mark the transaction as locked
            # In real systems, this would involve database row locks
            
            if self._is_our_account(transaction.from_account):
                # Ensure sufficient balance (already checked in validation)
                current_balance = self.accounts[transaction.from_account]
                if current_balance >= transaction.amount:
                    # Mark as locked (in real system, this would be a proper lock)
                    logger.debug(f"Locked {transaction.from_account} for debit of ₹{transaction.amount}")
                    return True
                else:
                    return False
                    
            if self._is_our_account(transaction.to_account):
                # Credit account doesn't need balance check
                logger.debug(f"Locked {transaction.to_account} for credit of ₹{transaction.amount}")
                return True
                
            return True
            
        except Exception as e:
            logger.error(f"Resource lock failed: {e}")
            return False
            
    async def commit_transaction(self, commit_msg: CommitMessage) -> bool:
        """
        2PC Commit phase - apply or rollback transaction
        यहाँ actual fund transfer होता है या rollback
        """
        transaction_id = commit_msg.transaction_id
        
        try:
            # Simulate network latency
            await asyncio.sleep(self.network_latency)
            
            if transaction_id not in self.prepared_transactions:
                logger.warning(f"{self.bank_name}: No prepared transaction {transaction_id}")
                return False
                
            transaction = self.prepared_transactions[transaction_id]
            
            if commit_msg.phase == TransactionPhase.COMMIT:
                # Apply the transaction
                success = self._apply_transaction(transaction)
                
                if success:
                    transaction.state = TransactionState.COMMITTED
                    self.transaction_log.append(transaction)
                    self.commits_successful += 1
                    
                    logger.info(f"{self.bank_name}: Transaction {transaction_id} committed successfully")
                else:
                    transaction.state = TransactionState.ABORTED
                    self.aborts_count += 1
                    logger.error(f"{self.bank_name}: Failed to commit transaction {transaction_id}")
                    
                # Remove from prepared state
                del self.prepared_transactions[transaction_id]
                self.transactions_processed += 1
                
                return success
                
            elif commit_msg.phase == TransactionPhase.ABORT:
                # Rollback the transaction
                self._rollback_transaction(transaction)
                transaction.state = TransactionState.ABORTED
                
                # Remove from prepared state
                del self.prepared_transactions[transaction_id]
                self.aborts_count += 1
                
                logger.info(f"{self.bank_name}: Transaction {transaction_id} aborted")
                return True
                
        except Exception as e:
            logger.error(f"{self.bank_name}: Commit/Abort failed for {transaction_id}: {e}")
            return False
            
    def _apply_transaction(self, transaction: BankingTransaction) -> bool:
        """Apply the banking transaction"""
        try:
            # Apply debit
            if self._is_our_account(transaction.from_account):
                self.accounts[transaction.from_account] -= transaction.amount
                logger.debug(f"Debited ₹{transaction.amount} from {transaction.from_account}")
                
            # Apply credit
            if self._is_our_account(transaction.to_account):
                self.accounts[transaction.to_account] += transaction.amount
                logger.debug(f"Credited ₹{transaction.amount} to {transaction.to_account}")
                
            return True
            
        except Exception as e:
            logger.error(f"Transaction application failed: {e}")
            return False
            
    def _rollback_transaction(self, transaction: BankingTransaction):
        """Rollback transaction (release locks)"""
        # In a real system, this would release database locks
        # For our simulation, we just log the rollback
        logger.debug(f"Rolled back locks for transaction {transaction.transaction_id}")
        
    def get_account_balance(self, account_number: str) -> Optional[float]:
        """Get current account balance"""
        return self.accounts.get(account_number)
        
    def get_bank_status(self) -> Dict:
        """Get bank node status"""
        total_balance = sum(self.accounts.values())
        
        return {
            "bank_id": self.bank_id,
            "bank_name": self.bank_name,
            "online": self.is_online,
            "total_accounts": len(self.accounts),
            "total_balance": total_balance,
            "transactions_processed": self.transactions_processed,
            "commits_successful": self.commits_successful,
            "aborts_count": self.aborts_count,
            "timeouts_count": self.timeouts_count,
            "prepared_transactions": len(self.prepared_transactions),
            "active_as_coordinator": len(self.coordinator_for)
        }

class TwoPhaseCommitCoordinator:
    """
    2PC Coordinator for distributed banking transactions
    RBI clearing house के जैसे central coordinator
    """
    
    def __init__(self, coordinator_id: str):
        self.coordinator_id = coordinator_id
        self.participants: Dict[str, BankNode] = {}
        
        # Transaction state tracking
        self.active_transactions: Dict[str, BankingTransaction] = {}
        self.prepare_responses: Dict[str, Dict[str, VoteMessage]] = {}
        
        # Timing
        self.transaction_timeout = 30  # seconds
        
        # Performance metrics
        self.total_transactions = 0
        self.successful_commits = 0
        self.failed_transactions = 0
        
    def add_participant(self, bank_node: BankNode):
        """Add bank as participant"""
        self.participants[bank_node.bank_id] = bank_node
        logger.info(f"Added {bank_node.bank_name} as participant")
        
    async def execute_distributed_transaction(self, transaction: BankingTransaction) -> Tuple[bool, str]:
        """
        Execute distributed transaction using 2PC
        यह main 2PC coordination logic है
        """
        
        transaction.coordinator_id = self.coordinator_id
        self.total_transactions += 1
        
        # Determine participants based on accounts involved
        participants = self._get_relevant_participants(transaction)
        transaction.participants = [p.bank_id for p in participants]
        
        if not participants:
            return False, "No relevant participants found"
            
        logger.info(f"Starting 2PC for transaction {transaction.transaction_id}")
        logger.info(f"Participants: {[p.bank_name for p in participants]}")
        
        # Store transaction
        self.active_transactions[transaction.transaction_id] = transaction
        
        # Phase 1: Prepare
        prepare_success = await self._execute_prepare_phase(transaction, participants)
        
        if prepare_success:
            # Phase 2: Commit
            commit_success = await self._execute_commit_phase(transaction, participants, TransactionPhase.COMMIT)
            
            if commit_success:
                self.successful_commits += 1
                logger.info(f"Transaction {transaction.transaction_id} committed successfully via 2PC")
                return True, "Transaction committed successfully"
            else:
                self.failed_transactions += 1
                return False, "Commit phase failed"
        else:
            # Phase 2: Abort
            await self._execute_commit_phase(transaction, participants, TransactionPhase.ABORT)
            self.failed_transactions += 1
            logger.warning(f"Transaction {transaction.transaction_id} aborted due to prepare phase failure")
            return False, "Transaction aborted - prepare phase failed"
            
    def _get_relevant_participants(self, transaction: BankingTransaction) -> List[BankNode]:
        """Get banks that need to participate in transaction"""
        participants = []
        
        for bank_node in self.participants.values():
            if (bank_node._is_our_account(transaction.from_account) or 
                bank_node._is_our_account(transaction.to_account)):
                participants.append(bank_node)
                
        return participants
        
    async def _execute_prepare_phase(self, transaction: BankingTransaction, 
                                   participants: List[BankNode]) -> bool:
        """Execute 2PC prepare phase"""
        
        logger.info(f"Phase 1: Preparing transaction {transaction.transaction_id}")
        
        # Create prepare message
        prepare_msg = PrepareMessage(
            transaction_id=transaction.transaction_id,
            transaction_data=transaction,
            coordinator_id=self.coordinator_id,
            timeout=self.transaction_timeout
        )
        
        # Send prepare to all participants
        prepare_tasks = []
        for participant in participants:
            task = asyncio.create_task(participant.prepare_transaction(prepare_msg))
            prepare_tasks.append((participant.bank_id, task))
            
        # Collect responses with timeout
        responses = {}
        try:
            for bank_id, task in prepare_tasks:
                response = await asyncio.wait_for(task, timeout=self.transaction_timeout)
                responses[bank_id] = response
                
        except asyncio.TimeoutError:
            logger.error(f"Prepare phase timeout for transaction {transaction.transaction_id}")
            return False
            
        # Store responses
        self.prepare_responses[transaction.transaction_id] = responses
        
        # Analyze responses
        all_yes = True
        for bank_id, response in responses.items():
            logger.info(f"Prepare response from {bank_id}: {response.vote.value}")
            
            if response.vote != VoteResponse.YES:
                all_yes = False
                logger.warning(f"Negative vote from {bank_id}: {response.error_message}")
                
        return all_yes
        
    async def _execute_commit_phase(self, transaction: BankingTransaction,
                                  participants: List[BankNode], 
                                  phase: TransactionPhase) -> bool:
        """Execute 2PC commit/abort phase"""
        
        phase_name = "committing" if phase == TransactionPhase.COMMIT else "aborting"
        logger.info(f"Phase 2: {phase_name} transaction {transaction.transaction_id}")
        
        # Create commit message
        commit_msg = CommitMessage(
            transaction_id=transaction.transaction_id,
            phase=phase,
            coordinator_id=self.coordinator_id
        )
        
        # Send commit/abort to all participants
        commit_tasks = []
        for participant in participants:
            task = asyncio.create_task(participant.commit_transaction(commit_msg))
            commit_tasks.append((participant.bank_id, task))
            
        # Collect responses
        all_success = True
        try:
            for bank_id, task in commit_tasks:
                success = await asyncio.wait_for(task, timeout=self.transaction_timeout)
                if not success:
                    all_success = False
                    logger.error(f"Commit failed on {bank_id}")
                    
        except asyncio.TimeoutError:
            logger.error(f"Commit phase timeout for transaction {transaction.transaction_id}")
            return False
            
        # Cleanup
        self.active_transactions.pop(transaction.transaction_id, None)
        self.prepare_responses.pop(transaction.transaction_id, None)
        
        return all_success
        
    def get_coordinator_status(self) -> Dict:
        """Get coordinator status"""
        success_rate = (self.successful_commits / max(1, self.total_transactions)) * 100
        
        return {
            "coordinator_id": self.coordinator_id,
            "total_participants": len(self.participants),
            "total_transactions": self.total_transactions,
            "successful_commits": self.successful_commits,
            "failed_transactions": self.failed_transactions,
            "success_rate": round(success_rate, 2),
            "active_transactions": len(self.active_transactions)
        }

class InterBankingSystem:
    """Complete inter-banking system with 2PC"""
    
    def __init__(self):
        # Create banks
        self.banks = {
            "HDFC": BankNode("HDFC", "HDFC Bank"),
            "ICICI": BankNode("ICICI", "ICICI Bank"),
            "SBI": BankNode("SBI", "State Bank of India"),
            "AXIS": BankNode("AXIS", "Axis Bank"),
            "KOTAK": BankNode("KOTAK", "Kotak Mahindra Bank")
        }
        
        # Create coordinator (RBI clearing house simulation)
        self.coordinator = TwoPhaseCommitCoordinator("RBI_CLEARING_HOUSE")
        
        # Add banks as participants
        for bank in self.banks.values():
            self.coordinator.add_participant(bank)
            
    async def process_inter_bank_transfer(self, from_account: str, to_account: str,
                                        amount: float, transaction_type: str = "NEFT",
                                        metadata: Dict = None) -> Tuple[bool, str]:
        """Process inter-bank fund transfer"""
        
        # Determine banks involved
        from_bank = self._get_bank_for_account(from_account)
        to_bank = self._get_bank_for_account(to_account)
        
        if not from_bank or not to_bank:
            return False, "Invalid account numbers"
            
        # Create transaction
        transaction = BankingTransaction(
            transaction_id="",  # Will be auto-generated
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            from_bank=from_bank,
            to_bank=to_bank,
            transaction_type=transaction_type,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Execute via 2PC
        return await self.coordinator.execute_distributed_transaction(transaction)
        
    def _get_bank_for_account(self, account_number: str) -> Optional[str]:
        """Determine which bank owns the account"""
        for bank_id, bank in self.banks.items():
            if bank._is_our_account(account_number):
                return bank_id
        return None
        
    async def simulate_banking_load(self, transaction_count: int = 20):
        """Simulate realistic inter-bank transfers"""
        logger.info(f"Simulating {transaction_count} inter-bank transfers...")
        
        import random
        
        # Get all account numbers
        all_accounts = []
        for bank in self.banks.values():
            all_accounts.extend(bank.accounts.keys())
            
        successful = 0
        failed = 0
        
        for i in range(transaction_count):
            # Random transfer between different banks
            from_account = random.choice(all_accounts)
            to_accounts = [acc for acc in all_accounts 
                          if self._get_bank_for_account(acc) != self._get_bank_for_account(from_account)]
            
            if not to_accounts:
                continue
                
            to_account = random.choice(to_accounts)
            amount = round(random.uniform(1000, 50000), 2)
            
            transaction_type = random.choice(["NEFT", "RTGS", "IMPS"])
            
            metadata = {
                "purpose": random.choice(["Business", "Personal", "Investment", "Bill Payment"]),
                "channel": random.choice(["Net Banking", "Mobile App", "Branch"]),
                "reference": f"REF{i+1:04d}"
            }
            
            success, message = await self.process_inter_bank_transfer(
                from_account, to_account, amount, transaction_type, metadata
            )
            
            if success:
                successful += 1
                logger.info(f"Transfer {i+1}: ₹{amount} from {from_account} to {to_account} - SUCCESS")
            else:
                failed += 1
                logger.warning(f"Transfer {i+1}: ₹{amount} from {from_account} to {to_account} - FAILED: {message}")
                
            # Small delay between transactions
            await asyncio.sleep(0.2)
            
        logger.info(f"Banking load simulation completed: {successful} successful, {failed} failed")
        return successful, failed
        
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        return {
            "coordinator": self.coordinator.get_coordinator_status(),
            "banks": {bank_id: bank.get_bank_status() for bank_id, bank in self.banks.items()}
        }

# Testing and demonstration
async def demonstrate_sync_replication_2pc():
    """
    Complete demonstration of synchronous replication with 2PC
    Real inter-banking scenario के साथ comprehensive testing
    """
    print("\n" + "="*75)
    print("Inter-Bank Synchronous Replication with 2PC Demonstration")
    print("Episode 41: Database Replication Strategies")
    print("="*75)
    
    # Initialize banking system
    banking_system = InterBankingSystem()
    
    logger.info("Inter-Banking System initialized")
    logger.info(f"Banks: {list(banking_system.banks.keys())}")
    
    # Show initial balances
    logger.info("\n--- Initial Account Balances ---")
    for bank_id, bank in banking_system.banks.items():
        total_balance = sum(bank.accounts.values())
        print(f"{bank.bank_name}: ₹{total_balance:,.2f} total across {len(bank.accounts)} accounts")
        
    # Demonstrate simple inter-bank transfer
    logger.info("\n--- Simple Inter-Bank Transfer ---")
    
    success, message = await banking_system.process_inter_bank_transfer(
        "HDFC00000001", "ICICI0000001", 25000.0, "NEFT",
        {"purpose": "Business payment", "reference": "INV2024001"}
    )
    
    print(f"HDFC to ICICI transfer: {'SUCCESS' if success else 'FAILED'} - {message}")
    
    # Show balances after transfer
    hdfc_balance = banking_system.banks["HDFC"].get_account_balance("HDFC00000001")
    icici_balance = banking_system.banks["ICICI"].get_account_balance("ICICI0000001")
    print(f"HDFC account balance after transfer: ₹{hdfc_balance:,.2f}")
    print(f"ICICI account balance after transfer: ₹{icici_balance:,.2f}")
    
    # Demonstrate failed transaction (insufficient balance)
    logger.info("\n--- Failed Transaction Demo ---")
    
    success, message = await banking_system.process_inter_bank_transfer(
        "SBI000000001", "AXIS00000001", 200000.0, "RTGS",
        {"purpose": "Large payment"}
    )
    
    print(f"SBI to AXIS large transfer: {'SUCCESS' if success else 'FAILED'} - {message}")
    
    # Simulate network failure
    logger.info("\n--- Network Failure Simulation ---")
    
    # Take one bank offline
    banking_system.banks["KOTAK"].is_online = False
    print("Kotak Bank taken offline...")
    
    success, message = await banking_system.process_inter_bank_transfer(
        "HDFC00000002", "KOTAK0000001", 15000.0, "IMPS"
    )
    
    print(f"Transfer to offline bank: {'SUCCESS' if success else 'FAILED'} - {message}")
    
    # Bring bank back online
    banking_system.banks["KOTAK"].is_online = True
    print("Kotak Bank brought back online...")
    
    # Successful transfer after bringing online
    success, message = await banking_system.process_inter_bank_transfer(
        "HDFC00000002", "KOTAK0000001", 15000.0, "IMPS"
    )
    
    print(f"Transfer after bank online: {'SUCCESS' if success else 'FAILED'} - {message}")
    
    # High-volume simulation
    logger.info("\n--- High-Volume Transaction Simulation ---")
    
    successful, failed = await banking_system.simulate_banking_load(transaction_count=15)
    print(f"High-volume simulation: {successful} successful, {failed} failed transactions")
    
    # Final system status
    logger.info("\n--- Final System Status ---")
    system_status = banking_system.get_system_status()
    
    print(f"\nCoordinator (RBI Clearing House) Status:")
    coord_status = system_status["coordinator"]
    print(f"  Total transactions: {coord_status['total_transactions']}")
    print(f"  Successful commits: {coord_status['successful_commits']}")
    print(f"  Failed transactions: {coord_status['failed_transactions']}")
    print(f"  Success rate: {coord_status['success_rate']}%")
    
    print(f"\nBank Status:")
    for bank_id, bank_status in system_status["banks"].items():
        print(f"  {bank_status['bank_name']}:")
        print(f"    Transactions processed: {bank_status['transactions_processed']}")
        print(f"    Successful commits: {bank_status['commits_successful']}")
        print(f"    Aborts: {bank_status['aborts_count']}")
        print(f"    Total balance: ₹{bank_status['total_balance']:,.2f}")
        
    # Show final account balances
    logger.info("\n--- Final Account Balances Sample ---")
    for bank_id, bank in banking_system.banks.items():
        sample_account = list(bank.accounts.keys())[0]
        balance = bank.accounts[sample_account]
        print(f"{bank.bank_name} ({sample_account}): ₹{balance:,.2f}")

if __name__ == "__main__":
    print("Inter-Bank Synchronous Replication with 2PC")
    print("Episode 41: Database Replication Strategies")
    print("Demonstrating strong consistency in banking with Two-Phase Commit...")
    
    # Run the demonstration
    asyncio.run(demonstrate_sync_replication_2pc())