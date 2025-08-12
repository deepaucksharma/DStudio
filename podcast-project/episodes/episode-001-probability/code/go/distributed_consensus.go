// Distributed Consensus Probability Calculator
// भारतीय banking consortium के decision making process का mathematical model
//
// Indian Context: RBI monetary policy committee की consensus building
// Mumbai Example: Mumbai Municipal Corporation के ward representatives का voting pattern

package main

import (
	"fmt"
	"math"
	"math/rand"
	"sort"
	"time"
)

// ConsensusNode represents a single node in distributed system
// यह RBI committee के एक member की तरह है
type ConsensusNode struct {
	ID           string
	Region       string // Mumbai, Delhi, Bangalore, etc.
	Reliability  float64 // Node का historical accuracy (0.0 to 1.0)
	VotingWeight float64 // Voting power based on stake
	IsLeader     bool    // Current leader node
	LastSeen     time.Time
}

// ConsensusProposal represents a proposal that needs agreement
type ConsensusProposal struct {
	ProposalID   string
	Description  string
	ProposerNode string
	RequiredVotes int
	Timestamp    time.Time
	UrgencyLevel int // 1-5, higher means more urgent
}

// VoteDecision represents a node's vote on proposal
type VoteDecision struct {
	NodeID    string
	Vote      bool    // true = accept, false = reject
	Confidence float64 // How confident the node is (0.0 to 1.0)
	Timestamp time.Time
}

// DistributedConsensusCalculator simulates consensus in Indian distributed systems
type DistributedConsensusCalculator struct {
	Nodes           []ConsensusNode
	ConsensusType   string // "RAFT", "PBFT", "POW", etc.
	NetworkLatency  time.Duration
	PartitionRisk   float64 // Probability of network partition (0.0 to 1.0)
	ByzantineRisk   float64 // Probability of malicious nodes (0.0 to 1.0)
}

// NewBankingConsensusSystem creates a realistic Indian banking consensus system
func NewBankingConsensusSystem() *DistributedConsensusCalculator {
	nodes := []ConsensusNode{
		{"RBI_MUMBAI", "Mumbai", 0.95, 0.3, true, time.Now()},      // RBI head office
		{"SBI_DELHI", "Delhi", 0.90, 0.2, false, time.Now()},       // State Bank of India
		{"HDFC_BANGALORE", "Bangalore", 0.88, 0.15, false, time.Now()}, // Private bank
		{"ICICI_MUMBAI", "Mumbai", 0.87, 0.15, false, time.Now()},  // ICICI Bank
		{"AXIS_PUNE", "Pune", 0.85, 0.1, false, time.Now()},        // Axis Bank
		{"KOTAK_MUMBAI", "Mumbai", 0.83, 0.1, false, time.Now()},   // Kotak Bank
	}
	
	return &DistributedConsensusCalculator{
		Nodes:          nodes,
		ConsensusType:  "PBFT", // Practical Byzantine Fault Tolerance
		NetworkLatency: 50 * time.Millisecond, // Average latency between cities
		PartitionRisk:  0.05,  // 5% chance of network partition (realistic for India)
		ByzantineRisk:  0.02,  // 2% chance of malicious behavior (very low in banking)
	}
}

