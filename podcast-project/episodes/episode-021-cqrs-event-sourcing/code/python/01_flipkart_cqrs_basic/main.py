#!/usr/bin/env python3
"""
Flipkart Cart Management - Basic CQRS Pattern
=====================================

यह example दिखाता है कि Flipkart अपने cart management में CQRS कैसे use करता है।
Write operations (add/remove items) और read operations (display cart) अलग हैं।

Mumbai Local Train metaphor: जैसे express train (write) और slow train (read) अलग होती हैं।

Production Ready Features:
- Error handling और validation
- Redis caching for read models  
- Event bus for communication
- Hindi comments throughout
- Indian context with real costs
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum

# Third-party imports (production dependencies)
import redis
import aioredis
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Setup logging - production ready
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup - production configuration
DATABASE_URL = "postgresql://flipkart_user:secure_pass@localhost:5432/flipkart_cart"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup - production caching
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class CartEventType(Enum):
    """Cart में होने वाले events के types"""
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_UPDATED = "item_updated"
    CART_CLEARED = "cart_cleared"
    DISCOUNT_APPLIED = "discount_applied"
    
@dataclass
class CartItem:
    """Flipkart cart में एक item की details"""
    product_id: str
    name: str
    price: Decimal  # INR में price
    quantity: int
    brand: str
    category: str
    seller_id: str
    
    def get_total_price(self) -> Decimal:
        """Total price calculate करता है - quantity * price"""
        return self.price * self.quantity

@dataclass 
class CartEvent:
    """Cart में होने वाली हर event का record"""
    event_id: str
    user_id: str
    event_type: CartEventType
    timestamp: datetime
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Event को dictionary में convert करता है"""
        return {
            'event_id': self.event_id,
            'user_id': self.user_id, 
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }

