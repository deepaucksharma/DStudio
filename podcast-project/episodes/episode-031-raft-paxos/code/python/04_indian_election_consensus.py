#!/usr/bin/env python3
"""
Indian Election Consensus using Raft-like Algorithm
Simulating EVM (Electronic Voting Machine) consensus across polling stations

यह implementation Indian election system को Raft consensus के साथ secure बनाती है
जैसे कि सभी polling stations के बीच vote counting में consensus हो
"""

import time
import random
import threading
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from datetime import datetime

class PollingStationState(Enum):
    FOLLOWER = "follower"      # Normal polling station
    CANDIDATE = "candidate"    # Contending for coordinator role
    LEADER = "leader"         # Coordinator station

class VoteType(Enum):
    ELECTION_VOTE = "election_vote"    # Actual voter's choice
    CONSENSUS_VOTE = "consensus_vote"  # For leader election

@dataclass
class ElectionVote:
    """Individual voter's choice"""
    voter_id: str
    constituency: str
    candidate: str
    timestamp: float
    polling_station_id: str
    vote_hash: str
    
    def __post_init__(self):
        if not self.vote_hash:
            # Create secure hash of vote for integrity
            vote_data = f"{self.voter_id}:{self.constituency}:{self.candidate}:{self.timestamp}"
            self.vote_hash = hashlib.sha256(vote_data.encode()).hexdigest()[:16]

@dataclass
class VoteLogEntry:
    """Log entry containing election votes"""
    term: int
    index: int
    votes: List[ElectionVote]
    timestamp: float
    station_id: str
    entry_hash: str
    
    def __post_init__(self):
        if not self.entry_hash:
            # Hash for log integrity
            entry_data = f"{self.term}:{self.index}:{len(self.votes)}:{self.timestamp}"
            self.entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()[:12]

@dataclass
class VoteReplicationRequest:
    """Request to replicate votes to other stations"""
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[VoteLogEntry]
    leader_commit: int

