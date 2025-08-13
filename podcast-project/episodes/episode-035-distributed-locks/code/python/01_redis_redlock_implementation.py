#!/usr/bin/env python3
"""
Redis Redlock Implementation
===============================

Redlock algorithm implementation for distributed locking across multiple Redis instances.
Production-ready implementation with proper error handling and timeouts.

Mumbai Context: जैसे local train के लिए multiple ticket counters होते हैं,
वैसे ही multiple Redis instances में distributed lock implement करते हैं.

Real-world usage:
- Flipkart inventory management during Big Billion Day
- IRCTC tatkal booking system
- Paytm wallet balance updates
"""

import time
import random
import string
import redis
import threading
from typing import List, Optional, Dict
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RedisInstance:
    """Redis instance configuration"""
    host: str
    port: int
    db: int = 0
    password: Optional[str] = None

class RedlockError(Exception):
    """Redlock specific exceptions"""
    pass

class RedlockManager:
    """
    Redlock algorithm implementation for distributed locking
    
    Mumbai Metaphor: यह multiple railway stations पर साथ-साथ ticket booking
    करने जैसा है - majority में success मिले तो booking confirm!
    """
    
    def __init__(self, redis_instances: List[RedisInstance], retry_count: int = 3):
        self.redis_instances = redis_instances
        self.retry_count = retry_count
        self.quorum = len(redis_instances) // 2 + 1
        self.clock_drift_factor = 0.01  # 1% clock drift compensation
        
        # Initialize Redis connections
        self.redis_clients = []
        for instance in redis_instances:
            client = redis.Redis(
                host=instance.host,
                port=instance.port,
                db=instance.db,
                password=instance.password,
                socket_timeout=0.1,
                socket_connect_timeout=0.1,
                decode_responses=True
            )
            self.redis_clients.append(client)
    
    def _generate_random_value(self, length: int = 20) -> str:
        """Generate random value for lock identification"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def acquire_lock(self, resource: str, ttl: int = 10000) -> Optional[Dict]:
        """
        Acquire distributed lock using Redlock algorithm
        
        Args:
            resource: Resource name to lock
            ttl: Lock time-to-live in milliseconds
            
        Returns:
            Lock info dict if successful, None otherwise
        """
        retry = 0
        while retry < self.retry_count:
            lock_value = self._generate_random_value()
            start_time = int(time.time() * 1000)  # Current time in milliseconds
            
            # Try to acquire lock on all Redis instances
            locked_instances = 0
            for client in self.redis_clients:
                try:
                    # Use SET with NX (not exists) and PX (expire time in ms)
                    result = client.set(
                        name=f"lock:{resource}",
                        value=lock_value,
                        nx=True,
                        px=ttl
                    )
                    if result:
                        locked_instances += 1
                        logger.debug(f"Lock acquired on instance {client}")
                except Exception as e:
                    logger.warning(f"Failed to acquire lock on instance: {e}")
            
            # Calculate elapsed time and drift compensation
            elapsed_time = int(time.time() * 1000) - start_time
            drift = int(ttl * self.clock_drift_factor) + 2
            
            # Check if we have majority and enough validity time
            validity_time = ttl - elapsed_time - drift
            
            if locked_instances >= self.quorum and validity_time > 0:
                # Lock successfully acquired
                lock_info = {
                    'resource': resource,
                    'value': lock_value,
                    'validity_time': validity_time,
                    'locked_instances': locked_instances,
                    'acquired_at': time.time()
                }
                logger.info(f"✅ Lock acquired for {resource} (instances: {locked_instances}/{len(self.redis_clients)})")
                return lock_info
            else:
                # Failed to acquire majority - unlock all instances
                self._unlock_instances(resource, lock_value)
                logger.warning(f"❌ Failed to acquire lock for {resource} (instances: {locked_instances}/{len(self.redis_clients)})")
            
            # Wait before retry
            delay = random.randint(0, 100) / 1000.0  # Random delay 0-100ms
            time.sleep(delay)
            retry += 1
        
        return None
    
    def release_lock(self, lock_info: Dict) -> bool:
        """
        Release distributed lock
        
        Args:
            lock_info: Lock information returned by acquire_lock
            
        Returns:
            True if successfully released, False otherwise
        """
        resource = lock_info['resource']
        value = lock_info['value']
        
        return self._unlock_instances(resource, value)
    
    def _unlock_instances(self, resource: str, value: str) -> bool:
        """Unlock resource on all Redis instances"""
        unlock_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        unlocked_instances = 0
        for client in self.redis_clients:
            try:
                result = client.eval(
                    unlock_script,
                    1,
                    f"lock:{resource}",
                    value
                )
                if result:
                    unlocked_instances += 1
            except Exception as e:
                logger.warning(f"Failed to unlock instance: {e}")
        
        logger.info(f"Unlocked {resource} on {unlocked_instances} instances")
        return unlocked_instances > 0

class IRCTCTatkalBookingLock:
    """
    IRCTC Tatkal booking system using distributed locks
    
    Mumbai Story: Tatkal booking में multiple servers होते हैं, लेकिन same seat
    केवल एक user को ही मिल सकती है. Redlock ensure करता है कि conflict न हो!
    """
    
    def __init__(self, redlock_manager: RedlockManager):
        self.redlock_manager = redlock_manager
        self.booking_stats = {
            'attempts': 0,
            'successful_bookings': 0,
            'conflicts_prevented': 0
        }
    
    def book_tatkal_seat(self, train_no: str, seat_no: str, user_id: str) -> Dict:
        """
        Book tatkal seat with distributed locking
        
        Args:
            train_no: Train number
            seat_no: Seat number
            user_id: User attempting booking
            
        Returns:
            Booking result
        """
        self.booking_stats['attempts'] += 1
        resource = f"tatkal_seat_{train_no}_{seat_no}"
        
        # Try to acquire lock for 5 seconds
        lock_info = self.redlock_manager.acquire_lock(resource, ttl=5000)
        
        if not lock_info:
            return {
                'success': False,
                'message': 'Seat booking in progress by another user',
                'error_code': 'LOCK_ACQUIRE_FAILED'
            }
        
        try:
            # Simulate booking process
            logger.info(f"🎫 Processing tatkal booking: Train {train_no}, Seat {seat_no} for User {user_id}")
            time.sleep(0.2)  # Simulate database operations
            
            # Check seat availability (simulate)
            if random.random() > 0.1:  # 90% success rate
                self.booking_stats['successful_bookings'] += 1
                return {
                    'success': True,
                    'message': f'Seat {seat_no} booked successfully in train {train_no}',
                    'booking_id': f"TATKAL_{int(time.time())}",
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'message': 'Seat no longer available',
                    'error_code': 'SEAT_UNAVAILABLE'
                }
                
        finally:
            # Always release the lock
            self.redlock_manager.release_lock(lock_info)
            self.booking_stats['conflicts_prevented'] += 1

    def get_booking_stats(self) -> Dict:
        """Get booking statistics"""
        return {
            **self.booking_stats,
            'success_rate': (
                self.booking_stats['successful_bookings'] / 
                max(1, self.booking_stats['attempts'])
            ) * 100
        }

def simulate_concurrent_tatkal_booking():
    """
    Simulate concurrent tatkal booking scenario
    
    Mumbai Scenario: 10:00 AM tatkal booking शुरू होते ही thousands of users
    same seat के लिए try करते हैं. Redlock ensures data consistency!
    """
    # Setup Redis instances (in production, these would be on different servers)
    redis_instances = [
        RedisInstance('localhost', 6379, db=0),
        RedisInstance('localhost', 6379, db=1),
        RedisInstance('localhost', 6379, db=2),
    ]
    
    redlock_manager = RedlockManager(redis_instances)
    booking_system = IRCTCTatkalBookingLock(redlock_manager)
    
    # Simulate multiple users trying to book same seat
    train_no = "12345"
    seat_no = "A1-15"
    
    def user_booking_attempt(user_id: str):
        """Single user booking attempt"""
        result = booking_system.book_tatkal_seat(train_no, seat_no, user_id)
        logger.info(f"User {user_id}: {result}")
        return result
    
    # Create multiple threads simulating concurrent users
    threads = []
    users = [f"user_{i:03d}" for i in range(10)]
    
    logger.info("🚂 Starting concurrent tatkal booking simulation...")
    start_time = time.time()
    
    for user_id in users:
        thread = threading.Thread(target=user_booking_attempt, args=(user_id,))
        threads.append(thread)
        thread.start()
        time.sleep(0.01)  # Small delay to simulate real-world timing
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    # Print results
    stats = booking_system.get_booking_stats()
    logger.info(f"\n📊 Tatkal Booking Simulation Results:")
    logger.info(f"Total attempts: {stats['attempts']}")
    logger.info(f"Successful bookings: {stats['successful_bookings']}")
    logger.info(f"Conflicts prevented: {stats['conflicts_prevented']}")
    logger.info(f"Success rate: {stats['success_rate']:.2f}%")
    logger.info(f"Total time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    # Test Redis connection
    try:
        test_redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        test_redis.ping()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.error("Please ensure Redis is running on localhost:6379")
        exit(1)
    
    simulate_concurrent_tatkal_booking()