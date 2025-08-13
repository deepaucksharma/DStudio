/**
 * Paytm Real-time Transaction Analytics
 * Episode 43: Real-time Analytics at Scale
 * 
 * यह Java example Paytm जैसे payment platform का real-time transaction analytics दिखाता है
 * UPI payments, wallet transactions, और fraud detection के लिए production-ready system।
 * 
 * Production Stats:
 * - Paytm: 2+ billion transactions monthly
 * - Peak TPS: 10,000+ during festivals
 * - Fraud detection latency: <100ms
 * - Success rate: 98.5%+
 */

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

// Data Models
class PaymentTransaction {
    private final String transactionId;
    private final String senderId;
    private final String receiverId;
    private final double amount;
    private final String paymentMethod; // UPI, WALLET, CARD
    private final String bank;
    private final LocalDateTime timestamp;
    private final TransactionStatus status;
    private final String location;
    private final Map<String, Object> metadata;
    
    public enum TransactionStatus {
        INITIATED, PROCESSING, SUCCESS, FAILED, FRAUD_SUSPECTED
    }
    
    public PaymentTransaction(String transactionId, String senderId, String receiverId, 
                            double amount, String paymentMethod, String bank, 
                            LocalDateTime timestamp, TransactionStatus status, 
                            String location, Map<String, Object> metadata) {
        this.transactionId = transactionId;
        this.senderId = senderId;
        this.receiverId = receiverId;
        this.amount = amount;
        this.paymentMethod = paymentMethod;
        this.bank = bank;
        this.timestamp = timestamp;
        this.status = status;
        this.location = location;
        this.metadata = metadata;
    }
    
    // Getters
    public String getTransactionId() { return transactionId; }
    public String getSenderId() { return senderId; }
    public String getReceiverId() { return receiverId; }
    public double getAmount() { return amount; }
    public String getPaymentMethod() { return paymentMethod; }
    public String getBank() { return bank; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public TransactionStatus getStatus() { return status; }
    public String getLocation() { return location; }
    public Map<String, Object> getMetadata() { return metadata; }
}

class RealTimeMetrics {
    private final AtomicLong totalTransactions = new AtomicLong(0);
    private final AtomicLong successfulTransactions = new AtomicLong(0);
    private final AtomicLong failedTransactions = new AtomicLong(0);
    private final AtomicLong fraudTransactions = new AtomicLong(0);
    private final AtomicReference<Double> totalVolume = new AtomicReference<>(0.0);
    private final ConcurrentHashMap<String, AtomicLong> bankWiseCount = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, AtomicLong> methodWiseCount = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, AtomicLong> locationWiseCount = new ConcurrentHashMap<>();
    private final BlockingQueue<PaymentTransaction> recentTransactions = new LinkedBlockingQueue<>();
    
    public void updateMetrics(PaymentTransaction transaction) {
        totalTransactions.incrementAndGet();
        
        switch (transaction.getStatus()) {
            case SUCCESS:
                successfulTransactions.incrementAndGet();
                totalVolume.updateAndGet(v -> v + transaction.getAmount());
                break;
            case FAILED:
                failedTransactions.incrementAndGet();
                break;
            case FRAUD_SUSPECTED:
                fraudTransactions.incrementAndGet();
                break;
        }
        
        bankWiseCount.computeIfAbsent(transaction.getBank(), k -> new AtomicLong(0)).incrementAndGet();
        methodWiseCount.computeIfAbsent(transaction.getPaymentMethod(), k -> new AtomicLong(0)).incrementAndGet();
        locationWiseCount.computeIfAbsent(transaction.getLocation(), k -> new AtomicLong(0)).incrementAndGet();
        
        // Keep only recent transactions for analysis
        recentTransactions.offer(transaction);
        if (recentTransactions.size() > 10000) {
            recentTransactions.poll();
        }
    }
    
