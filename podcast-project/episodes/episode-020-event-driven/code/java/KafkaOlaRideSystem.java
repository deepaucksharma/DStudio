package com.ola.events;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Apache Kafka Producer/Consumer Implementation - Java
 * उदाहरण: PhonePe UPI transaction events को Kafka के through handle करना
 * 
 * Setup:
 * - Add Kafka, Jackson, Lombok dependencies
 * - Start Kafka cluster
 * 
 * Indian Context: PhonePe app mein जब UPI transaction होता है,
 * real-time events को different services handle करती हैं:
 * - Fraud detection
 * - Transaction processing
 * - Customer notifications
 * - Analytics और reporting
 */

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
class UPITransactionEvent {
    private String eventId;
    private String eventType;
    private String transactionId;
    private String customerId;
    private String merchantId;
    private Double amount;
    private String currency;
    private String status;
    private String paymentMethod;
    private Map<String, Object> metadata;
    private String timestamp;
    
    public UPITransactionEvent() {
        this.eventId = UUID.randomUUID().toString();
        this.timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        this.currency = "INR";
        this.metadata = new HashMap<>();
    }
    
    public UPITransactionEvent(String eventType, String transactionId, String customerId, 
                              String merchantId, Double amount, String status) {
        this();
        this.eventType = eventType;
        this.transactionId = transactionId;
        this.customerId = customerId;
        this.merchantId = merchantId;
        this.amount = amount;
        this.status = status;
        this.paymentMethod = "UPI";
    }
}

@Slf4j
class PhonePeKafkaProducer {
    private final KafkaProducer<String, String> producer;
    private final ObjectMapper objectMapper;
    private final String topicName;
    
    public PhonePeKafkaProducer(String bootstrapServers, String topicName) {
        this.topicName = topicName;
        this.objectMapper = new ObjectMapper();
        
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        
        // Production settings for reliability
        props.put(ProducerConfig.ACKS_CONFIG, "all"); // Wait for all replicas
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
        props.put(ProducerConfig.LINGER_MS_CONFIG, 10); // Batching के लिए wait
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 33554432); // 32MB buffer
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true); // Duplicate prevention
        
        this.producer = new KafkaProducer<>(props);
    }
    
    /**
     * UPI transaction event को Kafka topic par publish karna
     * Railway announcement ki tarah - sabko pata chal jaana chahiye
     */
    public CompletableFuture<RecordMetadata> publishTransactionEvent(UPITransactionEvent event) {
        try {
            String eventJson = objectMapper.writeValueAsString(event);
            
            // Transaction ID को key ke रूप mein use karna - same transaction के events same partition mein
            String key = event.getTransactionId();
            
            log.info("💳 Publishing {} for transaction {}", event.getEventType(), event.getTransactionId());
            
            ProducerRecord<String, String> record = new ProducerRecord<>(
                topicName,
                key,
                eventJson
            );
            
            // Async send with callback
            CompletableFuture<RecordMetadata> future = new CompletableFuture<>();
            
            producer.send(record, (metadata, exception) -> {
                if (exception != null) {
                    log.error("❌ Failed to publish event for transaction {}: {}", 
                             event.getTransactionId(), exception.getMessage());
                    future.completeExceptionally(exception);
                } else {
                    log.info("✅ Event published to partition {}, offset {}", 
                            metadata.partition(), metadata.offset());
                    future.complete(metadata);
                }
            });
            
            return future;
            
        } catch (JsonProcessingException e) {
            log.error("❌ Failed to serialize event: {}", e.getMessage());
            return CompletableFuture.failedFuture(e);
        }
    }
    
    public void close() {
        producer.close();
        log.info("🔴 Kafka producer closed");
    }
}

@Slf4j
abstract class KafkaEventConsumer {
    protected final KafkaConsumer<String, String> consumer;
    protected final ObjectMapper objectMapper;
    protected final AtomicBoolean running;
    protected final String consumerGroupId;
    
