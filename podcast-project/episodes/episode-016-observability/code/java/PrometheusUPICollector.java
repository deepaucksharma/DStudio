/*
 * Episode 16: Observability & Monitoring
 * Java Example: Enterprise UPI Monitoring with Micrometer
 * 
 * भारतीय enterprise applications के लिए production-ready UPI monitoring
 * Spring Boot और Micrometer के साथ comprehensive metrics collection
 * 
 * Author: Hindi Tech Podcast
 * Context: Enterprise Java applications में UPI monitoring
 */

package com.hindipodcast.observability.upi;

import io.micrometer.core.annotation.Timed;
import io.micrometer.core.instrument.*;
import io.micrometer.core.instrument.binder.MeterBinder;
import io.micrometer.prometheus.PrometheusConfig;
import io.micrometer.prometheus.PrometheusMeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.bind.annotation.*;

import javax.annotation.PostConstruct;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/**
 * UPI Bank enum - भारतीय banks की comprehensive list
 */
enum UPIBank {
    SBI("sbi", "State Bank of India"),
    HDFC("hdfc", "HDFC Bank"),
    ICICI("icici", "ICICI Bank"),
    AXIS("axis", "Axis Bank"),
    KOTAK("kotak", "Kotak Mahindra Bank"),
    PNB("pnb", "Punjab National Bank"),
    CANARA("canara", "Canara Bank"),
    UNION("union", "Union Bank"),
    BOI("boi", "Bank of India"),
    IOB("iob", "Indian Overseas Bank");

    private final String code;
    private final String displayName;

    UPIBank(String code, String displayName) {
        this.code = code;
        this.displayName = displayName;
    }

    public String getCode() { return code; }
    public String getDisplayName() { return displayName; }
}

/**
 * UPI Transaction Type enum
 */
enum UPITransactionType {
    P2P("person_to_person", "Person to Person"),
    P2M("person_to_merchant", "Person to Merchant"),
    BILL_PAYMENT("bill_payment", "Bill Payment"),
    MOBILE_RECHARGE("mobile_recharge", "Mobile Recharge"),
    ECOMMERCE("ecommerce", "E-commerce"),
    INVESTMENT("investment", "Investment"),
    INSURANCE("insurance", "Insurance");

    private final String code;
    private final String displayName;

    UPITransactionType(String code, String displayName) {
        this.code = code;
        this.displayName = displayName;
    }

    public String getCode() { return code; }
    public String getDisplayName() { return displayName; }
}

/**
 * UPI Transaction data model
 */
class UPITransaction {
    private final String transactionId;
    private final UPIBank bank;
    private final UPITransactionType transactionType;
    private final double amount;
    private final String currency;
    private final boolean success;
    private final String errorCode;
    private final long processingTimeMs;
    private final String userCity;
    private final String merchantCategory;
    private final LocalDateTime timestamp;
    private final int retryCount;

    // Constructor और getters
    public UPITransaction(String transactionId, UPIBank bank, UPITransactionType transactionType,
                         double amount, boolean success, String errorCode, long processingTimeMs,
                         String userCity, String merchantCategory, int retryCount) {
        this.transactionId = transactionId;
        this.bank = bank;
        this.transactionType = transactionType;
        this.amount = amount;
        this.currency = "INR";
        this.success = success;
        this.errorCode = errorCode;
        this.processingTimeMs = processingTimeMs;
        this.userCity = userCity;
        this.merchantCategory = merchantCategory;
        this.retryCount = retryCount;
        this.timestamp = LocalDateTime.now();
    }

    // Getters
    public String getTransactionId() { return transactionId; }
    public UPIBank getBank() { return bank; }
    public UPITransactionType getTransactionType() { return transactionType; }
    public double getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public boolean isSuccess() { return success; }
    public String getErrorCode() { return errorCode; }
    public long getProcessingTimeMs() { return processingTimeMs; }
    public String getUserCity() { return userCity; }
    public String getMerchantCategory() { return merchantCategory; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public int getRetryCount() { return retryCount; }
}

/**
 * Enterprise UPI Metrics Collector
 * Micrometer के साथ production-ready metrics collection
 */
@Configuration
public class PrometheusUPICollector implements MeterBinder {
    
    private static final Logger logger = LoggerFactory.getLogger(PrometheusUPICollector.class);
    
    // Core metrics
    private Counter upiTransactionsTotal;
    private Counter upiTransactionAmountTotal;
    private Timer upiResponseTime;
    private Gauge upiSuccessRate;
    private Counter upiErrorsTotal;
    private Gauge bankAvailability;
    private Gauge peakHourLoad;
    private Gauge festivalTransactionSpike;
    private Gauge rbiReportingLag;
    
