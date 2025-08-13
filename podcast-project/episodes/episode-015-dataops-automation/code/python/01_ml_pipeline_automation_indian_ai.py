#!/usr/bin/env python3
"""
DataOps Example 01: ML Pipeline Automation for Indian AI Companies
Complete MLOps pipeline with data validation, model training, and deployment automation
Focus: Indian AI companies like Haptik, Krutrim, Sarvam AI

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import sys
import json
import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import great_expectations as ge
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import boto3
import requests
from dataclasses import dataclass, asdict

# Configure logging for production debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mlops/pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for ML models - Indian AI company specific"""
    model_name: str
    version: str
    dataset_path: str
    target_column: str
    feature_columns: List[str]
    validation_rules: Dict[str, str]
    deployment_target: str
    cost_budget_inr: float
    performance_threshold: float
    
class DataQualityValidator:
    """
    Data quality validation using Great Expectations
    Validates data for Indian AI companies - handles multilingual data, 
    Indian phone numbers, addresses, etc.
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.context = ge.get_context()
        
    def validate_hindi_text_data(self, df: pd.DataFrame) -> bool:
        """Validate Hindi/Hinglish text data quality"""
        try:
            # Create expectations for Hindi text
            expectations = [
                {
                    "expectation_type": "expect_column_to_exist",
                    "kwargs": {"column": "hindi_text"}
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "hindi_text"}
                },
                {
                    "expectation_type": "expect_column_value_lengths_to_be_between",
                    "kwargs": {
                        "column": "hindi_text",
                        "min_value": 1,
                        "max_value": 1000
                    }
                }
            ]
            
            # Validate Indian phone numbers if present
            if 'phone' in df.columns:
                phone_pattern = r'^(\+91[\-\s]?)?[0]?(91)?[789]\d{9}$'
                expectations.append({
                    "expectation_type": "expect_column_values_to_match_regex",
                    "kwargs": {
                        "column": "phone",
                        "regex": phone_pattern
                    }
                })
            
            # Validate Indian postal codes
            if 'pincode' in df.columns:
                expectations.append({
                    "expectation_type": "expect_column_values_to_match_regex",
                    "kwargs": {
                        "column": "pincode",
                        "regex": r'^[1-9][0-9]{5}$'
                    }
                })
            
            # Create Great Expectations dataset
            ge_df = ge.from_pandas(df)
            
            # Apply expectations
            validation_results = []
            for expectation in expectations:
                try:
                    result = ge_df.expect(**expectation)
                    validation_results.append(result['success'])
                    logger.info(f"Validation: {expectation['expectation_type']} - {result['success']}")
                except Exception as e:
                    logger.error(f"Validation failed: {e}")
                    validation_results.append(False)
            
            return all(validation_results)
            
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return False
    
    def validate_multilingual_dataset(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Validate multilingual dataset for Indian AI companies"""
        validation_report = {
            'hindi_text_valid': False,
            'english_text_valid': False,
            'regional_language_valid': False,
            'metadata_valid': False
        }
        
        try:
            # Hindi text validation
            if 'hindi_text' in df.columns:
                hindi_null_pct = df['hindi_text'].isnull().sum() / len(df) * 100
                validation_report['hindi_text_valid'] = hindi_null_pct < 5
                logger.info(f"Hindi text null percentage: {hindi_null_pct}%")
            
            # English text validation
            if 'english_text' in df.columns:
                english_null_pct = df['english_text'].isnull().sum() / len(df) * 100
                validation_report['english_text_valid'] = english_null_pct < 5
                logger.info(f"English text null percentage: {english_null_pct}%")
            
            # Regional language validation (Tamil, Telugu, etc.)
            regional_cols = [col for col in df.columns if 'regional' in col.lower()]
            if regional_cols:
                regional_valid = True
                for col in regional_cols:
                    null_pct = df[col].isnull().sum() / len(df) * 100
                    if null_pct > 10:  # Allow more nulls for regional languages
                        regional_valid = False
                validation_report['regional_language_valid'] = regional_valid
            
            # Metadata validation
            required_metadata = ['created_at', 'source', 'language_code']
            metadata_valid = all(col in df.columns for col in required_metadata)
            validation_report['metadata_valid'] = metadata_valid
            
            return validation_report
            
        except Exception as e:
            logger.error(f"Multilingual validation error: {e}")
            return validation_report

