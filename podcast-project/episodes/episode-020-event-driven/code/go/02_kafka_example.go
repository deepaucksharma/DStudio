package main

/*
Apache Kafka Producer/Consumer Example - Go Implementation
उदाहरण: ICICI Bank के transaction events को Kafka के through handle करना

Setup:
go mod init kafka-banking-example
go get github.com/IBM/sarama
go get github.com/google/uuid

Indian Context: ICICI Bank app में जब transaction होता है,
multiple services को real-time notification चाहिए:
- Fraud detection service
- SMS notification service
- Balance update service
- Analytics service
- Regulatory reporting

Kafka Benefits:
- High throughput message processing
- Fault tolerance and durability
- Horizontal scalability
- Event ordering guarantees
*/

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strconv"
	"sync"
	"syscall"
	"time"

	"github.com/IBM/sarama"
	"github.com/google/uuid"
)

// Transaction event structure
type BankTransaction struct {
	TransactionID   string    `json:"transaction_id"`
	AccountNumber   string    `json:"account_number"`
	TransactionType string    `json:"transaction_type"` // DEBIT/CREDIT/TRANSFER
	Amount          float64   `json:"amount"`
	Currency        string    `json:"currency"`
	Description     string    `json:"description"`
	Timestamp       time.Time `json:"timestamp"`
	BranchCode      string    `json:"branch_code"`
	CustomerID      string    `json:"customer_id"`
	BalanceAfter    float64   `json:"balance_after"`
}

// Kafka Producer for banking transactions
type BankingKafkaProducer struct {
	producer sarama.SyncProducer
	topic    string
}

func NewBankingKafkaProducer(brokers []string, topic string) (*BankingKafkaProducer, error) {
	config := sarama.NewConfig()
	
	// Producer configuration for reliability
	config.Producer.RequiredAcks = sarama.WaitForAll // Wait for all replicas
	config.Producer.Retry.Max = 3
	config.Producer.Return.Successes = true
	config.Producer.Return.Errors = true
	
	// Idempotency for exactly-once semantics
	config.Producer.Idempotent = true
	config.Net.MaxOpenRequests = 1
	
	// Compression for better throughput
	config.Producer.Compression = sarama.CompressionGZIP
	
	// Batching for performance
	config.Producer.Flush.Frequency = 10 * time.Millisecond
	config.Producer.Flush.Messages = 100
	
	producer, err := sarama.NewSyncProducer(brokers, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create producer: %w", err)
	}
	
	log.Printf("✅ Banking Kafka producer initialized for topic: %s", topic)
	
	return &BankingKafkaProducer{
		producer: producer,
		topic:    topic,
	}, nil
}

func (p *BankingKafkaProducer) PublishTransaction(transaction BankTransaction) error {
	// Serialize transaction to JSON
	transactionJSON, err := json.Marshal(transaction)
	if err != nil {
		return fmt.Errorf("failed to marshal transaction: %w", err)
	}
	
	// Create Kafka message
	msg := &sarama.ProducerMessage{
		Topic: p.topic,
		Key:   sarama.StringEncoder(transaction.AccountNumber), // Partition by account
		Value: sarama.ByteEncoder(transactionJSON),
		Headers: []sarama.RecordHeader{
			{
				Key:   []byte("transaction_type"),
				Value: []byte(transaction.TransactionType),
			},
			{
				Key:   []byte("customer_id"),
				Value: []byte(transaction.CustomerID),
			},
		},
		Timestamp: transaction.Timestamp,
	}
	
	// Send message
	partition, offset, err := p.producer.SendMessage(msg)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}
	
	log.Printf("💳 Transaction published: %s to partition %d, offset %d", 
		transaction.TransactionID, partition, offset)
	
	return nil
}

func (p *BankingKafkaProducer) Close() error {
	return p.producer.Close()
}

// Kafka Consumer for different banking services
type BankingKafkaConsumer struct {
	consumer      sarama.ConsumerGroup
	topic         string
	consumerGroup string
	handler       ConsumerGroupHandler
}

type ConsumerGroupHandler struct {
	serviceName string
	processor   func(BankTransaction) error
}

func (h *ConsumerGroupHandler) Setup(sarama.ConsumerGroupSession) error {
	log.Printf("🎧 %s consumer group session started", h.serviceName)
	return nil
}

func (h *ConsumerGroupHandler) Cleanup(sarama.ConsumerGroupSession) error {
	log.Printf("🔴 %s consumer group session ended", h.serviceName)
	return nil
}

