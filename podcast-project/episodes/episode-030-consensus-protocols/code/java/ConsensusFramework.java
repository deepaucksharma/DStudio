/*
 * Generic Consensus Framework - Mumbai Committee Style!
 * ===================================================
 * 
 * Flexible framework for implementing different consensus algorithms
 * Just like Mumbai housing societies have different committee structures,
 * this framework supports multiple consensus protocols.
 * 
 * Author: Hindi Tech Podcast
 * Episode: 030 - Consensus Protocols
 */

package com.hinditechpodcast.consensus;

import java.util.*;
import java.util.concurrent.*;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

// Enums for consensus types and states
enum ConsensusType {
    MAJORITY_VOTING,
    QUORUM_BASED,
    BYZANTINE_FAULT_TOLERANT,
    PROOF_OF_STAKE,
    LEADER_ELECTION
}

enum NodeState {
    ACTIVE,
    INACTIVE,
    SUSPECTED,
    BYZANTINE
}

enum ProposalStatus {
    PENDING,
    ACCEPTED,
    REJECTED,
    COMMITTED
}

// Core interfaces for consensus framework
interface ConsensusNode {
    String getNodeId();
    NodeState getState();
    boolean vote(Proposal proposal);
    void receiveMessage(ConsensusMessage message);
    void processProposal(Proposal proposal);
}

interface ConsensusAlgorithm {
    ConsensusResult runConsensus(Proposal proposal, List<ConsensusNode> nodes);
    ConsensusType getType();
    Map<String, Object> getParameters();
}

// Core data structures
class Proposal {
    private final String proposalId;
    private final String description;
    private final String proposer;
    private final Map<String, Object> data;
    private final long timestamp;
    private ProposalStatus status;

    public Proposal(String proposalId, String description, String proposer, Map<String, Object> data) {
        this.proposalId = proposalId;
        this.description = description;
        this.proposer = proposer;
        this.data = new HashMap<>(data);
        this.timestamp = System.currentTimeMillis();
        this.status = ProposalStatus.PENDING;
    }

    // Getters and setters
    public String getProposalId() { return proposalId; }
    public String getDescription() { return description; }
    public String getProposer() { return proposer; }
    public Map<String, Object> getData() { return new HashMap<>(data); }
    public long getTimestamp() { return timestamp; }
    public ProposalStatus getStatus() { return status; }
    public void setStatus(ProposalStatus status) { this.status = status; }

    public String calculateHash() {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            String content = proposalId + ":" + description + ":" + proposer + ":" + timestamp;
            byte[] hash = digest.digest(content.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(hash).substring(0, 16);
        } catch (Exception e) {
            return "error_hash";
        }
    }

    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }

    @Override
    public String toString() {
        return String.format("Proposal{id='%s', desc='%s', proposer='%s', status=%s}",
                proposalId, description, proposer, status);
    }
}

class ConsensusMessage {
    private final String messageId;
    private final String senderId;
    private final String receiverId;
    private final String type;
    private final Map<String, Object> payload;
    private final long timestamp;

    public ConsensusMessage(String senderId, String receiverId, String type, Map<String, Object> payload) {
        this.messageId = UUID.randomUUID().toString().substring(0, 8);
        this.senderId = senderId;
        this.receiverId = receiverId;
        this.type = type;
        this.payload = new HashMap<>(payload);
        this.timestamp = System.currentTimeMillis();
    }

    // Getters
    public String getMessageId() { return messageId; }
    public String getSenderId() { return senderId; }
    public String getReceiverId() { return receiverId; }
    public String getType() { return type; }
    public Map<String, Object> getPayload() { return new HashMap<>(payload); }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return String.format("Message{id='%s', from='%s', to='%s', type='%s'}",
                messageId, senderId, receiverId, type);
    }
}

class ConsensusResult {
    private final boolean success;
    private final String result;
    private final Map<String, Object> details;
    private final long duration;
    private final int participantCount;

    public ConsensusResult(boolean success, String result, Map<String, Object> details, 
                          long duration, int participantCount) {
        this.success = success;
        this.result = result;
        this.details = new HashMap<>(details);
        this.duration = duration;
        this.participantCount = participantCount;
    }