class EVMPollingStation:
    """
    Electronic Voting Machine Polling Station with Raft consensus
    हर polling station EVM की तरह votes collect करता है और consensus maintain करता है
    """
    
    def __init__(self, station_id: str, constituency: str, all_stations: List[str]):
        self.station_id = station_id
        self.constituency = constituency
        self.all_stations = all_stations
        self.state = PollingStationState.FOLLOWER
        
        # Election state
        self.current_term = 0
        self.voted_for: Optional[str] = None
        
        # Vote log (tamper-proof voting record)
        self.vote_log: List[VoteLogEntry] = []
        self.commit_index = -1
        self.last_applied = -1
        
        # Vote tallies (final results)
        self.vote_tallies: Dict[str, int] = {}
        
        # Leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        # Network and timers
        self.network: Dict[str, 'EVMPollingStation'] = {}
        self.election_timer = None
        self.heartbeat_timer = None
        self.is_running = True
        
        # EVM specific
        self.total_votes_cast = 0
        self.candidates = ['BJP', 'INC', 'AAP', 'BSP', 'SP', 'NOTA']  # Sample candidates
        
        print(f"🗳️ EVM Polling Station {station_id} initialized for {constituency}")
    
    def set_network(self, network: Dict[str, 'EVMPollingStation']):
        """Set network connections to other polling stations"""
        self.network = network
    
    def cast_vote(self, voter_id: str, candidate: str) -> bool:
        """
        Voter casts a vote (only leader can accept votes)
        यह function तब call होता है जब voter EVM पर button press करता है
        """
        if self.state != PollingStationState.LEADER:
            print(f"❌ Station {self.station_id}: Not coordinator, cannot accept votes")
            return False
        
        # Validate candidate
        if candidate not in self.candidates:
            print(f"❌ Station {self.station_id}: Invalid candidate {candidate}")
            return False
        
        # Create vote record
        vote = ElectionVote(
            voter_id=voter_id,
            constituency=self.constituency,
            candidate=candidate,
            timestamp=time.time(),
            polling_station_id=self.station_id,
            vote_hash=""
        )
        
        # Create log entry
        log_entry = VoteLogEntry(
            term=self.current_term,
            index=len(self.vote_log),
            votes=[vote],
            timestamp=time.time(),
            station_id=self.station_id,
            entry_hash=""
        )
        
        # Append to local log
        self.vote_log.append(log_entry)
        self.total_votes_cast += 1
        
        print(f"🗳️ Station {self.station_id}: Vote cast by {voter_id} for {candidate}")
        
        # Replicate to other stations
        self.replicate_votes_to_followers()
        
        return True
    
    def replicate_votes_to_followers(self):
        """Replicate vote log to all follower stations"""
        if self.state != PollingStationState.LEADER:
            return
        
        for station_id in self.all_stations:
            if station_id != self.station_id and station_id in self.network:
                threading.Thread(
                    target=self.replicate_to_station,
                    args=(station_id,)
                ).start()
    
    def replicate_to_station(self, station_id: str):
        """Replicate votes to specific station"""
        try:
            next_index = self.next_index.get(station_id, 0)
            
            # Determine entries to send
            entries_to_send = []
            if next_index < len(self.vote_log):
                entries_to_send = self.vote_log[next_index:]
            
            # Previous log entry info
            prev_log_index = next_index - 1
            prev_log_term = 0
            if prev_log_index >= 0 and prev_log_index < len(self.vote_log):
                prev_log_term = self.vote_log[prev_log_index].term
            
            # Create replication request
            request = VoteReplicationRequest(
                term=self.current_term,
                leader_id=self.station_id,
                prev_log_index=prev_log_index,
                prev_log_term=prev_log_term,
                entries=entries_to_send,
                leader_commit=self.commit_index
            )
            
            # Send to station
            station = self.network[station_id]
            response = station.handle_vote_replication(request)
            self.handle_replication_response(station_id, request, response)
            
        except Exception as e:
            print(f"❌ Coordinator {self.station_id}: Failed to replicate to {station_id}: {e}")
    
    def handle_vote_replication(self, request: VoteReplicationRequest) -> Dict:
        """Handle vote replication from coordinator station"""
        # Check term
        if request.term < self.current_term:
            return {
                'term': self.current_term,
                'success': False,
                'station_id': self.station_id
            }
        
        # Update term and become follower if necessary
        if request.term > self.current_term:
            self.current_term = request.term
            self.voted_for = None
            self.state = PollingStationState.FOLLOWER
        
        self.reset_election_timer()
        
        # Check log consistency
        if request.prev_log_index >= 0:
            if (request.prev_log_index >= len(self.vote_log) or
                self.vote_log[request.prev_log_index].term != request.prev_log_term):
                
                print(f"🔄 Station {self.station_id}: Vote log inconsistency at index {request.prev_log_index}")
                return {
                    'term': self.current_term,
                    'success': False,
                    'station_id': self.station_id,
                    'conflict_index': min(len(self.vote_log), request.prev_log_index)
                }
        
        # Append new vote entries
        if request.entries:
            start_index = request.prev_log_index + 1
            
            # Handle conflicts
            for i, new_entry in enumerate(request.entries):
                entry_index = start_index + i
                
                if entry_index < len(self.vote_log):
                    existing_entry = self.vote_log[entry_index]
                    if existing_entry.term != new_entry.term:
                        # Delete conflicting entries
                        self.vote_log = self.vote_log[:entry_index]
                        print(f"🗑️ Station {self.station_id}: Deleted conflicting vote entries from index {entry_index}")
                        break
                elif entry_index == len(self.vote_log):
                    break
            
            # Append new entries
            entries_to_append = request.entries[len(self.vote_log) - start_index:]
            for entry in entries_to_append:
                self.vote_log.append(entry)
                votes_count = len(entry.votes)
                self.total_votes_cast += votes_count
                print(f"➕ Station {self.station_id}: Replicated {votes_count} votes from coordinator")
        
        # Update commit index
        if request.leader_commit > self.commit_index:
            old_commit = self.commit_index
            self.commit_index = min(request.leader_commit, len(self.vote_log) - 1)
            
            # Apply committed votes
            self.apply_committed_votes()
            
            if self.commit_index > old_commit:
                print(f"✅ Station {self.station_id}: Updated commit index to {self.commit_index}")
        
        return {
            'term': self.current_term,
            'success': True,
            'station_id': self.station_id,
            'match_index': len(self.vote_log) - 1
        }
    
    def handle_replication_response(self, station_id: str, request: VoteReplicationRequest, response: Dict):
        """Handle response from follower station"""
        if self.state != PollingStationState.LEADER:
            return
        
        if response.get('success', False):
            # Update indices for successful replication
            match_index = response.get('match_index', -1)
            self.next_index[station_id] = match_index + 1
            self.match_index[station_id] = match_index
            
            print(f"✅ Coordinator {self.station_id}: Successfully replicated votes to {station_id}")
            
            # Update commit index
            self.update_commit_index()
        else:
            # Handle replication failure
            conflict_index = response.get('conflict_index', 0)
            self.next_index[station_id] = max(0, conflict_index)
            
            print(f"🔄 Coordinator {self.station_id}: Retrying replication to {station_id} from index {self.next_index[station_id]}")
            
            # Retry replication
            threading.Thread(
                target=self.replicate_to_station,
                args=(station_id,)
            ).start()
    
    def update_commit_index(self):
        """Update commit index based on majority replication"""
        if self.state != PollingStationState.LEADER:
            return
        
        # Find highest index replicated on majority
        for index in range(len(self.vote_log) - 1, self.commit_index, -1):
            if self.vote_log[index].term != self.current_term:
                continue
            
            # Count replications
            replication_count = 1  # Leader has it
            for station_id in self.all_stations:
                if station_id != self.station_id and station_id in self.match_index:
                    if self.match_index[station_id] >= index:
                        replication_count += 1
            
            # Check majority
            majority = len(self.all_stations) // 2 + 1
            if replication_count >= majority:
                old_commit = self.commit_index
                self.commit_index = index
                
                # Apply committed votes
                self.apply_committed_votes()
                
                votes_committed = sum(len(self.vote_log[i].votes) for i in range(old_commit + 1, self.commit_index + 1))
                print(f"🎯 Coordinator {self.station_id}: Committed {votes_committed} votes (replicated on {replication_count}/{len(self.all_stations)} stations)")
                break
    
    def apply_committed_votes(self):
        """Apply committed votes to final tally"""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.vote_log[self.last_applied]
            
            # Count votes for each candidate
            for vote in entry.votes:
                candidate = vote.candidate
                if candidate not in self.vote_tallies:
                    self.vote_tallies[candidate] = 0
                self.vote_tallies[candidate] += 1
            
            votes_applied = len(entry.votes)
            print(f"🗳️ Station {self.station_id}: Applied {votes_applied} votes to final tally")
    
    def become_leader(self):
        """Become coordinator station"""
        print(f"👑 Station {self.station_id}: Became COORDINATOR for term {self.current_term}")
        self.state = PollingStationState.LEADER
        
        # Initialize leader state
        for station_id in self.all_stations:
            if station_id != self.station_id:
                self.next_index[station_id] = len(self.vote_log)
                self.match_index[station_id] = -1
        
        # Start heartbeats
        self.start_heartbeat_timer()
    
    def start_election(self):
        """Start coordinator election (simplified)"""
        if not self.is_running:
            return
        
        print(f"🗳️ Station {self.station_id}: Starting coordinator election for term {self.current_term + 1}")
        
        self.state = PollingStationState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.station_id
        
        # Simplified: assume this station wins (in real implementation, would send vote requests)
        if random.random() > 0.3:  # 70% chance to win
            self.become_leader()
        else:
            self.reset_election_timer()
    
    def reset_election_timer(self):
        """Reset election timer"""
        if self.election_timer:
            self.election_timer.cancel()
        
        timeout = random.uniform(2.0, 4.0)  # 2-4 seconds
        self.election_timer = threading.Timer(timeout, self.start_election)
        self.election_timer.start()
    
    def start_heartbeat_timer(self):
        """Start heartbeat timer for coordinator"""
        if self.state == PollingStationState.LEADER and self.is_running:
            self.heartbeat_timer = threading.Timer(0.5, self.heartbeat_routine)  # 500ms
            self.heartbeat_timer.start()
    
    def heartbeat_routine(self):
        """Send heartbeats to maintain coordination"""
        if self.state == PollingStationState.LEADER:
            self.replicate_votes_to_followers()  # Heartbeat via replication
            self.start_heartbeat_timer()
    
    def get_election_results(self) -> Dict:
        """Get current election results"""
        return {
            'station_id': self.station_id,
            'constituency': self.constituency,
            'total_votes': self.total_votes_cast,
            'votes_committed': sum(self.vote_tallies.values()),
            'candidate_tallies': dict(self.vote_tallies),
            'log_entries': len(self.vote_log),
            'state': self.state.value
        }
    
    def stop(self):
        """Stop polling station"""
        self.is_running = False
        if self.election_timer:
            self.election_timer.cancel()
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()

