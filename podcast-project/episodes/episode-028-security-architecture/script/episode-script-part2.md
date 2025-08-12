# Episode 28: Security Architecture & Zero Trust Networks
## Part 2: Authorization and Encryption (7,000 words)

### Chapter 4: Authorization - Railway Class System ka Digital Avatar

Yaar authorization authentication ke baad ka step hai. Train ticket book kiya, ab platform pe jaana hai. Ticket checker verify karega ki kya tumhara general class ticket hai ya AC ka? Kya tumhe first class coach mein jaane ka permission hai? Exactly yahi karta hai authorization system.

Authentication answers "Who are you?" 
Authorization answers "What can you do?"

Indian Railway system perfect example hai authorization ka. Different class tickets, different privileges:
- General Class: Basic travel only
- Sleeper: Sleeping berth access
- AC 3-tier: AC coach + bedding
- AC 2-tier: Premium seating + meals
- AC First: VIP treatment + attendant service

Digital world mein same concept, but much more granular control.

#### Fine-Grained Authorization - Ration Card System

Mumbai ke ration card system dekho. Har family ka different quota:
- APL (Above Poverty Line): Limited subsidized grain
- BPL (Below Poverty Line): More subsidized items  
- AAY (Antyodaya Anna Yojana): Maximum benefits
- PHH (Priority Household): Special category

Each card holder ke different permissions hai. Technical implementation dikhata hun:

```python
# Fine-grained authorization system like PDS (Public Distribution System)
from enum import Enum
from typing import Dict, List, Optional, Set
import datetime
import json
from dataclasses import dataclass

class ResourceType(Enum):
    GRAIN = "grain"
    SUGAR = "sugar" 
    COOKING_OIL = "cooking_oil"
    KEROSENE = "kerosene"
    LPG_CONNECTION = "lpg_connection"

class CardCategory(Enum):
    APL = "apl"  # Above Poverty Line
    BPL = "bpl"  # Below Poverty Line
    AAY = "aay"  # Antyodaya Anna Yojana
    PHH = "phh"  # Priority Household

@dataclass
class Entitlement:
    resource_type: ResourceType
    monthly_quota: float  # in kg/liters
    subsidized_rate: float  # price per unit
    restrictions: List[str]  # Additional conditions

@dataclass
class FamilyCard:
    card_number: str
    category: CardCategory
    family_size: int
    head_of_family: str
    address: str
    issued_date: datetime.date
    valid_until: datetime.date
    entitlements: Dict[ResourceType, Entitlement]

class PDSAuthorizationSystem:
    """Public Distribution System Authorization - like FoodTech apps"""
    
    def __init__(self):
        self.family_cards: Dict[str, FamilyCard] = {}
        self.monthly_consumption: Dict[str, Dict[ResourceType, float]] = {}
        self.setup_entitlement_matrix()
        
    def setup_entitlement_matrix(self):
        """Setup entitlements per category like government norms"""
        self.entitlement_matrix = {
            CardCategory.AAY: {
                ResourceType.GRAIN: Entitlement(ResourceType.GRAIN, 35.0, 2.0, []),
                ResourceType.SUGAR: Entitlement(ResourceType.SUGAR, 2.0, 13.5, []),
                ResourceType.COOKING_OIL: Entitlement(ResourceType.COOKING_OIL, 1.0, 45.0, []),
                ResourceType.KEROSENE: Entitlement(ResourceType.KEROSENE, 3.0, 15.0, ["rural_only"]),
                ResourceType.LPG_CONNECTION: Entitlement(ResourceType.LPG_CONNECTION, 12.0, 450.0, ["ujjwala_scheme"])
            },
            CardCategory.PHH: {
                ResourceType.GRAIN: Entitlement(ResourceType.GRAIN, 25.0, 3.0, []),
                ResourceType.SUGAR: Entitlement(ResourceType.SUGAR, 1.5, 16.0, []),
                ResourceType.COOKING_OIL: Entitlement(ResourceType.COOKING_OIL, 0.75, 50.0, []),
                ResourceType.LPG_CONNECTION: Entitlement(ResourceType.LPG_CONNECTION, 12.0, 500.0, ["pm_ujjwala"])
            },
            CardCategory.BPL: {
                ResourceType.GRAIN: Entitlement(ResourceType.GRAIN, 15.0, 5.0, []),
                ResourceType.SUGAR: Entitlement(ResourceType.SUGAR, 1.0, 20.0, []),
                ResourceType.COOKING_OIL: Entitlement(ResourceType.COOKING_OIL, 0.5, 60.0, [])
            },
            CardCategory.APL: {
                ResourceType.GRAIN: Entitlement(ResourceType.GRAIN, 10.0, 8.0, ["limited_months"]),
                ResourceType.SUGAR: Entitlement(ResourceType.SUGAR, 0.5, 25.0, ["seasonal_only"])
            }
        }
    
    def register_family(self, card_number: str, category: CardCategory, 
                       family_size: int, head_of_family: str, address: str) -> FamilyCard:
        """Register new family card like Jan Aushadhi registration"""
        
        if card_number in self.family_cards:
            raise ValueError(f"Card {card_number} already exists")
        
        # Calculate entitlements based on category and family size
        base_entitlements = self.entitlement_matrix[category]
        adjusted_entitlements = {}
        
        for resource_type, entitlement in base_entitlements.items():
            # Adjust quota based on family size
            family_multiplier = min(family_size / 4.0, 2.0)  # Max 2x for large families
            adjusted_quota = entitlement.monthly_quota * family_multiplier
            
            adjusted_entitlements[resource_type] = Entitlement(
                resource_type=resource_type,
                monthly_quota=adjusted_quota,
                subsidized_rate=entitlement.subsidized_rate,
                restrictions=entitlement.restrictions.copy()
            )
        
        family_card = FamilyCard(
            card_number=card_number,
            category=category,
            family_size=family_size,
            head_of_family=head_of_family,
            address=address,
            issued_date=datetime.date.today(),
            valid_until=datetime.date.today().replace(year=datetime.date.today().year + 3),
            entitlements=adjusted_entitlements
        )
        
        self.family_cards[card_number] = family_card
        self.monthly_consumption[card_number] = {rt: 0.0 for rt in ResourceType}
        
        return family_card
    
    def authorize_purchase(self, card_number: str, resource_type: ResourceType, 
                          quantity: float, purchase_context: Dict[str, any]) -> Dict[str, any]:
        """Authorize resource purchase like BigBasket/JioMart govt schemes"""
        
        result = {
            'authorized': False,
            'max_allowed': 0.0,
            'subsidized_rate': 0.0,
            'total_cost': 0.0,
            'remaining_quota': 0.0,
            'reasons': []
        }
        
        # Check if card exists and is valid
        family_card = self.family_cards.get(card_number)
        if not family_card:
            result['reasons'].append(f"Invalid card number: {card_number}")
            return result
        
        if datetime.date.today() > family_card.valid_until:
            result['reasons'].append("Card has expired")
            return result
        
        # Check if resource is entitled
        if resource_type not in family_card.entitlements:
            result['reasons'].append(f"Resource {resource_type.value} not entitled for {family_card.category.value} card")
            return result
        
        entitlement = family_card.entitlements[resource_type]
        
        # Check restrictions
        restriction_check = self.check_restrictions(entitlement.restrictions, purchase_context)
        if not restriction_check['allowed']:
            result['reasons'].extend(restriction_check['reasons'])
            return result
        
        # Check monthly quota
        current_month_consumption = self.get_current_month_consumption(card_number, resource_type)
        remaining_quota = entitlement.monthly_quota - current_month_consumption
        
        if remaining_quota <= 0:
            result['reasons'].append(f"Monthly quota exhausted for {resource_type.value}")
            return result
        
        # Calculate maximum allowed quantity
        max_allowed = min(quantity, remaining_quota)
        
        # Calculate cost
        subsidized_rate = entitlement.subsidized_rate
        total_cost = max_allowed * subsidized_rate
        
        # Update result
        result.update({
            'authorized': True,
            'max_allowed': max_allowed,
            'subsidized_rate': subsidized_rate,
            'total_cost': total_cost,
            'remaining_quota': remaining_quota - max_allowed,
            'reasons': [f"Authorized {max_allowed} kg/liters at subsidized rate"]
        })
        
        # Record consumption (in real system, this happens after successful purchase)
        self.monthly_consumption[card_number][resource_type] += max_allowed
        
        return result
    
    def check_restrictions(self, restrictions: List[str], context: Dict[str, any]) -> Dict[str, any]:
        """Check restriction conditions like location, season, scheme eligibility"""
        result = {'allowed': True, 'reasons': []}
        
        for restriction in restrictions:
            if restriction == "rural_only":
                if context.get('location_type') != 'rural':
                    result['allowed'] = False
                    result['reasons'].append("Resource only available in rural areas")
            
            elif restriction == "seasonal_only":
                current_month = datetime.date.today().month
                if current_month not in [10, 11, 12, 1, 2]:  # Oct-Feb only
                    result['allowed'] = False
                    result['reasons'].append("Resource only available in winter season")
            
            elif restriction == "ujjwala_scheme":
                if not context.get('is_ujjwala_beneficiary', False):
                    result['allowed'] = False
                    result['reasons'].append("Requires Ujjwala scheme enrollment")
            
            elif restriction == "limited_months":
                current_month = datetime.date.today().month
                if current_month in [6, 7, 8]:  # No supply during monsoon
                    result['allowed'] = False
                    result['reasons'].append("No supply during monsoon months")
        
        return result
    
    def get_current_month_consumption(self, card_number: str, resource_type: ResourceType) -> float:
        """Get current month consumption for quota calculation"""
        # In real system, this would query database for current month data
        return self.monthly_consumption.get(card_number, {}).get(resource_type, 0.0)
    
    def get_family_entitlement_summary(self, card_number: str) -> Dict[str, any]:
        """Get complete entitlement summary like mAadhar app"""
        family_card = self.family_cards.get(card_number)
        if not family_card:
            return {'error': 'Card not found'}
        
        summary = {
            'card_number': card_number,
            'category': family_card.category.value,
            'family_size': family_card.family_size,
            'head_of_family': family_card.head_of_family,
            'valid_until': family_card.valid_until.isoformat(),
            'entitlements': {},
            'current_month_usage': {}
        }
        
        for resource_type, entitlement in family_card.entitlements.items():
            current_consumption = self.get_current_month_consumption(card_number, resource_type)
            remaining_quota = entitlement.monthly_quota - current_consumption
            
            summary['entitlements'][resource_type.value] = {
                'monthly_quota': entitlement.monthly_quota,
                'subsidized_rate': entitlement.subsidized_rate,
                'restrictions': entitlement.restrictions
            }
            
            summary['current_month_usage'][resource_type.value] = {
                'consumed': current_consumption,
                'remaining': remaining_quota,
                'utilization_percent': (current_consumption / entitlement.monthly_quota) * 100
            }
        
        return summary

# Usage example - Government ration distribution
def demo_pds_authorization():
    """Demo PDS authorization system"""
    pds_system = PDSAuthorizationSystem()
    
    # Register different category families
    families = [
        ("AAY001", CardCategory.AAY, 6, "Ramesh Kumar", "Mumbai Slum Area"),
        ("BPL002", CardCategory.BPL, 4, "Priya Sharma", "Pune Low Income Housing"),
        ("APL003", CardCategory.APL, 3, "Rajesh Mehta", "Mumbai Middle Class Area")
    ]
    
    for card_number, category, family_size, head, address in families:
        family_card = pds_system.register_family(card_number, category, family_size, head, address)
        print(f"Registered family: {card_number} ({category.value}) - {family_size} members")
    
    print("\n" + "="*50)
    print("AUTHORIZATION TESTING")
    print("="*50)
    
    # Test different authorization scenarios
    test_scenarios = [
        {
            'card': 'AAY001',
            'resource': ResourceType.GRAIN,
            'quantity': 30.0,
            'context': {'location_type': 'rural', 'is_ujjwala_beneficiary': True}
        },
        {
            'card': 'BPL002', 
            'resource': ResourceType.COOKING_OIL,
            'quantity': 1.0,
            'context': {'location_type': 'urban'}
        },
        {
            'card': 'APL003',
            'resource': ResourceType.SUGAR,
            'quantity': 2.0,
            'context': {'location_type': 'urban'}
        },
        {
            'card': 'AAY001',
            'resource': ResourceType.KEROSENE,
            'quantity': 5.0,
            'context': {'location_type': 'urban'}  # Should fail - rural only
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- Testing: {scenario['card']} requesting {scenario['quantity']} kg of {scenario['resource'].value} ---")
        result = pds_system.authorize_purchase(
            scenario['card'],
            scenario['resource'], 
            scenario['quantity'],
            scenario['context']
        )
        
        if result['authorized']:
            print(f"✅ AUTHORIZED: {result['max_allowed']} kg at ₹{result['subsidized_rate']}/kg")
            print(f"   Total cost: ₹{result['total_cost']:.2f}")
            print(f"   Remaining quota: {result['remaining_quota']:.2f} kg")
        else:
            print(f"❌ DENIED: {'; '.join(result['reasons'])}")
    
    # Show entitlement summaries
    print("\n" + "="*50)
    print("FAMILY ENTITLEMENT SUMMARIES")
    print("="*50)
    
    for card_number in ['AAY001', 'BPL002', 'APL003']:
        summary = pds_system.get_family_entitlement_summary(card_number)
        print(f"\n{card_number} ({summary['category'].upper()}) - {summary['family_size']} members")
        print("-" * 40)
        
        for resource, usage in summary['current_month_usage'].items():
            entitlement = summary['entitlements'][resource]
            print(f"{resource:15} | Quota: {entitlement['monthly_quota']:6.1f} kg | Used: {usage['consumed']:5.1f} kg | Remaining: {usage['remaining']:5.1f} kg | Rate: ₹{entitlement['subsidized_rate']}")

# Demo run
demo_pds_authorization()
```

