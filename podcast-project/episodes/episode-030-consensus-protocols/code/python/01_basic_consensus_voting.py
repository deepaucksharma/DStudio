#!/usr/bin/env python3
"""
Basic Consensus Voting Implementation
=====================================

Mumbai Local Train ki tarah - sabko agreement chahiye destination ke liye!
Just like Mumbai local trains need agreement on the destination, 
distributed systems need consensus on decisions.

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from collections import defaultdict

class VoteType(Enum):
    """Vote types - Mumbai election style"""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

@dataclass
class Proposal:
    """
    Proposal data structure - Mumbai Municipal Corporation proposal style
    """
    proposal_id: str
    description: str
    proposer: str
    timestamp: float
    data: Optional[Dict] = None

@dataclass
class Vote:
    """
    Vote structure - like Mumbai election ballot
    """
    voter_id: str
    proposal_id: str
    vote_type: VoteType
    timestamp: float
    signature: Optional[str] = None

class BasicConsensusNode:
    """
    Basic consensus node - har Mumbai society mein committee member
    Like every Mumbai housing society committee member
    """
    
    def __init__(self, node_id: str, total_nodes: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.votes_received: Dict[str, List[Vote]] = defaultdict(list)
        self.proposals: Dict[str, Proposal] = {}
        self.consensus_results: Dict[str, Tuple[bool, Dict]] = {}
        self.is_active = True
        self.network_delay = random.uniform(0.1, 0.5)  # Mumbai traffic delay!
        
        # Mumbai society committee member characteristics
        self.reliability = random.uniform(0.7, 0.99)  # Some members are more reliable
        self.response_time = random.uniform(1.0, 5.0)  # Some are quick responders
        
        print(f"🏢 Node {self.node_id} initialized - Mumbai society committee member ready!")
    
    def create_proposal(self, description: str, data: Optional[Dict] = None) -> Proposal:
        """
        Create new proposal - Mumbai society mein naya proposal
        Like creating a new proposal in Mumbai housing society
        """
        proposal_id = f"prop_{self.node_id}_{int(time.time() * 1000)}"
        proposal = Proposal(
            proposal_id=proposal_id,
            description=description,
            proposer=self.node_id,
            timestamp=time.time(),
            data=data or {}
        )
        
        self.proposals[proposal_id] = proposal
        print(f"📝 Node {self.node_id} created proposal: {description}")
        return proposal
    
    def cast_vote(self, proposal_id: str, vote_type: VoteType, 
                  reason: str = "") -> Vote:
        """
        Cast vote on proposal - Mumbai style voting
        """
        if not self.is_active:
            raise Exception(f"Node {self.node_id} is inactive - like member absent from meeting!")
        
        # Simulate Mumbai traffic delay in vote casting
        time.sleep(self.network_delay)
        
        # Simulate reliability - some votes might fail
        if random.random() > self.reliability:
            print(f"❌ Node {self.node_id} vote failed - network issue (Mumbai bandwidth problem!)")
            return None
        
        vote = Vote(
            voter_id=self.node_id,
            proposal_id=proposal_id,
            vote_type=vote_type,
            timestamp=time.time(),
            signature=f"sig_{self.node_id}_{proposal_id}"
        )
        
        print(f"🗳️ Node {self.node_id} voted {vote_type.value} for proposal {proposal_id}")
        if reason:
            print(f"   Reason: {reason}")
        
        return vote
    
    def receive_vote(self, vote: Vote):
        """
        Receive vote from other node - like collecting ballot papers
        """
        if not vote:
            return
        
        self.votes_received[vote.proposal_id].append(vote)
        print(f"📥 Node {self.node_id} received vote from {vote.voter_id}")
    
    def check_consensus(self, proposal_id: str, 
                       threshold: float = 0.5) -> Tuple[bool, Dict]:
        """
        Check if consensus reached - Mumbai majority rule
        """
        if proposal_id not in self.votes_received:
            return False, {"status": "no_votes", "votes": []}
        
        votes = self.votes_received[proposal_id]
        total_votes = len(votes)
        
        # Count votes - Mumbai election counting style
        vote_counts = {
            VoteType.YES: 0,
            VoteType.NO: 0,
            VoteType.ABSTAIN: 0
        }
        
        for vote in votes:
            vote_counts[vote.vote_type] += 1
        
        # Check if we have enough votes (quorum)
        quorum_required = max(1, int(self.total_nodes * 0.5) + 1)  # Simple majority
        
        if total_votes < quorum_required:
            return False, {
                "status": "insufficient_votes",
                "required": quorum_required,
                "received": total_votes,
                "counts": {vt.value: count for vt, count in vote_counts.items()}
            }
        
        # Check consensus based on threshold
        yes_percentage = vote_counts[VoteType.YES] / total_votes
        consensus_reached = yes_percentage > threshold
        
        result = {
            "status": "consensus_reached" if consensus_reached else "consensus_failed",
            "total_votes": total_votes,
            "yes_votes": vote_counts[VoteType.YES],
            "no_votes": vote_counts[VoteType.NO],
            "abstain_votes": vote_counts[VoteType.ABSTAIN],
            "yes_percentage": yes_percentage,
            "threshold": threshold,
            "consensus": consensus_reached
        }
        
        self.consensus_results[proposal_id] = (consensus_reached, result)
        return consensus_reached, result

class MumbaiSocietyConsensus:
    """
    Mumbai Housing Society Consensus System
    Real-world example: Society committee decisions
    """
    
    def __init__(self, num_members: int = 7):
        self.members = []
        self.num_members = num_members
        
        # Create society committee members
        member_names = [
            "Sharma_Uncle", "Patel_Aunti", "Iyer_Sir", 
            "Khan_Bhai", "Gupta_Madam", "Fernandes_Sir", "Joshi_Uncle"
        ]
        
        for i in range(num_members):
            member_id = member_names[i] if i < len(member_names) else f"Member_{i+1}"
            node = BasicConsensusNode(member_id, num_members)
            self.members.append(node)
        
        print(f"🏠 Mumbai Housing Society consensus system initialized with {num_members} members")
    
    def run_consensus_round(self, proposer_idx: int, 
                          proposal_desc: str, 
                          proposal_data: Dict = None) -> Dict:
        """
        Run complete consensus round - Mumbai society meeting
        """
        print(f"\n{'='*60}")
        print(f"🏛️ MUMBAI SOCIETY COMMITTEE MEETING STARTED")
        print(f"{'='*60}")
        
        # Step 1: Create proposal
        proposer = self.members[proposer_idx]
        proposal = proposer.create_proposal(proposal_desc, proposal_data)
        
        print(f"\n📋 Proposal Details:")
        print(f"   ID: {proposal.proposal_id}")
        print(f"   Description: {proposal.description}")
        print(f"   Proposer: {proposal.proposer}")
        
        # Step 2: Voting phase (parallel voting)
        print(f"\n🗳️ VOTING PHASE STARTED")
        print("-" * 40)
        
        votes = []
        vote_threads = []
        
        def cast_vote_async(member, proposal_id):
            # Each member makes decision based on their characteristics
            decision_factors = random.random()
            
            if decision_factors > 0.7:
                vote_type = VoteType.YES
                reason = "Good for society development"
            elif decision_factors > 0.3:
                vote_type = VoteType.NO
                reason = "Concerns about implementation"
            else:
                vote_type = VoteType.ABSTAIN
                reason = "Need more information"
            
            vote = member.cast_vote(proposal_id, vote_type, reason)
            if vote:
                votes.append(vote)
        
        # Start parallel voting (Mumbai style - everyone talks at once!)
        for member in self.members:
            if member.node_id != proposer.node_id:  # Proposer doesn't vote
                thread = threading.Thread(
                    target=cast_vote_async, 
                    args=(member, proposal.proposal_id)
                )
                vote_threads.append(thread)
                thread.start()
        
        # Wait for all votes
        for thread in vote_threads:
            thread.join()
        
        # Step 3: Distribute votes to all nodes
        print(f"\n📤 VOTE DISTRIBUTION PHASE")
        print("-" * 40)
        
        for member in self.members:
            for vote in votes:
                member.receive_vote(vote)
        
        # Step 4: Check consensus
        print(f"\n🔍 CONSENSUS CHECKING PHASE")
        print("-" * 40)
        
        consensus_results = []
        for member in self.members:
            consensus, result = member.check_consensus(proposal.proposal_id)
            consensus_results.append((member.node_id, consensus, result))
        
        # All nodes should have same result (in ideal case)
        final_consensus = consensus_results[0][1] if consensus_results else False
        final_result = consensus_results[0][2] if consensus_results else {}
        
        print(f"\n📊 CONSENSUS RESULTS")
        print("=" * 40)
        print(f"Proposal: {proposal.description}")
        print(f"Total Votes: {final_result.get('total_votes', 0)}")
        print(f"YES: {final_result.get('yes_votes', 0)}")
        print(f"NO: {final_result.get('no_votes', 0)}")
        print(f"ABSTAIN: {final_result.get('abstain_votes', 0)}")
        print(f"YES %: {final_result.get('yes_percentage', 0)*100:.1f}%")
        print(f"Consensus: {'✅ REACHED' if final_consensus else '❌ FAILED'}")
        
        return {
            "proposal": proposal,
            "votes": votes,
            "consensus_reached": final_consensus,
            "result_details": final_result,
            "node_results": consensus_results
        }

def simulate_mumbai_scenarios():
    """
    Simulate real Mumbai scenarios
    """
    print("🌆 MUMBAI CONSENSUS SCENARIOS SIMULATION")
    print("=" * 50)
    
    # Scenario 1: Small society decision
    print("\n📍 Scenario 1: 5-member society deciding on elevator maintenance")
    society = MumbaiSocietyConsensus(5)
    result1 = society.run_consensus_round(
        0, 
        "Elevator maintenance - Rs 50,000", 
        {"cost": 50000, "contractor": "Mumbai Elevators Ltd"}
    )
    
    # Scenario 2: Large society decision
    print("\n📍 Scenario 2: 7-member society deciding on swimming pool construction")
    society2 = MumbaiSocietyConsensus(7)
    result2 = society2.run_consensus_round(
        2, 
        "Swimming pool construction - Rs 15 lakhs", 
        {"cost": 1500000, "area": "terrace", "contractor": "AquaTech Mumbai"}
    )
    
    # Scenario 3: Controversial decision
    print("\n📍 Scenario 3: Controversial parking policy change")
    result3 = society2.run_consensus_round(
        1, 
        "Ban visitor parking after 10 PM", 
        {"enforcement": "security_guard", "fine": 500}
    )
    
    return [result1, result2, result3]

def demonstrate_consensus_properties():
    """
    Demonstrate key consensus properties
    """
    print("\n🎯 CONSENSUS PROPERTIES DEMONSTRATION")
    print("=" * 50)
    
    society = MumbaiSocietyConsensus(5)
    
    # Test different scenarios
    scenarios = [
        ("Install CCTV cameras", {"cost": 25000}),
        ("Allow pets in common areas", {"rules": "leash_required"}),
        ("Increase maintenance by 20%", {"current": 2000, "new": 2400}),
    ]
    
    results = []
    for desc, data in scenarios:
        result = society.run_consensus_round(0, desc, data)
        results.append(result)
        
        print(f"\n📈 Performance Metrics:")
        print(f"   Vote Collection Time: ~{len(society.members) * 0.3:.1f}s")
        print(f"   Consensus Check Time: ~{len(society.members) * 0.1:.1f}s")
        print(f"   Network Messages: {len(society.members) * (len(society.members) - 1)}")
        
        time.sleep(1)  # Brief pause between scenarios
    
    return results

if __name__ == "__main__":
    print("🚀 BASIC CONSENSUS VOTING SYSTEM")
    print("Mumbai Housing Society Committee Simulation")
    print("=" * 60)
    
    try:
        # Run Mumbai scenarios
        scenario_results = simulate_mumbai_scenarios()
        
        # Demonstrate consensus properties
        property_results = demonstrate_consensus_properties()
        
        print("\n🎊 SIMULATION COMPLETED SUCCESSFULLY!")
        print(f"Total scenarios tested: {len(scenario_results) + len(property_results)}")
        print("Key learning: Like Mumbai local trains, consensus needs everyone to agree on destination!")
        
    except Exception as e:
        print(f"❌ Error in consensus simulation: {e}")
        raise