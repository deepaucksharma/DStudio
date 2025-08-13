#!/usr/bin/env python3
"""
Write-Behind (Write-Back) Cache Pattern Implementation
E-commerce analytics और user behavior tracking के लिए async write-behind caching

Key Features:
- Write-behind cache pattern (async writes)
- High write throughput
- Batch database operations
- User analytics data collection
- Event streaming architecture
- Mumbai e-commerce behavior tracking

Use Cases:
- Flipkart user activity tracking
- Product view analytics
- Cart abandonment analysis
- Real-time recommendation data
- A/B testing metrics

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 25 - Caching Strategies (Write-Behind Pattern)
"""

import asyncio
import sqlite3
import redis
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Deque
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserActivity:
    """User activity event"""
    activity_id: str
    user_id: str
    session_id: str
    activity_type: str  # PAGE_VIEW, PRODUCT_VIEW, ADD_TO_CART, SEARCH, etc.
    timestamp: str
    page_url: str
    product_id: Optional[str] = None
    search_query: Optional[str] = None
    device_type: str = "web"
    location: str = "mumbai"
    user_agent: str = ""
    referrer: str = ""
    metadata: Dict[str, Any] = None

@dataclass
class ProductAnalytics:
    """Product analytics data"""
    product_id: str
    total_views: int = 0
    unique_views: int = 0
    cart_additions: int = 0
    purchases: int = 0
    last_viewed: str = ""
    trending_score: float = 0.0
    category: str = ""
    price_range: str = ""

@dataclass
class UserProfile:
    """User profile with behavior data"""
    user_id: str
    total_sessions: int = 0
    total_page_views: int = 0
    total_time_spent: int = 0  # seconds
    favorite_categories: List[str] = None
    last_activity: str = ""
    device_preferences: Dict[str, int] = None
    location_history: List[str] = None
    conversion_rate: float = 0.0

