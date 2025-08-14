#!/usr/bin/env python3
"""
SAGA Orchestration for IRCTC Railway Booking System
===================================================
IRCTC रेलवे बुकिंग सिस्टम के लिए SAGA ऑर्केस्ट्रेशन

Production-ready SAGA orchestration implementation for IRCTC (Indian Railway 
Catering and Tourism Corporation) train booking system. Handles complex 
distributed transactions across multiple services with compensation logic.

This example demonstrates:
यह उदाहरण प्रदर्शित करता है:

1. Orchestrator-based SAGA pattern - ऑर्केस्ट्रेटर-आधारित SAGA पैटर्न
2. Distributed transaction coordination - वितरित लेन-देन समन्वय
3. Compensation actions for rollback - रोलबैक के लिए क्षतिपूर्ति कार्रवाई
4. State machine for SAGA steps - SAGA चरणों के लिए स्टेट मशीन
5. Failure handling and recovery - विफलता हैंडलिंग और रिकवरी
6. Timeout and retry mechanisms - टाइमआउट और retry तंत्र

Author: Hindi Podcast Series
Episode: 020 - Event-Driven Architecture
Context: IRCTC train booking with multiple service coordination
"""

import asyncio
import json
import uuid
import time
import logging
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from abc import ABC, abstractmethod
import random
from collections import defaultdict

# Configure logging - लॉगिंग कॉन्फ़िगरेशन
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SagaStatus(Enum):
    """SAGA execution status - SAGA निष्पादन स्थिति"""
    STARTED = "STARTED"              # शुरू हुई
    IN_PROGRESS = "IN_PROGRESS"      # प्रगति में
    COMPLETED = "COMPLETED"          # पूर्ण हुई
    COMPENSATING = "COMPENSATING"    # क्षतिपूर्ति कर रही
    COMPENSATED = "COMPENSATED"      # क्षतिपूर्ति की गई
    FAILED = "FAILED"                # असफल

class StepStatus(Enum):
    """SAGA step status - SAGA चरण स्थिति"""
    PENDING = "PENDING"              # लंबित
    STARTED = "STARTED"              # शुरू हुई
    COMPLETED = "COMPLETED"          # पूर्ण हुई
    COMPENSATING = "COMPENSATING"    # क्षतिपूर्ति कर रही
    COMPENSATED = "COMPENSATED"      # क्षतिपूर्ति की गई
    FAILED = "FAILED"                # असफल

class TrainClass(Enum):
    """Train class types - ट्रेन क्लास प्रकार"""
    SLEEPER = "SL"           # स्लीपर
    AC_3_TIER = "3A"         # AC 3 टियर
    AC_2_TIER = "2A"         # AC 2 टियर
    AC_1_TIER = "1A"         # AC 1 टियर
    CC = "CC"                # Chair Car
    EC = "EC"                # Executive Chair Car

@dataclass
class BookingRequest:
    """Train booking request - ट्रेन बुकिंग अनुरोध"""
    booking_id: str
    user_id: str
    train_number: str
    train_name: str
    from_station: str
    to_station: str
    journey_date: str
    travel_class: TrainClass
    passengers: List[Dict[str, Any]]
    total_fare: float
    payment_method: str
    mobile_number: str
    email: str

@dataclass
class SagaStep:
    """SAGA step definition - SAGA चरण परिभाषा"""
    step_id: str
    step_name: str
    action: Callable
    compensation: Callable
    timeout_seconds: int = 30
    retry_count: int = 3
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SagaExecution:
    """SAGA execution state - SAGA निष्पादन स्थिति"""
    saga_id: str
    booking_request: BookingRequest
    status: SagaStatus = SagaStatus.STARTED
    current_step: int = 0
    steps: List[SagaStep] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    compensation_reason: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

