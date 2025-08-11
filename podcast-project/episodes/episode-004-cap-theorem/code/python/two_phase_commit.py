#!/usr/bin/env python3
"""
Two-Phase Commit Protocol - Episode 4
व्यावहारिक 2PC protocol का production-ready implementation

यह protocol distributed transactions में ACID properties ensure करता है।
Atomic transactions across multiple databases/services.

Indian Context Examples:
- Paytm wallet to bank transfer (2 systems involved)
- Flipkart order + inventory + payment (3 systems)  
- IRCTC ticket booking + payment gateway (2 systems)
- Zomato order + restaurant + delivery (3 systems)

2PC Phases:
1. Prepare Phase - सभी participants से vote माँगना
2. Commit Phase - सभी का YES मिले तो commit, नहीं तो abort

Roles:
- Coordinator: Transaction को manage करता है
- Participants: Actual work करते हैं (databases, services)
"""

import time
import uuid
import threading
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random

class TransactionState(Enum):
    """Transaction की different states"""
    ACTIVE = "active"           # Transaction चल रहा है
    PREPARING = "preparing"     # Prepare phase में है
    PREPARED = "prepared"       # सभी participants prepared हैं
    COMMITTING = "committing"   # Commit phase में है
    COMMITTED = "committed"     # Successfully committed
    ABORTING = "aborting"      # Abort phase में है
    ABORTED = "aborted"        # Transaction aborted

class ParticipantState(Enum):
    """Participant की state"""
    IDLE = "idle"              # कोई transaction नहीं
    WORKING = "working"        # Transaction पर काम कर रहा है
    PREPARED = "prepared"      # Commit के लिए ready
    COMMITTED = "committed"    # Committed
    ABORTED = "aborted"       # Aborted

class VoteType(Enum):
    """Participant का vote"""
    YES = "yes"    # Ready to commit
    NO = "no"      # Cannot commit
    TIMEOUT = "timeout"  # No response

@dataclass
class PrepareRequest:
    """Prepare phase का request"""
    transaction_id: str
    coordinator_id: str
    operations: List[Dict[str, Any]]
    timeout_seconds: int = 30

@dataclass
class PrepareResponse:
    """Prepare phase का response"""
    transaction_id: str
    participant_id: str
    vote: VoteType
    message: str = ""
    prepared_at: float = field(default_factory=time.time)

@dataclass
class CommitRequest:
    """Commit/Abort phase का request"""
    transaction_id: str
    coordinator_id: str
    decision: str  # "commit" or "abort"
    
@dataclass
class CommitResponse:
    """Commit/Abort phase का response"""
    transaction_id: str
    participant_id: str
    success: bool
    message: str = ""
    completed_at: float = field(default_factory=time.time)

