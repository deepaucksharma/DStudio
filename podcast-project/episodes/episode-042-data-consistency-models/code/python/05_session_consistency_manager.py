"""
Session Consistency Manager
Ensures user sees monotonic progress in their session
Example: Amazon shopping cart, Gmail inbox updates
"""

import time
import uuid
import threading
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')

class ReadType(Enum):
    READ_YOUR_WRITES = "READ_YOUR_WRITES"
    MONOTONIC_READS = "MONOTONIC_READS" 
    WRITES_FOLLOW_READS = "WRITES_FOLLOW_READS"

@dataclass
class Operation:
    """
    Single read/write operation
    """
    op_id: str
    session_id: str
    operation_type: str  # "READ" or "WRITE"
    key: str
    value: Any
    timestamp: float
    version: int
    replica_id: str

@dataclass
class UserSession:
    """
    User ka session state - Amazon shopping cart jaisa
    """
    session_id: str
    user_id: str
    last_write_timestamp: float = 0.0
    last_read_version: Dict[str, int] = field(default_factory=dict)
    session_writes: Set[str] = field(default_factory=set)
    operation_history: List[Operation] = field(default_factory=list)
    preferred_replica: str = "mumbai"

@dataclass
class DataItem:
    """
    Storage mein data item
    """
    key: str
    value: Any
    version: int
    last_modified: float
    last_writer_session: str

class SessionConsistencyManager:
    """
    Session consistency ensure karne wala system
    Amazon/Flipkart jaisa e-commerce experience
    """
    
    def __init__(self):
        self.replicas: Dict[str, Dict[str, DataItem]] = {}
        self.sessions: Dict[str, UserSession] = {}
        self.lock = threading.RLock()
        self.sync_delay = 0.1  # Inter-replica sync delay
        
        # Initialize replicas - Indian cities
        self.replicas = {
            "mumbai": {},
            "delhi": {},
            "bangalore": {},
            "chennai": {},
            "hyderabad": {}
        }
        
    def create_session(self, user_id: str, preferred_replica: str = "mumbai") -> str:
        """
        Naya user session create karo - login jaisa
        """
        session_id = f"session_{str(uuid.uuid4())[:8]}"
        
        with self.lock:
            self.sessions[session_id] = UserSession(
                session_id=session_id,
                user_id=user_id,
                preferred_replica=preferred_replica
            )
            
        logging.info(f"Session created: {session_id} for user {user_id}")
        return session_id
        
    def write_data(self, session_id: str, key: str, value: Any, 
                  replica_id: Optional[str] = None) -> bool:
        """
        Data write karo - shopping cart mein item add karna jaisa
        Guarantees: Read-your-writes consistency
        """
        if session_id not in self.sessions:
            logging.error(f"Session {session_id} not found")
            return False
            
        session = self.sessions[session_id]
        target_replica = replica_id or session.preferred_replica
        
        with self.lock:
            # Generate new version
            current_item = self.replicas[target_replica].get(key)
            new_version = (current_item.version + 1) if current_item else 1
            
            # Create new data item
            data_item = DataItem(
                key=key,
                value=value,
                version=new_version,
                last_modified=time.time(),
                last_writer_session=session_id
            )
            
            # Write to target replica
            self.replicas[target_replica][key] = data_item
            
            # Update session state
            session.last_write_timestamp = data_item.last_modified
            session.session_writes.add(key)
            
            # Log operation
            operation = Operation(
                op_id=str(uuid.uuid4())[:8],
                session_id=session_id,
                operation_type="WRITE",
                key=key,
                value=value,
                timestamp=data_item.last_modified,
                version=new_version,
                replica_id=target_replica
            )
            session.operation_history.append(operation)
            
            logging.info(f"Write: {key}={value} v{new_version} by {session_id} in {target_replica}")
            
            # Async propagation to other replicas
            self._schedule_propagation(key, data_item, target_replica)
            
        return True
        
    def read_data(self, session_id: str, key: str, 
                 replica_id: Optional[str] = None) -> Optional[Any]:
        """
        Data read karo with session consistency guarantees
        Amazon cart items consistent dikhenge session mein
        """
        if session_id not in self.sessions:
            logging.error(f"Session {session_id} not found")
            return None
            
        session = self.sessions[session_id]
        target_replica = replica_id or session.preferred_replica
        
        with self.lock:
            # Check read-your-writes consistency
            if key in session.session_writes:
                suitable_replica = self._find_suitable_replica_for_read(session, key)
                if suitable_replica:
                    target_replica = suitable_replica
                else:
                    # Force read from replica with user's writes
                    for replica_name, replica_data in self.replicas.items():
                        item = replica_data.get(key)
                        if item and item.last_writer_session == session_id:
                            target_replica = replica_name
                            break
                            
            # Get data from target replica
            replica_data = self.replicas[target_replica]
            data_item = replica_data.get(key)
            
            if data_item:
                # Update session read state for monotonic reads
                session.last_read_version[key] = data_item.version
                
                # Log operation
                operation = Operation(
                    op_id=str(uuid.uuid4())[:8],
                    session_id=session_id,
                    operation_type="READ",
                    key=key,
                    value=data_item.value,
                    timestamp=time.time(),
                    version=data_item.version,
                    replica_id=target_replica
                )
                session.operation_history.append(operation)
                
                logging.info(f"Read: {key}={data_item.value} v{data_item.version} by {session_id} from {target_replica}")
                return data_item.value
            else:
                logging.warning(f"Key {key} not found in {target_replica}")
                return None
                
    def _find_suitable_replica_for_read(self, session: UserSession, key: str) -> Optional[str]:
        """
        Suitable replica find karo for session consistency
        """
        last_read_version = session.last_read_version.get(key, 0)
        
        # Find replica with version >= last read version (monotonic reads)
        for replica_name, replica_data in self.replicas.items():
            item = replica_data.get(key)
            if item and item.version >= last_read_version:
                # Also check read-your-writes if applicable
                if key in session.session_writes:
                    if item.last_writer_session == session.session_id:
                        return replica_name
                else:
                    return replica_name
                    
        return None
        
    def _schedule_propagation(self, key: str, data_item: DataItem, source_replica: str):
        """
        Async propagation to other replicas
        """
        def propagate():
            time.sleep(self.sync_delay)  # Network delay
            
            with self.lock:
                for replica_name, replica_data in self.replicas.items():
                    if replica_name == source_replica:
                        continue
                        
                    current_item = replica_data.get(key)
                    
                    # Only propagate if version is newer
                    if not current_item or data_item.version > current_item.version:
                        replica_data[key] = data_item
                        logging.info(f"Propagated {key} v{data_item.version} to {replica_name}")
                        
        # Start propagation in background
        thread = threading.Thread(target=propagate)
        thread.daemon = True
        thread.start()
        
    def get_session_state(self, session_id: str) -> Dict:
        """
        Session ka current state dekho
        """
        if session_id not in self.sessions:
            return {}
            
        session = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "preferred_replica": session.preferred_replica,
            "writes_count": len(session.session_writes),
            "operations_count": len(session.operation_history),
            "last_write_time": session.last_write_timestamp,
            "read_versions": dict(session.last_read_version)
        }
        
    def verify_session_consistency(self, session_id: str) -> Dict:
        """
        Session consistency verify karo
        """
        if session_id not in self.sessions:
            return {"error": "Session not found"}
            
        session = self.sessions[session_id]
        violations = []
        
        # Check read-your-writes violations
        for key in session.session_writes:
            # Check if user can read their own writes
            value = self.read_data(session_id, key)
            if value is None:
                violations.append({
                    "type": "read_your_writes_violation",
                    "key": key,
                    "issue": "Cannot read own write"
                })
                
        # Check monotonic reads violations
        read_operations = [op for op in session.operation_history if op.operation_type == "READ"]
        
        for i in range(1, len(read_operations)):
            current_op = read_operations[i]
            previous_op = read_operations[i-1]
            
            if current_op.key == previous_op.key and current_op.version < previous_op.version:
                violations.append({
                    "type": "monotonic_reads_violation",
                    "key": current_op.key,
                    "current_version": current_op.version,
                    "previous_version": previous_op.version
                })
                
        return {
            "session_id": session_id,
            "consistent": len(violations) == 0,
            "violations": violations
        }