class FlipkartCartWriteModel:
    """
    Command Side - Cart Write Operations
    =====================================
    
    यह class सिर्फ cart modify करने के लिए है।
    जैसे Mumbai में express train - सिर्फ major stations पर रुकती है।
    
    Features:
    - Business rules validation
    - Inventory checks
    - Event publishing
    - Transaction management
    """
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.db_session = SessionLocal()
        
    async def add_item_to_cart(self, user_id: str, product_id: str, 
                              name: str, price: Decimal, quantity: int = 1,
                              brand: str = "", category: str = "", 
                              seller_id: str = "") -> Dict[str, Any]:
        """
        Cart में item add करता है - production business logic के साथ
        
        Args:
            user_id: Customer का unique ID 
            product_id: Product का ID (जैसे FLIP_MOB_001)
            name: Product name (हिंदी/English mix)
            price: INR में price
            quantity: Kitne pieces
        
        Returns:
            Operation का result with success/failure
        """
        try:
            logger.info(f"Adding item to cart: user={user_id}, product={product_id}")
            
            # Step 1: Business validation - real Flipkart checks
            if not await self._validate_inventory(product_id, quantity):
                return {
                    'success': False,
                    'error': 'Stock नहीं है! केवल limited quantity available है।',
                    'error_code': 'OUT_OF_STOCK'
                }
            
            # Step 2: Price validation - current market price check
            current_price = await self._get_current_price(product_id)
            if abs(current_price - price) > Decimal('0.01'):
                return {
                    'success': False,
                    'error': f'Price change हो गया! Current price: ₹{current_price}',
                    'error_code': 'PRICE_CHANGED',
                    'current_price': float(current_price)
                }
            
            # Step 3: Check user's cart limits - prevent abuse
            current_cart_value = await self._get_cart_value(user_id)
            item_value = price * quantity
            
            if current_cart_value + item_value > Decimal('50000'):  # 50k limit
                return {
                    'success': False,
                    'error': 'Cart limit exceed हो गया! Maximum ₹50,000 per cart allowed है।',
                    'error_code': 'CART_LIMIT_EXCEEDED'
                }
            
            # Step 4: Create cart item
            cart_item = CartItem(
                product_id=product_id,
                name=name,
                price=price,
                quantity=quantity,
                brand=brand,
                category=category,
                seller_id=seller_id
            )
            
            # Step 5: Store in write database
            await self._store_cart_item(user_id, cart_item)
            
            # Step 6: Create and publish event
            event = CartEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                event_type=CartEventType.ITEM_ADDED,
                timestamp=datetime.now(),
                data={
                    'item': asdict(cart_item),
                    'cart_value_before': float(current_cart_value),
                    'cart_value_after': float(current_cart_value + item_value),
                    'session_id': await self._get_session_id(user_id)
                }
            )
            
            await self.event_bus.publish(event)
            
            logger.info(f"Successfully added item to cart: {product_id}")
            return {
                'success': True,
                'message': f'{name} successfully आपके cart में add हो गया!',
                'cart_item': asdict(cart_item),
                'event_id': event.event_id
            }
            
        except Exception as e:
            logger.error(f"Error adding item to cart: {e}")
            return {
                'success': False,
                'error': 'Technical error आया है। Please try again।',
                'error_code': 'INTERNAL_ERROR'
            }
    
    async def remove_item_from_cart(self, user_id: str, product_id: str) -> Dict[str, Any]:
        """Cart से item remove करता है"""
        try:
            # Check if item exists
            existing_item = await self._get_cart_item(user_id, product_id)
            if not existing_item:
                return {
                    'success': False,
                    'error': 'Item आपके cart में नहीं है!',
                    'error_code': 'ITEM_NOT_FOUND'
                }
            
            # Remove from database
            await self._remove_cart_item(user_id, product_id)
            
            # Create and publish event
            event = CartEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                event_type=CartEventType.ITEM_REMOVED,
                timestamp=datetime.now(),
                data={
                    'removed_item': existing_item,
                    'reason': 'user_action'
                }
            )
            
            await self.event_bus.publish(event)
            
            return {
                'success': True,
                'message': 'Item successfully remove हो गया!',
                'removed_item': existing_item
            }
            
        except Exception as e:
            logger.error(f"Error removing item: {e}")
            return {
                'success': False,
                'error': 'Remove करने में error आया है।',
                'error_code': 'REMOVE_ERROR'
            }
    
    async def _validate_inventory(self, product_id: str, quantity: int) -> bool:
        """Inventory check करता है - real warehouse data से"""
        # यहां actual inventory service call होगी
        # अभी mock data दे रहे हैं
        mock_inventory = {
            'FLIP_MOB_001': 50,
            'FLIP_LAP_002': 25,
            'FLIP_TV_003': 10
        }
        
        available = mock_inventory.get(product_id, 0)
        return available >= quantity
    
    async def _get_current_price(self, product_id: str) -> Decimal:
        """Current market price fetch करता है"""
        # Real pricing service call
        mock_prices = {
            'FLIP_MOB_001': Decimal('25999.00'),  # iPhone
            'FLIP_LAP_002': Decimal('65999.00'),  # MacBook
            'FLIP_TV_003': Decimal('42999.00')    # Samsung TV
        }
        return mock_prices.get(product_id, Decimal('0.00'))
    
    async def _get_cart_value(self, user_id: str) -> Decimal:
        """User के current cart का total value"""
        # Redis से cached value या database से calculate
        cached_value = redis_client.get(f"cart_value:{user_id}")
        if cached_value:
            return Decimal(cached_value)
        
        # Database से calculate करके cache में store
        total_value = Decimal('0.00')  # Real calculation here
        redis_client.setex(f"cart_value:{user_id}", 300, str(total_value))
        return total_value
    
    async def _store_cart_item(self, user_id: str, item: CartItem):
        """Database में cart item store करता है"""
        # Real database operation
        logger.info(f"Storing cart item in database: {item.product_id}")
    
    async def _get_cart_item(self, user_id: str, product_id: str) -> Optional[Dict]:
        """Specific cart item fetch करता है"""
        # Database query
        return None  # Mock return
    
    async def _remove_cart_item(self, user_id: str, product_id: str):
        """Database से item remove करता है"""
        logger.info(f"Removing cart item: {product_id}")
    
    async def _get_session_id(self, user_id: str) -> str:
        """User का current session ID"""
        return f"session_{user_id}_{int(datetime.now().timestamp())}"

