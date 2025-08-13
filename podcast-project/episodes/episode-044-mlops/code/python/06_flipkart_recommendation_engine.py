#!/usr/bin/env python3
"""
Flipkart-style Recommendation Engine - MLOps Episode 44
Production-ready recommendation system with collaborative filtering and content-based filtering

Author: Claude Code
Context: Real-time recommendation engine like Flipkart's production system
"""

import json
import time
import uuid
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict, Counter
import hashlib
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import scipy.sparse as sp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Types of recommendations"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    TRENDING = "trending"
    PERSONALIZED = "personalized"

class InteractionType(Enum):
    """User interaction types"""
    VIEW = "view"
    CLICK = "click"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    LIKE = "like"
    SHARE = "share"
    REVIEW = "review"

@dataclass
class Product:
    """Product information"""
    product_id: str
    name: str
    category: str
    subcategory: str
    brand: str
    price: float
    rating: float
    num_reviews: int
    description: str
    features: List[str]
    tags: List[str]
    created_at: datetime

@dataclass
class UserInteraction:
    """User-product interaction"""
    interaction_id: str
    user_id: str
    product_id: str
    interaction_type: InteractionType
    rating: Optional[float]
    timestamp: datetime
    session_id: str
    device_type: str
    location: Optional[str]

@dataclass
class RecommendationResult:
    """Recommendation result"""
    user_id: str
    product_id: str
    score: float
    rank: int
    algorithm: RecommendationType
    explanation: str
    confidence: float
    timestamp: datetime

@dataclass
class UserProfile:
    """User profile for recommendations"""
    user_id: str
    preferred_categories: List[str]
    preferred_brands: List[str]
    price_range: Tuple[float, float]
    avg_rating_given: float
    total_purchases: int
    favorite_features: List[str]
    last_active: datetime

