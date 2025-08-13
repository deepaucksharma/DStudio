/*
Consensus Protocol Simulator
============================

Mumbai Traffic Signal Coordination Style!
Just like Mumbai traffic signals need consensus to manage flow,
distributed systems need consensus protocols for coordination.

This simulator implements and compares different consensus algorithms.

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
*/

package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"strconv"
	"sync"
	"time"
)

// Consensus algorithm types
type ConsensusType string

const (
	RAFT_CONSENSUS     ConsensusType = "raft"
	PBFT_CONSENSUS     ConsensusType = "pbft"
	POW_CONSENSUS      ConsensusType = "pow"
	POS_CONSENSUS      ConsensusType = "pos"
	MAJORITY_CONSENSUS ConsensusType = "majority"
)

// Node states
type NodeState string

const (
	FOLLOWER  NodeState = "follower"
	CANDIDATE NodeState = "candidate"
	LEADER    NodeState = "leader"
	INACTIVE  NodeState = "inactive"
	BYZANTINE NodeState = "byzantine"
)

// Message types for consensus protocols
type MessageType string

const (
	REQUEST_VOTE MessageType = "request_vote"
	VOTE         MessageType = "vote"
	HEARTBEAT    MessageType = "heartbeat"
	APPEND_LOG   MessageType = "append_log"
	PREPARE      MessageType = "prepare"
	COMMIT       MessageType = "commit"
)

// Core structures
type Node struct {
	ID           string
	State        NodeState
	Term         int
	VotedFor     string
	Log          []LogEntry
	CommitIndex  int
	LastApplied  int
	Reliability  float64 // Mumbai node characteristic: how reliable is this node
	ResponseTime time.Duration
	
	// Performance metrics
	MessagesReceived int
	MessagesSent     int
	VotesCast        int
	Leadership       int // Times this node was leader
	
	// Mumbai characteristics
	TrafficLoad float64 // How much traffic this node handles (0.0-1.0)
	PowerStable bool    // Mumbai power situation
}

type LogEntry struct {
	Term    int
	Index   int
	Command string
	Data    map[string]interface{}
	Hash    string
}

type Message struct {
	ID        string
	Type      MessageType
	Sender    string
	Receiver  string
	Term      int
	Data      map[string]interface{}
	Timestamp time.Time
}

type ConsensusResult struct {
	Success           bool
	Leader            string
	Term              int
	CommittedEntries  int
	Duration          time.Duration
	MessagesExchanged int
	ParticipantCount  int
	Details           map[string]interface{}
}

// Mumbai Traffic Node - represents a traffic signal controller
func NewMumbaiTrafficNode(id string) *Node {
	return &Node{
		ID:           id,
		State:        FOLLOWER,
		Term:         0,
		VotedFor:     "",
		Log:          make([]LogEntry, 0),
		CommitIndex:  0,
		LastApplied:  0,
		Reliability:  0.8 + rand.Float64()*0.19, // 80-99% reliability
		ResponseTime: time.Duration(100+rand.Intn(400)) * time.Millisecond,
		TrafficLoad:  rand.Float64(),
		PowerStable:  rand.Float64() > 0.1, // 90% power stability
		
		MessagesReceived: 0,
		MessagesSent:     0,
		VotesCast:        0,
		Leadership:       0,
	}
}

func (n *Node) IsActive() bool {
	return n.State != INACTIVE && n.PowerStable
}

func (n *Node) ProcessMessage(msg *Message) error {
	n.MessagesReceived++
	
	// Simulate Mumbai network delays and reliability
	time.Sleep(n.ResponseTime)
	
	if rand.Float64() > n.Reliability {
		return fmt.Errorf("message processing failed - Mumbai network issue")
	}
	
	fmt.Printf("   📨 %s received %s from %s (term: %d)\n", 
		n.ID, msg.Type, msg.Sender, msg.Term)
	
	switch msg.Type {
	case REQUEST_VOTE:
		return n.handleVoteRequest(msg)
	case VOTE:
		return n.handleVote(msg)
	case HEARTBEAT:
		return n.handleHeartbeat(msg)
	case APPEND_LOG:
		return n.handleAppendLog(msg)
	default:
		return fmt.Errorf("unknown message type: %s", msg.Type)
	}
}

