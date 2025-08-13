/*
Episode 41: Database Replication Strategies
Go Example: Auto-scaling Replication System

यह advanced auto-scaling replication system है जो demand के based पर
automatically replication nodes को scale करता है। Indian e-commerce
और banking systems के realistic load patterns के साथ।

Real-world Use Case: Flipkart Sale Events और Banking Rush Hours
- Auto-scaling based on throughput and lag metrics
- Regional scaling for Indian markets
- Cost optimization with dynamic node management
- Peak hour handling (Big Billion Day, Banking hours)
*/

package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"math/rand"
	"sync"
	"time"
)

// ScalingMetrics represents metrics used for scaling decisions
type ScalingMetrics struct {
	Timestamp           time.Time `json:"timestamp"`
	TotalThroughputOPS  float64   `json:"total_throughput_ops"`
	AverageLatencyMs    int64     `json:"average_latency_ms"`
	ErrorRate           float64   `json:"error_rate"`
	CPUUtilization      float64   `json:"cpu_utilization"`
	MemoryUtilization   float64   `json:"memory_utilization"`
	NetworkUtilization  float64   `json:"network_utilization"`
	ActiveConnections   int       `json:"active_connections"`
	QueueDepth          int       `json:"queue_depth"`
}

// ReplicationNode represents a replication node
type ReplicationNode struct {
	ID               string    `json:"id"`
	Region           string    `json:"region"`
	NodeType         string    `json:"node_type"` // master, slave, read_replica
	Status           string    `json:"status"`    // starting, active, draining, stopping
	CreatedAt        time.Time `json:"created_at"`
	LastHealthCheck  time.Time `json:"last_health_check"`
	Capacity         NodeCapacity `json:"capacity"`
	CurrentLoad      NodeLoad     `json:"current_load"`
	CostPerHour      float64   `json:"cost_per_hour"`
}

// NodeCapacity represents the capacity of a node
type NodeCapacity struct {
	MaxThroughputOPS    float64 `json:"max_throughput_ops"`
	MaxConnections      int     `json:"max_connections"`
	MaxMemoryGB         float64 `json:"max_memory_gb"`
	MaxCPUCores         int     `json:"max_cpu_cores"`
}

// NodeLoad represents current load on a node
type NodeLoad struct {
	CurrentThroughputOPS float64 `json:"current_throughput_ops"`
	CurrentConnections   int     `json:"current_connections"`
	CPUUtilization      float64 `json:"cpu_utilization"`
	MemoryUtilization   float64 `json:"memory_utilization"`
	NetworkUtilization  float64 `json:"network_utilization"`
}

// ScalingRule defines when and how to scale
type ScalingRule struct {
	MetricType        string  `json:"metric_type"`
	Threshold         float64 `json:"threshold"`
	ComparisonType    string  `json:"comparison_type"` // greater_than, less_than
	ScaleDirection    string  `json:"scale_direction"` // up, down
	CooldownPeriod    time.Duration `json:"cooldown_period"`
	MinNodes          int     `json:"min_nodes"`
	MaxNodes          int     `json:"max_nodes"`
}

// RegionalConfig contains region-specific configuration
type RegionalConfig struct {
	RegionName          string
	PeakHours          []TimeRange
	ExpectedLoadPattern LoadPattern
	NodeConfigurations []NodeConfiguration
	CostMultiplier     float64
}

// TimeRange represents a time range for peak hours
type TimeRange struct {
	StartHour int
	EndHour   int
}

// LoadPattern represents expected load patterns
type LoadPattern struct {
	BaselineOPS     float64
	PeakMultiplier  float64
	SaleEventMultiplier float64
	BusinessHoursMultiplier float64
}

// NodeConfiguration defines node specs available in a region
type NodeConfiguration struct {
	Type            string
	CPUCores        int
	MemoryGB        float64
	MaxThroughputOPS float64
	CostPerHour     float64
}

// AutoScalingReplicationManager manages auto-scaling replication
type AutoScalingReplicationManager struct {
	ctx                context.Context
	cancel            context.CancelFunc
	nodes             map[string]*ReplicationNode
	nodesMutex        sync.RWMutex
	scalingRules      []ScalingRule
	regionalConfigs   map[string]RegionalConfig
	lastScalingAction time.Time
	
	// Current state
	currentMetrics    ScalingMetrics
	scalingHistory    []ScalingEvent
	costOptimization  bool
	
	// Configuration
	monitoringInterval time.Duration
	scalingInterval   time.Duration
	healthCheckInterval time.Duration
	
	// Indian e-commerce specific
	saleEventActive   bool
	saleEventStart    time.Time
	saleEventDuration time.Duration
	
	// Performance tracking
	totalScalingEvents int64
	costSavings       float64
}

