package main

/*
Raft Consensus Algorithm - Episode 4
व्यावहारिक Raft consensus का production-ready implementation

यह algorithm distributed systems में consensus achieve करने के लिए use होता है।
Strong consistency guarantee करता है leader election के through.

Indian Context Examples:
- IRCTC master database selection
- Paytm wallet service leader election  
- Flipkart order service coordination
- Zomato delivery assignment system

Raft Components:
1. Leader Election - कौन सा node leader बनेगा
2. Log Replication - सभी nodes पर same logs
3. Safety Properties - consistency guarantee

Raft States:
- Follower: Normal state, requests को leader को forward
- Candidate: Leader election के लिए vote माँगता है
- Leader: सभी client requests handle करता है
*/

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"sync"
	"time"
)

// NodeState represents the current state of a Raft node
type NodeState int

const (
	Follower NodeState = iota
	Candidate
	Leader
)

func (s NodeState) String() string {
	switch s {
	case Follower:
		return "Follower"
	case Candidate:
		return "Candidate" 
	case Leader:
		return "Leader"
	default:
		return "Unknown"
	}
}

// LogEntry represents a single entry in the Raft log
// जैसे IRCTC में ticket booking entry
type LogEntry struct {
	Index     int         `json:"index"`
	Term      int         `json:"term"`
	Command   string      `json:"command"`
	Data      interface{} `json:"data"`
	Timestamp time.Time   `json:"timestamp"`
}

// VoteRequest is sent during leader election
type VoteRequest struct {
	Term         int    `json:"term"`
	CandidateId  string `json:"candidate_id"`
	LastLogIndex int    `json:"last_log_index"`
	LastLogTerm  int    `json:"last_log_term"`
}

// VoteResponse is the reply to vote request  
type VoteResponse struct {
	Term        int  `json:"term"`
	VoteGranted bool `json:"vote_granted"`
	VoterId     string `json:"voter_id"`
}

// AppendEntriesRequest for log replication
type AppendEntriesRequest struct {
	Term         int        `json:"term"`
	LeaderId     string     `json:"leader_id"`
	PrevLogIndex int        `json:"prev_log_index"`
	PrevLogTerm  int        `json:"prev_log_term"`
	Entries      []LogEntry `json:"entries"`
	LeaderCommit int        `json:"leader_commit"`
}

// AppendEntriesResponse reply
type AppendEntriesResponse struct {
	Term         int    `json:"term"`
	Success      bool   `json:"success"`
	FollowerId   string `json:"follower_id"`
	LastLogIndex int    `json:"last_log_index"`
}

// RaftNode represents a single node in the Raft cluster
type RaftNode struct {
	// Node identification
	id       string
	location string // Data center location (Mumbai, Delhi, etc.)
	
	// Persistent state (survives restarts)
	currentTerm int
	votedFor    string
	logs        []LogEntry
	
	// Volatile state
	commitIndex int
	lastApplied int
	state       NodeState
	leaderId    string
	
	// Leader state (only for leader)
	nextIndex  map[string]int
	matchIndex map[string]int
	
	// Cluster membership
	peers map[string]*RaftNode
	
	// Channels for communication
	voteRequestCh    chan VoteRequest
	voteResponseCh   chan VoteResponse
	appendEntriesCh  chan AppendEntriesRequest
	appendResponseCh chan AppendEntriesResponse
	clientRequestCh  chan interface{}
	
	// Timers
	electionTimeout  *time.Timer
	heartbeatTimeout *time.Timer
	
	// Synchronization
	mu sync.RWMutex
	
	// Statistics
	stats Stats
}

// Stats for monitoring
type Stats struct {
	ElectionCount     int       `json:"election_count"`
	HeartbeatsSent    int       `json:"heartbeats_sent"`
	LogEntriesAdded   int       `json:"log_entries_added"`
	VotesReceived     int       `json:"votes_received"`
	VotesGranted      int       `json:"votes_granted"`
	LastElectionTime  time.Time `json:"last_election_time"`
	TotalLeaderTime   time.Duration `json:"total_leader_time"`
	CurrentLeaderSince time.Time `json:"current_leader_since"`
}