class TransactionParticipant:
    """
    2PC Participant - एक service/database जो transaction में participate करती है
    
    Examples:
    - Paytm Wallet Service
    - Bank API Service  
    - Inventory Management Service
    - Payment Gateway Service
    """
    
    def __init__(self, participant_id: str, service_type: str, location: str = "Mumbai"):
        self.participant_id = participant_id
        self.service_type = service_type
        self.location = location
        self.state = ParticipantState.IDLE
        
        # Simulated database/storage
        self.data_store: Dict[str, Any] = {}
        self.prepared_transactions: Dict[str, Dict] = {}
        
        # Configuration
        self.failure_rate = 0.1  # 10% chance of failure
        self.slow_response_rate = 0.2  # 20% chance of slow response
        self.max_response_time = 5.0  # seconds
        
        # Statistics
        self.stats = {
            'transactions_prepared': 0,
            'transactions_committed': 0,
            'transactions_aborted': 0,
            'prepare_failures': 0,
            'commit_failures': 0,
            'total_response_time': 0.0,
            'avg_response_time': 0.0
        }
        
        print(f"🏪 Participant {participant_id} ({service_type}) started at {location}")
    
    def prepare(self, request: PrepareRequest) -> PrepareResponse:
        """
        Prepare phase - participant को check करना है कि वह transaction commit कर सकता है
        
        Example: Paytm wallet checking if sufficient balance है
        """
        start_time = time.time()
        
        print(f"🔍 {self.participant_id}: Received prepare request for txn {request.transaction_id}")
        
        # Simulate work and potential delays
        if random.random() < self.slow_response_rate:
            delay = random.uniform(1.0, 3.0)
            print(f"⏳ {self.participant_id}: Slow response, delaying {delay:.1f}s")
            time.sleep(delay)
        else:
            time.sleep(random.uniform(0.1, 0.5))  # Normal processing time
        
        response = PrepareResponse(
            transaction_id=request.transaction_id,
            participant_id=self.participant_id,
            vote=VoteType.NO,  # Default to NO
            message=""
        )
        
        try:
            # Simulate business logic validation
            can_prepare = self._validate_operations(request.operations)
            
            if can_prepare and random.random() > self.failure_rate:
                # Successfully prepared
                self.state = ParticipantState.PREPARED
                self.prepared_transactions[request.transaction_id] = {
                    'operations': request.operations,
                    'prepared_at': time.time(),
                    'coordinator': request.coordinator_id
                }
                
                response.vote = VoteType.YES
                response.message = f"{self.service_type} ready to commit"
                self.stats['transactions_prepared'] += 1
                
                print(f"✅ {self.participant_id}: PREPARED for txn {request.transaction_id}")
                
            else:
                # Cannot prepare
                response.vote = VoteType.NO
                response.message = f"{self.service_type} cannot commit: validation failed"
                self.stats['prepare_failures'] += 1
                
                print(f"❌ {self.participant_id}: REJECTED txn {request.transaction_id}")
        
        except Exception as e:
            response.vote = VoteType.NO
            response.message = f"Prepare error: {str(e)}"
            self.stats['prepare_failures'] += 1
            
            print(f"💥 {self.participant_id}: Prepare failed with error: {e}")
        
        # Update response time stats
        response_time = time.time() - start_time
        self.stats['total_response_time'] += response_time
        prepared_count = self.stats['transactions_prepared'] + self.stats['prepare_failures']
        if prepared_count > 0:
            self.stats['avg_response_time'] = self.stats['total_response_time'] / prepared_count
        
        return response
    
    def commit(self, request: CommitRequest) -> CommitResponse:
        """
        Commit phase - actual work को commit या abort करना
        
        Example: Actually transferring money from Paytm wallet
        """
        print(f"🎯 {self.participant_id}: Received {request.decision} request for txn {request.transaction_id}")
        
        response = CommitResponse(
            transaction_id=request.transaction_id,
            participant_id=self.participant_id,
            success=False,
            message=""
        )
        
        try:
            if request.decision == "commit":
                if request.transaction_id in self.prepared_transactions:
                    # Execute the actual operations
                    prepared_data = self.prepared_transactions[request.transaction_id]
                    self._execute_operations(prepared_data['operations'])
                    
                    # Clean up
                    del self.prepared_transactions[request.transaction_id]
                    self.state = ParticipantState.COMMITTED
                    
                    response.success = True
                    response.message = f"{self.service_type} committed successfully"
                    self.stats['transactions_committed'] += 1
                    
                    print(f"✅ {self.participant_id}: COMMITTED txn {request.transaction_id}")
                    
                else:
                    response.message = "Transaction not prepared"
                    print(f"❌ {self.participant_id}: Cannot commit - not prepared")
            
            elif request.decision == "abort":
                # Clean up prepared transaction
                if request.transaction_id in self.prepared_transactions:
                    del self.prepared_transactions[request.transaction_id]
                
                self.state = ParticipantState.ABORTED
                response.success = True
                response.message = f"{self.service_type} aborted successfully"
                self.stats['transactions_aborted'] += 1
                
                print(f"🚫 {self.participant_id}: ABORTED txn {request.transaction_id}")
        
        except Exception as e:
            response.message = f"Commit/Abort error: {str(e)}"
            self.stats['commit_failures'] += 1
            
            print(f"💥 {self.participant_id}: Commit/Abort failed: {e}")
        
        return response
    
    def _validate_operations(self, operations: List[Dict]) -> bool:
        """
        Business logic validation for operations
        
        Example: Check if Paytm wallet has sufficient balance
        """
        for operation in operations:
            if operation.get('type') == 'debit':
                account = operation.get('account')
                amount = operation.get('amount', 0)
                current_balance = self.data_store.get(account, 0)
                
                if current_balance < amount:
                    print(f"❌ {self.participant_id}: Insufficient balance {current_balance} < {amount}")
                    return False
            
            elif operation.get('type') == 'reserve_inventory':
                item_id = operation.get('item_id')
                quantity = operation.get('quantity', 0)
                available = self.data_store.get(f"inventory_{item_id}", 0)
                
                if available < quantity:
                    print(f"❌ {self.participant_id}: Insufficient inventory {available} < {quantity}")
                    return False
        
        return True
    
    def _execute_operations(self, operations: List[Dict]):
        """
        Actually execute the operations after commit decision
        """
        for operation in operations:
            if operation.get('type') == 'debit':
                account = operation.get('account')
                amount = operation.get('amount', 0)
                current_balance = self.data_store.get(account, 0)
                self.data_store[account] = current_balance - amount
                
                print(f"💰 {self.participant_id}: Debited {amount} from {account}, new balance: {self.data_store[account]}")
            
            elif operation.get('type') == 'credit':
                account = operation.get('account') 
                amount = operation.get('amount', 0)
                current_balance = self.data_store.get(account, 0)
                self.data_store[account] = current_balance + amount
                
                print(f"💰 {self.participant_id}: Credited {amount} to {account}, new balance: {self.data_store[account]}")
            
            elif operation.get('type') == 'reserve_inventory':
                item_id = operation.get('item_id')
                quantity = operation.get('quantity', 0)
                current_inventory = self.data_store.get(f"inventory_{item_id}", 0)
                self.data_store[f"inventory_{item_id}"] = current_inventory - quantity
                
                print(f"📦 {self.participant_id}: Reserved {quantity} of {item_id}, remaining: {self.data_store[f'inventory_{item_id}']}")
    
    def get_stats(self) -> Dict:
        """Get participant statistics"""
        return self.stats.copy()

