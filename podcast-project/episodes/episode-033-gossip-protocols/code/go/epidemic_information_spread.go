// Epidemic Information Spread using Gossip Protocol  
// =================================================
//
// JioMart Supply Chain Alert System: जब कोई important alert या stock update हो
// तो कैसे epidemic model के साथ efficiently सभी warehouses तक पहुंचाएं?
//
// This implements an epidemic-style information dissemination system
// that models information spread like disease propagation.
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

// EpidemicState represents the state of a node in epidemic model
type EpidemicState int

const (
	Susceptible EpidemicState = iota // अभी तक information नहीं मिली
	Infected                        // Information मिल गई, अब spread कर रहा
	Recovered                       // Information spread कर चुका, अब inactive
	Immune                          // Immune to certain types of information
)

func (s EpidemicState) String() string {
	switch s {
	case Susceptible:
		return "SUSCEPTIBLE"
	case Infected:
		return "INFECTED"
	case Recovered:
		return "RECOVERED"
	case Immune:
		return "IMMUNE"
	default:
		return "UNKNOWN"
	}
}

// AlertType represents different types of supply chain alerts
type AlertType int

const (
	StockAlert AlertType = iota
	QualityAlert
	DeliveryAlert
	SupplierAlert
	WeatherAlert
	SecurityAlert
	PriceAlert
)

func (a AlertType) String() string {
	types := []string{"STOCK", "QUALITY", "DELIVERY", "SUPPLIER", "WEATHER", "SECURITY", "PRICE"}
	if int(a) < len(types) {
		return types[a]
	}
	return "UNKNOWN"
}

// SupplyChainAlert represents an alert in the JioMart supply chain
type SupplyChainAlert struct {
	AlertID     string    `json:"alert_id"`
	AlertType   AlertType `json:"alert_type"`
	Severity    int       `json:"severity"` // 1=Critical, 2=High, 3=Medium, 4=Low, 5=Info
	Title       string    `json:"title"`
	Description string    `json:"description"`
	AffectedSKU string    `json:"affected_sku"`
	SourceNode  string    `json:"source_node"`
	Timestamp   time.Time `json:"timestamp"`
	ExpiryTime  time.Time `json:"expiry_time"`
	Version     int64     `json:"version"`
	
	// Epidemic parameters
	InfectionRate   float64 `json:"infection_rate"`   // How easily it spreads
	RecoveryRate    float64 `json:"recovery_rate"`    // How quickly nodes stop spreading
	Immunity        time.Duration `json:"immunity"`   // How long nodes stay immune
	TransmissionRadius int   `json:"transmission_radius"` // How far it can spread
}

// EpidemicMessage represents a message carrying epidemic information
type EpidemicMessage struct {
	MessageID   string                      `json:"message_id"`
	SenderID    string                      `json:"sender_id"`
	MessageType string                      `json:"message_type"`
	Alerts      map[string]SupplyChainAlert `json:"alerts"`
	Timestamp   time.Time                   `json:"timestamp"`
	Generation  int                         `json:"generation"` // How many hops from source
	
	// Epidemic metadata
	InfectionProb float64 `json:"infection_prob"`
	SpreadRadius  int     `json:"spread_radius"`
}

// EpidemicNodeState tracks epidemic state for each alert type
type EpidemicNodeState struct {
	AlertID        string        `json:"alert_id"`
	State          EpidemicState `json:"state"`
	InfectionTime  time.Time     `json:"infection_time"`
	RecoveryTime   time.Time     `json:"recovery_time"`
	ImmunityExpiry time.Time     `json:"immunity_expiry"`
	SpreadCount    int           `json:"spread_count"`
	Generation     int           `json:"generation"`
	mu             sync.RWMutex
}

// EpidemicMetrics tracks epidemic propagation metrics
type EpidemicMetrics struct {
	TotalInfections    int64         `json:"total_infections"`
	TotalRecoveries    int64         `json:"total_recoveries"`
	TotalTransmissions int64         `json:"total_transmissions"`
	AvgSpreadTime      time.Duration `json:"avg_spread_time"`
	PeakInfectionRate  float64       `json:"peak_infection_rate"`
	ConvergenceTime    time.Duration `json:"convergence_time"`
	NetworkCoverage    float64       `json:"network_coverage"`
	EffectiveReproduction float64    `json:"effective_reproduction"` // R_eff
	mu                 sync.RWMutex
}