// NewRaftNode creates a new Raft node
func NewRaftNode(id, location string) *RaftNode {
	node := &RaftNode{
		id:       id,
		location: location,
		
		// Initialize persistent state
		currentTerm: 0,
		votedFor:    "",
		logs:        make([]LogEntry, 0),
		
		// Initialize volatile state  
		commitIndex: -1,
		lastApplied: -1,
		state:       Follower,
		leaderId:    "",
		
		// Initialize leader state
		nextIndex:  make(map[string]int),
		matchIndex: make(map[string]int),
		
		// Initialize cluster
		peers: make(map[string]*RaftNode),
		
		// Initialize channels
		voteRequestCh:    make(chan VoteRequest, 10),
		voteResponseCh:   make(chan VoteResponse, 10),
		appendEntriesCh:  make(chan AppendEntriesRequest, 10),
		appendResponseCh: make(chan AppendEntriesResponse, 10),
		clientRequestCh:  make(chan interface{}, 10),
		
		// Initialize stats
		stats: Stats{},
	}
	
	// Add initial log entry (like genesis block)
	node.logs = append(node.logs, LogEntry{
		Index:     0,
		Term:      0,
		Command:   "INIT",
		Data:      fmt.Sprintf("Node %s initialized at %s", id, location),
		Timestamp: time.Now(),
	})
	
	fmt.Printf("🚀 Raft node %s started at %s\n", id, location)
	return node
}

// Start begins the Raft node operation
func (rn *RaftNode) Start() {
	fmt.Printf("▶️ Starting Raft node %s\n", rn.id)
	
	// Reset to follower state
	rn.becomeFollower(0)
	
	// Start main event loop
	go rn.eventLoop()
	
	// Start election timeout
	rn.resetElectionTimeout()
}

// Main event loop - handles all Raft events
func (rn *RaftNode) eventLoop() {
	for {
		select {
		// Vote request received
		case req := <-rn.voteRequestCh:
			rn.handleVoteRequest(req)
			
		// Vote response received  
		case resp := <-rn.voteResponseCh:
			rn.handleVoteResponse(resp)
			
		// Append entries request received
		case req := <-rn.appendEntriesCh:
			rn.handleAppendEntries(req)
			
		// Append entries response received
		case resp := <-rn.appendResponseCh:
			rn.handleAppendEntriesResponse(resp)
			
		// Client request received
		case req := <-rn.clientRequestCh:
			rn.handleClientRequest(req)
			
		// Election timeout - become candidate
		case <-rn.electionTimeout.C:
			if rn.state != Leader {
				fmt.Printf("⏰ Election timeout for %s - starting election\n", rn.id)
				rn.startElection()
			}
			
		// Heartbeat timeout - send heartbeats (leader only)
		case <-rn.heartbeatTimeout.C:
			if rn.state == Leader {
				rn.sendHeartbeats()
				rn.resetHeartbeatTimeout()
			}
		}
	}
}

// Start leader election process
func (rn *RaftNode) startElection() {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	// Become candidate
	rn.state = Candidate
	rn.currentTerm++
	rn.votedFor = rn.id // Vote for self
	rn.stats.ElectionCount++
	rn.stats.LastElectionTime = time.Now()
	
	fmt.Printf("🗳️ Node %s starting election for term %d\n", rn.id, rn.currentTerm)
	
	// Reset election timeout
	rn.resetElectionTimeout()
	
	// Request votes from all peers
	lastLogIndex := len(rn.logs) - 1
	lastLogTerm := 0
	if lastLogIndex >= 0 {
		lastLogTerm = rn.logs[lastLogIndex].Term
	}
	
	voteRequest := VoteRequest{
		Term:         rn.currentTerm,
		CandidateId:  rn.id,
		LastLogIndex: lastLogIndex,
		LastLogTerm:  lastLogTerm,
	}
	
	// Send vote requests to all peers
	for peerId, peer := range rn.peers {
		go func(id string, p *RaftNode) {
			fmt.Printf("📨 Sending vote request from %s to %s\n", rn.id, id)
			select {
			case p.voteRequestCh <- voteRequest:
			case <-time.After(time.Millisecond * 100):
				fmt.Printf("⚠️ Vote request timeout to %s\n", id)
			}
		}(peerId, peer)
	}
}

