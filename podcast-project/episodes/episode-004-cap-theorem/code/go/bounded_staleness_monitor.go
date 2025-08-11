package main

/*
Bounded Staleness Monitor - Episode 4
व्यावहारिक Bounded Staleness का monitoring और measurement

यह system track करता है कि कितना stale data है across replicas।
Eventually consistent systems में data freshness को monitor करना जरूरी है।

Indian Context Examples:
- Flipkart product price staleness across regions  
- Paytm wallet balance consistency across apps
- Zomato restaurant availability sync delay
- WhatsApp message delivery lag tracking

Staleness Types:
1. Read Staleness - कितना पुराना data read किया
2. Write Staleness - write के बाद कितनी देर में visible
3. Replica Staleness - replicas के बीच time lag
4. Causal Staleness - causally related events का order
*/

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"sort"
	"sync"
	"time"
)

// StalenessType represents different types of staleness measurements
type StalenessType string

const (
	ReadStaleness    StalenessType = "read_staleness"
	WriteStaleness   StalenessType = "write_staleness"
	ReplicaStaleness StalenessType = "replica_staleness"
	CausalStaleness  StalenessType = "causal_staleness"
)

// DataRecord represents a piece of data with versioning info
type DataRecord struct {
	Key           string      `json:"key"`
	Value         interface{} `json:"value"`
	Version       int64       `json:"version"`
	WriteTime     time.Time   `json:"write_time"`
	OriginReplica string      `json:"origin_replica"`
	ReplicaTimes  map[string]time.Time `json:"replica_times"` // When each replica got this version
}

// StalenessMetric represents a staleness measurement
type StalenessMetric struct {
	Type              StalenessType `json:"type"`
	Key               string        `json:"key"`
	StalenessMs       float64       `json:"staleness_ms"`
	MeasurementTime   time.Time     `json:"measurement_time"`
	SourceReplica     string        `json:"source_replica"`
	TargetReplica     string        `json:"target_replica,omitempty"`
	ExpectedVersion   int64         `json:"expected_version,omitempty"`
	ActualVersion     int64         `json:"actual_version,omitempty"`
	WithinBounds      bool          `json:"within_bounds"`
}

// StalenessAlert represents an alert when staleness exceeds bounds
type StalenessAlert struct {
	AlertID         string        `json:"alert_id"`
	Type            StalenessType `json:"type"`
	Key             string        `json:"key"`
	StalenessMs     float64       `json:"staleness_ms"`
	BoundMs         float64       `json:"bound_ms"`
	Severity        string        `json:"severity"` // LOW, MEDIUM, HIGH, CRITICAL
	Message         string        `json:"message"`
	Timestamp       time.Time     `json:"timestamp"`
	AffectedReplicas []string     `json:"affected_replicas"`
}

// ReplicaNode represents a single replica in the system
type ReplicaNode struct {
	ID       string               `json:"id"`
	Location string               `json:"location"`
	Data     map[string]*DataRecord `json:"data"`
	mu       sync.RWMutex
}

// NewReplicaNode creates a new replica node
func NewReplicaNode(id, location string) *ReplicaNode {
	return &ReplicaNode{
		ID:       id,
		Location: location,
		Data:     make(map[string]*DataRecord),
	}
}

// WriteData writes data to this replica
func (rn *ReplicaNode) WriteData(key string, value interface{}, version int64, originReplica string) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	now := time.Now()
	
	record := &DataRecord{
		Key:           key,
		Value:         value,
		Version:       version,
		WriteTime:     now,
		OriginReplica: originReplica,
		ReplicaTimes:  make(map[string]time.Time),
	}
	
	// Track when this replica received the data
	record.ReplicaTimes[rn.ID] = now
	
	rn.Data[key] = record
	
	fmt.Printf("📝 Replica %s (%s): Wrote %s = %v (v%d) at %s\n", 
		rn.ID, rn.Location, key, value, version, now.Format("15:04:05.000"))
}

