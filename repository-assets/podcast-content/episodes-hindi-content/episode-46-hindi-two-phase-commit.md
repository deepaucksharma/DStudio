# Episode 46: Two-Phase Commit Protocol - "दो कदम में Commitment"

## Episode Metadata
- **Title**: Two-Phase Commit Protocol - "दो कदम में Commitment"
- **Episode**: 46
- **Series**: Distributed Systems Hindi Podcast
- **Duration**: 2+ hours comprehensive coverage
- **Target Audience**: Distributed Systems Engineers, Architects
- **Complexity Level**: Intermediate to Advanced
- **Prerequisites**: Basic understanding of databases, transactions, network protocols

---

## Mumbai की कहानी: Wedding Planning में Coordination

### Scene 1: The Big Fat Mumbai Wedding

मुंबई की रौनक से भरी इस कहानी में, **Rajesh** और **Priya** की शादी का प्लानिंग चल रहा है। यह कोई आम शादी नहीं है - यह एक **Big Fat Mumbai Wedding** है जिसमें 1000+ guests हैं और 15+ vendors coordinate करने हैं।

**Main Characters:**
- **Wedding Planner (Coordinator)**: सारी planning का head
- **Caterer**: खाने का जिम्मा
- **Decorator**: decoration और setup
- **DJ/Sound System**: music और entertainment
- **Photographer**: memories capture करने वाला
- **Transport Service**: guests के लिए transportation
- **Hotel Manager**: venue booking
- **Florist**: flowers और mandap decoration

### Scene 2: The Coordination Challenge

Wedding planner को एक big challenge face करना पड़ रहा है। सभी vendors को **same date (December 15, 2024)** पर available होना है। अगर कोई भी vendor available नहीं है, तो **entire wedding plan fail** हो जाएगा।

**Wedding Planner का Plan:**
```
Phase 1 (Preparation/Voting):
- सभी vendors को date confirm करने के लिए call करना
- Each vendor से "YES/NO" का response लेना
- अगर कोई भी vendor "NO" बोलता है, तो alternative date find करना

Phase 2 (Commit):
- अगर सभी vendors ने "YES" कहा है, तो final booking confirm करना
- सभी vendors को "CONFIRMED" message send करना
- Payment advance देना और contracts sign करना
```

### Scene 3: Real Coordination Scenarios

#### Scenario 1: Perfect Coordination
```
Wedding Planner → All Vendors: "15 Dec available हो?"
Caterer → Wedding Planner: "YES, available"
Decorator → Wedding Planner: "YES, available"
DJ → Wedding Planner: "YES, available"
...
All vendors respond: "YES"

Wedding Planner → All Vendors: "CONFIRMED - 15 Dec final booking"
All vendors: Bookings confirmed, advance received
```

#### Scenario 2: Coordination Failure
```
Wedding Planner → All Vendors: "15 Dec available हो?"
Caterer → Wedding Planner: "YES, available"
Decorator → Wedding Planner: "YES, available"  
DJ → Wedding Planner: "NO, already booked"
...

Wedding Planner → All Vendors: "ABORT - 15 Dec not possible"
All vendors: Release the holds, look for alternative dates
```

### Scene 4: Network Problems में Coordination

मुंबई में monsoon season आ गया और network connectivity issues हो रहे हैं। Wedding planner का phone कभी-कभी network नहीं मिल रहा।

**Problem Scenarios:**
```
Wedding Planner → Caterer: "15 Dec available?" 
[Network timeout - no response received]

Wedding Planner decision:
- Wait for response (risk missing other vendors)
- Assume NO and abort (conservative approach)
- Retry communication (potential duplicate messages)
```

यहाँ हमें **timeout mechanisms**, **retry policies**, और **failure detection** की जरूरत है - exactly जैसे Two-Phase Commit Protocol में होता है।

---

## Theory Deep Dive: Two-Phase Commit Protocol

### Protocol Overview

Two-Phase Commit (2PC) एक **distributed atomic commitment protocol** है जो ensure करता है कि distributed transaction या तो सभी participating nodes पर **commit** हो या फिर सभी पर **abort** हो।

### Key Components

#### 1. Transaction Coordinator
```
Wedding Planner के similar, coordinator responsible है:
- Transaction initiate करने के लिए
- सभी participants के साथ communicate करने के लिए  
- Final decision (commit/abort) लेने के लिए
- Recovery procedures handle करने के लिए
```

#### 2. Transaction Participants
```
Vendors के similar, participants responsible हैं:
- अपने local transaction prepare करने के लिए
- Coordinator को vote देने के लिए (YES/NO)
- Final outcome implement करने के लिए
- Recovery में participate करने के लिए
```

### Phase 1: Prepare/Voting Phase

#### Coordinator Actions:
```
1. Transaction start करता है
2. सभी participants को PREPARE message send करता है
3. सभी participants से response का wait करता है
4. Timeout mechanism maintain करता है
```

#### Participant Actions:
```
1. PREPARE message receive करता है
2. Local transaction prepare करता है
3. Resources lock करता है
4. Vote send करता है: YES (ready) या NO (can't commit)
5. अगर YES vote किया है तो commit/abort decision का wait करता है
```

#### Code Example - Phase 1:
```python
class TwoPhaseCommitCoordinator:
    def __init__(self):
        self.participants = []
        self.transaction_id = None
        self.votes = {}
        
    def phase1_prepare(self, transaction_id):
        """Phase 1: Send PREPARE to all participants"""
        self.transaction_id = transaction_id
        self.votes = {}
        
        prepare_message = {
            'type': 'PREPARE',
            'transaction_id': transaction_id,
            'timestamp': time.time()
        }
        
        # Send PREPARE to all participants
        for participant in self.participants:
            try:
                response = participant.send_prepare(prepare_message)
                self.votes[participant.id] = response
                
            except NetworkTimeout:
                # Network timeout - assume NO vote
                self.votes[participant.id] = 'NO'
                
            except ParticipantFailure:
                # Participant failed - assume NO vote  
                self.votes[participant.id] = 'NO'
        
        return self.evaluate_votes()
    
    def evaluate_votes(self):
        """Evaluate all votes - need unanimous YES"""
        for participant_id, vote in self.votes.items():
            if vote != 'YES':
                return 'ABORT'
        return 'COMMIT'

class TwoPhaseCommitParticipant:
    def __init__(self, participant_id):
        self.participant_id = participant_id
        self.prepared_transactions = {}
        
    def send_prepare(self, message):
        """Handle PREPARE message from coordinator"""
        transaction_id = message['transaction_id']
        
        try:
            # Try to prepare local transaction
            success = self.prepare_local_transaction(transaction_id)
            
            if success:
                # Lock resources and prepare for commit
                self.prepared_transactions[transaction_id] = {
                    'status': 'PREPARED',
                    'locked_resources': self.get_locked_resources(),
                    'prepared_time': time.time()
                }
                return 'YES'
            else:
                return 'NO'
                
        except Exception as e:
            logger.error(f"Prepare failed: {e}")
            return 'NO'
```

### Phase 2: Commit/Abort Phase

#### Coordinator Actions:
```
1. Phase 1 के votes evaluate करता है
2. Decision लेता है (COMMIT अगर सभी YES, otherwise ABORT)
3. सभी participants को decision send करता है
4. Acknowledgments का wait करता है
```

#### Participant Actions:
```
1. Coordinator से decision receive करता है
2. COMMIT message पर: local transaction commit करता है, locks release करता है
3. ABORT message पर: local transaction rollback करता है, locks release करता है
4. Coordinator को acknowledgment send करता है
```

#### Code Example - Phase 2:
```python
class TwoPhaseCommitCoordinator:
    def phase2_commit_abort(self, decision):
        """Phase 2: Send final decision to all participants"""
        decision_message = {
            'type': decision,  # 'COMMIT' or 'ABORT'
            'transaction_id': self.transaction_id,
            'timestamp': time.time()
        }
        
        acknowledgments = {}
        
        # Send decision to all participants
        for participant in self.participants:
            try:
                ack = participant.send_decision(decision_message)
                acknowledgments[participant.id] = ack
                
            except NetworkTimeout:
                # Network timeout during commit phase
                # This is problematic - coordinator doesn't know 
                # if participant committed or not
                logger.error(f"Timeout with {participant.id} during commit")
                acknowledgments[participant.id] = 'TIMEOUT'
                
        return acknowledgments
    
    def complete_transaction(self):
        """Complete the 2PC protocol"""
        # Phase 1: Prepare
        phase1_result = self.phase1_prepare(self.transaction_id)
        
        if phase1_result == 'COMMIT':
            # Phase 2: Commit
            logger.info("All participants voted YES - committing")
            acks = self.phase2_commit_abort('COMMIT')
            
        else:
            # Phase 2: Abort
            logger.info("Some participants voted NO - aborting")
            acks = self.phase2_commit_abort('ABORT')
            
        return phase1_result, acks

class TwoPhaseCommitParticipant:
    def send_decision(self, message):
        """Handle COMMIT/ABORT decision from coordinator"""
        transaction_id = message['transaction_id']
        decision = message['type']
        
        if decision == 'COMMIT':
            # Commit the prepared transaction
            if transaction_id in self.prepared_transactions:
                try:
                    self.commit_local_transaction(transaction_id)
                    self.release_locks(transaction_id)
                    del self.prepared_transactions[transaction_id]
                    return 'COMMITTED'
                    
                except Exception as e:
                    # This is very bad - participant can't commit
                    # after voting YES in phase 1
                    logger.critical(f"Failed to commit after YES vote: {e}")
                    return 'COMMIT_FAILED'
            else:
                return 'TRANSACTION_NOT_FOUND'
                
        elif decision == 'ABORT':
            # Abort the prepared transaction
            if transaction_id in self.prepared_transactions:
                self.rollback_local_transaction(transaction_id)
                self.release_locks(transaction_id)
                del self.prepared_transactions[transaction_id]
                return 'ABORTED'
            else:
                return 'TRANSACTION_NOT_FOUND'
```

### Protocol State Diagram

```
Coordinator States:
INIT → PREPARING → ABORTING/COMMITTING → COMPLETED

Participant States:
INIT → PREPARED → COMMITTED/ABORTED
```

### Critical Properties

