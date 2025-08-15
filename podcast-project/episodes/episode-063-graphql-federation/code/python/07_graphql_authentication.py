#!/usr/bin/env python3
"""
07_graphql_authentication.py
GraphQL में Authentication और Authorization implementation
JWT tokens, role-based access control, और field-level security
"""

import jwt
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import graphene
from graphene import ObjectType, String, Boolean, List as GrapheneList, Field, Schema, Mutation
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.graphql import GraphQLApp
from starlette.requests import Request
import bcrypt

# Configuration
JWT_SECRET = "your-super-secret-jwt-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# User Roles
class UserRole(Enum):
    ADMIN = "admin"
    SELLER = "seller" 
    CUSTOMER = "customer"
    GUEST = "guest"

# Permissions
class Permission(Enum):
    READ_PRODUCTS = "read:products"
    WRITE_PRODUCTS = "write:products"
    DELETE_PRODUCTS = "delete:products"
    READ_ORDERS = "read:orders"
    WRITE_ORDERS = "write:orders"
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    READ_ANALYTICS = "read:analytics"

# Role-Permission mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ_PRODUCTS, Permission.WRITE_PRODUCTS, Permission.DELETE_PRODUCTS,
        Permission.READ_ORDERS, Permission.WRITE_ORDERS,
        Permission.READ_USERS, Permission.WRITE_USERS, Permission.DELETE_USERS,
        Permission.READ_ANALYTICS
    ],
    UserRole.SELLER: [
        Permission.READ_PRODUCTS, Permission.WRITE_PRODUCTS,
        Permission.READ_ORDERS, Permission.WRITE_ORDERS,
        Permission.READ_ANALYTICS
    ],
    UserRole.CUSTOMER: [
        Permission.READ_PRODUCTS,
        Permission.READ_ORDERS, Permission.WRITE_ORDERS
    ],
    UserRole.GUEST: [
        Permission.READ_PRODUCTS
    ]
}

# Data Models
@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = None
    last_login: datetime = None

@dataclass
class Product:
    id: str
    name: str
    price: float
    seller_id: str
    is_published: bool = True
    created_at: datetime = None

@dataclass
class Order:
    id: str
    user_id: str
    product_ids: List[str]
    total_amount: float
    status: str = "pending"
    created_at: datetime = None

# Mock Database
class AuthDatabase:
    def __init__(self):
        # Hash password utility
        def hash_password(password: str) -> str:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Sample users
        self.users = {
            '1': User('1', 'admin', 'admin@flipkart.com', hash_password('admin123'), UserRole.ADMIN),
            '2': User('2', 'seller1', 'seller@amazon.in', hash_password('seller123'), UserRole.SELLER),
            '3': User('3', 'customer1', 'customer@paytm.com', hash_password('customer123'), UserRole.CUSTOMER),
            '4': User('4', 'guest', 'guest@example.com', hash_password('guest123'), UserRole.GUEST),
        }
        
        # Sample products
        self.products = {
            '1': Product('1', 'iPhone 15 Pro', 134900.0, '2'),
            '2': Product('2', 'Samsung Galaxy S24', 84999.0, '2'),  
            '3': Product('3', 'Secret Product', 999999.0, '1'),  # Admin only
        }
        
        # Sample orders
        self.orders = {
            '1': Order('1', '3', ['1'], 134900.0, 'delivered'),
            '2': Order('2', '3', ['2'], 84999.0, 'shipped'),
        }
        
        # Session tracking
        self.active_sessions = {}
        
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """User authentication"""
        print(f"🔐 Authenticating user: {username}")
        
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            print(f"❌ User {username} not found")
            return None
            
        if not user.is_active:
            print(f"❌ User {username} is deactivated")
            return None
            
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Update last login
            user.last_login = datetime.now()
            print(f"✅ Authentication successful for {username}")
            return user
        else:
            print(f"❌ Invalid password for {username}")
            return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

# Database instance
auth_db = AuthDatabase()

# JWT Utilities
def create_jwt_token(user: User) -> str:
    """JWT token create करता है"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role.value,
        'permissions': [p.value for p in ROLE_PERMISSIONS.get(user.role, [])],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
        'iss': 'graphql-auth-service'
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """JWT token verify करता है"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        if datetime.utcnow() > datetime.utcfromtimestamp(payload['exp']):
            print("❌ JWT token expired")
            return None
            
        return payload
    
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid JWT token: {e}")
        return None

