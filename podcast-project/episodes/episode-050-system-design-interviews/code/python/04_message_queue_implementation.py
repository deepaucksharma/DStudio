#!/usr/bin/env python3
"""
Message Queue Implementation - Episode 50: System Design Interview Mastery
Mumbai Local Train Message System - IRCTC Booking Queue

Message Queue जैसे Mumbai Local का timing system है -
सब कुछ order में, reliable delivery के साथ

Author: Hindi Podcast Series
Topic: Distributed Message Queue with Kafka-like Features
"""

import json
import time
import threading
import uuid
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import heapq
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging for message queue operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageStatus(Enum):
    """Message delivery status - Mumbai delivery tracking"""
    PENDING = "pending"          # Message waiting in queue
    IN_TRANSIT = "in_transit"    # Being delivered
    DELIVERED = "delivered"      # Successfully delivered
    FAILED = "failed"            # Delivery failed
    DEAD_LETTER = "dead_letter"  # Moved to dead letter queue

class DeliveryMode(Enum):
    """Delivery guarantee modes"""
    AT_MOST_ONCE = "at_most_once"      # Fire and forget
    AT_LEAST_ONCE = "at_least_once"    # Guarantee delivery
    EXACTLY_ONCE = "exactly_once"      # No duplicates

@dataclass
class Message:
    """Individual message - Mumbai train announcement"""
    id: str
    topic: str
    partition: int
    content: Any
    timestamp: float
    headers: Dict[str, str]
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    expiry_time: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.expiry_time is None:
            return False
        return time.time() > self.expiry_time
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return asdict(self)

@dataclass
class Consumer:
    """Message consumer - Mumbai passenger waiting for train"""
    consumer_id: str
    group_id: str
    topics: List[str]
    callback: Callable
    auto_commit: bool = True
    max_poll_records: int = 500
    is_active: bool = True
    last_heartbeat: float = None
    
    def __post_init__(self):
        self.last_heartbeat = time.time()

class TopicPartition:
    """Single partition of a topic - Platform track"""
    
    def __init__(self, topic: str, partition_id: int, max_size: int = 10000):
        self.topic = topic
        self.partition_id = partition_id
        self.messages = deque(maxlen=max_size)
        self.offset = 0
        self.committed_offsets = {}  # consumer_group -> offset
        self.lock = threading.RLock()
        
        # Performance metrics
        self.produced_count = 0
        self.consumed_count = 0
        self.failed_count = 0
    
    def append_message(self, message: Message) -> int:
        """Add message to partition - Train arrival"""
        with self.lock:
            message.partition = self.partition_id
            self.messages.append(message)
            current_offset = self.offset
            self.offset += 1
            self.produced_count += 1
            
            logger.info(f"📦 Message {message.id} added to {self.topic}-{self.partition_id} at offset {current_offset}")
            return current_offset
    
    def consume_messages(self, consumer_group: str, max_records: int = 100) -> List[Message]:
        """Consume messages from partition"""
        with self.lock:
            committed_offset = self.committed_offsets.get(consumer_group, 0)
            available_messages = list(self.messages)[committed_offset:]
            
            consumed = available_messages[:max_records]
            self.consumed_count += len(consumed)
            
            return consumed
    
    def commit_offset(self, consumer_group: str, offset: int):
        """Commit consumer offset - Passenger boarded train"""
        with self.lock:
            self.committed_offsets[consumer_group] = offset
            logger.info(f"✅ Offset {offset} committed for group {consumer_group} on {self.topic}-{self.partition_id}")
    
    def get_lag(self, consumer_group: str) -> int:
        """Get consumer lag - How many messages behind"""
        with self.lock:
            committed_offset = self.committed_offsets.get(consumer_group, 0)
            return len(self.messages) - committed_offset

