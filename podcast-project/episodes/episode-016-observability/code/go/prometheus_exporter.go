/*
 * Episode 16: Observability & Monitoring
 * Go Example: High-Performance Prometheus Exporter
 *
 * भारतीय scale के लिए high-performance metrics collection
 * Goroutines और channels के साथ concurrent processing
 *
 * Author: Hindi Tech Podcast
 * Context: High-throughput metrics collection for Indian applications
 */

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/gorilla/mux"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/sirupsen/logrus"
)

// Transaction types for Indian ecosystem
type TransactionType string

const (
	UPITransaction       TransactionType = "upi"
	CardTransaction      TransactionType = "card"
	WalletTransaction    TransactionType = "wallet"
	NetBankingTransaction TransactionType = "netbanking"
	CashOnDelivery       TransactionType = "cod"
)

// Indian banks enum
type BankCode string

const (
	SBI    BankCode = "sbi"
	HDFC   BankCode = "hdfc"
	ICICI  BankCode = "icici"
	AXIS   BankCode = "axis"
	KOTAK  BankCode = "kotak"
	PNB    BankCode = "pnb"
	CANARA BankCode = "canara"
)

// Indian cities for geographic tracking
var IndianCities = []string{
	"Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
	"Pune", "Hyderabad", "Ahmedabad", "Surat", "Jaipur",
	"Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
}

// PaymentTransaction represents a payment transaction
type PaymentTransaction struct {
	TransactionID   string          `json:"transaction_id"`
	Type            TransactionType `json:"type"`
	Bank            BankCode        `json:"bank"`
	Amount          float64         `json:"amount"`
	Currency        string          `json:"currency"`
	Success         bool            `json:"success"`
	ErrorCode       string          `json:"error_code,omitempty"`
	ProcessingTime  time.Duration   `json:"processing_time"`
	UserCity        string          `json:"user_city"`
	MerchantCity    string          `json:"merchant_city"`
	UserTier        string          `json:"user_tier"` // metro, tier1, tier2, tier3
	RetryCount      int             `json:"retry_count"`
	Timestamp       time.Time       `json:"timestamp"`
	RiskScore       float64         `json:"risk_score"`
	IsFraudFlagged  bool            `json:"is_fraud_flagged"`
	BusinessEvent   string          `json:"business_event,omitempty"` // diwali, bbd, nye
}

// IndianPaymentMetrics contains all Prometheus metrics for Indian payment systems
type IndianPaymentMetrics struct {
	// Transaction volume metrics
	TransactionTotal *prometheus.CounterVec
	TransactionAmount *prometheus.CounterVec
	
	// Performance metrics
	TransactionDuration *prometheus.HistogramVec
	ProcessingLatency   *prometheus.SummaryVec
	
	// Success and error metrics
	SuccessRate *prometheus.GaugeVec
	ErrorRate   *prometheus.CounterVec
	
	// Bank-specific metrics
	BankAvailability *prometheus.GaugeVec
	BankResponseTime *prometheus.HistogramVec
	
	// Regional performance metrics
	RegionalLatency  *prometheus.HistogramVec
	CityTransactionRate *prometheus.GaugeVec
	
	// Business metrics
	RevenueByCity     *prometheus.CounterVec
	PeakHourLoad      *prometheus.GaugeVec
	FestivalMultiplier *prometheus.GaugeVec
	
	// Security metrics
	FraudDetectionRate *prometheus.CounterVec
	RiskScoreDistribution *prometheus.HistogramVec
	
	// Compliance metrics
	RBIReportingLag    *prometheus.GaugeVec
	ComplianceScore    *prometheus.GaugeVec
	KYCVerificationRate *prometheus.GaugeVec
	
	// Infrastructure metrics
	ConcurrentConnections *prometheus.GaugeVec
	QueueDepth           *prometheus.GaugeVec
	CacheHitRate         *prometheus.GaugeVec
}

// MetricsCollector handles high-performance metrics collection
type MetricsCollector struct {
	metrics         *IndianPaymentMetrics
	registry        *prometheus.Registry
	transactionChan chan PaymentTransaction
	workerPool      *WorkerPool
	logger          *logrus.Logger
	ctx             context.Context
	cancel          context.CancelFunc
	wg              sync.WaitGroup
	
	// Success rate tracking
	successCounts map[string]*prometheus.CounterVec
	totalCounts   map[string]*prometheus.CounterVec
	
	// Performance tracking
	lastMinuteTransactions []time.Time
	mutex                  sync.RWMutex
}

