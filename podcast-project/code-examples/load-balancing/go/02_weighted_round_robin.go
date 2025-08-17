/*
🇮🇳 Weighted Round Robin Load Balancer - Zomato Cloud Kitchen Style
Different capacity के cloud kitchens को orders distribute करने जैसा

Features:
- Weight-based request distribution
- Dynamic weight adjustment
- Capacity-aware routing
- Zomato cloud kitchen patterns
- Performance monitoring
- Production-ready implementation
- Hindi comments

Author: Agent 5 - Code Developer
Episode: 27 - Load Balancing
Context: Zomato cloud kitchen optimization system
*/

package main

import (
	"context"
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

// CloudKitchen represents a backend server with capacity
type CloudKitchen struct {
	ID               string                // Kitchen ID (e.g., "kitchen-mumbai-001")
	URL              *url.URL              // Kitchen API endpoint
	Weight           int                   // Kitchen capacity weight (1-100)
	CurrentWeight    int                   // Current effective weight
	EffectiveWeight  int                   // Effective weight (reduces on failures)
	IsHealthy        bool                  // Kitchen availability status
	Zone             string                // Geographic zone
	Metadata         map[string]string     // Kitchen metadata
	RequestCount     uint64                // Total requests handled
	SuccessCount     uint64                // Successful requests
	FailureCount     uint64                // Failed requests
	LastChecked      time.Time             // Last health check
	ResponseTime     time.Duration         // Average response time
	mutex            sync.RWMutex          // Thread safety
}

// IsAvailable checks if kitchen is accepting orders
func (ck *CloudKitchen) IsAvailable() bool {
	ck.mutex.RLock()
	defer ck.mutex.RUnlock()
	return ck.IsHealthy && ck.EffectiveWeight > 0
}

// SetHealth updates kitchen health and adjusts weights
func (ck *CloudKitchen) SetHealth(healthy bool) {
	ck.mutex.Lock()
	defer ck.mutex.Unlock()

	ck.IsHealthy = healthy
	ck.LastChecked = time.Now()

	// Adjust effective weight based on health
	if healthy {
		// Gradually restore weight on recovery
		if ck.EffectiveWeight < ck.Weight {
			ck.EffectiveWeight = int(math.Min(float64(ck.EffectiveWeight+1), float64(ck.Weight)))
		}
	} else {
		// Reduce weight on failure
		ck.EffectiveWeight = int(math.Max(0, float64(ck.EffectiveWeight-5)))
	}

	status := "🟢 Available"
	if !healthy {
		status = "🔴 Unavailable"
	}
	log.Printf("🏭 Kitchen %s status: %s (weight: %d->%d)",
		ck.ID, status, ck.Weight, ck.EffectiveWeight)
}

// RecordRequest records request statistics
func (ck *CloudKitchen) RecordRequest(success bool, responseTime time.Duration) {
	ck.mutex.Lock()
	defer ck.mutex.Unlock()

	atomic.AddUint64(&ck.RequestCount, 1)

	if success {
		atomic.AddUint64(&ck.SuccessCount, 1)
		// Increase effective weight on success (up to original weight)
		if ck.EffectiveWeight < ck.Weight {
			ck.EffectiveWeight++
		}
	} else {
		atomic.AddUint64(&ck.FailureCount, 1)
		// Decrease effective weight on failure
		if ck.EffectiveWeight > 0 {
			ck.EffectiveWeight--
		}
	}

	// Update average response time
	ck.ResponseTime = (ck.ResponseTime + responseTime) / 2
}

// GetStats returns kitchen statistics
func (ck *CloudKitchen) GetStats() map[string]interface{} {
	ck.mutex.RLock()
	defer ck.mutex.RUnlock()

	total := atomic.LoadUint64(&ck.RequestCount)
	success := atomic.LoadUint64(&ck.SuccessCount)
	failure := atomic.LoadUint64(&ck.FailureCount)

	successRate := float64(0)
	if total > 0 {
		successRate = float64(success) / float64(total) * 100
	}

	return map[string]interface{}{
		"id":             ck.ID,
		"zone":           ck.Zone,
		"weight":         ck.Weight,
		"effective_weight": ck.EffectiveWeight,
		"is_healthy":     ck.IsHealthy,
		"total_requests": total,
		"success_count":  success,
		"failure_count":  failure,
		"success_rate":   successRate,
		"response_time":  ck.ResponseTime.Milliseconds(),
	}
}

// ZomatoLoadBalancer implements weighted round-robin load balancing
type ZomatoLoadBalancer struct {
	kitchens      []*CloudKitchen // List of cloud kitchens
	totalWeight   int             // Total weight of all kitchens
	mutex         sync.RWMutex    // Thread safety
	lastSelected  int             // Last selected kitchen index
}

// NewZomatoLoadBalancer creates a new weighted load balancer
func NewZomatoLoadBalancer() *ZomatoLoadBalancer {
	return &ZomatoLoadBalancer{
		kitchens:     make([]*CloudKitchen, 0),
		totalWeight:  0,
		lastSelected: -1,
	}
}

// AddKitchen adds a new cloud kitchen to the load balancer
func (lb *ZomatoLoadBalancer) AddKitchen(kitchen *CloudKitchen) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	// Initialize effective weight to match weight
	kitchen.EffectiveWeight = kitchen.Weight

	lb.kitchens = append(lb.kitchens, kitchen)
	lb.recalculateTotalWeight()

	log.Printf("✅ Cloud kitchen added: %s in %s zone (weight: %d)",
		kitchen.ID, kitchen.Zone, kitchen.Weight)
}

