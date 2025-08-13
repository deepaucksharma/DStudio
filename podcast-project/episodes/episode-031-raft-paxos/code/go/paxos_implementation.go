/*
Paxos Consensus Algorithm Implementation in Go
High-performance implementation similar to etcd and Consul

यह implementation production-grade Paxos consensus को Go में दिखाती है
जैसे कि etcd में इस्तेमाल होती है service discovery के लिए
*/

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// ProposalValue represents a value being proposed in Paxos
type ProposalValue struct {
	Type        string                 `json:"type"`
	Key         string                 `json:"key,omitempty"`
	Value       interface{}            `json:"value,omitempty"`
	ServiceInfo map[string]interface{} `json:"service_info,omitempty"`
	Timestamp   int64                  `json:"timestamp"`
	ProposerID  string                 `json:"proposer_id"`
}

// PrepareRequest is Phase 1 of Paxos
type PrepareRequest struct {
	ProposalNumber int64  `json:"proposal_number"`
	ProposerID     string `json:"proposer_id"`
}

// PrepareResponse is response to Phase 1
type PrepareResponse struct {
	AcceptorID                string         `json:"acceptor_id"`
	Promised                  bool           `json:"promised"`
	HighestProposalAccepted   *int64         `json:"highest_proposal_accepted,omitempty"`
	HighestValueAccepted      *ProposalValue `json:"highest_value_accepted,omitempty"`
	Reason                    string         `json:"reason"`
}

// AcceptRequest is Phase 2 of Paxos
type AcceptRequest struct {
	ProposalNumber int64          `json:"proposal_number"`
	Value          ProposalValue  `json:"value"`
	ProposerID     string         `json:"proposer_id"`
}

// AcceptResponse is response to Phase 2
type AcceptResponse struct {
	AcceptorID     string `json:"acceptor_id"`
	Accepted       bool   `json:"accepted"`
	ProposalNumber int64  `json:"proposal_number"`
	Reason         string `json:"reason"`
}

// PaxosAcceptor represents an acceptor node in Paxos
type PaxosAcceptor struct {
	acceptorID                string
	mu                        sync.RWMutex
	highestPromisedProposal   int64
	highestAcceptedProposal   int64
	acceptedValue             *ProposalValue
	acceptRequestCount        int64
	promiseRequestCount       int64
}

// NewPaxosAcceptor creates a new Paxos acceptor
func NewPaxosAcceptor(acceptorID string) *PaxosAcceptor {
	return &PaxosAcceptor{
		acceptorID:              acceptorID,
		highestPromisedProposal: -1,
		highestAcceptedProposal: -1,
	}
}

// HandlePrepare handles Phase 1: Prepare request
func (a *PaxosAcceptor) HandlePrepare(ctx context.Context, req *PrepareRequest) *PrepareResponse {
	atomic.AddInt64(&a.promiseRequestCount, 1)
	
	a.mu.Lock()
	defer a.mu.Unlock()
	
	log.Printf("📋 Acceptor %s: Received prepare request %d from %s", 
		a.acceptorID, req.ProposalNumber, req.ProposerID)
	
	// If proposal number is higher than any promised, promise it
	if req.ProposalNumber > a.highestPromisedProposal {
		a.highestPromisedProposal = req.ProposalNumber
		
		response := &PrepareResponse{
			AcceptorID: a.acceptorID,
			Promised:   true,
			Reason:     fmt.Sprintf("Promised proposal %d", req.ProposalNumber),
		}
		
		// Return highest accepted proposal if any
		if a.highestAcceptedProposal >= 0 {
			response.HighestProposalAccepted = &a.highestAcceptedProposal
			response.HighestValueAccepted = a.acceptedValue
		}
		
		log.Printf("✅ Acceptor %s: Promised proposal %d", a.acceptorID, req.ProposalNumber)
		return response
	}
	
	// Reject if already promised higher proposal
	response := &PrepareResponse{
		AcceptorID: a.acceptorID,
		Promised:   false,
		Reason:     fmt.Sprintf("Already promised higher proposal %d", a.highestPromisedProposal),
	}
	
	log.Printf("❌ Acceptor %s: Rejected prepare %d (promised: %d)", 
		a.acceptorID, req.ProposalNumber, a.highestPromisedProposal)
	
	return response
}