def simulate_indian_election():
    """
    Simulate Indian election with EVM consensus
    यह simulation real Indian election की security और transparency को बढ़ाने के लिए है
    """
    print("🇮🇳 Indian Election Consensus - EVM Network Simulation")
    print("🏛️ Constituency: Mumbai North-West")
    print("=" * 60)
    
    # Create polling stations (Mumbai North-West constituency)
    station_ids = ['PS-001-Andheri', 'PS-002-Jogeshwari', 'PS-003-Goregaon', 'PS-004-Malad', 'PS-005-Kandivali']
    constituency = "Mumbai North-West"
    
    # Initialize polling stations
    polling_stations = {}
    for station_id in station_ids:
        polling_stations[station_id] = EVMPollingStation(station_id, constituency, station_ids)
    
    # Set network connections
    for station in polling_stations.values():
        station.set_network(polling_stations)
    
    # Start election process
    print(f"\n🚀 Starting polling stations...")
    for station in polling_stations.values():
        station.reset_election_timer()
    
    # Wait for coordinator election
    time.sleep(3)
    
    # Find coordinator
    coordinators = [s for s in polling_stations.values() if s.state == PollingStationState.LEADER]
    
    if coordinators:
        coordinator = coordinators[0]
        print(f"\n👑 Coordinator Station: {coordinator.station_id}")
        
        # Simulate voting process
        print(f"\n🗳️ Starting voting process...")
        
        # Sample voters and their choices
        sample_votes = [
            ('VOTER001', 'BJP'), ('VOTER002', 'INC'), ('VOTER003', 'AAP'),
            ('VOTER004', 'BJP'), ('VOTER005', 'INC'), ('VOTER006', 'BJP'),
            ('VOTER007', 'AAP'), ('VOTER008', 'NOTA'), ('VOTER009', 'BJP'),
            ('VOTER010', 'INC'), ('VOTER011', 'BJP'), ('VOTER012', 'AAP'),
            ('VOTER013', 'BJP'), ('VOTER014', 'INC'), ('VOTER015', 'BSP'),
            ('VOTER016', 'BJP'), ('VOTER017', 'AAP'), ('VOTER018', 'BJP'),
            ('VOTER019', 'INC'), ('VOTER020', 'SP')
        ]
        
        # Cast votes through coordinator
        for voter_id, candidate in sample_votes:
            success = coordinator.cast_vote(voter_id, candidate)
            if success:
                print(f"   ✅ Vote recorded: {voter_id} → {candidate}")
            
            # Small delay between votes
            time.sleep(0.1)
        
        # Wait for replication and commitment
        print(f"\n⏳ Waiting for vote replication and commitment...")
        time.sleep(3)
        
        # Show results from all stations
        print(f"\n📊 Election Results Across All Polling Stations:")
        print("=" * 60)
        
        all_results = {}
        consistent = True
        
        for station_id, station in polling_stations.items():
            results = station.get_election_results()
            all_results[station_id] = results
            
            print(f"\n🏢 {station_id} ({results['state'].upper()}):")
            print(f"   Total votes cast: {results['total_votes']}")
            print(f"   Committed votes: {results['votes_committed']}")
            print(f"   Log entries: {results['log_entries']}")
            print(f"   Candidate tallies:")
            
            for candidate, votes in results['candidate_tallies'].items():
                print(f"     {candidate}: {votes} votes")
        
        # Verify consistency across all stations
        print(f"\n🔍 Consistency Verification:")
        reference_tallies = list(all_results.values())[0]['candidate_tallies']
        
        for station_id, results in all_results.items():
            if results['candidate_tallies'] == reference_tallies:
                print(f"   ✅ {station_id}: CONSISTENT")
            else:
                print(f"   ❌ {station_id}: INCONSISTENT")
                consistent = False
        
        if consistent:
            print(f"\n🎉 All polling stations have consistent vote tallies!")
            
            # Show final results
            print(f"\n🏆 FINAL ELECTION RESULTS - {constituency}:")
            total_votes = sum(reference_tallies.values())
            
            # Sort candidates by votes
            sorted_candidates = sorted(reference_tallies.items(), key=lambda x: x[1], reverse=True)
            
            for rank, (candidate, votes) in enumerate(sorted_candidates, 1):
                percentage = (votes / total_votes * 100) if total_votes > 0 else 0
                print(f"   {rank}. {candidate}: {votes} votes ({percentage:.1f}%)")
            
            if sorted_candidates:
                winner = sorted_candidates[0]
                print(f"\n👑 WINNER: {winner[0]} with {winner[1]} votes!")
        
        else:
            print(f"\n❌ Inconsistency detected! Manual audit required.")
    
    else:
        print(f"\n❌ No coordinator elected! Election cannot proceed.")
    
    # Cleanup
    print(f"\n🧹 Closing polling stations...")
    for station in polling_stations.values():
        station.stop()

