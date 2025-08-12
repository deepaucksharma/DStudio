/*
Indian Election Consensus System - Episode 4
भारतीय चुनाव प्रणाली में distributed consensus का practical implementation

यह system demonstrate करता है कि कैसे Election Commission of India
distributed voting across states को coordinate करती है।

Real scenarios:
- EVM vote counting across constituencies
- State-wise result coordination
- Final tally consensus across Election Commission nodes
- Handling network partitions between states
- Ensuring no double voting or vote manipulation

CAP Trade-off: Strong Consistency + Partition Tolerance (CP System)
Election results की accuracy सबसे important है, availability sacrifice कर सकते हैं।
*/

package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"sync"
	"time"
)

// VoteType represents different types of votes in Indian elections
type VoteType int

const (
	LokSabha VoteType = iota // लोकसभा चुनाव
	VidhanSabha              // विधानसभा चुनाव
	LocalBody                // स्थानीय निकाय चुनाव
	PresidentialElection     // राष्ट्रपति चुनाव
)

func (vt VoteType) String() string {
	switch vt {
		case LokSabha: return "Lok Sabha"
		case VidhanSabha: return "Vidhan Sabha"
		case LocalBody: return "Local Body"
		case PresidentialElection: return "Presidential"
		default: return "Unknown"
	}
}

// NodeStatus represents the status of an Election Commission node
type NodeStatus int

const (
	NodeActive NodeStatus = iota
	NodeFailed
	NodePartitioned
	NodeRecovering
)

func (ns NodeStatus) String() string {
	switch ns {
		case NodeActive: return "ACTIVE"
		case NodeFailed: return "FAILED"
		case NodePartitioned: return "PARTITIONED"
		case NodeRecovering: return "RECOVERING"
		default: return "UNKNOWN"
	}
}

// Candidate represents an election candidate
type Candidate struct {
	ID       string `json:"id"`
	Name     string `json:"name"`
	Party    string `json:"party"`
	Symbol   string `json:"symbol"`
	State    string `json:"state"`
}

// Vote represents a single vote in the election
type Vote struct {
	VoterID      string    `json:"voter_id"`
	CandidateID  string    `json:"candidate_id"`
	Constituency string    `json:"constituency"`
	State        string    `json:"state"`
	VoteType     VoteType  `json:"vote_type"`
	Timestamp    time.Time `json:"timestamp"`
	EVMNumber    string    `json:"evm_number"`
	Checksum     string    `json:"checksum"`
}

// generateChecksum creates a SHA-256 checksum for vote integrity
func (v *Vote) generateChecksum() {
	data := fmt.Sprintf("%s-%s-%s-%s-%d-%s", 
		v.VoterID, v.CandidateID, v.Constituency, v.State, v.VoteType, v.EVMNumber)
	hash := sha256.Sum256([]byte(data))
	v.Checksum = fmt.Sprintf("%x", hash)[:16] // First 16 characters
}

// ElectionResult represents aggregated results for a constituency
type ElectionResult struct {
	Constituency string            `json:"constituency"`
	State        string            `json:"state"`
	VoteType     VoteType          `json:"vote_type"`
	CandidateVotes map[string]int  `json:"candidate_votes"` // candidate_id -> vote_count
	TotalVotes   int              `json:"total_votes"`
	Winner       string           `json:"winner"`
	Margin       int              `json:"margin"`
	TurnoutPercent float64        `json:"turnout_percent"`
	LastUpdated  time.Time        `json:"last_updated"`
}

// ElectionNode represents an Election Commission node (state/regional office)
type ElectionNode struct {
	NodeID        string                      `json:"node_id"`
	StateName     string                      `json:"state_name"`
	Status        NodeStatus                  `json:"status"`
	Votes         map[string]*Vote            `json:"votes"`          // vote_id -> Vote
	Results       map[string]*ElectionResult  `json:"results"`        // constituency -> Result
	Candidates    map[string]*Candidate       `json:"candidates"`     // candidate_id -> Candidate
	LastHeartbeat time.Time                   `json:"last_heartbeat"`
	
	// Consensus fields
	Term          int                         `json:"term"`           // Current election term
	CommittedIndex int                        `json:"committed_index"` // Last committed vote index
	Log           []*Vote                     `json:"log"`            // Vote log for consensus
	
	// Network simulation
	NetworkDelay  time.Duration               `json:"network_delay"`
	IsPartitioned bool                        `json:"is_partitioned"`
	
	mutex         sync.RWMutex
}