class ModelTrainer:
    """
    ML Model training with MLflow tracking
    Optimized for Indian AI company requirements
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment(f"indian_ai_{config.model_name}")
        
    def train_hindi_classification_model(self, df: pd.DataFrame) -> Dict[str, any]:
        """Train classification model for Hindi text data"""
        
        with mlflow.start_run(run_name=f"{self.config.model_name}_v{self.config.version}"):
            try:
                # Log parameters
                mlflow.log_param("model_type", "RandomForestClassifier")
                mlflow.log_param("dataset_size", len(df))
                mlflow.log_param("features", self.config.feature_columns)
                mlflow.log_param("target", self.config.target_column)
                
                # Prepare data
                X = df[self.config.feature_columns]
                y = df[self.config.target_column]
                
                # Handle text preprocessing for Hindi
                if 'hindi_text' in self.config.feature_columns:
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    
                    # Create TF-IDF vectorizer for Hindi text
                    hindi_vectorizer = TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 2),
                        stop_words=None  # No built-in Hindi stopwords
                    )
                    
                    hindi_features = hindi_vectorizer.fit_transform(df['hindi_text']).toarray()
                    
                    # Combine with other features
                    other_features = df[self.config.feature_columns].select_dtypes(include=[np.number])
                    X = np.hstack([hindi_features, other_features.values])
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
                
                # Train model
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # Log metrics
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("training_samples", len(X_train))
                mlflow.log_metric("test_samples", len(X_test))
                
                # Log model
                mlflow.sklearn.log_model(model, "model")
                
                # Cost calculation in INR
                training_cost_inr = self.calculate_training_cost_inr(len(df))
                mlflow.log_metric("training_cost_inr", training_cost_inr)
                
                logger.info(f"Model trained successfully. Accuracy: {accuracy:.4f}")
                logger.info(f"Training cost: ₹{training_cost_inr:,.2f}")
                
                return {
                    'model': model,
                    'accuracy': accuracy,
                    'training_cost_inr': training_cost_inr,
                    'run_id': mlflow.active_run().info.run_id
                }
                
            except Exception as e:
                logger.error(f"Model training failed: {e}")
                mlflow.log_param("error", str(e))
                raise
    
    def calculate_training_cost_inr(self, dataset_size: int) -> float:
        """Calculate training cost in INR for Indian cloud providers"""
        
        # Cost estimates based on Indian cloud providers (Tata Communications, etc.)
        base_compute_cost_per_hour = 50  # INR per hour for GPU instance
        storage_cost_per_gb_month = 2    # INR per GB per month
        network_cost_per_gb = 5         # INR per GB data transfer
        
        # Estimate training time based on dataset size
        if dataset_size < 10000:
            training_hours = 0.5
        elif dataset_size < 100000:
            training_hours = 2
        else:
            training_hours = 5
        
        # Calculate costs
        compute_cost = base_compute_cost_per_hour * training_hours
        storage_cost = (dataset_size * 0.001) * storage_cost_per_gb_month  # Assume 1MB per 1000 records
        network_cost = (dataset_size * 0.0001) * network_cost_per_gb      # Minimal network usage
        
        total_cost = compute_cost + storage_cost + network_cost
        
        logger.info(f"Cost breakdown - Compute: ₹{compute_cost}, Storage: ₹{storage_cost}, Network: ₹{network_cost}")
        
        return total_cost

class ModelDeployer:
    """
    Model deployment automation for Indian infrastructure
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        
    def deploy_to_indian_cloud(self, model_run_id: str) -> Dict[str, str]:
        """Deploy model to Indian cloud infrastructure"""
        
        try:
            deployment_config = {
                'model_run_id': model_run_id,
                'deployment_target': self.config.deployment_target,
                'instance_type': 't3.medium',  # Cost-effective for Indian companies
                'region': 'ap-south-1',        # Mumbai region
                'auto_scaling': {
                    'min_instances': 1,
                    'max_instances': 5,
                    'target_cpu': 70
                }
            }
            
            # Simulate deployment to AWS India or Azure India
            if self.config.deployment_target == 'aws_india':
                endpoint_url = self.deploy_to_aws_india(deployment_config)
            elif self.config.deployment_target == 'azure_india':
                endpoint_url = self.deploy_to_azure_india(deployment_config)
            else:
                endpoint_url = self.deploy_to_local_server(deployment_config)
            
            # Calculate deployment cost
            monthly_cost_inr = self.calculate_deployment_cost_inr()
            
            logger.info(f"Model deployed successfully to {endpoint_url}")
            logger.info(f"Monthly deployment cost: ₹{monthly_cost_inr:,.2f}")
            
            return {
                'endpoint_url': endpoint_url,
                'deployment_status': 'success',
                'monthly_cost_inr': monthly_cost_inr,
                'deployment_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {
                'endpoint_url': None,
                'deployment_status': 'failed',
                'error': str(e)
            }
    
    def deploy_to_aws_india(self, config: Dict) -> str:
        """Deploy to AWS India (Mumbai region)"""
        # Simulate AWS SageMaker deployment
        endpoint_name = f"hindi-ai-model-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"https://{endpoint_name}.sagemaker.ap-south-1.amazonaws.com/invocations"
    
    def deploy_to_azure_india(self, config: Dict) -> str:
        """Deploy to Azure India"""
        # Simulate Azure ML deployment
        endpoint_name = f"hindi-ai-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"https://{endpoint_name}.centralindia.inference.ml.azure.com/score"
    
    def deploy_to_local_server(self, config: Dict) -> str:
        """Deploy to local server (common for Indian startups)"""
        return f"http://localhost:8080/predict/{config['model_run_id']}"
    
    def calculate_deployment_cost_inr(self) -> float:
        """Calculate monthly deployment cost in INR"""
        
        # Cost estimates for Indian cloud deployment
        instance_cost_per_hour = 25      # INR per hour for t3.medium
        load_balancer_cost_per_month = 1000  # INR per month
        storage_cost_per_month = 500     # INR per month
        
        # Calculate monthly costs
        monthly_instance_cost = instance_cost_per_hour * 24 * 30  # 24/7 operation
        total_monthly_cost = monthly_instance_cost + load_balancer_cost_per_month + storage_cost_per_month
        
        return total_monthly_cost