// WorkerPool manages concurrent transaction processing
type WorkerPool struct {
	numWorkers int
	jobQueue   chan PaymentTransaction
	wg         sync.WaitGroup
	ctx        context.Context
}

// NewIndianPaymentMetrics creates comprehensive metrics for Indian payment systems
func NewIndianPaymentMetrics() *IndianPaymentMetrics {
	return &IndianPaymentMetrics{
		// Core transaction metrics
		TransactionTotal: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "payment_transactions_total",
				Help: "Total payment transactions processed",
			},
			[]string{"type", "bank", "status", "city", "user_tier", "business_event"},
		),
		
		TransactionAmount: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "payment_transaction_amount_inr_total",
				Help: "Total payment transaction amount in INR",
			},
			[]string{"type", "bank", "city", "amount_range"},
		),
		
		// Performance metrics with detailed buckets
		TransactionDuration: prometheus.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "payment_transaction_duration_seconds",
				Help:    "Payment transaction processing duration",
				Buckets: []float64{0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0},
			},
			[]string{"type", "bank", "success"},
		),
		
		ProcessingLatency: prometheus.NewSummaryVec(
			prometheus.SummaryOpts{
				Name:       "payment_processing_latency_seconds",
				Help:       "Payment processing latency summary",
				Objectives: map[float64]float64{0.5: 0.05, 0.9: 0.01, 0.95: 0.005, 0.99: 0.001},
			},
			[]string{"type", "bank"},
		),
		
		// Success and error tracking
		SuccessRate: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "payment_success_rate_percentage",
				Help: "Payment success rate by various dimensions",
			},
			[]string{"type", "bank", "city", "time_window"},
		),
		
		ErrorRate: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "payment_errors_total",
				Help: "Total payment errors by type and cause",
			},
			[]string{"type", "bank", "error_code", "error_category"},
		),
		
		// Bank-specific metrics
		BankAvailability: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "bank_upi_availability",
				Help: "Bank UPI service availability (1=up, 0=down)",
			},
			[]string{"bank", "service_type"},
		),
		
		BankResponseTime: prometheus.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "bank_response_time_seconds",
				Help:    "Bank API response time",
				Buckets: []float64{0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0},
			},
			[]string{"bank", "api_endpoint"},
		),
		
		// Regional performance
		RegionalLatency: prometheus.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "regional_transaction_latency_seconds",
				Help:    "Transaction latency by Indian regions",
				Buckets: []float64{0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0},
			},
			[]string{"source_city", "destination_city", "user_tier"},
		),
		
		CityTransactionRate: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "city_transaction_rate_per_second",
				Help: "Transaction rate per second by city",
			},
			[]string{"city", "user_tier"},
		),
		
		// Business intelligence metrics
		RevenueByCity: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "revenue_by_city_inr_total",
				Help: "Total revenue by Indian cities in INR",
			},
			[]string{"city", "merchant_category", "payment_type"},
		),
		
		PeakHourLoad: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "peak_hour_transaction_load",
				Help: "Transaction load during Indian peak hours",
			},
			[]string{"hour", "day_type", "city"},
		),
		
		FestivalMultiplier: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "festival_transaction_multiplier",
				Help: "Transaction volume multiplier during Indian festivals",
			},
			[]string{"festival", "payment_type", "region"},
		),
		
		// Security metrics
		FraudDetectionRate: prometheus.NewCounterVec(
			prometheus.CounterOpts{
				Name: "fraud_detection_events_total",
				Help: "Total fraud detection events",
			},
			[]string{"detection_type", "risk_level", "payment_type"},
		),
		
		RiskScoreDistribution: prometheus.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "transaction_risk_score",
				Help:    "Distribution of transaction risk scores",
				Buckets: []float64{0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0},
			},
			[]string{"payment_type", "amount_range", "city"},
		),
		
		// Compliance metrics (RBI requirements)
		RBIReportingLag: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "rbi_reporting_lag_seconds",
				Help: "RBI transaction reporting lag in seconds",
			},
			[]string{"bank", "report_type"},
		),
		
		ComplianceScore: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "payment_compliance_score",
				Help: "Payment system compliance score (0-100)",
			},
			[]string{"compliance_type", "bank"},
		),
		
		KYCVerificationRate: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "kyc_verification_rate_percentage",
				Help: "KYC verification success rate",
			},
			[]string{"verification_type", "city"},
		),
		
		// Infrastructure metrics
		ConcurrentConnections: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "concurrent_connections",
				Help: "Current number of concurrent connections",
			},
			[]string{"service", "endpoint"},
		),
		
		QueueDepth: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "processing_queue_depth",
				Help: "Current processing queue depth",
			},
			[]string{"queue_type", "priority"},
		),
		
		CacheHitRate: prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "cache_hit_rate_percentage",
				Help: "Cache hit rate percentage",
			},
			[]string{"cache_type", "region"},
		),
	}
}

