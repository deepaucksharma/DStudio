#!/usr/bin/env python3
"""
Episode 22: Streaming Architectures - Kafka Producer/Consumer for UPI Transactions
Author: Code Developer Agent
Description: Production-ready Kafka implementation for UPI transaction processing

Kafka है real-time data streaming का backbone
UPI transactions का volume बहुत high है, इसलिए streaming critical है
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

# Mock Kafka (replace with real kafka-python in production)
class MockKafkaProducer:
    """Mock Kafka Producer for demonstration"""
    
    def __init__(self, bootstrap_servers: str, **configs):
        self.bootstrap_servers = bootstrap_servers
        self.configs = configs
        self.message_queue = []
        print(f"🚀 Kafka Producer initialized: {bootstrap_servers}")
    
    def send(self, topic: str, key: bytes, value: bytes, **kwargs):
        """Send message to Kafka topic"""
        message = {
            'topic': topic,
            'key': key.decode('utf-8') if key else None,
            'value': value.decode('utf-8'),
            'timestamp': datetime.now().isoformat(),
            'partition': hash(key) % 3 if key else 0  # Mock partitioning
        }
        self.message_queue.append(message)
        print(f"📤 Sent to {topic}: {key.decode('utf-8') if key else 'None'}")
        return message
    
    def flush(self):
        """Flush pending messages"""
        print(f"💾 Flushed {len(self.message_queue)} messages")
        return True

class MockKafkaConsumer:
    """Mock Kafka Consumer for demonstration"""
    
    def __init__(self, topics: List[str], bootstrap_servers: str, group_id: str, **configs):
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.configs = configs
        self.messages = []
        print(f"📥 Kafka Consumer initialized: {group_id} for topics {topics}")
    
    def poll(self, timeout_ms: int = 1000):
        """Poll for messages"""
        # Simulate message polling
        time.sleep(timeout_ms / 1000.0)
        return self.messages[:5]  # Return up to 5 messages
    
    def commit(self):
        """Commit offset"""
        print("✅ Offset committed")
    
    def close(self):
        """Close consumer"""
        print("🔚 Consumer closed")

# UPI Transaction Models
class TransactionType(Enum):
    P2P = "person_to_person"
    P2M = "person_to_merchant"
    BILL_PAYMENT = "bill_payment"
    RECHARGE = "mobile_recharge"
    ECOMMERCE = "ecommerce"

class TransactionStatus(Enum):
    INITIATED = "initiated"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class UPITransaction:
    """UPI Transaction model"""
    transaction_id: str
    sender_vpa: str
    receiver_vpa: str
    amount: float
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    initiated_at: datetime
    completed_at: Optional[datetime]
    merchant_id: Optional[str]
    purpose: str
    reference_id: str
    bank_ref_number: Optional[str]
    metadata: Dict

@dataclass
class FraudAlert:
    """Fraud detection alert"""
    alert_id: str
    transaction_id: str
    risk_score: float
    alert_type: str
    reason: str
    created_at: datetime
    requires_manual_review: bool

# UPI Transaction Producer
class UPITransactionProducer:
    """High-throughput UPI transaction producer"""
    
    def __init__(self, bootstrap_servers: str):
        self.producer = MockKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=lambda x: x.encode('utf-8') if x else None,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks='all',  # Wait for all replicas
            retries=3,
            batch_size=16384,  # 16KB batches
            linger_ms=10,  # Wait 10ms for batching
            compression_type='gzip'
        )
        self.transaction_topic = "upi-transactions"
        self.fraud_alerts_topic = "fraud-alerts"
        self.metrics_topic = "transaction-metrics"
    
    async def produce_transaction(self, transaction: UPITransaction):
        """Produce UPI transaction to Kafka"""
        try:
            # Create message key for partitioning (based on sender VPA)
            key = transaction.sender_vpa
            
            # Serialize transaction
            value = asdict(transaction)
            value['initiated_at'] = transaction.initiated_at.isoformat()
            if transaction.completed_at:
                value['completed_at'] = transaction.completed_at.isoformat()
            value['transaction_type'] = transaction.transaction_type.value
            value['status'] = transaction.status.value
            
            # Send to Kafka
            future = self.producer.send(
                topic=self.transaction_topic,
                key=key.encode('utf-8'),
                value=json.dumps(value).encode('utf-8')
            )
            
            print(f"💳 UPI Transaction produced: {transaction.transaction_id} | ₹{transaction.amount}")
            
            # Produce metrics event
            await self._produce_metrics(transaction)
            
            return future
            
        except Exception as e:
            print(f"❌ Failed to produce transaction {transaction.transaction_id}: {e}")
            raise
    
    async def produce_fraud_alert(self, alert: FraudAlert):
        """Produce fraud alert to Kafka"""
        try:
            key = alert.transaction_id
            value = asdict(alert)
            value['created_at'] = alert.created_at.isoformat()
            
            future = self.producer.send(
                topic=self.fraud_alerts_topic,
                key=key.encode('utf-8'),
                value=json.dumps(value).encode('utf-8')
            )
            
            print(f"🚨 Fraud Alert produced: {alert.alert_id} | Risk: {alert.risk_score}")
            return future
            
        except Exception as e:
            print(f"❌ Failed to produce fraud alert {alert.alert_id}: {e}")
            raise
    
    async def _produce_metrics(self, transaction: UPITransaction):
        """Produce transaction metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'transaction_count': 1,
            'amount': transaction.amount,
            'transaction_type': transaction.transaction_type.value,
            'status': transaction.status.value,
            'bank': transaction.sender_vpa.split('@')[1] if '@' in transaction.sender_vpa else 'unknown'
        }
        
        self.producer.send(
            topic=self.metrics_topic,
            key=f"metrics-{datetime.now().hour}".encode('utf-8'),
            value=json.dumps(metrics).encode('utf-8')
        )
    
    def flush_and_close(self):
        """Flush and close producer"""
        self.producer.flush()
        print("📤 Producer flushed and closed")