class FlipkartRecommendationEngine:
    """
    Production Recommendation Engine for Flipkart-style e-commerce
    Mumbai me sabse advanced recommendation system!
    """
    
    def __init__(self, db_path: str = "flipkart_recommendations.db"):
        self.db_path = db_path
        self.user_item_matrix = None
        self.content_features = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.svd_model = TruncatedSVD(n_components=50, random_state=42)
        self.scaler = StandardScaler()
        
        # In-memory caches for performance
        self.user_profiles: Dict[str, UserProfile] = {}
        self.product_catalog: Dict[str, Product] = {}
        self.user_interactions: Dict[str, List[UserInteraction]] = defaultdict(list)
        self.product_similarity_cache: Dict[str, Dict[str, float]] = {}
        self.trending_products: List[str] = []
        
        # Recommendation weights
        self.interaction_weights = {
            InteractionType.VIEW: 1.0,
            InteractionType.CLICK: 2.0,
            InteractionType.ADD_TO_CART: 3.0,
            InteractionType.LIKE: 2.5,
            InteractionType.SHARE: 3.0,
            InteractionType.REVIEW: 4.0,
            InteractionType.PURCHASE: 5.0
        }
        
        self.lock = threading.Lock()
        self._init_database()
        self._load_data()
    
    def _init_database(self):
        """Initialize recommendation database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    brand TEXT,
                    price REAL NOT NULL,
                    rating REAL DEFAULT 0.0,
                    num_reviews INTEGER DEFAULT 0,
                    description TEXT,
                    features TEXT,
                    tags TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    interaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    rating REAL,
                    timestamp TEXT NOT NULL,
                    session_id TEXT,
                    device_type TEXT,
                    location TEXT,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    recommendation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    score REAL NOT NULL,
                    rank_position INTEGER NOT NULL,
                    algorithm TEXT NOT NULL,
                    explanation TEXT,
                    confidence REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    preferred_categories TEXT,
                    preferred_brands TEXT,
                    min_price REAL DEFAULT 0.0,
                    max_price REAL DEFAULT 999999.0,
                    avg_rating_given REAL DEFAULT 0.0,
                    total_purchases INTEGER DEFAULT 0,
                    favorite_features TEXT,
                    last_active TEXT
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_interactions_user ON user_interactions (user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_interactions_product ON user_interactions (product_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_interactions_time ON user_interactions (timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations (user_id)')
    
    def _load_data(self):
        """Load data from database into memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load products
                cursor = conn.execute("SELECT * FROM products")
                for row in cursor.fetchall():
                    product = Product(
                        product_id=row[0],
                        name=row[1],
                        category=row[2],
                        subcategory=row[3] or "",
                        brand=row[4] or "",
                        price=row[5],
                        rating=row[6],
                        num_reviews=row[7],
                        description=row[8] or "",
                        features=json.loads(row[9]) if row[9] else [],
                        tags=json.loads(row[10]) if row[10] else [],
                        created_at=datetime.fromisoformat(row[11])
                    )
                    self.product_catalog[product.product_id] = product
                
                # Load interactions
                cursor = conn.execute("SELECT * FROM user_interactions ORDER BY timestamp")
                for row in cursor.fetchall():
                    interaction = UserInteraction(
                        interaction_id=row[0],
                        user_id=row[1],
                        product_id=row[2],
                        interaction_type=InteractionType(row[3]),
                        rating=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                        session_id=row[6] or "",
                        device_type=row[7] or "",
                        location=row[8] or ""
                    )
                    self.user_interactions[interaction.user_id].append(interaction)
                
                logger.info(f"Loaded {len(self.product_catalog)} products and {sum(len(interactions) for interactions in self.user_interactions.values())} interactions")
                
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
    
    def add_product(self, product: Product) -> bool:
        """Add new product to catalog"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.product_id, product.name, product.category, product.subcategory,
                    product.brand, product.price, product.rating, product.num_reviews,
                    product.description, json.dumps(product.features), json.dumps(product.tags),
                    product.created_at.isoformat()
                ))
            
            with self.lock:
                self.product_catalog[product.product_id] = product
            
            logger.info(f"Product added: {product.product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add product: {e}")
            return False
    
    def record_interaction(self, interaction: UserInteraction) -> bool:
        """
        Record user-product interaction
        Mumbai me user interaction ka record!
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO user_interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.interaction_id, interaction.user_id, interaction.product_id,
                    interaction.interaction_type.value, interaction.rating,
                    interaction.timestamp.isoformat(), interaction.session_id,
                    interaction.device_type, interaction.location
                ))
            
            with self.lock:
                self.user_interactions[interaction.user_id].append(interaction)
            
            # Update user profile asynchronously
            self._update_user_profile(interaction.user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record interaction: {e}")
            return False
    
    def _update_user_profile(self, user_id: str):
        """Update user profile based on interactions"""
        interactions = self.user_interactions[user_id]
        
        if not interactions:
            return
        
        # Calculate preferences
        category_counts = Counter()
        brand_counts = Counter()
        prices = []
        ratings = []
        feature_counts = Counter()
        purchase_count = 0
        
        for interaction in interactions:
            product = self.product_catalog.get(interaction.product_id)
            if not product:
                continue
            
            # Weight by interaction type
            weight = self.interaction_weights[interaction.interaction_type]
            
            category_counts[product.category] += weight
            brand_counts[product.brand] += weight
            prices.append(product.price)
            
            if interaction.rating:
                ratings.append(interaction.rating)
            
            for feature in product.features:
                feature_counts[feature] += weight
            
            if interaction.interaction_type == InteractionType.PURCHASE:
                purchase_count += 1
        
        # Create user profile
        preferred_categories = [cat for cat, _ in category_counts.most_common(5)]
        preferred_brands = [brand for brand, _ in brand_counts.most_common(5)]
        price_range = (min(prices) if prices else 0.0, max(prices) if prices else 999999.0)
        avg_rating = np.mean(ratings) if ratings else 0.0
        favorite_features = [feat for feat, _ in feature_counts.most_common(10)]
        
        profile = UserProfile(
            user_id=user_id,
            preferred_categories=preferred_categories,
            preferred_brands=preferred_brands,
            price_range=price_range,
            avg_rating_given=avg_rating,
            total_purchases=purchase_count,
            favorite_features=favorite_features,
            last_active=max(interaction.timestamp for interaction in interactions)
        )
        
        with self.lock:
            self.user_profiles[user_id] = profile
    
    def _build_user_item_matrix(self) -> sp.csr_matrix:
        """
        Build user-item interaction matrix
        Mumbai me user-item matrix ka construction!
        """
        user_ids = list(self.user_interactions.keys())
        product_ids = list(self.product_catalog.keys())
        
        user_to_idx = {user_id: idx for idx, user_id in enumerate(user_ids)}
        product_to_idx = {product_id: idx for idx, product_id in enumerate(product_ids)}
        
        # Create sparse matrix
        row_indices = []
        col_indices = []
        data = []
        
        for user_id, interactions in self.user_interactions.items():
            if user_id not in user_to_idx:
                continue
            
            user_idx = user_to_idx[user_id]
            
            for interaction in interactions:
                if interaction.product_id not in product_to_idx:
                    continue
                
                product_idx = product_to_idx[interaction.product_id]
                weight = self.interaction_weights[interaction.interaction_type]
                
                # Add rating if available
                if interaction.rating:
                    weight *= interaction.rating / 5.0
                
                row_indices.append(user_idx)
                col_indices.append(product_idx)
                data.append(weight)
        
        matrix = sp.csr_matrix(
            (data, (row_indices, col_indices)),
            shape=(len(user_ids), len(product_ids))
        )
        
        return matrix, user_to_idx, product_to_idx
    
    def _collaborative_filtering_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """
        Generate collaborative filtering recommendations
        Mumbai me collaborative filtering ka magic!
        """
        try:
            # Build user-item matrix
            matrix, user_to_idx, product_to_idx = self._build_user_item_matrix()
            
            if user_id not in user_to_idx:
                return []
            
            user_idx = user_to_idx[user_id]
            
            # Train SVD model
            user_factors = self.svd_model.fit_transform(matrix)
            item_factors = self.svd_model.components_.T
            
            # Get user vector
            user_vector = user_factors[user_idx]
            
            # Calculate scores for all items
            scores = np.dot(item_factors, user_vector)
            
            # Get user's already interacted items
            interacted_items = set()
            for interaction in self.user_interactions[user_id]:
                if interaction.product_id in product_to_idx:
                    interacted_items.add(product_to_idx[interaction.product_id])
            
            # Get top recommendations (excluding already interacted)
            recommendations = []
            product_ids = list(product_to_idx.keys())
            
            for product_idx in np.argsort(scores)[::-1]:
                if product_idx in interacted_items:
                    continue
                
                if len(recommendations) >= n_recommendations:
                    break
                
                product_id = product_ids[product_idx]
                score = scores[product_idx]
                
                recommendation = RecommendationResult(
                    user_id=user_id,
                    product_id=product_id,
                    score=float(score),
                    rank=len(recommendations) + 1,
                    algorithm=RecommendationType.COLLABORATIVE_FILTERING,
                    explanation="Based on similar users' preferences",
                    confidence=min(0.95, max(0.1, float(score) / np.max(scores))),
                    timestamp=datetime.now()
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Collaborative filtering error: {e}")
            return []
    
    def _content_based_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """
        Generate content-based recommendations
        Mumbai me content-based filtering!
        """
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                return []
            
            # Get user's interaction history
            user_interactions = self.user_interactions[user_id]
            if not user_interactions:
                return []
            
            # Get products user has interacted with
            interacted_products = set(interaction.product_id for interaction in user_interactions)
            
            # Build content features for all products
            product_features = []
            product_ids = []
            
            for product_id, product in self.product_catalog.items():
                if product_id in interacted_products:
                    continue
                
                # Create feature vector
                features = f"{product.category} {product.subcategory} {product.brand} {product.description} {' '.join(product.features)} {' '.join(product.tags)}"
                product_features.append(features)
                product_ids.append(product_id)
            
            if not product_features:
                return []
            
            # Create TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(product_features)
            
            # Calculate user preference vector based on interacted products
            user_feature_vector = np.zeros(tfidf_matrix.shape[1])
            total_weight = 0
            
            for interaction in user_interactions:
                product = self.product_catalog.get(interaction.product_id)
                if not product:
                    continue
                
                weight = self.interaction_weights[interaction.interaction_type]
                if interaction.rating:
                    weight *= interaction.rating / 5.0
                
                # Get product features
                product_text = f"{product.category} {product.subcategory} {product.brand} {product.description} {' '.join(product.features)} {' '.join(product.tags)}"
                product_vector = self.tfidf_vectorizer.transform([product_text])
                
                user_feature_vector += weight * product_vector.toarray()[0]
                total_weight += weight
            
            if total_weight > 0:
                user_feature_vector /= total_weight
            
            # Calculate similarity scores
            user_vector = user_feature_vector.reshape(1, -1)
            similarities = cosine_similarity(user_vector, tfidf_matrix)[0]
            
            # Generate recommendations
            recommendations = []
            for idx in np.argsort(similarities)[::-1]:
                if len(recommendations) >= n_recommendations:
                    break
                
                product_id = product_ids[idx]
                score = similarities[idx]
                
                if score < 0.1:  # Minimum similarity threshold
                    break
                
                # Add category and brand preference bonus
                product = self.product_catalog[product_id]
                bonus = 0.0
                
                if product.category in user_profile.preferred_categories:
                    bonus += 0.1
                
                if product.brand in user_profile.preferred_brands:
                    bonus += 0.05
                
                # Price preference
                if user_profile.price_range[0] <= product.price <= user_profile.price_range[1]:
                    bonus += 0.05
                
                final_score = score + bonus
                
                recommendation = RecommendationResult(
                    user_id=user_id,
                    product_id=product_id,
                    score=float(final_score),
                    rank=len(recommendations) + 1,
                    algorithm=RecommendationType.CONTENT_BASED,
                    explanation=f"Based on your interest in {product.category} products",
                    confidence=min(0.95, max(0.1, float(final_score))),
                    timestamp=datetime.now()
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Content-based filtering error: {e}")
            return []
    
    def _trending_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """
        Generate trending product recommendations
        Mumbai me trending products!
        """
        try:
            # Calculate trending score based on recent interactions
            cutoff_time = datetime.now() - timedelta(hours=24)
            product_scores = defaultdict(float)
            
            for interactions in self.user_interactions.values():
                for interaction in interactions:
                    if interaction.timestamp > cutoff_time:
                        weight = self.interaction_weights[interaction.interaction_type]
                        # More recent interactions get higher weight
                        time_weight = 1.0 - (datetime.now() - interaction.timestamp).total_seconds() / (24 * 3600)
                        product_scores[interaction.product_id] += weight * time_weight
            
            # Get user's already interacted items
            user_interactions = self.user_interactions.get(user_id, [])
            interacted_products = set(interaction.product_id for interaction in user_interactions)
            
            # Generate recommendations
            recommendations = []
            for product_id, score in sorted(product_scores.items(), key=lambda x: x[1], reverse=True):
                if product_id in interacted_products:
                    continue
                
                if len(recommendations) >= n_recommendations:
                    break
                
                if product_id not in self.product_catalog:
                    continue
                
                recommendation = RecommendationResult(
                    user_id=user_id,
                    product_id=product_id,
                    score=float(score),
                    rank=len(recommendations) + 1,
                    algorithm=RecommendationType.TRENDING,
                    explanation="Currently trending among users",
                    confidence=min(0.9, max(0.3, float(score) / max(product_scores.values()))),
                    timestamp=datetime.now()
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Trending recommendations error: {e}")
            return []
    
    def get_recommendations(self, user_id: str, n_recommendations: int = 10, algorithm: RecommendationType = RecommendationType.HYBRID) -> List[RecommendationResult]:
        """
        Get personalized recommendations for user
        Mumbai me personalized recommendations!
        """
        start_time = time.time()
        
        try:
            if algorithm == RecommendationType.COLLABORATIVE_FILTERING:
                recommendations = self._collaborative_filtering_recommendations(user_id, n_recommendations)
            elif algorithm == RecommendationType.CONTENT_BASED:
                recommendations = self._content_based_recommendations(user_id, n_recommendations)
            elif algorithm == RecommendationType.TRENDING:
                recommendations = self._trending_recommendations(user_id, n_recommendations)
            elif algorithm == RecommendationType.HYBRID:
                # Combine multiple algorithms
                cf_recs = self._collaborative_filtering_recommendations(user_id, n_recommendations // 2)
                cb_recs = self._content_based_recommendations(user_id, n_recommendations // 2)
                trending_recs = self._trending_recommendations(user_id, max(2, n_recommendations // 5))
                
                # Merge and re-rank
                all_recs = cf_recs + cb_recs + trending_recs
                
                # Remove duplicates and re-rank
                seen_products = set()
                merged_recs = []
                
                for rec in sorted(all_recs, key=lambda x: x.score, reverse=True):
                    if rec.product_id not in seen_products and len(merged_recs) < n_recommendations:
                        rec.rank = len(merged_recs) + 1
                        rec.algorithm = RecommendationType.HYBRID
                        merged_recs.append(rec)
                        seen_products.add(rec.product_id)
                
                recommendations = merged_recs
            else:
                recommendations = []
            
            # Store recommendations
            self._store_recommendations(recommendations)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Generated {len(recommendations)} recommendations for {user_id} in {processing_time:.2f}ms")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _store_recommendations(self, recommendations: List[RecommendationResult]):
        """Store recommendations in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for rec in recommendations:
                    conn.execute('''
                        INSERT INTO recommendations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(uuid.uuid4()), rec.user_id, rec.product_id, rec.score,
                        rec.rank, rec.algorithm.value, rec.explanation, rec.confidence,
                        rec.timestamp.isoformat()
                    ))
        except Exception as e:
            logger.error(f"Failed to store recommendations: {e}")
    
    def get_similar_products(self, product_id: str, n_similar: int = 5) -> List[Tuple[str, float]]:
        """
        Get products similar to given product
        Mumbai me similar products ka search!
        """
        try:
            if product_id not in self.product_catalog:
                return []
            
            target_product = self.product_catalog[product_id]
            
            # Calculate similarity scores
            similarities = []
            
            for other_product_id, other_product in self.product_catalog.items():
                if other_product_id == product_id:
                    continue
                
                # Content similarity
                target_features = f"{target_product.category} {target_product.subcategory} {target_product.brand} {target_product.description} {' '.join(target_product.features)}"
                other_features = f"{other_product.category} {other_product.subcategory} {other_product.brand} {other_product.description} {' '.join(other_product.features)}"
                
                tfidf_matrix = self.tfidf_vectorizer.fit_transform([target_features, other_features])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                
                # Add category bonus
                if target_product.category == other_product.category:
                    similarity += 0.1
                
                # Add brand bonus
                if target_product.brand == other_product.brand:
                    similarity += 0.05
                
                # Price similarity bonus
                price_ratio = min(target_product.price, other_product.price) / max(target_product.price, other_product.price)
                similarity += 0.05 * price_ratio
                
                similarities.append((other_product_id, similarity))
            
            # Sort by similarity and return top N
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:n_similar]
            
        except Exception as e:
            logger.error(f"Failed to get similar products: {e}")
            return []
    
    def get_recommendation_stats(self) -> Dict[str, Any]:
        """Get recommendation system statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Basic stats
            cursor = conn.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(DISTINCT user_id) FROM user_interactions")
            total_users = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM user_interactions")
            total_interactions = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM recommendations")
            total_recommendations = cursor.fetchone()[0]
            
            # Interaction type distribution
            cursor = conn.execute('''
                SELECT interaction_type, COUNT(*) 
                FROM user_interactions 
                GROUP BY interaction_type
            ''')
            interaction_distribution = dict(cursor.fetchall())
            
            return {
                'total_products': total_products,
                'total_users': total_users,
                'total_interactions': total_interactions,
                'total_recommendations': total_recommendations,
                'interaction_distribution': interaction_distribution,
                'avg_interactions_per_user': total_interactions / max(total_users, 1),
                'catalog_coverage': len(self.product_catalog) / max(total_products, 1) * 100
            }

def create_sample_ecommerce_data():
    """
    Create sample e-commerce data for testing
    Mumbai me sample e-commerce data!
    """
    # Sample categories and brands
    categories = {
        'Electronics': ['Mobile', 'Laptop', 'Headphones', 'Camera', 'Television'],
        'Fashion': ['Clothing', 'Shoes', 'Accessories', 'Bags', 'Watches'],
        'Home': ['Furniture', 'Kitchen', 'Decor', 'Garden', 'Storage'],
        'Books': ['Fiction', 'Non-Fiction', 'Academic', 'Comics', 'Children'],
        'Sports': ['Fitness', 'Outdoor', 'Cricket', 'Football', 'Swimming']
    }
    
    brands = ['Samsung', 'Apple', 'Sony', 'Nike', 'Adidas', 'Puma', 'Levi\'s', 'H&M', 'IKEA', 'Philips']
    
    products = []
    
    # Generate products
    for i in range(500):
        category = np.random.choice(list(categories.keys()))
        subcategory = np.random.choice(categories[category])
        brand = np.random.choice(brands)
        
        product = Product(
            product_id=f"prod_{i:04d}",
            name=f"{brand} {subcategory} {i+1}",
            category=category,
            subcategory=subcategory,
            brand=brand,
            price=round(np.random.lognormal(6, 1), 2),  # Log-normal price distribution
            rating=round(np.random.uniform(3.0, 5.0), 1),
            num_reviews=np.random.randint(0, 1000),
            description=f"High quality {subcategory.lower()} from {brand}",
            features=[f"feature_{j}" for j in range(np.random.randint(1, 6))],
            tags=[f"tag_{j}" for j in range(np.random.randint(1, 4))],
            created_at=datetime.now() - timedelta(days=np.random.randint(1, 365))
        )
        
        products.append(product)
    
    return products

def generate_user_interactions(products: List[Product], n_users: int = 100, n_interactions: int = 5000):
    """Generate realistic user interactions"""
    interactions = []
    user_ids = [f"user_{i:04d}" for i in range(n_users)]
    
    for i in range(n_interactions):
        user_id = np.random.choice(user_ids)
        product = np.random.choice(products)
        interaction_type = np.random.choice(list(InteractionType), p=[0.4, 0.2, 0.15, 0.1, 0.05, 0.05, 0.05])
        
        rating = None
        if interaction_type in [InteractionType.REVIEW, InteractionType.PURCHASE]:
            rating = np.random.randint(1, 6)
        
        interaction = UserInteraction(
            interaction_id=f"int_{i:06d}",
            user_id=user_id,
            product_id=product.product_id,
            interaction_type=interaction_type,
            rating=rating,
            timestamp=datetime.now() - timedelta(hours=np.random.randint(1, 24*30)),
            session_id=f"session_{np.random.randint(1, 1000)}",
            device_type=np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.6, 0.3, 0.1]),
            location=np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'])
        )
        
        interactions.append(interaction)
    
    return interactions

def main():
    """
    Demo Flipkart Recommendation Engine
    Mumbai ke recommendation engine ka demo!
    """
    print("🛍️ Starting Flipkart Recommendation Engine Demo")
    print("=" * 60)
    
    # Initialize recommendation engine
    engine = FlipkartRecommendationEngine("flipkart_rec_demo.db")
    
    # Create sample data
    print("\n📦 Creating sample e-commerce data...")
    products = create_sample_ecommerce_data()
    
    # Add products to catalog
    print(f"Adding {len(products)} products to catalog...")
    for product in products:
        engine.add_product(product)
    
    # Generate user interactions
    print("\n👥 Generating user interactions...")
    interactions = generate_user_interactions(products, n_users=50, n_interactions=2000)
    
    print(f"Recording {len(interactions)} user interactions...")
    for interaction in interactions:
        engine.record_interaction(interaction)
    
    # Get recommendation stats
    print("\n📊 Recommendation System Statistics:")
    stats = engine.get_recommendation_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Test recommendations for sample users
    print("\n🎯 Testing Recommendations:")
    
    test_users = ["user_0001", "user_0002", "user_0003"]
    
    for user_id in test_users:
        print(f"\n  User: {user_id}")
        
        # Test different algorithms
        for algorithm in [RecommendationType.COLLABORATIVE_FILTERING, RecommendationType.CONTENT_BASED, RecommendationType.HYBRID]:
            print(f"\n    {algorithm.value.upper()} Recommendations:")
            
            recommendations = engine.get_recommendations(user_id, n_recommendations=5, algorithm=algorithm)
            
            for i, rec in enumerate(recommendations[:3], 1):
                product = engine.product_catalog[rec.product_id]
                print(f"      {i}. {product.name} ({product.category})")
                print(f"         Price: ₹{product.price:.2f} | Score: {rec.score:.3f} | Confidence: {rec.confidence:.3f}")
                print(f"         Explanation: {rec.explanation}")
    
    # Test similar products
    print(f"\n🔍 Similar Products Example:")
    sample_product = products[0]
    print(f"Product: {sample_product.name} ({sample_product.category})")
    
    similar_products = engine.get_similar_products(sample_product.product_id, n_similar=3)
    print(f"Similar Products:")
    
    for product_id, similarity in similar_products:
        product = engine.product_catalog[product_id]
        print(f"  - {product.name} ({product.category}) - Similarity: {similarity:.3f}")
    
    # Performance metrics
    print(f"\n⚡ Performance Test:")
    start_time = time.time()
    
    # Generate recommendations for multiple users
    for user_id in test_users:
        recommendations = engine.get_recommendations(user_id, n_recommendations=10, algorithm=RecommendationType.HYBRID)
    
    total_time = (time.time() - start_time) * 1000
    avg_time = total_time / len(test_users)
    
    print(f"  Total Time: {total_time:.2f}ms")
    print(f"  Average Time per User: {avg_time:.2f}ms")
    print(f"  Throughput: {1000 / avg_time:.0f} recommendations/second")
    
    print(f"\n✅ Recommendation engine demo completed!")
    print("Mumbai me recommendation engine bhi perfect shopping companion!")

if __name__ == "__main__":
    main()