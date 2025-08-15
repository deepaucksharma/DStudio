/*
API Security Gateway (Go)
========================

यह high-performance API security gateway है Go में लिखी गई।
Kong, Envoy Proxy जैसे enterprise gateways की तरह यह
comprehensive security features provide करती है।

Features:
- JWT Token Validation
- Rate Limiting with Redis
- Request/Response Transformation
- Load Balancing
- Circuit Breaker
- Metrics Collection

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
*/

package main

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/redis/go-redis/v9"
	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Constants
const (
	// JWT Secret - Production में environment variable से load करें
	JWT_SECRET = "api_gateway_secret_change_in_production"
	
	// Rate limiting
	DEFAULT_RATE_LIMIT = 100
	RATE_WINDOW        = 60 // seconds
	
	// Circuit breaker
	FAILURE_THRESHOLD  = 5
	RECOVERY_TIMEOUT   = 30 * time.Second
)

// Metrics
var (
	requestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "api_gateway_requests_total",
			Help: "Total number of requests processed",
		},
		[]string{"method", "endpoint", "status"},
	)
	
	requestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "api_gateway_request_duration_seconds",
			Help: "Request duration in seconds",
		},
		[]string{"method", "endpoint"},
	)
	
	rateLimitExceeded = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "api_gateway_rate_limit_exceeded_total",
			Help: "Total number of rate limit exceeded",
		},
		[]string{"client_id"},
	)
)

// SecurityConfig represents security configuration
type SecurityConfig struct {
	RequireAuth    bool     `json:"require_auth"`
	RequiredScopes []string `json:"required_scopes"`
	RateLimit      int      `json:"rate_limit"`
	AllowedMethods []string `json:"allowed_methods"`
}

// UpstreamService represents backend service
type UpstreamService struct {
	ID       string `json:"id"`
	Name     string `json:"name"`
	URL      string `json:"url"`
	Weight   int    `json:"weight"`
	Healthy  bool   `json:"healthy"`
	proxy    *httputil.ReverseProxy
}

// Route represents API route configuration
type Route struct {
	ID        string           `json:"id"`
	Path      string           `json:"path"`
	Methods   []string         `json:"methods"`
	Upstreams []*UpstreamService `json:"upstreams"`
	Security  SecurityConfig   `json:"security"`
}

// Claims represents JWT claims
type Claims struct {
	UserID   string   `json:"sub"`
	ClientID string   `json:"client_id"`
	Scopes   []string `json:"scopes"`
	jwt.RegisteredClaims
}

// CircuitBreaker represents circuit breaker state
type CircuitBreaker struct {
	failureCount int
	lastFailure  time.Time
	state        string // "closed", "open", "half-open"
	mutex        sync.Mutex
}

// APIGateway represents the main gateway structure
type APIGateway struct {
	routes          map[string]*Route
	redis           *redis.Client
	circuitBreakers map[string]*CircuitBreaker
	loadBalancers   map[string]*LoadBalancer
	mutex           sync.RWMutex
}

// LoadBalancer handles load balancing
type LoadBalancer struct {
	services []*UpstreamService
	current  int
	mutex    sync.Mutex
}

// NewAPIGateway creates a new API gateway instance
func NewAPIGateway() *APIGateway {
	// Redis client
	rdb := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "",
		DB:       0,
	})
	
	gateway := &APIGateway{
		routes:          make(map[string]*Route),
		redis:           rdb,
		circuitBreakers: make(map[string]*CircuitBreaker),
		loadBalancers:   make(map[string]*LoadBalancer),
	}
	
	// Load default routes
	gateway.loadDefaultRoutes()
	
	// Start health check goroutine
	go gateway.startHealthChecks()
	
	log.Println("🚪 API Gateway initialized")
	return gateway
}

