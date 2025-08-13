// Cloud Native API Gateway Implementation
// क्लाउड नेटिव एपीआई गेटवे कार्यान्वयन
//
// Real-world example: Razorpay's API Gateway for payment processing
// High-performance, feature-rich API gateway for Indian fintech scale

package main

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/gorilla/mux"
	"golang.org/x/time/rate"
)

// LoadBalancingStrategy defines load balancing algorithms
// लोड बैलेंसिंग रणनीति परिभाषित करती है
type LoadBalancingStrategy int

const (
	RoundRobin LoadBalancingStrategy = iota
	LeastConnections
	WeightedRoundRobin
	IPHash
	HealthBased
)

// BackendStatus represents backend health status
// बैकएंड हेल्थ स्टेटस का प्रतिनिधित्व करता है
type BackendStatus int

const (
	Healthy BackendStatus = iota
	Unhealthy
	Draining
)

// Backend represents a backend service instance
// बैकएंड सर्विस इंस्टेंस का प्रतिनिधित्व करता है
type Backend struct {
	ID                string        `json:"id"`
	URL               *url.URL      `json:"url"`
	Weight            int           `json:"weight"`
	CurrentWeight     int           `json:"current_weight"`
	MaxConnections    int           `json:"max_connections"`
	ActiveConnections int64         `json:"active_connections"`
	Status            BackendStatus `json:"status"`
	LastHealthCheck   time.Time     `json:"last_health_check"`
	ResponseTime      time.Duration `json:"response_time"`
	ErrorCount        int64         `json:"error_count"`
	RequestCount      int64         `json:"request_count"`
	Region            string        `json:"region"`
	Zone              string        `json:"zone"`
	Metadata          map[string]string `json:"metadata"`
	mutex             sync.RWMutex
}

// Route represents an API route configuration
// एपीआई रूट कॉन्फ़िगरेशन का प्रतिनिधित्व करता है
type Route struct {
	ID                 string                `json:"id"`
	Path               string                `json:"path"`
	Method             string                `json:"method"`
	ServiceName        string                `json:"service_name"`
	Backends           []*Backend            `json:"backends"`
	LoadBalancer       LoadBalancingStrategy `json:"load_balancer"`
	Timeout            time.Duration         `json:"timeout"`
	RetryAttempts      int                   `json:"retry_attempts"`
	RateLimiter        *rate.Limiter         `json:"-"`
	RateLimit          int                   `json:"rate_limit"`
	CircuitBreakerOpen bool                  `json:"circuit_breaker_open"`
	Middleware         []string              `json:"middleware"`
	RequireAuth        bool                  `json:"require_auth"`
	AllowedOrigins     []string              `json:"allowed_origins"`
	CreatedAt          time.Time             `json:"created_at"`
	UpdatedAt          time.Time             `json:"updated_at"`
	mutex              sync.RWMutex
}

// RazorpayAPIGateway represents the main API gateway
// मुख्य एपीआई गेटवे का प्रतिनिधित्व करता है
type RazorpayAPIGateway struct {
	routes          map[string]*Route
	globalRateLimit *rate.Limiter
	healthChecker   *HealthChecker
	metrics         *GatewayMetrics
	middleware      []MiddlewareFunc
	tlsConfig       *tls.Config
	shutdownCh      chan struct{}
	mutex           sync.RWMutex
}

// MiddlewareFunc represents a middleware function
type MiddlewareFunc func(http.Handler) http.Handler

// GatewayMetrics holds gateway performance metrics
// गेटवे प्रदर्शन मेट्रिक्स रखता है
type GatewayMetrics struct {
	TotalRequests    int64             `json:"total_requests"`
	TotalResponses   int64             `json:"total_responses"`
	ErrorRequests    int64             `json:"error_requests"`
	ResponseTimes    map[string]int64  `json:"response_times"`
	BackendStatus    map[string]string `json:"backend_status"`
	RateLimitHits    int64             `json:"rate_limit_hits"`
	CircuitBreakerHits int64           `json:"circuit_breaker_hits"`
	ActiveConnections int64            `json:"active_connections"`
	StartTime        time.Time         `json:"start_time"`
	mutex            sync.RWMutex
}

// HealthChecker performs backend health checks
// बैकएंड हेल्थ चेक करता है
type HealthChecker struct {
	interval     time.Duration
	timeout      time.Duration
	gateway      *RazorpayAPIGateway
	stopCh       chan struct{}
	httpClient   *http.Client
}

