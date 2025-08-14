/*
Domain-Driven Design: Microservices with DDD - Razorpay Payment Service
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD principles का इस्तेमाल करके
Razorpay payment microservice बनाते हैं। Go में clean architecture
और domain-driven approach के साथ।

Author: Hindi Tech Podcast
Date: 2025
*/

package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/mux"
)

// ====================================================================
// DOMAIN LAYER - Core Business Logic
// ====================================================================

// Domain Errors - Business rule violations
var (
	ErrInvalidAmount       = errors.New("invalid payment amount - गलत payment amount")
	ErrInsufficientFunds   = errors.New("insufficient funds - पैसे कम हैं")
	ErrPaymentNotFound     = errors.New("payment not found - payment नहीं मिली")
	ErrInvalidPaymentID    = errors.New("invalid payment ID - गलत payment ID")
	ErrPaymentAlreadyProcessed = errors.New("payment already processed - payment पहले से process हो चुकी है")
	ErrMerchantNotFound    = errors.New("merchant not found - merchant नहीं मिला")
	ErrInvalidMerchantKey  = errors.New("invalid merchant key - गलत merchant key")
)

// Enums - Domain-specific types
type PaymentStatus string

const (
	PaymentStatusCreated    PaymentStatus = "created"
	PaymentStatusPending    PaymentStatus = "pending"
	PaymentStatusAuthorized PaymentStatus = "authorized"
	PaymentStatusCaptured   PaymentStatus = "captured"
	PaymentStatusFailed     PaymentStatus = "failed"
	PaymentStatusRefunded   PaymentStatus = "refunded"
)

type PaymentMethod string

const (
	PaymentMethodUPI         PaymentMethod = "upi"
	PaymentMethodCard        PaymentMethod = "card"
	PaymentMethodNetBanking  PaymentMethod = "netbanking"
	PaymentMethodWallet      PaymentMethod = "wallet"
)

type Currency string

const (
	CurrencyINR Currency = "INR"
	CurrencyUSD Currency = "USD"
)

// Value Objects - Immutable domain concepts
type Money struct {
	Amount   int64    `json:"amount"`   // Amount in smallest currency unit (पैसे में)
	Currency Currency `json:"currency"`
}

// NewMoney creates a new Money value object with validation
func NewMoney(amount int64, currency Currency) (*Money, error) {
	if amount < 0 {
		return nil, errors.New("amount cannot be negative - रकम negative नहीं हो सकती")
	}
	if currency != CurrencyINR && currency != CurrencyUSD {
		return nil, errors.New("invalid currency - गलत currency")
	}
	return &Money{Amount: amount, Currency: currency}, nil
}

// ToRupees converts पैसे to rupees for display
func (m *Money) ToRupees() float64 {
	return float64(m.Amount) / 100.0
}

// Add adds two money amounts (same currency)
func (m *Money) Add(other *Money) (*Money, error) {
	if m.Currency != other.Currency {
		return nil, errors.New("currency mismatch - currency match नहीं करती")
	}
	return &Money{Amount: m.Amount + other.Amount, Currency: m.Currency}, nil
}

// String representation
func (m *Money) String() string {
	if m.Currency == CurrencyINR {
		return fmt.Sprintf("₹%.2f", m.ToRupees())
	}
	return fmt.Sprintf("$%.2f", m.ToRupees())
}

type PaymentID struct {
	Value string `json:"value"`
}

// NewPaymentID creates a new payment ID with validation
func NewPaymentID(id string) (*PaymentID, error) {
	if len(id) < 8 {
		return nil, ErrInvalidPaymentID
	}
	return &PaymentID{Value: id}, nil
}

// Generate creates a new payment ID
func (p *PaymentID) Generate() *PaymentID {
	id := fmt.Sprintf("pay_%d_%d", time.Now().Unix(), rand.Intn(10000))
	return &PaymentID{Value: id}
}

func (p *PaymentID) String() string {
	return p.Value
}

type MerchantID struct {
	Value string `json:"value"`
}

func NewMerchantID(id string) (*MerchantID, error) {
	if len(id) < 5 {
		return nil, errors.New("invalid merchant ID - गलत merchant ID")
	}
	return &MerchantID{Value: id}, nil
}

