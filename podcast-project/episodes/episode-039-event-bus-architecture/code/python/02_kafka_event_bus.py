#!/usr/bin/env python3
"""
Kafka-based Event Bus Implementation
===================================

Production-ready Kafka-based event bus for high-throughput event processing.
Apache Kafka provides reliable, scalable message streaming for event-driven systems.

Mumbai Context: यह Mumbai local train network जैसा है! Multiple parallel tracks
(topics) हैं, high-frequency trains (messages) चलती हैं, और multiple stations
(consumers) efficiently handle करते हैं. Peak hours में भी smoothly चलता है!

Real-world usage:
- High-volume event streaming
- Real-time data pipelines
- Microservices communication
- Log aggregation
- Activity tracking
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError
import avro.schema
import avro.io
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KafkaEvent:
    """Kafka event message structure"""
    event_id: str
    event_type: str
    source_service: str
    data: Dict[str, Any]
    timestamp: float
    correlation_id: str = ""
    partition_key: Optional[str] = None  # For message ordering
    headers: Optional[Dict[str, str]] = None
    schema_version: int = 1

class KafkaEventBus:
    """
    Kafka-based Event Bus Implementation
    
    Mumbai Metaphor: यह Mumbai's suburban railway network जैसा है!
    - Multiple tracks (topics) for different lines
    - High frequency trains (high throughput messages)  
    - Efficient stations (consumer groups) handling passengers
    - Peak hour management (partition scaling)
    - Reliable service even during monsoons (fault tolerance)
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092', 
                 client_id: str = 'eventbus-client'):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        
        # Kafka clients
        self.producer = None
        self.admin_client = None
        self.consumers: Dict[str, KafkaConsumer] = {}
        self.consumer_threads: Dict[str, threading.Thread] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Configuration
        self.default_num_partitions = 3
        self.default_replication_factor = 1
        
        # Statistics
        self.stats = {
            'events_published': 0,
            'events_consumed': 0,
            'events_failed': 0,
            'active_consumers': 0,
            'topics_created': 0
        }
        
        # Running state
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        logger.info(f"🚊 Kafka Event Bus initialized (servers: {bootstrap_servers})")
    
    def start(self):
        """Start the Kafka event bus"""
        try:
            # Initialize Kafka producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-producer",
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas
                retries=3,
                batch_size=16384,
                linger_ms=10,  # Small delay for batching
                compression_type='snappy'
            )
            
            # Initialize admin client
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-admin"
            )
            
            self.running = True
            logger.info("✅ Kafka Event Bus started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Kafka Event Bus: {e}")
            raise
    
    def stop(self):
        """Stop the Kafka event bus"""
        self.running = False
        
        # Stop all consumers
        for consumer_id, thread in self.consumer_threads.items():
            logger.info(f"🛑 Stopping consumer: {consumer_id}")
            thread.join(timeout=5)
        
        # Close producer
        if self.producer:
            self.producer.close()
        
        # Close admin client
        if self.admin_client:
            self.admin_client.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("🛑 Kafka Event Bus stopped")
    
    def create_topic(self, topic_name: str, num_partitions: Optional[int] = None,
                     replication_factor: Optional[int] = None) -> bool:
        """Create a Kafka topic"""
        try:
            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions or self.default_num_partitions,
                replication_factor=replication_factor or self.default_replication_factor
            )
            
            result = self.admin_client.create_topics([topic])
            
            # Wait for topic creation
            for topic_name, future in result.items():
                try:
                    future.result(timeout=30)
                    self.stats['topics_created'] += 1
                    logger.info(f"📋 Topic created: {topic_name}")
                    return True
                except TopicAlreadyExistsError:
                    logger.info(f"📋 Topic already exists: {topic_name}")
                    return True
                except Exception as e:
                    logger.error(f"❌ Failed to create topic {topic_name}: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating topic {topic_name}: {e}")
            return False
    
    def publish(self, topic: str, event: KafkaEvent) -> bool:
        """
        Publish an event to Kafka topic
        
        Args:
            topic: Kafka topic name
            event: Event to publish
            
        Returns:
            True if published successfully
        """
        if not self.producer or not self.running:
            logger.error("❌ Event bus not started")
            return False
        
        try:
            # Prepare message
            message_value = {
                'event_id': event.event_id,
                'event_type': event.event_type,
                'source_service': event.source_service,
                'data': event.data,
                'timestamp': event.timestamp,
                'correlation_id': event.correlation_id,
                'schema_version': event.schema_version
            }
            
            # Prepare headers
            headers = event.headers or {}
            headers['event_type'] = event.event_type
            headers['source_service'] = event.source_service
            headers['correlation_id'] = event.correlation_id
            
            kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]
            
            # Send message
            future = self.producer.send(
                topic,
                value=message_value,
                key=event.partition_key,
                headers=kafka_headers
            )
            
            # Wait for send completion
            record_metadata = future.get(timeout=10)
            
            self.stats['events_published'] += 1
            
            logger.info(f"📤 Event published: {event.event_type} to {topic} " +
                       f"(partition: {record_metadata.partition}, offset: {record_metadata.offset})")
            
            return True
            
        except Exception as e:
            self.stats['events_failed'] += 1
            logger.error(f"❌ Failed to publish event to {topic}: {e}")
            return False
    
    def subscribe(self, topic: str, consumer_group: str, handler: Callable[[KafkaEvent], bool],
                  auto_offset_reset: str = 'latest') -> str:
        """
        Subscribe to events from a Kafka topic
        
        Args:
            topic: Kafka topic name
            consumer_group: Consumer group ID
            handler: Event handler function
            auto_offset_reset: Offset reset policy
            
        Returns:
            Consumer ID
        """
        consumer_id = f"{consumer_group}_{topic}_{int(time.time())}"
        
        # Ensure topic exists
        self.create_topic(topic)
        
        # Store handler
        if topic not in self.event_handlers:
            self.event_handlers[topic] = []
        self.event_handlers[topic].append(handler)
        
        # Create and start consumer
        def consume_messages():
            try:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=consumer_group,
                    client_id=f"{self.client_id}-{consumer_id}",
                    auto_offset_reset=auto_offset_reset,
                    enable_auto_commit=True,
                    auto_commit_interval_ms=1000,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    key_deserializer=lambda k: k.decode('utf-8') if k else None,
                    max_poll_records=10,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=3000
                )
                
                self.consumers[consumer_id] = consumer
                self.stats['active_consumers'] += 1
                
                logger.info(f"🎧 Consumer started: {consumer_id} for topic {topic}")
                
                # Message consumption loop
                while self.running:
                    try:
                        message_batch = consumer.poll(timeout_ms=1000)
                        
                        for topic_partition, messages in message_batch.items():
                            for message in messages:
                                self._process_message(message, handler, consumer_id)
                                
                    except Exception as e:
                        logger.error(f"❌ Error in consumer {consumer_id}: {e}")
                        time.sleep(1)  # Brief pause before retry
                
            except Exception as e:
                logger.error(f"❌ Failed to create consumer {consumer_id}: {e}")
            finally:
                # Cleanup
                if consumer_id in self.consumers:
                    self.consumers[consumer_id].close()
                    del self.consumers[consumer_id]
                    self.stats['active_consumers'] -= 1
                
                logger.info(f"🔌 Consumer stopped: {consumer_id}")
        
        # Start consumer thread
        consumer_thread = threading.Thread(target=consume_messages, daemon=True)
        consumer_thread.start()
        self.consumer_threads[consumer_id] = consumer_thread
        
        logger.info(f"📝 Subscription created: {consumer_id}")
        return consumer_id
    
    def _process_message(self, message, handler: Callable, consumer_id: str):
        """Process a single Kafka message"""
        try:
            # Parse message
            message_data = message.value
            
            # Extract headers
            headers = {}
            if message.headers:
                for key, value in message.headers:
                    headers[key] = value.decode('utf-8')
            
            # Create event object
            event = KafkaEvent(
                event_id=message_data['event_id'],
                event_type=message_data['event_type'],
                source_service=message_data['source_service'],
                data=message_data['data'],
                timestamp=message_data['timestamp'],
                correlation_id=message_data.get('correlation_id', ''),
                partition_key=message.key,
                headers=headers,
                schema_version=message_data.get('schema_version', 1)
            )
            
            # Submit to thread pool for processing
            future = self.executor.submit(handler, event)
            
            # Get result with timeout
            success = future.result(timeout=30)
            
            if success:
                self.stats['events_consumed'] += 1
                logger.debug(f"✅ Event processed: {event.event_id} by {consumer_id}")
            else:
                self.stats['events_failed'] += 1
                logger.warning(f"⚠️ Event processing failed: {event.event_id} by {consumer_id}")
                
        except Exception as e:
            self.stats['events_failed'] += 1
            logger.error(f"❌ Error processing message in {consumer_id}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            **self.stats,
            'running': self.running,
            'active_topics': len(self.event_handlers)
        }

