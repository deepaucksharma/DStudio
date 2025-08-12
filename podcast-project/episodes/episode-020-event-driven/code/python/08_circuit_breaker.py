#!/usr/bin/env python3
"""
Circuit Breaker Pattern for Event Processing
उदाहरण: BookMyShow ticket booking events के लिए circuit breaker

Setup:
pip install asyncio dataclasses

Indian Context: BookMyShow app मein movie ticket booking के दौरान:
- Payment gateway failures (Razorpay/Paytm down)
- Seat allocation service timeouts
- SMS notification service failures  
- Email service overload during blockbuster releases

Circuit Breaker prevents cascade failures:
- CLOSED: Normal operation
- OPEN: Service blocked (fail fast)
- HALF_OPEN: Testing if service recovered
"""

import asyncio
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable
import random
import uuid

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation - requests allowed
    OPEN = "open"            # Service blocked - fail fast
    HALF_OPEN = "half_open"  # Testing service recovery

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5          # Failures to trigger OPEN
    recovery_timeout: int = 60          # Seconds before trying HALF_OPEN
    success_threshold: int = 3          # Successes to close from HALF_OPEN
    timeout_duration: float = 10.0     # Request timeout seconds
    
@dataclass 
class CircuitStats:
    """Circuit breaker statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    state_changes: List[str] = None
    
    def __post_init__(self):
        if self.state_changes is None:
            self.state_changes = []

class CircuitBreakerException(Exception):
    """Circuit breaker is OPEN"""
    pass

class CircuitBreaker:
    """
    Circuit Breaker implementation
    Mumbai local train signals की तरह - red signal par sab रुक जाता है
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._state_lock = asyncio.Lock()
        
        logger.info(f"🔌 Circuit breaker initialized: {name}")
        logger.info(f"   ⚙️ Config: {config.failure_threshold} failures, "
                   f"{config.recovery_timeout}s recovery, "
                   f"{config.timeout_duration}s timeout")
    
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        """
        async with self._state_lock:
            # Check current state
            await self._update_state()
            
            if self.state == CircuitState.OPEN:
                self.stats.total_requests += 1
                logger.warning(f"🚫 Circuit breaker OPEN: {self.name} - failing fast")
                raise CircuitBreakerException(f"Circuit breaker {self.name} is OPEN")
            
            # CLOSED or HALF_OPEN state - allow request
            self.stats.total_requests += 1
            
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs), 
                timeout=self.config.timeout_duration
            )
            
            # Success handling
            async with self._state_lock:
                await self._on_success()
            
            return result
            
        except asyncio.TimeoutError:
            async with self._state_lock:
                await self._on_failure(f"Timeout after {self.config.timeout_duration}s")
            raise
            
        except Exception as e:
            async with self._state_lock:
                await self._on_failure(str(e))
            raise
    
    async def _update_state(self):
        """Update circuit state based on current conditions"""
        current_time = time.time()
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (self.stats.last_failure_time and 
                current_time - self.stats.last_failure_time >= self.config.recovery_timeout):
                await self._transition_to_half_open()
    
    async def _on_success(self):
        """Handle successful request"""
        self.stats.successful_requests += 1
        self.stats.consecutive_failures = 0
        self.stats.consecutive_successes += 1
        
        logger.info(f"✅ {self.name}: Success (consecutive: {self.stats.consecutive_successes})")
        
        # If in HALF_OPEN, check if we can close
        if self.state == CircuitState.HALF_OPEN:
            if self.stats.consecutive_successes >= self.config.success_threshold:
                await self._transition_to_closed()
    
    async def _on_failure(self, error: str):
        """Handle failed request"""
        self.stats.failed_requests += 1
        self.stats.consecutive_successes = 0
        self.stats.consecutive_failures += 1
        self.stats.last_failure_time = time.time()
        
        logger.error(f"❌ {self.name}: Failure (consecutive: {self.stats.consecutive_failures}) - {error}")
        
        # Check if we should open the circuit
        if (self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN] and 
            self.stats.consecutive_failures >= self.config.failure_threshold):
            await self._transition_to_open()
    
    async def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self.stats.state_changes.append(f"{datetime.now().isoformat()}: CLOSED/HALF_OPEN -> OPEN")
        
        logger.warning(f"🔴 {self.name}: Circuit breaker OPENED "
                      f"(failures: {self.stats.consecutive_failures})")
    
    async def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.stats.consecutive_successes = 0
        self.stats.state_changes.append(f"{datetime.now().isoformat()}: OPEN -> HALF_OPEN")
        
        logger.info(f"🟡 {self.name}: Circuit breaker HALF_OPEN (testing recovery)")
    
    async def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.stats.consecutive_failures = 0
        self.stats.state_changes.append(f"{datetime.now().isoformat()}: HALF_OPEN -> CLOSED")
        
        logger.info(f"🟢 {self.name}: Circuit breaker CLOSED (service recovered)")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        success_rate = 0.0
        if self.stats.total_requests > 0:
            success_rate = (self.stats.successful_requests / self.stats.total_requests) * 100
        
        return {
            'name': self.name,
            'state': self.state.value,
            'total_requests': self.stats.total_requests,
            'success_rate': f"{success_rate:.1f}%",
            'consecutive_failures': self.stats.consecutive_failures,
            'consecutive_successes': self.stats.consecutive_successes,
            'last_failure': datetime.fromtimestamp(self.stats.last_failure_time).isoformat() 
                           if self.stats.last_failure_time else None,
            'state_changes': len(self.stats.state_changes)
        }

# BookMyShow services with failures

class PaymentGatewayService:
    """Payment gateway service with simulated failures"""
    
    def __init__(self, failure_rate: float = 0.3):
        self.service_name = "Payment Gateway"
        self.failure_rate = failure_rate
        self.processed_payments = []
    
    async def process_payment(self, booking_id: str, amount: float, 
                            customer_id: str) -> Dict[str, Any]:
        """Process payment with potential failures"""
        logger.info(f"💳 {self.service_name}: Processing payment for booking {booking_id}")
        logger.info(f"   💰 Amount: ₹{amount}")
        logger.info(f"   👤 Customer: {customer_id}")
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate various failure scenarios
        failure_chance = random.random()
        
        if failure_chance < self.failure_rate:
            failure_types = [
                "Payment gateway timeout",
                "Insufficient funds",
                "Card declined",
                "Network connectivity issues",
                "Bank server unavailable",
                "Transaction limit exceeded"
            ]
            raise Exception(random.choice(failure_types))
        
        # Successful payment
        payment_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
        result = {
            'payment_id': payment_id,
            'booking_id': booking_id,
            'amount': amount,
            'status': 'success',
            'transaction_time': datetime.now().isoformat()
        }
        
        self.processed_payments.append(result)
        logger.info(f"✅ Payment successful: {payment_id}")
        
        return result

class SeatAllocationService:
    """Seat allocation service with capacity issues"""
    
    def __init__(self, failure_rate: float = 0.2):
        self.service_name = "Seat Allocation"
        self.failure_rate = failure_rate
        self.allocated_seats = {}
    
    async def allocate_seats(self, show_id: str, seat_count: int, 
                           customer_id: str) -> Dict[str, Any]:
        """Allocate seats with potential failures"""
        logger.info(f"🎫 {self.service_name}: Allocating {seat_count} seats for show {show_id}")
        logger.info(f"   👤 Customer: {customer_id}")
        
        # Simulate allocation processing
        await asyncio.sleep(random.uniform(0.3, 1.5))
        
        # Simulate failures
        if random.random() < self.failure_rate:
            failure_types = [
                "No seats available",
                "Database connection timeout", 
                "Seat allocation service overloaded",
                "Concurrent booking conflict",
                "Show cancelled",
                "Venue capacity exceeded"
            ]
            raise Exception(random.choice(failure_types))
        
        # Successful allocation
        allocation_id = f"SEAT_{uuid.uuid4().hex[:8].upper()}"
        seat_numbers = [f"A{i+1}" for i in range(seat_count)]  # Simple seat numbering
        
        result = {
            'allocation_id': allocation_id,
            'show_id': show_id,
            'seat_numbers': seat_numbers,
            'customer_id': customer_id,
            'allocated_at': datetime.now().isoformat()
        }
        
        self.allocated_seats[allocation_id] = result
        logger.info(f"✅ Seats allocated: {seat_numbers}")
        
        return result

class NotificationService:
    """Notification service with intermittent failures"""
    
    def __init__(self, failure_rate: float = 0.25):
        self.service_name = "Notification Service"
        self.failure_rate = failure_rate
        self.sent_notifications = []
    
    async def send_booking_confirmation(self, customer_id: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send booking confirmation with potential failures"""
        logger.info(f"📱 {self.service_name}: Sending confirmation to {customer_id}")
        logger.info(f"   🎬 Movie: {booking_details.get('movie_name', 'Unknown')}")
        
        # Simulate notification delay
        await asyncio.sleep(random.uniform(0.2, 1.0))
        
        # Simulate failures
        if random.random() < self.failure_rate:
            failure_types = [
                "SMS gateway overloaded",
                "Email service down",
                "Push notification failed",
                "Customer phone unreachable",
                "Network timeout",
                "Rate limit exceeded"
            ]
            raise Exception(random.choice(failure_types))
        
        # Successful notification
        notification_id = f"NOTIF_{uuid.uuid4().hex[:8].upper()}"
        result = {
            'notification_id': notification_id,
            'customer_id': customer_id,
            'type': 'booking_confirmation',
            'sent_at': datetime.now().isoformat(),
            'status': 'delivered'
        }
        
        self.sent_notifications.append(result)
        logger.info(f"✅ Notification sent: {notification_id}")
        
        return result

