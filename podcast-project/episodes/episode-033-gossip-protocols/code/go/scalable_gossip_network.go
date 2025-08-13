// Scalable Gossip Network Implementation
// =====================================
//
// IRCTC Real-time Train Status Network: जब हजारों trains की real-time status
// को millions of users तक पहुंचाना हो तो कैसे efficiently gossip करें?
//
// This implements a highly scalable gossip protocol designed for
// large-scale distributed systems with thousands of nodes.
//
// Author: Code Developer Agent
// Episode: 33 - Gossip Protocols

package main

import (
	"context"
	"crypto/rand"
	"fmt"
	"log"
	"math"
	mathRand "math/rand"
	"strings"
	"sync"
	"time"
)

// TrainStatus represents real-time train information
type TrainStatus struct {
	TrainNumber    string    `json:"train_number"`
	TrainName      string    `json:"train_name"`
	CurrentStation string    `json:"current_station"`
	DelayMinutes   int       `json:"delay_minutes"`
	Status         string    `json:"status"` // RUNNING, DELAYED, CANCELLED, ARRIVED
	Timestamp      time.Time `json:"timestamp"`
	Source         string    `json:"source"`
	Version        int64     `json:"version"`
}

// GossipMessage represents a message in the gossip protocol
type GossipMessage struct {
	MessageID    string                 `json:"message_id"`
	SenderID     string                 `json:"sender_id"`
	MessageType  string                 `json:"message_type"` // STATUS_UPDATE, HEARTBEAT, MEMBERSHIP
	TrainUpdates map[string]TrainStatus `json:"train_updates"`
	Timestamp    time.Time              `json:"timestamp"`
	TTL          int                    `json:"ttl"`
	Checksum     string                 `json:"checksum"`
}

// NodeMetrics tracks performance metrics for the gossip node
type NodeMetrics struct {
	MessagesReceived   int64         `json:"messages_received"`
	MessagesSent       int64         `json:"messages_sent"`
	StatusUpdates      int64         `json:"status_updates"`
	GossipRounds       int64         `json:"gossip_rounds"`
	AverageLatency     time.Duration `json:"average_latency"`
	NetworkEfficiency  float64       `json:"network_efficiency"`
	LastGossipTime     time.Time     `json:"last_gossip_time"`
	ActiveConnections  int           `json:"active_connections"`
	DataConsistency    float64       `json:"data_consistency"`
	mu                 sync.RWMutex
}

// ScalableGossipNode represents an IRCTC status server node
type ScalableGossipNode struct {
	NodeID       string
	StationCode  string
	Region       string
	Zone         string
	
	// Data storage
	trainStatuses   map[string]TrainStatus
	statusMutex     sync.RWMutex
	
	// Gossip protocol parameters
	gossipFanout    int
	gossipInterval  time.Duration
	maxMessageSize  int
	heartbeatInterval time.Duration
	
	// Network topology
	peers           map[string]*PeerInfo
	peersMutex      sync.RWMutex
	
	// Scalability features
	bloomFilter     *BloomFilter
	messageCache    *MessageCache
	rateLimiter     *RateLimiter
	
	// Metrics and monitoring
	metrics         *NodeMetrics
	
	// Control channels
	ctx             context.Context
	cancel          context.CancelFunc
	gossipTicker    *time.Ticker
	heartbeatTicker *time.Ticker
	
	// Message processing
	incomingMessages chan GossipMessage
	outgoingMessages chan GossipMessage
	
	logger          *log.Logger
}

// PeerInfo stores information about a peer node
type PeerInfo struct {
	NodeID       string    `json:"node_id"`
	StationCode  string    `json:"station_code"`
	Region       string    `json:"region"`
	Zone         string    `json:"zone"`
	LastSeen     time.Time `json:"last_seen"`
	Reliability  float64   `json:"reliability"`
	Distance     int       `json:"distance"` // Hop distance
	MessageCount int64     `json:"message_count"`
}

// BloomFilter for efficient message deduplication
type BloomFilter struct {
	bitArray []bool
	size     int
	hashFunc func(string) []int
	mu       sync.RWMutex
}