// RemoveKitchen removes a kitchen from the load balancer
func (lb *ZomatoLoadBalancer) RemoveKitchen(kitchenID string) error {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for i, kitchen := range lb.kitchens {
		if kitchen.ID == kitchenID {
			lb.kitchens = append(lb.kitchens[:i], lb.kitchens[i+1:]...)
			lb.recalculateTotalWeight()
			log.Printf("🗑️ Cloud kitchen removed: %s", kitchenID)
			return nil
		}
	}

	return fmt.Errorf("kitchen not found: %s", kitchenID)
}

// recalculateTotalWeight recalculates total effective weight
func (lb *ZomatoLoadBalancer) recalculateTotalWeight() {
	lb.totalWeight = 0
	for _, kitchen := range lb.kitchens {
		if kitchen.IsAvailable() {
			lb.totalWeight += kitchen.EffectiveWeight
		}
	}
}

// GetNextKitchen returns the next kitchen using weighted round-robin
func (lb *ZomatoLoadBalancer) GetNextKitchen() (*CloudKitchen, error) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	if len(lb.kitchens) == 0 {
		return nil, errors.New("no kitchens available")
	}

	lb.recalculateTotalWeight()
	if lb.totalWeight == 0 {
		return nil, errors.New("no healthy kitchens available")
	}

	// Weighted round-robin algorithm
	var selected *CloudKitchen
	maxCurrentWeight := -1

	for i, kitchen := range lb.kitchens {
		if !kitchen.IsAvailable() {
			continue
		}

		// Increase current weight by effective weight
		kitchen.CurrentWeight += kitchen.EffectiveWeight

		// Find kitchen with maximum current weight
		if kitchen.CurrentWeight > maxCurrentWeight {
			maxCurrentWeight = kitchen.CurrentWeight
			selected = kitchen
			lb.lastSelected = i
		}
	}

	if selected != nil {
		// Decrease current weight by total weight
		selected.CurrentWeight -= lb.totalWeight

		log.Printf("🎯 Selected kitchen: %s (weight: %d/%d, current: %d)",
			selected.ID, selected.EffectiveWeight, selected.Weight, selected.CurrentWeight)

		return selected, nil
	}

	return nil, errors.New("no suitable kitchen found")
}

