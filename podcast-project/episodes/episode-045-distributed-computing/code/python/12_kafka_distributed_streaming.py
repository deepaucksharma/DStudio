#!/usr/bin/env python3
"""
Kafka Distributed Streaming System for Real-time Data Processing
Episode 45: Distributed Computing at Scale

यह example Kafka-like distributed streaming system दिखाता है
Real-time event processing, partitioning, और replication के साथ
high-throughput data streaming for Indian scale applications।

Production Stats:
- Swiggy: 100M+ events per day (order tracking, delivery updates)
- Throughput: 1M+ messages per second during peak hours
- Latency: <10ms for event processing
- Partitions: 1000+ for load distribution
- Replication factor: 3 for fault tolerance
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import bisect
import heapq

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageStatus(Enum):
    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FAILED = "FAILED"

class ConsumerState(Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    REBALANCING = "REBALANCING"

@dataclass
class StreamMessage:
    """Message in the streaming system"""
    key: Optional[str]
    value: Any
    headers: Dict[str, str]
    timestamp: datetime
    partition: int
    offset: int
    topic: str
    producer_id: str
    message_id: str = None
    status: MessageStatus = MessageStatus.PENDING
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class TopicPartition:
    """Topic partition information"""
    topic: str
    partition: int
    
    def __str__(self):
        return f"{self.topic}-{self.partition}"

@dataclass
class ConsumerOffset:
    """Consumer offset tracking"""
    topic: str
    partition: int
    offset: int
    consumer_group: str
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class Partition:
    """Individual partition for storing messages"""
    
    def __init__(self, topic: str, partition_id: int, max_size: int = 10000):
        self.topic = topic
        self.partition_id = partition_id
        self.max_size = max_size
        
        # Message storage
        self.messages = []  # List of StreamMessage
        self.offset_counter = 0
        
        # Performance tracking
        self.bytes_in = 0
        self.bytes_out = 0
        self.message_count = 0
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.debug(f"📂 Created partition {topic}-{partition_id}")
    
    def append_message(self, message: StreamMessage) -> int:
        """Append message to partition and return offset"""
        with self.lock:
            # Assign offset and partition
            message.offset = self.offset_counter
            message.partition = self.partition_id
            message.topic = self.topic
            
            # Add to storage
            self.messages.append(message)
            self.offset_counter += 1
            self.message_count += 1
            
            # Track bytes
            message_bytes = len(json.dumps(asdict(message), default=str).encode('utf-8'))
            self.bytes_in += message_bytes
            
            # Trim old messages if partition is full
            if len(self.messages) > self.max_size:
                removed_message = self.messages.pop(0)
                removed_bytes = len(json.dumps(asdict(removed_message), default=str).encode('utf-8'))
                self.bytes_out += removed_bytes
            
            return message.offset
    
    def get_messages(self, start_offset: int, max_messages: int = 100) -> List[StreamMessage]:
        """Get messages starting from offset"""
        with self.lock:
            if not self.messages:
                return []
            
            # Find starting position
            start_pos = 0
            for i, msg in enumerate(self.messages):
                if msg.offset >= start_offset:
                    start_pos = i
                    break
            else:
                # All messages have offset < start_offset
                return []
            
            # Return messages
            end_pos = min(start_pos + max_messages, len(self.messages))
            return self.messages[start_pos:end_pos].copy()
    
    def get_latest_offset(self) -> int:
        """Get the latest offset in partition"""
        with self.lock:
            return self.offset_counter
    
    def get_partition_stats(self) -> Dict[str, Any]:
        """Get partition statistics"""
        with self.lock:
            return {
                "topic": self.topic,
                "partition": self.partition_id,
                "message_count": self.message_count,
                "current_messages": len(self.messages),
                "latest_offset": self.offset_counter,
                "bytes_in": self.bytes_in,
                "bytes_out": self.bytes_out,
                "size_mb": self.bytes_in / (1024 * 1024)
            }

class Topic:
    """Topic with multiple partitions"""
    
    def __init__(self, name: str, num_partitions: int = 8, replication_factor: int = 3):
        self.name = name
        self.num_partitions = num_partitions
        self.replication_factor = replication_factor
        
        # Create partitions
        self.partitions = {}  # partition_id -> Partition
        for i in range(num_partitions):
            self.partitions[i] = Partition(name, i)
        
        # Partition assignment for round-robin
        self.next_partition = 0
        
        logger.info(f"📋 Created topic '{name}' with {num_partitions} partitions")
    
    def get_partition_for_key(self, key: Optional[str]) -> int:
        """Get partition for message key using consistent hashing"""
        if key is None:
            # Round-robin for null keys
            partition = self.next_partition
            self.next_partition = (self.next_partition + 1) % self.num_partitions
            return partition
        
        # Hash-based partitioning for keys
        hash_value = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
        return hash_value % self.num_partitions
    
    def produce_message(self, message: StreamMessage) -> int:
        """Produce message to appropriate partition"""
        partition_id = self.get_partition_for_key(message.key)
        partition = self.partitions[partition_id]
        return partition.append_message(message)
    
    def consume_messages(self, partition_id: int, start_offset: int, max_messages: int = 100) -> List[StreamMessage]:
        """Consume messages from specific partition"""
        if partition_id not in self.partitions:
            return []
        
        partition = self.partitions[partition_id]
        return partition.get_messages(start_offset, max_messages)
    
    def get_topic_stats(self) -> Dict[str, Any]:
        """Get comprehensive topic statistics"""
        total_messages = sum(p.message_count for p in self.partitions.values())
        total_bytes = sum(p.bytes_in for p in self.partitions.values())
        
        partition_stats = {
            str(pid): partition.get_partition_stats() 
            for pid, partition in self.partitions.items()
        }
        
        return {
            "topic_name": self.name,
            "num_partitions": self.num_partitions,
            "replication_factor": self.replication_factor,
            "total_messages": total_messages,
            "total_bytes": total_bytes,
            "size_mb": total_bytes / (1024 * 1024),
            "partitions": partition_stats
        }

class StreamingProducer:
    """Producer for streaming messages"""
    
    def __init__(self, producer_id: str, cluster: 'DistributedStreamingCluster'):
        self.producer_id = producer_id
        self.cluster = cluster
        
        # Performance metrics
        self.messages_sent = 0
        self.bytes_sent = 0
        self.failed_sends = 0
        self.send_times = deque(maxlen=1000)
        
        logger.info(f"📤 Producer {producer_id} initialized")
    
    async def send_message(self, topic: str, key: Optional[str], value: Any, 
                          headers: Dict[str, str] = None) -> Optional[int]:
        """Send message to topic"""
        start_time = time.time()
        
        try:
            # Create message
            message = StreamMessage(
                key=key,
                value=value,
                headers=headers or {},
                timestamp=datetime.now(),
                partition=-1,  # Will be assigned by topic
                offset=-1,     # Will be assigned by partition
                topic=topic,
                producer_id=self.producer_id
            )
            
            # Send to cluster
            offset = await self.cluster.produce_message(topic, message)
            
            if offset is not None:
                # Update metrics
                self.messages_sent += 1
                message_bytes = len(json.dumps(asdict(message), default=str).encode('utf-8'))
                self.bytes_sent += message_bytes
                
                send_time = (time.time() - start_time) * 1000
                self.send_times.append(send_time)
                
                return offset
            else:
                self.failed_sends += 1
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            self.failed_sends += 1
            return None
    
    def get_producer_stats(self) -> Dict[str, Any]:
        """Get producer statistics"""
        avg_send_time = sum(self.send_times) / max(len(self.send_times), 1)
        
        return {
            "producer_id": self.producer_id,
            "messages_sent": self.messages_sent,
            "bytes_sent": self.bytes_sent,
            "failed_sends": self.failed_sends,
            "success_rate": (self.messages_sent / max(self.messages_sent + self.failed_sends, 1)) * 100,
            "avg_send_time_ms": avg_send_time,
            "throughput_msg_per_sec": len(self.send_times) / max(sum(self.send_times) / 1000, 1) if self.send_times else 0
        }

class StreamingConsumer:
    """Consumer for streaming messages"""
    
    def __init__(self, consumer_id: str, consumer_group: str, cluster: 'DistributedStreamingCluster'):
        self.consumer_id = consumer_id
        self.consumer_group = consumer_group
        self.cluster = cluster
        
        # Subscription and offsets
        self.subscribed_topics = set()
        self.assigned_partitions = {}  # TopicPartition -> current_offset
        self.committed_offsets = {}    # TopicPartition -> committed_offset
        
        # Consumer state
        self.state = ConsumerState.STOPPED
        self.message_processor = None  # Callback function
        
        # Performance metrics
        self.messages_consumed = 0
        self.bytes_consumed = 0
        self.processing_times = deque(maxlen=1000)
        
        logger.info(f"📥 Consumer {consumer_id} initialized for group {consumer_group}")
    
    def subscribe(self, topics: List[str], message_processor: Callable[[StreamMessage], None]):
        """Subscribe to topics with message processor"""
        self.subscribed_topics = set(topics)
        self.message_processor = message_processor
        
        # Assign partitions (simplified - in real Kafka, this is done by coordinator)
        self.assigned_partitions = {}
        for topic in topics:
            if topic in self.cluster.topics:
                topic_obj = self.cluster.topics[topic]
                for partition_id in range(topic_obj.num_partitions):
                    tp = TopicPartition(topic, partition_id)
                    self.assigned_partitions[tp] = 0  # Start from offset 0
        
        logger.info(f"📋 Consumer {self.consumer_id} subscribed to topics: {topics}")
        logger.info(f"📍 Assigned partitions: {list(self.assigned_partitions.keys())}")
    
    async def start_consuming(self):
        """Start consuming messages"""
        if not self.subscribed_topics or not self.message_processor:
            logger.error("❌ Cannot start consuming: no topics subscribed or processor set")
            return
        
        self.state = ConsumerState.RUNNING
        logger.info(f"🚀 Consumer {self.consumer_id} started consuming")
        
        try:
            while self.state == ConsumerState.RUNNING:
                # Poll messages from assigned partitions
                messages_batch = await self._poll_messages()
                
                if messages_batch:
                    # Process messages
                    await self._process_messages(messages_batch)
                    
                    # Commit offsets periodically
                    await self._commit_offsets()
                else:
                    # No messages, short delay
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"❌ Error in consumer loop: {e}")
        finally:
            self.state = ConsumerState.STOPPED
            logger.info(f"🛑 Consumer {self.consumer_id} stopped")
    
    async def _poll_messages(self, max_messages: int = 100) -> List[StreamMessage]:
        """Poll messages from assigned partitions"""
        all_messages = []
        
        for tp, current_offset in self.assigned_partitions.items():
            messages = self.cluster.consume_messages(tp.topic, tp.partition, current_offset, max_messages // len(self.assigned_partitions))
            
            if messages:
                all_messages.extend(messages)
                # Update current offset
                self.assigned_partitions[tp] = messages[-1].offset + 1
        
        return all_messages
    
    async def _process_messages(self, messages: List[StreamMessage]):
        """Process batch of messages"""
        for message in messages:
            start_time = time.time()
            
            try:
                # Call user-provided message processor
                self.message_processor(message)
                
                # Update metrics
                self.messages_consumed += 1
                message_bytes = len(json.dumps(asdict(message), default=str).encode('utf-8'))
                self.bytes_consumed += message_bytes
                
                processing_time = (time.time() - start_time) * 1000
                self.processing_times.append(processing_time)
                
            except Exception as e:
                logger.error(f"❌ Error processing message {message.message_id}: {e}")
    
    async def _commit_offsets(self):
        """Commit current offsets"""
        for tp, current_offset in self.assigned_partitions.items():
            if tp not in self.committed_offsets or self.committed_offsets[tp] < current_offset:
                self.committed_offsets[tp] = current_offset
                
                # Store in cluster's offset storage
                await self.cluster.commit_consumer_offset(
                    self.consumer_group, tp.topic, tp.partition, current_offset
                )
    
    def stop(self):
        """Stop consuming"""
        self.state = ConsumerState.STOPPED
    
    def get_consumer_stats(self) -> Dict[str, Any]:
        """Get consumer statistics"""
        avg_processing_time = sum(self.processing_times) / max(len(self.processing_times), 1)
        
        return {
            "consumer_id": self.consumer_id,
            "consumer_group": self.consumer_group,
            "state": self.state.value,
            "subscribed_topics": list(self.subscribed_topics),
            "assigned_partitions": [str(tp) for tp in self.assigned_partitions.keys()],
            "messages_consumed": self.messages_consumed,
            "bytes_consumed": self.bytes_consumed,
            "avg_processing_time_ms": avg_processing_time,
            "throughput_msg_per_sec": len(self.processing_times) / max(sum(self.processing_times) / 1000, 1) if self.processing_times else 0
        }

class DistributedStreamingCluster:
    """Distributed streaming cluster (Kafka-like)"""
    
    def __init__(self):
        # Topic management
        self.topics = {}  # topic_name -> Topic
        
        # Consumer offset management
        self.consumer_offsets = {}  # (consumer_group, topic, partition) -> offset
        
        # Cluster metrics
        self.cluster_start_time = datetime.now()
        self.total_messages_produced = 0
        self.total_messages_consumed = 0
        self.total_bytes_processed = 0
        
        # Active producers and consumers
        self.producers = {}  # producer_id -> StreamingProducer
        self.consumers = {}  # consumer_id -> StreamingConsumer
        
        logger.info("🌐 Distributed streaming cluster initialized")
    
    def create_topic(self, name: str, num_partitions: int = 8, replication_factor: int = 3) -> bool:
        """Create new topic"""
        if name in self.topics:
            logger.warning(f"Topic '{name}' already exists")
            return False
        
        self.topics[name] = Topic(name, num_partitions, replication_factor)
        logger.info(f"✅ Created topic '{name}' with {num_partitions} partitions")
        return True
    
    def create_producer(self, producer_id: str) -> StreamingProducer:
        """Create new producer"""
        producer = StreamingProducer(producer_id, self)
        self.producers[producer_id] = producer
        return producer
    
    def create_consumer(self, consumer_id: str, consumer_group: str) -> StreamingConsumer:
        """Create new consumer"""
        consumer = StreamingConsumer(consumer_id, consumer_group, self)
        self.consumers[consumer_id] = consumer
        return consumer
    
    async def produce_message(self, topic_name: str, message: StreamMessage) -> Optional[int]:
        """Produce message to topic"""
        if topic_name not in self.topics:
            logger.error(f"❌ Topic '{topic_name}' does not exist")
            return None
        
        topic = self.topics[topic_name]
        offset = topic.produce_message(message)
        
        # Update cluster metrics
        self.total_messages_produced += 1
        message_bytes = len(json.dumps(asdict(message), default=str).encode('utf-8'))
        self.total_bytes_processed += message_bytes
        
        return offset
    
    def consume_messages(self, topic_name: str, partition: int, start_offset: int, 
                        max_messages: int = 100) -> List[StreamMessage]:
        """Consume messages from topic partition"""
        if topic_name not in self.topics:
            return []
        
        topic = self.topics[topic_name]
        messages = topic.consume_messages(partition, start_offset, max_messages)
        
        # Update cluster metrics
        self.total_messages_consumed += len(messages)
        return messages
    
    async def commit_consumer_offset(self, consumer_group: str, topic: str, 
                                   partition: int, offset: int):
        """Commit consumer offset"""
        key = (consumer_group, topic, partition)
        self.consumer_offsets[key] = ConsumerOffset(
            topic=topic,
            partition=partition,
            offset=offset,
            consumer_group=consumer_group,
            timestamp=datetime.now()
        )
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get comprehensive cluster statistics"""
        uptime = datetime.now() - self.cluster_start_time
        
        # Topic statistics
        topic_stats = {name: topic.get_topic_stats() for name, topic in self.topics.items()}
        
        # Producer statistics
        producer_stats = {pid: producer.get_producer_stats() for pid, producer in self.producers.items()}
        
        # Consumer statistics
        consumer_stats = {cid: consumer.get_consumer_stats() for cid, consumer in self.consumers.items()}
        
        # Aggregate metrics
        total_partitions = sum(topic.num_partitions for topic in self.topics.values())
        total_topic_bytes = sum(topic.get_topic_stats()["total_bytes"] for topic in self.topics.values())
        
        return {
            "cluster_uptime": str(uptime),
            "total_topics": len(self.topics),
            "total_partitions": total_partitions,
            "total_producers": len(self.producers),
            "total_consumers": len(self.consumers),
            "total_messages_produced": self.total_messages_produced,
            "total_messages_consumed": self.total_messages_consumed,
            "total_bytes_processed": self.total_bytes_processed,
            "total_topic_bytes": total_topic_bytes,
            "messages_per_second": self.total_messages_produced / max(uptime.total_seconds(), 1),
            "throughput_mb_per_sec": (self.total_bytes_processed / (1024 * 1024)) / max(uptime.total_seconds(), 1),
            "topics": topic_stats,
            "producers": producer_stats,
            "consumers": consumer_stats,
            "consumer_offsets": len(self.consumer_offsets),
            "timestamp": datetime.now().isoformat()
        }
    
    def print_cluster_dashboard(self):
        """Print comprehensive cluster dashboard"""
        stats = self.get_cluster_stats()
        
        print(f"\n{'='*80}")
        print(f"🌊 DISTRIBUTED STREAMING CLUSTER DASHBOARD 🌊")
        print(f"{'='*80}")
        
        print(f"🌐 Cluster Overview:")
        print(f"   Cluster Uptime: {stats['cluster_uptime']}")
        print(f"   Total Topics: {stats['total_topics']}")
        print(f"   Total Partitions: {stats['total_partitions']}")
        print(f"   Active Producers: {stats['total_producers']}")
        print(f"   Active Consumers: {stats['total_consumers']}")
        
        print(f"\n📊 Throughput Metrics:")
        print(f"   Messages Produced: {stats['total_messages_produced']:,}")
        print(f"   Messages Consumed: {stats['total_messages_consumed']:,}")
        print(f"   Messages/Second: {stats['messages_per_second']:.1f}")
        print(f"   Throughput: {stats['throughput_mb_per_sec']:.2f} MB/sec")
        print(f"   Total Data Processed: {stats['total_bytes_processed'] / (1024*1024):.1f} MB")
        
        print(f"\n📋 Topic Details:")
        for topic_name, topic_stats in stats['topics'].items():
            print(f"   {topic_name}:")
            print(f"     Partitions: {topic_stats['num_partitions']}")
            print(f"     Messages: {topic_stats['total_messages']:,}")
            print(f"     Size: {topic_stats['size_mb']:.2f} MB")
        
        print(f"\n📤 Producer Performance:")
        for producer_id, producer_stats in stats['producers'].items():
            print(f"   {producer_id}:")
            print(f"     Messages Sent: {producer_stats['messages_sent']:,}")
            print(f"     Success Rate: {producer_stats['success_rate']:.1f}%")
            print(f"     Avg Send Time: {producer_stats['avg_send_time_ms']:.2f} ms")
        
        print(f"\n📥 Consumer Performance:")
        for consumer_id, consumer_stats in stats['consumers'].items():
            print(f"   {consumer_id} (Group: {consumer_stats['consumer_group']}):")
            print(f"     State: {consumer_stats['state']}")
            print(f"     Messages Consumed: {consumer_stats['messages_consumed']:,}")
            print(f"     Avg Processing Time: {consumer_stats['avg_processing_time_ms']:.2f} ms")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

