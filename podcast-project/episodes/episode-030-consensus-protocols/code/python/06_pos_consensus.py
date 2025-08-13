#!/usr/bin/env python3
"""
Proof of Stake (PoS) Consensus Implementation
=============================================

Ethereum 2.0 style staking consensus - Mumbai society committee ki tarah!
Just like Mumbai housing societies elect committees based on ownership stakes,
PoS selects validators based on their stake in the network.

Features:
- Stake-based validator selection
- Slashing for malicious behavior
- Reward distribution
- Delegated staking (Mumbai investor style)
- Validator rotation

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import uuid
import math

class ValidatorStatus(Enum):
    """Validator status in PoS system"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SLASHED = "slashed"
    PENDING = "pending"
    EXITING = "exiting"

class SlashingReason(Enum):
    """Reasons for validator slashing"""
    DOUBLE_VOTING = "double_voting"
    LONG_RANGE_ATTACK = "long_range_attack"
    NOTHING_AT_STAKE = "nothing_at_stake"
    OFFLINE_PENALTY = "offline_penalty"
    INVALID_ATTESTATION = "invalid_attestation"

@dataclass
class Stake:
    """
    Staking record - Mumbai society share certificate
    """
    staker_id: str
    validator_id: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    lock_period: int = 365  # Days
    delegation: bool = False
    
    def is_locked(self) -> bool:
        """Check if stake is still locked"""
        lock_duration = self.lock_period * 24 * 3600  # Convert to seconds
        return (time.time() - self.timestamp) < lock_duration
    
    def calculate_rewards(self, annual_rate: float, days: int) -> float:
        """Calculate staking rewards"""
        return self.amount * (annual_rate / 365) * days

@dataclass
class Block:
    """
    PoS Block structure
    """
    block_number: int
    previous_hash: str
    validator_id: str
    transactions: List[Dict]
    timestamp: float
    block_hash: str = ""
    attestations: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.block_hash:
            self.block_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = f"{self.block_number}:{self.previous_hash}:{self.validator_id}:{len(self.transactions)}:{self.timestamp}"
        return hashlib.sha256(block_data.encode()).hexdigest()

@dataclass
class Attestation:
    """
    Validator attestation - Mumbai committee vote
    """
    attester_id: str
    block_hash: str
    block_number: int
    timestamp: float
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            self.signature = self.calculate_signature()
    
    def calculate_signature(self) -> str:
        """Calculate attestation signature"""
        data = f"{self.attester_id}:{self.block_hash}:{self.block_number}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