// NewMetricsCollector creates a new high-performance metrics collector
func NewMetricsCollector(numWorkers int) *MetricsCollector {
	ctx, cancel := context.WithCancel(context.Background())
	
	metrics := NewIndianPaymentMetrics()
	registry := prometheus.NewRegistry()
	
	// Register all metrics
	registry.MustRegister(
		metrics.TransactionTotal,
		metrics.TransactionAmount,
		metrics.TransactionDuration,
		metrics.ProcessingLatency,
		metrics.SuccessRate,
		metrics.ErrorRate,
		metrics.BankAvailability,
		metrics.BankResponseTime,
		metrics.RegionalLatency,
		metrics.CityTransactionRate,
		metrics.RevenueByCity,
		metrics.PeakHourLoad,
		metrics.FestivalMultiplier,
		metrics.FraudDetectionRate,
		metrics.RiskScoreDistribution,
		metrics.RBIReportingLag,
		metrics.ComplianceScore,
		metrics.KYCVerificationRate,
		metrics.ConcurrentConnections,
		metrics.QueueDepth,
		metrics.CacheHitRate,
	)
	
	logger := logrus.New()
	logger.SetFormatter(&logrus.JSONFormatter{})
	
	transactionChan := make(chan PaymentTransaction, 10000) // High-capacity buffer
	
	workerPool := &WorkerPool{
		numWorkers: numWorkers,
		jobQueue:   transactionChan,
		ctx:        ctx,
	}
	
	return &MetricsCollector{
		metrics:         metrics,
		registry:        registry,
		transactionChan: transactionChan,
		workerPool:      workerPool,
		logger:          logger,
		ctx:             ctx,
		cancel:          cancel,
		successCounts:   make(map[string]*prometheus.CounterVec),
		totalCounts:     make(map[string]*prometheus.CounterVec),
		lastMinuteTransactions: make([]time.Time, 0, 1000),
	}
}

// Start begins the metrics collection process
func (mc *MetricsCollector) Start() {
	mc.logger.Info("Starting Indian Payment Metrics Collector")
	
	// Start worker pool
	mc.startWorkerPool()
	
	// Start periodic updates
	mc.startPeriodicUpdates()
	
	mc.logger.Info("Metrics collector started successfully")
}

// startWorkerPool initializes and starts the worker pool for concurrent processing
func (mc *MetricsCollector) startWorkerPool() {
	for i := 0; i < mc.workerPool.numWorkers; i++ {
		mc.wg.Add(1)
		go mc.worker(i)
	}
	
	mc.logger.WithField("workers", mc.workerPool.numWorkers).Info("Worker pool started")
}

// worker processes transactions concurrently
func (mc *MetricsCollector) worker(workerID int) {
	defer mc.wg.Done()
	
	mc.logger.WithField("worker_id", workerID).Info("Worker started")
	
	for {
		select {
		case transaction := <-mc.transactionChan:
			mc.processTransaction(transaction, workerID)
		case <-mc.ctx.Done():
			mc.logger.WithField("worker_id", workerID).Info("Worker stopping")
			return
		}
	}
}

// RecordTransaction queues a transaction for processing
func (mc *MetricsCollector) RecordTransaction(transaction PaymentTransaction) error {
	select {
	case mc.transactionChan <- transaction:
		return nil
	case <-time.After(time.Millisecond * 100):
		mc.logger.Warn("Transaction queue full, dropping transaction")
		return fmt.Errorf("transaction queue full")
	}
}

