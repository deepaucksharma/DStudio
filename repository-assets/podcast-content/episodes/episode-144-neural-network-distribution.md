# Episode 144: Neural Network Distribution - AI & ML Systems in Distributed Computing

## Abstract

The deployment of neural networks at scale requires sophisticated distributed inference architectures that can handle millions of concurrent requests while maintaining low latency and high availability. Modern AI applications, from autonomous vehicles to voice assistants, rely on distributed neural network systems that span edge devices, data centers, and cloud infrastructure. This episode explores the distributed systems principles underlying neural network deployment, examining model sharding techniques, pipeline parallelism for inference, and edge AI deployment patterns.

Through detailed analysis of production systems like Tesla's Full Self-Driving (FSD) infrastructure, Amazon Alexa's distributed speech processing, and Google Assistant's multi-tier architecture, we'll understand how large-scale neural network distribution balances computational efficiency, network bandwidth, latency requirements, and energy constraints across heterogeneous distributed environments.

## Table of Contents

1. Distributed Neural Network Inference Fundamentals
2. Model Sharding and Partitioning Strategies
3. Pipeline Parallelism for Neural Network Inference
4. Edge AI and Distributed Computing Hierarchies
5. Load Balancing and Request Routing for AI Services
6. Caching and Optimization in Distributed Inference
7. Multi-Tier Neural Network Architectures
8. Production System Analysis: Tesla, Alexa, Google Assistant
9. Resource Management and Auto-Scaling for AI Workloads
10. Fault Tolerance and High Availability in AI Systems
11. Future Directions in Distributed Neural Networks

## 1. Distributed Neural Network Inference Fundamentals

Distributed neural network inference presents unique challenges compared to traditional distributed systems: irregular computation patterns, varying model sizes, heterogeneous hardware requirements, and stringent latency constraints.

### Theoretical Framework for Distributed Inference

Consider a neural network f(x) = f_L ∘ f_{L-1} ∘ ... ∘ f_1(x) with L layers. In distributed inference, we must decide:

1. **Spatial Distribution**: Which layers execute on which devices
2. **Temporal Distribution**: How to pipeline computations across time
3. **Data Distribution**: How to batch and route inference requests

The optimal distribution minimizes total latency:

```
T_total = max_i(T_compute_i + T_comm_i) + T_routing + T_aggregation
```

where:
- T_compute_i: Computation time on device i
- T_comm_i: Communication time for device i
- T_routing: Request routing latency
- T_aggregation: Result aggregation time

### Distributed Inference Architecture