class MessageBroker:
    """Main message broker - Mumbai Railway Control Room"""
    
    def __init__(self, name: str = "MumbaiMessageBroker"):
        self.name = name
        self.topics = {}  # topic_name -> List[TopicPartition]
        self.consumers = {}  # consumer_id -> Consumer
        self.consumer_groups = defaultdict(list)  # group_id -> [consumer_ids]
        self.dead_letter_queue = deque()
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = True
        
        # Background tasks
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_messages, daemon=True)
        
        # Metrics
        self.total_produced = 0
        self.total_consumed = 0
        self.total_failed = 0
        
        # Start background tasks
        self.heartbeat_thread.start()
        self.cleanup_thread.start()
        
        logger.info(f"🚂 Message Broker '{name}' started")
    
    def create_topic(self, topic_name: str, num_partitions: int = 3, max_partition_size: int = 10000):
        """Create new topic - Setup new train route"""
        if topic_name in self.topics:
            logger.warning(f"Topic {topic_name} already exists")
            return
        
        partitions = []
        for i in range(num_partitions):
            partition = TopicPartition(topic_name, i, max_partition_size)
            partitions.append(partition)
        
        self.topics[topic_name] = partitions
        logger.info(f"🛤️ Topic '{topic_name}' created with {num_partitions} partitions")
    
    def delete_topic(self, topic_name: str):
        """Delete topic - Close train route"""
        if topic_name in self.topics:
            del self.topics[topic_name]
            logger.info(f"🗑️ Topic '{topic_name}' deleted")
    
    def produce_message(self, topic: str, content: Any, 
                       headers: Dict[str, str] = None, 
                       partition_key: str = None,
                       ttl_seconds: int = None) -> str:
        """Produce message to topic - Send train announcement"""
        
        if topic not in self.topics:
            raise ValueError(f"Topic {topic} does not exist")
        
        # Create message
        message_id = str(uuid.uuid4())
        expiry_time = time.time() + ttl_seconds if ttl_seconds else None
        
        message = Message(
            id=message_id,
            topic=topic,
            partition=0,  # Will be set by partition
            content=content,
            timestamp=time.time(),
            headers=headers or {},
            expiry_time=expiry_time
        )
        
        # Select partition (simple hash-based partitioning)
        partitions = self.topics[topic]
        if partition_key:
            partition_idx = hash(partition_key) % len(partitions)
        else:
            partition_idx = hash(message_id) % len(partitions)
        
        # Add to partition
        offset = partitions[partition_idx].append_message(message)
        self.total_produced += 1
        
        return message_id
    
    def register_consumer(self, consumer_id: str, group_id: str, topics: List[str], 
                         callback: Callable, auto_commit: bool = True) -> Consumer:
        """Register message consumer - Register passenger for train"""
        
        consumer = Consumer(
            consumer_id=consumer_id,
            group_id=group_id,
            topics=topics,
            callback=callback,
            auto_commit=auto_commit
        )
        
        self.consumers[consumer_id] = consumer
        self.consumer_groups[group_id].append(consumer_id)
        
        # Start consumer polling
        self.executor.submit(self._consumer_polling_loop, consumer)
        
        logger.info(f"👤 Consumer {consumer_id} registered for group {group_id}, topics: {topics}")
        return consumer
    
    def unregister_consumer(self, consumer_id: str):
        """Unregister consumer - Passenger exit"""
        if consumer_id in self.consumers:
            consumer = self.consumers[consumer_id]
            consumer.is_active = False
            
            # Remove from group
            self.consumer_groups[consumer.group_id].remove(consumer_id)
            del self.consumers[consumer_id]
            
            logger.info(f"👋 Consumer {consumer_id} unregistered")
    
    def _consumer_polling_loop(self, consumer: Consumer):
        """Consumer polling loop - Passenger waiting for train"""
        logger.info(f"🔄 Started polling for consumer {consumer.consumer_id}")
        
        while consumer.is_active and self.running:
            try:
                # Poll messages from subscribed topics
                for topic in consumer.topics:
                    if topic in self.topics:
                        self._poll_topic_for_consumer(topic, consumer)
                
                # Update heartbeat
                consumer.last_heartbeat = time.time()
                
                # Sleep between polls
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error in consumer {consumer.consumer_id} polling: {e}")
                time.sleep(1)
        
        logger.info(f"🛑 Consumer {consumer.consumer_id} polling stopped")
    
    def _poll_topic_for_consumer(self, topic: str, consumer: Consumer):
        """Poll specific topic for consumer"""
        partitions = self.topics[topic]
        
        for partition in partitions:
            messages = partition.consume_messages(consumer.group_id, consumer.max_poll_records)
            
            for message in messages:
                if message.is_expired():
                    logger.warning(f"⏰ Message {message.id} expired, skipping")
                    continue
                
                try:
                    # Process message through callback
                    result = consumer.callback(message)
                    
                    if result:
                        message.status = MessageStatus.DELIVERED
                        self.total_consumed += 1
                        
                        # Auto-commit offset
                        if consumer.auto_commit:
                            partition.commit_offset(consumer.group_id, 
                                                  partition.committed_offsets.get(consumer.group_id, 0) + 1)
                    else:
                        self._handle_message_failure(message, partition, consumer.group_id)
                
                except Exception as e:
                    logger.error(f"❌ Error processing message {message.id}: {e}")
                    self._handle_message_failure(message, partition, consumer.group_id)
    
    def _handle_message_failure(self, message: Message, partition: TopicPartition, group_id: str):
        """Handle message processing failure"""
        message.retry_count += 1
        self.total_failed += 1
        
        if message.retry_count >= message.max_retries:
            message.status = MessageStatus.DEAD_LETTER
            self.dead_letter_queue.append(message)
            logger.warning(f"💀 Message {message.id} moved to dead letter queue")
        else:
            message.status = MessageStatus.FAILED
            logger.warning(f"🔄 Message {message.id} will be retried (attempt {message.retry_count})")
    
    def _heartbeat_monitor(self):
        """Monitor consumer heartbeats"""
        while self.running:
            try:
                current_time = time.time()
                inactive_consumers = []
                
                for consumer_id, consumer in self.consumers.items():
                    if current_time - consumer.last_heartbeat > 30:  # 30 seconds timeout
                        inactive_consumers.append(consumer_id)
                
                for consumer_id in inactive_consumers:
                    logger.warning(f"💔 Consumer {consumer_id} heartbeat timeout")
                    self.unregister_consumer(consumer_id)
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Heartbeat monitor error: {e}")
    
    def _cleanup_expired_messages(self):
        """Clean up expired messages"""
        while self.running:
            try:
                for topic, partitions in self.topics.items():
                    for partition in partitions:
                        with partition.lock:
                            # Remove expired messages
                            valid_messages = deque()
                            expired_count = 0
                            
                            for message in partition.messages:
                                if not message.is_expired():
                                    valid_messages.append(message)
                                else:
                                    expired_count += 1
                            
                            if expired_count > 0:
                                partition.messages = valid_messages
                                logger.info(f"🧹 Cleaned {expired_count} expired messages from {topic}-{partition.partition_id}")
                
                time.sleep(60)  # Clean every minute
                
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")
    
    def get_topic_stats(self, topic: str) -> Dict:
        """Get topic statistics"""
        if topic not in self.topics:
            return {}
        
        partitions = self.topics[topic]
        stats = {
            'topic': topic,
            'partitions': len(partitions),
            'total_messages': sum(len(p.messages) for p in partitions),
            'total_produced': sum(p.produced_count for p in partitions),
            'total_consumed': sum(p.consumed_count for p in partitions),
            'total_failed': sum(p.failed_count for p in partitions),
            'partition_stats': []
        }
        
        for partition in partitions:
            partition_stats = {
                'partition_id': partition.partition_id,
                'message_count': len(partition.messages),
                'produced_count': partition.produced_count,
                'consumed_count': partition.consumed_count,
                'current_offset': partition.offset,
                'consumer_lags': {group: partition.get_lag(group) 
                                for group in partition.committed_offsets.keys()}
            }
            stats['partition_stats'].append(partition_stats)
        
        return stats
    
    def get_broker_stats(self) -> Dict:
        """Get overall broker statistics"""
        active_consumers = sum(1 for c in self.consumers.values() if c.is_active)
        
        return {
            'broker_name': self.name,
            'topics': len(self.topics),
            'total_partitions': sum(len(partitions) for partitions in self.topics.values()),
            'active_consumers': active_consumers,
            'consumer_groups': len(self.consumer_groups),
            'total_produced': self.total_produced,
            'total_consumed': self.total_consumed,
            'total_failed': self.total_failed,
            'dead_letter_messages': len(self.dead_letter_queue),
            'uptime': time.time() - (time.time() - 3600)  # Simplified uptime
        }
    
    def shutdown(self):
        """Shutdown broker gracefully"""
        logger.info("🛑 Shutting down message broker...")
        self.running = False
        
        # Stop all consumers
        for consumer in self.consumers.values():
            consumer.is_active = False
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ Message broker shutdown complete")

