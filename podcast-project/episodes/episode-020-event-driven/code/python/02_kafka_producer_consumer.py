#!/usr/bin/env python3
"""
Apache Kafka Producer/Consumer Implementation
उदाहरण: Ola cab booking events को Kafka के through handle करना

Setup:
pip install kafka-python asyncio

Docker setup for Kafka:
docker run -d --name zookeeper -p 2181:2181 confluentinc/cp-zookeeper:latest
docker run -d --name kafka -p 9092:9092 --link zookeeper confluentinc/cp-kafka:latest

Indian Context: Ola app mein jab customer cab book karta hai,
real-time events ko handle karna padta hai:
- Driver assignment
- Ride tracking
- Payment processing
- Customer notifications
- Analytics data
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import threading

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class OlaRideEvent:
    """Ola ride event structure"""
    event_id: str
    event_type: str
    ride_id: str
    customer_id: str
    driver_id: str = None
    pickup_location: Dict[str, float] = None
    drop_location: Dict[str, float] = None
    fare: float = 0.0
    status: str = "requested"
    timestamp: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.metadata:
            self.metadata = {}

class OlaKafkaProducer:
    """
    Ola ride events ka producer
    Mumbai traffic ki tarah - continuous flow of events
    """
    
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # Production settings for reliability
            acks='all',  # Wait for all replicas
            retries=3,
            batch_size=16384,
            linger_ms=10,  # Wait 10ms for batching
            buffer_memory=33554432  # 32MB buffer
        )
        
    async def publish_ride_event(self, event: OlaRideEvent, topic: str = 'ola-rides'):
        """
        Ride event ko Kafka topic par publish karna
        Local train announcement ki tarah - sabko pata chal jaana chahiye
        """
        try:
            # Event ko dictionary mein convert karna
            event_dict = asdict(event)
            
            # Ride ID ko key ke roop mein use karna - same ride ke events same partition mein jayenge
            key = event.ride_id
            
            logger.info(f"🚗 Publishing {event.event_type} for ride {event.ride_id}")
            
            # Send event to Kafka
            future = self.producer.send(
                topic=topic,
                key=key,
                value=event_dict,
                partition=None  # Let Kafka decide based on key
            )
            
            # Async result get karna
            record_metadata = future.get(timeout=10)
            
            logger.info(f"✅ Event published to partition {record_metadata.partition}, "
                       f"offset {record_metadata.offset}")
            
            return record_metadata
            
        except KafkaError as e:
            logger.error(f"❌ Failed to publish event: {e}")
            raise
    
    def close(self):
        """Producer close karna"""
        self.producer.close()

class OlaKafkaConsumer:
    """
    Ola ride events ka consumer
    Different services ke liye different consumer groups
    """
    
    def __init__(self, topic: str, consumer_group: str, 
                 bootstrap_servers='localhost:9092'):
        self.topic = topic
        self.consumer_group = consumer_group
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=consumer_group,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            # Consumer settings for reliability
            auto_offset_reset='latest',  # Start from latest messages
            enable_auto_commit=False,    # Manual commit for better control
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000
        )
        self.running = False
        
    def start_consuming(self, message_handler):
        """
        Message consumption start karna
        Mumbai local ki tarah - continuously चलता रहता है
        """
        self.running = True
        logger.info(f"🎧 Started consuming from topic '{self.topic}' "
                   f"with group '{self.consumer_group}'")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                try:
                    # Message process karna
                    event_data = message.value
                    key = message.key
                    
                    logger.info(f"📨 Received message - Key: {key}, "
                               f"Partition: {message.partition}, "
                               f"Offset: {message.offset}")
                    
                    # Handler call karna
                    success = message_handler(event_data)
                    
                    if success:
                        # Manual commit after successful processing
                        self.consumer.commit()
                        logger.debug(f"✅ Message committed - Offset: {message.offset}")
                    else:
                        logger.warning(f"⚠️ Message processing failed - will retry")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    
        except KeyboardInterrupt:
            logger.info("🛑 Consumer interrupted by user")
        finally:
            self.stop()
    
    def stop(self):
        """Consumer stop karna"""
        self.running = False
        self.consumer.close()
        logger.info(f"🔴 Consumer stopped for group '{self.consumer_group}'")

# Different services for handling Ola events

class DriverAssignmentService:
    """Driver assignment service - ride ke liye driver dhundhna"""
    
    def __init__(self):
        self.service_name = "Driver Assignment Service"
        self.available_drivers = [
            {"id": "DRV001", "name": "Ramesh Kumar", "location": {"lat": 19.0760, "lng": 72.8777}},
            {"id": "DRV002", "name": "Suresh Patil", "location": {"lat": 19.0896, "lng": 72.8656}},
            {"id": "DRV003", "name": "Amit Singh", "location": {"lat": 19.0728, "lng": 72.8826}},
        ]
    
    def handle_ride_request(self, event_data: Dict) -> bool:
        """Ride request par driver assign karna"""
        try:
            ride_id = event_data.get('ride_id')
            pickup_location = event_data.get('pickup_location')
            
            logger.info(f"🚗 {self.service_name}: Processing ride request {ride_id}")
            logger.info(f"   📍 Pickup: {pickup_location}")
            
            # Nearest driver find karna (simplified)
            import random
            selected_driver = random.choice(self.available_drivers)
            
            # Driver assignment simulation
            time.sleep(0.5)
            
            logger.info(f"✅ Driver assigned: {selected_driver['name']} ({selected_driver['id']})")
            
            # यहाँ driver assignment का event publish करना चाहिए
            # But for demo, just logging
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Driver assignment failed: {e}")
            return False

class RideTrackingService:
    """Ride tracking service - location updates handle karna"""
    
    def __init__(self):
        self.service_name = "Ride Tracking Service"
    
    def handle_ride_started(self, event_data: Dict) -> bool:
        """Ride start hone par tracking start karna"""
        try:
            ride_id = event_data.get('ride_id')
            driver_id = event_data.get('driver_id')
            
            logger.info(f"📍 {self.service_name}: Starting tracking for ride {ride_id}")
            logger.info(f"   🚗 Driver: {driver_id}")
            
            # GPS tracking start karna
            time.sleep(0.3)
            
            logger.info(f"✅ Tracking started for ride {ride_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Tracking start failed: {e}")
            return False

class PaymentService:
    """Payment processing service"""
    
    def __init__(self):
        self.service_name = "Payment Service"
    
    def handle_ride_completed(self, event_data: Dict) -> bool:
        """Ride complete hone par payment process karna"""
        try:
            ride_id = event_data.get('ride_id')
            fare = event_data.get('fare', 0)
            customer_id = event_data.get('customer_id')
            
            logger.info(f"💳 {self.service_name}: Processing payment for ride {ride_id}")
            logger.info(f"   💰 Fare: ₹{fare}")
            logger.info(f"   👤 Customer: {customer_id}")
            
            # Payment processing via UPI/Card
            time.sleep(0.7)
            
            # Payment success simulation (95% success rate)
            import random
            success = random.random() > 0.05
            
            if success:
                txn_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
                logger.info(f"✅ Payment successful - Transaction: {txn_id}")
            else:
                logger.info(f"❌ Payment failed - will retry")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Payment processing failed: {e}")
            return False

class AnalyticsService:
    """Analytics aur reporting service"""
    
    def __init__(self):
        self.service_name = "Analytics Service"
        self.ride_metrics = []
    
    def handle_any_ride_event(self, event_data: Dict) -> bool:
        """Har ride event ko analytics ke liye track karna"""
        try:
            event_type = event_data.get('event_type')
            ride_id = event_data.get('ride_id')
            timestamp = event_data.get('timestamp')
            
            logger.info(f"📊 {self.service_name}: Recording {event_type} for {ride_id}")
            
            # Metrics collection
            metric = {
                'ride_id': ride_id,
                'event_type': event_type,
                'timestamp': timestamp,
                'processed_at': datetime.now().isoformat()
            }
            
            self.ride_metrics.append(metric)
            
            # Analytics processing simulation
            time.sleep(0.1)
            
            logger.info(f"✅ Analytics recorded - Total metrics: {len(self.ride_metrics)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analytics processing failed: {e}")
            return False

async def simulate_ola_rides():
    """Ola ride simulation - multiple rides ko handle karna"""
    
    producer = OlaKafkaProducer()
    
    try:
        # Sample ride requests
        rides = [
            {
                "customer_id": "CUST001",
                "pickup": {"lat": 19.0760, "lng": 72.8777, "address": "Andheri West"},
                "drop": {"lat": 19.0896, "lng": 72.8656, "address": "Goregaon East"},
                "fare": 180.0
            },
            {
                "customer_id": "CUST002", 
                "pickup": {"lat": 19.0728, "lng": 72.8826, "address": "Juhu Beach"},
                "drop": {"lat": 19.0544, "lng": 72.8324, "address": "Bandra West"},
                "fare": 120.0
            }
        ]
        
        for ride_data in rides:
            ride_id = f"RIDE{uuid.uuid4().hex[:8].upper()}"
            
            # Ride request event
            request_event = OlaRideEvent(
                event_id=str(uuid.uuid4()),
                event_type="ride.requested",
                ride_id=ride_id,
                customer_id=ride_data["customer_id"],
                pickup_location=ride_data["pickup"],
                drop_location=ride_data["drop"],
                fare=ride_data["fare"]
            )
            
            await producer.publish_ride_event(request_event)
            
            # Wait between events
            await asyncio.sleep(1)
            
            # Ride started event
            started_event = OlaRideEvent(
                event_id=str(uuid.uuid4()),
                event_type="ride.started",
                ride_id=ride_id,
                customer_id=ride_data["customer_id"],
                driver_id=f"DRV{uuid.uuid4().hex[:3].upper()}",
                status="in_progress"
            )
            
            await producer.publish_ride_event(started_event)
            await asyncio.sleep(2)
            
            # Ride completed event
            completed_event = OlaRideEvent(
                event_id=str(uuid.uuid4()),
                event_type="ride.completed",
                ride_id=ride_id,
                customer_id=ride_data["customer_id"],
                driver_id=started_event.driver_id,
                fare=ride_data["fare"],
                status="completed"
            )
            
            await producer.publish_ride_event(completed_event)
            await asyncio.sleep(1)
            
    finally:
        producer.close()

def start_consumer_services():
    """Different consumer services start karna"""
    
    # Driver assignment service
    def start_driver_service():
        driver_service = DriverAssignmentService()
        consumer = OlaKafkaConsumer(
            topic='ola-rides',
            consumer_group='driver-assignment-service'
        )
        
        def driver_handler(event_data):
            if event_data.get('event_type') == 'ride.requested':
                return driver_service.handle_ride_request(event_data)
            return True
            
        consumer.start_consuming(driver_handler)
    
    # Tracking service
    def start_tracking_service():
        tracking_service = RideTrackingService()
        consumer = OlaKafkaConsumer(
            topic='ola-rides',
            consumer_group='ride-tracking-service'
        )
        
        def tracking_handler(event_data):
            if event_data.get('event_type') == 'ride.started':
                return tracking_service.handle_ride_started(event_data)
            return True
            
        consumer.start_consuming(tracking_handler)
    
    # Payment service
    def start_payment_service():
        payment_service = PaymentService()
        consumer = OlaKafkaConsumer(
            topic='ola-rides',
            consumer_group='payment-service'
        )
        
        def payment_handler(event_data):
            if event_data.get('event_type') == 'ride.completed':
                return payment_service.handle_ride_completed(event_data)
            return True
            
        consumer.start_consuming(payment_handler)
    
    # Analytics service
    def start_analytics_service():
        analytics_service = AnalyticsService()
        consumer = OlaKafkaConsumer(
            topic='ola-rides',
            consumer_group='analytics-service'
        )
        
        def analytics_handler(event_data):
            return analytics_service.handle_any_ride_event(event_data)
            
        consumer.start_consuming(analytics_handler)
    
    # Start all services in separate threads
    services = [
        threading.Thread(target=start_driver_service, daemon=True),
        threading.Thread(target=start_tracking_service, daemon=True),
        threading.Thread(target=start_payment_service, daemon=True),
        threading.Thread(target=start_analytics_service, daemon=True)
    ]
    
    for service in services:
        service.start()
    
    return services

async def main():
    """Main demo function"""
    print("🚗 Ola Kafka Event-Driven Ride Sharing Demo")
    print("=" * 50)
    print("📋 Make sure Kafka is running on localhost:9092")
    print("📋 Docker commands:")
    print("   docker run -d --name zookeeper -p 2181:2181 -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-zookeeper")
    print("   docker run -d --name kafka -p 9092:9092 -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 confluentinc/cp-kafka")
    print()
    
    try:
        # Start consumer services
        print("🎧 Starting consumer services...")
        consumer_threads = start_consumer_services()
        
        # Wait for consumers to initialize
        await asyncio.sleep(2)
        
        # Start producing events
        print("🚀 Starting ride simulation...")
        await simulate_ola_rides()
        
        # Let consumers process for a while
        print("⏳ Processing events...")
        await asyncio.sleep(10)
        
        print("✅ Demo completed successfully!")
        
    except KeyboardInterrupt:
        print("🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Demo error details:")

if __name__ == "__main__":
    asyncio.run(main())