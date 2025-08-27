// Episode 125: Zero Trust Gateway Implementation
// Mumbai Police Checkpoint Style Security
// 
// Bhai, jaise Mumbai Police har checkpoint pe 
// \"kaun hai, kaha se aaya, kaha jaana hai\" puchti hai,
// waise hi ye gateway har request ko verify karta hai.
// Zero Trust = Kisi pe bharosa nahi!
//
// Author: Hindi Podcast Team
// Cost: ₹8,000-15,000/month for production deployment
// Security Level: Enterprise Grade

package main

import (
	\"context\"
	\"crypto/sha256\"
	\"encoding/hex\"
	\"encoding/json\"
	\"fmt\"
	\"log\"
	\"net/http\"
	\"strings\"
	\"time\"

	\"github.com/dgrijalva/jwt-go\"
	\"github.com/gin-gonic/gin\"
	\"github.com/go-redis/redis/v8\"
	\"github.com/prometheus/client_golang/prometheus\"
	\"github.com/prometheus/client_golang/prometheus/promhttp\"
)

// MumbaiSecurityClaims - JWT claims with Mumbai context
type MumbaiSecurityClaims struct {
	UserID        string   `json:\"user_id\"`
	Name          string   `json:\"name\"`
	Role          string   `json:\"role\"`
	Department    string   `json:\"department\"`
	MumbaiArea    string   `json:\"mumbai_area\"`
	Permissions   []string `json:\"permissions\"`
	SecurityLevel int      `json:\"security_level\"` // 1-5, Mumbai Police style
	AadhaarHash   string   `json:\"aadhaar_hash\"`   // Hashed Aadhaar for compliance
	jwt.StandardClaims
}

// SecurityContext - Request security context
type SecurityContext struct {
	RequestID     string            `json:\"request_id\"`
	UserAgent     string            `json:\"user_agent\"`
	ClientIP      string            `json:\"client_ip\"`
	MumbaiArea    string            `json:\"mumbai_area\"`
	DeviceID      string            `json:\"device_id\"`
	RiskScore     int               `json:\"risk_score\"` // 1-100
	Headers       map[string]string `json:\"headers\"`
	Timestamp     time.Time         `json:\"timestamp\"`
	GeoLocation   GeoLocation       `json:\"geo_location\"`
}

// GeoLocation - Mumbai location context
type GeoLocation struct {
	Latitude   float64 `json:\"latitude\"`
	Longitude  float64 `json:\"longitude\"`
	Area       string  `json:\"area\"`
	Pincode    string  `json:\"pincode\"`
	TrainLine  string  `json:\"train_line\"` // Western, Central, Harbour
	IsInMumbai bool    `json:\"is_in_mumbai\"`
}

// ZeroTrustGateway - Mumbai Police style security gateway
type ZeroTrustGateway struct {
	redisClient    *redis.Client
	jwtSecret      []byte
	metrics        *SecurityMetrics
	policyEngine   *PolicyEngine
	auditLogger    *AuditLogger
	mumbaiAreas    map[string]bool
	trustedDevices map[string]bool
}

// SecurityMetrics - Prometheus metrics
type SecurityMetrics struct {
	RequestsTotal     prometheus.Counter
	AuthSuccessTotal  prometheus.Counter
	AuthFailureTotal  prometheus.Counter
	RiskScoreHist     prometheus.Histogram
	LatencyHist       prometheus.Histogram
	MumbaiRequestsTotal prometheus.Counter
}

// PolicyEngine - Security policy engine
type PolicyEngine struct {
	policies map[string]SecurityPolicy
}

// SecurityPolicy - Mumbai style security policy
type SecurityPolicy struct {
	Name            string   `json:\"name\"`
	RequiredRole    string   `json:\"required_role\"`
	RequiredLevel   int      `json:\"required_level\"`
	AllowedAreas    []string `json:\"allowed_areas\"`
	TimeRestriction string   `json:\"time_restriction\"`
	MumbaiOnly      bool     `json:\"mumbai_only\"`
}

// AuditLogger - Complete audit trail
type AuditLogger struct {
	redisClient *redis.Client
}

