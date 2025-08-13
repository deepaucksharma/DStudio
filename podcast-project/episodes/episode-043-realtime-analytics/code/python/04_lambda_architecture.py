#!/usr/bin/env python3
"""
Lambda Architecture Implementation
Episode 43: Real-time Analytics at Scale

Complete Lambda Architecture for handling both batch and stream processing
Production-grade implementation with fault tolerance and data consistency

Use Case: Flipkart product recommendation system
Batch layer: Historical purchase analysis
Speed layer: Real-time browsing behavior
Serving layer: Combined recommendations
"""

import asyncio
import time
import json
import sqlite3
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import threading
import queue
import logging
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserEvent:
    """User interaction event"""
    user_id: str
    event_type: str  # view, cart_add, purchase, search
    product_id: str
    category: str
    price: float
    timestamp: datetime
    session_id: str
    device_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class ProductRecommendation:
    """Product recommendation"""
    product_id: str
    score: float
    reason: str
    source: str  # batch, stream, or combined

class BatchLayer:
    """
    Batch Layer - Historical data processing
    रोज रात को complete dataset का analysis करता है
    
    Responsibilities:
    1. Historical purchase pattern analysis
    2. User-item collaborative filtering
    3. Product similarity calculation
    4. Seasonal trend analysis
    """
    
    def __init__(self, db_path: str = "flipkart_batch.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize batch processing database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_events (
            user_id TEXT,
            event_type TEXT,
            product_id TEXT,
            category TEXT,
            price REAL,
            timestamp TEXT,
            session_id TEXT,
            device_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Batch recommendations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS batch_recommendations (
            user_id TEXT,
            product_id TEXT,
            score REAL,
            reason TEXT,
            computed_at TEXT,
            PRIMARY KEY (user_id, product_id)
        )
        """)
        
        # Product similarity table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_similarity (
            product_id_1 TEXT,
            product_id_2 TEXT,
            similarity_score REAL,
            computed_at TEXT,
            PRIMARY KEY (product_id_1, product_id_2)
        )
        """)
        
        # User profiles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            preferred_categories TEXT,
            avg_price_range TEXT,
            purchase_frequency REAL,
            last_active TEXT,
            computed_at TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    def store_events(self, events: List[UserEvent]):
        """Store events for batch processing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for event in events:
            cursor.execute("""
            INSERT INTO user_events 
            (user_id, event_type, product_id, category, price, timestamp, session_id, device_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.user_id, event.event_type, event.product_id,
                event.category, event.price, event.timestamp.isoformat(),
                event.session_id, event.device_type
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Stored {len(events)} events for batch processing")
    
    def compute_user_profiles(self):
        """
        Compute comprehensive user profiles from historical data
        User की purchasing behavior analyze करता है
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all users with purchase history
        cursor.execute("""
        SELECT user_id, 
               GROUP_CONCAT(category) as categories,
               AVG(price) as avg_price,
               COUNT(*) as total_events,
               MAX(timestamp) as last_active
        FROM user_events 
        WHERE event_type = 'purchase'
        GROUP BY user_id
        HAVING COUNT(*) >= 3
        """)
        
        users = cursor.fetchall()
        
        for user_data in users:
            user_id, categories_str, avg_price, total_events, last_active = user_data
            
            # Analyze preferred categories
            category_counts = defaultdict(int)
            for category in categories_str.split(','):
                category_counts[category] += 1
            
            preferred_categories = json.dumps(dict(category_counts))
            
            # Price range classification
            if avg_price < 500:
                price_range = "budget"
            elif avg_price < 2000:
                price_range = "mid_range"
            else:
                price_range = "premium"
            
            # Purchase frequency (events per day)
            days_active = (datetime.now() - datetime.fromisoformat(last_active)).days + 1
            frequency = total_events / days_active
            
            # Store user profile
            cursor.execute("""
            INSERT OR REPLACE INTO user_profiles
            (user_id, preferred_categories, avg_price_range, purchase_frequency, last_active, computed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id, preferred_categories, price_range, 
                frequency, last_active, datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Computed profiles for {len(users)} users")
    
    def compute_product_similarity(self):
        """
        Compute product similarity based on user co-purchasing patterns
        "साथ में खरीदे जाने वाले products" find करता है
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get co-purchase data
        cursor.execute("""
        SELECT e1.product_id as product1, e2.product_id as product2, COUNT(*) as co_purchases
        FROM user_events e1
        JOIN user_events e2 ON e1.user_id = e2.user_id 
                             AND e1.session_id = e2.session_id
                             AND e1.product_id != e2.product_id
        WHERE e1.event_type = 'purchase' AND e2.event_type = 'purchase'
        GROUP BY e1.product_id, e2.product_id
        HAVING co_purchases >= 3
        """)
        
        co_purchases = cursor.fetchall()
        
        # Calculate Jaccard similarity
        for product1, product2, co_count in co_purchases:
            # Get individual purchase counts
            cursor.execute("SELECT COUNT(*) FROM user_events WHERE product_id = ? AND event_type = 'purchase'", (product1,))
            count1 = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_events WHERE product_id = ? AND event_type = 'purchase'", (product2,))
            count2 = cursor.fetchone()[0]
            
            # Jaccard similarity = |A ∩ B| / |A ∪ B|
            similarity = co_count / (count1 + count2 - co_count)
            
            cursor.execute("""
            INSERT OR REPLACE INTO product_similarity
            (product_id_1, product_id_2, similarity_score, computed_at)
            VALUES (?, ?, ?, ?)
            """, (product1, product2, similarity, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        logger.info(f"Computed similarity for {len(co_purchases)} product pairs")
    
    def generate_batch_recommendations(self):
        """
        Generate recommendations using batch-computed data
        Historical patterns के based पर recommendations करता है
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear old recommendations
        cursor.execute("DELETE FROM batch_recommendations")
        
        # Get all user profiles
        cursor.execute("SELECT user_id, preferred_categories, avg_price_range FROM user_profiles")
        users = cursor.fetchall()
        
        for user_id, categories_json, price_range in users:
            preferred_categories = json.loads(categories_json)
            recommendations = []
            
            # Get user's purchase history
            cursor.execute("""
            SELECT product_id FROM user_events 
            WHERE user_id = ? AND event_type = 'purchase'
            """, (user_id,))
            purchased_products = {row[0] for row in cursor.fetchall()}
            
            # Collaborative filtering - find similar products
            for purchased_product in purchased_products:
                cursor.execute("""
                SELECT product_id_2, similarity_score 
                FROM product_similarity 
                WHERE product_id_1 = ? 
                ORDER BY similarity_score DESC 
                LIMIT 5
                """, (purchased_product,))
                
                similar_products = cursor.fetchall()
                
                for similar_product, similarity in similar_products:
                    if similar_product not in purchased_products:
                        recommendations.append(ProductRecommendation(
                            product_id=similar_product,
                            score=similarity * 0.8,  # Collaborative filtering weight
                            reason=f"साथ में खरीदा जाता है {purchased_product} के साथ",
                            source="batch"
                        ))
            
            # Content-based filtering - recommend by category preference
            for category, count in preferred_categories.items():
                category_weight = count / sum(preferred_categories.values())
                
                # Find popular products in preferred categories
                cursor.execute("""
                SELECT product_id, COUNT(*) as popularity
                FROM user_events 
                WHERE category = ? AND event_type = 'purchase'
                AND product_id NOT IN ({})
                GROUP BY product_id
                ORDER BY popularity DESC
                LIMIT 3
                """.format(','.join(['?' for _ in purchased_products])), 
                [category] + list(purchased_products))
                
                popular_products = cursor.fetchall()
                
                for product_id, popularity in popular_products:
                    recommendations.append(ProductRecommendation(
                        product_id=product_id,
                        score=category_weight * min(popularity / 100.0, 1.0),
                        reason=f"आपकी पसंदीदा category: {category}",
                        source="batch"
                    ))
            
            # Store top recommendations
            recommendations.sort(key=lambda x: x.score, reverse=True)
            for rec in recommendations[:10]:  # Top 10 recommendations
                cursor.execute("""
                INSERT INTO batch_recommendations
                (user_id, product_id, score, reason, computed_at)
                VALUES (?, ?, ?, ?, ?)
                """, (user_id, rec.product_id, rec.score, rec.reason, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        logger.info(f"Generated batch recommendations for {len(users)} users")
    
    def run_batch_job(self):
        """
        Run complete batch processing job
        Production में यह daily/hourly run होता है
        """
        logger.info("Starting batch processing job...")
        
        start_time = time.time()
        
        # Step 1: Compute user profiles
        self.compute_user_profiles()
        
        # Step 2: Compute product similarities
        self.compute_product_similarity()
        
        # Step 3: Generate recommendations
        self.generate_batch_recommendations()
        
        end_time = time.time()
        logger.info(f"Batch job completed in {end_time - start_time:.2f} seconds")

class SpeedLayer:
    """
    Speed Layer - Real-time stream processing
    User के real-time behavior को track करता है
    
    Responsibilities:
    1. Real-time session tracking
    2. Immediate behavior-based recommendations
    3. Hot product detection
    4. Real-time personalization
    """
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
        except redis.ConnectionError:
            logger.warning("Redis not available, using in-memory storage")
            self.redis_client = None
        
        # In-memory fallback
        self.session_data = defaultdict(list)
        self.hot_products = defaultdict(int)
        self.user_recent_activity = defaultdict(list)
        
        # Real-time recommendation weights
        self.weights = {
            'view': 0.1,
            'cart_add': 0.3,
            'purchase': 1.0,
            'search': 0.05
        }
    
    def process_real_time_event(self, event: UserEvent) -> List[ProductRecommendation]:
        """
        Process real-time event and generate immediate recommendations
        User का current behavior analyze करके instant recommendations देता है
        """
        recommendations = []
        
        # Update session data
        self._update_session_data(event)
        
        # Update hot products
        self._update_hot_products(event)
        
        # Update user's recent activity
        self._update_user_activity(event)
        
        # Generate real-time recommendations
        if event.event_type == 'view':
            recommendations.extend(self._get_view_based_recommendations(event))
        elif event.event_type == 'cart_add':
            recommendations.extend(self._get_cart_based_recommendations(event))
        elif event.event_type == 'search':
            recommendations.extend(self._get_search_based_recommendations(event))
        
        # Add trending products
        recommendations.extend(self._get_trending_recommendations(event))
        
        return recommendations
    
    def _update_session_data(self, event: UserEvent):
        """Update user session data"""
        session_key = f"session:{event.user_id}:{event.session_id}"
        
        if self.redis_client:
            # Store in Redis with 30-minute expiration
            self.redis_client.lpush(session_key, json.dumps(event.to_dict()))
            self.redis_client.expire(session_key, 1800)
        else:
            # Store in memory
            self.session_data[session_key].append(event)
            
            # Keep only last 50 events per session
            if len(self.session_data[session_key]) > 50:
                self.session_data[session_key] = self.session_data[session_key][-50:]
    
    def _update_hot_products(self, event: UserEvent):
        """Update hot products tracking"""
        weight = self.weights.get(event.event_type, 0.1)
        
        if self.redis_client:
            # Increment with weight
            self.redis_client.zincrby("hot_products", weight, event.product_id)
            
            # Keep only top 100 hot products
            self.redis_client.zremrangebyrank("hot_products", 0, -101)
        else:
            self.hot_products[event.product_id] += weight
    
    def _update_user_activity(self, event: UserEvent):
        """Update user's recent activity"""
        activity_key = f"user_activity:{event.user_id}"
        
        if self.redis_client:
            activity_data = {
                'product_id': event.product_id,
                'category': event.category,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat()
            }
            
            self.redis_client.lpush(activity_key, json.dumps(activity_data))
            self.redis_client.ltrim(activity_key, 0, 19)  # Keep last 20 activities
            self.redis_client.expire(activity_key, 3600)  # 1 hour expiration
        else:
            self.user_recent_activity[event.user_id].append(event)
            
            # Keep only last 20 activities
            if len(self.user_recent_activity[event.user_id]) > 20:
                self.user_recent_activity[event.user_id] = self.user_recent_activity[event.user_id][-20:]
    
    def _get_view_based_recommendations(self, event: UserEvent) -> List[ProductRecommendation]:
        """Generate recommendations based on product view"""
        recommendations = []
        
        # Recommend products from same category
        recommendations.append(ProductRecommendation(
            product_id=f"similar_{event.category}_{hash(event.product_id) % 100}",
            score=0.4,
            reason=f"Same category: {event.category}",
            source="stream"
        ))
        
        # Recommend based on recent user activity
        user_categories = self._get_user_preferred_categories(event.user_id)
        for category in user_categories:
            if category != event.category:
                recommendations.append(ProductRecommendation(
                    product_id=f"category_{category}_{hash(event.user_id) % 100}",
                    score=0.3,
                    reason=f"आपकी पसंदीदा category: {category}",
                    source="stream"
                ))
        
        return recommendations
    
    def _get_cart_based_recommendations(self, event: UserEvent) -> List[ProductRecommendation]:
        """Generate recommendations when user adds to cart"""
        recommendations = []
        
        # Frequently bought together recommendations
        recommendations.append(ProductRecommendation(
            product_id=f"bundle_{event.product_id}_{hash(event.user_id) % 50}",
            score=0.7,
            reason="साथ में खरीदे जाने वाले products",
            source="stream"
        ))
        
        # Accessories/complementary products
        recommendations.append(ProductRecommendation(
            product_id=f"accessory_{event.category}_{hash(event.product_id) % 30}",
            score=0.6,
            reason="Complementary products",
            source="stream"
        ))
        
        return recommendations
    
    def _get_search_based_recommendations(self, event: UserEvent) -> List[ProductRecommendation]:
        """Generate recommendations based on search behavior"""
        recommendations = []
        
        # Search intent-based recommendations
        recommendations.append(ProductRecommendation(
            product_id=f"search_match_{hash(event.product_id) % 100}",
            score=0.5,
            reason="Search में मिले products",
            source="stream"
        ))
        
        return recommendations
    
    def _get_trending_recommendations(self, event: UserEvent) -> List[ProductRecommendation]:
        """Get recommendations from trending products"""
        recommendations = []
        
        if self.redis_client:
            # Get top 5 hot products
            hot_products = self.redis_client.zrevrange("hot_products", 0, 4, withscores=True)
            
            for product_id, score in hot_products:
                if product_id != event.product_id:
                    recommendations.append(ProductRecommendation(
                        product_id=product_id,
                        score=min(score / 100.0, 0.8),  # Normalize score
                        reason="अभी trending products",
                        source="stream"
                    ))
        else:
            # Use in-memory hot products
            sorted_products = sorted(self.hot_products.items(), key=lambda x: x[1], reverse=True)
            
            for product_id, score in sorted_products[:5]:
                if product_id != event.product_id:
                    recommendations.append(ProductRecommendation(
                        product_id=product_id,
                        score=min(score / 100.0, 0.8),
                        reason="अभी trending products",
                        source="stream"
                    ))
        
        return recommendations
    
    def _get_user_preferred_categories(self, user_id: str) -> List[str]:
        """Get user's preferred categories from recent activity"""
        categories = defaultdict(int)
        
        if self.redis_client:
            activity_key = f"user_activity:{user_id}"
            activities = self.redis_client.lrange(activity_key, 0, -1)
            
            for activity_str in activities:
                activity = json.loads(activity_str)
                categories[activity['category']] += 1
        else:
            for event in self.user_recent_activity.get(user_id, []):
                categories[event.category] += 1
        
        # Return top 3 categories
        return [cat for cat, _ in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics"""
        stats = {}
        
        if self.redis_client:
            # Hot products
            hot_products = self.redis_client.zrevrange("hot_products", 0, 9, withscores=True)
            stats['hot_products'] = [{'product_id': p, 'score': s} for p, s in hot_products]
            
            # Active sessions count
            session_keys = self.redis_client.keys("session:*")
            stats['active_sessions'] = len(session_keys)
        else:
            # In-memory stats
            stats['hot_products'] = [
                {'product_id': p, 'score': s} 
                for p, s in sorted(self.hot_products.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            stats['active_sessions'] = len(self.session_data)
        
        return stats

class ServingLayer:
    """
    Serving Layer - Combines batch and speed layer results
    Final recommendations को serve करता है
    
    Responsibilities:
    1. Merge batch and stream recommendations
    2. Real-time serving with low latency
    3. A/B testing support
    4. Caching layer
    """
    
    def __init__(self, batch_layer: BatchLayer, speed_layer: SpeedLayer):
        self.batch_layer = batch_layer
        self.speed_layer = speed_layer
        
        # Recommendation cache
        self.recommendation_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # A/B testing configuration
        self.ab_test_enabled = True
        self.speed_layer_weight = 0.4
        self.batch_layer_weight = 0.6
    
    def get_recommendations(self, user_id: str, limit: int = 10) -> List[ProductRecommendation]:
        """
        Get final recommendations by combining batch and speed layers
        दोनों layers के results को intelligently merge करता है
        """
        
        # Check cache first
        cache_key = f"recommendations:{user_id}:{limit}"
        if cache_key in self.recommendation_cache:
            cached_data = self.recommendation_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['recommendations']
        
        # Get batch recommendations
        batch_recommendations = self._get_batch_recommendations(user_id)
        
        # Get speed layer recommendations (based on recent activity)
        speed_recommendations = self._get_recent_speed_recommendations(user_id)
        
        # Merge recommendations
        merged_recommendations = self._merge_recommendations(
            batch_recommendations, speed_recommendations
        )
        
        # Apply business rules and filters
        final_recommendations = self._apply_business_rules(merged_recommendations, user_id)
        
        # Limit results
        final_recommendations = final_recommendations[:limit]
        
        # Cache results
        self.recommendation_cache[cache_key] = {
            'recommendations': final_recommendations,
            'timestamp': time.time()
        }
        
        return final_recommendations
    
    def _get_batch_recommendations(self, user_id: str) -> List[ProductRecommendation]:
        """Get recommendations from batch layer"""
        conn = sqlite3.connect(self.batch_layer.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT product_id, score, reason
        FROM batch_recommendations
        WHERE user_id = ?
        ORDER BY score DESC
        """, (user_id,))
        
        batch_recs = []
        for product_id, score, reason in cursor.fetchall():
            batch_recs.append(ProductRecommendation(
                product_id=product_id,
                score=score * self.batch_layer_weight,
                reason=reason,
                source="batch"
            ))
        
        conn.close()
        return batch_recs
    
    def _get_recent_speed_recommendations(self, user_id: str) -> List[ProductRecommendation]:
        """Get recent recommendations from speed layer"""
        # For demo purposes, generate some speed layer recommendations
        # In production, this would come from the speed layer's cache
        
        speed_recs = []
        
        # Simulate real-time recommendations
        user_categories = self.speed_layer._get_user_preferred_categories(user_id)
        
        for i, category in enumerate(user_categories):
            speed_recs.append(ProductRecommendation(
                product_id=f"trending_{category}_{hash(user_id) % 100}",
                score=(0.8 - i * 0.1) * self.speed_layer_weight,
                reason=f"Real-time trending in {category}",
                source="stream"
            ))
        
        return speed_recs
    
    def _merge_recommendations(self, 
                             batch_recs: List[ProductRecommendation], 
                             speed_recs: List[ProductRecommendation]) -> List[ProductRecommendation]:
        """
        Merge batch and speed recommendations intelligently
        Duplicate products को handle करता है और best score रखता है
        """
        
        # Combine all recommendations
        all_recs = batch_recs + speed_recs
        
        # Group by product_id and take best score
        product_recommendations = {}
        
        for rec in all_recs:
            if rec.product_id not in product_recommendations:
                product_recommendations[rec.product_id] = rec
            else:
                # Keep recommendation with higher score
                existing_rec = product_recommendations[rec.product_id]
                if rec.score > existing_rec.score:
                    # Update with better score but combine reasons
                    rec.reason = f"{existing_rec.reason} + {rec.reason}"
                    rec.source = "combined"
                    product_recommendations[rec.product_id] = rec
        
        # Sort by score
        merged_recs = sorted(product_recommendations.values(), key=lambda x: x.score, reverse=True)
        
        return merged_recs
    
    def _apply_business_rules(self, recommendations: List[ProductRecommendation], user_id: str) -> List[ProductRecommendation]:
        """
        Apply business rules and filters
        Business constraints और user preferences apply करता है
        """
        
        filtered_recs = []
        
        # Business rules
        max_price_limit = 50000  # Maximum price limit
        category_diversity_required = True
        
        seen_categories = set()
        
        for rec in recommendations:
            # Skip if we have too many recommendations
            if len(filtered_recs) >= 20:
                break
            
            # Price filtering (simulate)
            product_price = hash(rec.product_id) % 10000  # Simulated price
            if product_price > max_price_limit:
                continue
            
            # Category diversity
            product_category = rec.product_id.split('_')[1] if '_' in rec.product_id else 'general'
            
            if category_diversity_required and product_category in seen_categories and len(seen_categories) < 5:
                # Skip if we already have 2+ products from this category
                category_count = sum(1 for r in filtered_recs 
                                   if r.product_id.split('_')[1] if '_' in r.product_id else 'general' == product_category)
                if category_count >= 2:
                    continue
            
            seen_categories.add(product_category)
            filtered_recs.append(rec)
        
        return filtered_recs
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get serving layer metrics"""
        
        return {
            "cache_size": len(self.recommendation_cache),
            "batch_layer_weight": self.batch_layer_weight,
            "speed_layer_weight": self.speed_layer_weight,
            "speed_layer_stats": self.speed_layer.get_real_time_stats(),
            "timestamp": datetime.now().isoformat()
        }

class FlipkartLambdaArchitecture:
    """
    Complete Lambda Architecture implementation for Flipkart recommendations
    सभी layers को coordinate करता है
    """
    
    def __init__(self):
        self.batch_layer = BatchLayer()
        self.speed_layer = SpeedLayer()
        self.serving_layer = ServingLayer(self.batch_layer, self.speed_layer)
        
        # Event processing queue
        self.event_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
    
    def start(self):
        """Start the lambda architecture"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_events_continuously)
        self.processing_thread.start()
        logger.info("Lambda Architecture started")
    
    def stop(self):
        """Stop the lambda architecture"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
        logger.info("Lambda Architecture stopped")
    
    def ingest_event(self, event: UserEvent):
        """Ingest new user event"""
        # Send to speed layer immediately
        speed_recommendations = self.speed_layer.process_real_time_event(event)
        
        # Queue for batch processing
        self.event_queue.put(event)
        
        return speed_recommendations
    
    def _process_events_continuously(self):
        """Process events continuously for batch layer"""
        batch_events = []
        
        while self.running:
            try:
                # Collect events for batch processing
                event = self.event_queue.get(timeout=1.0)
                batch_events.append(event)
                
                # Process batch when we have enough events
                if len(batch_events) >= 100:
                    self.batch_layer.store_events(batch_events)
                    batch_events = []
                
            except queue.Empty:
                # Process any remaining events
                if batch_events:
                    self.batch_layer.store_events(batch_events)
                    batch_events = []
                continue
    
    def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[ProductRecommendation]:
        """Get recommendations for user"""
        return self.serving_layer.get_recommendations(user_id, limit)
    
    def run_batch_job(self):
        """Run batch processing job"""
        self.batch_layer.run_batch_job()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get complete system metrics"""
        return {
            "serving_layer": self.serving_layer.get_real_time_metrics(),
            "event_queue_size": self.event_queue.qsize(),
            "system_status": "running" if self.running else "stopped",
            "timestamp": datetime.now().isoformat()
        }

def generate_sample_events(num_events: int = 1000) -> List[UserEvent]:
    """Generate sample user events for testing"""
    import random
    
    users = [f"user_{i:03d}" for i in range(1, 101)]  # 100 users
    products = [f"product_{i:04d}" for i in range(1, 501)]  # 500 products
    categories = ["electronics", "fashion", "books", "home", "sports", "beauty"]
    event_types = ["view", "cart_add", "purchase", "search"]
    devices = ["mobile", "desktop", "tablet"]
    
    events = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(num_events):
        user_id = random.choice(users)
        product_id = random.choice(products)
        category = random.choice(categories)
        event_type = random.choices(
            event_types, 
            weights=[60, 20, 10, 10]  # View is most common
        )[0]
        
        # Generate realistic timestamps
        timestamp = base_time + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        event = UserEvent(
            user_id=user_id,
            event_type=event_type,
            product_id=product_id,
            category=category,
            price=random.uniform(100, 5000),
            timestamp=timestamp,
            session_id=f"session_{user_id}_{timestamp.date()}_{random.randint(1, 5)}",
            device_type=random.choice(devices)
        )
        
        events.append(event)
    
    return sorted(events, key=lambda x: x.timestamp)

def run_lambda_architecture_demo():
    """Run complete lambda architecture demo"""
    
    logger.info("Starting Flipkart Lambda Architecture Demo...")
    
    # Initialize architecture
    lambda_arch = FlipkartLambdaArchitecture()
    lambda_arch.start()
    
    try:
        # Generate sample historical data
        logger.info("Generating sample historical data...")
        historical_events = generate_sample_events(2000)
        
        # Process historical events (batch layer)
        lambda_arch.batch_layer.store_events(historical_events)
        lambda_arch.run_batch_job()
        
        # Simulate real-time events
        logger.info("Simulating real-time events...")
        real_time_events = generate_sample_events(100)
        
        for i, event in enumerate(real_time_events):
            # Process real-time event
            speed_recs = lambda_arch.ingest_event(event)
            
            if i % 20 == 0:  # Every 20 events
                # Get final recommendations
                user_id = event.user_id
                final_recs = lambda_arch.get_user_recommendations(user_id, limit=5)
                
                print(f"\n=== Recommendations for {user_id} (after {i+1} events) ===")
                for j, rec in enumerate(final_recs, 1):
                    print(f"{j}. {rec.product_id} (score: {rec.score:.3f}) - {rec.reason} [{rec.source}]")
                
                # System metrics
                if i % 40 == 0:
                    metrics = lambda_arch.get_system_metrics()
                    print(f"\n=== System Metrics ===")
                    print(f"Event Queue Size: {metrics['event_queue_size']}")
                    print(f"Cache Size: {metrics['serving_layer']['cache_size']}")
                    print(f"Hot Products: {len(metrics['serving_layer']['speed_layer_stats'].get('hot_products', []))}")
            
            # Simulate processing delay
            time.sleep(0.05)  # 50ms delay
        
        # Final batch job after real-time processing
        logger.info("Running final batch job...")
        lambda_arch.run_batch_job()
        
        # Final recommendations for a few users
        print(f"\n=== Final Recommendations (after batch reprocessing) ===")
        for user_id in ["user_001", "user_002", "user_003"]:
            recs = lambda_arch.get_user_recommendations(user_id, limit=3)
            print(f"\n{user_id}:")
            for i, rec in enumerate(recs, 1):
                print(f"  {i}. {rec.product_id} - {rec.reason} [{rec.source}]")
    
    finally:
        lambda_arch.stop()

if __name__ == "__main__":
    run_lambda_architecture_demo()