// NewElectionNode creates a new Election Commission node
func NewElectionNode(nodeID, stateName string) *ElectionNode {
	return &ElectionNode{
		NodeID:        nodeID,
		StateName:     stateName,
		Status:        NodeActive,
		Votes:         make(map[string]*Vote),
		Results:       make(map[string]*ElectionResult),
		Candidates:    make(map[string]*Candidate),
		LastHeartbeat: time.Now(),
		Term:          1,
		CommittedIndex: 0,
		Log:           make([]*Vote, 0),
		NetworkDelay:  100 * time.Millisecond, // Default network delay
		IsPartitioned: false,
	}
}

// AddCandidate adds a candidate to the node's registry
func (node *ElectionNode) AddCandidate(candidate *Candidate) {
	node.mutex.Lock()
	defer node.mutex.Unlock()
	
	node.Candidates[candidate.ID] = candidate
	fmt.Printf("📝 Node %s: Candidate registered - %s (%s) from %s\n", 
		node.NodeID, candidate.Name, candidate.Party, candidate.State)
}

// CastVote records a vote with integrity checks
func (node *ElectionNode) CastVote(vote *Vote) error {
	node.mutex.Lock()
	defer node.mutex.Unlock()
	
	// Simulate network delay
	time.Sleep(node.NetworkDelay)
	
	if node.Status != NodeActive {
		return fmt.Errorf("node %s is not active (status: %s)", node.NodeID, node.Status)
	}
	
	// Check for duplicate voting (based on VoterID + VoteType + Constituency)
	voteKey := fmt.Sprintf("%s-%s-%d", vote.VoterID, vote.Constituency, vote.VoteType)
	for _, existingVote := range node.Votes {
		existingKey := fmt.Sprintf("%s-%s-%d", existingVote.VoterID, existingVote.Constituency, existingVote.VoteType)
		if existingKey == voteKey {
			return fmt.Errorf("duplicate vote detected for voter %s in %s", vote.VoterID, vote.Constituency)
		}
	}
	
	// Validate candidate exists
	if _, exists := node.Candidates[vote.CandidateID]; !exists {
		return fmt.Errorf("candidate %s not found", vote.CandidateID)
	}
	
	// Generate vote checksum for integrity
	vote.generateChecksum()
	
	// Add vote to local storage
	voteID := fmt.Sprintf("%s-%d", vote.VoterID, time.Now().UnixNano())
	node.Votes[voteID] = vote
	
	// Add to consensus log
	node.Log = append(node.Log, vote)
	
	fmt.Printf("🗳️  Node %s: Vote cast by %s for %s in %s (EVM: %s)\n", 
		node.NodeID, vote.VoterID, node.Candidates[vote.CandidateID].Name, 
		vote.Constituency, vote.EVMNumber)
	
	return nil
}

// CalculateResults calculates election results for a constituency
func (node *ElectionNode) CalculateResults(constituency string, voteType VoteType) *ElectionResult {
	node.mutex.RLock()
	defer node.mutex.RUnlock()
	
	candidateVotes := make(map[string]int)
	totalVotes := 0
	
	// Count votes for this constituency
	for _, vote := range node.Votes {
		if vote.Constituency == constituency && vote.VoteType == voteType {
			candidateVotes[vote.CandidateID]++
			totalVotes++
		}
	}
	
	// Find winner
	winner := ""
	maxVotes := 0
	secondHighest := 0
	
	for candidateID, votes := range candidateVotes {
		if votes > maxVotes {
			secondHighest = maxVotes
			maxVotes = votes
			winner = candidateID
		} else if votes > secondHighest {
			secondHighest = votes
		}
	}
	
	margin := maxVotes - secondHighest
	
	// Simulate voter turnout percentage (in real system, this would be based on registered voters)
	turnoutPercent := float64(totalVotes) / 1000.0 * 100 // Assuming 1000 registered voters per constituency
	
	result := &ElectionResult{
		Constituency:   constituency,
		State:         node.StateName,
		VoteType:      voteType,
		CandidateVotes: candidateVotes,
		TotalVotes:    totalVotes,
		Winner:        winner,
		Margin:        margin,
		TurnoutPercent: turnoutPercent,
		LastUpdated:   time.Now(),
	}
	
	node.Results[constituency] = result
	
	if winner != "" && node.Candidates[winner] != nil {
		fmt.Printf("🏆 Node %s: %s leads in %s with %d votes (Margin: %d)\n", 
			node.NodeID, node.Candidates[winner].Name, constituency, maxVotes, margin)
	}
	
	return result
}

