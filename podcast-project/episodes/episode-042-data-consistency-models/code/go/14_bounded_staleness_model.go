/*
Bounded Staleness Consistency Model
Data maximum X seconds purana ho sakta hai
Example: Stock prices, Sports scores, Analytics dashboards
*/

package main

import (
	"fmt"
	"log"
	"math/rand"
	"sort"
	"sync"
	"time"
)

// StalenessRecord represents data with staleness bounds
type StalenessRecord struct {
	Key              string
	Value            interface{}
	Version          int64
	WriteTimestamp   time.Time
	NodeID           string
	StalenessBound   time.Duration // Maximum acceptable staleness
}

// IsWithinBounds checks if the record is within staleness bounds
func (r *StalenessRecord) IsWithinBounds(now time.Time) bool {
	age := now.Sub(r.WriteTimestamp)
	return age <= r.StalenessBound
}

// GetAge returns the age of the record
func (r *StalenessRecord) GetAge(now time.Time) time.Duration {
	return now.Sub(r.WriteTimestamp)
}

// BoundedStalenessNode represents a distributed node with staleness tracking
type BoundedStalenessNode struct {
	NodeID         string
	Location       string
	Data           map[string]*StalenessRecord
	SyncDelay      time.Duration
	IsOnline       bool
	DefaultBounds  map[string]time.Duration // Key prefix -> default staleness bound
	VersionCounters map[string]int64
	mutex          sync.RWMutex
}

// NewBoundedStalenessNode creates a new node
func NewBoundedStalenessNode(nodeID, location string, syncDelay time.Duration) *BoundedStalenessNode {
	return &BoundedStalenessNode{
		NodeID:          nodeID,
		Location:        location,
		Data:            make(map[string]*StalenessRecord),
		SyncDelay:       syncDelay,
		IsOnline:        true,
		DefaultBounds:   make(map[string]time.Duration),
		VersionCounters: make(map[string]int64),
	}
}

// SetDefaultStaleness sets default staleness bound for key patterns
func (n *BoundedStalenessNode) SetDefaultStaleness(keyPrefix string, bound time.Duration) {
	n.mutex.Lock()
	defer n.mutex.Unlock()
	n.DefaultBounds[keyPrefix] = bound
	log.Printf("[%s] Set default staleness for '%s': %v", n.NodeID, keyPrefix, bound)
}

// getStalenessBound returns appropriate staleness bound for a key
func (n *BoundedStalenessNode) getStalenessBound(key string) time.Duration {
	// Check for matching prefix
	for prefix, bound := range n.DefaultBounds {
		if len(key) >= len(prefix) && key[:len(prefix)] == prefix {
			return bound
		}
	}
	
	// Default to 1 minute if no specific bound set
	return time.Minute
}

// Write writes data with timestamp and staleness bounds
func (n *BoundedStalenessNode) Write(key string, value interface{}, customBound *time.Duration) (*StalenessRecord, error) {
	if !n.IsOnline {
		return nil, fmt.Errorf("node %s is offline", n.NodeID)
	}

	n.mutex.Lock()
	defer n.mutex.Unlock()

	// Increment version
	n.VersionCounters[key]++
	version := n.VersionCounters[key]

	// Determine staleness bound
	stalenessBound := n.getStalenessBound(key)
	if customBound != nil {
		stalenessBound = *customBound
	}

	record := &StalenessRecord{
		Key:            key,
		Value:          value,
		Version:        version,
		WriteTimestamp: time.Now(),
		NodeID:         n.NodeID,
		StalenessBound: stalenessBound,
	}

	n.Data[key] = record
	log.Printf("[%s] Write: %s = %v (v%d, staleness: %v)", 
		n.NodeID, key, value, version, stalenessBound)

	return record, nil
}