// processTransaction handles the actual metrics recording
func (mc *MetricsCollector) processTransaction(transaction PaymentTransaction, workerID int) {
	startTime := time.Now()
	
	// Track transaction timing
	mc.mutex.Lock()
	mc.lastMinuteTransactions = append(mc.lastMinuteTransactions, startTime)
	// Keep only last minute of transactions
	cutoff := startTime.Add(-time.Minute)
	for len(mc.lastMinuteTransactions) > 0 && mc.lastMinuteTransactions[0].Before(cutoff) {
		mc.lastMinuteTransactions = mc.lastMinuteTransactions[1:]
	}
	mc.mutex.Unlock()
	
	// Record core transaction metrics
	status := "success"
	if !transaction.Success {
		status = "failure"
	}
	
	mc.metrics.TransactionTotal.WithLabelValues(
		string(transaction.Type),
		string(transaction.Bank),
		status,
		transaction.UserCity,
		transaction.UserTier,
		transaction.BusinessEvent,
	).Inc()
	
	// Record transaction amount (only for successful transactions)
	if transaction.Success {
		amountRange := getAmountRange(transaction.Amount)
		mc.metrics.TransactionAmount.WithLabelValues(
			string(transaction.Type),
			string(transaction.Bank),
			transaction.UserCity,
			amountRange,
		).Add(transaction.Amount)
		
		// Record revenue by city
		mc.metrics.RevenueByCity.WithLabelValues(
			transaction.MerchantCity,
			"ecommerce", // Simplified merchant category
			string(transaction.Type),
		).Add(transaction.Amount)
	}
	
	// Record processing duration
	durationSeconds := transaction.ProcessingTime.Seconds()
	mc.metrics.TransactionDuration.WithLabelValues(
		string(transaction.Type),
		string(transaction.Bank),
		status,
	).Observe(durationSeconds)
	
	mc.metrics.ProcessingLatency.WithLabelValues(
		string(transaction.Type),
		string(transaction.Bank),
	).Observe(durationSeconds)
	
	// Record errors for failed transactions
	if !transaction.Success && transaction.ErrorCode != "" {
		errorCategory := categorizeError(transaction.ErrorCode)
		mc.metrics.ErrorRate.WithLabelValues(
			string(transaction.Type),
			string(transaction.Bank),
			transaction.ErrorCode,
			errorCategory,
		).Inc()
	}
	
	// Record regional latency (if different cities)
	if transaction.UserCity != transaction.MerchantCity {
		mc.metrics.RegionalLatency.WithLabelValues(
			transaction.UserCity,
			transaction.MerchantCity,
			transaction.UserTier,
		).Observe(durationSeconds)
	}
	
	// Record security metrics
	if transaction.RiskScore > 0 {
		amountRange := getAmountRange(transaction.Amount)
		mc.metrics.RiskScoreDistribution.WithLabelValues(
			string(transaction.Type),
			amountRange,
			transaction.UserCity,
		).Observe(transaction.RiskScore)
		
		if transaction.IsFraudFlagged {
			riskLevel := getRiskLevel(transaction.RiskScore)
			mc.metrics.FraudDetectionRate.WithLabelValues(
				"ml_model",
				riskLevel,
				string(transaction.Type),
			).Inc()
		}
	}
	
	// Log processing time
	processingTime := time.Since(startTime)
	mc.logger.WithFields(logrus.Fields{
		"worker_id":       workerID,
		"transaction_id":  transaction.TransactionID,
		"type":           transaction.Type,
		"bank":           transaction.Bank,
		"amount":         transaction.Amount,
		"success":        transaction.Success,
		"processing_time": processingTime.Milliseconds(),
	}).Debug("Transaction processed")
}

// startPeriodicUpdates starts background goroutines for periodic metric updates
func (mc *MetricsCollector) startPeriodicUpdates() {
	// Update success rates every 30 seconds
	mc.wg.Add(1)
	go mc.updateSuccessRates()
	
	// Update business metrics every minute
	mc.wg.Add(1)
	go mc.updateBusinessMetrics()
	
	// Update compliance metrics every 5 minutes
	mc.wg.Add(1)
	go mc.updateComplianceMetrics()
	
	// Update infrastructure metrics every 10 seconds
	mc.wg.Add(1)
	go mc.updateInfrastructureMetrics()
}

