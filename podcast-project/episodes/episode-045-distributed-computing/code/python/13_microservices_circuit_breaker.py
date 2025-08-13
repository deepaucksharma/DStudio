#!/usr/bin/env python3
"""
Microservices Circuit Breaker Pattern Implementation
Episode 45: Distributed Computing at Scale

यह example microservices के बीच circuit breaker pattern दिखाता है
Service-to-service communication में fault tolerance, automatic recovery,
और cascading failure prevention के साथ।

Production Stats:
- Netflix: 1000+ microservices with circuit breakers
- Hystrix library: Prevents 99.5% of cascading failures
- Recovery time: <30 seconds for failed services
- Latency reduction: 40% during service failures
- Indian companies: Flipkart, PhonePe, Ola use similar patterns
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"        # Normal operation
    OPEN = "OPEN"           # Circuit is open, requests fail fast
    HALF_OPEN = "HALF_OPEN" # Testing if service has recovered

class ServiceHealth(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    RECOVERING = "RECOVERING"

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Failures before opening circuit
    success_threshold: int = 3          # Successes before closing circuit
    timeout_duration: int = 60          # Seconds to wait before trying again
    request_volume_threshold: int = 10  # Minimum requests in window
    window_duration: int = 60           # Sliding window duration in seconds
    slow_call_duration_threshold: float = 5.0  # Seconds to consider call slow
    slow_call_rate_threshold: float = 0.5      # % of slow calls to open circuit

@dataclass
class CallResult:
    """Result of a service call"""
    success: bool
    duration_ms: float
    timestamp: datetime
    error_message: Optional[str] = None
    response_data: Any = None

class RollingWindow:
    """Rolling window for tracking call statistics"""
    
    def __init__(self, window_duration: int = 60):
        self.window_duration = window_duration
        self.calls = deque()  # (timestamp, CallResult)
        self.lock = threading.RLock()
    
    def add_call(self, result: CallResult):
        """Add call result to window"""
        with self.lock:
            now = datetime.now()
            self.calls.append((now, result))
            self._cleanup_old_calls(now)
    
    def _cleanup_old_calls(self, current_time: datetime):
        """Remove calls outside the window"""
        cutoff_time = current_time - timedelta(seconds=self.window_duration)
        while self.calls and self.calls[0][0] < cutoff_time:
            self.calls.popleft()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for current window"""
        with self.lock:
            now = datetime.now()
            self._cleanup_old_calls(now)
            
            if not self.calls:
                return {
                    "total_calls": 0,
                    "failure_count": 0,
                    "success_count": 0,
                    "failure_rate": 0.0,
                    "slow_call_count": 0,
                    "slow_call_rate": 0.0,
                    "avg_duration_ms": 0.0
                }
            
            results = [call_result for _, call_result in self.calls]
            
            total_calls = len(results)
            failure_count = sum(1 for r in results if not r.success)
            success_count = total_calls - failure_count
            slow_call_count = sum(1 for r in results if r.duration_ms > 5000)  # 5 seconds
            
            durations = [r.duration_ms for r in results]
            avg_duration = statistics.mean(durations) if durations else 0.0
            
            return {
                "total_calls": total_calls,
                "failure_count": failure_count,
                "success_count": success_count,
                "failure_rate": failure_count / total_calls if total_calls > 0 else 0.0,
                "slow_call_count": slow_call_count,
                "slow_call_rate": slow_call_count / total_calls if total_calls > 0 else 0.0,
                "avg_duration_ms": avg_duration
            }

