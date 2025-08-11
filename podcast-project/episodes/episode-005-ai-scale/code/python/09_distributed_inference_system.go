// Distributed Inference System for High-Scale Indian Applications
// Episode 5: Code Example 9
//
// Production-ready distributed inference system in Go
// Supporting high-scale Indian applications like Paytm, Flipkart scale
//
// Author: Code Developer Agent
// Context: Million+ requests/day inference for Indian applications

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// InferenceRequest represents a request for model inference
type InferenceRequest struct {
	Text       string            `json:"text" binding:"required"`
	ModelID    string            `json:"model_id"`
	UserID     string            `json:"user_id"`
	Language   string            `json:"language"`
	Region     string            `json:"region"`
	Metadata   map[string]string `json:"metadata"`
	RequestID  string            `json:"request_id"`
	Timestamp  int64             `json:"timestamp"`
	Priority   int               `json:"priority"` // 1=high, 2=medium, 3=low
}

// InferenceResponse represents the response from model inference
type InferenceResponse struct {
	RequestID        string                 `json:"request_id"`
	Prediction       interface{}            `json:"prediction"`
	Confidence       float64                `json:"confidence"`
	ModelVersion     string                 `json:"model_version"`
	ProcessingTimeMS int64                  `json:"processing_time_ms"`
	CostINR          float64                `json:"cost_inr"`
	ServerID         string                 `json:"server_id"`
	CacheHit         bool                   `json:"cache_hit"`
	Metadata         map[string]interface{} `json:"metadata"`
	Timestamp        int64                  `json:"timestamp"`
}

// ModelInstance represents a loaded model instance
type ModelInstance struct {
	ID              string    `json:"id"`
	Version         string    `json:"version"`
	Language        string    `json:"language"`
	LoadTime        time.Time `json:"load_time"`
	RequestCount    int64     `json:"request_count"`
	AverageLatency  float64   `json:"average_latency_ms"`
	SuccessRate     float64   `json:"success_rate"`
	MemoryUsageMB   float64   `json:"memory_usage_mb"`
	CostPerRequest  float64   `json:"cost_per_request_inr"`
	SupportedRegions []string `json:"supported_regions"`
}

// LoadBalancer handles request distribution across model instances
type LoadBalancer struct {
	instances    []*ModelInstance
	currentIndex int64
	mutex        sync.RWMutex
	strategy     string // "round_robin", "least_connections", "weighted"
}

// CacheManager handles response caching with Redis
type CacheManager struct {
	client     *redis.Client
	defaultTTL time.Duration
	hitCount   int64
	missCount  int64
}

// RateLimiter handles rate limiting for different user tiers
type RateLimiter struct {
	limits map[string]int // requests per minute by user tier
	usage  map[string]*UserUsage
	mutex  sync.RWMutex
}

// UserUsage tracks usage per user
type UserUsage struct {
	Count     int
	ResetTime time.Time
	Tier      string // "free", "basic", "premium", "enterprise"
}

// DistributedInferenceSystem is the main system orchestrator
type DistributedInferenceSystem struct {
	loadBalancer    *LoadBalancer
	cacheManager    *CacheManager
	rateLimiter     *RateLimiter
	serverID        string
	requestCounter  int64
	errorCounter    int64
	totalCostINR    float64
	startTime       time.Time
	healthChecker   *HealthChecker
	metricsRegistry *prometheus.Registry
}

// HealthChecker monitors system health
type HealthChecker struct {
	isHealthy      bool
	lastHealthTime time.Time
	mutex          sync.RWMutex
}

// Prometheus metrics for monitoring
var (
	requestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "inference_requests_total",
			Help: "Total number of inference requests",
		},
		[]string{"model_id", "language", "region", "status"},
	)

	requestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "inference_request_duration_seconds",
			Help:    "Request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"model_id", "language"},
	)

	cacheHitRate = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "cache_hit_rate",
			Help: "Cache hit rate percentage",
		},
		[]string{"cache_type"},
	)

	activeConnections = prometheus.NewGauge(
		prometheus.GaugeOpts{
			Name: "active_connections",
			Help: "Number of active connections",
		},
	)

	costPerRequest = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name: "cost_per_request_inr",
			Help: "Cost per request in INR",
		},
	)
)

