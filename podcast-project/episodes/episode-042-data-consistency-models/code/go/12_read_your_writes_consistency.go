/*
Read-Your-Writes Consistency Implementation
User apne writes ko immediately read kar sakta hai
Example: Amazon cart, Gmail sent folder, Facebook posts
*/

package main

import (
	"fmt"
	"log"
	"math/rand"
	"sync"
	"time"
)

// DataItem represents a piece of data with version and metadata
type DataItem struct {
	Key           string
	Value         interface{}
	Version       int64
	LastModified  time.Time
	WriterSession string
	ReplicaID     string
}

// UserSession tracks user's reads and writes for consistency
type UserSession struct {
	SessionID      string
	UserID         string
	LastWrites     map[string]*DataItem // Key -> Last written item
	LastReadTimes  map[string]time.Time // Key -> Last read time
	PreferredReplica string
	CreatedAt      time.Time
	mutex          sync.RWMutex
}

// NewUserSession creates a new user session
func NewUserSession(sessionID, userID, preferredReplica string) *UserSession {
	return &UserSession{
		SessionID:        sessionID,
		UserID:           userID,
		LastWrites:       make(map[string]*DataItem),
		LastReadTimes:    make(map[string]time.Time),
		PreferredReplica: preferredReplica,
		CreatedAt:        time.Now(),
	}
}

// RecordWrite records a write operation in the session
func (s *UserSession) RecordWrite(item *DataItem) {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.LastWrites[item.Key] = item
}

// RecordRead records a read operation in the session
func (s *UserSession) RecordRead(key string) {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.LastReadTimes[key] = time.Now()
}

// GetLastWrite returns the last write for a key
func (s *UserSession) GetLastWrite(key string) (*DataItem, bool) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	item, exists := s.LastWrites[key]
	return item, exists
}

// Replica represents a data store replica
type Replica struct {
	ID            string
	Location      string
	Data          map[string]*DataItem
	SyncDelay     time.Duration // Simulation of network delay
	FailureRate   float64       // Simulation of failures
	mutex         sync.RWMutex
}

// NewReplica creates a new replica
func NewReplica(id, location string, syncDelay time.Duration, failureRate float64) *Replica {
	return &Replica{
		ID:          id,
		Location:    location,
		Data:        make(map[string]*DataItem),
		SyncDelay:   syncDelay,
		FailureRate: failureRate,
	}
}

// Write writes data to the replica
func (r *Replica) Write(key string, value interface{}, sessionID string) (*DataItem, error) {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	// Simulate failure
	if rand.Float64() < r.FailureRate {
		return nil, fmt.Errorf("replica %s write failed", r.ID)
	}

	// Get current version
	currentVersion := int64(1)
	if existing, exists := r.Data[key]; exists {
		currentVersion = existing.Version + 1
	}

	item := &DataItem{
		Key:           key,
		Value:         value,
		Version:       currentVersion,
		LastModified:  time.Now(),
		WriterSession: sessionID,
		ReplicaID:     r.ID,
	}

	r.Data[key] = item
	log.Printf("[%s] Write: %s = %v (v%d) by session %s", r.ID, key, value, currentVersion, sessionID)

	return item, nil
}

// Read reads data from the replica
func (r *Replica) Read(key string) (*DataItem, error) {
	// Simulate network delay
	time.Sleep(r.SyncDelay)

	r.mutex.RLock()
	defer r.mutex.RUnlock()

	// Simulate failure
	if rand.Float64() < r.FailureRate {
		return nil, fmt.Errorf("replica %s read failed", r.ID)
	}

	if item, exists := r.Data[key]; exists {
		log.Printf("[%s] Read: %s = %v (v%d)", r.ID, key, item.Value, item.Version)
		return item, nil
	}

	return nil, fmt.Errorf("key %s not found in replica %s", key, r.ID)
}

// GetVersion returns the version of a key
func (r *Replica) GetVersion(key string) int64 {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	if item, exists := r.Data[key]; exists {
		return item.Version
	}
	return 0
}

// SyncFrom synchronizes data from another replica
func (r *Replica) SyncFrom(source *Replica, key string) error {
	sourceItem, err := source.Read(key)
	if err != nil {
		return err
	}

	r.mutex.Lock()
	defer r.mutex.Unlock()

	// Only sync if source has newer version
	if currentItem, exists := r.Data[key]; !exists || sourceItem.Version > currentItem.Version {
		// Create a copy of the item
		syncedItem := &DataItem{
			Key:           sourceItem.Key,
			Value:         sourceItem.Value,
			Version:       sourceItem.Version,
			LastModified:  sourceItem.LastModified,
			WriterSession: sourceItem.WriterSession,
			ReplicaID:     r.ID, // Update replica ID
		}

		r.Data[key] = syncedItem
		log.Printf("[%s] Synced: %s = %v (v%d) from %s", r.ID, key, syncedItem.Value, syncedItem.Version, source.ID)
		return nil
	}

	return nil
}