// ScalingEvent represents a scaling action
type ScalingEvent struct {
	Timestamp   time.Time `json:"timestamp"`
	Action      string    `json:"action"` // scale_up, scale_down
	Region      string    `json:"region"`
	NodeID      string    `json:"node_id,omitempty"`
	Reason      string    `json:"reason"`
	MetricValue float64   `json:"metric_value"`
	Success     bool      `json:"success"`
}

// NewAutoScalingReplicationManager creates a new auto-scaling manager
func NewAutoScalingReplicationManager() *AutoScalingReplicationManager {
	ctx, cancel := context.WithCancel(context.Background())
	
	// Indian regional configurations
	regionalConfigs := map[string]RegionalConfig{
		"mumbai": {
			RegionName: "Mumbai Financial Hub",
			PeakHours: []TimeRange{
				{StartHour: 9, EndHour: 11},   // Morning banking rush
				{StartHour: 14, EndHour: 16},  // Afternoon banking
				{StartHour: 19, EndHour: 21},  // Evening e-commerce peak
			},
			ExpectedLoadPattern: LoadPattern{
				BaselineOPS:             500,  // 500 ops/sec baseline
				PeakMultiplier:          3.0,  // 3x during peak hours
				SaleEventMultiplier:     8.0,  // 8x during sale events
				BusinessHoursMultiplier: 2.0,  // 2x during business hours
			},
			NodeConfigurations: []NodeConfiguration{
				{Type: "small", CPUCores: 2, MemoryGB: 4, MaxThroughputOPS: 200, CostPerHour: 0.50},
				{Type: "medium", CPUCores: 4, MemoryGB: 8, MaxThroughputOPS: 500, CostPerHour: 1.00},
				{Type: "large", CPUCores: 8, MemoryGB: 16, MaxThroughputOPS: 1000, CostPerHour: 2.00},
				{Type: "xlarge", CPUCores: 16, MemoryGB: 32, MaxThroughputOPS: 2000, CostPerHour: 4.00},
			},
			CostMultiplier: 1.0, // Mumbai standard pricing
		},
		"bangalore": {
			RegionName: "Bangalore Tech Hub",
			PeakHours: []TimeRange{
				{StartHour: 10, EndHour: 12},
				{StartHour: 15, EndHour: 17},
				{StartHour: 20, EndHour: 22}, // Later peak for tech workers
			},
			ExpectedLoadPattern: LoadPattern{
				BaselineOPS:             600,
				PeakMultiplier:          4.0,  // Higher peak for e-commerce
				SaleEventMultiplier:     10.0, // Highest sale activity
				BusinessHoursMultiplier: 2.5,
			},
			NodeConfigurations: []NodeConfiguration{
				{Type: "small", CPUCores: 2, MemoryGB: 4, MaxThroughputOPS: 250, CostPerHour: 0.45},
				{Type: "medium", CPUCores: 4, MemoryGB: 8, MaxThroughputOPS: 600, CostPerHour: 0.90},
				{Type: "large", CPUCores: 8, MemoryGB: 16, MaxThroughputOPS: 1200, CostPerHour: 1.80},
				{Type: "xlarge", CPUCores: 16, MemoryGB: 32, MaxThroughputOPS: 2400, CostPerHour: 3.60},
			},
			CostMultiplier: 0.9, // Bangalore slightly cheaper
		},
		"delhi": {
			RegionName: "Delhi North Region",
			PeakHours: []TimeRange{
				{StartHour: 9, EndHour: 11},
				{StartHour: 14, EndHour: 16},
				{StartHour: 18, EndHour: 20},
			},
			ExpectedLoadPattern: LoadPattern{
				BaselineOPS:             400,
				PeakMultiplier:          2.5,
				SaleEventMultiplier:     6.0,
				BusinessHoursMultiplier: 1.8,
			},
			NodeConfigurations: []NodeConfiguration{
				{Type: "small", CPUCores: 2, MemoryGB: 4, MaxThroughputOPS: 180, CostPerHour: 0.55},
				{Type: "medium", CPUCores: 4, MemoryGB: 8, MaxThroughputOPS: 450, CostPerHour: 1.10},
				{Type: "large", CPUCores: 8, MemoryGB: 16, MaxThroughputOPS: 900, CostPerHour: 2.20},
				{Type: "xlarge", CPUCores: 16, MemoryGB: 32, MaxThroughputOPS: 1800, CostPerHour: 4.40},
			},
			CostMultiplier: 1.1, // Delhi slightly more expensive
		},
	}
	
	// Default scaling rules
	scalingRules := []ScalingRule{
		// Scale up rules
		{
			MetricType:     "cpu_utilization",
			Threshold:      75.0, // 75% CPU utilization
			ComparisonType: "greater_than",
			ScaleDirection: "up",
			CooldownPeriod: 5 * time.Minute,
			MinNodes:       1,
			MaxNodes:       20,
		},
		{
			MetricType:     "average_latency_ms",
			Threshold:      100.0, // 100ms latency
			ComparisonType: "greater_than",
			ScaleDirection: "up",
			CooldownPeriod: 3 * time.Minute,
			MinNodes:       1,
			MaxNodes:       20,
		},
		{
			MetricType:     "queue_depth",
			Threshold:      50.0, // 50 requests in queue
			ComparisonType: "greater_than",
			ScaleDirection: "up",
			CooldownPeriod: 2 * time.Minute,
			MinNodes:       1,
			MaxNodes:       20,
		},
		// Scale down rules
		{
			MetricType:     "cpu_utilization",
			Threshold:      30.0, // 30% CPU utilization
			ComparisonType: "less_than",
			ScaleDirection: "down",
			CooldownPeriod: 10 * time.Minute, // Longer cooldown for scale down
			MinNodes:       1,
			MaxNodes:       20,
		},
		{
			MetricType:     "average_latency_ms",
			Threshold:      20.0, // 20ms latency
			ComparisonType: "less_than",
			ScaleDirection: "down",
			CooldownPeriod: 15 * time.Minute,
			MinNodes:       1,
			MaxNodes:       20,
		},
	}
	
	return &AutoScalingReplicationManager{
		ctx:                 ctx,
		cancel:             cancel,
		nodes:              make(map[string]*ReplicationNode),
		scalingRules:       scalingRules,
		regionalConfigs:    regionalConfigs,
		lastScalingAction:  time.Now(),
		scalingHistory:     make([]ScalingEvent, 0),
		costOptimization:   true,
		monitoringInterval: 10 * time.Second,
		scalingInterval:    30 * time.Second,
		healthCheckInterval: 5 * time.Second,
		saleEventActive:    false,
	}
}