class TwoPhaseCommitCoordinator:
    """
    2PC Coordinator - Transaction को coordinate करता है
    
    Examples:
    - Paytm Payment Orchestrator
    - Flipkart Order Management Service
    - IRCTC Booking Coordinator
    """
    
    def __init__(self, coordinator_id: str, location: str = "Mumbai"):
        self.coordinator_id = coordinator_id
        self.location = location
        
        # Active transactions
        self.active_transactions: Dict[str, Dict] = {}
        
        # Configuration
        self.prepare_timeout = 10.0  # seconds
        self.commit_timeout = 5.0    # seconds
        self.max_retries = 3
        
        # Statistics
        self.stats = {
            'transactions_started': 0,
            'transactions_committed': 0,
            'transactions_aborted': 0,
            'prepare_timeouts': 0,
            'commit_timeouts': 0,
            'avg_transaction_time': 0.0,
            'total_transaction_time': 0.0
        }
        
        print(f"🎬 Coordinator {coordinator_id} started at {location}")
    
    def execute_transaction(self, participants: List[TransactionParticipant], 
                           operations_per_participant: Dict[str, List[Dict]]) -> bool:
        """
        Main 2PC protocol execution
        
        Example: Coordinating Paytm payment across wallet, bank, and merchant services
        """
        transaction_id = str(uuid.uuid4())
        start_time = time.time()
        
        print(f"\n🚀 Starting transaction {transaction_id}")
        print(f"👥 Participants: {[p.participant_id for p in participants]}")
        
        # Initialize transaction state
        transaction_data = {
            'transaction_id': transaction_id,
            'participants': {p.participant_id: p for p in participants},
            'operations': operations_per_participant,
            'state': TransactionState.ACTIVE,
            'start_time': start_time,
            'prepare_responses': {},
            'commit_responses': {}
        }
        
        self.active_transactions[transaction_id] = transaction_data
        self.stats['transactions_started'] += 1
        
        try:
            # Phase 1: Prepare
            print(f"\n📋 PHASE 1: PREPARE")
            prepare_success = self._prepare_phase(transaction_data)
            
            if prepare_success:
                # Phase 2: Commit
                print(f"\n✅ PHASE 2: COMMIT")
                transaction_data['state'] = TransactionState.COMMITTING
                commit_success = self._commit_phase(transaction_data, "commit")
                
                if commit_success:
                    transaction_data['state'] = TransactionState.COMMITTED
                    self.stats['transactions_committed'] += 1
                    result = True
                    print(f"🎉 Transaction {transaction_id} COMMITTED successfully")
                else:
                    transaction_data['state'] = TransactionState.ABORTED  
                    self.stats['transactions_aborted'] += 1
                    result = False
                    print(f"💥 Transaction {transaction_id} commit FAILED")
            else:
                # Phase 2: Abort
                print(f"\n🚫 PHASE 2: ABORT")
                transaction_data['state'] = TransactionState.ABORTING
                self._commit_phase(transaction_data, "abort")
                transaction_data['state'] = TransactionState.ABORTED
                self.stats['transactions_aborted'] += 1
                result = False
                print(f"🚫 Transaction {transaction_id} ABORTED")
        
        except Exception as e:
            print(f"💥 Transaction {transaction_id} failed with error: {e}")
            transaction_data['state'] = TransactionState.ABORTED
            self.stats['transactions_aborted'] += 1
            result = False
        
        # Update timing stats
        transaction_time = time.time() - start_time
        self.stats['total_transaction_time'] += transaction_time
        total_txns = self.stats['transactions_committed'] + self.stats['transactions_aborted']
        if total_txns > 0:
            self.stats['avg_transaction_time'] = self.stats['total_transaction_time'] / total_txns
        
        transaction_data['end_time'] = time.time()
        transaction_data['duration'] = transaction_time
        
        print(f"📊 Transaction {transaction_id} completed in {transaction_time:.2f}s")
        return result
    
    def _prepare_phase(self, transaction_data: Dict) -> bool:
        """
        Phase 1: Send prepare requests to all participants
        """
        transaction_id = transaction_data['transaction_id']
        participants = transaction_data['participants']
        operations = transaction_data['operations']
        
        print(f"📤 Sending prepare requests to {len(participants)} participants")
        transaction_data['state'] = TransactionState.PREPARING
        
        # Send prepare requests in parallel
        prepare_responses = {}
        
        with ThreadPoolExecutor(max_workers=len(participants)) as executor:
            # Submit prepare requests
            future_to_participant = {}
            
            for participant_id, participant in participants.items():
                participant_operations = operations.get(participant_id, [])
                prepare_request = PrepareRequest(
                    transaction_id=transaction_id,
                    coordinator_id=self.coordinator_id,
                    operations=participant_operations,
                    timeout_seconds=int(self.prepare_timeout)
                )
                
                future = executor.submit(participant.prepare, prepare_request)
                future_to_participant[future] = participant_id
            
            # Collect responses with timeout
            for future in as_completed(future_to_participant, timeout=self.prepare_timeout):
                participant_id = future_to_participant[future]
                try:
                    response = future.result()
                    prepare_responses[participant_id] = response
                    
                    vote_status = "✅ YES" if response.vote == VoteType.YES else "❌ NO"
                    print(f"📥 {participant_id}: {vote_status} - {response.message}")
                    
                except Exception as e:
                    # Timeout or error - count as NO vote
                    prepare_responses[participant_id] = PrepareResponse(
                        transaction_id=transaction_id,
                        participant_id=participant_id,
                        vote=VoteType.TIMEOUT,
                        message=f"Prepare timeout/error: {str(e)}"
                    )
                    self.stats['prepare_timeouts'] += 1
                    print(f"⏰ {participant_id}: TIMEOUT/ERROR - {str(e)}")
        
        transaction_data['prepare_responses'] = prepare_responses
        
        # Check if all participants voted YES
        all_yes = all(resp.vote == VoteType.YES for resp in prepare_responses.values())
        
        if all_yes:
            transaction_data['state'] = TransactionState.PREPARED
            print(f"✅ All participants prepared - proceeding to commit")
            return True
        else:
            no_votes = [pid for pid, resp in prepare_responses.items() 
                       if resp.vote != VoteType.YES]
            print(f"❌ Prepare failed - NO votes from: {no_votes}")
            return False
    
    def _commit_phase(self, transaction_data: Dict, decision: str) -> bool:
        """
        Phase 2: Send commit/abort requests to all participants
        """
        transaction_id = transaction_data['transaction_id']
        participants = transaction_data['participants']
        
        print(f"📤 Sending {decision} requests to {len(participants)} participants")
        
        # Send commit/abort requests in parallel
        commit_responses = {}
        
        with ThreadPoolExecutor(max_workers=len(participants)) as executor:
            # Submit requests
            future_to_participant = {}
            
            for participant_id, participant in participants.items():
                commit_request = CommitRequest(
                    transaction_id=transaction_id,
                    coordinator_id=self.coordinator_id,
                    decision=decision
                )
                
                future = executor.submit(participant.commit, commit_request)
                future_to_participant[future] = participant_id
            
            # Collect responses with timeout
            for future in as_completed(future_to_participant, timeout=self.commit_timeout):
                participant_id = future_to_participant[future]
                try:
                    response = future.result()
                    commit_responses[participant_id] = response
                    
                    status = "✅ SUCCESS" if response.success else "❌ FAILED"
                    print(f"📥 {participant_id}: {status} - {response.message}")
                    
                except Exception as e:
                    commit_responses[participant_id] = CommitResponse(
                        transaction_id=transaction_id,
                        participant_id=participant_id,
                        success=False,
                        message=f"Commit timeout/error: {str(e)}"
                    )
                    self.stats['commit_timeouts'] += 1
                    print(f"⏰ {participant_id}: TIMEOUT/ERROR - {str(e)}")
        
        transaction_data['commit_responses'] = commit_responses
        
        # Check if all participants succeeded
        all_success = all(resp.success for resp in commit_responses.values())
        
        if decision == "commit":
            return all_success
        else:
            # For abort, we don't strictly need all to succeed
            return True
    
    def get_stats(self) -> Dict:
        """Get coordinator statistics"""
        return self.stats.copy()