    // Getters
    public boolean isSuccess() { return success; }
    public String getResult() { return result; }
    public Map<String, Object> getDetails() { return new HashMap<>(details); }
    public long getDuration() { return duration; }
    public int getParticipantCount() { return participantCount; }

    @Override
    public String toString() {
        return String.format("ConsensusResult{success=%s, result='%s', duration=%dms, participants=%d}",
                success, result, duration, participantCount);
    }
}

// Mumbai Housing Society Node - representing committee member
class MumbaiSocietyNode implements ConsensusNode {
    private final String nodeId;
    private NodeState state;
    private final double reliability;
    private final double responseTime; // in seconds
    private final Random random;

    // Performance metrics
    private int proposalsVoted = 0;
    private int proposalsAccepted = 0;
    private int messagesReceived = 0;

    public MumbaiSocietyNode(String nodeId, double reliability) {
        this.nodeId = nodeId;
        this.state = NodeState.ACTIVE;
        this.reliability = Math.max(0.1, Math.min(1.0, reliability));
        this.responseTime = 0.5 + Math.random() * 2.0; // 0.5-2.5 seconds
        this.random = new Random();
        
        System.out.printf("🏢 Mumbai Society Node '%s' initialized (reliability: %.2f)%n", 
                         nodeId, reliability);
    }

    @Override
    public String getNodeId() {
        return nodeId;
    }

    @Override
    public NodeState getState() {
        return state;
    }

    public void setState(NodeState state) {
        this.state = state;
    }

    @Override
    public boolean vote(Proposal proposal) {
        proposalsVoted++;

        // Simulate network delay
        try {
            Thread.sleep((long) (responseTime * 1000));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }

        // Check if node is active
        if (state != NodeState.ACTIVE) {
            System.out.printf("   ❌ %s is not active - cannot vote%n", nodeId);
            return false;
        }

        // Simulate reliability - sometimes nodes fail to respond
        if (random.nextDouble() > reliability) {
            System.out.printf("   ❌ %s failed to vote - Mumbai network issue!%n", nodeId);
            return false;
        }

        // Decision-making logic (Mumbai committee member style)
        boolean decision = makeVotingDecision(proposal);
        
        if (decision) {
            proposalsAccepted++;
        }

        String voteStr = decision ? "✅ YES" : "❌ NO";
        System.out.printf("   🗳️ %s voted: %s for proposal '%s'%n", 
                         nodeId, voteStr, proposal.getDescription());

        return decision;
    }

    private boolean makeVotingDecision(Proposal proposal) {
        // Mumbai committee member decision factors
        double societyBenefit = random.nextDouble();        // How much it benefits society
        double personalImpact = random.nextDouble();        // Personal impact
        double costConcern = random.nextDouble();          // Cost concerns
        double legalCompliance = random.nextDouble();      // Legal/regulatory compliance
        double popularSupport = random.nextDouble();       // Expected popular support

        // Weighted decision making
        double supportScore = 
            societyBenefit * 0.3 +
            (1.0 - personalImpact) * 0.2 +  // Lower personal impact is better
            (1.0 - costConcern) * 0.2 +     // Lower cost concern is better
            legalCompliance * 0.2 +
            popularSupport * 0.1;

        // Mumbai committee members are generally conservative
        double threshold = 0.55 + (random.nextDouble() * 0.2); // 0.55-0.75

        return supportScore > threshold;
    }

    @Override
    public void receiveMessage(ConsensusMessage message) {
        messagesReceived++;
        
        System.out.printf("   📨 %s received message: %s%n", nodeId, message.getType());
        
        // Process message based on type
        switch (message.getType()) {
            case "PROPOSAL":
                // Handle proposal message
                break;
            case "VOTE_REQUEST":
                // Handle vote request
                break;
            case "CONSENSUS_RESULT":
                // Handle consensus result
                break;
            default:
                System.out.printf("   ⚠️ Unknown message type: %s%n", message.getType());
        }
    }