// StartAutoScaling starts the auto-scaling process
func (m *AutoScalingReplicationManager) StartAutoScaling() {
	log.Println("Starting auto-scaling replication manager...")
	
	// Initialize with minimum nodes for each region
	m.initializeMinimumNodes()
	
	// Start monitoring goroutine
	go func() {
		monitoringTicker := time.NewTicker(m.monitoringInterval)
		defer monitoringTicker.Stop()
		
		for {
			select {
			case <-m.ctx.Done():
				return
			case <-monitoringTicker.C:
				m.collectMetrics()
				m.performHealthChecks()
			}
		}
	}()
	
	// Start scaling decision goroutine
	go func() {
		scalingTicker := time.NewTicker(m.scalingInterval)
		defer scalingTicker.Stop()
		
		for {
			select {
			case <-m.ctx.Done():
				return
			case <-scalingTicker.C:
				m.evaluateScalingDecisions()
			}
		}
	}()
	
	// Start load simulation
	go m.simulateRealisticLoad()
}

// initializeMinimumNodes creates minimum required nodes for each region
func (m *AutoScalingReplicationManager) initializeMinimumNodes() {
	for region := range m.regionalConfigs {
		// Create one master node per region
		masterID := m.createNode(region, "master", "medium")
		log.Printf("Created master node %s in region %s", masterID, region)
		
		// Create one read replica per region
		replicaID := m.createNode(region, "read_replica", "small")
		log.Printf("Created read replica %s in region %s", replicaID, region)
	}
}

// createNode creates a new replication node
func (m *AutoScalingReplicationManager) createNode(region, nodeType, configType string) string {
	m.nodesMutex.Lock()
	defer m.nodesMutex.Unlock()
	
	regionConfig := m.regionalConfigs[region]
	
	// Find node configuration
	var nodeConfig NodeConfiguration
	for _, config := range regionConfig.NodeConfigurations {
		if config.Type == configType {
			nodeConfig = config
			break
		}
	}
	
	if nodeConfig.Type == "" {
		log.Printf("Warning: Node configuration %s not found for region %s", configType, region)
		return ""
	}
	
	nodeID := fmt.Sprintf("%s-%s-%s-%d", region, nodeType, configType, time.Now().Unix())
	
	node := &ReplicationNode{
		ID:              nodeID,
		Region:          region,
		NodeType:        nodeType,
		Status:          "starting",
		CreatedAt:       time.Now(),
		LastHealthCheck: time.Now(),
		Capacity: NodeCapacity{
			MaxThroughputOPS: nodeConfig.MaxThroughputOPS,
			MaxConnections:   int(nodeConfig.MaxThroughputOPS * 2), // 2 connections per OPS
			MaxMemoryGB:      nodeConfig.MemoryGB,
			MaxCPUCores:      nodeConfig.CPUCores,
		},
		CurrentLoad: NodeLoad{},
		CostPerHour: nodeConfig.CostPerHour * regionConfig.CostMultiplier,
	}
	
	m.nodes[nodeID] = node
	
	// Simulate node startup time (2-5 seconds)
	go func() {
		startupTime := time.Duration(rand.Intn(3)+2) * time.Second
		time.Sleep(startupTime)
		
		m.nodesMutex.Lock()
		if node, exists := m.nodes[nodeID]; exists {
			node.Status = "active"
		}
		m.nodesMutex.Unlock()
		
		log.Printf("Node %s is now active (startup took %v)", nodeID, startupTime)
	}()
	
	return nodeID
}

