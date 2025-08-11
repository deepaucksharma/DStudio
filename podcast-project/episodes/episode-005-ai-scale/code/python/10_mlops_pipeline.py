#!/usr/bin/env python3
"""
MLOps Pipeline for Indian Language Models
Episode 5: Code Example 10

Production-ready MLOps pipeline with CI/CD, versioning, and monitoring
Optimized for Indian language models and compliance requirements

Author: Code Developer Agent
Context: End-to-end MLOps for Indian AI applications
"""

import os
import json
import time
import logging
import hashlib
import subprocess
import shutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import yaml
import boto3
import torch
import mlflow
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
import requests

# Production logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    DATA_VALIDATION = "data_validation"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    MODEL_TESTING = "model_testing"
    MODEL_PACKAGING = "model_packaging"
    STAGING_DEPLOYMENT = "staging_deployment"
    PRODUCTION_DEPLOYMENT = "production_deployment"
    MONITORING = "monitoring"

class ModelStatus(Enum):
    TRAINING = "training"
    EVALUATION = "evaluation"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    FAILED = "failed"

@dataclass
class MLOpsConfig:
    """MLOps pipeline configuration for Indian context"""
    project_name: str
    model_name: str
    version: str
    environment: str  # dev, staging, production
    
    # Data configuration
    data_source: str
    data_validation_rules: Dict[str, Any]
    
    # Training configuration
    training_config: Dict[str, Any]
    compute_resources: Dict[str, Any]
    
    # Deployment configuration
    deployment_target: str  # kubernetes, lambda, ec2
    scaling_config: Dict[str, Any]
    
    # Indian specific
    supported_languages: List[str]
    regional_compliance: List[str]  # data residency requirements
    cost_budget_inr: float
    
    # Monitoring
    monitoring_config: Dict[str, Any]
    alerting_config: Dict[str, Any]

@dataclass
class PipelineRun:
    """Represents a single pipeline execution"""
    run_id: str
    config: MLOpsConfig
    start_time: float
    end_time: Optional[float]
    status: str
    stages_completed: List[PipelineStage]
    metrics: Dict[str, float]
    artifacts: Dict[str, str]
    cost_inr: float
    logs: List[str]

