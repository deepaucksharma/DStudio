#!/usr/bin/env python3
"""
Circuit Breaker with Advanced Fallback Mechanisms
विभिन्न प्रकार की fallback strategies और recovery patterns

Production systems में fallback mechanism सबसे critical part होता है
यह users को graceful experience देता है जब main service fail हो जाए
"""

import time
import random
import threading
import json
from enum import Enum
from typing import Callable, Any, Optional, Dict, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import functools
import pickle
import sqlite3
import hashlib


class FallbackType(Enum):
    """Different types of fallback strategies"""
    STATIC_RESPONSE = "static_response"       # Static JSON/data response
    CACHE_LOOKUP = "cache_lookup"             # Look in cache for previous response
    ALTERNATIVE_SERVICE = "alternative_service"  # Call alternative service
    QUEUE_FOR_LATER = "queue_for_later"       # Queue request for later processing
    DEGRADED_RESPONSE = "degraded_response"   # Simplified/reduced functionality response
    CIRCUIT_BREAKER_CHAIN = "circuit_breaker_chain"  # Try multiple services in sequence
    USER_NOTIFICATION = "user_notification"   # Notify user about service unavailability


class FallbackPriority(Enum):
    """Priority levels for fallback execution"""
    HIGH = 1      # Execute immediately
    MEDIUM = 2    # Execute with slight delay
    LOW = 3       # Execute when resources available
    BACKGROUND = 4  # Execute in background


@dataclass
class FallbackConfig:
    """Configuration for fallback mechanism"""
    fallback_type: FallbackType
    priority: FallbackPriority = FallbackPriority.MEDIUM
    timeout: float = 5.0
    retry_count: int = 0
    static_data: Any = None
    alternative_endpoint: Optional[str] = None
    cache_ttl: int = 300  # Cache TTL in seconds
    queue_name: Optional[str] = None
    notification_message: Optional[str] = None
    enabled: bool = True


@dataclass
class FallbackMetrics:
    """Metrics for fallback executions"""
    total_fallbacks: int = 0
    successful_fallbacks: int = 0
    failed_fallbacks: int = 0
    fallback_by_type: Dict[str, int] = field(default_factory=dict)
    avg_fallback_duration: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    queue_size: int = 0


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self.cache = {}
        self.expiry = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key in self.cache:
                if key in self.expiry and time.time() > self.expiry[key]:
                    # Expired
                    del self.cache[key]
                    del self.expiry[key]
                    return None
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        with self._lock:
            self.cache[key] = value
            self.expiry[key] = time.time() + ttl
    
    def clear(self):
        """Clear all cache"""
        with self._lock:
            self.cache.clear()
            self.expiry.clear()
    
    def size(self) -> int:
        """Get cache size"""
        with self._lock:
            # Clean expired entries first
            current_time = time.time()
            expired_keys = [k for k, exp in self.expiry.items() if current_time > exp]
            for key in expired_keys:
                del self.cache[key]
                del self.expiry[key]
            
            return len(self.cache)


