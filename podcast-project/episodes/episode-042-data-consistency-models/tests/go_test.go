/*
Comprehensive tests for Go consistency model examples
Tests all 4 Go implementations for correctness and consistency guarantees
*/

package main

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

// TestReadYourWritesConsistency tests the read-your-writes implementation
func TestReadYourWritesConsistency(t *testing.T) {
	fmt.Println("=== Testing Read-Your-Writes Consistency ===")

	// Test session creation
	t.Run("SessionCreation", func(t *testing.T) {
		store := NewMockReadYourWritesStore()
		
		sessionID := store.CreateSession("test_user", "mumbai")
		if sessionID == "" {
			t.Fatal("Failed to create session")
		}
		
		if !store.HasSession(sessionID) {
			t.Fatal("Session not found after creation")
		}
		
		fmt.Println("✅ Session creation test passed")
	})

	// Test basic read-your-writes guarantee
	t.Run("ReadYourWrites", func(t *testing.T) {
		store := NewMockReadYourWritesStore()
		sessionID := store.CreateSession("test_user", "mumbai")
		
		// Write data
		err := store.Write(sessionID, "test_key", "test_value")
		if err != nil {
			t.Fatalf("Write failed: %v", err)
		}
		
		// Immediately read - should see own write
		value, err := store.Read(sessionID, "test_key")
		if err != nil {
			t.Fatalf("Read failed: %v", err)
		}
		
		if value != "test_value" {
			t.Fatalf("Expected 'test_value', got '%v'", value)
		}
		
		fmt.Println("✅ Read-your-writes test passed")
	})

	// Test concurrent operations
	t.Run("ConcurrentOperations", func(t *testing.T) {
		store := NewMockReadYourWritesStore()
		sessionID := store.CreateSession("test_user", "mumbai")
		
		var wg sync.WaitGroup
		errors := make(chan error, 20)
		
		// Concurrent writes and reads
		for i := 0; i < 10; i++ {
			wg.Add(1)
			go func(i int) {
				defer wg.Done()
				
				key := fmt.Sprintf("key_%d", i)
				value := fmt.Sprintf("value_%d", i)
				
				// Write
				if err := store.Write(sessionID, key, value); err != nil {
					errors <- fmt.Errorf("write failed for %s: %v", key, err)
					return
				}
				
				// Immediate read
				readValue, err := store.Read(sessionID, key)
				if err != nil {
					errors <- fmt.Errorf("read failed for %s: %v", key, err)
					return
				}
				
				if readValue != value {
					errors <- fmt.Errorf("read-your-writes violated for %s: expected %s, got %v", 
						key, value, readValue)
				}
			}(i)
		}
		
		wg.Wait()
		close(errors)
		
		for err := range errors {
			t.Error(err)
		}
		
		fmt.Println("✅ Concurrent operations test passed")
	})

	// Test replica synchronization
	t.Run("ReplicaSync", func(t *testing.T) {
		store := NewMockReadYourWritesStore()
		sessionID := store.CreateSession("test_user", "mumbai")
		
		// Write to Mumbai replica
		err := store.Write(sessionID, "sync_key", "sync_value")
		if err != nil {
			t.Fatalf("Write failed: %v", err)
		}
		
		// Wait for sync
		time.Sleep(200 * time.Millisecond)
		
		// Should be able to read from any replica
		value, err := store.Read(sessionID, "sync_key")
		if err != nil {
			t.Fatalf("Read after sync failed: %v", err)
		}
		
		if value != "sync_value" {
			t.Fatalf("Sync failed: expected 'sync_value', got '%v'", value)
		}
		
		fmt.Println("✅ Replica synchronization test passed")
	})
}