class PoSValidator:
    """
    Proof of Stake Validator - Mumbai society committee member
    """
    
    def __init__(self, validator_id: str, initial_stake: float):
        self.validator_id = validator_id
        self.total_stake = initial_stake
        self.own_stake = initial_stake
        self.delegated_stakes: List[Stake] = []
        
        self.status = ValidatorStatus.ACTIVE
        self.reputation_score = 1.0  # 0-1 scale
        
        # Performance metrics
        self.blocks_proposed = 0
        self.blocks_finalized = 0
        self.attestations_made = 0
        self.successful_attestations = 0
        self.rewards_earned = 0.0
        self.penalties_incurred = 0.0
        
        # Mumbai characteristics
        self.reliability = random.uniform(0.85, 0.98)
        self.response_time = random.uniform(0.1, 2.0)  # Seconds
        self.network_connectivity = random.uniform(0.9, 1.0)
        
        print(f"🏛️ Validator {validator_id} initialized with stake: {initial_stake}")
    
    def add_delegated_stake(self, stake: Stake):
        """Accept delegated stake - Mumbai investment"""
        self.delegated_stakes.append(stake)
        self.total_stake += stake.amount
        print(f"   💰 Delegated stake received: {stake.amount} from {stake.staker_id}")
    
    def remove_delegated_stake(self, staker_id: str) -> bool:
        """Remove delegated stake"""
        for i, stake in enumerate(self.delegated_stakes):
            if stake.staker_id == staker_id:
                if stake.is_locked():
                    print(f"   ❌ Cannot remove stake from {staker_id} - still locked")
                    return False
                
                self.total_stake -= stake.amount
                self.delegated_stakes.pop(i)
                print(f"   📤 Delegated stake removed: {stake.amount} from {staker_id}")
                return True
        return False
    
    def propose_block(self, block_number: int, previous_hash: str, 
                     transactions: List[Dict]) -> Block:
        """
        Propose new block - Mumbai committee proposal
        """
        if self.status != ValidatorStatus.ACTIVE:
            raise Exception(f"Validator {self.validator_id} is not active")
        
        # Simulate network delay and reliability
        time.sleep(self.response_time)
        
        if random.random() > self.reliability:
            raise Exception(f"Validator {self.validator_id} failed to propose block (Mumbai network issue)")
        
        block = Block(
            block_number=block_number,
            previous_hash=previous_hash,
            validator_id=self.validator_id,
            transactions=transactions,
            timestamp=time.time()
        )
        
        self.blocks_proposed += 1
        print(f"📝 {self.validator_id} proposed block {block_number}")
        
        return block
    
    def attest_block(self, block: Block) -> Attestation:
        """
        Attest to a block - Mumbai committee approval
        """
        if self.status != ValidatorStatus.ACTIVE:
            raise Exception(f"Validator {self.validator_id} is not active")
        
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate network connectivity issues
        if random.random() > self.network_connectivity:
            raise Exception(f"Network connectivity issue for {self.validator_id}")
        
        attestation = Attestation(
            attester_id=self.validator_id,
            block_hash=block.block_hash,
            block_number=block.block_number,
            timestamp=time.time()
        )
        
        self.attestations_made += 1
        print(f"   ✅ {self.validator_id} attested to block {block.block_number}")
        
        return attestation
    
    def apply_slashing(self, reason: SlashingReason, penalty_percentage: float):
        """
        Apply slashing penalty - Mumbai committee punishment
        """
        penalty_amount = self.own_stake * (penalty_percentage / 100)
        self.own_stake -= penalty_amount
        self.total_stake -= penalty_amount
        self.penalties_incurred += penalty_amount
        
        if penalty_percentage >= 50:  # Severe slashing
            self.status = ValidatorStatus.SLASHED
        
        print(f"⚡ {self.validator_id} slashed: {reason.value} - penalty: {penalty_amount}")
        
        # Reduce reputation
        self.reputation_score = max(0.1, self.reputation_score - 0.2)
    
    def distribute_rewards(self, block_reward: float):
        """
        Distribute block rewards - Mumbai profit sharing
        """
        if self.total_stake == 0:
            return
        
        # Validator commission (typically 5-10%)
        validator_commission = block_reward * 0.05
        delegator_rewards = block_reward - validator_commission
        
        # Own stake reward
        own_stake_ratio = self.own_stake / self.total_stake
        own_reward = validator_commission + (delegator_rewards * own_stake_ratio)
        
        self.rewards_earned += own_reward
        
        # Distribute to delegators
        for stake in self.delegated_stakes:
            delegator_ratio = stake.amount / self.total_stake
            delegator_reward = delegator_rewards * delegator_ratio
            print(f"   💰 Delegator {stake.staker_id} earned: {delegator_reward:.4f}")
        
        print(f"   🏆 Validator {self.validator_id} earned: {own_reward:.4f}")
    
    def get_validator_stats(self) -> Dict:
        """Get validator performance statistics"""
        if self.attestations_made > 0:
            success_rate = self.successful_attestations / self.attestations_made
        else:
            success_rate = 0.0
        
        return {
            "validator_id": self.validator_id,
            "status": self.status.value,
            "total_stake": self.total_stake,
            "own_stake": self.own_stake,
            "delegated_stake": self.total_stake - self.own_stake,
            "delegator_count": len(self.delegated_stakes),
            "blocks_proposed": self.blocks_proposed,
            "blocks_finalized": self.blocks_finalized,
            "attestation_success_rate": success_rate,
            "rewards_earned": self.rewards_earned,
            "penalties_incurred": self.penalties_incurred,
            "reputation_score": self.reputation_score,
            "net_earnings": self.rewards_earned - self.penalties_incurred
        }