```python
import asyncio
import time
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import grpc
import redis
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import networkx as nx

@dataclass
class InferenceRequest:
    """Request for distributed neural network inference"""
    request_id: str
    input_data: torch.Tensor
    model_id: str
    priority: int = 5  # 1-10, higher is more urgent
    timeout_ms: int = 1000
    routing_hints: Dict[str, Any] = None
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.routing_hints is None:
            self.routing_hints = {}

@dataclass
class InferenceResult:
    """Result from distributed neural network inference"""
    request_id: str
    output: torch.Tensor
    latency_ms: float
    compute_path: List[str]  # Devices used for computation
    cache_hit: bool = False
    error: Optional[str] = None

class DistributedInferenceEngine:
    """
    Core engine for distributed neural network inference
    with advanced routing, caching, and optimization
    """
    
    def __init__(self, cluster_config: Dict[str, Any]):
        self.cluster_config = cluster_config
        self.device_pool = DevicePool(cluster_config['devices'])
        self.model_registry = ModelRegistry()
        self.request_router = InferenceRouter(self.device_pool)
        self.cache_manager = InferenceCache()
        
        # Performance monitoring
        self.metrics = InferenceMetrics()
        
        # Load balancing
        self.load_balancer = LoadBalancer(self.device_pool)
        
        # Request queue management
        self.request_queues = {
            priority: asyncio.Queue() 
            for priority in range(1, 11)
        }
        
        # Worker pools for different priority levels
        self.worker_pools = {}
        for priority in range(1, 11):
            pool_size = self._calculate_pool_size(priority)
            self.worker_pools[priority] = ThreadPoolExecutor(max_workers=pool_size)
        
        self.logger = logging.getLogger(__name__)
        self.running = False
    
    async def start(self):
        """Start the distributed inference engine"""
        self.running = True
        
        # Start request processors for each priority level
        processors = []
        for priority in range(1, 11):
            processor = asyncio.create_task(
                self._process_requests(priority)
            )
            processors.append(processor)
        
        # Start background tasks
        background_tasks = [
            asyncio.create_task(self._update_device_status()),
            asyncio.create_task(self._optimize_placement()),
            asyncio.create_task(self._collect_metrics())
        ]
        
        try:
            await asyncio.gather(*processors, *background_tasks)
        except Exception as e:
            self.logger.error(f"Error in inference engine: {e}")
            self.running = False
    
    async def infer(self, request: InferenceRequest) -> InferenceResult:
        """Submit inference request and get result"""
        
        start_time = time.time()
        
        try:
            # Check cache first
            cached_result = await self.cache_manager.get(request)
            if cached_result:
                cached_result.latency_ms = (time.time() - start_time) * 1000
                cached_result.cache_hit = True
                return cached_result
            
            # Route request to appropriate device(s)
            execution_plan = await self.request_router.route(request)
            
            # Execute inference
            result = await self._execute_inference(request, execution_plan)
            
            # Cache result if beneficial
            await self.cache_manager.put(request, result)
            
            # Update metrics
            result.latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_request(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Inference failed for request {request.request_id}: {e}")
            return InferenceResult(
                request_id=request.request_id,
                output=torch.tensor([]),
                latency_ms=(time.time() - start_time) * 1000,
                compute_path=[],
                error=str(e)
            )
    
    async def _execute_inference(self, request: InferenceRequest, 
                               execution_plan: 'ExecutionPlan') -> InferenceResult:
        """Execute inference according to execution plan"""
        
        if execution_plan.execution_type == 'single_device':
            return await self._single_device_inference(request, execution_plan)
        elif execution_plan.execution_type == 'model_parallel':
            return await self._model_parallel_inference(request, execution_plan)
        elif execution_plan.execution_type == 'pipeline':
            return await self._pipeline_inference(request, execution_plan)
        else:
            raise ValueError(f"Unknown execution type: {execution_plan.execution_type}")
    
    async def _single_device_inference(self, request: InferenceRequest,
                                     execution_plan: 'ExecutionPlan') -> InferenceResult:
        """Execute inference on a single device"""
        
        device_id = execution_plan.device_assignments[0]
        device = self.device_pool.get_device(device_id)
        
        if not device.is_available():
            raise RuntimeError(f"Device {device_id} is not available")
        
        # Load model if not already loaded
        model = await self.model_registry.get_model(
            request.model_id, device_id
        )
        
        # Execute inference
        start_time = time.time()
        
        async with device.acquire():
            with torch.no_grad():
                device_input = request.input_data.to(device.torch_device)
                output = model(device_input)
                output = output.cpu()
        
        compute_time = (time.time() - start_time) * 1000
        
        return InferenceResult(
            request_id=request.request_id,
            output=output,
            latency_ms=compute_time,
            compute_path=[device_id]
        )
    
    async def _model_parallel_inference(self, request: InferenceRequest,
                                      execution_plan: 'ExecutionPlan') -> InferenceResult:
        """Execute inference with model parallelism across multiple devices"""
        
        device_assignments = execution_plan.device_assignments
        layer_assignments = execution_plan.layer_assignments
        
        # Get model shards
        model_shards = {}
        for device_id in device_assignments:
            layers = layer_assignments[device_id]
            model_shard = await self.model_registry.get_model_shard(
                request.model_id, device_id, layers
            )
            model_shards[device_id] = model_shard
        
        # Execute model parallel inference
        current_data = request.input_data
        compute_path = []
        
        start_time = time.time()
        
        for device_id in execution_plan.execution_order:
            device = self.device_pool.get_device(device_id)
            model_shard = model_shards[device_id]
            
            async with device.acquire():
                with torch.no_grad():
                    device_input = current_data.to(device.torch_device)
                    current_data = model_shard(device_input).cpu()
            
            compute_path.append(device_id)
        
        compute_time = (time.time() - start_time) * 1000
        
        return InferenceResult(
            request_id=request.request_id,
            output=current_data,
            latency_ms=compute_time,
            compute_path=compute_path
        )
    
    async def _pipeline_inference(self, request: InferenceRequest,
                                execution_plan: 'ExecutionPlan') -> InferenceResult:
        """Execute inference with pipeline parallelism"""
        
        pipeline_stages = execution_plan.pipeline_stages
        
        # Create pipeline execution tasks
        pipeline_queues = {}
        for i in range(len(pipeline_stages)):
            pipeline_queues[i] = asyncio.Queue(maxsize=1)
        
        # Start pipeline stages
        stage_tasks = []
        for i, stage in enumerate(pipeline_stages):
            task = asyncio.create_task(
                self._execute_pipeline_stage(
                    stage, 
                    pipeline_queues.get(i-1),
                    pipeline_queues.get(i),
                    i == 0,
                    i == len(pipeline_stages) - 1
                )
            )
            stage_tasks.append(task)
        
        start_time = time.time()
        
        # Send initial input
        if 0 in pipeline_queues:
            await pipeline_queues[0].put((request.request_id, request.input_data))
        
        # Wait for final output
        final_stage_idx = len(pipeline_stages) - 1
        if final_stage_idx in pipeline_queues:
            result_id, output = await pipeline_queues[final_stage_idx].get()
        else:
            output = torch.tensor([])
        
        # Clean up pipeline tasks
        for task in stage_tasks:
            task.cancel()
        
        compute_time = (time.time() - start_time) * 1000
        
        return InferenceResult(
            request_id=request.request_id,
            output=output,
            latency_ms=compute_time,
            compute_path=[stage.device_id for stage in pipeline_stages]
        )
    
    def _calculate_pool_size(self, priority: int) -> int:
        """Calculate thread pool size based on priority"""
        # Higher priority requests get more workers
        base_size = 10
        priority_multiplier = (priority / 5.0)
        return max(1, int(base_size * priority_multiplier))

@dataclass
class ExecutionPlan:
    """Plan for executing distributed inference"""
    execution_type: str  # 'single_device', 'model_parallel', 'pipeline'
    device_assignments: List[str]
    layer_assignments: Dict[str, List[int]] = None
    execution_order: List[str] = None
    pipeline_stages: List['PipelineStage'] = None
    estimated_latency_ms: float = 0.0
    estimated_energy_cost: float = 0.0

@dataclass
class PipelineStage:
    """Single stage in pipeline execution"""
    stage_id: int
    device_id: str
    model_layers: List[int]
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    estimated_compute_time_ms: float

class DevicePool:
    """Manages pool of available compute devices"""
    
    def __init__(self, device_configs: List[Dict]):
        self.devices = {}
        
        for config in device_configs:
            device = ComputeDevice(
                device_id=config['id'],
                device_type=config['type'],
                memory_gb=config['memory_gb'],
                compute_capability=config['compute_capability'],
                network_bandwidth_gbps=config.get('network_bandwidth_gbps', 1.0),
                energy_efficiency=config.get('energy_efficiency', 1.0)
            )
            self.devices[config['id']] = device
    
    def get_device(self, device_id: str) -> 'ComputeDevice':
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_available_devices(self) -> List['ComputeDevice']:
        """Get list of available devices"""
        return [device for device in self.devices.values() 
                if device.is_available()]
    
    def get_devices_by_type(self, device_type: str) -> List['ComputeDevice']:
        """Get devices of specific type"""
        return [device for device in self.devices.values()
                if device.device_type == device_type]

class ComputeDevice:
    """Represents a compute device in the distributed system"""
    
    def __init__(self, device_id: str, device_type: str, memory_gb: float,
                 compute_capability: float, network_bandwidth_gbps: float = 1.0,
                 energy_efficiency: float = 1.0):
        self.device_id = device_id
        self.device_type = device_type  # 'gpu', 'cpu', 'tpu', 'edge'
        self.memory_gb = memory_gb
        self.compute_capability = compute_capability
        self.network_bandwidth_gbps = network_bandwidth_gbps
        self.energy_efficiency = energy_efficiency
        
        # Runtime state
        self.current_load = 0.0  # 0.0 to 1.0
        self.memory_used_gb = 0.0
        self.temperature = 25.0  # Celsius
        self.is_healthy = True
        
        # Concurrency control
        self._semaphore = asyncio.Semaphore(1)
        
        # Set up torch device
        if device_type == 'gpu' and torch.cuda.is_available():
            gpu_id = int(device_id.split('-')[-1]) if '-' in device_id else 0
            self.torch_device = torch.device(f'cuda:{gpu_id}')
        else:
            self.torch_device = torch.device('cpu')
    
    async def acquire(self):
        """Acquire device for exclusive use"""
        return self._semaphore
    
    def is_available(self) -> bool:
        """Check if device is available for inference"""
        return (self.is_healthy and 
                self.current_load < 0.9 and 
                self.memory_used_gb < self.memory_gb * 0.9 and
                self.temperature < 80.0)
    
    def get_utilization_metrics(self) -> Dict[str, float]:
        """Get current device utilization metrics"""
        return {
            'load': self.current_load,
            'memory_utilization': self.memory_used_gb / self.memory_gb,
            'temperature': self.temperature,
            'health_score': 1.0 if self.is_healthy else 0.0
        }
    
    def estimate_inference_time(self, model_complexity: float, 
                              input_size: int) -> float:
        """Estimate inference time for given model and input"""
        
        # Base computation time
        base_time_ms = model_complexity / self.compute_capability
        
        # Adjust for current load
        load_factor = 1.0 + self.current_load
        
        # Adjust for memory pressure
        memory_factor = 1.0 + max(0, (self.memory_used_gb / self.memory_gb) - 0.7) * 2
        
        # Adjust for input size
        size_factor = np.sqrt(input_size / 1000.0)  # Baseline: 1k elements
        
        return base_time_ms * load_factor * memory_factor * size_factor

class InferenceRouter:
    """Routes inference requests to optimal device configurations"""
    
    def __init__(self, device_pool: DevicePool):
        self.device_pool = device_pool
        self.routing_algorithms = {
            'greedy': self._greedy_routing,
            'optimal': self._optimal_routing,
            'load_aware': self._load_aware_routing,
            'energy_aware': self._energy_aware_routing
        }
        
        # Routing statistics
        self.routing_stats = {
            'total_requests': 0,
            'algorithm_usage': {},
            'average_latency': 0.0
        }
    
    async def route(self, request: InferenceRequest) -> ExecutionPlan:
        """Route request to optimal execution configuration"""
        
        self.routing_stats['total_requests'] += 1
        
        # Determine routing algorithm based on request hints and system state
        algorithm = self._select_routing_algorithm(request)
        
        # Get execution plan
        execution_plan = await self.routing_algorithms[algorithm](request)
        
        # Update statistics
        self.routing_stats['algorithm_usage'][algorithm] = (
            self.routing_stats['algorithm_usage'].get(algorithm, 0) + 1
        )
        
        return execution_plan
    
    def _select_routing_algorithm(self, request: InferenceRequest) -> str:
        """Select appropriate routing algorithm for request"""
        
        routing_hints = request.routing_hints
        
        # High priority requests use optimal routing
        if request.priority >= 8:
            return 'optimal'
        
        # Energy-constrained environments
        if routing_hints.get('energy_budget'):
            return 'energy_aware'
        
        # High load situations use load-aware routing
        avg_load = np.mean([device.current_load 
                           for device in self.device_pool.get_available_devices()])
        if avg_load > 0.7:
            return 'load_aware'
        
        # Default to greedy for low-priority requests
        return 'greedy'
    
    async def _greedy_routing(self, request: InferenceRequest) -> ExecutionPlan:
        """Greedy routing: choose fastest single device"""
        
        available_devices = self.device_pool.get_available_devices()
        
        if not available_devices:
            raise RuntimeError("No available devices for inference")
        
        # Estimate inference time on each device
        best_device = None
        best_time = float('inf')
        
        # Rough model complexity estimate (in practice, get from model registry)
        model_complexity = 1000.0  # FLOPS estimate
        input_size = request.input_data.numel()
        
        for device in available_devices:
            estimated_time = device.estimate_inference_time(model_complexity, input_size)
            if estimated_time < best_time:
                best_time = estimated_time
                best_device = device
        
        return ExecutionPlan(
            execution_type='single_device',
            device_assignments=[best_device.device_id],
            estimated_latency_ms=best_time
        )
    
    async def _optimal_routing(self, request: InferenceRequest) -> ExecutionPlan:
        """Optimal routing using dynamic programming"""
        
        available_devices = self.device_pool.get_available_devices()
        
        if not available_devices:
            raise RuntimeError("No available devices for inference")
        
        # Get model information
        model_layers = 50  # In practice, get from model registry
        model_complexity_per_layer = 20.0  # FLOPS per layer
        input_size = request.input_data.numel()
        
        # Try different execution strategies
        strategies = []
        
        # Single device strategy
        single_device_plan = await self._greedy_routing(request)
        strategies.append(single_device_plan)
        
        # Model parallel strategy (if multiple devices available)
        if len(available_devices) >= 2:
            model_parallel_plan = self._plan_model_parallel(
                available_devices, model_layers, model_complexity_per_layer, input_size
            )
            strategies.append(model_parallel_plan)
        
        # Pipeline strategy (if multiple devices available)
        if len(available_devices) >= 3:
            pipeline_plan = self._plan_pipeline(
                available_devices, model_layers, model_complexity_per_layer, input_size
            )
            strategies.append(pipeline_plan)
        
        # Choose strategy with minimum estimated latency
        best_strategy = min(strategies, key=lambda x: x.estimated_latency_ms)
        
        return best_strategy
    
    def _plan_model_parallel(self, devices: List[ComputeDevice], 
                           model_layers: int, complexity_per_layer: float,
                           input_size: int) -> ExecutionPlan:
        """Plan model parallel execution"""
        
        # Distribute layers across devices based on compute capability
        total_capability = sum(device.compute_capability for device in devices)
        
        layer_assignments = {}
        execution_order = []
        current_layer = 0
        
        for device in devices:
            # Assign layers proportional to compute capability
            device_share = device.compute_capability / total_capability
            layers_for_device = max(1, int(model_layers * device_share))
            
            assigned_layers = list(range(current_layer, 
                                       min(current_layer + layers_for_device, model_layers)))
            layer_assignments[device.device_id] = assigned_layers
            execution_order.append(device.device_id)
            
            current_layer += layers_for_device
            
            if current_layer >= model_layers:
                break
        
        # Estimate total latency (sequential execution + communication)
        total_latency = 0.0
        
        for device_id in execution_order:
            device = self.device_pool.get_device(device_id)
            layers = layer_assignments[device_id]
            
            device_complexity = len(layers) * complexity_per_layer
            compute_time = device.estimate_inference_time(device_complexity, input_size)
            communication_time = self._estimate_communication_time(device, input_size)
            
            total_latency += compute_time + communication_time
        
        return ExecutionPlan(
            execution_type='model_parallel',
            device_assignments=[device.device_id for device in devices],
            layer_assignments=layer_assignments,
            execution_order=execution_order,
            estimated_latency_ms=total_latency
        )
    
    def _estimate_communication_time(self, device: ComputeDevice, 
                                   data_size: int) -> float:
        """Estimate communication time for data transfer"""
        
        # Data size in bytes (assuming float32)
        bytes_to_transfer = data_size * 4
        
        # Convert to GB
        gb_to_transfer = bytes_to_transfer / (1024 ** 3)
        
        # Transfer time in seconds
        transfer_time_sec = gb_to_transfer / device.network_bandwidth_gbps
        
        # Convert to milliseconds and add overhead
        overhead_ms = 1.0  # Network overhead
        return transfer_time_sec * 1000 + overhead_ms

class ModelRegistry:
    """Registry for managing distributed neural network models"""
    
    def __init__(self):
        self.models = {}  # model_id -> ModelMetadata
        self.model_cache = {}  # (model_id, device_id) -> cached model
        self.model_shards = {}  # (model_id, device_id, layers) -> model shard
        
    async def get_model(self, model_id: str, device_id: str) -> torch.nn.Module:
        """Get model for specific device"""
        
        cache_key = (model_id, device_id)
        
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Load model (in practice, from model store)
        model = self._create_mock_model(model_id)
        
        # Move to device
        device = torch.device('cuda' if 'gpu' in device_id else 'cpu')
        model = model.to(device)
        
        # Cache model
        self.model_cache[cache_key] = model
        
        return model
    
    async def get_model_shard(self, model_id: str, device_id: str, 
                            layers: List[int]) -> torch.nn.Module:
        """Get specific layers of model as shard"""
        
        cache_key = (model_id, device_id, tuple(layers))
        
        if cache_key in self.model_shards:
            return self.model_shards[cache_key]
        
        # Create model shard
        full_model = await self.get_model(model_id, device_id)
        model_shard = self._extract_layers(full_model, layers)
        
        # Cache shard
        self.model_shards[cache_key] = model_shard
        
        return model_shard
    
    def _create_mock_model(self, model_id: str) -> torch.nn.Module:
        """Create mock model for demonstration"""
        
        class MockModel(nn.Module):
            def __init__(self, num_layers=50):
                super().__init__()
                self.layers = nn.ModuleList([
                    nn.Linear(512, 512) for _ in range(num_layers)
                ])
                self.output = nn.Linear(512, 1000)
            
            def forward(self, x):
                for layer in self.layers:
                    x = torch.relu(layer(x))
                return self.output(x)
        
        return MockModel()
    
    def _extract_layers(self, model: torch.nn.Module, 
                       layer_indices: List[int]) -> torch.nn.Module:
        """Extract specific layers from model"""
        
        class ModelShard(nn.Module):
            def __init__(self, original_model, layer_indices):
                super().__init__()
                self.layers = nn.ModuleList([
                    original_model.layers[i] for i in layer_indices
                ])
            
            def forward(self, x):
                for layer in self.layers:
                    x = torch.relu(layer(x))
                return x
        
        return ModelShard(model, layer_indices)

class InferenceCache:
    """Cache for inference results"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=False)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    async def get(self, request: InferenceRequest) -> Optional[InferenceResult]:
        """Get cached inference result"""
        
        cache_key = self._generate_cache_key(request)
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                self.cache_stats['hits'] += 1
                # Deserialize result (simplified)
                return self._deserialize_result(cached_data)
            else:
                self.cache_stats['misses'] += 1
                return None
        except Exception as e:
            logging.warning(f"Cache get failed: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    async def put(self, request: InferenceRequest, result: InferenceResult,
                 ttl_seconds: int = 3600):
        """Cache inference result"""
        
        if result.error:
            return  # Don't cache errors
        
        cache_key = self._generate_cache_key(request)
        
        try:
            serialized_result = self._serialize_result(result)
            self.redis_client.setex(cache_key, ttl_seconds, serialized_result)
        except Exception as e:
            logging.warning(f"Cache put failed: {e}")
    
    def _generate_cache_key(self, request: InferenceRequest) -> str:
        """Generate cache key for request"""
        
        # Create deterministic key based on model and input
        input_hash = hash(tuple(request.input_data.flatten().tolist()))
        return f"inference:{request.model_id}:{input_hash}"
    
    def _serialize_result(self, result: InferenceResult) -> bytes:
        """Serialize inference result"""
        # In practice, use efficient serialization like Protocol Buffers
        import pickle
        return pickle.dumps(result)
    
    def _deserialize_result(self, data: bytes) -> InferenceResult:
        """Deserialize inference result"""
        import pickle
        return pickle.loads(data)

class InferenceMetrics:
    """Metrics collection for distributed inference"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_latency_ms': 0.0,
            'p50_latency_ms': 0.0,
            'p95_latency_ms': 0.0,
            'p99_latency_ms': 0.0,
            'throughput_rps': 0.0
        }
        
        self.latency_history = []
        self.request_timestamps = []
        
    def record_request(self, request: InferenceRequest, result: InferenceResult):
        """Record metrics for completed request"""
        
        self.metrics['total_requests'] += 1
        
        if result.error:
            self.metrics['failed_requests'] += 1
        else:
            self.metrics['successful_requests'] += 1
        
        # Record latency
        self.latency_history.append(result.latency_ms)
        self.request_timestamps.append(time.time())
        
        # Keep only recent history
        if len(self.latency_history) > 10000:
            self.latency_history = self.latency_history[-5000:]
            self.request_timestamps = self.request_timestamps[-5000:]
        
        # Update computed metrics
        self._update_computed_metrics()
    
    def _update_computed_metrics(self):
        """Update computed metrics from raw data"""
        
        if not self.latency_history:
            return
        
        # Latency percentiles
        sorted_latencies = sorted(self.latency_history)
        n = len(sorted_latencies)
        
        self.metrics['average_latency_ms'] = np.mean(sorted_latencies)
        self.metrics['p50_latency_ms'] = sorted_latencies[int(n * 0.5)]
        self.metrics['p95_latency_ms'] = sorted_latencies[int(n * 0.95)]
        self.metrics['p99_latency_ms'] = sorted_latencies[int(n * 0.99)]
        
        # Throughput (requests in last minute)
        current_time = time.time()
        recent_requests = [ts for ts in self.request_timestamps 
                          if current_time - ts <= 60]
        self.metrics['throughput_rps'] = len(recent_requests) / 60.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
```

