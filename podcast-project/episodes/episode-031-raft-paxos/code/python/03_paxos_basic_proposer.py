#!/usr/bin/env python3
"""
Paxos Consensus Algorithm - Basic Proposer Implementation
Real-world example: Google's Chubby lock service और Apache Zookeeper

यह implementation Paxos के proposer role को demonstrate करती है
जैसे कि distributed systems में leader election के लिए इस्तेमाल होता है
"""

import time
import random
import threading
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class ProposalStatus(Enum):
    PENDING = "pending"
    PROMISED = "promised"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

@dataclass
class Proposal:
    """Paxos proposal with proposal number and value"""
    proposal_id: str
    proposal_number: int
    value: Any
    timestamp: float
    proposer_id: str

@dataclass
class PrepareRequest:
    """Phase 1: Prepare request"""
    proposal_number: int
    proposer_id: str

@dataclass
class PrepareResponse:
    """Phase 1: Prepare response"""
    acceptor_id: str
    promised: bool
    highest_proposal_accepted: Optional[int] = None
    highest_value_accepted: Optional[Any] = None
    reason: str = ""

@dataclass
class AcceptRequest:
    """Phase 2: Accept request"""
    proposal_number: int
    value: Any
    proposer_id: str

@dataclass
class AcceptResponse:
    """Phase 2: Accept response"""
    acceptor_id: str
    accepted: bool
    proposal_number: int
    reason: str = ""

class PaxosAcceptor:
    """
    Paxos Acceptor node
    यह Google Chubby के acceptor की तरह काम करता है
    """
    
    def __init__(self, acceptor_id: str):
        self.acceptor_id = acceptor_id
        
        # Persistent state (disk पर store होता है)
        self.highest_promised_proposal = -1  # Highest proposal number promised
        self.highest_accepted_proposal = -1  # Highest proposal number accepted
        self.accepted_value: Any = None      # Value accepted
        
        self.lock = threading.Lock()
        
        print(f"🏛️ Paxos Acceptor {acceptor_id} initialized")
    
    def handle_prepare(self, request: PrepareRequest) -> PrepareResponse:
        """
        Handle Phase 1: Prepare request
        यह phase में acceptor promise करता है कि वो इससे कम proposal number को reject करेगा
        """
        with self.lock:
            print(f"📋 Acceptor {self.acceptor_id}: Received prepare request {request.proposal_number} from {request.proposer_id}")
            
            # If proposal number is higher than any promised, promise it
            if request.proposal_number > self.highest_promised_proposal:
                self.highest_promised_proposal = request.proposal_number
                
                response = PrepareResponse(
                    acceptor_id=self.acceptor_id,
                    promised=True,
                    highest_proposal_accepted=self.highest_accepted_proposal if self.highest_accepted_proposal >= 0 else None,
                    highest_value_accepted=self.accepted_value,
                    reason=f"Promised proposal {request.proposal_number}"
                )
                
                print(f"✅ Acceptor {self.acceptor_id}: Promised proposal {request.proposal_number}")
                return response
            
            else:
                response = PrepareResponse(
                    acceptor_id=self.acceptor_id,
                    promised=False,
                    reason=f"Already promised higher proposal {self.highest_promised_proposal}"
                )
                
                print(f"❌ Acceptor {self.acceptor_id}: Rejected prepare {request.proposal_number} (promised: {self.highest_promised_proposal})")
                return response
    
    def handle_accept(self, request: AcceptRequest) -> AcceptResponse:
        """
        Handle Phase 2: Accept request
        यह phase में acceptor actually value को accept करता है
        """
        with self.lock:
            print(f"📝 Acceptor {self.acceptor_id}: Received accept request {request.proposal_number} from {request.proposer_id}")
            
            # Accept if proposal number >= highest promised
            if request.proposal_number >= self.highest_promised_proposal:
                self.highest_accepted_proposal = request.proposal_number
                self.accepted_value = request.value
                
                response = AcceptResponse(
                    acceptor_id=self.acceptor_id,
                    accepted=True,
                    proposal_number=request.proposal_number,
                    reason=f"Accepted proposal {request.proposal_number}"
                )
                
                print(f"✅ Acceptor {self.acceptor_id}: Accepted proposal {request.proposal_number} with value {request.value}")
                return response
            
            else:
                response = AcceptResponse(
                    acceptor_id=self.acceptor_id,
                    accepted=False,
                    proposal_number=request.proposal_number,
                    reason=f"Promised higher proposal {self.highest_promised_proposal}"
                )
                
                print(f"❌ Acceptor {self.acceptor_id}: Rejected accept {request.proposal_number}")
                return response
    
    def get_state(self) -> Dict:
        """Get current acceptor state"""
        with self.lock:
            return {
                'acceptor_id': self.acceptor_id,
                'highest_promised': self.highest_promised_proposal,
                'highest_accepted': self.highest_accepted_proposal,
                'accepted_value': self.accepted_value
            }

