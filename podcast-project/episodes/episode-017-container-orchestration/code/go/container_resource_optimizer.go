package main

// Container Resource Optimizer for Zomato-style Food Delivery
// Episode 17: Container Orchestration
//
// यह example दिखाता है कि कैसे Zomato जैसी companies
// container resources को optimize करती हैं real-time में।

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"sort"
	"sync"
	"time"

	"github.com/prometheus/client_golang/api"
	v1 "github.com/prometheus/client_golang/api/prometheus/v1"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// ContainerMetrics represents container resource metrics
type ContainerMetrics struct {
	ContainerID     string    `json:"container_id"`
	ServiceName     string    `json:"service_name"`
	CPUUsage        float64   `json:"cpu_usage_percent"`
	MemoryUsage     float64   `json:"memory_usage_mb"`
	MemoryLimit     float64   `json:"memory_limit_mb"`
	NetworkIO       int64     `json:"network_io_bytes"`
	DiskIO          int64     `json:"disk_io_bytes"`
	RequestRate     float64   `json:"request_rate_per_sec"`
	ResponseTime    float64   `json:"response_time_ms"`
	ErrorRate       float64   `json:"error_rate_percent"`
	Timestamp       time.Time `json:"timestamp"`
	Environment     string    `json:"environment"`
	Region          string    `json:"region"` // mumbai, bangalore, delhi
}

// OptimizationRecommendation represents resource optimization suggestion
type OptimizationRecommendation struct {
	ContainerID     string                 `json:"container_id"`
	ServiceName     string                 `json:"service_name"`
	RecommendationType string              `json:"type"` // scale_up, scale_down, right_size
	CurrentResources   map[string]string   `json:"current_resources"`
	RecommendedResources map[string]string `json:"recommended_resources"`
	PotentialSavings   float64             `json:"potential_savings_inr"`
	Confidence        float64              `json:"confidence_score"`
	Reason            string               `json:"reason"`
	Priority          int                  `json:"priority"` // 1-10, 10 being highest
}

// ZomatoResourceOptimizer optimizes container resources for food delivery workloads
type ZomatoResourceOptimizer struct {
	metricsHistory    map[string][]ContainerMetrics
	recommendations   []OptimizationRecommendation
	mutex             sync.RWMutex
	prometheusClient  v1.API
	
	// Indian company specific configurations
	costPerCPUCore    float64 // INR per CPU core per hour
	costPerGBMemory   float64 // INR per GB memory per hour
	peakHours         []TimeRange
	regionMultipliers map[string]float64 // Cost multipliers by region
	
	// Optimization thresholds
	cpuUnderutilized  float64 // Below this percentage = under-utilized
	cpuOverutilized   float64 // Above this percentage = over-utilized
	memoryUnderutilized float64
	memoryOverutilized  float64
	
	// Prometheus metrics for monitoring
	optimizationSavings prometheus.Gauge
	recommendationCount prometheus.Counter
}

// TimeRange represents a time range for peak hours
type TimeRange struct {
	StartHour int
	EndHour   int
	Name      string
}