// ReadData reads data from this replica
func (rn *ReplicaNode) ReadData(key string) (*DataRecord, bool) {
	rn.mu.RLock()
	defer rn.mu.RUnlock()
	
	record, exists := rn.Data[key]
	if !exists {
		return nil, false
	}
	
	// Create a copy to avoid race conditions
	recordCopy := *record
	recordCopy.ReplicaTimes = make(map[string]time.Time)
	for k, v := range record.ReplicaTimes {
		recordCopy.ReplicaTimes[k] = v
	}
	
	return &recordCopy, true
}

// UpdateReplicaTime updates when this replica received a specific version
func (rn *ReplicaNode) UpdateReplicaTime(key string, replicaID string, receiveTime time.Time) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	if record, exists := rn.Data[key]; exists {
		record.ReplicaTimes[replicaID] = receiveTime
	}
}

// BoundedStalenessMonitor monitors staleness across replicas
type BoundedStalenessMonitor struct {
	replicas        map[string]*ReplicaNode
	stalenessBounds map[StalenessType]float64 // Maximum allowed staleness in milliseconds
	metrics         []StalenessMetric
	alerts          []StalenessAlert
	alertHandlers   []func(StalenessAlert)
	
	mu sync.RWMutex
	
	// Configuration
	monitorInterval time.Duration
	alertThreshold  float64 // Alert when staleness exceeds this multiplier of bound
	
	// Statistics
	stats StalenesStats
}

// StalenesStats holds monitoring statistics
type StalenesStats struct {
	TotalMeasurements   int64     `json:"total_measurements"`
	BoundViolations     int64     `json:"bound_violations"`
	TotalAlerts         int64     `json:"total_alerts"`
	AvgStaleness        float64   `json:"avg_staleness_ms"`
	MaxStaleness        float64   `json:"max_staleness_ms"`
	P95Staleness        float64   `json:"p95_staleness_ms"`
	P99Staleness        float64   `json:"p99_staleness_ms"`
	LastMeasurement     time.Time `json:"last_measurement"`
	HealthyReplicas     int       `json:"healthy_replicas"`
	UnhealthyReplicas   int       `json:"unhealthy_replicas"`
}

// NewBoundedStalenessMonitor creates a new staleness monitor
func NewBoundedStalenessMonitor() *BoundedStalenessMonitor {
	monitor := &BoundedStalenessMonitor{
		replicas:        make(map[string]*ReplicaNode),
		stalenessBounds: make(map[StalenessType]float64),
		metrics:         make([]StalenessMetric, 0),
		alerts:          make([]StalenessAlert, 0),
		alertHandlers:   make([]func(StalenessAlert), 0),
		monitorInterval: 5 * time.Second,
		alertThreshold:  1.5, // Alert at 1.5x the bound
	}
	
	// Set default staleness bounds (production values for Indian context)
	monitor.stalenessBounds[ReadStaleness] = 2000    // 2 seconds (Flipkart product prices)
	monitor.stalenessBounds[WriteStaleness] = 5000   // 5 seconds (Paytm balance updates)
	monitor.stalenessBounds[ReplicaStaleness] = 10000 // 10 seconds (WhatsApp message sync)
	monitor.stalenessBounds[CausalStaleness] = 1000  // 1 second (causally related events)
	
	fmt.Printf("📊 Bounded Staleness Monitor initialized\n")
	fmt.Printf("🎯 Staleness bounds: Read=%dms, Write=%dms, Replica=%dms, Causal=%dms\n",
		int(monitor.stalenessBounds[ReadStaleness]),
		int(monitor.stalenessBounds[WriteStaleness]),
		int(monitor.stalenessBounds[ReplicaStaleness]),
		int(monitor.stalenessBounds[CausalStaleness]))
	
	return monitor
}

// AddReplica adds a replica to monitor
func (bsm *BoundedStalenessMonitor) AddReplica(replica *ReplicaNode) {
	bsm.mu.Lock()
	defer bsm.mu.Unlock()
	
	bsm.replicas[replica.ID] = replica
	fmt.Printf("🔄 Added replica %s (%s) to staleness monitor\n", replica.ID, replica.Location)
}

// SetStalenessBound sets the staleness bound for a specific type
func (bsm *BoundedStalenessMonitor) SetStalenessBound(stalenessType StalenessType, boundMs float64) {
	bsm.mu.Lock()
	defer bsm.mu.Unlock()
	
	bsm.stalenessBounds[stalenessType] = boundMs
	fmt.Printf("⚙️ Set %s bound to %.0fms\n", stalenessType, boundMs)
}

