/*
🇮🇳 Health-Aware Load Balancer - Flipkart Warehouse Style
Warehouse health के basis पर orders distribute करने जैसा

Features:
- Real-time health monitoring
- Circuit breaker integration
- Failure detection and recovery
- Flipkart warehouse health patterns
- Automated failover
- Performance metrics
- Hindi comments

Author: Agent 5 - Code Developer
Episode: 27 - Load Balancing
Context: Flipkart warehouse health monitoring system
*/

package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"math"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sync"
	"sync/atomic"
	"time"
)

// WarehouseHealth represents health status of a warehouse
type WarehouseHealth struct {
	IsHealthy           bool          `json:"is_healthy"`
	LastCheck           time.Time     `json:"last_check"`
	ConsecutiveFailures int           `json:"consecutive_failures"`
	ConsecutiveSuccesses int          `json:"consecutive_successes"`
	ResponseTime        time.Duration `json:"response_time"`
	ErrorRate           float64       `json:"error_rate"`
	TotalRequests       uint64        `json:"total_requests"`
	FailedRequests      uint64        `json:"failed_requests"`
	State               string        `json:"state"` // HEALTHY, DEGRADED, FAILED
}

// Warehouse represents a backend server with health monitoring
type Warehouse struct {
	ID              string                `json:"id"`
	URL             *url.URL              `json:"url"`
	Zone            string                `json:"zone"`
	Health          *WarehouseHealth      `json:"health"`
	Metadata        map[string]string     `json:"metadata"`
	CircuitBreaker  *CircuitBreaker       `json:"-"`
	mutex           sync.RWMutex          `json:"-"`
}

// CircuitBreakerState represents circuit breaker states
type CircuitBreakerState int

const (
	StateClosed CircuitBreakerState = iota
	StateHalfOpen
	StateOpen
)

func (s CircuitBreakerState) String() string {
	switch s {
	case StateClosed:
		return "CLOSED"
	case StateHalfOpen:
		return "HALF_OPEN"
	case StateOpen:
		return "OPEN"
	default:
		return "UNKNOWN"
	}
}

// CircuitBreaker implements circuit breaker pattern
type CircuitBreaker struct {
	MaxFailures     int                 `json:"max_failures"`
	ResetTimeout    time.Duration       `json:"reset_timeout"`
	State           CircuitBreakerState `json:"state"`
	FailureCount    int                 `json:"failure_count"`
	LastFailureTime time.Time           `json:"last_failure_time"`
	NextAttempt     time.Time           `json:"next_attempt"`
	mutex           sync.RWMutex        `json:"-"`
}

// NewCircuitBreaker creates a new circuit breaker
func NewCircuitBreaker(maxFailures int, resetTimeout time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		MaxFailures:  maxFailures,
		ResetTimeout: resetTimeout,
		State:        StateClosed,
	}
}

// IsAllowed checks if request is allowed through circuit breaker
func (cb *CircuitBreaker) IsAllowed() bool {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	switch cb.State {
	case StateClosed:
		return true
	case StateOpen:
		// Check if we should transition to half-open
		if time.Now().After(cb.NextAttempt) {
			cb.State = StateHalfOpen
			log.Printf("🔄 Circuit breaker transitioning to HALF_OPEN")
			return true
		}
		return false
	case StateHalfOpen:
		return true
	}
	return false
}

// RecordSuccess records a successful request
func (cb *CircuitBreaker) RecordSuccess() {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	if cb.State == StateHalfOpen {
		// Transition back to closed on success
		cb.State = StateClosed
		cb.FailureCount = 0
		log.Printf("✅ Circuit breaker reset to CLOSED")
	}
}

// RecordFailure records a failed request
func (cb *CircuitBreaker) RecordFailure() {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	cb.FailureCount++
	cb.LastFailureTime = time.Now()

	if cb.FailureCount >= cb.MaxFailures {
		cb.State = StateOpen
		cb.NextAttempt = time.Now().Add(cb.ResetTimeout)
		log.Printf("🔴 Circuit breaker OPENED (failures: %d)", cb.FailureCount)
	}
}

// GetState returns current circuit breaker state
func (cb *CircuitBreaker) GetState() CircuitBreakerState {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()
	return cb.State
}