    public Map<String, Object> getMetricsSnapshot() {
        Map<String, Object> metrics = new HashMap<>();
        metrics.put("totalTransactions", totalTransactions.get());
        metrics.put("successfulTransactions", successfulTransactions.get());
        metrics.put("failedTransactions", failedTransactions.get());
        metrics.put("fraudTransactions", fraudTransactions.get());
        metrics.put("totalVolume", totalVolume.get());
        metrics.put("successRate", (double) successfulTransactions.get() / Math.max(1, totalTransactions.get()) * 100);
        metrics.put("fraudRate", (double) fraudTransactions.get() / Math.max(1, totalTransactions.get()) * 100);
        
        // Top banks
        List<Map.Entry<String, AtomicLong>> topBanks = bankWiseCount.entrySet().stream()
                .sorted(Map.Entry.<String, AtomicLong>comparingByValue((a, b) -> Long.compare(b.get(), a.get())))
                .limit(5)
                .collect(Collectors.toList());
        metrics.put("topBanks", topBanks);
        
        // Payment method distribution
        Map<String, Long> methodDistribution = methodWiseCount.entrySet().stream()
                .collect(Collectors.toMap(
                    Map.Entry::getKey,
                    e -> e.getValue().get()
                ));
        metrics.put("paymentMethodDistribution", methodDistribution);
        
        // Top locations
        List<Map.Entry<String, AtomicLong>> topLocations = locationWiseCount.entrySet().stream()
                .sorted(Map.Entry.<String, AtomicLong>comparingByValue((a, b) -> Long.compare(b.get(), a.get())))
                .limit(5)
                .collect(Collectors.toList());
        metrics.put("topLocations", topLocations);
        
        return metrics;
    }
    
    public Queue<PaymentTransaction> getRecentTransactions() {
        return new LinkedList<>(recentTransactions);
    }
}

class FraudDetectionEngine {
    private final Map<String, List<PaymentTransaction>> userTransactionHistory = new ConcurrentHashMap<>();
    private final Map<String, Double> userDailyLimits = new ConcurrentHashMap<>();
    
    public boolean isSuspiciousByAmount(PaymentTransaction transaction) {
        // Large amount threshold for Indian context
        double suspiciousAmount = 50000.0; // 50k INR
        return transaction.getAmount() > suspiciousAmount;
    }
    
    public boolean isSuspiciousByFrequency(PaymentTransaction transaction) {
        String userId = transaction.getSenderId();
        List<PaymentTransaction> userHistory = userTransactionHistory.computeIfAbsent(userId, k -> new ArrayList<>());
        
        // Check transactions in last 5 minutes
        LocalDateTime fiveMinutesAgo = LocalDateTime.now().minusMinutes(5);
        long recentTransactions = userHistory.stream()
                .filter(t -> t.getTimestamp().isAfter(fiveMinutesAgo))
                .count();
        
        // More than 10 transactions in 5 minutes is suspicious
        return recentTransactions > 10;
    }
    
    public boolean isSuspiciousByVelocity(PaymentTransaction transaction) {
        String userId = transaction.getSenderId();
        List<PaymentTransaction> userHistory = userTransactionHistory.computeIfAbsent(userId, k -> new ArrayList<>());
        
        // Check daily transaction amount
        LocalDateTime todayStart = LocalDateTime.now().withHour(0).withMinute(0).withSecond(0);
        double dailyAmount = userHistory.stream()
                .filter(t -> t.getTimestamp().isAfter(todayStart))
                .filter(t -> t.getStatus() == PaymentTransaction.TransactionStatus.SUCCESS)
                .mapToDouble(PaymentTransaction::getAmount)
                .sum();
        
        double dailyLimit = userDailyLimits.getOrDefault(userId, 100000.0); // Default 1 lakh limit
        return (dailyAmount + transaction.getAmount()) > dailyLimit * 1.5; // 150% of limit
    }
    
