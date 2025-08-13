package main

/*
Service Mesh Controller
Mumbai Traffic Management System Inspired

Context:
PhonePe/Paytm जैसे financial services के लिए service mesh control plane
जैसे Mumbai traffic control center सभी signals को manage करता है

Features:
- Service discovery
- Traffic routing management  
- Health checking
- Load balancing
- Circuit breaking
*/

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/mux"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

// ServiceInstance represents a service instance
type ServiceInstance struct {
	ID       string    `json:"id"`
	Host     string    `json:"host"`
	Port     int       `json:"port"`
	Version  string    `json:"version"`
	Healthy  bool      `json:"healthy"`
	Weight   int       `json:"weight"`
	Zone     string    `json:"zone"`
	LastSeen time.Time `json:"last_seen"`
	Metadata map[string]string `json:"metadata"`
}

// TrafficPolicy represents traffic routing policy
type TrafficPolicy struct {
	ServiceName   string            `json:"service_name"`
	Strategy      string            `json:"strategy"` // round_robin, weighted, locality
	RetryPolicy   *RetryPolicy      `json:"retry_policy,omitempty"`
	CircuitBreaker *CircuitBreaker  `json:"circuit_breaker,omitempty"`
	HealthCheck   *HealthCheck     `json:"health_check,omitempty"`
	Metadata      map[string]string `json:"metadata"`
}

// RetryPolicy configuration
type RetryPolicy struct {
	MaxRetries      int           `json:"max_retries"`
	RetryTimeout    time.Duration `json:"retry_timeout"`
	BackoffStrategy string        `json:"backoff_strategy"`
	RetriableErrors []string      `json:"retriable_errors"`
}

// CircuitBreaker configuration  
type CircuitBreaker struct {
	FailureThreshold int           `json:"failure_threshold"`
	RecoveryTimeout  time.Duration `json:"recovery_timeout"`
	MonitoringPeriod time.Duration `json:"monitoring_period"`
	State           string        `json:"state"` // CLOSED, OPEN, HALF_OPEN
	FailureCount    int           `json:"failure_count"`
	LastFailureTime time.Time     `json:"last_failure_time"`
}

// HealthCheck configuration
type HealthCheck struct {
	Path     string        `json:"path"`
	Interval time.Duration `json:"interval"`
	Timeout  time.Duration `json:"timeout"`
	Healthy  int           `json:"healthy_threshold"`
	Unhealthy int          `json:"unhealthy_threshold"`
}

// MumbaiServiceMeshController - Main controller
type MumbaiServiceMeshController struct {
	services     map[string][]*ServiceInstance
	policies     map[string]*TrafficPolicy  
	mutex        sync.RWMutex
	k8sClient    kubernetes.Interface
	httpServer   *http.Server
	
	// Mumbai specific context
	peakHours    []PeakHour
	currentState TrafficState
}

// PeakHour represents Mumbai peak traffic hours
type PeakHour struct {
	Start int `json:"start"` // Hour of day (0-23)  
	End   int `json:"end"`
	Zone  string `json:"zone"`
}

// TrafficState represents current traffic conditions
type TrafficState string

const (
	TrafficNormal    TrafficState = "normal"
	TrafficPeak      TrafficState = "peak"
	TrafficJam       TrafficState = "jam"
	TrafficEmergency TrafficState = "emergency"
)

// NewMumbaiServiceMeshController creates new controller instance
func NewMumbaiServiceMeshController() *MumbaiServiceMeshController {
	// Initialize Kubernetes client
	config, err := rest.InClusterConfig()
	if err != nil {
		log.Printf("Warning: Could not create in-cluster config: %v", err)
	}
	
	var k8sClient kubernetes.Interface
	if config != nil {
		k8sClient, err = kubernetes.NewForConfig(config)
		if err != nil {
			log.Printf("Warning: Could not create Kubernetes client: %v", err)
		}
	}
	
	controller := &MumbaiServiceMeshController{
		services:  make(map[string][]*ServiceInstance),
		policies:  make(map[string]*TrafficPolicy),
		k8sClient: k8sClient,
		
		// Mumbai peak hours configuration
		peakHours: []PeakHour{
			{Start: 7, End: 11, Zone: "mumbai-west"},   // Morning rush
			{Start: 17, End: 22, Zone: "mumbai-west"},  // Evening rush  
			{Start: 12, End: 14, Zone: "mumbai-central"}, // Lunch hour
		},
		currentState: TrafficNormal,
	}
	
	// Start background processes
	go controller.startHealthChecker()
	go controller.startTrafficStateMonitor()
	
	log.Println("🚂 Mumbai Service Mesh Controller initialized")
	return controller
}

