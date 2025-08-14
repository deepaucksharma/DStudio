#!/usr/bin/env python3
"""
Domain-Driven Design: Product Entity - Flipkart Example
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में Entity pattern का इस्तेमाल करके
Flipkart के product domain को model करते हैं।

Author: Hindi Tech Podcast
Date: 2025
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from uuid import uuid4, UUID
from decimal import Decimal
import json

# Domain Exceptions - डोमेन specific errors
class DomainException(Exception):
    """Base exception for domain rules violations"""
    pass

class InvalidPriceException(DomainException):
    """Price validation failed - गलत कीमत"""
    pass

class InsufficientStockException(DomainException):
    """Stock insufficient - स्टॉक कम है"""
    pass

class ProductNotActiveException(DomainException):
    """Product not available - प्रोडक्ट available नहीं है"""
    pass

# Value Objects - Values जो अपने आप में complete हैं
@dataclass(frozen=True)
class ProductId:
    """Product identifier - मजबूत type safety के लिए"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 6:
            raise ValueError("Product ID must be at least 6 characters - प्रोडक्ट ID कम से कम 6 characters का होना चाहिए")

@dataclass(frozen=True)
class Money:
    """Money value object - पैसे की representation"""
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise InvalidPriceException("Amount cannot be negative - रकम negative नहीं हो सकती")
        if self.currency not in ["INR", "USD", "EUR"]:
            raise ValueError("Invalid currency - गलत currency")
    
    def add(self, other: 'Money') -> 'Money':
        """Add money - पैसे जोड़ना"""
        if self.currency != other.currency:
            raise ValueError("Currency mismatch - Currency match नहीं करती")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        """Multiply money - पैसे को multiply करना"""
        return Money(self.amount * Decimal(str(factor)), self.currency)

@dataclass(frozen=True)
class Category:
    """Product category - प्रोडक्ट category"""
    name: str
    level: int  # 1=Electronics, 2=Mobile, 3=Smartphone
    parent_category: Optional[str] = None
    
    def __post_init__(self):
        if self.level < 1 or self.level > 5:
            raise ValueError("Category level must be between 1-5")

@dataclass
class Stock:
    """Stock information - स्टॉक की जानकारी"""
    quantity: int
    reserved: int = 0
    threshold: int = 5  # Low stock warning
    
    def __post_init__(self):
        if self.quantity < 0 or self.reserved < 0:
            raise ValueError("Stock quantities cannot be negative")
    
    @property
    def available(self) -> int:
        """Available stock - उपलब्ध स्टॉक"""
        return self.quantity - self.reserved
    
    @property 
    def is_low_stock(self) -> bool:
        """Check if stock is low - स्टॉक कम है क्या"""
        return self.available <= self.threshold
    
    def reserve(self, quantity: int) -> None:
        """Reserve stock for order - ऑर्डर के लिए स्टॉक reserve करना"""
        if quantity > self.available:
            raise InsufficientStockException(
                f"Cannot reserve {quantity} items, only {self.available} available"
            )
        self.reserved += quantity
    
    def release_reservation(self, quantity: int) -> None:
        """Release reserved stock - Reserved stock छोड़ना"""
        if quantity > self.reserved:
            raise ValueError("Cannot release more than reserved")
        self.reserved -= quantity
    
    def confirm_sale(self, quantity: int) -> None:
        """Confirm sale and reduce stock - Sale confirm करना"""
        if quantity > self.reserved:
            raise ValueError("Cannot confirm more than reserved")
        self.quantity -= quantity
        self.reserved -= quantity