// ReadWithinBounds reads data only if within staleness bounds
func (n *BoundedStalenessNode) ReadWithinBounds(key string) (*StalenessRecord, error) {
	// Simulate network delay
	time.Sleep(n.SyncDelay)

	if !n.IsOnline {
		return nil, fmt.Errorf("node %s is offline", n.NodeID)
	}

	n.mutex.RLock()
	defer n.mutex.RUnlock()

	record, exists := n.Data[key]
	if !exists {
		return nil, fmt.Errorf("key %s not found in node %s", key, n.NodeID)
	}

	now := time.Now()
	if !record.IsWithinBounds(now) {
		age := record.GetAge(now)
		return nil, fmt.Errorf("data too stale: age %v exceeds bound %v", age, record.StalenessBound)
	}

	log.Printf("[%s] Read: %s = %v (v%d, age: %v)", 
		n.NodeID, key, record.Value, record.Version, record.GetAge(now))

	return record, nil
}

// ReadAnyVersion reads data regardless of staleness (for comparison)
func (n *BoundedStalenessNode) ReadAnyVersion(key string) (*StalenessRecord, error) {
	time.Sleep(n.SyncDelay)

	if !n.IsOnline {
		return nil, fmt.Errorf("node %s is offline", n.NodeID)
	}

	n.mutex.RLock()
	defer n.mutex.RUnlock()

	if record, exists := n.Data[key]; exists {
		return record, nil
	}

	return nil, fmt.Errorf("key %s not found in node %s", key, n.NodeID)
}

// GetStalenessInfo returns staleness information for a key
func (n *BoundedStalenessNode) GetStalenessInfo(key string) map[string]interface{} {
	n.mutex.RLock()
	defer n.mutex.RUnlock()

	record, exists := n.Data[key]
	if !exists {
		return map[string]interface{}{"exists": false}
	}

	now := time.Now()
	age := record.GetAge(now)

	return map[string]interface{}{
		"exists":          true,
		"version":         record.Version,
		"age_seconds":     age.Seconds(),
		"bound_seconds":   record.StalenessBound.Seconds(),
		"within_bounds":   record.IsWithinBounds(now),
		"write_timestamp": record.WriteTimestamp,
		"staleness_ratio": age.Seconds() / record.StalenessBound.Seconds(),
	}
}

// SyncFrom synchronizes data from another node
func (n *BoundedStalenessNode) SyncFrom(source *BoundedStalenessNode, key string) error {
	sourceRecord, err := source.ReadAnyVersion(key)
	if err != nil {
		return err
	}

	n.mutex.Lock()
	defer n.mutex.Unlock()

	// Only sync if source has newer version
	currentRecord, exists := n.Data[key]
	if !exists || sourceRecord.Version > currentRecord.Version {
		// Create synced record
		syncedRecord := &StalenessRecord{
			Key:            sourceRecord.Key,
			Value:          sourceRecord.Value,
			Version:        sourceRecord.Version,
			WriteTimestamp: sourceRecord.WriteTimestamp,
			NodeID:         sourceRecord.NodeID, // Keep original node ID
			StalenessBound: sourceRecord.StalenessBound,
		}

		n.Data[key] = syncedRecord
		n.VersionCounters[key] = sourceRecord.Version

		log.Printf("[%s] Synced: %s = %v (v%d) from %s", 
			n.NodeID, key, syncedRecord.Value, syncedRecord.Version, source.NodeID)
	}

	return nil
}

// SetOnline sets the online status
func (n *BoundedStalenessNode) SetOnline(online bool) {
	n.mutex.Lock()
	defer n.mutex.Unlock()
	n.IsOnline = online

	status := "ONLINE"
	if !online {
		status = "OFFLINE"
	}
	log.Printf("[%s] Status changed to %s", n.NodeID, status)
}

// BoundedStalenessStore manages bounded staleness consistency
type BoundedStalenessStore struct {
	Nodes map[string]*BoundedStalenessNode
	mutex sync.RWMutex
}

