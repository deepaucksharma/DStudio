#!/usr/bin/env python3
"""
Episode 124: Kafka Real-time Producer
Mumbai Local Train Style Data Streaming

Bhai, jaise Mumbai local train har 2-3 minute mein aati hai,
waise hi ye producer har second thousands of events send karta hai.
Real-time data streaming ka real power dekho!

Author: Hindi Podcast Team
Cost: ₹5,000-15,000/month for production Kafka cluster
Throughput: 1M+ messages per second possible
"""

import json
import time
import random
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from kafka import KafkaProducer
from kafka.errors import KafkaError
import avro.schema
from avro.io import DatumWriter, BinaryEncoder
import io
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

logging.basicConfig(level=logging.INFO, format='🚂 %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MumbaiTrainEvent:
    \"\"\"Mumbai Local Train real-time event\"\"\"
    train_id: str
    route: str  # Western, Central, Harbour
    station_from: str
    station_to: str
    departure_time: str
    arrival_time: str
    passenger_count: int
    delay_minutes: int
    coach_count: int
    event_timestamp: str
    event_type: str  # arrival, departure, delay, breakdown

@dataclass
class UPITransactionEvent:
    \"\"\"UPI transaction real-time event\"\"\"
    transaction_id: str
    payer_vpa: str  # masked
    payee_vpa: str  # masked
    amount: float
    currency: str
    merchant_category: str
    location: str
    timestamp: str
    status: str  # success, failed, pending
    bank_code: str

@dataclass
class EcommerceOrderEvent:
    \"\"\"E-commerce order real-time event\"\"\"
    order_id: str
    customer_id: str  # hashed
    product_category: str
    order_value: float
    payment_method: str
    delivery_city: str
    warehouse_location: str
    timestamp: str
    event_type: str  # placed, confirmed, shipped, delivered
    platform: str  # flipkart, amazon, myntra

class MumbaiKafkaProducer:
    \"\"\"
    Mumbai Style Kafka Producer - Real-time Event Streaming
    Har second thousands of events produce karta hai
    \"\"\"
    
    def __init__(self, 
                 bootstrap_servers: List[str] = ['localhost:9092'],
                 batch_size: int = 16384,
                 linger_ms: int = 10):
        
        self.bootstrap_servers = bootstrap_servers
        self.running = False
        
        # Kafka producer configuration - Mumbai optimized
        self.producer_config = {
            'bootstrap_servers': bootstrap_servers,
            'value_serializer': self._json_serializer,
            'key_serializer': self._string_serializer,
            'batch_size': batch_size,  # 16KB batches
            'linger_ms': linger_ms,    # Wait 10ms for batching
            'compression_type': 'snappy',  # Fast compression
            'acks': 'all',  # Wait for all replicas
            'retries': 5,
            'retry_backoff_ms': 100,
            'buffer_memory': 33554432,  # 32MB buffer
            'max_block_ms': 10000,  # 10 second timeout
            'request_timeout_ms': 30000,
            'delivery_timeout_ms': 120000
        }
        
        # Topics for different event types
        self.topics = {
            'mumbai_trains': 'mumbai-local-trains',
            'upi_transactions': 'india-upi-transactions', 
            'ecommerce_orders': 'india-ecommerce-orders',
            'stock_market': 'india-stock-market',
            'weather_data': 'mumbai-weather-realtime'
        }
        
        # Mumbai-specific data for realistic events
        self.mumbai_data = {
            'train_routes': ['Western', 'Central', 'Harbour', 'Trans-Harbour'],
            'western_stations': ['Churchgate', 'Marine Lines', 'Charni Road', 'Grant Road', 
                               'Mumbai Central', 'Mahalaxmi', 'Lower Parel', 'Prabhadevi',
                               'Dadar', 'Matunga Road', 'Mahim', 'Bandra', 'Khar Road',
                               'Santacruz', 'Vile Parle', 'Andheri', 'Jogeshwari', 'Ram Mandir',
                               'Goregaon', 'Malad', 'Kandivali', 'Borivali', 'Dahisar', 'Virar'],
            'central_stations': ['CST', 'Masjid', 'Sandhurst Road', 'Dockyard Road', 'Reay Road',
                               'Cotton Green', 'Sewri', 'Wadala Road', 'Guru Tegh Bahadur Nagar',
                               'Chunabhatti', 'Kurla', 'Vidyavihar', 'Ghatkopar', 'Vikhroli',
                               'Kanjurmarg', 'Bhandup', 'Nahur', 'Mulund', 'Thane', 'Kalyan'],
            'upi_banks': ['HDFC', 'SBI', 'ICICI', 'Axis', 'Kotak', 'PNB', 'BOB', 'Canara'],
            'merchant_categories': ['Grocery', 'Food & Dining', 'Fuel', 'Shopping', 'Entertainment',
                                  'Travel', 'Bills & Utilities', 'Health', 'Education'],
            'mumbai_areas': ['Andheri', 'Bandra', 'Borivali', 'Dadar', 'Ghatkopar', 'Kurla',
                           'Malad', 'Mulund', 'Powai', 'Thane', 'Vashi', 'Worli'],
            'ecommerce_categories': ['Electronics', 'Fashion', 'Home & Kitchen', 'Books',
                                   'Sports', 'Beauty', 'Groceries', 'Mobile & Accessories']
        }
        
        # Producer instance
        self.producer = None
        
        # Statistics
        self.stats = {
            'total_messages': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'average_latency_ms': 0,
            'messages_per_second': 0,
            'bytes_sent': 0
        }
        
        # Thread pool for parallel sending
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def _json_serializer(self, data: Dict) -> bytes:
        \"\"\"JSON serializer with optimized performance\"\"\"
        return json.dumps(data, separators=(',', ':')).encode('utf-8')
    
    def _string_serializer(self, data: str) -> bytes:
        \"\"\"String serializer\"\"\"
        return data.encode('utf-8')
    
    def start_producer(self):
        \"\"\"Kafka producer start karo\"\"\"
        logger.info(\"🚀 Starting Mumbai Kafka Producer\")
        
        try:
            self.producer = KafkaProducer(**self.producer_config)
            self.running = True
            logger.info(f\"✅ Connected to Kafka: {self.bootstrap_servers}\")
            
            # Test connectivity
            metadata = self.producer.bootstrap_connected()
            logger.info(f\"📡 Kafka cluster metadata: {len(self.producer.cluster.brokers())} brokers\")
            
        except Exception as e:
            logger.error(f\"❌ Failed to start producer: {e}\")
            raise
    
    def stop_producer(self):
        \"\"\"Producer gracefully stop karo\"\"\"
        logger.info(\"🛑 Stopping Mumbai Kafka Producer\")
        self.running = False
        
        if self.producer:
            # Flush pending messages
            self.producer.flush(timeout=10)
            self.producer.close()
            
        if self.executor:
            self.executor.shutdown(wait=True)
            
        logger.info(\"✅ Producer stopped successfully\")
    
    def generate_train_event(self) -> MumbaiTrainEvent:
        \"\"\"Mumbai local train event generate karo\"\"\"
        route = random.choice(self.mumbai_data['train_routes'])
        
        if route == 'Western':
            stations = self.mumbai_data['western_stations']
        elif route == 'Central':
            stations = self.mumbai_data['central_stations']
        else:
            stations = self.mumbai_data['western_stations']  # Default
        
        from_station = random.choice(stations[:-1])
        to_station = random.choice(stations[stations.index(from_station)+1:])
        
        # Rush hour simulation
        current_hour = datetime.now().hour
        if 7 <= current_hour <= 10 or 17 <= current_hour <= 21:
            passenger_count = random.randint(800, 1200)  # Rush hour
            delay_minutes = random.randint(2, 15)
        else:
            passenger_count = random.randint(200, 600)   # Normal hours
            delay_minutes = random.randint(0, 5)
        
        departure_time = datetime.now(timezone.utc)
        arrival_time = departure_time + timedelta(minutes=random.randint(5, 30))
        
        return MumbaiTrainEvent(
            train_id=f\"MT_{route[:3].upper()}_{random.randint(1000, 9999)}\",
            route=route,
            station_from=from_station,
            station_to=to_station,
            departure_time=departure_time.isoformat(),
            arrival_time=arrival_time.isoformat(),
            passenger_count=passenger_count,
            delay_minutes=delay_minutes,
            coach_count=random.choice([9, 12, 15]),
            event_timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=random.choice(['arrival', 'departure', 'delay', 'on_time'])
        )
    
    def generate_upi_transaction(self) -> UPITransactionEvent:
        \"\"\"UPI transaction event generate karo\"\"\"
        amount = random.uniform(10, 50000)  # ₹10 to ₹50,000
        
        # Amount-based merchant category
        if amount < 100:
            category = random.choice(['Fuel', 'Food & Dining', 'Bills & Utilities'])
        elif amount < 1000:
            category = random.choice(['Grocery', 'Food & Dining', 'Shopping'])
        else:
            category = random.choice(['Shopping', 'Electronics', 'Travel'])
        
        # Bank distribution - realistic Indian scenario
        bank_weights = {'HDFC': 0.25, 'SBI': 0.20, 'ICICI': 0.15, 'Axis': 0.12, 
                       'Kotak': 0.10, 'PNB': 0.08, 'BOB': 0.06, 'Canara': 0.04}
        bank = random.choices(list(bank_weights.keys()), weights=list(bank_weights.values()))[0]
        
        # Success rate simulation
        success_rate = 0.97  # 97% success rate in India
        status = 'success' if random.random() < success_rate else random.choice(['failed', 'pending'])
        
        return UPITransactionEvent(
            transaction_id=f\"UPI_{uuid.uuid4().hex[:12].upper()}\",
            payer_vpa=f\"user{random.randint(1000, 9999)}@{bank.lower()}\",
            payee_vpa=f\"merchant{random.randint(100, 999)}@paytm\",
            amount=round(amount, 2),
            currency=\"INR\",
            merchant_category=category,
            location=random.choice(self.mumbai_data['mumbai_areas']),
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            bank_code=bank
        )
    
    def generate_ecommerce_order(self) -> EcommerceOrderEvent:
        \"\"\"E-commerce order event generate karo\"\"\"
        platform = random.choice(['Flipkart', 'Amazon', 'Myntra', 'Nykaa', 'BigBasket'])
        category = random.choice(self.mumbai_data['ecommerce_categories'])
        
        # Category-based order value
        if category == 'Electronics':
            order_value = random.uniform(5000, 100000)
        elif category == 'Fashion':
            order_value = random.uniform(500, 15000)
        elif category == 'Groceries':
            order_value = random.uniform(200, 5000)
        else:
            order_value = random.uniform(300, 10000)
        
        # Payment method distribution
        payment_methods = {
            'UPI': 0.40, 'Card': 0.30, 'COD': 0.20, 'Wallet': 0.10
        }
        payment_method = random.choices(list(payment_methods.keys()), 
                                      weights=list(payment_methods.values()))[0]
        
        return EcommerceOrderEvent(
            order_id=f\"{platform[:3].upper()}_{uuid.uuid4().hex[:10].upper()}\",
            customer_id=hashlib.sha256(f\"customer_{random.randint(10000, 99999)}\".encode()).hexdigest()[:16],
            product_category=category,
            order_value=round(order_value, 2),
            payment_method=payment_method,
            delivery_city=random.choice(self.mumbai_data['mumbai_areas']),
            warehouse_location=random.choice(['Mumbai', 'Pune', 'Nashik', 'Aurangabad']),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=random.choice(['placed', 'confirmed', 'shipped', 'delivered']),
            platform=platform
        )
    
    async def send_event_async(self, topic: str, key: str, event: Dict) -> bool:
        \"\"\"Single event async send karo\"\"\"
        try:
            start_time = time.time()
            
            # Send with callback
            future = self.producer.send(
                topic=topic,
                key=key,
                value=event,
                partition=None  # Let Kafka decide based on key
            )
            
            # Wait for acknowledgment
            record_metadata = future.get(timeout=10)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats['successful_sends'] += 1
            self.stats['total_messages'] += 1
            self.stats['bytes_sent'] += len(json.dumps(event))
            
            # Update average latency
            current_avg = self.stats['average_latency_ms']
            total_successful = self.stats['successful_sends']
            self.stats['average_latency_ms'] = (
                (current_avg * (total_successful - 1) + latency_ms) / total_successful
            )
            
            logger.debug(f\"✅ Event sent to {topic}:{record_metadata.partition}:{record_metadata.offset}\")
            return True
            
        except KafkaError as e:
            logger.error(f\"❌ Kafka error sending to {topic}: {e}\")
            self.stats['failed_sends'] += 1
            self.stats['total_messages'] += 1
            return False
        except Exception as e:
            logger.error(f\"❌ Unexpected error sending to {topic}: {e}\")
            self.stats['failed_sends'] += 1
            self.stats['total_messages'] += 1
            return False
    
    async def start_train_stream(self, events_per_second: int = 10):
        \"\"\"Mumbai train events stream start karo\"\"\"
        logger.info(f\"🚂 Starting train events stream: {events_per_second} events/sec\")
        
        interval = 1.0 / events_per_second
        
        while self.running:
            try:
                # Generate train event
                train_event = self.generate_train_event()
                event_dict = asdict(train_event)
                
                # Send to Kafka
                await self.send_event_async(
                    topic=self.topics['mumbai_trains'],
                    key=train_event.train_id,
                    event=event_dict
                )
                
                # Rate limiting
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f\"❌ Error in train stream: {e}\")
                await asyncio.sleep(1)
    
    async def start_upi_stream(self, events_per_second: int = 100):
        \"\"\"UPI transactions stream start karo\"\"\"
        logger.info(f\"💳 Starting UPI events stream: {events_per_second} events/sec\")
        
        interval = 1.0 / events_per_second
        
        while self.running:
            try:
                # Generate UPI transaction
                upi_event = self.generate_upi_transaction()
                event_dict = asdict(upi_event)
                
                # Send to Kafka
                await self.send_event_async(
                    topic=self.topics['upi_transactions'],
                    key=upi_event.transaction_id,
                    event=event_dict
                )
                
                # Rate limiting
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f\"❌ Error in UPI stream: {e}\")
                await asyncio.sleep(1)
    
    async def start_ecommerce_stream(self, events_per_second: int = 50):
        \"\"\"E-commerce orders stream start karo\"\"\"
        logger.info(f\"🛒 Starting e-commerce events stream: {events_per_second} events/sec\")
        
        interval = 1.0 / events_per_second
        
        while self.running:
            try:
                # Generate e-commerce order
                order_event = self.generate_ecommerce_order()
                event_dict = asdict(order_event)
                
                # Send to Kafka
                await self.send_event_async(
                    topic=self.topics['ecommerce_orders'],
                    key=order_event.order_id,
                    event=event_dict
                )
                
                # Rate limiting
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f\"❌ Error in e-commerce stream: {e}\")
                await asyncio.sleep(1)
    
    async def start_all_streams(self, 
                              train_rate: int = 10,
                              upi_rate: int = 100, 
                              ecommerce_rate: int = 50):
        \"\"\"Sabhi streams parallel mein start karo\"\"\"
        logger.info(\"🌊 Starting all Mumbai data streams\")
        
        # Create tasks for all streams
        tasks = [
            asyncio.create_task(self.start_train_stream(train_rate)),
            asyncio.create_task(self.start_upi_stream(upi_rate)),
            asyncio.create_task(self.start_ecommerce_stream(ecommerce_rate))
        ]
        
        # Start statistics reporter
        stats_task = asyncio.create_task(self.report_statistics())
        tasks.append(stats_task)
        
        try:
            # Wait for all tasks
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info(\"🛑 Stopping all streams...\")
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
            
            # Wait for cleanup
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def report_statistics(self, interval: int = 30):
        \"\"\"Statistics report karo har interval pe\"\"\"
        last_total = 0
        
        while self.running:
            await asyncio.sleep(interval)
            
            current_total = self.stats['total_messages']
            messages_in_interval = current_total - last_total
            self.stats['messages_per_second'] = messages_in_interval / interval
            
            logger.info(
                f\"📊 Stats - Total: {current_total}, \"
                f\"Success: {self.stats['successful_sends']}, \"
                f\"Failed: {self.stats['failed_sends']}, \"
                f\"Rate: {self.stats['messages_per_second']:.1f} msg/sec, \"
                f\"Avg Latency: {self.stats['average_latency_ms']:.2f}ms, \"
                f\"Bytes: {self.stats['bytes_sent']:,}\"
            )
            
            last_total = current_total
    
    def get_statistics(self) -> Dict:
        \"\"\"Current statistics return karo\"\"\"
        total = self.stats['total_messages']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'success_rate': (self.stats['successful_sends'] / total) * 100,
            'failure_rate': (self.stats['failed_sends'] / total) * 100,
            'average_message_size_bytes': self.stats['bytes_sent'] / total if total > 0 else 0
        }

def signal_handler(signum, frame):
    \"\"\"Graceful shutdown on signal\"\"\"
    logger.info(\"🛑 Received shutdown signal\")
    sys.exit(0)

async def demo_mumbai_kafka_producer():
    \"\"\"
    Mumbai Kafka Producer ka demo
    \"\"\"
    print(\"🚂 === Mumbai Kafka Producer Demo === 🚂\")
    
    # Initialize producer
    producer = MumbaiKafkaProducer(
        bootstrap_servers=['localhost:9092'],
        batch_size=32768,  # 32KB batches for demo
        linger_ms=50       # 50ms batching delay
    )
    
    try:
        # Start producer
        producer.start_producer()
        
        print(\"\
📡 Producer started successfully!\")
        print(\"🚂 Generating Mumbai local train events...\")
        print(\"💳 Generating UPI transaction events...\")
        print(\"🛒 Generating e-commerce order events...\")
        print(\"\
⏹️ Press Ctrl+C to stop\
\")
        
        # Start all streams
        await producer.start_all_streams(
            train_rate=5,      # 5 train events per second
            upi_rate=20,       # 20 UPI transactions per second  
            ecommerce_rate=10  # 10 e-commerce orders per second
        )
        
    except KeyboardInterrupt:
        print(\"\
🛑 Stopping producer...\")
    except Exception as e:
        logger.error(f\"❌ Demo error: {e}\")
    finally:
        # Cleanup
        producer.stop_producer()
        
        # Final statistics
        final_stats = producer.get_statistics()
        print(\"\
📊 === Final Statistics === 📊\")
        print(f\"   Total messages: {final_stats['total_messages']:,}\")
        print(f\"   Successful: {final_stats['successful_sends']:,}\")
        print(f\"   Failed: {final_stats['failed_sends']:,}\")
        print(f\"   Success rate: {final_stats.get('success_rate', 0):.2f}%\")
        print(f\"   Average latency: {final_stats['average_latency_ms']:.2f}ms\")
        print(f\"   Average message size: {final_stats.get('average_message_size_bytes', 0):.0f} bytes\")
        print(f\"   Total data sent: {final_stats['bytes_sent']:,} bytes\")

def calculate_kafka_costs():
    \"\"\"
    Mumbai Kafka infrastructure costs calculate karo
    \"\"\"
    print(\"\
💰 === Mumbai Kafka Cost Analysis === 💰\")
    
    # AWS MSK costs (Mumbai region)
    costs = {
        'kafka_cluster_3_brokers': 15000,  # INR per month
        'data_transfer_100gb': 500,        # INR per month
        'storage_1tb_ssd': 2000,          # INR per month
        'zookeeper_3_nodes': 3000,        # INR per month
        'monitoring_cloudwatch': 1000,    # INR per month
        'backup_storage_500gb': 800,      # INR per month
        'network_load_balancer': 1200     # INR per month
    }
    
    monthly_total = sum(costs.values())
    annual_total = monthly_total * 12
    
    print(f\"📊 Cost Breakdown (INR/month):\")
    for service, cost in costs.items():
        print(f\"   {service.replace('_', ' ').title()}: ₹{cost:,}\")
    
    print(f\"\
💸 Total Monthly Cost: ₹{monthly_total:,}\")
    print(f\"💸 Total Annual Cost: ₹{annual_total:,}\")
    
    # Per message cost calculation
    messages_per_month = 30 * 24 * 3600 * (5 + 20 + 10)  # 35 msg/sec for 30 days
    cost_per_million_messages = (monthly_total / messages_per_month) * 1000000
    
    print(f\"\
📈 Performance Metrics:\")
    print(f\"   Messages per month: {messages_per_month:,}\")
    print(f\"   Cost per million messages: ₹{cost_per_million_messages:.2f}\")
    print(f\"   Cost per event: ₹{monthly_total/messages_per_month:.6f}\")
    
    # Scaling scenarios
    print(f\"\
🚀 Scaling Scenarios:\")
    scaling_factors = [1, 5, 10, 50, 100]
    
    for factor in scaling_factors:
        scaled_cost = monthly_total * factor
        scaled_throughput = 35 * factor  # messages per second
        
        print(f\"   {factor}x scale: ₹{scaled_cost:,}/month, {scaled_throughput:,} msg/sec\")

if __name__ == \"__main__\":
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Add required import
    import hashlib
    
    print(\"🇮🇳 Mumbai Real-time Data Producer Starting...\")
    
    # Run demo
    try:
        asyncio.run(demo_mumbai_kafka_producer())
    except KeyboardInterrupt:
        print(\"\
👋 Demo stopped by user\")
    
    # Show cost analysis
    calculate_kafka_costs()
    
    print(\"\
📚 Next Steps:\")
    print(\"   1. Setup Kafka cluster: docker-compose up -d\")
    print(\"   2. Create topics: kafka-topics --create --topic mumbai-local-trains\")
    print(\"   3. Run consumer: python 02_kafka_realtime_consumer.py\")
    print(\"   4. Monitor with Kafka UI: http://localhost:8080\")
    
    print(\"\
🌐 Resources:\")
    print(\"   • Kafka Documentation: https://kafka.apache.org/documentation/\")
    print(\"   • Confluent Platform: https://docs.confluent.io/\")
    print(\"   • Mumbai Train API: https://opendata.gov.in/\")