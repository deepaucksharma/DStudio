# Episode 47: Three-Phase Commit Protocol - "तीसरा कदम Safety के लिए"

## Episode Metadata
- **Title**: Three-Phase Commit Protocol - "तीसरा कदम Safety के लिए"
- **Episode**: 47
- **Series**: Distributed Systems Hindi Podcast
- **Duration**: 2+ hours comprehensive coverage
- **Target Audience**: Distributed Systems Engineers, Architects
- **Complexity Level**: Advanced
- **Prerequisites**: Two-Phase Commit Protocol, Distributed Consensus, Network Partitions

---

## Mumbai की कहानी: Property Registration में Triple Coordination

### Scene 1: The Complex Property Deal

मुंबई में एक बड़ी property deal हो रही है। **Rajesh** एक luxury apartment buy कर रहा है जिसकी value ₹5 crores है। लेकिन यह कोई simple purchase नहीं है - इसमें **तीन major players** involved हैं, और सभी को simultaneously agree करना होगा।

**Main Characters:**
- **Government Registrar (Coordinator)**: Final registration authority
- **Bank Manager (Financial Authority)**: Loan approval और fund transfer
- **Builder/Developer (Property Authority)**: Property ownership transfer
- **Buyer (Rajesh)**: Transaction initiator

### Scene 2: The Three-Phase Coordination Challenge

Traditional two-phase system में problem यह था कि अगर Government Registrar (coordinator) Phase 2 के दौरान crash हो जाए, तो Bank और Builder को पता नहीं चलता कि final decision क्या था। This creates a **blocking scenario**.

**New Three-Phase Process:**

```
Phase 1 (Prepare): 
- Government asks: "Can you proceed with ₹5 crore deal?"
- Bank: Checks loan approval, fund availability
- Builder: Checks property clearances, legal documents

Phase 2 (Pre-Commit):
- Government announces: "Decision is COMMIT - everyone prepare final steps"
- Bank: Prepares fund transfer, holds amount
- Builder: Prepares property papers, legal transfers
- All acknowledge: "Ready for final commit"

Phase 3 (Final Commit):
- Government announces: "Execute final commit"
- Bank: Transfers funds
- Builder: Transfers property ownership
- Registration completed
```

### Scene 3: The Critical Advantage - Non-Blocking Property

Traditional Two-Phase में problem:
```
Mumbai Property Deal (2PC):
Government → Bank & Builder: "Can you proceed?"
Bank → Government: "YES" 
Builder → Government: "YES"

[Government decides COMMIT और message send करता है]
[Network failure - Government का phone network down]

Bank और Builder waiting: "Commit करें या Abort?"
- Bank has locked ₹5 crores
- Builder has reserved property
- Deal stuck indefinitely!
```

Three-Phase में solution:
```
Mumbai Property Deal (3PC):
Phase 1 - Prepare:
Government → Bank & Builder: "Can you proceed?"
Bank → Government: "YES"
Builder → Government: "YES"

Phase 2 - Pre-Commit:
Government → Bank & Builder: "Decision is COMMIT, prepare final steps"
Bank → Government: "Prepared for final commit"
Builder → Government: "Prepared for final commit"

[Network failure होने पर भी]
Phase 3 - Final Commit:
Bank और Builder know: "Decision was COMMIT"
They can complete transaction without Government!
```

### Scene 4: The Monsoon Network Challenge

मुंबई में heavy monsoon आ गया है और communication networks intermittent हैं। Property deal middle में stuck है।

#### Scenario 1: Network Partition During Phase 2
```
Government (in Bandra) can communicate with Bank (Nariman Point)
But Builder (in Andheri) is cut off due to flooding

With 2PC: Deal would block completely
With 3PC: 
- If majority (Government + Bank) received Pre-Commit → Continue with COMMIT
- If majority didn't receive Pre-Commit → Safe to ABORT
```

#### Scenario 2: Coordinator Recovery After Crash
```
Government system crashes during Phase 2

2PC Recovery: 
- Bank और Builder don't know final decision
- Have to wait indefinitely or manually intervene

3PC Recovery:
- Bank और Builder check each other's state
- If both received Pre-Commit → Continue with COMMIT  
- If Pre-Commit not received → ABORT
- Non-blocking recovery possible!
```

---

## Theory Deep Dive: Three-Phase Commit Protocol

### Protocol Overview

Three-Phase Commit (3PC) एक **non-blocking atomic commitment protocol** है जो Two-Phase Commit की blocking limitation को solve करता है। इसमें एक additional **Pre-Commit phase** add करके network partitions और coordinator failures को handle करना possible हो जाता है।

### Key Innovations Over 2PC

#### 1. Non-Blocking Property
```
2PC में blocking scenarios:
- Coordinator fails after deciding but before communicating
- Participants can't determine final decision
- Resources remain locked indefinitely

3PC में non-blocking property:  
- Pre-commit phase provides decision visibility
- Participants can determine final decision independently
- Recovery possible without coordinator
```

#### 2. State Machine Enhancement
```
2PC States: INIT → PREPARED → COMMITTED/ABORTED
3PC States: INIT → PREPARED → PRE-COMMITTED → COMMITTED/ABORTED

Additional PRE-COMMITTED state allows:
- Clear decision point identification
- Safe recovery mechanisms
- Timeout-based progression
```

### Three Phases Detailed

#### Phase 1: Prepare (Same as 2PC)
```
Coordinator Actions:
1. Send PREPARE message to all participants
2. Wait for votes from all participants  
3. Collect YES/NO votes
4. Decide based on unanimous YES requirement

Participant Actions:
1. Receive PREPARE message
2. Lock resources, prepare local transaction
3. Vote YES if can commit, NO otherwise
4. Send vote to coordinator
```

#### Phase 2: Pre-Commit (New Addition)
```
Coordinator Actions:
1. If all voted YES: Send PRE-COMMIT to all participants
2. If any voted NO: Send ABORT to all participants  
3. Wait for acknowledgments from all participants
4. Log decision for recovery

Participant Actions:
1. Receive PRE-COMMIT or ABORT message
2. If PRE-COMMIT: Prepare for final commit, ACK coordinator
3. If ABORT: Release locks, cleanup, ACK coordinator  
4. Wait for final COMMIT message
```

#### Phase 3: Final Commit
```
Coordinator Actions:
1. Send final COMMIT message to all participants
2. Wait for completion acknowledgments
3. Log transaction completion

Participant Actions:
1. Receive COMMIT message
2. Execute final commit operation
3. Release all locks
4. Send completion ACK to coordinator
```

### Code Implementation

