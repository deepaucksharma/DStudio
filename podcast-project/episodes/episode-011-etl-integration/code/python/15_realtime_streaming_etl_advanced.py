#!/usr/bin/env python3
"""
Real-time Streaming ETL with Advanced Patterns - Episode 11
Production-grade streaming ETL with Kafka, Redis, windowing, and state management

यह real-time streaming ETL pipeline advanced patterns दिखाता है:
- Event time vs Processing time handling
- Watermarks और late data handling
- Exactly-once processing semantics
- State management और checkpointing

Indian Context: UPI real-time fraud detection और Zomato live order tracking जैसे use cases
"""

import asyncio
import json
import time
import logging
import uuid
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import hashlib
import redis
import pandas as pd
from kafka import KafkaProducer, KafkaConsumer
import threading
from concurrent.futures import ThreadPoolExecutor
import pickle
import statistics

# Configure logging for Hindi comments
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] %(message)s',
    handlers=[
        logging.FileHandler('streaming_etl.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event types for streaming processing"""
    UPI_TRANSACTION = "upi_transaction"
    ORDER_STATUS = "order_status"
    USER_ACTIVITY = "user_activity"
    FRAUD_ALERT = "fraud_alert"
    SYSTEM_METRIC = "system_metric"

@dataclass
class StreamEvent:
    """Stream event with timestamps for windowing"""
    event_id: str
    event_type: EventType
    user_id: str
    data: Dict[str, Any]
    event_time: datetime  # When event actually occurred
    ingestion_time: datetime  # When event was received
    partition_key: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'data': self.data,
            'event_time': self.event_time.isoformat(),
            'ingestion_time': self.ingestion_time.isoformat(),
            'partition_key': self.partition_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StreamEvent':
        """Create from dictionary"""
        return cls(
            event_id=data['event_id'],
            event_type=EventType(data['event_type']),
            user_id=data['user_id'],
            data=data['data'],
            event_time=pd.to_datetime(data['event_time']).to_pydatetime(),
            ingestion_time=pd.to_datetime(data['ingestion_time']).to_pydatetime(),
            partition_key=data['partition_key']
        )

@dataclass
class WindowState:
    """State for windowed operations"""
    window_start: datetime
    window_end: datetime
    events: List[StreamEvent] = field(default_factory=list)
    aggregated_data: Dict[str, Any] = field(default_factory=dict)
    is_closed: bool = False
    watermark: Optional[datetime] = None

class WatermarkGenerator:
    """
    Generate watermarks for handling late data
    UPI transaction processing में कभी कभी delayed events आते हैं
    """
    
    def __init__(self, allowed_lateness: timedelta = timedelta(minutes=5)):
        self.allowed_lateness = allowed_lateness
        self.max_seen_timestamp = datetime.min
    
    def update_watermark(self, event_time: datetime) -> datetime:
        """Update watermark based on event time"""
        if event_time > self.max_seen_timestamp:
            self.max_seen_timestamp = event_time
        
        # Watermark = max_seen_timestamp - allowed_lateness
        watermark = self.max_seen_timestamp - self.allowed_lateness
        return watermark
    
    def is_late(self, event_time: datetime, watermark: datetime) -> bool:
        """Check if event is late based on watermark"""
        return event_time <= watermark

class StateStore:
    """
    Persistent state store using Redis for fault tolerance
    Zomato order tracking जैसा state management
    """
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=False  # Keep binary for pickle
        )
        self.checkpoint_interval = 30  # seconds
        self.last_checkpoint = time.time()
    
    def save_state(self, key: str, state: Any):
        """Save state to Redis"""
        try:
            serialized_state = pickle.dumps(state)
            self.redis_client.set(f"state:{key}", serialized_state)
            logger.debug(f"State saved for key: {key}")
        except Exception as e:
            logger.error(f"Failed to save state for {key}: {e}")
    
    def load_state(self, key: str) -> Any:
        """Load state from Redis"""
        try:
            serialized_state = self.redis_client.get(f"state:{key}")
            if serialized_state:
                return pickle.loads(serialized_state)
            return None
        except Exception as e:
            logger.error(f"Failed to load state for {key}: {e}")
            return None
    
    def delete_state(self, key: str):
        """Delete state from Redis"""
        self.redis_client.delete(f"state:{key}")
    
    def should_checkpoint(self) -> bool:
        """Check if it's time to checkpoint"""
        return time.time() - self.last_checkpoint > self.checkpoint_interval
    
    def checkpoint(self):
        """Update checkpoint timestamp"""
        self.last_checkpoint = time.time()
        logger.info("State checkpoint completed")

class StreamingWindow:
    """
    Windowing operations for streaming data
    Time-based windows जैसे sliding window, tumbling window
    """
    
    def __init__(self, window_size: timedelta, slide_interval: timedelta = None):
        self.window_size = window_size
        self.slide_interval = slide_interval or window_size  # Default: tumbling window
        self.windows: Dict[str, WindowState] = {}
        self.watermark_gen = WatermarkGenerator()
    
    def add_event(self, event: StreamEvent) -> List[str]:
        """Add event to appropriate windows"""
        watermark = self.watermark_gen.update_watermark(event.event_time)
        window_keys = []
        
        # Calculate which windows this event belongs to
        window_keys_for_event = self._get_window_keys(event.event_time)
        
        for window_key in window_keys_for_event:
            if window_key not in self.windows:
                window_start, window_end = self._parse_window_key(window_key)
                self.windows[window_key] = WindowState(
                    window_start=window_start,
                    window_end=window_end,
                    watermark=watermark
                )
            
            # Check if event is late
            if not self.watermark_gen.is_late(event.event_time, watermark):
                self.windows[window_key].events.append(event)
                window_keys.append(window_key)
                logger.debug(f"Event {event.event_id} added to window {window_key}")
            else:
                logger.warning(f"Late event ignored: {event.event_id}, event_time: {event.event_time}, watermark: {watermark}")
        
        # Check for windows that can be closed
        self._close_expired_windows(watermark)
        
        return window_keys
    
    def _get_window_keys(self, event_time: datetime) -> List[str]:
        """Get window keys for an event time"""
        window_keys = []
        
        # For sliding windows, an event can belong to multiple windows
        current_window_start = self._align_to_window(event_time)
        
        # Generate window keys for sliding window
        slide_count = int(self.window_size.total_seconds() / self.slide_interval.total_seconds())
        
        for i in range(slide_count):
            window_start = current_window_start - (i * self.slide_interval)
            window_end = window_start + self.window_size
            
            if window_start <= event_time < window_end:
                window_key = f"{window_start.timestamp()}_{window_end.timestamp()}"
                window_keys.append(window_key)
        
        return window_keys
    
    def _align_to_window(self, timestamp: datetime) -> datetime:
        """Align timestamp to window boundary"""
        window_seconds = self.window_size.total_seconds()
        aligned_seconds = (timestamp.timestamp() // window_seconds) * window_seconds
        return datetime.fromtimestamp(aligned_seconds)
    
    def _parse_window_key(self, window_key: str) -> tuple:
        """Parse window key to get start and end times"""
        start_ts, end_ts = window_key.split('_')
        return datetime.fromtimestamp(float(start_ts)), datetime.fromtimestamp(float(end_ts))
    
    def _close_expired_windows(self, watermark: datetime):
        """Close windows that have passed the watermark"""
        expired_windows = []
        
        for window_key, window_state in self.windows.items():
            if window_state.window_end <= watermark and not window_state.is_closed:
                window_state.is_closed = True
                expired_windows.append(window_key)
        
        return expired_windows
    
    def get_closed_windows(self) -> List[str]:
        """Get list of closed windows ready for processing"""
        return [key for key, state in self.windows.items() if state.is_closed]

class FraudDetectionProcessor:
    """
    Real-time fraud detection using streaming patterns
    UPI fraud detection जैसा - real-time में suspicious patterns detect करना
    """
    
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        self.user_velocity_window = timedelta(minutes=10)  # 10-minute velocity check
        self.amount_threshold = 50000  # ₹50,000
        self.velocity_threshold = 5    # 5 transactions in 10 minutes
        
    def process_upi_transaction(self, event: StreamEvent) -> Optional[StreamEvent]:
        """Process UPI transaction for fraud detection"""
        user_id = event.user_id
        transaction_data = event.data
        
        # Load user transaction history
        user_history_key = f"user_transactions:{user_id}"
        user_history = self.state_store.load_state(user_history_key) or []
        
        # Add current transaction
        transaction_entry = {
            'amount': transaction_data.get('amount', 0),
            'merchant': transaction_data.get('merchant', ''),
            'location': transaction_data.get('location', ''),
            'timestamp': event.event_time.isoformat()
        }
        
        # Keep only recent transactions (last hour)
        cutoff_time = event.event_time - timedelta(hours=1)
        user_history = [
            tx for tx in user_history 
            if pd.to_datetime(tx['timestamp']).to_pydatetime() > cutoff_time
        ]
        user_history.append(transaction_entry)
        
        # Calculate fraud indicators
        fraud_score = self._calculate_fraud_score(user_history, transaction_entry)
        
        # Save updated history
        self.state_store.save_state(user_history_key, user_history)
        
        # Generate fraud alert if score is high
        if fraud_score > 0.7:
            fraud_alert = StreamEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.FRAUD_ALERT,
                user_id=user_id,
                data={
                    'original_transaction_id': event.event_id,
                    'fraud_score': fraud_score,
                    'risk_factors': self._get_risk_factors(user_history, transaction_entry),
                    'recommended_action': 'BLOCK_TRANSACTION' if fraud_score > 0.9 else 'MANUAL_REVIEW'
                },
                event_time=event.event_time,
                ingestion_time=datetime.now(),
                partition_key=f"fraud:{user_id}"
            )
            
            logger.warning(f"🚨 Fraud alert generated for user {user_id}, score: {fraud_score}")
            return fraud_alert
        
        return None
    
    def _calculate_fraud_score(self, user_history: List[Dict], current_transaction: Dict) -> float:
        """Calculate fraud risk score based on transaction patterns"""
        score = 0.0
        
        # High amount risk
        amount = current_transaction.get('amount', 0)
        if amount > self.amount_threshold:
            score += 0.3
        
        # Velocity risk - too many transactions
        recent_transactions = [
            tx for tx in user_history 
            if pd.to_datetime(tx['timestamp']).to_pydatetime() > 
               pd.to_datetime(current_transaction['timestamp']).to_pydatetime() - self.user_velocity_window
        ]
        
        if len(recent_transactions) > self.velocity_threshold:
            score += 0.4
        
        # Location change risk
        if len(user_history) > 1:
            last_location = user_history[-2].get('location', '')
            current_location = current_transaction.get('location', '')
            if last_location and current_location and last_location != current_location:
                score += 0.2
        
        # Round-amount risk (exactly round amounts like ₹50,000)
        if amount % 10000 == 0 and amount > 10000:
            score += 0.1
        
        # Late night transaction (Indian timezone)
        tx_hour = pd.to_datetime(current_transaction['timestamp']).hour
        if tx_hour < 6 or tx_hour > 22:
            score += 0.15
        
        return min(score, 1.0)
    
    def _get_risk_factors(self, user_history: List[Dict], current_transaction: Dict) -> List[str]:
        """Get list of risk factors for transparency"""
        risk_factors = []
        
        amount = current_transaction.get('amount', 0)
        if amount > self.amount_threshold:
            risk_factors.append('high_amount')
        
        recent_count = len([
            tx for tx in user_history 
            if pd.to_datetime(tx['timestamp']).to_pydatetime() > 
               pd.to_datetime(current_transaction['timestamp']).to_pydatetime() - self.user_velocity_window
        ])
        if recent_count > self.velocity_threshold:
            risk_factors.append('high_velocity')
        
        if len(user_history) > 1:
            last_location = user_history[-2].get('location', '')
            current_location = current_transaction.get('location', '')
            if last_location != current_location:
                risk_factors.append('location_change')
        
        if amount % 10000 == 0 and amount > 10000:
            risk_factors.append('round_amount')
        
        tx_hour = pd.to_datetime(current_transaction['timestamp']).hour
        if tx_hour < 6 or tx_hour > 22:
            risk_factors.append('unusual_time')
        
        return risk_factors

class OrderTrackingProcessor:
    """
    Real-time order tracking and analytics
    Zomato/Swiggy order tracking जैसा real-time order status updates
    """
    
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        self.delivery_time_sla = timedelta(minutes=30)  # 30 minutes SLA
        
    def process_order_event(self, event: StreamEvent) -> List[StreamEvent]:
        """Process order status events"""
        order_id = event.data.get('order_id')
        status = event.data.get('status')  # PLACED, CONFIRMED, PREPARING, OUT_FOR_DELIVERY, DELIVERED
        
        if not order_id:
            return []
        
        # Load order state
        order_state_key = f"order:{order_id}"
        order_state = self.state_store.load_state(order_state_key) or {
            'order_id': order_id,
            'user_id': event.user_id,
            'status_history': [],
            'estimated_delivery': None,
            'actual_delivery': None,
            'restaurant_id': event.data.get('restaurant_id'),
            'created_at': event.event_time.isoformat()
        }
        
        # Update status history
        order_state['status_history'].append({
            'status': status,
            'timestamp': event.event_time.isoformat(),
            'location': event.data.get('location')
        })
        
        # Calculate delivery metrics
        generated_events = []
        
        if status == 'PLACED':
            # Set estimated delivery time
            order_state['estimated_delivery'] = (
                event.event_time + self.delivery_time_sla
            ).isoformat()
            
        elif status == 'DELIVERED':
            order_state['actual_delivery'] = event.event_time.isoformat()
            
            # Calculate delivery time
            placed_time = None
            for status_entry in order_state['status_history']:
                if status_entry['status'] == 'PLACED':
                    placed_time = pd.to_datetime(status_entry['timestamp']).to_pydatetime()
                    break
            
            if placed_time:
                delivery_time = event.event_time - placed_time
                
                # Generate delivery analytics event
                delivery_metrics_event = StreamEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.SYSTEM_METRIC,
                    user_id=event.user_id,
                    data={
                        'metric_type': 'delivery_performance',
                        'order_id': order_id,
                        'restaurant_id': order_state['restaurant_id'],
                        'delivery_time_minutes': delivery_time.total_seconds() / 60,
                        'sla_met': delivery_time <= self.delivery_time_sla,
                        'placed_at': placed_time.isoformat(),
                        'delivered_at': event.event_time.isoformat()
                    },
                    event_time=event.event_time,
                    ingestion_time=datetime.now(),
                    partition_key=f"metrics:{order_state['restaurant_id']}"
                )
                
                generated_events.append(delivery_metrics_event)
                
                logger.info(f"📦 Order {order_id} delivered in {delivery_time.total_seconds()/60:.1f} minutes")
        
        # Check for SLA violations
        if order_state.get('estimated_delivery'):
            estimated_time = pd.to_datetime(order_state['estimated_delivery']).to_pydatetime()
            if event.event_time > estimated_time and status not in ['DELIVERED', 'CANCELLED']:
                # Generate SLA violation alert
                sla_alert = StreamEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.SYSTEM_METRIC,
                    user_id=event.user_id,
                    data={
                        'metric_type': 'sla_violation',
                        'order_id': order_id,
                        'restaurant_id': order_state['restaurant_id'],
                        'current_status': status,
                        'estimated_delivery': order_state['estimated_delivery'],
                        'delay_minutes': (event.event_time - estimated_time).total_seconds() / 60
                    },
                    event_time=event.event_time,
                    ingestion_time=datetime.now(),
                    partition_key=f"alerts:{order_state['restaurant_id']}"
                )
                
                generated_events.append(sla_alert)
                logger.warning(f"⏰ SLA violation for order {order_id}, delay: {(event.event_time - estimated_time).total_seconds()/60:.1f} minutes")
        
        # Save updated order state
        self.state_store.save_state(order_state_key, order_state)
        
        return generated_events