# Event generators for Indian applications
def generate_swiggy_order_event() -> Dict[str, Any]:
    """Generate Swiggy order tracking event"""
    order_statuses = ["PLACED", "CONFIRMED", "PREPARING", "PICKED_UP", "OUT_FOR_DELIVERY", "DELIVERED"]
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune"]
    
    return {
        "event_type": "ORDER_STATUS_UPDATE",
        "order_id": f"SWG{random.randint(100000, 999999)}",
        "customer_id": f"CUST{random.randint(10000, 99999)}",
        "restaurant_id": f"REST{random.randint(1000, 9999)}",
        "delivery_partner_id": f"DP{random.randint(100, 999)}",
        "status": random.choice(order_statuses),
        "city": random.choice(cities),
        "area": f"Area {random.randint(1, 50)}",
        "coordinates": {
            "lat": 18.9 + random.uniform(-0.5, 0.5),
            "lng": 72.8 + random.uniform(-0.5, 0.5)
        },
        "order_value": random.randint(200, 1500),
        "payment_method": random.choice(["UPI", "Card", "Cash", "Wallet"]),
        "estimated_delivery_time": random.randint(20, 60),
        "timestamp": datetime.now().isoformat()
    }

def generate_ola_ride_event() -> Dict[str, Any]:
    """Generate Ola ride tracking event"""
    ride_statuses = ["REQUESTED", "ACCEPTED", "DRIVER_ARRIVING", "TRIP_STARTED", "TRIP_COMPLETED", "CANCELLED"]
    car_types = ["Mini", "Prime", "Auto", "Bike", "Lux"]
    
    return {
        "event_type": "RIDE_STATUS_UPDATE",
        "ride_id": f"OLA{random.randint(100000, 999999)}",
        "customer_id": f"RIDER{random.randint(10000, 99999)}",
        "driver_id": f"DRIVER{random.randint(1000, 9999)}",
        "status": random.choice(ride_statuses),
        "car_type": random.choice(car_types),
        "pickup_location": {
            "lat": 19.0 + random.uniform(-0.1, 0.1),
            "lng": 72.8 + random.uniform(-0.1, 0.1),
            "address": f"Pickup Address {random.randint(1, 100)}"
        },
        "drop_location": {
            "lat": 19.0 + random.uniform(-0.1, 0.1),
            "lng": 72.8 + random.uniform(-0.1, 0.1),
            "address": f"Drop Address {random.randint(1, 100)}"
        },
        "fare_estimate": random.randint(50, 500),
        "distance_km": random.uniform(2, 20),
        "eta_minutes": random.randint(5, 30),
        "payment_method": random.choice(["UPI", "Card", "Cash", "Wallet"]),
        "timestamp": datetime.now().isoformat()
    }

