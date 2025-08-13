/**
 * Two-Phase Commit Protocol Implementation
 * Distributed transaction coordination across multiple databases
 * Example: Banking transfer across different bank systems
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.time.Instant;
import java.util.logging.Logger;
import java.util.logging.Level;

// Transaction states
enum TransactionState {
    PREPARING, PREPARED, COMMITTED, ABORTED, UNKNOWN
}

// Participant response types
enum ParticipantResponse {
    VOTE_COMMIT, VOTE_ABORT, ACK_COMMIT, ACK_ABORT
}

// Transaction participant - Individual bank database
class TransactionParticipant {
    private final String participantId;
    private final String bankName;
    private final Map<String, Double> accounts; // Account -> Balance
    private final Map<String, TransactionState> transactionStates;
    private final Random random = new Random();
    private volatile boolean isOnline = true;
    private final double failureRate; // Simulate network/system failures
    
    public TransactionParticipant(String participantId, String bankName, double failureRate) {
        this.participantId = participantId;
        this.bankName = bankName;
        this.failureRate = failureRate;
        this.accounts = new ConcurrentHashMap<>();
        this.transactionStates = new ConcurrentHashMap<>();
        
        // Initialize with some accounts
        initializeAccounts();
    }
    
    private void initializeAccounts() {
        accounts.put("ACC001", 50000.0);
        accounts.put("ACC002", 75000.0);
        accounts.put("ACC003", 100000.0);
        accounts.put("ACC004", 25000.0);
        accounts.put("ACC005", 80000.0);
    }
    
    // Phase 1: Prepare phase
    public CompletableFuture<ParticipantResponse> prepare(String transactionId, 
                                                         String account, double amount, String operation) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Simulate network delay
                Thread.sleep(random.nextInt(100) + 50);
                
                // Simulate failures
                if (!isOnline || random.nextDouble() < failureRate) {
                    throw new RuntimeException("Participant " + participantId + " is offline or failed");
                }
                
                Logger.getLogger(getClass().getName()).info(
                    String.format("[%s] Preparing transaction %s: %s ₹%.2f on %s", 
                                bankName, transactionId, operation, amount, account));
                
                // Check if transaction can be performed
                boolean canCommit = canPerformOperation(account, amount, operation);
                
                if (canCommit) {
                    transactionStates.put(transactionId, TransactionState.PREPARED);
                    // Hold resources (simulate locking)
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[%s] VOTE_COMMIT for transaction %s", bankName, transactionId));
                    return ParticipantResponse.VOTE_COMMIT;
                } else {
                    transactionStates.put(transactionId, TransactionState.ABORTED);
                    Logger.getLogger(getClass().getName()).warning(
                        String.format("[%s] VOTE_ABORT for transaction %s: Insufficient funds or invalid account", 
                                    bankName, transactionId));
                    return ParticipantResponse.VOTE_ABORT;
                }
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return ParticipantResponse.VOTE_ABORT;
            } catch (Exception e) {
                Logger.getLogger(getClass().getName()).log(Level.WARNING, 
                    String.format("[%s] Prepare failed for transaction %s", bankName, transactionId), e);
                return ParticipantResponse.VOTE_ABORT;
            }
        });
    }
    
    // Phase 2: Commit phase
    public CompletableFuture<ParticipantResponse> commit(String transactionId, 
                                                        String account, double amount, String operation) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(random.nextInt(50) + 25);
                
                if (!isOnline) {
                    throw new RuntimeException("Participant " + participantId + " is offline");
                }
                
                TransactionState state = transactionStates.get(transactionId);
                if (state != TransactionState.PREPARED) {
                    Logger.getLogger(getClass().getName()).warning(
                        String.format("[%s] Cannot commit transaction %s: Not in PREPARED state", 
                                    bankName, transactionId));
                    return ParticipantResponse.ACK_ABORT;
                }
                
                // Perform the actual operation
                boolean success = performOperation(account, amount, operation);
                
                if (success) {
                    transactionStates.put(transactionId, TransactionState.COMMITTED);
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[%s] Successfully committed transaction %s", bankName, transactionId));
                    return ParticipantResponse.ACK_COMMIT;
                } else {
                    transactionStates.put(transactionId, TransactionState.ABORTED);
                    return ParticipantResponse.ACK_ABORT;
                }
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return ParticipantResponse.ACK_ABORT;
            } catch (Exception e) {
                Logger.getLogger(getClass().getName()).log(Level.WARNING, 
                    String.format("[%s] Commit failed for transaction %s", bankName, transactionId), e);
                return ParticipantResponse.ACK_ABORT;
            }
        });
    }
    
    // Phase 2: Abort phase
    public CompletableFuture<ParticipantResponse> abort(String transactionId) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(random.nextInt(50) + 25);
                
                transactionStates.put(transactionId, TransactionState.ABORTED);
                // Release held resources
                
                Logger.getLogger(getClass().getName()).info(
                    String.format("[%s] Successfully aborted transaction %s", bankName, transactionId));
                
                return ParticipantResponse.ACK_ABORT;
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return ParticipantResponse.ACK_ABORT;
            }
        });
    }
    
    private boolean canPerformOperation(String account, double amount, String operation) {
        Double balance = accounts.get(account);
        if (balance == null) {
            return false; // Account doesn't exist
        }
        
        if ("DEBIT".equals(operation)) {
            return balance >= amount; // Sufficient funds check
        } else if ("CREDIT".equals(operation)) {
            return true; // Credits are always allowed
        }
        
        return false;
    }
    
    private boolean performOperation(String account, double amount, String operation) {
        Double currentBalance = accounts.get(account);
        if (currentBalance == null) {
            return false;
        }
        
        if ("DEBIT".equals(operation)) {
            if (currentBalance >= amount) {
                accounts.put(account, currentBalance - amount);
                Logger.getLogger(getClass().getName()).info(
                    String.format("[%s] Debited ₹%.2f from %s. New balance: ₹%.2f", 
                                bankName, amount, account, accounts.get(account)));
                return true;
            }
        } else if ("CREDIT".equals(operation)) {
            accounts.put(account, currentBalance + amount);
            Logger.getLogger(getClass().getName()).info(
                String.format("[%s] Credited ₹%.2f to %s. New balance: ₹%.2f", 
                            bankName, amount, account, accounts.get(account)));
            return true;
        }
        
        return false;
    }
    
    public double getBalance(String account) {
        return accounts.getOrDefault(account, 0.0);
    }
    
    public void setOnline(boolean online) {
        this.isOnline = online;
        Logger.getLogger(getClass().getName()).info(
            String.format("[%s] is now %s", bankName, online ? "ONLINE" : "OFFLINE"));
    }
    
    public String getParticipantId() { return participantId; }
    public String getBankName() { return bankName; }
    public Map<String, Double> getAccounts() { return new HashMap<>(accounts); }
}

// Transaction coordinator - Central bank jaisa
class TransactionCoordinator {
    private static final Logger logger = Logger.getLogger(TransactionCoordinator.class.getName());
    
    private final String coordinatorId;
    private final List<TransactionParticipant> participants;
    private final Map<String, TransactionState> globalTransactionStates;
    private final AtomicLong transactionCounter;
    private final ExecutorService executor;
    
    public TransactionCoordinator(String coordinatorId) {
        this.coordinatorId = coordinatorId;
        this.participants = new ArrayList<>();
        this.globalTransactionStates = new ConcurrentHashMap<>();
        this.transactionCounter = new AtomicLong(1);
        this.executor = Executors.newFixedThreadPool(20);
    }
    
    public void addParticipant(TransactionParticipant participant) {
        participants.add(participant);
        logger.info("Added participant: " + participant.getBankName());
    }
    
    // Distributed money transfer using 2PC
    public CompletableFuture<Boolean> transferMoney(String fromAccount, String toAccount, 
                                                   double amount, String fromBankId, String toBankId) {
        String transactionId = "TXN_" + transactionCounter.getAndIncrement() + "_" + System.currentTimeMillis();
        
        logger.info(String.format("Starting 2PC transaction %s: Transfer ₹%.2f from %s@%s to %s@%s",
                                transactionId, amount, fromAccount, fromBankId, toAccount, toBankId));
        
        return executeTransaction(transactionId, fromAccount, toAccount, amount, fromBankId, toBankId);
    }
    
    private CompletableFuture<Boolean> executeTransaction(String transactionId, String fromAccount, 
                                                         String toAccount, double amount, 
                                                         String fromBankId, String toBankId) {
        
        globalTransactionStates.put(transactionId, TransactionState.PREPARING);
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Phase 1: Prepare
                logger.info(String.format("[COORDINATOR] Starting Phase 1 (PREPARE) for transaction %s", transactionId));
                
                boolean phase1Success = executePhase1(transactionId, fromAccount, toAccount, amount, fromBankId, toBankId);
                
                if (!phase1Success) {
                    logger.warning(String.format("[COORDINATOR] Phase 1 failed for transaction %s. Starting abort.", transactionId));
                    executeGlobalAbort(transactionId);
                    return false;
                }
                
                // Phase 2: Commit
                logger.info(String.format("[COORDINATOR] Phase 1 successful. Starting Phase 2 (COMMIT) for transaction %s", transactionId));
                
                boolean phase2Success = executePhase2Commit(transactionId, fromAccount, toAccount, amount, fromBankId, toBankId);
                
                if (phase2Success) {
                    globalTransactionStates.put(transactionId, TransactionState.COMMITTED);
                    logger.info(String.format("[COORDINATOR] Transaction %s COMMITTED successfully", transactionId));
                } else {
                    globalTransactionStates.put(transactionId, TransactionState.ABORTED);
                    logger.warning(String.format("[COORDINATOR] Transaction %s ABORTED during Phase 2", transactionId));
                }
                
                return phase2Success;
                
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Transaction coordinator error for " + transactionId, e);
                executeGlobalAbort(transactionId);
                return false;
            }
        }, executor);
    }
    
    private boolean executePhase1(String transactionId, String fromAccount, String toAccount, 
                                 double amount, String fromBankId, String toBankId) {
        
        List<CompletableFuture<ParticipantResponse>> prepareResponses = new ArrayList<>();
        
        // Send prepare to all relevant participants
        for (TransactionParticipant participant : participants) {
            if (participant.getParticipantId().equals(fromBankId)) {
                // Debit operation
                prepareResponses.add(participant.prepare(transactionId, fromAccount, amount, "DEBIT"));
            } else if (participant.getParticipantId().equals(toBankId)) {
                // Credit operation  
                prepareResponses.add(participant.prepare(transactionId, toAccount, amount, "CREDIT"));
            }
        }
        
        // Wait for all prepare responses with timeout
        try {
            List<ParticipantResponse> responses = new ArrayList<>();
            
            for (CompletableFuture<ParticipantResponse> future : prepareResponses) {
                ParticipantResponse response = future.get(5, TimeUnit.SECONDS);
                responses.add(response);
            }
            
            // Check if all participants voted to commit
            boolean allCommit = responses.stream()
                                        .allMatch(response -> response == ParticipantResponse.VOTE_COMMIT);
            
            logger.info(String.format("[COORDINATOR] Phase 1 results for %s: %d participants, all voted commit: %s",
                                    transactionId, responses.size(), allCommit));
            
            return allCommit;
            
        } catch (TimeoutException e) {
            logger.warning(String.format("[COORDINATOR] Phase 1 timeout for transaction %s", transactionId));
            return false;
        } catch (Exception e) {
            logger.log(Level.WARNING, "Phase 1 execution error for " + transactionId, e);
            return false;
        }
    }
    
    private boolean executePhase2Commit(String transactionId, String fromAccount, String toAccount,
                                       double amount, String fromBankId, String toBankId) {
        
        List<CompletableFuture<ParticipantResponse>> commitResponses = new ArrayList<>();
        
        // Send commit to all relevant participants
        for (TransactionParticipant participant : participants) {
            if (participant.getParticipantId().equals(fromBankId)) {
                commitResponses.add(participant.commit(transactionId, fromAccount, amount, "DEBIT"));
            } else if (participant.getParticipantId().equals(toBankId)) {
                commitResponses.add(participant.commit(transactionId, toAccount, amount, "CREDIT"));
            }
        }
        
        try {
            List<ParticipantResponse> responses = new ArrayList<>();
            
            for (CompletableFuture<ParticipantResponse> future : commitResponses) {
                ParticipantResponse response = future.get(10, TimeUnit.SECONDS);
                responses.add(response);
            }
            
            boolean allCommitted = responses.stream()
                                           .allMatch(response -> response == ParticipantResponse.ACK_COMMIT);
            
            logger.info(String.format("[COORDINATOR] Phase 2 results for %s: all committed: %s",
                                    transactionId, allCommitted));
            
            return allCommitted;
            
        } catch (Exception e) {
            logger.log(Level.WARNING, "Phase 2 commit error for " + transactionId, e);
            // In real implementation, would retry commits or handle partial failures
            return false;
        }
    }
    
    private void executeGlobalAbort(String transactionId) {
        logger.info(String.format("[COORDINATOR] Executing global abort for transaction %s", transactionId));
        
        List<CompletableFuture<ParticipantResponse>> abortResponses = new ArrayList<>();
        
        // Send abort to all participants
        for (TransactionParticipant participant : participants) {
            abortResponses.add(participant.abort(transactionId));
        }
        
        // Wait for abort acknowledgments (best effort)
        try {
            CompletableFuture.allOf(abortResponses.toArray(new CompletableFuture[0]))
                            .get(5, TimeUnit.SECONDS);
        } catch (Exception e) {
            logger.log(Level.WARNING, "Global abort completion error for " + transactionId, e);
        }
        
        globalTransactionStates.put(transactionId, TransactionState.ABORTED);
    }
    
    public Map<String, Object> getSystemStatus() {
        Map<String, Object> status = new HashMap<>();
        
        // Participant status
        List<Map<String, Object>> participantStatus = new ArrayList<>();
        for (TransactionParticipant participant : participants) {
            Map<String, Object> pStatus = new HashMap<>();
            pStatus.put("id", participant.getParticipantId());
            pStatus.put("bank", participant.getBankName());
            pStatus.put("accounts", participant.getAccounts());
            participantStatus.add(pStatus);
        }
        
        status.put("participants", participantStatus);
        status.put("total_transactions", transactionCounter.get() - 1);
        status.put("transaction_states", new HashMap<>(globalTransactionStates));
        
        return status;
    }
    
    public void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

// Main demo class
public class TwoPhaseCommitProtocol {
    
    public static void main(String[] args) {
        System.out.println("=== Two-Phase Commit Protocol Demo ===");
        System.out.println("Simulating inter-bank transfers using 2PC");
        
        // Create transaction coordinator
        TransactionCoordinator coordinator = new TransactionCoordinator("CENTRAL_COORDINATOR");
        
        // Create bank participants - Indian banks
        TransactionParticipant sbi = new TransactionParticipant("SBI_001", "State Bank of India", 0.05);
        TransactionParticipant hdfc = new TransactionParticipant("HDFC_001", "HDFC Bank", 0.03);
        TransactionParticipant icici = new TransactionParticipant("ICICI_001", "ICICI Bank", 0.04);
        TransactionParticipant axis = new TransactionParticipant("AXIS_001", "Axis Bank", 0.06);
        
        // Register participants
        coordinator.addParticipant(sbi);
        coordinator.addParticipant(hdfc);
        coordinator.addParticipant(icici);
        coordinator.addParticipant(axis);
        
        System.out.println("\n=== Initial Account Balances ===");
        printSystemStatus(coordinator);
        
        try {
            // Test successful transfers
            System.out.println("\n=== Testing Successful Transfers ===");
            
            // SBI to HDFC transfer
            CompletableFuture<Boolean> transfer1 = coordinator.transferMoney(
                "ACC001", "ACC002", 5000.0, "SBI_001", "HDFC_001"
            );
            
            // ICICI to Axis transfer
            CompletableFuture<Boolean> transfer2 = coordinator.transferMoney(
                "ACC003", "ACC004", 8000.0, "ICICI_001", "AXIS_001"
            );
            
            // Wait for transfers to complete
            Boolean result1 = transfer1.get(15, TimeUnit.SECONDS);
            Boolean result2 = transfer2.get(15, TimeUnit.SECONDS);
            
            System.out.println("Transfer 1 result: " + (result1 ? "SUCCESS" : "FAILED"));
            System.out.println("Transfer 2 result: " + (result2 ? "SUCCESS" : "FAILED"));
            
            Thread.sleep(500); // Wait for all operations to complete
            
            System.out.println("\n=== Balances After Successful Transfers ===");
            printSystemStatus(coordinator);
            
            // Test failure scenarios
            System.out.println("\n=== Testing Failure Scenarios ===");
            
            // Test insufficient funds
            System.out.println("\n1. Testing insufficient funds scenario:");
            CompletableFuture<Boolean> transfer3 = coordinator.transferMoney(
                "ACC004", "ACC001", 100000.0, "AXIS_001", "SBI_001" // More than available
            );
            
            Boolean result3 = transfer3.get(15, TimeUnit.SECONDS);
            System.out.println("Large transfer result: " + (result3 ? "SUCCESS" : "FAILED (Expected)"));
            
            // Test network failure
            System.out.println("\n2. Testing network failure scenario:");
            hdfc.setOnline(false); // Simulate HDFC going offline
            
            CompletableFuture<Boolean> transfer4 = coordinator.transferMoney(
                "ACC001", "ACC002", 2000.0, "SBI_001", "HDFC_001"
            );
            
            Boolean result4 = transfer4.get(15, TimeUnit.SECONDS);
            System.out.println("Transfer to offline bank result: " + (result4 ? "SUCCESS" : "FAILED (Expected)"));
            
            hdfc.setOnline(true); // Bring HDFC back online
            
            // Test concurrent transfers
            System.out.println("\n=== Testing Concurrent Transfers ===");
            
            List<CompletableFuture<Boolean>> concurrentTransfers = new ArrayList<>();
            
            // Multiple simultaneous transfers
            for (int i = 0; i < 5; i++) {
                CompletableFuture<Boolean> transfer = coordinator.transferMoney(
                    "ACC00" + ((i % 3) + 1), "ACC00" + ((i % 3) + 2), 1000.0, 
                    "SBI_001", "HDFC_001"
                );
                concurrentTransfers.add(transfer);
            }
            
            // Wait for all concurrent transfers
            int successCount = 0;
            for (CompletableFuture<Boolean> transfer : concurrentTransfers) {
                try {
                    Boolean result = transfer.get(20, TimeUnit.SECONDS);
                    if (result) successCount++;
                } catch (Exception e) {
                    System.out.println("Concurrent transfer failed: " + e.getMessage());
                }
            }
            
            System.out.println(String.format("Concurrent transfers: %d/%d successful", 
                                            successCount, concurrentTransfers.size()));
            
            Thread.sleep(1000);
            
            System.out.println("\n=== Final System Status ===");
            printSystemStatus(coordinator);
            
            // Performance metrics
            System.out.println("\n=== Performance Metrics ===");
            Map<String, Object> status = coordinator.getSystemStatus();
            System.out.println("Total transactions processed: " + status.get("total_transactions"));
            
            @SuppressWarnings("unchecked")
            Map<String, TransactionState> txStates = (Map<String, TransactionState>) status.get("transaction_states");
            long committed = txStates.values().stream().filter(state -> state == TransactionState.COMMITTED).count();
            long aborted = txStates.values().stream().filter(state -> state == TransactionState.ABORTED).count();
            
            System.out.println("Committed transactions: " + committed);
            System.out.println("Aborted transactions: " + aborted);
            System.out.println("Success rate: " + String.format("%.1f%%", (committed * 100.0) / (committed + aborted)));
            
            System.out.println("\n✅ Two-Phase Commit Protocol demo completed successfully!");
            
        } catch (Exception e) {
            System.err.println("Demo failed: " + e.getMessage());
            e.printStackTrace();
        } finally {
            coordinator.shutdown();
        }
    }
    
    private static void printSystemStatus(TransactionCoordinator coordinator) {
        Map<String, Object> status = coordinator.getSystemStatus();
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> participants = (List<Map<String, Object>>) status.get("participants");
        
        for (Map<String, Object> participant : participants) {
            String bankName = (String) participant.get("bank");
            String bankId = (String) participant.get("id");
            
            @SuppressWarnings("unchecked")
            Map<String, Double> accounts = (Map<String, Double>) participant.get("accounts");
            
            System.out.println(String.format("%s (%s):", bankName, bankId));
            for (Map.Entry<String, Double> account : accounts.entrySet()) {
                System.out.println(String.format("  %s: ₹%.2f", account.getKey(), account.getValue()));
            }
        }
    }
}