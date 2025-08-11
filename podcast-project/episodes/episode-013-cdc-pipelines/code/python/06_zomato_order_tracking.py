#!/usr/bin/env python3
"""
Episode 13: CDC & Real-Time Data Pipelines
Example 6: Zomato Order Tracking Pipeline

यह example Zomato style real-time order tracking implement करता है।
Mumbai से Delhi तक food delivery की complete journey track करो।

Author: Distributed Systems Podcast Team
Context: Food delivery order lifecycle - placement से delivery तक
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import uuid
from dataclasses import dataclass, asdict, field
from decimal import Decimal
import redis.asyncio as redis
from kafka import KafkaProducer, KafkaConsumer
import websockets
from enum import Enum
import random
import geopy.distance
from geopy import Point
import threading
import time

# Hindi logging setup  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(thread)d]',
    handlers=[
        logging.FileHandler('zomato_tracking.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    """Zomato order status lifecycle"""
    PLACED = "PLACED"
    RESTAURANT_ACCEPTED = "RESTAURANT_ACCEPTED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    PICKED_UP = "PICKED_UP"
    ON_THE_WAY = "ON_THE_WAY"
    NEARBY = "NEARBY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class DeliveryPartnerStatus(Enum):
    """Delivery partner status"""
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    PICKING_UP = "PICKING_UP"
    DELIVERING = "DELIVERING"
    OFFLINE = "OFFLINE"

@dataclass
class Location:
    """GPS coordinates with accuracy"""
    latitude: float
    longitude: float
    accuracy: float = 10.0  # meters
    timestamp: datetime = field(default_factory=datetime.now)
    
    def distance_to(self, other_location: 'Location') -> float:
        """Distance calculate करो meters में"""
        point1 = Point(latitude=self.latitude, longitude=self.longitude)
        point2 = Point(latitude=other_location.latitude, longitude=other_location.longitude)
        return geopy.distance.distance(point1, point2).meters

@dataclass
class FoodItem:
    """Individual food item"""
    item_id: str
    name: str
    quantity: int
    price: Decimal
    customizations: List[str] = field(default_factory=list)

@dataclass
class Restaurant:
    """Restaurant details for tracking"""
    restaurant_id: str
    name: str
    location: Location
    phone: str
    avg_prep_time: int  # minutes
    is_cloud_kitchen: bool = False

@dataclass
class DeliveryPartner:
    """Delivery partner details"""
    partner_id: str
    name: str
    phone: str
    vehicle_type: str  # BIKE, SCOOTER, BICYCLE
    current_location: Location
    status: DeliveryPartnerStatus
    rating: float = 4.5
    total_deliveries: int = 0

@dataclass
class ZomatoOrder:
    """Complete Zomato order with tracking info"""
    order_id: str
    user_id: str
    restaurant: Restaurant
    delivery_partner: Optional[DeliveryPartner]
    items: List[FoodItem]
    delivery_address: Dict[str, Any]
    delivery_location: Location
    
    # Order details
    subtotal: Decimal
    taxes: Decimal
    delivery_charges: Decimal
    total_amount: Decimal
    
    # Status and timing
    status: OrderStatus
    placed_at: datetime
    estimated_delivery_time: datetime
    actual_delivery_time: Optional[datetime] = None
    
    # Tracking data
    status_updates: List[Dict[str, Any]] = field(default_factory=list)
    location_updates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Payment
    payment_method: str = "UPI"
    payment_status: str = "PAID"

class ZomatoOrderTracker:
    """
    Zomato order tracking system - Mumbai traffic में real-time tracking
    """
    
    def __init__(self, kafka_servers: List[str], redis_url: str):
        self.kafka_servers = kafka_servers
        self.redis_url = redis_url
        
        # Components
        self.kafka_producer = None
        self.redis_client = None
        self.websocket_server = None
        
        # Active tracking
        self.active_orders: Dict[str, ZomatoOrder] = {}
        self.active_partners: Dict[str, DeliveryPartner] = {}
        self.websocket_clients: Dict[str, Any] = {}  # order_id -> websocket connection
        
        # Processing
        self.running = False
        self.tracking_threads = []
        
        # Mumbai area restaurants and locations
        self.mumbai_restaurants = [
            {
                "name": "Mumbai Tiffin Service",
                "location": Location(19.0760, 72.8777),
                "prep_time": 25,
                "cloud_kitchen": False
            },
            {
                "name": "Vada Pav Junction",
                "location": Location(19.0596, 72.8295),
                "prep_time": 15,
                "cloud_kitchen": False
            },
            {
                "name": "Cloud Kitchen Express",
                "location": Location(19.1197, 72.9073),
                "prep_time": 20,
                "cloud_kitchen": True
            },
            {
                "name": "South Indian Delights",
                "location": Location(19.0330, 72.8697),
                "prep_time": 30,
                "cloud_kitchen": False
            }
        ]
        
        # Popular Mumbai food items
        self.popular_items = [
            {"name": "Butter Chicken", "price": 320},
            {"name": "Vada Pav", "price": 35},
            {"name": "Pav Bhaji", "price": 150},
            {"name": "Masala Dosa", "price": 120},
            {"name": "Biryani", "price": 250},
            {"name": "Chole Bhature", "price": 180},
            {"name": "Fish Curry Rice", "price": 280}
        ]
        
        # Kafka topics for different types of events
        self.topics = {
            'order_placed': 'zomato.orders.placed',
            'order_updates': 'zomato.orders.updates', 
            'location_tracking': 'zomato.tracking.locations',
            'delivery_events': 'zomato.delivery.events',
            'customer_notifications': 'zomato.notifications.customer'
        }
    
    async def initialize(self):
        """System initialize करो"""
        logger.info("🍕 Initializing Zomato Order Tracking System")
        
        try:
            # Kafka producer
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8'),
                compression_type='snappy'
            )
            
            # Redis client
            self.redis_client = await redis.from_url(self.redis_url)
            
            logger.info("✅ Zomato tracking system initialized")
            
        except Exception as e:
            logger.error(f"💥 Initialization failed: {str(e)}")
            raise
    
    def generate_sample_order(self) -> ZomatoOrder:
        """
        Sample Zomato order generate करو - Mumbai context
        """
        # Random restaurant
        restaurant_data = random.choice(self.mumbai_restaurants)
        restaurant = Restaurant(
            restaurant_id=f"REST{uuid.uuid4().hex[:8].upper()}",
            name=restaurant_data["name"],
            location=restaurant_data["location"],
            phone=f"+91{random.randint(7000000000, 9999999999)}",
            avg_prep_time=restaurant_data["prep_time"],
            is_cloud_kitchen=restaurant_data["cloud_kitchen"]
        )
        
        # Random items
        num_items = random.randint(1, 4)
        items = []
        subtotal = Decimal('0')
        
        for i in range(num_items):
            item_data = random.choice(self.popular_items)
            quantity = random.randint(1, 3)
            
            item = FoodItem(
                item_id=f"ITEM{i+1:03d}",
                name=item_data["name"],
                quantity=quantity,
                price=Decimal(str(item_data["price"])),
                customizations=["Extra Spicy", "Less Oil"] if random.random() < 0.3 else []
            )
            items.append(item)
            subtotal += item.price * quantity
        
        # Calculate charges
        taxes = subtotal * Decimal('0.18')  # 18% GST
        delivery_charges = Decimal('30') if subtotal < 300 else Decimal('0')
        total_amount = subtotal + taxes + delivery_charges
        
        # Delivery location (within 5km of restaurant)
        delivery_location = Location(
            latitude=restaurant.location.latitude + random.uniform(-0.05, 0.05),
            longitude=restaurant.location.longitude + random.uniform(-0.05, 0.05)
        )
        
        # Create order
        order = ZomatoOrder(
            order_id=f"ZOM{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}",
            user_id=f"USER{random.randint(100000, 999999)}",
            restaurant=restaurant,
            delivery_partner=None,
            items=items,
            delivery_address={
                "line1": f"Flat {random.randint(101, 999)}",
                "line2": f"Building {random.randint(1, 100)}",
                "area": "Andheri East",
                "city": "Mumbai",
                "pincode": "400069"
            },
            delivery_location=delivery_location,
            subtotal=subtotal,
            taxes=taxes,
            delivery_charges=delivery_charges,
            total_amount=total_amount,
            status=OrderStatus.PLACED,
            placed_at=datetime.now(),
            estimated_delivery_time=datetime.now() + timedelta(minutes=restaurant.avg_prep_time + 25)
        )
        
        return order
    
    async def place_order(self, order: ZomatoOrder):
        """
        Order place करो और tracking start करो
        """
        logger.info(f"📱 Placing order: {order.order_id}")
        
        try:
            # Add to active orders
            self.active_orders[order.order_id] = order
            
            # Add initial status update
            order.status_updates.append({
                'status': OrderStatus.PLACED.value,
                'timestamp': datetime.now().isoformat(),
                'message': 'Order placed successfully'
            })
            
            # Send to Kafka
            order_data = self.serialize_order(order)
            self.kafka_producer.send(
                topic=self.topics['order_placed'],
                key=order.order_id,
                value=order_data
            )
            
            # Cache in Redis for fast access
            await self.redis_client.setex(
                f"order:{order.order_id}",
                3600,  # 1 hour TTL
                json.dumps(order_data, default=str)
            )
            
            # Start order lifecycle
            asyncio.create_task(self.simulate_order_lifecycle(order))
            
            logger.info(f"✅ Order placed successfully: {order.order_id}")
            
        except Exception as e:
            logger.error(f"💥 Order placement failed: {str(e)}")
    
    async def simulate_order_lifecycle(self, order: ZomatoOrder):
        """
        Complete order lifecycle simulate करो - realistic timing के साथ
        """
        try:
            # Restaurant acceptance (2-5 minutes)
            await asyncio.sleep(random.randint(2, 5) * 60)
            await self.update_order_status(order, OrderStatus.RESTAURANT_ACCEPTED)
            
            # Assign delivery partner
            await self.assign_delivery_partner(order)
            
            # Food preparation (restaurant's avg time +/- 5 minutes)
            prep_time = order.restaurant.avg_prep_time + random.randint(-5, 5)
            await asyncio.sleep(prep_time * 60)
            await self.update_order_status(order, OrderStatus.PREPARING)
            
            # Ready for pickup
            await asyncio.sleep(random.randint(3, 8) * 60)
            await self.update_order_status(order, OrderStatus.READY_FOR_PICKUP)
            
            # Pickup simulation
            await asyncio.sleep(random.randint(2, 5) * 60)
            await self.update_order_status(order, OrderStatus.PICKED_UP)
            
            # Start delivery tracking
            await self.simulate_delivery_journey(order)
            
        except Exception as e:
            logger.error(f"💥 Order lifecycle error: {str(e)}")
    
    async def assign_delivery_partner(self, order: ZomatoOrder):
        """
        Delivery partner assign करो - location based
        """
        try:
            # Create delivery partner near restaurant
            partner = DeliveryPartner(
                partner_id=f"DEL{uuid.uuid4().hex[:8].upper()}",
                name=f"Delivery Hero {random.randint(1, 1000)}",
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                vehicle_type=random.choice(["BIKE", "SCOOTER"]),
                current_location=Location(
                    latitude=order.restaurant.location.latitude + random.uniform(-0.01, 0.01),
                    longitude=order.restaurant.location.longitude + random.uniform(-0.01, 0.01)
                ),
                status=DeliveryPartnerStatus.AVAILABLE,
                rating=round(random.uniform(4.0, 5.0), 1),
                total_deliveries=random.randint(100, 5000)
            )
            
            # Assign to order
            order.delivery_partner = partner
            partner.status = DeliveryPartnerStatus.ASSIGNED
            
            # Store partner info
            self.active_partners[partner.partner_id] = partner
            
            # Send assignment event
            assignment_event = {
                'order_id': order.order_id,
                'partner_id': partner.partner_id,
                'partner_name': partner.name,
                'partner_phone': partner.phone,
                'vehicle_type': partner.vehicle_type,
                'partner_rating': partner.rating,
                'timestamp': datetime.now().isoformat()
            }
            
            self.kafka_producer.send(
                topic=self.topics['delivery_events'],
                key=order.order_id,
                value=assignment_event
            )
            
            logger.info(f"👨‍🍳 Delivery partner assigned: {partner.name} for order {order.order_id}")
            
        except Exception as e:
            logger.error(f"💥 Partner assignment failed: {str(e)}")
    
    async def simulate_delivery_journey(self, order: ZomatoOrder):
        """
        Delivery journey simulate करो - Mumbai traffic के साथ realistic movement
        """
        if not order.delivery_partner:
            logger.warning(f"⚠️ No delivery partner for order: {order.order_id}")
            return
        
        try:
            partner = order.delivery_partner
            restaurant_location = order.restaurant.location
            delivery_location = order.delivery_location
            
            # Calculate total distance
            total_distance = restaurant_location.distance_to(delivery_location)
            
            # Mumbai traffic factor (slower during peak hours)
            current_hour = datetime.now().hour
            traffic_factor = 1.0
            if 8 <= current_hour <= 10 or 17 <= current_hour <= 20:  # Peak hours
                traffic_factor = 1.8
            elif 10 <= current_hour <= 17:  # Day time
                traffic_factor = 1.3
            
            # Estimate delivery time based on distance and traffic
            estimated_speed = 20  # km/h average in Mumbai
            travel_time_minutes = (total_distance / 1000) * (60 / estimated_speed) * traffic_factor
            
            logger.info(f"🛵 Starting delivery journey: {total_distance:.0f}m, estimated {travel_time_minutes:.1f} minutes")
            
            # Update status to on the way
            await self.update_order_status(order, OrderStatus.ON_THE_WAY)
            
            # Simulate movement with location updates
            num_updates = max(5, int(travel_time_minutes / 3))  # Update every 3 minutes
            
            for i in range(num_updates):
                # Calculate intermediate location
                progress = (i + 1) / num_updates
                
                lat_diff = delivery_location.latitude - restaurant_location.latitude
                lng_diff = delivery_location.longitude - restaurant_location.longitude
                
                current_lat = restaurant_location.latitude + (lat_diff * progress)
                current_lng = restaurant_location.longitude + (lng_diff * progress)
                
                # Add some randomness for realistic movement
                current_lat += random.uniform(-0.002, 0.002)
                current_lng += random.uniform(-0.002, 0.002)
                
                partner.current_location = Location(current_lat, current_lng)
                
                # Send location update
                await self.send_location_update(order, partner.current_location)
                
                # Check if nearby (last 20% of journey)
                if progress > 0.8 and order.status != OrderStatus.NEARBY:
                    await self.update_order_status(order, OrderStatus.NEARBY)
                
                # Wait for next update
                await asyncio.sleep((travel_time_minutes * 60) / num_updates)
            
            # Final delivery
            await asyncio.sleep(random.randint(2, 5) * 60)  # Final delivery time
            order.actual_delivery_time = datetime.now()
            await self.update_order_status(order, OrderStatus.DELIVERED)
            
            # Update partner status
            partner.status = DeliveryPartnerStatus.AVAILABLE
            partner.total_deliveries += 1
            
        except Exception as e:
            logger.error(f"💥 Delivery journey simulation failed: {str(e)}")
    
    async def update_order_status(self, order: ZomatoOrder, new_status: OrderStatus):
        """
        Order status update करो और notifications send करो
        """
        try:
            old_status = order.status
            order.status = new_status
            
            # Add status update
            status_update = {
                'status': new_status.value,
                'timestamp': datetime.now().isoformat(),
                'message': self.get_status_message(new_status)
            }
            order.status_updates.append(status_update)
            
            # Send to Kafka
            update_event = {
                'order_id': order.order_id,
                'user_id': order.user_id,
                'old_status': old_status.value,
                'new_status': new_status.value,
                'timestamp': datetime.now().isoformat(),
                'estimated_delivery_time': order.estimated_delivery_time.isoformat(),
                'actual_delivery_time': order.actual_delivery_time.isoformat() if order.actual_delivery_time else None
            }
            
            self.kafka_producer.send(
                topic=self.topics['order_updates'],
                key=order.order_id,
                value=update_event
            )
            
            # Send customer notification
            await self.send_customer_notification(order, new_status)
            
            # Update Redis cache
            await self.redis_client.setex(
                f"order_status:{order.order_id}",
                3600,
                json.dumps({
                    'status': new_status.value,
                    'timestamp': datetime.now().isoformat()
                })
            )
            
            # Send to connected websocket clients
            await self.broadcast_to_websocket_clients(order, update_event)
            
            logger.info(f"📊 Order status updated: {order.order_id} -> {new_status.value}")
            
        except Exception as e:
            logger.error(f"💥 Status update failed: {str(e)}")
    
    async def send_location_update(self, order: ZomatoOrder, location: Location):
        """
        Real-time location update send करो
        """
        try:
            location_event = {
                'order_id': order.order_id,
                'partner_id': order.delivery_partner.partner_id if order.delivery_partner else None,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'accuracy': location.accuracy,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to order tracking
            order.location_updates.append(location_event)
            
            # Send to Kafka
            self.kafka_producer.send(
                topic=self.topics['location_tracking'],
                key=order.order_id,
                value=location_event
            )
            
            # Update Redis for real-time queries
            await self.redis_client.setex(
                f"location:{order.order_id}",
                300,  # 5 minutes TTL
                json.dumps(location_event)
            )
            
            # Send to websocket clients
            await self.broadcast_to_websocket_clients(order, location_event)
            
            logger.debug(f"📍 Location updated for order: {order.order_id}")
            
        except Exception as e:
            logger.error(f"💥 Location update failed: {str(e)}")
    
    def get_status_message(self, status: OrderStatus) -> str:
        """Status के लिए user-friendly message"""
        messages = {
            OrderStatus.PLACED: "आपका ऑर्डर प्लेस हो गया है!",
            OrderStatus.RESTAURANT_ACCEPTED: "रेस्टोरेंट ने आपका ऑर्डर स्वीकार कर लिया है",
            OrderStatus.PREPARING: "आपका खाना बन रहा है 👨‍🍳",
            OrderStatus.READY_FOR_PICKUP: "आपका ऑर्डर पिकअप के लिए तैयार है",
            OrderStatus.PICKED_UP: "डिलीवरी पार्टनर ने आपका ऑर्डर पिकअप कर लिया है",
            OrderStatus.ON_THE_WAY: "आपका ऑर्डर आपके पास आ रहा है 🛵",
            OrderStatus.NEARBY: "डिलीवरी पार्टनर आपके नजदीक है! 📍",
            OrderStatus.DELIVERED: "आपका ऑर्डर डिलीवर हो गया है! Enjoy your meal! 🍽️",
            OrderStatus.CANCELLED: "आपका ऑर्डर कैंसल हो गया है"
        }
        return messages.get(status, "Order status updated")
    
    async def send_customer_notification(self, order: ZomatoOrder, status: OrderStatus):
        """Customer को notification send करो"""
        notification = {
            'user_id': order.user_id,
            'order_id': order.order_id,
            'type': 'ORDER_STATUS_UPDATE',
            'title': f"Order {order.order_id}",
            'message': self.get_status_message(status),
            'status': status.value,
            'timestamp': datetime.now().isoformat()
        }
        
        self.kafka_producer.send(
            topic=self.topics['customer_notifications'],
            key=order.user_id,
            value=notification
        )
        
        logger.info(f"📱 Notification sent to user {order.user_id}")
    
    async def broadcast_to_websocket_clients(self, order: ZomatoOrder, data: Dict[str, Any]):
        """Connected websocket clients को broadcast करो"""
        if order.order_id in self.websocket_clients:
            try:
                websocket = self.websocket_clients[order.order_id]
                await websocket.send(json.dumps(data, default=str))
            except Exception as e:
                logger.error(f"💥 Websocket broadcast error: {str(e)}")
                # Remove disconnected client
                del self.websocket_clients[order.order_id]
    
    def serialize_order(self, order: ZomatoOrder) -> Dict[str, Any]:
        """Order को JSON serializable format में convert करो"""
        return {
            'order_id': order.order_id,
            'user_id': order.user_id,
            'restaurant': asdict(order.restaurant),
            'delivery_partner': asdict(order.delivery_partner) if order.delivery_partner else None,
            'items': [asdict(item) for item in order.items],
            'delivery_address': order.delivery_address,
            'delivery_location': asdict(order.delivery_location),
            'subtotal': float(order.subtotal),
            'taxes': float(order.taxes),
            'delivery_charges': float(order.delivery_charges),
            'total_amount': float(order.total_amount),
            'status': order.status.value,
            'placed_at': order.placed_at.isoformat(),
            'estimated_delivery_time': order.estimated_delivery_time.isoformat(),
            'actual_delivery_time': order.actual_delivery_time.isoformat() if order.actual_delivery_time else None,
            'status_updates': order.status_updates,
            'location_updates': order.location_updates,
            'payment_method': order.payment_method,
            'payment_status': order.payment_status
        }
    
    async def start_websocket_server(self, port: int = 8765):
        """
        WebSocket server start करो - real-time updates के लिए
        """
        async def handle_websocket(websocket, path):
            try:
                # Extract order_id from path
                order_id = path.split('/')[-1] if path.startswith('/track/') else None
                
                if order_id and order_id in self.active_orders:
                    self.websocket_clients[order_id] = websocket
                    logger.info(f"📡 WebSocket client connected for order: {order_id}")
                    
                    # Send current order status
                    current_order = self.active_orders[order_id]
                    current_status = {
                        'type': 'CURRENT_STATUS',
                        'order_id': order_id,
                        'status': current_order.status.value,
                        'status_updates': current_order.status_updates,
                        'location_updates': current_order.location_updates[-5:]  # Last 5 locations
                    }
                    await websocket.send(json.dumps(current_status, default=str))
                    
                    # Keep connection alive
                    await websocket.wait_closed()
                else:
                    await websocket.close(code=4004, reason="Order not found")
                    
            except Exception as e:
                logger.error(f"💥 WebSocket error: {str(e)}")
            finally:
                if order_id in self.websocket_clients:
                    del self.websocket_clients[order_id]
        
        # Start WebSocket server
        logger.info(f"🔗 Starting WebSocket server on port {port}")
        self.websocket_server = await websockets.serve(handle_websocket, "localhost", port)
    
    async def start_order_generator(self, orders_per_minute: int = 10):
        """
        Continuous order generation - realistic Mumbai food delivery volume
        """
        logger.info(f"🏭 Starting order generator: {orders_per_minute} orders/minute")
        
        while self.running:
            try:
                # Generate new order
                order = self.generate_sample_order()
                await self.place_order(order)
                
                # Wait for next order
                await asyncio.sleep(60 / orders_per_minute)
                
            except Exception as e:
                logger.error(f"💥 Order generation error: {str(e)}")
                await asyncio.sleep(10)
    
    async def start(self, orders_per_minute: int = 5):
        """
        Complete tracking system start करो
        """
        logger.info("🚀 Starting Zomato Order Tracking System")
        
        try:
            # Initialize system
            await self.initialize()
            
            # Start WebSocket server
            await self.start_websocket_server()
            
            # Mark as running
            self.running = True
            
            # Start order generator
            asyncio.create_task(self.start_order_generator(orders_per_minute))
            
            logger.info("✅ Zomato Order Tracking System started successfully")
            
            # Keep running and show metrics
            while self.running:
                await asyncio.sleep(30)
                active_count = len(self.active_orders)
                partner_count = len(self.active_partners)
                websocket_count = len(self.websocket_clients)
                
                logger.info(f"📊 Active Orders: {active_count}, Partners: {partner_count}, WebSocket Connections: {websocket_count}")
                
        except Exception as e:
            logger.error(f"💥 System startup failed: {str(e)}")
            raise
    
    async def stop(self):
        """System को gracefully stop करो"""
        logger.info("🛑 Stopping Zomato Order Tracking System")
        
        self.running = False
        
        # Close WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        # Close connections
        if self.kafka_producer:
            self.kafka_producer.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("✅ Zomato Order Tracking System stopped")

async def main():
    """Main function - Zomato tracking demo"""
    logger.info("🇮🇳 Starting Zomato Order Tracking Demo")
    
    # Configuration
    kafka_servers = ['localhost:9092']
    redis_url = 'redis://localhost:6379'
    
    # Initialize tracking system
    zomato_tracker = ZomatoOrderTracker(kafka_servers, redis_url)
    
    try:
        # Start the system
        await zomato_tracker.start(orders_per_minute=3)  # 3 orders per minute for demo
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
        await zomato_tracker.stop()
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        await zomato_tracker.stop()

if __name__ == "__main__":
    asyncio.run(main())

"""
Production Implementation Guide:

1. Real-time Architecture:
   - WebSocket connections for live tracking
   - Redis for fast order status lookups  
   - Kafka for event streaming and processing
   - MongoDB/PostgreSQL for persistent storage

2. Location Tracking:
   - GPS accuracy handling
   - Map matching algorithms
   - ETA calculation with traffic data
   - Geofencing for pickup/delivery confirmation

3. Scalability Features:
   - Horizontal scaling of tracking services
   - Kafka partitioning by city/region
   - Redis clustering for cache distribution
   - CDN for static content delivery

4. Business Logic:
   - Dynamic ETA updates based on real-time conditions
   - Partner assignment algorithms (distance, rating, load)
   - Customer preference handling
   - Peak hour surge pricing integration

5. Integration Points:
   - Payment gateway webhooks
   - SMS/Push notification services
   - Restaurant POS systems
   - Customer support chat systems

6. Monitoring & Analytics:
   - Order completion rates by area
   - Average delivery times
   - Partner performance metrics
   - Customer satisfaction tracking
"""