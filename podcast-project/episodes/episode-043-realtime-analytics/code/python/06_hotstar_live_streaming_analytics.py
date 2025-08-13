#!/usr/bin/env python3
"""
Hotstar Live Streaming Analytics
Episode 43: Real-time Analytics at Scale

यह example Hotstar जैसे streaming platform का real-time analytics दिखाता है
Live cricket match के दौरान concurrent viewers tracking करता है।

Real Production Stats:
- Hotstar: 25.3 million concurrent viewers (IPL 2019)
- Data points per second: 100,000+
- Analytics latency: <500ms
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import aioredis
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ViewerEvent:
    """Single viewer event data structure"""
    user_id: str
    session_id: str
    event_type: str  # join, leave, buffer, error
    timestamp: datetime
    location: Dict[str, str]
    device: Dict[str, str]
    quality: str  # 720p, 1080p, 4K
    cdn_edge: str
    buffer_health: float  # 0-100%
    bandwidth_mbps: float

@dataclass
class LiveMetrics:
    """Real-time streaming metrics"""
    concurrent_viewers: int
    peak_viewers: int
    total_joins: int
    total_leaves: int
    avg_buffer_health: float
    quality_distribution: Dict[str, int]
    location_breakdown: Dict[str, int]
    cdn_performance: Dict[str, float]
    errors_per_minute: int
    bandwidth_usage_gbps: float
    last_updated: datetime

class HotstarStreamingAnalytics:
    """
    Real-time streaming analytics for live events
    Production-ready implementation for handling millions of concurrent viewers
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = None
        self.redis_url = redis_url
        
        # In-memory analytics for demo
        self.metrics = LiveMetrics(
            concurrent_viewers=0,
            peak_viewers=0,
            total_joins=0,
            total_leaves=0,
            avg_buffer_health=95.0,
            quality_distribution={},
            location_breakdown={},
            cdn_performance={},
            errors_per_minute=0,
            bandwidth_usage_gbps=0.0,
            last_updated=datetime.now()
        )
        
        # Sliding window for real-time calculations
        self.viewer_events = deque(maxlen=10000)  # Last 10k events
        self.active_sessions = {}  # session_id -> ViewerEvent
        self.error_window = deque(maxlen=60)  # Last minute errors
        
        # CDN edges (Hotstar uses multiple CDNs)
        self.cdn_edges = [
            "mumbai-edge-01", "delhi-edge-02", "bangalore-edge-03",
            "chennai-edge-04", "kolkata-edge-05", "pune-edge-06",
            "hyderabad-edge-07", "ahmedabad-edge-08"
        ]
        
    async def connect_redis(self):
        """Connect to Redis for distributed analytics"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory mode")
    
    def generate_viewer_event(self, event_type: str = "join") -> ViewerEvent:
        """Generate realistic viewer event"""
        locations = [
            {"city": "Mumbai", "state": "Maharashtra"},
            {"city": "Delhi", "state": "Delhi"},
            {"city": "Bangalore", "state": "Karnataka"},
            {"city": "Chennai", "state": "Tamil Nadu"},
            {"city": "Kolkata", "state": "West Bengal"},
            {"city": "Pune", "state": "Maharashtra"},
            {"city": "Hyderabad", "state": "Telangana"}
        ]
        
        devices = [
            {"type": "mobile", "os": "Android", "model": "OnePlus 11"},
            {"type": "mobile", "os": "iOS", "model": "iPhone 14"},
            {"type": "tv", "os": "Android TV", "model": "Sony Bravia"},
            {"type": "desktop", "os": "Windows", "model": "Chrome"},
            {"type": "tablet", "os": "iPadOS", "model": "iPad Air"}
        ]
        
        user_id = f"user_{random.randint(1, 1000000)}"
        session_id = f"session_{int(time.time())}_{user_id}"
        
        return ViewerEvent(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            timestamp=datetime.now(),
            location=random.choice(locations),
            device=random.choice(devices),
            quality=random.choices(
                ["720p", "1080p", "4K"], 
                weights=[50, 40, 10]  # Most users on 720p/1080p
            )[0],
            cdn_edge=random.choice(self.cdn_edges),
            buffer_health=random.uniform(85, 100) if event_type != "buffer" else random.uniform(0, 50),
            bandwidth_mbps=random.uniform(1.5, 25.0)
        )
    
    async def process_viewer_event(self, event: ViewerEvent):
        """Process single viewer event and update metrics"""
        self.viewer_events.append(event)
        
        if event.event_type == "join":
            self.active_sessions[event.session_id] = event
            self.metrics.concurrent_viewers = len(self.active_sessions)
            self.metrics.total_joins += 1
            
            if self.metrics.concurrent_viewers > self.metrics.peak_viewers:
                self.metrics.peak_viewers = self.metrics.concurrent_viewers
                logger.info(f"🔥 New peak viewers: {self.metrics.peak_viewers:,}")
        
        elif event.event_type == "leave":
            if event.session_id in self.active_sessions:
                del self.active_sessions[event.session_id]
                self.metrics.concurrent_viewers = len(self.active_sessions)
                self.metrics.total_leaves += 1
        
        elif event.event_type == "error":
            self.error_window.append(event.timestamp)
            # Remove errors older than 1 minute
            cutoff = datetime.now() - timedelta(minutes=1)
            while self.error_window and self.error_window[0] < cutoff:
                self.error_window.popleft()
            self.metrics.errors_per_minute = len(self.error_window)
        
        # Update aggregations
        await self._update_aggregations()
        self.metrics.last_updated = datetime.now()
        
        # Store in Redis if available
        if self.redis:
            await self._store_in_redis(event)
    
    async def _update_aggregations(self):
        """Update aggregated metrics"""
        if not self.active_sessions:
            return
        
        # Quality distribution
        self.metrics.quality_distribution = defaultdict(int)
        location_count = defaultdict(int)
        cdn_buffer_health = defaultdict(list)
        total_bandwidth = 0.0
        
        for session in self.active_sessions.values():
            self.metrics.quality_distribution[session.quality] += 1
            location_count[session.location["city"]] += 1
            cdn_buffer_health[session.cdn_edge].append(session.buffer_health)
            total_bandwidth += session.bandwidth_mbps
        
        self.metrics.location_breakdown = dict(location_count)
        self.metrics.bandwidth_usage_gbps = total_bandwidth / 1000  # Convert to Gbps
        
        # CDN performance (average buffer health per edge)
        self.metrics.cdn_performance = {
            edge: sum(healths) / len(healths) 
            for edge, healths in cdn_buffer_health.items()
        }
        
        # Average buffer health
        all_buffer_healths = [s.buffer_health for s in self.active_sessions.values()]
        if all_buffer_healths:
            self.metrics.avg_buffer_health = sum(all_buffer_healths) / len(all_buffer_healths)
    
    async def _store_in_redis(self, event: ViewerEvent):
        """Store event in Redis for distributed processing"""
        try:
            # Store event
            await self.redis.lpush(
                "viewer_events", 
                json.dumps(asdict(event), default=str)
            )
            
            # Keep only last 10000 events
            await self.redis.ltrim("viewer_events", 0, 9999)
            
            # Store current metrics
            await self.redis.hset(
                "live_metrics",
                mapping={
                    "concurrent_viewers": self.metrics.concurrent_viewers,
                    "peak_viewers": self.metrics.peak_viewers,
                    "bandwidth_gbps": self.metrics.bandwidth_usage_gbps,
                    "errors_per_minute": self.metrics.errors_per_minute,
                    "last_updated": self.metrics.last_updated.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Redis storage failed: {e}")
    
    def print_live_dashboard(self):
        """Print real-time analytics dashboard"""
        print(f"\n{'='*60}")
        print(f"🔴 HOTSTAR LIVE STREAMING ANALYTICS 🔴")
        print(f"{'='*60}")
        print(f"⚡ Concurrent Viewers: {self.metrics.concurrent_viewers:,}")
        print(f"🏆 Peak Viewers: {self.metrics.peak_viewers:,}")
        print(f"📈 Total Joins: {self.metrics.total_joins:,}")
        print(f"📉 Total Leaves: {self.metrics.total_leaves:,}")
        print(f"🔧 Buffer Health: {self.metrics.avg_buffer_health:.1f}%")
        print(f"🌐 Bandwidth Usage: {self.metrics.bandwidth_usage_gbps:.2f} Gbps")
        print(f"❌ Errors/min: {self.metrics.errors_per_minute}")
        print(f"🕐 Last Updated: {self.metrics.last_updated.strftime('%H:%M:%S')}")
        
        if self.metrics.quality_distribution:
            print(f"\n📺 Quality Distribution:")
            total_viewers = sum(self.metrics.quality_distribution.values())
            for quality, count in sorted(self.metrics.quality_distribution.items()):
                percentage = (count / total_viewers) * 100
                print(f"  {quality}: {count:,} ({percentage:.1f}%)")
        
        if self.metrics.location_breakdown:
            print(f"\n🌍 Top Cities:")
            sorted_cities = sorted(
                self.metrics.location_breakdown.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            for city, count in sorted_cities:
                print(f"  {city}: {count:,}")
        
        if self.metrics.cdn_performance:
            print(f"\n🖥️ CDN Performance (Buffer Health):")
            sorted_cdns = sorted(
                self.metrics.cdn_performance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            for edge, health in sorted_cdns:
                print(f"  {edge}: {health:.1f}%")
    
    async def simulate_cricket_match(self, duration_minutes: int = 10):
        """
        Simulate IPL cricket match viewer pattern
        Real IPL matches में viewer pattern देखते हैं:
        - Match start: Rapid increase
        - Wickets/boundaries: Spikes
        - Strategic timeout: Slight dip
        - Match end: Rapid decrease
        """
        logger.info(f"🏏 Starting IPL match simulation for {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Cricket match events timeline
        match_events = [
            (0.1, "match_start", 5000),    # 5k viewers/sec at start
            (0.3, "first_wicket", 8000),   # Wicket spike
            (0.5, "big_six", 6000),        # Boundary excitement
            (0.7, "strategic_timeout", 2000), # Timeout dip
            (0.9, "match_finish", 10000),  # Finish spike
        ]
        
        event_index = 0
        base_join_rate = 1000  # Base viewers joining per second
        
        try:
            while time.time() < end_time:
                current_progress = (time.time() - start_time) / (duration_minutes * 60)
                
                # Check for cricket events
                if event_index < len(match_events):
                    event_time, event_name, spike_rate = match_events[event_index]
                    if current_progress >= event_time:
                        logger.info(f"🎯 Cricket Event: {event_name} - Viewer spike!")
                        base_join_rate = spike_rate
                        event_index += 1
                
                # Generate viewer events based on current rate
                events_this_second = random.poisson(base_join_rate // 10)  # Scale down for demo
                
                for _ in range(events_this_second):
                    # 80% joins, 15% leaves, 5% errors during normal play
                    event_type = random.choices(
                        ["join", "leave", "buffer", "error"],
                        weights=[80, 15, 3, 2]
                    )[0]
                    
                    event = self.generate_viewer_event(event_type)
                    await self.process_viewer_event(event)
                
                # Print dashboard every 10 seconds
                if int(time.time()) % 10 == 0:
                    self.print_live_dashboard()
                
                await asyncio.sleep(0.1)  # 100ms processing cycle
                
        except KeyboardInterrupt:
            logger.info("Match simulation stopped by user")
        
        logger.info("🏏 Match simulation completed!")
        self.print_live_dashboard()
    
    async def close(self):
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()

class ViewerBehaviorAnalyzer:
    """
    Analyze viewer behavior patterns
    Production में यह data ML models को feed करता है
    """
    
    def __init__(self, analytics: HotstarStreamingAnalytics):
        self.analytics = analytics
    
    def analyze_churn_risk(self) -> Dict[str, List[str]]:
        """Identify users at risk of churning based on buffer health"""
        high_risk = []
        medium_risk = []
        
        for session_id, session in self.analytics.active_sessions.items():
            if session.buffer_health < 70:
                high_risk.append(session_id)
            elif session.buffer_health < 85:
                medium_risk.append(session_id)
        
        return {
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "recommendations": [
                "Switch high-risk users to lower quality",
                "Pre-buffer content for medium-risk users",
                "Alert CDN team for edge optimization"
            ]
        }
    
    def get_peak_prediction(self) -> Dict[str, any]:
        """Predict peak viewers based on current trend"""
        if len(self.analytics.viewer_events) < 100:
            return {"prediction": "Insufficient data"}
        
        recent_events = list(self.analytics.viewer_events)[-100:]
        join_rate = sum(1 for e in recent_events if e.event_type == "join")
        leave_rate = sum(1 for e in recent_events if e.event_type == "leave")
        
        net_rate = join_rate - leave_rate
        predicted_peak = self.analytics.metrics.concurrent_viewers + (net_rate * 10)  # 10 minutes projection
        
        return {
            "current_viewers": self.analytics.metrics.concurrent_viewers,
            "predicted_peak_10min": max(predicted_peak, self.analytics.metrics.concurrent_viewers),
            "confidence": min(90, len(recent_events)),
            "recommendation": "Scale CDN capacity" if predicted_peak > self.analytics.metrics.peak_viewers else "Current capacity sufficient"
        }

async def main():
    """Main demo function"""
    print("🚀 Starting Hotstar Real-time Analytics Demo")
    
    analytics = HotstarStreamingAnalytics()
    await analytics.connect_redis()
    
    try:
        # Run cricket match simulation
        await analytics.simulate_cricket_match(duration_minutes=5)
        
        # Show behavior analysis
        analyzer = ViewerBehaviorAnalyzer(analytics)
        churn_analysis = analyzer.analyze_churn_risk()
        peak_prediction = analyzer.get_peak_prediction()
        
        print(f"\n📊 BEHAVIOR ANALYSIS")
        print(f"High Churn Risk Users: {len(churn_analysis['high_risk'])}")
        print(f"Medium Churn Risk Users: {len(churn_analysis['medium_risk'])}")
        
        print(f"\n📈 PEAK PREDICTION")
        for key, value in peak_prediction.items():
            print(f"{key}: {value}")
        
    finally:
        await analytics.close()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())