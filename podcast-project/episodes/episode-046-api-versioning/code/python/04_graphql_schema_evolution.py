#!/usr/bin/env python3
"""
GraphQL Schema Evolution and Versioning
Inspired by Zomato's API evolution from REST to GraphQL

Example: Zomato ne kaise GraphQL adopt kiya for flexible restaurant data queries
"""

import graphene
from graphene import ObjectType, String, Int, Float, Boolean, List, Field, Schema
from typing import Dict, Any, Optional, List as PyList
import json
from datetime import datetime
from dataclasses import dataclass

# Data models for Indian restaurant context
@dataclass
class RestaurantData:
    id: str
    name: str
    cuisine_type: str
    rating: float
    delivery_time: int
    location: str
    is_pure_veg: bool
    cost_for_two: int

@dataclass
class DishData:
    id: str
    name: str
    price: float
    is_veg: bool
    category: str
    description: str
    restaurant_id: str

# Mock database - Zomato style Indian restaurants
RESTAURANTS = [
    RestaurantData("1", "Saravana Bhavan", "South Indian", 4.2, 25, "Mumbai", True, 300),
    RestaurantData("2", "Bikanervala", "North Indian", 4.0, 30, "Delhi", True, 400),
    RestaurantData("3", "McDonald's", "Fast Food", 3.8, 20, "Bangalore", False, 350),
    RestaurantData("4", "Haldiram's", "Indian Sweets", 4.1, 35, "Pune", True, 250),
]

DISHES = [
    DishData("1", "Masala Dosa", 120, True, "South Indian", "Crispy dosa with potato filling", "1"),
    DishData("2", "Idli Sambar", 80, True, "South Indian", "Steamed rice cakes with sambar", "1"),
    DishData("3", "Chole Bhature", 150, True, "North Indian", "Spicy chickpeas with fried bread", "2"),
    DishData("4", "Dal Makhani", 180, True, "North Indian", "Rich black lentils with butter", "2"),
    DishData("5", "Big Mac", 220, False, "Burger", "Classic McDonald's burger", "3"),
    DishData("6", "McVeggie", 180, True, "Burger", "Vegetarian burger option", "3"),
]

# GraphQL Schema Evolution - Version 1 (Basic Schema)
class RestaurantV1(ObjectType):
    """
    Version 1: Basic restaurant information
    Zomato ka initial GraphQL schema - minimal fields
    """
    id = String()
    name = String()
    rating = Float()
    cuisine_type = String()
    
    def resolve_id(self, info):
        return self.id
    
    def resolve_name(self, info):
        return self.name
    
    def resolve_rating(self, info):
        return self.rating
    
    def resolve_cuisine_type(self, info):
        return self.cuisine_type

class QueryV1(ObjectType):
    """Version 1 Query - Basic restaurant search"""
    restaurant = Field(RestaurantV1, id=String(required=True))
    restaurants = List(RestaurantV1)
    
    def resolve_restaurant(self, info, id):
        """Get single restaurant by ID"""
        restaurant = next((r for r in RESTAURANTS if r.id == id), None)
        return restaurant
    
    def resolve_restaurants(self, info):
        """Get all restaurants"""
        return RESTAURANTS

# GraphQL Schema Evolution - Version 2 (Enhanced Schema)
class RestaurantV2(ObjectType):
    """
    Version 2: Enhanced restaurant with delivery info
    Added delivery time and location - customer demand ke basis pe
    """
    id = String()
    name = String()
    rating = Float()
    cuisine_type = String()
    
    # V2 additions - backward compatible
    delivery_time = Int()
    location = String()
    cost_for_two = Int()
    
    # Computed field - GraphQL ki power
    is_fast_delivery = Boolean()
    
    def resolve_is_fast_delivery(self, info):
        """Computed field - delivery time < 30 minutes"""
        return self.delivery_time < 30
    
    def resolve_delivery_time(self, info):
        """Delivery time in minutes"""
        return self.delivery_time
    
    def resolve_location(self, info):
        """Restaurant location"""
        return self.location
    
    def resolve_cost_for_two(self, info):
        """Average cost for two people"""
        return self.cost_for_two

class DishV2(ObjectType):
    """
    Version 2: Dish information added
    Customer chahte the menu details bhi
    """
    id = String()
    name = String()
    price = Float()
    is_veg = Boolean()
    category = String()
    description = String()
    
    def resolve_price_in_inr(self, info):
        """Price formatted in INR"""
        return f"₹{self.price}"