// AddAlertHandler adds a handler for staleness alerts
func (bsm *BoundedStalenessMonitor) AddAlertHandler(handler func(StalenessAlert)) {
	bsm.mu.Lock()
	defer bsm.mu.Unlock()
	
	bsm.alertHandlers = append(bsm.alertHandlers, handler)
}

// StartMonitoring begins continuous staleness monitoring
func (bsm *BoundedStalenessMonitor) StartMonitoring() {
	fmt.Printf("▶️ Starting staleness monitoring (interval: %v)\n", bsm.monitorInterval)
	
	go func() {
		ticker := time.NewTicker(bsm.monitorInterval)
		defer ticker.Stop()
		
		for range ticker.C {
			bsm.measureStaleness()
			bsm.updateStatistics()
		}
	}()
}

// measureStaleness performs all types of staleness measurements
func (bsm *BoundedStalenessMonitor) measureStaleness() {
	bsm.mu.RLock()
	replicas := make([]*ReplicaNode, 0, len(bsm.replicas))
	for _, replica := range bsm.replicas {
		replicas = append(replicas, replica)
	}
	bsm.mu.RUnlock()
	
	if len(replicas) < 2 {
		return // Need at least 2 replicas for staleness measurement
	}
	
	// Measure read staleness
	bsm.measureReadStaleness(replicas)
	
	// Measure replica staleness
	bsm.measureReplicaStaleness(replicas)
	
	// Measure write staleness (requires write tracking)
	bsm.measureWriteStaleness(replicas)
}

// measureReadStaleness measures how stale the data is when reading from each replica
func (bsm *BoundedStalenessMonitor) measureReadStaleness(replicas []*ReplicaNode) {
	now := time.Now()
	
	// Get all unique keys across all replicas
	allKeys := make(map[string]bool)
	for _, replica := range replicas {
		replica.mu.RLock()
		for key := range replica.Data {
			allKeys[key] = true
		}
		replica.mu.RUnlock()
	}
	
	for key := range allKeys {
		// Find the most recent version across all replicas
		var mostRecentWrite time.Time
		var mostRecentVersion int64
		
		for _, replica := range replicas {
			if record, exists := replica.ReadData(key); exists {
				if record.WriteTime.After(mostRecentWrite) {
					mostRecentWrite = record.WriteTime
					mostRecentVersion = record.Version
				}
			}
		}
		
		// Measure staleness for each replica
		for _, replica := range replicas {
			if record, exists := replica.ReadData(key); exists {
				staleness := mostRecentWrite.Sub(record.WriteTime).Seconds() * 1000 // Convert to ms
				
				metric := StalenessMetric{
					Type:              ReadStaleness,
					Key:               key,
					StalenessMs:       staleness,
					MeasurementTime:   now,
					SourceReplica:     replica.ID,
					ExpectedVersion:   mostRecentVersion,
					ActualVersion:     record.Version,
					WithinBounds:      staleness <= bsm.stalenessBounds[ReadStaleness],
				}
				
				bsm.recordMetric(metric)
				
				// Check if alert is needed
				if staleness > bsm.stalenessBounds[ReadStaleness]*bsm.alertThreshold {
					bsm.generateAlert(metric, bsm.stalenessBounds[ReadStaleness])
				}
			}
		}
	}
}

// measureReplicaStaleness measures lag between replicas
func (bsm *BoundedStalenessMonitor) measureReplicaStaleness(replicas []*ReplicaNode) {
	now := time.Now()
	
	// Compare each pair of replicas
	for i := 0; i < len(replicas); i++ {
		for j := i + 1; j < len(replicas); j++ {
			replica1 := replicas[i]
			replica2 := replicas[j]
			
			bsm.compareReplicas(replica1, replica2, now)
			bsm.compareReplicas(replica2, replica1, now)
		}
	}
}