# Specialized Mumbai services using Kafka Event Bus

class SwiggyOrderEventProducer:
    """
    Swiggy order event producer
    
    Mumbai Story: यह Swiggy का central event publisher है! जब भी कोई order
    activity होती है, तो सभी interested services को events भेजता है.
    """
    
    def __init__(self, kafka_bus: KafkaEventBus):
        self.kafka_bus = kafka_bus
        self.order_topic = "swiggy.orders"
        self.payment_topic = "swiggy.payments"
        self.delivery_topic = "swiggy.deliveries"
        
        # Create topics
        for topic in [self.order_topic, self.payment_topic, self.delivery_topic]:
            self.kafka_bus.create_topic(topic, num_partitions=5)  # More partitions for scaling
        
        logger.info("🏪 Swiggy Order Event Producer initialized")
    
    def publish_order_created(self, order_data: Dict[str, Any]):
        """Publish order created event"""
        event = KafkaEvent(
            event_id=f"order_created_{order_data['order_id']}_{int(time.time() * 1000)}",
            event_type="ORDER_CREATED",
            source_service="SwiggyOrderService",
            data=order_data,
            timestamp=time.time(),
            correlation_id=order_data['order_id'],
            partition_key=order_data['customer_id']  # Partition by customer for ordering
        )
        
        return self.kafka_bus.publish(self.order_topic, event)
    
    def publish_payment_initiated(self, payment_data: Dict[str, Any]):
        """Publish payment initiated event"""
        event = KafkaEvent(
            event_id=f"payment_initiated_{payment_data['payment_id']}_{int(time.time() * 1000)}",
            event_type="PAYMENT_INITIATED",
            source_service="SwiggyPaymentService",
            data=payment_data,
            timestamp=time.time(),
            correlation_id=payment_data['order_id'],
            partition_key=payment_data['customer_id']
        )
        
        return self.kafka_bus.publish(self.payment_topic, event)
    
    def publish_delivery_assigned(self, delivery_data: Dict[str, Any]):
        """Publish delivery assigned event"""
        event = KafkaEvent(
            event_id=f"delivery_assigned_{delivery_data['delivery_id']}_{int(time.time() * 1000)}",
            event_type="DELIVERY_ASSIGNED", 
            source_service="SwiggyDeliveryService",
            data=delivery_data,
            timestamp=time.time(),
            correlation_id=delivery_data['order_id'],
            partition_key=delivery_data['delivery_partner_id']  # Partition by delivery partner
        )
        
        return self.kafka_bus.publish(self.delivery_topic, event)

