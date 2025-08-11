#!/usr/bin/env python3
"""
Circuit Breaker Usage Examples
Real-world scenarios for Indian microservices

जैसे Mumbai local train system में different lines के लिए
अलग-अलग circuit breakers होते हैं, वैसे ही different services
के लिए customized protection
"""

import asyncio
import random
import time
import requests
import redis
from circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, MumbaiCircuitBreakers,
    CircuitBreakerOpenException, CircuitBreakerTimeoutException,
    circuit_breaker
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CircuitBreakerExamples")

# Redis client for state persistence
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Example 1: IRCTC Ticket Booking Service
class IRCTCBookingService:
    """
    IRCTC जैसी ticket booking service
    Peak hours में server overload होने पर circuit breaker protection
    """
    
    def __init__(self):
        self.circuit_breaker = MumbaiCircuitBreakers.irctc_booking_breaker(redis_client)
    
    def book_ticket(self, train_number: str, passenger_count: int, journey_date: str):
        """
        Ticket booking with circuit breaker protection
        जैसे Tatkal booking में server crash protection
        """
        
        @self.circuit_breaker
        def _internal_booking():
            # Simulate IRCTC server behavior
            logger.info(f"Attempting to book {passenger_count} tickets for train {train_number}")
            
            # Simulate server overload during peak hours (10% failure rate)
            if random.random() < 0.1:
                raise Exception("IRCTC server overloaded - Like Monday morning rush!")
            
            # Simulate slow response during heavy traffic (20% slow responses)
            if random.random() < 0.2:
                time.sleep(random.uniform(16, 25))  # Slow response
            else:
                time.sleep(random.uniform(2, 8))    # Normal response
            
            pnr = f"PNR{random.randint(1000000000, 9999999999)}"
            return {
                "status": "CONFIRMED",
                "pnr": pnr,
                "train_number": train_number,
                "passenger_count": passenger_count,
                "journey_date": journey_date,
                "booking_time": time.time()
            }
        
        try:
            return _internal_booking()
        except CircuitBreakerOpenException:
            # Fallback: Show queue position or alternative trains
            logger.warning("IRCTC booking circuit breaker open - Showing alternatives")
            return {
                "status": "CIRCUIT_BREAKER_OPEN",
                "message": "Service temporarily unavailable. Please try alternative trains:",
                "alternatives": [
                    f"Train {int(train_number) + 2}",
                    f"Train {int(train_number) + 4}"
                ],
                "queue_position": random.randint(1, 100)
            }

# Example 2: Paytm Payment Gateway
class PaymentGatewayService:
    """
    Paytm/PhonePe जैसी payment gateway service
    Payment failures के लिए critical circuit breaker
    """
    
    def __init__(self):
        # Custom configuration for payment service
        payment_config = CircuitBreakerConfig(
            failure_threshold=2,      # Payment failures are critical
            recovery_timeout=30,      # Quick recovery needed
            timeout=45.0,            # Generous timeout for payments
            expected_exception=(requests.RequestException, ValueError),
            fallback_function=self._payment_fallback
        )
        self.circuit_breaker = CircuitBreaker("paytm_payments", payment_config, redis_client)
    
    def process_payment(self, user_id: str, amount: float, payment_method: str):
        """Process payment with circuit breaker protection"""
        
        @self.circuit_breaker
        def _internal_payment_processing():
            logger.info(f"Processing payment of ₹{amount} for user {user_id} via {payment_method}")
            
            # Simulate payment gateway failures (5% failure rate)
            if random.random() < 0.05:
                raise requests.RequestException("Payment gateway timeout - Bank server down!")
            
            # Simulate slow payment processing (15% slow payments)
            if random.random() < 0.15:
                time.sleep(random.uniform(20, 40))  # Slow payment
            else:
                time.sleep(random.uniform(2, 8))    # Normal payment
            
            transaction_id = f"TXN{random.randint(100000000, 999999999)}"
            return {
                "status": "SUCCESS",
                "transaction_id": transaction_id,
                "amount": amount,
                "payment_method": payment_method,
                "timestamp": time.time()
            }
        
        return _internal_payment_processing()
    
    def _payment_fallback(self, user_id: str, amount: float, payment_method: str):
        """Fallback when payment circuit breaker is open"""
        logger.warning("Payment circuit breaker open - Using fallback COD option")
        return {
            "status": "FALLBACK_COD",
            "message": "Online payment temporarily unavailable. Order placed for Cash on Delivery.",
            "amount": amount,
            "delivery_charges": 40.0,  # ₹40 COD charges
            "total_amount": amount + 40.0
        }

