#!/usr/bin/env python3
"""
Feature Store Implementation - MLOps Episode 44
Production-ready feature store for Indian fintech applications

Author: Claude Code
Context: Paytm-style feature store for real-time ML predictions
"""

import json
import time
import sqlite3
import redis
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FeatureMetadata:
    """Feature metadata information"""
    name: str
    data_type: str
    description: str
    owner: str
    created_at: datetime
    updated_at: datetime
    version: str
    tags: List[str]
    is_active: bool = True

@dataclass
class FeatureValue:
    """Feature value with timestamp"""
    entity_id: str
    feature_name: str
    value: Any
    timestamp: datetime
    version: str

class FeatureStorageBackend(ABC):
    """Abstract base class for feature storage backends"""
    
    @abstractmethod
    def write_feature(self, feature_value: FeatureValue) -> bool:
        pass
    
    @abstractmethod
    def read_feature(self, entity_id: str, feature_name: str) -> Optional[FeatureValue]:
        pass
    
    @abstractmethod
    def read_features_batch(self, entity_ids: List[str], feature_names: List[str]) -> Dict[str, Dict[str, Any]]:
        pass

class RedisFeatureBackend(FeatureStorageBackend):
    """
    Redis backend for real-time feature serving
    Mumbai me sabse fast feature delivery!
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = 86400  # 24 hours TTL
    
    def _generate_key(self, entity_id: str, feature_name: str) -> str:
        """Generate Redis key for feature"""
        return f"feature:{feature_name}:{entity_id}"
    
    def write_feature(self, feature_value: FeatureValue) -> bool:
        """Write feature to Redis with TTL"""
        try:
            key = self._generate_key(feature_value.entity_id, feature_value.feature_name)
            value_dict = {
                'value': pickle.dumps(feature_value.value),
                'timestamp': feature_value.timestamp.isoformat(),
                'version': feature_value.version
            }
            
            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.hset(key, mapping=value_dict)
            pipe.expire(key, self.ttl)
            pipe.execute()
            
            return True
        except Exception as e:
            logger.error(f"Error writing feature to Redis: {e}")
            return False
    
    def read_feature(self, entity_id: str, feature_name: str) -> Optional[FeatureValue]:
        """Read single feature from Redis"""
        try:
            key = self._generate_key(entity_id, feature_name)
            data = self.redis_client.hgetall(key)
            
            if not data:
                return None
            
            return FeatureValue(
                entity_id=entity_id,
                feature_name=feature_name,
                value=pickle.loads(data['value'].encode('latin1')),
                timestamp=datetime.fromisoformat(data['timestamp']),
                version=data['version']
            )
        except Exception as e:
            logger.error(f"Error reading feature from Redis: {e}")
            return None
    
    def read_features_batch(self, entity_ids: List[str], feature_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """Read multiple features in batch"""
        results = {}
        
        # Use pipeline for batch operations
        pipe = self.redis_client.pipeline()
        keys = []
        
        for entity_id in entity_ids:
            for feature_name in feature_names:
                key = self._generate_key(entity_id, feature_name)
                keys.append((entity_id, feature_name, key))
                pipe.hgetall(key)
        
        try:
            redis_results = pipe.execute()
            
            for i, (entity_id, feature_name, key) in enumerate(keys):
                if entity_id not in results:
                    results[entity_id] = {}
                
                data = redis_results[i]
                if data:
                    results[entity_id][feature_name] = pickle.loads(data['value'].encode('latin1'))
                else:
                    results[entity_id][feature_name] = None
            
            return results
        except Exception as e:
            logger.error(f"Error in batch read: {e}")
            return {}

class SQLiteFeatureBackend(FeatureStorageBackend):
    """
    SQLite backend for offline feature storage
    Mumbai ke offline train schedule ki tarah reliable!
    """
    
    def __init__(self, db_path: str = "feature_store.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS features (
                    entity_id TEXT,
                    feature_name TEXT,
                    value BLOB,
                    timestamp TEXT,
                    version TEXT,
                    PRIMARY KEY (entity_id, feature_name, timestamp)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_entity_feature 
                ON features (entity_id, feature_name)
            ''')
    
    def write_feature(self, feature_value: FeatureValue) -> bool:
        """Write feature to SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO features 
                    (entity_id, feature_name, value, timestamp, version)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    feature_value.entity_id,
                    feature_value.feature_name,
                    pickle.dumps(feature_value.value),
                    feature_value.timestamp.isoformat(),
                    feature_value.version
                ))
            return True
        except Exception as e:
            logger.error(f"Error writing to SQLite: {e}")
            return False
    
    def read_feature(self, entity_id: str, feature_name: str) -> Optional[FeatureValue]:
        """Read latest feature from SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT value, timestamp, version FROM features
                    WHERE entity_id = ? AND feature_name = ?
                    ORDER BY timestamp DESC LIMIT 1
                ''', (entity_id, feature_name))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return FeatureValue(
                    entity_id=entity_id,
                    feature_name=feature_name,
                    value=pickle.loads(row[0]),
                    timestamp=datetime.fromisoformat(row[1]),
                    version=row[2]
                )
        except Exception as e:
            logger.error(f"Error reading from SQLite: {e}")
            return None
    
    def read_features_batch(self, entity_ids: List[str], feature_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """Read multiple features from SQLite"""
        results = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create placeholders for IN clause
                entity_placeholders = ','.join(['?' for _ in entity_ids])
                feature_placeholders = ','.join(['?' for _ in feature_names])
                
                cursor = conn.execute(f'''
                    SELECT entity_id, feature_name, value, timestamp, version
                    FROM features f1
                    WHERE entity_id IN ({entity_placeholders})
                    AND feature_name IN ({feature_placeholders})
                    AND timestamp = (
                        SELECT MAX(timestamp) FROM features f2
                        WHERE f2.entity_id = f1.entity_id 
                        AND f2.feature_name = f1.feature_name
                    )
                ''', entity_ids + feature_names)
                
                for row in cursor.fetchall():
                    entity_id, feature_name, value, timestamp, version = row
                    
                    if entity_id not in results:
                        results[entity_id] = {}
                    
                    results[entity_id][feature_name] = pickle.loads(value)
            
            return results
        except Exception as e:
            logger.error(f"Error in SQLite batch read: {e}")
            return {}

class PaytmFeatureStore:
    """
    Production Feature Store for Paytm-style fintech applications
    Mumbai ke paytm wale ki tarah fast aur reliable!
    """
    
    def __init__(self, online_backend: FeatureStorageBackend, offline_backend: FeatureStorageBackend):
        self.online_backend = online_backend  # Redis for real-time
        self.offline_backend = offline_backend  # SQLite for historical
        self.feature_registry: Dict[str, FeatureMetadata] = {}
        self.feature_groups: Dict[str, List[str]] = {}
    
    def register_feature(self, metadata: FeatureMetadata) -> bool:
        """
        Register feature in the store
        Mumbai me nayi shop register karne ki tarah!
        """
        try:
            # Validate feature metadata
            if not metadata.name or not metadata.data_type:
                raise ValueError("Feature name and data_type are required")
            
            # Store in registry
            self.feature_registry[metadata.name] = metadata
            
            logger.info(f"Feature registered: {metadata.name}")
            return True
        except Exception as e:
            logger.error(f"Error registering feature: {e}")
            return False
    
    def create_feature_group(self, group_name: str, feature_names: List[str]) -> bool:
        """Create logical grouping of features"""
        try:
            # Validate all features exist
            missing_features = [name for name in feature_names if name not in self.feature_registry]
            if missing_features:
                raise ValueError(f"Missing features: {missing_features}")
            
            self.feature_groups[group_name] = feature_names
            logger.info(f"Feature group created: {group_name} with {len(feature_names)} features")
            return True
        except Exception as e:
            logger.error(f"Error creating feature group: {e}")
            return False
    
    def write_features(self, entity_id: str, features: Dict[str, Any], version: str = "1.0.0") -> bool:
        """
        Write features to both online and offline stores
        Mumbai ke double backup system!
        """
        timestamp = datetime.now()
        success_count = 0
        
        for feature_name, value in features.items():
            if feature_name not in self.feature_registry:
                logger.warning(f"Feature not registered: {feature_name}")
                continue
            
            feature_value = FeatureValue(
                entity_id=entity_id,
                feature_name=feature_name,
                value=value,
                timestamp=timestamp,
                version=version
            )
            
            # Write to both backends
            online_success = self.online_backend.write_feature(feature_value)
            offline_success = self.offline_backend.write_feature(feature_value)
            
            if online_success and offline_success:
                success_count += 1
            else:
                logger.error(f"Failed to write feature: {feature_name}")
        
        logger.info(f"Successfully wrote {success_count}/{len(features)} features for entity {entity_id}")
        return success_count == len(features)
    
    def get_online_features(self, entity_id: str, feature_names: List[str]) -> Dict[str, Any]:
        """
        Get features for real-time inference
        Mumbai local ki speed me features!
        """
        start_time = time.time()
        
        # Validate features exist
        valid_features = [name for name in feature_names if name in self.feature_registry]
        
        if len(valid_features) != len(feature_names):
            invalid = set(feature_names) - set(valid_features)
            logger.warning(f"Invalid features requested: {invalid}")
        
        # Get features from online store
        features = {}
        for feature_name in valid_features:
            feature_value = self.online_backend.read_feature(entity_id, feature_name)
            if feature_value:
                features[feature_name] = feature_value.value
            else:
                features[feature_name] = None
                logger.warning(f"Missing feature: {feature_name} for entity {entity_id}")
        
        latency = (time.time() - start_time) * 1000  # milliseconds
        logger.info(f"Retrieved {len(features)} features in {latency:.2f}ms")
        
        return features
    
    def get_batch_features(self, entity_ids: List[str], feature_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get features for batch inference
        Mumbai me bulk delivery ki tarah efficient!
        """
        start_time = time.time()
        
        # Validate features
        valid_features = [name for name in feature_names if name in self.feature_registry]
        
        # Get from online store first (faster)
        online_results = self.online_backend.read_features_batch(entity_ids, valid_features)
        
        # Fill gaps from offline store
        for entity_id in entity_ids:
            if entity_id not in online_results:
                online_results[entity_id] = {}
            
            for feature_name in valid_features:
                if feature_name not in online_results[entity_id] or online_results[entity_id][feature_name] is None:
                    offline_feature = self.offline_backend.read_feature(entity_id, feature_name)
                    if offline_feature:
                        online_results[entity_id][feature_name] = offline_feature.value
        
        latency = (time.time() - start_time) * 1000
        logger.info(f"Retrieved batch features for {len(entity_ids)} entities in {latency:.2f}ms")
        
        return online_results
    
    def get_feature_group(self, entity_id: str, group_name: str) -> Dict[str, Any]:
        """Get all features in a feature group"""
        if group_name not in self.feature_groups:
            logger.error(f"Feature group not found: {group_name}")
            return {}
        
        feature_names = self.feature_groups[group_name]
        return self.get_online_features(entity_id, feature_names)
    
    def get_feature_statistics(self, feature_name: str, days: int = 7) -> Dict[str, Any]:
        """
        Get feature statistics for monitoring
        Mumbai ke feature health check!
        """
        if feature_name not in self.feature_registry:
            return {'error': 'Feature not found'}
        
        # This would typically query the offline store for statistics
        # For demo purposes, return mock statistics
        return {
            'feature_name': feature_name,
            'total_entities': 1000,
            'null_count': 10,
            'null_percentage': 1.0,
            'unique_values': 950,
            'min_value': 0,
            'max_value': 100,
            'mean_value': 50.5,
            'last_updated': datetime.now().isoformat()
        }
    
    def list_features(self) -> List[Dict[str, Any]]:
        """List all registered features"""
        return [
            {
                'name': name,
                'data_type': metadata.data_type,
                'description': metadata.description,
                'owner': metadata.owner,
                'is_active': metadata.is_active,
                'tags': metadata.tags
            }
            for name, metadata in self.feature_registry.items()
        ]

