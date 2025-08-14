#!/usr/bin/env python3
"""
CDN Cache Simulator - कंटेंट डिलीवरी नेटवर्क कैश सिमुलेशन
Mumbai ke local stations में chai vendors की तरह - popular items cache में रखते हैं

Real-world inspired by Cloudflare's edge caching and Indian OTT platforms like Hotstar
Cost Analysis: Cache hit = ₹0.1 per request, Cache miss = ₹2.0 per request
"""

import time
import random
import json
import hashlib
from collections import defaultdict, OrderedDict
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content types - अलग अलग content types"""
    VIDEO = "वीडियो"           # Heavy content like movies
    IMAGE = "इमेज"            # Medium content like photos  
    TEXT = "टेक्स्ट"           # Light content like web pages
    API = "एपीआई"             # Dynamic API responses

class CachePolicy(Enum):
    """Cache replacement policies"""
    LRU = "Least Recently Used"      # सबसे पुराना use किया गया
    LFU = "Least Frequently Used"    # सबसे कम use किया गया  
    FIFO = "First In First Out"      # पहले आया पहले जाएगा
    TTL = "Time To Live"             # Time based expiry

@dataclass
class CacheItem:
    """
    Cache item representation
    Mumbai local train ticket की तरह - har item ka details
    """
    content_id: str
    content_type: ContentType
    size_mb: float
    creation_time: float
    last_access_time: float
    access_count: int
    ttl_seconds: Optional[int] = None
    cost_to_fetch: float = 2.0      # Cost in INR to fetch from origin
    
    def is_expired(self) -> bool:
        """Check if content has expired based on TTL"""
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.creation_time) > self.ttl_seconds

class CDNEdgeCache:
    """
    CDN Edge Cache - Mumbai local station ke chai vendor की तरह
    Popular items ko cache में रखकर fast serving
    """
    
    def __init__(self, location: str, capacity_gb: float = 100.0, policy: CachePolicy = CachePolicy.LRU):
        """
        Initialize CDN Edge Cache
        Args:
            location: Geographic location (Mumbai area)
            capacity_gb: Cache capacity in GB  
            policy: Cache replacement policy
        """
        self.location = location
        self.capacity_gb = capacity_gb
        self.policy = policy
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.current_size_gb = 0.0
        
        # Performance metrics
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'evictions': 0,
            'bytes_served': 0,
            'cost_savings': 0.0,
            'response_times': [],
            'popular_content': defaultdict(int)
        }
        
        # Regional content preferences - Mumbai specific
        self.regional_preferences = {
            'bollywood_movies': 0.4,    # 40% requests
            'cricket_highlights': 0.2,   # 20% requests  
            'news_content': 0.15,       # 15% requests
            'web_apis': 0.15,           # 15% requests
            'social_media': 0.1         # 10% requests
        }
        
        # TTL settings by content type
        self.default_ttl = {
            ContentType.VIDEO: 86400,    # 24 hours
            ContentType.IMAGE: 3600,     # 1 hour
            ContentType.TEXT: 300,       # 5 minutes
            ContentType.API: 60          # 1 minute
        }
        
        logger.info(f"CDN Edge Cache initialized at {location} with {capacity_gb}GB capacity")
    
    def request_content(self, content_id: str, content_type: ContentType, size_mb: float) -> Tuple[bool, float, float]:
        """
        Request content from cache
        Returns: (cache_hit, response_time_ms, cost_inr)
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        # Check if content exists in cache and is not expired
        if content_id in self.cache:
            item = self.cache[content_id]
            
            if not item.is_expired():
                # Cache HIT! - Mumbai local train में seats mil gayi
                self._handle_cache_hit(content_id)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                cost = 0.1  # Cache hit cost in INR
                
                self.stats['response_times'].append(response_time)
                logger.debug(f"Cache HIT: {content_id} from {self.location} - {response_time:.2f}ms")
                return True, response_time, cost
            else:
                # Content expired - remove from cache
                self._remove_item(content_id)
        
        # Cache MISS - Origin se content fetch karna padega
        self.stats['cache_misses'] += 1
        
        # Simulate origin fetch time (much slower)
        origin_delay = self._simulate_origin_fetch(content_type, size_mb)
        response_time = (time.time() - start_time + origin_delay) * 1000
        cost = 2.0  # Origin fetch cost in INR
        
        # Add to cache if space available or make space
        self._add_to_cache(content_id, content_type, size_mb)
        
        self.stats['response_times'].append(response_time)
        logger.debug(f"Cache MISS: {content_id} fetched from origin - {response_time:.2f}ms")
        return False, response_time, cost
    
    def _handle_cache_hit(self, content_id: str):
        """Handle cache hit - update access patterns"""
        item = self.cache[content_id]
        item.last_access_time = time.time()
        item.access_count += 1
        self.stats['cache_hits'] += 1
        self.stats['bytes_served'] += item.size_mb * 1024 * 1024  # Convert to bytes
        self.stats['cost_savings'] += 1.9  # Saved ₹1.9 per hit (₹2.0 - ₹0.1)
        self.stats['popular_content'][content_id] += 1
        
        # Update position based on policy
        if self.policy == CachePolicy.LRU:
            # Move to end (most recently used)
            self.cache.move_to_end(content_id)
        
    def _simulate_origin_fetch(self, content_type: ContentType, size_mb: float) -> float:
        """
        Simulate origin server fetch delay
        Mumbai se distant datacenter fetch - network latency included
        """
        # Base latency to origin server (Mumbai to Singapore)
        base_latency = 0.15  # 150ms base latency
        
        # Size-based delay (network transfer time)
        transfer_time = size_mb / 10.0  # Assuming 10MB/s effective bandwidth
        
        # Content type specific processing delay
        processing_delay = {
            ContentType.VIDEO: 0.5,   # Video encoding/processing
            ContentType.IMAGE: 0.1,   # Image optimization  
            ContentType.TEXT: 0.05,   # Text compression
            ContentType.API: 0.2      # Database query + processing
        }.get(content_type, 0.1)
        
        total_delay = base_latency + transfer_time + processing_delay
        
        # Add some randomness to simulate real-world variations
        variation = random.uniform(0.8, 1.2)
        return total_delay * variation
    
    def _add_to_cache(self, content_id: str, content_type: ContentType, size_mb: float):
        """Add content to cache, evicting if necessary"""
        
        # Check if we need to make space
        while self.current_size_gb + (size_mb / 1024.0) > self.capacity_gb and self.cache:
            self._evict_content()
        
        # Create cache item
        ttl = self.default_ttl.get(content_type)
        item = CacheItem(
            content_id=content_id,
            content_type=content_type, 
            size_mb=size_mb,
            creation_time=time.time(),
            last_access_time=time.time(),
            access_count=1,
            ttl_seconds=ttl
        )
        
        # Add to cache
        self.cache[content_id] = item
        self.current_size_gb += size_mb / 1024.0
        
        logger.debug(f"Added to cache: {content_id} ({size_mb:.2f}MB)")
    
    def _evict_content(self):
        """Evict content based on cache policy"""
        if not self.cache:
            return
            
        if self.policy == CachePolicy.LRU:
            # Remove least recently used (first item)
            content_id, item = self.cache.popitem(last=False)
            
        elif self.policy == CachePolicy.LFU:
            # Remove least frequently used
            min_access_count = min(item.access_count for item in self.cache.values())
            for content_id, item in self.cache.items():
                if item.access_count == min_access_count:
                    break
            item = self.cache.pop(content_id)
            
        elif self.policy == CachePolicy.FIFO:
            # Remove oldest item by creation time
            content_id, item = self.cache.popitem(last=False)
            
        elif self.policy == CachePolicy.TTL:
            # Remove expired items first, then LRU
            expired_items = [(cid, item) for cid, item in self.cache.items() if item.is_expired()]
            if expired_items:
                content_id, item = expired_items[0]
                self.cache.pop(content_id)
            else:
                content_id, item = self.cache.popitem(last=False)
        
        self.current_size_gb -= item.size_mb / 1024.0
        self.stats['evictions'] += 1
        
        logger.debug(f"Evicted from cache: {content_id} ({item.size_mb:.2f}MB)")
    
    def _remove_item(self, content_id: str):
        """Remove specific item from cache"""
        if content_id in self.cache:
            item = self.cache.pop(content_id)
            self.current_size_gb -= item.size_mb / 1024.0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.stats['total_requests']
        if total_requests == 0:
            return {"error": "No requests processed yet"}
        
        hit_rate = (self.stats['cache_hits'] / total_requests) * 100
        miss_rate = (self.stats['cache_misses'] / total_requests) * 100
        
        avg_response_time = np.mean(self.stats['response_times']) if self.stats['response_times'] else 0
        
        # Calculate cost savings
        total_origin_cost = total_requests * 2.0
        actual_cost = (self.stats['cache_hits'] * 0.1) + (self.stats['cache_misses'] * 2.0)
        cost_savings = total_origin_cost - actual_cost
        savings_percentage = (cost_savings / total_origin_cost) * 100 if total_origin_cost > 0 else 0
        
        return {
            "location": self.location,
            "policy": self.policy.value,
            "capacity_gb": self.capacity_gb,
            "current_usage_gb": round(self.current_size_gb, 2),
            "utilization_percent": round((self.current_size_gb / self.capacity_gb) * 100, 2),
            "performance": {
                "total_requests": total_requests,
                "cache_hits": self.stats['cache_hits'],
                "cache_misses": self.stats['cache_misses'],
                "hit_rate_percent": round(hit_rate, 2),
                "miss_rate_percent": round(miss_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "bytes_served": self.stats['bytes_served']
            },
            "cost_analysis": {
                "total_cost_inr": round(actual_cost, 2),
                "cost_without_cache_inr": round(total_origin_cost, 2),
                "savings_inr": round(cost_savings, 2),
                "savings_percent": round(savings_percentage, 2)
            },
            "cache_details": {
                "items_in_cache": len(self.cache),
                "evictions": self.stats['evictions'],
                "popular_content": dict(list(self.stats['popular_content'].most_common(5)))
            }
        }

class CDNSimulator:
    """
    Complete CDN Simulator with multiple edge locations
    Mumbai metro network की तरह multiple stations
    """
    
    def __init__(self):
        """Initialize CDN with multiple edge locations across Mumbai"""
        self.edge_locations = {
            "andheri": CDNEdgeCache("Andheri", capacity_gb=500.0, policy=CachePolicy.LRU),
            "bandra": CDNEdgeCache("Bandra", capacity_gb=300.0, policy=CachePolicy.LFU),
            "thane": CDNEdgeCache("Thane", capacity_gb=200.0, policy=CachePolicy.TTL),
            "south_mumbai": CDNEdgeCache("South Mumbai", capacity_gb=400.0, policy=CachePolicy.LRU),
            "navi_mumbai": CDNEdgeCache("Navi Mumbai", capacity_gb=250.0, policy=CachePolicy.FIFO)
        }
        
        # Content catalog - Mumbai specific content
        self.content_catalog = self._generate_content_catalog()
        
        # User distribution by location
        self.user_distribution = {
            "andheri": 0.25,      # 25% users
            "bandra": 0.20,       # 20% users  
            "thane": 0.15,        # 15% users
            "south_mumbai": 0.30, # 30% users
            "navi_mumbai": 0.10   # 10% users
        }
        
        logger.info("CDN Simulator initialized with 5 edge locations")
    
    def _generate_content_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Generate realistic content catalog with Indian context"""
        catalog = {}
        
        # Bollywood movies (popular content)
        movies = [
            "dangal_2016", "bahubali_2017", "kgf_chapter2", "pushpa_2021", 
            "sooryavanshi_2021", "83_movie_2021", "jersey_2022", "laal_singh_chaddha"
        ]
        
        for movie in movies:
            catalog[movie] = {
                "type": ContentType.VIDEO,
                "size_mb": random.uniform(800, 2000),  # 800MB to 2GB
                "popularity": random.uniform(0.6, 0.9)  # High popularity
            }
        
        # Cricket content (very popular in India)
        cricket_content = [
            "ipl_2024_highlights", "india_vs_australia_series", "t20_worldcup_2024",
            "csk_vs_mi_match", "kohli_century_compilation", "dhoni_last_match"
        ]
        
        for content in cricket_content:
            catalog[content] = {
                "type": ContentType.VIDEO,
                "size_mb": random.uniform(200, 500),
                "popularity": random.uniform(0.7, 0.95)
            }
        
        # News content
        news_items = [
            "breaking_news_mumbai", "stock_market_updates", "weather_forecast",
            "local_mumbai_news", "national_news_hindi", "sports_updates"
        ]
        
        for news in news_items:
            catalog[news] = {
                "type": ContentType.TEXT,
                "size_mb": random.uniform(0.1, 2.0),
                "popularity": random.uniform(0.3, 0.7)
            }
        
        # API endpoints
        api_endpoints = [
            "user_profile_api", "payment_gateway_api", "maps_location_api",
            "weather_api", "stock_price_api", "train_schedule_api"
        ]
        
        for api in api_endpoints:
            catalog[api] = {
                "type": ContentType.API,
                "size_mb": random.uniform(0.001, 0.1),  # Very small
                "popularity": random.uniform(0.4, 0.8)
            }
        
        # Social media images
        social_images = [
            "instagram_stories", "whatsapp_status", "facebook_posts", 
            "twitter_images", "linkedin_posts"
        ]
        
        for image in social_images:
            catalog[image] = {
                "type": ContentType.IMAGE,
                "size_mb": random.uniform(0.5, 5.0),
                "popularity": random.uniform(0.5, 0.8)
            }
        
        return catalog
    
    def simulate_requests(self, num_requests: int = 10000, duration_hours: float = 24.0):
        """
        Simulate realistic request patterns over time
        Mumbai के traffic patterns की तरह - peak और off-peak hours
        """
        logger.info(f"Starting CDN simulation: {num_requests} requests over {duration_hours} hours")
        
        requests_per_second = num_requests / (duration_hours * 3600)
        
        for i in range(num_requests):
            # Simulate time progression
            current_hour = (i / num_requests) * duration_hours
            
            # Mumbai traffic pattern - peak hours simulation
            if 8 <= current_hour % 24 <= 11 or 17 <= current_hour % 24 <= 21:  # Peak hours
                request_multiplier = 2.5  # High traffic
            elif 22 <= current_hour % 24 or current_hour % 24 <= 6:  # Night hours
                request_multiplier = 0.3  # Low traffic
            else:
                request_multiplier = 1.0  # Normal traffic
            
            # Choose user location based on distribution
            location = np.random.choice(
                list(self.user_distribution.keys()),
                p=list(self.user_distribution.values())
            )
            
            # Choose content based on popularity and regional preferences
            content_id = self._choose_content_by_popularity()
            content_info = self.content_catalog[content_id]
            
            # Make request to appropriate edge location
            edge_cache = self.edge_locations[location]
            cache_hit, response_time, cost = edge_cache.request_content(
                content_id, 
                content_info["type"], 
                content_info["size_mb"]
            )
            
            # Log periodic updates
            if (i + 1) % 1000 == 0:
                logger.info(f"Processed {i + 1}/{num_requests} requests")
        
        logger.info("CDN simulation completed!")
    
    def _choose_content_by_popularity(self) -> str:
        """Choose content based on popularity weights"""
        content_ids = list(self.content_catalog.keys())
        popularities = [self.content_catalog[cid]["popularity"] for cid in content_ids]
        
        # Normalize probabilities
        total_popularity = sum(popularities)
        probabilities = [p / total_popularity for p in popularities]
        
        return np.random.choice(content_ids, p=probabilities)
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get statistics across all edge locations"""
        global_stats = {
            "total_locations": len(self.edge_locations),
            "locations": {},
            "aggregate": {
                "total_requests": 0,
                "total_cache_hits": 0,
                "total_cache_misses": 0,
                "total_cost": 0.0,
                "total_savings": 0.0,
                "avg_response_time": 0.0,
                "total_capacity_gb": 0.0,
                "total_usage_gb": 0.0
            }
        }
        
        all_response_times = []
        
        for location_name, cache in self.edge_locations.items():
            location_stats = cache.get_cache_stats()
            global_stats["locations"][location_name] = location_stats
            
            # Aggregate numbers
            if "error" not in location_stats:
                global_stats["aggregate"]["total_requests"] += location_stats["performance"]["total_requests"]
                global_stats["aggregate"]["total_cache_hits"] += location_stats["performance"]["cache_hits"]
                global_stats["aggregate"]["total_cache_misses"] += location_stats["performance"]["cache_misses"]
                global_stats["aggregate"]["total_cost"] += location_stats["cost_analysis"]["total_cost_inr"]
                global_stats["aggregate"]["total_savings"] += location_stats["cost_analysis"]["savings_inr"]
                global_stats["aggregate"]["total_capacity_gb"] += location_stats["capacity_gb"]
                global_stats["aggregate"]["total_usage_gb"] += location_stats["current_usage_gb"]
                
                if cache.stats['response_times']:
                    all_response_times.extend(cache.stats['response_times'])
        
        # Calculate aggregate metrics
        agg = global_stats["aggregate"]
        if agg["total_requests"] > 0:
            agg["global_hit_rate_percent"] = round((agg["total_cache_hits"] / agg["total_requests"]) * 100, 2)
            agg["global_miss_rate_percent"] = round((agg["total_cache_misses"] / agg["total_requests"]) * 100, 2)
        
        if all_response_times:
            agg["avg_response_time"] = round(np.mean(all_response_times), 2)
        
        if agg["total_capacity_gb"] > 0:
            agg["global_utilization_percent"] = round((agg["total_usage_gb"] / agg["total_capacity_gb"]) * 100, 2)
        
        return global_stats
    
    def generate_performance_report(self) -> str:
        """Generate detailed performance report"""
        stats = self.get_global_stats()
        agg = stats["aggregate"]
        
        report = f"""
🌐 CDN Performance Report - Mumbai Edge Network
{'=' * 60}

📊 Global Statistics:
• Total Edge Locations: {stats['total_locations']}
• Total Requests Processed: {agg['total_requests']:,}
• Global Cache Hit Rate: {agg.get('global_hit_rate_percent', 0)}%
• Average Response Time: {agg['avg_response_time']}ms
• Total Cache Capacity: {agg['total_capacity_gb']}GB
• Global Cache Utilization: {agg.get('global_utilization_percent', 0)}%

💰 Cost Analysis (24 hours):
• Total Cost with CDN: ₹{agg['total_cost']:,.2f}
• Cost without CDN: ₹{agg['total_cost'] + agg['total_savings']:,.2f}
• Total Savings: ₹{agg['total_savings']:,.2f}
• Monthly Savings Projection: ₹{agg['total_savings'] * 30:,.2f}
• Annual Savings Projection: ₹{agg['total_savings'] * 365:,.2f}

🏢 Location-wise Performance:
"""
        
        for location, location_stats in stats["locations"].items():
            if "error" in location_stats:
                continue
                
            perf = location_stats["performance"] 
            cost = location_stats["cost_analysis"]
            
            report += f"""
📍 {location.title()}:
   • Requests: {perf['total_requests']:,}
   • Hit Rate: {perf['hit_rate_percent']}%
   • Avg Response: {perf['avg_response_time_ms']}ms
   • Cost Savings: ₹{cost['savings_inr']:,.2f}
   • Cache Policy: {location_stats['policy']}
   • Utilization: {location_stats['utilization_percent']}%
"""
        
        report += f"""
📈 Business Impact:
• User Experience: {agg.get('global_hit_rate_percent', 0)}% faster content delivery
• Cost Efficiency: {((agg['total_savings'] / (agg['total_cost'] + agg['total_savings'])) * 100):.1f}% cost reduction
• Network Traffic: {agg['total_cache_hits']:,} requests served locally
• Origin Server Load: Reduced by {agg.get('global_hit_rate_percent', 0)}%

🎯 Mumbai-specific Benefits:
• Local Cricket/Bollywood content cached closer to users
• Reduced dependency on international connectivity
• Better performance during monsoon season network issues
• Cost-effective solution for Indian content consumption patterns
"""
        
        return report

# Example usage and performance testing
def main():
    """
    Demo CDN Cache Simulator with Mumbai traffic patterns
    Real-world performance testing with Indian content preferences
    """
    print("🌐 CDN Cache Simulator - Mumbai Edge Network")
    print("=" * 60)
    
    # Initialize CDN
    cdn = CDNSimulator()
    
    print(f"✅ CDN initialized with {len(cdn.edge_locations)} edge locations")
    print(f"📚 Content catalog: {len(cdn.content_catalog)} items")
    
    # Test individual cache operations
    print("\n🧪 Testing individual cache operations...")
    
    andheri_cache = cdn.edge_locations["andheri"]
    
    # Test popular content requests
    popular_content = [
        ("dangal_2016", ContentType.VIDEO, 1200.0),
        ("ipl_2024_highlights", ContentType.VIDEO, 350.0),
        ("breaking_news_mumbai", ContentType.TEXT, 0.5),
        ("user_profile_api", ContentType.API, 0.05)
    ]
    
    for content_id, content_type, size_mb in popular_content:
        cache_hit, response_time, cost = andheri_cache.request_content(content_id, content_type, size_mb)
        status = "HIT" if cache_hit else "MISS"
        print(f"  • {content_id}: {status} - {response_time:.2f}ms - ₹{cost:.2f}")
    
    # Test cache hit on second request
    print("\n🔄 Testing cache hits on repeat requests...")
    for content_id, content_type, size_mb in popular_content[:2]:
        cache_hit, response_time, cost = andheri_cache.request_content(content_id, content_type, size_mb)
        status = "HIT" if cache_hit else "MISS"
        print(f"  • {content_id}: {status} - {response_time:.2f}ms - ₹{cost:.2f}")
    
    # Run full simulation
    print("\n🚀 Running full CDN simulation...")
    print("Simulating 24 hours of Mumbai traffic patterns...")
    
    cdn.simulate_requests(num_requests=5000, duration_hours=24.0)
    
    # Generate and display performance report
    print("\n📊 Performance Report Generated!")
    print("=" * 60)
    
    report = cdn.generate_performance_report()
    print(report)
    
    # Additional analysis
    global_stats = cdn.get_global_stats()
    
    print("\n🔍 Detailed Analysis:")
    print("-" * 40)
    
    best_hit_rate = 0
    best_location = ""
    worst_hit_rate = 100
    worst_location = ""
    
    for location, stats in global_stats["locations"].items():
        if "error" in stats:
            continue
            
        hit_rate = stats["performance"]["hit_rate_percent"]
        if hit_rate > best_hit_rate:
            best_hit_rate = hit_rate
            best_location = location
        if hit_rate < worst_hit_rate:
            worst_hit_rate = hit_rate
            worst_location = location
    
    print(f"🏆 Best Performing Location: {best_location} ({best_hit_rate}% hit rate)")
    print(f"⚠️  Needs Attention: {worst_location} ({worst_hit_rate}% hit rate)")
    
    # Cost comparison
    agg = global_stats["aggregate"]
    monthly_savings = agg['total_savings'] * 30
    print(f"\n💰 ROI Analysis:")
    print(f"  • Daily Savings: ₹{agg['total_savings']:,.2f}")
    print(f"  • Monthly Savings: ₹{monthly_savings:,.2f}")
    print(f"  • Annual Savings: ₹{monthly_savings * 12:,.2f}")
    
    # Infrastructure cost estimate
    total_capacity = agg['total_capacity_gb']
    estimated_infra_cost = total_capacity * 1000  # ₹1000 per GB capacity
    payback_months = estimated_infra_cost / monthly_savings if monthly_savings > 0 else float('inf')
    
    print(f"  • Est. Infrastructure Cost: ₹{estimated_infra_cost:,.2f}")
    print(f"  • Payback Period: {payback_months:.1f} months")
    
    print("\n✅ CDN Cache Simulation completed successfully!")
    print("🏁 Mumbai edge computing network optimized for local content delivery!")

if __name__ == "__main__":
    main()