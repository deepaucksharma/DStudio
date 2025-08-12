#!/usr/bin/env python3
"""
Swiggy JWT Authentication System  
स्विग्गी style JWT token based authentication और authorization

JWT (JSON Web Token) Features:
- Stateless authentication (server पे session store नहीं करना पडता)
- Self-contained tokens (सारी user info token में ही होती है)
- Cross-service authentication (microservices के लिए perfect)
- Mobile app friendly (token store करना easy)

Swiggy Use Cases:
- Customer login/logout
- Delivery partner authentication
- Restaurant partner access
- Admin panel access
- API access for third-party integrations

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns (JWT Authentication)
"""

from flask import Flask, request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta
import hashlib
import uuid
import json
from typing import Dict, List, Optional
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT configuration - Production में यह environment variables से आएगा
JWT_SECRET = "swiggy_secret_key_mumbai_ka_khana"  # Production में complex secret use करें
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(hours=24)  # 24 hours token validity
JWT_REFRESH_EXPIRATION_DELTA = timedelta(days=30)  # 30 days refresh token

# User database (Production में यह PostgreSQL/MongoDB होगा)
USERS_DB = {
    # Customer accounts
    "customer_123": {
        "user_id": "customer_123",
        "name": "Rahul Sharma", 
        "email": "rahul@gmail.com",
        "mobile": "+91-9876543210",
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "customer",
        "addresses": [
            {
                "id": "addr_1",
                "type": "home",
                "address": "A-101 Mumbai Heights, Andheri East, Mumbai - 400069",
                "landmark": "Near Metro Station"
            }
        ],
        "preferences": {
            "cuisine": ["North Indian", "Chinese", "Fast Food"],
            "dietary": ["vegetarian"],
            "default_address": "addr_1"
        },
        "wallet_balance": 500.50,
        "loyalty_points": 1250,
        "status": "active",
        "created_at": "2023-01-15"
    },
    
    # Delivery partner account
    "delivery_456": {
        "user_id": "delivery_456",
        "name": "Suresh Kumar",
        "email": "suresh.delivery@swiggy.com", 
        "mobile": "+91-9876543211",
        "password_hash": hashlib.sha256("delivery123".encode()).hexdigest(),
        "role": "delivery_partner",
        "vehicle_details": {
            "type": "motorcycle",
            "number": "MH-01-AB-1234",
            "insurance_valid": True
        },
        "zone": "Andheri-Versova",
        "rating": 4.8,
        "total_deliveries": 2450,
        "earnings_today": 850.00,
        "status": "online",
        "created_at": "2022-05-20"
    },
    
    # Restaurant partner account  
    "restaurant_789": {
        "user_id": "restaurant_789",
        "restaurant_name": "Mumbai Vada Pav Corner",
        "owner_name": "Prakash Patil",
        "email": "prakash@vadapav.com",
        "mobile": "+91-9876543212", 
        "password_hash": hashlib.sha256("restaurant123".encode()).hexdigest(),
        "role": "restaurant_partner",
        "address": "Shop No. 15, FC Road, Pune - 411004",
        "cuisines": ["Street Food", "Maharashtrian"],
        "rating": 4.2,
        "commission_rate": 0.18,  # 18% commission to Swiggy
        "menu_items": 45,
        "avg_delivery_time": 25,
        "status": "active",
        "created_at": "2023-03-10"
    },
    
    # Admin account
    "admin_001": {
        "user_id": "admin_001",
        "name": "Swiggy Admin",
        "email": "admin@swiggy.com",
        "mobile": "+91-9876543213",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(), 
        "role": "admin",
        "permissions": ["users", "restaurants", "orders", "analytics", "system"],
        "department": "Operations",
        "city": "Mumbai",
        "status": "active",
        "created_at": "2021-01-01"
    }
}

# Refresh tokens store (Production में यह Redis होगा)
REFRESH_TOKENS = {}

# JWT token creation और validation functions

