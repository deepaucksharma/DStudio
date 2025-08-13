#!/usr/bin/env python3
"""
Database Connection Pool System - Episode 50: System Design Interview Mastery
IRCTC Database Connection Management System

Database connection pool जैसे Mumbai local train का coach system है।
Limited coaches हैं, efficiently use करके maximum passengers को serve करना है।

Author: Hindi Podcast Series
Topic: Database Connection Pooling with Indian Banking Context
"""

import time
import threading
import queue
import sqlite3
import psycopg2
import pymongo
from contextlib import contextmanager
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta
import json
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Database types supported"""
    POSTGRESQL = "postgresql"     # IRCTC main database
    MYSQL = "mysql"              # Flipkart product catalog
    MONGODB = "mongodb"          # Zomato restaurant data
    SQLITE = "sqlite"           # Local development
    REDIS = "redis"             # Session cache

class ConnectionState(Enum):
    """Database connection states"""
    IDLE = "idle"               # Available for use
    ACTIVE = "active"           # Currently in use
    STALE = "stale"            # Connection is old/suspect
    BROKEN = "broken"          # Connection failed

@dataclass
class ConnectionConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    db_type: DatabaseType
    connection_timeout: int = 30
    max_lifetime: int = 3600    # 1 hour max connection life
    validation_query: str = "SELECT 1"
    ssl_enabled: bool = True
    
    def get_connection_string(self) -> str:
        """Generate connection string based on DB type"""
        if self.db_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == DatabaseType.MYSQL:
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == DatabaseType.MONGODB:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        return ""

@dataclass
class PooledConnection:
    """Pooled database connection wrapper"""
    connection: Any
    created_at: float
    last_used: float
    use_count: int = 0
    state: ConnectionState = ConnectionState.IDLE
    validation_failures: int = 0
    
    def is_expired(self, max_lifetime: int) -> bool:
        """Check if connection has exceeded max lifetime"""
        return time.time() - self.created_at > max_lifetime
    
    def is_stale(self, max_idle_time: int = 300) -> bool:
        """Check if connection has been idle too long (5 minutes default)"""
        return time.time() - self.last_used > max_idle_time
    
    def mark_used(self):
        """Mark connection as recently used"""
        self.last_used = time.time()
        self.use_count += 1
        self.state = ConnectionState.ACTIVE
    
    def mark_idle(self):
        """Mark connection as idle"""
        self.state = ConnectionState.IDLE
    
    def mark_broken(self):
        """Mark connection as broken"""
        self.state = ConnectionState.BROKEN

class ConnectionPool:
    """Database Connection Pool - IRCTC Style Resource Management"""
    
    def __init__(self, 
                 config: ConnectionConfig,
                 min_connections: int = 5,
                 max_connections: int = 50,
                 max_idle_connections: int = 10):
        """
        Initialize connection pool
        min_connections: Minimum connections to maintain
        max_connections: Maximum connections allowed  
        max_idle_connections: Maximum idle connections
        """
        self.config = config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_idle_connections = max_idle_connections
        
        # Connection pools
        self.idle_connections: queue.Queue[PooledConnection] = queue.Queue()
        self.active_connections: Dict[int, PooledConnection] = {}
        self.broken_connections: List[PooledConnection] = []
        
        # Synchronization
        self.lock = threading.RLock()
        self.connection_semaphore = threading.Semaphore(max_connections)
        
        # Statistics
        self.stats = {
            'connections_created': 0,
            'connections_destroyed': 0,
            'connections_borrowed': 0,
            'connections_returned': 0,
            'validation_failures': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'active_connections': 0,
            'idle_connections': 0
        }
        
        # Background maintenance
        self.maintenance_thread = None
        self.running = True
        
        # Initialize minimum connections
        self._initialize_pool()
        self._start_maintenance()
        
        print(f"🏊 Connection Pool initialized for {config.db_type.value}")
        print(f"   Min: {min_connections}, Max: {max_connections}, Max Idle: {max_idle_connections}")
    
    def _initialize_pool(self):
        """Initialize pool with minimum connections"""
        for i in range(self.min_connections):
            try:
                conn = self._create_connection()
                if conn:
                    pooled_conn = PooledConnection(
                        connection=conn,
                        created_at=time.time(),
                        last_used=time.time()
                    )
                    self.idle_connections.put(pooled_conn)
                    self.stats['connections_created'] += 1
            except Exception as e:
                logger.error(f"Failed to create initial connection {i}: {e}")
    
    def _create_connection(self) -> Optional[Any]:
        """Create new database connection"""
        try:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                return psycopg2.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.username,
                    password=self.config.password,
                    connect_timeout=self.config.connection_timeout
                )
            elif self.config.db_type == DatabaseType.SQLITE:
                # For demo purposes, use SQLite
                return sqlite3.connect(
                    f"{self.config.database}.db",
                    timeout=self.config.connection_timeout
                )
            elif self.config.db_type == DatabaseType.MONGODB:
                from pymongo import MongoClient
                client = MongoClient(
                    host=self.config.host,
                    port=self.config.port,
                    username=self.config.username,
                    password=self.config.password,
                    serverSelectionTimeoutMS=self.config.connection_timeout * 1000
                )
                return client[self.config.database]
            else:
                # Simulate connection for unsupported types
                return {"type": self.config.db_type.value, "connected": True}
        
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None
    
    def get_connection(self, timeout: float = 30.0) -> Optional[PooledConnection]:
        """Get connection from pool - Train coach allocation"""
        start_time = time.time()
        
        # Acquire semaphore (blocks if max connections reached)
        if not self.connection_semaphore.acquire(timeout=timeout):
            logger.warning("Connection pool exhausted - no connections available")
            return None
        
        try:
            with self.lock:
                # Try to get idle connection first
                if not self.idle_connections.empty():
                    pooled_conn = self.idle_connections.get_nowait()
                    
                    # Validate connection before returning
                    if self._validate_connection(pooled_conn):
                        pooled_conn.mark_used()
                        self.active_connections[id(pooled_conn)] = pooled_conn
                        self.stats['connections_borrowed'] += 1
                        self.stats['pool_hits'] += 1
                        logger.debug(f"Connection borrowed from pool (validation passed)")
                        return pooled_conn
                    else:
                        # Connection is broken, destroy it
                        self._destroy_connection(pooled_conn)
                        self.stats['validation_failures'] += 1
                
                # No valid idle connections, create new one
                if len(self.active_connections) < self.max_connections:
                    conn = self._create_connection()
                    if conn:
                        pooled_conn = PooledConnection(
                            connection=conn,
                            created_at=time.time(),
                            last_used=time.time()
                        )
                        pooled_conn.mark_used()
                        self.active_connections[id(pooled_conn)] = pooled_conn
                        self.stats['connections_created'] += 1
                        self.stats['connections_borrowed'] += 1
                        self.stats['pool_misses'] += 1
                        logger.debug(f"New connection created")
                        return pooled_conn
                
                # No connections available
                logger.warning("Unable to create new connection")
                return None
        
        finally:
            elapsed = time.time() - start_time
            if elapsed > 1.0:  # Log slow connection acquisitions
                logger.warning(f"Slow connection acquisition: {elapsed:.2f}s")
    
    def return_connection(self, pooled_conn: PooledConnection, force_close: bool = False):
        """Return connection to pool - Train coach के वापस करना"""
        if not pooled_conn:
            return
        
        try:
            with self.lock:
                conn_id = id(pooled_conn)
                
                # Remove from active connections
                if conn_id in self.active_connections:
                    del self.active_connections[conn_id]
                
                if force_close or pooled_conn.state == ConnectionState.BROKEN:
                    # Destroy broken connection
                    self._destroy_connection(pooled_conn)
                    self.stats['connections_destroyed'] += 1
                elif (pooled_conn.is_expired(self.config.max_lifetime) or
                      self.idle_connections.qsize() >= self.max_idle_connections):
                    # Destroy expired or excess connections
                    self._destroy_connection(pooled_conn)
                    self.stats['connections_destroyed'] += 1
                else:
                    # Return to idle pool
                    pooled_conn.mark_idle()
                    self.idle_connections.put(pooled_conn)
                    self.stats['connections_returned'] += 1
                    logger.debug(f"Connection returned to pool")
        
        finally:
            # Always release semaphore
            self.connection_semaphore.release()
    
    def _validate_connection(self, pooled_conn: PooledConnection) -> bool:
        """Validate database connection"""
        try:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                cursor = pooled_conn.connection.cursor()
                cursor.execute(self.config.validation_query)
                cursor.close()
                return True
            elif self.config.db_type == DatabaseType.SQLITE:
                cursor = pooled_conn.connection.cursor()
                cursor.execute(self.config.validation_query)
                cursor.close()
                return True
            elif self.config.db_type == DatabaseType.MONGODB:
                # Ping MongoDB
                pooled_conn.connection.command('ping')
                return True
            else:
                # Simulate validation for demo
                return pooled_conn.connection.get('connected', False)
        
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            pooled_conn.validation_failures += 1
            return False
    
    def _destroy_connection(self, pooled_conn: PooledConnection):
        """Destroy database connection"""
        try:
            if self.config.db_type in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE]:
                pooled_conn.connection.close()
            elif self.config.db_type == DatabaseType.MONGODB:
                pooled_conn.connection.client.close()
            # For simulated connections, just mark as destroyed
            pooled_conn.state = ConnectionState.BROKEN
            logger.debug(f"Connection destroyed")
        except Exception as e:
            logger.error(f"Error destroying connection: {e}")
    
    def _start_maintenance(self):
        """Start background maintenance thread"""
        self.maintenance_thread = threading.Thread(target=self._maintenance_loop)
        self.maintenance_thread.daemon = True
        self.maintenance_thread.start()
        logger.info("Connection pool maintenance started")
    
    def _maintenance_loop(self):
        """Background maintenance loop"""
        while self.running:
            try:
                time.sleep(60)  # Run every minute
                self._perform_maintenance()
            except Exception as e:
                logger.error(f"Maintenance error: {e}")
    
    def _perform_maintenance(self):
        """Perform pool maintenance - Remove stale/expired connections"""
        with self.lock:
            current_time = time.time()
            stale_connections = []
            
            # Check idle connections
            idle_count = self.idle_connections.qsize()
            for _ in range(idle_count):
                try:
                    pooled_conn = self.idle_connections.get_nowait()
                    
                    if (pooled_conn.is_expired(self.config.max_lifetime) or
                        pooled_conn.is_stale(300)):  # 5 minutes idle
                        stale_connections.append(pooled_conn)
                    else:
                        self.idle_connections.put(pooled_conn)
                except queue.Empty:
                    break
            
            # Destroy stale connections
            for conn in stale_connections:
                self._destroy_connection(conn)
                self.stats['connections_destroyed'] += 1
            
            # Ensure minimum connections
            current_idle = self.idle_connections.qsize()
            if current_idle < self.min_connections:
                needed = self.min_connections - current_idle
                for _ in range(needed):
                    conn = self._create_connection()
                    if conn:
                        pooled_conn = PooledConnection(
                            connection=conn,
                            created_at=current_time,
                            last_used=current_time
                        )
                        self.idle_connections.put(pooled_conn)
                        self.stats['connections_created'] += 1
            
            logger.debug(f"Maintenance completed - Removed {len(stale_connections)} stale connections")
    
    @contextmanager
    def get_connection_context(self, timeout: float = 30.0):
        """Context manager for automatic connection management"""
        conn = None
        try:
            conn = self.get_connection(timeout=timeout)
            if conn:
                yield conn.connection
            else:
                raise Exception("Unable to acquire database connection")
        except Exception as e:
            if conn:
                self.return_connection(conn, force_close=True)
            raise e
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_pool_stats(self) -> Dict:
        """Get connection pool statistics"""
        with self.lock:
            return {
                **self.stats,
                'active_connections': len(self.active_connections),
                'idle_connections': self.idle_connections.qsize(),
                'total_connections': len(self.active_connections) + self.idle_connections.qsize(),
                'max_connections': self.max_connections,
                'min_connections': self.min_connections,
                'pool_utilization': (len(self.active_connections) / self.max_connections) * 100
            }
    
    def shutdown(self):
        """Shutdown connection pool"""
        self.running = False
        
        with self.lock:
            # Close all active connections
            for conn in list(self.active_connections.values()):
                self._destroy_connection(conn)
            self.active_connections.clear()
            
            # Close all idle connections
            while not self.idle_connections.empty():
                try:
                    conn = self.idle_connections.get_nowait()
                    self._destroy_connection(conn)
                except queue.Empty:
                    break
        
        if self.maintenance_thread and self.maintenance_thread.is_alive():
            self.maintenance_thread.join(timeout=5)
        
        logger.info("Connection pool shutdown completed")

class IRCTCConnectionManager:
    """IRCTC-style multi-database connection manager"""
    
    def __init__(self):
        """Initialize IRCTC database connections"""
        # Different databases for different services
        self.database_configs = {
            # Main IRCTC user database (PostgreSQL)
            'user_db': ConnectionConfig(
                host='irctc-user-db.railway.gov.in',
                port=5432,
                database='irctc_users',
                username='irctc_app',
                password='secure_password_123',
                db_type=DatabaseType.POSTGRESQL
            ),
            
            # Train schedule database (PostgreSQL)
            'schedule_db': ConnectionConfig(
                host='irctc-schedule-db.railway.gov.in', 
                port=5432,
                database='train_schedules',
                username='schedule_reader',
                password='schedule_pass_456',
                db_type=DatabaseType.POSTGRESQL
            ),
            
            # Booking transactions (PostgreSQL with high concurrency)
            'booking_db': ConnectionConfig(
                host='irctc-booking-db.railway.gov.in',
                port=5432, 
                database='bookings',
                username='booking_service',
                password='booking_secure_789',
                db_type=DatabaseType.POSTGRESQL
            ),
            
            # Session cache (Redis simulation)
            'session_cache': ConnectionConfig(
                host='irctc-redis.railway.gov.in',
                port=6379,
                database='sessions',
                username='redis_user',
                password='redis_pass_000',
                db_type=DatabaseType.SQLITE  # Using SQLite for demo
            )
        }
        
        # Initialize connection pools
        self.pools: Dict[str, ConnectionPool] = {}
        
        # Different pool configurations for different workloads
        pool_configs = {
            'user_db': {'min': 10, 'max': 100, 'max_idle': 20},      # Medium load
            'schedule_db': {'min': 5, 'max': 50, 'max_idle': 15},   # Read-heavy
            'booking_db': {'min': 20, 'max': 200, 'max_idle': 40},  # High load
            'session_cache': {'min': 5, 'max': 30, 'max_idle': 10}  # Cache operations
        }
        
        for db_name, config in self.database_configs.items():
            pool_config = pool_configs[db_name]
            self.pools[db_name] = ConnectionPool(
                config=config,
                min_connections=pool_config['min'],
                max_connections=pool_config['max'],
                max_idle_connections=pool_config['max_idle']
            )
        
        print("🚂 IRCTC Connection Manager initialized")
        print(f"   Databases: {len(self.pools)}")
        for db_name, pool in self.pools.items():
            stats = pool.get_pool_stats()
            print(f"   {db_name}: {stats['total_connections']} connections")
    
    def get_user_database(self):
        """Get user database connection"""
        return self.pools['user_db'].get_connection_context()
    
    def get_schedule_database(self):
        """Get schedule database connection"""
        return self.pools['schedule_db'].get_connection_context()
    
    def get_booking_database(self):
        """Get booking database connection"""
        return self.pools['booking_db'].get_connection_context()
    
    def get_session_cache(self):
        """Get session cache connection"""
        return self.pools['session_cache'].get_connection_context()
    
    def simulate_user_login(self, user_id: str) -> Dict:
        """Simulate user login process using multiple databases"""
        start_time = time.time()
        
        try:
            # 1. Authenticate user (user_db)
            with self.get_user_database() as user_conn:
                # Simulate user authentication query
                time.sleep(0.1)  # Database query time
                user_data = {
                    'user_id': user_id,
                    'name': f'User_{user_id}',
                    'status': 'active',
                    'last_login': datetime.now().isoformat()
                }
            
            # 2. Create session (session_cache)
            with self.get_session_cache() as cache_conn:
                # Simulate session creation
                time.sleep(0.05)
                session_id = f"session_{int(time.time())}_{user_id}"
            
            # 3. Get recent bookings (booking_db)
            with self.get_booking_database() as booking_conn:
                # Simulate booking history query
                time.sleep(0.15)
                recent_bookings = [
                    {'pnr': f'PNR{i}', 'train': f'Train_{i}', 'date': '2024-01-15'}
                    for i in range(3)
                ]
            
            login_time = time.time() - start_time
            
            return {
                'success': True,
                'user_data': user_data,
                'session_id': session_id,
                'recent_bookings': recent_bookings,
                'login_time_ms': login_time * 1000
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'login_time_ms': (time.time() - start_time) * 1000
            }
    
    def simulate_train_search(self, from_station: str, to_station: str) -> Dict:
        """Simulate train search using schedule database"""
        start_time = time.time()
        
        try:
            with self.get_schedule_database() as schedule_conn:
                # Simulate train search query
                time.sleep(0.2)  # Complex search query
                
                trains = [
                    {
                        'train_number': '12951',
                        'train_name': 'Mumbai Rajdhani',
                        'departure': '16:35',
                        'arrival': '08:35+1',
                        'duration': '16:00',
                        'available_seats': {
                            '3AC': 45,
                            '2AC': 23,
                            '1AC': 12,
                            'SL': 120
                        }
                    },
                    {
                        'train_number': '12953',
                        'train_name': 'August Kranti Rajdhani',
                        'departure': '17:55',
                        'arrival': '09:55+1',
                        'duration': '16:00',
                        'available_seats': {
                            '3AC': 38,
                            '2AC': 19,
                            '1AC': 8,
                            'SL': 95
                        }
                    }
                ]
            
            search_time = time.time() - start_time
            
            return {
                'success': True,
                'from_station': from_station,
                'to_station': to_station,
                'trains': trains,
                'search_time_ms': search_time * 1000
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'search_time_ms': (time.time() - start_time) * 1000
            }
    
    def get_cluster_stats(self) -> Dict:
        """Get overall connection cluster statistics"""
        cluster_stats = {
            'total_pools': len(self.pools),
            'pool_stats': {},
            'aggregate_stats': {
                'total_connections': 0,
                'active_connections': 0,
                'idle_connections': 0,
                'connections_created': 0,
                'connections_destroyed': 0
            }
        }
        
        for db_name, pool in self.pools.items():
            stats = pool.get_pool_stats()
            cluster_stats['pool_stats'][db_name] = stats
            
            # Aggregate statistics
            cluster_stats['aggregate_stats']['total_connections'] += stats['total_connections']
            cluster_stats['aggregate_stats']['active_connections'] += stats['active_connections']
            cluster_stats['aggregate_stats']['idle_connections'] += stats['idle_connections']
            cluster_stats['aggregate_stats']['connections_created'] += stats['connections_created']
            cluster_stats['aggregate_stats']['connections_destroyed'] += stats['connections_destroyed']
        
        return cluster_stats
    
    def shutdown(self):
        """Shutdown all connection pools"""
        for db_name, pool in self.pools.items():
            print(f"Shutting down {db_name} pool...")
            pool.shutdown()
        print("✅ All connection pools shutdown completed")

def demonstrate_connection_pool():
    """Demonstrate basic connection pool functionality"""
    print("🏊 Connection Pool Demo - IRCTC Database Pool")
    print("=" * 55)
    
    # Create SQLite config for demo
    config = ConnectionConfig(
        host='localhost',
        port=5432,
        database='demo_irctc',
        username='test_user',
        password='test_pass',
        db_type=DatabaseType.SQLITE
    )
    
    # Create connection pool
    pool = ConnectionPool(
        config=config,
        min_connections=3,
        max_connections=10,
        max_idle_connections=5
    )
    
    print(f"\n📊 Initial Pool Stats:")
    stats = pool.get_pool_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Simulate concurrent usage
    print(f"\n⚡ Simulating Concurrent Database Usage:")
    print("-" * 45)
    
    def worker_thread(worker_id: int, operations: int):
        """Simulate worker thread using database connections"""
        for i in range(operations):
            try:
                with pool.get_connection_context(timeout=5.0) as conn:
                    # Simulate database work
                    if hasattr(conn, 'execute'):
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()
                        cursor.close()
                    time.sleep(0.1)  # Simulate work
                    
                if i % 5 == 0:
                    print(f"   Worker {worker_id}: Completed {i+1}/{operations} operations")
            
            except Exception as e:
                print(f"   Worker {worker_id}: Error - {e}")
    
    # Start multiple worker threads
    import threading
    
    workers = []
    for i in range(5):
        worker = threading.Thread(target=worker_thread, args=(i, 10))
        workers.append(worker)
        worker.start()
    
    # Wait for all workers to complete
    for worker in workers:
        worker.join()
    
    print(f"\n📈 Final Pool Stats:")
    final_stats = pool.get_pool_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    # Cleanup
    pool.shutdown()
    
    return pool

def demonstrate_irctc_system():
    """Demonstrate IRCTC-style multi-database system"""
    print("\n🚂 IRCTC Multi-Database System Demo")
    print("=" * 50)
    
    # Initialize IRCTC connection manager
    irctc = IRCTCConnectionManager()
    
    # Simulate multiple user operations
    print(f"\n👥 Simulating User Operations:")
    print("-" * 35)
    
    users = ['user_9876543210', 'user_8765432109', 'user_7654321098']
    
    for user_id in users:
        # Simulate login
        login_result = irctc.simulate_user_login(user_id)
        if login_result['success']:
            print(f"✅ {user_id} login: {login_result['login_time_ms']:.1f}ms")
        else:
            print(f"❌ {user_id} login failed: {login_result['error']}")
    
    print(f"\n🔍 Simulating Train Searches:")
    print("-" * 35)
    
    # Simulate train searches
    search_queries = [
        ('MUMBAI', 'DELHI'),
        ('DELHI', 'BANGALORE'),
        ('CHENNAI', 'KOLKATA')
    ]
    
    for from_station, to_station in search_queries:
        search_result = irctc.simulate_train_search(from_station, to_station)
        if search_result['success']:
            train_count = len(search_result['trains'])
            print(f"🚆 {from_station} → {to_station}: {train_count} trains "
                  f"({search_result['search_time_ms']:.1f}ms)")
        else:
            print(f"❌ Search failed: {search_result['error']}")
    
    # Show cluster statistics
    print(f"\n📊 Cluster Statistics:")
    print("-" * 25)
    
    cluster_stats = irctc.get_cluster_stats()
    aggregate = cluster_stats['aggregate_stats']
    
    print(f"   Total Connections: {aggregate['total_connections']}")
    print(f"   Active Connections: {aggregate['active_connections']}")
    print(f"   Idle Connections: {aggregate['idle_connections']}")
    print(f"   Connections Created: {aggregate['connections_created']}")
    
    # Show per-database stats
    print(f"\n📋 Per-Database Statistics:")
    print("-" * 30)
    
    for db_name, stats in cluster_stats['pool_stats'].items():
        print(f"   {db_name}:")
        print(f"     Pool Utilization: {stats['pool_utilization']:.1f}%")
        print(f"     Connections Borrowed: {stats['connections_borrowed']}")
        print(f"     Pool Hit Rate: {(stats['pool_hits']/(stats['pool_hits']+stats['pool_misses'])*100) if (stats['pool_hits']+stats['pool_misses']) > 0 else 0:.1f}%")
    
    # Cleanup
    irctc.shutdown()
    
    return irctc

def demonstrate_high_load_scenario():
    """Demonstrate high load database scenario"""
    print("\n⚡ High Load Scenario - Tatkal Booking Rush")
    print("=" * 55)
    
    # Create high-capacity pool for Tatkal booking
    config = ConnectionConfig(
        host='localhost',
        port=5432, 
        database='tatkal_booking',
        username='tatkal_user',
        password='tatkal_secure',
        db_type=DatabaseType.SQLITE
    )
    
    # High-capacity pool for flash booking
    pool = ConnectionPool(
        config=config,
        min_connections=20,
        max_connections=100,
        max_idle_connections=30
    )
    
    print(f"🎯 Simulating Tatkal booking rush (100 concurrent users)...")
    
    # Simulate high concurrent load
    def tatkal_booking_user(user_id: int):
        """Simulate individual user trying to book Tatkal ticket"""
        try:
            with pool.get_connection_context(timeout=10.0) as conn:
                # Simulate booking logic
                booking_start = time.time()
                
                # Check seat availability
                time.sleep(0.05)
                
                # Lock seat
                time.sleep(0.1)
                
                # Process payment  
                time.sleep(0.15)
                
                # Confirm booking
                time.sleep(0.1)
                
                booking_time = time.time() - booking_start
                
                if user_id % 10 == 0:  # Show progress
                    print(f"   User {user_id}: Booking completed in {booking_time:.3f}s")
                
                return True
        
        except Exception as e:
            if user_id % 20 == 0:  # Show failures
                print(f"   User {user_id}: Booking failed - {e}")
            return False
    
    # Run concurrent booking simulation
    import concurrent.futures
    import threading
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(tatkal_booking_user, i) for i in range(100)]
        
        # Wait for all bookings to complete
        successful_bookings = 0
        failed_bookings = 0
        
        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result():
                    successful_bookings += 1
                else:
                    failed_bookings += 1
            except Exception:
                failed_bookings += 1
    
    total_time = time.time() - start_time
    
    print(f"\n📈 High Load Results:")
    print(f"   Total Users: 100")
    print(f"   Successful Bookings: {successful_bookings}")
    print(f"   Failed Bookings: {failed_bookings}")
    print(f"   Success Rate: {successful_bookings/100*100:.1f}%")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Throughput: {100/total_time:.1f} bookings/sec")
    
    # Final pool statistics
    final_stats = pool.get_pool_stats()
    print(f"\n📊 Pool Performance:")
    print(f"   Max Pool Utilization: {final_stats['pool_utilization']:.1f}%")
    print(f"   Total Connections Used: {final_stats['connections_borrowed']}")
    print(f"   Pool Hit Rate: {(final_stats['pool_hits']/(final_stats['pool_hits']+final_stats['pool_misses'])*100) if (final_stats['pool_hits']+final_stats['pool_misses']) > 0 else 0:.1f}%")
    
    pool.shutdown()

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_connection_pool()
    
    print("\n" + "="*80 + "\n")
    
    irctc_system = demonstrate_irctc_system()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_high_load_scenario()
    
    print(f"\n✅ Database Connection Pool Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Connection Pooling - Resource management and reuse")
    print(f"   • Pool Sizing - Min/max/idle connection configuration") 
    print(f"   • Connection Lifecycle - Creation, validation, destruction")
    print(f"   • Context Managers - Automatic resource cleanup")
    print(f"   • Multi-Database Management - Different pools per service")
    print(f"   • High Load Handling - Concurrent access management")
    print(f"   • Health Monitoring - Connection validation and maintenance")
    print(f"   • Indian Context - IRCTC, Tatkal booking, Indian databases")