// updateSuccessRates calculates and updates success rates
func (mc *MetricsCollector) updateSuccessRates() {
	defer mc.wg.Done()
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			// Calculate current transaction rate
			mc.mutex.RLock()
			currentRate := float64(len(mc.lastMinuteTransactions))
			mc.mutex.RUnlock()
			
			// Update transaction rate by city
			for _, city := range IndianCities {
				for _, tier := range []string{"metro", "tier1", "tier2", "tier3"} {
					// Simulate city-specific rates
					cityRate := currentRate * getCityMultiplier(city, tier)
					mc.metrics.CityTransactionRate.WithLabelValues(city, tier).Set(cityRate)
				}
			}
			
			// Update peak hour metrics
			mc.updatePeakHourMetrics()
			
		case <-mc.ctx.Done():
			return
		}
	}
}

// updateBusinessMetrics updates business intelligence metrics
func (mc *MetricsCollector) updateBusinessMetrics() {
	defer mc.wg.Done()
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			mc.updateFestivalMetrics()
			
		case <-mc.ctx.Done():
			return
		}
	}
}

// updateComplianceMetrics updates regulatory compliance metrics
func (mc *MetricsCollector) updateComplianceMetrics() {
	defer mc.wg.Done()
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			// Update RBI reporting lag
			for _, bank := range []BankCode{SBI, HDFC, ICICI, AXIS, KOTAK} {
				lag := rand.Float64() * 300 // 0-5 minutes
				mc.metrics.RBIReportingLag.WithLabelValues(
					string(bank),
					"transaction_summary",
				).Set(lag)
			}
			
			// Update compliance scores
			for _, bank := range []BankCode{SBI, HDFC, ICICI, AXIS, KOTAK} {
				score := 90 + rand.Float64()*10 // 90-100%
				mc.metrics.ComplianceScore.WithLabelValues(
					"rbi_guidelines",
					string(bank),
				).Set(score)
			}
			
			// Update KYC verification rates
			for _, city := range IndianCities {
				rate := 85 + rand.Float64()*13 // 85-98%
				mc.metrics.KYCVerificationRate.WithLabelValues(
					"full_kyc",
					city,
				).Set(rate)
			}
			
		case <-mc.ctx.Done():
			return
		}
	}
}

// updateInfrastructureMetrics updates system infrastructure metrics
func (mc *MetricsCollector) updateInfrastructureMetrics() {
	defer mc.wg.Done()
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			// Update concurrent connections
			connections := 1000 + rand.Float64()*9000 // 1K-10K connections
			mc.metrics.ConcurrentConnections.WithLabelValues(
				"payment_api",
				"process_transaction",
			).Set(connections)
			
			// Update queue depth
			queueDepth := float64(len(mc.transactionChan))
			mc.metrics.QueueDepth.WithLabelValues(
				"transaction_processing",
				"high",
			).Set(queueDepth)
			
			// Update cache hit rates
			for _, region := range []string{"mumbai", "delhi", "bangalore"} {
				hitRate := 80 + rand.Float64()*18 // 80-98%
				mc.metrics.CacheHitRate.WithLabelValues(
					"user_session",
					region,
				).Set(hitRate)
			}
			
			// Update bank availability
			for _, bank := range []BankCode{SBI, HDFC, ICICI, AXIS, KOTAK} {
				availability := 1.0
				if rand.Float64() < 0.05 { // 5% chance of downtime
					availability = 0.0
				}
				mc.metrics.BankAvailability.WithLabelValues(
					string(bank),
					"upi_gateway",
				).Set(availability)
			}
			
		case <-mc.ctx.Done():
			return
		}
	}
}

// updatePeakHourMetrics updates metrics specific to Indian peak hours
func (mc *MetricsCollector) updatePeakHourMetrics() {
	now := time.Now()
	hour := now.Hour()
	dayType := "weekday"
	if now.Weekday() == time.Saturday || now.Weekday() == time.Sunday {
		dayType = "weekend"
	}
	
	// Peak hours: 10-11 AM (Tatkal booking), 7-9 PM (evening shopping)
	var loadMultiplier float64 = 1.0
	if (hour >= 10 && hour <= 11) || (hour >= 19 && hour <= 21) {
		loadMultiplier = 3.0 + rand.Float64()*2.0 // 3-5x normal load
	}
	
	for _, city := range IndianCities[:5] { // Top 5 cities
		load := 100 * loadMultiplier * getCityMultiplier(city, "metro")
		mc.metrics.PeakHourLoad.WithLabelValues(
			strconv.Itoa(hour),
			dayType,
			city,
		).Set(load)
	}
}

