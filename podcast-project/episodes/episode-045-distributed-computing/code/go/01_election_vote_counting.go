package main

import (
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"log"
	"math/big"
	"sync"
	"sync/atomic"
	"time"
)

/*
Election Vote Counting System - Distributed Computing Implementation
भारत के चुनाव में vote counting का distributed implementation

यह example दिखाता है कि कैसे भारत के General Elections में millions of votes को
multiple counting centers के बीच efficiently process करते हैं using
distributed computing principles। Election Commission of India (ECI)
इसी तरह के systems use करती है real-time vote counting के लिए।

Production context: India processes 600+ million votes across 1M+ polling stations
Scale: Results aggregated in real-time from 2,000+ counting centers
Challenge: Ensuring accuracy, preventing fraud, and delivering results within hours
*/

// VoteRecord represents a single vote cast
type VoteRecord struct {
	VoteID          string    `json:"vote_id"`
	ConstituencyID  string    `json:"constituency_id"`
	PollingStationID string   `json:"polling_station_id"`
	CandidateID     string    `json:"candidate_id"`
	PartyID         string    `json:"party_id"`
	Timestamp       time.Time `json:"timestamp"`
	VerificationHash string   `json:"verification_hash"`
}

// CandidateInfo represents candidate information
type CandidateInfo struct {
	CandidateID   string `json:"candidate_id"`
	Name          string `json:"name"`
	PartyID       string `json:"party_id"`
	PartyName     string `json:"party_name"`
	ConstituencyID string `json:"constituency_id"`
}

// CountingResult represents vote counting results
type CountingResult struct {
	ConstituencyID   string            `json:"constituency_id"`
	ConstituencyName string            `json:"constituency_name"`
	TotalVotes       int64             `json:"total_votes"`
	ValidVotes       int64             `json:"valid_votes"`
	InvalidVotes     int64             `json:"invalid_votes"`
	CandidateVotes   map[string]int64  `json:"candidate_votes"`
	PartyVotes       map[string]int64  `json:"party_votes"`
	Winner          *CandidateInfo    `json:"winner"`
	Margin          int64             `json:"margin"`
	ProcessingTime  time.Duration     `json:"processing_time"`
	LastUpdated     time.Time         `json:"last_updated"`
}

// DistributedCountingCenter represents a single counting center
type DistributedCountingCenter struct {
	CenterID     string
	Region       string
	State        string
	Mutex        sync.RWMutex
	
	// Vote processing
	VoteQueue    chan VoteRecord
	Results      map[string]*CountingResult
	Candidates   map[string]*CandidateInfo
	
	// Statistics
	ProcessedVotes   int64
	InvalidVotes     int64
	ProcessingErrors int64
	StartTime       time.Time
	
	// Cluster coordination
	ClusterNodes    map[string]*DistributedCountingCenter
	IsRunning       int32
	WorkerCount     int
	
	// Result broadcasting
	ResultChannel   chan *CountingResult
	subscribers     []chan *CountingResult
	
	ctx    context.Context
	cancel context.CancelFunc
}

// NewDistributedCountingCenter creates a new counting center
func NewDistributedCountingCenter(centerID, region, state string, workerCount int) *DistributedCountingCenter {
	ctx, cancel := context.WithCancel(context.Background())
	
	center := &DistributedCountingCenter{
		CenterID:        centerID,
		Region:          region,
		State:           state,
		VoteQueue:       make(chan VoteRecord, 10000), // Buffer for 10K votes
		Results:         make(map[string]*CountingResult),
		Candidates:      make(map[string]*CandidateInfo),
		ClusterNodes:    make(map[string]*DistributedCountingCenter),
		WorkerCount:     workerCount,
		ResultChannel:   make(chan *CountingResult, 1000),
		subscribers:     make([]chan *CountingResult, 0),
		ctx:             ctx,
		cancel:          cancel,
		StartTime:       time.Now(),
	}
	
	// Initialize with sample candidates for demo
	center.initializeSampleCandidates()
	
	log.Printf("[%s] Election counting center initialized in %s, %s with %d workers", 
		centerID, region, state, workerCount)
	
	return center
}