```python
import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any

class ThreePhaseCommitState(Enum):
    INITIATED = "INITIATED"
    PREPARING = "PREPARING" 
    PREPARED = "PREPARED"
    PRE_COMMITTING = "PRE_COMMITTING"
    PRE_COMMITTED = "PRE_COMMITTED"
    COMMITTING = "COMMITTING"
    COMMITTED = "COMMITTED"
    ABORTING = "ABORTING"
    ABORTED = "ABORTED"
    FAILED = "FAILED"

class MessageType(Enum):
    PREPARE = "PREPARE"
    VOTE_YES = "VOTE_YES"
    VOTE_NO = "VOTE_NO"
    PRE_COMMIT = "PRE_COMMIT"
    ABORT = "ABORT"
    ACK_PC = "ACK_PC"  # Acknowledge Pre-Commit
    ACK_ABORT = "ACK_ABORT"  # Acknowledge Abort
    DO_COMMIT = "DO_COMMIT"
    COMMITTED = "COMMITTED"

@dataclass
class ThreePhaseTransaction:
    transaction_id: str
    coordinator_id: str
    participants: List[str]
    operation_data: Dict[str, Any]
    timeout_ms: int
    created_at: float
    state: ThreePhaseCommitState = ThreePhaseCommitState.INITIATED

class ThreePhaseCommitCoordinator:
    """Three-Phase Commit Coordinator Implementation"""
    
    def __init__(self, coordinator_id: str):
        self.coordinator_id = coordinator_id
        self.participants: Dict[str, 'ThreePhaseParticipant'] = {}
        self.active_transactions: Dict[str, ThreePhaseTransaction] = {}
        self.transaction_log = ThreePhaseTransactionLog()
        self.logger = logging.getLogger(__name__)
        
    async def execute_transaction(self, operation_data: Dict[str, Any], 
                                participant_ids: List[str],
                                timeout_ms: int = 30000) -> 'ThreePhaseResult':
        """Execute distributed transaction using 3PC"""
        
        transaction_id = str(uuid.uuid4())
        start_time = time.time()
        
        transaction = ThreePhaseTransaction(
            transaction_id=transaction_id,
            coordinator_id=self.coordinator_id,
            participants=participant_ids,
            operation_data=operation_data,
            timeout_ms=timeout_ms,
            created_at=start_time
        )
        
        self.active_transactions[transaction_id] = transaction
        self.transaction_log.log_transaction_start(transaction)
        
        try:
            # Phase 1: Prepare
            self.logger.info(f"3PC Phase 1 (Prepare) starting for {transaction_id}")
            transaction.state = ThreePhaseCommitState.PREPARING
            
            phase1_result = await self.execute_phase1_prepare(transaction)
            
            if phase1_result.all_voted_yes():
                # Phase 2: Pre-Commit
                self.logger.info(f"3PC Phase 2 (Pre-Commit) starting for {transaction_id}")
                transaction.state = ThreePhaseCommitState.PRE_COMMITTING
                self.transaction_log.log_state_change(transaction, "PRE_COMMITTING")
                
                phase2_result = await self.execute_phase2_precommit(transaction)
                
                if phase2_result.all_acknowledged():
                    # Phase 3: Final Commit
                    self.logger.info(f"3PC Phase 3 (Final Commit) starting for {transaction_id}")
                    transaction.state = ThreePhaseCommitState.COMMITTING
                    
                    phase3_result = await self.execute_phase3_commit(transaction)
                    
                    if phase3_result.all_committed():
                        transaction.state = ThreePhaseCommitState.COMMITTED
                        return ThreePhaseResult(
                            transaction_id=transaction_id,
                            status='COMMITTED',
                            duration=time.time() - start_time
                        )
                    else:
                        return ThreePhaseResult(
                            transaction_id=transaction_id,
                            status='PARTIAL_COMMIT',
                            duration=time.time() - start_time,
                            error="Some participants failed final commit"
                        )
                else:
                    # Pre-commit failed - abort
                    await self.execute_abort_phase(transaction)
                    return ThreePhaseResult(
                        transaction_id=transaction_id,
                        status='ABORTED',
                        duration=time.time() - start_time,
                        abort_reason="Pre-commit phase failed"
                    )
            else:
                # Phase 1 failed - abort
                await self.execute_abort_phase(transaction)
                return ThreePhaseResult(
                    transaction_id=transaction_id,
                    status='ABORTED', 
                    duration=time.time() - start_time,
                    abort_reason=phase1_result.get_abort_reason()
                )
                
        except Exception as e:
            self.logger.error(f"3PC transaction {transaction_id} failed: {e}")
            await self.execute_abort_phase(transaction)
            
            return ThreePhaseResult(
                transaction_id=transaction_id,
                status='FAILED',
                duration=time.time() - start_time,
                error=str(e)
            )
            
        finally:
            if transaction_id in self.active_transactions:
                del self.active_transactions[transaction_id]
    
    async def execute_phase1_prepare(self, transaction: ThreePhaseTransaction) -> 'PreparePhaseResult':
        """Phase 1: Prepare - Same as 2PC prepare phase"""
        
        prepare_tasks = []
        timeout_seconds = transaction.timeout_ms / 1000.0
        
        for participant_id in transaction.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                self.send_prepare_message(participant, transaction, timeout_seconds)
            )
            prepare_tasks.append((participant_id, task))
        
        votes = {}
        for participant_id, task in prepare_tasks:
            try:
                vote = await task
                votes[participant_id] = vote
            except asyncio.TimeoutError:
                votes[participant_id] = 'NO'  # Timeout = NO vote
            except Exception:
                votes[participant_id] = 'NO'  # Exception = NO vote
        
        return PreparePhaseResult(transaction.transaction_id, votes)
    
    async def execute_phase2_precommit(self, transaction: ThreePhaseTransaction) -> 'PreCommitPhaseResult':
        """Phase 2: Pre-Commit - New phase in 3PC"""
        
        precommit_tasks = []
        
        for participant_id in transaction.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                participant.handle_precommit(transaction.transaction_id)
            )
            precommit_tasks.append((participant_id, task))
        
        acks = {}
        for participant_id, task in precommit_tasks:
            try:
                ack = await task
                acks[participant_id] = ack
            except Exception as e:
                self.logger.error(f"Pre-commit failed for {participant_id}: {e}")
                acks[participant_id] = False
        
        return PreCommitPhaseResult(transaction.transaction_id, acks)
    
    async def execute_phase3_commit(self, transaction: ThreePhaseTransaction) -> 'FinalCommitPhaseResult':
        """Phase 3: Final Commit"""
        
        commit_tasks = []
        
        for participant_id in transaction.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                participant.handle_final_commit(transaction.transaction_id)
            )
            commit_tasks.append((participant_id, task))
        
        commits = {}
        for participant_id, task in commit_tasks:
            try:
                success = await task
                commits[participant_id] = success
            except Exception as e:
                self.logger.error(f"Final commit failed for {participant_id}: {e}")
                commits[participant_id] = False
        
        return FinalCommitPhaseResult(transaction.transaction_id, commits)
    
    async def send_prepare_message(self, participant: 'ThreePhaseParticipant', 
                                 transaction: ThreePhaseTransaction, 
                                 timeout: float) -> str:
        """Send prepare message to participant"""
        try:
            response = await asyncio.wait_for(
                participant.handle_prepare(transaction),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            return 'NO'
        except Exception:
            return 'NO'

class ThreePhaseParticipant(ABC):
    """Abstract base class for 3PC participants"""
    
    def __init__(self, participant_id: str):
        self.participant_id = participant_id
        self.prepared_transactions: Dict[str, Any] = {}
        self.precommitted_transactions: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    @abstractmethod
    async def handle_prepare(self, transaction: ThreePhaseTransaction) -> str:
        """Phase 1: Handle prepare request"""
        pass
    
    @abstractmethod  
    async def handle_precommit(self, transaction_id: str) -> bool:
        """Phase 2: Handle pre-commit request"""
        pass
    
    @abstractmethod
    async def handle_final_commit(self, transaction_id: str) -> bool:
        """Phase 3: Handle final commit request"""
        pass
    
    @abstractmethod
    async def handle_abort(self, transaction_id: str) -> bool:
        """Handle abort request"""
        pass

class DatabaseThreePhaseParticipant(ThreePhaseParticipant):
    """Database participant for 3PC protocol"""
    
    def __init__(self, participant_id: str, database_connection):
        super().__init__(participant_id)
        self.db = database_connection
        
    async def handle_prepare(self, transaction: ThreePhaseTransaction) -> str:
        """Phase 1: Prepare database transaction"""
        try:
            # Begin database transaction
            db_txn = await self.db.begin_transaction()
            
            # Execute operations (but don't commit yet)
            operations = transaction.operation_data.get(self.participant_id, [])
            for operation in operations:
                await self.execute_operation(db_txn, operation)
            
            # Store prepared transaction
            self.prepared_transactions[transaction.transaction_id] = {
                'db_transaction': db_txn,
                'operations': operations,
                'prepared_at': time.time()
            }
            
            return 'YES'
            
        except Exception as e:
            self.logger.error(f"Prepare failed: {e}")
            return 'NO'
    
    async def handle_precommit(self, transaction_id: str) -> bool:
        """Phase 2: Handle pre-commit - prepare for final commit"""
        try:
            if transaction_id in self.prepared_transactions:
                prepared_txn = self.prepared_transactions[transaction_id]
                
                # Move to pre-committed state
                self.precommitted_transactions[transaction_id] = prepared_txn
                
                # Keep in prepared state as well until final commit
                self.logger.info(f"Pre-committed transaction {transaction_id}")
                return True
            else:
                self.logger.error(f"Transaction {transaction_id} not in prepared state")
                return False
                
        except Exception as e:
            self.logger.error(f"Pre-commit failed: {e}")
            return False
    
    async def handle_final_commit(self, transaction_id: str) -> bool:
        """Phase 3: Execute final commit"""
        try:
            if transaction_id in self.precommitted_transactions:
                precommitted_txn = self.precommitted_transactions[transaction_id]
                db_txn = precommitted_txn['db_transaction']
                
                # Execute final commit
                await db_txn.commit()
                
                # Cleanup
                if transaction_id in self.prepared_transactions:
                    del self.prepared_transactions[transaction_id]
                del self.precommitted_transactions[transaction_id]
                
                self.logger.info(f"Final commit successful for {transaction_id}")
                return True
            else:
                self.logger.error(f"Transaction {transaction_id} not in pre-committed state")
                return False
                
        except Exception as e:
            self.logger.error(f"Final commit failed: {e}")
            return False
    
    async def handle_abort(self, transaction_id: str) -> bool:
        """Handle transaction abort"""
        try:
            success = True
            
            # Cleanup prepared transaction
            if transaction_id in self.prepared_transactions:
                prepared_txn = self.prepared_transactions[transaction_id]
                db_txn = prepared_txn['db_transaction']
                await db_txn.rollback()
                del self.prepared_transactions[transaction_id]
                
            # Cleanup pre-committed transaction  
            if transaction_id in self.precommitted_transactions:
                precommitted_txn = self.precommitted_transactions[transaction_id]
                db_txn = precommitted_txn['db_transaction']
                await db_txn.rollback()
                del self.precommitted_transactions[transaction_id]
                
            self.logger.info(f"Abort successful for {transaction_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Abort failed: {e}")
            return False
    
    async def execute_operation(self, db_txn, operation):
        """Execute database operation within transaction"""
        if operation['type'] == 'INSERT':
            await db_txn.execute(operation['sql'], operation['params'])
        elif operation['type'] == 'UPDATE':
            await db_txn.execute(operation['sql'], operation['params'])
        elif operation['type'] == 'DELETE':
            await db_txn.execute(operation['sql'], operation['params'])
        else:
            raise ValueError(f"Unknown operation type: {operation['type']}")

# Result classes
@dataclass  
class ThreePhaseResult:
    transaction_id: str
    status: str
    duration: float
    error: Optional[str] = None
    abort_reason: Optional[str] = None

class PreparePhaseResult:
    def __init__(self, transaction_id: str, votes: Dict[str, str]):
        self.transaction_id = transaction_id
        self.votes = votes
    
    def all_voted_yes(self) -> bool:
        return all(vote == 'YES' for vote in self.votes.values())
    
    def get_abort_reason(self) -> str:
        no_votes = [pid for pid, vote in self.votes.items() if vote != 'YES']
        return f"Participants voted NO: {no_votes}"

class PreCommitPhaseResult:
    def __init__(self, transaction_id: str, acks: Dict[str, bool]):
        self.transaction_id = transaction_id
        self.acks = acks
    
    def all_acknowledged(self) -> bool:
        return all(self.acks.values())

class FinalCommitPhaseResult:
    def __init__(self, transaction_id: str, commits: Dict[str, bool]):
        self.transaction_id = transaction_id
        self.commits = commits
    
    def all_committed(self) -> bool:
        return all(self.commits.values())
```