// Handle vote request from candidate
func (rn *RaftNode) handleVoteRequest(req VoteRequest) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	fmt.Printf("📥 Node %s received vote request from %s (term %d)\n", 
		rn.id, req.CandidateId, req.Term)
	
	response := VoteResponse{
		Term:        rn.currentTerm,
		VoteGranted: false,
		VoterId:     rn.id,
	}
	
	// If candidate's term is newer, update our term
	if req.Term > rn.currentTerm {
		rn.currentTerm = req.Term
		rn.votedFor = ""
		rn.becomeFollower(req.Term)
	}
	
	// Grant vote if:
	// 1. Haven't voted in this term OR already voted for this candidate
	// 2. Candidate's log is at least as up-to-date as ours
	if req.Term >= rn.currentTerm &&
		(rn.votedFor == "" || rn.votedFor == req.CandidateId) &&
		rn.isLogUpToDate(req.LastLogIndex, req.LastLogTerm) {
		
		response.VoteGranted = true
		response.Term = req.Term
		rn.votedFor = req.CandidateId
		rn.currentTerm = req.Term
		rn.stats.VotesGranted++
		
		fmt.Printf("✅ Node %s granted vote to %s for term %d\n", 
			rn.id, req.CandidateId, req.Term)
		
		// Reset election timeout since we participated in election
		rn.resetElectionTimeout()
	} else {
		fmt.Printf("❌ Node %s denied vote to %s for term %d\n", 
			rn.id, req.CandidateId, req.Term)
	}
	
	// Send response back to candidate
	if candidate, exists := rn.peers[req.CandidateId]; exists {
		go func() {
			select {
			case candidate.voteResponseCh <- response:
			case <-time.After(time.Millisecond * 100):
				fmt.Printf("⚠️ Vote response timeout to %s\n", req.CandidateId)
			}
		}()
	}
}

// Handle vote response during election
func (rn *RaftNode) handleVoteResponse(resp VoteResponse) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	// Ignore if not candidate or term is old
	if rn.state != Candidate || resp.Term < rn.currentTerm {
		return
	}
	
	// If response has newer term, become follower
	if resp.Term > rn.currentTerm {
		rn.becomeFollower(resp.Term)
		return
	}
	
	fmt.Printf("📨 Node %s received vote response from %s: %t\n", 
		rn.id, resp.VoterId, resp.VoteGranted)
	
	if resp.VoteGranted {
		rn.stats.VotesReceived++
		
		// Count votes (including self-vote)
		votes := 1 // Self vote
		for _, peer := range rn.peers {
			// This is simplified - in real implementation, 
			// we'd track votes properly
			if peer.votedFor == rn.id && peer.currentTerm == rn.currentTerm {
				votes++
			}
		}
		
		// Check if majority reached
		majority := (len(rn.peers) + 1) / 2 + 1
		if votes >= majority {
			fmt.Printf("🎉 Node %s won election with %d votes (needed %d)\n", 
				rn.id, votes, majority)
			rn.becomeLeader()
		}
	}
}

