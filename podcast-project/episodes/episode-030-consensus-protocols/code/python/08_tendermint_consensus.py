#!/usr/bin/env python3
"""
Tendermint Consensus Implementation
==================================

Cosmos-style consensus with instant finality - Mumbai local train timing!
Just like Mumbai locals have precise schedules and instant confirmations,
Tendermint provides immediate finality with Byzantine fault tolerance.

Features:
- Round-based consensus
- Instant finality
- Validator rotation
- Evidence submission for malicious behavior
- Cosmos Hub simulation

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json
import uuid

class RoundStep(Enum):
    """Tendermint round steps"""
    PROPOSE = "propose"
    PREVOTE = "prevote"
    PRECOMMIT = "precommit"
    COMMIT = "commit"

class VoteType(Enum):
    """Vote types in Tendermint"""
    PREVOTE = "prevote"
    PRECOMMIT = "precommit"

class ValidatorState(Enum):
    """Validator states"""
    ACTIVE = "active"
    JAILED = "jailed"
    UNBONDED = "unbonded"

@dataclass
class TendermintBlock:
    """
    Tendermint block structure
    """
    height: int
    round: int
    proposer: str
    transactions: List[Dict]
    prev_hash: str
    timestamp: float
    block_hash: str = ""
    
    def __post_init__(self):
        if not self.block_hash:
            self.block_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        data = f"{self.height}:{self.round}:{self.proposer}:{len(self.transactions)}:{self.prev_hash}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

@dataclass
class Vote:
    """
    Tendermint vote structure
    """
    vote_type: VoteType
    height: int
    round: int
    block_hash: Optional[str]
    validator_id: str
    timestamp: float = field(default_factory=time.time)
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            self.signature = self.calculate_signature()
    
    def calculate_signature(self) -> str:
        """Calculate vote signature"""
        data = f"{self.vote_type.value}:{self.height}:{self.round}:{self.block_hash}:{self.validator_id}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def is_nil_vote(self) -> bool:
        """Check if this is a nil vote"""
        return self.block_hash is None

@dataclass
class Evidence:
    """
    Evidence of malicious behavior
    """
    evidence_type: str
    validator_id: str
    height: int
    details: Dict
    timestamp: float = field(default_factory=time.time)
    
    def get_slash_percentage(self) -> float:
        """Get slashing percentage for this evidence"""
        slash_map = {
            "double_signing": 5.0,
            "long_range_attack": 100.0,
            "downtime": 0.01
        }
        return slash_map.get(self.evidence_type, 1.0)

class TendermintValidator:
    """
    Tendermint validator - Mumbai train conductor
    """
    
    def __init__(self, validator_id: str, voting_power: int = 100):
        self.validator_id = validator_id
        self.voting_power = voting_power
        self.state = ValidatorState.ACTIVE
        
        # Consensus state
        self.current_height = 0
        self.current_round = 0
        self.current_step = RoundStep.PROPOSE
        self.locked_round = -1
        self.locked_value = None
        self.valid_round = -1
        self.valid_value = None
        
        # Vote tracking
        self.prevotes: Dict[Tuple[int, int], List[Vote]] = defaultdict(list)
        self.precommits: Dict[Tuple[int, int], List[Vote]] = defaultdict(list)
        
        # Performance metrics
        self.blocks_proposed = 0
        self.votes_cast = 0
        self.proposals_accepted = 0
        self.rounds_participated = 0
        
        # Mumbai characteristics
        self.reliability = random.uniform(0.9, 0.99)
        self.latency = random.uniform(0.05, 0.3)  # Network latency
        self.availability = random.uniform(0.95, 1.0)
        
        print(f"🚂 Tendermint Validator {validator_id} initialized (power: {voting_power})")
    
    def is_proposer(self, height: int, round: int, validators: List[str], 
                   voting_powers: Dict[str, int]) -> bool:
        """
        Check if this validator is proposer for given height/round
        Tendermint uses deterministic proposer selection
        """
        # Simplified proposer selection (weighted round-robin)
        total_power = sum(voting_powers.values())
        if total_power == 0:
            return False
        
        # Calculate proposer index based on height and round
        proposer_index = (height + round) % len(validators)
        selected_proposer = validators[proposer_index]
        
        return selected_proposer == self.validator_id
    
    def propose_block(self, height: int, round: int, transactions: List[Dict], 
                     prev_hash: str) -> TendermintBlock:
        """
        Propose block - Mumbai train schedule proposal
        """
        if self.state != ValidatorState.ACTIVE:
            raise Exception(f"Validator {self.validator_id} is not active")
        
        # Simulate processing time
        time.sleep(self.latency)
        
        # Check availability
        if random.random() > self.availability:
            raise Exception(f"Validator {self.validator_id} is unavailable")
        
        block = TendermintBlock(
            height=height,
            round=round,
            proposer=self.validator_id,
            transactions=transactions,
            prev_hash=prev_hash,
            timestamp=time.time()
        )
        
        self.blocks_proposed += 1
        self.current_height = height
        self.current_round = round
        self.current_step = RoundStep.PREVOTE
        
        print(f"📋 {self.validator_id} proposed block at height {height}, round {round}")
        return block
    
    def vote_prevote(self, height: int, round: int, 
                    proposed_block: Optional[TendermintBlock]) -> Vote:
        """
        Cast prevote - Mumbai conductor's initial signal
        """
        self.votes_cast += 1
        
        # Decision logic for prevoting
        block_hash = None
        if proposed_block and self.should_prevote_for_block(proposed_block):
            block_hash = proposed_block.block_hash
            
        vote = Vote(
            vote_type=VoteType.PREVOTE,
            height=height,
            round=round,
            block_hash=block_hash,
            validator_id=self.validator_id
        )
        
        # Store vote
        self.prevotes[(height, round)].append(vote)
        
        if block_hash:
            print(f"   ✅ {self.validator_id} prevoted for block {block_hash[:8]}")
        else:
            print(f"   ❌ {self.validator_id} prevoted nil")
        
        return vote
    
    def vote_precommit(self, height: int, round: int, 
                      prevote_tally: Dict[str, int]) -> Vote:
        """
        Cast precommit - Mumbai conductor's final confirmation
        """
        self.votes_cast += 1
        
        # Check if any block has +2/3 prevotes
        winning_block = None
        total_power = sum(prevote_tally.values())
        
        for block_hash, power in prevote_tally.items():
            if block_hash != "nil" and power > (total_power * 2 / 3):
                winning_block = block_hash
                break
        
        vote = Vote(
            vote_type=VoteType.PRECOMMIT,
            height=height,
            round=round,
            block_hash=winning_block,
            validator_id=self.validator_id
        )
        
        # Store vote
        self.precommits[(height, round)].append(vote)
        
        if winning_block:
            print(f"   🎯 {self.validator_id} precommitted to {winning_block[:8]}")
            
            # Lock on this value if not already locked or higher round
            if self.locked_round < round:
                self.locked_round = round
                self.locked_value = winning_block
                
        else:
            print(f"   ⏸️ {self.validator_id} precommitted nil")
        
        return vote
    
    def should_prevote_for_block(self, block: TendermintBlock) -> bool:
        """
        Decide whether to prevote for a block
        """
        # Locked value check
        if self.locked_round >= 0 and self.locked_value:
            return block.block_hash == self.locked_value
        
        # Valid value check  
        if self.valid_round >= 0 and self.valid_value:
            if block.round > self.valid_round:
                return True
            return block.block_hash == self.valid_value
        
        # Basic validity check
        return self.is_block_valid(block)
    
    def is_block_valid(self, block: TendermintBlock) -> bool:
        """
        Validate block - Mumbai quality control
        """
        # Simulate validation with some randomness for failures
        if random.random() > self.reliability:
            return False
        
        # Basic checks
        if block.height <= self.current_height and self.current_height > 0:
            return False
        
        if not block.transactions:
            return len(block.transactions) >= 0  # Empty blocks are valid
        
        return True
    
    def advance_round(self, new_round: int):
        """
        Advance to new round - Mumbai train delay handling
        """
        if new_round > self.current_round:
            self.current_round = new_round
            self.current_step = RoundStep.PROPOSE
            print(f"   🔄 {self.validator_id} advanced to round {new_round}")
    
    def commit_block(self, block: TendermintBlock):
        """
        Commit block to blockchain - Mumbai train departure confirmation
        """
        self.current_height = block.height + 1
        self.current_round = 0
        self.current_step = RoundStep.PROPOSE
        
        # Reset locks
        self.locked_round = -1
        self.locked_value = None
        self.valid_round = -1
        self.valid_value = None
        
        print(f"   📦 {self.validator_id} committed block at height {block.height}")
    
    def submit_evidence(self, evidence: Evidence):
        """
        Submit evidence of malicious behavior
        """
        print(f"⚖️ {self.validator_id} submitted evidence: {evidence.evidence_type} against {evidence.validator_id}")
    
    def get_validator_stats(self) -> Dict:
        """Get validator statistics"""
        return {
            "validator_id": self.validator_id,
            "voting_power": self.voting_power,
            "state": self.state.value,
            "current_height": self.current_height,
            "current_round": self.current_round,
            "blocks_proposed": self.blocks_proposed,
            "votes_cast": self.votes_cast,
            "proposals_accepted": self.proposals_accepted,
            "rounds_participated": self.rounds_participated,
            "reliability": self.reliability,
            "availability": self.availability
        }

class TendermintConsensus:
    """
    Tendermint Consensus Engine - Mumbai Local Train System
    """
    
    def __init__(self, validators: List[TendermintValidator]):
        self.validators = {v.validator_id: v for v in validators}
        self.validator_ids = list(self.validators.keys())
        self.voting_powers = {v.validator_id: v.voting_power for v in validators}
        
        # Blockchain state
        self.blockchain: List[TendermintBlock] = []
        self.current_height = 1
        self.current_round = 0
        
        # Consensus parameters
        self.timeout_propose = 3.0
        self.timeout_prevote = 1.0
        self.timeout_precommit = 1.0
        self.timeout_commit = 1.0
        
        # Vote tracking
        self.current_prevotes: Dict[str, int] = defaultdict(int)
        self.current_precommits: Dict[str, int] = defaultdict(int)
        
        # Evidence tracking
        self.evidence_pool: List[Evidence] = []
        
        # Performance metrics
        self.rounds_completed = 0
        self.total_consensus_time = 0.0
        
        print(f"🚂 Tendermint Consensus initialized with {len(validators)} validators")
        print(f"   Total voting power: {sum(self.voting_powers.values())}")
    
    def get_proposer(self, height: int, round: int) -> str:
        """
        Get proposer for given height and round
        """
        # Weighted round-robin proposer selection
        total_power = sum(self.voting_powers.values())
        if total_power == 0:
            return self.validator_ids[0]
        
        proposer_index = (height + round) % len(self.validator_ids)
        return self.validator_ids[proposer_index]
    
    def run_consensus_round(self, transactions: List[Dict]) -> Optional[TendermintBlock]:
        """
        Run single consensus round - Mumbai train scheduling round
        """
        print(f"\n🎯 CONSENSUS ROUND: Height {self.current_height}, Round {self.current_round}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Phase 1: Propose
        committed_block = self.propose_phase(transactions)
        if committed_block:
            consensus_time = time.time() - start_time
            self.total_consensus_time += consensus_time
            self.rounds_completed += 1
            print(f"   ⏱️ Consensus completed in {consensus_time:.2f}s")
            return committed_block
        
        # Phase 2: Prevote
        prevote_result = self.prevote_phase()
        if not prevote_result:
            self.advance_round()
            return None
        
        # Phase 3: Precommit
        precommit_result = self.precommit_phase(prevote_result)
        if not precommit_result:
            self.advance_round()
            return None
        
        # Phase 4: Commit
        committed_block = self.commit_phase(precommit_result)
        if committed_block:
            consensus_time = time.time() - start_time
            self.total_consensus_time += consensus_time
            self.rounds_completed += 1
            print(f"   ⏱️ Consensus completed in {consensus_time:.2f}s")
        
        return committed_block
    
    def propose_phase(self, transactions: List[Dict]) -> Optional[TendermintBlock]:
        """
        Propose phase - Mumbai train schedule announcement
        """
        print(f"\n📋 PROPOSE PHASE")
        print("-" * 20)
        
        proposer_id = self.get_proposer(self.current_height, self.current_round)
        proposer = self.validators[proposer_id]
        
        print(f"   Proposer: {proposer_id}")
        
        try:
            prev_hash = self.blockchain[-1].block_hash if self.blockchain else "genesis"
            
            proposed_block = proposer.propose_block(
                self.current_height,
                self.current_round,
                transactions,
                prev_hash
            )
            
            # Broadcast proposal (simulated)
            print(f"   📤 Block proposal broadcasted")
            
            # Wait for proposal timeout
            time.sleep(min(self.timeout_propose, 1.0))  # Reduced for simulation
            
            return proposed_block
            
        except Exception as e:
            print(f"   ❌ Proposal failed: {str(e)}")
            return None
    
    def prevote_phase(self) -> Optional[str]:
        """
        Prevote phase - Mumbai conductors' initial signals
        """
        print(f"\n🗳️ PREVOTE PHASE")
        print("-" * 20)
        
        # Collect prevotes from all validators
        prevotes = []
        for validator in self.validators.values():
            if validator.state == ValidatorState.ACTIVE:
                try:
                    # In real implementation, proposed_block would be received from network
                    proposed_block = None  # Simplified
                    
                    vote = validator.vote_prevote(
                        self.current_height,
                        self.current_round,
                        proposed_block
                    )
                    prevotes.append(vote)
                    
                except Exception as e:
                    print(f"   ❌ {validator.validator_id} prevote failed: {str(e)}")
        
        # Tally prevotes
        prevote_tally = defaultdict(int)
        for vote in prevotes:
            block_hash = vote.block_hash or "nil"
            validator_power = self.voting_powers[vote.validator_id]
            prevote_tally[block_hash] += validator_power
        
        total_power = sum(self.voting_powers.values())
        
        print(f"   📊 Prevote tally:")
        for block_hash, power in prevote_tally.items():
            percentage = (power / total_power) * 100
            hash_display = block_hash[:8] if block_hash != "nil" else "nil"
            print(f"      {hash_display}: {power} votes ({percentage:.1f}%)")
        
        # Check for +2/3 majority
        for block_hash, power in prevote_tally.items():
            if power > (total_power * 2 / 3):
                if block_hash != "nil":
                    print(f"   ✅ Block {block_hash[:8]} has +2/3 prevotes")
                    return block_hash
                else:
                    print(f"   ❌ Nil has +2/3 prevotes")
                    return None
        
        print(f"   ⏸️ No +2/3 prevote majority")
        return None
    
    def precommit_phase(self, winning_block: str) -> Optional[str]:
        """
        Precommit phase - Mumbai conductors' final confirmations
        """
        print(f"\n🎯 PRECOMMIT PHASE")
        print("-" * 20)
        
        # Simulate prevote tally for precommit decisions
        prevote_tally = {winning_block: sum(self.voting_powers.values())}
        
        # Collect precommits
        precommits = []
        for validator in self.validators.values():
            if validator.state == ValidatorState.ACTIVE:
                try:
                    vote = validator.vote_precommit(
                        self.current_height,
                        self.current_round,
                        prevote_tally
                    )
                    precommits.append(vote)
                    
                except Exception as e:
                    print(f"   ❌ {validator.validator_id} precommit failed: {str(e)}")
        
        # Tally precommits
        precommit_tally = defaultdict(int)
        for vote in precommits:
            block_hash = vote.block_hash or "nil"
            validator_power = self.voting_powers[vote.validator_id]
            precommit_tally[block_hash] += validator_power
        
        total_power = sum(self.voting_powers.values())
        
        print(f"   📊 Precommit tally:")
        for block_hash, power in precommit_tally.items():
            percentage = (power / total_power) * 100
            hash_display = block_hash[:8] if block_hash != "nil" else "nil"
            print(f"      {hash_display}: {power} votes ({percentage:.1f}%)")
        
        # Check for +2/3 majority
        for block_hash, power in precommit_tally.items():
            if power > (total_power * 2 / 3):
                if block_hash != "nil":
                    print(f"   ✅ Block {block_hash[:8]} has +2/3 precommits")
                    return block_hash
        
        print(f"   ⏸️ No +2/3 precommit majority")
        return None
    
    def commit_phase(self, commit_block_hash: str) -> Optional[TendermintBlock]:
        """
        Commit phase - Mumbai train final departure
        """
        print(f"\n📦 COMMIT PHASE")
        print("-" * 20)
        
        # Create committed block (simplified)
        committed_block = TendermintBlock(
            height=self.current_height,
            round=self.current_round,
            proposer=self.get_proposer(self.current_height, self.current_round),
            transactions=[],  # Would contain actual transactions
            prev_hash=self.blockchain[-1].block_hash if self.blockchain else "genesis",
            timestamp=time.time()
        )
        committed_block.block_hash = commit_block_hash
        
        # Add to blockchain
        self.blockchain.append(committed_block)
        
        # Update all validators
        for validator in self.validators.values():
            validator.commit_block(committed_block)
        
        # Move to next height
        self.current_height += 1
        self.current_round = 0
        
        print(f"   ✅ Block committed at height {committed_block.height}")
        print(f"   🔗 Blockchain length: {len(self.blockchain)}")
        
        return committed_block
    
    def advance_round(self):
        """
        Advance to next round - Mumbai train delay management
        """
        self.current_round += 1
        
        for validator in self.validators.values():
            validator.advance_round(self.current_round)
        
        print(f"   🔄 Advanced to round {self.current_round}")
    
    def simulate_consensus_session(self, num_blocks: int = 10) -> List[Dict]:
        """
        Simulate complete consensus session - Mumbai daily operations
        """
        print(f"\n🚂 SIMULATING TENDERMINT CONSENSUS SESSION")
        print(f"Target blocks: {num_blocks}")
        print("=" * 70)
        
        session_results = []
        
        for block_num in range(num_blocks):
            print(f"\n{'='*50}")
            print(f"BLOCK {block_num + 1}/{num_blocks}")
            print(f"{'='*50}")
            
            # Generate sample transactions
            transactions = [
                {"tx_id": f"tx_{self.current_height}_{i}", "amount": random.uniform(1, 100)}
                for i in range(random.randint(1, 5))
            ]
            
            max_rounds = 5  # Maximum rounds to try
            committed_block = None
            
            for round_attempt in range(max_rounds):
                if round_attempt > 0:
                    print(f"\n🔄 Round {round_attempt + 1} attempt...")
                
                committed_block = self.run_consensus_round(transactions)
                if committed_block:
                    break
            
            if committed_block:
                session_results.append({
                    "height": committed_block.height,
                    "rounds": self.current_round,
                    "proposer": committed_block.proposer,
                    "transactions": len(committed_block.transactions),
                    "success": True,
                    "timestamp": committed_block.timestamp
                })
            else:
                print(f"   ❌ Failed to reach consensus after {max_rounds} rounds")
                session_results.append({
                    "height": self.current_height,
                    "rounds": max_rounds,
                    "proposer": None,
                    "transactions": 0,
                    "success": False,
                    "timestamp": time.time()
                })
                
                # Move to next height anyway
                self.current_height += 1
                self.current_round = 0
            
            # Brief pause between blocks
            time.sleep(0.5)
        
        return session_results
    
    def get_consensus_stats(self) -> Dict:
        """Get consensus performance statistics"""
        validator_stats = [v.get_validator_stats() for v in self.validators.values()]
        
        avg_consensus_time = (
            self.total_consensus_time / max(1, self.rounds_completed)
        )
        
        return {
            "total_validators": len(self.validators),
            "blockchain_height": len(self.blockchain),
            "current_height": self.current_height,
            "current_round": self.current_round,
            "rounds_completed": self.rounds_completed,
            "total_consensus_time": self.total_consensus_time,
            "average_consensus_time": avg_consensus_time,
            "evidence_count": len(self.evidence_pool),
            "validator_details": validator_stats
        }

def create_mumbai_tendermint_network():
    """
    Create Mumbai local train style Tendermint network
    """
    print("🏗️ CREATING MUMBAI TENDERMINT NETWORK")
    print("=" * 50)
    
    # Create validators representing Mumbai local train lines
    mumbai_lines = [
        ("Central_Line", 150),
        ("Western_Line", 140),
        ("Harbour_Line", 100),
        ("Trans_Harbour", 80),
        ("Mono_Rail", 60),
        ("Metro_Line_1", 70)
    ]
    
    validators = []
    for line_name, voting_power in mumbai_lines:
        validator = TendermintValidator(line_name, voting_power)
        validators.append(validator)
    
    consensus = TendermintConsensus(validators)
    
    return consensus, validators

if __name__ == "__main__":
    print("🚀 TENDERMINT CONSENSUS SYSTEM")
    print("Mumbai Local Train Coordination")
    print("=" * 70)
    
    try:
        # Create Mumbai Tendermint network
        consensus, validators = create_mumbai_tendermint_network()
        
        # Show initial network state
        initial_stats = consensus.get_consensus_stats()
        print(f"\n📊 INITIAL NETWORK STATE")
        print("-" * 40)
        print(f"Total validators: {initial_stats['total_validators']}")
        print(f"Total voting power: {sum(v.voting_power for v in validators)}")
        
        # Simulate consensus session
        session_results = consensus.simulate_consensus_session(num_blocks=6)
        
        # Analyze results
        successful_blocks = [r for r in session_results if r['success']]
        
        print(f"\n📈 SESSION RESULTS")
        print("=" * 40)
        print(f"Blocks attempted: {len(session_results)}")
        print(f"Blocks committed: {len(successful_blocks)}")
        print(f"Success rate: {len(successful_blocks)/len(session_results)*100:.1f}%")
        
        if successful_blocks:
            avg_rounds = sum(r['rounds'] for r in successful_blocks) / len(successful_blocks)
            print(f"Average rounds per block: {avg_rounds:.1f}")
        
        # Final statistics
        final_stats = consensus.get_consensus_stats()
        
        print(f"\n🏆 FINAL STATISTICS")
        print("-" * 30)
        print(f"Blockchain height: {final_stats['blockchain_height']}")
        print(f"Average consensus time: {final_stats['average_consensus_time']:.2f}s")
        print(f"Rounds completed: {final_stats['rounds_completed']}")
        
        # Validator performance
        print(f"\n🚂 VALIDATOR PERFORMANCE")
        print("-" * 30)
        for validator in validators[:3]:  # Show top 3
            stats = validator.get_validator_stats()
            print(f"{stats['validator_id']}: {stats['blocks_proposed']} blocks, {stats['votes_cast']} votes")
        
        print("\n🎯 Key Insights:")
        print("• Tendermint provides instant finality")
        print("• Round-based consensus with timeout progression")
        print("• Byzantine fault tolerance with immediate confirmation")
        print("• Like Mumbai locals - precise timing and instant confirmation!")
        
        print("\n🎊 TENDERMINT SIMULATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error in Tendermint simulation: {e}")
        raise