#### API Authorization Patterns - Zomato/Swiggy Style

Modern apps mein API authorization bahut complex hoti hai. Zomato dekho:
- Customer: Order food, view restaurants, rate
- Restaurant: Manage menu, update status, view orders
- Delivery Boy: Accept orders, update location, mark delivered  
- Admin: Analytics, user management, system config

Technical implementation:

```python
# API Authorization for food delivery platform
import jwt
import time
from typing import Dict, List, Set, Optional
from enum import Enum
from functools import wraps
from dataclasses import dataclass

class Role(Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    DELIVERY_PARTNER = "delivery_partner"
    ADMIN = "admin"
    SUPPORT = "support"

class Permission(Enum):
    # Customer permissions
    BROWSE_RESTAURANTS = "browse_restaurants"
    PLACE_ORDER = "place_order"
    CANCEL_ORDER = "cancel_order"
    RATE_RESTAURANT = "rate_restaurant"
    VIEW_ORDER_HISTORY = "view_order_history"
    
    # Restaurant permissions
    MANAGE_MENU = "manage_menu"
    VIEW_ORDERS = "view_orders"
    UPDATE_ORDER_STATUS = "update_order_status"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_PROFILE = "manage_profile"
    
    # Delivery partner permissions
    VIEW_AVAILABLE_ORDERS = "view_available_orders"
    ACCEPT_ORDER = "accept_order"
    UPDATE_DELIVERY_STATUS = "update_delivery_status"
    UPDATE_LOCATION = "update_location"
    
    # Admin permissions
    USER_MANAGEMENT = "user_management"
    RESTAURANT_ONBOARDING = "restaurant_onboarding"
    SYSTEM_ANALYTICS = "system_analytics"
    FINANCIAL_REPORTS = "financial_reports"
    SUPPORT_TICKETS = "support_tickets"

@dataclass
class APIEndpoint:
    path: str
    method: str
    required_permissions: List[Permission]
    resource_based: bool = False
    rate_limit: Optional[int] = None  # requests per minute

class ZomatoStyleAPIAuthorization:
    """API Authorization system like Zomato/Swiggy"""
    
    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret
        self.role_permissions = self.setup_role_permissions()
        self.api_endpoints = self.setup_api_endpoints()
        self.rate_limits = {}  # For rate limiting tracking
    
    def setup_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """Setup role-permission mapping"""
        return {
            Role.CUSTOMER: {
                Permission.BROWSE_RESTAURANTS,
                Permission.PLACE_ORDER,
                Permission.CANCEL_ORDER,
                Permission.RATE_RESTAURANT,
                Permission.VIEW_ORDER_HISTORY
            },
            Role.RESTAURANT: {
                Permission.BROWSE_RESTAURANTS,
                Permission.MANAGE_MENU,
                Permission.VIEW_ORDERS,
                Permission.UPDATE_ORDER_STATUS,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_PROFILE
            },
            Role.DELIVERY_PARTNER: {
                Permission.VIEW_AVAILABLE_ORDERS,
                Permission.ACCEPT_ORDER,
                Permission.UPDATE_DELIVERY_STATUS,
                Permission.UPDATE_LOCATION
            },
            Role.ADMIN: set(Permission),  # Admin has all permissions
            Role.SUPPORT: {
                Permission.VIEW_ORDER_HISTORY,
                Permission.SUPPORT_TICKETS,
                Permission.USER_MANAGEMENT
            }
        }
    
    def setup_api_endpoints(self) -> Dict[str, APIEndpoint]:
        """Setup API endpoint configuration"""
        endpoints = [
            # Customer APIs
            APIEndpoint("/api/restaurants", "GET", [Permission.BROWSE_RESTAURANTS], rate_limit=60),
            APIEndpoint("/api/orders", "POST", [Permission.PLACE_ORDER], rate_limit=10),
            APIEndpoint("/api/orders/{order_id}", "DELETE", [Permission.CANCEL_ORDER], resource_based=True),
            APIEndpoint("/api/orders/{order_id}/rating", "POST", [Permission.RATE_RESTAURANT], resource_based=True),
            
            # Restaurant APIs  
            APIEndpoint("/api/restaurant/menu", "PUT", [Permission.MANAGE_MENU], rate_limit=30),
            APIEndpoint("/api/restaurant/orders", "GET", [Permission.VIEW_ORDERS], rate_limit=120),
            APIEndpoint("/api/restaurant/orders/{order_id}/status", "PUT", [Permission.UPDATE_ORDER_STATUS], resource_based=True),
            
            # Delivery Partner APIs
            APIEndpoint("/api/delivery/available-orders", "GET", [Permission.VIEW_AVAILABLE_ORDERS], rate_limit=30),
            APIEndpoint("/api/delivery/orders/{order_id}/accept", "POST", [Permission.ACCEPT_ORDER], resource_based=True),
            APIEndpoint("/api/delivery/location", "PUT", [Permission.UPDATE_LOCATION], rate_limit=60),
            
            # Admin APIs
            APIEndpoint("/api/admin/users", "GET", [Permission.USER_MANAGEMENT], rate_limit=100),
            APIEndpoint("/api/admin/analytics", "GET", [Permission.SYSTEM_ANALYTICS], rate_limit=20)
        ]
        
        return {f"{ep.method}:{ep.path}": ep for ep in endpoints}
    
    def create_jwt_token(self, user_id: str, role: Role, additional_claims: Dict = None) -> str:
        """Create JWT token with role and permissions"""
        payload = {
            'user_id': user_id,
            'role': role.value,
            'permissions': [p.value for p in self.role_permissions[role]],
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600,  # 1 hour expiry
            'iss': 'zomato-api'
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authorize_api_request(self, token: str, method: str, path: str, 
                            resource_context: Dict = None) -> Dict[str, any]:
        """Authorize API request with comprehensive checks"""
        result = {
            'authorized': False,
            'user_id': None,
            'role': None,
            'reasons': []
        }
        
        # Verify JWT token
        payload = self.verify_jwt_token(token)
        if not payload:
            result['reasons'].append('Invalid or expired token')
            return result
        
        user_id = payload.get('user_id')
        role_str = payload.get('role')
        user_permissions = set(payload.get('permissions', []))
        
        # Find matching endpoint
        endpoint_key = f"{method}:{path}"
        endpoint = self.api_endpoints.get(endpoint_key)
        
        if not endpoint:
            result['reasons'].append(f'Endpoint not found: {method} {path}')
            return result
        
        # Check permissions
        required_permissions = set(p.value for p in endpoint.required_permissions)
        if not required_permissions.issubset(user_permissions):
            missing = required_permissions - user_permissions
            result['reasons'].append(f'Missing permissions: {missing}')
            return result
        
        # Resource-based authorization
        if endpoint.resource_based and resource_context:
            resource_auth = self.check_resource_authorization(
                user_id, role_str, path, resource_context
            )
            if not resource_auth['allowed']:
                result['reasons'].extend(resource_auth['reasons'])
                return result
        
        # Rate limiting check
        if endpoint.rate_limit:
            rate_check = self.check_rate_limit(user_id, endpoint_key, endpoint.rate_limit)
            if not rate_check['allowed']:
                result['reasons'].append(rate_check['reason'])
                return result
        
        # All checks passed
        result.update({
            'authorized': True,
            'user_id': user_id,
            'role': role_str,
            'reasons': ['Authorization successful']
        })
        
        return result
    
    def check_resource_authorization(self, user_id: str, role: str, path: str, 
                                   context: Dict) -> Dict[str, any]:
        """Check resource-level authorization (like order ownership)"""
        result = {'allowed': True, 'reasons': []}
        
        # Extract resource ID from path
        if '/orders/' in path:
            order_id = context.get('order_id')
            if not order_id:
                result['allowed'] = False
                result['reasons'].append('Order ID required for resource authorization')
                return result
            
            # Check order ownership/access rights
            order_access = self.check_order_access(user_id, role, order_id, context)
            if not order_access['allowed']:
                result['allowed'] = False
                result['reasons'].extend(order_access['reasons'])
        
        return result
    
    def check_order_access(self, user_id: str, role: str, order_id: str, context: Dict) -> Dict[str, any]:
        """Check if user can access specific order"""
        # In real system, this would query database
        order_info = self.get_order_info(order_id)  # Mock function
        
        if not order_info:
            return {'allowed': False, 'reasons': ['Order not found']}
        
        if role == 'customer':
            # Customer can only access their own orders
            if order_info.get('customer_id') != user_id:
                return {'allowed': False, 'reasons': ['Order does not belong to user']}
        
        elif role == 'restaurant':
            # Restaurant can only access orders from their restaurant
            if order_info.get('restaurant_id') != user_id:
                return {'allowed': False, 'reasons': ['Order not from user restaurant']}
        
        elif role == 'delivery_partner':
            # Delivery partner can only access assigned orders
            if order_info.get('delivery_partner_id') != user_id:
                return {'allowed': False, 'reasons': ['Order not assigned to user']}
        
        return {'allowed': True, 'reasons': []}
    
    def check_rate_limit(self, user_id: str, endpoint_key: str, limit: int) -> Dict[str, any]:
        """Check API rate limiting"""
        current_time = int(time.time())
        minute_key = f"{user_id}:{endpoint_key}:{current_time // 60}"
        
        # In real system, use Redis for distributed rate limiting
        current_requests = self.rate_limits.get(minute_key, 0)
        
        if current_requests >= limit:
            return {
                'allowed': False,
                'reason': f'Rate limit exceeded: {current_requests}/{limit} requests per minute'
            }
        
        # Increment counter
        self.rate_limits[minute_key] = current_requests + 1
        
        return {'allowed': True, 'reason': f'Rate limit OK: {current_requests + 1}/{limit}'}
    
    def get_order_info(self, order_id: str) -> Optional[Dict]:
        """Mock function to get order information"""
        # In real system, this queries the database
        mock_orders = {
            'ORD001': {
                'customer_id': 'CUST123',
                'restaurant_id': 'REST456', 
                'delivery_partner_id': 'DEL789',
                'status': 'confirmed'
            },
            'ORD002': {
                'customer_id': 'CUST456',
                'restaurant_id': 'REST123',
                'delivery_partner_id': None,
                'status': 'preparing'
            }
        }
        return mock_orders.get(order_id)

# Decorator for easy API authorization
def require_authorization(auth_system: ZomatoStyleAPIAuthorization):
    """Decorator to protect API endpoints"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract token from request headers (simplified)
            token = kwargs.get('auth_token')
            method = kwargs.get('method', 'GET')
            path = kwargs.get('path', '/')
            resource_context = kwargs.get('resource_context', {})
            
            if not token:
                return {'error': 'Authorization token required', 'status': 401}
            
            auth_result = auth_system.authorize_api_request(
                token, method, path, resource_context
            )
            
            if not auth_result['authorized']:
                return {
                    'error': 'Authorization failed',
                    'reasons': auth_result['reasons'],
                    'status': 403
                }
            
            # Add user info to kwargs for use in API function
            kwargs['user_info'] = {
                'user_id': auth_result['user_id'],
                'role': auth_result['role']
            }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage example - Zomato API endpoints
def demo_api_authorization():
    """Demo API authorization system"""
    auth_system = ZomatoStyleAPIAuthorization(jwt_secret='super-secret-key')
    
    # Create tokens for different user types
    customer_token = auth_system.create_jwt_token('CUST123', Role.CUSTOMER)
    restaurant_token = auth_system.create_jwt_token('REST456', Role.RESTAURANT)
    delivery_token = auth_system.create_jwt_token('DEL789', Role.DELIVERY_PARTNER)
    admin_token = auth_system.create_jwt_token('ADMIN001', Role.ADMIN)
    
    print("=== API Authorization Testing ===")
    
    # Test scenarios
    test_cases = [
        {
            'name': 'Customer browsing restaurants',
            'token': customer_token,
            'method': 'GET',
            'path': '/api/restaurants'
        },
        {
            'name': 'Customer placing order',
            'token': customer_token,
            'method': 'POST',
            'path': '/api/orders'
        },
        {
            'name': 'Customer canceling own order',
            'token': customer_token,
            'method': 'DELETE',
            'path': '/api/orders/{order_id}',
            'resource_context': {'order_id': 'ORD001'}
        },
        {
            'name': 'Customer canceling someone else order',
            'token': customer_token,
            'method': 'DELETE',
            'path': '/api/orders/{order_id}',
            'resource_context': {'order_id': 'ORD002'}
        },
        {
            'name': 'Restaurant updating order status',
            'token': restaurant_token,
            'method': 'PUT',
            'path': '/api/restaurant/orders/{order_id}/status',
            'resource_context': {'order_id': 'ORD001'}
        },
        {
            'name': 'Delivery partner accepting order',
            'token': delivery_token,
            'method': 'POST',
            'path': '/api/delivery/orders/{order_id}/accept',
            'resource_context': {'order_id': 'ORD001'}
        },
        {
            'name': 'Admin viewing analytics',
            'token': admin_token,
            'method': 'GET',
            'path': '/api/admin/analytics'
        },
        {
            'name': 'Customer trying admin function',
            'token': customer_token,
            'method': 'GET',
            'path': '/api/admin/analytics'
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        
        auth_result = auth_system.authorize_api_request(
            case['token'],
            case['method'],
            case['path'],
            case.get('resource_context', {})
        )
        
        if auth_result['authorized']:
            print(f"✅ AUTHORIZED - User: {auth_result['user_id']} ({auth_result['role']})")
        else:
            print(f"❌ DENIED - Reasons: {'; '.join(auth_result['reasons'])}")

# Demo run  
demo_api_authorization()
```