// NewDistributedInferenceSystem creates a new inference system
func NewDistributedInferenceSystem() *DistributedInferenceSystem {
	// Initialize Redis client
	rdb := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "",
		DB:       0,
	})

	// Initialize components
	cacheManager := &CacheManager{
		client:     rdb,
		defaultTTL: 10 * time.Minute,
	}

	rateLimiter := &RateLimiter{
		limits: map[string]int{
			"free":       100,   // 100 requests/minute
			"basic":      1000,  // 1000 requests/minute
			"premium":    10000, // 10000 requests/minute
			"enterprise": 50000, // 50000 requests/minute
		},
		usage: make(map[string]*UserUsage),
	}

	loadBalancer := &LoadBalancer{
		strategy: "round_robin",
	}

	// Initialize with sample model instances
	loadBalancer.instances = []*ModelInstance{
		{
			ID:               "sentiment-hindi-v1",
			Version:          "1.2.0",
			Language:         "hi",
			LoadTime:         time.Now(),
			CostPerRequest:   0.05, // ₹0.05 per request
			SupportedRegions: []string{"north", "west", "central"},
		},
		{
			ID:               "sentiment-english-v1",
			Version:          "1.1.0",
			Language:         "en",
			LoadTime:         time.Now(),
			CostPerRequest:   0.03, // ₹0.03 per request
			SupportedRegions: []string{"all"},
		},
		{
			ID:               "translation-indic-v2",
			Version:          "2.0.0",
			Language:         "multi",
			LoadTime:         time.Now(),
			CostPerRequest:   0.10, // ₹0.10 per request
			SupportedRegions: []string{"all"},
		},
	}

	healthChecker := &HealthChecker{
		isHealthy:      true,
		lastHealthTime: time.Now(),
	}

	// Create metrics registry
	registry := prometheus.NewRegistry()
	registry.MustRegister(requestsTotal, requestDuration, cacheHitRate, activeConnections, costPerRequest)

	return &DistributedInferenceSystem{
		loadBalancer:    loadBalancer,
		cacheManager:    cacheManager,
		rateLimiter:     rateLimiter,
		serverID:        fmt.Sprintf("server-%d", rand.Intn(1000)),
		startTime:       time.Now(),
		healthChecker:   healthChecker,
		metricsRegistry: registry,
	}
}

// ProcessInference handles a single inference request
func (d *DistributedInferenceSystem) ProcessInference(ctx context.Context, req *InferenceRequest) (*InferenceResponse, error) {
	startTime := time.Now()
	atomic.AddInt64(&d.requestCounter, 1)

	// Check rate limiting
	if !d.rateLimiter.CheckRateLimit(req.UserID) {
		atomic.AddInt64(&d.errorCounter, 1)
		requestsTotal.WithLabelValues(req.ModelID, req.Language, req.Region, "rate_limited").Inc()
		return nil, fmt.Errorf("rate limit exceeded for user %s", req.UserID)
	}

	// Check cache first
	cacheKey := d.generateCacheKey(req)
	if cachedResponse, found := d.cacheManager.Get(ctx, cacheKey); found {
		atomic.AddInt64(&d.cacheManager.hitCount, 1)
		response := cachedResponse.(*InferenceResponse)
		response.CacheHit = true
		response.ServerID = d.serverID
		response.Timestamp = time.Now().Unix()
		
		cacheHitRate.WithLabelValues("inference").Set(d.cacheManager.GetHitRate())
		requestsTotal.WithLabelValues(req.ModelID, req.Language, req.Region, "cache_hit").Inc()
		
		return response, nil
	}

	atomic.AddInt64(&d.cacheManager.missCount, 1)

	// Select model instance using load balancer
	instance, err := d.loadBalancer.SelectInstance(req)
	if err != nil {
		atomic.AddInt64(&d.errorCounter, 1)
		requestsTotal.WithLabelValues(req.ModelID, req.Language, req.Region, "no_instance").Inc()
		return nil, fmt.Errorf("no available model instance: %v", err)
	}

	// Simulate model inference (in production, this would call actual model)
	prediction, confidence := d.simulateInference(req, instance)

	processingTime := time.Since(startTime).Milliseconds()
	cost := instance.CostPerRequest

	// Update instance metrics
	atomic.AddInt64(&instance.RequestCount, 1)
	d.totalCostINR += cost

	// Create response
	response := &InferenceResponse{
		RequestID:        req.RequestID,
		Prediction:       prediction,
		Confidence:       confidence,
		ModelVersion:     instance.Version,
		ProcessingTimeMS: processingTime,
		CostINR:          cost,
		ServerID:         d.serverID,
		CacheHit:         false,
		Metadata: map[string]interface{}{
			"model_id":        instance.ID,
			"language":        instance.Language,
			"server_region":   "india-west", // Mumbai region
			"processing_node": d.serverID,
		},
		Timestamp: time.Now().Unix(),
	}

	// Cache the response
	d.cacheManager.Set(ctx, cacheKey, response, d.cacheManager.defaultTTL)

	// Update metrics
	requestsTotal.WithLabelValues(req.ModelID, req.Language, req.Region, "success").Inc()
	requestDuration.WithLabelValues(req.ModelID, req.Language).Observe(float64(processingTime) / 1000)
	costPerRequest.Observe(cost)
	cacheHitRate.WithLabelValues("inference").Set(d.cacheManager.GetHitRate())

	log.Printf("Processed request %s: %dms, ₹%.4f, model=%s", 
		req.RequestID, processingTime, cost, instance.ID)

	return response, nil
}

