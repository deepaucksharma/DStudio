#!/usr/bin/env python3
"""
Kafka Producer/Consumer for Real-time Analytics
Episode 43: Real-time Analytics at Scale

यह example Kafka producer और consumer का basic setup दिखाता है
जो production में real-time events handle करने के लिए use होता है।

Use Case: Flipkart BBD में order events को real-time track करना
"""

import json
import time
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import logging
import threading
from typing import Dict, Any

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlipkartOrderProducer:
    """
    Flipkart Big Billion Day order events producer
    हर second में thousands of orders generate करता है
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # Production settings for high throughput
            batch_size=16384,  # 16KB batch size
            linger_ms=10,      # Wait 10ms for batching
            compression_type='snappy',
            retries=3,
            acks='all'  # Wait for all replicas
        )
        
    def generate_order_event(self, user_id: str) -> Dict[str, Any]:
        """Generate realistic order event data"""
        import random
        
        products = [
            {"id": "phone_001", "name": "iPhone 15", "price": 79999, "category": "electronics"},
            {"id": "laptop_001", "name": "MacBook Air", "price": 119999, "category": "electronics"},
            {"id": "shirt_001", "name": "Cotton Shirt", "price": 1299, "category": "fashion"},
            {"id": "book_001", "name": "System Design", "price": 599, "category": "books"}
        ]
        
        product = random.choice(products)
        quantity = random.randint(1, 3)
        
        return {
            "order_id": f"FKO_{int(time.time())}_{user_id}",
            "user_id": user_id,
            "product": product,
            "quantity": quantity,
            "total_amount": product["price"] * quantity,
            "timestamp": datetime.now().isoformat(),
            "location": {
                "city": random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]),
                "state": "Maharashtra"  # For simplicity
            },
            "payment_method": random.choice(["UPI", "Credit Card", "Debit Card", "COD"]),
            "discount_applied": random.uniform(0, 0.3)  # 0-30% discount
        }
    
    def produce_orders(self, num_orders: int = 100, orders_per_second: int = 50):
        """
        Simulate BBD traffic - orders_per_second orders continuously
        Real BBD में 10,000+ orders per second आते हैं
        """
        logger.info(f"शुरू कर रहे हैं {orders_per_second} orders per second simulation")
        
        for i in range(num_orders):
            user_id = f"user_{i % 1000}"  # 1000 unique users
            order_event = self.generate_order_event(user_id)
            
            try:
                # Partition by user_id for ordered processing
                future = self.producer.send(
                    topic='flipkart_orders',
                    key=user_id,
                    value=order_event
                )
                
                # Optional: Wait for confirmation (reduces throughput)
                # record_metadata = future.get(timeout=10)
                
                if i % 100 == 0:
                    logger.info(f"भेजे गए orders: {i}")
                
                # Rate limiting
                time.sleep(1.0 / orders_per_second)
                
            except KafkaError as e:
                logger.error(f"Order send failed: {e}")
        
        # Flush remaining messages
        self.producer.flush()
        logger.info("सभी orders successfully भेज दिए गए")
    
    def close(self):
        self.producer.close()

class FlipkartOrderConsumer:
    """
    Real-time order consumer for analytics
    Orders को consume करके real-time metrics calculate करता है
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092', group_id: str = 'analytics_group'):
        self.consumer = KafkaConsumer(
            'flipkart_orders',
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            # Start from earliest available message
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            auto_commit_interval_ms=1000
        )
        
        # Real-time metrics
        self.metrics = {
            "total_orders": 0,
            "total_revenue": 0.0,
            "orders_by_city": {},
            "orders_by_category": {},
            "payment_methods": {},
            "last_updated": None
        }
        
    def process_order(self, order: Dict[str, Any]):
        """Process single order and update metrics"""
        self.metrics["total_orders"] += 1
        self.metrics["total_revenue"] += order["total_amount"]
        
        # City-wise breakdown
        city = order["location"]["city"]
        self.metrics["orders_by_city"][city] = self.metrics["orders_by_city"].get(city, 0) + 1
        
        # Category-wise breakdown
        category = order["product"]["category"]
        self.metrics["orders_by_category"][category] = self.metrics["orders_by_category"].get(category, 0) + 1
        
        # Payment method breakdown
        payment = order["payment_method"]
        self.metrics["payment_methods"][payment] = self.metrics["payment_methods"].get(payment, 0) + 1
        
        self.metrics["last_updated"] = datetime.now().isoformat()
    
    def print_metrics(self):
        """Print current real-time metrics"""
        print(f"\n=== Flipkart BBD Real-time Analytics ===")
        print(f"कुल Orders: {self.metrics['total_orders']:,}")
        print(f"कुल Revenue: ₹{self.metrics['total_revenue']:,.2f}")
        print(f"Last Updated: {self.metrics['last_updated']}")
        
        print("\nCity-wise Orders:")
        for city, count in sorted(self.metrics["orders_by_city"].items(), key=lambda x: x[1], reverse=True):
            print(f"  {city}: {count:,}")
        
        print("\nCategory-wise Orders:")
        for category, count in sorted(self.metrics["orders_by_category"].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count:,}")
            
        print("\nPayment Methods:")
        for method, count in sorted(self.metrics["payment_methods"].items(), key=lambda x: x[1], reverse=True):
            print(f"  {method}: {count:,}")
    
    def consume_orders(self, max_messages: int = None):
        """
        Consume orders and update real-time analytics
        Production में यह continuously run होता है
        """
        logger.info("शुरू कर रहे हैं real-time order consumption...")
        
        message_count = 0
        try:
            for message in self.consumer:
                order = message.value
                self.process_order(order)
                message_count += 1
                
                # Print metrics every 50 orders
                if message_count % 50 == 0:
                    self.print_metrics()
                
                if max_messages and message_count >= max_messages:
                    break
                    
        except KeyboardInterrupt:
            logger.info("Consumer को manually stop किया गया")
        finally:
            self.consumer.close()
            self.print_metrics()

def run_producer_demo():
    """Run producer demo"""
    producer = FlipkartOrderProducer()
    try:
        producer.produce_orders(num_orders=500, orders_per_second=20)
    finally:
        producer.close()

def run_consumer_demo():
    """Run consumer demo"""
    consumer = FlipkartOrderConsumer()
    consumer.consume_orders(max_messages=100)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "producer":
            run_producer_demo()
        elif sys.argv[1] == "consumer":
            run_consumer_demo()
        else:
            print("Usage: python kafka_example.py [producer|consumer]")
    else:
        # Run both in separate threads for demo
        print("Running producer and consumer demo...")
        
        producer_thread = threading.Thread(target=run_producer_demo)
        consumer_thread = threading.Thread(target=run_consumer_demo)
        
        producer_thread.start()
        time.sleep(2)  # Let producer start first
        consumer_thread.start()
        
        producer_thread.join()
        consumer_thread.join()