func (n *Node) handleVoteRequest(msg *Message) error {
	candidateID := msg.Sender
	candidateTerm, _ := msg.Data["term"].(int)
	
	// Vote if we haven't voted in this term and candidate is qualified
	if candidateTerm >= n.Term && (n.VotedFor == "" || n.VotedFor == candidateID) {
		n.VotedFor = candidateID
		n.Term = candidateTerm
		n.VotesCast++
		
		fmt.Printf("   🗳️  %s votes for %s in term %d\n", n.ID, candidateID, candidateTerm)
		return nil
	}
	
	fmt.Printf("   ❌ %s rejects vote for %s (already voted for %s)\n", 
		n.ID, candidateID, n.VotedFor)
	return nil
}

func (n *Node) handleVote(msg *Message) error {
	// Leaders don't process votes
	if n.State != CANDIDATE {
		return nil
	}
	
	// Process vote (implementation would count votes)
	fmt.Printf("   ✅ %s received vote from %s\n", n.ID, msg.Sender)
	return nil
}

func (n *Node) handleHeartbeat(msg *Message) error {
	leaderTerm, _ := msg.Data["term"].(int)
	
	if leaderTerm >= n.Term {
		n.State = FOLLOWER
		n.Term = leaderTerm
		fmt.Printf("   💓 %s acknowledges leader %s (term %d)\n", 
			n.ID, msg.Sender, leaderTerm)
	}
	
	return nil
}

func (n *Node) handleAppendLog(msg *Message) error {
	// Process log append (simplified)
	fmt.Printf("   📝 %s appending log from %s\n", n.ID, msg.Sender)
	return nil
}

func (n *Node) BecomeLeader(term int) {
	n.State = LEADER
	n.Term = term
	n.Leadership++
	fmt.Printf("   👑 %s became LEADER for term %d\n", n.ID, term)
}

func (n *Node) BecomeCandidate() {
	n.State = CANDIDATE
	n.Term++
	n.VotedFor = n.ID
	fmt.Printf("   🏃 %s became CANDIDATE for term %d\n", n.ID, n.Term)
}

func (n *Node) AddLogEntry(command string, data map[string]interface{}) {
	entry := LogEntry{
		Term:    n.Term,
		Index:   len(n.Log),
		Command: command,
		Data:    data,
		Hash:    calculateHash(command + strconv.Itoa(n.Term)),
	}
	
	n.Log = append(n.Log, entry)
	fmt.Printf("   📚 %s added log entry: %s (index %d)\n", n.ID, command, entry.Index)
}

func calculateHash(data string) string {
	hash := sha256.Sum256([]byte(data))
	return hex.EncodeToString(hash[:])[:16]
}

func (n *Node) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"id":               n.ID,
		"state":            string(n.State),
		"term":             n.Term,
		"reliability":      n.Reliability,
		"responseTime":     n.ResponseTime.Milliseconds(),
		"messagesReceived": n.MessagesReceived,
		"messagesSent":     n.MessagesSent,
		"votesCast":        n.VotesCast,
		"leadership":       n.Leadership,
		"logSize":          len(n.Log),
		"trafficLoad":      n.TrafficLoad,
		"powerStable":      n.PowerStable,
	}
}

// Raft Consensus Algorithm Implementation
type RaftConsensus struct {
	Nodes        []*Node
	CurrentTerm  int
	CurrentLeader string
	MessageLog   []Message
}

func NewRaftConsensus(nodes []*Node) *RaftConsensus {
	return &RaftConsensus{
		Nodes:       nodes,
		CurrentTerm: 0,
		MessageLog:  make([]Message, 0),
	}
}

