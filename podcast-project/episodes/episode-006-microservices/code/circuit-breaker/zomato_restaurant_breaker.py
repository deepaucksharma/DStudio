#!/usr/bin/env python3
"""
Zomato-style Restaurant Service Circuit Breaker
Real-world example showing how circuit breaker protects restaurant ordering system

जैसे Mumbai में restaurant बंद हो जाता है तो Zomato orders block कर देता है,
वैसे ही circuit breaker failing restaurant services को protect करता है
"""

import asyncio
import time
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import redis

# Import our circuit breaker
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerException

# Zomato-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ZomatoRestaurantBreaker")

class RestaurantStatus(Enum):
    """Restaurant operating status"""
    OPEN = "open"           # Normal operations - like Tanjore Tiffin Center
    BUSY = "busy"           # High order volume - like Cafe Mocha during lunch
    CLOSED = "closed"       # Temporarily closed - like maintenance break
    UNAVAILABLE = "unavailable"  # System issues - like POS system down

@dataclass
class Restaurant:
    """Restaurant details"""
    restaurant_id: str
    name: str
    area: str              # Bandra, Andheri, Powai etc.
    cuisine_type: str      # North Indian, Chinese, Continental
    rating: float
    status: RestaurantStatus
    prep_time_minutes: int
    is_accepting_orders: bool = True
    current_load: int = 0  # Current pending orders

@dataclass
class OrderRequest:
    """Food order request"""
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    delivery_address: str
    special_instructions: str = ""

@dataclass
class OrderResponse:
    """Order response from restaurant"""
    order_id: str
    status: str           # confirmed, rejected, preparing
    estimated_time: int   # minutes
    actual_amount: float
    message: str