// Entities - Core domain objects with identity
type Payment struct {
	ID          *PaymentID    `json:"id"`
	MerchantID  *MerchantID   `json:"merchant_id"`
	Amount      *Money        `json:"amount"`
	Method      PaymentMethod `json:"method"`
	Status      PaymentStatus `json:"status"`
	Description string        `json:"description"`
	
	// Customer information
	CustomerEmail string `json:"customer_email"`
	CustomerPhone string `json:"customer_phone"`
	
	// Payment details
	GatewayResponse map[string]interface{} `json:"gateway_response,omitempty"`
	FailureReason   string                 `json:"failure_reason,omitempty"`
	
	// Timestamps
	CreatedAt   time.Time  `json:"created_at"`
	AuthorizedAt *time.Time `json:"authorized_at,omitempty"`
	CapturedAt   *time.Time `json:"captured_at,omitempty"`
	FailedAt     *time.Time `json:"failed_at,omitempty"`
	
	// Audit
	Version int `json:"version"`
}

// NewPayment creates a new payment entity
func NewPayment(merchantID *MerchantID, amount *Money, method PaymentMethod, description string) *Payment {
	paymentID := &PaymentID{}
	id := paymentID.Generate()
	
	payment := &Payment{
		ID:          id,
		MerchantID:  merchantID,
		Amount:      amount,
		Method:      method,
		Status:      PaymentStatusCreated,
		Description: description,
		CreatedAt:   time.Now(),
		Version:     1,
	}
	
	fmt.Printf("💳 Payment created: %s for %s\n", id.Value, amount.String())
	return payment
}

// Business Methods - Domain operations

func (p *Payment) SetCustomerInfo(email, phone string) error {
	if email == "" || !strings.Contains(email, "@") {
		return errors.New("invalid email - गलत email")
	}
	if len(phone) != 10 {
		return errors.New("invalid phone number - गलत phone number")
	}
	
	p.CustomerEmail = email
	p.CustomerPhone = phone
	p.Version++
	
	return nil
}

func (p *Payment) Authorize(gatewayResponse map[string]interface{}) error {
	if p.Status != PaymentStatusCreated && p.Status != PaymentStatusPending {
		return ErrPaymentAlreadyProcessed
	}
	
	now := time.Now()
	p.Status = PaymentStatusAuthorized
	p.AuthorizedAt = &now
	p.GatewayResponse = gatewayResponse
	p.Version++
	
	fmt.Printf("✅ Payment authorized: %s\n", p.ID.Value)
	return nil
}

func (p *Payment) Capture() error {
	if p.Status != PaymentStatusAuthorized {
		return errors.New("payment must be authorized first - payment पहले authorize होनी चाहिए")
	}
	
	now := time.Now()
	p.Status = PaymentStatusCaptured
	p.CapturedAt = &now
	p.Version++
	
	fmt.Printf("🎯 Payment captured: %s for %s\n", p.ID.Value, p.Amount.String())
	return nil
}

func (p *Payment) Fail(reason string) error {
	if p.Status == PaymentStatusCaptured || p.Status == PaymentStatusRefunded {
		return errors.New("cannot fail captured or refunded payment")
	}
	
	now := time.Now()
	p.Status = PaymentStatusFailed
	p.FailedAt = &now
	p.FailureReason = reason
	p.Version++
	
	fmt.Printf("❌ Payment failed: %s - %s\n", p.ID.Value, reason)
	return nil
}

func (p *Payment) IsSuccessful() bool {
	return p.Status == PaymentStatusCaptured
}

func (p *Payment) CanBeRefunded() bool {
	return p.Status == PaymentStatusCaptured
}

