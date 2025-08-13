#!/usr/bin/env python3
"""
etcd Distributed Lock Implementation
===================================

Production-ready etcd-based distributed locking for cloud-native applications.
Used by Kubernetes, CoreOS, and many microservices architectures.

Mumbai Context: etcd = Mumbai metro का signaling system! हर train को पता होना
चाहिए कि कौन सा track free है. etcd भी distributed systems में coordination करता है.

Real-world usage:
- Kubernetes master election
- Microservices leader election
- Configuration management locks
- Service discovery coordination
"""

import time
import threading
import logging
import json
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
import etcd3
import uuid
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EtcdConfig:
    """etcd connection configuration"""
    host: str = 'localhost'
    port: int = 2379
    timeout: int = 10
    user: Optional[str] = None
    password: Optional[str] = None

class EtcdLockError(Exception):
    """etcd lock specific exceptions"""
    pass

class EtcdDistributedLock:
    """
    etcd-based distributed lock implementation
    
    Mumbai Metaphor: यह Mumbai metro के Central Control जैसा है - सभी trains
    का coordination, track allocation, signal management centrally होता है.
    etcd भी distributed systems में same role play करता है!
    """
    
    def __init__(self, config: EtcdConfig):
        self.config = config
        self.client = None
        self.lease_id = None
        self.session_id = str(uuid.uuid4())
        
    def connect(self) -> bool:
        """Connect to etcd cluster"""
        try:
            self.client = etcd3.client(
                host=self.config.host,
                port=self.config.port,
                timeout=self.config.timeout,
                user=self.config.user,
                password=self.config.password
            )
            
            # Test connection
            self.client.status()
            logger.info(f"✅ Connected to etcd: {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to etcd: {e}")
            return False
    
    def acquire_lock(self, resource: str, ttl: int = 30) -> Optional[Dict]:
        """
        Acquire distributed lock using etcd lease mechanism
        
        Args:
            resource: Resource name to lock
            ttl: Lock time-to-live in seconds
            
        Returns:
            Lock info if successful, None otherwise
        """
        if not self.client:
            raise EtcdLockError("Not connected to etcd")
        
        try:
            # Create lease for lock expiration
            lease = self.client.lease(ttl)
            self.lease_id = lease.id
            
            # Lock key path
            lock_key = f"/locks/{resource}"
            
            # Lock metadata
            lock_metadata = {
                'session_id': self.session_id,
                'acquired_at': time.time(),
                'ttl': ttl,
                'owner': f"process_{uuid.uuid4().hex[:8]}"
            }
            
            # Try to acquire lock atomically
            # This uses etcd's compare-and-swap (CAS) operation
            success, responses = self.client.transaction(
                compare=[
                    # Check if key doesn't exist or is expired
                    self.client.transactions.create(lock_key) == 0
                ],
                success=[
                    # If condition true, set the lock
                    self.client.transactions.put(
                        lock_key,
                        json.dumps(lock_metadata),
                        lease=lease
                    )
                ],
                failure=[
                    # If condition false, get current value
                    self.client.transactions.get(lock_key)
                ]
            )
            
            if success:
                # Lock acquired successfully
                lock_info = {
                    'resource': resource,
                    'key': lock_key,
                    'lease_id': lease.id,
                    'metadata': lock_metadata,
                    'acquired_at': time.time()
                }
                
                # Keep lease alive
                self._keep_lease_alive(lease)
                
                logger.info(f"🔒 Lock acquired: {resource} (lease: {lease.id})")
                return lock_info
            else:
                # Lock already held by someone else
                for response in responses:
                    if hasattr(response, 'kvs') and response.kvs:
                        current_owner = json.loads(response.kvs[0].value.decode())
                        logger.warning(f"❌ Lock held by: {current_owner.get('owner', 'unknown')}")
                
                lease.revoke()
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to acquire lock for {resource}: {e}")
            if self.lease_id:
                try:
                    self.client.revoke_lease(self.lease_id)
                except:
                    pass
            return None
    
    def release_lock(self, lock_info: Dict) -> bool:
        """
        Release distributed lock by revoking lease
        
        Args:
            lock_info: Lock information from acquire_lock
            
        Returns:
            True if successfully released
        """
        try:
            lease_id = lock_info['lease_id']
            
            # Revoke lease (this will delete the key automatically)
            self.client.revoke_lease(lease_id)
            
            logger.info(f"🔓 Lock released: {lock_info['resource']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to release lock: {e}")
            return False
    
    def _keep_lease_alive(self, lease):
        """Keep lease alive in background thread"""
        def lease_refresh():
            try:
                lease.refresh()
            except Exception as e:
                logger.warning(f"⚠️ Lease refresh failed: {e}")
        
        # Start lease refresh in background
        threading.Timer(lease.ttl / 3, lease_refresh).start()
    
    @contextmanager
    def lock_context(self, resource: str, ttl: int = 30):
        """
        Context manager for automatic lock acquisition and release
        
        Usage:
            with etcd_lock.lock_context("resource_name"):
                # Critical section code here
                pass
        """
        lock_info = self.acquire_lock(resource, ttl)
        if not lock_info:
            raise EtcdLockError(f"Failed to acquire lock for {resource}")
        
        try:
            yield lock_info
        finally:
            self.release_lock(lock_info)
    
    def disconnect(self):
        """Disconnect from etcd"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from etcd")

class OlaDriverAssignment:
    """
    Ola driver assignment system using etcd locks
    
    Mumbai Story: Peak traffic time में multiple customers एक साथ ride book करते हैं
    और nearest driver को assign होना चाहिए. etcd locks ensure करते हैं कि same
    driver multiple customers को assign न हो जाए!
    """
    
    def __init__(self, etcd_lock: EtcdDistributedLock):
        self.etcd_lock = etcd_lock
        self.drivers = {
            f"driver_{i:03d}": {
                'id': f"driver_{i:03d}",
                'name': f"राहुल {i:03d}",
                'location': f"Zone_{i % 5}",
                'status': 'available',
                'rating': 4.0 + (i % 10) * 0.1,
                'vehicle': 'sedan' if i % 3 == 0 else 'hatchback'
            }
            for i in range(20)
        }
        self.assignment_stats = {
            'rides_requested': 0,
            'successful_assignments': 0,
            'driver_conflicts_prevented': 0,
            'assignment_failures': 0
        }
    
    def request_ride(self, customer_id: str, pickup_location: str) -> Dict:
        """
        Request ride with driver assignment using distributed locking
        
        Args:
            customer_id: Customer identifier
            pickup_location: Pickup location
            
        Returns:
            Ride assignment result
        """
        self.assignment_stats['rides_requested'] += 1
        
        # Find available drivers in the area
        available_drivers = [
            driver for driver in self.drivers.values()
            if driver['status'] == 'available' and 
            pickup_location.startswith(driver['location'])
        ]
        
        if not available_drivers:
            self.assignment_stats['assignment_failures'] += 1
            return {
                'success': False,
                'message': 'No drivers available in your area',
                'error_code': 'NO_DRIVERS_AVAILABLE'
            }
        
        # Sort by rating (best drivers first)
        available_drivers.sort(key=lambda d: d['rating'], reverse=True)
        
        # Try to assign each driver until one is successfully locked
        for driver in available_drivers:
            driver_id = driver['id']
            
            try:
                # Use context manager for automatic lock management
                with self.etcd_lock.lock_context(f"driver_assignment_{driver_id}", ttl=10):
                    # Double-check driver availability within lock
                    if self.drivers[driver_id]['status'] != 'available':
                        continue  # Driver was assigned by another process
                    
                    # Assign driver
                    self.drivers[driver_id]['status'] = 'busy'
                    
                    ride_id = f"RIDE_{int(time.time())}_{customer_id[-4:]}"
                    
                    self.assignment_stats['successful_assignments'] += 1
                    self.assignment_stats['driver_conflicts_prevented'] += 1
                    
                    logger.info(f"🚗 Ride assigned: {ride_id} - {driver['name']} to {customer_id}")
                    
                    # Simulate driver accepting ride
                    time.sleep(0.1)
                    
                    return {
                        'success': True,
                        'ride_id': ride_id,
                        'driver': {
                            'id': driver_id,
                            'name': driver['name'],
                            'rating': driver['rating'],
                            'vehicle': driver['vehicle'],
                            'location': driver['location']
                        },
                        'customer_id': customer_id,
                        'pickup_location': pickup_location,
                        'estimated_arrival': '5-8 minutes'
                    }
                    
            except EtcdLockError:
                # Driver is being assigned by another process
                continue
        
        # All drivers were busy or locked
        self.assignment_stats['assignment_failures'] += 1
        return {
            'success': False,
            'message': 'All nearby drivers are currently busy',
            'error_code': 'DRIVERS_BUSY'
        }
    
    def complete_ride(self, ride_id: str, driver_id: str) -> bool:
        """
        Complete ride and make driver available again
        
        Args:
            ride_id: Ride identifier
            driver_id: Driver identifier
            
        Returns:
            Success status
        """
        try:
            with self.etcd_lock.lock_context(f"driver_assignment_{driver_id}", ttl=5):
                if driver_id in self.drivers:
                    self.drivers[driver_id]['status'] = 'available'
                    logger.info(f"✅ Ride completed: {ride_id} - {driver_id} now available")
                    return True
                return False
        except EtcdLockError:
            logger.error(f"Failed to update driver status for {ride_id}")
            return False
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        available_drivers = len([d for d in self.drivers.values() if d['status'] == 'available'])
        busy_drivers = len([d for d in self.drivers.values() if d['status'] == 'busy'])
        
        return {
            'drivers': {
                'total': len(self.drivers),
                'available': available_drivers,
                'busy': busy_drivers
            },
            'stats': self.assignment_stats.copy(),
            'success_rate': (
                self.assignment_stats['successful_assignments'] / 
                max(1, self.assignment_stats['rides_requested'])
            ) * 100
        }

def simulate_peak_hour_ola_requests():
    """
    Simulate Ola peak hour ride requests
    
    Mumbai Scenario: शाम 7 बजे office time में हजारों लोग साथ-साथ cab book करते हैं.
    etcd locks ensure करते हैं कि driver assignment efficiently और correctly हो!
    """
    # Initialize etcd lock manager
    etcd_config = EtcdConfig(host='localhost', port=2379)
    etcd_lock = EtcdDistributedLock(etcd_config)
    
    if not etcd_lock.connect():
        logger.error("Failed to connect to etcd. Please ensure etcd is running on localhost:2379")
        return
    
    ola_system = OlaDriverAssignment(etcd_lock)
    
    # Peak hour locations in Mumbai
    locations = [
        'Zone_0_Bandra', 'Zone_0_Kurla', 'Zone_0_Andheri',
        'Zone_1_Thane', 'Zone_1_Ghatkopar', 'Zone_1_Mulund',
        'Zone_2_CST', 'Zone_2_Churchgate', 'Zone_2_Marine_Drive',
        'Zone_3_Goregaon', 'Zone_3_Malad', 'Zone_3_Kandivali',
        'Zone_4_Powai', 'Zone_4_Hiranandani', 'Zone_4_Vikhroli'
    ]
    
    def request_ride_simulation(customer_id: str, location: str):
        """Single customer ride request"""
        result = ola_system.request_ride(customer_id, location)
        
        if result['success']:
            # Simulate ride completion after some time
            ride_id = result['ride_id']
            driver_id = result['driver']['id']
            
            # Complete ride after 2-5 minutes (simulated as 0.2-0.5 seconds)
            completion_delay = 0.2 + (hash(customer_id) % 3) * 0.1
            threading.Timer(
                completion_delay,
                lambda: ola_system.complete_ride(ride_id, driver_id)
            ).start()
        
        logger.info(f"Customer {customer_id} [{location}]: {result.get('message', 'Success')}")
        return result
    
    # Simulate concurrent ride requests
    threads = []
    customers = [f"customer_{i:04d}" for i in range(30)]
    
    logger.info("🏙️ Starting Ola peak hour simulation...")
    start_time = time.time()
    
    # Create threads for concurrent requests
    for customer_id in customers:
        location = locations[hash(customer_id) % len(locations)]
        thread = threading.Thread(
            target=request_ride_simulation,
            args=(customer_id, location)
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.05)  # Simulate realistic request timing
    
    # Wait for all requests to complete
    for thread in threads:
        thread.join()
    
    # Wait a bit more for ride completions
    time.sleep(1)
    
    end_time = time.time()
    
    # Show final results
    status = ola_system.get_system_status()
    logger.info(f"\n📊 Ola Peak Hour Results:")
    logger.info(f"Total requests: {status['stats']['rides_requested']}")
    logger.info(f"Successful assignments: {status['stats']['successful_assignments']}")
    logger.info(f"Assignment failures: {status['stats']['assignment_failures']}")
    logger.info(f"Driver conflicts prevented: {status['stats']['driver_conflicts_prevented']}")
    logger.info(f"Success rate: {status['success_rate']:.2f}%")
    logger.info(f"Available drivers: {status['drivers']['available']}/{status['drivers']['total']}")
    logger.info(f"Processing time: {end_time - start_time:.2f} seconds")
    
    # Cleanup
    etcd_lock.disconnect()

if __name__ == "__main__":
    try:
        simulate_peak_hour_ola_requests()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()