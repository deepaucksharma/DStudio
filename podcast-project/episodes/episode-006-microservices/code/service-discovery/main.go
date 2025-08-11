package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/hashicorp/consul/api"
	"github.com/gorilla/mux"
)

// ServiceDiscovery - Consul-based service discovery like Mumbai's local train network
// जैसे Mumbai में हर station का अपना ID होता है, वैसे ही हर service का unique ID
type ServiceDiscovery struct {
	client     *api.Client
	serviceID  string
	serviceName string
	port       int
	health     *HealthChecker
}

// ServiceInfo - Service की जानकारी, जैसे train की timing और platform info
type ServiceInfo struct {
	ID      string            `json:"id"`
	Name    string            `json:"name"`
	Address string            `json:"address"`
	Port    int               `json:"port"`
	Tags    []string          `json:"tags"`
	Meta    map[string]string `json:"meta"`
	Health  string            `json:"health"`
}

// HealthChecker - Service health monitor, जैसे railway का signal system
type HealthChecker struct {
	serviceName string
	checks      []HealthCheck
}

type HealthCheck func() (bool, string)

// NewServiceDiscovery - नया service discovery client बनाता है
// Example: Zomato delivery service registration
func NewServiceDiscovery(serviceName string, port int) (*ServiceDiscovery, error) {
	config := api.DefaultConfig()
	// Production में Consul cluster का address
	if consulAddr := os.Getenv("CONSUL_ADDR"); consulAddr != "" {
		config.Address = consulAddr
	}
	
	client, err := api.NewClient(config)
	if err != nil {
		return nil, fmt.Errorf("consul client creation failed: %v", err)
	}
	
	serviceID := fmt.Sprintf("%s-%d-%d", serviceName, port, time.Now().Unix())
	
	sd := &ServiceDiscovery{
		client:      client,
		serviceID:   serviceID,
		serviceName: serviceName,
		port:        port,
		health:      NewHealthChecker(serviceName),
	}
	
	return sd, nil
}

// NewHealthChecker - Health monitoring system
func NewHealthChecker(serviceName string) *HealthChecker {
	hc := &HealthChecker{
		serviceName: serviceName,
		checks:      make([]HealthCheck, 0),
	}
	
	// Basic health check - service running hai ya nahi
	hc.AddCheck(func() (bool, string) {
		// यहाँ database connectivity, memory usage etc check करते हैं
		return true, "Service is running smoothly like Dabbawalas"
	})
	
	return hc
}

// AddCheck - नया health check add करता है
func (hc *HealthChecker) AddCheck(check HealthCheck) {
	hc.checks = append(hc.checks, check)
}

// RegisterService - Service को Consul में register करता है
// जैसे Mumbai local में नया station add करना
func (sd *ServiceDiscovery) RegisterService(tags []string, meta map[string]string) error {
	// Health check endpoint - Paytm style monitoring
	healthCheck := &api.AgentServiceCheck{
		HTTP:                           fmt.Sprintf("http://localhost:%d/health", sd.port),
		Timeout:                        "10s",
		Interval:                       "30s",
		DeregisterCriticalServiceAfter: "1m",
		Notes:                          "Health check like IRCTC server monitoring",
	}
	
	// Service registration
	service := &api.AgentServiceRegistration{
		ID:      sd.serviceID,
		Name:    sd.serviceName,
		Port:    sd.port,
		Tags:    tags,
		Meta:    meta,
		Check:   healthCheck,
		Address: getLocalIP(),
	}
	
	err := sd.client.Agent().ServiceRegister(service)
	if err != nil {
		return fmt.Errorf("service registration failed: %v", err)
	}
	
	log.Printf("Service %s registered successfully with ID: %s", sd.serviceName, sd.serviceID)
	log.Printf("Service running on port %d - Ready for traffic like Gateway of India!", sd.port)
	return nil
}

// DiscoverServices - Available services discover करता है
// जैसे Google Maps में nearby restaurants find करना
func (sd *ServiceDiscovery) DiscoverServices(serviceName string, tag string) ([]ServiceInfo, error) {
	var queryOptions *api.QueryOptions
	
	services, _, err := sd.client.Health().Service(serviceName, tag, true, queryOptions)
	if err != nil {
		return nil, fmt.Errorf("service discovery failed: %v", err)
	}
	
	var serviceList []ServiceInfo
	for _, service := range services {
		serviceInfo := ServiceInfo{
			ID:      service.Service.ID,
			Name:    service.Service.Service,
			Address: service.Service.Address,
			Port:    service.Service.Port,
			Tags:    service.Service.Tags,
			Meta:    service.Service.Meta,
			Health:  getHealthStatus(service.Checks),
		}
		serviceList = append(serviceList, serviceInfo)
	}
	
	log.Printf("Discovered %d instances of %s service - Like finding all Vada Pav stalls in Dadar!", 
		len(serviceList), serviceName)
	return serviceList, nil
}

// getHealthStatus - Service health determine करता है
func getHealthStatus(checks api.HealthChecks) string {
	for _, check := range checks {
		if check.Status != api.HealthPassing {
			return "unhealthy"
		}
	}
	return "healthy"
}