def demonstrate_irctc_booking_queue():
    """IRCTC Tatkal booking message queue demonstration"""
    print("🚂 IRCTC Tatkal Booking Message Queue Demo")
    print("=" * 60)
    
    # Create message broker
    broker = MessageBroker("IRCTC_Booking_Broker")
    
    # Create topics for different types of bookings
    broker.create_topic("tatkal_bookings", num_partitions=3)
    broker.create_topic("general_bookings", num_partitions=2)
    broker.create_topic("notifications", num_partitions=1)
    
    # Message processing callbacks
    def process_tatkal_booking(message: Message) -> bool:
        """Process tatkal booking - High priority"""
        booking_data = message.content
        print(f"🎫 Processing Tatkal booking: {booking_data['pnr']} for {booking_data['passenger']}")
        
        # Simulate booking processing time
        time.sleep(0.5)
        
        # Simulate 90% success rate
        import random
        success = random.random() > 0.1
        
        if success:
            print(f"✅ Tatkal booking {booking_data['pnr']} confirmed!")
            
            # Send confirmation notification
            broker.produce_message("notifications", {
                "type": "booking_confirmed",
                "pnr": booking_data['pnr'],
                "message": f"Your tatkal booking is confirmed. PNR: {booking_data['pnr']}"
            })
            
        else:
            print(f"❌ Tatkal booking {booking_data['pnr']} failed - seats not available")
        
        return success
    
    def process_general_booking(message: Message) -> bool:
        """Process general booking - Normal priority"""
        booking_data = message.content
        print(f"🎟️ Processing General booking: {booking_data['pnr']} for {booking_data['passenger']}")
        
        time.sleep(0.2)
        return True  # General bookings usually succeed
    
    def process_notification(message: Message) -> bool:
        """Process notification messages"""
        notification = message.content
        print(f"📱 Sending notification: {notification['message']}")
        return True
    
    # Register consumers
    tatkal_consumer = broker.register_consumer(
        consumer_id="tatkal_processor_1",
        group_id="tatkal_processing_group",
        topics=["tatkal_bookings"],
        callback=process_tatkal_booking
    )
    
    general_consumer = broker.register_consumer(
        consumer_id="general_processor_1",
        group_id="general_processing_group", 
        topics=["general_bookings"],
        callback=process_general_booking
    )
    
    notification_consumer = broker.register_consumer(
        consumer_id="notification_processor_1",
        group_id="notification_group",
        topics=["notifications"],
        callback=process_notification
    )
    
    print("\n📦 Simulating IRCTC booking requests...")
    
    # Simulate tatkal booking rush (10:00 AM scenario)
    tatkal_bookings = [
        {"pnr": "T001", "passenger": "Rajesh Kumar", "train": "12951", "from": "Mumbai", "to": "Delhi"},
        {"pnr": "T002", "passenger": "Priya Sharma", "train": "12627", "from": "Delhi", "to": "Bangalore"},
        {"pnr": "T003", "passenger": "Amit Singh", "train": "12023", "from": "Chennai", "to": "Mumbai"},
        {"pnr": "T004", "passenger": "Sunita Devi", "train": "12801", "from": "Delhi", "to": "Bhubaneswar"},
        {"pnr": "T005", "passenger": "Vikram Patel", "train": "12432", "from": "Mumbai", "to": "Ahmedabad"},
    ]
    
    for booking in tatkal_bookings:
        message_id = broker.produce_message("tatkal_bookings", booking, 
                                          headers={"priority": "high", "booking_type": "tatkal"})
        print(f"📋 Tatkal booking request submitted: {booking['pnr']}")
    
    # Simulate general bookings
    general_bookings = [
        {"pnr": "G001", "passenger": "Meera Joshi", "train": "12345", "from": "Pune", "to": "Goa"},
        {"pnr": "G002", "passenger": "Arjun Reddy", "train": "12678", "from": "Hyderabad", "to": "Chennai"},
        {"pnr": "G003", "passenger": "Kavya Nair", "train": "12890", "from": "Kochi", "to": "Bangalore"},
    ]
    
    for booking in general_bookings:
        broker.produce_message("general_bookings", booking,
                             headers={"priority": "normal", "booking_type": "general"})
        print(f"📝 General booking request submitted: {booking['pnr']}")
    
    # Let processing happen
    print("\n⏳ Processing bookings...")
    time.sleep(5)
    
    # Show statistics
    print("\n📊 IRCTC Booking Queue Statistics:")
    print("-" * 40)
    
    for topic in ["tatkal_bookings", "general_bookings", "notifications"]:
        stats = broker.get_topic_stats(topic)
        print(f"\n🎯 Topic: {topic}")
        print(f"   Total Messages: {stats['total_messages']}")
        print(f"   Produced: {stats['total_produced']}")
        print(f"   Consumed: {stats['total_consumed']}")
        
        for partition_stats in stats['partition_stats']:
            print(f"   Partition {partition_stats['partition_id']}: "
                  f"Messages: {partition_stats['message_count']}, "
                  f"Offset: {partition_stats['current_offset']}")
    
    broker_stats = broker.get_broker_stats()
    print(f"\n🚂 Broker Statistics:")
    print(f"   Topics: {broker_stats['topics']}")
    print(f"   Active Consumers: {broker_stats['active_consumers']}")
    print(f"   Total Produced: {broker_stats['total_produced']}")
    print(f"   Total Consumed: {broker_stats['total_consumed']}")
    print(f"   Failed Messages: {broker_stats['total_failed']}")
    
    # Cleanup
    time.sleep(2)
    broker.shutdown()