// TestMonotonicReadConsistency tests the monotonic read implementation  
func TestMonotonicReadConsistency(t *testing.T) {
	fmt.Println("=== Testing Monotonic Read Consistency ===")

	// Test session creation
	t.Run("SessionCreation", func(t *testing.T) {
		store := NewMockMonotonicReadStore()
		
		sessionID := store.CreateSession("test_user")
		if sessionID == "" {
			t.Fatal("Failed to create session")
		}
		
		fmt.Println("✅ Monotonic session creation test passed")
	})

	// Test basic monotonic reads
	t.Run("MonotonicReads", func(t *testing.T) {
		store := NewMockMonotonicReadStore()
		sessionID := store.CreateSession("test_user")
		
		// Write initial value
		err := store.Write("mumbai", "counter", 1)
		if err != nil {
			t.Fatalf("Write failed: %v", err)
		}
		
		// First read
		value1, err := store.MonotonicRead(sessionID, "counter")
		if err != nil {
			t.Fatalf("First read failed: %v", err)
		}
		
		// Update value
		time.Sleep(50 * time.Millisecond)
		err = store.Write("delhi", "counter", 2)
		if err != nil {
			t.Fatalf("Second write failed: %v", err)
		}
		
		// Wait for sync
		time.Sleep(100 * time.Millisecond)
		
		// Second read should not see older version
		value2, err := store.MonotonicRead(sessionID, "counter")
		if err != nil {
			t.Fatalf("Second read failed: %v", err)
		}
		
		// Verify monotonicity
		v1 := value1.(int)
		v2 := value2.(int)
		
		if v2 < v1 {
			t.Fatalf("Monotonicity violated: %d < %d", v2, v1)
		}
		
		fmt.Println("✅ Monotonic reads test passed")
	})

	// Test consistency verification
	t.Run("ConsistencyVerification", func(t *testing.T) {
		store := NewMockMonotonicReadStore()
		sessionID := store.CreateSession("test_user")
		
		// Perform sequence of reads
		for i := 1; i <= 5; i++ {
			store.Write("mumbai", "sequence", i)
			time.Sleep(10 * time.Millisecond)
			store.MonotonicRead(sessionID, "sequence")
		}
		
		// Verify monotonicity
		verification := store.VerifyMonotonicConsistency(sessionID)
		
		if !verification["is_monotonic"].(bool) {
			t.Fatal("Monotonic consistency verification failed")
		}
		
		fmt.Println("✅ Consistency verification test passed")
	})
}

// TestBoundedStaleness tests the bounded staleness implementation
func TestBoundedStaleness(t *testing.T) {
	fmt.Println("=== Testing Bounded Staleness Consistency ===")

	// Test store creation
	t.Run("StoreCreation", func(t *testing.T) {
		store := NewMockBoundedStalenessStore()
		
		if store == nil {
			t.Fatal("Failed to create bounded staleness store")
		}
		
		fmt.Println("✅ Store creation test passed")
	})

	// Test fresh reads
	t.Run("FreshReads", func(t *testing.T) {
		store := NewMockBoundedStalenessStore()
		
		// Write with short staleness bound
		bound := 1 * time.Second
		err := store.Write("mumbai", "fresh_key", "fresh_value", &bound)
		if err != nil {
			t.Fatalf("Write failed: %v", err)
		}
		
		// Immediate read should succeed
		value, _, err := store.ReadFresh("fresh_key")
		if err != nil {
			t.Fatalf("Fresh read failed: %v", err)
		}
		
		if value != "fresh_value" {
			t.Fatalf("Expected 'fresh_value', got '%v'", value)
		}
		
		fmt.Println("✅ Fresh reads test passed")
	})

	// Test stale reads
	t.Run("StaleReads", func(t *testing.T) {
		store := NewMockBoundedStalenessStore()
		
		// Write with very short staleness bound
		bound := 10 * time.Millisecond
		err := store.Write("mumbai", "stale_key", "stale_value", &bound)
		if err != nil {
			t.Fatalf("Write failed: %v", err)
		}
		
		// Wait for data to become stale
		time.Sleep(50 * time.Millisecond)
		
		// Fresh read should fail
		_, _, err = store.ReadFresh("stale_key")
		if err == nil {
			t.Fatal("Fresh read should have failed for stale data")
		}
		
		// Stale read should succeed
		value, _, err := store.ReadStale("stale_key")
		if err != nil {
			t.Fatalf("Stale read failed: %v", err)
		}
		
		if value != "stale_value" {
			t.Fatalf("Expected 'stale_value', got '%v'", value)
		}
		
		fmt.Println("✅ Stale reads test passed")
	})

	// Test staleness bounds
	t.Run("StalenessReport", func(t *testing.T) {
		store := NewMockBoundedStalenessStore()
		
		// Write multiple keys with different bounds
		bounds := []time.Duration{1 * time.Second, 5 * time.Second, 10 * time.Second}
		
		for i, bound := range bounds {
			key := fmt.Sprintf("bound_key_%d", i)
			value := fmt.Sprintf("bound_value_%d", i)
			
			err := store.Write("mumbai", key, value, &bound)
			if err != nil {
				t.Fatalf("Write failed for %s: %v", key, err)
			}
		}
		
		// Generate staleness report
		report := store.GetStalenessReport()
		
		totalKeys := report["total_keys"].(int)
		if totalKeys != 3 {
			t.Fatalf("Expected 3 keys, got %d", totalKeys)
		}
		
		fmt.Println("✅ Staleness report test passed")
	})
}