// Aggregate - Merchant with payment history
type Merchant struct {
	ID          *MerchantID `json:"id"`
	Name        string      `json:"name"`
	Email       string      `json:"email"`
	Phone       string      `json:"phone"`
	APIKey      string      `json:"api_key"`
	IsActive    bool        `json:"is_active"`
	
	// Business info
	BusinessType string `json:"business_type"`
	Website      string `json:"website"`
	
	// Metrics
	TotalPayments   int64  `json:"total_payments"`
	SuccessfulPayments int64 `json:"successful_payments"`
	TotalVolume     *Money `json:"total_volume"`
	
	// Audit
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

func NewMerchant(name, email, phone, businessType string) *Merchant {
	merchantID, _ := NewMerchantID(generateMerchantID())
	totalVolume, _ := NewMoney(0, CurrencyINR)
	
	merchant := &Merchant{
		ID:           merchantID,
		Name:         name,
		Email:        email,
		Phone:        phone,
		APIKey:       generateAPIKey(),
		IsActive:     true,
		BusinessType: businessType,
		TotalVolume:  totalVolume,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}
	
	fmt.Printf("🏪 Merchant created: %s (%s)\n", name, merchantID.Value)
	return merchant
}

func (m *Merchant) RecordPayment(payment *Payment) {
	m.TotalPayments++
	if payment.IsSuccessful() {
		m.SuccessfulPayments++
		newVolume, _ := m.TotalVolume.Add(payment.Amount)
		m.TotalVolume = newVolume
	}
	m.UpdatedAt = time.Now()
}

func (m *Merchant) GetSuccessRate() float64 {
	if m.TotalPayments == 0 {
		return 0.0
	}
	return float64(m.SuccessfulPayments) / float64(m.TotalPayments) * 100.0
}

// Domain Services - Complex business logic across entities
type PaymentProcessingService struct {
	gatewayService GatewayService
}

func NewPaymentProcessingService(gateway GatewayService) *PaymentProcessingService {
	return &PaymentProcessingService{
		gatewayService: gateway,
	}
}

func (s *PaymentProcessingService) ProcessPayment(ctx context.Context, payment *Payment) error {
	fmt.Printf("🔄 Processing payment: %s via %s\n", payment.ID.Value, payment.Method)
	
	// Update status to pending
	payment.Status = PaymentStatusPending
	
	// Call external gateway
	response, err := s.gatewayService.AuthorizePayment(ctx, payment)
	if err != nil {
		payment.Fail(err.Error())
		return err
	}
	
	// Authorize payment
	err = payment.Authorize(response)
	if err != nil {
		return err
	}
	
	// Auto-capture for UPI payments (Indian preference)
	if payment.Method == PaymentMethodUPI {
		err = payment.Capture()
		if err != nil {
			return err
		}
	}
	
	return nil
}

// ====================================================================
// APPLICATION LAYER - Use cases and orchestration
// ====================================================================

type PaymentService struct {
	paymentRepo    PaymentRepository
	merchantRepo   MerchantRepository
	processingService *PaymentProcessingService
	mu            sync.RWMutex
}

func NewPaymentService(paymentRepo PaymentRepository, merchantRepo MerchantRepository, 
                      processingService *PaymentProcessingService) *PaymentService {
	return &PaymentService{
		paymentRepo:       paymentRepo,
		merchantRepo:      merchantRepo,
		processingService: processingService,
	}
}

func (s *PaymentService) CreatePayment(ctx context.Context, request CreatePaymentRequest) (*Payment, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	// Validate merchant
	merchant, err := s.merchantRepo.FindByAPIKey(ctx, request.MerchantAPIKey)
	if err != nil {
		return nil, ErrMerchantNotFound
	}
	if !merchant.IsActive {
		return nil, errors.New("merchant is not active - merchant active नहीं है")
	}
	
	// Create money value object
	amount, err := NewMoney(request.Amount, Currency(request.Currency))
	if err != nil {
		return nil, err
	}
	
	// Create payment entity
	payment := NewPayment(merchant.ID, amount, PaymentMethod(request.Method), request.Description)
	
	// Set customer info if provided
	if request.CustomerEmail != "" && request.CustomerPhone != "" {
		err = payment.SetCustomerInfo(request.CustomerEmail, request.CustomerPhone)
		if err != nil {
			return nil, err
		}
	}
	
	// Save payment
	err = s.paymentRepo.Save(ctx, payment)
	if err != nil {
		return nil, err
	}
	
	// Record in merchant stats
	merchant.RecordPayment(payment)
	err = s.merchantRepo.Save(ctx, merchant)
	if err != nil {
		fmt.Printf("Warning: Failed to update merchant stats: %v\n", err)
	}
	
	return payment, nil
}

func (s *PaymentService) ProcessPayment(ctx context.Context, paymentID string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	paymentIDObj, err := NewPaymentID(paymentID)
	if err != nil {
		return err
	}
	
	payment, err := s.paymentRepo.FindByID(ctx, paymentIDObj)
	if err != nil {
		return err
	}
	
	err = s.processingService.ProcessPayment(ctx, payment)
	if err != nil {
		// Save failed payment
		s.paymentRepo.Save(ctx, payment)
		return err
	}
	
	// Save successful payment
	err = s.paymentRepo.Save(ctx, payment)
	if err != nil {
		return err
	}
	
	fmt.Printf("✅ Payment processed successfully: %s\n", paymentID)
	return nil
}

func (s *PaymentService) GetPayment(ctx context.Context, paymentID string) (*Payment, error) {
	paymentIDObj, err := NewPaymentID(paymentID)
	if err != nil {
		return nil, err
	}
	
	return s.paymentRepo.FindByID(ctx, paymentIDObj)
}

func (s *PaymentService) GetMerchantPayments(ctx context.Context, merchantAPIKey string) ([]*Payment, error) {
	merchant, err := s.merchantRepo.FindByAPIKey(ctx, merchantAPIKey)
	if err != nil {
		return nil, ErrMerchantNotFound
	}
	
	return s.paymentRepo.FindByMerchantID(ctx, merchant.ID)
}

// ====================================================================
// INFRASTRUCTURE LAYER - External concerns
// ====================================================================

// Repository interfaces (Ports)
type PaymentRepository interface {
	Save(ctx context.Context, payment *Payment) error
	FindByID(ctx context.Context, id *PaymentID) (*Payment, error)
	FindByMerchantID(ctx context.Context, merchantID *MerchantID) ([]*Payment, error)
	FindByStatus(ctx context.Context, status PaymentStatus) ([]*Payment, error)
}

type MerchantRepository interface {
	Save(ctx context.Context, merchant *Merchant) error
	FindByID(ctx context.Context, id *MerchantID) (*Merchant, error)
	FindByAPIKey(ctx context.Context, apiKey string) (*Merchant, error)
}

type GatewayService interface {
	AuthorizePayment(ctx context.Context, payment *Payment) (map[string]interface{}, error)
}

// In-memory implementations (for demo)
type InMemoryPaymentRepository struct {
	payments map[string]*Payment
	mu       sync.RWMutex
}

func NewInMemoryPaymentRepository() *InMemoryPaymentRepository {
	return &InMemoryPaymentRepository{
		payments: make(map[string]*Payment),
	}
}

func (r *InMemoryPaymentRepository) Save(ctx context.Context, payment *Payment) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	r.payments[payment.ID.Value] = payment
	fmt.Printf("💾 Payment saved: %s\n", payment.ID.Value)
	return nil
}