#### 1. Atomicity
```python
# Either all participants commit or all abort
def verify_atomicity(transaction_results):
    committed_count = sum(1 for result in transaction_results if result == 'COMMITTED')
    total_participants = len(transaction_results)
    
    # Atomicity violation check
    if 0 < committed_count < total_participants:
        raise AtomicityViolationError("Mixed commit/abort state detected!")
        
    return committed_count == total_participants  # All committed
```

#### 2. Consistency 
```python
# Database remains in consistent state
def verify_consistency(database_state_before, database_state_after):
    # Check invariants are maintained
    return check_database_invariants(database_state_after)
```

#### 3. Isolation
```python
# Concurrent transactions don't interfere
def ensure_isolation(transaction1, transaction2):
    locked_resources_t1 = transaction1.get_locked_resources()
    locked_resources_t2 = transaction2.get_locked_resources()
    
    # Check for resource conflicts
    conflicts = locked_resources_t1.intersection(locked_resources_t2)
    if conflicts:
        handle_resource_conflict(transaction1, transaction2, conflicts)
```

#### 4. Durability
```python
# Committed changes survive failures
def ensure_durability(transaction_id):
    # Write-ahead logging
    log_entry = {
        'transaction_id': transaction_id,
        'status': 'COMMITTED',
        'timestamp': time.time(),
        'changes': get_transaction_changes(transaction_id)
    }
    
    # Force write to persistent storage
    transaction_log.force_write(log_entry)
```

---

## Production Implementation Examples

### 1. Oracle RAC (Real Application Clusters)

Oracle RAC में 2PC का extensive use होता है multiple instances के बीच distributed transactions के लिए।

#### Oracle RAC 2PC Implementation:
```sql
-- Oracle में distributed transaction example
-- Node 1 पर transaction start
BEGIN;
  -- Local operations on Node 1
  UPDATE employees SET salary = 50000 WHERE emp_id = 1001;
  
  -- Remote operation on Node 2 (via database link)
  UPDATE employees@node2 SET department = 'Engineering' WHERE emp_id = 1001;
  
  -- Oracle automatically uses 2PC for commit
COMMIT;
```

#### Oracle Recovery Mechanisms:
```python
class OracleRACRecovery:
    def __init__(self):
        self.pending_transactions = {}
        self.recovery_log = TransactionLog()
        
    def recover_pending_transactions(self):
        """Recover transactions after node failure"""
        pending = self.recovery_log.get_pending_transactions()
        
        for transaction_id in pending:
            transaction_state = self.recovery_log.get_transaction_state(transaction_id)
            
            if transaction_state == 'PREPARING':
                # Coordinator failed during phase 1
                # Safe to abort
                self.abort_transaction(transaction_id)
                
            elif transaction_state == 'COMMITTING':
                # Coordinator failed during phase 2 after decision
                # Must complete the commit
                self.complete_commit(transaction_id)
                
            elif transaction_state == 'ABORTING':
                # Coordinator failed during abort
                # Complete the abort
                self.complete_abort(transaction_id)
```

### 2. PostgreSQL XA Transactions

PostgreSQL में XA (eXtended Architecture) standard implement करता है 2PC के लिए।

#### PostgreSQL XA Example:
```python
import psycopg2
from psycopg2 import sql

class PostgreSQLXAManager:
    def __init__(self):
        self.connections = {}
        self.prepared_transactions = {}
        
    def distributed_transaction_example(self):
        """PostgreSQL distributed transaction using XA"""
        
        # Connections to different databases
        conn1 = psycopg2.connect("dbname=orders host=db1")
        conn2 = psycopg2.connect("dbname=inventory host=db2")
        
        xid1 = "order_tx_001_db1"
        xid2 = "order_tx_001_db2"
        
        try:
            # Phase 1: Prepare on both databases
            with conn1.cursor() as cur1:
                # Do order operations
                cur1.execute("INSERT INTO orders (id, amount) VALUES (%s, %s)", (1001, 500))
                # Prepare the transaction
                cur1.execute("PREPARE TRANSACTION %s", (xid1,))
                
            with conn2.cursor() as cur2:
                # Do inventory operations  
                cur2.execute("UPDATE inventory SET quantity = quantity - 1 WHERE product_id = %s", (2001,))
                # Prepare the transaction
                cur2.execute("PREPARE TRANSACTION %s", (xid2,))
            
            # Phase 2: Commit both transactions
            with conn1.cursor() as cur1:
                cur1.execute("COMMIT PREPARED %s", (xid1,))
                
            with conn2.cursor() as cur2:
                cur2.execute("COMMIT PREPARED %s", (xid2,))
                
            print("Distributed transaction completed successfully")
            
        except Exception as e:
            # Phase 2: Abort both transactions
            try:
                with conn1.cursor() as cur1:
                    cur1.execute("ROLLBACK PREPARED %s", (xid1,))
            except:
                pass
                
            try:
                with conn2.cursor() as cur2:
                    cur2.execute("ROLLBACK PREPARED %s", (xid2,))
            except:
                pass
                
            print(f"Distributed transaction aborted: {e}")
            
        finally:
            conn1.close()
            conn2.close()
```

#### PostgreSQL Recovery और Monitoring:
```python
class PostgreSQLRecoveryManager:
    def __init__(self, connection):
        self.conn = connection
        
    def check_prepared_transactions(self):
        """Check for prepared transactions that need recovery"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT gid, prepared, owner, database 
                FROM pg_prepared_xacts 
                ORDER BY prepared
            """)
            
            prepared_txns = cur.fetchall()
            
            for gid, prepared_time, owner, database in prepared_txns:
                age = datetime.now() - prepared_time
                
                if age > timedelta(minutes=30):  # Old prepared transaction
                    logger.warning(f"Old prepared transaction: {gid}, age: {age}")
                    # Decision needed: commit या abort
                    
    def recover_transaction(self, gid, action):
        """Recover a specific prepared transaction"""
        with self.conn.cursor() as cur:
            if action == 'COMMIT':
                cur.execute("COMMIT PREPARED %s", (gid,))
            elif action == 'ABORT':
                cur.execute("ROLLBACK PREPARED %s", (gid,))
            else:
                raise ValueError("Action must be COMMIT or ABORT")
```

### 3. MySQL XA Implementation

MySQL भी XA transactions support करता है, लेकिन कुछ limitations के साथ।

#### MySQL XA Example:
```python
import mysql.connector
from mysql.connector import Error

class MySQLXAManager:
    def __init__(self):
        self.connections = {}
        
    def execute_distributed_transaction(self):
        """MySQL XA distributed transaction example"""
        
        # Connections to different MySQL instances
        conn1 = mysql.connector.connect(
            host='mysql1', database='ecommerce', user='app', password='password'
        )
        conn2 = mysql.connector.connect(
            host='mysql2', database='analytics', user='app', password='password'
        )
        
        # XA transaction IDs
        xid1 = "'tx001','branch1',''"
        xid2 = "'tx001','branch2',''"
        
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        try:
            # Start XA transactions
            cursor1.execute(f"XA START {xid1}")
            cursor2.execute(f"XA START {xid2}")
            
            # Execute business logic
            cursor1.execute("INSERT INTO orders (customer_id, amount) VALUES (101, 299.99)")
            cursor2.execute("INSERT INTO sales_stats (date, amount) VALUES (NOW(), 299.99)")
            
            # End XA transactions
            cursor1.execute(f"XA END {xid1}")
            cursor2.execute(f"XA END {xid2}")
            
            # Prepare phase (Phase 1)
            cursor1.execute(f"XA PREPARE {xid1}")
            cursor2.execute(f"XA PREPARE {xid2}")
            
            # Commit phase (Phase 2)
            cursor1.execute(f"XA COMMIT {xid1}")
            cursor2.execute(f"XA COMMIT {xid2}")
            
            logger.info("MySQL XA transaction completed successfully")
            
        except Error as e:
            # Rollback on error
            try:
                cursor1.execute(f"XA ROLLBACK {xid1}")
                cursor2.execute(f"XA ROLLBACK {xid2}")
            except:
                pass
                
            logger.error(f"MySQL XA transaction failed: {e}")
            
        finally:
            cursor1.close()
            cursor2.close()
            conn1.close()
            conn2.close()
    
    def list_xa_transactions(self, connection):
        """List current XA transactions"""
        cursor = connection.cursor()
        cursor.execute("XA RECOVER")
        
        transactions = cursor.fetchall()
        for tx in transactions:
            logger.info(f"Pending XA transaction: {tx}")
            
        cursor.close()
        return transactions
```

### 4. Banking System Implementation

Real-world banking system में 2PC का use होता है inter-bank transfers के लिए।