// NewBoundedStalenessStore creates a new store
func NewBoundedStalenessStore() *BoundedStalenessStore {
	return &BoundedStalenessStore{
		Nodes: make(map[string]*BoundedStalenessNode),
	}
}

// AddNode adds a node to the store
func (store *BoundedStalenessStore) AddNode(node *BoundedStalenessNode) {
	store.mutex.Lock()
	defer store.mutex.Unlock()
	store.Nodes[node.NodeID] = node
	log.Printf("Added node: %s (%s)", node.NodeID, node.Location)
}

// Write writes data to a specific node
func (store *BoundedStalenessStore) Write(nodeID, key string, value interface{}, customBound *time.Duration) error {
	store.mutex.RLock()
	node, exists := store.Nodes[nodeID]
	store.mutex.RUnlock()

	if !exists {
		return fmt.Errorf("node %s not found", nodeID)
	}

	record, err := node.Write(key, value, customBound)
	if err != nil {
		return err
	}

	// Async sync to other nodes
	go store.asyncSync(nodeID, key, record)

	return nil
}

// ReadFresh reads fresh data (within staleness bounds) from any available node
func (store *BoundedStalenessStore) ReadFresh(key string) (interface{}, *StalenessRecord, error) {
	store.mutex.RLock()
	defer store.mutex.RUnlock()

	var bestRecord *StalenessRecord
	var bestAge time.Duration = time.Hour * 24 // Start with very old age

	// Find the freshest record within bounds
	for _, node := range store.Nodes {
		if !node.IsOnline {
			continue
		}

		record, err := node.ReadWithinBounds(key)
		if err != nil {
			continue // Try next node
		}

		age := record.GetAge(time.Now())
		if bestRecord == nil || age < bestAge {
			bestRecord = record
			bestAge = age
		}
	}

	if bestRecord == nil {
		return nil, nil, fmt.Errorf("no fresh data found for key %s", key)
	}

	return bestRecord.Value, bestRecord, nil
}

// ReadStale reads potentially stale data from fastest responding node
func (store *BoundedStalenessStore) ReadStale(key string) (interface{}, *StalenessRecord, error) {
	store.mutex.RLock()
	defer store.mutex.RUnlock()

	// Try to read from any node (fastest response)
	type nodeResult struct {
		record *StalenessRecord
		err    error
	}

	resultChan := make(chan nodeResult, len(store.Nodes))

	// Start concurrent reads
	for _, node := range store.Nodes {
		if node.IsOnline {
			go func(n *BoundedStalenessNode) {
				record, err := n.ReadAnyVersion(key)
				resultChan <- nodeResult{record, err}
			}(node)
		}
	}

	// Return first successful result
	for i := 0; i < len(store.Nodes); i++ {
		select {
		case result := <-resultChan:
			if result.err == nil {
				return result.record.Value, result.record, nil
			}
		case <-time.After(time.Second):
			return nil, nil, fmt.Errorf("timeout reading key %s", key)
		}
	}

	return nil, nil, fmt.Errorf("no data found for key %s", key)
}

// asyncSync asynchronously syncs data between nodes
func (store *BoundedStalenessStore) asyncSync(sourceNodeID, key string, record *StalenessRecord) {
	sourceNode := store.Nodes[sourceNodeID]
	if sourceNode == nil {
		return
	}

	// Random delay to simulate real-world async replication
	time.Sleep(time.Duration(100+rand.Intn(300)) * time.Millisecond)

	for _, targetNode := range store.Nodes {
		if targetNode.NodeID != sourceNodeID && targetNode.IsOnline {
			if err := targetNode.SyncFrom(sourceNode, key); err != nil {
				log.Printf("Sync failed from %s to %s for key %s: %v", 
					sourceNodeID, targetNode.NodeID, key, err)
			}
		}
	}
}