def create_paytm_features():
    """
    Create sample Paytm-style features for demo
    Mumbai ke real paytm features!
    """
    
    # Initialize feature store
    redis_backend = RedisFeatureBackend()
    sqlite_backend = SQLiteFeatureBackend()
    feature_store = PaytmFeatureStore(redis_backend, sqlite_backend)
    
    # Register user features
    user_features = [
        FeatureMetadata(
            name="user_transaction_count_7d",
            data_type="int",
            description="Number of transactions in last 7 days",
            owner="fraud_team",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="1.0.0",
            tags=["user", "transaction", "fraud"]
        ),
        FeatureMetadata(
            name="user_avg_transaction_amount",
            data_type="float",
            description="Average transaction amount for user",
            owner="risk_team",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="1.0.0",
            tags=["user", "amount", "risk"]
        ),
        FeatureMetadata(
            name="user_kyc_status",
            data_type="string",
            description="KYC verification status",
            owner="compliance_team",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="1.0.0",
            tags=["user", "kyc", "compliance"]
        ),
        FeatureMetadata(
            name="user_fraud_score",
            data_type="float",
            description="Real-time fraud risk score",
            owner="fraud_team",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="1.0.0",
            tags=["user", "fraud", "score"]
        )
    ]
    
    # Register features
    for feature_metadata in user_features:
        feature_store.register_feature(feature_metadata)
    
    # Create feature groups
    feature_store.create_feature_group("fraud_detection", [
        "user_transaction_count_7d",
        "user_avg_transaction_amount", 
        "user_fraud_score"
    ])
    
    feature_store.create_feature_group("user_profile", [
        "user_kyc_status",
        "user_avg_transaction_amount"
    ])
    
    return feature_store

