"""
User Session Tracking with State Management
यह system IPL viewing sessions को track करता है with proper state management
Example: Hotstar user sessions, continuity across devices, viewing preferences

Mumbai dabba delivery जैसे - हर user का session perfectly track करना पड़ता है!
"""

import json
import time
import threading
import pickle
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import redis
import rocksdb
from kafka import KafkaConsumer, KafkaProducer
import hashlib
import uuid
import concurrent.futures
from contextlib import contextmanager

class SessionState(Enum):
    """User session के different states"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE" 
    PAUSED = "PAUSED"
    EXPIRED = "EXPIRED"
    MIGRATED = "MIGRATED"  # Device change

class QualityLevel(Enum):
    """Video quality levels"""
    LOW = "480p"
    MEDIUM = "720p" 
    HIGH = "1080p"
    ULTRA = "4K"

@dataclass
class ViewingPreferences:
    """User के viewing preferences"""
    preferred_quality: QualityLevel = QualityLevel.MEDIUM
    preferred_language: str = "Hindi"
    notifications_enabled: bool = True
    autoplay_enabled: bool = True
    data_saver_mode: bool = False
    preferred_commentary: str = "Hindi"
    
@dataclass 
class DeviceInfo:
    """Device information"""
    device_id: str
    device_type: str  # MOBILE, TV, DESKTOP, TABLET
    os_type: str      # Android, iOS, Web, Android_TV
    app_version: str
    screen_resolution: str
    network_type: str # WIFI, 4G, 5G, 3G, 2G
    
@dataclass
class UserSession:
    """Complete user session state"""
    session_id: str
    user_id: str
    match_id: str
    state: SessionState
    start_time: datetime
    last_activity: datetime
    device_info: DeviceInfo
    current_position: int = 0  # Video position in seconds
    viewing_quality: QualityLevel = QualityLevel.MEDIUM
    preferences: ViewingPreferences = field(default_factory=ViewingPreferences)
    watch_duration: int = 0  # Total watch time in seconds
    buffer_events: int = 0
    quality_changes: int = 0
    pause_count: int = 0
    seek_count: int = 0
    
    # Session metadata
    ip_address: str = ""
    geographic_location: str = ""
    isp: str = ""
    bandwidth_mbps: float = 0.0
    
    # Viewing behavior
    segments_watched: Set[int] = field(default_factory=set)  # 30-second segments
    peak_concurrent_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'match_id': self.match_id,
            'state': self.state.value,
            'start_time': self.start_time.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'device_info': {
                'device_id': self.device_info.device_id,
                'device_type': self.device_info.device_type,
                'os_type': self.device_info.os_type,
                'app_version': self.device_info.app_version,
                'screen_resolution': self.device_info.screen_resolution,
                'network_type': self.device_info.network_type,
            },
            'current_position': self.current_position,
            'viewing_quality': self.viewing_quality.value,
            'preferences': {
                'preferred_quality': self.preferences.preferred_quality.value,
                'preferred_language': self.preferences.preferred_language,
                'notifications_enabled': self.preferences.notifications_enabled,
                'autoplay_enabled': self.preferences.autoplay_enabled,
                'data_saver_mode': self.preferences.data_saver_mode,
                'preferred_commentary': self.preferences.preferred_commentary,
            },
            'watch_duration': self.watch_duration,
            'buffer_events': self.buffer_events,
            'quality_changes': self.quality_changes,
            'pause_count': self.pause_count,
            'seek_count': self.seek_count,
            'ip_address': self.ip_address,
            'geographic_location': self.geographic_location,
            'isp': self.isp,
            'bandwidth_mbps': self.bandwidth_mbps,
            'segments_watched': list(self.segments_watched),
            'peak_concurrent_time': self.peak_concurrent_time.isoformat() if self.peak_concurrent_time else None
        }

class StateBackend:
    """Abstract base class for state backends"""
    
    def save_session(self, session: UserSession) -> bool:
        raise NotImplementedError
    
    def load_session(self, session_id: str) -> Optional[UserSession]:
        raise NotImplementedError
    
    def delete_session(self, session_id: str) -> bool:
        raise NotImplementedError
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        raise NotImplementedError

class RedisStateBackend(StateBackend):
    """Redis-based state backend for fast access"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.session_ttl = 3600 * 4  # 4 hours TTL
        
    def save_session(self, session: UserSession) -> bool:
        try:
            key = f"session:{session.session_id}"
            session_data = json.dumps(session.to_dict(), default=str)
            
            # Save with TTL
            self.redis_client.setex(key, self.session_ttl, session_data)
            
            # Index by user for quick lookup
            user_key = f"user_sessions:{session.user_id}"
            self.redis_client.sadd(user_key, session.session_id)
            self.redis_client.expire(user_key, self.session_ttl)
            
            return True
        except Exception as e:
            print(f"❌ Redis save error: {str(e)}")
            return False
    
    def load_session(self, session_id: str) -> Optional[UserSession]:
        try:
            key = f"session:{session_id}"
            session_data = self.redis_client.get(key)
            
            if session_data:
                data = json.loads(session_data)
                return self._dict_to_session(data)
            return None
        except Exception as e:
            print(f"❌ Redis load error: {str(e)}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        try:
            session = self.load_session(session_id)
            if session:
                # Remove from user index
                user_key = f"user_sessions:{session.user_id}"
                self.redis_client.srem(user_key, session_id)
            
            # Delete session
            key = f"session:{session_id}"
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"❌ Redis delete error: {str(e)}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        try:
            user_key = f"user_sessions:{user_id}"
            session_ids = self.redis_client.smembers(user_key)
            
            sessions = []
            for session_id in session_ids:
                session = self.load_session(session_id)
                if session:
                    sessions.append(session)
            
            return sessions
        except Exception as e:
            print(f"❌ Redis get user sessions error: {str(e)}")
            return []
    
    def _dict_to_session(self, data: Dict) -> UserSession:
        """Convert dictionary back to UserSession object"""
        device_info = DeviceInfo(
            device_id=data['device_info']['device_id'],
            device_type=data['device_info']['device_type'],
            os_type=data['device_info']['os_type'],
            app_version=data['device_info']['app_version'],
            screen_resolution=data['device_info']['screen_resolution'],
            network_type=data['device_info']['network_type']
        )
        
        preferences = ViewingPreferences(
            preferred_quality=QualityLevel(data['preferences']['preferred_quality']),
            preferred_language=data['preferences']['preferred_language'],
            notifications_enabled=data['preferences']['notifications_enabled'],
            autoplay_enabled=data['preferences']['autoplay_enabled'],
            data_saver_mode=data['preferences']['data_saver_mode'],
            preferred_commentary=data['preferences']['preferred_commentary']
        )
        
        session = UserSession(
            session_id=data['session_id'],
            user_id=data['user_id'],
            match_id=data['match_id'],
            state=SessionState(data['state']),
            start_time=datetime.fromisoformat(data['start_time']),
            last_activity=datetime.fromisoformat(data['last_activity']),
            device_info=device_info,
            current_position=data['current_position'],
            viewing_quality=QualityLevel(data['viewing_quality']),
            preferences=preferences,
            watch_duration=data['watch_duration'],
            buffer_events=data['buffer_events'],
            quality_changes=data['quality_changes'],
            pause_count=data['pause_count'],
            seek_count=data['seek_count'],
            ip_address=data['ip_address'],
            geographic_location=data['geographic_location'],
            isp=data['isp'],
            bandwidth_mbps=data['bandwidth_mbps'],
            segments_watched=set(data['segments_watched'])
        )
        
        if data['peak_concurrent_time']:
            session.peak_concurrent_time = datetime.fromisoformat(data['peak_concurrent_time'])
        
        return session

class RocksDBStateBackend(StateBackend):
    """RocksDB-based state backend for persistent storage"""
    
    def __init__(self, db_path: str = "/tmp/ipl_sessions_rocksdb"):
        self.db_path = db_path
        self.db = rocksdb.DB(db_path, rocksdb.Options(create_if_missing=True))
        
    def save_session(self, session: UserSession) -> bool:
        try:
            key = f"session:{session.session_id}".encode('utf-8')
            value = pickle.dumps(session)
            self.db.put(key, value)
            
            # Index by user
            user_key = f"user:{session.user_id}".encode('utf-8')
            existing_sessions = self.db.get(user_key)
            
            session_ids = set()
            if existing_sessions:
                session_ids = pickle.loads(existing_sessions)
            
            session_ids.add(session.session_id)
            self.db.put(user_key, pickle.dumps(session_ids))
            
            return True
        except Exception as e:
            print(f"❌ RocksDB save error: {str(e)}")
            return False
    
    def load_session(self, session_id: str) -> Optional[UserSession]:
        try:
            key = f"session:{session_id}".encode('utf-8')
            value = self.db.get(key)
            
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"❌ RocksDB load error: {str(e)}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        try:
            session = self.load_session(session_id)
            if session:
                # Remove from user index
                user_key = f"user:{session.user_id}".encode('utf-8')
                existing_sessions = self.db.get(user_key)
                
                if existing_sessions:
                    session_ids = pickle.loads(existing_sessions)
                    session_ids.discard(session_id)
                    self.db.put(user_key, pickle.dumps(session_ids))
            
            # Delete session
            key = f"session:{session_id}".encode('utf-8')
            self.db.delete(key)
            return True
        except Exception as e:
            print(f"❌ RocksDB delete error: {str(e)}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        try:
            user_key = f"user:{user_id}".encode('utf-8')
            session_ids_data = self.db.get(user_key)
            
            if not session_ids_data:
                return []
            
            session_ids = pickle.loads(session_ids_data)
            sessions = []
            
            for session_id in session_ids:
                session = self.load_session(session_id)
                if session:
                    sessions.append(session)
            
            return sessions
        except Exception as e:
            print(f"❌ RocksDB get user sessions error: {str(e)}")
            return []

class UserSessionManager:
    """Main session manager with state management"""
    
    def __init__(self, state_backend: StateBackend):
        self.state_backend = state_backend
        self.active_sessions: Dict[str, UserSession] = {}  # In-memory cache
        self.session_lock = threading.RLock()
        self.cleanup_thread = None
        self.stats = {
            'total_sessions': 0,
            'active_sessions': 0,
            'device_migrations': 0,
            'session_timeouts': 0
        }
        
        # Session configuration
        self.session_timeout = timedelta(minutes=30)  # 30 minutes inactivity timeout
        self.max_concurrent_sessions_per_user = 3
        
        print("🎯 User Session Manager initialized with state backend")
    
    def create_session(self, user_id: str, match_id: str, device_info: DeviceInfo, 
                      preferences: ViewingPreferences = None) -> UserSession:
        """Create new user session"""
        
        with self.session_lock:
            # Check existing sessions for user
            existing_sessions = self.get_active_user_sessions(user_id)
            
            # Limit concurrent sessions
            if len(existing_sessions) >= self.max_concurrent_sessions_per_user:
                # Expire oldest session
                oldest_session = min(existing_sessions, key=lambda s: s.last_activity)
                self.expire_session(oldest_session.session_id, "MAX_SESSIONS_EXCEEDED")
            
            # Generate session ID
            session_id = self._generate_session_id(user_id, device_info.device_id)
            
            # Check for device migration (same user, same device, different session)
            migrated_session = self._check_device_migration(user_id, device_info.device_id)
            if migrated_session:
                # Continue from previous position
                current_position = migrated_session.current_position
                preferences = migrated_session.preferences
                self.stats['device_migrations'] += 1
                print(f"🔄 Device migration detected for user {user_id}")
            else:
                current_position = 0
                if not preferences:
                    preferences = ViewingPreferences()
            
            # Create new session
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                match_id=match_id,
                state=SessionState.ACTIVE,
                start_time=datetime.now(),
                last_activity=datetime.now(),
                device_info=device_info,
                current_position=current_position,
                viewing_quality=preferences.preferred_quality,
                preferences=preferences
            )
            
            # Save to backend and cache
            self._save_session(session)
            self.active_sessions[session_id] = session
            self.stats['total_sessions'] += 1
            self.stats['active_sessions'] += 1
            
            print(f"✅ Session created: {session_id} for user {user_id} on {device_info.device_type}")
            return session
    
    def update_session(self, session_id: str, **updates) -> bool:
        """Update session with new data"""
        
        with self.session_lock:
            session = self._get_session(session_id)
            if not session or session.state == SessionState.EXPIRED:
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            # Always update last activity
            session.last_activity = datetime.now()
            
            # Save updated session
            self._save_session(session)
            
            return True
    
    def pause_session(self, session_id: str) -> bool:
        """Pause user session"""
        return self.update_session(session_id, 
                                 state=SessionState.PAUSED, 
                                 pause_count=lambda s: s.pause_count + 1)
    
    def resume_session(self, session_id: str) -> bool:
        """Resume paused session"""
        return self.update_session(session_id, state=SessionState.ACTIVE)
    
    def seek_session(self, session_id: str, position: int) -> bool:
        """Update playback position"""
        with self.session_lock:
            session = self._get_session(session_id)
            if session:
                return self.update_session(session_id, 
                                         current_position=position,
                                         seek_count=session.seek_count + 1)
            return False
    
    def change_quality(self, session_id: str, quality: QualityLevel) -> bool:
        """Change video quality"""
        with self.session_lock:
            session = self._get_session(session_id)
            if session:
                return self.update_session(session_id,
                                         viewing_quality=quality,
                                         quality_changes=session.quality_changes + 1)
            return False
    
    def report_buffer_event(self, session_id: str) -> bool:
        """Report buffering event"""
        with self.session_lock:
            session = self._get_session(session_id)
            if session:
                return self.update_session(session_id,
                                         buffer_events=session.buffer_events + 1)
            return False
    
    def update_watch_progress(self, session_id: str, position: int, duration: int) -> bool:
        """Update watch progress and segments"""
        with self.session_lock:
            session = self._get_session(session_id)
            if not session:
                return False
            
            # Calculate 30-second segment
            segment = position // 30
            session.segments_watched.add(segment)
            
            # Update watch duration
            if position > session.current_position:
                session.watch_duration += position - session.current_position
            
            return self.update_session(session_id, 
                                     current_position=position,
                                     segments_watched=session.segments_watched,
                                     watch_duration=session.watch_duration)
    
    def expire_session(self, session_id: str, reason: str = "TIMEOUT") -> bool:
        """Expire a session"""
        
        with self.session_lock:
            session = self._get_session(session_id)
            if not session:
                return False
            
            session.state = SessionState.EXPIRED
            
            # Save final state
            self._save_session(session)
            
            # Remove from active cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                self.stats['active_sessions'] -= 1
            
            if reason == "TIMEOUT":
                self.stats['session_timeouts'] += 1
            
            print(f"⏰ Session expired: {session_id} (Reason: {reason})")
            return True
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        return self._get_session(session_id)
    
    def get_active_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all active sessions for a user"""
        sessions = self.state_backend.get_user_sessions(user_id)
        return [s for s in sessions if s.state == SessionState.ACTIVE]
    
    def get_session_analytics(self, session_id: str) -> Dict:
        """Get detailed analytics for a session"""
        session = self._get_session(session_id)
        if not session:
            return {}
        
        total_duration = (datetime.now() - session.start_time).total_seconds()
        watch_percentage = (session.watch_duration / total_duration * 100) if total_duration > 0 else 0
        
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'total_duration_minutes': total_duration / 60,
            'watch_duration_minutes': session.watch_duration / 60,
            'watch_percentage': round(watch_percentage, 2),
            'segments_watched': len(session.segments_watched),
            'buffer_events': session.buffer_events,
            'quality_changes': session.quality_changes,
            'pause_count': session.pause_count,
            'seek_count': session.seek_count,
            'current_quality': session.viewing_quality.value,
            'device_type': session.device_info.device_type,
            'geographic_location': session.geographic_location,
            'engagement_score': self._calculate_engagement_score(session)
        }
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (run periodically)"""
        current_time = datetime.now()
        expired_sessions = []
        
        with self.session_lock:
            for session_id, session in list(self.active_sessions.items()):
                # Check for timeout
                if (current_time - session.last_activity) > self.session_timeout:
                    expired_sessions.append(session_id)
        
        # Expire timed out sessions
        for session_id in expired_sessions:
            self.expire_session(session_id, "TIMEOUT")
        
        print(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    def start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_loop():
            while True:
                time.sleep(300)  # Run every 5 minutes
                try:
                    self.cleanup_expired_sessions()
                except Exception as e:
                    print(f"❌ Cleanup error: {str(e)}")
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        print("🧹 Session cleanup thread started")
    
    def get_stats(self) -> Dict:
        """Get session manager statistics"""
        with self.session_lock:
            active_count = len([s for s in self.active_sessions.values() 
                              if s.state == SessionState.ACTIVE])
            
            return {
                **self.stats,
                'current_active_sessions': active_count,
                'cached_sessions': len(self.active_sessions)
            }
    
    def _get_session(self, session_id: str) -> Optional[UserSession]:
        """Internal method to get session from cache or backend"""
        
        # Try cache first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Load from backend
        session = self.state_backend.load_session(session_id)
        if session and session.state != SessionState.EXPIRED:
            self.active_sessions[session_id] = session
            return session
        
        return None
    
    def _save_session(self, session: UserSession):
        """Save session to backend"""
        self.state_backend.save_session(session)
        if session.session_id in self.active_sessions:
            self.active_sessions[session.session_id] = session
    
    def _generate_session_id(self, user_id: str, device_id: str) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time()))
        unique_string = f"{user_id}:{device_id}:{timestamp}:{uuid.uuid4()}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _check_device_migration(self, user_id: str, device_id: str) -> Optional[UserSession]:
        """Check for device migration scenario"""
        sessions = self.get_active_user_sessions(user_id)
        
        for session in sessions:
            if (session.device_info.device_id == device_id and 
                session.state in [SessionState.INACTIVE, SessionState.PAUSED]):
                return session
        
        return None
    
    def _calculate_engagement_score(self, session: UserSession) -> float:
        """Calculate engagement score (0-100)"""
        score = 0.0
        
        # Base score from watch duration
        if session.watch_duration > 0:
            total_time = (datetime.now() - session.start_time).total_seconds()
            watch_ratio = session.watch_duration / max(total_time, 1)
            score += min(watch_ratio * 40, 40)  # Max 40 points
        
        # Segments continuity (watching without gaps)
        if session.segments_watched:
            continuity = len(session.segments_watched) / (max(session.segments_watched) + 1)
            score += continuity * 20  # Max 20 points
        
        # Low buffer events = good experience
        if session.buffer_events < 5:
            score += 20
        elif session.buffer_events < 10:
            score += 10
        
        # Quality stability
        if session.quality_changes < 3:
            score += 10
        elif session.quality_changes < 6:
            score += 5
        
        # Active engagement (seeks, pauses indicate engagement)
        engagement_actions = session.seek_count + session.pause_count
        if engagement_actions > 0:
            score += min(engagement_actions * 2, 10)  # Max 10 points
        
        return min(score, 100.0)