// CalculateConsensusRobability calculates probability of reaching consensus
func (dcc *DistributedConsensusCalculator) CalculateConsensusRobability(
	proposal ConsensusProposal,
	networkCondition float64, // 0.0 (poor) to 1.0 (excellent)
) float64 {
	
	fmt.Printf("🏛️  Calculating consensus probability for: %s\n", proposal.Description)
	
	// Base probability starts high for banking systems (trust is important)
	baseProbability := 0.75
	
	// Network condition impact - Indian internet infrastructure challenges
	networkMultiplier := 0.5 + (networkCondition * 0.5) // 0.5 to 1.0
	
	// Node reliability average - weighted by voting power
	totalWeight := 0.0
	weightedReliability := 0.0
	
	for _, node := range dcc.Nodes {
		totalWeight += node.VotingWeight
		weightedReliability += node.Reliability * node.VotingWeight
	}
	
	avgReliability := weightedReliability / totalWeight
	
	// Leader availability bonus - stable leadership helps consensus
	leaderBonus := 1.0
	for _, node := range dcc.Nodes {
		if node.IsLeader && time.Since(node.LastSeen) > 10*time.Second {
			leaderBonus = 0.8 // Leader unavailable penalty
			break
		}
	}
	
	// Urgency factor - urgent proposals get higher priority
	urgencyMultiplier := 1.0 + (float64(proposal.UrgencyLevel-1) * 0.1)
	
	// Byzantine fault tolerance adjustment
	byzantineAdjustment := 1.0 - (dcc.ByzantineRisk * 2.0) // Reduce probability
	
	// Network partition risk adjustment
	partitionAdjustment := 1.0 - (dcc.PartitionRisk * 3.0)
	
	// Quorum size impact - larger quorum makes consensus harder
	requiredQuorum := float64(proposal.RequiredVotes) / float64(len(dcc.Nodes))
	quorumMultiplier := 1.2 - requiredQuorum // Harder with more nodes required
	
	// Final probability calculation
	finalProbability := baseProbability * networkMultiplier * avgReliability * 
		leaderBonus * urgencyMultiplier * byzantineAdjustment * 
		partitionAdjustment * quorumMultiplier
	
	// Ensure probability stays within bounds
	if finalProbability > 0.99 {
		finalProbability = 0.99
	}
	if finalProbability < 0.1 {
		finalProbability = 0.1
	}
	
	fmt.Printf("   Network Condition: %.1f%%\n", networkCondition*100)
	fmt.Printf("   Average Node Reliability: %.1f%%\n", avgReliability*100)
	fmt.Printf("   Required Quorum: %.1f%% (%d/%d nodes)\n", 
		requiredQuorum*100, proposal.RequiredVotes, len(dcc.Nodes))
	fmt.Printf("   Consensus Probability: %.1f%%\n", finalProbability*100)
	
	return finalProbability
}

// SimulateConsensusRound simulates actual voting round with realistic behaviors
func (dcc *DistributedConsensusCalculator) SimulateConsensusRound(
	proposal ConsensusProposal,
	networkCondition float64,
) ConsensusResult {
	
	fmt.Printf("\n🗳️  Starting consensus round for: %s\n", proposal.ProposalID)
	fmt.Printf("   Proposal: %s\n", proposal.Description)
	
	votes := make([]VoteDecision, 0, len(dcc.Nodes))
	
	// Each node votes based on its characteristics
	for _, node := range dcc.Nodes {
		
		// Simulate network delay and possible failure
		time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
		
		// Node availability check - Mumbai monsoon can affect connectivity
		isAvailable := rand.Float64() < (networkCondition * 0.9 + 0.1)
		if !isAvailable {
			fmt.Printf("   📴 %s unavailable (network issue)\n", node.ID)
			continue
		}
		
		// Vote decision based on node reliability and random factors
		voteDecision := rand.Float64() < node.Reliability
		
		// Regional bias - nodes in same region might vote similarly
		// Mumbai financial center nodes might have similar perspectives
		if node.Region == "Mumbai" && proposal.UrgencyLevel >= 4 {
			voteDecision = voteDecision || (rand.Float64() < 0.3) // Slight bias for urgent Mumbai proposals
		}
		
		// Confidence level - how sure is the node about its vote
		confidence := node.Reliability * (0.7 + rand.Float64()*0.3)
		
		vote := VoteDecision{
			NodeID:     node.ID,
			Vote:       voteDecision,
			Confidence: confidence,
			Timestamp:  time.Now(),
		}
		
		votes = append(votes, vote)
		
		voteStr := "REJECT"
		if vote.Vote {
			voteStr = "ACCEPT"
		}
		
		fmt.Printf("   🗳️  %s: %s (confidence: %.1f%%)\n", 
			node.ID, voteStr, confidence*100)
	}
	
	// Calculate consensus result
	acceptVotes := 0
	totalWeight := 0.0
	acceptedWeight := 0.0
	
	for _, vote := range votes {
		// Find corresponding node for weight
		for _, node := range dcc.Nodes {
			if node.ID == vote.NodeID {
				totalWeight += node.VotingWeight
				if vote.Vote {
					acceptVotes++
					acceptedWeight += node.VotingWeight
				}
				break
			}
		}
	}
	
	// Consensus achieved if we have enough votes AND enough weighted support
	quorumMet := acceptVotes >= proposal.RequiredVotes
	weightedQuorumMet := acceptedWeight/totalWeight >= 0.6 // 60% weighted support needed
	
	consensusAchieved := quorumMet && weightedQuorumMet
	
	result := ConsensusResult{
		ProposalID:        proposal.ProposalID,
		ConsensusAchieved: consensusAchieved,
		AcceptVotes:       acceptVotes,
		TotalVotes:        len(votes),
		WeightedSupport:   acceptedWeight / totalWeight,
		Votes:             votes,
		Duration:          time.Since(proposal.Timestamp),
	}
	
	return result
}