class BookingService:
    """Train booking service - ट्रेन बुकिंग सर्विस"""
    
    def __init__(self):
        self.bookings: Dict[str, Dict] = {}
        self.failure_rate = 0.15  # 15% failure simulation - 15% विफलता सिमुलेशन
    
    async def check_seat_availability(self, train_number: str, journey_date: str, 
                                    travel_class: TrainClass, passenger_count: int) -> Dict[str, Any]:
        """Check seat availability - सीट उपलब्धता जांचें"""
        await asyncio.sleep(1)  # Simulate API call - API कॉल का सिमुलेशन
        
        # Simulate occasional failures - कभी-कभार विफलता का सिमुलेशन
        if random.random() < self.failure_rate:
            raise Exception("Seat availability service temporarily unavailable")
        
        # Simulate availability check - उपलब्धता जांच का सिमुलेशन
        available_seats = random.randint(50, 200)
        waiting_list = random.randint(0, 50)
        
        result = {
            'train_number': train_number,
            'journey_date': journey_date,
            'travel_class': travel_class.value,
            'available_seats': available_seats,
            'waiting_list': waiting_list,
            'is_available': available_seats >= passenger_count
        }
        
        logger.info(f"Seat availability check: {result}")
        return result
    
    async def reserve_seats(self, booking_request: BookingRequest) -> Dict[str, Any]:
        """Reserve seats for passengers - यात्रियों के लिए सीट आरक्षित करें"""
        await asyncio.sleep(2)  # Simulate seat reservation - सीट आरक्षण का सिमुलेशन
        
        if random.random() < self.failure_rate:
            raise Exception("Seat reservation failed due to high demand")
        
        # Generate PNR and seat details - PNR और सीट विवरण जेनरेट करें
        pnr = f"PNR{random.randint(1000000, 9999999)}"
        seats = [f"S{i+1}-{random.randint(1, 72)}" for i in range(len(booking_request.passengers))]
        
        reservation = {
            'pnr': pnr,
            'seats': seats,
            'status': 'CONFIRMED',
            'train_number': booking_request.train_number,
            'journey_date': booking_request.journey_date,
            'passengers': booking_request.passengers
        }
        
        self.bookings[booking_request.booking_id] = reservation
        logger.info(f"Seats reserved: PNR {pnr}")
        return reservation
    
    async def cancel_reservation(self, booking_id: str) -> bool:
        """Cancel seat reservation - सीट आरक्षण रद्द करें"""
        await asyncio.sleep(1)
        
        if booking_id in self.bookings:
            reservation = self.bookings[booking_id]
            reservation['status'] = 'CANCELLED'
            logger.info(f"Reservation cancelled: PNR {reservation.get('pnr')}")
            return True
        
        logger.warning(f"No reservation found for booking {booking_id}")
        return False

class PaymentService:
    """Payment processing service - भुगतान प्रसंस्करण सेवा"""
    
    def __init__(self):
        self.payments: Dict[str, Dict] = {}
        self.failure_rate = 0.20  # 20% payment failure rate - 20% भुगतान विफलता दर
    
    async def process_payment(self, booking_request: BookingRequest) -> Dict[str, Any]:
        """Process payment for booking - बुकिंग के लिए भुगतान प्रक्रिया करें"""
        await asyncio.sleep(3)  # Simulate payment gateway processing
        
        if random.random() < self.failure_rate:
            raise Exception("Payment gateway declined the transaction")
        
        payment_id = f"PAY{uuid.uuid4().hex[:10].upper()}"
        
        payment = {
            'payment_id': payment_id,
            'booking_id': booking_request.booking_id,
            'amount': booking_request.total_fare,
            'payment_method': booking_request.payment_method,
            'status': 'SUCCESS',
            'gateway_ref': f"HDFC{random.randint(100000, 999999)}",
            'processed_at': datetime.now().isoformat()
        }
        
        self.payments[booking_request.booking_id] = payment
        logger.info(f"Payment processed: {payment_id} - ₹{booking_request.total_fare}")
        return payment
    
    async def refund_payment(self, booking_id: str, reason: str) -> bool:
        """Refund payment for cancelled booking - रद्द बुकिंग के लिए भुगतान रिफंड"""
        await asyncio.sleep(2)
        
        if booking_id in self.payments:
            payment = self.payments[booking_id]
            refund_id = f"REF{uuid.uuid4().hex[:10].upper()}"
            
            payment['refund_id'] = refund_id
            payment['refund_status'] = 'PROCESSED'
            payment['refund_reason'] = reason
            payment['refunded_at'] = datetime.now().isoformat()
            
            logger.info(f"Payment refunded: {refund_id} - ₹{payment['amount']}")
            return True
        
        logger.warning(f"No payment found for booking {booking_id}")
        return False