// IndianElectionConsensus manages distributed consensus across Election Commission nodes
type IndianElectionConsensus struct {
	Nodes         map[string]*ElectionNode  `json:"nodes"`
	CurrentTerm   int                       `json:"current_term"`
	LeaderID      string                   `json:"leader_id"`
	
	// Metrics
	TotalVotes         int `json:"total_votes"`
	SuccessfulVotes    int `json:"successful_votes"`
	FailedVotes        int `json:"failed_votes"`
	ConsensusRounds    int `json:"consensus_rounds"`
	PartitionEvents    int `json:"partition_events"`
	
	mutex sync.RWMutex
}

// NewIndianElectionConsensus creates a new Election Commission consensus system
func NewIndianElectionConsensus() *IndianElectionConsensus {
	return &IndianElectionConsensus{
		Nodes:       make(map[string]*ElectionNode),
		CurrentTerm: 1,
		LeaderID:    "",
	}
}

// AddNode adds an Election Commission node to the system
func (ec *IndianElectionConsensus) AddNode(nodeID, stateName string) {
	ec.mutex.Lock()
	defer ec.mutex.Unlock()
	
	node := NewElectionNode(nodeID, stateName)
	ec.Nodes[nodeID] = node
	
	fmt.Printf("🏛️  Election Commission node added: %s (%s)\n", nodeID, stateName)
	
	// If this is the first node, make it the leader
	if ec.LeaderID == "" {
		ec.LeaderID = nodeID
		fmt.Printf("👑 Node %s elected as leader\n", nodeID)
	}
}

// AddCandidateToAllNodes adds a candidate to all active nodes
func (ec *IndianElectionConsensus) AddCandidateToAllNodes(candidate *Candidate) {
	ec.mutex.RLock()
	defer ec.mutex.RUnlock()
	
	for _, node := range ec.Nodes {
		if node.Status == NodeActive && !node.IsPartitioned {
			node.AddCandidate(candidate)
		}
	}
}

// DistributedVoteCast handles distributed vote casting with consensus
func (ec *IndianElectionConsensus) DistributedVoteCast(vote *Vote) error {
	ec.mutex.Lock()
	defer ec.mutex.Unlock()
	
	ec.TotalVotes++
	
	fmt.Printf("\n🗳️  DISTRIBUTED VOTE CASTING\n")
	fmt.Printf("   Voter: %s\n", vote.VoterID)
	fmt.Printf("   Constituency: %s\n", vote.Constituency)
	fmt.Printf("   State: %s\n", vote.State)
	fmt.Printf("   Vote Type: %s\n", vote.VoteType)
	
	// Phase 1: Prepare - Check if majority of nodes can accept the vote
	activeNodes := ec.getActiveNodes()
	if len(activeNodes) == 0 {
		ec.FailedVotes++
		return fmt.Errorf("no active nodes available")
	}
	
	requiredNodes := len(activeNodes)/2 + 1 // Majority
	preparedNodes := make([]*ElectionNode, 0)
	
	fmt.Printf("   Phase 1: Preparing vote across %d nodes (need %d for majority)...\n", 
		len(activeNodes), requiredNodes)
	
	for _, node := range activeNodes {
		// Simulate preparation check
		if ec.canNodeAcceptVote(node, vote) {
			preparedNodes = append(preparedNodes, node)
			fmt.Printf("   ✅ Node %s prepared\n", node.NodeID)
		} else {
			fmt.Printf("   ❌ Node %s preparation failed\n", node.NodeID)
		}
	}
	
	if len(preparedNodes) < requiredNodes {
		ec.FailedVotes++
		return fmt.Errorf("insufficient nodes prepared (%d/%d)", len(preparedNodes), requiredNodes)
	}
	
	// Phase 2: Commit - Actually cast the vote on prepared nodes
	fmt.Printf("   Phase 2: Committing vote to %d prepared nodes...\n", len(preparedNodes))
	
	successfulCommits := 0
	for _, node := range preparedNodes {
		if err := node.CastVote(vote); err != nil {
			fmt.Printf("   ❌ Commit failed on node %s: %v\n", node.NodeID, err)
		} else {
			successfulCommits++
			fmt.Printf("   ✅ Vote committed on node %s\n", node.NodeID)
		}
	}
	
	if successfulCommits >= requiredNodes {
		ec.SuccessfulVotes++
		ec.ConsensusRounds++
		
		// Async replication to remaining nodes
		go ec.replicateVoteToRemainingNodes(vote, preparedNodes)
		
		fmt.Printf("   ✅ VOTE SUCCESSFULLY COMMITTED (%d/%d nodes)\n", 
			successfulCommits, len(preparedNodes))
		return nil
	} else {
		ec.FailedVotes++
		return fmt.Errorf("insufficient commits (%d/%d)", successfulCommits, requiredNodes)
	}
}