func (r *RaftConsensus) RunLeaderElection() *ConsensusResult {
	startTime := time.Now()
	
	fmt.Println("\n🚦 RAFT LEADER ELECTION - MUMBAI TRAFFIC CONTROL")
	fmt.Printf("Nodes participating: %d\n", len(r.Nodes))
	fmt.Println("=" + strings.Repeat("=", 50))
	
	// Reset all nodes to followers
	for _, node := range r.Nodes {
		node.State = FOLLOWER
		node.VotedFor = ""
	}
	
	maxRounds := 5
	
	for round := 1; round <= maxRounds; round++ {
		fmt.Printf("\n📊 ELECTION ROUND %d\n", round)
		fmt.Println(strings.Repeat("-", 30))
		
		// Select random candidate (in real Raft, timeout triggers election)
		candidateIndex := rand.Intn(len(r.Nodes))
		candidate := r.Nodes[candidateIndex]
		
		if !candidate.IsActive() {
			fmt.Printf("Selected candidate %s is inactive, skipping round\n", candidate.ID)
			continue
		}
		
		candidate.BecomeCandidate()
		r.CurrentTerm = candidate.Term
		
		// Collect votes
		votes := r.collectVotes(candidate)
		
		// Check for majority
		requiredVotes := len(r.Nodes)/2 + 1
		fmt.Printf("Votes received: %d/%d (required: %d)\n", 
			votes, len(r.Nodes), requiredVotes)
		
		if votes >= requiredVotes {
			candidate.BecomeLeader(r.CurrentTerm)
			r.CurrentLeader = candidate.ID
			
			// Send heartbeats to establish leadership
			r.sendHeartbeats(candidate)
			
			duration := time.Since(startTime)
			
			fmt.Printf("\n✅ LEADER ELECTED: %s (term %d)\n", candidate.ID, r.CurrentTerm)
			
			return &ConsensusResult{
				Success:           true,
				Leader:            candidate.ID,
				Term:              r.CurrentTerm,
				Duration:          duration,
				MessagesExchanged: len(r.MessageLog),
				ParticipantCount:  len(r.Nodes),
				Details: map[string]interface{}{
					"electionRounds": round,
					"votesReceived":  votes,
					"algorithm":      "raft",
				},
			}
		}
		
		fmt.Printf("❌ Insufficient votes, trying next round\n")
		time.Sleep(time.Millisecond * 500) // Brief pause
	}
	
	// Election failed
	duration := time.Since(startTime)
	
	return &ConsensusResult{
		Success:           false,
		Duration:          duration,
		MessagesExchanged: len(r.MessageLog),
		ParticipantCount:  len(r.Nodes),
		Details: map[string]interface{}{
			"electionRounds": maxRounds,
			"algorithm":      "raft",
			"failure":        "max_rounds_exceeded",
		},
	}
}

func (r *RaftConsensus) collectVotes(candidate *Node) int {
	votes := 1 // Candidate votes for itself
	var wg sync.WaitGroup
	var mu sync.Mutex
	
	for _, node := range r.Nodes {
		if node.ID == candidate.ID || !node.IsActive() {
			continue
		}
		
		wg.Add(1)
		go func(n *Node) {
			defer wg.Done()
			
			// Create vote request message
			msg := &Message{
				ID:       fmt.Sprintf("vote_req_%s_%s", candidate.ID, n.ID),
				Type:     REQUEST_VOTE,
				Sender:   candidate.ID,
				Receiver: n.ID,
				Term:     candidate.Term,
				Data: map[string]interface{}{
					"term": candidate.Term,
				},
				Timestamp: time.Now(),
			}
			
			r.MessageLog = append(r.MessageLog, *msg)
			candidate.MessagesSent++
			
			err := n.ProcessMessage(msg)
			if err == nil && n.VotedFor == candidate.ID {
				mu.Lock()
				votes++
				mu.Unlock()
			}
		}(node)
	}
	
	wg.Wait()
	return votes
}

func (r *RaftConsensus) sendHeartbeats(leader *Node) {
	fmt.Printf("\n💓 Leader %s sending heartbeats\n", leader.ID)
	
	for _, node := range r.Nodes {
		if node.ID == leader.ID || !node.IsActive() {
			continue
		}
		
		msg := &Message{
			ID:       fmt.Sprintf("heartbeat_%s_%s", leader.ID, node.ID),
			Type:     HEARTBEAT,
			Sender:   leader.ID,
			Receiver: node.ID,
			Term:     leader.Term,
			Data: map[string]interface{}{
				"term": leader.Term,
			},
			Timestamp: time.Now(),
		}
		
		r.MessageLog = append(r.MessageLog, *msg)
		leader.MessagesSent++
		
		node.ProcessMessage(msg)
	}
}

// Majority Voting Consensus (simplified)
type MajorityConsensus struct {
	Nodes     []*Node
	Threshold float64
}

func NewMajorityConsensus(nodes []*Node, threshold float64) *MajorityConsensus {
	return &MajorityConsensus{
		Nodes:     nodes,
		Threshold: threshold,
	}
}

