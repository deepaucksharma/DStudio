/**
 * Episode 34: Vector Clocks - Java Implementation
 * Mumbai Banking System with Vector Clocks
 * 
 * Demonstrates: Vector clocks in distributed banking transactions
 * Context: HDFC Bank branch coordination across Mumbai
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

class BankTransaction {
    private final String transactionId;
    private final String fromAccount;
    private final String toAccount;
    private final double amount;
    private final String branchId;
    private final LocalDateTime timestamp;
    private final Map<String, Integer> vectorClock;
    private final String transactionType;
    
    public BankTransaction(String transactionId, String fromAccount, String toAccount, 
                          double amount, String branchId, Map<String, Integer> vectorClock, 
                          String transactionType) {
        this.transactionId = transactionId;
        this.fromAccount = fromAccount;
        this.toAccount = toAccount;
        this.amount = amount;
        this.branchId = branchId;
        this.timestamp = LocalDateTime.now();
        this.vectorClock = new HashMap<>(vectorClock);
        this.transactionType = transactionType;
    }
    
    // Getters
    public String getTransactionId() { return transactionId; }
    public String getFromAccount() { return fromAccount; }
    public String getToAccount() { return toAccount; }
    public double getAmount() { return amount; }
    public String getBranchId() { return branchId; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public Map<String, Integer> getVectorClock() { return new HashMap<>(vectorClock); }
    public String getTransactionType() { return transactionType; }
    
    @Override
    public String toString() {
        return String.format("TX[%s] %s→%s ₹%.2f @ %s | Clock: %s", 
                           transactionId, fromAccount, toAccount, amount, 
                           timestamp.format(DateTimeFormatter.ofPattern("HH:mm:ss")), 
                           vectorClock);
    }
}

class HDFCBranchVectorClock {
    private final String branchId;
    private final Map<String, Integer> clock;
    private final List<BankTransaction> transactionLog;
    private final ReentrantLock lock;
    private final Set<String> allBranches;
    
    public HDFCBranchVectorClock(String branchId, Set<String> allBranches) {
        this.branchId = branchId;
        this.allBranches = new HashSet<>(allBranches);
        this.clock = new ConcurrentHashMap<>();
        this.transactionLog = new ArrayList<>();
        this.lock = new ReentrantLock();
        
        // Initialize vector clock
        for (String branch : allBranches) {
            clock.put(branch, 0);
        }
    }
    
    public BankTransaction processLocalTransaction(String fromAccount, String toAccount, 
                                                 double amount, String transactionType) {
        lock.lock();
        try {
            // Increment own clock
            clock.put(branchId, clock.get(branchId) + 1);
            
            String txId = generateTransactionId();
            BankTransaction transaction = new BankTransaction(
                txId, fromAccount, toAccount, amount, branchId, clock, transactionType
            );
            
            transactionLog.add(transaction);
            
            System.out.printf("🏦 %s | %s | Clock: %s%n", 
                            branchId, transaction.getTransactionType(), clock);
            
            return transaction;
        } finally {
            lock.unlock();
        }
    }
    
    public void receiveRemoteTransaction(BankTransaction remoteTransaction) {
        lock.lock();
        try {
            // Update vector clock using max rule
            Map<String, Integer> remoteClock = remoteTransaction.getVectorClock();
            for (String branch : allBranches) {
                if (remoteClock.containsKey(branch)) {
                    clock.put(branch, Math.max(clock.get(branch), remoteClock.get(branch)));
                }
            }
            
            // Increment own clock
            clock.put(branchId, clock.get(branchId) + 1);
            
            transactionLog.add(remoteTransaction);
            
            System.out.printf("📨 %s received TX from %s | Updated Clock: %s%n",
                            branchId, remoteTransaction.getBranchId(), clock);
        } finally {
            lock.unlock();
        }
    }
    
    public String compareTransactions(BankTransaction tx1, BankTransaction tx2) {
        Map<String, Integer> clock1 = tx1.getVectorClock();
        Map<String, Integer> clock2 = tx2.getVectorClock();
        
        boolean tx1BeforeTx2 = true;
        boolean tx1StrictlyBefore = false;
        boolean tx2BeforeTx1 = true;
        boolean tx2StrictlyBefore = false;
        
        for (String branch : allBranches) {
            int c1 = clock1.getOrDefault(branch, 0);
            int c2 = clock2.getOrDefault(branch, 0);
            
            if (c1 > c2) {
                tx1BeforeTx2 = false;
            }
            if (c1 < c2) {
                tx1StrictlyBefore = true;
                tx2BeforeTx1 = false;
            }
            if (c2 > c1) {
                tx2BeforeTx1 = false;
            }
            if (c2 < c1) {
                tx2StrictlyBefore = true;
                tx1BeforeTx2 = false;
            }
        }
        
        if (tx1BeforeTx2 && tx1StrictlyBefore) {
            return "BEFORE";
        } else if (tx2BeforeTx1 && tx2StrictlyBefore) {
            return "AFTER";
        } else if (clock1.equals(clock2)) {
            return "SAME";
        } else {
            return "CONCURRENT";
        }
    }
    
    private String generateTransactionId() {
        return String.format("TX_%s_%d", branchId, System.currentTimeMillis() % 10000);
    }
    
    public List<BankTransaction> getTransactionLog() {
        return new ArrayList<>(transactionLog);
    }
    
    public String getBranchId() {
        return branchId;
    }
    
    public Map<String, Integer> getCurrentClock() {
        return new HashMap<>(clock);
    }
}

public class VectorClockSystem {
    
    public static void main(String[] args) {
        System.out.println("🏛️ HDFC Bank Mumbai Branch Coordination System");
        System.out.println("Vector Clocks for Distributed Banking Transactions");
        System.out.println("=" + "=".repeat(60));
        
        // Mumbai HDFC branches
        Set<String> branches = Set.of("ANDHERI_WEST", "BANDRA_KURLA", "FORT_BRANCH");
        
        Map<String, HDFCBranchVectorClock> branchSystems = new HashMap<>();
        for (String branch : branches) {
            branchSystems.put(branch, new HDFCBranchVectorClock(branch, branches));
        }
        
        // Simulate banking transactions during peak hours
        simulatePeakHourTransactions(branchSystems);
        
        // Analyze transaction ordering
        analyzeCausalRelationships(branchSystems);
        
        // Production scenario - UPI integration
        simulateUPIIntegration(branchSystems);
    }
    
    private static void simulatePeakHourTransactions(Map<String, HDFCBranchVectorClock> branches) {
        System.out.println("\n💼 Peak Hour Transaction Simulation (10 AM - 12 PM)");
        System.out.println("-".repeat(50));
        
        // Transaction 1: Andheri West - Customer deposit
        BankTransaction tx1 = branches.get("ANDHERI_WEST")
            .processLocalTransaction("SAVINGS_12345", "SAVINGS_12345", 50000, "CASH_DEPOSIT");
        
        // Transaction 2: Bandra Kurla - NEFT transfer
        BankTransaction tx2 = branches.get("BANDRA_KURLA")
            .processLocalTransaction("CURRENT_67890", "SAVINGS_11111", 150000, "NEFT_TRANSFER");
        
        // Branches synchronize transaction information
        System.out.println("\n🔄 Inter-branch Communication:");
        branches.get("BANDRA_KURLA").receiveRemoteTransaction(tx1);
        branches.get("FORT_BRANCH").receiveRemoteTransaction(tx2);
        
        // Transaction 3: Fort branch processes loan disbursement after receiving updates
        BankTransaction tx3 = branches.get("FORT_BRANCH")
            .processLocalTransaction("LOAN_ACCOUNT", "SAVINGS_22222", 2500000, "LOAN_DISBURSEMENT");
        
        // Transaction 4: Andheri West processes ATM withdrawal
        BankTransaction tx4 = branches.get("ANDHERI_WEST")
            .processLocalTransaction("SAVINGS_33333", "ATM_CASH", 10000, "ATM_WITHDRAWAL");
        
        // More inter-branch communication
        branches.get("ANDHERI_WEST").receiveRemoteTransaction(tx3);
        branches.get("BANDRA_KURLA").receiveRemoteTransaction(tx4);
    }
    
    private static void analyzeCausalRelationships(Map<String, HDFCBranchVectorClock> branches) {
        System.out.println("\n🔍 Transaction Causal Relationship Analysis");
        System.out.println("-".repeat(50));
        
        List<BankTransaction> allTransactions = new ArrayList<>();
        for (HDFCBranchVectorClock branch : branches.values()) {
            allTransactions.addAll(branch.getTransactionLog());
        }
        
        // Sort by timestamp for analysis
        allTransactions.sort(Comparator.comparing(BankTransaction::getTimestamp));
        
        System.out.println("Transaction Timeline:");
        for (int i = 0; i < allTransactions.size(); i++) {
            BankTransaction tx = allTransactions.get(i);
            System.out.printf("%d. %s%n", i + 1, tx);
        }
        
        // Find concurrent transactions
        System.out.println("\n⏱️ Concurrent Transaction Detection:");
        HDFCBranchVectorClock analyzer = branches.values().iterator().next();
        
        for (int i = 0; i < allTransactions.size(); i++) {
            for (int j = i + 1; j < allTransactions.size(); j++) {
                String relationship = analyzer.compareTransactions(
                    allTransactions.get(i), allTransactions.get(j)
                );
                if ("CONCURRENT".equals(relationship)) {
                    System.out.printf("  • TX%d || TX%d (Concurrent)%n", i + 1, j + 1);
                }
            }
        }
    }
    
    private static void simulateUPIIntegration(Map<String, HDFCBranchVectorClock> branches) {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("📱 Production Example: UPI Payment Coordination");
        System.out.println("Multiple branches coordinating UPI transactions");
        System.out.println("=".repeat(60));
        
        // UPI payment scenario
        System.out.println("\n💳 UPI Payment: Customer→Merchant (₹2,500)");
        
        // Step 1: Customer's bank (Andheri) initiates payment
        BankTransaction upiDebit = branches.get("ANDHERI_WEST")
            .processLocalTransaction("UPI_CUST_12345", "UPI_CLEARING", 2500, "UPI_DEBIT");
        
        // Step 2: Clearing branch (Bandra) processes payment
        branches.get("BANDRA_KURLA").receiveRemoteTransaction(upiDebit);
        BankTransaction upiClearing = branches.get("BANDRA_KURLA")
            .processLocalTransaction("UPI_CLEARING", "UPI_MERCHANT_67890", 2500, "UPI_CLEARING");
        
        // Step 3: Merchant's bank (Fort) credits account
        branches.get("FORT_BRANCH").receiveRemoteTransaction(upiClearing);
        BankTransaction upiCredit = branches.get("FORT_BRANCH")
            .processLocalTransaction("UPI_MERCHANT_67890", "MERCHANT_ACCOUNT", 2500, "UPI_CREDIT");
        
        // Analyze UPI transaction flow causality
        System.out.println("\n🔗 UPI Transaction Causality:");
        HDFCBranchVectorClock analyzer = branches.get("ANDHERI_WEST");
        System.out.printf("Debit→Clearing: %s%n", 
                         analyzer.compareTransactions(upiDebit, upiClearing));
        System.out.printf("Clearing→Credit: %s%n", 
                         analyzer.compareTransactions(upiClearing, upiCredit));
        
        // Print final clock states
        System.out.println("\n📊 Final Vector Clock States:");
        for (HDFCBranchVectorClock branch : branches.values()) {
            System.out.printf("%s: %s%n", branch.getBranchId(), branch.getCurrentClock());
        }
        
        System.out.println("\n✅ Banking Vector Clock Simulation Complete!");
        System.out.println("💡 Key Insight: Vector clocks ensure proper transaction ordering");
        System.out.println("   across distributed bank branches without synchronized clocks");
    }
}