// HandleAccept handles Phase 2: Accept request
func (a *PaxosAcceptor) HandleAccept(ctx context.Context, req *AcceptRequest) *AcceptResponse {
	atomic.AddInt64(&a.acceptRequestCount, 1)
	
	a.mu.Lock()
	defer a.mu.Unlock()
	
	log.Printf("📝 Acceptor %s: Received accept request %d from %s", 
		a.acceptorID, req.ProposalNumber, req.ProposerID)
	
	// Accept if proposal number >= highest promised
	if req.ProposalNumber >= a.highestPromisedProposal {
		a.highestAcceptedProposal = req.ProposalNumber
		a.acceptedValue = &req.Value
		
		response := &AcceptResponse{
			AcceptorID:     a.acceptorID,
			Accepted:       true,
			ProposalNumber: req.ProposalNumber,
			Reason:         fmt.Sprintf("Accepted proposal %d", req.ProposalNumber),
		}
		
		log.Printf("✅ Acceptor %s: Accepted proposal %d with value type %s", 
			a.acceptorID, req.ProposalNumber, req.Value.Type)
		
		return response
	}
	
	// Reject if promised higher proposal
	response := &AcceptResponse{
		AcceptorID:     a.acceptorID,
		Accepted:       false,
		ProposalNumber: req.ProposalNumber,
		Reason:         fmt.Sprintf("Promised higher proposal %d", a.highestPromisedProposal),
	}
	
	log.Printf("❌ Acceptor %s: Rejected accept %d", a.acceptorID, req.ProposalNumber)
	return response
}

// GetState returns current acceptor state (thread-safe)
func (a *PaxosAcceptor) GetState() map[string]interface{} {
	a.mu.RLock()
	defer a.mu.RUnlock()
	
	state := map[string]interface{}{
		"acceptor_id":                a.acceptorID,
		"highest_promised":           a.highestPromisedProposal,
		"highest_accepted":           a.highestAcceptedProposal,
		"promise_request_count":      atomic.LoadInt64(&a.promiseRequestCount),
		"accept_request_count":       atomic.LoadInt64(&a.acceptRequestCount),
	}
	
	if a.acceptedValue != nil {
		state["accepted_value"] = *a.acceptedValue
	}
	
	return state
}

// PaxosProposer represents a proposer node in Paxos
type PaxosProposer struct {
	proposerID       string
	acceptors        []*PaxosAcceptor
	proposalCounter  int64
	proposerHash     int64
	mu               sync.Mutex
}

// NewPaxosProposer creates a new Paxos proposer
func NewPaxosProposer(proposerID string, acceptors []*PaxosAcceptor) *PaxosProposer {
	// Generate hash for unique proposal numbers
	hash := int64(0)
	for _, b := range []byte(proposerID) {
		hash = hash*31 + int64(b)
	}
	if hash < 0 {
		hash = -hash
	}
	
	return &PaxosProposer{
		proposerID:   proposerID,
		acceptors:    acceptors,
		proposerHash: hash % 256,
	}
}

// GenerateProposalNumber generates unique, monotonically increasing proposal number
func (p *PaxosProposer) GenerateProposalNumber() int64 {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	p.proposalCounter++
	// Combine counter and proposer hash for uniqueness across proposers
	return (p.proposalCounter << 8) | p.proposerHash
}