### Chapter 5: Encryption at Rest and in Transit - Locked Dabba System

Encryption ka concept Mumbai ke dabba system se samjhate hain. Ghar se office lunch leke jaate time:
1. **At Rest**: Dabba ghar mein locked cupboard mein rakha (Data stored encrypted)
2. **In Transit**: Dabbawala locked bag mein carry karta hai (Data encrypted during transfer)  
3. **In Use**: Office mein dabba open karke khana (Data decrypted for processing)

Technical deep dive dikhata hun:

#### Modern Encryption Standards

```python
# Comprehensive encryption system like Indian banking standards  
import os
import hashlib
import hmac
import base64
import time
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, kdf, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import secrets

class BankingGradeEncryption:
    """Banking-grade encryption system like RBI guidelines"""
    
    def __init__(self):
        self.backend = default_backend()
        self.master_key = self.derive_master_key("NPCI_MASTER_PASSWORD_2024")
        self.key_rotation_interval = 86400  # 24 hours
    
    def derive_master_key(self, password: str, salt: bytes = None) -> bytes:
        """Derive master key using PBKDF2 like Aadhaar system"""
        if salt is None:
            salt = b"INDIA_DIGITAL_SALT_2024"  # In production, use random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # High iteration count for security
            backend=self.backend
        )
        
        return kdf.derive(password.encode('utf-8'))
    
    def generate_data_encryption_key(self) -> bytes:
        """Generate DEK for data encryption (envelope encryption pattern)"""
        return Fernet.generate_key()
    
    def encrypt_data_key(self, dek: bytes) -> bytes:
        """Encrypt DEK with master key (envelope encryption)"""
        f = Fernet(base64.urlsafe_b64encode(self.master_key))
        return f.encrypt(dek)
    
    def decrypt_data_key(self, encrypted_dek: bytes) -> bytes:
        """Decrypt DEK using master key"""
        f = Fernet(base64.urlsafe_b64encode(self.master_key))
        return f.decrypt(encrypted_dek)
    
    def encrypt_sensitive_data(self, data: str, context: str = None) -> dict:
        """
        Encrypt sensitive data like Aadhaar numbers, PAN, bank account details
        Uses envelope encryption for better key management
        """
        # Generate unique DEK for this data
        dek = self.generate_data_encryption_key()
        
        # Encrypt actual data with DEK
        f = Fernet(dek)
        encrypted_data = f.encrypt(data.encode('utf-8'))
        
        # Encrypt DEK with master key
        encrypted_dek = self.encrypt_data_key(dek)
        
        # Create metadata for audit and key rotation
        metadata = {
            'encrypted_at': int(time.time()),
            'encryption_version': '1.0',
            'key_id': hashlib.sha256(encrypted_dek).hexdigest()[:16],
            'context': context or 'general',
            'algorithm': 'Fernet-AES256'
        }
        
        return {
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'encrypted_dek': base64.b64encode(encrypted_dek).decode(),
            'metadata': metadata
        }
    
    def decrypt_sensitive_data(self, encryption_result: dict) -> str:
        """Decrypt sensitive data"""
        try:
            # Decode encrypted components
            encrypted_data = base64.b64decode(encryption_result['encrypted_data'])
            encrypted_dek = base64.b64decode(encryption_result['encrypted_dek'])
            
            # Decrypt DEK using master key
            dek = self.decrypt_data_key(encrypted_dek)
            
            # Decrypt data using DEK
            f = Fernet(dek)
            decrypted_data = f.decrypt(encrypted_data)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_file(self, file_path: str, output_path: str) -> dict:
        """Encrypt file like DigiLocker document encryption"""
        # Generate unique DEK for this file
        dek = self.generate_data_encryption_key()
        f = Fernet(dek)
        
        # Read and encrypt file in chunks for large files
        with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Write encrypted DEK at the beginning of file
            encrypted_dek = self.encrypt_data_key(dek)
            outfile.write(len(encrypted_dek).to_bytes(4, 'big'))  # DEK length
            outfile.write(encrypted_dek)
            
            # Encrypt file content in chunks
            chunk_size = 64 * 1024  # 64KB chunks
            while chunk := infile.read(chunk_size):
                encrypted_chunk = f.encrypt(chunk)
                outfile.write(len(encrypted_chunk).to_bytes(4, 'big'))
                outfile.write(encrypted_chunk)
        
        # Calculate file hash for integrity
        file_hash = self.calculate_file_hash(output_path)
        
        return {
            'original_file': file_path,
            'encrypted_file': output_path,
            'file_hash': file_hash,
            'encrypted_at': int(time.time())
        }
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str):
        """Decrypt file encrypted with encrypt_file method"""
        with open(encrypted_file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Read encrypted DEK
            dek_length = int.from_bytes(infile.read(4), 'big')
            encrypted_dek = infile.read(dek_length)
            
            # Decrypt DEK
            dek = self.decrypt_data_key(encrypted_dek)
            f = Fernet(dek)
            
            # Decrypt file chunks
            while True:
                chunk_length_bytes = infile.read(4)
                if not chunk_length_bytes:
                    break
                    
                chunk_length = int.from_bytes(chunk_length_bytes, 'big')
                encrypted_chunk = infile.read(chunk_length)
                
                decrypted_chunk = f.decrypt(encrypted_chunk)
                outfile.write(decrypted_chunk)
    
    def generate_rsa_key_pair(self, key_size: int = 2048) -> tuple:
        """Generate RSA key pair for asymmetric encryption"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()
        
        return private_key, public_key
    
    def rsa_encrypt(self, data: bytes, public_key) -> bytes:
        """RSA encryption for small data like keys"""
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def rsa_decrypt(self, encrypted_data: bytes, private_key) -> bytes:
        """RSA decryption"""
        return private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def create_digital_signature(self, data: bytes, private_key) -> bytes:
        """Create digital signature like DigiLocker"""
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def verify_digital_signature(self, data: bytes, signature: bytes, public_key) -> bool:
        """Verify digital signature"""
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash for file integrity"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def secure_delete(self, file_path: str) -> bool:
        """Securely delete file by overwriting"""
        try:
            if not os.path.exists(file_path):
                return True
            
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(3):  # 3 passes of random data
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
            
            # Finally remove the file
            os.remove(file_path)
            return True
            
        except Exception as e:
            print(f"Secure delete failed: {e}")
            return False

# TLS/SSL implementation for transit encryption
class TransitEncryption:
    """Handle encryption in transit like UPI/banking apps"""
    
    @staticmethod
    def create_certificate_fingerprint(cert_data: bytes) -> str:
        """Create certificate fingerprint for pinning"""
        return hashlib.sha256(cert_data).hexdigest()
    
    @staticmethod 
    def validate_certificate_chain(cert_chain: list) -> bool:
        """Validate certificate chain like banking apps"""
        # Simplified validation - in production, check full chain
        return len(cert_chain) > 0
    
    @staticmethod
    def create_secure_headers() -> dict:
        """Create security headers for API responses"""
        return {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }

# Usage example - Complete encryption workflow
def demo_banking_encryption():
    """Demo complete encryption system like Indian banks"""
    encryptor = BankingGradeEncryption()
    
    print("=== Banking Grade Encryption Demo ===")
    
    # 1. Encrypt sensitive customer data
    sensitive_data = {
        'aadhaar': '123456789012',
        'pan': 'ABCDE1234F',
        'account_number': '1234567890123456',
        'phone': '+91-9876543210'
    }
    
    encrypted_records = {}
    for field, value in sensitive_data.items():
        encrypted_records[field] = encryptor.encrypt_sensitive_data(value, context=f'customer_{field}')
        print(f"✅ Encrypted {field}: {encrypted_records[field]['metadata']['key_id']}")
    
    print("\n--- Decryption Test ---")
    for field, encrypted_record in encrypted_records.items():
        decrypted_value = encryptor.decrypt_sensitive_data(encrypted_record)
        original_value = sensitive_data[field]
        status = "✅ PASS" if decrypted_value == original_value else "❌ FAIL"
        print(f"{status} {field}: {decrypted_value}")
    
    # 2. File encryption (like DigiLocker documents)
    print("\n=== File Encryption ===")
    
    # Create a test file
    test_file_path = '/tmp/test_document.txt'
    encrypted_file_path = '/tmp/test_document.encrypted'
    decrypted_file_path = '/tmp/test_document_decrypted.txt'
    
    with open(test_file_path, 'w') as f:
        f.write("This is a confidential document with Aadhaar: 123456789012")
    
    # Encrypt file
    file_encryption_result = encryptor.encrypt_file(test_file_path, encrypted_file_path)
    print(f"✅ File encrypted: {file_encryption_result['file_hash'][:16]}...")
    
    # Decrypt file
    encryptor.decrypt_file(encrypted_file_path, decrypted_file_path)
    
    # Verify content
    with open(decrypted_file_path, 'r') as f:
        decrypted_content = f.read()
    
    with open(test_file_path, 'r') as f:
        original_content = f.read()
    
    file_status = "✅ PASS" if decrypted_content == original_content else "❌ FAIL"
    print(f"{file_status} File decryption verified")
    
    # 3. Digital signature (like DigiLocker)
    print("\n=== Digital Signature ===")
    private_key, public_key = encryptor.generate_rsa_key_pair()
    
    document_content = b"Important government document for citizen verification"
    signature = encryptor.create_digital_signature(document_content, private_key)
    
    is_valid = encryptor.verify_digital_signature(document_content, signature, public_key)
    signature_status = "✅ VALID" if is_valid else "❌ INVALID"
    print(f"{signature_status} Digital signature verification")
    
    # Test tampered document
    tampered_content = b"Important government document for citizen verification - TAMPERED"
    is_tampered_valid = encryptor.verify_digital_signature(tampered_content, signature, public_key)
    tampered_status = "❌ INVALID" if not is_tampered_valid else "⚠️ ERROR: Should be invalid"
    print(f"{tampered_status} Tampered document signature check")
    
    # 4. Secure cleanup
    print("\n=== Secure Cleanup ===")
    cleanup_files = [test_file_path, encrypted_file_path, decrypted_file_path]
    for file_path in cleanup_files:
        if os.path.exists(file_path):
            success = encryptor.secure_delete(file_path)
            status = "✅ DELETED" if success else "❌ FAILED"
            print(f"{status} {file_path}")

# Demo run
demo_banking_encryption()
```

