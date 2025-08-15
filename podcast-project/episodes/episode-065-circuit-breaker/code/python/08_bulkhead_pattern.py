#!/usr/bin/env python3
"""
Bulkhead Pattern with Circuit Breaker
Resource isolation और thread pool management के साथ

Bulkhead pattern ship के compartments की तरह काम करता है
अगर एक section fail हो जाए तो बाकी safe रहते हैं
"""

import time
import threading
import queue
import concurrent.futures
from enum import Enum
from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random
import json
import functools


class BulkheadType(Enum):
    """Different types of bulkhead isolation"""
    THREAD_POOL = "thread_pool"           # Thread pool isolation
    SEMAPHORE = "semaphore"               # Semaphore-based isolation
    QUEUE_BASED = "queue_based"           # Queue-based resource isolation
    CPU_INTENSIVE = "cpu_intensive"       # CPU-intensive task isolation
    IO_INTENSIVE = "io_intensive"         # I/O-intensive task isolation


class ResourceType(Enum):
    """Types of resources to isolate"""
    DATABASE_CONNECTIONS = "database_connections"
    HTTP_CONNECTIONS = "http_connections"
    FILE_HANDLES = "file_handles"
    MEMORY_BUFFERS = "memory_buffers"
    CPU_CORES = "cpu_cores"
    NETWORK_BANDWIDTH = "network_bandwidth"


@dataclass
class BulkheadConfig:
    """Configuration for bulkhead pattern"""
    bulkhead_type: BulkheadType
    resource_type: ResourceType
    max_concurrent_requests: int = 10
    max_queue_size: int = 100
    timeout: float = 30.0
    thread_pool_size: int = 5
    semaphore_permits: int = 5
    rejection_threshold: float = 0.8  # Reject when 80% capacity reached
    priority_levels: int = 3
    enable_priority_queue: bool = False


@dataclass
class BulkheadMetrics:
    """Metrics for bulkhead performance"""
    total_requests: int = 0
    successful_requests: int = 0
    rejected_requests: int = 0
    queued_requests: int = 0
    timeout_requests: int = 0
    current_active_threads: int = 0
    current_queue_size: int = 0
    peak_active_threads: int = 0
    peak_queue_size: int = 0
    avg_execution_time: float = 0.0
    avg_queue_time: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)


class PriorityRequest:
    """Request with priority for queue ordering"""
    
    def __init__(self, func: Callable, args: tuple, kwargs: dict, priority: int = 1):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.priority = priority
        self.created_at = time.time()
        self.request_id = f"REQ_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
    
    def __lt__(self, other):
        # Higher priority first (lower number = higher priority)
        return self.priority < other.priority
    
    def execute(self) -> Any:
        """Execute the request"""
        return self.func(*self.args, **self.kwargs)