// RegisterService registers a new service instance
func (c *MumbaiServiceMeshController) RegisterService(serviceName string, instance *ServiceInstance) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	// Initialize service if not exists
	if c.services[serviceName] == nil {
		c.services[serviceName] = make([]*ServiceInstance, 0)
		
		// Create default traffic policy
		c.policies[serviceName] = &TrafficPolicy{
			ServiceName: serviceName,
			Strategy:    "weighted",
			RetryPolicy: &RetryPolicy{
				MaxRetries:      3,
				RetryTimeout:    5 * time.Second,
				BackoffStrategy: "exponential",
				RetriableErrors: []string{"5xx", "connection-failure", "timeout"},
			},
			CircuitBreaker: &CircuitBreaker{
				FailureThreshold: 5,
				RecoveryTimeout:  30 * time.Second,
				MonitoringPeriod: 60 * time.Second,
				State:           "CLOSED",
			},
			HealthCheck: &HealthCheck{
				Path:     "/health",
				Interval: 10 * time.Second,
				Timeout:  5 * time.Second,
				Healthy:  2,
				Unhealthy: 3,
			},
		}
	}
	
	// Check if instance already exists
	for i, existing := range c.services[serviceName] {
		if existing.ID == instance.ID {
			// Update existing instance
			c.services[serviceName][i] = instance
			log.Printf("📍 Updated service instance: %s/%s", serviceName, instance.ID)
			return nil
		}
	}
	
	// Add new instance
	instance.LastSeen = time.Now()
	c.services[serviceName] = append(c.services[serviceName], instance)
	
	log.Printf("✅ Registered new service instance: %s/%s (zone: %s)", 
		serviceName, instance.ID, instance.Zone)
	return nil
}

// GetHealthyInstances returns healthy instances for a service
func (c *MumbaiServiceMeshController) GetHealthyInstances(serviceName string) []*ServiceInstance {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	instances := c.services[serviceName]
	if instances == nil {
		return nil
	}
	
	var healthy []*ServiceInstance
	for _, instance := range instances {
		if instance.Healthy {
			healthy = append(healthy, instance)
		}
	}
	
	return healthy
}

// SelectInstance selects an instance based on load balancing strategy
func (c *MumbaiServiceMeshController) SelectInstance(serviceName string) (*ServiceInstance, error) {
	policy := c.policies[serviceName]
	if policy == nil {
		return nil, fmt.Errorf("no policy found for service %s", serviceName)
	}
	
	// Check circuit breaker
	if policy.CircuitBreaker != nil && policy.CircuitBreaker.State == "OPEN" {
		// Check if recovery timeout has passed
		if time.Since(policy.CircuitBreaker.LastFailureTime) > policy.CircuitBreaker.RecoveryTimeout {
			policy.CircuitBreaker.State = "HALF_OPEN"
			log.Printf("🔄 Circuit breaker half-open for %s", serviceName)
		} else {
			return nil, fmt.Errorf("circuit breaker is OPEN for service %s", serviceName)
		}
	}
	
	healthy := c.GetHealthyInstances(serviceName)
	if len(healthy) == 0 {
		return nil, fmt.Errorf("no healthy instances for service %s", serviceName)
	}
	
	// Apply Mumbai-specific routing logic
	switch c.currentState {
	case TrafficPeak:
		return c.selectForPeakTraffic(healthy), nil
	case TrafficJam:
		return c.selectForJamCondition(healthy), nil
	case TrafficEmergency:
		return c.selectForEmergency(healthy), nil
	default:
		return c.selectByStrategy(healthy, policy.Strategy), nil
	}
}