// simulateInference simulates model inference with Indian context
func (d *DistributedInferenceSystem) simulateInference(req *InferenceRequest, instance *ModelInstance) (interface{}, float64) {
	// Simulate processing delay based on text length and model complexity
	baseDelay := time.Duration(len(req.Text)/10+10) * time.Millisecond
	
	// Add variability for realistic simulation
	jitter := time.Duration(rand.Intn(50)) * time.Millisecond
	time.Sleep(baseDelay + jitter)

	// Generate mock predictions based on model type
	if instance.ID == "sentiment-hindi-v1" || instance.ID == "sentiment-english-v1" {
		sentiments := []string{"positive", "negative", "neutral"}
		prediction := sentiments[rand.Intn(len(sentiments))]
		confidence := 0.7 + rand.Float64()*0.3 // 0.7-1.0 confidence
		
		return map[string]interface{}{
			"sentiment": prediction,
			"scores": map[string]float64{
				"positive": rand.Float64(),
				"negative": rand.Float64(),
				"neutral":  rand.Float64(),
			},
			"language_detected": req.Language,
		}, confidence
		
	} else if instance.ID == "translation-indic-v2" {
		// Mock translation
		translations := map[string]string{
			"hi": "यह एक अनुवाद का उदाहरण है",
			"en": "This is a translation example",
			"ta": "இது ஒரு மொழிபெயர்ப்பு உதாரணம்",
		}
		
		targetLang := req.Metadata["target_language"]
		if targetLang == "" {
			targetLang = "en"
		}
		
		return map[string]interface{}{
			"translated_text":   translations[targetLang],
			"source_language":   req.Language,
			"target_language":   targetLang,
			"translation_score": 0.92,
		}, 0.92
	}

	// Default prediction
	return map[string]interface{}{
		"result": "processed",
		"input_length": len(req.Text),
	}, 0.8
}

// generateCacheKey creates a cache key for the request
func (d *DistributedInferenceSystem) generateCacheKey(req *InferenceRequest) string {
	key := fmt.Sprintf("%s:%s:%s:%s", req.ModelID, req.Language, req.Text, req.Region)
	return fmt.Sprintf("inference:%x", key) // Use hash for clean keys
}

// SelectInstance selects best available model instance
func (lb *LoadBalancer) SelectInstance(req *InferenceRequest) (*ModelInstance, error) {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	if len(lb.instances) == 0 {
		return nil, fmt.Errorf("no available instances")
	}

	// Filter instances by language and region if specified
	var candidates []*ModelInstance
	for _, instance := range lb.instances {
		if req.ModelID != "" && instance.ID != req.ModelID {
			continue
		}
		
		if req.Language != "" && instance.Language != "multi" && instance.Language != req.Language {
			continue
		}
		
		// Check regional support
		if req.Region != "" {
			supported := false
			for _, region := range instance.SupportedRegions {
				if region == "all" || region == req.Region {
					supported = true
					break
				}
			}
			if !supported {
				continue
			}
		}
		
		candidates = append(candidates, instance)
	}

	if len(candidates) == 0 {
		return nil, fmt.Errorf("no suitable instances found for request")
	}

	// Round-robin selection
	index := atomic.AddInt64(&lb.currentIndex, 1) % int64(len(candidates))
	return candidates[index], nil
}

// CheckRateLimit checks if user is within rate limits
func (rl *RateLimiter) CheckRateLimit(userID string) bool {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()

	now := time.Now()
	usage, exists := rl.usage[userID]
	
	if !exists {
		// New user, default to basic tier
		usage = &UserUsage{
			Count:     1,
			ResetTime: now.Add(time.Minute),
			Tier:      "basic",
		}
		rl.usage[userID] = usage
		return true
	}

	// Reset counter if time window expired
	if now.After(usage.ResetTime) {
		usage.Count = 1
		usage.ResetTime = now.Add(time.Minute)
		return true
	}

	// Check against tier limit
	limit := rl.limits[usage.Tier]
	if usage.Count >= limit {
		return false // Rate limit exceeded
	}

	usage.Count++
	return true
}