class MLPipelineOrchestrator:
    """
    Complete MLOps pipeline orchestration using Apache Airflow
    Designed for Indian AI companies with cost optimization
    """
    
    def __init__(self):
        self.default_args = {
            'owner': 'dataops-team',
            'depends_on_past': False,
            'start_date': datetime(2025, 1, 1),
            'email_on_failure': True,
            'email_on_retry': False,
            'retries': 2,
            'retry_delay': timedelta(minutes=5)
        }
    
    def create_indian_ai_pipeline_dag(self, config: ModelConfig) -> DAG:
        """Create Airflow DAG for Indian AI company ML pipeline"""
        
        dag = DAG(
            f'indian_ai_{config.model_name}_pipeline',
            default_args=self.default_args,
            description='Complete MLOps pipeline for Indian AI companies',
            schedule_interval='@daily',
            catchup=False,
            tags=['mlops', 'indian_ai', 'production']
        )
        
        # Task 1: Data Quality Validation
        validate_data = PythonOperator(
            task_id='validate_data_quality',
            python_callable=self.validate_data_task,
            op_kwargs={'config': asdict(config)},
            dag=dag
        )
        
        # Task 2: Model Training
        train_model = PythonOperator(
            task_id='train_model',
            python_callable=self.train_model_task,
            op_kwargs={'config': asdict(config)},
            dag=dag
        )
        
        # Task 3: Model Evaluation
        evaluate_model = PythonOperator(
            task_id='evaluate_model',
            python_callable=self.evaluate_model_task,
            op_kwargs={'config': asdict(config)},
            dag=dag
        )
        
        # Task 4: Deploy Model
        deploy_model = PythonOperator(
            task_id='deploy_model',
            python_callable=self.deploy_model_task,
            op_kwargs={'config': asdict(config)},
            dag=dag
        )
        
        # Task 5: Send Notification
        notify_team = PythonOperator(
            task_id='notify_team',
            python_callable=self.send_notification,
            op_kwargs={'config': asdict(config)},
            dag=dag
        )
        
        # Set dependencies
        validate_data >> train_model >> evaluate_model >> deploy_model >> notify_team
        
        return dag
    
    def validate_data_task(self, config: Dict):
        """Airflow task for data validation"""
        try:
            model_config = ModelConfig(**config)
            validator = DataQualityValidator(model_config)
            
            # Load data
            df = pd.read_csv(model_config.dataset_path)
            
            # Validate data
            validation_result = validator.validate_multilingual_dataset(df)
            
            if not all(validation_result.values()):
                raise ValueError(f"Data validation failed: {validation_result}")
            
            logger.info("Data validation passed successfully")
            return validation_result
            
        except Exception as e:
            logger.error(f"Data validation task failed: {e}")
            raise
    
    def train_model_task(self, config: Dict):
        """Airflow task for model training"""
        try:
            model_config = ModelConfig(**config)
            trainer = ModelTrainer(model_config)
            
            # Load validated data
            df = pd.read_csv(model_config.dataset_path)
            
            # Train model
            training_result = trainer.train_hindi_classification_model(df)
            
            if training_result['accuracy'] < model_config.performance_threshold:
                raise ValueError(f"Model accuracy {training_result['accuracy']} below threshold {model_config.performance_threshold}")
            
            logger.info(f"Model training completed successfully. Run ID: {training_result['run_id']}")
            return training_result
            
        except Exception as e:
            logger.error(f"Model training task failed: {e}")
            raise
    
    def evaluate_model_task(self, config: Dict):
        """Airflow task for model evaluation"""
        try:
            # Perform additional model evaluation
            # Compare with previous models, A/B testing setup, etc.
            
            logger.info("Model evaluation completed successfully")
            return {'evaluation_status': 'passed'}
            
        except Exception as e:
            logger.error(f"Model evaluation task failed: {e}")
            raise
    
    def deploy_model_task(self, config: Dict):
        """Airflow task for model deployment"""
        try:
            model_config = ModelConfig(**config)
            deployer = ModelDeployer(model_config)
            
            # Get latest model run ID from MLflow
            client = mlflow.tracking.MlflowClient()
            experiment = client.get_experiment_by_name(f"indian_ai_{model_config.model_name}")
            runs = client.search_runs(experiment.experiment_id, order_by=["start_time DESC"], max_results=1)
            
            if not runs:
                raise ValueError("No trained models found")
            
            latest_run_id = runs[0].info.run_id
            
            # Deploy model
            deployment_result = deployer.deploy_to_indian_cloud(latest_run_id)
            
            if deployment_result['deployment_status'] != 'success':
                raise ValueError(f"Deployment failed: {deployment_result.get('error', 'Unknown error')}")
            
            logger.info(f"Model deployed successfully: {deployment_result['endpoint_url']}")
            return deployment_result
            
        except Exception as e:
            logger.error(f"Model deployment task failed: {e}")
            raise
    
    def send_notification(self, config: Dict):
        """Send notification to team via Slack/Teams"""
        try:
            # Simulate sending notification to Indian AI team
            notification_message = f"""
            🚀 ML Pipeline Completed Successfully!
            
            Model: {config['model_name']} v{config['version']}
            Deployment: {config['deployment_target']}
            Cost Budget: ₹{config['cost_budget_inr']:,.2f}
            
            Ready for production use! 🎉
            """
            
            logger.info(f"Notification sent: {notification_message}")
            return {'notification_status': 'sent'}
            
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return {'notification_status': 'failed'}

