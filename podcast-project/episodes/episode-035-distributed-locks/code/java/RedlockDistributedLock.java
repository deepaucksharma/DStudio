/**
 * Redis Redlock Implementation in Java
 * ===================================
 * 
 * Production-ready Redlock algorithm implementation for distributed locking.
 * Used by companies like Twitter, Pinterest for critical resource coordination.
 * 
 * Mumbai Context: यह multiple railway stations पर एक साथ ticket booking
 * control करने जैसा है - majority stations में lock मिले तो booking confirm!
 * 
 * Real-world usage:
 * - Critical section protection in microservices
 * - Leader election in distributed systems  
 * - Resource allocation coordination
 * - Database migration locks
 */

package com.distributedlocks.redlock;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;
import redis.clients.jedis.exceptions.JedisException;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Logger;
import java.util.logging.Level;

public class RedlockDistributedLock {
    
    private static final Logger LOGGER = Logger.getLogger(RedlockDistributedLock.class.getName());
    
    private final List<JedisPool> redisInstances;
    private final int quorum;
    private final int retryCount;
    private final double clockDriftFactor;
    private final ExecutorService executor;
    
    // Lock statistics
    private final AtomicInteger locksAcquired = new AtomicInteger(0);
    private final AtomicInteger locksFailed = new AtomicInteger(0);
    private final AtomicInteger locksReleased = new AtomicInteger(0);
    
    public RedlockDistributedLock(List<RedisInstance> instances) {
        this(instances, 3, 0.01);
    }
    
    public RedlockDistributedLock(List<RedisInstance> instances, int retryCount, double clockDriftFactor) {
        this.redisInstances = new ArrayList<>();
        this.retryCount = retryCount;
        this.clockDriftFactor = clockDriftFactor;
        this.quorum = instances.size() / 2 + 1;
        
        // Initialize Redis connection pools
        for (RedisInstance instance : instances) {
            JedisPoolConfig poolConfig = new JedisPoolConfig();
            poolConfig.setMaxTotal(10);
            poolConfig.setMaxIdle(5);
            poolConfig.setMinIdle(1);
            poolConfig.setTestOnBorrow(true);
            poolConfig.setTestOnReturn(true);
            poolConfig.setTestWhileIdle(true);
            poolConfig.setBlockWhenExhausted(true);
            poolConfig.setMaxWaitMillis(2000);
            
            JedisPool pool = new JedisPool(poolConfig, 
                instance.getHost(), 
                instance.getPort(), 
                1000, // 1 second timeout
                instance.getPassword(),
                instance.getDatabase()
            );
            
            this.redisInstances.add(pool);
        }
        
        // Thread pool for parallel Redis operations
        this.executor = Executors.newFixedThreadPool(instances.size());
        
        LOGGER.info(String.format("✅ Redlock initialized with %d instances (quorum: %d)", 
            instances.size(), this.quorum));
    }
    
    /**
     * Acquire distributed lock using Redlock algorithm
     * 
     * @param resource Resource name to lock
     * @param ttlMillis Time-to-live in milliseconds
     * @return Lock information if successful, null otherwise
     */
    public LockInfo acquireLock(String resource, long ttlMillis) {
        return acquireLock(resource, ttlMillis, 10000); // 10 second timeout
    }
    
