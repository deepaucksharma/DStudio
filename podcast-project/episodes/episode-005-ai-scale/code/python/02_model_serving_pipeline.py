#!/usr/bin/env python3
"""
Model Serving Pipeline with A/B Testing for AI at Scale
Episode 5: Code Example 2 - भारतीय ई-कॉमर्स के लिए AI मॉडल सर्विंग

Production-ready model serving system for Indian e-commerce platforms
Supporting A/B testing, shadow deployment, and canary rollouts

भारतीय संदर्भ:
- Flipkart, Amazon India, Myntra जैसे platforms के लिए optimized
- Hindi, Tamil, Bengali समेत multiple Indian languages support
- INR में cost tracking और optimization
- Indian cloud regions (Mumbai, Chennai, Hyderabad) support
- Code-mixing (Hinglish) text processing capabilities

Real Production Examples:
- Flipkart: 300M+ requests/day sentiment analysis
- Amazon India: 50M+ product reviews processed daily
- Myntra: 20M+ fashion reviews in multiple languages
- Zomato: 100M+ restaurant reviews sentiment tracking

Author: Code Developer Agent
Context: Flipkart/Amazon India scale model serving - भारतीय स्केल पर AI मॉडल deployment
"""

import asyncio
import json
import time
import uuid
import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import redis
import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
from transformers import pipeline, AutoTokenizer, AutoModel
import asyncpg
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Production logging setup - Mumbai style clear messaging
# प्रोडक्शन लॉगिंग सेटअप - स्पष्ट संदेश के साथ
logger = structlog.get_logger()

# Prometheus metrics for production monitoring
# प्रोडक्शन मॉनिटरिंग के लिए मेट्रिक्स - Flipkart/Amazon जैसे scale पर
REQUEST_COUNT = Counter('model_requests_total', 'Total model requests', ['model_version', 'experiment'])
REQUEST_DURATION = Histogram('model_request_duration_seconds', 'Request duration')  # Response time tracking
MODEL_ACCURACY = Gauge('model_accuracy', 'Current model accuracy', ['model_version'])  # Model performance
ACTIVE_EXPERIMENTS = Gauge('active_ab_tests', 'Number of active A/B tests')  # A/B test count
INFERENCE_COST_INR = Counter('inference_cost_inr_total', 'Total inference cost in INR')  # भारतीय रुपए में cost tracking

class DeploymentType(Enum):
    """
    Deployment types for Indian e-commerce scale
    भारतीय ई-कॉमर्स स्केल के लिए deployment types
    """
    PRODUCTION = "production"    # मुख्य production model - 95% traffic
    SHADOW = "shadow"           # Shadow testing - बिना user impact के testing
    CANARY = "canary"          # Canary deployment - 5% traffic for testing
    A_B_TEST = "ab_test"       # A/B testing - traffic split between models

class ModelStatus(Enum):
    """
    Model health status for monitoring
    मॉडल की health status - Flipkart/Amazon जैसे monitoring के लिए
    """
    HEALTHY = "healthy"        # सब कुछ ठीक है - normal operations
    DEGRADED = "degraded"      # Performance issues - slow responses
    UNHEALTHY = "unhealthy"    # Model failure - need immediate action
    LOADING = "loading"        # Model loading in progress

@dataclass
class ModelConfig:
    """
    Configuration for model serving - मॉडल सर्विंग की configuration
    भारतीय भाषाओं और cost optimization के साथ
    """
    model_id: str                        # Model का unique identifier
    model_path: str                      # Model file path or HuggingFace model name
    model_version: str                   # Version tracking के लिए (e.g., "2.1.0")
    deployment_type: DeploymentType      # Production, Canary, Shadow आदि
    traffic_percentage: float = 100.0    # Traffic percentage (0-100)
    max_batch_size: int = 32            # Batch size limit - performance optimization
    timeout_seconds: float = 5.0         # Request timeout - Indian latency को ध्यान में रखकर
    cost_per_request_inr: float = 0.05  # ₹0.05 per request - Indian pricing
    supported_languages: List[str] = None  # Supported Indian languages
    
    def __post_init__(self):
        """Initialize supported Indian languages"""
        if self.supported_languages is None:
            # Major Indian languages - भारत की मुख्य भाषाएं
            self.supported_languages = [
                "hi",  # Hindi - हिंदी
                "en",  # English
                "ta",  # Tamil - तमिल
                "bn",  # Bengali - बंगाली  
                "te",  # Telugu - तेलुगु
                "mr",  # Marathi - मराठी
                "gu",  # Gujarati - गुजराती
                "kn",  # Kannada - कन्नड़
            ]