// NewRazorpayAPIGateway creates a new API gateway instance
// नया एपीआई गेटवे इंस्टेंस बनाता है
func NewRazorpayAPIGateway() *RazorpayAPIGateway {
	gateway := &RazorpayAPIGateway{
		routes:          make(map[string]*Route),
		globalRateLimit: rate.NewLimiter(rate.Limit(10000), 10000), // 10k req/sec burst
		metrics:         &GatewayMetrics{
			ResponseTimes: make(map[string]int64),
			BackendStatus: make(map[string]string),
			StartTime:     time.Now(),
		},
		middleware: make([]MiddlewareFunc, 0),
		tlsConfig: &tls.Config{
			MinVersion: tls.VersionTLS12,
		},
		shutdownCh: make(chan struct{}),
	}

	// Initialize health checker
	gateway.healthChecker = &HealthChecker{
		interval: 30 * time.Second,
		timeout:  5 * time.Second,
		gateway:  gateway,
		stopCh:   make(chan struct{}),
		httpClient: &http.Client{
			Timeout: 5 * time.Second,
			Transport: &http.Transport{
				MaxIdleConns:       100,
				IdleConnTimeout:    90 * time.Second,
				DisableCompression: false,
			},
		},
	}

	// Setup default routes for Razorpay services
	gateway.setupDefaultRoutes()

	log.Println("💳 Razorpay API Gateway initialized")
	return gateway
}

// setupDefaultRoutes configures default routes for Razorpay services
// Razorpay सेवाओं के लिए डिफ़ॉल्ट रूट कॉन्फ़िगर करता है
func (gw *RazorpayAPIGateway) setupDefaultRoutes() {
	// Payment processing route
	paymentBackends := []*Backend{
		{
			ID:             "payment-svc-1",
			URL:            parseURL("http://payment-service-1:8080"),
			Weight:         100,
			MaxConnections: 1000,
			Status:         Healthy,
			Region:         "ap-south-1",
			Zone:           "ap-south-1a",
			Metadata:       map[string]string{"version": "2.1.0"},
		},
		{
			ID:             "payment-svc-2", 
			URL:            parseURL("http://payment-service-2:8080"),
			Weight:         100,
			MaxConnections: 1000,
			Status:         Healthy,
			Region:         "ap-south-1",
			Zone:           "ap-south-1b",
			Metadata:       map[string]string{"version": "2.1.0"},
		},
		{
			ID:             "payment-svc-3",
			URL:            parseURL("http://payment-service-3:8080"),
			Weight:         50, // Canary deployment
			MaxConnections: 500,
			Status:         Healthy,
			Region:         "ap-south-1",
			Zone:           "ap-south-1c",
			Metadata:       map[string]string{"version": "2.2.0-beta"},
		},
	}

	gw.RegisterRoute(&Route{
		ID:             "payment-processing",
		Path:           "/v1/payments",
		Method:         "POST",
		ServiceName:    "payment-service",
		Backends:       paymentBackends,
		LoadBalancer:   WeightedRoundRobin,
		Timeout:        30 * time.Second,
		RetryAttempts:  2,
		RateLimit:      1000, // 1000 req/min per client
		RequireAuth:    true,
		AllowedOrigins: []string{"https://dashboard.razorpay.com", "https://checkout.razorpay.com"},
		Middleware:     []string{"auth", "rateLimit", "cors", "metrics"},
	})

	// UPI payment route
	upiBackends := []*Backend{
		{
			ID:             "upi-svc-1",
			URL:            parseURL("http://upi-service-1:8080"),
			Weight:         100,
			MaxConnections: 2000,
			Status:         Healthy,
			Region:         "ap-south-1",
			Zone:           "ap-south-1a",
		},
		{
			ID:             "upi-svc-2",
			URL:            parseURL("http://upi-service-2:8080"),
			Weight:         100,
			MaxConnections: 2000,
			Status:         Healthy,
			Region:         "ap-south-1",
			Zone:           "ap-south-1b",
		},
	}

	gw.RegisterRoute(&Route{
		ID:             "upi-payments",
		Path:           "/v1/payments/upi",
		Method:         "POST",
		ServiceName:    "upi-service",
		Backends:       upiBackends,
		LoadBalancer:   RoundRobin,
		Timeout:        15 * time.Second,
		RetryAttempts:  3,
		RateLimit:      2000, // Higher limit for UPI
		RequireAuth:    true,
		Middleware:     []string{"auth", "rateLimit", "upiValidation", "metrics"},
	})

	// Merchant onboarding route
	merchantBackends := []*Backend{
		{
			ID:             "merchant-svc-1",
			URL:            parseURL("http://merchant-service-1:8080"),
			Weight:         100,
			MaxConnections: 500,
			Status:         Healthy,
			Region:         "ap-south-1",
		},
	}

	gw.RegisterRoute(&Route{
		ID:             "merchant-onboarding",
		Path:           "/v1/merchants",
		Method:         "POST",
		ServiceName:    "merchant-service",
		Backends:       merchantBackends,
		LoadBalancer:   RoundRobin,
		Timeout:        60 * time.Second, // Longer timeout for onboarding
		RetryAttempts:  1,
		RateLimit:      100, // Lower rate limit for onboarding
		RequireAuth:    true,
		Middleware:     []string{"auth", "rateLimit", "kycValidation", "metrics"},
	})

	log.Println("🛤️ Default routes configured for Razorpay services")
}

