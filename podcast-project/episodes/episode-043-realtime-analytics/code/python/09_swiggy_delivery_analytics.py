#!/usr/bin/env python3
"""
Swiggy Real-time Delivery Analytics
Episode 43: Real-time Analytics at Scale

यह example Swiggy का real-time delivery analytics system दिखाता है
Order placement से delivery completion तक का complete tracking और optimization।

Real Production Stats:
- Swiggy: 6+ lakh orders daily
- Peak delivery time: 30 minutes average
- Delivery partner tracking: Real-time GPS updates
- Dynamic pricing based on demand/supply
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    PLACED = "PLACED"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY = "READY"
    PICKED = "PICKED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class DeliveryPartnerStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"

@dataclass
class Location:
    """GPS coordinates"""
    lat: float
    lng: float
    address: str

@dataclass
class DeliveryPartner:
    """Delivery partner information"""
    partner_id: str
    name: str
    phone: str
    current_location: Location
    status: DeliveryPartnerStatus
    rating: float
    total_deliveries: int
    earnings_today: float
    vehicle_type: str  # bike, cycle

@dataclass
class Restaurant:
    """Restaurant information"""
    restaurant_id: str
    name: str
    location: Location
    cuisine_type: str
    rating: float
    avg_prep_time: int  # minutes
    is_busy: bool
    current_orders: int

@dataclass
class Order:
    """Food order information"""
    order_id: str
    customer_id: str
    restaurant: Restaurant
    delivery_location: Location
    items: List[Dict]
    total_amount: float
    order_time: datetime
    estimated_delivery_time: datetime
    actual_delivery_time: Optional[datetime]
    status: OrderStatus
    assigned_partner: Optional[DeliveryPartner]
    distance_km: float
    weather_condition: str

class SwiggyDeliveryAnalytics:
    """
    Real-time delivery analytics for Swiggy-like platform
    Complete order lifecycle tracking and optimization
    """
    
    def __init__(self):
        # Order management
        self.active_orders = {}  # order_id -> Order
        self.completed_orders = []
        self.cancelled_orders = []
        
        # Delivery partner management
        self.delivery_partners = {}  # partner_id -> DeliveryPartner
        self.partner_locations = {}  # Real-time location tracking
        
        # Restaurant management
        self.restaurants = {}  # restaurant_id -> Restaurant
        
        # Real-time analytics
        self.metrics = {
            "orders_per_minute": 0,
            "average_delivery_time": 30.0,  # minutes
            "on_time_delivery_rate": 85.0,  # percentage
            "partner_utilization": 75.0,  # percentage
            "customer_satisfaction": 4.2,  # rating
            "total_revenue": 0.0,
            "active_delivery_partners": 0,
            "peak_demand_areas": [],
            "restaurant_performance": {},
            "delivery_efficiency": 0.0,
            "last_updated": datetime.now()
        }
        
        # Mumbai delivery zones
        self.delivery_zones = {
            "Bandra": Location(19.0596, 72.8295, "Bandra West, Mumbai"),
            "Andheri": Location(19.1136, 72.8697, "Andheri East, Mumbai"),
            "Powai": Location(19.1176, 72.9060, "Powai, Mumbai"),
            "Lower Parel": Location(19.0133, 72.8302, "Lower Parel, Mumbai"),
            "Worli": Location(19.0176, 72.8182, "Worli, Mumbai"),
            "Malad": Location(19.1864, 72.8493, "Malad West, Mumbai"),
            "Borivali": Location(19.2307, 72.8567, "Borivali West, Mumbai"),
            "Thane": Location(19.2183, 72.9781, "Thane West, Mumbai"),
        }
        
        # Initialize restaurants and partners
        self._initialize_restaurants()
        self._initialize_delivery_partners()
    
    def _initialize_restaurants(self):
        """Initialize restaurant data"""
        restaurant_data = [
            {"name": "Domino's Pizza", "cuisine": "Pizza", "rating": 4.2, "prep_time": 20},
            {"name": "KFC", "cuisine": "Fast Food", "rating": 4.0, "prep_time": 15},
            {"name": "McDonald's", "cuisine": "Burgers", "rating": 3.8, "prep_time": 12},
            {"name": "Biryani Blues", "cuisine": "Indian", "rating": 4.5, "prep_time": 30},
            {"name": "Wow! Momo", "cuisine": "Chinese", "rating": 4.1, "prep_time": 18},
            {"name": "Subway", "cuisine": "Healthy", "rating": 4.3, "prep_time": 10},
            {"name": "Pizza Hut", "cuisine": "Pizza", "rating": 3.9, "prep_time": 25},
            {"name": "Burger King", "cuisine": "Burgers", "rating": 4.0, "prep_time": 15},
            {"name": "Haldiram's", "cuisine": "Indian", "rating": 4.4, "prep_time": 20},
            {"name": "Chinese Wok", "cuisine": "Chinese", "rating": 4.2, "prep_time": 22},
        ]
        
        for i, rest_data in enumerate(restaurant_data):
            zone_name = random.choice(list(self.delivery_zones.keys()))
            location = self.delivery_zones[zone_name]
            
            restaurant = Restaurant(
                restaurant_id=f"rest_{i+1:03d}",
                name=rest_data["name"],
                location=location,
                cuisine_type=rest_data["cuisine"],
                rating=rest_data["rating"],
                avg_prep_time=rest_data["prep_time"],
                is_busy=random.choice([True, False]),
                current_orders=random.randint(0, 15)
            )
            
            self.restaurants[restaurant.restaurant_id] = restaurant
    
    def _initialize_delivery_partners(self):
        """Initialize delivery partner data"""
        partner_names = [
            "Rajesh Kumar", "Amit Singh", "Deepak Sharma", "Vikash Yadav",
            "Santosh Patil", "Rahul Gupta", "Manoj Tiwari", "Suresh Jain",
            "Arjun Patel", "Krishna Murthy", "Sanjay Das", "Rohit Verma",
            "Naveen Kumar", "Anil Pandey", "Vinod Mehta", "Subhash Rai"
        ]
        
        for i, name in enumerate(partner_names):
            zone_name = random.choice(list(self.delivery_zones.keys()))
            location = self.delivery_zones[zone_name]
            
            partner = DeliveryPartner(
                partner_id=f"partner_{i+1:03d}",
                name=name,
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                current_location=location,
                status=random.choice([DeliveryPartnerStatus.AVAILABLE, DeliveryPartnerStatus.BUSY]),
                rating=round(random.uniform(4.0, 4.9), 1),
                total_deliveries=random.randint(500, 5000),
                earnings_today=random.uniform(800, 2000),
                vehicle_type=random.choice(["bike", "cycle"])
            )
            
            self.delivery_partners[partner.partner_id] = partner
            self.partner_locations[partner.partner_id] = location
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate distance between two locations using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(loc1.lat), math.radians(loc1.lng)
        lat2, lon2 = math.radians(loc2.lat), math.radians(loc2.lng)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def generate_food_order(self) -> Order:
        """Generate realistic food order"""
        restaurant = random.choice(list(self.restaurants.values()))
        delivery_zone = random.choice(list(self.delivery_zones.keys()))
        delivery_location = self.delivery_zones[delivery_zone]
        
        # Generate order items based on cuisine
        items = self.generate_order_items(restaurant.cuisine_type)
        total_amount = sum(item["price"] * item["quantity"] for item in items)
        
        # Add delivery charges and taxes
        delivery_charge = 0 if total_amount > 300 else 30  # Free delivery above 300
        platform_fee = 5
        taxes = total_amount * 0.18  # 18% GST
        final_amount = total_amount + delivery_charge + platform_fee + taxes
        
        # Calculate distance and estimated delivery time
        distance = self.calculate_distance(restaurant.location, delivery_location)
        
        # Base delivery time + prep time + travel time
        prep_time = restaurant.avg_prep_time
        travel_time = max(10, distance * 3)  # 3 minutes per km minimum 10 minutes
        
        # Weather and traffic impact
        weather_conditions = ["Clear", "Rainy", "Heavy Traffic", "Normal"]
        weather = random.choice(weather_conditions)
        
        weather_multiplier = {
            "Clear": 1.0,
            "Rainy": 1.4,  # 40% more time in rain
            "Heavy Traffic": 1.3,  # 30% more time in traffic
            "Normal": 1.1
        }
        
        estimated_delivery_minutes = (prep_time + travel_time) * weather_multiplier[weather]
        estimated_delivery_time = datetime.now() + timedelta(minutes=estimated_delivery_minutes)
        
        return Order(
            order_id=f"ORD_{int(time.time())}_{random.randint(1000, 9999)}",
            customer_id=f"customer_{random.randint(1, 100000)}",
            restaurant=restaurant,
            delivery_location=delivery_location,
            items=items,
            total_amount=round(final_amount, 2),
            order_time=datetime.now(),
            estimated_delivery_time=estimated_delivery_time,
            actual_delivery_time=None,
            status=OrderStatus.PLACED,
            assigned_partner=None,
            distance_km=round(distance, 2),
            weather_condition=weather
        )
    
    def generate_order_items(self, cuisine_type: str) -> List[Dict]:
        """Generate order items based on cuisine type"""
        menu_items = {
            "Pizza": [
                {"name": "Margherita Pizza", "price": 299},
                {"name": "Pepperoni Pizza", "price": 399},
                {"name": "Chicken Pizza", "price": 459},
                {"name": "Garlic Bread", "price": 149},
                {"name": "Coke", "price": 60}
            ],
            "Fast Food": [
                {"name": "Chicken Bucket", "price": 599},
                {"name": "Zinger Burger", "price": 199},
                {"name": "French Fries", "price": 99},
                {"name": "Pepsi", "price": 65}
            ],
            "Indian": [
                {"name": "Chicken Biryani", "price": 329},
                {"name": "Paneer Butter Masala", "price": 249},
                {"name": "Dal Tadka", "price": 179},
                {"name": "Naan", "price": 49},
                {"name": "Lassi", "price": 89}
            ],
            "Chinese": [
                {"name": "Chicken Fried Rice", "price": 229},
                {"name": "Hakka Noodles", "price": 199},
                {"name": "Manchurian", "price": 179},
                {"name": "Spring Rolls", "price": 149}
            ],
            "Burgers": [
                {"name": "Whopper", "price": 219},
                {"name": "Chicken Burger", "price": 169},
                {"name": "Fries", "price": 99},
                {"name": "Milkshake", "price": 129}
            ],
            "Healthy": [
                {"name": "Veggie Sub", "price": 189},
                {"name": "Chicken Sub", "price": 229},
                {"name": "Salad Bowl", "price": 149},
                {"name": "Fresh Juice", "price": 99}
            ]
        }
        
        available_items = menu_items.get(cuisine_type, menu_items["Indian"])
        num_items = random.randint(1, 4)  # 1-4 items per order
        
        selected_items = random.sample(available_items, min(num_items, len(available_items)))
        
        return [
            {
                **item,
                "quantity": random.randint(1, 2)
            }
            for item in selected_items
        ]
    
    def find_best_delivery_partner(self, order: Order) -> Optional[DeliveryPartner]:
        """Find the best available delivery partner for an order"""
        available_partners = [
            p for p in self.delivery_partners.values() 
            if p.status == DeliveryPartnerStatus.AVAILABLE
        ]
        
        if not available_partners:
            return None
        
        # Calculate score based on distance, rating, and vehicle type
        partner_scores = []
        
        for partner in available_partners:
            distance = self.calculate_distance(
                self.partner_locations[partner.partner_id],
                order.restaurant.location
            )
            
            # Scoring factors
            distance_score = max(0, 10 - distance)  # Closer is better
            rating_score = partner.rating * 2  # Rating weight
            vehicle_score = 2 if partner.vehicle_type == "bike" else 1  # Bikes are faster
            
            total_score = distance_score + rating_score + vehicle_score
            partner_scores.append((partner, total_score, distance))
        
        # Sort by score (higher is better)
        partner_scores.sort(key=lambda x: x[1], reverse=True)
        
        return partner_scores[0][0] if partner_scores else None
    
    async def process_order_lifecycle(self, order: Order):
        """Process complete order lifecycle"""
        self.active_orders[order.order_id] = order
        
        # Stage 1: Restaurant accepts order
        await asyncio.sleep(random.uniform(1, 3))  # 1-3 seconds acceptance time
        if random.random() < 0.95:  # 95% acceptance rate
            order.status = OrderStatus.ACCEPTED
            order.restaurant.current_orders += 1
            logger.info(f"✅ Order Accepted: {order.order_id} at {order.restaurant.name}")
        else:
            order.status = OrderStatus.CANCELLED
            self.cancelled_orders.append(order)
            del self.active_orders[order.order_id]
            return
        
        # Stage 2: Find delivery partner
        partner = self.find_best_delivery_partner(order)
        if partner:
            order.assigned_partner = partner
            partner.status = DeliveryPartnerStatus.BUSY
            logger.info(f"🏍️ Partner Assigned: {partner.name} for {order.order_id}")
        else:
            # No partner available - order might be delayed
            logger.warning(f"⏳ No partner available for {order.order_id}")
            await asyncio.sleep(5)  # Wait 5 seconds and try again
            partner = self.find_best_delivery_partner(order)
            if partner:
                order.assigned_partner = partner
                partner.status = DeliveryPartnerStatus.BUSY
            else:
                # Cancel order if no partner found after waiting
                order.status = OrderStatus.CANCELLED
                self.cancelled_orders.append(order)
                del self.active_orders[order.order_id]
                return
        
        # Stage 3: Food preparation
        order.status = OrderStatus.PREPARING
        prep_time = order.restaurant.avg_prep_time + random.randint(-5, 10)  # Some variation
        await asyncio.sleep(prep_time * 0.1)  # Scaled down for demo
        
        order.status = OrderStatus.READY
        logger.info(f"🍽️ Food Ready: {order.order_id}")
        
        # Stage 4: Partner picks up
        pickup_time = random.uniform(2, 8)  # 2-8 minutes to reach restaurant
        await asyncio.sleep(pickup_time * 0.1)
        
        order.status = OrderStatus.PICKED
        logger.info(f"📦 Order Picked: {order.order_id} by {partner.name}")
        
        # Stage 5: Out for delivery
        order.status = OrderStatus.OUT_FOR_DELIVERY
        
        # Delivery time calculation with real-world factors
        base_delivery_time = order.distance_km * 3  # 3 minutes per km
        
        # Weather impact
        weather_impact = {
            "Clear": 1.0,
            "Rainy": 1.5,
            "Heavy Traffic": 1.3,
            "Normal": 1.1
        }
        
        delivery_time = base_delivery_time * weather_impact.get(order.weather_condition, 1.0)
        
        # Partner efficiency (experienced partners are faster)
        experience_factor = 0.9 if partner.total_deliveries > 1000 else 1.0
        delivery_time *= experience_factor
        
        await asyncio.sleep(delivery_time * 0.1)
        
        # Stage 6: Delivered
        order.status = OrderStatus.DELIVERED
        order.actual_delivery_time = datetime.now()
        
        # Update partner status and earnings
        partner.status = DeliveryPartnerStatus.AVAILABLE
        delivery_fee = 50 + (order.distance_km * 8)  # Base + per km
        partner.earnings_today += delivery_fee
        partner.total_deliveries += 1
        
        # Move to completed orders
        self.completed_orders.append(order)
        del self.active_orders[order.order_id]
        order.restaurant.current_orders -= 1
        
        # Update metrics
        self.metrics["total_revenue"] += order.total_amount
        
        # Calculate delivery time performance
        actual_time = (order.actual_delivery_time - order.order_time).total_seconds() / 60
        estimated_time = (order.estimated_delivery_time - order.order_time).total_seconds() / 60
        
        on_time = actual_time <= estimated_time * 1.1  # 10% tolerance
        
        logger.info(f"🎯 Delivered: {order.order_id} in {actual_time:.1f} mins (Est: {estimated_time:.1f}) {'✅' if on_time else '❌'}")
    
    def calculate_real_time_metrics(self):
        """Calculate real-time performance metrics"""
        if not self.completed_orders:
            return
        
        # Recent deliveries (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_deliveries = [
            o for o in self.completed_orders 
            if o.actual_delivery_time and o.actual_delivery_time > recent_cutoff
        ]
        
        if recent_deliveries:
            # Average delivery time
            delivery_times = []
            on_time_count = 0
            
            for order in recent_deliveries:
                actual_minutes = (order.actual_delivery_time - order.order_time).total_seconds() / 60
                estimated_minutes = (order.estimated_delivery_time - order.order_time).total_seconds() / 60
                
                delivery_times.append(actual_minutes)
                
                if actual_minutes <= estimated_minutes * 1.1:  # 10% tolerance
                    on_time_count += 1
            
            self.metrics["average_delivery_time"] = sum(delivery_times) / len(delivery_times)
            self.metrics["on_time_delivery_rate"] = (on_time_count / len(recent_deliveries)) * 100
        
        # Orders per minute (last 5 minutes)
        recent_5min = datetime.now() - timedelta(minutes=5)
        recent_orders = [
            o for o in (list(self.active_orders.values()) + self.completed_orders)
            if o.order_time > recent_5min
        ]
        self.metrics["orders_per_minute"] = len(recent_orders) / 5
        
        # Partner utilization
        busy_partners = sum(1 for p in self.delivery_partners.values() if p.status == DeliveryPartnerStatus.BUSY)
        total_partners = len(self.delivery_partners)
        self.metrics["partner_utilization"] = (busy_partners / total_partners) * 100
        
        # Active delivery partners
        self.metrics["active_delivery_partners"] = sum(
            1 for p in self.delivery_partners.values() 
            if p.status != DeliveryPartnerStatus.OFFLINE
        )
        
        # Peak demand areas
        area_orders = defaultdict(int)
        for order in recent_orders:
            area_orders[order.delivery_location.address.split(',')[0]] += 1
        
        sorted_areas = sorted(area_orders.items(), key=lambda x: x[1], reverse=True)
        self.metrics["peak_demand_areas"] = sorted_areas[:5]
        
        # Restaurant performance
        restaurant_performance = defaultdict(lambda: {"orders": 0, "avg_prep_time": 0, "rating": 0})
        
        for order in recent_deliveries:
            rest_id = order.restaurant.restaurant_id
            restaurant_performance[rest_id]["orders"] += 1
            
            # Calculate actual prep time (if we had the data)
            restaurant_performance[rest_id]["avg_prep_time"] = order.restaurant.avg_prep_time
            restaurant_performance[rest_id]["rating"] = order.restaurant.rating
        
        self.metrics["restaurant_performance"] = dict(restaurant_performance)
        
        # Overall delivery efficiency
        if recent_deliveries:
            efficiency_scores = []
            for order in recent_deliveries:
                estimated_mins = (order.estimated_delivery_time - order.order_time).total_seconds() / 60
                actual_mins = (order.actual_delivery_time - order.order_time).total_seconds() / 60
                efficiency = min(100, (estimated_mins / actual_mins) * 100)  # Cap at 100%
                efficiency_scores.append(efficiency)
            
            self.metrics["delivery_efficiency"] = sum(efficiency_scores) / len(efficiency_scores)
        
        self.metrics["last_updated"] = datetime.now()
    
    def print_delivery_dashboard(self):
        """Print real-time delivery dashboard"""
        print(f"\n{'='*70}")
        print(f"🛵 SWIGGY REAL-TIME DELIVERY ANALYTICS 🛵")
        print(f"{'='*70}")
        print(f"Orders per Minute: {self.metrics['orders_per_minute']:.1f}")
        print(f"Average Delivery Time: {self.metrics['average_delivery_time']:.1f} minutes")
        print(f"On-Time Delivery Rate: {self.metrics['on_time_delivery_rate']:.1f}%")
        print(f"Partner Utilization: {self.metrics['partner_utilization']:.1f}%")
        print(f"Delivery Efficiency: {self.metrics['delivery_efficiency']:.1f}%")
        print(f"Active Partners: {self.metrics['active_delivery_partners']}")
        print(f"Total Revenue: ₹{self.metrics['total_revenue']:,.2f}")
        print(f"Active Orders: {len(self.active_orders)}")
        print(f"Completed Orders: {len(self.completed_orders)}")
        
        # Peak demand areas
        if self.metrics["peak_demand_areas"]:
            print(f"\n🔥 Peak Demand Areas:")
            for area, count in self.metrics["peak_demand_areas"]:
                print(f"  {area}: {count} orders")
        
        # Top performing restaurants
        if self.metrics["restaurant_performance"]:
            print(f"\n⭐ Restaurant Performance:")
            sorted_restaurants = sorted(
                self.metrics["restaurant_performance"].items(),
                key=lambda x: x[1]["orders"],
                reverse=True
            )[:5]
            
            for rest_id, perf in sorted_restaurants:
                restaurant = self.restaurants[rest_id]
                print(f"  {restaurant.name}: {perf['orders']} orders, {perf['rating']}⭐")
        
        print(f"\n🕐 Last Updated: {self.metrics['last_updated'].strftime('%H:%M:%S')}")
    
    def print_partner_dashboard(self):
        """Print delivery partner performance dashboard"""
        print(f"\n{'='*50}")
        print(f"👨‍💼 DELIVERY PARTNER DASHBOARD")
        print(f"{'='*50}")
        
        # Top performing partners
        top_partners = sorted(
            self.delivery_partners.values(),
            key=lambda p: p.earnings_today,
            reverse=True
        )[:10]
        
        for i, partner in enumerate(top_partners, 1):
            status_emoji = "🟢" if partner.status == DeliveryPartnerStatus.AVAILABLE else "🔴"
            vehicle_emoji = "🏍️" if partner.vehicle_type == "bike" else "🚲"
            
            print(f"{i:2d}. {partner.name} {status_emoji} {vehicle_emoji}")
            print(f"    Earnings: ₹{partner.earnings_today:.0f} | Rating: {partner.rating}⭐ | Deliveries: {partner.total_deliveries}")
    
    async def simulate_lunch_rush(self, duration_minutes: int = 10):
        """
        Simulate lunch rush hour (12 PM - 2 PM)
        Peak ordering time में maximum load testing
        """
        logger.info(f"🍽️ Starting lunch rush simulation for {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Lunch rush patterns
        rush_patterns = [
            (0.0, 0.2, 150, "Early Lunch - Orders Building Up"),
            (0.2, 0.6, 300, "Peak Lunch Rush - Maximum Orders"),  
            (0.6, 0.8, 200, "Late Lunch - Orders Tapering"),
            (0.8, 1.0, 80, "Post Lunch - Normal Rate")
        ]
        
        current_pattern_index = 0
        
        try:
            while time.time() < end_time:
                current_progress = (time.time() - start_time) / (duration_minutes * 60)
                
                # Update rush pattern
                if current_pattern_index < len(rush_patterns):
                    pattern_start, pattern_end, orders_per_hour, pattern_name = rush_patterns[current_pattern_index]
                    
                    if current_progress >= pattern_end and current_pattern_index < len(rush_patterns) - 1:
                        current_pattern_index += 1
                        logger.info(f"📊 Rush Pattern: {pattern_name}")
                        orders_per_hour = rush_patterns[current_pattern_index][2]
                    elif pattern_start <= current_progress <= pattern_end:
                        orders_per_hour = rush_patterns[current_pattern_index][2]
                
                # Generate orders
                orders_this_minute = random.poisson(orders_per_hour / 60)
                
                for _ in range(orders_this_minute):
                    order = self.generate_food_order()
                    # Process order in background
                    asyncio.create_task(self.process_order_lifecycle(order))
                
                # Calculate metrics every cycle
                self.calculate_real_time_metrics()
                
                # Print dashboard every 1 minute
                if int(time.time()) % 60 == 0:
                    self.print_delivery_dashboard()
                    self.print_partner_dashboard()
                
                await asyncio.sleep(5)  # 5 second processing cycle
                
        except KeyboardInterrupt:
            logger.info("Lunch rush simulation stopped by user")
        
        logger.info("🍽️ Lunch rush simulation completed!")
        
        # Final dashboard
        self.print_delivery_dashboard()

async def main():
    """Main demo function"""
    print("🚀 Starting Swiggy Real-time Delivery Analytics Demo")
    
    analytics = SwiggyDeliveryAnalytics()
    
    try:
        # Run lunch rush simulation
        await analytics.simulate_lunch_rush(duration_minutes=5)
        
        # Final summary
        total_orders = len(analytics.completed_orders) + len(analytics.active_orders) + len(analytics.cancelled_orders)
        success_rate = (len(analytics.completed_orders) / max(1, total_orders)) * 100
        
        print(f"\n🏁 DELIVERY SUMMARY")
        print(f"Total Orders: {total_orders}")
        print(f"Completed: {len(analytics.completed_orders)}")
        print(f"Active: {len(analytics.active_orders)}")
        print(f"Cancelled: {len(analytics.cancelled_orders)}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Revenue: ₹{analytics.metrics['total_revenue']:,.2f}")
        
        # Partner earnings summary
        total_earnings = sum(p.earnings_today for p in analytics.delivery_partners.values())
        print(f"Total Partner Earnings: ₹{total_earnings:,.2f}")
        
    except Exception as e:
        logger.error(f"Error in delivery simulation: {e}")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())