// ConsensusResult stores the outcome of a consensus round
type ConsensusResult struct {
	ProposalID        string
	ConsensusAchieved bool
	AcceptVotes       int
	TotalVotes        int
	WeightedSupport   float64
	Votes             []VoteDecision
	Duration          time.Duration
}

// MonteCarloConsensusAnalysis runs multiple scenarios for statistical analysis
func (dcc *DistributedConsensusCalculator) MonteCarloConsensusAnalysis(
	simulations int,
	proposalType string,
) {
	
	fmt.Printf("\n🎲 Monte Carlo Analysis: %s Consensus\n", proposalType)
	fmt.Printf("   Running %d simulations...\n", simulations)
	fmt.Printf("   System: %s with %d nodes\n", dcc.ConsensusType, len(dcc.Nodes))
	
	successCount := 0
	totalDuration := time.Duration(0)
	networkConditions := []float64{}
	
	// Different network scenarios based on Indian infrastructure reality
	scenarios := map[string]float64{
		"Excellent (Tier-1 cities)": 0.95,
		"Good (Urban areas)":        0.80,
		"Average (Semi-urban)":      0.65,
		"Poor (Rural/Monsoon)":      0.40,
	}
	
	scenarioResults := make(map[string]int)
	
	for i := 0; i < simulations; i++ {
		// Random network condition based on realistic distribution
		var networkCondition float64
		var scenario string
		
		rand_val := rand.Float64()
		if rand_val < 0.3 {
			scenario = "Excellent (Tier-1 cities)"
			networkCondition = scenarios[scenario]
		} else if rand_val < 0.6 {
			scenario = "Good (Urban areas)"
			networkCondition = scenarios[scenario]
		} else if rand_val < 0.85 {
			scenario = "Average (Semi-urban)"
			networkCondition = scenarios[scenario]
		} else {
			scenario = "Poor (Rural/Monsoon)"
			networkCondition = scenarios[scenario]
		}
		
		networkConditions = append(networkConditions, networkCondition)
		
		// Create test proposal
		proposal := ConsensusProposal{
			ProposalID:    fmt.Sprintf("PROP_%d", i+1),
			Description:   fmt.Sprintf("%s Policy Decision #%d", proposalType, i+1),
			RequiredVotes: (len(dcc.Nodes) + 1) / 2, // Simple majority
			UrgencyLevel:  rand.Intn(5) + 1,
			Timestamp:     time.Now(),
		}
		
		// Simulate consensus
		result := dcc.SimulateConsensusRound(proposal, networkCondition)
		
		if result.ConsensusAchieved {
			successCount++
			scenarioResults[scenario]++
		}
		
		totalDuration += result.Duration
		
		// Progress update
		if (i+1)%100 == 0 {
			fmt.Printf("   ✅ Completed %d simulations...\n", i+1)
		}
	}
	
	// Calculate statistics
	successRate := float64(successCount) / float64(simulations)
	avgDuration := totalDuration / time.Duration(simulations)
	
	// Display results
	fmt.Printf("\n📊 Monte Carlo Results:\n")
	fmt.Printf("   Overall Success Rate: %.1f%%\n", successRate*100)
	fmt.Printf("   Successful Consensus: %d/%d\n", successCount, simulations)
	fmt.Printf("   Average Duration: %v\n", avgDuration)
	
	// Network scenario breakdown
	fmt.Printf("\n🌐 Success Rate by Network Condition:\n")
	scenarioOrder := []string{
		"Excellent (Tier-1 cities)",
		"Good (Urban areas)",
		"Average (Semi-urban)",
		"Poor (Rural/Monsoon)",
	}
	
	for _, scenario := range scenarioOrder {
		scenarioSimulations := 0
		for _, condition := range networkConditions {
			if math.Abs(condition-scenarios[scenario]) < 0.01 {
				scenarioSimulations++
			}
		}
		
		if scenarioSimulations > 0 {
			scenarioSuccessRate := float64(scenarioResults[scenario]) / float64(scenarioSimulations) * 100
			fmt.Printf("   %s: %.1f%% (%d/%d)\n",
				scenario, scenarioSuccessRate, scenarioResults[scenario], scenarioSimulations)
		}
	}
}