// NewZomatoResourceOptimizer creates a new resource optimizer
func NewZomatoResourceOptimizer() *ZomatoResourceOptimizer {
	// Initialize Prometheus client (in production, use actual Prometheus endpoint)
	client, err := api.NewClient(api.Config{
		Address: "http://localhost:9090",
	})
	if err != nil {
		log.Printf("Error creating Prometheus client: %v", err)
	}
	
	optimizer := &ZomatoResourceOptimizer{
		metricsHistory:   make(map[string][]ContainerMetrics),
		recommendations:  make([]OptimizationRecommendation, 0),
		prometheusClient: v1.NewAPI(client),
		
		// Indian cloud costs (approximate INR per hour)
		costPerCPUCore:  2.50,  // ~₹2.50 per CPU core per hour
		costPerGBMemory: 0.80,  // ~₹0.80 per GB memory per hour
		
		// Indian peak hours for food delivery
		peakHours: []TimeRange{
			{StartHour: 12, EndHour: 14, Name: "lunch_rush"},
			{StartHour: 19, EndHour: 22, Name: "dinner_rush"},
			{StartHour: 8, EndHour: 10, Name: "breakfast"},
		},
		
		// Regional cost multipliers (Mumbai most expensive)
		regionMultipliers: map[string]float64{
			"mumbai":    1.3,  // 30% more expensive
			"bangalore": 1.0,  // Base cost
			"delhi":     1.1,  // 10% more expensive
			"pune":      0.9,  // 10% cheaper
			"hyderabad": 0.85, // 15% cheaper
		},
		
		// Optimization thresholds
		cpuUnderutilized:    30.0,  // Less than 30% CPU usage
		cpuOverutilized:     80.0,  // More than 80% CPU usage
		memoryUnderutilized: 40.0,  // Less than 40% memory usage
		memoryOverutilized:  85.0,  // More than 85% memory usage
	}
	
	// Initialize Prometheus metrics
	optimizer.optimizationSavings = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "zomato_optimization_potential_savings_inr",
		Help: "Potential cost savings from optimization recommendations in INR",
	})
	
	optimizer.recommendationCount = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "zomato_optimization_recommendations_total",
		Help: "Total number of optimization recommendations generated",
	})
	
	prometheus.MustRegister(optimizer.optimizationSavings)
	prometheus.MustRegister(optimizer.recommendationCount)
	
	return optimizer
}

// CollectMetrics collects container metrics (simulated data for demo)
func (z *ZomatoResourceOptimizer) CollectMetrics() {
	log.Println("🍔 Collecting Zomato container metrics...")
	
	// Simulate Zomato services across Indian cities
	services := []string{
		"zomato-order-service",
		"zomato-restaurant-service", 
		"zomato-delivery-service",
		"zomato-payment-service",
		"zomato-notification-service",
	}
	
	regions := []string{"mumbai", "bangalore", "delhi", "pune", "hyderabad"}
	environments := []string{"production", "staging"}
	
	z.mutex.Lock()
	defer z.mutex.Unlock()
	
	currentTime := time.Now()
	currentHour := currentTime.Hour()
	
	// Determine if it's peak hour
	isPeakHour := false
	for _, peak := range z.peakHours {
		if currentHour >= peak.StartHour && currentHour <= peak.EndHour {
			isPeakHour = true
			break
		}
	}
	
	for _, service := range services {
		for _, region := range regions {
			for _, env := range environments {
				// Generate realistic metrics based on service type and time
				metrics := z.generateRealisticMetrics(service, region, env, isPeakHour)
				
				containerID := fmt.Sprintf("%s-%s-%s-%d", service, region, env, time.Now().Unix()%1000)
				
				// Store metrics in history
				if z.metricsHistory[containerID] == nil {
					z.metricsHistory[containerID] = make([]ContainerMetrics, 0)
				}
				
				z.metricsHistory[containerID] = append(z.metricsHistory[containerID], metrics)
				
				// Keep only last 100 data points
				if len(z.metricsHistory[containerID]) > 100 {
					z.metricsHistory[containerID] = z.metricsHistory[containerID][1:]
				}
			}
		}
	}
	
	log.Printf("📊 Collected metrics for %d containers", len(z.metricsHistory))
}

