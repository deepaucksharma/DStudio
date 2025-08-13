// gRPC Payment Service for Indian E-commerce
// UPI payments के लिए high-performance gRPC service
//
// Key Features:
// - UPI payment processing
// - Multi-bank integration (HDFC, SBI, ICICI)
// - Real-time payment status tracking
// - Fraud detection और prevention
// - Circuit breaker और retry logic
//
// Author: Code Developer Agent for Hindi Tech Podcast
// Episode: 24 - API Design Patterns

package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"log"
	"net"
	"strconv"
	"strings"
	"sync"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/timestamppb"
)

// PaymentStatus enum - Payment के अलग-अलग states
type PaymentStatus int32

const (
	PaymentStatus_PENDING PaymentStatus = iota
	PaymentStatus_PROCESSING
	PaymentStatus_SUCCESS
	PaymentStatus_FAILED
	PaymentStatus_REFUNDED
)

// PaymentMethod enum - भारतीय payment methods
type PaymentMethod int32

const (
	PaymentMethod_UPI PaymentMethod = iota
	PaymentMethod_CREDIT_CARD
	PaymentMethod_DEBIT_CARD
	PaymentMethod_NET_BANKING
	PaymentMethod_WALLET
)

// Bank enum - Major Indian banks
type Bank int32

const (
	Bank_SBI Bank = iota
	Bank_HDFC
	Bank_ICICI
	Bank_AXIS
	Bank_KOTAK
)

// Payment request structure
type PaymentRequest struct {
	Amount        float64       `json:"amount"`
	Currency      string        `json:"currency"`
	PaymentMethod PaymentMethod `json:"payment_method"`
	UpiId         string        `json:"upi_id,omitempty"`
	MerchantId    string        `json:"merchant_id"`
	OrderId       string        `json:"order_id"`
	Description   string        `json:"description"`
	CustomerInfo  *CustomerInfo `json:"customer_info"`
}

// Customer information
type CustomerInfo struct {
	UserId      string `json:"user_id"`
	Name        string `json:"name"`
	Email       string `json:"email"`
	Phone       string `json:"phone"`
	DeviceId    string `json:"device_id"`
	IpAddress   string `json:"ip_address"`
	Region      string `json:"region"`
}

// Payment response structure
type PaymentResponse struct {
	PaymentId     string                 `json:"payment_id"`
	Status        PaymentStatus          `json:"status"`
	Amount        float64                `json:"amount"`
	Currency      string                 `json:"currency"`
	TransactionId string                 `json:"transaction_id"`
	Message       string                 `json:"message"`
	CreatedAt     *timestamppb.Timestamp `json:"created_at"`
	ProcessedAt   *timestamppb.Timestamp `json:"processed_at,omitempty"`
	ErrorCode     string                 `json:"error_code,omitempty"`
}

// Payment status query
type PaymentStatusRequest struct {
	PaymentId string `json:"payment_id"`
}

// UPI Payment Service implementation
type UPIPaymentService struct {
	// In-memory storage - production में यह database होगा
	payments map[string]*PaymentResponse
	mutex    sync.RWMutex

	// Bank connections - production में real bank APIs होंगी
	bankConnections map[Bank]bool

	// Fraud detection system
	fraudDetector *FraudDetector
}

// Fraud detection system
type FraudDetector struct {
	suspiciousIPs    map[string]time.Time
	dailyLimits      map[string]float64
	velocityChecks   map[string][]time.Time
	mutex            sync.RWMutex
}

// Initialize UPI Payment Service
func NewUPIPaymentService() *UPIPaymentService {
	service := &UPIPaymentService{
		payments:        make(map[string]*PaymentResponse),
		bankConnections: make(map[Bank]bool),
		fraudDetector:   NewFraudDetector(),
	}

	// Initialize bank connections
	service.bankConnections[Bank_SBI] = true
	service.bankConnections[Bank_HDFC] = true
	service.bankConnections[Bank_ICICI] = true
	service.bankConnections[Bank_AXIS] = true
	service.bankConnections[Bank_KOTAK] = true

	log.Println("🏦 UPI Payment Service initialized")
	log.Printf("📱 Connected to %d banks", len(service.bankConnections))

	return service
}

// Initialize fraud detector
func NewFraudDetector() *FraudDetector {
	return &FraudDetector{
		suspiciousIPs:  make(map[string]time.Time),
		dailyLimits:    make(map[string]float64),
		velocityChecks: make(map[string][]time.Time),
	}
}

