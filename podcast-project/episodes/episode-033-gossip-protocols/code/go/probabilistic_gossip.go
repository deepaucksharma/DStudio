// Probabilistic Gossip Protocol with Adaptive Parameters
// =====================================================
//
// Swiggy Delivery Partner Network: जब हजारों delivery partners हों तो
// कैसे efficiently order updates को propagate करें probabilistic gossip के साथ?
//
// This implements a probabilistic gossip protocol with adaptive parameters
// that optimize based on network conditions and message importance.
//
// Author: Code Developer Agent
// Episode: 33 - Gossip Protocols

package main

import (
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"strings"
	"sync"
	"time"
)

// DeliveryOrder represents a Swiggy delivery order
type DeliveryOrder struct {
	OrderID        string    `json:"order_id"`
	RestaurantID   string    `json:"restaurant_id"`
	CustomerID     string    `json:"customer_id"`
	DeliveryPartner string   `json:"delivery_partner"`
	Status         string    `json:"status"` // PLACED, PREPARING, READY, PICKED_UP, DELIVERED, CANCELLED
	Priority       int       `json:"priority"` // 1=highest, 5=lowest
	EstimatedTime  int       `json:"estimated_time"` // minutes
	Location       Location  `json:"location"`
	Timestamp      time.Time `json:"timestamp"`
	Version        int64     `json:"version"`
	Source         string    `json:"source"`
}

// Location represents GPS coordinates
type Location struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	Address   string  `json:"address"`
}

// ProbabilisticMessage represents a probabilistic gossip message
type ProbabilisticMessage struct {
	MessageID       string                    `json:"message_id"`
	SenderID        string                    `json:"sender_id"`
	MessageType     string                    `json:"message_type"`
	Orders          map[string]DeliveryOrder  `json:"orders"`
	Timestamp       time.Time                 `json:"timestamp"`
	TTL             int                       `json:"ttl"`
	PropagationProb float64                   `json:"propagation_prob"`
	Checksum        string                    `json:"checksum"`
}

// NetworkConditions tracks current network state
type NetworkConditions struct {
	Congestion      float64   `json:"congestion"`       // 0.0 to 1.0
	AvgLatency      time.Duration `json:"avg_latency"`
	MessageLoss     float64   `json:"message_loss"`     // 0.0 to 1.0
	ActiveNodes     int       `json:"active_nodes"`
	LastUpdated     time.Time `json:"last_updated"`
	mu              sync.RWMutex
}

// AdaptiveParams holds adaptive gossip parameters
type AdaptiveParams struct {
	BaseProbability     float64 `json:"base_probability"`
	PriorityMultiplier  float64 `json:"priority_multiplier"`
	CongestionFactor    float64 `json:"congestion_factor"`
	LatencyThreshold    time.Duration `json:"latency_threshold"`
	FanoutMin          int     `json:"fanout_min"`
	FanoutMax          int     `json:"fanout_max"`
	TTLMin             int     `json:"ttl_min"`
	TTLMax             int     `json:"ttl_max"`
	mu                 sync.RWMutex
}

// GossipMetrics tracks performance metrics
type GossipMetrics struct {
	MessagesGenerated  int64         `json:"messages_generated"`
	MessagesReceived   int64         `json:"messages_received"`
	MessagesPropagated int64         `json:"messages_propagated"`
	MessagesDropped    int64         `json:"messages_dropped"`
	OrderUpdates       int64         `json:"order_updates"`
	LatencySum         time.Duration `json:"latency_sum"`
	LatencyCount       int64         `json:"latency_count"`
	ConvergenceTime    time.Duration `json:"convergence_time"`
	NetworkUtilization float64       `json:"network_utilization"`
	mu                 sync.RWMutex
}

// ProbabilisticGossipNode represents a Swiggy delivery partner node
type ProbabilisticGossipNode struct {
	NodeID          string
	PartnerName     string
	Zone            string
	Location        Location
	
	// Data storage
	orders          map[string]DeliveryOrder
	ordersMutex     sync.RWMutex
	
	// Network topology
	peers           map[string]*PeerConnection
	peersMutex      sync.RWMutex
	
	// Probabilistic gossip parameters
	adaptiveParams  *AdaptiveParams
	netConditions   *NetworkConditions
	
	// Metrics and monitoring
	metrics         *GossipMetrics
	
	// Control
	ctx             context.Context
	cancel          context.CancelFunc
	
	// Message channels
	incomingMsgs    chan ProbabilisticMessage
	outgoingMsgs    chan ProbabilisticMessage
	
	// Timers
	gossipTicker    *time.Ticker
	metricsTicker   *time.Ticker
	adaptiveTicker  *time.Ticker
	
	logger          *log.Logger
}

