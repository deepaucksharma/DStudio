#!/usr/bin/env python3
"""
Flipkart Product Catalog GraphQL API
फ्लिपकार्ट स्टाइल product catalog और recommendation system

GraphQL के फायदे:
- Client को जो data चाहिए वही fetch करे
- Over-fetching और under-fetching की problem नहीं  
- Single endpoint से सब कुछ
- Strong typing और introspection

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns (GraphQL Implementation)
"""

import graphene
from graphene import ObjectType, String, Int, Float, List, Field, Argument, Schema
from graphene import Mutation, Boolean
import json
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GraphQL Types - Flipkart product structure

class ProductImage(ObjectType):
    url = String(description="Image URL")
    alt_text = String(description="Alternative text for accessibility")
    is_primary = Boolean(description="Is this the primary image")

class ProductRating(ObjectType):
    average_rating = Float(description="Average rating out of 5")
    total_reviews = Int(description="Total number of reviews")
    rating_distribution = String(description="JSON string of rating distribution")

class ProductPrice(ObjectType):
    mrp = Float(description="Maximum Retail Price in ₹")
    selling_price = Float(description="Current selling price in ₹")
    discount_percentage = Int(description="Discount percentage")
    emi_available = Boolean(description="Is EMI available")
    emi_starting_from = Float(description="EMI starting price")

class ProductSpecification(ObjectType):
    key = String(description="Specification key")
    value = String(description="Specification value")
    category = String(description="Specification category")

class Product(ObjectType):
    """
    Flipkart Product - Complete product information
    GraphQL client सिर्फ जो fields चाहिए वो fetch कर सकता है
    """
    id = String(description="Unique product ID")
    name = String(description="Product name")
    brand = String(description="Product brand")
    category = String(description="Product category")
    sub_category = String(description="Product sub-category")
    
    # Price information  
    price = Field(ProductPrice, description="Pricing details")
    
    # Images
    images = List(ProductImage, description="Product images")
    
    # Ratings and reviews
    rating = Field(ProductRating, description="Rating information")
    
    # Specifications
    specifications = List(ProductSpecification, description="Product specifications")
    
    # Availability
    in_stock = Boolean(description="Is product in stock")
    stock_quantity = Int(description="Available quantity")
    estimated_delivery = String(description="Estimated delivery date")
    
    # Seller information
    seller_name = String(description="Seller name")
    seller_rating = Float(description="Seller rating")
    
    # Additional info
    is_flipkart_assured = Boolean(description="Flipkart Assured product")
    is_plus_product = Boolean(description="Flipkart Plus product")
    
    # Mumbai specific
    cod_available = Boolean(description="Cash on Delivery available")
    same_day_delivery = Boolean(description="Same day delivery available in Mumbai")

class User(ObjectType):
    """Flipkart User Profile"""
    id = String(description="User ID")
    name = String(description="User name")
    email = String(description="Email address")
    mobile = String(description="Mobile number")
    is_plus_member = Boolean(description="Flipkart Plus member")
    wishlist = List(Product, description="User's wishlist products")

class SearchFilters(ObjectType):
    """Available filters for product search"""
    brands = List(String, description="Available brands")
    price_ranges = List(String, description="Available price ranges")
    ratings = List(String, description="Rating filters")
    categories = List(String, description="Product categories")

# In-memory database - Production में यह MongoDB/Elasticsearch होगा
PRODUCTS_DB = {
    "MOBILE_IPHONE15": {
        "id": "MOBILE_IPHONE15",
        "name": "Apple iPhone 15",
        "brand": "Apple",
        "category": "Mobile",
        "sub_category": "Smartphone",
        "price": {
            "mrp": 79900,
            "selling_price": 76900,
            "discount_percentage": 4,
            "emi_available": True,
            "emi_starting_from": 3845
        },
        "images": [
            {"url": "/images/iphone15-blue.jpg", "alt_text": "iPhone 15 Blue", "is_primary": True},
            {"url": "/images/iphone15-back.jpg", "alt_text": "iPhone 15 Back", "is_primary": False}
        ],
        "rating": {
            "average_rating": 4.4,
            "total_reviews": 15420,
            "rating_distribution": '{"5": 8500, "4": 4200, "3": 1800, "2": 600, "1": 320}'
        },
        "specifications": [
            {"key": "Screen Size", "value": "6.1 inch", "category": "Display"},
            {"key": "Storage", "value": "128 GB", "category": "Memory"},
            {"key": "Camera", "value": "48 MP", "category": "Camera"},
            {"key": "Battery", "value": "Li-Ion", "category": "Power"}
        ],
        "in_stock": True,
        "stock_quantity": 45,
        "estimated_delivery": "Tomorrow by 10 PM",
        "seller_name": "Flipkart Retail Ltd.",
        "seller_rating": 4.8,
        "is_flipkart_assured": True,
        "is_plus_product": True,
        "cod_available": False,  # High value item
        "same_day_delivery": True
    },
    "BOOK_SYSTEM_DESIGN": {
        "id": "BOOK_SYSTEM_DESIGN",
        "name": "System Design Interview Book",
        "brand": "Tech Publications",
        "category": "Books",
        "sub_category": "Technical Books",
        "price": {
            "mrp": 1499,
            "selling_price": 1049,
            "discount_percentage": 30,
            "emi_available": False,
            "emi_starting_from": None
        },
        "images": [
            {"url": "/images/system-design-book.jpg", "alt_text": "System Design Book Cover", "is_primary": True}
        ],
        "rating": {
            "average_rating": 4.7,
            "total_reviews": 2840,
            "rating_distribution": '{"5": 2100, "4": 540, "3": 120, "2": 50, "1": 30}'
        },
        "specifications": [
            {"key": "Pages", "value": "450", "category": "Physical"},
            {"key": "Language", "value": "English", "category": "Content"},
            {"key": "Publisher", "value": "Tech Publications", "category": "Publication"}
        ],
        "in_stock": True,
        "stock_quantity": 120,
        "estimated_delivery": "2 days",
        "seller_name": "Book Paradise",
        "seller_rating": 4.5,
        "is_flipkart_assured": False,
        "is_plus_product": False,
        "cod_available": True,
        "same_day_delivery": False
    }
}