// GetKitchenByCapacity returns kitchen based on current load
func (lb *ZomatoLoadBalancer) GetKitchenByCapacity() (*CloudKitchen, error) {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	var bestKitchen *CloudKitchen
	bestScore := float64(-1)

	for _, kitchen := range lb.kitchens {
		if !kitchen.IsAvailable() {
			continue
		}

		// Calculate load score (lower is better)
		total := atomic.LoadUint64(&kitchen.RequestCount)
		loadRatio := float64(total) / float64(kitchen.EffectiveWeight)
		responseScore := float64(kitchen.ResponseTime.Milliseconds())

		// Combined score (weight capacity vs current load)
		score := float64(kitchen.EffectiveWeight) / (loadRatio + responseScore/1000 + 1)

		if score > bestScore {
			bestScore = score
			bestKitchen = kitchen
		}
	}

	if bestKitchen != nil {
		log.Printf("🎯 Selected kitchen by capacity: %s (score: %.2f)",
			bestKitchen.ID, bestScore)
		return bestKitchen, nil
	}

	return nil, errors.New("no available kitchen with capacity")
}

// UpdateKitchenWeights dynamically adjusts weights based on performance
func (lb *ZomatoLoadBalancer) UpdateKitchenWeights() {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	log.Printf("🔄 Updating kitchen weights based on performance...")

	for _, kitchen := range lb.kitchens {
		if !kitchen.IsHealthy {
			continue
		}

		stats := kitchen.GetStats()
		successRate := stats["success_rate"].(float64)
		responseTime := stats["response_time"].(int64)

		// Adjust effective weight based on performance
		performanceMultiplier := 1.0

		// Success rate factor (0.5x to 1.5x)
		if successRate >= 95 {
			performanceMultiplier *= 1.2
		} else if successRate >= 90 {
			performanceMultiplier *= 1.0
		} else if successRate >= 80 {
			performanceMultiplier *= 0.8
		} else {
			performanceMultiplier *= 0.5
		}

		// Response time factor
		if responseTime < 100 {
			performanceMultiplier *= 1.1
		} else if responseTime > 500 {
			performanceMultiplier *= 0.8
		}

		// Apply performance adjustment
		newEffectiveWeight := int(float64(kitchen.Weight) * performanceMultiplier)
		newEffectiveWeight = int(math.Max(1, math.Min(float64(kitchen.Weight*2), float64(newEffectiveWeight))))

		if newEffectiveWeight != kitchen.EffectiveWeight {
			log.Printf("⚖️ Kitchen %s weight: %d -> %d (success: %.1f%%, response: %dms)",
				kitchen.ID, kitchen.EffectiveWeight, newEffectiveWeight, successRate, responseTime)
			kitchen.EffectiveWeight = newEffectiveWeight
		}
	}

	lb.recalculateTotalWeight()
}

// GetLoadBalancingStats returns comprehensive load balancing statistics
func (lb *ZomatoLoadBalancer) GetLoadBalancingStats() map[string]interface{} {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	kitchenStats := make([]map[string]interface{}, 0, len(lb.kitchens))
	totalRequests := uint64(0)
	healthyKitchens := 0

	for _, kitchen := range lb.kitchens {
		stats := kitchen.GetStats()
		kitchenStats = append(kitchenStats, stats)

		if kitchen.IsHealthy {
			healthyKitchens++
		}

		totalRequests += atomic.LoadUint64(&kitchen.RequestCount)
	}

	return map[string]interface{}{
		"total_kitchens":   len(lb.kitchens),
		"healthy_kitchens": healthyKitchens,
		"total_weight":     lb.totalWeight,
		"total_requests":   totalRequests,
		"kitchen_stats":    kitchenStats,
	}
}

