#!/usr/bin/env python3
"""
Domain-Driven Design: Bounded Context - Zomato Order Management
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में Bounded Context का इस्तेमाल करके
Zomato के different domains को अलग करते हैं। हर context का अपना model है।

Author: Hindi Tech Podcast
Date: 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Protocol, Union
from dataclasses import dataclass, field
from uuid import uuid4
from decimal import Decimal
from enum import Enum
import json

# Common Value Objects - Shared across contexts
@dataclass(frozen=True)
class CustomerId:
    """Customer identifier - सभी contexts में common"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 5:
            raise ValueError("Customer ID must be at least 5 characters")

@dataclass(frozen=True)
class RestaurantId:
    """Restaurant identifier"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 5:
            raise ValueError("Restaurant ID must be at least 5 characters")

@dataclass(frozen=True)
class Location:
    """Geographic location"""
    latitude: float
    longitude: float
    address: str
    pincode: str
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Invalid latitude")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Invalid longitude")
        if len(self.pincode) != 6 or not self.pincode.isdigit():
            raise ValueError("Pincode must be 6 digits")

# ====================================================================
# ORDER MANAGEMENT BOUNDED CONTEXT
# यह context order lifecycle को handle करता है
# ====================================================================

class OrderStatus(Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass(frozen=True)
class OrderId:
    """Order identifier"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.startswith("ZOM_"):
            raise ValueError("Order ID must start with ZOM_")

@dataclass(frozen=True)
class OrderItem:
    """Individual item in order"""
    item_id: str
    name: str
    quantity: int
    unit_price: Decimal
    customizations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price <= 0:
            raise ValueError("Unit price must be positive")
    
    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity

@dataclass
class DeliveryInfo:
    """Delivery information"""
    address: Location
    customer_phone: str
    delivery_instructions: str = ""
    estimated_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    
    def __post_init__(self):
        if len(self.customer_phone) != 10 or not self.customer_phone.isdigit():
            raise ValueError("Invalid phone number")

class OrderAggregate:
    """
    Order Aggregate - Order Management Context
    
    यह aggregate order की complete lifecycle को handle करता है।
    """
    
    def __init__(
        self,
        order_id: OrderId,
        customer_id: CustomerId,
        restaurant_id: RestaurantId,
        items: List[OrderItem],
        delivery_info: DeliveryInfo
    ):
        if not items:
            raise ValueError("Order must have at least one item")
        
        self._order_id = order_id
        self._customer_id = customer_id
        self._restaurant_id = restaurant_id
        self._items = items.copy()
        self._delivery_info = delivery_info
        
        # Order state
        self._status = OrderStatus.PLACED
        self._placed_at = datetime.now()
        self._updated_at = datetime.now()
        
        # Pricing
        self._subtotal = sum(item.total_price for item in self._items)
        self._taxes = self._subtotal * Decimal('0.05')  # 5% tax
        self._delivery_fee = Decimal('20.00')  # ₹20 delivery
        self._total_amount = self._subtotal + self._taxes + self._delivery_fee
        
        # Tracking
        self._preparation_time: Optional[timedelta] = None
        self._delivery_partner_id: Optional[str] = None
        
        print(f"📋 Order placed: {self._order_id.value} for ₹{self._total_amount}")
    
    @property
    def order_id(self) -> OrderId:
        return self._order_id
    
    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id
    
    @property
    def restaurant_id(self) -> RestaurantId:
        return self._restaurant_id
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def total_amount(self) -> Decimal:
        return self._total_amount
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()
    
    def confirm_order(self, estimated_prep_time: timedelta) -> None:
        """Restaurant confirms order"""
        if self._status != OrderStatus.PLACED:
            raise ValueError("Order must be in placed status")
        
        self._status = OrderStatus.CONFIRMED
        self._preparation_time = estimated_prep_time
        self._delivery_info.estimated_time = datetime.now() + estimated_prep_time + timedelta(minutes=20)
        self._updated_at = datetime.now()
        
        print(f"✅ Order confirmed: {self._order_id.value}")
        print(f"   Prep time: {estimated_prep_time.total_seconds() / 60:.0f} minutes")
    
    def start_preparation(self) -> None:
        """Start food preparation"""
        if self._status != OrderStatus.CONFIRMED:
            raise ValueError("Order must be confirmed first")
        
        self._status = OrderStatus.PREPARING
        self._updated_at = datetime.now()
        
        print(f"👨‍🍳 Food preparation started: {self._order_id.value}")
    
    def mark_ready_for_pickup(self) -> None:
        """Food is ready for pickup"""
        if self._status != OrderStatus.PREPARING:
            raise ValueError("Order must be in preparing status")
        
        self._status = OrderStatus.READY_FOR_PICKUP
        self._updated_at = datetime.now()
        
        print(f"🍽️ Order ready for pickup: {self._order_id.value}")
    
    def assign_delivery_partner(self, partner_id: str) -> None:
        """Assign delivery partner"""
        if self._status != OrderStatus.READY_FOR_PICKUP:
            raise ValueError("Order must be ready for pickup")
        
        self._status = OrderStatus.OUT_FOR_DELIVERY
        self._delivery_partner_id = partner_id
        self._updated_at = datetime.now()
        
        print(f"🏍️ Order out for delivery: {self._order_id.value}")
        print(f"   Delivery partner: {partner_id}")
    
    def mark_delivered(self) -> None:
        """Mark order as delivered"""
        if self._status != OrderStatus.OUT_FOR_DELIVERY:
            raise ValueError("Order must be out for delivery")
        
        self._status = OrderStatus.DELIVERED
        self._delivery_info.actual_delivery_time = datetime.now()
        self._updated_at = datetime.now()
        
        delivery_duration = (self._delivery_info.actual_delivery_time - self._placed_at).total_seconds() / 60
        print(f"🎉 Order delivered: {self._order_id.value}")
        print(f"   Total time: {delivery_duration:.0f} minutes")
    
    def cancel_order(self, reason: str) -> None:
        """Cancel order"""
        if self._status in [OrderStatus.DELIVERED, OrderStatus.OUT_FOR_DELIVERY]:
            raise ValueError("Cannot cancel delivered or out-for-delivery orders")
        
        self._status = OrderStatus.CANCELLED
        self._updated_at = datetime.now()
        
        print(f"❌ Order cancelled: {self._order_id.value}")
        print(f"   Reason: {reason}")