class QueryV2(ObjectType):
    """Version 2 Query - Enhanced with filters and dishes"""
    restaurant = Field(RestaurantV2, id=String(required=True))
    restaurants = List(RestaurantV2, veg_only=Boolean(), max_delivery_time=Int())
    
    # New in V2
    dishes_by_restaurant = List(DishV2, restaurant_id=String(required=True))
    search_dishes = List(DishV2, query=String(), veg_only=Boolean())
    
    def resolve_restaurant(self, info, id):
        """Get single restaurant by ID"""
        restaurant = next((r for r in RESTAURANTS if r.id == id), None)
        return restaurant
    
    def resolve_restaurants(self, info, veg_only=None, max_delivery_time=None):
        """Get restaurants with filters - GraphQL ki flexibility"""
        restaurants = RESTAURANTS.copy()
        
        # Apply filters
        if veg_only:
            restaurants = [r for r in restaurants if r.is_pure_veg]
        
        if max_delivery_time:
            restaurants = [r for r in restaurants if r.delivery_time <= max_delivery_time]
        
        return restaurants
    
    def resolve_dishes_by_restaurant(self, info, restaurant_id):
        """Get dishes for a restaurant"""
        return [d for d in DISHES if d.restaurant_id == restaurant_id]
    
    def resolve_search_dishes(self, info, query=None, veg_only=None):
        """Search dishes with filters"""
        dishes = DISHES.copy()
        
        if query:
            dishes = [d for d in dishes if query.lower() in d.name.lower()]
        
        if veg_only:
            dishes = [d for d in dishes if d.is_veg]
        
        return dishes

# GraphQL Schema Evolution - Version 3 (Full Featured)
class NutritionInfo(ObjectType):
    """Version 3: Nutrition information added"""
    calories = Int()
    protein = Float()
    carbs = Float()
    fat = Float()

class RestaurantV3(ObjectType):
    """
    Version 3: Full-featured restaurant with relationships
    Health-conscious customers ke liye nutrition info
    """
    id = String()
    name = String()
    rating = Float()
    cuisine_type = String()
    delivery_time = Int()
    location = String()
    cost_for_two = Int()
    is_pure_veg = Boolean()
    
    # V3 additions
    popular_dishes = List(DishV2)
    avg_rating_breakdown = Field(lambda: RatingBreakdown)
    sustainability_score = Float()
    
    def resolve_popular_dishes(self, info):
        """Get popular dishes for this restaurant"""
        restaurant_dishes = [d for d in DISHES if d.restaurant_id == self.id]
        # Return first 3 as popular (mock logic)
        return restaurant_dishes[:3]
    
    def resolve_avg_rating_breakdown(self, info):
        """Detailed rating breakdown"""
        # Mock rating breakdown
        return {
            "food_quality": 4.3,
            "delivery_time": 4.0,
            "value_for_money": 4.1,
            "packaging": 4.2
        }
    
    def resolve_sustainability_score(self, info):
        """Sustainability score out of 5"""
        # Mock sustainability calculation
        return 4.2 if self.is_pure_veg else 3.5

class RatingBreakdown(ObjectType):
    """Rating breakdown by categories"""
    food_quality = Float()
    delivery_time = Float()
    value_for_money = Float()
    packaging = Float()

class DishV3(ObjectType):
    """
    Version 3: Enhanced dish with nutrition and customization
    """
    id = String()
    name = String()
    price = Float()
    is_veg = Boolean()
    category = String()
    description = String()
    
    # V3 additions
    nutrition_info = Field(NutritionInfo)
    customization_options = List(String)
    allergen_info = List(String)
    spice_level = Int()  # 1-5 scale
    
    def resolve_nutrition_info(self, info):
        """Mock nutrition information"""
        # Different nutrition based on dish type
        if self.is_veg:
            return {
                "calories": 250,
                "protein": 8.0,
                "carbs": 45.0,
                "fat": 6.0
            }
        else:
            return {
                "calories": 350,
                "protein": 15.0,
                "carbs": 30.0,
                "fat": 18.0
            }
    
    def resolve_customization_options(self, info):
        """Available customizations"""
        if "Dosa" in self.name:
            return ["Extra Sambar", "Less Oil", "Extra Chutney"]
        elif "Burger" in self.category:
            return ["No Onions", "Extra Cheese", "Spicy Mayo"]
        else:
            return ["Less Spicy", "Extra Gravy"]
    
    def resolve_allergen_info(self, info):
        """Allergen information"""
        allergens = []
        if not self.is_veg:
            allergens.append("Contains Meat")
        if "cheese" in self.name.lower():
            allergens.append("Contains Dairy")
        if "wheat" in self.description.lower() or "bread" in self.name.lower():
            allergens.append("Contains Gluten")
        return allergens
    
    def resolve_spice_level(self, info):
        """Spice level 1-5"""
        if "Masala" in self.name:
            return 4
        elif "Chole" in self.name:
            return 3
        else:
            return 1