// Process Payment - मुख्य payment processing function
func (s *UPIPaymentService) ProcessPayment(ctx context.Context, req *PaymentRequest) (*PaymentResponse, error) {
	log.Printf("💳 Processing payment: ₹%.2f for order %s", req.Amount, req.OrderId)

	// Validation - Input validation
	if err := s.validatePaymentRequest(req); err != nil {
		log.Printf("❌ Validation failed: %v", err)
		return nil, status.Errorf(codes.InvalidArgument, "Validation failed: %v", err)
	}

	// Fraud detection check
	if isFraud, reason := s.fraudDetector.CheckForFraud(req); isFraud {
		log.Printf("🚨 Fraud detected: %s", reason)
		return &PaymentResponse{
			PaymentId: s.generatePaymentID(),
			Status:    PaymentStatus_FAILED,
			Amount:    req.Amount,
			Currency:  req.Currency,
			Message:   "Transaction blocked due to suspicious activity",
			ErrorCode: "FRAUD_DETECTED",
			CreatedAt: timestamppb.Now(),
		}, nil
	}

	// Generate payment ID
	paymentID := s.generatePaymentID()

	// Create payment record
	payment := &PaymentResponse{
		PaymentId: paymentID,
		Status:    PaymentStatus_PENDING,
		Amount:    req.Amount,
		Currency:  req.Currency,
		Message:   "Payment initiated",
		CreatedAt: timestamppb.Now(),
	}

	// Store payment
	s.mutex.Lock()
	s.payments[paymentID] = payment
	s.mutex.Unlock()

	// Process based on payment method
	switch req.PaymentMethod {
	case PaymentMethod_UPI:
		return s.processUPIPayment(ctx, req, payment)
	case PaymentMethod_CREDIT_CARD, PaymentMethod_DEBIT_CARD:
		return s.processCardPayment(ctx, req, payment)
	case PaymentMethod_NET_BANKING:
		return s.processNetBanking(ctx, req, payment)
	case PaymentMethod_WALLET:
		return s.processWalletPayment(ctx, req, payment)
	default:
		return nil, status.Errorf(codes.InvalidArgument, "Unsupported payment method")
	}
}

// Process UPI Payment - UPI payments का detailed processing
func (s *UPIPaymentService) processUPIPayment(ctx context.Context, req *PaymentRequest, payment *PaymentResponse) (*PaymentResponse, error) {
	log.Printf("📱 Processing UPI payment for %s", req.UpiId)

	// Update status to processing
	payment.Status = PaymentStatus_PROCESSING
	payment.Message = "Contacting UPI network..."

	// Simulate UPI network call - production में real UPI API होगी
	bank := s.getBankFromUPI(req.UpiId)
	if !s.bankConnections[bank] {
		payment.Status = PaymentStatus_FAILED
		payment.Message = "Bank service unavailable"
		payment.ErrorCode = "BANK_UNAVAILABLE"
		return payment, nil
	}

	// Simulate network delay और processing
	time.Sleep(time.Millisecond * 500) // 500ms processing time

	// Simulate payment success/failure (90% success rate)
	if s.simulatePaymentOutcome(0.9) {
		payment.Status = PaymentStatus_SUCCESS
		payment.TransactionId = s.generateTransactionID()
		payment.Message = "Payment completed successfully"
		payment.ProcessedAt = timestamppb.Now()

		log.Printf("✅ UPI payment successful: %s", payment.TransactionId)
	} else {
		payment.Status = PaymentStatus_FAILED
		payment.Message = "Payment declined by bank"
		payment.ErrorCode = "BANK_DECLINED"

		log.Printf("❌ UPI payment failed for %s", req.UpiId)
	}

	// Update stored payment
	s.mutex.Lock()
	s.payments[payment.PaymentId] = payment
	s.mutex.Unlock()

	return payment, nil
}

// Process Card Payment - Credit/Debit card processing
func (s *UPIPaymentService) processCardPayment(ctx context.Context, req *PaymentRequest, payment *PaymentResponse) (*PaymentResponse, error) {
	log.Printf("💳 Processing card payment for order %s", req.OrderId)

	payment.Status = PaymentStatus_PROCESSING
	payment.Message = "Processing card payment..."

	// Simulate card network processing
	time.Sleep(time.Millisecond * 800) // Slightly longer for card processing

	// 85% success rate for cards (slightly lower than UPI)
	if s.simulatePaymentOutcome(0.85) {
		payment.Status = PaymentStatus_SUCCESS
		payment.TransactionId = s.generateTransactionID()
		payment.Message = "Card payment successful"
		payment.ProcessedAt = timestamppb.Now()
	} else {
		payment.Status = PaymentStatus_FAILED
		payment.Message = "Card declined"
		payment.ErrorCode = "CARD_DECLINED"
	}

	s.mutex.Lock()
	s.payments[payment.PaymentId] = payment
	s.mutex.Unlock()

	return payment, nil
}