// PeerConnection represents connection to a peer node
type PeerConnection struct {
	NodeID       string    `json:"node_id"`
	Zone         string    `json:"zone"`
	Location     Location  `json:"location"`
	Distance     float64   `json:"distance"` // kilometers
	Reliability  float64   `json:"reliability"`
	LastContact  time.Time `json:"last_contact"`
	MessageCount int64     `json:"message_count"`
	LatencySum   time.Duration `json:"latency_sum"`
	mu           sync.RWMutex
}

// NewProbabilisticGossipNode creates a new probabilistic gossip node
func NewProbabilisticGossipNode(nodeID, partnerName, zone string, location Location) *ProbabilisticGossipNode {
	ctx, cancel := context.WithCancel(context.Background())
	
	node := &ProbabilisticGossipNode{
		NodeID:      nodeID,
		PartnerName: partnerName,
		Zone:        zone,
		Location:    location,
		
		orders: make(map[string]DeliveryOrder),
		peers:  make(map[string]*PeerConnection),
		
		adaptiveParams: &AdaptiveParams{
			BaseProbability:    0.7,
			PriorityMultiplier: 1.5,
			CongestionFactor:   0.5,
			LatencyThreshold:   100 * time.Millisecond,
			FanoutMin:         2,
			FanoutMax:         6,
			TTLMin:            3,
			TTLMax:            8,
		},
		
		netConditions: &NetworkConditions{
			Congestion:   0.3,
			AvgLatency:   50 * time.Millisecond,
			MessageLoss:  0.05,
			ActiveNodes:  0,
			LastUpdated:  time.Now(),
		},
		
		metrics: &GossipMetrics{},
		
		ctx:    ctx,
		cancel: cancel,
		
		incomingMsgs: make(chan ProbabilisticMessage, 500),
		outgoingMsgs: make(chan ProbabilisticMessage, 500),
		
		logger: log.New(log.Writer(), fmt.Sprintf("[%s] ", nodeID), log.LstdFlags),
	}
	
	// Start background processes
	go node.messageProcessor()
	go node.gossipLoop()
	go node.adaptiveParameterUpdater()
	go node.metricsCollector()
	
	node.logger.Printf("🛵 Swiggy Partner %s started in %s zone", partnerName, zone)
	
	return node
}

// AddPeer adds a peer connection
func (n *ProbabilisticGossipNode) AddPeer(peerID, zone string, location Location) {
	distance := calculateDistance(n.Location, location)
	
	peer := &PeerConnection{
		NodeID:      peerID,
		Zone:        zone,
		Location:    location,
		Distance:    distance,
		Reliability: 0.9, // Initial reliability
		LastContact: time.Now(),
	}
	
	n.peersMutex.Lock()
	n.peers[peerID] = peer
	n.peersMutex.Unlock()
	
	n.netConditions.mu.Lock()
	n.netConditions.ActiveNodes = len(n.peers) + 1
	n.netConditions.mu.Unlock()
	
	n.logger.Printf("🔗 Added peer %s (%.2f km away)", peerID, distance)
}

// UpdateOrder updates or creates a delivery order
func (n *ProbabilisticGossipNode) UpdateOrder(order DeliveryOrder) {
	order.Source = n.NodeID
	order.Timestamp = time.Now()
	order.Version = time.Now().UnixNano()
	
	n.ordersMutex.Lock()
	n.orders[order.OrderID] = order
	n.ordersMutex.Unlock()
	
	n.logger.Printf("📦 Order %s updated: %s (Priority: %d)", 
		order.OrderID, order.Status, order.Priority)
	
	// Calculate propagation probability based on order priority and network conditions
	propagationProb := n.calculatePropagationProbability(order)
	
	// Create gossip message
	message := ProbabilisticMessage{
		MessageID:       generateMessageID(),
		SenderID:        n.NodeID,
		MessageType:     "ORDER_UPDATE",
		Orders:          map[string]DeliveryOrder{order.OrderID: order},
		Timestamp:       time.Now(),
		TTL:             n.calculateTTL(order),
		PropagationProb: propagationProb,
	}
	
	// Queue for gossip
	select {
	case n.outgoingMsgs <- message:
		n.metrics.mu.Lock()
		n.metrics.MessagesGenerated++
		n.metrics.mu.Unlock()
	default:
		n.logger.Printf("⚠️ Outgoing queue full, dropping order update")
	}
}

