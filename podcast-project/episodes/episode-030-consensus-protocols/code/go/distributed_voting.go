/*
Distributed Voting System
=========================

Mumbai Election Commission Style!
Just like Mumbai conducts elections across multiple constituencies,
this system demonstrates distributed voting with consensus mechanisms.

Features:
- Multi-constituency voting
- Fraud detection consensus
- Vote tallying across distributed nodes
- Election result verification
- Mumbai democracy simulation

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
*/

package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"math/big"
	"sort"
	"sync"
	"time"
)

// Election system types
type VoterStatus string

const (
	ELIGIBLE    VoterStatus = "eligible"
	VOTED       VoterStatus = "voted"
	INELIGIBLE  VoterStatus = "ineligible"
	SUSPENDED   VoterStatus = "suspended"
)

type VoteChoice string

const (
	CANDIDATE_A VoteChoice = "candidate_a"
	CANDIDATE_B VoteChoice = "candidate_b"
	CANDIDATE_C VoteChoice = "candidate_c"
	NOTA        VoteChoice = "nota" // None Of The Above
)

type ElectionPhase string

const (
	REGISTRATION ElectionPhase = "registration"
	VOTING       ElectionPhase = "voting"
	COUNTING     ElectionPhase = "counting"
	COMPLETED    ElectionPhase = "completed"
)

// Core structures
type Voter struct {
	ID           string
	Name         string
	Constituency string
	Status       VoterStatus
	HasVoted     bool
	VoteHash     string // For privacy while maintaining integrity
	Timestamp    time.Time
}

type Vote struct {
	VoterID      string
	Choice       VoteChoice
	Constituency string
	Timestamp    time.Time
	Hash         string
	Signature    string // Simplified digital signature
}

type Candidate struct {
	ID           string
	Name         string
	Party        string
	Constituency string
	VoteCount    int
	Percentage   float64
}

type Constituency struct {
	ID                string
	Name              string
	TotalVoters       int
	VotesCast         int
	Candidates        []*Candidate
	Votes             []*Vote
	ElectionOfficer   string
	Phase             ElectionPhase
	SecurityLevel     float64 // 0.0-1.0, Mumbai security concerns
	
	// Consensus mechanism
	ValidationNodes   []string
	ConsensusThreshold float64
}

type ElectionNode struct {
	ID               string
	Name             string
	Region           string
	Constituencies   map[string]*Constituency
	Reliability      float64
	ProcessingSpeed  time.Duration
	
	// Performance metrics
	VotesProcessed   int
	ValidationsDone  int
	FraudDetected    int
	UptimeSeconds    int64
	
	// Mumbai characteristics
	PowerBackup      bool    // UPS availability
	NetworkStability float64 // Internet connectivity
	StaffPresent     bool    // Election staff availability
}

func NewElectionNode(id, name, region string) *ElectionNode {
	// Generate random characteristics for Mumbai nodes
	randBig, _ := rand.Int(rand.Reader, big.NewInt(100))
	reliabilityBase := float64(randBig.Int64()) / 100.0
	
	randSpeed, _ := rand.Int(rand.Reader, big.NewInt(500))
	processingSpeed := time.Duration(100+randSpeed.Int64()) * time.Millisecond
	
	randNetwork, _ := rand.Int(rand.Reader, big.NewInt(40))
	networkStability := 0.6 + float64(randNetwork.Int64())/100.0 // 60-100%
	
	randBackup, _ := rand.Int(rand.Reader, big.NewInt(100))
	powerBackup := randBackup.Int64() > 20 // 80% have backup power
	
	return &ElectionNode{
		ID:               id,
		Name:             name,
		Region:           region,
		Constituencies:   make(map[string]*Constituency),
		Reliability:      0.85 + reliabilityBase*0.14, // 85-99%
		ProcessingSpeed:  processingSpeed,
		PowerBackup:      powerBackup,
		NetworkStability: networkStability,
		StaffPresent:     true, // Assume staff is present during elections
		
		VotesProcessed:  0,
		ValidationsDone: 0,
		FraudDetected:   0,
		UptimeSeconds:   0,
	}
}