// compareReplicas compares staleness between two specific replicas
func (bsm *BoundedStalenessMonitor) compareReplicas(replica1, replica2 *ReplicaNode, now time.Time) {
	replica1.mu.RLock()
	data1 := make(map[string]*DataRecord)
	for k, v := range replica1.Data {
		data1[k] = v
	}
	replica1.mu.RUnlock()
	
	for key, record1 := range data1 {
		if record2, exists := replica2.ReadData(key); exists {
			// Calculate version lag
			versionLag := float64(record1.Version - record2.Version)
			
			// Calculate time lag
			timeLag := record1.WriteTime.Sub(record2.WriteTime).Seconds() * 1000
			if timeLag < 0 {
				timeLag = -timeLag // Use absolute value
			}
			
			metric := StalenessMetric{
				Type:            ReplicaStaleness,
				Key:             key,
				StalenessMs:     timeLag,
				MeasurementTime: now,
				SourceReplica:   replica1.ID,
				TargetReplica:   replica2.ID,
				ExpectedVersion: record1.Version,
				ActualVersion:   record2.Version,
				WithinBounds:    timeLag <= bsm.stalenessBounds[ReplicaStaleness] && versionLag <= 1,
			}
			
			bsm.recordMetric(metric)
			
			// Alert if staleness is too high
			if timeLag > bsm.stalenessBounds[ReplicaStaleness]*bsm.alertThreshold {
				bsm.generateAlert(metric, bsm.stalenessBounds[ReplicaStaleness])
			}
		}
	}
}

// measureWriteStaleness measures how long it takes for writes to be visible
func (bsm *BoundedStalenessMonitor) measureWriteStaleness(replicas []*ReplicaNode) {
	now := time.Now()
	
	for _, replica := range replicas {
		replica.mu.RLock()
		data := make(map[string]*DataRecord)
		for k, v := range replica.Data {
			data[k] = v
		}
		replica.mu.RUnlock()
		
		for key, record := range data {
			// Check how long it took to propagate to this replica
			if record.OriginReplica != replica.ID {
				if replicaTime, exists := record.ReplicaTimes[replica.ID]; exists {
					propagationTime := replicaTime.Sub(record.WriteTime).Seconds() * 1000
					
					metric := StalenessMetric{
						Type:            WriteStaleness,
						Key:             key,
						StalenessMs:     propagationTime,
						MeasurementTime: now,
						SourceReplica:   record.OriginReplica,
						TargetReplica:   replica.ID,
						ExpectedVersion: record.Version,
						ActualVersion:   record.Version,
						WithinBounds:    propagationTime <= bsm.stalenessBounds[WriteStaleness],
					}
					
					bsm.recordMetric(metric)
					
					if propagationTime > bsm.stalenessBounds[WriteStaleness]*bsm.alertThreshold {
						bsm.generateAlert(metric, bsm.stalenessBounds[WriteStaleness])
					}
				}
			}
		}
	}
}

// recordMetric records a staleness metric
func (bsm *BoundedStalenessMonitor) recordMetric(metric StalenessMetric) {
	bsm.mu.Lock()
	defer bsm.mu.Unlock()
	
	bsm.metrics = append(bsm.metrics, metric)
	bsm.stats.TotalMeasurements++
	
	if !metric.WithinBounds {
		bsm.stats.BoundViolations++
	}
	
	// Keep only last 10000 metrics to prevent memory leak
	if len(bsm.metrics) > 10000 {
		bsm.metrics = bsm.metrics[1000:] // Keep last 9000
	}
}

// generateAlert generates a staleness alert
func (bsm *BoundedStalenessMonitor) generateAlert(metric StalenessMetric, bound float64) {
	alert := StalenessAlert{
		AlertID:     fmt.Sprintf("alert_%d_%s", time.Now().Unix(), metric.Key),
		Type:        metric.Type,
		Key:         metric.Key,
		StalenessMs: metric.StalenessMs,
		BoundMs:     bound,
		Timestamp:   time.Now(),
		AffectedReplicas: []string{metric.SourceReplica},
	}
	
	if metric.TargetReplica != "" {
		alert.AffectedReplicas = append(alert.AffectedReplicas, metric.TargetReplica)
	}
	
	// Determine severity
	stalenessRatio := metric.StalenessMs / bound
	if stalenessRatio > 5 {
		alert.Severity = "CRITICAL"
	} else if stalenessRatio > 3 {
		alert.Severity = "HIGH"
	} else if stalenessRatio > 2 {
		alert.Severity = "MEDIUM"
	} else {
		alert.Severity = "LOW"
	}
	
	alert.Message = fmt.Sprintf("%s staleness for key '%s' is %.0fms (bound: %.0fms, ratio: %.1fx)",
		string(alert.Type), alert.Key, alert.StalenessMs, alert.BoundMs, stalenessRatio)
	
	bsm.mu.Lock()
	bsm.alerts = append(bsm.alerts, alert)
	bsm.stats.TotalAlerts++
	bsm.mu.Unlock()
	
	fmt.Printf("🚨 %s ALERT: %s\n", alert.Severity, alert.Message)
	
	// Trigger alert handlers
	for _, handler := range bsm.alertHandlers {
		go handler(alert)
	}
}