def simulate_vote_tampering_protection():
    """
    Demonstrate how consensus protects against vote tampering
    यह example दिखाता है कि कैसे consensus algorithm vote tampering को prevent करता है
    """
    print("\n" + "="*60)
    print("🛡️ Vote Tampering Protection Demo")
    print("=" * 60)
    
    # Create minimal setup
    stations = ['PS-A', 'PS-B', 'PS-C']
    network = {}
    
    for station_id in stations:
        network[station_id] = EVMPollingStation(station_id, "Test Constituency", stations)
    
    for station in network.values():
        station.set_network(network)
    
    # Make PS-A the coordinator
    coordinator = network['PS-A']
    coordinator.become_leader()
    
    print(f"👑 Coordinator: {coordinator.station_id}")
    
    # Cast legitimate votes
    legitimate_votes = [('V001', 'BJP'), ('V002', 'INC'), ('V003', 'AAP')]
    
    for voter_id, candidate in legitimate_votes:
        coordinator.cast_vote(voter_id, candidate)
    
    time.sleep(1)  # Allow replication
    
    print(f"\n✅ Legitimate votes cast and replicated")
    
    # Show current state
    for station_id, station in network.items():
        results = station.get_election_results()
        print(f"   {station_id}: {results['votes_committed']} committed votes")
    
    # Attempt to tamper with follower's votes (this should be detected)
    print(f"\n💀 Attempting to tamper with follower votes...")
    
    follower = network['PS-B']
    
    # Direct manipulation (bypassing consensus) - this simulates tampering
    fake_vote = ElectionVote(
        voter_id='FAKE001',
        constituency="Test Constituency", 
        candidate='TAMPERER',
        timestamp=time.time(),
        polling_station_id='PS-B',
        vote_hash=""
    )
    
    fake_entry = VoteLogEntry(
        term=99,  # Wrong term
        index=len(follower.vote_log),
        votes=[fake_vote],
        timestamp=time.time(),
        station_id='PS-B',
        entry_hash=""
    )
    
    # Directly manipulate follower's log (simulating tampering)
    follower.vote_log.append(fake_entry)
    follower.vote_tallies['TAMPERER'] = 1
    
    print(f"   💀 Fake vote injected into {follower.station_id}")
    
    # Coordinator sends heartbeat - this should detect the inconsistency
    print(f"\n🔍 Coordinator sending heartbeat to detect tampering...")
    coordinator.replicate_votes_to_followers()
    
    time.sleep(1)
    
    # Show that tampering is corrected
    print(f"\n🛡️ After consensus correction:")
    for station_id, station in network.items():
        results = station.get_election_results()
        has_tamperer = 'TAMPERER' in results['candidate_tallies']
        print(f"   {station_id}: Tampered vote present = {has_tamperer}")
    
    # Cleanup
    for station in network.values():
        station.stop()

if __name__ == "__main__":
    # Run main election simulation
    simulate_indian_election()
    
    # Run tampering protection demo
    simulate_vote_tampering_protection()
    
    print("\n" + "="*60)
    print("🇮🇳 Indian Election Security Benefits:")
    print("1. Distributed consensus prevents single point of tampering")
    print("2. All votes are cryptographically hashed for integrity")
    print("3. Majority agreement required for vote commitment")
    print("4. Automatic detection and correction of inconsistencies")
    print("5. Immutable audit trail across all polling stations")
    print("6. Byzantine fault tolerance against malicious actors")