// initializeSampleCandidates sets up sample candidates for demonstration
func (dcc *DistributedCountingCenter) initializeSampleCandidates() {
	candidates := []*CandidateInfo{
		{"CAND001", "Rahul Gandhi", "INC", "Indian National Congress", "CONSTITUENCY_001"},
		{"CAND002", "Narendra Modi", "BJP", "Bharatiya Janata Party", "CONSTITUENCY_001"},
		{"CAND003", "Arvind Kejriwal", "AAP", "Aam Aadmi Party", "CONSTITUENCY_001"},
		{"CAND004", "Mamata Banerjee", "AITC", "All India Trinamool Congress", "CONSTITUENCY_002"},
		{"CAND005", "Yogi Adityanath", "BJP", "Bharatiya Janata Party", "CONSTITUENCY_002"},
		{"CAND006", "Priyanka Gandhi", "INC", "Indian National Congress", "CONSTITUENCY_002"},
		{"CAND007", "Akhilesh Yadav", "SP", "Samajwadi Party", "CONSTITUENCY_003"},
		{"CAND008", "Mayawati", "BSP", "Bahujan Samaj Party", "CONSTITUENCY_003"},
		{"CAND009", "Sharad Pawar", "NCP", "Nationalist Congress Party", "CONSTITUENCY_003"},
	}
	
	for _, candidate := range candidates {
		dcc.Candidates[candidate.CandidateID] = candidate
	}
}

// AddClusterNode adds another counting center to the cluster
func (dcc *DistributedCountingCenter) AddClusterNode(node *DistributedCountingCenter) {
	dcc.Mutex.Lock()
	defer dcc.Mutex.Unlock()
	
	dcc.ClusterNodes[node.CenterID] = node
	log.Printf("[%s] Added cluster node: %s (%s, %s)", 
		dcc.CenterID, node.CenterID, node.Region, node.State)
}

// Start begins the vote counting process
func (dcc *DistributedCountingCenter) Start() {
	if !atomic.CompareAndSwapInt32(&dcc.IsRunning, 0, 1) {
		return
	}
	
	log.Printf("[%s] Starting election counting center with %d workers", 
		dcc.CenterID, dcc.WorkerCount)
	
	// Start worker goroutines for vote processing
	for i := 0; i < dcc.WorkerCount; i++ {
		go dcc.voteProcessingWorker(i)
	}
	
	// Start result broadcasting goroutine
	go dcc.resultBroadcaster()
	
	// Start periodic statistics reporting
	go dcc.statisticsReporter()
}

// Stop gracefully shuts down the counting center
func (dcc *DistributedCountingCenter) Stop() {
	if !atomic.CompareAndSwapInt32(&dcc.IsRunning, 1, 0) {
		return
	}
	
	log.Printf("[%s] Stopping election counting center", dcc.CenterID)
	dcc.cancel()
	close(dcc.VoteQueue)
	close(dcc.ResultChannel)
}

// SubmitVote submits a vote for counting
func (dcc *DistributedCountingCenter) SubmitVote(vote VoteRecord) error {
	select {
	case dcc.VoteQueue <- vote:
		return nil
	case <-time.After(time.Second):
		atomic.AddInt64(&dcc.ProcessingErrors, 1)
		return fmt.Errorf("vote queue full, vote rejected")
	}
}

// voteProcessingWorker processes votes from the queue
func (dcc *DistributedCountingCenter) voteProcessingWorker(workerID int) {
	log.Printf("[%s] Vote processing worker %d started", dcc.CenterID, workerID)
	
	for {
		select {
		case vote, ok := <-dcc.VoteQueue:
			if !ok {
				log.Printf("[%s] Worker %d shutting down - queue closed", dcc.CenterID, workerID)
				return
			}
			
			dcc.processVote(vote)
			
		case <-dcc.ctx.Done():
			log.Printf("[%s] Worker %d shutting down - context cancelled", dcc.CenterID, workerID)
			return
		}
	}
}

