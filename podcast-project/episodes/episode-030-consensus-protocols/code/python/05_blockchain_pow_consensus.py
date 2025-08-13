#!/usr/bin/env python3
"""
Blockchain Proof of Work (PoW) Consensus Implementation
======================================================

Bitcoin-style mining consensus - Mumbai gold market ki tarah!
Just like Mumbai's Zaveri Bazaar gold trading requires proof of authenticity,
blockchain requires proof of work for consensus.

Features:
- SHA-256 based mining
- Difficulty adjustment
- Chain validation
- Orphan blocks handling
- Mining pool simulation (Mumbai style)

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import hashlib
import threading
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import uuid

class BlockStatus(Enum):
    """Block status in the chain"""
    PENDING = "pending"
    MINED = "mined"
    CONFIRMED = "confirmed"
    ORPHANED = "orphaned"

@dataclass
class Transaction:
    """
    Transaction structure - Mumbai hawala style!
    """
    tx_id: str
    sender: str
    receiver: str
    amount: float
    fee: float
    timestamp: float = field(default_factory=time.time)
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            self.signature = self.calculate_signature()
    
    def calculate_signature(self) -> str:
        """Calculate transaction signature"""
        data = f"{self.sender}:{self.receiver}:{self.amount}:{self.fee}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def is_valid(self) -> bool:
        """Validate transaction"""
        return self.signature == self.calculate_signature() and self.amount > 0

@dataclass
class Block:
    """
    Blockchain block structure
    """
    block_number: int
    previous_hash: str
    merkle_root: str
    timestamp: float
    difficulty: int
    nonce: int
    miner_id: str
    transactions: List[Transaction]
    block_hash: str = ""
    status: BlockStatus = BlockStatus.PENDING
    
    # Mining statistics
    mining_duration: float = 0.0
    hash_rate: float = 0.0
    
    def __post_init__(self):
        if not self.block_hash:
            self.block_hash = self.calculate_hash()
    
    def calculate_merkle_root(self) -> str:
        """Calculate Merkle root of transactions"""
        if not self.transactions:
            return "0" * 64
        
        # Simplified Merkle tree calculation
        tx_hashes = [tx.tx_id for tx in self.transactions]
        
        while len(tx_hashes) > 1:
            next_level = []
            for i in range(0, len(tx_hashes), 2):
                left = tx_hashes[i]
                right = tx_hashes[i + 1] if i + 1 < len(tx_hashes) else left
                combined = hashlib.sha256(f"{left}{right}".encode()).hexdigest()
                next_level.append(combined)
            tx_hashes = next_level
        
        return tx_hashes[0] if tx_hashes else "0" * 64
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = f"{self.block_number}:{self.previous_hash}:{self.merkle_root}:{self.timestamp}:{self.difficulty}:{self.nonce}:{self.miner_id}"
        return hashlib.sha256(block_data.encode()).hexdigest()
    
    def is_valid_proof_of_work(self) -> bool:
        """Check if block satisfies proof of work difficulty"""
        target = "0" * self.difficulty
        return self.block_hash.startswith(target)
    
    def get_block_reward(self) -> float:
        """Calculate block mining reward"""
        base_reward = 50.0  # Base mining reward
        
        # Bitcoin-style halving every 210,000 blocks (simplified)
        halvings = self.block_number // 210000
        current_reward = base_reward / (2 ** halvings)
        
        # Add transaction fees
        total_fees = sum(tx.fee for tx in self.transactions)
        
        return current_reward + total_fees

class MiningPool:
    """
    Mining pool - Mumbai cooperative mining!
    Like Mumbai housing society, miners pool resources
    """
    
    def __init__(self, pool_name: str):
        self.pool_name = pool_name
        self.miners: List[str] = []
        self.pool_hash_rate = 0.0
        self.blocks_mined = 0
        self.total_rewards = 0.0
        self.fee_percentage = 2.0  # Pool fee
        
        # Performance tracking
        self.mining_attempts = 0
        self.successful_mines = 0
        
        print(f"⛏️ Mining Pool '{pool_name}' established")
    
    def add_miner(self, miner_id: str, hash_rate: float):
        """Add miner to pool"""
        if miner_id not in self.miners:
            self.miners.append(miner_id)
            self.pool_hash_rate += hash_rate
            print(f"   👷 Miner {miner_id} joined pool (hash rate: {hash_rate:.2f} H/s)")
    
    def remove_miner(self, miner_id: str, hash_rate: float):
        """Remove miner from pool"""
        if miner_id in self.miners:
            self.miners.remove(miner_id)
            self.pool_hash_rate -= hash_rate
            print(f"   👷 Miner {miner_id} left pool")
    
    def distribute_rewards(self, block_reward: float, miner_contributions: Dict[str, float]) -> Dict[str, float]:
        """Distribute mining rewards among pool members"""
        pool_fee = block_reward * (self.fee_percentage / 100)
        distributable_reward = block_reward - pool_fee
        
        total_contribution = sum(miner_contributions.values())
        if total_contribution == 0:
            return {}
        
        distributions = {}
        for miner_id, contribution in miner_contributions.items():
            share = (contribution / total_contribution) * distributable_reward
            distributions[miner_id] = share
        
        self.total_rewards += block_reward
        self.blocks_mined += 1
        
        return distributions

class PoWMiner:
    """
    Proof of Work Miner - Mumbai gold trader style!
    """
    
    def __init__(self, miner_id: str, hash_rate: float):
        self.miner_id = miner_id
        self.hash_rate = hash_rate  # Hashes per second
        self.is_mining = False
        self.current_block = None
        
        # Mining pool
        self.mining_pool: Optional[MiningPool] = None
        
        # Performance statistics
        self.blocks_mined = 0
        self.total_hash_attempts = 0
        self.mining_start_time = 0.0
        self.earnings = 0.0
        
        # Mumbai characteristics
        self.electricity_cost = 0.05  # Cost per hash (Mumbai power rates)
        self.hardware_efficiency = random.uniform(0.8, 0.95)
        
        print(f"⛏️ Miner {miner_id} initialized (hash rate: {hash_rate} H/s)")
    
    def join_mining_pool(self, pool: MiningPool):
        """Join a mining pool"""
        self.mining_pool = pool
        pool.add_miner(self.miner_id, self.hash_rate)
        print(f"   {self.miner_id} joined mining pool: {pool.pool_name}")
    
    def leave_mining_pool(self):
        """Leave current mining pool"""
        if self.mining_pool:
            self.mining_pool.remove_miner(self.miner_id, self.hash_rate)
            print(f"   {self.miner_id} left mining pool: {self.mining_pool.pool_name}")
            self.mining_pool = None
    
    def mine_block(self, block: Block, max_time: float = 60.0) -> Tuple[bool, Block]:
        """
        Mine a block using Proof of Work - Mumbai gold mining style!
        """
        print(f"⛏️ {self.miner_id} started mining block {block.block_number}")
        
        self.is_mining = True
        self.current_block = block
        self.mining_start_time = time.time()
        
        # Calculate target hash
        target = "0" * block.difficulty
        
        start_nonce = 0
        hash_attempts = 0
        
        while self.is_mining and (time.time() - self.mining_start_time) < max_time:
            # Try different nonce values
            block.nonce = start_nonce + hash_attempts
            block.timestamp = time.time()  # Update timestamp
            
            # Calculate hash
            block.block_hash = block.calculate_hash()
            hash_attempts += 1
            
            # Check if we found a valid proof of work
            if block.block_hash.startswith(target):
                mining_duration = time.time() - self.mining_start_time
                actual_hash_rate = hash_attempts / max(0.001, mining_duration)
                
                block.mining_duration = mining_duration
                block.hash_rate = actual_hash_rate
                block.status = BlockStatus.MINED
                
                self.blocks_mined += 1
                self.total_hash_attempts += hash_attempts
                
                print(f"✅ {self.miner_id} successfully mined block {block.block_number}!")
                print(f"   Nonce: {block.nonce}")
                print(f"   Hash: {block.block_hash}")
                print(f"   Time: {mining_duration:.2f}s")
                print(f"   Hash Rate: {actual_hash_rate:.2f} H/s")
                
                self.is_mining = False
                return True, block
            
            # Simulate hash rate limitation
            time.sleep(1.0 / self.hash_rate)
        
        # Mining timeout or stopped
        self.is_mining = False
        print(f"⏰ {self.miner_id} mining timeout for block {block.block_number}")
        return False, block
    
    def estimate_mining_profitability(self, block: Block, network_hash_rate: float) -> Dict:
        """
        Estimate mining profitability - Mumbai business calculation
        """
        block_reward = block.get_block_reward()
        
        # Calculate probability of mining this block
        if network_hash_rate == 0:
            mining_probability = 1.0
        else:
            mining_probability = self.hash_rate / network_hash_rate
        
        # Estimate time to mine
        expected_time = (2 ** block.difficulty) / self.hash_rate
        
        # Calculate costs
        electricity_cost = expected_time * self.hash_rate * self.electricity_cost
        
        # Expected profit
        expected_reward = block_reward * mining_probability
        expected_profit = expected_reward - electricity_cost
        
        return {
            "block_reward": block_reward,
            "mining_probability": mining_probability,
            "expected_time_seconds": expected_time,
            "electricity_cost": electricity_cost,
            "expected_reward": expected_reward,
            "expected_profit": expected_profit,
            "roi_percentage": (expected_profit / electricity_cost * 100) if electricity_cost > 0 else 0
        }
    
    def get_miner_stats(self) -> Dict:
        """Get miner performance statistics"""
        total_time = time.time() - self.mining_start_time if self.mining_start_time > 0 else 0
        avg_hash_rate = self.total_hash_attempts / max(0.001, total_time)
        
        return {
            "miner_id": self.miner_id,
            "declared_hash_rate": self.hash_rate,
            "actual_avg_hash_rate": avg_hash_rate,
            "blocks_mined": self.blocks_mined,
            "total_hash_attempts": self.total_hash_attempts,
            "earnings": self.earnings,
            "mining_pool": self.mining_pool.pool_name if self.mining_pool else "Solo",
            "hardware_efficiency": self.hardware_efficiency,
            "is_currently_mining": self.is_mining
        }

class PoWBlockchain:
    """
    Proof of Work Blockchain - Mumbai ledger system!
    """
    
    def __init__(self, initial_difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.miners: List[PoWMiner] = []
        self.mining_pools: List[MiningPool] = []
        
        # Network parameters
        self.current_difficulty = initial_difficulty
        self.target_block_time = 10.0  # Target 10 seconds per block
        self.difficulty_adjustment_interval = 10  # Adjust every 10 blocks
        self.max_transactions_per_block = 100
        
        # Network statistics
        self.total_network_hash_rate = 0.0
        self.blocks_orphaned = 0
        
        print("⛓️ PoW Blockchain initialized")
        print(f"   Initial difficulty: {initial_difficulty}")
        print(f"   Target block time: {self.target_block_time}s")
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block - Mumbai foundation stone"""
        genesis_transactions = [
            Transaction(
                tx_id="genesis_tx",
                sender="genesis",
                receiver="network",
                amount=0.0,
                fee=0.0
            )
        ]
        
        genesis_block = Block(
            block_number=0,
            previous_hash="0" * 64,
            merkle_root="genesis_merkle",
            timestamp=time.time(),
            difficulty=0,  # Genesis block has no difficulty
            nonce=0,
            miner_id="genesis_miner",
            transactions=genesis_transactions
        )
        
        genesis_block.status = BlockStatus.CONFIRMED
        self.chain.append(genesis_block)
        
        print("🧱 Genesis block created")
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add transaction to pending pool"""
        if not transaction.is_valid():
            print(f"❌ Invalid transaction: {transaction.tx_id}")
            return False
        
        self.pending_transactions.append(transaction)
        print(f"📝 Transaction added: {transaction.tx_id} ({transaction.amount} coins)")
        return True
    
    def create_mining_block(self, miner_id: str) -> Block:
        """Create a new block for mining"""
        if not self.chain:
            raise Exception("No genesis block found")
        
        last_block = self.chain[-1]
        
        # Select transactions for this block
        selected_transactions = self.pending_transactions[:self.max_transactions_per_block]
        
        # Create coinbase transaction (mining reward)
        coinbase_tx = Transaction(
            tx_id=f"coinbase_{len(self.chain)}",
            sender="network",
            receiver=miner_id,
            amount=50.0,  # Base mining reward
            fee=0.0
        )
        
        all_transactions = [coinbase_tx] + selected_transactions
        
        new_block = Block(
            block_number=len(self.chain),
            previous_hash=last_block.block_hash,
            merkle_root="",  # Will be calculated
            timestamp=time.time(),
            difficulty=self.current_difficulty,
            nonce=0,
            miner_id=miner_id,
            transactions=all_transactions
        )
        
        # Calculate merkle root
        new_block.merkle_root = new_block.calculate_merkle_root()
        
        return new_block
    
    def add_miner(self, miner: PoWMiner):
        """Add miner to network"""
        self.miners.append(miner)
        self.total_network_hash_rate += miner.hash_rate
        print(f"👷 Miner {miner.miner_id} added to network")
    
    def add_mining_pool(self, pool: MiningPool):
        """Add mining pool to network"""
        self.mining_pools.append(pool)
        print(f"🏊 Mining pool {pool.pool_name} added to network")
    
    def validate_block(self, block: Block) -> bool:
        """Validate a mined block"""
        # Check proof of work
        if not block.is_valid_proof_of_work():
            print(f"❌ Block {block.block_number} failed PoW validation")
            return False
        
        # Check previous hash
        if len(self.chain) > 0:
            last_block = self.chain[-1]
            if block.previous_hash != last_block.block_hash:
                print(f"❌ Block {block.block_number} has invalid previous hash")
                return False
        
        # Validate transactions
        for tx in block.transactions:
            if not tx.is_valid():
                print(f"❌ Block {block.block_number} contains invalid transaction: {tx.tx_id}")
                return False
        
        # Check merkle root
        calculated_merkle = block.calculate_merkle_root()
        if block.merkle_root != calculated_merkle:
            print(f"❌ Block {block.block_number} has invalid merkle root")
            return False
        
        return True
    
    def add_block(self, block: Block) -> bool:
        """Add a valid block to the chain"""
        if not self.validate_block(block):
            return False
        
        # Remove transactions that are now confirmed
        confirmed_tx_ids = {tx.tx_id for tx in block.transactions if tx.sender != "network"}
        self.pending_transactions = [
            tx for tx in self.pending_transactions 
            if tx.tx_id not in confirmed_tx_ids
        ]
        
        block.status = BlockStatus.CONFIRMED
        self.chain.append(block)
        
        print(f"✅ Block {block.block_number} added to chain")
        print(f"   Hash: {block.block_hash}")
        print(f"   Transactions: {len(block.transactions)}")
        print(f"   Mined by: {block.miner_id}")
        
        # Adjust difficulty if needed
        if len(self.chain) % self.difficulty_adjustment_interval == 0:
            self.adjust_difficulty()
        
        return True
    
    def adjust_difficulty(self):
        """Adjust mining difficulty - Mumbai traffic adaptation"""
        if len(self.chain) < self.difficulty_adjustment_interval:
            return
        
        # Calculate actual time for last N blocks
        recent_blocks = self.chain[-self.difficulty_adjustment_interval:]
        time_span = recent_blocks[-1].timestamp - recent_blocks[0].timestamp
        expected_time = self.target_block_time * self.difficulty_adjustment_interval
        
        # Adjust difficulty
        time_ratio = expected_time / max(0.1, time_span)
        
        if time_ratio > 1.25:  # Blocks coming too slow
            self.current_difficulty = max(1, self.current_difficulty - 1)
            print(f"📉 Difficulty decreased to {self.current_difficulty}")
        elif time_ratio < 0.8:  # Blocks coming too fast
            self.current_difficulty += 1
            print(f"📈 Difficulty increased to {self.current_difficulty}")
        else:
            print(f"⚖️ Difficulty remains at {self.current_difficulty}")
    
    def simulate_mining_competition(self, duration_seconds: float = 300) -> List[Dict]:
        """
        Simulate mining competition - Mumbai gold rush!
        """
        print(f"\n⛏️ MINING COMPETITION STARTED")
        print(f"Duration: {duration_seconds}s")
        print("=" * 50)
        
        start_time = time.time()
        mining_results = []
        
        # Create some sample transactions
        for i in range(20):
            tx = Transaction(
                tx_id=f"tx_{i:03d}",
                sender=f"user_{i % 5}",
                receiver=f"user_{(i + 1) % 5}",
                amount=random.uniform(1.0, 100.0),
                fee=random.uniform(0.01, 1.0)
            )
            self.add_transaction(tx)
        
        while time.time() - start_time < duration_seconds:
            # Each miner attempts to mine
            mining_threads = []
            mining_results_round = []
            
            def mine_block_async(miner: PoWMiner):
                block = self.create_mining_block(miner.miner_id)
                success, mined_block = miner.mine_block(block, max_time=30.0)
                
                if success:
                    mining_results_round.append((miner, mined_block))
            
            # Start mining for all miners
            for miner in self.miners:
                if not miner.is_mining:  # Only start if not already mining
                    thread = threading.Thread(target=mine_block_async, args=(miner,))
                    mining_threads.append(thread)
                    thread.start()
            
            # Wait for first successful mining
            while mining_threads and not mining_results_round:
                time.sleep(0.1)
                # Remove completed threads
                mining_threads = [t for t in mining_threads if t.is_alive()]
            
            # Stop all other miners
            for miner in self.miners:
                miner.is_mining = False
            
            # Wait for all threads to complete
            for thread in mining_threads:
                thread.join()
            
            # Add first successful block
            if mining_results_round:
                winner_miner, winning_block = mining_results_round[0]
                
                if self.add_block(winning_block):
                    # Calculate and distribute rewards
                    block_reward = winning_block.get_block_reward()
                    
                    if winner_miner.mining_pool:
                        # Pool mining - distribute rewards
                        contributions = {winner_miner.miner_id: 1.0}  # Simplified contribution
                        distributions = winner_miner.mining_pool.distribute_rewards(
                            block_reward, contributions
                        )
                        winner_miner.earnings += distributions.get(winner_miner.miner_id, 0)
                    else:
                        # Solo mining - full reward
                        winner_miner.earnings += block_reward
                    
                    mining_results.append({
                        "block_number": winning_block.block_number,
                        "miner": winner_miner.miner_id,
                        "mining_pool": winner_miner.mining_pool.pool_name if winner_miner.mining_pool else "Solo",
                        "mining_time": winning_block.mining_duration,
                        "hash_rate": winning_block.hash_rate,
                        "difficulty": winning_block.difficulty,
                        "reward": block_reward,
                        "timestamp": winning_block.timestamp
                    })
            
            # Brief pause before next round
            time.sleep(1.0)
        
        return mining_results
    
    def get_blockchain_stats(self) -> Dict:
        """Get comprehensive blockchain statistics"""
        if not self.chain:
            return {"error": "No blocks in chain"}
        
        total_transactions = sum(len(block.transactions) for block in self.chain)
        total_mining_time = sum(
            block.mining_duration for block in self.chain 
            if hasattr(block, 'mining_duration')
        )
        
        return {
            "total_blocks": len(self.chain),
            "current_difficulty": self.current_difficulty,
            "total_transactions": total_transactions,
            "pending_transactions": len(self.pending_transactions),
            "total_miners": len(self.miners),
            "total_mining_pools": len(self.mining_pools),
            "network_hash_rate": self.total_network_hash_rate,
            "average_block_time": total_mining_time / max(1, len(self.chain) - 1),
            "blocks_orphaned": self.blocks_orphaned,
            "chain_length": len(self.chain)
        }

def create_mumbai_mining_ecosystem():
    """
    Create Mumbai-style mining ecosystem
    """
    print("🏗️ CREATING MUMBAI MINING ECOSYSTEM")
    print("=" * 50)
    
    # Initialize blockchain
    blockchain = PoWBlockchain(initial_difficulty=3)
    
    # Create mining pools (Mumbai style names)
    pools = [
        MiningPool("Zaveri_Bazaar_Pool"),
        MiningPool("Crawford_Market_Pool"), 
        MiningPool("Dharavi_Cooperative_Pool")
    ]
    
    for pool in pools:
        blockchain.add_mining_pool(pool)
    
    # Create miners with Mumbai characteristics
    mumbai_miners = [
        ("Kiran_Jeweller", 15.0),      # High-end jeweller
        ("Ramesh_Trader", 12.0),       # Gold trader
        ("Suresh_Cooperative", 8.0),   # Cooperative member
        ("Priya_Tech", 20.0),          # Tech-savvy miner
        ("Arjun_Solo", 5.0),           # Solo miner
        ("Deepika_Pool", 18.0),        # Pool organizer
    ]
    
    miners = []
    for name, hash_rate in mumbai_miners:
        miner = PoWMiner(name, hash_rate)
        miners.append(miner)
        blockchain.add_miner(miner)
    
    # Assign some miners to pools
    miners[0].join_mining_pool(pools[0])  # Kiran to Zaveri Bazaar
    miners[1].join_mining_pool(pools[0])  # Ramesh to Zaveri Bazaar
    miners[2].join_mining_pool(pools[2])  # Suresh to Dharavi Cooperative
    miners[5].join_mining_pool(pools[1])  # Deepika to Crawford Market
    
    # Keep Priya and Arjun as solo miners
    
    return blockchain, miners, pools

if __name__ == "__main__":
    print("🚀 BLOCKCHAIN PROOF OF WORK CONSENSUS")
    print("Mumbai Gold Market Mining Simulation")
    print("=" * 70)
    
    try:
        # Create Mumbai mining ecosystem
        blockchain, miners, pools = create_mumbai_mining_ecosystem()
        
        # Show initial profitability estimates
        print(f"\n📊 MINING PROFITABILITY ANALYSIS")
        print("-" * 40)
        
        sample_block = blockchain.create_mining_block("test_miner")
        for miner in miners[:3]:  # Show for first 3 miners
            profitability = miner.estimate_mining_profitability(
                sample_block, blockchain.total_network_hash_rate
            )
            print(f"{miner.miner_id}:")
            print(f"   Expected profit: ₹{profitability['expected_profit']:.2f}")
            print(f"   ROI: {profitability['roi_percentage']:.1f}%")
            print(f"   Mining probability: {profitability['mining_probability']*100:.2f}%")
        
        # Simulate mining competition
        mining_results = blockchain.simulate_mining_competition(duration_seconds=120)
        
        # Show results
        print(f"\n🏆 MINING COMPETITION RESULTS")
        print("=" * 50)
        
        if mining_results:
            for result in mining_results:
                print(f"Block {result['block_number']}: {result['miner']} "
                      f"({result['mining_pool']}) - {result['mining_time']:.2f}s")
            
            # Winner statistics
            winner_stats = Counter(result['miner'] for result in mining_results)
            print(f"\n🥇 TOP MINERS:")
            for miner, wins in winner_stats.most_common(3):
                print(f"   {miner}: {wins} blocks")
        
        # Final blockchain stats
        stats = blockchain.get_blockchain_stats()
        
        print(f"\n📈 FINAL BLOCKCHAIN STATISTICS")
        print("=" * 40)
        print(f"Total blocks: {stats['total_blocks']}")
        print(f"Final difficulty: {stats['current_difficulty']}")
        print(f"Network hash rate: {stats['network_hash_rate']:.2f} H/s")
        print(f"Average block time: {stats['average_block_time']:.2f}s")
        print(f"Total transactions: {stats['total_transactions']}")
        
        # Miner performance
        print(f"\n👷 MINER PERFORMANCE")
        print("-" * 30)
        for miner in miners:
            miner_stats = miner.get_miner_stats()
            print(f"{miner_stats['miner_id']}: "
                  f"{miner_stats['blocks_mined']} blocks, "
                  f"₹{miner_stats['earnings']:.2f} earned")
        
        print("\n🎯 Key Insights:")
        print("• PoW provides security through computational work")
        print("• Mining pools share risks and rewards")
        print("• Difficulty adjusts to maintain block time")
        print("• Like Mumbai gold market - trust through verification!")
        
        print("\n🎊 BLOCKCHAIN PoW SIMULATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error in PoW simulation: {e}")
        raise