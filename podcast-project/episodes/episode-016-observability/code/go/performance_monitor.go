// Episode 16: Observability & Monitoring
// Go Example: High-Performance Application Monitoring
//
// भारतीय context: IRCTC Tatkal booking system performance monitoring
// Real-world scenario: Handle 10 lakh concurrent users at 10 AM

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net/http"
	"runtime"
	"sync"
	"sync/atomic"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// IndianPerformanceMonitor represents a high-performance monitoring system
// optimized for Indian scale applications
type IndianPerformanceMonitor struct {
	// Atomic counters for high-concurrency scenarios
	totalRequests     int64
	successfulReqs    int64
	failedRequests    int64
	activeConnections int64

	// Prometheus metrics
	requestDuration  *prometheus.HistogramVec
	requestCounter   *prometheus.CounterVec
	activeConnGauge  prometheus.Gauge
	systemMetrics    *prometheus.GaugeVec
	businessMetrics  *prometheus.GaugeVec

	// Indian-specific tracking
	regionalMetrics map[string]*RegionalMetrics
	festivalMetrics *FestivalMetrics
	
	// Performance tracking
	responseTimeData []float64
	mu              sync.RWMutex
	
	// Circuit breaker for protection
	circuitBreaker *CircuitBreaker

	// Context for graceful shutdown
	ctx    context.Context
	cancel context.CancelFunc
}

// RegionalMetrics tracks performance by Indian regions
type RegionalMetrics struct {
	Region        string
	RequestCount  int64
	AvgLatency    float64
	ErrorRate     float64
	PeakCapacity  int64
	NetworkQuality float64 // 0.0 to 1.0 (1.0 = best)
}

// FestivalMetrics tracks performance during Indian festivals
type FestivalMetrics struct {
	Festival        string
	TrafficMultiplier float64
	StartTime       time.Time
	PeakRequests    int64
	SystemStability float64
}

// CircuitBreaker protects system from overload
type CircuitBreaker struct {
	failureThreshold int64
	recoveryTime     time.Duration
	state           int32 // 0: closed, 1: open, 2: half-open
	lastFailTime    int64
	failures        int64
}

// Transaction represents a business transaction (like Tatkal booking)
type Transaction struct {
	ID              string
	Type            TransactionType
	UserRegion      string
	StartTime       time.Time
	EndTime         time.Time
	Duration        time.Duration
	Success         bool
	ErrorCode       string
	BusinessContext map[string]interface{}
}

type TransactionType int

const (
	TatkalBooking TransactionType = iota
	GeneralBooking
	Payment
	Cancellation
	Refund
)

// Indian regions for monitoring
var IndianRegions = []string{
	"MUMBAI", "DELHI", "BANGALORE", "CHENNAI", "KOLKATA",
	"HYDERABAD", "PUNE", "AHMEDABAD", "JAIPUR", "LUCKNOW",
}

// NewIndianPerformanceMonitor creates a new performance monitor
func NewIndianPerformanceMonitor() *IndianPerformanceMonitor {
	ctx, cancel := context.WithCancel(context.Background())
	
	// Initialize Prometheus metrics
	requestDuration := prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "http_request_duration_seconds",
			Help: "HTTP request duration in seconds",
			Buckets: []float64{0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10},
		},
		[]string{"method", "endpoint", "status_code", "region", "user_type"},
	)

	requestCounter := prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status_code", "region"},
	)

	activeConnGauge := prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "active_connections",
		Help: "Current number of active connections",
	})

	systemMetrics := prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "system_metrics",
			Help: "System performance metrics",
		},
		[]string{"metric_type"},
	)

	businessMetrics := prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "business_metrics",
			Help: "Indian business-specific metrics",
		},
		[]string{"metric_type", "context"},
	)

	// Register metrics
	prometheus.MustRegister(requestDuration, requestCounter, activeConnGauge, systemMetrics, businessMetrics)

	monitor := &IndianPerformanceMonitor{
		requestDuration: requestDuration,
		requestCounter:  requestCounter,
		activeConnGauge: activeConnGauge,
		systemMetrics:   systemMetrics,
		businessMetrics: businessMetrics,
		regionalMetrics: make(map[string]*RegionalMetrics),
		festivalMetrics: &FestivalMetrics{},
		responseTimeData: make([]float64, 0, 10000),
		circuitBreaker:  NewCircuitBreaker(100, 30*time.Second),
		ctx:            ctx,
		cancel:         cancel,
	}

	// Initialize regional metrics
	for _, region := range IndianRegions {
		monitor.regionalMetrics[region] = &RegionalMetrics{
			Region:         region,
			NetworkQuality: getRegionNetworkQuality(region),
		}
	}

	// Start background monitoring
	go monitor.startSystemMonitoring()
	go monitor.startBusinessMetricsCollection()
	
	log.Println("🚀 Indian Performance Monitor initialized")
	return monitor
}