// processVote processes a single vote record
func (dcc *DistributedCountingCenter) processVote(vote VoteRecord) {
	startTime := time.Now()
	
	// Validate vote
	if !dcc.validateVote(vote) {
		atomic.AddInt64(&dcc.InvalidVotes, 1)
		log.Printf("[%s] Invalid vote rejected: %s", dcc.CenterID, vote.VoteID)
		return
	}
	
	// Update results atomically
	dcc.Mutex.Lock()
	defer dcc.Mutex.Unlock()
	
	// Get or create constituency result
	result, exists := dcc.Results[vote.ConstituencyID]
	if !exists {
		result = &CountingResult{
			ConstituencyID:   vote.ConstituencyID,
			ConstituencyName: fmt.Sprintf("Constituency %s", vote.ConstituencyID),
			CandidateVotes:   make(map[string]int64),
			PartyVotes:       make(map[string]int64),
			LastUpdated:      time.Now(),
		}
		dcc.Results[vote.ConstituencyID] = result
	}
	
	// Update vote counts
	result.TotalVotes++
	result.ValidVotes++
	result.CandidateVotes[vote.CandidateID]++
	
	// Update party votes
	candidate, exists := dcc.Candidates[vote.CandidateID]
	if exists {
		result.PartyVotes[candidate.PartyID]++
	}
	
	// Determine winner and margin
	dcc.updateWinner(result)
	
	result.LastUpdated = time.Now()
	result.ProcessingTime = time.Since(startTime)
	
	atomic.AddInt64(&dcc.ProcessedVotes, 1)
	
	// Broadcast result update every 100 votes
	if result.TotalVotes%100 == 0 {
		select {
		case dcc.ResultChannel <- result:
		default:
			// Channel full, skip broadcast
		}
	}
	
	// Log progress for high-profile constituencies
	if result.TotalVotes%1000 == 0 {
		log.Printf("[%s] %s: %d votes counted, current leader: %s", 
			dcc.CenterID, result.ConstituencyName, result.TotalVotes, 
			func() string {
				if result.Winner != nil {
					return result.Winner.Name
				}
				return "TBD"
			}())
	}
}

// validateVote validates a vote record
func (dcc *DistributedCountingCenter) validateVote(vote VoteRecord) bool {
	// Check if candidate exists
	if _, exists := dcc.Candidates[vote.CandidateID]; !exists {
		return false
	}
	
	// Check timestamp (should be within election day)
	now := time.Now()
	if vote.Timestamp.After(now) || vote.Timestamp.Before(now.Add(-24*time.Hour)) {
		return false
	}
	
	// Verify hash (simplified check)
	if len(vote.VerificationHash) < 10 {
		return false
	}
	
	return true
}

// updateWinner determines the current winner for a constituency
func (dcc *DistributedCountingCenter) updateWinner(result *CountingResult) {
	var winnerID string
	var maxVotes int64 = 0
	var secondMaxVotes int64 = 0
	
	for candidateID, votes := range result.CandidateVotes {
		if votes > maxVotes {
			secondMaxVotes = maxVotes
			maxVotes = votes
			winnerID = candidateID
		} else if votes > secondMaxVotes {
			secondMaxVotes = votes
		}
	}
	
	if winnerID != "" {
		if candidate, exists := dcc.Candidates[winnerID]; exists {
			result.Winner = candidate
			result.Margin = maxVotes - secondMaxVotes
		}
	}
}

// resultBroadcaster broadcasts results to subscribers
func (dcc *DistributedCountingCenter) resultBroadcaster() {
	log.Printf("[%s] Result broadcaster started", dcc.CenterID)
	
	for {
		select {
		case result, ok := <-dcc.ResultChannel:
			if !ok {
				log.Printf("[%s] Result broadcaster shutting down", dcc.CenterID)
				return
			}
			
			// Broadcast to all subscribers
			for _, subscriber := range dcc.subscribers {
				select {
				case subscriber <- result:
				default:
					// Subscriber channel full, skip
				}
			}
			
			// Broadcast to cluster nodes
			dcc.broadcastToCluster(result)
			
		case <-dcc.ctx.Done():
			log.Printf("[%s] Result broadcaster shutting down - context cancelled", dcc.CenterID)
			return
		}
	}
}