class PaxosProposer:
    """
    Paxos Proposer node
    यह distributed coordination के लिए values propose करता है
    """
    
    def __init__(self, proposer_id: str, acceptors: List[PaxosAcceptor]):
        self.proposer_id = proposer_id
        self.acceptors = acceptors
        self.proposal_counter = 0
        self.lock = threading.Lock()
        
        # For generating unique proposal numbers
        # Format: (counter << 8) | proposer_hash
        self.proposer_hash = hash(proposer_id) % 256
        
        print(f"🚀 Paxos Proposer {proposer_id} initialized with {len(acceptors)} acceptors")
    
    def generate_proposal_number(self) -> int:
        """Generate unique, monotonically increasing proposal number"""
        with self.lock:
            self.proposal_counter += 1
            # Combine counter and proposer ID to ensure uniqueness across proposers
            return (self.proposal_counter << 8) | self.proposer_hash
    
    def propose_value(self, value: Any, timeout: float = 5.0) -> Tuple[bool, Any]:
        """
        Main Paxos algorithm to propose a value
        यह function complete two-phase protocol implement करता है
        """
        proposal_number = self.generate_proposal_number()
        
        print(f"\n🎯 Proposer {self.proposer_id}: Starting proposal {proposal_number} for value '{value}'")
        print("=" * 60)
        
        start_time = time.time()
        
        # Phase 1: Prepare
        print(f"📋 Phase 1: PREPARE (Proposal {proposal_number})")
        prepare_success, chosen_value = self.phase_1_prepare(proposal_number, value)
        
        if not prepare_success:
            print(f"❌ Proposer {self.proposer_id}: Phase 1 failed for proposal {proposal_number}")
            return False, None
        
        # If majority already chose a different value, use that
        if chosen_value != value:
            print(f"🔄 Proposer {self.proposer_id}: Using previously chosen value '{chosen_value}' instead of '{value}'")
            value = chosen_value
        
        # Phase 2: Accept
        print(f"\n📝 Phase 2: ACCEPT (Proposal {proposal_number})")
        accept_success = self.phase_2_accept(proposal_number, value)
        
        elapsed = time.time() - start_time
        
        if accept_success:
            print(f"🎉 Proposer {self.proposer_id}: Successfully proposed '{value}' in {elapsed:.3f}s")
            return True, value
        else:
            print(f"❌ Proposer {self.proposer_id}: Failed to get value accepted in {elapsed:.3f}s")
            return False, None
    
    def phase_1_prepare(self, proposal_number: int, proposed_value: Any) -> Tuple[bool, Any]:
        """
        Phase 1: Send prepare requests to acceptors
        इस phase में हम majority से promise लेते हैं
        """
        prepare_request = PrepareRequest(
            proposal_number=proposal_number,
            proposer_id=self.proposer_id
        )
        
        # Send prepare to all acceptors
        responses = []
        for acceptor in self.acceptors:
            try:
                response = acceptor.handle_prepare(prepare_request)
                responses.append(response)
            except Exception as e:
                print(f"⚠️ Failed to get prepare response from {acceptor.acceptor_id}: {e}")
        
        # Count promises
        promises = [r for r in responses if r.promised]
        majority = len(self.acceptors) // 2 + 1
        
        print(f"   📊 Received {len(promises)}/{len(self.acceptors)} promises (need {majority})")
        
        if len(promises) < majority:
            print(f"   ❌ Failed to get majority promises")
            return False, None
        
        # Find highest accepted proposal among promises
        highest_accepted = -1
        chosen_value = proposed_value
        
        for response in promises:
            if (response.highest_proposal_accepted is not None and 
                response.highest_proposal_accepted > highest_accepted):
                highest_accepted = response.highest_proposal_accepted
                chosen_value = response.highest_value_accepted
                print(f"   🔍 Found higher accepted proposal {highest_accepted} with value '{chosen_value}'")
        
        print(f"   ✅ Phase 1 successful - will propose value '{chosen_value}'")
        return True, chosen_value
    
    def phase_2_accept(self, proposal_number: int, value: Any) -> bool:
        """
        Phase 2: Send accept requests to acceptors
        इस phase में actual value को accept कराते हैं
        """
        accept_request = AcceptRequest(
            proposal_number=proposal_number,
            value=value,
            proposer_id=self.proposer_id
        )
        
        # Send accept to all acceptors
        responses = []
        for acceptor in self.acceptors:
            try:
                response = acceptor.handle_accept(accept_request)
                responses.append(response)
            except Exception as e:
                print(f"⚠️ Failed to get accept response from {acceptor.acceptor_id}: {e}")
        
        # Count accepts
        accepts = [r for r in responses if r.accepted]
        majority = len(self.acceptors) // 2 + 1
        
        print(f"   📊 Received {len(accepts)}/{len(self.acceptors)} accepts (need {majority})")
        
        if len(accepts) >= majority:
            print(f"   ✅ Phase 2 successful - value '{value}' chosen!")
            return True
        else:
            print(f"   ❌ Failed to get majority accepts")
            return False