class TwoPhaseCommitSystem:
    """
    Complete 2PC System - Multiple coordinators और participants को manage करता है
    """
    
    def __init__(self):
        self.coordinators: Dict[str, TwoPhaseCommitCoordinator] = {}
        self.participants: Dict[str, TransactionParticipant] = {}
        
        print(f"🌐 Two-Phase Commit System initialized")
    
    def add_coordinator(self, coordinator_id: str, location: str = "Mumbai") -> TwoPhaseCommitCoordinator:
        """Add coordinator to system"""
        coordinator = TwoPhaseCommitCoordinator(coordinator_id, location)
        self.coordinators[coordinator_id] = coordinator
        return coordinator
    
    def add_participant(self, participant_id: str, service_type: str, 
                       location: str = "Mumbai") -> TransactionParticipant:
        """Add participant to system"""
        participant = TransactionParticipant(participant_id, service_type, location)
        self.participants[participant_id] = participant
        return participant
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        coordinator_stats = {}
        for coord_id, coordinator in self.coordinators.items():
            coordinator_stats[coord_id] = coordinator.get_stats()
        
        participant_stats = {}
        for part_id, participant in self.participants.items():
            participant_stats[part_id] = participant.get_stats()
        
        return {
            'coordinators': coordinator_stats,
            'participants': participant_stats,
            'total_coordinators': len(self.coordinators),
            'total_participants': len(self.participants)
        }

