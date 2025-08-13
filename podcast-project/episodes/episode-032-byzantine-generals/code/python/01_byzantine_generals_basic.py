#!/usr/bin/env python3
"""
Byzantine Generals Problem - Basic Implementation
Real-world application: Blockchain consensus and distributed banking systems

यह implementation Byzantine Generals problem को solve करती है
जैसे कि Bitcoin और Ethereum में consensus के लिए इस्तेमाल होता है
"""

import time
import random
import threading
import hashlib
import json
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class GeneralType(Enum):
    LOYAL = "loyal"
    TRAITOR = "traitor"

class BattleDecision(Enum):
    ATTACK = "attack"
    RETREAT = "retreat"

@dataclass
class ByzantineMessage:
    """Message passed between generals"""
    sender_id: str
    receiver_id: str
    decision: BattleDecision
    round_number: int
    path: List[str]  # Path the message has traveled
    signature: str
    timestamp: float
    
    def __post_init__(self):
        if not self.signature:
            # Create message signature for authenticity
            msg_data = f"{self.sender_id}:{self.decision.value}:{self.round_number}:{self.timestamp}"
            self.signature = hashlib.sha256(msg_data.encode()).hexdigest()[:16]

@dataclass
class GeneralState:
    """State of a Byzantine general"""
    general_id: str
    general_type: GeneralType
    decision: Optional[BattleDecision]
    round_decisions: Dict[int, Dict[str, BattleDecision]]  # round -> general_id -> decision
    messages_received: List[ByzantineMessage]
    is_commander: bool = False

