package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"math/rand"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

/*
Load Balancing Algorithms for Distributed Systems
जैसे कि Jio के network traffic distribution में use होता है

यह example दिखाता है कि कैसे different load balancing algorithms
work करते हैं distributed systems में। Indian telecom companies
जैसे Jio, Airtel इसे use करती हैं millions of users के traffic को
efficiently distribute करने के लिए।

Production context: Jio handles 400M+ users with distributed load balancing
Scale: Traffic distributed across thousands of servers nationwide
Challenge: Maintaining low latency while handling massive concurrent load
*/

// Server represents a backend server in the load balancer pool
type Server struct {
	ID              string
	Host            string
	Port            int
	Weight          int
	IsHealthy       bool
	CurrentLoad     int64
	TotalRequests   int64
	SuccessRequests int64
	FailedRequests  int64
	AvgResponseTime time.Duration
	LastHealthCheck time.Time
	Capacity        int64
	CPUUsage        float64
	MemoryUsage     float64
	NetworkLatency  time.Duration
	Region          string
	Zone            string
	Mutex           sync.RWMutex
}

// NewServer creates a new server instance
func NewServer(id, host string, port, weight int, capacity int64, region, zone string) *Server {
	return &Server{
		ID:              id,
		Host:            host,
		Port:            port,
		Weight:          weight,
		IsHealthy:       true,
		Capacity:        capacity,
		Region:          region,
		Zone:            zone,
		LastHealthCheck: time.Now(),
		AvgResponseTime: time.Duration(50 + rand.Intn(100)) * time.Millisecond, // 50-150ms baseline
	}
}

// HandleRequest simulates processing a request on this server
func (s *Server) HandleRequest() (bool, time.Duration) {
	s.Mutex.Lock()
	defer s.Mutex.Unlock()
	
	if !s.IsHealthy {
		atomic.AddInt64(&s.FailedRequests, 1)
		return false, 0
	}
	
	// Check capacity
	if atomic.LoadInt64(&s.CurrentLoad) >= s.Capacity {
		atomic.AddInt64(&s.FailedRequests, 1)
		return false, 0
	}
	
	// Simulate request processing
	atomic.AddInt64(&s.CurrentLoad, 1)
	atomic.AddInt64(&s.TotalRequests, 1)
	
	// Simulate processing time based on current load
	loadFactor := float64(s.CurrentLoad) / float64(s.Capacity)
	processingTime := time.Duration(float64(s.AvgResponseTime) * (1 + loadFactor))
	
	// Simulate actual processing delay
	go func() {
		time.Sleep(processingTime)
		atomic.AddInt64(&s.CurrentLoad, -1)
	}()
	
	// Simulate success/failure (95% success rate when healthy)
	success := rand.Float64() > 0.05
	if success {
		atomic.AddInt64(&s.SuccessRequests, 1)
	} else {
		atomic.AddInt64(&s.FailedRequests, 1)
	}
	
	return success, processingTime
}

// GetStats returns current server statistics
func (s *Server) GetStats() ServerStats {
	s.Mutex.RLock()
	defer s.Mutex.RUnlock()
	
	total := atomic.LoadInt64(&s.TotalRequests)
	success := atomic.LoadInt64(&s.SuccessRequests)
	failed := atomic.LoadInt64(&s.FailedRequests)
	currentLoad := atomic.LoadInt64(&s.CurrentLoad)
	
	var successRate float64
	if total > 0 {
		successRate = float64(success) / float64(total) * 100
	}
	
	return ServerStats{
		ID:              s.ID,
		Host:            s.Host,
		Port:            s.Port,
		IsHealthy:       s.IsHealthy,
		CurrentLoad:     currentLoad,
		TotalRequests:   total,
		SuccessRequests: success,
		FailedRequests:  failed,
		SuccessRate:     successRate,
		AvgResponseTime: s.AvgResponseTime,
		CPUUsage:        s.CPUUsage,
		MemoryUsage:     s.MemoryUsage,
		NetworkLatency:  s.NetworkLatency,
		Region:          s.Region,
		Zone:            s.Zone,
	}
}