@dataclass
class PredictionRequest:
    """Standardized prediction request"""
    text: str
    user_id: str
    session_id: str
    language: str = "hi"
    context: Dict[str, Any] = None
    experiment_id: Optional[str] = None

@dataclass
class PredictionResponse:
    """Standardized prediction response"""
    prediction: Any
    confidence: float
    model_version: str
    response_time_ms: float
    cost_inr: float
    experiment_id: Optional[str] = None
    metadata: Dict[str, Any] = None

class IndianLanguageModel:
    """
    Model wrapper optimized for Indian languages
    Supports Hindi, Tamil, Bengali, and English
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.status = ModelStatus.LOADING
        self.load_time = None
        self.request_count = 0
        self.total_cost_inr = 0.0
        
        logger.info("Initializing Indian language model", 
                   model_id=config.model_id, version=config.model_version)
    
    async def load_model(self):
        """Load model asynchronously"""
        try:
            start_time = time.time()
            
            # Load different models based on task
            if "sentiment" in self.config.model_id:
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model="ai4bharat/indic-bert",
                    tokenizer="ai4bharat/indic-bert",
                    device=0 if torch.cuda.is_available() else -1
                )
            elif "translation" in self.config.model_id:
                self.pipeline = pipeline(
                    "translation",
                    model="ai4bharat/indictrans2-indic-en-1B",
                    device=0 if torch.cuda.is_available() else -1
                )
            else:
                # Default to text classification
                self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)
                self.model = AutoModel.from_pretrained(self.config.model_path)
                self.pipeline = pipeline(
                    "text-classification",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if torch.cuda.is_available() else -1
                )
            
            self.load_time = time.time() - start_time
            self.status = ModelStatus.HEALTHY
            
            logger.info("Model loaded successfully",
                       model_id=self.config.model_id,
                       load_time=f"{self.load_time:.2f}s")
            
        except Exception as e:
            self.status = ModelStatus.UNHEALTHY
            logger.error("Model loading failed",
                        model_id=self.config.model_id,
                        error=str(e))
            raise
    
    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Make prediction with cost tracking"""
        if self.status != ModelStatus.HEALTHY:
            raise HTTPException(status_code=503, detail="Model not available")
        
        start_time = time.time()
        
        try:
            # Preprocess text for Indian languages
            processed_text = self._preprocess_indian_text(request.text, request.language)
            
            # Make prediction
            result = self.pipeline(processed_text)
            
            # Process result based on model type
            prediction, confidence = self._process_prediction_result(result)
            
            # Calculate metrics
            response_time_ms = (time.time() - start_time) * 1000
            cost_inr = self.config.cost_per_request_inr
            
            # Update counters
            self.request_count += 1
            self.total_cost_inr += cost_inr
            
            # Update Prometheus metrics
            REQUEST_COUNT.labels(
                model_version=self.config.model_version,
                experiment=request.experiment_id or "none"
            ).inc()
            REQUEST_DURATION.observe(response_time_ms / 1000)
            INFERENCE_COST_INR.inc(cost_inr)
            
            response = PredictionResponse(
                prediction=prediction,
                confidence=confidence,
                model_version=self.config.model_version,
                response_time_ms=response_time_ms,
                cost_inr=cost_inr,
                experiment_id=request.experiment_id,
                metadata={
                    "language": request.language,
                    "processed_text_length": len(processed_text),
                    "original_text_length": len(request.text)
                }
            )
            
            logger.info("Prediction completed",
                       model_version=self.config.model_version,
                       response_time_ms=response_time_ms,
                       cost_inr=cost_inr)
            
            return response
            
        except Exception as e:
            logger.error("Prediction failed",
                        model_id=self.config.model_id,
                        error=str(e))
            raise HTTPException(status_code=500, detail="Prediction failed")
    
    def _preprocess_indian_text(self, text: str, language: str) -> str:
        """
        Preprocess text for Indian languages and code-mixing
        भारतीय भाषाओं और code-mixing के लिए text preprocessing
        
        Real examples from Indian e-commerce:
        - "यह product bahut अच्छा है" -> Mixed Hindi-English
        - "Delivery thik tha but quality मैं disappointed हूं"
        """
        
        # Handle common Hinglish code-mixing patterns
        # आम हिंग्लिश patterns को handle करना
        hinglish_replacements = {
            "भाई": "bhai",           # Brother
            "यार": "yaar",           # Friend  
            "बिल्कुल": "bilkul",     # Absolutely
            "अच्छा": "accha",        # Good
            "बहुत": "bahut",         # Very/Much
            "ठीक": "thik",           # Okay/Fine
            "बुरा": "bura",          # Bad
            "पैसा": "paisa",         # Money
            "वसूल": "vasool",        # Worth it
            "धन्यवाद": "dhanyawad",  # Thank you
            "माफ़": "maaf",          # Sorry
        }
        
        # Apply replacements for better model understanding
        for hindi, english in hinglish_replacements.items():
            text = text.replace(hindi, english)
        
        # Handle common e-commerce terms in Indian context
        # भारतीय ई-कॉमर्स के आम शब्दों को normalize करना
        ecommerce_terms = {
            "delivery": "delivery",
            "product": "product", 
            "quality": "quality",
            "price": "price",
            "service": "service",
            "customer care": "customer_care",
            "return": "return",
            "refund": "refund",
        }
        
        # Normalize whitespace and remove extra spaces
        text = " ".join(text.split())
        
        # Add language prefix for model context
        if language != "en":
            text = f"[{language}] {text}"
        
        return text
    
    def _process_prediction_result(self, result) -> Tuple[Any, float]:
        """Process prediction result from pipeline"""
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], dict):
                # Classification result
                prediction = result[0].get('label', 'UNKNOWN')
                confidence = result[0].get('score', 0.0)
            else:
                prediction = result[0]
                confidence = 0.9  # Default confidence
        else:
            prediction = result
            confidence = 0.8
        
        return prediction, float(confidence)

