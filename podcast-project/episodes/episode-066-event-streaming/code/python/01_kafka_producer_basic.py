"""
Event Streaming Episode - Basic Kafka Producer
Production-ready Kafka producer with error handling and monitoring

Author: Hindi Tech Podcast Series
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging - लॉगिंग सेटअप करते हैं
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SwiggyOrderProducer:
    """
    Swiggy जैसे food delivery app के लिए order events भेजने वाला producer
    Real-time order updates के लिए designed है
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        """
        Producer initialize करते हैं with production-ready configurations
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = 'swiggy-orders'
        
        # Production-ready producer configuration
        # अधिक reliability और performance के लिए settings
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8'),
            
            # Reliability settings - डेटा loss avoid करने के लिए
            acks='all',  # सभी replicas confirm करें
            retries=3,   # Failed messages को retry करें
            
            # Performance settings
            batch_size=16384,  # 16KB batch size
            linger_ms=10,      # 10ms तक wait करें batching के लिए
            buffer_memory=33554432,  # 32MB buffer
            
            # Compression for better throughput
            compression_type='gzip',
            
            # Timeout settings
            request_timeout_ms=30000,
            delivery_timeout_ms=120000
        )
        
        logger.info(f"Swiggy Order Producer initialized for topic: {self.topic}")

    def create_order_event(self, order_id: str, user_id: str, 
                          restaurant_id: str, items: list, 
                          total_amount: float) -> Dict[str, Any]:
        """
        Order event create करते हैं proper structure के साथ
        """
        return {
            'event_id': f"order_{order_id}_{int(time.time())}",
            'event_type': 'ORDER_PLACED',
            'timestamp': datetime.now().isoformat(),
            'order_id': order_id,
            'user_id': user_id,
            'restaurant_id': restaurant_id,
            'items': items,
            'total_amount': total_amount,
            'status': 'PLACED',
            'delivery_partner_id': None,
            'estimated_delivery_time': None,
            'metadata': {
                'app_version': '1.2.3',
                'platform': 'android',
                'location': 'Mumbai_Bandra'
            }
        }

    def send_order_event(self, order_event: Dict[str, Any]) -> Optional[str]:
        """
        Order event को Kafka topic पर send करते हैं
        Proper error handling के साथ
        """
        try:
            # Order ID को key बनाते हैं partitioning के लिए
            order_key = order_event['order_id']
            
            # Asynchronous send with callback
            future = self.producer.send(
                self.topic, 
                key=order_key, 
                value=order_event
            )
            
            # Add callback for success/failure handling
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
            # Wait for acknowledgment (optional for sync behavior)
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Order event sent successfully: {order_key} -> "
                       f"Topic: {record_metadata.topic}, "
                       f"Partition: {record_metadata.partition}, "
                       f"Offset: {record_metadata.offset}")
            
            return f"{record_metadata.partition}:{record_metadata.offset}"
            
        except KafkaError as e:
            logger.error(f"Failed to send order event: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def _on_send_success(self, record_metadata):
        """Success callback - जब message successfully send हो जाए"""
        logger.info(f"Message delivered to {record_metadata.topic} "
                   f"[{record_metadata.partition}] at offset {record_metadata.offset}")

    def _on_send_error(self, excp):
        """Error callback - जब message send fail हो जाए"""
        logger.error(f"Failed to deliver message: {excp}")

    def send_bulk_orders(self, orders: list) -> Dict[str, Any]:
        """
        Multiple orders को efficiently send करते हैं
        Batch processing के लिए useful है
        """
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        logger.info(f"Sending bulk orders: {len(orders)} orders")
        
        for order_data in orders:
            order_event = self.create_order_event(**order_data)
            result = self.send_order_event(order_event)
            
            if result:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(order_data['order_id'])
        
        # Flush करके सभी pending messages send करें
        self.producer.flush()
        
        logger.info(f"Bulk order results: {results}")
        return results

    def close(self):
        """Producer को properly close करते हैं"""
        if self.producer:
            self.producer.flush()  # Pending messages send करें
            self.producer.close()
            logger.info("Kafka producer closed successfully")

def simulate_swiggy_orders():
    """
    Real-world Swiggy orders simulate करते हैं
    Mumbai restaurants के data के साथ
    """
    producer = SwiggyOrderProducer()
    
    # Sample Mumbai restaurant orders
    # Mumbai के famous restaurants के orders
    sample_orders = [
        {
            'order_id': 'SWG_001_2024',
            'user_id': 'user_mumbai_001',
            'restaurant_id': 'trishna_fort',
            'items': [
                {'name': 'Butter Chicken', 'price': 450, 'quantity': 1},
                {'name': 'Garlic Naan', 'price': 120, 'quantity': 2}
            ],
            'total_amount': 690.0
        },
        {
            'order_id': 'SWG_002_2024',
            'user_id': 'user_mumbai_002', 
            'restaurant_id': 'theobroma_bandra',
            'items': [
                {'name': 'Chocolate Truffle Cake', 'price': 800, 'quantity': 1},
                {'name': 'Black Forest Pastry', 'price': 350, 'quantity': 2}
            ],
            'total_amount': 1500.0
        },
        {
            'order_id': 'SWG_003_2024',
            'user_id': 'user_mumbai_003',
            'restaurant_id': 'britannia_ballard',
            'items': [
                {'name': 'Berry Pulav', 'price': 420, 'quantity': 1},
                {'name': 'Mutton Berry Pulav', 'price': 650, 'quantity': 1}
            ],
            'total_amount': 1070.0
        }
    ]
    
    try:
        # Individual orders send करें
        logger.info("Sending individual orders...")
        for order_data in sample_orders:
            order_event = producer.create_order_event(**order_data)
            result = producer.send_order_event(order_event)
            
            if result:
                print(f"✅ Order {order_data['order_id']} sent successfully at {result}")
            else:
                print(f"❌ Failed to send order {order_data['order_id']}")
            
            time.sleep(1)  # Rate limiting
        
        # Bulk orders भी send करें demonstration के लिए
        logger.info("Sending bulk orders...")
        bulk_results = producer.send_bulk_orders(sample_orders)
        print(f"\n📊 Bulk Order Results: {bulk_results}")
        
        # Producer metrics show करें
        producer_metrics = producer.producer.metrics()
        print(f"\n📈 Producer Metrics Summary:")
        print(f"Records sent: {producer_metrics.get('producer-metrics', {}).get('record-send-total', 0)}")
        print(f"Batch size avg: {producer_metrics.get('producer-metrics', {}).get('batch-size-avg', 0):.2f}")
        
    except Exception as e:
        logger.error(f"Error in order simulation: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    print("🍕 Starting Swiggy Order Producer Simulation...")
    print("📱 Real-time food delivery order streaming with Kafka")
    print("-" * 60)
    
    simulate_swiggy_orders()
    
    print("\n✅ Order streaming simulation completed!")
    print("💡 Check Kafka topic 'swiggy-orders' for streamed events")