// Cache management methods
func (cm *CacheManager) Get(ctx context.Context, key string) (interface{}, bool) {
	val, err := cm.client.Get(ctx, key).Result()
	if err != nil {
		return nil, false
	}

	var response InferenceResponse
	err = json.Unmarshal([]byte(val), &response)
	if err != nil {
		return nil, false
	}

	return &response, true
}

func (cm *CacheManager) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	jsonValue, err := json.Marshal(value)
	if err != nil {
		return err
	}

	return cm.client.Set(ctx, key, jsonValue, ttl).Err()
}

func (cm *CacheManager) GetHitRate() float64 {
	total := cm.hitCount + cm.missCount
	if total == 0 {
		return 0
	}
	return float64(cm.hitCount) / float64(total) * 100
}

// Health checking
func (hc *HealthChecker) CheckHealth() bool {
	hc.mutex.Lock()
	defer hc.mutex.Unlock()
	
	// Simple health check - in production, check dependencies
	hc.lastHealthTime = time.Now()
	hc.isHealthy = true // Simulate healthy state
	
	return hc.isHealthy
}

// HTTP handlers
func (d *DistributedInferenceSystem) setupRoutes() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(gin.Logger(), gin.Recovery())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		healthy := d.healthChecker.CheckHealth()
		status := "healthy"
		if !healthy {
			status = "unhealthy"
			c.Status(http.StatusServiceUnavailable)
		}

		c.JSON(http.StatusOK, gin.H{
			"status":           status,
			"server_id":        d.serverID,
			"uptime_seconds":   int(time.Since(d.startTime).Seconds()),
			"total_requests":   atomic.LoadInt64(&d.requestCounter),
			"total_errors":     atomic.LoadInt64(&d.errorCounter),
			"total_cost_inr":   fmt.Sprintf("₹%.2f", d.totalCostINR),
			"cache_hit_rate":   fmt.Sprintf("%.1f%%", d.cacheManager.GetHitRate()),
			"active_instances": len(d.loadBalancer.instances),
		})
	})

	// Inference endpoint
	router.POST("/inference", func(c *gin.Context) {
		var req InferenceRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Generate request ID if not provided
		if req.RequestID == "" {
			req.RequestID = fmt.Sprintf("req_%d_%d", time.Now().UnixNano(), rand.Intn(1000))
		}

		// Set timestamp
		req.Timestamp = time.Now().Unix()

		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		response, err := d.ProcessInference(ctx, &req)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error":      err.Error(),
				"request_id": req.RequestID,
				"timestamp":  time.Now().Unix(),
			})
			return
		}

		c.JSON(http.StatusOK, response)
	})

	// Batch inference endpoint
	router.POST("/inference/batch", func(c *gin.Context) {
		var requests []InferenceRequest
		if err := c.ShouldBindJSON(&requests); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		if len(requests) > 100 { // Limit batch size
			c.JSON(http.StatusBadRequest, gin.H{"error": "batch size too large (max 100)"})
			return
		}

		responses := make([]*InferenceResponse, len(requests))
		var wg sync.WaitGroup
		
		for i, req := range requests {
			wg.Add(1)
			go func(idx int, request InferenceRequest) {
				defer wg.Done()
				
				if request.RequestID == "" {
					request.RequestID = fmt.Sprintf("batch_req_%d_%d", time.Now().UnixNano(), idx)
				}
				request.Timestamp = time.Now().Unix()

				ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
				defer cancel()

				response, err := d.ProcessInference(ctx, &request)
				if err != nil {
					response = &InferenceResponse{
						RequestID: request.RequestID,
						Metadata: map[string]interface{}{
							"error": err.Error(),
						},
						Timestamp: time.Now().Unix(),
					}
				}
				responses[idx] = response
			}(i, req)
		}

		wg.Wait()

		// Calculate batch summary
		totalCost := 0.0
		successCount := 0
		for _, resp := range responses {
			if resp.Metadata["error"] == nil {
				successCount++
				totalCost += resp.CostINR
			}
		}

		c.JSON(http.StatusOK, gin.H{
			"responses":     responses,
			"batch_size":    len(requests),
			"success_count": successCount,
			"total_cost_inr": fmt.Sprintf("₹%.4f", totalCost),
			"timestamp":     time.Now().Unix(),
		})
	})

	// Metrics endpoint
	router.GET("/metrics", gin.WrapH(promhttp.HandlerFor(d.metricsRegistry, promhttp.HandlerOpts{})))

	// System stats endpoint
	router.GET("/stats", func(c *gin.Context) {
		stats := map[string]interface{}{
			"server_info": map[string]interface{}{
				"server_id":      d.serverID,
				"uptime_seconds": int(time.Since(d.startTime).Seconds()),
				"version":        "1.0.0",
				"region":         "india-west",
			},
			"request_stats": map[string]interface{}{
				"total_requests": atomic.LoadInt64(&d.requestCounter),
				"total_errors":   atomic.LoadInt64(&d.errorCounter),
				"success_rate":   fmt.Sprintf("%.2f%%", float64(atomic.LoadInt64(&d.requestCounter)-atomic.LoadInt64(&d.errorCounter))/float64(atomic.LoadInt64(&d.requestCounter))*100),
			},
			"cost_stats": map[string]interface{}{
				"total_cost_inr":     fmt.Sprintf("₹%.2f", d.totalCostINR),
				"avg_cost_per_req":   fmt.Sprintf("₹%.4f", d.totalCostINR/float64(atomic.LoadInt64(&d.requestCounter))),
			},
			"cache_stats": map[string]interface{}{
				"hit_rate":   fmt.Sprintf("%.1f%%", d.cacheManager.GetHitRate()),
				"hit_count":  atomic.LoadInt64(&d.cacheManager.hitCount),
				"miss_count": atomic.LoadInt64(&d.cacheManager.missCount),
			},
			"model_instances": d.loadBalancer.instances,
		}

		c.JSON(http.StatusOK, stats)
	})

	return router
}