def paytm_transfer_demo():
    """
    Paytm Wallet to Bank Transfer - 2PC example
    """
    print(f"\n💰 DEMO: Paytm Wallet to Bank Transfer")
    print("-" * 45)
    
    # Create 2PC system
    system = TwoPhaseCommitSystem()
    
    # Add coordinator (Paytm Payment Service)
    coordinator = system.add_coordinator("paytm_payment_coordinator", "Mumbai")
    
    # Add participants
    wallet_service = system.add_participant("paytm_wallet", "Wallet Service", "Mumbai")
    bank_service = system.add_participant("sbi_bank_api", "Bank API", "Delhi")
    notification_service = system.add_participant("notification_service", "Notification Service", "Bangalore")
    
    # Initialize account balances
    wallet_service.data_store["user_rajesh"] = 5000  # Rajesh has ₹5000 in wallet
    bank_service.data_store["user_rajesh_bank"] = 10000  # ₹10000 in bank
    
    print(f"💼 Initial balances:")
    print(f"   Paytm Wallet: ₹{wallet_service.data_store['user_rajesh']}")
    print(f"   SBI Bank: ₹{bank_service.data_store['user_rajesh_bank']}")
    
    # Define transfer operations
    transfer_amount = 2000
    operations = {
        "paytm_wallet": [
            {
                "type": "debit",
                "account": "user_rajesh", 
                "amount": transfer_amount,
                "description": f"Transfer to bank ₹{transfer_amount}"
            }
        ],
        "sbi_bank_api": [
            {
                "type": "credit",
                "account": "user_rajesh_bank",
                "amount": transfer_amount,
                "description": f"Credit from Paytm ₹{transfer_amount}"
            }
        ],
        "notification_service": [
            {
                "type": "send_notification",
                "user": "user_rajesh",
                "message": f"₹{transfer_amount} transferred from Paytm to SBI Bank",
                "type": "SMS"
            }
        ]
    }
    
    # Execute transaction
    participants = [wallet_service, bank_service, notification_service]
    success = coordinator.execute_transaction(participants, operations)
    
    if success:
        print(f"\n🎉 Transfer successful!")
        print(f"💼 Final balances:")
        print(f"   Paytm Wallet: ₹{wallet_service.data_store.get('user_rajesh', 0)}")
        print(f"   SBI Bank: ₹{bank_service.data_store.get('user_rajesh_bank', 0)}")
    else:
        print(f"\n❌ Transfer failed - balances unchanged")