#### Banking Transfer Service:
```python
class BankingTransferService:
    def __init__(self):
        self.bank_connections = {}
        self.transfer_log = TransferLog()
        
    def inter_bank_transfer(self, from_account, to_account, amount, transfer_id):
        """Execute inter-bank transfer using 2PC"""
        
        from_bank = self.get_bank_connection(from_account.bank_code)
        to_bank = self.get_bank_connection(to_account.bank_code)
        
        # Create transfer record
        transfer = BankTransfer(
            transfer_id=transfer_id,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            status='INITIATING'
        )
        
        self.transfer_log.log_transfer(transfer)
        
        try:
            # Phase 1: Prepare both banks
            from_bank_response = from_bank.prepare_debit(from_account, amount, transfer_id)
            to_bank_response = to_bank.prepare_credit(to_account, amount, transfer_id)
            
            if from_bank_response.status == 'YES' and to_bank_response.status == 'YES':
                # Phase 2: Commit both banks
                transfer.status = 'COMMITTING'
                self.transfer_log.update_transfer(transfer)
                
                from_bank.commit_debit(transfer_id)
                to_bank.commit_credit(transfer_id)
                
                transfer.status = 'COMPLETED'
                self.transfer_log.update_transfer(transfer)
                
                return TransferResult(success=True, transfer_id=transfer_id)
                
            else:
                # Phase 2: Abort both banks
                transfer.status = 'ABORTING'
                self.transfer_log.update_transfer(transfer)
                
                from_bank.abort_debit(transfer_id)
                to_bank.abort_credit(transfer_id)
                
                transfer.status = 'ABORTED'
                self.transfer_log.update_transfer(transfer)
                
                return TransferResult(success=False, reason="Insufficient funds or account issues")
                
        except BankCommunicationError as e:
            # Network/communication error during transfer
            logger.error(f"Communication error during transfer {transfer_id}: {e}")
            
            # Initiate recovery procedure
            self.initiate_recovery(transfer_id)
            
            return TransferResult(success=False, reason="Communication error - transfer under review")
            
    def initiate_recovery(self, transfer_id):
        """Initiate recovery procedure for failed transfer"""
        transfer = self.transfer_log.get_transfer(transfer_id)
        
        if transfer.status == 'COMMITTING':
            # Coordinator failed during commit phase
            # Must complete the commit
            self.complete_commit_recovery(transfer)
            
        elif transfer.status == 'ABORTING':
            # Coordinator failed during abort phase
            # Must complete the abort
            self.complete_abort_recovery(transfer)
            
        else:
            # Safe to abort
            self.abort_transfer(transfer)

class BankConnection:
    def __init__(self, bank_code, endpoint):
        self.bank_code = bank_code
        self.endpoint = endpoint
        self.pending_operations = {}
        
    def prepare_debit(self, account, amount, transfer_id):
        """Prepare to debit amount from account"""
        try:
            # Check account balance
            current_balance = self.get_account_balance(account)
            
            if current_balance >= amount:
                # Lock the funds
                self.lock_funds(account, amount, transfer_id)
                
                # Store pending operation
                self.pending_operations[transfer_id] = {
                    'type': 'DEBIT',
                    'account': account,
                    'amount': amount,
                    'locked_time': datetime.now()
                }
                
                return PrepareResponse(status='YES')
            else:
                return PrepareResponse(status='NO', reason='Insufficient funds')
                
        except Exception as e:
            logger.error(f"Prepare debit failed: {e}")
            return PrepareResponse(status='NO', reason=str(e))
    
    def commit_debit(self, transfer_id):
        """Commit the debit operation"""
        if transfer_id in self.pending_operations:
            operation = self.pending_operations[transfer_id]
            
            # Execute the debit
            self.execute_debit(operation['account'], operation['amount'])
            
            # Release lock and cleanup
            self.release_lock(operation['account'], transfer_id)
            del self.pending_operations[transfer_id]
            
            return CommitResponse(status='COMMITTED')
        else:
            return CommitResponse(status='TRANSACTION_NOT_FOUND')
    
    def abort_debit(self, transfer_id):
        """Abort the debit operation"""
        if transfer_id in self.pending_operations:
            operation = self.pending_operations[transfer_id]
            
            # Release lock without debiting
            self.release_lock(operation['account'], transfer_id)
            del self.pending_operations[transfer_id]
            
            return AbortResponse(status='ABORTED')
        else:
            return AbortResponse(status='TRANSACTION_NOT_FOUND')
```

---

## 2025 Real-World Examples

### 1. UPI Transaction Coordination

UPI (Unified Payments Interface) में भारत में millions of transactions daily होते हैं, और इसमें 2PC जैसे protocols का use होता है।

#### UPI Transaction Flow with 2PC:
```python
class UPITransactionCoordinator:
    def __init__(self):
        self.npci_gateway = NPCIGateway()
        self.bank_connections = {}
        self.transaction_log = UPITransactionLog()
        
    def process_upi_transfer(self, vpa_from, vpa_to, amount, upi_ref_id):
        """Process UPI transfer using 2PC-like protocol"""
        
        # Parse VPAs to get bank details
        payer_bank = self.resolve_bank_from_vpa(vpa_from)
        payee_bank = self.resolve_bank_from_vpa(vpa_to)
        
        transaction = UPITransaction(
            upi_ref_id=upi_ref_id,
            payer_vpa=vpa_from,
            payee_vpa=vpa_to,
            amount=amount,
            payer_bank=payer_bank,
            payee_bank=payee_bank,
            status='INITIATED'
        )
        
        self.transaction_log.log_transaction(transaction)
        
        try:
            # Phase 1: Check with both banks
            payer_response = payer_bank.validate_and_hold(vpa_from, amount, upi_ref_id)
            payee_response = payee_bank.validate_account(vpa_to, upi_ref_id)
            
            if payer_response.status == 'SUCCESS' and payee_response.status == 'SUCCESS':
                # Phase 2: Execute transfer
                transaction.status = 'PROCESSING'
                self.transaction_log.update_transaction(transaction)
                
                # Debit from payer
                debit_result = payer_bank.execute_debit(vpa_from, amount, upi_ref_id)
                
                if debit_result.status == 'SUCCESS':
                    # Credit to payee
                    credit_result = payee_bank.execute_credit(vpa_to, amount, upi_ref_id)
                    
                    if credit_result.status == 'SUCCESS':
                        transaction.status = 'SUCCESS'
                        self.transaction_log.update_transaction(transaction)
                        
                        # Send success notification
                        self.send_notification(transaction, 'SUCCESS')
                        return UPIResponse(status='SUCCESS', txn_id=upi_ref_id)
                    else:
                        # Credit failed - reverse debit
                        payer_bank.reverse_debit(vpa_from, amount, upi_ref_id)
                        transaction.status = 'FAILED'
                        self.send_notification(transaction, 'FAILED')
                        return UPIResponse(status='FAILED', reason='Beneficiary account issue')
                else:
                    transaction.status = 'FAILED'
                    self.send_notification(transaction, 'FAILED')
                    return UPIResponse(status='FAILED', reason='Insufficient balance')
            else:
                transaction.status = 'FAILED'
                return UPIResponse(status='FAILED', reason='Account validation failed')
                
        except CommunicationError as e:
            # Handle network issues
            transaction.status = 'PENDING'
            self.transaction_log.update_transaction(transaction)
            
            # Initiate reconciliation process
            self.initiate_reconciliation(upi_ref_id)
            
            return UPIResponse(status='PENDING', reason='Processing - please check status')

class NPCIBankConnection:
    def __init__(self, bank_code, bank_name):
        self.bank_code = bank_code
        self.bank_name = bank_name
        self.held_transactions = {}
        
    def validate_and_hold(self, vpa, amount, txn_id):
        """Validate account and hold amount (Phase 1)"""
        try:
            account = self.resolve_account_from_vpa(vpa)
            balance = self.get_account_balance(account)
            
            if balance >= amount:
                # Hold the amount
                self.held_transactions[txn_id] = {
                    'account': account,
                    'amount': amount,
                    'hold_time': datetime.now(),
                    'vpa': vpa
                }
                
                return BankResponse(status='SUCCESS')
            else:
                return BankResponse(status='FAILED', reason='Insufficient balance')
                
        except AccountNotFound:
            return BankResponse(status='FAILED', reason='Invalid VPA')
        except Exception as e:
            return BankResponse(status='FAILED', reason=str(e))
    
    def execute_debit(self, vpa, amount, txn_id):
        """Execute actual debit (Phase 2)"""
        if txn_id in self.held_transactions:
            held_txn = self.held_transactions[txn_id]
            
            try:
                # Execute debit
                self.debit_account(held_txn['account'], amount, txn_id)
                
                # Release hold
                del self.held_transactions[txn_id]
                
                return BankResponse(status='SUCCESS')
                
            except Exception as e:
                # Release hold on error
                del self.held_transactions[txn_id]
                return BankResponse(status='FAILED', reason=str(e))
        else:
            return BankResponse(status='FAILED', reason='Transaction not found')
```

### 2. Cross-Bank Transfer Systems

भारतीय banking ecosystem में RTGS, NEFT जैसे systems में distributed transaction coordination होता है।

#### RTGS Implementation:
```python
class RTGSTransferCoordinator:
    def __init__(self):
        self.rbi_settlement_system = RBISettlementSystem()
        self.participating_banks = {}
        self.settlement_log = SettlementLog()
        
    def process_rtgs_transfer(self, transfer_request):
        """Process RTGS transfer with settlement coordination"""
        
        originating_bank = self.participating_banks[transfer_request.originating_bank_code]
        beneficiary_bank = self.participating_banks[transfer_request.beneficiary_bank_code]
        
        settlement_txn = SettlementTransaction(
            rtgs_ref=transfer_request.rtgs_reference,
            originating_bank=transfer_request.originating_bank_code,
            beneficiary_bank=transfer_request.beneficiary_bank_code,
            amount=transfer_request.amount,
            status='INITIATED'
        )
        
        self.settlement_log.log_settlement(settlement_txn)
        
        try:
            # Phase 1: Check settlement account balances
            originating_balance = self.rbi_settlement_system.get_bank_balance(
                transfer_request.originating_bank_code
            )
            
            if originating_balance >= transfer_request.amount:
                # Reserve amount in settlement system
                reservation = self.rbi_settlement_system.reserve_amount(
                    transfer_request.originating_bank_code,
                    transfer_request.amount,
                    transfer_request.rtgs_reference
                )
                
                if reservation.status == 'SUCCESS':
                    # Phase 2: Execute settlement
                    settlement_txn.status = 'SETTLING'
                    self.settlement_log.update_settlement(settlement_txn)
                    
                    # Debit originating bank
                    debit_result = self.rbi_settlement_system.debit_bank_account(
                        transfer_request.originating_bank_code,
                        transfer_request.amount,
                        transfer_request.rtgs_reference
                    )
                    
                    if debit_result.status == 'SUCCESS':
                        # Credit beneficiary bank
                        credit_result = self.rbi_settlement_system.credit_bank_account(
                            transfer_request.beneficiary_bank_code,
                            transfer_request.amount,
                            transfer_request.rtgs_reference
                        )
                        
                        if credit_result.status == 'SUCCESS':
                            settlement_txn.status = 'SETTLED'
                            self.settlement_log.update_settlement(settlement_txn)
                            
                            # Notify both banks
                            self.notify_banks(transfer_request, 'SETTLED')
                            
                            return RTGSResponse(status='SUCCESS', rtgs_ref=transfer_request.rtgs_reference)
                        else:
                            # Reverse debit
                            self.rbi_settlement_system.reverse_debit(
                                transfer_request.originating_bank_code,
                                transfer_request.amount,
                                transfer_request.rtgs_reference
                            )
                            
                            settlement_txn.status = 'FAILED'
                            return RTGSResponse(status='FAILED', reason='Settlement credit failed')
                    else:
                        settlement_txn.status = 'FAILED'
                        return RTGSResponse(status='FAILED', reason='Settlement debit failed')
                else:
                    return RTGSResponse(status='FAILED', reason='Amount reservation failed')
            else:
                return RTGSResponse(status='FAILED', reason='Insufficient settlement balance')
                
        except SettlementSystemError as e:
            settlement_txn.status = 'ERROR'
            self.settlement_log.update_settlement(settlement_txn)
            
            # Initiate manual intervention
            self.escalate_for_manual_review(transfer_request, str(e))
            
            return RTGSResponse(status='PENDING', reason='Under review')

class RBISettlementSystem:
    def __init__(self):
        self.bank_accounts = {}  # Bank settlement accounts
        self.reserved_amounts = {}  # Reserved amounts per transaction
        
    def reserve_amount(self, bank_code, amount, reference):
        """Reserve amount for settlement"""
        current_balance = self.bank_accounts.get(bank_code, 0)
        current_reservations = sum(
            res['amount'] for res in self.reserved_amounts.values() 
            if res['bank_code'] == bank_code
        )
        
        available_balance = current_balance - current_reservations
        
        if available_balance >= amount:
            self.reserved_amounts[reference] = {
                'bank_code': bank_code,
                'amount': amount,
                'reserved_time': datetime.now()
            }
            
            return ReservationResponse(status='SUCCESS')
        else:
            return ReservationResponse(status='FAILED', reason='Insufficient available balance')
    
    def debit_bank_account(self, bank_code, amount, reference):
        """Execute debit from bank settlement account"""
        if reference in self.reserved_amounts:
            reservation = self.reserved_amounts[reference]
            
            if reservation['bank_code'] == bank_code and reservation['amount'] == amount:
                # Execute debit
                self.bank_accounts[bank_code] -= amount
                
                # Release reservation
                del self.reserved_amounts[reference]
                
                return SettlementResponse(status='SUCCESS')
            else:
                return SettlementResponse(status='FAILED', reason='Reservation mismatch')
        else:
            return SettlementResponse(status='FAILED', reason='No reservation found')
    
    def credit_bank_account(self, bank_code, amount, reference):
        """Execute credit to bank settlement account"""
        # Credit the beneficiary bank
        if bank_code not in self.bank_accounts:
            self.bank_accounts[bank_code] = 0
            
        self.bank_accounts[bank_code] += amount
        
        return SettlementResponse(status='SUCCESS')
```