// EpidemicInformationNode represents a JioMart warehouse/distribution center
type EpidemicInformationNode struct {
	NodeID       string
	WarehouseName string
	Region       string
	Tier         int // 1=DC, 2=Regional, 3=Local
	Capacity     int
	Location     Location
	
	// Epidemic state management
	alertStates     map[string]*EpidemicNodeState
	statesMutex     sync.RWMutex
	
	// Network topology
	neighbors       map[string]*NeighborInfo
	neighborsMutex  sync.RWMutex
	
	// Epidemic parameters
	susceptibility  map[AlertType]float64 // How susceptible to each alert type
	infectiousness  float64               // How infectious this node is
	transmissionRange int                 // Max distance for transmission
	
	// Active alerts
	activeAlerts    map[string]SupplyChainAlert
	alertsMutex     sync.RWMutex
	
	// Metrics
	metrics         *EpidemicMetrics
	
	// Control
	ctx             context.Context
	cancel          context.CancelFunc
	
	// Message processing
	incomingMessages chan EpidemicMessage
	outgoingMessages chan EpidemicMessage
	
	// Epidemic simulation
	epidemicTicker  *time.Ticker
	recoveryTicker  *time.Ticker
	
	logger          *log.Logger
}

// NeighborInfo stores information about neighboring nodes
type NeighborInfo struct {
	NodeID       string    `json:"node_id"`
	Distance     float64   `json:"distance"` // Geographic distance
	LogicalHops  int       `json:"logical_hops"` // Network hops
	Reliability  float64   `json:"reliability"`
	LastContact  time.Time `json:"last_contact"`
	Bandwidth    float64   `json:"bandwidth"` // Message transmission capacity
}

// NewEpidemicInformationNode creates a new epidemic information spread node
func NewEpidemicInformationNode(nodeID, warehouseName, region string, tier int, location Location) *EpidemicInformationNode {
	ctx, cancel := context.WithCancel(context.Background())
	
	node := &EpidemicInformationNode{
		NodeID:        nodeID,
		WarehouseName: warehouseName,
		Region:        region,
		Tier:          tier,
		Location:      location,
		
		alertStates:   make(map[string]*EpidemicNodeState),
		neighbors:     make(map[string]*NeighborInfo),
		activeAlerts:  make(map[string]SupplyChainAlert),
		
		// Initialize susceptibility based on node type
		susceptibility: make(map[AlertType]float64),
		infectiousness: 0.8, // Base infectiousness
		transmissionRange: 3,
		
		metrics: &EpidemicMetrics{},
		
		ctx:    ctx,
		cancel: cancel,
		
		incomingMessages: make(chan EpidemicMessage, 200),
		outgoingMessages: make(chan EpidemicMessage, 200),
		
		logger: log.New(log.Writer(), fmt.Sprintf("[%s] ", nodeID), log.LstdFlags),
	}
	
	// Initialize susceptibility based on node tier
	node.initializeSusceptibility()
	
	// Start epidemic processes
	go node.messageProcessor()
	go node.epidemicSimulation()
	go node.recoveryProcess()
	
	node.logger.Printf("🏪 JioMart %s warehouse started in %s (Tier %d)", 
		warehouseName, region, tier)
	
	return node
}

// initializeSusceptibility sets up susceptibility based on warehouse type
func (n *EpidemicInformationNode) initializeSusceptibility() {
	// Different warehouse tiers have different susceptibilities
	switch n.Tier {
	case 1: // Distribution Center - highly susceptible to all alerts
		n.susceptibility[StockAlert] = 0.9
		n.susceptibility[QualityAlert] = 0.9
		n.susceptibility[DeliveryAlert] = 0.8
		n.susceptibility[SupplierAlert] = 0.9
		n.susceptibility[WeatherAlert] = 0.7
		n.susceptibility[SecurityAlert] = 0.8
		n.susceptibility[PriceAlert] = 0.9
		
	case 2: // Regional Hub - moderate susceptibility
		n.susceptibility[StockAlert] = 0.8
		n.susceptibility[QualityAlert] = 0.7
		n.susceptibility[DeliveryAlert] = 0.9
		n.susceptibility[SupplierAlert] = 0.6
		n.susceptibility[WeatherAlert] = 0.8
		n.susceptibility[SecurityAlert] = 0.7
		n.susceptibility[PriceAlert] = 0.6
		
	case 3: // Local Warehouse - selective susceptibility
		n.susceptibility[StockAlert] = 0.7
		n.susceptibility[QualityAlert] = 0.6
		n.susceptibility[DeliveryAlert] = 0.9
		n.susceptibility[SupplierAlert] = 0.4
		n.susceptibility[WeatherAlert] = 0.9
		n.susceptibility[SecurityAlert] = 0.6
		n.susceptibility[PriceAlert] = 0.4
	}
}