func (m *MajorityConsensus) RunConsensus(proposal string) *ConsensusResult {
	startTime := time.Now()
	
	fmt.Printf("\n🗳️ MAJORITY VOTING CONSENSUS - %s\n", proposal)
	fmt.Printf("Threshold: %.1f%%\n", m.Threshold*100)
	fmt.Println("=" + strings.Repeat("=", 50))
	
	yesVotes := 0
	noVotes := 0
	totalVotes := 0
	
	var wg sync.WaitGroup
	var mu sync.Mutex
	
	for _, node := range m.Nodes {
		if !node.IsActive() {
			continue
		}
		
		wg.Add(1)
		go func(n *Node) {
			defer wg.Done()
			
			// Simulate voting decision - Mumbai style!
			vote := m.makeVotingDecision(n, proposal)
			
			mu.Lock()
			if vote {
				yesVotes++
			} else {
				noVotes++
			}
			totalVotes++
			n.VotesCast++
			mu.Unlock()
			
			voteStr := "YES"
			if !vote {
				voteStr = "NO"
			}
			fmt.Printf("   🗳️ %s voted: %s\n", n.ID, voteStr)
		}(node)
	}
	
	wg.Wait()
	
	// Calculate results
	approvalRate := float64(yesVotes) / float64(totalVotes)
	success := approvalRate >= m.Threshold
	
	duration := time.Since(startTime)
	
	fmt.Printf("\n📊 VOTING RESULTS:\n")
	fmt.Printf("Yes votes: %d\n", yesVotes)
	fmt.Printf("No votes: %d\n", noVotes)
	fmt.Printf("Total votes: %d\n", totalVotes)
	fmt.Printf("Approval rate: %.1f%%\n", approvalRate*100)
	fmt.Printf("Result: %s\n", map[bool]string{true: "✅ APPROVED", false: "❌ REJECTED"}[success])
	
	return &ConsensusResult{
		Success:          success,
		Duration:         duration,
		ParticipantCount: totalVotes,
		Details: map[string]interface{}{
			"yesVotes":     yesVotes,
			"noVotes":      noVotes,
			"approvalRate": approvalRate,
			"threshold":    m.Threshold,
			"algorithm":    "majority",
			"proposal":     proposal,
		},
	}
}

func (m *MajorityConsensus) makeVotingDecision(node *Node, proposal string) bool {
	// Mumbai-style decision making factors
	
	// Base probability based on proposal type
	baseSupport := 0.6
	
	// Node characteristics influence
	reliabilityFactor := node.Reliability * 0.2
	
	// Traffic load influence (busy nodes are more conservative)
	trafficFactor := (1.0 - node.TrafficLoad) * 0.1
	
	// Power stability influence
	powerFactor := 0.0
	if node.PowerStable {
		powerFactor = 0.1
	}
	
	// Random Mumbai factor (unpredictability!)
	mumbaiChaos := (rand.Float64() - 0.5) * 0.3
	
	totalSupport := baseSupport + reliabilityFactor + trafficFactor + powerFactor + mumbaiChaos
	
	return totalSupport > 0.5
}

// Consensus Simulator - manages different consensus algorithms
type ConsensusSimulator struct {
	Algorithms map[string]interface{}
	Results    []ConsensusResult
}

func NewConsensusSimulator() *ConsensusSimulator {
	return &ConsensusSimulator{
		Algorithms: make(map[string]interface{}),
		Results:    make([]ConsensusResult, 0),
	}
}

func (cs *ConsensusSimulator) AddAlgorithm(name string, algorithm interface{}) {
	cs.Algorithms[name] = algorithm
	fmt.Printf("➕ Added consensus algorithm: %s\n", name)
}