# Example 3: Zomato Restaurant Service
@circuit_breaker("zomato_restaurants", failure_threshold=4, recovery_timeout=60, timeout=15.0)
def get_nearby_restaurants(latitude: float, longitude: float, cuisine_type: str = None):
    """
    Get nearby restaurants with circuit breaker protection
    जैसे Mumbai में restaurant search during lunch rush
    """
    logger.info(f"Searching restaurants near {latitude}, {longitude}")
    
    # Simulate restaurant service load (10% failure during lunch/dinner rush)
    current_hour = time.localtime().tm_hour
    if current_hour in [12, 13, 19, 20, 21]:  # Lunch and dinner hours
        if random.random() < 0.15:  # Higher failure rate during peak hours
            raise Exception("Restaurant service overloaded - Like Mumbai food courts during lunch!")
    else:
        if random.random() < 0.05:  # Lower failure rate during off-peak
            raise Exception("Restaurant service maintenance")
    
    # Simulate API response time
    time.sleep(random.uniform(1, 5))
    
    # Generate sample restaurants
    restaurants = []
    for i in range(random.randint(10, 25)):
        restaurants.append({
            "id": f"REST_{i+1}",
            "name": f"Mumbai Kitchen {i+1}",
            "cuisine": cuisine_type or random.choice(["North Indian", "South Indian", "Chinese", "Street Food"]),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "delivery_time": random.randint(20, 45),
            "distance": round(random.uniform(0.5, 5.0), 1)
        })
    
    return {
        "restaurants": restaurants,
        "total_count": len(restaurants),
        "search_time": time.time()
    }

# Example 4: Async Ola Cab Booking Service
class CabBookingService:
    """
    Ola/Uber जैसी cab booking service
    Async operations के साथ circuit breaker
    """
    
    def __init__(self):
        self.circuit_breaker = MumbaiCircuitBreakers.cab_booking_breaker(redis_client)
    
    async def book_cab(self, pickup_location: str, drop_location: str, cab_type: str = "MINI"):
        """Book cab with async circuit breaker protection"""
        
        async def _internal_cab_booking():
            logger.info(f"Booking {cab_type} cab from {pickup_location} to {drop_location}")
            
            # Simulate driver unavailability (8% failure rate during peak hours)
            if random.random() < 0.08:
                raise Exception("No drivers available - Like Mumbai traffic jam situation!")
            
            # Simulate slow driver allocation (25% slow responses)
            if random.random() < 0.25:
                await asyncio.sleep(random.uniform(10, 20))  # Slow allocation
            else:
                await asyncio.sleep(random.uniform(2, 6))    # Normal allocation
            
            ride_id = f"RIDE{random.randint(10000000, 99999999)}"
            driver_id = f"DRV{random.randint(1000, 9999)}"
            
            return {
                "status": "CONFIRMED",
                "ride_id": ride_id,
                "driver_id": driver_id,
                "driver_name": f"Driver {random.randint(1, 100)}",
                "cab_number": f"MH02AB{random.randint(1000, 9999)}",
                "estimated_arrival": random.randint(3, 12),
                "fare_estimate": random.randint(80, 350)
            }
        
        try:
            return await self.circuit_breaker.async_call(_internal_cab_booking)
        except CircuitBreakerOpenException:
            logger.warning("Cab booking circuit breaker open - Suggesting alternatives")
            return {
                "status": "CIRCUIT_BREAKER_OPEN",
                "message": "Cab booking temporarily unavailable",
                "alternatives": [
                    "Mumbai Local Train",
                    "BEST Bus Service", 
                    "Mumbai Metro",
                    "Auto Rickshaw"
                ],
                "wait_time": "5-10 minutes"
            }

# Example 5: Circuit Breaker Dashboard
class CircuitBreakerDashboard:
    """
    Circuit breaker monitoring dashboard
    जैसे Mumbai local train control room
    """
    
    def __init__(self, circuit_breakers: list):
        self.circuit_breakers = circuit_breakers
    
    def get_overall_status(self):
        """Get overall system health"""
        total_breakers = len(self.circuit_breakers)
        healthy_breakers = 0
        open_breakers = []
        
        for cb in self.circuit_breakers:
            health = cb.health_check()
            if health['healthy']:
                healthy_breakers += 1
            else:
                open_breakers.append(health['name'])
        
        return {
            "overall_health": (healthy_breakers / total_breakers) * 100,
            "total_circuit_breakers": total_breakers,
            "healthy_breakers": healthy_breakers,
            "open_breakers": open_breakers,
            "timestamp": time.time()
        }
    
    def get_detailed_status(self):
        """Get detailed status of all circuit breakers"""
        status_report = {
            "circuit_breakers": [],
            "summary": self.get_overall_status()
        }
        
        for cb in self.circuit_breakers:
            health = cb.health_check()
            status_report["circuit_breakers"].append(health)
        
        return status_report