class RestaurantService:
    """
    Simulated restaurant service that can fail
    जैसे real Zomato में restaurant का POS system fail हो सकता है
    """
    
    def __init__(self, restaurant: Restaurant):
        self.restaurant = restaurant
        self.failure_rate = 0.0  # Current failure probability
        self.latency_ms = 1000   # Response time in milliseconds
        self.is_overloaded = False
        
        # Simulate realistic Mumbai restaurant scenarios
        self._setup_failure_scenarios()
    
    def _setup_failure_scenarios(self):
        """Setup realistic failure scenarios for Mumbai restaurants"""
        current_hour = datetime.now().hour
        
        # Peak hours failures - lunch and dinner rush
        if current_hour in [12, 13, 14, 19, 20, 21]:
            self.failure_rate = 0.15  # 15% failure during peak hours
            self.latency_ms = 3000    # Slower during peak
            self.is_overloaded = True
            logger.info(f"Restaurant {self.restaurant.name} in PEAK HOUR mode - higher failure rate")
        
        # Late night operations
        elif current_hour >= 23 or current_hour <= 6:
            self.failure_rate = 0.08  # 8% failure late night
            self.latency_ms = 2000    # Slower at night
            logger.info(f"Restaurant {self.restaurant.name} in LATE NIGHT mode")
        
        # Monsoon season failures (simulated)
        elif random.random() < 0.1:  # 10% chance of monsoon impact
            self.failure_rate = 0.25  # 25% failure during monsoons
            self.latency_ms = 4000    # Very slow due to weather
            logger.warning(f"Restaurant {self.restaurant.name} affected by MONSOON - high failure rate")
        
        else:
            self.failure_rate = 0.05  # 5% normal failure rate
            self.latency_ms = 1500    # Normal response time
    
    async def place_order(self, order_request: OrderRequest) -> OrderResponse:
        """
        Process order placement - can fail realistically
        जैसे real restaurant में order processing fail हो सकती है
        """
        # Simulate network latency
        await asyncio.sleep(self.latency_ms / 1000.0)
        
        # Simulate various failure scenarios
        if random.random() < self.failure_rate:
            await self._simulate_failure()
        
        # Check if restaurant is overloaded
        if self.is_overloaded and self.restaurant.current_load > 10:
            raise Exception(f"Restaurant {self.restaurant.name} is overloaded - like Tanjore during lunch rush!")
        
        # Check restaurant status
        if self.restaurant.status == RestaurantStatus.CLOSED:
            raise Exception(f"Restaurant {self.restaurant.name} is temporarily closed")
        
        if self.restaurant.status == RestaurantStatus.UNAVAILABLE:
            raise Exception(f"Restaurant {self.restaurant.name} POS system down - technical issues")
        
        if not self.restaurant.is_accepting_orders:
            raise Exception(f"Restaurant {self.restaurant.name} not accepting orders - kitchen issue")
        
        # Success case - process order
        self.restaurant.current_load += 1
        
        # Calculate realistic estimated time based on load and area
        base_prep_time = self.restaurant.prep_time_minutes
        load_multiplier = 1 + (self.restaurant.current_load * 0.1)  # More load = more time
        area_multiplier = self._get_area_multiplier(self.restaurant.area)
        
        estimated_time = int(base_prep_time * load_multiplier * area_multiplier)
        
        return OrderResponse(
            order_id=order_request.order_id,
            status="confirmed",
            estimated_time=estimated_time,
            actual_amount=order_request.total_amount,
            message=f"Order confirmed at {self.restaurant.name} - ready in {estimated_time} minutes!"
        )
    
    async def _simulate_failure(self):
        """Simulate realistic restaurant failures"""
        failure_types = [
            ("POS_SYSTEM_DOWN", "Point of sale system crashed - like power cut in Dadar"),
            ("KITCHEN_FIRE", "Kitchen safety system triggered - temporary shutdown"),
            ("INGREDIENT_SHORTAGE", "Key ingredients not available - supply chain issue"),
            ("STAFF_SHORTAGE", "Insufficient kitchen staff - Mumbai traffic delayed employees"),
            ("PAYMENT_GATEWAY_ISSUE", "Payment processing down - bank server maintenance"),
            ("NETWORK_CONNECTIVITY", "Internet connectivity issues - ISP problems in area"),
            ("EQUIPMENT_BREAKDOWN", "Kitchen equipment malfunction - gas connection issue"),
            ("HEALTH_INSPECTION", "Surprise health department visit - operations paused")
        ]
        
        failure_type, message = random.choice(failure_types)
        logger.error(f"Restaurant failure simulation: {failure_type} - {message}")
        
        # Different failure types have different characteristics
        if failure_type in ["KITCHEN_FIRE", "HEALTH_INSPECTION"]:
            # Critical failures - longer delay before throwing exception
            await asyncio.sleep(2.0)
            raise Exception(f"CRITICAL: {message}")
        elif failure_type in ["POS_SYSTEM_DOWN", "PAYMENT_GATEWAY_ISSUE"]:
            # System failures - medium delay
            await asyncio.sleep(1.0)
            raise Exception(f"SYSTEM_ERROR: {message}")
        else:
            # Operational failures - quick failure
            await asyncio.sleep(0.5)
            raise Exception(f"OPERATIONAL_ERROR: {message}")
    
    def _get_area_multiplier(self, area: str) -> float:
        """Get delivery time multiplier based on Mumbai area"""
        # Mumbai area-wise delivery time multipliers
        area_multipliers = {
            "Bandra": 1.2,      # Popular area, more traffic
            "Andheri": 1.3,     # Far from city center
            "Powai": 1.4,       # IT hub, heavy traffic
            "Thane": 1.6,       # Outside Mumbai proper
            "Dadar": 1.1,       # Central Mumbai
            "Fort": 1.0,        # Business district, good connectivity
            "Colaba": 1.1,      # South Mumbai
            "Borivali": 1.5,    # Far north
            "Malad": 1.4,       # Western suburbs
            "Worli": 1.2,       # Business area
        }
        
        return area_multipliers.get(area, 1.2)  # Default multiplier
    
    def update_status(self, status: RestaurantStatus, accepting_orders: bool = None):
        """Update restaurant status"""
        old_status = self.restaurant.status
        self.restaurant.status = status
        
        if accepting_orders is not None:
            self.restaurant.is_accepting_orders = accepting_orders
        
        logger.info(f"Restaurant {self.restaurant.name} status changed: {old_status.value} → {status.value}")