// MessageCache for recent message tracking
type MessageCache struct {
	cache    map[string]time.Time
	maxSize  int
	ttl      time.Duration
	mu       sync.RWMutex
}

// RateLimiter for controlling message flow
type RateLimiter struct {
	tokens    int
	maxTokens int
	refillRate time.Duration
	lastRefill time.Time
	mu        sync.Mutex
}

// NewScalableGossipNode creates a new scalable gossip node
func NewScalableGossipNode(nodeID, stationCode, region, zone string) *ScalableGossipNode {
	ctx, cancel := context.WithCancel(context.Background())
	
	node := &ScalableGossipNode{
		NodeID:       nodeID,
		StationCode:  stationCode,
		Region:       region,
		Zone:         zone,
		
		trainStatuses: make(map[string]TrainStatus),
		
		// Scalable configuration
		gossipFanout:      5,  // Limited fanout for scalability
		gossipInterval:    3 * time.Second,
		maxMessageSize:    1024 * 10, // 10KB max message
		heartbeatInterval: 30 * time.Second,
		
		peers: make(map[string]*PeerInfo),
		
		// Scalability components
		bloomFilter:  NewBloomFilter(10000),
		messageCache: NewMessageCache(1000, 5*time.Minute),
		rateLimiter:  NewRateLimiter(100, time.Second),
		
		metrics: &NodeMetrics{},
		
		ctx:    ctx,
		cancel: cancel,
		
		incomingMessages: make(chan GossipMessage, 1000),
		outgoingMessages: make(chan GossipMessage, 1000),
		
		logger: log.New(log.Writer(), fmt.Sprintf("[%s] ", nodeID), log.LstdFlags),
	}
	
	// Start background processes
	go node.messageProcessor()
	go node.gossipLoop()
	go node.heartbeatLoop()
	go node.metricsUpdater()
	
	node.logger.Printf("🚂 IRCTC Station %s started in %s zone (%s region)", stationCode, zone, region)
	
	return node
}

// NewBloomFilter creates a new bloom filter
func NewBloomFilter(size int) *BloomFilter {
	return &BloomFilter{
		bitArray: make([]bool, size),
		size:     size,
		hashFunc: func(data string) []int {
			// Simple hash functions for demo
			h1 := int(djb2Hash(data)) % size
			h2 := int(sdbmHash(data)) % size
			h3 := int(fnvHash(data)) % size
			return []int{h1, h2, h3}
		},
	}
}

// NewMessageCache creates a new message cache
func NewMessageCache(maxSize int, ttl time.Duration) *MessageCache {
	cache := &MessageCache{
		cache:   make(map[string]time.Time),
		maxSize: maxSize,
		ttl:     ttl,
	}
	
	// Start cleanup goroutine
	go cache.cleanup()
	return cache
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(maxTokens int, refillRate time.Duration) *RateLimiter {
	return &RateLimiter{
		tokens:     maxTokens,
		maxTokens:  maxTokens,
		refillRate: refillRate,
		lastRefill: time.Now(),
	}
}

// AddPeer adds a peer to the node's network
func (n *ScalableGossipNode) AddPeer(peerInfo *PeerInfo) {
	n.peersMutex.Lock()
	defer n.peersMutex.Unlock()
	
	n.peers[peerInfo.NodeID] = peerInfo
	n.logger.Printf("🔗 Added peer: %s (%s)", peerInfo.NodeID, peerInfo.StationCode)
	
	n.metrics.mu.Lock()
	n.metrics.ActiveConnections = len(n.peers)
	n.metrics.mu.Unlock()
}

// UpdateTrainStatus updates the status of a train
func (n *ScalableGossipNode) UpdateTrainStatus(status TrainStatus) {
	status.Source = n.NodeID
	status.Timestamp = time.Now()
	status.Version = time.Now().UnixNano()
	
	n.statusMutex.Lock()
	n.trainStatuses[status.TrainNumber] = status
	n.statusMutex.Unlock()
	
	n.logger.Printf("📊 Updated train %s: %s at %s (delay: %d min)", 
		status.TrainNumber, status.Status, status.CurrentStation, status.DelayMinutes)
	
	// Trigger immediate gossip for critical updates
	if status.DelayMinutes > 30 || status.Status == "CANCELLED" {
		n.triggerUrgentGossip(status)
	}
	
	n.metrics.mu.Lock()
	n.metrics.StatusUpdates++
	n.metrics.mu.Unlock()
}

// triggerUrgentGossip sends urgent updates immediately
func (n *ScalableGossipNode) triggerUrgentGossip(status TrainStatus) {
	updates := map[string]TrainStatus{
		status.TrainNumber: status,
	}
	
	message := GossipMessage{
		MessageID:    generateMessageID(),
		SenderID:     n.NodeID,
		MessageType:  "URGENT_UPDATE",
		TrainUpdates: updates,
		Timestamp:    time.Now(),
		TTL:          10, // Higher TTL for urgent messages
	}
	
	select {
	case n.outgoingMessages <- message:
		n.logger.Printf("🚨 Triggered urgent gossip for train %s", status.TrainNumber)
	default:
		n.logger.Printf("⚠️ Outgoing message queue full, dropping urgent message")
	}
}

// messageProcessor handles incoming and outgoing messages
func (n *ScalableGossipNode) messageProcessor() {
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case msg := <-n.incomingMessages:
			n.processIncomingMessage(msg)
			
		case msg := <-n.outgoingMessages:
			n.processOutgoingMessage(msg)
		}
	}
}