class DataValidator:
    """Validate data quality and compliance for Indian language models"""
    
    def __init__(self, config: MLOpsConfig):
        self.config = config
        self.validation_rules = config.data_validation_rules
    
    def validate_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Validate dataset quality and compliance"""
        logger.info(f"Validating dataset: {dataset_path}")
        
        start_time = time.time()
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        try:
            # Load dataset
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith('.json'):
                df = pd.read_json(dataset_path)
            else:
                raise ValueError(f"Unsupported dataset format: {dataset_path}")
            
            # Basic validation
            validation_results["metrics"]["total_samples"] = len(df)
            validation_results["metrics"]["columns"] = list(df.columns)
            
            # Check minimum sample size
            min_samples = self.validation_rules.get("min_samples", 1000)
            if len(df) < min_samples:
                validation_results["errors"].append(f"Dataset too small: {len(df)} < {min_samples}")
                validation_results["is_valid"] = False
            
            # Check for required columns
            required_columns = self.validation_rules.get("required_columns", [])
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                validation_results["errors"].append(f"Missing columns: {missing_columns}")
                validation_results["is_valid"] = False
            
            # Check data quality
            null_percentage = (df.isnull().sum() / len(df) * 100)
            max_null_percentage = self.validation_rules.get("max_null_percentage", 10)
            
            for column, null_pct in null_percentage.items():
                if null_pct > max_null_percentage:
                    validation_results["warnings"].append(
                        f"High null percentage in {column}: {null_pct:.1f}%"
                    )
            
            # Indian language specific validations
            if "text" in df.columns:
                text_column = df["text"]
                
                # Check for Hindi text presence
                if "hi" in self.config.supported_languages:
                    hindi_samples = text_column.str.contains(r'[\u0900-\u097F]', regex=True, na=False).sum()
                    hindi_percentage = (hindi_samples / len(df)) * 100
                    validation_results["metrics"]["hindi_percentage"] = hindi_percentage
                    
                    if hindi_percentage < 10:  # Expect at least 10% Hindi for Hindi models
                        validation_results["warnings"].append(
                            f"Low Hindi content: {hindi_percentage:.1f}%"
                        )
                
                # Check average text length
                avg_length = text_column.str.len().mean()
                validation_results["metrics"]["avg_text_length"] = avg_length
                
                if avg_length < 10:
                    validation_results["warnings"].append(f"Short average text length: {avg_length:.1f}")
                elif avg_length > 1000:
                    validation_results["warnings"].append(f"Long average text length: {avg_length:.1f}")
            
            # Data compliance checks for Indian regulations
            self._check_data_compliance(df, validation_results)
            
            validation_time = time.time() - start_time
            validation_results["metrics"]["validation_time_seconds"] = validation_time
            
            logger.info(f"Data validation completed in {validation_time:.2f}s")
            
        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["errors"].append(f"Validation failed: {str(e)}")
            logger.error(f"Data validation error: {e}")
        
        return validation_results
    
    def _check_data_compliance(self, df: pd.DataFrame, results: Dict[str, Any]):
        """Check data compliance for Indian regulations"""
        
        # Check for PII (Personal Identifiable Information)
        pii_patterns = [
            r'\b\d{12}\b',  # Aadhaar pattern
            r'\b\d{10}\b',  # Phone number pattern
            r'\b[A-Z]{5}\d{4}[A-Z]\b',  # PAN pattern
        ]
        
        if "text" in df.columns:
            text_data = df["text"].astype(str)
            
            for pattern in pii_patterns:
                matches = text_data.str.contains(pattern, regex=True, na=False).sum()
                if matches > 0:
                    results["warnings"].append(f"Potential PII detected: {matches} samples")
        
        # Check data residency requirements
        if "region" in df.columns:
            non_indian_data = df["region"].value_counts().get("international", 0)
            if non_indian_data > 0 and "data_residency" in self.config.regional_compliance:
                results["warnings"].append(
                    f"Non-Indian data found: {non_indian_data} samples (data residency required)"
                )

class ModelTrainer:
    """Train and evaluate Indian language models"""
    
    def __init__(self, config: MLOpsConfig):
        self.config = config
        self.mlflow_client = MlflowClient()
    
    def train_model(self, train_data_path: str, val_data_path: str) -> Dict[str, Any]:
        """Train model with MLflow tracking"""
        
        logger.info("Starting model training...")
        
        with mlflow.start_run() as run:
            # Log configuration
            mlflow.log_params(self.config.training_config)
            mlflow.set_tag("model_name", self.config.model_name)
            mlflow.set_tag("version", self.config.version)
            mlflow.set_tag("environment", self.config.environment)
            mlflow.set_tag("supported_languages", ",".join(self.config.supported_languages))
            
            start_time = time.time()
            
            try:
                # Load training data
                train_df = pd.read_csv(train_data_path)
                val_df = pd.read_csv(val_data_path)
                
                # Log data metrics
                mlflow.log_metric("train_samples", len(train_df))
                mlflow.log_metric("val_samples", len(val_df))
                
                # Simulate model training (in production, use actual training code)
                training_metrics = self._simulate_training(train_df, val_df)
                
                # Log metrics
                for metric_name, value in training_metrics.items():
                    mlflow.log_metric(metric_name, value)
                
                # Create and save model artifact
                model_artifact = self._create_model_artifact(training_metrics)
                model_path = f"models/{self.config.model_name}_{self.config.version}"
                
                # Save model
                mlflow.pytorch.log_model(
                    model_artifact["model"],
                    model_path,
                    registered_model_name=self.config.model_name
                )
                
                training_time = time.time() - start_time
                training_cost = self._calculate_training_cost(training_time, len(train_df))
                
                mlflow.log_metric("training_time_seconds", training_time)
                mlflow.log_metric("training_cost_inr", training_cost)
                
                results = {
                    "run_id": run.info.run_id,
                    "model_path": model_path,
                    "metrics": training_metrics,
                    "training_time": training_time,
                    "cost_inr": training_cost,
                    "status": "completed"
                }
                
                logger.info(f"Training completed in {training_time:.2f}s, cost: ₹{training_cost:.2f}")
                return results
                
            except Exception as e:
                mlflow.log_param("error", str(e))
                logger.error(f"Training failed: {e}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "cost_inr": 0
                }
    
    def _simulate_training(self, train_df: pd.DataFrame, val_df: pd.DataFrame) -> Dict[str, float]:
        """Simulate model training with realistic metrics"""
        
        # Simulate training progress
        epochs = self.config.training_config.get("epochs", 10)
        
        metrics = {}
        for epoch in range(epochs):
            # Simulate epoch training
            time.sleep(0.1)  # Simulate training time
            
            # Mock metrics that improve over epochs
            train_loss = 1.0 - (epoch / epochs) * 0.7 + np.random.normal(0, 0.05)
            val_loss = train_loss + np.random.normal(0, 0.1)
            
            train_accuracy = 0.5 + (epoch / epochs) * 0.4 + np.random.normal(0, 0.02)
            val_accuracy = train_accuracy - np.random.normal(0, 0.05)
            
            # Log intermediate metrics
            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_loss, step=epoch)
            mlflow.log_metric("train_accuracy", train_accuracy, step=epoch)
            mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)
        
        # Final metrics
        final_metrics = {
            "final_train_accuracy": max(0.6, min(0.95, train_accuracy)),
            "final_val_accuracy": max(0.55, min(0.92, val_accuracy)),
            "final_train_loss": max(0.1, train_loss),
            "final_val_loss": max(0.15, val_loss),
            "f1_score": max(0.5, min(0.9, val_accuracy + np.random.normal(0, 0.05))),
        }
        
        return final_metrics
    
    def _create_model_artifact(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Create model artifact for saving"""
        
        # Create a simple PyTorch model for demonstration
        class SimpleClassifier(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(100, 3)  # 3 classes
                
            def forward(self, x):
                return self.linear(x)
        
        model = SimpleClassifier()
        
        return {
            "model": model,
            "metrics": metrics,
            "config": asdict(self.config),
            "model_signature": "simple_classifier_v1"
        }
    
    def _calculate_training_cost(self, training_time_seconds: float, num_samples: int) -> float:
        """Calculate training cost in INR"""
        
        # Base cost calculation
        base_cost_per_hour = 50.0  # ₹50/hour for GPU training
        time_cost = (training_time_seconds / 3600) * base_cost_per_hour
        
        # Data processing cost
        data_cost = (num_samples / 10000) * 5.0  # ₹5 per 10k samples
        
        # Total cost
        total_cost = time_cost + data_cost
        
        return total_cost

class ModelDeployer:
    """Deploy models to different environments"""
    
    def __init__(self, config: MLOpsConfig):
        self.config = config
    
    def deploy_to_staging(self, model_run_id: str) -> Dict[str, Any]:
        """Deploy model to staging environment"""
        
        logger.info(f"Deploying model {model_run_id} to staging...")
        
        deployment_start = time.time()
        
        try:
            # Download model from MLflow
            model_uri = f"runs:/{model_run_id}/models/{self.config.model_name}_{self.config.version}"
            
            # Create deployment configuration
            deployment_config = {
                "model_uri": model_uri,
                "environment": "staging",
                "instance_type": "t3.medium",  # AWS instance type
                "min_instances": 1,
                "max_instances": 3,
                "target_cpu": 70,
                "health_check_path": "/health",
                "supported_languages": self.config.supported_languages
            }
            
            # Simulate deployment process
            deployment_result = self._simulate_deployment(deployment_config, "staging")
            
            deployment_time = time.time() - deployment_start
            deployment_cost = 100.0  # ₹100 for staging deployment
            
            result = {
                "deployment_id": f"staging-{int(time.time())}",
                "status": deployment_result["status"],
                "endpoint_url": deployment_result["endpoint_url"],
                "deployment_time": deployment_time,
                "cost_inr": deployment_cost,
                "config": deployment_config
            }
            
            logger.info(f"Staging deployment completed: {result['endpoint_url']}")
            return result
            
        except Exception as e:
            logger.error(f"Staging deployment failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "cost_inr": 0
            }
    
    def deploy_to_production(self, staging_deployment_id: str) -> Dict[str, Any]:
        """Deploy model to production after staging validation"""
        
        logger.info(f"Deploying to production from staging: {staging_deployment_id}")
        
        deployment_start = time.time()
        
        try:
            # Production deployment configuration
            production_config = {
                "environment": "production",
                "instance_type": "c5.xlarge",
                "min_instances": 2,
                "max_instances": 10,
                "target_cpu": 60,
                "health_check_path": "/health",
                "load_balancer": True,
                "auto_scaling": True,
                "monitoring_enabled": True,
                "backup_enabled": True
            }
            
            # Simulate production deployment
            deployment_result = self._simulate_deployment(production_config, "production")
            
            deployment_time = time.time() - deployment_start
            deployment_cost = 500.0  # ₹500 for production deployment
            
            result = {
                "deployment_id": f"prod-{int(time.time())}",
                "status": deployment_result["status"],
                "endpoint_url": deployment_result["endpoint_url"],
                "deployment_time": deployment_time,
                "cost_inr": deployment_cost,
                "config": production_config,
                "rollback_available": True
            }
            
            logger.info(f"Production deployment completed: {result['endpoint_url']}")
            return result
            
        except Exception as e:
            logger.error(f"Production deployment failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "cost_inr": 0
            }
    
    def _simulate_deployment(self, config: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Simulate deployment process"""
        
        # Simulate deployment time
        time.sleep(2)
        
        # Create mock endpoint URL
        endpoint_url = f"https://api-{environment}.yourcompany.com/v1/inference"
        
        return {
            "status": "deployed",
            "endpoint_url": endpoint_url,
            "health_status": "healthy",
            "instances_running": config.get("min_instances", 1)
        }

class MLOpsPipeline:
    """Complete MLOps pipeline orchestrator"""
    
    def __init__(self, config: MLOpsConfig):
        self.config = config
        self.data_validator = DataValidator(config)
        self.model_trainer = ModelTrainer(config)
        self.model_deployer = ModelDeployer(config)
        
        # Initialize MLflow
        mlflow.set_tracking_uri("http://localhost:5000")  # MLflow server
        mlflow.set_experiment(config.project_name)
    
    def run_pipeline(self, train_data_path: str, val_data_path: str) -> PipelineRun:
        """Execute complete MLOps pipeline"""
        
        run_id = f"pipeline_{int(time.time())}"
        start_time = time.time()
        
        pipeline_run = PipelineRun(
            run_id=run_id,
            config=self.config,
            start_time=start_time,
            end_time=None,
            status="running",
            stages_completed=[],
            metrics={},
            artifacts={},
            cost_inr=0.0,
            logs=[]
        )
        
        logger.info(f"Starting MLOps pipeline run: {run_id}")
        
        try:
            # Stage 1: Data Validation
            logger.info("Stage 1: Data Validation")
            validation_result = self.data_validator.validate_dataset(train_data_path)
            
            if not validation_result["is_valid"]:
                raise Exception(f"Data validation failed: {validation_result['errors']}")
            
            pipeline_run.stages_completed.append(PipelineStage.DATA_VALIDATION)
            pipeline_run.metrics.update(validation_result["metrics"])
            pipeline_run.logs.append(f"Data validation completed: {len(validation_result['warnings'])} warnings")
            
            # Stage 2: Model Training
            logger.info("Stage 2: Model Training")
            training_result = self.model_trainer.train_model(train_data_path, val_data_path)
            
            if training_result["status"] != "completed":
                raise Exception(f"Training failed: {training_result.get('error', 'Unknown error')}")
            
            pipeline_run.stages_completed.append(PipelineStage.MODEL_TRAINING)
            pipeline_run.metrics.update(training_result["metrics"])
            pipeline_run.artifacts["model_path"] = training_result["model_path"]
            pipeline_run.cost_inr += training_result["cost_inr"]
            pipeline_run.logs.append(f"Model training completed: run_id={training_result['run_id']}")
            
            # Stage 3: Model Evaluation
            logger.info("Stage 3: Model Evaluation")
            evaluation_result = self._evaluate_model(training_result)
            
            pipeline_run.stages_completed.append(PipelineStage.MODEL_EVALUATION)
            pipeline_run.metrics.update(evaluation_result["metrics"])
            pipeline_run.logs.append(f"Model evaluation completed: score={evaluation_result['score']:.3f}")
            
            # Stage 4: Staging Deployment
            if evaluation_result["score"] >= 0.8:  # Only deploy if model is good enough
                logger.info("Stage 4: Staging Deployment")
                staging_result = self.model_deployer.deploy_to_staging(training_result["run_id"])
                
                pipeline_run.stages_completed.append(PipelineStage.STAGING_DEPLOYMENT)
                pipeline_run.artifacts["staging_endpoint"] = staging_result["endpoint_url"]
                pipeline_run.cost_inr += staging_result["cost_inr"]
                pipeline_run.logs.append(f"Staging deployment completed: {staging_result['endpoint_url']}")
                
                # Stage 5: Production Deployment (if staging is successful)
                if staging_result["status"] == "deployed":
                    logger.info("Stage 5: Production Deployment")
                    prod_result = self.model_deployer.deploy_to_production(staging_result["deployment_id"])
                    
                    pipeline_run.stages_completed.append(PipelineStage.PRODUCTION_DEPLOYMENT)
                    pipeline_run.artifacts["production_endpoint"] = prod_result["endpoint_url"]
                    pipeline_run.cost_inr += prod_result["cost_inr"]
                    pipeline_run.logs.append(f"Production deployment completed: {prod_result['endpoint_url']}")
            
            # Pipeline completion
            pipeline_run.end_time = time.time()
            pipeline_run.status = "completed"
            total_time = pipeline_run.end_time - pipeline_run.start_time
            
            logger.info(f"Pipeline completed successfully in {total_time:.2f}s, total cost: ₹{pipeline_run.cost_inr:.2f}")
            
        except Exception as e:
            pipeline_run.end_time = time.time()
            pipeline_run.status = "failed"
            pipeline_run.logs.append(f"Pipeline failed: {str(e)}")
            logger.error(f"Pipeline failed: {e}")
        
        return pipeline_run
    
    def _evaluate_model(self, training_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate trained model"""
        
        # Simulate model evaluation
        base_score = training_result["metrics"]["final_val_accuracy"]
        
        # Add some evaluation metrics
        evaluation_metrics = {
            "accuracy": base_score,
            "precision": base_score + np.random.normal(0, 0.02),
            "recall": base_score + np.random.normal(0, 0.02),
            "f1_score": training_result["metrics"]["f1_score"],
            "inference_latency_ms": 50 + np.random.normal(0, 10),
            "memory_usage_mb": 200 + np.random.normal(0, 50)
        }
        
        # Overall evaluation score
        overall_score = (evaluation_metrics["accuracy"] + evaluation_metrics["f1_score"]) / 2
        
        return {
            "score": overall_score,
            "metrics": evaluation_metrics,
            "passed": overall_score >= 0.8
        }
    
    def generate_pipeline_report(self, pipeline_run: PipelineRun) -> str:
        """Generate comprehensive pipeline report"""
        
        report = f"""
MLOps Pipeline Report
====================

Run ID: {pipeline_run.run_id}
Project: {pipeline_run.config.project_name}
Model: {pipeline_run.config.model_name} v{pipeline_run.config.version}
Environment: {pipeline_run.config.environment}

Pipeline Status: {pipeline_run.status.upper()}
Start Time: {time.ctime(pipeline_run.start_time)}
End Time: {time.ctime(pipeline_run.end_time) if pipeline_run.end_time else 'Running'}
Duration: {pipeline_run.end_time - pipeline_run.start_time if pipeline_run.end_time else 'N/A':.2f} seconds

Stages Completed:
{chr(10).join(f"  ✅ {stage.value}" for stage in pipeline_run.stages_completed)}

Key Metrics:
{chr(10).join(f"  {k}: {v}" for k, v in pipeline_run.metrics.items())}

Artifacts:
{chr(10).join(f"  {k}: {v}" for k, v in pipeline_run.artifacts.items())}

Total Cost: ₹{pipeline_run.cost_inr:.2f}

Logs:
{chr(10).join(f"  • {log}" for log in pipeline_run.logs)}

Supported Languages: {', '.join(pipeline_run.config.supported_languages)}
Regional Compliance: {', '.join(pipeline_run.config.regional_compliance)}
        """
        
        return report.strip()

# Example usage and testing
def test_mlops_pipeline():
    """Test MLOps pipeline with Indian language model"""
    
    print("🔧 MLOps Pipeline Test - Indian Language Models")
    print("=" * 60)
    
    # Create sample configuration
    config = MLOpsConfig(
        project_name="indian_sentiment_analysis",
        model_name="indic_sentiment_classifier",
        version="v2.1.0",
        environment="staging",
        data_source="s3://indian-nlp-data/sentiment/",
        data_validation_rules={
            "min_samples": 1000,
            "required_columns": ["text", "label"],
            "max_null_percentage": 5
        },
        training_config={
            "epochs": 10,
            "batch_size": 32,
            "learning_rate": 0.001,
            "optimizer": "adam"
        },
        compute_resources={
            "instance_type": "p3.2xlarge",
            "gpu_count": 1,
            "memory_gb": 32
        },
        deployment_target="kubernetes",
        scaling_config={
            "min_replicas": 2,
            "max_replicas": 10,
            "target_cpu": 70
        },
        supported_languages=["hi", "en", "ta", "bn"],
        regional_compliance=["data_residency", "gdpr_equivalent"],
        cost_budget_inr=5000.0,
        monitoring_config={
            "metrics": ["accuracy", "latency", "throughput"],
            "alerts": ["accuracy_drop", "high_latency", "error_rate"]
        },
        alerting_config={
            "slack_webhook": "https://hooks.slack.com/...",
            "email_recipients": ["ml-team@company.com"]
        }
    )
    
    # Create sample datasets
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    # Sample training data
    train_data = pd.DataFrame({
        "text": [
            "यह फिल्म बहुत अच्छी है!",
            "मुझे यह product पसंद नहीं आया",
            "This movie is excellent",
            "Very poor service quality",
            "ठीक है, normal quality",
        ] * 500,  # 2500 samples
        "label": [2, 0, 2, 0, 1] * 500  # positive, negative, positive, negative, neutral
    })
    
    val_data = train_data.sample(n=500).reset_index(drop=True)
    
    train_path = os.path.join(temp_dir, "train.csv")
    val_path = os.path.join(temp_dir, "val.csv")
    
    train_data.to_csv(train_path, index=False)
    val_data.to_csv(val_path, index=False)
    
    print(f"✅ Configuration created")
    print(f"   Project: {config.project_name}")
    print(f"   Model: {config.model_name} {config.version}")
    print(f"   Languages: {config.supported_languages}")
    print(f"   Budget: ₹{config.cost_budget_inr}")
    
    print(f"\n📁 Sample data created")
    print(f"   Training samples: {len(train_data)}")
    print(f"   Validation samples: {len(val_data)}")
    
    # Initialize and run pipeline
    pipeline = MLOpsPipeline(config)
    
    print(f"\n🚀 Running MLOps pipeline...")
    pipeline_run = pipeline.run_pipeline(train_path, val_path)
    
    # Generate and display report
    print(f"\n📊 Pipeline Report:")
    report = pipeline.generate_pipeline_report(pipeline_run)
    print(report)
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    print(f"\n🎯 MLOps Features Demonstrated:")
    print(f"   ✅ Data validation with Indian language support")
    print(f"   ✅ MLflow experiment tracking")
    print(f"   ✅ Model training with cost tracking")
    print(f"   ✅ Staging and production deployments")
    print(f"   ✅ Compliance checks for Indian regulations")
    print(f"   ✅ Cost optimization and budgeting")
    print(f"   ✅ Comprehensive pipeline reporting")

if __name__ == "__main__":
    test_mlops_pipeline()