class DatabaseManager:
    """
    Database manager for analytics data
    Analytics data के लिए optimized database operations
    """
    
    def __init__(self, db_path: str = "flipkart_analytics.db"):
        self.db_path = db_path
        self.init_database()
        logger.info("📊 Analytics database initialized")
    
    def init_database(self):
        """Initialize analytics tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User activities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    activity_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    page_url TEXT,
                    product_id TEXT,
                    search_query TEXT,
                    device_type TEXT DEFAULT 'web',
                    location TEXT DEFAULT 'mumbai',
                    user_agent TEXT,
                    referrer TEXT,
                    metadata TEXT
                )
            """)
            
            # Product analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_analytics (
                    product_id TEXT PRIMARY KEY,
                    total_views INTEGER DEFAULT 0,
                    unique_views INTEGER DEFAULT 0,
                    cart_additions INTEGER DEFAULT 0,
                    purchases INTEGER DEFAULT 0,
                    last_viewed TEXT,
                    trending_score REAL DEFAULT 0.0,
                    category TEXT,
                    price_range TEXT
                )
            """)
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    total_sessions INTEGER DEFAULT 0,
                    total_page_views INTEGER DEFAULT 0,
                    total_time_spent INTEGER DEFAULT 0,
                    favorite_categories TEXT,
                    last_activity TEXT,
                    device_preferences TEXT,
                    location_history TEXT,
                    conversion_rate REAL DEFAULT 0.0
                )
            """)
            
            # Indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_user ON user_activities(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON user_activities(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_product ON user_activities(product_id)")
            
            conn.commit()
    
    def batch_insert_activities(self, activities: List[UserActivity]) -> bool:
        """Batch insert user activities"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                activity_data = []
                for activity in activities:
                    activity_data.append((
                        activity.activity_id,
                        activity.user_id,
                        activity.session_id,
                        activity.activity_type,
                        activity.timestamp,
                        activity.page_url,
                        activity.product_id,
                        activity.search_query,
                        activity.device_type,
                        activity.location,
                        activity.user_agent,
                        activity.referrer,
                        json.dumps(activity.metadata) if activity.metadata else None
                    ))
                
                cursor.executemany("""
                    INSERT OR REPLACE INTO user_activities 
                    (activity_id, user_id, session_id, activity_type, timestamp, page_url,
                     product_id, search_query, device_type, location, user_agent, referrer, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, activity_data)
                
                conn.commit()
                logger.info(f"📝 Batch inserted {len(activities)} activities")
                return True
                
        except Exception as e:
            logger.error(f"❌ Batch insert failed: {str(e)}")
            return False
    
    def batch_update_product_analytics(self, analytics: List[ProductAnalytics]) -> bool:
        """Batch update product analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                analytics_data = []
                for analytic in analytics:
                    analytics_data.append((
                        analytic.product_id,
                        analytic.total_views,
                        analytic.unique_views,
                        analytic.cart_additions,
                        analytic.purchases,
                        analytic.last_viewed,
                        analytic.trending_score,
                        analytic.category,
                        analytic.price_range
                    ))
                
                cursor.executemany("""
                    INSERT OR REPLACE INTO product_analytics 
                    (product_id, total_views, unique_views, cart_additions, purchases,
                     last_viewed, trending_score, category, price_range)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, analytics_data)
                
                conn.commit()
                logger.info(f"📈 Batch updated {len(analytics)} product analytics")
                return True
                
        except Exception as e:
            logger.error(f"❌ Product analytics update failed: {str(e)}")
            return False
    
    def batch_update_user_profiles(self, profiles: List[UserProfile]) -> bool:
        """Batch update user profiles"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                profile_data = []
                for profile in profiles:
                    profile_data.append((
                        profile.user_id,
                        profile.total_sessions,
                        profile.total_page_views,
                        profile.total_time_spent,
                        json.dumps(profile.favorite_categories) if profile.favorite_categories else None,
                        profile.last_activity,
                        json.dumps(profile.device_preferences) if profile.device_preferences else None,
                        json.dumps(profile.location_history) if profile.location_history else None,
                        profile.conversion_rate
                    ))
                
                cursor.executemany("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, total_sessions, total_page_views, total_time_spent,
                     favorite_categories, last_activity, device_preferences, location_history, conversion_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, profile_data)
                
                conn.commit()
                logger.info(f"👤 Batch updated {len(profiles)} user profiles")
                return True
                
        except Exception as e:
            logger.error(f"❌ User profiles update failed: {str(e)}")
            return False

class WriteBehindCache:
    """
    Write-Behind Cache implementation for analytics
    High-throughput analytics data के लिए async write-behind cache
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=2,  # Use DB 2 for analytics
                decode_responses=True
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis connection established for write-behind cache")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {str(e)}")
            self.redis_available = False
        
        # Write-behind queues
        self.activity_queue = deque()
        self.product_analytics_cache = {}
        self.user_profiles_cache = {}
        
        # Configuration
        self.batch_size = 100
        self.flush_interval = 30  # seconds
        self.max_queue_size = 10000
        
        # Background processing
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.running = True
        
        # Statistics
        self.stats = {
            'total_writes': 0,
            'cache_writes': 0,
            'database_writes': 0,
            'batch_operations': 0,
            'queue_overflows': 0,
            'async_write_time': 0.0
        }
        
        # Start background processes
        self.start_background_processes()
    
    def start_background_processes(self):
        """Start background write processes"""
        # Activity writer
        self.executor.submit(self._activity_writer_loop)
        
        # Analytics aggregator
        self.executor.submit(self._analytics_aggregator_loop)
        
        # User profile updater
        self.executor.submit(self._profile_updater_loop)
        
        logger.info("🔄 Background write processes started")
    
    def track_user_activity(self, activity: UserActivity) -> bool:
        """
        Track user activity (immediate cache write, async DB write)
        User activity को तुरंत cache में store करते हैं, database write बाद में होता है
        """
        self.stats['total_writes'] += 1
        self.stats['cache_writes'] += 1
        
        try:
            # Immediate cache write
            if self.redis_available:
                cache_key = f"activity:{activity.user_id}:{activity.session_id}"
                activity_data = asdict(activity)
                self.redis_client.lpush(cache_key, json.dumps(activity_data))
                self.redis_client.expire(cache_key, 3600)  # 1 hour TTL
            
            # Queue for async database write
            if len(self.activity_queue) < self.max_queue_size:
                self.activity_queue.append(activity)
            else:
                self.stats['queue_overflows'] += 1
                logger.warning("📦 Activity queue overflow - dropping oldest items")
                # Drop oldest items to make room
                for _ in range(50):
                    if self.activity_queue:
                        self.activity_queue.popleft()
                self.activity_queue.append(activity)
            
            # Update real-time analytics in cache
            self._update_realtime_analytics(activity)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Activity tracking failed: {str(e)}")
            return False
    
    def _update_realtime_analytics(self, activity: UserActivity):
        """Update real-time analytics in cache"""
        # Update product analytics
        if activity.product_id:
            if activity.product_id not in self.product_analytics_cache:
                self.product_analytics_cache[activity.product_id] = ProductAnalytics(
                    product_id=activity.product_id
                )
            
            analytics = self.product_analytics_cache[activity.product_id]
            
            if activity.activity_type == "PRODUCT_VIEW":
                analytics.total_views += 1
                analytics.last_viewed = activity.timestamp
            elif activity.activity_type == "ADD_TO_CART":
                analytics.cart_additions += 1
            elif activity.activity_type == "PURCHASE":
                analytics.purchases += 1
            
            # Calculate trending score
            analytics.trending_score = (analytics.total_views * 0.3 + 
                                      analytics.cart_additions * 0.5 + 
                                      analytics.purchases * 0.2)
        
        # Update user profile
        if activity.user_id not in self.user_profiles_cache:
            self.user_profiles_cache[activity.user_id] = UserProfile(
                user_id=activity.user_id,
                device_preferences={},
                favorite_categories=[],
                location_history=[]
            )
        
        profile = self.user_profiles_cache[activity.user_id]
        profile.total_page_views += 1
        profile.last_activity = activity.timestamp
        
        # Update device preferences
        if profile.device_preferences is None:
            profile.device_preferences = {}
        profile.device_preferences[activity.device_type] = profile.device_preferences.get(activity.device_type, 0) + 1
        
        # Update location history
        if profile.location_history is None:
            profile.location_history = []
        if activity.location not in profile.location_history:
            profile.location_history.append(activity.location)
    
    def get_user_activities(self, user_id: str, session_id: str = None, limit: int = 50) -> List[UserActivity]:
        """
        Get user activities (immediate cache read)
        Cache से immediately user activities read करते हैं
        """
        activities = []
        
        try:
            if self.redis_available:
                if session_id:
                    cache_key = f"activity:{user_id}:{session_id}"
                    cached_activities = self.redis_client.lrange(cache_key, 0, limit-1)
                else:
                    # Get from all sessions (simplified)
                    pattern = f"activity:{user_id}:*"
                    keys = self.redis_client.keys(pattern)
                    cached_activities = []
                    for key in keys[:10]:  # Limit to 10 sessions
                        cached_activities.extend(self.redis_client.lrange(key, 0, 10))
                
                for activity_json in cached_activities:
                    try:
                        activity_data = json.loads(activity_json)
                        activity = UserActivity(**activity_data)
                        activities.append(activity)
                    except Exception as e:
                        logger.error(f"Error parsing activity: {str(e)}")
            
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to get user activities: {str(e)}")
            return []
    
    def get_product_analytics(self, product_id: str) -> Optional[ProductAnalytics]:
        """
        Get product analytics (from cache)
        Product analytics को real-time cache से read करते हैं
        """
        try:
            # Try cache first
            if product_id in self.product_analytics_cache:
                return self.product_analytics_cache[product_id]
            
            # If not in cache, try Redis
            if self.redis_available:
                cache_key = f"product_analytics:{product_id}"
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    analytics_data = json.loads(cached_data)
                    return ProductAnalytics(**analytics_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get product analytics: {str(e)}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile (from cache)
        User profile को cache से read करते हैं
        """
        try:
            # Try cache first
            if user_id in self.user_profiles_cache:
                return self.user_profiles_cache[user_id]
            
            # If not in cache, try Redis
            if self.redis_available:
                cache_key = f"user_profile:{user_id}"
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    profile_data = json.loads(cached_data)
                    return UserProfile(**profile_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user profile: {str(e)}")
            return None
    
    def _activity_writer_loop(self):
        """Background loop for writing activities to database"""
        logger.info("📝 Activity writer loop started")
        
        while self.running:
            try:
                if len(self.activity_queue) >= self.batch_size:
                    # Collect batch
                    batch = []
                    for _ in range(min(self.batch_size, len(self.activity_queue))):
                        if self.activity_queue:
                            batch.append(self.activity_queue.popleft())
                    
                    if batch:
                        start_time = time.time()
                        if self.db.batch_insert_activities(batch):
                            self.stats['database_writes'] += len(batch)
                            self.stats['batch_operations'] += 1
                            self.stats['async_write_time'] += time.time() - start_time
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Activity writer error: {str(e)}")
                time.sleep(5)
    
    def _analytics_aggregator_loop(self):
        """Background loop for aggregating product analytics"""
        logger.info("📊 Analytics aggregator loop started")
        
        while self.running:
            try:
                if self.product_analytics_cache:
                    # Get current analytics
                    analytics_batch = list(self.product_analytics_cache.values())
                    
                    if analytics_batch:
                        start_time = time.time()
                        if self.db.batch_update_product_analytics(analytics_batch):
                            self.stats['database_writes'] += len(analytics_batch)
                            self.stats['batch_operations'] += 1
                            self.stats['async_write_time'] += time.time() - start_time
                            
                            # Also store in Redis for fast access
                            if self.redis_available:
                                for analytics in analytics_batch:
                                    cache_key = f"product_analytics:{analytics.product_id}"
                                    self.redis_client.setex(cache_key, 3600, json.dumps(asdict(analytics)))
                
                time.sleep(self.flush_interval)
                
            except Exception as e:
                logger.error(f"❌ Analytics aggregator error: {str(e)}")
                time.sleep(30)
    
    def _profile_updater_loop(self):
        """Background loop for updating user profiles"""
        logger.info("👤 Profile updater loop started")
        
        while self.running:
            try:
                if self.user_profiles_cache:
                    # Get current profiles
                    profiles_batch = list(self.user_profiles_cache.values())
                    
                    if profiles_batch:
                        start_time = time.time()
                        if self.db.batch_update_user_profiles(profiles_batch):
                            self.stats['database_writes'] += len(profiles_batch)
                            self.stats['batch_operations'] += 1
                            self.stats['async_write_time'] += time.time() - start_time
                            
                            # Also store in Redis for fast access
                            if self.redis_available:
                                for profile in profiles_batch:
                                    cache_key = f"user_profile:{profile.user_id}"
                                    profile_dict = asdict(profile)
                                    self.redis_client.setex(cache_key, 3600, json.dumps(profile_dict))
                
                time.sleep(self.flush_interval)
                
            except Exception as e:
                logger.error(f"❌ Profile updater error: {str(e)}")
                time.sleep(30)
    
    def flush_all(self):
        """
        Force flush all pending writes to database
        सभी pending writes को immediately database में flush करते हैं
        """
        logger.info("🔄 Flushing all pending writes...")
        
        try:
            # Flush activities
            if self.activity_queue:
                activities = []
                while self.activity_queue:
                    activities.append(self.activity_queue.popleft())
                
                if activities:
                    self.db.batch_insert_activities(activities)
                    self.stats['database_writes'] += len(activities)
                    logger.info(f"✅ Flushed {len(activities)} activities")
            
            # Flush product analytics
            if self.product_analytics_cache:
                analytics = list(self.product_analytics_cache.values())
                self.db.batch_update_product_analytics(analytics)
                self.stats['database_writes'] += len(analytics)
                logger.info(f"✅ Flushed {len(analytics)} product analytics")
            
            # Flush user profiles
            if self.user_profiles_cache:
                profiles = list(self.user_profiles_cache.values())
                self.db.batch_update_user_profiles(profiles)
                self.stats['database_writes'] += len(profiles)
                logger.info(f"✅ Flushed {len(profiles)} user profiles")
            
            logger.info("🎉 All data flushed successfully")
            
        except Exception as e:
            logger.error(f"❌ Flush failed: {str(e)}")
    
    def get_cache_stats(self) -> Dict:
        """Get comprehensive cache statistics"""
        return {
            'cache_type': 'Write-Behind (Write-Back)',
            'stats': self.stats,
            'queue_size': len(self.activity_queue),
            'max_queue_size': self.max_queue_size,
            'batch_size': self.batch_size,
            'flush_interval': self.flush_interval,
            'products_in_cache': len(self.product_analytics_cache),
            'users_in_cache': len(self.user_profiles_cache),
            'redis_available': self.redis_available,
            'background_processes_running': self.running
        }
    
    def shutdown(self):
        """Graceful shutdown with data flush"""
        logger.info("🛑 Shutting down write-behind cache...")
        self.running = False
        
        # Flush all pending data
        self.flush_all()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ Write-behind cache shutdown completed")

def demo_write_behind_cache():
    """
    Demo write-behind cache with e-commerce analytics
    Flipkart style user behavior tracking demo
    """
    print("📊 Write-Behind Cache Pattern Demo")
    print("🛒 Flipkart User Analytics Simulation")
    print("=" * 60)
    
    # Initialize system
    db_manager = DatabaseManager()
    cache = WriteBehindCache(db_manager)
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down gracefully...")
        cache.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n1. Simulating User Activities")
    print("-" * 35)
    
    # Simulate user activities
    users = ["user_mumbai_001", "user_delhi_002", "user_bangalore_003"]
    products = ["MOBILE_001", "LAPTOP_002", "BOOK_003", "HEADPHONE_004"]
    activities = ["PAGE_VIEW", "PRODUCT_VIEW", "ADD_TO_CART", "SEARCH", "PURCHASE"]
    
    print("📱 Generating user activities...")
    
    for i in range(200):  # Generate 200 activities
        user_id = users[i % len(users)]
        session_id = f"session_{user_id}_{int(time.time())}"
        
        activity = UserActivity(
            activity_id=f"activity_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            session_id=session_id,
            activity_type=activities[i % len(activities)],
            timestamp=datetime.now().isoformat(),
            page_url=f"/products/{products[i % len(products)]}",
            product_id=products[i % len(products)] if i % 3 == 0 else None,
            search_query="smartphone" if activities[i % len(activities)] == "SEARCH" else None,
            device_type="mobile" if i % 3 == 0 else "web",
            location="mumbai" if i % 2 == 0 else "bangalore",
            metadata={"source": "organic", "campaign": "big_billion_day"}
        )
        
        cache.track_user_activity(activity)
        
        if (i + 1) % 50 == 0:
            print(f"   📊 {i + 1} activities tracked")
            time.sleep(0.1)  # Small delay to simulate real traffic
    
    print("\n2. Real-time Analytics Access")
    print("-" * 35)
    
    # Check real-time analytics
    for product_id in products[:3]:
        analytics = cache.get_product_analytics(product_id)
        if analytics:
            print(f"📈 {product_id}: {analytics.total_views} views, {analytics.cart_additions} cart adds")
    
    print("\n3. User Profile Analytics")
    print("-" * 30)
    
    # Check user profiles
    for user_id in users:
        profile = cache.get_user_profile(user_id)
        if profile:
            print(f"👤 {user_id}: {profile.total_page_views} page views")
            print(f"   📱 Devices: {profile.device_preferences}")
    
    print("\n4. Recent User Activities")
    print("-" * 30)
    
    # Check recent activities
    for user_id in users[:2]:
        activities = cache.get_user_activities(user_id, limit=5)
        print(f"\n📋 {user_id} - Last {len(activities)} activities:")
        for activity in activities:
            print(f"   {activity.activity_type} - {activity.page_url}")
    
    print("\n5. Cache Performance Statistics")
    print("-" * 35)
    
    # Wait for some background processing
    print("⏳ Waiting for background processing...")
    time.sleep(5)
    
    stats = cache.get_cache_stats()
    print(f"📊 Cache Type: {stats['cache_type']}")
    print(f"✍️  Total Writes: {stats['stats']['total_writes']}")
    print(f"💾 Cache Writes: {stats['stats']['cache_writes']}")
    print(f"💿 Database Writes: {stats['stats']['database_writes']}")
    print(f"📦 Batch Operations: {stats['stats']['batch_operations']}")
    print(f"📊 Queue Size: {stats['queue_size']}/{stats['max_queue_size']}")
    print(f"🏭 Products in Cache: {stats['products_in_cache']}")
    print(f"👥 Users in Cache: {stats['users_in_cache']}")
    
    if stats['stats']['async_write_time'] > 0:
        avg_write_time = stats['stats']['async_write_time'] / stats['stats']['batch_operations']
        print(f"⚡ Avg Batch Write Time: {avg_write_time:.3f}s")
    
    print("\n6. Manual Flush Test")
    print("-" * 25)
    
    print("🔄 Flushing all pending writes...")
    cache.flush_all()
    
    print("\n" + "=" * 60)
    print("🎉 Write-Behind Cache Demo Completed!")
    print("💡 Key Benefits:")
    print("   - Very high write throughput")
    print("   - Low write latency (immediate cache response)")
    print("   - Efficient batch database operations")
    print("   - Perfect for analytics and logging systems")
    print("   - Async processing doesn't block user experience")
    print("\n⚠️  Important Considerations:")
    print("   - Risk of data loss if cache fails before flush")
    print("   - Eventual consistency (data may not be in DB immediately)")
    print("   - Need proper queue management and monitoring")
    
    # Keep demo running for background processing
    print("\n🔄 Background processes running... Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(10)
            current_stats = cache.get_cache_stats()
            print(f"📊 Queue: {current_stats['queue_size']}, DB Writes: {current_stats['stats']['database_writes']}")
    except KeyboardInterrupt:
        cache.shutdown()

if __name__ == "__main__":
    demo_write_behind_cache()