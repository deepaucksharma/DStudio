"""
RabbitMQ Message Queue for IRCTC-style Train Booking System
Reliable asynchronous messaging with work queues and routing

Author: Episode 9 - Microservices Communication
Context: IRCTC jaise train booking - message queues for reliability aur scaling
"""

import pika
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
from decimal import Decimal
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Hindi logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enums for booking management
class BookingStatus(Enum):
    INITIATED = "INITIATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    WAITLISTED = "WAITLISTED"
    RAC = "RAC"

class PassengerClass(Enum):
    SL = "SL"  # Sleeper
    AC3 = "3A"  # AC 3 Tier
    AC2 = "2A"  # AC 2 Tier
    AC1 = "1A"  # AC 1 Tier
    CC = "CC"  # Chair Car

class MessageType(Enum):
    BOOKING_REQUEST = "BOOKING_REQUEST"
    PAYMENT_PROCESSING = "PAYMENT_PROCESSING"
    SEAT_ALLOCATION = "SEAT_ALLOCATION"
    BOOKING_CONFIRMATION = "BOOKING_CONFIRMATION"
    WAITLIST_UPDATE = "WAITLIST_UPDATE"
    NOTIFICATION = "NOTIFICATION"

# Data models
@dataclass
class Passenger:
    name: str
    age: int
    gender: str
    phone: str = ""

@dataclass
class BookingRequest:
    booking_id: str
    user_id: str
    train_number: str
    train_name: str
    source_station: str
    destination_station: str
    journey_date: str
    passenger_class: PassengerClass
    passengers: List[Passenger]
    total_amount: Decimal
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class PaymentRequest:
    payment_id: str
    booking_id: str
    amount: Decimal
    payment_method: str
    gateway: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SeatAllocation:
    booking_id: str
    coach_number: str
    seat_numbers: List[str]
    berth_preference: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class BookingConfirmation:
    booking_id: str
    pnr_number: str
    status: BookingStatus
    seat_details: Optional[SeatAllocation] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# Custom JSON encoder for RabbitMQ messages
class RabbitMQEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if hasattr(obj, 'value'):  # Enums
            return obj.value
        if hasattr(obj, '__dict__'):  # Dataclasses
            return asdict(obj)
        return super().default(obj)

