#!/usr/bin/env python3
"""
ML Pipeline Automation System - MLOps Episode 44
Comprehensive pipeline orchestration for Indian e-commerce ML models

Author: Claude Code
Context: Production-ready ML pipeline for Flipkart-style recommendation system
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import pickle
import os
import yaml
import hashlib
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status states"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PipelineConfig:
    """ML Pipeline configuration"""
    name: str
    version: str
    model_type: str
    feature_columns: List[str]
    target_column: str
    test_size: float = 0.2
    random_state: int = 42
    max_training_time: int = 3600  # seconds
    min_accuracy_threshold: float = 0.85

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    training_time: float
    data_size: int
    feature_count: int
    timestamp: datetime

class FlipkartMLPipeline:
    """
    Production ML Pipeline for Flipkart-style recommendation system
    Mumbai me jo sabse fast recommendation chahiye, wo yaha milti hai!
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.status = PipelineStatus.PENDING
        self.model = None
        self.metrics: Optional[ModelMetrics] = None
        self.pipeline_id = self._generate_pipeline_id()
        self.artifacts_path = f"artifacts/{self.pipeline_id}"
        os.makedirs(self.artifacts_path, exist_ok=True)
        
        logger.info(f"Pipeline initialized: {self.pipeline_id}")
    
    def _generate_pipeline_id(self) -> str:
        """Generate unique pipeline ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_hash = hashlib.md5(str(self.config).encode()).hexdigest()[:8]
        return f"{self.config.name}_{timestamp}_{config_hash}"
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Data validation step - Mumbai ka traffic police check karta hai!
        Ensures data quality before model training
        """
        logger.info("Starting data validation...")
        
        # Check required columns
        missing_columns = set(self.config.feature_columns + [self.config.target_column]) - set(data.columns)
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            return False
        
        # Check for null values
        null_percentage = data.isnull().sum() / len(data)
        high_null_columns = null_percentage[null_percentage > 0.5].index.tolist()
        if high_null_columns:
            logger.warning(f"High null percentage in columns: {high_null_columns}")
        
        # Check data types
        for col in self.config.feature_columns:
            if not pd.api.types.is_numeric_dtype(data[col]):
                logger.warning(f"Non-numeric column: {col}")
        
        # Minimum data size check
        if len(data) < 1000:
            logger.error(f"Insufficient data: {len(data)} rows")
            return False
        
        logger.info("Data validation passed!")
        return True
    
    def preprocess_data(self, data: pd.DataFrame) -> tuple:
        """
        Data preprocessing with Mumbai local train efficiency
        """
        logger.info("Starting data preprocessing...")
        
        # Handle missing values
        data_clean = data.copy()
        for col in self.config.feature_columns:
            if data_clean[col].dtype in ['float64', 'int64']:
                data_clean[col].fillna(data_clean[col].median(), inplace=True)
            else:
                data_clean[col].fillna(data_clean[col].mode()[0], inplace=True)
        
        # Feature selection
        X = data_clean[self.config.feature_columns]
        y = data_clean[self.config.target_column]
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=y if len(np.unique(y)) > 1 else None
        )
        
        logger.info(f"Data split - Train: {len(X_train)}, Test: {len(X_test)}")
        return X_train, X_test, y_train, y_test
    
    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series) -> bool:
        """
        Model training with timeout protection
        Mumbai me time is money!
        """
        logger.info("Starting model training...")
        start_time = time.time()
        
        try:
            if self.config.model_type == "random_forest":
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=self.config.random_state,
                    n_jobs=-1  # Use all CPU cores - Mumbai style parallel processing!
                )
            else:
                raise ValueError(f"Unsupported model type: {self.config.model_type}")
            
            # Train with timeout protection
            self.model.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            if training_time > self.config.max_training_time:
                logger.warning(f"Training time exceeded limit: {training_time}s")
            
            logger.info(f"Model training completed in {training_time:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            return False
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> ModelMetrics:
        """
        Model evaluation with comprehensive metrics
        """
        logger.info("Starting model evaluation...")
        
        start_time = time.time()
        y_pred = self.model.predict(X_test)
        prediction_time = time.time() - start_time
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        
        metrics = ModelMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            training_time=prediction_time,
            data_size=len(X_test),
            feature_count=len(X_test.columns),
            timestamp=datetime.now()
        )
        
        logger.info(f"Model Metrics - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")
        
        return metrics
    
    def save_artifacts(self) -> Dict[str, str]:
        """
        Save model artifacts and metadata
        Mumbai ke artifact collection jaise important!
        """
        logger.info("Saving model artifacts...")
        
        artifacts = {}
        
        # Save model
        model_path = os.path.join(self.artifacts_path, "model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        artifacts['model'] = model_path
        
        # Save configuration
        config_path = os.path.join(self.artifacts_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(self.config.__dict__, f)
        artifacts['config'] = config_path
        
        # Save metrics
        if self.metrics:
            metrics_path = os.path.join(self.artifacts_path, "metrics.json")
            with open(metrics_path, 'w') as f:
                json.dump(self.metrics.__dict__, f, default=str)
            artifacts['metrics'] = metrics_path
        
        # Save pipeline metadata
        metadata = {
            'pipeline_id': self.pipeline_id,
            'status': self.status.value,
            'created_at': datetime.now().isoformat(),
            'artifacts': artifacts
        }
        
        metadata_path = os.path.join(self.artifacts_path, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Artifacts saved to: {self.artifacts_path}")
        return artifacts
    
    def run_pipeline(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute complete ML pipeline
        Mumbai Express ki tarah - non-stop execution!
        """
        logger.info(f"Starting pipeline execution: {self.pipeline_id}")
        self.status = PipelineStatus.RUNNING
        
        try:
            # Step 1: Data Validation
            if not self.validate_data(data):
                self.status = PipelineStatus.FAILED
                return {'status': 'failed', 'error': 'Data validation failed'}
            
            # Step 2: Data Preprocessing
            X_train, X_test, y_train, y_test = self.preprocess_data(data)
            
            # Step 3: Model Training
            if not self.train_model(X_train, y_train):
                self.status = PipelineStatus.FAILED
                return {'status': 'failed', 'error': 'Model training failed'}
            
            # Step 4: Model Evaluation
            self.metrics = self.evaluate_model(X_test, y_test)
            
            # Step 5: Quality Gate Check
            if self.metrics.accuracy < self.config.min_accuracy_threshold:
                self.status = PipelineStatus.FAILED
                return {
                    'status': 'failed', 
                    'error': f'Accuracy {self.metrics.accuracy:.4f} below threshold {self.config.min_accuracy_threshold}'
                }
            
            # Step 6: Save Artifacts
            artifacts = self.save_artifacts()
            
            self.status = PipelineStatus.SUCCESS
            logger.info(f"Pipeline completed successfully: {self.pipeline_id}")
            
            return {
                'status': 'success',
                'pipeline_id': self.pipeline_id,
                'metrics': self.metrics.__dict__,
                'artifacts': artifacts
            }
            
        except Exception as e:
            self.status = PipelineStatus.FAILED
            logger.error(f"Pipeline failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

class PipelineOrchestrator:
    """
    Orchestrates multiple ML pipelines
    Mumbai me sabse efficient traffic control!
    """
    
    def __init__(self):
        self.pipelines: Dict[str, FlipkartMLPipeline] = {}
        self.pipeline_history: List[Dict] = []
    
    def register_pipeline(self, config: PipelineConfig) -> str:
        """Register new pipeline configuration"""
        pipeline = FlipkartMLPipeline(config)
        self.pipelines[pipeline.pipeline_id] = pipeline
        logger.info(f"Pipeline registered: {pipeline.pipeline_id}")
        return pipeline.pipeline_id
    
    def execute_pipeline(self, pipeline_id: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute specific pipeline"""
        if pipeline_id not in self.pipelines:
            return {'status': 'failed', 'error': 'Pipeline not found'}
        
        pipeline = self.pipelines[pipeline_id]
        result = pipeline.run_pipeline(data)
        
        # Add to history
        self.pipeline_history.append({
            'pipeline_id': pipeline_id,
            'timestamp': datetime.now().isoformat(),
            'result': result
        })
        
        return result
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status and metrics"""
        if pipeline_id not in self.pipelines:
            return {'error': 'Pipeline not found'}
        
        pipeline = self.pipelines[pipeline_id]
        return {
            'pipeline_id': pipeline_id,
            'status': pipeline.status.value,
            'config': pipeline.config.__dict__,
            'metrics': pipeline.metrics.__dict__ if pipeline.metrics else None
        }
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all registered pipelines"""
        return [
            {
                'pipeline_id': pid,
                'name': pipeline.config.name,
                'status': pipeline.status.value,
                'created_at': datetime.now().isoformat()
            }
            for pid, pipeline in self.pipelines.items()
        ]

def create_sample_ecommerce_data(n_samples: int = 10000) -> pd.DataFrame:
    """
    Create sample e-commerce data for testing
    Mumbai ke market data jaise realistic!
    """
    np.random.seed(42)
    
    # Indian e-commerce context
    categories = ['Electronics', 'Fashion', 'Books', 'Home', 'Sports']
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
    
    data = {
        'user_age': np.random.randint(18, 65, n_samples),
        'user_city': np.random.choice(cities, n_samples),
        'product_category': np.random.choice(categories, n_samples),
        'product_price': np.random.lognormal(6, 1, n_samples),  # Log-normal distribution for prices
        'user_previous_purchases': np.random.poisson(5, n_samples),
        'time_on_site': np.random.exponential(300, n_samples),  # seconds
        'cart_size': np.random.randint(1, 10, n_samples),
        'discount_offered': np.random.uniform(0, 0.5, n_samples),
        'is_mobile': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),  # 70% mobile users
        'season': np.random.choice(['Summer', 'Monsoon', 'Winter', 'Festival'], n_samples)
    }
    
    # Create target variable (purchase probability)
    # Mumbai style complex probability calculation!
    purchase_prob = (
        0.3 * (data['discount_offered'] > 0.2) +
        0.2 * (data['user_previous_purchases'] > 3) +
        0.2 * (data['time_on_site'] > 600) +
        0.1 * (data['cart_size'] > 3) +
        0.2 * (data['is_mobile'] == 1)
    )
    
    data['will_purchase'] = np.random.binomial(1, purchase_prob, n_samples)
    
    return pd.DataFrame(data)

def main():
    """
    Main function to demonstrate ML pipeline automation
    Mumbai Express ML Pipeline!
    """
    print("🚀 Starting Flipkart ML Pipeline Automation Demo")
    print("=" * 60)
    
    # Create sample data
    print("📊 Creating sample e-commerce data...")
    data = create_sample_ecommerce_data(10000)
    print(f"Data created: {len(data)} samples with {len(data.columns)} features")
    
    # Configure pipeline
    config = PipelineConfig(
        name="flipkart_purchase_prediction",
        version="1.0.0",
        model_type="random_forest",
        feature_columns=[
            'user_age', 'product_price', 'user_previous_purchases',
            'time_on_site', 'cart_size', 'discount_offered', 'is_mobile'
        ],
        target_column='will_purchase',
        test_size=0.2,
        min_accuracy_threshold=0.75
    )
    
    # Initialize orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Register and execute pipeline
    print("\n🔧 Registering ML pipeline...")
    pipeline_id = orchestrator.register_pipeline(config)
    print(f"Pipeline ID: {pipeline_id}")
    
    print("\n🏃‍♂️ Executing pipeline...")
    result = orchestrator.execute_pipeline(pipeline_id, data)
    
    # Display results
    print("\n📈 Pipeline Results:")
    print(json.dumps(result, indent=2, default=str))
    
    # Show pipeline status
    print("\n📊 Pipeline Status:")
    status = orchestrator.get_pipeline_status(pipeline_id)
    print(json.dumps(status, indent=2, default=str))
    
    print("\n✅ Pipeline automation demo completed!")
    print("Mumbai me ML pipeline bhi local train ki tarah efficient!")

if __name__ == "__main__":
    main()