// loadDefaultRoutes loads default route configurations
func (gw *APIGateway) loadDefaultRoutes() {
	// User service route
	userService := &UpstreamService{
		ID:      "user-service",
		Name:    "User Management Service",
		URL:     "http://localhost:8001",
		Weight:  1,
		Healthy: true,
	}
	userService.proxy = gw.createProxy(userService.URL)
	
	userRoute := &Route{
		ID:      "user-api",
		Path:    "/api/v1/users",
		Methods: []string{"GET", "POST", "PUT", "DELETE"},
		Upstreams: []*UpstreamService{userService},
		Security: SecurityConfig{
			RequireAuth:    true,
			RequiredScopes: []string{"read", "write"},
			RateLimit:      50,
			AllowedMethods: []string{"GET", "POST", "PUT", "DELETE"},
		},
	}
	
	// Payment service route
	paymentService := &UpstreamService{
		ID:      "payment-service",
		Name:    "Payment Service",
		URL:     "http://localhost:8002",
		Weight:  1,
		Healthy: true,
	}
	paymentService.proxy = gw.createProxy(paymentService.URL)
	
	paymentRoute := &Route{
		ID:      "payment-api",
		Path:    "/api/v1/payments",
		Methods: []string{"POST", "GET"},
		Upstreams: []*UpstreamService{paymentService},
		Security: SecurityConfig{
			RequireAuth:    true,
			RequiredScopes: []string{"payment"},
			RateLimit:      20,
			AllowedMethods: []string{"POST", "GET"},
		},
	}
	
	// Public API route
	publicService := &UpstreamService{
		ID:      "public-service",
		Name:    "Public API Service",
		URL:     "http://localhost:8003",
		Weight:  1,
		Healthy: true,
	}
	publicService.proxy = gw.createProxy(publicService.URL)
	
	publicRoute := &Route{
		ID:      "public-api",
		Path:    "/api/v1/public",
		Methods: []string{"GET"},
		Upstreams: []*UpstreamService{publicService},
		Security: SecurityConfig{
			RequireAuth:    false,
			RequiredScopes: []string{},
			RateLimit:      200,
			AllowedMethods: []string{"GET"},
		},
	}
	
	// Register routes
	gw.routes[userRoute.Path] = userRoute
	gw.routes[paymentRoute.Path] = paymentRoute
	gw.routes[publicRoute.Path] = publicRoute
	
	// Initialize load balancers
	gw.loadBalancers[userRoute.ID] = &LoadBalancer{services: userRoute.Upstreams}
	gw.loadBalancers[paymentRoute.ID] = &LoadBalancer{services: paymentRoute.Upstreams}
	gw.loadBalancers[publicRoute.ID] = &LoadBalancer{services: publicRoute.Upstreams}
	
	// Initialize circuit breakers
	for _, route := range gw.routes {
		for _, upstream := range route.Upstreams {
			gw.circuitBreakers[upstream.ID] = &CircuitBreaker{
				state: "closed",
			}
		}
	}
	
	log.Println("📋 Default routes loaded")
}

// createProxy creates reverse proxy for upstream service
func (gw *APIGateway) createProxy(targetURL string) *httputil.ReverseProxy {
	target, _ := url.Parse(targetURL)
	
	proxy := httputil.NewSingleHostReverseProxy(target)
	
	// Customize proxy behavior
	proxy.ModifyResponse = func(resp *http.Response) error {
		// Add security headers
		resp.Header.Set("X-Gateway-Version", "1.0.0")
		resp.Header.Set("X-Frame-Options", "DENY")
		resp.Header.Set("X-Content-Type-Options", "nosniff")
		
		return nil
	}
	
	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		log.Printf("Proxy error: %v", err)
		
		// Record circuit breaker failure
		// Extract service ID from context or URL
		serviceID := r.Header.Get("X-Service-ID")
		if serviceID != "" {
			gw.recordFailure(serviceID)
		}
		
		w.WriteHeader(http.StatusBadGateway)
		json.NewEncoder(w).Encode(map[string]string{
			"error": "Service unavailable",
			"code":  "UPSTREAM_ERROR",
		})
	}
	
	return proxy
}

// Security Middleware
func (gw *APIGateway) securityMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Find matching route
		route := gw.findRoute(c.Request.URL.Path)
		if route == nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Route not found"})
			c.Abort()
			return
		}
		
		// Check if authentication required
		if route.Security.RequireAuth {
			if err := gw.validateJWT(c, route.Security.RequiredScopes); err != nil {
				c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
				c.Abort()
				return
			}
		}
		
		// Store route in context
		c.Set("route", route)
		c.Next()
	}
}

// Rate Limiting Middleware
func (gw *APIGateway) rateLimitMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		route, exists := c.Get("route")
		if !exists {
			c.Next()
			return
		}
		
		r := route.(*Route)
		
		// Get client identifier
		clientID := gw.getClientID(c)
		
		// Check rate limit
		if !gw.checkRateLimit(clientID, r.ID, r.Security.RateLimit) {
			rateLimitExceeded.WithLabelValues(clientID).Inc()
			
			c.Header("X-RateLimit-Limit", strconv.Itoa(r.Security.RateLimit))
			c.Header("X-RateLimit-Remaining", "0")
			c.Header("Retry-After", strconv.Itoa(RATE_WINDOW))
			
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error": "Rate limit exceeded",
				"limit": r.Security.RateLimit,
				"window": RATE_WINDOW,
			})
			c.Abort()
			return
		}
		
		c.Next()
	}
}

