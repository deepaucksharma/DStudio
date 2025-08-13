#!/usr/bin/env python3
"""
Model Versioning System - MLOps Episode 44
Production-ready model versioning for continuous ML deployment

Author: Claude Code
Context: GitOps-style model versioning for Indian fintech ML models
"""

import os
import json
import hashlib
import shutil
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging
import tarfile
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    """Model lifecycle status"""
    TRAINING = "training"
    VALIDATION = "validation"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

@dataclass
class ModelMetrics:
    """Comprehensive model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    validation_samples: int
    training_time_seconds: float
    model_size_mb: float
    feature_count: int

@dataclass
class ModelMetadata:
    """Complete model metadata"""
    model_id: str
    name: str
    version: str
    algorithm: str
    framework: str
    created_by: str
    created_at: datetime
    status: ModelStatus
    metrics: ModelMetrics
    tags: List[str]
    description: str
    parent_model_id: Optional[str] = None
    experiment_id: Optional[str] = None

class ModelArtifact:
    """
    Model artifact container
    Mumbai me model ka full package!
    """
    
    def __init__(self, model_id: str, base_path: str = "model_registry"):
        self.model_id = model_id
        self.base_path = base_path
        self.model_path = os.path.join(base_path, model_id)
        os.makedirs(self.model_path, exist_ok=True)
    
    def save_model(self, model: BaseEstimator, filename: str = "model.pkl") -> str:
        """Save ML model"""
        model_file = os.path.join(self.model_path, filename)
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        return model_file
    
    def load_model(self, filename: str = "model.pkl") -> BaseEstimator:
        """Load ML model"""
        model_file = os.path.join(self.model_path, filename)
        with open(model_file, 'rb') as f:
            return pickle.load(f)
    
    def save_metadata(self, metadata: ModelMetadata) -> str:
        """Save model metadata"""
        metadata_file = os.path.join(self.model_path, "metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(asdict(metadata), f, indent=2, default=str)
        return metadata_file
    
    def load_metadata(self) -> ModelMetadata:
        """Load model metadata"""
        metadata_file = os.path.join(self.model_path, "metadata.json")
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        # Convert string dates back to datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['status'] = ModelStatus(data['status'])
        
        return ModelMetadata(**data)
    
    def save_requirements(self, requirements: List[str]) -> str:
        """Save model dependencies"""
        req_file = os.path.join(self.model_path, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write('\n'.join(requirements))
        return req_file
    
    def save_training_data_schema(self, schema: Dict[str, str]) -> str:
        """Save training data schema"""
        schema_file = os.path.join(self.model_path, "data_schema.json")
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=2)
        return schema_file
    
    def create_archive(self) -> str:
        """Create compressed archive of model"""
        archive_path = f"{self.model_path}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(self.model_path, arcname=self.model_id)
        return archive_path
    
    def extract_archive(self, archive_path: str, extract_to: str) -> str:
        """Extract model archive"""
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_to)
        return os.path.join(extract_to, self.model_id)

class PaytmModelRegistry:
    """
    Production Model Registry for Paytm-style ML operations
    Mumbai me sabse organized model ka godown!
    """
    
    def __init__(self, registry_path: str = "paytm_model_registry"):
        self.registry_path = registry_path
        self.db_path = os.path.join(registry_path, "registry.db")
        os.makedirs(registry_path, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize model registry database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    model_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    training_samples INTEGER,
                    validation_samples INTEGER,
                    training_time_seconds REAL,
                    model_size_mb REAL,
                    feature_count INTEGER,
                    tags TEXT,
                    description TEXT,
                    parent_model_id TEXT,
                    experiment_id TEXT,
                    UNIQUE(name, version)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_model_id TEXT NOT NULL,
                    child_model_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (parent_model_id) REFERENCES models (model_id),
                    FOREIGN KEY (child_model_id) REFERENCES models (model_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS deployments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    deployed_at TEXT NOT NULL,
                    deployed_by TEXT NOT NULL,
                    endpoint_url TEXT,
                    status TEXT NOT NULL,
                    FOREIGN KEY (model_id) REFERENCES models (model_id)
                )
            ''')
    
    def _generate_model_id(self, name: str, version: str) -> str:
        """Generate unique model ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content = f"{name}_{version}_{timestamp}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{name}_v{version}_{hash_suffix}"
    
    def register_model(self, 
                      model: BaseEstimator,
                      name: str,
                      version: str,
                      algorithm: str,
                      metrics: ModelMetrics,
                      created_by: str,
                      description: str = "",
                      tags: List[str] = None,
                      parent_model_id: str = None,
                      experiment_id: str = None) -> str:
        """
        Register new model in the registry
        Mumbai me nayi model ki entry karna!
        """
        
        if tags is None:
            tags = []
        
        # Generate model ID
        model_id = self._generate_model_id(name, version)
        
        # Create model metadata
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            version=version,
            algorithm=algorithm,
            framework="scikit-learn",
            created_by=created_by,
            created_at=datetime.now(),
            status=ModelStatus.TRAINING,
            metrics=metrics,
            tags=tags,
            description=description,
            parent_model_id=parent_model_id,
            experiment_id=experiment_id
        )
        
        try:
            # Save model artifacts
            artifact = ModelArtifact(model_id, self.registry_path)
            artifact.save_model(model)
            artifact.save_metadata(metadata)
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO models VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    model_id, name, version, algorithm, "scikit-learn", created_by,
                    metadata.created_at.isoformat(), metadata.status.value,
                    metrics.accuracy, metrics.precision, metrics.recall, metrics.f1_score,
                    metrics.training_samples, metrics.validation_samples,
                    metrics.training_time_seconds, metrics.model_size_mb,
                    metrics.feature_count, json.dumps(tags), description,
                    parent_model_id, experiment_id
                ))
                
                # Add lineage if parent exists
                if parent_model_id:
                    conn.execute('''
                        INSERT INTO model_lineage (parent_model_id, child_model_id, relationship_type, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (parent_model_id, model_id, "retrain", datetime.now().isoformat()))
            
            logger.info(f"Model registered successfully: {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            raise
    
    def get_model(self, model_id: str) -> Tuple[BaseEstimator, ModelMetadata]:
        """Load model and metadata"""
        try:
            artifact = ModelArtifact(model_id, self.registry_path)
            model = artifact.load_model()
            metadata = artifact.load_metadata()
            return model, metadata
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise
    
    def get_latest_model(self, name: str, status: ModelStatus = None) -> Tuple[str, BaseEstimator, ModelMetadata]:
        """Get latest version of a model"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT model_id FROM models WHERE name = ?"
            params = [name]
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC LIMIT 1"
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"No model found with name: {name}")
            
            model_id = row[0]
            model, metadata = self.get_model(model_id)
            return model_id, model, metadata
    
    def promote_model(self, model_id: str, target_status: ModelStatus) -> bool:
        """
        Promote model through stages
        Mumbai me model ka promotion!
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get current status
                cursor = conn.execute("SELECT status FROM models WHERE model_id = ?", (model_id,))
                row = cursor.fetchone()
                
                if not row:
                    raise ValueError(f"Model not found: {model_id}")
                
                current_status = ModelStatus(row[0])
                
                # Validate promotion path
                valid_promotions = {
                    ModelStatus.TRAINING: [ModelStatus.VALIDATION],
                    ModelStatus.VALIDATION: [ModelStatus.TESTING],
                    ModelStatus.TESTING: [ModelStatus.STAGING],
                    ModelStatus.STAGING: [ModelStatus.PRODUCTION],
                    ModelStatus.PRODUCTION: [ModelStatus.DEPRECATED],
                    ModelStatus.DEPRECATED: [ModelStatus.ARCHIVED]
                }
                
                if target_status not in valid_promotions.get(current_status, []):
                    raise ValueError(f"Invalid promotion: {current_status.value} -> {target_status.value}")
                
                # Update status
                conn.execute(
                    "UPDATE models SET status = ? WHERE model_id = ?",
                    (target_status.value, model_id)
                )
                
                logger.info(f"Model {model_id} promoted: {current_status.value} -> {target_status.value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to promote model: {e}")
            return False
    
    def compare_models(self, model_id1: str, model_id2: str) -> Dict[str, Any]:
        """
        Compare two models
        Mumbai me do model ka comparison!
        """
        try:
            _, metadata1 = self.get_model(model_id1)
            _, metadata2 = self.get_model(model_id2)
            
            comparison = {
                'model1': {
                    'id': model_id1,
                    'name': metadata1.name,
                    'version': metadata1.version,
                    'accuracy': metadata1.metrics.accuracy,
                    'precision': metadata1.metrics.precision,
                    'recall': metadata1.metrics.recall,
                    'f1_score': metadata1.metrics.f1_score,
                    'created_at': metadata1.created_at.isoformat()
                },
                'model2': {
                    'id': model_id2,
                    'name': metadata2.name,
                    'version': metadata2.version,
                    'accuracy': metadata2.metrics.accuracy,
                    'precision': metadata2.metrics.precision,
                    'recall': metadata2.metrics.recall,
                    'f1_score': metadata2.metrics.f1_score,
                    'created_at': metadata2.created_at.isoformat()
                },
                'improvements': {
                    'accuracy': metadata2.metrics.accuracy - metadata1.metrics.accuracy,
                    'precision': metadata2.metrics.precision - metadata1.metrics.precision,
                    'recall': metadata2.metrics.recall - metadata1.metrics.recall,
                    'f1_score': metadata2.metrics.f1_score - metadata1.metrics.f1_score
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare models: {e}")
            return {}
    
    def list_models(self, name: str = None, status: ModelStatus = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List models with filters"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT model_id, name, version, algorithm, status, accuracy, created_at FROM models"
            params = []
            conditions = []
            
            if name:
                conditions.append("name = ?")
                params.append(name)
            
            if status:
                conditions.append("status = ?")
                params.append(status.value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            
            models = []
            for row in cursor.fetchall():
                model_dict = dict(zip(columns, row))
                models.append(model_dict)
            
            return models
    
    def get_model_lineage(self, model_id: str) -> Dict[str, List[str]]:
        """Get model lineage (parents and children)"""
        with sqlite3.connect(self.db_path) as conn:
            # Get parents
            cursor = conn.execute('''
                SELECT parent_model_id FROM model_lineage WHERE child_model_id = ?
            ''', (model_id,))
            parents = [row[0] for row in cursor.fetchall()]
            
            # Get children
            cursor = conn.execute('''
                SELECT child_model_id FROM model_lineage WHERE parent_model_id = ?
            ''', (model_id,))
            children = [row[0] for row in cursor.fetchall()]
            
            return {'parents': parents, 'children': children}
    
    def archive_old_models(self, name: str, keep_versions: int = 5) -> List[str]:
        """
        Archive old model versions
        Mumbai me purane model ka safai!
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get models to archive (keeping latest N versions)
            cursor = conn.execute('''
                SELECT model_id FROM models 
                WHERE name = ? AND status != ? 
                ORDER BY created_at DESC OFFSET ?
            ''', (name, ModelStatus.PRODUCTION.value, keep_versions))
            
            models_to_archive = [row[0] for row in cursor.fetchall()]
            
            # Archive models
            archived = []
            for model_id in models_to_archive:
                try:
                    # Create archive
                    artifact = ModelArtifact(model_id, self.registry_path)
                    archive_path = artifact.create_archive()
                    
                    # Update status
                    conn.execute(
                        "UPDATE models SET status = ? WHERE model_id = ?",
                        (ModelStatus.ARCHIVED.value, model_id)
                    )
                    
                    # Remove original directory
                    shutil.rmtree(artifact.model_path)
                    
                    archived.append(model_id)
                    logger.info(f"Archived model: {model_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to archive {model_id}: {e}")
            
            return archived

def create_sample_fraud_model(transaction_data: pd.DataFrame) -> Tuple[BaseEstimator, ModelMetrics]:
    """
    Create sample fraud detection model
    Mumbai me fraud detection ka model!
    """
    # Prepare features
    feature_columns = ['amount', 'user_age', 'transaction_hour', 'is_weekend']
    X = transaction_data[feature_columns]
    y = transaction_data['is_fraud']
    
    # Train model
    start_time = datetime.now()
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    training_time = (datetime.now() - start_time).total_seconds()
    
    # Calculate metrics
    y_pred = model.predict(X)
    metrics = ModelMetrics(
        accuracy=accuracy_score(y, y_pred),
        precision=precision_score(y, y_pred),
        recall=recall_score(y, y_pred),
        f1_score=f1_score(y, y_pred),
        training_samples=len(X),
        validation_samples=0,
        training_time_seconds=training_time,
        model_size_mb=0.5,  # Approximate
        feature_count=len(feature_columns)
    )
    
    return model, metrics

def generate_sample_transaction_data(n_samples: int = 10000) -> pd.DataFrame:
    """Generate sample transaction data for demo"""
    np.random.seed(42)
    
    data = {
        'transaction_id': [f"txn_{i:06d}" for i in range(n_samples)],
        'amount': np.random.lognormal(6, 1.5, n_samples),  # Log-normal for realistic amounts
        'user_age': np.random.randint(18, 80, n_samples),
        'transaction_hour': np.random.randint(0, 24, n_samples),
        'is_weekend': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    }
    
    # Create fraud labels (5% fraud rate)
    fraud_probability = (
        0.3 * (data['amount'] > 50000) +  # High amount
        0.2 * (data['transaction_hour'] < 6) +  # Late night
        0.1 * (data['user_age'] < 25)  # Young users
    )
    
    data['is_fraud'] = np.random.binomial(1, np.clip(fraud_probability, 0, 0.2), n_samples)
    
    return pd.DataFrame(data)

def main():
    """
    Demo Paytm Model Versioning System
    Mumbai ke model versioning ka demo!
    """
    print("🏦 Starting Paytm Model Versioning Demo")
    print("=" * 50)
    
    # Initialize model registry
    registry = PaytmModelRegistry("demo_model_registry")
    
    # Generate sample data
    print("\n📊 Generating sample transaction data...")
    transaction_data = generate_sample_transaction_data(10000)
    print(f"Generated {len(transaction_data)} transactions")
    print(f"Fraud rate: {transaction_data['is_fraud'].mean():.1%}")
    
    # Create and register first model version
    print("\n🤖 Training fraud detection model v1.0...")
    model_v1, metrics_v1 = create_sample_fraud_model(transaction_data)
    
    model_id_v1 = registry.register_model(
        model=model_v1,
        name="paytm_fraud_detector",
        version="1.0",
        algorithm="RandomForest",
        metrics=metrics_v1,
        created_by="fraud_team",
        description="Initial fraud detection model for Paytm transactions",
        tags=["fraud", "production", "v1"]
    )
    
    print(f"Model v1.0 registered: {model_id_v1}")
    print(f"Accuracy: {metrics_v1.accuracy:.4f}")
    
    # Create improved model version
    print("\n🚀 Training improved model v2.0...")
    # Simulate model improvement
    transaction_data_v2 = transaction_data.copy()
    transaction_data_v2['amount_log'] = np.log1p(transaction_data_v2['amount'])
    
    model_v2, metrics_v2 = create_sample_fraud_model(transaction_data)
    # Simulate improvement
    metrics_v2.accuracy += 0.02
    metrics_v2.precision += 0.03
    metrics_v2.recall += 0.01
    metrics_v2.f1_score += 0.02
    
    model_id_v2 = registry.register_model(
        model=model_v2,
        name="paytm_fraud_detector",
        version="2.0",
        algorithm="RandomForest",
        metrics=metrics_v2,
        created_by="fraud_team",
        description="Improved fraud detection with feature engineering",
        tags=["fraud", "production", "v2", "improved"],
        parent_model_id=model_id_v1
    )
    
    print(f"Model v2.0 registered: {model_id_v2}")
    print(f"Accuracy: {metrics_v2.accuracy:.4f}")
    
    # Promote models through stages
    print("\n📈 Promoting models through stages...")
    
    # Promote v1 to production
    registry.promote_model(model_id_v1, ModelStatus.VALIDATION)
    registry.promote_model(model_id_v1, ModelStatus.TESTING)
    registry.promote_model(model_id_v1, ModelStatus.STAGING)
    registry.promote_model(model_id_v1, ModelStatus.PRODUCTION)
    print("Model v1.0 promoted to PRODUCTION")
    
    # Promote v2 to staging
    registry.promote_model(model_id_v2, ModelStatus.VALIDATION)
    registry.promote_model(model_id_v2, ModelStatus.TESTING)
    registry.promote_model(model_id_v2, ModelStatus.STAGING)
    print("Model v2.0 promoted to STAGING")
    
    # Compare models
    print("\n⚖️  Comparing models...")
    comparison = registry.compare_models(model_id_v1, model_id_v2)
    print("Model Comparison:")
    print(f"  v1.0 Accuracy: {comparison['model1']['accuracy']:.4f}")
    print(f"  v2.0 Accuracy: {comparison['model2']['accuracy']:.4f}")
    print(f"  Improvement: {comparison['improvements']['accuracy']:.4f}")
    
    # Get latest production model
    print("\n🏷️  Getting latest production model...")
    latest_model_id, latest_model, latest_metadata = registry.get_latest_model(
        "paytm_fraud_detector", 
        ModelStatus.PRODUCTION
    )
    print(f"Latest production model: {latest_model_id}")
    print(f"Version: {latest_metadata.version}")
    print(f"Status: {latest_metadata.status.value}")
    
    # List all models
    print("\n📋 All registered models:")
    all_models = registry.list_models("paytm_fraud_detector")
    for model_info in all_models:
        print(f"  {model_info['model_id']}: v{model_info['version']} - {model_info['status']} (Acc: {model_info['accuracy']:.4f})")
    
    # Check model lineage
    print(f"\n🌳 Model lineage for v2.0:")
    lineage = registry.get_model_lineage(model_id_v2)
    print(f"  Parents: {lineage['parents']}")
    print(f"  Children: {lineage['children']}")
    
    print("\n✅ Model versioning demo completed!")
    print("Mumbai me model versioning bhi version control ki tarah systematic!")

if __name__ == "__main__":
    main()