class ByzantineGeneral:
    """
    Byzantine General implementation
    हर general एक node की तरह है जो consensus achieve करने की कोशिश करता है
    """
    
    def __init__(self, general_id: str, general_type: GeneralType, all_generals: List[str]):
        self.general_id = general_id
        self.general_type = general_type
        self.all_generals = all_generals
        self.n = len(all_generals)
        
        # State management
        self.decision: Optional[BattleDecision] = None
        self.final_decision: Optional[BattleDecision] = None
        self.round_decisions: Dict[int, Dict[str, BattleDecision]] = {}
        self.messages_received: List[ByzantineMessage] = []
        
        # Network simulation
        self.network: Dict[str, 'ByzantineGeneral'] = {}
        self.message_queue: List[ByzantineMessage] = []
        self.is_running = True
        
        # Byzantine behavior parameters
        self.malicious_probability = 0.7 if general_type == GeneralType.TRAITOR else 0.0
        
        print(f"⚔️ Byzantine General {general_id} ({general_type.value}) initialized")
    
    def set_network(self, network: Dict[str, 'ByzantineGeneral']):
        """Set network connections to other generals"""
        self.network = network
    
    def send_message(self, receiver_id: str, decision: BattleDecision, 
                    round_number: int, path: List[str] = None):
        """
        Send message to another general
        Traitor generals might send different messages to different receivers
        """
        if path is None:
            path = [self.general_id]
        
        # Traitor behavior: might send conflicting messages
        if self.general_type == GeneralType.TRAITOR and random.random() < self.malicious_probability:
            # Send opposite decision to some receivers
            if random.random() < 0.5:
                decision = BattleDecision.RETREAT if decision == BattleDecision.ATTACK else BattleDecision.ATTACK
                print(f"🔥 Traitor {self.general_id}: Sending CONFLICTING message to {receiver_id}")
        
        message = ByzantineMessage(
            sender_id=self.general_id,
            receiver_id=receiver_id,
            decision=decision,
            round_number=round_number,
            path=path.copy(),
            signature="",
            timestamp=time.time()
        )
        
        # Send message through network
        if receiver_id in self.network:
            receiver = self.network[receiver_id]
            receiver.receive_message(message)
            
            print(f"📨 {self.general_id} → {receiver_id}: {decision.value} (round {round_number})")
    
    def receive_message(self, message: ByzantineMessage):
        """Receive and process message from another general"""
        self.messages_received.append(message)
        
        # Update round decisions
        round_num = message.round_number
        if round_num not in self.round_decisions:
            self.round_decisions[round_num] = {}
        
        self.round_decisions[round_num][message.sender_id] = message.decision
        
        print(f"📬 {self.general_id}: Received {message.decision.value} from {message.sender_id} (round {round_num})")
    
    def broadcast_decision(self, decision: BattleDecision, round_number: int, path: List[str] = None):
        """Broadcast decision to all other generals"""
        if path is None:
            path = [self.general_id]
        
        for general_id in self.all_generals:
            if general_id != self.general_id:
                self.send_message(general_id, decision, round_number, path)
    
    def oral_message_algorithm(self, commander_id: str, commander_decision: BattleDecision, 
                             max_rounds: int) -> BattleDecision:
        """
        Implement Oral Message Algorithm for Byzantine Agreement
        यह algorithm m rounds में consensus achieve करती है जहाँ m >= number of traitors
        """
        print(f"\n🎯 {self.general_id}: Starting Oral Message Algorithm (max rounds: {max_rounds})")
        
        # Round 0: Commander broadcasts initial decision
        if self.general_id == commander_id:
            print(f"👑 Commander {self.general_id}: Broadcasting initial decision: {commander_decision.value}")
            self.decision = commander_decision
            self.broadcast_decision(commander_decision, 0)
        
        # Execute multiple rounds
        for round_num in range(1, max_rounds + 1):
            self.execute_round(round_num, max_rounds)
            time.sleep(0.1)  # Small delay between rounds
        
        # Make final decision based on majority
        final_decision = self.make_final_decision(max_rounds)
        self.final_decision = final_decision
        
        print(f"🎖️ {self.general_id}: Final decision = {final_decision.value}")
        return final_decision
    
    def execute_round(self, round_number: int, max_rounds: int):
        """Execute a single round of the algorithm"""
        print(f"\n🔄 {self.general_id}: Executing round {round_number}")
        
        # In each round, relay messages received in previous round
        if round_number == 1:
            # Round 1: Relay commander's message
            if 0 in self.round_decisions:
                for sender_id, decision in self.round_decisions[0].items():
                    # Relay to all others (except sender and self)
                    for receiver_id in self.all_generals:
                        if receiver_id != sender_id and receiver_id != self.general_id:
                            path = [sender_id, self.general_id]
                            self.send_message(receiver_id, decision, round_number, path)
        
        else:
            # Later rounds: Relay messages from previous round
            prev_round = round_number - 1
            if prev_round in self.round_decisions:
                for sender_id, decision in self.round_decisions[prev_round].items():
                    # Only relay if path length is appropriate
                    for receiver_id in self.all_generals:
                        if receiver_id != sender_id and receiver_id != self.general_id:
                            # Find the message path
                            original_message = self.find_message_by_sender_round(sender_id, prev_round)
                            if original_message and len(original_message.path) < max_rounds:
                                new_path = original_message.path + [self.general_id]
                                self.send_message(receiver_id, decision, round_number, new_path)
        
        # Wait for messages in this round
        time.sleep(0.2)
    
    def find_message_by_sender_round(self, sender_id: str, round_number: int) -> Optional[ByzantineMessage]:
        """Find message by sender and round"""
        for message in self.messages_received:
            if message.sender_id == sender_id and message.round_number == round_number:
                return message
        return None
    
    def make_final_decision(self, max_rounds: int) -> BattleDecision:
        """Make final decision based on majority vote across all rounds"""
        attack_count = 0
        retreat_count = 0
        
        # Count decisions from all rounds and all generals
        all_decisions = {}
        
        for round_num in range(max_rounds + 1):
            if round_num in self.round_decisions:
                for general_id, decision in self.round_decisions[round_num].items():
                    # Use the first decision we received from each general
                    if general_id not in all_decisions:
                        all_decisions[general_id] = decision
        
        # Count votes
        for general_id, decision in all_decisions.items():
            if decision == BattleDecision.ATTACK:
                attack_count += 1
            else:
                retreat_count += 1
        
        # Majority decision
        if attack_count > retreat_count:
            print(f"📊 {self.general_id}: Majority vote = ATTACK ({attack_count} vs {retreat_count})")
            return BattleDecision.ATTACK
        elif retreat_count > attack_count:
            print(f"📊 {self.general_id}: Majority vote = RETREAT ({retreat_count} vs {attack_count})")
            return BattleDecision.RETREAT
        else:
            # Tie-breaker: default to retreat (safer option)
            print(f"📊 {self.general_id}: Tie vote, defaulting to RETREAT")
            return BattleDecision.RETREAT
    
    def get_state(self) -> Dict:
        """Get current general state"""
        return {
            'general_id': self.general_id,
            'type': self.general_type.value,
            'decision': self.decision.value if self.decision else None,
            'final_decision': self.final_decision.value if self.final_decision else None,
            'messages_received': len(self.messages_received),
            'rounds_participated': len(self.round_decisions)
        }