// UpdateHealth updates server health status
func (s *Server) UpdateHealth(healthy bool, cpuUsage, memoryUsage float64, latency time.Duration) {
	s.Mutex.Lock()
	defer s.Mutex.Unlock()
	
	s.IsHealthy = healthy
	s.CPUUsage = cpuUsage
	s.MemoryUsage = memoryUsage
	s.NetworkLatency = latency
	s.LastHealthCheck = time.Now()
}

// ServerStats represents server statistics
type ServerStats struct {
	ID              string        `json:"id"`
	Host            string        `json:"host"`
	Port            int           `json:"port"`
	IsHealthy       bool          `json:"is_healthy"`
	CurrentLoad     int64         `json:"current_load"`
	TotalRequests   int64         `json:"total_requests"`
	SuccessRequests int64         `json:"success_requests"`
	FailedRequests  int64         `json:"failed_requests"`
	SuccessRate     float64       `json:"success_rate"`
	AvgResponseTime time.Duration `json:"avg_response_time"`
	CPUUsage        float64       `json:"cpu_usage"`
	MemoryUsage     float64       `json:"memory_usage"`
	NetworkLatency  time.Duration `json:"network_latency"`
	Region          string        `json:"region"`
	Zone            string        `json:"zone"`
}

// LoadBalancer interface defines load balancing algorithms
type LoadBalancer interface {
	SelectServer() *Server
	AddServer(server *Server)
	RemoveServer(serverID string)
	GetStats() LoadBalancerStats
	UpdateHealthStatus()
	GetName() string
}

// LoadBalancerStats represents load balancer statistics
type LoadBalancerStats struct {
	Name                string        `json:"name"`
	TotalServers        int           `json:"total_servers"`
	HealthyServers      int           `json:"healthy_servers"`
	TotalRequests       int64         `json:"total_requests"`
	SuccessfulRequests  int64         `json:"successful_requests"`
	FailedRequests      int64         `json:"failed_requests"`
	SuccessRate         float64       `json:"success_rate"`
	AvgResponseTime     time.Duration `json:"avg_response_time"`
	RequestsPerSecond   float64       `json:"requests_per_second"`
}

// RoundRobinLoadBalancer implements round-robin algorithm
type RoundRobinLoadBalancer struct {
	Name     string
	Servers  []*Server
	Current  int64
	Mutex    sync.RWMutex
	Stats    LoadBalancerStats
	StartTime time.Time
}

// NewRoundRobinLoadBalancer creates a new round-robin load balancer
func NewRoundRobinLoadBalancer() *RoundRobinLoadBalancer {
	return &RoundRobinLoadBalancer{
		Name:      "Round Robin",
		Servers:   make([]*Server, 0),
		Current:   0,
		StartTime: time.Now(),
	}
}

func (rr *RoundRobinLoadBalancer) GetName() string {
	return rr.Name
}

func (rr *RoundRobinLoadBalancer) AddServer(server *Server) {
	rr.Mutex.Lock()
	defer rr.Mutex.Unlock()
	
	rr.Servers = append(rr.Servers, server)
	log.Printf("[%s] Added server: %s (%s:%d)", rr.Name, server.ID, server.Host, server.Port)
}

func (rr *RoundRobinLoadBalancer) RemoveServer(serverID string) {
	rr.Mutex.Lock()
	defer rr.Mutex.Unlock()
	
	for i, server := range rr.Servers {
		if server.ID == serverID {
			rr.Servers = append(rr.Servers[:i], rr.Servers[i+1:]...)
			log.Printf("[%s] Removed server: %s", rr.Name, serverID)
			break
		}
	}
}

func (rr *RoundRobinLoadBalancer) SelectServer() *Server {
	rr.Mutex.RLock()
	defer rr.Mutex.RUnlock()
	
	if len(rr.Servers) == 0 {
		return nil
	}
	
	// Find next healthy server
	attempts := 0
	for attempts < len(rr.Servers) {
		current := atomic.AddInt64(&rr.Current, 1) % int64(len(rr.Servers))
		server := rr.Servers[current]
		
		if server.IsHealthy {
			return server
		}
		attempts++
	}
	
	return nil // No healthy servers
}

func (rr *RoundRobinLoadBalancer) UpdateHealthStatus() {
	rr.Mutex.RLock()
	defer rr.Mutex.RUnlock()
	
	// Simulate health checks
	for _, server := range rr.Servers {
		// Simulate random health changes (90% healthy)
		healthy := rand.Float64() > 0.1
		cpuUsage := rand.Float64() * 100
		memoryUsage := rand.Float64() * 100
		latency := time.Duration(rand.Intn(100)) * time.Millisecond
		
		server.UpdateHealth(healthy, cpuUsage, memoryUsage, latency)
	}
}