def generate_jwt_token(user_id: str, additional_claims: Dict = None) -> str:
    """
    JWT token generate करता है user के लिए
    Mumbai style token with all necessary claims
    """
    if user_id not in USERS_DB:
        raise ValueError("User not found")
    
    user = USERS_DB[user_id]
    current_time = datetime.utcnow()
    
    # Standard JWT claims
    payload = {
        'user_id': user_id,
        'role': user['role'],
        'name': user['name'],
        'email': user['email'],
        'mobile': user['mobile'],
        'iat': current_time,  # issued at
        'exp': current_time + JWT_EXPIRATION_DELTA,  # expiry
        'iss': 'swiggy.com',  # issuer
        'aud': 'swiggy-api'   # audience
    }
    
    # Role-specific claims
    if user['role'] == 'customer':
        payload.update({
            'wallet_balance': user['wallet_balance'],
            'loyalty_points': user['loyalty_points'], 
            'default_address': user['preferences']['default_address']
        })
    elif user['role'] == 'delivery_partner':
        payload.update({
            'zone': user['zone'],
            'rating': user['rating'],
            'vehicle_type': user['vehicle_details']['type'],
            'status': user['status']
        })
    elif user['role'] == 'restaurant_partner':
        payload.update({
            'restaurant_name': user['restaurant_name'],
            'commission_rate': user['commission_rate'],
            'rating': user['rating']
        })
    elif user['role'] == 'admin':
        payload.update({
            'permissions': user['permissions'],
            'department': user['department']
        })
    
    # Additional claims (optional)
    if additional_claims:
        payload.update(additional_claims)
    
    # Generate JWT token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"JWT token generated for user: {user_id}, role: {user['role']}")
    
    return token

def generate_refresh_token(user_id: str) -> str:
    """
    Refresh token generate करता है - Long lived token for token renewal
    """
    refresh_token = str(uuid.uuid4())
    REFRESH_TOKENS[refresh_token] = {
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + JWT_REFRESH_EXPIRATION_DELTA
    }
    return refresh_token