class ExperimentManager:
    """
    A/B Testing and Experiment Management
    Production-grade experiment tracking for Indian scale
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.active_experiments: Dict[str, Dict] = {}
        
    async def create_experiment(self, 
                              experiment_id: str,
                              model_a_config: ModelConfig,
                              model_b_config: ModelConfig,
                              traffic_split: float = 0.5,
                              duration_hours: int = 24) -> bool:
        """Create new A/B test experiment"""
        
        experiment_data = {
            "id": experiment_id,
            "model_a": asdict(model_a_config),
            "model_b": asdict(model_b_config),
            "traffic_split": traffic_split,
            "start_time": time.time(),
            "duration_hours": duration_hours,
            "status": "active",
            "results": {
                "model_a": {"requests": 0, "total_cost_inr": 0, "avg_response_time": 0},
                "model_b": {"requests": 0, "total_cost_inr": 0, "avg_response_time": 0}
            }
        }
        
        # Store in Redis with expiration
        await self.redis.setex(
            f"experiment:{experiment_id}",
            duration_hours * 3600,
            json.dumps(experiment_data)
        )
        
        self.active_experiments[experiment_id] = experiment_data
        ACTIVE_EXPERIMENTS.set(len(self.active_experiments))
        
        logger.info("A/B test created",
                   experiment_id=experiment_id,
                   model_a=model_a_config.model_id,
                   model_b=model_b_config.model_id,
                   traffic_split=traffic_split)
        
        return True
    
    def should_use_model_b(self, user_id: str, experiment_id: str) -> bool:
        """Determine if user should get Model B (consistent hashing)"""
        if experiment_id not in self.active_experiments:
            return False
        
        # Use consistent hashing based on user_id
        hash_input = f"{experiment_id}:{user_id}".encode('utf-8')
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        
        traffic_split = self.active_experiments[experiment_id]["traffic_split"]
        return (hash_value % 100) < (traffic_split * 100)
    
    async def record_experiment_result(self, 
                                     experiment_id: str,
                                     model_used: str,
                                     response_time: float,
                                     cost_inr: float):
        """Record experiment result for analysis"""
        if experiment_id not in self.active_experiments:
            return
        
        # Update in-memory stats
        results = self.active_experiments[experiment_id]["results"][model_used]
        results["requests"] += 1
        results["total_cost_inr"] += cost_inr
        
        # Update average response time
        old_avg = results["avg_response_time"]
        new_count = results["requests"]
        results["avg_response_time"] = ((old_avg * (new_count - 1)) + response_time) / new_count
        
        # Update in Redis (async)
        experiment_data = self.active_experiments[experiment_id]
        await self.redis.set(
            f"experiment:{experiment_id}",
            json.dumps(experiment_data)
        )

class ModelServingPipeline:
    """
    Main model serving pipeline with A/B testing, shadow deployment, and canary rollouts
    Optimized for Indian e-commerce scale (millions of requests/day)
    """
    
    def __init__(self):
        self.models: Dict[str, IndianLanguageModel] = {}
        self.experiment_manager = None
        self.redis_client = None
        self.db_pool = None
        self.app = FastAPI(title="AI Model Serving Pipeline - Indian Scale")
        
        # Add CORS for web applications
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
    
    async def initialize(self):
        """Initialize all components"""
        
        # Setup Redis connection for experiment management
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Setup PostgreSQL connection for logging
        self.db_pool = await asyncpg.create_pool(
            "postgresql://user:password@localhost/modelserving",
            min_size=10,
            max_size=50
        )
        
        # Initialize experiment manager
        self.experiment_manager = ExperimentManager(self.redis_client)
        
        # Load production models
        await self._load_production_models()
        
        logger.info("Model serving pipeline initialized successfully")
    
    async def _load_production_models(self):
        """Load production models for Indian languages"""
        
        # Production sentiment analysis model
        sentiment_config = ModelConfig(
            model_id="indic_sentiment_v2",
            model_path="ai4bharat/indic-bert",
            model_version="2.1.0",
            deployment_type=DeploymentType.PRODUCTION,
            cost_per_request_inr=0.03
        )
        
        sentiment_model = IndianLanguageModel(sentiment_config)
        await sentiment_model.load_model()
        self.models["sentiment"] = sentiment_model
        
        # Canary model for testing
        sentiment_canary_config = ModelConfig(
            model_id="indic_sentiment_v3_canary",
            model_path="ai4bharat/indic-bert",
            model_version="3.0.0-beta",
            deployment_type=DeploymentType.CANARY,
            traffic_percentage=5.0,  # 5% traffic
            cost_per_request_inr=0.04
        )
        
        sentiment_canary = IndianLanguageModel(sentiment_canary_config)
        await sentiment_canary.load_model()
        self.models["sentiment_canary"] = sentiment_canary
        
        # Create A/B test
        await self.experiment_manager.create_experiment(
            "sentiment_v2_vs_v3",
            sentiment_config,
            sentiment_canary_config,
            traffic_split=0.05,  # 5% get new model
            duration_hours=48
        )
        
        logger.info("Production models loaded",
                   model_count=len(self.models))
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            model_statuses = {}
            for name, model in self.models.items():
                model_statuses[name] = {
                    "status": model.status.value,
                    "requests": model.request_count,
                    "total_cost_inr": f"₹{model.total_cost_inr:.2f}"
                }
            
            return {
                "status": "healthy",
                "models": model_statuses,
                "active_experiments": len(self.experiment_manager.active_experiments) if self.experiment_manager else 0,
                "timestamp": time.time()
            }
        
        @self.app.post("/predict/sentiment")
        async def predict_sentiment(request: PredictionRequest):
            """Sentiment analysis with A/B testing"""
            return await self._route_prediction("sentiment", request)
        
        @self.app.post("/predict/batch")
        async def batch_predict(requests: List[PredictionRequest]):
            """Batch prediction for efficiency"""
            if len(requests) > 100:  # Limit batch size
                raise HTTPException(status_code=400, detail="Batch size too large")
            
            results = []
            total_cost = 0
            
            for req in requests:
                try:
                    result = await self._route_prediction("sentiment", req)
                    results.append(result)
                    total_cost += result.cost_inr
                except Exception as e:
                    results.append({"error": str(e), "request_id": req.user_id})
            
            return {
                "results": results,
                "batch_size": len(requests),
                "total_cost_inr": f"₹{total_cost:.2f}",
                "timestamp": time.time()
            }
        
        @self.app.get("/experiments")
        async def get_experiments():
            """Get active experiments"""
            if not self.experiment_manager:
                return {"experiments": []}
            
            return {
                "active_experiments": self.experiment_manager.active_experiments,
                "count": len(self.experiment_manager.active_experiments)
            }
        
        @self.app.post("/experiments/{experiment_id}/stop")
        async def stop_experiment(experiment_id: str):
            """Stop an active experiment"""
            if experiment_id in self.experiment_manager.active_experiments:
                experiment = self.experiment_manager.active_experiments[experiment_id]
                experiment["status"] = "stopped"
                
                # Calculate results
                model_a_results = experiment["results"]["model_a"]
                model_b_results = experiment["results"]["model_b"]
                
                winner = "model_a" if model_a_results["avg_response_time"] < model_b_results["avg_response_time"] else "model_b"
                
                del self.experiment_manager.active_experiments[experiment_id]
                ACTIVE_EXPERIMENTS.set(len(self.experiment_manager.active_experiments))
                
                return {
                    "experiment_id": experiment_id,
                    "status": "stopped",
                    "results": experiment["results"],
                    "winner": winner,
                    "total_requests": model_a_results["requests"] + model_b_results["requests"],
                    "total_cost_inr": f"₹{model_a_results['total_cost_inr'] + model_b_results['total_cost_inr']:.2f}"
                }
            else:
                raise HTTPException(status_code=404, detail="Experiment not found")
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Prometheus metrics endpoint"""
            return prometheus_client.generate_latest()
    
    async def _route_prediction(self, model_type: str, request: PredictionRequest) -> PredictionResponse:
        """Route prediction request with A/B testing logic"""
        
        # Check for active experiments
        experiment_id = "sentiment_v2_vs_v3"  # Default experiment
        model_key = model_type
        
        if (self.experiment_manager and 
            experiment_id in self.experiment_manager.active_experiments and
            self.experiment_manager.should_use_model_b(request.user_id, experiment_id)):
            
            model_key = f"{model_type}_canary"
            request.experiment_id = experiment_id
        
        # Get the appropriate model
        if model_key not in self.models:
            raise HTTPException(status_code=404, detail=f"Model {model_key} not found")
        
        model = self.models[model_key]
        
        # Make prediction
        response = await model.predict(request)
        
        # Record experiment result if applicable
        if request.experiment_id and self.experiment_manager:
            model_used = "model_b" if "canary" in model_key else "model_a"
            await self.experiment_manager.record_experiment_result(
                request.experiment_id,
                model_used,
                response.response_time_ms,
                response.cost_inr
            )
        
        # Log to database (async)
        asyncio.create_task(self._log_prediction_to_db(request, response))
        
        return response
    
    async def _log_prediction_to_db(self, request: PredictionRequest, response: PredictionResponse):
        """Log prediction to PostgreSQL for analytics"""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO prediction_logs 
                    (user_id, session_id, model_version, prediction, confidence, 
                     response_time_ms, cost_inr, experiment_id, language, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                request.user_id,
                request.session_id,
                response.model_version,
                json.dumps(response.prediction),
                response.confidence,
                response.response_time_ms,
                response.cost_inr,
                response.experiment_id,
                request.language,
                time.time()
                )
        except Exception as e:
            logger.error("Failed to log prediction", error=str(e))

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    pipeline = ModelServingPipeline()
    
    @pipeline.app.on_event("startup")
    async def startup_event():
        await pipeline.initialize()
    
    @pipeline.app.on_event("shutdown")
    async def shutdown_event():
        if pipeline.db_pool:
            await pipeline.db_pool.close()
        if pipeline.redis_client:
            pipeline.redis_client.close()
    
    return pipeline.app