// AddNeighbor adds a neighboring warehouse
func (n *EpidemicInformationNode) AddNeighbor(neighborID string, distance float64, hops int) {
	neighbor := &NeighborInfo{
		NodeID:      neighborID,
		Distance:    distance,
		LogicalHops: hops,
		Reliability: 0.9,
		LastContact: time.Now(),
		Bandwidth:   1.0, // Default bandwidth
	}
	
	n.neighborsMutex.Lock()
	n.neighbors[neighborID] = neighbor
	n.neighborsMutex.Unlock()
	
	n.logger.Printf("🔗 Added neighbor %s (%.1f km, %d hops)", 
		neighborID, distance, hops)
}

// CreateAlert creates and initiates epidemic spread of an alert
func (n *EpidemicInformationNode) CreateAlert(alertType AlertType, severity int, 
	title, description, affectedSKU string, expiryDuration time.Duration) {
	
	alert := SupplyChainAlert{
		AlertID:     generateAlertID(),
		AlertType:   alertType,
		Severity:    severity,
		Title:       title,
		Description: description,
		AffectedSKU: affectedSKU,
		SourceNode:  n.NodeID,
		Timestamp:   time.Now(),
		ExpiryTime:  time.Now().Add(expiryDuration),
		Version:     time.Now().UnixNano(),
		
		// Set epidemic parameters based on severity and type
		InfectionRate:      n.calculateInfectionRate(alertType, severity),
		RecoveryRate:       n.calculateRecoveryRate(alertType, severity),
		Immunity:           n.calculateImmunityDuration(alertType, severity),
		TransmissionRadius: n.calculateTransmissionRadius(alertType, severity),
	}
	
	// Store alert locally
	n.alertsMutex.Lock()
	n.activeAlerts[alert.AlertID] = alert
	n.alertsMutex.Unlock()
	
	// Infect self with the alert
	n.infectWithAlert(alert, 0)
	
	n.logger.Printf("🚨 Created %s alert: %s (Severity: %d)", 
		alertType.String(), title, severity)
	
	// Start epidemic spread
	n.initiateEpidemicSpread(alert)
}

// calculateInfectionRate calculates how infectious an alert should be
func (n *EpidemicInformationNode) calculateInfectionRate(alertType AlertType, severity int) float64 {
	baseRate := 0.5
	
	// Severity multiplier (higher severity = more infectious)
	severityMultiplier := (6.0 - float64(severity)) / 5.0
	
	// Alert type modifiers
	typeModifiers := map[AlertType]float64{
		StockAlert:    1.2, // High spread for stock issues
		QualityAlert:  1.3, // Very high spread for quality issues
		DeliveryAlert: 1.0, // Normal spread for delivery issues
		SupplierAlert: 0.8, // Lower spread for supplier issues
		WeatherAlert:  1.5, // Very high spread for weather alerts
		SecurityAlert: 1.4, // High spread for security alerts
		PriceAlert:    0.9, // Moderate spread for price changes
	}
	
	typeMultiplier := typeModifiers[alertType]
	
	rate := baseRate * severityMultiplier * typeMultiplier
	return math.Max(0.1, math.Min(1.0, rate))
}

// calculateRecoveryRate calculates how quickly nodes stop spreading
func (n *EpidemicInformationNode) calculateRecoveryRate(alertType AlertType, severity int) float64 {
	baseRate := 0.3
	
	// Critical alerts take longer to recover from
	severityFactor := float64(severity) / 5.0
	
	// Some alert types naturally have longer spreading periods
	typeFactors := map[AlertType]float64{
		StockAlert:    0.8, // Stock alerts spread for shorter time
		QualityAlert:  0.6, // Quality alerts spread longer
		DeliveryAlert: 1.0, // Normal recovery
		SupplierAlert: 0.7, // Supplier issues spread longer
		WeatherAlert:  1.2, // Weather alerts resolve faster
		SecurityAlert: 0.5, // Security alerts spread very long
		PriceAlert:    1.1, // Price changes resolve quickly
	}
	
	typeFactor := typeFactors[alertType]
	
	rate := baseRate * severityFactor * typeFactor
	return math.Max(0.1, math.Min(0.8, rate))
}

// calculateImmunityDuration calculates immunity period after recovery
func (n *EpidemicInformationNode) calculateImmunityDuration(alertType AlertType, severity int) time.Duration {
	baseDuration := 10 * time.Minute
	
	// Higher severity leads to longer immunity
	severityMultiplier := (6.0 - float64(severity)) / 2.0
	
	// Alert type affects immunity duration
	typeMultipliers := map[AlertType]float64{
		StockAlert:    1.0,
		QualityAlert:  2.0, // Longer immunity for quality issues
		DeliveryAlert: 0.8,
		SupplierAlert: 1.5,
		WeatherAlert:  0.5, // Short immunity for weather
		SecurityAlert: 3.0, // Very long immunity for security
		PriceAlert:    0.3, // Very short immunity for prices
	}
	
	typeMultiplier := typeMultipliers[alertType]
	
	duration := time.Duration(float64(baseDuration) * severityMultiplier * typeMultiplier)
	return duration
}