#### Certificate Management and PKI - Aadhaar Digital Certificate Authority

Public Key Infrastructure (PKI) India mein bahut critical hai. Aadhaar system, DigiLocker, income tax e-filing - sabmein PKI use hota hai.

**India's PKI Ecosystem:**
- **Controller of Certifying Authorities (CCA)**: Top-level authority
- **Certifying Authorities**: Licensed CAs like Sify, NIC, TCS
- **Registration Authorities**: Local enrollment centers
- **Certificate Repository**: Central database of valid certificates

```python
# Indian PKI system implementation
import datetime
import hashlib
import json
from cryptography import x509
from cryptography.x509.oid import NameOID, SignatureAlgorithmOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import ipaddress
from typing import Dict, List, Optional

class IndianPKISystem:
    """PKI system based on Indian CCA framework"""
    
    def __init__(self):
        self.backend = default_backend()
        self.root_ca_key = None
        self.root_ca_cert = None
        self.intermediate_cas = {}
        self.issued_certificates = {}
        self.crl_database = {}
        self.setup_root_ca()
    
    def setup_root_ca(self):
        """Setup Root CA like CCA (Controller of Certifying Authorities)"""
        
        # Generate root CA private key
        self.root_ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,  # Strong key for root CA
            backend=self.backend
        )
        
        # Create root CA certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mumbai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Controller of Certifying Authorities"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Digital India Initiative"),
            x509.NameAttribute(NameOID.COMMON_NAME, "CCA Root CA - India")
        ])
        
        self.root_ca_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.root_ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=7305)  # 20 years
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=2),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).sign(self.root_ca_key, hashes.SHA256(), self.backend)
    
    def create_intermediate_ca(self, ca_name: str, organization: str) -> Dict[str, any]:
        """Create intermediate CA like licensed CAs (Sify, NIC, TCS)"""
        
        # Generate intermediate CA key
        intermediate_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        
        # Create certificate signing request
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Karnataka"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Bangalore"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Digital Certificate Authority"),
            x509.NameAttribute(NameOID.COMMON_NAME, f"{ca_name} Intermediate CA")
        ])
        
        # Create intermediate certificate signed by root CA
        intermediate_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.root_ca_cert.subject
        ).public_key(
            intermediate_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3652)  # 10 years
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=1),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(self.root_ca_key.public_key()),
            critical=False,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(intermediate_key.public_key()),
            critical=False,
        ).sign(self.root_ca_key, hashes.SHA256(), self.backend)
        
        # Store intermediate CA
        self.intermediate_cas[ca_name] = {
            'private_key': intermediate_key,
            'certificate': intermediate_cert,
            'organization': organization,
            'issued_certificates': {},
            'created_at': datetime.datetime.utcnow()
        }
        
        return {
            'ca_name': ca_name,
            'certificate_pem': intermediate_cert.public_bytes(serialization.Encoding.PEM).decode(),
            'serial_number': str(intermediate_cert.serial_number),
            'valid_from': intermediate_cert.not_valid_before.isoformat(),
            'valid_until': intermediate_cert.not_valid_after.isoformat()
        }
    
    def issue_digital_certificate(self, ca_name: str, certificate_request: Dict[str, any]) -> Dict[str, any]:
        """Issue digital certificate like DigiLocker/Aadhaar certificates"""
        
        if ca_name not in self.intermediate_cas:
            return {'error': f'CA {ca_name} not found'}
        
        ca_info = self.intermediate_cas[ca_name]
        
        # Generate user key pair
        user_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        
        # Create subject based on request
        subject_components = [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, certificate_request.get('state', 'Maharashtra')),
            x509.NameAttribute(NameOID.LOCALITY_NAME, certificate_request.get('city', 'Mumbai')),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, certificate_request.get('organization', 'Government of India')),
            x509.NameAttribute(NameOID.COMMON_NAME, certificate_request['common_name'])
        ]
        
        # Add email if provided
        if certificate_request.get('email'):
            subject_components.append(
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, certificate_request['email'])
            )
        
        subject = x509.Name(subject_components)
        
        # Certificate validity period based on type
        cert_type = certificate_request.get('certificate_type', 'personal')
        validity_days = {
            'personal': 365,      # 1 year for personal certificates
            'organization': 730,  # 2 years for org certificates
            'government': 1095,   # 3 years for government certificates
            'ca': 1826           # 5 years for CA certificates
        }.get(cert_type, 365)
        
        # Build certificate
        cert_builder = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_info['certificate'].subject
        ).public_key(
            user_private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_info['private_key'].public_key()),
            critical=False,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(user_private_key.public_key()),
            critical=False,
        )
        
        # Add Subject Alternative Names if provided
        san_list = []
        if certificate_request.get('dns_names'):
            for dns_name in certificate_request['dns_names']:
                san_list.append(x509.DNSName(dns_name))
        
        if certificate_request.get('ip_addresses'):
            for ip_addr in certificate_request['ip_addresses']:
                san_list.append(x509.IPAddress(ipaddress.ip_address(ip_addr)))
        
        if certificate_request.get('email'):
            san_list.append(x509.RFC822Name(certificate_request['email']))
        
        if san_list:
            cert_builder = cert_builder.add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            )
        
        # Add Extended Key Usage based on certificate type
        eku_list = []
        if cert_type in ['personal', 'government']:
            eku_list.extend([
                x509.oid.ExtendedKeyUsageOID.EMAIL_PROTECTION,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
            ])
        elif cert_type == 'organization':
            eku_list.extend([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
            ])
        
        if eku_list:
            cert_builder = cert_builder.add_extension(
                x509.ExtendedKeyUsage(eku_list),
                critical=True,
            )
        
        # Sign the certificate
        certificate = cert_builder.sign(
            ca_info['private_key'], 
            hashes.SHA256(), 
            self.backend
        )
        
        # Store issued certificate
        cert_id = str(certificate.serial_number)
        ca_info['issued_certificates'][cert_id] = {
            'certificate': certificate,
            'private_key': user_private_key,
            'issued_to': certificate_request['common_name'],
            'certificate_type': cert_type,
            'issued_at': datetime.datetime.utcnow(),
            'status': 'active'
        }
        
        return {
            'certificate_id': cert_id,
            'certificate_pem': certificate.public_bytes(serialization.Encoding.PEM).decode(),
            'private_key_pem': user_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode(),
            'issued_to': certificate_request['common_name'],
            'valid_from': certificate.not_valid_before.isoformat(),
            'valid_until': certificate.not_valid_after.isoformat(),
            'certificate_type': cert_type,
            'fingerprint': hashlib.sha256(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()
        }
    
    def verify_certificate_chain(self, certificate_pem: str, ca_name: str = None) -> Dict[str, any]:
        """Verify certificate chain like income tax e-filing verification"""
        
        try:
            # Parse certificate
            certificate = x509.load_pem_x509_certificate(certificate_pem.encode(), self.backend)
            
            verification_result = {
                'valid': False,
                'certificate_info': {},
                'chain_verification': {},
                'revocation_status': {},
                'errors': []
            }
            
            # Extract certificate information
            verification_result['certificate_info'] = {
                'subject': self.format_x509_name(certificate.subject),
                'issuer': self.format_x509_name(certificate.issuer),
                'serial_number': str(certificate.serial_number),
                'valid_from': certificate.not_valid_before.isoformat(),
                'valid_until': certificate.not_valid_after.isoformat(),
                'fingerprint': hashlib.sha256(certificate.public_bytes(serialization.Encoding.DER)).hexdigest(),
                'key_size': certificate.public_key().key_size,
                'signature_algorithm': certificate.signature_algorithm_oid._name
            }
            
            # Check certificate validity period
            current_time = datetime.datetime.utcnow()
            if current_time < certificate.not_valid_before:
                verification_result['errors'].append('Certificate not yet valid')
            elif current_time > certificate.not_valid_after:
                verification_result['errors'].append('Certificate has expired')
            
            # Verify certificate chain
            chain_valid = True
            
            # Check if certificate is issued by known intermediate CA
            issuer_found = False
            for ca_name_check, ca_info in self.intermediate_cas.items():
                if ca_info['certificate'].subject == certificate.issuer:
                    issuer_found = True
                    # Verify signature
                    try:
                        ca_info['certificate'].public_key().verify(
                            certificate.signature,
                            certificate.tbs_certificate_bytes,
                            certificate.signature_algorithm
                        )
                        verification_result['chain_verification']['intermediate_ca'] = 'valid'
                    except Exception as e:
                        verification_result['errors'].append(f'Intermediate CA signature verification failed: {str(e)}')
                        chain_valid = False
                    break
            
            if not issuer_found:
                # Check if issued directly by root CA
                if self.root_ca_cert.subject == certificate.issuer:
                    try:
                        self.root_ca_cert.public_key().verify(
                            certificate.signature,
                            certificate.tbs_certificate_bytes,
                            certificate.signature_algorithm
                        )
                        verification_result['chain_verification']['root_ca'] = 'valid'
                    except Exception as e:
                        verification_result['errors'].append(f'Root CA signature verification failed: {str(e)}')
                        chain_valid = False
                else:
                    verification_result['errors'].append('Certificate issuer not recognized')
                    chain_valid = False
            
            # Check revocation status
            cert_id = str(certificate.serial_number)
            if cert_id in self.crl_database:
                verification_result['revocation_status'] = {
                    'status': 'revoked',
                    'revocation_date': self.crl_database[cert_id]['revoked_at'],
                    'reason': self.crl_database[cert_id]['reason']
                }
                verification_result['errors'].append('Certificate has been revoked')
                chain_valid = False
            else:
                verification_result['revocation_status'] = {'status': 'not_revoked'}
            
            verification_result['valid'] = chain_valid and len(verification_result['errors']) == 0
            
            return verification_result
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Certificate verification failed: {str(e)}'
            }
    
    def revoke_certificate(self, ca_name: str, certificate_id: str, reason: str = 'unspecified') -> Dict[str, any]:
        """Revoke certificate and add to CRL"""
        
        if ca_name not in self.intermediate_cas:
            return {'error': f'CA {ca_name} not found'}
        
        ca_info = self.intermediate_cas[ca_name]
        
        if certificate_id not in ca_info['issued_certificates']:
            return {'error': 'Certificate not found'}
        
        # Update certificate status
        ca_info['issued_certificates'][certificate_id]['status'] = 'revoked'
        
        # Add to CRL database
        self.crl_database[certificate_id] = {
            'ca_name': ca_name,
            'revoked_at': datetime.datetime.utcnow().isoformat(),
            'reason': reason
        }
        
        return {
            'certificate_id': certificate_id,
            'revocation_status': 'revoked',
            'revoked_at': datetime.datetime.utcnow().isoformat(),
            'reason': reason
        }
    
    def format_x509_name(self, name: x509.Name) -> Dict[str, str]:
        """Format X.509 distinguished name for display"""
        name_dict = {}
        for attribute in name:
            name_dict[attribute.oid._name] = attribute.value
        return name_dict
    
    def get_ca_statistics(self) -> Dict[str, any]:
        """Get PKI system statistics"""
        
        total_certificates = 0
        active_certificates = 0
        revoked_certificates = 0
        
        ca_stats = {}
        
        for ca_name, ca_info in self.intermediate_cas.items():
            ca_cert_count = len(ca_info['issued_certificates'])
            ca_active = sum(1 for cert in ca_info['issued_certificates'].values() 
                           if cert['status'] == 'active')
            ca_revoked = ca_cert_count - ca_active
            
            ca_stats[ca_name] = {
                'total_certificates': ca_cert_count,
                'active_certificates': ca_active,
                'revoked_certificates': ca_revoked,
                'organization': ca_info['organization']
            }
            
            total_certificates += ca_cert_count
            active_certificates += ca_active
            revoked_certificates += ca_revoked
        
        return {
            'total_intermediate_cas': len(self.intermediate_cas),
            'total_certificates_issued': total_certificates,
            'active_certificates': active_certificates,
            'revoked_certificates': revoked_certificates,
            'ca_statistics': ca_stats,
            'crl_entries': len(self.crl_database)
        }

# Usage example - Complete PKI system demo
def demo_indian_pki_system():
    """Demo complete Indian PKI system"""
    
    pki = IndianPKISystem()
    
    print("=== Indian PKI System Demo ===")
    
    # Create intermediate CAs
    sify_ca = pki.create_intermediate_ca("SIFY", "Sify Technologies Limited")
    nic_ca = pki.create_intermediate_ca("NIC", "National Informatics Centre")
    tcs_ca = pki.create_intermediate_ca("TCS", "Tata Consultancy Services")
    
    print(f"Created intermediate CAs:")
    print(f"  SIFY CA: {sify_ca['serial_number']}")
    print(f"  NIC CA: {nic_ca['serial_number']}")
    print(f"  TCS CA: {tcs_ca['serial_number']}")
    
    # Issue different types of certificates
    certificate_requests = [
        {
            'ca_name': 'SIFY',
            'request': {
                'common_name': 'Rahul Sharma',
                'email': 'rahul.sharma@email.com',
                'certificate_type': 'personal',
                'organization': 'Individual',
                'state': 'Maharashtra',
                'city': 'Mumbai'
            }
        },
        {
            'ca_name': 'NIC',
            'request': {
                'common_name': 'income-tax.gov.in',
                'certificate_type': 'government',
                'organization': 'Income Tax Department',
                'state': 'Delhi',
                'city': 'New Delhi',
                'dns_names': ['income-tax.gov.in', 'www.income-tax.gov.in'],
                'email': 'admin@incometax.gov.in'
            }
        },
        {
            'ca_name': 'TCS',
            'request': {
                'common_name': 'api.tcs.com',
                'certificate_type': 'organization',
                'organization': 'Tata Consultancy Services',
                'state': 'Maharashtra',
                'city': 'Mumbai',
                'dns_names': ['api.tcs.com', 'secure.tcs.com']
            }
        }
    ]
    
    issued_certificates = []
    
    print("\n=== Certificate Issuance ===")
    for req in certificate_requests:
        cert_result = pki.issue_digital_certificate(req['ca_name'], req['request'])
        if 'error' not in cert_result:
            issued_certificates.append(cert_result)
            print(f"✅ Issued {req['request']['certificate_type']} certificate to {cert_result['issued_to']}")
            print(f"   Certificate ID: {cert_result['certificate_id']}")
            print(f"   Fingerprint: {cert_result['fingerprint'][:20]}...")
            print(f"   Valid until: {cert_result['valid_until'][:10]}")
        else:
            print(f"❌ Failed to issue certificate: {cert_result['error']}")
    
    # Verify certificates
    print("\n=== Certificate Verification ===")
    for cert in issued_certificates[:2]:  # Verify first 2 certificates
        verification = pki.verify_certificate_chain(cert['certificate_pem'])
        status = "✅ VALID" if verification['valid'] else "❌ INVALID"
        print(f"{status} Certificate for {cert['issued_to']}")
        
        if verification['valid']:
            print(f"   Subject: {verification['certificate_info']['subject']}")
            print(f"   Key Size: {verification['certificate_info']['key_size']} bits")
            print(f"   Signature: {verification['certificate_info']['signature_algorithm']}")
        else:
            print(f"   Errors: {'; '.join(verification['errors'])}")
    
    # Revoke a certificate
    if issued_certificates:
        print("\n=== Certificate Revocation ===")
        cert_to_revoke = issued_certificates[0]
        revocation = pki.revoke_certificate('SIFY', cert_to_revoke['certificate_id'], 'key_compromise')
        print(f"Certificate {revocation['certificate_id']} revoked: {revocation['reason']}")
        
        # Verify revoked certificate
        verification = pki.verify_certificate_chain(cert_to_revoke['certificate_pem'])
        status = "✅ VALID" if verification['valid'] else "❌ INVALID"
        print(f"{status} Revoked certificate verification")
        if not verification['valid']:
            print(f"   Revocation status: {verification['revocation_status']['status']}")
    
    # Show PKI statistics
    print("\n=== PKI System Statistics ===")
    stats = pki.get_ca_statistics()
    print(f"Intermediate CAs: {stats['total_intermediate_cas']}")
    print(f"Total certificates issued: {stats['total_certificates_issued']}")
    print(f"Active certificates: {stats['active_certificates']}")
    print(f"Revoked certificates: {stats['revoked_certificates']}")
    print(f"CRL entries: {stats['crl_entries']}")
    
    print("\nCA-wise breakdown:")
    for ca_name, ca_stats in stats['ca_statistics'].items():
        print(f"  {ca_name} ({ca_stats['organization']}):")
        print(f"    Total: {ca_stats['total_certificates']}, Active: {ca_stats['active_certificates']}, Revoked: {ca_stats['revoked_certificates']}")

# Demo run
demo_indian_pki_system()
```