// updateFestivalMetrics updates festival-specific transaction multipliers
func (mc *MetricsCollector) updateFestivalMetrics() {
	now := time.Now()
	month := int(now.Month())
	
	festivals := map[int]struct {
		name       string
		multiplier float64
	}{
		10: {"dussehra", 3.5},      // October - Dussehra/BBD
		11: {"diwali", 8.0},        // November - Diwali
		12: {"christmas", 4.0},     // December - Christmas/NYE
		3:  {"holi", 2.5},          // March - Holi
		8:  {"raksha_bandhan", 2.0}, // August - Raksha Bandhan
	}
	
	if festival, exists := festivals[month]; exists {
		for _, paymentType := range []TransactionType{UPITransaction, CardTransaction, WalletTransaction} {
			for _, region := range []string{"north", "south", "west", "east"} {
				multiplier := festival.multiplier
				if paymentType == UPITransaction {
					multiplier *= 1.2 // UPI sees higher festival growth
				}
				
				mc.metrics.FestivalMultiplier.WithLabelValues(
					festival.name,
					string(paymentType),
					region,
				).Set(multiplier)
			}
		}
	}
}

// Stop gracefully shuts down the metrics collector
func (mc *MetricsCollector) Stop() {
	mc.logger.Info("Stopping metrics collector")
	
	mc.cancel()
	close(mc.transactionChan)
	
	mc.wg.Wait()
	
	mc.logger.Info("Metrics collector stopped")
}

// GetRegistry returns the Prometheus registry
func (mc *MetricsCollector) GetRegistry() *prometheus.Registry {
	return mc.registry
}

// Helper functions

func getAmountRange(amount float64) string {
	if amount <= 100 {
		return "micro"
	} else if amount <= 1000 {
		return "small"
	} else if amount <= 10000 {
		return "medium"
	} else if amount <= 100000 {
		return "large"
	} else {
		return "bulk"
	}
}

func categorizeError(errorCode string) string {
	upperCode := strings.ToUpper(errorCode)
	
	if strings.Contains(upperCode, "TIMEOUT") || strings.Contains(upperCode, "BT") {
		return "BANK_TIMEOUT"
	} else if strings.Contains(upperCode, "INSUFFICIENT") || strings.Contains(upperCode, "IF") {
		return "INSUFFICIENT_FUNDS"
	} else if strings.Contains(upperCode, "AUTH") || strings.Contains(upperCode, "PIN") {
		return "AUTHENTICATION_FAILED"
	} else if strings.Contains(upperCode, "NETWORK") || strings.Contains(upperCode, "CONN") {
		return "NETWORK_ERROR"
	} else if strings.Contains(upperCode, "LIMIT") || strings.Contains(upperCode, "LE") {
		return "LIMIT_EXCEEDED"
	} else if strings.Contains(upperCode, "FRAUD") {
		return "FRAUD_SUSPECTED"
	} else {
		return "TECHNICAL_ERROR"
	}
}

func getRiskLevel(riskScore float64) string {
	if riskScore <= 0.3 {
		return "low"
	} else if riskScore <= 0.6 {
		return "medium"
	} else if riskScore <= 0.8 {
		return "high"
	} else {
		return "critical"
	}
}

func getCityMultiplier(city, tier string) float64 {
	tierMultipliers := map[string]float64{
		"metro": 1.0,
		"tier1": 0.7,
		"tier2": 0.4,
		"tier3": 0.2,
	}
	
	cityMultipliers := map[string]float64{
		"Mumbai":    1.0,
		"Delhi":     0.9,
		"Bangalore": 0.8,
		"Chennai":   0.6,
		"Kolkata":   0.5,
	}
	
	cityMult := cityMultipliers[city]
	if cityMult == 0 {
		cityMult = 0.3 // Default for smaller cities
	}
	
	tierMult := tierMultipliers[tier]
	if tierMult == 0 {
		tierMult = 0.5 // Default
	}
	
	return cityMult * tierMult
}