class SwiggyInventoryService:
    """
    Swiggy inventory service (event consumer)
    
    Mumbai Story: यह restaurant का inventory management system है!
    Order events सुनकर items को reserve/update करता है.
    """
    
    def __init__(self, kafka_bus: KafkaEventBus):
        self.kafka_bus = kafka_bus
        self.inventory = {
            'butter_chicken': 50,
            'biryani': 30,
            'pizza': 25,
            'burger': 40,
            'noodles': 35,
            'dal_rice': 60
        }
        
        self.reservations: Dict[str, List[str]] = {}
        
        # Subscribe to order events
        self.consumer_id = self.kafka_bus.subscribe(
            topic="swiggy.orders",
            consumer_group="inventory-service",
            handler=self.handle_order_event
        )
        
        logger.info("📦 Swiggy Inventory Service initialized")
    
    def handle_order_event(self, event: KafkaEvent) -> bool:
        """Handle order events"""
        try:
            if event.event_type == "ORDER_CREATED":
                return self._process_order_created(event)
            
            # Handle other order events as needed
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in inventory service: {e}")
            return False
    
    def _process_order_created(self, event: KafkaEvent) -> bool:
        """Process order created event"""
        try:
            order_data = event.data
            order_id = order_data['order_id']
            items = order_data.get('items', [])
            
            reserved_items = []
            
            # Check and reserve items
            for item in items:
                item_name = item.get('name', '').lower().replace(' ', '_')
                quantity = item.get('quantity', 1)
                
                if item_name in self.inventory:
                    if self.inventory[item_name] >= quantity:
                        # Reserve item
                        self.inventory[item_name] -= quantity
                        reserved_items.append(f"{item_name} x{quantity}")
                        
                        logger.info(f"📦 Reserved: {item_name} x{quantity} for order {order_id}")
                    else:
                        logger.warning(f"⚠️ Insufficient inventory: {item_name} (need: {quantity}, have: {self.inventory[item_name]})")
                        # In real system, this would trigger stock replenishment
            
            # Store reservation
            if reserved_items:
                self.reservations[order_id] = reserved_items
                logger.info(f"✅ Inventory reserved for order {order_id}: {reserved_items}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing order created event: {e}")
            return False
    
    def get_inventory_status(self) -> Dict[str, Any]:
        """Get current inventory status"""
        return {
            'inventory': self.inventory.copy(),
            'reservations': len(self.reservations),
            'total_items': sum(self.inventory.values())
        }