// broadcastToCluster broadcasts results to other nodes in the cluster
func (dcc *DistributedCountingCenter) broadcastToCluster(result *CountingResult) {
	dcc.Mutex.RLock()
	defer dcc.Mutex.RUnlock()
	
	for nodeID, node := range dcc.ClusterNodes {
		if atomic.LoadInt32(&node.IsRunning) == 1 {
			select {
			case node.ResultChannel <- result:
				// Successfully broadcasted
			default:
				log.Printf("[%s] Failed to broadcast to node %s - channel full", 
					dcc.CenterID, nodeID)
			}
		}
	}
}

// statisticsReporter periodically reports processing statistics
func (dcc *DistributedCountingCenter) statisticsReporter() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			dcc.reportStatistics()
		case <-dcc.ctx.Done():
			return
		}
	}
}

// reportStatistics reports current processing statistics
func (dcc *DistributedCountingCenter) reportStatistics() {
	processed := atomic.LoadInt64(&dcc.ProcessedVotes)
	invalid := atomic.LoadInt64(&dcc.InvalidVotes)
	errors := atomic.LoadInt64(&dcc.ProcessingErrors)
	
	elapsed := time.Since(dcc.StartTime)
	votesPerSecond := float64(processed) / elapsed.Seconds()
	
	dcc.Mutex.RLock()
	constituencyCount := len(dcc.Results)
	dcc.Mutex.RUnlock()
	
	log.Printf("[%s] Stats: Processed=%d, Invalid=%d, Errors=%d, Rate=%.1f votes/sec, Constituencies=%d", 
		dcc.CenterID, processed, invalid, errors, votesPerSecond, constituencyCount)
}

// GetResults returns current counting results
func (dcc *DistributedCountingCenter) GetResults() map[string]*CountingResult {
	dcc.Mutex.RLock()
	defer dcc.Mutex.RUnlock()
	
	// Create a copy of results
	results := make(map[string]*CountingResult)
	for k, v := range dcc.Results {
		// Deep copy the result
		resultCopy := *v
		resultCopy.CandidateVotes = make(map[string]int64)
		resultCopy.PartyVotes = make(map[string]int64)
		
		for ck, cv := range v.CandidateVotes {
			resultCopy.CandidateVotes[ck] = cv
		}
		for pk, pv := range v.PartyVotes {
			resultCopy.PartyVotes[pk] = pv
		}
		
		results[k] = &resultCopy
	}
	
	return results
}

// GetAggregatedResults aggregates results across all cluster nodes
func (dcc *DistributedCountingCenter) GetAggregatedResults() map[string]*CountingResult {
	aggregated := dcc.GetResults()
	
	dcc.Mutex.RLock()
	defer dcc.Mutex.RUnlock()
	
	// Aggregate results from cluster nodes
	for _, node := range dcc.ClusterNodes {
		nodeResults := node.GetResults()
		
		for constituencyID, nodeResult := range nodeResults {
			if existing, exists := aggregated[constituencyID]; exists {
				// Merge results
				existing.TotalVotes += nodeResult.TotalVotes
				existing.ValidVotes += nodeResult.ValidVotes
				existing.InvalidVotes += nodeResult.InvalidVotes
				
				for candidateID, votes := range nodeResult.CandidateVotes {
					existing.CandidateVotes[candidateID] += votes
				}
				
				for partyID, votes := range nodeResult.PartyVotes {
					existing.PartyVotes[partyID] += votes
				}
				
				// Update winner based on merged data
				dcc.updateWinner(existing)
				
			} else {
				// Copy new constituency result
				resultCopy := *nodeResult
				resultCopy.CandidateVotes = make(map[string]int64)
				resultCopy.PartyVotes = make(map[string]int64)
				
				for ck, cv := range nodeResult.CandidateVotes {
					resultCopy.CandidateVotes[ck] = cv
				}
				for pk, pv := range nodeResult.PartyVotes {
					resultCopy.PartyVotes[pk] = pv
				}
				
				aggregated[constituencyID] = &resultCopy
			}
		}
	}
	
	return aggregated
}