// Metrics Middleware
func (gw *APIGateway) metricsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method
		
		c.Next()
		
		duration := time.Since(start).Seconds()
		status := strconv.Itoa(c.Writer.Status())
		
		requestsTotal.WithLabelValues(method, path, status).Inc()
		requestDuration.WithLabelValues(method, path).Observe(duration)
	}
}

// Load Balancing और Proxying
func (gw *APIGateway) proxyHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		route, exists := c.Get("route")
		if !exists {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Route not found in context"})
			return
		}
		
		r := route.(*Route)
		
		// Select upstream service using load balancer
		upstream := gw.selectUpstream(r.ID)
		if upstream == nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{"error": "No healthy upstream services"})
			return
		}
		
		// Check circuit breaker
		if !gw.isServiceHealthy(upstream.ID) {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"error": "Service circuit breaker open",
				"service": upstream.ID,
			})
			return
		}
		
		// Add service ID to headers for error handling
		c.Request.Header.Set("X-Service-ID", upstream.ID)
		
		// Proxy request
		upstream.proxy.ServeHTTP(c.Writer, c.Request)
		
		// Record success
		gw.recordSuccess(upstream.ID)
	}
}

// JWT Validation
func (gw *APIGateway) validateJWT(c *gin.Context, requiredScopes []string) error {
	// Get token from Authorization header
	authHeader := c.GetHeader("Authorization")
	if authHeader == "" {
		return fmt.Errorf("authorization header required")
	}
	
	tokenString := strings.TrimPrefix(authHeader, "Bearer ")
	if tokenString == authHeader {
		return fmt.Errorf("bearer token required")
	}
	
	// Parse and validate JWT
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method")
		}
		return []byte(JWT_SECRET), nil
	})
	
	if err != nil {
		return fmt.Errorf("invalid token: %v", err)
	}
	
	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return fmt.Errorf("invalid token claims")
	}
	
	// Check required scopes
	if len(requiredScopes) > 0 {
		if !gw.hasRequiredScopes(claims.Scopes, requiredScopes) {
			return fmt.Errorf("insufficient scopes")
		}
	}
	
	// Store claims in context
	c.Set("claims", claims)
	
	return nil
}

// Rate Limiting Implementation
func (gw *APIGateway) checkRateLimit(clientID, routeID string, limit int) bool {
	ctx := context.Background()
	key := fmt.Sprintf("rate_limit:%s:%s", routeID, clientID)
	
	// Use Redis for distributed rate limiting
	current, err := gw.redis.Get(ctx, key).Int()
	if err == redis.Nil {
		// First request in window
		gw.redis.Set(ctx, key, 1, time.Duration(RATE_WINDOW)*time.Second)
		return true
	} else if err != nil {
		log.Printf("Redis error in rate limiting: %v", err)
		return true // Fail open
	}
	
	if current >= limit {
		return false
	}
	
	// Increment counter
	gw.redis.Incr(ctx, key)
	return true
}

// Load Balancing - Round Robin
func (gw *APIGateway) selectUpstream(routeID string) *UpstreamService {
	lb, exists := gw.loadBalancers[routeID]
	if !exists {
		return nil
	}
	
	lb.mutex.Lock()
	defer lb.mutex.Unlock()
	
	// Find next healthy service
	for i := 0; i < len(lb.services); i++ {
		service := lb.services[lb.current%len(lb.services)]
		lb.current++
		
		if service.Healthy {
			return service
		}
	}
	
	return nil // No healthy services
}

// Circuit Breaker Implementation
func (gw *APIGateway) isServiceHealthy(serviceID string) bool {
	cb, exists := gw.circuitBreakers[serviceID]
	if !exists {
		return true
	}
	
	cb.mutex.Lock()
	defer cb.mutex.Unlock()
	
	switch cb.state {
	case "closed":
		return true
	case "open":
		if time.Since(cb.lastFailure) > RECOVERY_TIMEOUT {
			cb.state = "half-open"
			return true
		}
		return false
	case "half-open":
		return true
	default:
		return true
	}
}