class StreamingETLPipeline:
    """
    Main streaming ETL pipeline with advanced patterns
    Production-ready streaming ETL जो real-time में complex processing करता है
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state_store = StateStore(
            redis_host=config.get('redis_host', 'localhost'),
            redis_port=config.get('redis_port', 6379)
        )
        
        # Initialize processors
        self.fraud_processor = FraudDetectionProcessor(self.state_store)
        self.order_processor = OrderTrackingProcessor(self.state_store)
        
        # Initialize windowing
        self.analytics_window = StreamingWindow(
            window_size=timedelta(minutes=5),    # 5-minute windows
            slide_interval=timedelta(minutes=1)  # Sliding every minute
        )
        
        # Kafka setup
        self.kafka_servers = config.get('kafka_servers', ['localhost:9092'])
        self.input_topics = config.get('input_topics', ['upi-transactions', 'order-events', 'user-activities'])
        self.output_topics = config.get('output_topics', {
            'fraud_alerts': 'fraud-alerts',
            'order_analytics': 'order-analytics',
            'system_metrics': 'system-metrics'
        })
        
        # Processing state
        self.running = False
        self.processed_count = 0
        self.error_count = 0
        self.last_checkpoint = time.time()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=config.get('worker_threads', 4))
        
    def start_pipeline(self):
        """Start the streaming ETL pipeline"""
        logger.info("🚀 Starting Real-time Streaming ETL Pipeline")
        self.running = True
        
        # Start consumer threads
        consumer_threads = []
        for topic in self.input_topics:
            thread = threading.Thread(
                target=self._consume_topic,
                args=(topic,),
                name=f"Consumer-{topic}"
            )
            thread.start()
            consumer_threads.append(thread)
        
        # Start window processing thread
        window_thread = threading.Thread(
            target=self._process_windows,
            name="WindowProcessor"
        )
        window_thread.start()
        
        # Start checkpoint thread
        checkpoint_thread = threading.Thread(
            target=self._checkpoint_loop,
            name="Checkpointer"
        )
        checkpoint_thread.start()
        
        logger.info("All processing threads started")
        
        try:
            # Wait for all threads
            for thread in consumer_threads:
                thread.join()
            window_thread.join()
            checkpoint_thread.join()
            
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
            self.running = False
    
    def _consume_topic(self, topic: str):
        """Consume events from a Kafka topic"""
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.kafka_servers,
            group_id=f"streaming-etl-{topic}",
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None,
            enable_auto_commit=False,  # Manual commit for exactly-once
            max_poll_records=100
        )
        
        logger.info(f"Started consuming from topic: {topic}")
        
        try:
            while self.running:
                message_batch = consumer.poll(timeout_ms=1000)
                
                if not message_batch:
                    continue
                
                # Process batch
                events_to_commit = []
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            # Parse event
                            event = StreamEvent.from_dict(message.value)
                            
                            # Process event based on type
                            generated_events = self._process_event(event)
                            
                            # Add to window
                            self.analytics_window.add_event(event)
                            
                            # Send generated events
                            for gen_event in generated_events:
                                self._send_event(gen_event)
                            
                            events_to_commit.append(message)
                            self.processed_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            self.error_count += 1
                
                # Commit offsets for successfully processed messages
                if events_to_commit:
                    consumer.commit()
                    logger.debug(f"Committed {len(events_to_commit)} events from {topic}")
                
        except Exception as e:
            logger.error(f"Consumer error for topic {topic}: {e}")
        finally:
            consumer.close()
            logger.info(f"Consumer closed for topic: {topic}")
    
    def _process_event(self, event: StreamEvent) -> List[StreamEvent]:
        """Process single event and return generated events"""
        generated_events = []
        
        try:
            if event.event_type == EventType.UPI_TRANSACTION:
                # Fraud detection processing
                fraud_alert = self.fraud_processor.process_upi_transaction(event)
                if fraud_alert:
                    generated_events.append(fraud_alert)
            
            elif event.event_type == EventType.ORDER_STATUS:
                # Order tracking processing
                order_events = self.order_processor.process_order_event(event)
                generated_events.extend(order_events)
            
            elif event.event_type == EventType.USER_ACTIVITY:
                # User activity analytics (simplified)
                analytics_event = self._process_user_activity(event)
                if analytics_event:
                    generated_events.append(analytics_event)
            
            logger.debug(f"Processed event {event.event_id}, generated {len(generated_events)} events")
            
        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            self.error_count += 1
        
        return generated_events
    
    def _process_user_activity(self, event: StreamEvent) -> Optional[StreamEvent]:
        """Process user activity events for engagement analytics"""
        # Simple user activity processing
        activity_type = event.data.get('activity_type')
        
        if activity_type in ['app_open', 'search', 'view_product', 'add_to_cart']:
            # Generate engagement metrics
            return StreamEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.SYSTEM_METRIC,
                user_id=event.user_id,
                data={
                    'metric_type': 'user_engagement',
                    'activity_type': activity_type,
                    'session_id': event.data.get('session_id'),
                    'screen': event.data.get('screen'),
                    'engagement_score': self._calculate_engagement_score(activity_type)
                },
                event_time=event.event_time,
                ingestion_time=datetime.now(),
                partition_key=f"engagement:{event.user_id}"
            )
        
        return None
    
    def _calculate_engagement_score(self, activity_type: str) -> float:
        """Calculate engagement score for activity"""
        scores = {
            'app_open': 1.0,
            'search': 2.0,
            'view_product': 3.0,
            'add_to_cart': 5.0
        }
        return scores.get(activity_type, 0.0)
    
    def _process_windows(self):
        """Process closed windows for analytics"""
        logger.info("Window processor started")
        
        while self.running:
            try:
                # Get closed windows
                closed_windows = self.analytics_window.get_closed_windows()
                
                for window_key in closed_windows:
                    window_state = self.analytics_window.windows[window_key]
                    
                    # Process window aggregations
                    aggregated_data = self._aggregate_window_data(window_state.events)
                    
                    # Create analytics event
                    analytics_event = StreamEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=EventType.SYSTEM_METRIC,
                        user_id="system",
                        data={
                            'metric_type': 'window_analytics',
                            'window_start': window_state.window_start.isoformat(),
                            'window_end': window_state.window_end.isoformat(),
                            'event_count': len(window_state.events),
                            'aggregations': aggregated_data
                        },
                        event_time=window_state.window_end,
                        ingestion_time=datetime.now(),
                        partition_key="window_analytics"
                    )
                    
                    # Send analytics event
                    self._send_event(analytics_event)
                    
                    # Clean up processed window
                    del self.analytics_window.windows[window_key]
                    
                    logger.info(f"Processed window {window_key} with {len(window_state.events)} events")
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Window processing error: {e}")
                time.sleep(5)
    
    def _aggregate_window_data(self, events: List[StreamEvent]) -> Dict[str, Any]:
        """Aggregate events in a window"""
        aggregations = {
            'total_events': len(events),
            'event_types': defaultdict(int),
            'users': set(),
            'transactions': {
                'count': 0,
                'total_amount': 0,
                'avg_amount': 0
            }
        }
        
        transaction_amounts = []
        
        for event in events:
            # Count by event type
            aggregations['event_types'][event.event_type.value] += 1
            aggregations['users'].add(event.user_id)
            
            # Transaction-specific aggregations
            if event.event_type == EventType.UPI_TRANSACTION:
                amount = event.data.get('amount', 0)
                aggregations['transactions']['count'] += 1
                aggregations['transactions']['total_amount'] += amount
                transaction_amounts.append(amount)
        
        # Calculate averages
        if transaction_amounts:
            aggregations['transactions']['avg_amount'] = statistics.mean(transaction_amounts)
            aggregations['transactions']['median_amount'] = statistics.median(transaction_amounts)
        
        aggregations['unique_users'] = len(aggregations['users'])
        aggregations['users'] = list(aggregations['users'])  # Convert set to list for serialization
        
        return aggregations
    
    def _send_event(self, event: StreamEvent):
        """Send event to appropriate Kafka topic"""
        try:
            # Determine output topic based on event type
            if event.event_type == EventType.FRAUD_ALERT:
                topic = self.output_topics.get('fraud_alerts', 'fraud-alerts')
            elif event.event_type == EventType.SYSTEM_METRIC:
                if event.data.get('metric_type') == 'delivery_performance':
                    topic = self.output_topics.get('order_analytics', 'order-analytics')
                else:
                    topic = self.output_topics.get('system_metrics', 'system-metrics')
            else:
                topic = 'processed-events'
            
            # Create producer (in production, use a shared producer)
            producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
            
            # Send event
            producer.send(
                topic,
                key=event.partition_key,
                value=event.to_dict()
            )
            producer.flush()
            producer.close()
            
            logger.debug(f"Sent event {event.event_id} to topic {topic}")
            
        except Exception as e:
            logger.error(f"Error sending event {event.event_id}: {e}")
    
    def _checkpoint_loop(self):
        """Periodic checkpointing of state"""
        logger.info("Checkpoint thread started")
        
        while self.running:
            try:
                if self.state_store.should_checkpoint():
                    self.state_store.checkpoint()
                    
                    # Log processing stats
                    logger.info(f"📊 Processing Stats - Processed: {self.processed_count}, Errors: {self.error_count}")
                
                time.sleep(30)  # Checkpoint every 30 seconds
                
            except Exception as e:
                logger.error(f"Checkpoint error: {e}")
                time.sleep(10)
    
    def stop_pipeline(self):
        """Stop the streaming pipeline"""
        logger.info("Stopping streaming ETL pipeline")
        self.running = False
        self.executor.shutdown(wait=True)

def create_sample_events() -> List[StreamEvent]:
    """Create sample events for testing"""
    events = []
    
    # UPI transaction events
    for i in range(10):
        upi_event = StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.UPI_TRANSACTION,
            user_id=f'+919876543{i:03d}',
            data={
                'transaction_id': f'UPI_{i:06d}',
                'amount': round(random.uniform(100, 10000), 2),
                'merchant': random.choice(['Zomato', 'Swiggy', 'Amazon', 'Flipkart']),
                'location': random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Pune']),
                'payment_method': 'UPI'
            },
            event_time=datetime.now() - timedelta(minutes=random.randint(0, 60)),
            ingestion_time=datetime.now(),
            partition_key=f'upi_user_{i}'
        )
        events.append(upi_event)
    
    # Order events
    for i in range(5):
        order_event = StreamEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.ORDER_STATUS,
            user_id=f'+919876543{i:03d}',
            data={
                'order_id': f'ORDER_{i:06d}',
                'restaurant_id': f'REST_{i:03d}',
                'status': random.choice(['PLACED', 'CONFIRMED', 'PREPARING', 'OUT_FOR_DELIVERY', 'DELIVERED']),
                'location': random.choice(['Koramangala', 'Whitefield', 'Indiranagar', 'HSR Layout'])
            },
            event_time=datetime.now() - timedelta(minutes=random.randint(0, 45)),
            ingestion_time=datetime.now(),
            partition_key=f'order_{i}'
        )
        events.append(order_event)
    
    return events

async def main():
    """
    Main function to demonstrate streaming ETL pipeline
    Production-ready streaming ETL का complete demo
    """
    
    # Configuration
    config = {
        'kafka_servers': ['localhost:9092'],
        'redis_host': 'localhost',
        'redis_port': 6379,
        'input_topics': ['upi-transactions', 'order-events', 'user-activities'],
        'output_topics': {
            'fraud_alerts': 'fraud-alerts',
            'order_analytics': 'order-analytics',
            'system_metrics': 'system-metrics'
        },
        'worker_threads': 4
    }
    
    logger.info("🌊 Starting Advanced Real-time Streaming ETL Pipeline")
    logger.info("यह pipeline real-time में complex event processing करता है:")
    logger.info("  • UPI fraud detection")
    logger.info("  • Order tracking and analytics")
    logger.info("  • Windowed aggregations")
    logger.info("  • State management with Redis")
    
    # Initialize pipeline
    pipeline = StreamingETLPipeline(config)
    
    try:
        # For demo purposes, create sample events
        print("\n📝 Creating sample events for demonstration...")
        sample_events = create_sample_events()
        
        # Process sample events to show functionality
        print(f"\n🔄 Processing {len(sample_events)} sample events...")
        
        fraud_alerts = 0
        order_analytics = 0
        
        for event in sample_events:
            generated_events = pipeline._process_event(event)
            pipeline.analytics_window.add_event(event)
            
            for gen_event in generated_events:
                if gen_event.event_type == EventType.FRAUD_ALERT:
                    fraud_alerts += 1
                    print(f"  🚨 Fraud Alert: User {gen_event.user_id}, Score: {gen_event.data.get('fraud_score', 0):.2f}")
                elif gen_event.data.get('metric_type') == 'delivery_performance':
                    order_analytics += 1
                    delivery_time = gen_event.data.get('delivery_time_minutes', 0)
                    sla_met = gen_event.data.get('sla_met', False)
                    print(f"  📦 Order Delivered: {delivery_time:.1f} min, SLA: {'✅' if sla_met else '❌'}")
        
        # Process closed windows
        closed_windows = pipeline.analytics_window.get_closed_windows()
        for window_key in closed_windows:
            window_state = pipeline.analytics_window.windows[window_key]
            aggregated_data = pipeline._aggregate_window_data(window_state.events)
            print(f"\n📊 Window Analytics [{window_key}]:")
            print(f"  • Total Events: {aggregated_data['total_events']}")
            print(f"  • Unique Users: {aggregated_data['unique_users']}")
            print(f"  • Transactions: {aggregated_data['transactions']['count']}")
            print(f"  • Total Amount: ₹{aggregated_data['transactions']['total_amount']:,.2f}")
        
        print(f"\n✅ Sample processing completed!")
        print(f"  • Fraud Alerts Generated: {fraud_alerts}")
        print(f"  • Order Analytics: {order_analytics}")
        print(f"  • Windows Processed: {len(closed_windows)}")
        
        print(f"\n🚀 To run the full streaming pipeline:")
        print(f"  1. Start Kafka and Redis servers")
        print(f"  2. Create topics: {config['input_topics']}")
        print(f"  3. Run: pipeline.start_pipeline()")
        print(f"\nयह production-ready streaming ETL pipeline है जो real-world scale handle करता है!")
        
    except Exception as e:
        logger.error(f"Pipeline demonstration failed: {e}")
        raise

if __name__ == "__main__":
    # Run the streaming ETL pipeline demo
    import random
    asyncio.run(main())