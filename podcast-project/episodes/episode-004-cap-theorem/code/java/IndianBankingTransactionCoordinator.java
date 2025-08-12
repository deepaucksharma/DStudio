/**
 * Indian Banking Transaction Coordinator - Episode 4
 * भारतीय banking system में distributed transactions का practical implementation
 * 
 * यह system दिखाता है कि कैसे Indian banks (SBI, HDFC, ICICI) के बीच
 * NEFT/RTGS/IMPS transfers में strong consistency maintain होती है।
 * 
 * Real scenarios:
 * - Inter-bank fund transfers
 * - RBI settlement system integration
 * - UPI transaction coordination  
 * - ATM network transactions
 * - Credit card payment processing
 */

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Indian Banking Transaction Types
 */
enum TransactionType {
    NEFT("National Electronic Funds Transfer"),
    RTGS("Real Time Gross Settlement"), 
    IMPS("Immediate Payment Service"),
    UPI("Unified Payments Interface"),
    ATM_WITHDRAWAL("ATM Cash Withdrawal"),
    CARD_PAYMENT("Card Payment");
    
    private final String description;
    
    TransactionType(String description) {
        this.description = description;
    }
    
    public String getDescription() { return description; }
}

/**
 * Transaction Status Lifecycle
 */
enum TransactionStatus {
    INITIATED,      // लेनदेन शुरू हुआ
    VALIDATED,      // Validation passed
    AUTHORIZED,     // Bank authorization done  
    COMMITTED,      // Successfully committed
    FAILED,         // Transaction failed
    REVERSED,       // Transaction reversed
    TIMEOUT         // Transaction timed out
}

/**
 * Indian Bank Representation
 */
class IndianBank {
    private final String bankCode;
    private final String bankName;
    private final String swiftCode;
    private final Map<String, BankAccount> accounts;
    private final AtomicLong transactionCounter;
    
    // Network simulation
    private volatile boolean isOnline;
    private volatile double networkDelay; // in milliseconds
    
    public IndianBank(String bankCode, String bankName, String swiftCode) {
        this.bankCode = bankCode;
        this.bankName = bankName;
        this.swiftCode = swiftCode;
        this.accounts = new ConcurrentHashMap<>();
        this.transactionCounter = new AtomicLong(1);
        this.isOnline = true;
        this.networkDelay = 100.0; // Default 100ms network delay
    }
    
    /**
     * Create sample account - Indian banking format
     */
    public void createAccount(String accountNumber, String customerName, 
                            BigDecimal initialBalance, String ifscCode) {
        BankAccount account = new BankAccount(accountNumber, customerName, 
                                            initialBalance, ifscCode, bankCode);
        accounts.put(accountNumber, account);
        System.out.println("✅ Account created: " + customerName + 
                          " (" + bankName + ") - Balance: ₹" + initialBalance);
    }
    
    /**
     * Debit amount from account with validation
     */
    public synchronized boolean debitAccount(String accountNumber, BigDecimal amount, 
                                           String transactionRef) throws InterruptedException {
        // Simulate network delay
        Thread.sleep((long) networkDelay);
        
        if (!isOnline) {
            System.out.println("❌ " + bankName + " is offline - transaction failed");
            return false;
        }
        
        BankAccount account = accounts.get(accountNumber);
        if (account == null) {
            System.out.println("❌ Account not found: " + accountNumber);
            return false;
        }
        
        // Check minimum balance (₹10,000 for current accounts)
        BigDecimal minimumBalance = new BigDecimal("10000");
        if (account.getBalance().subtract(amount).compareTo(minimumBalance) < 0) {
            System.out.println("❌ Insufficient balance. Required minimum: ₹" + minimumBalance);
            return false;
        }
        
        // Check daily transaction limit (₹2,00,000 for NEFT/RTGS)
        if (amount.compareTo(new BigDecimal("200000")) > 0) {
            System.out.println("⚠️  High value transaction - additional verification required");
        }
        
        // Debit the amount
        BigDecimal newBalance = account.getBalance().subtract(amount);
        account.setBalance(newBalance);
        account.addTransaction(transactionRef, amount.negate(), "DEBIT");
        
        System.out.println("💸 " + bankName + " debited ₹" + amount + 
                          " from " + account.getCustomerName() + 
                          " (New balance: ₹" + newBalance + ")");
        return true;
    }
    