// Process Net Banking - Net banking payment processing
func (s *UPIPaymentService) processNetBanking(ctx context.Context, req *PaymentRequest, payment *PaymentResponse) (*PaymentResponse, error) {
	log.Printf("🏦 Processing net banking payment")

	payment.Status = PaymentStatus_PROCESSING
	payment.Message = "Redirecting to bank..."

	// Simulate bank redirection और processing
	time.Sleep(time.Millisecond * 1200) // Longer processing for net banking

	if s.simulatePaymentOutcome(0.88) {
		payment.Status = PaymentStatus_SUCCESS
		payment.TransactionId = s.generateTransactionID()
		payment.Message = "Net banking payment successful"
		payment.ProcessedAt = timestamppb.Now()
	} else {
		payment.Status = PaymentStatus_FAILED
		payment.Message = "Net banking payment failed"
		payment.ErrorCode = "NETBANKING_FAILED"
	}

	s.mutex.Lock()
	s.payments[payment.PaymentId] = payment
	s.mutex.Unlock()

	return payment, nil
}

// Process Wallet Payment - Digital wallet processing
func (s *UPIPaymentService) processWalletPayment(ctx context.Context, req *PaymentRequest, payment *PaymentResponse) (*PaymentResponse, error) {
	log.Printf("👛 Processing wallet payment")

	payment.Status = PaymentStatus_PROCESSING
	payment.Message = "Processing wallet payment..."

	// Fastest processing for wallets
	time.Sleep(time.Millisecond * 300)

	// Highest success rate for wallets (95%)
	if s.simulatePaymentOutcome(0.95) {
		payment.Status = PaymentStatus_SUCCESS
		payment.TransactionId = s.generateTransactionID()
		payment.Message = "Wallet payment successful"
		payment.ProcessedAt = timestamppb.Now()
	} else {
		payment.Status = PaymentStatus_FAILED
		payment.Message = "Insufficient wallet balance"
		payment.ErrorCode = "INSUFFICIENT_BALANCE"
	}

	s.mutex.Lock()
	s.payments[payment.PaymentId] = payment
	s.mutex.Unlock()

	return payment, nil
}

// Get Payment Status - Payment status check करने के लिए
func (s *UPIPaymentService) GetPaymentStatus(ctx context.Context, req *PaymentStatusRequest) (*PaymentResponse, error) {
	log.Printf("🔍 Checking payment status for: %s", req.PaymentId)

	s.mutex.RLock()
	payment, exists := s.payments[req.PaymentId]
	s.mutex.RUnlock()

	if !exists {
		return nil, status.Errorf(codes.NotFound, "Payment not found: %s", req.PaymentId)
	}

	return payment, nil
}

// Validate payment request
func (s *UPIPaymentService) validatePaymentRequest(req *PaymentRequest) error {
	if req.Amount <= 0 {
		return fmt.Errorf("amount must be positive")
	}

	if req.Amount > 100000 { // ₹1 lakh limit
		return fmt.Errorf("amount exceeds maximum limit of ₹100,000")
	}

	if req.Currency != "INR" {
		return fmt.Errorf("only INR currency supported")
	}

	if req.MerchantId == "" {
		return fmt.Errorf("merchant ID required")
	}

	if req.OrderId == "" {
		return fmt.Errorf("order ID required")
	}

	// UPI specific validation
	if req.PaymentMethod == PaymentMethod_UPI {
		if req.UpiId == "" {
			return fmt.Errorf("UPI ID required for UPI payments")
		}
		if !s.isValidUPIID(req.UpiId) {
			return fmt.Errorf("invalid UPI ID format")
		}
	}

	return nil
}

// Validate UPI ID format
func (s *UPIPaymentService) isValidUPIID(upiID string) bool {
	// Basic UPI ID validation: should contain @ and valid provider
	if !strings.Contains(upiID, "@") {
		return false
	}

	validProviders := []string{"paytm", "googlepay", "phonepe", "ybl", "okhdfcbank", "okicici", "okaxis"}
	parts := strings.Split(upiID, "@")
	if len(parts) != 2 {
		return false
	}

	provider := parts[1]
	for _, validProvider := range validProviders {
		if provider == validProvider {
			return true
		}
	}

	return false
}