// processIncomingMessage processes received gossip messages
func (n *ScalableGossipNode) processIncomingMessage(msg GossipMessage) {
	// Check rate limiting
	if !n.rateLimiter.Allow() {
		n.logger.Printf("🚫 Rate limit exceeded, dropping message from %s", msg.SenderID)
		return
	}
	
	// Check bloom filter for duplicate detection
	if n.bloomFilter.Contains(msg.MessageID) {
		return // Duplicate message
	}
	n.bloomFilter.Add(msg.MessageID)
	
	// Check message cache
	if n.messageCache.Contains(msg.MessageID) {
		return // Already processed
	}
	n.messageCache.Add(msg.MessageID)
	
	// Update peer information
	n.updatePeerInfo(msg.SenderID)
	
	// Process train status updates
	updatedCount := 0
	n.statusMutex.Lock()
	for trainNumber, newStatus := range msg.TrainUpdates {
		existingStatus, exists := n.trainStatuses[trainNumber]
		
		if !exists || newStatus.Version > existingStatus.Version {
			n.trainStatuses[trainNumber] = newStatus
			updatedCount++
			
			n.logger.Printf("📥 Updated train %s from %s: %s", 
				trainNumber, msg.SenderID, newStatus.Status)
		}
	}
	n.statusMutex.Unlock()
	
	// Forward message if TTL allows and we have updates
	if msg.TTL > 0 && updatedCount > 0 {
		n.forwardMessage(msg, updatedCount)
	}
	
	n.metrics.mu.Lock()
	n.metrics.MessagesReceived++
	n.metrics.mu.Unlock()
}

// processOutgoingMessage sends gossip messages to peers
func (n *ScalableGossipNode) processOutgoingMessage(msg GossipMessage) {
	selectedPeers := n.selectGossipPeers()
	
	for _, peerID := range selectedPeers {
		// Simulate sending message to peer
		n.sendToPeer(peerID, msg)
	}
	
	n.metrics.mu.Lock()
	n.metrics.MessagesSent += int64(len(selectedPeers))
	n.metrics.mu.Unlock()
}