func (r *InMemoryPaymentRepository) FindByID(ctx context.Context, id *PaymentID) (*Payment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	payment, exists := r.payments[id.Value]
	if !exists {
		return nil, ErrPaymentNotFound
	}
	return payment, nil
}

func (r *InMemoryPaymentRepository) FindByMerchantID(ctx context.Context, merchantID *MerchantID) ([]*Payment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var payments []*Payment
	for _, payment := range r.payments {
		if payment.MerchantID.Value == merchantID.Value {
			payments = append(payments, payment)
		}
	}
	return payments, nil
}

func (r *InMemoryPaymentRepository) FindByStatus(ctx context.Context, status PaymentStatus) ([]*Payment, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var payments []*Payment
	for _, payment := range r.payments {
		if payment.Status == status {
			payments = append(payments, payment)
		}
	}
	return payments, nil
}

type InMemoryMerchantRepository struct {
	merchants map[string]*Merchant
	apiKeys   map[string]*Merchant
	mu        sync.RWMutex
}

func NewInMemoryMerchantRepository() *InMemoryMerchantRepository {
	return &InMemoryMerchantRepository{
		merchants: make(map[string]*Merchant),
		apiKeys:   make(map[string]*Merchant),
	}
}

func (r *InMemoryMerchantRepository) Save(ctx context.Context, merchant *Merchant) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	r.merchants[merchant.ID.Value] = merchant
	r.apiKeys[merchant.APIKey] = merchant
	return nil
}

func (r *InMemoryMerchantRepository) FindByID(ctx context.Context, id *MerchantID) (*Merchant, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	merchant, exists := r.merchants[id.Value]
	if !exists {
		return nil, ErrMerchantNotFound
	}
	return merchant, nil
}