def flipkart_order_demo():
    """
    Flipkart Order Processing - Multiple services coordination
    """
    print(f"\n🛒 DEMO: Flipkart Order Processing")
    print("-" * 40)
    
    system = TwoPhaseCommitSystem()
    
    # Add coordinator
    coordinator = system.add_coordinator("flipkart_order_coordinator", "Bangalore")
    
    # Add participants
    inventory_service = system.add_participant("inventory_service", "Inventory Management", "Bangalore")
    payment_service = system.add_participant("payment_service", "Payment Gateway", "Mumbai") 
    shipping_service = system.add_participant("shipping_service", "Shipping Service", "Delhi")
    loyalty_service = system.add_participant("loyalty_service", "Loyalty Points", "Chennai")
    
    # Initialize data
    inventory_service.data_store["inventory_iphone14"] = 10  # 10 units available
    payment_service.data_store["user_priya_card"] = 100000   # Credit limit ₹1,00,000
    shipping_service.data_store["shipping_capacity_delhi"] = 100  # 100 slots available
    loyalty_service.data_store["user_priya_points"] = 5000   # 5000 loyalty points
    
    print(f"📦 Initial state:")
    print(f"   iPhone 14 inventory: {inventory_service.data_store['inventory_iphone14']} units")
    print(f"   Payment limit: ₹{payment_service.data_store['user_priya_card']}")
    print(f"   Shipping capacity: {shipping_service.data_store['shipping_capacity_delhi']} slots")
    print(f"   Loyalty points: {loyalty_service.data_store['user_priya_points']} points")
    
    # Define order operations
    order_operations = {
        "inventory_service": [
            {
                "type": "reserve_inventory",
                "item_id": "iphone14",
                "quantity": 1,
                "order_id": "ORD123456"
            }
        ],
        "payment_service": [
            {
                "type": "debit",
                "account": "user_priya_card",
                "amount": 79999,
                "description": "iPhone 14 purchase",
                "order_id": "ORD123456"
            }
        ],
        "shipping_service": [
            {
                "type": "reserve_inventory",
                "item_id": "shipping_capacity_delhi", 
                "quantity": 1,
                "order_id": "ORD123456"
            }
        ],
        "loyalty_service": [
            {
                "type": "credit",
                "account": "user_priya_points",
                "amount": 800,  # 800 points earned
                "description": "Points for iPhone 14 purchase"
            }
        ]
    }
    
    # Execute order transaction
    participants = [inventory_service, payment_service, shipping_service, loyalty_service]
    success = coordinator.execute_transaction(participants, order_operations)
    
    if success:
        print(f"\n🎉 Order placed successfully!")
        print(f"📦 Final state:")
        print(f"   iPhone 14 inventory: {inventory_service.data_store['inventory_iphone14']} units")
        print(f"   Payment charged: ₹79,999")
        print(f"   Shipping reserved: 1 slot")
        print(f"   Loyalty points: {loyalty_service.data_store['user_priya_points']} points")
    else:
        print(f"\n❌ Order failed - all operations rolled back")