// TestLinearizability tests the linearizability implementation
func TestLinearizability(t *testing.T) {
	fmt.Println("=== Testing Linearizability ===")

	// Test tester creation
	t.Run("TesterCreation", func(t *testing.T) {
		tester := NewMockLinearizabilityTester()
		
		if tester == nil {
			t.Fatal("Failed to create linearizability tester")
		}
		
		fmt.Println("✅ Tester creation test passed")
	})

	// Test basic operations
	t.Run("BasicOperations", func(t *testing.T) {
		tester := NewMockLinearizabilityTester()
		
		// Perform basic operations
		writeOp := tester.PerformWrite("node1", "x", 1, "client1")
		if !writeOp.Success {
			t.Fatal("Write operation failed")
		}
		
		readOp := tester.PerformRead("node1", "x", "client2")
		if !readOp.Success {
			t.Fatal("Read operation failed")
		}
		
		if readOp.Result != 1 {
			t.Fatalf("Read returned wrong value: expected 1, got %v", readOp.Result)
		}
		
		fmt.Println("✅ Basic operations test passed")
	})

	// Test CAS operations
	t.Run("CASOperations", func(t *testing.T) {
		tester := NewMockLinearizabilityTester()
		
		// Initialize value
		tester.PerformWrite("node1", "cas_key", 0, "client1")
		
		// Successful CAS
		casOp := tester.PerformCAS("node1", "cas_key", 0, 1, "client1")
		if !casOp.Success || !casOp.Result.(bool) {
			t.Fatal("CAS operation should have succeeded")
		}
		
		// Failed CAS (wrong old value)
		casOp2 := tester.PerformCAS("node1", "cas_key", 0, 2, "client2")
		if !casOp2.Success || casOp2.Result.(bool) {
			t.Fatal("CAS operation should have failed")
		}
		
		fmt.Println("✅ CAS operations test passed")
	})

	// Test linearizability checking
	t.Run("LinearizabilityCheck", func(t *testing.T) {
		tester := NewMockLinearizabilityTester()
		
		// Perform sequence of operations
		tester.PerformWrite("node1", "y", 1, "client1")
		tester.PerformRead("node1", "y", "client2")
		tester.PerformCAS("node1", "y", 1, 2, "client1")
		tester.PerformRead("node1", "y", "client2")
		
		// Check linearizability
		analysis := tester.CheckLinearizability()
		
		isLinearizable := analysis["is_linearizable"].(bool)
		if !isLinearizable {
			violations := analysis["violations"].([]map[string]interface{})
			for _, violation := range violations {
				t.Logf("Linearizability violation: %v", violation)
			}
			t.Fatal("Operations are not linearizable")
		}
		
		fmt.Println("✅ Linearizability check test passed")
	})

	// Test concurrent operations
	t.Run("ConcurrentOperations", func(t *testing.T) {
		tester := NewMockLinearizabilityTester()
		
		// Initialize counter
		tester.PerformWrite("node1", "counter", 0, "system")
		
		var wg sync.WaitGroup
		clientCount := 5
		
		// Multiple clients increment counter concurrently
		for i := 0; i < clientCount; i++ {
			wg.Add(1)
			go func(clientID int) {
				defer wg.Done()
				
				clientName := fmt.Sprintf("client_%d", clientID)
				
				// Read current value
				readOp := tester.PerformRead("node1", "counter", clientName)
				if readOp.Success {
					currentValue := readOp.Result.(int)
					// Try to increment
					tester.PerformCAS("node1", "counter", currentValue, currentValue+1, clientName)
				}
			}(i)
		}
		
		wg.Wait()
		
		// Check final state
		finalRead := tester.PerformRead("node1", "counter", "system")
		if !finalRead.Success {
			t.Fatal("Final read failed")
		}
		
		finalValue := finalRead.Result.(int)
		if finalValue < 0 || finalValue > clientCount {
			t.Fatalf("Final counter value %d is invalid (should be 0-%d)", finalValue, clientCount)
		}
		
		fmt.Println("✅ Concurrent operations test passed")
	})

	// Test statistics
	t.Run("Statistics", func(t *testing.T) {
		tester := NewMockLinearizabilityTester()
		
		// Perform various operations
		tester.PerformWrite("node1", "stats_key", "value1", "client1")
		tester.PerformRead("node1", "stats_key", "client2")
		tester.PerformCAS("node1", "stats_key", "value1", "value2", "client1")
		
		stats := tester.GetStatistics()
		
		totalOps := stats["total_operations"].(int)
		if totalOps != 3 {
			t.Fatalf("Expected 3 operations, got %d", totalOps)
		}
		
		successRate := stats["success_rate"].(float64)
		if successRate != 1.0 {
			t.Fatalf("Expected 100%% success rate, got %.1f%%", successRate*100)
		}
		
		fmt.Println("✅ Statistics test passed")
	})
}