class PoSConsensus:
    """
    Proof of Stake Consensus System - Mumbai Housing Society
    """
    
    def __init__(self, min_stake: float = 32.0, max_validators: int = 100):
        self.min_stake = min_stake
        self.max_validators = max_validators
        
        self.validators: Dict[str, PoSValidator] = {}
        self.active_validators: List[str] = []
        self.blockchain: List[Block] = []
        
        # Consensus parameters
        self.finality_threshold = 0.67  # 2/3 majority for finalization
        self.attestation_window = 10    # Blocks to collect attestations
        self.reward_per_block = 2.0     # Base reward per block
        
        # Network state
        self.current_epoch = 0
        self.epoch_length = 32  # Blocks per epoch
        self.pending_attestations: Dict[int, List[Attestation]] = defaultdict(list)
        
        print("🏛️ PoS Consensus System initialized")
        print(f"   Minimum stake: {min_stake}")
        print(f"   Maximum validators: {max_validators}")
        print(f"   Finality threshold: {self.finality_threshold*100}%")
    
    def register_validator(self, validator: PoSValidator) -> bool:
        """
        Register new validator - Mumbai society membership
        """
        if validator.total_stake < self.min_stake:
            print(f"❌ {validator.validator_id} stake too low: {validator.total_stake} < {self.min_stake}")
            return False
        
        if len(self.validators) >= self.max_validators:
            print(f"❌ Maximum validators reached: {len(self.validators)}")
            return False
        
        if validator.validator_id in self.validators:
            print(f"❌ Validator {validator.validator_id} already registered")
            return False
        
        self.validators[validator.validator_id] = validator
        self.active_validators.append(validator.validator_id)
        
        print(f"✅ Validator {validator.validator_id} registered")
        return True
    
    def select_block_proposer(self, block_number: int) -> str:
        """
        Select block proposer using stake-weighted randomness
        Mumbai society committee rotation
        """
        if not self.active_validators:
            raise Exception("No active validators")
        
        # Calculate stake weights
        total_stake = sum(self.validators[vid].total_stake for vid in self.active_validators)
        
        if total_stake == 0:
            raise Exception("No stake in active validators")
        
        # Weighted random selection based on stake
        random.seed(block_number)  # Deterministic randomness based on block number
        target = random.uniform(0, total_stake)
        
        current_weight = 0
        for validator_id in self.active_validators:
            validator = self.validators[validator_id]
            current_weight += validator.total_stake
            
            if current_weight >= target:
                return validator_id
        
        # Fallback to first validator
        return self.active_validators[0]
    
    def propose_block(self, transactions: List[Dict]) -> Tuple[Block, str]:
        """
        Propose new block through selected validator
        """
        block_number = len(self.blockchain)
        previous_hash = self.blockchain[-1].block_hash if self.blockchain else "genesis"
        
        # Select proposer
        proposer_id = self.select_block_proposer(block_number)
        proposer = self.validators[proposer_id]
        
        print(f"\n📋 Block {block_number} proposer: {proposer_id} (stake: {proposer.total_stake})")
        
        # Propose block
        block = proposer.propose_block(block_number, previous_hash, transactions)
        
        return block, proposer_id
    
    def collect_attestations(self, block: Block) -> List[Attestation]:
        """
        Collect attestations from validators - Mumbai voting process
        """
        attestations = []
        
        print(f"   🗳️ Collecting attestations for block {block.block_number}")
        
        # All active validators except proposer can attest
        attesters = [vid for vid in self.active_validators if vid != block.validator_id]
        
        for validator_id in attesters:
            validator = self.validators[validator_id]
            
            try:
                # Simulate validator decision (most will attest if block is valid)
                will_attest = random.random() < validator.reliability
                
                if will_attest:
                    attestation = validator.attest_block(block)
                    attestations.append(attestation)
                    validator.successful_attestations += 1
                
            except Exception as e:
                print(f"   ❌ {validator_id} failed to attest: {str(e)}")
        
        return attestations
    
    def check_finality(self, block: Block, attestations: List[Attestation]) -> bool:
        """
        Check if block reaches finality - Mumbai consensus achieved
        """
        # Calculate total stake of attesters
        attester_stake = 0
        for attestation in attestations:
            validator = self.validators[attestation.attester_id]
            attester_stake += validator.total_stake
        
        # Calculate total active stake
        total_active_stake = sum(
            self.validators[vid].total_stake 
            for vid in self.active_validators
        )
        
        # Check finality threshold
        if total_active_stake == 0:
            return False
        
        attestation_ratio = attester_stake / total_active_stake
        is_finalized = attestation_ratio >= self.finality_threshold
        
        print(f"   📊 Attestation ratio: {attestation_ratio:.2%} (threshold: {self.finality_threshold:.2%})")
        print(f"   {'✅ FINALIZED' if is_finalized else '⏳ Pending finality'}")
        
        return is_finalized
    
    def add_block_to_chain(self, block: Block, attestations: List[Attestation]):
        """
        Add finalized block to blockchain
        """
        block.attestations = [att.__dict__ for att in attestations]
        self.blockchain.append(block)
        
        # Mark block as finalized for proposer
        proposer = self.validators[block.validator_id]
        proposer.blocks_finalized += 1
        
        print(f"   ⛓️ Block {block.block_number} added to chain")
    
    def distribute_block_rewards(self, block: Block, attestations: List[Attestation]):
        """
        Distribute rewards to proposer and attesters
        """
        # Proposer gets base reward
        proposer = self.validators[block.validator_id]
        proposer_reward = self.reward_per_block * 0.6  # 60% to proposer
        proposer.distribute_rewards(proposer_reward)
        
        # Attesters share remaining reward
        if attestations:
            attester_reward_pool = self.reward_per_block * 0.4  # 40% to attesters
            reward_per_attester = attester_reward_pool / len(attestations)
            
            for attestation in attestations:
                validator = self.validators[attestation.attester_id]
                validator.distribute_rewards(reward_per_attester)
    
    def simulate_slashing_event(self, validator_id: str, reason: SlashingReason):
        """
        Simulate slashing event - Mumbai committee punishment
        """
        if validator_id not in self.validators:
            return
        
        validator = self.validators[validator_id]
        
        # Different penalty percentages for different reasons
        penalty_map = {
            SlashingReason.DOUBLE_VOTING: 50.0,       # Severe
            SlashingReason.LONG_RANGE_ATTACK: 100.0,  # Maximum
            SlashingReason.NOTHING_AT_STAKE: 30.0,    # Moderate
            SlashingReason.OFFLINE_PENALTY: 5.0,      # Light
            SlashingReason.INVALID_ATTESTATION: 10.0  # Light-moderate
        }
        
        penalty = penalty_map.get(reason, 5.0)
        validator.apply_slashing(reason, penalty)
        
        # Remove from active validators if severely slashed
        if validator.status == ValidatorStatus.SLASHED:
            if validator_id in self.active_validators:
                self.active_validators.remove(validator_id)
    
    def simulate_consensus_round(self, num_blocks: int = 10) -> List[Dict]:
        """
        Simulate complete consensus rounds - Mumbai society meetings
        """
        print(f"\n🏛️ SIMULATING {num_blocks} CONSENSUS ROUNDS")
        print("=" * 60)
        
        round_results = []
        
        # Generate sample transactions
        transactions = []
        for i in range(num_blocks * 5):  # 5 transactions per block
            tx = {
                "tx_id": f"tx_{i:03d}",
                "from": f"user_{i % 10}",
                "to": f"user_{(i + 1) % 10}", 
                "amount": random.uniform(1.0, 100.0),
                "fee": random.uniform(0.01, 1.0),
                "timestamp": time.time()
            }
            transactions.append(tx)
        
        for block_round in range(num_blocks):
            print(f"\n{'='*50}")
            print(f"CONSENSUS ROUND {block_round + 1}")
            print(f"{'='*50}")
            
            try:
                # Select transactions for this block
                block_transactions = transactions[block_round*5:(block_round+1)*5]
                
                # Propose block
                block, proposer_id = self.propose_block(block_transactions)
                
                # Collect attestations
                attestations = self.collect_attestations(block)
                
                # Check finality
                is_finalized = self.check_finality(block, attestations)
                
                if is_finalized:
                    # Add to blockchain
                    self.add_block_to_chain(block, attestations)
                    
                    # Distribute rewards
                    self.distribute_block_rewards(block, attestations)
                    
                    round_results.append({
                        "block_number": block.block_number,
                        "proposer": proposer_id,
                        "attestations": len(attestations),
                        "finalized": True,
                        "timestamp": block.timestamp
                    })
                else:
                    print(f"   ❌ Block {block.block_number} failed to reach finality")
                    round_results.append({
                        "block_number": block.block_number,
                        "proposer": proposer_id,
                        "attestations": len(attestations),
                        "finalized": False,
                        "timestamp": block.timestamp
                    })
                
                # Simulate occasional slashing events
                if random.random() < 0.1:  # 10% chance
                    random_validator = random.choice(self.active_validators)
                    random_reason = random.choice(list(SlashingReason))
                    print(f"\n⚡ SLASHING EVENT!")
                    self.simulate_slashing_event(random_validator, random_reason)
                
                time.sleep(0.5)  # Brief pause between rounds
                
            except Exception as e:
                print(f"❌ Error in consensus round {block_round + 1}: {str(e)}")
                continue
        
        return round_results
    
    def get_network_stats(self) -> Dict:
        """
        Get comprehensive network statistics
        """
        validator_stats = [v.get_validator_stats() for v in self.validators.values()]
        
        total_stake = sum(v.total_stake for v in self.validators.values())
        active_stake = sum(
            self.validators[vid].total_stake 
            for vid in self.active_validators
        )
        
        return {
            "total_validators": len(self.validators),
            "active_validators": len(self.active_validators),
            "total_stake": total_stake,
            "active_stake": active_stake,
            "blockchain_length": len(self.blockchain),
            "current_epoch": self.current_epoch,
            "finality_threshold": self.finality_threshold,
            "validator_details": validator_stats
        }