    @Override
    public void processProposal(Proposal proposal) {
        System.out.printf("   📋 %s processing proposal: %s%n", nodeId, proposal.getDescription());
        
        // Simulate processing time
        try {
            Thread.sleep((long) (responseTime * 500)); // Half the voting time
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // Basic validation
        if (proposal.getDescription().isEmpty()) {
            System.out.printf("   ❌ %s rejects proposal - empty description%n", nodeId);
            return;
        }
        
        System.out.printf("   ✅ %s validated proposal%n", nodeId);
    }

    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("nodeId", nodeId);
        stats.put("state", state.toString());
        stats.put("reliability", reliability);
        stats.put("responseTime", responseTime);
        stats.put("proposalsVoted", proposalsVoted);
        stats.put("proposalsAccepted", proposalsAccepted);
        stats.put("messagesReceived", messagesReceived);
        stats.put("acceptanceRate", proposalsVoted > 0 ? (double) proposalsAccepted / proposalsVoted : 0.0);
        return stats;
    }
}

// Majority Voting Algorithm - Mumbai Democracy Style
class MajorityVotingAlgorithm implements ConsensusAlgorithm {
    private final double threshold;
    private final int minParticipants;

    public MajorityVotingAlgorithm(double threshold, int minParticipants) {
        this.threshold = Math.max(0.5, Math.min(1.0, threshold)); // At least 50%
        this.minParticipants = Math.max(1, minParticipants);
        
        System.out.printf("🗳️ Majority Voting Algorithm initialized (threshold: %.0f%%, min participants: %d)%n", 
                         threshold * 100, minParticipants);
    }

    @Override
    public ConsensusResult runConsensus(Proposal proposal, List<ConsensusNode> nodes) {
        long startTime = System.currentTimeMillis();
        
        System.out.printf("%n🏛️ MAJORITY VOTING CONSENSUS%n");
        System.out.printf("Proposal: %s%n", proposal.getDescription());
        System.out.printf("Nodes participating: %d%n", nodes.size());
        System.out.printf("Approval threshold: %.1f%%%n", threshold * 100);
        System.out.println("=" + "=".repeat(50));

        Map<String, Object> details = new HashMap<>();
        details.put("algorithm", "majority_voting");
        details.put("threshold", threshold);

        // Check minimum participants
        if (nodes.size() < minParticipants) {
            String error = String.format("Insufficient participants: %d < %d", nodes.size(), minParticipants);
            System.out.printf("❌ %s%n", error);
            details.put("error", error);
            return new ConsensusResult(false, "insufficient_participants", details, 
                                     System.currentTimeMillis() - startTime, nodes.size());
        }

        // Collect votes in parallel
        List<Future<Boolean>> voteFutures = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(Math.min(nodes.size(), 10));

        for (ConsensusNode node : nodes) {
            voteFutures.add(executor.submit(() -> {
                try {
                    return node.vote(proposal);
                } catch (Exception e) {
                    System.out.printf("   ❌ Voting error for %s: %s%n", node.getNodeId(), e.getMessage());
                    return false;
                }
            }));
        }

        // Collect results
        int yesVotes = 0;
        int noVotes = 0;
        int totalVotes = 0;
        List<String> voterResponses = new ArrayList<>();

        for (int i = 0; i < voteFutures.size(); i++) {
            try {
                boolean vote = voteFutures.get(i).get(10, TimeUnit.SECONDS); // 10 second timeout
                totalVotes++;
                if (vote) {
                    yesVotes++;
                } else {
                    noVotes++;
                }
                voterResponses.add(nodes.get(i).getNodeId() + ":" + (vote ? "YES" : "NO"));
            } catch (Exception e) {
                System.out.printf("   ⏰ Vote timeout for node %d%n", i);
                voterResponses.add(nodes.get(i).getNodeId() + ":TIMEOUT");
            }
        }

        executor.shutdown();

        // Calculate results
        double approvalRate = totalVotes > 0 ? (double) yesVotes / totalVotes : 0.0;
        boolean consensusReached = approvalRate >= threshold;

        // Update proposal status
        proposal.setStatus(consensusReached ? ProposalStatus.ACCEPTED : ProposalStatus.REJECTED);

        // Store details
        details.put("yesVotes", yesVotes);
        details.put("noVotes", noVotes);
        details.put("totalVotes", totalVotes);
        details.put("approvalRate", approvalRate);
        details.put("voterResponses", voterResponses);

        // Display results
        System.out.printf("%n📊 VOTING RESULTS%n");
        System.out.printf("Yes votes: %d%n", yesVotes);
        System.out.printf("No votes: %d%n", noVotes);
        System.out.printf("Total votes: %d%n", totalVotes);
        System.out.printf("Approval rate: %.1f%%%n", approvalRate * 100);
        System.out.printf("Consensus: %s%n", consensusReached ? "✅ REACHED" : "❌ FAILED");

        String result = consensusReached ? "accepted" : "rejected";
        long duration = System.currentTimeMillis() - startTime;

        return new ConsensusResult(consensusReached, result, details, duration, totalVotes);
    }

