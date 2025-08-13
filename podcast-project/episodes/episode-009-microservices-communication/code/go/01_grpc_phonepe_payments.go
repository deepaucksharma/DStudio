/*
gRPC Payment Service in Go for PhonePe-style UPI Payments
High-performance microservice with streaming and error handling

Author: Episode 9 - Microservices Communication
Context: PhonePe jaise UPI payment system - Go mein gRPC implementation
*/

package main

import (
	"context"
	"crypto/rand"
	"fmt"
	"log"
	"net"
	"sync"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// Payment status enum
type PaymentStatus int32

const (
	PaymentStatus_PENDING PaymentStatus = iota
	PaymentStatus_SUCCESS
	PaymentStatus_FAILED
	PaymentStatus_TIMEOUT
)

func (s PaymentStatus) String() string {
	switch s {
	case PaymentStatus_PENDING:
		return "PENDING"
	case PaymentStatus_SUCCESS:
		return "SUCCESS"
	case PaymentStatus_FAILED:
		return "FAILED"
	case PaymentStatus_TIMEOUT:
		return "TIMEOUT"
	default:
		return "UNKNOWN"
	}
}

// UPI Provider enum
type UpiProvider int32

const (
	UpiProvider_PHONEPE UpiProvider = iota
	UpiProvider_GPAY
	UpiProvider_PAYTM
	UpiProvider_BHIM
)

func (p UpiProvider) String() string {
	switch p {
	case UpiProvider_PHONEPE:
		return "PHONEPE"
	case UpiProvider_GPAY:
		return "GPAY"
	case UpiProvider_PAYTM:
		return "PAYTM"
	case UpiProvider_BHIM:
		return "BHIM"
	default:
		return "UNKNOWN"
	}
}

// gRPC Request/Response structures (normally generated from .proto files)

type PaymentRequest struct {
	PaymentId     string      `json:"payment_id"`
	FromUpiId     string      `json:"from_upi_id"`
	ToUpiId       string      `json:"to_upi_id"`
	Amount        int64       `json:"amount"` // Amount in paisa (₹1 = 100 paisa)
	Currency      string      `json:"currency"`
	Description   string      `json:"description"`
	Provider      UpiProvider `json:"provider"`
	RequestTime   int64       `json:"request_time"`
}

type PaymentResponse struct {
	PaymentId       string        `json:"payment_id"`
	TransactionId   string        `json:"transaction_id"`
	Status          PaymentStatus `json:"status"`
	Message         string        `json:"message"`
	ProcessingTime  int64         `json:"processing_time"` // in milliseconds
	ResponseTime    int64         `json:"response_time"`
}

type BalanceRequest struct {
	UpiId string `json:"upi_id"`
}

type BalanceResponse struct {
	UpiId         string `json:"upi_id"`
	Balance       int64  `json:"balance"` // in paisa
	Currency      string `json:"currency"`
	LastUpdated   int64  `json:"last_updated"`
}

type TransactionHistoryRequest struct {
	UpiId  string `json:"upi_id"`
	Limit  int32  `json:"limit"`
	Offset int32  `json:"offset"`
}

type TransactionHistoryResponse struct {
	Transactions []*PaymentResponse `json:"transactions"`
	TotalCount   int32              `json:"total_count"`
}

// gRPC Service Interface (normally generated)
type PaymentServiceServer interface {
	ProcessPayment(ctx context.Context, req *PaymentRequest) (*PaymentResponse, error)
	GetBalance(ctx context.Context, req *BalanceRequest) (*BalanceResponse, error)
	GetTransactionHistory(ctx context.Context, req *TransactionHistoryRequest) (*TransactionHistoryResponse, error)
	ProcessBulkPayments(stream BulkPaymentStream) error
	StreamPaymentStatus(req *PaymentRequest, stream PaymentStatusStream) error
}

// Mock streaming interfaces
type BulkPaymentStream interface {
	Recv() (*PaymentRequest, error)
	Send(*PaymentResponse) error
}

type PaymentStatusStream interface {
	Send(*PaymentResponse) error
}

// PhonePe Payment Service Implementation
type PhonePePaymentService struct {
	// In-memory storage (production mein database hoga)
	balances     map[string]int64 // UPI ID -> balance in paisa
	transactions map[string][]*PaymentResponse
	mutex        sync.RWMutex
	
	// Performance metrics
	totalTransactions int64
	successfulCount   int64
	failureCount      int64
}

// NewPhonePePaymentService creates new payment service instance
func NewPhonePePaymentService() *PhonePePaymentService {
	service := &PhonePePaymentService{
		balances:     make(map[string]int64),
		transactions: make(map[string][]*PaymentResponse),
	}
	
	// Demo accounts create karte hai with initial balance
	demoAccounts := map[string]int64{
		"rahul@phonepe":    500000, // ₹5000.00
		"priya@phonepe":    300000, // ₹3000.00
		"amit@phonepe":     800000, // ₹8000.00
		"sneha@phonepe":    150000, // ₹1500.00
		"merchant@zomato":  5000000, // ₹50000.00
		"merchant@ola":     2500000, // ₹25000.00
	}
	
	for upiId, balance := range demoAccounts {
		service.balances[upiId] = balance
		service.transactions[upiId] = make([]*PaymentResponse, 0)
	}
	
	log.Printf("PhonePe Payment Service initialized with %d demo accounts", len(demoAccounts))
	return service
}

// ProcessPayment handles UPI payment requests
func (s *PhonePePaymentService) ProcessPayment(ctx context.Context, req *PaymentRequest) (*PaymentResponse, error) {
	startTime := time.Now()
	
	// Input validation
	if req.FromUpiId == "" || req.ToUpiId == "" {
		return nil, status.Errorf(codes.InvalidArgument, "UPI IDs cannot be empty")
	}
	
	if req.Amount <= 0 {
		return nil, status.Errorf(codes.InvalidArgument, "Amount must be positive")
	}
	
	if req.FromUpiId == req.ToUpiId {
		return nil, status.Errorf(codes.InvalidArgument, "Self-payment not allowed")
	}
	
	// Check for context cancellation
	select {
	case <-ctx.Done():
		return nil, status.Errorf(codes.Canceled, "Request canceled")
	default:
	}
	
	s.mutex.Lock()
	defer s.mutex.Unlock()
	
	// Check sender balance
	senderBalance, senderExists := s.balances[req.FromUpiId]
	if !senderExists {
		return &PaymentResponse{
			PaymentId:      req.PaymentId,
			Status:         PaymentStatus_FAILED,
			Message:        "Sender UPI ID not found",
			ProcessingTime: time.Since(startTime).Milliseconds(),
			ResponseTime:   time.Now().Unix(),
		}, nil
	}
	
	if senderBalance < req.Amount {
		return &PaymentResponse{
			PaymentId:      req.PaymentId,
			Status:         PaymentStatus_FAILED,
			Message:        fmt.Sprintf("Insufficient balance. Available: ₹%.2f", float64(senderBalance)/100),
			ProcessingTime: time.Since(startTime).Milliseconds(),
			ResponseTime:   time.Now().Unix(),
		}, nil
	}
	
	// Check recipient exists
	_, recipientExists := s.balances[req.ToUpiId]
	if !recipientExists {
		return &PaymentResponse{
			PaymentId:      req.PaymentId,
			Status:         PaymentStatus_FAILED,
			Message:        "Recipient UPI ID not found",
			ProcessingTime: time.Since(startTime).Milliseconds(),
			ResponseTime:   time.Now().Unix(),
		}, nil
	}
	
	// Fraud detection (basic)
	if s.isSuspiciousTransaction(req) {
		log.Printf("Suspicious transaction blocked: %s", req.PaymentId)
		return &PaymentResponse{
			PaymentId:      req.PaymentId,
			Status:         PaymentStatus_FAILED,
			Message:        "Transaction blocked for security reasons",
			ProcessingTime: time.Since(startTime).Milliseconds(),
			ResponseTime:   time.Now().Unix(),
		}, nil
	}
	
	// Simulate bank processing time (50-200ms)
	processingDelay := time.Duration(50+rand.Int31n(150)) * time.Millisecond
	time.Sleep(processingDelay)
	
	// Check for timeout
	select {
	case <-ctx.Done():
		return &PaymentResponse{
			PaymentId:      req.PaymentId,
			Status:         PaymentStatus_TIMEOUT,
			Message:        "Transaction timed out",
			ProcessingTime: time.Since(startTime).Milliseconds(),
			ResponseTime:   time.Now().Unix(),
		}, nil
	default:
	}
	
	// Simulate success rate (95%)
	successRate := rand.Int31n(100)
	if successRate >= 95 {
		s.failureCount++
		return &PaymentResponse{
			PaymentId:      req.PaymentId,
			Status:         PaymentStatus_FAILED,
			Message:        "Bank declined transaction - network error",
			ProcessingTime: time.Since(startTime).Milliseconds(),
			ResponseTime:   time.Now().Unix(),
		}, nil
	}
	
	// Process successful transaction
	s.balances[req.FromUpiId] -= req.Amount
	s.balances[req.ToUpiId] += req.Amount
	
	// Generate transaction ID
	transactionId := s.generateTransactionId()
	
	response := &PaymentResponse{
		PaymentId:       req.PaymentId,
		TransactionId:   transactionId,
		Status:          PaymentStatus_SUCCESS,
		Message:         "Transaction completed successfully",
		ProcessingTime:  time.Since(startTime).Milliseconds(),
		ResponseTime:    time.Now().Unix(),
	}
	
	// Store transaction history
	s.transactions[req.FromUpiId] = append(s.transactions[req.FromUpiId], response)
	s.transactions[req.ToUpiId] = append(s.transactions[req.ToUpiId], response)
	
	s.totalTransactions++
	s.successfulCount++
	
	log.Printf("Payment processed: %s → %s, Amount: ₹%.2f, TxnID: %s",
		req.FromUpiId, req.ToUpiId, float64(req.Amount)/100, transactionId)
	
	return response, nil
}

// GetBalance returns UPI account balance
func (s *PhonePePaymentService) GetBalance(ctx context.Context, req *BalanceRequest) (*BalanceResponse, error) {
	if req.UpiId == "" {
		return nil, status.Errorf(codes.InvalidArgument, "UPI ID cannot be empty")
	}
	
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	
	balance, exists := s.balances[req.UpiId]
	if !exists {
		return nil, status.Errorf(codes.NotFound, "UPI ID not found: %s", req.UpiId)
	}
	
	return &BalanceResponse{
		UpiId:       req.UpiId,
		Balance:     balance,
		Currency:    "INR",
		LastUpdated: time.Now().Unix(),
	}, nil
}

// GetTransactionHistory returns transaction history for UPI ID
func (s *PhonePePaymentService) GetTransactionHistory(ctx context.Context, req *TransactionHistoryRequest) (*TransactionHistoryResponse, error) {
	if req.UpiId == "" {
		return nil, status.Errorf(codes.InvalidArgument, "UPI ID cannot be empty")
	}
	
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	
	allTransactions, exists := s.transactions[req.UpiId]
	if !exists {
		return &TransactionHistoryResponse{
			Transactions: make([]*PaymentResponse, 0),
			TotalCount:   0,
		}, nil
	}
	
	// Apply pagination
	totalCount := len(allTransactions)
	start := int(req.Offset)
	end := start + int(req.Limit)
	
	if start >= totalCount {
		return &TransactionHistoryResponse{
			Transactions: make([]*PaymentResponse, 0),
			TotalCount:   int32(totalCount),
		}, nil
	}
	
	if end > totalCount {
		end = totalCount
	}
	
	return &TransactionHistoryResponse{
		Transactions: allTransactions[start:end],
		TotalCount:   int32(totalCount),
	}, nil
}

// isSuspiciousTransaction performs basic fraud detection
func (s *PhonePePaymentService) isSuspiciousTransaction(req *PaymentRequest) bool {
	// Large amount check (> ₹1,00,000)
	if req.Amount > 10000000 { // ₹1 lakh
		return true
	}
	
	// Rapid transaction check would be implemented here in production
	// checking against Redis cache or database for recent transactions
	
	return false
}

// generateTransactionId creates unique transaction ID
func (s *PhonePePaymentService) generateTransactionId() string {
	// Simple transaction ID generation (production mein UUID ya better algorithm)
	timestamp := time.Now().Unix()
	randomBytes := make([]byte, 4)
	rand.Read(randomBytes)
	
	return fmt.Sprintf("TXN%d%X", timestamp, randomBytes)
}

// GetServiceMetrics returns service performance metrics
func (s *PhonePePaymentService) GetServiceMetrics() map[string]interface{} {
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	
	successRate := float64(0)
	if s.totalTransactions > 0 {
		successRate = float64(s.successfulCount) / float64(s.totalTransactions) * 100
	}
	
	return map[string]interface{}{
		"total_transactions": s.totalTransactions,
		"successful_count":   s.successfulCount,
		"failure_count":      s.failureCount,
		"success_rate":       fmt.Sprintf("%.2f%%", successRate),
		"total_accounts":     len(s.balances),
	}
}

// gRPC Server setup and main function
func main() {
	fmt.Println("💳 PhonePe Payment Service - gRPC Implementation in Go")
	fmt.Println(strings.Repeat("=", 60))
	
	// Create payment service
	paymentService := NewPhonePePaymentService()
	
	// Demo gRPC calls (normally would be actual gRPC server)
	runPaymentServiceDemo(paymentService)
}

func runPaymentServiceDemo(service *PhonePePaymentService) {
	fmt.Println("\n📱 Demo UPI Accounts:")
	
	// Show demo account balances
	demoAccounts := []string{
		"rahul@phonepe", "priya@phonepe", "amit@phonepe", 
		"sneha@phonepe", "merchant@zomato", "merchant@ola",
	}
	
	ctx := context.Background()
	
	for _, upiId := range demoAccounts {
		balanceReq := &BalanceRequest{UpiId: upiId}
		balance, err := service.GetBalance(ctx, balanceReq)
		if err != nil {
			fmt.Printf("   Error getting balance for %s: %v\n", upiId, err)
			continue
		}
		fmt.Printf("   %s: ₹%.2f\n", upiId, float64(balance.Balance)/100)
	}
	
	fmt.Println("\n💸 Processing Sample UPI Payments:")
	fmt.Println(strings.Repeat("-", 50))
	
	// Sample payment requests
	payments := []*PaymentRequest{
		{
			PaymentId:   "PAY001",
			FromUpiId:   "rahul@phonepe",
			ToUpiId:     "merchant@zomato",
			Amount:      45000, // ₹450.00
			Currency:    "INR",
			Description: "Zomato food order - Biryani from Paradise",
			Provider:    UpiProvider_PHONEPE,
			RequestTime: time.Now().Unix(),
		},
		{
			PaymentId:   "PAY002",
			FromUpiId:   "priya@phonepe",
			ToUpiId:     "merchant@ola",
			Amount:      25000, // ₹250.00
			Currency:    "INR",
			Description: "Ola cab ride - Bandra to Andheri",
			Provider:    UpiProvider_PHONEPE,
			RequestTime: time.Now().Unix(),
		},
		{
			PaymentId:   "PAY003",
			FromUpiId:   "amit@phonepe",
			ToUpiId:     "sneha@phonepe",
			Amount:      100000, // ₹1000.00
			Currency:    "INR",
			Description: "Money transfer - Birthday gift",
			Provider:    UpiProvider_PHONEPE,
			RequestTime: time.Now().Unix(),
		},
		{
			PaymentId:   "PAY004",
			FromUpiId:   "sneha@phonepe",
			ToUpiId:     "rahul@phonepe",
			Amount:      2000000, // ₹20000.00 - Large amount for fraud detection
			Currency:    "INR",
			Description: "Large transfer - Should be suspicious",
			Provider:    UpiProvider_PHONEPE,
			RequestTime: time.Now().Unix(),
		},
	}
	
	// Process payments with context timeout
	for i, payment := range payments {
		fmt.Printf("\n%d. Payment %s:\n", i+1, payment.PaymentId)
		fmt.Printf("   From: %s\n", payment.FromUpiId)
		fmt.Printf("   To: %s\n", payment.ToUpiId)
		fmt.Printf("   Amount: ₹%.2f\n", float64(payment.Amount)/100)
		fmt.Printf("   Description: %s\n", payment.Description)
		
		// Create context with timeout (5 seconds)
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		
		response, err := service.ProcessPayment(ctx, payment)
		cancel()
		
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
			continue
		}
		
		fmt.Printf("   Status: %s\n", response.Status)
		fmt.Printf("   Message: %s\n", response.Message)
		if response.TransactionId != "" {
			fmt.Printf("   Transaction ID: %s\n", response.TransactionId)
		}
		fmt.Printf("   Processing Time: %dms\n", response.ProcessingTime)
	}
	
	// Show updated balances
	fmt.Println("\n📊 Updated Account Balances:")
	for _, upiId := range demoAccounts[:4] { // Show first 4 accounts
		balanceReq := &BalanceRequest{UpiId: upiId}
		balance, err := service.GetBalance(ctx, balanceReq)
		if err != nil {
			continue
		}
		fmt.Printf("   %s: ₹%.2f\n", upiId, float64(balance.Balance)/100)
	}
	
	// Show transaction history
	fmt.Println("\n📜 Transaction History for rahul@phonepe:")
	historyReq := &TransactionHistoryRequest{
		UpiId:  "rahul@phonepe",
		Limit:  5,
		Offset: 0,
	}
	
	history, err := service.GetTransactionHistory(ctx, historyReq)
	if err == nil && len(history.Transactions) > 0 {
		for _, txn := range history.Transactions {
			fmt.Printf("   • %s - %s (₹%.2f)\n", txn.TransactionId, txn.Status, 
				float64(txn.ProcessingTime)/100) // Approximation for demo
		}
	}
	
	// Service metrics
	metrics := service.GetServiceMetrics()
	fmt.Println("\n📈 Service Performance Metrics:")
	for key, value := range metrics {
		fmt.Printf("   %s: %v\n", key, value)
	}
	
	fmt.Printf("\n⚡ gRPC Go Implementation Benefits:")
	fmt.Printf("   ✅ High-performance with goroutines\n")
	fmt.Printf("   ✅ Strong typing with protocol buffers\n")
	fmt.Printf("   ✅ Built-in load balancing and retries\n")
	fmt.Printf("   ✅ Context-based timeout and cancellation\n")
	fmt.Printf("   ✅ Streaming support for real-time data\n")
	fmt.Printf("   ✅ Low memory footprint\n")
	fmt.Printf("   ✅ Cross-language interoperability\n")
	
	fmt.Printf("\n🏭 Production Considerations:")
	fmt.Printf("   • Database integration (PostgreSQL/MongoDB)\n")
	fmt.Printf("   • Redis for caching and rate limiting\n")
	fmt.Printf("   • Distributed tracing with OpenTracing\n")
	fmt.Printf("   • Metrics with Prometheus\n")
	fmt.Printf("   • Circuit breakers with Hystrix-Go\n")
	fmt.Printf("   • TLS/SSL for secure communication\n")
	fmt.Printf("   • Service mesh integration (Istio)\n")
}

// Helper function to create string repetition (since strings.Repeat might not be available)
func strings_Repeat(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}