func (r *InMemoryMerchantRepository) FindByAPIKey(ctx context.Context, apiKey string) (*Merchant, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	merchant, exists := r.apiKeys[apiKey]
	if !exists {
		return nil, ErrInvalidMerchantKey
	}
	return merchant, nil
}

// Mock Gateway Service
type MockGatewayService struct{}

func NewMockGatewayService() *MockGatewayService {
	return &MockGatewayService{}
}

func (g *MockGatewayService) AuthorizePayment(ctx context.Context, payment *Payment) (map[string]interface{}, error) {
	fmt.Printf("🌐 Calling gateway for payment: %s\n", payment.ID.Value)
	
	// Simulate gateway call delay
	time.Sleep(100 * time.Millisecond)
	
	// Simulate success/failure (95% success rate)
	if rand.Float64() > 0.95 {
		return nil, errors.New("gateway error - gateway error हुई")
	}
	
	// Return mock gateway response
	response := map[string]interface{}{
		"gateway_payment_id": fmt.Sprintf("gw_%d", time.Now().Unix()),
		"status":            "authorized",
		"auth_code":         generateAuthCode(),
		"processor":         string(payment.Method),
	}
	
	return response, nil
}

// ====================================================================
// PRESENTATION LAYER - HTTP API
// ====================================================================

type CreatePaymentRequest struct {
	MerchantAPIKey string `json:"merchant_api_key"`
	Amount         int64  `json:"amount"`
	Currency       string `json:"currency"`
	Method         string `json:"method"`
	Description    string `json:"description"`
	CustomerEmail  string `json:"customer_email,omitempty"`
	CustomerPhone  string `json:"customer_phone,omitempty"`
}

type PaymentResponse struct {
	ID          string `json:"id"`
	Amount      *Money `json:"amount"`
	Method      string `json:"method"`
	Status      string `json:"status"`
	Description string `json:"description"`
	CreatedAt   string `json:"created_at"`
}

type PaymentHandler struct {
	paymentService *PaymentService
}

func NewPaymentHandler(paymentService *PaymentService) *PaymentHandler {
	return &PaymentHandler{paymentService: paymentService}
}

func (h *PaymentHandler) CreatePayment(w http.ResponseWriter, r *http.Request) {
	var request CreatePaymentRequest
	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}
	
	payment, err := h.paymentService.CreatePayment(r.Context(), request)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	
	response := PaymentResponse{
		ID:          payment.ID.Value,
		Amount:      payment.Amount,
		Method:      string(payment.Method),
		Status:      string(payment.Status),
		Description: payment.Description,
		CreatedAt:   payment.CreatedAt.Format(time.RFC3339),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (h *PaymentHandler) ProcessPayment(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	paymentID := vars["id"]
	
	err := h.paymentService.ProcessPayment(r.Context(), paymentID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"status": "success",
		"message": "Payment processed successfully",
	})
}