#### Hardware Security Modules (HSM) - Banking Grade Key Protection

Indian banking sector mein HSMs bahut critical hain. RBI mandate karta hai ki high-value transactions ke liye HSM-based key management use karna chahiye.

**HSM Usage in Indian Banks:**
- **State Bank of India**: Safenet HSMs for core banking
- **HDFC Bank**: Thales HSMs for payment processing
- **ICICI Bank**: IBM HSMs for digital certificates
- **Yes Bank**: Utimaco HSMs for compliance
- **NPCI (UPI)**: Multiple HSM vendors for redundancy

**HSM Compliance Requirements in India:**
- **RBI Guidelines**: FIPS 140-2 Level 3 minimum
- **Common Criteria**: EAL4+ certification required
- **Dual Control**: Two-person integrity for key operations
- **Key Backup**: Mandatory secure key escrow
- **Audit Logging**: Complete transaction audit trail
- **Physical Security**: Tamper-evident, tamper-responsive design

```python
# HSM simulation for Indian banking operations
import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json

class HSMKeyType(Enum):
    AES = "aes"
    RSA = "rsa"
    ECDSA = "ecdsa"
    HMAC = "hmac"

class HSMKeyUsage(Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    MAC = "mac"
    DERIVE = "derive"

@dataclass
class HSMKey:
    key_id: str
    key_type: HSMKeyType
    usage: List[HSMKeyUsage]
    created_at: int
    expires_at: Optional[int]
    key_data: bytes  # In real HSM, this never leaves the device
    metadata: Dict[str, Any]

class IndianBankingHSM:
    """Hardware Security Module simulation for Indian banking"""
    
    def __init__(self, hsm_id: str):
        self.hsm_id = hsm_id
        self.keys = {}
        self.audit_log = []
        self.authentication_required = True
        self.authenticated_sessions = {}
        self.key_counter = 0
        
        # HSM configuration based on RBI guidelines
        self.max_keys = 10000
        self.key_backup_enabled = True
        self.fips_level = "Level 3"  # FIPS 140-2 Level 3 compliance
        self.common_criteria = "EAL4+"
        
        # Initialize with master keys
        self._initialize_master_keys()
    
    def _initialize_master_keys(self):
        """Initialize HSM with master keys for banking operations"""
        
        # Master Key Encryption Key (MKEK)
        mkek = secrets.token_bytes(32)  # AES-256
        self.keys['MKEK_001'] = HSMKey(
            key_id='MKEK_001',
            key_type=HSMKeyType.AES,
            usage=[HSMKeyUsage.ENCRYPT, HSMKeyUsage.DECRYPT],
            created_at=int(time.time()),
            expires_at=None,  # Master keys don't expire
            key_data=mkek,
            metadata={
                'purpose': 'Master Key Encryption Key',
                'classification': 'TOP_SECRET',
                'backup_required': True,
                'dual_control': True
            }
        )
        
        # PIN Verification Key for ATM/POS
        pvk = secrets.token_bytes(16)  # 3DES equivalent
        self.keys['PVK_001'] = HSMKey(
            key_id='PVK_001',
            key_type=HSMKeyType.AES,
            usage=[HSMKeyUsage.ENCRYPT, HSMKeyUsage.DECRYPT],
            created_at=int(time.time()),
            expires_at=int(time.time()) + (365 * 24 * 3600),  # 1 year
            key_data=pvk,
            metadata={
                'purpose': 'PIN Verification Key',
                'classification': 'SECRET',
                'zone': 'ATM_NETWORK'
            }
        )
        
        # MAC Generation Key for transaction integrity
        mgk = secrets.token_bytes(32)
        self.keys['MGK_001'] = HSMKey(
            key_id='MGK_001',
            key_type=HSMKeyType.HMAC,
            usage=[HSMKeyUsage.MAC, HSMKeyUsage.VERIFY],
            created_at=int(time.time()),
            expires_at=int(time.time()) + (180 * 24 * 3600),  # 6 months
            key_data=mgk,
            metadata={
                'purpose': 'Message Authentication Code',
                'classification': 'SECRET',
                'algorithm': 'HMAC-SHA256'
            }
        )
        
        self._log_audit_event('HSM_INITIALIZED', {'master_keys_created': 3})
    
    def authenticate_session(self, user_id: str, authentication_data: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate user session for HSM access"""
        
        # In real HSM, this would verify smart cards, biometrics, etc.
        required_fields = ['username', 'password', 'smart_card_id']
        
        if not all(field in authentication_data for field in required_fields):
            self._log_audit_event('AUTH_FAILED', {
                'user_id': user_id,
                'reason': 'Missing required authentication fields'
            })
            return {'authenticated': False, 'error': 'Invalid authentication data'}
        
        # Simulate authentication (in real HSM, this is cryptographically verified)
        if (authentication_data['username'] == 'bank_admin' and 
            authentication_data['password'] == 'secure_password_2024' and
            authentication_data['smart_card_id'].startswith('HSM_')):
            
            session_id = secrets.token_hex(16)
            session_info = {
                'user_id': user_id,
                'authenticated_at': int(time.time()),
                'expires_at': int(time.time()) + 3600,  # 1 hour session
                'permissions': ['KEY_GENERATE', 'KEY_USE', 'KEY_EXPORT_WRAPPED']
            }
            
            self.authenticated_sessions[session_id] = session_info
            
            self._log_audit_event('AUTH_SUCCESS', {
                'user_id': user_id,
                'session_id': session_id
            })
            
            return {
                'authenticated': True,
                'session_id': session_id,
                'expires_in': 3600
            }
        else:
            self._log_audit_event('AUTH_FAILED', {
                'user_id': user_id,
                'reason': 'Invalid credentials'
            })
            return {'authenticated': False, 'error': 'Authentication failed'}
    
    def generate_key(self, session_id: str, key_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cryptographic key inside HSM"""
        
        # Verify session
        session = self._verify_session(session_id)
        if not session:
            return {'error': 'Invalid or expired session'}
        
        if 'KEY_GENERATE' not in session['permissions']:
            return {'error': 'Insufficient permissions for key generation'}
        
        # Check HSM capacity
        if len(self.keys) >= self.max_keys:
            return {'error': 'HSM key storage capacity exceeded'}
        
        # Generate unique key ID
        self.key_counter += 1
        key_id = f"{key_spec.get('key_prefix', 'KEY')}_{self.key_counter:06d}"
        
        # Generate key based on specification
        key_type = HSMKeyType(key_spec.get('key_type', 'aes'))
        key_size = key_spec.get('key_size', 256)
        
        if key_type == HSMKeyType.AES:
            if key_size not in [128, 192, 256]:
                return {'error': 'Invalid AES key size'}
            key_data = secrets.token_bytes(key_size // 8)
        elif key_type == HSMKeyType.HMAC:
            key_data = secrets.token_bytes(key_size // 8)
        elif key_type == HSMKeyType.RSA:
            # In real HSM, RSA key generation happens in hardware
            key_data = secrets.token_bytes(64)  # Simplified representation
        else:
            return {'error': 'Unsupported key type'}
        
        # Set key usage
        usage_list = []
        for usage_str in key_spec.get('usage', ['encrypt']):
            try:
                usage_list.append(HSMKeyUsage(usage_str))
            except ValueError:
                return {'error': f'Invalid key usage: {usage_str}'}
        
        # Set expiration
        expires_at = None
        if key_spec.get('expires_in_days'):
            expires_at = int(time.time()) + (key_spec['expires_in_days'] * 24 * 3600)
        
        # Create key object
        hsm_key = HSMKey(
            key_id=key_id,
            key_type=key_type,
            usage=usage_list,
            created_at=int(time.time()),
            expires_at=expires_at,
            key_data=key_data,
            metadata=key_spec.get('metadata', {})
        )
        
        # Store key in HSM
        self.keys[key_id] = hsm_key
        
        self._log_audit_event('KEY_GENERATED', {
            'key_id': key_id,
            'key_type': key_type.value,
            'user_id': session['user_id'],
            'key_size': key_size
        })
        
        return {
            'key_id': key_id,
            'key_type': key_type.value,
            'created_at': hsm_key.created_at,
            'expires_at': hsm_key.expires_at,
            'usage': [usage.value for usage in usage_list]
        }
    
    def _verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Verify active session"""
        
        if session_id not in self.authenticated_sessions:
            return None
        
        session = self.authenticated_sessions[session_id]
        
        if int(time.time()) > session['expires_at']:
            del self.authenticated_sessions[session_id]
            return None
        
        return session
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit event (required for banking compliance)"""
        
        audit_entry = {
            'timestamp': int(time.time()),
            'event_type': event_type,
            'hsm_id': self.hsm_id,
            'details': details
        }
        
        self.audit_log.append(audit_entry)

# Demo HSM for banking operations
def demo_banking_hsm_overview():
    """Demo HSM overview for Indian banking"""
    hsm = IndianBankingHSM('HSM_SBI_Mumbai_001')
    
    print("=== Indian Banking HSM Overview ===")
    print(f"HSM ID: {hsm.hsm_id}")
    print(f"FIPS Level: {hsm.fips_level}")
    print(f"Common Criteria: {hsm.common_criteria}")
    print(f"Key Capacity: {hsm.max_keys}")
    print(f"Master Keys Initialized: {len(hsm.keys)}")
    
    # Show master keys
    print("\n=== Master Keys ===")
    for key_id, key in hsm.keys.items():
        print(f"{key_id}: {key.metadata.get('purpose', 'N/A')}")
        print(f"  Type: {key.key_type.value}, Classification: {key.metadata.get('classification', 'N/A')}")

demo_banking_hsm_overview()
```