// Become leader after winning election
func (rn *RaftNode) becomeLeader() {
	fmt.Printf("👑 Node %s became LEADER for term %d\n", rn.id, rn.currentTerm)
	
	rn.state = Leader
	rn.leaderId = rn.id
	rn.stats.CurrentLeaderSince = time.Now()
	
	// Initialize leader state
	lastLogIndex := len(rn.logs) - 1
	for peerId := range rn.peers {
		rn.nextIndex[peerId] = lastLogIndex + 1
		rn.matchIndex[peerId] = -1
	}
	
	// Stop election timeout
	rn.electionTimeout.Stop()
	
	// Start sending heartbeats
	rn.resetHeartbeatTimeout()
	rn.sendHeartbeats()
	
	// Send leadership announcement
	fmt.Printf("📢 LEADERSHIP ANNOUNCEMENT: %s is now leader of the cluster\n", rn.id)
}

// Become follower (demotion or initialization)
func (rn *RaftNode) becomeFollower(term int) {
	oldState := rn.state
	rn.state = Follower
	rn.currentTerm = term
	rn.votedFor = ""
	
	// Update leadership time if was leader
	if oldState == Leader {
		rn.stats.TotalLeaderTime += time.Since(rn.stats.CurrentLeaderSince)
	}
	
	// Stop heartbeat timeout if was leader
	if rn.heartbeatTimeout != nil {
		rn.heartbeatTimeout.Stop()
	}
	
	// Reset election timeout
	rn.resetElectionTimeout()
	
	fmt.Printf("📉 Node %s became FOLLOWER (term %d)\n", rn.id, term)
}

// Send heartbeats to all peers (leader only)
func (rn *RaftNode) sendHeartbeats() {
	if rn.state != Leader {
		return
	}
	
	fmt.Printf("💓 Leader %s sending heartbeats for term %d\n", rn.id, rn.currentTerm)
	rn.stats.HeartbeatsSent++
	
	for peerId, peer := range rn.peers {
		go rn.sendAppendEntries(peerId, peer, true) // Empty heartbeat
	}
}

// Send append entries (heartbeat or log replication)
func (rn *RaftNode) sendAppendEntries(peerId string, peer *RaftNode, heartbeat bool) {
	rn.mu.RLock()
	
	nextIndex := rn.nextIndex[peerId]
	prevLogIndex := nextIndex - 1
	prevLogTerm := 0
	
	if prevLogIndex >= 0 && prevLogIndex < len(rn.logs) {
		prevLogTerm = rn.logs[prevLogIndex].Term
	}
	
	// Prepare entries to send
	var entries []LogEntry
	if !heartbeat && nextIndex < len(rn.logs) {
		entries = rn.logs[nextIndex:]
	}
	
	request := AppendEntriesRequest{
		Term:         rn.currentTerm,
		LeaderId:     rn.id,
		PrevLogIndex: prevLogIndex,
		PrevLogTerm:  prevLogTerm,
		Entries:      entries,
		LeaderCommit: rn.commitIndex,
	}
	
	rn.mu.RUnlock()
	
	// Send request
	select {
	case peer.appendEntriesCh <- request:
	case <-time.After(time.Millisecond * 100):
		fmt.Printf("⚠️ Append entries timeout to %s\n", peerId)
	}
}

