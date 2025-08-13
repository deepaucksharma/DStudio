#!/usr/bin/env python3
"""
Indian Parliament Consensus Simulation
=====================================

Real Indian Parliamentary System - Lok Sabha voting consensus!
Complete simulation of how consensus works in Indian democracy,
from bill introduction to presidential assent.

Features:
- Multi-party system with coalitions
- Voting procedures (voice vote, division, etc.)
- Quorum requirements 
- Anti-defection law simulation
- Rajya Sabha coordination

Author: Hindi Tech Podcast  
Episode: 030 - Consensus Protocols
"""

import time
import random
import threading
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, Counter
import uuid

class PartyType(Enum):
    """Indian Political Parties"""
    BJP = "bharatiya_janata_party"
    CONGRESS = "indian_national_congress"
    AAP = "aam_aadmi_party"
    TMC = "trinamool_congress"
    DMK = "dravida_munnetra_kazhagam"
    SP = "samajwadi_party"
    BSP = "bahujan_samaj_party"
    JDU = "janata_dal_united"
    SHIV_SENA = "shiv_sena"
    INDEPENDENT = "independent"

class VoteType(Enum):
    """Types of votes in Indian Parliament"""
    VOICE_VOTE = "voice_vote"        # Ayes and Noes
    DIVISION = "division"            # Counted vote
    SECRET_BALLOT = "secret_ballot"   # Anonymous voting

class BillType(Enum):
    """Types of bills in Indian Parliament"""
    MONEY_BILL = "money_bill"           # Financial matters
    ORDINARY_BILL = "ordinary_bill"     # General legislation
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"  # Constitution changes

class VoteDecision(Enum):
    """Vote decisions"""
    AYE = "aye"           # Support
    NOE = "noe"           # Opposition  
    ABSTAIN = "abstain"   # No participation
    ABSENT = "absent"     # Not present

@dataclass
class Bill:
    """
    Parliamentary bill structure
    """
    bill_id: str
    title: str
    bill_type: BillType
    introduced_by: str
    party: PartyType
    description: str
    urgency: str = "normal"  # normal, urgent, emergency
    financial_impact: Optional[float] = None  # In crores
    timestamp: float = field(default_factory=time.time)
    
    def get_required_majority(self) -> float:
        """Get required majority for bill passage"""
        if self.bill_type == BillType.CONSTITUTIONAL_AMENDMENT:
            return 0.67  # 2/3rd majority
        elif self.bill_type == BillType.MONEY_BILL:
            return 0.5   # Simple majority in Lok Sabha only
        else:
            return 0.5   # Simple majority

@dataclass
class MP:
    """
    Member of Parliament - Lok Sabha/Rajya Sabha
    """
    mp_id: str
    name: str
    party: PartyType
    constituency: str
    house: str  # lok_sabha or rajya_sabha
    state: str
    
    # Behavioral characteristics (Mumbai MP style!)
    attendance_rate: float = field(default_factory=lambda: random.uniform(0.7, 0.95))
    party_loyalty: float = field(default_factory=lambda: random.uniform(0.8, 0.98))
    independent_thinking: float = field(default_factory=lambda: random.uniform(0.1, 0.4))
    
    # Performance tracking
    bills_voted: int = 0
    party_line_votes: int = 0
    independent_votes: int = 0
    absences: int = 0
    
    def will_attend_session(self) -> bool:
        """Check if MP will attend session - Mumbai traffic delays!"""
        return random.random() < self.attendance_rate
    
    def decide_vote(self, bill: Bill, party_whip: VoteDecision) -> VoteDecision:
        """
        Decide how to vote on bill - complex Indian political dynamics
        """
        if not self.will_attend_session():
            self.absences += 1
            return VoteDecision.ABSENT
        
        self.bills_voted += 1
        
        # Anti-defection law consideration
        if party_whip != VoteDecision.ABSTAIN:
            # Strong party whip - anti-defection risk
            if random.random() < self.party_loyalty:
                self.party_line_votes += 1
                return party_whip
        
        # Independent decision making
        decision_factors = {
            "constituency_benefit": random.uniform(0, 1),
            "personal_conviction": random.uniform(0, 1),
            "party_pressure": self.party_loyalty,
            "public_opinion": random.uniform(0, 1),
            "media_attention": random.uniform(0, 1)
        }
        
        # Weighted decision
        support_score = (
            decision_factors["constituency_benefit"] * 0.3 +
            decision_factors["personal_conviction"] * 0.2 +
            decision_factors["party_pressure"] * 0.3 +
            decision_factors["public_opinion"] * 0.1 +
            decision_factors["media_attention"] * 0.1
        )
        
        self.independent_votes += 1
        
        if support_score > 0.6:
            return VoteDecision.AYE
        elif support_score < 0.4:
            return VoteDecision.NOE
        else:
            return VoteDecision.ABSTAIN
    
    def get_performance_stats(self) -> Dict:
        """Get MP performance statistics"""
        total_votes = self.bills_voted
        if total_votes == 0:
            return {"mp_id": self.mp_id, "no_voting_data": True}
        
        return {
            "mp_id": self.mp_id,
            "name": self.name,
            "party": self.party.value,
            "constituency": self.constituency,
            "attendance_rate": self.attendance_rate,
            "bills_voted": self.bills_voted,
            "party_loyalty_rate": self.party_line_votes / total_votes,
            "independent_vote_rate": self.independent_votes / total_votes,
            "absence_count": self.absences
        }