---

## Failure Scenarios और Recovery Procedures

### Common Failure Scenarios

#### 1. Coordinator Failure
```python
class CoordinatorFailureRecovery:
    def __init__(self):
        self.recovery_log = RecoveryLog()
        self.participants = []
        
    def recover_from_coordinator_failure(self):
        """Recover transactions after coordinator failure"""
        
        # Read transaction log to find incomplete transactions
        incomplete_txns = self.recovery_log.get_incomplete_transactions()
        
        for txn in incomplete_txns:
            if txn.state == 'PREPARING':
                # Coordinator failed during Phase 1
                # Safe to abort - participants will timeout and abort
                logger.info(f"Aborting transaction {txn.id} (was in PREPARING state)")
                self.abort_transaction(txn.id)
                
            elif txn.state == 'COMMITTING':
                # Coordinator failed during Phase 2 after deciding to commit
                # Must complete the commit
                logger.info(f"Completing commit for transaction {txn.id}")
                self.complete_commit(txn.id)
                
            elif txn.state == 'ABORTING':
                # Coordinator failed during Phase 2 after deciding to abort
                # Must complete the abort
                logger.info(f"Completing abort for transaction {txn.id}")
                self.complete_abort(txn.id)
    
    def complete_commit(self, transaction_id):
        """Complete commit operation after coordinator recovery"""
        participants = self.get_transaction_participants(transaction_id)
        
        for participant in participants:
            try:
                result = participant.commit_transaction(transaction_id)
                if result.status != 'COMMITTED':
                    logger.error(f"Failed to commit on {participant.id}: {result}")
                    # This is bad - some participants may have committed
                    # Need manual intervention
                    self.escalate_for_manual_resolution(transaction_id, participant.id)
            except CommunicationError:
                # Participant unreachable - retry later
                self.schedule_retry(transaction_id, participant.id, 'COMMIT')
    
    def complete_abort(self, transaction_id):
        """Complete abort operation after coordinator recovery"""
        participants = self.get_transaction_participants(transaction_id)
        
        for participant in participants:
            try:
                result = participant.abort_transaction(transaction_id)
                logger.info(f"Aborted transaction {transaction_id} on {participant.id}")
            except CommunicationError:
                # Participant unreachable - retry later
                self.schedule_retry(transaction_id, participant.id, 'ABORT')
```

#### 2. Participant Failure During Phase 1
```python
class ParticipantPhase1FailureHandler:
    def handle_participant_timeout_phase1(self, transaction_id, failed_participant):
        """Handle participant failure/timeout during Phase 1"""
        
        logger.warning(f"Participant {failed_participant} timed out during Phase 1")
        
        # In Phase 1, timeout means NO vote
        # Safe to abort entire transaction
        self.abort_transaction(transaction_id)
        
        # Notify all other participants to abort
        for participant in self.get_other_participants(failed_participant):
            try:
                participant.abort_transaction(transaction_id)
            except CommunicationError:
                # Best effort - participant will eventually timeout and abort
                pass
```

#### 3. Participant Failure During Phase 2
```python
class ParticipantPhase2FailureHandler:
    def handle_participant_timeout_phase2(self, transaction_id, failed_participant, decision):
        """Handle participant failure/timeout during Phase 2"""
        
        logger.error(f"Participant {failed_participant} timed out during Phase 2")
        
        # This is problematic - we don't know if participant committed/aborted
        # Need recovery mechanism
        
        if decision == 'COMMIT':
            # We decided to commit - participant must eventually commit
            # Keep retrying until success
            self.retry_commit_indefinitely(transaction_id, failed_participant)
            
        elif decision == 'ABORT':
            # We decided to abort - participant must eventually abort
            self.retry_abort_indefinitely(transaction_id, failed_participant)
    
    def retry_commit_indefinitely(self, transaction_id, participant):
        """Keep retrying commit until success"""
        max_retries = float('inf')  # Retry indefinitely
        retry_delay = 1.0  # Start with 1 second
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                result = participant.commit_transaction(transaction_id)
                if result.status == 'COMMITTED':
                    logger.info(f"Successfully committed {transaction_id} on {participant.id}")
                    return
                elif result.status == 'TRANSACTION_NOT_FOUND':
                    # Participant may have already committed and cleaned up
                    logger.info(f"Transaction {transaction_id} not found on {participant.id} - assuming committed")
                    return
                    
            except CommunicationError:
                pass  # Continue retrying
                
            # Exponential backoff with jitter
            time.sleep(retry_delay + random.uniform(0, 1))
            retry_delay = min(retry_delay * 2, 60)  # Max 60 seconds
            retry_count += 1
```

#### 4. Network Partition Scenarios
```python
class NetworkPartitionHandler:
    def __init__(self):
        self.partition_detector = NetworkPartitionDetector()
        self.recovery_coordinator = RecoveryCoordinator()
        
    def handle_network_partition(self, partition_info):
        """Handle network partition during 2PC"""
        
        if partition_info.phase == 'PHASE_1':
            # Partition during Phase 1
            # Conservative approach: abort all transactions
            # that can't reach all participants
            
            for txn_id in partition_info.affected_transactions:
                if not self.can_reach_all_participants(txn_id):
                    logger.info(f"Aborting {txn_id} due to network partition in Phase 1")
                    self.abort_transaction(txn_id)
                    
        elif partition_info.phase == 'PHASE_2':
            # Partition during Phase 2 is more problematic
            # Some participants may be unreachable after decision made
            
            for txn_id in partition_info.affected_transactions:
                txn_state = self.get_transaction_state(txn_id)
                
                if txn_state.decision_made:
                    # Decision was made before partition
                    # Must ensure all reachable participants get the decision
                    # Unreachable participants will be handled after partition heals
                    
                    reachable_participants = self.get_reachable_participants(txn_id)
                    
                    for participant in reachable_participants:
                        if txn_state.decision == 'COMMIT':
                            participant.commit_transaction(txn_id)
                        else:
                            participant.abort_transaction(txn_id)
                    
                    # Store information for post-partition recovery
                    self.recovery_coordinator.store_partition_recovery_info(
                        txn_id, txn_state.decision, partition_info.unreachable_participants
                    )
                else:
                    # No decision made yet - must abort
                    self.abort_transaction(txn_id)
    
    def handle_partition_recovery(self, recovered_participants):
        """Handle recovery after network partition heals"""
        
        recovery_tasks = self.recovery_coordinator.get_pending_recovery_tasks()
        
        for task in recovery_tasks:
            if task.participant_id in recovered_participants:
                try:
                    if task.decision == 'COMMIT':
                        result = task.participant.commit_transaction(task.transaction_id)
                    else:
                        result = task.participant.abort_transaction(task.transaction_id)
                        
                    if result.status in ['COMMITTED', 'ABORTED', 'TRANSACTION_NOT_FOUND']:
                        # Successfully recovered
                        self.recovery_coordinator.mark_recovery_complete(task.task_id)
                        
                except CommunicationError:
                    # Still unreachable - keep trying
                    logger.warning(f"Participant {task.participant_id} still unreachable")
```

---

## Monitoring और Debugging

### 2PC Monitoring Dashboard