---

## Non-Blocking Recovery Mechanisms

### Coordinator Failure Recovery

3PC का major advantage यह है कि coordinator failure के बाद भी participants non-blocking recovery कर सकते हैं।

#### Recovery Algorithm:

```python
class ThreePhaseRecoveryManager:
    """Recovery manager for 3PC coordinator failures"""
    
    def __init__(self):
        self.participant_network = ParticipantNetwork()
        self.logger = logging.getLogger(__name__)
    
    async def recover_from_coordinator_failure(self, failed_coordinator_id: str):
        """Recover transactions after coordinator failure"""
        
        # Get all participants that were communicating with failed coordinator
        affected_participants = self.participant_network.get_participants_for_coordinator(
            failed_coordinator_id
        )
        
        # Discover incomplete transactions
        incomplete_transactions = await self.discover_incomplete_transactions(
            affected_participants
        )
        
        for transaction_id in incomplete_transactions:
            await self.recover_transaction(transaction_id, affected_participants)
    
    async def recover_transaction(self, transaction_id: str, participants: List['ThreePhaseParticipant']):
        """Recover a specific transaction"""
        
        # Phase 1: Collect participant states
        participant_states = {}
        for participant in participants:
            try:
                state = await participant.get_transaction_state(transaction_id)
                participant_states[participant.participant_id] = state
            except Exception as e:
                self.logger.warning(f"Cannot reach participant {participant.participant_id}: {e}")
                participant_states[participant.participant_id] = 'UNKNOWN'
        
        # Phase 2: Determine recovery action based on states
        recovery_action = self.determine_recovery_action(participant_states)
        
        # Phase 3: Execute recovery
        await self.execute_recovery_action(transaction_id, participants, recovery_action)
    
    def determine_recovery_action(self, participant_states: Dict[str, str]) -> str:
        """Determine what recovery action to take"""
        
        states = list(participant_states.values())
        
        # If any participant is in COMMITTED state -> COMMIT all
        if 'COMMITTED' in states:
            return 'COMMIT'
        
        # If any participant is in PRE_COMMITTED state -> COMMIT all  
        if 'PRE_COMMITTED' in states:
            return 'COMMIT'
        
        # If all participants are in PREPARED state -> can go either way
        # Use timeout or majority decision
        if all(state == 'PREPARED' for state in states):
            return 'ABORT'  # Conservative approach
        
        # If any participant is in ABORTED state -> ABORT all
        if 'ABORTED' in states:
            return 'ABORT'
        
        # Default: ABORT for safety
        return 'ABORT'
    
    async def execute_recovery_action(self, transaction_id: str, 
                                    participants: List['ThreePhaseParticipant'],
                                    action: str):
        """Execute the determined recovery action"""
        
        if action == 'COMMIT':
            self.logger.info(f"Recovering transaction {transaction_id} with COMMIT")
            
            # First ensure all participants reach PRE_COMMITTED state
            for participant in participants:
                try:
                    state = await participant.get_transaction_state(transaction_id)
                    if state == 'PREPARED':
                        await participant.handle_precommit(transaction_id)
                except Exception as e:
                    self.logger.error(f"Failed to pre-commit {participant.participant_id}: {e}")
            
            # Then execute final commit
            for participant in participants:
                try:
                    await participant.handle_final_commit(transaction_id)
                except Exception as e:
                    self.logger.error(f"Failed to final commit {participant.participant_id}: {e}")
                    
        elif action == 'ABORT':
            self.logger.info(f"Recovering transaction {transaction_id} with ABORT")
            
            for participant in participants:
                try:
                    await participant.handle_abort(transaction_id)
                except Exception as e:
                    self.logger.error(f"Failed to abort {participant.participant_id}: {e}")

class DistributedRecoveryCoordinator:
    """Distributed recovery using participant coordination"""
    
    def __init__(self, participants: List['ThreePhaseParticipant']):
        self.participants = participants
        self.logger = logging.getLogger(__name__)
    
    async def initiate_distributed_recovery(self, transaction_id: str):
        """Participants coordinate among themselves for recovery"""
        
        # Step 1: Elect temporary coordinator
        temp_coordinator = await self.elect_temporary_coordinator()
        
        # Step 2: Temporary coordinator runs recovery protocol
        await temp_coordinator.coordinate_recovery(transaction_id, self.participants)
    
    async def elect_temporary_coordinator(self) -> 'ThreePhaseParticipant':
        """Elect temporary coordinator using simple algorithm"""
        
        # Simple election: participant with lowest ID becomes coordinator
        available_participants = []
        
        for participant in self.participants:
            try:
                # Check if participant is reachable
                await participant.ping()
                available_participants.append(participant)
            except:
                continue
        
        if not available_participants:
            raise Exception("No participants available for recovery")
        
        # Sort by participant ID and pick first
        available_participants.sort(key=lambda p: p.participant_id)
        elected_coordinator = available_participants[0]
        
        self.logger.info(f"Elected temporary coordinator: {elected_coordinator.participant_id}")
        return elected_coordinator
```

### Network Partition Handling

3PC का एक important feature यह है कि network partitions को handle कर सकता है without blocking.

```python
class NetworkPartitionHandler:
    """Handle network partitions in 3PC"""
    
    def __init__(self):
        self.partition_detector = NetworkPartitionDetector()
        self.logger = logging.getLogger(__name__)
    
    async def handle_partition_during_3pc(self, transaction_id: str, partition_info: 'PartitionInfo'):
        """Handle network partition during 3PC execution"""
        
        if partition_info.phase == 'PHASE_1':
            await self.handle_phase1_partition(transaction_id, partition_info)
        elif partition_info.phase == 'PHASE_2':
            await self.handle_phase2_partition(transaction_id, partition_info)
        elif partition_info.phase == 'PHASE_3':
            await self.handle_phase3_partition(transaction_id, partition_info)
    
    async def handle_phase1_partition(self, transaction_id: str, partition_info: 'PartitionInfo'):
        """Handle partition during Phase 1 (Prepare)"""
        
        # Phase 1 partition handling same as 2PC
        # Conservative approach: ABORT if can't reach all participants
        
        reachable_participants = partition_info.reachable_participants
        all_participants = partition_info.all_participants
        
        if len(reachable_participants) < len(all_participants):
            self.logger.info(f"Phase 1 partition detected, aborting {transaction_id}")
            
            # Abort reachable participants
            for participant in reachable_participants:
                try:
                    await participant.handle_abort(transaction_id)
                except Exception as e:
                    self.logger.error(f"Failed to abort {participant.participant_id}: {e}")
    
    async def handle_phase2_partition(self, transaction_id: str, partition_info: 'PartitionInfo'):
        """Handle partition during Phase 2 (Pre-Commit) - Critical phase"""
        
        reachable_participants = partition_info.reachable_participants
        all_participants = partition_info.all_participants
        
        # Check if majority of participants are reachable
        majority_threshold = len(all_participants) // 2 + 1
        
        if len(reachable_participants) >= majority_threshold:
            # Majority available - can proceed with decision
            self.logger.info(f"Phase 2 partition: majority available, proceeding")
            
            # Check if decision was already made
            decision_made = await self.check_if_decision_made(transaction_id, reachable_participants)
            
            if decision_made == 'PRE_COMMIT':
                # Continue with commit process
                await self.continue_commit_process(transaction_id, reachable_participants)
            else:
                # Abort transaction
                await self.abort_transaction(transaction_id, reachable_participants)
        else:
            # Minority available - must abort for safety
            self.logger.info(f"Phase 2 partition: minority available, aborting")
            await self.abort_transaction(transaction_id, reachable_participants)
    
    async def handle_phase3_partition(self, transaction_id: str, partition_info: 'PartitionInfo'):
        """Handle partition during Phase 3 (Final Commit)"""
        
        # Phase 3 partition is less problematic
        # Decision is already made and communicated in Phase 2
        
        reachable_participants = partition_info.reachable_participants
        
        self.logger.info(f"Phase 3 partition detected for {transaction_id}")
        
        # Check participant states to determine action
        for participant in reachable_participants:
            try:
                state = await participant.get_transaction_state(transaction_id)
                
                if state == 'PRE_COMMITTED':
                    # Should proceed with final commit
                    await participant.handle_final_commit(transaction_id)
                elif state == 'PREPARED':
                    # Shouldn't happen in Phase 3, but abort for safety
                    await participant.handle_abort(transaction_id)
                    
            except Exception as e:
                self.logger.error(f"Failed to handle partition for {participant.participant_id}: {e}")
    
    async def check_if_decision_made(self, transaction_id: str, 
                                   participants: List['ThreePhaseParticipant']) -> str:
        """Check if pre-commit decision was made"""
        
        for participant in participants:
            try:
                state = await participant.get_transaction_state(transaction_id)
                if state == 'PRE_COMMITTED':
                    return 'PRE_COMMIT'
                elif state == 'ABORTED':
                    return 'ABORT'
            except Exception:
                continue
        
        return 'UNKNOWN'
```