class ParliamentaryParty:
    """
    Political party in parliament with whip system
    """
    
    def __init__(self, party_type: PartyType, mps: List[MP]):
        self.party_type = party_type
        self.mps = mps
        self.party_strength = len(mps)
        
        # Coalition dynamics
        self.coalition_partners: List[PartyType] = []
        self.opposition_parties: Set[PartyType] = set()
        
        # Party characteristics
        self.discipline_level = random.uniform(0.8, 0.95)  # Internal discipline
        self.ideology_consistency = random.uniform(0.7, 0.9)
        
        print(f"🏛️ Party {party_type.value} formed with {len(mps)} MPs")
    
    def issue_party_whip(self, bill: Bill) -> VoteDecision:
        """
        Issue party whip for voting - Indian party line decision
        """
        # Party decision based on various factors
        decision_factors = {
            "ideological_alignment": self.calculate_ideological_alignment(bill),
            "coalition_dynamics": self.consider_coalition_position(bill),
            "electoral_impact": random.uniform(0, 1),
            "pressure_group_influence": random.uniform(0, 1),
            "leadership_directive": random.uniform(0.8, 1.0)  # Strong in Indian politics
        }
        
        # Calculate overall party position
        support_score = sum(decision_factors.values()) / len(decision_factors)
        
        if support_score > 0.65:
            whip_decision = VoteDecision.AYE
        elif support_score < 0.35:
            whip_decision = VoteDecision.NOE
        else:
            whip_decision = VoteDecision.ABSTAIN
        
        print(f"   📢 {self.party_type.value} issues {whip_decision.value} whip (support score: {support_score:.2f})")
        return whip_decision
    
    def calculate_ideological_alignment(self, bill: Bill) -> float:
        """Calculate how bill aligns with party ideology"""
        # Simplified ideological calculation
        alignment_map = {
            PartyType.BJP: {
                BillType.CONSTITUTIONAL_AMENDMENT: 0.7,
                BillType.MONEY_BILL: 0.8,
                BillType.ORDINARY_BILL: 0.6
            },
            PartyType.CONGRESS: {
                BillType.CONSTITUTIONAL_AMENDMENT: 0.6,
                BillType.MONEY_BILL: 0.5,
                BillType.ORDINARY_BILL: 0.7
            }
            # Add more parties as needed
        }
        
        return alignment_map.get(self.party_type, {}).get(bill.bill_type, 0.5)
    
    def consider_coalition_position(self, bill: Bill) -> float:
        """Consider coalition partner positions"""
        if not self.coalition_partners:
            return 0.5  # Neutral if no coalition
        
        # Simplified coalition consensus
        return random.uniform(0.4, 0.8)
    
    def get_party_stats(self) -> Dict:
        """Get party performance statistics"""
        mp_stats = [mp.get_performance_stats() for mp in self.mps]
        
        # Calculate party-level metrics
        total_attendance = sum(1 - mp.absences / max(1, mp.bills_voted) for mp in self.mps) / len(self.mps)
        party_discipline = sum(mp.party_line_votes / max(1, mp.bills_voted) for mp in self.mps) / len(self.mps)
        
        return {
            "party": self.party_type.value,
            "strength": self.party_strength,
            "average_attendance": total_attendance,
            "party_discipline": party_discipline,
            "coalition_partners": [p.value for p in self.coalition_partners],
            "mp_details": mp_stats
        }