// canNodeAcceptVote checks if a node can accept a vote (preparation phase)
func (ec *IndianElectionConsensus) canNodeAcceptVote(node *ElectionNode, vote *Vote) bool {
	if node.Status != NodeActive || node.IsPartitioned {
		return false
	}
	
	// Check for duplicate vote
	voteKey := fmt.Sprintf("%s-%s-%d", vote.VoterID, vote.Constituency, vote.VoteType)
	for _, existingVote := range node.Votes {
		existingKey := fmt.Sprintf("%s-%s-%d", existingVote.VoterID, existingVote.Constituency, existingVote.VoteType)
		if existingKey == voteKey {
			return false // Duplicate vote
		}
	}
	
	// Check if candidate exists
	if _, exists := node.Candidates[vote.CandidateID]; !exists {
		return false
	}
	
	return true
}

// getActiveNodes returns all active, non-partitioned nodes
func (ec *IndianElectionConsensus) getActiveNodes() []*ElectionNode {
	activeNodes := make([]*ElectionNode, 0)
	for _, node := range ec.Nodes {
		if node.Status == NodeActive && !node.IsPartitioned {
			activeNodes = append(activeNodes, node)
		}
	}
	return activeNodes
}

// replicateVoteToRemainingNodes asynchronously replicates vote to other nodes
func (ec *IndianElectionConsensus) replicateVoteToRemainingNodes(vote *Vote, alreadyCommitted []*ElectionNode) {
	committedIDs := make(map[string]bool)
	for _, node := range alreadyCommitted {
		committedIDs[node.NodeID] = true
	}
	
	for _, node := range ec.Nodes {
		if !committedIDs[node.NodeID] && node.Status == NodeActive && !node.IsPartitioned {
			go func(n *ElectionNode) {
				time.Sleep(time.Duration(rand.Intn(1000)) * time.Millisecond) // Random delay
				if err := n.CastVote(vote); err == nil {
					fmt.Printf("   🔄 Vote replicated to node %s\n", n.NodeID)
				}
			}(node)
		}
	}
}

// CalculateNationalResults aggregates results across all nodes
func (ec *IndianElectionConsensus) CalculateNationalResults(voteType VoteType) map[string]*ElectionResult {
	ec.mutex.RLock()
	defer ec.mutex.RUnlock()
	
	fmt.Printf("\n🏛️  CALCULATING NATIONAL RESULTS FOR %s ELECTION\n", voteType)
	
	nationalResults := make(map[string]*ElectionResult)
	
	// Get unique constituencies across all nodes
	constituencies := make(map[string]bool)
	for _, node := range ec.Nodes {
		if node.Status == NodeActive {
			for _, vote := range node.Votes {
				if vote.VoteType == voteType {
					constituencies[vote.Constituency] = true
				}
			}
		}
	}
	
	// Calculate consensus results for each constituency
	for constituency := range constituencies {
		result := ec.calculateConsensusResult(constituency, voteType)
		if result != nil {
			nationalResults[constituency] = result
		}
	}
	
	fmt.Printf("   📊 National results calculated for %d constituencies\n", len(nationalResults))
	return nationalResults
}