// TransactionGenerator generates realistic Indian payment transactions
type TransactionGenerator struct {
	rand *rand.Rand
}

func NewTransactionGenerator() *TransactionGenerator {
	return &TransactionGenerator{
		rand: rand.New(rand.NewSource(time.Now().UnixNano())),
	}
}

func (tg *TransactionGenerator) GenerateTransaction() PaymentTransaction {
	// Payment method distribution (UPI dominant in India)
	paymentTypes := []TransactionType{UPITransaction, CardTransaction, WalletTransaction, NetBankingTransaction}
	weights := []float64{0.7, 0.15, 0.1, 0.05} // UPI 70%, Cards 15%, Wallets 10%, NetBanking 5%
	
	paymentType := tg.weightedChoice(paymentTypes, weights)
	
	// Bank selection
	banks := []BankCode{SBI, HDFC, ICICI, AXIS, KOTAK, PNB, CANARA}
	bank := banks[tg.rand.Intn(len(banks))]
	
	// Amount generation based on payment type
	var amount float64
	switch paymentType {
	case UPITransaction:
		amount = 50 + tg.rand.Float64()*4950 // ₹50-5000 typical UPI range
	case CardTransaction:
		amount = 500 + tg.rand.Float64()*49500 // ₹500-50000 typical card range
	case WalletTransaction:
		amount = 100 + tg.rand.Float64()*1900 // ₹100-2000 wallet recharges
	default:
		amount = 200 + tg.rand.Float64()*9800 // ₹200-10000 others
	}
	
	// Success rate varies by payment type
	successRates := map[TransactionType]float64{
		UPITransaction:       0.96,
		CardTransaction:      0.88,
		WalletTransaction:    0.98,
		NetBankingTransaction: 0.82,
	}
	
	success := tg.rand.Float64() < successRates[paymentType]
	
	// Error code for failed transactions
	var errorCode string
	if !success {
		errors := []string{"BT01", "IF01", "NE01", "LE01", "AUTH_FAIL", "FRAUD_DETECTED"}
		errorCode = errors[tg.rand.Intn(len(errors))]
	}
	
	// Processing time varies by type and success
	var processingTime time.Duration
	if success {
		processingTime = time.Duration(1000+tg.rand.Intn(4000)) * time.Millisecond // 1-5 seconds
	} else {
		processingTime = time.Duration(2000+tg.rand.Intn(8000)) * time.Millisecond // 2-10 seconds
	}
	
	// Geographic selection
	userCity := IndianCities[tg.rand.Intn(len(IndianCities))]
	merchantCity := userCity
	if tg.rand.Float64() < 0.2 { // 20% cross-city transactions
		merchantCity = IndianCities[tg.rand.Intn(len(IndianCities))]
	}
	
	// User tier based on city
	var userTier string
	switch userCity {
	case "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Pune":
		userTier = "metro"
	case "Hyderabad", "Ahmedabad", "Jaipur", "Surat":
		userTier = "tier1"
	default:
		userTier = "tier2"
	}
	
	// Risk scoring
	riskScore := 0.1 + tg.rand.Float64()*0.3 // Base risk 0.1-0.4
	if amount > 50000 {
		riskScore += 0.2
	}
	if userTier != "metro" {
		riskScore += 0.1
	}
	if riskScore > 1.0 {
		riskScore = 1.0
	}
	
	isFraudFlagged := riskScore > 0.7
	
	// Business event detection
	var businessEvent string
	month := time.Now().Month()
	switch month {
	case 10:
		businessEvent = "dussehra_bbd"
	case 11:
		businessEvent = "diwali"
	case 12:
		businessEvent = "christmas_nye"
	default:
		businessEvent = ""
	}
	
	transactionID := fmt.Sprintf("TXN%d%04d", time.Now().Unix(), tg.rand.Intn(10000))
	
	return PaymentTransaction{
		TransactionID:   transactionID,
		Type:           paymentType,
		Bank:           bank,
		Amount:         amount,
		Currency:       "INR",
		Success:        success,
		ErrorCode:      errorCode,
		ProcessingTime: processingTime,
		UserCity:       userCity,
		MerchantCity:   merchantCity,
		UserTier:       userTier,
		RetryCount:     tg.rand.Intn(3),
		Timestamp:      time.Now(),
		RiskScore:      riskScore,
		IsFraudFlagged: isFraudFlagged,
		BusinessEvent:  businessEvent,
	}
}

