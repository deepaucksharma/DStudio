#!/usr/bin/env python3
"""
Distributed Hash Table (DHT) Implementation
Distributed Hash Table - जैसे BitTorrent और Blockchain में use होता है

यह example दिखाता है कि कैसे data को multiple nodes पर distribute करते हैं
using consistent hashing. India में Jio, Paytm जैसी companies इसे use करती हैं
large-scale caching और data distribution के लिए।

Production context: Paytm stores 1+ billion wallet transactions using DHT concepts
Scale: Data automatically redistributes when nodes join/leave
Cost benefit: No single point of failure, horizontal scaling possible
"""

import hashlib
import bisect
import json
import threading
import time
import random
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import logging
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """Node status in the DHT ring"""
    ACTIVE = "active"
    JOINING = "joining"
    LEAVING = "leaving"
    FAILED = "failed"

@dataclass
class DHTNode:
    """
    Represents a node in the distributed hash table
    """
    node_id: str
    host: str
    port: int
    hash_value: int
    status: NodeStatus = NodeStatus.ACTIVE
    last_heartbeat: float = 0.0
    data_store: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data_store is None:
            self.data_store = {}
        self.last_heartbeat = time.time()
    
    def __str__(self):
        return f"Node({self.node_id}@{self.host}:{self.port}, hash={self.hash_value})"

class ConsistentHashing:
    """
    Consistent hashing implementation for DHT
    Ring-based data distribution with virtual nodes
    """
    
    def __init__(self, virtual_nodes: int = 3):
        """
        Initialize consistent hashing ring
        
        Args:
            virtual_nodes: Number of virtual nodes per physical node
        """
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}  # hash_value -> node_id
        self.sorted_hashes: List[int] = []
        self.nodes: Dict[str, DHTNode] = {}
        self.lock = threading.RLock()
        
        logger.info(f"Consistent hashing initialized with {virtual_nodes} virtual nodes per physical node")
    
    def _hash(self, key: str) -> int:
        """
        Generate hash value for a key
        """
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: DHTNode) -> List[Tuple[str, str]]:
        """
        Add a node to the hash ring
        
        Returns:
            List of (key, from_node_id) pairs that need to be migrated to this node
        """
        with self.lock:
            self.nodes[node.node_id] = node
            migrations = []
            
            # Add virtual nodes
            for i in range(self.virtual_nodes):
                virtual_key = f"{node.node_id}:{i}"
                hash_value = self._hash(virtual_key)
                
                # Find the node that was previously responsible for this hash
                if self.sorted_hashes:
                    idx = bisect.bisect_right(self.sorted_hashes, hash_value)
                    if idx == len(self.sorted_hashes):
                        prev_node_id = self.ring[self.sorted_hashes[0]]
                    else:
                        prev_node_id = self.ring[self.sorted_hashes[idx]]
                    
                    # Collect keys that need migration
                    prev_node = self.nodes.get(prev_node_id)
                    if prev_node:
                        keys_to_migrate = []
                        for key in list(prev_node.data_store.keys()):
                            if self._hash(key) <= hash_value:
                                keys_to_migrate.append(key)
                        
                        for key in keys_to_migrate:
                            migrations.append((key, prev_node_id))
                
                self.ring[hash_value] = node.node_id
                bisect.insort(self.sorted_hashes, hash_value)
            
            logger.info(f"Added node {node.node_id} to ring, {len(migrations)} keys to migrate")
            return migrations
    
    def remove_node(self, node_id: str) -> List[Tuple[str, Any, str]]:
        """
        Remove a node from the hash ring
        
        Returns:
            List of (key, value, to_node_id) tuples for data migration
        """
        with self.lock:
            if node_id not in self.nodes:
                return []
            
            node = self.nodes[node_id]
            migrations = []
            
            # Remove virtual nodes
            hashes_to_remove = []
            for hash_value, ring_node_id in self.ring.items():
                if ring_node_id == node_id:
                    hashes_to_remove.append(hash_value)
            
            for hash_value in hashes_to_remove:
                del self.ring[hash_value]
                self.sorted_hashes.remove(hash_value)
            
            # Migrate data to successor nodes
            for key, value in node.data_store.items():
                successor_node_id = self.get_node(key)
                if successor_node_id and successor_node_id != node_id:
                    migrations.append((key, value, successor_node_id))
            
            del self.nodes[node_id]
            logger.info(f"Removed node {node_id} from ring, {len(migrations)} keys to migrate")
            return migrations
    
    def get_node(self, key: str) -> Optional[str]:
        """
        Get the node responsible for a key
        """
        with self.lock:
            if not self.sorted_hashes:
                return None
            
            hash_value = self._hash(key)
            idx = bisect.bisect_right(self.sorted_hashes, hash_value)
            
            if idx == len(self.sorted_hashes):
                return self.ring[self.sorted_hashes[0]]
            else:
                return self.ring[self.sorted_hashes[idx]]
    
    def get_replica_nodes(self, key: str, num_replicas: int = 2) -> List[str]:
        """
        Get nodes for storing replicas of a key
        """
        with self.lock:
            if not self.sorted_hashes:
                return []
            
            hash_value = self._hash(key)
            idx = bisect.bisect_right(self.sorted_hashes, hash_value)
            
            replica_nodes = []
            seen_physical_nodes = set()
            
            for i in range(len(self.sorted_hashes)):
                actual_idx = (idx + i) % len(self.sorted_hashes)
                node_id = self.ring[self.sorted_hashes[actual_idx]]
                
                # Only add if we haven't seen this physical node
                if node_id not in seen_physical_nodes:
                    replica_nodes.append(node_id)
                    seen_physical_nodes.add(node_id)
                    
                    if len(replica_nodes) >= num_replicas:
                        break
            
            return replica_nodes

