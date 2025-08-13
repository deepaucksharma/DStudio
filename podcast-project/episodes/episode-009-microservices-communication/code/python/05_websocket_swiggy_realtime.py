"""
WebSocket Real-time Communication for Swiggy-style Food Delivery
Live order tracking and notifications using WebSockets

Author: Episode 9 - Microservices Communication
Context: Swiggy jaise real-time order tracking - WebSocket bidirectional communication
"""

import asyncio
import websockets
import json
import time
import logging
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# Hindi logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enums for order management
class OrderStatus(Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    PICKED_UP = "PICKED_UP"
    ON_THE_WAY = "ON_THE_WAY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class MessageType(Enum):
    ORDER_UPDATE = "ORDER_UPDATE"
    DELIVERY_LOCATION = "DELIVERY_LOCATION"
    CHAT_MESSAGE = "CHAT_MESSAGE"
    NOTIFICATION = "NOTIFICATION"
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"

# Data models
@dataclass
class Location:
    latitude: float
    longitude: float
    address: str = ""

@dataclass
class OrderUpdateMessage:
    message_type: MessageType = MessageType.ORDER_UPDATE
    order_id: str = ""
    status: OrderStatus = OrderStatus.PLACED
    estimated_time: int = 0  # minutes
    message: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class DeliveryLocationMessage:
    message_type: MessageType = MessageType.DELIVERY_LOCATION
    order_id: str = ""
    delivery_partner_id: str = ""
    current_location: Location = None
    estimated_arrival: int = 0  # minutes
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ChatMessage:
    message_type: MessageType = MessageType.CHAT_MESSAGE
    order_id: str = ""
    sender_id: str = ""
    sender_type: str = "customer"  # customer, delivery_partner, restaurant
    message: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class NotificationMessage:
    message_type: MessageType = MessageType.NOTIFICATION
    title: str = ""
    body: str = ""
    type: str = "info"  # info, warning, error, success
    action_required: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# Custom JSON encoder for WebSocket messages
class WebSocketEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, 'value'):  # Enums
            return obj.value
        if hasattr(obj, '__dict__'):  # Dataclasses
            return asdict(obj)
        return super().default(obj)