---

## Production Implementation Challenges

### Why 3PC Is Rarely Used in Practice

Despite इसके theoretical advantages, 3PC rarely production systems में use होता है। यहाँ main reasons हैं:

#### 1. Performance Overhead
```python
class PerformanceComparison:
    """Compare 2PC vs 3PC performance characteristics"""
    
    def compare_message_complexity(self):
        """Message complexity comparison"""
        participants = 'N'
        
        two_pc_messages = {
            'prepare_phase': f'{participants} (coordinator to participants)',
            'vote_phase': f'{participants} (participants to coordinator)', 
            'decision_phase': f'{participants} (coordinator to participants)',
            'ack_phase': f'{participants} (participants to coordinator)',
            'total': f'4 * {participants} = 4N messages'
        }
        
        three_pc_messages = {
            'prepare_phase': f'{participants} (coordinator to participants)',
            'vote_phase': f'{participants} (participants to coordinator)',
            'precommit_phase': f'{participants} (coordinator to participants)', 
            'precommit_ack_phase': f'{participants} (participants to coordinator)',
            'final_commit_phase': f'{participants} (coordinator to participants)',
            'final_ack_phase': f'{participants} (participants to coordinator)',
            'total': f'6 * {participants} = 6N messages'
        }
        
        return {
            '2PC': two_pc_messages,
            '3PC': three_pc_messages,
            'overhead': '50% more messages in 3PC'
        }
    
    def compare_latency(self):
        """Latency comparison"""
        return {
            '2PC': '2 network round trips',
            '3PC': '3 network round trips', 
            'overhead': '50% more latency in 3PC'
        }
    
    def compare_failure_scenarios(self):
        """Failure scenario handling comparison"""
        return {
            '2PC': {
                'coordinator_failure': 'Blocking - participants must wait',
                'participant_failure': 'Non-blocking - coordinator can decide',
                'network_partition': 'May block depending on partition'
            },
            '3PC': {
                'coordinator_failure': 'Non-blocking - participants can recover',
                'participant_failure': 'Non-blocking - majority can proceed', 
                'network_partition': 'Non-blocking with majority partition'
            }
        }

# Real-world performance impact measurement
class ProductionPerformanceAnalysis:
    """Analyze 3PC performance impact in production scenarios"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        
    def analyze_transaction_latency(self, transaction_logs: List[Dict]):
        """Analyze latency impact of extra round trip"""
        
        results = {
            'avg_network_latency_per_hop': 0,
            'participants_count': 0,
            'extra_latency_3pc': 0,
            'percentage_increase': 0
        }
        
        # Calculate from transaction logs
        network_latencies = []
        for log in transaction_logs:
            if 'network_latency' in log:
                network_latencies.append(log['network_latency'])
        
        if network_latencies:
            results['avg_network_latency_per_hop'] = sum(network_latencies) / len(network_latencies)
            results['participants_count'] = len(transaction_logs[0].get('participants', []))
            
            # Extra latency = one additional round trip
            results['extra_latency_3pc'] = results['avg_network_latency_per_hop']
            
            # Percentage increase over 2PC
            two_pc_total_latency = 2 * results['avg_network_latency_per_hop']  
            three_pc_total_latency = 3 * results['avg_network_latency_per_hop']
            
            results['percentage_increase'] = (
                (three_pc_total_latency - two_pc_total_latency) / two_pc_total_latency
            ) * 100
        
        return results
    
    def analyze_resource_utilization(self, system_metrics: Dict):
        """Analyze resource utilization increase"""
        
        return {
            'additional_log_entries': '50% more transaction log entries',
            'memory_overhead': '20-30% more memory for state tracking',
            'cpu_overhead': '15-25% more CPU for message processing',
            'storage_overhead': '40-50% more storage for recovery logs'
        }
```

#### 2. Modern Alternatives Are Better

```python
class ModernAlternativesToThreePC:
    """Modern alternatives that solve 3PC's problems more efficiently"""
    
    def saga_pattern_comparison(self):
        """Saga pattern as alternative to 3PC"""
        
        return {
            'saga_advantages': {
                'performance': 'No blocking, asynchronous execution',
                'scalability': 'Scales to many participants', 
                'complexity': 'Simpler implementation',
                'failure_handling': 'Compensating actions for rollback'
            },
            'saga_disadvantages': {
                'consistency': 'Eventual consistency only',
                'isolation': 'No transaction isolation', 
                'complexity': 'Business logic must handle compensation'
            },
            'use_cases': {
                'good_for': 'Microservices, long-running processes, high-scale systems',
                'not_good_for': 'Strong consistency requirements, financial transactions'
            }
        }
    
    def event_sourcing_comparison(self):
        """Event sourcing as alternative"""
        
        return {
            'advantages': {
                'auditability': 'Complete transaction history',
                'recoverability': 'Can replay events for recovery',
                'scalability': 'Event-driven, highly scalable'
            },
            'disadvantages': {
                'complexity': 'Complex event handling and replay logic',
                'consistency': 'Eventually consistent',
                'storage': 'Higher storage requirements'
            }
        }
    
    def modern_consensus_algorithms(self):
        """Modern consensus algorithms (Raft, PBFT, etc.)"""
        
        return {
            'raft': {
                'advantages': 'Simple, proven, widely adopted',
                'disadvantages': 'Leader-based, not Byzantine fault tolerant',
                'use_cases': 'Distributed databases, configuration management'
            },
            'pbft': {
                'advantages': 'Byzantine fault tolerance, strong consistency',
                'disadvantages': 'Complex, high message overhead',
                'use_cases': 'Blockchain, high-security systems'
            },
            'practical_choice': 'Most systems use Raft or Paxos instead of 3PC'
        }

# Example: Saga implementation as 3PC alternative
class SagaTransactionCoordinator:
    """Saga pattern implementation as alternative to 3PC"""
    
    def __init__(self):
        self.saga_log = SagaTransactionLog()
        self.compensation_handlers = {}
        
    async def execute_saga(self, saga_definition: 'SagaDefinition') -> 'SagaResult':
        """Execute saga transaction"""
        
        saga_id = str(uuid.uuid4())
        executed_steps = []
        
        try:
            # Execute steps sequentially
            for step in saga_definition.steps:
                step_result = await self.execute_saga_step(step, saga_id)
                
                if step_result.success:
                    executed_steps.append(step)
                    self.saga_log.log_step_success(saga_id, step)
                else:
                    # Step failed - run compensation for all executed steps
                    await self.compensate_executed_steps(saga_id, executed_steps)
                    return SagaResult(saga_id, 'FAILED', step_result.error)
            
            # All steps successful
            self.saga_log.log_saga_success(saga_id)
            return SagaResult(saga_id, 'SUCCESS')
            
        except Exception as e:
            # Exception during saga execution
            await self.compensate_executed_steps(saga_id, executed_steps)
            return SagaResult(saga_id, 'FAILED', str(e))
    
    async def execute_saga_step(self, step: 'SagaStep', saga_id: str) -> 'StepResult':
        """Execute individual saga step"""
        
        try:
            result = await step.execute()
            return StepResult(success=True, data=result)
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def compensate_executed_steps(self, saga_id: str, executed_steps: List['SagaStep']):
        """Run compensation for executed steps in reverse order"""
        
        # Execute compensations in reverse order
        for step in reversed(executed_steps):
            try:
                if step.compensation_action:
                    await step.compensation_action.execute()
                    self.saga_log.log_compensation_success(saga_id, step)
            except Exception as e:
                self.saga_log.log_compensation_failure(saga_id, step, str(e))
                # Continue with other compensations even if one fails
```

