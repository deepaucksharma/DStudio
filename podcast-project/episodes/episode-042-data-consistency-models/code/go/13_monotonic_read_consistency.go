/*
Monotonic Read Consistency Implementation
User kabhi bhi purane version read nahi karega
Example: News feed, Stock prices, Chat messages
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

// DataRecord represents a versioned data record
type DataRecord struct {
	Key       string
	Value     interface{}
	Version   int64
	Timestamp time.Time
	NodeID    string
}

// MonotonicSession tracks user's read progress
type MonotonicSession struct {
	SessionID     string
	UserID        string
	LastReadVersions map[string]int64 // Key -> highest version read
	ReadHistory   []*ReadOperation
	CreatedAt     time.Time
	mutex         sync.RWMutex
}

// ReadOperation represents a read operation
type ReadOperation struct {
	Key       string
	Version   int64
	Value     interface{}
	Timestamp time.Time
	ReplicaID string
}

// NewMonotonicSession creates a new session
func NewMonotonicSession(sessionID, userID string) *MonotonicSession {
	return &MonotonicSession{
		SessionID:        sessionID,
		UserID:           userID,
		LastReadVersions: make(map[string]int64),
		ReadHistory:      make([]*ReadOperation, 0),
		CreatedAt:        time.Now(),
	}
}

// UpdateReadVersion updates the highest read version for a key
func (s *MonotonicSession) UpdateReadVersion(key string, version int64, value interface{}, replicaID string) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// Only update if this version is higher
	if version > s.LastReadVersions[key] {
		s.LastReadVersions[key] = version
		
		// Add to read history
		s.ReadHistory = append(s.ReadHistory, &ReadOperation{
			Key:       key,
			Version:   version,
			Value:     value,
			Timestamp: time.Now(),
			ReplicaID: replicaID,
		})
	}
}

// GetMinVersionForRead returns minimum version required for monotonic read
func (s *MonotonicSession) GetMinVersionForRead(key string) int64 {
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	return s.LastReadVersions[key]
}

// GetReadHistory returns copy of read history
func (s *MonotonicSession) GetReadHistory() []*ReadOperation {
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	
	history := make([]*ReadOperation, len(s.ReadHistory))
	copy(history, s.ReadHistory)
	return history
}

// DataNode represents a distributed data node
type DataNode struct {
	NodeID      string
	Location    string
	Data        map[string]*DataRecord
	SyncDelay   time.Duration
	IsOnline    bool
	VersionCounters map[string]int64 // Key -> current version counter
	mutex       sync.RWMutex
}

// NewDataNode creates a new data node
func NewDataNode(nodeID, location string, syncDelay time.Duration) *DataNode {
	return &DataNode{
		NodeID:         nodeID,
		Location:       location,
		Data:           make(map[string]*DataRecord),
		SyncDelay:      syncDelay,
		IsOnline:       true,
		VersionCounters: make(map[string]int64),
	}
}

// Write updates data in the node
func (n *DataNode) Write(key string, value interface{}) (*DataRecord, error) {
	if !n.IsOnline {
		return nil, fmt.Errorf("node %s is offline", n.NodeID)
	}

	n.mutex.Lock()
	defer n.mutex.Unlock()

	// Increment version
	n.VersionCounters[key]++
	version := n.VersionCounters[key]

	record := &DataRecord{
		Key:       key,
		Value:     value,
		Version:   version,
		Timestamp: time.Now(),
		NodeID:    n.NodeID,
	}

	n.Data[key] = record
	log.Printf("[%s] Write: %s = %v (v%d)", n.NodeID, key, value, version)

	return record, nil
}

// Read retrieves data from the node
func (n *DataNode) Read(key string) (*DataRecord, error) {
	// Simulate network delay
	time.Sleep(n.SyncDelay)

	if !n.IsOnline {
		return nil, fmt.Errorf("node %s is offline", n.NodeID)
	}

	n.mutex.RLock()
	defer n.mutex.RUnlock()

	if record, exists := n.Data[key]; exists {
		log.Printf("[%s] Read: %s = %v (v%d)", n.NodeID, key, record.Value, record.Version)
		return record, nil
	}

	return nil, fmt.Errorf("key %s not found in node %s", key, n.NodeID)
}

// GetVersion returns current version for a key
func (n *DataNode) GetVersion(key string) int64 {
	n.mutex.RLock()
	defer n.mutex.RUnlock()

	if record, exists := n.Data[key]; exists {
		return record.Version
	}
	return 0
}

// SyncFrom synchronizes data from another node
func (n *DataNode) SyncFrom(source *DataNode, key string) error {
	sourceRecord, err := source.Read(key)
	if err != nil {
		return err
	}

	n.mutex.Lock()
	defer n.mutex.Unlock()

	// Only sync if source has newer version
	currentRecord, exists := n.Data[key]
	if !exists || sourceRecord.Version > currentRecord.Version {
		// Create synced record
		syncedRecord := &DataRecord{
			Key:       sourceRecord.Key,
			Value:     sourceRecord.Value,
			Version:   sourceRecord.Version,
			Timestamp: sourceRecord.Timestamp,
			NodeID:    sourceRecord.NodeID, // Keep original node ID
		}

		n.Data[key] = syncedRecord
		n.VersionCounters[key] = sourceRecord.Version
		
		log.Printf("[%s] Synced: %s = %v (v%d) from %s", 
			n.NodeID, key, syncedRecord.Value, syncedRecord.Version, source.NodeID)
	}

	return nil
}

// SetOnline sets the online status
func (n *DataNode) SetOnline(online bool) {
	n.mutex.Lock()
	defer n.mutex.Unlock()
	n.IsOnline = online
	
	status := "ONLINE"
	if !online {
		status = "OFFLINE"
	}
	log.Printf("[%s] Status changed to %s", n.NodeID, status)
}

// MonotonicReadStore manages monotonic read consistency
type MonotonicReadStore struct {
	Nodes    map[string]*DataNode
	Sessions map[string]*MonotonicSession
	mutex    sync.RWMutex
}

// NewMonotonicReadStore creates a new store
func NewMonotonicReadStore() *MonotonicReadStore {
	return &MonotonicReadStore{
		Nodes:    make(map[string]*DataNode),
		Sessions: make(map[string]*MonotonicSession),
	}
}

// AddNode adds a data node
func (store *MonotonicReadStore) AddNode(node *DataNode) {
	store.mutex.Lock()
	defer store.mutex.Unlock()
	store.Nodes[node.NodeID] = node
	log.Printf("Added node: %s (%s)", node.NodeID, node.Location)
}

// CreateSession creates a new user session
func (store *MonotonicReadStore) CreateSession(userID string) string {
	sessionID := fmt.Sprintf("mono_session_%d_%s", time.Now().UnixNano(), userID)
	session := NewMonotonicSession(sessionID, userID)

	store.mutex.Lock()
	defer store.mutex.Unlock()
	store.Sessions[sessionID] = session

	log.Printf("Created monotonic session: %s for user %s", sessionID, userID)
	return sessionID
}

// Write performs a write operation
func (store *MonotonicReadStore) Write(nodeID, key string, value interface{}) error {
	store.mutex.RLock()
	node, exists := store.Nodes[nodeID]
	store.mutex.RUnlock()

	if !exists {
		return fmt.Errorf("node %s not found", nodeID)
	}

	record, err := node.Write(key, value)
	if err != nil {
		return err
	}

	// Async sync to other nodes
	go store.asyncSync(nodeID, key, record)

	return nil
}

// MonotonicRead performs a read with monotonic consistency guarantee
func (store *MonotonicReadStore) MonotonicRead(sessionID, key string) (interface{}, error) {
	store.mutex.RLock()
	session, sessionExists := store.Sessions[sessionID]
	store.mutex.RUnlock()

	if !sessionExists {
		return nil, fmt.Errorf("session %s not found", sessionID)
	}

	// Get minimum version required for monotonic read
	minVersion := session.GetMinVersionForRead(key)

	// Find a node that has at least the minimum version
	suitableNode := store.findNodeWithMinVersion(key, minVersion)
	if suitableNode == nil {
		return nil, fmt.Errorf("no node has version >= %d for key %s", minVersion, key)
	}

	// Read from the suitable node
	record, err := suitableNode.Read(key)
	if err != nil {
		return nil, err
	}

	// Update session's read version
	session.UpdateReadVersion(key, record.Version, record.Value, suitableNode.NodeID)

	return record.Value, nil
}

// findNodeWithMinVersion finds a node that has at least the minimum version
func (store *MonotonicReadStore) findNodeWithMinVersion(key string, minVersion int64) *DataNode {
	var bestNode *DataNode
	var bestVersion int64 = -1

	for _, node := range store.Nodes {
		if !node.IsOnline {
			continue
		}

		version := node.GetVersion(key)
		if version >= minVersion && version > bestVersion {
			bestNode = node
			bestVersion = version
		}
	}

	return bestNode
}

// asyncSync asynchronously syncs data between nodes
func (store *MonotonicReadStore) asyncSync(sourceNodeID, key string, record *DataRecord) {
	sourceNode := store.Nodes[sourceNodeID]
	if sourceNode == nil {
		return
	}

	// Random delay to simulate real-world async replication
	time.Sleep(time.Duration(50+rand.Intn(150)) * time.Millisecond)

	for _, targetNode := range store.Nodes {
		if targetNode.NodeID != sourceNodeID && targetNode.IsOnline {
			if err := targetNode.SyncFrom(sourceNode, key); err != nil {
				log.Printf("Sync failed from %s to %s for key %s: %v", 
					sourceNodeID, targetNode.NodeID, key, err)
			}
		}
	}
}

// VerifyMonotonicConsistency checks if reads are monotonic for a session
func (store *MonotonicReadStore) VerifyMonotonicConsistency(sessionID string) map[string]interface{} {
	store.mutex.RLock()
	session, exists := store.Sessions[sessionID]
	store.mutex.RUnlock()

	if !exists {
		return map[string]interface{}{"error": "session not found"}
	}

	readHistory := session.GetReadHistory()
	violations := make([]map[string]interface{}, 0)

	// Group reads by key
	keyReads := make(map[string][]*ReadOperation)
	for _, read := range readHistory {
		keyReads[read.Key] = append(keyReads[read.Key], read)
	}

	// Check monotonicity for each key
	for key, reads := range keyReads {
		// Sort by timestamp
		sort.Slice(reads, func(i, j int) bool {
			return reads[i].Timestamp.Before(reads[j].Timestamp)
		})

		// Check if versions are monotonic
		for i := 1; i < len(reads); i++ {
			if reads[i].Version < reads[i-1].Version {
				violations = append(violations, map[string]interface{}{
					"key":           key,
					"violation":     "version_regression",
					"current_read":  reads[i].Version,
					"previous_read": reads[i-1].Version,
					"timestamp":     reads[i].Timestamp,
				})
			}
		}
	}

	return map[string]interface{}{
		"session_id":    sessionID,
		"user_id":       session.UserID,
		"total_reads":   len(readHistory),
		"violations":    violations,
		"is_monotonic":  len(violations) == 0,
		"keys_read":     len(keyReads),
	}
}

// GetSystemStatus returns overall system status
func (store *MonotonicReadStore) GetSystemStatus() map[string]interface{} {
	store.mutex.RLock()
	defer store.mutex.RUnlock()

	nodeStatus := make(map[string]interface{})
	for nodeID, node := range store.Nodes {
		node.mutex.RLock()
		status := map[string]interface{}{
			"location":   node.Location,
			"online":     node.IsOnline,
			"data_count": len(node.Data),
		}
		node.mutex.RUnlock()
		nodeStatus[nodeID] = status
	}

	return map[string]interface{}{
		"total_nodes":    len(store.Nodes),
		"total_sessions": len(store.Sessions),
		"nodes":          nodeStatus,
	}
}

// simulateNewsFeed simulates a news feed with monotonic reads
func simulateNewsFeed(store *MonotonicReadStore) {
	fmt.Println("\n=== News Feed Simulation ===")

	// Create user sessions
	rahulSession := store.CreateSession("rahul")
	priyaSession := store.CreateSession("priya")
	
	newsItems := []string{
		"Breaking: Mumbai gets heavy rainfall",
		"Cricket: India wins by 50 runs",
		"Tech: New iPhone launched",
		"Politics: Election results announced",
		"Weather: Cyclone approaching coast",
		"Sports: Olympics preparation starts",
		"Business: Stock market hits record high",
		"Entertainment: New Bollywood movie released",
	}

	fmt.Println("Publishing news items...")

	// Publish news items on different nodes
	nodes := []string{"mumbai", "delhi", "bangalore"}
	for i, news := range newsItems {
		nodeID := nodes[i%len(nodes)]
		key := fmt.Sprintf("news:%d", i+1)
		
		if err := store.Write(nodeID, key, news); err != nil {
			log.Printf("Failed to publish news: %v", err)
		}
		
		// Small delay between publications
		time.Sleep(50 * time.Millisecond)
	}

	// Let replication catch up
	time.Sleep(500 * time.Millisecond)

	fmt.Println("\nUsers reading news feed...")

	// Rahul reads news sequentially
	fmt.Println("\nRahul's reading session:")
	for i := 1; i <= len(newsItems); i++ {
		key := fmt.Sprintf("news:%d", i)
		if value, err := store.MonotonicRead(rahulSession, key); err == nil {
			fmt.Printf("  Rahul read: %s\n", value)
		} else {
			fmt.Printf("  Rahul failed to read %s: %v\n", key, err)
		}
		time.Sleep(20 * time.Millisecond)
	}

	// Priya reads news in random order
	fmt.Println("\nPriya's reading session (random order):")
	indices := rand.Perm(len(newsItems))
	for _, i := range indices[:5] { // Read only 5 items
		key := fmt.Sprintf("news:%d", i+1)
		if value, err := store.MonotonicRead(priyaSession, key); err == nil {
			fmt.Printf("  Priya read: %s\n", value)
		} else {
			fmt.Printf("  Priya failed to read %s: %v\n", key, err)
		}
		time.Sleep(30 * time.Millisecond)
	}
}

// demonstrateMonotonicReads demonstrates monotonic read consistency
func demonstrateMonotonicReads() {
	fmt.Println("=== Monotonic Read Consistency Demo ===")
	fmt.Println("News feed/Chat messages jaisa behavior")

	// Create store
	store := NewMonotonicReadStore()

	// Add nodes - Indian cities
	mumbaiNode := NewDataNode("mumbai", "Mumbai", 30*time.Millisecond)
	delhiNode := NewDataNode("delhi", "Delhi", 40*time.Millisecond)
	bangaloreNode := NewDataNode("bangalore", "Bangalore", 35*time.Millisecond)
	chennaiNode := NewDataNode("chennai", "Chennai", 45*time.Millisecond)

	store.AddNode(mumbaiNode)
	store.AddNode(delhiNode)
	store.AddNode(bangaloreNode)
	store.AddNode(chennaiNode)

	fmt.Println("\n=== Basic Monotonic Read Test ===")

	// Create user session
	userSession := store.CreateSession("test_user")

	// Write data updates on different nodes
	fmt.Println("Writing data updates...")
	store.Write("mumbai", "stock:INFY", 1500.0)
	time.Sleep(100 * time.Millisecond)
	
	store.Write("delhi", "stock:INFY", 1520.0)
	time.Sleep(100 * time.Millisecond)
	
	store.Write("bangalore", "stock:INFY", 1535.0)
	
	// Wait for some sync
	time.Sleep(200 * time.Millisecond)

	fmt.Println("\nReading stock price (should be monotonic)...")
	
	// Read multiple times - should never see older versions
	for i := 0; i < 5; i++ {
		if value, err := store.MonotonicRead(userSession, "stock:INFY"); err == nil {
			fmt.Printf("  Read %d: ₹%.2f\n", i+1, value)
		} else {
			fmt.Printf("  Read %d failed: %v\n", i+1, err)
		}
		time.Sleep(50 * time.Millisecond)
	}

	// Simulate news feed
	simulateNewsFeed(store)

	fmt.Println("\n=== Network Partition Test ===")

	// Simulate network partition
	fmt.Println("Simulating network partition (Delhi node offline)...")
	delhiNode.SetOnline(false)

	// Continue writing and reading
	store.Write("mumbai", "alert:weather", "Heavy rain expected")
	time.Sleep(100 * time.Millisecond)

	// User should still get monotonic reads
	testSession := store.CreateSession("partition_test")
	if value, err := store.MonotonicRead(testSession, "alert:weather"); err == nil {
		fmt.Printf("Read during partition: %s\n", value)
	} else {
		fmt.Printf("Read failed during partition: %v\n", err)
	}

	// Bring Delhi back online
	delhiNode.SetOnline(true)
	fmt.Println("Delhi node back online")

	fmt.Println("\n=== Consistency Verification ===")

	// Verify monotonic consistency for all sessions
	sessions := []string{userSession, testSession}
	for _, sessionID := range sessions {
		verification := store.VerifyMonotonicConsistency(sessionID)
		
		fmt.Printf("Session %s:\n", verification["user_id"])
		fmt.Printf("  Total reads: %d\n", verification["total_reads"])
		fmt.Printf("  Keys read: %d\n", verification["keys_read"])
		fmt.Printf("  Monotonic: %t\n", verification["is_monotonic"])
		
		if violations, ok := verification["violations"].([]map[string]interface{}); ok && len(violations) > 0 {
			fmt.Printf("  Violations:\n")
			for _, violation := range violations {
				fmt.Printf("    %s: %v\n", violation["violation"], violation)
			}
		}
	}

	fmt.Println("\n=== Concurrent Users Test ===")

	// Multiple users reading concurrently
	var wg sync.WaitGroup
	userCount := 5

	for i := 0; i < userCount; i++ {
		wg.Add(1)
		go func(userID int) {
			defer wg.Done()
			
			sessionID := store.CreateSession(fmt.Sprintf("concurrent_user_%d", userID))
			
			// Each user reads multiple times
			for j := 0; j < 10; j++ {
				key := fmt.Sprintf("news:%d", (j%3)+1) // Read from first 3 news items
				
				if _, err := store.MonotonicRead(sessionID, key); err != nil {
					log.Printf("Concurrent read failed for user %d: %v", userID, err)
				}
				
				time.Sleep(time.Duration(rand.Intn(50)) * time.Millisecond)
			}
		}(i)
	}

	wg.Wait()
	fmt.Printf("Completed concurrent reads for %d users\n", userCount)

	fmt.Println("\n=== System Status ===")

	status := store.GetSystemStatus()
	fmt.Printf("Total nodes: %d\n", status["total_nodes"])
	fmt.Printf("Total sessions: %d\n", status["total_sessions"])

	if nodes, ok := status["nodes"].(map[string]interface{}); ok {
		fmt.Println("Node status:")
		for nodeID, nodeInfo := range nodes {
			if info, ok := nodeInfo.(map[string]interface{}); ok {
				fmt.Printf("  %s (%s): %d items, online: %t\n", 
					nodeID, info["location"], info["data_count"], info["online"])
			}
		}
	}

	fmt.Println("\n✅ Monotonic Read Consistency demo completed!")
	fmt.Println("\nKey Benefits:")
	fmt.Println("- Users never see data going backwards in time")
	fmt.Println("- Essential for feeds, timelines, chat messages")
	fmt.Println("- Prevents confusing user experiences")
	fmt.Println("- Works even with partial network failures")
	fmt.Println("- Maintains progress guarantee per user session")
}

func main() {
	// Set random seed
	rand.Seed(time.Now().UnixNano())
	
	// Configure logging
	log.SetFlags(log.Ltime | log.Lmicroseconds)
	
	// Run demonstration
	demonstrateMonotonicReads()
}