class IndianParliament:
    """
    Complete Indian Parliament System - Lok Sabha + Rajya Sabha
    """
    
    def __init__(self):
        # Constitutional parameters
        self.lok_sabha_strength = 543  # Current strength
        self.rajya_sabha_strength = 245
        self.lok_sabha_quorum = 55     # 1/10th of total strength
        self.rajya_sabha_quorum = 25   # 1/10th of total strength
        
        # Initialize houses
        self.lok_sabha_mps: List[MP] = []
        self.rajya_sabha_mps: List[MP] = []
        self.parties: Dict[PartyType, ParliamentaryParty] = {}
        
        # Session management
        self.current_session = "winter_session_2024"
        self.bills_introduced = 0
        self.bills_passed = 0
        self.bills_rejected = 0
        
        # Performance tracking
        self.voting_history: List[Dict] = []
        
        print("🏛️ Indian Parliament System Initialized")
        print(f"   Lok Sabha: {self.lok_sabha_strength} seats")
        print(f"   Rajya Sabha: {self.rajya_sabha_strength} seats")
        
        # Create simplified parliament for simulation
        self.create_sample_parliament()
    
    def create_sample_parliament(self):
        """
        Create sample parliament with major parties - Mumbai constituencies
        """
        # Sample party strengths (simplified)
        party_strengths = {
            PartyType.BJP: 120,
            PartyType.CONGRESS: 80,
            PartyType.AAP: 15,
            PartyType.TMC: 20,
            PartyType.DMK: 12,
            PartyType.SP: 18,
            PartyType.SHIV_SENA: 10,
            PartyType.INDEPENDENT: 25
        }
        
        # Mumbai and Maharashtra constituencies
        mumbai_constituencies = [
            "Mumbai_North", "Mumbai_South", "Mumbai_Central", "Bandra_East",
            "Andheri_West", "Borivali", "Thane", "Kalyan", "Pune_Central",
            "Nagpur", "Aurangabad", "Nashik"
        ]
        
        mp_counter = 0
        
        for party_type, strength in party_strengths.items():
            party_mps = []
            
            for i in range(strength):
                constituency = random.choice(mumbai_constituencies)
                state = "Maharashtra" if constituency.startswith("Mumbai") else "Various"
                
                mp = MP(
                    mp_id=f"mp_{mp_counter:03d}",
                    name=f"MP_{party_type.value}_{i+1}",
                    party=party_type,
                    constituency=constituency,
                    house="lok_sabha",  # Simplified to Lok Sabha only for this simulation
                    state=state
                )
                
                party_mps.append(mp)
                self.lok_sabha_mps.append(mp)
                mp_counter += 1
            
            # Create party organization
            party = ParliamentaryParty(party_type, party_mps)
            self.parties[party_type] = party
        
        # Set up coalitions (simplified)
        if PartyType.BJP in self.parties and PartyType.SHIV_SENA in self.parties:
            self.parties[PartyType.BJP].coalition_partners.append(PartyType.SHIV_SENA)
            self.parties[PartyType.SHIV_SENA].coalition_partners.append(PartyType.BJP)
        
        print(f"✅ Created sample parliament with {len(self.lok_sabha_mps)} MPs across {len(self.parties)} parties")
    
    def introduce_bill(self, title: str, bill_type: BillType, 
                      introduced_by: str, party: PartyType,
                      description: str, **kwargs) -> Bill:
        """
        Introduce new bill in parliament
        """
        self.bills_introduced += 1
        
        bill = Bill(
            bill_id=f"bill_{self.bills_introduced:03d}",
            title=title,
            bill_type=bill_type,
            introduced_by=introduced_by,
            party=party,
            description=description,
            **kwargs
        )
        
        print(f"\n📜 BILL INTRODUCED IN PARLIAMENT")
        print(f"   Title: {bill.title}")
        print(f"   Type: {bill.bill_type.value}")
        print(f"   Introduced by: {bill.introduced_by} ({party.value})")
        print(f"   Bill ID: {bill.bill_id}")
        
        return bill
    
    def conduct_parliamentary_voting(self, bill: Bill, 
                                   vote_type: VoteType = VoteType.DIVISION) -> Dict:
        """
        Conduct complete parliamentary voting process
        """
        print(f"\n🗳️ PARLIAMENTARY VOTING SESSION")
        print(f"   Bill: {bill.title}")
        print(f"   Vote Type: {vote_type.value}")
        print(f"   Required Majority: {bill.get_required_majority()*100}%")
        print("-" * 50)
        
        # Check quorum
        present_mps = [mp for mp in self.lok_sabha_mps if mp.will_attend_session()]
        
        if len(present_mps) < self.lok_sabha_quorum:
            print(f"❌ QUORUM NOT MET: Only {len(present_mps)} MPs present, need {self.lok_sabha_quorum}")
            return {
                "result": "quorum_not_met",
                "present_mps": len(present_mps),
                "required_quorum": self.lok_sabha_quorum
            }
        
        print(f"✅ Quorum met: {len(present_mps)} MPs present")
        
        # Phase 1: Party whips issue directions
        print(f"\n📢 PARTY WHIP PHASE")
        party_whips = {}
        for party_type, party in self.parties.items():
            whip_decision = party.issue_party_whip(bill)
            party_whips[party_type] = whip_decision
        
        # Phase 2: Individual MP voting
        print(f"\n🗳️ VOTING PHASE")
        vote_results = {
            VoteDecision.AYE: [],
            VoteDecision.NOE: [],
            VoteDecision.ABSTAIN: [],
            VoteDecision.ABSENT: []
        }
        
        # Parallel voting simulation
        voting_threads = []
        vote_lock = threading.Lock()
        
        def cast_mp_vote(mp: MP):
            party_whip = party_whips.get(mp.party, VoteDecision.ABSTAIN)
            vote_decision = mp.decide_vote(bill, party_whip)
            
            with vote_lock:
                vote_results[vote_decision].append(mp)
        
        # Start voting
        for mp in present_mps:
            thread = threading.Thread(target=cast_mp_vote, args=(mp,))
            voting_threads.append(thread)
            thread.start()
        
        # Wait for all votes
        for thread in voting_threads:
            thread.join()
        
        # Phase 3: Count votes and determine result
        return self.count_votes_and_determine_result(bill, vote_results, vote_type)
    
    def count_votes_and_determine_result(self, bill: Bill, 
                                       vote_results: Dict, 
                                       vote_type: VoteType) -> Dict:
        """
        Count votes and determine parliamentary result
        """
        print(f"\n📊 VOTE COUNTING PHASE")
        print("-" * 30)
        
        # Count votes
        ayes = len(vote_results[VoteDecision.AYE])
        noes = len(vote_results[VoteDecision.NOE])
        abstentions = len(vote_results[VoteDecision.ABSTAIN])
        absents = len(vote_results[VoteDecision.ABSENT])
        
        total_present = ayes + noes + abstentions
        total_votes_cast = ayes + noes  # Abstentions don't count in division
        
        print(f"   Ayes: {ayes}")
        print(f"   Noes: {noes}")
        print(f"   Abstentions: {abstentions}")
        print(f"   Absents: {absents}")
        print(f"   Total Present: {total_present}")
        
        # Determine result
        required_majority = bill.get_required_majority()
        
        if total_votes_cast == 0:
            result = "no_decision"
            bill_passed = False
        else:
            aye_percentage = ayes / total_votes_cast
            bill_passed = aye_percentage > required_majority
            result = "passed" if bill_passed else "rejected"
        
        # Update parliament statistics
        if bill_passed:
            self.bills_passed += 1
        else:
            self.bills_rejected += 1
        
        print(f"\n🎯 VOTING RESULT")
        print("=" * 30)
        print(f"   Bill: {bill.title}")
        print(f"   Result: {result.upper()}")
        print(f"   Aye Percentage: {aye_percentage*100:.1f}%")
        print(f"   Required: {required_majority*100:.1f}%")
        print(f"   Margin: {(aye_percentage - required_majority)*100:.1f}%")
        
        # Analyze party-wise voting pattern
        party_voting_analysis = self.analyze_party_voting(vote_results)
        
        # Store voting history
        voting_record = {
            "bill": bill.__dict__,
            "vote_type": vote_type.value,
            "result": result,
            "bill_passed": bill_passed,
            "vote_counts": {
                "ayes": ayes,
                "noes": noes,
                "abstentions": abstentions,
                "absents": absents
            },
            "party_analysis": party_voting_analysis,
            "timestamp": time.time()
        }
        
        self.voting_history.append(voting_record)
        
        return voting_record
    
    def analyze_party_voting(self, vote_results: Dict) -> Dict:
        """
        Analyze party-wise voting patterns
        """
        party_votes = defaultdict(lambda: {"ayes": 0, "noes": 0, "abstentions": 0, "absents": 0})
        
        for decision, mps in vote_results.items():
            for mp in mps:
                party_votes[mp.party.value][decision.value.replace("abstain", "abstentions").replace("absent", "absents")] += 1
        
        return dict(party_votes)
    
    def simulate_parliament_session(self) -> List[Dict]:
        """
        Simulate complete parliament session with multiple bills
        """
        print("🏛️ PARLIAMENT SESSION SIMULATION")
        print(f"Session: {self.current_session}")
        print("=" * 60)
        
        # Sample bills for the session
        sample_bills = [
            {
                "title": "Mumbai Metro Expansion Act 2024",
                "bill_type": BillType.MONEY_BILL,
                "introduced_by": "Transport_Minister",
                "party": PartyType.BJP,
                "description": "Funding for Mumbai Metro Phase 4",
                "financial_impact": 25000  # 25,000 crores
            },
            {
                "title": "Digital India Privacy Amendment",
                "bill_type": BillType.ORDINARY_BILL,
                "introduced_by": "IT_Minister", 
                "party": PartyType.BJP,
                "description": "Enhanced privacy protections for digital platforms"
            },
            {
                "title": "Anti-Defection Law Amendment",
                "bill_type": BillType.CONSTITUTIONAL_AMENDMENT,
                "introduced_by": "Law_Minister",
                "party": PartyType.CONGRESS,
                "description": "Stricter anti-defection provisions"
            },
            {
                "title": "Mumbai Housing for All Act",
                "bill_type": BillType.ORDINARY_BILL,
                "introduced_by": "Housing_Minister",
                "party": PartyType.AAP,
                "description": "Affordable housing scheme for Mumbai"
            }
        ]
        
        session_results = []
        
        for bill_data in sample_bills:
            print(f"\n{'='*60}")
            
            # Introduce bill
            bill = self.introduce_bill(**bill_data)
            
            # Conduct voting
            voting_result = self.conduct_parliamentary_voting(bill)
            session_results.append(voting_result)
            
            # Brief pause between bills
            time.sleep(0.5)
        
        return session_results
    
    def get_parliament_performance_report(self) -> Dict:
        """
        Generate comprehensive parliament performance report
        """
        # Overall statistics
        total_bills = self.bills_introduced
        pass_rate = self.bills_passed / max(1, total_bills)
        
        # Party performance
        party_stats = {}
        for party_type, party in self.parties.items():
            party_stats[party_type.value] = party.get_party_stats()
        
        # Top performing MPs (by attendance and participation)
        mp_performances = []
        for mp in self.lok_sabha_mps:
            stats = mp.get_performance_stats()
            if not stats.get("no_voting_data"):
                mp_performances.append(stats)
        
        # Sort by participation
        mp_performances.sort(key=lambda x: x.get("bills_voted", 0), reverse=True)
        
        return {
            "session": self.current_session,
            "overall_stats": {
                "total_bills_introduced": total_bills,
                "bills_passed": self.bills_passed,
                "bills_rejected": self.bills_rejected,
                "pass_rate": pass_rate,
                "total_mps": len(self.lok_sabha_mps),
                "total_parties": len(self.parties)
            },
            "party_performance": party_stats,
            "top_performers": mp_performances[:10],  # Top 10 MPs
            "voting_history_count": len(self.voting_history),
            "average_attendance": sum(mp.attendance_rate for mp in self.lok_sabha_mps) / len(self.lok_sabha_mps)
        }

