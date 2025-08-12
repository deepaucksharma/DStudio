#!/usr/bin/env python3
"""
IRCTC Train Availability Caching with Memcached
ट्रेन availability caching for high-traffic Tatkal booking

Memcached vs Redis:
- Memcached: Simple key-value, better for basic caching
- Redis: Feature-rich, supports data structures
- IRCTC uses Memcached for simple seat availability data
- Faster reads, good for high-frequency queries

Use Cases:
- Train seat availability (updates every 5 minutes)
- Station codes lookup (static data)
- Route information caching
- PNR status quick lookup
- Tatkal booking burst traffic handling

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 25 - Caching Strategies (Memcached Implementation)
"""

try:
    import memcache
    memcached_available = True
except ImportError:
    memcached_available = False

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memcached client setup
if memcached_available:
    try:
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        # Test connection
        mc.set("test_key", "test_value", time=1)
        if mc.get("test_key") == "test_value":
            memcached_connected = True
            logger.info("✅ Memcached connection established")
        else:
            memcached_connected = False
    except Exception as e:
        logger.warning(f"⚠️ Memcached connection failed: {str(e)}")
        memcached_connected = False
else:
    logger.warning("⚠️ python-memcached not installed, using fallback cache")
    memcached_connected = False

# Fallback in-memory cache
class MemoryCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str):
        if key in self._expiry and time.time() > self._expiry[key]:
            self.delete(key)
            return None
        return self._cache.get(key)
    
    def set(self, key: str, value, time_seconds: int):
        self._cache[key] = value
        self._expiry[key] = time.time() + time_seconds
        return True
    
    def delete(self, key: str):
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
    
    def flush_all(self):
        self._cache.clear()
        self._expiry.clear()

# Cache client
cache = mc if memcached_connected else MemoryCache()

@dataclass
class TrainAvailability:
    """Train availability data structure"""
    train_number: str
    train_name: str
    date: str
    from_station: str
    to_station: str
    classes: Dict[str, int]  # class_name: available_seats
    prices: Dict[str, float] # class_name: price
    departure_time: str
    arrival_time: str
    duration: str
    running_status: str
    last_updated: str

@dataclass
class Station:
    """Railway station data"""
    code: str
    name: str
    state: str
    zone: str
    division: str

@dataclass 
class Route:
    """Train route information"""
    train_number: str
    stations: List[Dict]  # station_code, arrival, departure, distance
    total_distance: int

# Cache TTL configuration (seconds)
CACHE_TTL = {
    'availability': 300,      # 5 minutes - train seat availability  
    'station_info': 86400,    # 24 hours - station codes (static)
    'route_info': 3600,       # 1 hour - train routes
    'pnr_status': 300,        # 5 minutes - PNR status
    'train_list': 7200,       # 2 hours - train list for route
    'fare_inquiry': 1800      # 30 minutes - fare information
}

# Mock database
STATIONS_DB = {
    'CSTM': Station('CSTM', 'Mumbai CST', 'Maharashtra', 'Central Railway', 'Mumbai'),
    'NDLS': Station('NDLS', 'New Delhi', 'Delhi', 'Northern Railway', 'Delhi'),
    'MAS': Station('MAS', 'Chennai Central', 'Tamil Nadu', 'Southern Railway', 'Chennai'),
    'HWH': Station('HWH', 'Howrah', 'West Bengal', 'Eastern Railway', 'Howrah'),
    'SBC': Station('SBC', 'Bangalore City', 'Karnataka', 'South Western Railway', 'Bangalore')
}

TRAINS_DB = {
    '12137': {
        'train_number': '12137',
        'train_name': 'Punjab Mail',
        'route': ['CSTM', 'NDLS'],
        'classes': ['SL', '3A', '2A', '1A'],
        'departure_time': '20:05',
        'arrival_time': '08:35',
        'duration': '12h 30m',
        'running_days': [1, 2, 3, 4, 5, 6, 7]  # Daily
    },
    '12951': {
        'train_number': '12951',
        'train_name': 'Mumbai Rajdhani',
        'route': ['CSTM', 'NDLS'],
        'classes': ['3A', '2A', '1A'],
        'departure_time': '17:00',
        'arrival_time': '08:35',
        'duration': '15h 35m', 
        'running_days': [1, 2, 3, 4, 5, 6]  # Except Sunday
    }
}