class BookMyShowBookingService:
    """
    Main booking service with circuit breaker protection
    Film production की तरह - हर department का backup plan होना चाहिए
    """
    
    def __init__(self):
        # Initialize services with different failure rates
        self.payment_service = PaymentGatewayService(failure_rate=0.4)  # High failure rate
        self.seat_service = SeatAllocationService(failure_rate=0.2)
        self.notification_service = NotificationService(failure_rate=0.3)
        
        # Circuit breaker configurations for different services
        self.circuit_breakers = {
            'payment': CircuitBreaker(
                "Payment Gateway CB",
                CircuitBreakerConfig(
                    failure_threshold=3,
                    recovery_timeout=30,
                    success_threshold=2,
                    timeout_duration=5.0
                )
            ),
            'seat_allocation': CircuitBreaker(
                "Seat Allocation CB", 
                CircuitBreakerConfig(
                    failure_threshold=4,
                    recovery_timeout=20,
                    success_threshold=3,
                    timeout_duration=3.0
                )
            ),
            'notification': CircuitBreaker(
                "Notification CB",
                CircuitBreakerConfig(
                    failure_threshold=5,
                    recovery_timeout=15,
                    success_threshold=2,
                    timeout_duration=2.0
                )
            )
        }
        
        self.bookings = {}
    
    async def book_tickets(self, customer_id: str, show_id: str, 
                          seat_count: int, movie_name: str) -> Dict[str, Any]:
        """Complete ticket booking with circuit breaker protection"""
        booking_id = f"BMS_{uuid.uuid4().hex[:8].upper()}"
        
        logger.info(f"🎬 Starting ticket booking: {booking_id}")
        logger.info(f"   🎭 Movie: {movie_name}")
        logger.info(f"   🎫 Seats: {seat_count}")
        logger.info(f"   👤 Customer: {customer_id}")
        
        booking_result = {
            'booking_id': booking_id,
            'customer_id': customer_id,
            'show_id': show_id,
            'movie_name': movie_name,
            'seat_count': seat_count,
            'status': 'pending',
            'steps_completed': [],
            'errors': []
        }
        
        try:
            # Step 1: Seat Allocation (protected by circuit breaker)
            logger.info("🎫 Step 1: Allocating seats...")
            try:
                seat_result = await self.circuit_breakers['seat_allocation'].call(
                    self.seat_service.allocate_seats,
                    show_id, seat_count, customer_id
                )
                booking_result['seat_allocation'] = seat_result
                booking_result['steps_completed'].append('seat_allocation')
                
            except CircuitBreakerException:
                logger.error("🚫 Seat allocation circuit breaker is OPEN - using fallback")
                # Fallback: Virtual queue or waitlist
                booking_result['seat_allocation'] = {
                    'status': 'waitlisted',
                    'message': 'Added to waiting list due to high demand'
                }
                booking_result['steps_completed'].append('seat_allocation_fallback')
            
            # Step 2: Payment Processing (protected by circuit breaker)
            logger.info("💳 Step 2: Processing payment...")
            ticket_price = 250.0 * seat_count  # ₹250 per ticket
            
            try:
                payment_result = await self.circuit_breakers['payment'].call(
                    self.payment_service.process_payment,
                    booking_id, ticket_price, customer_id
                )
                booking_result['payment'] = payment_result
                booking_result['steps_completed'].append('payment')
                
            except CircuitBreakerException:
                logger.error("🚫 Payment circuit breaker is OPEN - using fallback")
                # Fallback: Hold booking for limited time
                booking_result['payment'] = {
                    'status': 'held',
                    'message': 'Booking held for 10 minutes - complete payment later',
                    'hold_until': (datetime.now() + timedelta(minutes=10)).isoformat()
                }
                booking_result['steps_completed'].append('payment_fallback')
            
            # Step 3: Send Confirmation (protected by circuit breaker)
            logger.info("📱 Step 3: Sending confirmation...")
            try:
                notification_result = await self.circuit_breakers['notification'].call(
                    self.notification_service.send_booking_confirmation,
                    customer_id, booking_result
                )
                booking_result['notification'] = notification_result
                booking_result['steps_completed'].append('notification')
                
            except CircuitBreakerException:
                logger.warning("🚫 Notification circuit breaker is OPEN - using fallback")
                # Fallback: Store notification for later retry
                booking_result['notification'] = {
                    'status': 'queued',
                    'message': 'Confirmation will be sent once service recovers'
                }
                booking_result['steps_completed'].append('notification_fallback')
            
            # Determine overall booking status
            if 'payment' in booking_result['steps_completed'] and 'seat_allocation' in booking_result['steps_completed']:
                booking_result['status'] = 'confirmed'
            elif any('fallback' in step for step in booking_result['steps_completed']):
                booking_result['status'] = 'partial_success'
            else:
                booking_result['status'] = 'failed'
            
            self.bookings[booking_id] = booking_result
            
            logger.info(f"✅ Booking completed: {booking_id} - Status: {booking_result['status']}")
            return booking_result
            
        except Exception as e:
            booking_result['status'] = 'failed'
            booking_result['errors'].append(str(e))
            logger.error(f"❌ Booking failed: {booking_id} - {e}")
            return booking_result
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            name: cb.get_health_status() 
            for name, cb in self.circuit_breakers.items()
        }