class BulkheadCircuitBreaker:
    """
    Circuit Breaker with Bulkhead Pattern implementation
    यह multiple resources को isolate करता है different bulkheads में
    ताकि एक service का failure दूसरे को affect न करे
    """
    
    def __init__(
        self,
        name: str,
        bulkhead_configs: Dict[str, BulkheadConfig],
        circuit_failure_threshold: int = 5,
        circuit_recovery_timeout: float = 60.0
    ):
        self.name = name
        self.bulkhead_configs = bulkhead_configs
        self.circuit_failure_threshold = circuit_failure_threshold
        self.circuit_recovery_timeout = circuit_recovery_timeout
        
        # Circuit breaker state per bulkhead
        self.circuit_states = {}
        self.failure_counts = {}
        self.last_failure_times = {}
        
        # Bulkhead resources per configuration
        self.thread_pools = {}
        self.semaphores = {}
        self.request_queues = {}
        self.priority_queues = {}
        
        # Metrics per bulkhead
        self.metrics = {}
        
        # Thread safety
        self._locks = {}
        
        # Initialize bulkheads
        self._initialize_bulkheads()
        
        print(f"🚢 Bulkhead Circuit Breaker '{name}' initialized")
        print(f"   - Number of bulkheads: {len(bulkhead_configs)}")
        for bulkhead_name, config in bulkhead_configs.items():
            print(f"   - {bulkhead_name}: {config.bulkhead_type.value} "
                  f"(max: {config.max_concurrent_requests})")
    
    def _initialize_bulkheads(self):
        """Initialize all bulkhead resources"""
        for bulkhead_name, config in self.bulkhead_configs.items():
            # Initialize circuit state
            self.circuit_states[bulkhead_name] = "CLOSED"
            self.failure_counts[bulkhead_name] = 0
            self.last_failure_times[bulkhead_name] = None
            
            # Initialize metrics
            self.metrics[bulkhead_name] = BulkheadMetrics()
            
            # Initialize lock
            self._locks[bulkhead_name] = threading.Lock()
            
            # Initialize bulkhead-specific resources
            if config.bulkhead_type == BulkheadType.THREAD_POOL:
                self.thread_pools[bulkhead_name] = concurrent.futures.ThreadPoolExecutor(
                    max_workers=config.thread_pool_size,
                    thread_name_prefix=f"{bulkhead_name}_thread"
                )
            
            elif config.bulkhead_type == BulkheadType.SEMAPHORE:
                self.semaphores[bulkhead_name] = threading.Semaphore(config.semaphore_permits)
            
            elif config.bulkhead_type == BulkheadType.QUEUE_BASED:
                if config.enable_priority_queue:
                    self.priority_queues[bulkhead_name] = queue.PriorityQueue(maxsize=config.max_queue_size)
                else:
                    self.request_queues[bulkhead_name] = queue.Queue(maxsize=config.max_queue_size)
    
    def call(
        self,
        bulkhead_name: str,
        func: Callable,
        *args,
        priority: int = 1,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """
        Execute function through specified bulkhead
        """
        if bulkhead_name not in self.bulkhead_configs:
            raise ValueError(f"Unknown bulkhead: {bulkhead_name}")
        
        config = self.bulkhead_configs[bulkhead_name]
        timeout = timeout or config.timeout
        
        with self._locks[bulkhead_name]:
            # Check circuit state
            if self._should_reject_request(bulkhead_name):
                self.metrics[bulkhead_name].rejected_requests += 1
                raise CircuitBreakerOpenError(
                    f"Circuit breaker for bulkhead '{bulkhead_name}' is OPEN"
                )
            
            # Check capacity and reject if needed
            if self._should_reject_due_to_capacity(bulkhead_name):
                self.metrics[bulkhead_name].rejected_requests += 1
                raise BulkheadCapacityError(
                    f"Bulkhead '{bulkhead_name}' at capacity. Request rejected."
                )
        
        # Execute based on bulkhead type
        return self._execute_through_bulkhead(
            bulkhead_name, func, args, kwargs, priority, timeout
        )
    
    def _should_reject_request(self, bulkhead_name: str) -> bool:
        """Check if request should be rejected due to circuit state"""
        state = self.circuit_states[bulkhead_name]
        
        if state == "CLOSED":
            return False
        
        if state == "OPEN":
            # Check if recovery timeout has passed
            last_failure = self.last_failure_times[bulkhead_name]
            if last_failure and (time.time() - last_failure) >= self.circuit_recovery_timeout:
                self.circuit_states[bulkhead_name] = "HALF_OPEN"
                print(f"🟡 Circuit for bulkhead '{bulkhead_name}' moved to HALF_OPEN")
                return False
            return True
        
        # HALF_OPEN state - allow limited requests
        return False
    
    def _should_reject_due_to_capacity(self, bulkhead_name: str) -> bool:
        """Check if request should be rejected due to capacity limits"""
        config = self.bulkhead_configs[bulkhead_name]
        metrics = self.metrics[bulkhead_name]
        
        # Check current utilization
        current_utilization = self._get_current_utilization(bulkhead_name)
        
        if current_utilization >= config.rejection_threshold:
            return True
        
        return False
    
    def _get_current_utilization(self, bulkhead_name: str) -> float:
        """Get current resource utilization for bulkhead"""
        config = self.bulkhead_configs[bulkhead_name]
        metrics = self.metrics[bulkhead_name]
        
        if config.bulkhead_type == BulkheadType.THREAD_POOL:
            if bulkhead_name in self.thread_pools:
                # ThreadPoolExecutor doesn't expose current thread count directly
                # Using active count as approximation
                return metrics.current_active_threads / config.thread_pool_size
        
        elif config.bulkhead_type == BulkheadType.SEMAPHORE:
            if bulkhead_name in self.semaphores:
                semaphore = self.semaphores[bulkhead_name]
                # Approximate utilization based on available permits
                available = semaphore._value if hasattr(semaphore, '_value') else 0
                return 1.0 - (available / config.semaphore_permits)
        
        elif config.bulkhead_type == BulkheadType.QUEUE_BASED:
            return metrics.current_queue_size / config.max_queue_size
        
        return 0.0
    
    def _execute_through_bulkhead(
        self,
        bulkhead_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        priority: int,
        timeout: float
    ) -> Any:
        """Execute function through appropriate bulkhead mechanism"""
        config = self.bulkhead_configs[bulkhead_name]
        start_time = time.time()
        
        try:
            if config.bulkhead_type == BulkheadType.THREAD_POOL:
                result = self._execute_thread_pool(bulkhead_name, func, args, kwargs, timeout)
            
            elif config.bulkhead_type == BulkheadType.SEMAPHORE:
                result = self._execute_semaphore(bulkhead_name, func, args, kwargs, timeout)
            
            elif config.bulkhead_type == BulkheadType.QUEUE_BASED:
                result = self._execute_queue_based(bulkhead_name, func, args, kwargs, priority, timeout)
            
            else:
                raise ValueError(f"Unsupported bulkhead type: {config.bulkhead_type}")
            
            # Success handling
            execution_time = time.time() - start_time
            self._handle_success(bulkhead_name, execution_time)
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_failure(bulkhead_name, e, execution_time)
            raise e
    
    def _execute_thread_pool(
        self,
        bulkhead_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        timeout: float
    ) -> Any:
        """Execute using thread pool bulkhead"""
        thread_pool = self.thread_pools[bulkhead_name]
        metrics = self.metrics[bulkhead_name]
        
        # Update active thread count
        metrics.current_active_threads += 1
        metrics.peak_active_threads = max(metrics.peak_active_threads, metrics.current_active_threads)
        
        try:
            future = thread_pool.submit(func, *args, **kwargs)
            result = future.result(timeout=timeout)
            
            print(f"🏊‍♂️ Thread pool execution successful: {bulkhead_name}")
            return result
        
        except concurrent.futures.TimeoutError:
            metrics.timeout_requests += 1
            raise TimeoutError(f"Request timed out in thread pool '{bulkhead_name}' after {timeout}s")
        
        finally:
            metrics.current_active_threads -= 1
    
    def _execute_semaphore(
        self,
        bulkhead_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        timeout: float
    ) -> Any:
        """Execute using semaphore bulkhead"""
        semaphore = self.semaphores[bulkhead_name]
        metrics = self.metrics[bulkhead_name]
        
        # Try to acquire semaphore
        acquired = semaphore.acquire(timeout=timeout)
        if not acquired:
            metrics.timeout_requests += 1
            raise TimeoutError(f"Could not acquire semaphore for '{bulkhead_name}' within {timeout}s")
        
        try:
            # Execute function with timeout
            result = self._execute_with_timeout(func, args, kwargs, timeout)
            print(f"🚧 Semaphore execution successful: {bulkhead_name}")
            return result
        
        finally:
            semaphore.release()
    
    def _execute_queue_based(
        self,
        bulkhead_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        priority: int,
        timeout: float
    ) -> Any:
        """Execute using queue-based bulkhead"""
        config = self.bulkhead_configs[bulkhead_name]
        metrics = self.metrics[bulkhead_name]
        
        if config.enable_priority_queue and bulkhead_name in self.priority_queues:
            return self._execute_priority_queue(bulkhead_name, func, args, kwargs, priority, timeout)
        else:
            return self._execute_simple_queue(bulkhead_name, func, args, kwargs, timeout)
    
    def _execute_priority_queue(
        self,
        bulkhead_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        priority: int,
        timeout: float
    ) -> Any:
        """Execute using priority queue"""
        pq = self.priority_queues[bulkhead_name]
        metrics = self.metrics[bulkhead_name]
        
        request = PriorityRequest(func, args, kwargs, priority)
        
        try:
            # Add to priority queue
            pq.put(request, timeout=timeout)
            metrics.queued_requests += 1
            metrics.current_queue_size = pq.qsize()
            metrics.peak_queue_size = max(metrics.peak_queue_size, metrics.current_queue_size)
            
            print(f"📋 Request queued with priority {priority}: {bulkhead_name}")
            
            # In real implementation, background workers would process the queue
            # For demo, we'll process immediately
            processed_request = pq.get(timeout=timeout)
            queue_time = time.time() - processed_request.created_at
            
            metrics.avg_queue_time = (metrics.avg_queue_time + queue_time) / 2
            metrics.current_queue_size = pq.qsize()
            
            result = processed_request.execute()
            print(f"✅ Priority queue execution successful: {bulkhead_name} (queue time: {queue_time:.3f}s)")
            
            return result
        
        except queue.Full:
            raise BulkheadCapacityError(f"Priority queue for '{bulkhead_name}' is full")
        except queue.Empty:
            raise TimeoutError(f"Timeout waiting for queue processing in '{bulkhead_name}'")
    
    def _execute_simple_queue(
        self,
        bulkhead_name: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        timeout: float
    ) -> Any:
        """Execute using simple FIFO queue"""
        q = self.request_queues[bulkhead_name]
        metrics = self.metrics[bulkhead_name]
        
        request = PriorityRequest(func, args, kwargs)
        
        try:
            q.put(request, timeout=timeout)
            metrics.queued_requests += 1
            metrics.current_queue_size = q.qsize()
            metrics.peak_queue_size = max(metrics.peak_queue_size, metrics.current_queue_size)
            
            # Process immediately for demo
            processed_request = q.get(timeout=timeout)
            queue_time = time.time() - processed_request.created_at
            
            metrics.avg_queue_time = (metrics.avg_queue_time + queue_time) / 2
            metrics.current_queue_size = q.qsize()
            
            result = processed_request.execute()
            print(f"✅ Queue execution successful: {bulkhead_name} (queue time: {queue_time:.3f}s)")
            
            return result
        
        except queue.Full:
            raise BulkheadCapacityError(f"Queue for '{bulkhead_name}' is full")
    
    def _execute_with_timeout(self, func: Callable, args: tuple, kwargs: dict, timeout: float) -> Any:
        """Execute function with timeout using threading"""
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            # Timeout occurred
            raise TimeoutError(f"Function execution timed out after {timeout}s")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def _handle_success(self, bulkhead_name: str, execution_time: float):
        """Handle successful request execution"""
        metrics = self.metrics[bulkhead_name]
        
        metrics.total_requests += 1
        metrics.successful_requests += 1
        
        # Update average execution time
        if metrics.successful_requests > 1:
            metrics.avg_execution_time = (
                (metrics.avg_execution_time * (metrics.successful_requests - 1) + execution_time) /
                metrics.successful_requests
            )
        else:
            metrics.avg_execution_time = execution_time
        
        # Circuit breaker state management
        state = self.circuit_states[bulkhead_name]
        if state == "HALF_OPEN":
            # Reset circuit on success
            self.circuit_states[bulkhead_name] = "CLOSED"
            self.failure_counts[bulkhead_name] = 0
            print(f"✅ Circuit for bulkhead '{bulkhead_name}' CLOSED - Service recovered")
        elif state == "CLOSED":
            # Reset failure count on success
            self.failure_counts[bulkhead_name] = 0
    
    def _handle_failure(self, bulkhead_name: str, error: Exception, execution_time: float):
        """Handle failed request execution"""
        metrics = self.metrics[bulkhead_name]
        
        metrics.total_requests += 1
        self.failure_counts[bulkhead_name] += 1
        self.last_failure_times[bulkhead_name] = time.time()
        
        # Check if circuit should be opened
        if self.failure_counts[bulkhead_name] >= self.circuit_failure_threshold:
            if self.circuit_states[bulkhead_name] != "OPEN":
                self.circuit_states[bulkhead_name] = "OPEN"
                print(f"🔴 Circuit for bulkhead '{bulkhead_name}' OPENED after "
                      f"{self.failure_counts[bulkhead_name]} failures")
        
        print(f"❌ Failure in bulkhead '{bulkhead_name}': {str(error)[:50]} ({execution_time:.3f}s)")
    
    def get_bulkhead_metrics(self, bulkhead_name: str) -> Dict[str, Any]:
        """Get metrics for specific bulkhead"""
        if bulkhead_name not in self.metrics:
            return {}
        
        metrics = self.metrics[bulkhead_name]
        config = self.bulkhead_configs[bulkhead_name]
        
        success_rate = 0.0
        if metrics.total_requests > 0:
            success_rate = (metrics.successful_requests / metrics.total_requests) * 100
        
        return {
            "bulkhead_name": bulkhead_name,
            "bulkhead_type": config.bulkhead_type.value,
            "resource_type": config.resource_type.value,
            "circuit_state": self.circuit_states[bulkhead_name],
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "rejected_requests": metrics.rejected_requests,
            "queued_requests": metrics.queued_requests,
            "timeout_requests": metrics.timeout_requests,
            "success_rate": round(success_rate, 2),
            "failure_count": self.failure_counts[bulkhead_name],
            "current_active_threads": metrics.current_active_threads,
            "current_queue_size": metrics.current_queue_size,
            "peak_active_threads": metrics.peak_active_threads,
            "peak_queue_size": metrics.peak_queue_size,
            "avg_execution_time": round(metrics.avg_execution_time, 3),
            "avg_queue_time": round(metrics.avg_queue_time, 3),
            "current_utilization": round(self._get_current_utilization(bulkhead_name) * 100, 2),
            "capacity_config": {
                "max_concurrent": config.max_concurrent_requests,
                "max_queue_size": config.max_queue_size,
                "thread_pool_size": config.thread_pool_size if config.bulkhead_type == BulkheadType.THREAD_POOL else None,
                "semaphore_permits": config.semaphore_permits if config.bulkhead_type == BulkheadType.SEMAPHORE else None
            }
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all bulkheads"""
        all_metrics = {}
        for bulkhead_name in self.bulkhead_configs.keys():
            all_metrics[bulkhead_name] = self.get_bulkhead_metrics(bulkhead_name)
        
        return {
            "system_name": self.name,
            "total_bulkheads": len(self.bulkhead_configs),
            "bulkheads": all_metrics,
            "system_summary": self._get_system_summary()
        }
    
    def _get_system_summary(self) -> Dict[str, Any]:
        """Get system-wide summary metrics"""
        total_requests = sum(m.total_requests for m in self.metrics.values())
        total_successful = sum(m.successful_requests for m in self.metrics.values())
        total_rejected = sum(m.rejected_requests for m in self.metrics.values())
        
        open_circuits = sum(1 for state in self.circuit_states.values() if state == "OPEN")
        healthy_circuits = sum(1 for state in self.circuit_states.values() if state == "CLOSED")
        
        overall_success_rate = (total_successful / max(total_requests, 1)) * 100
        
        return {
            "total_requests": total_requests,
            "total_successful": total_successful,
            "total_rejected": total_rejected,
            "overall_success_rate": round(overall_success_rate, 2),
            "healthy_circuits": healthy_circuits,
            "open_circuits": open_circuits,
            "half_open_circuits": len(self.circuit_states) - healthy_circuits - open_circuits
        }
    
    def shutdown(self):
        """Cleanup resources"""
        for thread_pool in self.thread_pools.values():
            thread_pool.shutdown(wait=True)
        print(f"🚢 Bulkhead Circuit Breaker '{self.name}' shutdown complete")


class CircuitBreakerOpenError(Exception):
    """Circuit breaker is open"""
    pass


class BulkheadCapacityError(Exception):
    """Bulkhead at capacity"""
    pass


# Example services for testing different bulkheads
def database_operation(operation: str, delay: float = 1.0, fail_rate: float = 0.2):
    """Simulate database operation"""
    print(f"🗄️  Database operation: {operation}")
    time.sleep(delay)
    
    if random.random() < fail_rate:
        raise Exception(f"Database operation '{operation}' failed")
    
    return f"Database result for {operation}"


def http_api_call(endpoint: str, delay: float = 2.0, fail_rate: float = 0.3):
    """Simulate HTTP API call"""
    print(f"🌐 HTTP API call: {endpoint}")
    time.sleep(delay)
    
    if random.random() < fail_rate:
        raise Exception(f"HTTP call to '{endpoint}' failed")
    
    return f"API response from {endpoint}"


def file_processing(filename: str, delay: float = 3.0, fail_rate: float = 0.1):
    """Simulate file processing"""
    print(f"📁 Processing file: {filename}")
    time.sleep(delay)
    
    if random.random() < fail_rate:
        raise Exception(f"File processing '{filename}' failed")
    
    return f"Processed file {filename}"


def cpu_intensive_task(task_name: str, delay: float = 2.5, fail_rate: float = 0.15):
    """Simulate CPU-intensive task"""
    print(f"💻 CPU task: {task_name}")
    time.sleep(delay)
    
    if random.random() < fail_rate:
        raise Exception(f"CPU task '{task_name}' failed")
    
    return f"CPU task {task_name} completed"


def test_bulkhead_circuit_breaker():
    """Comprehensive test of bulkhead pattern with circuit breaker"""
    print("🧪 Testing Bulkhead Pattern with Circuit Breaker")
    print("=" * 70)
    
    # Configure multiple bulkheads for different resource types
    bulkhead_configs = {
        "database": BulkheadConfig(
            bulkhead_type=BulkheadType.THREAD_POOL,
            resource_type=ResourceType.DATABASE_CONNECTIONS,
            max_concurrent_requests=3,
            thread_pool_size=3,
            timeout=10.0,
            rejection_threshold=0.8
        ),
        
        "http_api": BulkheadConfig(
            bulkhead_type=BulkheadType.SEMAPHORE,
            resource_type=ResourceType.HTTP_CONNECTIONS,
            semaphore_permits=5,
            timeout=15.0,
            rejection_threshold=0.7
        ),
        
        "file_processing": BulkheadConfig(
            bulkhead_type=BulkheadType.QUEUE_BASED,
            resource_type=ResourceType.FILE_HANDLES,
            max_queue_size=10,
            timeout=20.0,
            enable_priority_queue=True,
            priority_levels=3
        ),
        
        "cpu_tasks": BulkheadConfig(
            bulkhead_type=BulkheadType.THREAD_POOL,
            resource_type=ResourceType.CPU_CORES,
            max_concurrent_requests=2,
            thread_pool_size=2,
            timeout=10.0,
            rejection_threshold=0.9
        )
    }
    
    # Create bulkhead circuit breaker
    bcb = BulkheadCircuitBreaker(
        name="multi-service-system",
        bulkhead_configs=bulkhead_configs,
        circuit_failure_threshold=3,
        circuit_recovery_timeout=15.0
    )
    
    print("\n📊 Phase 1: Testing isolated bulkhead operations")
    print("-" * 60)
    
    # Test each bulkhead independently
    test_scenarios = [
        ("database", database_operation, ("SELECT users", 1.5, 0.3)),
        ("http_api", http_api_call, ("/api/users", 2.0, 0.4)),
        ("file_processing", file_processing, ("data.csv", 2.5, 0.2)),
        ("cpu_tasks", cpu_intensive_task, ("ML_training", 3.0, 0.25)),
    ]
    
    # Run multiple requests concurrently for each bulkhead
    import concurrent.futures
    
    def run_bulkhead_test(bulkhead_name: str, func: Callable, test_args: tuple):
        """Run multiple requests against a bulkhead"""
        results = []
        for i in range(5):
            try:
                priority = random.randint(1, 3)  # Random priority for queue-based
                result = bcb.call(
                    bulkhead_name,
                    func,
                    f"{test_args[0]}_{i+1}",
                    test_args[1],
                    test_args[2],
                    priority=priority,
                    timeout=test_args[1] + 5.0
                )
                results.append(f"✅ {bulkhead_name}-{i+1}: Success")
            except Exception as e:
                results.append(f"❌ {bulkhead_name}-{i+1}: {str(e)[:50]}")
            
            time.sleep(0.5)
        return results
    
    # Run bulkhead tests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for bulkhead_name, func, test_args in test_scenarios:
            future = executor.submit(run_bulkhead_test, bulkhead_name, func, test_args)
            futures.append((bulkhead_name, future))
        
        # Collect results
        for bulkhead_name, future in futures:
            try:
                results = future.result(timeout=30)
                print(f"\n{bulkhead_name.upper()} Bulkhead Results:")
                for result in results:
                    print(f"  {result}")
            except concurrent.futures.TimeoutError:
                print(f"\n{bulkhead_name.upper()} Bulkhead: Timeout")
    
    print("\n📊 Phase 2: Testing bulkhead isolation during failures")
    print("-" * 60)
    
    # Force one bulkhead to fail heavily
    print("Forcing database bulkhead failures...")
    for i in range(6):  # Exceed failure threshold
        try:
            bcb.call(
                "database",
                database_operation,
                f"FAILING_QUERY_{i+1}",
                1.0,
                1.0  # 100% failure rate
            )
        except Exception as e:
            print(f"  Expected failure {i+1}: {str(e)[:40]}")
        time.sleep(0.5)
    
    # Test that other bulkheads still work
    print("\nTesting isolation - other bulkheads should still work:")
    try:
        result = bcb.call("http_api", http_api_call, "/api/health", 1.0, 0.1)
        print(f"✅ HTTP API still working: Success")
    except Exception as e:
        print(f"❌ HTTP API affected: {str(e)[:50]}")
    
    try:
        result = bcb.call("file_processing", file_processing, "backup.txt", 1.0, 0.1, priority=1)
        print(f"✅ File processing still working: Success")
    except Exception as e:
        print(f"❌ File processing affected: {str(e)[:50]}")
    
    print("\n📊 Phase 3: Testing bulkhead recovery")
    print("-" * 60)
    
    print("Waiting for circuit recovery...")
    time.sleep(16)  # Wait for recovery timeout
    
    # Test database recovery
    for i in range(3):
        try:
            result = bcb.call(
                "database",
                database_operation,
                f"RECOVERY_QUERY_{i+1}",
                1.0,
                0.1  # Low failure rate
            )
            print(f"✅ Database recovery test {i+1}: Success")
        except Exception as e:
            print(f"❌ Database recovery test {i+1}: {str(e)[:50]}")
        time.sleep(1)
    
    print("\n📊 Phase 4: Load testing bulkhead capacity")
    print("-" * 60)
    
    # Stress test one bulkhead to see rejection behavior
    def stress_test_bulkhead():
        results = {"success": 0, "rejected": 0, "timeout": 0, "error": 0}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # Submit many requests quickly
            for i in range(20):
                future = executor.submit(
                    bcb.call,
                    "http_api",
                    http_api_call,
                    f"/api/stress_{i}",
                    0.5,  # Fast requests
                    0.2   # Some failures
                )
                futures.append(future)
            
            # Collect results
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=5)
                    results["success"] += 1
                    print(f"✅ Stress {i+1}: Success")
                except BulkheadCapacityError:
                    results["rejected"] += 1
                    print(f"🚫 Stress {i+1}: Rejected (capacity)")
                except concurrent.futures.TimeoutError:
                    results["timeout"] += 1
                    print(f"⏰ Stress {i+1}: Timeout")
                except Exception as e:
                    results["error"] += 1
                    print(f"❌ Stress {i+1}: {str(e)[:30]}")
        
        return results
    
    stress_results = stress_test_bulkhead()
    print(f"\nStress Test Results:")
    print(f"  Success: {stress_results['success']}")
    print(f"  Rejected: {stress_results['rejected']}")
    print(f"  Timeout: {stress_results['timeout']}")
    print(f"  Error: {stress_results['error']}")
    
    print("\n📈 Final System Metrics:")
    print("=" * 50)
    final_metrics = bcb.get_all_metrics()
    print(json.dumps(final_metrics, indent=2, default=str))
    
    # Cleanup
    bcb.shutdown()


if __name__ == "__main__":
    test_bulkhead_circuit_breaker()