// LoadBalancer - Simple round-robin load balancer
// जैसे auto rickshaw queue में next available rickshaw लेना
type LoadBalancer struct {
	services []ServiceInfo
	current  int
}

// GetNextService - Next available service return करता है
func (lb *LoadBalancer) GetNextService() *ServiceInfo {
	if len(lb.services) == 0 {
		return nil
	}
	
	// Round-robin selection like Mumbai local train coaches
	service := &lb.services[lb.current]
	lb.current = (lb.current + 1) % len(lb.services)
	
	return service
}

// UpdateServices - Service list update करता है
func (lb *LoadBalancer) UpdateServices(services []ServiceInfo) {
	lb.services = services
	lb.current = 0
	log.Printf("Load balancer updated with %d services", len(services))
}

// HTTP Handlers

// healthHandler - Health check endpoint
func (sd *ServiceDiscovery) healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	
	// सभी health checks run करते हैं
	allHealthy := true
	var results []map[string]interface{}
	
	for _, check := range sd.health.checks {
		healthy, message := check()
		if !healthy {
			allHealthy = false
		}
		
		results = append(results, map[string]interface{}{
			"healthy": healthy,
			"message": message,
		})
	}
	
	status := "healthy"
	if !allHealthy {
		status = "unhealthy"
		w.WriteHeader(http.StatusServiceUnavailable)
	}
	
	response := map[string]interface{}{
		"service":   sd.serviceName,
		"status":    status,
		"checks":    results,
		"timestamp": time.Now().Format(time.RFC3339),
		"message":   "Service health like Mumbai's resilient spirit!",
	}
	
	json.NewEncoder(w).Encode(response)
}

// serviceDiscoveryHandler - Available services list करता है
func (sd *ServiceDiscovery) serviceDiscoveryHandler(w http.ResponseWriter, r *http.Request) {
	serviceName := r.URL.Query().Get("service")
	tag := r.URL.Query().Get("tag")
	
	if serviceName == "" {
		http.Error(w, "service parameter required", http.StatusBadRequest)
		return
	}
	
	services, err := sd.DiscoverServices(serviceName, tag)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"services": services,
		"count":    len(services),
		"message":  "Services discovered faster than finding good street food in Mumbai!",
	})
}

// getLocalIP - Local IP address get करता है
func getLocalIP() string {
	// Simple implementation - production में proper network interface detection
	return "127.0.0.1"
}

// Graceful shutdown handler
func (sd *ServiceDiscovery) gracefulShutdown() {
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	
	<-c
	log.Println("Shutting down service gracefully...")
	
	// Service को Consul से deregister करते हैं
	err := sd.client.Agent().ServiceDeregister(sd.serviceID)
	if err != nil {
		log.Printf("Error deregistering service: %v", err)
	} else {
		log.Println("Service deregistered successfully")
	}
	
	os.Exit(0)
}

func main() {
	// Environment variables
	serviceName := os.Getenv("SERVICE_NAME")
	if serviceName == "" {
		serviceName = "zomato-delivery-service"
	}
	
	port := 8080
	if portStr := os.Getenv("PORT"); portStr != "" {
		fmt.Sscanf(portStr, "%d", &port)
	}
	
	// Service discovery initialize करते हैं
	sd, err := NewServiceDiscovery(serviceName, port)
	if err != nil {
		log.Fatal("Failed to initialize service discovery:", err)
	}
	
	// Additional health checks add करते हैं
	sd.health.AddCheck(func() (bool, string) {
		// Database connection check
		// यहाँ actual database ping करेंगे
		return true, "Database connection healthy like Marine Drive sea breeze"
	})
	
	sd.health.AddCheck(func() (bool, string) {
		// Memory usage check
		// Production में actual memory stats check करेंगे
		return true, "Memory usage optimal like efficient Mumbai traffic management"
	})
	
	// HTTP server setup
	router := mux.NewRouter()
	router.HandleFunc("/health", sd.healthHandler).Methods("GET")
	router.HandleFunc("/discover", sd.serviceDiscoveryHandler).Methods("GET")
	
	// Sample business endpoint
	router.HandleFunc("/api/orders", func(w http.ResponseWriter, r *http.Request) {
		response := map[string]interface{}{
			"message": "Order service ready - Fast like Mumbai Dabbawalas!",
			"service": serviceName,
			"port":    port,
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	}).Methods("GET")
	
	// Service register करते हैं
	tags := []string{"microservice", "api", "production"}
	meta := map[string]string{
		"version":     "1.0.0",
		"region":      "mumbai-west",
		"cost_center": "engineering",
		"team":        "platform",
	}
	
	err = sd.RegisterService(tags, meta)
	if err != nil {
		log.Fatal("Failed to register service:", err)
	}
	
	// Graceful shutdown setup
	go sd.gracefulShutdown()
	
	// Server start करते हैं
	log.Printf("Starting %s on port %d", serviceName, port)
	log.Printf("Health check endpoint: http://localhost:%d/health", port)
	log.Printf("Service discovery endpoint: http://localhost:%d/discover", port)
	
	server := &http.Server{
		Addr:    fmt.Sprintf(":%d", port),
		Handler: router,
		// Production timeouts
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  60 * time.Second,
	}
	
	if err := server.ListenAndServe(); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}