def simulate_byzantine_generals_basic():
    """
    Simulate basic Byzantine Generals problem
    यह simulation blockchain consensus की foundation है
    """
    print("🇮🇳 Byzantine Generals Problem - Basic Consensus Simulation")
    print("⚔️ Scenario: Indian Army coordinating border defense")
    print("=" * 60)
    
    # Create generals (army commanders at different positions)
    general_positions = ['North-Command', 'South-Command', 'East-Command', 'West-Command', 'Central-Command']
    
    # Set up generals: 2 traitors out of 5 (can tolerate up to 1 traitor with 4+ generals)
    generals = {}
    traitor_count = 1  # We can tolerate 1 traitor with 5 generals
    
    for i, position in enumerate(general_positions):
        general_type = GeneralType.TRAITOR if i < traitor_count else GeneralType.LOYAL
        generals[position] = ByzantineGeneral(position, general_type, general_positions)
    
    print(f"🏛️ Created {len(generals)} generals:")
    for general_id, general in generals.items():
        print(f"   {general_id}: {general.general_type.value}")
    
    # Set network connections
    for general in generals.values():
        general.set_network(generals)
    
    # Choose commander and initial decision
    commander_id = 'North-Command'
    commander_decision = BattleDecision.ATTACK
    
    print(f"\n👑 Commander: {commander_id}")
    print(f"📋 Commander's decision: {commander_decision.value}")
    
    # Calculate required rounds (must be > number of traitors)
    max_rounds = traitor_count + 1
    
    print(f"🔄 Algorithm will run for {max_rounds} rounds (traitors: {traitor_count})")
    
    # Execute Byzantine Agreement
    print(f"\n⚔️ Starting Byzantine Generals Algorithm...")
    
    final_decisions = {}
    
    # Run algorithm for each general
    for general_id, general in generals.items():
        decision = general.oral_message_algorithm(commander_id, commander_decision, max_rounds)
        final_decisions[general_id] = decision
    
    # Analyze results
    print(f"\n📊 Final Results:")
    print("=" * 40)
    
    attack_votes = sum(1 for d in final_decisions.values() if d == BattleDecision.ATTACK)
    retreat_votes = sum(1 for d in final_decisions.values() if d == BattleDecision.RETREAT)
    
    print(f"Attack votes: {attack_votes}")
    print(f"Retreat votes: {retreat_votes}")
    
    # Check consensus
    loyal_generals = [g for g in generals.values() if g.general_type == GeneralType.LOYAL]
    loyal_decisions = [g.final_decision for g in loyal_generals]
    
    if len(set(loyal_decisions)) == 1:
        consensus_decision = loyal_decisions[0]
        print(f"\n✅ CONSENSUS ACHIEVED!")
        print(f"🎯 All loyal generals agreed on: {consensus_decision.value}")
        
        # Show individual decisions
        print(f"\n🔍 Individual General Decisions:")
        for general_id, decision in final_decisions.items():
            general_type = generals[general_id].general_type.value
            status = "✅" if decision == consensus_decision else "❌"
            print(f"   {status} {general_id} ({general_type}): {decision.value}")
        
    else:
        print(f"\n❌ CONSENSUS FAILED!")
        print(f"Loyal generals could not agree on a single decision")
    
    # Show detailed statistics
    print(f"\n📈 Algorithm Statistics:")
    for general_id, general in generals.items():
        state = general.get_state()
        print(f"   {general_id}:")
        print(f"     Type: {state['type']}")
        print(f"     Messages received: {state['messages_received']}")
        print(f"     Rounds participated: {state['rounds_participated']}")
        print(f"     Final decision: {state['final_decision']}")