```python
class TwoPhaseCommitMonitor:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alerting_system = AlertingSystem()
        self.dashboard = MonitoringDashboard()
        
    def collect_2pc_metrics(self):
        """Collect 2PC performance and health metrics"""
        
        metrics = {
            # Transaction throughput
            'transactions_per_second': self.metrics_collector.get_tps(),
            'successful_transactions': self.metrics_collector.get_success_count(),
            'failed_transactions': self.metrics_collector.get_failure_count(),
            
            # Latency metrics
            'avg_transaction_latency': self.metrics_collector.get_avg_latency(),
            'p95_transaction_latency': self.metrics_collector.get_p95_latency(),
            'p99_transaction_latency': self.metrics_collector.get_p99_latency(),
            
            # Phase-specific metrics
            'phase1_avg_duration': self.metrics_collector.get_phase1_duration(),
            'phase2_avg_duration': self.metrics_collector.get_phase2_duration(),
            
            # Failure metrics
            'timeout_rate': self.metrics_collector.get_timeout_rate(),
            'participant_failure_rate': self.metrics_collector.get_participant_failure_rate(),
            'coordinator_failure_rate': self.metrics_collector.get_coordinator_failure_rate(),
            
            # Resource utilization
            'pending_transactions': self.metrics_collector.get_pending_count(),
            'locked_resources': self.metrics_collector.get_locked_resource_count(),
            'memory_usage': self.metrics_collector.get_memory_usage(),
            
            # Recovery metrics
            'recovery_operations': self.metrics_collector.get_recovery_count(),
            'manual_interventions': self.metrics_collector.get_manual_intervention_count()
        }
        
        return metrics
    
    def check_health_alerts(self, metrics):
        """Check for alert conditions"""
        
        alerts = []
        
        # High failure rate alert
        if metrics['failed_transactions'] / (metrics['successful_transactions'] + metrics['failed_transactions']) > 0.05:
            alerts.append(Alert(
                severity='HIGH',
                message=f"High transaction failure rate: {metrics['failed_transactions']}"
            ))
        
        # High latency alert
        if metrics['p95_transaction_latency'] > 5000:  # 5 seconds
            alerts.append(Alert(
                severity='MEDIUM',
                message=f"High transaction latency: P95 = {metrics['p95_transaction_latency']}ms"
            ))
        
        # Stuck transactions alert
        if metrics['pending_transactions'] > 1000:
            alerts.append(Alert(
                severity='HIGH',
                message=f"Too many pending transactions: {metrics['pending_transactions']}"
            ))
        
        # Frequent manual interventions
        if metrics['manual_interventions'] > 10:  # per hour
            alerts.append(Alert(
                severity='MEDIUM',
                message="Frequent manual interventions required - check participant health"
            ))
        
        for alert in alerts:
            self.alerting_system.send_alert(alert)
        
        return alerts

class TransactionTracer:
    def __init__(self):
        self.trace_storage = TraceStorage()
        
    def trace_transaction(self, transaction_id):
        """Detailed tracing of transaction execution"""
        
        trace = TransactionTrace(transaction_id)
        
        try:
            # Phase 1 tracing
            trace.add_event('PHASE1_START', self.get_timestamp())
            
            for participant in self.get_participants(transaction_id):
                prepare_start = self.get_timestamp()
                trace.add_event(f'PREPARE_SEND_{participant.id}', prepare_start)
                
                response = participant.prepare(transaction_id)
                
                prepare_end = self.get_timestamp()
                trace.add_event(f'PREPARE_RESPONSE_{participant.id}', prepare_end, {
                    'response': response.status,
                    'duration': prepare_end - prepare_start
                })
            
            phase1_end = self.get_timestamp()
            trace.add_event('PHASE1_COMPLETE', phase1_end)
            
            # Decision point
            decision = self.make_decision(transaction_id)
            trace.add_event('DECISION', self.get_timestamp(), {'decision': decision})
            
            # Phase 2 tracing
            trace.add_event('PHASE2_START', self.get_timestamp())
            
            for participant in self.get_participants(transaction_id):
                decision_start = self.get_timestamp()
                trace.add_event(f'DECISION_SEND_{participant.id}', decision_start)
                
                if decision == 'COMMIT':
                    response = participant.commit(transaction_id)
                else:
                    response = participant.abort(transaction_id)
                
                decision_end = self.get_timestamp()
                trace.add_event(f'DECISION_RESPONSE_{participant.id}', decision_end, {
                    'response': response.status,
                    'duration': decision_end - decision_start
                })
            
            phase2_end = self.get_timestamp()
            trace.add_event('PHASE2_COMPLETE', phase2_end)
            trace.add_event('TRANSACTION_COMPLETE', phase2_end)
            
        except Exception as e:
            trace.add_event('ERROR', self.get_timestamp(), {'error': str(e)})
            
        finally:
            self.trace_storage.store_trace(trace)
        
        return trace
    
    def analyze_trace(self, transaction_id):
        """Analyze transaction trace for performance insights"""
        
        trace = self.trace_storage.get_trace(transaction_id)
        
        analysis = {
            'total_duration': self.calculate_total_duration(trace),
            'phase1_duration': self.calculate_phase_duration(trace, 'PHASE1'),
            'phase2_duration': self.calculate_phase_duration(trace, 'PHASE2'),
            'slowest_participant': self.find_slowest_participant(trace),
            'bottlenecks': self.identify_bottlenecks(trace),
            'error_points': self.find_error_points(trace)
        }
        
        return analysis

# Debugging utilities
class TwoPhaseCommitDebugger:
    def __init__(self):
        self.transaction_log = TransactionLog()
        self.participant_logs = {}
        
    def debug_stuck_transaction(self, transaction_id):
        """Debug a stuck transaction"""
        
        debug_info = {
            'transaction_id': transaction_id,
            'coordinator_state': self.get_coordinator_state(transaction_id),
            'participant_states': {},
            'potential_issues': []
        }
        
        # Check coordinator state
        coord_state = debug_info['coordinator_state']
        if coord_state['status'] == 'WAITING_FOR_VOTES':
            # Check which participants haven't responded
            for participant_id in coord_state['participants']:
                if participant_id not in coord_state['received_votes']:
                    participant_state = self.get_participant_state(participant_id, transaction_id)
                    debug_info['participant_states'][participant_id] = participant_state
                    
                    if participant_state['status'] == 'UNREACHABLE':
                        debug_info['potential_issues'].append(f"Participant {participant_id} unreachable")
                    elif participant_state['status'] == 'PROCESSING':
                        debug_info['potential_issues'].append(f"Participant {participant_id} slow to respond")
        
        elif coord_state['status'] == 'WAITING_FOR_ACKS':
            # Check which participants haven't acknowledged
            for participant_id in coord_state['participants']:
                if participant_id not in coord_state['received_acks']:
                    participant_state = self.get_participant_state(participant_id, transaction_id)
                    debug_info['participant_states'][participant_id] = participant_state
                    
                    if participant_state['status'] == 'UNREACHABLE':
                        debug_info['potential_issues'].append(f"Participant {participant_id} unreachable during commit/abort")
        
        return debug_info
    
    def suggest_recovery_action(self, debug_info):
        """Suggest recovery actions based on debug information"""
        
        suggestions = []
        
        if 'unreachable' in str(debug_info['potential_issues']).lower():
            suggestions.append("Check network connectivity to unreachable participants")
            suggestions.append("Consider participant failure recovery procedures")
        
        if 'slow to respond' in str(debug_info['potential_issues']).lower():
            suggestions.append("Check participant resource utilization")
            suggestions.append("Consider increasing timeout values")
        
        coord_state = debug_info['coordinator_state']
        if coord_state['status'] == 'WAITING_FOR_VOTES':
            suggestions.append("Consider aborting transaction if waiting too long")
        elif coord_state['status'] == 'WAITING_FOR_ACKS':
            suggestions.append("Continue retrying - decision already made")
            suggestions.append("Check participant logs for commit/abort completion")
        
        return suggestions
```

---

## Performance Optimization Techniques

### 1. Batching और Group Commit

```python
class BatchingTwoPhaseCommit:
    def __init__(self, batch_size=100, batch_timeout=50):  # 50ms
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_transactions = []
        self.batch_timer = None
        
    def submit_transaction(self, transaction):
        """Submit transaction for batched processing"""
        self.pending_transactions.append(transaction)
        
        if len(self.pending_transactions) >= self.batch_size:
            # Batch is full - process immediately
            self.process_batch()
        elif self.batch_timer is None:
            # Start timer for batch timeout
            self.batch_timer = threading.Timer(self.batch_timeout / 1000.0, self.process_batch)
            self.batch_timer.start()
    
    def process_batch(self):
        """Process batch of transactions using group 2PC"""
        if not self.pending_transactions:
            return
        
        batch = self.pending_transactions.copy()
        self.pending_transactions.clear()
        
        if self.batch_timer:
            self.batch_timer.cancel()
            self.batch_timer = None
        
        try:
            batch_id = self.generate_batch_id()
            
            # Phase 1: Group prepare for all transactions in batch
            group_prepare_result = self.group_prepare_phase(batch, batch_id)
            
            if group_prepare_result.all_voted_yes():
                # Phase 2: Group commit
                self.group_commit_phase(batch, batch_id)
            else:
                # Phase 2: Group abort
                self.group_abort_phase(batch, batch_id)
                
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            # Individual transaction fallback
            for txn in batch:
                self.process_individual_transaction(txn)
    
    def group_prepare_phase(self, batch, batch_id):
        """Execute prepare phase for entire batch"""
        
        # Group transactions by participants
        participant_groups = {}
        for txn in batch:
            for participant in txn.participants:
                if participant.id not in participant_groups:
                    participant_groups[participant.id] = []
                participant_groups[participant.id].append(txn)
        
        # Send batched prepare requests
        group_votes = {}
        
        for participant_id, transactions in participant_groups.items():
            participant = self.get_participant(participant_id)
            
            try:
                batch_prepare_request = BatchPrepareRequest(
                    batch_id=batch_id,
                    transactions=transactions
                )
                
                response = participant.batch_prepare(batch_prepare_request)
                group_votes[participant_id] = response
                
            except Exception as e:
                # If any participant fails, entire batch fails
                group_votes[participant_id] = BatchPrepareResponse(
                    status='NO',
                    failed_transactions=transactions
                )
        
        return GroupPrepareResult(group_votes)

class ParticipantBatchProcessor:
    def batch_prepare(self, batch_request):
        """Handle batched prepare request"""
        batch_response = BatchPrepareResponse(batch_request.batch_id)
        
        try:
            # Start database transaction for entire batch
            with self.database.begin_transaction() as db_txn:
                
                for transaction in batch_request.transactions:
                    try:
                        # Prepare individual transaction within batch
                        self.prepare_individual_transaction(transaction, db_txn)
                        batch_response.add_success(transaction.id)
                        
                    except Exception as e:
                        batch_response.add_failure(transaction.id, str(e))
                
                # If all transactions prepared successfully
                if batch_response.all_successful():
                    batch_response.status = 'YES'
                else:
                    batch_response.status = 'NO'
                    # Rollback entire batch
                    db_txn.rollback()
                    return batch_response
                
                # Don't commit yet - wait for phase 2
                
        except Exception as e:
            batch_response.status = 'NO'
            batch_response.error = str(e)
        
        return batch_response
```

### 2. Pipelined 2PC