## 2. Model Sharding and Partitioning Strategies

Model sharding distributes neural network parameters across multiple devices to handle models too large for single-device memory or to parallelize computation.

### Tensor Parallelism for Neural Networks

```python
class TensorParallelLayer(nn.Module):
    """
    Tensor parallel implementation of neural network layer
    distributing computation across multiple devices
    """
    
    def __init__(self, input_size: int, output_size: int, world_size: int, rank: int,
                 bias: bool = True, activation: str = 'relu'):
        super().__init__()
        
        self.input_size = input_size
        self.output_size = output_size
        self.world_size = world_size
        self.rank = rank
        
        # Determine partitioning strategy based on dimensions
        self.partition_dim = self._determine_partition_dimension()
        
        if self.partition_dim == 'output':
            # Column-wise partitioning
            self.local_output_size = output_size // world_size
            self.weight = nn.Parameter(torch.randn(input_size, self.local_output_size))
            if bias:
                self.bias = nn.Parameter(torch.randn(self.local_output_size))
            else:
                self.register_buffer('bias', None)
        
        elif self.partition_dim == 'input':
            # Row-wise partitioning
            self.local_input_size = input_size // world_size
            self.weight = nn.Parameter(torch.randn(self.local_input_size, output_size))
            # Only rank 0 has bias to avoid duplication
            if bias and rank == 0:
                self.bias = nn.Parameter(torch.randn(output_size))
            else:
                self.register_buffer('bias', torch.zeros(output_size) if bias else None)
        
        self.activation = self._get_activation_function(activation)
        
        # Communication group for tensor parallelism
        self.process_group = None  # Initialize in setup_distributed()
        
    def _determine_partition_dimension(self) -> str:
        """Determine optimal partitioning dimension"""
        # Heuristic: partition along larger dimension
        if self.output_size >= self.input_size:
            return 'output'
        else:
            return 'input'
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with tensor parallelism"""
        
        if self.partition_dim == 'output':
            return self._forward_column_parallel(x)
        else:
            return self._forward_row_parallel(x)
    
    def _forward_column_parallel(self, x: torch.Tensor) -> torch.Tensor:
        """Column-wise parallel forward pass"""
        
        # Local computation
        local_output = torch.matmul(x, self.weight)
        if self.bias is not None:
            local_output += self.bias
        
        # Apply activation locally
        if self.activation is not None:
            local_output = self.activation(local_output)
        
        # All-gather outputs from all ranks
        if self.world_size > 1:
            output_list = [torch.zeros_like(local_output) for _ in range(self.world_size)]
            torch.distributed.all_gather(output_list, local_output, group=self.process_group)
            global_output = torch.cat(output_list, dim=-1)
        else:
            global_output = local_output
        
        return global_output
    
    def _forward_row_parallel(self, x: torch.Tensor) -> torch.Tensor:
        """Row-wise parallel forward pass"""
        
        # Split input across ranks
        local_input = x[..., self.rank * self.local_input_size:
                         (self.rank + 1) * self.local_input_size]
        
        # Local computation
        local_output = torch.matmul(local_input, self.weight)
        
        # All-reduce to sum partial results
        if self.world_size > 1:
            torch.distributed.all_reduce(local_output, group=self.process_group)
        
        # Add bias (only on rank 0)
        if self.bias is not None and self.rank == 0:
            local_output += self.bias
        
        # Broadcast bias addition result
        if self.world_size > 1:
            torch.distributed.broadcast(local_output, src=0, group=self.process_group)
        
        # Apply activation
        if self.activation is not None:
            local_output = self.activation(local_output)
        
        return local_output
    
    def _get_activation_function(self, activation: str):
        """Get activation function by name"""
        activations = {
            'relu': torch.nn.functional.relu,
            'gelu': torch.nn.functional.gelu,
            'tanh': torch.tanh,
            'sigmoid': torch.sigmoid,
            'none': None
        }
        return activations.get(activation, torch.nn.functional.relu)

class DistributedTransformerBlock(nn.Module):
    """
    Distributed transformer block with tensor and pipeline parallelism
    """
    
    def __init__(self, hidden_size: int, num_attention_heads: int, 
                 intermediate_size: int, world_size: int, rank: int,
                 tensor_parallel_size: int = 1, pipeline_parallel_size: int = 1):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.world_size = world_size
        self.rank = rank
        self.tensor_parallel_size = tensor_parallel_size
        self.pipeline_parallel_size = pipeline_parallel_size
        
        # Determine parallelism configuration
        self.tensor_rank = rank % tensor_parallel_size
        self.pipeline_rank = rank // tensor_parallel_size
        
        # Multi-head attention with tensor parallelism
        self.attention = DistributedMultiHeadAttention(
            hidden_size, num_attention_heads, tensor_parallel_size, self.tensor_rank
        )
        
        # Feed-forward network with tensor parallelism
        self.feed_forward = DistributedFeedForward(
            hidden_size, intermediate_size, tensor_parallel_size, self.tensor_rank
        )
        
        # Layer normalization (replicated across all devices)
        self.ln1 = nn.LayerNorm(hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)
        
        # Dropout
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, hidden_states: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass with distributed computation"""
        
        # Pre-attention layer norm
        attention_input = self.ln1(hidden_states)
        
        # Multi-head attention
        attention_output = self.attention(attention_input, attention_mask)
        attention_output = self.dropout(attention_output)
        
        # Residual connection
        hidden_states = hidden_states + attention_output
        
        # Pre-feed-forward layer norm
        feed_forward_input = self.ln2(hidden_states)
        
        # Feed-forward network
        feed_forward_output = self.feed_forward(feed_forward_input)
        feed_forward_output = self.dropout(feed_forward_output)
        
        # Residual connection
        output = hidden_states + feed_forward_output
        
        return output

class DistributedMultiHeadAttention(nn.Module):
    """Multi-head attention with tensor parallelism"""
    
    def __init__(self, hidden_size: int, num_attention_heads: int, 
                 tensor_parallel_size: int, tensor_rank: int):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.tensor_parallel_size = tensor_parallel_size
        self.tensor_rank = tensor_rank
        
        # Ensure divisibility
        assert num_attention_heads % tensor_parallel_size == 0
        self.local_num_heads = num_attention_heads // tensor_parallel_size
        self.head_dim = hidden_size // num_attention_heads
        
        # Local attention heads
        self.query = TensorParallelLayer(
            hidden_size, hidden_size, tensor_parallel_size, tensor_rank, bias=False
        )
        self.key = TensorParallelLayer(
            hidden_size, hidden_size, tensor_parallel_size, tensor_rank, bias=False
        )
        self.value = TensorParallelLayer(
            hidden_size, hidden_size, tensor_parallel_size, tensor_rank, bias=False
        )
        
        # Output projection
        self.out_proj = TensorParallelLayer(
            hidden_size, hidden_size, tensor_parallel_size, tensor_rank, bias=False
        )
        
        # Attention dropout
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, hidden_states: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass with distributed attention computation"""
        
        batch_size, seq_len, hidden_size = hidden_states.shape
        
        # Compute Q, K, V projections
        query_states = self.query(hidden_states)
        key_states = self.key(hidden_states)
        value_states = self.value(hidden_states)
        
        # Reshape for multi-head attention (local heads only)
        query_states = query_states.view(
            batch_size, seq_len, self.local_num_heads, self.head_dim
        ).transpose(1, 2)
        
        key_states = key_states.view(
            batch_size, seq_len, self.local_num_heads, self.head_dim
        ).transpose(1, 2)
        
        value_states = value_states.view(
            batch_size, seq_len, self.local_num_heads, self.head_dim
        ).transpose(1, 2)
        
        # Scaled dot-product attention
        attention_scores = torch.matmul(query_states, key_states.transpose(-2, -1))
        attention_scores = attention_scores / math.sqrt(self.head_dim)
        
        # Apply attention mask if provided
        if attention_mask is not None:
            attention_scores += attention_mask
        
        # Softmax
        attention_probs = torch.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        
        # Apply attention to values
        context_states = torch.matmul(attention_probs, value_states)
        
        # Reshape back
        context_states = context_states.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.local_num_heads * self.head_dim
        )
        
        # Output projection
        attention_output = self.out_proj(context_states)
        
        return attention_output

class ModelPartitioner:
    """
    Advanced model partitioner for distributed neural networks
    using graph-based optimization
    """
    
    def __init__(self, model: nn.Module, device_capabilities: Dict[str, Dict]):
        self.model = model
        self.device_capabilities = device_capabilities
        
        # Build computation graph
        self.computation_graph = self._build_computation_graph(model)
        
        # Partitioning constraints
        self.memory_constraints = {}
        self.latency_constraints = {}
        
        for device_id, caps in device_capabilities.items():
            self.memory_constraints[device_id] = caps.get('memory_gb', 8) * 1024**3  # Convert to bytes
            self.latency_constraints[device_id] = caps.get('max_latency_ms', 100)
    
    def partition_model(self, num_devices: int, 
                       optimization_objective: str = 'latency') -> Dict[str, List[str]]:
        """
        Partition model across devices optimizing for specified objective
        
        Args:
            num_devices: Number of devices to partition across
            optimization_objective: 'latency', 'throughput', 'memory', or 'energy'
            
        Returns:
            Dictionary mapping device_id to list of layer names
        """
        
        if optimization_objective == 'latency':
            return self._partition_for_latency(num_devices)
        elif optimization_objective == 'throughput':
            return self._partition_for_throughput(num_devices)
        elif optimization_objective == 'memory':
            return self._partition_for_memory(num_devices)
        elif optimization_objective == 'energy':
            return self._partition_for_energy(num_devices)
        else:
            raise ValueError(f"Unknown optimization objective: {optimization_objective}")
    
    def _partition_for_latency(self, num_devices: int) -> Dict[str, List[str]]:
        """Partition model to minimize total inference latency"""
        
        # Get layer information
        layers = list(self.computation_graph.nodes())
        layer_info = {}
        
        for layer in layers:
            info = self.computation_graph.nodes[layer]
            layer_info[layer] = {
                'computation_cost': info.get('flops', 1000),
                'memory_requirement': info.get('memory_mb', 100) * 1024**2,
                'output_size': info.get('output_size', 1024)
            }
        
        # Dynamic programming approach for optimal partitioning
        partition = self._dp_partition(layers, layer_info, num_devices)
        
        # Convert to device assignment
        device_assignment = {}
        available_devices = list(self.device_capabilities.keys())[:num_devices]
        
        for i, device_layers in enumerate(partition):
            device_id = available_devices[i % len(available_devices)]
            if device_id not in device_assignment:
                device_assignment[device_id] = []
            device_assignment[device_id].extend(device_layers)
        
        return device_assignment
    
    def _dp_partition(self, layers: List[str], layer_info: Dict, 
                     num_partitions: int) -> List[List[str]]:
        """Dynamic programming solution for optimal layer partitioning"""
        
        n = len(layers)
        if n == 0 or num_partitions == 0:
            return []
        
        if num_partitions == 1:
            return [layers]
        
        if num_partitions >= n:
            return [[layer] for layer in layers]
        
        # DP table: dp[i][j] = minimum cost to partition first i layers into j partitions
        dp = [[float('inf')] * (num_partitions + 1) for _ in range(n + 1)]
        parent = [[(-1, -1)] * (num_partitions + 1) for _ in range(n + 1)]
        
        # Base cases
        dp[0][0] = 0
        
        # Fill DP table
        for i in range(1, n + 1):
            for j in range(1, min(i + 1, num_partitions + 1)):
                # Try all possible positions for the j-th partition boundary
                for k in range(j - 1, i):
                    # Cost of putting layers k to i-1 in partition j
                    partition_cost = self._calculate_partition_cost(
                        layers[k:i], layer_info
                    )
                    
                    total_cost = dp[k][j - 1] + partition_cost
                    
                    if total_cost < dp[i][j]:
                        dp[i][j] = total_cost
                        parent[i][j] = (k, j - 1)
        
        # Reconstruct solution
        partitions = []
        i, j = n, num_partitions
        
        while i > 0 and j > 0:
            k, prev_j = parent[i][j]
            partitions.append(layers[k:i])
            i, j = k, prev_j
        
        partitions.reverse()
        return partitions
    
    def _calculate_partition_cost(self, partition_layers: List[str], 
                                layer_info: Dict) -> float:
        """Calculate cost of a partition (execution time + communication)"""
        
        if not partition_layers:
            return 0.0
        
        # Computation cost (sequential execution within partition)
        computation_cost = sum(
            layer_info[layer]['computation_cost'] for layer in partition_layers
        )
        
        # Communication cost (based on output size of last layer)
        last_layer = partition_layers[-1]
        communication_cost = layer_info[last_layer]['output_size'] * 0.001  # ms per byte
        
        # Memory constraint penalty
        memory_usage = sum(
            layer_info[layer]['memory_requirement'] for layer in partition_layers
        )
        memory_penalty = max(0, memory_usage - 8 * 1024**3) * 0.1  # Penalty for exceeding 8GB
        
        return computation_cost + communication_cost + memory_penalty
    
    def _build_computation_graph(self, model: nn.Module) -> nx.DiGraph:
        """Build computation graph from PyTorch model"""
        
        graph = nx.DiGraph()
        
        # Simplified graph construction - in practice, use torch.fx or similar
        layer_names = []
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Leaf modules only
                layer_names.append(name)
                
                # Add node with estimated properties
                flops = self._estimate_flops(module)
                memory_mb = self._estimate_memory(module)
                output_size = self._estimate_output_size(module)
                
                graph.add_node(name, flops=flops, memory_mb=memory_mb, 
                             output_size=output_size)
        
        # Add edges (simplified sequential model assumption)
        for i in range(len(layer_names) - 1):
            graph.add_edge(layer_names[i], layer_names[i + 1])
        
        return graph
    
    def _estimate_flops(self, module: nn.Module) -> float:
        """Estimate FLOPs for a module"""
        if isinstance(module, nn.Linear):
            return module.in_features * module.out_features * 2  # MAC operations
        elif isinstance(module, nn.Conv2d):
            # Simplified estimation
            return (module.in_channels * module.out_channels * 
                   module.kernel_size[0] * module.kernel_size[1] * 1000)
        else:
            return 1000  # Default estimate
    
    def _estimate_memory(self, module: nn.Module) -> float:
        """Estimate memory usage in MB"""
        param_count = sum(p.numel() for p in module.parameters())
        return param_count * 4 / (1024**2)  # 4 bytes per float32, convert to MB
    
    def _estimate_output_size(self, module: nn.Module) -> int:
        """Estimate output tensor size in bytes"""
        if isinstance(module, nn.Linear):
            return module.out_features * 4 * 32  # Assume batch size 32
        else:
            return 4096  # Default estimate
```

This implementation provides comprehensive distributed neural network inference capabilities including tensor parallelism, model partitioning, and intelligent routing. The system handles complex model sharding strategies and optimizes for different objectives like latency, throughput, and energy efficiency.

The episode would continue with sections on pipeline parallelism, edge AI deployment patterns, production system analysis, load balancing, caching optimization, and fault tolerance mechanisms, all maintaining the same level of technical depth and practical implementation focus.

Would you like me to continue with the remaining sections of Episode 144 or proceed to create Episode 145?