// calculatePropagationProbability calculates adaptive propagation probability
func (n *ProbabilisticGossipNode) calculatePropagationProbability(order DeliveryOrder) float64 {
	n.adaptiveParams.mu.RLock()
	params := *n.adaptiveParams
	n.adaptiveParams.mu.RUnlock()
	
	n.netConditions.mu.RLock()
	conditions := *n.netConditions
	n.netConditions.mu.RUnlock()
	
	// Base probability
	prob := params.BaseProbability
	
	// Priority adjustment (higher priority = higher probability)
	priorityFactor := params.PriorityMultiplier * (6.0 - float64(order.Priority)) / 5.0
	prob *= priorityFactor
	
	// Network congestion adjustment
	congestionAdjustment := 1.0 - (conditions.Congestion * params.CongestionFactor)
	prob *= congestionAdjustment
	
	// Latency adjustment
	if conditions.AvgLatency > params.LatencyThreshold {
		latencyFactor := 1.0 - (float64(conditions.AvgLatency-params.LatencyThreshold) / float64(params.LatencyThreshold))
		prob *= math.Max(0.1, latencyFactor)
	}
	
	// Message loss adjustment
	lossAdjustment := 1.0 + conditions.MessageLoss
	prob *= lossAdjustment
	
	// Ensure probability is within bounds
	return math.Max(0.1, math.Min(1.0, prob))
}

// calculateTTL calculates adaptive TTL based on message importance and network conditions
func (n *ProbabilisticGossipNode) calculateTTL(order DeliveryOrder) int {
	n.adaptiveParams.mu.RLock()
	params := *n.adaptiveParams
	n.adaptiveParams.mu.RUnlock()
	
	// Base TTL based on priority
	baseTTL := params.TTLMax - order.Priority + 1
	
	// Adjust based on network size
	n.netConditions.mu.RLock()
	networkSize := n.netConditions.ActiveNodes
	n.netConditions.mu.RUnlock()
	
	// Larger networks need higher TTL for propagation
	networkFactor := int(math.Log(float64(networkSize)) + 1)
	adjustedTTL := baseTTL + networkFactor
	
	// Ensure TTL is within bounds
	if adjustedTTL < params.TTLMin {
		return params.TTLMin
	}
	if adjustedTTL > params.TTLMax {
		return params.TTLMax
	}
	
	return adjustedTTL
}

// messageProcessor handles incoming and outgoing messages
func (n *ProbabilisticGossipNode) messageProcessor() {
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case msg := <-n.incomingMsgs:
			n.processIncomingMessage(msg)
			
		case msg := <-n.outgoingMsgs:
			n.processOutgoingMessage(msg)
		}
	}
}

// processIncomingMessage processes received gossip messages
func (n *ProbabilisticGossipNode) processIncomingMessage(msg ProbabilisticMessage) {
	startTime := time.Now()
	
	n.metrics.mu.Lock()
	n.metrics.MessagesReceived++
	n.metrics.mu.Unlock()
	
	// Update peer information
	n.updatePeerInfo(msg.SenderID, time.Since(startTime))
	
	// Process order updates
	updatedOrders := 0
	n.ordersMutex.Lock()
	for orderID, newOrder := range msg.Orders {
		existingOrder, exists := n.orders[orderID]
		
		if !exists || newOrder.Version > existingOrder.Version {
			n.orders[orderID] = newOrder
			updatedOrders++
			
			n.logger.Printf("📥 Received order update %s: %s", orderID, newOrder.Status)
		}
	}
	n.ordersMutex.Unlock()
	
	if updatedOrders > 0 {
		n.metrics.mu.Lock()
		n.metrics.OrderUpdates += int64(updatedOrders)
		n.metrics.mu.Unlock()
	}
	
	// Probabilistically forward the message
	if msg.TTL > 0 && updatedOrders > 0 {
		n.probabilisticForward(msg, float64(updatedOrders))
	}
}

// probabilisticForward forwards message based on probability
func (n *ProbabilisticGossipNode) probabilisticForward(msg ProbabilisticMessage, relevanceFactor float64) {
	// Adjust propagation probability based on relevance
	adjustedProb := msg.PropagationProb * math.Min(2.0, 1.0+relevanceFactor/10.0)
	
	// Make probabilistic decision
	if rand.Float64() > adjustedProb {
		return // Don't forward
	}
	
	// Create forwarded message
	forwardedMsg := ProbabilisticMessage{
		MessageID:       generateMessageID(),
		SenderID:        n.NodeID,
		MessageType:     "FORWARDED_UPDATE",
		Orders:          msg.Orders,
		Timestamp:       time.Now(),
		TTL:             msg.TTL - 1,
		PropagationProb: adjustedProb * 0.9, // Slightly reduce probability
	}
	
	select {
	case n.outgoingMsgs <- forwardedMsg:
		n.metrics.mu.Lock()
		n.metrics.MessagesPropagated++
		n.metrics.mu.Unlock()
		
		n.logger.Printf("↪️ Forwarded message (prob: %.2f, TTL: %d)", 
			adjustedProb, forwardedMsg.TTL)
	default:
		n.metrics.mu.Lock()
		n.metrics.MessagesDropped++
		n.metrics.mu.Unlock()
	}
}