// generateRealisticMetrics generates realistic metrics based on service and context
func (z *ZomatoResourceOptimizer) generateRealisticMetrics(service, region, environment string, isPeakHour bool) ContainerMetrics {
	baseLoad := 0.3 // 30% base load
	peakMultiplier := 1.0
	
	if isPeakHour {
		peakMultiplier = 3.0 // 3x load during peak hours
	}
	
	// Service-specific load patterns
	serviceMultiplier := 1.0
	switch service {
	case "zomato-order-service":
		serviceMultiplier = 4.0 // High load service
	case "zomato-delivery-service":
		serviceMultiplier = 3.0 // Medium-high load
	case "zomato-payment-service":
		serviceMultiplier = 2.0 // Medium load
	default:
		serviceMultiplier = 1.5 // Low-medium load
	}
	
	// Regional load differences
	regionMultiplier := z.regionMultipliers[region]
	
	// Environment differences
	envMultiplier := 1.0
	if environment == "staging" {
		envMultiplier = 0.3 // 30% of production load
	}
	
	// Calculate final load
	finalLoad := baseLoad * peakMultiplier * serviceMultiplier * regionMultiplier * envMultiplier
	
	// Add some randomness
	variance := 0.2 // 20% variance
	randomFactor := 1.0 + (variance * (2.0*getRandom() - 1.0))
	
	cpuUsage := math.Min(95.0, finalLoad*50*randomFactor)
	memoryUsage := math.Min(90.0, finalLoad*40*randomFactor)
	
	return ContainerMetrics{
		ContainerID:  fmt.Sprintf("%s-%s-%s", service, region, environment),
		ServiceName:  service,
		CPUUsage:     cpuUsage,
		MemoryUsage:  memoryUsage * 1024, // Convert to MB
		MemoryLimit:  2048,               // 2GB limit
		NetworkIO:    int64(finalLoad * 1000000 * randomFactor), // Network I/O in bytes
		DiskIO:       int64(finalLoad * 500000 * randomFactor),  // Disk I/O in bytes
		RequestRate:  finalLoad * 100 * randomFactor,            // Requests per second
		ResponseTime: (1000 * finalLoad * randomFactor),         // Response time in ms
		ErrorRate:    math.Min(10.0, finalLoad*2*randomFactor),  // Error rate percentage
		Timestamp:    time.Now(),
		Environment:  environment,
		Region:       region,
	}
}

// AnalyzeAndOptimize analyzes metrics and generates optimization recommendations
func (z *ZomatoResourceOptimizer) AnalyzeAndOptimize() {
	log.Println("🔍 Analyzing containers for optimization opportunities...")
	
	z.mutex.Lock()
	defer z.mutex.Unlock()
	
	newRecommendations := make([]OptimizationRecommendation, 0)
	totalPotentialSavings := 0.0
	
	for containerID, metricsHistory := range z.metricsHistory {
		if len(metricsHistory) < 5 {
			continue // Need at least 5 data points for analysis
		}
		
		// Get recent metrics (last 10 data points)
		recentMetrics := metricsHistory[len(metricsHistory)-10:]
		recommendation := z.analyzeContainerMetrics(containerID, recentMetrics)
		
		if recommendation != nil {
			newRecommendations = append(newRecommendations, *recommendation)
			totalPotentialSavings += recommendation.PotentialSavings
		}
	}
	
	// Sort recommendations by potential savings (highest first)
	sort.Slice(newRecommendations, func(i, j int) bool {
		return newRecommendations[i].PotentialSavings > newRecommendations[j].PotentialSavings
	})
	
	z.recommendations = newRecommendations
	z.optimizationSavings.Set(totalPotentialSavings)
	z.recommendationCount.Add(float64(len(newRecommendations)))
	
	log.Printf("💡 Generated %d optimization recommendations", len(newRecommendations))
	log.Printf("💰 Total potential savings: ₹%.2f per hour", totalPotentialSavings)
}

// analyzeContainerMetrics analyzes individual container metrics
func (z *ZomatoResourceOptimizer) analyzeContainerMetrics(containerID string, metrics []ContainerMetrics) *OptimizationRecommendation {
	if len(metrics) == 0 {
		return nil
	}
	
	// Calculate averages
	var avgCPU, avgMemory, avgMemoryUsage float64
	for _, m := range metrics {
		avgCPU += m.CPUUsage
		avgMemoryUsage += m.MemoryUsage
		avgMemory += m.MemoryLimit
	}
	
	avgCPU /= float64(len(metrics))
	avgMemoryUsage /= float64(len(metrics))
	avgMemory /= float64(len(metrics))
	
	memoryUtilization := (avgMemoryUsage / avgMemory) * 100
	
	latestMetrics := metrics[len(metrics)-1]
	regionMultiplier := z.regionMultipliers[latestMetrics.Region]
	
	// Check for optimization opportunities
	
	// Case 1: Under-utilized resources (scale down)
	if avgCPU < z.cpuUnderutilized && memoryUtilization < z.memoryUnderutilized {
		return z.createScaleDownRecommendation(containerID, latestMetrics, avgCPU, memoryUtilization, regionMultiplier)
	}
	
	// Case 2: Over-utilized resources (scale up)
	if avgCPU > z.cpuOverutilized || memoryUtilization > z.memoryOverutilized {
		return z.createScaleUpRecommendation(containerID, latestMetrics, avgCPU, memoryUtilization, regionMultiplier)
	}
	
	// Case 3: Right-sizing opportunity (memory vs CPU imbalance)
	if z.hasResourceImbalance(avgCPU, memoryUtilization) {
		return z.createRightSizeRecommendation(containerID, latestMetrics, avgCPU, memoryUtilization, regionMultiplier)
	}
	
	return nil
}