# Authentication decorator
def require_permission(permission: Permission):
    """Field-level permission decorator"""
    def decorator(func):
        async def wrapper(self, info, *args, **kwargs):
            context = info.context
            user = context.get('current_user')
            
            if not user:
                raise Exception("Authentication required")
            
            user_permissions = ROLE_PERMISSIONS.get(user.role, [])
            if permission not in user_permissions:
                raise Exception(f"Permission denied. Required: {permission.value}")
            
            print(f"✅ Permission check passed: {permission.value} for user {user.username}")
            return await func(self, info, *args, **kwargs)
        
        return wrapper
    return decorator

def require_role(required_role: UserRole):
    """Role-based access decorator"""
    def decorator(func):
        async def wrapper(self, info, *args, **kwargs):
            context = info.context
            user = context.get('current_user')
            
            if not user:
                raise Exception("Authentication required")
            
            if user.role != required_role:
                raise Exception(f"Access denied. Required role: {required_role.value}")
            
            print(f"✅ Role check passed: {required_role.value} for user {user.username}")
            return await func(self, info, *args, **kwargs)
        
        return wrapper
    return decorator

# GraphQL Types
class UserType(ObjectType):
    id = String()
    username = String()
    email = String()
    role = String()
    is_active = Boolean()
    created_at = String()
    last_login = String()
    
    # Sensitive field - only accessible by admin or self
    async def resolve_email(self, info):
        context = info.context
        current_user = context.get('current_user')
        
        if not current_user:
            raise Exception("Authentication required to view email")
        
        # Admin can see anyone's email, users can see their own
        if current_user.role == UserRole.ADMIN or current_user.id == self.id:
            return self.email
        else:
            raise Exception("Permission denied: Cannot view other user's email")

class ProductType(ObjectType):
    id = String()
    name = String()
    price = String()  # Sensitive pricing info
    seller_id = String()
    is_published = Boolean()
    created_at = String()
    
    # Price field with permission check
    async def resolve_price(self, info):
        context = info.context
        current_user = context.get('current_user')
        
        # Special handling for secret products
        if self.name == "Secret Product":
            if not current_user or current_user.role != UserRole.ADMIN:
                raise Exception("Access denied: Secret product")
        
        # Price visibility based on role
        if current_user and current_user.role in [UserRole.ADMIN, UserRole.SELLER]:
            return f"₹{self.price:,.2f}"
        else:
            # Guests and customers see rounded price
            rounded_price = round(self.price, -3)  # Round to nearest thousand
            return f"₹{rounded_price:,.2f}+"

class OrderType(ObjectType):
    id = String()
    user_id = String()
    product_ids = GrapheneList(String)
    total_amount = String()
    status = String()
    created_at = String()
    
    # User can only see their own orders
    async def resolve_user_id(self, info):
        context = info.context
        current_user = context.get('current_user')
        
        if not current_user:
            raise Exception("Authentication required")
        
        # Admin can see all, users can see their own
        if current_user.role == UserRole.ADMIN or current_user.id == self.user_id:
            return self.user_id
        else:
            raise Exception("Permission denied: Cannot view other user's orders")

# Authentication Mutations
class LoginInput(graphene.InputObjectType):
    username = String(required=True)
    password = String(required=True)

class LoginPayload(ObjectType):
    success = Boolean()
    message = String()
    token = String()
    user = Field(UserType)
    expires_in = String()

class Login(Mutation):
    class Arguments:
        input = LoginInput(required=True)
    
    Output = LoginPayload
    
    async def mutate(self, info, input):
        username = input.username
        password = input.password
        
        print(f"🔐 Login attempt for: {username}")
        
        # Authenticate user
        user = auth_db.authenticate_user(username, password)
        
        if not user:
            return LoginPayload(
                success=False,
                message="Invalid credentials",
                token=None,
                user=None
            )
        
        # Create JWT token
        token = create_jwt_token(user)
        
        # Track active session
        auth_db.active_sessions[user.id] = {
            'token': token,
            'login_time': datetime.now(),
            'last_activity': datetime.now()
        }
        
        return LoginPayload(
            success=True,
            message=f"Login successful. Welcome {user.username}!",
            token=token,
            user=user,
            expires_in=f"{JWT_EXPIRATION_HOURS} hours"
        )

class Logout(Mutation):
    success = Boolean()
    message = String()
    
    async def mutate(self, info):
        context = info.context
        current_user = context.get('current_user')
        
        if not current_user:
            return Logout(success=False, message="Not logged in")
        
        # Remove from active sessions
        auth_db.active_sessions.pop(current_user.id, None)
        
        print(f"👋 User {current_user.username} logged out")
        
        return Logout(success=True, message="Logged out successfully")