// ReadYourWritesStore manages read-your-writes consistency
type ReadYourWritesStore struct {
	Replicas map[string]*Replica
	Sessions map[string]*UserSession
	mutex    sync.RWMutex
}

// NewReadYourWritesStore creates a new store
func NewReadYourWritesStore() *ReadYourWritesStore {
	return &ReadYourWritesStore{
		Replicas: make(map[string]*Replica),
		Sessions: make(map[string]*UserSession),
	}
}

// AddReplica adds a replica to the store
func (store *ReadYourWritesStore) AddReplica(replica *Replica) {
	store.mutex.Lock()
	defer store.mutex.Unlock()
	store.Replicas[replica.ID] = replica
	log.Printf("Added replica: %s (%s)", replica.ID, replica.Location)
}

// CreateSession creates a new user session
func (store *ReadYourWritesStore) CreateSession(userID, preferredReplica string) string {
	sessionID := fmt.Sprintf("session_%d_%s", time.Now().UnixNano(), userID)
	session := NewUserSession(sessionID, userID, preferredReplica)

	store.mutex.Lock()
	defer store.mutex.Unlock()
	store.Sessions[sessionID] = session

	log.Printf("Created session: %s for user %s", sessionID, userID)
	return sessionID
}

// Write performs a write operation with read-your-writes guarantee
func (store *ReadYourWritesStore) Write(sessionID, key string, value interface{}) error {
	store.mutex.RLock()
	session, exists := store.Sessions[sessionID]
	store.mutex.RUnlock()

	if !exists {
		return fmt.Errorf("session %s not found", sessionID)
	}

	// Write to preferred replica first
	replica, exists := store.Replicas[session.PreferredReplica]
	if !exists {
		return fmt.Errorf("preferred replica %s not found", session.PreferredReplica)
	}

	item, err := replica.Write(key, value, sessionID)
	if err != nil {
		return err
	}

	// Record the write in session
	session.RecordWrite(item)

	// Async sync to other replicas
	go store.asyncSync(session.PreferredReplica, key)

	return nil
}

// Read performs a read operation with read-your-writes guarantee
func (store *ReadYourWritesStore) Read(sessionID, key string) (interface{}, error) {
	store.mutex.RLock()
	session, exists := store.Sessions[sessionID]
	store.mutex.RUnlock()

	if !exists {
		return nil, fmt.Errorf("session %s not found", sessionID)
	}

	// Check if user has written this key
	if lastWrite, hasWritten := session.GetLastWrite(key); hasWritten {
		// Ensure we read from a replica that has the user's write
		suitableReplica := store.findReplicaWithVersion(key, lastWrite.Version)
		if suitableReplica != nil {
			item, err := suitableReplica.Read(key)
			if err == nil {
				session.RecordRead(key)
				return item.Value, nil
			}
		}

		// If no suitable replica found, sync and retry
		if err := store.ensureWriteVisibility(session, key); err != nil {
			log.Printf("Warning: Could not ensure write visibility for %s: %v", key, err)
		}
	}

	// Read from preferred replica
	replica, exists := store.Replicas[session.PreferredReplica]
	if !exists {
		return nil, fmt.Errorf("preferred replica %s not found", session.PreferredReplica)
	}

	item, err := replica.Read(key)
	if err != nil {
		// Fallback to other replicas
		for _, fallbackReplica := range store.Replicas {
			if fallbackReplica.ID != session.PreferredReplica {
				if item, err = fallbackReplica.Read(key); err == nil {
					break
				}
			}
		}
	}

	if err != nil {
		return nil, err
	}

	session.RecordRead(key)
	return item.Value, nil
}

// findReplicaWithVersion finds a replica that has at least the specified version
func (store *ReadYourWritesStore) findReplicaWithVersion(key string, minVersion int64) *Replica {
	for _, replica := range store.Replicas {
		if replica.GetVersion(key) >= minVersion {
			return replica
		}
	}
	return nil
}

