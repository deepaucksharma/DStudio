#!/usr/bin/env python3
"""
Circuit Breaker Pattern Implementation - Zomato Style
Cloud Native Resilience Pattern for Microservices

Zomato ke food delivery system mein circuit breaker implementation
Restaurant services fail hone par user experience protect karta hai
"""

import time
import threading
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import requests
from concurrent.futures import ThreadPoolExecutor
import json


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation - requests allowed
    OPEN = "open"          # Circuit broken - requests blocked
    HALF_OPEN = "half_open"  # Testing - limited requests allowed


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5          # Failures needed to open circuit
    recovery_timeout: int = 60          # Seconds before attempting recovery
    expected_exception: Exception = Exception  # Exception type to track
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 5.0                # Request timeout in seconds
    monitor_window: int = 60            # Monitoring window in seconds


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics and statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    state_changes: Dict[str, int] = field(default_factory=lambda: {
        'closed_to_open': 0,
        'open_to_half_open': 0,
        'half_open_to_closed': 0,
        'half_open_to_open': 0
    })
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    average_response_time: float = 0.0
    current_failure_count: int = 0
    
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100


class ZomatoCircuitBreaker:
    """
    Circuit Breaker implementation for Zomato services
    Mumbai mein restaurant down ho gaya toh user ko proper message show karna hai
    """
    
    def __init__(self, service_name: str, config: CircuitBreakerConfig = None):
        self.service_name = service_name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.lock = threading.RLock()
        self.last_failure_time = None
        self.consecutive_successes = 0
        
        # Setup logging
        self.logger = logging.getLogger(f"circuit-breaker-{service_name}")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{service_name}] %(asctime)s %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info(f"🔌 Circuit Breaker initialized for {service_name}")
        self.logger.info(f"⚙️  Config: failure_threshold={self.config.failure_threshold}, "
                        f"timeout={self.config.recovery_timeout}s")
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker"""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        
        wrapper._circuit_breaker = self
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        Zomato mein restaurant API call karte waqt protection lagana
        """
        with self.lock:
            self.metrics.total_requests += 1
            
            # Check circuit state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.logger.warning(f"🚫 Circuit OPEN - Request blocked for {self.service_name}")
                    raise CircuitOpenException(
                        f"Circuit breaker is OPEN for {self.service_name}. "
                        f"Service unavailable. Try again in {self._time_until_reset():.0f} seconds."
                    )
            
            # Execute the function
            start_time = time.time()
            
            try:
                # Add timeout to the call
                result = self._execute_with_timeout(func, args, kwargs)
                
                execution_time = time.time() - start_time
                self._on_success(execution_time)
                
                return result
                
            except self.config.expected_exception as e:
                execution_time = time.time() - start_time
                self._on_failure(e, execution_time)
                raise
    
    def _execute_with_timeout(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """Execute function with timeout"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=self.config.timeout)
            except TimeoutError:
                self.metrics.timeouts += 1
                self.logger.error(f"⏰ Timeout executing {func.__name__} for {self.service_name}")
                raise CircuitTimeoutException(f"Function call timed out after {self.config.timeout}s")
    
    def _on_success(self, execution_time: float):
        """Handle successful execution"""
        self.metrics.successful_requests += 1
        self.metrics.last_success_time = datetime.utcnow()
        
        # Update average response time
        total_time = self.metrics.average_response_time * (self.metrics.successful_requests - 1)
        self.metrics.average_response_time = (total_time + execution_time) / self.metrics.successful_requests
        
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            self.logger.info(f"✅ Success in HALF-OPEN state ({self.consecutive_successes}/{self.config.success_threshold})")
            
            if self.consecutive_successes >= self.config.success_threshold:
                self._transition_to_closed()
        
        self.logger.debug(f"✅ Success - {self.service_name} ({execution_time:.3f}s)")
    
    def _on_failure(self, exception: Exception, execution_time: float):
        """Handle failed execution"""
        self.metrics.failed_requests += 1
        self.metrics.current_failure_count += 1
        self.metrics.last_failure_time = datetime.utcnow()
        self.last_failure_time = time.time()
        
        self.logger.error(f"❌ Failure - {self.service_name}: {str(exception)} ({execution_time:.3f}s)")
        
        if self.state == CircuitState.HALF_OPEN:
            self.logger.warning(f"🔄 Failure in HALF-OPEN state - returning to OPEN")
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            if self.metrics.current_failure_count >= self.config.failure_threshold:
                self.logger.error(f"🚨 Failure threshold reached - opening circuit")
                self._transition_to_open()
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout
    
    def _time_until_reset(self) -> float:
        """Time remaining until reset attempt"""
        if self.last_failure_time is None:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, self.config.recovery_timeout - elapsed)
    
    def _transition_to_open(self):
        """Transition circuit to OPEN state"""
        old_state = self.state.value
        self.state = CircuitState.OPEN
        self.consecutive_successes = 0
        self.metrics.state_changes[f'{old_state}_to_open'] += 1
        
        self.logger.error(f"🔴 Circuit OPEN - {self.service_name} is unavailable")
        self.logger.error(f"📊 Metrics: Success Rate: {self.metrics.success_rate():.1f}%, "
                         f"Failures: {self.metrics.current_failure_count}")
    
    def _transition_to_half_open(self):
        """Transition circuit to HALF-OPEN state"""
        old_state = self.state.value
        self.state = CircuitState.HALF_OPEN
        self.consecutive_successes = 0
        self.metrics.current_failure_count = 0  # Reset failure count
        self.metrics.state_changes[f'{old_state}_to_half_open'] += 1
        
        self.logger.warning(f"🟡 Circuit HALF-OPEN - Testing {self.service_name} recovery")
    
    def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        old_state = self.state.value
        self.state = CircuitState.CLOSED
        self.consecutive_successes = 0
        self.metrics.current_failure_count = 0
        self.metrics.state_changes[f'{old_state}_to_closed'] += 1
        
        self.logger.info(f"🟢 Circuit CLOSED - {self.service_name} is healthy again")
        self.logger.info(f"📊 Recovery confirmed after {self.config.success_threshold} successful calls")
    
    def get_metrics(self) -> Dict:
        """Get circuit breaker metrics"""
        with self.lock:
            return {
                'service_name': self.service_name,
                'state': self.state.value,
                'metrics': {
                    'total_requests': self.metrics.total_requests,
                    'successful_requests': self.metrics.successful_requests,
                    'failed_requests': self.metrics.failed_requests,
                    'timeouts': self.metrics.timeouts,
                    'success_rate_percent': self.metrics.success_rate(),
                    'current_failure_count': self.metrics.current_failure_count,
                    'average_response_time_ms': self.metrics.average_response_time * 1000
                },
                'state_changes': self.metrics.state_changes.copy(),
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout_seconds': self.config.recovery_timeout,
                    'success_threshold': self.config.success_threshold,
                    'timeout_seconds': self.config.timeout
                },
                'timing': {
                    'last_failure': self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
                    'last_success': self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None,
                    'time_until_reset_seconds': self._time_until_reset() if self.state == CircuitState.OPEN else 0
                }
            }
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        with self.lock:
            old_state = self.state.value
            self.state = CircuitState.CLOSED
            self.metrics.current_failure_count = 0
            self.consecutive_successes = 0
            self.last_failure_time = None
            
            self.logger.info(f"🔄 Circuit breaker manually reset from {old_state} to CLOSED")


# Custom Exceptions
class CircuitOpenException(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitTimeoutException(Exception):
    """Raised when function execution times out"""
    pass


# Zomato Service Classes
class ZomatoRestaurantService:
    """
    Zomato restaurant service with circuit breaker protection
    Mumbai ke restaurants ki API calls ko protect karta hai
    """
    
    def __init__(self):
        # Create circuit breakers for different restaurant operations
        self.menu_circuit = ZomatoCircuitBreaker(
            "restaurant-menu-service",
            CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30)
        )
        
        self.availability_circuit = ZomatoCircuitBreaker(
            "restaurant-availability-service", 
            CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60)
        )
        
        self.order_circuit = ZomatoCircuitBreaker(
            "restaurant-order-service",
            CircuitBreakerConfig(failure_threshold=2, recovery_timeout=45, timeout=10.0)
        )
        
        self.logger = logging.getLogger("zomato-restaurant-service")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    @property
    def get_menu(self):
        """Get restaurant menu with circuit breaker protection"""
        @self.menu_circuit
        def _get_menu(restaurant_id: str) -> Dict:
            """
            Fetch restaurant menu
            Mumbai mein restaurant ka menu fetch karna - kabhi kabhi fail ho sakta hai
            """
            self.logger.info(f"🍽️  Fetching menu for restaurant {restaurant_id}")
            
            # Simulate API call that sometimes fails
            if random.random() < 0.2:  # 20% failure rate
                raise requests.RequestException("Menu service unavailable")
            
            # Simulate some processing time
            time.sleep(random.uniform(0.1, 0.5))
            
            return {
                'restaurant_id': restaurant_id,
                'menu': [
                    {'item': 'Butter Chicken', 'price': 280, 'available': True},
                    {'item': 'Biryani', 'price': 320, 'available': True},
                    {'item': 'Paneer Tikka', 'price': 250, 'available': True}
                ],
                'currency': 'INR',
                'last_updated': datetime.utcnow().isoformat()
            }
        
        return _get_menu
    
    @property 
    def check_availability(self):
        """Check restaurant availability with circuit breaker"""
        @self.availability_circuit
        def _check_availability(restaurant_id: str, items: list) -> Dict:
            """
            Check item availability
            Peak hours mein availability service slow ho sakti hai
            """
            self.logger.info(f"📋 Checking availability for restaurant {restaurant_id}")
            
            # Simulate higher failure rate during peak hours
            current_hour = datetime.now().hour
            failure_rate = 0.3 if 12 <= current_hour <= 14 or 19 <= current_hour <= 21 else 0.1
            
            if random.random() < failure_rate:
                raise requests.RequestException("Availability service overloaded")
            
            # Simulate processing time
            time.sleep(random.uniform(0.2, 0.8))
            
            availability = {}
            for item in items:
                availability[item] = {
                    'available': random.random() > 0.1,  # 90% items available
                    'quantity': random.randint(1, 10),
                    'estimated_time_minutes': random.randint(15, 45)
                }
            
            return {
                'restaurant_id': restaurant_id,
                'availability': availability,
                'peak_hours': 12 <= current_hour <= 14 or 19 <= current_hour <= 21,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return _check_availability
    
    @property
    def place_order(self):
        """Place order with circuit breaker protection"""
        @self.order_circuit
        def _place_order(restaurant_id: str, order_items: list, customer_info: dict) -> Dict:
            """
            Place order at restaurant
            Order placement critical operation hai - failures kam tolerance
            """
            self.logger.info(f"🛒 Placing order at restaurant {restaurant_id}")
            
            # Simulate occasional failures
            if random.random() < 0.15:  # 15% failure rate
                raise requests.RequestException("Order placement failed")
            
            # Simulate longer processing for orders
            time.sleep(random.uniform(0.5, 2.0))
            
            order_id = f"ORD_{restaurant_id}_{int(time.time())}"
            total_amount = sum(item.get('price', 0) * item.get('quantity', 1) for item in order_items)
            
            return {
                'order_id': order_id,
                'restaurant_id': restaurant_id,
                'items': order_items,
                'total_amount': total_amount,
                'currency': 'INR',
                'status': 'confirmed',
                'estimated_delivery_time': datetime.utcnow() + timedelta(minutes=random.randint(25, 45)),
                'customer': customer_info,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return _place_order
    
    def get_all_circuit_metrics(self) -> Dict:
        """Get metrics for all circuit breakers"""
        return {
            'menu_service': self.menu_circuit.get_metrics(),
            'availability_service': self.availability_circuit.get_metrics(),
            'order_service': self.order_circuit.get_metrics()
        }


# Demo and Testing Functions
def demonstrate_zomato_circuit_breakers():
    """
    Demonstrate circuit breaker patterns in Zomato service
    Mumbai ke restaurants ke saath testing karte hain
    """
    print("🍕 Starting Zomato Circuit Breaker Demonstration")
    print("=" * 60)
    
    # Initialize restaurant service
    restaurant_service = ZomatoRestaurantService()
    
    # Test restaurant IDs
    mumbai_restaurants = [
        "rest_mumbai_bandra_001",
        "rest_mumbai_andheri_002", 
        "rest_mumbai_powai_003"
    ]
    
    # Test menu fetching with circuit breaker
    print("\n🍽️  Testing Menu Service (with failures)...")
    for i in range(15):  # Multiple calls to trigger circuit breaker
        try:
            restaurant_id = random.choice(mumbai_restaurants)
            menu = restaurant_service.get_menu(restaurant_id)
            print(f"✅ Menu fetched for {restaurant_id}: {len(menu['menu'])} items")
        except CircuitOpenException as e:
            print(f"🚫 Circuit OPEN: {e}")
        except Exception as e:
            print(f"❌ Menu fetch failed: {e}")
        
        time.sleep(0.5)  # Small delay between calls
    
    # Show metrics after menu testing
    print(f"\n📊 Menu Service Metrics:")
    menu_metrics = restaurant_service.menu_circuit.get_metrics()
    print(f"   State: {menu_metrics['state']}")
    print(f"   Success Rate: {menu_metrics['metrics']['success_rate_percent']:.1f}%")
    print(f"   Total Requests: {menu_metrics['metrics']['total_requests']}")
    
    # Test availability checking
    print(f"\n📋 Testing Availability Service...")
    test_items = ["Butter Chicken", "Biryani"]
    
    for i in range(10):
        try:
            restaurant_id = random.choice(mumbai_restaurants)
            availability = restaurant_service.check_availability(restaurant_id, test_items)
            available_count = sum(1 for item_info in availability['availability'].values() if item_info['available'])
            print(f"✅ Availability checked for {restaurant_id}: {available_count}/{len(test_items)} items available")
        except CircuitOpenException as e:
            print(f"🚫 Availability Circuit OPEN: {e}")
        except Exception as e:
            print(f"❌ Availability check failed: {e}")
        
        time.sleep(0.3)
    
    # Test order placement (most critical)
    print(f"\n🛒 Testing Order Service...")
    customer_info = {
        'customer_id': 'cust_mumbai_001',
        'name': 'Rajesh Sharma',
        'phone': '+919876543210',
        'address': 'Bandra West, Mumbai'
    }
    
    order_items = [
        {'item': 'Butter Chicken', 'price': 280, 'quantity': 1},
        {'item': 'Biryani', 'price': 320, 'quantity': 2}
    ]
    
    for i in range(8):
        try:
            restaurant_id = random.choice(mumbai_restaurants)
            order = restaurant_service.place_order(restaurant_id, order_items, customer_info)
            print(f"✅ Order placed: {order['order_id']} for ₹{order['total_amount']}")
        except CircuitOpenException as e:
            print(f"🚫 Order Circuit OPEN: {e}")
        except Exception as e:
            print(f"❌ Order placement failed: {e}")
        
        time.sleep(1.0)
    
    # Final metrics
    print(f"\n📊 Final Circuit Breaker Metrics:")
    print("=" * 60)
    all_metrics = restaurant_service.get_all_circuit_metrics()
    
    for service_name, metrics in all_metrics.items():
        print(f"\n{service_name.upper()}:")
        print(f"   State: {metrics['state']}")
        print(f"   Success Rate: {metrics['metrics']['success_rate_percent']:.1f}%")
        print(f"   Total Requests: {metrics['metrics']['total_requests']}")
        print(f"   Failures: {metrics['metrics']['failed_requests']}")
        print(f"   Avg Response Time: {metrics['metrics']['average_response_time_ms']:.1f}ms")
        print(f"   State Changes: {metrics['state_changes']}")
        
        if metrics['state'] == 'open':
            print(f"   Time until reset: {metrics['timing']['time_until_reset_seconds']:.0f}s")


# Circuit Breaker Manager for multiple services
class ZomatoCircuitBreakerManager:
    """
    Centralized management of multiple circuit breakers
    Zomato ke saare microservices ke liye unified monitoring
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, ZomatoCircuitBreaker] = {}
        self.logger = logging.getLogger("zomato-circuit-manager")
    
    def register_circuit_breaker(self, name: str, circuit_breaker: ZomatoCircuitBreaker):
        """Register a circuit breaker"""
        self.circuit_breakers[name] = circuit_breaker
        self.logger.info(f"📝 Registered circuit breaker: {name}")
    
    def get_all_metrics(self) -> Dict:
        """Get metrics for all registered circuit breakers"""
        metrics = {}
        for name, cb in self.circuit_breakers.items():
            metrics[name] = cb.get_metrics()
        return metrics
    
    def get_health_summary(self) -> Dict:
        """Get overall health summary"""
        total_circuits = len(self.circuit_breakers)
        if total_circuits == 0:
            return {'status': 'unknown', 'message': 'No circuit breakers registered'}
        
        states = {'closed': 0, 'open': 0, 'half_open': 0}
        total_success_rate = 0
        
        for cb in self.circuit_breakers.values():
            metrics = cb.get_metrics()
            states[metrics['state']] += 1
            total_success_rate += metrics['metrics']['success_rate_percent']
        
        avg_success_rate = total_success_rate / total_circuits
        open_percentage = (states['open'] / total_circuits) * 100
        
        if open_percentage > 50:
            status = 'critical'
            message = f"{states['open']}/{total_circuits} circuits are open"
        elif open_percentage > 20:
            status = 'degraded'
            message = f"{states['open']}/{total_circuits} circuits are open"
        elif avg_success_rate < 80:
            status = 'degraded'
            message = f"Average success rate: {avg_success_rate:.1f}%"
        else:
            status = 'healthy'
            message = f"All circuits healthy (avg success: {avg_success_rate:.1f}%)"
        
        return {
            'status': status,
            'message': message,
            'summary': {
                'total_circuits': total_circuits,
                'closed': states['closed'],
                'open': states['open'],
                'half_open': states['half_open'],
                'average_success_rate': avg_success_rate
            },
            'timestamp': datetime.utcnow().isoformat()
        }


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s %(levelname)s: %(message)s')
    
    # Run demonstration
    demonstrate_zomato_circuit_breakers()
    
    print("\n" + "=" * 60)
    print("🎯 Circuit Breaker Pattern Demonstration Complete!")
    print("Key learnings:")
    print("1. Circuit breakers protect downstream services")
    print("2. Different failure thresholds for different criticality")
    print("3. Automatic recovery through half-open state")
    print("4. Comprehensive metrics for monitoring")
    print("5. Fail-fast approach improves user experience")