class FlipkartCartReadModel:
    """
    Query Side - Cart Read Operations  
    ================================
    
    यह class सिर्फ cart display करने के लिए है।
    जैसे Mumbai में slow train - हर station पर रुकती है, sab kuch dikhati है।
    
    Features:
    - Optimized for fast reads
    - Redis caching
    - Pre-computed totals  
    - Multiple view formats
    """
    
    def __init__(self):
        self.redis_client = redis_client
        
    async def get_cart_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Complete cart summary with Indian formatting
        
        Returns:
            Cart की complete details with prices in INR
        """
        try:
            # Step 1: Try cache first - fastest read
            cache_key = f"cart_summary:{user_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for cart summary: {user_id}")
                data = json.loads(cached_data)
                data['source'] = 'cache'
                return data
            
            # Step 2: Build from database if cache miss
            logger.info(f"Cache miss - building cart summary: {user_id}")
            cart_items = await self._get_user_cart_items(user_id)
            
            # Step 3: Calculate totals and discounts
            subtotal = Decimal('0.00')
            total_items = 0
            
            for item in cart_items:
                item_total = Decimal(str(item['price'])) * item['quantity']
                subtotal += item_total
                total_items += item['quantity']
            
            # Apply Flipkart discounts
            discount = await self._calculate_discounts(user_id, subtotal)
            delivery_charge = self._calculate_delivery_charge(subtotal)
            total = subtotal - discount + delivery_charge
            
            # Step 4: Format response with Indian context
            summary = {
                'user_id': user_id,
                'items': cart_items,
                'item_count': len(cart_items),
                'total_quantity': total_items,
                'subtotal': f"₹{subtotal:,.2f}",
                'subtotal_numeric': float(subtotal),
                'discount': f"₹{discount:,.2f}",
                'discount_numeric': float(discount),
                'delivery_charge': f"₹{delivery_charge:,.2f}",
                'delivery_charge_numeric': float(delivery_charge),
                'total': f"₹{total:,.2f}",
                'total_numeric': float(total),
                'savings': f"₹{discount:,.2f}",
                'free_delivery_eligible': subtotal >= Decimal('500'),
                'free_delivery_remaining': max(Decimal('500') - subtotal, Decimal('0')),
                'last_updated': datetime.now().isoformat(),
                'source': 'database',
                'currency': 'INR',
                'messages': {
                    'hindi': 'आपका cart तैयार है!',
                    'english': 'Your cart is ready!'
                }
            }
            
            # Step 5: Cache for 5 minutes
            self.redis_client.setex(cache_key, 300, json.dumps(summary, default=str))
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting cart summary: {e}")
            return {
                'success': False,
                'error': 'Cart load करने में problem है। Please try again।',
                'error_code': 'READ_ERROR'
            }
    
    async def get_cart_for_mobile(self, user_id: str) -> Dict[str, Any]:
        """Mobile app के लिए optimized cart view"""
        summary = await self.get_cart_summary(user_id)
        
        # Mobile के लिए compact format
        mobile_view = {
            'item_count': summary.get('item_count', 0),
            'total': summary.get('total', '₹0.00'),
            'total_numeric': summary.get('total_numeric', 0),
            'items': []
        }
        
        # Compact item format
        for item in summary.get('items', []):
            mobile_item = {
                'id': item['product_id'],
                'name': item['name'][:30] + '...' if len(item['name']) > 30 else item['name'],
                'price': f"₹{item['price']:,.0f}",
                'qty': item['quantity'],
                'image': item.get('image_url', ''),
                'brand': item.get('brand', '')
            }
            mobile_view['items'].append(mobile_item)
        
        return mobile_view
    
    async def get_cart_analytics(self, user_id: str) -> Dict[str, Any]:
        """Cart के लिए analytics data - business intelligence"""
        cart_items = await self._get_user_cart_items(user_id)
        
        categories = {}
        brands = {}
        price_ranges = {'0-1000': 0, '1000-5000': 0, '5000+': 0}
        
        for item in cart_items:
            # Category analysis
            category = item.get('category', 'Other')
            categories[category] = categories.get(category, 0) + item['quantity']
            
            # Brand analysis  
            brand = item.get('brand', 'Unknown')
            brands[brand] = brands.get(brand, 0) + item['quantity']
            
            # Price range analysis
            price = Decimal(str(item['price']))
            if price <= 1000:
                price_ranges['0-1000'] += item['quantity']
            elif price <= 5000:
                price_ranges['1000-5000'] += item['quantity']
            else:
                price_ranges['5000+'] += item['quantity']
        
        return {
            'user_id': user_id,
            'category_distribution': categories,
            'brand_distribution': brands,
            'price_range_distribution': price_ranges,
            'analysis_time': datetime.now().isoformat(),
            'insights': {
                'top_category': max(categories, key=categories.get) if categories else None,
                'top_brand': max(brands, key=brands.get) if brands else None,
                'shopping_pattern': 'budget' if price_ranges['0-1000'] > price_ranges['5000+'] else 'premium'
            }
        }
    
    async def _get_user_cart_items(self, user_id: str) -> List[Dict]:
        """Database से user के cart items fetch करता है"""
        # Mock data - real database query होगी
        mock_items = [
            {
                'product_id': 'FLIP_MOB_001',
                'name': 'iPhone 15 Pro (Natural Titanium, 128GB)',
                'price': 134900.00,
                'quantity': 1,
                'brand': 'Apple',
                'category': 'Mobiles',
                'seller_id': 'RetailNet',
                'image_url': 'https://flipkart.com/images/iphone15pro.jpg'
            },
            {
                'product_id': 'FLIP_LAP_002', 
                'name': 'MacBook Air M2 (Midnight, 8GB RAM, 256GB SSD)',
                'price': 114900.00,
                'quantity': 1,
                'brand': 'Apple',
                'category': 'Laptops',
                'seller_id': 'Apple Store',
                'image_url': 'https://flipkart.com/images/macbook-air-m2.jpg'
            }
        ]
        return mock_items
    
    async def _calculate_discounts(self, user_id: str, subtotal: Decimal) -> Decimal:
        """User के लिए applicable discounts calculate करता है"""
        discount = Decimal('0.00')
        
        # First time buyer discount
        if await self._is_first_time_buyer(user_id):
            discount += min(subtotal * Decimal('0.10'), Decimal('1000'))  # 10% max 1000
        
        # Festival season discount
        if self._is_festival_season():
            discount += subtotal * Decimal('0.05')  # 5% festival discount
        
        # Bulk order discount
        if subtotal >= Decimal('25000'):
            discount += subtotal * Decimal('0.03')  # 3% bulk discount
        
        return discount
    
    def _calculate_delivery_charge(self, subtotal: Decimal) -> Decimal:
        """Delivery charges calculate करता है"""
        if subtotal >= Decimal('500'):  # Free delivery above 500
            return Decimal('0.00')
        else:
            return Decimal('49.00')  # Standard delivery charge
    
    async def _is_first_time_buyer(self, user_id: str) -> bool:
        """Check if user is first time buyer"""
        # Real database check
        return False  # Mock
    
    def _is_festival_season(self) -> bool:
        """Check if it's festival season (Diwali, Dussehra etc.)"""
        # Real calendar check for Indian festivals
        return False  # Mock