# Example usage and testing
async def run_examples():
    """Run all circuit breaker examples"""
    
    logger.info("🚆 Starting Mumbai Circuit Breaker Examples 🚆")
    
    # Initialize services
    irctc_service = IRCTCBookingService()
    payment_service = PaymentGatewayService()
    cab_service = CabBookingService()
    
    # Create dashboard
    dashboard = CircuitBreakerDashboard([
        irctc_service.circuit_breaker,
        payment_service.circuit_breaker,
        cab_service.circuit_breaker
    ])
    
    # Example 1: IRCTC Booking
    logger.info("\n--- IRCTC Ticket Booking Example ---")
    for i in range(15):  # Simulate multiple booking attempts
        try:
            result = irctc_service.book_ticket("12345", 2, "2024-12-25")
            logger.info(f"Booking {i+1}: {result['status']}")
            if 'pnr' in result:
                logger.info(f"PNR: {result['pnr']}")
        except Exception as e:
            logger.error(f"Booking {i+1} failed: {e}")
        
        await asyncio.sleep(0.5)  # Brief pause between bookings
    
    # Example 2: Payment Processing
    logger.info("\n--- Payment Processing Example ---")
    for i in range(10):
        try:
            result = payment_service.process_payment(f"USER_{i+1}", 250.0 + i*50, "UPI")
            logger.info(f"Payment {i+1}: {result['status']}")
            if 'transaction_id' in result:
                logger.info(f"Transaction ID: {result['transaction_id']}")
        except Exception as e:
            logger.error(f"Payment {i+1} failed: {e}")
        
        await asyncio.sleep(0.3)
    
    # Example 3: Restaurant Search
    logger.info("\n--- Restaurant Search Example ---")
    for i in range(8):
        try:
            result = get_nearby_restaurants(19.0760, 72.8777, "North Indian")
            logger.info(f"Search {i+1}: Found {result['total_count']} restaurants")
        except Exception as e:
            logger.error(f"Search {i+1} failed: {e}")
        
        await asyncio.sleep(0.5)
    
    # Example 4: Async Cab Booking
    logger.info("\n--- Async Cab Booking Example ---")
    tasks = []
    for i in range(12):
        task = cab_service.book_cab(f"Location_{i}", f"Destination_{i}", "MINI")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Cab booking {i+1} failed: {result}")
        else:
            logger.info(f"Cab booking {i+1}: {result['status']}")
            if 'ride_id' in result:
                logger.info(f"Ride ID: {result['ride_id']}")
    
    # Show dashboard status
    logger.info("\n--- Circuit Breaker Dashboard ---")
    dashboard_status = dashboard.get_detailed_status()
    
    logger.info(f"Overall Health: {dashboard_status['summary']['overall_health']:.1f}%")
    logger.info(f"Healthy Breakers: {dashboard_status['summary']['healthy_breakers']}/{dashboard_status['summary']['total_circuit_breakers']}")
    
    if dashboard_status['summary']['open_breakers']:
        logger.warning(f"Open Breakers: {', '.join(dashboard_status['summary']['open_breakers'])}")
    
    for cb_status in dashboard_status['circuit_breakers']:
        logger.info(f"Circuit Breaker: {cb_status['name']}")
        logger.info(f"  State: {cb_status['state']}")
        logger.info(f"  Success Rate: {cb_status['metrics']['success_rate']:.2%}")
        logger.info(f"  Total Requests: {cb_status['metrics']['total_requests']}")
        logger.info(f"  Message: {cb_status['message']}")
        print()

def run_load_test():
    """
    Load test to demonstrate circuit breaker behavior
    जैसे Mumbai local train में Monday morning rush का simulation
    """
    logger.info("🔥 Starting Mumbai Scale Load Test 🔥")
    
    # High failure rate service for demo
    @circuit_breaker("load_test_service", failure_threshold=3, recovery_timeout=10)
    def failing_service():
        # 60% failure rate to quickly trigger circuit breaker
        if random.random() < 0.6:
            raise Exception("Service overloaded!")
        time.sleep(0.1)
        return "Success"
    
    # Run load test
    success_count = 0
    failure_count = 0
    blocked_count = 0
    
    for i in range(100):
        try:
            result = failing_service()
            success_count += 1
            if i % 10 == 0:
                logger.info(f"Request {i+1}: SUCCESS")
        except CircuitBreakerOpenException:
            blocked_count += 1
            if i % 10 == 0:
                logger.warning(f"Request {i+1}: BLOCKED (Circuit Breaker Open)")
        except Exception:
            failure_count += 1
            if i % 10 == 0:
                logger.error(f"Request {i+1}: FAILED")
        
        time.sleep(0.1)
    
    logger.info(f"\n--- Load Test Results ---")
    logger.info(f"Total Requests: 100")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {failure_count}")
    logger.info(f"Blocked: {blocked_count}")
    logger.info(f"Success Rate: {success_count}%")
    logger.info(f"Protection Rate: {blocked_count}% (Requests saved from failure)")

if __name__ == "__main__":
    print("🚆 Mumbai Circuit Breaker Examples - Production Ready! 🚆")
    print("Like Mumbai's resilient train system, our microservices stay protected!")
    print()
    
    # Run async examples
    asyncio.run(run_examples())
    
    print("\n" + "="*60)
    
    # Run load test
    run_load_test()
    
    print("\n🎉 All examples completed! Circuit breakers working like Mumbai's efficient infrastructure! 🎉")