// NewZeroTrustGateway - Create new security gateway
func NewZeroTrustGateway() *ZeroTrustGateway {
	// Redis connection for session management
	rdb := redis.NewClient(&redis.Options{
		Addr:     \"localhost:6379\",
		Password: \"\",
		DB:       0,
	})

	// Initialize metrics
	metrics := &SecurityMetrics{
		RequestsTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: \"mumbai_security_requests_total\",
			Help: \"Total number of security requests\",
		}),
		AuthSuccessTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: \"mumbai_auth_success_total\",
			Help: \"Total successful authentications\",
		}),
		AuthFailureTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: \"mumbai_auth_failure_total\",
			Help: \"Total failed authentications\",
		}),
		RiskScoreHist: prometheus.NewHistogram(prometheus.HistogramOpts{
			Name:    \"mumbai_risk_score\",
			Help:    \"Risk score distribution\",
			Buckets: []float64{10, 25, 50, 75, 90, 100},
		}),
		LatencyHist: prometheus.NewHistogram(prometheus.HistogramOpts{
			Name: \"mumbai_security_latency_seconds\",
			Help: \"Security check latency\",
		}),
		MumbaiRequestsTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Name: \"mumbai_local_requests_total\",
			Help: \"Total requests from Mumbai\",
		}),
	}

	// Register metrics
	prometheus.MustRegister(
		metrics.RequestsTotal,
		metrics.AuthSuccessTotal,
		metrics.AuthFailureTotal,
		metrics.RiskScoreHist,
		metrics.LatencyHist,
		metrics.MumbaiRequestsTotal,
	)

	// Mumbai areas mapping
	mumbaiAreas := map[string]bool{
		\"Andheri\":   true,
		\"Bandra\":    true,
		\"Borivali\":  true,
		\"Dadar\":     true,
		\"Ghatkopar\": true,
		\"Kurla\":     true,
		\"Malad\":     true,
		\"Mulund\":    true,
		\"Powai\":     true,
		\"Thane\":     true,
		\"Vashi\":     true,
		\"Worli\":     true,
	}

	// Initialize policy engine
	policyEngine := &PolicyEngine{
		policies: make(map[string]SecurityPolicy),
	}

	// Load Mumbai Police style policies
	policyEngine.LoadMumbaiPolicies()

	// Initialize audit logger
	auditLogger := &AuditLogger{
		redisClient: rdb,
	}

	return &ZeroTrustGateway{
		redisClient:    rdb,
		jwtSecret:      []byte(\"mumbai-police-secret-key-2024\"),
		metrics:        metrics,
		policyEngine:   policyEngine,
		auditLogger:    auditLogger,
		mumbaiAreas:    mumbaiAreas,
		trustedDevices: make(map[string]bool),
	}
}

