"""
Event Streaming Episode - Kafka Consumer with Consumer Groups
Production-ready consumer implementation with proper error handling

Author: Hindi Tech Podcast Series
"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
import signal
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
import threading

# Configure logging - Consumer के लिए logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] %(message)s'
)
logger = logging.getLogger(__name__)

class SwiggyOrderConsumer:
    """
    Swiggy order events consume करने के लिए consumer group based implementation
    Multiple instances run कर सकते हैं parallel processing के लिए
    """
    
    def __init__(self, group_id: str, service_name: str, 
                 bootstrap_servers: str = 'localhost:9092'):
        """
        Consumer initialize करते हैं with production configurations
        """
        self.group_id = group_id
        self.service_name = service_name
        self.bootstrap_servers = bootstrap_servers
        self.topic = 'swiggy-orders'
        self.running = True
        
        # Consumer configuration - Production ready settings
        # High availability और fault tolerance के लिए
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            
            # Deserialization settings
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            
            # Consumer behavior settings
            auto_offset_reset='earliest',  # शुरुआत से messages पढ़ें अगर offset नहीं मिला
            enable_auto_commit=False,      # Manual commit करेंगे reliability के लिए
            max_poll_records=10,           # एक साथ 10 records ही process करें
            
            # Session और heartbeat settings
            session_timeout_ms=30000,      # 30 सेकंड session timeout
            heartbeat_interval_ms=10000,   # 10 सेकंड heartbeat
            
            # Performance settings
            fetch_min_bytes=1024,          # Minimum 1KB fetch करें
            fetch_max_wait_ms=500,         # Maximum 500ms wait करें
        )
        
        # Statistics tracking
        self.processed_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        logger.info(f"Consumer initialized - Group: {group_id}, Service: {service_name}")

    def process_order_placed(self, order_event: Dict[str, Any]) -> bool:
        """
        ORDER_PLACED event process करते हैं
        Restaurant notification और inventory update के लिए
        """
        try:
            order_id = order_event['order_id']
            restaurant_id = order_event['restaurant_id']
            items = order_event['items']
            total_amount = order_event['total_amount']
            
            logger.info(f"Processing ORDER_PLACED: {order_id}")
            
            # Restaurant को notify करें - Real implementation में API call होगी
            self._notify_restaurant(restaurant_id, order_event)
            
            # Inventory update करें
            self._update_inventory(restaurant_id, items)
            
            # Payment processing initiate करें
            self._initiate_payment_processing(order_id, total_amount)
            
            # ETA calculation करें
            eta = self._calculate_delivery_eta(restaurant_id, order_event['metadata']['location'])
            
            logger.info(f"✅ Order {order_id} processed successfully. ETA: {eta} minutes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing ORDER_PLACED {order_event.get('order_id', 'unknown')}: {e}")
            return False

    def process_order_status_update(self, order_event: Dict[str, Any]) -> bool:
        """
        Order status updates process करते हैं
        Customer notification और delivery partner coordination के लिए
        """
        try:
            order_id = order_event['order_id']
            status = order_event['status']
            
            logger.info(f"Processing ORDER_STATUS_UPDATE: {order_id} -> {status}")
            
            if status == 'CONFIRMED':
                self._start_food_preparation(order_id)
            elif status == 'PREPARING':
                self._assign_delivery_partner(order_id)
            elif status == 'READY':
                self._notify_delivery_partner(order_id)
            elif status == 'PICKED_UP':
                self._start_live_tracking(order_id)
            elif status == 'DELIVERED':
                self._complete_order_cycle(order_id)
            
            # Customer को real-time notification भेजें
            self._send_customer_notification(order_event)
            
            logger.info(f"✅ Status update {order_id} processed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing status update {order_event.get('order_id', 'unknown')}: {e}")
            return False

    def _notify_restaurant(self, restaurant_id: str, order_event: Dict[str, Any]):
        """Restaurant को new order की notification भेजते हैं"""
        logger.info(f"📱 Notifying restaurant {restaurant_id} about new order")
        # Real implementation में restaurant POS system को API call करेंगे
        time.sleep(0.1)  # Simulate API call

    def _update_inventory(self, restaurant_id: str, items: List[Dict]):
        """Restaurant inventory update करते हैं"""
        logger.info(f"📦 Updating inventory for restaurant {restaurant_id}")
        for item in items:
            logger.info(f"   - {item['name']}: -{item['quantity']}")
        time.sleep(0.1)  # Simulate database update

    def _initiate_payment_processing(self, order_id: str, amount: float):
        """Payment processing initiate करते हैं"""
        logger.info(f"💳 Initiating payment processing for {order_id}: ₹{amount}")
        time.sleep(0.1)  # Simulate payment gateway call

    def _calculate_delivery_eta(self, restaurant_id: str, location: str) -> int:
        """Delivery ETA calculate करते हैं Mumbai traffic के साथ"""
        # Mumbai traffic patterns के based पर ETA calculation
        base_time = 30  # Base 30 minutes
        traffic_factor = 1.2 if 'Bandra' in location else 1.0  # Bandra में traffic ज्यादा
        return int(base_time * traffic_factor)

    def _start_food_preparation(self, order_id: str):
        """Food preparation start करते हैं"""
        logger.info(f"👨‍🍳 Food preparation started for {order_id}")

    def _assign_delivery_partner(self, order_id: str):
        """Delivery partner assign करते हैं"""
        logger.info(f"🛵 Assigning delivery partner for {order_id}")

    def _notify_delivery_partner(self, order_id: str):
        """Delivery partner को pickup notification भेजते हैं"""
        logger.info(f"📲 Notifying delivery partner for pickup: {order_id}")

    def _start_live_tracking(self, order_id: str):
        """Live tracking start करते हैं"""
        logger.info(f"📍 Live tracking started for {order_id}")

    def _complete_order_cycle(self, order_id: str):
        """Order cycle complete करते हैं"""
        logger.info(f"✅ Order cycle completed for {order_id}")

    def _send_customer_notification(self, order_event: Dict[str, Any]):
        """Customer को notification भेजते हैं"""
        logger.info(f"📢 Sending notification to user {order_event['user_id']}")

    def consume_messages(self):
        """
        Main consumption loop - Messages को continuously process करते हैं
        Graceful shutdown और error handling के साथ
        """
        logger.info(f"🚀 Starting consumption for topic: {self.topic}")
        
        try:
            while self.running:
                try:
                    # Messages poll करते हैं with timeout
                    message_pack = self.consumer.poll(timeout_ms=1000)
                    
                    if not message_pack:
                        continue  # No messages, continue polling
                    
                    # Process each partition's messages
                    for topic_partition, messages in message_pack.items():
                        logger.info(f"📨 Processing {len(messages)} messages from "
                                   f"partition {topic_partition.partition}")
                        
                        for message in messages:
                            success = self._process_single_message(message)
                            
                            if success:
                                self.processed_count += 1
                            else:
                                self.error_count += 1
                                # Error handling - Dead letter queue में भेज सकते हैं
                        
                        # Manual commit after processing all messages from partition
                        # Reliability ensure करने के लिए
                        try:
                            self.consumer.commit()
                            logger.debug(f"✅ Committed offset for partition {topic_partition.partition}")
                        except Exception as e:
                            logger.error(f"❌ Failed to commit offset: {e}")
                    
                    # Performance stats print करें
                    if self.processed_count % 100 == 0 and self.processed_count > 0:
                        self._print_performance_stats()
                
                except KafkaError as e:
                    logger.error(f"Kafka error during consumption: {e}")
                    time.sleep(5)  # Wait before retrying
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down gracefully...")
        finally:
            self._shutdown()

    def _process_single_message(self, message) -> bool:
        """
        Single message को process करते हैं proper error handling के साथ
        """
        try:
            order_event = message.value
            event_type = order_event.get('event_type', 'UNKNOWN')
            
            logger.info(f"📍 Processing message: {event_type} - "
                       f"Partition: {message.partition}, Offset: {message.offset}")
            
            # Event type के based पर different processing
            if event_type == 'ORDER_PLACED':
                return self.process_order_placed(order_event)
            elif event_type in ['ORDER_CONFIRMED', 'ORDER_PREPARING', 'ORDER_READY', 
                               'ORDER_PICKED_UP', 'ORDER_DELIVERED']:
                return self.process_order_status_update(order_event)
            else:
                logger.warning(f"⚠️ Unknown event type: {event_type}")
                return True  # Skip unknown events
                
        except Exception as e:
            logger.error(f"❌ Error processing message at offset {message.offset}: {e}")
            return False

    def _print_performance_stats(self):
        """Performance statistics print करते हैं"""
        duration = (datetime.now() - self.start_time).total_seconds()
        rate = self.processed_count / duration if duration > 0 else 0
        
        logger.info(f"📊 Performance Stats - Service: {self.service_name}")
        logger.info(f"   Processed: {self.processed_count} messages")
        logger.info(f"   Errors: {self.error_count}")
        logger.info(f"   Rate: {rate:.2f} messages/second")
        logger.info(f"   Duration: {duration:.2f} seconds")

    def _shutdown(self):
        """Graceful shutdown - Resources properly cleanup करते हैं"""
        logger.info("🛑 Shutting down consumer...")
        self.running = False
        
        try:
            # Final commit करें
            self.consumer.commit()
            logger.info("✅ Final offset commit completed")
        except Exception as e:
            logger.error(f"❌ Error during final commit: {e}")
        
        # Consumer close करें
        self.consumer.close()
        
        # Final stats print करें
        self._print_performance_stats()
        logger.info(f"✅ Consumer shutdown completed - Service: {self.service_name}")

def signal_handler(signum, frame):
    """Signal handler for graceful shutdown"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    global consumer_instance
    if consumer_instance:
        consumer_instance.running = False

