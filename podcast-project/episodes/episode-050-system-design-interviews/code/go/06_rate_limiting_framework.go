/*
Rate Limiting Framework - Episode 50: System Design Interview Mastery
UPI Transaction Rate Limiter - Mumbai Local Train Crowd Control

Rate Limiting जैसे Mumbai Local में rush hour control है -
Peak time में train frequency badhate हैं, crowd control करते हैं

Author: Hindi Podcast Series
Topic: Distributed Rate Limiting with Multiple Algorithms
*/

package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

// RateLimitAlgorithm - Rate limiting algorithms
type RateLimitAlgorithm int

const (
	TokenBucket RateLimitAlgorithm = iota // Token bucket algorithm
	LeakyBucket                           // Leaky bucket algorithm  
	FixedWindow                           // Fixed time window
	SlidingWindow                         // Sliding window counter
	SlidingWindowLog                      // Sliding window log
)

func (r RateLimitAlgorithm) String() string {
	switch r {
	case TokenBucket:
		return "TokenBucket"
	case LeakyBucket:
		return "LeakyBucket"
	case FixedWindow:
		return "FixedWindow"
	case SlidingWindow:
		return "SlidingWindow"
	case SlidingWindowLog:
		return "SlidingWindowLog"
	default:
		return "Unknown"
	}
}

// RateLimitConfig - Rate limiting configuration
type RateLimitConfig struct {
	Algorithm    RateLimitAlgorithm `json:"algorithm"`
	Limit        int                `json:"limit"`        // Maximum requests
	WindowSize   time.Duration      `json:"window_size"`  // Time window
	BucketSize   int                `json:"bucket_size"`  // Token bucket size
	RefillRate   int                `json:"refill_rate"`  // Token refill rate per second
	Burst        int                `json:"burst"`        // Burst capacity
	Description  string             `json:"description"`  // Human readable description
}

// RateLimitResult - Result of rate limiting check
type RateLimitResult struct {
	Allowed       bool          `json:"allowed"`
	RemainingCalls int          `json:"remaining_calls"`
	ResetTime     time.Time     `json:"reset_time"`
	RetryAfter    time.Duration `json:"retry_after"`
	Algorithm     string        `json:"algorithm"`
}

// RateLimiter interface - Common interface for all rate limiters
type RateLimiter interface {
	CheckLimit(ctx context.Context, key string) *RateLimitResult
	GetStats(key string) map[string]interface{}
	Reset(key string)
	Close()
}

// TokenBucketLimiter - Token bucket rate limiter implementation
type TokenBucketLimiter struct {
	config  RateLimitConfig
	buckets map[string]*tokenBucket
	mutex   sync.RWMutex
}

type tokenBucket struct {
	tokens     float64
	lastRefill time.Time
	mutex      sync.Mutex
}

// NewTokenBucketLimiter - Create new token bucket limiter
func NewTokenBucketLimiter(config RateLimitConfig) *TokenBucketLimiter {
	return &TokenBucketLimiter{
		config:  config,
		buckets: make(map[string]*tokenBucket),
	}
}

func (t *TokenBucketLimiter) CheckLimit(ctx context.Context, key string) *RateLimitResult {
	t.mutex.RLock()
	bucket, exists := t.buckets[key]
	t.mutex.RUnlock()

	if !exists {
		t.mutex.Lock()
		// Double-check pattern
		if bucket, exists = t.buckets[key]; !exists {
			bucket = &tokenBucket{
				tokens:     float64(t.config.BucketSize),
				lastRefill: time.Now(),
			}
			t.buckets[key] = bucket
		}
		t.mutex.Unlock()
	}

	bucket.mutex.Lock()
	defer bucket.mutex.Unlock()

	now := time.Now()
	elapsed := now.Sub(bucket.lastRefill).Seconds()

	// Refill tokens based on elapsed time
	tokensToAdd := elapsed * float64(t.config.RefillRate)
	bucket.tokens = math.Min(bucket.tokens+tokensToAdd, float64(t.config.BucketSize))
	bucket.lastRefill = now

	result := &RateLimitResult{
		Algorithm: t.config.Algorithm.String(),
	}

	if bucket.tokens >= 1.0 {
		bucket.tokens--
		result.Allowed = true
		result.RemainingCalls = int(bucket.tokens)
	} else {
		result.Allowed = false
		result.RemainingCalls = 0
		result.RetryAfter = time.Duration((1.0-bucket.tokens)/float64(t.config.RefillRate)) * time.Second
	}

	return result
}

