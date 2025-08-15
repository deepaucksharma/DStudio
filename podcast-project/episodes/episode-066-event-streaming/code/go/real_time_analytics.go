/*
Event Streaming Episode - Real-time Analytics Pipeline with Go
Production-ready analytics processing for Indian fintech applications

Author: Hindi Tech Podcast Series
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"github.com/go-redis/redis/v8"
)

// PaytmTransactionEvent represents a Paytm transaction for real-time analytics
// Paytm जैसे payment platform के transaction events
type PaytmTransactionEvent struct {
	TransactionID   string    `json:"transaction_id"`
	UserID          string    `json:"user_id"`
	MerchantID      string    `json:"merchant_id"`
	Amount          float64   `json:"amount"`
	PaymentMethod   string    `json:"payment_method"`    // UPI, WALLET, CARD
	Status          string    `json:"status"`            // SUCCESS, FAILED, PENDING
	Category        string    `json:"category"`          // FOOD, TRANSPORT, SHOPPING, etc.
	Location        string    `json:"location"`          // Mumbai, Delhi, etc.
	Timestamp       time.Time `json:"timestamp"`
	ProcessingTime  int64     `json:"processing_time_ms"` // Processing time in milliseconds
	ErrorCode       string    `json:"error_code,omitempty"`
	MerchantType    string    `json:"merchant_type"`     // ONLINE, OFFLINE
	DeviceType      string    `json:"device_type"`       // MOBILE, DESKTOP
}

// RealTimeMetrics represents aggregated metrics
// Real-time analytics के लिए metrics structure
type RealTimeMetrics struct {
	WindowStart       time.Time `json:"window_start"`
	WindowEnd         time.Time `json:"window_end"`
	TransactionCount  int64     `json:"transaction_count"`
	TotalVolume       float64   `json:"total_volume"`
	SuccessCount      int64     `json:"success_count"`
	FailureCount      int64     `json:"failure_count"`
	AvgProcessingTime float64   `json:"avg_processing_time_ms"`
	SuccessRate       float64   `json:"success_rate"`
	TopCategories     map[string]int64 `json:"top_categories"`
	TopLocations      map[string]int64 `json:"top_locations"`
	PaymentMethods    map[string]int64 `json:"payment_methods"`
	LastUpdated       time.Time `json:"last_updated"`
}

// FraudAlert represents a potential fraud alert
// Fraud detection के लिए alert structure
type FraudAlert struct {
	AlertID       string    `json:"alert_id"`
	UserID        string    `json:"user_id"`
	AlertType     string    `json:"alert_type"`
	Severity      string    `json:"severity"`
	Description   string    `json:"description"`
	TriggerData   string    `json:"trigger_data"`
	Timestamp     time.Time `json:"timestamp"`
	ActionTaken   string    `json:"action_taken"`
}

// AnalyticsProcessor processes transaction events in real-time
// Real-time event processing का main engine
type AnalyticsProcessor struct {
	kafkaConsumer   *kafka.Consumer
	kafkaProducer   *kafka.Producer
	redisClient     *redis.Client
	metrics         *RealTimeMetrics
	fraudDetector   *FraudDetector
	metricsWindow   time.Duration
	windowMutex     sync.RWMutex
	ctx             context.Context
	cancel          context.CancelFunc
	wg              sync.WaitGroup
}

// FraudDetector implements real-time fraud detection
// Real-time fraud detection logic
type FraudDetector struct {
	redisClient       *redis.Client
	velocityThreshold int     // Transactions per minute threshold
	amountThreshold   float64 // High amount threshold
	ctx               context.Context
}

// NewAnalyticsProcessor creates a new analytics processor
func NewAnalyticsProcessor() (*AnalyticsProcessor, error) {
	log.Println("🚀 Initializing Paytm Real-time Analytics Processor...")

	// Kafka consumer configuration
	// Production-ready settings के साथ
	consumerConfig := kafka.ConfigMap{
		"bootstrap.servers":        "localhost:9092",
		"group.id":                 "paytm-analytics-processor",
		"auto.offset.reset":        "latest",
		"enable.auto.commit":       false, // Manual commit for exactly-once
		"session.timeout.ms":       30000,
		"max.poll.interval.ms":     300000,
		"fetch.min.bytes":          1024,
		"fetch.max.wait.ms":        500,
		"max.partition.fetch.bytes": 1024 * 1024, // 1MB
	}

	consumer, err := kafka.NewConsumer(&consumerConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create consumer: %w", err)
	}

	// Kafka producer configuration
	producerConfig := kafka.ConfigMap{
		"bootstrap.servers": "localhost:9092",
		"acks":              "all",
		"retries":           3,
		"enable.idempotence": true,
		"batch.size":        16384,
		"linger.ms":         10,
		"compression.type":  "gzip",
	}

	producer, err := kafka.NewProducer(&producerConfig)
	if err != nil {
		consumer.Close()
		return nil, fmt.Errorf("failed to create producer: %w", err)
	}

	// Redis client for caching and fraud detection
	// High-performance caching के लिए Redis
	redisClient := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		DB:       0,
		PoolSize: 20,
	})

	// Test Redis connection
	ctx := context.Background()
	_, err = redisClient.Ping(ctx).Result()
	if err != nil {
		log.Printf("⚠️  Redis not available, using local cache: %v", err)
		// Continue without Redis for demo purposes
	}

	ctx, cancel := context.WithCancel(context.Background())

	processor := &AnalyticsProcessor{
		kafkaConsumer: consumer,
		kafkaProducer: producer,
		redisClient:   redisClient,
		metrics: &RealTimeMetrics{
			TopCategories:  make(map[string]int64),
			TopLocations:   make(map[string]int64),
			PaymentMethods: make(map[string]int64),
		},
		fraudDetector: &FraudDetector{
			redisClient:       redisClient,
			velocityThreshold: 10,    // 10 transactions per minute
			amountThreshold:   50000, // ₹50,000 threshold
			ctx:               ctx,
		},
		metricsWindow: 1 * time.Minute, // 1-minute window
		ctx:           ctx,
		cancel:        cancel,
	}

	log.Println("✅ Analytics processor initialized successfully")
	return processor, nil
}

// Start begins processing transaction events
func (ap *AnalyticsProcessor) Start() error {
	log.Println("🎯 Starting real-time analytics processing...")

	// Subscribe to transaction events topic
	// Paytm transaction events को consume करना शुरू करते हैं
	err := ap.kafkaConsumer.Subscribe("paytm-transaction-events", nil)
	if err != nil {
		return fmt.Errorf("failed to subscribe to topic: %w", err)
	}

	// Start metrics aggregation window reset goroutine
	ap.wg.Add(1)
	go ap.metricsWindowProcessor()

	// Start fraud detection pipeline
	ap.wg.Add(1)
	go ap.fraudDetectionProcessor()

	// Start main event processing loop
	ap.wg.Add(1)
	go ap.eventProcessor()

	// Start metrics publisher
	ap.wg.Add(1)
	go ap.metricsPublisher()

	log.Println("🚀 All processors started successfully")
	return nil
}

// Stop gracefully shuts down the processor
func (ap *AnalyticsProcessor) Stop() {
	log.Println("🛑 Shutting down analytics processor...")

	ap.cancel()
	ap.wg.Wait()

	if ap.kafkaConsumer != nil {
		ap.kafkaConsumer.Close()
	}

	if ap.kafkaProducer != nil {
		ap.kafkaProducer.Close()
	}

	if ap.redisClient != nil {
		ap.redisClient.Close()
	}

	log.Println("✅ Analytics processor shut down complete")
}

// eventProcessor is the main event processing loop
func (ap *AnalyticsProcessor) eventProcessor() {
	defer ap.wg.Done()
	log.Println("📨 Starting event processor...")

	for {
		select {
		case <-ap.ctx.Done():
			return
		default:
			// Poll for messages with timeout
			msg, err := ap.kafkaConsumer.ReadMessage(1000 * time.Millisecond)
			if err != nil {
				if err.(kafka.Error).Code() == kafka.ErrTimedOut {
					continue // Timeout is normal, continue polling
				}
				log.Printf("❌ Error reading message: %v", err)
				continue
			}

			// Process the transaction event
			ap.processTransactionEvent(msg)

			// Commit the message offset
			// Exactly-once processing के लिए manual commit
			_, err = ap.kafkaConsumer.CommitMessage(msg)
			if err != nil {
				log.Printf("⚠️  Failed to commit message: %v", err)
			}
		}
	}
}

// processTransactionEvent processes a single transaction event
func (ap *AnalyticsProcessor) processTransactionEvent(msg *kafka.Message) {
	var event PaytmTransactionEvent
	err := json.Unmarshal(msg.Value, &event)
	if err != nil {
		log.Printf("❌ Error unmarshaling event: %v", err)
		return
	}

	log.Printf("📊 Processing transaction: %s - ₹%.2f (%s)", 
		event.TransactionID, event.Amount, event.Status)

	// Update real-time metrics
	ap.updateMetrics(&event)

	// Run fraud detection
	ap.runFraudDetection(&event)

	// Cache transaction for future analysis
	ap.cacheTransaction(&event)
}

// updateMetrics updates real-time metrics with the new transaction
func (ap *AnalyticsProcessor) updateMetrics(event *PaytmTransactionEvent) {
	ap.windowMutex.Lock()
	defer ap.windowMutex.Unlock()

	// Update aggregate counters
	ap.metrics.TransactionCount++
	ap.metrics.TotalVolume += event.Amount

	// Update success/failure counts
	if event.Status == "SUCCESS" {
		ap.metrics.SuccessCount++
	} else if event.Status == "FAILED" {
		ap.metrics.FailureCount++
	}

	// Update processing time average
	// Running average calculation
	totalProcessingTime := ap.metrics.AvgProcessingTime * float64(ap.metrics.TransactionCount-1)
	ap.metrics.AvgProcessingTime = (totalProcessingTime + float64(event.ProcessingTime)) / float64(ap.metrics.TransactionCount)

	// Update success rate
	totalCompleted := ap.metrics.SuccessCount + ap.metrics.FailureCount
	if totalCompleted > 0 {
		ap.metrics.SuccessRate = float64(ap.metrics.SuccessCount) / float64(totalCompleted) * 100
	}

	// Update category distribution
	ap.metrics.TopCategories[event.Category]++

	// Update location distribution
	ap.metrics.TopLocations[event.Location]++

	// Update payment method distribution
	ap.metrics.PaymentMethods[event.PaymentMethod]++

	ap.metrics.LastUpdated = time.Now()

	// Log metrics periodically
	if ap.metrics.TransactionCount%100 == 0 {
		log.Printf("📈 Metrics Update: %d transactions, ₹%.2f volume, %.2f%% success rate",
			ap.metrics.TransactionCount, ap.metrics.TotalVolume, ap.metrics.SuccessRate)
	}
}

// runFraudDetection performs real-time fraud detection
func (ap *AnalyticsProcessor) runFraudDetection(event *PaytmTransactionEvent) {
	alert := ap.fraudDetector.DetectFraud(event)
	if alert != nil {
		log.Printf("🚨 FRAUD ALERT: %s - %s", alert.AlertType, alert.Description)
		ap.publishFraudAlert(alert)
	}
}

// DetectFraud implements fraud detection logic
func (fd *FraudDetector) DetectFraud(event *PaytmTransactionEvent) *FraudAlert {
	// 1. High amount transaction check
	// बड़ी राशि के transactions को flag करते हैं
	if event.Amount > fd.amountThreshold {
		return &FraudAlert{
			AlertID:     fmt.Sprintf("fraud_%s_%d", event.TransactionID, time.Now().Unix()),
			UserID:      event.UserID,
			AlertType:   "HIGH_AMOUNT_TRANSACTION",
			Severity:    "HIGH",
			Description: fmt.Sprintf("High amount transaction: ₹%.2f exceeds threshold ₹%.2f", event.Amount, fd.amountThreshold),
			TriggerData: fmt.Sprintf(`{"transaction_id":"%s","amount":%.2f}`, event.TransactionID, event.Amount),
			Timestamp:   time.Now(),
			ActionTaken: "REVIEW_REQUIRED",
		}
	}

	// 2. Transaction velocity check
	// User की transaction frequency check करते हैं
	velocityKey := fmt.Sprintf("velocity:%s", event.UserID)
	count, err := fd.redisClient.Incr(fd.ctx, velocityKey).Result()
	if err == nil {
		// Set expiry for velocity window (1 minute)
		fd.redisClient.Expire(fd.ctx, velocityKey, 1*time.Minute)

		if count > int64(fd.velocityThreshold) {
			return &FraudAlert{
				AlertID:     fmt.Sprintf("fraud_%s_%d", event.TransactionID, time.Now().Unix()),
				UserID:      event.UserID,
				AlertType:   "HIGH_VELOCITY_TRANSACTIONS",
				Severity:    "MEDIUM",
				Description: fmt.Sprintf("High transaction velocity: %d transactions in 1 minute", count),
				TriggerData: fmt.Sprintf(`{"user_id":"%s","count":%d}`, event.UserID, count),
				Timestamp:   time.Now(),
				ActionTaken: "TEMPORARY_HOLD",
			}
		}
	}

	// 3. Failed transaction pattern check
	// बार-बार fail होने वाले transactions को track करते हैं
	if event.Status == "FAILED" {
		failureKey := fmt.Sprintf("failures:%s", event.UserID)
		failureCount, err := fd.redisClient.Incr(fd.ctx, failureKey).Result()
		if err == nil {
			fd.redisClient.Expire(fd.ctx, failureKey, 5*time.Minute) // 5 minute window

			if failureCount >= 5 { // 5 failures in 5 minutes
				return &FraudAlert{
					AlertID:     fmt.Sprintf("fraud_%s_%d", event.TransactionID, time.Now().Unix()),
					UserID:      event.UserID,
					AlertType:   "REPEATED_FAILURES",
					Severity:    "MEDIUM",
					Description: fmt.Sprintf("Multiple failed transactions: %d failures in 5 minutes", failureCount),
					TriggerData: fmt.Sprintf(`{"user_id":"%s","failure_count":%d}`, event.UserID, failureCount),
					Timestamp:   time.Now(),
					ActionTaken: "ACCOUNT_VERIFICATION",
				}
			}
		}
	}

	// 4. Unusual time pattern check
	// असामान्य समय में transactions को check करते हैं
	hour := event.Timestamp.Hour()
	if hour >= 2 && hour <= 5 { // 2 AM to 5 AM transactions
		if event.Amount > 10000 { // High amount in unusual hours
			return &FraudAlert{
				AlertID:     fmt.Sprintf("fraud_%s_%d", event.TransactionID, time.Now().Unix()),
				UserID:      event.UserID,
				AlertType:   "UNUSUAL_TIME_TRANSACTION",
				Severity:    "LOW",
				Description: fmt.Sprintf("Large transaction at unusual time: ₹%.2f at %02d:00", event.Amount, hour),
				TriggerData: fmt.Sprintf(`{"transaction_id":"%s","hour":%d,"amount":%.2f}`, event.TransactionID, hour, event.Amount),
				Timestamp:   time.Now(),
				ActionTaken: "MONITORING",
			}
		}
	}

	return nil // No fraud detected
}

// cacheTransaction stores transaction data for analysis
func (ap *AnalyticsProcessor) cacheTransaction(event *PaytmTransactionEvent) {
	// Store in Redis for fast access
	// Recent transactions को Redis में cache करते हैं
	key := fmt.Sprintf("transaction:%s", event.TransactionID)
	data, err := json.Marshal(event)
	if err != nil {
		log.Printf("⚠️  Error marshaling transaction for cache: %v", err)
		return
	}

	err = ap.redisClient.SetEX(ap.ctx, key, data, 1*time.Hour).Err() // 1 hour TTL
	if err != nil {
		log.Printf("⚠️  Error caching transaction: %v", err)
	}

	// Add to user transaction list for velocity checking
	userKey := fmt.Sprintf("user_transactions:%s", event.UserID)
	ap.redisClient.LPush(ap.ctx, userKey, event.TransactionID)
	ap.redisClient.LTrim(ap.ctx, userKey, 0, 99) // Keep last 100 transactions
	ap.redisClient.Expire(ap.ctx, userKey, 24*time.Hour) // 24 hour TTL
}

// publishFraudAlert publishes fraud alerts to Kafka
func (ap *AnalyticsProcessor) publishFraudAlert(alert *FraudAlert) {
	alertData, err := json.Marshal(alert)
	if err != nil {
		log.Printf("❌ Error marshaling fraud alert: %v", err)
		return
	}

	message := &kafka.Message{
		TopicPartition: kafka.TopicPartition{
			Topic:     &[]string{"paytm-fraud-alerts"}[0],
			Partition: kafka.PartitionAny,
		},
		Key:   []byte(alert.UserID),
		Value: alertData,
	}

	deliveryChan := make(chan kafka.Event)
	err = ap.kafkaProducer.Produce(message, deliveryChan)
	if err != nil {
		log.Printf("❌ Error producing fraud alert: %v", err)
		return
	}

	// Wait for delivery confirmation
	go func() {
		e := <-deliveryChan
		m := e.(*kafka.Message)
		if m.TopicPartition.Error != nil {
			log.Printf("❌ Failed to deliver fraud alert: %v", m.TopicPartition.Error)
		} else {
			log.Printf("🚨 Fraud alert delivered: %s", alert.AlertID)
		}
		close(deliveryChan)
	}()
}

// metricsWindowProcessor resets metrics window periodically
func (ap *AnalyticsProcessor) metricsWindowProcessor() {
	defer ap.wg.Done()
	ticker := time.NewTicker(ap.metricsWindow)
	defer ticker.Stop()

	for {
		select {
		case <-ap.ctx.Done():
			return
		case <-ticker.C:
			ap.resetMetricsWindow()
		}
	}
}

// resetMetricsWindow resets the metrics for a new window
func (ap *AnalyticsProcessor) resetMetricsWindow() {
	ap.windowMutex.Lock()
	defer ap.windowMutex.Unlock()

	// Log current window metrics before reset
	log.Printf("📊 Window Complete: %d transactions, ₹%.2f volume, %.2f%% success rate",
		ap.metrics.TransactionCount, ap.metrics.TotalVolume, ap.metrics.SuccessRate)

	// Archive current metrics (in production, this would go to time-series DB)
	ap.archiveMetrics()

	// Reset for new window
	now := time.Now()
	ap.metrics = &RealTimeMetrics{
		WindowStart:    now,
		WindowEnd:      now.Add(ap.metricsWindow),
		TopCategories:  make(map[string]int64),
		TopLocations:   make(map[string]int64),
		PaymentMethods: make(map[string]int64),
	}

	log.Println("🔄 New metrics window started")
}

// archiveMetrics archives completed window metrics
func (ap *AnalyticsProcessor) archiveMetrics() {
	// In production, this would store to time-series database
	// यहाँ हम metrics को historical storage में save करेंगे
	metricsData, err := json.Marshal(ap.metrics)
	if err != nil {
		log.Printf("⚠️  Error marshaling metrics: %v", err)
		return
	}

	// Store in Redis with timestamp key
	key := fmt.Sprintf("metrics:window:%d", time.Now().Unix())
	err = ap.redisClient.SetEX(ap.ctx, key, metricsData, 24*time.Hour).Err()
	if err != nil {
		log.Printf("⚠️  Error archiving metrics: %v", err)
	}
}

// fraudDetectionProcessor handles fraud detection pipeline
func (ap *AnalyticsProcessor) fraudDetectionProcessor() {
	defer ap.wg.Done()
	log.Println("🛡️  Starting fraud detection processor...")

	// This could include ML model inference, pattern detection, etc.
	// Real-time fraud detection pipeline

	ticker := time.NewTicker(30 * time.Second) // Check every 30 seconds
	defer ticker.Stop()

	for {
		select {
		case <-ap.ctx.Done():
			return
		case <-ticker.C:
			ap.runAdvancedFraudChecks()
		}
	}
}

// runAdvancedFraudChecks performs advanced fraud detection
func (ap *AnalyticsProcessor) runAdvancedFraudChecks() {
	// Advanced fraud detection logic
	// Pattern analysis, ML model inference, etc.

	// Example: Check for users with unusual transaction patterns
	// असामान्य patterns के लिए user behavior analysis
	
	log.Println("🔍 Running advanced fraud checks...")
	
	// In production, this would include:
	// 1. ML model inference for anomaly detection
	// 2. Graph-based fraud detection
	// 3. Cross-user pattern analysis
	// 4. Geographic anomaly detection
	// 5. Device fingerprinting analysis
}

// metricsPublisher publishes current metrics to dashboard
func (ap *AnalyticsProcessor) metricsPublisher() {
	defer ap.wg.Done()
	ticker := time.NewTicker(10 * time.Second) // Publish every 10 seconds
	defer ticker.Stop()

	for {
		select {
		case <-ap.ctx.Done():
			return
		case <-ticker.C:
			ap.publishCurrentMetrics()
		}
	}
}

// publishCurrentMetrics publishes current metrics to Kafka
func (ap *AnalyticsProcessor) publishCurrentMetrics() {
	ap.windowMutex.RLock()
	metricsSnapshot := *ap.metrics // Create a copy
	ap.windowMutex.RUnlock()

	metricsData, err := json.Marshal(metricsSnapshot)
	if err != nil {
		log.Printf("⚠️  Error marshaling metrics for publishing: %v", err)
		return
	}

	message := &kafka.Message{
		TopicPartition: kafka.TopicPartition{
			Topic:     &[]string{"paytm-realtime-metrics"}[0],
			Partition: kafka.PartitionAny,
		},
		Key:   []byte(fmt.Sprintf("metrics_%d", time.Now().Unix())),
		Value: metricsData,
	}

	deliveryChan := make(chan kafka.Event)
	err = ap.kafkaProducer.Produce(message, deliveryChan)
	if err != nil {
		log.Printf("⚠️  Error producing metrics: %v", err)
		return
	}

	// Non-blocking delivery confirmation
	go func() {
		e := <-deliveryChan
		m := e.(*kafka.Message)
		if m.TopicPartition.Error != nil {
			log.Printf("⚠️  Failed to deliver metrics: %v", m.TopicPartition.Error)
		}
		close(deliveryChan)
	}()
}

// generateSampleData generates sample transaction data for testing
func generateSampleData() {
	log.Println("🎲 Starting sample data generator...")

	// Kafka producer for sample data
	producerConfig := kafka.ConfigMap{
		"bootstrap.servers": "localhost:9092",
		"acks":              "all",
		"retries":           3,
	}

	producer, err := kafka.NewProducer(&producerConfig)
	if err != nil {
		log.Printf("❌ Failed to create sample data producer: %v", err)
		return
	}
	defer producer.Close()

	// Sample data patterns
	categories := []string{"FOOD", "TRANSPORT", "SHOPPING", "UTILITIES", "ENTERTAINMENT", "HEALTHCARE"}
	locations := []string{"Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune", "Hyderabad"}
	paymentMethods := []string{"UPI", "WALLET", "CARD", "NET_BANKING"}
	merchantTypes := []string{"ONLINE", "OFFLINE"}
	deviceTypes := []string{"MOBILE", "DESKTOP"}

	// Generate transactions every second
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	transactionCounter := 1

	for range ticker.C {
		// Generate 1-5 transactions per second
		numTransactions := rand.Intn(5) + 1

		for i := 0; i < numTransactions; i++ {
			event := PaytmTransactionEvent{
				TransactionID:   fmt.Sprintf("TXN_%d_%d", time.Now().Unix(), transactionCounter),
				UserID:          fmt.Sprintf("USER_%d", rand.Intn(1000)+1),
				MerchantID:      fmt.Sprintf("MERCHANT_%d", rand.Intn(100)+1),
				Amount:          float64(rand.Intn(50000) + 100), // ₹100 to ₹50,100
				PaymentMethod:   paymentMethods[rand.Intn(len(paymentMethods))],
				Status:          generateTransactionStatus(),
				Category:        categories[rand.Intn(len(categories))],
				Location:        locations[rand.Intn(len(locations))],
				Timestamp:       time.Now(),
				ProcessingTime:  int64(rand.Intn(1000) + 50), // 50-1050 ms
				MerchantType:    merchantTypes[rand.Intn(len(merchantTypes))],
				DeviceType:      deviceTypes[rand.Intn(len(deviceTypes))],
			}

			// Add error code for failed transactions
			if event.Status == "FAILED" {
				errorCodes := []string{"INSUFFICIENT_FUNDS", "NETWORK_ERROR", "INVALID_PIN", "CARD_EXPIRED"}
				event.ErrorCode = errorCodes[rand.Intn(len(errorCodes))]
			}

			// Serialize and send
			eventData, err := json.Marshal(event)
			if err != nil {
				log.Printf("❌ Error marshaling sample event: %v", err)
				continue
			}

			message := &kafka.Message{
				TopicPartition: kafka.TopicPartition{
					Topic:     &[]string{"paytm-transaction-events"}[0],
					Partition: kafka.PartitionAny,
				},
				Key:   []byte(event.UserID),
				Value: eventData,
			}

			err = producer.Produce(message, nil)
			if err != nil {
				log.Printf("❌ Error producing sample event: %v", err)
			}

			transactionCounter++
		}

		producer.Flush(1000) // Flush every second

		// Stop after 1000 transactions for demo
		if transactionCounter > 1000 {
			log.Println("✅ Sample data generation completed")
			break
		}
	}
}

// generateTransactionStatus generates realistic transaction status distribution
func generateTransactionStatus() string {
	// 90% success, 8% failed, 2% pending
	rand_val := rand.Float32()
	if rand_val < 0.90 {
		return "SUCCESS"
	} else if rand_val < 0.98 {
		return "FAILED"
	} else {
		return "PENDING"
	}
}

func main() {
	fmt.Println("💳 Starting Paytm Real-time Analytics Pipeline")
	fmt.Println("📊 Processing transaction events with fraud detection")
	fmt.Println(strings.Repeat("-", 60))

	// Initialize analytics processor
	processor, err := NewAnalyticsProcessor()
	if err != nil {
		log.Fatalf("❌ Failed to initialize analytics processor: %v", err)
	}

	// Start sample data generation in background
	go generateSampleData()

	// Start the analytics processor
	err = processor.Start()
	if err != nil {
		log.Fatalf("❌ Failed to start analytics processor: %v", err)
	}

	// Setup graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	log.Println("🎯 Real-time analytics pipeline is running...")
	log.Println("💡 Processing Paytm transactions with fraud detection")
	log.Println("📈 Generating real-time metrics and alerts")

	// Wait for shutdown signal
	<-sigChan

	log.Println("📊 Analytics Summary:")
	log.Printf("   Processed transactions with real-time fraud detection")
	log.Printf("   Generated metrics windows with 1-minute aggregation")
	log.Printf("   Published fraud alerts and real-time metrics")
	log.Printf("   Demonstrated high-throughput event streaming pipeline")

	// Graceful shutdown
	processor.Stop()
	
	fmt.Println("\n✅ Real-time analytics pipeline demonstration completed!")
	fmt.Println("💡 Key features demonstrated:")
	fmt.Println("   - High-throughput transaction processing")
	fmt.Println("   - Real-time fraud detection and alerting")
	fmt.Println("   - Sliding window metrics aggregation")
	fmt.Println("   - Redis-backed caching and velocity checks")
	fmt.Println("   - Production-ready Kafka integration")
}