USERS_DB = {
    "user_123": {
        "id": "user_123",
        "name": "Rahul Sharma",
        "email": "rahul@gmail.com",
        "mobile": "+91-9876543210",
        "is_plus_member": True,
        "wishlist": ["MOBILE_IPHONE15"]
    }
}

# GraphQL Queries
class Query(ObjectType):
    """
    GraphQL Query Root
    यहाँ सभी query operations define होते हैं
    """
    
    # Product queries
    product = Field(
        Product, 
        product_id=Argument(String, required=True, description="Product ID"),
        description="Get a single product by ID"
    )
    
    search_products = Field(
        List(Product),
        query=Argument(String, required=True, description="Search query"),
        category=Argument(String, description="Filter by category"),
        min_price=Argument(Float, description="Minimum price filter"),
        max_price=Argument(Float, description="Maximum price filter"),
        brand=Argument(String, description="Filter by brand"),
        sort_by=Argument(String, description="Sort by: price_low, price_high, rating, popularity"),
        limit=Argument(Int, description="Number of results to return"),
        description="Search products with filters - Flipkart style search"
    )
    
    recommendations = Field(
        List(Product),
        product_id=Argument(String, required=True, description="Base product ID"),
        limit=Argument(Int, description="Number of recommendations"),
        description="Get product recommendations based on a product"
    )
    
    trending_products = Field(
        List(Product),
        category=Argument(String, description="Filter by category"),
        limit=Argument(Int, description="Number of trending products"),
        description="Get trending products - Mumbai mein क्या चल रहा है"
    )
    
    # User queries
    user = Field(
        User,
        user_id=Argument(String, required=True, description="User ID"),
        description="Get user profile information"
    )
    
    # Filter queries
    search_filters = Field(
        SearchFilters,
        category=Argument(String, description="Get filters for a category"),
        description="Get available search filters"
    )

    def resolve_product(self, info, product_id):
        """Single product fetch - Mumbai style error handling"""
        logger.info(f"Fetching product: {product_id}")
        
        if product_id not in PRODUCTS_DB:
            raise Exception(f"Product {product_id} nahi mila! Check the ID once more")
            
        product_data = PRODUCTS_DB[product_id]
        return Product(**product_data)
    
    def resolve_search_products(self, info, query, **filters):
        """
        Product search - Advanced filtering जैसे Flipkart पे होता है
        GraphQL की power - client specify कर सकता है कौन se fields चाहिए
        """
        logger.info(f"Product search: query='{query}', filters={filters}")
        
        matching_products = []
        
        for product_id, product_data in PRODUCTS_DB.items():
            # Text search in name, brand, category
            if (query.lower() in product_data['name'].lower() or 
                query.lower() in product_data['brand'].lower() or
                query.lower() in product_data['category'].lower()):
                
                # Apply filters
                if filters.get('category') and filters['category'].lower() != product_data['category'].lower():
                    continue
                    
                if filters.get('brand') and filters['brand'].lower() != product_data['brand'].lower():
                    continue
                    
                if filters.get('min_price') and product_data['price']['selling_price'] < filters['min_price']:
                    continue
                    
                if filters.get('max_price') and product_data['price']['selling_price'] > filters['max_price']:
                    continue
                
                matching_products.append(Product(**product_data))
        
        # Sorting - Mumbai mein सबसे पहले price देखते हैं
        sort_by = filters.get('sort_by', 'popularity')
        if sort_by == 'price_low':
            matching_products.sort(key=lambda p: PRODUCTS_DB[p.id]['price']['selling_price'])
        elif sort_by == 'price_high':
            matching_products.sort(key=lambda p: PRODUCTS_DB[p.id]['price']['selling_price'], reverse=True)
        elif sort_by == 'rating':
            matching_products.sort(key=lambda p: PRODUCTS_DB[p.id]['rating']['average_rating'], reverse=True)
            
        # Limit results
        limit = filters.get('limit', 10)
        return matching_products[:limit]
    
    def resolve_recommendations(self, info, product_id, limit=5):
        """
        Product recommendations - ML algorithms का simplified version
        Production में collaborative filtering या content-based filtering होगा
        """
        logger.info(f"Getting recommendations for product: {product_id}")
        
        if product_id not in PRODUCTS_DB:
            return []
            
        base_product = PRODUCTS_DB[product_id]
        recommendations = []
        
        # Same category products (simple recommendation logic)
        for pid, pdata in PRODUCTS_DB.items():
            if (pid != product_id and 
                pdata['category'] == base_product['category'] and
                len(recommendations) < limit):
                recommendations.append(Product(**pdata))
                
        return recommendations
    
    def resolve_trending_products(self, info, category=None, limit=10):
        """Trending products - Mumbai में क्या popular है"""
        logger.info(f"Getting trending products for category: {category}")
        
        trending = []
        for product_id, product_data in PRODUCTS_DB.items():
            if not category or product_data['category'].lower() == category.lower():
                # Simple trending logic - high rating products
                if product_data['rating']['average_rating'] >= 4.0:
                    trending.append(Product(**product_data))
                    
        # Sort by rating * review count (popularity metric)
        trending.sort(
            key=lambda p: PRODUCTS_DB[p.id]['rating']['average_rating'] * PRODUCTS_DB[p.id]['rating']['total_reviews'], 
            reverse=True
        )
        
        return trending[:limit]
    
    def resolve_user(self, info, user_id):
        """User profile with wishlist"""
        if user_id not in USERS_DB:
            raise Exception(f"User {user_id} not found!")
            
        user_data = USERS_DB[user_id].copy()
        
        # Populate wishlist with full product objects
        wishlist_products = []
        for product_id in user_data['wishlist']:
            if product_id in PRODUCTS_DB:
                wishlist_products.append(Product(**PRODUCTS_DB[product_id]))
                
        user_data['wishlist'] = wishlist_products
        return User(**user_data)
    
    def resolve_search_filters(self, info, category=None):
        """Available search filters - Dynamic filter generation"""
        brands = set()
        categories = set()
        
        for product_data in PRODUCTS_DB.values():
            if not category or product_data['category'].lower() == category.lower():
                brands.add(product_data['brand'])
                categories.add(product_data['category'])
        
        return SearchFilters(
            brands=list(brands),
            categories=list(categories),
            price_ranges=["Under ₹1000", "₹1000-₹5000", "₹5000-₹25000", "Above ₹25000"],
            ratings=["4★ & above", "3★ & above", "2★ & above"]
        )