// LoadTest simulates high load for testing
func (d *DistributedInferenceSystem) LoadTest(requests int, concurrency int) {
	log.Printf("Starting load test: %d requests with %d concurrent workers", requests, concurrency)
	
	startTime := time.Now()
	var wg sync.WaitGroup
	requestChan := make(chan int, requests)
	
	// Fill request channel
	for i := 0; i < requests; i++ {
		requestChan <- i
	}
	close(requestChan)
	
	// Launch workers
	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			
			for reqNum := range requestChan {
				req := &InferenceRequest{
					Text:      fmt.Sprintf("यह एक test message है #%d", reqNum),
					ModelID:   "sentiment-hindi-v1",
					UserID:    fmt.Sprintf("user_%d", reqNum%1000), // 1000 unique users
					Language:  "hi",
					Region:    "north",
					RequestID: fmt.Sprintf("load_test_%d_%d", workerID, reqNum),
					Priority:  2, // medium priority
				}
				
				ctx := context.Background()
				_, err := d.ProcessInference(ctx, req)
				if err != nil {
					log.Printf("Request failed: %v", err)
				}
			}
		}(i)
	}
	
	wg.Wait()
	duration := time.Since(startTime)
	
	log.Printf("Load test completed:")
	log.Printf("  Duration: %v", duration)
	log.Printf("  Requests/second: %.2f", float64(requests)/duration.Seconds())
	log.Printf("  Total cost: ₹%.2f", d.totalCostINR)
	log.Printf("  Cache hit rate: %.1f%%", d.cacheManager.GetHitRate())
	log.Printf("  Success rate: %.2f%%", float64(atomic.LoadInt64(&d.requestCounter)-atomic.LoadInt64(&d.errorCounter))/float64(atomic.LoadInt64(&d.requestCounter))*100)
}

func main() {
	fmt.Println("🚀 Distributed Inference System - Indian Scale")
	fmt.Println("==============================================")
	
	// Initialize system
	system := NewDistributedInferenceSystem()
	
	// Setup HTTP routes
	router := system.setupRoutes()
	
	// Start background health checking
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()
		
		for range ticker.C {
			system.healthChecker.CheckHealth()
		}
	}()
	
	fmt.Printf("✅ System initialized\n")
	fmt.Printf("   Server ID: %s\n", system.serverID)
	fmt.Printf("   Model instances: %d\n", len(system.loadBalancer.instances))
	fmt.Printf("   Rate limits configured: %v\n", system.rateLimiter.limits)
	
	// Run load test
	fmt.Println("\n🧪 Running load test...")
	system.LoadTest(1000, 50) // 1000 requests, 50 concurrent
	
	// Start HTTP server
	fmt.Println("\n🌐 Starting HTTP server on :8080")
	fmt.Println("   Health: http://localhost:8080/health")
	fmt.Println("   Inference: POST http://localhost:8080/inference")
	fmt.Println("   Batch: POST http://localhost:8080/inference/batch")
	fmt.Println("   Stats: http://localhost:8080/stats")
	fmt.Println("   Metrics: http://localhost:8080/metrics")
	
	log.Fatal(router.Run(":8080"))
}