def create_mumbai_pos_network():
    """
    Create Mumbai-style PoS network
    """
    print("🏗️ CREATING MUMBAI PoS NETWORK")
    print("=" * 50)
    
    # Initialize consensus system
    pos_system = PoSConsensus(min_stake=32.0, max_validators=20)
    
    # Create validators with Mumbai characteristics
    mumbai_validators = [
        ("Bandra_Society", 50.0),
        ("Andheri_Cooperative", 75.0),
        ("Worli_Heights", 100.0),
        ("Powai_Tech_Park", 150.0),
        ("Borivali_Apartments", 60.0),
        ("Thane_Complex", 80.0),
        ("Kurla_Towers", 45.0),
        ("Malad_Residency", 65.0)
    ]
    
    validators = []
    for name, stake in mumbai_validators:
        validator = PoSValidator(name, stake)
        validators.append(validator)
        pos_system.register_validator(validator)
    
    # Add some delegated stakes (Mumbai investment style)
    delegated_stakes = [
        ("Investor_Sharma", "Worli_Heights", 25.0),
        ("Investor_Patel", "Powai_Tech_Park", 30.0),
        ("Investor_Khan", "Bandra_Society", 20.0),
        ("Investor_Gupta", "Thane_Complex", 15.0)
    ]
    
    for investor, validator_name, amount in delegated_stakes:
        validator = pos_system.validators[validator_name]
        stake = Stake(
            staker_id=investor,
            validator_id=validator_name,
            amount=amount,
            delegation=True
        )
        validator.add_delegated_stake(stake)
    
    return pos_system, validators