// processOutgoingMessage sends messages to selected peers
func (n *ProbabilisticGossipNode) processOutgoingMessage(msg ProbabilisticMessage) {
	selectedPeers := n.selectProbabilisticPeers(msg)
	
	for _, peerID := range selectedPeers {
		n.sendToPeer(peerID, msg)
	}
}

// selectProbabilisticPeers selects peers based on probabilistic criteria
func (n *ProbabilisticGossipNode) selectProbabilisticPeers(msg ProbabilisticMessage) []string {
	n.peersMutex.RLock()
	defer n.peersMutex.RUnlock()
	
	if len(n.peers) == 0 {
		return nil
	}
	
	n.adaptiveParams.mu.RLock()
	params := *n.adaptiveParams
	n.adaptiveParams.mu.RUnlock()
	
	// Calculate adaptive fanout
	fanout := n.calculateAdaptiveFanout(msg)
	
	// Create weighted peer selection
	type weightedPeer struct {
		peerID string
		weight float64
	}
	
	var candidates []weightedPeer
	
	for peerID, peer := range n.peers {
		peer.mu.RLock()
		
		// Calculate selection weight
		weight := n.calculatePeerWeight(peer, msg)
		
		candidates = append(candidates, weightedPeer{
			peerID: peerID,
			weight: weight,
		})
		
		peer.mu.RUnlock()
	}
	
	// Sort by weight (descending)
	for i := 0; i < len(candidates)-1; i++ {
		for j := i + 1; j < len(candidates); j++ {
			if candidates[i].weight < candidates[j].weight {
				candidates[i], candidates[j] = candidates[j], candidates[i]
			}
		}
	}
	
	// Select peers probabilistically with bias towards higher weights
	var selected []string
	for i, candidate := range candidates {
		if len(selected) >= fanout {
			break
		}
		
		// Higher weight = higher selection probability
		selectionProb := candidate.weight * (1.0 - float64(i)*0.1)
		
		if rand.Float64() < selectionProb {
			selected = append(selected, candidate.peerID)
		}
	}
	
	// Ensure minimum fanout if possible
	if len(selected) < params.FanoutMin && len(candidates) >= params.FanoutMin {
		for i := 0; i < params.FanoutMin && i < len(candidates); i++ {
			peerID := candidates[i].peerID
			found := false
			for _, selectedID := range selected {
				if selectedID == peerID {
					found = true
					break
				}
			}
			if !found {
				selected = append(selected, peerID)
			}
		}
	}
	
	return selected
}

// calculateAdaptiveFanout calculates adaptive fanout based on message and network conditions
func (n *ProbabilisticGossipNode) calculateAdaptiveFanout(msg ProbabilisticMessage) int {
	n.adaptiveParams.mu.RLock()
	params := *n.adaptiveParams
	n.adaptiveParams.mu.RUnlock()
	
	n.netConditions.mu.RLock()
	conditions := *n.netConditions
	n.netConditions.mu.RUnlock()
	
	// Base fanout
	baseFanout := (params.FanoutMin + params.FanoutMax) / 2
	
	// Adjust based on message priority (higher priority = higher fanout)
	priorityFactor := 1.0
	if len(msg.Orders) > 0 {
		totalPriority := 0
		for _, order := range msg.Orders {
			totalPriority += order.Priority
		}
		avgPriority := float64(totalPriority) / float64(len(msg.Orders))
		priorityFactor = (6.0 - avgPriority) / 3.0 // Scale to ~0.5-2.0
	}
	
	// Adjust based on network congestion (less fanout when congested)
	congestionFactor := 1.0 - conditions.Congestion*0.5
	
	// Adjust based on network size (larger networks may need more fanout)
	sizeFactor := math.Min(2.0, math.Log(float64(conditions.ActiveNodes))/3.0)
	
	adjustedFanout := int(float64(baseFanout) * priorityFactor * congestionFactor * sizeFactor)
	
	// Ensure within bounds
	if adjustedFanout < params.FanoutMin {
		return params.FanoutMin
	}
	if adjustedFanout > params.FanoutMax {
		return params.FanoutMax
	}
	
	return adjustedFanout
}

// calculatePeerWeight calculates selection weight for a peer
func (n *ProbabilisticGossipNode) calculatePeerWeight(peer *PeerConnection, msg ProbabilisticMessage) float64 {
	// Base weight from reliability
	weight := peer.Reliability
	
	// Distance factor (closer peers preferred for efficiency)
	distanceFactor := 1.0 / (1.0 + peer.Distance/10.0)
	weight *= distanceFactor
	
	// Zone factor (same zone gets slight preference)
	zoneFactor := 1.0
	if peer.Zone == n.Zone {
		zoneFactor = 1.2
	}
	weight *= zoneFactor
	
	// Recent contact factor
	timeSinceContact := time.Since(peer.LastContact)
	contactFactor := 1.0
	if timeSinceContact < time.Minute {
		contactFactor = 1.3 // Recent contact is good
	} else if timeSinceContact > 10*time.Minute {
		contactFactor = 0.7 // Old contact is less preferred
	}
	weight *= contactFactor
	
	// Latency factor
	if peer.MessageCount > 0 {
		avgLatency := peer.LatencySum / time.Duration(peer.MessageCount)
		if avgLatency < 100*time.Millisecond {
			weight *= 1.2 // Fast peer
		} else if avgLatency > 500*time.Millisecond {
			weight *= 0.8 // Slow peer
		}
	}
	
	return math.Max(0.1, math.Min(2.0, weight))
}

