#!/usr/bin/env python3
"""
Feature Store Client for AI at Scale
Episode 5: Code Example 3

Production-ready feature store for Indian user preferences and real-time ML
Supporting real-time features, batch features, and feature versioning

Author: Code Developer Agent
Context: Paytm/PhonePe scale feature engineering for Indian users
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import redis
import asyncpg
from sqlalchemy import create_engine, text
import logging
import pickle
from concurrent.futures import ThreadPoolExecutor
import requests
from abc import ABC, abstractmethod

# Mumbai production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureType(Enum):
    REAL_TIME = "real_time"
    BATCH = "batch" 
    STREAMING = "streaming"
    COMPUTED = "computed"

class FeatureStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"

@dataclass
class FeatureConfig:
    """Feature configuration for Indian context"""
    name: str
    version: str
    feature_type: FeatureType
    data_type: str  # int, float, str, list, dict
    description: str
    owner_team: str
    tags: List[str]
    ttl_seconds: int = 3600  # 1 hour default
    compute_cost_inr: float = 0.001  # ₹0.001 per computation
    
    # Indian context specific
    supports_hindi: bool = False
    regional_variations: List[str] = None  # ["north", "south", "east", "west"]
    tier_specific: bool = False  # Tier 1/2/3 city specific
    
    def __post_init__(self):
        if self.regional_variations is None:
            self.regional_variations = []

@dataclass 
class FeatureValue:
    """Feature value with metadata"""
    feature_name: str
    value: Any
    timestamp: float
    version: str
    confidence: float = 1.0
    region: Optional[str] = None
    tier: Optional[int] = None
    computed_cost_inr: float = 0.0

class FeatureComputer(ABC):
    """Abstract base class for feature computation"""
    
    @abstractmethod
    async def compute(self, user_id: str, context: Dict[str, Any]) -> FeatureValue:
        pass

class IndianUserBehaviorComputer(FeatureComputer):
    """
    Compute Indian user behavior features
    Context: UPI usage, regional preferences, festival patterns
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        
    async def compute(self, user_id: str, context: Dict[str, Any]) -> FeatureValue:
        """Compute user behavior score for Indian context"""
        
        try:
            async with self.db_pool.acquire() as conn:
                # Query user transaction patterns
                query = """
                SELECT 
                    COUNT(*) as transaction_count,
                    AVG(amount) as avg_amount,
                    COUNT(DISTINCT merchant_category) as category_diversity,
                    COUNT(CASE WHEN payment_method = 'UPI' THEN 1 END) as upi_count,
                    MAX(created_at) as last_transaction,
                    STRING_AGG(DISTINCT region, ',') as regions,
                    AVG(CASE WHEN EXTRACT(HOUR FROM created_at) BETWEEN 9 AND 18 THEN 1 ELSE 0 END) as business_hours_ratio
                FROM user_transactions 
                WHERE user_id = $1 
                AND created_at >= NOW() - INTERVAL '30 days'
                """
                
                result = await conn.fetchrow(query, user_id)
                
                if not result or result['transaction_count'] == 0:
                    # New user - assign based on region and tier
                    region = context.get('region', 'unknown')
                    tier = context.get('tier', 3)
                    
                    behavior_score = self._calculate_new_user_score(region, tier)
                else:
                    behavior_score = self._calculate_behavior_score(result)
                
                return FeatureValue(
                    feature_name="user_behavior_score",
                    value=behavior_score,
                    timestamp=time.time(),
                    version="1.2.0",
                    confidence=0.85 if result and result['transaction_count'] > 10 else 0.6,
                    region=context.get('region'),
                    tier=context.get('tier'),
                    computed_cost_inr=0.002
                )
                
        except Exception as e:
            logger.error(f"Error computing user behavior for {user_id}: {e}")
            
            # Return safe default
            return FeatureValue(
                feature_name="user_behavior_score", 
                value=0.5,
                timestamp=time.time(),
                version="1.2.0",
                confidence=0.3,
                computed_cost_inr=0.001
            )
    
    def _calculate_new_user_score(self, region: str, tier: int) -> float:
        """Calculate score for new users based on regional data"""
        
        # Regional preferences (based on Indian market research)
        regional_multipliers = {
            "north": 0.8,  # Delhi, Punjab - conservative
            "west": 0.9,   # Mumbai, Gujarat - tech-savvy
            "south": 0.85, # Bangalore, Chennai - balanced
            "east": 0.7,   # Kolkata - cautious
            "northeast": 0.75
        }
        
        # Tier multipliers
        tier_multipliers = {1: 0.9, 2: 0.75, 3: 0.6}
        
        base_score = 0.5
        regional_factor = regional_multipliers.get(region, 0.7)
        tier_factor = tier_multipliers.get(tier, 0.6)
        
        return min(1.0, base_score * regional_factor * tier_factor)
    
    def _calculate_behavior_score(self, data: Dict) -> float:
        """Calculate behavior score from transaction data"""
        
        # Normalize transaction frequency (Indian context)
        freq_score = min(1.0, data['transaction_count'] / 100)  # 100 transactions/month = max
        
        # UPI adoption (very important in India)
        upi_ratio = data['upi_count'] / max(1, data['transaction_count'])
        upi_score = upi_ratio * 0.3  # 30% weightage for UPI usage
        
        # Category diversity (broader financial behavior)
        diversity_score = min(1.0, data['category_diversity'] / 10) * 0.2
        
        # Recency (how recently active)
        days_since_last = (datetime.now() - data['last_transaction']).days
        recency_score = max(0, (30 - days_since_last) / 30) * 0.3
        
        # Business hours usage (professional vs casual)
        business_score = data['business_hours_ratio'] * 0.2
        
        final_score = freq_score * 0.4 + upi_score + diversity_score + recency_score + business_score
        return min(1.0, final_score)