// generateRandomVote generates a random vote for simulation
func generateRandomVote(constituencyID string, candidates []string) VoteRecord {
	// Random candidate selection with some bias towards major parties
	candidateIndex := 0
	if len(candidates) > 0 {
		r, _ := rand.Int(rand.Reader, big.NewInt(int64(len(candidates))))
		candidateIndex = int(r.Int64())
	}
	
	candidateID := candidates[candidateIndex]
	
	// Generate vote ID
	voteIDNum, _ := rand.Int(rand.Reader, big.NewInt(1000000))
	voteID := fmt.Sprintf("VOTE_%s_%06d", constituencyID, voteIDNum.Int64())
	
	// Generate polling station ID
	stationNum, _ := rand.Int(rand.Reader, big.NewInt(300))
	stationID := fmt.Sprintf("PS_%s_%03d", constituencyID, stationNum.Int64())
	
	return VoteRecord{
		VoteID:           voteID,
		ConstituencyID:   constituencyID,
		PollingStationID: stationID,
		CandidateID:      candidateID,
		PartyID:          fmt.Sprintf("PARTY_%s", candidateID[4:7]),
		Timestamp:        time.Now().Add(-time.Duration(stationNum.Int64()) * time.Minute),
		VerificationHash: fmt.Sprintf("HASH_%d", time.Now().UnixNano()),
	}
}