// selectGossipPeers selects optimal peers for gossip using smart algorithms
func (n *ScalableGossipNode) selectGossipPeers() []string {
	n.peersMutex.RLock()
	defer n.peersMutex.RUnlock()
	
	if len(n.peers) == 0 {
		return nil
	}
	
	// Create weighted peer list based on reliability and distance
	type weightedPeer struct {
		peerID string
		weight float64
	}
	
	var weightedPeers []weightedPeer
	
	for peerID, peer := range n.peers {
		// Calculate weight based on multiple factors
		reliabilityWeight := peer.Reliability
		distanceWeight := 1.0 / (float64(peer.Distance) + 1.0)
		freshnessWeight := calculateFreshnessWeight(peer.LastSeen)
		
		totalWeight := reliabilityWeight * distanceWeight * freshnessWeight
		
		weightedPeers = append(weightedPeers, weightedPeer{
			peerID: peerID,
			weight: totalWeight,
		})
	}
	
	// Sort by weight (descending)
	for i := 0; i < len(weightedPeers)-1; i++ {
		for j := i + 1; j < len(weightedPeers); j++ {
			if weightedPeers[i].weight < weightedPeers[j].weight {
				weightedPeers[i], weightedPeers[j] = weightedPeers[j], weightedPeers[i]
			}
		}
	}
	
	// Select top peers (with some randomness for load balancing)
	selectedCount := min(n.gossipFanout, len(weightedPeers))
	var selected []string
	
	// Take top 70% deterministically
	deterministicCount := int(float64(selectedCount) * 0.7)
	for i := 0; i < deterministicCount && i < len(weightedPeers); i++ {
		selected = append(selected, weightedPeers[i].peerID)
	}
	
	// Random selection for remaining slots
	remaining := selectedCount - len(selected)
	if remaining > 0 && len(weightedPeers) > deterministicCount {
		// Simple random selection from remaining peers
		for i := 0; i < remaining && deterministicCount+i < len(weightedPeers); i++ {
			selected = append(selected, weightedPeers[deterministicCount+i].peerID)
		}
	}
	
	return selected
}

// forwardMessage forwards a message with decremented TTL
func (n *ScalableGossipNode) forwardMessage(msg GossipMessage, updatedCount int) {
	// Create forwarded message
	forwardedMsg := GossipMessage{
		MessageID:    generateMessageID(),
		SenderID:     n.NodeID,
		MessageType:  "FORWARDED_UPDATE",
		TrainUpdates: n.getRecentUpdates(10), // Limit forwarded updates
		Timestamp:    time.Now(),
		TTL:          msg.TTL - 1,
	}
	
	select {
	case n.outgoingMessages <- forwardedMsg:
		n.logger.Printf("↪️ Forwarded message with %d updates (TTL: %d)", 
			len(forwardedMsg.TrainUpdates), forwardedMsg.TTL)
	default:
		n.logger.Printf("⚠️ Outgoing queue full, dropping forwarded message")
	}
}

// getRecentUpdates returns recent train status updates
func (n *ScalableGossipNode) getRecentUpdates(limit int) map[string]TrainStatus {
	n.statusMutex.RLock()
	defer n.statusMutex.RUnlock()
	
	updates := make(map[string]TrainStatus)
	count := 0
	
	// Get most recent updates (simplified - in real system would sort by timestamp)
	for trainNumber, status := range n.trainStatuses {
		if count >= limit {
			break
		}
		
		// Only include recent updates (last 10 minutes)
		if time.Since(status.Timestamp) < 10*time.Minute {
			updates[trainNumber] = status
			count++
		}
	}
	
	return updates
}

// gossipLoop performs regular gossip rounds
func (n *ScalableGossipNode) gossipLoop() {
	n.gossipTicker = time.NewTicker(n.gossipInterval)
	defer n.gossipTicker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-n.gossipTicker.C:
			n.performGossipRound()
		}
	}
}

// performGossipRound executes one gossip round
func (n *ScalableGossipNode) performGossipRound() {
	updates := n.getRecentUpdates(20) // Get up to 20 recent updates
	
	if len(updates) == 0 {
		return // Nothing to gossip
	}
	
	message := GossipMessage{
		MessageID:    generateMessageID(),
		SenderID:     n.NodeID,
		MessageType:  "STATUS_UPDATE",
		TrainUpdates: updates,
		Timestamp:    time.Now(),
		TTL:          5, // Standard TTL
	}
	
	select {
	case n.outgoingMessages <- message:
		n.metrics.mu.Lock()
		n.metrics.GossipRounds++
		n.metrics.LastGossipTime = time.Now()
		n.metrics.mu.Unlock()
		
		n.logger.Printf("📡 Gossip round %d: %d updates", 
			n.metrics.GossipRounds, len(updates))
	default:
		n.logger.Printf("⚠️ Outgoing queue full, skipping gossip round")
	}
}

// heartbeatLoop sends periodic heartbeats
func (n *ScalableGossipNode) heartbeatLoop() {
	n.heartbeatTicker = time.NewTicker(n.heartbeatInterval)
	defer n.heartbeatTicker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-n.heartbeatTicker.C:
			n.sendHeartbeat()
		}
	}
}