# ====================================================================
# RESTAURANT MANAGEMENT BOUNDED CONTEXT
# यह context restaurant operations को handle करता है
# ====================================================================

class CuisineType(Enum):
    NORTH_INDIAN = "north_indian"
    SOUTH_INDIAN = "south_indian"
    CHINESE = "chinese"
    CONTINENTAL = "continental"
    FAST_FOOD = "fast_food"
    DESSERTS = "desserts"

@dataclass(frozen=True)
class MenuItem:
    """Menu item in restaurant context"""
    item_id: str
    name: str
    description: str
    price: Decimal
    cuisine_type: CuisineType
    is_vegetarian: bool
    is_available: bool = True
    preparation_time_minutes: int = 15
    
    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.preparation_time_minutes <= 0:
            raise ValueError("Preparation time must be positive")

class RestaurantAggregate:
    """
    Restaurant Aggregate - Restaurant Management Context
    
    यह aggregate restaurant की information और operations handle करता है।
    """
    
    def __init__(
        self,
        restaurant_id: RestaurantId,
        name: str,
        location: Location,
        cuisine_types: List[CuisineType],
        owner_id: str
    ):
        self._restaurant_id = restaurant_id
        self._name = name
        self._location = location
        self._cuisine_types = cuisine_types.copy()
        self._owner_id = owner_id
        
        # Restaurant state
        self._is_open = False
        self._menu_items: Dict[str, MenuItem] = {}
        self._rating = Decimal('0.0')
        self._total_reviews = 0
        
        # Operational metrics
        self._orders_completed_today = 0
        self._average_preparation_time = timedelta(minutes=20)
        self._capacity_orders_per_hour = 30
        
        print(f"🏪 Restaurant registered: {self._name}")
    
    @property
    def restaurant_id(self) -> RestaurantId:
        return self._restaurant_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def location(self) -> Location:
        return self._location
    
    @property
    def is_open(self) -> bool:
        return self._is_open
    
    @property
    def rating(self) -> Decimal:
        return self._rating
    
    @property
    def menu_items(self) -> List[MenuItem]:
        return list(self._menu_items.values())
    
    def open_restaurant(self) -> None:
        """Open restaurant for orders"""
        self._is_open = True
        print(f"🟢 {self._name} is now open for orders")
    
    def close_restaurant(self) -> None:
        """Close restaurant"""
        self._is_open = False
        print(f"🔴 {self._name} is now closed")
    
    def add_menu_item(self, menu_item: MenuItem) -> None:
        """Add item to menu"""
        self._menu_items[menu_item.item_id] = menu_item
        print(f"🍽️ Added menu item: {menu_item.name} - ₹{menu_item.price}")
    
    def update_item_availability(self, item_id: str, is_available: bool) -> None:
        """Update item availability"""
        if item_id not in self._menu_items:
            raise ValueError("Menu item not found")
        
        # Create new menu item with updated availability (immutable)
        old_item = self._menu_items[item_id]
        new_item = MenuItem(
            old_item.item_id,
            old_item.name,
            old_item.description,
            old_item.price,
            old_item.cuisine_type,
            old_item.is_vegetarian,
            is_available,
            old_item.preparation_time_minutes
        )
        self._menu_items[item_id] = new_item
        
        status = "available" if is_available else "unavailable"
        print(f"📋 {old_item.name} is now {status}")
    
    def estimate_preparation_time(self, items: List[OrderItem]) -> timedelta:
        """Estimate preparation time for order"""
        if not self._is_open:
            raise ValueError("Restaurant is closed")
        
        max_prep_time = 0
        total_items = sum(item.quantity for item in items)
        
        for order_item in items:
            if order_item.item_id in self._menu_items:
                menu_item = self._menu_items[order_item.item_id]
                prep_time = menu_item.preparation_time_minutes * order_item.quantity
                max_prep_time = max(max_prep_time, prep_time)
        
        # Add buffer based on restaurant load
        load_factor = min(self._orders_completed_today / 100, 2.0)  # Max 2x multiplier
        estimated_minutes = max_prep_time * (1 + load_factor * 0.3)
        
        return timedelta(minutes=int(estimated_minutes))
    
    def can_accept_order(self, items: List[OrderItem]) -> bool:
        """Check if restaurant can accept order"""
        if not self._is_open:
            return False
        
        # Check if all items are available
        for order_item in items:
            if order_item.item_id not in self._menu_items:
                return False
            
            menu_item = self._menu_items[order_item.item_id]
            if not menu_item.is_available:
                return False
        
        # Check capacity
        current_hour_orders = self._orders_completed_today % 24  # Simplified
        if current_hour_orders >= self._capacity_orders_per_hour:
            return False
        
        return True
    
    def record_order_completion(self) -> None:
        """Record that an order was completed"""
        self._orders_completed_today += 1
    
    def update_rating(self, new_rating: float) -> None:
        """Update restaurant rating"""
        if not (1.0 <= new_rating <= 5.0):
            raise ValueError("Rating must be between 1.0 and 5.0")
        
        # Weighted average with existing rating
        total_points = self._rating * self._total_reviews + Decimal(str(new_rating))
        self._total_reviews += 1
        self._rating = total_points / self._total_reviews
        
        print(f"⭐ Rating updated: {self._rating:.1f} ({self._total_reviews} reviews)")