// Handle append entries request
func (rn *RaftNode) handleAppendEntries(req AppendEntriesRequest) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	response := AppendEntriesResponse{
		Term:         rn.currentTerm,
		Success:      false,
		FollowerId:   rn.id,
		LastLogIndex: len(rn.logs) - 1,
	}
	
	// If request term is newer, update our term and become follower
	if req.Term > rn.currentTerm {
		rn.becomeFollower(req.Term)
		response.Term = req.Term
	}
	
	// Reject if term is older
	if req.Term < rn.currentTerm {
		fmt.Printf("❌ Node %s rejected append entries from %s (old term %d < %d)\n", 
			rn.id, req.LeaderId, req.Term, rn.currentTerm)
	} else {
		// Valid leader for current term
		rn.leaderId = req.LeaderId
		rn.resetElectionTimeout() // Reset timeout since we heard from leader
		
		if len(req.Entries) == 0 {
			// Heartbeat
			fmt.Printf("💓 Node %s received heartbeat from leader %s\n", rn.id, req.LeaderId)
		} else {
			// Log replication
			fmt.Printf("📝 Node %s received %d log entries from leader %s\n", 
				rn.id, len(req.Entries), req.LeaderId)
		}
		
		// Check log consistency
		if req.PrevLogIndex < 0 || 
			(req.PrevLogIndex < len(rn.logs) && 
			 (req.PrevLogIndex < 0 || rn.logs[req.PrevLogIndex].Term == req.PrevLogTerm)) {
			
			response.Success = true
			
			// Append new entries
			if len(req.Entries) > 0 {
				// Remove conflicting entries first
				if req.PrevLogIndex + 1 < len(rn.logs) {
					rn.logs = rn.logs[:req.PrevLogIndex + 1]
				}
				
				// Append new entries
				rn.logs = append(rn.logs, req.Entries...)
				rn.stats.LogEntriesAdded += len(req.Entries)
				
				fmt.Printf("✅ Node %s appended %d entries, log size now %d\n", 
					rn.id, len(req.Entries), len(rn.logs))
			}
			
			// Update commit index
			if req.LeaderCommit > rn.commitIndex {
				rn.commitIndex = min(req.LeaderCommit, len(rn.logs) - 1)
				fmt.Printf("📊 Node %s updated commit index to %d\n", rn.id, rn.commitIndex)
			}
			
			response.LastLogIndex = len(rn.logs) - 1
		}
	}
	
	// Send response back to leader
	if leader, exists := rn.peers[req.LeaderId]; exists {
		go func() {
			select {
			case leader.appendResponseCh <- response:
			case <-time.After(time.Millisecond * 100):
				fmt.Printf("⚠️ Append response timeout to %s\n", req.LeaderId)
			}
		}()
	}
}

// Handle append entries response (leader only)
func (rn *RaftNode) handleAppendEntriesResponse(resp AppendEntriesResponse) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	if rn.state != Leader || resp.Term < rn.currentTerm {
		return
	}
	
	// If response has newer term, step down
	if resp.Term > rn.currentTerm {
		rn.becomeFollower(resp.Term)
		return
	}
	
	if resp.Success {
		// Update match and next indices
		rn.matchIndex[resp.FollowerId] = resp.LastLogIndex
		rn.nextIndex[resp.FollowerId] = resp.LastLogIndex + 1
		
		fmt.Printf("✅ Leader %s: Follower %s up to date (index %d)\n", 
			rn.id, resp.FollowerId, resp.LastLogIndex)
		
		// Check if we can advance commit index
		rn.updateCommitIndex()
	} else {
		// Decrement next index and retry
		if rn.nextIndex[resp.FollowerId] > 0 {
			rn.nextIndex[resp.FollowerId]--
		}
		
		fmt.Printf("❌ Leader %s: Follower %s rejected, retrying with index %d\n", 
			rn.id, resp.FollowerId, rn.nextIndex[resp.FollowerId])
		
		// Retry append entries
		if peer, exists := rn.peers[resp.FollowerId]; exists {
			go rn.sendAppendEntries(resp.FollowerId, peer, false)
		}
	}
}

// Update commit index based on majority replication
func (rn *RaftNode) updateCommitIndex() {
	if rn.state != Leader {
		return
	}
	
	// Find highest index replicated on majority
	for index := len(rn.logs) - 1; index > rn.commitIndex; index-- {
		if rn.logs[index].Term == rn.currentTerm {
			replicas := 1 // Leader has it
			for _, matchIndex := range rn.matchIndex {
				if matchIndex >= index {
					replicas++
				}
			}
			
			majority := (len(rn.peers) + 1) / 2 + 1
			if replicas >= majority {
				rn.commitIndex = index
				fmt.Printf("📊 Leader %s advanced commit index to %d (replicated on %d/%d nodes)\n", 
					rn.id, index, replicas, len(rn.peers) + 1)
				break
			}
		}
	}
}

