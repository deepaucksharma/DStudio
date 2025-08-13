"""
Eventual Consistency Demo
Simulating distributed systems like Facebook, WhatsApp Messages
Example: Social media post propagation across data centers
"""

import asyncio
import time
import uuid
import random
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')

class NodeStatus(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE" 
    SLOW = "SLOW"

@dataclass
class Post:
    post_id: str
    user_id: str
    content: str
    timestamp: float
    likes: int = 0
    version: int = 1

@dataclass
class DataCenter:
    """
    WhatsApp jaisa data center - har region mein ek
    """
    name: str
    region: str
    posts: Dict[str, Post] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.ONLINE
    network_delay: float = 0.1  # Network latency in seconds
    
class EventualConsistencySystem:
    """
    WhatsApp/Facebook jaisa distributed system
    Messages/Posts eventually sabhi data centers mein sync ho jaate hain
    """
    
    def __init__(self):
        self.data_centers: Dict[str, DataCenter] = {}
        self.message_queue: List[Dict] = []
        self.sync_interval = 2.0  # Sync every 2 seconds
        self.running = False
        
        # Initialize data centers - Real WhatsApp locations
        self._setup_data_centers()
        
    def _setup_data_centers(self):
        """
        Global data centers setup - WhatsApp actual locations
        """
        centers = [
            ("mumbai-dc", "India", 0.05),      # Local DC - fast
            ("singapore-dc", "APAC", 0.15),    # Regional - medium
            ("ireland-dc", "Europe", 0.25),    # International - slow
            ("california-dc", "US", 0.30),     # US West - slowest
            ("sao-paulo-dc", "LATAM", 0.35)    # South America
        ]
        
        for name, region, delay in centers:
            self.data_centers[name] = DataCenter(name, region, network_delay=delay)
            logging.info(f"Data center {name} initialized in {region}")
            
    async def start_background_sync(self):
        """
        Background process - continuous sync between data centers
        WhatsApp jaisa message propagation
        """
        self.running = True
        while self.running:
            await self._sync_all_datacenters()
            await asyncio.sleep(self.sync_interval)
            
    async def stop_sync(self):
        """
        Graceful shutdown
        """
        self.running = False
        
    async def create_post(self, user_id: str, content: str, origin_dc: str = "mumbai-dc") -> str:
        """
        Naya post create karo - Instagram/Facebook jaisa
        Pehle local DC mein store hoga, baad mein propagate hoga
        """
        post_id = str(uuid.uuid4())[:8]
        post = Post(
            post_id=post_id,
            user_id=user_id,
            content=content,
            timestamp=time.time()
        )
        
        # Store in origin data center first
        if origin_dc in self.data_centers:
            dc = self.data_centers[origin_dc]
            dc.posts[post_id] = post
            
            logging.info(f"Post created: {post_id} by {user_id} in {origin_dc}")
            
            # Add to sync queue for other data centers
            self._queue_sync_message({
                "type": "CREATE_POST",
                "post": post,
                "origin": origin_dc,
                "timestamp": time.time()
            })
            
        return post_id
        
    async def like_post(self, post_id: str, user_id: str, dc_name: str = "mumbai-dc") -> bool:
        """
        Post ko like karo - eventually sabhi DCs mein sync hoga
        Instagram jaisa instant feel, backend mein eventual consistency
        """
        dc = self.data_centers.get(dc_name)
        if not dc or post_id not in dc.posts:
            logging.warning(f"Post {post_id} not found in {dc_name}")
            return False
            
        # Local like increment - instant feedback user ko
        post = dc.posts[post_id]
        post.likes += 1
        post.version += 1
        
        logging.info(f"Post {post_id} liked by {user_id} in {dc_name} (likes: {post.likes})")
        
        # Queue for eventual sync
        self._queue_sync_message({
            "type": "LIKE_POST", 
            "post_id": post_id,
            "likes": post.likes,
            "version": post.version,
            "origin": dc_name,
            "timestamp": time.time()
        })
        
        return True
        
    def get_post(self, post_id: str, dc_name: str = "mumbai-dc") -> Optional[Post]:
        """
        Post retrieve karo - local DC se milega (eventual consistency)
        """
        dc = self.data_centers.get(dc_name)
        return dc.posts.get(post_id) if dc else None
        
    def _queue_sync_message(self, message: Dict):
        """
        Message queue mein dal do - async processing ke liye
        """
        self.message_queue.append(message)
        
    async def _sync_all_datacenters(self):
        """
        Sabhi pending messages ko process karo
        WhatsApp jaisa message delivery between servers
        """
        if not self.message_queue:
            return
            
        messages_to_process = self.message_queue.copy()
        self.message_queue.clear()
        
        for message in messages_to_process:
            await self._process_sync_message(message)
            
    async def _process_sync_message(self, message: Dict):
        """
        Individual message ko sabhi DCs mein sync karo
        Network delays and failures simulate karte hain
        """
        origin_dc = message.get("origin")
        
        for dc_name, dc in self.data_centers.items():
            if dc_name == origin_dc:
                continue  # Origin DC mein already hai
                
            # Simulate network delay
            await asyncio.sleep(dc.network_delay)
            
            # Simulate network failures (2% chance)
            if random.random() < 0.02:
                logging.warning(f"Network failure: Message not delivered to {dc_name}")
                # Re-queue for retry
                self.message_queue.append(message)
                continue
                
            # Process message based on type
            try:
                if message["type"] == "CREATE_POST":
                    await self._sync_create_post(dc, message)
                elif message["type"] == "LIKE_POST":
                    await self._sync_like_post(dc, message)
                    
            except Exception as e:
                logging.error(f"Sync error to {dc_name}: {str(e)}")
                
    async def _sync_create_post(self, dc: DataCenter, message: Dict):
        """
        Post creation sync - eventually consistent
        """
        post = message["post"]
        if post.post_id not in dc.posts:
            dc.posts[post.post_id] = post
            logging.info(f"Post {post.post_id} synced to {dc.name}")
            
    async def _sync_like_post(self, dc: DataCenter, message: Dict):
        """
        Like count sync with conflict resolution
        Version vector approach for handling conflicts
        """
        post_id = message["post_id"]
        new_likes = message["likes"]
        new_version = message["version"]
        
        if post_id in dc.posts:
            current_post = dc.posts[post_id]
            
            # Simple conflict resolution: higher version wins
            if new_version > current_post.version:
                current_post.likes = new_likes
                current_post.version = new_version
                logging.info(f"Likes synced for {post_id} in {dc.name}: {new_likes}")
            elif new_version == current_post.version and new_likes != current_post.likes:
                # Conflict detected - merge likes (simple addition)
                current_post.likes = max(current_post.likes, new_likes)
                current_post.version += 1
                logging.warning(f"Conflict resolved for {post_id} in {dc.name}")
                
    def get_system_state(self) -> Dict:
        """
        Poore system ka state dekho - debugging ke liye
        """
        state = {}
        for dc_name, dc in self.data_centers.items():
            state[dc_name] = {
                "region": dc.region,
                "post_count": len(dc.posts),
                "posts": {pid: {"likes": post.likes, "version": post.version} 
                         for pid, post in dc.posts.items()}
            }
        return state
        
    def simulate_network_partition(self, dc_name: str, duration: float = 5.0):
        """
        Network partition simulate karo - real world scenario
        Mumbai mein cable cut ho gaya type situation
        """
        dc = self.data_centers.get(dc_name)
        if dc:
            dc.status = NodeStatus.OFFLINE
            logging.warning(f"Network partition: {dc_name} offline for {duration}s")
            
            async def restore_connection():
                await asyncio.sleep(duration)
                dc.status = NodeStatus.ONLINE
                logging.info(f"Network restored: {dc_name} back online")
                
            asyncio.create_task(restore_connection())

async def demonstrate_eventual_consistency():
    """
    Real-world demo: Social media post propagation
    WhatsApp/Instagram jaisa behavior
    """
    print("=== Eventual Consistency Demo: Social Media System ===")
    
    system = EventualConsistencySystem()
    
    # Start background sync
    sync_task = asyncio.create_task(system.start_background_sync())
    
    try:
        # Create posts from different users - Mumbai se
        print("\n=== Creating Posts ===")
        post1 = await system.create_post("rahul_mumbai", "Mumbai mein baarish aa gayi! 🌧️", "mumbai-dc")
        post2 = await system.create_post("priya_delhi", "Delhi traffic is crazy today!", "mumbai-dc")
        post3 = await system.create_post("vikram_blr", "Bangalore weather is perfect ☀️", "mumbai-dc")
        
        # Wait for initial sync
        await asyncio.sleep(3)
        
        print("\n=== System State After Initial Sync ===")
        state = system.get_system_state()
        for dc, info in state.items():
            print(f"{dc}: {info['post_count']} posts")
            
        # Simulate likes from different regions
        print("\n=== Liking Posts from Different Regions ===")
        
        # Mumbai users like posts
        await system.like_post(post1, "user1", "mumbai-dc")
        await system.like_post(post1, "user2", "mumbai-dc")
        
        # Singapore users like posts
        await system.like_post(post1, "sg_user1", "singapore-dc") 
        await system.like_post(post2, "sg_user2", "singapore-dc")
        
        # US users like posts
        await system.like_post(post3, "us_user1", "california-dc")
        await system.like_post(post3, "us_user2", "california-dc")
        
        # Wait for sync
        await asyncio.sleep(4)
        
        print("\n=== Like Counts After Sync ===")
        for dc_name in ["mumbai-dc", "singapore-dc", "california-dc"]:
            post = system.get_post(post1, dc_name)
            if post:
                print(f"{dc_name}: Post1 has {post.likes} likes (version: {post.version})")
                
        # Simulate network partition
        print("\n=== Simulating Network Partition ===")
        system.simulate_network_partition("singapore-dc", 3.0)
        
        # Continue liking during partition
        await system.like_post(post1, "mumbai_user3", "mumbai-dc")
        await system.like_post(post1, "sg_user3", "singapore-dc")  # This might fail
        
        # Wait for partition to heal and sync
        await asyncio.sleep(6)
        
        print("\n=== Final State After Partition Healing ===")
        state = system.get_system_state()
        for dc, info in state.items():
            print(f"\n{dc} ({info['region']}):")
            for post_id, post_info in info['posts'].items():
                print(f"  Post {post_id}: {post_info['likes']} likes (v{post_info['version']})")
                
    finally:
        await system.stop_sync()
        sync_task.cancel()
        
        try:
            await sync_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(demonstrate_eventual_consistency())