// NewWarehouse creates a new warehouse with health monitoring
func NewWarehouse(id, urlStr, zone string, metadata map[string]string) *Warehouse {
	url, err := url.Parse(urlStr)
	if err != nil {
		panic(fmt.Sprintf("Invalid URL: %s", urlStr))
	}

	return &Warehouse{
		ID:   id,
		URL:  url,
		Zone: zone,
		Health: &WarehouseHealth{
			IsHealthy: true,
			LastCheck: time.Now(),
			State:     "HEALTHY",
		},
		Metadata:       metadata,
		CircuitBreaker: NewCircuitBreaker(5, 30*time.Second), // 5 failures, 30s reset
	}
}

// IsAvailable checks if warehouse is available for requests
func (w *Warehouse) IsAvailable() bool {
	w.mutex.RLock()
	defer w.mutex.RUnlock()

	return w.Health.IsHealthy && 
		   w.CircuitBreaker.IsAllowed() && 
		   w.Health.State != "FAILED"
}

// UpdateHealth updates warehouse health status
func (w *Warehouse) UpdateHealth(isHealthy bool, responseTime time.Duration) {
	w.mutex.Lock()
	defer w.mutex.Unlock()

	w.Health.LastCheck = time.Now()
	w.Health.ResponseTime = responseTime

	if isHealthy {
		w.Health.ConsecutiveSuccesses++
		w.Health.ConsecutiveFailures = 0
		
		// Gradually improve health state
		if w.Health.ConsecutiveSuccesses >= 3 {
			w.Health.IsHealthy = true
			w.Health.State = "HEALTHY"
		} else if w.Health.State == "FAILED" {
			w.Health.State = "DEGRADED"
		}
		
		w.CircuitBreaker.RecordSuccess()
	} else {
		w.Health.ConsecutiveFailures++
		w.Health.ConsecutiveSuccesses = 0
		atomic.AddUint64(&w.Health.FailedRequests, 1)
		
		// Degrade health state
		if w.Health.ConsecutiveFailures >= 3 {
			w.Health.IsHealthy = false
			w.Health.State = "FAILED"
		} else if w.Health.ConsecutiveFailures >= 2 {
			w.Health.State = "DEGRADED"
		}
		
		w.CircuitBreaker.RecordFailure()
	}

	// Update error rate
	atomic.AddUint64(&w.Health.TotalRequests, 1)
	total := atomic.LoadUint64(&w.Health.TotalRequests)
	failed := atomic.LoadUint64(&w.Health.FailedRequests)
	w.Health.ErrorRate = float64(failed) / float64(total) * 100

	status := "🟢"
	switch w.Health.State {
	case "DEGRADED":
		status = "🟡"
	case "FAILED":
		status = "🔴"
	}

	log.Printf("%s Warehouse %s health updated: %s (consecutive: %d/%d, circuit: %s)",
		status, w.ID, w.Health.State, 
		w.Health.ConsecutiveSuccesses, w.Health.ConsecutiveFailures,
		w.CircuitBreaker.GetState())
}

// GetHealthScore returns a health score (0-100)
func (w *Warehouse) GetHealthScore() float64 {
	w.mutex.RLock()
	defer w.mutex.RUnlock()

	if !w.Health.IsHealthy {
		return 0
	}

	score := 100.0

	// Reduce score based on error rate
	score -= w.Health.ErrorRate

	// Reduce score based on response time
	responseTimeMs := float64(w.Health.ResponseTime.Milliseconds())
	if responseTimeMs > 1000 {
		score -= math.Min(50, responseTimeMs/100)
	}

	// Circuit breaker impact
	switch w.CircuitBreaker.GetState() {
	case StateOpen:
		score = 0
	case StateHalfOpen:
		score *= 0.5
	}

	return math.Max(0, score)
}

// FlipkartLoadBalancer implements health-aware load balancing
type FlipkartLoadBalancer struct {
	warehouses    []*Warehouse        `json:"warehouses"`
	healthChecker *HealthChecker      `json:"-"`
	mutex         sync.RWMutex        `json:"-"`
}

// NewFlipkartLoadBalancer creates a new health-aware load balancer
func NewFlipkartLoadBalancer() *FlipkartLoadBalancer {
	lb := &FlipkartLoadBalancer{
		warehouses: make([]*Warehouse, 0),
	}

	// Start health checker
	lb.healthChecker = NewHealthChecker(lb, 15*time.Second, 5*time.Second)
	lb.healthChecker.Start()

	return lb
}

// AddWarehouse adds a warehouse to the load balancer
func (lb *FlipkartLoadBalancer) AddWarehouse(warehouse *Warehouse) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	lb.warehouses = append(lb.warehouses, warehouse)
	log.Printf("✅ Warehouse added: %s in %s zone", warehouse.ID, warehouse.Zone)
}