# Example usage and testing
async def test_model_serving():
    """Test the model serving pipeline"""
    
    # Create test requests (भारतीय e-commerce context से real examples)
    test_requests = [
        PredictionRequest(
            text="यह product बहुत अच्छा है! Quality bilkul solid है, Flipkart से खरीदना worth it था।",
            user_id="flipkart_user_123",
            session_id="session_456",
            language="hi",
            context={"platform": "flipkart", "category": "electronics"}
        ),
        PredictionRequest(
            text="Amazon Prime delivery bahut slow tha, but product quality मैं satisfied हूं। Customer service भी responsive थी।",
            user_id="amazon_user_124", 
            session_id="session_457",
            language="hi",
            context={"platform": "amazon", "category": "fashion"}
        ),
        PredictionRequest(
            text="Myntra से ordered dress fitting perfect है! Paisa vasool product, recommended to all friends.",
            user_id="myntra_user_125",
            session_id="session_458", 
            language="hi",
            context={"platform": "myntra", "category": "fashion"}
        ),
        PredictionRequest(
            text="Zomato food delivery experience was terrible. Order came cold and customer care was not helpful at all.",
            user_id="zomato_user_126",
            session_id="session_459",
            language="en",
            context={"platform": "zomato", "category": "food"}
        ),
        PredictionRequest(
            text="Swiggy ka service bahut बढ़िया है। Fast delivery और food quality भी maintained रहती है। Highly satisfied!",
            user_id="swiggy_user_127",
            session_id="session_460",
            language="hi",
            context={"platform": "swiggy", "category": "food"}
        )
    ]
    
    pipeline = ModelServingPipeline()
    await pipeline.initialize()
    
    print("🚀 Model Serving Pipeline Test - Indian E-commerce Scale")
    print("=" * 60)
    
    total_cost = 0
    for i, request in enumerate(test_requests, 1):
        try:
            response = await pipeline._route_prediction("sentiment", request)
            total_cost += response.cost_inr
            
            print(f"\n📝 Request {i}:")
            print(f"Text: {request.text}")
            print(f"Language: {request.language}")
            print(f"Prediction: {response.prediction}")
            print(f"Confidence: {response.confidence:.3f}")
            print(f"Model: {response.model_version}")
            print(f"Response Time: {response.response_time_ms:.1f}ms")
            print(f"Cost: ₹{response.cost_inr:.3f}")
            if response.experiment_id:
                print(f"Experiment: {response.experiment_id}")
                
        except Exception as e:
            print(f"Error processing request {i}: {e}")
    
    print(f"\n💰 Total Cost: ₹{total_cost:.2f}")
    print(f"🔬 Active Experiments: {len(pipeline.experiment_manager.active_experiments)}")
    print(f"🏭 Models Loaded: {len(pipeline.models)}")
    
    # Show experiment results
    if pipeline.experiment_manager.active_experiments:
        print(f"\n📊 Experiment Results:")
        for exp_id, exp_data in pipeline.experiment_manager.active_experiments.items():
            print(f"  Experiment: {exp_id}")
            print(f"  Model A Requests: {exp_data['results']['model_a']['requests']}")
            print(f"  Model B Requests: {exp_data['results']['model_b']['requests']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test
        asyncio.run(test_model_serving())
    else:
        # Run server
        app = create_app()
        print("🚀 Starting Model Serving Pipeline")
        print("📊 Metrics available at: http://localhost:8000/metrics")
        print("🏥 Health check at: http://localhost:8000/health")
        print("🧪 Experiments at: http://localhost:8000/experiments")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            workers=4,  # Production workers
            access_log=True
        )