    @Override
    public ConsensusType getType() {
        return ConsensusType.MAJORITY_VOTING;
    }

    @Override
    public Map<String, Object> getParameters() {
        Map<String, Object> params = new HashMap<>();
        params.put("threshold", threshold);
        params.put("minParticipants", minParticipants);
        return params;
    }
}

// Main Consensus Framework Class
public class ConsensusFramework {
    private final List<ConsensusNode> nodes;
    private final Map<String, ConsensusAlgorithm> algorithms;
    private final List<ConsensusResult> history;

    public ConsensusFramework() {
        this.nodes = new ArrayList<>();
        this.algorithms = new HashMap<>();
        this.history = new ArrayList<>();
        
        System.out.println("🏗️ Consensus Framework initialized");
    }

    public void addNode(ConsensusNode node) {
        nodes.add(node);
        System.out.printf("➕ Added node: %s%n", node.getNodeId());
    }

    public void addAlgorithm(String name, ConsensusAlgorithm algorithm) {
        algorithms.put(name, algorithm);
        System.out.printf("➕ Added algorithm: %s (%s)%n", name, algorithm.getType());
    }

    public ConsensusResult runConsensus(String algorithmName, Proposal proposal) {
        ConsensusAlgorithm algorithm = algorithms.get(algorithmName);
        if (algorithm == null) {
            throw new IllegalArgumentException("Unknown algorithm: " + algorithmName);
        }

        System.out.printf("%n🚀 RUNNING CONSENSUS%n");
        System.out.printf("Algorithm: %s%n", algorithmName);
        System.out.printf("Proposal: %s%n", proposal.getDescription());
        System.out.printf("Timestamp: %s%n", 
                         LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));

        ConsensusResult result = algorithm.runConsensus(proposal, new ArrayList<>(nodes));
        history.add(result);

        System.out.printf("%n🏁 CONSENSUS COMPLETED%n");
        System.out.printf("Result: %s%n", result);
        
