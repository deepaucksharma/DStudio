"""
RESTful API Implementation for Zomato-style Food Ordering Service
Production-grade microservice with proper HTTP status codes and error handling

Author: Episode 9 - Microservices Communication  
Context: Zomato jaise food ordering system - REST API best practices
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from decimal import Decimal
import json
import time
import logging
import uuid
from enum import Enum
import threading
from datetime import datetime, timedelta
import hashlib
import jwt
from functools import wraps

# Custom JSON encoder for Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Enums for order management
class OrderStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED" 
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

# Data models
@dataclass
class Restaurant:
    restaurant_id: str
    name: str
    cuisine_type: str
    location: str
    rating: float
    delivery_time_mins: int
    is_active: bool = True
    phone: str = ""
    
@dataclass
class MenuItem:
    item_id: str
    restaurant_id: str
    name: str
    description: str
    price: Decimal
    category: str
    is_veg: bool
    is_available: bool = True
    preparation_time_mins: int = 20

@dataclass
class OrderItem:
    item_id: str
    quantity: int
    unit_price: Decimal
    special_instructions: str = ""

@dataclass
class Order:
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    total_amount: Decimal
    delivery_address: str
    phone: str
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = None
    estimated_delivery: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

# Hindi logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZomatoOrderingService:
    """
    Production-ready Zomato-style food ordering service
    
    Features:
    - RESTful API design
    - JWT authentication
    - Rate limiting
    - Order lifecycle management
    - Real-time order tracking
    - Payment integration ready
    """
    
    def __init__(self):
        # In-memory storage (production mein database)
        self.restaurants: Dict[str, Restaurant] = {}
        self.menu_items: Dict[str, MenuItem] = {}
        self.orders: Dict[str, Order] = {}
        self.users: Dict[str, dict] = {}  # User authentication data
        
        # Thread safety
        self.data_lock = threading.RLock()
        
        # Rate limiting (simple implementation)
        self.request_counts: Dict[str, List[float]] = {}
        
        # JWT secret (production mein environment variable se)
        self.jwt_secret = "zomato_secret_key_production_change_karna"
        
        logger.info("Zomato Ordering Service initialized")
        self._setup_demo_data()
    
    def _setup_demo_data(self):
        """Demo restaurants aur menu items create karta hai"""
        # Demo restaurants
        demo_restaurants = [
            Restaurant(
                "rest_001", "Toit Brewery", "Continental", "Indiranagar, Bangalore",
                4.5, 45, True, "+91-9876543210"
            ),
            Restaurant(
                "rest_002", "Saravana Bhavan", "South Indian", "T Nagar, Chennai", 
                4.3, 30, True, "+91-9876543211"
            ),
            Restaurant(
                "rest_003", "Barbeque Nation", "North Indian", "Khan Market, Delhi",
                4.4, 50, True, "+91-9876543212"
            ),
            Restaurant(
                "rest_004", "Leopold Cafe", "Multi-cuisine", "Colaba, Mumbai",
                4.1, 35, True, "+91-9876543213"
            )
        ]
        
        for restaurant in demo_restaurants:
            self.restaurants[restaurant.restaurant_id] = restaurant
        
        # Demo menu items
        demo_menu_items = [
            # Toit Brewery menu
            MenuItem("item_001", "rest_001", "Craft Beer Flight", "4 different craft beers", 
                    Decimal("899.00"), "Beverages", False, True, 5),
            MenuItem("item_002", "rest_001", "Bangalore Biryani", "Signature chicken biryani",
                    Decimal("450.00"), "Main Course", False, True, 35),
            MenuItem("item_003", "rest_001", "Paneer Tikka Pizza", "Wood-fired pizza with paneer",
                    Decimal("549.00"), "Main Course", True, True, 25),
            
            # Saravana Bhavan menu  
            MenuItem("item_004", "rest_002", "Masala Dosa", "Crispy dosa with potato filling",
                    Decimal("120.00"), "South Indian", True, True, 15),
            MenuItem("item_005", "rest_002", "Chettinad Chicken", "Spicy Tamil chicken curry",
                    Decimal("280.00"), "Main Course", False, True, 30),
            MenuItem("item_006", "rest_002", "Filter Coffee", "Traditional South Indian coffee",
                    Decimal("45.00"), "Beverages", True, True, 5),
            
            # Barbeque Nation items
            MenuItem("item_007", "rest_003", "Unlimited Buffet", "All-you-can-eat buffet",
                    Decimal("899.00"), "Buffet", False, True, 0),
            MenuItem("item_008", "rest_003", "Tandoori Platter", "Mixed tandoori items",
                    Decimal("650.00"), "Starters", False, True, 25),
            
            # Leopold Cafe items
            MenuItem("item_009", "rest_004", "Mumbai Pav Bhaji", "Street-style pav bhaji",
                    Decimal("180.00"), "Street Food", True, True, 20),
            MenuItem("item_010", "rest_004", "Bombay Duck Curry", "Traditional Konkani curry",
                    Decimal("420.00"), "Main Course", False, True, 35)
        ]
        
        for item in demo_menu_items:
            self.menu_items[item.item_id] = item
        
        # Demo user
        self.users["user_123"] = {
            "user_id": "user_123",
            "name": "Rahul Sharma",
            "phone": "+91-9876543000",
            "email": "rahul@email.com",
            "password_hash": hashlib.sha256("password123".encode()).hexdigest()
        }
        
        logger.info(f"Demo data loaded: {len(demo_restaurants)} restaurants, "
                   f"{len(demo_menu_items)} menu items")


# Flask app setup
app = Flask(__name__)
CORS(app)  # Cross-origin support
app.json_encoder = DecimalEncoder

# Global service instance
ordering_service = ZomatoOrderingService()

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token missing - login required'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]  # Remove 'Bearer ' prefix
                
            data = jwt.decode(token, ordering_service.jwt_secret, algorithms=['HS256'])
            g.current_user_id = data['user_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired - please login again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

# Rate limiting decorator
def rate_limit(max_requests: int = 100, window_minutes: int = 1):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            window_start = current_time - (window_minutes * 60)
            
            with ordering_service.data_lock:
                if client_ip not in ordering_service.request_counts:
                    ordering_service.request_counts[client_ip] = []
                
                # Remove old requests outside the window
                ordering_service.request_counts[client_ip] = [
                    req_time for req_time in ordering_service.request_counts[client_ip]
                    if req_time > window_start
                ]
                
                # Check rate limit
                if len(ordering_service.request_counts[client_ip]) >= max_requests:
                    return jsonify({
                        'error': f'Rate limit exceeded - max {max_requests} requests per {window_minutes} minute(s)'
                    }), 429
                
                # Add current request
                ordering_service.request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Service health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'zomato-ordering',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'restaurants_count': len(ordering_service.restaurants),
        'active_orders': len([o for o in ordering_service.orders.values() 
                            if o.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]])
    }), 200

@app.route('/auth/login', methods=['POST'])
@rate_limit(max_requests=5, window_minutes=1)  # Prevent brute force
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Simple authentication (production mein proper hashing)
        user_id = "user_123"  # Demo user
        user = ordering_service.users.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        
        if user['password_hash'] != password_hash:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token_payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, ordering_service.jwt_secret, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/restaurants', methods=['GET'])
@rate_limit(max_requests=50, window_minutes=1)
def get_restaurants():
    """Get all active restaurants"""
    try:
        location = request.args.get('location', '')
        cuisine = request.args.get('cuisine', '')
        
        restaurants = []
        
        for restaurant in ordering_service.restaurants.values():
            if not restaurant.is_active:
                continue
                
            # Filter by location (case-insensitive partial match)
            if location and location.lower() not in restaurant.location.lower():
                continue
                
            # Filter by cuisine
            if cuisine and cuisine.lower() not in restaurant.cuisine_type.lower():
                continue
            
            restaurants.append(asdict(restaurant))
        
        return jsonify({
            'restaurants': restaurants,
            'count': len(restaurants),
            'filters_applied': {
                'location': location if location else None,
                'cuisine': cuisine if cuisine else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get restaurants error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/restaurants/<restaurant_id>/menu', methods=['GET'])
@rate_limit(max_requests=30, window_minutes=1)
def get_restaurant_menu(restaurant_id):
    """Get menu for specific restaurant"""
    try:
        if restaurant_id not in ordering_service.restaurants:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        restaurant = ordering_service.restaurants[restaurant_id]
        
        if not restaurant.is_active:
            return jsonify({'error': 'Restaurant currently not available'}), 503
        
        # Get menu items for this restaurant
        menu_items = []
        categories = set()
        
        for item in ordering_service.menu_items.values():
            if item.restaurant_id == restaurant_id and item.is_available:
                menu_items.append(asdict(item))
                categories.add(item.category)
        
        return jsonify({
            'restaurant': asdict(restaurant),
            'menu_items': menu_items,
            'categories': sorted(list(categories)),
            'total_items': len(menu_items)
        }), 200
        
    except Exception as e:
        logger.error(f"Get menu error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/orders', methods=['POST'])
@token_required
@rate_limit(max_requests=10, window_minutes=1)
def create_order():
    """Create new food order"""
    try:
        data = request.get_json()
        
        # Validate request data
        required_fields = ['restaurant_id', 'items', 'delivery_address', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        restaurant_id = data['restaurant_id']
        
        # Validate restaurant
        if restaurant_id not in ordering_service.restaurants:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        restaurant = ordering_service.restaurants[restaurant_id]
        if not restaurant.is_active:
            return jsonify({'error': 'Restaurant currently closed'}), 503
        
        # Validate and process order items
        order_items = []
        total_amount = Decimal('0.00')
        total_prep_time = 0
        
        for item_data in data['items']:
            if 'item_id' not in item_data or 'quantity' not in item_data:
                return jsonify({'error': 'Invalid item format'}), 400
            
            item_id = item_data['item_id']
            quantity = int(item_data['quantity'])
            
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be positive'}), 400
            
            if item_id not in ordering_service.menu_items:
                return jsonify({'error': f'Menu item {item_id} not found'}), 404
            
            menu_item = ordering_service.menu_items[item_id]
            
            if menu_item.restaurant_id != restaurant_id:
                return jsonify({'error': f'Item {item_id} not from selected restaurant'}), 400
            
            if not menu_item.is_available:
                return jsonify({'error': f'Item {menu_item.name} currently unavailable'}), 409
            
            # Create order item
            order_item = OrderItem(
                item_id=item_id,
                quantity=quantity,
                unit_price=menu_item.price,
                special_instructions=item_data.get('special_instructions', '')
            )
            
            order_items.append(order_item)
            total_amount += menu_item.price * quantity
            total_prep_time = max(total_prep_time, menu_item.preparation_time_mins)
        
        # Create order
        order_id = f"ORD_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        estimated_delivery = datetime.now() + timedelta(
            minutes=total_prep_time + restaurant.delivery_time_mins
        )
        
        order = Order(
            order_id=order_id,
            user_id=g.current_user_id,
            restaurant_id=restaurant_id,
            items=order_items,
            total_amount=total_amount,
            delivery_address=data['delivery_address'],
            phone=data['phone'],
            estimated_delivery=estimated_delivery
        )
        
        with ordering_service.data_lock:
            ordering_service.orders[order_id] = order
        
        logger.info(f"New order created: {order_id} for user {g.current_user_id}, "
                   f"total ₹{total_amount}")
        
        # Return order confirmation
        return jsonify({
            'message': 'Order placed successfully',
            'order_id': order_id,
            'status': order.status.value,
            'total_amount': float(total_amount),
            'estimated_delivery': estimated_delivery.isoformat(),
            'restaurant': restaurant.name,
            'items_count': len(order_items)
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Create order error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/orders/<order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Get specific order details"""
    try:
        if order_id not in ordering_service.orders:
            return jsonify({'error': 'Order not found'}), 404
        
        order = ordering_service.orders[order_id]
        
        # Check if user owns this order
        if order.user_id != g.current_user_id:
            return jsonify({'error': 'Access denied - not your order'}), 403
        
        # Get restaurant and item details
        restaurant = ordering_service.restaurants[order.restaurant_id]
        
        order_details = {
            'order_id': order.order_id,
            'status': order.status.value,
            'payment_status': order.payment_status.value,
            'total_amount': float(order.total_amount),
            'delivery_address': order.delivery_address,
            'phone': order.phone,
            'created_at': order.created_at.isoformat(),
            'estimated_delivery': order.estimated_delivery.isoformat(),
            'restaurant': {
                'name': restaurant.name,
                'phone': restaurant.phone,
                'location': restaurant.location
            },
            'items': []
        }
        
        for order_item in order.items:
            menu_item = ordering_service.menu_items[order_item.item_id]
            order_details['items'].append({
                'name': menu_item.name,
                'quantity': order_item.quantity,
                'unit_price': float(order_item.unit_price),
                'total_price': float(order_item.unit_price * order_item.quantity),
                'special_instructions': order_item.special_instructions,
                'is_veg': menu_item.is_veg
            })
        
        return jsonify(order_details), 200
        
    except Exception as e:
        logger.error(f"Get order error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/orders/<order_id>/cancel', methods=['PUT'])
@token_required
def cancel_order(order_id):
    """Cancel an order"""
    try:
        if order_id not in ordering_service.orders:
            return jsonify({'error': 'Order not found'}), 404
        
        order = ordering_service.orders[order_id]
        
        # Check ownership
        if order.user_id != g.current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if cancellation is allowed
        if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            return jsonify({'error': 'Order cannot be cancelled'}), 409
        
        if order.status == OrderStatus.OUT_FOR_DELIVERY:
            return jsonify({'error': 'Order is out for delivery - cannot cancel'}), 409
        
        # Cancel order
        with ordering_service.data_lock:
            order.status = OrderStatus.CANCELLED
        
        logger.info(f"Order cancelled: {order_id}")
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order_id': order_id,
            'status': order.status.value
        }), 200
        
    except Exception as e:
        logger.error(f"Cancel order error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/orders/user/<user_id>', methods=['GET'])
@token_required
def get_user_orders(user_id):
    """Get all orders for a user"""
    try:
        # Check if requesting own orders
        if user_id != g.current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        user_orders = []
        
        for order in ordering_service.orders.values():
            if order.user_id == user_id:
                restaurant = ordering_service.restaurants[order.restaurant_id]
                
                user_orders.append({
                    'order_id': order.order_id,
                    'status': order.status.value,
                    'total_amount': float(order.total_amount),
                    'created_at': order.created_at.isoformat(),
                    'restaurant_name': restaurant.name,
                    'items_count': len(order.items)
                })
        
        # Sort by creation date (newest first)
        user_orders.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'orders': user_orders,
            'total_orders': len(user_orders)
        }), 200
        
    except Exception as e:
        logger.error(f"Get user orders error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def run_zomato_api_demo():
    """
    Demo function to showcase the REST API functionality
    """
    print("🍔 Zomato Food Ordering REST API")
    print("="*50)
    
    print("\n📋 Available Endpoints:")
    endpoints = [
        "GET    /health                    - Service health check",
        "POST   /auth/login               - User authentication", 
        "GET    /restaurants              - List restaurants (with filters)",
        "GET    /restaurants/{id}/menu    - Get restaurant menu",
        "POST   /orders                   - Create new order",
        "GET    /orders/{id}              - Get order details", 
        "PUT    /orders/{id}/cancel       - Cancel order",
        "GET    /orders/user/{id}         - Get user's orders"
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")
    
    print(f"\n🔐 Authentication:")
    print(f"   • JWT token-based authentication")
    print(f"   • Bearer token in Authorization header")
    print(f"   • 24-hour token expiry")
    
    print(f"\n⚡ Features Implemented:")
    print(f"   ✅ RESTful API design with proper HTTP methods")
    print(f"   ✅ JSON request/response format")
    print(f"   ✅ JWT authentication and authorization")
    print(f"   ✅ Rate limiting (prevents abuse)")
    print(f"   ✅ Input validation and error handling")
    print(f"   ✅ CORS support for web clients")
    print(f"   ✅ Structured error responses")
    print(f"   ✅ Health check endpoint for monitoring")
    
    print(f"\n🏭 Production Considerations:")
    print(f"   • Database integration (PostgreSQL/MongoDB)")
    print(f"   • Redis for caching and sessions") 
    print(f"   • API versioning (/v1/, /v2/)")
    print(f"   • Rate limiting with Redis")
    print(f"   • Proper logging and monitoring")
    print(f"   • API documentation (Swagger/OpenAPI)")
    print(f"   • Load balancing and auto-scaling")

if __name__ == "__main__":
    # Run the demo first
    run_zomato_api_demo()
    
    print("\n" + "="*50)
    print("🚀 Starting Flask Development Server...")
    print("API available at: http://localhost:5000")
    print("Test with: curl -X GET http://localhost:5000/health")
    print("\n📚 LEARNING POINTS:")
    print("• REST API stateless hai - server pe session store nahi karte")
    print("• HTTP status codes ka proper use important hai")
    print("• JWT tokens se scalable authentication")
    print("• Rate limiting se API abuse prevent karte hai")
    print("• Input validation har endpoint pe mandatory hai")
    print("• Error handling production mein critical hai")
    
    # Start the Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)