class IRCTCRabbitMQSystem:
    """
    Production-ready RabbitMQ message system for IRCTC train booking
    
    Features:
    - Work queues for booking processing
    - Direct exchanges for targeted messaging
    - Topic exchanges for flexible routing
    - Dead letter queues for failed messages
    - Message persistence
    - Acknowledgements and retries
    """
    
    def __init__(self, rabbitmq_url: str = 'amqp://localhost'):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        
        # Exchange and queue names
        self.exchanges = {
            'booking_direct': 'irctc.booking.direct',
            'booking_topic': 'irctc.booking.topic',
            'notifications': 'irctc.notifications'
        }
        
        self.queues = {
            'booking_requests': 'booking.requests',
            'payment_processing': 'payment.processing',
            'seat_allocation': 'seat.allocation',
            'booking_confirmation': 'booking.confirmation',
            'waitlist_management': 'waitlist.management',
            'notifications': 'notifications.queue',
            'dead_letter': 'dead.letter.queue'
        }
        
        # Message counters
        self.message_counts = {queue: 0 for queue in self.queues.keys()}
        self.processing_errors = 0
        
        # Thread pool for consumers
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.consumer_threads = []
        self.running = True
        
        logger.info("IRCTC RabbitMQ System initializing...")
        self._setup_rabbitmq_infrastructure()
    
    def _setup_rabbitmq_infrastructure(self):
        """RabbitMQ connection aur infrastructure setup karta hai"""
        try:
            # Establish connection
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            
            # Declare exchanges
            self.channel.exchange_declare(
                exchange=self.exchanges['booking_direct'],
                exchange_type='direct',
                durable=True
            )
            
            self.channel.exchange_declare(
                exchange=self.exchanges['booking_topic'],
                exchange_type='topic',
                durable=True
            )
            
            self.channel.exchange_declare(
                exchange=self.exchanges['notifications'],
                exchange_type='fanout',
                durable=True
            )
            
            # Declare dead letter exchange
            self.channel.exchange_declare(
                exchange='dead_letter_exchange',
                exchange_type='direct',
                durable=True
            )
            
            # Declare queues with appropriate settings
            self._declare_queues()
            
            logger.info("RabbitMQ infrastructure setup completed")
            
        except Exception as e:
            logger.error(f"RabbitMQ setup failed: {e}")
            raise
    
    def _declare_queues(self):
        """All required queues declare karta hai"""
        # Dead letter queue (for failed messages)
        self.channel.queue_declare(
            queue=self.queues['dead_letter'],
            durable=True
        )
        
        # Bind dead letter queue
        self.channel.queue_bind(
            exchange='dead_letter_exchange',
            queue=self.queues['dead_letter']
        )
        
        # Main processing queues with dead letter routing
        queue_configs = [
            {
                'name': self.queues['booking_requests'],
                'routing_key': 'booking.request',
                'exchange': self.exchanges['booking_direct']
            },
            {
                'name': self.queues['payment_processing'],
                'routing_key': 'booking.payment',
                'exchange': self.exchanges['booking_direct']
            },
            {
                'name': self.queues['seat_allocation'],
                'routing_key': 'booking.seat.*',
                'exchange': self.exchanges['booking_topic']
            },
            {
                'name': self.queues['booking_confirmation'],
                'routing_key': 'booking.confirm',
                'exchange': self.exchanges['booking_direct']
            },
            {
                'name': self.queues['waitlist_management'],
                'routing_key': 'booking.waitlist.*',
                'exchange': self.exchanges['booking_topic']
            },
            {
                'name': self.queues['notifications'],
                'routing_key': '',  # Fanout exchange doesn't need routing key
                'exchange': self.exchanges['notifications']
            }
        ]
        
        for config in queue_configs:
            # Declare queue with dead letter routing
            self.channel.queue_declare(
                queue=config['name'],
                durable=True,
                arguments={
                    'x-dead-letter-exchange': 'dead_letter_exchange',
                    'x-dead-letter-routing-key': 'dead_letter',
                    'x-message-ttl': 3600000,  # 1 hour TTL
                    'x-max-retries': 3
                }
            )
            
            # Bind queue to exchange
            if config['exchange'] == self.exchanges['booking_topic']:
                self.channel.queue_bind(
                    exchange=config['exchange'],
                    queue=config['name'],
                    routing_key=config['routing_key']
                )
            elif config['exchange'] == self.exchanges['notifications']:
                self.channel.queue_bind(
                    exchange=config['exchange'],
                    queue=config['name']
                )
            else:
                self.channel.queue_bind(
                    exchange=config['exchange'],
                    queue=config['name'],
                    routing_key=config['routing_key']
                )
        
        logger.info(f"Declared {len(queue_configs)} queues with bindings")
    
    def publish_booking_request(self, booking_request: BookingRequest):
        """Booking request message publish karta hai"""
        try:
            message = {
                'message_type': MessageType.BOOKING_REQUEST.value,
                'data': booking_request
            }
            
            message_json = json.dumps(message, cls=RabbitMQEncoder)
            
            self.channel.basic_publish(
                exchange=self.exchanges['booking_direct'],
                routing_key='booking.request',
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    message_id=str(uuid.uuid4()),
                    timestamp=int(time.time()),
                    content_type='application/json'
                )
            )
            
            self.message_counts['booking_requests'] += 1
            
            logger.info(f"Booking request published: {booking_request.booking_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish booking request: {e}")
            raise
    
    def publish_payment_request(self, payment_request: PaymentRequest):
        """Payment processing request publish karta hai"""
        try:
            message = {
                'message_type': MessageType.PAYMENT_PROCESSING.value,
                'data': payment_request
            }
            
            message_json = json.dumps(message, cls=RabbitMQEncoder)
            
            self.channel.basic_publish(
                exchange=self.exchanges['booking_direct'],
                routing_key='booking.payment',
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    message_id=str(uuid.uuid4()),
                    timestamp=int(time.time())
                )
            )
            
            self.message_counts['payment_processing'] += 1
            
            logger.info(f"Payment request published: {payment_request.payment_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish payment request: {e}")
            raise
    
    def publish_seat_allocation(self, seat_allocation: SeatAllocation, seat_class: str):
        """Seat allocation message publish karta hai (Topic exchange)"""
        try:
            message = {
                'message_type': MessageType.SEAT_ALLOCATION.value,
                'data': seat_allocation
            }
            
            message_json = json.dumps(message, cls=RabbitMQEncoder)
            
            # Dynamic routing key based on class
            routing_key = f'booking.seat.{seat_class.lower()}'
            
            self.channel.basic_publish(
                exchange=self.exchanges['booking_topic'],
                routing_key=routing_key,
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    message_id=str(uuid.uuid4()),
                    timestamp=int(time.time())
                )
            )
            
            self.message_counts['seat_allocation'] += 1
            
            logger.info(f"Seat allocation published: {seat_allocation.booking_id} ({routing_key})")
            
        except Exception as e:
            logger.error(f"Failed to publish seat allocation: {e}")
            raise
    
    def publish_booking_confirmation(self, confirmation: BookingConfirmation):
        """Booking confirmation publish karta hai"""
        try:
            message = {
                'message_type': MessageType.BOOKING_CONFIRMATION.value,
                'data': confirmation
            }
            
            message_json = json.dumps(message, cls=RabbitMQEncoder)
            
            self.channel.basic_publish(
                exchange=self.exchanges['booking_direct'],
                routing_key='booking.confirm',
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    message_id=str(uuid.uuid4()),
                    timestamp=int(time.time())
                )
            )
            
            self.message_counts['booking_confirmation'] += 1
            
            logger.info(f"Booking confirmation published: {confirmation.pnr_number}")
            
        except Exception as e:
            logger.error(f"Failed to publish booking confirmation: {e}")
            raise
    
    def publish_notification(self, notification: Dict):
        """Notification broadcast karta hai (Fanout exchange)"""
        try:
            message = {
                'message_type': MessageType.NOTIFICATION.value,
                'data': notification,
                'timestamp': datetime.now().isoformat()
            }
            
            message_json = json.dumps(message, cls=RabbitMQEncoder)
            
            self.channel.basic_publish(
                exchange=self.exchanges['notifications'],
                routing_key='',  # Fanout doesn't use routing key
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    message_id=str(uuid.uuid4()),
                    timestamp=int(time.time())
                )
            )
            
            self.message_counts['notifications'] += 1
            
            logger.info(f"Notification broadcasted: {notification.get('title', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to publish notification: {e}")
            raise
    
    def start_booking_request_consumer(self):
        """Booking request consumer start karta hai"""
        def consume_booking_requests():
            try:
                # Create new connection for this thread
                connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
                channel = connection.channel()
                
                def callback(ch, method, properties, body):
                    try:
                        message_data = json.loads(body)
                        booking_data = message_data['data']
                        
                        logger.info(f"Processing booking request: {booking_data['booking_id']}")
                        
                        # Simulate booking processing
                        self._process_booking_request(booking_data)
                        
                        # Acknowledge message
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
                    except Exception as e:
                        logger.error(f"Booking request processing failed: {e}")
                        self.processing_errors += 1
                        # Reject message (will go to dead letter queue after retries)
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
                # Set QoS to process one message at a time
                channel.basic_qos(prefetch_count=1)
                
                channel.basic_consume(
                    queue=self.queues['booking_requests'],
                    on_message_callback=callback
                )
                
                logger.info("Started booking request consumer")
                channel.start_consuming()
                
            except Exception as e:
                logger.error(f"Booking consumer error: {e}")
        
        # Start consumer in thread
        thread = threading.Thread(target=consume_booking_requests, daemon=True)
        thread.start()
        self.consumer_threads.append(thread)
        
        return thread
    
    def _process_booking_request(self, booking_data: Dict):
        """
        Booking request ki actual processing
        Production mein complex business logic hogi
        """
        # Simulate processing time
        time.sleep(0.5)
        
        booking_id = booking_data['booking_id']
        
        # Simulate availability check (70% success rate)
        if hash(booking_id) % 10 < 7:
            # Seats available - proceed with payment
            payment_request = PaymentRequest(
                payment_id=f"pay_{booking_id}",
                booking_id=booking_id,
                amount=Decimal(booking_data['total_amount']),
                payment_method="UPI",
                gateway="IRCTC_PG"
            )
            
            # Publish payment request
            self.publish_payment_request(payment_request)
            
        else:
            # No seats - add to waitlist
            waitlist_message = {
                'booking_id': booking_id,
                'status': 'WAITLISTED',
                'position': hash(booking_id) % 50 + 1
            }
            
            # Publish to waitlist queue using topic routing
            routing_key = f'booking.waitlist.{booking_data["passenger_class"]}'
            
            message_json = json.dumps({
                'message_type': 'WAITLIST_UPDATE',
                'data': waitlist_message
            }, cls=RabbitMQEncoder)
            
            self.channel.basic_publish(
                exchange=self.exchanges['booking_topic'],
                routing_key=routing_key,
                body=message_json,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            logger.info(f"Booking waitlisted: {booking_id}")
    
    def start_payment_consumer(self):
        """Payment processing consumer start karta hai"""
        def consume_payments():
            try:
                connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
                channel = connection.channel()
                
                def callback(ch, method, properties, body):
                    try:
                        message_data = json.loads(body)
                        payment_data = message_data['data']
                        
                        logger.info(f"Processing payment: {payment_data['payment_id']}")
                        
                        # Simulate payment processing
                        self._process_payment(payment_data)
                        
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
                    except Exception as e:
                        logger.error(f"Payment processing failed: {e}")
                        self.processing_errors += 1
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue=self.queues['payment_processing'],
                    on_message_callback=callback
                )
                
                logger.info("Started payment consumer")
                channel.start_consuming()
                
            except Exception as e:
                logger.error(f"Payment consumer error: {e}")
        
        thread = threading.Thread(target=consume_payments, daemon=True)
        thread.start()
        self.consumer_threads.append(thread)
        
        return thread
    
    def _process_payment(self, payment_data: Dict):
        """Payment processing logic"""
        time.sleep(0.3)  # Simulate payment gateway time
        
        payment_id = payment_data['payment_id']
        booking_id = payment_data['booking_id']
        
        # Simulate payment success (90% success rate)
        if hash(payment_id) % 10 < 9:
            # Payment successful - allocate seats
            seat_allocation = SeatAllocation(
                booking_id=booking_id,
                coach_number=f"S{hash(booking_id) % 10 + 1}",
                seat_numbers=[f"{hash(booking_id) % 72 + 1}", f"{hash(booking_id) % 72 + 2}"],
                berth_preference="Lower"
            )
            
            # Publish seat allocation
            passenger_class = "SL"  # Default for demo
            self.publish_seat_allocation(seat_allocation, passenger_class)
            
            # Generate PNR and confirmation
            pnr_number = f"{int(time.time()) % 10000:04d}{hash(booking_id) % 1000000:06d}"
            
            confirmation = BookingConfirmation(
                booking_id=booking_id,
                pnr_number=pnr_number,
                status=BookingStatus.CONFIRMED,
                seat_details=seat_allocation
            )
            
            # Publish confirmation
            self.publish_booking_confirmation(confirmation)
            
            # Send notification
            notification = {
                'title': 'Booking Confirmed!',
                'message': f'Your booking is confirmed. PNR: {pnr_number}',
                'booking_id': booking_id,
                'pnr': pnr_number
            }
            
            self.publish_notification(notification)
            
            logger.info(f"Payment successful, booking confirmed: PNR {pnr_number}")
            
        else:
            # Payment failed
            logger.info(f"Payment failed for booking: {booking_id}")
    
    def simulate_booking_flow(self, num_bookings: int = 5):
        """Complete booking flow simulate karta hai"""
        logger.info(f"Simulating {num_bookings} train bookings...")
        
        # Sample train data
        trains = [
            ("12301", "Rajdhani Express", "NDLS", "HWH", "AC2"),
            ("12951", "Mumbai Rajdhani", "MMCT", "NDLS", "AC3"),
            ("12002", "Shatabdi Express", "NDLS", "HWH", "CC"),
            ("16587", "Yesvantpur Express", "YPR", "BZA", "SL"),
            ("12621", "Tamil Nadu Express", "NDLS", "MS", "SL")
        ]
        
        for i in range(num_bookings):
            train_data = trains[i % len(trains)]
            
            booking_request = BookingRequest(
                booking_id=f"book_{int(time.time())}_{i:03d}",
                user_id=f"user_{hash(str(i)) % 10000:04d}",
                train_number=train_data[0],
                train_name=train_data[1],
                source_station=train_data[2],
                destination_station=train_data[3],
                journey_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                passenger_class=PassengerClass(train_data[4]),
                passengers=[
                    Passenger("Rahul Sharma", 32, "M", "+91-9876543210"),
                    Passenger("Priya Sharma", 28, "F", "+91-9876543211")
                ],
                total_amount=Decimal("1250.00")
            )
            
            # Publish booking request
            self.publish_booking_request(booking_request)
            
            # Small delay between bookings
            time.sleep(0.2)
        
        logger.info(f"Published {num_bookings} booking requests")
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """Queue statistics aur message counts"""
        try:
            stats = {}
            
            for queue_name in self.queues.values():
                method = self.channel.queue_declare(queue=queue_name, passive=True)
                stats[queue_name] = {
                    'message_count': method.method.message_count,
                    'consumer_count': method.method.consumer_count
                }
            
            return {
                'queue_stats': stats,
                'published_counts': self.message_counts.copy(),
                'processing_errors': self.processing_errors,
                'active_consumers': len(self.consumer_threads)
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue statistics: {e}")
            return {}
    
    def shutdown(self):
        """Gracefully shutdown all consumers and connection"""
        logger.info("Shutting down IRCTC RabbitMQ system...")
        
        self.running = False
        
        # Wait for consumer threads to finish
        for thread in self.consumer_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        # Close connection
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        
        self.executor.shutdown(wait=True)
        
        logger.info("IRCTC RabbitMQ system shutdown complete")


def run_irctc_rabbitmq_demo():
    """
    Complete IRCTC RabbitMQ messaging demo
    Production-ready example with multiple message patterns
    """
    print("🚂 IRCTC Train Booking - RabbitMQ Message System")
    print("="*65)
    
    try:
        # Initialize RabbitMQ system
        irctc_system = IRCTCRabbitMQSystem()
        
        print(f"\n📋 Message Infrastructure:")
        print(f"   • Exchanges: {len(irctc_system.exchanges)}")
        print(f"   • Queues: {len(irctc_system.queues)}")
        print(f"   • Dead letter queue configured")
        print(f"   • Message persistence enabled")
        
        # Start consumers
        print(f"\n🔄 Starting Message Consumers...")
        booking_consumer = irctc_system.start_booking_request_consumer()
        payment_consumer = irctc_system.start_payment_consumer()
        
        # Let consumers start
        time.sleep(2)
        
        # Simulate booking requests
        print(f"\n🚀 Simulating Train Bookings...")
        irctc_system.simulate_booking_flow(num_bookings=8)
        
        # Let messages process
        print(f"\n⏳ Processing bookings (waiting 10 seconds)...")
        time.sleep(10)
        
        # Show statistics
        stats = irctc_system.get_queue_statistics()
        
        print(f"\n📊 Message Processing Statistics:")
        
        if 'published_counts' in stats:
            print(f"   Messages Published:")
            for queue, count in stats['published_counts'].items():
                if count > 0:
                    print(f"     • {queue}: {count}")
        
        if 'queue_stats' in stats:
            print(f"   Queue Status:")
            for queue, queue_stats in stats['queue_stats'].items():
                if queue_stats['message_count'] > 0 or queue_stats['consumer_count'] > 0:
                    print(f"     • {queue}: {queue_stats['message_count']} messages, "
                         f"{queue_stats['consumer_count']} consumers")
        
        print(f"   Processing Errors: {stats.get('processing_errors', 0)}")
        print(f"   Active Consumers: {stats.get('active_consumers', 0)}")
        
        print(f"\n⚡ RabbitMQ Benefits Demonstrated:")
        print(f"   ✅ Reliable message delivery with acknowledgements")
        print(f"   ✅ Work queue distribution among consumers")
        print(f"   ✅ Flexible routing (direct, topic, fanout)")
        print(f"   ✅ Message persistence across restarts")
        print(f"   ✅ Dead letter queues for error handling")
        print(f"   ✅ QoS control and flow control")
        print(f"   ✅ Multiple exchange types for different patterns")
        
        print(f"\n🏭 Production Features:")
        print(f"   • Clustering for high availability")
        print(f"   • Federation for distributed deployments")
        print(f"   • Management UI for monitoring")
        print(f"   • Message TTL and priority queues")
        print(f"   • Publisher confirms for guaranteed delivery")
        print(f"   • Shovel and exchange-to-exchange bindings")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        print(f"💡 Make sure RabbitMQ is running:")
        print(f"   • docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management")
        print(f"   • Management UI: http://localhost:15672 (guest/guest)")
        
    finally:
        # Cleanup
        try:
            irctc_system.shutdown()
        except:
            pass

if __name__ == "__main__":
    # Run the IRCTC RabbitMQ demo
    run_irctc_rabbitmq_demo()
    
    print("\n" + "="*65)
    print("📚 LEARNING POINTS:")
    print("• RabbitMQ AMQP protocol use karta hai - reliable messaging")
    print("• Multiple exchange types different routing patterns provide karte hai")
    print("• Work queues automatic load balancing karte hai consumers mein")
    print("• Message acknowledgements prevent data loss")
    print("• Dead letter queues failed messages handle karte hai")
    print("• Durable queues aur persistent messages survive server restarts")
    print("• Publisher confirms guarantee message delivery")
    
    print("\n🔧 Advanced RabbitMQ Patterns:")
    print("• Request-Reply pattern with correlation IDs")
    print("• Priority queues for urgent messages")
    print("• Message TTL for automatic cleanup")
    print("• Delayed messages with plugins")
    print("• Consistent hash exchange for sharding")
    print("• Federation for multi-datacenter setups")