func (rr *RoundRobinLoadBalancer) GetStats() LoadBalancerStats {
	rr.Mutex.RLock()
	defer rr.Mutex.RUnlock()
	
	totalServers := len(rr.Servers)
	healthyServers := 0
	var totalRequests, successfulRequests, failedRequests int64
	var totalResponseTime time.Duration
	
	for _, server := range rr.Servers {
		stats := server.GetStats()
		if stats.IsHealthy {
			healthyServers++
		}
		totalRequests += stats.TotalRequests
		successfulRequests += stats.SuccessRequests
		failedRequests += stats.FailedRequests
		totalResponseTime += stats.AvgResponseTime
	}
	
	var successRate float64
	if totalRequests > 0 {
		successRate = float64(successfulRequests) / float64(totalRequests) * 100
	}
	
	var avgResponseTime time.Duration
	if totalServers > 0 {
		avgResponseTime = totalResponseTime / time.Duration(totalServers)
	}
	
	elapsed := time.Since(rr.StartTime).Seconds()
	requestsPerSecond := float64(totalRequests) / elapsed
	
	return LoadBalancerStats{
		Name:               rr.Name,
		TotalServers:       totalServers,
		HealthyServers:     healthyServers,
		TotalRequests:      totalRequests,
		SuccessfulRequests: successfulRequests,
		FailedRequests:     failedRequests,
		SuccessRate:        successRate,
		AvgResponseTime:    avgResponseTime,
		RequestsPerSecond:  requestsPerSecond,
	}
}

// WeightedRoundRobinLoadBalancer implements weighted round-robin algorithm
type WeightedRoundRobinLoadBalancer struct {
	Name         string
	Servers      []*Server
	Weights      []int
	CurrentIndex int
	CurrentWeight int
	TotalWeight  int
	Mutex        sync.RWMutex
	StartTime    time.Time
}

// NewWeightedRoundRobinLoadBalancer creates a new weighted round-robin load balancer
func NewWeightedRoundRobinLoadBalancer() *WeightedRoundRobinLoadBalancer {
	return &WeightedRoundRobinLoadBalancer{
		Name:      "Weighted Round Robin",
		Servers:   make([]*Server, 0),
		Weights:   make([]int, 0),
		StartTime: time.Now(),
	}
}

func (wrr *WeightedRoundRobinLoadBalancer) GetName() string {
	return wrr.Name
}

func (wrr *WeightedRoundRobinLoadBalancer) AddServer(server *Server) {
	wrr.Mutex.Lock()
	defer wrr.Mutex.Unlock()
	
	wrr.Servers = append(wrr.Servers, server)
	wrr.Weights = append(wrr.Weights, server.Weight)
	wrr.TotalWeight += server.Weight
	log.Printf("[%s] Added server: %s (weight: %d)", wrr.Name, server.ID, server.Weight)
}

func (wrr *WeightedRoundRobinLoadBalancer) RemoveServer(serverID string) {
	wrr.Mutex.Lock()
	defer wrr.Mutex.Unlock()
	
	for i, server := range wrr.Servers {
		if server.ID == serverID {
			wrr.TotalWeight -= wrr.Weights[i]
			wrr.Servers = append(wrr.Servers[:i], wrr.Servers[i+1:]...)
			wrr.Weights = append(wrr.Weights[:i], wrr.Weights[i+1:]...)
			log.Printf("[%s] Removed server: %s", wrr.Name, serverID)
			break
		}
	}
}

func (wrr *WeightedRoundRobinLoadBalancer) SelectServer() *Server {
	wrr.Mutex.Lock()
	defer wrr.Mutex.Unlock()
	
	if len(wrr.Servers) == 0 {
		return nil
	}
	
	// Weighted round-robin algorithm
	for {
		wrr.CurrentIndex = (wrr.CurrentIndex + 1) % len(wrr.Servers)
		
		if wrr.CurrentIndex == 0 {
			wrr.CurrentWeight -= wrr.gcd()
			if wrr.CurrentWeight <= 0 {
				wrr.CurrentWeight = wrr.maxWeight()
			}
		}
		
		if wrr.Weights[wrr.CurrentIndex] >= wrr.CurrentWeight && wrr.Servers[wrr.CurrentIndex].IsHealthy {
			return wrr.Servers[wrr.CurrentIndex]
		}
	}
}