// updateStatistics updates monitoring statistics
func (bsm *BoundedStalenessMonitor) updateStatistics() {
	bsm.mu.Lock()
	defer bsm.mu.Unlock()
	
	if len(bsm.metrics) == 0 {
		return
	}
	
	// Calculate statistics from recent metrics (last 1000)
	recentMetrics := bsm.metrics
	if len(recentMetrics) > 1000 {
		recentMetrics = bsm.metrics[len(bsm.metrics)-1000:]
	}
	
	// Calculate average staleness
	totalStaleness := 0.0
	maxStaleness := 0.0
	stalenessValues := make([]float64, 0, len(recentMetrics))
	
	healthyReplicas := make(map[string]bool)
	unhealthyReplicas := make(map[string]bool)
	
	for _, metric := range recentMetrics {
		totalStaleness += metric.StalenessMs
		if metric.StalenessMs > maxStaleness {
			maxStaleness = metric.StalenessMs
		}
		stalenessValues = append(stalenessValues, metric.StalenessMs)
		
		// Track replica health
		if metric.WithinBounds {
			healthyReplicas[metric.SourceReplica] = true
		} else {
			unhealthyReplicas[metric.SourceReplica] = true
		}
		
		if metric.TargetReplica != "" {
			if metric.WithinBounds {
				healthyReplicas[metric.TargetReplica] = true
			} else {
				unhealthyReplicas[metric.TargetReplica] = true
			}
		}
	}
	
	bsm.stats.AvgStaleness = totalStaleness / float64(len(recentMetrics))
	bsm.stats.MaxStaleness = maxStaleness
	
	// Calculate percentiles
	sort.Float64s(stalenessValues)
	if len(stalenessValues) > 0 {
		p95Index := int(float64(len(stalenessValues)) * 0.95)
		p99Index := int(float64(len(stalenessValues)) * 0.99)
		
		if p95Index >= len(stalenessValues) {
			p95Index = len(stalenessValues) - 1
		}
		if p99Index >= len(stalenessValues) {
			p99Index = len(stalenessValues) - 1
		}
		
		bsm.stats.P95Staleness = stalenessValues[p95Index]
		bsm.stats.P99Staleness = stalenessValues[p99Index]
	}
	
	bsm.stats.HealthyReplicas = len(healthyReplicas)
	bsm.stats.UnhealthyReplicas = len(unhealthyReplicas)
	bsm.stats.LastMeasurement = time.Now()
}

// GetStatistics returns current staleness statistics
func (bsm *BoundedStalenessMonitor) GetStatistics() StalenesStats {
	bsm.mu.RLock()
	defer bsm.mu.RUnlock()
	
	return bsm.stats
}

// GetRecentAlerts returns recent alerts
func (bsm *BoundedStalenessMonitor) GetRecentAlerts(count int) []StalenessAlert {
	bsm.mu.RLock()
	defer bsm.mu.RUnlock()
	
	if len(bsm.alerts) <= count {
		return bsm.alerts
	}
	
	return bsm.alerts[len(bsm.alerts)-count:]
}