func (en *ElectionNode) IsOperational() bool {
	if !en.PowerBackup {
		// Simulate power cuts in Mumbai
		randPower, _ := rand.Int(rand.Reader, big.NewInt(100))
		if randPower.Int64() < 15 { // 15% chance of power failure
			return false
		}
	}
	
	return en.StaffPresent && en.NetworkStability > 0.3
}

func (en *ElectionNode) AddConstituency(constituency *Constituency) {
	en.Constituencies[constituency.ID] = constituency
	fmt.Printf("🏛️ Node %s managing constituency: %s\n", en.Name, constituency.Name)
}

func (en *ElectionNode) ProcessVote(vote *Vote) error {
	if !en.IsOperational() {
		return fmt.Errorf("election node %s is not operational", en.ID)
	}
	
	// Simulate processing time
	time.Sleep(en.ProcessingSpeed)
	
	constituency, exists := en.Constituencies[vote.Constituency]
	if !exists {
		return fmt.Errorf("constituency %s not managed by this node", vote.Constituency)
	}
	
	// Validate vote
	if err := en.validateVote(vote, constituency); err != nil {
		return fmt.Errorf("vote validation failed: %v", err)
	}
	
	// Add vote to constituency
	constituency.Votes = append(constituency.Votes, vote)
	constituency.VotesCast++
	
	en.VotesProcessed++
	
	fmt.Printf("   ✅ Vote processed by %s for constituency %s\n", 
		en.Name, constituency.Name)
	
	return nil
}

func (en *ElectionNode) validateVote(vote *Vote, constituency *Constituency) error {
	en.ValidationsDone++
	
	// Check if vote hash is valid
	expectedHash := calculateVoteHash(vote)
	if vote.Hash != expectedHash {
		en.FraudDetected++
		return fmt.Errorf("vote hash mismatch")
	}
	
	// Check for duplicate voting
	for _, existingVote := range constituency.Votes {
		if existingVote.VoterID == vote.VoterID {
			en.FraudDetected++
			return fmt.Errorf("duplicate vote detected for voter %s", vote.VoterID)
		}
	}
	
	// Validate choice
	validChoice := false
	for _, candidate := range constituency.Candidates {
		if vote.Choice == VoteChoice(candidate.ID) || vote.Choice == NOTA {
			validChoice = true
			break
		}
	}
	
	if !validChoice {
		return fmt.Errorf("invalid vote choice: %s", vote.Choice)
	}
	
	// Simulate fraud detection with Mumbai-specific patterns
	if en.detectFraud(vote) {
		en.FraudDetected++
		return fmt.Errorf("potential fraud detected")
	}
	
	return nil
}

func (en *ElectionNode) detectFraud(vote *Vote) bool {
	// Mumbai-specific fraud detection patterns
	
	// Check for suspicious timing patterns
	now := time.Now()
	if vote.Timestamp.After(now) {
		return true // Future timestamp
	}
	
	// Check for unusual voting patterns during election hours
	hour := vote.Timestamp.Hour()
	if hour < 7 || hour > 18 { // Voting hours: 7 AM to 6 PM
		return true
	}
	
	// Random fraud detection (simulating ML-based detection)
	randFraud, _ := rand.Int(rand.Reader, big.NewInt(1000))
	return randFraud.Int64() < 5 // 0.5% chance of fraud detection
}

func calculateVoteHash(vote *Vote) string {
	data := fmt.Sprintf("%s:%s:%s:%d", 
		vote.VoterID, string(vote.Choice), vote.Constituency, 
		vote.Timestamp.Unix())
	hash := sha256.Sum256([]byte(data))
	return hex.EncodeToString(hash[:])[:16]
}

// Distributed Voting System
type DistributedVotingSystem struct {
	Nodes         []*ElectionNode
	Constituencies map[string]*Constituency
	Voters        map[string]*Voter
	TotalVotes    int
	
	// Consensus parameters
	ConsensusThreshold float64
	ValidationRounds   int
	
	// System metrics
	StartTime         time.Time
	ProcessingTime    time.Duration
	TotalValidations  int
	FraudAttempts     int
	
	mu sync.RWMutex
}

func NewDistributedVotingSystem(consensusThreshold float64) *DistributedVotingSystem {
	return &DistributedVotingSystem{
		Nodes:              make([]*ElectionNode, 0),
		Constituencies:     make(map[string]*Constituency),
		Voters:             make(map[string]*Voter),
		ConsensusThreshold: consensusThreshold,
		ValidationRounds:   3,
		StartTime:          time.Now(),
		
		TotalVotes:       0,
		TotalValidations: 0,
		FraudAttempts:    0,
	}
}