class FlipkartShoppingCart:
    """
    Flipkart jaisa shopping cart using session consistency
    """
    
    def __init__(self):
        self.consistency_manager = SessionConsistencyManager()
        
    def user_login(self, user_id: str, location: str = "mumbai") -> str:
        """
        User login - nearest server se connect
        """
        location_to_replica = {
            "mumbai": "mumbai",
            "delhi": "delhi", 
            "bangalore": "bangalore",
            "chennai": "chennai",
            "hyderabad": "hyderabad"
        }
        
        replica = location_to_replica.get(location, "mumbai")
        return self.consistency_manager.create_session(user_id, replica)
        
    def add_to_cart(self, session_id: str, product_id: str, quantity: int) -> bool:
        """
        Cart mein item add karo
        """
        cart_key = f"cart:{session_id}"
        
        # Get current cart
        current_cart = self.consistency_manager.read_data(session_id, cart_key) or {}
        
        # Update cart
        current_cart[product_id] = current_cart.get(product_id, 0) + quantity
        
        # Write back to cart
        return self.consistency_manager.write_data(session_id, cart_key, current_cart)
        
    def remove_from_cart(self, session_id: str, product_id: str, quantity: int = None) -> bool:
        """
        Cart se item remove karo
        """
        cart_key = f"cart:{session_id}"
        
        # Get current cart
        current_cart = self.consistency_manager.read_data(session_id, cart_key) or {}
        
        if product_id in current_cart:
            if quantity is None:
                del current_cart[product_id]
            else:
                current_cart[product_id] = max(0, current_cart[product_id] - quantity)
                if current_cart[product_id] == 0:
                    del current_cart[product_id]
                    
            return self.consistency_manager.write_data(session_id, cart_key, current_cart)
            
        return False
        
    def get_cart(self, session_id: str) -> Dict:
        """
        Current cart state dekho
        """
        cart_key = f"cart:{session_id}"
        return self.consistency_manager.read_data(session_id, cart_key) or {}
        
    def save_address(self, session_id: str, address: Dict) -> bool:
        """
        Delivery address save karo
        """
        address_key = f"address:{session_id}"
        return self.consistency_manager.write_data(session_id, address_key, address)
        
    def get_address(self, session_id: str) -> Optional[Dict]:
        """
        Saved address retrieve karo
        """
        address_key = f"address:{session_id}"
        return self.consistency_manager.read_data(session_id, address_key)