// RegisterRoute registers a new route in the gateway
// गेटवे में नया रूट रजिस्टर करता है
func (gw *RazorpayAPIGateway) RegisterRoute(route *Route) {
	gw.mutex.Lock()
	defer gw.mutex.Unlock()

	route.ID = generateRouteID(route.Path, route.Method)
	route.RateLimiter = rate.NewLimiter(rate.Limit(route.RateLimit), route.RateLimit)
	route.CreatedAt = time.Now()
	route.UpdatedAt = time.Now()

	// Initialize backend weights for weighted round robin
	for _, backend := range route.Backends {
		backend.CurrentWeight = backend.Weight
	}

	gw.routes[route.ID] = route
	log.Printf("📝 Registered route: %s %s -> %s", route.Method, route.Path, route.ServiceName)
}

// StartGateway starts the API gateway server
// एपीआई गेटवे सर्वर शुरू करता है
func (gw *RazorpayAPIGateway) StartGateway(port int) error {
	// Start health checker
	go gw.healthChecker.Start()

	// Setup middleware
	gw.setupMiddleware()

	// Create HTTP router
	router := mux.NewRouter()

	// Register routes
	gw.mutex.RLock()
	for _, route := range gw.routes {
		gw.registerHTTPRoute(router, route)
	}
	gw.mutex.RUnlock()

	// Add gateway management endpoints
	gw.addManagementEndpoints(router)

	// Create HTTP server
	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", port),
		Handler:      gw.applyMiddleware(router),
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
		TLSConfig:    gw.tlsConfig,
	}

	log.Printf("🚀 Starting Razorpay API Gateway on port %d", port)

	// Start server
	return server.ListenAndServe()
}

// setupMiddleware configures gateway middleware
// गेटवे मिडलवेयर कॉन्फ़िगर करता है
func (gw *RazorpayAPIGateway) setupMiddleware() {
	// Request logging middleware
	gw.middleware = append(gw.middleware, func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// Increment request counter
			atomic.AddInt64(&gw.metrics.TotalRequests, 1)
			atomic.AddInt64(&gw.metrics.ActiveConnections, 1)

			next.ServeHTTP(w, r)

			// Record response time
			duration := time.Since(start)
			gw.metrics.mutex.Lock()
			gw.metrics.ResponseTimes[r.URL.Path] = duration.Milliseconds()
			gw.metrics.mutex.Unlock()

			atomic.AddInt64(&gw.metrics.ActiveConnections, -1)
			atomic.AddInt64(&gw.metrics.TotalResponses, 1)

			log.Printf("📊 %s %s - %v", r.Method, r.URL.Path, duration)
		})
	})

	// CORS middleware
	gw.middleware = append(gw.middleware, func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Add CORS headers
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")

			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}

			next.ServeHTTP(w, r)
		})
	})

	// Global rate limiting middleware
	gw.middleware = append(gw.middleware, func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if !gw.globalRateLimit.Allow() {
				atomic.AddInt64(&gw.metrics.RateLimitHits, 1)
				http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
				return
			}

			next.ServeHTTP(w, r)
		})
	})

	log.Println("🔧 Gateway middleware configured")
}

// registerHTTPRoute registers a single HTTP route
// एकल HTTP रूट रजिस्टर करता है
func (gw *RazorpayAPIGateway) registerHTTPRoute(router *mux.Router, route *Route) {
	handler := gw.createRouteHandler(route)

	if route.Method == "GET" {
		router.HandleFunc(route.Path, handler).Methods("GET")
	} else if route.Method == "POST" {
		router.HandleFunc(route.Path, handler).Methods("POST")
	} else if route.Method == "PUT" {
		router.HandleFunc(route.Path, handler).Methods("PUT")
	} else if route.Method == "DELETE" {
		router.HandleFunc(route.Path, handler).Methods("DELETE")
	}
}