// RemoveWarehouse removes a warehouse from the load balancer
func (lb *FlipkartLoadBalancer) RemoveWarehouse(warehouseID string) error {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for i, warehouse := range lb.warehouses {
		if warehouse.ID == warehouseID {
			lb.warehouses = append(lb.warehouses[:i], lb.warehouses[i+1:]...)
			log.Printf("🗑️ Warehouse removed: %s", warehouseID)
			return nil
		}
	}

	return fmt.Errorf("warehouse not found: %s", warehouseID)
}

// GetBestWarehouse returns the healthiest available warehouse
func (lb *FlipkartLoadBalancer) GetBestWarehouse() (*Warehouse, error) {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	var bestWarehouse *Warehouse
	bestScore := float64(-1)

	for _, warehouse := range lb.warehouses {
		if !warehouse.IsAvailable() {
			continue
		}

		score := warehouse.GetHealthScore()
		if score > bestScore {
			bestScore = score
			bestWarehouse = warehouse
		}
	}

	if bestWarehouse != nil {
		log.Printf("🎯 Selected warehouse: %s (health score: %.1f)",
			bestWarehouse.ID, bestScore)
		return bestWarehouse, nil
	}

	return nil, errors.New("no healthy warehouses available")
}

// GetWarehousesByZone returns available warehouses in a specific zone
func (lb *FlipkartLoadBalancer) GetWarehousesByZone(zone string) []*Warehouse {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	var zoneWarehouses []*Warehouse
	for _, warehouse := range lb.warehouses {
		if warehouse.Zone == zone && warehouse.IsAvailable() {
			zoneWarehouses = append(zoneWarehouses, warehouse)
		}
	}

	return zoneWarehouses
}

// GetHealthStatus returns comprehensive health status
func (lb *FlipkartLoadBalancer) GetHealthStatus() map[string]interface{} {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	totalWarehouses := len(lb.warehouses)
	healthyWarehouses := 0
	degradedWarehouses := 0
	failedWarehouses := 0
	zoneStats := make(map[string]map[string]int)

	warehouseDetails := make([]map[string]interface{}, 0, totalWarehouses)

	for _, warehouse := range lb.warehouses {
		// Count by health state
		switch warehouse.Health.State {
		case "HEALTHY":
			healthyWarehouses++
		case "DEGRADED":
			degradedWarehouses++
		case "FAILED":
			failedWarehouses++
		}

		// Zone statistics
		if zoneStats[warehouse.Zone] == nil {
			zoneStats[warehouse.Zone] = make(map[string]int)
		}
		zoneStats[warehouse.Zone][warehouse.Health.State]++

		// Warehouse details
		warehouseDetails = append(warehouseDetails, map[string]interface{}{
			"id":                warehouse.ID,
			"zone":              warehouse.Zone,
			"health_score":      warehouse.GetHealthScore(),
			"state":             warehouse.Health.State,
			"error_rate":        warehouse.Health.ErrorRate,
			"response_time_ms":  warehouse.Health.ResponseTime.Milliseconds(),
			"circuit_breaker":   warehouse.CircuitBreaker.GetState().String(),
			"total_requests":    atomic.LoadUint64(&warehouse.Health.TotalRequests),
			"failed_requests":   atomic.LoadUint64(&warehouse.Health.FailedRequests),
		})
	}

	return map[string]interface{}{
		"total_warehouses":    totalWarehouses,
		"healthy_warehouses":  healthyWarehouses,
		"degraded_warehouses": degradedWarehouses,
		"failed_warehouses":   failedWarehouses,
		"zone_statistics":     zoneStats,
		"warehouse_details":   warehouseDetails,
	}
}

// HealthChecker performs periodic health checks
type HealthChecker struct {
	loadBalancer *FlipkartLoadBalancer
	interval     time.Duration
	timeout      time.Duration
	ctx          context.Context
	cancel       context.CancelFunc
}

// NewHealthChecker creates a new health checker
func NewHealthChecker(lb *FlipkartLoadBalancer, interval, timeout time.Duration) *HealthChecker {
	ctx, cancel := context.WithCancel(context.Background())
	return &HealthChecker{
		loadBalancer: lb,
		interval:     interval,
		timeout:      timeout,
		ctx:          ctx,
		cancel:       cancel,
	}
}