#### 3. Network Assumptions Don't Hold

```python
class NetworkAssumptionAnalysis:
    """Analyze network assumptions in 3PC vs reality"""
    
    def analyze_3pc_assumptions(self):
        """3PC makes assumptions that don't hold in practice"""
        
        return {
            'assumptions': {
                'reliable_network': '3PC assumes network will eventually deliver messages',
                'bounded_delays': 'Assumes network delays are bounded and predictable',
                'failure_detection': 'Assumes failures can be reliably detected',
                'no_byzantine_failures': 'Assumes participants are honest (crash-stop model)'
            },
            'reality': {
                'unreliable_network': 'Networks can lose messages, have partitions',
                'unbounded_delays': 'Network delays can be arbitrary and unpredictable',
                'imperfect_failure_detection': 'Difficult to distinguish slow vs failed nodes',
                'byzantine_behavior': 'Real systems can have buggy or malicious behavior'
            },
            'consequences': {
                'false_progress': '3PC may make progress when it shouldn\'t',
                'safety_violations': 'Can violate consistency guarantees',
                'availability_issues': 'May not be as available as claimed'
            }
        }
    
    def real_world_network_characteristics(self):
        """Real-world network characteristics that break 3PC assumptions"""
        
        return {
            'cloud_environments': {
                'aws_cross_az': 'Higher latency between availability zones',
                'network_variability': 'Variable network performance',
                'partial_failures': 'Complex failure modes'
            },
            'geographical_distribution': {
                'wan_latency': 'High WAN latencies (100ms+)',
                'packet_loss': 'Higher packet loss rates',
                'jitter': 'Variable network timing'
            },
            'mobile_networks': {
                'intermittent_connectivity': 'Frequent network state changes',
                'high_latency': 'Variable high latency',
                'bandwidth_constraints': 'Limited bandwidth'
            }
        }
```

---

## 2025 Modern Use Cases और Alternatives

### 1. Blockchain Consensus Integration

हाल के सालों में blockchain systems में 3PC के concepts का use हो रहा है, लेकिन modified forms में:

```python
class BlockchainThreePhaseConsensus:
    """Modified 3PC for blockchain consensus"""
    
    def __init__(self, blockchain_network):
        self.blockchain = blockchain_network
        self.validators = blockchain_network.get_validators()
        self.consensus_log = BlockchainConsensusLog()
        
    async def propose_block(self, block_data: Dict) -> 'BlockProposal':
        """Phase 1: Block proposal (similar to 3PC prepare)"""
        
        block_hash = self.calculate_block_hash(block_data)
        proposal = BlockProposal(
            block_hash=block_hash,
            block_data=block_data,
            proposer=self.blockchain.get_current_validator(),
            timestamp=time.time()
        )
        
        # Send proposal to all validators
        votes = {}
        for validator in self.validators:
            try:
                vote = await validator.validate_block_proposal(proposal)
                votes[validator.address] = vote
            except Exception as e:
                votes[validator.address] = BlockVote(False, str(e))
        
        return BlockVoteResult(proposal, votes)
    
    async def pre_commit_block(self, proposal: 'BlockProposal', 
                             votes: 'BlockVoteResult') -> 'PreCommitResult':
        """Phase 2: Pre-commit (validators prepare to finalize)"""
        
        if votes.has_majority_approval():
            # Send pre-commit messages
            pre_commit_msg = PreCommitMessage(
                block_hash=proposal.block_hash,
                round=self.blockchain.get_current_round()
            )
            
            pre_commit_votes = {}
            for validator in self.validators:
                try:
                    response = await validator.handle_pre_commit(pre_commit_msg)
                    pre_commit_votes[validator.address] = response
                except Exception as e:
                    pre_commit_votes[validator.address] = False
            
            return PreCommitResult(proposal, pre_commit_votes)
        else:
            return PreCommitResult(proposal, {}, aborted=True)
    
    async def finalize_block(self, pre_commit_result: 'PreCommitResult') -> 'FinalizationResult':
        """Phase 3: Final block commitment"""
        
        if pre_commit_result.has_majority_pre_commits():
            # Finalize block on blockchain
            finalization_msg = FinalizationMessage(
                block_hash=pre_commit_result.proposal.block_hash
            )
            
            finalization_results = {}
            for validator in self.validators:
                try:
                    result = await validator.finalize_block(finalization_msg)
                    finalization_results[validator.address] = result
                except Exception as e:
                    finalization_results[validator.address] = False
            
            # Update blockchain state
            if self.majority_finalized(finalization_results):
                self.blockchain.add_finalized_block(pre_commit_result.proposal)
                return FinalizationResult(success=True, block_hash=pre_commit_result.proposal.block_hash)
            else:
                return FinalizationResult(success=False, error="Majority finalization failed")
        
        else:
            return FinalizationResult(success=False, error="Insufficient pre-commits")

class TendermintConsensus:
    """Tendermint-style consensus (inspired by 3PC concepts)"""
    
    def __init__(self):
        self.validators = []
        self.current_height = 0
        self.current_round = 0
        
    async def consensus_round(self, proposed_block: 'Block') -> 'ConsensusResult':
        """Execute one consensus round with 3-phase approach"""
        
        # Phase 1: Propose
        proposal_result = await self.propose_phase(proposed_block)
        if not proposal_result.success:
            return ConsensusResult(False, "Proposal failed")
        
        # Phase 2: Prevote (similar to pre-commit)
        prevote_result = await self.prevote_phase(proposed_block)
        if not prevote_result.has_majority():
            return ConsensusResult(False, "Prevote failed")
        
        # Phase 3: Precommit and commit
        precommit_result = await self.precommit_phase(proposed_block)
        if precommit_result.has_majority():
            await self.commit_block(proposed_block)
            return ConsensusResult(True, f"Block committed at height {self.current_height}")
        else:
            return ConsensusResult(False, "Precommit failed")
    
    async def propose_phase(self, block: 'Block') -> 'ProposalResult':
        """Phase 1: Block proposal"""
        proposer = self.get_round_proposer()
        
        if proposer.is_valid_proposer():
            proposal = BlockProposal(block, self.current_height, self.current_round)
            await self.broadcast_proposal(proposal)
            return ProposalResult(True)
        else:
            return ProposalResult(False, "Invalid proposer")
    
    async def prevote_phase(self, block: 'Block') -> 'PrevoteResult':
        """Phase 2: Prevote (validators indicate readiness)"""
        prevotes = {}
        
        for validator in self.validators:
            try:
                prevote = await validator.send_prevote(block, self.current_height, self.current_round)
                prevotes[validator.address] = prevote
            except Exception:
                prevotes[validator.address] = PrevoteMessage(False)
        
        return PrevoteResult(prevotes)
    
    async def precommit_phase(self, block: 'Block') -> 'PrecommitResult':
        """Phase 3: Precommit (final commitment preparation)"""
        precommits = {}
        
        for validator in self.validators:
            try:
                precommit = await validator.send_precommit(block, self.current_height, self.current_round)
                precommits[validator.address] = precommit
            except Exception:
                precommits[validator.address] = PrecommitMessage(False)
        
        return PrecommitResult(precommits)
```

### 2. Microservices Orchestration

Modern microservices architectures में 3PC concepts का use distributed transaction orchestration के लिए:

```python
class MicroservicesThreePhaseOrchestrator:
    """3PC-inspired orchestration for microservices"""
    
    def __init__(self):
        self.services = {}
        self.orchestration_log = OrchestrationLog()
        self.saga_manager = SagaManager()
        
    async def execute_distributed_operation(self, operation: 'DistributedOperation') -> 'OperationResult':
        """Execute operation across multiple microservices using 3PC principles"""
        
        operation_id = str(uuid.uuid4())
        
        # Phase 1: Service preparation (check availability and preconditions)
        preparation_result = await self.prepare_services(operation, operation_id)
        if not preparation_result.all_services_ready():
            return OperationResult(operation_id, 'FAILED', 'Service preparation failed')
        
        # Phase 2: Service pre-commit (reserve resources, prepare for execution)
        precommit_result = await self.precommit_services(operation, operation_id)
        if not precommit_result.all_services_precommitted():
            # Rollback prepared services
            await self.rollback_prepared_services(operation, operation_id)
            return OperationResult(operation_id, 'FAILED', 'Service pre-commit failed')
        
        # Phase 3: Service execution (final execution)
        execution_result = await self.execute_services(operation, operation_id)
        if execution_result.all_services_executed():
            return OperationResult(operation_id, 'SUCCESS')
        else:
            # Partial execution - use saga compensation
            await self.saga_manager.compensate_partial_execution(operation, operation_id, execution_result)
            return OperationResult(operation_id, 'PARTIAL_SUCCESS', 'Some services failed, compensated')
    
    async def prepare_services(self, operation: 'DistributedOperation', operation_id: str) -> 'ServicePreparationResult':
        """Phase 1: Prepare all involved services"""
        
        preparation_results = {}
        
        for service_name, service_operation in operation.service_operations.items():
            service = self.services[service_name]
            
            try:
                # Check service availability and validate operation
                preparation = await service.prepare_operation(service_operation, operation_id)
                preparation_results[service_name] = preparation
                
            except ServiceUnavailableError as e:
                preparation_results[service_name] = ServicePreparation(False, f"Service unavailable: {e}")
            except ValidationError as e:
                preparation_results[service_name] = ServicePreparation(False, f"Validation failed: {e}")
            except Exception as e:
                preparation_results[service_name] = ServicePreparation(False, f"Preparation error: {e}")
        
        return ServicePreparationResult(operation_id, preparation_results)
    
    async def precommit_services(self, operation: 'DistributedOperation', operation_id: str) -> 'ServicePrecommitResult':
        """Phase 2: Pre-commit all services (reserve resources)"""
        
        precommit_results = {}
        
        for service_name, service_operation in operation.service_operations.items():
            service = self.services[service_name]
            
            try:
                # Reserve resources, lock data, prepare for execution
                precommit = await service.precommit_operation(service_operation, operation_id)
                precommit_results[service_name] = precommit
                
            except ResourceUnavailableError as e:
                precommit_results[service_name] = ServicePrecommit(False, f"Resources unavailable: {e}")
            except Exception as e:
                precommit_results[service_name] = ServicePrecommit(False, f"Pre-commit error: {e}")
        
        return ServicePrecommitResult(operation_id, precommit_results)
    
    async def execute_services(self, operation: 'DistributedOperation', operation_id: str) -> 'ServiceExecutionResult':
        """Phase 3: Execute final operations on all services"""
        
        execution_results = {}
        
        for service_name, service_operation in operation.service_operations.items():
            service = self.services[service_name]
            
            try:
                # Execute final operation
                execution = await service.execute_operation(service_operation, operation_id)
                execution_results[service_name] = execution
                
            except Exception as e:
                execution_results[service_name] = ServiceExecution(False, f"Execution error: {e}")
        
        return ServiceExecutionResult(operation_id, execution_results)

# Example: E-commerce order processing with 3PC-style orchestration
class ECommerceOrderProcessor:
    """E-commerce order processing using 3PC principles"""
    
    def __init__(self):
        self.inventory_service = InventoryService()
        self.payment_service = PaymentService()
        self.shipping_service = ShippingService()
        self.notification_service = NotificationService()
        
    async def process_order(self, order: 'Order') -> 'OrderResult':
        """Process order using 3PC-style coordination"""
        
        order_id = order.order_id
        
        try:
            # Phase 1: Prepare all services
            inventory_preparation = await self.inventory_service.check_availability(order.items, order_id)
            payment_preparation = await self.payment_service.validate_payment_method(order.payment, order_id)
            shipping_preparation = await self.shipping_service.validate_shipping_address(order.shipping, order_id)
            
            if not (inventory_preparation.success and payment_preparation.success and shipping_preparation.success):
                return OrderResult(order_id, 'FAILED', 'Order preparation failed')
            
            # Phase 2: Pre-commit (reserve resources)
            inventory_reservation = await self.inventory_service.reserve_items(order.items, order_id)
            payment_hold = await self.payment_service.hold_payment(order.payment, order_id)
            shipping_booking = await self.shipping_service.book_shipping_slot(order.shipping, order_id)
            
            if not (inventory_reservation.success and payment_hold.success and shipping_booking.success):
                # Release any successful reservations
                await self.release_reservations(order_id, inventory_reservation, payment_hold, shipping_booking)
                return OrderResult(order_id, 'FAILED', 'Resource reservation failed')
            
            # Phase 3: Final execution
            inventory_update = await self.inventory_service.update_inventory(order.items, order_id)
            payment_charge = await self.payment_service.charge_payment(order.payment, order_id)
            shipping_create = await self.shipping_service.create_shipment(order.shipping, order_id)
            
            if inventory_update.success and payment_charge.success and shipping_create.success:
                # Send confirmation notification
                await self.notification_service.send_order_confirmation(order, order_id)
                return OrderResult(order_id, 'SUCCESS')
            else:
                # Partial failure - need compensation
                await self.compensate_partial_order(order, order_id, inventory_update, payment_charge, shipping_create)
                return OrderResult(order_id, 'FAILED', 'Order execution failed, compensated')
                
        except Exception as e:
            # Unexpected error - cleanup and fail
            await self.cleanup_failed_order(order_id)
            return OrderResult(order_id, 'FAILED', f'Unexpected error: {e}')
    
    async def release_reservations(self, order_id: str, inventory_res, payment_hold, shipping_book):
        """Release reservations in case of pre-commit failure"""
        
        if inventory_res.success:
            await self.inventory_service.release_reservation(order_id)
        
        if payment_hold.success:
            await self.payment_service.release_hold(order_id)
            
        if shipping_book.success:
            await self.shipping_service.cancel_booking(order_id)
    
    async def compensate_partial_order(self, order: 'Order', order_id: str, 
                                     inventory_result, payment_result, shipping_result):
        """Compensate for partial order execution"""
        
        # Reverse successful operations
        if inventory_result.success:
            await self.inventory_service.reverse_inventory_update(order.items, order_id)
        
        if payment_result.success:
            await self.payment_service.refund_payment(order.payment, order_id)
            
        if shipping_result.success:
            await self.shipping_service.cancel_shipment(order_id)
```

### 3. Database Replication with 3PC

Modern distributed databases में 3PC concepts का enhanced use:

```python
class DatabaseReplicationWithThreePhase:
    """Database replication using enhanced 3PC protocol"""
    
    def __init__(self, replicas: List['DatabaseReplica']):
        self.replicas = replicas
        self.replication_log = ReplicationLog()
        self.leader_election = LeaderElection()
        
    async def replicate_transaction(self, transaction: 'DatabaseTransaction') -> 'ReplicationResult':
        """Replicate transaction across database replicas using 3PC"""
        
        transaction_id = transaction.transaction_id
        leader = await self.leader_election.get_current_leader()
        
        if leader != self:
            # Forward to leader
            return await leader.replicate_transaction(transaction)
        
        try:
            # Phase 1: Prepare replicas
            prepare_result = await self.prepare_replicas(transaction)
            if not prepare_result.majority_prepared():
                return ReplicationResult(transaction_id, 'ABORTED', 'Majority preparation failed')
            
            # Phase 2: Pre-commit replicas
            precommit_result = await self.precommit_replicas(transaction)
            if not precommit_result.majority_precommitted():
                await self.abort_transaction_on_replicas(transaction)
                return ReplicationResult(transaction_id, 'ABORTED', 'Majority pre-commit failed')
            
            # Phase 3: Final commit
            commit_result = await self.commit_transaction_on_replicas(transaction)
            if commit_result.majority_committed():
                return ReplicationResult(transaction_id, 'COMMITTED')
            else:
                # Partial commit - this is problematic, need recovery
                await self.initiate_replica_recovery(transaction)
                return ReplicationResult(transaction_id, 'PARTIAL_COMMIT', 'Recovery initiated')
                
        except Exception as e:
            await self.abort_transaction_on_replicas(transaction)
            return ReplicationResult(transaction_id, 'FAILED', str(e))
    
    async def prepare_replicas(self, transaction: 'DatabaseTransaction') -> 'ReplicaPreparationResult':
        """Phase 1: Prepare transaction on all replicas"""
        
        preparation_tasks = []
        for replica in self.replicas:
            task = asyncio.create_task(replica.prepare_transaction(transaction))
            preparation_tasks.append((replica.replica_id, task))
        
        preparation_results = {}
        for replica_id, task in preparation_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=5.0)  # 5 second timeout
                preparation_results[replica_id] = result
            except asyncio.TimeoutError:
                preparation_results[replica_id] = PreparationResult(False, "Timeout")
            except Exception as e:
                preparation_results[replica_id] = PreparationResult(False, str(e))
        
        return ReplicaPreparationResult(transaction.transaction_id, preparation_results)
    
    async def precommit_replicas(self, transaction: 'DatabaseTransaction') -> 'ReplicaPrecommitResult':
        """Phase 2: Pre-commit transaction on all replicas"""
        
        precommit_tasks = []
        for replica in self.replicas:
            task = asyncio.create_task(replica.precommit_transaction(transaction))
            precommit_tasks.append((replica.replica_id, task))
        
        precommit_results = {}
        for replica_id, task in precommit_tasks:
            try:
                result = await task
                precommit_results[replica_id] = result
            except Exception as e:
                precommit_results[replica_id] = PrecommitResult(False, str(e))
        
        return ReplicaPrecommitResult(transaction.transaction_id, precommit_results)
    
    async def commit_transaction_on_replicas(self, transaction: 'DatabaseTransaction') -> 'ReplicaCommitResult':
        """Phase 3: Final commit on all replicas"""
        
        commit_tasks = []
        for replica in self.replicas:
            task = asyncio.create_task(replica.commit_transaction(transaction))
            commit_tasks.append((replica.replica_id, task))
        
        commit_results = {}
        for replica_id, task in commit_tasks:
            try:
                result = await task
                commit_results[replica_id] = result
            except Exception as e:
                commit_results[replica_id] = CommitResult(False, str(e))
        
        return ReplicaCommitResult(transaction.transaction_id, commit_results)

class DatabaseReplica:
    """Individual database replica implementing 3PC participant"""
    
    def __init__(self, replica_id: str, database_connection):
        self.replica_id = replica_id
        self.db = database_connection
        self.prepared_transactions = {}
        self.precommitted_transactions = {}
        
    async def prepare_transaction(self, transaction: 'DatabaseTransaction') -> 'PreparationResult':
        """Phase 1: Prepare transaction on this replica"""
        
        try:
            # Start local transaction
            local_txn = await self.db.begin_transaction()
            
            # Execute transaction operations
            for operation in transaction.operations:
                await self.execute_operation(local_txn, operation)
            
            # Store prepared transaction (don't commit yet)
            self.prepared_transactions[transaction.transaction_id] = {
                'local_transaction': local_txn,
                'prepared_at': time.time()
            }
            
            return PreparationResult(True, "Prepared successfully")
            
        except Exception as e:
            return PreparationResult(False, f"Preparation failed: {e}")
    
    async def precommit_transaction(self, transaction: 'DatabaseTransaction') -> 'PrecommitResult':
        """Phase 2: Pre-commit transaction (prepare for final commit)"""
        
        try:
            if transaction.transaction_id not in self.prepared_transactions:
                return PrecommitResult(False, "Transaction not prepared")
            
            prepared_data = self.prepared_transactions[transaction.transaction_id]
            
            # Move to pre-committed state
            self.precommitted_transactions[transaction.transaction_id] = prepared_data
            
            # Write pre-commit log entry for recovery
            await self.write_precommit_log(transaction.transaction_id)
            
            return PrecommitResult(True, "Pre-committed successfully")
            
        except Exception as e:
            return PrecommitResult(False, f"Pre-commit failed: {e}")
    
    async def commit_transaction(self, transaction: 'DatabaseTransaction') -> 'CommitResult':
        """Phase 3: Final commit of transaction"""
        
        try:
            if transaction.transaction_id not in self.precommitted_transactions:
                return CommitResult(False, "Transaction not pre-committed")
            
            precommitted_data = self.precommitted_transactions[transaction.transaction_id]
            local_txn = precommitted_data['local_transaction']
            
            # Execute final commit
            await local_txn.commit()
            
            # Cleanup
            if transaction.transaction_id in self.prepared_transactions:
                del self.prepared_transactions[transaction.transaction_id]
            del self.precommitted_transactions[transaction.transaction_id]
            
            # Write commit log entry
            await self.write_commit_log(transaction.transaction_id)
            
            return CommitResult(True, "Committed successfully")
            
        except Exception as e:
            return CommitResult(False, f"Commit failed: {e}")
    
    async def abort_transaction(self, transaction_id: str) -> 'AbortResult':
        """Abort transaction and cleanup"""
        
        try:
            # Cleanup prepared transaction
            if transaction_id in self.prepared_transactions:
                prepared_data = self.prepared_transactions[transaction_id]
                local_txn = prepared_data['local_transaction']
                await local_txn.rollback()
                del self.prepared_transactions[transaction_id]
            
            # Cleanup pre-committed transaction
            if transaction_id in self.precommitted_transactions:
                precommitted_data = self.precommitted_transactions[transaction_id]
                local_txn = precommitted_data['local_transaction']
                await local_txn.rollback()
                del self.precommitted_transactions[transaction_id]
            
            return AbortResult(True, "Aborted successfully")
            
        except Exception as e:
            return AbortResult(False, f"Abort failed: {e}")
```

---

## Comparison with Modern Alternatives

### 3PC vs Raft Consensus

```python
class ConsensusAlgorithmComparison:
    """Compare 3PC with modern consensus algorithms"""
    
    def compare_with_raft(self):
        """Compare 3PC vs Raft consensus"""
        
        return {
            'message_complexity': {
                '3PC': 'O(N) per phase, 3 phases = 3N messages',
                'Raft': 'O(N) per round, typically 1-2 rounds = 1-2N messages',
                'winner': 'Raft (fewer messages)'
            },
            'failure_handling': {
                '3PC': 'Non-blocking but assumes synchronous network',
                'Raft': 'Leader-based, handles asynchronous networks well',
                'winner': 'Raft (better practical failure handling)'
            },
            'consistency_guarantees': {
                '3PC': 'Strong consistency with non-blocking property',
                'Raft': 'Strong consistency with leader-based coordination',
                'winner': 'Tie (both provide strong consistency)'
            },
            'implementation_complexity': {
                '3PC': 'Complex state management, recovery protocols',
                'Raft': 'Simpler conceptually, well-understood',
                'winner': 'Raft (simpler implementation)'
            },
            'performance': {
                '3PC': 'Higher latency due to 3 phases',
                'Raft': 'Lower latency, efficient log replication',
                'winner': 'Raft (better performance)'
            },
            'practical_adoption': {
                '3PC': 'Rarely used in production',
                'Raft': 'Widely adopted (etcd, Consul, etc.)',
                'winner': 'Raft (proven in practice)'
            }
        }
    
    def compare_with_pbft(self):
        """Compare 3PC vs Practical Byzantine Fault Tolerance"""
        
        return {
            'fault_model': {
                '3PC': 'Crash-stop failures only',
                'PBFT': 'Byzantine (arbitrary) failures',
                'winner': 'PBFT (handles more failure types)'
            },
            'message_complexity': {
                '3PC': 'O(N) messages per phase',
                'PBFT': 'O(N²) messages per round',
                'winner': '3PC (lower message complexity)'
            },
            'performance': {
                '3PC': 'Better performance in non-Byzantine scenarios',
                'PBFT': 'Higher overhead due to Byzantine protection',
                'winner': '3PC (for crash-stop scenarios)'
            },
            'security': {
                '3PC': 'No protection against malicious behavior',
                'PBFT': 'Tolerates up to f Byzantine nodes out of 3f+1',
                'winner': 'PBFT (better security)'
            },
            'use_cases': {
                '3PC': 'Traditional distributed systems',
                'PBFT': 'Blockchain, high-security systems',
                'winner': 'Context dependent'
            }
        }

# Modern hybrid approach combining concepts
class HybridConsensusProtocol:
    """Hybrid protocol combining 3PC concepts with modern improvements"""
    
    def __init__(self):
        self.view_number = 0
        self.sequence_number = 0
        self.participants = []
        
    async def execute_hybrid_consensus(self, proposal: 'Proposal') -> 'ConsensusResult':
        """Execute consensus using hybrid approach"""
        
        # Use Raft-style leader election
        leader = await self.elect_leader()
        
        if leader == self:
            # Use 3PC-style phases but with Raft optimizations
            return await self.execute_as_leader(proposal)
        else:
            # Forward to leader
            return await leader.execute_consensus(proposal)
    
    async def execute_as_leader(self, proposal: 'Proposal') -> 'ConsensusResult':
        """Execute consensus as leader with 3PC-inspired phases"""
        
        proposal_id = str(uuid.uuid4())
        
        # Phase 1: Prepare (with Raft-style heartbeats)
        prepare_result = await self.prepare_with_heartbeat(proposal, proposal_id)
        if not prepare_result.majority_prepared():
            return ConsensusResult(False, "Prepare phase failed")
        
        # Phase 2: Pre-commit (with early termination optimization)
        precommit_result = await self.precommit_with_optimization(proposal, proposal_id)
        if not precommit_result.majority_precommitted():
            return ConsensusResult(False, "Pre-commit phase failed")
        
        # Phase 3: Commit (with async notification)
        commit_result = await self.commit_with_async_notification(proposal, proposal_id)
        return ConsensusResult(commit_result.success, commit_result.message)
    
    async def prepare_with_heartbeat(self, proposal: 'Proposal', proposal_id: str) -> 'PrepareResult':
        """Enhanced prepare phase with heartbeat mechanism"""
        
        prepare_tasks = []
        
        for participant in self.participants:
            # Send prepare with current view number (Raft-style)
            prepare_msg = PrepareMessage(
                proposal=proposal,
                proposal_id=proposal_id,
                view_number=self.view_number,
                leader_heartbeat=time.time()
            )
            
            task = asyncio.create_task(participant.handle_prepare_with_heartbeat(prepare_msg))
            prepare_tasks.append((participant.id, task))
        
        # Collect responses with timeout
        responses = {}
        for participant_id, task in prepare_tasks:
            try:
                response = await asyncio.wait_for(task, timeout=2.0)
                responses[participant_id] = response
            except asyncio.TimeoutError:
                responses[participant_id] = PrepareResponse(False, "Timeout")
        
        return PrepareResult(proposal_id, responses)
```