func (dvs *DistributedVotingSystem) AddElectionNode(node *ElectionNode) {
	dvs.mu.Lock()
	defer dvs.mu.Unlock()
	
	dvs.Nodes = append(dvs.Nodes, node)
	fmt.Printf("📊 Added election node: %s (Region: %s)\n", node.Name, node.Region)
}

func (dvs *DistributedVotingSystem) RegisterConstituency(constituency *Constituency) {
	dvs.mu.Lock()
	defer dvs.mu.Unlock()
	
	dvs.Constituencies[constituency.ID] = constituency
	
	// Assign to appropriate nodes based on region
	for _, node := range dvs.Nodes {
		// Simple assignment: each constituency managed by 2-3 nodes for redundancy
		if len(node.Constituencies) < 3 {
			node.AddConstituency(constituency)
		}
	}
	
	fmt.Printf("🏛️ Registered constituency: %s (%d voters)\n", 
		constituency.Name, constituency.TotalVoters)
}

func (dvs *DistributedVotingSystem) RegisterVoter(voter *Voter) {
	dvs.mu.Lock()
	defer dvs.mu.Unlock()
	
	dvs.Voters[voter.ID] = voter
}

func (dvs *DistributedVotingSystem) CastVote(voterID string, choice VoteChoice, constituency string) error {
	dvs.mu.Lock()
	defer dvs.mu.Unlock()
	
	voter, exists := dvs.Voters[voterID]
	if !exists {
		return fmt.Errorf("voter %s not registered", voterID)
	}
	
	if voter.HasVoted {
		return fmt.Errorf("voter %s has already voted", voterID)
	}
	
	if voter.Status != ELIGIBLE {
		return fmt.Errorf("voter %s is not eligible", voterID)
	}
	
	// Create vote
	vote := &Vote{
		VoterID:      voterID,
		Choice:       choice,
		Constituency: constituency,
		Timestamp:    time.Now(),
	}
	vote.Hash = calculateVoteHash(vote)
	vote.Signature = dvs.generateSignature(vote)
	
	// Process vote through consensus
	success := dvs.processVoteWithConsensus(vote)
	if !success {
		dvs.FraudAttempts++
		return fmt.Errorf("vote rejected by consensus mechanism")
	}
	
	// Mark voter as voted
	voter.HasVoted = true
	voter.VoteHash = vote.Hash
	voter.Timestamp = vote.Timestamp
	
	dvs.TotalVotes++
	
	fmt.Printf("🗳️  Vote cast by voter %s for %s in %s\n", 
		voterID, string(choice), constituency)
	
	return nil
}

func (dvs *DistributedVotingSystem) generateSignature(vote *Vote) string {
	// Simplified digital signature
	data := vote.Hash + "election_authority_mumbai"
	hash := sha256.Sum256([]byte(data))
	return hex.EncodeToString(hash[:])[:12]
}

func (dvs *DistributedVotingSystem) processVoteWithConsensus(vote *Vote) bool {
	// Find nodes managing this constituency
	var managingNodes []*ElectionNode
	
	for _, node := range dvs.Nodes {
		if _, manages := node.Constituencies[vote.Constituency]; manages && node.IsOperational() {
			managingNodes = append(managingNodes, node)
		}
	}
	
	if len(managingNodes) == 0 {
		fmt.Printf("❌ No operational nodes for constituency %s\n", vote.Constituency)
		return false
	}
	
	fmt.Printf("   🔍 Processing vote through %d nodes\n", len(managingNodes))
	
	// Process vote in parallel across nodes
	var wg sync.WaitGroup
	validations := make(chan bool, len(managingNodes))
	
	for _, node := range managingNodes {
		wg.Add(1)
		go func(n *ElectionNode) {
			defer wg.Done()
			
			err := n.ProcessVote(vote)
			validations <- err == nil
			
			if err != nil {
				fmt.Printf("   ❌ Node %s rejected vote: %v\n", n.Name, err)
			}
		}(node)
	}
	
	wg.Wait()
	close(validations)
	
	// Count validations
	successCount := 0
	totalValidations := 0
	
	for valid := range validations {
		totalValidations++
		if valid {
			successCount++
		}
	}
	
	dvs.TotalValidations += totalValidations
	
	// Check consensus
	consensusRate := float64(successCount) / float64(totalValidations)
	consensusReached := consensusRate >= dvs.ConsensusThreshold
	
	fmt.Printf("   📊 Consensus: %.1f%% (%d/%d) - %s\n", 
		consensusRate*100, successCount, totalValidations,
		map[bool]string{true: "✅ ACCEPTED", false: "❌ REJECTED"}[consensusReached])
	
	return consensusReached
}