    public LockInfo acquireLock(String resource, long ttlMillis, long timeoutMillis) {
        String lockKey = "lock:" + resource;
        String lockValue = generateLockValue();
        
        long startTime = System.currentTimeMillis();
        long deadline = startTime + timeoutMillis;
        
        for (int attempt = 0; attempt < retryCount && System.currentTimeMillis() < deadline; attempt++) {
            long attemptStartTime = System.currentTimeMillis();
            
            // Try to acquire lock on all Redis instances in parallel
            List<Future<Boolean>> futures = new ArrayList<>();
            
            for (JedisPool pool : redisInstances) {
                Future<Boolean> future = executor.submit(() -> {
                    try (Jedis jedis = pool.getResource()) {
                        // SET key value NX PX ttl
                        String result = jedis.set(lockKey, lockValue, "NX", "PX", ttlMillis);
                        return "OK".equals(result);
                    } catch (JedisException e) {
                        LOGGER.log(Level.WARNING, "Redis operation failed", e);
                        return false;
                    }
                });
                futures.add(future);
            }
            
            // Collect results
            int locksAcquiredCount = 0;
            for (Future<Boolean> future : futures) {
                try {
                    if (future.get(100, TimeUnit.MILLISECONDS)) {
                        locksAcquiredCount++;
                    }
                } catch (InterruptedException | ExecutionException | TimeoutException e) {
                    LOGGER.log(Level.WARNING, "Failed to get lock result", e);
                }
            }
            
            // Calculate elapsed time and drift
            long elapsedTime = System.currentTimeMillis() - attemptStartTime;
            long drift = (long) (ttlMillis * clockDriftFactor) + 2;
            long validityTime = ttlMillis - elapsedTime - drift;
            
            // Check if we have majority and sufficient validity time
            if (locksAcquiredCount >= quorum && validityTime > 0) {
                LockInfo lockInfo = new LockInfo(
                    resource,
                    lockValue,
                    validityTime,
                    locksAcquiredCount,
                    Instant.now()
                );
                
                this.locksAcquired.incrementAndGet();
                LOGGER.info(String.format("🔒 Redlock acquired: %s (instances: %d/%d, validity: %dms)",
                    resource, locksAcquiredCount, redisInstances.size(), validityTime));
                
                return lockInfo;
            } else {
                // Failed to acquire majority - release acquired locks
                releaseLockInstances(lockKey, lockValue);
                LOGGER.warning(String.format("❌ Failed to acquire Redlock: %s (instances: %d/%d)",
                    resource, locksAcquiredCount, redisInstances.size()));
            }
            
            // Wait before retry with jitter
            if (attempt < retryCount - 1) {
                try {
                    Thread.sleep(new Random().nextInt(100) + 50); // 50-150ms
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
        
        this.locksFailed.incrementAndGet();
        return null;
    }
    
    /**
     * Release distributed lock
     * 
     * @param lockInfo Lock information from acquireLock
     * @return true if lock was released successfully
     */
    public boolean releaseLock(LockInfo lockInfo) {
        String lockKey = "lock:" + lockInfo.getResource();
        String lockValue = lockInfo.getValue();
        
        boolean released = releaseLockInstances(lockKey, lockValue);
        
        if (released) {
            this.locksReleased.incrementAndGet();
            LOGGER.info(String.format("🔓 Redlock released: %s", lockInfo.getResource()));
        }
        
        return released;
    }
    
    private boolean releaseLockInstances(String lockKey, String lockValue) {
        // Lua script for atomic check-and-delete
        String unlockScript = 
            "if redis.call('get', KEYS[1]) == ARGV[1] then " +
            "    return redis.call('del', KEYS[1]) " +
            "else " +
            "    return 0 " +
            "end";
        
        List<Future<Boolean>> futures = new ArrayList<>();
        
        for (JedisPool pool : redisInstances) {
            Future<Boolean> future = executor.submit(() -> {
                try (Jedis jedis = pool.getResource()) {
                    Object result = jedis.eval(unlockScript, 1, lockKey, lockValue);
                    return Long.valueOf(1).equals(result);
                } catch (JedisException e) {
                    LOGGER.log(Level.WARNING, "Redis unlock failed", e);
                    return false;
                }
            });
            futures.add(future);
        }
        
        int unlockedCount = 0;
        for (Future<Boolean> future : futures) {
            try {
                if (future.get(100, TimeUnit.MILLISECONDS)) {
                    unlockedCount++;
                }
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                LOGGER.log(Level.WARNING, "Failed to get unlock result", e);
            }
        }
        
        return unlockedCount > 0;
    }
    
    private String generateLockValue() {
        return UUID.randomUUID().toString() + ":" + System.currentTimeMillis();
    }
    
    /**
     * Get lock statistics
     */
    public LockStatistics getStatistics() {
        return new LockStatistics(
            locksAcquired.get(),
            locksFailed.get(),
            locksReleased.get()
        );
    }
    
    /**
     * Shutdown the lock manager
     */
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
        
        // Close Redis pools
        for (JedisPool pool : redisInstances) {
            pool.close();
        }
        
        LOGGER.info("🔌 Redlock manager shutdown completed");
    }
    
    // Helper classes
    public static class RedisInstance {
        private final String host;
        private final int port;
        private final String password;
        private final int database;
        
        public RedisInstance(String host, int port) {
            this(host, port, null, 0);
        }
        
        public RedisInstance(String host, int port, String password, int database) {
            this.host = host;
            this.port = port;
            this.password = password;
            this.database = database;
        }
        
        // Getters
        public String getHost() { return host; }
        public int getPort() { return port; }
        public String getPassword() { return password; }
        public int getDatabase() { return database; }
    }
    
    public static class LockInfo {
        private final String resource;
        private final String value;
        private final long validityTime;
        private final int lockedInstances;
        private final Instant acquiredAt;
        
        public LockInfo(String resource, String value, long validityTime, 
                       int lockedInstances, Instant acquiredAt) {
            this.resource = resource;
            this.value = value;
            this.validityTime = validityTime;
            this.lockedInstances = lockedInstances;
            this.acquiredAt = acquiredAt;
        }
        
        // Getters
        public String getResource() { return resource; }
        public String getValue() { return value; }
        public long getValidityTime() { return validityTime; }
        public int getLockedInstances() { return lockedInstances; }
        public Instant getAcquiredAt() { return acquiredAt; }
        
        public boolean isValid() {
            return System.currentTimeMillis() < (acquiredAt.toEpochMilli() + validityTime);
        }
    }
    
    public static class LockStatistics {
        private final int acquired;
        private final int failed;
        private final int released;
        
        public LockStatistics(int acquired, int failed, int released) {
            this.acquired = acquired;
            this.failed = failed;
            this.released = released;
        }
        
        public int getAcquired() { return acquired; }
        public int getFailed() { return failed; }
        public int getReleased() { return released; }
        public double getSuccessRate() {
            int total = acquired + failed;
            return total == 0 ? 0.0 : (double) acquired / total * 100.0;
        }
    }
}

/**
 * HDFC Bank Transaction Coordinator using Redlock
 * ==============================================
 * 
 * Mumbai Story: HDFC Bank में हजारों branches हैं और UPI transactions के लिए
 * coordination की जरुरत होती है. Redlock ensures कि duplicate transactions न हों!
 */
class HDFCTransactionCoordinator {
    
    private static final Logger LOGGER = Logger.getLogger(HDFCTransactionCoordinator.class.getName());
    
    private final RedlockDistributedLock redlock;
    private final Map<String, Double> accountBalances;
    private final List<TransactionRecord> transactionHistory;
    private final AtomicInteger transactionCounter = new AtomicInteger(0);
    
    // Transaction statistics
    private final AtomicInteger totalTransactions = new AtomicInteger(0);
    private final AtomicInteger successfulTransactions = new AtomicInteger(0);
    private final AtomicInteger failedTransactions = new AtomicInteger(0);
    private final AtomicInteger duplicatesPrevented = new AtomicInteger(0);
    
    public HDFCTransactionCoordinator(RedlockDistributedLock redlock) {
        this.redlock = redlock;
        this.accountBalances = new ConcurrentHashMap<>();
        this.transactionHistory = Collections.synchronizedList(new ArrayList<>());
        
        // Initialize sample accounts
        initializeAccounts();
        
        LOGGER.info("🏦 HDFC Transaction Coordinator initialized");
    }
    
    private void initializeAccounts() {
        // Sample HDFC bank accounts with initial balances
        String[] accountNumbers = {
            "HDFC001234567890", "HDFC001234567891", "HDFC001234567892",
            "HDFC001234567893", "HDFC001234567894", "HDFC001234567895",
            "HDFC001234567896", "HDFC001234567897", "HDFC001234567898",
            "HDFC001234567899"
        };
        
        for (String account : accountNumbers) {
            accountBalances.put(account, 100000.0); // ₹1,00,000 initial balance
        }
    }
    
    /**
     * Process UPI transaction with distributed locking
     */
    public TransactionResult processUPITransaction(String transactionId, String fromAccount, 
                                                  String toAccount, double amount) {
        totalTransactions.incrementAndGet();
        
        // Lock for duplicate prevention
        String duplicateLockResource = "upi_transaction_" + transactionId;
        RedlockDistributedLock.LockInfo duplicateLock = redlock.acquireLock(duplicateLockResource, 30000);
        
        if (duplicateLock == null) {
            failedTransactions.incrementAndGet();
            return new TransactionResult(false, "Transaction processing busy - please retry", 
                "DUPLICATE_LOCK_FAILED");
        }
        
        try {
            // Check for duplicate transaction
            boolean isDuplicate = transactionHistory.stream()
                .anyMatch(t -> t.getTransactionId().equals(transactionId));
            
            if (isDuplicate) {
                duplicatesPrevented.incrementAndGet();
                return new TransactionResult(false, "Duplicate transaction detected", 
                    "DUPLICATE_TRANSACTION");
            }
            
            // Lock both accounts in consistent order to prevent deadlock
            List<String> accountsToLock = Arrays.asList(fromAccount, toAccount);
            Collections.sort(accountsToLock);
            
            String balanceLockResource = "balance_" + String.join("_", accountsToLock);
            RedlockDistributedLock.LockInfo balanceLock = redlock.acquireLock(balanceLockResource, 20000);
            
            if (balanceLock == null) {
                failedTransactions.incrementAndGet();
                return new TransactionResult(false, "Balance update busy - please retry", 
                    "BALANCE_LOCK_FAILED");
            }
            
            try {
                // Validate accounts
                if (!accountBalances.containsKey(fromAccount) || !accountBalances.containsKey(toAccount)) {
                    failedTransactions.incrementAndGet();
                    return new TransactionResult(false, "Invalid account number", "INVALID_ACCOUNT");
                }
                
                // Check balance
                double fromBalance = accountBalances.get(fromAccount);
                if (fromBalance < amount) {
                    failedTransactions.incrementAndGet();
                    return new TransactionResult(false, 
                        String.format("Insufficient balance. Available: ₹%.2f", fromBalance),
                        "INSUFFICIENT_BALANCE");
                }
                
                // Process transaction
                accountBalances.put(fromAccount, fromBalance - amount);
                accountBalances.put(toAccount, accountBalances.get(toAccount) + amount);
                
                // Record transaction
                TransactionRecord record = new TransactionRecord(
                    transactionId,
                    fromAccount,
                    toAccount,
                    amount,
                    Instant.now(),
                    "SUCCESS"
                );
                
                transactionHistory.add(record);
                successfulTransactions.incrementAndGet();
                
                LOGGER.info(String.format("💰 UPI Transaction processed: %s - ₹%.2f (%s → %s)",
                    transactionId, amount, fromAccount.substring(4, 10) + "***", 
                    toAccount.substring(4, 10) + "***"));
                
                return new TransactionResult(true, 
                    String.format("Transaction successful - ₹%.2f transferred", amount),
                    record);
                    
            } finally {
                redlock.releaseLock(balanceLock);
            }
            
        } finally {
            redlock.releaseLock(duplicateLock);
        }
    }
    
    /**
     * Get account balance safely
     */
    public double getAccountBalance(String accountNumber) {
        String lockResource = "balance_read_" + accountNumber;
        RedlockDistributedLock.LockInfo lock = redlock.acquireLock(lockResource, 5000);
        
        try {
            return accountBalances.getOrDefault(accountNumber, 0.0);
        } finally {
            if (lock != null) {
                redlock.releaseLock(lock);
            }
        }
    }
    
    /**
     * Get transaction statistics
     */
    public TransactionStatistics getStatistics() {
        int total = totalTransactions.get();
        int successful = successfulTransactions.get();
        int failed = failedTransactions.get();
        int duplicates = duplicatesPrevented.get();
        
        double successRate = total == 0 ? 0.0 : (double) successful / total * 100.0;
        
        return new TransactionStatistics(total, successful, failed, duplicates, successRate);
    }
    
    // Helper classes
    public static class TransactionRecord {
        private final String transactionId;
        private final String fromAccount;
        private final String toAccount;
        private final double amount;
        private final Instant timestamp;
        private final String status;
        
        public TransactionRecord(String transactionId, String fromAccount, String toAccount,
                               double amount, Instant timestamp, String status) {
            this.transactionId = transactionId;
            this.fromAccount = fromAccount;
            this.toAccount = toAccount;
            this.amount = amount;
            this.timestamp = timestamp;
            this.status = status;
        }
        
        // Getters
        public String getTransactionId() { return transactionId; }
        public String getFromAccount() { return fromAccount; }
        public String getToAccount() { return toAccount; }
        public double getAmount() { return amount; }
        public Instant getTimestamp() { return timestamp; }
        public String getStatus() { return status; }
    }
    
    public static class TransactionResult {
        private final boolean success;
        private final String message;
        private final String errorCode;
        private final TransactionRecord record;
        
        public TransactionResult(boolean success, String message, String errorCode) {
            this.success = success;
            this.message = message;
            this.errorCode = errorCode;
            this.record = null;
        }
        
        public TransactionResult(boolean success, String message, TransactionRecord record) {
            this.success = success;
            this.message = message;
            this.errorCode = null;
            this.record = record;
        }
        
        // Getters
        public boolean isSuccess() { return success; }
        public String getMessage() { return message; }
        public String getErrorCode() { return errorCode; }
        public TransactionRecord getRecord() { return record; }
    }
    
    public static class TransactionStatistics {
        private final int total;
        private final int successful;
        private final int failed;
        private final int duplicatesPrevented;
        private final double successRate;
        
        public TransactionStatistics(int total, int successful, int failed, 
                                   int duplicatesPrevented, double successRate) {
            this.total = total;
            this.successful = successful;
            this.failed = failed;
            this.duplicatesPrevented = duplicatesPrevented;
            this.successRate = successRate;
        }
        
        // Getters
        public int getTotal() { return total; }
        public int getSuccessful() { return successful; }
        public int getFailed() { return failed; }
        public int getDuplicatesPrevented() { return duplicatesPrevented; }
        public double getSuccessRate() { return successRate; }
    }
}

/**
 * Demo class to test HDFC UPI transaction processing
 */
class HDFCUPIDemo {
    
    public static void main(String[] args) throws InterruptedException {
        Logger.getGlobal().setLevel(Level.INFO);
        
        // Setup Redis instances (in production, these would be on different servers)
        List<RedlockDistributedLock.RedisInstance> instances = Arrays.asList(
            new RedlockDistributedLock.RedisInstance("localhost", 6379, null, 0),
            new RedlockDistributedLock.RedisInstance("localhost", 6379, null, 1),
            new RedlockDistributedLock.RedisInstance("localhost", 6379, null, 2)
        );
        
        RedlockDistributedLock redlock = new RedlockDistributedLock(instances);
        HDFCTransactionCoordinator coordinator = new HDFCTransactionCoordinator(redlock);
        
        // Simulate concurrent UPI transactions
        simulateUPITransactions(coordinator);
        
        // Cleanup
        redlock.shutdown();
    }
    
    private static void simulateUPITransactions(HDFCTransactionCoordinator coordinator) 
            throws InterruptedException {
        
        System.out.println("🏦 Starting HDFC UPI transaction simulation...\n");
        
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(20);
        
        // Sample accounts
        String[] accounts = {
            "HDFC001234567890", "HDFC001234567891", "HDFC001234567892", 
            "HDFC001234567893", "HDFC001234567894"
        };
        
        Random random = new Random();
        
        for (int i = 0; i < 20; i++) {
            final int txnNum = i + 1;
            
            executor.submit(() -> {
                try {
                    String transactionId = String.format("UPI%08d%04d", 
                        System.currentTimeMillis() % 100000000, txnNum);
                    
                    String fromAccount = accounts[random.nextInt(accounts.length)];
                    String toAccount = accounts[random.nextInt(accounts.length)];
                    
                    // Ensure different accounts
                    while (fromAccount.equals(toAccount)) {
                        toAccount = accounts[random.nextInt(accounts.length)];
                    }
                    
                    double amount = 100 + random.nextDouble() * 900; // ₹100-1000
                    
                    HDFCTransactionCoordinator.TransactionResult result = 
                        coordinator.processUPITransaction(transactionId, fromAccount, toAccount, amount);
                    
                    System.out.println(String.format("%s Transaction %s: %s", 
                        result.isSuccess() ? "✅" : "❌", transactionId, result.getMessage()));
                        
                } catch (Exception e) {
                    System.err.println("Transaction failed: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
            
            Thread.sleep(50); // Small delay between transactions
        }
        
        latch.await(30, TimeUnit.SECONDS);
        executor.shutdown();
        
        // Show final statistics
        HDFCTransactionCoordinator.TransactionStatistics stats = coordinator.getStatistics();
        RedlockDistributedLock.LockStatistics lockStats = redlock.getStatistics();
        
        System.out.println("\n📊 HDFC UPI Transaction Results:");
        System.out.println("Total transactions: " + stats.getTotal());
        System.out.println("Successful transactions: " + stats.getSuccessful());
        System.out.println("Failed transactions: " + stats.getFailed());
        System.out.println("Duplicates prevented: " + stats.getDuplicatesPrevented());
        System.out.println("Success rate: " + String.format("%.2f%%", stats.getSuccessRate()));
        
        System.out.println("\n🔒 Redlock Statistics:");
        System.out.println("Locks acquired: " + lockStats.getAcquired());
        System.out.println("Lock failures: " + lockStats.getFailed());
        System.out.println("Locks released: " + lockStats.getReleased());
        System.out.println("Lock success rate: " + String.format("%.2f%%", lockStats.getSuccessRate()));
        
        // Show sample balances
        System.out.println("\n💰 Sample account balances:");
        String[] sampleAccounts = {"HDFC001234567890", "HDFC001234567891", "HDFC001234567892"};
        for (String account : sampleAccounts) {
            double balance = coordinator.getAccountBalance(account);
            System.out.println(String.format("%s: ₹%.2f", account, balance));
        }
    }
}