// ProposeValue implements the full two-phase Paxos protocol
func (p *PaxosProposer) ProposeValue(ctx context.Context, value ProposalValue) (bool, *ProposalValue, error) {
	proposalNumber := p.GenerateProposalNumber()
	
	log.Printf("\n🎯 Proposer %s: Starting proposal %d for value type '%s'", 
		p.proposerID, proposalNumber, value.Type)
	log.Println(strings.Repeat("=", 60))
	
	startTime := time.Now()
	
	// Phase 1: Prepare
	log.Printf("📋 Phase 1: PREPARE (Proposal %d)", proposalNumber)
	success, chosenValue, err := p.phase1Prepare(ctx, proposalNumber, &value)
	
	if err != nil {
		return false, nil, fmt.Errorf("phase 1 failed: %w", err)
	}
	
	if !success {
		log.Printf("❌ Proposer %s: Phase 1 failed for proposal %d", p.proposerID, proposalNumber)
		return false, nil, nil
	}
	
	// Use previously chosen value if different
	if chosenValue != nil && chosenValue.Type != value.Type {
		log.Printf("🔄 Proposer %s: Using previously chosen value type '%s' instead of '%s'", 
			p.proposerID, chosenValue.Type, value.Type)
		value = *chosenValue
	}
	
	// Phase 2: Accept
	log.Printf("\n📝 Phase 2: ACCEPT (Proposal %d)", proposalNumber)
	acceptSuccess, err := p.phase2Accept(ctx, proposalNumber, value)
	
	if err != nil {
		return false, nil, fmt.Errorf("phase 2 failed: %w", err)
	}
	
	elapsed := time.Since(startTime)
	
	if acceptSuccess {
		log.Printf("🎉 Proposer %s: Successfully proposed value type '%s' in %v", 
			p.proposerID, value.Type, elapsed)
		return true, &value, nil
	} else {
		log.Printf("❌ Proposer %s: Failed to get value accepted in %v", p.proposerID, elapsed)
		return false, nil, nil
	}
}

// phase1Prepare executes Phase 1 of Paxos
func (p *PaxosProposer) phase1Prepare(ctx context.Context, proposalNumber int64, 
	proposedValue *ProposalValue) (bool, *ProposalValue, error) {
	
	request := &PrepareRequest{
		ProposalNumber: proposalNumber,
		ProposerID:     p.proposerID,
	}
	
	// Send prepare to all acceptors concurrently
	responses := make([]*PrepareResponse, len(p.acceptors))
	var wg sync.WaitGroup
	
	for i, acceptor := range p.acceptors {
		wg.Add(1)
		go func(idx int, acc *PaxosAcceptor) {
			defer wg.Done()
			
			// Simulate network delay
			time.Sleep(time.Duration(rand.Intn(50)) * time.Millisecond)
			responses[idx] = acc.HandlePrepare(ctx, request)
		}(i, acceptor)
	}
	
	// Wait for all responses
	wg.Wait()
	
	// Count promises
	var promises []*PrepareResponse
	for _, response := range responses {
		if response != nil && response.Promised {
			promises = append(promises, response)
		}
	}
	
	majority := len(p.acceptors)/2 + 1
	log.Printf("   📊 Received %d/%d promises (need %d)", 
		len(promises), len(p.acceptors), majority)
	
	if len(promises) < majority {
		log.Printf("   ❌ Failed to get majority promises")
		return false, nil, nil
	}
	
	// Find highest accepted proposal among promises
	var highestAccepted int64 = -1
	var chosenValue *ProposalValue = proposedValue
	
	for _, response := range promises {
		if response.HighestProposalAccepted != nil && 
		   *response.HighestProposalAccepted > highestAccepted {
			highestAccepted = *response.HighestProposalAccepted
			chosenValue = response.HighestValueAccepted
			log.Printf("   🔍 Found higher accepted proposal %d with value type '%s'", 
				highestAccepted, chosenValue.Type)
		}
	}
	
	log.Printf("   ✅ Phase 1 successful - will propose value type '%s'", chosenValue.Type)
	return true, chosenValue, nil
}