class SwiggyNotificationService:
    """
    Swiggy notification service (event consumer)
    
    Mumbai Story: यह notification system है! सभी order updates के लिए
    customers को real-time notifications भेजता है.
    """
    
    def __init__(self, kafka_bus: KafkaEventBus):
        self.kafka_bus = kafka_bus
        self.sent_notifications = []
        
        # Subscribe to multiple topics
        topics = ["swiggy.orders", "swiggy.payments", "swiggy.deliveries"]
        self.consumer_ids = []
        
        for topic in topics:
            consumer_id = self.kafka_bus.subscribe(
                topic=topic,
                consumer_group="notification-service",
                handler=self.handle_event
            )
            self.consumer_ids.append(consumer_id)
        
        logger.info("📱 Swiggy Notification Service initialized")
    
    def handle_event(self, event: KafkaEvent) -> bool:
        """Handle all types of events"""
        try:
            notification_message = self._generate_notification(event)
            
            if notification_message:
                notification = {
                    'event_id': event.event_id,
                    'event_type': event.event_type,
                    'customer_id': self._extract_customer_id(event),
                    'message': notification_message,
                    'sent_at': time.time(),
                    'channel': 'app_push'  # Could be SMS, email, etc.
                }
                
                self.sent_notifications.append(notification)
                
                logger.info(f"📱 Notification sent: {event.event_type} to {notification['customer_id']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in notification service: {e}")
            return False
    
    def _generate_notification(self, event: KafkaEvent) -> Optional[str]:
        """Generate notification message based on event"""
        event_type = event.event_type
        data = event.data
        
        if event_type == "ORDER_CREATED":
            restaurant_name = data.get('restaurant_name', 'Restaurant')
            total_amount = data.get('total_amount', 0)
            return f"🍽️ आपका order confirm हो गया! {restaurant_name} से ₹{total_amount:.2f} का order."
        
        elif event_type == "PAYMENT_INITIATED":
            amount = data.get('amount', 0)
            return f"💰 Payment processing... Amount: ₹{amount:.2f}"
        
        elif event_type == "DELIVERY_ASSIGNED":
            partner_name = data.get('delivery_partner_name', 'Delivery Partner')
            eta = data.get('estimated_time', 30)
            return f"🛵 {partner_name} आपका order deliver करने आ रहे हैं! ETA: {eta} minutes"
        
        return None
    
    def _extract_customer_id(self, event: KafkaEvent) -> str:
        """Extract customer ID from event data"""
        return event.data.get('customer_id', 'unknown')
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        if not self.sent_notifications:
            return {'total_sent': 0, 'by_type': {}}
        
        by_type = {}
        for notif in self.sent_notifications:
            event_type = notif['event_type']
            by_type[event_type] = by_type.get(event_type, 0) + 1
        
        return {
            'total_sent': len(self.sent_notifications),
            'by_type': by_type,
            'recent_notifications': self.sent_notifications[-5:]  # Last 5
        }