// PerformanceMonitor monitors and adjusts kitchen performance
type PerformanceMonitor struct {
	loadBalancer *ZomatoLoadBalancer
	interval     time.Duration
	ctx          context.Context
	cancel       context.CancelFunc
}

// NewPerformanceMonitor creates a new performance monitor
func NewPerformanceMonitor(lb *ZomatoLoadBalancer, interval time.Duration) *PerformanceMonitor {
	ctx, cancel := context.WithCancel(context.Background())
	return &PerformanceMonitor{
		loadBalancer: lb,
		interval:     interval,
		ctx:          ctx,
		cancel:       cancel,
	}
}

// Start begins performance monitoring
func (pm *PerformanceMonitor) Start() {
	go pm.monitorLoop()
	log.Printf("📊 Performance monitor started (interval: %v)", pm.interval)
}

// Stop stops performance monitoring
func (pm *PerformanceMonitor) Stop() {
	pm.cancel()
	log.Printf("🛑 Performance monitor stopped")
}

// monitorLoop performs periodic performance adjustments
func (pm *PerformanceMonitor) monitorLoop() {
	ticker := time.NewTicker(pm.interval)
	defer ticker.Stop()

	for {
		select {
		case <-pm.ctx.Done():
			return
		case <-ticker.C:
			pm.loadBalancer.UpdateKitchenWeights()
		}
	}
}

// ZomatoProxy implements HTTP proxy with weighted load balancing
type ZomatoProxy struct {
	loadBalancer       *ZomatoLoadBalancer
	performanceMonitor *PerformanceMonitor
}

// NewZomatoProxy creates a new proxy with weighted load balancing
func NewZomatoProxy(lb *ZomatoLoadBalancer) *ZomatoProxy {
	proxy := &ZomatoProxy{
		loadBalancer: lb,
	}

	// Start performance monitoring
	proxy.performanceMonitor = NewPerformanceMonitor(lb, 60*time.Second)
	proxy.performanceMonitor.Start()

	return proxy
}

// ServeHTTP implements http.Handler interface
func (p *ZomatoProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	startTime := time.Now()

	// Get next kitchen using weighted algorithm
	kitchen, err := p.loadBalancer.GetNextKitchen()
	if err != nil {
		log.Printf("❌ No kitchens available: %v", err)
		http.Error(w, "Service Unavailable", http.StatusServiceUnavailable)
		return
	}

	// Create reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(kitchen.URL)

	// Add custom headers
	r.Header.Set("X-Forwarded-Kitchen", kitchen.ID)
	r.Header.Set("X-Forwarded-Zone", kitchen.Zone)
	r.Header.Set("X-Kitchen-Weight", fmt.Sprintf("%d", kitchen.EffectiveWeight))

	// Custom response writer to capture status
	responseWriter := &responseWriterWrapper{
		ResponseWriter: w,
		statusCode:     200,
	}

	// Log request routing
	log.Printf("🔀 Routing request %s %s to kitchen %s (weight: %d)",
		r.Method, r.URL.Path, kitchen.ID, kitchen.EffectiveWeight)

	// Proxy the request
	proxy.ServeHTTP(responseWriter, r)

	// Record request statistics
	responseTime := time.Since(startTime)
	success := responseWriter.statusCode >= 200 && responseWriter.statusCode < 400
	kitchen.RecordRequest(success, responseTime)

	log.Printf("📊 Request completed: %s -> %d (%v, success: %t)",
		kitchen.ID, responseWriter.statusCode, responseTime, success)
}