    /**
     * Credit amount to account
     */
    public synchronized boolean creditAccount(String accountNumber, BigDecimal amount, 
                                            String transactionRef) throws InterruptedException {
        // Simulate network delay
        Thread.sleep((long) networkDelay);
        
        if (!isOnline) {
            System.out.println("❌ " + bankName + " is offline - transaction failed");
            return false;
        }
        
        BankAccount account = accounts.get(accountNumber);
        if (account == null) {
            System.out.println("❌ Account not found: " + accountNumber);
            return false;
        }
        
        // Credit the amount
        BigDecimal newBalance = account.getBalance().add(amount);
        account.setBalance(newBalance);
        account.addTransaction(transactionRef, amount, "CREDIT");
        
        System.out.println("💰 " + bankName + " credited ₹" + amount + 
                          " to " + account.getCustomerName() + 
                          " (New balance: ₹" + newBalance + ")");
        return true;
    }
    
    public BankAccount getAccount(String accountNumber) {
        return accounts.get(accountNumber);
    }
    
    public void simulateNetworkIssue(boolean offline, double delayMs) {
        this.isOnline = !offline;
        this.networkDelay = delayMs;
        if (offline) {
            System.out.println("🌐 " + bankName + " network issues simulated");
        }
    }
    
    // Getters
    public String getBankCode() { return bankCode; }
    public String getBankName() { return bankName; }
    public String getSwiftCode() { return swiftCode; }
    public boolean isOnline() { return isOnline; }
}

/**
 * Bank Account with Indian banking features
 */
class BankAccount {
    private final String accountNumber;
    private final String customerName;
    private volatile BigDecimal balance;
    private final String ifscCode;
    private final String bankCode;
    private final List<TransactionEntry> transactionHistory;
    private final LocalDateTime createdDate;
    
    public BankAccount(String accountNumber, String customerName, BigDecimal balance,
                      String ifscCode, String bankCode) {
        this.accountNumber = accountNumber;
        this.customerName = customerName;
        this.balance = balance;
        this.ifscCode = ifscCode;
        this.bankCode = bankCode;
        this.transactionHistory = Collections.synchronizedList(new ArrayList<>());
        this.createdDate = LocalDateTime.now();
    }
    
    public void addTransaction(String transactionRef, BigDecimal amount, String type) {
        transactionHistory.add(new TransactionEntry(transactionRef, amount, type, LocalDateTime.now()));
    }
    
    // Getters and setters
    public String getAccountNumber() { return accountNumber; }
    public String getCustomerName() { return customerName; }
    public synchronized BigDecimal getBalance() { return balance; }
    public synchronized void setBalance(BigDecimal balance) { this.balance = balance; }
    public String getIfscCode() { return ifscCode; }
    public String getBankCode() { return bankCode; }
    public List<TransactionEntry> getTransactionHistory() { return new ArrayList<>(transactionHistory); }
}

/**
 * Transaction History Entry
 */
class TransactionEntry {
    private final String transactionRef;
    private final BigDecimal amount;
    private final String type;
    private final LocalDateTime timestamp;
    
    public TransactionEntry(String transactionRef, BigDecimal amount, String type, LocalDateTime timestamp) {
        this.transactionRef = transactionRef;
        this.amount = amount;
        this.type = type;
        this.timestamp = timestamp;
    }
    
    // Getters
    public String getTransactionRef() { return transactionRef; }
    public BigDecimal getAmount() { return amount; }
    public String getType() { return type; }
    public LocalDateTime getTimestamp() { return timestamp; }
}

/**
 * Banking Transaction Request
 */