// selectForPeakTraffic - Mumbai peak hour routing
func (c *MumbaiServiceMeshController) selectForPeakTraffic(instances []*ServiceInstance) *ServiceInstance {
	// Prefer local zone instances during peak hours
	localInstances := make([]*ServiceInstance, 0)
	for _, instance := range instances {
		if instance.Zone == "mumbai-west" { // Assuming we're in west zone
			localInstances = append(localInstances, instance)
		}
	}
	
	if len(localInstances) > 0 {
		return c.selectWeightedRoundRobin(localInstances)
	}
	
	return c.selectWeightedRoundRobin(instances)
}

// selectForJamCondition - Emergency routing during traffic jams
func (c *MumbaiServiceMeshController) selectForJamCondition(instances []*ServiceInstance) *ServiceInstance {
	// Select instance with lowest response time
	if len(instances) == 0 {
		return nil
	}
	
	// For demo, just return first available
	return instances[0]
}

// selectForEmergency - Emergency service routing  
func (c *MumbaiServiceMeshController) selectForEmergency(instances []*ServiceInstance) *ServiceInstance {
	// During emergency, use highest capacity instance
	var selected *ServiceInstance
	maxWeight := 0
	
	for _, instance := range instances {
		if instance.Weight > maxWeight {
			maxWeight = instance.Weight
			selected = instance
		}
	}
	
	return selected
}

// selectByStrategy - Normal load balancing strategies
func (c *MumbaiServiceMeshController) selectByStrategy(instances []*ServiceInstance, strategy string) *ServiceInstance {
	switch strategy {
	case "weighted":
		return c.selectWeightedRoundRobin(instances)
	case "round_robin":
		return c.selectRoundRobin(instances)
	case "locality":
		return c.selectByLocality(instances)
	default:
		return c.selectWeightedRoundRobin(instances)
	}
}

// selectWeightedRoundRobin - Weighted round robin selection
func (c *MumbaiServiceMeshController) selectWeightedRoundRobin(instances []*ServiceInstance) *ServiceInstance {
	if len(instances) == 0 {
		return nil
	}
	
	// Calculate total weight
	totalWeight := 0
	for _, instance := range instances {
		totalWeight += instance.Weight
	}
	
	if totalWeight == 0 {
		return instances[0]
	}
	
	// Simple weighted selection (in production, use proper WRR algorithm)
	// For demo, just return first instance with highest weight
	var selected *ServiceInstance
	maxWeight := 0
	
	for _, instance := range instances {
		if instance.Weight > maxWeight {
			maxWeight = instance.Weight
			selected = instance
		}
	}
	
	return selected
}

// selectRoundRobin - Simple round robin selection
func (c *MumbaiServiceMeshController) selectRoundRobin(instances []*ServiceInstance) *ServiceInstance {
	if len(instances) == 0 {
		return nil
	}
	
	// Simple round robin (in production, maintain counter per service)
	return instances[0]
}

// selectByLocality - Locality-aware selection
func (c *MumbaiServiceMeshController) selectByLocality(instances []*ServiceInstance) *ServiceInstance {
	// Prefer same zone instances
	for _, instance := range instances {
		if instance.Zone == "mumbai-west" { // Our current zone
			return instance
		}
	}
	
	// Fallback to any instance
	if len(instances) > 0 {
		return instances[0]
	}
	
	return nil
}

// UpdateTrafficPolicy updates traffic policy for a service
func (c *MumbaiServiceMeshController) UpdateTrafficPolicy(serviceName string, policy *TrafficPolicy) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	c.policies[serviceName] = policy
	log.Printf("📋 Updated traffic policy for %s", serviceName)
	return nil
}

// RecordRequestResult records request result for circuit breaker
func (c *MumbaiServiceMeshController) RecordRequestResult(serviceName string, success bool) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	policy := c.policies[serviceName]
	if policy == nil || policy.CircuitBreaker == nil {
		return
	}
	
	cb := policy.CircuitBreaker
	
	if success {
		cb.FailureCount = 0
		if cb.State == "HALF_OPEN" {
			cb.State = "CLOSED"
			log.Printf("✅ Circuit breaker closed for %s", serviceName)
		}
	} else {
		cb.FailureCount++
		cb.LastFailureTime = time.Now()
		
		if cb.FailureCount >= cb.FailureThreshold {
			cb.State = "OPEN"
			log.Printf("🚫 Circuit breaker opened for %s (failures: %d)", 
				serviceName, cb.FailureCount)
		}
	}
}