// sendHeartbeat sends heartbeat to all peers
func (n *ScalableGossipNode) sendHeartbeat() {
	heartbeat := GossipMessage{
		MessageID:   generateMessageID(),
		SenderID:    n.NodeID,
		MessageType: "HEARTBEAT",
		Timestamp:   time.Now(),
		TTL:         1, // Heartbeats don't propagate
	}
	
	select {
	case n.outgoingMessages <- heartbeat:
		n.logger.Printf("💓 Sent heartbeat to network")
	default:
		// Don't log heartbeat failures to avoid spam
	}
}

// metricsUpdater updates performance metrics
func (n *ScalableGossipNode) metricsUpdater() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-ticker.C:
			n.updateMetrics()
		}
	}
}

// updateMetrics calculates and updates performance metrics
func (n *ScalableGossipNode) updateMetrics() {
	n.metrics.mu.Lock()
	defer n.metrics.mu.Unlock()
	
	// Calculate network efficiency (simplified)
	if n.metrics.MessagesSent > 0 {
		n.metrics.NetworkEfficiency = float64(n.metrics.StatusUpdates) / float64(n.metrics.MessagesSent)
	}
	
	// Calculate data consistency (simplified)
	n.statusMutex.RLock()
	totalStatuses := len(n.trainStatuses)
	n.statusMutex.RUnlock()
	
	if totalStatuses > 0 {
		// Simplified consistency calculation
		n.metrics.DataConsistency = math.Min(1.0, float64(totalStatuses)/100.0)
	}
}

// Utility functions for the gossip protocol

func (bf *BloomFilter) Add(item string) {
	bf.mu.Lock()
	defer bf.mu.Unlock()
	
	hashes := bf.hashFunc(item)
	for _, hash := range hashes {
		if hash >= 0 && hash < bf.size {
			bf.bitArray[hash] = true
		}
	}
}

func (bf *BloomFilter) Contains(item string) bool {
	bf.mu.RLock()
	defer bf.mu.RUnlock()
	
	hashes := bf.hashFunc(item)
	for _, hash := range hashes {
		if hash >= 0 && hash < bf.size && !bf.bitArray[hash] {
			return false
		}
	}
	return true
}

func (mc *MessageCache) Add(messageID string) {
	mc.mu.Lock()
	defer mc.mu.Unlock()
	
	// Remove oldest entries if cache is full
	if len(mc.cache) >= mc.maxSize {
		oldest := time.Now()
		var oldestKey string
		
		for key, timestamp := range mc.cache {
			if timestamp.Before(oldest) {
				oldest = timestamp
				oldestKey = key
			}
		}
		
		if oldestKey != "" {
			delete(mc.cache, oldestKey)
		}
	}
	
	mc.cache[messageID] = time.Now()
}

func (mc *MessageCache) Contains(messageID string) bool {
	mc.mu.RLock()
	defer mc.mu.RUnlock()
	
	timestamp, exists := mc.cache[messageID]
	if !exists {
		return false
	}
	
	// Check if entry has expired
	if time.Since(timestamp) > mc.ttl {
		// Remove expired entry (will be cleaned up later)
		return false
	}
	
	return true
}

func (mc *MessageCache) cleanup() {
	ticker := time.NewTicker(time.Minute)
	defer ticker.Stop()
	
	for range ticker.C {
		mc.mu.Lock()
		now := time.Now()
		
		for key, timestamp := range mc.cache {
			if now.Sub(timestamp) > mc.ttl {
				delete(mc.cache, key)
			}
		}
		mc.mu.Unlock()
	}
}

func (rl *RateLimiter) Allow() bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	
	now := time.Now()
	elapsed := now.Sub(rl.lastRefill)
	
	// Refill tokens based on elapsed time
	tokensToAdd := int(elapsed / rl.refillRate)
	if tokensToAdd > 0 {
		rl.tokens = min(rl.maxTokens, rl.tokens+tokensToAdd)
		rl.lastRefill = now
	}
	
	if rl.tokens > 0 {
		rl.tokens--
		return true
	}
	
	return false
}

