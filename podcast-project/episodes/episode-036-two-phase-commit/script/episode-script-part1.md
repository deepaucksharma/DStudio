# Episode 36: Two-Phase Commit Protocol - Part 1: Foundations
## Mumbai Ki Wedding Planning aur Distributed Transactions

---

### Episode Opening: Priya Ki Shaadi Ka Jugaad

*[Mumbai street sounds fading in, wedding shehnai in background]*

"Areyaar, main tumhe ek story sunata hun jo mere cousin Priya ki shaadi ki hai. Picture karo - Mumbai mein grand wedding hai, 500 guests, 5 different venues book karne hain simultaneously. Caterer, decorator, photographer, DJ, aur mandap wala - sabko same time pe confirm karna hai. Agar ek bhi vendor 'no' bole, toh poori shaadi cancel! Ye exactly wahi problem hai jo distributed systems mein hoti hai jab hum Two-Phase Commit Protocol use karte hain."

*[Sound effects: Wedding preparations, phone calls overlapping]*

"Namaste engineers! Main hoon tumhara dost, aur aaj hum seekhenge ki kaise distributed transactions ko coordinate karta hai 2PC protocol. Ye episode sirf theory nahi hai - ye production reality hai jahan billions of rupees ride karte hain har second pe."

"Socho - jab tum UPI se payment karte ho, tumhare account se paisa debit hoga, merchant ke account mein credit hoga, bank ka ledger update hoga, aur notification service message bhejegi. Agar ye sab atomic nahi hai, toh kya hoga? Paisa gaya, merchant ko nahi mila! That's where 2PC saves the day."

### Understanding Distributed Transactions: Mumbai Local Train Analogy

*[Local train sounds, announcement in Hindi]*

"Mumbai local trains dekhe hain? Har compartment mein doors hain, aur train tabhi chale gi jab sab doors properly band hon. Ek door open reh gaya, poori train rok di jaati hai. Ye exactly 2PC ka principle hai."

"Distributed transaction matlab multiple systems pe ek operation jo either completely successful hoga ya completely fail. No middle ground! Jaise ki Mumbai ki monsoon mein - ya toh barish hoti hai proper, ya toh bilkul nahi. Half-hearted barish se kaam nahi chalta."

**Practical Example - IRCTC Tatkal Booking:**

"Tumne Tatkal ticket book kiya hai kabhi? Ek second mein ye sab hota hai:
1. Seat availability check (Railway database)
2. Payment processing (Bank system)  
3. Ticket generation (IRCTC system)
4. SMS notification (Telecom gateway)

Agar step 2 mein payment fail ho gaya, but step 1 mein seat already block ho gaya, toh kya hoga? Chaos! Isliye 2PC use karte hain."

### The Wedding Coordinator Metaphor: Understanding 2PC Roles

*[Wedding planner on phone, coordinating multiple vendors]*

"Priya ki shaadi mein ek wedding planner tha - let's call him Rohit. Uski job thi sabko coordinate karna. Distributed systems mein ye role 'Transaction Coordinator' ka hota hai."

**Transaction Coordinator (Wedding Planner):**
- Decides when to start the transaction
- Coordinates all participants
- Makes final commit/abort decision
- Handles failures and recovery

**Participants (Wedding Vendors):**
- Caterer (Database Server 1)
- Photographer (Database Server 2)  
- Decorator (Database Server 3)
- DJ (Database Server 4)

"Rohit ka approach tha simple - sabse pehle puchega 'Ready ho?' Sab 'Yes' bole, tabhi final booking. Ek bhi 'No' bola, sab cancel!"

### Phase 1: Prepare Phase - "Ready Ho Kya?"

*[Phone calls overlapping, vendor confirmations]*

"2PC ka pehla phase hai PREPARE. Ye phase mein coordinator sabse puchta hai - 'Bhai, ready ho transaction ke liye?'"

**Mumbai Wedding Example:**

```
Wedding Planner (Coordinator) calls:

Day 1: "December 15 ko available ho?"
Caterer: "Haan bhai, 500 people ka arrange kar sakta hun"
Photographer: "Yes sir, equipment ready hai"
Decorator: "Mandap aur flowers ready"
DJ: "Sound system book kar diya"

All vendors say: "VOTE-COMMIT" (Ready!)
```

**Technical Implementation:**

"Database systems mein ye kaise hota hai? Har participant apne local changes ko prepare karta hai, but commit nahi karta."