def generate_payment_event() -> Dict[str, Any]:
    """Generate UPI payment event"""
    payment_statuses = ["INITIATED", "PROCESSING", "SUCCESS", "FAILED", "TIMEOUT"]
    
    return {
        "event_type": "UPI_PAYMENT",
        "transaction_id": f"UPI{int(time.time())}{random.randint(1000, 9999)}",
        "payer_vpa": f"user{random.randint(1000, 9999)}@paytm",
        "payee_vpa": f"merchant{random.randint(100, 999)}@phonepe",
        "amount": random.choice([100, 200, 500, 1000, 2000, 5000]),
        "status": random.choice(payment_statuses),
        "bank_ref_number": f"BRN{random.randint(100000, 999999)}",
        "merchant_name": random.choice(["Swiggy", "Zomato", "Amazon", "Flipkart", "BookMyShow"]),
        "category": random.choice(["Food", "Shopping", "Travel", "Entertainment", "Utility"]),
        "timestamp": datetime.now().isoformat()
    }

async def simulate_indian_app_streaming(cluster: DistributedStreamingCluster, duration_minutes: int = 5):
    """Simulate high-volume streaming for Indian applications"""
    logger.info(f"🇮🇳 Starting Indian app streaming simulation for {duration_minutes} minutes")
    
    # Create topics
    cluster.create_topic("swiggy_orders", num_partitions=12, replication_factor=3)
    cluster.create_topic("ola_rides", num_partitions=8, replication_factor=3)
    cluster.create_topic("upi_payments", num_partitions=16, replication_factor=3)
    
    # Create producers
    swiggy_producer = cluster.create_producer("swiggy_producer")
    ola_producer = cluster.create_producer("ola_producer")
    payment_producer = cluster.create_producer("payment_producer")
    
    # Message processors for consumers
    def process_order_event(message: StreamMessage):
        event = message.value
        if event.get("status") == "DELIVERED":
            logger.info(f"🍕 Order delivered: {event['order_id']} in {event['city']}")
    
    def process_ride_event(message: StreamMessage):
        event = message.value
        if event.get("status") == "TRIP_COMPLETED":
            logger.info(f"🚗 Ride completed: {event['ride_id']} - ₹{event['fare_estimate']}")
    
    def process_payment_event(message: StreamMessage):
        event = message.value
        if event.get("status") == "SUCCESS":
            logger.info(f"💳 Payment success: ₹{event['amount']} from {event['payer_vpa']}")
    
    # Create consumers
    order_consumer = cluster.create_consumer("order_consumer", "order_processing_group")
    ride_consumer = cluster.create_consumer("ride_consumer", "ride_tracking_group")
    payment_consumer = cluster.create_consumer("payment_consumer", "payment_processing_group")
    
    # Subscribe consumers
    order_consumer.subscribe(["swiggy_orders"], process_order_event)
    ride_consumer.subscribe(["ola_rides"], process_ride_event)
    payment_consumer.subscribe(["upi_payments"], process_payment_event)
    
    # Start consumers
    consumer_tasks = [
        asyncio.create_task(order_consumer.start_consuming()),
        asyncio.create_task(ride_consumer.start_consuming()),
        asyncio.create_task(payment_consumer.start_consuming())
    ]
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    event_count = 0
    
    try:
        while time.time() < end_time:
            # Simulate peak traffic patterns
            current_hour = datetime.now().hour
            
            if 12 <= current_hour <= 14 or 19 <= current_hour <= 22:
                # Peak hours - higher event rate
                events_per_second = random.randint(100, 200)
            else:
                # Normal hours
                events_per_second = random.randint(50, 100)
            
            # Generate and send events
            producer_tasks = []
            
            for _ in range(events_per_second):
                event_type = random.choices(
                    ["order", "ride", "payment"],
                    weights=[40, 30, 30]
                )[0]
                
                if event_type == "order":
                    event = generate_swiggy_order_event()
                    task = swiggy_producer.send_message(
                        "swiggy_orders",
                        event["order_id"],
                        event,
                        {"event_type": "ORDER_UPDATE"}
                    )
                elif event_type == "ride":
                    event = generate_ola_ride_event()
                    task = ola_producer.send_message(
                        "ola_rides",
                        event["ride_id"],
                        event,
                        {"event_type": "RIDE_UPDATE"}
                    )
                else:  # payment
                    event = generate_payment_event()
                    task = payment_producer.send_message(
                        "upi_payments",
                        event["transaction_id"],
                        event,
                        {"event_type": "PAYMENT_UPDATE"}
                    )
                
                producer_tasks.append(task)
                event_count += 1
            
            # Execute producer tasks
            if producer_tasks:
                await asyncio.gather(*producer_tasks, return_exceptions=True)
            
            # Print dashboard every 30 seconds
            if event_count % 2000 == 0:
                cluster.print_cluster_dashboard()
            
            # Small delay
            await asyncio.sleep(1.0)
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    finally:
        # Stop consumers
        order_consumer.stop()
        ride_consumer.stop()
        payment_consumer.stop()
        
        # Wait for consumer tasks to complete
        for task in consumer_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    logger.info(f"🏁 Streaming simulation completed! Processed {event_count} events")
    
    # Final dashboard
    cluster.print_cluster_dashboard()

async def main():
    """Main demo function"""
    print("🇮🇳 Distributed Streaming System (Kafka-like)")
    print("🌊 High-throughput event streaming for Indian applications")
    print("📊 Real-time processing of orders, rides, और payments...\n")
    
    # Initialize streaming cluster
    cluster = DistributedStreamingCluster()
    
    try:
        # Show initial cluster status
        cluster.print_cluster_dashboard()
        
        # Run streaming simulation
        await simulate_indian_app_streaming(cluster, duration_minutes=3)
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"💡 Production system capabilities:")
        print(f"   - Handle 100M+ events per day")
        print(f"   - 1M+ messages per second throughput")
        print(f"   - <10ms latency for event processing")
        print(f"   - Automatic partitioning और load balancing")
        print(f"   - Fault-tolerant replication")
        print(f"   - Real-time consumer group management")
        
    except Exception as e:
        logger.error(f"❌ Error in simulation: {e}")

if __name__ == "__main__":
    # Run the distributed streaming system demo
    asyncio.run(main())