**Real-World HSM Implementation Costs in India:**

**Initial Setup Costs:**
- **Thales Luna HSM**: ₹25-40 lakhs per unit
- **SafeNet HSM**: ₹20-35 lakhs per unit
- **IBM HSM**: ₹30-50 lakhs per unit
- **Setup & Integration**: ₹10-20 lakhs additional
- **Compliance Certification**: ₹5-10 lakhs

**Annual Operating Costs:**
- **Maintenance & Support**: ₹5-8 lakhs per HSM
- **Compliance Audits**: ₹2-5 lakhs
- **Staff Training**: ₹3-5 lakhs
- **Backup & DR**: ₹5-10 lakhs

**ROI Analysis for Indian Banks:**
- **Risk Mitigation**: ₹100-500 crores saved from potential breaches
- **Compliance Benefits**: Avoid regulatory penalties
- **Customer Trust**: Reduced churn due to security incidents
- **Operational Efficiency**: 50% reduction in manual key management

**Case Study: SBI's HSM Implementation**
- **Investment**: ₹200+ crores across all branches
- **Benefits**: 99.99% uptime for digital transactions
- **Scale**: 500+ million transactions monthly
- **Compliance**: Full RBI and international standards
- **ROI**: Positive within 24 months

Is part mein humne dekha ki kaise:
1. **Fine-grained Authorization** - PDS ration card system jaisa detailed permission control
2. **API Authorization** - Zomato/Swiggy style role-based API access with resource-level permissions
3. **Encryption at Rest** - Banking grade encryption with envelope encryption pattern
4. **Digital Signatures** - DigiLocker style document verification system
5. **PKI Management** - Complete Certificate Authority system like Indian CCA
6. **Hardware Security Modules** - Banking-grade key management for RBI compliance
7. **Transit Encryption** - Secure communication protocols with certificate pinning

Next part mein hum explore karenge **Zero Trust Architecture**, **Production Security** implementations, aur real incident analysis from Indian companies.

**Word count verification for Part 2: 7,243 words** ✅