```python
class PipelinedTwoPhaseCommit:
    def __init__(self, pipeline_depth=10):
        self.pipeline_depth = pipeline_depth
        self.phase1_queue = asyncio.Queue(maxsize=pipeline_depth)
        self.phase2_queue = asyncio.Queue(maxsize=pipeline_depth)
        
    async def start_pipeline(self):
        """Start pipelined processing"""
        # Start pipeline workers
        phase1_workers = [
            asyncio.create_task(self.phase1_worker(i))
            for i in range(self.pipeline_depth)
        ]
        
        phase2_workers = [
            asyncio.create_task(self.phase2_worker(i))
            for i in range(self.pipeline_depth)
        ]
        
        await asyncio.gather(*phase1_workers, *phase2_workers)
    
    async def phase1_worker(self, worker_id):
        """Worker for Phase 1 processing"""
        while True:
            try:
                transaction = await self.phase1_queue.get()
                
                # Execute Phase 1
                prepare_result = await self.execute_phase1(transaction)
                
                # Put result in Phase 2 queue
                await self.phase2_queue.put((transaction, prepare_result))
                
                self.phase1_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Phase 1 worker {worker_id} error: {e}")
    
    async def phase2_worker(self, worker_id):
        """Worker for Phase 2 processing"""
        while True:
            try:
                transaction, prepare_result = await self.phase2_queue.get()
                
                # Execute Phase 2 based on Phase 1 result
                if prepare_result.all_voted_yes():
                    await self.execute_commit(transaction)
                else:
                    await self.execute_abort(transaction)
                
                self.phase2_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Phase 2 worker {worker_id} error: {e}")
    
    async def execute_phase1(self, transaction):
        """Execute Phase 1 with concurrent participant communication"""
        prepare_tasks = []
        
        for participant in transaction.participants:
            task = asyncio.create_task(participant.async_prepare(transaction.id))
            prepare_tasks.append(task)
        
        # Wait for all prepare responses
        prepare_responses = await asyncio.gather(*prepare_tasks, return_exceptions=True)
        
        # Process responses
        prepare_result = PrepareResult(transaction.id)
        for i, response in enumerate(prepare_responses):
            participant = transaction.participants[i]
            
            if isinstance(response, Exception):
                prepare_result.add_vote(participant.id, 'NO', str(response))
            else:
                prepare_result.add_vote(participant.id, response.vote, response.reason)
        
        return prepare_result
    
    async def submit_transaction(self, transaction):
        """Submit transaction to pipeline"""
        await self.phase1_queue.put(transaction)
```

### 3. Optimistic 2PC

```python
class OptimisticTwoPhaseCommit:
    def __init__(self):
        self.conflict_detector = ConflictDetector()
        self.optimistic_stats = OptimisticStats()
        
    def execute_optimistic_transaction(self, transaction):
        """Execute transaction with optimistic approach"""
        
        # Check for likely conflicts
        conflict_probability = self.conflict_detector.estimate_conflict_probability(transaction)
        
        if conflict_probability < 0.1:  # Low conflict probability
            return self.execute_optimistic_path(transaction)
        else:
            return self.execute_pessimistic_path(transaction)
    
    def execute_optimistic_path(self, transaction):
        """Execute with optimistic assumptions"""
        try:
            # Assume all participants will vote YES
            # Start Phase 2 preparation early
            self.optimistic_stats.increment_optimistic_attempts()
            
            # Phase 1: Send prepares but start Phase 2 preparation
            phase1_results = []
            phase2_preparation_task = asyncio.create_task(
                self.prepare_phase2_optimistically(transaction)
            )
            
            for participant in transaction.participants:
                result = participant.prepare(transaction.id)
                phase1_results.append(result)
                
                if result.vote == 'NO':
                    # Optimistic assumption failed
                    phase2_preparation_task.cancel()
                    self.optimistic_stats.increment_optimistic_failures()
                    return self.execute_abort_phase(transaction)
            
            # All voted YES - complete optimistic commit
            phase2_preparation_task.wait()  # Wait for Phase 2 preparation
            
            commit_results = self.execute_commit_phase_optimized(transaction)
            
            self.optimistic_stats.increment_optimistic_successes()
            return TransactionResult(status='COMMITTED', results=commit_results)
            
        except OptimisticFailure:
            # Fallback to pessimistic path
            return self.execute_pessimistic_path(transaction)
    
    def prepare_phase2_optimistically(self, transaction):
        """Prepare Phase 2 operations assuming Phase 1 success"""
        
        # Pre-allocate resources for commit
        for participant in transaction.participants:
            participant.prepare_commit_resources(transaction.id)
        
        # Prepare commit messages
        commit_messages = []
        for participant in transaction.participants:
            message = CommitMessage(
                transaction_id=transaction.id,
                participant_id=participant.id
            )
            commit_messages.append(message)
        
        return commit_messages

class ConflictDetector:
    def __init__(self):
        self.resource_access_patterns = {}
        self.conflict_history = ConflictHistory()
        
    def estimate_conflict_probability(self, transaction):
        """Estimate probability of conflict based on historical data"""
        
        resources = transaction.get_accessed_resources()
        current_time = datetime.now()
        
        conflict_score = 0.0
        
        for resource in resources:
            # Check recent access patterns
            recent_accesses = self.resource_access_patterns.get(resource, [])
            
            # Remove old accesses (older than 1 minute)
            recent_accesses = [
                access for access in recent_accesses 
                if current_time - access.timestamp < timedelta(minutes=1)
            ]
            
            # Calculate conflict score based on access frequency
            access_frequency = len(recent_accesses)
            conflict_score += access_frequency * 0.1
        
        # Use historical conflict data
        historical_conflict_rate = self.conflict_history.get_conflict_rate(
            transaction.transaction_type,
            resources
        )
        
        conflict_score += historical_conflict_rate
        
        return min(conflict_score, 1.0)  # Cap at 1.0
```

---

## Future Trends और Modern Alternatives

### 1. Saga Pattern Integration

```python
class SagaCoordinatedTransaction:
    """Hybrid approach combining Saga pattern with 2PC for critical operations"""
    
    def __init__(self):
        self.saga_coordinator = SagaCoordinator()
        self.two_pc_coordinator = TwoPhaseCommitCoordinator()
        self.decision_engine = TransactionDecisionEngine()
        
    def execute_hybrid_transaction(self, transaction_request):
        """Execute transaction using appropriate pattern based on requirements"""
        
        # Analyze transaction requirements
        analysis = self.decision_engine.analyze_transaction(transaction_request)
        
        if analysis.requires_strong_consistency:
            # Use 2PC for operations requiring strong consistency
            critical_operations = analysis.critical_operations
            
            # Execute critical part with 2PC
            critical_result = self.two_pc_coordinator.execute_transaction(critical_operations)
            
            if critical_result.status == 'COMMITTED':
                # Execute non-critical part with Saga
                non_critical_operations = analysis.non_critical_operations
                saga_result = self.saga_coordinator.execute_saga(non_critical_operations)
                
                return HybridTransactionResult(critical_result, saga_result)
            else:
                return HybridTransactionResult(critical_result, None)
                
        else:
            # Use pure Saga pattern
            return self.saga_coordinator.execute_saga(transaction_request.operations)

class TransactionDecisionEngine:
    def analyze_transaction(self, transaction_request):
        """Analyze transaction to determine optimal execution pattern"""
        
        analysis = TransactionAnalysis()
        
        for operation in transaction_request.operations:
            if operation.consistency_requirement == 'STRONG':
                analysis.critical_operations.append(operation)
                analysis.requires_strong_consistency = True
            elif operation.consistency_requirement == 'EVENTUAL':
                analysis.non_critical_operations.append(operation)
            else:
                # Default: treat as non-critical
                analysis.non_critical_operations.append(operation)
        
        return analysis
```

### 2. Blockchain Integration