    // Indian cities for regional monitoring
    private static final List<String> INDIAN_CITIES = Arrays.asList(
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
        "Pune", "Hyderabad", "Ahmedabad", "Surat", "Jaipur",
        "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal"
    );
    
    // Success rate tracking per bank (5-minute window)
    private final Map<UPIBank, AtomicLong> successCounts = new ConcurrentHashMap<>();
    private final Map<UPIBank, AtomicLong> totalCounts = new ConcurrentHashMap<>();
    
    // Scheduled executor for periodic updates
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

    @Override
    public void bindTo(MeterRegistry meterRegistry) {
        /*
         * Core UPI Transaction Metrics
         * भारतीय scale के लिए optimized metrics
         */
        
        // Transaction count by bank, type, status, and city
        upiTransactionsTotal = Counter.builder("upi_transactions_total")
                .description("Total UPI transactions processed")
                .tag("application", "upi-processor")
                .register(meterRegistry);
        
        // Transaction amount in INR
        upiTransactionAmountTotal = Counter.builder("upi_transaction_amount_inr_total")
                .description("Total UPI transaction amount in INR")
                .tag("application", "upi-processor")
                .register(meterRegistry);
        
        // Response time distribution
        upiResponseTime = Timer.builder("upi_response_time_seconds")
                .description("UPI transaction response time")
                .tag("application", "upi-processor")
                .register(meterRegistry);
        
        // Error tracking
        upiErrorsTotal = Counter.builder("upi_errors_total")
                .description("Total UPI transaction errors")
                .tag("application", "upi-processor")
                .register(meterRegistry);
        
        /*
         * Bank और Infrastructure Metrics
         */
        
        // Bank availability (1=up, 0=down)
        bankAvailability = Gauge.builder("upi_bank_availability")
                .description("UPI bank service availability")
                .tag("application", "upi-processor")
                .register(meterRegistry, this, obj -> getBankAvailabilityValue());
        
        // Success rate gauge per bank
        upiSuccessRate = Gauge.builder("upi_success_rate_percentage")
                .description("UPI transaction success rate by bank")
                .tag("application", "upi-processor")
                .register(meterRegistry, this, obj -> getOverallSuccessRate());
        
        /*
         * Indian Context Specific Metrics
         */
        
        // Peak hour transaction rate (Indian business hours)
        peakHourLoad = Gauge.builder("upi_peak_hour_transaction_rate")
                .description("Transaction rate during Indian peak hours")
                .tag("application", "upi-processor")
                .register(meterRegistry, this, obj -> getCurrentTransactionRate());
        
        // Festival season traffic spike
        festivalTransactionSpike = Gauge.builder("upi_festival_transaction_multiplier")
                .description("Transaction volume multiplier during festivals")
                .tag("application", "upi-processor")
                .register(meterRegistry, this, obj -> getFestivalMultiplier());
        
        /*
         * Compliance Metrics (RBI requirements)
         */
        
        // RBI reporting lag
        rbiReportingLag = Gauge.builder("upi_rbi_reporting_lag_seconds")
                .description("RBI transaction reporting lag")
                .tag("application", "upi-processor")
                .register(meterRegistry, this, obj -> getRBIReportingLag());
        
        logger.info("UPI Prometheus metrics initialized with {} banks and {} cities", 
                   UPIBank.values().length, INDIAN_CITIES.size());
        
        // Initialize bank counters
        for (UPIBank bank : UPIBank.values()) {
            successCounts.put(bank, new AtomicLong(0));
            totalCounts.put(bank, new AtomicLong(0));
        }
    }