// RecordHTTPRequest records an HTTP request with comprehensive metrics
func (m *IndianPerformanceMonitor) RecordHTTPRequest(method, endpoint, statusCode, region, userType string, duration time.Duration) {
	atomic.AddInt64(&m.totalRequests, 1)

	if statusCode[0] == '2' {
		atomic.AddInt64(&m.successfulReqs, 1)
	} else {
		atomic.AddInt64(&m.failedRequests, 1)
	}

	// Record Prometheus metrics
	m.requestDuration.WithLabelValues(method, endpoint, statusCode, region, userType).Observe(duration.Seconds())
	m.requestCounter.WithLabelValues(method, endpoint, statusCode, region).Inc()

	// Update regional metrics
	if regionalMetric, exists := m.regionalMetrics[region]; exists {
		atomic.AddInt64(&regionalMetric.RequestCount, 1)
		m.updateRegionalLatency(region, duration.Seconds()*1000) // Convert to milliseconds
	}

	// Store response time for statistical analysis
	m.mu.Lock()
	if len(m.responseTimeData) < cap(m.responseTimeData) {
		m.responseTimeData = append(m.responseTimeData, duration.Seconds()*1000)
	} else {
		// Circular buffer behavior
		m.responseTimeData = append(m.responseTimeData[1:], duration.Seconds()*1000)
	}
	m.mu.Unlock()
}

// RecordTransaction records a business transaction (like Tatkal booking)
func (m *IndianPerformanceMonitor) RecordTransaction(tx Transaction) {
	duration := tx.Duration.Seconds() * 1000 // Convert to milliseconds

	// Business metrics based on transaction type
	switch tx.Type {
	case TatkalBooking:
		m.businessMetrics.WithLabelValues("tatkal_booking_duration", "peak_hour").Set(duration)
		if duration > 10000 { // 10 seconds threshold for Tatkal
			m.businessMetrics.WithLabelValues("tatkal_slow_bookings", "count").Add(1)
		}

	case Payment:
		m.businessMetrics.WithLabelValues("payment_duration", "transaction").Set(duration)
		if tx.Success {
			m.businessMetrics.WithLabelValues("payment_success_rate", "percentage").Add(1)
		} else {
			m.businessMetrics.WithLabelValues("payment_failure_rate", "percentage").Add(1)
		}

	case GeneralBooking:
		m.businessMetrics.WithLabelValues("general_booking_duration", "normal_hour").Set(duration)
	}

	// Regional transaction tracking
	if ctx, ok := tx.BusinessContext["festival"]; ok {
		festival := ctx.(string)
		m.recordFestivalMetric(festival, tx.Success, duration)
	}

	log.Printf("📊 Transaction recorded: %s - %v (%.2fms)", 
		tx.ID, tx.Success, duration)
}