// PrintStatistics prints comprehensive statistics
func (bsm *BoundedStalenessMonitor) PrintStatistics() {
	stats := bsm.GetStatistics()
	
	fmt.Printf("\n📊 STALENESS MONITORING STATISTICS\n")
	fmt.Printf("=" + "=" * 45 + "\n")
	fmt.Printf("Total measurements: %d\n", stats.TotalMeasurements)
	fmt.Printf("Bound violations: %d (%.1f%%)\n", 
		stats.BoundViolations, 
		float64(stats.BoundViolations)/float64(stats.TotalMeasurements)*100)
	fmt.Printf("Total alerts: %d\n", stats.TotalAlerts)
	fmt.Printf("Average staleness: %.1fms\n", stats.AvgStaleness)
	fmt.Printf("Maximum staleness: %.1fms\n", stats.MaxStaleness)
	fmt.Printf("P95 staleness: %.1fms\n", stats.P95Staleness)
	fmt.Printf("P99 staleness: %.1fms\n", stats.P99Staleness)
	fmt.Printf("Healthy replicas: %d\n", stats.HealthyReplicas)
	fmt.Printf("Unhealthy replicas: %d\n", stats.UnhealthyReplicas)
	fmt.Printf("Last measurement: %s\n", stats.LastMeasurement.Format("15:04:05"))
	
	// Show recent alerts
	recentAlerts := bsm.GetRecentAlerts(5)
	if len(recentAlerts) > 0 {
		fmt.Printf("\n🚨 Recent Alerts (last %d):\n", len(recentAlerts))
		for _, alert := range recentAlerts {
			fmt.Printf("  [%s] %s: %s\n", 
				alert.Severity, 
				alert.Timestamp.Format("15:04:05"), 
				alert.Message)
		}
	}
}

// Simulate data replication with delays
func simulateDataReplication(source *ReplicaNode, targets []*ReplicaNode, key string, value interface{}, version int64) {
	// Write to source first
	source.WriteData(key, value, version, source.ID)
	
	// Simulate async replication to targets with varying delays
	for _, target := range targets {
		go func(t *ReplicaNode) {
			// Simulate network delay and processing time
			delay := time.Duration(50+len(t.Location)*10) * time.Millisecond // Different delays for different locations
			if t.Location == "Slow Region" {
				delay += time.Duration(2000) * time.Millisecond // Extra delay for slow regions
			}
			
			time.Sleep(delay)
			
			// Write to target
			t.WriteData(key, value, version, source.ID)
			
			// Update replica timing info
			receiveTime := time.Now()
			source.UpdateReplicaTime(key, t.ID, receiveTime)
			t.UpdateReplicaTime(key, t.ID, receiveTime)
			
		}(target)
	}
}

// Demo functions

func flipkartPriceStalenessDemo() {
	fmt.Printf("\n🛒 DEMO: Flipkart Product Price Staleness\n")
	fmt.Printf("-" + "-" * 40 + "\n")
	
	// Create replicas for different regions
	mumbaiReplica := NewReplicaNode("flipkart_mumbai", "Mumbai")
	delhiReplica := NewReplicaNode("flipkart_delhi", "Delhi")
	bangaloreReplica := NewReplicaNode("flipkart_bangalore", "Bangalore")
	slowReplica := NewReplicaNode("flipkart_remote", "Slow Region")
	
	// Create staleness monitor
	monitor := NewBoundedStalenessMonitor()
	monitor.AddReplica(mumbaiReplica)
	monitor.AddReplica(delhiReplica)
	monitor.AddReplica(bangaloreReplica)
	monitor.AddReplica(slowReplica)
	
	// Set bounds specific to e-commerce
	monitor.SetStalenessBound(ReadStaleness, 1000)    // 1s for product prices
	monitor.SetStalenessBound(ReplicaStaleness, 3000) // 3s for price consistency
	monitor.SetStalenessBound(WriteStaleness, 2000)   // 2s for price updates
	
	// Add alert handler
	monitor.AddAlertHandler(func(alert StalenessAlert) {
		fmt.Printf("📧 Email Alert: %s staleness alert for %s - %.0fms\n", 
			alert.Severity, alert.Key, alert.StalenessMs)
	})
	
	// Start monitoring
	monitor.StartMonitoring()
	
	// Simulate price updates
	products := []struct {
		key   string
		price float64
	}{
		{"iphone_14_pro", 79999.0},
		{"samsung_s23", 69999.0},
		{"oneplus_11", 59999.0},
	}
	
	allReplicas := []*ReplicaNode{delhiReplica, bangaloreReplica, slowReplica}
	
	fmt.Printf("💰 Simulating price updates...\n")
	
	version := int64(1)
	for _, product := range products {
		fmt.Printf("Updating %s price to ₹%.0f\n", product.key, product.price)
		simulateDataReplication(mumbaiReplica, allReplicas, product.key, product.price, version)
		version++
		time.Sleep(500 * time.Millisecond)
	}
	
	// Let the system stabilize and generate metrics
	time.Sleep(5 * time.Second)
	
	// Print statistics
	monitor.PrintStatistics()
}