def simulate_blockchain_consensus():
    """
    Simulate blockchain-style consensus with Byzantine nodes
    यह example Bitcoin/Ethereum के consensus mechanism को demonstrate करता है
    """
    print("\n" + "="*60)
    print("🇮🇳 Blockchain Byzantine Consensus - Mining Pool Coordination")
    print("=" * 60)
    
    # Mining pools as generals
    mining_pools = ['Antpool-India', 'F2Pool-Mumbai', 'ViaBTC-Delhi', 'Poolin-Bangalore', 'Binance-Chennai']
    
    # Create mining pool generals
    pools = {}
    traitor_pools = 1  # 1 malicious pool
    
    for i, pool_id in enumerate(mining_pools):
        pool_type = GeneralType.TRAITOR if i < traitor_pools else GeneralType.LOYAL
        pools[pool_id] = ByzantineGeneral(pool_id, pool_type, mining_pools)
    
    # Set network
    for pool in pools.values():
        pool.set_network(pools)
    
    # Block proposal scenario
    print(f"\n⛏️ Mining Pool Consensus on Block Validation:")
    print(f"Scenario: Validating a high-value transaction block")
    
    commander_pool = 'Antpool-India'
    block_decision = BattleDecision.ATTACK  # ATTACK = Accept block, RETREAT = Reject block
    
    print(f"👑 Proposing pool: {commander_pool}")
    print(f"📦 Block proposal: {'Accept' if block_decision == BattleDecision.ATTACK else 'Reject'}")
    
    # Run consensus
    max_rounds = traitor_pools + 1
    
    print(f"\n🔄 Running consensus for {max_rounds} rounds...")
    
    final_decisions = {}
    for pool_id, pool in pools.items():
        decision = pool.oral_message_algorithm(commander_pool, block_decision, max_rounds)
        final_decisions[pool_id] = decision
    
    # Analyze blockchain consensus
    print(f"\n⛏️ Mining Pool Consensus Results:")
    accept_count = sum(1 for d in final_decisions.values() if d == BattleDecision.ATTACK)
    reject_count = sum(1 for d in final_decisions.values() if d == BattleDecision.RETREAT)
    
    print(f"Pools accepting block: {accept_count}")
    print(f"Pools rejecting block: {reject_count}")
    
    # Determine network decision
    if accept_count > len(mining_pools) // 2:
        print(f"🎉 BLOCK ACCEPTED by network majority!")
    else:
        print(f"⛔ BLOCK REJECTED by network majority!")
    
    # Show pool decisions
    print(f"\n🏊 Individual Pool Decisions:")
    for pool_id, decision in final_decisions.items():
        pool_type = pools[pool_id].general_type.value
        action = "Accept" if decision == BattleDecision.ATTACK else "Reject"
        print(f"   {pool_id} ({pool_type}): {action} block")

if __name__ == "__main__":
    # Run basic Byzantine Generals simulation
    simulate_byzantine_generals_basic()
    
    # Run blockchain consensus simulation
    simulate_blockchain_consensus()
    
    print("\n" + "="*60)
    print("🇮🇳 Key Byzantine Fault Tolerance Learnings:")
    print("1. Can tolerate up to (n-1)/3 Byzantine (malicious) nodes")
    print("2. Requires multiple rounds of communication")
    print("3. Oral Message Algorithm needs m+1 rounds for m traitors")
    print("4. Essential for blockchain and cryptocurrency consensus")
    print("5. Used in systems like Bitcoin, Ethereum, and Hyperledger")
    print("6. Provides safety even with malicious/compromised nodes")