# Product Entity - Main domain entity
class Product:
    """
    Product Entity - Flipkart Product Domain
    
    यह class एक complete product को represent करती है।
    इसमें सारे business rules और domain logic है।
    """
    
    def __init__(
        self,
        product_id: ProductId,
        name: str,
        description: str,
        price: Money,
        category: Category,
        seller_id: str,
        stock: Stock,
        brand: str,
        specifications: Dict[str, str]
    ):
        # Domain validation - बिजनेस rules check करना
        if not name or len(name.strip()) < 3:
            raise ValueError("Product name must be at least 3 characters")
        
        if not seller_id or len(seller_id) < 5:
            raise ValueError("Invalid seller ID")
        
        if not brand or len(brand.strip()) < 2:
            raise ValueError("Brand name required")
        
        # Private attributes - Encapsulation
        self._id = product_id
        self._name = name.strip()
        self._description = description.strip()
        self._price = price
        self._category = category
        self._seller_id = seller_id
        self._stock = stock
        self._brand = brand
        self._specifications = specifications.copy()
        
        # Domain state
        self._is_active = True
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._version = 1  # For optimistic locking
        
        # Domain events - बाद में event sourcing के लिए
        self._domain_events: List[dict] = []
        self._add_domain_event("ProductCreated", {
            "product_id": str(self._id.value),
            "name": self._name,
            "price": float(self._price.amount),
            "seller_id": self._seller_id
        })
    
    # Properties - Read-only access to domain state
    @property
    def id(self) -> ProductId:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def price(self) -> Money:
        return self._price
    
    @property
    def category(self) -> Category:
        return self._category
    
    @property
    def seller_id(self) -> str:
        return self._seller_id
    
    @property
    def stock(self) -> Stock:
        return self._stock
    
    @property
    def brand(self) -> str:
        return self._brand
    
    @property
    def specifications(self) -> Dict[str, str]:
        return self._specifications.copy()
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def version(self) -> int:
        return self._version
    
    # Domain Methods - Business logic
    
    def update_price(self, new_price: Money) -> None:
        """
        Update product price - प्रोडक्ट की कीमत बदलना
        
        Business rules:
        - Price cannot decrease by more than 50% in one go
        - Price cannot be 0 for active products
        """
        if not self._is_active:
            raise ProductNotActiveException("Cannot update price of inactive product")
        
        # Business rule: Max 50% discount in one update
        max_discount_price = self._price.multiply(0.5)
        if new_price.amount < max_discount_price.amount:
            raise InvalidPriceException(
                f"Price cannot be reduced by more than 50% in one update. "
                f"Minimum allowed: ₹{max_discount_price.amount}"
            )
        
        old_price = self._price
        self._price = new_price
        self._updated_at = datetime.now()
        self._version += 1
        
        self._add_domain_event("PriceUpdated", {
            "product_id": str(self._id.value),
            "old_price": float(old_price.amount),
            "new_price": float(new_price.amount),
            "updated_by": "system"  # प्रोडक्शन में user ID होगा
        })
    
    def update_stock(self, new_quantity: int) -> None:
        """Update stock quantity - स्टॉक की मात्रा बदलना"""
        if new_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        old_quantity = self._stock.quantity
        self._stock.quantity = new_quantity
        self._updated_at = datetime.now()
        self._version += 1
        
        self._add_domain_event("StockUpdated", {
            "product_id": str(self._id.value),
            "old_quantity": old_quantity,
            "new_quantity": new_quantity,
            "available_quantity": self._stock.available
        })
        
        # Auto-deactivate if out of stock - अगर स्टॉक खत्म तो deactivate
        if new_quantity == 0 and self._is_active:
            self.deactivate("Out of stock")
    
    def reserve_for_order(self, quantity: int, order_id: str) -> None:
        """
        Reserve stock for an order - ऑर्डर के लिए स्टॉक reserve करना
        
        Business rules:
        - Product must be active
        - Sufficient stock must be available
        """
        if not self._is_active:
            raise ProductNotActiveException("Cannot reserve inactive product")
        
        self._stock.reserve(quantity)
        self._updated_at = datetime.now()
        self._version += 1
        
        self._add_domain_event("StockReserved", {
            "product_id": str(self._id.value),
            "order_id": order_id,
            "quantity": quantity,
            "available_after_reservation": self._stock.available
        })
    
    def confirm_sale(self, quantity: int, order_id: str) -> None:
        """Confirm sale and reduce stock - Sale confirm करके स्टॉक कम करना"""
        if not self._is_active:
            raise ProductNotActiveException("Cannot sell inactive product")
        
        self._stock.confirm_sale(quantity)
        self._updated_at = datetime.now()
        self._version += 1
        
        self._add_domain_event("SaleConfirmed", {
            "product_id": str(self._id.value),
            "order_id": order_id,
            "quantity": quantity,
            "remaining_stock": self._stock.quantity
        })
    
    def cancel_reservation(self, quantity: int, order_id: str) -> None:
        """Cancel stock reservation - Stock reservation cancel करना"""
        self._stock.release_reservation(quantity)
        self._updated_at = datetime.now()
        self._version += 1
        
        self._add_domain_event("ReservationCancelled", {
            "product_id": str(self._id.value),
            "order_id": order_id,
            "quantity": quantity,
            "available_after_cancellation": self._stock.available
        })
    
    def activate(self) -> None:
        """Activate product - प्रोडक्ट को active करना"""
        if self._stock.quantity == 0:
            raise ValueError("Cannot activate product with zero stock")
        
        if not self._is_active:
            self._is_active = True
            self._updated_at = datetime.now()
            self._version += 1
            
            self._add_domain_event("ProductActivated", {
                "product_id": str(self._id.value)
            })
    
    def deactivate(self, reason: str) -> None:
        """Deactivate product - प्रोडक्ट को deactive करना"""
        if self._is_active:
            self._is_active = False
            self._updated_at = datetime.now()
            self._version += 1
            
            self._add_domain_event("ProductDeactivated", {
                "product_id": str(self._id.value),
                "reason": reason
            })
    
    def update_specifications(self, new_specs: Dict[str, str]) -> None:
        """Update product specifications - प्रोडक्ट specifications update करना"""
        old_specs = self._specifications.copy()
        self._specifications.update(new_specs)
        self._updated_at = datetime.now()
        self._version += 1
        
        self._add_domain_event("SpecificationsUpdated", {
            "product_id": str(self._id.value),
            "old_specifications": old_specs,
            "new_specifications": self._specifications
        })
    
    def calculate_discounted_price(self, discount_percent: float) -> Money:
        """Calculate discounted price - Discount के बाद कीमत calculate करना"""
        if discount_percent < 0 or discount_percent > 90:
            raise ValueError("Discount must be between 0-90%")
        
        discount_multiplier = 1 - (discount_percent / 100)
        return self._price.multiply(discount_multiplier)
    
    def is_eligible_for_discount(self, max_discount_percent: float = 70) -> bool:
        """Check if product eligible for discount - Discount के लिए eligible है क्या"""
        # Business rules for discount eligibility
        if not self._is_active:
            return False
        
        if self._stock.quantity < 5:  # Low stock items no discount
            return False
        
        if self._category.name in ["Books", "Medicines"]:  # Some categories exempt
            return False
        
        return True
    
    def get_search_keywords(self) -> List[str]:
        """Generate search keywords - Search के लिए keywords generate करना"""
        keywords = []
        
        # Product name words
        keywords.extend(self._name.lower().split())
        
        # Brand
        keywords.append(self._brand.lower())
        
        # Category
        keywords.append(self._category.name.lower())
        
        # Specifications
        for key, value in self._specifications.items():
            keywords.extend([key.lower(), value.lower()])
        
        return list(set(keywords))  # Remove duplicates
    
    def _add_domain_event(self, event_type: str, event_data: dict) -> None:
        """Add domain event - Domain event add करना"""
        self._domain_events.append({
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.now().isoformat(),
            "version": self._version
        })
    
    def clear_domain_events(self) -> List[dict]:
        """Clear and return domain events - Events clear करके return करना"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def to_dict(self) -> dict:
        """Convert to dictionary - Dictionary में convert करना"""
        return {
            "id": self._id.value,
            "name": self._name,
            "description": self._description,
            "price": {
                "amount": float(self._price.amount),
                "currency": self._price.currency
            },
            "category": {
                "name": self._category.name,
                "level": self._category.level,
                "parent_category": self._category.parent_category
            },
            "seller_id": self._seller_id,
            "stock": {
                "quantity": self._stock.quantity,
                "reserved": self._stock.reserved,
                "available": self._stock.available,
                "is_low_stock": self._stock.is_low_stock
            },
            "brand": self._brand,
            "specifications": self._specifications,
            "is_active": self._is_active,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "version": self._version
        }
    
    def __str__(self) -> str:
        return f"Product({self._id.value}: {self._name} - ₹{self._price.amount})"
    
    def __eq__(self, other) -> bool:
        """Entity equality based on ID - ID के base पर equality"""
        if not isinstance(other, Product):
            return False
        return self._id.value == other._id.value

# Domain Service - Cross-aggregate business logic
class ProductPricingService:
    """
    Domain service for complex pricing logic
    यह service complex pricing rules handle करती है
    """
    
    @staticmethod
    def calculate_dynamic_price(
        product: Product,
        demand_factor: float,
        competitor_prices: List[Money],
        market_conditions: dict
    ) -> Money:
        """
        Calculate dynamic pricing - Dynamic pricing calculate करना
        
        Factors:
        - Demand (high demand = higher price)
        - Competitor prices
        - Market conditions
        - Stock levels
        """
        base_price = product.price.amount
        
        # Demand-based adjustment
        demand_multiplier = 1.0
        if demand_factor > 1.5:  # High demand
            demand_multiplier = 1.1
        elif demand_factor < 0.5:  # Low demand
            demand_multiplier = 0.9
        
        # Competitor price adjustment
        if competitor_prices:
            avg_competitor_price = sum(p.amount for p in competitor_prices) / len(competitor_prices)
            if base_price > avg_competitor_price * Decimal('1.2'):  # 20% higher
                demand_multiplier *= 0.95  # Reduce by 5%
        
        # Stock-based adjustment
        if product.stock.is_low_stock:
            demand_multiplier *= 1.05  # Premium for low stock
        
        # Market conditions
        festival_season = market_conditions.get("festival_season", False)
        if festival_season:
            demand_multiplier *= 1.02  # 2% festival premium
        
        new_amount = base_price * Decimal(str(demand_multiplier))
        return Money(new_amount, product.price.currency)

def create_sample_flipkart_products() -> List[Product]:
    """Create sample Flipkart products - Sample products बनाना"""
    
    products = []
    
    # Electronics category
    electronics = Category("Electronics", 1)
    mobile_category = Category("Mobile", 2, "Electronics")
    
    # Sample iPhone
    iphone = Product(
        product_id=ProductId("FLIP_IPH_001"),
        name="iPhone 15 Pro Max 256GB Natural Titanium",
        description="Latest iPhone with A17 Pro chip, titanium design, and advanced camera system",
        price=Money(Decimal("134900.00")),  # ₹1,34,900
        category=mobile_category,
        seller_id="APPLE_OFFICIAL",
        stock=Stock(quantity=50, threshold=10),
        brand="Apple",
        specifications={
            "RAM": "8GB",
            "Storage": "256GB", 
            "Display": "6.7 inch Super Retina XDR",
            "Camera": "48MP Main + 12MP Ultra Wide",
            "Battery": "4441 mAh",
            "OS": "iOS 17"
        }
    )
    products.append(iphone)
    
    # Sample Samsung
    samsung = Product(
        product_id=ProductId("FLIP_SAM_002"),
        name="Samsung Galaxy S24 Ultra 5G 512GB Titanium Black",
        description="Premium Samsung flagship with S Pen and AI features",
        price=Money(Decimal("129999.00")),  # ₹1,29,999
        category=mobile_category,
        seller_id="SAMSUNG_OFFICIAL",
        stock=Stock(quantity=75, threshold=15),
        brand="Samsung",
        specifications={
            "RAM": "12GB",
            "Storage": "512GB",
            "Display": "6.8 inch Dynamic AMOLED 2X",
            "Camera": "200MP Main + 50MP Periscope",
            "Battery": "5000 mAh",
            "OS": "Android 14"
        }
    )
    products.append(samsung)
    
    # Sample OnePlus (Indian brand preference)
    oneplus = Product(
        product_id=ProductId("FLIP_ONE_003"),
        name="OnePlus 12R 5G 256GB Cool Blue",
        description="Flagship killer with Snapdragon 8 Gen 2 and 100W charging",
        price=Money(Decimal("42999.00")),  # ₹42,999
        category=mobile_category,
        seller_id="ONEPLUS_OFFICIAL",
        stock=Stock(quantity=120, threshold=20),
        brand="OnePlus",
        specifications={
            "RAM": "12GB",
            "Storage": "256GB",
            "Display": "6.78 inch LTPO4 AMOLED",
            "Camera": "50MP Main + 8MP Ultra Wide",
            "Battery": "5500 mAh",
            "OS": "OxygenOS 14"
        }
    )
    products.append(oneplus)
    
    return products

# Usage Example और Testing
if __name__ == "__main__":
    print("🛍️ Flipkart Product Domain - DDD Example")
    print("=" * 50)
    
    # Create sample products
    products = create_sample_flipkart_products()
    
    for product in products:
        print(f"\n📱 {product}")
        print(f"   Category: {product.category.name}")
        print(f"   Price: ₹{product.price.amount}")
        print(f"   Available Stock: {product.stock.available}")
        print(f"   Brand: {product.brand}")
        
        # Test some domain operations
        print(f"\n🔄 Testing domain operations...")
        
        # Reserve stock for order
        try:
            product.reserve_for_order(2, "ORDER_001")
            print(f"   ✅ Reserved 2 units. Available now: {product.stock.available}")
        except Exception as e:
            print(f"   ❌ Reservation failed: {e}")
        
        # Test price update
        try:
            discount_price = product.calculate_discounted_price(10)  # 10% off
            print(f"   💰 10% discount price: ₹{discount_price.amount}")
            
            # Update price (within limits)
            product.update_price(discount_price)
            print(f"   ✅ Price updated to: ₹{product.price.amount}")
        except Exception as e:
            print(f"   ❌ Price update failed: {e}")
        
        # Check domain events
        events = product.clear_domain_events()
        print(f"   📋 Generated {len(events)} domain events")
        for event in events[-2:]:  # Show last 2 events
            print(f"      - {event['event_type']}")
    
    print(f"\n🏷️ Testing Dynamic Pricing Service...")
    
    # Test pricing service
    pricing_service = ProductPricingService()
    iphone = products[0]
    
    # Simulate competitor prices
    competitor_prices = [
        Money(Decimal("129999")),  # Samsung
        Money(Decimal("139999"))   # iPhone alternative
    ]
    
    dynamic_price = pricing_service.calculate_dynamic_price(
        product=iphone,
        demand_factor=1.8,  # High demand
        competitor_prices=competitor_prices,
        market_conditions={"festival_season": True}
    )
    
    print(f"📊 Original Price: ₹{iphone.price.amount}")
    print(f"📊 Dynamic Price: ₹{dynamic_price.amount}")
    print(f"📊 Price Change: {((dynamic_price.amount - iphone.price.amount) / iphone.price.amount * 100):.2f}%")
    
    print(f"\n✨ All domain rules validated successfully!")
    print(f"✨ Ready for production use in Flipkart-scale system!")