// Stop gracefully shuts down the proxy
func (p *ZomatoProxy) Stop() {
	if p.performanceMonitor != nil {
		p.performanceMonitor.Stop()
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

// mustParseURL parses URL or panics
func mustParseURL(rawURL string) *url.URL {
	url, err := url.Parse(rawURL)
	if err != nil {
		panic(fmt.Sprintf("Invalid URL: %s", rawURL))
	}
	return url
}

// Example usage and demo
func main() {
	// Create weighted load balancer
	lb := NewZomatoLoadBalancer()

	// Add cloud kitchens with different capacities
	kitchens := []*CloudKitchen{
		{
			ID:        "kitchen-mumbai-premium",
			URL:       mustParseURL("http://localhost:8081"),
			Weight:    30, // High capacity kitchen
			IsHealthy: true,
			Zone:      "mumbai",
			Metadata: map[string]string{
				"type":     "premium",
				"capacity": "300-orders/hour",
			},
		},
		{
			ID:        "kitchen-mumbai-standard",
			URL:       mustParseURL("http://localhost:8082"),
			Weight:    20, // Medium capacity kitchen
			IsHealthy: true,
			Zone:      "mumbai",
			Metadata: map[string]string{
				"type":     "standard",
				"capacity": "200-orders/hour",
			},
		},
		{
			ID:        "kitchen-delhi-premium",
			URL:       mustParseURL("http://localhost:8083"),
			Weight:    25, // High capacity kitchen
			IsHealthy: true,
			Zone:      "delhi",
			Metadata: map[string]string{
				"type":     "premium",
				"capacity": "250-orders/hour",
			},
		},
		{
			ID:        "kitchen-bangalore-basic",
			URL:       mustParseURL("http://localhost:8084"),
			Weight:    10, // Low capacity kitchen
			IsHealthy: true,
			Zone:      "bangalore",
			Metadata: map[string]string{
				"type":     "basic",
				"capacity": "100-orders/hour",
			},
		},
	}

	// Add kitchens to load balancer
	for _, kitchen := range kitchens {
		lb.AddKitchen(kitchen)
	}

	// Create proxy
	proxy := NewZomatoProxy(lb)
	defer proxy.Stop()

	// Demo: Show weighted round-robin behavior
	fmt.Println("\n🏭 Zomato Weighted Load Balancer Demo")
	fmt.Println("==================================================")

	fmt.Println("\n1. 🔄 Weighted round-robin kitchen selection:")
	for i := 0; i < 10; i++ {
		kitchen, err := lb.GetNextKitchen()
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
			continue
		}
		fmt.Printf("   Order %d -> Kitchen: %s (weight: %d/%d)\n",
			i+1, kitchen.ID, kitchen.EffectiveWeight, kitchen.Weight)
	}

	fmt.Println("\n2. 📊 Load balancing statistics:")
	stats := lb.GetLoadBalancingStats()
	fmt.Printf("   🏭 Total kitchens: %d\n", stats["total_kitchens"])
	fmt.Printf("   💚 Healthy kitchens: %d\n", stats["healthy_kitchens"])
	fmt.Printf("   ⚖️ Total weight: %d\n", stats["total_weight"])

	fmt.Println("\n3. 🏭 Individual kitchen stats:")
	kitchenStats := stats["kitchen_stats"].([]map[string]interface{})
	for _, kStats := range kitchenStats {
		fmt.Printf("   🍽️ %s: weight=%d, effective=%d, zone=%s\n",
			kStats["id"], kStats["weight"], kStats["effective_weight"], kStats["zone"])
	}

	fmt.Println("\n4. 🎯 Capacity-based selection:")
	for i := 0; i < 3; i++ {
		kitchen, err := lb.GetKitchenByCapacity()
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
			continue
		}
		fmt.Printf("   Capacity selection %d -> Kitchen: %s\n", i+1, kitchen.ID)
	}

	// Start HTTP server for demo
	fmt.Println("\n🌐 Starting HTTP proxy server on :8080")
	fmt.Println("📝 Test with: curl http://localhost:8080/api/orders")
	fmt.Println("📊 Performance monitoring active")
	fmt.Println("🛑 Press Ctrl+C to stop")

	server := &http.Server{
		Addr:    ":8080",
		Handler: proxy,
	}

	log.Fatal(server.ListenAndServe())
}