// Start begins health checking
func (hc *HealthChecker) Start() {
	go hc.healthCheckLoop()
	log.Printf("🔍 Health checker started (interval: %v)", hc.interval)
}

// Stop stops health checking
func (hc *HealthChecker) Stop() {
	hc.cancel()
	log.Printf("🛑 Health checker stopped")
}

// healthCheckLoop performs periodic health checks
func (hc *HealthChecker) healthCheckLoop() {
	ticker := time.NewTicker(hc.interval)
	defer ticker.Stop()

	for {
		select {
		case <-hc.ctx.Done():
			return
		case <-ticker.C:
			hc.checkAllWarehouses()
		}
	}
}

// checkAllWarehouses checks health of all warehouses
func (hc *HealthChecker) checkAllWarehouses() {
	hc.loadBalancer.mutex.RLock()
	warehouses := make([]*Warehouse, len(hc.loadBalancer.warehouses))
	copy(warehouses, hc.loadBalancer.warehouses)
	hc.loadBalancer.mutex.RUnlock()

	// Check each warehouse concurrently
	var wg sync.WaitGroup
	for _, warehouse := range warehouses {
		wg.Add(1)
		go func(w *Warehouse) {
			defer wg.Done()
			hc.checkWarehouseHealth(w)
		}(warehouse)
	}
	wg.Wait()
}

// checkWarehouseHealth checks health of a single warehouse
func (hc *HealthChecker) checkWarehouseHealth(warehouse *Warehouse) {
	ctx, cancel := context.WithTimeout(hc.ctx, hc.timeout)
	defer cancel()

	startTime := time.Now()
	healthURL := fmt.Sprintf("%s/health", warehouse.URL.String())

	req, err := http.NewRequestWithContext(ctx, "GET", healthURL, nil)
	if err != nil {
		warehouse.UpdateHealth(false, time.Since(startTime))
		return
	}

	client := &http.Client{Timeout: hc.timeout}
	resp, err := client.Do(req)
	responseTime := time.Since(startTime)

	if err != nil {
		warehouse.UpdateHealth(false, responseTime)
		return
	}
	defer resp.Body.Close()

	// Consider 2xx status codes as healthy
	isHealthy := resp.StatusCode >= 200 && resp.StatusCode < 300
	warehouse.UpdateHealth(isHealthy, responseTime)
}

// FlipkartProxy implements HTTP proxy with health-aware load balancing
type FlipkartProxy struct {
	loadBalancer *FlipkartLoadBalancer
}

// NewFlipkartProxy creates a new proxy with health-aware load balancing
func NewFlipkartProxy(lb *FlipkartLoadBalancer) *FlipkartProxy {
	return &FlipkartProxy{
		loadBalancer: lb,
	}
}

// ServeHTTP implements http.Handler interface
func (p *FlipkartProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	startTime := time.Now()

	// Get best available warehouse
	warehouse, err := p.loadBalancer.GetBestWarehouse()
	if err != nil {
		log.Printf("❌ No warehouses available: %v", err)
		http.Error(w, "Service Unavailable", http.StatusServiceUnavailable)
		return
	}

	// Create reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(warehouse.URL)

	// Add custom headers
	r.Header.Set("X-Forwarded-Warehouse", warehouse.ID)
	r.Header.Set("X-Forwarded-Zone", warehouse.Zone)
	r.Header.Set("X-Warehouse-Health", warehouse.Health.State)

	// Custom response writer to capture status
	responseWriter := &responseWriterWrapper{
		ResponseWriter: w,
		statusCode:     200,
	}

	// Log request routing
	log.Printf("🔀 Routing request %s %s to warehouse %s (health: %.1f)",
		r.Method, r.URL.Path, warehouse.ID, warehouse.GetHealthScore())

	// Proxy the request
	proxy.ServeHTTP(responseWriter, r)

	// Update warehouse health based on response
	responseTime := time.Since(startTime)
	success := responseWriter.statusCode >= 200 && responseWriter.statusCode < 500
	warehouse.UpdateHealth(success, responseTime)
}

// Stop gracefully shuts down the proxy
func (p *FlipkartProxy) Stop() {
	if p.loadBalancer.healthChecker != nil {
		p.loadBalancer.healthChecker.Stop()
	}
}

// responseWriterWrapper wraps http.ResponseWriter to capture status code
type responseWriterWrapper struct {
	http.ResponseWriter
	statusCode int
}

func (rw *responseWriterWrapper) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