// Utility functions

func (n *ScalableGossipNode) updatePeerInfo(peerID string) {
	n.peersMutex.Lock()
	defer n.peersMutex.Unlock()
	
	if peer, exists := n.peers[peerID]; exists {
		peer.LastSeen = time.Now()
		peer.MessageCount++
		
		// Update reliability based on responsiveness
		timeSinceLastSeen := time.Since(peer.LastSeen)
		if timeSinceLastSeen < time.Minute {
			peer.Reliability = math.Min(1.0, peer.Reliability+0.01)
		}
	}
}

func (n *ScalableGossipNode) sendToPeer(peerID string, msg GossipMessage) {
	// Simulate network transmission delay
	go func() {
		time.Sleep(time.Duration(50+mathRand.Intn(100)) * time.Millisecond)
		
		// In a real implementation, this would send over network
		// For simulation, we just log the sending
		n.logger.Printf("📤 Sent %s to %s (%d updates)", 
			msg.MessageType, peerID, len(msg.TrainUpdates))
	}()
}

// Hash functions for bloom filter
func djb2Hash(data string) uint32 {
	hash := uint32(5381)
	for _, c := range data {
		hash = ((hash << 5) + hash) + uint32(c)
	}
	return hash
}

func sdbmHash(data string) uint32 {
	hash := uint32(0)
	for _, c := range data {
		hash = uint32(c) + (hash << 6) + (hash << 16) - hash
	}
	return hash
}

func fnvHash(data string) uint32 {
	hash := uint32(2166136261)
	for _, c := range data {
		hash ^= uint32(c)
		hash *= 16777619
	}
	return hash
}

func calculateFreshnessWeight(lastSeen time.Time) float64 {
	elapsed := time.Since(lastSeen)
	
	if elapsed < time.Minute {
		return 1.0
	} else if elapsed < 5*time.Minute {
		return 0.8
	} else if elapsed < 15*time.Minute {
		return 0.5
	}
	
	return 0.2
}