class SwiggyWebSocketServer:
    """
    Production-ready WebSocket server for Swiggy-style real-time communication
    
    Features:
    - Order tracking
    - Live delivery partner location
    - Chat support
    - Push notifications
    - Connection management
    - Broadcasting
    - Error handling
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        
        # Connection management
        self.connected_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}  # client_id -> {order_ids}
        self.order_subscribers: Dict[str, Set[str]] = {}  # order_id -> {client_ids}
        
        # Demo data
        self.active_orders: Dict[str, Dict] = {}
        self.delivery_partners: Dict[str, Dict] = {}
        
        # Message queue for background processing
        self.message_queue = queue.Queue()
        
        # Thread pool for background tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"Swiggy WebSocket Server initialized on {host}:{port}")
        self._setup_demo_data()
        
        # Start background tasks
        self.background_task_running = True
        self.background_thread = threading.Thread(target=self._background_tasks, daemon=True)
        self.background_thread.start()
    
    def _setup_demo_data(self):
        """Demo orders aur delivery partners create karta hai"""
        # Demo active orders
        demo_orders = [
            {
                "order_id": "ORD123456",
                "customer_id": "customer_rahul",
                "restaurant_name": "Burger King",
                "status": OrderStatus.PREPARING,
                "estimated_time": 25,
                "delivery_partner_id": "dp_001"
            },
            {
                "order_id": "ORD123457", 
                "customer_id": "customer_priya",
                "restaurant_name": "McDonald's",
                "status": OrderStatus.ON_THE_WAY,
                "estimated_time": 12,
                "delivery_partner_id": "dp_002"
            },
            {
                "order_id": "ORD123458",
                "customer_id": "customer_amit",
                "restaurant_name": "Domino's Pizza",
                "status": OrderStatus.READY_FOR_PICKUP,
                "estimated_time": 5,
                "delivery_partner_id": "dp_003"
            }
        ]
        
        for order in demo_orders:
            self.active_orders[order["order_id"]] = order
        
        # Demo delivery partners
        demo_partners = [
            {
                "partner_id": "dp_001",
                "name": "Ravi Kumar",
                "phone": "+91-9876543001",
                "location": Location(19.0760, 72.8777, "Bandra West"),
                "vehicle": "Bike"
            },
            {
                "partner_id": "dp_002", 
                "name": "Suresh Sharma",
                "phone": "+91-9876543002",
                "location": Location(19.0176, 72.8562, "Colaba"),
                "vehicle": "Bike"
            },
            {
                "partner_id": "dp_003",
                "name": "Ajay Singh", 
                "phone": "+91-9876543003",
                "location": Location(19.1136, 72.8697, "Santacruz East"),
                "vehicle": "Bike"
            }
        ]
        
        for partner in demo_partners:
            self.delivery_partners[partner["partner_id"]] = partner
        
        logger.info(f"Demo data loaded: {len(demo_orders)} orders, {len(demo_partners)} delivery partners")
    
    async def register_client(self, websocket, client_id: str):
        """Client connection register karta hai"""
        self.connected_clients[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        
        logger.info(f"Client registered: {client_id}")
        
        # Send welcome message
        welcome_msg = NotificationMessage(
            title="Connected to Swiggy",
            body="You will receive real-time order updates",
            type="success"
        )
        
        await self.send_to_client(client_id, welcome_msg)
    
    async def unregister_client(self, client_id: str):
        """Client connection remove karta hai"""
        if client_id in self.connected_clients:
            del self.connected_clients[client_id]
        
        # Remove subscriptions
        if client_id in self.client_subscriptions:
            for order_id in self.client_subscriptions[client_id]:
                if order_id in self.order_subscribers:
                    self.order_subscribers[order_id].discard(client_id)
            del self.client_subscriptions[client_id]
        
        logger.info(f"Client unregistered: {client_id}")
    
    async def subscribe_to_order(self, client_id: str, order_id: str):
        """Order updates ke liye subscribe karta hai"""
        if client_id not in self.client_subscriptions:
            self.client_subscriptions[client_id] = set()
        
        if order_id not in self.order_subscribers:
            self.order_subscribers[order_id] = set()
        
        self.client_subscriptions[client_id].add(order_id)
        self.order_subscribers[order_id].add(client_id)
        
        logger.info(f"Client {client_id} subscribed to order {order_id}")
        
        # Send current order status
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            status_msg = OrderUpdateMessage(
                order_id=order_id,
                status=order["status"],
                estimated_time=order["estimated_time"],
                message=f"Order from {order['restaurant_name']}"
            )
            
            await self.send_to_client(client_id, status_msg)
    
    async def send_to_client(self, client_id: str, message: Any):
        """Specific client ko message send karta hai"""
        if client_id in self.connected_clients:
            try:
                websocket = self.connected_clients[client_id]
                message_json = json.dumps(message, cls=WebSocketEncoder)
                await websocket.send(message_json)
                
                logger.debug(f"Message sent to {client_id}: {type(message).__name__}")
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Client {client_id} connection closed")
                await self.unregister_client(client_id)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
    
    async def broadcast_to_order_subscribers(self, order_id: str, message: Any):
        """Order ke subscribers ko broadcast karta hai"""
        if order_id in self.order_subscribers:
            subscribers = list(self.order_subscribers[order_id])  # Copy to avoid modification during iteration
            
            for client_id in subscribers:
                await self.send_to_client(client_id, message)
            
            logger.info(f"Message broadcasted to {len(subscribers)} subscribers of order {order_id}")
    
    async def broadcast_to_all(self, message: Any):
        """All connected clients ko broadcast karta hai"""
        client_ids = list(self.connected_clients.keys())  # Copy to avoid modification
        
        for client_id in client_ids:
            await self.send_to_client(client_id, message)
        
        logger.info(f"Message broadcasted to {len(client_ids)} clients")
    
    async def handle_client_message(self, client_id: str, message_data: Dict):
        """Client se aaye message handle karta hai"""
        try:
            message_type = message_data.get("type")
            
            if message_type == "subscribe_order":
                order_id = message_data.get("order_id")
                if order_id:
                    await self.subscribe_to_order(client_id, order_id)
            
            elif message_type == "send_chat":
                order_id = message_data.get("order_id")
                message_text = message_data.get("message", "")
                
                chat_msg = ChatMessage(
                    order_id=order_id,
                    sender_id=client_id,
                    sender_type="customer",
                    message=message_text
                )
                
                # Broadcast to order subscribers
                await self.broadcast_to_order_subscribers(order_id, chat_msg)
            
            elif message_type == "heartbeat":
                # Respond with heartbeat
                heartbeat_msg = {
                    "message_type": "HEARTBEAT",
                    "timestamp": datetime.now().isoformat(),
                    "server_time": time.time()
                }
                await self.send_to_client(client_id, heartbeat_msg)
            
            else:
                error_msg = {
                    "message_type": "ERROR",
                    "error": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }
                await self.send_to_client(client_id, error_msg)
        
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            error_msg = {
                "message_type": "ERROR", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await self.send_to_client(client_id, error_msg)
    
    def _background_tasks(self):
        """Background mein order updates aur location updates simulate karta hai"""
        logger.info("Background tasks started")
        
        while self.background_task_running:
            try:
                # Simulate order status updates every 10 seconds
                self._simulate_order_updates()
                
                # Simulate delivery partner location updates every 5 seconds
                self._simulate_location_updates()
                
                time.sleep(5)  # Wait 5 seconds
                
            except Exception as e:
                logger.error(f"Background task error: {e}")
    
    def _simulate_order_updates(self):
        """Order status updates simulate karta hai"""
        for order_id, order in self.active_orders.items():
            # Random chance to update status
            if hash(f"{order_id}{int(time.time())}") % 20 == 0:  # 5% chance
                current_status = order["status"]
                
                # Status progression logic
                status_progression = {
                    OrderStatus.PLACED: OrderStatus.CONFIRMED,
                    OrderStatus.CONFIRMED: OrderStatus.PREPARING,
                    OrderStatus.PREPARING: OrderStatus.READY_FOR_PICKUP,
                    OrderStatus.READY_FOR_PICKUP: OrderStatus.PICKED_UP,
                    OrderStatus.PICKED_UP: OrderStatus.ON_THE_WAY,
                    OrderStatus.ON_THE_WAY: OrderStatus.DELIVERED
                }
                
                if current_status in status_progression:
                    new_status = status_progression[current_status]
                    order["status"] = new_status
                    order["estimated_time"] = max(0, order["estimated_time"] - 5)
                    
                    # Create update message
                    update_msg = OrderUpdateMessage(
                        order_id=order_id,
                        status=new_status,
                        estimated_time=order["estimated_time"],
                        message=f"Order status updated: {new_status.value}"
                    )
                    
                    # Queue message for async sending
                    self.message_queue.put(("order_update", order_id, update_msg))
                    
                    logger.info(f"Order {order_id} status updated: {current_status.value} → {new_status.value}")
    
    def _simulate_location_updates(self):
        """Delivery partner location updates simulate karta hai"""
        for partner_id, partner in self.delivery_partners.items():
            # Find orders assigned to this partner
            partner_orders = [
                order_id for order_id, order in self.active_orders.items()
                if order.get("delivery_partner_id") == partner_id and 
                   order["status"] in [OrderStatus.PICKED_UP, OrderStatus.ON_THE_WAY]
            ]
            
            if partner_orders:
                # Simulate location movement
                current_loc = partner["location"]
                new_lat = current_loc.latitude + (hash(f"{partner_id}{time.time()}") % 100 - 50) * 0.0001
                new_lng = current_loc.longitude + (hash(f"{partner_id}{time.time() + 1}") % 100 - 50) * 0.0001
                
                partner["location"] = Location(new_lat, new_lng, "Moving location")
                
                # Send location update for each order
                for order_id in partner_orders:
                    location_msg = DeliveryLocationMessage(
                        order_id=order_id,
                        delivery_partner_id=partner_id,
                        current_location=partner["location"],
                        estimated_arrival=self.active_orders[order_id]["estimated_time"]
                    )
                    
                    self.message_queue.put(("location_update", order_id, location_msg))
    
    async def process_message_queue(self):
        """Message queue process karta hai asynchronously"""
        while True:
            try:
                if not self.message_queue.empty():
                    message_type, target, message = self.message_queue.get_nowait()
                    
                    if message_type == "order_update":
                        await self.broadcast_to_order_subscribers(target, message)
                    elif message_type == "location_update":
                        await self.broadcast_to_order_subscribers(target, message)
                
                await asyncio.sleep(0.1)  # Small delay
                
            except queue.Empty:
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Message queue processing error: {e}")
    
    async def handle_client_connection(self, websocket, path):
        """
        Individual client connection handle karta hai
        WebSocket connection lifecycle management
        """
        client_id = f"client_{uuid.uuid4().hex[:8]}"
        
        try:
            # Register client
            await self.register_client(websocket, client_id)
            
            # Handle messages from client
            async for message in websocket:
                try:
                    message_data = json.loads(message)
                    await self.handle_client_message(client_id, message_data)
                except json.JSONDecodeError:
                    error_msg = {
                        "message_type": "ERROR",
                        "error": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(error_msg))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Client connection error: {e}")
        finally:
            await self.unregister_client(client_id)
    
    async def start_server(self):
        """WebSocket server start karta hai"""
        logger.info(f"Starting Swiggy WebSocket server on {self.host}:{self.port}")
        
        # Start message queue processor
        asyncio.create_task(self.process_message_queue())
        
        # Start WebSocket server
        server = await websockets.serve(
            self.handle_client_connection,
            self.host,
            self.port,
            # Production settings
            max_size=1048576,  # 1MB max message size
            ping_interval=30,   # 30 second ping
            ping_timeout=10,    # 10 second timeout
            close_timeout=10    # 10 second close timeout
        )
        
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        return server
    
    def stop_background_tasks(self):
        """Background tasks band karta hai"""
        self.background_task_running = False
        if self.background_thread.is_alive():
            self.background_thread.join()
        
        self.executor.shutdown(wait=True)
        logger.info("Background tasks stopped")

# WebSocket Client for testing
class SwiggyWebSocketClient:
    """
    Test client for WebSocket server
    Production mein mobile app ya web app use karega
    """
    
    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Server se connect karta hai"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.running = True
            logger.info(f"Connected to {self.uri}")
            
            # Start message listener
            asyncio.create_task(self.listen_for_messages())
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    async def listen_for_messages(self):
        """Server se messages sunta hai"""
        try:
            async for message in self.websocket:
                message_data = json.loads(message)
                await self.handle_server_message(message_data)
        except Exception as e:
            logger.error(f"Message listening error: {e}")
    
    async def handle_server_message(self, message_data: Dict):
        """Server se aaye message handle karta hai"""
        message_type = message_data.get("message_type", "UNKNOWN")
        
        if message_type == "ORDER_UPDATE":
            order_id = message_data.get("order_id")
            status = message_data.get("status")
            estimated_time = message_data.get("estimated_time")
            print(f"🍔 Order Update: {order_id} - {status} (ETA: {estimated_time} mins)")
        
        elif message_type == "DELIVERY_LOCATION":
            order_id = message_data.get("order_id")
            location = message_data.get("current_location")
            if location:
                print(f"📍 Delivery Update: Order {order_id} - Lat: {location['latitude']:.4f}, Lng: {location['longitude']:.4f}")
        
        elif message_type == "NOTIFICATION":
            title = message_data.get("title")
            body = message_data.get("body")
            print(f"🔔 Notification: {title} - {body}")
        
        elif message_type == "CHAT_MESSAGE":
            sender = message_data.get("sender_id")
            message = message_data.get("message")
            print(f"💬 Chat: {sender}: {message}")
        
        elif message_type == "HEARTBEAT":
            print("💓 Heartbeat received")
        
        else:
            print(f"📨 Message: {message_type} - {message_data}")
    
    async def subscribe_to_order(self, order_id: str):
        """Order tracking subscribe karta hai"""
        subscribe_msg = {
            "type": "subscribe_order",
            "order_id": order_id
        }
        
        await self.websocket.send(json.dumps(subscribe_msg))
        logger.info(f"Subscribed to order: {order_id}")
    
    async def send_chat_message(self, order_id: str, message: str):
        """Chat message send karta hai"""
        chat_msg = {
            "type": "send_chat",
            "order_id": order_id,
            "message": message
        }
        
        await self.websocket.send(json.dumps(chat_msg))
        logger.info(f"Chat message sent: {message}")
    
    async def disconnect(self):
        """Connection close karta hai"""
        if self.websocket:
            await self.websocket.close()
            self.running = False
            logger.info("Disconnected from server")


async def run_swiggy_websocket_demo():
    """
    Complete Swiggy WebSocket demo with server and client
    Production-ready real-time communication example
    """
    print("🍕 Swiggy Real-time Order Tracking - WebSocket Demo")
    print("="*60)
    
    # Start WebSocket server
    server_instance = SwiggyWebSocketServer()
    server = await server_instance.start_server()
    
    # Wait for server to start
    await asyncio.sleep(1)
    
    print(f"\n🚀 WebSocket Server Started")
    print(f"   • URL: ws://localhost:8765")
    print(f"   • Active orders: {len(server_instance.active_orders)}")
    print(f"   • Delivery partners: {len(server_instance.delivery_partners)}")
    
    # Create test client
    client = SwiggyWebSocketClient()
    
    try:
        # Connect client
        await client.connect()
        
        print(f"\n📱 Test Client Connected")
        
        # Subscribe to demo orders
        demo_order_ids = list(server_instance.active_orders.keys())[:2]
        
        for order_id in demo_order_ids:
            await client.subscribe_to_order(order_id)
            await asyncio.sleep(0.5)
        
        print(f"\n🔔 Subscribed to orders: {demo_order_ids}")
        
        # Send a test chat message
        await asyncio.sleep(1)
        await client.send_chat_message(demo_order_ids[0], "Hi, when will my order arrive?")
        
        # Let the demo run for some time to show real-time updates
        print(f"\n⏳ Running demo for 15 seconds to show real-time updates...")
        print(f"   Watch for order status updates and delivery tracking")
        
        await asyncio.sleep(15)
        
        print(f"\n📊 Demo Statistics:")
        print(f"   • Connected clients: {len(server_instance.connected_clients)}")
        print(f"   • Order subscriptions: {len(server_instance.order_subscribers)}")
        print(f"   • Messages processed: {server_instance.message_queue.qsize()} in queue")
        
        print(f"\n⚡ WebSocket Benefits Demonstrated:")
        print(f"   ✅ Real-time bidirectional communication")
        print(f"   ✅ Low latency order updates")
        print(f"   ✅ Live delivery partner tracking")
        print(f"   ✅ Interactive chat support")
        print(f"   ✅ Push notifications")
        print(f"   ✅ Connection management and error handling")
        print(f"   ✅ Broadcasting to multiple clients")
        
        print(f"\n🏭 Production Features:")
        print(f"   • Connection pooling and scaling")
        print(f"   • Message queuing and persistence")
        print(f"   • Authentication and authorization")
        print(f"   • Rate limiting and abuse prevention")
        print(f"   • Monitoring and metrics")
        print(f"   • Load balancing with Redis adapter")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"❌ Demo error: {e}")
    
    finally:
        # Cleanup
        try:
            await client.disconnect()
            server_instance.stop_background_tasks()
            server.close()
            await server.wait_closed()
            print(f"\n✅ Demo cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


def run_websocket_demo():
    """Synchronous wrapper for async demo"""
    try:
        asyncio.run(run_swiggy_websocket_demo())
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    # Run the Swiggy WebSocket demo
    run_websocket_demo()
    
    print("\n" + "="*60)
    print("📚 LEARNING POINTS:")
    print("• WebSocket full-duplex communication provide karta hai")
    print("• HTTP ke comparison mein low latency aur overhead kam hai")
    print("• Real-time applications ke liye perfect - gaming, chat, live tracking")
    print("• Connection state maintain karna challenging hai")
    print("• Scaling ke liye Redis adapter ya message broker use karte hai")
    print("• Mobile apps mein battery optimization important hai")
    print("• Fallback mechanism HTTP polling ke saath implement karte hai")
    
    print("\n🔧 Advanced WebSocket Patterns:")
    print("• Socket.IO for cross-platform compatibility")
    print("• WebSocket Secure (WSS) for production")
    print("• Connection pooling for high concurrency")
    print("• Room-based broadcasting")
    print("• Heartbeat mechanism for connection health")
    print("• Graceful degradation to HTTP polling")