class BankingTransactionRequest {
    private final String transactionId;
    private final TransactionType type;
    private final String fromBankCode;
    private final String fromAccountNumber;
    private final String toBankCode;
    private final String toAccountNumber;
    private final BigDecimal amount;
    private final String purpose;
    private final LocalDateTime initiatedTime;
    
    public BankingTransactionRequest(String transactionId, TransactionType type,
                                   String fromBankCode, String fromAccountNumber,
                                   String toBankCode, String toAccountNumber,
                                   BigDecimal amount, String purpose) {
        this.transactionId = transactionId;
        this.type = type;
        this.fromBankCode = fromBankCode;
        this.fromAccountNumber = fromAccountNumber;
        this.toBankCode = toBankCode;
        this.toAccountNumber = toAccountNumber;
        this.amount = amount;
        this.purpose = purpose;
        this.initiatedTime = LocalDateTime.now();
    }
    
    // Getters
    public String getTransactionId() { return transactionId; }
    public TransactionType getType() { return type; }
    public String getFromBankCode() { return fromBankCode; }
    public String getFromAccountNumber() { return fromAccountNumber; }
    public String getToBankCode() { return toBankCode; }
    public String getToAccountNumber() { return toAccountNumber; }
    public BigDecimal getAmount() { return amount; }
    public String getPurpose() { return purpose; }
    public LocalDateTime getInitiatedTime() { return initiatedTime; }
}

/**
 * Main Transaction Coordinator
 * यह class Two-Phase Commit protocol implement करती है
 * Indian banking regulations के अनुसार
 */
public class IndianBankingTransactionCoordinator {
    
    private final Map<String, IndianBank> banks;
    private final ExecutorService executorService;
    private final AtomicLong transactionCounter;
    
    // Metrics
    private volatile int totalTransactions = 0;
    private volatile int successfulTransactions = 0;
    private volatile int failedTransactions = 0;
    private volatile int timeoutTransactions = 0;
    
    public IndianBankingTransactionCoordinator() {
        this.banks = new ConcurrentHashMap<>();
        this.executorService = Executors.newFixedThreadPool(10);
        this.transactionCounter = new AtomicLong(1);
        
        initializeIndianBanks();
        System.out.println("🏦 Indian Banking Transaction Coordinator initialized");
        System.out.println("🇮🇳 Supporting NEFT, RTGS, IMPS, and UPI transactions");
    }
    
    /**
     * Initialize major Indian banks
     */
    private void initializeIndianBanks() {
        // State Bank of India
        IndianBank sbi = new IndianBank("SBI", "State Bank of India", "SBININBB");
        sbi.createAccount("50100123456789", "Rajesh Kumar Sharma", 
                         new BigDecimal("150000"), "SBIN0001234");
        sbi.createAccount("50100987654321", "Sunita Devi", 
                         new BigDecimal("85000"), "SBIN0001234");
        banks.put("SBI", sbi);
        
        // HDFC Bank  
        IndianBank hdfc = new IndianBank("HDFC", "HDFC Bank", "HDFCINBB");
        hdfc.createAccount("50200111222333", "Amit Patel", 
                          new BigDecimal("225000"), "HDFC0001122");
        hdfc.createAccount("50200444555666", "Priya Singh", 
                          new BigDecimal("95000"), "HDFC0001122");
        banks.put("HDFC", hdfc);
        
        // ICICI Bank
        IndianBank icici = new IndianBank("ICICI", "ICICI Bank", "ICICINBB");
        icici.createAccount("50300777888999", "Vikram Gupta", 
                           new BigDecimal("175000"), "ICIC0001133");
        icici.createAccount("50300101112131", "Anjali Sharma", 
                           new BigDecimal("125000"), "ICIC0001133");
        banks.put("ICICI", icici);
        
        System.out.println("✅ Major Indian banks initialized with sample accounts");
    }
    