if __name__ == "__main__":
    print("🚀 INDIAN PARLIAMENT CONSENSUS SIMULATION")
    print("Real Democratic Process - Mumbai Style!")
    print("=" * 70)
    
    try:
        # Initialize parliament
        parliament = IndianParliament()
        
        # Simulate parliament session
        session_results = parliament.simulate_parliament_session()
        
        # Generate performance report
        performance_report = parliament.get_parliament_performance_report()
        
        print("\n📋 SESSION SUMMARY")
        print("=" * 40)
        print(f"Bills introduced: {performance_report['overall_stats']['total_bills_introduced']}")
        print(f"Bills passed: {performance_report['overall_stats']['bills_passed']}")
        print(f"Bills rejected: {performance_report['overall_stats']['bills_rejected']}")
        print(f"Pass rate: {performance_report['overall_stats']['pass_rate']*100:.1f}%")
        print(f"Average MP attendance: {performance_report['average_attendance']*100:.1f}%")
        
        print("\n🏆 TOP PERFORMING PARTIES")
        print("-" * 30)
        for party, stats in performance_report['party_performance'].items():
            print(f"{party}: {stats['strength']} MPs, {stats['party_discipline']*100:.1f}% discipline")
        
        print("\n🎯 Key Insights:")
        print("• Indian Parliament uses sophisticated consensus mechanisms")
        print("• Anti-defection law ensures party discipline")
        print("• Quorum requirements prevent minority decisions")
        print("• Coalition dynamics add complexity to consensus")
        print("• Like Mumbai local trains - coordination needed for smooth operation!")
        
        print("\n🎊 PARLIAMENT SIMULATION COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error in parliament simulation: {e}")
        raise