// Middleware for HTTP request monitoring
func (m *IndianPerformanceMonitor) HTTPMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Check circuit breaker
		if !m.circuitBreaker.Allow() {
			http.Error(w, "Service temporarily unavailable", http.StatusServiceUnavailable)
			return
		}

		start := time.Now()
		atomic.AddInt64(&m.activeConnections, 1)
		m.activeConnGauge.Set(float64(atomic.LoadInt64(&m.activeConnections)))

		// Extract context information
		region := r.Header.Get("X-User-Region")
		if region == "" {
			region = "UNKNOWN"
		}
		userType := r.Header.Get("X-User-Type")
		if userType == "" {
			userType = "REGULAR"
		}

		// Custom response writer to capture status code
		wrappedWriter := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

		// Process request
		next.ServeHTTP(wrappedWriter, r)

		// Record metrics
		duration := time.Since(start)
		statusCode := fmt.Sprintf("%d", wrappedWriter.statusCode)
		
		m.RecordHTTPRequest(r.Method, r.URL.Path, statusCode, region, userType, duration)

		atomic.AddInt64(&m.activeConnections, -1)
		m.activeConnGauge.Set(float64(atomic.LoadInt64(&m.activeConnections)))

		// Update circuit breaker
		if wrappedWriter.statusCode >= 500 {
			m.circuitBreaker.RecordFailure()
		} else {
			m.circuitBreaker.RecordSuccess()
		}
	}
}

// startSystemMonitoring starts system-level monitoring in background
func (m *IndianPerformanceMonitor) startSystemMonitoring() {
	ticker := time.NewTicker(15 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-m.ctx.Done():
			return
		case <-ticker.C:
			m.collectSystemMetrics()
		}
	}
}

// collectSystemMetrics collects system performance metrics
func (m *IndianPerformanceMonitor) collectSystemMetrics() {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// Memory metrics
	m.systemMetrics.WithLabelValues("memory_used_mb").Set(float64(memStats.Alloc) / 1024 / 1024)
	m.systemMetrics.WithLabelValues("memory_total_mb").Set(float64(memStats.Sys) / 1024 / 1024)
	m.systemMetrics.WithLabelValues("gc_count").Set(float64(memStats.NumGC))

	// Goroutine metrics
	m.systemMetrics.WithLabelValues("goroutines").Set(float64(runtime.NumGoroutine()))
	
	// CPU metrics (simplified)
	m.systemMetrics.WithLabelValues("cpu_cores").Set(float64(runtime.NumCPU()))

	// Custom Indian scale metrics
	m.systemMetrics.WithLabelValues("total_requests").Set(float64(atomic.LoadInt64(&m.totalRequests)))
	m.systemMetrics.WithLabelValues("success_rate").Set(m.calculateSuccessRate())
	m.systemMetrics.WithLabelValues("active_connections").Set(float64(atomic.LoadInt64(&m.activeConnections)))
}

// startBusinessMetricsCollection starts business-specific metrics collection
func (m *IndianPerformanceMonitor) startBusinessMetricsCollection() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-m.ctx.Done():
			return
		case <-ticker.C:
			m.collectBusinessMetrics()
		}
	}
}

// collectBusinessMetrics collects Indian business-specific metrics
func (m *IndianPerformanceMonitor) collectBusinessMetrics() {
	// Peak hour detection (Tatkal booking at 10 AM)
	currentHour := time.Now().Hour()
	if currentHour == 10 {
		m.businessMetrics.WithLabelValues("tatkal_peak_hour", "active").Set(1)
	} else {
		m.businessMetrics.WithLabelValues("tatkal_peak_hour", "active").Set(0)
	}

	// Festival season detection
	if m.isFestivalSeason() {
		festival := m.getCurrentFestival()
		m.businessMetrics.WithLabelValues("festival_mode", festival).Set(1)
		
		// Adjust performance expectations during festivals
		trafficMultiplier := m.getFestivalTrafficMultiplier(festival)
		m.businessMetrics.WithLabelValues("traffic_multiplier", festival).Set(trafficMultiplier)
	} else {
		m.businessMetrics.WithLabelValues("festival_mode", "normal").Set(0)
		m.businessMetrics.WithLabelValues("traffic_multiplier", "normal").Set(1.0)
	}

	// Regional performance analysis
	m.analyzeRegionalPerformance()

	// Calculate percentiles for response times
	m.calculateResponseTimePercentiles()
}