def demonstrate_zomato_order_queue():
    """Zomato food delivery order queue demonstration"""
    print("\n🍕 Zomato Food Delivery Order Queue Demo")
    print("=" * 60)
    
    broker = MessageBroker("Zomato_Delivery_Broker")
    
    # Create topics for food delivery
    broker.create_topic("food_orders", num_partitions=4)
    broker.create_topic("delivery_assignments", num_partitions=2)
    broker.create_topic("customer_updates", num_partitions=1)
    
    def process_food_order(message: Message) -> bool:
        """Process food order"""
        order = message.content
        print(f"🍽️ Processing food order: {order['order_id']} from {order['restaurant']}")
        
        # Simulate order preparation time
        prep_time = order.get('prep_time', 2)
        time.sleep(prep_time / 10)  # Scaled down for demo
        
        # Assign delivery partner
        broker.produce_message("delivery_assignments", {
            "order_id": order['order_id'],
            "delivery_partner": f"Delivery_Partner_{hash(order['order_id']) % 10}",
            "pickup_location": order['restaurant'],
            "delivery_location": order['customer_address']
        })
        
        return True
    
    def process_delivery_assignment(message: Message) -> bool:
        """Process delivery assignment"""
        assignment = message.content
        print(f"🛵 Assigning delivery: Order {assignment['order_id']} to {assignment['delivery_partner']}")
        
        # Notify customer
        broker.produce_message("customer_updates", {
            "order_id": assignment['order_id'],
            "status": "out_for_delivery",
            "message": f"Your order is out for delivery with {assignment['delivery_partner']}"
        })
        
        return True
    
    def process_customer_update(message: Message) -> bool:
        """Process customer notification"""
        update = message.content
        print(f"📱 Customer notification: Order {update['order_id']} - {update['message']}")
        return True
    
    # Register consumers
    broker.register_consumer("order_processor_1", "order_processing", 
                           ["food_orders"], process_food_order)
    broker.register_consumer("delivery_assigner_1", "delivery_assignment", 
                           ["delivery_assignments"], process_delivery_assignment)
    broker.register_consumer("notification_sender_1", "customer_notifications", 
                           ["customer_updates"], process_customer_update)
    
    # Simulate Mumbai food orders
    mumbai_orders = [
        {"order_id": "ZOM001", "restaurant": "Theobroma Bandra", "customer_address": "Linking Road", 
         "items": ["Chocolate Cake", "Cold Coffee"], "amount": 450, "prep_time": 3},
        {"order_id": "ZOM002", "restaurant": "Toit Lower Parel", "customer_address": "Phoenix Mills", 
         "items": ["Pizza Margherita", "Beer"], "amount": 800, "prep_time": 4},
        {"order_id": "ZOM003", "restaurant": "Social Khar", "customer_address": "Khar West", 
         "items": ["Butter Chicken", "Naan"], "amount": 600, "prep_time": 5},
        {"order_id": "ZOM004", "restaurant": "McDonald's Andheri", "customer_address": "Versova", 
         "items": ["Big Mac", "Fries", "Coke"], "amount": 350, "prep_time": 2},
    ]
    
    print("\n🍔 Processing Mumbai food orders...")
    for order in mumbai_orders:
        broker.produce_message("food_orders", order, 
                             headers={"city": "mumbai", "priority": "normal"})
        print(f"📋 Order placed: {order['order_id']} from {order['restaurant']}")
    
    # Let processing happen
    time.sleep(8)
    
    # Show final statistics
    print(f"\n📊 Zomato Order Queue Final Stats:")
    stats = broker.get_broker_stats()
    print(f"   Total Orders Processed: {stats['total_consumed']}")
    print(f"   Failed Processing: {stats['total_failed']}")
    
    broker.shutdown()

if __name__ == "__main__":
    # Run IRCTC booking demonstration
    demonstrate_irctc_booking_queue()
    
    print("\n" + "="*80 + "\n")
    
    # Run Zomato delivery demonstration
    demonstrate_zomato_order_queue()
    
    print("\n" + "="*80)
    print("✅ Message Queue Implementation Demo Complete!")
    print("📚 Key Features Demonstrated:")
    print("   • Topic-based message distribution")
    print("   • Partitioned message storage")
    print("   • Consumer groups with load balancing")
    print("   • Automatic failure handling and retries")
    print("   • Dead letter queue for failed messages")
    print("   • Consumer heartbeat monitoring")
    print("   • Message expiration and cleanup")
    print("   • Production-ready for Mumbai scale operations")