// Handle client requests (leader only)
func (rn *RaftNode) handleClientRequest(req interface{}) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	if rn.state != Leader {
		fmt.Printf("❌ Node %s is not leader, redirecting to %s\n", rn.id, rn.leaderId)
		return
	}
	
	// Create log entry
	entry := LogEntry{
		Index:     len(rn.logs),
		Term:      rn.currentTerm,
		Command:   "CLIENT_REQUEST",
		Data:      req,
		Timestamp: time.Now(),
	}
	
	// Append to our log
	rn.logs = append(rn.logs, entry)
	fmt.Printf("📝 Leader %s appended client request to log (index %d)\n", rn.id, entry.Index)
	
	// Replicate to followers
	for peerId, peer := range rn.peers {
		go rn.sendAppendEntries(peerId, peer, false)
	}
}

// Utility functions
func (rn *RaftNode) isLogUpToDate(lastLogIndex, lastLogTerm int) bool {
	ourLastIndex := len(rn.logs) - 1
	ourLastTerm := 0
	if ourLastIndex >= 0 {
		ourLastTerm = rn.logs[ourLastIndex].Term
	}
	
	// Candidate's log is up-to-date if:
	// 1. Last term is higher, OR
	// 2. Same term but index is at least as high
	return lastLogTerm > ourLastTerm || 
		   (lastLogTerm == ourLastTerm && lastLogIndex >= ourLastIndex)
}

func (rn *RaftNode) resetElectionTimeout() {
	if rn.electionTimeout != nil {
		rn.electionTimeout.Stop()
	}
	
	// Random timeout between 150-300ms (production: 150-300ms)
	timeout := time.Duration(150 + rand.Intn(150)) * time.Millisecond
	rn.electionTimeout = time.NewTimer(timeout)
}

func (rn *RaftNode) resetHeartbeatTimeout() {
	if rn.heartbeatTimeout != nil {
		rn.heartbeatTimeout.Stop()
	}
	
	// Heartbeat every 50ms (production: 50-100ms)
	rn.heartbeatTimeout = time.NewTimer(50 * time.Millisecond)
}

// Add peer to cluster
func (rn *RaftNode) AddPeer(peer *RaftNode) {
	rn.mu.Lock()
	defer rn.mu.Unlock()
	
	rn.peers[peer.id] = peer
	fmt.Printf("🤝 Node %s added peer %s\n", rn.id, peer.id)
}

// Get current state info
func (rn *RaftNode) GetState() (string, int, bool) {
	rn.mu.RLock()
	defer rn.mu.RUnlock()
	
	return rn.state.String(), rn.currentTerm, rn.state == Leader
}

// Get statistics
func (rn *RaftNode) GetStats() Stats {
	rn.mu.RLock()
	defer rn.mu.RUnlock()
	
	stats := rn.stats
	if rn.state == Leader {
		stats.TotalLeaderTime += time.Since(rn.stats.CurrentLeaderSince)
	}
	return stats
}