def process_session_events(session_manager: UserSessionManager):
    """Process session events from Kafka"""
    
    consumer = KafkaConsumer(
        'ipl-user-sessions',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='session-manager',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    print("📡 Processing session events from Kafka...")
    
    for message in consumer:
        event_data = message.value
        event_type = event_data.get('event_type')
        session_id = event_data.get('session_id')
        
        try:
            if event_type == 'SESSION_START':
                # Create new session
                device_info = DeviceInfo(**event_data['device_info'])
                preferences = ViewingPreferences(**event_data.get('preferences', {}))
                
                session = session_manager.create_session(
                    user_id=event_data['user_id'],
                    match_id=event_data['match_id'],
                    device_info=device_info,
                    preferences=preferences
                )
                print(f"📱 New session started: {session.session_id}")
                
            elif event_type == 'HEARTBEAT':
                # Update last activity
                session_manager.update_session(session_id)
                
            elif event_type == 'PAUSE':
                session_manager.pause_session(session_id)
                print(f"⏸️ Session paused: {session_id}")
                
            elif event_type == 'RESUME':
                session_manager.resume_session(session_id)
                print(f"▶️ Session resumed: {session_id}")
                
            elif event_type == 'SEEK':
                position = event_data.get('position', 0)
                session_manager.seek_session(session_id, position)
                print(f"⏩ Seek to position {position}: {session_id}")
                
            elif event_type == 'QUALITY_CHANGE':
                quality = QualityLevel(event_data.get('quality'))
                session_manager.change_quality(session_id, quality)
                print(f"🎥 Quality changed to {quality.value}: {session_id}")
                
            elif event_type == 'BUFFER':
                session_manager.report_buffer_event(session_id)
                print(f"🔄 Buffer event: {session_id}")
                
            elif event_type == 'PROGRESS':
                position = event_data.get('position', 0)
                duration = event_data.get('duration', 0)
                session_manager.update_watch_progress(session_id, position, duration)
                
            elif event_type == 'SESSION_END':
                session_manager.expire_session(session_id, "USER_ENDED")
                print(f"🛑 Session ended: {session_id}")
                
        except Exception as e:
            print(f"❌ Error processing event {event_type}: {str(e)}")

def generate_sample_session_events():
    """Generate sample session events for testing"""
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
    )
    
    users = ["user_1", "user_2", "user_3"]
    devices = ["mobile_123", "tv_456", "desktop_789"]
    match_id = "MI_vs_CSK_State_Test"
    
    print("🎬 Generating sample session events...")
    
    # Start sessions
    for i, user_id in enumerate(users):
        device_info = {
            'device_id': devices[i],
            'device_type': ['MOBILE', 'TV', 'DESKTOP'][i],
            'os_type': ['Android', 'Android_TV', 'Web'][i],
            'app_version': '2.5.0',
            'screen_resolution': ['1080x1920', '3840x2160', '1920x1080'][i],
            'network_type': ['4G', 'WIFI', 'WIFI'][i]
        }
        
        preferences = {
            'preferred_quality': ['720p', '4K', '1080p'][i],
            'preferred_language': 'Hindi',
            'notifications_enabled': True,
            'autoplay_enabled': True,
            'data_saver_mode': i == 0,  # Only mobile user
            'preferred_commentary': 'Hindi'
        }
        
        start_event = {
            'event_type': 'SESSION_START',
            'user_id': user_id,
            'match_id': match_id,
            'device_info': device_info,
            'preferences': preferences,
            'timestamp': datetime.now().isoformat()
        }
        
        producer.send('ipl-user-sessions', value=start_event)
        print(f"📤 Session start event for {user_id}")
        time.sleep(1)
    
    # Simulate session activity
    session_ids = []  # In real scenario, we'd get these from session creation response
    
    for i in range(10):  # 10 activity events
        for j, user_id in enumerate(users):
            session_id = f"session_{user_id}_{j}"  # Mock session ID
            session_ids.append(session_id)
            
            # Random activity
            events = ['HEARTBEAT', 'SEEK', 'QUALITY_CHANGE', 'BUFFER', 'PROGRESS']
            event_type = events[i % len(events)]
            
            event = {
                'event_type': event_type,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add event-specific data
            if event_type == 'SEEK':
                event['position'] = (i + 1) * 30  # Seek to different positions
            elif event_type == 'QUALITY_CHANGE':
                event['quality'] = ['480p', '720p', '1080p'][i % 3]
            elif event_type == 'PROGRESS':
                event['position'] = (i + 1) * 15
                event['duration'] = 7200  # 2-hour match
            
            producer.send('ipl-user-sessions', value=event)
            
        time.sleep(2)
    
    producer.flush()
    print("✅ Sample session events generated!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-data":
        generate_sample_session_events()
    else:
        # Choose state backend
        backend_type = "redis"  # redis or rocksdb
        
        if backend_type == "redis":
            state_backend = RedisStateBackend()
        else:
            state_backend = RocksDBStateBackend()
        
        # Create session manager
        session_manager = UserSessionManager(state_backend)
        
        # Start cleanup thread
        session_manager.start_cleanup_thread()
        
        # Start processing events
        try:
            process_session_events(session_manager)
        except KeyboardInterrupt:
            print("\n🛑 Stopping session manager...")
            final_stats = session_manager.get_stats()
            print(f"📊 Final Statistics: {final_stats}")
            print("✅ Session manager stopped gracefully")