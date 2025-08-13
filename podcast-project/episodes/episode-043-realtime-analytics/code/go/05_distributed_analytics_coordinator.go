/*
Distributed Analytics Coordinator in Go
Episode 43: Real-time Analytics at Scale

Distributed analytics system with coordinator pattern and consensus
Use Case: Netflix viewing analytics across multiple data centers
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sort"
	"sync"
	"time"

	"github.com/gorilla/mux"
)

// ViewingEvent represents a Netflix viewing event
// Netflix viewing का एक event
type ViewingEvent struct {
	UserID          string    `json:"user_id"`
	ContentID       string    `json:"content_id"`
	ContentTitle    string    `json:"content_title"`
	ContentType     string    `json:"content_type"` // movie, series, documentary
	EventType       string    `json:"event_type"`   // start, pause, resume, stop, seek, complete
	Timestamp       time.Time `json:"timestamp"`
	Position        int64     `json:"position"`        // Position in seconds
	Duration        int64     `json:"duration"`        // Total duration in seconds
	Quality         string    `json:"quality"`         // 480p, 720p, 1080p, 4K
	DeviceType      string    `json:"device_type"`     // tv, mobile, laptop, tablet
	Location        string    `json:"location"`        // Country/Region
	SessionID       string    `json:"session_id"`
	BitrateKbps     int       `json:"bitrate_kbps"`
	BufferHealth    float64   `json:"buffer_health"`   // Buffer health percentage
	NetworkType     string    `json:"network_type"`    // wifi, cellular, ethernet
	SubscriptionTier string   `json:"subscription_tier"` // basic, standard, premium
	IsRewatch       bool      `json:"is_rewatch"`
	SeasonNumber    int       `json:"season_number,omitempty"`
	EpisodeNumber   int       `json:"episode_number,omitempty"`
}

// DataCenterMetrics represents aggregated metrics from a data center
// Data center के aggregated metrics
type DataCenterMetrics struct {
	DataCenterID        string    `json:"datacenter_id"`
	Region              string    `json:"region"`
	Timestamp           time.Time `json:"timestamp"`
	ActiveUsers         int64     `json:"active_users"`
	ConcurrentStreams   int64     `json:"concurrent_streams"`
	TotalBandwidthGbps  float64   `json:"total_bandwidth_gbps"`
	AverageQuality      string    `json:"average_quality"`
	BufferRatio         float64   `json:"buffer_ratio"`
	CompletionRate      float64   `json:"completion_rate"`
	TopContent          []ContentRank `json:"top_content"`
	QualityDistribution map[string]int64 `json:"quality_distribution"`
	DeviceDistribution  map[string]int64 `json:"device_distribution"`
	ErrorRate           float64   `json:"error_rate"`
	AvgBitrateKbps      int       `json:"avg_bitrate_kbps"`
	PeakConcurrency     int64     `json:"peak_concurrency"`
	GeographicSpread    map[string]int64 `json:"geographic_spread"`
}

type ContentRank struct {
	ContentID    string `json:"content_id"`
	ContentTitle string `json:"content_title"`
	ViewCount    int64  `json:"view_count"`
	WatchTime    int64  `json:"watch_time_hours"`
}

// GlobalMetrics represents aggregated global metrics
// सभी data centers का combined metrics
type GlobalMetrics struct {
	Timestamp           time.Time `json:"timestamp"`
	TotalActiveUsers    int64     `json:"total_active_users"`
	TotalConcurrentStreams int64  `json:"total_concurrent_streams"`
	TotalBandwidthGbps  float64   `json:"total_bandwidth_gbps"`
	GlobalCompletionRate float64  `json:"global_completion_rate"`
	GlobalErrorRate     float64   `json:"global_error_rate"`
	DataCenterCount     int       `json:"datacenter_count"`
	TopGlobalContent    []ContentRank `json:"top_global_content"`
	RegionalLeaders     map[string]string `json:"regional_leaders"` // region -> datacenter_id
	QualityTrends       map[string]float64 `json:"quality_trends"`
	DevicePreferences   map[string]float64 `json:"device_preferences"`
	ConsensusVersion    int64     `json:"consensus_version"`
	ConsensusLeader     string    `json:"consensus_leader"`
}

// DataCenterNode represents a single data center in the distributed system
// Distributed system का एक data center node
type DataCenterNode struct {
	ID               string
	Region           string
	IsActive         bool
	IsLeader         bool
	LastHeartbeat    time.Time
	LocalMetrics     *DataCenterMetrics
	EventBuffer      []ViewingEvent
	mutex            sync.RWMutex
	coordinator      *DistributedCoordinator
	
	// Analytics state
	activeUsers      map[string]bool
	activeStreams    map[string]*ViewingEvent
	contentViews     map[string]*ContentRank
	qualityStats     map[string]int64
	deviceStats      map[string]int64
	locationStats    map[string]int64
	bandwidthUsage   float64
	errorEvents      int64
	totalEvents      int64
}

func NewDataCenterNode(id, region string, coordinator *DistributedCoordinator) *DataCenterNode {
	return &DataCenterNode{
		ID:               id,
		Region:           region,
		IsActive:         true,
		LastHeartbeat:    time.Now(),
		EventBuffer:      make([]ViewingEvent, 0),
		coordinator:      coordinator,
		activeUsers:      make(map[string]bool),
		activeStreams:    make(map[string]*ViewingEvent),
		contentViews:     make(map[string]*ContentRank),
		qualityStats:     make(map[string]int64),
		deviceStats:      make(map[string]int64),
		locationStats:    make(map[string]int64),
	}
}

func (dcn *DataCenterNode) ProcessEvent(event ViewingEvent) {
	dcn.mutex.Lock()
	defer dcn.mutex.Unlock()
	
	dcn.totalEvents++
	
	// Update active users
	dcn.activeUsers[event.UserID] = true
	
	// Handle different event types
	switch event.EventType {
	case "start", "resume":
		dcn.activeStreams[event.SessionID] = &event
		dcn.updateContentStats(event)
		dcn.updateQualityStats(event)
		dcn.updateDeviceStats(event)
		dcn.updateLocationStats(event)
		dcn.updateBandwidthUsage(event)
		
	case "stop", "complete":
		delete(dcn.activeStreams, event.SessionID)
		dcn.updateContentStats(event)
		
	case "error":
		dcn.errorEvents++
		delete(dcn.activeStreams, event.SessionID)
		
	case "pause":
		// Stream remains active but not consuming bandwidth
		if stream, exists := dcn.activeStreams[event.SessionID]; exists {
			stream.Position = event.Position
		}
		
	case "seek":
		if stream, exists := dcn.activeStreams[event.SessionID]; exists {
			stream.Position = event.Position
		}
	}
	
	// Add to buffer for coordination
	dcn.EventBuffer = append(dcn.EventBuffer, event)
	if len(dcn.EventBuffer) > 1000 {
		dcn.EventBuffer = dcn.EventBuffer[len(dcn.EventBuffer)-1000:] // Keep last 1000 events
	}
}

func (dcn *DataCenterNode) updateContentStats(event ViewingEvent) {
	content, exists := dcn.contentViews[event.ContentID]
	if !exists {
		content = &ContentRank{
			ContentID:    event.ContentID,
			ContentTitle: event.ContentTitle,
		}
		dcn.contentViews[event.ContentID] = content
	}
	
	content.ViewCount++
	if event.EventType == "complete" && event.Duration > 0 {
		content.WatchTime += event.Duration / 3600 // Convert to hours
	}
}

func (dcn *DataCenterNode) updateQualityStats(event ViewingEvent) {
	dcn.qualityStats[event.Quality]++
}

func (dcn *DataCenterNode) updateDeviceStats(event ViewingEvent) {
	dcn.deviceStats[event.DeviceType]++
}

func (dcn *DataCenterNode) updateLocationStats(event ViewingEvent) {
	dcn.locationStats[event.Location]++
}

func (dcn *DataCenterNode) updateBandwidthUsage(event ViewingEvent) {
	// Estimate bandwidth based on quality and active streams
	qualityBandwidth := map[string]float64{
		"480p":  1.5,   // 1.5 Mbps
		"720p":  3.0,   // 3 Mbps
		"1080p": 5.0,   // 5 Mbps
		"4K":    15.0,  // 15 Mbps
	}
	
	if bandwidth, exists := qualityBandwidth[event.Quality]; exists {
		dcn.bandwidthUsage += bandwidth
	}
}

func (dcn *DataCenterNode) GenerateMetrics() *DataCenterMetrics {
	dcn.mutex.RLock()
	defer dcn.mutex.RUnlock()
	
	// Calculate top content
	var topContent []ContentRank
	for _, content := range dcn.contentViews {
		topContent = append(topContent, *content)
	}
	
	// Sort by view count
	sort.Slice(topContent, func(i, j int) bool {
		return topContent[i].ViewCount > topContent[j].ViewCount
	})
	
	// Limit to top 10
	if len(topContent) > 10 {
		topContent = topContent[:10]
	}
	
	// Calculate average quality
	totalQualityEvents := int64(0)
	qualityScore := 0.0
	qualityScores := map[string]float64{"480p": 1.0, "720p": 2.0, "1080p": 3.0, "4K": 4.0}
	
	for quality, count := range dcn.qualityStats {
		totalQualityEvents += count
		if score, exists := qualityScores[quality]; exists {
			qualityScore += score * float64(count)
		}
	}
	
	avgQuality := "720p" // default
	if totalQualityEvents > 0 {
		avgScore := qualityScore / float64(totalQualityEvents)
		if avgScore >= 3.5 {
			avgQuality = "4K"
		} else if avgScore >= 2.5 {
			avgQuality = "1080p"
		} else if avgScore >= 1.5 {
			avgQuality = "720p"
		} else {
			avgQuality = "480p"
		}
	}
	
	// Calculate completion rate
	completionRate := 0.0
	if dcn.totalEvents > 0 {
		completeEvents := int64(0)
		for _, event := range dcn.EventBuffer {
			if event.EventType == "complete" {
				completeEvents++
			}
		}
		completionRate = float64(completeEvents) / float64(dcn.totalEvents) * 100
	}
	
	// Calculate error rate
	errorRate := 0.0
	if dcn.totalEvents > 0 {
		errorRate = float64(dcn.errorEvents) / float64(dcn.totalEvents) * 100
	}
	
	// Calculate average bitrate
	totalBitrate := 0
	activeStreamCount := 0
	for _, stream := range dcn.activeStreams {
		totalBitrate += stream.BitrateKbps
		activeStreamCount++
	}
	
	avgBitrate := 0
	if activeStreamCount > 0 {
		avgBitrate = totalBitrate / activeStreamCount
	}
	
	return &DataCenterMetrics{
		DataCenterID:        dcn.ID,
		Region:              dcn.Region,
		Timestamp:           time.Now(),
		ActiveUsers:         int64(len(dcn.activeUsers)),
		ConcurrentStreams:   int64(len(dcn.activeStreams)),
		TotalBandwidthGbps:  dcn.bandwidthUsage / 1000, // Convert Mbps to Gbps
		AverageQuality:      avgQuality,
		BufferRatio:         dcn.calculateBufferRatio(),
		CompletionRate:      completionRate,
		TopContent:          topContent,
		QualityDistribution: make(map[string]int64),
		DeviceDistribution:  make(map[string]int64),
		ErrorRate:           errorRate,
		AvgBitrateKbps:      avgBitrate,
		PeakConcurrency:     int64(len(dcn.activeStreams)), // Simplified for demo
		GeographicSpread:    make(map[string]int64),
	}
	
	// Copy maps to avoid race conditions
	for k, v := range dcn.qualityStats {
		dcn.LocalMetrics.QualityDistribution[k] = v
	}
	for k, v := range dcn.deviceStats {
		dcn.LocalMetrics.DeviceDistribution[k] = v
	}
	for k, v := range dcn.locationStats {
		dcn.LocalMetrics.GeographicSpread[k] = v
	}
}

func (dcn *DataCenterNode) calculateBufferRatio() float64 {
	// Calculate average buffer health across active streams
	totalBuffer := 0.0
	count := 0
	
	for _, stream := range dcn.activeStreams {
		totalBuffer += stream.BufferHealth
		count++
	}
	
	if count > 0 {
		return totalBuffer / float64(count)
	}
	
	return 100.0 // Default healthy buffer
}

func (dcn *DataCenterNode) SendHeartbeat() {
	dcn.mutex.Lock()
	defer dcn.mutex.Unlock()
	
	dcn.LastHeartbeat = time.Now()
	dcn.LocalMetrics = dcn.GenerateMetrics()
	
	// Send to coordinator
	if dcn.coordinator != nil {
		dcn.coordinator.ReceiveHeartbeat(dcn.ID, dcn.LocalMetrics)
	}
}

// DistributedCoordinator manages multiple data center nodes
// Multiple data centers को coordinate करता है
type DistributedCoordinator struct {
	nodes              map[string]*DataCenterNode
	leaderID           string
	globalMetrics      *GlobalMetrics
	consensusVersion   int64
	mutex              sync.RWMutex
	electionInProgress bool
	httpServer         *http.Server
}

func NewDistributedCoordinator() *DistributedCoordinator {
	return &DistributedCoordinator{
		nodes:            make(map[string]*DataCenterNode),
		globalMetrics:    &GlobalMetrics{},
		consensusVersion: 1,
	}
}

func (dc *DistributedCoordinator) RegisterNode(node *DataCenterNode) {
	dc.mutex.Lock()
	defer dc.mutex.Unlock()
	
	dc.nodes[node.ID] = node
	node.coordinator = dc
	
	log.Printf("📍 Registered data center: %s (%s)", node.ID, node.Region)
	
	// Trigger leader election if no leader
	if dc.leaderID == "" {
		dc.electLeader()
	}
}

func (dc *DistributedCoordinator) ReceiveHeartbeat(nodeID string, metrics *DataCenterMetrics) {
	dc.mutex.Lock()
	defer dc.mutex.Unlock()
	
	if node, exists := dc.nodes[nodeID]; exists {
		node.LastHeartbeat = time.Now()
		node.LocalMetrics = metrics
	}
}

func (dc *DistributedCoordinator) electLeader() {
	if dc.electionInProgress {
		return
	}
	
	dc.electionInProgress = true
	defer func() { dc.electionInProgress = false }()
	
	log.Println("🗳️ Starting leader election...")
	
	// Simple leader election: choose node with highest total events processed
	var bestNode *DataCenterNode
	maxEvents := int64(0)
	
	for _, node := range dc.nodes {
		if node.IsActive && node.totalEvents > maxEvents {
			maxEvents = node.totalEvents
			bestNode = node
		}
	}
	
	if bestNode != nil {
		// Update leader
		for _, node := range dc.nodes {
			node.IsLeader = false
		}
		
		bestNode.IsLeader = true
		dc.leaderID = bestNode.ID
		dc.consensusVersion++
		
		log.Printf("👑 New leader elected: %s (%s) with %d events processed",
			bestNode.ID, bestNode.Region, bestNode.totalEvents)
	}
}

func (dc *DistributedCoordinator) checkNodeHealth() {
	dc.mutex.Lock()
	defer dc.mutex.Unlock()
	
	healthyNodes := 0
	leaderHealthy := false
	
	for nodeID, node := range dc.nodes {
		// Check if node is healthy (heartbeat within last 30 seconds)
		if time.Since(node.LastHeartbeat) > 30*time.Second {
			node.IsActive = false
			log.Printf("❌ Node %s marked as unhealthy", nodeID)
		} else {
			node.IsActive = true
			healthyNodes++
			
			if node.IsLeader {
				leaderHealthy = true
			}
		}
	}
	
	// Trigger leader election if current leader is unhealthy
	if !leaderHealthy && healthyNodes > 0 {
		log.Println("👑 Current leader is unhealthy, triggering new election")
		dc.electLeader()
	}
	
	log.Printf("💓 Health check: %d healthy nodes", healthyNodes)
}

func (dc *DistributedCoordinator) aggregateGlobalMetrics() {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()
	
	globalMetrics := &GlobalMetrics{
		Timestamp:           time.Now(),
		RegionalLeaders:     make(map[string]string),
		QualityTrends:       make(map[string]float64),
		DevicePreferences:   make(map[string]float64),
		ConsensusVersion:    dc.consensusVersion,
		ConsensusLeader:     dc.leaderID,
	}
	
	totalUsers := int64(0)
	totalStreams := int64(0)
	totalBandwidth := 0.0
	totalCompletionRate := 0.0
	totalErrorRate := 0.0
	activeNodeCount := 0
	
	// Content aggregation
	globalContentViews := make(map[string]*ContentRank)
	qualityTotals := make(map[string]int64)
	deviceTotals := make(map[string]int64)
	
	for _, node := range dc.nodes {
		if !node.IsActive || node.LocalMetrics == nil {
			continue
		}
		
		metrics := node.LocalMetrics
		activeNodeCount++
		
		// Aggregate basic metrics
		totalUsers += metrics.ActiveUsers
		totalStreams += metrics.ConcurrentStreams
		totalBandwidth += metrics.TotalBandwidthGbps
		totalCompletionRate += metrics.CompletionRate
		totalErrorRate += metrics.ErrorRate
		
		// Track regional leaders (node with highest concurrent streams per region)
		currentLeader, exists := globalMetrics.RegionalLeaders[node.Region]
		if !exists {
			globalMetrics.RegionalLeaders[node.Region] = node.ID
		} else {
			if existingNode, exists := dc.nodes[currentLeader]; exists {
				if metrics.ConcurrentStreams > existingNode.LocalMetrics.ConcurrentStreams {
					globalMetrics.RegionalLeaders[node.Region] = node.ID
				}
			}
		}
		
		// Aggregate content views
		for _, content := range metrics.TopContent {
			if global, exists := globalContentViews[content.ContentID]; exists {
				global.ViewCount += content.ViewCount
				global.WatchTime += content.WatchTime
			} else {
				globalContentViews[content.ContentID] = &ContentRank{
					ContentID:    content.ContentID,
					ContentTitle: content.ContentTitle,
					ViewCount:    content.ViewCount,
					WatchTime:    content.WatchTime,
				}
			}
		}
		
		// Aggregate quality stats
		for quality, count := range metrics.QualityDistribution {
			qualityTotals[quality] += count
		}
		
		// Aggregate device stats
		for device, count := range metrics.DeviceDistribution {
			deviceTotals[device] += count
		}
	}
	
	// Calculate global averages
	if activeNodeCount > 0 {
		globalMetrics.TotalActiveUsers = totalUsers
		globalMetrics.TotalConcurrentStreams = totalStreams
		globalMetrics.TotalBandwidthGbps = totalBandwidth
		globalMetrics.GlobalCompletionRate = totalCompletionRate / float64(activeNodeCount)
		globalMetrics.GlobalErrorRate = totalErrorRate / float64(activeNodeCount)
		globalMetrics.DataCenterCount = activeNodeCount
	}
	
	// Create global top content list
	var globalTopContent []ContentRank
	for _, content := range globalContentViews {
		globalTopContent = append(globalTopContent, *content)
	}
	
	// Sort by view count
	sort.Slice(globalTopContent, func(i, j int) bool {
		return globalTopContent[i].ViewCount > globalTopContent[j].ViewCount
	})
	
	// Limit to top 20
	if len(globalTopContent) > 20 {
		globalTopContent = globalTopContent[:20]
	}
	globalMetrics.TopGlobalContent = globalTopContent
	
	// Calculate quality trends (percentages)
	totalQualityEvents := int64(0)
	for _, count := range qualityTotals {
		totalQualityEvents += count
	}
	
	if totalQualityEvents > 0 {
		for quality, count := range qualityTotals {
			globalMetrics.QualityTrends[quality] = float64(count) / float64(totalQualityEvents) * 100
		}
	}
	
	// Calculate device preferences (percentages)
	totalDeviceEvents := int64(0)
	for _, count := range deviceTotals {
		totalDeviceEvents += count
	}
	
	if totalDeviceEvents > 0 {
		for device, count := range deviceTotals {
			globalMetrics.DevicePreferences[device] = float64(count) / float64(totalDeviceEvents) * 100
		}
	}
	
	dc.globalMetrics = globalMetrics
}

func (dc *DistributedCoordinator) StartPeriodicTasks() {
	// Health check every 10 seconds
	go func() {
		ticker := time.NewTicker(10 * time.Second)
		defer ticker.Stop()
		
		for range ticker.C {
			dc.checkNodeHealth()
		}
	}()
	
	// Global metrics aggregation every 5 seconds
	go func() {
		ticker := time.NewTicker(5 * time.Second)
		defer ticker.Stop()
		
		for range ticker.C {
			dc.aggregateGlobalMetrics()
		}
	}()
	
	// Periodic reporting every 30 seconds
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()
		
		for range ticker.C {
			dc.printGlobalReport()
		}
	}()
}

func (dc *DistributedCoordinator) printGlobalReport() {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()
	
	log.Println("\n🌍 === Netflix Global Analytics Report ===")
	log.Printf("👑 Leader: %s (Consensus v%d)", dc.leaderID, dc.consensusVersion)
	log.Printf("🏢 Active Data Centers: %d", dc.globalMetrics.DataCenterCount)
	log.Printf("👥 Global Active Users: %d", dc.globalMetrics.TotalActiveUsers)
	log.Printf("📺 Concurrent Streams: %d", dc.globalMetrics.TotalConcurrentStreams)
	log.Printf("🌐 Total Bandwidth: %.2f Gbps", dc.globalMetrics.TotalBandwidthGbps)
	log.Printf("✅ Completion Rate: %.2f%%", dc.globalMetrics.GlobalCompletionRate)
	log.Printf("❌ Error Rate: %.2f%%", dc.globalMetrics.GlobalErrorRate)
	
	if len(dc.globalMetrics.TopGlobalContent) > 0 {
		log.Printf("🔥 Top Content Globally:")
		for i, content := range dc.globalMetrics.TopGlobalContent {
			if i >= 5 { break }
			log.Printf("   %d. %s (%d views, %dh watch time)",
				i+1, content.ContentTitle, content.ViewCount, content.WatchTime)
		}
	}
	
	if len(dc.globalMetrics.RegionalLeaders) > 0 {
		log.Printf("🌎 Regional Leaders:")
		for region, leaderID := range dc.globalMetrics.RegionalLeaders {
			if node, exists := dc.nodes[leaderID]; exists {
				log.Printf("   %s: %s (%d streams)",
					region, leaderID, node.LocalMetrics.ConcurrentStreams)
			}
		}
	}
	
	log.Println("=========================================")
}

// HTTP API for external access
func (dc *DistributedCoordinator) setupHTTPAPI() {
	r := mux.NewRouter()
	
	r.HandleFunc("/metrics/global", dc.handleGlobalMetrics).Methods("GET")
	r.HandleFunc("/metrics/datacenter/{id}", dc.handleDataCenterMetrics).Methods("GET")
	r.HandleFunc("/health", dc.handleHealth).Methods("GET")
	r.HandleFunc("/leader", dc.handleLeaderInfo).Methods("GET")
	
	dc.httpServer = &http.Server{
		Addr:    ":8080",
		Handler: r,
	}
	
	go func() {
		log.Println("🌐 Starting HTTP API server on :8080")
		if err := dc.httpServer.ListenAndServe(); err != http.ErrServerClosed {
			log.Printf("HTTP server error: %v", err)
		}
	}()
}

func (dc *DistributedCoordinator) handleGlobalMetrics(w http.ResponseWriter, r *http.Request) {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(dc.globalMetrics)
}

func (dc *DistributedCoordinator) handleDataCenterMetrics(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	dcID := vars["id"]
	
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()
	
	if node, exists := dc.nodes[dcID]; exists && node.LocalMetrics != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(node.LocalMetrics)
	} else {
		http.Error(w, "Data center not found", http.StatusNotFound)
	}
}

func (dc *DistributedCoordinator) handleHealth(w http.ResponseWriter, r *http.Request) {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()
	
	healthyCount := 0
	for _, node := range dc.nodes {
		if node.IsActive {
			healthyCount++
		}
	}
	
	health := map[string]interface{}{
		"status":         "healthy",
		"total_nodes":    len(dc.nodes),
		"healthy_nodes":  healthyCount,
		"leader":         dc.leaderID,
		"consensus_version": dc.consensusVersion,
		"timestamp":      time.Now(),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(health)
}

func (dc *DistributedCoordinator) handleLeaderInfo(w http.ResponseWriter, r *http.Request) {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()
	
	var leaderInfo map[string]interface{}
	
	if leader, exists := dc.nodes[dc.leaderID]; exists {
		leaderInfo = map[string]interface{}{
			"leader_id":         leader.ID,
			"region":            leader.Region,
			"is_active":         leader.IsActive,
			"last_heartbeat":    leader.LastHeartbeat,
			"consensus_version": dc.consensusVersion,
			"metrics":           leader.LocalMetrics,
		}
	} else {
		leaderInfo = map[string]interface{}{
			"leader_id": nil,
			"message":   "No leader elected",
		}
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(leaderInfo)
}

// ViewingEventGenerator generates sample Netflix viewing events
// Testing के लिए sample viewing events generate करता है
type ViewingEventGenerator struct {
	contentLibrary []ContentInfo
	users          []string
	locations      []string
}

type ContentInfo struct {
	ID       string
	Title    string
	Type     string
	Duration int64 // in seconds
}

func NewViewingEventGenerator() *ViewingEventGenerator {
	content := []ContentInfo{
		{"CONTENT_001", "Stranger Things S4", "series", 3600},
		{"CONTENT_002", "The Crown", "series", 3000},
		{"CONTENT_003", "Extraction 2", "movie", 7200},
		{"CONTENT_004", "Money Heist", "series", 2700},
		{"CONTENT_005", "Bridgerton", "series", 3300},
		{"CONTENT_006", "Squid Game", "series", 3600},
		{"CONTENT_007", "The Witcher", "series", 3600},
		{"CONTENT_008", "Ozark", "series", 3300},
		{"CONTENT_009", "Bird Box", "movie", 7400},
		{"CONTENT_010", "Dark", "series", 3600},
	}
	
	users := make([]string, 1000)
	for i := range users {
		users[i] = fmt.Sprintf("USER_%06d", i+1)
	}
	
	locations := []string{"US", "BR", "IN", "UK", "CA", "AU", "DE", "FR", "JP", "KR"}
	
	return &ViewingEventGenerator{
		contentLibrary: content,
		users:          users,
		locations:      locations,
	}
}

func (veg *ViewingEventGenerator) GenerateEvent() ViewingEvent {
	content := veg.contentLibrary[rand.Intn(len(veg.contentLibrary))]
	user := veg.users[rand.Intn(len(veg.users))]
	location := veg.locations[rand.Intn(len(veg.locations))]
	
	eventTypes := []string{"start", "pause", "resume", "stop", "seek", "complete", "error"}
	eventWeights := []float64{0.25, 0.15, 0.15, 0.15, 0.10, 0.15, 0.05}
	eventType := weightedChoice(eventTypes, eventWeights)
	
	qualities := []string{"480p", "720p", "1080p", "4K"}
	qualityWeights := []float64{0.15, 0.30, 0.40, 0.15}
	quality := weightedChoice(qualities, qualityWeights)
	
	devices := []string{"tv", "mobile", "laptop", "tablet"}
	deviceWeights := []float64{0.40, 0.35, 0.20, 0.05}
	device := weightedChoice(devices, deviceWeights)
	
	networks := []string{"wifi", "cellular", "ethernet"}
	networkWeights := []float64{0.60, 0.25, 0.15}
	network := weightedChoice(networks, networkWeights)
	
	subscriptions := []string{"basic", "standard", "premium"}
	subWeights := []float64{0.30, 0.45, 0.25}
	subscription := weightedChoice(subscriptions, subWeights)
	
	// Generate realistic position and bitrate
	position := int64(rand.Intn(int(content.Duration)))
	if eventType == "start" {
		position = 0
	}
	
	bitrateMap := map[string]int{
		"480p":  1500,
		"720p":  3000,
		"1080p": 5000,
		"4K":    15000,
	}
	bitrate := bitrateMap[quality] + rand.Intn(1000) - 500 // ±500 kbps variation
	
	bufferHealth := 85.0 + rand.Float64()*15.0 // 85-100%
	if network == "cellular" {
		bufferHealth -= 10.0 // Lower buffer health on cellular
	}
	
	return ViewingEvent{
		UserID:           user,
		ContentID:        content.ID,
		ContentTitle:     content.Title,
		ContentType:      content.Type,
		EventType:        eventType,
		Timestamp:        time.Now(),
		Position:         position,
		Duration:         content.Duration,
		Quality:          quality,
		DeviceType:       device,
		Location:         location,
		SessionID:        fmt.Sprintf("SESSION_%s_%d", user, rand.Int63()),
		BitrateKbps:      bitrate,
		BufferHealth:     bufferHealth,
		NetworkType:      network,
		SubscriptionTier: subscription,
		IsRewatch:        rand.Float64() < 0.15, // 15% chance of rewatch
	}
}

func weightedChoice(choices []string, weights []float64) string {
	totalWeight := 0.0
	for _, weight := range weights {
		totalWeight += weight
	}
	
	r := rand.Float64() * totalWeight
	currentWeight := 0.0
	
	for i, weight := range weights {
		currentWeight += weight
		if r <= currentWeight {
			return choices[i]
		}
	}
	
	return choices[len(choices)-1]
}

func main() {
	log.Println("🎬 Starting Netflix Distributed Analytics Coordinator...")
	
	// Initialize coordinator
	coordinator := NewDistributedCoordinator()
	coordinator.setupHTTPAPI()
	coordinator.StartPeriodicTasks()
	
	// Create data center nodes
	dataCenters := []struct{ id, region string }{
		{"DC_US_EAST", "US_EAST"},
		{"DC_US_WEST", "US_WEST"},
		{"DC_EU_WEST", "EU_WEST"},
		{"DC_APAC", "APAC"},
		{"DC_LATAM", "LATAM"},
	}
	
	var nodes []*DataCenterNode
	for _, dc := range dataCenters {
		node := NewDataCenterNode(dc.id, dc.region, coordinator)
		coordinator.RegisterNode(node)
		nodes = append(nodes, node)
	}
	
	// Start event generation for each data center
	generator := NewViewingEventGenerator()
	
	for _, node := range nodes {
		go func(n *DataCenterNode) {
			ticker := time.NewTicker(200 * time.Millisecond) // 5 events per second per DC
			defer ticker.Stop()
			
			for range ticker.C {
				event := generator.GenerateEvent()
				n.ProcessEvent(event)
			}
		}(node)
	}
	
	// Start heartbeat sending
	for _, node := range nodes {
		go func(n *DataCenterNode) {
			ticker := time.NewTicker(5 * time.Second)
			defer ticker.Stop()
			
			for range ticker.C {
				n.SendHeartbeat()
			}
		}(node)
	}
	
	// Simulate node failures and recoveries
	go func() {
		time.Sleep(1 * time.Minute)
		
		// Simulate node failure
		if len(nodes) > 2 {
			failingNode := nodes[2]
			log.Printf("🔥 Simulating failure of %s", failingNode.ID)
			failingNode.IsActive = false
		}
		
		time.Sleep(30 * time.Second)
		
		// Simulate node recovery
		if len(nodes) > 2 {
			recoveringNode := nodes[2]
			log.Printf("🔧 Simulating recovery of %s", recoveringNode.ID)
			recoveringNode.IsActive = true
			recoveringNode.LastHeartbeat = time.Now()
		}
	}()
	
	// Run simulation
	log.Println("🎭 Running Netflix distributed analytics simulation...")
	log.Printf("🏢 %d data centers processing viewing events", len(nodes))
	log.Println("🌐 HTTP API available at http://localhost:8080")
	log.Println("   GET /metrics/global - Global analytics")
	log.Println("   GET /metrics/datacenter/{id} - Data center metrics")
	log.Println("   GET /health - System health")
	log.Println("   GET /leader - Leader information")
	
	time.Sleep(3 * time.Minute)
	
	// Final report
	log.Println("\n🏁 === Final Distributed Analytics Report ===")
	coordinator.mutex.RLock()
	finalGlobal := coordinator.globalMetrics
	coordinator.mutex.RUnlock()
	
	reportData := map[string]interface{}{
		"final_global_metrics": finalGlobal,
		"simulation_duration":  "3 minutes",
		"data_centers":         len(nodes),
		"events_per_second":    25, // 5 per DC * 5 DCs
	}
	
	reportJSON, _ := json.MarshalIndent(reportData, "", "  ")
	log.Printf("📊 Complete Report:\n%s", reportJSON)
	
	log.Println("✅ Netflix Distributed Analytics Coordinator Demo completed!")
}

/*
Key Features Demonstrated:

1. Distributed Architecture:
   - Multiple data center nodes
   - Coordinator pattern for global coordination
   - Leader election with consensus mechanism
   - Health monitoring and failure detection

2. Real-time Analytics:
   - Per-datacenter metrics aggregation
   - Global metrics consolidation
   - Top content tracking across regions
   - Quality and device distribution analysis

3. Fault Tolerance:
   - Automatic leader election
   - Node failure detection and recovery
   - Health check mechanisms
   - Graceful degradation

4. Netflix-Specific Metrics:
   - Concurrent streaming analytics
   - Content popularity tracking
   - Quality distribution analysis
   - Regional performance monitoring
   - Bandwidth utilization tracking

5. Production Features:
   - HTTP API for external integration
   - Consensus-based coordination
   - Thread-safe operations
   - Configurable reporting intervals
   - JSON-based metrics export

6. Scalability Features:
   - Horizontal scaling support
   - Regional data center coordination
   - Load distribution across nodes
   - Efficient aggregation algorithms

This system simulates Netflix's distributed analytics infrastructure
handling 25+ events per second across 5 global data centers with
automatic failover and real-time global metrics aggregation.
*/