func (tg *TransactionGenerator) weightedChoice(items []TransactionType, weights []float64) TransactionType {
	totalWeight := 0.0
	for _, weight := range weights {
		totalWeight += weight
	}
	
	r := tg.rand.Float64() * totalWeight
	cumulative := 0.0
	
	for i, weight := range weights {
		cumulative += weight
		if r <= cumulative {
			return items[i]
		}
	}
	
	return items[len(items)-1]
}

// HTTP handlers

func healthHandler(w http.ResponseWriter, r *http.Request) {
	response := map[string]interface{}{
		"status":    "UP",
		"timestamp": time.Now().Format(time.RFC3339),
		"service":   "Indian Payment Metrics Exporter",
		"version":   "1.0.0",
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func transactionHandler(collector *MetricsCollector, generator *TransactionGenerator) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		
		// Generate and process transaction
		transaction := generator.GenerateTransaction()
		
		err := collector.RecordTransaction(transaction)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		
		response := map[string]interface{}{
			"status":         "success",
			"transaction_id": transaction.TransactionID,
			"amount":         transaction.Amount,
			"processing_time": transaction.ProcessingTime.Milliseconds(),
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}
}

func main() {
	// Configuration
	numWorkers := 10
	port := ":8080"
	
	// Initialize components
	collector := NewMetricsCollector(numWorkers)
	generator := NewTransactionGenerator()
	
	// Start metrics collection
	collector.Start()
	defer collector.Stop()
	
	// Setup HTTP routes
	router := mux.NewRouter()
	
	// Prometheus metrics endpoint
	router.Handle("/metrics", promhttp.HandlerFor(collector.GetRegistry(), promhttp.HandlerOpts{}))
	
	// Health check endpoint
	router.HandleFunc("/health", healthHandler)
	
	// Transaction processing endpoint
	router.HandleFunc("/api/transaction", transactionHandler(collector, generator))
	
	// Start transaction simulation
	go func() {
		ticker := time.NewTicker(100 * time.Millisecond) // 10 TPS
		defer ticker.Stop()
		
		for {
			select {
			case <-ticker.C:
				transaction := generator.GenerateTransaction()
				if err := collector.RecordTransaction(transaction); err != nil {
					log.Printf("Failed to record transaction: %v", err)
				}
			case <-collector.ctx.Done():
				return
			}
		}
	}()
	
	// Setup graceful shutdown
	server := &http.Server{
		Addr:    port,
		Handler: router,
	}
	
	// Start server
	go func() {
		log.Printf("🚀 Indian Payment Metrics Exporter starting on %s", port)
		log.Printf("📊 Metrics endpoint: http://localhost%s/metrics", port)
		log.Printf("🏥 Health endpoint: http://localhost%s/health", port)
		log.Printf("💳 Transaction endpoint: http://localhost%s/api/transaction", port)
		
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed to start: %v", err)
		}
	}()
	
	// Wait for interrupt signal
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c
	
	log.Println("🛑 Shutting down server...")
	
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	
	if err := server.Shutdown(ctx); err != nil {
		log.Printf("Server forced to shutdown: %v", err)
	}
	
	log.Println("✅ Server exited")
}

/*
Production Deployment Configuration:

1. Dockerfile:
```dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
```

2. Kubernetes Deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-metrics-exporter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-metrics-exporter
  template:
    metadata:
      labels:
        app: payment-metrics-exporter
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: payment-metrics-exporter
        image: payment-metrics-exporter:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

3. Performance Optimizations:
   - Worker pool for concurrent processing
   - High-capacity buffered channels
   - Efficient metric labeling
   - Memory-efficient data structures
   - Goroutine leak prevention

4. Monitoring and Alerting:
   - High transaction processing rate (>1000 TPS)
   - Low latency metrics collection (<1ms)
   - Comprehensive error tracking
   - Regional performance analysis
   - Festival season capacity planning

5. Production Considerations:
   - Proper error handling and recovery
   - Graceful shutdown procedures
   - Resource limit management
   - Metric cardinality control
   - Security and authentication
*/