class CircuitBreaker:
    """Circuit breaker implementation for service calls"""
    
    def __init__(self, service_name: str, config: CircuitBreakerConfig = None):
        self.service_name = service_name
        self.config = config or CircuitBreakerConfig()
        
        # Circuit state
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.half_open_calls = 0
        
        # Statistics tracking
        self.rolling_window = RollingWindow(self.config.window_duration)
        
        # Performance metrics
        self.total_calls = 0
        self.total_failures = 0
        self.circuit_opens = 0
        self.fallback_calls = 0
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info(f"🔧 Circuit breaker initialized for service: {service_name}")
    
    async def call(self, service_func: Callable, *args, fallback_func: Callable = None, **kwargs) -> Any:
        """Execute service call with circuit breaker protection"""
        with self.lock:
            self.total_calls += 1
            
            # Check if circuit should be opened based on current stats
            self._update_circuit_state()
            
            if self.state == CircuitState.OPEN:
                # Circuit is open, fail fast
                if fallback_func:
                    logger.warning(f"⚡ Circuit OPEN for {self.service_name}, using fallback")
                    self.fallback_calls += 1
                    return await self._execute_fallback(fallback_func, *args, **kwargs)
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {self.service_name}")
            
            elif self.state == CircuitState.HALF_OPEN:
                # Circuit is half-open, allow limited calls
                if self.half_open_calls >= self.config.success_threshold:
                    # Too many test calls, fall back to open state
                    self.state = CircuitState.OPEN
                    self.last_failure_time = datetime.now()
                    if fallback_func:
                        logger.warning(f"⚡ Circuit HALF_OPEN limit reached for {self.service_name}, using fallback")
                        self.fallback_calls += 1
                        return await self._execute_fallback(fallback_func, *args, **kwargs)
                    else:
                        raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {self.service_name}")
        
        # Execute the actual service call
        return await self._execute_call(service_func, fallback_func, *args, **kwargs)
    
    async def _execute_call(self, service_func: Callable, fallback_func: Callable, *args, **kwargs) -> Any:
        """Execute the actual service call"""
        start_time = time.time()
        call_result = None
        
        try:
            # Execute service function
            if asyncio.iscoroutinefunction(service_func):
                response = await service_func(*args, **kwargs)
            else:
                response = service_func(*args, **kwargs)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Record successful call
            call_result = CallResult(
                success=True,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                response_data=response
            )
            
            self.rolling_window.add_call(call_result)
            
            # Update circuit state for successful call
            with self.lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.half_open_calls += 1
                    # Check if we've had enough successes to close circuit
                    stats = self.rolling_window.get_stats()
                    recent_successes = stats["success_count"]
                    if recent_successes >= self.config.success_threshold:
                        self.state = CircuitState.CLOSED
                        self.half_open_calls = 0
                        logger.info(f"✅ Circuit CLOSED for {self.service_name} after recovery")
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Record failed call
            call_result = CallResult(
                success=False,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                error_message=str(e)
            )
            
            self.rolling_window.add_call(call_result)
            
            # Update failure count
            with self.lock:
                self.total_failures += 1
                self.last_failure_time = datetime.now()
                
                # Reset half-open counter on failure
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                    self.half_open_calls = 0
                    logger.warning(f"❌ Circuit reopened for {self.service_name} due to failure in HALF_OPEN state")
            
            # Use fallback if available
            if fallback_func:
                logger.warning(f"⚠️ Service call failed for {self.service_name}, using fallback: {str(e)}")
                self.fallback_calls += 1
                return await self._execute_fallback(fallback_func, *args, **kwargs)
            else:
                raise e
    
    async def _execute_fallback(self, fallback_func: Callable, *args, **kwargs) -> Any:
        """Execute fallback function"""
        try:
            if asyncio.iscoroutinefunction(fallback_func):
                return await fallback_func(*args, **kwargs)
            else:
                return fallback_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Fallback function failed for {self.service_name}: {str(e)}")
            raise e
    
    def _update_circuit_state(self):
        """Update circuit breaker state based on current statistics"""
        stats = self.rolling_window.get_stats()
        
        if self.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            should_open = False
            
            # Check failure rate
            if (stats["total_calls"] >= self.config.request_volume_threshold and
                stats["failure_rate"] >= 0.5):  # 50% failure rate
                should_open = True
                logger.warning(f"⚠️ High failure rate detected for {self.service_name}: {stats['failure_rate']:.2%}")
            
            # Check slow call rate
            if (stats["total_calls"] >= self.config.request_volume_threshold and
                stats["slow_call_rate"] >= self.config.slow_call_rate_threshold):
                should_open = True
                logger.warning(f"⚠️ High slow call rate detected for {self.service_name}: {stats['slow_call_rate']:.2%}")
            
            # Check consecutive failures
            if stats["failure_count"] >= self.config.failure_threshold:
                should_open = True
                logger.warning(f"⚠️ Failure threshold exceeded for {self.service_name}: {stats['failure_count']} failures")
            
            if should_open:
                self.state = CircuitState.OPEN
                self.last_failure_time = datetime.now()
                self.circuit_opens += 1
                logger.error(f"🔴 Circuit OPENED for {self.service_name}")
        
        elif self.state == CircuitState.OPEN:
            # Check if we should try half-open
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time >= timedelta(seconds=self.config.timeout_duration)):
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"🟡 Circuit HALF_OPEN for {self.service_name}, testing recovery")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker statistics"""
        window_stats = self.rolling_window.get_stats()
        
        with self.lock:
            return {
                "service_name": self.service_name,
                "state": self.state.value,
                "total_calls": self.total_calls,
                "total_failures": self.total_failures,
                "circuit_opens": self.circuit_opens,
                "fallback_calls": self.fallback_calls,
                "success_rate": ((self.total_calls - self.total_failures) / max(self.total_calls, 1)) * 100,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "window_stats": window_stats,
                "config": asdict(self.config)
            }
    
    def reset(self):
        """Reset circuit breaker to CLOSED state"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.last_failure_time = None
            self.half_open_calls = 0
            logger.info(f"🔄 Circuit breaker reset for {self.service_name}")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