// Main demonstration function
func main() {
	fmt.Println("🗳️  Indian Election Distributed Vote Counting System")
	fmt.Println("=" + string(make([]byte, 59)))
	
	// Create counting centers for different regions
	northernCenter := NewDistributedCountingCenter("ECI-NORTH-01", "Northern", "Delhi", 8)
	westernCenter := NewDistributedCountingCenter("ECI-WEST-01", "Western", "Maharashtra", 6)
	southernCenter := NewDistributedCountingCenter("ECI-SOUTH-01", "Southern", "Tamil Nadu", 10)
	
	// Setup cluster
	fmt.Println("\n🏢 Setting up distributed counting cluster...")
	northernCenter.AddClusterNode(westernCenter)
	northernCenter.AddClusterNode(southernCenter)
	westernCenter.AddClusterNode(northernCenter)
	westernCenter.AddClusterNode(southernCenter)
	southernCenter.AddClusterNode(northernCenter)
	southernCenter.AddClusterNode(westernCenter)
	
	// Start all centers
	northernCenter.Start()
	westernCenter.Start()
	southernCenter.Start()
	
	fmt.Println("✅ All counting centers started")
	
	// Simulate vote submission from different constituencies
	fmt.Println("\n📊 Simulating vote counting from polling stations...")
	
	constituencies := []string{"CONSTITUENCY_001", "CONSTITUENCY_002", "CONSTITUENCY_003"}
	candidateGroups := map[string][]string{
		"CONSTITUENCY_001": {"CAND001", "CAND002", "CAND003"},
		"CONSTITUENCY_002": {"CAND004", "CAND005", "CAND006"},
		"CONSTITUENCY_003": {"CAND007", "CAND008", "CAND009"},
	}
	
	// Submit votes in batches
	centers := []*DistributedCountingCenter{northernCenter, westernCenter, southernCenter}
	
	for round := 0; round < 10; round++ {
		fmt.Printf("\nRound %d: Submitting votes...\n", round+1)
		
		for _, constituency := range constituencies {
			candidates := candidateGroups[constituency]
			
			// Submit 1000 votes per constituency per round
			for i := 0; i < 1000; i++ {
				vote := generateRandomVote(constituency, candidates)
				
				// Distribute votes across centers
				center := centers[i%len(centers)]
				if err := center.SubmitVote(vote); err != nil {
					log.Printf("Failed to submit vote: %v", err)
				}
			}
		}
		
		// Wait between rounds
		time.Sleep(2 * time.Second)
	}
	
	// Allow processing to complete
	fmt.Println("\n⏳ Allowing vote processing to complete...")
	time.Sleep(5 * time.Second)
	
	// Display results from each center
	fmt.Println("\n📋 Results from individual counting centers:")
	for _, center := range centers {
		fmt.Printf("\n--- %s (%s, %s) ---\n", center.CenterID, center.Region, center.State)
		results := center.GetResults()
		
		for constituencyID, result := range results {
			fmt.Printf("Constituency: %s\n", result.ConstituencyName)
			fmt.Printf("  Total votes: %d\n", result.TotalVotes)
			fmt.Printf("  Valid votes: %d\n", result.ValidVotes)
			
			if result.Winner != nil {
				fmt.Printf("  Leading: %s (%s) with %d votes (margin: %d)\n",
					result.Winner.Name, result.Winner.PartyName, 
					result.CandidateVotes[result.Winner.CandidateID], result.Margin)
			}
			
			fmt.Printf("  Top candidates:\n")
			// Sort candidates by votes
			type candidateVote struct {
				ID    string
				Votes int64
			}
			var sorted []candidateVote
			for candidateID, votes := range result.CandidateVotes {
				sorted = append(sorted, candidateVote{candidateID, votes})
			}
			
			// Simple sort by votes (descending)
			for i := 0; i < len(sorted); i++ {
				for j := i + 1; j < len(sorted); j++ {
					if sorted[j].Votes > sorted[i].Votes {
						sorted[i], sorted[j] = sorted[j], sorted[i]
					}
				}
			}
			
			for i, cv := range sorted {
				if i >= 3 { break } // Top 3
				if candidate, exists := center.Candidates[cv.ID]; exists {
					fmt.Printf("    %d. %s (%s): %d votes\n", 
						i+1, candidate.Name, candidate.PartyName, cv.Votes)
				}
			}
			fmt.Println()
		}
	}
	
	// Display aggregated results
	fmt.Println("\n🏆 Aggregated Election Results Across All Centers:")
	fmt.Println("=" + string(make([]byte, 50)))
	
	aggregatedResults := northernCenter.GetAggregatedResults()
	
	for constituencyID, result := range aggregatedResults {
		fmt.Printf("\n%s:\n", result.ConstituencyName)
		fmt.Printf("  Total votes counted: %d\n", result.TotalVotes)
		
		if result.Winner != nil {
			fmt.Printf("  🥇 WINNER: %s (%s)\n", result.Winner.Name, result.Winner.PartyName)
			fmt.Printf("  Votes: %d (Margin: %d votes)\n", 
				result.CandidateVotes[result.Winner.CandidateID], result.Margin)
		}
		
		fmt.Printf("  Party-wise votes:\n")
		for partyID, votes := range result.PartyVotes {
			fmt.Printf("    %s: %d votes\n", partyID, votes)
		}
	}
	
	// Display final statistics
	fmt.Println("\n📈 Final Processing Statistics:")
	for _, center := range centers {
		processed := atomic.LoadInt64(&center.ProcessedVotes)
		invalid := atomic.LoadInt64(&center.InvalidVotes)
		errors := atomic.LoadInt64(&center.ProcessingErrors)
		elapsed := time.Since(center.StartTime)
		rate := float64(processed) / elapsed.Seconds()
		
		fmt.Printf("%s: Processed=%d, Invalid=%d, Errors=%d, Rate=%.1f votes/sec\n",
			center.CenterID, processed, invalid, errors, rate)
	}
	
	// Production insights
	fmt.Println("\n💡 Production Insights:")
	fmt.Println("- Distributed counting enables processing 600M+ votes across India simultaneously")
	fmt.Println("- Real-time result aggregation provides live election updates")
	fmt.Println("- Fault tolerance through multiple counting centers prevents single points of failure")
	fmt.Println("- Worker pool pattern scales to handle varying vote volumes across constituencies")
	fmt.Println("- Result broadcasting enables live TV coverage and ECI website updates")
	fmt.Println("- Validation ensures vote integrity and prevents counting errors")
	fmt.Println("- Horizontal scaling possible by adding more regional counting centers")
	fmt.Println("- Critical for maintaining democratic transparency and public trust")
	
	// Cleanup
	fmt.Println("\n🧹 Shutting down counting centers...")
	northernCenter.Stop()
	westernCenter.Stop()
	southernCenter.Stop()
	
	fmt.Println("Election counting demo completed!")
}