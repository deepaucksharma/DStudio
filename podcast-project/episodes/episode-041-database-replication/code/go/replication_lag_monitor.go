/*
Episode 41: Database Replication Strategies
Go Example: Replication Lag Monitoring System

यह comprehensive replication lag monitoring system है जो real-time में
database replication lag को track करता है। Indian banking और e-commerce
systems के लिए specialized monitoring include की गई है।

Real-world Use Case: Banking और E-commerce Monitoring
- Real-time lag detection और alerting
- Regional performance monitoring (Mumbai, Delhi, Bangalore)
- SLA compliance tracking
- Automated failover triggers
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net/http"
	"sort"
	"sync"
	"time"
)

// ReplicationMetrics represents replication metrics for a node
type ReplicationMetrics struct {
	NodeID            string    `json:"node_id"`
	NodeType          string    `json:"node_type"` // master, slave, replica
	Region            string    `json:"region"`
	LastSequenceNumber int64     `json:"last_sequence_number"`
	LastUpdateTime    time.Time `json:"last_update_time"`
	LagMilliseconds   int64     `json:"lag_milliseconds"`
	NetworkLatency    int64     `json:"network_latency_ms"`
	ThroughputOPS     float64   `json:"throughput_ops"`
	ErrorRate         float64   `json:"error_rate"`
	ConnectionStatus  string    `json:"connection_status"`
}

// AlertThreshold defines monitoring thresholds
type AlertThreshold struct {
	MaxLagMs        int64   `json:"max_lag_ms"`
	MaxErrorRate    float64 `json:"max_error_rate"`
	MinThroughput   float64 `json:"min_throughput"`
	MaxNetworkLatency int64 `json:"max_network_latency_ms"`
}

// Alert represents a monitoring alert
type Alert struct {
	ID          string    `json:"id"`
	Severity    string    `json:"severity"` // info, warning, critical
	NodeID      string    `json:"node_id"`
	AlertType   string    `json:"alert_type"`
	Message     string    `json:"message"`
	Timestamp   time.Time `json:"timestamp"`
	Resolved    bool      `json:"resolved"`
	ResolvedAt  *time.Time `json:"resolved_at,omitempty"`
}

// ReplicationLagMonitor monitors replication lag across nodes
type ReplicationLagMonitor struct {
	ctx            context.Context
	cancel         context.CancelFunc
	nodes          map[string]*ReplicationMetrics
	nodesMutex     sync.RWMutex
	alerts         []Alert
	alertsMutex    sync.RWMutex
	thresholds     map[string]AlertThreshold // region -> thresholds
	alertID        int64
	
	// Monitoring configuration
	monitoringInterval time.Duration
	retentionPeriod   time.Duration
	
	// Indian region-specific settings
	regionConfig map[string]RegionConfig
	
	// Performance metrics
	totalAlertsGenerated int64
	totalNodesMonitored  int64
}

// RegionConfig contains region-specific configuration
type RegionConfig struct {
	RegionName         string
	ExpectedLatencyMs  int64
	BusinessHours      BusinessHours
	CriticalSystems    []string
	BackupRegions      []string
}

// BusinessHours defines peak business hours for the region
type BusinessHours struct {
	StartHour int
	EndHour   int
	TimeZone  string
}

// NewReplicationLagMonitor creates a new replication lag monitor
func NewReplicationLagMonitor() *ReplicationLagMonitor {
	ctx, cancel := context.WithCancel(context.Background())
	
	// Indian region configuration
	regionConfig := map[string]RegionConfig{
		"mumbai": {
			RegionName:        "Mumbai Financial Hub",
			ExpectedLatencyMs: 25,
			BusinessHours:     BusinessHours{StartHour: 9, EndHour: 18, TimeZone: "Asia/Kolkata"},
			CriticalSystems:   []string{"banking", "payments", "trading"},
			BackupRegions:     []string{"pune", "delhi"},
		},
		"delhi": {
			RegionName:        "Delhi North Region",
			ExpectedLatencyMs: 30,
			BusinessHours:     BusinessHours{StartHour: 9, EndHour: 18, TimeZone: "Asia/Kolkata"},
			CriticalSystems:   []string{"banking", "government"},
			BackupRegions:     []string{"noida", "gurgaon"},
		},
		"bangalore": {
			RegionName:        "Bangalore Tech Hub",
			ExpectedLatencyMs: 35,
			BusinessHours:     BusinessHours{StartHour: 9, EndHour: 20, TimeZone: "Asia/Kolkata"},
			CriticalSystems:   []string{"ecommerce", "fintech", "payments"},
			BackupRegions:     []string{"hyderabad", "chennai"},
		},
		"chennai": {
			RegionName:        "Chennai South Hub",
			ExpectedLatencyMs: 40,
			BusinessHours:     BusinessHours{StartHour: 9, EndHour: 18, TimeZone: "Asia/Kolkata"},
			CriticalSystems:   []string{"manufacturing", "banking"},
			BackupRegions:     []string{"bangalore", "kochi"},
		},
		"kolkata": {
			RegionName:        "Kolkata East Region",
			ExpectedLatencyMs: 45,
			BusinessHours:     BusinessHours{StartHour: 9, EndHour: 17, TimeZone: "Asia/Kolkata"},
			CriticalSystems:   []string{"banking", "government"},
			BackupRegions:     []string{"bhubaneswar", "delhi"},
		},
	}
	
	// Default thresholds by region (stricter for financial hubs)
	thresholds := map[string]AlertThreshold{
		"mumbai": {
			MaxLagMs:          100,  // 100ms max for Mumbai (financial center)
			MaxErrorRate:      0.01, // 1% max error rate
			MinThroughput:     100,  // 100 ops/sec minimum
			MaxNetworkLatency: 50,   // 50ms max network latency
		},
		"delhi": {
			MaxLagMs:          150,
			MaxErrorRate:      0.02,
			MinThroughput:     80,
			MaxNetworkLatency: 60,
		},
		"bangalore": {
			MaxLagMs:          200,  // More lenient for tech hub
			MaxErrorRate:      0.02,
			MinThroughput:     120,  // Higher throughput expected
			MaxNetworkLatency: 70,
		},
		"chennai": {
			MaxLagMs:          250,
			MaxErrorRate:      0.03,
			MinThroughput:     60,
			MaxNetworkLatency: 80,
		},
		"kolkata": {
			MaxLagMs:          300,
			MaxErrorRate:      0.03,
			MinThroughput:     50,
			MaxNetworkLatency: 90,
		},
	}
	
	return &ReplicationLagMonitor{
		ctx:                ctx,
		cancel:             cancel,
		nodes:              make(map[string]*ReplicationMetrics),
		alerts:             make([]Alert, 0),
		thresholds:         thresholds,
		alertID:            1,
		monitoringInterval: 5 * time.Second,  // Monitor every 5 seconds
		retentionPeriod:   24 * time.Hour,    // Keep data for 24 hours
		regionConfig:      regionConfig,
	}
}

// RegisterNode registers a new node for monitoring
func (m *ReplicationLagMonitor) RegisterNode(nodeID, nodeType, region string) {
	m.nodesMutex.Lock()
	defer m.nodesMutex.Unlock()
	
	m.nodes[nodeID] = &ReplicationMetrics{
		NodeID:           nodeID,
		NodeType:         nodeType,
		Region:           region,
		LastUpdateTime:   time.Now(),
		ConnectionStatus: "connected",
	}
	
	m.totalNodesMonitored++
	
	log.Printf("Registered node: %s (%s) in region %s", nodeID, nodeType, region)
}

// UpdateNodeMetrics updates metrics for a specific node
func (m *ReplicationLagMonitor) UpdateNodeMetrics(nodeID string, sequenceNumber int64, 
	throughput float64, errorRate float64, networkLatency int64) {
	
	m.nodesMutex.Lock()
	defer m.nodesMutex.Unlock()
	
	node, exists := m.nodes[nodeID]
	if !exists {
		log.Printf("Warning: Node %s not found for metrics update", nodeID)
		return
	}
	
	// Calculate lag based on sequence number difference from master
	masterSequence := m.getMasterSequenceNumber(node.Region)
	lag := calculateLag(masterSequence, sequenceNumber)
	
	// Update metrics
	node.LastSequenceNumber = sequenceNumber
	node.LastUpdateTime = time.Now()
	node.LagMilliseconds = lag
	node.NetworkLatency = networkLatency
	node.ThroughputOPS = throughput
	node.ErrorRate = errorRate
	
	// Check for threshold violations
	m.checkThresholds(node)
}

// getMasterSequenceNumber gets the latest sequence number from master in the region
func (m *ReplicationLagMonitor) getMasterSequenceNumber(region string) int64 {
	var maxSequence int64 = 0
	
	for _, node := range m.nodes {
		if node.NodeType == "master" && node.Region == region {
			if node.LastSequenceNumber > maxSequence {
				maxSequence = node.LastSequenceNumber
			}
		}
	}
	
	return maxSequence
}

// calculateLag calculates replication lag in milliseconds
func calculateLag(masterSequence, replicaSequence int64) int64 {
	if masterSequence <= replicaSequence {
		return 0
	}
	
	// Estimate lag based on sequence difference
	// Assuming 1 sequence number = ~1ms (rough approximation)
	sequenceDiff := masterSequence - replicaSequence
	
	// Apply scaling factor based on typical transaction processing rate
	estimatedLagMs := sequenceDiff * 2 // 2ms per sequence difference
	
	return estimatedLagMs
}

// checkThresholds checks if node metrics violate thresholds
func (m *ReplicationLagMonitor) checkThresholds(node *ReplicationMetrics) {
	threshold, exists := m.thresholds[node.Region]
	if !exists {
		return
	}
	
	// Check replication lag
	if node.LagMilliseconds > threshold.MaxLagMs {
		m.generateAlert("critical", node.NodeID, "high_replication_lag",
			fmt.Sprintf("Replication lag %dms exceeds threshold %dms in %s",
				node.LagMilliseconds, threshold.MaxLagMs, node.Region))
	}
	
	// Check error rate
	if node.ErrorRate > threshold.MaxErrorRate {
		m.generateAlert("warning", node.NodeID, "high_error_rate",
			fmt.Sprintf("Error rate %.2f%% exceeds threshold %.2f%% in %s",
				node.ErrorRate*100, threshold.MaxErrorRate*100, node.Region))
	}
	
	// Check throughput
	if node.ThroughputOPS < threshold.MinThroughput {
		m.generateAlert("warning", node.NodeID, "low_throughput",
			fmt.Sprintf("Throughput %.1f ops/sec below threshold %.1f in %s",
				node.ThroughputOPS, threshold.MinThroughput, node.Region))
	}
	
	// Check network latency
	if node.NetworkLatency > threshold.MaxNetworkLatency {
		m.generateAlert("warning", node.NodeID, "high_network_latency",
			fmt.Sprintf("Network latency %dms exceeds threshold %dms in %s",
				node.NetworkLatency, threshold.MaxNetworkLatency, node.Region))
	}
	
	// Special checks during business hours
	if m.isBusinessHours(node.Region) {
		m.checkBusinessHoursCriteria(node, threshold)
	}
}

// isBusinessHours checks if current time is within business hours for the region
func (m *ReplicationLagMonitor) isBusinessHours(region string) bool {
	config, exists := m.regionConfig[region]
	if !exists {
		return false
	}
	
	// For simplicity, using local time (in real system would use region timezone)
	currentHour := time.Now().Hour()
	
	return currentHour >= config.BusinessHours.StartHour && 
		   currentHour <= config.BusinessHours.EndHour
}

// checkBusinessHoursCriteria applies stricter criteria during business hours
func (m *ReplicationLagMonitor) checkBusinessHoursCriteria(node *ReplicationMetrics, threshold AlertThreshold) {
	// During business hours, thresholds are 50% stricter
	businessHourLagThreshold := threshold.MaxLagMs / 2
	businessHourErrorThreshold := threshold.MaxErrorRate / 2
	
	if node.LagMilliseconds > businessHourLagThreshold {
		m.generateAlert("critical", node.NodeID, "business_hours_lag_violation",
			fmt.Sprintf("Business hours lag %dms exceeds strict threshold %dms in %s",
				node.LagMilliseconds, businessHourLagThreshold, node.Region))
	}
	
	if node.ErrorRate > businessHourErrorThreshold {
		m.generateAlert("critical", node.NodeID, "business_hours_error_violation",
			fmt.Sprintf("Business hours error rate %.2f%% exceeds strict threshold %.2f%% in %s",
				node.ErrorRate*100, businessHourErrorThreshold*100, node.Region))
	}
}

// generateAlert generates a new alert
func (m *ReplicationLagMonitor) generateAlert(severity, nodeID, alertType, message string) {
	m.alertsMutex.Lock()
	defer m.alertsMutex.Unlock()
	
	alert := Alert{
		ID:        fmt.Sprintf("ALERT_%d", m.alertID),
		Severity:  severity,
		NodeID:    nodeID,
		AlertType: alertType,
		Message:   message,
		Timestamp: time.Now(),
		Resolved:  false,
	}
	
	m.alerts = append(m.alerts, alert)
	m.alertID++
	m.totalAlertsGenerated++
	
	log.Printf("[%s] ALERT: %s - %s", severity, nodeID, message)
	
	// Auto-trigger failover for critical lag issues
	if severity == "critical" && alertType == "high_replication_lag" {
		m.triggerFailoverConsideration(nodeID)
	}
}

// triggerFailoverConsideration evaluates if failover should be triggered
func (m *ReplicationLagMonitor) triggerFailoverConsideration(nodeID string) {
	m.nodesMutex.RLock()
	node, exists := m.nodes[nodeID]
	m.nodesMutex.RUnlock()
	
	if !exists || node.NodeType == "master" {
		return // Don't failover masters automatically
	}
	
	regionConfig := m.regionConfig[node.Region]
	
	// Check if this is a critical system
	for _, criticalSystem := range regionConfig.CriticalSystems {
		if node.NodeType == criticalSystem {
			log.Printf("FAILOVER CONSIDERATION: Node %s (%s) in region %s has critical lag",
				nodeID, criticalSystem, node.Region)
			
			// In real system, this would trigger failover process
			m.generateAlert("info", nodeID, "failover_considered",
				fmt.Sprintf("Failover consideration triggered for critical system %s", criticalSystem))
			break
		}
	}
}

// StartMonitoring starts the monitoring process
func (m *ReplicationLagMonitor) StartMonitoring() {
	log.Println("Starting replication lag monitoring...")
	
	// Start monitoring goroutine
	go func() {
		ticker := time.NewTicker(m.monitoringInterval)
		defer ticker.Stop()
		
		for {
			select {
			case <-m.ctx.Done():
				log.Println("Monitoring stopped")
				return
			case <-ticker.C:
				m.performHealthCheck()
				m.cleanupOldAlerts()
			}
		}
	}()
	
	// Start metrics collection simulation
	go m.simulateMetricsCollection()
}

// performHealthCheck performs periodic health checks
func (m *ReplicationLagMonitor) performHealthCheck() {
	m.nodesMutex.RLock()
	defer m.nodesMutex.RUnlock()
	
	now := time.Now()
	staleThreshold := 30 * time.Second
	
	for nodeID, node := range m.nodes {
		// Check for stale nodes
		if now.Sub(node.LastUpdateTime) > staleThreshold {
			if node.ConnectionStatus != "stale" {
				node.ConnectionStatus = "stale"
				m.generateAlert("warning", nodeID, "node_stale",
					fmt.Sprintf("Node %s has not updated metrics for %v", 
						nodeID, now.Sub(node.LastUpdateTime)))
			}
		} else {
			if node.ConnectionStatus != "connected" {
				node.ConnectionStatus = "connected"
				// Resolve stale alert if exists
				m.resolveAlert(nodeID, "node_stale")
			}
		}
	}
}

// resolveAlert marks an alert as resolved
func (m *ReplicationLagMonitor) resolveAlert(nodeID, alertType string) {
	m.alertsMutex.Lock()
	defer m.alertsMutex.Unlock()
	
	for i := range m.alerts {
		if m.alerts[i].NodeID == nodeID && 
		   m.alerts[i].AlertType == alertType && 
		   !m.alerts[i].Resolved {
			m.alerts[i].Resolved = true
			now := time.Now()
			m.alerts[i].ResolvedAt = &now
			
			log.Printf("RESOLVED: Alert %s for node %s", alertType, nodeID)
			break
		}
	}
}

// cleanupOldAlerts removes old resolved alerts
func (m *ReplicationLagMonitor) cleanupOldAlerts() {
	m.alertsMutex.Lock()
	defer m.alertsMutex.Unlock()
	
	cutoff := time.Now().Add(-m.retentionPeriod)
	newAlerts := make([]Alert, 0)
	
	for _, alert := range m.alerts {
		if alert.Resolved && alert.ResolvedAt != nil && alert.ResolvedAt.Before(cutoff) {
			continue // Skip old resolved alerts
		}
		newAlerts = append(newAlerts, alert)
	}
	
	m.alerts = newAlerts
}

// simulateMetricsCollection simulates real-time metrics collection
func (m *ReplicationLagMonitor) simulateMetricsCollection() {
	// Register sample nodes for demonstration
	m.RegisterNode("hdfc-mumbai-master", "master", "mumbai")
	m.RegisterNode("hdfc-mumbai-slave1", "slave", "mumbai")
	m.RegisterNode("hdfc-mumbai-slave2", "slave", "mumbai")
	m.RegisterNode("icici-delhi-master", "master", "delhi")
	m.RegisterNode("icici-delhi-slave1", "slave", "delhi")
	m.RegisterNode("flipkart-bangalore-master", "master", "bangalore")
	m.RegisterNode("flipkart-bangalore-slave1", "slave", "bangalore")
	m.RegisterNode("flipkart-bangalore-slave2", "slave", "bangalore")
	m.RegisterNode("sbi-chennai-master", "master", "chennai")
	m.RegisterNode("sbi-kolkata-slave1", "slave", "kolkata")
	
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()
	
	sequenceNumbers := make(map[string]int64)
	
	for {
		select {
		case <-m.ctx.Done():
			return
		case <-ticker.C:
			// Simulate metrics for each node
			for nodeID, node := range m.nodes {
				// Simulate sequence number progression
				if _, exists := sequenceNumbers[nodeID]; !exists {
					sequenceNumbers[nodeID] = rand.Int63n(1000) + 1000
				}
				
				// Masters progress faster
				if node.NodeType == "master" {
					sequenceNumbers[nodeID] += rand.Int63n(50) + 20
				} else {
					// Slaves lag behind
					lagFactor := rand.Float64() * 0.8 + 0.1 // 10-90% of master progress
					sequenceNumbers[nodeID] += int64(float64(rand.Int63n(40)+10) * lagFactor)
				}
				
				// Simulate varying performance metrics
				throughput := m.simulateThroughput(node)
				errorRate := m.simulateErrorRate(node)
				networkLatency := m.simulateNetworkLatency(node)
				
				m.UpdateNodeMetrics(nodeID, sequenceNumbers[nodeID], 
					throughput, errorRate, networkLatency)
			}
		}
	}
}

// simulateThroughput simulates realistic throughput based on node type and region
func (m *ReplicationLagMonitor) simulateThroughput(node *ReplicationMetrics) float64 {
	baseThoughput := 100.0
	
	// Masters typically have higher throughput
	if node.NodeType == "master" {
		baseThoughput *= 1.5
	}
	
	// Regional variations
	switch node.Region {
	case "mumbai":
		baseThoughput *= 1.3 // Financial hub has higher activity
	case "bangalore":
		baseThoughput *= 1.2 // Tech hub
	case "delhi":
		baseThoughput *= 1.1
	default:
		baseThoughput *= 0.9
	}
	
	// Business hours boost
	if m.isBusinessHours(node.Region) {
		baseThoughput *= 1.4
	}
	
	// Add random variation
	variation := rand.Float64()*0.4 + 0.8 // 80-120% of base
	return baseThoughput * variation
}

// simulateErrorRate simulates realistic error rates
func (m *ReplicationLagMonitor) simulateErrorRate(node *ReplicationMetrics) float64 {
	baseErrorRate := 0.005 // 0.5% base error rate
	
	// Slaves might have slightly higher error rates
	if node.NodeType != "master" {
		baseErrorRate *= 1.2
	}
	
	// Regional network quality variations
	switch node.Region {
	case "mumbai", "bangalore":
		baseErrorRate *= 0.8 // Better infrastructure
	case "kolkata":
		baseErrorRate *= 1.3 // Some infrastructure challenges
	}
	
	// Occasional spike simulation
	if rand.Float64() < 0.05 { // 5% chance of error spike
		baseErrorRate *= rand.Float64()*5 + 2 // 2-7x spike
	}
	
	return math.Min(baseErrorRate, 0.1) // Cap at 10%
}

// simulateNetworkLatency simulates realistic network latencies
func (m *ReplicationLagMonitor) simulateNetworkLatency(node *ReplicationMetrics) int64 {
	config := m.regionConfig[node.Region]
	baseLatency := config.ExpectedLatencyMs
	
	// Add random variation (±50%)
	variation := rand.Float64()*0.5 - 0.25 // -25% to +25%
	latency := float64(baseLatency) * (1 + variation)
	
	// Occasional network spike
	if rand.Float64() < 0.02 { // 2% chance of spike
		latency *= rand.Float64()*3 + 2 // 2-5x spike
	}
	
	return int64(math.Max(latency, 1))
}

// GetDashboardData returns dashboard data for visualization
func (m *ReplicationLagMonitor) GetDashboardData() map[string]interface{} {
	m.nodesMutex.RLock()
	m.alertsMutex.RLock()
	defer m.nodesMutex.RUnlock()
	defer m.alertsMutex.RUnlock()
	
	// Group nodes by region
	regionData := make(map[string][]ReplicationMetrics)
	for _, node := range m.nodes {
		regionData[node.Region] = append(regionData[node.Region], *node)
	}
	
	// Get recent alerts
	recentAlerts := make([]Alert, 0)
	cutoff := time.Now().Add(-time.Hour) // Last hour
	for _, alert := range m.alerts {
		if alert.Timestamp.After(cutoff) {
			recentAlerts = append(recentAlerts, alert)
		}
	}
	
	// Calculate summary statistics
	var totalLag, maxLag int64
	var totalThroughput float64
	nodeCount := int64(len(m.nodes))
	
	for _, node := range m.nodes {
		totalLag += node.LagMilliseconds
		if node.LagMilliseconds > maxLag {
			maxLag = node.LagMilliseconds
		}
		totalThroughput += node.ThroughputOPS
	}
	
	avgLag := totalLag / nodeCount
	
	return map[string]interface{}{
		"regions":             regionData,
		"recent_alerts":       recentAlerts,
		"total_nodes":         nodeCount,
		"total_alerts":        m.totalAlertsGenerated,
		"average_lag_ms":      avgLag,
		"max_lag_ms":          maxLag,
		"total_throughput":    totalThroughput,
		"monitoring_uptime":   time.Since(time.Now().Add(-time.Hour)).String(),
	}
}

// HTTPHandler provides HTTP endpoints for monitoring
func (m *ReplicationLagMonitor) SetupHTTPEndpoints() {
	http.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		data := m.GetDashboardData()
		json.NewEncoder(w).Encode(data)
	})
	
	http.HandleFunc("/alerts", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		m.alertsMutex.RLock()
		alerts := make([]Alert, len(m.alerts))
		copy(alerts, m.alerts)
		m.alertsMutex.RUnlock()
		
		// Sort by timestamp, newest first
		sort.Slice(alerts, func(i, j int) bool {
			return alerts[i].Timestamp.After(alerts[j].Timestamp)
		})
		
		json.NewEncoder(w).Encode(alerts)
	})
	
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		health := map[string]interface{}{
			"status":           "healthy",
			"monitored_nodes":  len(m.nodes),
			"active_alerts":    len(m.alerts),
			"uptime":          time.Since(time.Now().Add(-time.Hour)).String(),
		}
		json.NewEncoder(w).Encode(health)
	})
}

// Stop stops the monitoring
func (m *ReplicationLagMonitor) Stop() {
	log.Println("Stopping replication lag monitor...")
	m.cancel()
}

// Main demonstration function
func main() {
	fmt.Println("================================================================================")
	fmt.Println("Database Replication Lag Monitoring System")
	fmt.Println("Episode 41: Database Replication Strategies")
	fmt.Println("Indian Banking और E-commerce Regional Monitoring")
	fmt.Println("================================================================================")
	
	// Create and start monitor
	monitor := NewReplicationLagMonitor()
	
	// Setup HTTP endpoints
	monitor.SetupHTTPEndpoints()
	
	// Start monitoring
	monitor.StartMonitoring()
	
	// Start HTTP server for dashboard
	go func() {
		log.Println("Starting HTTP dashboard on :8080")
		log.Println("Access metrics at: http://localhost:8080/metrics")
		log.Println("Access alerts at: http://localhost:8080/alerts")
		log.Println("Access health at: http://localhost:8080/health")
		
		if err := http.ListenAndServe(":8080", nil); err != nil {
			log.Printf("HTTP server error: %v", err)
		}
	}()
	
	// Run demonstration
	fmt.Println("\nStarting replication lag monitoring demonstration...")
	fmt.Println("Monitor will run for 60 seconds, generating realistic Indian banking/e-commerce metrics")
	fmt.Println("Check HTTP endpoints for real-time data")
	
	// Let it run for demonstration
	time.Sleep(60 * time.Second)
	
	// Print final summary
	fmt.Println("\n--- Monitoring Summary ---")
	data := monitor.GetDashboardData()
	
	fmt.Printf("Total Nodes Monitored: %v\n", data["total_nodes"])
	fmt.Printf("Total Alerts Generated: %v\n", data["total_alerts"])
	fmt.Printf("Average Replication Lag: %v ms\n", data["average_lag_ms"])
	fmt.Printf("Maximum Replication Lag: %v ms\n", data["max_lag_ms"])
	fmt.Printf("Total Throughput: %.1f ops/sec\n", data["total_throughput"])
	
	// Show recent alerts
	recentAlerts := data["recent_alerts"].([]Alert)
	if len(recentAlerts) > 0 {
		fmt.Printf("\nRecent Alerts (%d):\n", len(recentAlerts))
		for i, alert := range recentAlerts {
			if i >= 5 { // Show only first 5
				break
			}
			fmt.Printf("  [%s] %s: %s\n", alert.Severity, alert.NodeID, alert.Message)
		}
	}
	
	// Regional breakdown
	fmt.Println("\nRegional Breakdown:")
	regions := data["regions"].(map[string][]ReplicationMetrics)
	for region, nodes := range regions {
		fmt.Printf("  %s: %d nodes\n", region, len(nodes))
		
		var avgLag int64
		var avgThroughput float64
		for _, node := range nodes {
			avgLag += node.LagMilliseconds
			avgThroughput += node.ThroughputOPS
		}
		
		if len(nodes) > 0 {
			avgLag /= int64(len(nodes))
			avgThroughput /= float64(len(nodes))
			fmt.Printf("    Avg Lag: %d ms, Avg Throughput: %.1f ops/sec\n", avgLag, avgThroughput)
		}
	}
	
	// Stop monitoring
	monitor.Stop()
	
	fmt.Println("\nReplication lag monitoring demonstration completed!")
}