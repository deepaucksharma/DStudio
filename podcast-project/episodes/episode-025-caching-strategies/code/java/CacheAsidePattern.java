/**
 * Cache-Aside Pattern Implementation in Java
 * Indian Banking System के लिए cache-aside pattern
 * 
 * Key Features:
 * - Application manages cache
 * - Database remains authoritative source
 * - Cache miss handling
 * - HDFC Bank account management simulation
 * - Thread-safe operations
 * 
 * Use Cases:
 * - Bank account balance caching
 * - Customer profile caching
 * - Transaction history caching
 * - Mumbai branch network optimization
 * 
 * Author: Code Developer Agent for Hindi Tech Podcast
 * Episode: 25 - Caching Strategies (Cache-Aside Pattern)
 */

package com.hdfcbank.caching;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.concurrent.ThreadLocalRandom;
import java.util.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Bank Account model for HDFC Bank
 */
class BankAccount {
    private final String accountNumber;
    private final String customerName;
    private final String customerId;
    private BigDecimal balance;
    private final String accountType; // SAVINGS, CURRENT, FIXED_DEPOSIT
    private final String branchCode;
    private final String ifscCode;
    private boolean isActive;
    private LocalDateTime lastTransactionTime;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    public BankAccount(String accountNumber, String customerName, String customerId,
                      BigDecimal balance, String accountType, String branchCode, String ifscCode) {
        this.accountNumber = accountNumber;
        this.customerName = customerName;
        this.customerId = customerId;
        this.balance = balance;
        this.accountType = accountType;
        this.branchCode = branchCode;
        this.ifscCode = ifscCode;
        this.isActive = true;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.lastTransactionTime = LocalDateTime.now();
    }
    
    // Getters और setters
    public String getAccountNumber() { return accountNumber; }
    public String getCustomerName() { return customerName; }
    public String getCustomerId() { return customerId; }
    public BigDecimal getBalance() { return balance; }
    public String getAccountType() { return accountType; }
    public String getBranchCode() { return branchCode; }
    public String getIfscCode() { return ifscCode; }
    public boolean isActive() { return isActive; }
    public LocalDateTime getLastTransactionTime() { return lastTransactionTime; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    
    public void setBalance(BigDecimal balance) {
        this.balance = balance;
        this.updatedAt = LocalDateTime.now();
        this.lastTransactionTime = LocalDateTime.now();
    }
    
    public void setActive(boolean active) {
        this.isActive = active;
        this.updatedAt = LocalDateTime.now();
    }
    
    @Override
    public String toString() {
        return String.format("BankAccount{accountNumber='%s', customerName='%s', balance=%s, accountType='%s'}",
                accountNumber, customerName, balance, accountType);
    }
}

/**
 * Cache statistics for monitoring
 */
class CacheStatistics {
    private long hits = 0;
    private long misses = 0;
    private long sets = 0;
    private long evictions = 0;
    private long totalRequests = 0;
    
    public synchronized void recordHit() {
        hits++;
        totalRequests++;
    }
    
    public synchronized void recordMiss() {
        misses++;
        totalRequests++;
    }
    
    public synchronized void recordSet() {
        sets++;
    }
    
    public synchronized void recordEviction() {
        evictions++;
    }
    
    public synchronized double getHitRatio() {
        return totalRequests > 0 ? (double) hits / totalRequests : 0.0;
    }
    
    public long getHits() { return hits; }
    public long getMisses() { return misses; }
    public long getSets() { return sets; }
    public long getEvictions() { return evictions; }
    public long getTotalRequests() { return totalRequests; }
    
    @Override
    public String toString() {
        return String.format("CacheStats{hits=%d, misses=%d, hitRatio=%.2f%%, sets=%d, evictions=%d}",
                hits, misses, getHitRatio() * 100, sets, evictions);
    }
}

/**
 * LRU Cache implementation with TTL support
 */
class LRUCacheWithTTL<K, V> {
    private static class CacheEntry<V> {
        V value;
        long timestamp;
        long ttlMs;
        
        CacheEntry(V value, long ttlMs) {
            this.value = value;
            this.timestamp = System.currentTimeMillis();
            this.ttlMs = ttlMs;
        }
        
        boolean isExpired() {
            return (System.currentTimeMillis() - timestamp) > ttlMs;
        }
    }
    
    private final int maxSize;
    private final Map<K, CacheEntry<V>> cache;
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    private final CacheStatistics stats = new CacheStatistics();
    
