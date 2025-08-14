#!/usr/bin/env python3
"""
Domain-Driven Design: Domain Services - Swiggy Order Fulfillment
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में Domain Services का इस्तेमाल करके
complex business logic को handle करते हैं जो multiple aggregates को involve करती है।

Author: Hindi Tech Podcast
Date: 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Protocol
from dataclasses import dataclass
from uuid import uuid4
from decimal import Decimal
from enum import Enum
import math

# ====================================================================
# DOMAIN ENTITIES AND VALUE OBJECTS
# ====================================================================

# Enums
class OrderStatus(Enum):
    PLACED = "placed"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    ASSIGNED_TO_DELIVERY = "assigned_to_delivery"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class DeliveryPartnerStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class RestaurantStatus(Enum):
    OPEN = "open"
    BUSY = "busy"
    CLOSED = "closed"

# Value Objects
@dataclass(frozen=True)
class Location:
    """Geographic location with address"""
    latitude: float
    longitude: float
    address: str
    pincode: str
    landmark: Optional[str] = None
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Invalid latitude")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Invalid longitude")
        if len(self.pincode) != 6 or not self.pincode.isdigit():
            raise ValueError("Pincode must be 6 digits")

@dataclass(frozen=True)
class Money:
    """Money value object"""
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount - other.amount, self.currency)

@dataclass(frozen=True)
class OrderItem:
    """Individual order item"""
    item_id: str
    name: str
    quantity: int
    unit_price: Money
    preparation_time_minutes: int
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.preparation_time_minutes <= 0:
            raise ValueError("Preparation time must be positive")
    
    @property
    def total_price(self) -> Money:
        return Money(self.unit_price.amount * self.quantity)

# ====================================================================
# DOMAIN ENTITIES (Aggregates)
# ====================================================================

class Order:
    """
    Order Aggregate - Represents customer order
    Order aggregate - customer के order को represent करता है
    """
    
    def __init__(
        self,
        order_id: str,
        customer_id: str,
        restaurant_id: str,
        items: List[OrderItem],
        delivery_address: Location
    ):
        if not items:
            raise ValueError("Order must have at least one item")
        
        self._order_id = order_id
        self._customer_id = customer_id
        self._restaurant_id = restaurant_id
        self._items = items.copy()
        self._delivery_address = delivery_address
        
        # Order state
        self._status = OrderStatus.PLACED
        self._placed_at = datetime.now()
        self._updated_at = datetime.now()
        
        # Pricing
        subtotal = sum(item.total_price.amount for item in items)
        self._subtotal = Money(subtotal)
        self._taxes = Money(subtotal * Decimal('0.05'))  # 5% tax
        self._delivery_fee = Money(Decimal('0'))  # Will be calculated by domain service
        self._total_amount = Money(subtotal + self._taxes.amount)
        
        # Fulfillment details
        self._delivery_partner_id: Optional[str] = None
        self._estimated_delivery_time: Optional[datetime] = None
        self._actual_delivery_time: Optional[datetime] = None
        
        print(f"📋 Order placed: {self._order_id}")
        print(f"   Items: {len(self._items)}")
        print(f"   Subtotal: ₹{self._subtotal.amount}")
    
    @property
    def order_id(self) -> str:
        return self._order_id
    
    @property
    def customer_id(self) -> str:
        return self._customer_id
    
    @property
    def restaurant_id(self) -> str:
        return self._restaurant_id
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()
    
    @property
    def delivery_address(self) -> Location:
        return self._delivery_address
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def total_amount(self) -> Money:
        return self._total_amount
    
    @property
    def subtotal(self) -> Money:
        return self._subtotal
    
    @property
    def delivery_fee(self) -> Money:
        return self._delivery_fee
    
    @property
    def estimated_delivery_time(self) -> Optional[datetime]:
        return self._estimated_delivery_time
    
    def accept_order(self, preparation_time: timedelta) -> None:
        """Restaurant accepts order"""
        if self._status != OrderStatus.PLACED:
            raise ValueError("Order must be in placed status")
        
        self._status = OrderStatus.ACCEPTED
        self._updated_at = datetime.now()
        
        # Estimate delivery time
        self._estimated_delivery_time = datetime.now() + preparation_time + timedelta(minutes=20)
        
        print(f"✅ Order accepted: {self._order_id}")
        print(f"   Estimated delivery: {self._estimated_delivery_time.strftime('%H:%M')}")
    
    def start_preparation(self) -> None:
        """Start food preparation"""
        if self._status != OrderStatus.ACCEPTED:
            raise ValueError("Order must be accepted first")
        
        self._status = OrderStatus.PREPARING
        self._updated_at = datetime.now()
        
        print(f"👨‍🍳 Preparation started: {self._order_id}")
    
    def mark_ready_for_pickup(self) -> None:
        """Mark order ready for pickup"""
        if self._status != OrderStatus.PREPARING:
            raise ValueError("Order must be in preparing status")
        
        self._status = OrderStatus.READY_FOR_PICKUP
        self._updated_at = datetime.now()
        
        print(f"🍽️ Ready for pickup: {self._order_id}")
    
    def assign_delivery_partner(self, partner_id: str) -> None:
        """Assign delivery partner"""
        if self._status != OrderStatus.READY_FOR_PICKUP:
            raise ValueError("Order must be ready for pickup")
        
        self._status = OrderStatus.ASSIGNED_TO_DELIVERY
        self._delivery_partner_id = partner_id
        self._updated_at = datetime.now()
        
        print(f"🚚 Assigned to delivery partner: {partner_id}")
    
    def start_delivery(self) -> None:
        """Start delivery"""
        if self._status != OrderStatus.ASSIGNED_TO_DELIVERY:
            raise ValueError("Order must be assigned to delivery partner")
        
        self._status = OrderStatus.OUT_FOR_DELIVERY
        self._updated_at = datetime.now()
        
        print(f"🏍️ Out for delivery: {self._order_id}")
    
    def mark_delivered(self) -> None:
        """Mark order as delivered"""
        if self._status != OrderStatus.OUT_FOR_DELIVERY:
            raise ValueError("Order must be out for delivery")
        
        self._status = OrderStatus.DELIVERED
        self._actual_delivery_time = datetime.now()
        self._updated_at = datetime.now()
        
        delivery_duration = (self._actual_delivery_time - self._placed_at).total_seconds() / 60
        print(f"🎉 Order delivered: {self._order_id}")
        print(f"   Delivery time: {delivery_duration:.0f} minutes")
    
    def cancel_order(self, reason: str) -> None:
        """Cancel order"""
        if self._status in [OrderStatus.DELIVERED, OrderStatus.OUT_FOR_DELIVERY]:
            raise ValueError("Cannot cancel delivered or out-for-delivery orders")
        
        self._status = OrderStatus.CANCELLED
        self._updated_at = datetime.now()
        
        print(f"❌ Order cancelled: {self._order_id}")
        print(f"   Reason: {reason}")
    
    def update_delivery_fee(self, delivery_fee: Money) -> None:
        """Update delivery fee (called by domain service)"""
        self._delivery_fee = delivery_fee
        self._total_amount = self._subtotal.add(self._taxes).add(delivery_fee)
        
        print(f"💰 Delivery fee updated: ₹{delivery_fee.amount}")
        print(f"   Total amount: ₹{self._total_amount.amount}")
    
    def get_max_preparation_time(self) -> int:
        """Get maximum preparation time for all items"""
        return max(item.preparation_time_minutes for item in self._items)

class Restaurant:
    """
    Restaurant Aggregate
    Restaurant aggregate - restaurant की details और capacity
    """
    
    def __init__(
        self,
        restaurant_id: str,
        name: str,
        location: Location,
        cuisine_types: List[str]
    ):
        self._restaurant_id = restaurant_id
        self._name = name
        self._location = location
        self._cuisine_types = cuisine_types.copy()
        
        # Restaurant state
        self._status = RestaurantStatus.CLOSED
        self._current_orders_count = 0
        self._max_concurrent_orders = 25
        self._average_preparation_time = timedelta(minutes=20)
        self._rating = Decimal('4.0')
        self._delivery_radius_km = 8.0
        
        print(f"🏪 Restaurant created: {self._name}")
    
    @property
    def restaurant_id(self) -> str:
        return self._restaurant_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def location(self) -> Location:
        return self._location
    
    @property
    def status(self) -> RestaurantStatus:
        return self._status
    
    @property
    def current_orders_count(self) -> int:
        return self._current_orders_count
    
    @property
    def max_concurrent_orders(self) -> int:
        return self._max_concurrent_orders
    
    @property
    def rating(self) -> Decimal:
        return self._rating
    
    @property
    def delivery_radius_km(self) -> float:
        return self._delivery_radius_km
    
    def open_restaurant(self) -> None:
        """Open restaurant for orders"""
        self._status = RestaurantStatus.OPEN
        print(f"🟢 {self._name} is now open")
    
    def close_restaurant(self) -> None:
        """Close restaurant"""
        self._status = RestaurantStatus.CLOSED
        print(f"🔴 {self._name} is now closed")
    
    def can_accept_order(self) -> bool:
        """Check if restaurant can accept new orders"""
        if self._status != RestaurantStatus.OPEN:
            return False
        
        if self._current_orders_count >= self._max_concurrent_orders:
            return False
        
        return True
    
    def accept_new_order(self) -> None:
        """Accept a new order (increment counter)"""
        if not self.can_accept_order():
            raise ValueError("Cannot accept new order")
        
        self._current_orders_count += 1
        
        # Update status based on load
        if self._current_orders_count >= self._max_concurrent_orders * 0.8:
            self._status = RestaurantStatus.BUSY
    
    def complete_order(self) -> None:
        """Complete an order (decrement counter)"""
        if self._current_orders_count > 0:
            self._current_orders_count -= 1
        
        # Update status
        if self._current_orders_count < self._max_concurrent_orders * 0.8:
            self._status = RestaurantStatus.OPEN
    
    def estimate_preparation_time(self, items: List[OrderItem]) -> timedelta:
        """Estimate preparation time based on current load"""
        base_time = max(item.preparation_time_minutes for item in items)
        
        # Add delay based on current load
        load_factor = self._current_orders_count / self._max_concurrent_orders
        delay_minutes = base_time * load_factor * 0.5  # Up to 50% delay
        
        total_minutes = base_time + delay_minutes
        return timedelta(minutes=int(total_minutes))
    
    def is_within_delivery_radius(self, customer_location: Location) -> bool:
        """Check if customer is within delivery radius"""
        distance = self.calculate_distance_to(customer_location)
        return distance <= self._delivery_radius_km
    
    def calculate_distance_to(self, location: Location) -> float:
        """Calculate distance to location using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(self._location.latitude)
        lon1_rad = math.radians(self._location.longitude)
        lat2_rad = math.radians(location.latitude)
        lon2_rad = math.radians(location.longitude)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