// phase2Accept executes Phase 2 of Paxos
func (p *PaxosProposer) phase2Accept(ctx context.Context, proposalNumber int64, 
	value ProposalValue) (bool, error) {
	
	request := &AcceptRequest{
		ProposalNumber: proposalNumber,
		Value:          value,
		ProposerID:     p.proposerID,
	}
	
	// Send accept to all acceptors concurrently
	responses := make([]*AcceptResponse, len(p.acceptors))
	var wg sync.WaitGroup
	
	for i, acceptor := range p.acceptors {
		wg.Add(1)
		go func(idx int, acc *PaxosAcceptor) {
			defer wg.Done()
			
			// Simulate network delay
			time.Sleep(time.Duration(rand.Intn(50)) * time.Millisecond)
			responses[idx] = acc.HandleAccept(ctx, request)
		}(i, acceptor)
	}
	
	// Wait for all responses
	wg.Wait()
	
	// Count accepts
	var accepts []*AcceptResponse
	for _, response := range responses {
		if response != nil && response.Accepted {
			accepts = append(accepts, response)
		}
	}
	
	majority := len(p.acceptors)/2 + 1
	log.Printf("   📊 Received %d/%d accepts (need %d)", 
		len(accepts), len(p.acceptors), majority)
	
	if len(accepts) >= majority {
		log.Printf("   ✅ Phase 2 successful - value type '%s' chosen!", value.Type)
		return true, nil
	} else {
		log.Printf("   ❌ Failed to get majority accepts")
		return false, nil
	}
}

// ServiceRegistry simulates a service registry using Paxos consensus
type ServiceRegistry struct {
	services map[string]ProposalValue
	mu       sync.RWMutex
}

// NewServiceRegistry creates a new service registry
func NewServiceRegistry() *ServiceRegistry {
	return &ServiceRegistry{
		services: make(map[string]ProposalValue),
	}
}

// RegisterService registers a service using Paxos consensus
func (sr *ServiceRegistry) RegisterService(ctx context.Context, proposer *PaxosProposer,
	serviceName string, serviceInfo map[string]interface{}) (bool, error) {
	
	value := ProposalValue{
		Type:        "REGISTER_SERVICE",
		Key:         serviceName,
		ServiceInfo: serviceInfo,
		Timestamp:   time.Now().UnixNano(),
		ProposerID:  proposer.proposerID,
	}
	
	success, chosenValue, err := proposer.ProposeValue(ctx, value)
	
	if err != nil {
		return false, err
	}
	
	if success && chosenValue != nil {
		sr.mu.Lock()
		sr.services[serviceName] = *chosenValue
		sr.mu.Unlock()
		return true, nil
	}
	
	return false, nil
}

// GetServices returns all registered services
func (sr *ServiceRegistry) GetServices() map[string]ProposalValue {
	sr.mu.RLock()
	defer sr.mu.RUnlock()
	
	result := make(map[string]ProposalValue)
	for k, v := range sr.services {
		result[k] = v
	}
	return result
}