func paytmBalanceStalenessDemo() {
	fmt.Printf("\n💰 DEMO: Paytm Balance Staleness Across Apps\n")
	fmt.Printf("-" + "-" * 45 + "\n")
	
	// Create replicas for different Paytm services
	mobileApp := NewReplicaNode("paytm_mobile", "Mumbai")
	webApp := NewReplicaNode("paytm_web", "Delhi") 
	merchantApp := NewReplicaNode("paytm_merchant", "Bangalore")
	
	monitor := NewBoundedStalenessMonitor()
	monitor.AddReplica(mobileApp)
	monitor.AddReplica(webApp)
	monitor.AddReplica(merchantApp)
	
	// Stricter bounds for financial data
	monitor.SetStalenessBound(ReadStaleness, 500)     // 500ms for balance reads
	monitor.SetStalenessBound(WriteStaleness, 1000)   // 1s for balance updates
	monitor.SetStalenessBound(ReplicaStaleness, 2000) // 2s for cross-app consistency
	
	monitor.StartMonitoring()
	
	// Simulate wallet transactions
	userBalances := map[string]float64{
		"user_rajesh": 5000.0,
		"user_priya":  3000.0,
		"user_amit":   7500.0,
	}
	
	allApps := []*ReplicaNode{webApp, merchantApp}
	version := int64(1)
	
	fmt.Printf("💳 Simulating wallet transactions...\n")
	
	for user, balance := range userBalances {
		// Initial balance
		simulateDataReplication(mobileApp, allApps, user, balance, version)
		version++
		time.Sleep(300 * time.Millisecond)
		
		// Debit transaction
		newBalance := balance - 500
		simulateDataReplication(mobileApp, allApps, user, newBalance, version)
		version++
		time.Sleep(300 * time.Millisecond)
	}
	
	// Wait for monitoring
	time.Sleep(6 * time.Second)
	
	monitor.PrintStatistics()
}

func main() {
	fmt.Printf("🇮🇳 Bounded Staleness Monitor - Indian Tech Context\n")
	fmt.Printf("=" + "=" * 55 + "\n")
	
	// Demo 1: Flipkart product price staleness
	flipkartPriceStalenessDemo()
	
	// Demo 2: Paytm balance staleness
	paytmBalanceStalenessDemo()
	
	fmt.Printf("\n✅ Bounded Staleness monitoring complete!\n")
	
	fmt.Printf("\n📚 KEY LEARNINGS:\n")
	fmt.Printf("1. Bounded staleness provides guarantees on data freshness\n")
	fmt.Printf("2. Different staleness types: read, write, replica, causal\n")  
	fmt.Printf("3. SLA monitoring for eventually consistent systems\n")
	fmt.Printf("4. Alerting when staleness exceeds business requirements\n")
	fmt.Printf("5. Indian applications:\n")
	fmt.Printf("   • Flipkart price consistency across regions\n")
	fmt.Printf("   • Paytm balance sync across mobile/web apps\n") 
	fmt.Printf("   • Zomato restaurant availability updates\n")
	fmt.Printf("   • WhatsApp message delivery lag tracking\n")
	fmt.Printf("6. Trade-offs:\n")
	fmt.Printf("   ✅ Better user experience than eventual consistency\n")
	fmt.Printf("   ✅ Configurable staleness bounds per use case\n")
	fmt.Printf("   ❌ More complex than strong consistency\n")
	fmt.Printf("   ❌ Monitoring overhead\n")
	fmt.Printf("7. Used by: Azure Cosmos DB, Amazon DynamoDB\n")
}