// createScaleDownRecommendation creates a scale-down recommendation
func (z *ZomatoResourceOptimizer) createScaleDownRecommendation(containerID string, metrics ContainerMetrics, avgCPU, memoryUtil, regionMultiplier float64) *OptimizationRecommendation {
	// Calculate optimal resources (reduce by 30-50%)
	reductionFactor := 0.4 // 40% reduction
	
	currentCPU := 1.0 // Assume 1 CPU core currently
	currentMemory := metrics.MemoryLimit / 1024 // Convert to GB
	
	recommendedCPU := currentCPU * (1 - reductionFactor)
	recommendedMemory := currentMemory * (1 - reductionFactor)
	
	// Calculate potential savings
	cpuSavings := (currentCPU - recommendedCPU) * z.costPerCPUCore * regionMultiplier
	memorySavings := (currentMemory - recommendedMemory) * z.costPerGBMemory * regionMultiplier
	totalSavings := (cpuSavings + memorySavings) * 24 // Per day
	
	return &OptimizationRecommendation{
		ContainerID:        containerID,
		ServiceName:        metrics.ServiceName,
		RecommendationType: "scale_down",
		CurrentResources: map[string]string{
			"cpu":    fmt.Sprintf("%.1f cores", currentCPU),
			"memory": fmt.Sprintf("%.1f GB", currentMemory),
		},
		RecommendedResources: map[string]string{
			"cpu":    fmt.Sprintf("%.1f cores", recommendedCPU),
			"memory": fmt.Sprintf("%.1f GB", recommendedMemory),
		},
		PotentialSavings: totalSavings,
		Confidence:       0.85, // 85% confidence
		Reason:           fmt.Sprintf("Under-utilized: CPU %.1f%%, Memory %.1f%%", avgCPU, memoryUtil),
		Priority:         7,
	}
}

// createScaleUpRecommendation creates a scale-up recommendation  
func (z *ZomatoResourceOptimizer) createScaleUpRecommendation(containerID string, metrics ContainerMetrics, avgCPU, memoryUtil, regionMultiplier float64) *OptimizationRecommendation {
	// Calculate optimal resources (increase by 20-40%)
	increaseFactor := 0.3 // 30% increase
	
	currentCPU := 1.0 // Assume 1 CPU core currently
	currentMemory := metrics.MemoryLimit / 1024 // Convert to GB
	
	recommendedCPU := currentCPU * (1 + increaseFactor)
	recommendedMemory := currentMemory * (1 + increaseFactor)
	
	// Calculate additional cost (negative savings)
	cpuCost := (recommendedCPU - currentCPU) * z.costPerCPUCore * regionMultiplier
	memoryCost := (recommendedMemory - currentMemory) * z.costPerGBMemory * regionMultiplier
	totalCost := (cpuCost + memoryCost) * 24 // Per day
	
	return &OptimizationRecommendation{
		ContainerID:        containerID,
		ServiceName:        metrics.ServiceName,
		RecommendationType: "scale_up",
		CurrentResources: map[string]string{
			"cpu":    fmt.Sprintf("%.1f cores", currentCPU),
			"memory": fmt.Sprintf("%.1f GB", currentMemory),
		},
		RecommendedResources: map[string]string{
			"cpu":    fmt.Sprintf("%.1f cores", recommendedCPU),
			"memory": fmt.Sprintf("%.1f GB", recommendedMemory),
		},
		PotentialSavings: -totalCost, // Negative because it's additional cost
		Confidence:       0.90,       // 90% confidence for scale-up
		Reason:           fmt.Sprintf("Over-utilized: CPU %.1f%%, Memory %.1f%%", avgCPU, memoryUtil),
		Priority:         9, // High priority
	}
}