// collectMetrics collects current system metrics
func (m *AutoScalingReplicationManager) collectMetrics() {
	m.nodesMutex.RLock()
	defer m.nodesMutex.RUnlock()
	
	var totalThroughput float64
	var totalLatency int64
	var totalErrors float64
	var totalCPU, totalMemory, totalNetwork float64
	var totalConnections, totalQueue int
	var activeNodeCount int
	
	for _, node := range m.nodes {
		if node.Status == "active" {
			totalThroughput += node.CurrentLoad.CurrentThroughputOPS
			totalCPU += node.CurrentLoad.CPUUtilization
			totalMemory += node.CurrentLoad.MemoryUtilization
			totalNetwork += node.CurrentLoad.NetworkUtilization
			totalConnections += node.CurrentLoad.CurrentConnections
			activeNodeCount++
		}
	}
	
	if activeNodeCount > 0 {
		m.currentMetrics = ScalingMetrics{
			Timestamp:          time.Now(),
			TotalThroughputOPS: totalThroughput,
			AverageLatencyMs:   totalLatency / int64(activeNodeCount),
			ErrorRate:          totalErrors / float64(activeNodeCount),
			CPUUtilization:     totalCPU / float64(activeNodeCount),
			MemoryUtilization:  totalMemory / float64(activeNodeCount),
			NetworkUtilization: totalNetwork / float64(activeNodeCount),
			ActiveConnections:  totalConnections,
			QueueDepth:         totalQueue,
		}
	}
}

// performHealthChecks checks health of all nodes
func (m *AutoScalingReplicationManager) performHealthChecks() {
	m.nodesMutex.Lock()
	defer m.nodesMutex.Unlock()
	
	for nodeID, node := range m.nodes {
		if node.Status == "active" {
			// Simulate health check
			if m.simulateHealthCheck(node) {
				node.LastHealthCheck = time.Now()
			} else {
				log.Printf("Health check failed for node %s", nodeID)
				node.Status = "unhealthy"
				
				// Trigger replacement node creation
				go m.replaceUnhealthyNode(nodeID)
			}
		}
	}
}

// simulateHealthCheck simulates a health check
func (m *AutoScalingReplicationManager) simulateHealthCheck(node *ReplicationNode) bool {
	// 99% success rate for health checks
	if rand.Float64() < 0.01 {
		return false
	}
	
	// Higher failure rate if node is overloaded
	if node.CurrentLoad.CPUUtilization > 90 {
		return rand.Float64() < 0.95 // 95% success when overloaded
	}
	
	return true
}

// replaceUnhealthyNode replaces an unhealthy node
func (m *AutoScalingReplicationManager) replaceUnhealthyNode(unhealthyNodeID string) {
	m.nodesMutex.RLock()
	unhealthyNode, exists := m.nodes[unhealthyNodeID]
	m.nodesMutex.RUnlock()
	
	if !exists {
		return
	}
	
	log.Printf("Replacing unhealthy node %s in region %s", unhealthyNodeID, unhealthyNode.Region)
	
	// Create replacement node
	newNodeID := m.createNode(unhealthyNode.Region, unhealthyNode.NodeType, "medium")
	
	// Wait for new node to be active
	time.Sleep(5 * time.Second)
	
	// Remove unhealthy node
	m.nodesMutex.Lock()
	delete(m.nodes, unhealthyNodeID)
	m.nodesMutex.Unlock()
	
	m.recordScalingEvent("replace", unhealthyNode.Region, newNodeID, 
		"Replaced unhealthy node", 0, true)
	
	log.Printf("Successfully replaced node %s with %s", unhealthyNodeID, newNodeID)
}

// evaluateScalingDecisions evaluates whether scaling is needed
func (m *AutoScalingReplicationManager) evaluateScalingDecisions() {
	// Check cooldown period
	if time.Since(m.lastScalingAction) < 2*time.Minute {
		return
	}
	
	// Group nodes by region for regional scaling decisions
	regionNodes := m.groupNodesByRegion()
	
	for region, nodes := range regionNodes {
		m.evaluateRegionalScaling(region, nodes)
	}
}