// createRouteHandler creates an HTTP handler for a route
// रूट के लिए HTTP हैंडलर बनाता है
func (gw *RazorpayAPIGateway) createRouteHandler(route *Route) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Check circuit breaker
		if route.CircuitBreakerOpen {
			atomic.AddInt64(&gw.metrics.CircuitBreakerHits, 1)
			http.Error(w, "Service Temporarily Unavailable", http.StatusServiceUnavailable)
			return
		}

		// Apply route-specific rate limiting
		if !route.RateLimiter.Allow() {
			atomic.AddInt64(&gw.metrics.RateLimitHits, 1)
			http.Error(w, "Rate limit exceeded for this endpoint", http.StatusTooManyRequests)
			return
		}

		// Select backend using load balancing strategy
		backend := gw.selectBackend(route)
		if backend == nil {
			atomic.AddInt64(&gw.metrics.ErrorRequests, 1)
			http.Error(w, "No healthy backends available", http.StatusServiceUnavailable)
			return
		}

		// Create reverse proxy
		proxy := gw.createReverseProxy(backend, route)

		// Set request context with timeout
		ctx, cancel := context.WithTimeout(r.Context(), route.Timeout)
		defer cancel()

		// Proxy request
		r = r.WithContext(ctx)
		proxy.ServeHTTP(w, r)
	}
}

// selectBackend selects a backend based on load balancing strategy
// लोड बैलेंसिंग रणनीति के आधार पर बैकएंड चुनता है
func (gw *RazorpayAPIGateway) selectBackend(route *Route) *Backend {
	route.mutex.RLock()
	defer route.mutex.RUnlock()

	healthyBackends := make([]*Backend, 0)
	for _, backend := range route.Backends {
		if backend.Status == Healthy &&
			atomic.LoadInt64(&backend.ActiveConnections) < int64(backend.MaxConnections) {
			healthyBackends = append(healthyBackends, backend)
		}
	}

	if len(healthyBackends) == 0 {
		return nil
	}

	switch route.LoadBalancer {
	case RoundRobin:
		return gw.roundRobinSelect(healthyBackends)
	case LeastConnections:
		return gw.leastConnectionsSelect(healthyBackends)
	case WeightedRoundRobin:
		return gw.weightedRoundRobinSelect(healthyBackends)
	default:
		return healthyBackends[0]
	}
}

// roundRobinSelect implements round robin load balancing
// राउंड रॉबिन लोड बैलेंसिंग लागू करता है
func (gw *RazorpayAPIGateway) roundRobinSelect(backends []*Backend) *Backend {
	// Simple round robin based on current time
	index := int(time.Now().UnixNano()) % len(backends)
	return backends[index]
}

// leastConnectionsSelect selects backend with least active connections
// सबसे कम सक्रिय कनेक्शन वाले बैकएंड को चुनता है
func (gw *RazorpayAPIGateway) leastConnectionsSelect(backends []*Backend) *Backend {
	var selected *Backend
	minConnections := int64(^uint64(0) >> 1) // Max int64

	for _, backend := range backends {
		connections := atomic.LoadInt64(&backend.ActiveConnections)
		if connections < minConnections {
			minConnections = connections
			selected = backend
		}
	}

	return selected
}

// weightedRoundRobinSelect implements weighted round robin
// वेटेड राउंड रॉबिन लागू करता है
func (gw *RazorpayAPIGateway) weightedRoundRobinSelect(backends []*Backend) *Backend {
	var selected *Backend
	totalWeight := 0
	maxCurrentWeight := -1

	for _, backend := range backends {
		totalWeight += backend.Weight
		backend.CurrentWeight += backend.Weight

		if backend.CurrentWeight > maxCurrentWeight {
			maxCurrentWeight = backend.CurrentWeight
			selected = backend
		}
	}

	if selected != nil {
		selected.CurrentWeight -= totalWeight
	}

	return selected
}