// analyzeRegionalPerformance analyzes performance across Indian regions
func (m *IndianPerformanceMonitor) analyzeRegionalPerformance() {
	for region, metrics := range m.regionalMetrics {
		// Update regional metrics
		m.businessMetrics.WithLabelValues("regional_requests", region).Set(float64(metrics.RequestCount))
		m.businessMetrics.WithLabelValues("regional_avg_latency", region).Set(metrics.AvgLatency)
		m.businessMetrics.WithLabelValues("regional_error_rate", region).Set(metrics.ErrorRate)
		m.businessMetrics.WithLabelValues("network_quality", region).Set(metrics.NetworkQuality)
	}
}

// calculateResponseTimePercentiles calculates response time percentiles
func (m *IndianPerformanceMonitor) calculateResponseTimePercentiles() {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if len(m.responseTimeData) == 0 {
		return
	}

	// Create a sorted copy
	sortedData := make([]float64, len(m.responseTimeData))
	copy(sortedData, m.responseTimeData)
	
	// Simple bubble sort for small datasets
	for i := 0; i < len(sortedData); i++ {
		for j := 0; j < len(sortedData)-i-1; j++ {
			if sortedData[j] > sortedData[j+1] {
				sortedData[j], sortedData[j+1] = sortedData[j+1], sortedData[j]
			}
		}
	}

	// Calculate percentiles
	p50 := percentile(sortedData, 50)
	p90 := percentile(sortedData, 90)
	p95 := percentile(sortedData, 95)
	p99 := percentile(sortedData, 99)

	m.systemMetrics.WithLabelValues("response_time_p50").Set(p50)
	m.systemMetrics.WithLabelValues("response_time_p90").Set(p90)
	m.systemMetrics.WithLabelValues("response_time_p95").Set(p95)
	m.systemMetrics.WithLabelValues("response_time_p99").Set(p99)
}

// Helper functions

func (m *IndianPerformanceMonitor) calculateSuccessRate() float64 {
	total := atomic.LoadInt64(&m.totalRequests)
	if total == 0 {
		return 100.0
	}
	successful := atomic.LoadInt64(&m.successfulReqs)
	return float64(successful) / float64(total) * 100.0
}

func (m *IndianPerformanceMonitor) updateRegionalLatency(region string, latency float64) {
	if regionalMetric, exists := m.regionalMetrics[region]; exists {
		// Simple moving average
		regionalMetric.AvgLatency = (regionalMetric.AvgLatency + latency) / 2.0
	}
}

func (m *IndianPerformanceMonitor) recordFestivalMetric(festival string, success bool, duration float64) {
	m.festivalMetrics.Festival = festival
	if success {
		m.festivalMetrics.SystemStability += 0.1
	} else {
		m.festivalMetrics.SystemStability -= 0.1
	}
	
	// Clamp stability between 0 and 1
	if m.festivalMetrics.SystemStability < 0 {
		m.festivalMetrics.SystemStability = 0
	} else if m.festivalMetrics.SystemStability > 1 {
		m.festivalMetrics.SystemStability = 1
	}
}

func (m *IndianPerformanceMonitor) isFestivalSeason() bool {
	month := time.Now().Month()
	// Diwali (Oct-Nov), Holi (Mar), New Year (Dec-Jan)
	return month == time.October || month == time.November || 
		   month == time.March || month == time.December || month == time.January
}

func (m *IndianPerformanceMonitor) getCurrentFestival() string {
	month := time.Now().Month()
	switch month {
	case time.October, time.November:
		return "DIWALI"
	case time.March:
		return "HOLI"
	case time.December, time.January:
		return "NEW_YEAR"
	default:
		return "NORMAL"
	}
}

func (m *IndianPerformanceMonitor) getFestivalTrafficMultiplier(festival string) float64 {
	multipliers := map[string]float64{
		"DIWALI":   5.0,
		"HOLI":     3.0,
		"NEW_YEAR": 8.0,
		"NORMAL":   1.0,
	}
	if multiplier, exists := multipliers[festival]; exists {
		return multiplier
	}
	return 1.0
}