// groupNodesByRegion groups nodes by their region
func (m *AutoScalingReplicationManager) groupNodesByRegion() map[string][]*ReplicationNode {
	m.nodesMutex.RLock()
	defer m.nodesMutex.RUnlock()
	
	regionNodes := make(map[string][]*ReplicationNode)
	
	for _, node := range m.nodes {
		if node.Status == "active" {
			regionNodes[node.Region] = append(regionNodes[node.Region], node)
		}
	}
	
	return regionNodes
}

// evaluateRegionalScaling evaluates scaling for a specific region
func (m *AutoScalingReplicationManager) evaluateRegionalScaling(region string, nodes []*ReplicationNode) {
	if len(nodes) == 0 {
		return
	}
	
	// Calculate regional metrics
	var avgCPU, avgMemory float64
	var avgLatency int64
	var totalThroughput float64
	var queueDepth int
	
	for _, node := range nodes {
		avgCPU += node.CurrentLoad.CPUUtilization
		avgMemory += node.CurrentLoad.MemoryUtilization
		totalThroughput += node.CurrentLoad.CurrentThroughputOPS
	}
	
	avgCPU /= float64(len(nodes))
	avgMemory /= float64(len(nodes))
	
	// Simulate latency and queue depth based on load
	avgLatency = int64(avgCPU * 2) // Rough approximation
	queueDepth = int(avgCPU / 10)  // Queue builds up with high CPU
	
	// Check scaling rules
	for _, rule := range m.scalingRules {
		if m.shouldApplyRule(rule, avgCPU, avgLatency, float64(queueDepth), len(nodes)) {
			m.executeScalingAction(rule, region, avgCPU, avgLatency, float64(queueDepth))
			break // Apply only one rule per evaluation
		}
	}
}

// shouldApplyRule checks if a scaling rule should be applied
func (m *AutoScalingReplicationManager) shouldApplyRule(rule ScalingRule, avgCPU float64, 
	avgLatency int64, queueDepth float64, currentNodeCount int) bool {
	
	// Check node count limits
	if rule.ScaleDirection == "up" && currentNodeCount >= rule.MaxNodes {
		return false
	}
	if rule.ScaleDirection == "down" && currentNodeCount <= rule.MinNodes {
		return false
	}
	
	// Check cooldown period
	if time.Since(m.lastScalingAction) < rule.CooldownPeriod {
		return false
	}
	
	// Check metric thresholds
	var metricValue float64
	switch rule.MetricType {
	case "cpu_utilization":
		metricValue = avgCPU
	case "average_latency_ms":
		metricValue = float64(avgLatency)
	case "queue_depth":
		metricValue = queueDepth
	default:
		return false
	}
	
	if rule.ComparisonType == "greater_than" {
		return metricValue > rule.Threshold
	} else if rule.ComparisonType == "less_than" {
		return metricValue < rule.Threshold
	}
	
	return false
}

// executeScalingAction executes a scaling action
func (m *AutoScalingReplicationManager) executeScalingAction(rule ScalingRule, region string,
	avgCPU float64, avgLatency int64, queueDepth float64) {
	
	var metricValue float64
	switch rule.MetricType {
	case "cpu_utilization":
		metricValue = avgCPU
	case "average_latency_ms":
		metricValue = float64(avgLatency)
	case "queue_depth":
		metricValue = queueDepth
	}
	
	reason := fmt.Sprintf("%s exceeded threshold: %.2f > %.2f", 
		rule.MetricType, metricValue, rule.Threshold)
	
	if rule.ScaleDirection == "down" {
		reason = fmt.Sprintf("%s below threshold: %.2f < %.2f", 
			rule.MetricType, metricValue, rule.Threshold)
	}
	
	success := false
	var nodeID string
	
	if rule.ScaleDirection == "up" {
		nodeID = m.scaleUp(region, reason)
		success = nodeID != ""
	} else {
		nodeID = m.scaleDown(region, reason)
		success = nodeID != ""
	}
	
	if success {
		m.lastScalingAction = time.Now()
		m.totalScalingEvents++
	}
	
	m.recordScalingEvent(rule.ScaleDirection, region, nodeID, reason, metricValue, success)
}

// scaleUp adds a new node to the region
func (m *AutoScalingReplicationManager) scaleUp(region, reason string) string {
	// Determine best node type based on current load and cost optimization
	nodeType := "read_replica" // Default to read replica for scaling
	configType := m.selectOptimalNodeConfig(region)
	
	nodeID := m.createNode(region, nodeType, configType)
	
	if nodeID != "" {
		log.Printf("Scaled UP: Created node %s in region %s - %s", nodeID, region, reason)
	}
	
	return nodeID
}