// calculateTransmissionRadius calculates how far an alert can spread
func (n *EpidemicInformationNode) calculateTransmissionRadius(alertType AlertType, severity int) int {
	baseRadius := 3
	
	// Critical alerts spread further
	severityBonus := (6 - severity)
	
	// Alert type affects transmission range
	typeBonus := map[AlertType]int{
		StockAlert:    1,
		QualityAlert:  2, // Quality alerts spread very far
		DeliveryAlert: 0,
		SupplierAlert: 1,
		WeatherAlert:  3, // Weather affects large areas
		SecurityAlert: 2, // Security alerts spread far
		PriceAlert:    0,
	}
	
	radius := baseRadius + severityBonus + typeBonus[alertType]
	return int(math.Max(1, math.Min(10, float64(radius))))
}

// infectWithAlert infects the node with an alert
func (n *EpidemicInformationNode) infectWithAlert(alert SupplyChainAlert, generation int) bool {
	alertID := alert.AlertID
	
	n.statesMutex.Lock()
	defer n.statesMutex.Unlock()
	
	// Check if already infected or immune
	if state, exists := n.alertStates[alertID]; exists {
		if state.State == Infected || state.State == Immune {
			return false
		}
	}
	
	// Check susceptibility
	susceptibility := n.susceptibility[alert.AlertType]
	if rand.Float64() > susceptibility {
		return false // Not susceptible
	}
	
	// Create infected state
	infectionState := &EpidemicNodeState{
		AlertID:       alertID,
		State:         Infected,
		InfectionTime: time.Now(),
		Generation:    generation,
	}
	
	// Calculate recovery time based on alert's recovery rate
	recoveryDelay := time.Duration(float64(time.Minute) / alert.RecoveryRate)
	infectionState.RecoveryTime = time.Now().Add(recoveryDelay)
	
	n.alertStates[alertID] = infectionState
	
	n.metrics.mu.Lock()
	n.metrics.TotalInfections++
	n.metrics.mu.Unlock()
	
	n.logger.Printf("🦠 Infected with alert %s (Gen: %d)", 
		alert.Title, generation)
	
	return true
}

// initiateEpidemicSpread starts the epidemic spread process
func (n *EpidemicInformationNode) initiateEpidemicSpread(alert SupplyChainAlert) {
	message := EpidemicMessage{
		MessageID:   generateMessageID(),
		SenderID:    n.NodeID,
		MessageType: "EPIDEMIC_ALERT",
		Alerts:      map[string]SupplyChainAlert{alert.AlertID: alert},
		Timestamp:   time.Now(),
		Generation:  0,
		
		InfectionProb: alert.InfectionRate,
		SpreadRadius:  alert.TransmissionRadius,
	}
	
	select {
	case n.outgoingMessages <- message:
		n.logger.Printf("📤 Initiated epidemic spread for alert %s", alert.AlertID)
	default:
		n.logger.Printf("⚠️ Failed to initiate epidemic spread - queue full")
	}
}

// messageProcessor handles incoming and outgoing epidemic messages
func (n *EpidemicInformationNode) messageProcessor() {
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case msg := <-n.incomingMessages:
			n.processIncomingEpidemicMessage(msg)
			
		case msg := <-n.outgoingMessages:
			n.processOutgoingEpidemicMessage(msg)
		}
	}
}

// processIncomingEpidemicMessage processes received epidemic messages
func (n *EpidemicInformationNode) processIncomingEpidemicMessage(msg EpidemicMessage) {
	// Update neighbor contact information
	n.updateNeighborContact(msg.SenderID)
	
	newInfections := 0
	
	// Process each alert in the message
	for alertID, alert := range msg.Alerts {
		// Check if alert is still valid
		if time.Now().After(alert.ExpiryTime) {
			continue
		}
		
		// Store alert if not known
		n.alertsMutex.Lock()
		if _, exists := n.activeAlerts[alertID]; !exists {
			n.activeAlerts[alertID] = alert
		}
		n.alertsMutex.Unlock()
		
		// Try to get infected
		if n.infectWithAlert(alert, msg.Generation+1) {
			newInfections++
		}
	}
	
	if newInfections > 0 {
		n.logger.Printf("📥 Received epidemic message: %d new infections", newInfections)
		
		// Forward message if within transmission radius
		if msg.Generation < msg.SpreadRadius {
			n.forwardEpidemicMessage(msg)
		}
	}
}

