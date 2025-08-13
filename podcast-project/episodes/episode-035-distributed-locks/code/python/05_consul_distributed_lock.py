#!/usr/bin/env python3
"""
HashiCorp Consul Distributed Lock Implementation
==============================================

Production-ready Consul-based distributed locking for microservices.
Consul provides strong consistency and service discovery capabilities.

Mumbai Context: Consul = Mumbai के police control room जैसा है! हर area के
police station को central command से coordination करना पड़ता है.
Consul भी microservices को centrally coordinate करता है.

Real-world usage:
- Microservices leader election
- Configuration updates coordination
- Service deployment locks
- Health check coordination
"""

import time
import threading
import logging
import json
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import consul
import requests
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConsulConfig:
    """Consul connection configuration"""
    host: str = 'localhost'
    port: int = 8500
    token: Optional[str] = None
    datacenter: str = 'dc1'
    scheme: str = 'http'

class ConsulLockError(Exception):
    """Consul lock specific exceptions"""
    pass

class ConsulDistributedLock:
    """
    Consul-based distributed lock implementation using sessions and KV store
    
    Mumbai Metaphor: यह Mumbai police का wireless communication system जैसा है -
    हर patrol car को HQ से permission लेना पड़ता है special operations के लिए.
    Consul भी services को coordination प्रदान करता है!
    """
    
    def __init__(self, config: ConsulConfig):
        self.config = config
        self.client = consul.Consul(
            host=config.host,
            port=config.port,
            token=config.token,
            dc=config.datacenter,
            scheme=config.scheme
        )
        self.session_id = None
        self.node_id = f"node_{uuid.uuid4().hex[:8]}"
        
        # Test connection
        try:
            self.client.agent.self()
            logger.info(f"✅ Connected to Consul: {config.host}:{config.port}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Consul: {e}")
            raise ConsulLockError(f"Consul connection failed: {e}")
    
    def _create_session(self, ttl: int = 30) -> str:
        """Create Consul session for lock management"""
        session_data = {
            'Name': f'lock_session_{self.node_id}',
            'TTL': ttl,
            'Behavior': 'release',  # Release locks when session expires
            'LockDelay': 1  # Minimum delay before lock can be acquired again
        }
        
        try:
            session_id = self.client.session.create(
                name=session_data['Name'],
                ttl=session_data['TTL'],
                behavior=session_data['Behavior'],
                lock_delay=session_data['LockDelay']
            )
            
            # Start session renewal
            self._start_session_renewal(session_id, ttl)
            
            logger.debug(f"Created Consul session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create Consul session: {e}")
            raise ConsulLockError(f"Session creation failed: {e}")
    
    def _start_session_renewal(self, session_id: str, ttl: int):
        """Start background thread to renew session"""
        def renew_session():
            renewal_interval = ttl // 3  # Renew at 1/3 of TTL
            
            while True:
                try:
                    time.sleep(renewal_interval)
                    result = self.client.session.renew(session_id)
                    if result:
                        logger.debug(f"Renewed session: {session_id}")
                    else:
                        logger.warning(f"Session renewal failed: {session_id}")
                        break
                except Exception as e:
                    logger.warning(f"Session renewal error: {e}")
                    break
        
        renewal_thread = threading.Thread(target=renew_session, daemon=True)
        renewal_thread.start()
    
    def acquire_lock(self, resource: str, ttl: int = 30, timeout: int = 10) -> Optional[Dict]:
        """
        Acquire distributed lock using Consul KV store
        
        Args:
            resource: Resource name to lock
            ttl: Session TTL in seconds
            timeout: Lock acquisition timeout in seconds
            
        Returns:
            Lock info if successful, None otherwise
        """
        # Create session for this lock
        session_id = self._create_session(ttl)
        
        lock_key = f"locks/{resource}"
        lock_metadata = {
            'session_id': session_id,
            'node_id': self.node_id,
            'acquired_at': time.time(),
            'resource': resource,
            'ttl': ttl
        }
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Try to acquire lock by setting key with session
                success = self.client.kv.put(
                    key=lock_key,
                    value=json.dumps(lock_metadata),
                    acquire=session_id
                )
                
                if success:
                    lock_info = {
                        'resource': resource,
                        'session_id': session_id,
                        'lock_key': lock_key,
                        'metadata': lock_metadata,
                        'acquired_at': time.time()
                    }
                    
                    logger.info(f"🔒 Consul lock acquired: {resource} (session: {session_id[:8]}...)")
                    return lock_info
                else:
                    # Lock is held by another session
                    # Get current lock info
                    _, current_lock = self.client.kv.get(lock_key)
                    if current_lock and current_lock['Session']:
                        current_metadata = json.loads(current_lock['Value'].decode())
                        logger.debug(f"Lock held by node: {current_metadata.get('node_id', 'unknown')}")
                    
                    # Wait a bit before retrying
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.warning(f"Lock acquisition attempt failed: {e}")
                time.sleep(0.1)
        
        # Cleanup session if lock acquisition failed
        try:
            self.client.session.destroy(session_id)
        except:
            pass
        
        logger.warning(f"❌ Failed to acquire Consul lock for {resource} after {timeout}s")
        return None
    
    def release_lock(self, lock_info: Dict) -> bool:
        """
        Release distributed lock by destroying session
        
        Args:
            lock_info: Lock information from acquire_lock
            
        Returns:
            True if successfully released
        """
        try:
            session_id = lock_info['session_id']
            
            # Destroying session automatically releases all locks held by it
            success = self.client.session.destroy(session_id)
            
            if success:
                logger.info(f"🔓 Consul lock released: {lock_info['resource']}")
                return True
            else:
                logger.warning(f"⚠️ Failed to destroy session: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to release Consul lock: {e}")
            return False
    
    @contextmanager
    def lock_context(self, resource: str, ttl: int = 30, timeout: int = 10):
        """
        Context manager for automatic lock management
        
        Usage:
            with consul_lock.lock_context("resource_name"):
                # Critical section
                pass
        """
        lock_info = self.acquire_lock(resource, ttl, timeout)
        if not lock_info:
            raise ConsulLockError(f"Failed to acquire lock for {resource}")
        
        try:
            yield lock_info
        finally:
            self.release_lock(lock_info)
    
    def get_all_locks(self) -> List[Dict]:
        """Get information about all active locks"""
        try:
            _, locks = self.client.kv.get('locks/', recurse=True)
            if not locks:
                return []
            
            active_locks = []
            for lock in locks:
                if lock['Session']:  # Only active locks
                    try:
                        metadata = json.loads(lock['Value'].decode())
                        lock_info = {
                            'key': lock['Key'],
                            'session_id': lock['Session'],
                            'metadata': metadata
                        }
                        active_locks.append(lock_info)
                    except json.JSONDecodeError:
                        continue
            
            return active_locks
            
        except Exception as e:
            logger.error(f"Failed to get lock information: {e}")
            return []