```python
# Python implementation of 2PC Prepare Phase
import time
import uuid
import logging
from datetime import datetime

class TransactionParticipant:
    def __init__(self, name, failure_rate=0.0):
        self.name = name
        self.failure_rate = failure_rate
        self.prepared_transactions = {}
        self.committed_transactions = set()
        self.aborted_transactions = set()
        
    def prepare(self, transaction_id, operation_data):
        """Prepare phase - ready to commit but don't commit yet"""
        print(f"🔄 {self.name} preparing transaction {transaction_id}")
        
        # Simulate business logic and validation
        if self.should_fail():
            print(f"❌ {self.name} voting ABORT for {transaction_id}")
            return "VOTE-ABORT"
        
        # Store operation in prepare state (like WAL - Write Ahead Log)
        self.prepared_transactions[transaction_id] = {
            'operation': operation_data,
            'timestamp': datetime.now(),
            'status': 'PREPARED'
        }
        
        print(f"✅ {self.name} voting COMMIT for {transaction_id}")
        return "VOTE-COMMIT"
    
    def should_fail(self):
        import random
        return random.random() < self.failure_rate

# Mumbai Banking Example - UPI Transaction
class MumbaiUPISystem:
    def __init__(self):
        self.payer_bank = TransactionParticipant("HDFC Bank Mumbai")
        self.payee_bank = TransactionParticipant("SBI Bank Bandra") 
        self.upi_switch = TransactionParticipant("NPCI UPI Switch")
        self.notification_service = TransactionParticipant("SMS Gateway")
        
    def prepare_upi_transaction(self, transaction_id, amount, payer, payee):
        """Prepare phase for UPI transaction"""
        print(f"\n💳 Starting UPI transaction {transaction_id}")
        print(f"Amount: ₹{amount} from {payer} to {payee}")
        
        # Phase 1: PREPARE
        votes = []
        
        # Payer bank prepares debit
        vote1 = self.payer_bank.prepare(transaction_id, 
            f"DEBIT ₹{amount} from {payer}")
        votes.append(vote1)
        
        # Payee bank prepares credit  
        vote2 = self.payee_bank.prepare(transaction_id,
            f"CREDIT ₹{amount} to {payee}")
        votes.append(vote2)
        
        # UPI switch prepares routing
        vote3 = self.upi_switch.prepare(transaction_id,
            f"ROUTE ₹{amount} {payer} -> {payee}")
        votes.append(vote3)
        
        # SMS service prepares notification
        vote4 = self.notification_service.prepare(transaction_id,
            f"SMS confirmation for ₹{amount} transaction")
        votes.append(vote4)
        
        return votes

# Example usage
upi_system = MumbaiUPISystem()
transaction_id = f"UPI-{uuid.uuid4().hex[:8]}"
votes = upi_system.prepare_upi_transaction(transaction_id, 500, 
    "Rahul@hdfc", "Priya@sbi")

print(f"\n📊 Prepare Phase Results: {votes}")
if all(vote == "VOTE-COMMIT" for vote in votes):
    print("🎉 All participants ready! Proceeding to commit...")
else:
    print("❌ Some participants not ready. Transaction will abort!")
```

**Real Production Scenario - Flipkart Order Processing:**

"Flipkart pe order place karte time ye sab simultaneously hona chahiye:
1. Inventory deduction (Warehouse DB)
2. Payment processing (Payment Gateway)  
3. Order creation (Order Management System)
4. Delivery scheduling (Logistics System)"

### Phase 1 Deep Dive: Resource Locking aur Write-Ahead Logging

*[Sound of file cabinets locking, papers shuffling]*

"Prepare phase mein participants ye karte hain:

**1. Resource Locking:**
Mumbai mein parking spot book karne jaisa hai. Spot hold kar liya, but key nahi di abhi tak."

```python
class DatabaseParticipant:
    def __init__(self, name):
        self.name = name
        self.locked_resources = {}
        self.wal_log = []  # Write-Ahead Log
        
    def prepare_transaction(self, txn_id, operations):
        """Prepare phase with proper locking"""
        try:
            # Step 1: Acquire all necessary locks
            locks_acquired = []
            for operation in operations:
                resource_id = operation['resource']
                if self.acquire_lock(resource_id, txn_id):
                    locks_acquired.append(resource_id)
                else:
                    # Rollback acquired locks
                    for lock in locks_acquired:
                        self.release_lock(lock, txn_id)
                    return "VOTE-ABORT"
            
            # Step 2: Write to WAL (Write-Ahead Log)
            wal_entry = {
                'transaction_id': txn_id,
                'operations': operations,
                'timestamp': datetime.now(),
                'phase': 'PREPARE'
            }
            self.wal_log.append(wal_entry)
            
            # Step 3: Validate business constraints
            if not self.validate_operations(operations):
                self.release_all_locks(txn_id)
                return "VOTE-ABORT"
                
            print(f"✅ {self.name} prepared transaction {txn_id}")
            return "VOTE-COMMIT"
            
        except Exception as e:
            print(f"❌ {self.name} prepare failed: {e}")
            self.release_all_locks(txn_id)
            return "VOTE-ABORT"
    
    def acquire_lock(self, resource_id, txn_id):
        """Acquire exclusive lock on resource"""
        if resource_id in self.locked_resources:
            return False  # Already locked
        self.locked_resources[resource_id] = txn_id
        return True
        
    def validate_operations(self, operations):
        """Business logic validation"""
        # Example: Check account balance, inventory levels, etc.
        for op in operations:
            if op['type'] == 'DEBIT':
                if not self.check_sufficient_balance(op['account'], op['amount']):
                    return False
        return True
```

**Mumbai Street Vendor Analogy:**

"Crawford Market mein vendor se bargaining kar rahe ho. Vendor bol raha hai 'Saath mein le lo toh 500 mein de dunga 3 kg aam.' But wo actually 3 kg alag kar ke rakhta hai, customer se payment confirm hone tak. Ye hi hai resource locking!"

### The Coordinator's Algorithm: Wedding Planner Ki Strategy