func (t *TokenBucketLimiter) GetStats(key string) map[string]interface{} {
	t.mutex.RLock()
	defer t.mutex.RUnlock()

	bucket, exists := t.buckets[key]
	if !exists {
		return map[string]interface{}{
			"exists": false,
		}
	}

	bucket.mutex.Lock()
	defer bucket.mutex.Unlock()

	return map[string]interface{}{
		"exists":           true,
		"current_tokens":   bucket.tokens,
		"bucket_size":      t.config.BucketSize,
		"refill_rate":      t.config.RefillRate,
		"last_refill":      bucket.lastRefill,
		"utilization_pct":  (1.0 - bucket.tokens/float64(t.config.BucketSize)) * 100,
	}
}

func (t *TokenBucketLimiter) Reset(key string) {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	delete(t.buckets, key)
}

func (t *TokenBucketLimiter) Close() {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	t.buckets = make(map[string]*tokenBucket)
}

// FixedWindowLimiter - Fixed window rate limiter
type FixedWindowLimiter struct {
	config  RateLimitConfig
	windows map[string]*fixedWindow
	mutex   sync.RWMutex
}

type fixedWindow struct {
	count      int
	windowStart time.Time
	mutex      sync.Mutex
}

func NewFixedWindowLimiter(config RateLimitConfig) *FixedWindowLimiter {
	return &FixedWindowLimiter{
		config:  config,
		windows: make(map[string]*fixedWindow),
	}
}

func (f *FixedWindowLimiter) CheckLimit(ctx context.Context, key string) *RateLimitResult {
	f.mutex.RLock()
	window, exists := f.windows[key]
	f.mutex.RUnlock()

	if !exists {
		f.mutex.Lock()
		if window, exists = f.windows[key]; !exists {
			window = &fixedWindow{
				count:       0,
				windowStart: time.Now(),
			}
			f.windows[key] = window
		}
		f.mutex.Unlock()
	}

	window.mutex.Lock()
	defer window.mutex.Unlock()

	now := time.Now()
	
	// Check if we need a new window
	if now.Sub(window.windowStart) >= f.config.WindowSize {
		window.count = 0
		window.windowStart = now
	}

	result := &RateLimitResult{
		Algorithm: f.config.Algorithm.String(),
		ResetTime: window.windowStart.Add(f.config.WindowSize),
	}

	if window.count < f.config.Limit {
		window.count++
		result.Allowed = true
		result.RemainingCalls = f.config.Limit - window.count
	} else {
		result.Allowed = false
		result.RemainingCalls = 0
		result.RetryAfter = window.windowStart.Add(f.config.WindowSize).Sub(now)
	}

	return result
}

func (f *FixedWindowLimiter) GetStats(key string) map[string]interface{} {
	f.mutex.RLock()
	defer f.mutex.RUnlock()

	window, exists := f.windows[key]
	if !exists {
		return map[string]interface{}{"exists": false}
	}

	window.mutex.Lock()
	defer window.mutex.Unlock()

	return map[string]interface{}{
		"exists":           true,
		"current_count":    window.count,
		"limit":           f.config.Limit,
		"window_start":    window.windowStart,
		"utilization_pct": float64(window.count) / float64(f.config.Limit) * 100,
	}
}