class PaytmWalletDHT:
    """
    Paytm-style wallet system using Distributed Hash Table
    Wallet balance और transaction history को efficiently distribute करता है
    """
    
    def __init__(self, replication_factor: int = 3):
        """
        Initialize Paytm wallet DHT
        
        Args:
            replication_factor: Number of replicas for each data item
        """
        self.consistent_hashing = ConsistentHashing(virtual_nodes=5)
        self.replication_factor = replication_factor
        self.heartbeat_interval = 30.0  # seconds
        self.heartbeat_thread = None
        self.is_running = False
        
        logger.info(f"Paytm Wallet DHT initialized with replication factor {replication_factor}")
    
    def start_cluster(self) -> None:
        """
        Start the DHT cluster with heartbeat monitoring
        """
        self.is_running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.heartbeat_thread.start()
        logger.info("DHT cluster started with heartbeat monitoring")
    
    def stop_cluster(self) -> None:
        """
        Stop the DHT cluster
        """
        self.is_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        logger.info("DHT cluster stopped")
    
    def add_wallet_server(self, server_id: str, host: str, port: int) -> bool:
        """
        Add a new wallet server to the DHT cluster
        """
        try:
            # Create node
            hash_value = int(hashlib.md5(f"{server_id}".encode()).hexdigest(), 16)
            node = DHTNode(
                node_id=server_id,
                host=host,
                port=port,
                hash_value=hash_value,
                status=NodeStatus.JOINING
            )
            
            # Add to ring and handle migrations
            migrations = self.consistent_hashing.add_node(node)
            
            # Simulate data migration
            for key, from_node_id in migrations:
                self._migrate_data(key, from_node_id, server_id)
            
            # Mark as active
            node.status = NodeStatus.ACTIVE
            
            logger.info(f"Added wallet server {server_id} at {host}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add wallet server {server_id}: {e}")
            return False
    
    def remove_wallet_server(self, server_id: str) -> bool:
        """
        Remove a wallet server from the DHT cluster
        """
        try:
            # Mark as leaving
            if server_id in self.consistent_hashing.nodes:
                self.consistent_hashing.nodes[server_id].status = NodeStatus.LEAVING
            
            # Handle data migration
            migrations = self.consistent_hashing.remove_node(server_id)
            
            for key, value, to_node_id in migrations:
                self._store_data_on_node(to_node_id, key, value)
            
            logger.info(f"Removed wallet server {server_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove wallet server {server_id}: {e}")
            return False
    
    def create_wallet(self, user_id: str, initial_balance: float = 0.0) -> bool:
        """
        Create a new wallet for a user
        """
        try:
            wallet_key = f"wallet:{user_id}"
            wallet_data = {
                "user_id": user_id,
                "balance": initial_balance,
                "created_at": time.time(),
                "last_transaction": None,
                "transaction_count": 0
            }
            
            # Store on multiple nodes for replication
            replica_nodes = self.consistent_hashing.get_replica_nodes(wallet_key, self.replication_factor)
            
            success_count = 0
            for node_id in replica_nodes:
                if self._store_data_on_node(node_id, wallet_key, wallet_data):
                    success_count += 1
            
            # Consider successful if majority of replicas are stored
            threshold = (self.replication_factor // 2) + 1
            if success_count >= threshold:
                logger.info(f"Created wallet for user {user_id} with balance ₹{initial_balance}")
                return True
            else:
                logger.error(f"Failed to create wallet for user {user_id}: insufficient replicas")
                return False
                
        except Exception as e:
            logger.error(f"Error creating wallet for user {user_id}: {e}")
            return False
    
    def get_wallet_balance(self, user_id: str) -> Optional[float]:
        """
        Get wallet balance for a user
        """
        try:
            wallet_key = f"wallet:{user_id}"
            replica_nodes = self.consistent_hashing.get_replica_nodes(wallet_key, self.replication_factor)
            
            # Try to read from replicas until we get a successful response
            for node_id in replica_nodes:
                wallet_data = self._get_data_from_node(node_id, wallet_key)
                if wallet_data:
                    return wallet_data.get("balance")
            
            logger.warning(f"Could not retrieve wallet balance for user {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting wallet balance for user {user_id}: {e}")
            return None
    
    def transfer_money(self, from_user: str, to_user: str, amount: float) -> bool:
        """
        Transfer money between wallets
        """
        try:
            # Get current balances
            from_balance = self.get_wallet_balance(from_user)
            to_balance = self.get_wallet_balance(to_user)
            
            if from_balance is None or to_balance is None:
                logger.error(f"Transfer failed: wallet not found")
                return False
            
            if from_balance < amount:
                logger.error(f"Transfer failed: insufficient balance")
                return False
            
            # Update balances (simplified - in production would use distributed transactions)
            from_wallet_key = f"wallet:{from_user}"
            to_wallet_key = f"wallet:{to_user}"
            
            timestamp = time.time()
            
            # Update sender wallet
            from_wallet_data = self._get_data_from_node(
                self.consistent_hashing.get_node(from_wallet_key), 
                from_wallet_key
            )
            from_wallet_data["balance"] -= amount
            from_wallet_data["last_transaction"] = timestamp
            from_wallet_data["transaction_count"] += 1
            
            # Update receiver wallet
            to_wallet_data = self._get_data_from_node(
                self.consistent_hashing.get_node(to_wallet_key), 
                to_wallet_key
            )
            to_wallet_data["balance"] += amount
            to_wallet_data["last_transaction"] = timestamp
            to_wallet_data["transaction_count"] += 1
            
            # Store updated data on replicas
            from_replicas = self.consistent_hashing.get_replica_nodes(from_wallet_key, self.replication_factor)
            to_replicas = self.consistent_hashing.get_replica_nodes(to_wallet_key, self.replication_factor)
            
            success = True
            for node_id in from_replicas:
                if not self._store_data_on_node(node_id, from_wallet_key, from_wallet_data):
                    success = False
            
            for node_id in to_replicas:
                if not self._store_data_on_node(node_id, to_wallet_key, to_wallet_data):
                    success = False
            
            if success:
                logger.info(f"Transfer successful: ₹{amount} from {from_user} to {to_user}")
            else:
                logger.error(f"Transfer partially failed: some replicas not updated")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in money transfer: {e}")
            return False
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """
        Get DHT cluster statistics
        """
        total_nodes = len(self.consistent_hashing.nodes)
        active_nodes = sum(1 for node in self.consistent_hashing.nodes.values() 
                          if node.status == NodeStatus.ACTIVE)
        
        total_data_items = sum(len(node.data_store) for node in self.consistent_hashing.nodes.values())
        
        # Data distribution analysis
        data_distribution = {}
        for node_id, node in self.consistent_hashing.nodes.items():
            data_distribution[node_id] = len(node.data_store)
        
        return {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "total_data_items": total_data_items,
            "average_data_per_node": total_data_items / max(total_nodes, 1),
            "data_distribution": data_distribution,
            "replication_factor": self.replication_factor
        }
    
    def _migrate_data(self, key: str, from_node_id: str, to_node_id: str) -> bool:
        """
        Migrate data between nodes
        """
        try:
            from_node = self.consistent_hashing.nodes.get(from_node_id)
            to_node = self.consistent_hashing.nodes.get(to_node_id)
            
            if not from_node or not to_node:
                return False
            
            if key in from_node.data_store:
                value = from_node.data_store[key]
                to_node.data_store[key] = value
                del from_node.data_store[key]
                logger.debug(f"Migrated key {key} from {from_node_id} to {to_node_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error migrating data: {e}")
            return False
    
    def _store_data_on_node(self, node_id: str, key: str, value: Any) -> bool:
        """
        Store data on a specific node
        """
        try:
            node = self.consistent_hashing.nodes.get(node_id)
            if node and node.status == NodeStatus.ACTIVE:
                node.data_store[key] = value
                return True
            return False
        except Exception as e:
            logger.error(f"Error storing data on node {node_id}: {e}")
            return False
    
    def _get_data_from_node(self, node_id: str, key: str) -> Optional[Any]:
        """
        Get data from a specific node
        """
        try:
            node = self.consistent_hashing.nodes.get(node_id)
            if node and node.status == NodeStatus.ACTIVE:
                return node.data_store.get(key)
            return None
        except Exception as e:
            logger.error(f"Error getting data from node {node_id}: {e}")
            return None
    
    def _heartbeat_monitor(self) -> None:
        """
        Monitor node health using heartbeats
        """
        while self.is_running:
            try:
                current_time = time.time()
                failed_nodes = []
                
                for node_id, node in self.consistent_hashing.nodes.items():
                    # Simulate random heartbeat updates
                    if random.random() > 0.05:  # 95% uptime
                        node.last_heartbeat = current_time
                    
                    # Check for failed nodes
                    if current_time - node.last_heartbeat > self.heartbeat_interval * 2:
                        if node.status == NodeStatus.ACTIVE:
                            logger.warning(f"Node {node_id} failed heartbeat check")
                            node.status = NodeStatus.FAILED
                            failed_nodes.append(node_id)
                
                # Handle failed nodes (would trigger replication/recovery)
                for node_id in failed_nodes:
                    logger.info(f"Initiating recovery for failed node {node_id}")
                    # In production, this would trigger data replication to other nodes
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")

def demonstrate_paytm_wallet_dht():
    """
    Demonstrate DHT-based Paytm wallet system
    """
    print("\n💰 Paytm Wallet DHT System Demo")
    print("=" * 50)
    
    # Initialize DHT cluster
    dht = PaytmWalletDHT(replication_factor=3)
    dht.start_cluster()
    
    try:
        # Add wallet servers (simulating different data centers)
        print("\n🏢 Setting up wallet servers across India...")
        servers = [
            ("mumbai-wallet-01", "10.1.1.10", 8001),
            ("delhi-wallet-01", "10.1.2.10", 8001),
            ("bangalore-wallet-01", "10.1.3.10", 8001),
            ("chennai-wallet-01", "10.1.4.10", 8001),
            ("kolkata-wallet-01", "10.1.5.10", 8001)
        ]
        
        for server_id, host, port in servers:
            dht.add_wallet_server(server_id, host, port)
            print(f"✅ Added {server_id} at {host}:{port}")
        
        # Create sample wallets
        print("\n👤 Creating user wallets...")
        users = [
            ("rahul_mumbai", 5000.0),
            ("priya_delhi", 3000.0),
            ("arjun_bangalore", 7500.0),
            ("sneha_chennai", 2000.0),
            ("amit_kolkata", 4000.0)
        ]
        
        for user_id, initial_balance in users:
            dht.create_wallet(user_id, initial_balance)
            print(f"✅ Created wallet for {user_id} with ₹{initial_balance}")
        
        # Display cluster stats
        print("\n📊 Cluster Statistics:")
        stats = dht.get_cluster_stats()
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Active nodes: {stats['active_nodes']}")
        print(f"Total data items: {stats['total_data_items']}")
        print(f"Average data per node: {stats['average_data_per_node']:.1f}")
        
        print("\nData distribution across nodes:")
        for node_id, data_count in stats['data_distribution'].items():
            print(f"  {node_id}: {data_count} items")
        
        # Demonstrate money transfers
        print("\n💸 Demonstrating money transfers...")
        transfers = [
            ("rahul_mumbai", "priya_delhi", 500.0),
            ("arjun_bangalore", "sneha_chennai", 1000.0),
            ("amit_kolkata", "rahul_mumbai", 300.0)
        ]
        
        for from_user, to_user, amount in transfers:
            print(f"\nTransferring ₹{amount} from {from_user} to {to_user}...")
            
            # Show balances before
            from_balance_before = dht.get_wallet_balance(from_user)
            to_balance_before = dht.get_wallet_balance(to_user)
            print(f"Before: {from_user} = ₹{from_balance_before}, {to_user} = ₹{to_balance_before}")
            
            # Execute transfer
            success = dht.transfer_money(from_user, to_user, amount)
            
            # Show balances after
            if success:
                from_balance_after = dht.get_wallet_balance(from_user)
                to_balance_after = dht.get_wallet_balance(to_user)
                print(f"After:  {from_user} = ₹{from_balance_after}, {to_user} = ₹{to_balance_after}")
                print("✅ Transfer successful")
            else:
                print("❌ Transfer failed")
        
        # Simulate node failure and recovery
        print("\n⚠️  Simulating node failure...")
        failed_node = "mumbai-wallet-01"
        print(f"Removing node: {failed_node}")
        dht.remove_wallet_server(failed_node)
        
        # Check if data is still accessible
        print("\nVerifying data accessibility after node failure...")
        for user_id, _ in users:
            balance = dht.get_wallet_balance(user_id)
            if balance is not None:
                print(f"✅ {user_id}: ₹{balance} (accessible)")
            else:
                print(f"❌ {user_id}: data not accessible")
        
        # Add replacement node
        print(f"\n🔄 Adding replacement node...")
        dht.add_wallet_server("mumbai-wallet-02", "10.1.1.20", 8001)
        print("✅ Replacement node added")
        
        # Final cluster stats
        print("\n📊 Final Cluster Statistics:")
        final_stats = dht.get_cluster_stats()
        print(f"Total nodes: {final_stats['total_nodes']}")
        print(f"Active nodes: {final_stats['active_nodes']}")
        print(f"Total data items: {final_stats['total_data_items']}")
        
        # Production insights
        print(f"\n💡 Production Insights:")
        print(f"- DHT enables horizontal scaling of wallet data across data centers")
        print(f"- Consistent hashing minimizes data movement when nodes join/leave")
        print(f"- Replication factor of 3 provides high availability during failures")
        print(f"- Each user's data automatically distributed based on user_id hash")
        print(f"- Can handle millions of wallets with sub-millisecond lookups")
        print(f"- Cost-effective: scales linearly with hardware addition")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
    finally:
        # Cleanup
        dht.stop_cluster()

if __name__ == "__main__":
    demonstrate_paytm_wallet_dht()