// calculateConsensusResult calculates consensus result for a constituency
func (ec *IndianElectionConsensus) calculateConsensusResult(constituency string, voteType VoteType) *ElectionResult {
	candidateVotes := make(map[string]int)
	totalVotes := 0
	nodeCount := 0
	
	// Aggregate votes from all active nodes
	for _, node := range ec.Nodes {
		if node.Status == NodeActive && !node.IsPartitioned {
			nodeCount++
			for _, vote := range node.Votes {
				if vote.Constituency == constituency && vote.VoteType == voteType {
					candidateVotes[vote.CandidateID]++
					totalVotes++
				}
			}
		}
	}
	
	if totalVotes == 0 {
		return nil
	}
	
	// Find winner
	winner := ""
	maxVotes := 0
	secondHighest := 0
	
	for candidateID, votes := range candidateVotes {
		if votes > maxVotes {
			secondHighest = maxVotes
			maxVotes = votes
			winner = candidateID
		} else if votes > secondHighest {
			secondHighest = votes
		}
	}
	
	// Get candidate info from any active node
	var winnerCandidate *Candidate
	for _, node := range ec.Nodes {
		if node.Status == NodeActive && !node.IsPartitioned {
			if candidate, exists := node.Candidates[winner]; exists {
				winnerCandidate = candidate
				break
			}
		}
	}
	
	margin := maxVotes - secondHighest
	turnoutPercent := float64(totalVotes) / 1000.0 * 100 // Simplified calculation
	
	result := &ElectionResult{
		Constituency:   constituency,
		VoteType:      voteType,
		CandidateVotes: candidateVotes,
		TotalVotes:    totalVotes,
		Winner:        winner,
		Margin:        margin,
		TurnoutPercent: turnoutPercent,
		LastUpdated:   time.Now(),
	}
	
	if winnerCandidate != nil {
		fmt.Printf("   🏆 %s: %s (%s) - %d votes (Margin: %d)\n", 
			constituency, winnerCandidate.Name, winnerCandidate.Party, maxVotes, margin)
	}
	
	return result
}

// SimulateNetworkPartition simulates network partition between states
func (ec *IndianElectionConsensus) SimulateNetworkPartition(nodeID string, duration time.Duration) {
	ec.mutex.Lock()
	node, exists := ec.Nodes[nodeID]
	if !exists {
		ec.mutex.Unlock()
		return
	}
	
	ec.PartitionEvents++
	node.IsPartitioned = true
	node.Status = NodePartitioned
	ec.mutex.Unlock()
	
	fmt.Printf("\n🌐 NETWORK PARTITION SIMULATION\n")
	fmt.Printf("   Node %s (%s) partitioned for %v\n", nodeID, node.StateName, duration)
	
	// Test voting during partition
	fmt.Printf("   Testing vote casting during partition...\n")
	
	testVote := &Vote{
		VoterID:      fmt.Sprintf("VOTER_PARTITION_%d", time.Now().Unix()),
		CandidateID:  "CAND001", // Assuming this candidate exists
		Constituency: "TEST_CONSTITUENCY",
		State:        node.StateName,
		VoteType:     LokSabha,
		Timestamp:    time.Now(),
		EVMNumber:    "EVM12345",
	}
	
	err := ec.DistributedVoteCast(testVote)
	if err != nil {
		fmt.Printf("   ❌ Vote failed during partition (expected): %v\n", err)
	} else {
		fmt.Printf("   ✅ Vote succeeded despite partition\n")
	}
	
	// Recover after duration
	go func() {
		time.Sleep(duration)
		
		ec.mutex.Lock()
		node.IsPartitioned = false
		node.Status = NodeRecovering
		ec.mutex.Unlock()
		
		fmt.Printf("   🔄 Node %s recovering from partition...\n", nodeID)
		
		time.Sleep(2 * time.Second) // Recovery time
		
		ec.mutex.Lock()
		node.Status = NodeActive
		ec.mutex.Unlock()
		
		fmt.Printf("   ✅ Node %s fully recovered\n", nodeID)
	}()
}

