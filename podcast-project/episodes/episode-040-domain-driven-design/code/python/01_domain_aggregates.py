#!/usr/bin/env python3
"""
Domain-Driven Design: Aggregates Implementation
==============================================

Production-ready DDD aggregates implementation with proper encapsulation.
Aggregates are the consistency boundaries in DDD that maintain invariants.

Mumbai Context: यह Mumbai housing society जैसा है! Society (aggregate root) में
multiple flats (entities) होते हैं, common rules follow करते हैं, और society
secretary (aggregate root) के through ही सब maintain होता है!

Real-world usage:
- E-commerce order management
- Banking account operations
- User profile management
- Inventory management
- Booking systems
"""

import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from decimal import Decimal
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DomainEvent(ABC):
    """Base class for domain events"""
    
    def __init__(self):
        self.event_id = str(uuid.uuid4())
        self.occurred_at = time.time()
        self.version = 1
    
    @abstractmethod
    def get_event_type(self) -> str:
        pass

class Entity(ABC):
    """Base entity class"""
    
    def __init__(self, entity_id: str):
        self._id = entity_id
        self._created_at = time.time()
        self._updated_at = time.time()
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def created_at(self) -> float:
        return self._created_at
    
    @property
    def updated_at(self) -> float:
        return self._updated_at
    
    def _touch(self):
        """Update the last modified timestamp"""
        self._updated_at = time.time()
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id
    
    def __hash__(self):
        return hash(self._id)

class ValueObject(ABC):
    """Base value object class"""
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