// gossipLoop performs regular probabilistic gossip rounds
func (n *ProbabilisticGossipNode) gossipLoop() {
	n.gossipTicker = time.NewTicker(3 * time.Second)
	defer n.gossipTicker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-n.gossipTicker.C:
			n.performProbabilisticGossip()
		}
	}
}

// performProbabilisticGossip performs one round of probabilistic gossip
func (n *ProbabilisticGossipNode) performProbabilisticGossip() {
	// Get recent order updates
	recentOrders := n.getRecentOrders(10)
	
	if len(recentOrders) == 0 {
		return
	}
	
	// Calculate average propagation probability for the batch
	avgPriority := 0.0
	for _, order := range recentOrders {
		avgPriority += float64(order.Priority)
	}
	avgPriority /= float64(len(recentOrders))
	
	// Create dummy order for probability calculation
	dummyOrder := DeliveryOrder{Priority: int(avgPriority)}
	propagationProb := n.calculatePropagationProbability(dummyOrder)
	
	message := ProbabilisticMessage{
		MessageID:       generateMessageID(),
		SenderID:        n.NodeID,
		MessageType:     "BATCH_UPDATE",
		Orders:          recentOrders,
		Timestamp:       time.Now(),
		TTL:             n.calculateTTL(dummyOrder),
		PropagationProb: propagationProb,
	}
	
	select {
	case n.outgoingMsgs <- message:
		n.logger.Printf("📡 Probabilistic gossip: %d orders (prob: %.2f)", 
			len(recentOrders), propagationProb)
	default:
		n.logger.Printf("⚠️ Gossip queue full, skipping round")
	}
}

// getRecentOrders returns recent order updates
func (n *ProbabilisticGossipNode) getRecentOrders(limit int) map[string]DeliveryOrder {
	n.ordersMutex.RLock()
	defer n.ordersMutex.RUnlock()
	
	recentOrders := make(map[string]DeliveryOrder)
	count := 0
	
	cutoffTime := time.Now().Add(-5 * time.Minute)
	
	for orderID, order := range n.orders {
		if count >= limit {
			break
		}
		
		if order.Timestamp.After(cutoffTime) {
			recentOrders[orderID] = order
			count++
		}
	}
	
	return recentOrders
}

// adaptiveParameterUpdater updates adaptive parameters based on network conditions
func (n *ProbabilisticGossipNode) adaptiveParameterUpdater() {
	n.adaptiveTicker = time.NewTicker(30 * time.Second)
	defer n.adaptiveTicker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-n.adaptiveTicker.C:
			n.updateAdaptiveParameters()
		}
	}
}

// updateAdaptiveParameters adjusts parameters based on observed network performance
func (n *ProbabilisticGossipNode) updateAdaptiveParameters() {
	n.metrics.mu.RLock()
	metrics := *n.metrics
	n.metrics.mu.RUnlock()
	
	n.netConditions.mu.Lock()
	defer n.netConditions.mu.Unlock()
	
	// Update network conditions
	if metrics.LatencyCount > 0 {
		n.netConditions.AvgLatency = metrics.LatencySum / time.Duration(metrics.LatencyCount)
	}
	
	// Update congestion based on message drop rate
	if metrics.MessagesGenerated > 0 {
		dropRate := float64(metrics.MessagesDropped) / float64(metrics.MessagesGenerated)
		n.netConditions.Congestion = math.Min(1.0, dropRate*2.0)
	}
	
	// Update message loss estimation
	if metrics.MessagesSent > 0 {
		deliveryRate := float64(metrics.MessagesReceived) / float64(metrics.MessagesSent)
		n.netConditions.MessageLoss = math.Max(0.0, 1.0-deliveryRate)
	}
	
	n.netConditions.LastUpdated = time.Now()
	
	// Adjust adaptive parameters
	n.adaptiveParams.mu.Lock()
	defer n.adaptiveParams.mu.Unlock()
	
	// Adjust base probability based on performance
	if n.netConditions.Congestion > 0.7 {
		n.adaptiveParams.BaseProbability = math.Max(0.3, n.adaptiveParams.BaseProbability*0.95)
	} else if n.netConditions.Congestion < 0.3 {
		n.adaptiveParams.BaseProbability = math.Min(0.9, n.adaptiveParams.BaseProbability*1.05)
	}
	
	// Adjust fanout based on network size and performance
	if n.netConditions.ActiveNodes > 20 && n.netConditions.Congestion > 0.5 {
		n.adaptiveParams.FanoutMax = math.Max(3, n.adaptiveParams.FanoutMax-1)
	} else if n.netConditions.ActiveNodes < 10 {
		n.adaptiveParams.FanoutMax = math.Min(8, n.adaptiveParams.FanoutMax+1)
	}
}