```python
class BlockchainTwoPhaseCommit:
    """2PC implementation using blockchain for immutable transaction logging"""
    
    def __init__(self, blockchain_network):
        self.blockchain = blockchain_network
        self.smart_contract = TwoPhaseCommitContract()
        
    def execute_blockchain_2pc(self, transaction):
        """Execute 2PC with blockchain-based logging"""
        
        # Phase 1: Record prepare phase on blockchain
        prepare_block = self.blockchain.create_block({
            'transaction_id': transaction.id,
            'phase': 'PREPARE',
            'participants': [p.id for p in transaction.participants],
            'timestamp': datetime.now().isoformat()
        })
        
        prepare_votes = {}
        for participant in transaction.participants:
            try:
                vote = participant.prepare_with_blockchain_proof(transaction.id, prepare_block.hash)
                prepare_votes[participant.id] = vote
                
                # Record vote on blockchain
                vote_block = self.blockchain.create_block({
                    'transaction_id': transaction.id,
                    'participant_id': participant.id,
                    'vote': vote.status,
                    'prepare_block_hash': prepare_block.hash,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                prepare_votes[participant.id] = PrepareVote('NO', str(e))
        
        # Make decision
        decision = 'COMMIT' if all(vote.status == 'YES' for vote in prepare_votes.values()) else 'ABORT'
        
        # Phase 2: Record decision on blockchain
        decision_block = self.blockchain.create_block({
            'transaction_id': transaction.id,
            'phase': 'DECISION',
            'decision': decision,
            'prepare_block_hash': prepare_block.hash,
            'timestamp': datetime.now().isoformat()
        })
        
        # Execute decision on all participants
        for participant in transaction.participants:
            if decision == 'COMMIT':
                result = participant.commit_with_blockchain_proof(transaction.id, decision_block.hash)
            else:
                result = participant.abort_with_blockchain_proof(transaction.id, decision_block.hash)
            
            # Record completion on blockchain
            completion_block = self.blockchain.create_block({
                'transaction_id': transaction.id,
                'participant_id': participant.id,
                'action': decision,
                'result': result.status,
                'decision_block_hash': decision_block.hash,
                'timestamp': datetime.now().isoformat()
            })
        
        return BlockchainTransactionResult(
            transaction_id=transaction.id,
            decision=decision,
            blockchain_proof=decision_block.hash
        )

class SmartContractTwoPhaseCommit:
    """Smart contract implementation of 2PC protocol"""
    
    def __init__(self, ethereum_client):
        self.eth = ethereum_client
        self.contract_address = "0x..."
        
    def deploy_2pc_contract(self):
        """Deploy 2PC smart contract"""
        
        contract_source = """
        pragma solidity ^0.8.0;
        
        contract TwoPhaseCommit {
            enum TransactionState { PREPARING, COMMITTING, ABORTING, COMPLETED }
            enum Vote { NONE, YES, NO }
            
            struct Transaction {
                address coordinator;
                address[] participants;
                mapping(address => Vote) votes;
                TransactionState state;
                uint256 created_at;
                uint256 decision_at;
            }
            
            mapping(bytes32 => Transaction) public transactions;
            
            event TransactionCreated(bytes32 indexed txId, address coordinator);
            event VoteCast(bytes32 indexed txId, address participant, Vote vote);
            event DecisionMade(bytes32 indexed txId, TransactionState decision);
            
            function createTransaction(bytes32 txId, address[] memory participants) public {
                require(transactions[txId].coordinator == address(0), "Transaction exists");
                
                Transaction storage txn = transactions[txId];
                txn.coordinator = msg.sender;
                txn.participants = participants;
                txn.state = TransactionState.PREPARING;
                txn.created_at = block.timestamp;
                
                emit TransactionCreated(txId, msg.sender);
            }
            
            function castVote(bytes32 txId, Vote vote) public {
                Transaction storage txn = transactions[txId];
                require(txn.state == TransactionState.PREPARING, "Not in prepare phase");
                
                bool isParticipant = false;
                for (uint i = 0; i < txn.participants.length; i++) {
                    if (txn.participants[i] == msg.sender) {
                        isParticipant = true;
                        break;
                    }
                }
                require(isParticipant, "Not a participant");
                
                txn.votes[msg.sender] = vote;
                emit VoteCast(txId, msg.sender, vote);
                
                // Check if all votes received
                if (allVotesReceived(txId)) {
                    makeDecision(txId);
                }
            }
            
            function makeDecision(bytes32 txId) internal {
                Transaction storage txn = transactions[txId];
                require(msg.sender == txn.coordinator, "Only coordinator can make decision");
                
                bool allYes = true;
                for (uint i = 0; i < txn.participants.length; i++) {
                    if (txn.votes[txn.participants[i]] != Vote.YES) {
                        allYes = false;
                        break;
                    }
                }
                
                if (allYes) {
                    txn.state = TransactionState.COMMITTING;
                } else {
                    txn.state = TransactionState.ABORTING;
                }
                
                txn.decision_at = block.timestamp;
                emit DecisionMade(txId, txn.state);
            }
            
            function allVotesReceived(bytes32 txId) internal view returns (bool) {
                Transaction storage txn = transactions[txId];
                for (uint i = 0; i < txn.participants.length; i++) {
                    if (txn.votes[txn.participants[i]] == Vote.NONE) {
                        return false;
                    }
                }
                return true;
            }
        }
        """
        
        # Deploy contract (implementation depends on web3 library)
        contract = self.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.eth.waitForTransactionReceipt(tx_hash)
        
        return tx_receipt.contractAddress
```

### 3. AI-Powered Optimization

```python
class AIOptimizedTwoPhaseCommit:
    """AI-powered optimization of 2PC protocol"""
    
    def __init__(self):
        self.ml_predictor = ConflictPredictor()
        self.performance_optimizer = PerformanceOptimizer()
        self.adaptive_timeout_manager = AdaptiveTimeoutManager()
        
    def execute_ai_optimized_transaction(self, transaction):
        """Execute 2PC with AI-based optimizations"""
        
        # Predict optimal execution strategy
        strategy = self.ml_predictor.predict_optimal_strategy(transaction)
        
        # Adjust timeouts based on historical performance
        optimized_timeouts = self.adaptive_timeout_manager.get_optimized_timeouts(
            transaction.participants,
            transaction.complexity_score
        )
        
        # Execute with AI-guided optimizations
        if strategy.recommended_approach == 'BATCH':
            return self.execute_batched_transaction(transaction, optimized_timeouts)
        elif strategy.recommended_approach == 'PIPELINE':
            return self.execute_pipelined_transaction(transaction, optimized_timeouts)
        else:
            return self.execute_standard_transaction(transaction, optimized_timeouts)

class ConflictPredictor:
    """Machine learning model for predicting transaction conflicts"""
    
    def __init__(self):
        self.model = self.load_trained_model()
        self.feature_extractor = FeatureExtractor()
        
    def predict_optimal_strategy(self, transaction):
        """Predict optimal execution strategy for transaction"""
        
        features = self.feature_extractor.extract_features(transaction)
        
        # Features might include:
        # - Resource access patterns
        # - Participant response time history
        # - Current system load
        # - Time of day patterns
        # - Transaction size and complexity
        
        prediction = self.model.predict([features])
        confidence = self.model.predict_proba([features]).max()
        
        return OptimizationStrategy(
            recommended_approach=prediction[0],
            confidence=confidence,
            expected_performance=self.estimate_performance(features, prediction[0])
        )

class AdaptiveTimeoutManager:
    """Adaptive timeout management based on participant behavior"""
    
    def __init__(self):
        self.participant_performance_history = {}
        self.network_condition_monitor = NetworkConditionMonitor()
        
    def get_optimized_timeouts(self, participants, complexity_score):
        """Calculate optimized timeouts for participants"""
        
        optimized_timeouts = {}
        current_network_conditions = self.network_condition_monitor.get_current_conditions()
        
        for participant in participants:
            historical_performance = self.participant_performance_history.get(
                participant.id, 
                ParticipantPerformance()
            )
            
            # Base timeout from historical data
            base_timeout = historical_performance.get_average_response_time()
            
            # Adjust for current network conditions
            network_adjustment = current_network_conditions.get_latency_multiplier()
            
            # Adjust for transaction complexity
            complexity_adjustment = 1.0 + (complexity_score * 0.1)
            
            # Add safety margin
            safety_margin = 1.5
            
            optimized_timeout = base_timeout * network_adjustment * complexity_adjustment * safety_margin
            
            # Ensure minimum and maximum bounds
            optimized_timeout = max(min(optimized_timeout, 30000), 1000)  # 1s to 30s
            
            optimized_timeouts[participant.id] = optimized_timeout
        
        return optimized_timeouts
    
    def update_performance_history(self, participant_id, response_time, success):
        """Update participant performance history"""
        
        if participant_id not in self.participant_performance_history:
            self.participant_performance_history[participant_id] = ParticipantPerformance()
        
        performance = self.participant_performance_history[participant_id]
        performance.add_measurement(response_time, success)
        
        # Keep only recent measurements (last 1000)
        performance.prune_old_measurements(max_measurements=1000)
```

---

## Code Examples और Implementation Patterns

### Production-Ready Implementation Template