class AggregateRoot(Entity):
    """Base aggregate root class"""
    
    def __init__(self, entity_id: str):
        super().__init__(entity_id)
        self._domain_events: List[DomainEvent] = []
        self._version = 1
    
    @property
    def version(self) -> int:
        return self._version
    
    def _add_domain_event(self, event: DomainEvent):
        """Add domain event to be published"""
        self._domain_events.append(event)
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get uncommitted domain events"""
        return self._domain_events.copy()
    
    def mark_events_as_committed(self):
        """Mark events as committed"""
        self._domain_events.clear()
        self._version += 1
    
    def _touch(self):
        super()._touch()
        self._version += 1

# Value Objects for Zomato domain

@dataclass(frozen=True)
class Money(ValueObject):
    """Money value object"""
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} and {other.currency}")
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Resulting amount cannot be negative")
        return Money(result_amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        return Money(self.amount * Decimal(str(factor)), self.currency)
    
    def __str__(self):
        return f"₹{self.amount:.2f}"

@dataclass(frozen=True)
class Address(ValueObject):
    """Address value object"""
    street: str
    area: str
    city: str
    pincode: str
    landmark: Optional[str] = None
    
    def __post_init__(self):
        if not self.street or not self.area or not self.city:
            raise ValueError("Street, area, and city are required")
        if len(self.pincode) != 6 or not self.pincode.isdigit():
            raise ValueError("Pincode must be 6 digits")
    
    def get_delivery_zone(self) -> str:
        """Get delivery zone based on area"""
        mumbai_zones = {
            'bandra': 'ZONE_WEST',
            'andheri': 'ZONE_WEST', 
            'powai': 'ZONE_CENTRAL',
            'thane': 'ZONE_CENTRAL',
            'kurla': 'ZONE_EAST',
            'ghatkopar': 'ZONE_EAST'
        }
        
        area_lower = self.area.lower()
        for location, zone in mumbai_zones.items():
            if location in area_lower:
                return zone
        
        return 'ZONE_OTHER'
    
    def __str__(self):
        parts = [self.street, self.area, self.city, self.pincode]
        if self.landmark:
            parts.insert(-2, f"Near {self.landmark}")
        return ", ".join(parts)

@dataclass(frozen=True)
class Phone(ValueObject):
    """Phone number value object"""
    number: str
    
    def __post_init__(self):
        # Remove spaces and special characters
        clean_number = ''.join(filter(str.isdigit, self.number))
        
        # Indian mobile number validation
        if len(clean_number) == 10 and clean_number[0] in '6789':
            object.__setattr__(self, 'number', clean_number)
        elif len(clean_number) == 13 and clean_number.startswith('91') and clean_number[2] in '6789':
            object.__setattr__(self, 'number', clean_number[2:])  # Remove country code
        else:
            raise ValueError(f"Invalid Indian mobile number: {self.number}")
    
    def get_formatted(self) -> str:
        """Get formatted phone number"""
        return f"+91 {self.number[:5]} {self.number[5:]}"
    
    def __str__(self):
        return self.get_formatted()

# Domain Events

class OrderCreated(DomainEvent):
    """Order created domain event"""
    
    def __init__(self, order_id: str, customer_id: str, restaurant_id: str, total_amount: Money):
        super().__init__()
        self.order_id = order_id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.total_amount = total_amount
    
    def get_event_type(self) -> str:
        return "ORDER_CREATED"

class OrderItemAdded(DomainEvent):
    """Order item added domain event"""
    
    def __init__(self, order_id: str, item_id: str, quantity: int, price: Money):
        super().__init__()
        self.order_id = order_id
        self.item_id = item_id
        self.quantity = quantity
        self.price = price
    
    def get_event_type(self) -> str:
        return "ORDER_ITEM_ADDED"

class OrderConfirmed(DomainEvent):
    """Order confirmed domain event"""
    
    def __init__(self, order_id: str, estimated_delivery_time: int):
        super().__init__()
        self.order_id = order_id
        self.estimated_delivery_time = estimated_delivery_time
    
    def get_event_type(self) -> str:
        return "ORDER_CONFIRMED"

class OrderCancelled(DomainEvent):
    """Order cancelled domain event"""
    
    def __init__(self, order_id: str, reason: str):
        super().__init__()
        self.order_id = order_id
        self.reason = reason
    
    def get_event_type(self) -> str:
        return "ORDER_CANCELLED"

# Entities

class OrderStatus(Enum):
    """Order status enumeration"""
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class OrderItem(Entity):
    """
    Order item entity
    
    Mumbai Context: यह menu में individual dish जैसा है - Butter Chicken,
    Garlic Naan, etc. हर item का अपना price, quantity, और customization होता है.
    """
    
    def __init__(self, item_id: str, menu_item_id: str, name: str, 
                 price: Money, quantity: int = 1, special_instructions: str = ""):
        super().__init__(item_id)
        self.menu_item_id = menu_item_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.special_instructions = special_instructions
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
    
    def get_total_price(self) -> Money:
        """Get total price for this item"""
        return self.price.multiply(self.quantity)
    
    def update_quantity(self, new_quantity: int):
        """Update item quantity"""
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self.quantity = new_quantity
        self._touch()
    
    def add_special_instruction(self, instruction: str):
        """Add special instruction"""
        if self.special_instructions:
            self.special_instructions += f"; {instruction}"
        else:
            self.special_instructions = instruction
        self._touch()

class ZomatoOrder(AggregateRoot):
    """
    Zomato Order Aggregate Root
    
    Mumbai Context: यह complete order जैसा है! Customer का order जिसमें multiple
    items होते हैं, delivery address, payment info, और सभी business rules
    maintain होते हैं. यह aggregate root है क्योंकि order के सारे changes इसी
    के through होते हैं!
    """
    
    def __init__(self, order_id: str, customer_id: str, restaurant_id: str, 
                 delivery_address: Address, customer_phone: Phone):
        super().__init__(order_id)
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.delivery_address = delivery_address
        self.customer_phone = customer_phone
        self.status = OrderStatus.DRAFT
        self.items: Dict[str, OrderItem] = {}
        self.created_at = time.time()
        self.confirmed_at: Optional[float] = None
        self.estimated_delivery_time: Optional[int] = None  # minutes
        self.actual_delivery_time: Optional[float] = None
        self.cancellation_reason: Optional[str] = None
        
        # Business rules
        self.max_items_per_order = 20
        self.max_order_amount = Money(Decimal("5000.00"))
        self.min_order_amount = Money(Decimal("50.00"))
        
        logger.info(f"🍽️ Order created: {order_id} for customer {customer_id}")
    
    def add_item(self, menu_item_id: str, name: str, price: Money, 
                 quantity: int = 1, special_instructions: str = "") -> str:
        """
        Add item to order
        
        Business rules:
        - Order must be in DRAFT status
        - Maximum items per order limit
        - No duplicate menu items (update quantity instead)
        """
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot add items to order in {self.status.value} status")
        
        if len(self.items) >= self.max_items_per_order:
            raise ValueError(f"Cannot add more than {self.max_items_per_order} items to order")
        
        # Check if item already exists
        existing_item = self._find_item_by_menu_id(menu_item_id)
        if existing_item:
            # Update quantity of existing item
            new_quantity = existing_item.quantity + quantity
            existing_item.update_quantity(new_quantity)
            
            if special_instructions:
                existing_item.add_special_instruction(special_instructions)
            
            item_id = existing_item.id
        else:
            # Add new item
            item_id = f"{self.id}_item_{len(self.items) + 1}"
            order_item = OrderItem(
                item_id=item_id,
                menu_item_id=menu_item_id,
                name=name,
                price=price,
                quantity=quantity,
                special_instructions=special_instructions
            )
            
            self.items[item_id] = order_item
        
        # Check order amount limit
        if self.get_total_amount().amount > self.max_order_amount.amount:
            raise ValueError(f"Order amount exceeds maximum limit of {self.max_order_amount}")
        
        # Emit domain event
        self._add_domain_event(OrderItemAdded(
            order_id=self.id,
            item_id=item_id,
            quantity=quantity,
            price=price
        ))
        
        self._touch()
        logger.info(f"📦 Item added to order {self.id}: {name} x{quantity}")
        
        return item_id
    
    def remove_item(self, item_id: str):
        """Remove item from order"""
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot remove items from order in {self.status.value} status")
        
        if item_id not in self.items:
            raise ValueError(f"Item {item_id} not found in order")
        
        removed_item = self.items.pop(item_id)
        self._touch()
        
        logger.info(f"🗑️ Item removed from order {self.id}: {removed_item.name}")
    
    def update_item_quantity(self, item_id: str, new_quantity: int):
        """Update quantity of an item"""
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot update items in order in {self.status.value} status")
        
        if item_id not in self.items:
            raise ValueError(f"Item {item_id} not found in order")
        
        self.items[item_id].update_quantity(new_quantity)
        
        # Check order amount limit
        if self.get_total_amount().amount > self.max_order_amount.amount:
            raise ValueError(f"Order amount exceeds maximum limit of {self.max_order_amount}")
        
        self._touch()
        logger.info(f"🔄 Item quantity updated in order {self.id}: {item_id} -> {new_quantity}")
    
    def place_order(self):
        """
        Place the order
        
        Business rules:
        - Order must have at least one item
        - Order amount must meet minimum requirement
        - Order must be in DRAFT status
        """
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot place order in {self.status.value} status")
        
        if not self.items:
            raise ValueError("Cannot place order without items")
        
        total_amount = self.get_total_amount()
        if total_amount.amount < self.min_order_amount.amount:
            raise ValueError(f"Order amount {total_amount} is below minimum {self.min_order_amount}")
        
        self.status = OrderStatus.PLACED
        self._touch()
        
        # Emit domain event
        self._add_domain_event(OrderCreated(
            order_id=self.id,
            customer_id=self.customer_id,
            restaurant_id=self.restaurant_id,
            total_amount=total_amount
        ))
        
        logger.info(f"🚀 Order placed: {self.id} - Total: {total_amount}")
    
    def confirm_order(self, estimated_delivery_minutes: int):
        """
        Confirm order (restaurant accepts)
        
        Args:
            estimated_delivery_minutes: Estimated delivery time in minutes
        """
        if self.status != OrderStatus.PLACED:
            raise ValueError(f"Cannot confirm order in {self.status.value} status")
        
        if estimated_delivery_minutes <= 0:
            raise ValueError("Estimated delivery time must be positive")
        
        self.status = OrderStatus.CONFIRMED
        self.confirmed_at = time.time()
        self.estimated_delivery_time = estimated_delivery_minutes
        self._touch()
        
        # Emit domain event
        self._add_domain_event(OrderConfirmed(
            order_id=self.id,
            estimated_delivery_time=estimated_delivery_minutes
        ))
        
        logger.info(f"✅ Order confirmed: {self.id} - ETA: {estimated_delivery_minutes} minutes")
    
    def start_preparation(self):
        """Start order preparation"""
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Cannot start preparation for order in {self.status.value} status")
        
        self.status = OrderStatus.PREPARING
        self._touch()
        
        logger.info(f"👨‍🍳 Order preparation started: {self.id}")
    
    def dispatch_for_delivery(self):
        """Dispatch order for delivery"""
        if self.status != OrderStatus.PREPARING:
            raise ValueError(f"Cannot dispatch order in {self.status.value} status")
        
        self.status = OrderStatus.OUT_FOR_DELIVERY
        self._touch()
        
        logger.info(f"🛵 Order dispatched for delivery: {self.id}")
    
    def mark_delivered(self):
        """Mark order as delivered"""
        if self.status != OrderStatus.OUT_FOR_DELIVERY:
            raise ValueError(f"Cannot mark order as delivered in {self.status.value} status")
        
        self.status = OrderStatus.DELIVERED
        self.actual_delivery_time = time.time()
        self._touch()
        
        logger.info(f"🎉 Order delivered: {self.id}")
    
    def cancel_order(self, reason: str):
        """
        Cancel order
        
        Business rules:
        - Cannot cancel delivered orders
        - Must provide cancellation reason
        """
        if self.status == OrderStatus.DELIVERED:
            raise ValueError("Cannot cancel delivered order")
        
        if not reason:
            raise ValueError("Cancellation reason is required")
        
        old_status = self.status
        self.status = OrderStatus.CANCELLED
        self.cancellation_reason = reason
        self._touch()
        
        # Emit domain event
        self._add_domain_event(OrderCancelled(
            order_id=self.id,
            reason=reason
        ))
        
        logger.info(f"🚫 Order cancelled: {self.id} (was {old_status.value}) - Reason: {reason}")
    
    def get_total_amount(self) -> Money:
        """Calculate total order amount"""
        if not self.items:
            return Money(Decimal("0.00"))
        
        total = Money(Decimal("0.00"))
        for item in self.items.values():
            total = total.add(item.get_total_price())
        
        return total
    
    def get_item_count(self) -> int:
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items.values())
    
    def _find_item_by_menu_id(self, menu_item_id: str) -> Optional[OrderItem]:
        """Find order item by menu item ID"""
        for item in self.items.values():
            if item.menu_item_id == menu_item_id:
                return item
        return None
    
    def get_delivery_zone(self) -> str:
        """Get delivery zone for this order"""
        return self.delivery_address.get_delivery_zone()
    
    def is_cancellable(self) -> bool:
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.DRAFT, OrderStatus.PLACED, OrderStatus.CONFIRMED]
    
    def get_estimated_delivery_timestamp(self) -> Optional[float]:
        """Get estimated delivery timestamp"""
        if not self.confirmed_at or not self.estimated_delivery_time:
            return None
        
        return self.confirmed_at + (self.estimated_delivery_time * 60)  # Convert minutes to seconds
    
    def __str__(self):
        return f"Order({self.id}, {self.status.value}, Items: {len(self.items)}, Total: {self.get_total_amount()})"

def simulate_zomato_order_aggregate():
    """
    Simulate Zomato order processing using DDD aggregates
    
    Mumbai Scenario: Customer Mumbai में Zomato से order place करता है.
    Complete order lifecycle demonstrate करते हैं - item addition, order placement,
    confirmation, preparation, delivery, और business rules validation!
    """
    logger.info("🍽️ Starting Zomato Order Aggregate simulation...")
    
    # Create customer details
    delivery_address = Address(
        street="123, Palm View Society",
        area="Bandra West",
        city="Mumbai",
        pincode="400050",
        landmark="Near Bandra Station"
    )
    
    customer_phone = Phone("+91 98765 43210")
    
    # Create order aggregate
    order = ZomatoOrder(
        order_id="ZOM_ORD_001",
        customer_id="customer_rahul_001",
        restaurant_id="rest_mumbai_darbar",
        delivery_address=delivery_address,
        customer_phone=customer_phone
    )
    
    logger.info(f"📍 Delivery to: {delivery_address}")
    logger.info(f"📞 Customer phone: {customer_phone}")
    logger.info(f"🏪 Delivery zone: {order.get_delivery_zone()}")
    
    try:
        # Add items to order
        logger.info("\n🛒 Adding items to order...")
        
        # Add Butter Chicken
        order.add_item(
            menu_item_id="menu_001",
            name="Butter Chicken",
            price=Money(Decimal("350.00")),
            quantity=1,
            special_instructions="Medium spicy"
        )
        
        # Add Garlic Naan
        order.add_item(
            menu_item_id="menu_002", 
            name="Garlic Naan",
            price=Money(Decimal("80.00")),
            quantity=2
        )
        
        # Add same item again (should update quantity)
        order.add_item(
            menu_item_id="menu_001",  # Same as Butter Chicken
            name="Butter Chicken",
            price=Money(Decimal("350.00")),
            quantity=1,
            special_instructions="Extra gravy"
        )
        
        # Add Lassi
        order.add_item(
            menu_item_id="menu_003",
            name="Sweet Lassi",
            price=Money(Decimal("120.00")),
            quantity=1
        )
        
        logger.info(f"💰 Current order total: {order.get_total_amount()}")
        logger.info(f"📦 Total items: {order.get_item_count()}")
        
        # Show order items
        logger.info("\n📋 Order items:")
        for item in order.items.values():
            logger.info(f"  {item.name} x{item.quantity} - {item.get_total_price()}")
            if item.special_instructions:
                logger.info(f"    Special: {item.special_instructions}")
        
        # Place order
        logger.info("\n🚀 Placing order...")
        order.place_order()
        
        # Get domain events
        events = order.get_uncommitted_events()
        logger.info(f"\n📢 Domain events generated: {len(events)}")
        for event in events:
            logger.info(f"  {event.get_event_type()}: {event.event_id}")
        
        # Simulate restaurant confirmation
        logger.info("\n✅ Restaurant confirming order...")
        order.confirm_order(estimated_delivery_minutes=35)
        
        # Start preparation
        logger.info("\n👨‍🍳 Starting preparation...")
        order.start_preparation()
        
        # Dispatch for delivery
        logger.info("\n🛵 Dispatching for delivery...")
        order.dispatch_for_delivery()
        
        # Mark as delivered
        logger.info("\n🎉 Marking as delivered...")
        order.mark_delivered()
        
        # Show final order state
        logger.info(f"\n📊 Final order status: {order.status.value}")
        logger.info(f"💰 Final amount: {order.get_total_amount()}")
        logger.info(f"⏰ Order placed at: {time.strftime('%H:%M:%S', time.localtime(order.created_at))}")
        if order.confirmed_at:
            logger.info(f"✅ Confirmed at: {time.strftime('%H:%M:%S', time.localtime(order.confirmed_at))}")
        if order.actual_delivery_time:
            logger.info(f"🚚 Delivered at: {time.strftime('%H:%M:%S', time.localtime(order.actual_delivery_time))}")
            
            # Calculate delivery time
            if order.confirmed_at:
                actual_delivery_minutes = (order.actual_delivery_time - order.confirmed_at) / 60
                logger.info(f"⏱️ Actual delivery time: {actual_delivery_minutes:.1f} minutes")
                if order.estimated_delivery_time:
                    difference = actual_delivery_minutes - order.estimated_delivery_time
                    if difference > 0:
                        logger.info(f"🐌 Delivered {difference:.1f} minutes late")
                    else:
                        logger.info(f"🚀 Delivered {-difference:.1f} minutes early")
        
        # Show all domain events generated
        all_events = order.get_uncommitted_events()
        logger.info(f"\n📢 Total domain events: {len(all_events)}")
        for i, event in enumerate(all_events, 1):
            logger.info(f"  {i}. {event.get_event_type()} at {time.strftime('%H:%M:%S', time.localtime(event.occurred_at))}")
        
        # Simulate order cancellation (this will fail as order is delivered)
        logger.info("\n🧪 Testing business rule: Cancel delivered order...")
        try:
            order.cancel_order("Customer changed mind")
        except ValueError as e:
            logger.info(f"✅ Business rule enforced: {e}")
        
    except ValueError as e:
        logger.error(f"❌ Business rule violation: {e}")
    
    # Demonstrate another order with cancellation
    logger.info("\n\n🔄 Creating another order to demonstrate cancellation...")
    
    order2 = ZomatoOrder(
        order_id="ZOM_ORD_002",
        customer_id="customer_priya_002", 
        restaurant_id="rest_pizza_corner",
        delivery_address=Address(
            street="456, Horizon Towers",
            area="Andheri East",
            city="Mumbai", 
            pincode="400069"
        ),
        customer_phone=Phone("9876543211")
    )
    
    # Add item and place order
    order2.add_item("menu_pizza", "Margherita Pizza", Money(Decimal("450.00")), 1)
    order2.place_order()
    order2.confirm_order(25)
    
    # Cancel order
    logger.info("🚫 Cancelling second order...")
    order2.cancel_order("Restaurant called - item not available")
    
    logger.info(f"📊 Order 2 final status: {order2.status.value}")
    logger.info(f"💬 Cancellation reason: {order2.cancellation_reason}")

if __name__ == "__main__":
    try:
        simulate_zomato_order_aggregate()
        logger.info("\n🎊 Zomato Order Aggregate simulation completed!")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()