    public LRUCacheWithTTL(int maxSize) {
        this.maxSize = maxSize;
        this.cache = new LinkedHashMap<K, CacheEntry<V>>(maxSize + 1, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, CacheEntry<V>> eldest) {
                boolean shouldRemove = size() > maxSize;
                if (shouldRemove) {
                    stats.recordEviction();
                }
                return shouldRemove;
            }
        };
    }
    
    public V get(K key) {
        lock.readLock().lock();
        try {
            CacheEntry<V> entry = cache.get(key);
            if (entry == null) {
                stats.recordMiss();
                return null;
            }
            
            if (entry.isExpired()) {
                cache.remove(key);
                stats.recordMiss();
                return null;
            }
            
            stats.recordHit();
            return entry.value;
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public void put(K key, V value, long ttlMs) {
        lock.writeLock().lock();
        try {
            cache.put(key, new CacheEntry<>(value, ttlMs));
            stats.recordSet();
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void remove(K key) {
        lock.writeLock().lock();
        try {
            cache.remove(key);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void clear() {
        lock.writeLock().lock();
        try {
            cache.clear();
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public int size() {
        lock.readLock().lock();
        try {
            return cache.size();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public CacheStatistics getStatistics() {
        return stats;
    }
}

/**
 * Simulated Database layer for HDFC Bank
 */
class HDFCBankDatabase {
    private final Map<String, BankAccount> accounts = new ConcurrentHashMap<>();
    private final Logger logger = Logger.getLogger(HDFCBankDatabase.class.getName());
    private long queryCount = 0;
    
    public HDFCBankDatabase() {
        initializeSampleData();
        logger.info("🏦 HDFC Bank Database initialized with sample accounts");
    }
    
    private void initializeSampleData() {
        // Mumbai branch accounts
        addAccount(new BankAccount("50100123456789", "राहुल शर्मा", "CUST001",
                new BigDecimal("50000.00"), "SAVINGS", "MUMBAI001", "HDFC0000123"));
        
        addAccount(new BankAccount("50100234567890", "प्रिया पटेल", "CUST002",
                new BigDecimal("125000.00"), "CURRENT", "MUMBAI002", "HDFC0000124"));
        
        addAccount(new BankAccount("50100345678901", "अमित कुमार", "CUST003",
                new BigDecimal("75000.00"), "SAVINGS", "MUMBAI003", "HDFC0000125"));
        
        // Delhi branch accounts
        addAccount(new BankAccount("50100456789012", "सुनीता गुप्ता", "CUST004",
                new BigDecimal("200000.00"), "CURRENT", "DELHI001", "HDFC0000126"));
        
        addAccount(new BankAccount("50100567890123", "विकास अग्रवाल", "CUST005",
                new BigDecimal("95000.00"), "SAVINGS", "DELHI002", "HDFC0000127"));
    }
    
    private void addAccount(BankAccount account) {
        accounts.put(account.getAccountNumber(), account);
    }
    
    /**
     * Simulate database query with latency
     */
    public BankAccount getAccount(String accountNumber) {
        // Simulate database query latency (200-500ms)
        try {
            Thread.sleep(200 + ThreadLocalRandom.current().nextInt(300));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        queryCount++;
        logger.info(String.format("💾 Database query for account: %s (Total queries: %d)", 
                                accountNumber, queryCount));
        
        return accounts.get(accountNumber);
    }
    
    /**
     * Update account in database
     */
    public boolean updateAccount(BankAccount account) {
        // Simulate database update latency
        try {
            Thread.sleep(150 + ThreadLocalRandom.current().nextInt(200));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        if (accounts.containsKey(account.getAccountNumber())) {
            accounts.put(account.getAccountNumber(), account);
            logger.info(String.format("💾 Database updated for account: %s", account.getAccountNumber()));
            return true;
        }
        return false;
    }
    
    /**
     * Get all accounts for a customer
     */
    public List<BankAccount> getAccountsByCustomerId(String customerId) {
        // Simulate complex query latency
        try {
            Thread.sleep(300 + ThreadLocalRandom.current().nextInt(400));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        queryCount++;
        logger.info(String.format("💾 Database query for customer accounts: %s (Total queries: %d)", 
                                customerId, queryCount));
        
        return accounts.values().stream()
                .filter(account -> account.getCustomerId().equals(customerId))
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
    
    public long getQueryCount() {
        return queryCount;
    }
}

/**
 * Cache-Aside Pattern implementation for HDFC Bank
 */
public class CacheAsidePattern {
    private final HDFCBankDatabase database;
    private final LRUCacheWithTTL<String, BankAccount> accountCache;
    private final LRUCacheWithTTL<String, List<BankAccount>> customerAccountsCache;
    private final Logger logger = Logger.getLogger(CacheAsidePattern.class.getName());
    
    // Cache TTL configuration (in milliseconds)
    private static final long ACCOUNT_TTL = 30 * 60 * 1000;        // 30 minutes
    private static final long CUSTOMER_ACCOUNTS_TTL = 15 * 60 * 1000; // 15 minutes
    
    public CacheAsidePattern() {
        this.database = new HDFCBankDatabase();
        this.accountCache = new LRUCacheWithTTL<>(1000);           // Max 1000 accounts
        this.customerAccountsCache = new LRUCacheWithTTL<>(500);   // Max 500 customer queries
        
        logger.info("🏦 HDFC Bank Cache-Aside System initialized");
        logger.info("📊 Account Cache: Max 1000 items, TTL 30 minutes");
        logger.info("👥 Customer Cache: Max 500 items, TTL 15 minutes");
    }
    
    /**
     * Get account using Cache-Aside pattern
     * पहले cache check करते हैं, cache miss पर database से fetch करते हैं
     */
    public BankAccount getAccount(String accountNumber) {
        logger.info(String.format("🔍 Getting account: %s", accountNumber));
        
        // Step 1: Try to get from cache
        BankAccount cachedAccount = accountCache.get(accountNumber);
        if (cachedAccount != null) {
            logger.info(String.format("✅ Cache hit for account: %s", accountNumber));
            return cachedAccount;
        }
        
        // Step 2: Cache miss - fetch from database
        logger.info(String.format("❌ Cache miss for account: %s - fetching from database", accountNumber));
        BankAccount account = database.getAccount(accountNumber);
        
        // Step 3: Store in cache for future requests
        if (account != null) {
            accountCache.put(accountNumber, account, ACCOUNT_TTL);
            logger.info(String.format("💾 Account cached: %s", accountNumber));
        }
        
        return account;
    }
    
    /**
     * Update account balance using Cache-Aside pattern
     * Database update के साथ cache invalidation
     */
    public boolean updateAccountBalance(String accountNumber, BigDecimal newBalance) {
        logger.info(String.format("💰 Updating balance for account: %s to ₹%s", accountNumber, newBalance));
        
        // Step 1: Get current account
        BankAccount account = getAccount(accountNumber);
        if (account == null) {
            logger.warning(String.format("❌ Account not found: %s", accountNumber));
            return false;
        }
        
        // Step 2: Update account balance
        account.setBalance(newBalance);
        
        // Step 3: Update database
        boolean updated = database.updateAccount(account);
        if (!updated) {
            logger.severe(String.format("❌ Database update failed for account: %s", accountNumber));
            return false;
        }
        
        // Step 4: Cache invalidation strategy
        // Option A: Invalidate cache (cache-aside pattern)
        accountCache.remove(accountNumber);
        logger.info(String.format("🗑️ Cache invalidated for account: %s", accountNumber));
        
        // Option B: Update cache (write-through pattern)
        // accountCache.put(accountNumber, account, ACCOUNT_TTL);
        // logger.info(String.format("♻️ Cache updated for account: %s", accountNumber));
        
        return true;
    }
    
    /**
     * Get all accounts for a customer using Cache-Aside pattern
     */
    public List<BankAccount> getAccountsByCustomerId(String customerId) {
        logger.info(String.format("👤 Getting accounts for customer: %s", customerId));
        
        // Step 1: Try to get from cache
        List<BankAccount> cachedAccounts = customerAccountsCache.get(customerId);
        if (cachedAccounts != null) {
            logger.info(String.format("✅ Cache hit for customer accounts: %s", customerId));
            return new ArrayList<>(cachedAccounts); // Return copy to prevent modification
        }
        
        // Step 2: Cache miss - fetch from database
        logger.info(String.format("❌ Cache miss for customer accounts: %s - fetching from database", customerId));
        List<BankAccount> accounts = database.getAccountsByCustomerId(customerId);
        
        // Step 3: Store in cache
        if (accounts != null && !accounts.isEmpty()) {
            customerAccountsCache.put(customerId, new ArrayList<>(accounts), CUSTOMER_ACCOUNTS_TTL);
            logger.info(String.format("💾 Customer accounts cached: %s (%d accounts)", customerId, accounts.size()));
        }
        
        return accounts;
    }
    
    /**
     * Transfer money between accounts with cache management
     */
    public boolean transferMoney(String fromAccount, String toAccount, BigDecimal amount) {
        logger.info(String.format("💸 Transfer: ₹%s from %s to %s", amount, fromAccount, toAccount));
        
        // Get both accounts
        BankAccount fromAcc = getAccount(fromAccount);
        BankAccount toAcc = getAccount(toAccount);
        
        if (fromAcc == null || toAcc == null) {
            logger.warning("❌ One or both accounts not found");
            return false;
        }
        
        // Check sufficient balance
        if (fromAcc.getBalance().compareTo(amount) < 0) {
            logger.warning(String.format("❌ Insufficient balance: ₹%s < ₹%s", fromAcc.getBalance(), amount));
            return false;
        }
        
        // Perform transfer
        BigDecimal newFromBalance = fromAcc.getBalance().subtract(amount);
        BigDecimal newToBalance = toAcc.getBalance().add(amount);
        
        // Update both accounts
        boolean fromUpdated = updateAccountBalance(fromAccount, newFromBalance);
        boolean toUpdated = updateAccountBalance(toAccount, newToBalance);
        
        if (fromUpdated && toUpdated) {
            logger.info(String.format("✅ Transfer completed: ₹%s from %s to %s", amount, fromAccount, toAccount));
            
            // Invalidate customer cache for both customers (if different)
            if (!fromAcc.getCustomerId().equals(toAcc.getCustomerId())) {
                customerAccountsCache.remove(fromAcc.getCustomerId());
                customerAccountsCache.remove(toAcc.getCustomerId());
                logger.info("🗑️ Customer caches invalidated for both customers");
            } else {
                customerAccountsCache.remove(fromAcc.getCustomerId());
                logger.info("🗑️ Customer cache invalidated");
            }
            
            return true;
        } else {
            logger.severe("❌ Transfer failed - database update error");
            return false;
        }
    }
    
    /**
     * Get comprehensive cache statistics
     */
    public void printCacheStatistics() {
        CacheStatistics accountStats = accountCache.getStatistics();
        CacheStatistics customerStats = customerAccountsCache.getStatistics();
        
        System.out.println("\n📊 Cache Performance Statistics");
        System.out.println("================================");
        System.out.println("🏦 Account Cache:");
        System.out.println("   " + accountStats);
        System.out.println(String.format("   Size: %d/1000 items", accountCache.size()));
        
        System.out.println("\n👥 Customer Accounts Cache:");
        System.out.println("   " + customerStats);
        System.out.println(String.format("   Size: %d/500 items", customerAccountsCache.size()));
        
        System.out.println(String.format("\n💾 Database Queries: %d", database.getQueryCount()));
        
        long totalRequests = accountStats.getTotalRequests() + customerStats.getTotalRequests();
        long totalHits = accountStats.getHits() + customerStats.getHits();
        double overallHitRatio = totalRequests > 0 ? (double) totalHits / totalRequests : 0.0;
        
        System.out.println(String.format("🎯 Overall Cache Hit Ratio: %.2f%%", overallHitRatio * 100));
        
        if (totalRequests > 0) {
            double cacheEfficiency = ((double)(totalRequests - database.getQueryCount()) / totalRequests) * 100;
            System.out.println(String.format("⚡ Cache Efficiency: %.2f%% (Requests served from cache)", cacheEfficiency));
        }
    }
    
    /**
     * Clear all caches
     */
    public void clearAllCaches() {
        accountCache.clear();
        customerAccountsCache.clear();
        logger.info("🧹 All caches cleared");
    }
    
    /**
     * Demo method for testing Cache-Aside pattern
     */
    public static void demonstrateCacheAside() {
        System.out.println("🏦 HDFC Bank Cache-Aside Pattern Demo");
        System.out.println("🇮🇳 Mumbai Banking System Simulation");
        System.out.println("=" + "=".repeat(50));
        
        CacheAsidePattern bankingSystem = new CacheAsidePattern();
        
        // Test accounts
        String[] testAccounts = {
            "50100123456789", // राहुल शर्मा - Mumbai
            "50100234567890", // प्रिया पटेल - Mumbai  
            "50100345678901", // अमित कुमार - Mumbai
            "50100456789012", // सुनीता गुप्ता - Delhi
            "50100567890123"  // विकास अग्रवाल - Delhi
        };
        
        System.out.println("\n1. First Access (Cold Cache)");
        System.out.println("-".repeat(35));
        
        // First access - cache is cold
        for (String accountNumber : testAccounts) {
            long startTime = System.currentTimeMillis();
            BankAccount account = bankingSystem.getAccount(accountNumber);
            long accessTime = System.currentTimeMillis() - startTime;
            
            if (account != null) {
                System.out.printf("   ✅ %s: %s - ₹%s (%dms)%n", 
                    account.getAccountNumber(), account.getCustomerName(), 
                    account.getBalance(), accessTime);
            }
        }
        
        System.out.println("\n2. Second Access (Warm Cache)");
        System.out.println("-".repeat(35));
        
        // Second access - should hit cache
        for (String accountNumber : testAccounts) {
            long startTime = System.currentTimeMillis();
            BankAccount account = bankingSystem.getAccount(accountNumber);
            long accessTime = System.currentTimeMillis() - startTime;
            
            if (account != null) {
                System.out.printf("   ⚡ %s: %s - ₹%s (%dms - From Cache!)%n", 
                    account.getAccountNumber(), account.getCustomerName(), 
                    account.getBalance(), accessTime);
            }
        }
        
        System.out.println("\n3. Account Balance Updates");
        System.out.println("-".repeat(30));
        
        // Test balance updates with cache invalidation
        System.out.println("💰 Updating राहुल शर्मा's account balance...");
        boolean updated = bankingSystem.updateAccountBalance("50100123456789", new BigDecimal("55000.00"));
        System.out.println("   Update status: " + (updated ? "✅ Success" : "❌ Failed"));
        
        // Fetch again to show cache miss and fresh data
        System.out.println("🔍 Fetching updated balance...");
        BankAccount updatedAccount = bankingSystem.getAccount("50100123456789");
        System.out.printf("   Updated balance: ₹%s%n", updatedAccount.getBalance());
        
        System.out.println("\n4. Money Transfer Test");
        System.out.println("-".repeat(25));
        
        // Test money transfer
        System.out.println("💸 Transfer ₹10,000 from प्रिया पटेल to अमित कुमार...");
        boolean transferSuccess = bankingSystem.transferMoney(
            "50100234567890", "50100345678901", new BigDecimal("10000.00"));
        System.out.println("   Transfer status: " + (transferSuccess ? "✅ Success" : "❌ Failed"));
        
        // Check updated balances
        BankAccount priya = bankingSystem.getAccount("50100234567890");
        BankAccount amit = bankingSystem.getAccount("50100345678901");
        System.out.printf("   प्रिया पटेल balance: ₹%s%n", priya.getBalance());
        System.out.printf("   अमित कुमार balance: ₹%s%n", amit.getBalance());
        
        System.out.println("\n5. Customer Accounts Query");
        System.out.println("-".repeat(30));
        
        // Test customer accounts caching
        System.out.println("👤 Getting all accounts for CUST001 (राहुल शर्मा)...");
        long startTime = System.currentTimeMillis();
        List<BankAccount> customerAccounts = bankingSystem.getAccountsByCustomerId("CUST001");
        long queryTime = System.currentTimeMillis() - startTime;
        
        System.out.printf("   Found %d accounts (%dms)%n", customerAccounts.size(), queryTime);
        for (BankAccount account : customerAccounts) {
            System.out.printf("   📋 %s: %s - ₹%s%n", 
                account.getAccountNumber(), account.getAccountType(), account.getBalance());
        }
        
        // Query again to test cache hit
        System.out.println("👤 Getting same customer accounts again (should hit cache)...");
        startTime = System.currentTimeMillis();
        customerAccounts = bankingSystem.getAccountsByCustomerId("CUST001");
        queryTime = System.currentTimeMillis() - startTime;
        System.out.printf("   Found %d accounts (%dms - From Cache!)%n", customerAccounts.size(), queryTime);
        
        // Print final statistics
        bankingSystem.printCacheStatistics();
        
        System.out.println("\n" + "=".repeat(51));
        System.out.println("🎉 Cache-Aside Pattern Demo Completed!");
        System.out.println("💡 Key Benefits:");
        System.out.println("   - Application controls cache logic");
        System.out.println("   - Database remains single source of truth");
        System.out.println("   - Flexible cache invalidation strategies");
        System.out.println("   - Good performance for read-heavy workloads");
        System.out.println("   - Easy to implement and understand");
        
        System.out.println("\n⚠️ Important Considerations:");
        System.out.println("   - Cache consistency must be managed by application");
        System.out.println("   - Risk of stale data if invalidation is not proper");
        System.out.println("   - Latency for cache misses");
        System.out.println("   - Need proper TTL configuration");
    }
    
    /**
     * Main method to run the demo
     */
    public static void main(String[] args) {
        // Set logging level
        Logger.getLogger("").setLevel(Level.INFO);
        
        demonstrateCacheAside();
    }
}