func (f *FixedWindowLimiter) Reset(key string) {
	f.mutex.Lock()
	defer f.mutex.Unlock()
	delete(f.windows, key)
}

func (f *FixedWindowLimiter) Close() {
	f.mutex.Lock()
	defer f.mutex.Unlock()
	f.windows = make(map[string]*fixedWindow)
}

// SlidingWindowLimiter - Sliding window counter limiter
type SlidingWindowLimiter struct {
	config  RateLimitConfig
	windows map[string]*slidingWindow
	mutex   sync.RWMutex
}

type slidingWindow struct {
	requests []time.Time
	mutex    sync.Mutex
}

func NewSlidingWindowLimiter(config RateLimitConfig) *SlidingWindowLimiter {
	return &SlidingWindowLimiter{
		config:  config,
		windows: make(map[string]*slidingWindow),
	}
}

func (s *SlidingWindowLimiter) CheckLimit(ctx context.Context, key string) *RateLimitResult {
	s.mutex.RLock()
	window, exists := s.windows[key]
	s.mutex.RUnlock()

	if !exists {
		s.mutex.Lock()
		if window, exists = s.windows[key]; !exists {
			window = &slidingWindow{
				requests: make([]time.Time, 0),
			}
			s.windows[key] = window
		}
		s.mutex.Unlock()
	}

	window.mutex.Lock()
	defer window.mutex.Unlock()

	now := time.Now()
	cutoff := now.Add(-s.config.WindowSize)

	// Remove old requests outside the window
	validRequests := make([]time.Time, 0)
	for _, reqTime := range window.requests {
		if reqTime.After(cutoff) {
			validRequests = append(validRequests, reqTime)
		}
	}
	window.requests = validRequests

	result := &RateLimitResult{
		Algorithm: s.config.Algorithm.String(),
	}

	if len(window.requests) < s.config.Limit {
		window.requests = append(window.requests, now)
		result.Allowed = true
		result.RemainingCalls = s.config.Limit - len(window.requests)
	} else {
		result.Allowed = false
		result.RemainingCalls = 0
		// Calculate when the oldest request will expire
		if len(window.requests) > 0 {
			result.RetryAfter = window.requests[0].Add(s.config.WindowSize).Sub(now)
		}
	}

	return result
}

func (s *SlidingWindowLimiter) GetStats(key string) map[string]interface{} {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	window, exists := s.windows[key]
	if !exists {
		return map[string]interface{}{"exists": false}
	}

	window.mutex.Lock()
	defer window.mutex.Unlock()

	return map[string]interface{}{
		"exists":           true,
		"request_count":    len(window.requests),
		"limit":           s.config.Limit,
		"window_size":     s.config.WindowSize,
		"utilization_pct": float64(len(window.requests)) / float64(s.config.Limit) * 100,
	}
}

func (s *SlidingWindowLimiter) Reset(key string) {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	delete(s.windows, key)
}

func (s *SlidingWindowLimiter) Close() {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.windows = make(map[string]*slidingWindow)
}

// DistributedRateLimitManager - Central rate limiting manager
type DistributedRateLimitManager struct {
	limiters map[string]RateLimiter
	configs  map[string]RateLimitConfig
	mutex    sync.RWMutex
	
	// Metrics
	totalRequests   int64
	allowedRequests int64
	blockedRequests int64
}

// NewDistributedRateLimitManager - Create new rate limit manager
func NewDistributedRateLimitManager() *DistributedRateLimitManager {
	return &DistributedRateLimitManager{
		limiters: make(map[string]RateLimiter),
		configs:  make(map[string]RateLimitConfig),
	}
}