// createRightSizeRecommendation creates a right-sizing recommendation
func (z *ZomatoResourceOptimizer) createRightSizeRecommendation(containerID string, metrics ContainerMetrics, avgCPU, memoryUtil, regionMultiplier float64) *OptimizationRecommendation {
	currentCPU := 1.0
	currentMemory := metrics.MemoryLimit / 1024
	
	// Adjust based on actual usage patterns
	recommendedCPU := currentCPU * (avgCPU / 70.0)       // Target 70% CPU
	recommendedMemory := currentMemory * (memoryUtil / 70.0) // Target 70% memory
	
	// Calculate savings
	cpuSavings := (currentCPU - recommendedCPU) * z.costPerCPUCore * regionMultiplier
	memorySavings := (currentMemory - recommendedMemory) * z.costPerGBMemory * regionMultiplier
	totalSavings := (cpuSavings + memorySavings) * 24
	
	return &OptimizationRecommendation{
		ContainerID:        containerID,
		ServiceName:        metrics.ServiceName,
		RecommendationType: "right_size",
		CurrentResources: map[string]string{
			"cpu":    fmt.Sprintf("%.1f cores", currentCPU),
			"memory": fmt.Sprintf("%.1f GB", currentMemory),
		},
		RecommendedResources: map[string]string{
			"cpu":    fmt.Sprintf("%.1f cores", recommendedCPU),
			"memory": fmt.Sprintf("%.1f GB", recommendedMemory),
		},
		PotentialSavings: totalSavings,
		Confidence:       0.75, // 75% confidence
		Reason:           fmt.Sprintf("Resource imbalance: CPU %.1f%%, Memory %.1f%%", avgCPU, memoryUtil),
		Priority:         6,
	}
}

// hasResourceImbalance checks if there's significant imbalance between CPU and memory usage
func (z *ZomatoResourceOptimizer) hasResourceImbalance(cpuUtil, memoryUtil float64) bool {
	imbalance := math.Abs(cpuUtil - memoryUtil)
	return imbalance > 30.0 // More than 30% difference
}

// GetTopRecommendations returns top N optimization recommendations
func (z *ZomatoResourceOptimizer) GetTopRecommendations(limit int) []OptimizationRecommendation {
	z.mutex.RLock()
	defer z.mutex.RUnlock()
	
	if len(z.recommendations) <= limit {
		return z.recommendations
	}
	
	return z.recommendations[:limit]
}

// StartOptimizationLoop starts the continuous optimization loop
func (z *ZomatoResourceOptimizer) StartOptimizationLoop() {
	log.Println("🔄 Starting Zomato resource optimization loop...")
	
	ticker := time.NewTicker(5 * time.Minute) // Run every 5 minutes
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			z.CollectMetrics()
			z.AnalyzeAndOptimize()
			z.printOptimizationSummary()
		}
	}
}

// printOptimizationSummary prints optimization summary
func (z *ZomatoResourceOptimizer) printOptimizationSummary() {
	recommendations := z.GetTopRecommendations(5)
	
	if len(recommendations) == 0 {
		log.Println("✅ No optimization opportunities found")
		return
	}
	
	log.Printf("📊 Top %d Optimization Recommendations:", len(recommendations))
	
	totalSavings := 0.0
	for i, rec := range recommendations {
		totalSavings += rec.PotentialSavings
		
		savingsText := fmt.Sprintf("₹%.2f/day", rec.PotentialSavings)
		if rec.PotentialSavings < 0 {
			savingsText = fmt.Sprintf("Cost: ₹%.2f/day", -rec.PotentialSavings)
		}
		
		log.Printf("   %d. %s (%s) - %s", 
			i+1, 
			rec.ServiceName, 
			rec.RecommendationType, 
			savingsText)
		log.Printf("      %s", rec.Reason)
		log.Printf("      Confidence: %.0f%%, Priority: %d", rec.Confidence*100, rec.Priority)
	}
	
	log.Printf("💰 Total potential savings: ₹%.2f per day", totalSavings)
	log.Printf("💰 Monthly savings potential: ₹%.2f", totalSavings*30)
}