// Example usage and demo
func main() {
	// Create health-aware load balancer
	lb := NewFlipkartLoadBalancer()

	// Add warehouses with different configurations
	warehouses := []*Warehouse{
		NewWarehouse(
			"warehouse-mumbai-central",
			"http://localhost:8081",
			"mumbai",
			map[string]string{"type": "primary", "capacity": "10000"},
		),
		NewWarehouse(
			"warehouse-mumbai-backup",
			"http://localhost:8082",
			"mumbai",
			map[string]string{"type": "backup", "capacity": "5000"},
		),
		NewWarehouse(
			"warehouse-delhi-primary",
			"http://localhost:8083",
			"delhi",
			map[string]string{"type": "primary", "capacity": "8000"},
		),
		NewWarehouse(
			"warehouse-bangalore-primary",
			"http://localhost:8084",
			"bangalore",
			map[string]string{"type": "primary", "capacity": "7000"},
		),
	}

	// Add warehouses to load balancer
	for _, warehouse := range warehouses {
		lb.AddWarehouse(warehouse)
	}

	// Create proxy
	proxy := NewFlipkartProxy(lb)
	defer proxy.Stop()

	// Demo: Show health-aware behavior
	fmt.Println("\n🏭 Flipkart Health-Aware Load Balancer Demo")
	fmt.Println("=============================================")

	fmt.Println("\n1. 🎯 Health-aware warehouse selection:")
	for i := 0; i < 5; i++ {
		warehouse, err := lb.GetBestWarehouse()
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
			continue
		}
		fmt.Printf("   Request %d -> Warehouse: %s (health: %.1f, state: %s)\n",
			i+1, warehouse.ID, warehouse.GetHealthScore(), warehouse.Health.State)
	}

	fmt.Println("\n2. 🌍 Zone-based warehouse selection:")
	mumbaiWarehouses := lb.GetWarehousesByZone("mumbai")
	fmt.Printf("   Mumbai warehouses: %d available\n", len(mumbaiWarehouses))
	for _, wh := range mumbaiWarehouses {
		fmt.Printf("   🏭 %s (health: %.1f)\n", wh.ID, wh.GetHealthScore())
	}

	fmt.Println("\n3. 📊 Comprehensive health status:")
	healthStatus := lb.GetHealthStatus()
	fmt.Printf("   🏭 Total warehouses: %d\n", healthStatus["total_warehouses"])
	fmt.Printf("   💚 Healthy: %d\n", healthStatus["healthy_warehouses"])
	fmt.Printf("   💛 Degraded: %d\n", healthStatus["degraded_warehouses"])
	fmt.Printf("   💔 Failed: %d\n", healthStatus["failed_warehouses"])

	fmt.Println("\n4. 🏭 Warehouse details:")
	warehouseDetails := healthStatus["warehouse_details"].([]map[string]interface{})
	for _, details := range warehouseDetails {
		fmt.Printf("   🏭 %s: health=%.1f, state=%s, circuit=%s\n",
			details["id"], details["health_score"], 
			details["state"], details["circuit_breaker"])
	}

	// Simulate some warehouse failures for demo
	fmt.Println("\n5. 🔧 Simulating warehouse failures:")
	warehouses[1].UpdateHealth(false, 2*time.Second) // Make backup unhealthy
	warehouses[2].UpdateHealth(false, 3*time.Second) // Make Delhi unhealthy

	time.Sleep(1 * time.Second) // Allow health checks to propagate

	fmt.Println("\n6. 🎯 Selection after failures:")
	for i := 0; i < 3; i++ {
		warehouse, err := lb.GetBestWarehouse()
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
			continue
		}
		fmt.Printf("   Request %d -> Warehouse: %s (health: %.1f)\n",
			i+1, warehouse.ID, warehouse.GetHealthScore())
	}

	// Start HTTP server for demo
	fmt.Println("\n🌐 Starting HTTP proxy server on :8080")
	fmt.Println("📝 Test with: curl http://localhost:8080/api/orders")
	fmt.Println("🔍 Health checks running every 15 seconds")
	fmt.Println("🛑 Press Ctrl+C to stop")

	// Health status endpoint
	http.HandleFunc("/health-status", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		status := lb.GetHealthStatus()
		json.NewEncoder(w).Encode(status)
	})

	server := &http.Server{
		Addr:    ":8080",
		Handler: proxy,
	}

	log.Fatal(server.ListenAndServe())
}