class QueryV3(ObjectType):
    """Version 3 Query - Advanced search and recommendations"""
    restaurant = Field(RestaurantV3, id=String(required=True))
    restaurants = List(RestaurantV3, 
                      veg_only=Boolean(), 
                      max_delivery_time=Int(),
                      min_rating=Float(),
                      max_cost=Int(),
                      cuisine_type=String())
    
    dish = Field(DishV3, id=String(required=True))
    dishes = List(DishV3, 
                 restaurant_id=String(),
                 veg_only=Boolean(),
                 max_price=Float(),
                 category=String(),
                 max_spice_level=Int())
    
    # V3 advanced features
    recommended_restaurants = List(RestaurantV3, user_location=String())
    trending_dishes = List(DishV3, location=String())
    
    def resolve_restaurant(self, info, id):
        """Get single restaurant with full details"""
        restaurant = next((r for r in RESTAURANTS if r.id == id), None)
        return restaurant
    
    def resolve_restaurants(self, info, **filters):
        """Advanced restaurant filtering"""
        restaurants = RESTAURANTS.copy()
        
        if filters.get('veg_only'):
            restaurants = [r for r in restaurants if r.is_pure_veg]
        
        if filters.get('max_delivery_time'):
            restaurants = [r for r in restaurants if r.delivery_time <= filters['max_delivery_time']]
        
        if filters.get('min_rating'):
            restaurants = [r for r in restaurants if r.rating >= filters['min_rating']]
        
        if filters.get('max_cost'):
            restaurants = [r for r in restaurants if r.cost_for_two <= filters['max_cost']]
        
        if filters.get('cuisine_type'):
            restaurants = [r for r in restaurants if r.cuisine_type == filters['cuisine_type']]
        
        return restaurants
    
    def resolve_dish(self, info, id):
        """Get single dish with full details"""
        dish = next((d for d in DISHES if d.id == id), None)
        return dish
    
    def resolve_dishes(self, info, **filters):
        """Advanced dish filtering"""
        dishes = DISHES.copy()
        
        if filters.get('restaurant_id'):
            dishes = [d for d in dishes if d.restaurant_id == filters['restaurant_id']]
        
        if filters.get('veg_only'):
            dishes = [d for d in dishes if d.is_veg]
        
        if filters.get('max_price'):
            dishes = [d for d in dishes if d.price <= filters['max_price']]
        
        if filters.get('category'):
            dishes = [d for d in dishes if d.category == filters['category']]
        
        return dishes
    
    def resolve_recommended_restaurants(self, info, user_location=None):
        """AI-powered restaurant recommendations"""
        # Mock recommendation logic based on location
        if user_location == "Mumbai":
            return [r for r in RESTAURANTS if "Mumbai" in r.location][:3]
        else:
            return RESTAURANTS[:2]  # Default recommendations
    
    def resolve_trending_dishes(self, info, location=None):
        """Trending dishes based on location"""
        # Mock trending logic
        return DISHES[:4]  # Return first 4 as trending