// AddRateLimiter - Add rate limiter for a specific service/endpoint
func (d *DistributedRateLimitManager) AddRateLimiter(service string, config RateLimitConfig) {
	d.mutex.Lock()
	defer d.mutex.Unlock()

	var limiter RateLimiter
	switch config.Algorithm {
	case TokenBucket:
		limiter = NewTokenBucketLimiter(config)
	case FixedWindow:
		limiter = NewFixedWindowLimiter(config)
	case SlidingWindow:
		limiter = NewSlidingWindowLimiter(config)
	default:
		log.Printf("Unknown algorithm: %v, defaulting to TokenBucket", config.Algorithm)
		limiter = NewTokenBucketLimiter(config)
	}

	d.limiters[service] = limiter
	d.configs[service] = config

	log.Printf("✅ Rate limiter added for service '%s' with %s algorithm", service, config.Algorithm)
}

// CheckRateLimit - Check rate limit for a service and key
func (d *DistributedRateLimitManager) CheckRateLimit(service, key string) *RateLimitResult {
	d.mutex.RLock()
	limiter, exists := d.limiters[service]
	d.mutex.RUnlock()

	if !exists {
		return &RateLimitResult{
			Allowed:       false,
			RemainingCalls: 0,
			Algorithm:     "NotConfigured",
		}
	}

	d.totalRequests++
	
	result := limiter.CheckLimit(context.Background(), key)
	if result.Allowed {
		d.allowedRequests++
	} else {
		d.blockedRequests++
	}

	return result
}

// GetServiceStats - Get statistics for a service
func (d *DistributedRateLimitManager) GetServiceStats(service string) map[string]interface{} {
	d.mutex.RLock()
	defer d.mutex.RUnlock()

	limiter, exists := d.limiters[service]
	config, configExists := d.configs[service]

	if !exists || !configExists {
		return map[string]interface{}{
			"service": service,
			"exists":  false,
		}
	}

	return map[string]interface{}{
		"service":     service,
		"exists":      true,
		"algorithm":   config.Algorithm.String(),
		"limit":       config.Limit,
		"window_size": config.WindowSize,
		"description": config.Description,
	}
}

// GetGlobalStats - Get global rate limiting statistics
func (d *DistributedRateLimitManager) GetGlobalStats() map[string]interface{} {
	d.mutex.RLock()
	defer d.mutex.RUnlock()

	blockingRate := float64(0)
	if d.totalRequests > 0 {
		blockingRate = float64(d.blockedRequests) / float64(d.totalRequests) * 100
	}

	return map[string]interface{}{
		"total_services":    len(d.limiters),
		"total_requests":    d.totalRequests,
		"allowed_requests":  d.allowedRequests,
		"blocked_requests":  d.blockedRequests,
		"blocking_rate_pct": blockingRate,
		"active_algorithms": d.getActiveAlgorithms(),
	}
}

func (d *DistributedRateLimitManager) getActiveAlgorithms() []string {
	algorithms := make(map[string]bool)
	for _, config := range d.configs {
		algorithms[config.Algorithm.String()] = true
	}

	result := make([]string, 0, len(algorithms))
	for alg := range algorithms {
		result = append(result, alg)
	}
	return result
}