    /**
     * UPI transaction को comprehensive metrics में record करता है
     * 
     * @param transaction UPI transaction details
     */
    public void recordUPITransaction(UPITransaction transaction) {
        try {
            long startTime = System.currentTimeMillis();
            
            // Basic transaction count
            String status = transaction.isSuccess() ? "success" : "failure";
            upiTransactionsTotal.increment(
                Tags.of(
                    "bank", transaction.getBank().getCode(),
                    "transaction_type", transaction.getTransactionType().getCode(),
                    "status", status,
                    "city", transaction.getUserCity(),
                    "merchant_category", transaction.getMerchantCategory()
                )
            );
            
            // Transaction amount (only for successful transactions)
            if (transaction.isSuccess()) {
                upiTransactionAmountTotal.increment(
                    Tags.of(
                        "bank", transaction.getBank().getCode(),
                        "transaction_type", transaction.getTransactionType().getCode(),
                        "city", transaction.getUserCity()
                    ),
                    transaction.getAmount()
                );
            }
            
            // Response time tracking
            upiResponseTime.record(
                transaction.getProcessingTimeMs(),
                TimeUnit.MILLISECONDS,
                Tags.of(
                    "bank", transaction.getBank().getCode(),
                    "transaction_type", transaction.getTransactionType().getCode()
                )
            );
            
            // Error tracking for failed transactions
            if (!transaction.isSuccess() && transaction.getErrorCode() != null) {
                String errorType = categorizeError(transaction.getErrorCode());
                upiErrorsTotal.increment(
                    Tags.of(
                        "bank", transaction.getBank().getCode(),
                        "error_code", transaction.getErrorCode(),
                        "error_type", errorType
                    )
                );
            }
            
            // Update success rate counters
            updateSuccessRateCounters(transaction);
            
            // Peak hour detection (Indian business hours: 10-11 AM, 7-9 PM IST)
            int currentHour = LocalDateTime.now().getHour();
            if (isPeakHour(currentHour)) {
                // Peak hour metrics are updated via gauge
                logger.debug("Peak hour transaction recorded: {}", transaction.getTransactionId());
            }
            
            long processingTime = System.currentTimeMillis() - startTime;
            
            logger.info("UPI transaction recorded - ID: {}, Bank: {}, Amount: {}, Success: {}, ProcessingTime: {}ms",
                       transaction.getTransactionId(),
                       transaction.getBank().getCode(),
                       transaction.getAmount(),
                       transaction.isSuccess(),
                       processingTime);
                       
        } catch (Exception e) {
            logger.error("Failed to record UPI transaction metrics for transaction: {}", 
                        transaction.getTransactionId(), e);
        }
    }

    /**
     * Error codes को categories में classify करता है
     * Indian banking error patterns के according
     */
    private String categorizeError(String errorCode) {
        if (errorCode == null) return "UNKNOWN";
        
        String upperErrorCode = errorCode.toUpperCase();
        
        if (upperErrorCode.contains("TIMEOUT") || upperErrorCode.contains("BT")) {
            return "BANK_TIMEOUT";
        } else if (upperErrorCode.contains("INSUFFICIENT") || upperErrorCode.contains("IF") || upperErrorCode.contains("BALANCE")) {
            return "INSUFFICIENT_FUNDS";
        } else if (upperErrorCode.contains("PIN") || upperErrorCode.contains("AUTH")) {
            return "AUTHENTICATION_FAILED";
        } else if (upperErrorCode.contains("NETWORK") || upperErrorCode.contains("CONN")) {
            return "NETWORK_ERROR";
        } else if (upperErrorCode.contains("LIMIT") || upperErrorCode.contains("LE")) {
            return "LIMIT_EXCEEDED";
        } else if (upperErrorCode.contains("FRAUD") || upperErrorCode.contains("SUSPICIOUS")) {
            return "FRAUD_SUSPECTED";
        } else if (upperErrorCode.contains("MAINTENANCE") || upperErrorCode.contains("SERVICE_DOWN")) {
            return "BANK_MAINTENANCE";
        } else {
            return "TECHNICAL_ERROR";
        }
    }

    /**
     * Success rate counters को update करता है
     */
    private void updateSuccessRateCounters(UPITransaction transaction) {
        UPIBank bank = transaction.getBank();
        totalCounts.get(bank).incrementAndGet();
        
        if (transaction.isSuccess()) {
            successCounts.get(bank).incrementAndGet();
        }
    }

    /**
     * Peak hour detection - Indian business timing
     */
    private boolean isPeakHour(int hour) {
        // Indian peak hours: 10-11 AM (Tatkal booking), 7-9 PM (evening shopping)
        return (hour >= 10 && hour <= 11) || (hour >= 19 && hour <= 21);
    }

    /*
     * Gauge value calculation methods
     * Real-time metrics के लिए
     */

    private double getBankAvailabilityValue() {
        // Simulate bank availability (in production, would check actual bank APIs)
        return Math.random() > 0.05 ? 1.0 : 0.0; // 95% uptime simulation
    }

    private double getOverallSuccessRate() {
        long totalSuccess = successCounts.values().stream().mapToLong(AtomicLong::get).sum();
        long totalTransactions = totalCounts.values().stream().mapToLong(AtomicLong::get).sum();
        
        if (totalTransactions == 0) return 100.0;
        return (totalSuccess * 100.0) / totalTransactions;
    }