func (h *PaymentHandler) GetPayment(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	paymentID := vars["id"]
	
	payment, err := h.paymentService.GetPayment(r.Context(), paymentID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}
	
	response := PaymentResponse{
		ID:          payment.ID.Value,
		Amount:      payment.Amount,
		Method:      string(payment.Method),
		Status:      string(payment.Status),
		Description: payment.Description,
		CreatedAt:   payment.CreatedAt.Format(time.RFC3339),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// ====================================================================
// UTILITY FUNCTIONS
// ====================================================================

func generateMerchantID() string {
	return fmt.Sprintf("merch_%d_%d", time.Now().Unix(), rand.Intn(1000))
}

func generateAPIKey() string {
	return fmt.Sprintf("rzp_test_%d%d", time.Now().Unix(), rand.Intn(100000))
}

func generateAuthCode() string {
	return fmt.Sprintf("AUTH_%d", rand.Intn(999999))
}

// ====================================================================
// MAIN APPLICATION
// ====================================================================

func main() {
	fmt.Println("💳 Razorpay Payment Microservice - DDD Example")
	fmt.Println(strings.Repeat("=", 55))
	
	// Initialize repositories
	paymentRepo := NewInMemoryPaymentRepository()
	merchantRepo := NewInMemoryMerchantRepository()
	
	// Initialize gateway service
	gatewayService := NewMockGatewayService()
	
	// Initialize domain services
	processingService := NewPaymentProcessingService(gatewayService)
	
	// Initialize application service
	paymentService := NewPaymentService(paymentRepo, merchantRepo, processingService)
	
	// Create sample merchant
	ctx := context.Background()
	merchant := NewMerchant("Tech Startup India", "founder@techstartup.in", "9876543210", "ecommerce")
	merchantRepo.Save(ctx, merchant)
	
	fmt.Printf("🔑 Merchant API Key: %s\n", merchant.APIKey)
	
	// Demo: Create and process payments
	demoPayments(ctx, paymentService, merchant.APIKey)
	
	// Initialize HTTP handlers
	handler := NewPaymentHandler(paymentService)
	
	// Setup routes
	r := mux.NewRouter()
	r.HandleFunc("/payments", handler.CreatePayment).Methods("POST")
	r.HandleFunc("/payments/{id}/process", handler.ProcessPayment).Methods("POST")
	r.HandleFunc("/payments/{id}", handler.GetPayment).Methods("GET")
	
	// Health check
	r.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(map[string]string{
			"status": "healthy",
			"service": "razorpay-payment-service",
		})
	}).Methods("GET")
	
	fmt.Println("\n🚀 Starting Razorpay Payment Microservice on :8080")
	fmt.Println("📋 Endpoints:")
	fmt.Println("   POST   /payments           - Create payment")
	fmt.Println("   POST   /payments/{id}/process - Process payment")
	fmt.Println("   GET    /payments/{id}      - Get payment details")
	fmt.Println("   GET    /health             - Health check")
	
	log.Fatal(http.ListenAndServe(":8080", r))
}

func demoPayments(ctx context.Context, paymentService *PaymentService, apiKey string) {
	fmt.Println("\n🔄 Demo: Creating and Processing Payments")
	fmt.Println(strings.Repeat("-", 45))
	
	// Demo payment scenarios
	scenarios := []CreatePaymentRequest{
		{
			MerchantAPIKey: apiKey,
			Amount:        50000, // ₹500.00
			Currency:      "INR",
			Method:        "upi",
			Description:   "Zomato food order",
			CustomerEmail: "customer@example.com",
			CustomerPhone: "9876543210",
		},
		{
			MerchantAPIKey: apiKey,
			Amount:        250000, // ₹2500.00
			Currency:      "INR",
			Method:        "card",
			Description:   "Flipkart electronics",
			CustomerEmail: "buyer@example.com",
			CustomerPhone: "9876543211",
		},
		{
			MerchantAPIKey: apiKey,
			Amount:        18500, // ₹185.00
			Currency:      "INR",
			Method:        "wallet",
			Description:   "Ola cab ride",
			CustomerEmail: "rider@example.com",
			CustomerPhone: "9876543212",
		},
	}
	
	for i, scenario := range scenarios {
		fmt.Printf("\n💰 Payment Scenario %d: %s\n", i+1, scenario.Description)
		
		// Create payment
		payment, err := paymentService.CreatePayment(ctx, scenario)
		if err != nil {
			fmt.Printf("❌ Failed to create payment: %v\n", err)
			continue
		}
		
		fmt.Printf("✅ Payment created: %s for %s\n", payment.ID.Value, payment.Amount.String())
		
		// Process payment
		err = paymentService.ProcessPayment(ctx, payment.ID.Value)
		if err != nil {
			fmt.Printf("❌ Failed to process payment: %v\n", err)
		} else {
			// Get updated payment
			updatedPayment, _ := paymentService.GetPayment(ctx, payment.ID.Value)
			fmt.Printf("🎯 Payment processed: Status = %s\n", updatedPayment.Status)
		}
		
		// Small delay for demo
		time.Sleep(500 * time.Millisecond)
	}
	
	fmt.Println("\n📊 Demo completed successfully!")
	fmt.Println("✨ DDD principles demonstrated:")
	fmt.Println("   ✅ Domain entities with business logic")
	fmt.Println("   ✅ Value objects for data integrity")
	fmt.Println("   ✅ Repository pattern for persistence")
	fmt.Println("   ✅ Domain services for complex logic")
	fmt.Println("   ✅ Clean architecture separation")
	fmt.Println("   ✅ Microservice-ready design")
}