// GetStalenessReport generates a staleness report for all keys
func (store *BoundedStalenessStore) GetStalenessReport() map[string]interface{} {
	store.mutex.RLock()
	defer store.mutex.RUnlock()

	allKeys := make(map[string]bool)
	
	// Collect all keys
	for _, node := range store.Nodes {
		node.mutex.RLock()
		for key := range node.Data {
			allKeys[key] = true
		}
		node.mutex.RUnlock()
	}

	keyReports := make(map[string]map[string]interface{})
	
	for key := range allKeys {
		nodeInfo := make(map[string]interface{})
		
		for nodeID, node := range store.Nodes {
			info := node.GetStalenessInfo(key)
			nodeInfo[nodeID] = info
		}
		
		keyReports[key] = nodeInfo
	}

	return map[string]interface{}{
		"total_keys":   len(allKeys),
		"total_nodes":  len(store.Nodes),
		"key_reports":  keyReports,
		"report_time":  time.Now(),
	}
}

// stockPriceSimulation simulates stock price updates with different staleness bounds
func stockPriceSimulation(store *BoundedStalenessStore) {
	fmt.Println("\n=== Stock Price Simulation ===")

	// Stock symbols and their staleness requirements
	stocks := map[string]time.Duration{
		"INFY":   2 * time.Second,  // High frequency trading - very fresh
		"TCS":    5 * time.Second,  // Active trading - moderately fresh
		"RELIANCE": 10 * time.Second, // Regular trading - less strict
		"HDFC":   15 * time.Second, // Conservative - even less strict
	}

	// Simulate price updates
	fmt.Println("Starting stock price updates...")
	
	var wg sync.WaitGroup
	
	for symbol, stalenessBound := range stocks {
		wg.Add(1)
		go func(sym string, bound time.Duration) {
			defer wg.Done()
			
			basePrice := 1000.0 + rand.Float64()*500 // Random base price
			
			for i := 0; i < 10; i++ {
				// Simulate price movement
				change := (rand.Float64() - 0.5) * 20 // ±10 change
				price := basePrice + change
				
				// Write to random node
				nodes := []string{"mumbai", "delhi", "bangalore"}
				nodeID := nodes[rand.Intn(len(nodes))]
				
				key := fmt.Sprintf("stock:%s", sym)
				if err := store.Write(nodeID, key, price, &bound); err != nil {
					log.Printf("Failed to write stock price: %v", err)
				}
				
				basePrice = price // Update base price
				time.Sleep(time.Duration(rand.Intn(500)+200) * time.Millisecond)
			}
		}(symbol, stalenessBound)
	}
	
	wg.Wait()
	fmt.Println("Stock price updates completed")
}

// analyticsSimulation simulates analytics data with relaxed staleness bounds
func analyticsSimulation(store *BoundedStalenessStore) {
	fmt.Println("\n=== Analytics Dashboard Simulation ===")

	// Analytics metrics with different staleness requirements
	metrics := map[string]time.Duration{
		"analytics:page_views":     5 * time.Minute,  // Page views - can be 5 min old
		"analytics:user_signups":   2 * time.Minute,  // Signups - more important
		"analytics:revenue":        30 * time.Second, // Revenue - fairly important
		"analytics:error_rate":     10 * time.Second, // Errors - need quick detection
	}

	fmt.Println("Generating analytics data...")

	for metric, bound := range metrics {
		value := rand.Intn(10000) + 1000 // Random metric value
		
		// Write to primary analytics node
		if err := store.Write("bangalore", metric, value, &bound); err != nil {
			log.Printf("Failed to write analytics: %v", err)
		}
		
		time.Sleep(100 * time.Millisecond)
	}

	// Wait for some propagation
	time.Sleep(500 * time.Millisecond)

	fmt.Println("\nReading analytics data...")

	for metric := range metrics {
		// Try fresh read first
		if value, record, err := store.ReadFresh(metric); err == nil {
			age := record.GetAge(time.Now())
			fmt.Printf("  %s: %v (age: %v)\n", metric, value, age)
		} else {
			fmt.Printf("  %s: No fresh data available (%v)\n", metric, err)
			
			// Fallback to stale read
			if value, record, err := store.ReadStale(metric); err == nil {
				age := record.GetAge(time.Now())
				fmt.Printf("    Stale fallback: %v (age: %v)\n", value, age)
			}
		}
	}
}