func (cs *ConsensusSimulator) RunComparison() {
	fmt.Println("\n🏆 CONSENSUS ALGORITHMS COMPARISON")
	fmt.Println("Mumbai Traffic Control vs Various Protocols")
	fmt.Println("=" + strings.Repeat("=", 60))
	
	// Create Mumbai traffic nodes
	nodeNames := []string{
		"CST_Junction", "Dadar_Signal", "Bandra_Crossing", "Andheri_Junction",
		"Borivali_Square", "Thane_Circle", "Kurla_Terminal", "Worli_Sealink",
		"Powai_Hub", "Vikhroli_Bridge",
	}
	
	nodes := make([]*Node, len(nodeNames))
	for i, name := range nodeNames {
		nodes[i] = NewMumbaiTrafficNode(name)
	}
	
	fmt.Printf("Created %d Mumbai traffic control nodes\n", len(nodes))
	
	// Test scenarios
	scenarios := []struct {
		name        string
		description string
	}{
		{"traffic_optimization", "Optimize signal timing for rush hour"},
		{"emergency_protocol", "Activate emergency vehicle priority"},
		{"maintenance_window", "Schedule maintenance during low traffic"},
		{"monsoon_mode", "Switch to monsoon traffic management"},
		{"festival_routing", "Implement festival traffic diversions"},
	}
	
	// Run Raft consensus
	raftConsensus := NewRaftConsensus(nodes)
	
	fmt.Printf("\n🚦 TESTING RAFT CONSENSUS\n")
	fmt.Println(strings.Repeat("-", 40))
	
	raftResult := raftConsensus.RunLeaderElection()
	cs.Results = append(cs.Results, *raftResult)
	
	// Run Majority consensus for each scenario
	majorityConsensus := NewMajorityConsensus(nodes, 0.6)
	
	fmt.Printf("\n🗳️ TESTING MAJORITY CONSENSUS\n")
	fmt.Println(strings.Repeat("-", 40))
	
	for i, scenario := range scenarios {
		if i >= 3 { // Limit to 3 scenarios for demo
			break
		}
		
		fmt.Printf("\nScenario %d: %s\n", i+1, scenario.description)
		result := majorityConsensus.RunConsensus(scenario.name)
		cs.Results = append(cs.Results, *result)
		
		time.Sleep(time.Millisecond * 500)
	}
}

func (cs *ConsensusSimulator) PrintSummary() {
	fmt.Printf("\n📊 SIMULATION SUMMARY\n")
	fmt.Println("=" + strings.Repeat("=", 40))
	
	successCount := 0
	totalDuration := time.Duration(0)
	totalMessages := 0
	
	algorithmStats := make(map[string][]ConsensusResult)
	
	for _, result := range cs.Results {
		if result.Success {
			successCount++
		}
		totalDuration += result.Duration
		totalMessages += result.MessagesExchanged
		
		algorithm := result.Details["algorithm"].(string)
		algorithmStats[algorithm] = append(algorithmStats[algorithm], result)
	}
	
	fmt.Printf("Total consensus runs: %d\n", len(cs.Results))
	fmt.Printf("Successful consensus: %d\n", successCount)
	fmt.Printf("Success rate: %.1f%%\n", float64(successCount)/float64(len(cs.Results))*100)
	fmt.Printf("Average duration: %.2fs\n", totalDuration.Seconds()/float64(len(cs.Results)))
	fmt.Printf("Total messages: %d\n", totalMessages)
	
	fmt.Printf("\n🔍 ALGORITHM BREAKDOWN:\n")
	
	for algorithm, results := range algorithmStats {
		successful := 0
		var avgDuration time.Duration
		
		for _, result := range results {
			if result.Success {
				successful++
			}
			avgDuration += result.Duration
		}
		
		if len(results) > 0 {
			avgDuration = time.Duration(int64(avgDuration) / int64(len(results)))
		}
		
		fmt.Printf("%s: %d runs, %.1f%% success, %.2fs avg duration\n",
			algorithm, len(results), float64(successful)/float64(len(results))*100,
			avgDuration.Seconds())
	}
	
	fmt.Printf("\n🎯 KEY INSIGHTS:\n")
	fmt.Println("• Raft provides strong leadership consensus")
	fmt.Println("• Majority voting is simple but effective")
	fmt.Println("• Mumbai characteristics add real-world challenges")
	fmt.Println("• Different algorithms suit different scenarios")
	fmt.Println("• Like Mumbai traffic - coordination is essential!")
}

// Helper function to create strings.Repeat equivalent
func strings.Repeat(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}

func main() {
	// Seed random number generator
	rand.Seed(time.Now().UnixNano())
	
	fmt.Println("🚀 CONSENSUS PROTOCOL SIMULATOR")
	fmt.Println("Mumbai Traffic Control Coordination System")
	fmt.Println("=" + strings.Repeat("=", 60))
	
	// Create simulator
	simulator := NewConsensusSimulator()
	
	// Run comprehensive comparison
	simulator.RunComparison()
	
	// Print final summary
	simulator.PrintSummary()
	
	fmt.Println("\n🎊 CONSENSUS SIMULATION COMPLETED!")
	fmt.Println("Remember: Like Mumbai traffic signals, consensus needs patience and coordination!")
}