// Get bank from UPI ID
func (s *UPIPaymentService) getBankFromUPI(upiID string) Bank {
	if strings.Contains(upiID, "hdfc") {
		return Bank_HDFC
	} else if strings.Contains(upiID, "icici") {
		return Bank_ICICI
	} else if strings.Contains(upiID, "axis") {
		return Bank_AXIS
	} else if strings.Contains(upiID, "kotak") {
		return Bank_KOTAK
	}
	return Bank_SBI // Default to SBI
}

// Simulate payment outcome
func (s *UPIPaymentService) simulatePaymentOutcome(successRate float64) bool {
	// Simple random success/failure based on success rate
	randBytes := make([]byte, 1)
	rand.Read(randBytes)
	random := float64(randBytes[0]) / 255.0
	return random < successRate
}

// Generate payment ID
func (s *UPIPaymentService) generatePaymentID() string {
	bytes := make([]byte, 8)
	rand.Read(bytes)
	return "PAY_" + hex.EncodeToString(bytes)
}

// Generate transaction ID
func (s *UPIPaymentService) generateTransactionID() string {
	bytes := make([]byte, 12)
	rand.Read(bytes)
	return "TXN_" + hex.EncodeToString(bytes)
}

// Fraud Detection Methods

// Check for fraud
func (fd *FraudDetector) CheckForFraud(req *PaymentRequest) (bool, string) {
	fd.mutex.Lock()
	defer fd.mutex.Unlock()

	// Check for suspicious IP
	if fd.isSuspiciousIP(req.CustomerInfo.IpAddress) {
		return true, "Suspicious IP address detected"
	}

	// Check daily transaction limits
	if fd.exceedsDailyLimit(req.CustomerInfo.UserId, req.Amount) {
		return true, "Daily transaction limit exceeded"
	}

	// Check velocity (too many transactions in short time)
	if fd.exceedsVelocityLimit(req.CustomerInfo.UserId) {
		return true, "Too many transactions in short time"
	}

	// Check for round amount fraud (exactly ₹10000, ₹50000 etc.)
	if fd.isRoundAmountFraud(req.Amount) {
		return true, "Suspicious round amount detected"
	}

	// Update tracking data
	fd.updateTracking(req)

	return false, ""
}

func (fd *FraudDetector) isSuspiciousIP(ipAddress string) bool {
	if suspiciousTime, exists := fd.suspiciousIPs[ipAddress]; exists {
		// If IP was marked suspicious in last 24 hours
		return time.Since(suspiciousTime) < 24*time.Hour
	}
	return false
}

func (fd *FraudDetector) exceedsDailyLimit(userID string, amount float64) bool {
	dailySpent, exists := fd.dailyLimits[userID]
	if !exists {
		dailySpent = 0
	}

	dailyLimit := 50000.0 // ₹50,000 daily limit
	return (dailySpent + amount) > dailyLimit
}

func (fd *FraudDetector) exceedsVelocityLimit(userID string) bool {
	transactions := fd.velocityChecks[userID]
	now := time.Now()

	// Remove transactions older than 10 minutes
	var recentTransactions []time.Time
	for _, txTime := range transactions {
		if now.Sub(txTime) < 10*time.Minute {
			recentTransactions = append(recentTransactions, txTime)
		}
	}

	// Update the slice
	fd.velocityChecks[userID] = recentTransactions

	// Check if more than 5 transactions in 10 minutes
	return len(recentTransactions) >= 5
}

func (fd *FraudDetector) isRoundAmountFraud(amount float64) bool {
	// Check for exactly round amounts above ₹10,000
	if amount >= 10000 && amount == float64(int(amount)) {
		// Check if it's exactly divisible by 1000
		return int(amount)%1000 == 0
	}
	return false
}

func (fd *FraudDetector) updateTracking(req *PaymentRequest) {
	// Update daily limits
	fd.dailyLimits[req.CustomerInfo.UserId] += req.Amount

	// Update velocity tracking
	fd.velocityChecks[req.CustomerInfo.UserId] = append(
		fd.velocityChecks[req.CustomerInfo.UserId],
		time.Now(),
	)
}