class SwiggyDeliveryCoordinator:
    """
    Swiggy delivery coordination using Consul locks
    
    Mumbai Story: Swiggy के पास multiple delivery partners होते हैं और same area
    में coordination की जरुरत होती है. Peak hours में traffic, weather updates,
    और delivery optimization के लिए Consul locks का use होता है!
    """
    
    def __init__(self, consul_lock: ConsulDistributedLock):
        self.consul_lock = consul_lock
        self.delivery_zones = {
            'Bandra_West': {'active_deliveries': 0, 'max_capacity': 10},
            'Andheri_East': {'active_deliveries': 0, 'max_capacity': 15},
            'Powai': {'active_deliveries': 0, 'max_capacity': 8},
            'Lower_Parel': {'active_deliveries': 0, 'max_capacity': 12},
            'Kurla_West': {'active_deliveries': 0, 'max_capacity': 9}
        }
        
        self.delivery_partners = {
            f"partner_{i:03d}": {
                'name': f"राहुल {i:03d}",
                'status': 'available',
                'current_zone': None,
                'deliveries_completed': 0,
                'rating': 4.0 + (i % 10) * 0.1
            }
            for i in range(30)
        }
        
        self.coordination_stats = {
            'delivery_requests': 0,
            'successful_assignments': 0,
            'zone_capacity_conflicts': 0,
            'partner_conflicts_prevented': 0
        }
    
    def assign_delivery(self, order_id: str, restaurant_zone: str, delivery_address_zone: str,
                       estimated_time: int = 30) -> Dict:
        """
        Assign delivery with zone capacity coordination
        
        Args:
            order_id: Order identifier
            restaurant_zone: Restaurant location zone
            delivery_address_zone: Delivery address zone
            estimated_time: Estimated delivery time in minutes
            
        Returns:
            Assignment result
        """
        self.coordination_stats['delivery_requests'] += 1
        
        # Lock the delivery zones to coordinate capacity
        zones_to_lock = list(set([restaurant_zone, delivery_address_zone]))
        zone_lock_resource = f"delivery_zones_{'_'.join(sorted(zones_to_lock))}"
        
        try:
            with self.consul_lock.lock_context(zone_lock_resource, ttl=60, timeout=15):
                # Check zone capacity
                for zone in zones_to_lock:
                    if zone not in self.delivery_zones:
                        return {
                            'success': False,
                            'message': f'Unknown delivery zone: {zone}',
                            'error_code': 'INVALID_ZONE'
                        }
                    
                    zone_info = self.delivery_zones[zone]
                    if zone_info['active_deliveries'] >= zone_info['max_capacity']:
                        self.coordination_stats['zone_capacity_conflicts'] += 1
                        return {
                            'success': False,
                            'message': f'Delivery capacity full in {zone}',
                            'error_code': 'ZONE_CAPACITY_FULL'
                        }
                
                # Find available delivery partner
                available_partners = [
                    partner for partner in self.delivery_partners.values()
                    if partner['status'] == 'available'
                ]
                
                if not available_partners:
                    return {
                        'success': False,
                        'message': 'No delivery partners available',
                        'error_code': 'NO_PARTNERS_AVAILABLE'
                    }
                
                # Select best partner (highest rating)
                selected_partner = max(available_partners, key=lambda p: p['rating'])
                partner_id = next(
                    pid for pid, p in self.delivery_partners.items() 
                    if p == selected_partner
                )
                
                # Now lock the specific partner to prevent conflicts
                partner_lock_resource = f"delivery_partner_{partner_id}"
                
                try:
                    with self.consul_lock.lock_context(partner_lock_resource, ttl=45, timeout=5):
                        # Double-check partner availability
                        if self.delivery_partners[partner_id]['status'] != 'available':
                            return {
                                'success': False,
                                'message': 'Selected partner no longer available',
                                'error_code': 'PARTNER_BUSY'
                            }
                        
                        # Assign delivery
                        self.delivery_partners[partner_id]['status'] = 'busy'
                        self.delivery_partners[partner_id]['current_zone'] = restaurant_zone
                        
                        # Update zone capacities
                        for zone in zones_to_lock:
                            self.delivery_zones[zone]['active_deliveries'] += 1
                        
                        delivery_assignment = {
                            'order_id': order_id,
                            'partner_id': partner_id,
                            'partner_name': selected_partner['name'],
                            'restaurant_zone': restaurant_zone,
                            'delivery_zone': delivery_address_zone,
                            'estimated_time': estimated_time,
                            'assigned_at': time.time()
                        }
                        
                        self.coordination_stats['successful_assignments'] += 1
                        self.coordination_stats['partner_conflicts_prevented'] += 1
                        
                        # Schedule delivery completion
                        completion_delay = estimated_time / 100.0  # Scale down for simulation
                        threading.Timer(
                            completion_delay,
                            lambda: self._complete_delivery(delivery_assignment)
                        ).start()
                        
                        logger.info(f"🛵 Delivery assigned: {order_id} -> {selected_partner['name']} ({restaurant_zone} → {delivery_address_zone})")
                        
                        return {
                            'success': True,
                            'assignment': delivery_assignment,
                            'message': f"Delivery assigned to {selected_partner['name']}"
                        }
                        
                except ConsulLockError:
                    return {
                        'success': False,
                        'message': 'Partner assignment conflict - please retry',
                        'error_code': 'PARTNER_LOCK_TIMEOUT'
                    }
                
        except ConsulLockError:
            return {
                'success': False,
                'message': 'Zone coordination busy - please retry',
                'error_code': 'ZONE_LOCK_TIMEOUT'
            }
    
    def _complete_delivery(self, delivery_info: Dict):
        """Complete delivery and update capacities"""
        partner_id = delivery_info['partner_id']
        restaurant_zone = delivery_info['restaurant_zone']
        delivery_zone = delivery_info['delivery_zone']
        
        zones_to_unlock = list(set([restaurant_zone, delivery_zone]))
        zone_lock_resource = f"delivery_zones_{'_'.join(sorted(zones_to_unlock))}"
        
        try:
            with self.consul_lock.lock_context(zone_lock_resource, ttl=30, timeout=10):
                # Update partner status
                if partner_id in self.delivery_partners:
                    self.delivery_partners[partner_id]['status'] = 'available'
                    self.delivery_partners[partner_id]['current_zone'] = None
                    self.delivery_partners[partner_id]['deliveries_completed'] += 1
                
                # Update zone capacities
                for zone in zones_to_unlock:
                    if zone in self.delivery_zones:
                        self.delivery_zones[zone]['active_deliveries'] = max(
                            0,
                            self.delivery_zones[zone]['active_deliveries'] - 1
                        )
                
                logger.info(f"✅ Delivery completed: {delivery_info['order_id']} by {partner_id}")
                
        except ConsulLockError:
            logger.warning(f"⚠️ Failed to update delivery completion for {delivery_info['order_id']}")
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        available_partners = len([
            p for p in self.delivery_partners.values() 
            if p['status'] == 'available'
        ])
        
        busy_partners = len([
            p for p in self.delivery_partners.values() 
            if p['status'] == 'busy'
        ])
        
        zone_utilization = {
            zone: f"{info['active_deliveries']}/{info['max_capacity']}"
            for zone, info in self.delivery_zones.items()
        }
        
        success_rate = (
            self.coordination_stats['successful_assignments'] / 
            max(1, self.coordination_stats['delivery_requests'])
        ) * 100
        
        return {
            'partners': {
                'total': len(self.delivery_partners),
                'available': available_partners,
                'busy': busy_partners
            },
            'zones': zone_utilization,
            'stats': {
                **self.coordination_stats,
                'success_rate': success_rate
            }
        }