// SimulateElectionDay simulates a full election day with concurrent voting
func (ec *IndianElectionConsensus) SimulateElectionDay(numVoters int, constituencies []string) {
	fmt.Printf("\n🗳️  ELECTION DAY SIMULATION\n")
	fmt.Printf("   Voters: %d\n", numVoters)
	fmt.Printf("   Constituencies: %v\n", constituencies)
	fmt.Printf("   Starting concurrent voting...\n")
	
	startTime := time.Now()
	
	// Create a wait group to track all votes
	var wg sync.WaitGroup
	
	// Simulate concurrent voting
	for i := 0; i < numVoters; i++ {
		wg.Add(1)
		
		go func(voterNum int) {
			defer wg.Done()
			
			// Random delay to simulate voters arriving at different times
			time.Sleep(time.Duration(rand.Intn(1000)) * time.Millisecond)
			
			// Create a vote
			constituency := constituencies[rand.Intn(len(constituencies))]
			candidateID := fmt.Sprintf("CAND%03d", rand.Intn(5)+1) // 5 candidates
			
			vote := &Vote{
				VoterID:      fmt.Sprintf("VOTER%06d", voterNum+1),
				CandidateID:  candidateID,
				Constituency: constituency,
				State:        "TEST_STATE",
				VoteType:     LokSabha,
				Timestamp:    time.Now(),
				EVMNumber:    fmt.Sprintf("EVM%03d", rand.Intn(100)+1),
			}
			
			// Cast the vote
			err := ec.DistributedVoteCast(vote)
			if err != nil {
				fmt.Printf("❌ Vote failed for voter %s: %v\n", vote.VoterID, err)
			}
			
		}(i)
		
		// Small delay between vote submissions to avoid overwhelming the system
		time.Sleep(10 * time.Millisecond)
	}
	
	// Wait for all votes to complete
	wg.Wait()
	
	duration := time.Since(startTime)
	
	fmt.Printf("\n📊 ELECTION DAY RESULTS\n")
	fmt.Printf("   Duration: %v\n", duration)
	fmt.Printf("   Total votes attempted: %d\n", ec.TotalVotes)
	fmt.Printf("   Successful votes: %d\n", ec.SuccessfulVotes)
	fmt.Printf("   Failed votes: %d\n", ec.FailedVotes)
	fmt.Printf("   Success rate: %.2f%%\n", float64(ec.SuccessfulVotes)/float64(ec.TotalVotes)*100)
	fmt.Printf("   Consensus rounds: %d\n", ec.ConsensusRounds)
	fmt.Printf("   Average time per vote: %v\n", duration/time.Duration(numVoters))
}

// PrintSystemStatus prints the current status of all nodes
func (ec *IndianElectionConsensus) PrintSystemStatus() {
	ec.mutex.RLock()
	defer ec.mutex.RUnlock()
	
	fmt.Printf("\n🏛️  ELECTION COMMISSION SYSTEM STATUS\n")
	fmt.Printf("   Current Term: %d\n", ec.CurrentTerm)
	fmt.Printf("   Leader Node: %s\n", ec.LeaderID)
	fmt.Printf("   Total Nodes: %d\n", len(ec.Nodes))
	
	activeNodes := 0
	for _, node := range ec.Nodes {
		fmt.Printf("   Node %s (%s): %s", node.NodeID, node.StateName, node.Status)
		if node.IsPartitioned {
			fmt.Printf(" [PARTITIONED]")
		}
		fmt.Printf(" - Votes: %d\n", len(node.Votes))
		
		if node.Status == NodeActive && !node.IsPartitioned {
			activeNodes++
		}
	}
	
	fmt.Printf("   Active Nodes: %d/%d\n", activeNodes, len(ec.Nodes))
	fmt.Printf("   System Health: ")
	
	if activeNodes > len(ec.Nodes)/2 {
		fmt.Printf("HEALTHY (Consensus possible)\n")
	} else {
		fmt.Printf("CRITICAL (Consensus not possible)\n")
	}
}