# GraphQL Mutations - Add to cart, wishlist operations
class AddToWishlist(Mutation):
    """Add product to user wishlist"""
    
    class Arguments:
        user_id = String(required=True, description="User ID")
        product_id = String(required=True, description="Product ID to add")
    
    success = Boolean()
    message = String()
    user = Field(User)
    
    def mutate(self, info, user_id, product_id):
        if user_id not in USERS_DB:
            return AddToWishlist(
                success=False, 
                message="User not found!", 
                user=None
            )
            
        if product_id not in PRODUCTS_DB:
            return AddToWishlist(
                success=False,
                message="Product not found!",
                user=None
            )
            
        user_data = USERS_DB[user_id]
        if product_id not in user_data['wishlist']:
            user_data['wishlist'].append(product_id)
            
        # Return updated user
        wishlist_products = []
        for pid in user_data['wishlist']:
            if pid in PRODUCTS_DB:
                wishlist_products.append(Product(**PRODUCTS_DB[pid]))
                
        user_data_copy = user_data.copy()
        user_data_copy['wishlist'] = wishlist_products
        
        return AddToWishlist(
            success=True,
            message=f"Product {product_id} wishlist mein add ho gaya!",
            user=User(**user_data_copy)
        )

class Mutation(ObjectType):
    """GraphQL Mutation Root"""
    add_to_wishlist = AddToWishlist.Field()

# GraphQL Schema creation
schema = Schema(query=Query, mutation=Mutation)

# GraphQL server setup using Flask-GraphQL
from flask import Flask
from flask_graphql import GraphQLView

app = Flask(__name__)

# GraphQL endpoint - Single endpoint GraphQL का main advantage
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Interactive GraphQL playground
    )
)

# REST endpoint for comparison
@app.route('/api/health')
def health():
    return {
        "status": "healthy",
        "service": "Flipkart GraphQL API", 
        "endpoints": {
            "graphql": "/graphql",
            "playground": "/graphql (GraphiQL interface)"
        },
        "message": "Flipkart GraphQL API ready! Mumbai से Delhi tak sab products available 🛒"
    }

if __name__ == '__main__':
    print("🛒 Flipkart GraphQL API Server starting...")
    print("📦 Product catalog, search, recommendations - सब GraphQL से!")
    print("🔍 GraphiQL playground available at: http://localhost:5000/graphql")
    print("\nExample GraphQL Query:")
    print("""
    query {
      searchProducts(query: "phone", minPrice: 50000, limit: 2) {
        name
        brand
        price {
          sellingPrice
          discountPercentage
        }
        rating {
          averageRating
          totalReviews
        }
        inStock
      }
    }
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=True)