// Utility functions

func (n *ProbabilisticGossipNode) updatePeerInfo(peerID string, latency time.Duration) {
	n.peersMutex.Lock()
	defer n.peersMutex.Unlock()
	
	if peer, exists := n.peers[peerID]; exists {
		peer.mu.Lock()
		peer.LastContact = time.Now()
		peer.MessageCount++
		peer.LatencySum += latency
		
		// Update reliability based on consistent communication
		timeSinceLastContact := time.Since(peer.LastContact)
		if timeSinceLastContact < time.Minute {
			peer.Reliability = math.Min(1.0, peer.Reliability+0.01)
		} else if timeSinceLastContact > 5*time.Minute {
			peer.Reliability = math.Max(0.1, peer.Reliability-0.01)
		}
		
		peer.mu.Unlock()
	}
}

func (n *ProbabilisticGossipNode) sendToPeer(peerID string, msg ProbabilisticMessage) {
	// Simulate network transmission
	go func() {
		// Simulate network latency
		latency := time.Duration(30+rand.Intn(100)) * time.Millisecond
		time.Sleep(latency)
		
		// Update metrics
		n.metrics.mu.Lock()
		n.metrics.LatencySum += latency
		n.metrics.LatencyCount++
		n.metrics.mu.Unlock()
		
		n.logger.Printf("📤 Sent %s to %s (%d orders)", 
			msg.MessageType, peerID, len(msg.Orders))
	}()
}

func (n *ProbabilisticGossipNode) metricsCollector() {
	n.metricsTicker = time.NewTicker(60 * time.Second)
	defer n.metricsTicker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-n.metricsTicker.C:
			n.logMetrics()
		}
	}
}

func (n *ProbabilisticGossipNode) logMetrics() {
	n.metrics.mu.RLock()
	metrics := *n.metrics
	n.metrics.mu.RUnlock()
	
	n.netConditions.mu.RLock()
	conditions := *n.netConditions
	n.netConditions.mu.RUnlock()
	
	n.adaptiveParams.mu.RLock()
	params := *n.adaptiveParams
	n.adaptiveParams.mu.RUnlock()
	
	if metrics.LatencyCount > 0 {
		avgLatency := metrics.LatencySum / time.Duration(metrics.LatencyCount)
		
		n.logger.Printf("📊 Metrics: Msg(Gen:%d,Rcv:%d,Prop:%d,Drop:%d) Lat:%.0fms Cong:%.2f Prob:%.2f", 
			metrics.MessagesGenerated, metrics.MessagesReceived, 
			metrics.MessagesPropagated, metrics.MessagesDropped,
			avgLatency.Seconds()*1000, conditions.Congestion, params.BaseProbability)
	}
}

// calculateDistance calculates distance between two locations (simplified)
func calculateDistance(loc1, loc2 Location) float64 {
	// Simplified distance calculation (Euclidean distance scaled)
	latDiff := loc1.Latitude - loc2.Latitude
	lonDiff := loc1.Longitude - loc2.Longitude
	return math.Sqrt(latDiff*latDiff+lonDiff*lonDiff) * 111.0 // Approximate km per degree
}

func generateMessageID() string {
	bytes := make([]byte, 8)
	rand.Read(bytes)
	return fmt.Sprintf("%x", bytes)
}

// GetMetrics returns current metrics
func (n *ProbabilisticGossipNode) GetMetrics() *GossipMetrics {
	n.metrics.mu.RLock()
	defer n.metrics.mu.RUnlock()
	
	return &GossipMetrics{
		MessagesGenerated:  n.metrics.MessagesGenerated,
		MessagesReceived:   n.metrics.MessagesReceived,
		MessagesPropagated: n.metrics.MessagesPropagated,
		MessagesDropped:    n.metrics.MessagesDropped,
		OrderUpdates:       n.metrics.OrderUpdates,
		LatencySum:         n.metrics.LatencySum,
		LatencyCount:       n.metrics.LatencyCount,
		ConvergenceTime:    n.metrics.ConvergenceTime,
		NetworkUtilization: n.metrics.NetworkUtilization,
	}
}