// Main demonstration function
func main() {
	fmt.Println("🇮🇳 INDIAN ELECTION CONSENSUS SYSTEM DEMO")
	fmt.Println(strings.Repeat("=", 60))
	
	// Initialize Election Commission consensus system
	ec := NewIndianElectionConsensus()
	
	// Add Election Commission nodes for major states
	ec.AddNode("EC_MAHARASHTRA", "Maharashtra")
	ec.AddNode("EC_UTTAR_PRADESH", "Uttar Pradesh")
	ec.AddNode("EC_WEST_BENGAL", "West Bengal")
	ec.AddNode("EC_TAMIL_NADU", "Tamil Nadu")
	ec.AddNode("EC_KARNATAKA", "Karnataka")
	
	// Add sample candidates
	candidates := []*Candidate{
		{"CAND001", "राहुल गांधी", "Indian National Congress", "Hand", "UP"},
		{"CAND002", "नरेंद्र मोदी", "Bharatiya Janata Party", "Lotus", "Gujarat"},
		{"CAND003", "अरविंद केजरीवाल", "Aam Aadmi Party", "Broom", "Delhi"},
		{"CAND004", "ममता बैनर्जी", "All India Trinamool Congress", "Flowers and Grass", "West Bengal"},
		{"CAND005", "उद्धव ठाकरे", "Shiv Sena (UBT)", "Flaming Torch", "Maharashtra"},
	}
	
	fmt.Printf("\n📝 REGISTERING CANDIDATES\n")
	for _, candidate := range candidates {
		ec.AddCandidateToAllNodes(candidate)
	}
	
	// Scenario 1: Normal voting process
	fmt.Printf("\n🗳️  SCENARIO 1: Normal Voting Process\n")
	
	normalVotes := []*Vote{
		{
			VoterID:      "VOTER000001",
			CandidateID:  "CAND001",
			Constituency: "AMETHI",
			State:        "Uttar Pradesh",
			VoteType:     LokSabha,
			Timestamp:    time.Now(),
			EVMNumber:    "EVM001",
		},
		{
			VoterID:      "VOTER000002",
			CandidateID:  "CAND002",
			Constituency: "VARANASI",
			State:        "Uttar Pradesh",
			VoteType:     LokSabha,
			Timestamp:    time.Now(),
			EVMNumber:    "EVM002",
		},
		{
			VoterID:      "VOTER000003",
			CandidateID:  "CAND003",
			Constituency: "NEW_DELHI",
			State:        "Delhi",
			VoteType:     LokSabha,
			Timestamp:    time.Now(),
			EVMNumber:    "EVM003",
		},
	}
	
	for _, vote := range normalVotes {
		err := ec.DistributedVoteCast(vote)
		if err != nil {
			fmt.Printf("❌ Vote casting failed: %v\n", err)
		}
	}
	
	// Scenario 2: Network partition simulation
	fmt.Printf("\n🌐 SCENARIO 2: Network Partition Simulation\n")
	ec.SimulateNetworkPartition("EC_MAHARASHTRA", 5*time.Second)
	time.Sleep(6 * time.Second) // Wait for partition to resolve
	
	// Scenario 3: Election day simulation
	fmt.Printf("\n🗳️  SCENARIO 3: Election Day Simulation\n")
	constituencies := []string{"AMETHI", "VARANASI", "NEW_DELHI", "MUMBAI_NORTH", "KOLKATA_SOUTH"}
	ec.SimulateElectionDay(25, constituencies) // 25 voters for demo
	
	// Scenario 4: Calculate national results
	fmt.Printf("\n🏆 SCENARIO 4: National Results Calculation\n")
	nationalResults := ec.CalculateNationalResults(LokSabha)
	
	fmt.Printf("\n🎯 FINAL ELECTION RESULTS\n")
	for constituency, result := range nationalResults {
		if result.Winner != "" {
			// Find winner candidate name
			var winnerName string
			for _, candidate := range candidates {
				if candidate.ID == result.Winner {
					winnerName = candidate.Name
					break
				}
			}
			fmt.Printf("   %s: %s wins with %d votes (Turnout: %.1f%%)\n", 
				constituency, winnerName, result.CandidateVotes[result.Winner], result.TurnoutPercent)
		}
	}
	
	// Final system status
	ec.PrintSystemStatus()
	
	fmt.Printf("\n✅ Indian Election Consensus System demo completed!\n")
	fmt.Printf("Key learnings:\n")
	fmt.Printf("1. Election systems require strong consistency (no double voting)\n")
	fmt.Printf("2. Distributed consensus ensures accurate vote counting\n")
	fmt.Printf("3. Network partitions are handled gracefully with majority rule\n")
	fmt.Printf("4. Two-phase commit ensures vote integrity across states\n")
	fmt.Printf("5. Real-time result aggregation requires coordination\n")
	fmt.Printf("6. CAP theorem: Consistency + Partition tolerance > Availability\n")
}

// Helper function since strings.Repeat might not be available
func strings.Repeat(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}