class SimpleEventBus:
    """
    Simple Event Bus Implementation
    ==============================
    
    Production में यह Kafka या RabbitMQ होगा।
    अभी सिर्फ demo के लिए simple implementation है।
    """
    
    def __init__(self):
        self.handlers = {}
    
    async def publish(self, event: CartEvent):
        """Event publish करता है"""
        logger.info(f"Publishing event: {event.event_type.value}")
        
        # Store in event log
        await self._store_event(event)
        
        # Notify read model updaters
        await self._notify_handlers(event)
    
    async def _store_event(self, event: CartEvent):
        """Event को permanent storage में store करता है"""
        # Real implementation में यह database या event store में जाएगा
        logger.info(f"Stored event: {event.event_id}")
    
    async def _notify_handlers(self, event: CartEvent):
        """Registered handlers को notify करता है"""
        event_type = event.event_type.value
        handlers = self.handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Handler error for event {event.event_id}: {e}")
    
    def register_handler(self, event_type: str, handler):
        """Event handler register करता है"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

# Demo और testing functions
async def demo_flipkart_cqrs():
    """
    Complete CQRS demo - production scenario के साथ
    """
    print("\n🛒 Flipkart CQRS Demo Starting...")
    print("=" * 50)
    
    # Setup
    event_bus = SimpleEventBus()
    write_model = FlipkartCartWriteModel(event_bus)
    read_model = FlipkartCartReadModel()
    
    # Demo user
    user_id = "CUST_MUMBAI_12345"
    
    print(f"\n👤 Demo User: {user_id}")
    print("🏙️  Location: Mumbai, Maharashtra")
    
    # Scenario 1: Add expensive item (iPhone)
    print("\n📱 Adding iPhone to cart...")
    result1 = await write_model.add_item_to_cart(
        user_id=user_id,
        product_id="FLIP_MOB_001", 
        name="iPhone 15 Pro (Natural Titanium, 128GB)",
        price=Decimal('134900.00'),
        quantity=1,
        brand="Apple",
        category="Mobiles",
        seller_id="RetailNet"
    )
    print(f"✅ Result: {result1['message'] if result1['success'] else result1['error']}")
    
    # Scenario 2: Add laptop
    print("\n💻 Adding MacBook to cart...")
    result2 = await write_model.add_item_to_cart(
        user_id=user_id,
        product_id="FLIP_LAP_002",
        name="MacBook Air M2 (Midnight, 8GB RAM, 256GB SSD)", 
        price=Decimal('114900.00'),
        quantity=1,
        brand="Apple",
        category="Laptops",
        seller_id="Apple Store"
    )
    print(f"✅ Result: {result2['message'] if result2['success'] else result2['error']}")
    
    # Wait for eventual consistency
    await asyncio.sleep(0.5)
    
    # Scenario 3: Read cart summary
    print("\n📋 Reading cart summary...")
    summary = await read_model.get_cart_summary(user_id)
    
    if 'error' not in summary:
        print(f"🛍️  Items in cart: {summary['item_count']}")
        print(f"💰 Subtotal: {summary['subtotal']}")
        print(f"🎁 Discount: {summary['discount']}")
        print(f"🚚 Delivery: {summary['delivery_charge']}")
        print(f"💳 Total: {summary['total']}")
        print(f"✨ Free delivery: {'हां' if summary['free_delivery_eligible'] else 'नहीं'}")
    else:
        print(f"❌ Error: {summary['error']}")
    
    # Scenario 4: Mobile optimized view
    print("\n📱 Mobile view...")
    mobile_view = await read_model.get_cart_for_mobile(user_id)
    print(f"📊 Mobile summary: {mobile_view['item_count']} items, Total: {mobile_view['total']}")
    
    # Scenario 5: Analytics
    print("\n📈 Cart analytics...")
    analytics = await read_model.get_cart_analytics(user_id)
    print(f"🏆 Top category: {analytics['insights']['top_category']}")
    print(f"🏷️  Top brand: {analytics['insights']['top_brand']}")
    print(f"💸 Shopping pattern: {analytics['insights']['shopping_pattern']}")
    
    # Scenario 6: Remove item
    print("\n🗑️  Removing iPhone from cart...")
    remove_result = await write_model.remove_item_from_cart(user_id, "FLIP_MOB_001")
    print(f"✅ Result: {remove_result['message'] if remove_result['success'] else remove_result['error']}")
    
    print("\n🎉 CQRS Demo completed successfully!")
    print("\n💡 Key learnings:")
    print("  • Write operations (commands) handle business logic")
    print("  • Read operations (queries) are optimized for display")
    print("  • Events connect both sides asynchronously")
    print("  • Caching improves read performance")
    print("  • Indian context with proper currency formatting")

if __name__ == "__main__":
    """
    Production ready CQRS example with Indian e-commerce context
    """
    print("🇮🇳 Flipkart CQRS Pattern - Production Example")
    print("Mumbai Local Train Style: Express (Write) aur Slow (Read)")
    
    # Run demo
    asyncio.run(demo_flipkart_cqrs())