// forwardEpidemicMessage forwards epidemic message to neighbors
func (n *EpidemicInformationNode) forwardEpidemicMessage(msg EpidemicMessage) {
	// Create forwarded message
	forwardedMsg := EpidemicMessage{
		MessageID:     generateMessageID(),
		SenderID:      n.NodeID,
		MessageType:   "FORWARDED_EPIDEMIC",
		Alerts:        msg.Alerts,
		Timestamp:     time.Now(),
		Generation:    msg.Generation + 1,
		InfectionProb: msg.InfectionProb * 0.9, // Slightly reduce infection probability
		SpreadRadius:  msg.SpreadRadius,
	}
	
	select {
	case n.outgoingMessages <- forwardedMsg:
		n.metrics.mu.Lock()
		n.metrics.TotalTransmissions++
		n.metrics.mu.Unlock()
	default:
		n.logger.Printf("⚠️ Failed to forward epidemic message - queue full")
	}
}

// processOutgoingEpidemicMessage sends epidemic messages to neighbors
func (n *EpidemicInformationNode) processOutgoingEpidemicMessage(msg EpidemicMessage) {
	selectedNeighbors := n.selectEpidemicTargets(msg)
	
	for _, neighborID := range selectedNeighbors {
		n.sendEpidemicMessage(neighborID, msg)
	}
}

// selectEpidemicTargets selects neighbors for epidemic transmission
func (n *EpidemicInformationNode) selectEpidemicTargets(msg EpidemicMessage) []string {
	n.neighborsMutex.RLock()
	defer n.neighborsMutex.RUnlock()
	
	if len(n.neighbors) == 0 {
		return nil
	}
	
	var candidates []string
	
	// Select neighbors within transmission radius
	for neighborID, neighbor := range n.neighbors {
		// Check if neighbor is within logical transmission range
		if neighbor.LogicalHops <= msg.SpreadRadius {
			// Probabilistic transmission based on infection probability
			if rand.Float64() < msg.InfectionProb {
				candidates = append(candidates, neighborID)
			}
		}
	}
	
	// Apply additional selection criteria for epidemic spread
	var selected []string
	
	for _, candidateID := range candidates {
		neighbor := n.neighbors[candidateID]
		
		// Distance-based transmission probability
		distanceProb := 1.0 / (1.0 + neighbor.Distance/100.0)
		
		// Reliability-based transmission probability
		reliabilityProb := neighbor.Reliability
		
		// Combined transmission probability
		transmissionProb := distanceProb * reliabilityProb
		
		if rand.Float64() < transmissionProb {
			selected = append(selected, candidateID)
		}
	}
	
	return selected
}

// sendEpidemicMessage sends epidemic message to a specific neighbor
func (n *EpidemicInformationNode) sendEpidemicMessage(neighborID string, msg EpidemicMessage) {
	// Simulate network transmission
	go func() {
		// Simulate transmission delay
		delay := time.Duration(20+rand.Intn(100)) * time.Millisecond
		time.Sleep(delay)
		
		n.logger.Printf("📤 Sent epidemic message to %s (Gen: %d, Alerts: %d)", 
			neighborID, msg.Generation, len(msg.Alerts))
	}()
}

// epidemicSimulation runs the main epidemic simulation loop
func (n *EpidemicInformationNode) epidemicSimulation() {
	n.epidemicTicker = time.NewTicker(2 * time.Second)
	defer n.epidemicTicker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-n.epidemicTicker.C:
			n.performEpidemicRound()
		}
	}
}

// performEpidemicRound performs one round of epidemic simulation
func (n *EpidemicInformationNode) performEpidemicRound() {
	n.statesMutex.RLock()
	var infectedAlerts []string
	
	for alertID, state := range n.alertStates {
		if state.State == Infected {
			infectedAlerts = append(infectedAlerts, alertID)
		}
	}
	n.statesMutex.RUnlock()
	
	if len(infectedAlerts) == 0 {
		return
	}
	
	// Create epidemic message with infected alerts
	n.alertsMutex.RLock()
	alerts := make(map[string]SupplyChainAlert)
	
	for _, alertID := range infectedAlerts {
		if alert, exists := n.activeAlerts[alertID]; exists {
			alerts[alertID] = alert
		}
	}
	n.alertsMutex.RUnlock()
	
	if len(alerts) == 0 {
		return
	}
	
	// Calculate average transmission parameters
	avgInfectionProb := 0.0
	maxSpreadRadius := 0
	
	for _, alert := range alerts {
		avgInfectionProb += alert.InfectionRate
		if alert.TransmissionRadius > maxSpreadRadius {
			maxSpreadRadius = alert.TransmissionRadius
		}
	}
	avgInfectionProb /= float64(len(alerts))
	
	message := EpidemicMessage{
		MessageID:     generateMessageID(),
		SenderID:      n.NodeID,
		MessageType:   "EPIDEMIC_ROUND",
		Alerts:        alerts,
		Timestamp:     time.Now(),
		Generation:    0,
		InfectionProb: avgInfectionProb,
		SpreadRadius:  maxSpreadRadius,
	}
	
	select {
	case n.outgoingMessages <- message:
		n.logger.Printf("🦠 Epidemic round: spreading %d alerts", len(alerts))
	default:
		// Queue full, skip this round
	}
}