func (dvs *DistributedVotingSystem) CountVotes(constituencyID string) map[VoteChoice]int {
	dvs.mu.RLock()
	defer dvs.mu.RUnlock()
	
	constituency, exists := dvs.Constituencies[constituencyID]
	if !exists {
		return nil
	}
	
	counts := make(map[VoteChoice]int)
	
	// Initialize counts
	for _, candidate := range constituency.Candidates {
		counts[VoteChoice(candidate.ID)] = 0
	}
	counts[NOTA] = 0
	
	// Count votes from all managing nodes
	uniqueVotes := make(map[string]bool) // Prevent double counting
	
	for _, node := range dvs.Nodes {
		if nodeConstituency, manages := node.Constituencies[constituencyID]; manages {
			for _, vote := range nodeConstituency.Votes {
				if !uniqueVotes[vote.Hash] {
					counts[vote.Choice]++
					uniqueVotes[vote.Hash] = true
				}
			}
		}
	}
	
	return counts
}

func (dvs *DistributedVotingSystem) GenerateElectionReport() map[string]interface{} {
	dvs.mu.RLock()
	defer dvs.mu.RUnlock()
	
	duration := time.Since(dvs.StartTime)
	
	// Calculate system-wide statistics
	systemStats := map[string]interface{}{
		"totalNodes":           len(dvs.Nodes),
		"totalConstituencies":  len(dvs.Constituencies),
		"totalRegisteredVoters": len(dvs.Voters),
		"totalVotesCast":       dvs.TotalVotes,
		"totalValidations":     dvs.TotalValidations,
		"fraudAttempts":        dvs.FraudAttempts,
		"electionDuration":     duration.String(),
		"consensusThreshold":   dvs.ConsensusThreshold,
	}
	
	// Node performance
	nodeStats := make([]map[string]interface{}, 0)
	totalFraud := 0
	totalProcessed := 0
	
	for _, node := range dvs.Nodes {
		stats := map[string]interface{}{
			"nodeID":         node.ID,
			"nodeName":       node.Name,
			"region":         node.Region,
			"reliability":    node.Reliability,
			"votesProcessed": node.VotesProcessed,
			"validationsDone": node.ValidationsDone,
			"fraudDetected":  node.FraudDetected,
			"operational":    node.IsOperational(),
		}
		
		nodeStats = append(nodeStats, stats)
		totalFraud += node.FraudDetected
		totalProcessed += node.VotesProcessed
	}
	
	// Constituency results
	constituencyResults := make(map[string]interface{})
	
	for id, constituency := range dvs.Constituencies {
		voteCounts := dvs.CountVotes(id)
		
		// Calculate turnout
		turnout := float64(constituency.VotesCast) / float64(constituency.TotalVoters) * 100
		
		constituencyResults[id] = map[string]interface{}{
			"name":       constituency.Name,
			"totalVoters": constituency.TotalVoters,
			"votesCast":  constituency.VotesCast,
			"turnout":    turnout,
			"results":    voteCounts,
		}
	}
	
	return map[string]interface{}{
		"systemStats":         systemStats,
		"nodePerformance":     nodeStats,
		"constituencyResults": constituencyResults,
		"securityMetrics": map[string]interface{}{
			"fraudDetectionRate": float64(totalFraud) / float64(totalProcessed) * 100,
			"consensusEfficiency": float64(dvs.TotalValidations) / float64(dvs.TotalVotes),
		},
	}
}