func getRegionNetworkQuality(region string) float64 {
	// Simplified network quality by region
	qualities := map[string]float64{
		"MUMBAI":    0.95,
		"BANGALORE": 0.98,
		"DELHI":     0.90,
		"CHENNAI":   0.88,
		"KOLKATA":   0.85,
		"HYDERABAD": 0.87,
		"PUNE":      0.92,
		"AHMEDABAD": 0.80,
		"JAIPUR":    0.75,
		"LUCKNOW":   0.70,
	}
	if quality, exists := qualities[region]; exists {
		return quality
	}
	return 0.75 // Default for unknown regions
}

func percentile(sortedData []float64, percentile int) float64 {
	if len(sortedData) == 0 {
		return 0
	}
	
	index := float64(percentile) / 100.0 * float64(len(sortedData)-1)
	lower := int(math.Floor(index))
	upper := int(math.Ceil(index))
	
	if lower == upper {
		return sortedData[lower]
	}
	
	// Linear interpolation
	weight := index - float64(lower)
	return sortedData[lower]*(1-weight) + sortedData[upper]*weight
}

// Circuit Breaker implementation

func NewCircuitBreaker(failureThreshold int64, recoveryTime time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		failureThreshold: failureThreshold,
		recoveryTime:     recoveryTime,
		state:           0, // closed
	}
}

func (cb *CircuitBreaker) Allow() bool {
	now := time.Now().UnixNano()
	state := atomic.LoadInt32(&cb.state)
	
	if state == 0 { // closed
		return true
	} else if state == 1 { // open
		lastFail := atomic.LoadInt64(&cb.lastFailTime)
		if now-lastFail > cb.recoveryTime.Nanoseconds() {
			atomic.StoreInt32(&cb.state, 2) // half-open
			return true
		}
		return false
	} else { // half-open
		return true
	}
}

func (cb *CircuitBreaker) RecordSuccess() {
	state := atomic.LoadInt32(&cb.state)
	if state == 2 { // half-open
		atomic.StoreInt32(&cb.state, 0) // closed
		atomic.StoreInt64(&cb.failures, 0)
	}
}

func (cb *CircuitBreaker) RecordFailure() {
	failures := atomic.AddInt64(&cb.failures, 1)
	if failures >= cb.failureThreshold {
		atomic.StoreInt32(&cb.state, 1) // open
		atomic.StoreInt64(&cb.lastFailTime, time.Now().UnixNano())
	}
}

// Custom response writer to capture status code
type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

// GetMetricsReport generates a comprehensive metrics report
func (m *IndianPerformanceMonitor) GetMetricsReport() map[string]interface{} {
	report := map[string]interface{}{
		"service":      "Indian Performance Monitor",
		"timestamp":    time.Now().Format(time.RFC3339),
		"total_requests": atomic.LoadInt64(&m.totalRequests),
		"successful_requests": atomic.LoadInt64(&m.successfulReqs),
		"failed_requests": atomic.LoadInt64(&m.failedRequests),
		"success_rate": m.calculateSuccessRate(),
		"active_connections": atomic.LoadInt64(&m.activeConnections),
		"circuit_breaker_state": atomic.LoadInt32(&m.circuitBreaker.state),
	}

	// Regional metrics
	regionalData := make(map[string]interface{})
	for region, metrics := range m.regionalMetrics {
		regionalData[region] = map[string]interface{}{
			"request_count":   metrics.RequestCount,
			"avg_latency_ms":  metrics.AvgLatency,
			"error_rate":      metrics.ErrorRate,
			"network_quality": metrics.NetworkQuality,
		}
	}
	report["regional_metrics"] = regionalData

	// Festival metrics
	report["festival_metrics"] = map[string]interface{}{
		"current_festival": m.getCurrentFestival(),
		"is_festival_season": m.isFestivalSeason(),
		"traffic_multiplier": m.getFestivalTrafficMultiplier(m.getCurrentFestival()),
		"system_stability": m.festivalMetrics.SystemStability,
	}

	return report
}