def run_consumer_service(group_id: str, service_name: str):
    """
    Consumer service को run करते हैं specific group ID के साथ
    Multiple services parallel में run हो सकती हैं
    """
    global consumer_instance
    
    # Signal handlers setup करें graceful shutdown के लिए
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        consumer_instance = SwiggyOrderConsumer(group_id, service_name)
        
        print(f"🚀 Starting {service_name} with consumer group: {group_id}")
        print(f"📱 Processing Swiggy order events from topic: swiggy-orders")
        print("-" * 60)
        
        consumer_instance.consume_messages()
        
    except Exception as e:
        logger.error(f"❌ Error running consumer service: {e}")
    finally:
        print(f"\n✅ {service_name} shutdown completed!")

if __name__ == "__main__":
    # Different services demonstrate करने के लिए
    # Real production में अलग-अलग servers पर run होंगी
    
    service_configs = [
        ('restaurant-service-group', 'Restaurant Notification Service'),
        ('delivery-service-group', 'Delivery Partner Service'),
        ('customer-service-group', 'Customer Notification Service'),
        ('analytics-service-group', 'Real-time Analytics Service')
    ]
    
    if len(sys.argv) > 1:
        # Specific service run करें
        service_index = int(sys.argv[1]) if sys.argv[1].isdigit() else 0
        if service_index < len(service_configs):
            group_id, service_name = service_configs[service_index]
            run_consumer_service(group_id, service_name)
        else:
            print("Invalid service index. Available services:")
            for i, (group, name) in enumerate(service_configs):
                print(f"  {i}: {name}")
    else:
        # Default service run करें
        group_id, service_name = service_configs[0]
        run_consumer_service(group_id, service_name)
        
    print("\n💡 To run different services:")
    print("  python 02_kafka_consumer_groups.py 0  # Restaurant Service")
    print("  python 02_kafka_consumer_groups.py 1  # Delivery Service") 
    print("  python 02_kafka_consumer_groups.py 2  # Customer Service")
    print("  python 02_kafka_consumer_groups.py 3  # Analytics Service")