// createReverseProxy creates a reverse proxy for the backend
// बैकएंड के लिए रिवर्स प्रॉक्सी बनाता है
func (gw *RazorpayAPIGateway) createReverseProxy(backend *Backend, route *Route) *httputil.ReverseProxy {
	proxy := httputil.NewSingleHostReverseProxy(backend.URL)

	// Increment active connections
	atomic.AddInt64(&backend.ActiveConnections, 1)
	atomic.AddInt64(&backend.RequestCount, 1)

	// Custom director to modify request
	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)

		// Add custom headers
		req.Header.Set("X-Gateway-Version", "1.0.0")
		req.Header.Set("X-Backend-ID", backend.ID)
		req.Header.Set("X-Forwarded-For", req.RemoteAddr)
		req.Header.Set("X-Request-ID", generateRequestID())

		// Add Razorpay-specific headers
		req.Header.Set("X-Razorpay-Region", backend.Region)
		req.Header.Set("X-Razorpay-Zone", backend.Zone)
	}

	// Custom error handler
	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		atomic.AddInt64(&backend.ErrorCount, 1)
		atomic.AddInt64(&gw.metrics.ErrorRequests, 1)

		log.Printf("❌ Proxy error for backend %s: %v", backend.ID, err)

		// Check if we should open circuit breaker
		if shouldOpenCircuitBreaker(backend) {
			route.CircuitBreakerOpen = true
			go gw.scheduleCircuitBreakerReset(route)
		}

		http.Error(w, "Backend service unavailable", http.StatusBadGateway)
	}

	// Modify response
	proxy.ModifyResponse = func(resp *http.Response) error {
		// Decrement active connections
		atomic.AddInt64(&backend.ActiveConnections, -1)

		// Add response headers
		resp.Header.Set("X-Gateway", "Razorpay-API-Gateway")
		resp.Header.Set("X-Backend-ID", backend.ID)

		return nil
	}

	return proxy
}

// shouldOpenCircuitBreaker determines if circuit breaker should open
// सर्किट ब्रेकर खोलना चाहिए या नहीं निर्धारित करता है
func shouldOpenCircuitBreaker(backend *Backend) bool {
	errorRate := float64(atomic.LoadInt64(&backend.ErrorCount)) / float64(atomic.LoadInt64(&backend.RequestCount))
	return errorRate > 0.5 && atomic.LoadInt64(&backend.RequestCount) > 10
}

// scheduleCircuitBreakerReset schedules circuit breaker reset
// सर्किट ब्रेकर रीसेट शेड्यूल करता है
func (gw *RazorpayAPIGateway) scheduleCircuitBreakerReset(route *Route) {
	time.Sleep(30 * time.Second) // Wait 30 seconds
	route.CircuitBreakerOpen = false
	log.Printf("🔄 Circuit breaker reset for route: %s", route.ID)
}

// Start starts the health checker
// हेल्थ चेकर शुरू करता है
func (hc *HealthChecker) Start() {
	ticker := time.NewTicker(hc.interval)
	defer ticker.Stop()

	log.Println("🔍 Health checker started")

	for {
		select {
		case <-ticker.C:
			hc.performHealthChecks()
		case <-hc.stopCh:
			return
		}
	}
}

// performHealthChecks performs health checks on all backends
// सभी बैकएंड पर हेल्थ चेक करता है
func (hc *HealthChecker) performHealthChecks() {
	hc.gateway.mutex.RLock()
	defer hc.gateway.mutex.RUnlock()

	for _, route := range hc.gateway.routes {
		for _, backend := range route.Backends {
			go hc.checkBackendHealth(backend)
		}
	}
}

// checkBackendHealth checks health of a single backend
// एकल बैकएंड की हेल्थ चेक करता है
func (hc *HealthChecker) checkBackendHealth(backend *Backend) {
	healthURL := fmt.Sprintf("%s/health", backend.URL.String())
	
	start := time.Now()
	resp, err := hc.httpClient.Get(healthURL)
	duration := time.Since(start)

	backend.mutex.Lock()
	backend.LastHealthCheck = time.Now()
	backend.ResponseTime = duration
	backend.mutex.Unlock()

	if err != nil || resp.StatusCode != http.StatusOK {
		if backend.Status == Healthy {
			backend.Status = Unhealthy
			log.Printf("⚠️ Backend %s marked unhealthy", backend.ID)
		}
		
		hc.gateway.metrics.mutex.Lock()
		hc.gateway.metrics.BackendStatus[backend.ID] = "unhealthy"
		hc.gateway.metrics.mutex.Unlock()
	} else {
		if backend.Status == Unhealthy {
			backend.Status = Healthy
			log.Printf("✅ Backend %s recovered", backend.ID)
		}
		
		hc.gateway.metrics.mutex.Lock()
		hc.gateway.metrics.BackendStatus[backend.ID] = "healthy"
		hc.gateway.metrics.mutex.Unlock()
	}

	if resp != nil {
		resp.Body.Close()
	}
}