// HTTP Middleware for rate limiting
func (d *DistributedRateLimitManager) RateLimitMiddleware(service string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Use client IP as key (in production, use user ID or API key)
			clientKey := r.RemoteAddr
			if forwardedFor := r.Header.Get("X-Forwarded-For"); forwardedFor != "" {
				clientKey = forwardedFor
			}

			result := d.CheckRateLimit(service, clientKey)

			// Add rate limit headers
			w.Header().Set("X-RateLimit-Algorithm", result.Algorithm)
			w.Header().Set("X-RateLimit-Remaining", strconv.Itoa(result.RemainingCalls))
			
			if !result.ResetTime.IsZero() {
				w.Header().Set("X-RateLimit-Reset", strconv.FormatInt(result.ResetTime.Unix(), 10))
			}

			if !result.Allowed {
				w.Header().Set("Retry-After", strconv.FormatInt(int64(result.RetryAfter.Seconds()), 10))
				w.WriteHeader(http.StatusTooManyRequests)
				w.Write([]byte(fmt.Sprintf(`{"error": "Rate limit exceeded", "retry_after": %d}`, 
					int64(result.RetryAfter.Seconds()))))
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// Demonstrate UPI Payment Rate Limiting
func demonstrateUPIRateLimiting() {
	fmt.Println("💰 UPI Payment Rate Limiting Demo")
	fmt.Println("=" + strings.Repeat("=", 50))

	manager := NewDistributedRateLimitManager()

	// Configure rate limits for different UPI operations
	upiConfigs := map[string]RateLimitConfig{
		"upi_payment": {
			Algorithm:   TokenBucket,
			Limit:       10,
			BucketSize:  10,
			RefillRate:  2, // 2 tokens per second
			WindowSize:  time.Minute,
			Description: "UPI payment transactions - 10 per minute with burst",
		},
		"upi_balance_check": {
			Algorithm:   FixedWindow,
			Limit:       30,
			WindowSize:  time.Minute,
			Description: "UPI balance inquiry - 30 per minute",
		},
		"upi_transaction_history": {
			Algorithm:   SlidingWindow,
			Limit:       20,
			WindowSize:  time.Minute,
			Description: "UPI transaction history - 20 per minute sliding",
		},
	}

	// Add rate limiters
	for service, config := range upiConfigs {
		manager.AddRateLimiter(service, config)
	}

	// Simulate UPI users from Mumbai
	users := []string{
		"user_mumbai_001@paytm",
		"user_mumbai_002@phonepe", 
		"user_mumbai_003@gpay",
		"user_mumbai_004@paytm",
	}

	fmt.Println("\n📱 Simulating UPI transactions from Mumbai users...")

	// Test different scenarios
	scenarios := []struct {
		service string
		user    string
		count   int
		delay   time.Duration
	}{
		{"upi_payment", users[0], 15, 100 * time.Millisecond},        // Exceed limit
		{"upi_balance_check", users[1], 25, 50 * time.Millisecond},   // Within limit  
		{"upi_transaction_history", users[2], 25, 200 * time.Millisecond}, // Test sliding window
	}

	for _, scenario := range scenarios {
		fmt.Printf("\n🧪 Testing %s for %s (%d requests):\n", 
			scenario.service, scenario.user, scenario.count)
		
		allowedCount := 0
		blockedCount := 0

		for i := 0; i < scenario.count; i++ {
			result := manager.CheckRateLimit(scenario.service, scenario.user)
			
			if result.Allowed {
				allowedCount++
				fmt.Printf("✅ Request %d: Allowed (Remaining: %d)\n", 
					i+1, result.RemainingCalls)
			} else {
				blockedCount++
				fmt.Printf("❌ Request %d: Blocked (Retry after: %.2fs)\n", 
					i+1, result.RetryAfter.Seconds())
			}
			
			time.Sleep(scenario.delay)
		}

		fmt.Printf("📊 Summary: %d allowed, %d blocked\n", allowedCount, blockedCount)
	}

	// Show global statistics
	fmt.Println("\n📊 Global Rate Limiting Statistics:")
	globalStats := manager.GetGlobalStats()
	fmt.Printf("   Total Services: %v\n", globalStats["total_services"])
	fmt.Printf("   Total Requests: %v\n", globalStats["total_requests"])
	fmt.Printf("   Allowed Requests: %v\n", globalStats["allowed_requests"])
	fmt.Printf("   Blocked Requests: %v\n", globalStats["blocked_requests"])
	fmt.Printf("   Blocking Rate: %.2f%%\n", globalStats["blocking_rate_pct"])
	fmt.Printf("   Active Algorithms: %v\n", globalStats["active_algorithms"])
}

// Demonstrate Mumbai Local Train API Rate Limiting
func demonstrateMumbaiLocalTrainAPI() {
	fmt.Println("\n🚂 Mumbai Local Train API Rate Limiting Demo")
	fmt.Println("=" + strings.Repeat("=", 60))

	manager := NewDistributedRateLimitManager()

	// Configure rate limits for train API endpoints
	trainConfigs := map[string]RateLimitConfig{
		"train_schedule": {
			Algorithm:   TokenBucket,
			Limit:       100,
			BucketSize:  50,
			RefillRate:  20, // 20 requests per second
			WindowSize:  time.Minute,
			Description: "Train schedule API - High frequency for mobile apps",
		},
		"seat_booking": {
			Algorithm:   FixedWindow,
			Limit:       5,
			WindowSize:  time.Minute,
			Description: "Seat booking API - Limited to prevent abuse",
		},
		"train_status": {
			Algorithm:   SlidingWindow,
			Limit:       200,
			WindowSize:  time.Minute,
			Description: "Live train status - High volume during peak hours",
		},
	}

	// Add rate limiters
	for service, config := range trainConfigs {
		manager.AddRateLimiter(service, config)
	}

	// Simulate mobile app usage during Mumbai rush hour
	fmt.Println("\n📱 Simulating Mumbai rush hour API usage...")

	rushHourApps := []string{
		"mumbai_local_app_001",
		"irctc_mobile_002", 
		"trainman_app_003",
		"where_is_my_train_004",
	}

	// High frequency train schedule requests (typical during rush)
	fmt.Println("\n🚊 Testing train schedule API during rush hour:")
	for i := 0; i < 60; i++ {
		app := rushHourApps[i%len(rushHourApps)]
		result := manager.CheckRateLimit("train_schedule", app)
		
		if i < 10 || !result.Allowed {
			status := "✅ Allowed"
			if !result.Allowed {
				status = "❌ Blocked"
			}
			fmt.Printf("%s Request %d from %s (Remaining: %d)\n", 
				status, i+1, app, result.RemainingCalls)
		}
		
		time.Sleep(50 * time.Millisecond) // High frequency
	}

	// Test seat booking (should be limited)
	fmt.Println("\n🎫 Testing seat booking API (strict limits):")
	for i := 0; i < 10; i++ {
		result := manager.CheckRateLimit("seat_booking", "user_booking_001")
		
		status := "✅ Allowed"
		if !result.Allowed {
			status = fmt.Sprintf("❌ Blocked (Retry: %.1fs)", result.RetryAfter.Seconds())
		}
		fmt.Printf("%s Booking attempt %d (Remaining: %d)\n", 
			status, i+1, result.RemainingCalls)
		
		time.Sleep(10 * time.Second / 10) // 1 request per second
	}

	// Show service statistics
	fmt.Println("\n📊 Mumbai Train API Statistics:")
	for service := range trainConfigs {
		stats := manager.GetServiceStats(service)
		fmt.Printf("   %s: %s algorithm, Limit: %v\n", 
			service, stats["algorithm"], stats["limit"])
	}
}

func main() {
	// Run UPI payment rate limiting demo
	demonstrateUPIRateLimiting()
	
	fmt.Println("\n" + strings.Repeat("=", 80))
	
	// Run Mumbai Local Train API demo
	demonstrateMumbaiLocalTrainAPI()
	
	fmt.Println("\n" + strings.Repeat("=", 80))
	fmt.Println("✅ Rate Limiting Framework Demo Complete!")
	fmt.Println("📚 Key Features Demonstrated:")
	fmt.Println("   • Token Bucket - Burst handling with steady refill")
	fmt.Println("   • Fixed Window - Simple time-based limiting")
	fmt.Println("   • Sliding Window - Smooth rate limiting")
	fmt.Println("   • Distributed management - Multiple services")
	fmt.Println("   • HTTP middleware integration")
	fmt.Println("   • Comprehensive metrics and monitoring")
	fmt.Println("   • Production-ready for Mumbai scale operations")
}