def demonstrate_session_consistency():
    """
    Real-world demo: Flipkart shopping experience
    Session consistency ki zarurat
    """
    print("=== Session Consistency Demo: Flipkart Shopping Cart ===")
    
    flipkart = FlipkartShoppingCart()
    
    # User login from different locations
    print("\n=== Users Login from Different Cities ===")
    rahul_session = flipkart.user_login("rahul", "mumbai")
    priya_session = flipkart.user_login("priya", "delhi") 
    vikram_session = flipkart.user_login("vikram", "bangalore")
    
    print(f"Rahul session: {rahul_session} (Mumbai)")
    print(f"Priya session: {priya_session} (Delhi)")
    print(f"Vikram session: {vikram_session} (Bangalore)")
    
    # Shopping activities
    print("\n=== Shopping Activities ===")
    
    # Rahul adds items to cart
    print("Rahul's shopping:")
    flipkart.add_to_cart(rahul_session, "iphone_13", 1)
    flipkart.add_to_cart(rahul_session, "airpods", 1)
    flipkart.add_to_cart(rahul_session, "phone_case", 2)
    
    rahul_cart = flipkart.get_cart(rahul_session)
    print(f"  Cart after adding: {rahul_cart}")
    
    # Rahul removes an item
    flipkart.remove_from_cart(rahul_session, "phone_case", 1)
    rahul_cart = flipkart.get_cart(rahul_session)
    print(f"  Cart after removing: {rahul_cart}")
    
    # Priya's shopping
    print("\nPriya's shopping:")
    flipkart.add_to_cart(priya_session, "laptop", 1)
    flipkart.add_to_cart(priya_session, "mouse", 1)
    
    priya_cart = flipkart.get_cart(priya_session)
    print(f"  Cart: {priya_cart}")
    
    # Address management
    print("\n=== Address Management ===")
    
    rahul_address = {
        "name": "Rahul Sharma",
        "street": "123 Linking Road",
        "city": "Mumbai",
        "pincode": "400050"
    }
    
    flipkart.save_address(rahul_session, rahul_address)
    saved_address = flipkart.get_address(rahul_session)
    print(f"Rahul's saved address: {saved_address}")
    
    # Simulate network issues and replica switches
    print("\n=== Network Issues Simulation ===")
    
    # Multiple rapid cart updates (testing read-your-writes)
    print("Rapid cart updates:")
    for i in range(5):
        flipkart.add_to_cart(rahul_session, f"item_{i}", 1)
        cart = flipkart.get_cart(rahul_session)
        print(f"  Update {i+1}: {len(cart)} items in cart")
        
    # Session consistency verification
    print("\n=== Session Consistency Verification ===")
    
    sessions = [rahul_session, priya_session, vikram_session]
    for session in sessions:
        verification = flipkart.consistency_manager.verify_session_consistency(session)
        user_state = flipkart.consistency_manager.get_session_state(session)
        
        status = "✅ CONSISTENT" if verification["consistent"] else "❌ INCONSISTENT"
        print(f"Session {session[:8]}: {status}")
        print(f"  User: {user_state['user_id']}")
        print(f"  Operations: {user_state['operations_count']}")
        print(f"  Writes: {user_state['writes_count']}")
        
        if not verification["consistent"]:
            for violation in verification["violations"]:
                print(f"  Violation: {violation}")
                
    # Demonstrate why session consistency matters
    print("\n=== Why Session Consistency Matters ===")
    print("Scenario: User adds item to cart")
    print("1. User clicks 'Add to Cart'")
    print("2. User immediately checks cart")
    print("3. Without session consistency: Item might not appear")
    print("4. With session consistency: Item always visible to user")
    print()
    print("Real examples:")
    print("- Amazon: Cart items consistent across page refreshes")
    print("- Gmail: Sent emails appear in sent folder immediately") 
    print("- Facebook: Your posts visible to you instantly")
    print("- Banking: Your transfers show up in transaction history")
    
    # Performance metrics
    print("\n=== System Performance Metrics ===")
    
    # Check replica synchronization
    manager = flipkart.consistency_manager
    total_keys = set()
    
    for replica_data in manager.replicas.values():
        total_keys.update(replica_data.keys())
        
    print(f"Total unique keys: {len(total_keys)}")
    
    for replica_name, replica_data in manager.replicas.items():
        sync_percentage = (len(replica_data) / len(total_keys) * 100) if total_keys else 0
        print(f"{replica_name.capitalize()}: {len(replica_data)} keys ({sync_percentage:.1f}% synced)")

if __name__ == "__main__":
    demonstrate_session_consistency()