// demonstrateBoundedStaleness demonstrates bounded staleness consistency
func demonstrateBoundedStaleness() {
	fmt.Println("=== Bounded Staleness Consistency Demo ===")
	fmt.Println("Stock prices/Analytics dashboard jaisa behavior")

	// Create store
	store := NewBoundedStalenessStore()

	// Add nodes with different characteristics
	mumbaiNode := NewBoundedStalenessNode("mumbai", "Mumbai", 20*time.Millisecond)
	delhiNode := NewBoundedStalenessNode("delhi", "Delhi", 40*time.Millisecond)
	bangaloreNode := NewBoundedStalenessNode("bangalore", "Bangalore", 30*time.Millisecond)
	singaporeNode := NewBoundedStalenessNode("singapore", "Singapore", 100*time.Millisecond)

	// Set default staleness bounds for different data types
	mumbaiNode.SetDefaultStaleness("stock:", 3*time.Second)
	mumbaiNode.SetDefaultStaleness("news:", 30*time.Second)
	mumbaiNode.SetDefaultStaleness("analytics:", 5*time.Minute)

	delhiNode.SetDefaultStaleness("stock:", 3*time.Second)
	delhiNode.SetDefaultStaleness("news:", 30*time.Second)
	delhiNode.SetDefaultStaleness("analytics:", 5*time.Minute)

	bangaloreNode.SetDefaultStaleness("stock:", 3*time.Second)
	bangaloreNode.SetDefaultStaleness("news:", 30*time.Second)
	bangaloreNode.SetDefaultStaleness("analytics:", 5*time.Minute)

	singaporeNode.SetDefaultStaleness("stock:", 5*time.Second)  // Slightly relaxed for international
	singaporeNode.SetDefaultStaleness("news:", 1*time.Minute)
	singaporeNode.SetDefaultStaleness("analytics:", 10*time.Minute)

	store.AddNode(mumbaiNode)
	store.AddNode(delhiNode)
	store.AddNode(bangaloreNode)
	store.AddNode(singaporeNode)

	fmt.Println("\n=== Basic Staleness Test ===")

	// Write some data
	customBound := 2 * time.Second
	store.Write("mumbai", "test:value", "Hello World", &customBound)

	// Immediate read - should work
	if value, record, err := store.ReadFresh("test:value"); err == nil {
		age := record.GetAge(time.Now())
		fmt.Printf("Immediate read: %v (age: %v)\n", value, age)
	} else {
		fmt.Printf("Immediate read failed: %v\n", err)
	}

	// Wait beyond staleness bound
	fmt.Println("Waiting for data to become stale...")
	time.Sleep(3 * time.Second)

	// Fresh read should fail
	if _, _, err := store.ReadFresh("test:value"); err != nil {
		fmt.Printf("Fresh read correctly failed: %v\n", err)
	} else {
		fmt.Printf("❌ Fresh read should have failed but didn't\n")
	}

	// Stale read should still work
	if value, record, err := store.ReadStale("test:value"); err == nil {
		age := record.GetAge(time.Now())
		fmt.Printf("Stale read succeeded: %v (age: %v)\n", value, age)
	} else {
		fmt.Printf("❌ Stale read failed: %v\n", err)
	}

	// Run simulations
	stockPriceSimulation(store)
	analyticsSimulation(store)

	fmt.Println("\n=== Network Partition Test ===")

	// Simulate network partition
	fmt.Println("Simulating network partition (Singapore node offline)...")
	singaporeNode.SetOnline(false)

	// Write fresh data
	store.Write("mumbai", "partition:test", "Fresh data during partition", nil)
	time.Sleep(100 * time.Millisecond)

	// Should still be able to read fresh data from other nodes
	if value, record, err := store.ReadFresh("partition:test"); err == nil {
		fmt.Printf("Read during partition: %v (age: %v)\n", value, record.GetAge(time.Now()))
	} else {
		fmt.Printf("Read failed during partition: %v\n", err)
	}

	// Bring Singapore back online
	singaporeNode.SetOnline(true)
	fmt.Println("Singapore node back online")

	// Wait for sync
	time.Sleep(200 * time.Millisecond)

	fmt.Println("\n=== Staleness Report ===")

	report := store.GetStalenessReport()
	if keyReports, ok := report["key_reports"].(map[string]map[string]interface{}); ok {
		fmt.Printf("Staleness report for %d keys:\n", report["total_keys"])
		
		// Sort keys for consistent output
		keys := make([]string, 0, len(keyReports))
		for key := range keyReports {
			keys = append(keys, key)
		}
		sort.Strings(keys)
		
		for _, key := range keys {
			nodeInfo := keyReports[key]
			fmt.Printf("\n%s:\n", key)
			
			for nodeID, info := range nodeInfo {
				if infoMap, ok := info.(map[string]interface{}); ok {
					if infoMap["exists"].(bool) {
						age := infoMap["age_seconds"].(float64)
						bound := infoMap["bound_seconds"].(float64)
						withinBounds := infoMap["within_bounds"].(bool)
						
						status := "✅ FRESH"
						if !withinBounds {
							status = "❌ STALE"
						}
						
						fmt.Printf("  %s: %s (age: %.1fs, bound: %.1fs)\n", 
							nodeID, status, age, bound)
					} else {
						fmt.Printf("  %s: Not present\n", nodeID)
					}
				}
			}
		}
	}

	fmt.Println("\n=== Performance Comparison ===")

	// Compare fresh vs stale read performance
	testKey := "perf:test"
	store.Write("mumbai", testKey, "Performance test data", nil)
	time.Sleep(100 * time.Millisecond)

	iterations := 10

	// Fresh reads
	start := time.Now()
	freshSuccesses := 0
	for i := 0; i < iterations; i++ {
		if _, _, err := store.ReadFresh(testKey); err == nil {
			freshSuccesses++
		}
	}
	freshDuration := time.Since(start)

	// Stale reads
	start = time.Now()
	staleSuccesses := 0
	for i := 0; i < iterations; i++ {
		if _, _, err := store.ReadStale(testKey); err == nil {
			staleSuccesses++
		}
	}
	staleDuration := time.Since(start)

	fmt.Printf("Fresh reads: %d/%d successful, %v total time\n", 
		freshSuccesses, iterations, freshDuration)
	fmt.Printf("Stale reads: %d/%d successful, %v total time\n", 
		staleSuccesses, iterations, staleDuration)
	
	if staleSuccesses > 0 && freshSuccesses > 0 {
		speedup := float64(freshDuration) / float64(staleDuration)
		fmt.Printf("Stale reads %.1fx faster than fresh reads\n", speedup)
	}

	fmt.Println("\n✅ Bounded Staleness Consistency demo completed!")
	fmt.Println("\nKey Benefits:")
	fmt.Println("- Predictable data freshness guarantees")
	fmt.Println("- Better performance than strong consistency")
	fmt.Println("- Flexible staleness bounds per data type")
	fmt.Println("- Graceful degradation during network issues")
	fmt.Println("- Suitable for analytics, monitoring, feeds")
}

func main() {
	// Set random seed
	rand.Seed(time.Now().UnixNano())
	
	// Configure logging
	log.SetFlags(log.Ltime | log.Lmicroseconds)
	
	// Run demonstration
	demonstrateBoundedStaleness()
}