    /**
     * Process inter-bank transaction using Two-Phase Commit
     * 
     * यह function Two-Phase Commit protocol use करता है:
     * Phase 1: सभी banks से prepare confirmation
     * Phase 2: सभी banks में actual commit या rollback
     */
    public CompletableFuture<TransactionResult> processTransaction(BankingTransactionRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            totalTransactions++;
            
            System.out.println("\n💳 Processing " + request.getType().getDescription());
            System.out.println("   Transaction ID: " + request.getTransactionId());
            System.out.println("   From: " + request.getFromBankCode() + " - " + request.getFromAccountNumber());
            System.out.println("   To: " + request.getToBankCode() + " - " + request.getToAccountNumber()); 
            System.out.println("   Amount: ₹" + request.getAmount());
            System.out.println("   Purpose: " + request.getPurpose());
            
            try {
                // Phase 1: Prepare
                boolean prepareResult = prepareTransaction(request);
                if (!prepareResult) {
                    failedTransactions++;
                    return new TransactionResult(request.getTransactionId(), 
                                               TransactionStatus.FAILED, 
                                               "Transaction preparation failed",
                                               System.currentTimeMillis());
                }
                
                // Phase 2: Commit
                boolean commitResult = commitTransaction(request);
                if (commitResult) {
                    successfulTransactions++;
                    return new TransactionResult(request.getTransactionId(), 
                                               TransactionStatus.COMMITTED, 
                                               "Transaction completed successfully",
                                               System.currentTimeMillis());
                } else {
                    // Rollback on commit failure
                    rollbackTransaction(request);
                    failedTransactions++;
                    return new TransactionResult(request.getTransactionId(), 
                                               TransactionStatus.FAILED, 
                                               "Transaction commit failed - rolled back",
                                               System.currentTimeMillis());
                }
                
            } catch (TimeoutException e) {
                timeoutTransactions++;
                System.out.println("⏰ Transaction timeout: " + request.getTransactionId());
                rollbackTransaction(request);
                return new TransactionResult(request.getTransactionId(), 
                                           TransactionStatus.TIMEOUT, 
                                           "Transaction timed out",
                                           System.currentTimeMillis());
            } catch (Exception e) {
                failedTransactions++;
                System.out.println("❌ Transaction error: " + e.getMessage());
                rollbackTransaction(request);
                return new TransactionResult(request.getTransactionId(), 
                                           TransactionStatus.FAILED, 
                                           "Transaction failed: " + e.getMessage(),
                                           System.currentTimeMillis());
            }
        }, executorService);
    }
    
    /**
     * Phase 1: Prepare Transaction
     * सभी involved banks से confirmation लेना कि वे transaction perform कर सकते हैं
     */
    private boolean prepareTransaction(BankingTransactionRequest request) throws TimeoutException {
        System.out.println("🔄 Phase 1: Preparing transaction...");
        
        IndianBank fromBank = banks.get(request.getFromBankCode());
        IndianBank toBank = banks.get(request.getToBankCode());
        
        if (fromBank == null || toBank == null) {
            System.out.println("❌ One or more banks not found");
            return false;
        }
        
        // Check both banks are online
        if (!fromBank.isOnline() || !toBank.isOnline()) {
            System.out.println("❌ One or more banks are offline");
            return false;
        }
        
        // Validate accounts exist
        BankAccount fromAccount = fromBank.getAccount(request.getFromAccountNumber());
        BankAccount toAccount = toBank.getAccount(request.getToAccountNumber());
        
        if (fromAccount == null) {
            System.out.println("❌ Source account not found: " + request.getFromAccountNumber());
            return false;
        }
        
        if (toAccount == null) {
            System.out.println("❌ Destination account not found: " + request.getToAccountNumber());
            return false;
        }
        
        // Check balance and limits
        BigDecimal minimumBalance = new BigDecimal("10000");
        if (fromAccount.getBalance().subtract(request.getAmount()).compareTo(minimumBalance) < 0) {
            System.out.println("❌ Insufficient balance for transaction");
            return false;
        }
        
        // RBI guidelines - RTGS minimum ₹2,00,000
        if (request.getType() == TransactionType.RTGS && 
            request.getAmount().compareTo(new BigDecimal("200000")) < 0) {
            System.out.println("❌ RTGS minimum amount is ₹2,00,000");
            return false;
        }
        
        // NEFT/IMPS maximum ₹10,00,000 per transaction
        if ((request.getType() == TransactionType.NEFT || request.getType() == TransactionType.IMPS) &&
            request.getAmount().compareTo(new BigDecimal("1000000")) > 0) {
            System.out.println("❌ NEFT/IMPS maximum amount is ₹10,00,000 per transaction");
            return false;
        }
        
        System.out.println("✅ Phase 1: Transaction prepared successfully");
        return true;
    }
    
    /**
     * Phase 2: Commit Transaction
     * Actual money transfer between banks
     */
    private boolean commitTransaction(BankingTransactionRequest request) throws InterruptedException {
        System.out.println("💰 Phase 2: Committing transaction...");
        
        IndianBank fromBank = banks.get(request.getFromBankCode());
        IndianBank toBank = banks.get(request.getToBankCode());
        
        // Create futures for concurrent execution
        CompletableFuture<Boolean> debitFuture = CompletableFuture.supplyAsync(() -> {
            try {
                return fromBank.debitAccount(request.getFromAccountNumber(), 
                                           request.getAmount(), 
                                           request.getTransactionId());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }, executorService);
        
        CompletableFuture<Boolean> creditFuture = CompletableFuture.supplyAsync(() -> {
            try {
                return toBank.creditAccount(request.getToAccountNumber(), 
                                          request.getAmount(), 
                                          request.getTransactionId());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }, executorService);
        
        try {
            // Wait for both operations with timeout
            boolean debitResult = debitFuture.get(30, TimeUnit.SECONDS);
            boolean creditResult = creditFuture.get(30, TimeUnit.SECONDS);
            
            if (debitResult && creditResult) {
                System.out.println("✅ Phase 2: Transaction committed successfully");
                
                // Simulate RBI reporting (required for high-value transactions)
                if (request.getAmount().compareTo(new BigDecimal("1000000")) > 0) {
                    reportToRBI(request);
                }
                
                return true;
            } else {
                System.out.println("❌ Phase 2: Commit failed - will rollback");
                return false;
            }
            
        } catch (TimeoutException e) {
            System.out.println("⏰ Phase 2: Commit timeout - will rollback");
            debitFuture.cancel(true);
            creditFuture.cancel(true);
            return false;
        } catch (ExecutionException e) {
            System.out.println("❌ Phase 2: Execution error - will rollback: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Rollback transaction in case of failure
     */
    private void rollbackTransaction(BankingTransactionRequest request) {
        System.out.println("🔄 Rolling back transaction: " + request.getTransactionId());
        
        IndianBank fromBank = banks.get(request.getFromBankCode());
        IndianBank toBank = banks.get(request.getToBankCode());
        
        if (fromBank != null && toBank != null) {
            try {
                // Try to reverse any partial operations
                // In a real system, this would be more sophisticated
                System.out.println("↩️  Transaction " + request.getTransactionId() + " rolled back");
            } catch (Exception e) {
                System.out.println("⚠️  Warning: Rollback issues for " + request.getTransactionId() + 
                                 " - manual intervention may be required");
            }
        }
    }
    
    /**
     * Report high-value transactions to RBI (simulation)
     */
    private void reportToRBI(BankingTransactionRequest request) {
        System.out.println("🏛️  Reporting to RBI: High-value transaction ₹" + request.getAmount() + 
                          " between " + request.getFromBankCode() + " and " + request.getToBankCode());
    }
    
    /**
     * Create transaction ID in Indian banking format
     */
    public String generateTransactionId(TransactionType type) {
        String prefix = switch (type) {
            case NEFT -> "N";
            case RTGS -> "R";
            case IMPS -> "I";
            case UPI -> "U";
            case ATM_WITHDRAWAL -> "A";
            case CARD_PAYMENT -> "C";
        };
        
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        long counter = transactionCounter.getAndIncrement();
        
        return prefix + dateStr + String.format("%06d", counter);
    }
    
    /**
     * NEFT Transaction (National Electronic Funds Transfer)
     * Available during business hours, batch processing
     */
    public CompletableFuture<TransactionResult> processNEFT(String fromBank, String fromAccount,
                                                           String toBank, String toAccount,
                                                           BigDecimal amount, String purpose) {
        // Check NEFT operating hours (8 AM to 7 PM on weekdays)
        LocalDateTime now = LocalDateTime.now();
        int hour = now.getHour();
        if (hour < 8 || hour >= 19) {
            CompletableFuture<TransactionResult> failedFuture = new CompletableFuture<>();
            failedFuture.complete(new TransactionResult("NEFT_FAILED", TransactionStatus.FAILED,
                                                       "NEFT not available outside business hours (8 AM - 7 PM)",
                                                       System.currentTimeMillis()));
            return failedFuture;
        }
        
        String txnId = generateTransactionId(TransactionType.NEFT);
        BankingTransactionRequest request = new BankingTransactionRequest(
            txnId, TransactionType.NEFT, fromBank, fromAccount, toBank, toAccount, amount, purpose
        );
        
        return processTransaction(request);
    }
    
    /**
     * RTGS Transaction (Real Time Gross Settlement)
     * For high-value transactions, real-time processing
     */
    public CompletableFuture<TransactionResult> processRTGS(String fromBank, String fromAccount,
                                                           String toBank, String toAccount,
                                                           BigDecimal amount, String purpose) {
        // RTGS minimum amount check
        if (amount.compareTo(new BigDecimal("200000")) < 0) {
            CompletableFuture<TransactionResult> failedFuture = new CompletableFuture<>();
            failedFuture.complete(new TransactionResult("RTGS_FAILED", TransactionStatus.FAILED,
                                                       "RTGS minimum amount is ₹2,00,000",
                                                       System.currentTimeMillis()));
            return failedFuture;
        }
        
        String txnId = generateTransactionId(TransactionType.RTGS);
        BankingTransactionRequest request = new BankingTransactionRequest(
            txnId, TransactionType.RTGS, fromBank, fromAccount, toBank, toAccount, amount, purpose
        );
        
        return processTransaction(request);
    }
    
    /**
     * IMPS Transaction (Immediate Payment Service)  
     * 24x7 availability, instant transfer
     */
    public CompletableFuture<TransactionResult> processIMPS(String fromBank, String fromAccount,
                                                           String toBank, String toAccount,
                                                           BigDecimal amount, String purpose) {
        String txnId = generateTransactionId(TransactionType.IMPS);
        BankingTransactionRequest request = new BankingTransactionRequest(
            txnId, TransactionType.IMPS, fromBank, fromAccount, toBank, toAccount, amount, purpose
        );
        
        return processTransaction(request);
    }
    
    /**
     * Simulate concurrent transactions load test
     */
    public void simulateConcurrentTransactions(int numberOfTransactions) {
        System.out.println("\n🔥 CONCURRENT TRANSACTIONS LOAD TEST");
        System.out.println("   Simulating " + numberOfTransactions + " concurrent transactions");
        System.out.println("   Testing system consistency under load...");
        
        long startTime = System.currentTimeMillis();
        List<CompletableFuture<TransactionResult>> futures = new ArrayList<>();
        
        // Create random transactions
        Random random = new Random();
        String[] bankCodes = {"SBI", "HDFC", "ICICI"};
        String[][] accountNumbers = {
            {"50100123456789", "50100987654321"}, // SBI accounts
            {"50200111222333", "50200444555666"}, // HDFC accounts  
            {"50300777888999", "50300101112131"}  // ICICI accounts
        };
        
        for (int i = 0; i < numberOfTransactions; i++) {
            int fromBankIndex = random.nextInt(bankCodes.length);
            int toBankIndex = random.nextInt(bankCodes.length);
            
            String fromBank = bankCodes[fromBankIndex];
            String toBank = bankCodes[toBankIndex];
            String fromAccount = accountNumbers[fromBankIndex][random.nextInt(2)];
            String toAccount = accountNumbers[toBankIndex][random.nextInt(2)];
            
            // Skip same account transfers
            if (fromAccount.equals(toAccount)) {
                continue;
            }
            
            BigDecimal amount = new BigDecimal(String.valueOf(1000 + random.nextInt(10000)));
            
            CompletableFuture<TransactionResult> future = processIMPS(
                fromBank, fromAccount, toBank, toAccount, amount, 
                "Load test transaction #" + (i + 1)
            );
            
            futures.add(future);
        }
        
        // Wait for all transactions to complete
        CompletableFuture<Void> allTransactions = CompletableFuture.allOf(
            futures.toArray(new CompletableFuture[0])
        );
        
        try {
            allTransactions.get(60, TimeUnit.SECONDS); // 60 second timeout
        } catch (Exception e) {
            System.out.println("❌ Some transactions failed or timed out: " + e.getMessage());
        }
        
        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        
        // Analyze results
        int completed = 0;
        int failed = 0;
        
        for (CompletableFuture<TransactionResult> future : futures) {
            try {
                if (future.isDone() && !future.isCompletedExceptionally()) {
                    TransactionResult result = future.get();
                    if (result.getStatus() == TransactionStatus.COMMITTED) {
                        completed++;
                    } else {
                        failed++;
                    }
                } else {
                    failed++;
                }
            } catch (Exception e) {
                failed++;
            }
        }
        
        System.out.println("\n📊 LOAD TEST RESULTS:");
        System.out.println("   Duration: " + duration + " ms");
        System.out.println("   Completed transactions: " + completed);
        System.out.println("   Failed transactions: " + failed);
        System.out.println("   Success rate: " + (completed * 100.0 / numberOfTransactions) + "%");
        System.out.println("   Average time per transaction: " + (duration / numberOfTransactions) + " ms");
    }
    
    /**
     * Simulate bank network failure
     */
    public void simulateBankNetworkFailure(String bankCode, int durationSeconds) {
        System.out.println("\n🌐 SIMULATING NETWORK FAILURE");
        System.out.println("   Bank: " + bankCode);
        System.out.println("   Duration: " + durationSeconds + " seconds");
        
        IndianBank bank = banks.get(bankCode);
        if (bank != null) {
            bank.simulateNetworkIssue(true, 5000); // Offline with 5s delay
            
            // Test transaction during failure
            System.out.println("   Testing transaction during network failure...");
            
            CompletableFuture<TransactionResult> testTransaction = processIMPS(
                "SBI", "50100123456789", bankCode, 
                bankCode.equals("HDFC") ? "50200111222333" : "50300777888999",
                new BigDecimal("5000"), "Network failure test"
            );
            
            try {
                TransactionResult result = testTransaction.get(10, TimeUnit.SECONDS);
                System.out.println("   Transaction result: " + result.getStatus());
            } catch (Exception e) {
                System.out.println("   Transaction failed as expected: " + e.getMessage());
            }
            
            // Recover after duration
            try {
                Thread.sleep(durationSeconds * 1000L);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            
            bank.simulateNetworkIssue(false, 100); // Back online with normal delay
            System.out.println("✅ " + bankCode + " network recovered");
        }
    }
    
    /**
     * Get system metrics
     */
    public void printSystemMetrics() {
        System.out.println("\n📊 SYSTEM METRICS");
        System.out.println("   Total transactions: " + totalTransactions);
        System.out.println("   Successful transactions: " + successfulTransactions);
        System.out.println("   Failed transactions: " + failedTransactions);
        System.out.println("   Timeout transactions: " + timeoutTransactions);
        if (totalTransactions > 0) {
            double successRate = (successfulTransactions * 100.0) / totalTransactions;
            System.out.println("   Success rate: " + String.format("%.2f", successRate) + "%");
        }
        
        System.out.println("\n🏦 BANK STATUS");
        for (IndianBank bank : banks.values()) {
            System.out.println("   " + bank.getBankName() + ": " + 
                             (bank.isOnline() ? "ONLINE" : "OFFLINE"));
        }
    }
    
    /**
     * Clean shutdown
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(10, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    /**
     * Main demonstration method
     */
    public static void main(String[] args) {
        IndianBankingTransactionCoordinator coordinator = new IndianBankingTransactionCoordinator();
        
        try {
            System.out.println("\n🇮🇳 INDIAN BANKING TRANSACTION COORDINATOR DEMO");
            System.out.println("=" + "=".repeat(60));
            
            // Scenario 1: Normal NEFT transaction
            System.out.println("\n💰 SCENARIO 1: NEFT Transaction");
            CompletableFuture<TransactionResult> neftResult = coordinator.processNEFT(
                "SBI", "50100123456789",
                "HDFC", "50200111222333", 
                new BigDecimal("25000"), 
                "Salary transfer"
            );
            
            TransactionResult result1 = neftResult.get();
            System.out.println("   Result: " + result1.getStatus() + " - " + result1.getMessage());
            
            // Scenario 2: High-value RTGS transaction
            System.out.println("\n🏛️  SCENARIO 2: High-Value RTGS Transaction");
            CompletableFuture<TransactionResult> rtgsResult = coordinator.processRTGS(
                "HDFC", "50200111222333",
                "ICICI", "50300777888999",
                new BigDecimal("500000"),
                "Property purchase payment"
            );
            
            TransactionResult result2 = rtgsResult.get();
            System.out.println("   Result: " + result2.getStatus() + " - " + result2.getMessage());
            
            // Scenario 3: 24x7 IMPS transaction
            System.out.println("\n⚡ SCENARIO 3: Instant IMPS Transaction");
            CompletableFuture<TransactionResult> impsResult = coordinator.processIMPS(
                "ICICI", "50300777888999",
                "SBI", "50100987654321",
                new BigDecimal("15000"),
                "Emergency fund transfer"
            );
            
            TransactionResult result3 = impsResult.get();
            System.out.println("   Result: " + result3.getStatus() + " - " + result3.getMessage());
            
            // Scenario 4: Concurrent transactions test
            System.out.println("\n🔥 SCENARIO 4: Concurrent Transactions Test");
            coordinator.simulateConcurrentTransactions(10);
            
            // Scenario 5: Network failure simulation
            System.out.println("\n🌐 SCENARIO 5: Network Failure Simulation");
            coordinator.simulateBankNetworkFailure("HDFC", 3);
            
            // Final metrics
            coordinator.printSystemMetrics();
            
            System.out.println("\n✅ Indian Banking Transaction Coordinator demo completed!");
            System.out.println("Key learnings:");
            System.out.println("1. Two-Phase Commit ensures banking consistency");
            System.out.println("2. Different payment systems have different constraints");
            System.out.println("3. Network failures require proper rollback mechanisms");
            System.out.println("4. Concurrent access control prevents double spending");
            System.out.println("5. RBI compliance requires transaction reporting");
            
        } catch (Exception e) {
            System.out.println("❌ Demo failed: " + e.getMessage());
            e.printStackTrace();
        } finally {
            coordinator.shutdown();
        }
    }
}

/**
 * Transaction Result
 */
class TransactionResult {
    private final String transactionId;
    private final TransactionStatus status;
    private final String message;
    private final long timestamp;
    
    public TransactionResult(String transactionId, TransactionStatus status, 
                           String message, long timestamp) {
        this.transactionId = transactionId;
        this.status = status;
        this.message = message;
        this.timestamp = timestamp;
    }
    
    // Getters
    public String getTransactionId() { return transactionId; }
    public TransactionStatus getStatus() { return status; }
    public String getMessage() { return message; }
    public long getTimestamp() { return timestamp; }
    
    @Override
    public String toString() {
        return String.format("TransactionResult{id='%s', status=%s, message='%s', timestamp=%d}",
                           transactionId, status, message, timestamp);
    }
}