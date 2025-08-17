/*
🇮🇳 Geographic Load Balancer - Ola Cab Style
User location के basis पर nearest cabs assign करने जैसा

Features:
- Geographic proximity-based routing
- Latency-aware load balancing
- Multi-region support
- Ola cab geographic distribution
- Distance calculation algorithms
- Failover across regions
- Hindi comments

Author: Agent 5 - Code Developer
Episode: 27 - Load Balancing
Context: Ola cab geographic distribution system
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
	"sort"
	"sync"
	"time"
)

// GeoLocation represents geographic coordinates
type GeoLocation struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	City      string  `json:"city"`
	State     string  `json:"state"`
	Country   string  `json:"country"`
}

// CalculateDistance calculates distance between two geo locations (in km)
func (g *GeoLocation) CalculateDistance(other *GeoLocation) float64 {
	const earthRadius = 6371 // Earth radius in kilometers

	lat1Rad := g.Latitude * math.Pi / 180
	lon1Rad := g.Longitude * math.Pi / 180
	lat2Rad := other.Latitude * math.Pi / 180
	lon2Rad := other.Longitude * math.Pi / 180

	deltaLat := lat2Rad - lat1Rad
	deltaLon := lon2Rad - lon1Rad

	a := math.Sin(deltaLat/2)*math.Sin(deltaLat/2) +
		math.Cos(lat1Rad)*math.Cos(lat2Rad)*
			math.Sin(deltaLon/2)*math.Sin(deltaLon/2)

	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	distance := earthRadius * c

	return distance
}

// CabService represents a backend service in specific location
type CabService struct {
	ID               string            `json:"id"`
	URL              *url.URL          `json:"url"`
	Location         *GeoLocation      `json:"location"`
	Zone             string            `json:"zone"`
	Region           string            `json:"region"`
	IsHealthy        bool              `json:"is_healthy"`
	Capacity         int               `json:"capacity"`
	CurrentLoad      int               `json:"current_load"`
	AverageLatency   time.Duration     `json:"average_latency"`
	TotalRequests    uint64            `json:"total_requests"`
	Metadata         map[string]string `json:"metadata"`
	LastHealthCheck  time.Time         `json:"last_health_check"`
	mutex            sync.RWMutex      `json:"-"`
}

// NewCabService creates a new cab service
func NewCabService(id, urlStr string, location *GeoLocation, capacity int) *CabService {
	url, err := url.Parse(urlStr)
	if err != nil {
		panic(fmt.Sprintf("Invalid URL: %s", urlStr))
	}

	return &CabService{
		ID:              id,
		URL:             url,
		Location:        location,
		Zone:            location.City,
		Region:          location.State,
		IsHealthy:       true,
		Capacity:        capacity,
		CurrentLoad:     0,
		AverageLatency:  time.Duration(0),
		Metadata:        make(map[string]string),
		LastHealthCheck: time.Now(),
	}
}

// IsAvailable checks if service can handle more requests
func (cs *CabService) IsAvailable() bool {
	cs.mutex.RLock()
	defer cs.mutex.RUnlock()

	return cs.IsHealthy && cs.CurrentLoad < cs.Capacity
}

// GetLoadPercentage returns current load as percentage
func (cs *CabService) GetLoadPercentage() float64 {
	cs.mutex.RLock()
	defer cs.mutex.RUnlock()

	if cs.Capacity == 0 {
		return 100.0
	}
	return float64(cs.CurrentLoad) / float64(cs.Capacity) * 100
}

// UpdateHealth updates service health and metrics
func (cs *CabService) UpdateHealth(healthy bool, latency time.Duration) {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()

	cs.IsHealthy = healthy
	cs.LastHealthCheck = time.Now()

	if healthy {
		// Update average latency using exponential moving average
		if cs.AverageLatency == 0 {
			cs.AverageLatency = latency
		} else {
			cs.AverageLatency = time.Duration(
				0.8*float64(cs.AverageLatency) + 0.2*float64(latency),
			)
		}
	}

	status := "🟢 Available"
	if !healthy {
		status = "🔴 Unavailable"
	}
	log.Printf("🚗 Cab service %s (%s) status: %s (load: %.1f%%, latency: %v)",
		cs.ID, cs.Zone, status, cs.GetLoadPercentage(), cs.AverageLatency)
}

// IncrementLoad increments current load
func (cs *CabService) IncrementLoad() {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()
	cs.CurrentLoad++
	cs.TotalRequests++
}

// DecrementLoad decrements current load
func (cs *CabService) DecrementLoad() {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()
	if cs.CurrentLoad > 0 {
		cs.CurrentLoad--
	}
}

// GetStats returns service statistics
func (cs *CabService) GetStats() map[string]interface{} {
	cs.mutex.RLock()
	defer cs.mutex.RUnlock()

	return map[string]interface{}{
		"id":               cs.ID,
		"zone":             cs.Zone,
		"region":           cs.Region,
		"is_healthy":       cs.IsHealthy,
		"capacity":         cs.Capacity,
		"current_load":     cs.CurrentLoad,
		"load_percentage":  cs.GetLoadPercentage(),
		"average_latency":  cs.AverageLatency.Milliseconds(),
		"total_requests":   cs.TotalRequests,
		"location":         cs.Location,
		"last_health_check": cs.LastHealthCheck,
	}
}

// ServiceWithDistance represents a service with calculated distance
type ServiceWithDistance struct {
	Service  *CabService `json:"service"`
	Distance float64     `json:"distance"`
	Score    float64     `json:"score"`
}

// OlaLoadBalancer implements geographic load balancing
type OlaLoadBalancer struct {
	services      []*CabService       `json:"services"`
	servicesByZone map[string][]*CabService `json:"-"`
	servicesByRegion map[string][]*CabService `json:"-"`
	healthChecker *GeoHealthChecker   `json:"-"`
	mutex         sync.RWMutex        `json:"-"`
}

// NewOlaLoadBalancer creates a new geographic load balancer
func NewOlaLoadBalancer() *OlaLoadBalancer {
	lb := &OlaLoadBalancer{
		services:         make([]*CabService, 0),
		servicesByZone:   make(map[string][]*CabService),
		servicesByRegion: make(map[string][]*CabService),
	}

	// Start health checker
	lb.healthChecker = NewGeoHealthChecker(lb, 20*time.Second, 5*time.Second)
	lb.healthChecker.Start()

	return lb
}

// AddService adds a cab service to the load balancer
func (lb *OlaLoadBalancer) AddService(service *CabService) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	lb.services = append(lb.services, service)

	// Add to zone map
	if lb.servicesByZone[service.Zone] == nil {
		lb.servicesByZone[service.Zone] = make([]*CabService, 0)
	}
	lb.servicesByZone[service.Zone] = append(lb.servicesByZone[service.Zone], service)

	// Add to region map
	if lb.servicesByRegion[service.Region] == nil {
		lb.servicesByRegion[service.Region] = make([]*CabService, 0)
	}
	lb.servicesByRegion[service.Region] = append(lb.servicesByRegion[service.Region], service)

	log.Printf("✅ Cab service added: %s in %s, %s",
		service.ID, service.Zone, service.Region)
}

// RemoveService removes a service from the load balancer
func (lb *OlaLoadBalancer) RemoveService(serviceID string) error {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	// Find and remove from main list
	serviceIndex := -1
	var removedService *CabService

	for i, service := range lb.services {
		if service.ID == serviceID {
			serviceIndex = i
			removedService = service
			break
		}
	}

	if serviceIndex == -1 {
		return fmt.Errorf("service not found: %s", serviceID)
	}

	// Remove from main list
	lb.services = append(lb.services[:serviceIndex], lb.services[serviceIndex+1:]...)

	// Remove from zone map
	zoneServices := lb.servicesByZone[removedService.Zone]
	for i, service := range zoneServices {
		if service.ID == serviceID {
			lb.servicesByZone[removedService.Zone] = append(
				zoneServices[:i], zoneServices[i+1:]...)
			break
		}
	}

	// Remove from region map
	regionServices := lb.servicesByRegion[removedService.Region]
	for i, service := range regionServices {
		if service.ID == serviceID {
			lb.servicesByRegion[removedService.Region] = append(
				regionServices[:i], regionServices[i+1:]...)
			break
		}
	}

	log.Printf("🗑️ Cab service removed: %s", serviceID)
	return nil
}

// GetNearestService returns the nearest available service to user location
func (lb *OlaLoadBalancer) GetNearestService(userLocation *GeoLocation) (*CabService, error) {
	services, err := lb.GetNearestServices(userLocation, 1)
	if err != nil {
		return nil, err
	}

	if len(services) > 0 {
		return services[0].Service, nil
	}

	return nil, errors.New("no services available")
}

// GetNearestServices returns multiple nearest services sorted by score
func (lb *OlaLoadBalancer) GetNearestServices(userLocation *GeoLocation, count int) ([]ServiceWithDistance, error) {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	if len(lb.services) == 0 {
		return nil, errors.New("no services available")
	}

	servicesWithDistance := make([]ServiceWithDistance, 0)

	for _, service := range lb.services {
		if !service.IsAvailable() {
			continue
		}

		distance := userLocation.CalculateDistance(service.Location)
		score := lb.calculateServiceScore(service, distance)

		servicesWithDistance = append(servicesWithDistance, ServiceWithDistance{
			Service:  service,
			Distance: distance,
			Score:    score,
		})
	}

	if len(servicesWithDistance) == 0 {
		return nil, errors.New("no available services found")
	}

	// Sort by score (higher is better)
	sort.Slice(servicesWithDistance, func(i, j int) bool {
		return servicesWithDistance[i].Score > servicesWithDistance[j].Score
	})

	// Return top N services
	if count > len(servicesWithDistance) {
		count = len(servicesWithDistance)
	}

	result := servicesWithDistance[:count]

	log.Printf("🎯 Found %d nearest services for location (%s)",
		len(result), userLocation.City)

	return result, nil
}

// calculateServiceScore calculates service selection score
func (lb *OlaLoadBalancer) calculateServiceScore(service *CabService, distance float64) float64 {
	// Base score starts at 100
	score := 100.0

	// Distance penalty (exponential decay)
	distancePenalty := math.Exp(-distance / 50) * 40 // 50km half-life
	score *= distancePenalty / 40

	// Load penalty (more load = lower score)
	loadPercentage := service.GetLoadPercentage()
	loadBonus := (100 - loadPercentage) / 100
	score *= loadBonus

	// Latency penalty
	latencyMs := float64(service.AverageLatency.Milliseconds())
	if latencyMs > 0 {
		latencyBonus := math.Max(0.1, 1.0-latencyMs/1000) // 1 second baseline
		score *= latencyBonus
	}

	// Capacity bonus (higher capacity = higher score)
	capacityBonus := math.Log(float64(service.Capacity+1)) / 10
	score += capacityBonus

	return score
}

// GetServicesByZone returns all available services in a specific zone
func (lb *OlaLoadBalancer) GetServicesByZone(zone string) []*CabService {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	availableServices := make([]*CabService, 0)
	if services, exists := lb.servicesByZone[zone]; exists {
		for _, service := range services {
			if service.IsAvailable() {
				availableServices = append(availableServices, service)
			}
		}
	}

	return availableServices
}

// GetServicesByRegion returns all available services in a specific region
func (lb *OlaLoadBalancer) GetServicesByRegion(region string) []*CabService {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	availableServices := make([]*CabService, 0)
	if services, exists := lb.servicesByRegion[region]; exists {
		for _, service := range services {
			if service.IsAvailable() {
				availableServices = append(availableServices, service)
			}
		}
	}

	return availableServices
}

// GetGeographicStats returns comprehensive geographic statistics
func (lb *OlaLoadBalancer) GetGeographicStats() map[string]interface{} {
	lb.mutex.RLock()
	defer lb.mutex.RUnlock()

	totalServices := len(lb.services)
	availableServices := 0
	zoneStats := make(map[string]interface{})
	regionStats := make(map[string]interface{})

	// Calculate zone statistics
	for zone, services := range lb.servicesByZone {
		available := 0
		totalCapacity := 0
		totalLoad := 0

		for _, service := range services {
			totalCapacity += service.Capacity
			totalLoad += service.CurrentLoad
			if service.IsAvailable() {
				available++
				availableServices++
			}
		}

		zoneStats[zone] = map[string]interface{}{
			"total_services":     len(services),
			"available_services": available,
			"total_capacity":     totalCapacity,
			"current_load":       totalLoad,
			"load_percentage":    float64(totalLoad) / float64(totalCapacity) * 100,
		}
	}

	// Calculate region statistics
	for region, services := range lb.servicesByRegion {
		available := 0
		totalCapacity := 0
		totalLoad := 0

		for _, service := range services {
			totalCapacity += service.Capacity
			totalLoad += service.CurrentLoad
			if service.IsAvailable() {
				available++
			}
		}

		regionStats[region] = map[string]interface{}{
			"total_services":     len(services),
			"available_services": available,
			"total_capacity":     totalCapacity,
			"current_load":       totalLoad,
			"load_percentage":    float64(totalLoad) / float64(totalCapacity) * 100,
		}
	}

	return map[string]interface{}{
		"total_services":     totalServices,
		"available_services": availableServices,
		"zone_stats":         zoneStats,
		"region_stats":       regionStats,
	}
}

// GeoHealthChecker performs health checks on geographic services
type GeoHealthChecker struct {
	loadBalancer *OlaLoadBalancer
	interval     time.Duration
	timeout      time.Duration
	ctx          context.Context
	cancel       context.CancelFunc
}

// NewGeoHealthChecker creates a new geographic health checker
func NewGeoHealthChecker(lb *OlaLoadBalancer, interval, timeout time.Duration) *GeoHealthChecker {
	ctx, cancel := context.WithCancel(context.Background())
	return &GeoHealthChecker{
		loadBalancer: lb,
		interval:     interval,
		timeout:      timeout,
		ctx:          ctx,
		cancel:       cancel,
	}
}

// Start begins health checking
func (ghc *GeoHealthChecker) Start() {
	go ghc.healthCheckLoop()
	log.Printf("🔍 Geographic health checker started (interval: %v)", ghc.interval)
}

// Stop stops health checking
func (ghc *GeoHealthChecker) Stop() {
	ghc.cancel()
	log.Printf("🛑 Geographic health checker stopped")
}

// healthCheckLoop performs periodic health checks
func (ghc *GeoHealthChecker) healthCheckLoop() {
	ticker := time.NewTicker(ghc.interval)
	defer ticker.Stop()

	for {
		select {
		case <-ghc.ctx.Done():
			return
		case <-ticker.C:
			ghc.checkAllServices()
		}
	}
}

// checkAllServices checks health of all services
func (ghc *GeoHealthChecker) checkAllServices() {
	ghc.loadBalancer.mutex.RLock()
	services := make([]*CabService, len(ghc.loadBalancer.services))
	copy(services, ghc.loadBalancer.services)
	ghc.loadBalancer.mutex.RUnlock()

	var wg sync.WaitGroup
	for _, service := range services {
		wg.Add(1)
		go func(s *CabService) {
			defer wg.Done()
			ghc.checkServiceHealth(s)
		}(service)
	}
	wg.Wait()
}

// checkServiceHealth checks health of a single service
func (ghc *GeoHealthChecker) checkServiceHealth(service *CabService) {
	ctx, cancel := context.WithTimeout(ghc.ctx, ghc.timeout)
	defer cancel()

	startTime := time.Now()
	healthURL := fmt.Sprintf("%s/health", service.URL.String())

	req, err := http.NewRequestWithContext(ctx, "GET", healthURL, nil)
	if err != nil {
		service.UpdateHealth(false, time.Since(startTime))
		return
	}

	client := &http.Client{Timeout: ghc.timeout}
	resp, err := client.Do(req)
	responseTime := time.Since(startTime)

	if err != nil {
		service.UpdateHealth(false, responseTime)
		return
	}
	defer resp.Body.Close()

	isHealthy := resp.StatusCode >= 200 && resp.StatusCode < 300
	service.UpdateHealth(isHealthy, responseTime)
}

// OlaProxy implements HTTP proxy with geographic load balancing
type OlaProxy struct {
	loadBalancer *OlaLoadBalancer
}

// NewOlaProxy creates a new proxy
func NewOlaProxy(lb *OlaLoadBalancer) *OlaProxy {
	return &OlaProxy{
		loadBalancer: lb,
	}
}

// ServeHTTP implements http.Handler interface
func (p *OlaProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Extract user location from headers or query params
	lat := r.Header.Get("X-User-Latitude")
	lon := r.Header.Get("X-User-Longitude")
	city := r.Header.Get("X-User-City")

	if lat == "" || lon == "" {
		http.Error(w, "User location required", http.StatusBadRequest)
		return
	}

	// Parse coordinates
	latitude, err := strconv.ParseFloat(lat, 64)
	if err != nil {
		http.Error(w, "Invalid latitude", http.StatusBadRequest)
		return
	}

	longitude, err := strconv.ParseFloat(lon, 64)
	if err != nil {
		http.Error(w, "Invalid longitude", http.StatusBadRequest)
		return
	}

	userLocation := &GeoLocation{
		Latitude:  latitude,
		Longitude: longitude,
		City:      city,
	}

	// Get nearest service
	service, err := p.loadBalancer.GetNearestService(userLocation)
	if err != nil {
		log.Printf("❌ No services available for location %s: %v", city, err)
		http.Error(w, "No services available in your area", http.StatusServiceUnavailable)
		return
	}

	// Calculate distance for logging
	distance := userLocation.CalculateDistance(service.Location)

	// Increment load
	service.IncrementLoad()
	defer service.DecrementLoad()

	// Create reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(service.URL)

	// Add custom headers
	r.Header.Set("X-Forwarded-Service", service.ID)
	r.Header.Set("X-Forwarded-Zone", service.Zone)
	r.Header.Set("X-Forwarded-Region", service.Region)
	r.Header.Set("X-Service-Distance", fmt.Sprintf("%.2f", distance))

	// Log request routing
	log.Printf("🔀 Routing request from %s to service %s (distance: %.2f km)",
		userLocation.City, service.ID, distance)

	// Proxy the request
	proxy.ServeHTTP(w, r)
}

// Stop gracefully shuts down the proxy
func (p *OlaProxy) Stop() {
	if p.loadBalancer.healthChecker != nil {
		p.loadBalancer.healthChecker.Stop()
	}
}

// Indian city locations for demo
var indianCities = map[string]*GeoLocation{
	"mumbai": {
		Latitude: 19.0760, Longitude: 72.8777,
		City: "Mumbai", State: "Maharashtra", Country: "India",
	},
	"delhi": {
		Latitude: 28.7041, Longitude: 77.1025,
		City: "Delhi", State: "Delhi", Country: "India",
	},
	"bangalore": {
		Latitude: 12.9716, Longitude: 77.5946,
		City: "Bangalore", State: "Karnataka", Country: "India",
	},
	"hyderabad": {
		Latitude: 17.3850, Longitude: 78.4867,
		City: "Hyderabad", State: "Telangana", Country: "India",
	},
	"chennai": {
		Latitude: 13.0827, Longitude: 80.2707,
		City: "Chennai", State: "Tamil Nadu", Country: "India",
	},
	"pune": {
		Latitude: 18.5204, Longitude: 73.8567,
		City: "Pune", State: "Maharashtra", Country: "India",
	},
}

// Example usage and demo
func main() {
	// Create Ola geographic load balancer
	lb := NewOlaLoadBalancer()

	// Add cab services across Indian cities
	services := []*CabService{
		NewCabService(
			"ola-mumbai-bandra",
			"http://localhost:8081",
			indianCities["mumbai"],
			150,
		),
		NewCabService(
			"ola-mumbai-andheri",
			"http://localhost:8082",
			&GeoLocation{19.1136, 72.8697, "Andheri", "Maharashtra", "India"},
			120,
		),
		NewCabService(
			"ola-delhi-connaught",
			"http://localhost:8083",
			indianCities["delhi"],
			200,
		),
		NewCabService(
			"ola-bangalore-koramangala",
			"http://localhost:8084",
			indianCities["bangalore"],
			180,
		),
		NewCabService(
			"ola-pune-deccan",
			"http://localhost:8085",
			indianCities["pune"],
			100,
		),
		NewCabService(
			"ola-hyderabad-hitec",
			"http://localhost:8086",
			indianCities["hyderabad"],
			160,
		),
	}

	// Add metadata to services
	services[0].Metadata["type"] = "premium"
	services[1].Metadata["type"] = "standard"
	services[2].Metadata["type"] = "premium"
	services[3].Metadata["type"] = "premium"
	services[4].Metadata["type"] = "standard"
	services[5].Metadata["type"] = "premium"

	// Add services to load balancer
	for _, service := range services {
		lb.AddService(service)
	}

	// Create proxy
	proxy := NewOlaProxy(lb)
	defer proxy.Stop()

	// Demo: Show geographic load balancing behavior
	fmt.Println("\n🚗 Ola Geographic Load Balancer Demo")
	fmt.Println("===================================")

	// Test user in Mumbai
	mumbaiUser := &GeoLocation{19.0896, 72.8656, "Powai", "Maharashtra", "India"}
	fmt.Println("\n1. 🗺️ User in Mumbai Powai requesting cab:")
	nearestServices, err := lb.GetNearestServices(mumbaiUser, 3)
	if err != nil {
		fmt.Printf("   ❌ Error: %v\n", err)
	} else {
		for i, swd := range nearestServices {
			fmt.Printf("   %d. %s (%.2f km, score: %.2f)\n",
				i+1, swd.Service.ID, swd.Distance, swd.Score)
		}
	}

	// Test user in Bangalore
	bangaloreUser := &GeoLocation{12.9355, 77.6245, "Whitefield", "Karnataka", "India"}
	fmt.Println("\n2. 🗺️ User in Bangalore Whitefield requesting cab:")
	nearestServices, err = lb.GetNearestServices(bangaloreUser, 3)
	if err != nil {
		fmt.Printf("   ❌ Error: %v\n", err)
	} else {
		for i, swd := range nearestServices {
			fmt.Printf("   %d. %s (%.2f km, score: %.2f)\n",
				i+1, swd.Service.ID, swd.Distance, swd.Score)
		}
	}

	fmt.Println("\n3. 🌍 Geographic statistics:")
	stats := lb.GetGeographicStats()
	fmt.Printf("   🚗 Total services: %d\n", stats["total_services"])
	fmt.Printf("   💚 Available services: %d\n", stats["available_services"])

	fmt.Println("\n4. 🏙️ Zone-wise distribution:")
	zoneStats := stats["zone_stats"].(map[string]interface{})
	for zone, zoneData := range zoneStats {
		data := zoneData.(map[string]interface{})
		fmt.Printf("   🏙️ %s: %d/%d available (%.1f%% load)\n",
			zone, data["available_services"], data["total_services"],
			data["load_percentage"])
	}

	fmt.Println("\n5. 🗺️ Region-wise distribution:")
	regionStats := stats["region_stats"].(map[string]interface{})
	for region, regionData := range regionStats {
		data := regionData.(map[string]interface{})
		fmt.Printf("   🗺️ %s: %d/%d available (%.1f%% load)\n",
			region, data["available_services"], data["total_services"],
			data["load_percentage"])
	}

	fmt.Println("\n6. 🔧 Testing service in specific zones:")
	mumbaiServices := lb.GetServicesByZone("Mumbai")
	fmt.Printf("   Mumbai services: %d available\n", len(mumbaiServices))
	for _, service := range mumbaiServices {
		fmt.Printf("   🚗 %s (load: %.1f%%)\n", service.ID, service.GetLoadPercentage())
	}

	fmt.Println("\n7. 📊 Distance calculations:")
	fmt.Printf("   Mumbai to Delhi: %.2f km\n",
		indianCities["mumbai"].CalculateDistance(indianCities["delhi"]))
	fmt.Printf("   Mumbai to Pune: %.2f km\n",
		indianCities["mumbai"].CalculateDistance(indianCities["pune"]))
	fmt.Printf("   Bangalore to Chennai: %.2f km\n",
		indianCities["bangalore"].CalculateDistance(indianCities["chennai"]))

	// Start HTTP server for demo
	fmt.Println("\n🌐 Starting HTTP proxy server on :8080")
	fmt.Println("📝 Test with headers:")
	fmt.Println("   curl -H \"X-User-Latitude: 19.0760\" -H \"X-User-Longitude: 72.8777\" -H \"X-User-City: Mumbai\" http://localhost:8080/api/book-cab")
	fmt.Println("🔍 Health checks running every 20 seconds")
	fmt.Println("🛑 Press Ctrl+C to stop")

	// Geographic stats endpoint
	http.HandleFunc("/geo-stats", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		stats := lb.GetGeographicStats()
		json.NewEncoder(w).Encode(stats)
	})

	server := &http.Server{
		Addr:    ":8080",
		Handler: proxy,
	}

	log.Fatal(server.ListenAndServe())
}