async def bookmyshow_circuit_breaker_demo():
    """BookMyShow circuit breaker demo"""
    print("🎬 BookMyShow Circuit Breaker Demo")
    print("=" * 50)
    
    booking_service = BookMyShowBookingService()
    
    # Movie shows for booking
    shows = [
        {"show_id": "SHOW001", "movie": "RRR", "customer": "CUST_RAHUL"},
        {"show_id": "SHOW002", "movie": "KGF Chapter 2", "customer": "CUST_PRIYA"},
        {"show_id": "SHOW003", "movie": "Pushpa", "customer": "CUST_AMIT"},
        {"show_id": "SHOW004", "movie": "Sooryavanshi", "customer": "CUST_NEHA"},
        {"show_id": "SHOW005", "movie": "Spider-Man", "customer": "CUST_RAVI"},
        {"show_id": "SHOW006", "movie": "Avengers", "customer": "CUST_SITA"},
        {"show_id": "SHOW007", "movie": "Fast & Furious", "customer": "CUST_RAMAN"},
        {"show_id": "SHOW008", "movie": "Dangal", "customer": "CUST_GEETA"},
    ]
    
    print("🎭 Starting ticket booking simulation...")
    print("⚠️ Note: Services have intentional failure rates to trigger circuit breakers")
    print()
    
    successful_bookings = 0
    partial_bookings = 0
    failed_bookings = 0
    
    # Process bookings one by one to see circuit breaker behavior
    for i, show in enumerate(shows, 1):
        print(f"📋 Booking {i}/{len(shows)}: {show['movie']}")
        
        try:
            result = await booking_service.book_tickets(
                customer_id=show['customer'],
                show_id=show['show_id'],
                seat_count=2,
                movie_name=show['movie']
            )
            
            status_emoji = {
                'confirmed': '✅',
                'partial_success': '⚠️',
                'failed': '❌'
            }.get(result['status'], '❓')
            
            print(f"   {status_emoji} Status: {result['status']}")
            print(f"   📋 Steps: {', '.join(result['steps_completed'])}")
            
            if result['status'] == 'confirmed':
                successful_bookings += 1
            elif result['status'] == 'partial_success':
                partial_bookings += 1
            else:
                failed_bookings += 1
            
        except Exception as e:
            print(f"   ❌ Booking failed: {e}")
            failed_bookings += 1
        
        print()
        
        # Show circuit breaker status every few bookings
        if i % 3 == 0:
            print("🔌 Circuit Breaker Status:")
            cb_status = booking_service.get_circuit_breaker_status()
            
            for service, status in cb_status.items():
                state_emoji = {
                    'closed': '🟢',
                    'open': '🔴', 
                    'half_open': '🟡'
                }.get(status['state'], '❓')
                
                print(f"   {state_emoji} {service.title()}: {status['state'].upper()} "
                      f"(Success: {status['success_rate']}, "
                      f"Failures: {status['consecutive_failures']})")
            print()
        
        # Small delay between bookings
        await asyncio.sleep(1)
    
    # Final statistics
    print("📊 Final Booking Results:")
    print(f"   ✅ Successful: {successful_bookings}")
    print(f"   ⚠️ Partial Success: {partial_bookings}")
    print(f"   ❌ Failed: {failed_bookings}")
    print()
    
    # Final circuit breaker status
    print("🔌 Final Circuit Breaker Status:")
    cb_status = booking_service.get_circuit_breaker_status()
    
    for service, status in cb_status.items():
        state_emoji = {
            'closed': '🟢',
            'open': '🔴',
            'half_open': '🟡'
        }.get(status['state'], '❓')
        
        print(f"   {state_emoji} {service.title()}:")
        print(f"      State: {status['state'].upper()}")
        print(f"      Total Requests: {status['total_requests']}")
        print(f"      Success Rate: {status['success_rate']}")
        print(f"      State Changes: {status['state_changes']}")
        
        if status['last_failure']:
            print(f"      Last Failure: {status['last_failure']}")
        print()
    
    print("🎯 Key Benefits Demonstrated:")
    print("   ✅ Fast failure when services are down")
    print("   ✅ Automatic recovery testing")
    print("   ✅ Graceful degradation with fallbacks") 
    print("   ✅ Prevention of cascade failures")
    print("   ✅ Service health monitoring")
    print("   ✅ Configurable failure thresholds")