// NetworkPartitionSimulation simulates split-brain scenarios
func (dcc *DistributedConsensusCalculator) NetworkPartitionSimulation() {
	fmt.Printf("\n🌐 Network Partition Simulation (Split-Brain Scenario)\n")
	fmt.Printf("   Simulating India North-South connectivity issues...\n")
	
	// Partition nodes by region - realistic Indian geography
	northNodes := []ConsensusNode{}
	southNodes := []ConsensusNode{}
	
	for _, node := range dcc.Nodes {
		if node.Region == "Delhi" || node.Region == "Mumbai" {
			northNodes = append(northNodes, node)
		} else {
			southNodes = append(southNodes, node)
		}
	}
	
	fmt.Printf("   North Partition: %d nodes\n", len(northNodes))
	fmt.Printf("   South Partition: %d nodes\n", len(southNodes))
	
	// Create proposal
	proposal := ConsensusProposal{
		ProposalID:    "PARTITION_TEST",
		Description:   "Critical Banking Policy During Network Split",
		RequiredVotes: (len(dcc.Nodes) + 1) / 2,
		UrgencyLevel:  5, // Maximum urgency
		Timestamp:     time.Now(),
	}
	
	// North partition tries consensus
	fmt.Printf("\n🔸 North Partition Consensus Attempt:\n")
	northConsensus := len(northNodes) >= proposal.RequiredVotes
	
	fmt.Printf("   Available Nodes: %d\n", len(northNodes))
	fmt.Printf("   Required Votes: %d\n", proposal.RequiredVotes)
	fmt.Printf("   Can Achieve Consensus: %t\n", northConsensus)
	
	// South partition tries consensus  
	fmt.Printf("\n🔹 South Partition Consensus Attempt:\n")
	southConsensus := len(southNodes) >= proposal.RequiredVotes
	
	fmt.Printf("   Available Nodes: %d\n", len(southNodes))
	fmt.Printf("   Required Votes: %d\n", proposal.RequiredVotes)
	fmt.Printf("   Can Achieve Consensus: %t\n", southConsensus)
	
	// Analysis
	fmt.Printf("\n📋 Partition Analysis:\n")
	if northConsensus && southConsensus {
		fmt.Printf("   ⚠️  DANGEROUS: Both partitions can achieve consensus!\n")
		fmt.Printf("   Risk: Split-brain scenario - conflicting decisions possible\n")
		fmt.Printf("   Solution: Implement partition detection and leader election\n")
	} else if northConsensus || southConsensus {
		fmt.Printf("   ✅ SAFE: Only one partition can achieve consensus\n")
		fmt.Printf("   System remains consistent during network partition\n")
	} else {
		fmt.Printf("   ❌ UNAVAILABLE: No partition can achieve consensus\n")
		fmt.Printf("   System is safe but unavailable during partition\n")
	}
}