# Simulated microservices for Indian applications
class PaymentService:
    """Simulated payment service (like Razorpay/Paytm)"""
    
    def __init__(self):
        self.service_name = "PaymentService"
        self.is_healthy = True
        self.failure_rate = 0.1  # 10% failure rate
        self.latency_ms = 100
        
    async def process_payment(self, amount: float, payment_method: str) -> Dict[str, Any]:
        """Process payment with simulated failures"""
        # Simulate varying latency
        base_latency = self.latency_ms / 1000
        actual_latency = base_latency + random.uniform(0, base_latency)
        await asyncio.sleep(actual_latency)
        
        # Simulate failures
        if not self.is_healthy or random.random() < self.failure_rate:
            raise Exception(f"Payment service unavailable: High load on {payment_method} gateway")
        
        return {
            "transaction_id": f"TXN_{int(time.time())}{random.randint(1000, 9999)}",
            "amount": amount,
            "payment_method": payment_method,
            "status": "SUCCESS",
            "gateway_response_time": actual_latency * 1000
        }
    
    def set_health(self, healthy: bool, failure_rate: float = 0.1, latency_ms: int = 100):
        """Simulate service health changes"""
        self.is_healthy = healthy
        self.failure_rate = failure_rate
        self.latency_ms = latency_ms
        logger.info(f"🏥 {self.service_name} health: {'Healthy' if healthy else 'Unhealthy'}, "
                   f"failure_rate: {failure_rate:.1%}, latency: {latency_ms}ms")