// scaleDown removes a node from the region
func (m *AutoScalingReplicationManager) scaleDown(region, reason string) string {
	// Find the best candidate for removal (least loaded, newest, read replica)
	candidates := m.findScaleDownCandidates(region)
	
	if len(candidates) == 0 {
		return ""
	}
	
	// Select candidate with lowest utilization
	var selectedNode *ReplicationNode
	lowestUtilization := 100.0
	
	for _, candidate := range candidates {
		if candidate.CurrentLoad.CPUUtilization < lowestUtilization {
			lowestUtilization = candidate.CurrentLoad.CPUUtilization
			selectedNode = candidate
		}
	}
	
	if selectedNode == nil {
		return ""
	}
	
	// Mark node for draining
	selectedNode.Status = "draining"
	
	// Simulate graceful shutdown
	go func() {
		time.Sleep(30 * time.Second) // 30 second drain period
		
		m.nodesMutex.Lock()
		delete(m.nodes, selectedNode.ID)
		m.nodesMutex.Unlock()
		
		log.Printf("Scaled DOWN: Removed node %s from region %s after draining", 
			selectedNode.ID, region)
	}()
	
	log.Printf("Scaled DOWN: Draining node %s in region %s - %s", 
		selectedNode.ID, region, reason)
	
	return selectedNode.ID
}

// findScaleDownCandidates finds nodes that can be safely removed
func (m *AutoScalingReplicationManager) findScaleDownCandidates(region string) []*ReplicationNode {
	m.nodesMutex.RLock()
	defer m.nodesMutex.RUnlock()
	
	var candidates []*ReplicationNode
	
	for _, node := range m.nodes {
		if node.Region == region && 
		   node.Status == "active" && 
		   node.NodeType != "master" && // Never remove masters
		   node.CurrentLoad.CPUUtilization < 50 { // Only low utilization nodes
			candidates = append(candidates, node)
		}
	}
	
	return candidates
}

// selectOptimalNodeConfig selects the best node configuration for scaling
func (m *AutoScalingReplicationManager) selectOptimalNodeConfig(region string) string {
	if m.costOptimization {
		// During normal times, prefer cost-effective nodes
		if m.saleEventActive {
			return "large" // Use larger nodes during sale events
		}
		if m.isPeakHour(region) {
			return "medium" // Medium nodes during peak hours
		}
		return "small" // Small nodes during off-peak
	}
	
	// Performance-optimized mode
	return "large"
}

// isPeakHour checks if current time is peak hour for the region
func (m *AutoScalingReplicationManager) isPeakHour(region string) bool {
	config, exists := m.regionalConfigs[region]
	if !exists {
		return false
	}
	
	currentHour := time.Now().Hour()
	
	for _, peakHour := range config.PeakHours {
		if currentHour >= peakHour.StartHour && currentHour <= peakHour.EndHour {
			return true
		}
	}
	
	return false
}

// recordScalingEvent records a scaling event for audit and analysis
func (m *AutoScalingReplicationManager) recordScalingEvent(action, region, nodeID, reason string, 
	metricValue float64, success bool) {
	
	event := ScalingEvent{
		Timestamp:   time.Now(),
		Action:      action,
		Region:      region,
		NodeID:      nodeID,
		Reason:      reason,
		MetricValue: metricValue,
		Success:     success,
	}
	
	m.scalingHistory = append(m.scalingHistory, event)
	
	// Keep only last 100 events
	if len(m.scalingHistory) > 100 {
		m.scalingHistory = m.scalingHistory[1:]
	}
}

// simulateRealisticLoad simulates realistic load patterns
func (m *AutoScalingReplicationManager) simulateRealisticLoad() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-m.ctx.Done():
			return
		case <-ticker.C:
			m.updateNodeLoads()
		}
	}
}

// updateNodeLoads updates the load on all nodes based on realistic patterns
func (m *AutoScalingReplicationManager) updateNodeLoads() {
	m.nodesMutex.Lock()
	defer m.nodesMutex.Unlock()
	
	for _, node := range m.nodes {
		if node.Status != "active" {
			continue
		}
		
		regionConfig := m.regionalConfigs[node.Region]
		baseLoad := m.calculateBaseLoad(regionConfig)
		
		// Distribute load across nodes in the region
		nodeLoad := m.distributeLoadToNode(node, baseLoad)
		
		// Update node metrics
		node.CurrentLoad.CurrentThroughputOPS = nodeLoad
		node.CurrentLoad.CPUUtilization = m.calculateCPUUtilization(node, nodeLoad)
		node.CurrentLoad.MemoryUtilization = m.calculateMemoryUtilization(node, nodeLoad)
		node.CurrentLoad.NetworkUtilization = m.calculateNetworkUtilization(node, nodeLoad)
		node.CurrentLoad.CurrentConnections = int(nodeLoad * 2) // 2 connections per OPS
	}
}