def simulate_swiggy_peak_hour():
    """
    Simulate Swiggy peak hour delivery coordination
    
    Mumbai Scenario: Lunch time (12-2 PM) और dinner time (7-10 PM) में orders का
    volume बहुत बढ़ जाता है. Consul locks help coordinate deliveries efficiently!
    """
    # Initialize Consul lock
    consul_config = ConsulConfig(host='localhost', port=8500)
    
    try:
        consul_lock = ConsulDistributedLock(consul_config)
    except ConsulLockError as e:
        logger.error("Failed to connect to Consul. Please ensure Consul is running on localhost:8500")
        logger.error("Start Consul with: consul agent -dev")
        return
    
    delivery_coordinator = SwiggyDeliveryCoordinator(consul_lock)
    
    # Mumbai zones and popular restaurants
    orders_to_process = [
        ('ORD001', 'Bandra_West', 'Bandra_West', 25),
        ('ORD002', 'Andheri_East', 'Powai', 45),
        ('ORD003', 'Lower_Parel', 'Lower_Parel', 20),
        ('ORD004', 'Kurla_West', 'Andheri_East', 35),
        ('ORD005', 'Powai', 'Powai', 15),
        ('ORD006', 'Bandra_West', 'Lower_Parel', 40),
        ('ORD007', 'Andheri_East', 'Andheri_East', 30),
        ('ORD008', 'Powai', 'Kurla_West', 50),
        ('ORD009', 'Lower_Parel', 'Bandra_West', 35),
        ('ORD010', 'Kurla_West', 'Kurla_West', 20),
        ('ORD011', 'Bandra_West', 'Andheri_East', 55),
        ('ORD012', 'Powai', 'Lower_Parel', 40),
        ('ORD013', 'Andheri_East', 'Kurla_West', 45),
        ('ORD014', 'Lower_Parel', 'Powai', 30),
        ('ORD015', 'Kurla_West', 'Bandra_West', 50),
    ]
    
    def process_order(order_data):
        """Process single order assignment"""
        order_id, restaurant_zone, delivery_zone, est_time = order_data
        result = delivery_coordinator.assign_delivery(
            order_id, restaurant_zone, delivery_zone, est_time
        )
        
        if result['success']:
            logger.debug(f"✅ {order_id}: {restaurant_zone} → {delivery_zone}")
        else:
            logger.debug(f"❌ {order_id}: {result['message']}")
        
        return result
    
    # Process orders concurrently
    threads = []
    
    logger.info(f"🍽️ Starting Swiggy peak hour simulation ({len(orders_to_process)} orders)...")
    start_time = time.time()
    
    # Create threads for concurrent order processing
    for order_data in orders_to_process:
        thread = threading.Thread(target=process_order, args=(order_data,))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Small delay between orders
    
    # Wait for all orders to complete
    for thread in threads:
        thread.join()
    
    # Wait for deliveries to complete
    time.sleep(2)
    
    end_time = time.time()
    
    # Show results
    status = delivery_coordinator.get_system_status()
    
    logger.info(f"\n📊 Swiggy Peak Hour Results:")
    logger.info(f"Orders processed: {status['stats']['delivery_requests']}")
    logger.info(f"Successful assignments: {status['stats']['successful_assignments']}")
    logger.info(f"Zone capacity conflicts: {status['stats']['zone_capacity_conflicts']}")
    logger.info(f"Partner conflicts prevented: {status['stats']['partner_conflicts_prevented']}")
    logger.info(f"Success rate: {status['stats']['success_rate']:.2f}%")
    logger.info(f"Available partners: {status['partners']['available']}/{status['partners']['total']}")
    logger.info(f"Processing time: {end_time - start_time:.2f} seconds")
    
    logger.info(f"\n🏙️ Zone utilization:")
    for zone, utilization in status['zones'].items():
        logger.info(f"{zone}: {utilization}")
    
    # Show active locks
    active_locks = consul_lock.get_all_locks()
    if active_locks:
        logger.info(f"\n🔒 Active locks: {len(active_locks)}")
        for lock in active_locks[:5]:  # Show first 5 locks
            logger.info(f"  {lock['key']} (session: {lock['session_id'][:8]}...)")

if __name__ == "__main__":
    try:
        simulate_swiggy_peak_hour()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()