    public KafkaEventConsumer(String bootstrapServers, String topicName, String consumerGroupId) {
        this.consumerGroupId = consumerGroupId;
        this.objectMapper = new ObjectMapper();
        this.running = new AtomicBoolean(false);
        
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, consumerGroupId);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        
        // Consumer settings for reliability
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false); // Manual commit
        props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 30000);
        props.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 10000);
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 100); // Batch size
        
        this.consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Arrays.asList(topicName));
    }
    
    /**
     * Start consuming messages
     * Mumbai local की tarah - continuously चलता रहता है
     */
    public void startConsuming() {
        running.set(true);
        log.info("🎧 Starting consumer for group: {}", consumerGroupId);
        
        try {
            while (running.get()) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
                
                for (ConsumerRecord<String, String> record : records) {
                    try {
                        // Message को UPI event mein convert karna
                        UPITransactionEvent event = objectMapper.readValue(
                            record.value(), UPITransactionEvent.class);
                        
                        log.info("📨 Received {} - Key: {}, Partition: {}, Offset: {}", 
                                event.getEventType(), record.key(), record.partition(), record.offset());
                        
                        // Event process karna
                        boolean success = processEvent(event);
                        
                        if (success) {
                            // Manual commit after successful processing
                            Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
                            offsets.put(
                                new TopicPartition(record.topic(), record.partition()),
                                new OffsetAndMetadata(record.offset() + 1)
                            );
                            consumer.commitSync(offsets);
                            log.debug("✅ Message committed - Offset: {}", record.offset());
                        } else {
                            log.warn("⚠️ Message processing failed - will retry");
                        }
                        
                    } catch (Exception e) {
                        log.error("❌ Error processing message at offset {}: {}", 
                                 record.offset(), e.getMessage());
                    }
                }
            }
        } catch (Exception e) {
            log.error("❌ Consumer error: {}", e.getMessage());
        } finally {
            consumer.close();
            log.info("🔴 Consumer closed for group: {}", consumerGroupId);
        }
    }
    
    /**
     * Process individual event - हर service mein अलग implementation
     */
    protected abstract boolean processEvent(UPITransactionEvent event);
    
    public void stop() {
        running.set(false);
    }
}

/**
 * Fraud detection service - suspicious transactions detect karna
 */
@Slf4j
class FraudDetectionService extends KafkaEventConsumer {
    private final Set<String> suspiciousPatterns;
    
    public FraudDetectionService(String bootstrapServers, String topicName) {
        super(bootstrapServers, topicName, "fraud-detection-service");
        
        // Suspicious patterns for fraud detection
        this.suspiciousPatterns = Set.of(
            "midnight_transaction", "high_velocity", "unusual_merchant"
        );
    }
    
    @Override
    protected boolean processEvent(UPITransactionEvent event) {
        try {
            String transactionId = event.getTransactionId();
            Double amount = event.getAmount();
            String customerId = event.getCustomerId();
            
            log.info("🔍 Fraud Detection: Analyzing transaction {}", transactionId);
            log.info("   💰 Amount: ₹{}", amount);
            log.info("   👤 Customer: {}", customerId);
            
            // Fraud checks
            boolean isSuspicious = false;
            
            // High amount check - ₹50,000 se zyada
            if (amount > 50000) {
                log.warn("⚠️ High amount transaction detected: ₹{}", amount);
                isSuspicious = true;
            }
            
            // Time based check - midnight transactions
            if (LocalDateTime.now().getHour() >= 23 || LocalDateTime.now().getHour() <= 5) {
                log.warn("⚠️ Midnight transaction detected");
                isSuspicious = true;
            }
            
            // Simulation - fraud processing
            Thread.sleep(200);
            
            if (isSuspicious) {
                log.warn("🚨 SUSPICIOUS TRANSACTION: {} flagged for review", transactionId);
                // यहाँ fraud alert event publish करना चाहिए
            } else {
                log.info("✅ Transaction {} cleared fraud checks", transactionId);
            }
            
            return true;
            
        } catch (Exception e) {
            log.error("❌ Fraud detection failed: {}", e.getMessage());
            return false;
        }
    }
}

/**
 * Transaction processing service
 */
@Slf4j
class TransactionProcessingService extends KafkaEventConsumer {
    
    public TransactionProcessingService(String bootstrapServers, String topicName) {
        super(bootstrapServers, topicName, "transaction-processing-service");
    }
    