def simulate_swiggy_kafka_events():
    """
    Simulate Swiggy order processing using Kafka event bus
    
    Mumbai Scenario: Peak lunch time में Swiggy के through बहुत सारे orders
    आते हैं. Kafka-based event bus high-volume events को efficiently handle
    करता है और सभी services को real-time updates देता है!
    """
    logger.info("🏪 Starting Swiggy Kafka Event Bus simulation...")
    
    # Initialize Kafka event bus
    kafka_bus = KafkaEventBus(bootstrap_servers='localhost:9092')
    
    try:
        kafka_bus.start()
    except Exception as e:
        logger.error(f"❌ Failed to connect to Kafka. Please ensure Kafka is running on localhost:9092")
        logger.error("Start Kafka with: bin/kafka-server-start.sh config/server.properties")
        return
    
    # Initialize services
    order_producer = SwiggyOrderEventProducer(kafka_bus)
    inventory_service = SwiggyInventoryService(kafka_bus)
    notification_service = SwiggyNotificationService(kafka_bus)
    
    logger.info("🎭 All Swiggy services initialized")
    
    # Wait for consumers to be ready
    time.sleep(2)
    
    # Sample orders for simulation
    sample_orders = [
        {
            'order_id': 'SWG_001',
            'customer_id': 'cust_mumbai_001',
            'restaurant_id': 'rest_mumbai_darbar',
            'restaurant_name': 'Mumbai Darbar',
            'items': [
                {'name': 'Butter Chicken', 'quantity': 1, 'price': 350.0},
                {'name': 'Biryani', 'quantity': 1, 'price': 400.0}
            ],
            'total_amount': 750.0,
            'delivery_address': 'Bandra West, Mumbai'
        },
        {
            'order_id': 'SWG_002',
            'customer_id': 'cust_mumbai_002',
            'restaurant_id': 'rest_pizza_corner',
            'restaurant_name': 'Pizza Corner',
            'items': [
                {'name': 'Pizza', 'quantity': 2, 'price': 450.0}
            ],
            'total_amount': 900.0,
            'delivery_address': 'Andheri East, Mumbai'
        },
        {
            'order_id': 'SWG_003',
            'customer_id': 'cust_mumbai_003',
            'restaurant_id': 'rest_burger_house',
            'restaurant_name': 'Burger House',
            'items': [
                {'name': 'Burger', 'quantity': 3, 'price': 200.0},
                {'name': 'Noodles', 'quantity': 1, 'price': 250.0}
            ],
            'total_amount': 850.0,
            'delivery_address': 'Powai, Mumbai'
        }
    ]
    
    # Publish order events
    for order in sample_orders:
        # 1. Publish order created event
        success = order_producer.publish_order_created(order)
        if success:
            logger.info(f"✅ Order published: {order['order_id']}")
        
        # 2. Simulate payment initiation
        time.sleep(0.1)
        payment_data = {
            'payment_id': f"PAY_{order['order_id']}",
            'order_id': order['order_id'],
            'customer_id': order['customer_id'],
            'amount': order['total_amount'],
            'payment_method': 'UPI'
        }
        
        order_producer.publish_payment_initiated(payment_data)
        
        # 3. Simulate delivery assignment
        time.sleep(0.1)
        delivery_data = {
            'delivery_id': f"DEL_{order['order_id']}",
            'order_id': order['order_id'],
            'customer_id': order['customer_id'],
            'delivery_partner_id': f"partner_{(hash(order['order_id']) % 100):03d}",
            'delivery_partner_name': f"राहुल {(hash(order['order_id']) % 100):03d}",
            'estimated_time': 25 + (hash(order['order_id']) % 20)  # 25-45 minutes
        }
        
        order_producer.publish_delivery_assigned(delivery_data)
        
        time.sleep(0.5)  # Small delay between orders
    
    # Wait for all events to be processed
    logger.info("⏳ Waiting for all events to be processed...")
    time.sleep(5)
    
    # Show results
    kafka_stats = kafka_bus.get_statistics()
    inventory_status = inventory_service.get_inventory_status()
    notification_stats = notification_service.get_notification_stats()
    
    logger.info("\n📊 Kafka Event Bus Statistics:")
    logger.info(f"Events published: {kafka_stats['events_published']}")
    logger.info(f"Events consumed: {kafka_stats['events_consumed']}")
    logger.info(f"Events failed: {kafka_stats['events_failed']}")
    logger.info(f"Active consumers: {kafka_stats['active_consumers']}")
    logger.info(f"Topics created: {kafka_stats['topics_created']}")
    
    logger.info(f"\n📦 Inventory Service Status:")
    logger.info(f"Total items available: {inventory_status['total_items']}")
    logger.info(f"Orders with reservations: {inventory_status['reservations']}")
    logger.info("Current inventory:")
    for item, quantity in inventory_status['inventory'].items():
        logger.info(f"  {item}: {quantity} units")
    
    logger.info(f"\n📱 Notification Service Statistics:")
    logger.info(f"Total notifications sent: {notification_stats['total_sent']}")
    logger.info("Notifications by type:")
    for event_type, count in notification_stats.get('by_type', {}).items():
        logger.info(f"  {event_type}: {count}")
    
    if 'recent_notifications' in notification_stats:
        logger.info("Recent notifications:")
        for notif in notification_stats['recent_notifications']:
            logger.info(f"  {notif['customer_id']}: {notif['message']}")
    
    # Cleanup
    kafka_bus.stop()

if __name__ == "__main__":
    try:
        simulate_swiggy_kafka_events()
        logger.info("\n🎊 Swiggy Kafka Event Bus simulation completed!")
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        import traceback
        traceback.print_exc()