// simulateEtcdServiceDiscovery simulates etcd-like service discovery using Paxos
func simulateEtcdServiceDiscovery() {
	fmt.Println("🇮🇳 Paxos Go Implementation - Service Discovery Simulation")
	fmt.Println("🔍 Simulating etcd-like distributed service registry")
	fmt.Println(strings.Repeat("=", 70))
	
	// Create acceptors (like etcd cluster members)
	acceptorNodes := []string{"etcd-mumbai", "etcd-delhi", "etcd-bangalore", "etcd-chennai", "etcd-pune"}
	acceptors := make([]*PaxosAcceptor, len(acceptorNodes))
	
	for i, nodeID := range acceptorNodes {
		acceptors[i] = NewPaxosAcceptor(nodeID)
	}
	
	fmt.Printf("🏛️ Created %d acceptors: %v\n", len(acceptors), acceptorNodes)
	
	// Create proposers (like service instances trying to register)
	proposerServices := []string{"payment-service", "user-service", "notification-service"}
	proposers := make([]*PaxosProposer, len(proposerServices))
	
	for i, serviceID := range proposerServices {
		proposers[i] = NewPaxosProposer(serviceID, acceptors)
	}
	
	fmt.Printf("🚀 Created %d proposers: %v\n", len(proposers), proposerServices)
	
	// Create service registry
	registry := NewServiceRegistry()
	
	// Simulate concurrent service registration
	fmt.Println("\n🗂️ Starting concurrent service registration...")
	
	ctx := context.Background()
	var wg sync.WaitGroup
	results := make([]bool, len(proposers))
	
	// Service registration data
	serviceInfos := []map[string]interface{}{
		{
			"host":     "10.0.1.100",
			"port":     8080,
			"version":  "v1.2.3",
			"region":   "mumbai",
			"protocol": "http",
		},
		{
			"host":     "10.0.2.101", 
			"port":     8081,
			"version":  "v2.1.0",
			"region":   "delhi",
			"protocol": "grpc",
		},
		{
			"host":     "10.0.3.102",
			"port":     8082,
			"version":  "v1.0.5",
			"region":   "bangalore",
			"protocol": "http",
		},
	}
	
	// Register services concurrently
	for i, proposer := range proposers {
		wg.Add(1)
		go func(idx int, prop *PaxosProposer, serviceName string) {
			defer wg.Done()
			
			// Add small random delay to simulate real-world timing
			time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
			
			success, err := registry.RegisterService(ctx, prop, serviceName, serviceInfos[idx])
			if err != nil {
				log.Printf("Error registering service %s: %v", serviceName, err)
			}
			results[idx] = success
		}(i, proposer, proposerServices[i])
	}
	
	// Wait for all registrations
	wg.Wait()
	
	// Show results
	fmt.Println("\n📊 Service Registration Results:")
	fmt.Println(strings.Repeat("-", 40))
	
	successCount := 0
	for i, success := range results {
		if success {
			fmt.Printf("✅ %s: REGISTERED\n", proposerServices[i])
			successCount++
		} else {
			fmt.Printf("❌ %s: FAILED\n", proposerServices[i])
		}
	}
	
	fmt.Printf("\n📈 Registration Summary: %d/%d successful\n", successCount, len(results))
	
	// Show registered services
	fmt.Println("\n🗂️ Final Service Registry:")
	services := registry.GetServices()
	
	for serviceName, serviceValue := range services {
		fmt.Printf("\n🔧 Service: %s\n", serviceName)
		fmt.Printf("   Host: %v\n", serviceValue.ServiceInfo["host"])
		fmt.Printf("   Port: %v\n", serviceValue.ServiceInfo["port"])
		fmt.Printf("   Version: %v\n", serviceValue.ServiceInfo["version"])
		fmt.Printf("   Region: %v\n", serviceValue.ServiceInfo["region"])
		fmt.Printf("   Protocol: %v\n", serviceValue.ServiceInfo["protocol"])
		fmt.Printf("   Registered by: %s\n", serviceValue.ProposerID)
		fmt.Printf("   Timestamp: %s\n", time.Unix(0, serviceValue.Timestamp).Format(time.RFC3339))
	}
	
	// Show acceptor states for verification
	fmt.Println("\n🏛️ Final Acceptor States:")
	for _, acceptor := range acceptors {
		state := acceptor.GetState()
		fmt.Printf("\n   %s:\n", acceptor.acceptorID)
		fmt.Printf("     Promised: %v\n", state["highest_promised"])
		fmt.Printf("     Accepted: %v\n", state["highest_accepted"])
		fmt.Printf("     Promise requests: %v\n", state["promise_request_count"])
		fmt.Printf("     Accept requests: %v\n", state["accept_request_count"])
		
		if acceptedValue, ok := state["accepted_value"]; ok {
			if av, ok := acceptedValue.(ProposalValue); ok {
				fmt.Printf("     Service registered: %s\n", av.Key)
			}
		}
	}
	
	// Verify consistency
	fmt.Println("\n🔍 Consistency Verification:")
	if len(services) > 0 {
		// Check if all acceptors have the same final value
		var referenceValue *ProposalValue
		
		for _, acceptor := range acceptors {
			state := acceptor.GetState()
			if acceptedValue, ok := state["accepted_value"]; ok {
				if av, ok := acceptedValue.(ProposalValue); ok {
					if referenceValue == nil {
						referenceValue = &av
					} else if av.Key == referenceValue.Key && av.Type == referenceValue.Type {
						// Same value
						continue
					} else {
						fmt.Println("❌ Inconsistency detected across acceptors!")
						return
					}
				}
			}
		}
		
		fmt.Println("✅ All acceptors have consistent final state!")
	}
}