func main() {
	// Seed random number generator
	rand.Seed(time.Now().UnixNano())
	
	fmt.Println("🇮🇳 Indian Banking Distributed Consensus Analysis")
	fmt.Println("🏛️  RBI Monetary Policy Committee Simulation")
	fmt.Println("=" + fmt.Sprintf("%60s", "="))
	
	// Create banking consensus system
	bankingSystem := NewBankingConsensusSystem()
	
	// Example 1: Interest Rate Decision
	fmt.Println("\n💰 Scenario 1: Interest Rate Revision Decision")
	
	interestRateProposal := ConsensusProposal{
		ProposalID:    "INTEREST_RATE_2024_Q3",
		Description:   "Revise repo rate from 6.5% to 6.75%",
		RequiredVotes: 4, // Need 4 out of 6 votes
		UrgencyLevel:  3, // Moderate urgency
		Timestamp:     time.Now(),
	}
	
	// Calculate probability with excellent network conditions
	consensusProbability := bankingSystem.CalculateConsensusRobability(
		interestRateProposal, 0.9,
	)
	
	// Simulate actual voting
	result := bankingSystem.SimulateConsensusRound(interestRateProposal, 0.9)
	
	fmt.Printf("\n📊 Consensus Result:\n")
	fmt.Printf("   Consensus Achieved: %t\n", result.ConsensusAchieved)
	fmt.Printf("   Accept Votes: %d/%d\n", result.AcceptVotes, result.TotalVotes)
	fmt.Printf("   Weighted Support: %.1f%%\n", result.WeightedSupport*100)
	fmt.Printf("   Duration: %v\n", result.Duration)
	
	// Example 2: Emergency Decision During Crisis
	fmt.Println("\n" + "=".repeat(60))
	fmt.Println("🚨 Scenario 2: Emergency Banking Decision (Monsoon Crisis)")
	
	emergencyProposal := ConsensusProposal{
		ProposalID:    "EMERGENCY_LIQUIDITY_2024",
		Description:   "Emergency liquidity injection ₹50,000 crores",
		RequiredVotes: 4, // Still need majority for emergency
		UrgencyLevel:  5, // Maximum urgency
		Timestamp:     time.Now(),
	}
	
	// Poor network conditions during monsoon
	bankingSystem.CalculateConsensusRobability(emergencyProposal, 0.4)
	emergencyResult := bankingSystem.SimulateConsensusRound(emergencyProposal, 0.4)
	
	fmt.Printf("\n📊 Emergency Consensus Result:\n")
	fmt.Printf("   Consensus Achieved: %t\n", emergencyResult.ConsensusAchieved)
	fmt.Printf("   Accept Votes: %d/%d\n", emergencyResult.AcceptVotes, emergencyResult.TotalVotes)
	fmt.Printf("   Weighted Support: %.1f%%\n", emergencyResult.WeightedSupport*100)
	
	// Monte Carlo Analysis
	fmt.Println("\n" + "=".repeat(60))
	bankingSystem.MonteCarloConsensusAnalysis(1000, "Banking Policy")
	
	// Network partition simulation
	fmt.Println("\n" + "=".repeat(60))
	bankingSystem.NetworkPartitionSimulation()
	
	// Business insights
	fmt.Printf("\n💼 Business Insights for Indian Banking:\n")
	fmt.Printf("   💡 Higher urgency proposals have better consensus rates\n")
	fmt.Printf("   💡 Network quality significantly impacts consensus success\n")
	fmt.Printf("   💡 Weighted voting prevents small banks from blocking decisions\n")
	fmt.Printf("   💡 Monsoon season requires backup communication channels\n")
	
	// Mumbai banking district analogy
	fmt.Printf("\n🏙️ Mumbai Banking District Analogy:\n")
	fmt.Printf("   Consensus nodes = Bank headquarters in BKC/Nariman Point\n")
	fmt.Printf("   Network partition = Monsoon flooding cutting communication\n")
	fmt.Printf("   Voting weights = Bank size and market capitalization\n")
	fmt.Printf("   Leader election = RBI governor's decisive role\n")
	fmt.Printf("   Byzantine faults = Rogue bank trying to manipulate decisions\n")
	
	// Technical recommendations
	fmt.Printf("\n🔧 Distributed Consensus Best Practices:\n")
	fmt.Printf("   1. Use weighted voting based on stake/reliability\n")
	fmt.Printf("   2. Implement partition detection and handling\n")
	Printf("   3. Set timeouts based on real network conditions\n")
	fmt.Printf("   4. Monitor node health and automatically exclude unhealthy nodes\n")
	fmt.Printf("   5. Use multiple communication channels for critical decisions\n")
}