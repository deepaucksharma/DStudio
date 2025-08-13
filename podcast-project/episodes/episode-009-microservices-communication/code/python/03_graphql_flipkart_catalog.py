"""
GraphQL API Implementation for Flipkart-style Product Catalog
Advanced query capabilities with single endpoint flexibility

Author: Episode 9 - Microservices Communication
Context: Flipkart jaise e-commerce catalog - GraphQL power showcase
"""

import graphene
from graphene import ObjectType, String, Int, Float, List, Field, Argument, Boolean
from typing import Dict, List as ListType, Optional, Any
from dataclasses import dataclass, asdict
from decimal import Decimal
import json
import logging
import time
from datetime import datetime
from enum import Enum
import uuid

# Hindi logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enums for product management
class ProductStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OUT_OF_STOCK = "OUT_OF_STOCK"

class CategoryType(Enum):
    ELECTRONICS = "ELECTRONICS"
    CLOTHING = "CLOTHING"
    HOME_KITCHEN = "HOME_KITCHEN"
    BOOKS = "BOOKS"
    SPORTS = "SPORTS"
    BEAUTY = "BEAUTY"

# Data models
@dataclass
class ProductSpec:
    key: str
    value: str
    unit: str = ""

@dataclass
class ProductImage:
    url: str
    alt_text: str
    is_primary: bool = False

@dataclass
class ProductReview:
    review_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: datetime
    is_verified: bool = False

@dataclass
class Product:
    product_id: str
    title: str
    description: str
    brand: str
    category: CategoryType
    price: Decimal
    original_price: Decimal
    discount_percentage: int
    status: ProductStatus
    stock_quantity: int
    specifications: ListType[ProductSpec]
    images: ListType[ProductImage]
    reviews: ListType[ProductReview]
    seller_id: str
    seller_name: str
    is_flipkart_assured: bool = False
    is_plus_eligible: bool = False
    delivery_days: int = 3
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Seller:
    seller_id: str
    name: str
    rating: float
    total_products: int
    years_on_platform: int
    location: str
    is_verified: bool = False

# GraphQL Types
class ProductSpecType(ObjectType):
    key = String()
    value = String()
    unit = String()

class ProductImageType(ObjectType):
    url = String()
    alt_text = String()
    is_primary = Boolean()

class ProductReviewType(ObjectType):
    review_id = String()
    user_id = String()
    user_name = String()
    rating = Int()
    comment = String()
    created_at = String()
    is_verified = Boolean()

class SellerType(ObjectType):
    seller_id = String()
    name = String()
    rating = Float()
    total_products = Int()
    years_on_platform = Int()
    location = String()
    is_verified = Boolean()

class ProductType(ObjectType):
    product_id = String()
    title = String()
    description = String()
    brand = String()
    category = String()
    price = Float()
    original_price = Float()
    discount_percentage = Int()
    status = String()
    stock_quantity = Int()
    specifications = List(ProductSpecType)
    images = List(ProductImageType)
    reviews = List(ProductReviewType)
    seller_id = String()
    seller_name = String()
    is_flipkart_assured = Boolean()
    is_plus_eligible = Boolean()
    delivery_days = Int()
    created_at = String()
    
    # Computed fields (GraphQL ki power)
    average_rating = Float()
    reviews_count = Int()
    final_price = Float()
    savings = Float()
    
    def resolve_average_rating(self, info):
        """Reviews se average rating calculate karta hai"""
        if not self.reviews:
            return 0.0
        
        total_rating = sum(review.rating for review in self.reviews)
        return round(total_rating / len(self.reviews), 1)
    
    def resolve_reviews_count(self, info):
        """Total reviews count"""
        return len(self.reviews) if self.reviews else 0
    
    def resolve_final_price(self, info):
        """Discounted price calculate karta hai"""
        return float(self.price)
    
    def resolve_savings(self, info):
        """Kitna paisa save hua"""
        return float(self.original_price - self.price)
    
    # Nested resolvers (seller details)
    seller_details = Field(SellerType)
    
    def resolve_seller_details(self, info):
        """Seller ki complete details"""
        catalog_service = info.context['catalog_service']
        return catalog_service.get_seller_by_id(self.seller_id)

# GraphQL Input Types
class ProductFilterInput(graphene.InputObjectType):
    category = String()
    brand = String()
    min_price = Float()
    max_price = Float()
    min_rating = Float()
    is_flipkart_assured = Boolean()
    is_plus_eligible = Boolean()
    in_stock_only = Boolean()