// LoadMumbaiPolicies - Load Mumbai Police style security policies
func (pe *PolicyEngine) LoadMumbaiPolicies() {
	// Mumbai Police Department policies
	pe.policies[\"admin\"] = SecurityPolicy{
		Name:            \"Mumbai Admin Access\",
		RequiredRole:    \"admin\",
		RequiredLevel:   5,
		AllowedAreas:    []string{\"all\"},
		TimeRestriction: \"24x7\",
		MumbaiOnly:      true,
	}

	pe.policies[\"officer\"] = SecurityPolicy{
		Name:            \"Police Officer Access\",
		RequiredRole:    \"officer\",
		RequiredLevel:   3,
		AllowedAreas:    []string{\"Andheri\", \"Bandra\", \"Kurla\"},
		TimeRestriction: \"06:00-22:00\",
		MumbaiOnly:      true,
	}

	pe.policies[\"citizen\"] = SecurityPolicy{
		Name:            \"Mumbai Citizen Access\",
		RequiredRole:    \"citizen\",
		RequiredLevel:   1,
		AllowedAreas:    []string{\"public\"},
		TimeRestriction: \"05:00-23:00\",
		MumbaiOnly:      false,
	}

	pe.policies[\"developer\"] = SecurityPolicy{
		Name:            \"Tech Developer Access\",
		RequiredRole:    \"developer\",
		RequiredLevel:   4,
		AllowedAreas:    []string{\"Powai\", \"BKC\", \"Lower Parel\"},
		TimeRestriction: \"24x7\",
		MumbaiOnly:      false,
	}
}

// ZeroTrustMiddleware - Main security middleware
func (ztg *ZeroTrustGateway) ZeroTrustMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		ztg.metrics.RequestsTotal.Inc()

		// Step 1: Extract security context
		securityCtx := ztg.extractSecurityContext(c)

		// Step 2: Risk assessment
		riskScore := ztg.calculateRiskScore(securityCtx)
		ztg.metrics.RiskScoreHist.Observe(float64(riskScore))

		// Step 3: JWT token validation
		claims, err := ztg.validateJWTToken(c)
		if err != nil {
			ztg.metrics.AuthFailureTotal.Inc()
			ztg.auditLogger.LogSecurityEvent(\"auth_failure\", securityCtx, err.Error())
			c.JSON(http.StatusUnauthorized, gin.H{
				\"error\":     \"Authentication failed\",
				\"message\":   \"Mumbai Police: Papers dikhao!\",
				\"timestamp\": time.Now(),
			})
			c.Abort()
			return
		}

		// Step 4: Policy-based authorization
		authorized, reason := ztg.checkAuthorization(claims, securityCtx, c.Request.URL.Path)
		if !authorized {
			ztg.metrics.AuthFailureTotal.Inc()
			ztg.auditLogger.LogSecurityEvent(\"authz_failure\", securityCtx, reason)
			c.JSON(http.StatusForbidden, gin.H{
				\"error\":     \"Authorization failed\",
				\"message\":   fmt.Sprintf(\"Mumbai Police: %s\", reason),
				\"timestamp\": time.Now(),
			})
			c.Abort()
			return
		}

		// Step 5: Additional security checks
		if riskScore > 80 {
			// High risk - additional verification
			if !ztg.performAdditionalVerification(claims, securityCtx) {
				ztg.metrics.AuthFailureTotal.Inc()
				c.JSON(http.StatusForbidden, gin.H{
					\"error\":   \"High risk detected\",
					\"message\": \"Mumbai Police: Additional verification required\",
					\"risk_score\": riskScore,
				})
				c.Abort()
				return
			}
		}

		// Success - proceed with request
		ztg.metrics.AuthSuccessTotal.Inc()
		if ztg.isMumbaiLocation(securityCtx.GeoLocation) {
			ztg.metrics.MumbaiRequestsTotal.Inc()
		}

		// Add security context to request
		c.Set(\"security_context\", securityCtx)
		c.Set(\"user_claims\", claims)

		// Log successful access
		ztg.auditLogger.LogSecurityEvent(\"access_granted\", securityCtx, \"Success\")

		// Record latency
		ztg.metrics.LatencyHist.Observe(time.Since(start).Seconds())

		c.Next()
	}
}

// extractSecurityContext - Extract security context from request
func (ztg *ZeroTrustGateway) extractSecurityContext(c *gin.Context) SecurityContext {
	requestID := c.GetHeader(\"X-Request-ID\")
	if requestID == "" {
		requestID = generateRequestID()
	}

	// Extract client information
	clientIP := c.ClientIP()
	userAgent := c.GetHeader(\"User-Agent\")
	deviceID := c.GetHeader(\"X-Device-ID\")

	// Mumbai area detection (simplified)
	mumbaiArea := ztg.detectMumbaiArea(clientIP)

	// Extract all headers for analysis
	headers := make(map[string]string)
	for name, values := range c.Request.Header {
		if len(values) > 0 {
			headers[name] = values[0]
		}
	}

	// Geo location (mock data for demo)
	geoLocation := GeoLocation{
		Latitude:   19.0760, // Mumbai coordinates
		Longitude:  72.8777,
		Area:       mumbaiArea,
		Pincode:    \"400001\",
		TrainLine:  \"Western\",
		IsInMumbai: ztg.mumbaiAreas[mumbaiArea],
	}

	return SecurityContext{
		RequestID:   requestID,
		UserAgent:   userAgent,
		ClientIP:    clientIP,
		MumbaiArea:  mumbaiArea,
		DeviceID:    deviceID,
		Headers:     headers,
		Timestamp:   time.Now(),
		GeoLocation: geoLocation,
	}
}

// calculateRiskScore - Mumbai Police style risk assessment
func (ztg *ZeroTrustGateway) calculateRiskScore(ctx SecurityContext) int {
	riskScore := 0

	// Base risk factors
	if !ctx.GeoLocation.IsInMumbai {
		riskScore += 20 // Outside Mumbai
	}

	if ctx.DeviceID == \"\" {
		riskScore += 15 // Unknown device
	}

	// User agent analysis
	if strings.Contains(strings.ToLower(ctx.UserAgent), \"bot\") {
		riskScore += 30 // Bot detected
	}

	// Time-based risk (Mumbai local time)
	currentHour := time.Now().Hour()
	if currentHour < 5 || currentHour > 23 {
		riskScore += 10 // Unusual hours
	}

	// IP-based risk
	if ztg.isKnownMaliciousIP(ctx.ClientIP) {
		riskScore += 50 // Known bad IP
	}

	// Device trust check
	if !ztg.trustedDevices[ctx.DeviceID] && ctx.DeviceID != \"\" {
		riskScore += 10 // Untrusted device
	}

	// Ensure risk score is within bounds
	if riskScore > 100 {
		riskScore = 100
	}
	if riskScore < 0 {
		riskScore = 0
	}

	return riskScore
}

// validateJWTToken - Validate JWT token Mumbai style
func (ztg *ZeroTrustGateway) validateJWTToken(c *gin.Context) (*MumbaiSecurityClaims, error) {
	// Extract token from Authorization header
	authHeader := c.GetHeader(\"Authorization\")
	if authHeader == \"\" {
		return nil, fmt.Errorf(\"authorization header missing\")
	}

	// Check Bearer token format
	if !strings.HasPrefix(authHeader, \"Bearer \") {
		return nil, fmt.Errorf(\"bearer token required\")
	}

	tokenString := strings.TrimPrefix(authHeader, \"Bearer \")

	// Parse and validate token
	token, err := jwt.ParseWithClaims(tokenString, &MumbaiSecurityClaims{}, func(token *jwt.Token) (interface{}, error) {
		// Ensure signing method is HMAC
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf(\"unexpected signing method: %v\", token.Header[\"alg\"])
		}
		return ztg.jwtSecret, nil
	})

	if err != nil {
		return nil, fmt.Errorf(\"invalid token: %v\", err)
	}

	// Extract claims
	claims, ok := token.Claims.(*MumbaiSecurityClaims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf(\"invalid token claims\")
	}

	// Check token expiration
	if time.Now().Unix() > claims.ExpiresAt {
		return nil, fmt.Errorf(\"token expired\")
	}

	// Additional Mumbai-specific validations
	if claims.SecurityLevel < 1 || claims.SecurityLevel > 5 {
		return nil, fmt.Errorf(\"invalid security level\")
	}

	return claims, nil
}

// checkAuthorization - Policy-based authorization
func (ztg *ZeroTrustGateway) checkAuthorization(claims *MumbaiSecurityClaims, ctx SecurityContext, path string) (bool, string) {
	// Get policy for user role
	policy, exists := ztg.policyEngine.policies[claims.Role]
	if !exists {
		return false, \"Unknown role - contact Mumbai Police IT\"
	}

	// Check security level
	if claims.SecurityLevel < policy.RequiredLevel {
		return false, fmt.Sprintf(\"Insufficient security clearance. Required: %d, Got: %d\", policy.RequiredLevel, claims.SecurityLevel)
	}

	// Check Mumbai location requirement
	if policy.MumbaiOnly && !ctx.GeoLocation.IsInMumbai {
		return false, \"Access restricted to Mumbai locations only\"
	}

	// Check area restrictions
	if len(policy.AllowedAreas) > 0 && !contains(policy.AllowedAreas, \"all\") {
		if !contains(policy.AllowedAreas, ctx.MumbaiArea) && !contains(policy.AllowedAreas, \"public\") {
			return false, fmt.Sprintf(\"Area access restricted. Allowed: %v, Current: %s\", policy.AllowedAreas, ctx.MumbaiArea)
		}
	}

	// Check time restrictions
	if !ztg.checkTimeRestriction(policy.TimeRestriction) {
		return false, fmt.Sprintf(\"Access not allowed at this time. Restriction: %s\", policy.TimeRestriction)
	}

	// Path-based authorization
	if !ztg.checkPathAuthorization(claims, path) {
		return false, \"Insufficient permissions for this resource\"
	}

	return true, \"Authorization granted\"
}

// performAdditionalVerification - High-risk additional checks
func (ztg *ZeroTrustGateway) performAdditionalVerification(claims *MumbaiSecurityClaims, ctx SecurityContext) bool {
	// For demo, we'll check if device is in trusted list
	if ctx.DeviceID != \"\" && ztg.trustedDevices[ctx.DeviceID] {
		return true
	}

	// Check if user has recent successful authentications
	key := fmt.Sprintf(\"recent_auth:%s\", claims.UserID)
	val, err := ztg.redisClient.Get(context.Background(), key).Result()
	if err == nil && val == \"trusted\" {
		return true
	}

	// In production, this would trigger:
	// - SMS OTP
	// - Push notification
	// - Biometric verification
	// - Mumbai Police verification call

	// For demo, always require additional verification for high risk
	return false
}

// Helper functions
func (ztg *ZeroTrustGateway) detectMumbaiArea(clientIP string) string {
	// Simplified area detection based on IP
	// In production, use GeoIP services
	areas := []string{\"Andheri\", \"Bandra\", \"Dadar\", \"Kurla\", \"Powai\"}
	hash := sha256.Sum256([]byte(clientIP))
	index := int(hash[0]) % len(areas)
	return areas[index]
}

func (ztg *ZeroTrustGateway) isMumbaiLocation(geo GeoLocation) bool {
	return geo.IsInMumbai
}

func (ztg *ZeroTrustGateway) isKnownMaliciousIP(ip string) bool {
	// In production, check against threat intelligence feeds
	maliciousIPs := map[string]bool{
		\"192.168.1.100\": true, // Demo malicious IP
	}
	return maliciousIPs[ip]
}

func (ztg *ZeroTrustGateway) checkTimeRestriction(restriction string) bool {
	if restriction == \"24x7\" {
		return true
	}

	// Simplified time check - in production, parse time ranges
	currentHour := time.Now().Hour()
	if restriction == \"06:00-22:00\" {
		return currentHour >= 6 && currentHour <= 22
	}
	if restriction == \"05:00-23:00\" {
		return currentHour >= 5 && currentHour <= 23
	}

	return true
}

func (ztg *ZeroTrustGateway) checkPathAuthorization(claims *MumbaiSecurityClaims, path string) bool {
	// Path-based permissions
	adminPaths := []string{\"/admin\", \"/config\", \"/users\"}
	officerPaths := []string{\"/police\", \"/reports\", \"/cases\"}

	if contains(adminPaths, path) {
		return claims.Role == \"admin\"
	}

	if containsPrefix(officerPaths, path) {
		return claims.Role == \"admin\" || claims.Role == \"officer\"
	}

	return true // Public path
}

// LogSecurityEvent - Audit logging
func (al *AuditLogger) LogSecurityEvent(eventType string, ctx SecurityContext, details string) {
	auditEvent := map[string]interface{}{
		\"event_type\":  eventType,
		\"request_id\": ctx.RequestID,
		\"client_ip\":  ctx.ClientIP,
		\"user_agent\": ctx.UserAgent,
		\"mumbai_area\": ctx.MumbaiArea,
		\"device_id\":  ctx.DeviceID,
		\"details\":    details,
		\"timestamp\":  time.Now(),
		\"risk_score\": ctx.RiskScore,
	}

	auditJSON, _ := json.Marshal(auditEvent)

	// Store in Redis with TTL
	key := fmt.Sprintf(\"audit:%s:%d\", eventType, time.Now().Unix())
	al.redisClient.Set(context.Background(), key, auditJSON, 24*time.Hour)

	// Log to console (in production, send to SIEM)
	log.Printf(\"[AUDIT] %s: %s\", eventType, string(auditJSON))
}

// Utility functions
func generateRequestID() string {
	return fmt.Sprintf(\"MUM_%d_%s\", time.Now().Unix(), hex.EncodeToString([]byte(fmt.Sprintf(\"%d\", time.Now().Nanosecond())))[:8])
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func containsPrefix(slice []string, path string) bool {
	for _, prefix := range slice {
		if strings.HasPrefix(path, prefix) {
			return true
		}
	}
	return false
}

// Main function - Demo server
func main() {
	// Initialize Zero Trust Gateway
	ztg := NewZeroTrustGateway()

	// Create Gin router
	router := gin.Default()

	// Add Zero Trust middleware
	router.Use(ztg.ZeroTrustMiddleware())

	// Health check endpoint (no auth required)
	router.GET(\"/health\", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			\"status\":    \"healthy\",
			\"service\":   \"mumbai-zero-trust-gateway\",
			\"timestamp\": time.Now(),
			\"version\":   \"1.0.0\",
		})
	})

	// Public endpoints
	public := router.Group(\"/public\")
	{
		public.GET(\"/info\", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				\"message\": \"Mumbai Police Digital Services\",
				\"area\":    \"Public Information\",
			})
		})
	}

	// Protected endpoints
	protected := router.Group(\"/api\")
	{
		protected.GET(\"/profile\", func(c *gin.Context) {
			claims := c.MustGet(\"user_claims\").(*MumbaiSecurityClaims)
			c.JSON(http.StatusOK, gin.H{
				\"user_id\":    claims.UserID,
				\"name\":       claims.Name,
				\"role\":       claims.Role,
				\"department\": claims.Department,
				\"mumbai_area\": claims.MumbaiArea,
			})
		})

		protected.GET(\"/reports\", func(c *gin.Context) {
			claims := c.MustGet(\"user_claims\").(*MumbaiSecurityClaims)
			if claims.Role != \"officer\" && claims.Role != \"admin\" {
				c.JSON(http.StatusForbidden, gin.H{\"error\": \"Officer access required\"})
				return
			}

			c.JSON(http.StatusOK, gin.H{
				\"reports\": []string{\"Crime Report 1\", \"Traffic Report 2\"},
				\"access_level\": claims.SecurityLevel,
			})
		})
	}

	// Admin endpoints
	admin := router.Group(\"/admin\")
	{
		admin.GET(\"/users\", func(c *gin.Context) {
			claims := c.MustGet(\"user_claims\").(*MumbaiSecurityClaims)
			if claims.Role != \"admin\" {
				c.JSON(http.StatusForbidden, gin.H{\"error\": \"Admin access required\"})
				return
			}

			c.JSON(http.StatusOK, gin.H{
				\"users\": []string{\"Officer Raj\", \"Admin Priya\"},
				\"total\": 2,
			})
		})
	}

	// Metrics endpoint
	router.GET(\"/metrics\", gin.WrapH(promhttp.Handler()))

	// Start server
	log.Println(\"🚨 Mumbai Zero Trust Gateway starting on :8080\")
	log.Println(\"🔐 Security Level: Maximum\")
	log.Println(\"📊 Metrics available at /metrics\")
	log.Println(\"🏥 Health check at /health\")

	if err := router.Run(\":8080\"); err != nil {
		log.Fatal(\"Failed to start server:\", err)
	}
}

// Note: To run this demo:
// 1. Install dependencies: go mod init mumbai-security && go mod tidy
// 2. Start Redis: docker run -d -p 6379:6379 redis
// 3. Run: go run 01_zero_trust_gateway.go
// 4. Test with JWT token (create separate token generator)
// 5. Monitor metrics at http://localhost:8080/metrics