func (gw *APIGateway) recordFailure(serviceID string) {
	cb, exists := gw.circuitBreakers[serviceID]
	if !exists {
		return
	}
	
	cb.mutex.Lock()
	defer cb.mutex.Unlock()
	
	cb.failureCount++
	cb.lastFailure = time.Now()
	
	if cb.failureCount >= FAILURE_THRESHOLD {
		cb.state = "open"
		log.Printf("🔴 Circuit breaker opened for service: %s", serviceID)
	}
}

func (gw *APIGateway) recordSuccess(serviceID string) {
	cb, exists := gw.circuitBreakers[serviceID]
	if !exists {
		return
	}
	
	cb.mutex.Lock()
	defer cb.mutex.Unlock()
	
	if cb.state == "half-open" {
		cb.state = "closed"
		cb.failureCount = 0
		log.Printf("🟢 Circuit breaker closed for service: %s", serviceID)
	}
}

// Health Checks
func (gw *APIGateway) startHealthChecks() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			gw.performHealthChecks()
		}
	}
}

func (gw *APIGateway) performHealthChecks() {
	gw.mutex.RLock()
	defer gw.mutex.RUnlock()
	
	for _, route := range gw.routes {
		for _, upstream := range route.Upstreams {
			go gw.checkServiceHealth(upstream)
		}
	}
}

func (gw *APIGateway) checkServiceHealth(service *UpstreamService) {
	healthURL := service.URL + "/health"
	
	client := &http.Client{
		Timeout: 5 * time.Second,
	}
	
	resp, err := client.Get(healthURL)
	if err != nil {
		service.Healthy = false
		log.Printf("❌ Health check failed for %s: %v", service.ID, err)
		return
	}
	defer resp.Body.Close()
	
	if resp.StatusCode == http.StatusOK {
		if !service.Healthy {
			log.Printf("✅ Service %s is healthy again", service.ID)
		}
		service.Healthy = true
	} else {
		service.Healthy = false
		log.Printf("❌ Health check failed for %s: status %d", service.ID, resp.StatusCode)
	}
}

// Helper Functions
func (gw *APIGateway) findRoute(path string) *Route {
	gw.mutex.RLock()
	defer gw.mutex.RUnlock()
	
	// Simple prefix matching (production में trie या regex use करें)
	for routePath, route := range gw.routes {
		if strings.HasPrefix(path, routePath) {
			return route
		}
	}
	
	return nil
}

func (gw *APIGateway) getClientID(c *gin.Context) string {
	// Try to get from JWT claims
	if claims, exists := c.Get("claims"); exists {
		if cl, ok := claims.(*Claims); ok {
			return cl.ClientID
		}
	}
	
	// Fallback to IP address
	return c.ClientIP()
}

func (gw *APIGateway) hasRequiredScopes(userScopes, requiredScopes []string) bool {
	scopeMap := make(map[string]bool)
	for _, scope := range userScopes {
		scopeMap[scope] = true
	}
	
	for _, required := range requiredScopes {
		if !scopeMap[required] {
			return false
		}
	}
	
	return true
}

// Admin Endpoints
func (gw *APIGateway) setupAdminRoutes(router *gin.Engine) {
	admin := router.Group("/admin")
	
	// Health endpoint
	admin.GET("/health", func(c *gin.Context) {
		healthyServices := 0
		totalServices := 0
		
		gw.mutex.RLock()
		for _, route := range gw.routes {
			for _, upstream := range route.Upstreams {
				totalServices++
				if upstream.Healthy {
					healthyServices++
				}
			}
		}
		gw.mutex.RUnlock()
		
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"timestamp": time.Now().Format(time.RFC3339),
			"services": gin.H{
				"healthy": healthyServices,
				"total":   totalServices,
			},
		})
	})
	
	// Routes endpoint
	admin.GET("/routes", func(c *gin.Context) {
		gw.mutex.RLock()
		routes := make([]gin.H, 0, len(gw.routes))
		for _, route := range gw.routes {
			routes = append(routes, gin.H{
				"id":      route.ID,
				"path":    route.Path,
				"methods": route.Methods,
				"security": gin.H{
					"require_auth": route.Security.RequireAuth,
					"rate_limit":   route.Security.RateLimit,
				},
			})
		}
		gw.mutex.RUnlock()
		
		c.JSON(http.StatusOK, gin.H{"routes": routes})
	})
	
	// Circuit breaker status
	admin.GET("/circuit-breakers", func(c *gin.Context) {
		status := make(map[string]gin.H)
		
		for serviceID, cb := range gw.circuitBreakers {
			cb.mutex.Lock()
			status[serviceID] = gin.H{
				"state":         cb.state,
				"failure_count": cb.failureCount,
				"last_failure":  cb.lastFailure.Format(time.RFC3339),
			}
			cb.mutex.Unlock()
		}
		
		c.JSON(http.StatusOK, gin.H{"circuit_breakers": status})
	})
}

