#!/usr/bin/env python3
"""
ZooKeeper Distributed Lock Manager
=================================

Production-ready ZooKeeper-based distributed locking implementation.
Used by companies like LinkedIn, Netflix for coordination services.

Mumbai Context: ZooKeeper = Mumbai के traffic signals का centralized control system!
सभी nodes को coordination के लिए central authority की जरुरत होती है.

Real-world usage:
- Flipkart's distributed configuration management
- Ola's driver assignment coordination
- PayU's transaction sequencing
"""

import time
import threading
import logging
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from kazoo.client import KazooClient
from kazoo.protocol.states import EventType, WatchedEvent
from kazoo.exceptions import NodeExistsError, NoNodeError
import uuid
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ZookeeperConfig:
    """ZooKeeper connection configuration"""
    hosts: str = "localhost:2181"
    timeout: int = 10
    retry_max_delay: int = 1000

class ZookeeperLockError(Exception):
    """ZooKeeper lock specific exceptions"""
    pass

class ZookeeperDistributedLock:
    """
    ZooKeeper-based distributed lock implementation
    
    Mumbai Metaphor: यह Mumbai traffic control room जैसा है - सभी signals
    एक central system से coordinate होते हैं. ZooKeeper भी वैसे ही सभी
    distributed processes को coordinate करता है!
    """
    
    def __init__(self, config: ZookeeperConfig, lock_path: str = "/locks"):
        self.config = config
        self.lock_path = lock_path
        self.client = None
        self.session_id = str(uuid.uuid4())
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to ZooKeeper cluster"""
        try:
            self.client = KazooClient(
                hosts=self.config.hosts,
                timeout=self.config.timeout
            )
            
            # Add connection state listener
            self.client.add_listener(self._connection_listener)
            self.client.start(timeout=self.config.timeout)
            
            # Ensure lock root path exists
            self.client.ensure_path(self.lock_path)
            
            self.connected = True
            logger.info(f"✅ Connected to ZooKeeper: {self.config.hosts}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ZooKeeper: {e}")
            return False
    
    def _connection_listener(self, state):
        """Handle ZooKeeper connection state changes"""
        if state == 'CONNECTED':
            self.connected = True
            logger.info("🔗 ZooKeeper connected")
        elif state == 'LOST':
            self.connected = False
            logger.warning("⚠️  ZooKeeper connection lost")
        elif state == 'SUSPENDED':
            logger.warning("⏸️  ZooKeeper connection suspended")
    
    def acquire_lock(self, resource: str, timeout: int = 30) -> Optional[Dict]:
        """
        Acquire distributed lock using ZooKeeper
        
        Algorithm:
        1. Create sequential ephemeral node
        2. Check if we have the lowest sequence number
        3. If not, watch the node just before us
        4. When that node disappears, we get the lock
        
        Args:
            resource: Resource name to lock
            timeout: Lock acquisition timeout in seconds
            
        Returns:
            Lock info if successful, None otherwise
        """
        if not self.connected:
            raise ZookeeperLockError("Not connected to ZooKeeper")
        
        resource_path = f"{self.lock_path}/{resource}"
        self.client.ensure_path(resource_path)
        
        # Create sequential ephemeral node
        lock_node_prefix = f"{resource_path}/lock_"
        lock_metadata = {
            'session_id': self.session_id,
            'acquired_at': time.time(),
            'timeout': timeout
        }
        
        try:
            actual_path = self.client.create(
                path=lock_node_prefix,
                value=json.dumps(lock_metadata).encode('utf-8'),
                ephemeral=True,
                sequence=True
            )
            
            # Extract sequence number
            sequence_num = int(actual_path.split('_')[-1])
            
            # Wait for lock acquisition
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Get all children and sort them
                children = sorted(self.client.get_children(resource_path))
                
                if not children:
                    logger.warning("No children found in lock path")
                    break
                
                # Find our position
                our_node = actual_path.split('/')[-1]
                if our_node not in children:
                    logger.error("Our node disappeared!")
                    return None
                
                our_index = children.index(our_node)
                
                # If we're first, we have the lock!
                if our_index == 0:
                    lock_info = {
                        'resource': resource,
                        'lock_path': actual_path,
                        'acquired_at': time.time(),
                        'session_id': self.session_id,
                        'sequence_num': sequence_num
                    }
                    logger.info(f"🔒 Lock acquired: {resource} (path: {actual_path})")
                    return lock_info
                
                # Watch the node before us
                prev_node_path = f"{resource_path}/{children[our_index - 1]}"
                watch_event = threading.Event()
                
                def watch_callback(event: WatchedEvent):
                    if event.type == EventType.DELETED:
                        watch_event.set()
                
                # Set watch and check if node still exists
                if self.client.exists(prev_node_path, watch=watch_callback):
                    logger.info(f"⏳ Waiting for lock, watching: {prev_node_path}")
                    # Wait for the previous node to be deleted or timeout
                    remaining_time = timeout - (time.time() - start_time)
                    watch_event.wait(timeout=remaining_time)
                # If node doesn't exist, loop again to check our status
            
            # Timeout occurred
            logger.warning(f"⏰ Lock acquisition timeout for {resource}")
            self._cleanup_lock_node(actual_path)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to acquire lock for {resource}: {e}")
            return None
    
    def release_lock(self, lock_info: Dict) -> bool:
        """
        Release distributed lock
        
        Args:
            lock_info: Lock information from acquire_lock
            
        Returns:
            True if successfully released
        """
        try:
            lock_path = lock_info['lock_path']
            self.client.delete(lock_path)
            logger.info(f"🔓 Lock released: {lock_info['resource']}")
            return True
            
        except NoNodeError:
            logger.warning("Lock node already deleted")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to release lock: {e}")
            return False
    
    def _cleanup_lock_node(self, node_path: str):
        """Clean up lock node if it exists"""
        try:
            if self.client.exists(node_path):
                self.client.delete(node_path)
        except Exception:
            pass  # Best effort cleanup
    
    def disconnect(self):
        """Disconnect from ZooKeeper"""
        if self.client:
            self.client.stop()
            self.client.close()
            self.connected = False
            logger.info("Disconnected from ZooKeeper")

class FlipkartInventoryManager:
    """
    Flipkart inventory management using ZooKeeper locks
    
    Mumbai Story: Big Billion Day के time पर हजारों customers एक साथ same product
    order करते हैं. ZooKeeper locks ensure करते हैं कि inventory correctly managed हो!
    """
    
    def __init__(self, zk_lock_manager: ZookeeperDistributedLock):
        self.zk_lock = zk_lock_manager
        self.inventory = {
            'smartphone_xyz_128gb': 100,
            'laptop_abc_16gb': 50,
            'headphones_premium': 200,
            'smartwatch_sport': 75
        }
        self.stats = {
            'orders_processed': 0,
            'inventory_conflicts_prevented': 0,
            'out_of_stock_scenarios': 0
        }
    
    def process_order(self, product_id: str, quantity: int, customer_id: str) -> Dict:
        """
        Process order with inventory locking
        
        Args:
            product_id: Product identifier
            quantity: Quantity to order
            customer_id: Customer identifier
            
        Returns:
            Order result
        """
        resource = f"inventory_{product_id}"
        
        # Acquire lock for inventory update
        lock_info = self.zk_lock.acquire_lock(resource, timeout=10)
        
        if not lock_info:
            return {
                'success': False,
                'message': 'Unable to process order - system busy',
                'error_code': 'LOCK_TIMEOUT'
            }
        
        try:
            self.stats['orders_processed'] += 1
            
            # Check inventory
            current_stock = self.inventory.get(product_id, 0)
            
            if current_stock < quantity:
                self.stats['out_of_stock_scenarios'] += 1
                return {
                    'success': False,
                    'message': f'Insufficient stock. Available: {current_stock}, Requested: {quantity}',
                    'error_code': 'OUT_OF_STOCK'
                }
            
            # Simulate processing time
            time.sleep(0.1)
            
            # Update inventory
            self.inventory[product_id] = current_stock - quantity
            
            order_id = f"ORD_{int(time.time())}_{customer_id[-4:]}"
            
            logger.info(f"📦 Order processed: {order_id} - {product_id} x{quantity} for {customer_id}")
            
            return {
                'success': True,
                'order_id': order_id,
                'product_id': product_id,
                'quantity': quantity,
                'remaining_stock': self.inventory[product_id],
                'customer_id': customer_id
            }
            
        finally:
            # Always release lock
            self.zk_lock.release_lock(lock_info)
            self.stats['inventory_conflicts_prevented'] += 1
    
    def get_inventory_status(self) -> Dict:
        """Get current inventory status"""
        return {
            'inventory': self.inventory.copy(),
            'stats': self.stats.copy()
        }
    
    def restock_item(self, product_id: str, quantity: int) -> bool:
        """
        Restock inventory item with locking
        
        Args:
            product_id: Product to restock
            quantity: Quantity to add
            
        Returns:
            Success status
        """
        resource = f"inventory_{product_id}"
        lock_info = self.zk_lock.acquire_lock(resource, timeout=5)
        
        if not lock_info:
            logger.warning(f"Failed to acquire lock for restocking {product_id}")
            return False
        
        try:
            current_stock = self.inventory.get(product_id, 0)
            self.inventory[product_id] = current_stock + quantity
            logger.info(f"📈 Restocked {product_id}: +{quantity} (Total: {self.inventory[product_id]})")
            return True
        finally:
            self.zk_lock.release_lock(lock_info)

def simulate_big_billion_day():
    """
    Simulate Flipkart Big Billion Day concurrent orders
    
    Mumbai Scenario: रात के 12 बजे sale शुरू होते ही लाखों users एक साथ
    orders place करते हैं. ZooKeeper distributed locks ensure consistency!
    """
    # Initialize ZooKeeper lock manager
    zk_config = ZookeeperConfig(hosts="localhost:2181")
    zk_lock = ZookeeperDistributedLock(zk_config)
    
    if not zk_lock.connect():
        logger.error("Failed to connect to ZooKeeper. Please ensure ZooKeeper is running.")
        return
    
    inventory_manager = FlipkartInventoryManager(zk_lock)
    
    # Popular product during sale
    popular_product = 'smartphone_xyz_128gb'
    
    def customer_order(customer_id: str, quantity: int = 1):
        """Single customer order attempt"""
        result = inventory_manager.process_order(
            popular_product, 
            quantity, 
            customer_id
        )
        logger.info(f"Customer {customer_id}: {result.get('message', result)}")
        return result
    
    # Simulate concurrent customers
    threads = []
    customers = [f"customer_{i:04d}" for i in range(50)]
    
    logger.info("🛒 Starting Big Billion Day simulation...")
    start_time = time.time()
    
    # Create threads for concurrent orders
    for customer_id in customers:
        # Some customers order multiple items
        quantity = 2 if customer_id.endswith(('0', '5')) else 1
        thread = threading.Thread(target=customer_order, args=(customer_id, quantity))
        threads.append(thread)
        thread.start()
        time.sleep(0.01)  # Simulate real-world request pattern
    
    # Wait for all orders to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    # Show final results
    status = inventory_manager.get_inventory_status()
    logger.info(f"\n📊 Big Billion Day Results:")
    logger.info(f"Orders processed: {status['stats']['orders_processed']}")
    logger.info(f"Conflicts prevented: {status['stats']['inventory_conflicts_prevented']}")
    logger.info(f"Out of stock scenarios: {status['stats']['out_of_stock_scenarios']}")
    logger.info(f"Final {popular_product} stock: {status['inventory'][popular_product]}")
    logger.info(f"Processing time: {end_time - start_time:.2f} seconds")
    
    # Cleanup
    zk_lock.disconnect()

if __name__ == "__main__":
    try:
        simulate_big_billion_day()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")