func (h *ConsumerGroupHandler) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
	for {
		select {
		case message := <-claim.Messages():
			if message == nil {
				return nil
			}
			
			// Deserialize transaction
			var transaction BankTransaction
			if err := json.Unmarshal(message.Value, &transaction); err != nil {
				log.Printf("❌ %s: Failed to unmarshal message: %v", h.serviceName, err)
				session.MarkMessage(message, "")
				continue
			}
			
			log.Printf("📨 %s: Processing transaction %s", h.serviceName, transaction.TransactionID)
			
			// Process transaction
			if err := h.processor(transaction); err != nil {
				log.Printf("❌ %s: Processing failed: %v", h.serviceName, err)
				// In production, you might want to send to DLQ instead of marking
			} else {
				log.Printf("✅ %s: Transaction processed successfully", h.serviceName)
			}
			
			// Mark message as processed
			session.MarkMessage(message, "")
			
		case <-session.Context().Done():
			return nil
		}
	}
}

func NewBankingKafkaConsumer(brokers []string, topic, consumerGroup, serviceName string, 
	processor func(BankTransaction) error) (*BankingKafkaConsumer, error) {
	
	config := sarama.NewConfig()
	
	// Consumer configuration
	config.Consumer.Group.Rebalance.Strategy = sarama.BalanceStrategyRoundRobin
	config.Consumer.Offsets.Initial = sarama.OffsetNewest
	config.Consumer.Group.Session.Timeout = 30 * time.Second
	config.Consumer.Group.Heartbeat.Interval = 10 * time.Second
	
	// Enable manual commit for better control
	config.Consumer.Offsets.AutoCommit.Enable = true
	config.Consumer.Offsets.AutoCommit.Interval = 1 * time.Second
	
	consumer, err := sarama.NewConsumerGroup(brokers, consumerGroup, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create consumer group: %w", err)
	}
	
	handler := &ConsumerGroupHandler{
		serviceName: serviceName,
		processor:   processor,
	}
	
	log.Printf("✅ %s consumer initialized for topic: %s, group: %s", 
		serviceName, topic, consumerGroup)
	
	return &BankingKafkaConsumer{
		consumer:      consumer,
		topic:         topic,
		consumerGroup: consumerGroup,
		handler:       *handler,
	}, nil
}

func (c *BankingKafkaConsumer) Start(ctx context.Context) error {
	for {
		select {
		case <-ctx.Done():
			log.Printf("🛑 %s consumer stopping due to context cancellation", c.handler.serviceName)
			return ctx.Err()
		default:
			if err := c.consumer.Consume(ctx, []string{c.topic}, &c.handler); err != nil {
				log.Printf("❌ %s consumer error: %v", c.handler.serviceName, err)
				return err
			}
		}
	}
}

func (c *BankingKafkaConsumer) Close() error {
	return c.consumer.Close()
}

// Banking services that process transactions

// Fraud Detection Service
func processFraudDetection(transaction BankTransaction) error {
	log.Printf("🔍 Fraud Detection: Analyzing transaction %s", transaction.TransactionID)
	log.Printf("   💰 Amount: ₹%.2f", transaction.Amount)
	log.Printf("   🏦 Account: %s", transaction.AccountNumber)
	
	// Simulate fraud analysis
	time.Sleep(200 * time.Millisecond)
	
	// Risk assessment based on amount and time
	riskScore := 0
	
	// High amount transactions
	if transaction.Amount > 100000 {
		riskScore += 30
		log.Printf("   ⚠️ High amount transaction detected")
	}
	
	// Late night transactions
	hour := transaction.Timestamp.Hour()
	if hour < 6 || hour > 22 {
		riskScore += 20
		log.Printf("   ⚠️ Off-hours transaction detected")
	}
	
	// ATM withdrawals
	if transaction.TransactionType == "DEBIT" && transaction.Description == "ATM Withdrawal" {
		riskScore += 10
	}
	
	if riskScore > 40 {
		log.Printf("🚨 HIGH RISK transaction flagged: %s (Score: %d)", 
			transaction.TransactionID, riskScore)
		// In production, this would trigger alerts
	} else {
		log.Printf("✅ Transaction cleared: %s (Score: %d)", 
			transaction.TransactionID, riskScore)
	}
	
	return nil
}

