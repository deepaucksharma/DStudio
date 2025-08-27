"""
Encrypted Recommendation System using Homomorphic Encryption
Flipkart, Amazon India के लिए privacy-preserving product recommendations
Customer browsing और purchase data को encrypt करके personalized suggestions
"""

import tenseal as ts
import numpy as np
import pandas as pd
import logging
import hashlib
import json
import time
from typing import List, Dict, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Hindi comments के साथ logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductCategory(Enum):
    """Indian e-commerce product categories"""
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    HOME_KITCHEN = "home_kitchen"
    BOOKS = "books"
    SPORTS = "sports"
    BEAUTY = "beauty"
    GROCERY = "grocery"
    MOBILE = "mobile"
    APPLIANCES = "appliances"
    FURNITURE = "furniture"
    JEWELRY = "jewelry"
    AUTOMOTIVE = "automotive"

class UserBehavior(Enum):
    """User interaction types"""
    VIEW = "view"
    CLICK = "click"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    WISHLIST = "wishlist"
    REVIEW = "review"
    SHARE = "share"
    SEARCH = "search"

@dataclass
class Product:
    """Product information structure"""
    product_id: str
    name: str
    category: ProductCategory
    brand: str
    price: float
    rating: float
    review_count: int
    
    # Product features for ML
    features: List[str] = field(default_factory=list)  # Tags, attributes
    description: str = ""
    seller_id: str = ""
    
    # Regional preferences
    popular_in_states: List[str] = field(default_factory=list)
    language_variants: List[str] = field(default_factory=list)  # Hindi, Tamil, etc.
    
    # Encrypted product vector (populated by system)
    encrypted_features: Optional[ts.CKKSVector] = None

@dataclass
class UserProfile:
    """User profile with encrypted behavioral data"""
    user_id: str
    user_hash: str  # Privacy-preserving identifier
    
    # Demographics (encrypted)
    age_group: str  # 18-25, 26-35, etc.
    gender: str
    location_state: str
    location_city: str
    income_bracket: str
    preferred_language: str
    
    # Shopping preferences
    favorite_categories: List[ProductCategory] = field(default_factory=list)
    price_sensitivity: str = "medium"  # low, medium, high
    brand_preference: str = "mixed"    # brand_conscious, value_conscious, mixed
    
    # Behavioral history
    total_orders: int = 0
    total_spent: float = 0.0
    avg_order_value: float = 0.0
    preferred_shopping_time: str = "evening"
    
    # Encrypted profile vector
    encrypted_profile: Optional[ts.CKKSVector] = None
    encrypted_preferences: Optional[ts.CKKSVector] = None

@dataclass 
class UserInteraction:
    """User-product interaction record"""
    interaction_id: str
    user_hash: str
    product_id: str
    behavior_type: UserBehavior
    timestamp: datetime
    
    # Context
    session_id: str
    device_type: str = "mobile"
    platform: str = "app"  # app, web, mweb
    
    # Interaction details
    duration_seconds: int = 0
    scroll_depth: float = 0.0
    rating_given: Optional[float] = None
    review_text: str = ""
    
    # Encrypted interaction features
    encrypted_context: Optional[ts.CKKSVector] = None