func (wrr *WeightedRoundRobinLoadBalancer) gcd() int {
	if len(wrr.Weights) == 0 {
		return 1
	}
	
	result := wrr.Weights[0]
	for i := 1; i < len(wrr.Weights); i++ {
		result = gcdTwo(result, wrr.Weights[i])
	}
	return result
}

func gcdTwo(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func (wrr *WeightedRoundRobinLoadBalancer) maxWeight() int {
	if len(wrr.Weights) == 0 {
		return 0
	}
	
	max := wrr.Weights[0]
	for _, weight := range wrr.Weights[1:] {
		if weight > max {
			max = weight
		}
	}
	return max
}

func (wrr *WeightedRoundRobinLoadBalancer) UpdateHealthStatus() {
	wrr.Mutex.RLock()
	defer wrr.Mutex.RUnlock()
	
	for _, server := range wrr.Servers {
		healthy := rand.Float64() > 0.1
		cpuUsage := rand.Float64() * 100
		memoryUsage := rand.Float64() * 100
		latency := time.Duration(rand.Intn(100)) * time.Millisecond
		
		server.UpdateHealth(healthy, cpuUsage, memoryUsage, latency)
	}
}

func (wrr *WeightedRoundRobinLoadBalancer) GetStats() LoadBalancerStats {
	wrr.Mutex.RLock()
	defer wrr.Mutex.RUnlock()
	
	totalServers := len(wrr.Servers)
	healthyServers := 0
	var totalRequests, successfulRequests, failedRequests int64
	var totalResponseTime time.Duration
	
	for _, server := range wrr.Servers {
		stats := server.GetStats()
		if stats.IsHealthy {
			healthyServers++
		}
		totalRequests += stats.TotalRequests
		successfulRequests += stats.SuccessRequests
		failedRequests += stats.FailedRequests
		totalResponseTime += stats.AvgResponseTime
	}
	
	var successRate float64
	if totalRequests > 0 {
		successRate = float64(successfulRequests) / float64(totalRequests) * 100
	}
	
	var avgResponseTime time.Duration
	if totalServers > 0 {
		avgResponseTime = totalResponseTime / time.Duration(totalServers)
	}
	
	elapsed := time.Since(wrr.StartTime).Seconds()
	requestsPerSecond := float64(totalRequests) / elapsed
	
	return LoadBalancerStats{
		Name:               wrr.Name,
		TotalServers:       totalServers,
		HealthyServers:     healthyServers,
		TotalRequests:      totalRequests,
		SuccessfulRequests: successfulRequests,
		FailedRequests:     failedRequests,
		SuccessRate:        successRate,
		AvgResponseTime:    avgResponseTime,
		RequestsPerSecond:  requestsPerSecond,
	}
}

// LeastConnectionsLoadBalancer implements least connections algorithm
type LeastConnectionsLoadBalancer struct {
	Name      string
	Servers   []*Server
	Mutex     sync.RWMutex
	StartTime time.Time
}

// NewLeastConnectionsLoadBalancer creates a new least connections load balancer
func NewLeastConnectionsLoadBalancer() *LeastConnectionsLoadBalancer {
	return &LeastConnectionsLoadBalancer{
		Name:      "Least Connections",
		Servers:   make([]*Server, 0),
		StartTime: time.Now(),
	}
}

func (lc *LeastConnectionsLoadBalancer) GetName() string {
	return lc.Name
}

func (lc *LeastConnectionsLoadBalancer) AddServer(server *Server) {
	lc.Mutex.Lock()
	defer lc.Mutex.Unlock()
	
	lc.Servers = append(lc.Servers, server)
	log.Printf("[%s] Added server: %s", lc.Name, server.ID)
}

func (lc *LeastConnectionsLoadBalancer) RemoveServer(serverID string) {
	lc.Mutex.Lock()
	defer lc.Mutex.Unlock()
	
	for i, server := range lc.Servers {
		if server.ID == serverID {
			lc.Servers = append(lc.Servers[:i], lc.Servers[i+1:]...)
			log.Printf("[%s] Removed server: %s", lc.Name, serverID)
			break
		}
	}
}

func (lc *LeastConnectionsLoadBalancer) SelectServer() *Server {
	lc.Mutex.RLock()
	defer lc.Mutex.RUnlock()
	
	if len(lc.Servers) == 0 {
		return nil
	}
	
	var selectedServer *Server
	minConnections := int64(math.MaxInt64)
	
	for _, server := range lc.Servers {
		if server.IsHealthy {
			currentLoad := atomic.LoadInt64(&server.CurrentLoad)
			if currentLoad < minConnections {
				minConnections = currentLoad
				selectedServer = server
			}
		}
	}
	
	return selectedServer
}

func (lc *LeastConnectionsLoadBalancer) UpdateHealthStatus() {
	lc.Mutex.RLock()
	defer lc.Mutex.RUnlock()
	
	for _, server := range lc.Servers {
		healthy := rand.Float64() > 0.1
		cpuUsage := rand.Float64() * 100
		memoryUsage := rand.Float64() * 100
		latency := time.Duration(rand.Intn(100)) * time.Millisecond
		
		server.UpdateHealth(healthy, cpuUsage, memoryUsage, latency)
	}
}

func (lc *LeastConnectionsLoadBalancer) GetStats() LoadBalancerStats {
	lc.Mutex.RLock()
	defer lc.Mutex.RUnlock()
	
	totalServers := len(lc.Servers)
	healthyServers := 0
	var totalRequests, successfulRequests, failedRequests int64
	var totalResponseTime time.Duration
	
	for _, server := range lc.Servers {
		stats := server.GetStats()
		if stats.IsHealthy {
			healthyServers++
		}
		totalRequests += stats.TotalRequests
		successfulRequests += stats.SuccessRequests
		failedRequests += stats.FailedRequests
		totalResponseTime += stats.AvgResponseTime
	}
	
	var successRate float64
	if totalRequests > 0 {
		successRate = float64(successfulRequests) / float64(totalRequests) * 100
	}
	
	var avgResponseTime time.Duration
	if totalServers > 0 {
		avgResponseTime = totalResponseTime / time.Duration(totalServers)
	}
	
	elapsed := time.Since(lc.StartTime).Seconds()
	requestsPerSecond := float64(totalRequests) / elapsed
	
	return LoadBalancerStats{
		Name:               lc.Name,
		TotalServers:       totalServers,
		HealthyServers:     healthyServers,
		TotalRequests:      totalRequests,
		SuccessfulRequests: successfulRequests,
		FailedRequests:     failedRequests,
		SuccessRate:        successRate,
		AvgResponseTime:    avgResponseTime,
		RequestsPerSecond:  requestsPerSecond,
	}
}

// JioTrafficSimulator simulates Jio-style network traffic load balancing
type JioTrafficSimulator struct {
	LoadBalancers map[string]LoadBalancer
	RequestCount  int64
	Mutex         sync.RWMutex
}

// NewJioTrafficSimulator creates a new traffic simulator
func NewJioTrafficSimulator() *JioTrafficSimulator {
	return &JioTrafficSimulator{
		LoadBalancers: make(map[string]LoadBalancer),
	}
}

// AddLoadBalancer adds a load balancer to the simulator
func (jts *JioTrafficSimulator) AddLoadBalancer(name string, lb LoadBalancer) {
	jts.Mutex.Lock()
	defer jts.Mutex.Unlock()
	
	jts.LoadBalancers[name] = lb
	log.Printf("Added load balancer: %s", name)
}

// SimulateTraffic simulates network traffic across load balancers
func (jts *JioTrafficSimulator) SimulateTraffic(ctx context.Context, requestsPerSecond int, duration time.Duration) {
	interval := time.Second / time.Duration(requestsPerSecond)
	endTime := time.Now().Add(duration)
	
	log.Printf("Starting traffic simulation: %d RPS for %v", requestsPerSecond, duration)
	
	for time.Now().Before(endTime) {
		select {
		case <-ctx.Done():
			return
		default:
			// Send requests to all load balancers
			for name, lb := range jts.LoadBalancers {
				go func(lbName string, loadBalancer LoadBalancer) {
					server := loadBalancer.SelectServer()
					if server != nil {
						success, responseTime := server.HandleRequest()
						atomic.AddInt64(&jts.RequestCount, 1)
						
						if !success {
							log.Printf("[%s] Request failed on server %s", lbName, server.ID)
						}
						_ = responseTime // Response time could be used for monitoring
					}
				}(name, lb)
			}
			
			time.Sleep(interval)
		}
	}
	
	log.Printf("Traffic simulation completed. Total requests: %d", 
		atomic.LoadInt64(&jts.RequestCount))
}

// PrintStatistics prints load balancer statistics
func (jts *JioTrafficSimulator) PrintStatistics() {
	jts.Mutex.RLock()
	defer jts.Mutex.RUnlock()
	
	fmt.Println("\n📊 Load Balancer Performance Comparison:")
	fmt.Println("=" + string(make([]byte, 60)))
	
	var allStats []LoadBalancerStats
	for _, lb := range jts.LoadBalancers {
		stats := lb.GetStats()
		allStats = append(allStats, stats)
	}
	
	// Sort by success rate
	sort.Slice(allStats, func(i, j int) bool {
		return allStats[i].SuccessRate > allStats[j].SuccessRate
	})
	
	for rank, stats := range allStats {
		fmt.Printf("\n%d. %s:\n", rank+1, stats.Name)
		fmt.Printf("   Servers: %d total, %d healthy\n", stats.TotalServers, stats.HealthyServers)
		fmt.Printf("   Requests: %d total, %d successful, %d failed\n", 
			stats.TotalRequests, stats.SuccessfulRequests, stats.FailedRequests)
		fmt.Printf("   Success Rate: %.2f%%\n", stats.SuccessRate)
		fmt.Printf("   Avg Response Time: %v\n", stats.AvgResponseTime)
		fmt.Printf("   Throughput: %.1f requests/sec\n", stats.RequestsPerSecond)
	}
}

// Main demonstration function
func main() {
	fmt.Println("📡 Jio Network Load Balancing Algorithms Demo")
	fmt.Println("=" + string(make([]byte, 59)))
	
	// Create traffic simulator
	simulator := NewJioTrafficSimulator()
	
	// Create different load balancer instances
	roundRobin := NewRoundRobinLoadBalancer()
	weightedRoundRobin := NewWeightedRoundRobinLoadBalancer()
	leastConnections := NewLeastConnectionsLoadBalancer()
	
	// Add load balancers to simulator
	simulator.AddLoadBalancer("round_robin", roundRobin)
	simulator.AddLoadBalancer("weighted_round_robin", weightedRoundRobin)
	simulator.AddLoadBalancer("least_connections", leastConnections)
	
	// Create Jio servers across different regions
	fmt.Println("\n🏢 Setting up Jio servers across India...")
	
	// Mumbai region servers (high capacity)
	mumbaiServers := []*Server{
		NewServer("JIO-MUM-01", "10.1.1.10", 8080, 5, 1000, "Mumbai", "West"),
		NewServer("JIO-MUM-02", "10.1.1.11", 8080, 5, 1000, "Mumbai", "West"),
		NewServer("JIO-MUM-03", "10.1.1.12", 8080, 4, 800, "Mumbai", "West"),
	}
	
	// Delhi region servers (medium capacity)
	delhiServers := []*Server{
		NewServer("JIO-DEL-01", "10.2.1.10", 8080, 4, 800, "Delhi", "North"),
		NewServer("JIO-DEL-02", "10.2.1.11", 8080, 3, 600, "Delhi", "North"),
	}
	
	// Bangalore region servers (lower capacity)
	bangaloreServers := []*Server{
		NewServer("JIO-BLR-01", "10.3.1.10", 8080, 3, 600, "Bangalore", "South"),
		NewServer("JIO-BLR-02", "10.3.1.11", 8080, 2, 400, "Bangalore", "South"),
	}
	
	// Add servers to all load balancers
	allServers := append(append(mumbaiServers, delhiServers...), bangaloreServers...)
	
	for _, server := range allServers {
		roundRobin.AddServer(server)
		weightedRoundRobin.AddServer(server)
		leastConnections.AddServer(server)
		fmt.Printf("✅ Added server: %s (%s, %s) - Weight: %d, Capacity: %d\n", 
			server.ID, server.Region, server.Zone, server.Weight, server.Capacity)
	}
	
	// Start health monitoring
	fmt.Println("\n💓 Starting health monitoring...")
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	go func() {
		ticker := time.NewTicker(5 * time.Second)
		defer ticker.Stop()
		
		for {
			select {
			case <-ticker.C:
				roundRobin.UpdateHealthStatus()
				weightedRoundRobin.UpdateHealthStatus()
				leastConnections.UpdateHealthStatus()
			case <-ctx.Done():
				return
			}
		}
	}()
	
	// Simulate different traffic patterns
	fmt.Println("\n🚀 Simulating Jio network traffic...")
	
	// Phase 1: Normal traffic (1000 RPS)
	fmt.Println("\nPhase 1: Normal traffic (1000 RPS)...")
	simulator.SimulateTraffic(ctx, 1000, 10*time.Second)
	
	// Phase 2: Peak traffic (5000 RPS) - like during IPL matches
	fmt.Println("\nPhase 2: Peak traffic (5000 RPS) - IPL match time...")
	simulator.SimulateTraffic(ctx, 5000, 10*time.Second)
	
	// Phase 3: Extreme traffic (10000 RPS) - like during major events
	fmt.Println("\nPhase 3: Extreme traffic (10000 RPS) - Festival/Election results...")
	simulator.SimulateTraffic(ctx, 10000, 5*time.Second)
	
	// Allow processing to complete
	time.Sleep(2 * time.Second)
	
	// Print final statistics
	simulator.PrintStatistics()
	
	// Print server-wise statistics
	fmt.Println("\n🖥️  Server Performance Statistics:")
	fmt.Println("=" + string(make([]byte, 50)))
	
	for _, server := range allServers {
		stats := server.GetStats()
		status := "🟢"
		if !stats.IsHealthy {
			status = "🔴"
		}
		
		fmt.Printf("\n%s %s (%s):\n", status, stats.ID, stats.Region)
		fmt.Printf("   Requests: %d total, %.1f%% success rate\n", 
			stats.TotalRequests, stats.SuccessRate)
		fmt.Printf("   Current Load: %d, Response Time: %v\n", 
			stats.CurrentLoad, stats.AvgResponseTime)
		fmt.Printf("   CPU: %.1f%%, Memory: %.1f%%, Latency: %v\n", 
			stats.CPUUsage, stats.MemoryUsage, stats.NetworkLatency)
	}
	
	// Algorithm comparison insights
	fmt.Println("\n💡 Load Balancing Algorithm Insights:")
	fmt.Println("=" + string(make([]byte, 50)))
	
	fmt.Println("\n🔄 Round Robin:")
	fmt.Println("   ✅ Simple and fair distribution")
	fmt.Println("   ✅ No server preference bias")
	fmt.Println("   ❌ Doesn't consider server capacity")
	fmt.Println("   ❌ May overload weaker servers")
	
	fmt.Println("\n⚖️  Weighted Round Robin:")
	fmt.Println("   ✅ Considers server capacity via weights")
	fmt.Println("   ✅ Better resource utilization")
	fmt.Println("   ✅ Suitable for heterogeneous server clusters")
	fmt.Println("   ❌ Static weights don't adapt to real-time load")
	
	fmt.Println("\n📊 Least Connections:")
	fmt.Println("   ✅ Dynamic load distribution")
	fmt.Println("   ✅ Adapts to real-time server load")
	fmt.Println("   ✅ Prevents server overload")
	fmt.Println("   ❌ Slightly more complex overhead")
	
	// Production insights
	fmt.Println("\n🎯 Production Insights for Jio-scale Systems:")
	fmt.Println("- Jio handles 400M+ users requiring sophisticated load balancing")
	fmt.Println("- Geographic load balancing reduces latency for regional users")
	fmt.Println("- Health monitoring prevents cascade failures during outages")
	fmt.Println("- Weighted algorithms optimize for heterogeneous server hardware")
	fmt.Println("- Real-time adaptation crucial for handling traffic spikes")
	fmt.Println("- Multiple algorithms used in combination for optimal performance")
	fmt.Println("- Cost optimization through efficient resource utilization")
	fmt.Println("- Critical for maintaining QoS during peak usage periods")
	
	fmt.Println("\nLoad balancing demo completed!")
}