// ensureWriteVisibility ensures user's write is visible for reading
func (store *ReadYourWritesStore) ensureWriteVisibility(session *UserSession, key string) error {
	lastWrite, hasWritten := session.GetLastWrite(key)
	if !hasWritten {
		return nil
	}

	// Find the replica with the write
	sourceReplica, exists := store.Replicas[lastWrite.ReplicaID]
	if !exists {
		return fmt.Errorf("source replica %s not found", lastWrite.ReplicaID)
	}

	// Sync to preferred replica if needed
	targetReplica, exists := store.Replicas[session.PreferredReplica]
	if !exists {
		return fmt.Errorf("preferred replica %s not found", session.PreferredReplica)
	}

	if targetReplica.GetVersion(key) < lastWrite.Version {
		return targetReplica.SyncFrom(sourceReplica, key)
	}

	return nil
}

// asyncSync asynchronously syncs data to other replicas
func (store *ReadYourWritesStore) asyncSync(sourceReplicaID, key string) {
	sourceReplica, exists := store.Replicas[sourceReplicaID]
	if !exists {
		return
	}

	// Add some delay to simulate real-world sync
	time.Sleep(time.Millisecond * time.Duration(50+rand.Intn(100)))

	for _, targetReplica := range store.Replicas {
		if targetReplica.ID != sourceReplicaID {
			if err := targetReplica.SyncFrom(sourceReplica, key); err != nil {
				log.Printf("Sync failed from %s to %s for key %s: %v", 
					sourceReplicaID, targetReplica.ID, key, err)
			}
		}
	}
}

// GetSessionStats returns statistics for a session
func (store *ReadYourWritesStore) GetSessionStats(sessionID string) map[string]interface{} {
	store.mutex.RLock()
	defer store.mutex.RUnlock()

	session, exists := store.Sessions[sessionID]
	if !exists {
		return nil
	}

	session.mutex.RLock()
	defer session.mutex.RUnlock()

	return map[string]interface{}{
		"session_id":       session.SessionID,
		"user_id":          session.UserID,
		"writes_count":     len(session.LastWrites),
		"reads_count":      len(session.LastReadTimes),
		"preferred_replica": session.PreferredReplica,
		"created_at":       session.CreatedAt,
		"age_seconds":      time.Since(session.CreatedAt).Seconds(),
	}
}