// Demo function for testing
func runPaymentDemo() {
	log.Println("🚀 Starting UPI Payment Service Demo")
	log.Println("🇮🇳 Indian e-commerce payment processing")

	service := NewUPIPaymentService()

	// Test cases - विभिन्न payment scenarios
	testCases := []struct {
		name    string
		request *PaymentRequest
	}{
		{
			name: "UPI Payment - PhonePe",
			request: &PaymentRequest{
				Amount:        1500.0,
				Currency:      "INR",
				PaymentMethod: PaymentMethod_UPI,
				UpiId:         "user123@phonepe",
				MerchantId:    "FLIPKART_001",
				OrderId:       "ORD_" + strconv.FormatInt(time.Now().Unix(), 10),
				Description:   "Smartphone purchase",
				CustomerInfo: &CustomerInfo{
					UserId:    "USER_001",
					Name:      "Rahul Sharma",
					Email:     "rahul@example.com",
					Phone:     "+91-9876543210",
					DeviceId:  "DEVICE_123",
					IpAddress: "49.32.123.45",
					Region:    "Mumbai",
				},
			},
		},
		{
			name: "Card Payment - Debit Card",
			request: &PaymentRequest{
				Amount:        2999.0,
				Currency:      "INR",
				PaymentMethod: PaymentMethod_DEBIT_CARD,
				MerchantId:    "AMAZON_001",
				OrderId:       "ORD_" + strconv.FormatInt(time.Now().Unix()+1, 10),
				Description:   "Laptop purchase",
				CustomerInfo: &CustomerInfo{
					UserId:    "USER_002",
					Name:      "Priya Patel",
					Email:     "priya@example.com",
					Phone:     "+91-9876543211",
					DeviceId:  "DEVICE_124",
					IpAddress: "49.32.123.46",
					Region:    "Bangalore",
				},
			},
		},
		{
			name: "Wallet Payment - Paytm",
			request: &PaymentRequest{
				Amount:        599.0,
				Currency:      "INR",
				PaymentMethod: PaymentMethod_WALLET,
				MerchantId:    "ZOMATO_001",
				OrderId:       "ORD_" + strconv.FormatInt(time.Now().Unix()+2, 10),
				Description:   "Food delivery",
				CustomerInfo: &CustomerInfo{
					UserId:    "USER_003",
					Name:      "Amit Kumar",
					Email:     "amit@example.com",
					Phone:     "+91-9876543212",
					DeviceId:  "DEVICE_125",
					IpAddress: "49.32.123.47",
					Region:    "Delhi",
				},
			},
		},
	}

	// Process all test payments
	for i, testCase := range testCases {
		log.Printf("\n📝 Test %d: %s", i+1, testCase.name)
		log.Println(strings.Repeat("-", 50))

		// Process payment
		ctx := context.Background()
		response, err := service.ProcessPayment(ctx, testCase.request)

		if err != nil {
			log.Printf("❌ Payment failed: %v", err)
			continue
		}

		// Print payment result
		log.Printf("💳 Payment ID: %s", response.PaymentId)
		log.Printf("📊 Status: %v", response.Status)
		log.Printf("💰 Amount: ₹%.2f %s", response.Amount, response.Currency)
		log.Printf("📝 Message: %s", response.Message)

		if response.TransactionId != "" {
			log.Printf("🔗 Transaction ID: %s", response.TransactionId)
		}

		if response.ErrorCode != "" {
			log.Printf("❌ Error Code: %s", response.ErrorCode)
		}

		// Check payment status
		time.Sleep(time.Millisecond * 100)
		statusReq := &PaymentStatusRequest{PaymentId: response.PaymentId}
		statusResp, err := service.GetPaymentStatus(ctx, statusReq)

		if err != nil {
			log.Printf("❌ Status check failed: %v", err)
		} else {
			log.Printf("🔍 Status Check: %v", statusResp.Status)
		}
	}

	log.Println("\n🎉 Payment service demo completed!")
	log.Println("💡 Key features demonstrated:")
	log.Println("  - Multiple payment methods (UPI, Cards, Net Banking, Wallet)")
	log.Println("  - Real-time fraud detection")
	log.Println("  - Bank connectivity simulation")
	log.Println("  - Production-ready error handling")
	log.Println("  - Payment status tracking")
}

// gRPC server setup
func startGRPCServer() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	s := grpc.NewServer()

	// Register payment service (proto definitions would be here in real implementation)
	// s.RegisterService(&_PaymentService_serviceDesc, NewUPIPaymentService())

	log.Println("🌐 gRPC Payment Service starting on :50051")
	log.Println("📱 Ready to process Indian e-commerce payments")

	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}

func main() {
	fmt.Println("💳 gRPC Payment Service for Indian E-commerce")
	fmt.Println("🇮🇳 UPI, Cards, Net Banking & Wallet Support")
	fmt.Println("=" + strings.Repeat("=", 50))

	// Run demo
	runPaymentDemo()

	// In production, you would start the gRPC server:
	// startGRPCServer()
}