class IRCTCCacheManager:
    """
    IRCTC-style cache manager using Memcached
    High-performance caching for train booking system
    """
    
    def __init__(self):
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_sets': 0
        }
        
        logger.info("🚂 IRCTC Cache Manager initialized")
        if memcached_connected:
            logger.info("✅ Using Memcached for caching")
        else:
            logger.info("⚠️ Using in-memory fallback cache")
    
    def _generate_availability_key(self, train_number: str, date: str, 
                                  from_station: str, to_station: str) -> str:
        """Generate cache key for train availability"""
        return f"irctc:avail:{train_number}:{date}:{from_station}:{to_station}"
    
    def _generate_station_key(self, station_code: str) -> str:
        """Generate cache key for station info"""
        return f"irctc:station:{station_code}"
    
    def _generate_route_key(self, train_number: str) -> str:
        """Generate cache key for train route"""
        return f"irctc:route:{train_number}"
    
    def _generate_fare_key(self, train_number: str, from_station: str, 
                          to_station: str, class_type: str) -> str:
        """Generate cache key for fare inquiry"""
        return f"irctc:fare:{train_number}:{from_station}:{to_station}:{class_type}"
    
    def get_train_availability(self, train_number: str, date: str, 
                             from_station: str, to_station: str) -> Optional[TrainAvailability]:
        """
        Get train availability with caching
        High-frequency queries during Tatkal booking
        """
        cache_key = self._generate_availability_key(train_number, date, from_station, to_station)
        
        # Try cache first
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit for availability: {train_number} on {date}")
                
                if isinstance(cached_data, str):
                    data = json.loads(cached_data)
                else:
                    data = cached_data
                    
                return TrainAvailability(**data)
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
        
        # Cache miss - fetch from database
        self.stats['cache_misses'] += 1
        logger.info(f"Cache miss for availability: {train_number} on {date}")
        
        availability = self._fetch_availability_from_db(train_number, date, from_station, to_station)
        if availability:
            # Cache the result
            self._cache_availability(cache_key, availability)
        
        return availability
    
    def _fetch_availability_from_db(self, train_number: str, date: str,
                                  from_station: str, to_station: str) -> Optional[TrainAvailability]:
        """Mock database fetch for train availability"""
        if train_number not in TRAINS_DB:
            return None
        
        train = TRAINS_DB[train_number]
        
        # Mock availability data - in production this comes from reservation system
        import random
        availability = TrainAvailability(
            train_number=train_number,
            train_name=train['train_name'],
            date=date,
            from_station=from_station,
            to_station=to_station,
            classes={
                'SL': random.randint(0, 200),  # Sleeper
                '3A': random.randint(0, 60),   # 3rd AC
                '2A': random.randint(0, 40),   # 2nd AC
                '1A': random.randint(0, 20)    # 1st AC
            },
            prices={
                'SL': 485.0,
                '3A': 1250.0,
                '2A': 1850.0,
                '1A': 3200.0
            },
            departure_time=train['departure_time'],
            arrival_time=train['arrival_time'],
            duration=train['duration'],
            running_status='On Time',
            last_updated=datetime.now().isoformat()
        )
        
        return availability
    
    def _cache_availability(self, cache_key: str, availability: TrainAvailability):
        """Cache availability data"""
        try:
            data = asdict(availability)
            if memcached_connected:
                success = cache.set(cache_key, json.dumps(data), time=CACHE_TTL['availability'])
            else:
                success = cache.set(cache_key, data, time_seconds=CACHE_TTL['availability'])
            
            if success:
                self.stats['cache_sets'] += 1
                logger.debug(f"Cached availability: {availability.train_number}")
            else:
                logger.error("Failed to cache availability data")
                
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
    
    def get_station_info(self, station_code: str) -> Optional[Station]:
        """
        Get station information with caching
        Static data - can be cached for longer periods
        """
        cache_key = self._generate_station_key(station_code)
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit for station: {station_code}")
                
                if isinstance(cached_data, str):
                    data = json.loads(cached_data)
                else:
                    data = cached_data
                    
                return Station(**data)
        except Exception as e:
            logger.error(f"Station cache error: {str(e)}")
        
        # Cache miss
        self.stats['cache_misses'] += 1
        
        if station_code in STATIONS_DB:
            station = STATIONS_DB[station_code]
            
            # Cache for 24 hours (static data)
            try:
                data = asdict(station)
                if memcached_connected:
                    cache.set(cache_key, json.dumps(data), time=CACHE_TTL['station_info'])
                else:
                    cache.set(cache_key, data, time_seconds=CACHE_TTL['station_info'])
                
                self.stats['cache_sets'] += 1
            except Exception as e:
                logger.error(f"Station cache set error: {str(e)}")
            
            return station
        
        return None
    
    def search_trains(self, from_station: str, to_station: str, date: str) -> List[TrainAvailability]:
        """
        Search trains between stations with caching
        Mumbai CST to New Delhi - all trains
        """
        cache_key = f"irctc:search:{from_station}:{to_station}:{date}"
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.info(f"Cache hit for train search: {from_station} to {to_station}")
                
                if isinstance(cached_data, str):
                    trains_data = json.loads(cached_data)
                else:
                    trains_data = cached_data
                
                return [TrainAvailability(**train) for train in trains_data]
        except Exception as e:
            logger.error(f"Search cache error: {str(e)}")
        
        # Cache miss - search trains
        self.stats['cache_misses'] += 1
        logger.info(f"Cache miss for search: {from_station} to {to_station}")
        
        matching_trains = []
        for train_number, train_info in TRAINS_DB.items():
            if from_station in train_info['route'] and to_station in train_info['route']:
                availability = self._fetch_availability_from_db(
                    train_number, date, from_station, to_station
                )
                if availability:
                    matching_trains.append(availability)
        
        # Cache search results
        try:
            cache_data = [asdict(train) for train in matching_trains]
            if memcached_connected:
                cache.set(cache_key, json.dumps(cache_data), time=CACHE_TTL['train_list'])
            else:
                cache.set(cache_key, cache_data, time_seconds=CACHE_TTL['train_list'])
            
            self.stats['cache_sets'] += 1
        except Exception as e:
            logger.error(f"Search cache set error: {str(e)}")
        
        return matching_trains
    
    def update_availability(self, train_number: str, date: str, 
                          from_station: str, to_station: str,
                          class_updates: Dict[str, int]):
        """
        Update availability and invalidate cache
        जब कोई booking हो जाए तो availability update करना पड़ता है
        """
        # Update database (mock)
        logger.info(f"Updating availability for {train_number} on {date}")
        
        # Invalidate cache
        cache_key = self._generate_availability_key(train_number, date, from_station, to_station)
        try:
            if memcached_connected:
                cache.delete(cache_key)
            else:
                cache.delete(cache_key)
            
            logger.info(f"Cache invalidated for: {train_number}")
            
            # Also invalidate search results that might include this train
            search_key = f"irctc:search:{from_station}:{to_station}:{date}"
            if memcached_connected:
                cache.delete(search_key)
            else:
                cache.delete(search_key)
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")
    
    def get_pnr_status(self, pnr_number: str) -> Dict:
        """
        PNR status with short-term caching
        Status changes frequently, so shorter cache duration
        """
        cache_key = f"irctc:pnr:{pnr_number}"
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                if isinstance(cached_data, str):
                    return json.loads(cached_data)
                return cached_data
        except Exception as e:
            logger.error(f"PNR cache error: {str(e)}")
        
        # Mock PNR status
        self.stats['cache_misses'] += 1
        pnr_status = {
            'pnr': pnr_number,
            'status': 'CONFIRMED',
            'train_number': '12137',
            'train_name': 'Punjab Mail',
            'date': '2025-01-15',
            'passengers': [
                {'name': 'Rahul Sharma', 'status': 'CNF', 'coach': 'B1', 'berth': '25'}
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        # Cache with shorter TTL
        try:
            if memcached_connected:
                cache.set(cache_key, json.dumps(pnr_status), time=CACHE_TTL['pnr_status'])
            else:
                cache.set(cache_key, pnr_status, time_seconds=CACHE_TTL['pnr_status'])
            
            self.stats['cache_sets'] += 1
        except Exception as e:
            logger.error(f"PNR cache set error: {str(e)}")
        
        return pnr_status
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_ratio = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        memcached_stats = {}
        if memcached_connected:
            try:
                mc_stats = cache.get_stats()
                if mc_stats and len(mc_stats) > 0:
                    server_stats = mc_stats[0][1]  # First server stats
                    memcached_stats = {
                        'total_items': server_stats.get(b'total_items', 0),
                        'bytes': server_stats.get(b'bytes', 0),
                        'get_hits': server_stats.get(b'get_hits', 0),
                        'get_misses': server_stats.get(b'get_misses', 0),
                        'uptime': server_stats.get(b'uptime', 0)
                    }
            except Exception as e:
                memcached_stats = {'error': str(e)}
        
        return {
            'application_stats': self.stats,
            'hit_ratio_percent': round(hit_ratio, 2),
            'memcached_stats': memcached_stats,
            'cache_ttl_config': CACHE_TTL,
            'cache_status': 'Memcached' if memcached_connected else 'Memory Fallback'
        }

def demo_irctc_memcached():
    """
    Comprehensive demo of IRCTC Memcached caching
    Tatkal booking simulation
    """
    print("🚂 IRCTC Memcached Caching System Demo")
    print("="*50)
    
    cache_manager = IRCTCCacheManager()
    
    print("\n1. Station Information Lookup (Static Data)")
    
    # Station info - should be cached for long time
    station = cache_manager.get_station_info('CSTM')
    if station:
        print(f"   📍 {station.code}: {station.name}, {station.state}")
    
    # Same station again (cache hit)
    station = cache_manager.get_station_info('CSTM')
    print(f"   ✅ Station cache hit: {station.name}")
    
    print("\n2. Train Search Between Stations")
    
    # Search trains Mumbai to Delhi
    trains = cache_manager.search_trains('CSTM', 'NDLS', '2025-01-15')
    print(f"   🚂 Found {len(trains)} trains from Mumbai CST to New Delhi")
    
    for train in trains:
        print(f"      {train.train_number} {train.train_name}")
        print(f"      Departure: {train.departure_time}, Duration: {train.duration}")
        print(f"      Available: SL-{train.classes.get('SL', 0)}, "
              f"3A-{train.classes.get('3A', 0)}")
    
    print("\n3. Individual Train Availability Check")
    
    # Check specific train availability
    availability = cache_manager.get_train_availability('12137', '2025-01-15', 'CSTM', 'NDLS')
    if availability:
        print(f"   🎫 {availability.train_name} ({availability.train_number})")
        print(f"   📅 Date: {availability.date}")
        print(f"   🕐 Departure: {availability.departure_time} from {availability.from_station}")
        print(f"   📊 Availability:")
        for class_type, seats in availability.classes.items():
            price = availability.prices.get(class_type, 0)
            print(f"      {class_type}: {seats} seats available at ₹{price}")
    
    # Same availability check (cache hit)
    print("\n   Checking same availability again (cache hit):")
    start_time = time.time()
    availability = cache_manager.get_train_availability('12137', '2025-01-15', 'CSTM', 'NDLS')
    response_time = (time.time() - start_time) * 1000
    print(f"   ⚡ Response time: {response_time:.2f}ms (cached)")
    
    print("\n4. Booking Simulation & Cache Invalidation")
    
    # Simulate a booking (3A class, 2 seats booked)
    print("   💳 Simulating booking: 2 seats in 3A class")
    cache_manager.update_availability('12137', '2025-01-15', 'CSTM', 'NDLS', {'3A': -2})
    
    # Check availability again (cache miss due to invalidation)
    print("   🔄 Checking availability after booking:")
    availability = cache_manager.get_train_availability('12137', '2025-01-15', 'CSTM', 'NDLS')
    print(f"   📊 Updated 3A availability: {availability.classes.get('3A', 0)} seats")
    
    print("\n5. PNR Status Check")
    
    # PNR status lookup
    pnr_status = cache_manager.get_pnr_status('1234567890')
    print(f"   🎫 PNR: {pnr_status['pnr']}")
    print(f"   📊 Status: {pnr_status['status']}")
    print(f"   🚂 Train: {pnr_status['train_number']} {pnr_status['train_name']}")
    
    for passenger in pnr_status['passengers']:
        print(f"      👤 {passenger['name']}: {passenger['status']} "
              f"({passenger['coach']}/{passenger['berth']})")
    
    print("\n6. Cache Performance Statistics")
    
    stats = cache_manager.get_cache_stats()
    print(f"   📊 Cache Hit Ratio: {stats['hit_ratio_percent']}%")
    print(f"   ✅ Cache Hits: {stats['application_stats']['cache_hits']}")
    print(f"   ❌ Cache Misses: {stats['application_stats']['cache_misses']}")
    print(f"   💾 Cache Status: {stats['cache_status']}")
    
    if 'error' not in stats['memcached_stats']:
        mc_stats = stats['memcached_stats']
        print(f"   🗄️ Memcached Items: {mc_stats.get('total_items', 'N/A')}")
        print(f"   📈 Memcached Hits: {mc_stats.get('get_hits', 'N/A')}")
        print(f"   📉 Memcached Misses: {mc_stats.get('get_misses', 'N/A')}")
    
    print("\n7. Tatkal Booking Load Test")
    print("   ⚡ Simulating Tatkal booking rush (10 AM sharp)...")
    
    # Simulate multiple rapid requests
    start_time = time.time()
    for i in range(10):
        cache_manager.get_train_availability('12137', '2025-01-15', 'CSTM', 'NDLS')
    
    total_time = time.time() - start_time
    avg_time = (total_time / 10) * 1000
    
    print(f"   🏃 10 availability checks completed")
    print(f"   ⚡ Average response time: {avg_time:.2f}ms")
    print(f"   💪 Total time: {total_time:.2f}s")
    
    final_stats = cache_manager.get_cache_stats()
    print(f"   📊 Final hit ratio: {final_stats['hit_ratio_percent']}%")
    
    print("\n" + "="*50)
    print("🎉 IRCTC Memcached demo completed!")
    print("🚂 Train availability cached efficiently for Tatkal booking rush!")
    print("Mumbai CST से New Delhi तक - सभी trains ready for booking!")

if __name__ == '__main__':
    demo_irctc_memcached()