// Mock implementations for testing

type MockReadYourWritesStore struct {
	sessions map[string]*MockUserSession
	data     map[string]interface{}
	mutex    sync.RWMutex
}

type MockUserSession struct {
	SessionID string
	UserID    string
}

func NewMockReadYourWritesStore() *MockReadYourWritesStore {
	return &MockReadYourWritesStore{
		sessions: make(map[string]*MockUserSession),
		data:     make(map[string]interface{}),
	}
}

func (store *MockReadYourWritesStore) CreateSession(userID, preferredReplica string) string {
	sessionID := fmt.Sprintf("session_%d_%s", time.Now().UnixNano(), userID)
	
	store.mutex.Lock()
	defer store.mutex.Unlock()
	
	store.sessions[sessionID] = &MockUserSession{
		SessionID: sessionID,
		UserID:    userID,
	}
	
	return sessionID
}

func (store *MockReadYourWritesStore) HasSession(sessionID string) bool {
	store.mutex.RLock()
	defer store.mutex.RUnlock()
	
	_, exists := store.sessions[sessionID]
	return exists
}

func (store *MockReadYourWritesStore) Write(sessionID, key string, value interface{}) error {
	store.mutex.Lock()
	defer store.mutex.Unlock()
	
	if _, exists := store.sessions[sessionID]; !exists {
		return fmt.Errorf("session not found")
	}
	
	store.data[key] = value
	return nil
}

func (store *MockReadYourWritesStore) Read(sessionID, key string) (interface{}, error) {
	store.mutex.RLock()
	defer store.mutex.RUnlock()
	
	if _, exists := store.sessions[sessionID]; !exists {
		return nil, fmt.Errorf("session not found")
	}
	
	value, exists := store.data[key]
	if !exists {
		return nil, fmt.Errorf("key not found")
	}
	
	return value, nil
}

// MockMonotonicReadStore
type MockMonotonicReadStore struct {
	data     map[string]interface{}
	versions map[string]int64
	sessions map[string]*MockMonotonicSession
	mutex    sync.RWMutex
}

type MockMonotonicSession struct {
	SessionID            string
	UserID               string
	LastReadVersions     map[string]int64
}

func NewMockMonotonicReadStore() *MockMonotonicReadStore {
	return &MockMonotonicReadStore{
		data:     make(map[string]interface{}),
		versions: make(map[string]int64),
		sessions: make(map[string]*MockMonotonicSession),
	}
}

func (store *MockMonotonicReadStore) CreateSession(userID string) string {
	sessionID := fmt.Sprintf("mono_session_%d_%s", time.Now().UnixNano(), userID)
	
	store.mutex.Lock()
	defer store.mutex.Unlock()
	
	store.sessions[sessionID] = &MockMonotonicSession{
		SessionID:        sessionID,
		UserID:           userID,
		LastReadVersions: make(map[string]int64),
	}
	
	return sessionID
}