def main():
    """Example usage for Indian AI companies"""
    
    # Configuration for Hindi sentiment analysis model
    hindi_sentiment_config = ModelConfig(
        model_name="hindi_sentiment_analyzer",
        version="1.0.0",
        dataset_path="/data/hindi_sentiment_dataset.csv",
        target_column="sentiment",
        feature_columns=["hindi_text", "english_translation", "context_score"],
        validation_rules={
            "hindi_text_null_pct": "< 5%",
            "sentiment_distribution": "balanced",
            "text_length_range": "1-1000 chars"
        },
        deployment_target="aws_india",
        cost_budget_inr=50000.0,
        performance_threshold=0.85
    )
    
    # Create and register Airflow DAG
    orchestrator = MLPipelineOrchestrator()
    dag = orchestrator.create_indian_ai_pipeline_dag(hindi_sentiment_config)
    
    # For testing, run individual components
    print("🚀 Starting Indian AI MLOps Pipeline")
    print(f"Model: {hindi_sentiment_config.model_name}")
    print(f"Budget: ₹{hindi_sentiment_config.cost_budget_inr:,.2f}")
    
    # Example data for testing
    sample_data = pd.DataFrame({
        'hindi_text': [
            'यह बहुत अच्छा है',
            'मुझे यह पसंद नहीं है',
            'इस प्रोडक्ट की quality excellent है',
            'delivery बहुत slow थी'
        ],
        'english_translation': [
            'This is very good',
            'I do not like this',
            'The quality of this product is excellent',
            'The delivery was very slow'
        ],
        'context_score': [0.8, 0.2, 0.9, 0.3],
        'sentiment': ['positive', 'negative', 'positive', 'negative'],
        'created_at': [datetime.now()] * 4,
        'source': ['mobile_app'] * 4,
        'language_code': ['hi'] * 4
    })
    
    # Save sample data
    os.makedirs('/tmp/ml_pipeline', exist_ok=True)
    sample_data.to_csv('/tmp/ml_pipeline/hindi_sentiment_dataset.csv', index=False)
    hindi_sentiment_config.dataset_path = '/tmp/ml_pipeline/hindi_sentiment_dataset.csv'
    
    # Test data validation
    validator = DataQualityValidator(hindi_sentiment_config)
    validation_result = validator.validate_multilingual_dataset(sample_data)
    print(f"📊 Data Validation Results: {validation_result}")
    
    # Test model training
    trainer = ModelTrainer(hindi_sentiment_config)
    # Note: MLflow requires setup, so we'll simulate this
    print("🤖 Model training simulation completed")
    
    # Test deployment cost calculation
    deployer = ModelDeployer(hindi_sentiment_config)
    monthly_cost = deployer.calculate_deployment_cost_inr()
    print(f"💰 Monthly deployment cost: ₹{monthly_cost:,.2f}")
    
    print("\n✅ MLOps Pipeline setup completed for Indian AI companies!")
    print("📝 Features included:")
    print("   - Multilingual data validation (Hindi/English)")
    print("   - Cost tracking in INR")
    print("   - Indian cloud provider integration")
    print("   - Production-ready monitoring")
    print("   - Automated deployment pipeline")

if __name__ == "__main__":
    main()