    @Override
    protected boolean processEvent(UPITransactionEvent event) {
        try {
            if (!"transaction.initiated".equals(event.getEventType())) {
                return true; // Only process initiated transactions
            }
            
            String transactionId = event.getTransactionId();
            Double amount = event.getAmount();
            String merchantId = event.getMerchantId();
            
            log.info("🏦 Transaction Processing: Processing {}", transactionId);
            log.info("   💰 Amount: ₹{}", amount);
            log.info("   🏪 Merchant: {}", merchantId);
            
            // Bank integration simulation
            Thread.sleep(800);
            
            // Success probability - 95%
            boolean success = Math.random() > 0.05;
            
            if (success) {
                log.info("✅ Transaction {} processed successfully", transactionId);
                // यहाँ transaction.completed event publish करना चाहिए
            } else {
                log.error("❌ Transaction {} failed", transactionId);
                // यहाँ transaction.failed event publish करना चाहिए
            }
            
            return true;
            
        } catch (Exception e) {
            log.error("❌ Transaction processing failed: {}", e.getMessage());
            return false;
        }
    }
}

/**
 * Customer notification service
 */
@Slf4j
class CustomerNotificationService extends KafkaEventConsumer {
    
    public CustomerNotificationService(String bootstrapServers, String topicName) {
        super(bootstrapServers, topicName, "customer-notification-service");
    }
    
    @Override
    protected boolean processEvent(UPITransactionEvent event) {
        try {
            String transactionId = event.getTransactionId();
            String customerId = event.getCustomerId();
            String eventType = event.getEventType();
            
            log.info("📱 Customer Notification: Sending {} notification", eventType);
            log.info("   👤 Customer: {}", customerId);
            log.info("   💳 Transaction: {}", transactionId);
            
            // Notification type based on event
            String notificationType;
            String message;
            
            switch (eventType) {
                case "transaction.initiated":
                    notificationType = "SMS";
                    message = String.format("₹%.2f payment initiated. Transaction ID: %s", 
                                           event.getAmount(), transactionId);
                    break;
                case "transaction.completed":
                    notificationType = "Push + SMS";
                    message = String.format("₹%.2f payment successful! Transaction ID: %s", 
                                           event.getAmount(), transactionId);
                    break;
                case "transaction.failed":
                    notificationType = "Push";
                    message = String.format("Payment failed. Please try again. Transaction ID: %s", 
                                           transactionId);
                    break;
                default:
                    return true; // Skip unknown events
            }
            
            // Notification sending simulation
            Thread.sleep(300);
            
            log.info("✅ {} sent: {}", notificationType, message);
            
            return true;
            
        } catch (Exception e) {
            log.error("❌ Customer notification failed: {}", e.getMessage());
            return false;
        }
    }
}

/**
 * Analytics service - metrics collection
 */
@Slf4j
class AnalyticsService extends KafkaEventConsumer {
    private final Map<String, Integer> eventCounts = new ConcurrentHashMap<>();
    private final Map<String, Double> amountTotals = new ConcurrentHashMap<>();
    
    public AnalyticsService(String bootstrapServers, String topicName) {
        super(bootstrapServers, topicName, "analytics-service");
    }
    
    @Override
    protected boolean processEvent(UPITransactionEvent event) {
        try {
            String eventType = event.getEventType();
            Double amount = event.getAmount();
            
            log.info("📊 Analytics: Recording {} event", eventType);
            
            // Event counts track karna
            eventCounts.merge(eventType, 1, Integer::sum);
            
            // Amount totals track karna
            if (amount != null) {
                amountTotals.merge(eventType, amount, Double::sum);
            }
            
            // Analytics processing simulation
            Thread.sleep(100);
            
            // Periodic stats logging
            if (eventCounts.values().stream().mapToInt(Integer::intValue).sum() % 10 == 0) {
                logStats();
            }
            
            return true;
            
        } catch (Exception e) {
            log.error("❌ Analytics processing failed: {}", e.getMessage());
            return false;
        }
    }
    
    private void logStats() {
        log.info("📈 Analytics Stats:");
        eventCounts.forEach((event, count) -> {
            Double total = amountTotals.getOrDefault(event, 0.0);
            log.info("   {} - Count: {}, Total Amount: ₹{}", event, count, total);
        });
    }
}