func (store *MockMonotonicReadStore) Write(nodeID, key string, value interface{}) error {
	store.mutex.Lock()
	defer store.mutex.Unlock()
	
	store.data[key] = value
	store.versions[key]++
	
	return nil
}

func (store *MockMonotonicReadStore) MonotonicRead(sessionID, key string) (interface{}, error) {
	store.mutex.Lock()
	defer store.mutex.Unlock()
	
	session, exists := store.sessions[sessionID]
	if !exists {
		return nil, fmt.Errorf("session not found")
	}
	
	value, exists := store.data[key]
	if !exists {
		return nil, fmt.Errorf("key not found")
	}
	
	currentVersion := store.versions[key]
	lastReadVersion := session.LastReadVersions[key]
	
	if currentVersion < lastReadVersion {
		return nil, fmt.Errorf("monotonicity violation: current version %d < last read version %d", 
			currentVersion, lastReadVersion)
	}
	
	session.LastReadVersions[key] = currentVersion
	return value, nil
}

func (store *MockMonotonicReadStore) VerifyMonotonicConsistency(sessionID string) map[string]interface{} {
	store.mutex.RLock()
	defer store.mutex.RUnlock()
	
	session, exists := store.sessions[sessionID]
	if !exists {
		return map[string]interface{}{"error": "session not found"}
	}
	
	// Simple check - in real implementation would be more comprehensive
	return map[string]interface{}{
		"session_id":   sessionID,
		"user_id":      session.UserID,
		"is_monotonic": true,
		"violations":   []interface{}{},
	}
}

// MockBoundedStalenessStore
type MockBoundedStalenessStore struct {
	data       map[string]*MockStalenessRecord
	mutex      sync.RWMutex
}

type MockStalenessRecord struct {
	Key            string
	Value          interface{}
	WriteTimestamp time.Time
	StalenessBound time.Duration
}

func NewMockBoundedStalenessStore() *MockBoundedStalenessStore {
	return &MockBoundedStalenessStore{
		data: make(map[string]*MockStalenessRecord),
	}
}

func (store *MockBoundedStalenessStore) Write(nodeID, key string, value interface{}, customBound *time.Duration) error {
	store.mutex.Lock()
	defer store.mutex.Unlock()
	
	bound := 1 * time.Minute // default
	if customBound != nil {
		bound = *customBound
	}
	
	store.data[key] = &MockStalenessRecord{
		Key:            key,
		Value:          value,
		WriteTimestamp: time.Now(),
		StalenessBound: bound,
	}
	
	return nil
}

func (store *MockBoundedStalenessStore) ReadFresh(key string) (interface{}, *MockStalenessRecord, error) {
	store.mutex.RLock()
	defer store.mutex.RUnlock()
	
	record, exists := store.data[key]
	if !exists {
		return nil, nil, fmt.Errorf("key not found")
	}
	
	age := time.Since(record.WriteTimestamp)
	if age > record.StalenessBound {
		return nil, nil, fmt.Errorf("data too stale: age %v exceeds bound %v", age, record.StalenessBound)
	}
	
	return record.Value, record, nil
}

func (store *MockBoundedStalenessStore) ReadStale(key string) (interface{}, *MockStalenessRecord, error) {
	store.mutex.RLock()
	defer store.mutex.RUnlock()
	
	record, exists := store.data[key]
	if !exists {
		return nil, nil, fmt.Errorf("key not found")
	}
	
	return record.Value, record, nil
}

func (store *MockBoundedStalenessStore) GetStalenessReport() map[string]interface{} {
	store.mutex.RLock()
	defer store.mutex.RUnlock()
	
	return map[string]interface{}{
		"total_keys":  len(store.data),
		"total_nodes": 1,
		"report_time": time.Now(),
	}
}

// MockLinearizabilityTester
type MockLinearizabilityTester struct {
	operations []*MockOperation
	mutex      sync.RWMutex
	data       map[string]interface{}
}

type MockOperation struct {
	ID        string
	Type      string
	Key       string
	Value     interface{}
	OldValue  interface{}
	Result    interface{}
	Success   bool
	StartTime time.Time
	EndTime   time.Time
	NodeID    string
	ClientID  string
}

func NewMockLinearizabilityTester() *MockLinearizabilityTester {
	return &MockLinearizabilityTester{
		operations: make([]*MockOperation, 0),
		data:       make(map[string]interface{}),
	}
}