// addManagementEndpoints adds gateway management endpoints
// गेटवे प्रबंधन एंडपॉइंट जोड़ता है
func (gw *RazorpayAPIGateway) addManagementEndpoints(router *mux.Router) {
	// Health endpoint
	router.HandleFunc("/gateway/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"status":    "healthy",
			"timestamp": time.Now().Format(time.RFC3339),
			"version":   "1.0.0",
		})
	}).Methods("GET")

	// Metrics endpoint
	router.HandleFunc("/gateway/metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		gw.metrics.mutex.RLock()
		defer gw.metrics.mutex.RUnlock()
		json.NewEncoder(w).Encode(gw.metrics)
	}).Methods("GET")

	// Routes endpoint
	router.HandleFunc("/gateway/routes", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		gw.mutex.RLock()
		defer gw.mutex.RUnlock()
		json.NewEncoder(w).Encode(gw.routes)
	}).Methods("GET")

	// Backends endpoint
	router.HandleFunc("/gateway/backends", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		
		backends := make(map[string][]*Backend)
		gw.mutex.RLock()
		for _, route := range gw.routes {
			backends[route.ServiceName] = route.Backends
		}
		gw.mutex.RUnlock()
		
		json.NewEncoder(w).Encode(backends)
	}).Methods("GET")
}

// applyMiddleware applies all registered middleware
// सभी पंजीकृत मिडलवेयर लागू करता है
func (gw *RazorpayAPIGateway) applyMiddleware(handler http.Handler) http.Handler {
	for i := len(gw.middleware) - 1; i >= 0; i-- {
		handler = gw.middleware[i](handler)
	}
	return handler
}

// Utility functions
func parseURL(rawURL string) *url.URL {
	u, err := url.Parse(rawURL)
	if err != nil {
		log.Fatalf("Invalid URL: %s", rawURL)
	}
	return u
}

func generateRouteID(path, method string) string {
	return fmt.Sprintf("%s-%s-%d", method, strings.ReplaceAll(path, "/", "-"), time.Now().Unix())
}

func generateRequestID() string {
	return fmt.Sprintf("req-%d-%d", time.Now().UnixNano(), rand.Int31())
}

// Main demonstration function
func main() {
	fmt.Println("💳 Razorpay Cloud Native API Gateway Demo")
	fmt.Println("==========================================")

	// Create gateway instance
	gateway := NewRazorpayAPIGateway()

	// Add custom route for webhook processing
	webhookBackends := []*Backend{
		{
			ID:             "webhook-processor-1",
			URL:            parseURL("http://webhook-service:8080"),
			Weight:         100,
			MaxConnections: 500,
			Status:         Healthy,
			Region:         "ap-south-1",
		},
	}

	gateway.RegisterRoute(&Route{
		Path:           "/v1/webhooks",
		Method:         "POST",
		ServiceName:    "webhook-service",
		Backends:       webhookBackends,
		LoadBalancer:   RoundRobin,
		Timeout:        10 * time.Second,
		RetryAttempts:  1,
		RateLimit:      500,
		RequireAuth:    false, // Webhooks use different auth
		Middleware:     []string{"webhookValidation", "metrics"},
	})

	fmt.Println("\n🎯 Gateway Features:")
	fmt.Println("  ✅ Multiple load balancing strategies")
	fmt.Println("  ✅ Circuit breaker pattern")
	fmt.Println("  ✅ Rate limiting (global and per-route)")
	fmt.Println("  ✅ Health checking with automatic recovery")
	fmt.Println("  ✅ Request/response middleware")
	fmt.Println("  ✅ Comprehensive metrics and monitoring")
	fmt.Println("  ✅ Indian payment service integration")
	fmt.Println("  ✅ Management APIs for observability")

	fmt.Println("\n🚀 Starting gateway on port 8080...")
	fmt.Println("Management endpoints:")
	fmt.Println("  - http://localhost:8080/gateway/health")
	fmt.Println("  - http://localhost:8080/gateway/metrics")
	fmt.Println("  - http://localhost:8080/gateway/routes")
	fmt.Println("  - http://localhost:8080/gateway/backends")

	// Start the gateway (this would run indefinitely in a real scenario)
	log.Fatal(gateway.StartGateway(8080))
}