        return result;
    }

    public List<ConsensusResult> getHistory() {
        return new ArrayList<>(history);
    }

    public Map<String, Object> getFrameworkStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalNodes", nodes.size());
        stats.put("totalAlgorithms", algorithms.size());
        stats.put("consensusRuns", history.size());
        
        // Calculate success rate
        long successfulRuns = history.stream()
                .mapToLong(result -> result.isSuccess() ? 1 : 0)
                .sum();
        stats.put("successRate", history.size() > 0 ? (double) successfulRuns / history.size() : 0.0);
        
        // Average duration
        double avgDuration = history.stream()
                .mapToLong(ConsensusResult::getDuration)
                .average()
                .orElse(0.0);
        stats.put("averageDuration", avgDuration);
        
        return stats;
    }

    // Mumbai Society Simulation
    public static void simulateMumbaiSocietyMeeting() {
        System.out.println("🌆 MUMBAI HOUSING SOCIETY CONSENSUS SIMULATION");
        System.out.println("=" + "=".repeat(60));

        // Create consensus framework
        ConsensusFramework framework = new ConsensusFramework();

        // Add Mumbai society committee members
        String[] memberNames = {
            "Sharma_Uncle", "Patel_Aunti", "Iyer_Sir", "Khan_Bhai",
            "Gupta_Madam", "Fernandes_Sir", "Joshi_Uncle", "Rao_Madam"
        };

        for (String memberName : memberNames) {
            double reliability = 0.7 + Math.random() * 0.25; // 70-95% reliability
            framework.addNode(new MumbaiSocietyNode(memberName, reliability));
        }

        // Add majority voting algorithm
        framework.addAlgorithm("majority_vote", new MajorityVotingAlgorithm(0.6, 5));

        // Society proposals
        List<Proposal> proposals = Arrays.asList(
            new Proposal("PROP001", "Install CCTV cameras in building", "Security_Committee", 
                        Map.of("cost", 50000, "vendor", "Mumbai Security Systems")),
            
            new Proposal("PROP002", "Renovate society garden", "Garden_Committee", 
                        Map.of("cost", 30000, "timeline", "2 months")),
            
            new Proposal("PROP003", "Increase maintenance charges by 15%", "Managing_Committee", 
                        Map.of("currentAmount", 2000, "newAmount", 2300, "reason", "inflation")),
            
            new Proposal("PROP004", "Allow pets in common areas", "Residents_Committee", 
                        Map.of("restrictions", "leash required", "timings", "6AM-8AM, 6PM-8PM")),
            
            new Proposal("PROP005", "Install solar panels on terrace", "Green_Committee", 
                        Map.of("cost", 200000, "savings", "30% electricity bill", "payback", "5 years"))
        );

        // Run consensus for each proposal
        List<ConsensusResult> results = new ArrayList<>();
        for (int i = 0; i < proposals.size(); i++) {
            Proposal proposal = proposals.get(i);
            
            System.out.printf("%n" + "=".repeat(70));
            System.out.printf("%nPROPOSAL %d/%d: %s%n", i + 1, proposals.size(), proposal.getDescription());
            System.out.printf("=".repeat(70));
            
            ConsensusResult result = framework.runConsensus("majority_vote", proposal);
            results.add(result);
            
            // Brief pause between proposals
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        // Summary
        System.out.printf("%n📈 SOCIETY MEETING SUMMARY%n");
        System.out.println("=" + "=".repeat(40));

        int acceptedProposals = 0;
        long totalDuration = 0;

        for (int i = 0; i < results.size(); i++) {
            ConsensusResult result = results.get(i);
            String status = result.isSuccess() ? "✅ ACCEPTED" : "❌ REJECTED";
            System.out.printf("Proposal %d: %s (%.1fs)%n", i + 1, status, result.getDuration() / 1000.0);
            
            if (result.isSuccess()) {
                acceptedProposals++;
            }
            totalDuration += result.getDuration();
        }

        System.out.printf("%nProposals accepted: %d/%d%n", acceptedProposals, proposals.size());
        System.out.printf("Success rate: %.1f%%%n", (double) acceptedProposals / proposals.size() * 100);
        System.out.printf("Total meeting time: %.1fs%n", totalDuration / 1000.0);

        // Framework statistics
        Map<String, Object> frameworkStats = framework.getFrameworkStats();
        System.out.printf("%n📊 Framework Performance:%n");
        System.out.printf("Total nodes: %s%n", frameworkStats.get("totalNodes"));
        System.out.printf("Success rate: %.1f%%%n", (Double) frameworkStats.get("successRate") * 100);
        System.out.printf("Average duration: %.0fms%n", frameworkStats.get("averageDuration"));

        System.out.println("\n🎊 Mumbai Society Meeting Simulation Completed!");
        System.out.println("Key insight: Like Mumbai society meetings, consensus needs patience and participation!");
    }

    public static void main(String[] args) {
        System.out.println("🚀 CONSENSUS FRAMEWORK DEMONSTRATION");
        System.out.println("Mumbai Housing Society Committee System");
        System.out.println("=" + "=".repeat(60));

        try {
            simulateMumbaiSocietyMeeting();
        } catch (Exception e) {
            System.err.printf("❌ Error in consensus simulation: %s%n", e.getMessage());
            e.printStackTrace();
        }
    }
}