// startHealthChecker starts background health checking
func (c *MumbaiServiceMeshController) startHealthChecker() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	
	for range ticker.C {
		c.performHealthChecks()
	}
}

// performHealthChecks checks health of all instances
func (c *MumbaiServiceMeshController) performHealthChecks() {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	for serviceName, instances := range c.services {
		policy := c.policies[serviceName]
		if policy == nil || policy.HealthCheck == nil {
			continue
		}
		
		for _, instance := range instances {
			go c.checkInstanceHealth(serviceName, instance, policy.HealthCheck)
		}
	}
}

// checkInstanceHealth checks health of individual instance
func (c *MumbaiServiceMeshController) checkInstanceHealth(serviceName string, instance *ServiceInstance, hc *HealthCheck) {
	client := &http.Client{Timeout: hc.Timeout}
	
	url := fmt.Sprintf("http://%s:%d%s", instance.Host, instance.Port, hc.Path)
	resp, err := client.Get(url)
	
	wasHealthy := instance.Healthy
	
	if err != nil {
		instance.Healthy = false
	} else {
		instance.Healthy = (resp.StatusCode >= 200 && resp.StatusCode < 300)
		resp.Body.Close()
	}
	
	instance.LastSeen = time.Now()
	
	// Log health status changes
	if wasHealthy != instance.Healthy {
		status := "healthy"
		if !instance.Healthy {
			status = "unhealthy"
		}
		log.Printf("🏥 Instance %s/%s changed to %s", serviceName, instance.ID, status)
	}
}

// startTrafficStateMonitor monitors Mumbai traffic conditions
func (c *MumbaiServiceMeshController) startTrafficStateMonitor() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for range ticker.C {
		c.updateTrafficState()
	}
}

// updateTrafficState updates current traffic state
func (c *MumbaiServiceMeshController) updateTrafficState() {
	currentHour := time.Now().Hour()
	
	// Check if current time is within peak hours
	isPeak := false
	for _, peak := range c.peakHours {
		if currentHour >= peak.Start && currentHour <= peak.End {
			isPeak = true
			break
		}
	}
	
	oldState := c.currentState
	
	if isPeak {
		c.currentState = TrafficPeak
	} else {
		// Check system health to determine if traffic is jammed
		totalInstances, healthyInstances := c.getSystemHealth()
		healthPercentage := float64(healthyInstances) / float64(totalInstances) * 100
		
		if healthPercentage < 70 {
			c.currentState = TrafficJam
		} else {
			c.currentState = TrafficNormal
		}
	}
	
	// Log state changes
	if oldState != c.currentState {
		log.Printf("🚦 Traffic state changed: %s -> %s", oldState, c.currentState)
	}
}

// getSystemHealth returns overall system health stats
func (c *MumbaiServiceMeshController) getSystemHealth() (total, healthy int) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	for _, instances := range c.services {
		for _, instance := range instances {
			total++
			if instance.Healthy {
				healthy++
			}
		}
	}
	
	return total, healthy
}

// SetupHTTPServer sets up HTTP API server
func (c *MumbaiServiceMeshController) SetupHTTPServer() {
	router := mux.NewRouter()
	
	// Health endpoint
	router.HandleFunc("/health", c.healthHandler).Methods("GET")
	
	// Service management endpoints
	router.HandleFunc("/services", c.listServicesHandler).Methods("GET")
	router.HandleFunc("/services/{service}/instances", c.getServiceInstancesHandler).Methods("GET")
	router.HandleFunc("/services/{service}/select", c.selectInstanceHandler).Methods("GET")
	
	// Traffic policy endpoints
	router.HandleFunc("/services/{service}/policy", c.getTrafficPolicyHandler).Methods("GET")
	router.HandleFunc("/services/{service}/policy", c.updateTrafficPolicyHandler).Methods("PUT")
	
	// Metrics endpoint
	router.HandleFunc("/metrics", c.metricsHandler).Methods("GET")
	
	c.httpServer = &http.Server{
		Addr:         ":8080",
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
	}
}