// recoveryProcess handles recovery from epidemic states
func (n *EpidemicInformationNode) recoveryProcess() {
	n.recoveryTicker = time.NewTicker(10 * time.Second)
	defer n.recoveryTicker.Stop()
	
	for {
		select {
		case <-n.ctx.Done():
			return
			
		case <-n.recoveryTicker.C:
			n.processRecoveries()
		}
	}
}

// processRecoveries processes state transitions for epidemic recovery
func (n *EpidemicInformationNode) processRecoveries() {
	currentTime := time.Now()
	recoveries := 0
	immunities := 0
	
	n.statesMutex.Lock()
	for alertID, state := range n.alertStates {
		switch state.State {
		case Infected:
			// Check if it's time to recover
			if currentTime.After(state.RecoveryTime) {
				state.State = Recovered
				state.ImmunityExpiry = currentTime.Add(30 * time.Minute) // Default immunity
				recoveries++
				
				// Set immunity expiry based on alert
				n.alertsMutex.RLock()
				if alert, exists := n.activeAlerts[alertID]; exists {
					state.ImmunityExpiry = currentTime.Add(alert.Immunity)
				}
				n.alertsMutex.RUnlock()
			}
			
		case Recovered:
			// Check if immunity period is over
			if currentTime.After(state.ImmunityExpiry) {
				state.State = Immune
				immunities++
			}
			
		case Immune:
			// Check if we should return to susceptible
			if currentTime.Sub(state.ImmunityExpiry) > time.Hour {
				delete(n.alertStates, alertID)
			}
		}
	}
	n.statesMutex.Unlock()
	
	if recoveries > 0 || immunities > 0 {
		n.logger.Printf("🏥 Recovery process: %d recovered, %d immune", recoveries, immunities)
		
		n.metrics.mu.Lock()
		n.metrics.TotalRecoveries += int64(recoveries)
		n.metrics.mu.Unlock()
	}
}

// Utility functions

func (n *EpidemicInformationNode) updateNeighborContact(neighborID string) {
	n.neighborsMutex.Lock()
	defer n.neighborsMutex.Unlock()
	
	if neighbor, exists := n.neighbors[neighborID]; exists {
		neighbor.LastContact = time.Now()
		
		// Update reliability based on consistent contact
		timeSinceLastContact := time.Since(neighbor.LastContact)
		if timeSinceLastContact < time.Minute {
			neighbor.Reliability = math.Min(1.0, neighbor.Reliability+0.01)
		}
	}
}

func generateAlertID() string {
	bytes := make([]byte, 6)
	rand.Read(bytes)
	return fmt.Sprintf("ALERT_%x", bytes)
}

func generateMessageID() string {
	bytes := make([]byte, 8)
	rand.Read(bytes)
	return fmt.Sprintf("%x", bytes)
}

// GetEpidemicStatus returns current epidemic status
func (n *EpidemicInformationNode) GetEpidemicStatus() map[string]interface{} {
	n.statesMutex.RLock()
	defer n.statesMutex.RUnlock()
	
	statusCounts := make(map[string]int)
	alertsByType := make(map[string]int)
	
	for _, state := range n.alertStates {
		statusCounts[state.State.String()]++
	}
	
	n.alertsMutex.RLock()
	for _, alert := range n.activeAlerts {
		alertsByType[alert.AlertType.String()]++
	}
	n.alertsMutex.RUnlock()
	
	return map[string]interface{}{
		"node_id":         n.NodeID,
		"warehouse":       n.WarehouseName,
		"region":          n.Region,
		"tier":           n.Tier,
		"status_counts":   statusCounts,
		"alerts_by_type":  alertsByType,
		"total_alerts":    len(n.activeAlerts),
		"neighbors":       len(n.neighbors),
	}
}

