#!/usr/bin/env python3
"""
Edge ML Inference Engine - एज पर मशीन लर्निंग इन्फरेंस
Mumbai traffic policeman की तरह - on-spot decision making without calling headquarters

Real-world inspired by Tesla's Autopilot, Google's Coral Edge TPU
Use cases: Real-time fraud detection, traffic analysis, medical diagnostics
Cost: Edge inference ₹0.001 per prediction vs Cloud ₹0.1 per API call
"""

import time
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from datetime import datetime, timedelta
from collections import deque, defaultdict
import pickle
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Different types of ML models for edge deployment"""
    FRAUD_DETECTION = "फ्रॉड डिटेक्शन"         # Payment fraud detection
    TRAFFIC_ANALYSIS = "ट्रैफिक एनालिसिस"      # Traffic pattern recognition
    FACE_RECOGNITION = "फेस रिकग्निशन"        # Security/access control
    ANOMALY_DETECTION = "एनोमली डिटेक्शन"     # System anomaly detection
    RECOMMENDATION = "रेकमेंडेशन"             # Content/product recommendations
    PREDICTIVE_MAINTENANCE = "प्रेडिक्टिव मेंटेनेंस"  # Equipment failure prediction

class InferenceMode(Enum):
    """Different inference execution modes"""
    REALTIME = "रियल-टाइम"        # <10ms response time
    BATCH = "बैच"                 # Process multiple requests together
    STREAMING = "स्ट्रीमिंग"        # Continuous data processing
    ON_DEMAND = "ऑन-डिमांड"       # Process when requested

@dataclass
class MLModel:
    """ML Model metadata and configuration"""
    model_id: str
    model_type: ModelType
    version: str
    model_size_mb: float
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    precision: str  # float32, float16, int8
    framework: str  # tensorflow, pytorch, onnx
    created_at: datetime
    accuracy: float
    latency_target_ms: float
    memory_requirement_mb: float
    
    def __post_init__(self):
        # Generate model hash for integrity checking
        self.model_hash = hashlib.md5(f"{self.model_id}_{self.version}".encode()).hexdigest()[:8]

@dataclass
class InferenceRequest:
    """Single inference request"""
    request_id: str
    model_id: str
    input_data: Any
    timestamp: datetime
    priority: int = 1  # 1=low, 2=medium, 3=high
    timeout_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class InferenceResult:
    """Inference result with performance metrics"""
    request_id: str
    model_id: str
    prediction: Any
    confidence: float
    processing_time_ms: float
    memory_used_mb: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class EdgeMLInferenceEngine:
    """
    Edge ML Inference Engine - Mumbai local train driver की तरह
    On-the-spot decisions without waiting for central control
    """
    
    def __init__(self, device_id: str, location: str = "Mumbai", max_memory_gb: float = 4.0):
        """
        Initialize Edge ML Inference Engine
        Args:
            device_id: Unique device identifier
            location: Geographic location
            max_memory_gb: Maximum memory available for models
        """
        self.device_id = device_id
        self.location = location
        self.max_memory_gb = max_memory_gb
        
        # Model management
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        self.model_registry: Dict[str, MLModel] = {}
        self.model_cache = {}
        self.current_memory_usage_gb = 0.0
        
        # Request processing
        self.request_queue = deque()
        self.batch_queue = defaultdict(list)
        self.processing_threads = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance monitoring
        self.stats = {
            'total_requests': 0,
            'successful_inferences': 0,
            'failed_inferences': 0,
            'total_processing_time_ms': 0,
            'model_usage_count': defaultdict(int),
            'inference_times': defaultdict(list),
            'memory_usage_history': deque(maxlen=1000),
            'throughput_history': deque(maxlen=100),
            'error_counts': defaultdict(int),
            'start_time': datetime.now()
        }
        
        # Mumbai-specific model configurations
        self.mumbai_models = self._initialize_mumbai_models()
        
        # Performance thresholds
        self.performance_thresholds = {
            ModelType.FRAUD_DETECTION: {'max_latency_ms': 100, 'min_accuracy': 0.95},
            ModelType.TRAFFIC_ANALYSIS: {'max_latency_ms': 500, 'min_accuracy': 0.85},
            ModelType.FACE_RECOGNITION: {'max_latency_ms': 200, 'min_accuracy': 0.98},
            ModelType.ANOMALY_DETECTION: {'max_latency_ms': 1000, 'min_accuracy': 0.90},
            ModelType.RECOMMENDATION: {'max_latency_ms': 300, 'min_accuracy': 0.75},
            ModelType.PREDICTIVE_MAINTENANCE: {'max_latency_ms': 2000, 'min_accuracy': 0.92}
        }
        
        self.running = False
        self.processing_thread = None
        
        logger.info(f"Edge ML Inference Engine initialized: {device_id} @ {location}")
    
    def _initialize_mumbai_models(self) -> List[MLModel]:
        """Initialize Mumbai-specific ML models"""
        models = [
            MLModel(
                model_id="paytm_fraud_detector_v2",
                model_type=ModelType.FRAUD_DETECTION,
                version="2.1.0",
                model_size_mb=15.5,
                input_shape=(20,),  # 20 transaction features
                output_shape=(2,),  # fraud/legitimate
                precision="float32",
                framework="tensorflow",
                created_at=datetime.now() - timedelta(days=30),
                accuracy=0.967,
                latency_target_ms=50,
                memory_requirement_mb=128
            ),
            MLModel(
                model_id="mumbai_traffic_analyzer",
                model_type=ModelType.TRAFFIC_ANALYSIS,
                version="1.8.3",
                model_size_mb=45.2,
                input_shape=(224, 224, 3),  # Camera image input
                output_shape=(10,),  # Traffic density classes
                precision="float16",
                framework="pytorch",
                created_at=datetime.now() - timedelta(days=15),
                accuracy=0.892,
                latency_target_ms=200,
                memory_requirement_mb=256
            ),
            MLModel(
                model_id="ola_demand_predictor",
                model_type=ModelType.RECOMMENDATION,
                version="3.2.1",
                model_size_mb=8.7,
                input_shape=(15,),  # Location, time, weather features
                output_shape=(1,),  # Demand score
                precision="float32",
                framework="onnx",
                created_at=datetime.now() - timedelta(days=5),
                accuracy=0.823,
                latency_target_ms=100,
                memory_requirement_mb=64
            ),
            MLModel(
                model_id="mumbai_security_face_rec",
                model_type=ModelType.FACE_RECOGNITION,
                version="4.1.0", 
                model_size_mb=125.3,
                input_shape=(160, 160, 3),  # Face image
                output_shape=(512,),  # Face embedding
                precision="float16",
                framework="tensorflow",
                created_at=datetime.now() - timedelta(days=2),
                accuracy=0.985,
                latency_target_ms=150,
                memory_requirement_mb=512
            ),
            MLModel(
                model_id="bmc_equipment_monitor",
                model_type=ModelType.PREDICTIVE_MAINTENANCE,
                version="2.0.5",
                model_size_mb=22.1,
                input_shape=(50,),  # Sensor readings over time
                output_shape=(3,),  # Normal/Warning/Critical
                precision="float32",
                framework="pytorch",
                created_at=datetime.now() - timedelta(days=10),
                accuracy=0.934,
                latency_target_ms=500,
                memory_requirement_mb=192
            )
        ]
        
        # Register models
        for model in models:
            self.model_registry[model.model_id] = model
        
        return models
    
    def start_engine(self):
        """Start the inference engine"""
        if self.running:
            logger.warning("Engine already running")
            return
        
        self.running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True,
            name="MLInferenceProcessor"
        )
        self.processing_thread.start()
        
        logger.info("Edge ML Inference Engine started")
    
    def stop_engine(self):
        """Stop the inference engine"""
        if not self.running:
            return
        
        self.running = False
        
        # Unload all models
        self.unload_all_models()
        
        logger.info("Edge ML Inference Engine stopped")
    
    def load_model(self, model_id: str) -> bool:
        """
        Load ML model into memory
        Mumbai local train में coach जोड़ने की तरह - resource management
        """
        try:
            if model_id not in self.model_registry:
                logger.error(f"Model {model_id} not found in registry")
                return False
            
            if model_id in self.loaded_models:
                logger.info(f"Model {model_id} already loaded")
                return True
            
            model_config = self.model_registry[model_id]
            required_memory_gb = model_config.memory_requirement_mb / 1024.0
            
            # Check memory availability
            if self.current_memory_usage_gb + required_memory_gb > self.max_memory_gb:
                logger.warning(f"Insufficient memory for model {model_id}")
                
                # Try to free memory by unloading least used models
                if not self._free_memory_for_model(required_memory_gb):
                    logger.error(f"Failed to free memory for model {model_id}")
                    return False
            
            # Simulate model loading (in production, this would load actual model)
            loading_start_time = time.time()
            
            # Simulate loading delay based on model size
            loading_delay = model_config.model_size_mb / 100.0  # 100MB per second loading speed
            time.sleep(min(loading_delay, 2.0))  # Cap at 2 seconds for demo
            
            # Create mock model object (in production, this would be actual model)
            model_object = self._create_mock_model(model_config)
            
            # Store loaded model
            self.loaded_models[model_id] = {
                'model_config': model_config,
                'model_object': model_object,
                'load_time': datetime.now(),
                'usage_count': 0,
                'last_used': datetime.now(),
                'memory_usage_gb': required_memory_gb
            }
            
            self.current_memory_usage_gb += required_memory_gb
            
            loading_time = (time.time() - loading_start_time) * 1000
            logger.info(f"Model loaded: {model_id} ({loading_time:.1f}ms, {required_memory_gb:.2f}GB)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {str(e)}")
            return False
    
    def unload_model(self, model_id: str) -> bool:
        """Unload model from memory"""
        try:
            if model_id not in self.loaded_models:
                logger.warning(f"Model {model_id} not loaded")
                return False
            
            model_info = self.loaded_models[model_id]
            memory_freed = model_info['memory_usage_gb']
            
            # Remove from loaded models
            del self.loaded_models[model_id]
            self.current_memory_usage_gb -= memory_freed
            
            logger.info(f"Model unloaded: {model_id} (freed {memory_freed:.2f}GB)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_id}: {str(e)}")
            return False
    
    def unload_all_models(self):
        """Unload all models from memory"""
        for model_id in list(self.loaded_models.keys()):
            self.unload_model(model_id)
    
    def _free_memory_for_model(self, required_memory_gb: float) -> bool:
        """Free memory by unloading least recently used models"""
        try:
            # Sort models by last used time (ascending)
            sorted_models = sorted(
                self.loaded_models.items(),
                key=lambda x: x[1]['last_used']
            )
            
            freed_memory = 0.0
            models_to_unload = []
            
            for model_id, model_info in sorted_models:
                if freed_memory >= required_memory_gb:
                    break
                
                models_to_unload.append(model_id)
                freed_memory += model_info['memory_usage_gb']
            
            # Unload selected models
            for model_id in models_to_unload:
                self.unload_model(model_id)
            
            return freed_memory >= required_memory_gb
            
        except Exception as e:
            logger.error(f"Failed to free memory: {str(e)}")
            return False
    
    def _create_mock_model(self, model_config: MLModel) -> Dict[str, Any]:
        """Create mock model for simulation (in production, load actual model)"""
        return {
            'model_id': model_config.model_id,
            'model_type': model_config.model_type,
            'input_shape': model_config.input_shape,
            'output_shape': model_config.output_shape,
            'precision': model_config.precision,
            'framework': model_config.framework,
            'accuracy': model_config.accuracy
        }
    
    async def inference(self, request: InferenceRequest) -> InferenceResult:
        """
        Perform ML inference
        Mumbai traffic signal की तरह - quick decision making
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Validate request
            if request.model_id not in self.model_registry:
                raise ValueError(f"Model {request.model_id} not found")
            
            # Load model if not already loaded
            if request.model_id not in self.loaded_models:
                success = self.load_model(request.model_id)
                if not success:
                    raise RuntimeError(f"Failed to load model {request.model_id}")
            
            model_info = self.loaded_models[request.model_id]
            model_config = model_info['model_config']
            
            # Update model usage
            model_info['usage_count'] += 1
            model_info['last_used'] = datetime.now()
            self.stats['model_usage_count'][request.model_id] += 1
            
            # Simulate inference processing
            processing_start = time.time()
            prediction, confidence = await self._perform_inference(
                request, model_config, model_info['model_object']
            )
            processing_time = (time.time() - processing_start) * 1000
            
            # Calculate memory usage (simplified)
            memory_used = model_info['memory_usage_gb'] / 1024.0 * 1000  # Convert to MB
            
            # Create result
            total_time = (time.time() - start_time) * 1000
            
            result = InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                prediction=prediction,
                confidence=confidence,
                processing_time_ms=total_time,
                memory_used_mb=memory_used,
                timestamp=datetime.now(),
                success=True
            )
            
            # Update statistics
            self.stats['successful_inferences'] += 1
            self.stats['total_processing_time_ms'] += total_time
            self.stats['inference_times'][request.model_id].append(total_time)
            
            # Limit history size
            if len(self.stats['inference_times'][request.model_id]) > 1000:
                self.stats['inference_times'][request.model_id] = \
                    self.stats['inference_times'][request.model_id][-500:]
            
            logger.debug(f"Inference completed: {request.request_id} in {total_time:.2f}ms")
            return result
            
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            
            self.stats['failed_inferences'] += 1
            self.stats['error_counts'][str(e)] += 1
            
            result = InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                prediction=None,
                confidence=0.0,
                processing_time_ms=total_time,
                memory_used_mb=0.0,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"Inference failed: {request.request_id} - {str(e)}")
            return result
    
    async def _perform_inference(self, request: InferenceRequest, model_config: MLModel, 
                               model_object: Dict[str, Any]) -> Tuple[Any, float]:
        """
        Perform actual model inference
        Mumbai specific model behaviors simulation
        """
        # Simulate processing delay based on model complexity
        base_delay = model_config.latency_target_ms / 1000.0
        actual_delay = base_delay * (0.8 + np.random.random() * 0.4)  # ±20% variation
        await asyncio.sleep(actual_delay)
        
        # Generate mock predictions based on model type
        if model_config.model_type == ModelType.FRAUD_DETECTION:
            # Fraud detection: binary classification
            fraud_probability = np.random.beta(2, 8)  # Most transactions are legitimate
            prediction = {"is_fraud": fraud_probability > 0.1, "fraud_score": fraud_probability}
            confidence = 0.85 + np.random.random() * 0.10
            
        elif model_config.model_type == ModelType.TRAFFIC_ANALYSIS:
            # Traffic analysis: density classification
            traffic_classes = ["Light", "Moderate", "Heavy", "Jam", "Blocked"]
            # Mumbai traffic patterns - higher probability of congestion
            weights = [0.1, 0.2, 0.3, 0.3, 0.1]
            predicted_class = np.random.choice(traffic_classes, p=weights)
            density_score = np.random.random()
            prediction = {"traffic_density": predicted_class, "density_score": density_score}
            confidence = 0.75 + np.random.random() * 0.15
            
        elif model_config.model_type == ModelType.FACE_RECOGNITION:
            # Face recognition: identity matching
            face_id = f"person_{np.random.randint(1, 10000)}"
            match_score = np.random.beta(8, 2)  # Higher probability of good matches
            prediction = {"identity": face_id, "match_score": match_score}
            confidence = 0.90 + np.random.random() * 0.08
            
        elif model_config.model_type == ModelType.RECOMMENDATION:
            # Recommendation: demand prediction
            demand_score = np.random.gamma(2, 0.5)  # Gamma distribution for demand
            demand_score = min(demand_score, 5.0)  # Cap at 5.0
            hotspots = ["Andheri", "Bandra", "Mumbai Central", "Thane", "Navi Mumbai"]
            predicted_hotspot = np.random.choice(hotspots)
            prediction = {"demand_score": demand_score, "hotspot": predicted_hotspot}
            confidence = 0.70 + np.random.random() * 0.20
            
        elif model_config.model_type == ModelType.PREDICTIVE_MAINTENANCE:
            # Predictive maintenance: equipment health
            health_states = ["Normal", "Warning", "Critical"]
            # Most equipment is normal
            weights = [0.7, 0.25, 0.05]
            predicted_state = np.random.choice(health_states, p=weights)
            health_score = np.random.beta(8, 3)  # Biased towards healthy
            prediction = {"health_state": predicted_state, "health_score": health_score}
            confidence = 0.88 + np.random.random() * 0.10
            
        else:
            # Generic prediction
            prediction = {"result": "processed", "score": np.random.random()}
            confidence = 0.80 + np.random.random() * 0.15
        
        return prediction, confidence
    
    def _processing_loop(self):
        """Background processing loop for batch and streaming requests"""
        logger.info("Processing loop started")
        
        while self.running:
            try:
                # Update memory usage statistics
                self.stats['memory_usage_history'].append(self.current_memory_usage_gb)
                
                # Process any queued batch requests
                self._process_batch_requests()
                
                # Update throughput statistics
                current_time = datetime.now()
                recent_requests = sum(
                    1 for times in self.stats['inference_times'].values()
                    for t in times[-10:]  # Last 10 inferences per model
                )
                self.stats['throughput_history'].append(recent_requests)
                
                time.sleep(1.0)  # Run every second
                
            except Exception as e:
                logger.error(f"Processing loop error: {str(e)}")
                time.sleep(5.0)
        
        logger.info("Processing loop stopped")
    
    def _process_batch_requests(self):
        """Process batched requests for better throughput"""
        for model_id, requests in self.batch_queue.items():
            if len(requests) >= 10 or (requests and 
                (datetime.now() - requests[0].timestamp).total_seconds() > 5):
                
                # Process batch
                logger.debug(f"Processing batch of {len(requests)} requests for {model_id}")
                
                # In production, this would do actual batch inference
                # For simulation, we'll process them individually
                batch_requests = requests.copy()
                self.batch_queue[model_id].clear()
                
                for request in batch_requests:
                    try:
                        # This would typically be processed asynchronously
                        asyncio.create_task(self.inference(request))
                    except Exception as e:
                        logger.error(f"Batch processing error: {str(e)}")
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        try:
            current_time = datetime.now()
            uptime = current_time - self.stats['start_time']
            uptime_hours = uptime.total_seconds() / 3600
            
            # Calculate performance metrics
            total_requests = self.stats['total_requests']
            if total_requests > 0:
                success_rate = (self.stats['successful_inferences'] / total_requests) * 100
                avg_processing_time = self.stats['total_processing_time_ms'] / total_requests
                requests_per_hour = total_requests / uptime_hours if uptime_hours > 0 else 0
            else:
                success_rate = 0
                avg_processing_time = 0
                requests_per_hour = 0
            
            # Model performance metrics
            model_performance = {}
            for model_id in self.loaded_models.keys():
                inference_times = self.stats['inference_times'][model_id]
                if inference_times:
                    model_performance[model_id] = {
                        'avg_latency_ms': statistics.mean(inference_times),
                        'p95_latency_ms': np.percentile(inference_times, 95),
                        'p99_latency_ms': np.percentile(inference_times, 99),
                        'usage_count': self.stats['model_usage_count'][model_id],
                        'meets_sla': statistics.mean(inference_times) <= 
                                   self.model_registry[model_id].latency_target_ms
                    }
            
            # Memory statistics
            memory_stats = {
                'current_usage_gb': round(self.current_memory_usage_gb, 3),
                'max_available_gb': self.max_memory_gb,
                'utilization_percent': round((self.current_memory_usage_gb / self.max_memory_gb) * 100, 2),
                'loaded_models_count': len(self.loaded_models),
                'avg_memory_usage_gb': round(
                    statistics.mean(self.stats['memory_usage_history']) 
                    if self.stats['memory_usage_history'] else 0, 3
                )
            }
            
            return {
                "engine_info": {
                    "device_id": self.device_id,
                    "location": self.location,
                    "uptime_hours": round(uptime_hours, 2),
                    "status": "running" if self.running else "stopped"
                },
                "performance_stats": {
                    "total_requests": total_requests,
                    "successful_inferences": self.stats['successful_inferences'],
                    "failed_inferences": self.stats['failed_inferences'],
                    "success_rate_percent": round(success_rate, 2),
                    "avg_processing_time_ms": round(avg_processing_time, 2),
                    "requests_per_hour": round(requests_per_hour, 1)
                },
                "memory_stats": memory_stats,
                "model_performance": model_performance,
                "model_registry": {
                    "total_models": len(self.model_registry),
                    "loaded_models": len(self.loaded_models),
                    "available_models": list(self.model_registry.keys())
                },
                "error_summary": dict(self.stats['error_counts']) if self.stats['error_counts'] else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get engine stats: {str(e)}")
            return {"error": str(e)}
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about specific model"""
        try:
            if model_id not in self.model_registry:
                return None
            
            model_config = self.model_registry[model_id]
            is_loaded = model_id in self.loaded_models
            
            model_info = {
                "model_id": model_config.model_id,
                "model_type": model_config.model_type.value,
                "version": model_config.version,
                "framework": model_config.framework,
                "model_size_mb": model_config.model_size_mb,
                "accuracy": model_config.accuracy,
                "latency_target_ms": model_config.latency_target_ms,
                "memory_requirement_mb": model_config.memory_requirement_mb,
                "is_loaded": is_loaded,
                "usage_count": self.stats['model_usage_count'][model_id]
            }
            
            # Add runtime information if model is loaded
            if is_loaded:
                loaded_info = self.loaded_models[model_id]
                model_info.update({
                    "load_time": loaded_info['load_time'].isoformat(),
                    "last_used": loaded_info['last_used'].isoformat(),
                    "memory_usage_gb": loaded_info['memory_usage_gb']
                })
                
                # Add performance metrics if available
                inference_times = self.stats['inference_times'][model_id]
                if inference_times:
                    model_info.update({
                        "avg_inference_time_ms": round(statistics.mean(inference_times), 2),
                        "min_inference_time_ms": round(min(inference_times), 2),
                        "max_inference_time_ms": round(max(inference_times), 2)
                    })
            
            return model_info
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {str(e)}")
            return None

# Example usage and comprehensive testing
async def main():
    """
    Comprehensive Edge ML Inference testing
    Mumbai AI applications demonstration
    """
    print("🧠 Edge ML Inference Engine - Mumbai AI Applications")
    print("=" * 60)
    
    # Initialize inference engine
    engine = EdgeMLInferenceEngine("mumbai-edge-ml-01", "Mumbai Central", max_memory_gb=8.0)
    engine.start_engine()
    
    print(f"✅ ML Inference Engine started: {engine.device_id}")
    print(f"📊 Available Models: {len(engine.model_registry)}")
    print(f"💾 Memory Limit: {engine.max_memory_gb}GB")
    
    # Display available models
    print(f"\n📚 Available Mumbai AI Models:")
    print("-" * 40)
    
    for model_id, model_config in engine.model_registry.items():
        print(f"• {model_id}")
        print(f"  Type: {model_config.model_type.value}")
        print(f"  Size: {model_config.model_size_mb}MB")
        print(f"  Target Latency: {model_config.latency_target_ms}ms")
        print(f"  Accuracy: {model_config.accuracy:.1%}")
        print()
    
    # Test individual model loading and inference
    print(f"🔄 Testing Individual Model Operations...")
    
    # Load fraud detection model
    fraud_model_id = "paytm_fraud_detector_v2"
    success = engine.load_model(fraud_model_id)
    print(f"Loading {fraud_model_id}: {'✅' if success else '❌'}")
    
    # Test fraud detection inference
    fraud_request = InferenceRequest(
        request_id="fraud_test_001",
        model_id=fraud_model_id,
        input_data={
            "amount": 15000,
            "merchant": "electronics_store",
            "location": "Mumbai",
            "time_of_day": "evening",
            "card_present": False,
            "customer_age": 28,
            "previous_transactions_today": 3
        },
        timestamp=datetime.now(),
        priority=3  # High priority for fraud detection
    )
    
    fraud_result = await engine.inference(fraud_request)
    
    print(f"\n🔍 Fraud Detection Test:")
    print(f"Request ID: {fraud_result.request_id}")
    print(f"Success: {'✅' if fraud_result.success else '❌'}")
    print(f"Processing Time: {fraud_result.processing_time_ms:.2f}ms")
    print(f"Prediction: {fraud_result.prediction}")
    print(f"Confidence: {fraud_result.confidence:.2%}")
    
    # Load traffic analysis model
    traffic_model_id = "mumbai_traffic_analyzer"
    success = engine.load_model(traffic_model_id)
    print(f"\nLoading {traffic_model_id}: {'✅' if success else '❌'}")
    
    # Test traffic analysis
    traffic_request = InferenceRequest(
        request_id="traffic_test_001",
        model_id=traffic_model_id,
        input_data={
            "location": "Western Express Highway",
            "time": "08:30",
            "day_of_week": "Monday",
            "weather": "Clear",
            "events": ["Office rush hour"]
        },
        timestamp=datetime.now()
    )
    
    traffic_result = await engine.inference(traffic_request)
    
    print(f"\n🚗 Traffic Analysis Test:")
    print(f"Success: {'✅' if traffic_result.success else '❌'}")
    print(f"Processing Time: {traffic_result.processing_time_ms:.2f}ms")
    print(f"Prediction: {traffic_result.prediction}")
    print(f"Confidence: {traffic_result.confidence:.2%}")
    
    # Load multiple models and test memory management
    print(f"\n🧮 Testing Memory Management...")
    
    models_to_load = [
        "ola_demand_predictor",
        "mumbai_security_face_rec",
        "bmc_equipment_monitor"
    ]
    
    for model_id in models_to_load:
        success = engine.load_model(model_id)
        current_memory = engine.current_memory_usage_gb
        print(f"Loading {model_id}: {'✅' if success else '❌'} "
              f"(Memory: {current_memory:.2f}GB)")
    
    # Test batch inference performance
    print(f"\n⚡ Testing Batch Inference Performance...")
    
    batch_requests = []
    for i in range(20):
        # Mix of different model requests
        model_ids = list(engine.loaded_models.keys())
        if model_ids:
            model_id = np.random.choice(model_ids)
            
            request = InferenceRequest(
                request_id=f"batch_test_{i:03d}",
                model_id=model_id,
                input_data={"test_data": f"batch_input_{i}"},
                timestamp=datetime.now()
            )
            batch_requests.append(request)
    
    # Execute batch requests
    batch_start_time = time.time()
    batch_results = await asyncio.gather(*[
        engine.inference(request) for request in batch_requests
    ])
    batch_total_time = (time.time() - batch_start_time) * 1000
    
    successful_batch = sum(1 for result in batch_results if result.success)
    avg_batch_latency = statistics.mean([r.processing_time_ms for r in batch_results if r.success])
    
    print(f"Batch Results:")
    print(f"• Total Requests: {len(batch_requests)}")
    print(f"• Successful: {successful_batch}")
    print(f"• Total Time: {batch_total_time:.1f}ms")
    print(f"• Average Latency: {avg_batch_latency:.2f}ms")
    print(f"• Throughput: {len(batch_requests) / (batch_total_time/1000):.1f} req/sec")
    
    # Get comprehensive statistics
    print(f"\n📊 Engine Performance Report:")
    print("=" * 45)
    
    stats = engine.get_engine_stats()
    
    # Engine info
    engine_info = stats["engine_info"]
    print(f"Device: {engine_info['device_id']} @ {engine_info['location']}")
    print(f"Uptime: {engine_info['uptime_hours']} hours")
    print(f"Status: {engine_info['status']}")
    
    # Performance stats
    perf_stats = stats["performance_stats"]
    print(f"\n⚡ Performance:")
    print(f"• Total Requests: {perf_stats['total_requests']}")
    print(f"• Success Rate: {perf_stats['success_rate_percent']}%")
    print(f"• Average Processing Time: {perf_stats['avg_processing_time_ms']:.2f}ms")
    print(f"• Throughput: {perf_stats['requests_per_hour']:.1f} req/hour")
    
    # Memory stats  
    memory_stats = stats["memory_stats"]
    print(f"\n💾 Memory Usage:")
    print(f"• Current Usage: {memory_stats['current_usage_gb']}GB")
    print(f"• Utilization: {memory_stats['utilization_percent']}%")
    print(f"• Loaded Models: {memory_stats['loaded_models_count']}")
    
    # Model performance
    model_performance = stats["model_performance"]
    if model_performance:
        print(f"\n🎯 Model Performance:")
        for model_id, metrics in model_performance.items():
            sla_status = "✅" if metrics['meets_sla'] else "⚠️"
            print(f"• {model_id}: {sla_status}")
            print(f"  Average Latency: {metrics['avg_latency_ms']:.2f}ms")
            print(f"  P95 Latency: {metrics['p95_latency_ms']:.2f}ms")
            print(f"  Usage Count: {metrics['usage_count']}")
    
    # Cost analysis
    print(f"\n💰 Cost Analysis:")
    print("-" * 20)
    
    total_inferences = perf_stats['total_requests']
    edge_cost = total_inferences * 0.001  # ₹0.001 per edge inference
    cloud_cost = total_inferences * 0.1   # ₹0.1 per cloud API call
    savings = cloud_cost - edge_cost
    
    print(f"Edge ML Cost: ₹{edge_cost:.3f}")
    print(f"Cloud API Cost: ₹{cloud_cost:.2f}")
    print(f"Cost Savings: ₹{savings:.2f}")
    print(f"Savings Percentage: {(savings/cloud_cost)*100:.1f}%")
    
    # Scale to daily estimates
    if perf_stats['requests_per_hour'] > 0:
        daily_requests = perf_stats['requests_per_hour'] * 24
        daily_savings = savings * (daily_requests / total_inferences)
        
        print(f"\n📈 Daily Projections:")
        print(f"Estimated Daily Requests: {daily_requests:,.0f}")
        print(f"Estimated Daily Savings: ₹{daily_savings:,.2f}")
        print(f"Monthly Savings: ₹{daily_savings * 30:,.2f}")
    
    # Business impact
    print(f"\n🎯 Business Impact:")
    print("• 99% cost reduction compared to cloud APIs")
    print("• Sub-100ms inference for critical applications")
    print("• Zero network dependency for predictions")
    print("• Enhanced privacy with local processing")
    print("• Improved user experience with low latency")
    
    # Model-specific insights
    print(f"\n🔍 Mumbai AI Applications Insights:")
    print("• Fraud Detection: Real-time payment security")
    print("• Traffic Analysis: Smart city traffic optimization") 
    print("• Face Recognition: Enhanced security systems")
    print("• Demand Prediction: Optimized ride-sharing")
    print("• Predictive Maintenance: Proactive infrastructure care")
    
    # Clean up
    print(f"\n🛑 Stopping inference engine...")
    engine.stop_engine()
    
    print(f"\n✅ Edge ML Inference demonstration completed!")
    print(f"🧠 Mumbai AI applications optimized for edge deployment!")

if __name__ == "__main__":
    asyncio.run(main())