class RegionalPreferenceComputer(FeatureComputer):
    """
    Compute regional preferences for Indian users
    Context: Language, cuisine, shopping patterns, festival preferences
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Pre-computed regional preferences (from market research)
        self.regional_preferences = {
            "north": {
                "languages": ["hi", "pa", "ur"],
                "cuisine": ["punjabi", "mughlai", "rajasthani"],
                "festivals": ["diwali", "holi", "karva_chauth", "dussehra"],
                "shopping": ["traditional_wear", "jewelry", "sweets"],
                "payment_preference": "upi_preferred"
            },
            "south": {
                "languages": ["ta", "te", "kn", "ml"],
                "cuisine": ["south_indian", "biryani", "seafood"],
                "festivals": ["pongal", "onam", "ugadi", "dussehra"],
                "shopping": ["silk_sarees", "electronics", "books"],
                "payment_preference": "digital_wallet"
            },
            "west": {
                "languages": ["hi", "gu", "mr"],
                "cuisine": ["gujarati", "maharashtrian", "street_food"],
                "festivals": ["navratri", "ganesh_chaturthi", "gudi_padwa"],
                "shopping": ["branded_clothes", "gadgets", "home_decor"],
                "payment_preference": "credit_card"
            },
            "east": {
                "languages": ["bn", "hi", "or"],
                "cuisine": ["bengali", "sweets", "fish"],
                "festivals": ["durga_puja", "kali_puja", "poila_boishakh"],
                "shopping": ["books", "traditional_sweets", "handloom"],
                "payment_preference": "cash_preferred"
            }
        }
    
    async def compute(self, user_id: str, context: Dict[str, Any]) -> FeatureValue:
        """Compute regional preferences for user"""
        
        region = context.get('region', 'unknown')
        user_tier = context.get('tier', 3)
        
        if region not in self.regional_preferences:
            # Try to infer from cached user data
            cached_region = await self._get_cached_region(user_id)
            region = cached_region or 'west'  # Default to west (Mumbai)
        
        preferences = self.regional_preferences.get(region, self.regional_preferences['west'])
        
        # Adjust preferences based on tier
        adjusted_preferences = self._adjust_for_tier(preferences, user_tier)
        
        # Cache the result
        await self._cache_preferences(user_id, region, adjusted_preferences)
        
        return FeatureValue(
            feature_name="regional_preferences",
            value=adjusted_preferences,
            timestamp=time.time(),
            version="2.1.0",
            confidence=0.9 if region != 'unknown' else 0.6,
            region=region,
            tier=user_tier,
            computed_cost_inr=0.001
        )
    
    async def _get_cached_region(self, user_id: str) -> Optional[str]:
        """Get cached region for user"""
        try:
            cached = await self.redis.get(f"user_region:{user_id}")
            return cached
        except:
            return None
    
    async def _cache_preferences(self, user_id: str, region: str, preferences: Dict):
        """Cache user preferences"""
        try:
            await self.redis.setex(
                f"user_preferences:{user_id}",
                3600,  # 1 hour
                json.dumps(preferences)
            )
            await self.redis.setex(f"user_region:{user_id}", 86400, region)  # 24 hours
        except Exception as e:
            logger.warning(f"Failed to cache preferences: {e}")
    
    def _adjust_for_tier(self, preferences: Dict, tier: int) -> Dict:
        """Adjust preferences based on city tier"""
        
        adjusted = preferences.copy()
        
        if tier == 1:  # Metro cities
            adjusted["shopping"].extend(["luxury_brands", "imported_goods"])
            adjusted["digital_adoption"] = "high"
            adjusted["delivery_preference"] = "same_day"
        elif tier == 2:  # Tier 2 cities  
            adjusted["shopping"].extend(["local_brands", "value_for_money"])
            adjusted["digital_adoption"] = "medium"
            adjusted["delivery_preference"] = "next_day"
        else:  # Tier 3+ cities
            adjusted["shopping"] = ["local_products", "essentials", "traditional"]
            adjusted["digital_adoption"] = "low"
            adjusted["delivery_preference"] = "standard"
            adjusted["cash_preference"] = "high"
        
        return adjusted

class FeatureStore:
    """
    Production Feature Store for Indian AI/ML Systems
    Supports real-time, batch, and streaming features with Indian context
    """
    
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
        self.feature_configs: Dict[str, FeatureConfig] = {}
        self.feature_computers: Dict[str, FeatureComputer] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Cost tracking
        self.total_cost_inr = 0.0
        self.request_count = 0
        
    async def initialize(self):
        """Initialize feature store components"""
        
        # Setup Redis for real-time features
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Setup PostgreSQL for batch features
        self.db_pool = await asyncpg.create_pool(
            "postgresql://user:password@localhost/featurestore",
            min_size=5,
            max_size=20
        )
        
        # Register feature computers
        await self._register_feature_computers()
        
        # Register feature configurations
        await self._register_feature_configs()
        
        logger.info("Feature Store initialized successfully")
    
    async def _register_feature_configs(self):
        """Register all feature configurations"""
        
        # User behavior score
        self.feature_configs["user_behavior_score"] = FeatureConfig(
            name="user_behavior_score",
            version="1.2.0", 
            feature_type=FeatureType.COMPUTED,
            data_type="float",
            description="User financial behavior score based on transaction patterns",
            owner_team="ml_platform",
            tags=["user", "behavior", "fintech", "indian_context"],
            ttl_seconds=3600,
            compute_cost_inr=0.002,
            supports_hindi=False,
            regional_variations=["north", "south", "east", "west"],
            tier_specific=True
        )
        
        # Regional preferences
        self.feature_configs["regional_preferences"] = FeatureConfig(
            name="regional_preferences",
            version="2.1.0",
            feature_type=FeatureType.COMPUTED,
            data_type="dict",
            description="Regional preferences based on Indian cultural patterns",
            owner_team="personalization",
            tags=["regional", "culture", "preferences", "localization"],
            ttl_seconds=86400,  # 24 hours
            compute_cost_inr=0.001,
            supports_hindi=True,
            regional_variations=["north", "south", "east", "west"],
            tier_specific=True
        )
        
        # Real-time transaction features
        self.feature_configs["transaction_velocity"] = FeatureConfig(
            name="transaction_velocity",
            version="1.0.0",
            feature_type=FeatureType.REAL_TIME,
            data_type="float",
            description="Real-time transaction velocity for fraud detection",
            owner_team="risk",
            tags=["real_time", "fraud", "velocity", "transactions"],
            ttl_seconds=300,  # 5 minutes
            compute_cost_inr=0.0005,
            supports_hindi=False,
            tier_specific=False
        )
    
    async def _register_feature_computers(self):
        """Register feature computers"""
        
        self.feature_computers["user_behavior_score"] = IndianUserBehaviorComputer(self.db_pool)
        self.feature_computers["regional_preferences"] = RegionalPreferenceComputer(self.redis_client)
    
    async def get_features(self, 
                          user_id: str,
                          feature_names: List[str],
                          context: Dict[str, Any] = None) -> Dict[str, FeatureValue]:
        """
        Get multiple features for a user
        Main interface for ML model serving
        """
        
        if context is None:
            context = {}
        
        self.request_count += 1
        start_time = time.time()
        
        features = {}
        tasks = []
        
        for feature_name in feature_names:
            if feature_name in self.feature_configs:
                task = self._get_single_feature(user_id, feature_name, context)
                tasks.append((feature_name, task))
            else:
                logger.warning(f"Unknown feature: {feature_name}")
        
        # Execute all feature retrievals concurrently
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        for (feature_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Error getting feature {feature_name}: {result}")
                # Return default/safe value
                features[feature_name] = FeatureValue(
                    feature_name=feature_name,
                    value=None,
                    timestamp=time.time(),
                    version="error",
                    confidence=0.0,
                    computed_cost_inr=0.0
                )
            else:
                features[feature_name] = result
                self.total_cost_inr += result.computed_cost_inr
        
        elapsed_time = time.time() - start_time
        logger.info(f"Retrieved {len(features)} features for {user_id} in {elapsed_time:.3f}s, "
                   f"cost: ₹{sum(f.computed_cost_inr for f in features.values()):.4f}")
        
        return features
    
    async def _get_single_feature(self, 
                                 user_id: str,
                                 feature_name: str,
                                 context: Dict[str, Any]) -> FeatureValue:
        """Get a single feature value"""
        
        config = self.feature_configs[feature_name]
        
        # Try cache first for real-time/computed features
        if config.feature_type in [FeatureType.REAL_TIME, FeatureType.COMPUTED]:
            cached_value = await self._get_cached_feature(user_id, feature_name)
            if cached_value:
                return cached_value
        
        # Compute feature
        if feature_name in self.feature_computers:
            computer = self.feature_computers[feature_name]
            feature_value = await computer.compute(user_id, context)
            
            # Cache the result
            await self._cache_feature(user_id, feature_name, feature_value, config.ttl_seconds)
            
            return feature_value
        
        # Fallback to batch feature from database
        return await self._get_batch_feature(user_id, feature_name)
    
    async def _get_cached_feature(self, user_id: str, feature_name: str) -> Optional[FeatureValue]:
        """Get cached feature value"""
        try:
            cached = await self.redis_client.get(f"feature:{feature_name}:{user_id}")
            if cached:
                data = json.loads(cached)
                return FeatureValue(**data)
        except Exception as e:
            logger.warning(f"Cache read failed for {feature_name}: {e}")
        
        return None
    
    async def _cache_feature(self, 
                           user_id: str, 
                           feature_name: str, 
                           feature_value: FeatureValue,
                           ttl_seconds: int):
        """Cache feature value"""
        try:
            cache_key = f"feature:{feature_name}:{user_id}"
            await self.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(asdict(feature_value))
            )
        except Exception as e:
            logger.warning(f"Cache write failed for {feature_name}: {e}")
    
    async def _get_batch_feature(self, user_id: str, feature_name: str) -> FeatureValue:
        """Get batch feature from database"""
        
        try:
            async with self.db_pool.acquire() as conn:
                query = """
                SELECT feature_value, timestamp, version, confidence
                FROM batch_features 
                WHERE user_id = $1 AND feature_name = $2
                ORDER BY timestamp DESC LIMIT 1
                """
                
                result = await conn.fetchrow(query, user_id, feature_name)
                
                if result:
                    return FeatureValue(
                        feature_name=feature_name,
                        value=json.loads(result['feature_value']),
                        timestamp=result['timestamp'],
                        version=result['version'],
                        confidence=result['confidence'],
                        computed_cost_inr=0.0001  # Minimal cost for batch retrieval
                    )
        except Exception as e:
            logger.error(f"Batch feature retrieval failed: {e}")
        
        # Return safe default
        return FeatureValue(
            feature_name=feature_name,
            value=None,
            timestamp=time.time(),
            version="unknown",
            confidence=0.0,
            computed_cost_inr=0.0
        )
    
    async def store_batch_features(self, 
                                 user_features: Dict[str, Dict[str, FeatureValue]]):
        """Store batch computed features"""
        
        try:
            async with self.db_pool.acquire() as conn:
                for user_id, features in user_features.items():
                    for feature_name, feature_value in features.items():
                        await conn.execute("""
                            INSERT INTO batch_features 
                            (user_id, feature_name, feature_value, timestamp, version, confidence)
                            VALUES ($1, $2, $3, $4, $5, $6)
                            ON CONFLICT (user_id, feature_name) 
                            DO UPDATE SET 
                                feature_value = EXCLUDED.feature_value,
                                timestamp = EXCLUDED.timestamp,
                                version = EXCLUDED.version,
                                confidence = EXCLUDED.confidence
                        """,
                        user_id,
                        feature_name,
                        json.dumps(feature_value.value),
                        feature_value.timestamp,
                        feature_value.version,
                        feature_value.confidence
                        )
                        
            logger.info(f"Stored batch features for {len(user_features)} users")
            
        except Exception as e:
            logger.error(f"Batch feature storage failed: {e}")
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for optimization"""
        
        avg_cost_per_request = self.total_cost_inr / max(1, self.request_count)
        
        return {
            "total_requests": self.request_count,
            "total_cost_inr": f"₹{self.total_cost_inr:.4f}",
            "avg_cost_per_request": f"₹{avg_cost_per_request:.4f}",
            "active_features": len(self.feature_configs),
            "registered_computers": len(self.feature_computers)
        }