// Client interface - submit request to cluster
func (rn *RaftNode) SubmitRequest(data interface{}) error {
	if rn.state != Leader {
		return fmt.Errorf("not leader, current leader: %s", rn.leaderId)
	}
	
	select {
	case rn.clientRequestCh <- data:
		return nil
	case <-time.After(time.Second):
		return fmt.Errorf("request timeout")
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// RaftCluster manages multiple Raft nodes
type RaftCluster struct {
	nodes    map[string]*RaftNode
	mu       sync.RWMutex
}

func NewRaftCluster() *RaftCluster {
	return &RaftCluster{
		nodes: make(map[string]*RaftNode),
	}
}

func (rc *RaftCluster) AddNode(id, location string) *RaftNode {
	rc.mu.Lock()
	defer rc.mu.Unlock()
	
	node := NewRaftNode(id, location)
	rc.nodes[id] = node
	
	// Connect to all existing nodes
	for _, existingNode := range rc.nodes {
		if existingNode.id != id {
			node.AddPeer(existingNode)
			existingNode.AddPeer(node)
		}
	}
	
	return node
}

func (rc *RaftCluster) StartAll() {
	rc.mu.RLock()
	defer rc.mu.RUnlock()
	
	fmt.Printf("🚀 Starting Raft cluster with %d nodes\n", len(rc.nodes))
	
	for _, node := range rc.nodes {
		node.Start()
	}
	
	time.Sleep(100 * time.Millisecond) // Let nodes initialize
}

func (rc *RaftCluster) GetLeader() *RaftNode {
	rc.mu.RLock()
	defer rc.mu.RUnlock()
	
	for _, node := range rc.nodes {
		if state, _, isLeader := node.GetState(); isLeader {
			fmt.Printf("👑 Current leader: %s (%s) at %s\n", node.id, state, node.location)
			return node
		}
	}
	return nil
}

func (rc *RaftCluster) PrintClusterState() {
	rc.mu.RLock()
	defer rc.mu.RUnlock()
	
	fmt.Printf("\n📊 RAFT CLUSTER STATE\n")
	fmt.Printf("=" + "=" * 50 + "\n")
	
	for id, node := range rc.nodes {
		state, term, isLeader := node.GetState()
		leader_indicator := ""
		if isLeader {
			leader_indicator = " 👑"
		}
		
		fmt.Printf("Node %s (%s): %s (Term %d)%s\n", 
			id, node.location, state, term, leader_indicator)
		
		stats := node.GetStats()
		fmt.Printf("  Elections: %d, Heartbeats: %d, Log entries: %d\n", 
			stats.ElectionCount, stats.HeartbeatsSent, stats.LogEntriesAdded)
		fmt.Printf("  Votes received: %d, Votes granted: %d\n", 
			stats.VotesReceived, stats.VotesGranted)
		
		if stats.TotalLeaderTime > 0 {
			fmt.Printf("  Total leader time: %v\n", stats.TotalLeaderTime.Round(time.Millisecond))
		}
	}
	fmt.Println()
}

// IRCTC Ticket Booking Simulation using Raft
func simulateIRCTCBooking(cluster *RaftCluster) {
	fmt.Printf("\n🚆 IRCTC TICKET BOOKING SIMULATION\n")
	fmt.Printf("-" + "-" * 40 + "\n")
	
	leader := cluster.GetLeader()
	if leader == nil {
		fmt.Printf("❌ No leader available for booking\n")
		return
	}
	
	// Simulate ticket booking requests
	bookingRequests := []map[string]interface{}{
		{
			"type": "BOOK_TICKET",
			"train": "12345_Rajdhani_Express", 
			"from": "Mumbai",
			"to": "Delhi",
			"passenger": "Rajesh Kumar",
			"seat": "A1-23",
		},
		{
			"type": "BOOK_TICKET",
			"train": "12345_Rajdhani_Express",
			"from": "Mumbai", 
			"to": "Delhi",
			"passenger": "Priya Sharma",
			"seat": "A1-24",
		},
		{
			"type": "CANCEL_TICKET",
			"ticket_id": "TKT123456",
			"passenger": "Amit Singh",
		},
	}
	
	for i, booking := range bookingRequests {
		fmt.Printf("📝 Submitting booking request %d: %v\n", i+1, booking["type"])
		
		err := leader.SubmitRequest(booking)
		if err != nil {
			fmt.Printf("❌ Booking request %d failed: %v\n", i+1, err)
		} else {
			fmt.Printf("✅ Booking request %d submitted successfully\n", i+1)
		}
		
		time.Sleep(500 * time.Millisecond) // Wait for replication
	}
	
	fmt.Printf("🎯 IRCTC booking simulation complete\n")
}

// Simulate leader failure and recovery
func simulateLeaderFailure(cluster *RaftCluster) {
	fmt.Printf("\n💥 LEADER FAILURE SIMULATION\n")
	fmt.Printf("-" + "-" * 30 + "\n")
	
	leader := cluster.GetLeader()
	if leader == nil {
		fmt.Printf("❌ No leader to fail\n")
		return
	}
	
	fmt.Printf("💥 Simulating failure of leader %s\n", leader.id)
	
	// Stop the leader (simulate crash)
	leader.mu.Lock()
	leader.state = Follower // Force step down
	leader.mu.Unlock()
	
	// Wait for new election
	fmt.Printf("⏳ Waiting for new leader election...\n")
	time.Sleep(2 * time.Second)
	
	newLeader := cluster.GetLeader()
	if newLeader != nil {
		fmt.Printf("👑 New leader elected: %s\n", newLeader.id)
		
		// Test new leader with a request
		testRequest := map[string]interface{}{
			"type": "HEALTH_CHECK",
			"message": "Testing new leader",
		}
		
		err := newLeader.SubmitRequest(testRequest)
		if err != nil {
			fmt.Printf("❌ New leader test failed: %v\n", err)
		} else {
			fmt.Printf("✅ New leader working correctly\n")
		}
	} else {
		fmt.Printf("❌ No new leader elected\n")
	}
}

// Main demonstration
func main() {
	fmt.Printf("🇮🇳 Raft Consensus Algorithm - Indian Tech Context\n")
	fmt.Printf("=" + "=" * 55 + "\n")
	
	// Initialize random seed
	rand.Seed(time.Now().UnixNano())
	
	// Create Raft cluster with Indian data centers
	cluster := NewRaftCluster()
	
	// Add nodes representing different Indian cities
	cluster.AddNode("mumbai_primary", "Mumbai") 
	cluster.AddNode("delhi_secondary", "Delhi")
	cluster.AddNode("bangalore_tertiary", "Bangalore")
	cluster.AddNode("chennai_backup", "Chennai")
	cluster.AddNode("hyderabad_dr", "Hyderabad")
	
	// Start all nodes
	cluster.StartAll()
	
	// Wait for initial election
	fmt.Printf("⏳ Waiting for initial leader election...\n")
	time.Sleep(1 * time.Second)
	
	// Show initial state
	cluster.PrintClusterState()
	
	// Wait a bit more for stability
	time.Sleep(2 * time.Second)
	
	// Simulate IRCTC ticket booking
	simulateIRCTCBooking(cluster)
	
	// Show state after bookings
	fmt.Printf("\nState after bookings:\n")
	cluster.PrintClusterState()
	
	// Simulate leader failure
	simulateLeaderFailure(cluster)
	
	// Final state
	fmt.Printf("\nFinal cluster state:\n")
	cluster.PrintClusterState()
	
	fmt.Printf("\n✅ Raft Consensus demonstration complete!\n")
	fmt.Printf("\n📚 KEY LEARNINGS:\n")
	fmt.Printf("1. Raft ensures strong consistency through leader election\n")
	fmt.Printf("2. Only leader handles client requests\n")
	fmt.Printf("3. Automatic failover when leader crashes\n")
	fmt.Printf("4. Log replication ensures all nodes have same state\n")
	fmt.Printf("5. Used by: etcd, Consul, MongoDB, CockroachDB\n")
	fmt.Printf("6. Indian use cases:\n")
	fmt.Printf("   • IRCTC master database selection\n")
	fmt.Printf("   • Paytm wallet service coordination\n")
	fmt.Printf("   • Flipkart order processing pipeline\n")
	fmt.Printf("   • Zomato delivery assignment system\n")
}