/**
 * Main demo class
 */
@Slf4j
public class KafkaOlaRideSystem {
    private static final String BOOTSTRAP_SERVERS = "localhost:9092";
    private static final String TOPIC_NAME = "phonepe-transactions";
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("💳 PhonePe Kafka Event-Driven UPI System Demo");
        System.out.println("=".repeat(60));
        System.out.println("📋 Make sure Kafka is running on localhost:9092");
        System.out.println();
        
        ExecutorService executorService = Executors.newCachedThreadPool();
        
        try {
            // Start consumer services
            log.info("🎧 Starting consumer services...");
            
            FraudDetectionService fraudService = new FraudDetectionService(BOOTSTRAP_SERVERS, TOPIC_NAME);
            TransactionProcessingService txnService = new TransactionProcessingService(BOOTSTRAP_SERVERS, TOPIC_NAME);
            CustomerNotificationService notificationService = new CustomerNotificationService(BOOTSTRAP_SERVERS, TOPIC_NAME);
            AnalyticsService analyticsService = new AnalyticsService(BOOTSTRAP_SERVERS, TOPIC_NAME);
            
            // Start consumers in separate threads
            executorService.submit(fraudService::startConsuming);
            executorService.submit(txnService::startConsuming);
            executorService.submit(notificationService::startConsuming);
            executorService.submit(analyticsService::startConsuming);
            
            // Wait for consumers to initialize
            Thread.sleep(3000);
            
            // Start producing events
            log.info("🚀 Starting UPI transaction simulation...");
            simulateUPITransactions();
            
            // Let consumers process for a while
            log.info("⏳ Processing events for 30 seconds...");
            Thread.sleep(30000);
            
            // Stop services
            fraudService.stop();
            txnService.stop();
            notificationService.stop();
            analyticsService.stop();
            
            log.info("✅ Demo completed successfully!");
            
        } catch (Exception e) {
            log.error("❌ Demo failed: {}", e.getMessage());
        } finally {
            executorService.shutdown();
        }
    }
    
    private static void simulateUPITransactions() {
        PhonePeKafkaProducer producer = new PhonePeKafkaProducer(BOOTSTRAP_SERVERS, TOPIC_NAME);
        
        try {
            // Sample merchants
            String[] merchants = {
                "AMAZON_IN", "FLIPKART", "SWIGGY", "ZOMATO", 
                "BIG_BASKET", "PAYTM_MALL", "MYNTRA", "NYKAA"
            };
            
            String[] customers = {
                "CUST001", "CUST002", "CUST003", "CUST004", "CUST005"
            };
            
            // Generate 20 transactions
            for (int i = 0; i < 20; i++) {
                String transactionId = "TXN" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
                String customerId = customers[i % customers.length];
                String merchantId = merchants[i % merchants.length];
                
                // Random amount between ₹50 to ₹5000
                Double amount = 50.0 + (Math.random() * 4950.0);
                
                // Transaction initiated event
                UPITransactionEvent initiatedEvent = new UPITransactionEvent(
                    "transaction.initiated",
                    transactionId,
                    customerId,
                    merchantId,
                    amount,
                    "pending"
                );
                
                producer.publishTransactionEvent(initiatedEvent);
                
                // Wait between transactions
                Thread.sleep(500);
                
                // 90% success rate for completion
                if (Math.random() > 0.1) {
                    UPITransactionEvent completedEvent = new UPITransactionEvent(
                        "transaction.completed",
                        transactionId,
                        customerId,
                        merchantId,
                        amount,
                        "completed"
                    );
                    producer.publishTransactionEvent(completedEvent);
                } else {
                    UPITransactionEvent failedEvent = new UPITransactionEvent(
                        "transaction.failed",
                        transactionId,
                        customerId,
                        merchantId,
                        amount,
                        "failed"
                    );
                    producer.publishTransactionEvent(failedEvent);
                }
                
                Thread.sleep(200);
            }
            
        } catch (InterruptedException e) {
            log.error("Transaction simulation interrupted");
            Thread.currentThread().interrupt();
        } finally {
            producer.close();
        }
    }
}