def failure_scenarios_demo():
    """
    Demonstrate various failure scenarios in 2PC
    """
    print(f"\n💥 DEMO: Failure Scenarios")
    print("-" * 30)
    
    system = TwoPhaseCommitSystem()
    coordinator = system.add_coordinator("test_coordinator", "Mumbai")
    
    # Create participants with different failure characteristics
    reliable_service = system.add_participant("reliable_service", "Reliable Service", "Mumbai")
    reliable_service.failure_rate = 0.0  # Never fails
    
    unreliable_service = system.add_participant("unreliable_service", "Unreliable Service", "Delhi")
    unreliable_service.failure_rate = 0.8  # 80% failure rate
    
    slow_service = system.add_participant("slow_service", "Slow Service", "Bangalore")
    slow_service.slow_response_rate = 1.0  # Always slow
    slow_service.failure_rate = 0.0
    
    # Initialize data
    for service in [reliable_service, unreliable_service, slow_service]:
        service.data_store["test_account"] = 1000
    
    # Test operations
    test_operations = {
        "reliable_service": [{"type": "debit", "account": "test_account", "amount": 100}],
        "unreliable_service": [{"type": "debit", "account": "test_account", "amount": 100}],
        "slow_service": [{"type": "debit", "account": "test_account", "amount": 100}]
    }
    
    print(f"🧪 Testing transaction with mixed service reliability...")
    
    participants = [reliable_service, unreliable_service, slow_service]
    success = coordinator.execute_transaction(participants, test_operations)
    
    if success:
        print(f"✅ Transaction succeeded despite challenges")
    else:
        print(f"❌ Transaction failed due to service issues")

def performance_benchmark():
    """
    Performance benchmark of 2PC system
    """
    print(f"\n📈 PERFORMANCE BENCHMARK")
    print("-" * 30)
    
    system = TwoPhaseCommitSystem()
    coordinator = system.add_coordinator("benchmark_coordinator", "Mumbai")
    
    # Create multiple participants
    participants = []
    for i in range(5):
        participant = system.add_participant(f"service_{i}", f"Service {i}", f"Location {i}")
        participant.failure_rate = 0.05  # 5% failure rate
        participant.data_store["benchmark_account"] = 10000
        participants.append(participant)
    
    # Define simple operations
    operations = {}
    for i, participant in enumerate(participants):
        operations[participant.participant_id] = [
            {
                "type": "debit",
                "account": "benchmark_account", 
                "amount": 10,
                "description": f"Benchmark operation {i}"
            }
        ]
    
    # Run multiple transactions
    num_transactions = 10
    successful_transactions = 0
    start_time = time.time()
    
    print(f"🏁 Running {num_transactions} transactions...")
    
    for i in range(num_transactions):
        success = coordinator.execute_transaction(participants, operations)
        if success:
            successful_transactions += 1
        
        if (i + 1) % 3 == 0:
            print(f"   Completed {i + 1}/{num_transactions} transactions")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n📊 BENCHMARK RESULTS:")
    print(f"Total transactions: {num_transactions}")
    print(f"Successful transactions: {successful_transactions}")
    print(f"Success rate: {(successful_transactions/num_transactions)*100:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per transaction: {(total_time/num_transactions):.2f}s")
    print(f"Throughput: {num_transactions/total_time:.2f} txns/sec")

def main():
    """
    Main demonstration with Indian tech company scenarios
    """
    print("🇮🇳 Two-Phase Commit Protocol - Indian Tech Context")
    print("=" * 60)
    
    # Demo 1: Paytm wallet to bank transfer
    paytm_transfer_demo()
    
    # Demo 2: Flipkart order processing
    flipkart_order_demo()
    
    # Demo 3: Failure scenarios
    failure_scenarios_demo()
    
    # Demo 4: Performance benchmark
    performance_benchmark()
    
    print(f"\n✅ Two-Phase Commit demonstration complete!")
    
    print(f"\n📚 KEY LEARNINGS:")
    print(f"1. 2PC ensures ACID properties across distributed systems")
    print(f"2. Two phases: Prepare (vote) and Commit (execute)")
    print(f"3. All participants must agree (YES vote) to commit")
    print(f"4. Coordinator handles the protocol orchestration")
    print(f"5. Blocking protocol - participants wait for coordinator")
    print(f"6. Real applications:")
    print(f"   • Paytm wallet ↔ bank transfers")
    print(f"   • Flipkart order + payment + inventory")
    print(f"   • IRCTC booking + payment gateway")
    print(f"   • Distributed database transactions")
    print(f"7. Trade-offs:")
    print(f"   ✅ Strong consistency guarantee")
    print(f"   ✅ ACID compliance")
    print(f"   ❌ Blocking protocol")
    print(f"   ❌ Single point of failure (coordinator)")
    print(f"   ❌ High latency")
    print(f"8. Alternatives: Saga pattern, Event sourcing")

if __name__ == "__main__":
    main()