// Mock JWT Token Generation (Testing के लिए)
func generateTestJWT(userID, clientID string, scopes []string) (string, error) {
	claims := &Claims{
		UserID:   userID,
		ClientID: clientID,
		Scopes:   scopes,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "api-gateway",
		},
	}
	
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(JWT_SECRET))
}

// Main Function
func main() {
	// Create API Gateway
	gateway := NewAPIGateway()
	
	// Setup Gin router
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	
	// Add middlewares
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	router.Use(gateway.metricsMiddleware())
	router.Use(gateway.securityMiddleware())
	router.Use(gateway.rateLimitMiddleware())
	
	// Main proxy handler
	router.NoRoute(gateway.proxyHandler())
	
	// Admin routes
	gateway.setupAdminRoutes(router)
	
	// Metrics endpoint
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))
	
	// Test token generation endpoint
	router.GET("/test/token", func(c *gin.Context) {
		token, err := generateTestJWT("user123", "test-client", []string{"read", "write", "payment"})
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		
		c.JSON(http.StatusOK, gin.H{
			"token": token,
			"curl_example": fmt.Sprintf(`curl -H "Authorization: Bearer %s" http://localhost:8080/api/v1/users`, token),
		})
	})
	
	// Mock upstream services (Testing के लिए)
	go startMockServices()
	
	// Start server
	log.Println("🚀 API Security Gateway starting on :8080")
	log.Println("📊 Metrics available at /metrics")
	log.Println("🔧 Admin interface at /admin/*")
	log.Println("🔑 Test token at /test/token")
	
	if err := router.Run(":8080"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

// Mock Services for Testing
func startMockServices() {
	// User service mock
	go func() {
		mux := http.NewServeMux()
		mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]string{"status": "healthy", "service": "user-service"})
		})
		mux.HandleFunc("/api/v1/users", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"users": []map[string]string{
					{"id": "1", "name": "Rahul Mumbai", "email": "rahul@example.com"},
					{"id": "2", "name": "Priya Delhi", "email": "priya@example.com"},
				},
				"service": "user-service",
			})
		})
		log.Println("👤 Mock User Service started on :8001")
		http.ListenAndServe(":8001", mux)
	}()
	
	// Payment service mock
	go func() {
		mux := http.NewServeMux()
		mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]string{"status": "healthy", "service": "payment-service"})
		})
		mux.HandleFunc("/api/v1/payments", func(w http.ResponseWriter, r *http.Request) {
			if r.Method == "POST" {
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(map[string]interface{}{
					"payment_id": "pay_123456",
					"status": "success",
					"amount": 1000.0,
					"service": "payment-service",
				})
			} else {
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(map[string]interface{}{
					"payments": []map[string]interface{}{
						{"id": "pay_123", "amount": 500.0, "status": "completed"},
						{"id": "pay_456", "amount": 750.0, "status": "pending"},
					},
					"service": "payment-service",
				})
			}
		})
		log.Println("💳 Mock Payment Service started on :8002")
		http.ListenAndServe(":8002", mux)
	}()
	
	// Public service mock
	go func() {
		mux := http.NewServeMux()
		mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]string{"status": "healthy", "service": "public-service"})
		})
		mux.HandleFunc("/api/v1/public", func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"message": "Public API is working",
				"timestamp": time.Now().Format(time.RFC3339),
				"service": "public-service",
			})
		})
		log.Println("🌐 Mock Public Service started on :8003")
		http.ListenAndServe(":8003", mux)
	}()
}

/*
Production Deployment Notes:
============================

1. Performance Optimizations:
   - Use connection pooling
   - Implement HTTP/2 support
   - Add request/response caching
   - Use efficient data structures

2. Security Enhancements:
   - TLS termination
   - Request signing verification
   - IP whitelisting/blacklisting
   - WAF integration

3. Observability:
   - Distributed tracing (Jaeger/Zipkin)
   - Structured logging
   - Custom metrics
   - Alerting rules

4. High Availability:
   - Multiple gateway instances
   - Redis cluster for shared state
   - Health check improvements
   - Graceful shutdown

5. Configuration:
   - External configuration management
   - Hot reloading of routes
   - Environment-specific settings
   - Secret management

यह implementation Kong, Envoy level की API gateway functionality provide करता है!
*/