class InventoryService:
    """Simulated inventory service (like Flipkart inventory)"""
    
    def __init__(self):
        self.service_name = "InventoryService"
        self.is_healthy = True
        self.failure_rate = 0.05
        self.latency_ms = 200
        
    async def check_availability(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Check product availability"""
        base_latency = self.latency_ms / 1000
        actual_latency = base_latency + random.uniform(0, base_latency * 0.5)
        await asyncio.sleep(actual_latency)
        
        if not self.is_healthy or random.random() < self.failure_rate:
            raise Exception("Inventory service timeout: Database connection issues")
        
        available = random.randint(0, quantity + 10)
        
        return {
            "product_id": product_id,
            "requested_quantity": quantity,
            "available_quantity": available,
            "can_fulfill": available >= quantity,
            "warehouse_location": random.choice(["Mumbai", "Delhi", "Bangalore"]),
            "response_time": actual_latency * 1000
        }
    
    def set_health(self, healthy: bool, failure_rate: float = 0.05, latency_ms: int = 200):
        self.is_healthy = healthy
        self.failure_rate = failure_rate
        self.latency_ms = latency_ms
        logger.info(f"🏥 {self.service_name} health: {'Healthy' if healthy else 'Unhealthy'}, "
                   f"failure_rate: {failure_rate:.1%}, latency: {latency_ms}ms")

class NotificationService:
    """Simulated notification service (SMS/Email)"""
    
    def __init__(self):
        self.service_name = "NotificationService"
        self.is_healthy = True
        self.failure_rate = 0.15
        self.latency_ms = 300
        
    async def send_notification(self, user_id: str, message: str, channel: str) -> Dict[str, Any]:
        """Send notification to user"""
        base_latency = self.latency_ms / 1000
        actual_latency = base_latency + random.uniform(0, base_latency * 0.3)
        await asyncio.sleep(actual_latency)
        
        if not self.is_healthy or random.random() < self.failure_rate:
            raise Exception(f"Notification service failed: {channel} gateway error")
        
        return {
            "notification_id": str(uuid.uuid4()),
            "user_id": user_id,
            "channel": channel,
            "status": "SENT",
            "delivery_time": actual_latency * 1000
        }
    
    def set_health(self, healthy: bool, failure_rate: float = 0.15, latency_ms: int = 300):
        self.is_healthy = healthy
        self.failure_rate = failure_rate
        self.latency_ms = latency_ms
        logger.info(f"🏥 {self.service_name} health: {'Healthy' if healthy else 'Unhealthy'}, "
                   f"failure_rate: {failure_rate:.1%}, latency: {latency_ms}ms")

class OrderProcessingService:
    """Main service that orchestrates other services with circuit breakers"""
    
    def __init__(self):
        # Initialize services
        self.payment_service = PaymentService()
        self.inventory_service = InventoryService()
        self.notification_service = NotificationService()
        
        # Initialize circuit breakers
        self.payment_circuit = CircuitBreaker(
            "PaymentService",
            CircuitBreakerConfig(
                failure_threshold=3,
                success_threshold=2,
                timeout_duration=30,
                request_volume_threshold=5
            )
        )
        
        self.inventory_circuit = CircuitBreaker(
            "InventoryService",
            CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=3,
                timeout_duration=45,
                request_volume_threshold=8
            )
        )
        
        self.notification_circuit = CircuitBreaker(
            "NotificationService",
            CircuitBreakerConfig(
                failure_threshold=4,
                success_threshold=2,
                timeout_duration=60,
                request_volume_threshold=6
            )
        )
        
        # Performance metrics
        self.total_orders = 0
        self.successful_orders = 0
        self.failed_orders = 0
        
        logger.info("🛒 Order Processing Service initialized with circuit breakers")
    
    async def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process order with circuit breaker protection"""
        order_id = order_data.get("order_id", str(uuid.uuid4()))
        self.total_orders += 1
        
        logger.info(f"🛒 Processing order {order_id}")
        
        order_result = {
            "order_id": order_id,
            "status": "PROCESSING",
            "steps": {},
            "fallbacks_used": [],
            "total_time_ms": 0,
            "errors": []
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Check inventory with circuit breaker
            inventory_result = await self.inventory_circuit.call(
                self.inventory_service.check_availability,
                order_data["product_id"],
                order_data["quantity"],
                fallback_func=self._inventory_fallback
            )
            
            order_result["steps"]["inventory"] = inventory_result
            
            if isinstance(inventory_result, dict) and not inventory_result.get("can_fulfill", False):
                order_result["status"] = "FAILED"
                order_result["errors"].append("Insufficient inventory")
                self.failed_orders += 1
                return order_result
            
            # Step 2: Process payment with circuit breaker
            payment_result = await self.payment_circuit.call(
                self.payment_service.process_payment,
                order_data["amount"],
                order_data["payment_method"],
                fallback_func=self._payment_fallback
            )
            
            order_result["steps"]["payment"] = payment_result
            
            # Step 3: Send notification with circuit breaker (non-critical)
            try:
                notification_result = await self.notification_circuit.call(
                    self.notification_service.send_notification,
                    order_data["user_id"],
                    f"Order {order_id} confirmed",
                    "SMS",
                    fallback_func=self._notification_fallback
                )
                order_result["steps"]["notification"] = notification_result
            except Exception as e:
                # Notification failure shouldn't fail the order
                order_result["steps"]["notification"] = {"error": str(e), "fallback": True}
                order_result["fallbacks_used"].append("notification")
            
            order_result["status"] = "SUCCESS"
            self.successful_orders += 1
            
        except Exception as e:
            order_result["status"] = "FAILED"
            order_result["errors"].append(str(e))
            self.failed_orders += 1
        
        order_result["total_time_ms"] = (time.time() - start_time) * 1000
        
        return order_result
    
    async def _inventory_fallback(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Fallback for inventory service"""
        logger.warning(f"🔄 Using inventory fallback for product {product_id}")
        # Return cached/estimated data
        return {
            "product_id": product_id,
            "requested_quantity": quantity,
            "available_quantity": quantity,  # Optimistic assumption
            "can_fulfill": True,
            "warehouse_location": "Cache",
            "fallback": True,
            "response_time": 10  # Fast fallback
        }
    
    async def _payment_fallback(self, amount: float, payment_method: str) -> Dict[str, Any]:
        """Fallback for payment service"""
        logger.warning(f"🔄 Using payment fallback for ₹{amount}")
        # Could queue for later processing or use alternative gateway
        return {
            "transaction_id": f"FALLBACK_{int(time.time())}{random.randint(1000, 9999)}",
            "amount": amount,
            "payment_method": "FALLBACK_QUEUE",
            "status": "QUEUED",
            "fallback": True,
            "gateway_response_time": 50
        }
    
    async def _notification_fallback(self, user_id: str, message: str, channel: str) -> Dict[str, Any]:
        """Fallback for notification service"""
        logger.warning(f"🔄 Using notification fallback for user {user_id}")
        # Could queue for later or use alternative channel
        return {
            "notification_id": f"FALLBACK_{str(uuid.uuid4())}",
            "user_id": user_id,
            "channel": "FALLBACK_QUEUE",
            "status": "QUEUED",
            "fallback": True,
            "delivery_time": 20
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        return {
            "order_processing": {
                "total_orders": self.total_orders,
                "successful_orders": self.successful_orders,
                "failed_orders": self.failed_orders,
                "success_rate": (self.successful_orders / max(self.total_orders, 1)) * 100
            },
            "circuit_breakers": {
                "payment": self.payment_circuit.get_stats(),
                "inventory": self.inventory_circuit.get_stats(),
                "notification": self.notification_circuit.get_stats()
            }
        }
    
    def print_dashboard(self):
        """Print service dashboard"""
        stats = self.get_service_stats()
        
        print(f"\n{'='*80}")
        print(f"🛒 MICROSERVICES CIRCUIT BREAKER DASHBOARD 🛒")
        print(f"{'='*80}")
        
        order_stats = stats["order_processing"]
        print(f"📊 Order Processing:")
        print(f"   Total Orders: {order_stats['total_orders']:,}")
        print(f"   Successful: {order_stats['successful_orders']:,}")
        print(f"   Failed: {order_stats['failed_orders']:,}")
        print(f"   Success Rate: {order_stats['success_rate']:.1f}%")
        
        print(f"\n🔧 Circuit Breaker Status:")
        for service_name, cb_stats in stats["circuit_breakers"].items():
            print(f"   {service_name.title()} Service:")
            print(f"     State: {cb_stats['state']}")
            print(f"     Total Calls: {cb_stats['total_calls']:,}")
            print(f"     Success Rate: {cb_stats['success_rate']:.1f}%")
            print(f"     Circuit Opens: {cb_stats['circuit_opens']}")
            print(f"     Fallback Calls: {cb_stats['fallback_calls']}")
            
            window_stats = cb_stats['window_stats']
            print(f"     Window Stats:")
            print(f"       Recent Calls: {window_stats['total_calls']}")
            print(f"       Failure Rate: {window_stats['failure_rate']:.1%}")
            print(f"       Avg Duration: {window_stats['avg_duration_ms']:.1f}ms")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
    
    def simulate_service_issues(self):
        """Simulate various service health issues"""
        # Randomly affect services
        services = [
            (self.payment_service, "Payment"),
            (self.inventory_service, "Inventory"), 
            (self.notification_service, "Notification")
        ]
        
        affected_service, service_name = random.choice(services)
        
        issue_type = random.choice(["high_latency", "high_failure_rate", "complete_failure"])
        
        if issue_type == "high_latency":
            affected_service.set_health(True, 0.1, 3000)  # High latency
            logger.warning(f"⚠️ {service_name} service experiencing high latency")
        elif issue_type == "high_failure_rate":
            affected_service.set_health(True, 0.8, 200)  # High failure rate
            logger.warning(f"⚠️ {service_name} service experiencing high failure rate")
        else:  # complete_failure
            affected_service.set_health(False, 1.0, 100)  # Complete failure
            logger.error(f"❌ {service_name} service completely down")

async def simulate_ecommerce_traffic(order_service: OrderProcessingService, duration_minutes: int = 5):
    """Simulate e-commerce traffic with service failures"""
    logger.info(f"🛒 Starting e-commerce traffic simulation for {duration_minutes} minutes")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    order_count = 0
    
    # Product data for Indian e-commerce
    products = [
        {"id": "PHONE001", "name": "iPhone 15", "price": 80000},
        {"id": "LAPTOP001", "name": "MacBook Air", "price": 120000},
        {"id": "BOOK001", "name": "System Design", "price": 500},
        {"id": "CLOTH001", "name": "Cotton Shirt", "price": 1200},
        {"id": "ELECT001", "name": "Smart TV", "price": 45000}
    ]
    
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]
    
    try:
        while time.time() < end_time:
            # Simulate varying load
            current_hour = datetime.now().hour
            
            if 12 <= current_hour <= 14 or 19 <= current_hour <= 22:
                # Peak hours
                orders_per_second = random.randint(5, 15)
            else:
                # Normal hours
                orders_per_second = random.randint(2, 8)
            
            # Process batch of orders
            tasks = []
            for _ in range(orders_per_second):
                product = random.choice(products)
                
                order_data = {
                    "order_id": f"ORD_{int(time.time())}{random.randint(1000, 9999)}",
                    "user_id": f"user_{random.randint(10000, 99999)}",
                    "product_id": product["id"],
                    "quantity": random.randint(1, 3),
                    "amount": product["price"],
                    "payment_method": random.choice(payment_methods)
                }
                
                task = order_service.process_order(order_data)
                tasks.append(task)
                order_count += 1
            
            # Execute orders concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log interesting events
                for result in results:
                    if isinstance(result, dict):
                        if result.get("fallbacks_used"):
                            logger.info(f"🔄 Order {result['order_id']} used fallbacks: {result['fallbacks_used']}")
                        if result.get("total_time_ms", 0) > 5000:
                            logger.warning(f"⏰ Slow order: {result['order_id']} took {result['total_time_ms']:.0f}ms")
            
            # Randomly introduce service issues
            if random.random() < 0.05:  # 5% chance every second
                order_service.simulate_service_issues()
            
            # Randomly recover services
            if random.random() < 0.03:  # 3% chance every second
                services = [order_service.payment_service, order_service.inventory_service, order_service.notification_service]
                recovering_service = random.choice(services)
                recovering_service.set_health(True, 0.05, 200)  # Back to healthy
                logger.info(f"✅ Service {recovering_service.service_name} recovered")
            
            # Print dashboard every 30 seconds
            if order_count % 50 == 0:
                order_service.print_dashboard()
            
            await asyncio.sleep(1.0)
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    
    logger.info(f"🏁 E-commerce simulation completed! Processed {order_count} orders")
    
    # Final dashboard
    order_service.print_dashboard()

async def main():
    """Main demo function"""
    print("🇮🇳 Microservices Circuit Breaker System")
    print("🔧 Fault-tolerant service communication with automatic recovery")
    print("🛒 E-commerce order processing with payment, inventory, और notification services...\n")
    
    # Initialize order processing service
    order_service = OrderProcessingService()
    
    try:
        # Show initial dashboard
        order_service.print_dashboard()
        
        # Run e-commerce simulation
        await simulate_ecommerce_traffic(order_service, duration_minutes=3)
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"💡 Production system capabilities:")
        print(f"   - Prevent cascading failures across microservices")
        print(f"   - Automatic recovery testing और circuit closure")
        print(f"   - Fallback mechanisms for critical operations")
        print(f"   - Real-time health monitoring और alerting")
        print(f"   - Configurable failure thresholds और timeouts")
        print(f"   - Performance metrics और observability")
        
    except Exception as e:
        logger.error(f"❌ Error in simulation: {e}")

if __name__ == "__main__":
    # Run the microservices circuit breaker demo
    asyncio.run(main())