# Example usage and testing
async def test_feature_store():
    """Test feature store with Indian user contexts"""
    
    feature_store = FeatureStore()
    await feature_store.initialize()
    
    print("🏪 Feature Store Test - Indian User Context")
    print("=" * 50)
    
    # Test different Indian user profiles
    test_users = [
        {
            "user_id": "user_mumbai_001",
            "context": {"region": "west", "tier": 1, "language": "hi"},
            "description": "Mumbai Tier-1 Hindi user"
        },
        {
            "user_id": "user_bangalore_002", 
            "context": {"region": "south", "tier": 1, "language": "en"},
            "description": "Bangalore Tier-1 English user"
        },
        {
            "user_id": "user_patna_003",
            "context": {"region": "north", "tier": 3, "language": "hi"},
            "description": "Patna Tier-3 Hindi user"
        }
    ]
    
    # Features to test
    feature_names = ["user_behavior_score", "regional_preferences"]
    
    total_cost = 0
    
    for user_data in test_users:
        print(f"\n👤 User: {user_data['description']}")
        print(f"   ID: {user_data['user_id']}")
        
        features = await feature_store.get_features(
            user_data["user_id"],
            feature_names,
            user_data["context"]
        )
        
        for feature_name, feature_value in features.items():
            print(f"   📊 {feature_name}:")
            print(f"      Value: {feature_value.value}")
            print(f"      Confidence: {feature_value.confidence:.3f}")
            print(f"      Region: {feature_value.region}")
            print(f"      Tier: {feature_value.tier}")
            print(f"      Cost: ₹{feature_value.computed_cost_inr:.4f}")
            print(f"      Version: {feature_value.version}")
            
            total_cost += feature_value.computed_cost_inr
    
    print(f"\n💰 Total Cost: ₹{total_cost:.4f}")
    
    # Cost summary
    cost_summary = feature_store.get_cost_summary()
    print(f"\n📈 Cost Summary:")
    for key, value in cost_summary.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_feature_store())