// HTTP Handlers

func (c *MumbaiServiceMeshController) healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	
	total, healthy := c.getSystemHealth()
	
	response := map[string]interface{}{
		"status":           "healthy",
		"traffic_state":    c.currentState,
		"total_instances":  total,
		"healthy_instances": healthy,
		"health_percentage": float64(healthy) / float64(total) * 100,
		"timestamp":        time.Now().Format(time.RFC3339),
	}
	
	json.NewEncoder(w).Encode(response)
}

func (c *MumbaiServiceMeshController) listServicesHandler(w http.ResponseWriter, r *http.Request) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	
	services := make(map[string]interface{})
	for serviceName, instances := range c.services {
		healthyCount := 0
		for _, instance := range instances {
			if instance.Healthy {
				healthyCount++
			}
		}
		
		services[serviceName] = map[string]interface{}{
			"total_instances":  len(instances),
			"healthy_instances": healthyCount,
			"policy":           c.policies[serviceName],
		}
	}
	
	response := map[string]interface{}{
		"services": services,
		"traffic_state": c.currentState,
		"timestamp": time.Now().Format(time.RFC3339),
	}
	
	json.NewEncoder(w).Encode(response)
}

func (c *MumbaiServiceMeshController) getServiceInstancesHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceName := vars["service"]
	
	c.mutex.RLock()
	instances := c.services[serviceName]
	c.mutex.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	
	if instances == nil {
		http.Error(w, "Service not found", http.StatusNotFound)
		return
	}
	
	response := map[string]interface{}{
		"service":   serviceName,
		"instances": instances,
		"timestamp": time.Now().Format(time.RFC3339),
	}
	
	json.NewEncoder(w).Encode(response)
}

func (c *MumbaiServiceMeshController) selectInstanceHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceName := vars["service"]
	
	instance, err := c.SelectInstance(serviceName)
	
	w.Header().Set("Content-Type", "application/json")
	
	if err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}
	
	response := map[string]interface{}{
		"selected_instance": instance,
		"selection_strategy": c.policies[serviceName].Strategy,
		"traffic_state": c.currentState,
		"timestamp": time.Now().Format(time.RFC3339),
	}
	
	json.NewEncoder(w).Encode(response)
}

func (c *MumbaiServiceMeshController) getTrafficPolicyHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceName := vars["service"]
	
	c.mutex.RLock()
	policy := c.policies[serviceName]
	c.mutex.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	
	if policy == nil {
		http.Error(w, "Policy not found", http.StatusNotFound)
		return
	}
	
	json.NewEncoder(w).Encode(policy)
}

func (c *MumbaiServiceMeshController) updateTrafficPolicyHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceName := vars["service"]
	
	var policy TrafficPolicy
	if err := json.NewDecoder(r.Body).Decode(&policy); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	
	policy.ServiceName = serviceName
	c.UpdateTrafficPolicy(serviceName, &policy)
	
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "updated"})
}

func (c *MumbaiServiceMeshController) metricsHandler(w http.ResponseWriter, r *http.Request) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	
	total, healthy := c.getSystemHealth()
	
	metrics := map[string]interface{}{
		"system_health": map[string]interface{}{
			"total_instances":     total,
			"healthy_instances":   healthy,
			"health_percentage":   float64(healthy) / float64(total) * 100,
		},
		"traffic_state": c.currentState,
		"services": len(c.services),
		"timestamp": time.Now().Format(time.RFC3339),
	}
	
	json.NewEncoder(w).Encode(metrics)
}

// StartServer starts the HTTP server
func (c *MumbaiServiceMeshController) StartServer(ctx context.Context) error {
	c.SetupHTTPServer()
	
	log.Printf("🌐 Starting Mumbai Service Mesh Controller API server on :8080")
	
	go func() {
		if err := c.httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("❌ Server error: %v", err)
		}
	}()
	
	// Wait for context cancellation
	<-ctx.Done()
	
	// Shutdown server gracefully
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	
	return c.httpServer.Shutdown(shutdownCtx)
}