    public boolean isSuspiciousByLocation(PaymentTransaction transaction) {
        String userId = transaction.getSenderId();
        List<PaymentTransaction> userHistory = userTransactionHistory.computeIfAbsent(userId, k -> new ArrayList<>());
        
        // Check if user suddenly transacted from different city
        LocalDateTime oneHourAgo = LocalDateTime.now().minusHours(1);
        Set<String> recentLocations = userHistory.stream()
                .filter(t -> t.getTimestamp().isAfter(oneHourAgo))
                .map(PaymentTransaction::getLocation)
                .collect(Collectors.toSet());
        
        // If user was in different city within last hour, it's suspicious
        return recentLocations.size() > 0 && !recentLocations.contains(transaction.getLocation());
    }
    
    public PaymentTransaction.TransactionStatus evaluateTransaction(PaymentTransaction transaction) {
        // Add to user history
        String userId = transaction.getSenderId();
        userTransactionHistory.computeIfAbsent(userId, k -> new ArrayList<>()).add(transaction);
        
        // Clean old history (keep last 1000 transactions per user)
        List<PaymentTransaction> history = userTransactionHistory.get(userId);
        if (history.size() > 1000) {
            history.remove(0);
        }
        
        // Check fraud indicators
        boolean suspiciousAmount = isSuspiciousByAmount(transaction);
        boolean suspiciousFrequency = isSuspiciousByFrequency(transaction);
        boolean suspiciousVelocity = isSuspiciousByVelocity(transaction);
        boolean suspiciousLocation = isSuspiciousByLocation(transaction);
        
        // Fraud scoring
        int fraudScore = 0;
        if (suspiciousAmount) fraudScore += 40;
        if (suspiciousFrequency) fraudScore += 30;
        if (suspiciousVelocity) fraudScore += 20;
        if (suspiciousLocation) fraudScore += 10;
        
        if (fraudScore >= 50) {
            System.out.println("🚨 Fraud Alert: " + transaction.getTransactionId() + 
                             " (Score: " + fraudScore + ")");
            return PaymentTransaction.TransactionStatus.FRAUD_SUSPECTED;
        }
        
        // Simulate payment processing success/failure
        Random random = new Random();
        double successProbability = 0.985; // 98.5% success rate
        
        return random.nextDouble() < successProbability ? 
               PaymentTransaction.TransactionStatus.SUCCESS : 
               PaymentTransaction.TransactionStatus.FAILED;
    }
}

public class PaytmTransactionAnalyzer {
    private final RealTimeMetrics metrics = new RealTimeMetrics();
    private final FraudDetectionEngine fraudEngine = new FraudDetectionEngine();
    private final ExecutorService processingPool = Executors.newFixedThreadPool(10);
    private final ScheduledExecutorService scheduledPool = Executors.newScheduledThreadPool(2);
    
    // Indian banks for realistic simulation
    private final String[] indianBanks = {
        "SBI", "HDFC", "ICICI", "AXIS", "PNB", "BOB", "Canara", "Union", "IndusInd", "YES"
    };
    
    // Indian cities for location simulation
    private final String[] indianCities = {
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad", 
        "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur"
    };
    
    // Payment methods in India
    private final String[] paymentMethods = {"UPI", "WALLET", "DEBIT_CARD", "CREDIT_CARD", "NET_BANKING"};
    