class NotificationService:
    """Notification service for booking updates - बुकिंग अपडेट के लिए नोटिफिकेशन सर्विस"""
    
    def __init__(self):
        self.failure_rate = 0.05  # 5% notification failure rate
    
    async def send_booking_confirmation(self, booking_request: BookingRequest, 
                                      pnr: str, seats: List[str]) -> bool:
        """Send booking confirmation - बुकिंग पुष्टि भेजें"""
        await asyncio.sleep(0.5)
        
        if random.random() < self.failure_rate:
            logger.warning("Failed to send booking confirmation SMS/email")
            return False
        
        message = f"""
        🚆 IRCTC Booking Confirmed! बुकिंग पुष्टि!
        
        PNR: {pnr}
        Train: {booking_request.train_number} - {booking_request.train_name}
        Journey: {booking_request.from_station} → {booking_request.to_station}
        Date: {booking_request.journey_date}
        Seats: {', '.join(seats)}
        Class: {booking_request.travel_class.value}
        
        Happy Journey! सुखद यात्रा!
        """
        
        logger.info(f"📱 Booking confirmation sent to {booking_request.mobile_number}")
        return True
    
    async def send_cancellation_notice(self, booking_request: BookingRequest, 
                                     pnr: str, reason: str) -> bool:
        """Send cancellation notice - रद्दीकरण सूचना भेजें"""
        await asyncio.sleep(0.5)
        
        message = f"""
        ❌ IRCTC Booking Cancelled बुकिंग रद्द
        
        PNR: {pnr}
        Train: {booking_request.train_number}
        Reason: {reason}
        
        Refund will be processed in 7-10 working days.
        रिफंड 7-10 कार्य दिवसों में प्रक्रिया होगा।
        """
        
        logger.info(f"📱 Cancellation notice sent to {booking_request.mobile_number}")
        return True

class InventoryService:
    """Train inventory management - ट्रेन इन्वेंटरी प्रबंधन"""
    
    def __init__(self):
        self.inventory: Dict[str, Dict] = {}
        self.failure_rate = 0.10
    
    async def update_seat_inventory(self, train_number: str, journey_date: str, 
                                  travel_class: TrainClass, seat_count: int) -> bool:
        """Update seat inventory after booking - बुकिंग के बाद सीट इन्वेंटरी अपडेट करें"""
        await asyncio.sleep(1)
        
        if random.random() < self.failure_rate:
            raise Exception("Inventory update failed due to system maintenance")
        
        inventory_key = f"{train_number}_{journey_date}_{travel_class.value}"
        
        if inventory_key not in self.inventory:
            self.inventory[inventory_key] = {'available': 200, 'booked': 0}
        
        self.inventory[inventory_key]['available'] -= seat_count
        self.inventory[inventory_key]['booked'] += seat_count
        
        logger.info(f"Inventory updated: {inventory_key} - {seat_count} seats booked")
        return True
    
    async def restore_seat_inventory(self, train_number: str, journey_date: str, 
                                   travel_class: TrainClass, seat_count: int) -> bool:
        """Restore seat inventory after cancellation - रद्दीकरण के बाद सीट इन्वेंटरी बहाल करें"""
        await asyncio.sleep(1)
        
        inventory_key = f"{train_number}_{journey_date}_{travel_class.value}"
        
        if inventory_key in self.inventory:
            self.inventory[inventory_key]['available'] += seat_count
            self.inventory[inventory_key]['booked'] -= seat_count
            logger.info(f"Inventory restored: {inventory_key} - {seat_count} seats released")
        
        return True