func generateMessageID() string {
	bytes := make([]byte, 8)
	rand.Read(bytes)
	return fmt.Sprintf("%x", bytes)
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// GetMetrics returns current node metrics
func (n *ScalableGossipNode) GetMetrics() *NodeMetrics {
	n.metrics.mu.RLock()
	defer n.metrics.mu.RUnlock()
	
	// Create a copy to avoid race conditions
	return &NodeMetrics{
		MessagesReceived:  n.metrics.MessagesReceived,
		MessagesSent:      n.metrics.MessagesSent,
		StatusUpdates:     n.metrics.StatusUpdates,
		GossipRounds:      n.metrics.GossipRounds,
		AverageLatency:    n.metrics.AverageLatency,
		NetworkEfficiency: n.metrics.NetworkEfficiency,
		LastGossipTime:    n.metrics.LastGossipTime,
		ActiveConnections: n.metrics.ActiveConnections,
		DataConsistency:   n.metrics.DataConsistency,
	}
}

// GetTrainStatuses returns current train statuses
func (n *ScalableGossipNode) GetTrainStatuses() map[string]TrainStatus {
	n.statusMutex.RLock()
	defer n.statusMutex.RUnlock()
	
	// Create a copy
	statuses := make(map[string]TrainStatus)
	for k, v := range n.trainStatuses {
		statuses[k] = v
	}
	return statuses
}

// Shutdown gracefully shuts down the node
func (n *ScalableGossipNode) Shutdown() {
	n.logger.Printf("🛑 Shutting down node %s", n.NodeID)
	
	n.cancel()
	
	if n.gossipTicker != nil {
		n.gossipTicker.Stop()
	}
	
	if n.heartbeatTicker != nil {
		n.heartbeatTicker.Stop()
	}
	
	close(n.incomingMessages)
	close(n.outgoingMessages)
}

// Main function demonstrating the scalable gossip network
func main() {
	fmt.Println("🇮🇳 IRCTC Scalable Gossip Network Simulation")
	fmt.Println(strings.Repeat("=", 50))
	
	// Create IRCTC station nodes across India
	nodes := make(map[string]*ScalableGossipNode)
	
	stationData := []struct {
		id, station, region, zone string
	}{
		{"node_001", "CSMT", "West", "WR"},    // Mumbai
		{"node_002", "NDLS", "North", "NR"},   // New Delhi
		{"node_003", "SBC", "South", "SR"},    // Bangalore
		{"node_004", "MAS", "South", "SR"},    // Chennai
		{"node_005", "HWH", "East", "ER"},     // Howrah
		{"node_006", "PUNE", "West", "CR"},    // Pune
		{"node_007", "ADI", "West", "WR"},     // Ahmedabad
		{"node_008", "JP", "North", "NWR"},    // Jaipur
		{"node_009", "LKO", "North", "NER"},   // Lucknow
		{"node_010", "HYB", "South", "SCR"},   // Hyderabad
	}
	
	// Create nodes
	for _, data := range stationData {
		nodes[data.id] = NewScalableGossipNode(data.id, data.station, data.region, data.zone)
	}
	
	// Create network topology (each node connected to 3-5 others)
	connections := []struct {
		from, to string
		distance int
	}{
		// Major route connections
		{"node_001", "node_002", 2}, // Mumbai-Delhi
		{"node_001", "node_006", 1}, // Mumbai-Pune
		{"node_002", "node_008", 1}, // Delhi-Jaipur
		{"node_002", "node_009", 2}, // Delhi-Lucknow
		{"node_003", "node_004", 1}, // Bangalore-Chennai
		{"node_003", "node_010", 1}, // Bangalore-Hyderabad
		{"node_004", "node_005", 3}, // Chennai-Howrah
		{"node_001", "node_007", 2}, // Mumbai-Ahmedabad
		{"node_006", "node_007", 2}, // Pune-Ahmedabad
		{"node_008", "node_009", 2}, // Jaipur-Lucknow
		
		// Cross-zone connections for resilience
		{"node_001", "node_003", 3}, // Mumbai-Bangalore
		{"node_002", "node_005", 3}, // Delhi-Howrah
		{"node_004", "node_010", 2}, // Chennai-Hyderabad
	}
	
	// Establish peer connections
	for _, conn := range connections {
		if fromNode, exists := nodes[conn.from]; exists {
			if toNode, exists := nodes[conn.to]; exists {
				fromNode.AddPeer(&PeerInfo{
					NodeID:      conn.to,
					StationCode: toNode.StationCode,
					Region:      toNode.Region,
					Zone:        toNode.Zone,
					LastSeen:    time.Now(),
					Reliability: 0.9,
					Distance:    conn.distance,
				})
				
				toNode.AddPeer(&PeerInfo{
					NodeID:      conn.from,
					StationCode: fromNode.StationCode,
					Region:      fromNode.Region,
					Zone:        fromNode.Zone,
					LastSeen:    time.Now(),
					Reliability: 0.9,
					Distance:    conn.distance,
				})
			}
		}
	}
	
	fmt.Printf("Created IRCTC network with %d stations\n", len(nodes))
	fmt.Printf("Network connections: %d\n", len(connections))
	
	// Wait for network to stabilize
	time.Sleep(2 * time.Second)
	
	// Simulate train status updates
	trainData := []struct {
		number, name, station, status string
		delay                         int
	}{
		{"12001", "Shatabdi Express", "NDLS", "RUNNING", 0},
		{"12002", "Shatabdi Express", "CSMT", "DELAYED", 15},
		{"12301", "Rajdhani Express", "HWH", "RUNNING", 5},
		{"16339", "Nagarcoil Express", "MAS", "RUNNING", 0},
		{"12049", "Gatimaan Express", "JP", "DELAYED", 25},
		{"12627", "Karnataka Express", "SBC", "CANCELLED", 0},
		{"19019", "Dehradun Express", "LKO", "RUNNING", 10},
		{"17219", "Sabarmati Express", "ADI", "RUNNING", 0},
		{"11301", "Udyan Express", "PUNE", "DELAYED", 30},
		{"12759", "Charminar Express", "HYB", "RUNNING", 8},
	}
	
	fmt.Println("\n🚂 Starting train status simulation...")
	
	// Inject initial statuses
	for i, train := range trainData {
		nodeID := fmt.Sprintf("node_%03d", (i%len(nodes))+1)
		if node, exists := nodes[nodeID]; exists {
			status := TrainStatus{
				TrainNumber:    train.number,
				TrainName:      train.name,
				CurrentStation: train.station,
				DelayMinutes:   train.delay,
				Status:         train.status,
			}
			node.UpdateTrainStatus(status)
		}
		
		time.Sleep(500 * time.Millisecond)
	}
	
	// Let the gossip protocol propagate information
	fmt.Println("📡 Gossip propagation in progress...")
	time.Sleep(10 * time.Second)
	
	// Simulate some dynamic updates
	fmt.Println("\n🔄 Simulating dynamic updates...")
	
	// Simulate delay increase
	nodes["node_002"].UpdateTrainStatus(TrainStatus{
		TrainNumber:    "12002",
		TrainName:      "Shatabdi Express",
		CurrentStation: "CSMT",
		DelayMinutes:   45, // Increased delay
		Status:         "DELAYED",
	})
	
	// Simulate cancellation
	nodes["node_008"].UpdateTrainStatus(TrainStatus{
		TrainNumber:    "12049",
		TrainName:      "Gatimaan Express",
		CurrentStation: "JP",
		DelayMinutes:   0,
		Status:         "CANCELLED",
	})
	
	// Wait for propagation
	time.Sleep(8 * time.Second)
	
	// Print final network statistics
	fmt.Println("\n📊 Final Network Statistics:")
	fmt.Println(strings.Repeat("-", 50))
	
	totalMessages := int64(0)
	totalUpdates := int64(0)
	totalRounds := int64(0)
	
	for nodeID, node := range nodes {
		metrics := node.GetMetrics()
		statuses := node.GetTrainStatuses()
		
		fmt.Printf("Station %s (%s):\n", node.StationCode, nodeID)
		fmt.Printf("  Messages: Sent=%d, Received=%d\n", 
			metrics.MessagesSent, metrics.MessagesReceived)
		fmt.Printf("  Status Updates: %d\n", metrics.StatusUpdates)
		fmt.Printf("  Gossip Rounds: %d\n", metrics.GossipRounds)
		fmt.Printf("  Train Statuses Known: %d\n", len(statuses))
		fmt.Printf("  Network Efficiency: %.2f%%\n", metrics.NetworkEfficiency*100)
		fmt.Printf("  Data Consistency: %.2f%%\n", metrics.DataConsistency*100)
		fmt.Printf("  Active Connections: %d\n", metrics.ActiveConnections)
		fmt.Println()
		
		totalMessages += metrics.MessagesSent + metrics.MessagesReceived
		totalUpdates += metrics.StatusUpdates
		totalRounds += metrics.GossipRounds
	}
	
	fmt.Printf("📈 Network Summary:\n")
	fmt.Printf("  Total messages exchanged: %d\n", totalMessages)
	fmt.Printf("  Total status updates: %d\n", totalUpdates)
	fmt.Printf("  Total gossip rounds: %d\n", totalRounds)
	fmt.Printf("  Average messages per node: %.1f\n", float64(totalMessages)/float64(len(nodes)))
	fmt.Printf("  Network propagation efficiency: %.2f%%\n", 
		float64(totalUpdates)/float64(totalMessages)*100)
	
	// Sample train status convergence check
	fmt.Println("\n🔍 Convergence Analysis:")
	trainStatusCounts := make(map[string]int)
	
	for _, node := range nodes {
		statuses := node.GetTrainStatuses()
		fmt.Printf("  %s knows about %d trains\n", node.StationCode, len(statuses))
		
		for trainNumber := range statuses {
			trainStatusCounts[trainNumber]++
		}
	}
	
	fmt.Println("\n📋 Train Status Distribution:")
	for trainNumber, count := range trainStatusCounts {
		percentage := float64(count) / float64(len(nodes)) * 100
		fmt.Printf("  Train %s: Known by %d/%d nodes (%.1f%%)\n", 
			trainNumber, count, len(nodes), percentage)
	}
	
	// Cleanup
	fmt.Println("\n🛑 Shutting down network...")
	for _, node := range nodes {
		node.Shutdown()
	}
	
	fmt.Println("Scalable gossip network simulation completed!")
}