class ProductSortInput(graphene.InputObjectType):
    field = String()  # price, rating, popularity, newest
    direction = String()  # asc, desc

# Main Service Class
class FlipkartCatalogService:
    """
    Production-ready Flipkart-style catalog service
    
    Features:
    - Complex product queries
    - Advanced filtering and sorting
    - Nested data relationships
    - Performance optimization
    - Real-time inventory updates
    """
    
    def __init__(self):
        # In-memory storage (production mein database)
        self.products: Dict[str, Product] = {}
        self.sellers: Dict[str, Seller] = {}
        
        logger.info("Flipkart Catalog Service initialized")
        self._setup_demo_data()
    
    def _setup_demo_data(self):
        """Demo products aur sellers create karta hai"""
        # Demo sellers
        demo_sellers = [
            Seller("seller_001", "ElectroWorld Store", 4.3, 150, 5, "Mumbai", True),
            Seller("seller_002", "Fashion Galaxy", 4.1, 89, 3, "Delhi", True),  
            Seller("seller_003", "Book Paradise", 4.5, 234, 7, "Bangalore", True),
            Seller("seller_004", "Home Essentials", 4.0, 67, 2, "Chennai", False)
        ]
        
        for seller in demo_sellers:
            self.sellers[seller.seller_id] = seller
        
        # Demo products
        demo_products = [
            # Electronics
            Product(
                "prod_001",
                "Samsung Galaxy S24 Ultra (Titanium Black, 256GB)",
                "Latest flagship smartphone with S Pen, 200MP camera, 6.8-inch Dynamic AMOLED display",
                "Samsung",
                CategoryType.ELECTRONICS,
                Decimal("124999.00"),
                Decimal("139999.00"), 
                11,
                ProductStatus.ACTIVE,
                25,
                [
                    ProductSpec("RAM", "12", "GB"),
                    ProductSpec("Storage", "256", "GB"),
                    ProductSpec("Display", "6.8", "inches"),
                    ProductSpec("Camera", "200", "MP"),
                    ProductSpec("Battery", "5000", "mAh")
                ],
                [
                    ProductImage("https://cdn.flipkart.com/galaxy-s24-1.jpg", "Front view", True),
                    ProductImage("https://cdn.flipkart.com/galaxy-s24-2.jpg", "Back view", False)
                ],
                [
                    ProductReview("rev_001", "user_123", "Rahul S", 5, "Amazing phone! Camera quality ekdum mast hai", datetime.now(), True),
                    ProductReview("rev_002", "user_456", "Priya M", 4, "Good performance, battery life could be better", datetime.now(), True)
                ],
                "seller_001",
                "ElectroWorld Store",
                True,  # Flipkart Assured
                True,  # Plus eligible
                1      # 1-day delivery
            ),
            
            Product(
                "prod_002", 
                "Apple iPhone 15 Pro (Natural Titanium, 128GB)",
                "iPhone 15 Pro with A17 Pro chip, titanium design, advanced camera system",
                "Apple",
                CategoryType.ELECTRONICS,
                Decimal("134900.00"),
                Decimal("139900.00"),
                4,
                ProductStatus.ACTIVE,
                15,
                [
                    ProductSpec("RAM", "8", "GB"),
                    ProductSpec("Storage", "128", "GB"), 
                    ProductSpec("Display", "6.1", "inches"),
                    ProductSpec("Camera", "48", "MP"),
                    ProductSpec("Processor", "A17 Pro", "chip")
                ],
                [
                    ProductImage("https://cdn.flipkart.com/iphone-15-1.jpg", "iPhone 15 Pro front", True)
                ],
                [
                    ProductReview("rev_003", "user_789", "Amit K", 5, "Premium feel, iOS ecosystem perfect hai", datetime.now(), True)
                ],
                "seller_001",
                "ElectroWorld Store",
                True,
                True,
                1
            ),
            
            # Clothing
            Product(
                "prod_003",
                "Roadster Men Blue Regular Fit Jeans", 
                "Comfortable cotton denim jeans with regular fit, perfect for casual wear",
                "Roadster",
                CategoryType.CLOTHING,
                Decimal("899.00"),
                Decimal("1299.00"),
                31,
                ProductStatus.ACTIVE,
                45,
                [
                    ProductSpec("Material", "Cotton Denim", ""),
                    ProductSpec("Fit", "Regular", ""),
                    ProductSpec("Color", "Blue", ""),
                    ProductSpec("Waist", "32", "inches")
                ],
                [
                    ProductImage("https://cdn.flipkart.com/jeans-1.jpg", "Jeans front view", True)
                ],
                [
                    ProductReview("rev_004", "user_101", "Suresh R", 4, "Good quality, comfortable fit", datetime.now(), False)
                ],
                "seller_002",
                "Fashion Galaxy",
                False,
                True,
                2
            ),
            
            # Books
            Product(
                "prod_004",
                "Atomic Habits by James Clear (Paperback)",
                "An easy & proven way to build good habits & break bad ones. #1 New York Times bestseller",
                "Random House",
                CategoryType.BOOKS,
                Decimal("349.00"),
                Decimal("599.00"),
                42,
                ProductStatus.ACTIVE,
                100,
                [
                    ProductSpec("Pages", "320", ""),
                    ProductSpec("Language", "English", ""),
                    ProductSpec("Format", "Paperback", ""),
                    ProductSpec("Publisher", "Random House", "")
                ],
                [
                    ProductImage("https://cdn.flipkart.com/atomic-habits.jpg", "Book cover", True)
                ],
                [
                    ProductReview("rev_005", "user_202", "Kavya S", 5, "Life-changing book! Must read for everyone", datetime.now(), True),
                    ProductReview("rev_006", "user_303", "Nikhil P", 5, "Excellent content, practical advice", datetime.now(), True)
                ],
                "seller_003", 
                "Book Paradise",
                True,
                False,
                3
            ),
            
            # Home & Kitchen
            Product(
                "prod_005",
                "Prestige Deluxe Alpha Pressure Cooker (3 Litres)",
                "Stainless steel pressure cooker with controlled gasket release system",
                "Prestige",
                CategoryType.HOME_KITCHEN,
                Decimal("1299.00"),
                Decimal("1799.00"),
                28,
                ProductStatus.ACTIVE,
                30,
                [
                    ProductSpec("Capacity", "3", "Litres"),
                    ProductSpec("Material", "Stainless Steel", ""),
                    ProductSpec("Warranty", "5", "Years"),
                    ProductSpec("Base", "Induction Base", "")
                ],
                [
                    ProductImage("https://cdn.flipkart.com/pressure-cooker.jpg", "Pressure cooker", True)
                ],
                [
                    ProductReview("rev_007", "user_404", "Sunita D", 4, "Good quality, easy to use. Value for money", datetime.now(), True)
                ],
                "seller_004",
                "Home Essentials", 
                False,
                False,
                4
            )
        ]
        
        for product in demo_products:
            self.products[product.product_id] = product
        
        logger.info(f"Demo data loaded: {len(demo_products)} products, {len(demo_sellers)} sellers")
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Product by ID"""
        return self.products.get(product_id)
    
    def get_seller_by_id(self, seller_id: str) -> Optional[Seller]:
        """Seller by ID"""
        return self.sellers.get(seller_id)
    
    def search_products(self, query: str = "", filters: dict = None, sort: dict = None, 
                       limit: int = 20, offset: int = 0) -> ListType[Product]:
        """
        Advanced product search with filters and sorting
        GraphQL query power showcase
        """
        start_time = time.time()
        
        # Start with all products
        results = list(self.products.values())
        
        # Text search in title and description
        if query:
            query_lower = query.lower()
            results = [
                p for p in results 
                if query_lower in p.title.lower() or query_lower in p.description.lower()
            ]
        
        # Apply filters
        if filters:
            if filters.get('category'):
                results = [p for p in results if p.category.value == filters['category']]
            
            if filters.get('brand'):
                brand_lower = filters['brand'].lower()
                results = [p for p in results if brand_lower in p.brand.lower()]
            
            if filters.get('min_price'):
                min_price = Decimal(str(filters['min_price']))
                results = [p for p in results if p.price >= min_price]
            
            if filters.get('max_price'):
                max_price = Decimal(str(filters['max_price']))
                results = [p for p in results if p.price <= max_price]
            
            if filters.get('is_flipkart_assured'):
                results = [p for p in results if p.is_flipkart_assured == filters['is_flipkart_assured']]
            
            if filters.get('is_plus_eligible'):
                results = [p for p in results if p.is_plus_eligible == filters['is_plus_eligible']]
            
            if filters.get('in_stock_only'):
                results = [p for p in results if p.stock_quantity > 0]
            
            if filters.get('min_rating'):
                min_rating = filters['min_rating']
                results = [
                    p for p in results 
                    if p.reviews and sum(r.rating for r in p.reviews) / len(p.reviews) >= min_rating
                ]
        
        # Apply sorting
        if sort:
            sort_field = sort.get('field', 'created_at')
            sort_direction = sort.get('direction', 'desc')
            reverse = sort_direction == 'desc'
            
            if sort_field == 'price':
                results.sort(key=lambda x: x.price, reverse=reverse)
            elif sort_field == 'rating':
                results.sort(key=lambda x: (
                    sum(r.rating for r in x.reviews) / len(x.reviews) if x.reviews else 0
                ), reverse=reverse)
            elif sort_field == 'popularity':
                results.sort(key=lambda x: len(x.reviews), reverse=reverse)
            elif sort_field == 'newest':
                results.sort(key=lambda x: x.created_at, reverse=reverse)
        
        # Apply pagination
        total_results = len(results)
        results = results[offset:offset + limit]
        
        search_time = (time.time() - start_time) * 1000
        
        logger.info(f"Product search completed: query='{query}', filters={filters}, "
                   f"found={total_results}, returned={len(results)}, time={search_time:.2f}ms")
        
        return results
    
    def get_categories_stats(self) -> Dict[str, Any]:
        """Category-wise product statistics"""
        stats = {}
        
        for category in CategoryType:
            category_products = [p for p in self.products.values() if p.category == category]
            
            if category_products:
                total_products = len(category_products)
                avg_price = sum(p.price for p in category_products) / total_products
                in_stock = sum(1 for p in category_products if p.stock_quantity > 0)
                
                stats[category.value] = {
                    'total_products': total_products,
                    'average_price': float(avg_price),
                    'in_stock': in_stock,
                    'out_of_stock': total_products - in_stock
                }
        
        return stats

# GraphQL Query and Mutation classes
class Query(ObjectType):
    """
    GraphQL Query root - single endpoint for all data needs
    """
    
    # Single product query
    product = Field(ProductType, product_id=String(required=True))
    
    def resolve_product(self, info, product_id):
        """Get product by ID"""
        catalog_service = info.context['catalog_service']
        product = catalog_service.get_product_by_id(product_id)
        return product
    
    # Product search with advanced filtering
    products = Field(
        List(ProductType),
        query=String(),
        filters=Argument(ProductFilterInput),
        sort=Argument(ProductSortInput),
        limit=Int(default_value=20),
        offset=Int(default_value=0)
    )
    
    def resolve_products(self, info, query="", filters=None, sort=None, limit=20, offset=0):
        """Search products with filters and sorting"""
        catalog_service = info.context['catalog_service']
        
        # Convert GraphQL inputs to dict
        filters_dict = {}
        sort_dict = {}
        
        if filters:
            filters_dict = {
                'category': filters.category,
                'brand': filters.brand, 
                'min_price': filters.min_price,
                'max_price': filters.max_price,
                'min_rating': filters.min_rating,
                'is_flipkart_assured': filters.is_flipkart_assured,
                'is_plus_eligible': filters.is_plus_eligible,
                'in_stock_only': filters.in_stock_only
            }
            # Remove None values
            filters_dict = {k: v for k, v in filters_dict.items() if v is not None}
        
        if sort:
            sort_dict = {
                'field': sort.field,
                'direction': sort.direction
            }
        
        products = catalog_service.search_products(query, filters_dict, sort_dict, limit, offset)
        return products
    
    # Seller information
    seller = Field(SellerType, seller_id=String(required=True))
    
    def resolve_seller(self, info, seller_id):
        """Get seller by ID"""
        catalog_service = info.context['catalog_service']
        return catalog_service.get_seller_by_id(seller_id)
    
    # Category statistics
    category_stats = graphene.JSONString()
    
    def resolve_category_stats(self, info):
        """Get category-wise statistics"""
        catalog_service = info.context['catalog_service']
        return catalog_service.get_categories_stats()

# Create GraphQL Schema
schema = graphene.Schema(query=Query)

def run_graphql_catalog_demo():
    """
    Comprehensive GraphQL catalog demo
    Showcases complex queries and real-world scenarios
    """
    print("🛒 Flipkart Product Catalog - GraphQL API")
    print("="*60)
    
    # Initialize catalog service
    catalog_service = FlipkartCatalogService()
    
    # Sample GraphQL queries
    sample_queries = [
        {
            'name': 'Get Single Product',
            'query': '''
            query {
                product(productId: "prod_001") {
                    productId
                    title
                    brand
                    price
                    originalPrice
                    discountPercentage
                    averageRating
                    reviewsCount
                    finalPrice
                    savings
                    isFlipkartAssured
                    specifications {
                        key
                        value
                        unit
                    }
                    sellerDetails {
                        name
                        rating
                        location
                        isVerified
                    }
                }
            }
            ''',
            'description': 'Single product with nested data and computed fields'
        },
        {
            'name': 'Search Electronics with Filters',
            'query': '''
            query {
                products(
                    query: "smartphone"
                    filters: {
                        category: "ELECTRONICS"
                        minPrice: 50000
                        isFlipkartAssured: true
                    }
                    sort: {
                        field: "price"
                        direction: "desc"
                    }
                    limit: 5
                ) {
                    productId
                    title
                    brand
                    price
                    averageRating
                    reviewsCount
                    isFlipkartAssured
                    deliveryDays
                }
            }
            ''',
            'description': 'Complex search with filters and sorting'
        },
        {
            'name': 'Category Statistics',
            'query': '''
            query {
                categoryStats
            }
            ''',
            'description': 'Aggregate data across categories'
        }
    ]
    
    print(f"\n📋 Sample GraphQL Queries:")
    print("-" * 40)
    
    # Execute sample queries
    context = {'catalog_service': catalog_service}
    
    for i, sample in enumerate(sample_queries, 1):
        print(f"\n{i}. {sample['name']}")
        print(f"   Description: {sample['description']}")
        print(f"   Query:")
        
        # Show query (first few lines)
        query_lines = sample['query'].strip().split('\n')
        for line in query_lines[:8]:  # Show first 8 lines
            print(f"     {line}")
        if len(query_lines) > 8:
            print(f"     ... (truncated)")
        
        try:
            # Execute GraphQL query
            start_time = time.time()
            result = schema.execute(sample['query'], context_value=context)
            execution_time = (time.time() - start_time) * 1000
            
            if result.errors:
                print(f"   ❌ Errors: {result.errors}")
            else:
                print(f"   ✅ Success (executed in {execution_time:.2f}ms)")
                
                # Show sample result (truncated)
                if result.data:
                    result_str = json.dumps(result.data, indent=2, default=str)
                    result_lines = result_str.split('\n')
                    print(f"   Result preview:")
                    for line in result_lines[:6]:  # Show first 6 lines
                        print(f"     {line}")
                    if len(result_lines) > 6:
                        print(f"     ... (truncated)")
        
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
    
    print(f"\n🎯 GraphQL Advantages Demonstrated:")
    print(f"   ✅ Single endpoint for all data needs")
    print(f"   ✅ Client specifies exactly what data to fetch")
    print(f"   ✅ Nested queries in single request")
    print(f"   ✅ Strong type system with schema")
    print(f"   ✅ Real-time computed fields")
    print(f"   ✅ Efficient - no over/under fetching")
    print(f"   ✅ Introspection and documentation built-in")
    
    print(f"\n🏭 Production Benefits:")
    print(f"   • Mobile apps mein bandwidth saving")
    print(f"   • Frontend-driven development") 
    print(f"   • Microservices aggregation layer")
    print(f"   • API evolution without versioning")
    print(f"   • Developer productivity increase")
    
    print(f"\n⚠️  Production Considerations:")
    print(f"   • Query complexity limits (prevent DOS)")
    print(f"   • Caching strategy (different from REST)")
    print(f"   • N+1 query problem solution (DataLoader)")
    print(f"   • Rate limiting per query complexity")
    print(f"   • Monitoring and analytics integration")

if __name__ == "__main__":
    # Run the GraphQL catalog demo
    run_graphql_catalog_demo()
    
    print("\n" + "="*60)
    print("📚 LEARNING POINTS:")
    print("• GraphQL client ko exact data milta hai jo chahiye")
    print("• Single endpoint se multiple resources fetch kar sakte hai")
    print("• Schema-first development approach use karte hai")
    print("• Relay/Apollo client se powerful caching milta hai") 
    print("• Mobile apps ke liye perfect - bandwidth efficient")
    print("• Microservices ke upar aggregation layer ban sakta hai")
    print("• Real-time subscriptions bhi support karta hai")
    
    print("\n🔧 Advanced Features:")
    print("• Subscriptions for real-time updates")
    print("• Directives for conditional fields")
    print("• Custom scalars for complex data types")
    print("• Federation for microservices composition")
    print("• DataLoader for efficient batch loading")