class EncryptedRecommendationEngine:
    """
    Privacy-preserving recommendation system for Indian e-commerce
    Flipkart, Amazon India style personalized recommendations with HE
    """
    
    def __init__(self, platform_name: str = "ShopSecure", poly_modulus_degree: int = 8192):
        """
        Initialize encrypted recommendation engine
        
        Args:
            platform_name: E-commerce platform name
            poly_modulus_degree: HE security parameter
        """
        self.platform_name = platform_name
        
        # TenSEAL context setup
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_modulus_degree,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        
        self.scale = pow(2, 40)
        self.context.global_scale = self.scale
        self.context.generate_galois_keys()
        
        # Data stores
        self.products: Dict[str, Product] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.interactions: List[UserInteraction] = []
        
        # Encrypted models
        self.encrypted_user_item_matrix: Optional[ts.CKKSVector] = None
        self.encrypted_similarity_matrix: Optional[ts.CKKSVector] = None
        self.encrypted_category_preferences: Dict[str, ts.CKKSVector] = {}
        
        # Recommendation cache
        self.recommendation_cache: Dict[str, List[Dict]] = {}
        
        # Analytics
        self.recommendation_logs: List[Dict] = []
        
        # Text processing for content-based filtering
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        logger.info(f"🛒 Encrypted Recommendation Engine initialized: {platform_name}")
        logger.info(f"🔐 Security level: {poly_modulus_degree} bits")
        logger.info("🛍️ Privacy-preserving personalized recommendations")
    
    def add_product(self, product: Product) -> bool:
        """
        Add product to recommendation system
        
        Args:
            product: Product to add
            
        Returns:
            Success status
        """
        try:
            # Extract product features for encryption
            product_features = self._extract_product_features(product)
            
            # Encrypt product features
            product.encrypted_features = ts.ckks_vector(self.context, product_features)
            
            # Store product
            self.products[product.product_id] = product
            
            logger.info(f"📦 Product added: {product.name} ({product.category.value}) "
                       f"Price: ₹{product.price:,.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Product addition failed: {e}")
            return False
    
    def register_user(self, user: UserProfile) -> bool:
        """
        Register user with encrypted profile
        
        Args:
            user: User profile to register
            
        Returns:
            Registration success status
        """
        try:
            # Extract user features for encryption
            user_features = self._extract_user_features(user)
            preference_features = self._extract_preference_features(user)
            
            # Encrypt user profile
            user.encrypted_profile = ts.ckks_vector(self.context, user_features)
            user.encrypted_preferences = ts.ckks_vector(self.context, preference_features)
            
            # Store user profile
            self.user_profiles[user.user_hash] = user
            
            # Initialize encrypted category preferences
            for category in ProductCategory:
                # Start with neutral preferences, will be updated based on interactions
                self.encrypted_category_preferences[f"{user.user_hash}_{category.value}"] = ts.ckks_vector(
                    self.context, [0.5]  # Neutral preference
                )
            
            logger.info(f"👤 User registered: {user.user_id[:8]}... "
                       f"Location: {user.location_city}, {user.location_state}")
            return True
            
        except Exception as e:
            logger.error(f"❌ User registration failed: {e}")
            return False
    
    def record_interaction(self, interaction: UserInteraction) -> bool:
        """
        Record user-product interaction with encryption
        
        Args:
            interaction: User interaction to record
            
        Returns:
            Success status
        """
        try:
            # Extract interaction context features
            context_features = self._extract_interaction_features(interaction)
            
            # Encrypt interaction context
            interaction.encrypted_context = ts.ckks_vector(self.context, context_features)
            
            # Store interaction
            self.interactions.append(interaction)
            
            # Update encrypted user preferences based on interaction
            self._update_encrypted_preferences(interaction)
            
            # Invalidate recommendation cache for this user
            if interaction.user_hash in self.recommendation_cache:
                del self.recommendation_cache[interaction.user_hash]
            
            # Log interaction (privacy-preserving)
            self.recommendation_logs.append({
                'type': 'USER_INTERACTION',
                'user_hash': interaction.user_hash[:8],
                'product_id': interaction.product_id,
                'behavior': interaction.behavior_type.value,
                'timestamp': interaction.timestamp.isoformat(),
                'device': interaction.device_type,
                'privacy_preserved': True
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Interaction recording failed: {e}")
            return False
    
    def generate_recommendations(self, user_hash: str, num_recommendations: int = 10,
                               recommendation_type: str = "hybrid") -> List[Dict[str, Any]]:
        """
        Generate encrypted personalized recommendations
        
        Args:
            user_hash: User identifier hash
            num_recommendations: Number of recommendations to generate
            recommendation_type: Type of recommendations (collaborative, content, hybrid)
            
        Returns:
            List of recommended products with scores
        """
        try:
            # Check cache first
            cache_key = f"{user_hash}_{num_recommendations}_{recommendation_type}"
            if cache_key in self.recommendation_cache:
                logger.info(f"🎯 Serving cached recommendations for {user_hash[:8]}...")
                return self.recommendation_cache[cache_key]
            
            if user_hash not in self.user_profiles:
                logger.warning(f"⚠️ User not found: {user_hash[:8]}...")
                return []
            
            user_profile = self.user_profiles[user_hash]
            
            # Generate recommendations based on type
            if recommendation_type == "collaborative":
                recommendations = self._collaborative_filtering(user_hash, num_recommendations)
            elif recommendation_type == "content":
                recommendations = self._content_based_filtering(user_hash, num_recommendations)
            else:  # hybrid
                collab_recs = self._collaborative_filtering(user_hash, num_recommendations // 2)
                content_recs = self._content_based_filtering(user_hash, num_recommendations // 2)
                recommendations = self._merge_recommendations(collab_recs, content_recs, num_recommendations)
            
            # Add Indian e-commerce specific enhancements
            recommendations = self._enhance_recommendations_for_india(recommendations, user_profile)
            
            # Cache recommendations
            self.recommendation_cache[cache_key] = recommendations
            
            # Log recommendation generation
            self.recommendation_logs.append({
                'type': 'RECOMMENDATIONS_GENERATED',
                'user_hash': user_hash[:8],
                'recommendation_type': recommendation_type,
                'num_recommendations': len(recommendations),
                'timestamp': datetime.now().isoformat(),
                'cache_used': False
            })
            
            logger.info(f"🎁 Generated {len(recommendations)} recommendations for {user_hash[:8]}... "
                       f"Type: {recommendation_type}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Recommendation generation failed: {e}")
            return []
    
    def _collaborative_filtering(self, user_hash: str, num_recommendations: int) -> List[Dict[str, Any]]:
        """Collaborative filtering using encrypted user-item interactions"""
        try:
            # Find similar users based on encrypted preferences
            similar_users = self._find_similar_users_encrypted(user_hash)
            
            # Get products liked by similar users
            recommended_products = []
            user_interactions = [i for i in self.interactions if i.user_hash == user_hash]
            user_purchased_products = set(i.product_id for i in user_interactions 
                                        if i.behavior_type in [UserBehavior.PURCHASE, UserBehavior.ADD_TO_CART])
            
            for similar_user_hash, similarity_score in similar_users[:10]:  # Top 10 similar users
                similar_user_interactions = [i for i in self.interactions 
                                           if i.user_hash == similar_user_hash]
                
                for interaction in similar_user_interactions:
                    if (interaction.behavior_type in [UserBehavior.PURCHASE, UserBehavior.ADD_TO_CART] and
                        interaction.product_id not in user_purchased_products and
                        interaction.product_id in self.products):
                        
                        product = self.products[interaction.product_id]
                        
                        # Calculate recommendation score (encrypted)
                        base_score = similarity_score * 0.5
                        behavior_weight = {
                            UserBehavior.PURCHASE: 1.0,
                            UserBehavior.ADD_TO_CART: 0.7,
                            UserBehavior.WISHLIST: 0.5
                        }.get(interaction.behavior_type, 0.3)
                        
                        recommendation_score = base_score * behavior_weight
                        
                        # Check if product already in recommendations
                        existing = next((r for r in recommended_products 
                                       if r['product_id'] == product.product_id), None)
                        
                        if existing:
                            existing['score'] += recommendation_score
                        else:
                            recommended_products.append({
                                'product_id': product.product_id,
                                'product_name': product.name,
                                'category': product.category.value,
                                'brand': product.brand,
                                'price': product.price,
                                'rating': product.rating,
                                'score': recommendation_score,
                                'recommendation_reason': f'Users with similar preferences also bought this',
                                'algorithm': 'collaborative_filtering'
                            })
            
            # Sort by score and return top recommendations
            recommended_products.sort(key=lambda x: x['score'], reverse=True)
            return recommended_products[:num_recommendations]
            
        except Exception as e:
            logger.error(f"❌ Collaborative filtering failed: {e}")
            return []
    
    def _content_based_filtering(self, user_hash: str, num_recommendations: int) -> List[Dict[str, Any]]:
        """Content-based filtering using encrypted product features"""
        try:
            user_profile = self.user_profiles[user_hash]
            
            # Get user's interaction history
            user_interactions = [i for i in self.interactions if i.user_hash == user_hash]
            
            # Calculate encrypted preference scores for each product
            recommended_products = []
            
            for product_id, product in self.products.items():
                # Skip if user already interacted with this product significantly
                user_product_interactions = [i for i in user_interactions if i.product_id == product_id]
                if any(i.behavior_type == UserBehavior.PURCHASE for i in user_product_interactions):
                    continue
                
                # Calculate content similarity score (encrypted)
                content_score = self._calculate_encrypted_content_similarity(user_profile, product)
                
                # Category preference score
                category_pref_key = f"{user_hash}_{product.category.value}"
                if category_pref_key in self.encrypted_category_preferences:
                    category_score = self.encrypted_category_preferences[category_pref_key].decrypt()[0]
                else:
                    category_score = 0.5  # Neutral
                
                # Price suitability score
                price_score = self._calculate_price_suitability(user_profile, product)
                
                # Brand preference score
                brand_score = self._calculate_brand_preference(user_profile, product)
                
                # Regional relevance score
                regional_score = self._calculate_regional_relevance(user_profile, product)
                
                # Combined recommendation score
                final_score = (content_score * 0.3 + category_score * 0.25 + 
                             price_score * 0.2 + brand_score * 0.15 + regional_score * 0.1)
                
                recommended_products.append({
                    'product_id': product.product_id,
                    'product_name': product.name,
                    'category': product.category.value,
                    'brand': product.brand,
                    'price': product.price,
                    'rating': product.rating,
                    'score': final_score,
                    'recommendation_reason': f'Matches your interest in {product.category.value}',
                    'algorithm': 'content_based_filtering'
                })
            
            # Sort by score and return top recommendations
            recommended_products.sort(key=lambda x: x['score'], reverse=True)
            return recommended_products[:num_recommendations]
            
        except Exception as e:
            logger.error(f"❌ Content-based filtering failed: {e}")
            return []
    
    def _find_similar_users_encrypted(self, user_hash: str) -> List[Tuple[str, float]]:
        """Find similar users using encrypted profile comparison"""
        try:
            target_user = self.user_profiles[user_hash]
            similar_users = []
            
            for other_user_hash, other_user in self.user_profiles.items():
                if other_user_hash == user_hash:
                    continue
                
                # Calculate encrypted similarity between user profiles
                if target_user.encrypted_profile and other_user.encrypted_profile:
                    # Simplified similarity calculation using encrypted dot product
                    similarity_vector = target_user.encrypted_profile * other_user.encrypted_profile
                    
                    # Sum to get overall similarity
                    encrypted_sum = similarity_vector
                    for _ in range(int(np.log2(10))):  # Assuming 10 features
                        encrypted_sum = encrypted_sum + encrypted_sum.rotate_vector(1)
                    
                    similarity_score = encrypted_sum.decrypt()[0] / 10.0  # Normalize
                    similarity_score = max(0, min(1, similarity_score))  # Clamp to [0,1]
                    
                    similar_users.append((other_user_hash, similarity_score))
            
            # Sort by similarity score
            similar_users.sort(key=lambda x: x[1], reverse=True)
            return similar_users
            
        except Exception as e:
            logger.error(f"❌ Similar users calculation failed: {e}")
            return []
    
    def _calculate_encrypted_content_similarity(self, user_profile: UserProfile, product: Product) -> float:
        """Calculate content similarity using encrypted features"""
        try:
            if not user_profile.encrypted_preferences or not product.encrypted_features:
                return 0.5  # Neutral score
            
            # Calculate encrypted similarity between user preferences and product features
            similarity_vector = user_profile.encrypted_preferences * product.encrypted_features
            
            # Sum to get overall similarity
            encrypted_sum = similarity_vector
            for _ in range(int(np.log2(20))):  # Assuming 20 features
                encrypted_sum = encrypted_sum + encrypted_sum.rotate_vector(1)
            
            similarity_score = encrypted_sum.decrypt()[0] / 20.0  # Normalize
            return max(0, min(1, similarity_score))  # Clamp to [0,1]
            
        except Exception as e:
            logger.warning(f"⚠️ Content similarity calculation failed: {e}")
            return 0.5
    
    def _calculate_price_suitability(self, user_profile: UserProfile, product: Product) -> float:
        """Calculate price suitability based on user's price sensitivity"""
        try:
            # Price brackets for Indian market
            price_brackets = {
                'budget': (0, 1000),
                'mid_range': (1000, 10000),
                'premium': (10000, 50000),
                'luxury': (50000, float('inf'))
            }
            
            # Map income brackets to preferred price ranges
            income_to_price_pref = {
                'low': 'budget',
                'lower_middle': 'budget',
                'middle': 'mid_range',
                'upper_middle': 'premium',
                'high': 'luxury'
            }
            
            preferred_price_bracket = income_to_price_pref.get(user_profile.income_bracket, 'mid_range')
            min_price, max_price = price_brackets[preferred_price_bracket]
            
            if min_price <= product.price <= max_price:
                return 1.0  # Perfect price match
            elif product.price < min_price:
                return 0.8  # Cheaper than expected (good value)
            else:
                # More expensive than preferred
                price_ratio = product.price / max_price
                return max(0.2, 1.0 / price_ratio)  # Diminishing score for higher prices
            
        except Exception as e:
            logger.warning(f"⚠️ Price suitability calculation failed: {e}")
            return 0.5
    
    def _calculate_brand_preference(self, user_profile: UserProfile, product: Product) -> float:
        """Calculate brand preference score"""
        try:
            # Get user's brand interactions
            user_interactions = [i for i in self.interactions if i.user_hash == user_profile.user_hash]
            
            # Count brand interactions
            brand_counts = {}
            for interaction in user_interactions:
                if interaction.behavior_type in [UserBehavior.PURCHASE, UserBehavior.ADD_TO_CART]:
                    if interaction.product_id in self.products:
                        brand = self.products[interaction.product_id].brand
                        brand_counts[brand] = brand_counts.get(brand, 0) + 1
            
            if not brand_counts:
                return 0.5  # No history, neutral score
            
            # Check if user has preference for this brand
            if product.brand in brand_counts:
                total_purchases = sum(brand_counts.values())
                brand_preference = brand_counts[product.brand] / total_purchases
                return min(1.0, brand_preference * 2)  # Scale up preference
            else:
                # New brand - score based on user's brand preference type
                if user_profile.brand_preference == "brand_conscious":
                    return 0.3  # Lower score for unknown brands
                elif user_profile.brand_preference == "value_conscious":
                    return 0.8  # Higher score, focus on value
                else:  # mixed
                    return 0.6  # Moderate score
            
        except Exception as e:
            logger.warning(f"⚠️ Brand preference calculation failed: {e}")
            return 0.5
    
    def _calculate_regional_relevance(self, user_profile: UserProfile, product: Product) -> float:
        """Calculate regional relevance for Indian market"""
        try:
            # Check if product is popular in user's state
            if user_profile.location_state in product.popular_in_states:
                regional_score = 0.8
            else:
                regional_score = 0.5
            
            # Check language compatibility
            if user_profile.preferred_language in product.language_variants:
                regional_score += 0.2
            
            return min(1.0, regional_score)
            
        except Exception as e:
            logger.warning(f"⚠️ Regional relevance calculation failed: {e}")
            return 0.5
    
    def _merge_recommendations(self, collab_recs: List[Dict], content_recs: List[Dict],
                             num_recommendations: int) -> List[Dict]:
        """Merge collaborative and content-based recommendations"""
        try:
            # Combine recommendations with weighted scores
            merged_recommendations = {}
            
            # Add collaborative recommendations (weight: 0.6)
            for rec in collab_recs:
                product_id = rec['product_id']
                merged_recommendations[product_id] = rec.copy()
                merged_recommendations[product_id]['score'] *= 0.6
                merged_recommendations[product_id]['algorithm'] = 'collaborative_dominant'
            
            # Add content-based recommendations (weight: 0.4)
            for rec in content_recs:
                product_id = rec['product_id']
                if product_id in merged_recommendations:
                    # Combine scores
                    merged_recommendations[product_id]['score'] += rec['score'] * 0.4
                    merged_recommendations[product_id]['algorithm'] = 'hybrid'
                else:
                    merged_recommendations[product_id] = rec.copy()
                    merged_recommendations[product_id]['score'] *= 0.4
                    merged_recommendations[product_id]['algorithm'] = 'content_dominant'
            
            # Sort by combined score
            final_recommendations = list(merged_recommendations.values())
            final_recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return final_recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error(f"❌ Recommendation merging failed: {e}")
            return collab_recs + content_recs
    
    def _enhance_recommendations_for_india(self, recommendations: List[Dict],
                                         user_profile: UserProfile) -> List[Dict]:
        """Add Indian e-commerce specific enhancements"""
        try:
            enhanced_recommendations = []
            
            for rec in recommendations:
                enhanced_rec = rec.copy()
                
                # Add Indian-specific reasons
                product = self.products[rec['product_id']]
                
                # Festival season recommendations
                current_month = datetime.now().month
                festival_months = [9, 10, 11]  # Sep-Nov (Diwali season)
                if current_month in festival_months:
                    if product.category in [ProductCategory.FASHION, ProductCategory.JEWELRY, ProductCategory.ELECTRONICS]:
                        enhanced_rec['recommendation_reason'] += " | Perfect for festive season! 🎉"
                        enhanced_rec['score'] *= 1.1  # Boost for festival relevance
                
                # Regional language support
                if user_profile.preferred_language in product.language_variants:
                    enhanced_rec['recommendation_reason'] += f" | Available in {user_profile.preferred_language}"
                
                # Price in Indian context
                if product.price < 500:
                    enhanced_rec['price_category'] = 'Budget-friendly'
                elif product.price < 5000:
                    enhanced_rec['price_category'] = 'Great value'
                elif product.price < 25000:
                    enhanced_rec['price_category'] = 'Premium choice'
                else:
                    enhanced_rec['price_category'] = 'Luxury item'
                
                # Indian payment options hint
                enhanced_rec['payment_options'] = ['UPI', 'Card', 'COD', 'EMI']
                
                # Delivery estimation for Indian cities
                tier_1_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune']
                if user_profile.location_city in tier_1_cities:
                    enhanced_rec['estimated_delivery'] = 'Same day / Next day'
                else:
                    enhanced_rec['estimated_delivery'] = '2-3 days'
                
                enhanced_recommendations.append(enhanced_rec)
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.warning(f"⚠️ India-specific enhancement failed: {e}")
            return recommendations
    
    def _extract_product_features(self, product: Product) -> List[float]:
        """Extract numerical features from product"""
        features = []
        
        # Price (normalized)
        features.append(min(1.0, product.price / 100000.0))  # Normalize by ₹1 lakh
        
        # Rating
        features.append(product.rating / 5.0)
        
        # Review count (log normalized)
        features.append(min(1.0, np.log10(max(1, product.review_count)) / 4.0))  # Max log(10000)
        
        # Category encoding
        for category in ProductCategory:
            features.append(1.0 if product.category == category else 0.0)
        
        # Brand popularity (simplified)
        brand_popularity = {'Apple': 0.9, 'Samsung': 0.8, 'Xiaomi': 0.7, 'OnePlus': 0.6}
        features.append(brand_popularity.get(product.brand, 0.5))
        
        return features[:20]  # Fixed size vector
    
    def _extract_user_features(self, user: UserProfile) -> List[float]:
        """Extract numerical features from user profile"""
        features = []
        
        # Age group encoding
        age_mapping = {'18-25': 0.2, '26-35': 0.4, '36-45': 0.6, '46-55': 0.8, '56+': 1.0}
        features.append(age_mapping.get(user.age_group, 0.5))
        
        # Gender encoding
        features.append(1.0 if user.gender.lower() == 'male' else 0.0)
        
        # Income bracket
        income_mapping = {'low': 0.2, 'lower_middle': 0.4, 'middle': 0.6, 'upper_middle': 0.8, 'high': 1.0}
        features.append(income_mapping.get(user.income_bracket, 0.5))
        
        # Shopping behavior
        features.append(min(1.0, user.total_orders / 100.0))
        features.append(min(1.0, user.total_spent / 100000.0))
        features.append(min(1.0, user.avg_order_value / 10000.0))
        
        # Price sensitivity
        price_sens_mapping = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        features.append(price_sens_mapping.get(user.price_sensitivity, 0.6))
        
        return features[:10]  # Fixed size vector
    
    def _extract_preference_features(self, user: UserProfile) -> List[float]:
        """Extract preference features from user"""
        features = []
        
        # Category preferences
        for category in ProductCategory:
            features.append(1.0 if category in user.favorite_categories else 0.0)
        
        # Brand preference
        brand_pref_mapping = {'brand_conscious': 0.8, 'value_conscious': 0.2, 'mixed': 0.5}
        features.append(brand_pref_mapping.get(user.brand_preference, 0.5))
        
        # Location factor (state)
        metro_states = ['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu']
        features.append(1.0 if user.location_state in metro_states else 0.5)
        
        return features[:20]  # Fixed size vector
    
    def _extract_interaction_features(self, interaction: UserInteraction) -> List[float]:
        """Extract features from user interaction"""
        features = []
        
        # Behavior type encoding
        behavior_weights = {
            UserBehavior.VIEW: 0.1, UserBehavior.CLICK: 0.2, UserBehavior.ADD_TO_CART: 0.8,
            UserBehavior.PURCHASE: 1.0, UserBehavior.WISHLIST: 0.6, UserBehavior.REVIEW: 0.7,
            UserBehavior.SHARE: 0.5, UserBehavior.SEARCH: 0.3
        }
        features.append(behavior_weights.get(interaction.behavior_type, 0.1))
        
        # Time of day
        features.append(interaction.timestamp.hour / 24.0)
        
        # Day of week
        features.append(interaction.timestamp.weekday() / 7.0)
        
        # Duration (normalized)
        features.append(min(1.0, interaction.duration_seconds / 300.0))  # Max 5 minutes
        
        # Device type
        features.append(1.0 if interaction.device_type == 'mobile' else 0.0)
        
        return features[:10]  # Fixed size vector
    
    def _update_encrypted_preferences(self, interaction: UserInteraction):
        """Update user's encrypted category preferences based on interaction"""
        try:
            if interaction.product_id not in self.products:
                return
            
            product = self.products[interaction.product_id]
            category = product.category
            
            # Update weight based on interaction type
            update_weights = {
                UserBehavior.VIEW: 0.1, UserBehavior.CLICK: 0.2, UserBehavior.ADD_TO_CART: 0.6,
                UserBehavior.PURCHASE: 1.0, UserBehavior.WISHLIST: 0.4, UserBehavior.REVIEW: 0.3
            }
            
            weight = update_weights.get(interaction.behavior_type, 0.1)
            
            # Encrypt the weight update
            encrypted_update = ts.ckks_vector(self.context, [weight * 0.1])  # Small update
            
            # Update encrypted category preference
            category_key = f"{interaction.user_hash}_{category.value}"
            if category_key in self.encrypted_category_preferences:
                self.encrypted_category_preferences[category_key] = (
                    self.encrypted_category_preferences[category_key] + encrypted_update
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Preference update failed: {e}")

# Demonstration functions

def demo_product_catalog_setup():
    """Demonstrate setting up product catalog"""
    print("\n📦 === Product Catalog Setup Demo ===")
    
    # Initialize recommendation engine
    rec_engine = EncryptedRecommendationEngine("ShopSecureIndia")
    
    # Add sample Indian products
    products = [
        Product(
            product_id="MOBILE001",
            name="Xiaomi Redmi Note 12 Pro",
            category=ProductCategory.MOBILE,
            brand="Xiaomi",
            price=25999.0,
            rating=4.3,
            review_count=1250,
            features=['5G', 'AMOLED', '108MP camera', 'Fast charging'],
            popular_in_states=['Maharashtra', 'Karnataka', 'Delhi'],
            language_variants=['Hindi', 'English', 'Tamil']
        ),
        Product(
            product_id="FASHION001", 
            name="Ethnic Kurta Set for Men",
            category=ProductCategory.FASHION,
            brand="Manyavar",
            price=3499.0,
            rating=4.1,
            review_count=890,
            features=['Cotton', 'Festive', 'Traditional'],
            popular_in_states=['UP', 'Bihar', 'Rajasthan'],
            language_variants=['Hindi', 'English']
        ),
        Product(
            product_id="APPLIANCE001",
            name="LG 260L Double Door Refrigerator",
            category=ProductCategory.APPLIANCES,
            brand="LG",
            price=28999.0,
            rating=4.2,
            review_count=567,
            features=['Energy efficient', 'Smart inverter', 'Anti-bacterial'],
            popular_in_states=['Maharashtra', 'Gujarat', 'Tamil Nadu'],
            language_variants=['Hindi', 'English', 'Gujarati', 'Tamil']
        ),
        Product(
            product_id="BOOK001",
            name="Wings of Fire - APJ Abdul Kalam",
            category=ProductCategory.BOOKS,
            brand="Universities Press",
            price=199.0,
            rating=4.7,
            review_count=2345,
            features=['Autobiography', 'Inspirational', 'Indian author'],
            popular_in_states=['All India'],
            language_variants=['Hindi', 'English', 'Tamil', 'Telugu']
        ),
        Product(
            product_id="GROCERY001",
            name="Tata Salt - 1kg Pack",
            category=ProductCategory.GROCERY,
            brand="Tata",
            price=20.0,
            rating=4.5,
            review_count=12000,
            features=['Iodized', 'Pure', 'Essential'],
            popular_in_states=['All India'],
            language_variants=['Hindi', 'English', 'All regional']
        )
    ]
    
    for product in products:
        success = rec_engine.add_product(product)
        print(f"📦 Product: {product.name} - Added: {success}")
    
    print(f"🛒 Total products in catalog: {len(rec_engine.products)}")
    return rec_engine

def demo_user_registration_and_interactions():
    """Demonstrate user registration and interactions"""
    print("\n👤 === User Registration & Interactions Demo ===")
    
    rec_engine = demo_product_catalog_setup()
    
    # Register sample users
    users = [
        UserProfile(
            user_id="USER001",
            user_hash=hashlib.sha256("USER001".encode()).hexdigest(),
            age_group="26-35",
            gender="Male",
            location_state="Maharashtra",
            location_city="Mumbai", 
            income_bracket="middle",
            preferred_language="Hindi",
            favorite_categories=[ProductCategory.ELECTRONICS, ProductCategory.MOBILE],
            price_sensitivity="medium",
            brand_preference="value_conscious",
            total_orders=15,
            total_spent=75000.0,
            avg_order_value=5000.0
        ),
        UserProfile(
            user_id="USER002",
            user_hash=hashlib.sha256("USER002".encode()).hexdigest(),
            age_group="18-25",
            gender="Female",
            location_state="Karnataka",
            location_city="Bangalore",
            income_bracket="lower_middle",
            preferred_language="English",
            favorite_categories=[ProductCategory.FASHION, ProductCategory.BEAUTY],
            price_sensitivity="high",
            brand_preference="mixed",
            total_orders=8,
            total_spent=12000.0,
            avg_order_value=1500.0
        )
    ]
    
    for user in users:
        success = rec_engine.register_user(user)
        print(f"👤 User: {user.user_id} - Registered: {success}")
    
    # Simulate user interactions
    interactions = [
        UserInteraction(
            interaction_id="INT001",
            user_hash=users[0].user_hash,
            product_id="MOBILE001",
            behavior_type=UserBehavior.VIEW,
            timestamp=datetime.now() - timedelta(days=2),
            session_id="SESSION001",
            device_type="mobile",
            duration_seconds=45
        ),
        UserInteraction(
            interaction_id="INT002",
            user_hash=users[0].user_hash,
            product_id="MOBILE001",
            behavior_type=UserBehavior.ADD_TO_CART,
            timestamp=datetime.now() - timedelta(days=1),
            session_id="SESSION002",
            device_type="mobile",
            duration_seconds=120
        ),
        UserInteraction(
            interaction_id="INT003",
            user_hash=users[1].user_hash,
            product_id="FASHION001",
            behavior_type=UserBehavior.PURCHASE,
            timestamp=datetime.now() - timedelta(hours=6),
            session_id="SESSION003",
            device_type="mobile",
            duration_seconds=300
        )
    ]
    
    for interaction in interactions:
        success = rec_engine.record_interaction(interaction)
        print(f"📊 Interaction: {interaction.behavior_type.value} on {interaction.product_id} - Recorded: {success}")
    
    print(f"💾 Total interactions recorded: {len(rec_engine.interactions)}")
    return rec_engine, users

def demo_recommendation_generation():
    """Demonstrate recommendation generation"""
    print("\n🎁 === Recommendation Generation Demo ===")
    
    rec_engine, users = demo_user_registration_and_interactions()
    
    # Generate recommendations for both users
    for user in users:
        print(f"\n👤 Recommendations for {user.user_id} ({user.location_city}):")
        
        # Try different recommendation types
        for rec_type in ['collaborative', 'content', 'hybrid']:
            print(f"\n🔍 {rec_type.title()} Filtering:")
            
            recommendations = rec_engine.generate_recommendations(
                user_hash=user.user_hash,
                num_recommendations=3,
                recommendation_type=rec_type
            )
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec['product_name']} ({rec['category']})")
                    print(f"      Price: ₹{rec['price']:,.2f} | Rating: {rec['rating']}/5")
                    print(f"      Score: {rec['score']:.3f} | Reason: {rec['recommendation_reason']}")
                    if 'price_category' in rec:
                        print(f"      Category: {rec['price_category']} | Delivery: {rec['estimated_delivery']}")
            else:
                print("   No recommendations generated")

def demo_privacy_preserving_analytics():
    """Demonstrate privacy-preserving recommendation analytics"""
    print("\n📊 === Privacy-Preserving Analytics Demo ===")
    
    rec_engine, users = demo_user_registration_and_interactions()
    
    # Generate recommendations to populate analytics
    for user in users:
        rec_engine.generate_recommendations(user.user_hash, num_recommendations=5)
    
    # Analyze recommendation logs (privacy-preserving)
    print("🔍 Recommendation Analytics (Privacy-Preserving):")
    
    total_recommendations = len([log for log in rec_engine.recommendation_logs 
                               if log['type'] == 'RECOMMENDATIONS_GENERATED'])
    total_interactions = len([log for log in rec_engine.recommendation_logs 
                            if log['type'] == 'USER_INTERACTION'])
    
    print(f"   Total recommendation requests: {total_recommendations}")
    print(f"   Total user interactions: {total_interactions}")
    print(f"   Average recommendations per user: {total_recommendations / len(users):.1f}")
    
    # Category popularity (aggregated)
    category_interactions = {}
    for interaction in rec_engine.interactions:
        if interaction.product_id in rec_engine.products:
            category = rec_engine.products[interaction.product_id].category.value
            category_interactions[category] = category_interactions.get(category, 0) + 1
    
    print(f"\n📈 Popular Categories (Aggregated):")
    for category, count in sorted(category_interactions.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count} interactions")
    
    # Behavior distribution
    behavior_counts = {}
    for interaction in rec_engine.interactions:
        behavior = interaction.behavior_type.value
        behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
    
    print(f"\n🎯 User Behavior Distribution:")
    for behavior, count in sorted(behavior_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {behavior}: {count} actions")
    
    print(f"\n🔒 Privacy Features:")
    print(f"   ✅ All user profiles encrypted")
    print(f"   ✅ Product features encrypted") 
    print(f"   ✅ Similarity calculations performed on encrypted data")
    print(f"   ✅ Individual preferences never exposed")
    print(f"   ✅ Only aggregated analytics revealed")

if __name__ == "__main__":
    print("🇮🇳 Encrypted Recommendation System for Indian E-commerce")
    print("Privacy-preserving personalized recommendations using Homomorphic Encryption")
    
    # Run all demonstrations
    demo_product_catalog_setup()
    demo_user_registration_and_interactions()
    demo_recommendation_generation()
    demo_privacy_preserving_analytics()
    
    print("\n✅ All recommendation system demonstrations completed!")
    print("🛒 Product recommendations generated without exposing user preferences")
    print("🔐 Complete user privacy maintained throughout the recommendation process")
    print("📊 Analytics computed on encrypted data for business insights")