#!/usr/bin/env python3
"""
Distributed Lock Manager System - Episode 50: System Design Interview Mastery
Zomato Restaurant Table Booking Lock System

Distributed lock जैसे restaurant table booking है।
एक time पर sirf एक customer को same table book करने देना है।

Author: Hindi Podcast Series
Topic: Distributed Locking with Indian Restaurant Booking Context
"""

import time
import threading
import random
import hashlib
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import uuid
from datetime import datetime, timedelta
from contextlib import contextmanager
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LockType(Enum):
    """Types of distributed locks"""
    EXCLUSIVE = "exclusive"        # Only one holder allowed
    SHARED = "shared"             # Multiple readers allowed
    REENTRANT = "reentrant"       # Same client can acquire multiple times

class LockState(Enum):
    """Lock states"""
    AVAILABLE = "available"        # Lock is free
    ACQUIRED = "acquired"         # Lock is held
    EXPIRED = "expired"           # Lock has expired
    RELEASED = "released"         # Lock was released

@dataclass
class LockInfo:
    """Information about a distributed lock"""
    lock_id: str
    resource: str
    holder_id: str
    lock_type: LockType
    acquired_at: float
    expires_at: float
    lease_duration: float
    reentrant_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if lock has expired"""
        return time.time() > self.expires_at
    
    def time_remaining(self) -> float:
        """Get remaining time before expiration"""
        return max(0, self.expires_at - time.time())
    
    def extend_lease(self, additional_time: float):
        """Extend lock lease"""
        self.expires_at += additional_time

@dataclass
class LockRequest:
    """Lock acquisition request"""
    resource: str
    client_id: str
    lock_type: LockType = LockType.EXCLUSIVE
    lease_duration: float = 30.0
    timeout: float = 10.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class DistributedLock:
    """Individual distributed lock representation"""
    
    def __init__(self, lock_manager, resource: str, client_id: str, 
                 lease_duration: float = 30.0, lock_type: LockType = LockType.EXCLUSIVE):
        """Initialize distributed lock"""
        self.lock_manager = lock_manager
        self.resource = resource
        self.client_id = client_id
        self.lease_duration = lease_duration
        self.lock_type = lock_type
        self.lock_info: Optional[LockInfo] = None
        self.is_acquired = False
    
    def acquire(self, timeout: float = 10.0, metadata: Dict = None) -> bool:
        """Acquire the distributed lock"""
        request = LockRequest(
            resource=self.resource,
            client_id=self.client_id,
            lock_type=self.lock_type,
            lease_duration=self.lease_duration,
            timeout=timeout,
            metadata=metadata or {}
        )
        
        self.lock_info = self.lock_manager.acquire_lock(request)
        self.is_acquired = self.lock_info is not None
        
        return self.is_acquired
    
    def release(self) -> bool:
        """Release the distributed lock"""
        if not self.is_acquired or not self.lock_info:
            return False
        
        success = self.lock_manager.release_lock(
            self.lock_info.lock_id, 
            self.client_id
        )
        
        if success:
            self.is_acquired = False
            self.lock_info = None
        
        return success
    
    def extend_lease(self, additional_time: float) -> bool:
        """Extend lock lease"""
        if not self.is_acquired or not self.lock_info:
            return False
        
        return self.lock_manager.extend_lock_lease(
            self.lock_info.lock_id,
            self.client_id,
            additional_time
        )
    
    def is_valid(self) -> bool:
        """Check if lock is still valid"""
        if not self.is_acquired or not self.lock_info:
            return False
        
        return not self.lock_info.is_expired()
    
    def __enter__(self):
        """Context manager entry"""
        if not self.acquire():
            raise Exception(f"Failed to acquire lock for resource: {self.resource}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()

class DistributedLockManager:
    """Distributed Lock Manager - Zomato Style Table Booking"""
    
    def __init__(self, node_id: str = None):
        """Initialize distributed lock manager"""
        self.node_id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        
        # Lock storage (in production, this would be Redis/etcd/Zookeeper)
        self.locks: Dict[str, LockInfo] = {}
        self.lock_holders: Dict[str, Set[str]] = defaultdict(set)  # client_id -> lock_ids
        self.lock_waiters: Dict[str, List[Dict]] = defaultdict(list)  # resource -> waiters
        
        # Synchronization
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'locks_acquired': 0,
            'locks_released': 0,
            'locks_expired': 0,
            'lock_conflicts': 0,
            'lock_timeouts': 0,
            'lease_extensions': 0
        }
        
        # Background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_locks, daemon=True)
        self.running = True
        self.cleanup_thread.start()
        
        logger.info(f"🔒 Distributed Lock Manager started - Node: {self.node_id}")
    
    def _generate_lock_id(self) -> str:
        """Generate unique lock ID"""
        return f"lock_{uuid.uuid4().hex}"
    
    def _cleanup_expired_locks(self):
        """Background thread to cleanup expired locks"""
        while self.running:
            try:
                current_time = time.time()
                expired_locks = []
                
                with self.lock:
                    for lock_id, lock_info in list(self.locks.items()):
                        if lock_info.is_expired():
                            expired_locks.append(lock_id)
                
                # Release expired locks
                for lock_id in expired_locks:
                    self._release_expired_lock(lock_id)
                    self.stats['locks_expired'] += 1
                
                if expired_locks:
                    logger.debug(f"Cleaned up {len(expired_locks)} expired locks")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in lock cleanup: {e}")
    
    def _release_expired_lock(self, lock_id: str):
        """Release an expired lock and notify waiters"""
        with self.lock:
            if lock_id not in self.locks:
                return
            
            lock_info = self.locks[lock_id]
            resource = lock_info.resource
            holder_id = lock_info.holder_id
            
            # Remove from locks
            del self.locks[lock_id]
            
            # Remove from holder tracking
            if holder_id in self.lock_holders:
                self.lock_holders[holder_id].discard(lock_id)
                if not self.lock_holders[holder_id]:
                    del self.lock_holders[holder_id]
            
            logger.debug(f"Expired lock released: {lock_id} for resource {resource}")
            
            # Notify waiters
            self._notify_waiters(resource)
    
    def _can_acquire_lock(self, request: LockRequest) -> bool:
        """Check if lock can be acquired"""
        resource = request.resource
        client_id = request.client_id
        lock_type = request.lock_type
        
        # Check existing locks for this resource
        existing_locks = [lock for lock in self.locks.values() 
                         if lock.resource == resource and not lock.is_expired()]
        
        if not existing_locks:
            return True  # No existing locks
        
        # Handle reentrant locks (same client acquiring again)
        if lock_type == LockType.REENTRANT:
            client_locks = [lock for lock in existing_locks if lock.holder_id == client_id]
            if client_locks:
                return True  # Client can reacquire their own lock
        
        # Handle shared locks
        if lock_type == LockType.SHARED:
            # Can acquire if all existing locks are shared
            return all(lock.lock_type == LockType.SHARED for lock in existing_locks)
        
        # Exclusive locks cannot coexist with any other locks
        return False
    
    def _notify_waiters(self, resource: str):
        """Notify waiters that a resource might be available"""
        if resource in self.lock_waiters:
            waiters = self.lock_waiters[resource].copy()
            for waiter in waiters:
                # This would notify the waiting thread in a real implementation
                logger.debug(f"Notifying waiter for resource: {resource}")
    
    def acquire_lock(self, request: LockRequest) -> Optional[LockInfo]:
        """Acquire a distributed lock"""
        start_time = time.time()
        
        while time.time() - start_time < request.timeout:
            with self.lock:
                # Check if lock can be acquired
                if self._can_acquire_lock(request):
                    # Handle reentrant lock
                    if request.lock_type == LockType.REENTRANT:
                        existing_lock = next(
                            (lock for lock in self.locks.values() 
                             if lock.resource == request.resource and 
                             lock.holder_id == request.client_id and 
                             not lock.is_expired()), 
                            None
                        )
                        
                        if existing_lock:
                            # Increment reentrant count
                            existing_lock.reentrant_count += 1
                            existing_lock.expires_at = time.time() + request.lease_duration
                            self.stats['locks_acquired'] += 1
                            
                            logger.info(f"🔄 Reentrant lock acquired: {existing_lock.lock_id} "
                                      f"(count: {existing_lock.reentrant_count})")
                            return existing_lock
                    
                    # Create new lock
                    lock_id = self._generate_lock_id()
                    current_time = time.time()
                    
                    lock_info = LockInfo(
                        lock_id=lock_id,
                        resource=request.resource,
                        holder_id=request.client_id,
                        lock_type=request.lock_type,
                        acquired_at=current_time,
                        expires_at=current_time + request.lease_duration,
                        lease_duration=request.lease_duration,
                        metadata=request.metadata
                    )
                    
                    # Store lock
                    self.locks[lock_id] = lock_info
                    self.lock_holders[request.client_id].add(lock_id)
                    
                    self.stats['locks_acquired'] += 1
                    
                    logger.info(f"🔒 Lock acquired: {lock_id} for resource {request.resource} "
                              f"by {request.client_id}")
                    return lock_info
                
                else:
                    self.stats['lock_conflicts'] += 1
            
            # Wait before retrying
            time.sleep(0.1)
        
        # Timeout
        self.stats['lock_timeouts'] += 1
        logger.warning(f"🕒 Lock acquisition timeout for resource: {request.resource}")
        return None
    
    def release_lock(self, lock_id: str, client_id: str) -> bool:
        """Release a distributed lock"""
        with self.lock:
            if lock_id not in self.locks:
                logger.warning(f"Attempted to release non-existent lock: {lock_id}")
                return False
            
            lock_info = self.locks[lock_id]
            
            # Verify client owns the lock
            if lock_info.holder_id != client_id:
                logger.warning(f"Client {client_id} attempted to release lock owned by {lock_info.holder_id}")
                return False
            
            # Handle reentrant lock
            if lock_info.lock_type == LockType.REENTRANT and lock_info.reentrant_count > 1:
                lock_info.reentrant_count -= 1
                logger.info(f"🔄 Reentrant lock count decreased: {lock_id} "
                          f"(count: {lock_info.reentrant_count})")
                return True
            
            # Remove lock
            resource = lock_info.resource
            del self.locks[lock_id]
            
            # Remove from holder tracking
            self.lock_holders[client_id].discard(lock_id)
            if not self.lock_holders[client_id]:
                del self.lock_holders[client_id]
            
            self.stats['locks_released'] += 1
            
            logger.info(f"🔓 Lock released: {lock_id} for resource {resource}")
            
            # Notify waiters
            self._notify_waiters(resource)
            
            return True
    
    def extend_lock_lease(self, lock_id: str, client_id: str, additional_time: float) -> bool:
        """Extend the lease of a lock"""
        with self.lock:
            if lock_id not in self.locks:
                return False
            
            lock_info = self.locks[lock_id]
            
            # Verify client owns the lock
            if lock_info.holder_id != client_id:
                return False
            
            # Extend lease
            lock_info.extend_lease(additional_time)
            self.stats['lease_extensions'] += 1
            
            logger.info(f"⏰ Lock lease extended: {lock_id} (+{additional_time}s)")
            return True
    
    def get_lock_info(self, lock_id: str) -> Optional[LockInfo]:
        """Get information about a lock"""
        with self.lock:
            return self.locks.get(lock_id)
    
    def list_locks_for_resource(self, resource: str) -> List[LockInfo]:
        """List all locks for a resource"""
        with self.lock:
            return [lock for lock in self.locks.values() 
                   if lock.resource == resource and not lock.is_expired()]
    
    def list_locks_for_client(self, client_id: str) -> List[LockInfo]:
        """List all locks held by a client"""
        with self.lock:
            lock_ids = self.lock_holders.get(client_id, set())
            return [self.locks[lock_id] for lock_id in lock_ids 
                   if lock_id in self.locks and not self.locks[lock_id].is_expired()]
    
    def create_lock(self, resource: str, client_id: str, 
                   lease_duration: float = 30.0, 
                   lock_type: LockType = LockType.EXCLUSIVE) -> DistributedLock:
        """Create a distributed lock object"""
        return DistributedLock(self, resource, client_id, lease_duration, lock_type)
    
    def get_stats(self) -> Dict:
        """Get lock manager statistics"""
        with self.lock:
            return {
                **self.stats,
                'active_locks': len(self.locks),
                'active_clients': len(self.lock_holders),
                'resources_locked': len(set(lock.resource for lock in self.locks.values()))
            }
    
    def shutdown(self):
        """Shutdown lock manager"""
        self.running = False
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        logger.info("🔒 Distributed Lock Manager shutdown")

class ZomatoTableBookingSystem:
    """Zomato Restaurant Table Booking System with Distributed Locks"""
    
    def __init__(self):
        """Initialize Zomato table booking system"""
        self.lock_manager = DistributedLockManager("zomato_booking_node")
        
        # Mumbai restaurant table configuration
        self.restaurants = {
            'toit_pune': {
                'name': 'Toit Brewpub, Pune',
                'tables': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'],
                'location': 'Koregaon Park, Pune'
            },
            'social_bkc': {
                'name': 'Social, BKC Mumbai',
                'tables': ['BKC1', 'BKC2', 'BKC3', 'BKC4', 'BKC5', 'BKC6'],
                'location': 'Bandra Kurla Complex, Mumbai'
            },
            'theobroma_linking': {
                'name': 'Theobroma, Linking Road',
                'tables': ['LR1', 'LR2', 'LR3', 'LR4'],
                'location': 'Linking Road, Bandra West'
            },
            'cafe_mocha': {
                'name': 'Cafe Mocha, CP Delhi', 
                'tables': ['CP1', 'CP2', 'CP3', 'CP4', 'CP5'],
                'location': 'Connaught Place, New Delhi'
            }
        }
        
        # Booking statistics
        self.booking_stats = defaultdict(int)
        
        print("🍽️ Zomato Table Booking System initialized with distributed locks")
        for restaurant_id, restaurant in self.restaurants.items():
            print(f"   {restaurant['name']}: {len(restaurant['tables'])} tables")
    
    def book_table(self, restaurant_id: str, table_id: str, customer_id: str, 
                   booking_duration_minutes: int = 120) -> Dict:
        """Book a restaurant table with distributed locking"""
        
        if restaurant_id not in self.restaurants:
            return {
                'success': False,
                'error': f'Restaurant {restaurant_id} not found'
            }
        
        restaurant = self.restaurants[restaurant_id]
        if table_id not in restaurant['tables']:
            return {
                'success': False,
                'error': f'Table {table_id} not found in {restaurant["name"]}'
            }
        
        # Create lock resource identifier
        resource = f"restaurant:{restaurant_id}:table:{table_id}"
        lease_duration = booking_duration_minutes * 60  # Convert to seconds
        
        # Create distributed lock
        table_lock = self.lock_manager.create_lock(
            resource=resource,
            client_id=customer_id,
            lease_duration=lease_duration
        )
        
        booking_metadata = {
            'restaurant_id': restaurant_id,
            'restaurant_name': restaurant['name'],
            'table_id': table_id,
            'customer_id': customer_id,
            'booking_duration_minutes': booking_duration_minutes,
            'booking_time': datetime.now().isoformat()
        }
        
        try:
            # Attempt to acquire table lock
            if table_lock.acquire(timeout=5.0, metadata=booking_metadata):
                booking_id = f"BOOK_{int(time.time())}_{customer_id}"
                
                self.booking_stats['successful_bookings'] += 1
                self.booking_stats[f'{restaurant_id}_bookings'] += 1
                
                logger.info(f"🎉 Table booked: {restaurant['name']} - {table_id} "
                          f"by {customer_id} for {booking_duration_minutes} minutes")
                
                return {
                    'success': True,
                    'booking_id': booking_id,
                    'restaurant_name': restaurant['name'],
                    'table_id': table_id,
                    'customer_id': customer_id,
                    'booking_duration_minutes': booking_duration_minutes,
                    'expires_at': datetime.fromtimestamp(table_lock.lock_info.expires_at).isoformat(),
                    'lock_id': table_lock.lock_info.lock_id
                }
            else:
                self.booking_stats['failed_bookings'] += 1
                self.booking_stats['table_unavailable'] += 1
                
                return {
                    'success': False,
                    'error': f'Table {table_id} is currently unavailable',
                    'restaurant_name': restaurant['name']
                }
        
        except Exception as e:
            self.booking_stats['booking_errors'] += 1
            logger.error(f"Booking error: {e}")
            
            return {
                'success': False,
                'error': f'Booking failed: {str(e)}'
            }
    
    def cancel_booking(self, customer_id: str, lock_id: str) -> Dict:
        """Cancel table booking by releasing the lock"""
        
        try:
            lock_info = self.lock_manager.get_lock_info(lock_id)
            
            if not lock_info:
                return {
                    'success': False,
                    'error': 'Booking not found'
                }
            
            if lock_info.holder_id != customer_id:
                return {
                    'success': False,
                    'error': 'You can only cancel your own bookings'
                }
            
            # Release the lock
            if self.lock_manager.release_lock(lock_id, customer_id):
                self.booking_stats['cancelled_bookings'] += 1
                
                logger.info(f"❌ Booking cancelled: {lock_id} by {customer_id}")
                
                return {
                    'success': True,
                    'message': 'Booking cancelled successfully',
                    'refund_eligible': lock_info.time_remaining() > 3600  # 1 hour notice
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to cancel booking'
                }
        
        except Exception as e:
            logger.error(f"Cancellation error: {e}")
            return {
                'success': False,
                'error': f'Cancellation failed: {str(e)}'
            }
    
    def extend_booking(self, customer_id: str, lock_id: str, 
                      additional_minutes: int) -> Dict:
        """Extend table booking duration"""
        
        try:
            lock_info = self.lock_manager.get_lock_info(lock_id)
            
            if not lock_info:
                return {
                    'success': False,
                    'error': 'Booking not found'
                }
            
            if lock_info.holder_id != customer_id:
                return {
                    'success': False,
                    'error': 'You can only extend your own bookings'
                }
            
            additional_seconds = additional_minutes * 60
            
            if self.lock_manager.extend_lock_lease(lock_id, customer_id, additional_seconds):
                self.booking_stats['booking_extensions'] += 1
                
                logger.info(f"⏰ Booking extended: {lock_id} by {additional_minutes} minutes")
                
                return {
                    'success': True,
                    'message': f'Booking extended by {additional_minutes} minutes',
                    'new_expiry': datetime.fromtimestamp(lock_info.expires_at).isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to extend booking'
                }
        
        except Exception as e:
            logger.error(f"Extension error: {e}")
            return {
                'success': False,
                'error': f'Extension failed: {str(e)}'
            }
    
    def get_available_tables(self, restaurant_id: str) -> Dict:
        """Get list of available tables for a restaurant"""
        
        if restaurant_id not in self.restaurants:
            return {
                'success': False,
                'error': f'Restaurant {restaurant_id} not found'
            }
        
        restaurant = self.restaurants[restaurant_id]
        all_tables = restaurant['tables']
        available_tables = []
        booked_tables = []
        
        for table_id in all_tables:
            resource = f"restaurant:{restaurant_id}:table:{table_id}"
            locks = self.lock_manager.list_locks_for_resource(resource)
            
            if not locks:
                available_tables.append({
                    'table_id': table_id,
                    'status': 'available'
                })
            else:
                lock = locks[0]  # Should be only one for exclusive locks
                booked_tables.append({
                    'table_id': table_id,
                    'status': 'booked',
                    'customer_id': lock.holder_id,
                    'booked_until': datetime.fromtimestamp(lock.expires_at).isoformat(),
                    'remaining_minutes': int(lock.time_remaining() / 60)
                })
        
        return {
            'success': True,
            'restaurant_name': restaurant['name'],
            'total_tables': len(all_tables),
            'available_tables': available_tables,
            'booked_tables': booked_tables,
            'availability_rate': len(available_tables) / len(all_tables) * 100
        }
    
    def get_customer_bookings(self, customer_id: str) -> Dict:
        """Get all active bookings for a customer"""
        
        customer_locks = self.lock_manager.list_locks_for_client(customer_id)
        bookings = []
        
        for lock in customer_locks:
            # Parse resource to extract restaurant and table info
            resource_parts = lock.resource.split(':')
            if len(resource_parts) >= 4:
                restaurant_id = resource_parts[1]
                table_id = resource_parts[3]
                
                restaurant = self.restaurants.get(restaurant_id, {})
                
                bookings.append({
                    'booking_id': lock.lock_id,
                    'restaurant_id': restaurant_id,
                    'restaurant_name': restaurant.get('name', 'Unknown'),
                    'table_id': table_id,
                    'booked_at': datetime.fromtimestamp(lock.acquired_at).isoformat(),
                    'expires_at': datetime.fromtimestamp(lock.expires_at).isoformat(),
                    'remaining_minutes': int(lock.time_remaining() / 60),
                    'can_extend': lock.time_remaining() > 300  # Can extend if >5 minutes remaining
                })
        
        return {
            'success': True,
            'customer_id': customer_id,
            'active_bookings': bookings,
            'total_bookings': len(bookings)
        }
    
    def get_booking_statistics(self) -> Dict:
        """Get booking system statistics"""
        lock_stats = self.lock_manager.get_stats()
        
        return {
            'booking_stats': dict(self.booking_stats),
            'lock_manager_stats': lock_stats,
            'restaurant_count': len(self.restaurants),
            'total_tables': sum(len(r['tables']) for r in self.restaurants.values())
        }
    
    def shutdown(self):
        """Shutdown booking system"""
        self.lock_manager.shutdown()
        logger.info("🍽️ Zomato Table Booking System shutdown")

def demonstrate_basic_distributed_locking():
    """Demonstrate basic distributed locking functionality"""
    print("🔒 Basic Distributed Locking Demo - Resource Protection")
    print("=" * 60)
    
    lock_manager = DistributedLockManager("demo_node")
    
    # Test basic exclusive locking
    print(f"\n🔐 Testing Exclusive Locks:")
    print("-" * 30)
    
    # Client 1 acquires lock
    client1_lock = lock_manager.create_lock("shared_resource", "client_1", lease_duration=10.0)
    success1 = client1_lock.acquire(timeout=2.0)
    print(f"   Client 1 acquire: {'✅ Success' if success1 else '❌ Failed'}")
    
    # Client 2 tries to acquire same resource (should fail)
    client2_lock = lock_manager.create_lock("shared_resource", "client_2", lease_duration=5.0)
    success2 = client2_lock.acquire(timeout=2.0)
    print(f"   Client 2 acquire: {'✅ Success' if success2 else '❌ Failed (Expected)'}")
    
    # Client 1 releases lock
    release1 = client1_lock.release()
    print(f"   Client 1 release: {'✅ Success' if release1 else '❌ Failed'}")
    
    # Client 2 tries again (should succeed)
    success2_retry = client2_lock.acquire(timeout=2.0)
    print(f"   Client 2 retry:   {'✅ Success' if success2_retry else '❌ Failed'}")
    
    # Test context manager
    print(f"\n🎯 Testing Context Manager:")
    print("-" * 30)
    
    try:
        with lock_manager.create_lock("context_resource", "client_3", lease_duration=5.0):
            print(f"   ✅ Inside context manager - lock acquired")
            time.sleep(1)
        print(f"   ✅ Outside context manager - lock auto-released")
    except Exception as e:
        print(f"   ❌ Context manager failed: {e}")
    
    # Test reentrant locks
    print(f"\n🔄 Testing Reentrant Locks:")
    print("-" * 30)
    
    reentrant_lock = lock_manager.create_lock(
        "reentrant_resource", 
        "client_4", 
        lease_duration=15.0,
        lock_type=LockType.REENTRANT
    )
    
    # First acquisition
    success_1st = reentrant_lock.acquire()
    print(f"   First acquire:  {'✅ Success' if success_1st else '❌ Failed'}")
    
    # Second acquisition (same client)
    success_2nd = reentrant_lock.acquire()
    print(f"   Second acquire: {'✅ Success' if success_2nd else '❌ Failed'}")
    
    # Show lock info
    if reentrant_lock.lock_info:
        print(f"   Reentrant count: {reentrant_lock.lock_info.reentrant_count}")
    
    # Clean up
    client2_lock.release()
    reentrant_lock.release()
    reentrant_lock.release()  # Release twice for reentrant
    lock_manager.shutdown()

def demonstrate_zomato_table_booking():
    """Demonstrate Zomato table booking system"""
    print("\n🍽️ Zomato Table Booking Demo - Restaurant Reservation System")
    print("=" * 70)
    
    # Initialize booking system
    booking_system = ZomatoTableBookingSystem()
    
    # Show available restaurants
    print(f"\n🏪 Available Restaurants:")
    print("-" * 25)
    for restaurant_id, restaurant in booking_system.restaurants.items():
        table_count = len(restaurant['tables'])
        print(f"   {restaurant['name']:<25}: {table_count} tables")
    
    # Simulate customer bookings
    print(f"\n📅 Simulating Table Bookings:")
    print("-" * 35)
    
    bookings = [
        ('customer_raj_9876', 'toit_pune', 'T1', 90),
        ('customer_priya_8765', 'social_bkc', 'BKC1', 120),
        ('customer_amit_7654', 'toit_pune', 'T1', 60),  # Conflict with first booking
        ('customer_sneha_6543', 'toit_pune', 'T2', 90),
        ('customer_rahul_5432', 'social_bkc', 'BKC2', 150),
        ('customer_anita_4321', 'theobroma_linking', 'LR1', 60),
    ]
    
    successful_bookings = []
    
    for customer_id, restaurant_id, table_id, duration in bookings:
        result = booking_system.book_table(restaurant_id, table_id, customer_id, duration)
        
        if result['success']:
            print(f"   ✅ {customer_id}: {result['restaurant_name']} - {table_id} ({duration}min)")
            successful_bookings.append((customer_id, result['lock_id']))
        else:
            print(f"   ❌ {customer_id}: {result['error']}")
    
    # Show restaurant availability
    print(f"\n🔍 Current Restaurant Availability:")
    print("-" * 40)
    
    for restaurant_id in ['toit_pune', 'social_bkc']:
        availability = booking_system.get_available_tables(restaurant_id)
        if availability['success']:
            restaurant_name = availability['restaurant_name']
            available_count = len(availability['available_tables'])
            booked_count = len(availability['booked_tables'])
            
            print(f"\n   {restaurant_name}:")
            print(f"     Available tables: {available_count}")
            print(f"     Booked tables: {booked_count}")
            
            for booked in availability['booked_tables']:
                print(f"       {booked['table_id']}: {booked['remaining_minutes']}min remaining")
    
    # Test booking extension
    print(f"\n⏰ Testing Booking Extension:")
    print("-" * 30)
    
    if successful_bookings:
        customer_id, lock_id = successful_bookings[0]
        extension_result = booking_system.extend_booking(customer_id, lock_id, 30)
        
        if extension_result['success']:
            print(f"   ✅ Extended booking for {customer_id} by 30 minutes")
        else:
            print(f"   ❌ Extension failed: {extension_result['error']}")
    
    # Show customer bookings
    print(f"\n👤 Customer Booking Status:")
    print("-" * 30)
    
    if successful_bookings:
        customer_id, _ = successful_bookings[0]
        customer_bookings = booking_system.get_customer_bookings(customer_id)
        
        if customer_bookings['success']:
            print(f"\n   {customer_id} has {customer_bookings['total_bookings']} active bookings:")
            for booking in customer_bookings['active_bookings']:
                print(f"     {booking['restaurant_name']} - {booking['table_id']}: "
                      f"{booking['remaining_minutes']}min remaining")
    
    # Show statistics
    print(f"\n📊 Booking System Statistics:")
    print("-" * 35)
    
    stats = booking_system.get_booking_statistics()
    booking_stats = stats['booking_stats']
    lock_stats = stats['lock_manager_stats']
    
    print(f"   Successful bookings: {booking_stats.get('successful_bookings', 0)}")
    print(f"   Failed bookings: {booking_stats.get('failed_bookings', 0)}")
    print(f"   Active locks: {lock_stats['active_locks']}")
    print(f"   Active clients: {lock_stats['active_clients']}")
    
    # Cleanup
    booking_system.shutdown()
    
    return booking_system

def demonstrate_concurrent_booking_scenario():
    """Demonstrate concurrent table booking scenario"""
    print("\n⚡ Concurrent Booking Demo - Rush Hour Table Booking")
    print("=" * 60)
    
    booking_system = ZomatoTableBookingSystem()
    
    def simulate_customer_booking(customer_info: Dict) -> Dict:
        """Simulate individual customer trying to book table"""
        customer_id, restaurant_id, preferred_tables, duration = customer_info.values()
        
        # Try preferred tables in order
        for table_id in preferred_tables:
            result = booking_system.book_table(restaurant_id, table_id, customer_id, duration)
            if result['success']:
                return {
                    'customer_id': customer_id,
                    'success': True,
                    'table_booked': table_id,
                    'restaurant': result['restaurant_name']
                }
        
        return {
            'customer_id': customer_id,
            'success': False,
            'error': 'All preferred tables unavailable'
        }
    
    # Simulate 20 customers trying to book simultaneously
    customers = []
    for i in range(20):
        customer_id = f"customer_{i:03d}"
        restaurant_id = random.choice(['toit_pune', 'social_bkc', 'theobroma_linking'])
        restaurant = booking_system.restaurants[restaurant_id]
        
        # Each customer has 2-3 preferred tables
        preferred_tables = random.sample(restaurant['tables'], 
                                       min(3, len(restaurant['tables'])))
        duration = random.choice([60, 90, 120, 150])
        
        customers.append({
            'customer_id': customer_id,
            'restaurant_id': restaurant_id,
            'preferred_tables': preferred_tables,
            'duration': duration
        })
    
    print(f"🎯 Simulating {len(customers)} customers booking tables simultaneously...")
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor for concurrent bookings
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simulate_customer_booking, customer) 
                  for customer in customers]
        
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    end_time = time.time()
    
    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n📊 Concurrent Booking Results:")
    print("-" * 35)
    print(f"   Total Customers: {len(customers)}")
    print(f"   Successful Bookings: {len(successful)} ({len(successful)/len(customers)*100:.1f}%)")
    print(f"   Failed Bookings: {len(failed)} ({len(failed)/len(customers)*100:.1f}%)")
    print(f"   Booking Time: {end_time - start_time:.2f}s")
    print(f"   Throughput: {len(customers)/(end_time - start_time):.1f} bookings/sec")
    
    # Show restaurant utilization
    print(f"\n🏪 Restaurant Table Utilization:")
    print("-" * 35)
    
    for restaurant_id in booking_system.restaurants:
        availability = booking_system.get_available_tables(restaurant_id)
        if availability['success']:
            utilization = 100 - availability['availability_rate']
            print(f"   {availability['restaurant_name']:<25}: {utilization:.1f}% utilized")
    
    # Final statistics
    final_stats = booking_system.get_booking_statistics()
    lock_stats = final_stats['lock_manager_stats']
    
    print(f"\n🔒 Lock Manager Performance:")
    print("-" * 30)
    print(f"   Locks Acquired: {lock_stats['locks_acquired']}")
    print(f"   Lock Conflicts: {lock_stats['lock_conflicts']}")
    print(f"   Lock Timeouts: {lock_stats['lock_timeouts']}")
    print(f"   Active Locks: {lock_stats['active_locks']}")
    
    booking_system.shutdown()

def demonstrate_lock_expiration_scenario():
    """Demonstrate lock expiration and cleanup"""
    print("\n⏰ Lock Expiration Demo - Automatic Table Release")
    print("=" * 55)
    
    booking_system = ZomatoTableBookingSystem()
    
    # Book tables with short durations
    print(f"📅 Booking tables with short durations (10 seconds):")
    print("-" * 50)
    
    short_bookings = [
        ('customer_test_1', 'toit_pune', 'T1'),
        ('customer_test_2', 'toit_pune', 'T2'),
        ('customer_test_3', 'social_bkc', 'BKC1'),
    ]
    
    active_bookings = []
    
    for customer_id, restaurant_id, table_id in short_bookings:
        result = booking_system.book_table(
            restaurant_id, table_id, customer_id, 
            booking_duration_minutes=1  # 1 minute only
        )
        
        if result['success']:
            print(f"   ✅ {customer_id}: {table_id} booked for 1 minute")
            active_bookings.append((customer_id, result['lock_id'], restaurant_id, table_id))
        else:
            print(f"   ❌ {customer_id}: Booking failed")
    
    print(f"\n⏳ Waiting for lock expiration (monitoring for 2 minutes)...")
    print("-" * 60)
    
    start_time = time.time()
    check_interval = 15  # Check every 15 seconds
    
    while time.time() - start_time < 120:  # Monitor for 2 minutes
        elapsed = time.time() - start_time
        print(f"\n   Time elapsed: {elapsed:.0f}s")
        
        # Check status of each booking
        for customer_id, lock_id, restaurant_id, table_id in active_bookings:
            lock_info = booking_system.lock_manager.get_lock_info(lock_id)
            
            if lock_info:
                remaining = lock_info.time_remaining()
                if remaining > 0:
                    print(f"     {table_id}: {remaining:.0f}s remaining ({customer_id})")
                else:
                    print(f"     {table_id}: ⏰ EXPIRED but not yet cleaned up")
            else:
                print(f"     {table_id}: 🔓 Released/Cleaned up")
        
        # Show current restaurant availability
        availability = booking_system.get_available_tables('toit_pune')
        if availability['success']:
            available_count = len(availability['available_tables'])
            booked_count = len(availability['booked_tables'])
            print(f"   Toit Pune: {available_count} available, {booked_count} booked")
        
        if elapsed >= 120:
            break
            
        time.sleep(check_interval)
    
    print(f"\n✅ Lock expiration demonstration completed")
    
    # Final availability check
    final_availability = booking_system.get_available_tables('toit_pune')
    if final_availability['success']:
        print(f"   Final Toit Pune availability: {len(final_availability['available_tables'])}/8 tables free")
    
    booking_system.shutdown()

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_basic_distributed_locking()
    
    print("\n" + "="*80 + "\n")
    
    zomato_booking_system = demonstrate_zomato_table_booking()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_concurrent_booking_scenario()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_lock_expiration_scenario()
    
    print(f"\n✅ Distributed Lock Manager Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • Exclusive Locking - Single resource access control")
    print(f"   • Reentrant Locks - Same client multiple acquisitions") 
    print(f"   • Lock Leasing - Time-based automatic release")
    print(f"   • Context Managers - Automatic lock management")
    print(f"   • Lock Expiration - Automatic cleanup of expired locks")
    print(f"   • Concurrent Access - Multiple clients contention handling")
    print(f"   • Lease Extension - Dynamic lock duration management")
    print(f"   • Indian Context - Zomato, restaurant bookings, table reservations")
    print(f"   • High Concurrency - Rush hour booking scenarios")