// Mumbai Election Simulation
func simulateMumbaiElection() {
	fmt.Println("🌆 MUMBAI DISTRIBUTED ELECTION SIMULATION")
	fmt.Println("Mumbai Election Commission - Digital Voting System")
	fmt.Println("=" + repeatString("=", 60))
	
	// Create distributed voting system
	votingSystem := NewDistributedVotingSystem(0.67) // 67% consensus threshold
	
	// Create Mumbai election nodes
	mumbaiNodes := []*ElectionNode{
		NewElectionNode("MEC001", "South Mumbai Center", "South"),
		NewElectionNode("MEC002", "Central Mumbai Center", "Central"),
		NewElectionNode("MEC003", "Western Suburbs Center", "Western"),
		NewElectionNode("MEC004", "Eastern Suburbs Center", "Eastern"),
		NewElectionNode("MEC005", "Thane Division Center", "Thane"),
	}
	
	for _, node := range mumbaiNodes {
		votingSystem.AddElectionNode(node)
	}
	
	// Create Mumbai constituencies
	constituencies := []*Constituency{
		{
			ID: "CONST001", Name: "Mumbai North", TotalVoters: 500000,
			Candidates: []*Candidate{
				{ID: "candidate_a", Name: "Rajesh Sharma", Party: "Party A"},
				{ID: "candidate_b", Name: "Priya Patel", Party: "Party B"},
				{ID: "candidate_c", Name: "Amit Gupta", Party: "Party C"},
			},
			Phase: REGISTRATION, ConsensusThreshold: 0.67,
		},
		{
			ID: "CONST002", Name: "Mumbai South", TotalVoters: 450000,
			Candidates: []*Candidate{
				{ID: "candidate_a", Name: "Sunita Khan", Party: "Party A"},
				{ID: "candidate_b", Name: "Vikram Iyer", Party: "Party B"},
				{ID: "candidate_c", Name: "Deepika Rao", Party: "Party C"},
			},
			Phase: REGISTRATION, ConsensusThreshold: 0.67,
		},
		{
			ID: "CONST003", Name: "Mumbai Central", TotalVoters: 400000,
			Candidates: []*Candidate{
				{ID: "candidate_a", Name: "Kiran Joshi", Party: "Party A"},
				{ID: "candidate_b", Name: "Meera Singh", Party: "Party B"},
				{ID: "candidate_c", Name: "Arjun Mehta", Party: "Party C"},
			},
			Phase: REGISTRATION, ConsensusThreshold: 0.67,
		},
	}
	
	for _, constituency := range constituencies {
		votingSystem.RegisterConstituency(constituency)
	}
	
	// Register voters
	fmt.Printf("\n👥 VOTER REGISTRATION PHASE\n")
	fmt.Println(repeatString("-", 40))
	
	totalVoters := 1000 // Simulate subset for demo
	voterNames := []string{"Sharma", "Patel", "Gupta", "Khan", "Singh", "Iyer", "Rao", "Mehta", "Joshi", "Desai"}
	
	for i := 0; i < totalVoters; i++ {
		voterID := fmt.Sprintf("VOTER%06d", i+1)
		name := voterNames[i%len(voterNames)] + fmt.Sprintf("_%d", i)
		constituency := constituencies[i%len(constituencies)].ID
		
		voter := &Voter{
			ID:           voterID,
			Name:         name,
			Constituency: constituency,
			Status:       ELIGIBLE,
			HasVoted:     false,
		}
		
		votingSystem.RegisterVoter(voter)
	}
	
	fmt.Printf("Registered %d voters across %d constituencies\n", totalVoters, len(constituencies))
	
	// Simulate voting phase
	fmt.Printf("\n🗳️ VOTING PHASE\n")
	fmt.Println(repeatString("-", 40))
	
	// Change phase to voting
	for _, constituency := range constituencies {
		constituency.Phase = VOTING
	}
	
	choices := []VoteChoice{CANDIDATE_A, CANDIDATE_B, CANDIDATE_C, NOTA}
	votesSimulated := 0
	maxVotes := 500 // Limit for demo
	
	for voterID, voter := range votingSystem.Voters {
		if votesSimulated >= maxVotes {
			break
		}
		
		if voter.Status == ELIGIBLE && !voter.HasVoted {
			// Simulate voting behavior - weighted random choice
			randChoice, _ := rand.Int(rand.Reader, big.NewInt(100))
			choiceIndex := 0
			
			// Weighted distribution: 40%, 30%, 20%, 10%
			choice_val := randChoice.Int64()
			if choice_val < 40 {
				choiceIndex = 0
			} else if choice_val < 70 {
				choiceIndex = 1
			} else if choice_val < 90 {
				choiceIndex = 2
			} else {
				choiceIndex = 3
			}
			
			choice := choices[choiceIndex]
			
			err := votingSystem.CastVote(voterID, choice, voter.Constituency)
			if err != nil {
				fmt.Printf("❌ Vote failed for %s: %v\n", voterID, err)
			} else {
				votesSimulated++
			}
			
			// Add some delay to simulate real voting pace
			if votesSimulated%50 == 0 {
				time.Sleep(time.Millisecond * 100)
				fmt.Printf("   📊 Votes processed so far: %d\n", votesSimulated)
			}
		}
	}
	
	fmt.Printf("Voting simulation completed: %d votes cast\n", votesSimulated)
	
	// Counting phase
	fmt.Printf("\n🔢 COUNTING PHASE\n")
	fmt.Println(repeatString("-", 40))
	
	for _, constituency := range constituencies {
		constituency.Phase = COUNTING
		
		counts := votingSystem.CountVotes(constituency.ID)
		total := 0
		for _, count := range counts {
			total += count
		}
		
		fmt.Printf("\n📊 Results for %s:\n", constituency.Name)
		fmt.Printf("Total votes: %d\n", total)
		
		// Sort results
		type result struct {
			choice VoteChoice
			count  int
		}
		
		var results []result
		for choice, count := range counts {
			results = append(results, result{choice, count})
		}
		
		sort.Slice(results, func(i, j int) bool {
			return results[i].count > results[j].count
		})
		
		for i, r := range results {
			percentage := float64(r.count) / float64(total) * 100
			position := ""
			switch i {
			case 0:
				position = "🥇 WINNER"
			case 1:
				position = "🥈 2nd"
			case 2:
				position = "🥉 3rd"
			default:
				position = fmt.Sprintf("   %d", i+1)
			}
			
			candidateName := string(r.choice)
			if r.choice == NOTA {
				candidateName = "NOTA"
			}
			
			fmt.Printf("   %s: %s - %d votes (%.1f%%)\n", 
				position, candidateName, r.count, percentage)
		}
	}
	
	// Generate final report
	fmt.Printf("\n📋 FINAL ELECTION REPORT\n")
	fmt.Println("=" + repeatString("=", 40))
	
	report := votingSystem.GenerateElectionReport()
	systemStats := report["systemStats"].(map[string]interface{})
	
	fmt.Printf("Election completed successfully!\n")
	fmt.Printf("Duration: %s\n", systemStats["electionDuration"])
	fmt.Printf("Total votes cast: %d\n", systemStats["totalVotesCast"])
	fmt.Printf("Total validations: %d\n", systemStats["totalValidations"])
	fmt.Printf("Fraud attempts detected: %d\n", systemStats["fraudAttempts"])
	fmt.Printf("Consensus threshold: %.1f%%\n", systemStats["consensusThreshold"].(float64)*100)
	
	securityMetrics := report["securityMetrics"].(map[string]interface{})
	fmt.Printf("Security metrics:\n")
	fmt.Printf("  Fraud detection rate: %.3f%%\n", securityMetrics["fraudDetectionRate"])
	fmt.Printf("  Consensus efficiency: %.2f validations per vote\n", securityMetrics["consensusEfficiency"])
	
	fmt.Printf("\n🎯 Key Insights:\n")
	fmt.Println("• Distributed consensus ensures election integrity")
	fmt.Println("• Multiple nodes validate each vote independently")
	fmt.Println("• Fraud detection prevents manipulation")
	fmt.Println("• Like Mumbai elections - trust through transparency!")
	
	fmt.Printf("\n🎊 MUMBAI ELECTION SIMULATION COMPLETED!\n")
}

// Helper function to repeat strings
func repeatString(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}

func main() {
	fmt.Println("🚀 DISTRIBUTED VOTING SYSTEM")
	fmt.Println("Mumbai Election Commission Digital Democracy")
	fmt.Println("=" + repeatString("=", 60))
	
	simulateMumbaiElection()
}