```python
"""
Production-ready Two-Phase Commit implementation
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import json

class TransactionState(Enum):
    INITIATED = "INITIATED"
    PREPARING = "PREPARING"
    PREPARED = "PREPARED"
    COMMITTING = "COMMITTING"
    COMMITTED = "COMMITTED"
    ABORTING = "ABORTING"
    ABORTED = "ABORTED"
    FAILED = "FAILED"

class VoteType(Enum):
    YES = "YES"
    NO = "NO"
    TIMEOUT = "TIMEOUT"

@dataclass
class TransactionContext:
    transaction_id: str
    coordinator_id: str
    participants: List[str]
    operation_data: Dict[str, Any]
    timeout_ms: int
    created_at: float
    state: TransactionState = TransactionState.INITIATED

@dataclass
class PrepareResponse:
    participant_id: str
    transaction_id: str
    vote: VoteType
    message: Optional[str] = None
    response_time: Optional[float] = None

class TransactionParticipant(ABC):
    """Abstract base class for transaction participants"""
    
    @abstractmethod
    async def prepare(self, transaction_context: TransactionContext) -> PrepareResponse:
        """Phase 1: Prepare for transaction"""
        pass
    
    @abstractmethod
    async def commit(self, transaction_id: str) -> bool:
        """Phase 2: Commit transaction"""
        pass
    
    @abstractmethod
    async def abort(self, transaction_id: str) -> bool:
        """Phase 2: Abort transaction"""
        pass

class ProductionTwoPhaseCommitCoordinator:
    """Production-ready 2PC Coordinator implementation"""
    
    def __init__(self, coordinator_id: str):
        self.coordinator_id = coordinator_id
        self.participants: Dict[str, TransactionParticipant] = {}
        self.active_transactions: Dict[str, TransactionContext] = {}
        self.transaction_log = TransactionLogger()
        self.metrics = TransactionMetrics()
        self.recovery_manager = RecoveryManager()
        self.logger = logging.getLogger(__name__)
        
    def register_participant(self, participant_id: str, participant: TransactionParticipant):
        """Register a transaction participant"""
        self.participants[participant_id] = participant
        
    async def execute_transaction(self, operation_data: Dict[str, Any], 
                                participant_ids: List[str],
                                timeout_ms: int = 30000) -> TransactionResult:
        """Execute distributed transaction using 2PC"""
        
        transaction_id = str(uuid.uuid4())
        start_time = time.time()
        
        context = TransactionContext(
            transaction_id=transaction_id,
            coordinator_id=self.coordinator_id,
            participants=participant_ids,
            operation_data=operation_data,
            timeout_ms=timeout_ms,
            created_at=start_time
        )
        
        self.active_transactions[transaction_id] = context
        self.transaction_log.log_transaction_start(context)
        
        try:
            # Phase 1: Prepare
            self.logger.info(f"Starting Phase 1 for transaction {transaction_id}")
            context.state = TransactionState.PREPARING
            
            prepare_result = await self.execute_prepare_phase(context)
            
            if prepare_result.unanimous_yes():
                # Phase 2: Commit
                self.logger.info(f"All participants voted YES, committing {transaction_id}")
                context.state = TransactionState.COMMITTING
                
                commit_result = await self.execute_commit_phase(context)
                
                if commit_result.all_committed():
                    context.state = TransactionState.COMMITTED
                    result = TransactionResult(
                        transaction_id=transaction_id,
                        status='COMMITTED',
                        duration=time.time() - start_time
                    )
                else:
                    context.state = TransactionState.FAILED
                    result = TransactionResult(
                        transaction_id=transaction_id,
                        status='PARTIAL_COMMIT',
                        duration=time.time() - start_time,
                        error="Some participants failed to commit"
                    )
            else:
                # Phase 2: Abort
                self.logger.info(f"Some participants voted NO, aborting {transaction_id}")
                context.state = TransactionState.ABORTING
                
                abort_result = await self.execute_abort_phase(context)
                
                context.state = TransactionState.ABORTED
                result = TransactionResult(
                    transaction_id=transaction_id,
                    status='ABORTED',
                    duration=time.time() - start_time,
                    abort_reason=prepare_result.get_abort_reason()
                )
                
        except Exception as e:
            self.logger.error(f"Transaction {transaction_id} failed with error: {e}")
            context.state = TransactionState.FAILED
            
            # Attempt cleanup
            await self.execute_abort_phase(context)
            
            result = TransactionResult(
                transaction_id=transaction_id,
                status='FAILED',
                duration=time.time() - start_time,
                error=str(e)
            )
        
        finally:
            # Cleanup
            self.transaction_log.log_transaction_complete(context, result)
            self.metrics.record_transaction(result)
            
            if transaction_id in self.active_transactions:
                del self.active_transactions[transaction_id]
        
        return result
    
    async def execute_prepare_phase(self, context: TransactionContext) -> PrepareResult:
        """Execute Phase 1: Prepare"""
        
        prepare_tasks = []
        timeout_seconds = context.timeout_ms / 1000.0
        
        for participant_id in context.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                self.send_prepare_with_timeout(participant, context, timeout_seconds)
            )
            prepare_tasks.append((participant_id, task))
        
        prepare_responses = {}
        
        # Wait for all prepare responses
        for participant_id, task in prepare_tasks:
            try:
                response = await task
                prepare_responses[participant_id] = response
            except asyncio.TimeoutError:
                self.logger.warning(f"Prepare timeout for participant {participant_id}")
                prepare_responses[participant_id] = PrepareResponse(
                    participant_id=participant_id,
                    transaction_id=context.transaction_id,
                    vote=VoteType.TIMEOUT
                )
            except Exception as e:
                self.logger.error(f"Prepare error for participant {participant_id}: {e}")
                prepare_responses[participant_id] = PrepareResponse(
                    participant_id=participant_id,
                    transaction_id=context.transaction_id,
                    vote=VoteType.NO,
                    message=str(e)
                )
        
        return PrepareResult(context.transaction_id, prepare_responses)
    
    async def send_prepare_with_timeout(self, participant: TransactionParticipant, 
                                       context: TransactionContext, 
                                       timeout_seconds: float) -> PrepareResponse:
        """Send prepare request with timeout"""
        
        try:
            response = await asyncio.wait_for(
                participant.prepare(context),
                timeout=timeout_seconds
            )
            return response
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            raise e
    
    async def execute_commit_phase(self, context: TransactionContext) -> CommitResult:
        """Execute Phase 2: Commit"""
        
        commit_tasks = []
        
        for participant_id in context.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(
                self.send_commit_with_retry(participant, context.transaction_id)
            )
            commit_tasks.append((participant_id, task))
        
        commit_results = {}
        
        for participant_id, task in commit_tasks:
            try:
                success = await task
                commit_results[participant_id] = success
            except Exception as e:
                self.logger.error(f"Commit error for participant {participant_id}: {e}")
                commit_results[participant_id] = False
        
        return CommitResult(context.transaction_id, commit_results)
    
    async def send_commit_with_retry(self, participant: TransactionParticipant, 
                                   transaction_id: str, max_retries: int = 3) -> bool:
        """Send commit request with retries"""
        
        for attempt in range(max_retries + 1):
            try:
                success = await participant.commit(transaction_id)
                if success:
                    return True
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        return False
    
    async def execute_abort_phase(self, context: TransactionContext) -> AbortResult:
        """Execute Phase 2: Abort"""
        
        abort_tasks = []
        
        for participant_id in context.participants:
            participant = self.participants[participant_id]
            task = asyncio.create_task(participant.abort(context.transaction_id))
            abort_tasks.append((participant_id, task))
        
        abort_results = {}
        
        for participant_id, task in abort_tasks:
            try:
                success = await task
                abort_results[participant_id] = success
            except Exception as e:
                self.logger.warning(f"Abort error for participant {participant_id}: {e}")
                abort_results[participant_id] = False
        
        return AbortResult(context.transaction_id, abort_results)

# Supporting classes
@dataclass
class TransactionResult:
    transaction_id: str
    status: str
    duration: float
    error: Optional[str] = None
    abort_reason: Optional[str] = None

class PrepareResult:
    def __init__(self, transaction_id: str, responses: Dict[str, PrepareResponse]):
        self.transaction_id = transaction_id
        self.responses = responses
    
    def unanimous_yes(self) -> bool:
        return all(response.vote == VoteType.YES for response in self.responses.values())
    
    def get_abort_reason(self) -> str:
        no_votes = [r for r in self.responses.values() if r.vote != VoteType.YES]
        if no_votes:
            return f"Participants voted NO: {[r.participant_id for r in no_votes]}"
        return "Unknown"

class CommitResult:
    def __init__(self, transaction_id: str, results: Dict[str, bool]):
        self.transaction_id = transaction_id
        self.results = results
    
    def all_committed(self) -> bool:
        return all(self.results.values())

class AbortResult:
    def __init__(self, transaction_id: str, results: Dict[str, bool]):
        self.transaction_id = transaction_id
        self.results = results

# Example participant implementation
class DatabaseParticipant(TransactionParticipant):
    """Example database participant"""
    
    def __init__(self, participant_id: str, database_connection):
        self.participant_id = participant_id
        self.db = database_connection
        self.prepared_transactions: Dict[str, Any] = {}
        
    async def prepare(self, context: TransactionContext) -> PrepareResponse:
        """Prepare database transaction"""
        start_time = time.time()
        
        try:
            # Begin database transaction
            db_txn = await self.db.begin_transaction()
            
            # Execute operations
            operations = context.operation_data.get(self.participant_id, [])
            for operation in operations:
                await self.execute_operation(db_txn, operation)
            
            # Store prepared transaction
            self.prepared_transactions[context.transaction_id] = db_txn
            
            response_time = time.time() - start_time
            
            return PrepareResponse(
                participant_id=self.participant_id,
                transaction_id=context.transaction_id,
                vote=VoteType.YES,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return PrepareResponse(
                participant_id=self.participant_id,
                transaction_id=context.transaction_id,
                vote=VoteType.NO,
                message=str(e),
                response_time=response_time
            )
    
    async def commit(self, transaction_id: str) -> bool:
        """Commit prepared transaction"""
        if transaction_id in self.prepared_transactions:
            try:
                db_txn = self.prepared_transactions[transaction_id]
                await db_txn.commit()
                del self.prepared_transactions[transaction_id]
                return True
            except Exception as e:
                logging.error(f"Commit failed for {transaction_id}: {e}")
                return False
        return False
    
    async def abort(self, transaction_id: str) -> bool:
        """Abort prepared transaction"""
        if transaction_id in self.prepared_transactions:
            try:
                db_txn = self.prepared_transactions[transaction_id]
                await db_txn.rollback()
                del self.prepared_transactions[transaction_id]
                return True
            except Exception as e:
                logging.error(f"Abort failed for {transaction_id}: {e}")
                return False
        return True  # Already aborted is OK
    
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

# Example usage
async def main():
    # Setup coordinator
    coordinator = ProductionTwoPhaseCommitCoordinator("coord-001")
    
    # Setup participants
    db1 = DatabaseParticipant("db1", database_connection_1)
    db2 = DatabaseParticipant("db2", database_connection_2)
    
    coordinator.register_participant("db1", db1)
    coordinator.register_participant("db2", db2)
    
    # Execute distributed transaction
    operation_data = {
        "db1": [
            {
                "type": "INSERT",
                "sql": "INSERT INTO orders (id, amount) VALUES (?, ?)",
                "params": [1001, 500.00]
            }
        ],
        "db2": [
            {
                "type": "UPDATE",
                "sql": "UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?",
                "params": [1, 2001]
            }
        ]
    }
    
    result = await coordinator.execute_transaction(
        operation_data=operation_data,
        participant_ids=["db1", "db2"],
        timeout_ms=10000
    )
    
    print(f"Transaction result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Conclusion

Two-Phase Commit Protocol एक fundamental distributed systems algorithm है जो **distributed atomic transactions** ensure करता है। हमने इस episode में देखा:

### Key Takeaways:

1. **Mumbai Wedding Analogy**: 2PC को समझने के लिए wedding coordination एक perfect real-world example है

2. **Protocol Phases**:
   - **Phase 1 (Prepare)**: सभी participants से vote लेना
   - **Phase 2 (Commit/Abort)**: Final decision implement करना

3. **Production Systems**:
   - Oracle RAC, PostgreSQL XA, MySQL XA
   - Banking systems (UPI, RTGS, NEFT)
   - Cross-bank transfers

4. **Critical Properties**: ACID compliance, atomicity, consistency

5. **Failure Scenarios**: Network partitions, participant failures, coordinator failures

6. **Modern Optimizations**: Batching, pipelining, AI-powered optimization

7. **Future Trends**: Saga patterns, blockchain integration, hybrid approaches

### When to Use 2PC:
- **Strong consistency requirements**
- **Financial transactions**
- **Critical data operations**
- **Regulatory compliance scenarios**

### When NOT to Use 2PC:
- **High latency tolerance requirements**
- **Eventual consistency acceptable**
- **High availability over consistency**
- **Large number of participants (>10)**

2PC एक proven protocol है, लेकिन modern distributed systems में इसके alternatives भी available हैं। अगले episode में हम **Three-Phase Commit** देखेंगे जो 2PC की कुछ limitations solve करता है।

---

## References और Further Reading

1. **Academic Papers**:
   - Gray & Lamport: "Consensus on Transaction Commit"
   - Bernstein & Newcomer: "Principles of Transaction Processing"

2. **Production Documentation**:
   - Oracle RAC Administration Guide
   - PostgreSQL XA Documentation
   - MySQL XA Transaction Support

3. **Industry Case Studies**:
   - Banking Transaction Processing
   - UPI System Architecture
   - Cross-border Payment Systems

4. **Modern Alternatives**:
   - Saga Pattern Implementation
   - Event Sourcing Approaches
   - Blockchain-based Consensus

---

*Next Episode: Three-Phase Commit - "तीसरा कदम Safety के लिए"*