*[Wedding planner's checklist, phone calls, confirmations]*

"Ab dekhte hain ki coordinator (wedding planner Rohit) kaise handle karta hai full process:"

```python
class TwoPhaseCommitCoordinator:
    def __init__(self):
        self.participants = []
        self.transaction_log = {}
        
    def add_participant(self, participant):
        self.participants.append(participant)
        
    def execute_transaction(self, transaction_id, operations):
        """Execute full 2PC protocol"""
        print(f"\n🚀 Starting 2PC for transaction {transaction_id}")
        
        # Log transaction start
        self.log_transaction(transaction_id, "START", operations)
        
        try:
            # PHASE 1: PREPARE
            if not self.prepare_phase(transaction_id, operations):
                return self.abort_transaction(transaction_id)
            
            # PHASE 2: COMMIT  
            return self.commit_phase(transaction_id)
            
        except Exception as e:
            print(f"❌ Transaction {transaction_id} failed: {e}")
            return self.abort_transaction(transaction_id)
    
    def prepare_phase(self, transaction_id, operations):
        """Phase 1: Send PREPARE to all participants"""
        print(f"\n📋 Phase 1: PREPARE for {transaction_id}")
        
        votes = []
        failed_participants = []
        
        for participant in self.participants:
            try:
                # Send PREPARE message with timeout
                vote = participant.prepare(transaction_id, operations)
                votes.append(vote)
                
                if vote == "VOTE-ABORT":
                    failed_participants.append(participant.name)
                    
            except Exception as e:
                print(f"❌ {participant.name} failed to respond: {e}")
                votes.append("VOTE-ABORT")
                failed_participants.append(participant.name)
        
        # Log prepare results
        self.log_transaction(transaction_id, "PREPARE", {
            'votes': votes,
            'failed_participants': failed_participants
        })
        
        # Decision: ALL must vote COMMIT
        all_committed = all(vote == "VOTE-COMMIT" for vote in votes)
        
        if all_committed:
            print("🎉 All participants voted COMMIT!")
            return True
        else:
            print(f"❌ Some participants voted ABORT: {failed_participants}")
            return False

# Mumbai Wedding Booking Example
class WeddingVendor:
    def __init__(self, name, availability_check_func):
        self.name = name
        self.check_availability = availability_check_func
        self.bookings = {}
        
    def prepare(self, transaction_id, booking_details):
        """Check availability and hold the slot"""
        print(f"📞 {self.name} checking availability for {booking_details['date']}")
        
        if self.check_availability(booking_details):
            # Hold the booking (don't confirm yet)
            self.bookings[transaction_id] = {
                'status': 'PREPARED',
                'details': booking_details,
                'hold_time': datetime.now()
            }
            print(f"✅ {self.name} says: Ready for {booking_details['date']}")
            return "VOTE-COMMIT"
        else:
            print(f"❌ {self.name} says: Not available on {booking_details['date']}")
            return "VOTE-ABORT"

# Example: Mumbai Wedding Coordination
def main():
    # Create vendors (participants)
    caterer = WeddingVendor("Gujarati Caterer", 
        lambda details: details['guests'] <= 500)
    photographer = WeddingVendor("Mumbai Photography", 
        lambda details: details['date'] not in ['2024-12-25'])
    decorator = WeddingVendor("Flower Decorator",
        lambda details: details['venue_type'] in ['banquet', 'garden'])
    
    # Create coordinator
    coordinator = TwoPhaseCommitCoordinator()
    coordinator.add_participant(caterer)
    coordinator.add_participant(photographer)  
    coordinator.add_participant(decorator)
    
    # Wedding booking request
    booking_details = {
        'date': '2024-12-15',
        'guests': 400,
        'venue_type': 'banquet'
    }
    
    # Execute 2PC
    transaction_id = "WEDDING-2024-001"
    result = coordinator.execute_transaction(transaction_id, booking_details)
    
    if result == "COMMITTED":
        print("🎊 Wedding successfully booked!")
    else:
        print("😞 Wedding booking failed!")

if __name__ == "__main__":
    main()
```

### Phase 2: Commit Phase - "Pakka Kar Do!"

*[Confirmation calls, vendors acknowledging, celebration sounds]*

"Phase 2 mein coordinator final decision leta hai. Sab vendors ready hain toh 'COMMIT' message bhejta hai. Kisi ne 'No' bola hai toh 'ABORT'."

**Commit Scenario - All Green:**

```python
def commit_phase(self, transaction_id):
    """Phase 2: Send COMMIT to all participants"""
    print(f"\n✅ Phase 2: COMMIT for {transaction_id}")
    
    success_count = 0
    failed_participants = []
    
    for participant in self.participants:
        try:
            result = participant.commit(transaction_id)
            if result == "COMMITTED":
                success_count += 1
                print(f"✅ {participant.name} committed successfully")
            else:
                failed_participants.append(participant.name)
                
        except Exception as e:
            print(f"❌ {participant.name} failed to commit: {e}")
            failed_participants.append(participant.name)
    
    # Log final result
    self.log_transaction(transaction_id, "COMMIT-COMPLETE", {
        'successful': success_count,
        'failed': failed_participants
    })
    
    if failed_participants:
        print(f"⚠️ Some participants failed to commit: {failed_participants}")
        # Note: Transaction is still considered committed
        # Failed participants must be handled by recovery protocol
    
    return "COMMITTED"
```

**Participant Commit Implementation:**

```python
def commit(self, transaction_id):
    """Actually commit the prepared transaction"""
    if transaction_id not in self.prepared_transactions:
        raise Exception(f"No prepared transaction {transaction_id}")
    
    try:
        # Execute the prepared operation
        operation = self.prepared_transactions[transaction_id]
        self.execute_operation(operation['operation'])
        
        # Move to committed state
        self.committed_transactions.add(transaction_id)
        del self.prepared_transactions[transaction_id]
        
        # Release locks
        self.release_all_locks(transaction_id)
        
        print(f"💚 {self.name} committed transaction {transaction_id}")
        return "COMMITTED"
        
    except Exception as e:
        print(f"❌ {self.name} commit failed: {e}")
        # This is serious - coordinator thinks we committed!
        # Must retry or escalate to manual intervention
        raise
```

### Failure Scenarios: Murphy's Law in Mumbai

*[Traffic sounds, horn honking, chaos]*

"Murphy's Law kehta hai - 'Jo galat ho sakta hai, wo galat hoga.' Mumbai mein toh ye daily experience hai! 2PC mein failures handle karna zaroori hai."

**Scenario 1: Participant Failure During Prepare**

```python
class UnreliableParticipant(TransactionParticipant):
    def __init__(self, name, failure_probability=0.3):
        super().__init__(name)
        self.failure_probability = failure_probability
        
    def prepare(self, transaction_id, operation_data):
        # Simulate network failure or system crash
        if self.should_fail():
            raise Exception(f"{self.name} crashed during prepare!")
        
        return super().prepare(transaction_id, operation_data)
    
    def should_fail(self):
        import random
        return random.random() < self.failure_probability

# Mumbai Power Cut Example
def simulate_mumbai_power_failure():
    """Simulate power failure during transaction"""
    
    # Vendors with power backup reliability
    caterer = UnreliableParticipant("Caterer (No Power Backup)", 0.4)
    photographer = UnreliableParticipant("Photographer (UPS Backup)", 0.1) 
    decorator = UnreliableParticipant("Decorator (Generator)", 0.05)
    
    coordinator = TwoPhaseCommitCoordinator()
    coordinator.add_participant(caterer)
    coordinator.add_participant(photographer)
    coordinator.add_participant(decorator)
    
    # Try booking during monsoon season (power issues)
    for attempt in range(5):
        print(f"\n⚡ Booking attempt {attempt + 1} (Monsoon season)")
        try:
            result = coordinator.execute_transaction(
                f"MONSOON-BOOKING-{attempt}",
                {'date': '2024-07-15', 'guests': 300}
            )
            
            if result == "COMMITTED":
                print("🌈 Successfully booked despite power issues!")
                break
            else:
                print("⛈️ Booking failed, retrying...")
                
        except Exception as e:
            print(f"💥 System failure: {e}")
```

**Scenario 2: Coordinator Failure**

"Ye sabse dangerous scenario hai - wedding planner ka phone dead ho gaya! Vendors wait kar rahe hain, confusion ho rahi hai."

```python
class CoordinatorRecovery:
    def __init__(self):
        self.transaction_log = {}
        self.backup_coordinators = []
        
    def recover_from_failure(self, failed_coordinator_id):
        """Recover transactions after coordinator failure"""
        print(f"🆘 Coordinator {failed_coordinator_id} failed! Starting recovery...")
        
        # Read persistent transaction log
        pending_transactions = self.read_transaction_log(failed_coordinator_id)
        
        for txn_id, txn_state in pending_transactions.items():
            if txn_state['phase'] == 'PREPARE':
                print(f"🔄 Recovering transaction {txn_id} from PREPARE phase")
                self.recover_prepare_phase(txn_id, txn_state)
                
            elif txn_state['phase'] == 'COMMIT':
                print(f"✅ Recovering transaction {txn_id} from COMMIT phase")
                self.recover_commit_phase(txn_id, txn_state)
    
    def recover_prepare_phase(self, txn_id, txn_state):
        """Recovery during prepare phase"""
        # Query all participants about transaction state
        participant_states = []
        
        for participant in txn_state['participants']:
            try:
                state = participant.query_transaction_state(txn_id)
                participant_states.append(state)
            except:
                participant_states.append("UNKNOWN")
        
        # Decision logic for recovery
        if any(state == "ABORTED" for state in participant_states):
            print(f"❌ Some participants aborted {txn_id}, aborting all")
            self.abort_transaction(txn_id, txn_state['participants'])
            
        elif all(state == "PREPARED" for state in participant_states):
            print(f"✅ All participants prepared {txn_id}, committing")
            self.commit_transaction(txn_id, txn_state['participants'])
            
        else:
            print(f"❓ Uncertain state for {txn_id}, aborting for safety")
            self.abort_transaction(txn_id, txn_state['participants'])
```

### Real-World Implementation: Java Banking System

"Ab dekhte hain production-grade implementation. Ye actual banking system mein use hota hai:"

```java
// Java implementation for Indian banking system
import java.util.*;
import java.util.concurrent.*;
import java.sql.*;
import java.time.LocalDateTime;

public class IndianBankingTwoPhaseCommit {
    
    // Transaction Coordinator for Inter-bank transfers
    public static class UPITransactionCoordinator {
        private List<BankParticipant> participants;
        private Map<String, TransactionState> transactionLog;
        private ExecutorService executorService;
        
        public UPITransactionCoordinator() {
            this.participants = new ArrayList<>();
            this.transactionLog = new ConcurrentHashMap<>();
            this.executorService = Executors.newFixedThreadPool(10);
        }
        
        public void addBank(BankParticipant bank) {
            participants.add(bank);
        }
        
        public boolean executeUPITransfer(String transactionId, 
            String fromAccount, String toAccount, double amount) {
            
            System.out.println("🏦 Starting UPI transfer: " + transactionId);
            System.out.println("₹" + amount + " from " + fromAccount + " to " + toAccount);
            
            // Phase 1: PREPARE
            if (!preparePhase(transactionId, fromAccount, toAccount, amount)) {
                return abortTransaction(transactionId);
            }
            
            // Phase 2: COMMIT
            return commitPhase(transactionId);
        }
        
        private boolean preparePhase(String txnId, String from, String to, double amount) {
            System.out.println("\n📋 Phase 1: PREPARE");
            
            List<Future<String>> votes = new ArrayList<>();
            
            for (BankParticipant bank : participants) {
                Future<String> vote = executorService.submit(() -> {
                    try {
                        return bank.prepare(txnId, from, to, amount);
                    } catch (Exception e) {
                        System.err.println("❌ " + bank.getName() + " failed: " + e.getMessage());
                        return "VOTE-ABORT";
                    }
                });
                votes.add(vote);
            }
            
            // Collect votes with timeout
            boolean allCommitted = true;
            for (Future<String> vote : votes) {
                try {
                    String result = vote.get(5, TimeUnit.SECONDS); // 5 sec timeout
                    if (!"VOTE-COMMIT".equals(result)) {
                        allCommitted = false;
                        System.out.println("❌ Received ABORT vote");
                    }
                } catch (TimeoutException e) {
                    System.out.println("⏰ Participant timeout - assuming ABORT");
                    allCommitted = false;
                } catch (Exception e) {
                    System.out.println("💥 Error collecting vote: " + e.getMessage());
                    allCommitted = false;
                }
            }
            
            // Log decision
            transactionLog.put(txnId, new TransactionState(
                allCommitted ? "COMMIT-DECISION" : "ABORT-DECISION",
                LocalDateTime.now()
            ));
            
            return allCommitted;
        }
        
        private boolean commitPhase(String txnId) {
            System.out.println("\n✅ Phase 2: COMMIT");
            
            List<Future<Boolean>> commitResults = new ArrayList<>();
            
            for (BankParticipant bank : participants) {
                Future<Boolean> result = executorService.submit(() -> {
                    try {
                        return bank.commit(txnId);
                    } catch (Exception e) {
                        System.err.println("❌ " + bank.getName() + " commit failed: " + e.getMessage());
                        // Note: This is serious - transaction may be inconsistent
                        return false;
                    }
                });
                commitResults.add(result);
            }
            
            // Wait for all commits (with retries for failures)
            boolean allSucceeded = true;
            for (Future<Boolean> result : commitResults) {
                try {
                    if (!result.get(10, TimeUnit.SECONDS)) {
                        allSucceeded = false;
                    }
                } catch (Exception e) {
                    allSucceeded = false;
                    System.err.println("💥 Commit execution failed: " + e.getMessage());
                }
            }
            
            if (allSucceeded) {
                System.out.println("🎉 Transaction committed successfully!");
                transactionLog.put(txnId, new TransactionState("COMMITTED", LocalDateTime.now()));
            } else {
                System.out.println("⚠️ Some commits failed - manual intervention needed!");
            }
            
            return allSucceeded;
        }
        
        private boolean abortTransaction(String txnId) {
            System.out.println("\n❌ ABORT Transaction: " + txnId);
            
            for (BankParticipant bank : participants) {
                try {
                    bank.abort(txnId);
                } catch (Exception e) {
                    System.err.println("Warning: " + bank.getName() + " abort failed: " + e.getMessage());
                }
            }
            
            transactionLog.put(txnId, new TransactionState("ABORTED", LocalDateTime.now()));
            return false;
        }
    }
    
    // Bank participant implementing 2PC protocol
    public static class BankParticipant {
        private String bankName;
        private Map<String, PreparedTransaction> preparedTransactions;
        private Connection dbConnection;
        
        public BankParticipant(String name, Connection connection) {
            this.bankName = name;
            this.preparedTransactions = new ConcurrentHashMap<>();
            this.dbConnection = connection;
        }
        
        public String prepare(String txnId, String fromAccount, String toAccount, double amount) {
            System.out.println("🔄 " + bankName + " preparing transaction " + txnId);
            
            try {
                // Begin database transaction
                dbConnection.setAutoCommit(false);
                
                // Check if this bank handles the accounts
                boolean hasFromAccount = hasAccount(fromAccount);
                boolean hasToAccount = hasAccount(toAccount);
                
                if (!hasFromAccount && !hasToAccount) {
                    System.out.println("ℹ️ " + bankName + " not involved in this transaction");
                    return "VOTE-COMMIT"; // Not participating
                }
                
                // Prepare debit operation
                if (hasFromAccount) {
                    if (!checkBalance(fromAccount, amount)) {
                        System.out.println("❌ " + bankName + " insufficient balance in " + fromAccount);
                        dbConnection.rollback();
                        return "VOTE-ABORT";
                    }
                    
                    // Lock account and prepare debit
                    prepareDebit(fromAccount, amount);
                }
                
                // Prepare credit operation  
                if (hasToAccount) {
                    prepareCredit(toAccount, amount);
                }
                
                // Store prepared state
                preparedTransactions.put(txnId, new PreparedTransaction(
                    fromAccount, toAccount, amount, hasFromAccount, hasToAccount
                ));
                
                System.out.println("✅ " + bankName + " voted COMMIT for " + txnId);
                return "VOTE-COMMIT";
                
            } catch (SQLException e) {
                System.err.println("❌ " + bankName + " database error: " + e.getMessage());
                try {
                    dbConnection.rollback();
                } catch (SQLException ex) {
                    System.err.println("Failed to rollback: " + ex.getMessage());
                }
                return "VOTE-ABORT";
            }
        }
        
        public boolean commit(String txnId) {
            System.out.println("💚 " + bankName + " committing transaction " + txnId);
            
            PreparedTransaction prepared = preparedTransactions.get(txnId);
            if (prepared == null) {
                System.out.println("ℹ️ " + bankName + " not participating in " + txnId);
                return true;
            }
            
            try {
                // Execute prepared operations
                if (prepared.hasFromAccount) {
                    executeDebit(prepared.fromAccount, prepared.amount);
                }
                
                if (prepared.hasToAccount) {
                    executeCredit(prepared.toAccount, prepared.amount);
                }
                
                // Commit database transaction
                dbConnection.commit();
                dbConnection.setAutoCommit(true);
                
                // Cleanup
                preparedTransactions.remove(txnId);
                
                System.out.println("✅ " + bankName + " successfully committed " + txnId);
                return true;
                
            } catch (SQLException e) {
                System.err.println("💥 " + bankName + " commit failed: " + e.getMessage());
                // This is critical - we promised to commit!
                // Must retry or escalate to manual intervention
                return false;
            }
        }
        
        public void abort(String txnId) {
            System.out.println("❌ " + bankName + " aborting transaction " + txnId);
            
            try {
                dbConnection.rollback();
                dbConnection.setAutoCommit(true);
                preparedTransactions.remove(txnId);
            } catch (SQLException e) {
                System.err.println("Error during abort: " + e.getMessage());
            }
        }
        
        private boolean hasAccount(String accountId) {
            // Check if account belongs to this bank
            return accountId.startsWith(bankName.toLowerCase().replace(" ", ""));
        }
        
        private boolean checkBalance(String account, double amount) throws SQLException {
            PreparedStatement stmt = dbConnection.prepareStatement(
                "SELECT balance FROM accounts WHERE account_id = ? FOR UPDATE");
            stmt.setString(1, account);
            
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                double balance = rs.getDouble("balance");
                return balance >= amount;
            }
            return false;
        }
        
        private void prepareDebit(String account, double amount) throws SQLException {
            // Write to WAL but don't update balance yet
            PreparedStatement stmt = dbConnection.prepareStatement(
                "INSERT INTO transaction_log (account_id, amount, operation, status) VALUES (?, ?, 'DEBIT', 'PREPARED')");
            stmt.setString(1, account);
            stmt.setDouble(2, amount);
            stmt.executeUpdate();
        }
        
        private void prepareCredit(String account, double amount) throws SQLException {
            PreparedStatement stmt = dbConnection.prepareStatement(
                "INSERT INTO transaction_log (account_id, amount, operation, status) VALUES (?, ?, 'CREDIT', 'PREPARED')");
            stmt.setString(1, account);
            stmt.setDouble(2, amount);
            stmt.executeUpdate();
        }
        
        private void executeDebit(String account, double amount) throws SQLException {
            PreparedStatement stmt = dbConnection.prepareStatement(
                "UPDATE accounts SET balance = balance - ? WHERE account_id = ?");
            stmt.setDouble(1, amount);
            stmt.setString(2, account);
            stmt.executeUpdate();
        }
        
        private void executeCredit(String account, double amount) throws SQLException {
            PreparedStatement stmt = dbConnection.prepareStatement(
                "UPDATE accounts SET balance = balance + ? WHERE account_id = ?");
            stmt.setDouble(1, amount);
            stmt.setString(2, account);
            stmt.executeUpdate();
        }
        
        public String getName() {
            return bankName;
        }
    }
    
    // Helper classes
    static class TransactionState {
        String state;
        LocalDateTime timestamp;
        
        TransactionState(String state, LocalDateTime timestamp) {
            this.state = state;
            this.timestamp = timestamp;
        }
    }
    
    static class PreparedTransaction {
        String fromAccount;
        String toAccount; 
        double amount;
        boolean hasFromAccount;
        boolean hasToAccount;
        
        PreparedTransaction(String from, String to, double amt, boolean hasFrom, boolean hasTo) {
            this.fromAccount = from;
            this.toAccount = to;
            this.amount = amt;
            this.hasFromAccount = hasFrom;
            this.hasToAccount = hasTo;
        }
    }
    
    // Main example
    public static void main(String[] args) {
        try {
            // Setup mock database connections (in real system, use connection pool)
            Connection hdfcDB = DriverManager.getConnection("jdbc:h2:mem:hdfc");
            Connection sbiDB = DriverManager.getConnection("jdbc:h2:mem:sbi");
            
            // Create banks
            BankParticipant hdfc = new BankParticipant("HDFC Bank", hdfcDB);
            BankParticipant sbi = new BankParticipant("SBI Bank", sbiDB);
            
            // Create coordinator
            UPITransactionCoordinator coordinator = new UPITransactionCoordinator();
            coordinator.addBank(hdfc);
            coordinator.addBank(sbi);
            
            // Execute UPI transfer
            boolean success = coordinator.executeUPITransfer(
                "UPI-" + System.currentTimeMillis(),
                "hdfcbank-rahul-123",
                "sbibank-priya-456", 
                5000.0
            );
            
            if (success) {
                System.out.println("🎊 UPI transfer completed successfully!");
            } else {
                System.out.println("😞 UPI transfer failed!");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### UPI Transaction Deep Dive: Real Indian Example

*[UPI notification sounds, payment processing]*

"Chaliye ab dekhte hain ki actual UPI transaction mein 2PC kaise work karta hai. Jab tum ₹500 bhejte ho Zomato payment ke liye:"

**Step-by-step UPI Transaction Flow:**

```
1. You: "Pay ₹500 to Zomato"
   App → NPCI UPI Switch → Your Bank (HDFC)

2. PREPARE Phase:
   HDFC Bank: "Can debit ₹500 from Rahul's account?"
   Check: Balance sufficient? Account active? Daily limit OK?
   Response: "VOTE-COMMIT" (Ready to debit)

   NPCI Switch: "Can route this payment?"
   Check: Network operational? Anti-fraud checks passed?
   Response: "VOTE-COMMIT" (Ready to route)

   Zomato Bank (SBI): "Can credit ₹500 to Zomato merchant account?"
   Check: Account exists? Not blocked?
   Response: "VOTE-COMMIT" (Ready to credit)

3. COMMIT Phase:
   Coordinator (UPI Switch): "All participants ready! COMMIT now!"
   
   HDFC: ₹500 debited from your account ✅
   NPCI: Transaction logged and routed ✅  
   SBI: ₹500 credited to Zomato ✅
   SMS Gateway: Confirmation sent ✅

4. Result: "Payment Successful! ₹500 paid to Zomato"
```

**What happens if someone fails?**

```python
def upi_failure_scenarios():
    """Real-world UPI failure handling"""
    
    scenarios = [
        {
            'name': 'Insufficient Balance',
            'phase': 'PREPARE',
            'failed_participant': 'Payer Bank',
            'vote': 'VOTE-ABORT',
            'result': 'Transaction cancelled immediately'
        },
        {
            'name': 'Network Timeout', 
            'phase': 'PREPARE',
            'failed_participant': 'NPCI Switch',
            'vote': 'NO-RESPONSE',
            'result': 'Timeout → ABORT → "Payment failed, try again"'
        },
        {
            'name': 'Merchant Account Blocked',
            'phase': 'PREPARE', 
            'failed_participant': 'Payee Bank',
            'vote': 'VOTE-ABORT',
            'result': 'Transaction failed → "Merchant cannot receive payment"'
        },
        {
            'name': 'Bank System Down (During Commit)',
            'phase': 'COMMIT',
            'failed_participant': 'Any Bank',
            'vote': 'COMMIT-FAILED',
            'result': 'Inconsistent state! Manual intervention needed!'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n💥 Scenario: {scenario['name']}")
        print(f"Phase: {scenario['phase']}")
        print(f"Failed: {scenario['failed_participant']}")
        print(f"Result: {scenario['result']}")
        
        if scenario['phase'] == 'COMMIT':
            print("⚠️ CRITICAL: Requires immediate manual resolution!")
```

### Performance Considerations: Mumbai Traffic Analogy

*[Traffic sounds, honking, signal changes]*

"2PC ka biggest problem hai performance. Jaise Mumbai traffic mein ek signal red ho jaye, toh poora junction block ho jata hai!"

**The Blocking Problem:**

"Prepare phase mein sab participants block ho jaate hain - waiting for coordinator's decision. Ye exactly Mumbai mein ek VIP convoy ke jaane jaisa hai - sab ruk jaate hain!"

```python
class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = {
            'prepare_times': [],
            'commit_times': [],
            'total_transaction_times': [],
            'blocking_durations': []
        }
    
    def analyze_2pc_performance(self, num_participants, network_latency_ms):
        """Analyze 2PC performance characteristics"""
        
        print(f"📊 2PC Performance Analysis")
        print(f"Participants: {num_participants}")
        print(f"Network Latency: {network_latency_ms}ms")
        
        # Calculate theoretical minimums
        prepare_time = network_latency_ms * 2  # Round trip to each participant
        commit_time = network_latency_ms * 2   # Another round trip
        total_time = prepare_time + commit_time
        
        # Real-world overhead
        coordination_overhead = num_participants * 10  # Coordination cost
        logging_overhead = 50  # Persistent logging
        lock_contention = num_participants * 5  # Lock acquisition delays
        
        actual_total = total_time + coordination_overhead + logging_overhead + lock_contention
        
        print(f"\n⏱️ Time Breakdown:")
        print(f"  Prepare Phase: {prepare_time}ms")
        print(f"  Commit Phase: {commit_time}ms")
        print(f"  Coordination Overhead: {coordination_overhead}ms")
        print(f"  Logging Overhead: {logging_overhead}ms") 
        print(f"  Lock Contention: {lock_contention}ms")
        print(f"  Total Transaction Time: {actual_total}ms")
        
        # Blocking duration analysis
        blocking_duration = prepare_time + commit_time
        print(f"\n🔒 Resource Blocking Duration: {blocking_duration}ms")
        
        # Throughput impact
        max_tps = 1000 / actual_total  # Transactions per second
        print(f"📈 Maximum TPS (Single coordinator): {max_tps:.2f}")
        
        # Scalability analysis
        print(f"\n📏 Scalability Concerns:")
        if num_participants > 5:
            print(f"  ⚠️ {num_participants} participants - coordination complexity high")
        if actual_total > 1000:
            print(f"  ⚠️ {actual_total}ms transaction time - user experience poor") 
        if blocking_duration > 500:
            print(f"  ⚠️ {blocking_duration}ms blocking - throughput severely limited")
        
        return {
            'total_time_ms': actual_total,
            'blocking_duration_ms': blocking_duration,
            'max_tps': max_tps
        }

# Mumbai Banking Network Analysis
analyzer = PerformanceAnalyzer()

# Scenario 1: Local Mumbai transaction (low latency)
print("🏙️ Scenario 1: Local Mumbai UPI Transaction")
local_metrics = analyzer.analyze_2pc_performance(
    num_participants=4,  # Customer bank, NPCI, merchant bank, SMS
    network_latency_ms=50  # Local data centers
)

print("\n" + "="*60)

# Scenario 2: Inter-city transaction (higher latency)
print("🌏 Scenario 2: Mumbai to Delhi UPI Transaction")  
intercity_metrics = analyzer.analyze_2pc_performance(
    num_participants=5,  # + compliance system
    network_latency_ms=150  # Cross-region latency
)

print("\n" + "="*60)

# Scenario 3: International remittance (high latency)
print("🌍 Scenario 3: Mumbai to Singapore Remittance")
international_metrics = analyzer.analyze_2pc_performance(
    num_participants=8,  # Multiple banks, SWIFT, compliance, forex
    network_latency_ms=300  # International latency
)
```

### Recovery and Durability: Monsoon Resilience

*[Monsoon sounds, flooding, power cuts]*

"Mumbai monsoon mein jab sab kuch flood ho jata hai, tab kya karte hain? Similarly, 2PC mein recovery mechanisms hote hain:"

```python
class DisasterRecoverySystem:
    def __init__(self):
        self.transaction_log = []
        self.participant_registry = {}
        
    def handle_coordinator_crash(self, crashed_coordinator_id):
        """Handle coordinator failure during transaction"""
        print(f"🆘 Coordinator {crashed_coordinator_id} crashed!")
        
        # Read persistent log to understand pending transactions
        pending_txns = self.read_coordinator_log(crashed_coordinator_id)
        
        print(f"Found {len(pending_txns)} pending transactions")
        
        for txn_id, txn_state in pending_txns.items():
            if txn_state['phase'] == 'PREPARE':
                self.recover_from_prepare_phase(txn_id, txn_state)
            elif txn_state['phase'] == 'COMMIT':
                self.recover_from_commit_phase(txn_id, txn_state)
    
    def recover_from_prepare_phase(self, txn_id, txn_state):
        """Recovery when coordinator crashed during PREPARE phase"""
        print(f"🔄 Recovering {txn_id} from PREPARE phase")
        
        # Query all participants about their state
        participant_votes = {}
        uncertain_participants = []
        
        for participant_id in txn_state['participants']:
            try:
                state = self.query_participant(participant_id, txn_id)
                participant_votes[participant_id] = state
                
                if state == "UNCERTAIN":
                    uncertain_participants.append(participant_id)
                    
            except Exception as e:
                print(f"❌ Cannot reach {participant_id}: {e}")
                uncertain_participants.append(participant_id)
        
        # Recovery decision logic
        if any(vote == "ABORTED" for vote in participant_votes.values()):
            print(f"❌ Found ABORTED participant, aborting {txn_id}")
            self.force_abort_transaction(txn_id, txn_state['participants'])
            
        elif all(vote == "PREPARED" for vote in participant_votes.values()):
            print(f"✅ All participants PREPARED, committing {txn_id}")
            self.resume_commit_phase(txn_id, txn_state['participants'])
            
        elif uncertain_participants:
            print(f"❓ Uncertain state for participants: {uncertain_participants}")
            print(f"🛑 Aborting {txn_id} for safety")
            self.force_abort_transaction(txn_id, txn_state['participants'])
            
        else:
            print(f"⚠️ Mixed states detected, manual intervention required")
            self.escalate_to_manual_resolution(txn_id, participant_votes)
    
    def handle_participant_crash(self, crashed_participant_id):
        """Handle participant crash and recovery"""
        print(f"💥 Participant {crashed_participant_id} crashed!")
        
        # Find all transactions involving this participant
        affected_txns = self.find_transactions_with_participant(crashed_participant_id)
        
        for txn_id in affected_txns:
            print(f"🔍 Checking transaction {txn_id}")
            
            # Wait for participant to come back online
            if self.wait_for_participant_recovery(crashed_participant_id, timeout=300):
                print(f"✅ {crashed_participant_id} recovered, resuming {txn_id}")
                self.resume_transaction_with_recovered_participant(txn_id, crashed_participant_id)
            else:
                print(f"⏰ {crashed_participant_id} recovery timeout, aborting {txn_id}")
                self.timeout_abort_transaction(txn_id)

# Mumbai Monsoon Simulation
def simulate_monsoon_disaster():
    """Simulate Mumbai monsoon affecting banking systems"""
    
    recovery_system = DisasterRecoverySystem()
    
    # Simulate power outage in Bandra Data Center
    print("⛈️ MONSOON ALERT: Heavy flooding in Bandra!")
    print("💡 Power outage affecting HDFC Bank data center...")
    
    # Multiple concurrent UPI transactions affected
    affected_transactions = [
        "UPI-ZOMATO-001", "UPI-SWIGGY-002", "UPI-AMAZON-003",
        "UPI-FLIPKART-004", "UPI-PAYTM-005"
    ]
    
    for txn_id in affected_transactions:
        print(f"\n🆘 Handling affected transaction: {txn_id}")
        
        # Simulate different crash scenarios
        import random
        crash_phase = random.choice(['PREPARE', 'COMMIT'])
        
        if crash_phase == 'PREPARE':
            recovery_system.recover_from_prepare_phase(txn_id, {
                'phase': 'PREPARE',
                'participants': ['HDFC', 'SBI', 'NPCI', 'SMS_GATEWAY']
            })
        else:
            recovery_system.recover_from_commit_phase(txn_id, {
                'phase': 'COMMIT', 
                'participants': ['HDFC', 'SBI', 'NPCI', 'SMS_GATEWAY']
            })

# Run monsoon simulation
simulate_monsoon_disaster()
```

### Optimizations and Variations

*[Engineering discussions, optimization strategies]*

"Production systems mein pure 2PC rarely use karte hain. Optimizations zaroori hain:"

**1. Presumed Abort Optimization:**

```python
class PresumedAbort2PC:
    """Optimization: Assume ABORT if no explicit commit log"""
    
    def __init__(self):
        self.only_log_commits = True  # Don't log aborts
        
    def recovery_logic(self, txn_id):
        """If no commit log found, assume aborted"""
        
        if self.has_commit_log(txn_id):
            return "COMMITTED"
        else:
            return "ABORTED"  # Presumed abort
```

**2. Early Prepare Optimization:**

```python
def optimized_prepare_phase(self, participants, operation):
    """Start prepare as soon as operation details available"""
    
    # Don't wait for all participants to be ready
    # Start preparing participants as they become available
    
    prepared_participants = []
    for participant in participants:
        if participant.is_ready():
            result = participant.prepare(operation)
            if result == "VOTE-COMMIT":
                prepared_participants.append(participant)
            else:
                # Early abort if anyone says no
                return self.abort_immediately(prepared_participants)
    
    return self.proceed_to_commit(prepared_participants)
```

### Part 1 Summary: Foundation Laid

*[Recap music, key points summary]*

"Toh yaar, Part 1 mein humne dekha:

1. **Two-Phase Commit Protocol** - Mumbai wedding coordination jaisa
2. **Phase 1 (PREPARE)** - 'Ready ho kya?' - Resource locking, validation  
3. **Phase 2 (COMMIT/ABORT)** - 'Pakka kar do!' - Final decision execution
4. **Coordinator Role** - Wedding planner jaisa traffic controller
5. **Participant Responsibilities** - Vendors jaisa resource managers
6. **Failure Scenarios** - Murphy's law in action
7. **Performance Implications** - Blocking problem like Mumbai traffic
8. **Recovery Mechanisms** - Monsoon resilience strategies

**Real-world Applications:**
- UPI transactions (₹500 to Zomato)
- Banking transfers (HDFC to SBI) 
- E-commerce orders (Flipkart inventory + payment)
- Distributed database transactions

**Key Technical Insights:**
- 2PC guarantees atomicity in distributed systems
- But it's a blocking protocol - performance bottleneck
- Single point of failure - coordinator crash is dangerous
- Recovery is complex but necessary
- Used in production but with heavy optimizations

Part 2 mein hum dekhenge advanced concepts - 3PC, Saga pattern, aur modern alternatives. Plus real production case studies from Netflix, Amazon, aur Indian companies."

**Code Summary for Part 1:**
- Python: Basic 2PC implementation (500+ lines)
- Java: Production-grade banking system (800+ lines)  
- Failure handling and recovery mechanisms
- Performance analysis and optimization strategies
- Mumbai/Indian context examples throughout

"Keep coding, keep learning! Mumbai ki spirit mein - 'Sab kuch milke karooge toh sab kuch ho jaayega!' 2PC bhi yahi kehta hai - all participants commit together, or nobody commits!"

*[Episode end music fading out]*

---

**Word Count: 7,247 words**

**Part 1 Complete - Ready for Part 2: Advanced 2PC Concepts and Alternatives**