    private double getCurrentTransactionRate() {
        // Simulate current TPS based on time of day
        int currentHour = LocalDateTime.now().getHour();
        if (isPeakHour(currentHour)) {
            return 800 + (Math.random() * 400); // 800-1200 TPS during peak
        } else {
            return 100 + (Math.random() * 200); // 100-300 TPS during normal hours
        }
    }

    private double getFestivalMultiplier() {
        // Detect festival seasons and return traffic multiplier
        int currentMonth = LocalDateTime.now().getMonthValue();
        
        switch (currentMonth) {
            case 10: return 5.0; // October - BBD season
            case 11: return 8.0; // November - Diwali
            case 12: return 4.0; // December - Christmas/NYE
            case 3:  return 2.5; // March - Holi
            case 8:  return 2.0; // August - Raksha Bandhan
            default: return 1.0; // Normal times
        }
    }

    private double getRBIReportingLag() {
        // Simulate RBI reporting lag (in production, would measure actual lag)
        return Math.random() * 300; // 0-5 minutes lag simulation
    }

    /**
     * Bank availability को update करता है
     */
    public void updateBankAvailability(UPIBank bank, boolean isAvailable) {
        // This would be called by bank health check services
        logger.info("Bank availability updated - Bank: {}, Available: {}", bank.getCode(), isAvailable);
    }

    /**
     * Periodic metrics updates को start करता है
     */
    @PostConstruct
    public void startPeriodicUpdates() {
        // Update success rates every minute
        scheduler.scheduleAtFixedRate(this::updateSuccessRates, 0, 1, TimeUnit.MINUTES);
        
        // Update compliance metrics every 5 minutes
        scheduler.scheduleAtFixedRate(this::updateComplianceMetrics, 0, 5, TimeUnit.MINUTES);
        
        logger.info("Started periodic metrics updates");
    }

    private void updateSuccessRates() {
        // Success rates are calculated on-demand via gauges
        // This method could reset counters for sliding window calculations
        logger.debug("Updating success rate calculations");
    }

    private void updateComplianceMetrics() {
        // Update RBI compliance-related metrics
        logger.debug("Updating RBI compliance metrics");
    }

    /**
     * Cleanup resources
     */
    public void shutdown() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
        logger.info("UPI metrics collector shutdown completed");
    }
}

/**
 * Sample UPI transaction generator for testing
 */
class UPITransactionGenerator {
    
    private static final Random random = new Random();
    
    private static final List<String> INDIAN_CITIES = Arrays.asList(
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
        "Pune", "Hyderabad", "Ahmedabad", "Surat", "Jaipur"
    );
    
    private static final List<String> MERCHANT_CATEGORIES = Arrays.asList(
        "grocery", "fuel", "restaurant", "ecommerce", "utility",
        "healthcare", "education", "entertainment", "transport"
    );

    public static UPITransaction generateSampleTransaction() {
        // Random bank selection
        UPIBank bank = UPIBank.values()[random.nextInt(UPIBank.values().length)];
        
        // Random transaction type
        UPITransactionType txnType = UPITransactionType.values()[random.nextInt(UPITransactionType.values().length)];
        
        // Indian transaction amount patterns
        double amount;
        switch (txnType) {
            case P2P:
                amount = 100 + (random.nextDouble() * 49900); // ₹100 to ₹50,000
                break;
            case ECOMMERCE:
                amount = 500 + (random.nextDouble() * 9500); // ₹500 to ₹10,000
                break;
            case BILL_PAYMENT:
                amount = 200 + (random.nextDouble() * 4800); // ₹200 to ₹5,000
                break;
            default:
                amount = 50 + (random.nextDouble() * 1950); // ₹50 to ₹2,000
        }
        
        // Success rate varies by bank (realistic patterns)
        Map<UPIBank, Double> bankSuccessRates = new HashMap<>();
        bankSuccessRates.put(UPIBank.SBI, 0.96);
        bankSuccessRates.put(UPIBank.HDFC, 0.97);
        bankSuccessRates.put(UPIBank.ICICI, 0.95);
        bankSuccessRates.put(UPIBank.KOTAK, 0.98);
        bankSuccessRates.put(UPIBank.AXIS, 0.94);
        
        double successRate = bankSuccessRates.getOrDefault(bank, 0.90);
        boolean success = random.nextDouble() < successRate;
        
        // Error codes for failed transactions
        String errorCode = null;
        if (!success) {
            String[] errors = {"BT01", "IF01", "NE01", "LE01", "AUTH_FAIL", "FRAUD_DETECTED"};
            errorCode = errors[random.nextInt(errors.length)];
        }
        
        // Processing time varies by bank and success
        long processingTime = success ? 
            (long)(1000 + (random.nextDouble() * 4000)) :  // 1-5 seconds for success
            (long)(2000 + (random.nextDouble() * 8000));   // 2-10 seconds for failures
        
        String city = INDIAN_CITIES.get(random.nextInt(INDIAN_CITIES.size()));
        String merchantCategory = MERCHANT_CATEGORIES.get(random.nextInt(MERCHANT_CATEGORIES.size()));
        int retryCount = success ? 0 : random.nextInt(4);
        
        String transactionId = "UPI" + System.currentTimeMillis() + String.format("%04d", random.nextInt(10000));
        
        return new UPITransaction(
            transactionId, bank, txnType, amount, success, errorCode,
            processingTime, city, merchantCategory, retryCount
        );
    }
}