class ZomatoOrderService:
    """
    Zomato-style order service with circuit breaker protection
    जैसे real Zomato में restaurant failures को handle करना
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.restaurants = {}
        self.restaurant_services = {}
        self.circuit_breakers = {}
        
        # Setup test restaurants
        self._setup_test_restaurants()
    
    def _setup_test_restaurants(self):
        """Setup test restaurants across Mumbai"""
        test_restaurants = [
            Restaurant("rest_001", "Tanjore Tiffin Center", "Dadar", "South Indian", 4.5, RestaurantStatus.OPEN, 25),
            Restaurant("rest_002", "Cafe Mocha", "Bandra", "Continental", 4.2, RestaurantStatus.OPEN, 30),
            Restaurant("rest_003", "Mainland China", "Fort", "Chinese", 4.4, RestaurantStatus.OPEN, 35),
            Restaurant("rest_004", "Social", "Andheri", "Multi-cuisine", 4.1, RestaurantStatus.OPEN, 20),
            Restaurant("rest_005", "Theobroma", "Colaba", "Bakery", 4.6, RestaurantStatus.OPEN, 15),
            Restaurant("rest_006", "Brittania & Co", "Fort", "Parsi", 4.3, RestaurantStatus.OPEN, 40),
            Restaurant("rest_007", "Leopold Cafe", "Colaba", "Continental", 3.9, RestaurantStatus.OPEN, 25),
            Restaurant("rest_008", "Swathi Snacks", "Dadar", "Street Food", 4.4, RestaurantStatus.OPEN, 10),
        ]
        
        for restaurant in test_restaurants:
            self.restaurants[restaurant.restaurant_id] = restaurant
            self.restaurant_services[restaurant.restaurant_id] = RestaurantService(restaurant)
            
            # Create circuit breaker for each restaurant
            config = self._get_restaurant_circuit_config(restaurant)
            self.circuit_breakers[restaurant.restaurant_id] = CircuitBreaker(
                f"restaurant_{restaurant.restaurant_id}", 
                config, 
                self.redis_client
            )
        
        logger.info(f"Setup {len(test_restaurants)} test restaurants with circuit breakers")
    
    def _get_restaurant_circuit_config(self, restaurant: Restaurant) -> CircuitBreakerConfig:
        """Get circuit breaker config based on restaurant characteristics"""
        
        # High-rated restaurants get more lenient circuit breaker settings
        if restaurant.rating >= 4.5:
            return CircuitBreakerConfig(
                failure_threshold=5,        # Allow more failures for good restaurants
                recovery_timeout=45,        # Quick recovery
                timeout=15.0,              # Reasonable timeout
                success_threshold=2,        # Quick recovery from half-open
                slow_call_threshold=8.0,    # Fast service expected
                failure_rate_threshold=0.3  # 30% failure rate tolerance
            )
        
        # Medium-rated restaurants - standard settings
        elif restaurant.rating >= 4.0:
            return CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=60,
                timeout=20.0,
                success_threshold=3,
                slow_call_threshold=10.0,
                failure_rate_threshold=0.25
            )
        
        # Lower-rated restaurants - strict settings
        else:
            return CircuitBreakerConfig(
                failure_threshold=2,        # Less tolerance for failures
                recovery_timeout=90,        # Longer recovery time
                timeout=25.0,              # Higher timeout expectation
                success_threshold=4,        # More successes needed to recover
                slow_call_threshold=12.0,   # Slower service acceptable
                failure_rate_threshold=0.2  # Lower failure rate tolerance
            )
    
    async def place_order_with_protection(self, order_request: OrderRequest) -> OrderResponse:
        """
        Place order with circuit breaker protection
        जैसे Zomato में restaurant fail होने पर graceful handling
        """
        restaurant_id = order_request.restaurant_id
        
        if restaurant_id not in self.circuit_breakers:
            raise Exception(f"Restaurant {restaurant_id} not found")
        
        circuit_breaker = self.circuit_breakers[restaurant_id]
        restaurant_service = self.restaurant_services[restaurant_id]
        restaurant = self.restaurants[restaurant_id]
        
        try:
            # Use circuit breaker to protect the order placement
            logger.info(f"Attempting order placement at {restaurant.name} (Circuit: {circuit_breaker.get_state().value})")
            
            response = await circuit_breaker.async_call(
                restaurant_service.place_order, 
                order_request
            )
            
            logger.info(f"Order successful at {restaurant.name}: {response.order_id}")
            return response
            
        except CircuitBreakerException as e:
            logger.error(f"Circuit breaker blocked order to {restaurant.name}: {e}")
            
            # Try to find alternative restaurant
            alternative_response = await self._find_alternative_restaurant(order_request, restaurant)
            if alternative_response:
                return alternative_response
            
            # Return fallback response if no alternatives
            return OrderResponse(
                order_id=order_request.order_id,
                status="failed",
                estimated_time=0,
                actual_amount=0.0,
                message=f"Restaurant {restaurant.name} temporarily unavailable. Please try again later - Like Mumbai local during technical problems!"
            )
            
        except Exception as e:
            logger.error(f"Order placement failed at {restaurant.name}: {str(e)}")
            
            # The circuit breaker will handle this failure
            raise e
    
    async def _find_alternative_restaurant(self, original_order: OrderRequest, 
                                         failed_restaurant: Restaurant) -> Optional[OrderResponse]:
        """
        Find alternative restaurant when primary fails
        जैसे Zomato में one restaurant fail होने पर similar options suggest करना
        """
        logger.info(f"Finding alternative to {failed_restaurant.name}...")
        
        # Find restaurants with similar cuisine in same/nearby area
        alternatives = []
        for rest_id, restaurant in self.restaurants.items():
            if (rest_id != failed_restaurant.restaurant_id and
                restaurant.cuisine_type == failed_restaurant.cuisine_type and
                restaurant.status == RestaurantStatus.OPEN and
                restaurant.is_accepting_orders):
                
                # Check if circuit breaker allows this restaurant
                circuit_breaker = self.circuit_breakers[rest_id]
                if circuit_breaker.get_state().value != "OPEN":
                    alternatives.append((rest_id, restaurant))
        
        if not alternatives:
            logger.warning("No alternative restaurants available")
            return None
        
        # Select best alternative (highest rating)
        best_alternative = max(alternatives, key=lambda x: x[1].rating)
        alt_restaurant_id, alt_restaurant = best_alternative
        
        # Create new order request for alternative restaurant
        alt_order = OrderRequest(
            order_id=original_order.order_id + "_alt",
            user_id=original_order.user_id,
            restaurant_id=alt_restaurant_id,
            items=original_order.items,
            total_amount=original_order.total_amount,  # May need price adjustment
            delivery_address=original_order.delivery_address,
            special_instructions=f"Alternative to {failed_restaurant.name}. {original_order.special_instructions}"
        )
        
        try:
            logger.info(f"Trying alternative restaurant: {alt_restaurant.name}")
            response = await self.place_order_with_protection(alt_order)
            response.message = f"Ordered from {alt_restaurant.name} (alternative to {failed_restaurant.name}) - {response.message}"
            return response
            
        except Exception as e:
            logger.error(f"Alternative restaurant also failed: {str(e)}")
            return None
    
    def get_restaurant_health_status(self) -> Dict[str, Any]:
        """Get health status of all restaurants with circuit breaker info"""
        health_status = {}
        
        for restaurant_id, restaurant in self.restaurants.items():
            circuit_breaker = self.circuit_breakers[restaurant_id]
            health_info = circuit_breaker.health_check()
            
            health_status[restaurant_id] = {
                "restaurant_name": restaurant.name,
                "area": restaurant.area,
                "cuisine": restaurant.cuisine_type,
                "rating": restaurant.rating,
                "status": restaurant.status.value,
                "accepting_orders": restaurant.is_accepting_orders,
                "current_load": restaurant.current_load,
                "circuit_breaker": health_info
            }
        
        return health_status
    
    async def simulate_restaurant_failures(self):
        """Simulate realistic restaurant failures for demonstration"""
        logger.info("Starting restaurant failure simulation...")
        
        # Simulate various failure scenarios
        scenarios = [
            ("rest_001", RestaurantStatus.UNAVAILABLE, "POS system maintenance"),
            ("rest_002", RestaurantStatus.BUSY, "Kitchen overloaded during lunch rush"),
            ("rest_005", RestaurantStatus.CLOSED, "Temporary closure for cleaning"),
        ]
        
        for restaurant_id, status, reason in scenarios:
            if restaurant_id in self.restaurant_services:
                service = self.restaurant_services[restaurant_id]
                service.update_status(status, False)
                service.failure_rate = 0.8  # High failure rate
                logger.warning(f"Simulated failure: {self.restaurants[restaurant_id].name} - {reason}")
                
                await asyncio.sleep(2)  # Wait between simulations
        
        logger.info("Restaurant failure simulation completed")
    
    async def simulate_recovery(self):
        """Simulate restaurant recovery after failures"""
        logger.info("Starting restaurant recovery simulation...")
        
        for restaurant_id, restaurant in self.restaurants.items():
            service = self.restaurant_services[restaurant_id]
            service.update_status(RestaurantStatus.OPEN, True)
            service.failure_rate = 0.05  # Back to normal
            service.is_overloaded = False
            restaurant.current_load = 0
            
            # Reset circuit breakers
            circuit_breaker = self.circuit_breakers[restaurant_id]
            circuit_breaker.reset()
            
            logger.info(f"Restored restaurant: {restaurant.name}")
            await asyncio.sleep(1)
        
        logger.info("Restaurant recovery simulation completed")

async def demo_zomato_circuit_breaker():
    """
    Demonstrate Zomato-style circuit breaker in action
    Mumbai के restaurants के साथ realistic failure scenarios
    """
    print("\n=== Zomato Restaurant Circuit Breaker Demo ===")
    print("Mumbai restaurants के साथ circuit breaker protection!")
    
    # Initialize order service
    order_service = ZomatoOrderService()
    
    # Sample order requests
    sample_orders = [
        OrderRequest("order_001", "user123", "rest_001", [{"item": "Masala Dosa", "qty": 2}], 180.0, "Bandra West"),
        OrderRequest("order_002", "user124", "rest_002", [{"item": "Pasta", "qty": 1}], 350.0, "Andheri East"),
        OrderRequest("order_003", "user125", "rest_003", [{"item": "Hakka Noodles", "qty": 1}], 220.0, "Fort"),
        OrderRequest("order_004", "user126", "rest_001", [{"item": "Idli Sambhar", "qty": 3}], 120.0, "Dadar"),
        OrderRequest("order_005", "user127", "rest_002", [{"item": "Sandwich", "qty": 2}], 280.0, "Bandra"),
    ]
    
    print("\n--- Phase 1: Normal Operations ---")
    # Place orders normally
    for order in sample_orders[:2]:
        try:
            response = await order_service.place_order_with_protection(order)
            print(f"✅ Order {response.order_id}: {response.status} - {response.message}")
        except Exception as e:
            print(f"❌ Order {order.order_id}: Failed - {str(e)}")
    
    print(f"\n--- Phase 2: Restaurant Failures Simulation ---")
    # Simulate failures
    await order_service.simulate_restaurant_failures()
    
    # Try ordering from failed restaurants
    print("\nTrying to place orders during failures:")
    for order in sample_orders[2:]:
        try:
            response = await order_service.place_order_with_protection(order)
            print(f"✅ Order {response.order_id}: {response.status} - {response.message}")
        except Exception as e:
            print(f"❌ Order {order.order_id}: Failed - {str(e)}")
    
    print(f"\n--- Phase 3: Circuit Breaker Status ---")
    # Show circuit breaker status
    health_status = order_service.get_restaurant_health_status()
    for restaurant_id, health in health_status.items():
        cb_info = health['circuit_breaker']
        print(f"\n{health['restaurant_name']} ({health['area']}):")
        print(f"  Status: {health['status']}")
        print(f"  Circuit: {cb_info['state']} ({'Healthy' if cb_info['healthy'] else 'Unhealthy'})")
        print(f"  Success Rate: {cb_info['metrics']['success_rate']:.2%}")
        print(f"  Consecutive Failures: {cb_info['metrics']['consecutive_failures']}")
        print(f"  Message: {cb_info['message']}")
    
    print(f"\n--- Phase 4: Recovery Simulation ---")
    # Simulate recovery
    await order_service.simulate_recovery()
    
    # Try orders again after recovery
    print("\nTrying orders after recovery:")
    recovery_orders = [
        OrderRequest("order_006", "user128", "rest_001", [{"item": "Rava Dosa", "qty": 1}], 90.0, "Powai"),
        OrderRequest("order_007", "user129", "rest_002", [{"item": "Coffee", "qty": 2}], 160.0, "Worli"),
    ]
    
    for order in recovery_orders:
        try:
            response = await order_service.place_order_with_protection(order)
            print(f"✅ Order {response.order_id}: {response.status} - {response.message}")
        except Exception as e:
            print(f"❌ Order {order.order_id}: Failed - {str(e)}")
    
    print(f"\n--- Final Circuit Breaker Status ---")
    final_status = order_service.get_restaurant_health_status()
    healthy_count = sum(1 for h in final_status.values() if h['circuit_breaker']['healthy'])
    total_count = len(final_status)
    
    print(f"Overall System Health: {healthy_count}/{total_count} restaurants healthy")
    print("Circuit breakers successfully protected the system during failures!")
    print("जैसे Mumbai local train में safety systems, circuit breaker ने system को protect किया!")

if __name__ == "__main__":
    # Run the demo
    print("Starting Zomato Restaurant Circuit Breaker Demo...")
    asyncio.run(demo_zomato_circuit_breaker())