// HTTPHandler provides HTTP API for optimization data
func (z *ZomatoResourceOptimizer) HTTPHandler() {
	http.HandleFunc("/recommendations", func(w http.ResponseWriter, r *http.Request) {
		recommendations := z.GetTopRecommendations(20)
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"recommendations": recommendations,
			"total_count":     len(z.recommendations),
			"timestamp":       time.Now(),
		})
	})
	
	http.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		z.mutex.RLock()
		totalContainers := len(z.metricsHistory)
		totalRecommendations := len(z.recommendations)
		
		totalSavings := 0.0
		for _, rec := range z.recommendations {
			totalSavings += rec.PotentialSavings
		}
		z.mutex.RUnlock()
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"total_containers":      totalContainers,
			"total_recommendations": totalRecommendations,
			"potential_savings_inr": totalSavings,
			"monthly_savings_inr":   totalSavings * 30,
			"timestamp":            time.Now(),
		})
	})
	
	// Prometheus metrics endpoint
	http.Handle("/prometheus", promhttp.Handler())
}

// Simple random number generator for simulation
func getRandom() float64 {
	return float64(time.Now().UnixNano()%1000) / 1000.0
}

func main() {
	fmt.Println("🍔 Zomato Container Resource Optimizer")
	fmt.Println("Production-ready resource optimization for food delivery")
	fmt.Println("=" * 60)
	
	// Initialize optimizer
	optimizer := NewZomatoResourceOptimizer()
	
	// Start HTTP server for API and metrics
	go func() {
		optimizer.HTTPHandler()
		log.Println("🌐 HTTP API server starting on :8080")
		log.Println("   - Recommendations: http://localhost:8080/recommendations")
		log.Println("   - Metrics: http://localhost:8080/metrics")
		log.Println("   - Prometheus: http://localhost:8080/prometheus")
		
		if err := http.ListenAndServe(":8080", nil); err != nil {
			log.Fatalf("HTTP server failed: %v", err)
		}
	}()
	
	// Run initial analysis
	optimizer.CollectMetrics()
	optimizer.AnalyzeAndOptimize()
	optimizer.printOptimizationSummary()
	
	// Start continuous optimization (this would run indefinitely in production)
	log.Println("🔄 Starting optimization loop...")
	log.Println("Press Ctrl+C to stop")
	
	// For demo, run for limited time
	for i := 0; i < 3; i++ {
		time.Sleep(30 * time.Second)
		optimizer.CollectMetrics()
		optimizer.AnalyzeAndOptimize()
		optimizer.printOptimizationSummary()
	}
	
	fmt.Println("\n✅ Zomato resource optimization demo completed!")
	fmt.Println("In production, this would:")
	fmt.Println("  - Integrate with Kubernetes APIs for actual scaling")
	fmt.Println("  - Connect to real Prometheus for metrics")
	fmt.Println("  - Send recommendations to cost management systems")
	fmt.Println("  - Provide detailed financial reporting")
}

/*
Production Deployment:

# Build the Go application:
go mod init zomato-optimizer
go mod tidy
go build -o zomato-optimizer

# Docker container:
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o zomato-optimizer

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/zomato-optimizer .
CMD ["./zomato-optimizer"]

# Kubernetes deployment:
kubectl apply -f zomato-optimizer-deployment.yaml

# Monitor resource optimization:
curl http://localhost:8080/recommendations | jq .

# Prometheus integration:
curl http://localhost:8080/prometheus
*/