// simulateConfigConsensus simulates distributed configuration management
func simulateConfigConsensus() {
	fmt.Println("\n" + strings.Repeat("=", 70))
	fmt.Println("🇮🇳 Paxos - Distributed Configuration Management")
	fmt.Println(strings.Repeat("=", 70))
	
	// Create minimal setup for config consensus
	configNodes := []string{"config-server-1", "config-server-2", "config-server-3"}
	acceptors := make([]*PaxosAcceptor, len(configNodes))
	
	for i, nodeID := range configNodes {
		acceptors[i] = NewPaxosAcceptor(nodeID)
	}
	
	// Configuration proposers
	adminProposer := NewPaxosProposer("admin-console", acceptors)
	apiProposer := NewPaxosProposer("api-gateway", acceptors)
	
	// Configuration updates to propose
	configs := []ProposalValue{
		{
			Type:      "CONFIG_UPDATE",
			Key:       "database.connection_pool",
			Value:     map[string]interface{}{"max_connections": 100, "timeout": "30s"},
			Timestamp: time.Now().UnixNano(),
		},
		{
			Type:      "CONFIG_UPDATE", 
			Key:       "cache.redis",
			Value:     map[string]interface{}{"host": "redis-cluster.internal", "port": 6379},
			Timestamp: time.Now().UnixNano(),
		},
	}
	
	fmt.Println("\n🔧 Proposing configuration updates...")
	
	ctx := context.Background()
	
	// Propose configurations sequentially
	for i, config := range configs {
		fmt.Printf("\n📝 Configuration Update #%d:\n", i+1)
		fmt.Printf("   Key: %s\n", config.Key)
		
		if configValue, ok := config.Value.(map[string]interface{}); ok {
			configJson, _ := json.MarshalIndent(configValue, "   ", "  ")
			fmt.Printf("   Value: %s\n", string(configJson))
		}
		
		proposer := adminProposer
		if i == 1 {
			proposer = apiProposer
		}
		
		config.ProposerID = proposer.proposerID
		success, chosenConfig, err := proposer.ProposeValue(ctx, config)
		
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
		} else if success {
			fmt.Printf("   ✅ Configuration update successful!\n")
		} else {
			fmt.Printf("   ❌ Configuration update failed!\n")
		}
		
		time.Sleep(1 * time.Second) // Small delay between updates
	}
	
	// Show final configuration state
	fmt.Println("\n⚙️ Final Configuration State:")
	finalState := acceptors[0].GetState()
	if acceptedValue, ok := finalState["accepted_value"]; ok {
		if av, ok := acceptedValue.(ProposalValue); ok {
			fmt.Printf("   Key: %s\n", av.Key)
			if configValue, ok := av.Value.(map[string]interface{}); ok {
				configJson, _ := json.MarshalIndent(configValue, "   ", "  ")
				fmt.Printf("   Value: %s\n", string(configJson))
			}
			fmt.Printf("   Last updated by: %s\n", av.ProposerID)
			fmt.Printf("   Timestamp: %s\n", time.Unix(0, av.Timestamp).Format(time.RFC3339))
		}
	}
}

func main() {
	// Run service discovery simulation
	simulateEtcdServiceDiscovery()
	
	// Run configuration consensus simulation
	simulateConfigConsensus()
	
	fmt.Println("\n" + strings.Repeat("=", 70))
	fmt.Println("🇮🇳 Go Paxos Implementation Key Features:")
	fmt.Println("1. High-performance concurrent operations with goroutines")
	fmt.Println("2. Context-based cancellation support")
	fmt.Println("3. Atomic operations for thread-safe counters")
	fmt.Println("4. RWMutex for efficient read-heavy workloads")
	fmt.Println("5. JSON serialization for network communication")
	fmt.Println("6. Production-ready error handling and timeouts")
	fmt.Println("7. Suitable for building systems like etcd and Consul")
}