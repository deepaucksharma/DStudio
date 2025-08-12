#!/usr/bin/env python3
"""
Hotstar Video Content Delivery Network (CDN) Caching
हॉटस्टार style video caching और delivery system

CDN Caching Features:
- Edge server content caching
- Video quality adaptive streaming
- Regional content optimization
- Live streaming cache strategies
- Mumbai/Delhi/Bangalore edge servers
- Cricket match peak traffic handling

Use Cases:
- IPL live streaming (50M+ concurrent users)
- Regional movie content delivery
- Web series episode caching
- Thumbnail and metadata caching
- User preferences caching

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 25 - Caching Strategies (CDN Implementation)
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib
import logging
import threading
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoQuality(Enum):
    """Video quality options"""
    SD = "480p"      # 480p Standard Definition
    HD = "720p"      # 720p High Definition  
    FHD = "1080p"    # 1080p Full HD
    UHD = "2160p"    # 4K Ultra HD

class ContentType(Enum):
    """Content types on Hotstar"""
    LIVE_TV = "live_tv"
    LIVE_SPORTS = "live_sports"
    MOVIE = "movie"
    SERIES = "series"
    SHORT_VIDEO = "short_video"

@dataclass
class VideoContent:
    """Video content metadata"""
    content_id: str
    title: str
    content_type: ContentType
    duration_seconds: int
    available_qualities: List[VideoQuality]
    thumbnail_url: str
    description: str
    language: str
    genre: List[str]
    release_date: str
    view_count: int
    rating: float
    is_premium: bool
    regional_availability: List[str]  # States where available
    created_at: str

@dataclass
class EdgeServer:
    """CDN Edge server"""
    server_id: str
    location: str
    city: str
    state: str
    country: str = "IN"
    capacity_gbps: int = 100
    current_load_percent: int = 0
    cache_size_gb: int = 10000
    cache_used_gb: int = 0

@dataclass
class CacheItem:
    """Cached content item"""
    content_id: str
    quality: VideoQuality
    segment_number: int
    file_size_mb: float
    cache_timestamp: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    ttl_hours: int = 24

# Edge servers across India
EDGE_SERVERS = {
    'mumbai-01': EdgeServer('mumbai-01', 'Andheri', 'Mumbai', 'Maharashtra', capacity_gbps=200),
    'mumbai-02': EdgeServer('mumbai-02', 'BKC', 'Mumbai', 'Maharashtra', capacity_gbps=150),
    'delhi-01': EdgeServer('delhi-01', 'Gurgaon', 'Delhi', 'Delhi NCR', capacity_gbps=180),
    'bangalore-01': EdgeServer('bangalore-01', 'Whitefield', 'Bangalore', 'Karnataka', capacity_gbps=160),
    'chennai-01': EdgeServer('chennai-01', 'OMR', 'Chennai', 'Tamil Nadu', capacity_gbps=120),
    'kolkata-01': EdgeServer('kolkata-01', 'Rajarhat', 'Kolkata', 'West Bengal', capacity_gbps=100),
    'hyderabad-01': EdgeServer('hyderabad-01', 'Hitec City', 'Hyderabad', 'Telangana', capacity_gbps=140),
    'pune-01': EdgeServer('pune-01', 'Hinjewadi', 'Pune', 'Maharashtra', capacity_gbps=100)
}

# Sample content database
CONTENT_DATABASE = {
    'ipl_2025_final': VideoContent(
        content_id='ipl_2025_final',
        title='IPL 2025 Final - Mumbai Indians vs Chennai Super Kings',
        content_type=ContentType.LIVE_SPORTS,
        duration_seconds=14400,  # 4 hours
        available_qualities=[VideoQuality.SD, VideoQuality.HD, VideoQuality.FHD, VideoQuality.UHD],
        thumbnail_url='https://cdn.hotstar.com/ipl2025final_thumb.jpg',
        description='The ultimate showdown between MI and CSK',
        language='Hindi',
        genre=['Cricket', 'Sports', 'Live'],
        release_date='2025-05-30',
        view_count=45000000,  # 45M views
        rating=4.9,
        is_premium=True,
        regional_availability=['Maharashtra', 'Tamil Nadu', 'Delhi', 'Karnataka'],
        created_at=datetime.now().isoformat()
    ),
    
    'scam1992_ep1': VideoContent(
        content_id='scam1992_ep1',
        title='Scam 1992 - Episode 1',
        content_type=ContentType.SERIES,
        duration_seconds=3600,  # 1 hour
        available_qualities=[VideoQuality.HD, VideoQuality.FHD],
        thumbnail_url='https://cdn.hotstar.com/scam1992_ep1_thumb.jpg',
        description='The story of Harshad Mehta begins',
        language='Hindi',
        genre=['Drama', 'Biography', 'Thriller'],
        release_date='2020-10-09',
        view_count=12000000,  # 12M views
        rating=4.8,
        is_premium=True,
        regional_availability=['All States'],
        created_at=datetime.now().isoformat()
    ),
    
    'bollywood_blockbuster': VideoContent(
        content_id='bollywood_blockbuster',
        title='Mumbai Meri Jaan',
        content_type=ContentType.MOVIE,
        duration_seconds=9600,  # 2.67 hours
        available_qualities=[VideoQuality.SD, VideoQuality.HD, VideoQuality.FHD],
        thumbnail_url='https://cdn.hotstar.com/mumbai_movie_thumb.jpg',
        description='A heartwarming story of Mumbai dreams',
        language='Hindi',
        genre=['Drama', 'Romance', 'Family'],
        release_date='2023-12-25',
        view_count=8500000,  # 8.5M views
        rating=4.2,
        is_premium=False,
        regional_availability=['Maharashtra', 'Gujarat', 'Delhi', 'UP'],
        created_at=datetime.now().isoformat()
    )
}

class HotstarCDN:
    """
    Hotstar-style CDN system with intelligent caching
    Multi-tier caching with regional optimization
    """
    
    def __init__(self):
        # Cache storage for each edge server
        self.edge_caches = {server_id: {} for server_id in EDGE_SERVERS.keys()}
        
        # Content popularity tracking
        self.content_popularity = {}
        
        # Regional preferences
        self.regional_preferences = {
            'Maharashtra': ['Marathi', 'Hindi', 'English'],
            'Tamil Nadu': ['Tamil', 'Hindi', 'English'],
            'Karnataka': ['Kannada', 'Hindi', 'English'],
            'West Bengal': ['Bengali', 'Hindi', 'English'],
            'Delhi': ['Hindi', 'Punjabi', 'English']
        }
        
        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'origin_requests': 0,
            'total_bandwidth_saved_gb': 0,
            'peak_concurrent_users': 0
        }
        
        logger.info("📺 Hotstar CDN initialized with edge servers across India")
        
        # Start background cache management
        self._start_cache_management()
    
    def _start_cache_management(self):
        """Start background threads for cache management"""
        # Cache cleanup thread
        cleanup_thread = threading.Thread(target=self._cache_cleanup_worker, daemon=True)
        cleanup_thread.start()
        
        # Popular content preloading thread
        preload_thread = threading.Thread(target=self._popular_content_preloader, daemon=True)
        preload_thread.start()
    
    def find_nearest_edge_server(self, user_location: Dict) -> str:
        """
        Find nearest edge server based on user location
        Mumbai user को Mumbai servers मिलेंगे
        """
        user_state = user_location.get('state', '').lower()
        user_city = user_location.get('city', '').lower()
        
        # Direct city match
        for server_id, server in EDGE_SERVERS.items():
            if server.city.lower() == user_city:
                return server_id
        
        # State-based matching
        state_servers = {
            'maharashtra': ['mumbai-01', 'mumbai-02', 'pune-01'],
            'delhi': ['delhi-01'],
            'karnataka': ['bangalore-01'], 
            'tamil nadu': ['chennai-01'],
            'west bengal': ['kolkata-01'],
            'telangana': ['hyderabad-01']
        }
        
        if user_state in state_servers:
            available_servers = state_servers[user_state]
            # Return least loaded server
            return min(available_servers, 
                      key=lambda s: EDGE_SERVERS[s].current_load_percent)
        
        # Fallback to least loaded server
        return min(EDGE_SERVERS.keys(), 
                  key=lambda s: EDGE_SERVERS[s].current_load_percent)
    
    def get_video_content(self, content_id: str, quality: VideoQuality,
                         user_location: Dict, segment_number: int = 1) -> Dict:
        """
        Get video content with CDN caching
        IPL देखने वाले Mumbai users को Mumbai servers से content मिलेगा
        """
        start_time = time.time()
        
        # Find nearest edge server
        edge_server_id = self.find_nearest_edge_server(user_location)
        edge_server = EDGE_SERVERS[edge_server_id]
        
        # Generate cache key
        cache_key = f"{content_id}:{quality.value}:segment_{segment_number}"
        
        # Check edge cache first
        cache_hit = self._check_edge_cache(edge_server_id, cache_key)
        
        if cache_hit:
            self.stats['cache_hits'] += 1
            response_time = (time.time() - start_time) * 1000
            
            logger.info(f"✅ Cache HIT from {edge_server.city}: {content_id} ({quality.value})")
            
            # Update access statistics
            cache_hit.access_count += 1
            cache_hit.last_accessed = datetime.now()
            
            return {
                'content_id': content_id,
                'quality': quality.value,
                'segment_number': segment_number,
                'served_from': edge_server_id,
                'server_location': f"{edge_server.city}, {edge_server.state}",
                'cache_hit': True,
                'response_time_ms': response_time,
                'file_size_mb': cache_hit.file_size_mb,
                'cdn_url': f"https://{edge_server_id}.hotstar.com/{cache_key}",
                'bandwidth_saved': True
            }
        
        # Cache miss - fetch from origin
        self.stats['cache_misses'] += 1
        self.stats['origin_requests'] += 1
        
        logger.info(f"❌ Cache MISS from {edge_server.city}: {content_id} ({quality.value})")
        
        # Simulate origin server fetch
        origin_response_time = self._fetch_from_origin(content_id, quality, segment_number)
        
        # Cache the content at edge
        self._cache_at_edge(edge_server_id, cache_key, content_id, quality, segment_number)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            'content_id': content_id,
            'quality': quality.value,
            'segment_number': segment_number,
            'served_from': 'origin',
            'cached_at': edge_server_id,
            'server_location': f"{edge_server.city}, {edge_server.state}",
            'cache_hit': False,
            'response_time_ms': response_time,
            'origin_fetch_ms': origin_response_time,
            'file_size_mb': self._calculate_segment_size(quality, segment_number),
            'cdn_url': f"https://{edge_server_id}.hotstar.com/{cache_key}",
            'bandwidth_saved': False
        }
    
    def _check_edge_cache(self, server_id: str, cache_key: str) -> Optional[CacheItem]:
        """Check if content exists in edge cache"""
        edge_cache = self.edge_caches[server_id]
        cache_item = edge_cache.get(cache_key)
        
        if cache_item:
            # Check if cache item has expired
            age_hours = (datetime.now() - cache_item.cache_timestamp).total_seconds() / 3600
            if age_hours < cache_item.ttl_hours:
                return cache_item
            else:
                # Expired - remove from cache
                del edge_cache[cache_key]
                logger.debug(f"Cache expired for {cache_key}")
        
        return None
    
    def _fetch_from_origin(self, content_id: str, quality: VideoQuality, segment_number: int) -> float:
        """Simulate fetching content from origin server"""
        # Simulate network latency based on content size
        base_latency = 100  # 100ms base latency
        
        # Larger files take more time
        quality_multiplier = {
            VideoQuality.SD: 1.0,
            VideoQuality.HD: 1.5,
            VideoQuality.FHD: 2.0,
            VideoQuality.UHD: 3.0
        }
        
        fetch_time = base_latency * quality_multiplier[quality]
        time.sleep(fetch_time / 1000)  # Simulate fetch delay
        
        return fetch_time
    
    def _calculate_segment_size(self, quality: VideoQuality, segment_number: int) -> float:
        """Calculate video segment file size in MB"""
        # Typical segment sizes for 10-second chunks
        base_sizes = {
            VideoQuality.SD: 2.5,      # 2.5MB per segment
            VideoQuality.HD: 5.0,      # 5MB per segment
            VideoQuality.FHD: 8.0,     # 8MB per segment
            VideoQuality.UHD: 15.0     # 15MB per segment
        }
        
        return base_sizes[quality]
    
    def _cache_at_edge(self, server_id: str, cache_key: str, content_id: str,
                      quality: VideoQuality, segment_number: int):
        """Cache content at edge server"""
        file_size = self._calculate_segment_size(quality, segment_number)
        
        # Create cache item
        cache_item = CacheItem(
            content_id=content_id,
            quality=quality,
            segment_number=segment_number,
            file_size_mb=file_size,
            cache_timestamp=datetime.now(),
            ttl_hours=self._calculate_ttl(content_id, quality)
        )
        
        # Add to edge cache
        self.edge_caches[server_id][cache_key] = cache_item
        
        # Update server cache usage
        EDGE_SERVERS[server_id].cache_used_gb += file_size / 1024
        
        # Update bandwidth saved statistics
        self.stats['total_bandwidth_saved_gb'] += file_size / 1024
        
        logger.debug(f"Cached at {server_id}: {cache_key} ({file_size}MB)")
    
    def _calculate_ttl(self, content_id: str, quality: VideoQuality) -> int:
        """Calculate TTL based on content type and popularity"""
        if content_id not in CONTENT_DATABASE:
            return 24  # Default 24 hours
        
        content = CONTENT_DATABASE[content_id]
        
        # Live content has shorter TTL
        if content.content_type in [ContentType.LIVE_TV, ContentType.LIVE_SPORTS]:
            return 2  # 2 hours for live content
        
        # Popular content cached longer
        if content.view_count > 10000000:  # 10M+ views
            return 168  # 1 week
        elif content.view_count > 1000000:  # 1M+ views
            return 72   # 3 days
        else:
            return 24   # 1 day
    
    def preload_popular_content(self, content_ids: List[str]):
        """
        Preload popular content to all edge servers
        IPL start होने से पहले popular content को सभी servers पे cache कर देते हैं
        """
        logger.info(f"🔥 Preloading {len(content_ids)} popular content items...")
        
        preloaded_count = 0
        for content_id in content_ids:
            if content_id in CONTENT_DATABASE:
                content = CONTENT_DATABASE[content_id]
                
                # Preload multiple qualities for popular content
                qualities_to_preload = [VideoQuality.HD, VideoQuality.FHD]
                if content.view_count > 20000000:  # 20M+ views
                    qualities_to_preload.append(VideoQuality.UHD)
                
                for quality in qualities_to_preload:
                    # Preload first few segments
                    for segment in range(1, 6):  # First 5 segments
                        cache_key = f"{content_id}:{quality.value}:segment_{segment}"
                        
                        # Cache on multiple edge servers
                        target_servers = self._select_preload_servers(content)
                        
                        for server_id in target_servers:
                            if cache_key not in self.edge_caches[server_id]:
                                self._cache_at_edge(server_id, cache_key, content_id, quality, segment)
                                preloaded_count += 1
        
        logger.info(f"✅ Preloading completed: {preloaded_count} segments cached")
    
    def _select_preload_servers(self, content: VideoContent) -> List[str]:
        """Select edge servers for content preloading based on regional availability"""
        if 'All States' in content.regional_availability:
            return list(EDGE_SERVERS.keys())
        
        # Select servers based on regional availability
        selected_servers = []
        state_to_servers = {
            'Maharashtra': ['mumbai-01', 'mumbai-02', 'pune-01'],
            'Delhi': ['delhi-01'],
            'Karnataka': ['bangalore-01'],
            'Tamil Nadu': ['chennai-01'],
            'West Bengal': ['kolkata-01'],
            'Telangana': ['hyderabad-01']
        }
        
        for state in content.regional_availability:
            if state in state_to_servers:
                selected_servers.extend(state_to_servers[state])
        
        return list(set(selected_servers))  # Remove duplicates
    
    def _cache_cleanup_worker(self):
        """Background worker to clean expired cache items"""
        while True:
            try:
                cleaned_items = 0
                for server_id, cache in self.edge_caches.items():
                    expired_keys = []
                    
                    for cache_key, cache_item in cache.items():
                        age_hours = (datetime.now() - cache_item.cache_timestamp).total_seconds() / 3600
                        if age_hours >= cache_item.ttl_hours:
                            expired_keys.append(cache_key)
                    
                    # Remove expired items
                    for key in expired_keys:
                        cache_item = cache.pop(key)
                        EDGE_SERVERS[server_id].cache_used_gb -= cache_item.file_size_mb / 1024
                        cleaned_items += 1
                
                if cleaned_items > 0:
                    logger.info(f"🧹 Cache cleanup: {cleaned_items} expired items removed")
                
                time.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {str(e)}")
                time.sleep(60)
    
    def _popular_content_preloader(self):
        """Background worker to preload popular content"""
        while True:
            try:
                # Get top viewed content
                popular_content = sorted(
                    CONTENT_DATABASE.keys(),
                    key=lambda cid: CONTENT_DATABASE[cid].view_count,
                    reverse=True
                )[:5]  # Top 5
                
                self.preload_popular_content(popular_content)
                
                time.sleep(21600)  # Run every 6 hours
                
            except Exception as e:
                logger.error(f"Preload worker error: {str(e)}")
                time.sleep(3600)
    
    def get_cdn_statistics(self) -> Dict:
        """Get comprehensive CDN statistics"""
        total_cache_items = sum(len(cache) for cache in self.edge_caches.values())
        total_cache_size_gb = sum(server.cache_used_gb for server in EDGE_SERVERS.values())
        
        # Calculate hit ratio
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_ratio = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Server-wise statistics
        server_stats = {}
        for server_id, server in EDGE_SERVERS.items():
            cache_count = len(self.edge_caches[server_id])
            server_stats[server_id] = {
                'location': f"{server.city}, {server.state}",
                'cached_items': cache_count,
                'cache_used_gb': round(server.cache_used_gb, 2),
                'cache_utilization_percent': round((server.cache_used_gb / server.cache_size_gb) * 100, 2),
                'capacity_gbps': server.capacity_gbps,
                'current_load_percent': server.current_load_percent
            }
        
        return {
            'overall_stats': {
                'total_cache_hits': self.stats['cache_hits'],
                'total_cache_misses': self.stats['cache_misses'],
                'hit_ratio_percent': round(hit_ratio, 2),
                'origin_requests': self.stats['origin_requests'],
                'bandwidth_saved_gb': round(self.stats['total_bandwidth_saved_gb'], 2)
            },
            'edge_servers': server_stats,
            'total_cached_items': total_cache_items,
            'total_cache_size_gb': round(total_cache_size_gb, 2),
            'active_servers': len(EDGE_SERVERS)
        }

def demo_hotstar_cdn():
    """
    Comprehensive Hotstar CDN demo
    IPL season peak traffic simulation
    """
    print("📺 Hotstar CDN System Demo")
    print("="*50)
    
    cdn = HotstarCDN()
    
    print("\n1. Content Preloading for IPL Season")
    
    # Preload popular content
    popular_content = ['ipl_2025_final', 'scam1992_ep1']
    cdn.preload_popular_content(popular_content)
    
    print("\n2. User Requests from Different Cities")
    
    # Mumbai user watching IPL Final
    mumbai_user = {'city': 'Mumbai', 'state': 'Maharashtra'}
    print(f"\n   👤 Mumbai user watching IPL Final:")
    
    # First request (cache miss due to live content)
    response1 = cdn.get_video_content('ipl_2025_final', VideoQuality.FHD, mumbai_user, segment_number=1)
    print(f"      📺 Quality: {response1['quality']}")
    print(f"      🌐 Served from: {response1['server_location']}")
    print(f"      ⚡ Response time: {response1['response_time_ms']:.2f}ms")
    print(f"      💾 Cache hit: {response1['cache_hit']}")
    
    # Second request (cache hit)
    response2 = cdn.get_video_content('ipl_2025_final', VideoQuality.FHD, mumbai_user, segment_number=2)
    print(f"      ⚡ Second segment: {response2['response_time_ms']:.2f}ms (cached)")
    
    # Delhi user watching same content
    delhi_user = {'city': 'Delhi', 'state': 'Delhi'}
    print(f"\n   👤 Delhi user watching same IPL Final:")
    
    response3 = cdn.get_video_content('ipl_2025_final', VideoQuality.HD, delhi_user, segment_number=1)
    print(f"      🌐 Served from: {response3['server_location']}")
    print(f"      💾 Cache hit: {response3['cache_hit']}")
    
    print("\n3. Regional Content Access")
    
    # Chennai user accessing regional content
    chennai_user = {'city': 'Chennai', 'state': 'Tamil Nadu'}
    print(f"\n   👤 Chennai user watching Bollywood movie:")
    
    response4 = cdn.get_video_content('bollywood_blockbuster', VideoQuality.HD, chennai_user)
    print(f"      🌐 Served from: {response4['server_location']}")
    print(f"      ⚡ Response time: {response4['response_time_ms']:.2f}ms")
    
    print("\n4. Different Quality Streaming")
    
    # Bangalore user with different quality preferences
    bangalore_user = {'city': 'Bangalore', 'state': 'Karnataka'}
    
    print(f"\n   👤 Bangalore user streaming in different qualities:")
    
    for quality in [VideoQuality.SD, VideoQuality.HD, VideoQuality.FHD]:
        response = cdn.get_video_content('scam1992_ep1', quality, bangalore_user)
        print(f"      📺 {quality.value}: {response['response_time_ms']:.2f}ms, "
              f"Size: {response['file_size_mb']}MB")
    
    print("\n5. Peak Traffic Simulation (IPL Match)")
    
    print("   ⚡ Simulating peak traffic during IPL match...")
    
    # Simulate multiple concurrent users
    locations = [
        {'city': 'Mumbai', 'state': 'Maharashtra'},
        {'city': 'Delhi', 'state': 'Delhi'},
        {'city': 'Bangalore', 'state': 'Karnataka'},
        {'city': 'Chennai', 'state': 'Tamil Nadu'},
        {'city': 'Kolkata', 'state': 'West Bengal'}
    ]
    
    start_time = time.time()
    total_requests = 0
    
    for i in range(20):  # 20 requests simulation
        user_location = locations[i % len(locations)]
        response = cdn.get_video_content('ipl_2025_final', VideoQuality.HD, user_location, 
                                       segment_number=(i % 10) + 1)
        total_requests += 1
    
    simulation_time = time.time() - start_time
    
    print(f"   📊 Processed {total_requests} requests in {simulation_time:.2f}s")
    print(f"   ⚡ Average response time: {(simulation_time/total_requests)*1000:.2f}ms")
    
    print("\n6. CDN Performance Statistics")
    
    stats = cdn.get_cdn_statistics()
    
    print(f"\n   📊 Overall Performance:")
    overall = stats['overall_stats']
    print(f"      ✅ Cache Hits: {overall['total_cache_hits']}")
    print(f"      ❌ Cache Misses: {overall['total_cache_misses']}")
    print(f"      📈 Hit Ratio: {overall['hit_ratio_percent']}%")
    print(f"      💰 Bandwidth Saved: {overall['bandwidth_saved_gb']:.2f} GB")
    print(f"      🌐 Origin Requests: {overall['origin_requests']}")
    
    print(f"\n   🌐 Edge Server Status:")
    for server_id, server_stat in stats['edge_servers'].items():
        print(f"      📍 {server_stat['location']}:")
        print(f"         💾 Cached Items: {server_stat['cached_items']}")
        print(f"         📊 Cache Used: {server_stat['cache_used_gb']} GB "
              f"({server_stat['cache_utilization_percent']}%)")
        print(f"         🚄 Capacity: {server_stat['capacity_gbps']} Gbps")
    
    print(f"\n   📦 Total Cache Status:")
    print(f"      📁 Total Items: {stats['total_cached_items']}")
    print(f"      💾 Total Size: {stats['total_cache_size_gb']} GB")
    print(f"      🌍 Active Servers: {stats['active_servers']}")
    
    print("\n7. Content Popularity Analysis")
    
    content_stats = {}
    for server_id, cache in cdn.edge_caches.items():
        for cache_key, cache_item in cache.items():
            content_id = cache_item.content_id
            if content_id not in content_stats:
                content_stats[content_id] = {'access_count': 0, 'servers': set()}
            
            content_stats[content_id]['access_count'] += cache_item.access_count
            content_stats[content_id]['servers'].add(server_id)
    
    print(f"\n   📊 Content Performance:")
    for content_id, stat in content_stats.items():
        if content_id in CONTENT_DATABASE:
            content = CONTENT_DATABASE[content_id]
            print(f"      📺 {content.title[:40]}...")
            print(f"         🎯 Access Count: {stat['access_count']}")
            print(f"         🌐 Cached on: {len(stat['servers'])} servers")
            print(f"         👁️ Total Views: {content.view_count:,}")
    
    print("\n" + "="*50)
    print("🎉 Hotstar CDN demo completed!")
    print("📺 Content delivered efficiently across India!")
    print("🏏 Ready for next IPL season peak traffic!")
    print("Mumbai से Chennai तक - सभी users को smooth streaming! 🚀")

if __name__ == '__main__':
    demo_hotstar_cdn()