async def circuit_breaker_recovery_demo():
    """Demonstrate circuit breaker recovery"""
    print("\n" + "="*50)
    print("🛠️ Circuit Breaker Recovery Demo")
    print("="*50)
    
    # Create a circuit breaker with quick recovery for demo
    config = CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=5,  # 5 seconds recovery
        success_threshold=2,
        timeout_duration=1.0
    )
    
    cb = CircuitBreaker("Demo Service CB", config)
    
    # Simulate a failing service
    class FlakeyService:
        def __init__(self):
            self.call_count = 0
            
        async def process(self):
            self.call_count += 1
            
            # Fail first 3 calls, then succeed
            if self.call_count <= 3:
                raise Exception(f"Service failure #{self.call_count}")
            else:
                return f"Success #{self.call_count}"
    
    service = FlakeyService()
    
    print("🔬 Testing circuit breaker state transitions...")
    
    # Phase 1: Trigger failures to open circuit
    print("\n📉 Phase 1: Triggering failures (CLOSED -> OPEN)")
    for i in range(4):
        try:
            result = await cb.call(service.process)
            print(f"   ✅ Call {i+1}: {result}")
        except CircuitBreakerException:
            print(f"   🚫 Call {i+1}: Circuit breaker OPEN")
        except Exception as e:
            print(f"   ❌ Call {i+1}: {e}")
        
        print(f"      Circuit State: {cb.state.value}")
        await asyncio.sleep(0.5)
    
    # Phase 2: Wait for recovery timeout
    print(f"\n⏳ Phase 2: Waiting {config.recovery_timeout}s for recovery timeout...")
    await asyncio.sleep(config.recovery_timeout + 1)
    
    # Phase 3: Test recovery (OPEN -> HALF_OPEN -> CLOSED)
    print("\n📈 Phase 3: Testing recovery (OPEN -> HALF_OPEN -> CLOSED)")
    for i in range(4):
        try:
            result = await cb.call(service.process)
            print(f"   ✅ Call {i+1}: {result}")
        except CircuitBreakerException:
            print(f"   🚫 Call {i+1}: Circuit breaker OPEN")
        except Exception as e:
            print(f"   ❌ Call {i+1}: {e}")
        
        print(f"      Circuit State: {cb.state.value}")
        await asyncio.sleep(1)
    
    # Final status
    print(f"\n📊 Final Statistics:")
    health = cb.get_health_status()
    for key, value in health.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(bookmyshow_circuit_breaker_demo())
    asyncio.run(circuit_breaker_recovery_demo())