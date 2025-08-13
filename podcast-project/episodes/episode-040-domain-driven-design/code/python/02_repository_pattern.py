#!/usr/bin/env python3
"""
Domain-Driven Design: Repository Pattern Implementation
======================================================

Production-ready repository pattern implementation for aggregate persistence.
Repository provides an abstraction layer over data persistence mechanisms.

Mumbai Context: यह Mumbai के किसी बड़े office की filing system जैसा है!
Repository = file manager जो जानता है कि कौन सा document कहाँ store किया है.
Domain layer को पता नहीं होता कि data database में है या file में या कहीं और!

Real-world usage:
- Clean separation between domain and infrastructure
- Testable domain logic
- Technology-agnostic domain models
- Complex query abstraction
- Unit of Work pattern implementation
"""

import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Set, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import sqlite3
import json
from decimal import Decimal
import threading

# Import domain models from previous example
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from domain_aggregates import ZomatoOrder, OrderStatus, Money, Address, Phone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recreate essential domain classes for this example
class OrderStatus(Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED" 
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "INR"
    
    def __str__(self):
        return f"₹{self.amount:.2f}"

@dataclass(frozen=True) 
class Address:
    street: str
    area: str
    city: str
    pincode: str
    landmark: Optional[str] = None

# Repository Specifications and Criteria

class Specification(ABC):
    """Base specification for query criteria"""
    
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Check if candidate satisfies the specification"""
        pass
    
    def and_specification(self, other: 'Specification') -> 'Specification':
        """Combine with AND logic"""
        return AndSpecification(self, other)
    
    def or_specification(self, other: 'Specification') -> 'Specification':
        """Combine with OR logic"""
        return OrSpecification(self, other)
    
    def not_specification(self) -> 'Specification':
        """Negate specification"""
        return NotSpecification(self)

class AndSpecification(Specification):
    """AND combination of specifications"""
    
    def __init__(self, spec1: Specification, spec2: Specification):
        self.spec1 = spec1
        self.spec2 = spec2
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.spec1.is_satisfied_by(candidate) and self.spec2.is_satisfied_by(candidate)

class OrSpecification(Specification):
    """OR combination of specifications"""
    
    def __init__(self, spec1: Specification, spec2: Specification):
        self.spec1 = spec1
        self.spec2 = spec2
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.spec1.is_satisfied_by(candidate) or self.spec2.is_satisfied_by(candidate)

class NotSpecification(Specification):
    """NOT specification"""
    
    def __init__(self, spec: Specification):
        self.spec = spec
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return not self.spec.is_satisfied_by(candidate)

# Order-specific specifications

class OrderByCustomerSpecification(Specification):
    """Specification for orders by customer"""
    
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
    
    def is_satisfied_by(self, order) -> bool:
        return hasattr(order, 'customer_id') and order.customer_id == self.customer_id

class OrderByStatusSpecification(Specification):
    """Specification for orders by status"""
    
    def __init__(self, status: OrderStatus):
        self.status = status
    
    def is_satisfied_by(self, order) -> bool:
        return hasattr(order, 'status') and order.status == self.status

class OrderByRestaurantSpecification(Specification):
    """Specification for orders by restaurant"""
    
    def __init__(self, restaurant_id: str):
        self.restaurant_id = restaurant_id
    
    def is_satisfied_by(self, order) -> bool:
        return hasattr(order, 'restaurant_id') and order.restaurant_id == self.restaurant_id

class OrderByDateRangeSpecification(Specification):
    """Specification for orders in date range"""
    
    def __init__(self, start_date: float, end_date: float):
        self.start_date = start_date
        self.end_date = end_date
    
    def is_satisfied_by(self, order) -> bool:
        if not hasattr(order, 'created_at'):
            return False
        return self.start_date <= order.created_at <= self.end_date

class OrderByMinimumAmountSpecification(Specification):
    """Specification for orders above minimum amount"""
    
    def __init__(self, min_amount: Decimal):
        self.min_amount = min_amount
    
    def is_satisfied_by(self, order) -> bool:
        if not hasattr(order, 'get_total_amount'):
            return False
        return order.get_total_amount().amount >= self.min_amount

# Repository interfaces

class Repository(Protocol):
    """Base repository protocol"""
    
    def next_id(self) -> str:
        """Generate next unique identifier"""
        pass

class OrderRepository(Repository):
    """
    Order repository interface
    
    Mumbai Context: यह orders की library जैसा है! यहाँ सभी orders store होते हैं
    और different criteria के basis पर search किया जा सकता है.
    """
    
    @abstractmethod
    def next_id(self) -> str:
        """Generate next order ID"""
        pass
    
    @abstractmethod
    def save(self, order) -> None:
        """Save order to repository"""
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Any]:
        """Find order by ID"""
        pass
    
    @abstractmethod
    def find_by_specification(self, specification: Specification) -> List[Any]:
        """Find orders matching specification"""
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Any]:
        """Find all orders by customer"""
        pass
    
    @abstractmethod
    def find_active_orders(self) -> List[Any]:
        """Find all active (non-cancelled/delivered) orders"""
        pass
    
    @abstractmethod
    def count_by_specification(self, specification: Specification) -> int:
        """Count orders matching specification"""
        pass
    
    @abstractmethod
    def remove(self, order_id: str) -> bool:
        """Remove order from repository"""
        pass

# In-Memory Repository Implementation

class InMemoryOrderRepository(OrderRepository):
    """
    In-memory order repository implementation
    
    Mumbai Context: यह temporary filing system जैसा है - सब कुछ memory में store
    होता है. Development और testing के लिए perfect है!
    """
    
    def __init__(self):
        self._orders: Dict[str, Any] = {}
        self._next_id_counter = 1
        self._lock = threading.RLock()
    
    def next_id(self) -> str:
        """Generate next order ID"""
        with self._lock:
            order_id = f"ZOM_ORD_{self._next_id_counter:06d}"
            self._next_id_counter += 1
            return order_id
    
    def save(self, order) -> None:
        """Save order to in-memory storage"""
        with self._lock:
            self._orders[order.id] = order
            logger.debug(f"💾 Order saved to memory: {order.id}")
    
    def find_by_id(self, order_id: str) -> Optional[Any]:
        """Find order by ID"""
        with self._lock:
            return self._orders.get(order_id)
    
    def find_by_specification(self, specification: Specification) -> List[Any]:
        """Find orders matching specification"""
        with self._lock:
            matching_orders = []
            for order in self._orders.values():
                if specification.is_satisfied_by(order):
                    matching_orders.append(order)
            return matching_orders
    
    def find_by_customer(self, customer_id: str) -> List[Any]:
        """Find all orders by customer"""
        spec = OrderByCustomerSpecification(customer_id)
        return self.find_by_specification(spec)
    
    def find_active_orders(self) -> List[Any]:
        """Find all active orders"""
        with self._lock:
            active_orders = []
            for order in self._orders.values():
                if hasattr(order, 'status') and order.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                    active_orders.append(order)
            return active_orders
    
    def count_by_specification(self, specification: Specification) -> int:
        """Count orders matching specification"""
        return len(self.find_by_specification(specification))
    
    def remove(self, order_id: str) -> bool:
        """Remove order from repository"""
        with self._lock:
            if order_id in self._orders:
                del self._orders[order_id]
                logger.debug(f"🗑️ Order removed from memory: {order_id}")
                return True
            return False
    
    def get_all_orders(self) -> List[Any]:
        """Get all orders (for debugging)"""
        with self._lock:
            return list(self._orders.values())

# SQLite Repository Implementation

class SQLiteOrderRepository(OrderRepository):
    """
    SQLite-based order repository implementation
    
    Mumbai Context: यह permanent filing system जैसा है - सब कुछ database में
    persist होता है और बाद में retrieve किया जा सकता है!
    """
    
    def __init__(self, db_path: str = "zomato_orders.db"):
        self.db_path = db_path
        self._init_database()
        self._next_id_counter = self._get_max_order_id() + 1
        self._lock = threading.RLock()
    
    def _init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    restaurant_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_amount DECIMAL(10,2),
                    currency TEXT DEFAULT 'INR',
                    delivery_street TEXT,
                    delivery_area TEXT, 
                    delivery_city TEXT,
                    delivery_pincode TEXT,
                    delivery_landmark TEXT,
                    customer_phone TEXT,
                    created_at REAL NOT NULL,
                    confirmed_at REAL,
                    estimated_delivery_time INTEGER,
                    actual_delivery_time REAL,
                    cancellation_reason TEXT,
                    order_data TEXT,  -- JSON blob for full order data
                    version INTEGER DEFAULT 1,
                    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_customer_id ON orders(customer_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_restaurant_id ON orders(restaurant_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON orders(status)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON orders(created_at)
            """)
    
    def _get_max_order_id(self) -> int:
        """Get maximum order ID for next ID generation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(CAST(SUBSTR(id, 9) AS INTEGER)) FROM orders WHERE id LIKE 'ZOM_ORD_%'")
                result = cursor.fetchone()
                return result[0] if result[0] else 0
        except:
            return 0
    
    def next_id(self) -> str:
        """Generate next order ID"""
        with self._lock:
            order_id = f"ZOM_ORD_{self._next_id_counter:06d}"
            self._next_id_counter += 1
            return order_id
    
    def save(self, order) -> None:
        """Save order to SQLite database"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Serialize full order data
                order_data = {
                    'items': {},
                    'estimated_delivery_time': getattr(order, 'estimated_delivery_time', None),
                    'actual_delivery_time': getattr(order, 'actual_delivery_time', None)
                }
                
                # Add items if they exist
                if hasattr(order, 'items'):
                    for item_id, item in order.items.items():
                        order_data['items'][item_id] = {
                            'menu_item_id': getattr(item, 'menu_item_id', ''),
                            'name': getattr(item, 'name', ''),
                            'price': float(getattr(item, 'price', Money(Decimal("0"))).amount),
                            'quantity': getattr(item, 'quantity', 0),
                            'special_instructions': getattr(item, 'special_instructions', '')
                        }
                
                # Extract address fields
                address = getattr(order, 'delivery_address', None)
                address_fields = {
                    'delivery_street': address.street if address else '',
                    'delivery_area': address.area if address else '',
                    'delivery_city': address.city if address else '',
                    'delivery_pincode': address.pincode if address else '',
                    'delivery_landmark': address.landmark if address else ''
                }
                
                # Extract phone
                phone = getattr(order, 'customer_phone', None)
                phone_number = phone.number if phone else ''
                
                # Calculate total amount
                total_amount = 0.0
                if hasattr(order, 'get_total_amount'):
                    total_amount = float(order.get_total_amount().amount)
                
                conn.execute("""
                    INSERT OR REPLACE INTO orders 
                    (id, customer_id, restaurant_id, status, total_amount, currency,
                     delivery_street, delivery_area, delivery_city, delivery_pincode, delivery_landmark,
                     customer_phone, created_at, confirmed_at, estimated_delivery_time, 
                     actual_delivery_time, cancellation_reason, order_data, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order.id,
                    getattr(order, 'customer_id', ''),
                    getattr(order, 'restaurant_id', ''),
                    getattr(order, 'status', OrderStatus.DRAFT).value,
                    total_amount,
                    'INR',
                    address_fields['delivery_street'],
                    address_fields['delivery_area'],
                    address_fields['delivery_city'],
                    address_fields['delivery_pincode'],
                    address_fields['delivery_landmark'],
                    phone_number,
                    getattr(order, 'created_at', time.time()),
                    getattr(order, 'confirmed_at', None),
                    getattr(order, 'estimated_delivery_time', None),
                    getattr(order, 'actual_delivery_time', None),
                    getattr(order, 'cancellation_reason', None),
                    json.dumps(order_data),
                    getattr(order, 'version', 1)
                ))
                
                logger.debug(f"💾 Order saved to SQLite: {order.id}")
    
    def find_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Find order by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def find_by_specification(self, specification: Specification) -> List[Dict[str, Any]]:
        """Find orders matching specification - simplified implementation"""
        # For a full implementation, we would convert specifications to SQL
        # Here we'll load all and filter (not efficient for large datasets)
        all_orders = self._get_all_order_rows()
        
        matching_orders = []
        for row in all_orders:
            # Create a mock object for specification checking
            mock_order = self._row_to_mock_object(row)
            if specification.is_satisfied_by(mock_order):
                matching_orders.append(dict(row))
        
        return matching_orders
    
    def find_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Find all orders by customer"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC",
                (customer_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def find_active_orders(self) -> List[Dict[str, Any]]:
        """Find all active orders"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders 
                WHERE status NOT IN ('DELIVERED', 'CANCELLED')
                ORDER BY created_at ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def count_by_specification(self, specification: Specification) -> int:
        """Count orders matching specification"""
        matching_orders = self.find_by_specification(specification)
        return len(matching_orders)
    
    def remove(self, order_id: str) -> bool:
        """Remove order from repository"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
                
                if cursor.rowcount > 0:
                    logger.debug(f"🗑️ Order removed from SQLite: {order_id}")
                    return True
                return False
    
    def _get_all_order_rows(self) -> List[sqlite3.Row]:
        """Get all order rows"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            return cursor.fetchall()
    
    def _row_to_mock_object(self, row: sqlite3.Row):
        """Convert database row to mock object for specification checking"""
        class MockOrder:
            def __init__(self, row):
                self.id = row['id']
                self.customer_id = row['customer_id']
                self.restaurant_id = row['restaurant_id']
                self.status = OrderStatus(row['status'])
                self.created_at = row['created_at']
                self._total_amount = Money(Decimal(str(row['total_amount'])))
            
            def get_total_amount(self):
                return self._total_amount
        
        return MockOrder(row)

# Unit of Work Pattern

class UnitOfWork:
    """
    Unit of Work pattern implementation
    
    Mumbai Context: यह bank के transaction जैसा है! सभी operations एक साथ
    succeed या fail होते हैं. Half-done operations नहीं होते!
    """
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
        self._new_orders: List[Any] = []
        self._dirty_orders: List[Any] = []
        self._removed_order_ids: List[str] = []
        self._committed = False
    
    def register_new(self, order):
        """Register new order for creation"""
        if order not in self._new_orders:
            self._new_orders.append(order)
    
    def register_dirty(self, order):
        """Register order for update"""
        if order not in self._dirty_orders and order not in self._new_orders:
            self._dirty_orders.append(order)
    
    def register_removed(self, order_id: str):
        """Register order for removal"""
        if order_id not in self._removed_order_ids:
            self._removed_order_ids.append(order_id)
    
    def commit(self):
        """Commit all changes"""
        try:
            # Save new orders
            for order in self._new_orders:
                self.order_repository.save(order)
            
            # Save updated orders  
            for order in self._dirty_orders:
                self.order_repository.save(order)
            
            # Remove deleted orders
            for order_id in self._removed_order_ids:
                self.order_repository.remove(order_id)
            
            self._committed = True
            logger.info(f"💾 Unit of Work committed: {len(self._new_orders)} new, {len(self._dirty_orders)} updated, {len(self._removed_order_ids)} removed")
            
            # Clear tracking lists
            self._new_orders.clear()
            self._dirty_orders.clear()
            self._removed_order_ids.clear()
            
        except Exception as e:
            logger.error(f"❌ Unit of Work commit failed: {e}")
            raise
    
    def rollback(self):
        """Rollback all changes"""
        self._new_orders.clear()
        self._dirty_orders.clear()
        self._removed_order_ids.clear()
        logger.info("🔄 Unit of Work rolled back")

# Domain Service using Repository

class OrderDomainService:
    """
    Order domain service using repository pattern
    
    Mumbai Context: यह Zomato के order management का brain है! Repository use
    करके complex business operations perform करता है.
    """
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def get_customer_order_history(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive customer order history"""
        orders = self.order_repository.find_by_customer(customer_id)
        
        if not orders:
            return {
                'customer_id': customer_id,
                'total_orders': 0,
                'total_spent': 0.0,
                'average_order_value': 0.0,
                'order_statuses': {},
                'recent_orders': []
            }
        
        # Calculate statistics
        total_orders = len(orders)
        total_spent = sum(order.get('total_amount', 0) for order in orders)
        average_order_value = total_spent / total_orders if total_orders > 0 else 0.0
        
        # Order status distribution
        status_counts = {}
        for order in orders:
            status = order.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Recent orders (last 5)
        recent_orders = sorted(orders, key=lambda x: x.get('created_at', 0), reverse=True)[:5]
        
        return {
            'customer_id': customer_id,
            'total_orders': total_orders,
            'total_spent': total_spent,
            'average_order_value': average_order_value,
            'order_statuses': status_counts,
            'recent_orders': recent_orders
        }
    
    def get_restaurant_performance(self, restaurant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get restaurant performance metrics"""
        # Get orders from last N days
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)  # N days ago
        
        date_spec = OrderByDateRangeSpecification(start_time, end_time)
        restaurant_spec = OrderByRestaurantSpecification(restaurant_id)
        combined_spec = date_spec.and_specification(restaurant_spec)
        
        orders = self.order_repository.find_by_specification(combined_spec)
        
        if not orders:
            return {
                'restaurant_id': restaurant_id,
                'period_days': days,
                'total_orders': 0,
                'revenue': 0.0,
                'average_order_value': 0.0,
                'completion_rate': 0.0,
                'cancellation_rate': 0.0
            }
        
        # Calculate metrics
        total_orders = len(orders)
        total_revenue = sum(order.get('total_amount', 0) for order in orders)
        average_order_value = total_revenue / total_orders
        
        # Status-based metrics
        delivered_orders = len([o for o in orders if o.get('status') == 'DELIVERED'])
        cancelled_orders = len([o for o in orders if o.get('status') == 'CANCELLED'])
        
        completion_rate = (delivered_orders / total_orders) * 100 if total_orders > 0 else 0.0
        cancellation_rate = (cancelled_orders / total_orders) * 100 if total_orders > 0 else 0.0
        
        return {
            'restaurant_id': restaurant_id,
            'period_days': days,
            'total_orders': total_orders,
            'revenue': total_revenue,
            'average_order_value': average_order_value,
            'completion_rate': completion_rate,
            'cancellation_rate': cancellation_rate,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders
        }
    
    def find_high_value_orders(self, min_amount: Decimal) -> List[Any]:
        """Find orders above specified amount"""
        spec = OrderByMinimumAmountSpecification(min_amount)
        return self.order_repository.find_by_specification(spec)
    
    def get_pending_orders_for_restaurant(self, restaurant_id: str) -> List[Any]:
        """Get pending orders for a restaurant"""
        restaurant_spec = OrderByRestaurantSpecification(restaurant_id)
        placed_spec = OrderByStatusSpecification(OrderStatus.PLACED)
        confirmed_spec = OrderByStatusSpecification(OrderStatus.CONFIRMED)
        preparing_spec = OrderByStatusSpecification(OrderStatus.PREPARING)
        
        # Orders that are placed, confirmed, or preparing
        pending_spec = placed_spec.or_specification(confirmed_spec).or_specification(preparing_spec)
        combined_spec = restaurant_spec.and_specification(pending_spec)
        
        return self.order_repository.find_by_specification(combined_spec)

def simulate_zomato_repository_pattern():
    """
    Simulate Zomato repository pattern usage
    
    Mumbai Scenario: Zomato के backend system में orders को efficiently store
    और retrieve करना पड़ता है. Repository pattern clean abstraction provide
    करता है और different storage mechanisms को support करता है!
    """
    logger.info("🏪 Starting Zomato Repository Pattern simulation...")
    
    # Test both in-memory and SQLite repositories
    repositories = [
        ("In-Memory", InMemoryOrderRepository()),
        ("SQLite", SQLiteOrderRepository("test_orders.db"))
    ]
    
    for repo_name, repo in repositories:
        logger.info(f"\n📚 Testing {repo_name} Repository...")
        
        # Create domain service
        order_service = OrderDomainService(repo)
        
        # Create sample orders (simplified objects for testing)
        sample_orders = []
        
        for i in range(5):
            order_id = repo.next_id()
            
            # Create mock order object
            class MockOrder:
                def __init__(self, order_id, customer_id, restaurant_id, status, total_amount, created_at):
                    self.id = order_id
                    self.customer_id = customer_id
                    self.restaurant_id = restaurant_id
                    self.status = status
                    self._total_amount = Money(Decimal(str(total_amount)))
                    self.created_at = created_at
                    self.version = 1
                
                def get_total_amount(self):
                    return self._total_amount
            
            # Create diverse orders
            customers = ['customer_001', 'customer_002', 'customer_001', 'customer_003', 'customer_002']
            restaurants = ['rest_001', 'rest_002', 'rest_001', 'rest_003', 'rest_002']
            statuses = [OrderStatus.DELIVERED, OrderStatus.PLACED, OrderStatus.CANCELLED, OrderStatus.CONFIRMED, OrderStatus.DELIVERED]
            amounts = [450.0, 780.0, 320.0, 890.0, 650.0]
            
            order = MockOrder(
                order_id=order_id,
                customer_id=customers[i],
                restaurant_id=restaurants[i],
                status=statuses[i],
                total_amount=amounts[i],
                created_at=time.time() - (i * 3600)  # Spread orders over time
            )
            
            sample_orders.append(order)
            repo.save(order)
        
        logger.info(f"📦 Created and saved {len(sample_orders)} sample orders")
        
        # Test basic repository operations
        logger.info("\n🔍 Testing repository operations...")
        
        # Find by ID
        first_order = repo.find_by_id(sample_orders[0].id)
        if first_order:
            logger.info(f"✅ Found order by ID: {sample_orders[0].id}")
        
        # Find by customer
        customer_orders = repo.find_by_customer('customer_001')
        logger.info(f"👤 Orders for customer_001: {len(customer_orders)}")
        
        # Find active orders
        active_orders = repo.find_active_orders()
        logger.info(f"🏃 Active orders: {len(active_orders)}")
        
        # Test specifications
        logger.info("\n📋 Testing specifications...")
        
        # Orders by status
        delivered_spec = OrderByStatusSpecification(OrderStatus.DELIVERED)
        delivered_orders = repo.find_by_specification(delivered_spec)
        logger.info(f"✅ Delivered orders: {len(delivered_orders)}")
        
        # High-value orders
        high_value_spec = OrderByMinimumAmountSpecification(Decimal("500.0"))
        high_value_orders = repo.find_by_specification(high_value_spec)
        logger.info(f"💎 High value orders (>₹500): {len(high_value_orders)}")
        
        # Combined specification
        customer_and_delivered = OrderByCustomerSpecification('customer_001').and_specification(delivered_spec)
        customer_delivered_orders = repo.find_by_specification(customer_and_delivered)
        logger.info(f"👤✅ Customer_001 delivered orders: {len(customer_delivered_orders)}")
        
        # Test domain service operations
        logger.info("\n🎯 Testing domain service operations...")
        
        # Customer history
        customer_history = order_service.get_customer_order_history('customer_001')
        logger.info(f"📊 Customer_001 history:")
        logger.info(f"  Total orders: {customer_history['total_orders']}")
        logger.info(f"  Total spent: ₹{customer_history['total_spent']:.2f}")
        logger.info(f"  Average order value: ₹{customer_history['average_order_value']:.2f}")
        logger.info(f"  Order statuses: {customer_history['order_statuses']}")
        
        # Restaurant performance
        restaurant_performance = order_service.get_restaurant_performance('rest_001', days=1)
        logger.info(f"🏪 Restaurant_001 performance:")
        logger.info(f"  Total orders: {restaurant_performance['total_orders']}")
        logger.info(f"  Revenue: ₹{restaurant_performance['revenue']:.2f}")
        logger.info(f"  Completion rate: {restaurant_performance['completion_rate']:.2f}%")
        logger.info(f"  Cancellation rate: {restaurant_performance['cancellation_rate']:.2f}%")
        
        # High-value orders through domain service
        high_value_orders = order_service.find_high_value_orders(Decimal("600.0"))
        logger.info(f"💰 High-value orders (>₹600) found: {len(high_value_orders)}")
        
        # Pending orders for restaurant
        pending_orders = order_service.get_pending_orders_for_restaurant('rest_001')
        logger.info(f"⏳ Pending orders for rest_001: {len(pending_orders)}")
    
    # Test Unit of Work pattern
    logger.info("\n🔄 Testing Unit of Work pattern...")
    
    uow = UnitOfWork(InMemoryOrderRepository())
    
    # Create orders through UoW
    for i in range(3):
        class MockOrder:
            def __init__(self, order_id):
                self.id = order_id
                self.customer_id = f"customer_{i:03d}"
                self.restaurant_id = f"rest_{i:03d}"
                self.status = OrderStatus.PLACED
                self.created_at = time.time()
                self.version = 1
            
            def get_total_amount(self):
                return Money(Decimal("500.0"))
        
        order = MockOrder(f"UOW_ORDER_{i:03d}")
        uow.register_new(order)
    
    # Commit all changes
    uow.commit()
    logger.info("✅ Unit of Work committed successfully")

if __name__ == "__main__":
    try:
        simulate_zomato_repository_pattern()
        logger.info("\n🎊 Zomato Repository Pattern simulation completed!")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()