// SMS Notification Service
func processSMSNotification(transaction BankTransaction) error {
	log.Printf("📱 SMS Service: Sending notification for %s", transaction.TransactionID)
	log.Printf("   👤 Customer: %s", transaction.CustomerID)
	log.Printf("   💸 Type: %s", transaction.TransactionType)
	
	// Simulate SMS sending
	time.Sleep(300 * time.Millisecond)
	
	// Create SMS content based on transaction type
	var smsContent string
	switch transaction.TransactionType {
	case "DEBIT":
		smsContent = fmt.Sprintf("ICICI Bank: Rs %.2f debited from A/C %s on %s. Balance: Rs %.2f", 
			transaction.Amount, 
			maskAccountNumber(transaction.AccountNumber),
			transaction.Timestamp.Format("02-Jan-06 15:04"),
			transaction.BalanceAfter)
	case "CREDIT":
		smsContent = fmt.Sprintf("ICICI Bank: Rs %.2f credited to A/C %s on %s. Balance: Rs %.2f", 
			transaction.Amount,
			maskAccountNumber(transaction.AccountNumber), 
			transaction.Timestamp.Format("02-Jan-06 15:04"),
			transaction.BalanceAfter)
	case "TRANSFER":
		smsContent = fmt.Sprintf("ICICI Bank: Rs %.2f transferred from A/C %s on %s. Balance: Rs %.2f", 
			transaction.Amount,
			maskAccountNumber(transaction.AccountNumber),
			transaction.Timestamp.Format("02-Jan-06 15:04"),
			transaction.BalanceAfter)
	}
	
	log.Printf("✅ SMS sent: %s", smsContent)
	return nil
}

// Balance Update Service
func processBalanceUpdate(transaction BankTransaction) error {
	log.Printf("💰 Balance Service: Updating balance for %s", transaction.TransactionID)
	log.Printf("   🏦 Account: %s", transaction.AccountNumber)
	log.Printf("   💹 New Balance: ₹%.2f", transaction.BalanceAfter)
	
	// Simulate database update
	time.Sleep(150 * time.Millisecond)
	
	// In production, this would update the account balance in database
	log.Printf("✅ Balance updated for account %s", maskAccountNumber(transaction.AccountNumber))
	return nil
}

// Analytics Service
func processAnalytics(transaction BankTransaction) error {
	log.Printf("📊 Analytics: Recording metrics for %s", transaction.TransactionID)
	
	// Simulate analytics processing
	time.Sleep(100 * time.Millisecond)
	
	// Track metrics by transaction type
	metrics := map[string]interface{}{
		"transaction_type": transaction.TransactionType,
		"amount":          transaction.Amount,
		"branch_code":     transaction.BranchCode,
		"hour":            transaction.Timestamp.Hour(),
		"day_of_week":     transaction.Timestamp.Weekday().String(),
	}
	
	log.Printf("📈 Metrics recorded: %+v", metrics)
	return nil
}

// Utility function to mask account number
func maskAccountNumber(accountNumber string) string {
	if len(accountNumber) < 4 {
		return accountNumber
	}
	return "****" + accountNumber[len(accountNumber)-4:]
}

// Transaction generator for demo
func generateSampleTransactions() []BankTransaction {
	accounts := []string{
		"1234567890123456",
		"2345678901234567", 
		"3456789012345678",
		"4567890123456789",
	}
	
	customers := []string{
		"CUST_RAHUL_001",
		"CUST_PRIYA_002", 
		"CUST_AMIT_003",
		"CUST_NEHA_004",
	}
	
	transactionTypes := []string{"DEBIT", "CREDIT", "TRANSFER"}
	descriptions := map[string][]string{
		"DEBIT":    {"ATM Withdrawal", "Online Purchase", "Bill Payment", "EMI Deduction"},
		"CREDIT":   {"Salary Credit", "Fund Transfer", "Interest Credit", "Refund"},
		"TRANSFER": {"NEFT Transfer", "IMPS Transfer", "UPI Transfer", "Internal Transfer"},
	}
	
	branches := []string{"MUM001", "DEL002", "BLR003", "CHN004", "KOL005"}
	
	var transactions []BankTransaction
	
	for i := 0; i < 20; i++ {
		accountIdx := i % len(accounts)
		customerIdx := i % len(customers)
		
		txnType := transactionTypes[i%len(transactionTypes)]
		desc := descriptions[txnType][i%len(descriptions[txnType])]
		
		// Generate realistic amounts
		var amount float64
		switch txnType {
		case "DEBIT":
			amount = float64(500 + (i*123)%50000) // ₹500 to ₹50,000
		case "CREDIT":
			amount = float64(1000 + (i*456)%100000) // ₹1,000 to ₹1,00,000
		case "TRANSFER":
			amount = float64(100 + (i*789)%25000) // ₹100 to ₹25,000
		}
		
		// Simulate balance after transaction
		baseBalance := float64(50000 + (accountIdx * 25000))
		var balanceAfter float64
		if txnType == "DEBIT" || txnType == "TRANSFER" {
			balanceAfter = baseBalance - amount
		} else {
			balanceAfter = baseBalance + amount
		}
		
		transaction := BankTransaction{
			TransactionID:   fmt.Sprintf("TXN_%s", uuid.New().String()[:8]),
			AccountNumber:   accounts[accountIdx],
			TransactionType: txnType,
			Amount:          amount,
			Currency:        "INR",
			Description:     desc,
			Timestamp:       time.Now().Add(time.Duration(i) * time.Second),
			BranchCode:      branches[i%len(branches)],
			CustomerID:      customers[customerIdx],
			BalanceAfter:    balanceAfter,
		}
		
		transactions = append(transactions, transaction)
	}
	
	return transactions
}