class IRCTCSagaOrchestrator:
    """SAGA orchestrator for IRCTC booking - IRCTC बुकिंग के लिए SAGA ऑर्केस्ट्रेटर"""
    
    def __init__(self):
        self.booking_service = BookingService()
        self.payment_service = PaymentService()
        self.notification_service = NotificationService()
        self.inventory_service = InventoryService()
        
        self.active_sagas: Dict[str, SagaExecution] = {}
        self.completed_sagas: List[SagaExecution] = []
    
    def create_booking_saga(self, booking_request: BookingRequest) -> SagaExecution:
        """Create SAGA for booking process - बुकिंग प्रक्रिया के लिए SAGA बनाएं"""
        saga_id = str(uuid.uuid4())
        
        steps = [
            SagaStep(
                step_id="check_availability",
                step_name="Check Seat Availability",
                action=self._check_availability_action,
                compensation=self._check_availability_compensation,
                timeout_seconds=10
            ),
            SagaStep(
                step_id="reserve_seats", 
                step_name="Reserve Seats",
                action=self._reserve_seats_action,
                compensation=self._reserve_seats_compensation,
                timeout_seconds=15
            ),
            SagaStep(
                step_id="process_payment",
                step_name="Process Payment", 
                action=self._process_payment_action,
                compensation=self._process_payment_compensation,
                timeout_seconds=30
            ),
            SagaStep(
                step_id="update_inventory",
                step_name="Update Inventory",
                action=self._update_inventory_action,
                compensation=self._update_inventory_compensation,
                timeout_seconds=10
            ),
            SagaStep(
                step_id="send_confirmation",
                step_name="Send Confirmation",
                action=self._send_confirmation_action,
                compensation=self._send_confirmation_compensation,
                timeout_seconds=5
            )
        ]
        
        saga = SagaExecution(
            saga_id=saga_id,
            booking_request=booking_request,
            steps=steps
        )
        
        self.active_sagas[saga_id] = saga
        return saga
    
    async def execute_saga(self, saga: SagaExecution) -> bool:
        """Execute SAGA with compensation logic - क्षतिपूर्ति तर्क के साथ SAGA निष्पादन"""
        saga.status = SagaStatus.IN_PROGRESS
        logger.info(f"🚀 Starting SAGA {saga.saga_id} for booking {saga.booking_request.booking_id}")
        
        try:
            # Execute steps sequentially - चरणों को क्रमिक रूप से निष्पादित करें
            for i, step in enumerate(saga.steps):
                saga.current_step = i
                
                success = await self._execute_step(saga, step)
                if not success:
                    # Start compensation process - क्षतिपूर्ति प्रक्रिया शुरू करें
                    await self._compensate_saga(saga, f"Step {step.step_name} failed")
                    return False
            
            # All steps completed successfully - सभी चरण सफलतापूर्वक पूर्ण
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.now()
            
            logger.info(f"✅ SAGA {saga.saga_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ SAGA {saga.saga_id} failed with error: {e}")
            await self._compensate_saga(saga, str(e))
            return False
        finally:
            # Move to completed sagas - पूर्ण हुए SAGAs में स्थानांतरित करें
            if saga.saga_id in self.active_sagas:
                self.completed_sagas.append(saga)
                del self.active_sagas[saga.saga_id]
    
    async def _execute_step(self, saga: SagaExecution, step: SagaStep) -> bool:
        """Execute single SAGA step - एकल SAGA चरण निष्पादित करें"""
        step.status = StepStatus.STARTED
        step.started_at = datetime.now()
        
        logger.info(f"🔄 Executing step: {step.step_name}")
        
        for attempt in range(step.retry_count):
            try:
                # Execute with timeout - टाइमआउट के साथ निष्पादित करें
                result = await asyncio.wait_for(
                    step.action(saga, step),
                    timeout=step.timeout_seconds
                )
                
                if result:
                    step.status = StepStatus.COMPLETED
                    step.completed_at = datetime.now()
                    logger.info(f"✅ Step completed: {step.step_name}")
                    return True
                    
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Step timeout: {step.step_name} (attempt {attempt + 1})")
                if attempt == step.retry_count - 1:
                    step.status = StepStatus.FAILED
                    step.error_message = "Step timed out after retries"
                    
            except Exception as e:
                logger.error(f"❌ Step error: {step.step_name} - {e} (attempt {attempt + 1})")
                if attempt == step.retry_count - 1:
                    step.status = StepStatus.FAILED
                    step.error_message = str(e)
                else:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    async def _compensate_saga(self, saga: SagaExecution, reason: str):
        """Compensate SAGA by rolling back completed steps - पूर्ण चरणों को रोलबैक करके SAGA की क्षतिपूर्ति करें"""
        saga.status = SagaStatus.COMPENSATING
        saga.compensation_reason = reason
        
        logger.warning(f"🔄 Starting compensation for SAGA {saga.saga_id}: {reason}")
        
        # Compensate in reverse order - उलटे क्रम में क्षतिपूर्ति करें
        for step in reversed(saga.steps):
            if step.status == StepStatus.COMPLETED:
                step.status = StepStatus.COMPENSATING
                logger.info(f"🔄 Compensating step: {step.step_name}")
                
                try:
                    await step.compensation(saga, step)
                    step.status = StepStatus.COMPENSATED
                    logger.info(f"✅ Step compensated: {step.step_name}")
                except Exception as e:
                    logger.error(f"❌ Compensation failed for step {step.step_name}: {e}")
                    step.status = StepStatus.FAILED
        
        saga.status = SagaStatus.COMPENSATED
        saga.completed_at = datetime.now()
        
        logger.warning(f"⚠️  SAGA {saga.saga_id} compensated due to: {reason}")
    
    # SAGA Step Actions - SAGA चरण कार्रवाई
    async def _check_availability_action(self, saga: SagaExecution, step: SagaStep) -> bool:
        """Check seat availability action - सीट उपलब्धता जांच कार्रवाई"""
        request = saga.booking_request
        result = await self.booking_service.check_seat_availability(
            request.train_number,
            request.journey_date,
            request.travel_class,
            len(request.passengers)
        )
        
        step.context_data['availability_result'] = result
        saga.context['availability'] = result
        
        return result['is_available']
    
    async def _check_availability_compensation(self, saga: SagaExecution, step: SagaStep):
        """No compensation needed for availability check - उपलब्धता जांच के लिए कोई क्षतिपूर्ति की आवश्यकता नहीं"""
        pass  # No side effects to compensate
    
    async def _reserve_seats_action(self, saga: SagaExecution, step: SagaStep) -> bool:
        """Reserve seats action - सीट आरक्षण कार्रवाई"""
        reservation = await self.booking_service.reserve_seats(saga.booking_request)
        
        step.context_data['reservation'] = reservation
        saga.context['reservation'] = reservation
        
        return reservation['status'] == 'CONFIRMED'
    
    async def _reserve_seats_compensation(self, saga: SagaExecution, step: SagaStep):
        """Cancel seat reservation - सीट आरक्षण रद्द करें"""
        await self.booking_service.cancel_reservation(saga.booking_request.booking_id)
    
    async def _process_payment_action(self, saga: SagaExecution, step: SagaStep) -> bool:
        """Process payment action - भुगतान प्रक्रिया कार्रवाई"""
        payment = await self.payment_service.process_payment(saga.booking_request)
        
        step.context_data['payment'] = payment
        saga.context['payment'] = payment
        
        return payment['status'] == 'SUCCESS'
    
    async def _process_payment_compensation(self, saga: SagaExecution, step: SagaStep):
        """Refund payment - भुगतान रिफंड करें"""
        await self.payment_service.refund_payment(
            saga.booking_request.booking_id,
            saga.compensation_reason or "Booking failed"
        )
    
    async def _update_inventory_action(self, saga: SagaExecution, step: SagaStep) -> bool:
        """Update inventory action - इन्वेंटरी अपडेट कार्रवाई"""
        request = saga.booking_request
        result = await self.inventory_service.update_seat_inventory(
            request.train_number,
            request.journey_date,
            request.travel_class,
            len(request.passengers)
        )
        
        return result
    
    async def _update_inventory_compensation(self, saga: SagaExecution, step: SagaStep):
        """Restore inventory - इन्वेंटरी बहाल करें"""
        request = saga.booking_request
        await self.inventory_service.restore_seat_inventory(
            request.train_number,
            request.journey_date,
            request.travel_class,
            len(request.passengers)
        )
    
    async def _send_confirmation_action(self, saga: SagaExecution, step: SagaStep) -> bool:
        """Send confirmation action - पुष्टि भेजने की कार्रवाई"""
        reservation = saga.context.get('reservation', {})
        result = await self.notification_service.send_booking_confirmation(
            saga.booking_request,
            reservation.get('pnr', ''),
            reservation.get('seats', [])
        )
        
        return result
    
    async def _send_confirmation_compensation(self, saga: SagaExecution, step: SagaStep):
        """Send cancellation notice - रद्दीकरण सूचना भेजें"""
        reservation = saga.context.get('reservation', {})
        await self.notification_service.send_cancellation_notice(
            saga.booking_request,
            reservation.get('pnr', ''),
            saga.compensation_reason or "Booking cancelled"
        )
    
    def get_saga_status(self, saga_id: str) -> Optional[Dict[str, Any]]:
        """Get SAGA execution status - SAGA निष्पादन स्थिति प्राप्त करें"""
        saga = self.active_sagas.get(saga_id)
        if not saga:
            # Check completed sagas - पूर्ण SAGAs की जांच करें
            for completed_saga in self.completed_sagas:
                if completed_saga.saga_id == saga_id:
                    saga = completed_saga
                    break
        
        if not saga:
            return None
        
        return {
            'saga_id': saga.saga_id,
            'booking_id': saga.booking_request.booking_id,
            'status': saga.status.value,
            'current_step': saga.current_step,
            'total_steps': len(saga.steps),
            'started_at': saga.started_at.isoformat(),
            'completed_at': saga.completed_at.isoformat() if saga.completed_at else None,
            'compensation_reason': saga.compensation_reason,
            'steps': [
                {
                    'step_id': step.step_id,
                    'step_name': step.step_name,
                    'status': step.status.value,
                    'started_at': step.started_at.isoformat() if step.started_at else None,
                    'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                    'error_message': step.error_message
                }
                for step in saga.steps
            ]
        }

