#!/usr/bin/env python3
"""
Dead Letter Queue (DLQ) Implementation
उदाहरण: Swiggy order notifications के लिए DLQ system

Setup:
pip install redis asyncio

Indian Context: Swiggy app मein जब notifications fail होते हैं
(network issues, customer phone off, etc.), उन्हें DLQ मein store करके
बाद में retry करना पड़ता है:

- Order confirmation SMS
- Push notifications 
- Email receipts
- Delivery partner alerts
- Restaurant notifications

DLQ benefits:
- No message loss
- Automatic retry with backoff
- Manual intervention for persistent failures
- Monitoring and alerting
"""

import asyncio
import json
import logging
import redis
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
import random

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageStatus(Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DLQ = "dlq"
    EXPIRED = "expired"

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_DELAY = "fixed_delay"
    LINEAR_BACKOFF = "linear_backoff"

@dataclass
class Message:
    """Event message structure"""
    message_id: str
    topic: str
    payload: Dict[str, Any]
    headers: Dict[str, str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = None
    last_attempted_at: str = None
    status: MessageStatus = MessageStatus.PENDING
    error_details: List[str] = None
    correlation_id: str = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.headers is None:
            self.headers = {}
        if self.error_details is None:
            self.error_details = []
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())

class DeadLetterQueue:
    """
    Dead Letter Queue implementation with Redis
    Mumbai local train ki breakdown ki tarah - 
    jab normal service nahi chal sakti, alternate arrangement karna padta hai
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.dlq_key = "swiggy:dlq"
        self.processing_key = "swiggy:processing"
        self.retry_schedule_key = "swiggy:retry_schedule"
        
        # Test Redis connection
        try:
            self.redis_client.ping()
            logger.info("✅ Connected to Redis")
        except redis.ConnectionError:
            logger.error("❌ Failed to connect to Redis")
            raise
    
    async def enqueue_message(self, message: Message, delay_seconds: int = 0):
        """
        Message को queue mein add karna
        Delay के साथ - scheduled retry के लिए
        """
        message_json = json.dumps(asdict(message))
        
        if delay_seconds > 0:
            # Scheduled retry के लिए sorted set use karna
            execute_at = time.time() + delay_seconds
            self.redis_client.zadd(self.retry_schedule_key, {message_json: execute_at})
            
            logger.info(f"📅 Message scheduled for retry in {delay_seconds}s: {message.message_id}")
        else:
            # Immediate processing के लिए list use karna
            self.redis_client.lpush(self.dlq_key, message_json)
            
            logger.info(f"📥 Message enqueued: {message.message_id}")
    
    async def dequeue_message(self) -> Optional[Message]:
        """
        Queue से message retrieve karna
        FIFO order mein
        """
        # First check scheduled messages
        now = time.time()
        scheduled_messages = self.redis_client.zrangebyscore(
            self.retry_schedule_key, 0, now, start=0, num=1, withscores=True
        )
        
        if scheduled_messages:
            message_json, score = scheduled_messages[0]
            # Remove from scheduled set
            self.redis_client.zrem(self.retry_schedule_key, message_json)
            
            logger.info("⏰ Retrieved scheduled message")
            return Message(**json.loads(message_json))
        
        # Then check immediate queue
        message_json = self.redis_client.rpop(self.dlq_key)
        if message_json:
            return Message(**json.loads(message_json))
        
        return None
    
    async def move_to_dlq(self, message: Message, error: str):
        """
        Message को DLQ mein move karna
        Permanent failure के बाद
        """
        message.status = MessageStatus.DLQ
        message.error_details.append(f"{datetime.now().isoformat()}: {error}")
        
        # DLQ mein permanent storage
        dlq_storage_key = f"swiggy:dlq:permanent:{message.topic}"
        message_json = json.dumps(asdict(message))
        
        self.redis_client.lpush(dlq_storage_key, message_json)
        
        # TTL set karna - 30 days retention
        self.redis_client.expire(dlq_storage_key, 30 * 24 * 60 * 60)
        
        logger.error(f"💀 Message moved to DLQ: {message.message_id} - {error}")
    
    def get_dlq_messages(self, topic: str, limit: int = 10) -> List[Message]:
        """DLQ messages retrieve karna debugging के लिए"""
        dlq_storage_key = f"swiggy:dlq:permanent:{topic}"
        message_jsons = self.redis_client.lrange(dlq_storage_key, 0, limit - 1)
        
        messages = []
        for message_json in message_jsons:
            try:
                message = Message(**json.loads(message_json))
                messages.append(message)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in DLQ: {message_json}")
        
        return messages
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Queue statistics"""
        immediate_count = self.redis_client.llen(self.dlq_key)
        scheduled_count = self.redis_client.zcard(self.retry_schedule_key)
        processing_count = self.redis_client.scard(self.processing_key)
        
        return {
            'immediate_queue': immediate_count,
            'scheduled_retries': scheduled_count,
            'currently_processing': processing_count
        }

class MessageProcessor:
    """
    Message processing logic with retry mechanisms
    Mumbai traffic jam ki tarah - रुक जाना, फिर try करना
    """
    
    def __init__(self, dlq: DeadLetterQueue):
        self.dlq = dlq
        self.retry_strategies = {
            RetryStrategy.EXPONENTIAL_BACKOFF: self._exponential_backoff,
            RetryStrategy.FIXED_DELAY: self._fixed_delay,
            RetryStrategy.LINEAR_BACKOFF: self._linear_backoff
        }
    
    async def process_message(self, message: Message, handler: Callable) -> bool:
        """
        Message को process karna with error handling
        """
        message.status = MessageStatus.PROCESSING
        message.last_attempted_at = datetime.now().isoformat()
        
        try:
            logger.info(f"⚙️ Processing message: {message.message_id}")
            
            # Handler execute karna
            result = await handler(message)
            
            if result:
                message.status = MessageStatus.COMPLETED
                logger.info(f"✅ Message processed successfully: {message.message_id}")
                return True
            else:
                raise Exception("Handler returned False")
                
        except Exception as e:
            error_msg = str(e)
            message.error_details.append(f"{datetime.now().isoformat()}: {error_msg}")
            message.retry_count += 1
            message.status = MessageStatus.FAILED
            
            logger.error(f"❌ Message processing failed: {message.message_id} - {error_msg}")
            
            # Retry logic
            if message.retry_count <= message.max_retries:
                await self._schedule_retry(message)
                return False
            else:
                # Max retries exceeded - move to DLQ
                await self.dlq.move_to_dlq(message, f"Max retries exceeded: {error_msg}")
                return False
    
    async def _schedule_retry(self, message: Message):
        """Retry schedule karna with backoff strategy"""
        delay = self._exponential_backoff(message.retry_count)
        
        logger.info(f"🔄 Scheduling retry {message.retry_count}/{message.max_retries} "
                   f"for message {message.message_id} in {delay}s")
        
        await self.dlq.enqueue_message(message, delay)
    
    def _exponential_backoff(self, retry_count: int) -> int:
        """Exponential backoff: 2^retry_count seconds"""
        return min(300, 2 ** retry_count)  # Max 5 minutes
    
    def _fixed_delay(self, retry_count: int) -> int:
        """Fixed delay: 30 seconds"""
        return 30
    
    def _linear_backoff(self, retry_count: int) -> int:
        """Linear backoff: retry_count * 30 seconds"""
        return min(300, retry_count * 30)  # Max 5 minutes

# Swiggy notification services

class SMSNotificationService:
    """SMS notification service"""
    
    def __init__(self):
        self.service_name = "SMS Notification Service"
        self.failure_rate = 0.3  # 30% failure rate for demo
    
    async def send_sms(self, message: Message) -> bool:
        """SMS send karna"""
        payload = message.payload
        phone_number = payload.get('phone_number')
        sms_content = payload.get('content')
        
        logger.info(f"📱 {self.service_name}: Sending SMS to {phone_number}")
        logger.info(f"   📝 Content: {sms_content[:50]}...")
        
        # Simulation delay
        await asyncio.sleep(0.2)
        
        # Random failure simulation
        if random.random() < self.failure_rate:
            failures = [
                "Network timeout",
                "Invalid phone number",
                "SMS gateway down",
                "Rate limit exceeded",
                "Customer opted out"
            ]
            raise Exception(random.choice(failures))
        
        logger.info(f"✅ SMS sent successfully to {phone_number}")
        return True

class PushNotificationService:
    """Push notification service"""
    
    def __init__(self):
        self.service_name = "Push Notification Service"
        self.failure_rate = 0.25  # 25% failure rate
    
    async def send_push(self, message: Message) -> bool:
        """Push notification send karna"""
        payload = message.payload
        device_id = payload.get('device_id')
        title = payload.get('title')
        body = payload.get('body')
        
        logger.info(f"📲 {self.service_name}: Sending push to device {device_id}")
        logger.info(f"   📰 Title: {title}")
        
        # Simulation delay
        await asyncio.sleep(0.3)
        
        # Random failure simulation
        if random.random() < self.failure_rate:
            failures = [
                "Device not reachable",
                "FCM service unavailable",
                "Invalid device token",
                "App uninstalled",
                "Network connectivity issues"
            ]
            raise Exception(random.choice(failures))
        
        logger.info(f"✅ Push notification sent to device {device_id}")
        return True

class EmailNotificationService:
    """Email notification service"""
    
    def __init__(self):
        self.service_name = "Email Notification Service"
        self.failure_rate = 0.15  # 15% failure rate
    
    async def send_email(self, message: Message) -> bool:
        """Email send karna"""
        payload = message.payload
        email_address = payload.get('email')
        subject = payload.get('subject')
        
        logger.info(f"📧 {self.service_name}: Sending email to {email_address}")
        logger.info(f"   📋 Subject: {subject}")
        
        # Simulation delay
        await asyncio.sleep(0.5)
        
        # Random failure simulation
        if random.random() < self.failure_rate:
            failures = [
                "SMTP server timeout",
                "Invalid email address",
                "Email service rate limited",
                "Temporary blacklist",
                "Content blocked by spam filter"
            ]
            raise Exception(random.choice(failures))
        
        logger.info(f"✅ Email sent successfully to {email_address}")
        return True

class SwiggyNotificationWorker:
    """
    Notification worker - DLQ messages को process karta है
    Mumbai dabba delivery system की तरह - reliable delivery
    """
    
    def __init__(self, dlq: DeadLetterQueue):
        self.dlq = dlq
        self.processor = MessageProcessor(dlq)
        self.services = {
            'sms': SMSNotificationService(),
            'push': PushNotificationService(),
            'email': EmailNotificationService()
        }
        self.running = False
    
    async def start(self):
        """Worker start karna"""
        self.running = True
        logger.info("🏃 Swiggy notification worker started")
        
        while self.running:
            try:
                # Message retrieve karna
                message = await self.dlq.dequeue_message()
                
                if message:
                    # Service route karna based on topic
                    service_type = message.topic.split('.')[-1]  # e.g., 'order.sms' -> 'sms'
                    
                    if service_type in self.services:
                        service = self.services[service_type]
                        
                        # Service-specific handler call karna
                        if service_type == 'sms':
                            await self.processor.process_message(message, service.send_sms)
                        elif service_type == 'push':
                            await self.processor.process_message(message, service.send_push)
                        elif service_type == 'email':
                            await self.processor.process_message(message, service.send_email)
                    else:
                        logger.error(f"❌ Unknown service type: {service_type}")
                        await self.dlq.move_to_dlq(message, f"Unknown service type: {service_type}")
                else:
                    # No messages - wait briefly
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
                await asyncio.sleep(5)  # Error recovery delay
    
    def stop(self):
        """Worker stop karna"""
        self.running = False
        logger.info("🛑 Swiggy notification worker stopped")

async def swiggy_dlq_demo():
    """Swiggy DLQ system demo"""
    print("🍽️ Swiggy Dead Letter Queue Demo")
    print("=" * 50)
    print("📋 Make sure Redis is running on localhost:6379")
    print()
    
    # DLQ system initialize karna
    dlq = DeadLetterQueue()
    
    # Sample order data
    order_data = {
        'order_id': f"SWG_{uuid.uuid4().hex[:8].upper()}",
        'customer_name': "Rahul Sharma",
        'restaurant_name': "Domino's Pizza",
        'total_amount': 450.0,
        'delivery_time': "30 minutes"
    }
    
    print(f"🛍️ Order: {order_data['order_id']}")
    print(f"🍕 Restaurant: {order_data['restaurant_name']}")
    print(f"💰 Amount: ₹{order_data['total_amount']}")
    print()
    
    # Different notification messages create karna
    notifications = [
        # SMS notifications
        Message(
            message_id=str(uuid.uuid4()),
            topic="order.sms",
            payload={
                'phone_number': '+91-9876543210',
                'content': f"Your order {order_data['order_id']} from {order_data['restaurant_name']} "
                          f"has been confirmed! Amount: ₹{order_data['total_amount']}. "
                          f"Delivery in {order_data['delivery_time']}."
            },
            max_retries=3
        ),
        
        # Push notifications
        Message(
            message_id=str(uuid.uuid4()),
            topic="order.push",
            payload={
                'device_id': 'FCM_TOKEN_123ABC',
                'title': f"Order Confirmed - {order_data['restaurant_name']}",
                'body': f"Your order worth ₹{order_data['total_amount']} will be delivered in {order_data['delivery_time']}"
            },
            max_retries=2
        ),
        
        # Email notifications
        Message(
            message_id=str(uuid.uuid4()),
            topic="order.email",
            payload={
                'email': 'rahul.sharma@email.com',
                'subject': f"Order Receipt - {order_data['order_id']}",
                'body': f"Thank you for ordering from {order_data['restaurant_name']}!"
            },
            max_retries=2
        ),
        
        # Restaurant SMS
        Message(
            message_id=str(uuid.uuid4()),
            topic="restaurant.sms",
            payload={
                'phone_number': '+91-9123456789',
                'content': f"New order {order_data['order_id']} received! "
                          f"Customer: {order_data['customer_name']}, Amount: ₹{order_data['total_amount']}"
            },
            max_retries=3
        ),
        
        # Delivery partner push
        Message(
            message_id=str(uuid.uuid4()),
            topic="delivery.push",
            payload={
                'device_id': 'DELIVERY_PARTNER_456',
                'title': 'New Delivery Assignment',
                'body': f"Pick up from {order_data['restaurant_name']} - Order {order_data['order_id']}"
            },
            max_retries=2
        )
    ]
    
    # Messages को queue mein add karna
    print("📥 Enqueuing notification messages...")
    for notification in notifications:
        await dlq.enqueue_message(notification)
        print(f"   ✅ Queued: {notification.topic} - {notification.message_id}")
    
    print()
    
    # Queue stats check karna
    stats = dlq.get_queue_stats()
    print(f"📊 Queue Stats:")
    print(f"   📥 Immediate Queue: {stats['immediate_queue']} messages")
    print(f"   ⏰ Scheduled Retries: {stats['scheduled_retries']} messages")
    print(f"   ⚙️ Currently Processing: {stats['currently_processing']} messages")
    print()
    
    # Worker start karna
    worker = SwiggyNotificationWorker(dlq)
    worker_task = asyncio.create_task(worker.start())
    
    print("🏃 Starting notification worker...")
    print("⏳ Processing messages (this may take a while due to failures and retries)...")
    
    # Processing को monitor karna
    for i in range(60):  # 60 seconds max
        await asyncio.sleep(1)
        
        stats = dlq.get_queue_stats()
        if stats['immediate_queue'] == 0 and stats['scheduled_retries'] == 0:
            # All messages processed or moved to DLQ
            break
        
        if i % 10 == 0:  # Every 10 seconds
            print(f"   📊 Progress: {stats['immediate_queue']} immediate, "
                  f"{stats['scheduled_retries']} scheduled")
    
    # Worker stop karna
    worker.stop()
    worker_task.cancel()
    
    print("\n📊 Final Results:")
    
    # Final stats
    final_stats = dlq.get_queue_stats()
    print(f"   📥 Remaining in Queue: {final_stats['immediate_queue']}")
    print(f"   ⏰ Scheduled Retries: {final_stats['scheduled_retries']}")
    
    # DLQ analysis
    print("\n💀 Dead Letter Queue Analysis:")
    topics = ['order.sms', 'order.push', 'order.email', 'restaurant.sms', 'delivery.push']
    
    total_dlq_messages = 0
    for topic in topics:
        dlq_messages = dlq.get_dlq_messages(topic, 10)
        if dlq_messages:
            total_dlq_messages += len(dlq_messages)
            print(f"   🔸 {topic}: {len(dlq_messages)} messages in DLQ")
            
            # Show error details for first message
            first_msg = dlq_messages[0]
            print(f"      📝 Sample Error: {first_msg.error_details[-1] if first_msg.error_details else 'N/A'}")
    
    if total_dlq_messages == 0:
        print("   ✅ No messages in DLQ - all processed successfully!")
    else:
        print(f"   ⚠️ Total {total_dlq_messages} messages require manual intervention")
    
    print("\n🎯 Key Benefits Demonstrated:")
    print("   ✅ No message loss despite service failures")
    print("   ✅ Automatic retry with exponential backoff")
    print("   ✅ Failed messages isolated in DLQ")
    print("   ✅ Full audit trail with error details")
    print("   ✅ Queue monitoring and statistics")

async def dlq_recovery_demo():
    """DLQ recovery demo - manual intervention"""
    print("\n" + "="*50)
    print("🔧 DLQ Recovery Demo - Manual Message Processing")
    print("="*50)
    
    dlq = DeadLetterQueue()
    
    # Check DLQ contents
    topics = ['order.sms', 'order.push', 'order.email']
    recovered_count = 0
    
    for topic in topics:
        dlq_messages = dlq.get_dlq_messages(topic, 5)
        
        if dlq_messages:
            print(f"\n📋 Processing DLQ messages for {topic}:")
            
            for msg in dlq_messages[:2]:  # Process first 2 messages
                print(f"   🔍 Message: {msg.message_id}")
                print(f"   🔢 Retry Count: {msg.retry_count}")
                print(f"   ⚠️ Last Error: {msg.error_details[-1] if msg.error_details else 'N/A'}")
                
                # Simulate manual fix (e.g., fixing phone number, updating device token)
                print(f"   🔧 Applying manual fix...")
                
                # Reset retry count for reprocessing
                msg.retry_count = 0
                msg.max_retries = 1
                msg.status = MessageStatus.PENDING
                
                # Re-enqueue for processing
                await dlq.enqueue_message(msg)
                
                print(f"   ✅ Message re-queued for processing")
                recovered_count += 1
    
    if recovered_count > 0:
        print(f"\n🎉 Successfully recovered {recovered_count} messages from DLQ")
        print("💡 In production: Use admin dashboard for DLQ management")
    else:
        print("\n📝 No messages found in DLQ for recovery")

if __name__ == "__main__":
    asyncio.run(swiggy_dlq_demo())
    asyncio.run(dlq_recovery_demo())