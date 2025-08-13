#!/usr/bin/env python3
"""
Blockchain Proof-of-Stake Consensus Implementation
Episode 45: Distributed Computing at Scale

यह example blockchain में Proof-of-Stake consensus mechanism दिखाता है
Validator selection, stake-based voting, और fork resolution के साथ
decentralized network consensus for Indian blockchain applications।

Production Stats:
- Ethereum 2.0: 600,000+ validators staking 32 ETH each
- Polygon: 100+ validators securing ₹2+ lakh crore TVL
- Solana: 1,400+ validators with 1ms block time
- Indian blockchain adoption: 15M+ users on WazirX
- Energy efficiency: 99.9% less than Proof-of-Work
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import ecdsa
import base58

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidatorStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SLASHED = "SLASHED"
    EXITING = "EXITING"

class TransactionType(Enum):
    TRANSFER = "TRANSFER"
    STAKE = "STAKE"
    UNSTAKE = "UNSTAKE"
    SMART_CONTRACT = "SMART_CONTRACT"
    VALIDATOR_DEPOSIT = "VALIDATOR_DEPOSIT"

@dataclass
class Transaction:
    """Blockchain transaction"""
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    fee: float
    tx_type: TransactionType
    data: Dict[str, Any] = None
    timestamp: datetime = None
    signature: str = ""
    nonce: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.data is None:
            self.data = {}
    
    def get_hash(self) -> str:
        """Calculate transaction hash"""
        tx_string = f"{self.tx_id}{self.from_address}{self.to_address}{self.amount}{self.fee}{self.timestamp.isoformat()}{self.nonce}"
        return hashlib.sha256(tx_string.encode()).hexdigest()

@dataclass
class Block:
    """Blockchain block"""
    block_number: int
    previous_hash: str
    transactions: List[Transaction]
    validator_address: str
    timestamp: datetime
    block_hash: str = ""
    merkle_root: str = ""
    signature: str = ""
    gas_used: int = 0
    gas_limit: int = 1000000
    
    def __post_init__(self):
        if not self.block_hash:
            self.block_hash = self.calculate_hash()
        if not self.merkle_root:
            self.merkle_root = self.calculate_merkle_root()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = f"{self.block_number}{self.previous_hash}{self.validator_address}{self.timestamp.isoformat()}{self.merkle_root}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def calculate_merkle_root(self) -> str:
        """Calculate Merkle root of transactions"""
        if not self.transactions:
            return hashlib.sha256(b"").hexdigest()
        
        tx_hashes = [tx.get_hash() for tx in self.transactions]
        
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])  # Duplicate last hash if odd
            
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            
            tx_hashes = new_hashes
        
        return tx_hashes[0]

@dataclass
class Validator:
    """Proof-of-Stake validator"""
    validator_id: str
    address: str
    public_key: str
    stake_amount: float
    status: ValidatorStatus
    commission_rate: float  # Percentage
    joined_epoch: int
    last_activity: datetime
    
    # Performance metrics
    blocks_proposed: int = 0
    blocks_attested: int = 0
    missed_proposals: int = 0
    slashing_incidents: int = 0
    
    # Rewards and penalties
    rewards_earned: float = 0.0
    penalties_paid: float = 0.0
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    @property
    def effective_stake(self) -> float:
        """Calculate effective stake after penalties"""
        return max(0, self.stake_amount - self.penalties_paid)
    
    @property
    def performance_score(self) -> float:
        """Calculate validator performance score"""
        total_duties = self.blocks_proposed + self.blocks_attested + self.missed_proposals
        if total_duties == 0:
            return 1.0
        
        successful_duties = self.blocks_proposed + self.blocks_attested
        return successful_duties / total_duties

@dataclass
class Attestation:
    """Validator attestation for block consensus"""
    validator_id: str
    block_hash: str
    block_number: int
    epoch: int
    signature: str
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class CryptoUtils:
    """Cryptocurrency utilities for signing and verification"""
    
    @staticmethod
    def generate_keypair() -> Tuple[str, str]:
        """Generate public/private key pair"""
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        
        private_key_hex = private_key.to_string().hex()
        public_key_hex = public_key.to_string().hex()
        
        return private_key_hex, public_key_hex
    
    @staticmethod
    def create_address(public_key: str) -> str:
        """Create address from public key"""
        # Simplified address creation (real blockchains use more complex methods)
        address_hash = hashlib.sha256(public_key.encode()).digest()
        return base58.b58encode(address_hash[:20]).decode()
    
    @staticmethod
    def sign_message(private_key_hex: str, message: str) -> str:
        """Sign message with private key"""
        try:
            private_key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
            signature = private_key.sign(message.encode())
            return signature.hex()
        except:
            # Fallback to simple hash-based signature for demo
            return hashlib.sha256(f"{private_key_hex}{message}".encode()).hexdigest()

class ValidatorSelection:
    """Proof-of-Stake validator selection mechanism"""
    
    def __init__(self):
        self.validators = {}  # validator_id -> Validator
        self.total_stake = 0.0
        self.current_epoch = 0
        self.epoch_duration = 32  # blocks per epoch
        
    def add_validator(self, validator: Validator):
        """Add validator to the network"""
        self.validators[validator.validator_id] = validator
        self.total_stake += validator.effective_stake
        logger.info(f"🏛️ Added validator {validator.validator_id} with {validator.stake_amount} stake")
    
    def remove_validator(self, validator_id: str):
        """Remove validator from network"""
        if validator_id in self.validators:
            validator = self.validators[validator_id]
            self.total_stake -= validator.effective_stake
            del self.validators[validator_id]
            logger.info(f"🏛️ Removed validator {validator_id}")
    
    def select_block_proposer(self, block_number: int) -> Optional[Validator]:
        """Select validator to propose next block using stake-weighted randomness"""
        if not self.validators or self.total_stake == 0:
            return None
        
        # Create deterministic but unpredictable selection based on block number
        random.seed(block_number * 12345)  # Deterministic seed
        
        # Calculate cumulative stakes for weighted selection
        cumulative_stakes = []
        running_total = 0.0
        
        active_validators = [v for v in self.validators.values() 
                           if v.status == ValidatorStatus.ACTIVE and v.effective_stake > 0]
        
        if not active_validators:
            return None
        
        for validator in active_validators:
            running_total += validator.effective_stake
            cumulative_stakes.append((running_total, validator))
        
        # Random selection based on stake weight
        random_value = random.uniform(0, running_total)
        
        for cumulative_stake, validator in cumulative_stakes:
            if random_value <= cumulative_stake:
                return validator
        
        # Fallback to first validator
        return active_validators[0]
    
    def select_attestation_committee(self, epoch: int, committee_size: int = 64) -> List[Validator]:
        """Select committee of validators for attestations"""
        active_validators = [v for v in self.validators.values() 
                           if v.status == ValidatorStatus.ACTIVE and v.effective_stake > 0]
        
        if len(active_validators) <= committee_size:
            return active_validators
        
        # Deterministic selection based on epoch
        random.seed(epoch * 54321)
        
        # Stake-weighted selection for committee
        selected = []
        remaining_validators = active_validators.copy()
        
        for _ in range(committee_size):
            if not remaining_validators:
                break
            
            total_remaining_stake = sum(v.effective_stake for v in remaining_validators)
            if total_remaining_stake == 0:
                break
            
            random_value = random.uniform(0, total_remaining_stake)
            cumulative = 0.0
            
            for i, validator in enumerate(remaining_validators):
                cumulative += validator.effective_stake
                if random_value <= cumulative:
                    selected.append(validator)
                    remaining_validators.pop(i)
                    break
        
        return selected
    
    def slash_validator(self, validator_id: str, slash_amount: float, reason: str):
        """Slash validator for malicious behavior"""
        if validator_id in self.validators:
            validator = self.validators[validator_id]
            
            # Apply slashing penalty
            penalty = min(slash_amount, validator.stake_amount * 0.1)  # Max 10% slash
            validator.penalties_paid += penalty
            validator.slashing_incidents += 1
            
            # Update total stake
            self.total_stake -= penalty
            
            # Deactivate if stake too low
            if validator.effective_stake < 1000:  # Minimum stake requirement
                validator.status = ValidatorStatus.SLASHED
            
            logger.warning(f"⚔️ Slashed validator {validator_id} by {penalty} for {reason}")

class ProofOfStakeConsensus:
    """Proof-of-Stake consensus mechanism"""
    
    def __init__(self):
        self.blockchain = []  # List of blocks
        self.pending_transactions = []
        self.validator_selection = ValidatorSelection()
        
        # Consensus state
        self.current_epoch = 0
        self.finalized_block = 0
        self.justified_block = 0
        
        # Attestations
        self.pending_attestations = defaultdict(list)  # block_number -> [Attestation]
        self.block_votes = defaultdict(float)  # block_hash -> total_stake_voted
        
        # Network parameters
        self.block_time = 12  # seconds
        self.epoch_size = 32  # blocks per epoch
        self.finalization_threshold = 0.67  # 67% of stake for finalization
        
        # Performance metrics
        self.total_transactions = 0
        self.total_blocks = 0
        self.consensus_start_time = datetime.now()
        
        # Create genesis block
        self._create_genesis_block()
        
        logger.info("⛓️ Proof-of-Stake consensus initialized")
    
    def _create_genesis_block(self):
        """Create genesis block"""
        genesis_block = Block(
            block_number=0,
            previous_hash="0" * 64,
            transactions=[],
            validator_address="genesis",
            timestamp=datetime.now()
        )
        
        self.blockchain.append(genesis_block)
        self.finalized_block = 0
        self.justified_block = 0
        logger.info("🏗️ Genesis block created")
    
    async def propose_block(self, proposer: Validator) -> Optional[Block]:
        """Propose new block"""
        if not self.pending_transactions:
            return None
        
        previous_block = self.blockchain[-1]
        
        # Select transactions for block (up to gas limit)
        selected_transactions = []
        total_gas = 0
        
        for tx in self.pending_transactions[:100]:  # Max 100 transactions per block
            tx_gas = 21000  # Base gas cost
            if total_gas + tx_gas <= 1000000:  # Gas limit
                selected_transactions.append(tx)
                total_gas += tx_gas
            else:
                break
        
        if not selected_transactions:
            return None
        
        # Create new block
        new_block = Block(
            block_number=previous_block.block_number + 1,
            previous_hash=previous_block.block_hash,
            transactions=selected_transactions,
            validator_address=proposer.address,
            timestamp=datetime.now(),
            gas_used=total_gas
        )
        
        # Sign block (simplified)
        block_data = f"{new_block.block_hash}{new_block.validator_address}"
        new_block.signature = hashlib.sha256(block_data.encode()).hexdigest()
        
        # Remove selected transactions from pending
        for tx in selected_transactions:
            if tx in self.pending_transactions:
                self.pending_transactions.remove(tx)
        
        # Update proposer stats
        proposer.blocks_proposed += 1
        proposer.last_activity = datetime.now()
        
        logger.info(f"📦 Block {new_block.block_number} proposed by {proposer.validator_id} with {len(selected_transactions)} transactions")
        
        return new_block
    
    async def process_attestation(self, attestation: Attestation) -> bool:
        """Process validator attestation"""
        validator = self.validator_selection.validators.get(attestation.validator_id)
        
        if not validator or validator.status != ValidatorStatus.ACTIVE:
            return False
        
        # Verify attestation is for a valid block
        if attestation.block_number > len(self.blockchain):
            return False
        
        # Add attestation
        self.pending_attestations[attestation.block_number].append(attestation)
        
        # Add stake weight to block votes
        block_hash = attestation.block_hash
        self.block_votes[block_hash] += validator.effective_stake
        
        # Update validator stats
        validator.blocks_attested += 1
        validator.last_activity = datetime.now()
        
        logger.debug(f"✅ Attestation received from {attestation.validator_id} for block {attestation.block_number}")
        
        return True
    
    def check_finalization(self, block_number: int) -> bool:
        """Check if block can be finalized"""
        if block_number >= len(self.blockchain):
            return False
        
        block = self.blockchain[block_number]
        total_stake_voted = self.block_votes.get(block.block_hash, 0)
        
        # Check if supermajority (67%) of stake has voted
        finalization_threshold = self.validator_selection.total_stake * self.finalization_threshold
        
        if total_stake_voted >= finalization_threshold:
            # Update finalized block
            if block_number > self.finalized_block:
                self.finalized_block = block_number
                logger.info(f"🔒 Block {block_number} finalized with {total_stake_voted:.2f} stake votes")
                return True
        
        return False
    
    async def add_block(self, block: Block) -> bool:
        """Add block to blockchain after consensus"""
        # Validate block
        if not self._validate_block(block):
            return False
        
        # Add to blockchain
        self.blockchain.append(block)
        self.total_blocks += 1
        self.total_transactions += len(block.transactions)
        
        # Process transactions (update balances, etc.)
        await self._process_block_transactions(block)
        
        # Check for finalization
        self.check_finalization(block.block_number - 2)  # Finalize 2 blocks behind
        
        logger.info(f"⛓️ Block {block.block_number} added to blockchain")
        
        return True
    
    def _validate_block(self, block: Block) -> bool:
        """Validate block before adding to chain"""
        # Check if previous hash matches
        if len(self.blockchain) > 0:
            previous_block = self.blockchain[-1]
            if block.previous_hash != previous_block.block_hash:
                logger.error(f"❌ Invalid previous hash in block {block.block_number}")
                return False
            
            if block.block_number != previous_block.block_number + 1:
                logger.error(f"❌ Invalid block number: expected {previous_block.block_number + 1}, got {block.block_number}")
                return False
        
        # Validate transactions
        for tx in block.transactions:
            if not self._validate_transaction(tx):
                logger.error(f"❌ Invalid transaction {tx.tx_id} in block {block.block_number}")
                return False
        
        # Verify merkle root
        calculated_merkle = block.calculate_merkle_root()
        if calculated_merkle != block.merkle_root:
            logger.error(f"❌ Invalid merkle root in block {block.block_number}")
            return False
        
        return True
    
    def _validate_transaction(self, tx: Transaction) -> bool:
        """Validate individual transaction"""
        # Basic validation (amount > 0, fee > 0, etc.)
        if tx.amount < 0 or tx.fee < 0:
            return False
        
        if not tx.from_address or not tx.to_address:
            return False
        
        # Additional validation would include signature verification,
        # balance checks, nonce validation, etc.
        
        return True
    
    async def _process_block_transactions(self, block: Block):
        """Process transactions in block (update state)"""
        for tx in block.transactions:
            # In a real blockchain, this would update account balances,
            # execute smart contracts, update state trees, etc.
            logger.debug(f"💳 Processed transaction {tx.tx_id}: {tx.amount} from {tx.from_address} to {tx.to_address}")
    
    def add_transaction(self, transaction: Transaction):
        """Add transaction to pending pool"""
        self.pending_transactions.append(transaction)
        logger.debug(f"📝 Added transaction {transaction.tx_id} to pending pool")
    
    def get_consensus_stats(self) -> Dict[str, Any]:
        """Get comprehensive consensus statistics"""
        uptime = datetime.now() - self.consensus_start_time
        
        # Validator statistics
        active_validators = sum(1 for v in self.validator_selection.validators.values() 
                              if v.status == ValidatorStatus.ACTIVE)
        total_stake = self.validator_selection.total_stake
        
        # Block statistics
        finalization_rate = (self.finalized_block / max(self.total_blocks, 1)) * 100
        
        # Performance metrics
        avg_block_time = uptime.total_seconds() / max(self.total_blocks, 1)
        tps = self.total_transactions / max(uptime.total_seconds(), 1)
        
        return {
            "consensus_uptime": str(uptime),
            "total_blocks": self.total_blocks,
            "finalized_blocks": self.finalized_block,
            "justified_blocks": self.justified_block,
            "finalization_rate": finalization_rate,
            "pending_transactions": len(self.pending_transactions),
            "total_transactions": self.total_transactions,
            "active_validators": active_validators,
            "total_validators": len(self.validator_selection.validators),
            "total_stake": total_stake,
            "avg_block_time": avg_block_time,
            "transactions_per_second": tps,
            "current_epoch": self.current_epoch,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_consensus_dashboard(self):
        """Print consensus dashboard"""
        stats = self.get_consensus_stats()
        
        print(f"\n{'='*80}")
        print(f"⛓️ PROOF-OF-STAKE CONSENSUS DASHBOARD ⛓️")
        print(f"{'='*80}")
        
        print(f"🏛️ Network Overview:")
        print(f"   Consensus Uptime: {stats['consensus_uptime']}")
        print(f"   Total Validators: {stats['total_validators']}")
        print(f"   Active Validators: {stats['active_validators']}")
        print(f"   Total Stake: {stats['total_stake']:,.2f} tokens")
        print(f"   Current Epoch: {stats['current_epoch']}")
        
        print(f"\n⛓️ Blockchain Statistics:")
        print(f"   Total Blocks: {stats['total_blocks']:,}")
        print(f"   Finalized Blocks: {stats['finalized_blocks']:,}")
        print(f"   Finalization Rate: {stats['finalization_rate']:.1f}%")
        print(f"   Avg Block Time: {stats['avg_block_time']:.1f}s")
        
        print(f"\n📊 Transaction Metrics:")
        print(f"   Total Transactions: {stats['total_transactions']:,}")
        print(f"   Pending Transactions: {stats['pending_transactions']:,}")
        print(f"   TPS: {stats['transactions_per_second']:.2f}")
        
        print(f"\n🏛️ Top Validators:")
        validators = sorted(self.validator_selection.validators.values(), 
                          key=lambda v: v.effective_stake, reverse=True)
        
        for i, validator in enumerate(validators[:5]):
            status_icon = {
                ValidatorStatus.ACTIVE: "🟢",
                ValidatorStatus.INACTIVE: "🟡",
                ValidatorStatus.SLASHED: "🔴",
                ValidatorStatus.EXITING: "🟠"
            }.get(validator.status, "⚪")
            
            print(f"   {status_icon} {validator.validator_id}:")
            print(f"     Stake: {validator.effective_stake:,.2f} tokens")
            print(f"     Performance: {validator.performance_score:.2%}")
            print(f"     Blocks Proposed: {validator.blocks_proposed}")
            print(f"     Rewards: {validator.rewards_earned:.2f}")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

async def simulate_pos_network(consensus: ProofOfStakeConsensus, duration_minutes: int = 5):
    """Simulate Proof-of-Stake network operation"""
    logger.info(f"⛓️ Starting PoS network simulation for {duration_minutes} minutes")
    
    # Add validators with different stake amounts
    validators_data = [
        {"id": "validator_reliance", "stake": 50000, "commission": 5.0},
        {"id": "validator_tcs", "stake": 40000, "commission": 3.0},
        {"id": "validator_infosys", "stake": 35000, "commission": 4.0},
        {"id": "validator_hdfc", "stake": 30000, "commission": 6.0},
        {"id": "validator_wipro", "stake": 25000, "commission": 4.5},
        {"id": "validator_bharti", "stake": 20000, "commission": 5.5},
        {"id": "validator_icici", "stake": 15000, "commission": 7.0},
        {"id": "validator_sbi", "stake": 10000, "commission": 8.0},
    ]
    
    for val_data in validators_data:
        private_key, public_key = CryptoUtils.generate_keypair()
        address = CryptoUtils.create_address(public_key)
        
        validator = Validator(
            validator_id=val_data["id"],
            address=address,
            public_key=public_key,
            stake_amount=val_data["stake"],
            status=ValidatorStatus.ACTIVE,
            commission_rate=val_data["commission"],
            joined_epoch=0
        )
        
        consensus.validator_selection.add_validator(validator)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    block_count = 0
    
    try:
        while time.time() < end_time:
            # Generate transactions
            for _ in range(random.randint(5, 20)):
                tx = Transaction(
                    tx_id=f"tx_{int(time.time())}{random.randint(1000, 9999)}",
                    from_address=f"addr_{random.randint(10000, 99999)}",
                    to_address=f"addr_{random.randint(10000, 99999)}",
                    amount=random.uniform(0.1, 1000),
                    fee=random.uniform(0.001, 0.01),
                    tx_type=random.choice(list(TransactionType)),
                    nonce=random.randint(1, 1000)
                )
                consensus.add_transaction(tx)
            
            # Select proposer and create block
            proposer = consensus.validator_selection.select_block_proposer(len(consensus.blockchain))
            
            if proposer and consensus.pending_transactions:
                # Propose block
                new_block = await consensus.propose_block(proposer)
                
                if new_block:
                    # Add block to chain
                    success = await consensus.add_block(new_block)
                    
                    if success:
                        block_count += 1
                        
                        # Generate attestations from committee
                        committee = consensus.validator_selection.select_attestation_committee(
                            consensus.current_epoch, 32
                        )
                        
                        for validator in committee:
                            # 95% chance to attest
                            if random.random() < 0.95:
                                attestation = Attestation(
                                    validator_id=validator.validator_id,
                                    block_hash=new_block.block_hash,
                                    block_number=new_block.block_number,
                                    epoch=consensus.current_epoch,
                                    signature=hashlib.sha256(f"{validator.validator_id}{new_block.block_hash}".encode()).hexdigest(),
                                    timestamp=datetime.now()
                                )
                                
                                await consensus.process_attestation(attestation)
                        
                        # Update epoch if needed
                        if new_block.block_number % consensus.epoch_size == 0:
                            consensus.current_epoch += 1
                            logger.info(f"🔄 Epoch {consensus.current_epoch} started")
            
            # Print dashboard every 30 seconds
            if block_count % 10 == 0 and block_count > 0:
                consensus.print_consensus_dashboard()
            
            # Simulate block time
            await asyncio.sleep(2)  # 2 second blocks for demo
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    
    logger.info(f"🏁 PoS simulation completed! Produced {block_count} blocks")
    
    # Final dashboard
    consensus.print_consensus_dashboard()

async def main():
    """Main demo function"""
    print("🇮🇳 Blockchain Proof-of-Stake Consensus System")
    print("⛓️ Energy-efficient consensus with stake-based validator selection")
    print("🏛️ Simulating Indian blockchain network with major validators...\n")
    
    # Initialize PoS consensus
    consensus = ProofOfStakeConsensus()
    
    try:
        # Show initial dashboard
        consensus.print_consensus_dashboard()
        
        # Run PoS network simulation
        await simulate_pos_network(consensus, duration_minutes=3)
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"💡 Production system capabilities:")
        print(f"   - 99.9% energy efficiency vs Proof-of-Work")
        print(f"   - Stake-based validator selection और rewards")
        print(f"   - Byzantine fault tolerance up to 33% malicious stake")
        print(f"   - Instant finality with 67% supermajority")
        print(f"   - Slashing penalties for malicious behavior")
        print(f"   - Scalable to thousands of validators")
        
    except Exception as e:
        logger.error(f"❌ Error in simulation: {e}")

if __name__ == "__main__":
    # Run the blockchain PoS consensus demo
    asyncio.run(main())