// GetMetrics returns epidemic metrics
func (n *EpidemicInformationNode) GetMetrics() *EpidemicMetrics {
	n.metrics.mu.RLock()
	defer n.metrics.mu.RUnlock()
	
	return &EpidemicMetrics{
		TotalInfections:       n.metrics.TotalInfections,
		TotalRecoveries:       n.metrics.TotalRecoveries,
		TotalTransmissions:    n.metrics.TotalTransmissions,
		AvgSpreadTime:         n.metrics.AvgSpreadTime,
		PeakInfectionRate:     n.metrics.PeakInfectionRate,
		ConvergenceTime:       n.metrics.ConvergenceTime,
		NetworkCoverage:       n.metrics.NetworkCoverage,
		EffectiveReproduction: n.metrics.EffectiveReproduction,
	}
}

// Shutdown gracefully shuts down the epidemic node
func (n *EpidemicInformationNode) Shutdown() {
	n.logger.Printf("🛑 Shutting down epidemic node %s", n.NodeID)
	
	n.cancel()
	
	if n.epidemicTicker != nil {
		n.epidemicTicker.Stop()
	}
	if n.recoveryTicker != nil {
		n.recoveryTicker.Stop()
	}
	
	close(n.incomingMessages)
	close(n.outgoingMessages)
}