// demonstrateReadYourWrites demonstrates read-your-writes consistency
func demonstrateReadYourWrites() {
	fmt.Println("=== Read-Your-Writes Consistency Demo ===")
	fmt.Println("Amazon cart/Gmail sent folder jaisa behavior")

	// Create store
	store := NewReadYourWritesStore()

	// Add replicas - Indian cities
	mumbaiReplica := NewReplica("mumbai", "Mumbai", 20*time.Millisecond, 0.02)
	delhiReplica := NewReplica("delhi", "Delhi", 30*time.Millisecond, 0.03)
	bangaloreReplica := NewReplica("bangalore", "Bangalore", 25*time.Millisecond, 0.02)
	chennaiReplica := NewReplica("chennai", "Chennai", 35*time.Millisecond, 0.04)

	store.AddReplica(mumbaiReplica)
	store.AddReplica(delhiReplica)
	store.AddReplica(bangaloreReplica)
	store.AddReplica(chennaiReplica)

	fmt.Println("\n=== User Sessions ===")

	// Create user sessions
	rahulSession := store.CreateSession("rahul", "mumbai")
	priyaSession := store.CreateSession("priya", "delhi")
	vikramSession := store.CreateSession("vikram", "bangalore")

	fmt.Println("\n=== Write Operations ===")

	// Rahul adds items to cart
	fmt.Println("Rahul adding items to cart:")
	store.Write(rahulSession, "cart:rahul", []string{"iPhone", "AirPods"})
	store.Write(rahulSession, "profile:rahul", "Rahul Sharma, Mumbai")

	// Priya sends emails
	fmt.Println("\nPriya sending emails:")
	store.Write(priyaSession, "sent:priya:1", "Email to client about project")
	store.Write(priyaSession, "sent:priya:2", "Meeting invite for tomorrow")

	// Vikram creates posts
	fmt.Println("\nVikram creating posts:")
	store.Write(vikramSession, "post:vikram:1", "Working from Bangalore today!")
	store.Write(vikramSession, "post:vikram:2", "Amazing weather in Bangalore")

	fmt.Println("\n=== Immediate Read Tests (Read-Your-Writes) ===")

	// Users immediately read their own writes
	if cart, err := store.Read(rahulSession, "cart:rahul"); err == nil {
		fmt.Printf("Rahul reads his cart immediately: %v\n", cart)
	} else {
		fmt.Printf("❌ Rahul cannot read his cart: %v\n", err)
	}

	if email, err := store.Read(priyaSession, "sent:priya:1"); err == nil {
		fmt.Printf("Priya reads her sent email immediately: %v\n", email)
	} else {
		fmt.Printf("❌ Priya cannot read her sent email: %v\n", err)
	}

	if post, err := store.Read(vikramSession, "post:vikram:1"); err == nil {
		fmt.Printf("Vikram reads his post immediately: %v\n", post)
	} else {
		fmt.Printf("❌ Vikram cannot read his post: %v\n", err)
	}

	fmt.Println("\n=== Cross-User Read Tests ===")

	// Wait a bit for sync
	time.Sleep(200 * time.Millisecond)

	// Users reading others' data (may not be immediately available)
	if post, err := store.Read(rahulSession, "post:vikram:1"); err == nil {
		fmt.Printf("Rahul reads Vikram's post: %v\n", post)
	} else {
		fmt.Printf("Rahul cannot read Vikram's post yet: %v\n", err)
	}

	if cart, err := store.Read(priyaSession, "cart:rahul"); err == nil {
		fmt.Printf("Priya reads Rahul's cart: %v\n", cart)
	} else {
		fmt.Printf("Priya cannot read Rahul's cart yet: %v\n", err)
	}

	fmt.Println("\n=== Concurrent Write/Read Test ===")

	// Test rapid write followed by read
	var wg sync.WaitGroup
	
	wg.Add(1)
	go func() {
		defer wg.Done()
		store.Write(rahulSession, "quick_update", "Urgent message")
		
		// Immediate read after write
		if value, err := store.Read(rahulSession, "quick_update"); err == nil {
			fmt.Printf("✅ Rapid write-read test passed: %v\n", value)
		} else {
			fmt.Printf("❌ Rapid write-read test failed: %v\n", err)
		}
	}()

	wg.Wait()

	fmt.Println("\n=== Session Statistics ===")

	// Show session stats
	for _, sessionID := range []string{rahulSession, priyaSession, vikramSession} {
		stats := store.GetSessionStats(sessionID)
		if stats != nil {
			fmt.Printf("Session %s:\n", stats["user_id"])
			fmt.Printf("  Writes: %d, Reads: %d\n", stats["writes_count"], stats["reads_count"])
			fmt.Printf("  Preferred replica: %s\n", stats["preferred_replica"])
			fmt.Printf("  Age: %.2f seconds\n", stats["age_seconds"])
		}
	}

	fmt.Println("\n=== Stress Test: Multiple Rapid Operations ===")

	stressTest := func(sessionID, userID string, operations int) {
		var wg sync.WaitGroup
		
		for i := 0; i < operations; i++ {
			wg.Add(1)
			go func(i int) {
				defer wg.Done()
				
				key := fmt.Sprintf("stress:%s:%d", userID, i)
				value := fmt.Sprintf("Value %d by %s", i, userID)
				
				// Write then immediately read
				if err := store.Write(sessionID, key, value); err != nil {
					log.Printf("Stress write failed: %v", err)
					return
				}
				
				if readValue, err := store.Read(sessionID, key); err != nil {
					log.Printf("❌ Stress read-your-writes failed for %s: %v", key, err)
				} else if readValue != value {
					log.Printf("❌ Stress read-your-writes inconsistent for %s: expected %v, got %v", 
						key, value, readValue)
				}
			}(i)
		}
		
		wg.Wait()
		fmt.Printf("Completed stress test for %s: %d operations\n", userID, operations)
	}

	// Run stress tests concurrently
	var stressWG sync.WaitGroup
	stressWG.Add(3)
	
	go func() {
		defer stressWG.Done()
		stressTest(rahulSession, "rahul", 20)
	}()
	
	go func() {
		defer stressWG.Done()
		stressTest(priyaSession, "priya", 20)
	}()
	
	go func() {
		defer stressWG.Done()
		stressTest(vikramSession, "vikram", 20)
	}()
	
	stressWG.Wait()

	fmt.Println("\n=== Final Replica Status ===")

	// Show final state of all replicas
	for _, replica := range store.Replicas {
		replica.mutex.RLock()
		dataCount := len(replica.Data)
		replica.mutex.RUnlock()
		
		fmt.Printf("%s (%s): %d items\n", replica.ID, replica.Location, dataCount)
	}

	fmt.Println("\n✅ Read-Your-Writes Consistency demo completed!")
	fmt.Println("\nKey Benefits:")
	fmt.Println("- Users always see their own writes immediately")
	fmt.Println("- Works even when replicas are not fully synchronized")
	fmt.Println("- Essential for user experience (cart, sent messages, posts)")
	fmt.Println("- Handles network delays and partial failures gracefully")
}

func main() {
	// Set random seed for consistent demo behavior
	rand.Seed(time.Now().UnixNano())
	
	// Configure logging
	log.SetFlags(log.Ltime | log.Lmicroseconds)
	
	// Run demonstration
	demonstrateReadYourWrites()
}