// Shutdown gracefully shuts down the monitor
func (m *IndianPerformanceMonitor) Shutdown() {
	log.Println("🔄 Shutting down Indian Performance Monitor...")
	m.cancel()
}

// Example handlers for testing

func tatkalBookingHandler(w http.ResponseWriter, r *http.Request) {
	// Simulate Tatkal booking processing
	start := time.Now()
	
	// Simulate processing time (higher during peak hours)
	processingTime := time.Duration(rand.Intn(5000)+500) * time.Millisecond
	if time.Now().Hour() == 10 { // Tatkal peak hour
		processingTime = time.Duration(rand.Intn(10000)+2000) * time.Millisecond
	}
	
	time.Sleep(processingTime)
	
	// Simulate success/failure
	success := rand.Float32() > 0.1 // 90% success rate
	
	if success {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "success",
			"booking_id": fmt.Sprintf("TKT_%d", time.Now().Unix()),
			"processing_time_ms": time.Since(start).Milliseconds(),
		})
	} else {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "failed",
			"error": "Booking not available",
			"processing_time_ms": time.Since(start).Milliseconds(),
		})
	}
}

func paymentHandler(w http.ResponseWriter, r *http.Request) {
	// Simulate payment processing
	start := time.Now()
	processingTime := time.Duration(rand.Intn(3000)+1000) * time.Millisecond
	time.Sleep(processingTime)
	
	success := rand.Float32() > 0.05 // 95% success rate for payments
	
	if success {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "success",
			"payment_id": fmt.Sprintf("PAY_%d", time.Now().Unix()),
			"processing_time_ms": time.Since(start).Milliseconds(),
		})
	} else {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "failed",
			"error": "Payment failed",
			"processing_time_ms": time.Since(start).Milliseconds(),
		})
	}
}

func metricsReportHandler(monitor *IndianPerformanceMonitor) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		report := monitor.GetMetricsReport()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(report)
	}
}

func main() {
	// Initialize performance monitor
	monitor := NewIndianPerformanceMonitor()
	defer monitor.Shutdown()

	// Setup HTTP handlers with monitoring middleware
	http.HandleFunc("/tatkal/book", monitor.HTTPMiddleware(tatkalBookingHandler))
	http.HandleFunc("/payment/process", monitor.HTTPMiddleware(paymentHandler))
	http.HandleFunc("/metrics/report", metricsReportHandler(monitor))
	
	// Prometheus metrics endpoint
	http.Handle("/metrics", promhttp.Handler())

	// Health check endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "healthy",
			"timestamp": time.Now().Format(time.RFC3339),
			"active_connections": atomic.LoadInt64(&monitor.activeConnections),
		})
	})

	fmt.Println("🚀 Starting Indian Performance Monitor")
	fmt.Println("🌐 Server running on :8080")
	fmt.Println("📊 Metrics available at: http://localhost:8080/metrics")
	fmt.Println("📈 Custom report at: http://localhost:8080/metrics/report")
	fmt.Println("🎯 Test Tatkal booking: http://localhost:8080/tatkal/book")
	fmt.Println("💳 Test payments: http://localhost:8080/payment/process")
	
	// Start background simulation for testing
	go func() {
		regions := []string{"MUMBAI", "DELHI", "BANGALORE", "CHENNAI"}
		userTypes := []string{"REGULAR", "PREMIUM", "TATKAL"}
		
		for {
			time.Sleep(time.Duration(rand.Intn(1000)) * time.Millisecond)
			
			// Simulate various requests
			region := regions[rand.Intn(len(regions))]
			userType := userTypes[rand.Intn(len(userTypes))]
			
			client := &http.Client{Timeout: 30 * time.Second}
			
			req, _ := http.NewRequest("GET", "http://localhost:8080/tatkal/book", nil)
			req.Header.Set("X-User-Region", region)
			req.Header.Set("X-User-Type", userType)
			
			client.Do(req)
		}
	}()

	log.Fatal(http.ListenAndServe(":8080", nil))
}