// calculateBaseLoad calculates base load for a region
func (m *AutoScalingReplicationManager) calculateBaseLoad(config RegionalConfig) float64 {
	baseLoad := config.ExpectedLoadPattern.BaselineOPS
	
	// Apply time-based multipliers
	if m.isPeakHourForConfig(config) {
		baseLoad *= config.ExpectedLoadPattern.PeakMultiplier
	}
	
	if m.saleEventActive {
		baseLoad *= config.ExpectedLoadPattern.SaleEventMultiplier
	}
	
	// Add random variation (±20%)
	variation := rand.Float64()*0.4 - 0.2 // -20% to +20%
	baseLoad *= (1 + variation)
	
	return baseLoad
}

// isPeakHourForConfig checks peak hour for specific config
func (m *AutoScalingReplicationManager) isPeakHourForConfig(config RegionalConfig) bool {
	currentHour := time.Now().Hour()
	
	for _, peakHour := range config.PeakHours {
		if currentHour >= peakHour.StartHour && currentHour <= peakHour.EndHour {
			return true
		}
	}
	
	return false
}

// distributeLoadToNode distributes load to a specific node
func (m *AutoScalingReplicationManager) distributeLoadToNode(node *ReplicationNode, totalRegionLoad float64) float64 {
	// Count active nodes in the same region
	activeNodesInRegion := 0
	totalCapacityInRegion := 0.0
	
	for _, otherNode := range m.nodes {
		if otherNode.Region == node.Region && otherNode.Status == "active" {
			activeNodesInRegion++
			totalCapacityInRegion += otherNode.Capacity.MaxThroughputOPS
		}
	}
	
	if activeNodesInRegion == 0 || totalCapacityInRegion == 0 {
		return 0
	}
	
	// Distribute load proportionally based on node capacity
	nodeLoadRatio := node.Capacity.MaxThroughputOPS / totalCapacityInRegion
	nodeLoad := totalRegionLoad * nodeLoadRatio
	
	// Cap at node's maximum capacity
	return math.Min(nodeLoad, node.Capacity.MaxThroughputOPS)
}

// calculateCPUUtilization calculates CPU utilization based on load
func (m *AutoScalingReplicationManager) calculateCPUUtilization(node *ReplicationNode, load float64) float64 {
	utilizationRatio := load / node.Capacity.MaxThroughputOPS
	baseUtilization := utilizationRatio * 80 // Base utilization up to 80%
	
	// Add some overhead and variation
	overhead := rand.Float64() * 10 // 0-10% overhead
	return math.Min(baseUtilization+overhead, 100)
}

// calculateMemoryUtilization calculates memory utilization
func (m *AutoScalingReplicationManager) calculateMemoryUtilization(node *ReplicationNode, load float64) float64 {
	utilizationRatio := load / node.Capacity.MaxThroughputOPS
	baseUtilization := utilizationRatio * 60 // Memory grows slower than CPU
	
	overhead := rand.Float64() * 15 // 0-15% overhead
	return math.Min(baseUtilization+overhead, 95)
}

// calculateNetworkUtilization calculates network utilization
func (m *AutoScalingReplicationManager) calculateNetworkUtilization(node *ReplicationNode, load float64) float64 {
	utilizationRatio := load / node.Capacity.MaxThroughputOPS
	baseUtilization := utilizationRatio * 40 // Network usage is lower
	
	overhead := rand.Float64() * 20 // 0-20% overhead
	return math.Min(baseUtilization+overhead, 90)
}

// StartSaleEvent simulates a sale event (like Big Billion Day)
func (m *AutoScalingReplicationManager) StartSaleEvent(duration time.Duration) {
	log.Printf("🎉 Starting sale event for %v", duration)
	
	m.saleEventActive = true
	m.saleEventStart = time.Now()
	m.saleEventDuration = duration
	
	// Schedule end of sale event
	go func() {
		time.Sleep(duration)
		m.saleEventActive = false
		log.Println("Sale event ended")
	}()
}

// GetSystemStatus returns current system status
func (m *AutoScalingReplicationManager) GetSystemStatus() map[string]interface{} {
	m.nodesMutex.RLock()
	defer m.nodesMutex.RUnlock()
	
	// Count nodes by region and status
	regionStats := make(map[string]map[string]int)
	totalCost := 0.0
	
	for _, node := range m.nodes {
		if regionStats[node.Region] == nil {
			regionStats[node.Region] = make(map[string]int)
		}
		regionStats[node.Region][node.Status]++
		
		if node.Status == "active" {
			totalCost += node.CostPerHour
		}
	}
	
	return map[string]interface{}{
		"total_nodes":        len(m.nodes),
		"total_scaling_events": m.totalScalingEvents,
		"current_cost_per_hour": totalCost,
		"sale_event_active":   m.saleEventActive,
		"region_stats":       regionStats,
		"current_metrics":    m.currentMetrics,
		"recent_events":      m.getRecentScalingEvents(10),
	}
}