# UPI Transaction Consumer
class UPITransactionConsumer:
    """High-throughput UPI transaction consumer"""
    
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.consumer = MockKafkaConsumer(
            topics=['upi-transactions'],
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=False,  # Manual commit for reliability
            max_poll_records=500,  # Process in batches
            fetch_min_bytes=1024,  # Wait for 1KB minimum
            fetch_max_wait_ms=500  # Max wait 500ms
        )
        self.processed_count = 0
        self.error_count = 0
        self.running = False
    
    async def start_consuming(self, processor_func):
        """Start consuming UPI transactions"""
        self.running = True
        print(f"📥 Starting UPI transaction consumer...")
        
        try:
            while self.running:
                # Poll for messages
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                if not message_batch:
                    continue
                
                # Process batch
                await self._process_batch(message_batch, processor_func)
                
                # Commit offset after successful processing
                self.consumer.commit()
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Consumer error: {e}")
            raise
        finally:
            self.consumer.close()
    
    async def _process_batch(self, messages: List[Dict], processor_func):
        """Process batch of messages"""
        tasks = []
        
        for message in messages:
            try:
                # Parse transaction
                transaction_data = json.loads(message['value'])
                transaction = self._deserialize_transaction(transaction_data)
                
                # Create processing task
                task = asyncio.create_task(processor_func(transaction))
                tasks.append(task)
                
            except Exception as e:
                print(f"❌ Failed to parse message: {e}")
                self.error_count += 1
        
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            self.processed_count += len(tasks)
            
            print(f"✅ Processed batch of {len(tasks)} transactions. Total: {self.processed_count}")
    
    def _deserialize_transaction(self, data: Dict) -> UPITransaction:
        """Deserialize transaction from JSON"""
        return UPITransaction(
            transaction_id=data['transaction_id'],
            sender_vpa=data['sender_vpa'],
            receiver_vpa=data['receiver_vpa'],
            amount=data['amount'],
            currency=data['currency'],
            transaction_type=TransactionType(data['transaction_type']),
            status=TransactionStatus(data['status']),
            initiated_at=datetime.fromisoformat(data['initiated_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            merchant_id=data.get('merchant_id'),
            purpose=data['purpose'],
            reference_id=data['reference_id'],
            bank_ref_number=data.get('bank_ref_number'),
            metadata=data['metadata']
        )
    
    def stop(self):
        """Stop consuming"""
        self.running = False
        print("🛑 Consumer stop requested")

# Fraud Detection Consumer
class FraudDetectionConsumer:
    """Real-time fraud detection consumer"""
    
    def __init__(self, bootstrap_servers: str):
        self.consumer = MockKafkaConsumer(
            topics=['upi-transactions'],
            bootstrap_servers=bootstrap_servers,
            group_id='fraud-detection-service',
            auto_offset_reset='latest'  # Only new transactions
        )
        self.producer = UPITransactionProducer(bootstrap_servers)
        self.suspicious_patterns = set()
        self.user_transaction_history = {}
    
    async def start_fraud_monitoring(self):
        """Start real-time fraud monitoring"""
        print("🔍 Starting fraud detection monitoring...")
        
        try:
            while True:
                messages = self.consumer.poll(timeout_ms=1000)
                
                for message in messages:
                    try:
                        transaction_data = json.loads(message['value'])
                        transaction = self._deserialize_transaction(transaction_data)
                        
                        # Run fraud detection
                        await self._analyze_transaction(transaction)
                        
                    except Exception as e:
                        print(f"❌ Fraud detection error: {e}")
                
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("🛑 Fraud detection stopped")
        finally:
            self.consumer.close()
    
    async def _analyze_transaction(self, transaction: UPITransaction):
        """Analyze transaction for fraud patterns"""
        risk_score = 0.0
        risk_factors = []
        
        # 1. Amount-based risk
        if transaction.amount > 50000:  # High amount
            risk_score += 30
            risk_factors.append("high_amount")
        
        # 2. Velocity check
        user_history = self.user_transaction_history.get(transaction.sender_vpa, [])
        recent_transactions = [
            t for t in user_history 
            if (datetime.now() - t['timestamp']).seconds < 300  # Last 5 minutes
        ]
        
        if len(recent_transactions) > 5:  # More than 5 transactions in 5 minutes
            risk_score += 40
            risk_factors.append("high_velocity")
        
        # 3. Unusual time pattern
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 23:  # Late night transactions
            risk_score += 20
            risk_factors.append("unusual_time")
        
        # 4. New receiver check
        receiver_history = [t for t in user_history if t.get('receiver_vpa') == transaction.receiver_vpa]
        if not receiver_history and transaction.amount > 10000:  # First time high amount
            risk_score += 25
            risk_factors.append("new_receiver_high_amount")
        
        # Update user history
        user_history.append({
            'timestamp': datetime.now(),
            'amount': transaction.amount,
            'receiver_vpa': transaction.receiver_vpa,
            'transaction_id': transaction.transaction_id
        })
        
        # Keep only last 50 transactions
        self.user_transaction_history[transaction.sender_vpa] = user_history[-50:]
        
        # Generate alert if risk score is high
        if risk_score >= 50:
            alert = FraudAlert(
                alert_id=f"ALERT_{uuid.uuid4().hex[:8].upper()}",
                transaction_id=transaction.transaction_id,
                risk_score=risk_score,
                alert_type="SUSPICIOUS_TRANSACTION",
                reason=", ".join(risk_factors),
                created_at=datetime.now(),
                requires_manual_review=risk_score >= 70
            )
            
            await self.producer.produce_fraud_alert(alert)
    
    def _deserialize_transaction(self, data: Dict) -> UPITransaction:
        """Deserialize transaction from JSON"""
        return UPITransaction(
            transaction_id=data['transaction_id'],
            sender_vpa=data['sender_vpa'],
            receiver_vpa=data['receiver_vpa'],
            amount=data['amount'],
            currency=data['currency'],
            transaction_type=TransactionType(data['transaction_type']),
            status=TransactionStatus(data['status']),
            initiated_at=datetime.fromisoformat(data['initiated_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            merchant_id=data.get('merchant_id'),
            purpose=data['purpose'],
            reference_id=data['reference_id'],
            bank_ref_number=data.get('bank_ref_number'),
            metadata=data['metadata']
        )

# Transaction Generator for Demo
class UPITransactionGenerator:
    """Generate realistic UPI transactions for demo"""
    
    def __init__(self):
        self.merchants = [
            "amazon@paytm", "flipkart@phonepe", "zomato@gpay",
            "swiggy@paytm", "uber@phonepe", "ola@gpay",
            "bigbasket@paytm", "myntra@phonepe", "reliance@gpay"
        ]
        
        self.users = [
            "rajesh.sharma@paytm", "priya.patel@phonepe", "amit.kumar@gpay",
            "sunita.singh@paytm", "rohit.gupta@phonepe", "kavya.reddy@gpay",
            "manoj.jain@paytm", "deepika.nair@phonepe", "vikas.yadav@gpay"
        ]
    
    def generate_transaction(self) -> UPITransaction:
        """Generate a realistic UPI transaction"""
        import random
        
        # Random transaction type
        tx_type = random.choice(list(TransactionType))
        
        # Choose sender and receiver based on type
        if tx_type == TransactionType.P2M:
            sender = random.choice(self.users)
            receiver = random.choice(self.merchants)
            amount = round(random.uniform(100, 5000), 2)
            purpose = random.choice(["Food", "Shopping", "Cab", "Grocery", "Fashion"])
        else:
            sender = random.choice(self.users)
            receiver = random.choice([u for u in self.users if u != sender])
            amount = round(random.uniform(500, 25000), 2)
            purpose = random.choice(["Transfer", "Repayment", "Gift", "Expense sharing"])
        
        return UPITransaction(
            transaction_id=f"UPI{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}",
            sender_vpa=sender,
            receiver_vpa=receiver,
            amount=amount,
            currency="INR",
            transaction_type=tx_type,
            status=TransactionStatus.INITIATED,
            initiated_at=datetime.now(),
            completed_at=None,
            merchant_id=receiver.split('@')[0] if tx_type == TransactionType.P2M else None,
            purpose=purpose,
            reference_id=f"REF{uuid.uuid4().hex[:6].upper()}",
            bank_ref_number=None,
            metadata={
                "device_id": f"DEV{uuid.uuid4().hex[:8]}",
                "app_version": "1.2.3",
                "location": random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"])
            }
        )

# Transaction Processing Service
async def process_upi_transaction(transaction: UPITransaction):
    """Process UPI transaction (mock business logic)"""
    try:
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Mock validation and processing
        if transaction.amount > 100000:
            print(f"⚠️ High amount transaction requires approval: {transaction.transaction_id}")
        
        # Update transaction status
        success_rate = 0.95  # 95% success rate
        import random
        
        if random.random() < success_rate:
            transaction.status = TransactionStatus.SUCCESS
            transaction.completed_at = datetime.now()
            transaction.bank_ref_number = f"BNK{uuid.uuid4().hex[:8].upper()}"
            print(f"✅ Transaction successful: {transaction.transaction_id} | ₹{transaction.amount}")
        else:
            transaction.status = TransactionStatus.FAILED
            print(f"❌ Transaction failed: {transaction.transaction_id}")
        
    except Exception as e:
        print(f"❌ Processing error for {transaction.transaction_id}: {e}")
        transaction.status = TransactionStatus.FAILED

# Demo Function
async def demonstrate_upi_kafka_streaming():
    """Demonstrate UPI transaction streaming with Kafka"""
    print("💳 UPI Kafka Streaming Demo")
    print("=" * 50)
    
    bootstrap_servers = "localhost:9092"
    
    # Setup producer and consumers
    producer = UPITransactionProducer(bootstrap_servers)
    transaction_consumer = UPITransactionConsumer(bootstrap_servers, "upi-processing-service")
    fraud_consumer = FraudDetectionConsumer(bootstrap_servers)
    generator = UPITransactionGenerator()
    
    try:
        # Start fraud detection in background
        fraud_task = asyncio.create_task(fraud_consumer.start_fraud_monitoring())
        
        # Start transaction consumer in background
        consumer_task = asyncio.create_task(
            transaction_consumer.start_consuming(process_upi_transaction)
        )
        
        # Generate and produce transactions
        print("\n📤 Generating UPI transactions...")
        
        for i in range(20):  # Generate 20 transactions
            transaction = generator.generate_transaction()
            await producer.produce_transaction(transaction)
            
            # Small delay between transactions
            await asyncio.sleep(0.2)
        
        # Let consumers process for a while
        print("\n⏳ Processing transactions...")
        await asyncio.sleep(5)
        
        # Stop consumers
        transaction_consumer.stop()
        await asyncio.sleep(1)
        
        # Cancel tasks
        fraud_task.cancel()
        consumer_task.cancel()
        
        # Cleanup
        producer.flush_and_close()
        
        print(f"\n📊 Processing Summary:")
        print(f"  Transactions Processed: {transaction_consumer.processed_count}")
        print(f"  Processing Errors: {transaction_consumer.error_count}")
        
        print("\n✅ UPI Kafka Streaming Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    """
    Key Kafka Streaming Benefits for UPI:
    1. High Throughput: Millions of transactions per second
    2. Fault Tolerance: Replication और durability
    3. Real-time Processing: Immediate fraud detection
    4. Scalability: Horizontal scaling with partitions
    5. Decoupling: Services independently consume streams
    6. Event Replay: Historical transaction processing
    7. Multiple Consumers: Different services processing same data
    """
    asyncio.run(demonstrate_upi_kafka_streaming())