---

## Best Practices और When to Use 3PC

### Modern Usage Guidelines

```python
class ThreePhaseCommitUsageGuidelines:
    """Guidelines for when and how to use 3PC in modern systems"""
    
    def when_to_use_3pc(self):
        """Scenarios where 3PC might be appropriate"""
        
        return {
            'good_scenarios': {
                'academic_research': 'Understanding distributed consensus concepts',
                'theoretical_analysis': 'Analyzing non-blocking properties',
                'specialized_systems': 'Systems with specific non-blocking requirements',
                'hybrid_protocols': 'As inspiration for custom consensus protocols'
            },
            'bad_scenarios': {
                'general_production': 'Most production systems should use alternatives',
                'high_performance': 'Performance-critical applications',
                'cloud_environments': 'Cloud-native applications',
                'microservices': 'Modern microservice architectures'
            }
        }
    
    def alternative_recommendations(self):
        """Recommended alternatives for different use cases"""
        
        return {
            'distributed_databases': {
                'recommendation': 'Raft consensus (etcd, Consul)',
                'reason': 'Proven, efficient, handles network partitions well'
            },
            'microservices_transactions': {
                'recommendation': 'Saga pattern with compensation',
                'reason': 'Better scalability, eventual consistency acceptable'
            },
            'blockchain_consensus': {
                'recommendation': 'Tendermint, HotStuff, or custom protocols',
                'reason': 'Designed for blockchain requirements'
            },
            'financial_transactions': {
                'recommendation': 'Carefully designed 2PC with timeouts',
                'reason': 'Strong consistency more important than non-blocking'
            },
            'event_processing': {
                'recommendation': 'Event sourcing with CQRS',
                'reason': 'Natural fit for event-driven architectures'
            }
        }
    
    def implementation_best_practices(self):
        """Best practices if implementing 3PC"""
        
        return {
            'network_assumptions': 'Don\'t assume synchronous network behavior',
            'timeout_management': 'Implement adaptive timeout mechanisms',
            'failure_detection': 'Use sophisticated failure detection',
            'state_management': 'Persistent state logging for recovery',
            'testing': 'Extensive network failure and partition testing',
            'monitoring': 'Comprehensive monitoring and alerting',
            'documentation': 'Clear operational procedures for recovery'
        }

class ModernConsensusSelection:
    """Guide for selecting appropriate consensus algorithm"""
    
    def __init__(self):
        self.selection_criteria = ConsensusSelectionCriteria()
    
    def select_consensus_algorithm(self, requirements: 'SystemRequirements') -> 'ConsensusRecommendation':
        """Select appropriate consensus algorithm based on requirements"""
        
        if requirements.byzantine_fault_tolerance:
            if requirements.performance_critical:
                return ConsensusRecommendation('HotStuff', 'High-performance BFT consensus')
            else:
                return ConsensusRecommendation('PBFT', 'Classical Byzantine fault tolerance')
        
        elif requirements.strong_consistency:
            if requirements.leader_based_acceptable:
                return ConsensusRecommendation('Raft', 'Industry standard for strong consistency')
            elif requirements.non_blocking_required:
                return ConsensusRecommendation('Modified 3PC', 'Custom 3PC with modern improvements')
            else:
                return ConsensusRecommendation('Paxos', 'Classical consensus without leader')
        
        elif requirements.eventual_consistency_acceptable:
            if requirements.high_scalability:
                return ConsensusRecommendation('Saga Pattern', 'Scalable eventual consistency')
            else:
                return ConsensusRecommendation('Event Sourcing', 'Event-driven consistency')
        
        else:
            return ConsensusRecommendation('Raft', 'Safe default choice')
    
    def evaluate_3pc_suitability(self, system_context: 'SystemContext') -> 'SuitabilityScore':
        """Evaluate if 3PC is suitable for given system context"""
        
        score = 0
        reasons = []
        
        # Positive factors
        if system_context.non_blocking_critical:
            score += 30
            reasons.append("Non-blocking property is critical requirement")
        
        if system_context.academic_research:
            score += 20
            reasons.append("Academic research context")
        
        if system_context.network_synchronous:
            score += 15
            reasons.append("Synchronous network assumptions hold")
        
        # Negative factors
        if system_context.performance_critical:
            score -= 25
            reasons.append("Performance overhead of 3 phases")
        
        if system_context.cloud_environment:
            score -= 20
            reasons.append("Cloud networks are asynchronous and unreliable")
        
        if system_context.production_system:
            score -= 30
            reasons.append("Production systems need proven alternatives")
        
        if system_context.large_scale:
            score -= 15
            reasons.append("3PC doesn't scale well to many participants")
        
        suitability = 'HIGH' if score >= 50 else 'MEDIUM' if score >= 20 else 'LOW'
        
        return SuitabilityScore(score, suitability, reasons)
```

---

## Conclusion

Three-Phase Commit Protocol एक theoretically important distributed systems algorithm है जो Two-Phase Commit की **blocking limitation** को solve करता है। हमने इस episode में comprehensive analysis किया:

### Key Takeaways:

#### 1. **Theoretical Advantages**:
- **Non-blocking property**: Coordinator failure के बाद भी participants recovery कर सकते हैं
- **Better fault tolerance**: Network partitions को handle कर सकता है
- **Clear decision points**: Pre-commit phase से decision visibility मिलती है

#### 2. **Practical Limitations**:
- **Performance overhead**: 50% more messages और latency compared to 2PC
- **Network assumptions**: Synchronous network की assumption realistic नहीं है
- **Implementation complexity**: Complex state management और recovery logic

#### 3. **Modern Reality**:
- **Rarely used in production**: Most systems use Raft, Paxos, या Saga patterns
- **Better alternatives available**: Modern consensus algorithms more practical हैं
- **Academic value**: Concept समझना important है future protocols के लिए

#### 4. **2025 Applications**:
- **Blockchain consensus**: Modified 3PC concepts blockchain में use होते हैं
- **Microservices orchestration**: 3PC-inspired patterns microservices में
- **Research and education**: Protocol design के लिए important reference

### When NOT to Use 3PC (Almost Always):
- **Production systems**: Use Raft या other proven alternatives
- **Performance-critical applications**: Too much overhead
- **Cloud environments**: Network assumptions don't hold
- **Large-scale systems**: Doesn't scale well

### When 3PC Concepts Are Useful:
- **Protocol design inspiration**: For building custom consensus protocols
- **Academic research**: Understanding non-blocking properties
- **Blockchain systems**: Modified forms for consensus
- **Educational purposes**: Learning distributed systems fundamentals

### Modern Alternatives to Consider:
1. **Raft Consensus**: For distributed databases and coordination
2. **Saga Pattern**: For microservices transactions
3. **Event Sourcing**: For event-driven architectures
4. **PBFT/HotStuff**: For Byzantine fault tolerance
5. **Tendermint**: For blockchain applications

3PC एक important **theoretical milestone** है distributed systems के development में, लेकिन practical applications के लिए modern alternatives को prefer करना चाहिए। इसकी **non-blocking property** की insight आज भी modern protocols को influence करती है।

---

## References और Further Reading

1. **Academic Papers**:
   - Skeen & Stonebraker: "A Formal Model of Crash Recovery in a Distributed System"
   - Gray: "Notes on Database Operating Systems"
   - Fischer, Lynch & Paterson: "Impossibility of Distributed Consensus"

2. **Modern Consensus Protocols**:
   - Raft: "In Search of an Understandable Consensus Algorithm"
   - PBFT: "Practical Byzantine Fault Tolerance"
   - Tendermint: "The latest gossip on BFT consensus"

3. **Production Systems**:
   - etcd: Raft-based distributed key-value store
   - Consul: Service mesh with Raft consensus
   - MongoDB: Replica set consensus mechanisms

4. **Alternative Patterns**:
   - Microservices Patterns: Saga, Event Sourcing, CQRS
   - Cloud-Native Architectures: Eventually consistent systems
   - Blockchain Consensus: Modern BFT protocols

---

*Next Episodes: Distributed Database Patterns और Modern Consensus Algorithms*