/**
 * Main Spring Boot application class
 */
@SpringBootApplication
@RestController
public class UPIMonitoringApplication {
    
    private static final Logger logger = LoggerFactory.getLogger(UPIMonitoringApplication.class);
    
    private final PrometheusUPICollector metricsCollector;
    private final ScheduledExecutorService simulator = Executors.newSingleThreadScheduledExecutor();

    public UPIMonitoringApplication(PrometheusUPICollector metricsCollector) {
        this.metricsCollector = metricsCollector;
    }

    public static void main(String[] args) {
        SpringApplication.run(UPIMonitoringApplication.class, args);
    }

    @PostConstruct
    public void startTransactionSimulation() {
        // Start transaction simulation
        simulator.scheduleAtFixedRate(this::simulateTransaction, 0, 500, TimeUnit.MILLISECONDS);
        logger.info("UPI transaction simulation started");
    }

    private void simulateTransaction() {
        try {
            UPITransaction transaction = UPITransactionGenerator.generateSampleTransaction();
            metricsCollector.recordUPITransaction(transaction);
        } catch (Exception e) {
            logger.error("Error in transaction simulation", e);
        }
    }

    @GetMapping("/api/upi/health")
    public Map<String, Object> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        health.put("service", "UPI Monitoring");
        health.put("version", "1.0.0");
        return health;
    }

    @PostMapping("/api/upi/transaction")
    public Map<String, Object> processTransaction(@RequestBody Map<String, Object> transactionData) {
        // Simulate transaction processing
        Map<String, Object> response = new HashMap<>();
        
        try {
            // Generate transaction from request data
            UPITransaction transaction = UPITransactionGenerator.generateSampleTransaction();
            
            // Record metrics
            metricsCollector.recordUPITransaction(transaction);
            
            response.put("status", "success");
            response.put("transactionId", transaction.getTransactionId());
            response.put("amount", transaction.getAmount());
            response.put("processingTime", transaction.getProcessingTimeMs());
            
        } catch (Exception e) {
            logger.error("Transaction processing failed", e);
            response.put("status", "error");
            response.put("error", e.getMessage());
        }
        
        return response;
    }

    @Bean
    public PrometheusUPICollector upiMetricsCollector() {
        return new PrometheusUPICollector();
    }

    @Bean
    public PrometheusMeterRegistry prometheusMeterRegistry() {
        return new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
    }
}

/*
Production Deployment Configuration:

1. Application Properties (application.yml):
```yaml
spring:
  application:
    name: upi-monitoring-service
  
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    metrics:
      enabled: true
    prometheus:
      enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        upi.response.time: true
      percentiles:
        upi.response.time: 0.5, 0.95, 0.99

server:
  port: 8080

logging:
  level:
    com.hindipodcast.observability: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level [%logger{36}] - %msg%n"
```

2. Docker Configuration:
```dockerfile
FROM openjdk:11-jre-slim
COPY target/upi-monitoring-*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

3. Kubernetes Deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: upi-monitoring
spec:
  replicas: 3
  selector:
    matchLabels:
      app: upi-monitoring
  template:
    metadata:
      labels:
        app: upi-monitoring
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/actuator/prometheus"
    spec:
      containers:
      - name: upi-monitoring
        image: upi-monitoring:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "512Mi"
            cpu: "0.5"
          limits:
            memory: "1Gi"
            cpu: "1"
```

4. Maven Dependencies:
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-registry-prometheus</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

5. Production Monitoring:
   - JVM metrics (heap, GC, threads)
   - Database connection pool monitoring
   - HTTP request metrics
   - Custom business metrics
   - Alert integration with PagerDuty/Slack

6. Security Configuration:
   - Actuator endpoint security
   - Metrics data sanitization
   - Rate limiting for APIs
   - Authentication for sensitive endpoints
*/