def main():
    """
    Demo Paytm Feature Store implementation
    Mumbai ke feature store ka demo!
    """
    print("🏪 Starting Paytm Feature Store Demo")
    print("=" * 50)
    
    # Create feature store
    feature_store = create_paytm_features()
    
    # Sample user data
    sample_users = ["user_001", "user_002", "user_003"]
    
    # Write sample features
    print("\n📝 Writing sample features...")
    for i, user_id in enumerate(sample_users):
        features = {
            "user_transaction_count_7d": np.random.randint(1, 50),
            "user_avg_transaction_amount": round(np.random.uniform(100, 5000), 2),
            "user_kyc_status": np.random.choice(["verified", "pending", "rejected"]),
            "user_fraud_score": round(np.random.uniform(0.0, 1.0), 4)
        }
        
        success = feature_store.write_features(user_id, features)
        print(f"User {user_id}: {'✅' if success else '❌'} - {features}")
    
    # Test online feature retrieval
    print("\n🚀 Testing real-time feature retrieval...")
    test_user = "user_001"
    online_features = feature_store.get_online_features(
        test_user, 
        ["user_transaction_count_7d", "user_fraud_score"]
    )
    print(f"Online features for {test_user}: {online_features}")
    
    # Test feature group retrieval
    print(f"\n👥 Testing feature group retrieval...")
    fraud_features = feature_store.get_feature_group(test_user, "fraud_detection")
    print(f"Fraud detection features: {fraud_features}")
    
    # Test batch feature retrieval
    print(f"\n📦 Testing batch feature retrieval...")
    batch_features = feature_store.get_batch_features(
        sample_users,
        ["user_kyc_status", "user_avg_transaction_amount"]
    )
    print("Batch features:")
    for user_id, features in batch_features.items():
        print(f"  {user_id}: {features}")
    
    # Feature statistics
    print(f"\n📊 Feature statistics...")
    stats = feature_store.get_feature_statistics("user_fraud_score")
    print(f"Fraud score statistics: {json.dumps(stats, indent=2)}")
    
    # List all features
    print(f"\n📋 All registered features:")
    all_features = feature_store.list_features()
    for feature in all_features:
        print(f"  - {feature['name']}: {feature['description']}")
    
    print("\n✅ Feature store demo completed!")
    print("Mumbai me feature store bhi express delivery ki tarah fast!")

if __name__ == "__main__":
    main()