def simulate_zookeeper_leader_election():
    """
    Simulate ZooKeeper-style leader election using Paxos
    यह simulation Apache ZooKeeper के leader election को show करती है
    """
    print("🇮🇳 Paxos Consensus - ZooKeeper Leader Election Simulation")
    print("=" * 70)
    
    # Create acceptors (ZooKeeper ensemble members)
    acceptor_nodes = ['zk-mumbai', 'zk-delhi', 'zk-bangalore', 'zk-chennai', 'zk-hyderabad']
    acceptors = [PaxosAcceptor(node_id) for node_id in acceptor_nodes]
    
    print(f"🏛️ Created {len(acceptors)} acceptors: {acceptor_nodes}")
    
    # Multiple proposers competing for leadership
    proposer_candidates = ['app-server-1', 'app-server-2', 'app-server-3']
    proposers = [PaxosProposer(prop_id, acceptors) for prop_id in proposer_candidates]
    
    print(f"🚀 Created {len(proposers)} proposers: {proposer_candidates}")
    
    # Simulate concurrent leader election attempts
    print(f"\n🗳️ Starting concurrent leader election...")
    
    results = []
    threads = []
    
    def elect_leader(proposer: PaxosProposer, candidate_id: str):
        """Thread function for proposer to attempt leadership"""
        # Add small random delay to simulate real-world timing
        time.sleep(random.uniform(0.01, 0.05))
        
        leader_info = {
            'leader_id': candidate_id,
            'timestamp': time.time(),
            'proposer': proposer.proposer_id
        }
        
        success, chosen_value = proposer.propose_value(leader_info)
        results.append((success, chosen_value, proposer.proposer_id))
    
    # Start all proposers concurrently
    for i, proposer in enumerate(proposers):
        thread = threading.Thread(
            target=elect_leader,
            args=(proposer, proposer_candidates[i])
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all attempts to complete
    for thread in threads:
        thread.join()
    
    # Analyze results
    print(f"\n📊 Election Results:")
    print("-" * 40)
    
    successful_proposals = [r for r in results if r[0]]
    failed_proposals = [r for r in results if not r[0]]
    
    print(f"✅ Successful proposals: {len(successful_proposals)}")
    print(f"❌ Failed proposals: {len(failed_proposals)}")
    
    if successful_proposals:
        # Show the chosen leader
        chosen_leader = successful_proposals[0][1]  # First successful proposal
        print(f"\n👑 Elected Leader: {chosen_leader['leader_id']}")
        print(f"   Proposer: {chosen_leader['proposer']}")
        print(f"   Timestamp: {time.ctime(chosen_leader['timestamp'])}")
        
        # Verify all successful proposals chose the same value (Paxos consistency)
        all_same = all(r[1] == chosen_leader for r in successful_proposals)
        if all_same:
            print(f"✅ Consistency verified: All successful proposals chose the same leader")
        else:
            print(f"❌ Consistency violation: Different values were chosen!")
    
    # Show acceptor states
    print(f"\n🏛️ Final Acceptor States:")
    for acceptor in acceptors:
        state = acceptor.get_state()
        print(f"   {acceptor.acceptor_id}:")
        print(f"     Promised: {state['highest_promised']}")
        print(f"     Accepted: {state['highest_accepted']}")
        if state['accepted_value']:
            leader_id = state['accepted_value'].get('leader_id', 'Unknown')
            print(f"     Leader: {leader_id}")

def simulate_distributed_config_update():
    """
    Simulate distributed configuration update using Paxos
    यह example Chubby lock service के configuration consensus को show करता है
    """
    print("\n" + "="*70)
    print("🇮🇳 Paxos - Distributed Configuration Update")
    print("=" * 70)
    
    # Create acceptors for config service
    config_nodes = ['config-mumbai', 'config-delhi', 'config-bangalore']
    acceptors = [PaxosAcceptor(node_id) for node_id in config_nodes]
    
    # Configuration proposers
    admin_proposer = PaxosProposer('admin-console', acceptors)
    api_proposer = PaxosProposer('api-service', acceptors)
    
    # Simulate configuration changes
    configs_to_propose = [
        {
            'service': 'payment-gateway',
            'max_retry_attempts': 3,
            'timeout_ms': 5000,
            'updated_by': 'admin-console',
            'version': 1
        },
        {
            'service': 'payment-gateway', 
            'max_retry_attempts': 5,
            'timeout_ms': 8000,
            'updated_by': 'api-service',
            'version': 2
        }
    ]
    
    print(f"\n🔧 Proposing configuration updates...")
    
    # Propose configurations sequentially
    for i, config in enumerate(configs_to_propose):
        print(f"\n📝 Configuration Update #{i+1}:")
        print(f"   Service: {config['service']}")
        print(f"   Retry attempts: {config['max_retry_attempts']}")
        print(f"   Timeout: {config['timeout_ms']}ms")
        print(f"   Updated by: {config['updated_by']}")
        
        proposer = admin_proposer if i == 0 else api_proposer
        success, chosen_config = proposer.propose_value(config)
        
        if success:
            print(f"   ✅ Configuration update successful!")
        else:
            print(f"   ❌ Configuration update failed!")
        
        time.sleep(1)  # Small delay between updates
    
    # Show final configuration state
    print(f"\n⚙️ Final Configuration State:")
    final_state = acceptors[0].get_state()
    if final_state['accepted_value']:
        config = final_state['accepted_value']
        print(f"   Service: {config['service']}")
        print(f"   Max retries: {config['max_retry_attempts']}")
        print(f"   Timeout: {config['timeout_ms']}ms")
        print(f"   Version: {config['version']}")
        print(f"   Last updated by: {config['updated_by']}")

if __name__ == "__main__":
    # Run ZooKeeper leader election simulation
    simulate_zookeeper_leader_election()
    
    # Run configuration update simulation
    simulate_distributed_config_update()
    
    print("\n" + "="*70)
    print("Key Paxos Learnings:")
    print("1. Two-phase protocol: Prepare and Accept")
    print("2. Majority consensus required for both phases")
    print("3. Higher proposal numbers take precedence")
    print("4. Previously accepted values must be re-proposed")
    print("5. Guarantees consistency even with concurrent proposers")
    print("6. Used in systems like Google Chubby and Apache ZooKeeper")