class CreateUserInput(graphene.InputObjectType):
    username = String(required=True)
    email = String(required=True)
    password = String(required=True)
    role = String(required=True)

class CreateUser(Mutation):
    class Arguments:
        input = CreateUserInput(required=True)
    
    Output = UserType
    
    @require_role(UserRole.ADMIN)
    async def mutate(self, info, input):
        # Hash password
        password_hash = bcrypt.hashpw(input.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        new_user = User(
            id=str(len(auth_db.users) + 1),
            username=input.username,
            email=input.email,
            password_hash=password_hash,
            role=UserRole(input.role),
            created_at=datetime.now()
        )
        
        auth_db.users[new_user.id] = new_user
        
        print(f"👤 New user created: {input.username} with role {input.role}")
        
        return new_user

# Queries
class Query(ObjectType):
    # Public queries
    products = GrapheneList(ProductType)
    product = Field(ProductType, id=String(required=True))
    
    # Protected queries
    users = GrapheneList(UserType)
    user = Field(UserType, id=String(required=True))
    orders = GrapheneList(OrderType)
    user_orders = GrapheneList(OrderType, user_id=String())
    
    # Profile query
    me = Field(UserType)
    
    # Analytics queries
    admin_analytics = Field(String)
    
    # Public product listing
    async def resolve_products(self, info):
        context = info.context
        current_user = context.get('current_user')
        
        products = list(auth_db.products.values())
        
        # Filter secret products for non-admin users
        if not current_user or current_user.role != UserRole.ADMIN:
            products = [p for p in products if p.name != "Secret Product"]
        
        print(f"🛍️ Products query by {current_user.username if current_user else 'anonymous'}")
        return products
    
    async def resolve_product(self, info, id):
        product = auth_db.products.get(id)
        
        if not product:
            raise Exception(f"Product {id} not found")
        
        # Check access to secret products
        context = info.context
        current_user = context.get('current_user')
        
        if product.name == "Secret Product":
            if not current_user or current_user.role != UserRole.ADMIN:
                raise Exception("Access denied: Secret product")
        
        return product
    
    # Admin-only user listing
    @require_permission(Permission.READ_USERS)
    async def resolve_users(self, info):
        print("👥 Users query (admin only)")
        return list(auth_db.users.values())
    
    @require_permission(Permission.READ_USERS)
    async def resolve_user(self, info, id):
        user = auth_db.get_user(id)
        if not user:
            raise Exception(f"User {id} not found")
        return user
    
    # Order queries
    @require_permission(Permission.READ_ORDERS)
    async def resolve_orders(self, info):
        context = info.context
        current_user = context.get('current_user')
        
        orders = list(auth_db.orders.values())
        
        # Non-admin users can only see their own orders
        if current_user.role != UserRole.ADMIN:
            orders = [o for o in orders if o.user_id == current_user.id]
        
        print(f"📦 Orders query by {current_user.username}")
        return orders
    
    async def resolve_user_orders(self, info, user_id=None):
        context = info.context
        current_user = context.get('current_user')
        
        if not current_user:
            raise Exception("Authentication required")
        
        # If no user_id provided, return current user's orders
        target_user_id = user_id or current_user.id
        
        # Permission check
        if current_user.role != UserRole.ADMIN and current_user.id != target_user_id:
            raise Exception("Permission denied: Cannot view other user's orders")
        
        orders = [o for o in auth_db.orders.values() if o.user_id == target_user_id]
        print(f"📦 User orders query for user {target_user_id}")
        return orders
    
    # Profile query
    async def resolve_me(self, info):
        context = info.context
        current_user = context.get('current_user')
        
        if not current_user:
            raise Exception("Authentication required")
        
        return current_user
    
    # Analytics (admin only)
    @require_role(UserRole.ADMIN)
    async def resolve_admin_analytics(self, info):
        total_users = len(auth_db.users)
        total_products = len(auth_db.products)
        total_orders = len(auth_db.orders)
        
        analytics = f"""
        📊 Admin Analytics:
        - Total Users: {total_users}
        - Total Products: {total_products}
        - Total Orders: {total_orders}
        - Active Sessions: {len(auth_db.active_sessions)}
        """
        
        return analytics

# Mutations
class Mutations(ObjectType):
    login = Login.Field()
    logout = Logout.Field()
    create_user = CreateUser.Field()

# Schema
schema = Schema(query=Query, mutation=Mutations)

# FastAPI app
app = FastAPI(title="GraphQL Authentication System")

# Security
security = HTTPBearer()

async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[User]:
    """JWT token से user extract करता है"""
    try:
        token = credentials.credentials
        payload = verify_jwt_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        user = auth_db.get_user(user_id)
        
        if not user or not user.is_active:
            return None
        
        # Update last activity
        if user_id in auth_db.active_sessions:
            auth_db.active_sessions[user_id]['last_activity'] = datetime.now()
        
        return user
        
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return None

# Context function
async def get_context(request: Request):
    """GraphQL context with authentication"""
    context = {
        'request': request,
        'current_user': None,
        'is_authenticated': False
    }
    
    # Extract token from Authorization header
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        payload = verify_jwt_token(token)
        
        if payload:
            user_id = payload.get('user_id')
            user = auth_db.get_user(user_id)
            
            if user and user.is_active:
                context['current_user'] = user
                context['is_authenticated'] = True
                
                # Update activity tracking
                if user_id in auth_db.active_sessions:
                    auth_db.active_sessions[user_id]['last_activity'] = datetime.now()
                
                print(f"✅ Authenticated request from {user.username} ({user.role.value})")
            else:
                print("❌ User not found or inactive")
        else:
            print("❌ Invalid token")
    else:
        print("📭 Anonymous request (no token)")
    
    return context

# GraphQL endpoint
app.add_route("/graphql", GraphQLApp(schema=schema, context_value=get_context))

# Public endpoints
@app.get("/health")
async def health_check():
    return {
        "service": "graphql-authentication",
        "status": "healthy",
        "active_sessions": len(auth_db.active_sessions),
        "features": [
            "JWT authentication",
            "Role-based access control",
            "Field-level security",
            "Permission-based queries"
        ]
    }

@app.get("/")
async def root():
    return {
        "title": "GraphQL Authentication System",
        "description": "JWT-based authentication with role-based access control",
        "endpoints": {
            "/graphql": "GraphQL endpoint",
            "/health": "Health check",
            "/auth-demo": "Authentication demo guide"
        },
        "sample_users": {
            "admin": {"username": "admin", "password": "admin123", "role": "admin"},
            "seller": {"username": "seller1", "password": "seller123", "role": "seller"},
            "customer": {"username": "customer1", "password": "customer123", "role": "customer"},
            "guest": {"username": "guest", "password": "guest123", "role": "guest"}
        }
    }

@app.get("/auth-demo")
async def auth_demo():
    return {
        "authentication_flow": {
            "step_1": "Login using mutation",
            "step_2": "Use returned JWT token in Authorization header",
            "step_3": "Access protected queries based on role"
        },
        "sample_mutations": {
            "login": """
            mutation {
              login(input: {username: "admin", password: "admin123"}) {
                success
                message
                token
                user {
                  username
                  role
                }
              }
            }
            """,
            "logout": """
            mutation {
              logout {
                success
                message
              }
            }
            """
        },
        "sample_queries": {
            "public": """
            # No authentication required
            {
              products {
                id
                name
                price
              }
            }
            """,
            "protected": """
            # Requires authentication
            {
              me {
                username
                email
                role
              }
            }
            """,
            "admin_only": """
            # Requires admin role
            {
              users {
                id
                username
                role
              }
              adminAnalytics
            }
            """
        },
        "role_permissions": {
            role.name: [p.value for p in perms] 
            for role, perms in ROLE_PERMISSIONS.items()
        }
    }

if __name__ == "__main__":
    print("🔐 Starting GraphQL Authentication Server...")
    print("🎯 Features:")
    print("   - JWT token-based authentication")
    print("   - Role-based access control (RBAC)")
    print("   - Field-level security")
    print("   - Permission-based queries")
    print("   - Session tracking")
    print("\n👥 Test users:")
    print("   - admin/admin123 (full access)")
    print("   - seller1/seller123 (limited access)")  
    print("   - customer1/customer123 (customer access)")
    print("   - guest/guest123 (read-only access)")
    print("\n🧪 Testing:")
    print("   1. Login को JWT token प्राप्त करें")
    print("   2. Authorization header में token use करें")
    print("   3. Role-based queries test करें")
    
    uvicorn.run(
        "07_graphql_authentication:app",
        host="0.0.0.0",
        port=4022,
        reload=True,
        log_level="info"
    )