async def demonstrate_irctc_saga_orchestration():
    """Demonstrate SAGA orchestration for IRCTC booking"""
    """IRCTC बुकिंग के लिए SAGA ऑर्केस्ट्रेशन का प्रदर्शन"""
    
    print("🚂 Starting IRCTC SAGA Orchestration Demo")
    print("🚂 IRCTC SAGA ऑर्केस्ट्रेशन डेमो शुरू कर रहे हैं\n")
    
    # Initialize orchestrator - ऑर्केस्ट्रेटर इनिशियलाइज़ करें
    orchestrator = IRCTCSagaOrchestrator()
    
    # Create sample booking requests - नमूना बुकिंग अनुरोध बनाएं
    booking_requests = [
        BookingRequest(
            booking_id=str(uuid.uuid4()),
            user_id="USER001",
            train_number="12301",
            train_name="Howrah Rajdhani Express",
            from_station="NDLS",  # New Delhi
            to_station="HWH",     # Howrah
            journey_date="2025-02-15",
            travel_class=TrainClass.AC_2_TIER,
            passengers=[
                {"name": "राम कुमार", "age": 35, "gender": "M", "berth_preference": "Lower"},
                {"name": "सीता कुमारी", "age": 32, "gender": "F", "berth_preference": "Lower"}
            ],
            total_fare=3450.0,
            payment_method="UPI - PhonePe",
            mobile_number="9876543210",
            email="ram.kumar@example.com"
        ),
        BookingRequest(
            booking_id=str(uuid.uuid4()),
            user_id="USER002", 
            train_number="12009",
            train_name="Shatabdi Express",
            from_station="NDLS",  # New Delhi
            to_station="CDG",     # Chandigarh
            journey_date="2025-02-20",
            travel_class=TrainClass.CC,
            passengers=[
                {"name": "अमित शर्मा", "age": 28, "gender": "M", "berth_preference": "Window"}
            ],
            total_fare=1250.0,
            payment_method="Credit Card",
            mobile_number="9123456789",
            email="amit.sharma@example.com"
        ),
        BookingRequest(
            booking_id=str(uuid.uuid4()),
            user_id="USER003",
            train_number="12951",
            train_name="Mumbai Rajdhani",
            from_station="NDLS",  # New Delhi  
            to_station="MMCT",    # Mumbai Central
            journey_date="2025-02-25",
            travel_class=TrainClass.AC_3_TIER,
            passengers=[
                {"name": "प्रिया गुप्ता", "age": 26, "gender": "F", "berth_preference": "Upper"},
                {"name": "विकास गुप्ता", "age": 30, "gender": "M", "berth_preference": "Middle"},
                {"name": "आर्या गुप्ता", "age": 5, "gender": "F", "berth_preference": "Lower"}
            ],
            total_fare=4850.0,
            payment_method="Net Banking - HDFC",
            mobile_number="9988776655",
            email="priya.gupta@example.com"
        )
    ]
    
    # Process bookings with SAGA orchestration - SAGA ऑर्केस्ट्रेशन के साथ बुकिंग प्रक्रिया करें
    saga_results = []
    
    for i, booking_request in enumerate(booking_requests):
        print(f"🎫 Processing Booking {i+1}: {booking_request.train_name}")
        print(f"   Route: {booking_request.from_station} → {booking_request.to_station}")
        print(f"   Date: {booking_request.journey_date}")
        print(f"   Passengers: {len(booking_request.passengers)}")
        print(f"   Fare: ₹{booking_request.total_fare:,.2f}")
        
        # Create and execute SAGA - SAGA बनाएं और निष्पादित करें
        saga = orchestrator.create_booking_saga(booking_request)
        
        print(f"   🚀 Starting SAGA {saga.saga_id[:8]}...")
        
        # Execute SAGA - SAGA निष्पादित करें
        success = await orchestrator.execute_saga(saga)
        saga_results.append((saga, success))
        
        if success:
            reservation = saga.context.get('reservation', {})
            print(f"   ✅ Booking successful! PNR: {reservation.get('pnr', 'N/A')}")
        else:
            print(f"   ❌ Booking failed: {saga.compensation_reason}")
        
        print()
        
        # Small delay between bookings - बुकिंग के बीच छोटी देरी
        await asyncio.sleep(1)
    
    # Show detailed SAGA status - विस्तृत SAGA स्थिति दिखाएं
    print("📊 SAGA Execution Summary - SAGA निष्पादन सारांश:")
    print("=" * 60)
    
    for i, (saga, success) in enumerate(saga_results):
        print(f"\n🎫 Booking {i+1} - {saga.booking_request.train_name}")
        print(f"   SAGA ID: {saga.saga_id}")
        print(f"   Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"   Duration: {(saga.completed_at - saga.started_at).total_seconds():.2f}s")
        
        if not success:
            print(f"   Failure Reason: {saga.compensation_reason}")
        
        print(f"   Step Details:")
        for step in saga.steps:
            status_emoji = {
                StepStatus.COMPLETED: "✅",
                StepStatus.COMPENSATED: "🔄", 
                StepStatus.FAILED: "❌",
                StepStatus.PENDING: "⏳"
            }.get(step.status, "❓")
            
            print(f"     {status_emoji} {step.step_name}: {step.status.value}")
            if step.error_message:
                print(f"        Error: {step.error_message}")
    
    # Show success/failure statistics - सफलता/विफलता आंकड़े दिखाएं
    successful_bookings = sum(1 for _, success in saga_results if success)
    failed_bookings = len(saga_results) - successful_bookings
    
    print(f"\n📈 Overall Statistics - समग्र आंकड़े:")
    print(f"   Total Bookings: {len(saga_results)}")
    print(f"   Successful: {successful_bookings} ({successful_bookings/len(saga_results)*100:.1f}%)")
    print(f"   Failed: {failed_bookings} ({failed_bookings/len(saga_results)*100:.1f}%)")
    
    # Show service failure rates - सेवा विफलता दर दिखाएं
    print(f"\n🔧 Service Configuration - सेवा कॉन्फ़िगरेशन:")
    print(f"   Booking Service Failure Rate: {orchestrator.booking_service.failure_rate:.1%}")
    print(f"   Payment Service Failure Rate: {orchestrator.payment_service.failure_rate:.1%}")
    print(f"   Notification Service Failure Rate: {orchestrator.notification_service.failure_rate:.1%}")
    print(f"   Inventory Service Failure Rate: {orchestrator.inventory_service.failure_rate:.1%}")
    
    print("\n✅ IRCTC SAGA Orchestration Demo Complete!")
    print("✅ IRCTC SAGA ऑर्केस्ट्रेशन डेमो पूरा हुआ!")

if __name__ == "__main__":
    """
    Run the IRCTC SAGA orchestration demonstration
    IRCTC SAGA ऑर्केस्ट्रेशन प्रदर्शन चलाएं
    
    This demonstrates:
    यह प्रदर्शित करता है:
    
    1. Orchestrator-based SAGA pattern - ऑर्केस्ट्रेटर-आधारित SAGA पैटर्न
    2. Distributed transaction coordination - वितरित लेन-देन समन्वय
    3. Compensation actions for failure recovery - विफलता रिकवरी के लिए क्षतिपूर्ति कार्रवाई
    4. Step-by-step execution with timeouts - टाइमआउट के साथ चरणबद्ध निष्पादन
    5. Retry mechanisms and error handling - retry तंत्र और त्रुटि हैंडलिंग
    6. Real-world IRCTC booking workflow - वास्तविक IRCTC बुकिंग वर्कफ़्लो
    
    Key learnings:
    मुख्य सीख:
    
    - SAGA pattern ensures data consistency across services - SAGA पैटर्न सेवाओं में डेटा स्थिरता सुनिश्चित करता है
    - Compensation logic provides automatic rollback - क्षतिपूर्ति तर्क स्वचालित रोलबैक प्रदान करता है  
    - Orchestrator coordinates complex distributed transactions - ऑर्केस्ट्रेटर जटिल वितरित लेन-देन का समन्वय करता है
    - Retry and timeout mechanisms improve reliability - retry और टाइमआउट तंत्र विश्वसनीयता में सुधार करते हैं
    - Step isolation enables partial success handling - चरण अलगाव आंशिक सफलता हैंडलिंग सक्षम बनाता है
    """
    
    try:
        asyncio.run(demonstrate_irctc_saga_orchestration())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user - डेमो उपयोगकर्ता द्वारा बाधित")
    except Exception as e:
        print(f"\n❌ Demo failed with error - डेमो त्रुटि के साथ असफल: {e}")
        raise