def decode_jwt_token(token: str) -> Dict:
    """
    JWT token को decode और validate करता है
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if user still exists and is active
        user_id = payload.get('user_id')
        if user_id not in USERS_DB or USERS_DB[user_id]['status'] != 'active':
            raise jwt.InvalidTokenError("User inactive or deleted")
            
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired! Please login again")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

# Authentication decorators

def jwt_required(allowed_roles: List[str] = None):
    """
    JWT authentication decorator
    Only valid token holders can access protected endpoints
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = None
            
            # Extract token from different sources
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            elif 'token' in request.args:
                token = request.args.get('token')
            elif 'X-Access-Token' in request.headers:
                token = request.headers.get('X-Access-Token')
            
            if not token:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Token missing! Login kar ke token lao पहले'
                }), 401
            
            try:
                # Decode and validate token
                payload = decode_jwt_token(token)
                
                # Role-based access control
                if allowed_roles and payload.get('role') not in allowed_roles:
                    return jsonify({
                        'error': 'Access denied',
                        'message': f'Role {payload.get("role")} not allowed for this action',
                        'required_roles': allowed_roles
                    }), 403
                
                # Pass user info to the route handler
                request.current_user = payload
                return func(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                return jsonify({
                    'error': 'Token expired',
                    'message': 'Token expire ho gaya! Refresh करें या फिर login करें'
                }), 401
            except jwt.InvalidTokenError as e:
                return jsonify({
                    'error': 'Invalid token',
                    'message': str(e)
                }), 401
                
        return wrapper
    return decorator

def admin_required(func):
    """Admin-only access decorator"""
    @wraps(func)
    @jwt_required(['admin'])
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# Authentication endpoints

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    User login endpoint - All types of users (customer, delivery, restaurant, admin)
    """
    try:
        data = request.get_json()
        
        # Input validation
        identifier = data.get('identifier')  # email or mobile
        password = data.get('password')
        user_type = data.get('user_type', 'customer')  # Default to customer
        
        if not identifier or not password:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Email/Mobile और password दोनों required हैं'
            }), 400
        
        # Find user by email or mobile
        user_found = None
        user_id = None
        
        for uid, user in USERS_DB.items():
            if (user['email'] == identifier or 
                user['mobile'] == identifier or
                uid == identifier):
                user_found = user
                user_id = uid
                break
        
        if not user_found:
            return jsonify({
                'error': 'User not found',
                'message': 'Account नहीं मिला! Signup करें पहले'
            }), 404
        
        # Password verification
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user_found['password_hash']:
            return jsonify({
                'error': 'Invalid password',
                'message': 'Password galat है! Check करके try करें'
            }), 401
        
        # Account status check
        if user_found['status'] != 'active':
            return jsonify({
                'error': 'Account suspended',
                'message': 'Account suspended है! Support team से contact करें'
            }), 403
        
        # Generate tokens
        access_token = generate_jwt_token(user_id)
        refresh_token = generate_refresh_token(user_id)
        
        # Role-specific login response
        response_data = {
            'success': True,
            'message': f'Login successful! Welcome {user_found["name"]}',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(JWT_EXPIRATION_DELTA.total_seconds()),
            'user': {
                'user_id': user_id,
                'name': user_found['name'],
                'email': user_found['email'],
                'role': user_found['role']
            }
        }
        
        # Role-specific additional data
        if user_found['role'] == 'customer':
            response_data['user'].update({
                'wallet_balance': user_found['wallet_balance'],
                'loyalty_points': user_found['loyalty_points'],
                'addresses_count': len(user_found['addresses'])
            })
        elif user_found['role'] == 'delivery_partner':
            response_data['user'].update({
                'zone': user_found['zone'],
                'rating': user_found['rating'],
                'total_deliveries': user_found['total_deliveries'],
                'status': user_found['status']
            })
        elif user_found['role'] == 'restaurant_partner':
            response_data['user'].update({
                'restaurant_name': user_found['restaurant_name'],
                'rating': user_found['rating'],
                'menu_items': user_found['menu_items']
            })
        
        logger.info(f"Login successful for {user_found['role']}: {user_id}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Login failed',
            'message': 'कुछ technical problem! Please try again'
        }), 500

@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """
    Token refresh endpoint - Access token को renew करने के लिए
    """
    try:
        data = request.get_json()
        refresh_token_value = data.get('refresh_token')
        
        if not refresh_token_value:
            return jsonify({
                'error': 'Refresh token required',
                'message': 'Refresh token provide करें'
            }), 400
        
        # Validate refresh token
        if refresh_token_value not in REFRESH_TOKENS:
            return jsonify({
                'error': 'Invalid refresh token',
                'message': 'Invalid या expired refresh token'
            }), 401
        
        refresh_data = REFRESH_TOKENS[refresh_token_value]
        
        # Check expiration
        if datetime.utcnow() > refresh_data['expires_at']:
            del REFRESH_TOKENS[refresh_token_value]
            return jsonify({
                'error': 'Refresh token expired',
                'message': 'Refresh token expire हो गया! Please login again'
            }), 401
        
        # Generate new access token
        user_id = refresh_data['user_id']
        new_access_token = generate_jwt_token(user_id)
        
        logger.info(f"Token refreshed for user: {user_id}")
        
        return jsonify({
            'success': True,
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': int(JWT_EXPIRATION_DELTA.total_seconds()),
            'message': 'Token successfully refreshed!'
        })
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500

@app.route('/api/auth/logout', methods=['POST']) 
@jwt_required()
def logout():
    """
    Logout endpoint - Refresh token को revoke करता है
    """
    try:
        data = request.get_json()
        refresh_token_value = data.get('refresh_token')
        
        # Revoke refresh token
        if refresh_token_value and refresh_token_value in REFRESH_TOKENS:
            del REFRESH_TOKENS[refresh_token_value]
        
        user_id = request.current_user['user_id']
        logger.info(f"User logged out: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully logged out! Phir se aana Swiggy pe 😊'
        })
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

# Protected endpoints for different user roles

@app.route('/api/customer/profile', methods=['GET'])
@jwt_required(['customer'])
def get_customer_profile():
    """Customer profile endpoint - Only customers can access"""
    user_id = request.current_user['user_id']
    user = USERS_DB[user_id]
    
    return jsonify({
        'user_id': user_id,
        'name': user['name'],
        'email': user['email'],
        'mobile': user['mobile'],
        'addresses': user['addresses'],
        'preferences': user['preferences'],
        'wallet_balance': user['wallet_balance'],
        'loyalty_points': user['loyalty_points'],
        'message': f'Profile data for customer: {user["name"]}'
    })

@app.route('/api/delivery/dashboard', methods=['GET'])
@jwt_required(['delivery_partner'])
def get_delivery_dashboard():
    """Delivery partner dashboard - Only delivery partners can access"""
    user_id = request.current_user['user_id']
    user = USERS_DB[user_id]
    
    return jsonify({
        'partner_name': user['name'],
        'zone': user['zone'],
        'rating': user['rating'],
        'total_deliveries': user['total_deliveries'],
        'earnings_today': user['earnings_today'],
        'vehicle_details': user['vehicle_details'],
        'online_status': user['status'],
        'message': f'Dashboard for delivery partner: {user["name"]}'
    })

@app.route('/api/restaurant/orders', methods=['GET'])
@jwt_required(['restaurant_partner'])
def get_restaurant_orders():
    """Restaurant orders endpoint - Only restaurant partners can access"""
    user_id = request.current_user['user_id']
    user = USERS_DB[user_id]
    
    # Mock order data
    orders = [
        {
            'order_id': 'ORD123456',
            'customer_name': 'Rahul Sharma',
            'items': ['Vada Pav x2', 'Misal Pav x1'],
            'amount': 180.00,
            'status': 'preparing',
            'ordered_at': '2025-01-12T10:30:00'
        }
    ]
    
    return jsonify({
        'restaurant_name': user['restaurant_name'],
        'orders': orders,
        'total_orders_today': 25,
        'revenue_today': 4500.00,
        'message': f'Orders for restaurant: {user["restaurant_name"]}'
    })

@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def get_admin_analytics():
    """Admin analytics endpoint - Only admins can access"""
    user_id = request.current_user['user_id']
    
    # Mock analytics data
    analytics = {
        'total_customers': 150000,
        'active_delivery_partners': 5000,
        'partner_restaurants': 2500,
        'orders_today': 45000,
        'revenue_today': 2250000,
        'avg_delivery_time': 28,
        'top_cities': ['Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Chennai']
    }
    
    return jsonify({
        'admin': request.current_user['name'],
        'analytics': analytics,
        'message': 'Admin analytics dashboard'
    })

# Multi-role endpoint example
@app.route('/api/orders/<order_id>', methods=['GET'])
@jwt_required(['customer', 'delivery_partner', 'restaurant_partner', 'admin'])
def get_order_details(order_id):
    """
    Order details endpoint - Multiple roles can access but with different data
    """
    role = request.current_user['role']
    user_id = request.current_user['user_id']
    
    # Mock order data
    order = {
        'order_id': order_id,
        'customer_name': 'Rahul Sharma',
        'restaurant_name': 'Mumbai Vada Pav Corner',
        'delivery_partner': 'Suresh Kumar',
        'items': ['Vada Pav x2', 'Misal Pav x1'],
        'amount': 180.00,
        'status': 'delivered',
        'ordered_at': '2025-01-12T10:30:00',
        'delivered_at': '2025-01-12T11:15:00'
    }
    
    # Role-based data filtering
    if role == 'customer':
        # Customer sees order status and delivery details
        return jsonify({
            'order_id': order['order_id'],
            'restaurant_name': order['restaurant_name'],
            'items': order['items'],
            'amount': order['amount'],
            'status': order['status'],
            'delivery_partner': order['delivery_partner'],
            'ordered_at': order['ordered_at'],
            'delivered_at': order['delivered_at'],
            'message': 'Order details for customer'
        })
    elif role == 'delivery_partner':
        # Delivery partner sees pickup and delivery details
        return jsonify({
            'order_id': order['order_id'],
            'restaurant_name': order['restaurant_name'],
            'customer_name': order['customer_name'],
            'amount': order['amount'],
            'status': order['status'],
            'pickup_address': 'Shop No. 15, FC Road, Pune',
            'delivery_address': 'A-101 Mumbai Heights, Andheri East',
            'message': 'Order details for delivery partner'
        })
    elif role == 'restaurant_partner':
        # Restaurant sees order preparation details
        return jsonify({
            'order_id': order['order_id'],
            'customer_name': order['customer_name'],
            'items': order['items'],
            'amount': order['amount'],
            'status': order['status'],
            'commission': order['amount'] * 0.18,
            'message': 'Order details for restaurant'
        })
    elif role == 'admin':
        # Admin sees complete order details
        return jsonify(order)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Public health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Swiggy JWT Authentication API',
        'features': [
            'JWT-based stateless authentication',
            'Role-based access control (RBAC)',
            'Token refresh mechanism',
            'Multi-role support',
            'Secure password hashing'
        ],
        'supported_roles': ['customer', 'delivery_partner', 'restaurant_partner', 'admin'],
        'message': 'Swiggy authentication system ready! Mumbai se Delhi tak sab deliver करते हैं 🍕'
    })

if __name__ == '__main__':
    print("🍕 Swiggy JWT Authentication Server starting...")
    print("👥 Multi-role authentication system:")
    print("   - Customer: Food ordering and profile")
    print("   - Delivery Partner: Order pickup and delivery")
    print("   - Restaurant Partner: Order management")
    print("   - Admin: System analytics and control")
    print("\n🔐 JWT Features implemented:")
    print("   - Stateless authentication") 
    print("   - Role-based access control")
    print("   - Token refresh mechanism")
    print("   - Secure token validation")
    print("   - Mumbai style error messages")
    
    app.run(host='0.0.0.0', port=8001, debug=True)