class SchemaVersionManager:
    """
    Manage different GraphQL schema versions
    """
    
    def __init__(self):
        self.schemas = {
            "v1": Schema(query=QueryV1),
            "v2": Schema(query=QueryV2),
            "v3": Schema(query=QueryV3)
        }
        
        self.version_info = {
            "v1": {
                "description": "Basic restaurant information",
                "deprecated": True,
                "features": ["restaurant_search", "basic_info"],
                "sunset_date": "2024-06-30"
            },
            "v2": {
                "description": "Enhanced with delivery and dish information",
                "deprecated": False,
                "features": ["restaurant_search", "dish_search", "delivery_info", "filters"]
            },
            "v3": {
                "description": "Full-featured with nutrition and AI recommendations",
                "deprecated": False,
                "features": ["advanced_search", "nutrition_info", "recommendations", "customization"]
            }
        }
    
    def get_schema(self, version: str):
        """Get GraphQL schema for specific version"""
        return self.schemas.get(version)
    
    def execute_query(self, version: str, query: str):
        """Execute query on specific schema version"""
        schema = self.get_schema(version)
        if not schema:
            return {"error": f"Version {version} not supported"}
        
        try:
            result = schema.execute(query)
            if result.errors:
                return {"errors": [str(error) for error in result.errors]}
            return {"data": result.data}
        except Exception as e:
            return {"error": str(e)}
    
    def get_version_capabilities(self, version: str):
        """Get capabilities of specific version"""
        return self.version_info.get(version, {})

def demonstrate_graphql_evolution():
    """
    Demonstrate GraphQL schema evolution with real queries
    """
    print("🔥 GraphQL Schema Evolution - Zomato Style")
    print("=" * 60)
    
    manager = SchemaVersionManager()
    
    # Sample queries for each version
    queries = {
        "v1": """
        {
          restaurants {
            id
            name
            rating
            cuisine_type
          }
        }
        """,
        
        "v2": """
        {
          restaurants(veg_only: true, max_delivery_time: 30) {
            id
            name
            rating
            delivery_time
            location
            cost_for_two
            is_fast_delivery
          }
          
          dishes_by_restaurant(restaurant_id: "1") {
            name
            price
            is_veg
            category
          }
        }
        """,
        
        "v3": """
        {
          restaurants(veg_only: true, min_rating: 4.0) {
            id
            name
            rating
            sustainability_score
            popular_dishes {
              name
              price
              nutrition_info {
                calories
                protein
              }
              customization_options
              allergen_info
              spice_level
            }
            avg_rating_breakdown {
              food_quality
              delivery_time
              value_for_money
            }
          }
          
          recommended_restaurants(user_location: "Mumbai") {
            name
            cuisine_type
            delivery_time
          }
        }
        """
    }
    
    # Execute queries on different versions
    for version, query in queries.items():
        print(f"\n📊 {version.upper()} Query Results:")
        print("-" * 40)
        
        result = manager.execute_query(version, query)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        elif "errors" in result:
            print(f"❌ Errors: {result['errors']}")
        else:
            print("✅ Query successful")
            # Print formatted result (truncated for readability)
            data = result["data"]
            if "restaurants" in data:
                print(f"   Found {len(data['restaurants'])} restaurants")
                for restaurant in data['restaurants'][:2]:  # Show first 2
                    print(f"   - {restaurant['name']} ({restaurant['rating']} stars)")
    
    print("\n🔄 Schema Evolution Benefits:")
    print("1. Backward compatibility - old queries still work")
    print("2. Additive changes - new fields don't break existing clients")
    print("3. Flexible querying - clients request only needed data")
    print("4. Strong typing - schema validation at runtime")
    print("5. Introspection - clients can discover available fields")
    
    print("\n💡 GraphQL Versioning Strategies:")
    print("1. Schema stitching - combine multiple schemas")
    print("2. Deprecation warnings - mark fields as deprecated")
    print("3. Field-level versioning - version individual fields")
    print("4. Schema evolution - additive changes only")
    
    print("\n🎯 Best Practices for Indian Context:")
    print("1. Consider regional preferences in schema design")
    print("2. Handle multi-language content (Hindi/English)")
    print("3. Account for varying data quality across regions")
    print("4. Design for mobile-first usage patterns")
    print("5. Include cost-conscious filtering options")
    
    # Version comparison
    print("\n📈 Version Comparison:")
    for version, info in manager.version_info.items():
        status = "⚠️  DEPRECATED" if info.get('deprecated') else "✅ ACTIVE"
        print(f"{version.upper()}: {info['description']} - {status}")
        print(f"   Features: {', '.join(info['features'])}")
        if info.get('sunset_date'):
            print(f"   Sunset Date: {info['sunset_date']}")

if __name__ == "__main__":
    demonstrate_graphql_evolution()