func main() {
	fmt.Println("🏦 ICICI Bank Kafka Event-Driven Transaction Processing")
	fmt.Println("=" + string(make([]byte, 60)))
	fmt.Println("📋 Make sure Kafka is running on localhost:9092")
	fmt.Println()
	
	brokers := []string{"localhost:9092"}
	topic := "icici-bank-transactions"
	
	// Create producer
	producer, err := NewBankingKafkaProducer(brokers, topic)
	if err != nil {
		log.Fatalf("❌ Failed to create producer: %v", err)
	}
	defer producer.Close()
	
	// Create consumers for different services
	services := []struct {
		name      string
		group     string
		processor func(BankTransaction) error
	}{
		{"Fraud Detection", "fraud-detection-service", processFraudDetection},
		{"SMS Notification", "sms-notification-service", processSMSNotification}, 
		{"Balance Update", "balance-update-service", processBalanceUpdate},
		{"Analytics", "analytics-service", processAnalytics},
	}
	
	// Start all consumer services
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	var wg sync.WaitGroup
	
	for _, service := range services {
		consumer, err := NewBankingKafkaConsumer(brokers, topic, service.group, service.name, service.processor)
		if err != nil {
			log.Fatalf("❌ Failed to create %s consumer: %v", service.name, err)
		}
		
		wg.Add(1)
		go func(c *BankingKafkaConsumer) {
			defer wg.Done()
			defer c.Close()
			
			if err := c.Start(ctx); err != nil && err != context.Canceled {
				log.Printf("❌ %s consumer error: %v", c.handler.serviceName, err)
			}
		}(consumer)
	}
	
	// Wait for consumers to initialize
	time.Sleep(3 * time.Second)
	
	// Generate and publish sample transactions
	fmt.Println("🚀 Starting transaction processing simulation...")
	transactions := generateSampleTransactions()
	
	fmt.Printf("📤 Publishing %d transactions...\n", len(transactions))
	
	for i, transaction := range transactions {
		if err := producer.PublishTransaction(transaction); err != nil {
			log.Printf("❌ Failed to publish transaction %d: %v", i+1, err)
		} else {
			fmt.Printf("✅ Published transaction %d/%d: %s (₹%.2f)\n", 
				i+1, len(transactions), transaction.TransactionID, transaction.Amount)
		}
		
		// Small delay between transactions
		time.Sleep(500 * time.Millisecond)
	}
	
	fmt.Println("\n⏳ Processing transactions for 30 seconds...")
	
	// Setup graceful shutdown
	sigterm := make(chan os.Signal, 1)
	signal.Notify(sigterm, syscall.SIGINT, syscall.SIGTERM)
	
	// Wait for either timeout or signal
	select {
	case <-time.After(30 * time.Second):
		fmt.Println("\n⏰ Demo completed after 30 seconds")
	case <-sigterm:
		fmt.Println("\n🛑 Demo interrupted by signal")
	}
	
	// Graceful shutdown
	fmt.Println("\n🧹 Shutting down services...")
	cancel()
	
	// Wait for all consumers to stop
	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()
	
	select {
	case <-done:
		fmt.Println("✅ All services stopped gracefully")
	case <-time.After(10 * time.Second):
		fmt.Println("⚠️ Forced shutdown after timeout")
	}
	
	fmt.Println("\n🎯 Kafka Benefits Demonstrated:")
	fmt.Println("   ✅ High-throughput message processing")
	fmt.Println("   ✅ Fault-tolerant event streaming") 
	fmt.Println("   ✅ Consumer group load balancing")
	fmt.Println("   ✅ Message ordering per partition")
	fmt.Println("   ✅ Horizontal scalability")
	fmt.Println("   ✅ Exactly-once semantics")
}