// Main function demonstrating epidemic information spread
func main() {
	fmt.Println("🇮🇳 JioMart Epidemic Information Spread Simulation")
	fmt.Println(strings.Repeat("=", 55))
	
	// Create JioMart supply chain network
	nodes := make(map[string]*EpidemicInformationNode)
	
	warehouseData := []struct {
		id, name, region string
		tier             int
		location         Location
	}{
		// Tier 1 - Distribution Centers
		{"DC_MUM", "Mumbai DC", "West", 1, Location{19.0760, 72.8777, "Mumbai"}},
		{"DC_DEL", "Delhi DC", "North", 1, Location{28.7041, 77.1025, "Delhi"}},
		{"DC_BLR", "Bangalore DC", "South", 1, Location{12.9716, 77.5946, "Bangalore"}},
		{"DC_KOL", "Kolkata DC", "East", 1, Location{22.5726, 88.3639, "Kolkata"}},
		
		// Tier 2 - Regional Hubs
		{"RH_PUN", "Pune Regional", "West", 2, Location{18.5204, 73.8567, "Pune"}},
		{"RH_GUR", "Gurgaon Regional", "North", 2, Location{28.4595, 77.0266, "Gurgaon"}},
		{"RH_HYD", "Hyderabad Regional", "South", 2, Location{17.3850, 78.4867, "Hyderabad"}},
		{"RH_CHN", "Chennai Regional", "South", 2, Location{13.0827, 80.2707, "Chennai"}},
		
		// Tier 3 - Local Warehouses
		{"LW_THN", "Thane Local", "West", 3, Location{19.2183, 72.9781, "Thane"}},
		{"LW_NOI", "Noida Local", "North", 3, Location{28.5355, 77.3910, "Noida"}},
		{"LW_WHT", "Whitefield Local", "South", 3, Location{12.9698, 77.7500, "Whitefield"}},
		{"LW_SLT", "Salt Lake Local", "East", 3, Location{22.5958, 88.4497, "Salt Lake"}},
	}
	
	// Create nodes
	for _, data := range warehouseData {
		nodes[data.id] = NewEpidemicInformationNode(
			data.id, data.name, data.region, data.tier, data.location)
	}
	
	// Create hierarchical network topology
	connections := []struct {
		from, to string
		distance float64
		hops     int
	}{
		// DC to Regional Hub connections
		{"DC_MUM", "RH_PUN", 150.0, 1},
		{"DC_DEL", "RH_GUR", 30.0, 1},
		{"DC_BLR", "RH_HYD", 500.0, 1},
		{"DC_BLR", "RH_CHN", 350.0, 1},
		
		// Regional Hub to Local Warehouse connections
		{"RH_PUN", "LW_THN", 50.0, 1},
		{"RH_GUR", "LW_NOI", 25.0, 1},
		{"RH_HYD", "LW_WHT", 600.0, 1},
		{"DC_KOL", "LW_SLT", 15.0, 1},
		
		// Cross-regional connections for redundancy
		{"DC_MUM", "DC_DEL", 1400.0, 2},
		{"DC_DEL", "DC_BLR", 2100.0, 2},
		{"DC_BLR", "DC_KOL", 1600.0, 2},
		{"DC_MUM", "DC_BLR", 980.0, 2},
		
		// Some regional cross-connections
		{"RH_PUN", "RH_GUR", 1450.0, 3},
		{"RH_HYD", "RH_CHN", 625.0, 2},
	}
	
	// Establish connections
	for _, conn := range connections {
		if fromNode, exists := nodes[conn.from]; exists {
			if toNode, exists := nodes[conn.to]; exists {
				fromNode.AddNeighbor(conn.to, conn.distance, conn.hops)
				toNode.AddNeighbor(conn.from, conn.distance, conn.hops)
			}
		}
	}
	
	fmt.Printf("Created JioMart network with %d warehouses\n", len(nodes))
	fmt.Printf("Network connections: %d\n", len(connections))
	
	// Wait for network to stabilize
	time.Sleep(2 * time.Second)
	
	// Simulate various supply chain alerts
	fmt.Println("\n🚨 Starting epidemic alert simulation...")
	
	// Critical stock alert from Mumbai DC
	nodes["DC_MUM"].CreateAlert(
		StockAlert, 1,
		"Critical Stock Shortage",
		"iPhone 14 Pro Max stock critically low across West region",
		"IPHONE14PM",
		30*time.Minute,
	)
	
	time.Sleep(3 * time.Second)
	
	// Quality alert from Bangalore DC
	nodes["DC_BLR"].CreateAlert(
		QualityAlert, 2,
		"Quality Issue Detected",
		"Batch contamination detected in processed food items",
		"FOOD_BATCH_2024",
		45*time.Minute,
	)
	
	time.Sleep(4 * time.Second)
	
	// Weather alert from Delhi DC
	nodes["DC_DEL"].CreateAlert(
		WeatherAlert, 2,
		"Severe Weather Warning",
		"Heavy snowfall expected in North region, delivery delays anticipated",
		"ALL_ITEMS",
		2*time.Hour,
	)
	
	time.Sleep(2 * time.Second)
	
	// Security alert from Kolkata DC
	nodes["DC_KOL"].CreateAlert(
		SecurityAlert, 1,
		"Security Breach",
		"Unauthorized access detected at warehouse facility",
		"ALL_ITEMS",
		1*time.Hour,
	)
	
	// Let epidemic spread
	fmt.Println("🦠 Epidemic spread in progress...")
	time.Sleep(20 * time.Second)
	
	// Print epidemic status
	fmt.Println("\n📊 Epidemic Status Report:")
	fmt.Println(strings.Repeat("-", 60))
	
	totalInfections := int64(0)
	totalRecoveries := int64(0)
	totalTransmissions := int64(0)
	
	for nodeID, node := range nodes {
		status := node.GetEpidemicStatus()
		metrics := node.GetMetrics()
		
		fmt.Printf("%s (%s):\n", status["warehouse"], nodeID)
		fmt.Printf("  Region: %s, Tier: %d\n", status["region"], status["tier"])
		fmt.Printf("  Active Alerts: %d\n", status["total_alerts"])
		fmt.Printf("  Epidemic States: %v\n", status["status_counts"])
		fmt.Printf("  Alerts by Type: %v\n", status["alerts_by_type"])
		fmt.Printf("  Infections: %d, Recoveries: %d, Transmissions: %d\n",
			metrics.TotalInfections, metrics.TotalRecoveries, metrics.TotalTransmissions)
		fmt.Println()
		
		totalInfections += metrics.TotalInfections
		totalRecoveries += metrics.TotalRecoveries
		totalTransmissions += metrics.TotalTransmissions
	}
	
	fmt.Printf("📈 Network Summary:\n")
	fmt.Printf("  Total infections across network: %d\n", totalInfections)
	fmt.Printf("  Total recoveries across network: %d\n", totalRecoveries)
	fmt.Printf("  Total transmissions across network: %d\n", totalTransmissions)
	fmt.Printf("  Average infections per node: %.1f\n", 
		float64(totalInfections)/float64(len(nodes)))
	
	if totalTransmissions > 0 {
		infectionRate := float64(totalInfections) / float64(totalTransmissions) * 100
		fmt.Printf("  Network infection rate: %.2f%%\n", infectionRate)
	}
	
	// Analyze alert spread by type
	fmt.Println("\n🔍 Alert Spread Analysis:")
	alertTypeCounts := make(map[string]int)
	
	for _, node := range nodes {
		status := node.GetEpidemicStatus()
		if alertsByType, ok := status["alerts_by_type"].(map[string]int); ok {
			for alertType, count := range alertsByType {
				alertTypeCounts[alertType] += count
			}
		}
	}
	
	for alertType, totalCount := range alertTypeCounts {
		spreadPercentage := float64(totalCount) / float64(len(nodes)) * 100
		fmt.Printf("  %s: Spread to %.1f%% of network (%d/%d nodes)\n",
			alertType, spreadPercentage, totalCount, len(nodes))
	}
	
	// Cleanup
	fmt.Println("\n🛑 Shutting down epidemic network...")
	for _, node := range nodes {
		node.Shutdown()
	}
	
	fmt.Println("Epidemic information spread simulation completed!")
}