// Demo function
func main() {
	fmt.Println("🚂 Mumbai Service Mesh Controller")
	fmt.Println("=" + fmt.Sprintf("%50s", "="))
	
	// Create controller
	controller := NewMumbaiServiceMeshController()
	
	// Register sample services (Zomato-style food delivery)
	fmt.Println("\n🍕 Registering food delivery services...")
	
	// Order service instances
	orderService1 := &ServiceInstance{
		ID:      "order-svc-1",
		Host:    "10.0.1.10",
		Port:    8080,
		Version: "v1",
		Healthy: true,
		Weight:  100,
		Zone:    "mumbai-west",
		Metadata: map[string]string{
			"type": "order-service",
			"env":  "production",
		},
	}
	
	orderService2 := &ServiceInstance{
		ID:      "order-svc-2", 
		Host:    "10.0.1.11",
		Port:    8080,
		Version: "v1",
		Healthy: true,
		Weight:  100,
		Zone:    "mumbai-west",
		Metadata: map[string]string{
			"type": "order-service",
			"env":  "production",
		},
	}
	
	// Register services
	controller.RegisterService("order-service", orderService1)
	controller.RegisterService("order-service", orderService2)
	
	// Payment service
	paymentService := &ServiceInstance{
		ID:      "payment-svc-1",
		Host:    "10.0.2.10",
		Port:    8081,
		Version: "v2",
		Healthy: true,
		Weight:  150,
		Zone:    "mumbai-east",
		Metadata: map[string]string{
			"type": "payment-service", 
			"env":  "production",
		},
	}
	
	controller.RegisterService("payment-service", paymentService)
	
	fmt.Printf("✅ Registered services with controller\n")
	
	// Test instance selection
	fmt.Println("\n🎯 Testing instance selection...")
	
	for i := 0; i < 5; i++ {
		instance, err := controller.SelectInstance("order-service")
		if err != nil {
			fmt.Printf("❌ Selection error: %v\n", err)
		} else {
			fmt.Printf("  📍 Selected: %s (%s:%d) zone=%s weight=%d\n", 
				instance.ID, instance.Host, instance.Port, instance.Zone, instance.Weight)
		}
		
		// Simulate request results
		success := i%3 != 0 // 67% success rate
		controller.RecordRequestResult("order-service", success)
	}
	
	// Test traffic policy update
	fmt.Println("\n📋 Updating traffic policy...")
	
	newPolicy := &TrafficPolicy{
		ServiceName: "order-service",
		Strategy:    "locality",
		RetryPolicy: &RetryPolicy{
			MaxRetries:      5,
			RetryTimeout:    10 * time.Second,
			BackoffStrategy: "exponential",
		},
		CircuitBreaker: &CircuitBreaker{
			FailureThreshold: 3, // More aggressive during peak
			RecoveryTimeout:  15 * time.Second,
			State:           "CLOSED",
		},
	}
	
	controller.UpdateTrafficPolicy("order-service", newPolicy)
	
	// Show system status
	total, healthy := controller.getSystemHealth()
	fmt.Printf("\n📊 System Health: %d/%d instances healthy (%.1f%%)\n", 
		healthy, total, float64(healthy)/float64(total)*100)
	fmt.Printf("🚦 Current traffic state: %s\n", controller.currentState)
	
	// Start HTTP server in background for demo
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	go func() {
		if err := controller.StartServer(ctx); err != nil {
			log.Printf("Server error: %v", err)
		}
	}()
	
	fmt.Println("\n🌐 HTTP API server started on :8080")
	fmt.Println("📡 Try these endpoints:")
	fmt.Println("  GET  /health")
	fmt.Println("  GET  /services")
	fmt.Println("  GET  /services/order-service/instances")
	fmt.Println("  GET  /services/order-service/select")
	fmt.Println("  GET  /metrics")
	
	// Keep running for demo
	fmt.Println("\n🚀 Controller is running... (Ctrl+C to stop)")
	select {}
}