class RequestQueue:
    """Simple request queue for later processing"""
    
    def __init__(self, name: str, max_size: int = 1000):
        self.name = name
        self.max_size = max_size
        self.queue = []
        self._lock = threading.Lock()
    
    def enqueue(self, request_data: Dict[str, Any]) -> bool:
        """Add request to queue"""
        with self._lock:
            if len(self.queue) >= self.max_size:
                # Remove oldest request
                self.queue.pop(0)
            
            request_data['queued_at'] = time.time()
            self.queue.append(request_data)
            return True
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Remove and return oldest request"""
        with self._lock:
            if self.queue:
                return self.queue.pop(0)
            return None
    
    def size(self) -> int:
        """Get queue size"""
        with self._lock:
            return len(self.queue)
    
    def peek(self, count: int = 5) -> List[Dict[str, Any]]:
        """Peek at first N requests without removing"""
        with self._lock:
            return self.queue[:count]


class FallbackCircuitBreaker:
    """
    Advanced Circuit Breaker with multiple fallback mechanisms
    यह implementation विभिन्न fallback strategies provide करती है
    जो production systems में common होते हैं
    """
    
    def __init__(
        self,
        name: str,
        fallback_configs: List[FallbackConfig],
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0
    ):
        self.name = name
        self.fallback_configs = sorted(fallback_configs, key=lambda x: x.priority.value)
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        # Circuit state
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
        # Fallback infrastructure
        self.cache = SimpleCache()
        self.request_queues = {}
        self.fallback_metrics = FallbackMetrics()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize queues for queue-based fallbacks
        for config in fallback_configs:
            if config.fallback_type == FallbackType.QUEUE_FOR_LATER and config.queue_name:
                self.request_queues[config.queue_name] = RequestQueue(config.queue_name)
        
        print(f"🔧 Fallback Circuit Breaker '{name}' initialized")
        print(f"   - Fallback strategies: {len(fallback_configs)}")
        print(f"   - Failure threshold: {failure_threshold}")
        print(f"   - Recovery timeout: {recovery_timeout}s")
    
    def call(self, func: Callable, *args, cache_key: Optional[str] = None, **kwargs) -> Any:
        """
        Execute function with circuit breaker and fallback protection
        """
        with self._lock:
            # Check circuit state
            if self.state == "OPEN":
                time_since_failure = time.time() - (self.last_failure_time or 0)
                if time_since_failure >= self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    print(f"🟡 Circuit '{self.name}' moved to HALF_OPEN")
                else:
                    # Circuit is open, execute fallbacks immediately
                    return self._execute_fallbacks(func, args, kwargs, cache_key, "Circuit is OPEN")
        
        # Try primary function
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache successful result if cache_key provided
            if cache_key:
                self._cache_result(cache_key, result)
            
            # Success handling
            self._handle_success()
            
            print(f"✅ Primary call successful in {execution_time:.3f}s")
            return result
        
        except Exception as e:
            # Primary function failed, execute fallbacks
            self._handle_failure(str(e))
            return self._execute_fallbacks(func, args, kwargs, cache_key, str(e))
    
    def _execute_fallbacks(self, original_func: Callable, args: tuple, kwargs: dict, cache_key: Optional[str], error_reason: str) -> Any:
        """
        Execute fallback strategies in priority order
        """
        print(f"🔄 Executing fallbacks for '{self.name}' - Reason: {error_reason}")
        
        self.fallback_metrics.total_fallbacks += 1
        
        for config in self.fallback_configs:
            if not config.enabled:
                continue
            
            try:
                start_time = time.time()
                result = self._execute_single_fallback(config, original_func, args, kwargs, cache_key, error_reason)
                
                execution_time = time.time() - start_time
                self._update_fallback_metrics(config.fallback_type, True, execution_time)
                
                print(f"✅ Fallback successful: {config.fallback_type.value} ({execution_time:.3f}s)")
                return result
            
            except Exception as e:
                execution_time = time.time() - start_time
                self._update_fallback_metrics(config.fallback_type, False, execution_time)
                print(f"❌ Fallback failed: {config.fallback_type.value} - {str(e)}")
                continue
        
        # All fallbacks failed
        self.fallback_metrics.failed_fallbacks += 1
        raise Exception(f"All fallbacks failed for '{self.name}'. Original error: {error_reason}")
    
    def _execute_single_fallback(self, config: FallbackConfig, original_func: Callable, args: tuple, kwargs: dict, cache_key: Optional[str], error_reason: str) -> Any:
        """
        Execute a single fallback strategy
        """
        fallback_type = config.fallback_type
        
        if fallback_type == FallbackType.STATIC_RESPONSE:
            return self._static_response_fallback(config)
        
        elif fallback_type == FallbackType.CACHE_LOOKUP:
            return self._cache_lookup_fallback(config, cache_key)
        
        elif fallback_type == FallbackType.ALTERNATIVE_SERVICE:
            return self._alternative_service_fallback(config, args, kwargs)
        
        elif fallback_type == FallbackType.QUEUE_FOR_LATER:
            return self._queue_for_later_fallback(config, original_func, args, kwargs)
        
        elif fallback_type == FallbackType.DEGRADED_RESPONSE:
            return self._degraded_response_fallback(config, args, kwargs)
        
        elif fallback_type == FallbackType.USER_NOTIFICATION:
            return self._user_notification_fallback(config, error_reason)
        
        else:
            raise Exception(f"Unknown fallback type: {fallback_type}")
    
    def _static_response_fallback(self, config: FallbackConfig) -> Any:
        """Return predefined static response"""
        print(f"📄 Using static response fallback")
        return config.static_data or {"status": "service_unavailable", "message": "Using cached response"}
    
    def _cache_lookup_fallback(self, config: FallbackConfig, cache_key: Optional[str]) -> Any:
        """Look up cached response"""
        if not cache_key:
            raise Exception("Cache key not provided for cache lookup fallback")
        
        cached_result = self.cache.get(cache_key)
        if cached_result is None:
            self.fallback_metrics.cache_misses += 1
            raise Exception("No cached data available")
        
        self.fallback_metrics.cache_hits += 1
        print(f"💾 Using cached response (key: {cache_key})")
        
        # Add cache indicator to response
        if isinstance(cached_result, dict):
            cached_result["_cached"] = True
            cached_result["_cache_time"] = time.time()
        
        return cached_result
    
    def _alternative_service_fallback(self, config: FallbackConfig, args: tuple, kwargs: dict) -> Any:
        """Call alternative service endpoint"""
        if not config.alternative_endpoint:
            raise Exception("Alternative endpoint not configured")
        
        print(f"🔄 Calling alternative service: {config.alternative_endpoint}")
        
        # Simulate alternative service call
        # In real implementation, this would be actual HTTP call
        time.sleep(random.uniform(0.5, 1.5))  # Simulate network delay
        
        if random.random() < 0.8:  # 80% success rate for alternative service
            return {
                "status": "success",
                "data": f"Response from alternative service: {config.alternative_endpoint}",
                "source": "alternative_service",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise Exception("Alternative service also unavailable")
    
    def _queue_for_later_fallback(self, config: FallbackConfig, original_func: Callable, args: tuple, kwargs: dict) -> Any:
        """Queue request for later processing"""
        queue_name = config.queue_name or "default"
        
        if queue_name not in self.request_queues:
            self.request_queues[queue_name] = RequestQueue(queue_name)
        
        queue = self.request_queues[queue_name]
        
        request_data = {
            "function": original_func.__name__,
            "args": args,
            "kwargs": kwargs,
            "priority": config.priority.value,
            "retry_count": config.retry_count,
            "created_at": time.time()
        }
        
        queue.enqueue(request_data)
        self.fallback_metrics.queue_size = sum(q.size() for q in self.request_queues.values())
        
        print(f"📋 Request queued for later processing (queue: {queue_name}, size: {queue.size()})")
        
        return {
            "status": "queued",
            "message": f"Request has been queued for processing. Queue position: {queue.size()}",
            "queue_name": queue_name,
            "estimated_processing_time": queue.size() * 30,  # Rough estimate
            "tracking_id": hashlib.md5(f"{queue_name}_{time.time()}".encode()).hexdigest()[:8]
        }
    
    def _degraded_response_fallback(self, config: FallbackConfig, args: tuple, kwargs: dict) -> Any:
        """Return degraded/simplified response"""
        print(f"⚡ Providing degraded response")
        
        # Simulate creating a simplified response based on request
        degraded_data = {
            "status": "degraded_mode",
            "message": "Service is running in degraded mode. Some features may be limited.",
            "basic_info": "Limited functionality available",
            "retry_after": 300,  # Suggest retry after 5 minutes
            "support_contact": "help@company.com"
        }
        
        # Add any basic processing we can do without external services
        if args:
            degraded_data["request_processed"] = f"Partial processing for: {args[0] if args else 'unknown'}"
        
        return degraded_data
    
    def _user_notification_fallback(self, config: FallbackConfig, error_reason: str) -> Any:
        """Notify user about service unavailability"""
        message = config.notification_message or f"Service '{self.name}' is temporarily unavailable"
        
        print(f"📢 User notification: {message}")
        
        # In real implementation, this might send email, push notification, etc.
        notification_response = {
            "status": "notification_sent",
            "message": message,
            "error_details": error_reason,
            "service": self.name,
            "timestamp": datetime.now().isoformat(),
            "retry_suggested": True,
            "retry_after_seconds": 60,
            "incident_id": f"INC_{int(time.time())}"
        }
        
        return notification_response
    
    def _cache_result(self, cache_key: str, result: Any):
        """Cache successful result"""
        try:
            # Only cache serializable results
            json.dumps(result)  # Test if serializable
            self.cache.set(cache_key, result)
            print(f"💾 Result cached (key: {cache_key})")
        except (TypeError, ValueError):
            print(f"⚠️  Cannot cache non-serializable result")
    
    def _handle_success(self):
        """Handle successful execution"""
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= 3:  # Need 3 successes to close
                self.state = "CLOSED"
                self.failure_count = 0
                self.success_count = 0
                print(f"✅ Circuit '{self.name}' CLOSED - Service recovered")
        elif self.state == "CLOSED":
            self.failure_count = 0  # Reset failure count on success
    
    def _handle_failure(self, error: str):
        """Handle failure and update circuit state"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == "CLOSED" and self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"🔴 Circuit '{self.name}' OPENED after {self.failure_count} failures")
        elif self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.success_count = 0
            print(f"🔴 Circuit '{self.name}' back to OPEN state")
    
    def _update_fallback_metrics(self, fallback_type: FallbackType, success: bool, duration: float):
        """Update fallback execution metrics"""
        if success:
            self.fallback_metrics.successful_fallbacks += 1
        
        # Update type-specific metrics
        type_name = fallback_type.value
        if type_name not in self.fallback_metrics.fallback_by_type:
            self.fallback_metrics.fallback_by_type[type_name] = 0
        self.fallback_metrics.fallback_by_type[type_name] += 1
        
        # Update average duration
        total_fallbacks = self.fallback_metrics.successful_fallbacks + self.fallback_metrics.failed_fallbacks
        if total_fallbacks > 1:
            self.fallback_metrics.avg_fallback_duration = (
                (self.fallback_metrics.avg_fallback_duration * (total_fallbacks - 1) + duration) / total_fallbacks
            )
        else:
            self.fallback_metrics.avg_fallback_duration = duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "fallback_metrics": {
                "total_fallbacks": self.fallback_metrics.total_fallbacks,
                "successful_fallbacks": self.fallback_metrics.successful_fallbacks,
                "failed_fallbacks": self.fallback_metrics.failed_fallbacks,
                "success_rate": (self.fallback_metrics.successful_fallbacks / max(self.fallback_metrics.total_fallbacks, 1)) * 100,
                "avg_fallback_duration": round(self.fallback_metrics.avg_fallback_duration, 3),
                "fallback_by_type": self.fallback_metrics.fallback_by_type,
                "cache_hits": self.fallback_metrics.cache_hits,
                "cache_misses": self.fallback_metrics.cache_misses,
                "cache_hit_rate": (self.fallback_metrics.cache_hits / max(self.fallback_metrics.cache_hits + self.fallback_metrics.cache_misses, 1)) * 100,
                "total_queue_size": self.fallback_metrics.queue_size
            },
            "cache_size": self.cache.size(),
            "queue_info": {name: queue.size() for name, queue in self.request_queues.items()}
        }
    
    def process_queued_requests(self, queue_name: str, max_requests: int = 5) -> List[Dict[str, Any]]:
        """Process queued requests (background job simulation)"""
        if queue_name not in self.request_queues:
            return []
        
        queue = self.request_queues[queue_name]
        processed = []
        
        for _ in range(min(max_requests, queue.size())):
            request = queue.dequeue()
            if request:
                try:
                    # Simulate processing
                    time.sleep(0.5)
                    processed.append({
                        "function": request["function"],
                        "status": "processed",
                        "processed_at": time.time(),
                        "queue_time": time.time() - request["created_at"]
                    })
                except Exception as e:
                    processed.append({
                        "function": request["function"],
                        "status": "failed",
                        "error": str(e),
                        "processed_at": time.time()
                    })
        
        self.fallback_metrics.queue_size = sum(q.size() for q in self.request_queues.values())
        return processed
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get status of all queues"""
        status = {}
        for name, queue in self.request_queues.items():
            status[name] = {
                "size": queue.size(),
                "max_size": queue.max_size,
                "recent_requests": queue.peek(3)
            }
        return status


# Example services and testing
def unreliable_payment_service(order_id: str, amount: float) -> Dict[str, Any]:
    """Simulate unreliable payment service"""
    print(f"💳 Processing payment: Order {order_id}, Amount ${amount}")
    
    # Simulate random failures
    if random.random() < 0.6:  # 60% failure rate
        failure_types = [
            "Payment gateway timeout",
            "Insufficient funds",
            "Card expired",
            "Network error",
            "Service overloaded"
        ]
        raise Exception(random.choice(failure_types))
    
    time.sleep(random.uniform(1.0, 3.0))  # Simulate processing time
    
    return {
        "status": "success",
        "order_id": order_id,
        "amount": amount,
        "transaction_id": f"TXN_{int(time.time())}",
        "timestamp": datetime.now().isoformat()
    }


def unreliable_user_service(user_id: str) -> Dict[str, Any]:
    """Simulate unreliable user service"""
    print(f"👤 Fetching user data: {user_id}")
    
    if random.random() < 0.4:  # 40% failure rate
        raise Exception("User service database connection failed")
    
    time.sleep(random.uniform(0.5, 2.0))
    
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "status": "active"
    }


def test_fallback_mechanisms():
    """Comprehensive test of fallback mechanisms"""
    print("🧪 Testing Fallback Circuit Breaker Mechanisms")
    print("=" * 70)
    
    # Configure multiple fallback strategies
    fallback_configs = [
        # Priority 1: Try cache first
        FallbackConfig(
            fallback_type=FallbackType.CACHE_LOOKUP,
            priority=FallbackPriority.HIGH,
            timeout=1.0
        ),
        
        # Priority 2: Try alternative service
        FallbackConfig(
            fallback_type=FallbackType.ALTERNATIVE_SERVICE,
            priority=FallbackPriority.HIGH,
            timeout=3.0,
            alternative_endpoint="/alternative/payment"
        ),
        
        # Priority 3: Return static response
        FallbackConfig(
            fallback_type=FallbackType.STATIC_RESPONSE,
            priority=FallbackPriority.MEDIUM,
            static_data={
                "status": "accepted",
                "message": "Payment will be processed offline",
                "reference": "OFFLINE_PAYMENT"
            }
        ),
        
        # Priority 4: Queue for later
        FallbackConfig(
            fallback_type=FallbackType.QUEUE_FOR_LATER,
            priority=FallbackPriority.MEDIUM,
            queue_name="payment_queue",
            timeout=1.0
        ),
        
        # Priority 5: User notification
        FallbackConfig(
            fallback_type=FallbackType.USER_NOTIFICATION,
            priority=FallbackPriority.LOW,
            notification_message="Payment service is temporarily down. Please try again in a few minutes."
        )
    ]
    
    # Create circuit breaker with fallbacks
    cb = FallbackCircuitBreaker(
        name="payment-service",
        fallback_configs=fallback_configs,
        failure_threshold=2,
        recovery_timeout=10.0
    )
    
    print("\n📊 Phase 1: Testing normal operation with cache building")
    print("-" * 60)
    
    # First, make some successful calls to build cache
    for i in range(3):
        try:
            cache_key = f"payment_order_{i+1}"
            result = cb.call(
                unreliable_payment_service,
                f"ORDER_{i+1}",
                100.0 + (i * 50),
                cache_key=cache_key
            )
            print(f"✅ Successful payment {i+1}")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Payment {i+1} failed: {str(e)}")
    
    print(f"\n📈 Current cache size: {cb.cache.size()}")
    
    print("\n📊 Phase 2: Testing fallback execution")
    print("-" * 60)
    
    # Force circuit to open by making it fail
    cb.state = "OPEN"
    cb.last_failure_time = time.time()
    
    # Test different fallback scenarios
    test_cases = [
        ("Cached Order", "payment_order_1", "ORDER_CACHED", 150.0),
        ("New Order 1", "payment_order_new1", "ORDER_NEW1", 200.0),
        ("New Order 2", "payment_order_new2", "ORDER_NEW2", 250.0),
        ("New Order 3", "payment_order_new3", "ORDER_NEW3", 300.0),
    ]
    
    for test_name, cache_key, order_id, amount in test_cases:
        try:
            print(f"\n🔄 Testing: {test_name}")
            result = cb.call(
                unreliable_payment_service,
                order_id,
                amount,
                cache_key=cache_key
            )
            
            print(f"✅ {test_name}: {result.get('status', 'unknown')}")
            if '_cached' in result:
                print(f"   💾 Used cached response")
            elif result.get('source') == 'alternative_service':
                print(f"   🔄 Used alternative service")
            elif result.get('status') == 'queued':
                print(f"   📋 Request queued for later")
            
        except Exception as e:
            print(f"❌ {test_name} failed completely: {str(e)}")
        
        time.sleep(1)
    
    print("\n📊 Phase 3: Processing queued requests")
    print("-" * 60)
    
    # Process some queued requests
    processed = cb.process_queued_requests("payment_queue", max_requests=3)
    print(f"Processed {len(processed)} queued requests:")
    for req in processed:
        print(f"   - {req['function']}: {req['status']} (queue time: {req.get('queue_time', 0):.1f}s)")
    
    print("\n📊 Phase 4: Circuit recovery test")
    print("-" * 60)
    
    # Reset circuit to test recovery
    cb.state = "HALF_OPEN"
    cb.success_count = 0
    
    # Try a few calls to test recovery
    for i in range(4):
        try:
            result = cb.call(
                lambda: {"status": "success", "test": f"recovery_{i+1}"},
                cache_key=f"recovery_{i+1}"
            )
            print(f"✅ Recovery test {i+1}: Success")
        except Exception as e:
            print(f"❌ Recovery test {i+1}: {str(e)}")
        
        time.sleep(0.5)
    
    # Final comprehensive metrics
    print("\n📈 Final Comprehensive Metrics:")
    print("=" * 50)
    metrics = cb.get_metrics()
    print(json.dumps(metrics, indent=2, default=str))
    
    print("\n📋 Queue Status:")
    queue_status = cb.get_queue_status()
    print(json.dumps(queue_status, indent=2, default=str))


def test_user_service_fallbacks():
    """Test user service with different fallback strategy"""
    print("\n🧪 Testing User Service Fallbacks")
    print("=" * 60)
    
    # Different fallback strategy for user service
    user_fallback_configs = [
        FallbackConfig(
            fallback_type=FallbackType.CACHE_LOOKUP,
            priority=FallbackPriority.HIGH
        ),
        FallbackConfig(
            fallback_type=FallbackType.DEGRADED_RESPONSE,
            priority=FallbackPriority.MEDIUM
        ),
        FallbackConfig(
            fallback_type=FallbackType.STATIC_RESPONSE,
            priority=FallbackPriority.LOW,
            static_data={
                "user_id": "unknown",
                "name": "Guest User",
                "email": "guest@example.com",
                "status": "limited_access"
            }
        )
    ]
    
    user_cb = FallbackCircuitBreaker(
        name="user-service",
        fallback_configs=user_fallback_configs,
        failure_threshold=2
    )
    
    # Test user service with fallbacks
    for i in range(5):
        try:
            cache_key = f"user_{i+1}"
            result = user_cb.call(
                unreliable_user_service,
                f"USER_{i+1}",
                cache_key=cache_key
            )
            print(f"✅ User {i+1}: {result.get('name', 'Unknown')}")
        except Exception as e:
            print(f"❌ User {i+1} failed: {str(e)}")
        
        time.sleep(1)
    
    print("\n📈 User Service Metrics:")
    user_metrics = user_cb.get_metrics()
    print(json.dumps(user_metrics, indent=2, default=str))


if __name__ == "__main__":
    # Test payment service fallbacks
    test_fallback_mechanisms()
    
    # Test user service fallbacks
    test_user_service_fallbacks()