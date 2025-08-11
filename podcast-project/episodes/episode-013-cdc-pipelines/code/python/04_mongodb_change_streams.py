#!/usr/bin/env python3
"""
Episode 13: CDC & Real-Time Data Pipelines
Example 4: MongoDB Change Streams Implementation

यह example MongoDB के Change Streams का use करके real-time CDC implement करता है।
Swiggy, Zomato जैसे food delivery platforms के लिए order tracking और inventory management।

Author: Distributed Systems Podcast Team
Context: Indian food delivery platforms - orders, restaurants, delivery tracking
"""

import asyncio
import motor.motor_asyncio
import pymongo
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, AsyncGenerator
import uuid
from dataclasses import dataclass, asdict
from decimal import Decimal
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import time
from bson import ObjectId
import redis
import asyncio
from kafka import KafkaProducer

# Hindi logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(thread)d]',
    handlers=[
        logging.FileHandler('mongodb_cdc.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FoodOrder:
    """Swiggy/Zomato style food order"""
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[Dict[str, Any]]
    total_amount: Decimal
    delivery_address: Dict[str, str]
    delivery_boy_id: Optional[str] = None
    status: str = "PLACED"  # PLACED, CONFIRMED, PREPARING, PICKED_UP, DELIVERED
    payment_method: str = "UPI"
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    rating: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass 
class Restaurant:
    """Restaurant information - Mumbai street food से fine dining तक"""
    restaurant_id: str
    name: str
    cuisine_type: List[str]
    city: str
    area: str
    coordinates: Dict[str, float]  # lat, lng
    rating: float
    delivery_time_avg: int  # minutes
    is_open: bool = True
    menu_items: List[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class DeliveryBoy:
    """Delivery partner tracking - Mumbai traffic में navigate करने वाले heroes"""
    delivery_boy_id: str
    name: str
    phone: str
    vehicle_type: str  # BIKE, BICYCLE, SCOOTER
    current_location: Dict[str, float]  # lat, lng
    is_available: bool = True
    current_orders: List[str] = None
    rating: float = 4.5
    total_deliveries: int = 0
    created_at: datetime = None
    updated_at: datetime = None

class SwiggyMongoDBChangeStreamsProcessor:
    """
    Swiggy style MongoDB Change Streams processor
    Mumbai की food delivery ecosystem के लिए real-time processing
    """
    
    def __init__(self, mongo_uri: str, database_name: str):
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.client = None
        self.database = None
        
        # Async client for change streams
        self.async_client = None
        self.async_database = None
        
        # Processing components
        self.change_streams = {}
        self.processors = []
        self.running = False
        
        # External integrations
        self.kafka_producer = None
        self.redis_client = None
        
        # Indian cities and popular dishes
        self.indian_cities = [
            {"name": "Mumbai", "state": "Maharashtra"},
            {"name": "Delhi", "state": "Delhi"},
            {"name": "Bangalore", "state": "Karnataka"},
            {"name": "Hyderabad", "state": "Telangana"},
            {"name": "Chennai", "state": "Tamil Nadu"},
            {"name": "Kolkata", "state": "West Bengal"},
            {"name": "Pune", "state": "Maharashtra"},
            {"name": "Ahmedabad", "state": "Gujarat"},
            {"name": "Jaipur", "state": "Rajasthan"},
            {"name": "Surat", "state": "Gujarat"}
        ]
        
        self.popular_dishes = [
            {"name": "Butter Chicken", "price": 320, "cuisine": "North Indian"},
            {"name": "Biryani", "price": 250, "cuisine": "Hyderabadi"},
            {"name": "Dosa", "price": 120, "cuisine": "South Indian"},
            {"name": "Vada Pav", "price": 35, "cuisine": "Mumbai Street"},
            {"name": "Chole Bhature", "price": 180, "cuisine": "Punjabi"},
            {"name": "Idli Sambar", "price": 100, "cuisine": "South Indian"},
            {"name": "Pav Bhaji", "price": 150, "cuisine": "Mumbai Street"},
            {"name": "Rajma Rice", "price": 200, "cuisine": "North Indian"},
            {"name": "Fish Curry", "price": 280, "cuisine": "Bengali"},
            {"name": "Thali", "price": 350, "cuisine": "Regional"}
        ]
    
    async def initialize(self):
        """
        MongoDB connections और collections initialize करो
        """
        logger.info("🥘 Initializing Swiggy MongoDB CDC System")
        
        try:
            # Sync client for setup operations
            self.client = MongoClient(self.mongo_uri)
            self.database = self.client[self.database_name]
            
            # Async client for change streams
            self.async_client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
            self.async_database = self.async_client[self.database_name]
            
            # Initialize Kafka producer
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
            
            # Initialize Redis client
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            
            logger.info("✅ MongoDB CDC System initialized successfully")
            
        except Exception as e:
            logger.error(f"💥 Initialization failed: {str(e)}")
            raise
    
    async def setup_collections_and_indexes(self):
        """
        Collections और indexes setup करो - performance के लिए जरूरी
        """
        logger.info("🏗️ Setting up MongoDB collections and indexes")
        
        try:
            # Orders collection indexes
            orders_collection = self.database['orders']
            orders_collection.create_index([("user_id", 1), ("created_at", -1)])
            orders_collection.create_index([("restaurant_id", 1), ("status", 1)])
            orders_collection.create_index([("delivery_boy_id", 1), ("status", 1)])
            orders_collection.create_index([("status", 1), ("created_at", -1)])
            orders_collection.create_index([("created_at", -1)])
            
            # Restaurants collection indexes
            restaurants_collection = self.database['restaurants']
            restaurants_collection.create_index([("city", 1), ("area", 1)])
            restaurants_collection.create_index([("coordinates", "2dsphere")])
            restaurants_collection.create_index([("cuisine_type", 1)])
            restaurants_collection.create_index([("rating", -1)])
            restaurants_collection.create_index([("is_open", 1)])
            
            # Delivery boys collection indexes
            delivery_boys_collection = self.database['delivery_boys']
            delivery_boys_collection.create_index([("current_location", "2dsphere")])
            delivery_boys_collection.create_index([("is_available", 1)])
            delivery_boys_collection.create_index([("rating", -1)])
            delivery_boys_collection.create_index([("current_orders", 1)])
            
            # Order tracking collection (for real-time updates)
            tracking_collection = self.database['order_tracking']
            tracking_collection.create_index([("order_id", 1), ("timestamp", -1)])
            tracking_collection.create_index([("delivery_boy_id", 1), ("timestamp", -1)])
            
            logger.info("✅ Collections and indexes created successfully")
            
        except Exception as e:
            logger.error(f"💥 Collection setup failed: {str(e)}")
            raise
    
    async def generate_sample_data(self):
        """
        Indian food delivery के लिए sample data generate करो
        """
        logger.info("📊 Generating sample food delivery data")
        
        try:
            # Generate restaurants
            restaurants = []
            for i in range(50):
                city = self.indian_cities[i % len(self.indian_cities)]
                
                restaurant = {
                    "_id": ObjectId(),
                    "restaurant_id": f"REST{str(uuid.uuid4())[:8].upper()}",
                    "name": f"Restaurant {i+1} - {city['name']} Special",
                    "cuisine_type": ["North Indian", "South Indian", "Chinese", "Continental"][i % 4],
                    "city": city["name"],
                    "state": city["state"],
                    "area": f"Area {(i % 10) + 1}",
                    "coordinates": {
                        "lat": 19.0760 + (i % 20) * 0.01,  # Mumbai base coordinates
                        "lng": 72.8777 + (i % 20) * 0.01
                    },
                    "rating": round(3.5 + (i % 15) * 0.1, 1),
                    "delivery_time_avg": 20 + (i % 40),
                    "is_open": i % 10 != 0,  # 90% restaurants open
                    "menu_items": [
                        {
                            "item_id": f"ITEM{j:03d}",
                            "name": dish["name"],
                            "price": dish["price"] + (i % 50),
                            "cuisine": dish["cuisine"],
                            "is_available": True
                        }
                        for j, dish in enumerate(self.popular_dishes[:5])
                    ],
                    "created_at": datetime.now() - timedelta(days=i % 30),
                    "updated_at": datetime.now()
                }
                restaurants.append(restaurant)
            
            await self.async_database.restaurants.insert_many(restaurants)
            logger.info(f"✅ Created {len(restaurants)} restaurants")
            
            # Generate delivery boys
            delivery_boys = []
            for i in range(100):
                delivery_boy = {
                    "_id": ObjectId(),
                    "delivery_boy_id": f"DB{str(uuid.uuid4())[:8].upper()}",
                    "name": f"Delivery Hero {i+1}",
                    "phone": f"+91{'9' if i % 2 == 0 else '8'}{i+1000000000:>9}",
                    "vehicle_type": ["BIKE", "SCOOTER", "BICYCLE"][i % 3],
                    "current_location": {
                        "lat": 19.0760 + (i % 50) * 0.01,
                        "lng": 72.8777 + (i % 50) * 0.01
                    },
                    "is_available": i % 5 != 0,  # 80% available
                    "current_orders": [] if i % 5 != 0 else [f"ORD{i:06d}"],
                    "rating": round(3.8 + (i % 12) * 0.1, 1),
                    "total_deliveries": i * 10 + (i % 100),
                    "created_at": datetime.now() - timedelta(days=i % 60),
                    "updated_at": datetime.now()
                }
                delivery_boys.append(delivery_boy)
            
            await self.async_database.delivery_boys.insert_many(delivery_boys)
            logger.info(f"✅ Created {len(delivery_boys)} delivery boys")
            
            # Generate orders
            orders = []
            for i in range(200):
                restaurant = restaurants[i % len(restaurants)]
                
                # Select random items from restaurant menu
                selected_items = []
                num_items = (i % 3) + 1  # 1-3 items per order
                
                for j in range(num_items):
                    menu_item = restaurant["menu_items"][j % len(restaurant["menu_items"])]
                    selected_items.append({
                        "item_id": menu_item["item_id"],
                        "name": menu_item["name"],
                        "price": menu_item["price"],
                        "quantity": (i % 3) + 1
                    })
                
                total_amount = sum(item["price"] * item["quantity"] for item in selected_items)
                total_amount += 30 + (i % 20)  # Delivery charges
                
                order = {
                    "_id": ObjectId(),
                    "order_id": f"ORD{datetime.now().strftime('%Y%m%d')}{i:06d}",
                    "user_id": f"USER{(i % 100) + 1:06d}",
                    "restaurant_id": restaurant["restaurant_id"],
                    "items": selected_items,
                    "total_amount": total_amount,
                    "delivery_address": {
                        "street": f"Street {(i % 20) + 1}",
                        "area": f"Area {(i % 15) + 1}",
                        "city": restaurant["city"],
                        "state": restaurant["state"],
                        "pincode": f"{400000 + (i % 100):06d}",
                        "coordinates": {
                            "lat": restaurant["coordinates"]["lat"] + (i % 10) * 0.001,
                            "lng": restaurant["coordinates"]["lng"] + (i % 10) * 0.001
                        }
                    },
                    "delivery_boy_id": delivery_boys[i % len(delivery_boys)]["delivery_boy_id"] if i % 3 != 0 else None,
                    "status": ["PLACED", "CONFIRMED", "PREPARING", "PICKED_UP", "DELIVERED"][i % 5],
                    "payment_method": ["UPI", "Card", "Cash", "Wallet"][i % 4],
                    "estimated_delivery_time": datetime.now() + timedelta(minutes=30 + (i % 30)),
                    "actual_delivery_time": datetime.now() + timedelta(minutes=25 + (i % 45)) if i % 5 == 4 else None,
                    "rating": (i % 5) + 1 if i % 5 == 4 else None,
                    "created_at": datetime.now() - timedelta(hours=i % 24),
                    "updated_at": datetime.now() - timedelta(minutes=i % 60)
                }
                orders.append(order)
            
            await self.async_database.orders.insert_many(orders)
            logger.info(f"✅ Created {len(orders)} orders")
            
            logger.info("✅ All sample data generated successfully")
            
        except Exception as e:
            logger.error(f"💥 Sample data generation failed: {str(e)}")
            raise
    
    async def start_change_streams(self):
        """
        Multiple collections के लिए change streams start करो
        """
        logger.info("📡 Starting MongoDB Change Streams")
        
        collections_to_watch = [
            "orders",
            "restaurants", 
            "delivery_boys",
            "order_tracking"
        ]
        
        # Start change stream for each collection
        for collection_name in collections_to_watch:
            asyncio.create_task(
                self.watch_collection_changes(collection_name)
            )
            logger.info(f"✅ Started change stream for {collection_name}")
        
        logger.info("🎯 All change streams started successfully")
    
    async def watch_collection_changes(self, collection_name: str):
        """
        Individual collection के changes watch करो
        """
        logger.info(f"👀 Watching changes for collection: {collection_name}")
        
        try:
            collection = self.async_database[collection_name]
            
            # Change stream options
            pipeline = [
                {
                    '$match': {
                        'operationType': {'$in': ['insert', 'update', 'delete', 'replace']}
                    }
                }
            ]
            
            async with collection.watch(pipeline=pipeline) as change_stream:
                async for change in change_stream:
                    await self.process_change_event(collection_name, change)
                    
        except Exception as e:
            logger.error(f"💥 Change stream error for {collection_name}: {str(e)}")
            
            # Retry after delay
            await asyncio.sleep(5)
            asyncio.create_task(self.watch_collection_changes(collection_name))
    
    async def process_change_event(self, collection_name: str, change: Dict[str, Any]):
        """
        Individual change event को process करो - Mumbai express train की speed में
        """
        try:
            operation_type = change.get('operationType')
            document_id = change.get('documentKey', {}).get('_id')
            
            logger.info(f"📝 Processing {operation_type} on {collection_name} - ID: {document_id}")
            
            # Collection-specific processing
            if collection_name == "orders":
                await self.handle_order_change(change)
            elif collection_name == "restaurants":
                await self.handle_restaurant_change(change)
            elif collection_name == "delivery_boys":
                await self.handle_delivery_boy_change(change)
            elif collection_name == "order_tracking":
                await self.handle_tracking_change(change)
            
            # Send to Kafka for downstream processing
            await self.send_to_kafka(collection_name, change)
            
            # Update Redis cache
            await self.update_redis_cache(collection_name, change)
            
        except Exception as e:
            logger.error(f"💥 Change processing error: {str(e)}")
    
    async def handle_order_change(self, change: Dict[str, Any]):
        """
        Order changes handle करो - real-time order tracking
        """
        operation_type = change.get('operationType')
        
        if operation_type == 'insert':
            # New order placed
            new_order = change.get('fullDocument', {})
            order_id = new_order.get('order_id')
            restaurant_id = new_order.get('restaurant_id')
            user_id = new_order.get('user_id')
            
            logger.info(f"🆕 New order placed: {order_id} by {user_id} at {restaurant_id}")
            
            # Real-time notifications
            await self.send_order_notification(new_order, "ORDER_PLACED")
            
            # Find and assign delivery boy
            await self.assign_delivery_boy(new_order)
            
            # Update restaurant metrics
            await self.update_restaurant_metrics(restaurant_id, "new_order")
            
        elif operation_type == 'update':
            # Order status updated
            updated_fields = change.get('updateDescription', {}).get('updatedFields', {})
            
            if 'status' in updated_fields:
                new_status = updated_fields['status']
                order_id = change.get('documentKey', {}).get('_id')
                
                logger.info(f"📦 Order status updated: {order_id} -> {new_status}")
                
                # Send status update notification
                await self.send_status_update_notification(order_id, new_status)
                
                # Update delivery tracking
                if new_status in ['PICKED_UP', 'DELIVERED']:
                    await self.update_delivery_tracking(order_id, new_status)
    
    async def handle_restaurant_change(self, change: Dict[str, Any]):
        """
        Restaurant changes handle करो - availability, menu updates
        """
        operation_type = change.get('operationType')
        
        if operation_type == 'update':
            updated_fields = change.get('updateDescription', {}).get('updatedFields', {})
            restaurant_id = change.get('documentKey', {}).get('_id')
            
            if 'is_open' in updated_fields:
                is_open = updated_fields['is_open']
                logger.info(f"🏪 Restaurant availability updated: {restaurant_id} -> {'Open' if is_open else 'Closed'}")
                
                # Notify users with pending orders
                await self.notify_restaurant_availability_change(restaurant_id, is_open)
            
            if 'menu_items' in updated_fields:
                logger.info(f"🍽️ Menu updated for restaurant: {restaurant_id}")
                
                # Clear menu cache in Redis
                await self.clear_restaurant_menu_cache(restaurant_id)
    
    async def handle_delivery_boy_change(self, change: Dict[str, Any]):
        """
        Delivery boy changes handle करो - location tracking, availability
        """
        operation_type = change.get('operationType')
        
        if operation_type == 'update':
            updated_fields = change.get('updateDescription', {}).get('updatedFields', {})
            delivery_boy_id = change.get('documentKey', {}).get('_id')
            
            if 'current_location' in updated_fields:
                new_location = updated_fields['current_location']
                logger.info(f"📍 Delivery boy location updated: {delivery_boy_id}")
                
                # Update real-time tracking
                await self.update_delivery_boy_location(delivery_boy_id, new_location)
                
                # Check if near delivery destinations
                await self.check_delivery_proximity(delivery_boy_id, new_location)
            
            if 'is_available' in updated_fields:
                is_available = updated_fields['is_available']
                logger.info(f"🚴 Delivery boy availability: {delivery_boy_id} -> {'Available' if is_available else 'Busy'}")
                
                if is_available:
                    # Assign pending orders
                    await self.assign_pending_orders(delivery_boy_id)
    
    async def handle_tracking_change(self, change: Dict[str, Any]):
        """
        Order tracking changes handle करो - real-time delivery updates
        """
        operation_type = change.get('operationType')
        
        if operation_type == 'insert':
            tracking_data = change.get('fullDocument', {})
            order_id = tracking_data.get('order_id')
            
            logger.info(f"📱 New tracking update for order: {order_id}")
            
            # Send real-time update to customer app
            await self.send_real_time_tracking_update(tracking_data)
    
    async def send_to_kafka(self, collection_name: str, change: Dict[str, Any]):
        """
        Change events को Kafka में send करो - downstream processing के लिए
        """
        try:
            kafka_message = {
                'collection': collection_name,
                'operation': change.get('operationType'),
                'timestamp': datetime.now().isoformat(),
                'change_data': change,
                'source': 'swiggy-mongodb-cdc'
            }
            
            topic = f"swiggy.{collection_name}.changes"
            
            # Send to Kafka
            future = self.kafka_producer.send(
                topic=topic,
                key=str(change.get('documentKey', {}).get('_id', '')),
                value=kafka_message
            )
            
            # Don't wait for send completion to avoid blocking
            # Production में आप error handling add करें
            
        except Exception as e:
            logger.error(f"💥 Kafka send error: {str(e)}")
    
    async def update_redis_cache(self, collection_name: str, change: Dict[str, Any]):
        """
        Redis cache update करो - fast reads के लिए
        """
        try:
            operation_type = change.get('operationType')
            document_id = str(change.get('documentKey', {}).get('_id', ''))
            
            if operation_type == 'insert' or operation_type == 'update':
                # Cache the document
                if operation_type == 'insert':
                    document = change.get('fullDocument', {})
                else:
                    # For updates, fetch full document
                    document = await self.async_database[collection_name].find_one(
                        {"_id": change.get('documentKey', {}).get('_id')}
                    )
                
                if document:
                    cache_key = f"{collection_name}:{document_id}"
                    cache_value = json.dumps(document, default=str)
                    
                    self.redis_client.setex(
                        name=cache_key,
                        time=300,  # 5 minutes TTL
                        value=cache_value
                    )
                    
            elif operation_type == 'delete':
                # Remove from cache
                cache_key = f"{collection_name}:{document_id}"
                self.redis_client.delete(cache_key)
                
        except Exception as e:
            logger.error(f"💥 Redis cache update error: {str(e)}")
    
    async def send_order_notification(self, order: Dict[str, Any], event_type: str):
        """
        Order notification send करो - push notifications, SMS
        """
        logger.info(f"📱 Sending {event_type} notification for order: {order.get('order_id')}")
        
        # यहाँ actual notification service integration होगी
        # FCM, SMS gateway, email service etc.
        
        notification_data = {
            'user_id': order.get('user_id'),
            'order_id': order.get('order_id'),
            'event_type': event_type,
            'message': f"Your order {order.get('order_id')} has been {event_type.lower()}",
            'timestamp': datetime.now().isoformat()
        }
        
        # Mock notification sending
        logger.info(f"📤 Notification sent: {notification_data}")
    
    async def assign_delivery_boy(self, order: Dict[str, Any]):
        """
        Delivery boy assign करो - location-based assignment
        """
        restaurant_location = order.get('delivery_address', {}).get('coordinates', {})
        
        if not restaurant_location:
            logger.warning(f"⚠️ No location data for order: {order.get('order_id')}")
            return
        
        # Find nearest available delivery boy
        # यहाँ geospatial query होगी
        logger.info(f"🔍 Finding delivery boy for order: {order.get('order_id')}")
        
        # Mock assignment
        await self.async_database.orders.update_one(
            {"order_id": order.get('order_id')},
            {
                "$set": {
                    "delivery_boy_id": "DB12345678",
                    "status": "CONFIRMED",
                    "updated_at": datetime.now()
                }
            }
        )
        
        logger.info(f"✅ Delivery boy assigned to order: {order.get('order_id')}")
    
    async def send_status_update_notification(self, order_id: str, status: str):
        """Status update notification send करो"""
        logger.info(f"📱 Sending status update: {order_id} -> {status}")
    
    async def update_delivery_tracking(self, order_id: str, status: str):
        """Delivery tracking update करो"""
        logger.info(f"🚚 Updating delivery tracking: {order_id} -> {status}")
    
    async def notify_restaurant_availability_change(self, restaurant_id: str, is_open: bool):
        """Restaurant availability notification send करो"""
        logger.info(f"🏪 Restaurant availability notification: {restaurant_id} -> {'Open' if is_open else 'Closed'}")
    
    async def clear_restaurant_menu_cache(self, restaurant_id: str):
        """Restaurant menu cache clear करो"""
        pattern = f"menu:{restaurant_id}:*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
            logger.info(f"🗑️ Cleared menu cache for restaurant: {restaurant_id}")
    
    async def update_delivery_boy_location(self, delivery_boy_id: str, location: Dict[str, float]):
        """Delivery boy location update करो"""
        logger.info(f"📍 Location updated for delivery boy: {delivery_boy_id}")
    
    async def check_delivery_proximity(self, delivery_boy_id: str, location: Dict[str, float]):
        """Delivery proximity check करो"""
        logger.info(f"📍 Checking delivery proximity for: {delivery_boy_id}")
    
    async def assign_pending_orders(self, delivery_boy_id: str):
        """Pending orders assign करो"""
        logger.info(f"📦 Assigning pending orders to: {delivery_boy_id}")
    
    async def send_real_time_tracking_update(self, tracking_data: Dict[str, Any]):
        """Real-time tracking update send करो"""
        logger.info(f"📱 Real-time tracking update: {tracking_data.get('order_id')}")
    
    async def update_restaurant_metrics(self, restaurant_id: str, metric_type: str):
        """Restaurant metrics update करो"""
        logger.info(f"📊 Updating restaurant metrics: {restaurant_id} -> {metric_type}")
    
    async def start(self):
        """
        Complete CDC system start करो
        """
        logger.info("🚀 Starting Swiggy MongoDB CDC System")
        
        try:
            # Initialize connections
            await self.initialize()
            
            # Setup collections
            await self.setup_collections_and_indexes()
            
            # Generate sample data
            await self.generate_sample_data()
            
            # Start change streams
            await self.start_change_streams()
            
            # Mark as running
            self.running = True
            logger.info("✅ Swiggy MongoDB CDC System started successfully")
            
            # Keep running and log metrics
            while self.running:
                await asyncio.sleep(30)
                await self.log_system_metrics()
            
        except Exception as e:
            logger.error(f"💥 CDC System startup failed: {str(e)}")
            raise
    
    async def log_system_metrics(self):
        """System metrics log करो"""
        try:
            # Get collection counts
            orders_count = await self.async_database.orders.count_documents({})
            restaurants_count = await self.async_database.restaurants.count_documents({})
            delivery_boys_count = await self.async_database.delivery_boys.count_documents({})
            
            logger.info(f"📊 System Metrics - Orders: {orders_count}, Restaurants: {restaurants_count}, Delivery Boys: {delivery_boys_count}")
            
        except Exception as e:
            logger.error(f"💥 Metrics logging error: {str(e)}")
    
    async def stop(self):
        """
        CDC system को gracefully stop करो
        """
        logger.info("🛑 Stopping MongoDB CDC System")
        
        self.running = False
        
        # Close connections
        if self.kafka_producer:
            self.kafka_producer.close()
        
        if self.async_client:
            self.async_client.close()
        
        if self.client:
            self.client.close()
        
        logger.info("✅ MongoDB CDC System stopped successfully")

async def main():
    """
    Main function - Swiggy style food delivery CDC demo
    """
    logger.info("🇮🇳 Starting Indian Food Delivery CDC Demo")
    
    # MongoDB connection parameters
    mongo_uri = "mongodb://localhost:27017/"
    database_name = "swiggy_food_delivery"
    
    # Initialize CDC processor
    cdc_processor = SwiggyMongoDBChangeStreamsProcessor(mongo_uri, database_name)
    
    try:
        # Start the CDC system
        await cdc_processor.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
        await cdc_processor.stop()
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        await cdc_processor.stop()

if __name__ == "__main__":
    asyncio.run(main())

"""
Production Deployment Guide:

1. MongoDB Configuration:
   - Enable replica set (minimum 3 nodes)
   - Configure oplog size appropriately
   - Enable authentication and authorization
   - Set up proper indexes for performance

2. Change Streams Optimization:
   - Use resume tokens for fault tolerance
   - Implement proper error handling and retry logic
   - Monitor change stream lag
   - Use appropriate batch sizes

3. Scaling Strategy:
   - Shard collections based on location/restaurant
   - Use multiple change stream consumers
   - Implement proper load balancing
   - Cache frequently accessed data

4. Indian Food Delivery Specific:
   - Geospatial indexing for location-based queries
   - Real-time inventory management
   - Dynamic pricing based on demand
   - Multi-language support (Hindi, regional languages)

5. Integration Points:
   - Payment gateways (Razorpay, Paytm, PhonePe)
   - SMS gateways for notifications
   - Push notification services (FCM)
   - Analytics platforms (Mixpanel, Clevertap)

6. Monitoring & Observability:
   - MongoDB metrics monitoring
   - Change stream performance metrics
   - Business KPIs (order completion rate, delivery time)
   - Error rate monitoring and alerting
"""