# ====================================================================
# DELIVERY MANAGEMENT BOUNDED CONTEXT
# यह context delivery operations को handle करता है
# ====================================================================

class DeliveryPartnerStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

@dataclass(frozen=True)
class DeliveryPartnerId:
    """Delivery partner identifier"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.startswith("DEL_"):
            raise ValueError("Delivery partner ID must start with DEL_")

class DeliveryPartner:
    """
    Delivery Partner - Delivery Management Context
    
    यह entity delivery partner की information handle करता है।
    """
    
    def __init__(
        self,
        partner_id: DeliveryPartnerId,
        name: str,
        phone_number: str,
        vehicle_type: str,
        current_location: Location
    ):
        self._partner_id = partner_id
        self._name = name
        self._phone_number = phone_number
        self._vehicle_type = vehicle_type  # bike, bicycle, car
        self._current_location = current_location
        
        # Delivery state
        self._status = DeliveryPartnerStatus.OFFLINE
        self._current_order_id: Optional[str] = None
        self._earnings_today = Decimal('0.0')
        self._deliveries_completed_today = 0
        self._average_delivery_time = timedelta(minutes=25)
        
        print(f"🏍️ Delivery partner registered: {self._name}")
    
    @property
    def partner_id(self) -> DeliveryPartnerId:
        return self._partner_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def status(self) -> DeliveryPartnerStatus:
        return self._status
    
    @property
    def current_location(self) -> Location:
        return self._current_location
    
    @property
    def is_available(self) -> bool:
        return self._status == DeliveryPartnerStatus.AVAILABLE
    
    def go_online(self) -> None:
        """Go online and available for deliveries"""
        self._status = DeliveryPartnerStatus.AVAILABLE
        print(f"🟢 {self._name} is now online and available")
    
    def go_offline(self) -> None:
        """Go offline"""
        if self._status == DeliveryPartnerStatus.BUSY:
            raise ValueError("Cannot go offline while on delivery")
        
        self._status = DeliveryPartnerStatus.OFFLINE
        print(f"🔴 {self._name} is now offline")
    
    def accept_delivery(self, order_id: str) -> None:
        """Accept delivery assignment"""
        if not self.is_available:
            raise ValueError("Partner must be available to accept delivery")
        
        self._status = DeliveryPartnerStatus.BUSY
        self._current_order_id = order_id
        
        print(f"📦 {self._name} accepted delivery for order: {order_id}")
    
    def complete_delivery(self, delivery_fee: Decimal) -> None:
        """Complete delivery"""
        if self._status != DeliveryPartnerStatus.BUSY:
            raise ValueError("Partner must be on delivery to complete")
        
        self._status = DeliveryPartnerStatus.AVAILABLE
        self._current_order_id = None
        self._deliveries_completed_today += 1
        self._earnings_today += delivery_fee
        
        print(f"✅ {self._name} completed delivery")
        print(f"   Deliveries today: {self._deliveries_completed_today}")
        print(f"   Earnings today: ₹{self._earnings_today}")
    
    def update_location(self, new_location: Location) -> None:
        """Update current location"""
        self._current_location = new_location
        print(f"📍 {self._name} location updated to {new_location.pincode}")
    
    def calculate_distance_to(self, location: Location) -> float:
        """Calculate approximate distance to location (simplified)"""
        # Simplified distance calculation using Haversine formula approximation
        lat_diff = abs(self._current_location.latitude - location.latitude)
        lon_diff = abs(self._current_location.longitude - location.longitude)
        
        # Very rough approximation for demo
        distance_km = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # 111 km per degree
        return distance_km

# ====================================================================
# DOMAIN SERVICES - Cross-Context Services
# ====================================================================

class OrderFulfillmentService:
    """
    Domain Service that coordinates between different contexts
    यह service अलग-अलग contexts को coordinate करती है
    """
    
    def __init__(self):
        self._restaurants: Dict[str, RestaurantAggregate] = {}
        self._delivery_partners: Dict[str, DeliveryPartner] = {}
    
    def register_restaurant(self, restaurant: RestaurantAggregate) -> None:
        """Register restaurant"""
        self._restaurants[restaurant.restaurant_id.value] = restaurant
    
    def register_delivery_partner(self, partner: DeliveryPartner) -> None:
        """Register delivery partner"""
        self._delivery_partners[partner.partner_id.value] = partner
    
    def process_order(self, order: OrderAggregate) -> bool:
        """
        Process complete order workflow
        Complete order workflow process करना
        """
        print(f"\n🔄 Processing order: {order.order_id.value}")
        
        # Check if restaurant can accept order
        restaurant = self._restaurants.get(order.restaurant_id.value)
        if not restaurant:
            print(f"❌ Restaurant not found")
            return False
        
        if not restaurant.can_accept_order(order.items):
            print(f"❌ Restaurant cannot accept order")
            order.cancel_order("Restaurant unavailable or items out of stock")
            return False
        
        # Estimate preparation time
        prep_time = restaurant.estimate_preparation_time(order.items)
        order.confirm_order(prep_time)
        
        # Start preparation
        order.start_preparation()
        
        # Simulate preparation completion
        import time
        print(f"⏱️ Simulating preparation ({prep_time.total_seconds() / 60:.0f} minutes)...")
        # time.sleep(1)  # Simulate some time - disabled for demo
        
        order.mark_ready_for_pickup()
        restaurant.record_order_completion()
        
        # Find available delivery partner
        available_partners = [
            partner for partner in self._delivery_partners.values()
            if partner.is_available
        ]
        
        if not available_partners:
            print(f"❌ No delivery partners available")
            return False
        
        # Find closest partner
        customer_location = order._delivery_info.address
        closest_partner = min(
            available_partners,
            key=lambda p: p.calculate_distance_to(customer_location)
        )
        
        # Assign delivery
        closest_partner.accept_delivery(order.order_id.value)
        order.assign_delivery_partner(closest_partner.partner_id.value)
        
        # Simulate delivery
        print(f"🚚 Simulating delivery...")
        # time.sleep(1)  # Simulate delivery time
        
        order.mark_delivered()
        delivery_fee = Decimal('20.00')
        closest_partner.complete_delivery(delivery_fee)
        
        return True

# ====================================================================
# EXAMPLE USAGE
# ====================================================================

def create_sample_zomato_ecosystem():
    """Create complete Zomato ecosystem with all contexts"""
    
    print("🍽️ Setting up Zomato Ecosystem")
    print("=" * 40)
    
    # Locations
    mumbai_bandra = Location(19.0596, 72.8295, "Bandra West, Mumbai", "400050")
    mumbai_andheri = Location(19.1197, 72.8464, "Andheri West, Mumbai", "400058")
    
    # Create Restaurant (Restaurant Context)
    restaurant = RestaurantAggregate(
        restaurant_id=RestaurantId("REST_001"),
        name="Punjabi Tadka - Bandra",
        location=mumbai_bandra,
        cuisine_types=[CuisineType.NORTH_INDIAN],
        owner_id="OWNER_001"
    )
    
    # Add menu items
    restaurant.add_menu_item(MenuItem(
        "ITEM_001", "Butter Chicken", "Creamy tomato based chicken curry",
        Decimal("320.00"), CuisineType.NORTH_INDIAN, False, True, 25
    ))
    
    restaurant.add_menu_item(MenuItem(
        "ITEM_002", "Paneer Makhani", "Rich creamy paneer curry",
        Decimal("280.00"), CuisineType.NORTH_INDIAN, True, True, 20
    ))
    
    restaurant.add_menu_item(MenuItem(
        "ITEM_003", "Garlic Naan", "Fresh garlic naan bread",
        Decimal("60.00"), CuisineType.NORTH_INDIAN, True, True, 10
    ))
    
    restaurant.open_restaurant()
    
    # Create Delivery Partners (Delivery Context)
    partner1 = DeliveryPartner(
        DeliveryPartnerId("DEL_001"),
        "Rajesh Kumar",
        "9876543210",
        "bike",
        mumbai_bandra
    )
    partner1.go_online()
    
    partner2 = DeliveryPartner(
        DeliveryPartnerId("DEL_002"),
        "Amit Sharma",
        "9876543211",
        "bicycle",
        mumbai_andheri
    )
    partner2.go_online()
    
    # Create Order (Order Context)
    order_items = [
        OrderItem("ITEM_001", "Butter Chicken", 1, Decimal("320.00")),
        OrderItem("ITEM_002", "Paneer Makhani", 1, Decimal("280.00")),
        OrderItem("ITEM_003", "Garlic Naan", 2, Decimal("60.00"))
    ]
    
    delivery_info = DeliveryInfo(
        address=mumbai_andheri,
        customer_phone="8765432109",
        delivery_instructions="Ring the bell twice"
    )
    
    order = OrderAggregate(
        OrderId("ZOM_ORDER_001"),
        CustomerId("CUST_001"),
        RestaurantId("REST_001"),
        order_items,
        delivery_info
    )
    
    # Create Fulfillment Service (Domain Service)
    fulfillment_service = OrderFulfillmentService()
    fulfillment_service.register_restaurant(restaurant)
    fulfillment_service.register_delivery_partner(partner1)
    fulfillment_service.register_delivery_partner(partner2)
    
    return fulfillment_service, order, restaurant

if __name__ == "__main__":
    print("🏛️ Zomato Bounded Context Example - DDD")
    print("=" * 45)
    
    # Create ecosystem
    fulfillment_service, sample_order, sample_restaurant = create_sample_zomato_ecosystem()
    
    print(f"\n📋 Order Details:")
    print(f"   Order ID: {sample_order.order_id.value}")
    print(f"   Customer: {sample_order.customer_id.value}")
    print(f"   Restaurant: {sample_restaurant.name}")
    print(f"   Items: {len(sample_order.items)}")
    print(f"   Total: ₹{sample_order.total_amount}")
    
    # Process the order
    success = fulfillment_service.process_order(sample_order)
    
    if success:
        print(f"\n✅ Order processed successfully!")
        print(f"   Final Status: {sample_order.status.value}")
    else:
        print(f"\n❌ Order processing failed!")
    
    print(f"\n📊 Restaurant Status:")
    print(f"   Orders completed today: {sample_restaurant._orders_completed_today}")
    print(f"   Current rating: {sample_restaurant.rating}")
    print(f"   Is open: {sample_restaurant.is_open}")
    
    print(f"\n✨ All bounded contexts working together!")
    print(f"✨ Each context maintains its own domain model!")
    print(f"✨ Ready for microservices architecture!")