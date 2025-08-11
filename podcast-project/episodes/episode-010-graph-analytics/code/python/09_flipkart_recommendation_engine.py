"""
Flipkart-style Graph-based Recommendation Engine
Graph algorithms se personalized recommendations banana

Author: Episode 10 - Graph Analytics at Scale
Context: Indian e-commerce mein collaborative filtering aur content-based recommendations
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import logging
import time
import json
from datetime import datetime, timedelta
import random
from dataclasses import dataclass
from enum import Enum
import math
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Hindi mein logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Recommendation types"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"  # User-based similarities
    CONTENT_BASED = "content_based"                     # Product feature similarity
    GRAPH_BASED = "graph_based"                         # Graph walk algorithms
    HYBRID = "hybrid"                                   # Combination approach

class RecommendationContext(Enum):
    """Indian e-commerce contexts"""
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    HOME_KITCHEN = "home_kitchen"
    BOOKS = "books"
    GROCERY = "grocery"
    BEAUTY = "beauty"

@dataclass
class RecommendationScore:
    """Recommendation with score and reasoning"""
    item_id: str
    item_name: str
    score: float
    reasoning: str
    recommendation_type: RecommendationType
    confidence: float

class FlipkartStyleRecommendationEngine:
    """
    Graph-based Recommendation Engine for Indian E-commerce
    
    Features:
    - 10 crore+ products across categories
    - 50 crore+ customer interactions
    - Real-time personalization
    - Regional preferences integration
    - Festival/seasonal recommendations
    - Price-sensitive recommendations
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.user_profiles = {}
        self.product_profiles = {}
        self.interaction_history = {}
        
        # Indian e-commerce context
        self.indian_categories = {
            'Electronics': ['Mobile', 'Laptop', 'TV', 'Headphones', 'Camera', 'Tablet'],
            'Fashion': ['Clothing', 'Footwear', 'Watches', 'Sunglasses', 'Bags'],
            'Home & Kitchen': ['Furniture', 'Appliances', 'Cookware', 'Decor', 'Storage'],
            'Books': ['Fiction', 'Non-fiction', 'Academic', 'Comics', 'Regional'],
            'Grocery': ['Rice', 'Dal', 'Spices', 'Oil', 'Snacks', 'Beverages'],
            'Beauty': ['Skincare', 'Makeup', 'Haircare', 'Fragrance', 'Personal Care']
        }
        
        self.indian_brands = {
            'Electronics': ['Samsung', 'Xiaomi', 'OnePlus', 'Apple', 'Sony', 'LG', 'Boat'],
            'Fashion': ['Allen Solly', 'Peter England', 'Fabindia', 'W', 'Biba', 'Nike', 'Adidas'],
            'Home': ['IKEA', 'Godrej', 'Nilkamal', 'Urban Ladder', 'Pepperfry'],
            'Books': ['Penguin', 'HarperCollins', 'Rupa', 'Westland', 'Scholastic'],
            'Grocery': ['Amul', 'Britannia', 'Parle', 'ITC', 'Nestle', 'Tata', 'Patanjali'],
            'Beauty': ['Lakme', 'Nykaa', 'Mamaearth', 'Biotique', 'Forest Essentials']
        }
        
        # Regional preferences mapping
        self.regional_preferences = {
            'North': {'Food': ['Wheat', 'Dairy'], 'Fashion': ['Traditional', 'Winter_wear']},
            'South': {'Food': ['Rice', 'Coconut'], 'Fashion': ['Cotton', 'Silk']},
            'West': {'Food': ['Gujarati', 'Maharashtrian'], 'Fashion': ['Business', 'Casual']},
            'East': {'Food': ['Fish', 'Sweets'], 'Fashion': ['Handloom', 'Ethnic']}
        }
        
        # Festival seasons for recommendations
        self.festival_seasons = {
            'Diwali': ['October', 'November'],
            'Dussehra': ['September', 'October'],
            'Holi': ['March'],
            'Eid': ['Variable'],  # Based on lunar calendar
            'Christmas': ['December'],
            'New Year': ['December', 'January']
        }
        
        logger.info("Flipkart-style Recommendation Engine initialized!")
    
    def generate_ecommerce_data(self, num_users: int = 5000, 
                               num_products: int = 10000):
        """
        Indian e-commerce recommendation dataset generate karta hai
        """
        logger.info(f"Generating e-commerce data: {num_users:,} users, {num_products:,} products...")
        
        # Generate users with Indian characteristics
        for i in range(num_users):
            user_id = f"user_{i}"
            
            # Indian demographic characteristics
            age = max(16, int(np.random.normal(32, 12)))
            gender = random.choice(['Male', 'Female', 'Other'])
            city = random.choice([
                'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
                'Pune', 'Ahmedabad', 'Surat', 'Jaipur', 'Lucknow', 'Kanpur'
            ])
            
            # Income and spending behavior
            income_level = random.choices(['Low', 'Middle', 'Upper_Middle', 'High'], 
                                        weights=[30, 40, 25, 5])[0]
            
            # Technology adoption
            tech_savvy = random.uniform(0.0, 1.0)
            
            # Shopping preferences
            price_sensitive = random.uniform(0.3, 0.9)  # Indians are generally price-sensitive
            brand_conscious = random.uniform(0.2, 0.8)
            
            # Regional influence
            region = self._get_region_from_city(city)
            
            user_profile = {
                'age': age,
                'gender': gender,
                'city': city,
                'region': region,
                'income_level': income_level,
                'tech_savvy': tech_savvy,
                'price_sensitive': price_sensitive,
                'brand_conscious': brand_conscious,
                'preferred_categories': random.sample(list(self.indian_categories.keys()), 
                                                    random.randint(2, 4)),
                'shopping_frequency': random.choice(['Daily', 'Weekly', 'Monthly', 'Occasional'])
            }
            
            self.user_profiles[user_id] = user_profile
            self.graph.add_node(user_id, node_type='user', **user_profile)
        
        # Generate products with Indian market characteristics
        for i in range(num_products):
            product_id = f"product_{i}"
            
            # Product category and subcategory
            category = random.choice(list(self.indian_categories.keys()))
            subcategory = random.choice(self.indian_categories[category])
            
            # Brand selection
            if category in self.indian_brands:
                brand = random.choice(self.indian_brands[category] + ['Generic', 'Local'])
            else:
                brand = random.choice(['Generic', 'Local', 'Imported'])
            
            # Pricing based on Indian market
            if category == 'Electronics':
                base_price = random.randint(1000, 100000)  # 1K to 1L
            elif category == 'Fashion':
                base_price = random.randint(300, 10000)    # 300 to 10K
            elif category == 'Home & Kitchen':
                base_price = random.randint(500, 50000)    # 500 to 50K
            elif category == 'Books':
                base_price = random.randint(100, 2000)     # 100 to 2K
            elif category == 'Grocery':
                base_price = random.randint(50, 1000)      # 50 to 1K
            else:  # Beauty
                base_price = random.randint(200, 5000)     # 200 to 5K
            
            # Product ratings and reviews (Indian context)
            rating = random.uniform(2.5, 5.0)  # Most products have decent ratings
            num_reviews = random.randint(0, 10000)
            
            # Availability and delivery
            in_stock = random.choices([True, False], weights=[85, 15])[0]  # 85% in stock
            delivery_time = random.choice(['Same Day', '1 Day', '2-3 Days', '4-7 Days'])
            
            # Regional availability
            available_regions = random.sample(['North', 'South', 'East', 'West'], 
                                            random.randint(2, 4))
            
            product_profile = {
                'category': category,
                'subcategory': subcategory,
                'brand': brand,
                'price': base_price,
                'rating': rating,
                'num_reviews': num_reviews,
                'in_stock': in_stock,
                'delivery_time': delivery_time,
                'available_regions': available_regions,
                'description': f"{brand} {subcategory} - High quality {category.lower()} product",
                'features': self._generate_product_features(category, subcategory),
                'popularity': random.uniform(0.0, 1.0)
            }
            
            self.product_profiles[product_id] = product_profile
            self.graph.add_node(product_id, node_type='product', **product_profile)
        
        # Generate user-product interactions
        self._generate_user_product_interactions()
        
        logger.info(f"E-commerce data generated: {self.graph.number_of_nodes():,} nodes, "
                   f"{self.graph.number_of_edges():,} interactions")
    
    def _get_region_from_city(self, city: str) -> str:
        """City se region determine karta hai"""
        north_cities = ['Delhi', 'Jaipur', 'Lucknow', 'Kanpur', 'Chandigarh']
        south_cities = ['Bangalore', 'Chennai', 'Hyderabad', 'Kochi', 'Coimbatore']
        east_cities = ['Kolkata', 'Bhubaneswar', 'Guwahati']
        west_cities = ['Mumbai', 'Pune', 'Ahmedabad', 'Surat', 'Indore']
        
        if city in north_cities:
            return 'North'
        elif city in south_cities:
            return 'South'
        elif city in east_cities:
            return 'East'
        else:
            return 'West'
    
    def _generate_product_features(self, category: str, subcategory: str) -> List[str]:
        """Product ke liye features generate karta hai"""
        feature_map = {
            'Mobile': ['Android', 'iOS', '128GB', '256GB', '6GB RAM', '8GB RAM', 'Dual Camera'],
            'Laptop': ['Intel i5', 'Intel i7', 'AMD Ryzen', '8GB RAM', '16GB RAM', 'SSD'],
            'Clothing': ['Cotton', 'Polyester', 'Slim Fit', 'Regular Fit', 'Casual', 'Formal'],
            'Books': ['Paperback', 'Hardcover', 'English', 'Hindi', 'Fiction', 'Non-fiction']
        }
        
        base_features = feature_map.get(subcategory, ['Quality', 'Durable', 'Affordable'])
        return random.sample(base_features, min(3, len(base_features)))
    
    def _generate_user_product_interactions(self):
        """User-product interactions generate karta hai"""
        logger.info("Generating user-product interactions...")
        
        interaction_types = ['viewed', 'clicked', 'added_to_cart', 'purchased', 'rated', 'reviewed']
        
        # Generate interactions based on user preferences
        for user_id, user_profile in self.user_profiles.items():
            # Number of interactions based on shopping frequency
            freq_multiplier = {'Daily': 50, 'Weekly': 30, 'Monthly': 15, 'Occasional': 8}
            base_interactions = freq_multiplier.get(user_profile['shopping_frequency'], 15)
            num_interactions = random.randint(base_interactions//2, base_interactions*2)
            
            user_interactions = []
            
            for _ in range(num_interactions):
                # Select products based on user preferences
                preferred_products = [
                    pid for pid, profile in self.product_profiles.items()
                    if profile['category'] in user_profile['preferred_categories']
                    and user_profile['region'] in profile['available_regions']
                ]
                
                if not preferred_products:
                    # Fallback to any available product
                    preferred_products = list(self.product_profiles.keys())
                
                product_id = random.choice(preferred_products)
                interaction_type = random.choices(
                    interaction_types,
                    weights=[40, 30, 15, 8, 4, 3]  # Viewing most common, purchasing less
                )[0]
                
                # Interaction strength based on type
                strength_map = {
                    'viewed': 0.1, 'clicked': 0.2, 'added_to_cart': 0.5,
                    'purchased': 1.0, 'rated': 0.8, 'reviewed': 0.9
                }
                
                interaction_strength = strength_map[interaction_type]
                
                # Add price sensitivity factor
                product_price = self.product_profiles[product_id]['price']
                affordability = self._calculate_affordability(user_profile, product_price)
                
                final_strength = interaction_strength * affordability
                
                # Add edge to graph
                self.graph.add_edge(user_id, product_id,
                                  interaction_type=interaction_type,
                                  strength=final_strength,
                                  timestamp=datetime.now() - timedelta(days=random.randint(1, 365)))
                
                user_interactions.append({
                    'product_id': product_id,
                    'interaction_type': interaction_type,
                    'strength': final_strength,
                    'timestamp': datetime.now() - timedelta(days=random.randint(1, 365))
                })
            
            self.interaction_history[user_id] = user_interactions
    
    def _calculate_affordability(self, user_profile: Dict, product_price: float) -> float:
        """User ke liye product affordability calculate karta hai"""
        income_budget = {
            'Low': 5000, 'Middle': 15000, 'Upper_Middle': 50000, 'High': 200000
        }
        
        budget = income_budget.get(user_profile['income_level'], 15000)
        affordability = min(1.0, budget / max(product_price, 1))
        
        # Price sensitivity factor
        price_factor = 1.0 - user_profile['price_sensitive']
        return affordability * (1.0 + price_factor)
    
    def get_collaborative_filtering_recommendations(self, user_id: str, 
                                                  top_k: int = 10) -> List[RecommendationScore]:
        """
        Collaborative filtering recommendations using user-based similarity
        """
        if user_id not in self.user_profiles:
            return []
        
        logger.info(f"Generating collaborative filtering recommendations for {user_id}...")
        
        # Find users with similar interaction patterns
        target_user_products = set()
        if user_id in self.interaction_history:
            target_user_products = {
                interaction['product_id'] 
                for interaction in self.interaction_history[user_id]
                if interaction['strength'] > 0.3  # Minimum interaction threshold
            }
        
        if len(target_user_products) < 3:  # Too few interactions
            return self._get_popular_recommendations(user_id, top_k)
        
        # Calculate user similarities
        similar_users = []
        target_user_profile = self.user_profiles[user_id]
        
        for other_user_id, other_user_profile in self.user_profiles.items():
            if other_user_id == user_id:
                continue
            
            # Calculate similarity based on demographics and interaction patterns
            demo_similarity = self._calculate_demographic_similarity(
                target_user_profile, other_user_profile
            )
            
            other_user_products = set()
            if other_user_id in self.interaction_history:
                other_user_products = {
                    interaction['product_id']
                    for interaction in self.interaction_history[other_user_id]
                    if interaction['strength'] > 0.3
                }
            
            # Jaccard similarity for product interactions
            if other_user_products:
                jaccard_sim = len(target_user_products & other_user_products) / \
                             len(target_user_products | other_user_products)
            else:
                jaccard_sim = 0
            
            # Combined similarity score
            combined_similarity = 0.4 * demo_similarity + 0.6 * jaccard_sim
            
            if combined_similarity > 0.1:  # Minimum similarity threshold
                similar_users.append((other_user_id, combined_similarity))
        
        # Sort by similarity and take top similar users
        similar_users.sort(key=lambda x: x[1], reverse=True)
        top_similar_users = similar_users[:50]  # Top 50 similar users
        
        # Collect recommendations from similar users
        recommendation_scores = defaultdict(list)
        
        for similar_user_id, similarity_score in top_similar_users:
            if similar_user_id in self.interaction_history:
                for interaction in self.interaction_history[similar_user_id]:
                    product_id = interaction['product_id']
                    
                    # Skip products already interacted with by target user
                    if product_id not in {p['product_id'] for p in self.interaction_history.get(user_id, [])}:
                        # Score based on similarity and interaction strength
                        score = similarity_score * interaction['strength']
                        recommendation_scores[product_id].append(score)
        
        # Aggregate scores and create recommendations
        recommendations = []
        for product_id, scores in recommendation_scores.items():
            if product_id in self.product_profiles:
                avg_score = np.mean(scores)
                max_score = max(scores)
                final_score = 0.7 * avg_score + 0.3 * max_score  # Weighted combination
                
                product_profile = self.product_profiles[product_id]
                
                recommendation = RecommendationScore(
                    item_id=product_id,
                    item_name=f"{product_profile['brand']} {product_profile['subcategory']}",
                    score=final_score,
                    reasoning=f"Users similar to you also liked this {product_profile['category']}",
                    recommendation_type=RecommendationType.COLLABORATIVE_FILTERING,
                    confidence=min(1.0, len(scores) / 10)  # Higher confidence with more similar users
                )
                
                recommendations.append(recommendation)
        
        # Sort and return top k
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_k]
    
    def _calculate_demographic_similarity(self, profile1: Dict, profile2: Dict) -> float:
        """Calculate demographic similarity between users"""
        similarity = 0.0
        
        # Age similarity (closer ages are more similar)
        age_diff = abs(profile1['age'] - profile2['age'])
        age_similarity = max(0, 1 - age_diff / 50)  # Normalize by 50 years
        similarity += 0.2 * age_similarity
        
        # Gender similarity
        if profile1['gender'] == profile2['gender']:
            similarity += 0.1
        
        # City/Region similarity
        if profile1['city'] == profile2['city']:
            similarity += 0.3
        elif profile1['region'] == profile2['region']:
            similarity += 0.15
        
        # Income level similarity
        income_levels = ['Low', 'Middle', 'Upper_Middle', 'High']
        if profile1['income_level'] == profile2['income_level']:
            similarity += 0.2
        elif abs(income_levels.index(profile1['income_level']) - 
                income_levels.index(profile2['income_level'])) == 1:
            similarity += 0.1
        
        # Shopping frequency similarity
        if profile1['shopping_frequency'] == profile2['shopping_frequency']:
            similarity += 0.1
        
        # Category preference overlap
        common_categories = set(profile1['preferred_categories']) & \
                          set(profile2['preferred_categories'])
        category_similarity = len(common_categories) / \
                            max(1, len(set(profile1['preferred_categories']) | 
                                     set(profile2['preferred_categories'])))
        similarity += 0.1 * category_similarity
        
        return min(1.0, similarity)
    
    def get_content_based_recommendations(self, user_id: str, 
                                        top_k: int = 10) -> List[RecommendationScore]:
        """
        Content-based recommendations using product features
        """
        if user_id not in self.user_profiles:
            return []
        
        logger.info(f"Generating content-based recommendations for {user_id}...")
        
        # Get user's interaction history to understand preferences
        user_liked_products = []
        if user_id in self.interaction_history:
            user_liked_products = [
                interaction['product_id'] 
                for interaction in self.interaction_history[user_id]
                if interaction['strength'] > 0.5  # Strong positive interactions
            ]
        
        if not user_liked_products:
            return self._get_popular_recommendations(user_id, top_k)
        
        # Build user preference profile from liked products
        category_preferences = Counter()
        brand_preferences = Counter()
        price_range_preferences = []
        feature_preferences = Counter()
        
        for product_id in user_liked_products:
            if product_id in self.product_profiles:
                profile = self.product_profiles[product_id]
                category_preferences[profile['category']] += 1
                brand_preferences[profile['brand']] += 1
                price_range_preferences.append(profile['price'])
                
                for feature in profile.get('features', []):
                    feature_preferences[feature] += 1
        
        # Calculate preferred price range
        if price_range_preferences:
            avg_price = np.mean(price_range_preferences)
            price_tolerance = np.std(price_range_preferences) + 1000  # Add tolerance
        else:
            avg_price = 5000
            price_tolerance = 2000
        
        # Score all products based on content similarity
        recommendations = []
        
        for product_id, product_profile in self.product_profiles.items():
            # Skip products already interacted with
            if product_id in user_liked_products:
                continue
            
            content_score = 0.0
            
            # Category preference score
            category_score = category_preferences.get(product_profile['category'], 0) / \
                           max(1, sum(category_preferences.values()))
            content_score += 0.3 * category_score
            
            # Brand preference score
            brand_score = brand_preferences.get(product_profile['brand'], 0) / \
                         max(1, sum(brand_preferences.values()))
            content_score += 0.2 * brand_score
            
            # Price similarity score
            price_diff = abs(product_profile['price'] - avg_price)
            price_score = max(0, 1 - price_diff / price_tolerance)
            content_score += 0.2 * price_score
            
            # Feature similarity score
            product_features = product_profile.get('features', [])
            feature_score = 0
            for feature in product_features:
                feature_score += feature_preferences.get(feature, 0)
            
            if product_features:
                feature_score = feature_score / (len(product_features) * max(1, sum(feature_preferences.values())))
                content_score += 0.2 * feature_score
            
            # Rating and popularity bonus
            rating_bonus = (product_profile['rating'] - 2.5) / 2.5  # Normalize 2.5-5 to 0-1
            popularity_bonus = product_profile['popularity']
            content_score += 0.05 * rating_bonus + 0.05 * popularity_bonus
            
            if content_score > 0.1:  # Minimum threshold
                recommendation = RecommendationScore(
                    item_id=product_id,
                    item_name=f"{product_profile['brand']} {product_profile['subcategory']}",
                    score=content_score,
                    reasoning=f"Based on your interest in {product_profile['category']} products",
                    recommendation_type=RecommendationType.CONTENT_BASED,
                    confidence=min(1.0, len(user_liked_products) / 10)
                )
                
                recommendations.append(recommendation)
        
        # Sort and return top k
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_k]
    
    def get_graph_walk_recommendations(self, user_id: str, 
                                     top_k: int = 10,
                                     walk_length: int = 4,
                                     num_walks: int = 1000) -> List[RecommendationScore]:
        """
        Graph-based recommendations using random walks
        """
        if user_id not in self.graph:
            return []
        
        logger.info(f"Generating graph walk recommendations for {user_id}...")
        
        # Perform random walks from user node
        product_visit_counts = Counter()
        
        for _ in range(num_walks):
            current_node = user_id
            
            for step in range(walk_length):
                neighbors = list(self.graph.neighbors(current_node))
                if not neighbors:
                    break
                
                # Weighted selection based on edge strength
                weights = []
                for neighbor in neighbors:
                    edge_data = self.graph[current_node][neighbor]
                    weight = edge_data.get('strength', 0.1)
                    weights.append(weight)
                
                # Normalize weights
                total_weight = sum(weights)
                if total_weight > 0:
                    weights = [w / total_weight for w in weights]
                    next_node = np.random.choice(neighbors, p=weights)
                else:
                    next_node = random.choice(neighbors)
                
                # Count product visits
                if self.graph.nodes[next_node].get('node_type') == 'product':
                    product_visit_counts[next_node] += 1
                
                current_node = next_node
        
        # Convert visit counts to recommendations
        recommendations = []
        
        # Filter out products already interacted with
        user_products = set()
        if user_id in self.interaction_history:
            user_products = {
                interaction['product_id']
                for interaction in self.interaction_history[user_id]
            }
        
        for product_id, visit_count in product_visit_counts.most_common():
            if product_id not in user_products and product_id in self.product_profiles:
                product_profile = self.product_profiles[product_id]
                
                # Score based on visit frequency and product quality
                graph_score = visit_count / num_walks
                quality_score = (product_profile['rating'] - 2.5) / 2.5
                final_score = 0.8 * graph_score + 0.2 * quality_score
                
                recommendation = RecommendationScore(
                    item_id=product_id,
                    item_name=f"{product_profile['brand']} {product_profile['subcategory']}",
                    score=final_score,
                    reasoning="Discovered through similar user interactions",
                    recommendation_type=RecommendationType.GRAPH_BASED,
                    confidence=min(1.0, visit_count / 100)
                )
                
                recommendations.append(recommendation)
        
        return recommendations[:top_k]
    
    def get_hybrid_recommendations(self, user_id: str, 
                                 top_k: int = 10) -> List[RecommendationScore]:
        """
        Hybrid recommendations combining multiple approaches
        """
        logger.info(f"Generating hybrid recommendations for {user_id}...")
        
        # Get recommendations from different approaches
        collab_recs = self.get_collaborative_filtering_recommendations(user_id, top_k)
        content_recs = self.get_content_based_recommendations(user_id, top_k)
        graph_recs = self.get_graph_walk_recommendations(user_id, top_k)
        
        # Combine recommendations with weights
        combined_scores = defaultdict(list)
        
        # Weight the different recommendation types
        weights = {
            RecommendationType.COLLABORATIVE_FILTERING: 0.4,
            RecommendationType.CONTENT_BASED: 0.3,
            RecommendationType.GRAPH_BASED: 0.3
        }
        
        for rec_list in [collab_recs, content_recs, graph_recs]:
            for rec in rec_list:
                weight = weights[rec.recommendation_type]
                weighted_score = rec.score * weight
                combined_scores[rec.item_id].append((weighted_score, rec))
        
        # Create final hybrid recommendations
        hybrid_recommendations = []
        
        for item_id, score_rec_pairs in combined_scores.items():
            # Calculate final score
            total_score = sum(score for score, _ in score_rec_pairs)
            avg_confidence = np.mean([rec.confidence for _, rec in score_rec_pairs])
            
            # Use the best recommendation object as template
            best_rec = max(score_rec_pairs, key=lambda x: x[0])[1]
            
            hybrid_rec = RecommendationScore(
                item_id=item_id,
                item_name=best_rec.item_name,
                score=total_score,
                reasoning="Hybrid recommendation from multiple algorithms",
                recommendation_type=RecommendationType.HYBRID,
                confidence=avg_confidence
            )
            
            hybrid_recommendations.append(hybrid_rec)
        
        # Sort and return top k
        hybrid_recommendations.sort(key=lambda x: x.score, reverse=True)
        return hybrid_recommendations[:top_k]
    
    def _get_popular_recommendations(self, user_id: str, top_k: int) -> List[RecommendationScore]:
        """
        Fallback popular recommendations when personalized data is insufficient
        """
        user_profile = self.user_profiles.get(user_id, {})
        preferred_categories = user_profile.get('preferred_categories', list(self.indian_categories.keys()))
        
        # Get popular products in preferred categories
        popular_products = []
        
        for product_id, product_profile in self.product_profiles.items():
            if product_profile['category'] in preferred_categories:
                # Popularity score based on rating and number of reviews
                popularity = (product_profile['rating'] - 2.5) / 2.5 * 0.6 + \
                           min(1.0, product_profile['num_reviews'] / 1000) * 0.4
                
                popular_products.append((product_id, popularity))
        
        # Sort by popularity and create recommendations
        popular_products.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for product_id, popularity in popular_products[:top_k]:
            product_profile = self.product_profiles[product_id]
            
            recommendation = RecommendationScore(
                item_id=product_id,
                item_name=f"{product_profile['brand']} {product_profile['subcategory']}",
                score=popularity,
                reasoning="Popular in your preferred categories",
                recommendation_type=RecommendationType.CONTENT_BASED,
                confidence=0.8
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def generate_recommendation_report(self, user_id: str, 
                                     recommendations: Dict[str, List[RecommendationScore]]) -> str:
        """
        Comprehensive recommendation report generate karta hai
        """
        if user_id not in self.user_profiles:
            return "User not found!"
        
        user_profile = self.user_profiles[user_id]
        
        report = []
        report.append("🛒 FLIPKART-STYLE RECOMMENDATION REPORT")
        report.append("=" * 50)
        report.append("")
        
        # User profile summary
        report.append(f"👤 USER PROFILE: {user_id}")
        report.append(f"   • Age: {user_profile['age']} | Gender: {user_profile['gender']}")
        report.append(f"   • Location: {user_profile['city']}, {user_profile['region']}")
        report.append(f"   • Income Level: {user_profile['income_level']}")
        report.append(f"   • Shopping Frequency: {user_profile['shopping_frequency']}")
        report.append(f"   • Preferred Categories: {', '.join(user_profile['preferred_categories'])}")
        report.append("")
        
        # Interaction history summary
        if user_id in self.interaction_history:
            interactions = self.interaction_history[user_id]
            report.append(f"📊 INTERACTION HISTORY:")
            report.append(f"   • Total Interactions: {len(interactions)}")
            
            interaction_types = Counter([i['interaction_type'] for i in interactions])
            for int_type, count in interaction_types.most_common():
                report.append(f"   • {int_type.replace('_', ' ').title()}: {count}")
            report.append("")
        
        # Recommendations by type
        for rec_type, rec_list in recommendations.items():
            if not rec_list:
                continue
                
            report.append(f"🎯 {rec_type.replace('_', ' ').upper()} RECOMMENDATIONS:")
            report.append("-" * 40)
            
            for i, rec in enumerate(rec_list[:5], 1):  # Top 5 per type
                product_profile = self.product_profiles.get(rec.item_id, {})
                price = product_profile.get('price', 0)
                rating = product_profile.get('rating', 0)
                
                report.append(f"\n{i}. {rec.item_name}")
                report.append(f"   Price: ₹{price:,} | Rating: {rating:.1f}/5.0")
                report.append(f"   Score: {rec.score:.3f} | Confidence: {rec.confidence:.2f}")
                report.append(f"   Reason: {rec.reasoning}")
            
            report.append("")
        
        # Personalization insights
        report.append("💡 PERSONALIZATION INSIGHTS:")
        report.append("-" * 32)
        
        if user_profile['price_sensitive'] > 0.7:
            report.append("• High price sensitivity - showing value-for-money products")
        if user_profile['brand_conscious'] > 0.7:
            report.append("• Brand conscious - prioritizing well-known brands")
        if user_profile['tech_savvy'] > 0.7:
            report.append("• Tech-savvy user - including latest technology products")
        
        report.append(f"• Regional preference: {user_profile['region']} India products")
        
        return "\n".join(report)


def run_flipkart_recommendation_demo():
    """
    Complete Flipkart-style recommendation engine demonstration
    """
    print("🛒 Flipkart-style Graph-based Recommendation Engine")
    print("="*55)
    
    # Initialize recommendation engine
    engine = FlipkartStyleRecommendationEngine()
    
    # Generate e-commerce data
    print("\n🏗️ Generating Indian e-commerce dataset...")
    engine.generate_ecommerce_data(num_users=1000, num_products=2000)  # Smaller for demo
    
    print(f"✅ E-commerce dataset generated!")
    print(f"   • Users: {len(engine.user_profiles):,}")
    print(f"   • Products: {len(engine.product_profiles):,}")
    print(f"   • Interactions: {engine.graph.number_of_edges():,}")
    
    # Test recommendations for sample users
    sample_users = random.sample(list(engine.user_profiles.keys()), 3)
    
    for user_id in sample_users:
        user_profile = engine.user_profiles[user_id]
        print(f"\n👤 TESTING RECOMMENDATIONS FOR: {user_id}")
        print(f"Profile: {user_profile['age']}yr {user_profile['gender']} from {user_profile['city']}")
        print("="*60)
        
        # Get different types of recommendations
        recommendations = {}
        
        print("\n🤝 Collaborative Filtering Recommendations...")
        collab_recs = engine.get_collaborative_filtering_recommendations(user_id, top_k=5)
        recommendations['collaborative_filtering'] = collab_recs
        
        print(f"✅ Generated {len(collab_recs)} collaborative filtering recommendations")
        
        print("\n📝 Content-based Recommendations...")
        content_recs = engine.get_content_based_recommendations(user_id, top_k=5)
        recommendations['content_based'] = content_recs
        
        print(f"✅ Generated {len(content_recs)} content-based recommendations")
        
        print("\n🕸️ Graph Walk Recommendations...")
        graph_recs = engine.get_graph_walk_recommendations(user_id, top_k=5, num_walks=100)
        recommendations['graph_walk'] = graph_recs
        
        print(f"✅ Generated {len(graph_recs)} graph walk recommendations")
        
        print("\n🔄 Hybrid Recommendations...")
        hybrid_recs = engine.get_hybrid_recommendations(user_id, top_k=5)
        recommendations['hybrid'] = hybrid_recs
        
        print(f"✅ Generated {len(hybrid_recs)} hybrid recommendations")
        
        # Generate comprehensive report
        report = engine.generate_recommendation_report(user_id, recommendations)
        print(f"\n{report}")
        
        break  # Show detailed report for first user only
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE ANALYSIS:")
    print("-" * 30)
    
    start_time = time.time()
    test_user = sample_users[0]
    
    # Benchmark different algorithms
    collab_time = time.time()
    engine.get_collaborative_filtering_recommendations(test_user, top_k=10)
    collab_duration = time.time() - collab_time
    
    content_time = time.time()
    engine.get_content_based_recommendations(test_user, top_k=10)
    content_duration = time.time() - content_time
    
    graph_time = time.time()
    engine.get_graph_walk_recommendations(test_user, top_k=10, num_walks=500)
    graph_duration = time.time() - graph_time
    
    hybrid_time = time.time()
    engine.get_hybrid_recommendations(test_user, top_k=10)
    hybrid_duration = time.time() - hybrid_time
    
    print(f"🤝 Collaborative Filtering: {collab_duration:.3f}s")
    print(f"📝 Content-based: {content_duration:.3f}s")
    print(f"🕸️ Graph Walk: {graph_duration:.3f}s")
    print(f"🔄 Hybrid: {hybrid_duration:.3f}s")
    
    # Scalability projections
    print(f"\n📈 SCALABILITY PROJECTIONS:")
    print("-" * 35)
    
    scale_scenarios = [
        ("Current Demo", "1K users, 2K products", f"{max(collab_duration, content_duration):.2f}s"),
        ("Startup Scale", "10K users, 50K products", "2-5 seconds"),
        ("Growth Stage", "100K users, 500K products", "10-30 seconds"),
        ("Flipkart Scale", "10M users, 100M products", "Distributed processing needed")
    ]
    
    for scenario, scale, time_est in scale_scenarios:
        print(f"🎯 {scenario}: {scale} → {time_est}")
    
    # Real-world applications
    print(f"\n🚀 REAL-WORLD APPLICATIONS:")
    print("-" * 30)
    applications = [
        "🛍️ Product recommendations on homepage and category pages",
        "🔍 Search result personalization and ranking",
        "📧 Email marketing campaign personalization",
        "📱 Mobile app push notification targeting",
        "🛒 Shopping cart and checkout upselling",
        "💳 Credit and payment product recommendations",
        "🎁 Gift and festival season recommendations",
        "🏪 Seller and brand partnership insights"
    ]
    
    for app in applications:
        print(f"   {app}")


if __name__ == "__main__":
    # Flipkart-style recommendation engine demo
    run_flipkart_recommendation_demo()
    
    print("\n" + "="*55)
    print("📚 LEARNING POINTS:")
    print("• Graph-based recommendations capture complex user-product relationships")
    print("• Hybrid approaches combine strengths of different algorithms")  
    print("• Indian e-commerce needs regional and price sensitivity considerations")
    print("• Random walks discover non-obvious but relevant recommendations")
    print("• Production systems need real-time updates and distributed processing")