// getRecentScalingEvents returns recent scaling events
func (m *AutoScalingReplicationManager) getRecentScalingEvents(count int) []ScalingEvent {
	if len(m.scalingHistory) <= count {
		return m.scalingHistory
	}
	
	return m.scalingHistory[len(m.scalingHistory)-count:]
}

// Stop stops the auto-scaling manager
func (m *AutoScalingReplicationManager) Stop() {
	log.Println("Stopping auto-scaling replication manager...")
	m.cancel()
}

// Main demonstration function
func main() {
	fmt.Println("================================================================================")
	fmt.Println("Auto-scaling Replication System")
	fmt.Println("Episode 41: Database Replication Strategies")
	fmt.Println("Indian E-commerce और Banking Auto-scaling Patterns")
	fmt.Println("================================================================================")
	
	// Create and start auto-scaling manager
	manager := NewAutoScalingReplicationManager()
	manager.StartAutoScaling()
	
	fmt.Println("\nStarting auto-scaling demonstration...")
	fmt.Println("Simulating realistic Indian e-commerce and banking load patterns")
	
	// Let initial setup complete
	time.Sleep(10 * time.Second)
	
	// Print initial status
	fmt.Println("\n--- Initial System Status ---")
	status := manager.GetSystemStatus()
	fmt.Printf("Total Nodes: %v\n", status["total_nodes"])
	fmt.Printf("Current Cost/Hour: ₹%.2f\n", status["current_cost_per_hour"])
	
	// Simulate a sale event after 20 seconds
	go func() {
		time.Sleep(20 * time.Second)
		manager.StartSaleEvent(30 * time.Second)
	}()
	
	// Monitor for 2 minutes
	monitoringDuration := 2 * time.Minute
	start := time.Now()
	
	for time.Since(start) < monitoringDuration {
		time.Sleep(15 * time.Second)
		
		status := manager.GetSystemStatus()
		fmt.Printf("\n--- Status Update (%.0fs elapsed) ---\n", time.Since(start).Seconds())
		fmt.Printf("Total Nodes: %v\n", status["total_nodes"])
		fmt.Printf("Scaling Events: %v\n", status["total_scaling_events"])
		fmt.Printf("Cost/Hour: ₹%.2f\n", status["current_cost_per_hour"])
		fmt.Printf("Sale Event: %v\n", status["sale_event_active"])
		
		// Show regional breakdown
		regionStats := status["region_stats"].(map[string]map[string]int)
		fmt.Println("Regional Node Distribution:")
		for region, stats := range regionStats {
			fmt.Printf("  %s: ", region)
			for status, count := range stats {
				fmt.Printf("%s=%d ", status, count)
			}
			fmt.Println()
		}
		
		// Show recent scaling events
		recentEvents := status["recent_events"].([]ScalingEvent)
		if len(recentEvents) > 0 {
			fmt.Printf("Recent Scaling Events (%d):\n", len(recentEvents))
			for i, event := range recentEvents {
				if i >= 3 { // Show only last 3
					break
				}
				fmt.Printf("  [%s] %s in %s: %s\n", 
					event.Timestamp.Format("15:04:05"), event.Action, event.Region, event.Reason)
			}
		}
	}
	
	// Final summary
	fmt.Println("\n--- Final Summary ---")
	finalStatus := manager.GetSystemStatus()
	fmt.Printf("Total Scaling Events: %v\n", finalStatus["total_scaling_events"])
	fmt.Printf("Final Cost/Hour: ₹%.2f\n", finalStatus["current_cost_per_hour"])
	
	allEvents := finalStatus["recent_events"].([]ScalingEvent)
	scaleUpEvents := 0
	scaleDownEvents := 0
	
	for _, event := range allEvents {
		if event.Action == "scale_up" {
			scaleUpEvents++
		} else if event.Action == "scale_down" {
			scaleDownEvents++
		}
	}
	
	fmt.Printf("Scale Up Events: %d\n", scaleUpEvents)
	fmt.Printf("Scale Down Events: %d\n", scaleDownEvents)
	
	regionStats := finalStatus["region_stats"].(map[string]map[string]int)
	fmt.Println("\nFinal Regional Distribution:")
	for region, stats := range regionStats {
		total := 0
		for _, count := range stats {
			total += count
		}
		fmt.Printf("  %s: %d total nodes\n", region, total)
	}
	
	// Stop the manager
	manager.Stop()
	
	fmt.Println("\nAuto-scaling replication demonstration completed!")
}