    public void startRealTimeProcessing() {
        System.out.println("🚀 Starting Paytm Real-time Transaction Analytics");
        System.out.println("💳 Processing UPI, Wallet और Card transactions...\n");
        
        // Start metrics dashboard
        scheduledPool.scheduleAtFixedRate(this::printDashboard, 10, 30, TimeUnit.SECONDS);
        
        // Start transaction generation
        scheduledPool.scheduleAtFixedRate(this::generateTransactions, 0, 1, TimeUnit.SECONDS);
        
        // Runtime shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\n🛑 Shutting down transaction analyzer...");
            scheduledPool.shutdown();
            processingPool.shutdown();
        }));
    }
    
    private void generateTransactions() {
        Random random = new Random();
        
        // Generate multiple transactions per second (realistic load)
        int transactionsThisSecond = random.nextInt(50) + 10; // 10-60 TPS
        
        for (int i = 0; i < transactionsThisSecond; i++) {
            PaymentTransaction transaction = createRealisticTransaction();
            processingPool.submit(() -> processTransaction(transaction));
        }
    }
    
    private PaymentTransaction createRealisticTransaction() {
        Random random = new Random();
        
        String transactionId = "TXN_" + System.currentTimeMillis() + "_" + random.nextInt(10000);
        String senderId = "user_" + random.nextInt(1000000);
        String receiverId = "user_" + random.nextInt(1000000);
        
        // Realistic Indian transaction amounts
        double amount = generateRealisticAmount(random);
        
        String paymentMethod = paymentMethods[random.nextInt(paymentMethods.length)];
        String bank = indianBanks[random.nextInt(indianBanks.length)];
        String location = indianCities[random.nextInt(indianCities.length)];
        
        // Transaction metadata
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("deviceType", random.nextBoolean() ? "mobile" : "web");
        metadata.put("appVersion", "8.12.0");
        metadata.put("networkType", random.nextBoolean() ? "4G" : "WiFi");
        
        return new PaymentTransaction(
            transactionId, senderId, receiverId, amount, paymentMethod, bank,
            LocalDateTime.now(), PaymentTransaction.TransactionStatus.PROCESSING,
            location, metadata
        );
    }
    
    private double generateRealisticAmount(Random random) {
        // Indian payment patterns:
        // 60% small amounts (₹1 - ₹500) - chai, auto, small purchases
        // 25% medium amounts (₹500 - ₹5000) - meals, groceries, utilities
        // 10% large amounts (₹5000 - ₹25000) - shopping, rent
        // 5% very large (₹25000+) - business transactions
        
        double probability = random.nextDouble();
        
        if (probability < 0.60) {
            return 1 + random.nextDouble() * 499; // ₹1 - ₹500
        } else if (probability < 0.85) {
            return 500 + random.nextDouble() * 4500; // ₹500 - ₹5000
        } else if (probability < 0.95) {
            return 5000 + random.nextDouble() * 20000; // ₹5000 - ₹25000
        } else {
            return 25000 + random.nextDouble() * 75000; // ₹25000 - ₹100000
        }
    }
    
    private void processTransaction(PaymentTransaction transaction) {
        try {
            // Simulate processing latency (5-50ms for realistic payment processing)
            Thread.sleep(5 + new Random().nextInt(45));
            
            // Fraud detection
            PaymentTransaction.TransactionStatus finalStatus = fraudEngine.evaluateTransaction(transaction);
            
            // Create final transaction with updated status
            PaymentTransaction finalTransaction = new PaymentTransaction(
                transaction.getTransactionId(),
                transaction.getSenderId(),
                transaction.getReceiverId(),
                transaction.getAmount(),
                transaction.getPaymentMethod(),
                transaction.getBank(),
                transaction.getTimestamp(),
                finalStatus,
                transaction.getLocation(),
                transaction.getMetadata()
            );
            
            // Update metrics
            metrics.updateMetrics(finalTransaction);
            
            // Log important transactions
            if (finalStatus == PaymentTransaction.TransactionStatus.FRAUD_SUSPECTED || 
                transaction.getAmount() > 10000) {
                System.out.println(String.format("💰 %s: %s - ₹%.2f (%s via %s)",
                    finalStatus == PaymentTransaction.TransactionStatus.FRAUD_SUSPECTED ? "FRAUD" : "HIGH_VALUE",
                    finalTransaction.getTransactionId(),
                    finalTransaction.getAmount(),
                    finalTransaction.getLocation(),
                    finalTransaction.getPaymentMethod()
                ));
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    private void printDashboard() {
        Map<String, Object> metricsSnapshot = metrics.getMetricsSnapshot();
        
        System.out.println("\n" + "=".repeat(80));
        System.out.println("💳 PAYTM REAL-TIME TRANSACTION ANALYTICS DASHBOARD 💳");
        System.out.println("=".repeat(80));
        
        System.out.printf("📊 Total Transactions: %,d%n", (Long) metricsSnapshot.get("totalTransactions"));
        System.out.printf("✅ Successful: %,d%n", (Long) metricsSnapshot.get("successfulTransactions"));
        System.out.printf("❌ Failed: %,d%n", (Long) metricsSnapshot.get("failedTransactions"));
        System.out.printf("🚨 Fraud Suspected: %,d%n", (Long) metricsSnapshot.get("fraudTransactions"));
        System.out.printf("💰 Total Volume: ₹%,.2f%n", (Double) metricsSnapshot.get("totalVolume"));
        System.out.printf("📈 Success Rate: %.2f%%%n", (Double) metricsSnapshot.get("successRate"));
        System.out.printf("⚠️ Fraud Rate: %.2f%%%n", (Double) metricsSnapshot.get("fraudRate"));
        
        // Payment method distribution
        System.out.println("\n💳 Payment Method Distribution:");
        Map<String, Long> methodDist = (Map<String, Long>) metricsSnapshot.get("paymentMethodDistribution");
        methodDist.entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .forEach(entry -> {
                    long total = (Long) metricsSnapshot.get("totalTransactions");
                    double percentage = (double) entry.getValue() / Math.max(1, total) * 100;
                    System.out.printf("  %s: %,d (%.1f%%)%n", entry.getKey(), entry.getValue(), percentage);
                });
        
        // Top banks
        System.out.println("\n🏦 Top Banks by Volume:");
        List<Map.Entry<String, AtomicLong>> topBanks = (List<Map.Entry<String, AtomicLong>>) metricsSnapshot.get("topBanks");
        for (int i = 0; i < Math.min(5, topBanks.size()); i++) {
            Map.Entry<String, AtomicLong> entry = topBanks.get(i);
            System.out.printf("  %d. %s: %,d transactions%n", i + 1, entry.getKey(), entry.getValue().get());
        }
        
        // Top locations
        System.out.println("\n📍 Top Transaction Locations:");
        List<Map.Entry<String, AtomicLong>> topLocations = (List<Map.Entry<String, AtomicLong>>) metricsSnapshot.get("topLocations");
        for (int i = 0; i < Math.min(5, topLocations.size()); i++) {
            Map.Entry<String, AtomicLong> entry = topLocations.get(i);
            System.out.printf("  %d. %s: %,d transactions%n", i + 1, entry.getKey(), entry.getValue().get());
        }
        
        // Recent high-value transactions
        System.out.println("\n💎 Recent High-Value Transactions:");
        Queue<PaymentTransaction> recentTxns = metrics.getRecentTransactions();
        recentTxns.stream()
                .filter(t -> t.getAmount() > 5000)
                .sorted((a, b) -> b.getTimestamp().compareTo(a.getTimestamp()))
                .limit(3)
                .forEach(t -> {
                    String status = t.getStatus() == PaymentTransaction.TransactionStatus.SUCCESS ? "✅" : 
                                   t.getStatus() == PaymentTransaction.TransactionStatus.FRAUD_SUSPECTED ? "🚨" : "❌";
                    System.out.printf("  %s ₹%,.2f via %s (%s) - %s%n", 
                        status, t.getAmount(), t.getPaymentMethod(), t.getLocation(),
                        t.getTimestamp().format(DateTimeFormatter.ofPattern("HH:mm:ss")));
                });
        
        System.out.println("\n🕐 Last Updated: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")));
        System.out.println("=".repeat(80));
    }
    
    public static void main(String[] args) {
        PaytmTransactionAnalyzer analyzer = new PaytmTransactionAnalyzer();
        
        System.out.println("🇮🇳 Paytm Real-time Transaction Analytics - Production Simulation");
        System.out.println("📱 Simulating UPI, Wallet, और Banking transactions...");
        System.out.println("🔍 Real-time fraud detection और analytics active...\n");
        
        analyzer.startRealTimeProcessing();
        
        // Keep running for demo
        try {
            // Run for 5 minutes in demo mode
            Thread.sleep(300000);
            System.out.println("\n🏁 Demo completed! Production system would run 24/7");
        } catch (InterruptedException e) {
            System.out.println("🛑 Application stopped");
        }
    }
}