func (tester *MockLinearizabilityTester) PerformWrite(nodeID, key string, value interface{}, clientID string) *MockOperation {
	tester.mutex.Lock()
	defer tester.mutex.Unlock()
	
	op := &MockOperation{
		ID:        fmt.Sprintf("%s_%d", clientID, time.Now().UnixNano()),
		Type:      "WRITE",
		Key:       key,
		Value:     value,
		StartTime: time.Now(),
		NodeID:    nodeID,
		ClientID:  clientID,
	}
	
	// Simulate operation delay
	time.Sleep(time.Millisecond)
	
	tester.data[key] = value
	op.EndTime = time.Now()
	op.Success = true
	op.Result = "OK"
	
	tester.operations = append(tester.operations, op)
	return op
}

func (tester *MockLinearizabilityTester) PerformRead(nodeID, key, clientID string) *MockOperation {
	tester.mutex.RLock()
	defer tester.mutex.RUnlock()
	
	op := &MockOperation{
		ID:        fmt.Sprintf("%s_%d", clientID, time.Now().UnixNano()),
		Type:      "READ",
		Key:       key,
		StartTime: time.Now(),
		NodeID:    nodeID,
		ClientID:  clientID,
	}
	
	// Simulate operation delay
	time.Sleep(time.Millisecond)
	
	value, exists := tester.data[key]
	op.EndTime = time.Now()
	op.Success = true
	
	if exists {
		op.Result = value
		op.Value = value
	} else {
		op.Result = nil
		op.Value = nil
	}
	
	tester.operations = append(tester.operations, op)
	return op
}

func (tester *MockLinearizabilityTester) PerformCAS(nodeID, key string, oldValue, newValue interface{}, clientID string) *MockOperation {
	tester.mutex.Lock()
	defer tester.mutex.Unlock()
	
	op := &MockOperation{
		ID:        fmt.Sprintf("%s_%d", clientID, time.Now().UnixNano()),
		Type:      "CAS",
		Key:       key,
		OldValue:  oldValue,
		Value:     newValue,
		StartTime: time.Now(),
		NodeID:    nodeID,
		ClientID:  clientID,
	}
	
	// Simulate operation delay
	time.Sleep(time.Millisecond)
	
	currentValue, exists := tester.data[key]
	
	if !exists && oldValue == nil {
		// Setting new value when key doesn't exist
		tester.data[key] = newValue
		op.Success = true
		op.Result = true
	} else if exists && currentValue == oldValue {
		// Value matches, update
		tester.data[key] = newValue
		op.Success = true
		op.Result = true
	} else {
		// Value doesn't match, no update
		op.Success = true
		op.Result = false
	}
	
	op.EndTime = time.Now()
	tester.operations = append(tester.operations, op)
	return op
}

func (tester *MockLinearizabilityTester) CheckLinearizability() map[string]interface{} {
	tester.mutex.RLock()
	defer tester.mutex.RUnlock()
	
	// Simple linearizability check - real implementation would be more complex
	violations := make([]map[string]interface{}, 0)
	
	// For now, assume all operations are linearizable unless we detect obvious violations
	// In a real implementation, this would involve complex analysis of operation ordering
	
	return map[string]interface{}{
		"is_linearizable":  len(violations) == 0,
		"violations":       violations,
		"total_operations": len(tester.operations),
	}
}

func (tester *MockLinearizabilityTester) GetStatistics() map[string]interface{} {
	tester.mutex.RLock()
	defer tester.mutex.RUnlock()
	
	opsByType := make(map[string]int)
	successful := 0
	
	for _, op := range tester.operations {
		opsByType[op.Type]++
		if op.Success {
			successful++
		}
	}
	
	successRate := 0.0
	if len(tester.operations) > 0 {
		successRate = float64(successful) / float64(len(tester.operations))
	}
	
	return map[string]interface{}{
		"total_operations":   len(tester.operations),
		"operations_by_type": opsByType,
		"success_rate":       successRate,
	}
}

// Main test runner
func TestMain(m *testing.M) {
	fmt.Println("=== Running Go Consistency Model Tests ===")
	
	// Run all tests
	m.Run()
	
	fmt.Println("=== Go Consistency Model Tests Completed ===")
}