if __name__ == "__main__":
    print("🚀 PROOF OF STAKE CONSENSUS SYSTEM")
    print("Mumbai Housing Society Staking Simulation")
    print("=" * 70)
    
    try:
        # Create Mumbai PoS network
        pos_system, validators = create_mumbai_pos_network()
        
        # Show initial network state
        initial_stats = pos_system.get_network_stats()
        print(f"\n📊 INITIAL NETWORK STATE")
        print("-" * 40)
        print(f"Total validators: {initial_stats['total_validators']}")
        print(f"Active validators: {initial_stats['active_validators']}")
        print(f"Total stake: {initial_stats['total_stake']}")
        print(f"Active stake: {initial_stats['active_stake']}")
        
        # Simulate consensus rounds
        consensus_results = pos_system.simulate_consensus_round(num_blocks=8)
        
        # Show consensus results
        print(f"\n🏆 CONSENSUS RESULTS")
        print("=" * 40)
        
        finalized_blocks = [r for r in consensus_results if r['finalized']]
        print(f"Blocks proposed: {len(consensus_results)}")
        print(f"Blocks finalized: {len(finalized_blocks)}")
        print(f"Finalization rate: {len(finalized_blocks)/len(consensus_results)*100:.1f}%")
        
        # Show top validators
        validator_performance = []
        for validator in validators:
            stats = validator.get_validator_stats()
            validator_performance.append((
                stats['validator_id'],
                stats['blocks_finalized'],
                stats['net_earnings']
            ))
        
        validator_performance.sort(key=lambda x: x[2], reverse=True)  # Sort by earnings
        
        print(f"\n🥇 TOP VALIDATORS BY EARNINGS")
        print("-" * 40)
        for name, blocks, earnings in validator_performance[:5]:
            print(f"{name}: {blocks} blocks, {earnings:.4f} rewards")
        
        # Final network statistics
        final_stats = pos_system.get_network_stats()
        
        print(f"\n📈 FINAL NETWORK STATISTICS")
        print("=" * 40)
        print(f"Blockchain length: {final_stats['blockchain_length']}")
        print(f"Active validators: {final_stats['active_validators']}")
        print(f"Total staked: {final_stats['total_stake']}")
        
        print("\n🎯 Key Insights:")
        print("• PoS uses economic incentives for security")
        print("• Validators are rewarded for honest behavior")
        print("• Slashing punishes malicious actions")
        print("• Delegation allows broader participation")
        print("• Like Mumbai societies - stake gives voice in decisions!")
        
        print("\n🎊 PoS CONSENSUS SIMULATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error in PoS simulation: {e}")
        raise