// GetOrders returns current orders
func (n *ProbabilisticGossipNode) GetOrders() map[string]DeliveryOrder {
	n.ordersMutex.RLock()
	defer n.ordersMutex.RUnlock()
	
	orders := make(map[string]DeliveryOrder)
	for k, v := range n.orders {
		orders[k] = v
	}
	return orders
}

// Shutdown gracefully shuts down the node
func (n *ProbabilisticGossipNode) Shutdown() {
	n.logger.Printf("🛑 Shutting down probabilistic gossip node %s", n.NodeID)
	
	n.cancel()
	
	if n.gossipTicker != nil {
		n.gossipTicker.Stop()
	}
	if n.metricsTicker != nil {
		n.metricsTicker.Stop()
	}
	if n.adaptiveTicker != nil {
		n.adaptiveTicker.Stop()
	}
	
	close(n.incomingMsgs)
	close(n.outgoingMsgs)
}

// Main function demonstrating probabilistic gossip
func main() {
	fmt.Println("🇮🇳 Swiggy Probabilistic Gossip Protocol Simulation")
	fmt.Println(strings.Repeat("=", 55))
	
	// Create Swiggy delivery partner nodes in Mumbai
	nodes := make(map[string]*ProbabilisticGossipNode)
	
	partnerData := []struct {
		id, name, zone string
		location       Location
	}{
		{"partner_001", "Rajesh", "Bandra", Location{19.0596, 72.8295, "Bandra West"}},
		{"partner_002", "Amit", "Andheri", Location{19.1136, 72.8697, "Andheri East"}},
		{"partner_003", "Vikash", "Borivali", Location{19.2307, 72.8567, "Borivali West"}},
		{"partner_004", "Suresh", "Thane", Location{19.2183, 72.9781, "Thane West"}},
		{"partner_005", "Ravi", "Mulund", Location{19.1722, 72.9566, "Mulund East"}},
		{"partner_006", "Deepak", "Ghatkopar", Location{19.0863, 72.9081, "Ghatkopar East"}},
		{"partner_007", "Prakash", "Kurla", Location{19.0728, 72.8826, "Kurla East"}},
		{"partner_008", "Mahesh", "Dadar", Location{19.0178, 72.8478, "Dadar East"}},
		{"partner_009", "Satish", "Powai", Location{19.1176, 72.9060, "Powai"}},
		{"partner_010", "Ramesh", "Worli", Location{19.0176, 72.8170, "Worli"}},
	}
	
	// Create nodes
	for _, data := range partnerData {
		nodes[data.id] = NewProbabilisticGossipNode(data.id, data.name, data.zone, data.location)
	}
	
	// Create network topology based on geographical proximity
	for id1, node1 := range nodes {
		for id2, node2 := range nodes {
			if id1 != id2 {
				distance := calculateDistance(node1.Location, node2.Location)
				// Connect nodes within 15km of each other
				if distance <= 15.0 {
					node1.AddPeer(id2, node2.Zone, node2.Location)
				}
			}
		}
	}
	
	fmt.Printf("Created Swiggy network with %d delivery partners\n", len(nodes))
	
	// Wait for network to stabilize
	time.Sleep(2 * time.Second)
	
	// Simulate delivery orders
	restaurantData := []struct {
		id, name string
	}{
		{"REST_001", "McDonald's Bandra"},
		{"REST_002", "Domino's Andheri"},
		{"REST_003", "KFC Borivali"},
		{"REST_004", "Pizza Hut Thane"},
		{"REST_005", "Burger King Mulund"},
		{"REST_006", "Subway Ghatkopar"},
		{"REST_007", "Zomato Kitchen Kurla"},
		{"REST_008", "Cafe Coffee Day Dadar"},
		{"REST_009", "Starbucks Powai"},
		{"REST_010", "Haldiram's Worli"},
	}
	
	orderStatuses := []string{"PLACED", "PREPARING", "READY", "PICKED_UP", "DELIVERED"}
	
	fmt.Println("\n🍔 Starting order simulation...")
	
	// Generate initial orders
	for i := 0; i < 20; i++ {
		partnerID := fmt.Sprintf("partner_%03d", (i%len(nodes))+1)
		restaurant := restaurantData[i%len(restaurantData)]
		
		if node, exists := nodes[partnerID]; exists {
			order := DeliveryOrder{
				OrderID:         fmt.Sprintf("ORD_%06d", i+1),
				RestaurantID:    restaurant.id,
				CustomerID:      fmt.Sprintf("CUST_%04d", (i%100)+1),
				DeliveryPartner: partnerID,
				Status:          orderStatuses[i%len(orderStatuses)],
				Priority:        (i%5)+1, // Priority 1-5
				EstimatedTime:   20 + (i%30),
				Location:        node.Location,
			}
			
			node.UpdateOrder(order)
		}
		
		time.Sleep(300 * time.Millisecond)
	}
	
	// Let probabilistic gossip propagate
	fmt.Println("📡 Probabilistic gossip propagation in progress...")
	time.Sleep(15 * time.Second)
	
	// Simulate some high-priority updates
	fmt.Println("\n🚨 Simulating high-priority order updates...")
	
	// Urgent delivery
	nodes["partner_001"].UpdateOrder(DeliveryOrder{
		OrderID:         "ORD_URGENT_001",
		RestaurantID:    "REST_001",
		CustomerID:      "CUST_VIP_001",
		DeliveryPartner: "partner_001",
		Status:          "PICKED_UP",
		Priority:        1, // Highest priority
		EstimatedTime:   5,
		Location:        nodes["partner_001"].Location,
	})
	
	// Order cancellation
	nodes["partner_005"].UpdateOrder(DeliveryOrder{
		OrderID:         "ORD_000015",
		RestaurantID:    "REST_005",
		CustomerID:      "CUST_0015",
		DeliveryPartner: "partner_005",
		Status:          "CANCELLED",
		Priority:        2,
		EstimatedTime:   0,
		Location:        nodes["partner_005"].Location,
	})
	
	// Wait for propagation
	time.Sleep(10 * time.Second)
	
	// Print final statistics
	fmt.Println("\n📊 Final Probabilistic Gossip Statistics:")
	fmt.Println(strings.Repeat("-", 60))
	
	totalGenerated := int64(0)
	totalReceived := int64(0)
	totalPropagated := int64(0)
	totalDropped := int64(0)
	totalOrders := int64(0)
	
	for partnerID, node := range nodes {
		metrics := node.GetMetrics()
		orders := node.GetOrders()
		
		avgLatency := time.Duration(0)
		if metrics.LatencyCount > 0 {
			avgLatency = metrics.LatencySum / time.Duration(metrics.LatencyCount)
		}
		
		fmt.Printf("%s (%s):\n", node.PartnerName, partnerID)
		fmt.Printf("  Orders Known: %d\n", len(orders))
		fmt.Printf("  Messages: Gen=%d, Rcv=%d, Prop=%d, Drop=%d\n", 
			metrics.MessagesGenerated, metrics.MessagesReceived, 
			metrics.MessagesPropagated, metrics.MessagesDropped)
		fmt.Printf("  Avg Latency: %.0fms\n", avgLatency.Seconds()*1000)
		fmt.Printf("  Order Updates: %d\n", metrics.OrderUpdates)
		fmt.Println()
		
		totalGenerated += metrics.MessagesGenerated
		totalReceived += metrics.MessagesReceived
		totalPropagated += metrics.MessagesPropagated
		totalDropped += metrics.MessagesDropped
		totalOrders += int64(len(orders))
	}
	
	fmt.Printf("📈 Network Summary:\n")
	fmt.Printf("  Total messages generated: %d\n", totalGenerated)
	fmt.Printf("  Total messages received: %d\n", totalReceived)
	fmt.Printf("  Total messages propagated: %d\n", totalPropagated)
	fmt.Printf("  Total messages dropped: %d\n", totalDropped)
	fmt.Printf("  Total orders tracked: %d\n", totalOrders)
	
	if totalGenerated > 0 {
		efficiency := float64(totalReceived) / float64(totalGenerated) * 100
		fmt.Printf("  Network efficiency: %.2f%%\n", efficiency)
		
		dropRate := float64(totalDropped) / float64(totalGenerated) * 100
		fmt.Printf("  Message drop rate: %.2f%%\n", dropRate)
	}
	
	fmt.Printf("  Average orders per partner: %.1f\n", float64(totalOrders)/float64(len(nodes)))
	
	// Order convergence analysis
	fmt.Println("\n🔍 Order Convergence Analysis:")
	orderCounts := make(map[string]int)
	
	for _, node := range nodes {
		orders := node.GetOrders()
		for orderID := range orders {
			orderCounts[orderID]++
		}
	}
	
	fmt.Println("Order distribution across partners:")
	convergenceCount := 0
	for orderID, count := range orderCounts {
		percentage := float64(count) / float64(len(nodes)) * 100
		if percentage >= 80.0 {
			convergenceCount++
		}
		
		if len(orderID) <= 15 {
			fmt.Printf("  %s: %d/%d partners (%.1f%%)\n", 
				orderID, count, len(nodes), percentage)
		}
	}
	
	convergenceRate := float64(convergenceCount) / float64(len(orderCounts)) * 100
	fmt.Printf("\nConvergence rate (≥80%% propagation): %.1f%% (%d/%d orders)\n", 
		convergenceRate, convergenceCount, len(orderCounts))
	
	// Cleanup
	fmt.Println("\n🛑 Shutting down network...")
	for _, node := range nodes {
		node.Shutdown()
	}
	
	fmt.Println("Probabilistic gossip simulation completed!")
}