class DeliveryPartner:
    """
    Delivery Partner Aggregate
    Delivery partner aggregate - delivery करने वाले की details
    """
    
    def __init__(
        self,
        partner_id: str,
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
        
        # Partner state
        self._status = DeliveryPartnerStatus.OFFLINE
        self._current_order_id: Optional[str] = None
        self._earnings_today = Money(Decimal('0'))
        self._deliveries_completed_today = 0
        self._rating = Decimal('4.5')
        
        # Performance metrics
        self._average_delivery_time = timedelta(minutes=25)
        self._max_delivery_distance_km = 10.0
        
        print(f"🏍️ Delivery partner registered: {self._name}")
    
    @property
    def partner_id(self) -> str:
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
    
    @property
    def rating(self) -> Decimal:
        return self._rating
    
    @property
    def earnings_today(self) -> Money:
        return self._earnings_today
    
    @property
    def deliveries_completed_today(self) -> int:
        return self._deliveries_completed_today
    
    def go_online(self) -> None:
        """Go online and available for deliveries"""
        self._status = DeliveryPartnerStatus.AVAILABLE
        print(f"🟢 {self._name} is now online")
    
    def go_offline(self) -> None:
        """Go offline"""
        if self._status == DeliveryPartnerStatus.BUSY:
            raise ValueError("Cannot go offline while on delivery")
        
        self._status = DeliveryPartnerStatus.OFFLINE
        print(f"🔴 {self._name} is now offline")
    
    def accept_delivery(self, order_id: str) -> None:
        """Accept delivery assignment"""
        if not self.is_available:
            raise ValueError("Partner must be available")
        
        self._status = DeliveryPartnerStatus.BUSY
        self._current_order_id = order_id
        
        print(f"📦 {self._name} accepted delivery: {order_id}")
    
    def complete_delivery(self, delivery_fee: Money) -> None:
        """Complete delivery and update metrics"""
        if self._status != DeliveryPartnerStatus.BUSY:
            raise ValueError("Partner must be on delivery")
        
        self._status = DeliveryPartnerStatus.AVAILABLE
        self._current_order_id = None
        self._deliveries_completed_today += 1
        self._earnings_today = self._earnings_today.add(delivery_fee)
        
        print(f"✅ {self._name} completed delivery")
        print(f"   Earnings today: ₹{self._earnings_today.amount}")
        print(f"   Deliveries today: {self._deliveries_completed_today}")
    
    def update_location(self, new_location: Location) -> None:
        """Update current location"""
        self._current_location = new_location
    
    def calculate_distance_to(self, location: Location) -> float:
        """Calculate distance to location"""
        # Reuse the same Haversine formula as Restaurant
        R = 6371
        
        lat1_rad = math.radians(self._current_location.latitude)
        lon1_rad = math.radians(self._current_location.longitude)
        lat2_rad = math.radians(location.latitude)
        lon2_rad = math.radians(location.longitude)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def can_deliver_to(self, location: Location) -> bool:
        """Check if partner can deliver to location"""
        distance = self.calculate_distance_to(location)
        return distance <= self._max_delivery_distance_km

# ====================================================================
# DOMAIN SERVICES - Complex Business Logic
# ====================================================================

class DeliveryFeeCalculationService:
    """
    Domain Service for calculating delivery fees
    Delivery fee calculate करने के लिए domain service
    """
    
    @staticmethod
    def calculate_delivery_fee(
        restaurant_location: Location,
        customer_location: Location,
        order_value: Money,
        time_of_day: datetime,
        weather_condition: str = "normal"
    ) -> Money:
        """
        Calculate dynamic delivery fee based on multiple factors
        Multiple factors के base पर delivery fee calculate करना
        """
        # Base fee calculation based on distance
        distance_km = DeliveryFeeCalculationService._calculate_distance(
            restaurant_location, customer_location
        )
        
        # Base fee: ₹5 per km with minimum ₹20
        base_fee = max(Decimal('20'), Decimal(str(distance_km)) * Decimal('5'))
        
        # Order value discount
        if order_value.amount >= Decimal('500'):
            base_fee = Decimal('0')  # Free delivery for orders ₹500+
        elif order_value.amount >= Decimal('200'):
            base_fee = base_fee * Decimal('0.5')  # 50% discount
        
        # Time-based surge pricing
        hour = time_of_day.hour
        if hour >= 12 and hour <= 14:  # Lunch rush
            base_fee = base_fee * Decimal('1.3')  # 30% surge
        elif hour >= 19 and hour <= 21:  # Dinner rush
            base_fee = base_fee * Decimal('1.5')  # 50% surge
        elif hour >= 22 or hour <= 6:  # Late night/early morning
            base_fee = base_fee * Decimal('1.2')  # 20% surge
        
        # Weather conditions
        if weather_condition in ["heavy_rain", "storm"]:
            base_fee = base_fee * Decimal('1.4')  # 40% bad weather charge
        elif weather_condition in ["light_rain", "cloudy"]:
            base_fee = base_fee * Decimal('1.1')  # 10% charge
        
        return Money(base_fee)
    
    @staticmethod
    def _calculate_distance(loc1: Location, loc2: Location) -> float:
        """Calculate distance between two locations"""
        R = 6371
        
        lat1_rad = math.radians(loc1.latitude)
        lon1_rad = math.radians(loc1.longitude)
        lat2_rad = math.radians(loc2.latitude)
        lon2_rad = math.radians(loc2.longitude)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

class DeliveryPartnerAssignmentService:
    """
    Domain Service for assigning optimal delivery partners
    Optimal delivery partner assign करने के लिए domain service
    """
    
    @staticmethod
    def find_best_delivery_partner(
        available_partners: List[DeliveryPartner],
        restaurant_location: Location,
        customer_location: Location,
        urgency_level: str = "normal"
    ) -> Optional[DeliveryPartner]:
        """
        Find the best delivery partner based on multiple criteria
        Multiple criteria के base पर best delivery partner find करना
        """
        if not available_partners:
            return None
        
        # Filter partners who can deliver to customer location
        eligible_partners = [
            partner for partner in available_partners
            if partner.is_available and partner.can_deliver_to(customer_location)
        ]
        
        if not eligible_partners:
            return None
        
        # Scoring algorithm
        scored_partners = []
        
        for partner in eligible_partners:
            score = DeliveryPartnerAssignmentService._calculate_partner_score(
                partner, restaurant_location, customer_location, urgency_level
            )
            scored_partners.append((partner, score))
        
        # Sort by score (descending) and return best partner
        scored_partners.sort(key=lambda x: x[1], reverse=True)
        best_partner = scored_partners[0][0]
        
        print(f"🎯 Best partner selected: {best_partner.name}")
        print(f"   Score: {scored_partners[0][1]:.2f}")
        print(f"   Rating: {best_partner.rating}")
        
        return best_partner
    
    @staticmethod
    def _calculate_partner_score(
        partner: DeliveryPartner,
        restaurant_location: Location,
        customer_location: Location,
        urgency_level: str
    ) -> float:
        """
        Calculate partner suitability score
        Partner की suitability score calculate करना
        """
        score = 0.0
        
        # Distance to restaurant (closer is better)
        distance_to_restaurant = partner.calculate_distance_to(restaurant_location)
        distance_score = max(0, 10 - distance_to_restaurant)  # Max 10 points
        score += distance_score * 0.4  # 40% weight
        
        # Partner rating (higher is better)
        rating_score = float(partner.rating)  # 0-5 scale
        score += rating_score * 0.3  # 30% weight
        
        # Deliveries completed today (experience factor)
        experience_score = min(5, partner.deliveries_completed_today * 0.5)
        score += experience_score * 0.2  # 20% weight
        
        # Vehicle type preference based on urgency
        vehicle_score = 0
        if urgency_level == "urgent":
            if partner._vehicle_type == "bike":
                vehicle_score = 2  # Bikes are fastest
            elif partner._vehicle_type == "bicycle":
                vehicle_score = 1
        else:  # normal urgency
            if partner._vehicle_type in ["bike", "bicycle"]:
                vehicle_score = 2
            elif partner._vehicle_type == "car":
                vehicle_score = 1.5
        
        score += vehicle_score * 0.1  # 10% weight
        
        return score

class OrderFulfillmentService:
    """
    Core Domain Service for order fulfillment
    Order fulfillment के लिए core domain service
    """
    
    def __init__(self):
        self._restaurants: Dict[str, Restaurant] = {}
        self._delivery_partners: Dict[str, DeliveryPartner] = {}
        self._orders: Dict[str, Order] = {}
        
        # External services
        self._delivery_fee_service = DeliveryFeeCalculationService()
        self._partner_assignment_service = DeliveryPartnerAssignmentService()
    
    def register_restaurant(self, restaurant: Restaurant) -> None:
        """Register restaurant in the system"""
        self._restaurants[restaurant.restaurant_id] = restaurant
        print(f"🏪 Restaurant registered: {restaurant.name}")
    
    def register_delivery_partner(self, partner: DeliveryPartner) -> None:
        """Register delivery partner in the system"""
        self._delivery_partners[partner.partner_id] = partner
        print(f"🏍️ Partner registered: {partner.name}")
    
    def process_order(
        self,
        order: Order,
        weather_condition: str = "normal",
        urgency_level: str = "normal"
    ) -> bool:
        """
        Process complete order fulfillment workflow
        Complete order fulfillment workflow process करना
        """
        print(f"\n🔄 Processing order: {order.order_id}")
        
        # Step 1: Validate restaurant can accept order
        restaurant = self._restaurants.get(order.restaurant_id)
        if not restaurant:
            print(f"❌ Restaurant not found: {order.restaurant_id}")
            order.cancel_order("Restaurant not found")
            return False
        
        if not restaurant.can_accept_order():
            print(f"❌ Restaurant cannot accept more orders")
            order.cancel_order("Restaurant capacity full")
            return False
        
        # Check delivery radius
        if not restaurant.is_within_delivery_radius(order.delivery_address):
            print(f"❌ Customer outside delivery radius")
            order.cancel_order("Outside delivery radius")
            return False
        
        # Step 2: Calculate and update delivery fee
        delivery_fee = self._delivery_fee_service.calculate_delivery_fee(
            restaurant.location,
            order.delivery_address,
            order.subtotal,
            datetime.now(),
            weather_condition
        )
        order.update_delivery_fee(delivery_fee)
        
        # Step 3: Restaurant accepts order
        preparation_time = restaurant.estimate_preparation_time(order.items)
        restaurant.accept_new_order()
        order.accept_order(preparation_time)
        
        # Step 4: Start preparation
        order.start_preparation()
        
        # Simulate preparation time (in real system, this would be event-driven)
        print(f"⏱️ Simulating preparation ({preparation_time.total_seconds() / 60:.0f} minutes)...")
        
        # Step 5: Mark ready for pickup
        order.mark_ready_for_pickup()
        
        # Step 6: Find and assign delivery partner
        available_partners = [
            partner for partner in self._delivery_partners.values()
            if partner.is_available
        ]
        
        best_partner = self._partner_assignment_service.find_best_delivery_partner(
            available_partners,
            restaurant.location,
            order.delivery_address,
            urgency_level
        )
        
        if not best_partner:
            print(f"❌ No available delivery partners")
            return False
        
        # Step 7: Assign delivery
        best_partner.accept_delivery(order.order_id)
        order.assign_delivery_partner(best_partner.partner_id)
        
        # Step 8: Start and complete delivery
        order.start_delivery()
        
        print(f"🚚 Simulating delivery...")
        
        order.mark_delivered()
        best_partner.complete_delivery(delivery_fee)
        restaurant.complete_order()
        
        # Store order
        self._orders[order.order_id] = order
        
        return True
    
    def get_restaurant_analytics(self, restaurant_id: str) -> Dict[str, Any]:
        """Get restaurant performance analytics"""
        restaurant = self._restaurants.get(restaurant_id)
        if not restaurant:
            return {}
        
        # Find orders for this restaurant
        restaurant_orders = [
            order for order in self._orders.values()
            if order.restaurant_id == restaurant_id
        ]
        
        total_revenue = sum(
            order.total_amount.amount for order in restaurant_orders
            if order.status == OrderStatus.DELIVERED
        )
        
        delivered_orders = [
            order for order in restaurant_orders
            if order.status == OrderStatus.DELIVERED
        ]
        
        avg_delivery_time = 0
        if delivered_orders:
            total_time = sum(
                (order._actual_delivery_time - order._placed_at).total_seconds() / 60
                for order in delivered_orders
                if order._actual_delivery_time
            )
            avg_delivery_time = total_time / len(delivered_orders)
        
        return {
            "restaurant_name": restaurant.name,
            "total_orders": len(restaurant_orders),
            "delivered_orders": len(delivered_orders),
            "total_revenue": float(total_revenue),
            "current_load": restaurant.current_orders_count,
            "max_capacity": restaurant.max_concurrent_orders,
            "average_delivery_time_minutes": round(avg_delivery_time, 1),
            "rating": float(restaurant.rating)
        }
    
    def get_delivery_partner_analytics(self, partner_id: str) -> Dict[str, Any]:
        """Get delivery partner performance analytics"""
        partner = self._delivery_partners.get(partner_id)
        if not partner:
            return {}
        
        return {
            "partner_name": partner.name,
            "status": partner.status.value,
            "deliveries_today": partner.deliveries_completed_today,
            "earnings_today": float(partner.earnings_today.amount),
            "rating": float(partner.rating),
            "vehicle_type": partner._vehicle_type
        }

def create_swiggy_ecosystem():
    """Create complete Swiggy ecosystem for testing"""
    
    print("🍽️ Creating Swiggy Ecosystem")
    print("=" * 30)
    
    # Create locations
    mumbai_bandra = Location(19.0596, 72.8295, "Bandra West, Mumbai", "400050")
    mumbai_andheri = Location(19.1197, 72.8464, "Andheri West, Mumbai", "400058")
    mumbai_juhu = Location(19.1075, 72.8263, "Juhu, Mumbai", "400049")
    
    # Create restaurants
    restaurant1 = Restaurant(
        "REST_001",
        "Punjabi Dhaba - Bandra",
        mumbai_bandra,
        ["North Indian", "Punjabi"]
    )
    restaurant1.open_restaurant()
    
    restaurant2 = Restaurant(
        "REST_002",
        "South Indian Express",
        mumbai_andheri,
        ["South Indian", "Breakfast"]
    )
    restaurant2.open_restaurant()
    
    # Create delivery partners
    partner1 = DeliveryPartner(
        "DEL_001",
        "Rajesh Kumar",
        "9876543210",
        "bike",
        mumbai_bandra
    )
    partner1.go_online()
    
    partner2 = DeliveryPartner(
        "DEL_002",
        "Amit Sharma", 
        "9876543211",
        "bicycle",
        mumbai_andheri
    )
    partner2.go_online()
    
    partner3 = DeliveryPartner(
        "DEL_003",
        "Priya Singh",
        "9876543212",
        "bike", 
        mumbai_juhu
    )
    partner3.go_online()
    
    # Create fulfillment service
    fulfillment_service = OrderFulfillmentService()
    fulfillment_service.register_restaurant(restaurant1)
    fulfillment_service.register_restaurant(restaurant2)
    fulfillment_service.register_delivery_partner(partner1)
    fulfillment_service.register_delivery_partner(partner2)
    fulfillment_service.register_delivery_partner(partner3)
    
    # Create sample orders
    order_items1 = [
        OrderItem("ITEM_001", "Butter Chicken", 1, Money(Decimal("320")), 25),
        OrderItem("ITEM_002", "Garlic Naan", 2, Money(Decimal("60")), 10),
        OrderItem("ITEM_003", "Lassi", 2, Money(Decimal("80")), 5)
    ]
    
    order1 = Order(
        "ORD_001",
        "CUST_001",
        "REST_001",
        order_items1,
        mumbai_juhu  # Customer in Juhu
    )
    
    order_items2 = [
        OrderItem("ITEM_004", "Masala Dosa", 2, Money(Decimal("120")), 15),
        OrderItem("ITEM_005", "Filter Coffee", 2, Money(Decimal("40")), 5)
    ]
    
    order2 = Order(
        "ORD_002", 
        "CUST_002",
        "REST_002",
        order_items2,
        mumbai_bandra  # Customer in Bandra
    )
    
    return fulfillment_service, [order1, order2], [restaurant1, restaurant2]

def simulate_swiggy_domain_services():
    """Simulate Swiggy system with Domain Services"""
    
    print("🏛️ Swiggy Domain Services Simulation")
    print("=" * 40)
    
    # Create ecosystem
    fulfillment_service, orders, restaurants = create_swiggy_ecosystem()
    
    print(f"\n📋 Processing Orders with Domain Services:")
    
    # Process orders with different conditions
    for i, order in enumerate(orders, 1):
        print(f"\n--- Order {i} ---")
        
        # Vary conditions for different orders
        weather = "normal" if i == 1 else "light_rain"
        urgency = "normal" if i == 1 else "urgent"
        
        success = fulfillment_service.process_order(order, weather, urgency)
        
        if success:
            print(f"✅ Order {order.order_id} completed successfully!")
        else:
            print(f"❌ Order {order.order_id} failed!")
    
    print(f"\n📊 Analytics Dashboard:")
    print("=" * 25)
    
    # Restaurant analytics
    print(f"\n🏪 Restaurant Performance:")
    for restaurant in restaurants:
        analytics = fulfillment_service.get_restaurant_analytics(restaurant.restaurant_id)
        print(f"\n   {analytics['restaurant_name']}:")
        print(f"   • Total Orders: {analytics['total_orders']}")
        print(f"   • Delivered: {analytics['delivered_orders']}")
        print(f"   • Revenue: ₹{analytics['total_revenue']}")
        print(f"   • Avg Delivery Time: {analytics['average_delivery_time_minutes']} min")
        print(f"   • Current Load: {analytics['current_load']}/{analytics['max_capacity']}")
    
    # Delivery partner analytics
    print(f"\n🏍️ Delivery Partner Performance:")
    for partner_id in fulfillment_service._delivery_partners.keys():
        analytics = fulfillment_service.get_delivery_partner_analytics(partner_id)
        print(f"\n   {analytics['partner_name']}:")
        print(f"   • Status: {analytics['status']}")
        print(f"   • Deliveries Today: {analytics['deliveries_today']}")
        print(f"   • Earnings Today: ₹{analytics['earnings_today']}")
        print(f"   • Rating: {analytics['rating']}⭐")
        print(f"   • Vehicle: {analytics['vehicle_type']}")
    
    print(f"\n✨ Domain Services Benefits Demonstrated:")
    print(f"   ✅ Complex business logic encapsulated")
    print(f"   ✅ Cross-aggregate operations handled")
    print(f"   ✅ Dynamic pricing implemented")
    print(f"   ✅ Optimal partner assignment")
    print(f"   ✅ Separation of concerns maintained")

if __name__ == "__main__":
    print("🏛️ Swiggy Domain Services - DDD Example")
    print("=" * 45)
    
    simulate_swiggy_domain_services()
    
    print(f"\n✨ Domain Services pattern successfully implemented!")
    print(f"✨ Ready for production Swiggy-scale system!")
    print(f"✨ Complex business logic properly orchestrated!")